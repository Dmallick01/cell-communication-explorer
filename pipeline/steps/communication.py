from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import anndata as ad
import numpy as np
import pandas as pd
import seaborn as sns

from pipeline.integrations.nichenet import run_nichenet
from pipeline.utils.checkpoints import CheckpointError, validate_communication


def run_communication(
    adata: ad.AnnData,
    output_dir: Path,
    reference_dir: Path,
    demo_mode: bool = False,
) -> tuple[list[dict[str, Any]], dict[str, Any], str, str]:
    if demo_mode:
        raise CheckpointError(
            "Demo communication is disabled. Set DEVELOPMENT_ONLY=true for local synthetic runs, "
            "or install NicheNet priors (reference/nichenet/download_priors.sh) and R/nichenetr."
        )

    edges, metrics = run_nichenet(adata, output_dir, reference_dir)
    validate_communication(metrics)

    network_path = output_dir / "communication_network.png"
    heatmap_path = output_dir / "communication_heatmap.png"
    _save_network(edges, network_path)
    _save_heatmap(edges, heatmap_path)

    return edges, metrics, str(network_path), str(heatmap_path)


def _save_network(edges: list[dict[str, Any]], path: Path) -> None:
    if not edges:
        return

    top = edges[:20]
    labels = sorted(
        {e["source_cell_type"] for e in top} | {e["target_cell_type"] for e in top}
    )
    idx = {label: i for i, label in enumerate(labels)}
    n = len(labels)
    mat = np.zeros((n, n))

    for e in top:
        mat[idx[e["source_cell_type"]], idx[e["target_cell_type"]]] += float(e.get("score", 1))

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(mat, xticklabels=labels, yticklabels=labels, cmap="YlOrRd", ax=ax)
    ax.set_title("NicheNet cell-cell communication")
    ax.set_xlabel("Target")
    ax.set_ylabel("Source")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _save_heatmap(edges: list[dict[str, Any]], path: Path) -> None:
    if not edges:
        return

    df = pd.DataFrame(edges)
    pivot = df.pivot_table(
        index="ligand",
        columns=["source_cell_type", "target_cell_type"],
        values="score",
        aggfunc="max",
        fill_value=0,
    )
    fig, ax = plt.subplots(figsize=(10, max(4, len(pivot) * 0.3)))
    sns.heatmap(pivot, cmap="viridis", ax=ax)
    ax.set_title("Ligand-receptor interactions (NicheNet)")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)
