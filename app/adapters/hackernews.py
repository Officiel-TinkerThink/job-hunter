"""Hacker News freelance adapter — implements JobSource port.

Uses the PUBLIC, ToS-clean HN Algolia API (no auth). Good for freelance /
"who is hiring" style posts. Swap for an Upwork official-API adapter later
without touching the domain. This is the working default until Upwork API
access is available (their public RSS was discontinued — HTTP 410).
"""
from __future__ import annotations
import re

import requests

from ..domain.models import Money, Opportunity, Source
from ..domain.ports import JobSource

_BASE = "https://hn.algolia.com/api/v1/search"
_MONEY_RE = re.compile(r"(\$\s?[\d,]+(?:\.\d+)?\s?(?:k|hr|/hr|hour|mo|/mo)?)", re.I)


def _parse_budget(text: str) -> Money | None:
    m = _MONEY_RE.search(text or "")
    if not m:
        return None
    num = re.search(r"[\d,]+", m.group(1))
    if not num:
        return None
    try:
        val = float(num.group(0).replace(",", ""))
        if "k" in m.group(1).lower():
            val *= 1000
        return Money(val, "USD")
    except ValueError:
        return None


class HackerNewsSource(JobSource):
    def __init__(self, query: str = "freelance developer", hits: int = 30,
                 timeout: float = 15.0):
        self.query = query
        self.hits = hits
        self.timeout = timeout

    def discover(self):
        resp = requests.get(_BASE, params={
            "query": self.query, "tags": "story",
            "hitsPerPage": self.hits,
        }, timeout=self.timeout, headers={"User-Agent": "JobHunter/0.1"})
        resp.raise_for_status()
        hits = resp.json().get("hits", [])
        out = []
        for h in hits:
            title = (h.get("title") or "").strip()
            if not title:
                continue
            url = h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}"
            ext_id = f"hn_{h.get('objectID')}"
            tags = self._extract_skills(title)
            out.append(Opportunity(
                source=Source.UPWORK,  # shown as freelance; channel label can be refined later
                external_id=ext_id, title=title, url=url,
                summary=(h.get("story_text") or "")[:400].strip(),
                budget=_parse_budget(title), tags=tags,
            ))
        return out

    @staticmethod
    def _extract_skills(text: str) -> list[str]:
        known = ["python", "react", "typescript", "django", "fastapi", "aws",
                 "docker", "sql", "postgres", "rust", "go", "node", "next.js",
                 "tailwind", "devops", "fullstack", "full-stack"]
        t = (text or "").lower()
        return [k for k in known if k in t]
