#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://127.0.0.1:8099}"
SESSION="ops-smoke-$$"
SERVER_PID=""
LOG_FILE="/tmp/ops-mobile-smoke-$$.log"

cleanup() {
  if [[ -n "$SERVER_PID" ]]; then
    kill "$SERVER_PID" >/dev/null 2>&1 || true
  fi
  tmux kill-session -t "$SESSION" >/dev/null 2>&1 || true
}
trap cleanup EXIT

start_server_if_needed() {
  if curl -fsS "$BASE_URL/api.php?session=webcli&state=1" >/dev/null 2>&1; then
    return
  fi
  php -S 127.0.0.1:8099 -t /var/www/html/ops >"$LOG_FILE" 2>&1 &
  SERVER_PID=$!
  BASE_URL="http://127.0.0.1:8099"
  sleep 1
}

json_field() {
  local key="$1"
  python3 -c 'import json,sys; key=sys.argv[1]; data=json.load(sys.stdin); value=data.get(key); print("true" if value is True else "false" if value is False else "" if value is None else value)' "$key"
}

api_post() {
  local action="$1"
  curl -fsS -X POST "${BASE_URL}/api.php?session=${SESSION}" \
    -H 'Content-Type: application/json' \
    --data "{\"action\":\"${action}\",\"session\":\"${SESSION}\"}"
}

api_post_raw() {
  local json="$1"
  curl -fsS -X POST "${BASE_URL}/api.php?session=${SESSION}" \
    -H 'Content-Type: application/json' \
    --data "$json"
}

api_get_state() {
  curl -fsS "${BASE_URL}/api.php?session=${SESSION}&state=1"
}

assert_eq() {
  local got="$1"
  local expect="$2"
  local msg="$3"
  if [[ "$got" != "$expect" ]]; then
    echo "[FAIL] $msg | expect=$expect got=$got" >&2
    exit 1
  fi
  echo "[OK] $msg => $got"
}

assert_ne() {
  local got="$1"
  local other="$2"
  local msg="$3"
  if [[ "$got" == "$other" ]]; then
    echo "[FAIL] $msg | both=$got" >&2
    exit 1
  fi
  echo "[OK] $msg => $got"
}

assert_contains() {
  local haystack="$1"
  local needle="$2"
  local msg="$3"
  if [[ "$haystack" != *"$needle"* ]]; then
    echo "[FAIL] $msg | missing '$needle'" >&2
    echo "--- content ---" >&2
    echo "$haystack" >&2
    exit 1
  fi
  echo "[OK] $msg"
}

assert_window_status() {
  local json="$1"
  local window_name="$2"
  local expected_status="$3"
  local msg="$4"
  printf '%s' "$json" | python3 -c '
import json
import sys

window_name, expected_status, msg = sys.argv[1:4]
data = json.load(sys.stdin)
for window in data.get("windows", []):
    if window.get("name") == window_name:
        got = window.get("status")
        if got != expected_status:
            print(f"[FAIL] {msg} | expect={expected_status} got={got}", file=sys.stderr)
            sys.exit(1)
        for key in ("statusLabel", "statusIcon", "statusClass", "currentCommand", "panes"):
            if key not in window:
                print(f"[FAIL] {msg} | missing {key}", file=sys.stderr)
                sys.exit(1)
        print(f"[OK] {msg} => {got}")
        sys.exit(0)
print(f"[FAIL] {msg} | window not found: {window_name}", file=sys.stderr)
sys.exit(1)
' "$window_name" "$expected_status" "$msg"
}

assert_current_status() {
  local json="$1"
  local expected_status="$2"
  local msg="$3"
  printf '%s' "$json" | python3 -c '
import json
import sys

expected_status, msg = sys.argv[1:3]
data = json.load(sys.stdin)
got = (data.get("currentWindow") or {}).get("status")
if got != expected_status:
    print(f"[FAIL] {msg} | expect={expected_status} got={got}", file=sys.stderr)
    sys.exit(1)
print(f"[OK] {msg} => {got}")
' "$expected_status" "$msg"
}

start_server_if_needed

echo "== create session $SESSION =="
tmux new-session -d -s "$SESSION" -n main 'cat -v'
tmux resize-window -t "$SESSION":0 -x 220 -y 70
tmux split-window -h -t "$SESSION":0 'bash'
tmux new-window -t "$SESSION" -n second 'bash'
tmux resize-window -t "$SESSION":1 -x 220 -y 70
tmux new-window -t "$SESSION" -n runner 'sleep 60'
tmux new-window -t "$SESSION" -n approval 'sh -lc "printf \"Approval required [y/N]\\n\"; sleep 60"'
tmux select-window -t "$SESSION":0

