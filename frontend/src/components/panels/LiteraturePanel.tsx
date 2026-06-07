"use client";

import { useEffect, useState } from "react";
import { getJobLiterature, type LiteratureEdge } from "@/lib/api";

export default function LiteraturePanel({ jobId }: { jobId: string }) {
  const [edges, setEdges] = useState<LiteratureEdge[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getJobLiterature(jobId)
      .then((r) => setEdges(r.edges))
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load literature"))
      .finally(() => setLoading(false));
  }, [jobId]);

  if (loading) return <div className="empty-state">Fetching PubMed evidence…</div>;
  if (error) return <div className="alert alert-error">{error}</div>;
  if (!edges.length) return <div className="empty-state">No communication edges to cite.</div>;

  return (
    <div>
      <div className="group-header">
        <span>Literature evidence</span>
        <span className="group-count">PubMed · NCBI E-utilities</span>
      </div>

      <p style={{ color: "var(--cdisabled)", fontSize: 12, marginBottom: 16 }}>
        Papers linked to top ligand–receptor edges. No AI summarization — direct PubMed retrieval
        only.
      </p>

      {edges.map((edge, idx) => (
        <div key={`${edge.ligand}-${idx}`} className="panel" style={{ marginBottom: 16 }}>
          <h3>
            {edge.source_cell_type} → {edge.target_cell_type}: {edge.ligand} → {edge.receptor}
          </h3>
          {edge.papers.length === 0 ? (
            <p style={{ color: "var(--cdisabled)", fontSize: 11 }}>No PubMed hits for this edge.</p>
          ) : (
            <ul style={{ listStyle: "none" }}>
              {edge.papers.map((p) => (
                <li key={p.pmid} style={{ marginBottom: 12, fontSize: 12 }}>
                  <a href={p.url} target="_blank" rel="noreferrer">
                    {p.title}
                  </a>
                  <div style={{ color: "var(--cdisabled)", fontSize: 11, marginTop: 4 }}>
                    {p.journal} {p.year} · PMID {p.pmid}
                    {p.authors?.length ? ` · ${p.authors.join(", ")}` : ""}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      ))}
    </div>
  );
}
