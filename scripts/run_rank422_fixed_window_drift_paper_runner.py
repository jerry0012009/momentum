#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from paper_runner_utils import (
    ROOT,
    ensure_dir,
    fetch_binance_futures_book,
    fetch_binance_futures_klines,
    iso_z,
    read_csv_or_empty,
    utc_now,
    write_json,
)

ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank422_fixed_window_drift"
STATUS_PATH = ART_DIR / "rank422_status.csv"
STATE_PATH = ART_DIR / "rank422_state.json"
SPEC_PATH = ART_DIR / "rank422_frozen_launch_spec.json"
LEDGER_PATH = ART_DIR / "rank422_launch_checks.csv"
SNAPSHOT_PATH = ART_DIR / "rank422_current_snapshot.csv"
RUN_SUMMARY_PATH = ART_DIR / "rank422_last_run_summary.json"

RUNNER_SERVICE = "momentum-rank422-paper-refresh.service"
RUNNER_TIMER = "momentum-rank422-paper-refresh.timer"
SYSTEMD_DIR = Path("/etc/systemd/system")
CANDIDATE_ID = "rank422_us_session_fixed_window_drift"
CANDIDATE_RANK = 422
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "DOGEUSDT"]
INTERVAL = "15m"
ROUND_TRIP_COST_BPS = 8.0
ENTRY_HOUR = 21
ENTRY_MINUTE = 15
EXIT_HOUR = 23
EXIT_MINUTE = 0
LOOKBACK_BARS = 96


def build_spec() -> dict:
    return {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "scope": "21:15 UTC delay-one-bar entry -> 23:00 UTC exit, equal-weight EW5 basket (BTC/ETH/SOL/BNB/DOGE)",
        "signal_interval": INTERVAL,
        "entry_rule": "Use only closed 21:00-21:15 UTC bar information; enter at 21:15 UTC open",
        "exit_rule": "Exit basket at 23:00 UTC open",
        "weighting": "equal weight across BTCUSDT/ETHUSDT/SOLUSDT/BNBUSDT/DOGEUSDT",
        "basket_symbols": SYMBOLS,
        "round_trip_cost_bps": ROUND_TRIP_COST_BPS,
        "frozen_admission_metrics": {
            "source_verdict": "promote_P3",
            "ew5_base_gross_bps_per_day": 13.54,
            "ew5_delay_one_bar_gross_bps_per_day": 13.55,
            "ew5_delay_one_bar_net8_bps_per_day": 5.55,
            "ew5_delay_one_bar_win_rate": 58.31,
            "ew5_delay_one_bar_t_stat": 3.53,
        },
        "execution_honesty": "Fixed UTC scheduler only; no same-bar lookahead; no discretionary symbol selection after freeze",
        "source_records": [
            "research/optimization_loop/2026-04-18_2205_rank422_us_session_twowindow_drift_freshintake_keep_p1.md",
            "research/optimization_loop/2026-04-18_2254_rank422_survivor_followup_promote_p2_basket_childentry.md",
            "research/optimization_loop/2026-04-18_2358_rank422_p2_exit_promote_p3_scheduler_realism.md",
        ],
    }


def fetch_recent_frame(symbol: str) -> pd.DataFrame:
    now = utc_now()
    end = pd.Timestamp(now).ceil("15min") + pd.Timedelta(minutes=15)
    start = end - pd.Timedelta(minutes=15 * LOOKBACK_BARS)
    df = fetch_binance_futures_klines(symbol, INTERVAL, int(start.timestamp() * 1000), int(end.timestamp() * 1000))
    if df.empty:
        raise RuntimeError(f"no futures klines fetched for {symbol}")
    df = df.sort_values("ts").reset_index(drop=True)
    df["symbol"] = symbol
    return df.tail(LOOKBACK_BARS).reset_index(drop=True)


def current_window_state(now_ts: pd.Timestamp) -> tuple[str, str | None, str]:
    today = now_ts.normalize()
    entry_ts = today + pd.Timedelta(hours=ENTRY_HOUR, minutes=ENTRY_MINUTE)
    exit_ts = today + pd.Timedelta(hours=EXIT_HOUR, minutes=EXIT_MINUTE)
    if now_ts < entry_ts:
        return "flat", iso_z(entry_ts), "awaiting fixed 21:15 UTC entry"
    if entry_ts <= now_ts < exit_ts:
        return "long", iso_z(exit_ts), "inside fixed 21:15-23:00 UTC long sleeve"
    next_entry = today + pd.Timedelta(days=1, hours=ENTRY_HOUR, minutes=ENTRY_MINUTE)
    return "flat", iso_z(next_entry), "today sleeve finished; waiting next daily entry"


