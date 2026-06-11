#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="python3"
if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT/.venv/bin/python"
fi

EMA_SRC_PAGE="$ROOT/reports/site/factors/ema_psar_raw_alpha/report.html"
EMA_SRC_ART_DIR="$ROOT/reports/artifacts/ema_psar_raw_alpha"
DST_ROOT="/var/www/momentum-report"
EMA_DST_PAGE_DIR="$DST_ROOT/factors/ema_psar_raw_alpha"
EMA_DST_ART_DIR="$DST_ROOT/artifacts/ema_psar_raw_alpha"

"$PYTHON_BIN" "$ROOT/scripts/build_site_index.py"

sudo mkdir -p "$DST_ROOT" "$EMA_DST_PAGE_DIR" "$EMA_DST_ART_DIR"
sudo install -m 0644 "$ROOT/reports/site/index.html" "$DST_ROOT/index.html"
sudo install -m 0644 "$EMA_SRC_PAGE" "$EMA_DST_PAGE_DIR/report.html"
if [[ -d "$EMA_SRC_ART_DIR" ]]; then
  sudo rsync -a "$EMA_SRC_ART_DIR/" "$EMA_DST_ART_DIR/"
fi
sudo chown -R www-data:www-data "$DST_ROOT/index.html" "$EMA_DST_PAGE_DIR" "$EMA_DST_ART_DIR"

echo "[ok] published homepage + EMA paper page"
echo "[url] https://jp.jerrypsy.top/momentum/"
echo "[url] https://jp.jerrypsy.top/momentum/factors/ema_psar_raw_alpha/report.html"
