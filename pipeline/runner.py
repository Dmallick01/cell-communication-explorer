from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import anndata as ad

from pipeline.steps import (
    load_dataset,
    run_annotation,
    run_batch_correction,
    run_clustering,
    run_communication,
    run_export,
    run_qc,
)
from pipeline.utils.io import save_json

StepCallback = Callable[[str, str, str | None, bool | None], None]


def run_pipeline(
    job_id: str,
    input_path: str,
    metadata_path: str | None,
    output_dir: str,
    demo_mode: bool = False,
    on_step: StepCallback | None = None,
) -> dict[str, Any]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    def notify(step: str, status: str, message: str | None = None, checkpoint: bool | None = None):
        if on_step:
            on_step(step, status, message, checkpoint)

    # Step 1: Upload / load
    notify("upload", "running")
    adata, load_metrics = load_dataset(input_path, metadata_path, demo_mode=demo_mode)
    h5ad_path = out / "processed.h5ad"
    adata.write_h5ad(h5ad_path)
    save_json(out / "load_metrics.json", load_metrics)
    notify("upload", "completed", "Dataset loaded", True)

    # Step 2: QC
    notify("qc", "running")
    adata, qc_report = run_qc(adata, demo_mode=demo_mode)
    adata.write_h5ad(out / "qc.h5ad")
    save_json(out / "qc_report.json", qc_report)
    notify("qc", "completed", f"{qc_report['cells_remaining']} cells pass QC", True)

    # Step 3: Batch correction
    notify("batch_correction", "running")
    adata, batch_metrics = run_batch_correction(adata, demo_mode=demo_mode)
    save_json(out / "batch_correction.json", batch_metrics)
    notify("batch_correction", "completed", batch_metrics.get("method", "harmony"), True)

    # Step 4: Clustering
    notify("clustering", "running")
    adata, cluster_summary, umap_plot = run_clustering(adata, out, demo_mode=demo_mode)
    adata.write_h5ad(out / "clustered.h5ad")
    save_json(out / "cluster_summary.json", cluster_summary)
    notify(
        "clustering",
        "completed",
        f"{cluster_summary['n_clusters']} clusters",
        cluster_summary.get("silhouette_score", 0) is None
        or cluster_summary.get("silhouette_score", 0) >= 0.15,
    )

    # Step 5: Annotation
    notify("annotation", "running")
    adata, annotation_result = run_annotation(adata, demo_mode=demo_mode)
    cell_types = annotation_result["cell_types"]
    adata.write_h5ad(out / "annotated.h5ad")
    save_json(out / "annotation.json", annotation_result)
    notify(
        "annotation",
        "completed",
        f"{annotation_result['n_cell_types']} cell types",
        annotation_result["n_cell_types"] > 0,
    )

    # Step 6: Communication
    notify("communication", "running")
    edges, comm_metrics, network_plot, heatmap_plot = run_communication(
        adata, out, demo_mode=demo_mode
    )
    save_json(out / "communication.json", comm_metrics)
    notify(
        "communication",
        "completed",
        f"{len(edges)} interactions",
        len(edges) > 0,
    )

    # Step 7: Export
    notify("export", "running")
    plot_paths = {
        "umap": umap_plot,
        "network": network_plot,
        "heatmap": heatmap_plot,
    }
    exports = run_export(
        job_id,
        out,
        qc_report=qc_report,
        cluster_summary=cluster_summary,
        cell_types=cell_types,
        edges=edges,
        plot_paths=plot_paths,
    )
    notify("export", "completed", "Report generated", True)

    return {
        "qc_report": qc_report,
        "cluster_summary": cluster_summary,
        "cell_types": cell_types,
        "communication_edges": edges,
        "umap_plot": umap_plot,
        "network_plot": network_plot,
        "heatmap_plot": heatmap_plot,
        "exports": exports,
    }
