#!/usr/bin/env bash
set -euo pipefail

ROOT="/root/clawd/jerry/momentum"
DST="/var/www/momentum-report"
SITE_FACTOR_DIR="$ROOT/reports/site/factors/rank213_live_vs_backtest_checklist"
LIVE_ART_DIR="$ROOT/reports/artifacts/rank213_age90_live_canary_shell"
PAPER_ART_DIR="$ROOT/reports/artifacts/paper_rank213_age90_live"
PYTHON_BIN="python3"

if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT/.venv/bin/python"
fi

run_build() {
  local script_path="$1"
  "$PYTHON_BIN" "$script_path"
  echo "[ok] built $(basename "$script_path")"
}

run_build "$ROOT/scripts/build_rank213_live_vs_backtest_checklist.py"

mkdir -p "$DST/factors/rank213_live_vs_backtest_checklist"
rsync -a --delete "$SITE_FACTOR_DIR/" "$DST/factors/rank213_live_vs_backtest_checklist/"

mkdir -p "$DST/artifacts/rank213_age90_live_canary_shell"
rsync -a \
  "$LIVE_ART_DIR/live_vs_backtest_checklist.json" \
  "$LIVE_ART_DIR/live_vs_backtest_drift_attribution.csv" \
  "$LIVE_ART_DIR/live_vs_backtest_drift_summary.json" \
  "$LIVE_ART_DIR/live_status.json" \
  "$LIVE_ART_DIR/live_state.json" \
  "$LIVE_ART_DIR/live_exchange_positions.json" \
  "$LIVE_ART_DIR/rank213_archive_closeout_receipt.json" \
  "$DST/artifacts/rank213_age90_live_canary_shell/" 2>/dev/null || true

mkdir -p "$DST/artifacts/paper_rank213_age90_live"
rsync -a \
  "$PAPER_ART_DIR/rank213_age90_shadow_current_decision.json" \
  "$PAPER_ART_DIR/rank213_age90_shadow_status.json" \
  "$PAPER_ART_DIR/rank213_age90_shadow_recent_decisions.csv" \
  "$PAPER_ART_DIR/rank213_age90_signal_snapshot.json" \
  "$DST/artifacts/paper_rank213_age90_live/" 2>/dev/null || true

chown -R www-data:www-data \
  "$DST/factors/rank213_live_vs_backtest_checklist" \
  "$DST/artifacts/rank213_age90_live_canary_shell" \
  "$DST/artifacts/paper_rank213_age90_live"

echo "[ok] published rank213 checklist page -> $DST/factors/rank213_live_vs_backtest_checklist/report.html"
echo "[url] https://jp.jerrypsy.top/momentum/factors/rank213_live_vs_backtest_checklist/report.html"
echo "[url] https://jp.jerrypsy.top:24443/momentum/factors/rank213_live_vs_backtest_checklist/report.html"
