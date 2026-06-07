from __future__ import annotations

from typing import Any

import anndata as ad
import numpy as np


def run_batch_correction(
    adata: ad.AnnData,
    batch_key: str = "batch",
    demo_mode: bool = False,
) -> tuple[ad.AnnData, dict[str, Any]]:
    adata = adata.copy()

    if demo_mode or batch_key not in adata.obs.columns:
        if "X_pca" not in adata.obsm:
            _demo_pca(adata)
        metrics = {
            "method": "none",
            "batch_key": batch_key,
            "n_batches": int(adata.obs[batch_key].nunique()) if batch_key in adata.obs else 1,
            "message": "Skipped — no batch column or demo mode",
        }
        return adata, metrics

    import scanpy as sc

    work = adata.copy()
    sc.pp.normalize_total(work, target_sum=1e4)
    sc.pp.log1p(work)
    work.uns["log1p"] = {"base": None}
    sc.pp.highly_variable_genes(work, n_top_genes=2000, batch_key=batch_key)
    hvg = work[:, work.var.highly_variable].copy()
    sc.pp.scale(hvg, max_value=10)
    sc.tl.pca(hvg, n_comps=30)

    import harmonypy as hm

    ho = hm.run_harmony(hvg.obsm["X_pca"], hvg.obs, batch_key)
    work.obsm["X_pca_harmony"] = ho.Z_corr.T

    metrics = {
        "method": "harmony",
        "batch_key": batch_key,
        "n_batches": int(work.obs[batch_key].nunique()),
        "n_hvg": int(hvg.n_vars),
    }
    return work, metrics


def _demo_pca(adata: ad.AnnData, n_comps: int = 30) -> None:
    from sklearn.decomposition import PCA

    X = adata.X.toarray() if hasattr(adata.X, "toarray") else np.asarray(adata.X)
    n_comps = min(n_comps, X.shape[0] - 1, X.shape[1])
    adata.obsm["X_pca"] = PCA(n_components=n_comps).fit_transform(X)