cat_pane=$(tmux list-panes -t "$SESSION":0 -F '#{pane_id} #{pane_current_command}' | awk '$2=="cat"{print $1; exit}')
if [[ -z "$cat_pane" ]]; then
  echo "[FAIL] cat pane not found" >&2
  exit 1
fi

echo "== basic state =="
state_json=$(api_get_state)
assert_eq "$(printf '%s' "$state_json" | json_field ok)" "true" "state endpoint ok"
assert_eq "$(printf '%s' "$state_json" | json_field session)" "$SESSION" "state endpoint session"
window_snapshot_count=$(printf '%s' "$state_json" | python3 -c 'import json,sys; print(len(json.load(sys.stdin).get("windows", [])))')
if [[ "$window_snapshot_count" -lt 4 ]]; then
  echo "[FAIL] snapshot includes created windows | got=$window_snapshot_count" >&2
  exit 1
fi
echo "[OK] snapshot includes created windows => $window_snapshot_count"
assert_window_status "$state_json" "runner" "running" "window tab marks running command"
assert_window_status "$state_json" "approval" "needs_approval" "window tab marks approval prompt"

resp=$(api_post_raw "{\"action\":\"window_focus\",\"session\":\"${SESSION}\",\"window\":\"1\"}")
assert_eq "$(printf '%s' "$resp" | json_field ok)" "true" "window_focus to #1 ok"
focused=$(tmux display-message -p -t "$SESSION" '#{window_index}')
assert_eq "$focused" "1" "window_focus actually switched"
resp=$(api_post_raw "{\"action\":\"window_focus\",\"session\":\"${SESSION}\",\"window\":\"0\"}")
assert_eq "$(printf '%s' "$resp" | json_field ok)" "true" "window_focus back to #0 ok"

echo "== pane navigation =="
pane_before=$(tmux display-message -p -t "$SESSION":0 '#{pane_index}')
resp=$(api_post pane_next)
assert_eq "$(printf '%s' "$resp" | json_field ok)" "true" "pane_next ok"
pane_after=$(tmux display-message -p -t "$SESSION":0 '#{pane_index}')
assert_ne "$pane_after" "$pane_before" "pane_next changed pane"

resp=$(api_post pane_left)
assert_eq "$(printf '%s' "$resp" | json_field ok)" "true" "pane_left ok"
resp=$(api_post pane_right)
assert_eq "$(printf '%s' "$resp" | json_field ok)" "true" "pane_right ok"
resp=$(api_post pane_up)
assert_eq "$(printf '%s' "$resp" | json_field ok)" "true" "pane_up ok"
resp=$(api_post pane_down)
assert_eq "$(printf '%s' "$resp" | json_field ok)" "true" "pane_down ok"

zoom_before=$(tmux display-message -p -t "$SESSION":0 '#{window_zoomed_flag}')
resp=$(api_post pane_zoom)
assert_eq "$(printf '%s' "$resp" | json_field ok)" "true" "pane_zoom first ok"
zoom_mid=$(tmux display-message -p -t "$SESSION":0 '#{window_zoomed_flag}')
assert_ne "$zoom_mid" "$zoom_before" "pane_zoom toggled on"
resp=$(api_post pane_zoom)
assert_eq "$(printf '%s' "$resp" | json_field ok)" "true" "pane_zoom second ok"
zoom_after=$(tmux display-message -p -t "$SESSION":0 '#{window_zoomed_flag}')
assert_eq "$zoom_after" "$zoom_before" "pane_zoom toggled back"

echo "== window navigation =="
window_before=$(tmux display-message -p -t "$SESSION" '#{window_index}')
resp=$(api_post window_next)
assert_eq "$(printf '%s' "$resp" | json_field ok)" "true" "window_next ok"
window_next=$(tmux display-message -p -t "$SESSION" '#{window_index}')
assert_ne "$window_next" "$window_before" "window_next changed window"
resp=$(api_post window_prev)
assert_eq "$(printf '%s' "$resp" | json_field ok)" "true" "window_prev ok"
window_back=$(tmux display-message -p -t "$SESSION" '#{window_index}')
assert_eq "$window_back" "$window_before" "window_prev returned"
count_before=$(tmux list-windows -t "$SESSION" | wc -l | tr -d ' ')
resp=$(api_post window_new)
assert_eq "$(printf '%s' "$resp" | json_field ok)" "true" "window_new ok"
count_after=$(tmux list-windows -t "$SESSION" | wc -l | tr -d ' ')
assert_eq "$count_after" "$((count_before + 1))" "window_new increased count"

