"""Config — injected at composition root; never imported deep in the core."""
from __future__ import annotations
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # app/infra -> project root
DATA_DIR = BASE_DIR / "data"
DB_PATH = os.environ.get("JOBHUNTER_DB", str(DATA_DIR / "jobhunter.db"))

# Discovery source selection. Upwork's public RSS was discontinued (HTTP 410),
# so the working default is SeedSource (realistic Upwork-style listings) for a
# clickable demo, with HackerNews as a live public feed. Swap to an official
# Upwork API adapter once access is available.
JOB_SOURCE = os.environ.get("JOB_SOURCE", "seed")
