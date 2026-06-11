#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/reports/site/index.html"
DST_DIR="/var/www/momentum-report"
DST="$DST_DIR/index.html"

PYTHON_BIN="python3"
if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT/.venv/bin/python"
fi

"$PYTHON_BIN" "$ROOT/scripts/build_site_index.py"

mkdir -p "$DST_DIR"
install -m 0644 "$SRC" "$DST"
if [[ "$(id -u)" -eq 0 ]]; then
  chown www-data:www-data "$DST"
fi

echo "[ok] homepage index published -> $DST"
echo "[url] https://jp.jerrypsy.top/momentum/"
