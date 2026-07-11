"""Domain events — every meaningful state change emits one.

The opportunity progress timeline IS a projection of an opportunity's event stream.
In-process pub/sub now; promote to Redis Streams / RabbitMQ only when multi-process
durability is needed (see skill hex-ddd-event-architecture).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class DomainEvent:
    """Base event. `kind` drives UI icon/label; `payload` carries detail."""
    kind: str
    opp_id: int
    message: str
    at: str = field(default_factory=_now)
    payload: dict = field(default_factory=dict)
    id: Optional[int] = None

    # --- concrete helpers -------------------------------------------------
    @classmethod
    def discovered(cls, opp_id, title, source):
        return cls("discovered", opp_id, f"Discovered on {source}: {title}")

    @classmethod
    def scored(cls, opp_id, value, reasons, meets_floor):
        verdict = "promising" if (value >= 0.7 and meets_floor) else "not a fit"
        return cls("scored", opp_id,
                   f"Scored {value:.0%} — {verdict}",
                   payload={"score": value, "reasons": reasons,
                            "meets_floor": meets_floor})

    @classmethod
    def proposed(cls, opp_id):
        return cls("proposed", opp_id, "Awaiting your approval to draft a proposal")

    @classmethod
    def draft_ready(cls, opp_id):
        return cls("draft_ready", opp_id, "Proposal drafted and ready to send")

    @classmethod
    def applied(cls, opp_id, channel):
        return cls("applied", opp_id, f"Application submitted via {channel}",
                   payload={"channel": channel})

    @classmethod
    def reply(cls, opp_id, kind, summary):
        return cls("reply", opp_id, f"Reply received: {kind} — {summary}",
                   payload={"reply_kind": kind})

    @classmethod
    def escalated(cls, opp_id, kind):
        label = "interview" if kind == "interview" else "test"
        return cls("escalated", opp_id,
                   f"ACTION NEEDED: {label} scheduled — your attention required",
                   payload={"kind": kind})

    @classmethod
    def closed(cls, opp_id, won: bool):
        return cls("closed", opp_id, "Won" if won else "Lost")


class EventBus:
    """In-process pub/sub. Listeners are plain callables(event)."""
    def __init__(self):
        self._subs = []

    def subscribe(self, fn):
        self._subs.append(fn)

    def publish(self, event: DomainEvent):
        for fn in self._subs:
            fn(event)
