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

    import logging

    logger = logging.getLogger(__name__)

    try:
        import celltypist
        from celltypist import models

        ct_adata = adata.copy()
        if "log1p" not in ct_adata.uns:
            import scanpy as sc

            sc.pp.normalize_total(ct_adata, target_sum=1e4)
            sc.pp.log1p(ct_adata)

        model = models.Model.load(model="Immune_All_Low.pkl")
        predictions = celltypist.annotate(ct_adata, model=model, majority_voting=False)
        labels = predictions.predicted_labels
        if isinstance(labels, pd.DataFrame):
            labels = labels.iloc[:, 0]
        adata.obs["cell_type"] = labels.astype(str).values
        method = "celltypist"
    except Exception as exc:
        logger.warning("CellTypist failed (%s); using leiden cluster labels", exc)
        adata.obs["cell_type"] = adata.obs["leiden"].astype(str).map(
            lambda c: f"Cluster {c}"
        )
        method = "cluster_fallback"

    summary = _cell_type_summary(adata)
    return adata, {
        "method": method,
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
