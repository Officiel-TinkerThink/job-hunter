"""SMTP mailer adapter implementing the Mailer port.

Dry-run safe: if SMTP credentials are not configured (env), `send` does not contact
any server — it logs the intent and sets `dry_run = True` so the calling cell can
record the application as an event without actually transmitting. Configure
SMTP_HOST/SMTP_PORT/SMTP_USER/SMTP_PASSWORD/SMTP_FROM (and APPLY_TO) to send for real.

No third-party email libraries: stdlib smtplib only.
"""
from __future__ import annotations

import os
import smtplib
import ssl
from email.message import EmailMessage

from ..domain.ports import Mailer
from ..infra.config import (SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM)


class SmtpMailer(Mailer):
    def __init__(self):
        self.dry_run = not (SMTP_HOST and SMTP_USER and SMTP_PASSWORD and SMTP_FROM)

    def send(self, to: str, subject: str, body: str) -> None:
        if self.dry_run:
            print(f"[DRY-RUN] would send email -> {to!r} subject={subject!r}")
            return
        msg = EmailMessage()
        msg["From"] = SMTP_FROM
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)
        ctx = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.starttls(context=ctx)
            s.login(SMTP_USER, SMTP_PASSWORD)
            s.send_message(msg)
