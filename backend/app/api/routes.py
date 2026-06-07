import asyncio
import shutil
import zipfile
from pathlib import Path
from uuid import uuid4

import aiofiles
from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.job_store import job_store
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    JobCreateResponse,
    JobResultsResponse,
    JobStatus,
    JobStatusResponse,
    LiteratureResponse,
    PipelineStep,
)
from app.services.chat import answer_question
from app.services.literature import literature_for_edges
from app.services.pipeline_runner import run_job_pipeline

router = APIRouter()

ALLOWED_SUFFIXES = {".h5ad", ".mtx", ".csv", ".tsv", ".txt", ".gz", ".zip"}

ARTIFACT_FILES = {
    "umap_clusters.png",
    "communication_network.png",
    "communication_heatmap.png",
    "report.html",
    "report.pdf",
    "communication_edges.csv",
    "cell_types.csv",
    "qc_report.json",
    "session_summary.json",
    "provenance.json",
    "methods.txt",
    "de_genes.csv",
    "umap_coords.json",
    "de_summary.json",
}


def _artifact_url(job_id: str, filename: str) -> str:
    return f"{settings.api_prefix}/jobs/{job_id}/artifacts/{filename}"


def _public_results(job_id: str, results: dict) -> dict:
    """Map filesystem paths to API artifact URLs."""
    out = dict(results)
    plot_map = {
        "umap_plot": "umap_clusters.png",
        "network_plot": "communication_network.png",
        "heatmap_plot": "communication_heatmap.png",
    }
    for key, filename in plot_map.items():
        if out.get(key):
            out[key] = _artifact_url(job_id, filename)

    exports = out.get("exports") or {}
    export_keys = {
        "report_html": "report.html",
        "report_pdf": "report.pdf",
        "communication_edges": "communication_edges.csv",
        "cell_types": "cell_types.csv",
        "qc_report": "qc_report.json",
        "session_summary": "session_summary.json",
        "provenance": "provenance.json",
        "methods": "methods.txt",
        "de_genes": "de_genes.csv",
        "umap_coords": "umap_coords.json",
    }
    out["exports"] = {
        key: _artifact_url(job_id, filename)
        for key, filename in export_keys.items()
        if key in exports
    }
    return out


def _extract_zip(zip_path: Path, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(dest_dir)

    for name in ("matrix.mtx", "matrix.mtx.gz"):
        matches = list(dest_dir.rglob(name))
        if matches:
            return matches[0].parent

    raise ValueError(
        "ZIP must contain a 10x Genomics matrix (matrix.mtx + barcodes.tsv + features.tsv)"
    )


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


@router.get("/jobs")
async def list_jobs(limit: int = 50) -> list[dict]:
    jobs = await job_store.list_jobs(limit=limit)
    return [
        {
            "job_id": j.id,
            "status": j.status,
            "created_at": j.created_at.isoformat() if j.created_at else None,
            "updated_at": j.updated_at.isoformat() if j.updated_at else None,
            "error": j.error,
            "project_name": (j.results_json or {}).get("project_name"),
            "tissue": (j.results_json or {}).get("tissue"),
            "disease": (j.results_json or {}).get("disease"),
        }
        for j in jobs
    ]


@router.post("/jobs", response_model=JobCreateResponse)
async def create_job(
    background_tasks: BackgroundTasks,
    data_file: UploadFile = File(...),
    metadata_file: UploadFile | None = File(None),
    demo: bool = Form(False),
    project_name: str = Form(""),
    tissue: str = Form(""),
    disease: str = Form(""),
) -> JobCreateResponse:
    if demo and not settings.development_only:
        raise HTTPException(
            status_code=403,
            detail="Demo mode is disabled in production. Upload real scRNA-seq data.",
        )

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

    saved_path = settings.uploads_dir / f"{job_id}_{filename}"
    async with aiofiles.open(saved_path, "wb") as out:
        await out.write(content)

    input_path = saved_path
    if suffix == ".zip":
        try:
            extract_dir = settings.uploads_dir / f"{job_id}_10x"
            input_path = _extract_zip(saved_path, extract_dir)
        except ValueError as exc:
            shutil.rmtree(settings.uploads_dir / f"{job_id}_10x", ignore_errors=True)
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    metadata_path_str: str | None = None
    if metadata_file and metadata_file.filename:
        meta_path = settings.uploads_dir / f"{job_id}_{metadata_file.filename}"
        meta_content = await metadata_file.read()
        async with aiofiles.open(meta_path, "wb") as out:
            await out.write(meta_content)
        metadata_path_str = str(meta_path)

    await job_store.create_job(str(input_path), metadata_path_str, job_id=job_id)
    meta = {
        k: v
        for k, v in {
            "project_name": project_name.strip() or None,
            "tissue": tissue.strip() or None,
            "disease": disease.strip() or None,
        }.items()
        if v
    }
    if meta:
        await job_store.update_job(job_id, results=meta)
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

    results = _public_results(job_id, job.results_json or {})
    return JobResultsResponse(
        job_id=job.id,
        status=JobStatus(job.status),
        project_name=results.get("project_name"),
        tissue=results.get("tissue"),
        disease=results.get("disease"),
        qc_report=results.get("qc_report"),
        cluster_summary=results.get("cluster_summary"),
        cell_types=results.get("cell_types"),
        de_summary=results.get("de_summary"),
        de_tables=results.get("de_tables"),
        umap_data=results.get("umap_data"),
        communication_edges=results.get("communication_edges"),
        umap_plot=results.get("umap_plot"),
        network_plot=results.get("network_plot"),
        heatmap_plot=results.get("heatmap_plot"),
        exports=results.get("exports"),
    )


@router.get("/jobs/{job_id}/literature", response_model=LiteratureResponse)
async def get_job_literature(job_id: str) -> LiteratureResponse:
    job = await job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != JobStatus.COMPLETED.value:
        raise HTTPException(status_code=400, detail="Analysis not complete")

    edges = (job.results_json or {}).get("communication_edges") or []
    enriched = await asyncio.to_thread(literature_for_edges, edges)
    return LiteratureResponse(job_id=job_id, edges=enriched)


@router.post("/jobs/{job_id}/chat", response_model=ChatResponse)
async def chat_with_job(job_id: str, body: ChatRequest) -> ChatResponse:
    job = await job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    reply = answer_question(body.message, job.results_json or {})
    return ChatResponse(reply=reply)


@router.get("/jobs/{job_id}/artifacts/{filename}")
async def get_job_artifact(job_id: str, filename: str) -> FileResponse:
    if filename not in ARTIFACT_FILES:
        raise HTTPException(status_code=404, detail="Artifact not found")

    job = await job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    path = settings.results_dir / job_id / filename
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Artifact not ready")

    media = "application/octet-stream"
    if filename.endswith(".png"):
        media = "image/png"
    elif filename.endswith(".html"):
        media = "text/html"
    elif filename.endswith(".pdf"):
        media = "application/pdf"
    elif filename.endswith(".csv"):
        media = "text/csv"
    elif filename.endswith(".json"):
        media = "application/json"
    elif filename.endswith(".txt"):
        media = "text/plain"

    return FileResponse(path, media_type=media, filename=filename)
