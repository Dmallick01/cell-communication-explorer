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
    run_de,
    run_export,
    run_qc,
)
from pipeline.utils.checkpoints import clustering_quality_ok
from pipeline.utils.io import save_json
from pipeline.utils.provenance import write_provenance_bundle

StepCallback = Callable[[str, str, str | None, bool | None], None]


def run_pipeline(
    job_id: str,
    input_path: str,
    metadata_path: str | None,
    output_dir: str,
    reference_dir: str | None = None,
    demo_mode: bool = False,
    on_step: StepCallback | None = None,
) -> dict[str, Any]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    ref = Path(reference_dir) if reference_dir else Path("reference")

    def notify(step: str, status: str, message: str | None = None, checkpoint: bool | None = None):
        if on_step:
            on_step(step, status, message, checkpoint)

    step_outputs: dict[str, Any] = {}

    notify("upload", "running")
    adata, load_metrics = load_dataset(input_path, metadata_path, demo_mode=demo_mode)
    adata.write_h5ad(out / "processed.h5ad")
    save_json(out / "load_metrics.json", load_metrics)
    step_outputs["upload"] = load_metrics
    notify("upload", "completed", "Dataset loaded", True)

    notify("qc", "running")
    adata, qc_report = run_qc(adata, demo_mode=demo_mode)
    adata.write_h5ad(out / "qc.h5ad")
    save_json(out / "qc_report.json", qc_report)
    step_outputs["qc"] = qc_report
    notify("qc", "completed", f"{qc_report['cells_remaining']} cells pass QC", True)

    notify("batch_correction", "running")
    adata, batch_metrics = run_batch_correction(adata, demo_mode=demo_mode)
    save_json(out / "batch_correction.json", batch_metrics)
    step_outputs["batch_correction"] = batch_metrics
    notify("batch_correction", "completed", batch_metrics.get("method", "harmony"), True)

    notify("clustering", "running")
    adata, cluster_summary, umap_plot = run_clustering(adata, out, demo_mode=demo_mode)
    adata.write_h5ad(out / "clustered.h5ad")
    save_json(out / "cluster_summary.json", cluster_summary)
    step_outputs["clustering"] = cluster_summary
    silhouette = cluster_summary.get("silhouette_score")
    cluster_msg = f"{cluster_summary['n_clusters']} clusters"
    if silhouette is not None:
        cluster_msg += f" (silhouette {silhouette:.3f})"
    notify(
        "clustering",
        "completed",
        cluster_msg,
        clustering_quality_ok(cluster_summary, demo_mode=demo_mode),
    )

    notify("annotation", "running")
    adata, annotation_result = run_annotation(adata, demo_mode=demo_mode)
    cell_types = annotation_result["cell_types"]
    adata.write_h5ad(out / "annotated.h5ad")
    save_json(out / "annotation.json", annotation_result)
    step_outputs["annotation"] = annotation_result
    notify(
        "annotation",
        "completed",
        f"{annotation_result['n_cell_types']} cell types",
        annotation_result["n_cell_types"] > 0,
    )

    notify("de", "running")
    de_summary, de_tables = run_de(adata, out, demo_mode=demo_mode)
    save_json(out / "de_summary.json", de_summary)
    step_outputs["de"] = de_summary
    notify("de", "completed", f"{de_summary.get('n_genes_reported', 0)} DE genes", True)

    notify("communication", "running")
    edges, comm_metrics, network_plot, heatmap_plot = run_communication(
        adata, out, ref, demo_mode=demo_mode
    )
    save_json(out / "communication.json", comm_metrics)
    step_outputs["communication"] = comm_metrics
    notify("communication", "completed", f"{len(edges)} interactions (NicheNet)", len(edges) > 0)

    plot_paths = {"umap": umap_plot, "network": network_plot, "heatmap": heatmap_plot}
    parameters = {
        "communication_method": "nichenet",
        "batch_correction": batch_metrics.get("method"),
        "celltypist_model": annotation_result.get("method"),
        "demo_mode": demo_mode,
    }
    prov_exports = write_provenance_bundle(
        out,
        job_id,
        parameters=parameters,
        reference_dir=ref,
        step_outputs=step_outputs,
    )

    notify("export", "running")
    exports = run_export(
        job_id,
        out,
        qc_report=qc_report,
        cluster_summary=cluster_summary,
        cell_types=cell_types,
        edges=edges,
        plot_paths=plot_paths,
        methods_path=prov_exports.get("methods"),
    )
    exports.update(prov_exports)
    de_csv = out / "de_genes.csv"
    if de_csv.is_file():
        exports["de_genes"] = str(de_csv)
    umap_json = out / "umap_coords.json"
    if umap_json.is_file():
        exports["umap_coords"] = str(umap_json)
    notify("export", "completed", "Report + methods + provenance", True)

    umap_data = None
    umap_path = out / "umap_coords.json"
    if umap_path.is_file():
        umap_data = json.loads(umap_path.read_text())

    return {
        "qc_report": qc_report,
        "cluster_summary": cluster_summary,
        "cell_types": cell_types,
        "de_summary": de_summary,
        "de_tables": de_tables[:200],
        "umap_data": umap_data,
        "communication_edges": edges,
        "umap_plot": umap_plot,
        "network_plot": network_plot,
        "heatmap_plot": heatmap_plot,
        "exports": exports,
        "communication_method": "nichenet",
        "demo_mode": demo_mode,
    }
