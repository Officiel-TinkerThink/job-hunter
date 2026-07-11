"""Config — injected at composition root; never imported deep in the core."""
from __future__ import annotations
import os
from pathlib import Path

# Load .env (project root) if present — no third-party dep. Only fills vars that
# aren't already set in the environment, so shell exports always win.
_ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"
if _ENV_PATH.exists():
    for line in _ENV_PATH.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip()
        if k and k not in os.environ:
            os.environ[k] = v

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # app/infra -> project root
DATA_DIR = BASE_DIR / "data"
DB_PATH = os.environ.get("JOBHUNTER_DB", str(DATA_DIR / "jobhunter.db"))

# Discovery source selection. Upwork's public RSS was discontinued (HTTP 410),
# so the working default is SeedSource (realistic Upwork-style listings) for a
# clickable demo, with HackerNews as a live public feed. Swap to an official
# Upwork API adapter once access is available.
JOB_SOURCE = os.environ.get("JOB_SOURCE", "seed")

# Email-apply (SMTP). When any of these are missing the mailer runs in dry-run
# (logs intent, sends nothing) so the app is safe to run without credentials.
SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
SMTP_FROM = os.environ.get("SMTP_FROM")
APPLY_TO = os.environ.get("APPLY_TO")  # where applications are sent
