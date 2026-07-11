"""Cells — one use-case each, composing atoms + ports. No HTTP, no framework.

Each cell emits domain events via the injected EventBus. This is where the
hexagon's business behavior lives.
"""
from __future__ import annotations
from typing import Optional

from ..events import DomainEvent, EventBus
from ..models import Opportunity, OpportunityState, Profile
from ..ports import OpportunityRepository, ProfileStore
from .matching import match_score


class ScoreOpportunity:
    """Cell: score a freshly discovered opportunity and set its state.

    Gate: high-confidence + meets floor → PROPOSED (Wahyu approves, ToS-safe
    for now); promising → PROPOSED; otherwise NOT_A_FIT (archived silently).
    """

    def __init__(self, repo: OpportunityRepository, profiles: ProfileStore,
                 bus: EventBus, high_threshold: float = 0.7):
        self.repo = repo
        self.profiles = profiles
        self.bus = bus
        self.high_threshold = high_threshold

    def __call__(self, opp: Opportunity) -> Opportunity:
        profile = self.profiles.get()
        score = match_score(profile, opp)
        opp.score = score

        if score.is_promising(self.high_threshold):
            opp.state = OpportunityState.PROPOSED  # auto-stage candidate
        elif score.meets_floor and score.value >= 0.4:
            opp.state = OpportunityState.PROMISING
        else:
            opp.state = OpportunityState.NOT_A_FIT

        self.repo.save(opp)
        self.bus.publish(DomainEvent.scored(opp.id, score.value, score.reasons, score.meets_floor))
        if opp.state in (OpportunityState.PROPOSED, OpportunityState.PROMISING):
            self.bus.publish(DomainEvent.proposed(opp.id))
        return opp
