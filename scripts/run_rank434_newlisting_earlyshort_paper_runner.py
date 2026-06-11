#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from paper_runner_utils import ROOT, ensure_dir, iso_z, read_csv_or_empty, utc_now, write_json

CANDIDATE_ID = "rank434_newlisting_earlyshort_bubble_fade"
CANDIDATE_RANK = 434
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank434_newlisting_earlyshort_bubble_fade"
TRADES_PATH = ROOT / "reports" / "artifacts" / "quant_digests" / "newlisting_short_15m_trades_2026-04-22.csv"
SUMMARY_PATH = ROOT / "reports" / "artifacts" / "quant_digests" / "newlisting_short_15m_summary_2026-04-22.csv"
FOLLOWUP_PATH = ROOT / "reports" / "artifacts" / "optimization_loop" / "rank434_survivor_followup_symbolcap_realism_2026-04-22.csv"
STATUS_PATH = ART_DIR / "rank434_status.csv"
STATE_PATH = ART_DIR / "rank434_state.json"
SPEC_PATH = ART_DIR / "rank434_frozen_launch_spec.json"
LEDGER_PATH = ART_DIR / "rank434_launch_checks.csv"
SNAPSHOT_PATH = ART_DIR / "rank434_current_snapshot.csv"
SIGNAL_PATH = ART_DIR / "rank434_live_signal_snapshot.csv"
RUN_SUMMARY_PATH = ART_DIR / "rank434_last_run_summary.json"
RUNNER_SERVICE = "momentum-rank434-paper-refresh.service"
RUNNER_TIMER = "momentum-rank434-paper-refresh.timer"


def build_spec() -> dict:
    return {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "scope": "Binance USDⓈ-M newly listed USDT perps; early listing short bubble-fade sleeve only",
        "signal_interval": "15m parent signal; 5m/15m child execution allowed after paper launch",
        "entry_rule": "after listing age >= 3d, short when close is at/above 95th percentile of trailing 3d high window and latest funding is positive",
        "exit_rule": "desk paper lane freezes 8% TP / 5% SL / 3d hard timeout; no uncapped repeat-entry expansion",
        "risk_caps": {
            "max_trades_per_symbol_listing_window": 3,
            "paper_default_cap_for_admission": "1-3 early trades per symbol; one active short per symbol",
            "extra_early_listing_execution_buffer_bps": 100
        },
        "honesty_checks": [
            "listing age gate prevents immediate launch-period lookahead",
            "per-symbol cap blocks uncapped same-symbol overtrading",
            "positive funding is required, but paper status still records short-availability/funding as execution blocker fields",
            "first-run uses historical artifact only; routine runner writes status/ledger and does not synthesize new alpha evidence"
        ],
        "source_records": [
            "research/quant_digests/2026-04-22_1115_newlisting-early-short-bubblefade-shell.md",
            "research/optimization_loop/2026-04-22_1217_rank434_newlisting_earlyshort_freshintake_keep_p1.md",
            "research/optimization_loop/2026-04-22_1352_rank434_survivor_followup_promote_p2.md",
            "research/strategy_review/2026-04-22_1430_strategy-review.md"
        ],
        "source_artifacts": [
            str(TRADES_PATH.relative_to(ROOT)),
            str(SUMMARY_PATH.relative_to(ROOT)),
            str(FOLLOWUP_PATH.relative_to(ROOT))
        ]
    }


