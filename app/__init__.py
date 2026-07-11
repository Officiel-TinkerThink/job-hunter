"""JobHunter freelance core — Hexagonal + DDD + Event-Driven.

Package layout:
  domain/    pure business logic (no framework / IO imports)
  adapters/  implement ports; only place with external SDKs / network
  components/ feature modules wiring cells + adapters
  api/       HTTP layer (FastAPI routes)
  infra/     event bus, db session, config
"""
