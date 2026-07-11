"""Cells for the approve/pass user decision (human-in-loop gate).

Approving lets the agent draft a proposal (DraftProposal atom) and move the
opportunity to DRAFT_READY. Passing archives it. Both emit events so the
timeline stays truthful.
"""
from __future__ import annotations

from ..events import DomainEvent, EventBus
from ..models import Opportunity, OpportunityState
from ..ports import OpportunityRepository, ProfileStore
from .proposal_drafting import draft_proposal


class ApproveOpportunity:
    def __init__(self, repo: OpportunityRepository, profiles: ProfileStore, bus: EventBus):
        self.repo = repo
        self.profiles = profiles
        self.bus = bus

    def __call__(self, opp_id: int) -> Opportunity:
        opp = self.repo.get(opp_id)
        if not opp:
            raise ValueError("not found")
        opp.proposal = draft_proposal(self.profiles.get(), opp)
        opp.state = OpportunityState.DRAFT_READY
        self.repo.save(opp)
        self.bus.publish(DomainEvent.draft_ready(opp.id))
        return opp


class PassOpportunity:
    def __init__(self, repo: OpportunityRepository, bus: EventBus):
        self.repo = repo
        self.bus = bus

    def __call__(self, opp_id: int) -> Opportunity:
        opp = self.repo.get(opp_id)
        if not opp:
            raise ValueError("not found")
        opp.state = OpportunityState.ARCHIVED
        self.repo.save(opp)
        self.bus.publish(DomainEvent("passed", opp_id, "You passed on this opportunity"))
        return opp
