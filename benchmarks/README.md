# Benchmark Datasets

Download and place benchmark data here for validation runs. **Do not commit raw expression data to git.**

## PBMC 3k

```bash
mkdir -p benchmarks/pbmc3k
# Option A: Scanpy built-in
python -c "import scanpy as sc; ad=sc.datasets.pbmc3k(); ad.write_h5ad('benchmarks/pbmc3k/pbmc3k.h5ad')"
```

**Citation:** Zheng GXY et al. Massively parallel digital transcriptional profiling of single cells. Nat Commun. 2017.

## Kang IFN-β

```bash
mkdir -p benchmarks/kang_ifn
# Download from GEO GSE96583 and export as h5ad with condition metadata
```

**Citation:** Kang HM et al. Multiplexed droplet scRNA-seq of 8 Lupus patients. Nat Biotechnol. 2018.

## Metadata requirements

Each benchmark metadata CSV must include:
- `condition` (or `stim`) column for disease/control comparisons
- `batch` if multiple donors (for Harmony)
