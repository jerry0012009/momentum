#!/usr/bin/env bash
set -euo pipefail

ART_DIR="/root/clawd/jerry/momentum/reports/artifacts/rank32b_shadow_global_live_like_backtest"
LEDGER_DIR="$ART_DIR/trade_ledgers"
LOG_DIR="$ART_DIR/nohup_logs"
STATUS_JSON="$ART_DIR/long_backtests_watchdog_status.json"
WATCHDOG_LOG="$LOG_DIR/long_backtests_watchdog.log"

mkdir -p "$LOG_DIR"

find_pid() {
  local horizon="$1"
  pgrep -f "backtest_rank32b_global_shadow_live_like.py --horizon-days ${horizon}" | head -n 1 || true
}

is_alive() {
  local pid="$1"
  [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null
}

status_for_horizon() {
  local horizon="$1"
  local pid="$2"
  local trades_json="$LEDGER_DIR/paper_trades_${horizon}d.json"
  local monthly_json="$LEDGER_DIR/monthly_summary_${horizon}d.json"
  local running=false
  local state="missing"
  local trades_exists=false
  local monthly_exists=false

  if is_alive "$pid"; then
    running=true
    state="running"
  fi
  if [[ -f "$trades_json" ]]; then
    trades_exists=true
  fi
  if [[ -f "$monthly_json" ]]; then
    monthly_exists=true
  fi
  if [[ "$running" == false && "$trades_exists" == true && "$monthly_exists" == true ]]; then
    state="completed"
  elif [[ "$running" == false && ( "$trades_exists" == true || "$monthly_exists" == true ) ]]; then
    state="partial"
  elif [[ "$running" == false ]]; then
    state="failed_or_not_started"
  fi

  printf '{'
  printf '"pid": %s, ' "${pid:-null}"
  printf '"running": %s, ' "$running"
  printf '"state": "%s", ' "$state"
  printf '"paper_trades_json": "%s", ' "$trades_json"
  printf '"paper_trades_exists": %s, ' "$trades_exists"
  printf '"monthly_summary_json": "%s", ' "$monthly_json"
  printf '"monthly_summary_exists": %s' "$monthly_exists"
  printf '}'
}

while true; do
  ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  pid365="$(find_pid 365)"
  pid720="$(find_pid 720)"

  json365="$(status_for_horizon 365 "$pid365")"
  json720="$(status_for_horizon 720 "$pid720")"

  {
    printf '{\n'
    printf '  "updated_at_utc": "%s",\n' "$ts"
    printf '  "watchdog_log": "%s",\n' "$WATCHDOG_LOG"
    printf '  "h365": %s,\n' "$json365"
    printf '  "h720": %s\n' "$json720"
    printf '}\n'
  } > "$STATUS_JSON"

  echo "[$ts] h365 pid=${pid365:-none} h720 pid=${pid720:-none}" >> "$WATCHDOG_LOG"

  h365_done=false
  h720_done=false
  [[ -f "$LEDGER_DIR/paper_trades_365d.json" && -f "$LEDGER_DIR/monthly_summary_365d.json" ]] && h365_done=true
  [[ -f "$LEDGER_DIR/paper_trades_720d.json" && -f "$LEDGER_DIR/monthly_summary_720d.json" ]] && h720_done=true

  if [[ "$h365_done" == true && "$h720_done" == true ]] && ! is_alive "$pid365" && ! is_alive "$pid720"; then
    echo "[$ts] both long backtests completed" >> "$WATCHDOG_LOG"
    exit 0
  fi

  if [[ "$h365_done" == false ]] && ! is_alive "$pid365"; then
    echo "[$ts] warning: 365d process not alive and outputs incomplete" >> "$WATCHDOG_LOG"
  fi
  if [[ "$h720_done" == false ]] && ! is_alive "$pid720"; then
    echo "[$ts] warning: 720d process not alive and outputs incomplete" >> "$WATCHDOG_LOG"
  fi

  sleep 120
done
