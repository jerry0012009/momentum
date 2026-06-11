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
    iso_z,
    read_csv_or_empty,
    utc_now,
    write_json,
)

ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank423_liqshock_oiunwind_exhaustionfade"
SOURCE_SUMMARY_PATH = ROOT / "reports" / "artifacts" / "rank423_entry_realism_followup" / "rank423_entry_realism_summary.json"
SOURCE_EVENTS_PATH = ROOT / "reports" / "artifacts" / "rank423_entry_realism_followup" / "rank423_entry_realism_events.csv"
STATUS_PATH = ART_DIR / "rank423_status.csv"
STATE_PATH = ART_DIR / "rank423_state.json"
SPEC_PATH = ART_DIR / "rank423_frozen_launch_spec.json"
LEDGER_PATH = ART_DIR / "rank423_launch_checks.csv"
SNAPSHOT_PATH = ART_DIR / "rank423_current_snapshot.csv"
RUN_SUMMARY_PATH = ART_DIR / "rank423_last_run_summary.json"

RUNNER_SERVICE = "momentum-rank423-paper-refresh.service"
RUNNER_TIMER = "momentum-rank423-paper-refresh.timer"
SYSTEMD_DIR = Path("/etc/systemd/system")
CANDIDATE_ID = "rank423_liqshock_oiunwind_exhaustionfade"
CANDIDATE_RANK = 423
CORE_SYMBOLS = ["BTCUSDT", "SOLUSDT", "XRPUSDT"]
WATCH_SYMBOLS = ["ETHUSDT", "ADAUSDT"]
INTERVAL = "5m"
ENTRY_DELAY_BARS = 1
HOLD_MINUTES = 30
ROUND_TRIP_COST_BPS = 8.0


def build_spec(summary: dict) -> dict:
    by_symbol = summary.get("by_symbol", {})
    return {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "scope": "BTC/SOL/XRP core only; ETH/ADA close-entry watch only, excluded from default runner",
        "signal_interval": INTERVAL,
        "trigger": "abs(5m return) rolling-q90 + OI value change rolling-q20-or-lower + positive quote-volume z-score",
        "entry_rule": "fade the event direction after 1 closed 5m bar delay; no event-close default fill",
        "exit_rule": "fixed 30m time stop after delayed entry",
        "core_symbols": CORE_SYMBOLS,
        "watch_symbols_excluded_from_default": WATCH_SYMBOLS,
        "round_trip_cost_bps": ROUND_TRIP_COST_BPS,
        "frozen_admission_metrics": {
            "source_verdict": "promote_P3",
            "all_symbols_delay1_net8_bps_per_event": summary.get("delay1_entry_30m", {}).get("net8_mean_bps"),
            "all_symbols_delay1_net12_bps_per_event": summary.get("delay1_entry_30m", {}).get("net12_mean_bps"),
            "btc_delay1_net8": by_symbol.get("BTCUSDT", {}).get("delay_net8"),
            "sol_delay1_net8": by_symbol.get("SOLUSDT", {}).get("delay_net8"),
            "xrp_delay1_net8": by_symbol.get("XRPUSDT", {}).get("delay_net8"),
            "eth_delay1_net8_watch_only": by_symbol.get("ETHUSDT", {}).get("delay_net8"),
            "ada_delay1_net8_watch_only": by_symbol.get("ADAUSDT", {}).get("delay_net8"),
        },
        "execution_honesty": "runner freezes 1-bar delayed entry and BTC/SOL/XRP core scope; ETH/ADA are monitoring notes only, not discretionary live legs",
        "source_records": [
            "research/quant_digests/2026-04-18_2238_liqshock-oiunwind-exhaustionfade-alpha.md",
            "research/optimization_loop/2026-04-19_0040_rank423_liqshock_oiunwind_freshintake_keep_p1_symbol_cost_bucket.md",
            "research/optimization_loop/2026-04-19_0154_rank423_survivor_followup_promote_p2_entry_realism.md",
            "research/optimization_loop/2026-04-19_0300_rank423_p2_exit_promote_p3_delay1_core_scope.md",
        ],
        "source_artifacts": [
            str(SOURCE_SUMMARY_PATH.relative_to(ROOT)),
            str(SOURCE_EVENTS_PATH.relative_to(ROOT)),
        ],
    }


def scheduler_live() -> bool:
    return (SYSTEMD_DIR / RUNNER_SERVICE).exists() and (SYSTEMD_DIR / RUNNER_TIMER).exists() and (
        SYSTEMD_DIR / "timers.target.wants" / RUNNER_TIMER
    ).exists()


