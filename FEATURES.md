# JobHunter ·AI — Features

> Agent hunts, you decide. An agent-first freelance opportunity dashboard.
> Architecture: Hexagonal + DDD + Event-Driven (see skill `hex-ddd-event-architecture`).

## What it does
The agent discovers freelance gigs, scores each against **your profile**, and surfaces only
the best-fit matches. You glance at the dashboard, read *why* each fits, and tap to approve.
On approval the agent drafts a proposal; the opportunity's progress is an event timeline.

## Features

### 1. "For You" board (agent-recommended)
- Default view. Shows only the agent's recommended/shortlisted opportunities
  (states: `proposed`, `promising`, `draft_ready`, `applied`, `interview`, `test`).
- Each card shows: match %, client, budget, skill tags, state badge, and the top score reasons.
- Sorted by match score (highest first).

### 2. "All" tab (full firehose)
- Every discovered opportunity, including `not_a_fit` rejects.
- Rejects show *why*: e.g. `Below minimum (25.0USD)`, `Avoid-niche: crypto`.
- The transparency that lets you trust (or override) the agent's calls.

### 3. Opportunity detail
- Full description, budget, tags, source link.
- **Progress timeline** — event projection: `discovered → scored → proposed → draft_ready → archived`.
- **Agent's draft proposal** (preview before approval; saved after).
- **1-tap actions:** `✅ Approve & let agent draft` · `✕ Pass` · `⧉ Copy pitch`.

### 4. Profile (view + edit)
- Drives all scoring. Fields: name, headline, skills, summary, min hourly rate, timezone,
  avoid-niches, portfolio URL, remote-only.
- Saved via `POST /api/profile`; auto-seeded with a demo Wahyu profile on first run.

### 5. Agent scan
- `↻ Agent scan` button (header) triggers discovery against the configured source and
  refreshes the board.

### 6. Score transparency
- Every opportunity carries a `MatchScore` with `value` + `reasons[]` (skill match, budget
  floor, seniority, remote, avoid-niche hits, verdict). Reasons are persisted and shown on cards.

## Architecture (lego layering)
```
domain/      PURE: models, ports, events, services/ (atoms + cells)
adapters/    SQLite repo (+event store + migration), SeedSource, HackerNewsSource, UpworkRssSource(stub)
components/  Discovery (wires source + cell + repo + event bus)
api/         FastAPI routes -> components/cells (thin composition root)
infra/       config (source selection, DB path)
```
- **Hexagonal:** domain has zero framework/IO deps; I/O via ports → adapters.
- **Event-Driven:** every state change emits a domain event; the card timeline = event projection.
- **Decoupled:** swap Upwork↔HackerNews↔Seed by configuring `JOB_SOURCE` (one adapter, no domain change).

## API
| Method | Path | Purpose |
|---|---|---|
| GET | `/api/opportunities?states=` | list opportunities (optional state filter) |
| GET | `/api/opportunities/{id}/timeline` | event timeline + opportunity |
| POST | `/api/discover` | run discovery (agent scan) |
| GET/POST | `/api/profile` | get / replace your profile |
| POST | `/api/opportunities/{id}/approve` | approve → draft proposal (state `draft_ready`) |
| POST | `/api/opportunities/{id}/pass` | archive (state `archived`) |
| POST | `/api/opportunities/{id}/preview-proposal` | draft proposal without state change (preview/copy) |

## Run it
```bash
# backend
cd job-hunter
python -m venv .venv && source .venv/Scripts/activate && unset PYTHONPATH
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000

# frontend (separate terminal)
cd job-hunter/frontend
npm install
npm run dev        # http://localhost:5173 (proxies /api -> :8000)
```
Open http://localhost:5173. The backend also serves the built SPA at `/` after `npm run build`.

## Discovery sources
- `seed` (default) — realistic Upwork-style fixtures for a clickable demo.
- `hackernews` — live public Hacker News Algolia API (discussion posts, not gigs — low match quality).
- `upwork` — **stub**; Upwork discontinued its public RSS (HTTP 410). Wire the official Upwork
  API adapter here once API access is granted. **Do not log the agent into your account to
  scrape** — ToS violation + ban risk (loses JSS/reputation). Use official API or email-apply.

## Verification
- Backend: `python -m app.smoke` (discover→score→propose on seed data).
- Frontend: `npm run build` (tsc + vite, must pass clean). UI flows verified in a real browser
  (board, All tab w/ rejects, detail timeline, approve/pass, profile save, agent scan, header nav).
- Ad-hoc checks: `hermes-verify-*.py` scripts (isolated temp DB) for repo/event/profile behavior.
```
