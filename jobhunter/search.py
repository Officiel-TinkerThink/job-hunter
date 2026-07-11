import json
import requests
from . import db
from .config import ADZUNA_APP_ID, ADZUNA_APP_KEY, ADZUNA_COUNTRY


def _norm_remotive(data):
    out = []
    for j in data.get("jobs", []):
        out.append({
            "source": "remotive",
            "ext_id": str(j.get("id")),
            "title": j.get("title", ""),
            "company": j.get("company_name", ""),
            "location": j.get("candidate_required_location", ""),
            "url": j.get("url", ""),
            "description": j.get("description", ""),
            "tags": ", ".join(j.get("tags", []) or []),
            "salary": j.get("salary", "") or "",
            "posted_at": j.get("publication_date", ""),
            "raw_json": json.dumps(j),
        })
    return out


def _norm_adzuna(data):
    out = []
    for j in data.get("results", []):
        out.append({
            "source": "adzuna",
            "ext_id": str(j.get("id")),
            "title": j.get("title", ""),
            "company": (j.get("company") or {}).get("display_name", ""),
            "location": (j.get("location") or {}).get("display_name", ""),
            "url": j.get("redirect_url", ""),
            "description": j.get("description", ""),
            "tags": (j.get("category") or {}).get("label", ""),
            "salary": f"{j.get('salary_min')} - {j.get('salary_max')}",
            "posted_at": j.get("created", ""),
            "raw_json": json.dumps(j),
        })
    return out


def fetch_remotive(query):
    try:
        r = requests.get("https://remotive.com/api/remote-jobs",
                         params={"search": query}, timeout=20)
        r.raise_for_status()
        return _norm_remotive(r.json())
    except Exception as e:
        print("remotive fetch error:", e)
        return []


def fetch_adzuna(query, location=None):
    if not ADZUNA_APP_ID:
        return []
    params = {"app_id": ADZUNA_APP_ID, "app_key": ADZUNA_APP_KEY,
              "results_per_page": 20, "what": query}
    if location:
        params["where"] = location
    try:
        url = f"https://api.adzuna.com/v1/api/jobs/{ADZUNA_COUNTRY}/search/1"
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        return _norm_adzuna(r.json())
    except Exception as e:
        print("adzuna fetch error:", e)
        return []


def search_and_store(query, location=None):
    jobs = fetch_remotive(query) + fetch_adzuna(query, location)
    new = 0
    for j in jobs:
        exists = db.q("SELECT id FROM jobs WHERE source=? AND ext_id=?",
                      (j["source"], j["ext_id"]))
        if not exists:
            db.execute(
                """INSERT INTO jobs
                   (source, ext_id, title, company, location, url, description, tags, salary, posted_at, raw_json)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (j["source"], j["ext_id"], j["title"], j["company"], j["location"],
                 j["url"], j["description"], j["tags"], j["salary"], j["posted_at"], j["raw_json"]))
            new += 1
    return {"found": len(jobs), "new": new}
