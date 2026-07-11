"""Domain models — pure, no framework or I/O imports.

Wahyu's freelance-hunter core concepts as explicit DDD types.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Money:
    """A monetary amount with currency. Used for rate / budget floors."""
    amount: float
    currency: str = "USD"

    def __ge__(self, other: "Money") -> bool:
        if self.currency != other.currency:
            raise ValueError(f"Cannot compare {self.currency} vs {other.currency}")
        return self.amount >= other.amount

    def __lt__(self, other: "Money") -> bool:
        return not self.__ge__(other)


@dataclass(frozen=True)
class MatchScore:
    """Result of scoring an opportunity against Wahyu's profile."""
    value: float            # 0.0 .. 1.0
    reasons: list[str] = field(default_factory=list)
    meets_floor: bool = True  # False if budget/rate below Wahyu's minimum

    def is_promising(self, high_threshold: float = 0.7) -> bool:
        return self.value >= high_threshold and self.meets_floor


class Source(str, Enum):
    UPWORK = "upwork"
    FIVERR = "fiverr"
    # future channels added as one new adapter + enum member


class OpportunityState(str, Enum):
    NEW = "new"
    PROMISING = "promising"
    NOT_A_FIT = "not_a_fit"
    PROPOSED = "proposed"          # awaiting Wahyu's 1-tap approval
    DRAFT_READY = "draft_ready"
    APPLIED = "applied"
    FOLLOWED_UP = "followed_up"
    INTERVIEW = "interview"
    TEST = "test"
    WON = "won"
    LOST = "lost"
    ARCHIVED = "archived"


# ---------------------------------------------------------------------------
# Aggregates
# ---------------------------------------------------------------------------
@dataclass
class Opportunity:
    """A single freelance opportunity Wahyu is (or could be) pursuing.

    The progress timeline is a projection of the events this aggregate emits.
    """
    source: Source
    external_id: str
    title: str
    url: str
    client: str = ""
    summary: str = ""
    budget: Optional[Money] = None
    tags: list[str] = field(default_factory=list)
    state: OpportunityState = OpportunityState.NEW
    score: Optional[MatchScore] = None
    proposal: str = ""
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)
    id: Optional[int] = None

    @property
    def composite_key(self) -> str:
        return f"{self.source.value}:{self.external_id}"


@dataclass
class Profile:
    """Wahyu's freelancer profile — drives matching + proposal drafting.

    Replace the demo data via the API / `set_profile` before discovery runs.
    """
    full_name: str = ""
    headline: str = ""
    skills: list[str] = field(default_factory=list)
    experience_years: int = 0
    summary: str = ""
    portfolio_url: str = ""
    min_hourly_rate: Optional[Money] = None
    min_fixed_budget: Optional[Money] = None
    remote_only: bool = True
    avoid_niches: list[str] = field(default_factory=list)
    timezone: str = "UTC"
    upwork_profile_url: str = ""
    fiverr_gig_urls: list[str] = field(default_factory=list)
