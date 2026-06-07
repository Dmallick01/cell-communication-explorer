from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from pipeline.utils.io import save_json


def run_export(
    job_id: str,
    output_dir: Path,
    qc_report: dict[str, Any],
    cluster_summary: dict[str, Any],
    cell_types: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    plot_paths: dict[str, str],
    methods_path: str | None = None,
) -> dict[str, str]:
    exports: dict[str, str] = {}

    qc_path = output_dir / "qc_report.json"
    save_json(qc_path, qc_report)
    exports["qc_report"] = str(qc_path)

    cluster_path = output_dir / "cluster_summary.json"
    save_json(cluster_path, cluster_summary)
    exports["cluster_summary"] = str(cluster_path)

    ct_path = output_dir / "cell_types.csv"
    pd.DataFrame(cell_types).to_csv(ct_path, index=False)
    exports["cell_types"] = str(ct_path)

    edges_path = output_dir / "communication_edges.csv"
    pd.DataFrame(edges).to_csv(edges_path, index=False)
    exports["communication_edges"] = str(edges_path)

    summary_path = output_dir / "session_summary.json"
    save_json(
        summary_path,
        {
            "job_id": job_id,
            "n_cell_types": len(cell_types),
            "n_interactions": len(edges),
            "n_clusters": cluster_summary.get("n_clusters"),
            "plots": plot_paths,
        },
    )
    exports["session_summary"] = str(summary_path)

    html_path = output_dir / "report.html"
    _write_html_report(
        html_path,
        job_id=job_id,
        qc_report=qc_report,
        cluster_summary=cluster_summary,
        cell_types=cell_types,
        edges=edges[:20],
    )
    exports["report_html"] = str(html_path)

    if methods_path and Path(methods_path).is_file():
        exports["methods"] = methods_path

    pdf_path = _write_pdf_report(html_path, output_dir / "report.pdf")
    if pdf_path:
        exports["report_pdf"] = str(pdf_path)

    return exports


def _write_pdf_report(html_path: Path, pdf_path: Path) -> Path | None:
    try:
        from weasyprint import HTML

        HTML(filename=str(html_path)).write_pdf(str(pdf_path))
        return pdf_path
    except Exception:
        return None


def _write_html_report(
    path: Path,
    *,
    job_id: str,
    qc_report: dict[str, Any],
    cluster_summary: dict[str, Any],
    cell_types: list[dict[str, Any]],
    edges: list[dict[str, Any]],
) -> None:
    ct_rows = "".join(
        f"<tr><td>{c['cell_type']}</td><td>{c['count']}</td><td>{c['fraction']}</td></tr>"
        for c in cell_types
    )
    edge_rows = "".join(
        f"<tr><td>{e['source_cell_type']}</td><td>{e['target_cell_type']}</td>"
        f"<td>{e['ligand']}</td><td>{e['receptor']}</td><td>{e['score']}</td></tr>"
        for e in edges
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Cell Communication Report — {job_id}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #1a1a2e; }}
    h1, h2 {{ color: #16213e; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
    th, td {{ border: 1px solid #ddd; padding: 0.5rem; text-align: left; }}
    th {{ background: #0f3460; color: white; }}
    .plots img {{ max-width: 100%; margin: 1rem 0; border: 1px solid #eee; }}
    .metric {{ display: inline-block; margin-right: 2rem; }}
  </style>
</head>
<body>
  <h1>Cell Communication Explorer — Analysis Report</h1>
  <p><strong>Job ID:</strong> {job_id}</p>

  <h2>Quality Control</h2>
  <p class="metric"><strong>Cells remaining:</strong> {qc_report.get('cells_remaining', 'N/A')}</p>
  <p class="metric"><strong>Median mito %:</strong> {qc_report.get('pct_mito_median', 'N/A')}</p>
  <p class="metric"><strong>Doublet rate:</strong> {qc_report.get('doublet_rate', 'N/A')}</p>

  <h2>Clustering</h2>
  <p class="metric"><strong>Clusters:</strong> {cluster_summary.get('n_clusters', 'N/A')}</p>
  <p class="metric"><strong>Silhouette:</strong> {cluster_summary.get('silhouette_score', 'N/A')}</p>

  <h2>Cell Types</h2>
  <table>
    <tr><th>Cell Type</th><th>Count</th><th>Fraction</th></tr>
    {ct_rows}
  </table>

  <h2>Top Ligand-Receptor Interactions</h2>
  <table>
    <tr><th>Source</th><th>Target</th><th>Ligand</th><th>Receptor</th><th>Score</th></tr>
    {edge_rows}
  </table>

  <h2>Figures</h2>
  <div class="plots">
    <img src="umap_clusters.png" alt="UMAP clusters" />
    <img src="communication_network.png" alt="Communication network" />
    <img src="communication_heatmap.png" alt="Communication heatmap" />
  </div>
</body>
</html>"""
    path.write_text(html)