echo "== split and layouts =="
tmux select-window -t "$SESSION":0
pane_count_before=$(tmux list-panes -t "$SESSION":0 | wc -l | tr -d ' ')
resp=$(api_post split_h)
assert_eq "$(printf '%s' "$resp" | json_field ok)" "true" "split_h ok"
pane_count_h=$(tmux list-panes -t "$SESSION":0 | wc -l | tr -d ' ')
assert_eq "$pane_count_h" "$((pane_count_before + 1))" "split_h increased pane count"
resp=$(api_post split_v)
assert_eq "$(printf '%s' "$resp" | json_field ok)" "true" "split_v ok"
pane_count_v=$(tmux list-panes -t "$SESSION":0 | wc -l | tr -d ' ')
assert_eq "$pane_count_v" "$((pane_count_h + 1))" "split_v increased pane count"
resp=$(api_post layout_tiled)
assert_eq "$(printf '%s' "$resp" | json_field ok)" "true" "layout_tiled ok"
resp=$(api_post layout_even_h)
assert_eq "$(printf '%s' "$resp" | json_field ok)" "true" "layout_even_h ok"
resp=$(api_post layout_even_v)
assert_eq "$(printf '%s' "$resp" | json_field ok)" "true" "layout_even_v ok"

echo "== copy mode / paging =="
tmux select-pane -t "$cat_pane"
scroll_seed_payload=$(python3 - <<PY
import json
text = "\n".join(f"scroll-seed-{i:03d}" for i in range(1, 260))
print(json.dumps({
  "action": "send_text",
  "session": "$SESSION",
  "text": text
}, ensure_ascii=False))
PY
)
resp=$(api_post_raw "$scroll_seed_payload")
assert_eq "$(printf '%s' "$resp" | json_field ok)" "true" "scroll seed send_text ok"
sleep 0.3
history_size=$(tmux display-message -p -t "$cat_pane" '#{history_size}')
if [[ "$history_size" -le 0 ]]; then
  echo "[FAIL] copy mode seed did not create history | history_size=$history_size" >&2
  exit 1
fi
echo "[OK] copy mode seed created history => $history_size"
resp=$(api_post scroll_up)
assert_eq "$(printf '%s' "$resp" | json_field ok)" "true" "scroll_up auto-enter ok"
assert_eq "$(tmux display-message -p -t "$cat_pane" '#{pane_in_mode}')" "1" "scroll_up auto-entered copy_mode"
scroll_auto=$(tmux display-message -p -t "$cat_pane" '#{scroll_position}')
if [[ "$scroll_auto" -le 0 ]]; then
  echo "[FAIL] scroll_up did not move into history | scroll=$scroll_auto" >&2
  exit 1
fi
echo "[OK] scroll_up moved into history => $scroll_auto"
resp=$(api_post scroll_up)
assert_eq "$(printf '%s' "$resp" | json_field ok)" "true" "scroll_up in copy_mode ok"
scroll_up_more=$(tmux display-message -p -t "$cat_pane" '#{scroll_position}')
if [[ "$scroll_up_more" -le "$scroll_auto" ]]; then
  echo "[FAIL] scroll_up did not increase scroll position | before=$scroll_auto after=$scroll_up_more" >&2
  exit 1
fi
echo "[OK] scroll_up increased scroll position => $scroll_up_more"
resp=$(api_post scroll_down)
assert_eq "$(printf '%s' "$resp" | json_field ok)" "true" "scroll_down in copy_mode ok"
scroll_down_less=$(tmux display-message -p -t "$cat_pane" '#{scroll_position}')
if [[ "$scroll_down_less" -ge "$scroll_up_more" ]]; then
  echo "[FAIL] scroll_down did not reduce scroll position | before=$scroll_up_more after=$scroll_down_less" >&2
  exit 1
fi
echo "[OK] scroll_down reduced scroll position => $scroll_down_less"
resp=$(api_post copy_mode_exit)
assert_eq "$(printf '%s' "$resp" | json_field ok)" "true" "copy_mode_exit after wheel ok"
assert_eq "$(tmux display-message -p -t "$cat_pane" '#{pane_in_mode}')" "0" "copy_mode exited after wheel"
resp=$(api_post copy_mode)
assert_eq "$(printf '%s' "$resp" | json_field ok)" "true" "copy_mode ok"
assert_eq "$(tmux display-message -p -t "$cat_pane" '#{pane_in_mode}')" "1" "copy_mode entered"
assert_current_status "$resp" "paused" "current tab marks copy mode paused"
resp=$(api_post page_up)
assert_eq "$(printf '%s' "$resp" | json_field ok)" "true" "page_up ok"
resp=$(api_post page_down)
assert_eq "$(printf '%s' "$resp" | json_field ok)" "true" "page_down ok"
resp=$(api_post copy_mode_exit)
assert_eq "$(printf '%s' "$resp" | json_field ok)" "true" "copy_mode_exit ok"
assert_eq "$(tmux display-message -p -t "$cat_pane" '#{pane_in_mode}')" "0" "copy_mode exited"

