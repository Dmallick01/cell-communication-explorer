# Deployment Guide

Frontend: **Vercel** (already live)  
Backend: **Fly.io** (recommended) or **Render**

## Prerequisites

- NicheNet priors bundled in `reference/nichenet/` (included in Docker image)
- R + `nichenetr` installed in Docker image (`Dockerfile.backend`)
- Persistent disk for `data/` (SQLite job DB + uploads + results)

---

## Option A: Fly.io (recommended)

### 1. Install CLI and authenticate

```bash
brew install flyctl
fly auth login
```

### 2. Create app + volume (first time only)

```bash
cd /path/to/cell-communication-explorer
fly apps create cell-communication-api   # skip if name taken — edit fly.toml
fly volumes create cce_data --region iad --size 10
```

### 3. Set secrets

```bash
fly secrets set \
  CORS_ORIGINS='["https://frontend-sigma-nine-39.vercel.app","https://frontend-dmallick01s-projects.vercel.app"]' \
  DEVELOPMENT_ONLY=false \
  PIPELINE_DEMO_MODE=false
```

### 4. Deploy

```bash
fly deploy
```

### 5. Verify

```bash
fly status
curl https://cell-communication-api.fly.dev/api/v1/health
```

### 6. Connect Vercel frontend

In Vercel project settings → Environment Variables:

```
NEXT_PUBLIC_API_URL=https://cell-communication-api.fly.dev/api/v1
```

Redeploy frontend.

---

## Option B: Render

1. Connect GitHub repo in Render dashboard
2. New **Blueprint** → point at `render.yaml`
3. Deploy `cell-communication-api` web service
4. Set `NEXT_PUBLIC_API_URL` on Vercel to the Render URL + `/api/v1`

---

## Local production smoke test

```bash
docker build -f Dockerfile.backend -t cce-api .
docker run --rm -p 8000:8000 -v "$(pwd)/data:/app/data" cce-api
curl http://127.0.0.1:8000/api/v1/health
```

---

## Phase 0 benchmarks (before claiming research-grade)

```bash
pip install -r backend/requirements.txt
bash reference/nichenet/download_priors.sh
R -e 'install.packages("remotes"); remotes::install_github("saeyslab/nichenetr")'

# PBMC 3k (auto-download)
PYTHONPATH=. python -m pipeline.benchmarks.run --dataset pbmc3k --fetch

# Kang IFN-β (auto-download ~25k cells — allow 30–45 min)
PYTHONPATH=. python -m pipeline.benchmarks.run --dataset kang_ifn --fetch

# Both
PYTHONPATH=. python -m pipeline.benchmarks.run --dataset all --fetch
```

Reports written to `benchmarks/pbmc3k_report.json` and `benchmarks/kang_ifn_report.json`.

Quick smoke (subsampled, not a Phase 0 pass):

```bash
PYTHONPATH=. python -m pipeline.benchmarks.run --dataset pbmc3k --fetch --max-cells 800
```

---

## Resource requirements

| Workload | RAM | Time |
|----------|-----|------|
| PBMC 3k full | ~4 GB | 10–20 min |
| Kang IFN full | ~6–8 GB | 30–45 min |

Fly VM is configured for **4 GB** in `fly.toml`. Bump to `8gb` if Kang jobs OOM.
