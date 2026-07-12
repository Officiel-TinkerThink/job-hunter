"""API contracts (pydantic v2).

Single source of truth for request/response shapes. The frontend reads these
field names, so they must stay stable. Domain models stay framework-free — these
schemas are the HTTP boundary only.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class ProfileBase(BaseModel):
    full_name: str = ""
    headline: str = ""
    skills: list[str] = Field(default_factory=list)
    experience_years: int = 0
    summary: str = ""
    portfolio_url: str = ""
    min_hourly_rate: float | None = None
    min_fixed_budget: float | None = None
    remote_only: bool = True
    avoid_niches: list[str] = Field(default_factory=list)
    timezone: str = "UTC"
    upwork_profile_url: str = ""
    fiverr_gig_urls: list[str] = Field(default_factory=list)


class ProfileIn(ProfileBase):
    """Inbound profile edit. pydantic coerces strings→lists, so a stray
    comma-string from the UI won't crash the save (fixes the old array.split bug)."""


class ProfileOut(ProfileBase):
    model_config = {"from_attributes": True}


class OpportunityOut(BaseModel):
    id: int
    source: str
    title: str
    url: str
    client: str
    summary: str
    budget: str | None = None
    tags: list[str] = Field(default_factory=list)
    state: str
    score: float | None = None
    score_reasons: list[str] = Field(default_factory=list)
    proposal: str = ""
    created_at: str = ""


class TimelineEvent(BaseModel):
    kind: str
    message: str
    at: str
    payload: dict = Field(default_factory=dict)


class TimelineOut(BaseModel):
    opportunity: OpportunityOut
    events: list[TimelineEvent] = Field(default_factory=list)


class ApplyResult(BaseModel):
    ok: bool
    state: str
    channel: str
    to: str | None = None
    subject: str = ""
    dry_run: bool


class DiscoverResult(BaseModel):
    found: int = 0
    new: int = 0
    proposed: int = 0


class OkResult(BaseModel):
    ok: bool = True
