# Validation Protocol — Cell Communication Explorer

This document defines how we prove the pipeline is research-grade before shipping features.

## Reference

- Master spec: `CURSOR_MASTER_BUILD_PROMPT.md`
- NicheNet: Browaeys et al., Nat Methods 2020 ([doi:10.1038/s41592-019-0667-5](https://doi.org/10.1038/s41592-019-0667-5))

## Prerequisites

```bash
# 1. NicheNet priors (required)
bash reference/nichenet/download_priors.sh

# 2. R + nichenetr
R -e 'install.packages("nichenetr")'

# 3. Python scientific stack
pip install -r backend/requirements.txt
```

## Benchmark datasets

| ID | Source | Citation | Expected biology |
|----|--------|----------|------------------|
| `pbmc3k` | 10x Genomics 3k PBMC | Zheng et al. 2017 | Immune cell types; known CCL–CCR, cytokine pairs |
| `kang_ifn` | GEO GSE96583 | Kang et al. 2018 | IFN-stimulated immune response; IFNG–IFNGR axis |

Place files under `benchmarks/pbmc3k/` and `benchmarks/kang_ifn/` (not committed — download separately).

## Acceptance criteria (Phase 0 pass)

### PBMC 3k
- [ ] ≥6 cell types annotated with CellTypist (confidence documented)
- [ ] NicheNet returns ≥10 ligand–receptor edges
- [ ] `methods.txt` cites Scanpy, CellTypist, NicheNet with correct DOIs
- [ ] `provenance.json` contains SHA256 of all NicheNet prior files
- [ ] No demo/synthetic code path used

### Kang IFN-β
- [ ] Disease vs control DE detects ISG genes in stimulated cells
- [ ] Top NicheNet edges include IFN-pathway ligands (IFNG, IFNB1, or downstream)
- [ ] Pipeline completes in <45 min on M1 MacBook (8GB RAM baseline)

## Run benchmark (manual)

```bash
export PYTHONPATH=.
python -m pipeline.benchmarks.run --dataset pbmc3k --input benchmarks/pbmc3k/pbmc3k.h5ad
```

## Failure policy

- Missing NicheNet priors → **hard fail** with setup instructions (no fallback scoring)
- Low silhouette → **warning** in report, not job failure
- Zero LR edges → **hard fail** with diagnostic message

## Evidence tier definitions

| Tier | Meaning |
|------|---------|
| ESTABLISHED | Multiple PMIDs + database support |
| SUPPORTED | NicheNet prior + expression in sender/receiver |
| HYPOTHESIS | Computational only — requires experiment |
