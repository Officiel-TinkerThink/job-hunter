"""Atoms — proposal drafting (pure template, no I/O)."""
from __future__ import annotations

from ..models import Opportunity, Profile


def draft_proposal(profile: Profile, opp: Opportunity) -> str:
    """Generate a tailored cover/proposal letter from profile + opportunity.

    Pure function (the reusable atom). Real version later can call an LLM;
    the cell just swaps this atom for an LLM-backed one.
    """
    skills_line = ", ".join(profile.skills) if profile.skills else "relevant skills"
    return (
        f"Hi {opp.client or 'there'},\n\n"
        f"I'm {profile.full_name}, {profile.headline}. "
        f"I came across your project \"{opp.title}\" and it's a strong fit for my "
        f"background in {skills_line} ({profile.experience_years}+ years).\n\n"
        f"{profile.summary}\n\n"
        f"For this project I'd focus on delivering exactly what you described: "
        f"{opp.summary or 'the scope outlined'}. "
        f"I can start promptly and keep you updated throughout.\n\n"
        f"You can see more of my work here: {profile.portfolio_url or 'my profile'}.\n\n"
        f"Happy to hop on a quick call to align before we begin.\n\n"
        f"Best,\n{profile.full_name}"
    )
