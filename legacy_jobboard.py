import os
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from urllib.parse import urlencode

from jobhunter import db, search, coverletter, notifier

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title="JobHunter", version="0.1.0")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

SECRET = os.environ.get("SECRET_KEY", "dev-secret-change-me")


def flash_redirect(request: Request, name: str, message: str = ""):
    url = app.url_path_for(name)
    if message:
        url += "?" + urlencode({"flash": message})
    return RedirectResponse(url=url, status_code=303)


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    stats = {
        "jobs": db.q("SELECT COUNT(*) c FROM jobs")[0]["c"],
        "applied": db.q("SELECT COUNT(*) c FROM applications WHERE status='applied'")[0]["c"],
        "interviews": db.q("SELECT COUNT(*) c FROM applications WHERE interview_at IS NOT NULL")[0]["c"],
        "notifications": db.q("SELECT COUNT(*) c FROM notifications WHERE read=0")[0]["c"],
    }
    recent = db.q(
        "SELECT a.id, j.title, j.company, a.status, a.applied_at FROM applications a "
        "JOIN jobs j ON a.job_id=j.id ORDER BY a.applied_at DESC LIMIT 5")
    unread = db.q("SELECT * FROM notifications ORDER BY created_at DESC LIMIT 5")
    return templates.TemplateResponse("dashboard.html", {
        "request": request, "stats": stats, "recent": recent, "unread": unread})


@app.get("/profile", response_class=HTMLResponse)
def profile_get(request: Request):
    return templates.TemplateResponse("profile.html",
                                      {"request": request, "profile": db.get_profile()})


@app.post("/profile")
def profile_post(
    request: Request,
    full_name: str = Form(""), email: str = Form(""), phone: str = Form(""),
    headline: str = Form(""), skills: str = Form(""),
    experience_years: int = Form(0), summary: str = Form(""),
    portfolio_url: str = Form(""), resume_path: str = Form("")):
    db.save_profile(full_name=full_name, email=email, phone=phone, headline=headline,
                    skills=skills, experience_years=int(experience_years or 0),
                    summary=summary, portfolio_url=portfolio_url, resume_path=resume_path)
    return flash_redirect(request, "profile_get", "Profile saved.")


@app.get("/jobs", response_class=HTMLResponse)
def jobs_get(request: Request, q: str = ""):
    rows = db.q("SELECT * FROM jobs ORDER BY posted_at DESC LIMIT 200")
    if q:
        rows = [r for r in rows
                if q.lower() in (r["title"] + r["company"] + r["tags"]).lower()]
    return templates.TemplateResponse("jobs.html", {"request": request, "jobs": rows, "q": q})


@app.post("/search")
def do_search(request: Request, query: str = Form(""), location: str = Form("")):
    result = search.search_and_store(query, location or None)
    url = app.url_path_for("jobs_get") + "?" + urlencode({"q": query, "flash": f"Search '{query}': {result['found']} found, {result['new']} new."})
    return RedirectResponse(url=url, status_code=303)


@app.get("/apply/{job_id}", response_class=HTMLResponse)
def apply_get(request: Request, job_id: int):
    row = db.q("SELECT * FROM jobs WHERE id=?", (job_id,))
    if not row:
        return RedirectResponse(url=app.url_path_for("jobs_get"), status_code=303)
    job = dict(row[0])
    profile = db.get_profile()
    letter = coverletter.generate(profile, job)
    existing = db.q("SELECT * FROM applications WHERE job_id=?", (job_id,))
    existing = existing[0] if existing else None
    return templates.TemplateResponse("apply.html",
                                      {"request": request, "job": job, "letter": letter, "existing": existing})


@app.post("/apply/{job_id}")
def apply_post(request: Request, job_id: int, cover_letter: str = Form("")):
    row = db.q("SELECT * FROM jobs WHERE id=?", (job_id,))
    if not row:
        return RedirectResponse(url=app.url_path_for("jobs_get"), status_code=303)
    job = dict(row[0])
    profile = db.get_profile()
    cover = cover_letter or coverletter.generate(profile, job)
    when = datetime.utcnow().isoformat()
    existing = db.q("SELECT * FROM applications WHERE job_id=?", (job_id,))
    if existing:
        db.execute(
            "UPDATE applications SET cover_letter=?, status='applied', applied_at=? WHERE job_id=?",
            (cover, when, job_id))
    else:
        db.execute(
            "INSERT INTO applications (job_id, status, applied_at, cover_letter) VALUES (?,?,?,?)",
            (job_id, "applied", when, cover))
    notifier.notify("Application submitted",
                    f"Applied to {job['title']} at {job['company']}. Cover letter ready.")
    return flash_redirect(request, "applications_get", "Application recorded. Finish the final submit on the employer site via the job link.")


@app.get("/applications", response_class=HTMLResponse)
def applications_get(request: Request):
    rows = db.q(
        "SELECT a.*, j.title, j.company, j.url FROM applications a "
        "JOIN jobs j ON a.job_id=j.id ORDER BY a.applied_at DESC")
    return templates.TemplateResponse("applications.html", {"request": request, "apps": rows})


@app.post("/mark_interview/{app_id}")
def mark_interview(request: Request, app_id: int, interview_at: str = Form("")):
    when = interview_at or datetime.utcnow().isoformat()
    db.execute("UPDATE applications SET status='interview', interview_at=? WHERE id=?",
               (when, app_id))
    app = db.q(
        "SELECT j.title, j.company FROM applications a JOIN jobs j ON a.job_id=j.id WHERE a.id=?",
        (app_id,))
    if app:
        a = app[0]
        notifier.notify("Interview scheduled",
                        f"Interview for {a['title']} at {a['company']} on {when}.")
    return flash_redirect(request, "applications_get", "Interview marked — notification sent.")


@app.get("/notifications", response_class=HTMLResponse)
def notifications_get(request: Request):
    rows = db.q("SELECT * FROM notifications ORDER BY created_at DESC")
    return templates.TemplateResponse("notifications.html", {"request": request, "notes": rows})


@app.post("/notifications/read/{note_id}")
def mark_read(request: Request, note_id: int):
    db.execute("UPDATE notifications SET read=1 WHERE id=?", (note_id,))
    return RedirectResponse(url=app.url_path_for("notifications_get"), status_code=303)


@app.on_event("startup")
def on_startup():
    db.init_db()


if __name__ == "__main__":
    import uvicorn
    db.init_db()
    uvicorn.run(app, host="127.0.0.1", port=8000)
