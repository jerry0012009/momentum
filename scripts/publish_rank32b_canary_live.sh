#!/usr/bin/env bash
set -euo pipefail

ROOT="/root/clawd/jerry/momentum"
python3 "$ROOT/scripts/build_live_trading_center.py"

SRC_SITE="$ROOT/reports/site/factors/rank32b_canary"
SRC_ART="$ROOT/reports/artifacts/rank32b_canary"
SRC_GLOBAL_LIVE_SITE="$ROOT/reports/site/factors/rank32b_global_live"
SRC_GLOBAL_LIVE_ART="$ROOT/reports/artifacts/rank32b_global_live"
SRC_OPS_SITE="$ROOT/reports/site/factors/live_trading_center"

DST_ROOT="/var/www/momentum-report"
DST_SITE="$DST_ROOT/factors/rank32b_canary"
DST_ART="$DST_ROOT/artifacts/rank32b_canary"
DST_GLOBAL_LIVE_SITE="$DST_ROOT/factors/rank32b_global_live"
DST_GLOBAL_LIVE_ART="$DST_ROOT/artifacts/rank32b_global_live"
DST_OPS_SITE="$DST_ROOT/factors/live_trading_center"

if [[ ! -d "$SRC_SITE" ]]; then
  echo "[error] src site dir not found: $SRC_SITE" >&2
  exit 1
fi

mkdir -p "$DST_SITE"
rsync -a --delete "$SRC_SITE/" "$DST_SITE/"

if [[ -d "$SRC_ART" ]]; then
  mkdir -p "$DST_ART"
  rsync -a --delete "$SRC_ART/" "$DST_ART/"
fi

if [[ -d "$SRC_GLOBAL_LIVE_SITE" ]]; then
  mkdir -p "$DST_GLOBAL_LIVE_SITE"
  rsync -a --delete "$SRC_GLOBAL_LIVE_SITE/" "$DST_GLOBAL_LIVE_SITE/"
fi

if [[ -d "$SRC_OPS_SITE" ]]; then
  mkdir -p "$DST_OPS_SITE"
  rsync -a --delete "$SRC_OPS_SITE/" "$DST_OPS_SITE/"
fi

if [[ -d "$SRC_GLOBAL_LIVE_ART" ]]; then
  mkdir -p "$DST_GLOBAL_LIVE_ART"
  rsync -a --delete "$SRC_GLOBAL_LIVE_ART/" "$DST_GLOBAL_LIVE_ART/"
fi

chown -R www-data:www-data "$DST_SITE" || true
if [[ -d "$DST_ART" ]]; then
  chown -R www-data:www-data "$DST_ART" || true
fi
if [[ -d "$DST_GLOBAL_LIVE_SITE" ]]; then
  chown -R www-data:www-data "$DST_GLOBAL_LIVE_SITE" || true
fi
if [[ -d "$DST_OPS_SITE" ]]; then
  chown -R www-data:www-data "$DST_OPS_SITE" || true
fi
if [[ -d "$DST_GLOBAL_LIVE_ART" ]]; then
  chown -R www-data:www-data "$DST_GLOBAL_LIVE_ART" || true
fi

echo "[ok] published rank32b_canary -> $DST_SITE"
echo "[ok] published rank32b_global_live -> $DST_GLOBAL_LIVE_SITE"
echo "[ok] published live_trading_center -> $DST_OPS_SITE"