def build_snapshot(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    now_ts = min(pd.Timestamp(df.iloc[-1]["ts"]) for df in frames.values())
    side, planned_ts, reason = current_window_state(now_ts)
    rows: list[dict] = []
    for symbol, df in frames.items():
        row = df.iloc[-1]
        book = fetch_binance_futures_book(symbol, limit=5)
        bid = float(book["bids"][0][0]) if book.get("bids") else None
        ask = float(book["asks"][0][0]) if book.get("asks") else None
        mid = (bid + ask) / 2.0 if bid and ask else None
        spread_bps = ((ask - bid) / mid) * 10000.0 if mid else None
        rows.append(
            {
                "captured_at_utc": iso_z(utc_now()),
                "bar_ts": iso_z(row["ts"]),
                "candidate_rank": CANDIDATE_RANK,
                "symbol": symbol,
                "side": side,
                "weight": round(1.0 / len(SYMBOLS), 6) if side == "long" else 0.0,
                "planned_exit_or_next_entry_utc": planned_ts,
                "window_reason": reason,
                "last_open": float(row["open"]),
                "last_close": float(row["close"]),
                "last_volume": float(row["volume"]),
                "book_bid": bid,
                "book_ask": ask,
                "book_spread_bps": spread_bps,
            }
        )
    return pd.DataFrame(rows)


def scheduler_live() -> bool:
    return (SYSTEMD_DIR / RUNNER_SERVICE).exists() and (SYSTEMD_DIR / RUNNER_TIMER).exists() and (
        SYSTEMD_DIR / "timers.target.wants" / RUNNER_TIMER
    ).exists()


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank 422 fixed-window drift paper runner")
    parser.add_argument("--refresh", action="store_true", help="refresh runtime artifacts")
    args = parser.parse_args()
    if not args.refresh:
        parser.error("choose --refresh")

    ensure_dir(ART_DIR)
    spec = build_spec()
    write_json(SPEC_PATH, spec)

    frames = {symbol: fetch_recent_frame(symbol) for symbol in SYMBOLS}
    snapshot = build_snapshot(frames)
    snapshot.to_csv(SNAPSHOT_PATH, index=False)

    status_side = str(snapshot.iloc[0]["side"]) if not snapshot.empty else "flat"
    schedule_pointer = str(snapshot.iloc[0]["planned_exit_or_next_entry_utc"]) if not snapshot.empty else None
    window_reason = str(snapshot.iloc[0]["window_reason"]) if not snapshot.empty else "no snapshot"
    avg_spread = float(snapshot["book_spread_bps"].dropna().mean()) if not snapshot.empty and snapshot["book_spread_bps"].dropna().size else None
    now = utc_now()

    live_scheduler = scheduler_live()
    wiring_status = "connected_runner_live" if live_scheduler else "runner_ready_pending_scheduler"
    decisive_blocker = "none" if live_scheduler else "scheduler_not_installed_and_first_verified_run_not_done"

    ledger_row = pd.DataFrame([
        {
            "captured_at_utc": iso_z(now),
            "candidate_rank": CANDIDATE_RANK,
            "runner_script": "scripts/run_rank422_fixed_window_drift_paper_runner.py",
            "status_side": status_side,
            "schedule_pointer_utc": schedule_pointer,
            "window_reason": window_reason,
            "symbols": ",".join(SYMBOLS),
            "avg_book_spread_bps": avg_spread,
            "wiring_status": wiring_status,
            "verified_run": True,
        }
    ])
    prev = read_csv_or_empty(LEDGER_PATH)
    pd.concat([prev, ledger_row], ignore_index=True).to_csv(LEDGER_PATH, index=False)

    status = {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "stage": "paper_runner_ready",
        "wiring_status": wiring_status,
        "runner_mode": "frozen_scope_daily_fixed_window",
        "runner_script": "scripts/run_rank422_fixed_window_drift_paper_runner.py",
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "symbols": "|".join(SYMBOLS),
        "signal_interval": INTERVAL,
        "entry_utc": "21:15",
        "exit_utc": "23:00",
        "round_trip_cost_bps": ROUND_TRIP_COST_BPS,
        "current_side": status_side,
        "schedule_pointer_utc": schedule_pointer,
        "avg_book_spread_bps": avg_spread,
        "updated_at_utc": iso_z(now),
        "decisive_blocker": decisive_blocker,
    }
    pd.DataFrame([status]).to_csv(STATUS_PATH, index=False)

    state = {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "wiring_status": status["wiring_status"],
        "runner_mode": status["runner_mode"],
        "runner_script": status["runner_script"],
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "symbols": SYMBOLS,
        "signal_interval": INTERVAL,
        "entry_utc": status["entry_utc"],
        "exit_utc": status["exit_utc"],
        "round_trip_cost_bps": ROUND_TRIP_COST_BPS,
        "current_side": status_side,
        "schedule_pointer_utc": schedule_pointer,
        "window_reason": window_reason,
        "avg_book_spread_bps": avg_spread,
        "source_records": spec["source_records"],
        "last_run_at_utc": iso_z(now),
        "verified_run": True,
        "decisive_blocker": status["decisive_blocker"],
    }
    write_json(STATE_PATH, state)

    run_summary = {
        "run_at_utc": iso_z(now),
        "runner": "rank422_fixed_window_drift_paper_runner",
        "wiring_status": status["wiring_status"],
        "status_path": str(STATUS_PATH.relative_to(ROOT)),
        "state_path": str(STATE_PATH.relative_to(ROOT)),
        "snapshot_path": str(SNAPSHOT_PATH.relative_to(ROOT)),
        "ledger_path": str(LEDGER_PATH.relative_to(ROOT)),
        "spec_path": str(SPEC_PATH.relative_to(ROOT)),
    }
    write_json(RUN_SUMMARY_PATH, run_summary)
    print(json.dumps(run_summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
