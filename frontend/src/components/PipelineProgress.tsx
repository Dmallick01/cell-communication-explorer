"use client";

import type { JobStatusResponse } from "@/lib/api";

const STEP_LABELS: Record<string, string> = {
  upload: "Data validation",
  qc: "Quality control",
  batch_correction: "Batch correction (Harmony)",
  clustering: "Clustering & UMAP",
  annotation: "Cell-type annotation",
  de: "Differential expression",
  communication: "Cell-cell communication (NicheNet)",
  export: "Report export",
};

export default function PipelineProgress({ job }: { job: JobStatusResponse }) {
  const completed = job.steps.filter((s) => s.status === "completed").length;
  const progress = job.steps.length ? (completed / job.steps.length) * 100 : 0;

  return (
    <div className="progress-panel">
      <div className="group-header">
        <span>Pipeline progress</span>
        <span className="group-count">{job.status}</span>
      </div>

      <div className="progress-track">
        <div className="progress-fill" style={{ width: `${progress}%` }} />
      </div>

      <ul className="step-list">
        {job.steps.map((step) => (
          <li key={step.step} className="step-item">
            <span
              className={`step-status ${
                step.status === "completed"
                  ? "done"
                  : step.status === "running"
                    ? "running"
                    : step.status === "failed"
                      ? "failed"
                      : ""
              }`}
            >
              {step.status}
            </span>
            <div>
              <div>{STEP_LABELS[step.step] ?? step.step}</div>
              {step.message && (
                <div style={{ color: "var(--cdisabled)", fontSize: 11, marginTop: 4 }}>
                  {step.message}
                </div>
              )}
              {step.checkpoint_passed === false && step.status === "completed" && (
                <span className="badge badge-warn" style={{ marginTop: 4 }}>
                  quality warning
                </span>
              )}
            </div>
          </li>
        ))}
      </ul>

      {job.error && <div className="alert alert-error" style={{ marginTop: 16 }}>{job.error}</div>}
    </div>
  );
}
