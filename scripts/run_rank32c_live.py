#!/usr/bin/env python3
"""First-money strategy live runner.

Workflow:
1. Load latest cached 15m kline data
2. Call build_order_plan to get current month's signal
3. Check veto/gate controls
4. If allow_open=True and within entry window, place market order via Binance Futures
5. Track open position and exit after 16 bars
6. Record all trades to ledger CSV

Designed to be run every 15 minutes via systemd timer.
"""
from __future__ import annotations

import csv
import io
import json
import os
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from momentum.strategies.rank32c_btc_utc_weak_cell import (
    BAR_MINUTES,
    HOLD_BARS,
    TINY_LIVE_NOTIONAL_USDC,
    StrategySpec,
    build_order_plan,
    evaluate_entry_controls,
    load_cached_bars,
    month_start,
    select_month_cell,
    to_iso,
)

# Import broker
sys.path.insert(0, str(ROOT / "src" / "momentum" / "execution" / "rank32c"))
from binance_futures_broker import BinanceFuturesBroker

# Paths
ART_DIR = ROOT / "reports" / "artifacts" / "rank32c_live"
LEDGER_PATH = ART_DIR / "closed_trades.csv"
STATE_PATH = ART_DIR / "state.json"
STATUS_PATH = ART_DIR / "status.json"
EVENTS_PATH = ART_DIR / "events.jsonl"
RUN_SUMMARY_PATH = ART_DIR / "last_run_summary.json"
ORDER_PLAN_PATH = ART_DIR / "order_plan.json"

# Cache path — use the shared rank213 cache (incrementally updated)
RAW_15M_DIR = (
    ROOT
    / "reports"
    / "artifacts"
    / "paper_rank213_largecap_xs_jump_veto"
    / "rank213_local_cache"
    / "monthly_marketcap_universe"
    / "raw_15m"
)

# Config
SYMBOL = "BTCUSDT"
NOTIONAL_USDC = TINY_LIVE_NOTIONAL_USDC
LEVERAGE = 1

# Private API keys
PRIVATE_CONFIG = ROOT / "config" / "private" / "fr_monitor_config_private.py"


def load_api_keys() -> tuple[str, str]:
    """Load Binance API key and secret from private config."""
    text = PRIVATE_CONFIG.read_text(encoding="utf-8")
    ns: dict = {}
    exec(text, ns)
    api_key = ns.get("BN_API_KEY_ACCOUNT2", "")
    secret_key = ns.get("BN_SECRET_KEY_ACCOUNT2", "")
    if not api_key or not secret_key:
        raise RuntimeError("BN_API_KEY_ACCOUNT2 / BN_SECRET_KEY_ACCOUNT2 not found in private config")
    return api_key, secret_key


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    return utc_now().strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json(path: Path, default=None):
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def append_jsonl(path: Path, row: dict, keep_last: int = 500) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    if path.exists():
        lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    lines.append(json.dumps(row, ensure_ascii=False))
    lines = lines[-keep_last:]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_csv_or_empty(path: Path):
    import pandas as pd
    if not path.exists() or path.stat().st_size == 0:
        return __import__("pandas").DataFrame()
    return __import__("pandas").read_csv(path)


def ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def now_ts() -> __import__("pandas").Timestamp:
    import pandas as pd
    return pd.Timestamp.now(tz="UTC")


def load_state() -> dict:
    return read_json(STATE_PATH, {
        "open_position": False,
        "open_side": None,
        "open_entry_ts": None,
        "open_entry_price": None,
        "open_exit_ts": None,
        "open_order_id": None,
        "last_signal_ts": None,
        "trade_count": 0,
        "running_net_bps": 0.0,
        "kill_switch_active": False,
    })


def save_state(state: dict) -> None:
    write_json(STATE_PATH, state)


