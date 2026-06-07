from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class PipelineStep(str, Enum):
    UPLOAD = "upload"
    QC = "qc"
    BATCH_CORRECTION = "batch_correction"
    CLUSTERING = "clustering"
    ANNOTATION = "annotation"
    DE = "de"
    COMMUNICATION = "communication"
    EXPORT = "export"


class JobCreateResponse(BaseModel):
    job_id: str
    status: JobStatus


class StepStatus(BaseModel):
    step: PipelineStep
    status: JobStatus
    message: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    checkpoint_passed: bool | None = None


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    current_step: PipelineStep | None = None
    steps: list[StepStatus] = Field(default_factory=list)
    error: str | None = None
    created_at: datetime
    updated_at: datetime


class JobResultsResponse(BaseModel):
    job_id: str
    status: JobStatus
    project_name: str | None = None
    tissue: str | None = None
    disease: str | None = None
    qc_report: dict[str, Any] | None = None
    cluster_summary: dict[str, Any] | None = None
    cell_types: list[dict[str, Any]] | None = None
    de_summary: dict[str, Any] | None = None
    de_tables: list[dict[str, Any]] | None = None
    umap_data: dict[str, Any] | None = None
    communication_edges: list[dict[str, Any]] | None = None
    umap_plot: str | None = None
    network_plot: str | None = None
    heatmap_plot: str | None = None
    exports: dict[str, str] | None = None


class LiteratureEdge(BaseModel):
    source_cell_type: str
    target_cell_type: str
    ligand: str
    receptor: str
    score: float
    p_value: float
    papers: list[dict[str, Any]] = Field(default_factory=list)


class LiteratureResponse(BaseModel):
    job_id: str
    edges: list[LiteratureEdge]


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
