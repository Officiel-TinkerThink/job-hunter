"""Cell: submit an application by email (ToS-clean apply path).

Given an approved opportunity, compose the email (subject + body from the agent's
proposal + profile) and hand it to the Mailer port. Emits `applied` so the timeline
stays truthful. If the Mailer is in dry-run (no SMTP creds configured), nothing is
sent — the cell reports dry_run=True and still records the intent as an event.

This is the safe, human-in-loop apply channel. Upwork web-form submit stays behind
official API access (see ROADMAP)."""
from __future__ import annotations

from ..events import DomainEvent, EventBus
from ..models import Opportunity, OpportunityState
from ..ports import Mailer, OpportunityRepository, ProfileStore


def compose_email(profile, opp: Opportunity) -> tuple[str, str]:
    subject = f"Proposal: {opp.title}"
    body = (
        opp.proposal
        or f"Hi, I'm interested in your project \"{opp.title}\". "
           f"Here's my profile: {profile.headline}."
    )
    return subject, body


class SubmitApplication:
    def __init__(self, repo: OpportunityRepository, profiles: ProfileStore,
                 mailer: Mailer, bus: EventBus, apply_to: str | None = None):
        self.repo = repo
        self.profiles = profiles
        self.mailer = mailer
        self.bus = bus
        self.apply_to = apply_to

    def __call__(self, opp_id: int) -> dict:
        opp = self.repo.get(opp_id)
        if not opp:
            raise ValueError("not found")
        profile = self.profiles.get()
        subject, body = compose_email(profile, opp)

        to = self.apply_to or getattr(profile, "email", None)
        dry_run = to is None or getattr(self.mailer, "dry_run", False)
        if not dry_run:
            self.mailer.send(to, subject, body)  # type: ignore[arg-type]

        opp.state = OpportunityState.APPLIED
        self.repo.save(opp)
        self.bus.publish(DomainEvent.applied(opp.id, "email"))
        return {
            "ok": True,
            "state": "applied",
            "channel": "email",
            "to": to,
            "subject": subject,
            "dry_run": dry_run,
        }