def check_kill_switch(state: dict, broker: BinanceFuturesBroker) -> list[str]:
    """Check kill switch conditions. Returns list of active triggers."""
    triggers = []
    closed = read_csv_or_empty(LEDGER_PATH)
    if not closed.empty:
        recent = closed.tail(5)
        if len(recent) >= 5:
            net_ret_sum = recent["net_ret"].astype(float).sum()
            if net_ret_sum <= -0.025:
                triggers.append(f"5_trade_net_loss_{net_ret_sum:.4f}")
        if "net_ret" in closed.columns:
            worst = closed["net_ret"].astype(float).min()
            if worst <= -0.012:
                triggers.append(f"single_trade_loss_{worst:.4f}")
    return triggers


def record_trade(state: dict, entry_result: dict, exit_result: dict, signal_info: dict) -> None:
    """Record a completed trade to the ledger."""
    ensure_dir(LEDGER_PATH)

    entry_price = float(entry_result.get("avg_fill_price", 0) or 0)
    exit_price = float(exit_result.get("avg_fill_price", 0) or 0)

    side = signal_info.get("side", "short")
    if side == "short":
        gross_ret = (entry_price - exit_price) / entry_price if entry_price else 0
    else:
        gross_ret = (exit_price - entry_price) / entry_price if entry_price else 0

    # Assume 10bps round-trip for fees+slippage in live
    fees_bps = 10.0
    net_ret = gross_ret - fees_bps / 10000.0
    net_bps = net_ret * 10000.0

    row = {
        "entry_key": signal_info.get("entry_key", ""),
        "signal_ts": signal_info.get("signal_ts", ""),
        "entry_ts": entry_result.get("submitted_at", ""),
        "exit_ts": exit_result.get("submitted_at", ""),
        "symbol": SYMBOL,
        "side": side,
        "dow": signal_info.get("dow"),
        "hour": signal_info.get("hour"),
        "notional_usdc": NOTIONAL_USDC,
        "entry_price": entry_price,
        "exit_price": exit_price,
        "gross_ret": round(gross_ret, 8),
        "net_ret": round(net_ret, 8),
        "gross_bps": round(gross_ret * 10000, 2),
        "net_bps": round(net_bps, 2),
        "fees_bps": fees_bps,
        "entry_order_id": entry_result.get("order_id", ""),
        "exit_order_id": exit_result.get("order_id", ""),
        "train_mean_long_bps": signal_info.get("train_mean_long_bps", ""),
    }

    # Append to CSV
    fieldnames = list(row.keys())
    file_exists = LEDGER_PATH.exists() and LEDGER_PATH.stat().st_size > 0
    with LEDGER_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    return row


