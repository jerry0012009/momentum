#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_SITE="$ROOT/reports/site/interview_showcase"
SRC_ALIAS_SITE="$ROOT/reports/site/factor_research_library"
SRC_ART="$ROOT/reports/artifacts/interview_showcase"
SRC_ALIAS_ART="$ROOT/reports/artifacts/factor_research_library"
DST_ROOT="${MOMENTUM_REPORT_DST:-/var/www/momentum-report}"
DST_SITE="$DST_ROOT/interview_showcase"
DST_ALIAS_SITE="$DST_ROOT/factor_research_library"
DST_ART="$DST_ROOT/artifacts/interview_showcase"
DST_ALIAS_ART="$DST_ROOT/artifacts/factor_research_library"

PYTHON_BIN="python3"
if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT/.venv/bin/python"
fi

SKIP_BUILD="${OPENCLAW_SHOWCASE_SKIP_BUILD:-0}"
SKIP_CHOWN="${OPENCLAW_SHOWCASE_SKIP_CHOWN:-0}"

if [[ "$SKIP_BUILD" != "1" ]]; then
  "$PYTHON_BIN" "$ROOT/scripts/build_interview_showcase.py"
  "$PYTHON_BIN" "$ROOT/scripts/build_showcase_workflow_page.py"
  "$PYTHON_BIN" "$ROOT/scripts/build_rank151_paper_breakdown_page.py"
else
  echo "[info] OPENCLAW_SHOWCASE_SKIP_BUILD=1 -> syncing existing factor research library files"
fi

if [[ ! -d "$SRC_SITE" ]]; then
  echo "[error] factor research library site dir not found: $SRC_SITE" >&2
  exit 1
fi

mkdir -p "$DST_SITE"
rsync -a --delete "$SRC_SITE/" "$DST_SITE/"

if [[ -d "$SRC_ALIAS_SITE" ]]; then
  mkdir -p "$DST_ALIAS_SITE"
  rsync -a --delete "$SRC_ALIAS_SITE/" "$DST_ALIAS_SITE/"
fi

if [[ -d "$SRC_ART" ]]; then
  mkdir -p "$DST_ART"
  rsync -a --delete "$SRC_ART/" "$DST_ART/"
fi

if [[ -d "$SRC_ALIAS_ART" ]]; then
  mkdir -p "$DST_ALIAS_ART"
  rsync -a --delete "$SRC_ALIAS_ART/" "$DST_ALIAS_ART/"
fi

if [[ "$SKIP_CHOWN" != "1" ]]; then
  if command -v chown >/dev/null 2>&1; then
    chown -R www-data:www-data "$DST_SITE" "$DST_ART" "$DST_ALIAS_ART" 2>/dev/null || true
  fi
fi

echo "[ok] published factor research library -> $DST_SITE"
if [[ -d "$SRC_ALIAS_SITE" ]]; then
  echo "[ok] published factor research library alias -> $DST_ALIAS_SITE"
fi
echo "[ok] published factor research artifacts -> $DST_ART"
if [[ -d "$SRC_ALIAS_ART" ]]; then
  echo "[ok] published factor research artifact alias -> $DST_ALIAS_ART"
fi
echo "[url] https://jp.jerrypsy.top/momentum/interview_showcase/"
echo "[url] https://jp.jerrypsy.top/momentum/factor_research_library/"
echo "[url] https://jp.jerrypsy.top:24443/momentum/interview_showcase/"
echo "[url] https://jp.jerrypsy.top:24443/momentum/factor_research_library/"
