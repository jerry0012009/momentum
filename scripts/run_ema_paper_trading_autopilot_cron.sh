#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$ROOT/logs"
LOCK_DIR="$ROOT/.locks"
LOCK_FILE="$LOCK_DIR/ema_paper_autopilot.lock"
PYTHON_BIN="python3"
if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT/.venv/bin/python"
fi

mkdir -p "$LOG_DIR" "$LOCK_DIR"
cd "$ROOT"

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] [skip] ema autopilot already running"
  exit 0
fi

"$PYTHON_BIN" "$ROOT/scripts/run_ema_paper_trading_autopilot.py"
