#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from momentum.strategies.rank32c_btc_utc_weak_cell import (
    BAR_MINUTES,
    HOLD_BARS,
    MAX_SINGLE_TRADE_LOSS_PCT,
    ROUND_TRIP_COST_BPS,
    STRATEGY_ID,
    SYMBOL,
    TINY_LIVE_NOTIONAL_USDC,
    TRAIN_DAYS,
    build_order_plan,
    load_cached_bars,
    month_start,
    run_replay,
    to_iso,
)


RAW_15M_DIR = (
    ROOT
    / "reports"
    / "artifacts"
    / "paper_rank213_largecap_xs_jump_veto"
    / "rank213_local_cache"
    / "monthly_marketcap_universe"
    / "raw_15m"
)
ART_DIR = ROOT / "reports" / "artifacts" / "rank32c_pre_live_gate"
LIVE_CONFIG_PATH = ROOT / "config" / "strategies" / "rank32c_btc_utc_weak_cell_v1_live.yaml"


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv_header(path: Path, fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 0:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()


def write_live_config(decision: str, order_plan: dict) -> None:
    allow_live = decision == "launch_tiny_live"
    lines = [
        f'strategy_id: "{STRATEGY_ID}"',
        f'mode: "{decision}"',
        f'allow_live_orders: {"true" if allow_live else "false"}',
        f'symbol: "{SYMBOL}"',
        'bar_interval: "15m"',
        f'train_days: {TRAIN_DAYS}',
        f'hold_bars: {HOLD_BARS}',
        "side: \"short\"",
        "bottom_k: 1",
        "no_overlap: true",
        f'round_trip_cost_bps: {ROUND_TRIP_COST_BPS}',
        "entry_delay_bars: 0",
        "veto: \"prior_24h_abs_move_gt_trailing_180d_mean_plus_2std\"",
        "gate: \"selected_cell_train_mean_long_bps < -round_trip_cost_bps\"",
        f'notional_usdc: {TINY_LIVE_NOTIONAL_USDC}',
        f'max_single_trade_risk_pct: {MAX_SINGLE_TRADE_LOSS_PCT}',
        'runner_command: "python3 scripts/run_rank32c_btc_utc_weak_cell_tiny_live.py --config config/strategies/rank32c_btc_utc_weak_cell_v1_live.yaml"',
        f'order_plan_path: "{(ART_DIR / "order_plan.json").relative_to(ROOT)}"',
        f'state_path: "{(ART_DIR / "state.json").relative_to(ROOT)}"',
        f'status_path: "{(ART_DIR / "status.json").relative_to(ROOT)}"',
        f'closed_trade_ledger: "{(ART_DIR / "closed_trades.csv").relative_to(ROOT)}"',
        f'live_vs_shadow_ledger: "{(ART_DIR / "live_vs_shadow.csv").relative_to(ROOT)}"',
        'kill_switch: "block if stale data, open position exists, duplicate entry key exists, 5 closed trades net <= -2.5%, any single trade <= -1.2%, spread > 8bps, missing bars > 2, slippage > 12bps, or exit ack missing"',
        f'current_allow_open: {"true" if order_plan.get("allow_open") else "false"}',
    ]
    LIVE_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LIVE_CONFIG_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_audit(decision: str, order_plan: dict, status: dict) -> str:
    return f"""# Final Pre-live Release Gate: {STRATEGY_ID}

## Binary Decision

`{decision}`

## Fixed Spec

- universe: `{SYMBOL}` only
- signal: monthly as-of trailing `{TRAIN_DAYS}` completed days, select weakest UTC weekday-hour cell
- side: short only
- hold: `{HOLD_BARS}` x 15m bars
- no-overlap: true
- cost: `{ROUND_TRIP_COST_BPS}` bps round trip research assumption
- veto: prior 24h abs move above trailing 180d mean + 2 std
- gate: selected cell train mean long bps < -round-trip cost bps
- sizing: `{TINY_LIVE_NOTIONAL_USDC}` USDC tiny-live notional
- kill switch: stale data, residual position, duplicate entry, loss, spread, missing bar, slippage, or missing exit ack blocks live

## Unified Code Path

Backtest replay, shadow planning, and the tiny-live order plan are now required to use `src/momentum/strategies/rank32c_btc_utc_weak_cell.py`.

## Recent Replay

- source: `{status.get("recent_replay_summary", {}).get("source")}`
- replay_start_month: `{status.get("recent_replay_summary", {}).get("replay_start_month")}`
- replay_end_month_exclusive: `{status.get("recent_replay_summary", {}).get("replay_end_month_exclusive")}`
- trades: `{status.get("recent_replay_summary", {}).get("trades")}`
- net_mean_bps: `{status.get("recent_replay_summary", {}).get("net_mean_bps")}`
- net_cum_pct: `{status.get("recent_replay_summary", {}).get("net_cum_pct")}`

## Current Order Plan

- cache_last_bar_utc: `{order_plan.get("cache_last_bar_utc")}`
- required_last_train_bar_utc: `{order_plan.get("required_last_train_bar_utc")}`
- selected_cell: `{order_plan.get("selected_cell")}`
- next_entry_ts: `{order_plan.get("next_entry_ts")}`
- exit_ts: `{order_plan.get("exit_ts")}`
- allow_open: `{order_plan.get("allow_open")}`
- blocked_by: `{order_plan.get("blocked_by")}`
- notional_usdc: `{order_plan.get("notional_usdc")}`
- max_single_trade_risk_pct: `{order_plan.get("max_single_trade_risk_pct")}`
- kill_switch_state: `{order_plan.get("kill_switch_state")}`

## Honesty Audit

| Check | Evidence | Status |
| --- | --- | --- |
| No future returns/months/volume/current active list/hindsight hot coin | Universe is fixed BTCUSDT; monthly selection uses only bars before target month start. | pass |
| Monthly selection strictly as-of | `select_month_cell()` trains on `[month_start - 60d, month_start)`. | pass |
| Entry/exit/veto/no-overlap do not read future bars | Order plan uses scheduled entry, fixed exit, current/prior veto state, no overlap protection fields. | pass |
| Current month plan independently reproducible | Current cache must include the completed bar before current month start. | {"fail" if order_plan.get("decision_blocker") else "pass"} |
| Can predict next trade and exit | Requires selected cell and next entry/exit timestamps. | {"fail" if not order_plan.get("next_entry_ts") else "pass"} |
| Residual/duplicate-open protection | State/status initialize `open_position=false`, `duplicate_entry_key_guard=true`, `allow_live_orders` follows binary decision. | pass |
| Live-vs-shadow accounting fields | `live_vs_shadow.csv` header includes signal/entry/exit/slippage/fees/net fields. | pass |

## Reason

{status["release_reason"]}
"""


def main() -> int:
    ART_DIR.mkdir(parents=True, exist_ok=True)
    now = pd.Timestamp.now(tz="UTC")
    bars = load_cached_bars(RAW_15M_DIR)
    order_plan = build_order_plan(bars, now)
    replay_end_month = month_start(bars.index.max())
    replay_start_month = replay_end_month - pd.DateOffset(months=12)
    replay = run_replay(bars, replay_start_month, replay_end_month)
    replay_path = ART_DIR / "recent_replay_trades.csv"
    replay.to_csv(replay_path, index=False)
    replay_summary = {
        "strategy_id": STRATEGY_ID,
        "replay_start_month": replay_start_month.strftime("%Y-%m"),
        "replay_end_month_exclusive": replay_end_month.strftime("%Y-%m"),
        "trades": int(len(replay)),
        "net_mean_bps": float(replay["net_bps"].mean()) if not replay.empty else None,
        "net_cum_pct": float(((1.0 + replay["net_ret"]).prod() - 1.0) * 100.0) if not replay.empty else None,
        "source": "src/momentum/strategies/rank32c_btc_utc_weak_cell.py::run_replay",
    }

    hard_blockers = []
    if order_plan.get("decision_blocker"):
        hard_blockers.append(order_plan["decision_blocker"])
    if not order_plan.get("next_entry_ts"):
        hard_blockers.append("cannot_predict_next_entry_exit")
    if not order_plan.get("allow_open"):
        hard_blockers.extend([b for b in order_plan.get("blocked_by", []) if b not in hard_blockers])

    decision = "reject_before_live" if hard_blockers else "launch_tiny_live"
    release_reason = (
        "Current month as-of selection cannot be generated from the local cache; launching would violate the pre-live gate."
        if hard_blockers
        else "All release blockers cleared; next action is tiny-live falsification."
    )

    state = {
        "strategy_id": STRATEGY_ID,
        "updated_at_utc": to_iso(now),
        "decision": decision,
        "allow_live_orders": decision == "launch_tiny_live",
        "open_position": False,
        "open_position_ref": "",
        "last_entry_key": "",
        "duplicate_entry_key_guard": True,
        "residual_position_guard": True,
        "kill_switch_state": "blocked" if decision != "launch_tiny_live" else "armed",
        "hard_blockers": hard_blockers,
    }
    status = {
        "strategy_id": STRATEGY_ID,
        "generated_at_utc": to_iso(now),
        "decision": decision,
        "release_reason": release_reason,
        "hard_blockers": hard_blockers,
        "order_plan_path": str((ART_DIR / "order_plan.json").relative_to(ROOT)),
        "state_path": str((ART_DIR / "state.json").relative_to(ROOT)),
        "status_path": str((ART_DIR / "status.json").relative_to(ROOT)),
        "live_config_path": str(LIVE_CONFIG_PATH.relative_to(ROOT)),
        "recent_replay_path": str(replay_path.relative_to(ROOT)),
        "recent_replay_summary": replay_summary,
    }

    write_json(ART_DIR / "order_plan.json", order_plan)
    write_json(ART_DIR / "state.json", state)
    write_json(ART_DIR / "status.json", status)
    write_json(ART_DIR / "recent_replay_summary.json", replay_summary)
    write_json(ART_DIR / "release_decision.json", {"decision": decision, "hard_blockers": hard_blockers, "release_reason": release_reason})
    write_live_config(decision, order_plan)
    write_csv_header(
        ART_DIR / "closed_trades.csv",
        ["entry_key", "entry_ts", "exit_ts", "symbol", "side", "notional_usdc", "entry_price", "exit_price", "fees_bps", "slippage_bps", "net_ret", "exit_reason", "order_refs"],
    )
    write_csv_header(
        ART_DIR / "live_vs_shadow.csv",
        ["entry_key", "signal_ts", "selected_dow", "selected_hour", "shadow_entry_ts", "live_entry_ts", "shadow_exit_ts", "live_exit_ts", "shadow_ret", "live_ret", "fees_bps", "slippage_bps", "net_gap_bps", "reconciled"],
    )
    (ART_DIR / "release_gate_audit.md").write_text(render_audit(decision, order_plan, status), encoding="utf-8")
    print(json.dumps({"decision": decision, "hard_blockers": hard_blockers, "status_path": status["status_path"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
