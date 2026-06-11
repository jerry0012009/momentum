#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$ROOT/logs"
LOCK_DIR="$ROOT/.locks"
LOCK_FILE="$LOCK_DIR/rank151_breakout_bandpass_paper_runner.lock"
PYTHON_BIN="python3"
if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT/.venv/bin/python"
fi

mkdir -p "$LOG_DIR" "$LOCK_DIR"
cd "$ROOT"

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] [skip] rank151 breakout band-pass paper runner already running"
  exit 0
fi

STATE="$ROOT/reports/artifacts/paper_rank151_breakout_bandpass_gate/rank151_paper_state.json"
if [[ -f "$STATE" ]]; then
  "$PYTHON_BIN" "$ROOT/scripts/run_rank151_breakout_bandpass_paper_runner.py" --refresh
else
  "$PYTHON_BIN" "$ROOT/scripts/run_rank151_breakout_bandpass_paper_runner.py" --init-from-now
fi

bash "$ROOT/scripts/publish_rank151_breakout_bandpass_paper_page.sh"
