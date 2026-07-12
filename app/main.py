"""App factory — builds the composed FastAPI app.

Modern structure: no wiring at import time. `create_app()` wires the router,
the event-sink subscriber, the idempotent demo-profile seed, and the built SPA.
`uvicorn app.main:app` works because we expose a module-level `app` singleton.
"""
from __future__ import annotations

from fastapi import FastAPI

from .api.routes_opportunities import router, register_event_sink, mount_spa, _seed_demo_profile
from .api import deps


def create_app() -> FastAPI:
    app = FastAPI(title="JobHunter · Freelance", version="0.3.0")

    app.include_router(router)
    register_event_sink(app)

    # Idempotent demo profile so scoring works out of the box.
    _seed_demo_profile(deps.get_profiles())

    mount_spa(app)
    return app


app = create_app()
