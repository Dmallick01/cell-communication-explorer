#!/usr/bin/env bash
# One command: start API in background + print tunnel instructions.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG="$ROOT/data/local-api.log"

mkdir -p "$ROOT/data"

if lsof -ti:8000 >/dev/null 2>&1; then
  echo "API already listening on :8000"
else
  echo "Starting local API in background (log: data/local-api.log)..."
  nohup bash "$ROOT/scripts/start-local-api.sh" >"$LOG" 2>&1 &
  for _ in $(seq 1 30); do
    if curl -sf http://127.0.0.1:8000/api/v1/health >/dev/null 2>&1; then
      break
    fi
    sleep 1
  done
fi

if curl -sf http://127.0.0.1:8000/api/v1/health; then
  echo ""
  echo "Local API healthy at http://127.0.0.1:8000/api/v1/health"
  echo ""
  echo "To reach from Vercel frontend anywhere, run in another terminal:"
  echo "  bash scripts/expose-api.sh"
  echo ""
  echo "Then set NEXT_PUBLIC_API_URL=<tunnel-url>/api/v1 on Vercel and redeploy."
else
  echo "API failed to start. Check $LOG"
  tail -30 "$LOG" 2>/dev/null || true
  exit 1
fi
