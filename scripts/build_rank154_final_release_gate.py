#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = ROOT / "reports" / "artifacts" / "paper_rank154_crypto_stat_arb_runner"
ART_DIR = ROOT / "reports" / "artifacts" / "rank154_final_release_gate"
RUNNER_PATH = ROOT / "scripts" / "run_rank154_crypto_stat_arb_paper_runner.py"
LIVE_CONFIG_PATH = ROOT / "config" / "strategies" / "rank154_crypto_stat_arb_tiny_live.yaml"

EQUITY_PATH = PAPER_DIR / "rank154_paper_equity_curve.csv"
DECISIONS_PATH = PAPER_DIR / "rank154_paper_decisions.csv"
TRADES_PATH = PAPER_DIR / "rank154_paper_rebalance_trades.csv"
STATE_PATH = PAPER_DIR / "rank154_paper_state.json"
STATUS_PATH = PAPER_DIR / "rank154_paper_status.csv"

STRATEGY_ID = "rank154_crypto_stat_arb_v1"
TINY_GROSS_NOTIONAL_USDT = 25.0
ESTIMATED_MIN_PERP_ORDER_USDT = 5.0


def iso_z(ts: pd.Timestamp) -> str:
    return pd.to_datetime(ts, utc=True).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv_header(path: Path, fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 0:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=fields).writeheader()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def calc_return(first_equity: float, last_equity: float) -> float:
    if first_equity <= 0:
        return 0.0
    return last_equity / first_equity - 1.0


def build_scorecard(equity: pd.DataFrame, trades: pd.DataFrame, decisions: pd.DataFrame, state: dict) -> dict:
    equity = equity.copy()
    equity["signal_date_utc"] = pd.to_datetime(equity["signal_date_utc"], utc=True)
    equity = equity.sort_values("signal_date_utc").reset_index(drop=True)
    last = equity.iloc[-1]
    first = equity.iloc[0]
    daily_ret = equity["equity_after_rebalance_usd"].pct_change().dropna()
    selected_decisions = decisions[decisions["selected"].astype(str).isin(["1", "1.0", "True", "true"])] if not decisions.empty else pd.DataFrame()
    latest_signal = str(state.get("last_signal_date_utc") or "")
    latest_positions = state.get("positions", {}) or {}
    active_legs = [sym for sym, pos in latest_positions.items() if abs(float(pos.get("weight") or 0.0)) > 0]
    latest_actions = trades[trades["signal_date_utc"] == latest_signal].copy() if not trades.empty and latest_signal else pd.DataFrame()
    active_trade_actions = latest_actions[latest_actions["action"].isin(["buy", "sell"])] if not latest_actions.empty else pd.DataFrame()
    first_equity_after = float(first["equity_after_rebalance_usd"])
    last_equity = float(last["equity_after_rebalance_usd"])
    running_max = float(equity["running_max_equity_usd"].max())
    worst_drawdown = float(equity["drawdown"].min())
    last_7_return = calc_return(float(equity.tail(min(8, len(equity))).iloc[0]["equity_after_rebalance_usd"]), last_equity) if len(equity) >= 2 else 0.0
    last_14_return = calc_return(float(equity.tail(min(15, len(equity))).iloc[0]["equity_after_rebalance_usd"]), last_equity) if len(equity) >= 2 else 0.0
    last_30_return = calc_return(float(equity.tail(min(31, len(equity))).iloc[0]["equity_after_rebalance_usd"]), last_equity) if len(equity) >= 2 else 0.0
    return {
        "strategy_id": STRATEGY_ID,
        "source": "paper_rank154_crypto_stat_arb_runner",
        "sample_start_utc": iso_z(equity["signal_date_utc"].min()),
        "sample_end_utc": iso_z(equity["signal_date_utc"].max()),
        "paper_days": int(len(equity)),
        "latest_signal_date_utc": latest_signal,
        "latest_rebalance_ts_utc": state.get("last_rebalance_ts_utc"),
        "initial_equity_after_first_rebalance_usd": first_equity_after,
        "current_equity_usd": last_equity,
        "lifetime_return": float(last_equity / 10000.0 - 1.0),
        "return_from_first_forward_row": calc_return(first_equity_after, last_equity),
        "running_max_equity_usd": running_max,
        "current_drawdown": float(last["drawdown"]),
        "worst_drawdown": worst_drawdown,
        "positive_daily_return_share": float((daily_ret > 0).mean()) if not daily_ret.empty else None,
        "last_7_signal_day_return": last_7_return,
        "last_14_signal_day_return": last_14_return,
        "last_30_signal_day_return": last_30_return,
        "daily_rebalance_rows": int(len(equity)),
        "decision_rows": int(len(decisions)),
        "selected_decision_rows": int(len(selected_decisions)),
        "rebalance_trade_rows": int(len(trades)),
        "latest_active_legs": int(len(active_legs)),
        "latest_buy_sell_actions": int(len(active_trade_actions)),
        "gross_exposure": float(last["gross_exposure"]),
        "net_exposure": float(last["net_exposure"]),
        "latest_top_long": str(last["top_long"]),
        "latest_top_short": str(last["top_short"]),
    }


