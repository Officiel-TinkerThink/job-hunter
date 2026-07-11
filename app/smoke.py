"""Smoke test: runs discovery end-to-end against the real Upwork RSS feed.

Usage:  python -m app.smoke
"""
from .adapters.sqlite_repo import SQLiteOpportunityRepo, SQLiteProfileStore, init_db
from .adapters.seed_source import SeedSource
from .components.discovery import Discovery
from .domain.events import EventBus
from .domain.models import Money, Profile


def main():
    init_db()
    bus = EventBus()
    repo = SQLiteOpportunityRepo()
    profiles = SQLiteProfileStore()
    # a demo Wahyu profile so scoring is meaningful
    profiles.save(Profile(
        full_name="Wahyu Sinurat", headline="Full-stack Python / React developer",
        skills=["python", "react", "fastapi", "django", "aws", "docker", "sql"],
        experience_years=4, summary="I build reliable web apps end-to-end.",
        portfolio_url="https://github.com/Officiel-TinkerThink",
        min_hourly_rate=Money(25, "USD"), remote_only=True,
        avoid_niches=["crypto", "mlm"], timezone="Asia/Jakarta",
    ))
    disc = Discovery(SeedSource(), repo, profiles, bus)
    print("Running discovery against seed (realistic Upwork-style listings) ...")
    summary = disc.run()
    print("RESULT:", summary)
    print("\nOpportunities (state, score):")
    for o in repo.list_states():
        score = o.score.value if o.score else 0
        print(f"  [{o.state.value:10}] {score:.0%}  {o.title[:60]}  ({o.budget})")


if __name__ == "__main__":
    main()
