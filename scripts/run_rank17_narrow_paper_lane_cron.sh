#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="python3"
if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT/.venv/bin/python"
fi

cd "$ROOT"

STATE="$ROOT/reports/artifacts/paper_rank17_pullback_ethsol_narrow_pilot/rank17_paper_state.json"

if [[ -f "$STATE" ]]; then
  "$PYTHON_BIN" scripts/run_rank17_narrow_paper_lane.py --refresh
else
  "$PYTHON_BIN" scripts/run_rank17_narrow_paper_lane.py --init-from-now
fi

bash scripts/publish_rank17_narrow_paper_lane_page.sh