def static_honesty_audit() -> dict:
    text = RUNNER_PATH.read_text(encoding="utf-8")
    return {
        "runner_path": str(RUNNER_PATH.relative_to(ROOT)),
        "completed_daily_bar_filter_present": "close_time" in text and "< now_ms" in text,
        "daily_rolling_features_present": all(s in text for s in ["rolling(30", "pct_change(10)", "days_since_high_rolling"]),
        "funding_aggregation_present": "groupby(\"date\"" in text and "funding_rate" in text,
        "ffill_present": ".ffill(" in text or ".ffill()" in text,
        "bfill_present": ".bfill(" in text or ".bfill()" in text,
        "shared_signal_module_present": (ROOT / "src" / "momentum" / "strategies" / "rank154_crypto_stat_arb.py").exists(),
        "paper_runner_uses_shared_signal_module": "rank154_signal.build_panel_for_date" in text,
        "live_runner_present": (ROOT / "scripts" / "run_rank154_crypto_stat_arb_tiny_live.py").exists(),
    }


def build_order_plan(state: dict) -> dict:
    positions = state.get("positions", {}) or {}
    legs = []
    estimated_min_gross = 0.0
    for symbol, pos in sorted(positions.items()):
        weight = float(pos.get("weight") or 0.0)
        if abs(weight) <= 0:
            continue
        target_notional = TINY_GROSS_NOTIONAL_USDT * abs(weight)
        estimated_min_gross += ESTIMATED_MIN_PERP_ORDER_USDT
        legs.append(
            {
                "symbol": symbol,
                "side": "long" if weight > 0 else "short",
                "target_weight": weight,
                "tiny_target_notional_usdt": target_notional,
                "estimated_exchange_min_notional_usdt": ESTIMATED_MIN_PERP_ORDER_USDT,
                "tiny_leg_below_estimated_min": target_notional < ESTIMATED_MIN_PERP_ORDER_USDT,
                "shadow_entry_price": float(pos.get("entry_price") or 0.0),
                "shadow_signal_date_utc": pos.get("entry_signal_date_utc"),
                "decision_reason": pos.get("decision_reason") or "",
            }
        )
    return {
        "strategy_id": STRATEGY_ID,
        "mode": "tiny_live_order_plan_blocked",
        "latest_signal_date_utc": state.get("last_signal_date_utc"),
        "latest_rebalance_ts_utc": state.get("last_rebalance_ts_utc"),
        "paper_equity_usd": state.get("current_equity"),
        "tiny_gross_notional_usdt": TINY_GROSS_NOTIONAL_USDT,
        "estimated_min_gross_notional_for_current_legs_usdt": estimated_min_gross,
        "latest_active_legs": len(legs),
        "legs": legs,
        "allow_live_orders": False,
        "kill_switch_state": "blocked",
    }


