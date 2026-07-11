"""SQLite adapters implementing OpportunityRepository + ProfileStore ports.

This is the ONLY place that knows about SQL / sqlite3. The domain never imports it.
Events are stored in an `events` table → the opportunity timeline is a projection of it.
"""
from __future__ import annotations
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from ..domain.events import DomainEvent
from ..domain.models import (
    Money, Opportunity, OpportunityState, Profile, Source, MatchScore,
)
from ..domain.ports import OpportunityRepository, ProfileStore
from ..infra.config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS opportunities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,
    external_id TEXT,
    title TEXT,
    url TEXT,
    client TEXT,
    summary TEXT,
    budget_amount REAL,
    budget_currency TEXT,
    tags TEXT,
    state TEXT,
    score_value REAL,
    score_meets_floor INTEGER,
    proposal TEXT,
    created_at TEXT,
    updated_at TEXT,
    UNIQUE(source, external_id)
);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    opp_id INTEGER,
    kind TEXT,
    message TEXT,
    at TEXT,
    payload TEXT
);
CREATE TABLE IF NOT EXISTS profile (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    full_name TEXT, headline TEXT, skills TEXT, experience_years INTEGER,
    summary TEXT, portfolio_url TEXT,
    min_hourly_rate REAL, min_hourly_currency TEXT,
    min_fixed_budget REAL, min_fixed_currency TEXT,
    remote_only INTEGER, avoid_niches TEXT, timezone TEXT,
    upwork_profile_url TEXT, fiverr_gig_urls TEXT
);
"""


def _conn():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    c = _conn()
    c.executescript(SCHEMA)
    c.execute("INSERT OR IGNORE INTO profile (id) VALUES (1)")
    c.commit()
    c.close()


def _row_to_opp(r: sqlite3.Row) -> Opportunity:
    budget = None
    if r["budget_amount"] is not None:
        budget = Money(r["budget_amount"], r["budget_currency"] or "USD")
    opp = Opportunity(
        id=r["id"], source=Source(r["source"]), external_id=r["external_id"],
        title=r["title"], url=r["url"], client=r["client"] or "",
        summary=r["summary"] or "", budget=budget,
        tags=json.loads(r["tags"] or "[]"),
        state=OpportunityState(r["state"]),
        proposal=r["proposal"] or "",
        created_at=r["created_at"], updated_at=r["updated_at"],
    )
    if r["score_value"] is not None:
        opp.score = MatchScore(value=r["score_value"],
                               meets_floor=bool(r["score_meets_floor"]))
    return opp


class SQLiteOpportunityRepo(OpportunityRepository):
    def save(self, opp: Opportunity) -> Opportunity:
        c = _conn()
        now = datetime.now(timezone.utc).isoformat()
        if opp.budget:
            amt, cur = opp.budget.amount, opp.budget.currency
        else:
            amt, cur = None, None
        score_val = opp.score.value if opp.score else None
        meets = 1 if (opp.score and opp.score.meets_floor) else 0
        if opp.id is None:
            cur_r = c.execute(
                "SELECT id FROM opportunities WHERE source=? AND external_id=?",
                (opp.source.value, opp.external_id))
            existing = cur_r.fetchone()
            if existing:
                opp.id = existing["id"]
        if opp.id is None:
            r = c.execute(
                """INSERT INTO opportunities
                   (source,external_id,title,url,client,summary,budget_amount,budget_currency,
                    tags,state,score_value,score_meets_floor,proposal,created_at,updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (opp.source.value, opp.external_id, opp.title, opp.url, opp.client,
                 opp.summary, amt, cur, json.dumps(opp.tags), opp.state.value,
                 score_val, meets, opp.proposal, opp.created_at, now))
            opp.id = r.lastrowid
        else:
            c.execute(
                """UPDATE opportunities SET title=?,url=?,client=?,summary=?,
                   budget_amount=?,budget_currency=?,tags=?,state=?,score_value=?,
                   score_meets_floor=?,proposal=?,updated_at=?
                   WHERE id=?""",
                (opp.title, opp.url, opp.client, opp.summary, amt, cur,
                 json.dumps(opp.tags), opp.state.value, score_val, meets,
                 opp.proposal, now, opp.id))
        c.commit()
        c.close()
        return opp

    def get(self, opp_id: int) -> Optional[Opportunity]:
        c = _conn()
        r = c.execute("SELECT * FROM opportunities WHERE id=?", (opp_id,)).fetchone()
        c.close()
        return _row_to_opp(r) if r else None

    def get_by_external(self, source: str, external_id: str) -> Optional[Opportunity]:
        c = _conn()
        r = c.execute("SELECT * FROM opportunities WHERE source=? AND external_id=?",
                      (source, external_id)).fetchone()
        c.close()
        return _row_to_opp(r) if r else None

    def list_states(self, states: Optional[list[str]] = None) -> list[Opportunity]:
        c = _conn()
        if states:
            q = f"SELECT * FROM opportunities WHERE state IN ({','.join('?'*len(states))}) ORDER BY created_at DESC"
            rows = c.execute(q, states).fetchall()
        else:
            rows = c.execute("SELECT * FROM opportunities ORDER BY created_at DESC").fetchall()
        c.close()
        return [_row_to_opp(r) for r in rows]

    def add_event(self, opp_id: int, event: DomainEvent) -> None:
        c = _conn()
        r = c.execute(
            "INSERT INTO events (opp_id,kind,message,at,payload) VALUES (?,?,?,?,?)",
            (opp_id, event.kind, event.message, event.at, json.dumps(event.payload)))
        event.id = r.lastrowid
        c.commit()
        c.close()

    def events_for(self, opp_id: int) -> list[DomainEvent]:
        c = _conn()
        rows = c.execute("SELECT * FROM events WHERE opp_id=? ORDER BY id ASC",
                         (opp_id,)).fetchall()
        c.close()
        return [DomainEvent(kind=r["kind"], opp_id=r["opp_id"], message=r["message"],
                            at=r["at"], payload=json.loads(r["payload"] or "{}"), id=r["id"])
                for r in rows]


