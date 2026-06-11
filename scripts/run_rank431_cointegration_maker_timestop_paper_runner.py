#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "reports" / "artifacts" / "quant_digests"
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank431_cointegration_maker_timestop_pairs"

SUMMARY_PATH = SOURCE_DIR / "rank431_survivor_followup_proxy_summary_2026-04-21.csv"
TRADES_PATH = SOURCE_DIR / "rank431_survivor_followup_proxy_trades_2026-04-21.csv"
RECENT_PATH = SOURCE_DIR / "rank431_p2_exit_round2_recent7d_crosspair_realism_2026-04-21.csv"

STATUS_PATH = ART_DIR / "rank431_status.csv"
STATE_PATH = ART_DIR / "rank431_state.json"
SPEC_PATH = ART_DIR / "rank431_frozen_launch_spec.json"
LEDGER_PATH = ART_DIR / "rank431_launch_checks.csv"
SNAPSHOT_PATH = ART_DIR / "rank431_current_snapshot.csv"
SIGNAL_PATH = ART_DIR / "rank431_live_signal_snapshot.csv"
RUN_SUMMARY_PATH = ART_DIR / "rank431_last_run_summary.json"

RUNNER_SERVICE = "momentum-rank431-paper-refresh.service"
RUNNER_TIMER = "momentum-rank431-paper-refresh.timer"
CORE_PAIR = "NEARUSDT-ATOMUSDT"
WATCH_PAIR = "AVAXUSDT-SUIUSDT"
REJECTED_PAIR = "AVAXUSDT-ATOMUSDT"
TIME_STOP_BARS = 48
FRICTION_BPS = 16
SIGNAL_INTERVAL = "15m"


