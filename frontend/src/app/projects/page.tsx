"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { listJobs, type JobListItem } from "@/lib/api";

export default function ProjectsPage() {
  const [jobs, setJobs] = useState<JobListItem[]>([]);

  useEffect(() => {
    listJobs().then(setJobs).catch(() => setJobs([]));
  }, []);

  return (
    <div>
      <div className="app-header" style={{ borderBottom: "none", paddingTop: 0 }}>
        <div>
          <h1>Analysis projects</h1>
          <p className="header-meta">
            Upload scRNA-seq data to discover cell-to-cell signaling grounded in NicheNet priors
            and citable methods.
          </p>
        </div>
        <div className="header-actions">
          <Link href="/projects/new" className="btn btn-primary">
            New analysis
          </Link>
        </div>
      </div>

      {jobs.length === 0 ? (
        <div className="empty-state">
          No analyses yet.{" "}
          <Link href="/projects/new">Start a new upload</Link> or run a dev benchmark.
        </div>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>Project</th>
              <th>Tissue</th>
              <th>Condition</th>
              <th>Status</th>
              <th>Created</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {jobs.map((j) => (
              <tr key={j.job_id} className="clickable">
                <td>{j.project_name || `${j.job_id.slice(0, 8)}…`}</td>
                <td>{j.tissue || "—"}</td>
                <td>{j.disease || "—"}</td>
                <td>
                  <span className="badge">{j.status}</span>
                </td>
                <td>{j.created_at ? new Date(j.created_at).toLocaleString() : "—"}</td>
                <td>
                  <Link href={`/projects/${j.job_id}`} className="btn">
                    Open
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
