"use client";

import { useState } from "react";
import { resolveArtifactUrl, type CommunicationEdge, type JobResultsResponse } from "@/lib/api";

export default function CommunicationPanel({ results }: { results: JobResultsResponse }) {
  const edges = results.communication_edges ?? [];
  const [selected, setSelected] = useState<CommunicationEdge | null>(edges[0] ?? null);
  const [filter, setFilter] = useState("");

  const filtered = edges.filter((e) => {
    const q = filter.toLowerCase();
    if (!q) return true;
    return (
      e.ligand.toLowerCase().includes(q) ||
      e.receptor.toLowerCase().includes(q) ||
      e.source_cell_type.toLowerCase().includes(q) ||
      e.target_cell_type.toLowerCase().includes(q)
    );
  });

  return (
    <div>
      <div className="group-header">
        <span>Cell–cell communication</span>
        <span className="group-count">{edges.length} edges · NicheNet</span>
      </div>

      <div className="control-group">
        <label htmlFor="edge-filter">Filter edges</label>
        <input
          id="edge-filter"
          className="control-input"
          placeholder="ligand, receptor, cell type…"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        />
      </div>

      <div className="grid-2">
        <div className="plot-wrap">
          {results.network_plot ? (
            <img src={resolveArtifactUrl(results.network_plot)} alt="Communication network" />
          ) : (
            <div className="empty-state">Network plot pending</div>
          )}
        </div>
        <div className="plot-wrap">
          {results.heatmap_plot ? (
            <img src={resolveArtifactUrl(results.heatmap_plot)} alt="LR heatmap" />
          ) : (
            <div className="empty-state">Heatmap pending</div>
          )}
        </div>
      </div>

      <div className="panel" style={{ marginTop: 16 }}>
        <h3>Ligand–receptor interactions</h3>
        <table className="data-table">
          <thead>
            <tr>
              <th>Source</th>
              <th>Target</th>
              <th>Ligand</th>
              <th>Receptor</th>
              <th>Score</th>
              <th>p-value</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((e, i) => (
              <tr
                key={`${e.ligand}-${e.receptor}-${i}`}
                className={`clickable ${selected === e ? "selected" : ""}`}
                onClick={() => setSelected(e)}
              >
                <td>{e.source_cell_type}</td>
                <td>{e.target_cell_type}</td>
                <td>{e.ligand}</td>
                <td>{e.receptor}</td>
                <td>{e.score}</td>
                <td>{e.p_value}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selected && (
        <div className="panel panel-accent" style={{ marginTop: 16 }}>
          <h3>Selected edge</h3>
          <p>
            <strong>{selected.source_cell_type}</strong> →{" "}
            <strong>{selected.target_cell_type}</strong> via{" "}
            <strong>{selected.ligand}</strong> → <strong>{selected.receptor}</strong>
          </p>
          <p style={{ fontSize: 11, color: "var(--cdisabled)", marginTop: 8 }}>
            NicheNet score {selected.score} · p={selected.p_value}. See Literature tab for PubMed
            evidence.
          </p>
        </div>
      )}
    </div>
  );
}
