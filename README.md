# JobHunter

A semi-automated job-hunting assistant. It searches remote job boards, lets you **1-click apply** (with an auto-generated, tailored cover letter), tracks every application, and fires a notification the moment you mark an interview.

> **Why "semi-auto" and not fully automated?** Scraping and auto-submitting applications on LinkedIn, Upwork, Indeed, etc. violates their Terms of Service and gets accounts banned. JobHunter finds matches, pre-fills your materials, and you complete the final submit on the employer's site. Safe and durable.

## Features
- **Job search** from Remotive (remote, no API key needed) + Adzuna (needs free key).
- **1-click apply** with an auto-generated cover letter tailored from your profile + the job description.
- **Application tracker** (applied → interview) with notes.
- **Interview notifications** — in-app alert log + optional email via SMTP.
- Local SQLite DB, FastAPI + Jinja2, no external services required.

## Requirements
- Python 3.10+ (tested on 3.12).
- Windows / macOS / Linux.

## Setup

```bash
cd jobhunter
python -m venv .venv
.venv\Scripts\activate        # Windows  (or: source .venv/bin/activate on Unix)
pip install -r requirements.txt

# seed a demo profile + sample jobs (optional but recommended)
python -m jobhunter.seed

# run
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```
Open http://127.0.0.1:8000 (interactive API docs at /docs).

## Configuration (optional)
Copy `.env.example` to `.env` and set any of:

| Variable | Purpose |
|---|---|
| `ADZUNA_APP_ID` / `ADZUNA_APP_KEY` | Enable Adzuna job source (free at adzuna.com) |
| `ADZUNA_COUNTRY` | e.g. `gb`, `us` |
| `SMTP_HOST` / `SMTP_PORT` | Email notifications (e.g. Gmail `smtp.gmail.com:587`) |
| `SMTP_USER` / `SMTP_PASS` | Your email login (use an app password for Gmail) |
| `NOTIFY_EMAIL` | Where interview/application alerts are sent |
| `SECRET_KEY` | Session/security secret |

Without SMTP set, notifications still appear in the **Notifications** page.

## Usage flow
1. Fill in your **Profile** (drives cover letters).
2. **Search** jobs (Remotive live; add Adzuna keys for more).
3. Hit **Apply** on a job → review/edit the generated cover letter → **Record application**.
4. When an employer replies, open **Applications** → **Mark interview** → an alert is logged (and emailed if configured).

## Project layout
```
app.py                 FastAPI routes + HTML rendering
jobhunter/
  config.py            env config (API keys, SMTP)
  db.py                SQLite layer
  search.py            Remotive + Adzuna fetch + normalize
  coverletter.py       profile+job -> cover letter
  notifier.py          in-app + email notifications
  seed.py              demo profile + sample jobs
  templates/           Jinja2 pages
  static/              css/assets
```

## Roadmap ideas
- Official-board OAuth apply (where ToS permits).
- Resume PDF generation.
- Calendar integration for interview reminders.
- Daily auto-search + digest email.
