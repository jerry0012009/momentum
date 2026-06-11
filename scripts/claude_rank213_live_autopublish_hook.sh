#!/usr/bin/env bash
set -euo pipefail

ROOT="/root/clawd/jerry/momentum"
SUMMARY_PATH="$ROOT/reports/artifacts/rank213_live_canary_shell/live_last_run_summary.json"
STAMP_PATH="$ROOT/tmp/rank213_live_autopublish_last_generated_at.txt"
PUBLISH_SCRIPT="$ROOT/scripts/publish_rank213_live_checklist_page.sh"
STAMP_DIR="$ROOT/tmp"
WAIT_SECONDS=180
SLEEP_SECONDS=2

payload="$(cat)"
[[ -n "$payload" ]] || exit 0
command -v jq >/dev/null 2>&1 || exit 0

tool_name="$(printf '%s' "$payload" | jq -r '.tool_name // ""')"
cmd="$(printf '%s' "$payload" | jq -r '.tool_input.command // ""')"
[[ "$tool_name" == "Bash" ]] || exit 0

matches_live_trigger=0
needs_wait=0
case "$cmd" in
  *run_rank213_largecap_xs_jump_veto_live_canary.py*)
    matches_live_trigger=1
    ;;
  *momentum-rank213-live-canary-shell.service*)
    matches_live_trigger=1
    needs_wait=1
    ;;
esac
[[ "$matches_live_trigger" == "1" ]] || exit 0

read_summary_field() {
  local field="$1"
  [[ -f "$SUMMARY_PATH" ]] || return 1
  jq -r "$field // \"\"" "$SUMMARY_PATH"
}

mkdir -p "$STAMP_DIR"

last_published=""
if [[ -f "$STAMP_PATH" ]]; then
  last_published="$(tr -d '\n' < "$STAMP_PATH")"
fi

current_generated_at="$(read_summary_field '.generated_at_utc' || true)"
if [[ "$needs_wait" == "1" ]]; then
  waited=0
  while [[ $waited -lt $WAIT_SECONDS ]]; do
    current_generated_at="$(read_summary_field '.generated_at_utc' || true)"
    if [[ -n "$current_generated_at" && "$current_generated_at" != "$last_published" ]]; then
      break
    fi
    sleep "$SLEEP_SECONDS"
    waited=$((waited + SLEEP_SECONDS))
  done
fi

[[ -n "$current_generated_at" ]] || exit 0
[[ "$current_generated_at" != "$last_published" ]] || exit 0

runner="$(read_summary_field '.runner' || true)"

[[ "$runner" == "rank213_live_canary_shell" ]] || exit 0

"$PUBLISH_SCRIPT"
printf '%s\n' "$current_generated_at" > "$STAMP_PATH"
