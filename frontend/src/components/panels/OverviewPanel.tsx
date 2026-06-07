"use client";

import PipelineProgress from "@/components/PipelineProgress";
import type { JobResultsResponse, JobStatusResponse } from "@/lib/api";

export default function OverviewPanel({
  job,
  results,
}: {
  job: JobStatusResponse;
  results: JobResultsResponse | null;
}) {
  const qc = results?.qc_report;
  const cluster = results?.cluster_summary;

  return (
    <div>
      <div className="group-header">
        <span>Overview</span>
        {results?.project_name && (
          <span className="group-count">{results.project_name}</span>
        )}
      </div>

      <PipelineProgress job={job} />

      {results && (
        <div className="grid-2" style={{ marginTop: 16 }}>
          <div className="panel panel-accent">
            <h3>QC summary</h3>
            <p>Cells remaining: <strong>{String(qc?.cells_remaining ?? "—")}</strong></p>
            <p>Median mito %: <strong>{String(qc?.pct_mito_median ?? "—")}</strong></p>
          </div>
          <div className="panel panel-accent">
            <h3>Clustering</h3>
            <p>Clusters: <strong>{String(cluster?.n_clusters ?? "—")}</strong></p>
            <p>Silhouette: <strong>{String(cluster?.silhouette_score ?? "—")}</strong></p>
          </div>
          <div className="panel">
            <h3>Cell types</h3>
            <p><strong>{results.cell_types?.length ?? 0}</strong> annotated types</p>
          </div>
          <div className="panel">
            <h3>Communication</h3>
            <p><strong>{results.communication_edges?.length ?? 0}</strong> NicheNet edges</p>
            <p style={{ color: "var(--cdisabled)", fontSize: 11, marginTop: 4 }}>
              Method: {results.de_summary?.method ? "NicheNet + Wilcoxon DE" : "NicheNet"}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
