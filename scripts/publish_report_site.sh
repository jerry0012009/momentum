#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/reports/site"
ARTIFACTS_SRC="$ROOT/reports/artifacts"
DST="/var/www/momentum-report"

if [[ ! -d "$SRC" ]]; then
  echo "[error] site dir not found: $SRC" >&2
  exit 1
fi

PYTHON_BIN="python3"
if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT/.venv/bin/python"
fi

FAILED_BUILDS=()
SKIP_BUILDS="${OPENCLAW_PUBLISH_SKIP_BUILDS:-0}"
SKIP_ARTIFACTS="${OPENCLAW_PUBLISH_SKIP_ARTIFACTS:-0}"
SKIP_CHOWN="${OPENCLAW_PUBLISH_SKIP_CHOWN:-0}"

run_build() {
  local script_path="$1"
  if "$PYTHON_BIN" "$script_path"; then
    echo "[ok] built $(basename "$script_path")"
  else
    echo "[warn] build failed: $(basename "$script_path")" >&2
    FAILED_BUILDS+=("$(basename "$script_path")")
  fi
}

if [[ "$SKIP_BUILDS" == "1" ]]; then
  echo "[info] OPENCLAW_PUBLISH_SKIP_BUILDS=1 -> skipping site rebuilds and syncing existing reports/site"
else
  run_build "$ROOT/scripts/build_quant_digest_site.py"
  run_build "$ROOT/scripts/build_deep_dive_site.py"
  run_build "$ROOT/scripts/build_plans_site.py"
  run_build "$ROOT/scripts/build_trendline_alpha_scout_report.py"
  run_build "$ROOT/scripts/build_trendline_replication_briefs_report.py"
  run_build "$ROOT/scripts/build_alpha_closure_board_report.py"
  run_build "$ROOT/scripts/build_chan2022_paper_spec_report.py"
  run_build "$ROOT/scripts/build_chan_sr_feature_replication_report.py"
  run_build "$ROOT/scripts/build_pytrendline_event_validation_v2_report.py"
  run_build "$ROOT/scripts/build_trendline_confirmation_ladder_report.py"
  run_build "$ROOT/scripts/build_trendline_tracks_site.py"
  run_build "$ROOT/scripts/build_rank32b_canary_dashboard.py"
  run_build "$ROOT/scripts/build_rank32b_transparency_page.py"
  run_build "$ROOT/scripts/build_rank32b_decomposition_page.py"
  run_build "$ROOT/scripts/build_rank32b_exp12_decision_page.py"
  run_build "$ROOT/scripts/build_rank32b_global_live_like_stability.py"
  run_build "$ROOT/scripts/build_rank32b_strategy_portal.py"
  run_build "$ROOT/scripts/build_rank_strategy_hub.py"
  run_build "$ROOT/scripts/build_rank_p3_p2_full_registry_page.py"
  run_build "$ROOT/scripts/build_paper_runner_health_report.py"
  run_build "$ROOT/scripts/build_rank213_live_paper_reference.py"
  run_build "$ROOT/scripts/build_rank213_live_vs_backtest_checklist.py"
  run_build "$ROOT/scripts/build_rank213_archive_closeout_report.py"
  run_build "$ROOT/scripts/build_rank213_monthly_volume_segment_stability.py"
  run_build "$ROOT/scripts/build_rank213_monthly_volume_baseline_refresh.py"
  run_build "$ROOT/scripts/build_rank32c_live_dashboard.py"
  run_build "$ROOT/scripts/build_rank154_overview.py"
  run_build "$ROOT/scripts/build_rank154_archive_closeout_report.py"
  run_build "$ROOT/scripts/build_rank154_hub.py"
  run_build "$ROOT/scripts/build_rank154_admission_notes.py"
  run_build "$ROOT/scripts/build_rank154_carry_fix_report.py"
  run_build "$ROOT/scripts/build_rank154_validation_report.py"
  run_build "$ROOT/scripts/build_rank154_postmortem_report.py"
  run_build "$ROOT/scripts/build_v1_6a_report.py"
  run_build "$ROOT/scripts/build_rank450_strategy_directory.py"
  run_build "$ROOT/scripts/build_binance_event_study_hub.py"
  run_build "$ROOT/scripts/build_phase2_strategy_portal.py"
  run_build "$ROOT/scripts/build_site_index.py"
fi

mkdir -p "$DST"
rsync -a --delete "$SRC/" "$DST/"
mkdir -p "$DST/site"
rsync -a --delete --exclude 'site' "$SRC/" "$DST/site/"
if [[ "$SKIP_ARTIFACTS" == "1" ]]; then
  echo "[info] OPENCLAW_PUBLISH_SKIP_ARTIFACTS=1 -> skipping artifacts sync"
elif [[ -d "$ARTIFACTS_SRC" ]]; then
  mkdir -p "$DST/artifacts"
  rsync -a --delete "$ARTIFACTS_SRC/" "$DST/artifacts/"
fi
if [[ "$SKIP_CHOWN" == "1" ]]; then
  echo "[info] OPENCLAW_PUBLISH_SKIP_CHOWN=1 -> skipping recursive chown"
else
  chown -R www-data:www-data "$DST"
fi

echo "[ok] published -> $DST"
echo "[url] https://jp.jerrypsy.top/momentum/"
echo "[url] https://jp.jerrypsy.top:24443/momentum/"
if (( ${#FAILED_BUILDS[@]} > 0 )); then
  echo "[warn] partial publish; failed builds: ${FAILED_BUILDS[*]}" >&2
fi
