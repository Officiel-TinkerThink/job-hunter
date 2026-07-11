"""Discovery component — feature module wiring adapters + cells.

Flow: JobSource.discover() -> dedup -> ScoreOpportunity cell -> events.
This is the single "discover" capability; the HTTP route just calls it.
"""
from __future__ import annotations
from typing import Iterable

from ..domain.events import DomainEvent, EventBus
from ..domain.models import Opportunity
from ..domain.ports import JobSource, OpportunityRepository, ProfileStore
from ..domain.services.score_opportunity import ScoreOpportunity


class Discovery:
    def __init__(self, source: JobSource, repo: OpportunityRepository,
                 profiles: ProfileStore, bus: EventBus):
        self.source = source
        self.repo = repo
        self.profiles = profiles
        self.bus = bus
        self.scorer = ScoreOpportunity(repo, profiles, bus)

    def run(self) -> dict:
        """Discover + score opportunities. Returns a summary for the UI."""
        raw: Iterable[Opportunity] = self.source.discover()
        found = new = proposed = 0
        for opp in raw:
            found += 1
            existing = self.repo.get_by_external(opp.source.value, opp.external_id)
            if existing:
                continue
            new += 1
            saved = self.repo.save(opp)
            self.bus.publish(DomainEvent.discovered(saved.id, opp.title, opp.source.value))
            scored = self.scorer(saved)
            if scored.state.value in ("proposed", "promising"):
                proposed += 1
        return {"found": found, "new": new, "proposed": proposed}
