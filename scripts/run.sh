#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-9090}"
HOST="${HOST:-0.0.0.0}"
INTERVAL="${TICK_INTERVAL_SEC:-3.5}"

echo "⚡ [Metropolis] Launching Bengaluru Living Agent Metropolis OS on http://${HOST}:${PORT}..."

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

exec python3 server.py --port "${PORT}" --host "${HOST}" --interval "${INTERVAL}"
