"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { listJobs, type JobListItem } from "@/lib/api";

export default function ProjectQueue({ activeId }: { activeId?: string }) {
  const [jobs, setJobs] = useState<JobListItem[]>([]);

  useEffect(() => {
    listJobs().then(setJobs).catch(() => setJobs([]));
    const t = setInterval(() => listJobs().then(setJobs).catch(() => {}), 5000);
    return () => clearInterval(t);
  }, []);

  return (
    <div>
      <h3 className="queue-title">Recent analyses</h3>
      {jobs.length === 0 ? (
        <p style={{ color: "var(--cdisabled)", fontSize: 11 }}>No projects yet.</p>
      ) : (
        <ul className="nav-list">
          {jobs.slice(0, 12).map((j) => (
            <li key={j.job_id}>
              <Link
                href={`/projects/${j.job_id}`}
                className={`btn ${j.job_id === activeId ? "active" : ""}`}
                style={{ fontSize: 10 }}
              >
                {(j.project_name || j.job_id.slice(0, 8)) + "…"}
                <span style={{ display: "block", color: "var(--cdisabled)", marginTop: 2 }}>
                  {j.status}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
