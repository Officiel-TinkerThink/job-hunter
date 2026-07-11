# JobHunter — Roadmap (LIVING DRAFT)

> Vision owner: Wahyu. Draft to refine together — not committed spec.
> **Priority (2026-07-11):** Wahyu has a full-time job → **freelance track is PRIORITY #1**.
> **Architecture (2026-07-11):** rebuilt on Hexagonal + DDD + Event-Driven, lego layering
> (atom→cell→component), strictly decoupled/replaceable. See skill `hex-ddd-event-architecture`.

## Vision
A **universal job-hunter + freelance-project-hunter**: the *agent* hunts, Wahyu only watches.
Every opportunity = a **card**; clicking shows a **progress timeline** (event projection).
- Agent discovers opportunities that fit Wahyu and creates cards automatically.
- Agent can **send emails** and (later) **fill forms** to apply.
- **Freelance (PRIORITY):** Upwork (bid on posted projects) + Fiverr (maintain gigs, answer
  buyer requests). DIFFERENT marketplace models → separate components/modules.
- **Escalation rule:** agent only contacts Wahyu for a **test to complete** or an
  **interview to attend**. Everything else silent / shown in progress.

## Architecture decision (locked before coding)
Convention captured in skill `hex-ddd-event-architecture`. Shape:
- **Hexagonal:** domain core has no framework/DB/API deps. I/O via ports → adapters.
- **DDD:** aggregates `Opportunity`, `Proposal`, `Profile`, `Preference`; value objects
  `Rate`, `Skill`, `MatchScore`. Bounded contexts: Discovery / Proposal / Notification / Inbox.
- **Event-Driven:** each state change emits a domain event; the card timeline = event projection.
- **Lego layering:** atom (pure, reusable) → cell (one use-case) → component (feature module)
  → app shell (composition root, thin). Reuse, never recreate.
- **Decoupled:** swap Upwork↔LinkedIn by writing ONE adapter + zero domain changes.
- **Start lean:** in-process event dispatcher; one working path (Upwork RSS→score→propose)
  proves the architecture before adding channels.
- **ToS:** adapters stay human-in-loop until official APIs exist.

Target structure:
```
app/
  main.py            # composition root
  domain/            # PURE: models.py, ports.py, events.py, services/ (atoms+cells)
  adapters/          # upwork_rss, fiverr, smtp_mailer, sqlite_repo, imap_inbox
  components/        # discovery, outreach, notification
  api/               # routes_opportunities.py (HTTP -> components/cells)
  infra/             # event bus impl, db session, scheduler
templates/ static/ data.db
```
Lint rule: `domain` must not import `adapters`.

## UI / UX principle (locked)
The site is **user-readable but agent-first**. The agent monitors sources, scores, and
**recommends** jobs that suit Wahyu; the UI surfaces only the agent's best picks for a
1-tap approve/reject. Design for TWO readers:
- **Agent:** clean structured data, transparent match scores + reasons it can act on.
- **Wahyu:** glanceable, trustworthy dashboard — "here's what I found for you + why", tap to act.
Default view = agent-recommended / shortlisted opportunities, **NOT a raw firehose**.
BeaverHand-inspired shell (bold hero + search CTA, category tiles, minimal nav, airy/professional).
Stack: React + Vite + Tailwind + Framer Motion (approved).
1. **ToS / account bans = #1 risk.** LinkedIn + Upwork ban aggressively; Fiverr too.
   Banned = loss of reputation (Upwork JSS, Fiverr ranking) you can't rebuild.
   - Safe + automatable: **email-apply** path.
   - Human-in-loop / official-API only: web-form apply, LinkedIn scraping.
2. **Fiverr ≠ Upwork (structurally different):**
   - **Upwork** = you *bid* on posted jobs (spend **Connects**, real money). Active.
   - **Fiverr** = passive *gig storefront*; buyers come to you. No "apply to project".
     Closest is answering **Buyer Requests / Briefs**. Optimize gig SEO. Separate module.
3. **"Good for me" must be explicit:** skills, seniority, **min rate / budget floor**,
   remote-only?, timezone, industries to avoid, scam/MLM red flags. Currently demo "Jane Doe".
