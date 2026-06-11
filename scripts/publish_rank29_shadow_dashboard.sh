#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="python3"
if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT/.venv/bin/python"
fi

"$PYTHON_BIN" "$ROOT/scripts/build_manual_narrow_paper_lanes_report.py"
"$PYTHON_BIN" "$ROOT/scripts/build_rank29_trendline_breakout_clean_replication.py"
"$PYTHON_BIN" "$ROOT/scripts/build_rank29_shadow_dashboard.py"
"$PYTHON_BIN" "$ROOT/scripts/build_rank29_gate_live_dashboard.py"
"$PYTHON_BIN" "$ROOT/scripts/build_rank29_monitoring_hub.py"
"$PYTHON_BIN" "$ROOT/scripts/build_live_trading_center.py"

DST_ROOT="/var/www/momentum-report"
DST_DASH_DIR="$DST_ROOT/factors/rank29_shadow_dashboard"
DST_MANUAL_DIR="$DST_ROOT/factors/manual_narrow_paper_lanes"
DST_MAIN_DIR="$DST_ROOT/factors/scout_rank29_trendline_breakout_navigator_15m"
DST_HUB_DIR="$DST_ROOT/factors/rank29_monitoring_hub"
DST_LIVE_DIR="$DST_ROOT/factors/rank29_gate_live"
DST_OPS_DIR="$DST_ROOT/factors/live_trading_center"
DST_ART_DIR="$DST_ROOT/artifacts/manual_narrow_paper_lanes"
DST_LIVE_ART_DIR="$DST_ROOT/artifacts/rank29_gate_live"

SRC_DASH="$ROOT/reports/site/factors/rank29_shadow_dashboard/report.html"
SRC_MANUAL="$ROOT/reports/site/factors/manual_narrow_paper_lanes/report.html"
SRC_MAIN="$ROOT/reports/site/factors/scout_rank29_trendline_breakout_navigator_15m/report.html"
SRC_HUB="$ROOT/reports/site/factors/rank29_monitoring_hub/report.html"
SRC_LIVE="$ROOT/reports/site/factors/rank29_gate_live/report.html"
SRC_OPS="$ROOT/reports/site/factors/live_trading_center/report.html"
SRC_ART_DIR="$ROOT/reports/artifacts/manual_narrow_paper_lanes"
SRC_LIVE_ART_DIR="$ROOT/reports/artifacts/rank29_gate_live"

sudo mkdir -p "$DST_DASH_DIR" "$DST_MANUAL_DIR" "$DST_MAIN_DIR" "$DST_HUB_DIR" "$DST_LIVE_DIR" "$DST_OPS_DIR" "$DST_ART_DIR" "$DST_LIVE_ART_DIR"
sudo install -m 0644 "$SRC_DASH" "$DST_DASH_DIR/report.html"
sudo install -m 0644 "$SRC_MANUAL" "$DST_MANUAL_DIR/report.html"
sudo install -m 0644 "$SRC_MAIN" "$DST_MAIN_DIR/report.html"
sudo install -m 0644 "$SRC_HUB" "$DST_HUB_DIR/report.html"
sudo install -m 0644 "$SRC_LIVE" "$DST_LIVE_DIR/report.html"
sudo install -m 0644 "$SRC_OPS" "$DST_OPS_DIR/report.html"
if [[ -d "$SRC_ART_DIR" ]]; then
  sudo rsync -a "$SRC_ART_DIR/" "$DST_ART_DIR/"
fi
if [[ -d "$SRC_LIVE_ART_DIR" ]]; then
  sudo rsync -a "$SRC_LIVE_ART_DIR/" "$DST_LIVE_ART_DIR/"
fi
sudo chown -R www-data:www-data "$DST_DASH_DIR" "$DST_MANUAL_DIR" "$DST_MAIN_DIR" "$DST_HUB_DIR" "$DST_LIVE_DIR" "$DST_OPS_DIR" "$DST_ART_DIR" "$DST_LIVE_ART_DIR"

echo "[ok] published -> $DST_DASH_DIR/report.html"
echo "[ok] published -> $DST_HUB_DIR/report.html"
echo "[ok] published -> $DST_LIVE_DIR/report.html"
echo "[ok] published -> $DST_OPS_DIR/report.html"
echo "[url] https://jp.jerrypsy.top/momentum/factors/rank29_shadow_dashboard/report.html"
echo "[url] https://jp.jerrypsy.top/momentum/factors/rank29_monitoring_hub/report.html"
echo "[url] https://jp.jerrypsy.top/momentum/factors/rank29_gate_live/report.html"
echo "[url] https://jp.jerrypsy.top/momentum/factors/live_trading_center/report.html"