def write_live_config(decision: str, blockers: list[str], order_plan: dict) -> None:
    lines = [
        f'strategy_id: "{STRATEGY_ID}"',
        f'mode: "{decision}"',
        "allow_live_orders: false",
        'source_paper_runner: "scripts/run_rank154_crypto_stat_arb_paper_runner.py"',
        'signal_timeframe: "1d"',
        'refresh_cadence: "daily after UTC close"',
        "universe_rule: \"top 30 guarded Binance USDT-M perpetuals by completed rolling 30d quote volume from top 60 24h probe\"",
        'signal: "0.5 carry_decile + 0.2 momentum_10d_decile + 0.3 breakout_recency_decile, cross-section centered"',
        "max_abs_weight: 0.10",
        "cost_bps_per_side: 5.0",
        "min_listing_days: 180",
        f"tiny_gross_notional_usdt: {TINY_GROSS_NOTIONAL_USDT}",
        f"estimated_min_gross_notional_for_current_legs_usdt: {order_plan.get('estimated_min_gross_notional_for_current_legs_usdt')}",
        f"latest_active_legs: {order_plan.get('latest_active_legs')}",
        f'hard_blockers: "{", ".join(blockers)}"',
        f'order_plan_path: "{(ART_DIR / "order_plan.json").relative_to(ROOT)}"',
        f'status_path: "{(ART_DIR / "status.json").relative_to(ROOT)}"',
        f'state_path: "{(ART_DIR / "state.json").relative_to(ROOT)}"',
        f'live_vs_shadow_ledger: "{(ART_DIR / "live_vs_shadow.csv").relative_to(ROOT)}"',
        f'closed_trade_ledger: "{(ART_DIR / "closed_trades.csv").relative_to(ROOT)}"',
        'kill_switch: "blocked until shared signal module, tiny-live runner, exchange precision checks, residual flatten, duplicate rebalance guard, and live-vs-shadow reconciliation exist"',
    ]
    LIVE_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LIVE_CONFIG_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_audit(decision: str, blockers: list[str], scorecard: dict, static_audit: dict, order_plan: dict) -> str:
    return f"""# Rank154 Final Release Gate

## Binary Decision

`{decision}`

## Evidence Snapshot

- paper sample: `{scorecard["sample_start_utc"]}` to `{scorecard["sample_end_utc"]}` ({scorecard["paper_days"]} daily rows)
- lifetime_return: `{scorecard["lifetime_return"]}`
- current_drawdown: `{scorecard["current_drawdown"]}`
- worst_drawdown: `{scorecard["worst_drawdown"]}`
- last_7_signal_day_return: `{scorecard["last_7_signal_day_return"]}`
- last_14_signal_day_return: `{scorecard["last_14_signal_day_return"]}`
- last_30_signal_day_return: `{scorecard["last_30_signal_day_return"]}`
- latest_active_legs: `{scorecard["latest_active_legs"]}`
- latest_buy_sell_actions: `{scorecard["latest_buy_sell_actions"]}`
- gross_exposure: `{scorecard["gross_exposure"]}`
- net_exposure: `{scorecard["net_exposure"]}`

## Honesty And Execution Checks

| Check | Evidence | Status |
| --- | --- | --- |
| Completed daily bars only | close-time filter present in paper runner | {"pass" if static_audit["completed_daily_bar_filter_present"] else "fail"} |
| No obvious ffill/bfill path | static scan for `.ffill` / `.bfill` | {"pass" if not static_audit["ffill_present"] and not static_audit["bfill_present"] else "fail"} |
| Cost and funding accounted | daily funding aggregation and 5 bps/side cost path present | {"pass" if static_audit["funding_aggregation_present"] else "fail"} |
| Positive forward paper | lifetime return > 0 | {"pass" if scorecard["lifetime_return"] > 0 else "fail"} |
| Trigger frequency | daily rebalance rows and current buy/sell actions exist | {"pass" if scorecard["paper_days"] >= 20 and scorecard["latest_buy_sell_actions"] > 0 else "fail"} |
| Shared signal module | paper runner calls `rank154_signal.build_panel_for_date()` | {"pass" if static_audit["shared_signal_module_present"] and static_audit["paper_runner_uses_shared_signal_module"] else "fail"} |
| Tiny-live runner | `scripts/run_rank154_crypto_stat_arb_tiny_live.py` exists | {"pass" if static_audit["live_runner_present"] else "fail"} |
| Tiny notional executable | 25 USDT gross can cover current active legs | {"pass" if order_plan["tiny_gross_notional_usdt"] >= order_plan["estimated_min_gross_notional_for_current_legs_usdt"] else "fail"} |
| Live-vs-shadow ledger | release package creates required header | pass |

## Current Order Plan

- latest_signal_date_utc: `{order_plan["latest_signal_date_utc"]}`
- latest_rebalance_ts_utc: `{order_plan["latest_rebalance_ts_utc"]}`
- tiny_gross_notional_usdt: `{order_plan["tiny_gross_notional_usdt"]}`
- estimated_min_gross_notional_for_current_legs_usdt: `{order_plan["estimated_min_gross_notional_for_current_legs_usdt"]}`
- allow_live_orders: `{order_plan["allow_live_orders"]}`
- kill_switch_state: `{order_plan["kill_switch_state"]}`

## Hard Blockers

{chr(10).join(f"- `{b}`" for b in blockers)}
"""


