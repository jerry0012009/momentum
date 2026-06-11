#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "reports" / "artifacts" / "optimization_loop"
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank405_multienvelope_overshoot"

SUMMARY_PATH = SOURCE_DIR / "rank405_p2_exit_nextbar_capacity_summary.csv"
DETAIL_PATH = SOURCE_DIR / "rank405_p2_exit_nextbar_capacity_detail.csv"

STATUS_PATH = ART_DIR / "rank405_status.csv"
STATE_PATH = ART_DIR / "rank405_state.json"
SPEC_PATH = ART_DIR / "rank405_frozen_launch_spec.json"
LEDGER_PATH = ART_DIR / "rank405_launch_checks.csv"
SNAPSHOT_PATH = ART_DIR / "rank405_current_snapshot.csv"
RUN_SUMMARY_PATH = ART_DIR / "rank405_last_run_summary.json"

RUNNER_SERVICE = "momentum-rank405-paper-refresh.service"
RUNNER_TIMER = "momentum-rank405-paper-refresh.timer"


def iso_z(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def pick_metric(df: pd.DataFrame, mode: str, symbol: str, col: str) -> float:
    row = df[(df["mode"] == mode) & (df["symbol"] == symbol)]
    if row.empty:
        raise ValueError(f"missing summary row: mode={mode} symbol={symbol}")
    return float(row.iloc[0][col])


def pick_trades(df: pd.DataFrame, mode: str, symbol: str) -> int:
    return int(pick_metric(df, mode, symbol, "trades"))


def build_spec() -> dict:
    return {
        "candidate_id": "rank405_multienvelope_overshoot_average_return_shell",
        "candidate_rank": 405,
        "scope": "15m wall-clock scaled multienvelope overshoot mean-reversion shell (BTC+ETH)",
        "signal_interval": "15m",
        "entry_delay": "1 bar (next_open)",
        "capacity_cap": "max 2 envelope legs per trade",
        "cost_assumption_bps": {"entry": 2, "exit": 5},
        "frozen_trigger": {
            "execution_lane": "nextbar_cap2",
            "capacity_layers_max": 2,
            "symbols": ["BTCUSDT", "ETHUSDT"],
        },
        "execution_honesty": "trigger from closed-bar data only; execute at next-bar open; cap entries to max two layers",
        "source_artifacts": [
            "reports/artifacts/optimization_loop/rank405_p2_exit_nextbar_capacity_summary.csv",
            "reports/artifacts/optimization_loop/rank405_p2_exit_nextbar_capacity_detail.csv",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank405 multienvelope overshoot paper runner")
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    if not args.refresh:
        parser.error("choose --refresh")

    required = [SUMMARY_PATH, DETAIL_PATH]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError(f"rank405 source artifacts missing: {missing}")

    summary = pd.read_csv(SUMMARY_PATH)
    detail = pd.read_csv(DETAIL_PATH)

    pooled_cap3 = pick_metric(summary, "nextbar_cap3_baseline", "POOLED", "net_mean_bps")
    pooled_cap2 = pick_metric(summary, "nextbar_cap2", "POOLED", "net_mean_bps")
    btc_cap2 = pick_metric(summary, "nextbar_cap2", "BTCUSDT", "net_mean_bps")
    eth_cap2 = pick_metric(summary, "nextbar_cap2", "ETHUSDT", "net_mean_bps")
    pooled_trades = pick_trades(summary, "nextbar_cap2", "POOLED")

    gate_pass = bool(pooled_cap2 > 0 and pooled_trades >= 100)
    blocker = "none" if gate_pass else "cap2_pooled_net_not_positive_or_sample_too_small"

    ensure_dir(ART_DIR)
    now = datetime.now(timezone.utc)

    spec = build_spec()
    write_json(SPEC_PATH, spec)

    snapshot = pd.DataFrame([
        {
            "captured_at_utc": iso_z(now),
            "candidate_rank": 405,
            "signal_interval": "15m",
            "entry_delay": "1_bar",
            "capacity_layers_max": 2,
            "pooled_nextbar_cap3_net_mean_bps": pooled_cap3,
            "pooled_nextbar_cap2_net_mean_bps": pooled_cap2,
            "btc_nextbar_cap2_net_mean_bps": btc_cap2,
            "eth_nextbar_cap2_net_mean_bps": eth_cap2,
            "pooled_nextbar_cap2_trades": pooled_trades,
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
        "candidate_id": "rank405_multienvelope_overshoot_average_return_shell",
        "candidate_rank": 405,
        "stage": "paper_runner_ready",
        "wiring_status": "connected_runner_live" if gate_pass else "blocked",
        "runner_mode": "frozen_scope_paper_refresh",
        "runner_script": "scripts/run_rank405_multienvelope_overshoot_paper_runner.py",
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "scope": "15m wall-clock scaled multienvelope overshoot mean-reversion shell (BTC+ETH)",
        "signal_interval": "15m",
        "entry_delay": "1_bar",
        "capacity_layers_max": 2,
        "pooled_nextbar_cap3_net_mean_bps": pooled_cap3,
        "pooled_nextbar_cap2_net_mean_bps": pooled_cap2,
        "btc_nextbar_cap2_net_mean_bps": btc_cap2,
        "eth_nextbar_cap2_net_mean_bps": eth_cap2,
        "pooled_nextbar_cap2_trades": pooled_trades,
        "updated_at_utc": iso_z(now),
        "decisive_blocker": blocker,
    }
    pd.DataFrame([status]).to_csv(STATUS_PATH, index=False)

    state = {
        "candidate_id": status["candidate_id"],
        "candidate_rank": 405,
        "wiring_status": status["wiring_status"],
        "runner_mode": status["runner_mode"],
        "runner_script": status["runner_script"],
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "scope": status["scope"],
        "signal_interval": status["signal_interval"],
        "entry_delay": status["entry_delay"],
        "capacity_layers_max": 2,
        "pooled_nextbar_cap3_net_mean_bps": pooled_cap3,
        "pooled_nextbar_cap2_net_mean_bps": pooled_cap2,
        "btc_nextbar_cap2_net_mean_bps": btc_cap2,
        "eth_nextbar_cap2_net_mean_bps": eth_cap2,
        "pooled_nextbar_cap2_trades": pooled_trades,
        "decisive_blocker": blocker,
        "source_artifacts": spec["source_artifacts"],
        "last_run_at_utc": iso_z(now),
    }
    write_json(STATE_PATH, state)

    run_summary = {
        "run_at_utc": iso_z(now),
        "runner": "rank405_multienvelope_overshoot_paper_runner",
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