class SQLiteProfileStore(ProfileStore):
    def get(self) -> Profile:
        c = _conn()
        r = c.execute("SELECT * FROM profile WHERE id=1").fetchone()
        c.close()
        if not r:
            return Profile()
        hr = Money(r["min_hourly_rate"], r["min_hourly_currency"] or "USD") \
            if r["min_hourly_rate"] is not None else None
        fb = Money(r["min_fixed_budget"], r["min_fixed_currency"] or "USD") \
            if r["min_fixed_budget"] is not None else None
        return Profile(
            full_name=r["full_name"] or "", headline=r["headline"] or "",
            skills=json.loads(r["skills"] or "[]"),
            experience_years=r["experience_years"] or 0,
            summary=r["summary"] or "", portfolio_url=r["portfolio_url"] or "",
            min_hourly_rate=hr, min_fixed_budget=fb,
            remote_only=bool(r["remote_only"]),
            avoid_niches=json.loads(r["avoid_niches"] or "[]"),
            timezone=r["timezone"] or "UTC",
            upwork_profile_url=r["upwork_profile_url"] or "",
            fiverr_gig_urls=json.loads(r["fiverr_gig_urls"] or "[]"),
        )

    def save(self, p: Profile) -> None:
        c = _conn()
        hr = (p.min_hourly_rate.amount, p.min_hourly_rate.currency) \
            if p.min_hourly_rate else (None, None)
        fb = (p.min_fixed_budget.amount, p.min_fixed_budget.currency) \
            if p.min_fixed_budget else (None, None)
        c.execute(
            """UPDATE profile SET
               full_name=?,headline=?,skills=?,experience_years=?,summary=?,portfolio_url=?,
               min_hourly_rate=?,min_hourly_currency=?,min_fixed_budget=?,min_fixed_currency=?,
               remote_only=?,avoid_niches=?,timezone=?,upwork_profile_url=?,fiverr_gig_urls=?
               WHERE id=1""",
            (p.full_name, p.headline, json.dumps(p.skills), p.experience_years,
             p.summary, p.portfolio_url, hr[0], hr[1], fb[0], fb[1],
             int(p.remote_only), json.dumps(p.avoid_niches), p.timezone,
             p.upwork_profile_url, json.dumps(p.fiverr_gig_urls)))
        c.commit()
        c.close()
