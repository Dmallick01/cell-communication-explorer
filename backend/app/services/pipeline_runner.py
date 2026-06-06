import asyncio
import json
import logging
import os
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

from app.core.config import settings
from app.core.job_store import job_store
from app.core.job_store_sync import update_job_sync, update_step_sync
from app.models.schemas import JobStatus, PipelineStep

PIPELINE_ROOT = Path(__file__).resolve().parents[3] / "pipeline"
if str(PIPELINE_ROOT.parent) not in sys.path:
    sys.path.insert(0, str(PIPELINE_ROOT.parent))

from pipeline.runner import run_pipeline  # noqa: E402

logger = logging.getLogger(__name__)


def _on_step(step: str, status: str, message: str | None = None, checkpoint: bool | None = None):
    update_step_sync(step=step, status=status, job_id="", message=message, checkpoint=checkpoint)


async def run_job_pipeline(job_id: str, demo: bool = False) -> None:
    job = await job_store.get_job(job_id)
    if not job or not job.input_path:
        return

    await job_store.update_job(job_id, status=JobStatus.RUNNING)
    output_dir = job_store.job_results_dir(job_id)

    def on_step(step: str, status: str, message: str | None = None, checkpoint: bool | None = None):
        update_step_sync(job_id, step, status, message, checkpoint)

    try:
        results = await asyncio.to_thread(
            run_pipeline,
            job_id=job_id,
            input_path=job.input_path,
            metadata_path=job.metadata_path,
            output_dir=str(output_dir),
            demo_mode=demo or settings.pipeline_demo_mode,
            on_step=on_step,
        )
        update_job_sync(
            job_id,
            status=JobStatus.COMPLETED.value,
            results_json=json.dumps(results, default=str),
        )
        await job_store.update_job(
            job_id,
            status=JobStatus.COMPLETED,
            current_step=PipelineStep.EXPORT,
            results=results,
        )
    except Exception as exc:
        logger.exception("Pipeline failed for job %s", job_id)
        update_job_sync(job_id, status=JobStatus.FAILED.value, error=str(exc))
        await job_store.update_job(job_id, status=JobStatus.FAILED, error=str(exc))
