const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

export type JobStatus = "queued" | "running" | "completed" | "failed";

export interface StepStatus {
  step: string;
  status: JobStatus;
  message?: string;
  checkpoint_passed?: boolean;
}

export interface JobStatusResponse {
  job_id: string;
  status: JobStatus;
  current_step?: string;
  steps: StepStatus[];
  error?: string;
  created_at: string;
  updated_at: string;
}

export interface CommunicationEdge {
  source_cell_type: string;
  target_cell_type: string;
  ligand: string;
  receptor: string;
  score: number;
  p_value: number;
}

export interface JobResultsResponse {
  job_id: string;
  status: JobStatus;
  qc_report?: Record<string, unknown>;
  cluster_summary?: Record<string, unknown>;
  cell_types?: Array<{ cell_type: string; count: number; fraction: number }>;
  communication_edges?: CommunicationEdge[];
  umap_plot?: string;
  network_plot?: string;
  heatmap_plot?: string;
  exports?: Record<string, string>;
}

export async function createJob(
  dataFile: File,
  metadataFile?: File | null,
  demo = false,
): Promise<{ job_id: string; status: JobStatus }> {
  const form = new FormData();
  form.append("data_file", dataFile);
  if (metadataFile) {
    form.append("metadata_file", metadataFile);
  }
  if (demo) {
    form.append("demo", "true");
  }

  const res = await fetch(`${API_BASE}/jobs`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "Upload failed");
  }

  return res.json();
}

export async function getJobStatus(jobId: string): Promise<JobStatusResponse> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}`);
  if (!res.ok) throw new Error("Job not found");
  return res.json();
}

export async function getJobResults(jobId: string): Promise<JobResultsResponse> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}/results`);
  if (!res.ok) throw new Error("Results not available");
  return res.json();
}
