"use client";

import dynamic from "next/dynamic";
import { useMemo } from "react";
import { resolveArtifactUrl, type JobResultsResponse } from "@/lib/api";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

export default function CellsPanel({ results }: { results: JobResultsResponse }) {
  const cellTypes = results.cell_types ?? [];
  const deTables = results.de_tables ?? [];
  const points = results.umap_data?.points ?? [];

  const plotData = useMemo(() => {
    if (!points.length) return null;
    const types = [...new Set(points.map((p: { cell_type: string }) => p.cell_type))];
    return types.map((ct) => ({
      x: points.filter((p: { cell_type: string }) => p.cell_type === ct).map((p: { x: number }) => p.x),
      y: points.filter((p: { cell_type: string }) => p.cell_type === ct).map((p: { y: number }) => p.y),
      mode: "markers" as const,
      type: "scattergl" as const,
      name: ct,
      marker: { size: 4, opacity: 0.7 },
    }));
  }, [points]);

  return (
    <div>
      <div className="group-header">
        <span>Cell types</span>
        <span className="group-count">{cellTypes.length} types</span>
      </div>

      <div className="grid-2">
        <div className="panel">
          {plotData ? (
            <div className="plot-wrap">
              <Plot
                data={plotData}
                layout={{
                  title: { text: "UMAP — cell types", font: { family: "Inter", size: 14 } },
                  paper_bgcolor: "transparent",
                  plot_bgcolor: "transparent",
                  font: { family: "JetBrains Mono", size: 11 },
                  margin: { l: 40, r: 20, t: 40, b: 40 },
                  xaxis: { zeroline: false, gridcolor: "#ddd" },
                  yaxis: { zeroline: false, gridcolor: "#ddd" },
                  showlegend: true,
                  legend: { font: { size: 10 } },
                  height: 360,
                }}
                config={{ displayModeBar: false, responsive: true }}
                style={{ width: "100%" }}
              />
            </div>
          ) : (
            <div className="plot-wrap">
              {results.umap_plot ? (
                <img src={resolveArtifactUrl(results.umap_plot)} alt="UMAP clusters" />
              ) : (
                <div className="empty-state">UMAP not available</div>
              )}
            </div>
          )}
        </div>

        <div className="panel">
          <h3>Cell type counts</h3>
          <table className="data-table">
            <thead>
              <tr>
                <th>Cell type</th>
                <th>Count</th>
                <th>Fraction</th>
              </tr>
            </thead>
            <tbody>
              {cellTypes.map((ct) => (
                <tr key={ct.cell_type}>
                  <td>{ct.cell_type}</td>
                  <td>{ct.count}</td>
                  <td>{(ct.fraction * 100).toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="panel" style={{ marginTop: 16 }}>
        <h3>Differential expression / markers</h3>
        {results.de_summary && (
          <p style={{ color: "var(--cdisabled)", fontSize: 11, marginBottom: 12 }}>
            Method: {String(results.de_summary.method)} ·{" "}
            {Array.isArray(results.de_summary.comparisons)
              ? results.de_summary.comparisons.join(", ")
              : "per cell type"}
          </p>
        )}
        <table className="data-table">
          <thead>
            <tr>
              <th>Cell type</th>
              <th>Gene</th>
              <th>Score</th>
              <th>Adj. p-value</th>
              <th>Comparison</th>
            </tr>
          </thead>
          <tbody>
            {deTables.slice(0, 40).map((row, i) => (
              <tr key={`${row.names}-${i}`}>
                <td>{String(row.cell_type ?? "—")}</td>
                <td>{String(row.names ?? row.gene ?? "—")}</td>
                <td>{row.scores != null ? Number(row.scores).toFixed(2) : "—"}</td>
                <td>{row.pvals_adj != null ? Number(row.pvals_adj).toExponential(2) : "—"}</td>
                <td>{String(row.comparison ?? "—")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
