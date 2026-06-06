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
    qc_report: dict[str, Any] | None = None
    cluster_summary: dict[str, Any] | None = None
    cell_types: list[dict[str, Any]] | None = None
    communication_edges: list[dict[str, Any]] | None = None
    umap_plot: str | None = None
    network_plot: str | None = None
    heatmap_plot: str | None = None
    exports: dict[str, str] | None = None
