#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "reports" / "artifacts" / "quant_digests"
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank424_cointegration_spreadfade"

ROUTER_PATH = SOURCE_DIR / "2026-04-19_cointegration_pairs_probe_router_15m.csv"
SUMMARY_PATH = SOURCE_DIR / "2026-04-19_cointegration_pairs_probe_summary.json"

STATUS_PATH = ART_DIR / "rank424_status.csv"
STATE_PATH = ART_DIR / "rank424_state.json"
SPEC_PATH = ART_DIR / "rank424_frozen_launch_spec.json"
LEDGER_PATH = ART_DIR / "rank424_launch_checks.csv"
SNAPSHOT_PATH = ART_DIR / "rank424_current_snapshot.csv"
SIGNAL_PATH = ART_DIR / "rank424_live_signal_snapshot.csv"
RUN_SUMMARY_PATH = ART_DIR / "rank424_last_run_summary.json"

RUNNER_SERVICE = "momentum-rank424-paper-refresh.service"
RUNNER_TIMER = "momentum-rank424-paper-refresh.timer"
CORE_PAIR = "SOLUSDT/LTCUSDT"
WATCH_PAIR = "LINKUSDT/AVAXUSDT"
EXCLUDED_PAIR = "LINKUSDT/LTCUSDT"
TIME_STOP_BARS = 12
FRICTION_BPS = 16


