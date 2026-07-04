#!/usr/bin/env bash
# Start the production API locally (free, unlimited job runtime).
# Uses backend/.venv311 when present (fast); otherwise docker compose.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

mkdir -p data/uploads data/results

# Stop anything already bound to :8000
if lsof -ti:8000 >/dev/null 2>&1; then
  echo "Stopping process on port 8000..."
  lsof -ti:8000 | xargs kill -9 2>/dev/null || true
  sleep 1
fi

export MPLBACKEND=Agg
export PYTHONPATH="$ROOT"
export PIPELINE_DEMO_MODE=false
export DEVELOPMENT_ONLY=false
export DATA_DIR="$ROOT/data"

if [[ -x "$ROOT/backend/.venv311/bin/python" ]]; then
  echo "Starting API with backend/.venv311 (recommended on this machine)..."
  exec "$ROOT/backend/.venv311/bin/uvicorn" app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --app-dir backend
fi

echo "backend/.venv311 not found — falling back to Docker..."
exec docker compose -f docker-compose.prod.yml up --build api
