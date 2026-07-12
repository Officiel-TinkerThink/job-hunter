"""FastAPI routes — async, typed via pydantic v2 schemas, DI via Depends.

Business logic lives in domain components/cells; adapters are injected through
`deps`. Sync repo/SMTP calls run in a threadpool so the event loop stays free.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.concurrency import run_in_threadpool

from .schemas import (
    ApplyResult, DiscoverResult, OkResult, OpportunityOut, ProfileIn, ProfileOut,
    TimelineOut,
)
from . import deps
from ..domain.events import DomainEvent
from ..domain.models import Money, Profile, OpportunityState

router = APIRouter(prefix="/api")


def _opp_json(o) -> OpportunityOut:
    return OpportunityOut(
        id=o.id, source=o.source.value, title=o.title, url=o.url, client=o.client,
        summary=o.summary,
        budget=(f"{o.budget.amount:g} {o.budget.currency}" if o.budget else None),
        tags=o.tags, state=o.state.value,
        score=o.score.value if o.score else None,
        score_reasons=o.score.reasons if o.score else [],
        proposal=o.proposal or "", created_at=o.created_at,
    )


def _seed_demo_profile(profiles) -> None:
    """Idempotent demo profile so scoring works out of the box. Replace via UI."""
    if profiles.get().skills:
        return
    profiles.save(Profile(
        full_name="Wahyu Sinurat", headline="Full-stack Python / React developer",
        skills=["python", "react", "fastapi", "django", "aws", "docker", "sql"],
        experience_years=4, summary="I build reliable web apps end-to-end.",
        portfolio_url="https://github.com/Officiel-TinkerThink",
        min_hourly_rate=Money(25, "USD"), remote_only=True,
        avoid_niches=["crypto", "mlm"], timezone="Asia/Jakarta",
    ))


@router.get("/profile", response_model=ProfileOut)
async def get_profile(profiles=Depends(deps.get_profiles)) -> ProfileOut:
    p = await run_in_threadpool(profiles.get)
    return ProfileOut(
        full_name=p.full_name, headline=p.headline, skills=p.skills,
        experience_years=p.experience_years, summary=p.summary,
        portfolio_url=p.portfolio_url,
        min_hourly_rate=p.min_hourly_rate.amount if p.min_hourly_rate else None,
        min_fixed_budget=p.min_fixed_budget.amount if p.min_fixed_budget else None,
        remote_only=p.remote_only, avoid_niches=p.avoid_niches,
        timezone=p.timezone, upwork_profile_url=p.upwork_profile_url,
        fiverr_gig_urls=p.fiverr_gig_urls,
    )


@router.post("/profile", response_model=OkResult)
async def set_profile(p: ProfileIn, profiles=Depends(deps.get_profiles)) -> OkResult:
    await run_in_threadpool(profiles.save, Profile(
        full_name=p.full_name, headline=p.headline, skills=p.skills,
        experience_years=p.experience_years, summary=p.summary,
        portfolio_url=p.portfolio_url,
        min_hourly_rate=Money(p.min_hourly_rate) if p.min_hourly_rate else None,
        min_fixed_budget=Money(p.min_fixed_budget) if p.min_fixed_budget else None,
        remote_only=p.remote_only, avoid_niches=p.avoid_niches,
        timezone=p.timezone, upwork_profile_url=p.upwork_profile_url,
        fiverr_gig_urls=p.fiverr_gig_urls,
    ))
    return OkResult()


@router.post("/discover", response_model=DiscoverResult)
async def discover(discovery=Depends(deps.get_discovery)) -> DiscoverResult:
    s = await run_in_threadpool(discovery.run)
    return DiscoverResult(**s)


@router.get("/opportunities", response_model=list[OpportunityOut])
async def list_opportunities(
    states: str | None = None, repo=Depends(deps.get_repo)
) -> list[OpportunityOut]:
    state_list = states.split(",") if states else None
    opps = await run_in_threadpool(repo.list_states, state_list)
    return [_opp_json(o) for o in opps]


@router.post("/opportunities/{opp_id}/approve", response_model=OkResult)
async def approve(opp_id: int, cell=Depends(deps.get_approve)) -> OkResult:
    try:
        await run_in_threadpool(cell, opp_id)
    except ValueError:
        return JSONResponse({"error": "not found"}, status_code=404)
    return OkResult()


@router.post("/opportunities/{opp_id}/pass", response_model=OkResult)
async def reject(opp_id: int, cell=Depends(deps.get_pass)) -> OkResult:
    try:
        await run_in_threadpool(cell, opp_id)
    except ValueError:
        return JSONResponse({"error": "not found"}, status_code=404)
    return OkResult()


@router.post("/opportunities/{opp_id}/preview-proposal")
async def preview(opp_id: int, cell=Depends(deps.get_preview)):
    try:
        text = await run_in_threadpool(cell, opp_id)
    except ValueError:
        return JSONResponse({"error": "not found"}, status_code=404)
    return {"proposal": text}


@router.post("/opportunities/{opp_id}/apply", response_model=ApplyResult)
async def apply(opp_id: int, cell=Depends(deps.get_submit)) -> ApplyResult:
    try:
        r = await run_in_threadpool(cell, opp_id)
    except ValueError:
        return JSONResponse({"error": "not found"}, status_code=404)
    return ApplyResult(**r)


@router.get("/opportunities/{opp_id}/timeline", response_model=TimelineOut)
async def timeline(opp_id: int, repo=Depends(deps.get_repo)):
    opp = await run_in_threadpool(repo.get, opp_id)
    if not opp:
        return JSONResponse({"error": "not found"}, status_code=404)
    evs = await run_in_threadpool(repo.events_for, opp_id)
    return TimelineOut(
        opportunity=_opp_json(opp),
        events=[TimelineEvent(kind=e.kind, message=e.message, at=e.at, payload=e.payload)
                for e in evs],
    )


def register_event_sink(app) -> None:
    """Persist every domain event as the timeline projection (sink subscriber)."""
    bus = deps.get_bus()
    repo = deps.get_repo()

    def _on_event(e: DomainEvent) -> None:
        repo.add_event(e.opp_id, e)
        if e.kind == "escalated":
            print(f"[ESCALATE] {e.message}")

    bus.subscribe(_on_event)


def mount_spa(app) -> None:
    BASE_DIR = Path(__file__).resolve().parent.parent
    DIST = BASE_DIR.parent / "frontend" / "dist"
    if DIST.exists():
        app.mount("/", StaticFiles(directory=str(DIST), html=True), name="spa")
