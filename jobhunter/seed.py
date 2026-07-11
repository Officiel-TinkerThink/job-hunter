from datetime import datetime
from jobhunter import db

SAMPLE_JOBS = [
    ("remotive", "r1", "Remote Python Developer", "Acme Labs", "Worldwide",
     "https://example.com/j1", "We need a Python dev for our API.",
     "Python, Flask, SQL", "$60k-80k"),
    ("remotive", "r2", "React Frontend Engineer", "Globex", "Remote",
     "https://example.com/j2", "Build UI with React.",
     "React, JavaScript", "$50k-70k"),
    ("adzuna", "a1", "Backend Engineer", "Initech", "London",
     "https://example.com/j3", "Python microservices.",
     "Python", "GBP 40k-60k"),
]


def seed():
    db.init_db()
    db.save_profile(
        full_name="Jane Doe",
        email="jane@example.com",
        phone="+1 555 0100",
        headline="Full-stack Python developer",
        experience_years=4,
        skills="Python, Flask, React, SQL, AWS, Docker",
        summary="I build reliable web apps end-to-end and care about clean, tested code.",
        portfolio_url="https://github.com/janedoe",
    )
    now = datetime.utcnow().isoformat()
    for s in SAMPLE_JOBS:
        exists = db.q("SELECT id FROM jobs WHERE source=? AND ext_id=?", (s[0], s[1]))
        if not exists:
            db.execute(
                """INSERT INTO jobs
                   (source, ext_id, title, company, location, url, description, tags, salary, posted_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7], s[8], now),
            )
    print("Seeded demo profile + sample jobs.")


if __name__ == "__main__":
    seed()
