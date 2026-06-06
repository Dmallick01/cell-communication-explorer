"""Synchronous job store updates for pipeline worker threads."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import settings
from app.models.schemas import JobStatus, PipelineStep


def _db_path() -> Path:
    url = settings.database_url
    if url.startswith("sqlite+aiosqlite:///"):
        return Path(url.replace("sqlite+aiosqlite:///", ""))
    raise ValueError("Sync store only supports SQLite")


def update_step_sync(
    job_id: str,
    step: str,
    status: str,
    message: str | None = None,
    checkpoint: bool | None = None,
) -> None:
    db = _db_path()
    now = datetime.now(timezone.utc).isoformat()

    conn = sqlite3.connect(db)
    try:
        row = conn.execute(
            "SELECT steps_json, status FROM jobs WHERE id = ?", (job_id,)
        ).fetchone()
        if not row:
            return

        import json

        steps_data = json.loads(row[0]) if row[0] else {"steps": []}
        steps = steps_data.get("steps", [])

        for s in steps:
            if s["step"] == step:
                s["status"] = status
                if message is not None:
                    s["message"] = message
                if checkpoint is not None:
                    s["checkpoint_passed"] = checkpoint
                if status == JobStatus.RUNNING.value and "started_at" not in s:
                    s["started_at"] = now
                if status in (JobStatus.COMPLETED.value, JobStatus.FAILED.value):
                    s["completed_at"] = now

        job_status = row[1]
        if status == JobStatus.RUNNING.value and job_status == JobStatus.QUEUED.value:
            job_status = JobStatus.RUNNING.value

        conn.execute(
            """
            UPDATE jobs
            SET steps_json = ?, current_step = ?, status = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                json.dumps({"steps": steps}),
                step,
                job_status,
                datetime.now(timezone.utc).isoformat(),
                job_id,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def update_job_sync(
    job_id: str,
    *,
    status: str | None = None,
    error: str | None = None,
    results_json: str | None = None,
) -> None:
    conn = sqlite3.connect(_db_path())
    try:
        fields = ["updated_at = ?"]
        values: list[str] = [datetime.now(timezone.utc).isoformat()]

        if status is not None:
            fields.append("status = ?")
            values.append(status)
        if error is not None:
            fields.append("error = ?")
            values.append(error)
        if results_json is not None:
            fields.append("results_json = ?")
            values.append(results_json)

        values.append(job_id)
        conn.execute(f"UPDATE jobs SET {', '.join(fields)} WHERE id = ?", values)
        conn.commit()
    finally:
        conn.close()
