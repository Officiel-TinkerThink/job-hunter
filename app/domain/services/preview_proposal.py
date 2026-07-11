"""Cell: produce a draft proposal preview without changing the opportunity state.

Used by the UI to show the agent's proposed pitch (and let the user copy it)
before they commit to Approve (which drafts + moves to DRAFT_READY)."""
from ..models import Opportunity
from ..ports import OpportunityRepository, ProfileStore
from ..services.proposal_drafting import draft_proposal


class PreviewProposal:
    def __init__(self, repo: OpportunityRepository, profiles: ProfileStore):
        self.repo = repo
        self.profiles = profiles

    def __call__(self, opp_id: int) -> str:
        opp = self.repo.get(opp_id)
        if not opp:
            raise ValueError("not found")
        profile = self.profiles.get()
        return draft_proposal(profile, opp)
