"""Ports — abstract interfaces the domain depends on.

Adapters in app/adapters/ implement these. The domain NEVER imports adapters.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterable

from .models import Opportunity, Profile


class JobSource(ABC):
    """A channel that discovers freelance opportunities (Upwork RSS, Fiverr, ...)."""

    @abstractmethod
    def discover(self) -> Iterable[Opportunity]:
        """Return raw opportunities from the channel (no scoring yet)."""
        ...


class OpportunityRepository(ABC):
    """Persistence for opportunities + their event timeline."""

    @abstractmethod
    def save(self, opp: Opportunity) -> Opportunity: ...

    @abstractmethod
    def get(self, opp_id: int) -> Optional[Opportunity]: ...

    @abstractmethod
    def get_by_external(self, source: str, external_id: str) -> Optional[Opportunity]: ...

    @abstractmethod
    def list_states(self, states: list[str] | None = None) -> list[Opportunity]: ...

    @abstractmethod
    def add_event(self, opp_id: int, event: "DomainEvent") -> None: ...

    @abstractmethod
    def events_for(self, opp_id: int) -> list["DomainEvent"]: ...


class Mailer(ABC):
    """Outbound email (used by the SMTP adapter for email-apply)."""

    @abstractmethod
    def send(self, to: str, subject: str, body: str) -> None: ...


class ProfileStore(ABC):
    """Persistence for Wahyu's freelancer Profile (matching preferences)."""

    @abstractmethod
    def get(self) -> Profile: ...

    @abstractmethod
    def save(self, profile: Profile) -> None: ...
