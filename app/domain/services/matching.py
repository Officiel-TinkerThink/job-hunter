"""Atoms — pure, reusable, side-effect-free functions (no I/O, no framework)."""
from __future__ import annotations

from ..models import MatchScore, Money, Opportunity, Profile


def match_score(profile: Profile, opp: Opportunity) -> MatchScore:
    """Score an opportunity against Wahyu's profile.

    Pure function: same input → same score. This is the reusable "atom" the
    discovery cell depends on. Transparent reasoning so Wahyu can trust it.
    """
    reasons: list[str] = []
    score = 0.0

    # 1. Skill overlap (up to 0.45) — scan tags AND summary text
    if profile.skills:
        skill_set = {s.lower() for s in profile.skills}
        text = " ".join(opp.tags).lower() + " " + opp.summary.lower()
        opp_terms = set()
        for s in skill_set:
            if s in text:
                opp_terms.add(s)
        if opp_terms:
            ratio = len(opp_terms) / max(1, len(skill_set))
            score += min(0.45, 0.45 * (len(opp_terms) / 3 + 0.2))
            reasons.append(f"Skill match: {', '.join(sorted(opp_terms))}")
        else:
            reasons.append("No skill overlap")
    else:
        reasons.append("No skills configured")

    # 2. Budget / rate floor (gate, not additive)
    meets_floor = True
    if opp.budget is not None:
        floor = (profile.min_hourly_rate if opp.budget.currency == "USD"
                 else profile.min_fixed_budget)
        if floor is not None:
            if opp.budget < floor:
                meets_floor = False
                reasons.append(f"Below minimum ({floor.amount}{floor.currency})")
            else:
                score += 0.20
                reasons.append("Meets budget floor")

    # 3. Avoid-list / red-flag niches (penalize hard)
    lowered = (opp.title + " " + opp.summary).lower()
    hits = [n for n in profile.avoid_niches if n.lower() in lowered]
    if hits:
        score -= 0.30 * len(hits)
        reasons.append(f"Avoid-niche hit: {', '.join(hits)}")

    # 4. Experience relevance (up to 0.15)
    if profile.experience_years >= 3:
        score += 0.15
        reasons.append("Seniority match (3y+)")

    # 5. Remote (Upwork/Fiverr are remote by nature; small bonus)
    if profile.remote_only:
        score += 0.10
        reasons.append("Remote-friendly")

    score = max(0.0, min(1.0, score))
    if meets_floor and score >= 0.7:
        reasons.append("VERDICT: promising — auto-stage candidate")
    elif not meets_floor:
        reasons.append("VERDICT: not a fit (below floor)")
    else:
        reasons.append("VERDICT: review — awaiting approval")
    return MatchScore(value=round(score, 3), reasons=reasons, meets_floor=meets_floor)
