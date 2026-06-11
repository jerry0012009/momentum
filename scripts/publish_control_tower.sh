#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SITE_SRC="$ROOT/reports/site"
PLANS_SRC="$SITE_SRC/plans"
SITE_DST="/var/www/momentum-report"
PLANS_DST="$SITE_DST/plans"
LOCK_FILE="/tmp/momentum-control-tower-sync.lock"

PYTHON_BIN="python3"
if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT/.venv/bin/python"
fi

mkdir -p "$(dirname "$LOCK_FILE")"
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "[skip] another control-tower publish is already running"
  exit 0
fi

"$PYTHON_BIN" "$ROOT/scripts/build_plans_site.py"

sudo mkdir -p "$PLANS_DST"
sudo rsync -a --delete "$PLANS_SRC/" "$PLANS_DST/"

if [[ -f "$SITE_SRC/index.html" ]]; then
  sudo install -m 0644 "$SITE_SRC/index.html" "$SITE_DST/index.html"
fi

sudo chown -R www-data:www-data "$PLANS_DST"
if [[ -f "$SITE_DST/index.html" ]]; then
  sudo chown www-data:www-data "$SITE_DST/index.html"
fi

echo "[ok] control tower published"
echo "[url] https://jp.jerrypsy.top/momentum/plans/momentum_todo.html"
