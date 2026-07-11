"""In-memory seed source — implements JobSource port.

Provides realistic Upwork-style freelance listings so the full pipeline
(discover -> score -> propose -> timeline) is demoable immediately, without
depending on a gated live feed. Swap for a live adapter (Upwork API / HN)
in production. Tags + summary are populated so matching is meaningful.
"""
from __future__ import annotations

from ..domain.models import Money, Opportunity, Source
from ..domain.ports import JobSource

SEED = [
    ("Senior Python / FastAPI Developer", "Acme Labs",
     "Build a high-throughput API in FastAPI + Postgres. Docker, AWS deploy.",
     Money(40, "USD"), ["python", "fastapi", "postgres", "docker", "aws"]),
    ("React Frontend Engineer", "Globex",
     "React + TypeScript dashboard, Tailwind, REST integration.",
     Money(35, "USD"), ["react", "typescript", "tailwind"]),
    ("Full-stack Developer (Django + React)", "Initech",
     "End-to-end feature work on a SaaS. Django backend, React frontend.",
     Money(38, "USD"), ["python", "django", "react"]),
    ("DevOps / CI Pipeline Help", "Umbrella",
     "Set up GitHub Actions + Docker + AWS ECS. Terraform a plus.",
     Money(45, "USD"), ["devops", "docker", "aws"]),
    ("Scrape LinkedIn data (grey area)", "SketchyCo",
     "Automate scraping of LinkedIn profiles. Crypto paid.",
     Money(80, "USD"), ["python", "crypto"]),
    ("ML engineer for NLP chatbot", "Hooli",
     "Fine-tune an LLM, build a RAG pipeline. Python + SQL.",
     Money(50, "USD"), ["python", "machine learning", "nlp", "sql"]),
    ("WordPress fix for $5", "PennySavers",
     "Small CSS tweak on a WordPress site.",
     Money(5, "USD"), ["css"]),
    ("React Native mobile app", "PiedPiper",
     "Cross-platform app, React Native + Node backend.",
     Money(42, "USD"), ["react", "node", "sql"]),
]


class SeedSource(JobSource):
    def __init__(self, items=None):
        self.items = items or SEED

    def discover(self):
        out = []
        for i, (title, client, summary, budget, tags) in enumerate(self.items):
            out.append(Opportunity(
                source=Source.UPWORK, external_id=f"seed_{i}", title=title,
                url=f"https://example.com/job/{i}", client=client,
                summary=summary, budget=budget, tags=tags,
            ))
        return out
