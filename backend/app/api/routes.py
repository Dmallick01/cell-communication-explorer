from pathlib import Path
from uuid import uuid4

import aiofiles
from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile

from app.core.config import settings
from app.core.job_store import job_store
from app.models.schemas import (
    JobCreateResponse,
    JobResultsResponse,
    JobStatus,
    JobStatusResponse,
    PipelineStep,
)
from app.services.pipeline_runner import run_job_pipeline

router = APIRouter()

ALLOWED_SUFFIXES = {".h5ad", ".mtx", ".csv", ".tsv", ".txt", ".gz"}


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


@router.post("/jobs", response_model=JobCreateResponse)
async def create_job(
    background_tasks: BackgroundTasks,
    data_file: UploadFile = File(...),
    metadata_file: UploadFile | None = File(None),
    demo: bool = Form(False),
) -> JobCreateResponse:
    if not data_file.filename:
        raise HTTPException(status_code=400, detail="Data file is required")

    filename = data_file.filename
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES and not filename.endswith(".mtx.gz"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format. Allowed: {', '.join(sorted(ALLOWED_SUFFIXES))}",
        )

    content = await data_file.read()
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="File exceeds 2 GB limit")

    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    job_id = str(uuid4())

    input_path = settings.uploads_dir / f"{job_id}_{filename}"
    async with aiofiles.open(input_path, "wb") as out:
        await out.write(content)

    metadata_path_str: str | None = None
    if metadata_file and metadata_file.filename:
        meta_path = settings.uploads_dir / f"{job_id}_{metadata_file.filename}"
        meta_content = await metadata_file.read()
        async with aiofiles.open(meta_path, "wb") as out:
            await out.write(meta_content)
        metadata_path_str = str(meta_path)

    await job_store.create_job(str(input_path), metadata_path_str, job_id=job_id)
    background_tasks.add_task(run_job_pipeline, job_id, demo)
    return JobCreateResponse(job_id=job_id, status=JobStatus.QUEUED)


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str) -> JobStatusResponse:
    job = await job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        job_id=job.id,
        status=JobStatus(job.status),
        current_step=PipelineStep(job.current_step) if job.current_step else None,
        steps=job_store.parse_steps(job),
        error=job.error,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


@router.get("/jobs/{job_id}/results", response_model=JobResultsResponse)
async def get_job_results(job_id: str) -> JobResultsResponse:
    job = await job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    results = job.results_json or {}
    return JobResultsResponse(
        job_id=job.id,
        status=JobStatus(job.status),
        qc_report=results.get("qc_report"),
        cluster_summary=results.get("cluster_summary"),
        cell_types=results.get("cell_types"),
        communication_edges=results.get("communication_edges"),
        umap_plot=results.get("umap_plot"),
        network_plot=results.get("network_plot"),
        heatmap_plot=results.get("heatmap_plot"),
        exports=results.get("exports"),
    )