def run_once() -> int:
    """Execute one live-runner cycle. Returns exit code."""
    import pandas as pd

    t0 = utc_now()
    ts = pd.Timestamp.now(tz="UTC")
    ART_DIR.mkdir(parents=True, exist_ok=True)

    state = load_state()

    # Kill switch check
    if state.get("kill_switch_active"):
        summary = {"status": "killed", "reason": "kill_switch_active", "ts": utc_now_iso()}
        write_json(RUN_SUMMARY_PATH, summary)
        print(json.dumps(summary))
        return 1

    # Load API keys and create broker
    api_key, secret_key = load_api_keys()
    # Start with testnet=True for safety; switch to False for real money
    use_testnet = os.environ.get("RANK32C_TESTNET", "1") == "1"
    broker = BinanceFuturesBroker(api_key=api_key, secret_key=secret_key, testnet=use_testnet)

    # Load bars
    try:
        bars = load_cached_bars(RAW_15M_DIR)
    except FileNotFoundError as e:
        summary = {"status": "error", "reason": f"bar_cache_missing: {e}", "ts": utc_now_iso()}
        write_json(RUN_SUMMARY_PATH, summary)
        print(json.dumps(summary))
        return 1

    cache_last_bar = bars.index.max()
    cache_staleness_min = (ts - cache_last_bar).total_seconds() / 60.0
    if cache_staleness_min > 60:
        summary = {"status": "error", "reason": f"stale_cache_{cache_staleness_min:.0f}min", "ts": utc_now_iso()}
        write_json(RUN_SUMMARY_PATH, summary)
        print(json.dumps(summary))
        return 1

    # Build order plan
    try:
        plan = build_order_plan(bars, ts)
    except Exception as e:
        summary = {"status": "error", "reason": f"order_plan_failed: {e}", "ts": utc_now_iso()}
        write_json(RUN_SUMMARY_PATH, summary)
        print(json.dumps(summary))
        return 1

    write_json(ORDER_PLAN_PATH, plan)

    # Kill switch triggers
    kill_triggers = check_kill_switch(state, broker)
    if kill_triggers:
        state["kill_switch_active"] = True
        save_state(state)
        summary = {"status": "killed", "triggers": kill_triggers, "ts": utc_now_iso()}
        write_json(RUN_SUMMARY_PATH, summary)
        append_jsonl(EVENTS_PATH, {"event": "kill_switch", "triggers": kill_triggers, "ts": utc_now_iso()})
        print(json.dumps(summary))
        return 1

    # If we have an open position, check if it's time to exit
    if state.get("open_position"):
        exit_ts_str = state.get("open_exit_ts")
        if exit_ts_str:
            exit_ts = pd.Timestamp(exit_ts_str)
            if ts >= exit_ts:
                # Time to close
                try:
                    exit_result_raw = broker.close_position(SYMBOL)
                    exit_result = exit_result_raw.to_dict() if exit_result_raw else {"order_id": "no_position", "avg_fill_price": 0, "submitted_at": utc_now_iso()}

                    entry_info = {
                        "entry_key": state.get("open_entry_key", ""),
                        "signal_ts": state.get("open_signal_ts", ""),
                        "side": plan.get("side", "short"),
                        "dow": state.get("open_dow"),
                        "hour": state.get("open_hour"),
                        "train_mean_long_bps": state.get("open_train_mean_long_bps"),
                    }
                    trade_row = record_trade(state, {
                        "avg_fill_price": state.get("open_entry_price", 0),
                        "order_id": state.get("open_order_id", ""),
                        "submitted_at": state.get("open_entry_ts", ""),
                    }, exit_result, entry_info)

                    state["open_position"] = False
                    state["open_side"] = None
                    state["open_entry_ts"] = None
                    state["open_exit_ts"] = None
                    state["open_order_id"] = None
                    state["trade_count"] = state.get("trade_count", 0) + 1
                    state["running_net_bps"] = state.get("running_net_bps", 0) + trade_row["net_bps"]
                    save_state(state)

                    append_jsonl(EVENTS_PATH, {
                        "event": "exit",
                        "trade": trade_row,
                        "exit_order": exit_result,
                        "ts": utc_now_iso(),
                    })

                    summary = {
                        "status": "exited",
                        "trade": trade_row,
                        "state": state,
                        "ts": utc_now_iso(),
                    }
                    write_json(RUN_SUMMARY_PATH, summary)
                    print(json.dumps(summary))
                    return 0

                except Exception as e:
                    summary = {"status": "exit_error", "reason": str(e), "ts": utc_now_iso()}
                    write_json(RUN_SUMMARY_PATH, summary)
                    append_jsonl(EVENTS_PATH, {"event": "exit_error", "error": str(e), "ts": utc_now_iso()})
                    print(json.dumps(summary))
                    return 1
            else:
                # Position still open, nothing to do
                summary = {
                    "status": "holding",
                    "open_side": state.get("open_side"),
                    "exit_at": exit_ts_str,
                    "minutes_to_exit": (exit_ts - ts).total_seconds() / 60,
                    "ts": utc_now_iso(),
                }
                write_json(RUN_SUMMARY_PATH, summary)
                print(json.dumps(summary))
                return 0

    # No open position — check if we should enter
    if not plan.get("allow_open"):
        summary = {
            "status": "no_signal",
            "blocked_by": plan.get("blocked_by", []),
            "selected_cell": plan.get("selected_cell"),
            "ts": utc_now_iso(),
        }
        write_json(RUN_SUMMARY_PATH, summary)
        print(json.dumps(summary))
        return 0

    # We should enter — but only if we're within 1 bar of the entry time
    next_entry_str = plan.get("next_entry_ts")
    if not next_entry_str:
        summary = {"status": "no_entry_time", "ts": utc_now_iso()}
        write_json(RUN_SUMMARY_PATH, summary)
        print(json.dumps(summary))
        return 0

    next_entry = pd.Timestamp(next_entry_str)
    bars_until_entry = (next_entry - ts).total_seconds() / (BAR_MINUTES * 60)

    if bars_until_entry > 1.5:
        # Too early, wait
        summary = {
            "status": "waiting",
            "next_entry": next_entry_str,
            "bars_until_entry": round(bars_until_entry, 2),
            "ts": utc_now_iso(),
        }
        write_json(RUN_SUMMARY_PATH, summary)
        print(json.dumps(summary))
        return 0

    if bars_until_entry < -0.5:
        # Missed the window
        summary = {
            "status": "missed_window",
            "next_entry": next_entry_str,
            "bars_past": round(-bars_until_entry, 2),
            "ts": utc_now_iso(),
        }
        write_json(RUN_SUMMARY_PATH, summary)
        print(json.dumps(summary))
        return 0

    # Place entry order
    side = plan.get("side", "short")
    order_side = "SELL" if side == "short" else "BUY"

    try:
        broker.set_leverage(SYMBOL, LEVERAGE)
    except Exception:
        pass  # May already be set

    try:
        qty = broker.compute_qty(SYMBOL, NOTIONAL_USDC)
        if qty <= 0:
            summary = {"status": "qty_zero", "ts": utc_now_iso()}
            write_json(RUN_SUMMARY_PATH, summary)
            print(json.dumps(summary))
            return 1

        entry_result = broker.place_market_order(SYMBOL, order_side, qty)
        exit_ts = next_entry + pd.Timedelta(minutes=BAR_MINUTES * HOLD_BARS)

        cell = plan.get("selected_cell", {})
        entry_key = f"{SYMBOL}|{cell.get('dow')}|{cell.get('hour')}|{next_entry_str}"

        state["open_position"] = True
        state["open_side"] = side
        state["open_entry_ts"] = utc_now_iso()
        state["open_entry_price"] = entry_result.avg_fill_price
        state["open_exit_ts"] = to_iso(exit_ts)
        state["open_order_id"] = entry_result.order_id
        state["open_entry_key"] = entry_key
        state["open_signal_ts"] = utc_now_iso()
        state["open_dow"] = cell.get("dow")
        state["open_hour"] = cell.get("hour")
        state["open_train_mean_long_bps"] = cell.get("train_mean_long_bps")
        save_state(state)

        append_jsonl(EVENTS_PATH, {
            "event": "entry",
            "entry_order": entry_result.to_dict(),
            "plan": plan,
            "qty": qty,
            "notional_usdc": NOTIONAL_USDC,
            "ts": utc_now_iso(),
        })

        summary = {
            "status": "entered",
            "side": side,
            "qty": qty,
            "avg_fill_price": entry_result.avg_fill_price,
            "exit_ts": to_iso(exit_ts),
            "order": entry_result.to_dict(),
            "ts": utc_now_iso(),
        }
        write_json(RUN_SUMMARY_PATH, summary)
        print(json.dumps(summary))
        return 0

    except Exception as e:
        summary = {"status": "entry_error", "reason": str(e), "ts": utc_now_iso()}
        write_json(RUN_SUMMARY_PATH, summary)
        append_jsonl(EVENTS_PATH, {"event": "entry_error", "error": str(e), "ts": utc_now_iso()})
        print(json.dumps(summary))
        return 1


def main() -> int:
    return run_once()


if __name__ == "__main__":
    raise SystemExit(main())
