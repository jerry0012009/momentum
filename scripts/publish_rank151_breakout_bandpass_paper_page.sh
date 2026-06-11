#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="python3"
if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT/.venv/bin/python"
fi

"$PYTHON_BIN" "$ROOT/scripts/build_rank151_breakout_bandpass_paper_report.py"

SLUG="paper_rank151_breakout_bandpass_gate"
SRC_PAGE="$ROOT/reports/site/factors/$SLUG/report.html"
SRC_ART="$ROOT/reports/artifacts/$SLUG"
DST_ROOT="/var/www/momentum-report"
DST_PAGE_DIR="$DST_ROOT/factors/$SLUG"
DST_ART_DIR="$DST_ROOT/artifacts/$SLUG"

sudo mkdir -p "$DST_PAGE_DIR" "$DST_ART_DIR"
sudo install -m 0644 "$SRC_PAGE" "$DST_PAGE_DIR/report.html"
if [[ -d "$SRC_ART" ]]; then
  sudo rsync -a "$SRC_ART/" "$DST_ART_DIR/"
fi
sudo chown -R www-data:www-data "$DST_PAGE_DIR" "$DST_ART_DIR"

echo "[ok] published -> $DST_PAGE_DIR/report.html"
echo "[url] https://jp.jerrypsy.top/momentum/factors/$SLUG/report.html"
