from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from sqlalchemy import JSON, DateTime, String, Text, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.core.config import settings
from app.models.schemas import JobStatus, PipelineStep, StepStatus


class Base(DeclarativeBase):
    pass


class JobRecord(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    status: Mapped[str] = mapped_column(String(20), default=JobStatus.QUEUED.value)
    current_step: Mapped[str | None] = mapped_column(String(40), nullable=True)
    steps_json: Mapped[dict] = mapped_column(JSON, default=dict)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    input_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    results_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _default_steps() -> list[dict[str, Any]]:
    return [
        {"step": step.value, "status": JobStatus.QUEUED.value}
        for step in PipelineStep
    ]


engine = create_async_engine(settings.database_url, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def init_db() -> None:
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    settings.results_dir.mkdir(parents=True, exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


class JobStore:
    async def create_job(
        self,
        input_path: str,
        metadata_path: str | None = None,
        job_id: str | None = None,
    ) -> str:
        job_id = job_id or str(uuid4())
        now = _now()
        async with SessionLocal() as session:
            job = JobRecord(
                id=job_id,
                status=JobStatus.QUEUED.value,
                steps_json={"steps": _default_steps()},
                input_path=input_path,
                metadata_path=metadata_path,
                created_at=now,
                updated_at=now,
            )
            session.add(job)
            await session.commit()
        return job_id

    async def get_job(self, job_id: str) -> JobRecord | None:
        async with SessionLocal() as session:
            return await session.get(JobRecord, job_id)

    async def list_jobs(self, limit: int = 50) -> list[JobRecord]:
        async with SessionLocal() as session:
            result = await session.execute(
                select(JobRecord).order_by(JobRecord.created_at.desc()).limit(limit)
            )
            return list(result.scalars().all())

    async def update_job(
        self,
        job_id: str,
        *,
        status: JobStatus | None = None,
        current_step: PipelineStep | None = None,
        error: str | None = None,
        results: dict[str, Any] | None = None,
        step_update: tuple[PipelineStep, JobStatus, str | None, bool | None] | None = None,
    ) -> None:
        async with SessionLocal() as session:
            job = await session.get(JobRecord, job_id)
            if not job:
                return

            if status is not None:
                job.status = status.value
            if current_step is not None:
                job.current_step = current_step.value
            if error is not None:
                job.error = error
            if results is not None:
                job.results_json = {**job.results_json, **results}

            if step_update is not None:
                step_name, step_status, message, checkpoint = step_update
                steps = job.steps_json.get("steps", _default_steps())
                now = _now().isoformat()
                for step in steps:
                    if step["step"] == step_name.value:
                        step["status"] = step_status.value
                        if message is not None:
                            step["message"] = message
                        if checkpoint is not None:
                            step["checkpoint_passed"] = checkpoint
                        if step_status == JobStatus.RUNNING and "started_at" not in step:
                            step["started_at"] = now
                        if step_status in (JobStatus.COMPLETED, JobStatus.FAILED):
                            step["completed_at"] = now
                job.steps_json = {"steps": steps}

            job.updated_at = _now()
            await session.commit()

    def job_results_dir(self, job_id: str) -> Path:
        path = settings.results_dir / job_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def parse_steps(self, job: JobRecord) -> list[StepStatus]:
        steps = []
        for raw in job.steps_json.get("steps", []):
            steps.append(
                StepStatus(
                    step=PipelineStep(raw["step"]),
                    status=JobStatus(raw["status"]),
                    message=raw.get("message"),
                    started_at=raw.get("started_at"),
                    completed_at=raw.get("completed_at"),
                    checkpoint_passed=raw.get("checkpoint_passed"),
                )
            )
        return steps


job_store = JobStore()
