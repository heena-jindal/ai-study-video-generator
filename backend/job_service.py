"""
job_service.py

Tracks video generation jobs in SQLite instead of an in-memory dict.
Reason: gunicorn can run multiple WORKER PROCESSES, each with its own
separate memory space. If job status lived in a plain Python dict, a job
started by worker A would be invisible to a status-check request that
happens to land on worker B. SQLite is a real file on disk, readable by
any worker process regardless of which one handles which request --
same underlying lesson as Study Companion's weak-topic tracking, applied
here for a different reason (cross-PROCESS visibility, not cross-REQUEST
memory).

Known limitation, stated honestly: if the specific worker process running
a job's background thread crashes or restarts mid-job, that job is lost
(stuck at "running" forever). A production system would use a real task
queue (Celery, RQ) with proper worker recovery. For this project's scope,
threading + SQLite status tracking is a reasonable v1 -- not bulletproof,
but a deliberate, known tradeoff, not an oversight.
"""

import sqlite3
import uuid
from datetime import datetime, timezone

DB_PATH = "jobs.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            topic TEXT NOT NULL,
            status TEXT NOT NULL,
            video_path TEXT,
            error TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def create_job(topic: str) -> str:
    job_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO jobs (id, topic, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
        (job_id, topic, "pending", now, now),
    )
    conn.commit()
    conn.close()
    return job_id


def update_job(job_id: str, status: str, video_path: str = None, error: str = None):
    now = datetime.now(timezone.utc).isoformat()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE jobs SET status = ?, video_path = ?, error = ?, updated_at = ? WHERE id = ?",
        (status, video_path, error, now, job_id),
    )
    conn.commit()
    conn.close()


def get_job(job_id: str) -> dict:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    conn.close()
    return dict(row) if row else None