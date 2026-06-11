#!/usr/bin/env bash
set -euo pipefail

ROOT="/root/clawd/jerry/momentum"
SRC_SITE="$ROOT/reports/site/factors/rank32b_shadow_global_winner"
SRC_ART="$ROOT/reports/artifacts/rank32b_shadow_global_winner"

DST_ROOT="/var/www/momentum-report"
DST_SITE="$DST_ROOT/factors/rank32b_shadow_global_winner"
DST_ART="$DST_ROOT/artifacts/rank32b_shadow_global_winner"

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

chown -R www-data:www-data "$DST_SITE" || true
if [[ -d "$DST_ART" ]]; then
  chown -R www-data:www-data "$DST_ART" || true
fi

echo "[ok] published rank32b_shadow_global_winner -> $DST_SITE"
