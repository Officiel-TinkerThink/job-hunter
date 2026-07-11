"""FastAPI composition root — thin wiring only.

Routes call components/cells; adapters are injected here. No business logic.
"""
from __future__ import annotations
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ..adapters.sqlite_repo import SQLiteOpportunityRepo, SQLiteProfileStore, init_db
from ..adapters.hackernews import HackerNewsSource
from ..adapters.seed_source import SeedSource
from ..adapters.upwork_rss import UpworkRssSource
from ..domain.events import EventBus
from ..components.discovery import Discovery
from ..domain.services.decision import ApproveOpportunity, PassOpportunity
from ..domain.services.preview_proposal import PreviewProposal
from ..infra.config import JOB_SOURCE

BASE_DIR = Path(__file__).resolve().parent.parent

# --- wiring (composition root) -------------------------------------------
init_db()
bus = EventBus()
repo = SQLiteOpportunityRepo()
profiles = SQLiteProfileStore()

# Auto-seed a demo Wahyu profile on first run so scoring works out of the box.
# Replace via POST /api/profile with your real "good for me" preferences.
if not profiles.get().skills:
    from ..domain.models import Money, Profile
    profiles.save(Profile(
        full_name="Wahyu Sinurat", headline="Full-stack Python / React developer",
        skills=["python", "react", "fastapi", "django", "aws", "docker", "sql"],
        experience_years=4, summary="I build reliable web apps end-to-end.",
        portfolio_url="https://github.com/Officiel-TinkerThink",
        min_hourly_rate=Money(25, "USD"), remote_only=True,
        avoid_niches=["crypto", "mlm"], timezone="Asia/Jakarta",
    ))

_SOURCE_MAP = {"seed": SeedSource, "hackernews": HackerNewsSource, "upwork": UpworkRssSource}
_source_cls = _SOURCE_MAP.get(JOB_SOURCE, SeedSource)
_source = _source_cls()
discovery = Discovery(_source, repo, profiles, bus)
approve_opp = ApproveOpportunity(repo, profiles, bus)
pass_opp = PassOpportunity(repo, bus)
preview_proposal = PreviewProposal(repo, profiles)

# Escalation + persistence sink: every event is stored (timeline projection);
# "action needed" events are also flagged for notification (email/notify later).
def _on_event(e):
    repo.add_event(e.opp_id, e)
    if e.kind == "escalated":
        print(f"[ESCALATE] {e.message}")
bus.subscribe(_on_event)

app = FastAPI(title="JobHunter · Freelance", version="0.2.0")


class ProfileIn(BaseModel):
    full_name: str = ""
    headline: str = ""
    skills: list[str] = []
    experience_years: int = 0
    summary: str = ""
    portfolio_url: str = ""
    min_hourly_rate: float | None = None
    min_fixed_budget: float | None = None
    remote_only: bool = True
    avoid_niches: list[str] = []
    timezone: str = "UTC"
    upwork_profile_url: str = ""
    fiverr_gig_urls: list[str] = []


def _opp_json(o):
    return {
        "id": o.id, "source": o.source.value, "title": o.title, "url": o.url,
        "client": o.client, "summary": o.summary,
        "budget": (f"{o.budget.amount:g} {o.budget.currency}" if o.budget else None),
        "tags": o.tags, "state": o.state.value,
        "score": o.score.value if o.score else None,
        "score_reasons": o.score.reasons if o.score else [],
        "proposal": o.proposal,
        "created_at": o.created_at,
    }


@app.get("/api/profile")
def get_profile():
    p = profiles.get()
    return {
        "full_name": p.full_name, "headline": p.headline, "skills": p.skills,
        "experience_years": p.experience_years, "summary": p.summary,
        "portfolio_url": p.portfolio_url,
        "min_hourly_rate": p.min_hourly_rate.amount if p.min_hourly_rate else None,
        "min_fixed_budget": p.min_fixed_budget.amount if p.min_fixed_budget else None,
        "remote_only": p.remote_only, "avoid_niches": p.avoid_niches,
        "timezone": p.timezone, "upwork_profile_url": p.upwork_profile_url,
        "fiverr_gig_urls": p.fiverr_gig_urls,
    }


@app.post("/api/profile")
def set_profile(p: ProfileIn):
    from ..domain.models import Money, Profile
    profiles.save(Profile(
        full_name=p.full_name, headline=p.headline, skills=p.skills,
        experience_years=p.experience_years, summary=p.summary,
        portfolio_url=p.portfolio_url,
        min_hourly_rate=Money(p.min_hourly_rate) if p.min_hourly_rate else None,
        min_fixed_budget=Money(p.min_fixed_budget) if p.min_fixed_budget else None,
        remote_only=p.remote_only, avoid_niches=p.avoid_niches,
        timezone=p.timezone, upwork_profile_url=p.upwork_profile_url,
        fiverr_gig_urls=p.fiverr_gig_urls,
    ))
    return {"ok": True}


@app.post("/api/discover")
def discover():
    summary = discovery.run()
    return summary


@app.get("/api/opportunities")
def list_opportunities(states: str | None = None):
    state_list = states.split(",") if states else None
    opps = repo.list_states(state_list)
    return [_opp_json(o) for o in opps]


@app.post("/api/opportunities/{opp_id}/approve")
def approve(opp_id: int):
    try:
        approve_opp(opp_id)
    except ValueError:
        return JSONResponse({"error": "not found"}, status_code=404)
    return {"ok": True, "state": "draft_ready"}


@app.post("/api/opportunities/{opp_id}/pass")
def reject(opp_id: int):
    try:
        pass_opp(opp_id)
    except ValueError:
        return JSONResponse({"error": "not found"}, status_code=404)
    return {"ok": True, "state": "archived"}


@app.post("/api/opportunities/{opp_id}/preview-proposal")
def preview(opp_id: int):
    try:
        text = preview_proposal(opp_id)
    except ValueError:
        return JSONResponse({"error": "not found"}, status_code=404)
    return {"proposal": text}


@app.get("/api/opportunities/{opp_id}/timeline")
def timeline(opp_id: int):
    opp = repo.get(opp_id)
    if not opp:
        return JSONResponse({"error": "not found"}, status_code=404)
    evs = repo.events_for(opp_id)
    return {
        "opportunity": _opp_json(opp),
        "events": [{"kind": e.kind, "message": e.message, "at": e.at,
                    "payload": e.payload} for e in evs],
    }


# Serve the built React app (produced by the frontend build step)
DIST = BASE_DIR.parent / "frontend" / "dist"
if DIST.exists():
    app.mount("/", StaticFiles(directory=str(DIST), html=True), name="spa")