def iso_z(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_spec() -> dict:
    return {
        "candidate_id": "rank431_cointegration_maker_first_hard_timestop_pairs",
        "candidate_rank": 431,
        "scope": "15m rolling-admission pair spread fade with maker-first timeout-cross execution; NEAR/ATOM core plus AVAX/SUI secondary watch",
        "signal_interval": SIGNAL_INTERVAL,
        "execution": "maker-first; if maker not filled, timeout-cross adds 4bps extra fill cost",
        "exit": f"zero-cross or structural-break, hard stop {TIME_STOP_BARS} bars (~12h)",
        "friction_roundtrip_bps": FRICTION_BPS,
        "core_pair": CORE_PAIR,
        "secondary_watch_pair": WATCH_PAIR,
        "rejected_pair": REJECTED_PAIR,
        "source_artifacts": [
            "reports/artifacts/quant_digests/rank431_survivor_followup_proxy_summary_2026-04-21.csv",
            "reports/artifacts/quant_digests/rank431_survivor_followup_proxy_trades_2026-04-21.csv",
            "reports/artifacts/quant_digests/rank431_p2_exit_round2_recent7d_crosspair_realism_2026-04-21.csv",
        ],
        "frozen_notes": [
            "Launch runner stays on 15m pair lane; no 5m child-execution expansion.",
            "Core pair is NEAR/ATOM because it keeps positive net across 8/12/16bps and survives day-concentration pressure better.",
            "AVAX/SUI remains live secondary watch because recent-7d cross-pair durability re-opened a second positive pocket.",
            "AVAX/ATOM stays excluded from launch host set because after-cost proxy remains negative.",
        ],
    }


def load_pair_row(df: pd.DataFrame, pair: str) -> pd.Series:
    sub = df[df["pair"] == pair]
    if sub.empty:
        raise RuntimeError(f"missing pair row: {pair}")
    return sub.iloc[0]


def compute_overlap_ratio(trades: pd.DataFrame, pair_a: str, pair_b: str) -> float:
    a = trades[trades["pair"] == pair_a].copy()
    b = trades[trades["pair"] == pair_b].copy()
    if a.empty or b.empty:
        return 0.0
    a["entry_time"] = pd.to_datetime(a["entry_time"], utc=True)
    a["exit_time"] = pd.to_datetime(a["exit_time"], utc=True)
    b["entry_time"] = pd.to_datetime(b["entry_time"], utc=True)
    b["exit_time"] = pd.to_datetime(b["exit_time"], utc=True)
    overlaps = 0
    for _, row in a.iterrows():
        mask = (b["entry_time"] <= row["exit_time"]) & (b["exit_time"] >= row["entry_time"])
        if bool(mask.any()):
            overlaps += 1
    return overlaps / len(a)


def latest_pair_trade(trades: pd.DataFrame, pair: str) -> pd.Series:
    sub = trades[trades["pair"] == pair].copy()
    if sub.empty:
        raise RuntimeError(f"missing trade rows: {pair}")
    sub["entry_time"] = pd.to_datetime(sub["entry_time"], utc=True)
    sub = sub.sort_values("entry_time")
    return sub.iloc[-1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank431 cointegration maker-first hard time-stop paper runner")
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    if not args.refresh:
        parser.error("choose --refresh")

    required = [SUMMARY_PATH, TRADES_PATH, RECENT_PATH]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError(f"rank431 source artifacts missing: {missing}")

    ensure_dir(ART_DIR)
    now = datetime.now(timezone.utc)

    summary = pd.read_csv(SUMMARY_PATH)
    trades = pd.read_csv(TRADES_PATH)
    recent = pd.read_csv(RECENT_PATH)

    core = load_pair_row(summary, CORE_PAIR)
    watch = load_pair_row(summary, WATCH_PAIR)
    rejected = load_pair_row(summary, REJECTED_PAIR)
    core_recent = load_pair_row(recent, CORE_PAIR)
    watch_recent = load_pair_row(recent, WATCH_PAIR)

    overlap_ratio = compute_overlap_ratio(trades, WATCH_PAIR, CORE_PAIR)
    core_last = latest_pair_trade(trades, CORE_PAIR)
    watch_last = latest_pair_trade(trades, WATCH_PAIR)

    gate_pass = bool(
        float(core["net_mean_16bps"]) > 0
        and float(watch_recent["net16_mean"]) > 0
        and int(core["trades"]) >= 20
        and int(watch_recent["trades_recent7d"]) >= 10
    )
    blocker = "none" if gate_pass else "core_or_secondary_pair_failed_launch_gate"

    spec = build_spec()
    write_json(SPEC_PATH, spec)

    signal_snapshot = trades[trades["pair"].isin([CORE_PAIR, WATCH_PAIR])].copy()
    signal_snapshot["captured_at_utc"] = iso_z(now)
    signal_snapshot.to_csv(SIGNAL_PATH, index=False)

    snapshot = pd.DataFrame([
        {
            "captured_at_utc": iso_z(now),
            "candidate_rank": 431,
            "signal_interval": SIGNAL_INTERVAL,
            "execution_mode": "maker_first_timeout_cross",
            "time_stop_bars": TIME_STOP_BARS,
            "friction_roundtrip_bps": FRICTION_BPS,
            "core_pair": CORE_PAIR,
            "core_trades": int(core["trades"]),
            "core_selection_count_28d_daily": int(core["pair_selection_count_28d_daily"]),
            "core_maker_fill_rate": float(core["maker_fill_rate"]),
            "core_timeout_cross_rate": float(core["timeout_cross_rate"]),
            "core_net_mean_8bps": float(core["net_mean_8bps"]),
            "core_net_mean_12bps": float(core["net_mean_12bps"]),
            "core_net_mean_16bps": float(core["net_mean_16bps"]),
            "core_recent7d_trades": int(core_recent["trades_recent7d"]),
            "core_recent7d_net8_mean": float(core_recent["net8_mean"]),
            "core_recent7d_net12_mean": float(core_recent["net12_mean"]),
            "core_recent7d_net16_mean": float(core_recent["net16_mean"]),
            "core_latest_entry_time_utc": pd.to_datetime(core_last["entry_time"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "watch_pair": WATCH_PAIR,
            "watch_trades": int(watch["trades"]),
            "watch_selection_count_28d_daily": int(watch["pair_selection_count_28d_daily"]),
            "watch_maker_fill_rate": float(watch["maker_fill_rate"]),
            "watch_timeout_cross_rate": float(watch["timeout_cross_rate"]),
            "watch_net_mean_8bps": float(watch["net_mean_8bps"]),
            "watch_net_mean_12bps": float(watch["net_mean_12bps"]),
            "watch_net_mean_16bps": float(watch["net_mean_16bps"]),
            "watch_recent7d_trades": int(watch_recent["trades_recent7d"]),
            "watch_recent7d_net8_mean": float(watch_recent["net8_mean"]),
            "watch_recent7d_net12_mean": float(watch_recent["net12_mean"]),
            "watch_recent7d_net16_mean": float(watch_recent["net16_mean"]),
            "watch_latest_entry_time_utc": pd.to_datetime(watch_last["entry_time"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "cross_pair_overlap_ratio": overlap_ratio,
            "rejected_pair": REJECTED_PAIR,
            "rejected_net_mean_16bps": float(rejected["net_mean_16bps"]),
            "gate_pass": gate_pass,
            "decisive_blocker": blocker,
        }
    ])
    snapshot.to_csv(SNAPSHOT_PATH, index=False)

    ledger_cols = list(snapshot.columns)
    prev = pd.read_csv(LEDGER_PATH) if LEDGER_PATH.exists() and LEDGER_PATH.stat().st_size > 0 else pd.DataFrame(columns=ledger_cols)
    pd.concat([prev, snapshot[ledger_cols]], ignore_index=True).to_csv(LEDGER_PATH, index=False)

    status = {
        "candidate_id": spec["candidate_id"],
        "candidate_rank": 431,
        "stage": "paper_runner_ready",
        "wiring_status": "connected_runner_live" if gate_pass else "blocked",
        "runner_mode": "frozen_scope_paper_refresh",
        "runner_script": "scripts/run_rank431_cointegration_maker_timestop_paper_runner.py",
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "scope": spec["scope"],
        "signal_interval": SIGNAL_INTERVAL,
        "execution": spec["execution"],
        "exit": spec["exit"],
        "core_pair": CORE_PAIR,
        "core_net_mean_16bps": float(core["net_mean_16bps"]),
        "core_recent7d_net16_mean": float(core_recent["net16_mean"]),
        "watch_pair": WATCH_PAIR,
        "watch_net_mean_16bps": float(watch["net_mean_16bps"]),
        "watch_recent7d_net16_mean": float(watch_recent["net16_mean"]),
        "cross_pair_overlap_ratio": overlap_ratio,
        "rejected_pair": REJECTED_PAIR,
        "rejected_net_mean_16bps": float(rejected["net_mean_16bps"]),
        "updated_at_utc": iso_z(now),
        "decisive_blocker": blocker,
    }
    pd.DataFrame([status]).to_csv(STATUS_PATH, index=False)

    state = {
        "candidate_id": spec["candidate_id"],
        "candidate_rank": 431,
        "wiring_status": status["wiring_status"],
        "runner_mode": status["runner_mode"],
        "runner_script": status["runner_script"],
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "scope": status["scope"],
        "signal_interval": SIGNAL_INTERVAL,
        "execution": status["execution"],
        "exit": status["exit"],
        "core_pair": CORE_PAIR,
        "core_net_mean_16bps": float(core["net_mean_16bps"]),
        "core_recent7d_net16_mean": float(core_recent["net16_mean"]),
        "watch_pair": WATCH_PAIR,
        "watch_net_mean_16bps": float(watch["net_mean_16bps"]),
        "watch_recent7d_net16_mean": float(watch_recent["net16_mean"]),
        "cross_pair_overlap_ratio": overlap_ratio,
        "rejected_pair": REJECTED_PAIR,
        "rejected_net_mean_16bps": float(rejected["net_mean_16bps"]),
        "decisive_blocker": blocker,
        "source_artifacts": spec["source_artifacts"],
        "last_run_at_utc": iso_z(now),
    }
    write_json(STATE_PATH, state)

    run_summary = {
        "run_at_utc": iso_z(now),
        "runner": "rank431_cointegration_maker_timestop_paper_runner",
        "wiring_status": status["wiring_status"],
        "decisive_blocker": blocker,
        "status_path": str(STATUS_PATH.relative_to(ROOT)),
        "state_path": str(STATE_PATH.relative_to(ROOT)),
        "ledger_path": str(LEDGER_PATH.relative_to(ROOT)),
        "snapshot_path": str(SNAPSHOT_PATH.relative_to(ROOT)),
        "signal_path": str(SIGNAL_PATH.relative_to(ROOT)),
        "spec_path": str(SPEC_PATH.relative_to(ROOT)),
    }
    write_json(RUN_SUMMARY_PATH, run_summary)
    print(json.dumps(run_summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
