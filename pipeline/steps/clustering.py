from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import anndata as ad
import numpy as np
from sklearn.metrics import silhouette_score

from pipeline.steps.batch_correction import _demo_pca


def run_clustering(
    adata: ad.AnnData,
    output_dir: Path,
    demo_mode: bool = False,
) -> tuple[ad.AnnData, dict[str, Any], str]:
    adata = adata.copy()

    if demo_mode:
        adata, metrics = _demo_clustering(adata)
    else:
        adata, metrics = _scanpy_clustering(adata)

    plot_path = output_dir / "umap_clusters.png"
    _save_umap(adata, plot_path)

    cluster_counts = adata.obs["leiden"].value_counts().to_dict()
    metrics["cluster_counts"] = {str(k): int(v) for k, v in cluster_counts.items()}

    return adata, metrics, str(plot_path)


def _demo_clustering(adata: ad.AnnData) -> tuple[ad.AnnData, dict[str, Any]]:
    if "X_pca" not in adata.obsm:
        _demo_pca(adata)

    X = adata.obsm["X_pca"]
    # Use known cell types as cluster labels for a meaningful demo
    if "cell_type_raw" in adata.obs.columns:
        adata.obs["leiden"] = adata.obs["cell_type_raw"].astype(str)
    else:
        from sklearn.cluster import KMeans

        labels = KMeans(n_clusters=5, random_state=42, n_init=10).fit_predict(X)
        adata.obs["leiden"] = labels.astype(str)

    adata.obsm["X_umap"] = X[:, :2]
    labels = adata.obs["leiden"].astype(str)
    unique = sorted(labels.unique())
    label_ids = np.array([unique.index(v) for v in labels])
    silhouette = _silhouette(X, label_ids)

    return adata, {
        "n_clusters": len(unique),
        "silhouette_score": silhouette,
        "resolution": 0.8,
        "representation": "X_pca",
        "method": "demo",
    }


def _scanpy_clustering(adata: ad.AnnData) -> tuple[ad.AnnData, dict[str, Any]]:
    import scanpy as sc

    rep = "X_pca_harmony" if "X_pca_harmony" in adata.obsm else "X_pca"

    if rep not in adata.obsm:
        sc.pp.normalize_total(adata, target_sum=1e4)
        sc.pp.log1p(adata)
        sc.pp.highly_variable_genes(adata, n_top_genes=2000)
        adata = adata[:, adata.var.highly_variable].copy()
        sc.pp.scale(adata, max_value=10)
        sc.tl.pca(adata, n_comps=30)
        rep = "X_pca"

    sc.pp.neighbors(adata, use_rep=rep, n_neighbors=15)
    sc.tl.leiden(adata, resolution=0.8, key_added="leiden")
    sc.tl.umap(adata)

    silhouette = _silhouette(adata.obsm[rep], adata.obs["leiden"].astype(int))
    return adata, {
        "n_clusters": int(adata.obs["leiden"].nunique()),
        "silhouette_score": silhouette,
        "resolution": 0.8,
        "representation": rep,
        "method": "scanpy_leiden",
    }


def _silhouette(X: np.ndarray, labels: np.ndarray) -> float | None:
    try:
        if len(set(labels)) < 2:
            return None
        if X.shape[0] > 5000:
            idx = np.random.default_rng(0).choice(X.shape[0], 5000, replace=False)
            return float(silhouette_score(X[idx], labels[idx]))
        return float(silhouette_score(X, labels))
    except Exception:
        return None


def _save_umap(adata: ad.AnnData, path: Path) -> None:
    coords = adata.obsm.get("X_umap")
    if coords is None:
        return

    labels = adata.obs["leiden"].astype(str)
    fig, ax = plt.subplots(figsize=(8, 6))
    for cluster in sorted(labels.unique()):
        mask = labels == cluster
        ax.scatter(coords[mask, 0], coords[mask, 1], label=cluster, s=8, alpha=0.7)
    ax.set_title("Cell clusters")
    ax.legend(markerscale=2, fontsize=8)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)
