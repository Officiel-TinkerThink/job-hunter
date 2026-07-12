"""Dependency injection — FastAPI `Depends` providers.

Singletons are created once (lazily) and shared per request via Dependencies.
No module-level wiring, so the app is testable and reloadable.
"""
from __future__ import annotations

from functools import lru_cache

from ..adapters.hackernews import HackerNewsSource
from ..adapters.seed_source import SeedSource
from ..adapters.smtp_mailer import SmtpMailer
from ..adapters.sqlite_repo import SQLiteOpportunityRepo, SQLiteProfileStore, init_db
from ..adapters.upwork_rss import UpworkRssSource
from ..domain.events import EventBus
from ..components.discovery import Discovery
from ..domain.services.decision import ApproveOpportunity, PassOpportunity
from ..domain.services.preview_proposal import PreviewProposal
from ..domain.services.submit_application import SubmitApplication
from ..infra.config import JOB_SOURCE, APPLY_TO


@lru_cache(maxsize=1)
def _bus() -> EventBus:
    return EventBus()


@lru_cache(maxsize=1)
def _repo() -> SQLiteOpportunityRepo:
    init_db()
    return SQLiteOpportunityRepo()


@lru_cache(maxsize=1)
def _profiles() -> SQLiteProfileStore:
    return SQLiteProfileStore()


@lru_cache(maxsize=1)
def _discovery() -> Discovery:
    source_cls = {"seed": SeedSource, "hackernews": HackerNewsSource, "upwork": UpworkRssSource}.get(
        JOB_SOURCE, SeedSource
    )
    return Discovery(source_cls(), _repo(), _profiles(), _bus())


@lru_cache(maxsize=1)
def _approve() -> ApproveOpportunity:
    return ApproveOpportunity(_repo(), _profiles(), _bus())


@lru_cache(maxsize=1)
def _pass() -> PassOpportunity:
    return PassOpportunity(_repo(), _bus())


@lru_cache(maxsize=1)
def _preview() -> PreviewProposal:
    return PreviewProposal(_repo(), _profiles())


@lru_cache(maxsize=1)
def _submit() -> SubmitApplication:
    return SubmitApplication(_repo(), _profiles(), SmtpMailer(), _bus(), apply_to=APPLY_TO)


def get_bus() -> EventBus:
    return _bus()


def get_repo() -> SQLiteOpportunityRepo:
    return _repo()


def get_profiles() -> SQLiteProfileStore:
    return _profiles()


def get_discovery() -> Discovery:
    return _discovery()


def get_approve() -> ApproveOpportunity:
    return _approve()


def get_pass() -> PassOpportunity:
    return _pass()


def get_preview() -> PreviewProposal:
    return _preview()


def get_submit() -> SubmitApplication:
    return _submit()