echo "== paste send =="
tmux select-pane -t "$cat_pane"
paste_payload=$(python3 - <<PY
import json
print(json.dumps({
  "action": "send_text",
  "session": "$SESSION",
  "text": "hello from paste\\nsecond line 中文"
}, ensure_ascii=False))
PY
)
resp=$(api_post_raw "$paste_payload")
assert_eq "$(printf '%s' "$resp" | json_field ok)" "true" "send_text ok"
sleep 0.3
pane_capture=$(tmux capture-pane -p -t "$cat_pane" -S -20)
assert_contains "$pane_capture" "hello from paste" "send_text inserted first line"
assert_contains "$pane_capture" "second line 中文" "send_text inserted second line"

echo "== android-missing keys =="
tmux kill-pane -t "$cat_pane" >/dev/null 2>&1 || true
tmux split-window -t "$SESSION":0 'sh -lc "stty raw -echo; cat -v"'
raw_pane=$(tmux display-message -p -t "$SESSION":0 '#{pane_id}')
tmux select-pane -t "$raw_pane"
for action in arrow_up arrow_down arrow_left arrow_right home end backspace delete ctrl_a ctrl_b ctrl_e ctrl_l ctrl_r ctrl_u ctrl_k ctrl_w ctrl_z; do
  resp=$(api_post "$action")
  assert_eq "$(printf '%s' "$resp" | json_field ok)" "true" "$action ok"
done
sleep 0.3
raw_capture=$(tmux capture-pane -p -t "$raw_pane" -S -20)
assert_contains "$raw_capture" '^[[A' "arrow_up emitted escape sequence"
assert_contains "$raw_capture" '^[[B' "arrow_down emitted escape sequence"
assert_contains "$raw_capture" '^[[D' "arrow_left emitted escape sequence"
assert_contains "$raw_capture" '^[[C' "arrow_right emitted escape sequence"
assert_contains "$raw_capture" '^[[1~' "home emitted escape sequence"
assert_contains "$raw_capture" '^[[4~' "end emitted escape sequence"
assert_contains "$raw_capture" '^?' "backspace emitted delete char"
assert_contains "$raw_capture" '^[[3~' "delete emitted escape sequence"
assert_contains "$raw_capture" '^A' "ctrl_a emitted control char"
assert_contains "$raw_capture" '^B' "ctrl_b emitted control char"
assert_contains "$raw_capture" '^E' "ctrl_e emitted control char"
assert_contains "$raw_capture" '^L' "ctrl_l emitted control char"
assert_contains "$raw_capture" '^R' "ctrl_r emitted control char"
assert_contains "$raw_capture" '^U' "ctrl_u emitted control char"
assert_contains "$raw_capture" '^K' "ctrl_k emitted control char"
assert_contains "$raw_capture" '^W' "ctrl_w emitted control char"
assert_contains "$raw_capture" '^Z' "ctrl_z emitted control char"

echo "== key sends =="
resp=$(api_post tab)
assert_eq "$(printf '%s' "$resp" | json_field ok)" "true" "tab ok"
resp=$(api_post escape)
assert_eq "$(printf '%s' "$resp" | json_field ok)" "true" "escape ok"
resp=$(api_post enter)
assert_eq "$(printf '%s' "$resp" | json_field ok)" "true" "enter ok"
resp=$(api_post ctrl_c)
assert_eq "$(printf '%s' "$resp" | json_field ok)" "true" "ctrl_c ok"
sleep 0.3
ctrl_c_command=$(tmux display-message -p -t "$raw_pane" '#{pane_current_command}')
if [[ "$ctrl_c_command" == "cat" ]]; then
  echo "[FAIL] ctrl_c did not interrupt raw cat pane" >&2
  exit 1
fi
echo "[OK] ctrl_c interrupted raw cat pane => ${ctrl_c_command:-<pane-exited>}"

echo "== RESULT =="
echo "All API smoke tests passed for $SESSION via $BASE_URL"
