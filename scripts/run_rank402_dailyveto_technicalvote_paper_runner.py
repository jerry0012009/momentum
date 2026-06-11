#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "reports" / "artifacts" / "quant_digests"
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank402_dailyveto_technicalvote"

SUMMARY_PATH = SOURCE_DIR / "bybit_technical_bot_binance_probe_summary_2026-04-14.csv"
DETAIL_PATH = SOURCE_DIR / "bybit_technical_bot_binance_probe_detail_2026-04-14.csv"
ADMISSION_PATH = SOURCE_DIR / "rank402_p2_exit_admission_delaycheck_2026-04-14.csv"

STATUS_PATH = ART_DIR / "rank402_status.csv"
STATE_PATH = ART_DIR / "rank402_state.json"
SPEC_PATH = ART_DIR / "rank402_frozen_launch_spec.json"
LEDGER_PATH = ART_DIR / "rank402_launch_checks.csv"
SNAPSHOT_PATH = ART_DIR / "rank402_current_snapshot.csv"
RUN_SUMMARY_PATH = ART_DIR / "rank402_last_run_summary.json"

RUNNER_SERVICE = "momentum-rank402-paper-refresh.service"
RUNNER_TIMER = "momentum-rank402-paper-refresh.timer"


def iso_z(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def get_metric(df: pd.DataFrame, symbol: str, daily: bool, entry: str, col: str) -> float:
    picked = df[
        (df["symbol"] == symbol)
        & (df["use_daily_filter"] == daily)
        & (df["entry_mode"] == entry)
    ]
    if picked.empty:
        raise ValueError(f"missing summary row: symbol={symbol} daily={daily} entry={entry}")
    return float(picked.iloc[0][col])


def get_metric_with_fallback_entry(
    df: pd.DataFrame,
    symbol: str,
    daily: bool,
    entry_candidates: list[str],
    col: str,
) -> float:
    for entry in entry_candidates:
        picked = df[
            (df["symbol"] == symbol)
            & (df["use_daily_filter"] == daily)
            & (df["entry_mode"] == entry)
        ]
        if not picked.empty:
            return float(picked.iloc[0][col])
    raise ValueError(
        f"missing summary row: symbol={symbol} daily={daily} entries={entry_candidates}"
    )


def build_spec() -> dict:
    return {
        "candidate_id": "rank402_dailyveto_technicalvote_continuation_shell",
        "candidate_rank": 402,
        "scope": "15m technical-vote continuation with daily EMA20/50 trend veto (score 3-4 primary)",
        "signal_interval": "15m",
        "entry_delay": "1 bar (next_open baseline)",
        "hold_bars": 24,
        "cost_lanes_bps_per_side": [2, 4, 6],
        "frozen_trigger": {
            "use_daily_filter": True,
            "score_bucket_primary": "3-4",
            "score_bucket_veto": ">=5",
            "entry_mode": "next_open",
        },
        "execution_honesty": "signal computed from closed bars only; entry delayed to next bar open; no same-window forward price in trigger",
        "source_artifacts": [
            "reports/artifacts/quant_digests/bybit_technical_bot_binance_probe_summary_2026-04-14.csv",
            "reports/artifacts/quant_digests/bybit_technical_bot_binance_probe_detail_2026-04-14.csv",
            "reports/artifacts/quant_digests/rank402_p2_exit_admission_delaycheck_2026-04-14.csv",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank402 daily-veto technical-vote paper runner")
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    if not args.refresh:
        parser.error("choose --refresh")

    required = [SUMMARY_PATH, DETAIL_PATH, ADMISSION_PATH]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError(f"rank402 source artifacts missing: {missing}")

    summary = pd.read_csv(SUMMARY_PATH)
    detail = pd.read_csv(DETAIL_PATH)
    admission = pd.read_csv(ADMISSION_PATH)

    all_next_open = get_metric(summary, "ALL", True, "next_open", "avg_net_bps")
    score34_next_open = get_metric(summary, "SCORE_3-4", True, "next_open", "avg_net_bps")
    score5_next_open = get_metric(summary, "SCORE_5", True, "next_open", "avg_net_bps")
    all_without_daily = get_metric_with_fallback_entry(
        summary,
        "ALL",
        False,
        ["next_open", "repo_prev_close"],
        "avg_net_bps",
    )
    score34_trades = int(get_metric(summary, "SCORE_3-4", True, "next_open", "trades"))

    if "lane" in admission.columns:
        delay_row = admission[admission["lane"] == "score_3_4_next_open_plus1bar"]
    elif "slice" in admission.columns:
        delay_row = admission[admission["slice"] == "delay2_score3-4"]
    else:
        raise ValueError("rank402 admission csv missing lane/slice column")
    if delay_row.empty:
        raise ValueError("rank402 admission delay lane (plus1bar proxy) missing")
    delay_net = float(delay_row.iloc[0]["avg_net_bps"])
    delay_trades = int(delay_row.iloc[0]["trades"])

    gate_pass = bool(score34_next_open > 0 and delay_net > 0 and score34_trades >= 300)
    blocker = "none" if gate_pass else "score34_or_delay_lane_not_positive_or_too_few_trades"

    ensure_dir(ART_DIR)
    now = datetime.now(timezone.utc)

    spec = build_spec()
    write_json(SPEC_PATH, spec)

    snapshot = pd.DataFrame([
        {
            "captured_at_utc": iso_z(now),
            "candidate_rank": 402,
            "signal_interval": "15m",
            "entry_delay": "1_bar",
            "hold_bars": 24,
            "daily_filter_on_all_nextopen_avg_net_bps": all_next_open,
            "daily_filter_on_score3_4_nextopen_avg_net_bps": score34_next_open,
            "daily_filter_on_score5_nextopen_avg_net_bps": score5_next_open,
            "daily_filter_off_all_nextopen_avg_net_bps": all_without_daily,
            "delay_plus1bar_score3_4_avg_net_bps": delay_net,
            "score3_4_nextopen_trades": score34_trades,
            "delay_plus1bar_score3_4_trades": delay_trades,
            "detail_rows": int(len(detail)),
            "gate_pass": gate_pass,
            "decisive_blocker": blocker,
        }
    ])
    snapshot.to_csv(SNAPSHOT_PATH, index=False)

    ledger_cols = list(snapshot.columns)
    prev = pd.read_csv(LEDGER_PATH) if LEDGER_PATH.exists() and LEDGER_PATH.stat().st_size > 0 else pd.DataFrame(columns=ledger_cols)
    pd.concat([prev, snapshot[ledger_cols]], ignore_index=True).to_csv(LEDGER_PATH, index=False)

    status = {
        "candidate_id": "rank402_dailyveto_technicalvote_continuation_shell",
        "candidate_rank": 402,
        "stage": "paper_runner_ready",
        "wiring_status": "connected_runner_live" if gate_pass else "blocked",
        "runner_mode": "frozen_scope_paper_refresh",
        "runner_script": "scripts/run_rank402_dailyveto_technicalvote_paper_runner.py",
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "scope": "15m technical-vote continuation with daily trend veto",
        "signal_interval": "15m",
        "entry_delay": "1_bar",
        "hold_bars": 24,
        "daily_filter_on_score3_4_nextopen_avg_net_bps": score34_next_open,
        "delay_plus1bar_score3_4_avg_net_bps": delay_net,
        "daily_filter_off_all_nextopen_avg_net_bps": all_without_daily,
        "updated_at_utc": iso_z(now),
        "decisive_blocker": blocker,
    }
    pd.DataFrame([status]).to_csv(STATUS_PATH, index=False)

    state = {
        "candidate_id": status["candidate_id"],
        "candidate_rank": 402,
        "wiring_status": status["wiring_status"],
        "runner_mode": status["runner_mode"],
        "runner_script": status["runner_script"],
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "scope": status["scope"],
        "signal_interval": status["signal_interval"],
        "entry_delay": status["entry_delay"],
        "hold_bars": status["hold_bars"],
        "daily_filter_on_score3_4_nextopen_avg_net_bps": score34_next_open,
        "delay_plus1bar_score3_4_avg_net_bps": delay_net,
        "daily_filter_off_all_nextopen_avg_net_bps": all_without_daily,
        "decisive_blocker": blocker,
        "source_artifacts": spec["source_artifacts"],
        "last_run_at_utc": iso_z(now),
    }
    write_json(STATE_PATH, state)

    run_summary = {
        "run_at_utc": iso_z(now),
        "runner": "rank402_dailyveto_technicalvote_paper_runner",
        "wiring_status": status["wiring_status"],
        "decisive_blocker": blocker,
        "status_path": str(STATUS_PATH.relative_to(ROOT)),
        "state_path": str(STATE_PATH.relative_to(ROOT)),
        "ledger_path": str(LEDGER_PATH.relative_to(ROOT)),
        "snapshot_path": str(SNAPSHOT_PATH.relative_to(ROOT)),
        "spec_path": str(SPEC_PATH.relative_to(ROOT)),
    }
    write_json(RUN_SUMMARY_PATH, run_summary)
    print(json.dumps(run_summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