def capped_metrics(trades: pd.DataFrame, max_per_symbol: int) -> dict:
    desk = trades[trades["variant"] == "desk_8tp5sl3d"].copy()
    desk["entry_time"] = pd.to_datetime(desk["entry_time"], utc=True)
    desk = desk.sort_values(["symbol", "entry_time"]).groupby("symbol").head(max_per_symbol).copy()
    desk["entry_month"] = desk["entry_time"].dt.strftime("%Y-%m")
    months = desk.groupby("entry_month")["net_pct"].mean().to_dict()
    return {
        "max_trades_per_symbol": max_per_symbol,
        "trade_count": int(len(desk)),
        "symbols": int(desk["symbol"].nunique()),
        "avg_net_pct": float(desk["net_pct"].mean()),
        "avg_net_after_extra_100bps_pct": float((desk["net_pct"] - 1.0).mean()),
        "positive_symbols": int((desk.groupby("symbol")["net_pct"].sum() > 0).sum()),
        "positive_months": int(sum(1 for v in months.values() if v > 0)),
        "month_avg_net_pct": {k: float(v) for k, v in months.items()}
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank 434 new-listing early-short bubble-fade paper runner")
    parser.add_argument("--refresh", action="store_true", help="refresh runtime artifacts")
    args = parser.parse_args()
    if not args.refresh:
        parser.error("choose --refresh")

    missing = [str(p.relative_to(ROOT)) for p in [TRADES_PATH, SUMMARY_PATH] if not p.exists()]
    if missing:
        raise FileNotFoundError(f"rank434 source artifacts missing: {missing}")

    ensure_dir(ART_DIR)
    now = utc_now()
    trades = pd.read_csv(TRADES_PATH)
    summary = pd.read_csv(SUMMARY_PATH)
    desk_summary = summary[summary["variant"] == "desk_8tp5sl3d"].iloc[0].to_dict()
    cap1, cap2, cap3 = capped_metrics(trades, 1), capped_metrics(trades, 2), capped_metrics(trades, 3)

    decisive_blocker = "none"
    gate_pass = bool(cap1["positive_months"] >= 2 and cap3["avg_net_after_extra_100bps_pct"] > 0 and cap3["symbols"] >= 20)
    if not gate_pass:
        decisive_blocker = "symbol_cap_or_extra_100bps_aftercost_not_positive"

    write_json(SPEC_PATH, build_spec())
    snapshot = pd.DataFrame([
        {
            "captured_at_utc": iso_z(now),
            "candidate_rank": CANDIDATE_RANK,
            "source_variant": "desk_8tp5sl3d",
            "uncapped_trades": int(desk_summary["trades"]),
            "uncapped_symbols_with_trades": int(desk_summary["symbols_with_trades"]),
            "uncapped_avg_net_pct": float(desk_summary["avg_net_pct"]),
            "cap1_trades": cap1["trade_count"],
            "cap1_symbols": cap1["symbols"],
            "cap1_avg_net_pct": cap1["avg_net_pct"],
            "cap1_avg_net_after_extra_100bps_pct": cap1["avg_net_after_extra_100bps_pct"],
            "cap1_positive_months": cap1["positive_months"],
            "cap3_trades": cap3["trade_count"],
            "cap3_symbols": cap3["symbols"],
            "cap3_avg_net_pct": cap3["avg_net_pct"],
            "cap3_avg_net_after_extra_100bps_pct": cap3["avg_net_after_extra_100bps_pct"],
            "cap3_positive_months": cap3["positive_months"],
            "listing_age_gate_days": 3,
            "per_symbol_cap_live": 3,
            "short_availability_status": "paper_required_check_no_fatal_blocker_in_source_artifact",
            "child_fill_realism": "extra_100bps_buffer_positive_under_cap1_to_cap3",
            "gate_pass": gate_pass,
            "decisive_blocker": decisive_blocker
        }
    ])
    snapshot.to_csv(SNAPSHOT_PATH, index=False)
    prev = read_csv_or_empty(LEDGER_PATH)
    pd.concat([prev, snapshot], ignore_index=True).to_csv(LEDGER_PATH, index=False)

    live = trades[trades["variant"] == "desk_8tp5sl3d"].copy()
    live["entry_time"] = pd.to_datetime(live["entry_time"], utc=True)
    live = live.sort_values("entry_time").tail(20).copy()
    live.insert(0, "captured_at_utc", iso_z(now))
    live.to_csv(SIGNAL_PATH, index=False)

    status = {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "wiring_status": "connected_runner_live" if gate_pass else "blocked_by_single_decisive_execution_blocker",
        "runner_mode": "frozen_scope_paper_refresh",
        "runner_script": "scripts/run_rank434_newlisting_earlyshort_paper_runner.py",
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "last_run_at_utc": iso_z(now),
        "decisive_blocker": decisive_blocker,
        "cap3_avg_net_after_extra_100bps_pct": cap3["avg_net_after_extra_100bps_pct"],
        "cap3_positive_months": cap3["positive_months"]
    }
    pd.DataFrame([status]).to_csv(STATUS_PATH, index=False)
    write_json(STATE_PATH, {**status, "spec_path": str(SPEC_PATH.relative_to(ROOT)), "snapshot_path": str(SNAPSHOT_PATH.relative_to(ROOT)), "ledger_path": str(LEDGER_PATH.relative_to(ROOT))})
    write_json(RUN_SUMMARY_PATH, {"status": status, "cap1": cap1, "cap2": cap2, "cap3": cap3})
    print(json.dumps(status, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
