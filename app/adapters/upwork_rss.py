"""Upwork RSS adapter — implements JobSource port.

Uses Upwork's PUBLIC job RSS feed (no auth, ToS-clean). This is the safe,
automatable discovery path. Swap this single adapter for an official-API
adapter later without touching the domain.

FEED LIMIT: the public RSS returns a limited number of recent jobs. For
production volume you'll need the official Upwork API (restricted access).
"""
from __future__ import annotations
import re
from xml.etree import ElementTree as ET

import requests

from ..domain.models import Money, Opportunity, Source
from ..domain.ports import JobSource
from ..infra.config import JOB_SOURCE

_NS = {"rss": "http://purl.org/rss/1.0/"}
_MONEY_RE = re.compile(r"([$€£])\s?([\d,]+(?:\.\d+)?)", re.I)


def _parse_budget(text: str) -> Money | None:
    if not text:
        return None
    m = _MONEY_RE.search(text)
    if not m:
        return None
    sym, num = m.group(1), m.group(2).replace(",", "")
    cur = {"$": "USD", "€": "EUR", "£": "GBP"}.get(sym, "USD")
    try:
        return Money(float(num), cur)
    except ValueError:
        return None


class UpworkRssSource(JobSource):
    """DEPRECATED: Upwork discontinued its public RSS feed (HTTP 410, 2026).

    Kept as the adapter template for when official Upwork API access is granted.
    Do NOT use JOB_SOURCE=upwork until a working API-backed source exists.
    """

    def __init__(self, url: str | None = None, timeout: float = 15.0):
        self.url = url
        self.timeout = timeout

    def discover(self):
        raise NotImplementedError(
            "Upwork public RSS was discontinued (HTTP 410). Use JOB_SOURCE=hackernews "
            "or implement an official Upwork API adapter."
        )
