from __future__ import annotations

from pathlib import Path
from typing import Any

import anndata as ad
import numpy as np
import pandas as pd


def _condition_column(adata: ad.AnnData) -> str | None:
    for col in ("condition", "stim", "disease", "group", "treatment", "status"):
        if col in adata.obs.columns and adata.obs[col].nunique() >= 2:
            return col
    return None


def _demo_de(adata: ad.AnnData, label_col: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    tables: list[dict[str, Any]] = []
    for ct in adata.obs[label_col].astype(str).unique()[:6]:
        for gene in ("CD3D", "IL7R", "MS4A1", "FCGR3A", "PPBP"):
            if gene in adata.var_names:
                tables.append(
                    {
                        "names": gene,
                        "scores": float(np.random.default_rng(hash(ct) % 2**32).uniform(1, 5)),
                        "pvals_adj": 0.001,
                        "cell_type": ct,
                        "comparison": "markers vs rest",
                    }
                )
    return (
        {"method": "demo", "label_column": label_col, "n_genes_reported": len(tables)},
        tables,
    )


def run_de(
    adata: ad.AnnData,
    output_dir: Path,
    demo_mode: bool = False,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Marker genes per cell type; condition DE when a comparison column exists."""
    adata = adata.copy()
    label_col = "cell_type" if "cell_type" in adata.obs.columns else "leiden"
    condition_col = _condition_column(adata)

    if demo_mode or adata.n_obs < 50:
        return _demo_de(adata, label_col)

    try:
        import scanpy as sc
    except ImportError:
        return _demo_de(adata, label_col)

    tables: list[dict[str, Any]] = []

    if condition_col:
        groups = adata.obs[condition_col].astype(str).unique().tolist()
        if len(groups) == 2:
            case, control = groups[0], groups[1]
            sc.tl.rank_genes_groups(
                adata,
                groupby=label_col,
                reference=control,
                groups=adata.obs[label_col].astype(str).unique().tolist(),
                method="wilcoxon",
                key_added="de_condition",
            )
            for ct in adata.obs[label_col].astype(str).unique():
                df = sc.get.rank_genes_groups_df(adata, group=ct, key="de_condition")
                df = df.head(25)
                df["cell_type"] = ct
                df["comparison"] = f"{case} vs {control}"
                tables.extend(df.to_dict(orient="records"))
        else:
            condition_col = None

    if not condition_col:
        min_cells = 2
        counts = adata.obs[label_col].astype(str).value_counts()
        valid_groups = counts[counts >= min_cells].index.tolist()
        if len(valid_groups) < 2:
            return _demo_de(adata, label_col)
        sc.tl.rank_genes_groups(
            adata,
            groupby=label_col,
            groups=valid_groups,
            method="wilcoxon",
            key_added="de_markers",
        )
        for ct in valid_groups:
            df = sc.get.rank_genes_groups_df(adata, group=ct, key="de_markers")
            df = df.head(15)
            df["cell_type"] = ct
            df["comparison"] = "markers vs rest"
            tables.extend(df.to_dict(orient="records"))

    de_path = output_dir / "de_genes.csv"
    if tables:
        pd.DataFrame(tables).to_csv(de_path, index=False)

    summary = {
        "method": "wilcoxon" if not demo_mode else "demo",
        "label_column": label_col,
        "condition_column": condition_col,
        "n_genes_reported": len(tables),
        "comparisons": sorted({t.get("comparison", "") for t in tables}),
    }
    return summary, tables
