from __future__ import annotations

from typing import Any


class CheckpointError(Exception):
    """Raised when a hard scientific checkpoint fails."""


def validate_input_sanity(metrics: dict[str, Any]) -> None:
    if metrics.get("n_cells", 0) < 50:
        raise CheckpointError("Dataset has fewer than 50 cells after loading")
    if metrics.get("n_genes", 0) < 200:
        raise CheckpointError("Dataset has fewer than 200 genes")
    if not metrics.get("barcodes_unique", True):
        raise CheckpointError("Duplicate cell barcodes detected")


def validate_qc(metrics: dict[str, Any]) -> None:
    if metrics.get("pct_mito_median", 0) > 25:
        raise CheckpointError("Median mitochondrial % exceeds 25% after QC")
    if metrics.get("doublet_rate", 0) > 0.10:
        raise CheckpointError("Doublet rate exceeds 10%")
    if metrics.get("cells_remaining", 0) < 30:
        raise CheckpointError("Fewer than 30 cells remain after QC filtering")


def clustering_quality_ok(metrics: dict[str, Any], *, demo_mode: bool = False) -> bool:
    """Advisory checkpoint — low silhouette warns but does not fail the pipeline."""
    if demo_mode:
        return True
    silhouette = metrics.get("silhouette_score")
    if silhouette is None:
        return True
    return silhouette >= 0.15


def validate_communication(metrics: dict[str, Any]) -> None:
    if metrics.get("n_edges", 0) == 0:
        raise CheckpointError("No significant ligand-receptor interactions detected")
