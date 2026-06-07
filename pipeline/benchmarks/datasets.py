from __future__ import annotations

import urllib.request
from pathlib import Path

import anndata as ad

PBMC3K_PATH = Path("benchmarks/pbmc3k/pbmc3k.h5ad")
KANG_IFN_PATH = Path("benchmarks/kang_ifn/kang_ifn.h5ad")
KANG_FIGSHARE_URL = "https://figshare.com/ndownloader/files/34464122"


def fetch_pbmc3k(dest: Path | None = None) -> Path:
    """Download PBMC 3k via Scanpy (Zheng et al., Nat Commun 2017)."""
    import scanpy as sc

    path = dest or PBMC3K_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file():
        return path
    adata = sc.datasets.pbmc3k()
    adata.write_h5ad(path)
    return path


def fetch_kang_ifn(dest: Path | None = None) -> Path:
    """Download Kang IFN-β PBMC h5ad (Kang et al., Nat Biotechnol 2018)."""
    path = dest or KANG_IFN_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file():
        return path

    tmp = path.with_suffix(".h5ad.part")
    print(f"Downloading Kang IFN-β from figshare → {path}")
    urllib.request.urlretrieve(KANG_FIGSHARE_URL, tmp)
    tmp.rename(path)
    ad.read_h5ad(path)  # validate
    return path


def resolve_dataset(name: str, fetch: bool = False) -> Path:
    name = name.lower().replace("-", "_")
    if name in ("pbmc3k", "pbmc_3k"):
        path = PBMC3K_PATH
        if fetch and not path.is_file():
            return fetch_pbmc3k(path)
        return path
    if name in ("kang_ifn", "kang", "kang_ifn_beta"):
        path = KANG_IFN_PATH
        if fetch and not path.is_file():
            return fetch_kang_ifn(path)
        return path
    raise ValueError(f"Unknown dataset: {name}. Use pbmc3k or kang_ifn.")
