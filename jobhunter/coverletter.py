def generate(profile, job):
    """Build a tailored cover letter from the user profile + a job listing."""
    profile = dict(profile)
    name = profile.get("full_name") or "Applicant"
    headline = profile.get("headline") or "a motivated professional"
    years = profile.get("experience_years") or 0
    skills = profile.get("skills") or ""
    summary = profile.get("summary") or ""
    portfolio = profile.get("portfolio_url") or ""
    job_title = job.get("title") or "this role"
    company = job.get("company") or "your company"

    skill_list = [s.strip() for s in skills.replace(",", "\n").split("\n") if s.strip()]
    hay = (job.get("description", "") + " " + job.get("tags", "")).lower()
    matched = [s for s in skill_list if s.lower() in hay]
    if matched:
        match_line = "I bring direct, hands-on experience with " + ", ".join(matched[:6]) + "."
    else:
        match_line = "I am quick to ramp up on new tools and technologies, and I learn fast."

    summary_line = summary or (
        "I am passionate about delivering high-quality work and collaborating closely "
        "with cross-functional teams to ship results that matter."
    )
    portfolio_line = (f"You can review more of my work here: {portfolio}") if portfolio else ""

    letter = f"""Dear Hiring Team at {company},

I am {name}, {headline} with {years} year(s) of experience. I am writing to express
my interest in the {job_title} position.

{match_line}

{summary_line}

{portfolio_line}

Thank you for your time and consideration. I would welcome the opportunity to discuss
how I can contribute to {company}.

Best regards,
{name}
"""
    return letter
