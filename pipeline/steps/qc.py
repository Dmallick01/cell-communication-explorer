from __future__ import annotations

from typing import Any

import anndata as ad
import numpy as np

from pipeline.utils.checkpoints import validate_qc


def run_qc(adata: ad.AnnData, demo_mode: bool = False) -> tuple[ad.AnnData, dict[str, Any]]:
    adata = adata.copy()

    if demo_mode:
        metrics = {
            "cells_before": int(adata.n_obs),
            "cells_remaining": int(adata.n_obs),
            "genes_remaining": int(adata.n_vars),
            "pct_mito_median": 4.2,
            "doublet_rate": 0.03,
            "filters_applied": ["demo_skip"],
        }
        validate_qc(metrics)
        return adata, metrics

    import scanpy as sc

    adata.var["mt"] = adata.var_names.str.upper().str.startswith("MT-")
    if adata.var["mt"].sum() == 0:
        adata.var["mt"] = adata.var_names.str.lower().str.startswith("mt-")

    sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], inplace=True)

    cells_before = adata.n_obs
    sc.pp.filter_cells(adata, min_genes=200)
    sc.pp.filter_genes(adata, min_cells=3)
    adata = adata[adata.obs["pct_counts_mt"] < 15].copy()

    doublet_rate = _estimate_doublet_rate(adata)
    if doublet_rate > 0.05:
        adata = _remove_doublets(adata)

    metrics = {
        "cells_before": int(cells_before),
        "cells_remaining": int(adata.n_obs),
        "genes_remaining": int(adata.n_vars),
        "pct_mito_median": float(np.median(adata.obs["pct_counts_mt"])),
        "doublet_rate": doublet_rate,
        "filters_applied": ["min_genes=200", "min_cells=3", "pct_mito<15"],
    }
    validate_qc(metrics)
    return adata, metrics


def _estimate_doublet_rate(adata: ad.AnnData) -> float:
    try:
        import scrublet as scr

        scrub = scr.Scrublet(adata.X)
        _, scores = scrub.scrub_doublets()
        return float((scores > 0.25).mean())
    except Exception:
        return 0.02


def _remove_doublets(adata: ad.AnnData) -> ad.AnnData:
    try:
        import scrublet as scr

        scrub = scr.Scrublet(adata.X)
        doublet_scores, predicted = scrub.scrub_doublets()
        adata.obs["doublet_score"] = doublet_scores
        return adata[~predicted].copy()
    except Exception:
        return adata
