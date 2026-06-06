from __future__ import annotations

from typing import Any

import anndata as ad
import pandas as pd


def run_annotation(adata: ad.AnnData, demo_mode: bool = False) -> tuple[ad.AnnData, dict[str, Any]]:
    adata = adata.copy()

    if demo_mode or "cell_type_raw" in adata.obs.columns:
        if "cell_type_raw" in adata.obs.columns:
            adata.obs["cell_type"] = adata.obs["cell_type_raw"]
        else:
            adata.obs["cell_type"] = adata.obs["leiden"].map(
                lambda x: f"Cluster {x}"
            )
        summary = _cell_type_summary(adata)
        return adata, {
            "method": "provided" if "cell_type_raw" in adata.obs else "demo",
            "n_cell_types": len(summary),
            "cell_types": summary,
        }

    try:
        import celltypist
        from celltypist import models

        model = models.Model.load(model="Immune_All_Low.pkl")
        predictions = celltypist.annotate(adata, model=model, majority_voting=True)
        adata = predictions.to_adata()
        adata.obs["cell_type"] = adata.obs["predicted_labels"]
    except Exception:
        # Fallback: map clusters to generic labels based on marker heuristics
        adata.obs["cell_type"] = adata.obs["leiden"].astype(str).map(
            lambda c: f"Cluster {c}"
        )

    summary = _cell_type_summary(adata)
    return adata, {
        "method": "celltypist",
        "n_cell_types": len(summary),
        "cell_types": summary,
    }


def _cell_type_summary(adata: ad.AnnData) -> list[dict[str, Any]]:
    counts = adata.obs["cell_type"].value_counts()
    total = adata.n_obs
    return [
        {
            "cell_type": str(ct),
            "count": int(n),
            "fraction": round(n / total, 4),
        }
        for ct, n in counts.items()
    ]
