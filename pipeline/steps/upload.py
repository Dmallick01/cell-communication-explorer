from __future__ import annotations

from pathlib import Path
from typing import Any

import anndata as ad
import pandas as pd

from pipeline.utils.checkpoints import validate_input_sanity
from pipeline.utils.io import load_metadata


def load_dataset(
    input_path: str,
    metadata_path: str | None = None,
    demo_mode: bool = False,
) -> tuple[ad.AnnData, dict[str, Any]]:
    if demo_mode:
        return _synthetic_dataset(), {
            "n_cells": 500,
            "n_genes": 2000,
            "barcodes_unique": True,
            "source": "synthetic",
        }

    path = Path(input_path)
    adata: ad.AnnData

    if path.suffix.lower() == ".h5ad":
        adata = ad.read_h5ad(path)
    elif path.suffix.lower() in {".csv", ".tsv"}:
        sep = "\t" if path.suffix.lower() == ".tsv" else ","
        df = pd.read_csv(path, sep=sep, index_col=0)
        adata = ad.AnnData(df.T)
    else:
        raise ValueError(f"Unsupported input format: {path.suffix}")

    meta = load_metadata(metadata_path)
    if meta is not None:
        common = adata.obs_names.intersection(meta.index)
        if len(common) == 0:
            raise ValueError("Metadata barcodes do not match expression matrix")
        adata = adata[common].copy()
        adata.obs = adata.obs.join(meta.loc[common], how="left")

    metrics = {
        "n_cells": int(adata.n_obs),
        "n_genes": int(adata.n_vars),
        "barcodes_unique": adata.n_obs == len(set(adata.obs_names)),
        "source": str(path),
    }
    validate_input_sanity(metrics)
    return adata, metrics


def _synthetic_dataset() -> ad.AnnData:
    import numpy as np

    rng = np.random.default_rng(42)
    n_cells, n_genes = 500, 2000
    X = rng.negative_binomial(5, 0.3, size=(n_cells, n_genes)).astype(np.float32)
    cell_types = rng.choice(
        ["Macrophage", "Fibroblast", "T cell", "B cell", "Endothelial"],
        size=n_cells,
    )
    batches = rng.choice(["batch1", "batch2", "batch3"], size=n_cells)
    conditions = rng.choice(["control", "disease"], size=n_cells)

    adata = ad.AnnData(X)
    adata.obs_names = [f"cell_{i}" for i in range(n_cells)]
    adata.var_names = [f"gene_{i}" for i in range(n_genes)]
    adata.obs["cell_type_raw"] = cell_types
    adata.obs["batch"] = batches
    adata.obs["condition"] = conditions
    adata.var["gene_symbol"] = adata.var_names
    return adata