def main() -> int:
    ART_DIR.mkdir(parents=True, exist_ok=True)
    equity = pd.read_csv(EQUITY_PATH)
    decisions = pd.read_csv(DECISIONS_PATH)
    trades = pd.read_csv(TRADES_PATH)
    state = read_json(STATE_PATH)

    scorecard = build_scorecard(equity, trades, decisions, state)
    static_audit = static_honesty_audit()
    order_plan = build_order_plan(state)

    blockers: list[str] = []
    if scorecard["lifetime_return"] <= 0:
        blockers.append("forward_paper_not_positive")
    if scorecard["paper_days"] < 60:
        blockers.append("forward_paper_history_lt_60_daily_rows")
    if scorecard["worst_drawdown"] <= -0.12:
        blockers.append("paper_drawdown_exceeds_12pct")
    if scorecard["last_30_signal_day_return"] < 0:
        blockers.append("last_30_signal_days_negative")
    if not static_audit["completed_daily_bar_filter_present"]:
        blockers.append("completed_bar_filter_not_verified")
    if static_audit["ffill_present"] or static_audit["bfill_present"]:
        blockers.append("forward_fill_or_backfill_path_present")
    if not static_audit["shared_signal_module_present"] or not static_audit["paper_runner_uses_shared_signal_module"]:
        blockers.append("missing_shared_signal_module")
    if not static_audit["live_runner_present"]:
        blockers.append("missing_tiny_live_runner")
    if order_plan["tiny_gross_notional_usdt"] < order_plan["estimated_min_gross_notional_for_current_legs_usdt"]:
        blockers.append("tiny_notional_infeasible_for_current_leg_count")

    decision = "reject_before_live" if blockers else "launch_tiny_live"
    status = {
        "strategy_id": STRATEGY_ID,
        "decision": decision,
        "hard_blockers": blockers,
        "scorecard_path": str((ART_DIR / "scorecard.json").relative_to(ROOT)),
        "order_plan_path": str((ART_DIR / "order_plan.json").relative_to(ROOT)),
        "audit_path": str((ART_DIR / "release_gate_audit.md").relative_to(ROOT)),
        "status_path": str((ART_DIR / "status.json").relative_to(ROOT)),
        "live_config_path": str(LIVE_CONFIG_PATH.relative_to(ROOT)),
    }
    release = {
        "decision": decision,
        "hard_blockers": blockers,
        "reason": "Rank154 is the best current next candidate, but it is not yet honest/executable enough for tiny-live." if blockers else "All release blockers cleared.",
    }
    runtime_state = {
        "strategy_id": STRATEGY_ID,
        "decision": decision,
        "allow_live_orders": False,
        "open_position_guard": True,
        "duplicate_rebalance_guard": True,
        "residual_flatten_required": True,
        "hard_blockers": blockers,
        "source_paper_state": str(STATE_PATH.relative_to(ROOT)),
    }

    write_json(ART_DIR / "scorecard.json", scorecard)
    write_json(ART_DIR / "static_honesty_audit.json", static_audit)
    write_json(ART_DIR / "order_plan.json", order_plan)
    write_json(ART_DIR / "status.json", status)
    write_json(ART_DIR / "state.json", runtime_state)
    write_json(ART_DIR / "release_decision.json", release)
    write_live_config(decision, blockers, order_plan)
    write_csv_header(
        ART_DIR / "live_vs_shadow.csv",
        ["rebalance_date", "symbol", "shadow_target_weight", "live_target_weight", "shadow_order_notional", "live_order_notional", "shadow_price", "live_fill_price", "fees_usdt", "slippage_bps", "position_delta_usdt", "reconciled"],
    )
    write_csv_header(
        ART_DIR / "closed_trades.csv",
        ["rebalance_date", "symbol", "side", "entry_ts", "exit_ts", "entry_price", "exit_price", "quantity", "fees_usdt", "funding_usdt", "net_pnl_usdt", "shadow_pnl_usdt", "delta_vs_shadow_usdt", "exit_reason"],
    )
    (ART_DIR / "release_gate_audit.md").write_text(render_audit(decision, blockers, scorecard, static_audit, order_plan), encoding="utf-8")
    print(json.dumps({"decision": decision, "hard_blockers": blockers, "status_path": status["status_path"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