4. **Autonomy vs quality / cost:** Upwork bids spend **Connects ($)**. Scattershot auto-bidding
   burns cash AND lowers JSS. Start **propose-then-approve** (protect Connects + JSS); widen
   autonomy as match quality proves out.
5. **Profile quality is the ceiling:** proposal win-rate depends on a strong Upwork/Fiverr
   profile. Invest there first; the agent can't fix a weak profile.
6. **"Only ping for test/interview" needs inbox intelligence:** IMAP + LLM classify replies;
   conservative threshold + daily digest fallback so nothing drops silently.

## Freelance-hunter flow (mature, event-driven) — RECOMMENDED
Each step = a **cell** that emits a domain event; the opportunity card timeline = event projection.

1. **Discover** — adapter polls Upwork RSS / Fiverr briefs → emits `OpportunityDiscovered`
   → creates `Opportunity` (state: NEW). Safe, ToS-clean (public RSS).
2. **Score / Match** — cell `ScoreOpportunity` (match_score atom vs Profile preferences) →
   emits `OpportunityScored` with MatchScore + reason → state PROMISING / NOT_A_FIT.
   Low-confidence → archived silently (no card spam).
3. **Decide (gate)** — if score ≥ high threshold AND autonomy allows → auto-stage DRAFT;
   else → stays PROPOSED (card shown for 1-tap approve). Protects Connects + JSS.
4. **Draft** — cell `DraftProposal` (cover_letter atom + Profile + job) → emits
   `ProposalDrafted` → state DRAFT_READY. Proposal text stored on the opportunity.
5. **Submit / Apply** — adapter (Upwork connector; start human-in-loop via 1-tap, later auto
   via permitted path). Email-apply jobs → SMTP adapter sends. Emits `ApplicationSubmitted`
   → state APPLIED.
6. **Follow-up** (later) — scheduled cell detects silence, drafts a nudge (state FOLLOWED_UP).
7. **Inbox / Classify** — adapter IMAP poller → `classify_reply` atom → emits `ReplyReceived`
   (kind: interview / test / rejection / spam). test|interview → **escalate** (notify Wahyu
   + state INTERVIEW/TEST); else → log to timeline only. Daily digest fallback.
8. **Close** — state WON / LOST. Feeds back into match-quality learning.

Upwork-first (clear "bid" action to build toward); Fiverr second (profile/SEO + brief answers).

## Phased plan (FREELANCE-FIRST, architecture-aligned)
- **P0 — Foundation (restructure + timeline):** adopt hex/DDD/ED skeleton; `Opportunity`
  aggregate + `events` timeline table; opportunity **card + timeline** UI (works for Upwork
  jobs AND Fiverr briefs). One working path: Upwork RSS → score → propose. LOW RISK. ← START
- **P1 — Freelance discovery:** agent polls Upwork RSS + Fiverr briefs, scores vs profile,
  auto-creates cards (default PROPOSED; high-confidence auto-staged).
- **P2 — Upwork outreach:** DraftProposal cell + SubmitApplication (start propose-then-approve
  to protect Connects + JSS); email-apply via SMTP adapter.
- **P3 — Fiverr gig-maintainer:** optimize gig SEO/pricing; answer buyer requests/briefs.
- **P4 — Inbox monitor + auto-reply:** IMAP classify → escalate test/interview; draft routine replies.
- **P5 — Channels + full-time job modules** (LinkedIn scraping behind ToS-risk toggle, etc.)

## Open decisions (needed to scope P0)
- [x] Jobs vs freelance first? → **FREELANCE FIRST**
- [x] Architecture? → **Hexagonal + DDD + Event-Driven, lego layering**
- [ ] Real Wahyu profile + "good for me" rules (skills, min rate/budget floor, remote-only, timezone, dealbreakers)
- [ ] Risk appetite: fully auto vs propose-then-approve-top (recommend latter — protects Connects + JSS)
- [ ] Upwork + Fiverr accounts live? Which first (recommend Upwork)
- [ ] Runtime: this laptop (manual start) vs always-on (cron/server) — autonomy needs scheduling
