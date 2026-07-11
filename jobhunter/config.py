import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data.db")

# Adzuna API (free tier, needs app id + key) — optional, set via env to enable
ADZUNA_APP_ID = os.environ.get("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = os.environ.get("ADZUNA_APP_KEY", "")
ADZUNA_COUNTRY = os.environ.get("ADZUNA_COUNTRY", "gb")

# Email notifications (SMTP)
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
NOTIFY_EMAIL = os.environ.get("NOTIFY_EMAIL", "")