def iso_z(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_summary(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_spec() -> dict:
    return {
        "candidate_id": "rank424_cointegration_first_pair_admission_spreadfade",
        "candidate_rank": 424,
        "scope": "15m bar-close strongest residual z-score spread fade; SOL/LTC core, LINK/AVAX secondary-watch, LINK/LTC excluded",
        "signal_interval": "15m",
        "execution": "next-bar conservative paper fill",
        "exit": f"fixed {TIME_STOP_BARS} bars time-stop (~3h)",
        "friction_roundtrip_bps": FRICTION_BPS,
        "core_pair": CORE_PAIR,
        "secondary_watch_pair": WATCH_PAIR,
        "excluded_pair": EXCLUDED_PAIR,
        "source_artifacts": [
            "reports/artifacts/quant_digests/2026-04-19_cointegration_pairs_probe_router_15m.csv",
            "reports/artifacts/quant_digests/2026-04-19_cointegration_pairs_probe_summary.json",
        ],
        "frozen_notes": [
            "Do not use 5m child execution as launch improvement; 5m child probe is negative.",
            "Primary live lane is SOL/LTC only; LINK/AVAX remains secondary/watch evidence.",
        ],
    }


def pair_metrics(df: pd.DataFrame, pair: str) -> dict:
    sub = df[df["pair"] == pair].copy()
    if sub.empty:
        raise RuntimeError(f"missing pair rows: {pair}")
    last = pd.to_datetime(sub["ts"], utc=True).max()
    gross12 = float(sub["ret_12"].mean())
    return {
        "pair": pair,
        "signals_n": int(len(sub)),
        "gross_mean_bps_12bar": gross12,
        "net_mean_bps_12bar_at_16": gross12 - FRICTION_BPS,
        "latest_signal_ts_utc": iso_z(last.to_pydatetime()),
        "latest_abs_z": float(sub.loc[pd.to_datetime(sub["ts"], utc=True).idxmax(), "abs_z"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank424 cointegration spread fade paper runner")
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    if not args.refresh:
        parser.error("choose --refresh")

    required = [ROUTER_PATH, SUMMARY_PATH]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError(f"rank424 source artifacts missing: {missing}")

    ensure_dir(ART_DIR)
    now = datetime.now(timezone.utc)
    router = pd.read_csv(ROUTER_PATH)
    summary = load_summary(SUMMARY_PATH)

    core = pair_metrics(router, CORE_PAIR)
    watch = pair_metrics(router, WATCH_PAIR)
    excluded = pair_metrics(router, EXCLUDED_PAIR)

    child_5m_mean = float(summary["strongest_router_summary_5mchild"]["ret5_12"]["mean_bps"])
    gate_pass = bool(core["net_mean_bps_12bar_at_16"] > 0 and core["signals_n"] >= 100 and child_5m_mean < 0)
    blocker = "none" if gate_pass else "core_pair_after_cost_not_positive_or_sample_too_small"

    spec = build_spec()
    write_json(SPEC_PATH, spec)

    signal_snapshot = router[router["pair"].isin([CORE_PAIR, WATCH_PAIR])].copy()
    signal_snapshot["captured_at_utc"] = iso_z(now)
    signal_snapshot.to_csv(SIGNAL_PATH, index=False)

    snapshot = pd.DataFrame([
        {
            "captured_at_utc": iso_z(now),
            "candidate_rank": 424,
            "signal_interval": "15m",
            "execution_mode": "next_bar_conservative_fill",
            "time_stop_bars": TIME_STOP_BARS,
            "friction_roundtrip_bps": FRICTION_BPS,
            "core_pair": CORE_PAIR,
            "core_signals_n": core["signals_n"],
            "core_gross_mean_bps_12bar": core["gross_mean_bps_12bar"],
            "core_net_mean_bps_12bar_at_16": core["net_mean_bps_12bar_at_16"],
            "core_latest_signal_ts_utc": core["latest_signal_ts_utc"],
            "watch_pair": WATCH_PAIR,
            "watch_signals_n": watch["signals_n"],
            "watch_gross_mean_bps_12bar": watch["gross_mean_bps_12bar"],
            "watch_net_mean_bps_12bar_at_16": watch["net_mean_bps_12bar_at_16"],
            "excluded_pair": EXCLUDED_PAIR,
            "excluded_net_mean_bps_12bar_at_16": excluded["net_mean_bps_12bar_at_16"],
            "router_5m_child_mean_bps_12": child_5m_mean,
            "gate_pass": gate_pass,
            "decisive_blocker": blocker,
        }
    ])
    snapshot.to_csv(SNAPSHOT_PATH, index=False)

    ledger_cols = list(snapshot.columns)
    prev = pd.read_csv(LEDGER_PATH) if LEDGER_PATH.exists() and LEDGER_PATH.stat().st_size > 0 else pd.DataFrame(columns=ledger_cols)
    pd.concat([prev, snapshot[ledger_cols]], ignore_index=True).to_csv(LEDGER_PATH, index=False)

    status = {
        "candidate_id": "rank424_cointegration_first_pair_admission_spreadfade",
        "candidate_rank": 424,
        "stage": "paper_runner_ready",
        "wiring_status": "connected_runner_live" if gate_pass else "blocked",
        "runner_mode": "frozen_scope_paper_refresh",
        "runner_script": "scripts/run_rank424_cointegration_spreadfade_paper_runner.py",
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "scope": spec["scope"],
        "signal_interval": "15m",
        "execution": spec["execution"],
        "exit": spec["exit"],
        "core_pair": CORE_PAIR,
        "core_signals_n": core["signals_n"],
        "core_net_mean_bps_12bar_at_16": core["net_mean_bps_12bar_at_16"],
        "watch_pair": WATCH_PAIR,
        "watch_net_mean_bps_12bar_at_16": watch["net_mean_bps_12bar_at_16"],
        "excluded_pair": EXCLUDED_PAIR,
        "excluded_net_mean_bps_12bar_at_16": excluded["net_mean_bps_12bar_at_16"],
        "router_5m_child_mean_bps_12": child_5m_mean,
        "updated_at_utc": iso_z(now),
        "decisive_blocker": blocker,
    }
    pd.DataFrame([status]).to_csv(STATUS_PATH, index=False)

    state = {
        "candidate_id": status["candidate_id"],
        "candidate_rank": 424,
        "wiring_status": status["wiring_status"],
        "runner_mode": status["runner_mode"],
        "runner_script": status["runner_script"],
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "scope": status["scope"],
        "signal_interval": status["signal_interval"],
        "execution": status["execution"],
        "exit": status["exit"],
        "core_pair": CORE_PAIR,
        "core_signals_n": core["signals_n"],
        "core_net_mean_bps_12bar_at_16": core["net_mean_bps_12bar_at_16"],
        "watch_pair": WATCH_PAIR,
        "watch_net_mean_bps_12bar_at_16": watch["net_mean_bps_12bar_at_16"],
        "excluded_pair": EXCLUDED_PAIR,
        "excluded_net_mean_bps_12bar_at_16": excluded["net_mean_bps_12bar_at_16"],
        "router_5m_child_mean_bps_12": child_5m_mean,
        "decisive_blocker": blocker,
        "source_artifacts": spec["source_artifacts"],
        "last_run_at_utc": iso_z(now),
    }
    write_json(STATE_PATH, state)

    run_summary = {
        "run_at_utc": iso_z(now),
        "runner": "rank424_cointegration_spreadfade_paper_runner",
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
