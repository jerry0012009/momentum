#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="python3"
if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT/.venv/bin/python"
fi

cd "$ROOT"
"$PYTHON_BIN" scripts/run_manual_narrow_paper_lanes.py --refresh
# Keep Rank29-related pages in the same publish chain as the shared narrow-paper refresh
# so manual narrow lanes, Rank29 shadow dashboard, monitoring hub, and clean replication
# all reflect the same post-refresh artifacts.
bash scripts/publish_rank29_shadow_dashboard.sh
