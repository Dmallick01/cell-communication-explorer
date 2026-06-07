# Cell Communication Explorer

MVP platform for single-cell RNA-seq analysis focused on **cell-to-cell communication discovery**.

Upload scRNA-seq data → QC → Harmony batch correction → Leiden clustering → CellTypist annotation → ligand-receptor network inference → exportable report.

Built for scientific rigor first. No vector DB, no multi-agent orchestration, no literature AI in v1.

## Architecture

```
frontend/     Next.js + MUI dashboard
backend/      FastAPI job API (upload, status, results)
pipeline/     Sequential scientific pipeline (Scanpy, Harmony, CellTypist)
```

## Quick Start (local)

### 1. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-api.txt

# Demo mode (synthetic data, no heavy deps):
export PIPELINE_DEMO_MODE=true
export PYTHONPATH=".."
uvicorn app.main:app --reload --port 8000
```

For full scientific pipeline, install `requirements.txt` (includes Scanpy, Harmony, CellTypist).

### 2. Frontend

```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

Open http://localhost:3000

### 3. Docker

```bash
docker compose up --build
```

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health` | GET | Health check |
| `/api/v1/jobs` | POST | Upload data + start pipeline |
| `/api/v1/jobs/{id}` | GET | Job status + step progress |
| `/api/v1/jobs/{id}/results` | GET | Analysis results |
| `/api/v1/jobs/{id}/artifacts/{file}` | GET | Plots, reports, CSV exports |

## Pipeline Steps (v1.0)

1. **Upload** — validate `.h5ad`, 10x MTX (`.zip`), CSV; barcode uniqueness
2. **QC** — mitochondrial %, gene/cell filters, Scrublet doublets
3. **Batch correction** — Harmony (when `batch` column present)
4. **Clustering** — PCA, Leiden, UMAP + silhouette checkpoint
5. **Annotation** — CellTypist (Immune_All_Low model)
6. **Communication** — NicheNet-style LR scoring (curated panel + expression)
7. **Export** — HTML report, CSV tables, JSON summaries

## Version Roadmap

| Version | Features |
|---------|----------|
| **1.0** (current) | Full pipeline, visualization, export |
| **1.1** | PubMed / Europe PMC links (no AI) |
| **1.2** | Cited literature summarization |
| **2.0** | Vector knowledge base |
| **3.0** | Experiment design suggestions |

## Development

```bash
# Pipeline smoke test
PYTHONPATH=. python -c "from pipeline.runner import run_pipeline; import tempfile; print(run_pipeline('t','/dev/null',None,tempfile.mkdtemp(),demo_mode=True))"
```

## License

MIT
