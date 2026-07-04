#!/usr/bin/env bash
# Expose local :8000 to the internet via Cloudflare Quick Tunnel (free HTTPS URL).
# Use the printed URL as NEXT_PUBLIC_API_URL on Vercel (+ /api/v1).
set -euo pipefail

if ! command -v cloudflared >/dev/null 2>&1; then
  echo "Installing cloudflared..."
  if command -v brew >/dev/null 2>&1; then
    brew install cloudflared
  else
    echo "Install cloudflared: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/"
    exit 1
  fi
fi

if ! curl -sf http://127.0.0.1:8000/api/v1/health >/dev/null 2>&1; then
  echo "API not running on :8000. Start it first:"
  echo "  bash scripts/start-local-api.sh"
  exit 1
fi

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT/.local-deploy.env"

echo ""
echo "Starting Cloudflare tunnel → http://127.0.0.1:8000"
echo "Watch for https://….trycloudflare.com below."
echo "Press Ctrl+C to stop the tunnel."
echo ""

cloudflared tunnel --url http://127.0.0.1:8000 2>&1 | tee /tmp/cce-cloudflared.log | while IFS= read -r line; do
  printf '%s\n' "$line"
  url=$(printf '%s' "$line" | grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' | head -1)
  if [[ -n "$url" ]]; then
    printf 'NEXT_PUBLIC_API_URL=%s/api/v1\n' "$url" >"$ENV_FILE"
    echo ""
    echo "Saved to .local-deploy.env — set on Vercel and redeploy frontend."
  fi
done
