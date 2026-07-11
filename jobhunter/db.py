import sqlite3
import os
from .config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS profile (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    full_name TEXT,
    email TEXT,
    phone TEXT,
    headline TEXT,
    skills TEXT,
    experience_years INTEGER,
    summary TEXT,
    portfolio_url TEXT,
    resume_path TEXT
);

CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,
    ext_id TEXT,
    title TEXT,
    company TEXT,
    location TEXT,
    url TEXT,
    description TEXT,
    tags TEXT,
    salary TEXT,
    posted_at TEXT,
    raw_json TEXT,
    UNIQUE(source, ext_id)
);

CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER,
    status TEXT DEFAULT 'applied',
    applied_at TEXT,
    cover_letter TEXT,
    notes TEXT,
    interview_at TEXT,
    FOREIGN KEY(job_id) REFERENCES jobs(id)
);

CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kind TEXT,
    message TEXT,
    created_at TEXT,
    read INTEGER DEFAULT 0
);
"""


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_conn()
    conn.executescript(SCHEMA)
    conn.commit()
    cur = conn.execute("SELECT id FROM profile WHERE id=1")
    if not cur.fetchone():
        conn.execute("INSERT INTO profile (id) VALUES (1)")
        conn.commit()
    conn.close()


def q(sql, params=()):
    conn = get_conn()
    cur = conn.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return rows


def execute(sql, params=()):
    conn = get_conn()
    cur = conn.execute(sql, params)
    conn.commit()
    last = cur.lastrowid
    conn.close()
    return last


def get_profile():
    rows = q("SELECT * FROM profile WHERE id=1")
    return dict(rows[0]) if rows else {}


def save_profile(**fields):
    sets = ", ".join(f"{k}=?" for k in fields)
    execute(f"UPDATE profile SET {sets} WHERE id=1", tuple(fields.values()))
