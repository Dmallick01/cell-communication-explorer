# Benchmark Datasets

Download and place benchmark data here for validation runs. **Do not commit raw expression data to git.**

## PBMC 3k

```bash
PYTHONPATH=. python -m pipeline.benchmarks.run --dataset pbmc3k --fetch
```

Or manually:

```bash
python -c "import scanpy as sc; ad=sc.datasets.pbmc3k(); ad.write_h5ad('benchmarks/pbmc3k/pbmc3k.h5ad')"
```

**Citation:** Zheng GXY et al. Massively parallel digital transcriptional profiling of single cells. Nat Commun. 2017.

## Kang IFN-β

```bash
PYTHONPATH=. python -m pipeline.benchmarks.run --dataset kang_ifn --fetch
```

Auto-downloads from figshare (scverse mirror, Kang et al. 2018).

**Citation:** Kang HM et al. Multiplexed droplet scRNA-seq of 8 Lupus patients. Nat Biotechnol. 2018.

## Run all Phase 0 benchmarks

```bash
pip install -r backend/requirements.txt
bash reference/nichenet/download_priors.sh
R -e 'install.packages("remotes"); remotes::install_github("saeyslab/nichenetr")'

PYTHONPATH=. python -m pipeline.benchmarks.run --dataset all --fetch
```

Reports: `benchmarks/pbmc3k_report.json`, `benchmarks/kang_ifn_report.json`

## Metadata requirements

Kang h5ad includes `stim` (IFN-β vs control) and `cell_type`. PBMC3k uses pipeline-derived clusters + CellTypist.