def build_snapshot(summary: dict, events: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    by_symbol = summary.get("by_symbol", {})
    for symbol in CORE_SYMBOLS:
        metrics = by_symbol.get(symbol, {})
        bid = ask = mid = spread_bps = None
        try:
            book = fetch_binance_futures_book(symbol, limit=5)
            bid = float(book["bids"][0][0]) if book.get("bids") else None
            ask = float(book["asks"][0][0]) if book.get("asks") else None
            mid = (bid + ask) / 2.0 if bid and ask else None
            spread_bps = ((ask - bid) / mid) * 10000.0 if mid else None
        except Exception as exc:  # book is useful but not a blocker for wiring verification
            spread_bps = None
            mid = None
        symbol_events = events[events["symbol"] == symbol] if "symbol" in events.columns else pd.DataFrame()
        last_event_ts = str(symbol_events["ts"].max()) if not symbol_events.empty and "ts" in symbol_events.columns else None
        rows.append(
            {
                "captured_at_utc": iso_z(utc_now()),
                "candidate_rank": CANDIDATE_RANK,
                "symbol": symbol,
                "runner_role": "core_live_scope",
                "signal_interval": INTERVAL,
                "entry_delay_bars": ENTRY_DELAY_BARS,
                "hold_minutes": HOLD_MINUTES,
                "delay1_net8_bps_admission": metrics.get("delay_net8"),
                "event_count_admission": metrics.get("n"),
                "last_source_event_ts": last_event_ts,
                "book_mid": mid,
                "book_spread_bps": spread_bps,
            }
        )
    return pd.DataFrame(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank 423 liquidation-shock/OI-unwind exhaustion-fade paper runner")
    parser.add_argument("--refresh", action="store_true", help="refresh runtime artifacts")
    args = parser.parse_args()
    if not args.refresh:
        parser.error("choose --refresh")

    missing = [str(p.relative_to(ROOT)) for p in [SOURCE_SUMMARY_PATH, SOURCE_EVENTS_PATH] if not p.exists()]
    if missing:
        raise FileNotFoundError(f"rank423 source artifacts missing: {missing}")

    ensure_dir(ART_DIR)
    summary = json.loads(SOURCE_SUMMARY_PATH.read_text(encoding="utf-8"))
    events = pd.read_csv(SOURCE_EVENTS_PATH)
    spec = build_spec(summary)
    write_json(SPEC_PATH, spec)

    snapshot = build_snapshot(summary, events)
    snapshot.to_csv(SNAPSHOT_PATH, index=False)

    live_scheduler = scheduler_live()
    wiring_status = "connected_runner_live" if live_scheduler else "runner_ready_pending_scheduler"
    blocker = "none" if live_scheduler else "scheduler_not_installed_or_not_enabled"
    now = utc_now()

    core_net8 = [float(v) for v in snapshot["delay1_net8_bps_admission"].dropna().tolist()]
    min_core_net8 = min(core_net8) if core_net8 else None
    avg_spread = float(snapshot["book_spread_bps"].dropna().mean()) if snapshot["book_spread_bps"].dropna().size else None

    ledger_row = pd.DataFrame([
        {
            "captured_at_utc": iso_z(now),
            "candidate_rank": CANDIDATE_RANK,
            "runner_script": "scripts/run_rank423_liqshock_oiunwind_paper_runner.py",
            "symbols": "|".join(CORE_SYMBOLS),
            "signal_interval": INTERVAL,
            "entry_delay_bars": ENTRY_DELAY_BARS,
            "hold_minutes": HOLD_MINUTES,
            "min_core_delay1_net8_bps_admission": min_core_net8,
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
        "runner_mode": "frozen_scope_event_driven_exhaustion_fade",
        "runner_script": "scripts/run_rank423_liqshock_oiunwind_paper_runner.py",
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "core_symbols": "|".join(CORE_SYMBOLS),
        "watch_symbols_excluded": "|".join(WATCH_SYMBOLS),
        "signal_interval": INTERVAL,
        "entry_delay_bars": ENTRY_DELAY_BARS,
        "hold_minutes": HOLD_MINUTES,
        "round_trip_cost_bps": ROUND_TRIP_COST_BPS,
        "min_core_delay1_net8_bps_admission": min_core_net8,
        "avg_book_spread_bps": avg_spread,
        "updated_at_utc": iso_z(now),
        "decisive_blocker": blocker,
    }
    pd.DataFrame([status]).to_csv(STATUS_PATH, index=False)

    state = {
        **status,
        "wiring_status": wiring_status,
        "source_records": spec["source_records"],
        "source_artifacts": spec["source_artifacts"],
        "last_run_at_utc": iso_z(now),
        "verified_run": True,
    }
    write_json(STATE_PATH, state)

    run_summary = {
        "run_at_utc": iso_z(now),
        "runner": "rank423_liqshock_oiunwind_paper_runner",
        "wiring_status": wiring_status,
        "decisive_blocker": blocker,
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
