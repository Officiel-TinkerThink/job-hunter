import smtplib
from email.message import EmailMessage
from datetime import datetime
from . import db
from .config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, NOTIFY_EMAIL


def _log(kind, message):
    db.execute(
        "INSERT INTO notifications (kind, message, created_at) VALUES (?,?,?)",
        (kind, message, datetime.utcnow().isoformat()),
    )


def send_email(subject, body):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = NOTIFY_EMAIL
    msg.set_content(body)
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.starttls()
        s.login(SMTP_USER, SMTP_PASS)
        s.send_message(msg)


def notify(kind, message):
    """Log an in-app notification and, if email is configured, send it too."""
    _log(kind, message)
    if SMTP_USER and NOTIFY_EMAIL and SMTP_PASS:
        try:
            send_email(f"JobHunter: {kind}", message)
        except Exception as e:
            _log("email_error", f"Failed to send email: {e}")
