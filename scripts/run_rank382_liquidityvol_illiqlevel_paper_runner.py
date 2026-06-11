#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank382_liquidityvol_illiqlevel"

SUMMARY_PATH = ROOT / "reports" / "artifacts" / "literature" / "liquidity_volatility_illiqlevel_probe_summary_2026-04-11.csv"
CAPACITY_PATH = ROOT / "reports" / "artifacts" / "optimization_loop" / "rank382_filladjusted_capacity_check_2026-04-11.csv"
HONESTY_PATH = ROOT / "reports" / "artifacts" / "optimization_loop" / "rank382_p2_exit_honesty_delay_friction_consistency_2026-04-11.csv"

STATUS_PATH = ART_DIR / "rank382_status.csv"
STATE_PATH = ART_DIR / "rank382_state.json"
SPEC_PATH = ART_DIR / "rank382_frozen_launch_spec.json"
LEDGER_PATH = ART_DIR / "rank382_launch_checks.csv"
SNAPSHOT_PATH = ART_DIR / "rank382_current_snapshot.csv"
RUN_SUMMARY_PATH = ART_DIR / "rank382_last_run_summary.json"

RUNNER_SERVICE = "momentum-rank382-paper-refresh.service"
RUNNER_TIMER = "momentum-rank382-paper-refresh.timer"


def iso_z(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_spec() -> dict:
    return {
        "candidate_id": "rank382_liquidityvol_x_illiqlevel_xs",
        "candidate_rank": 382,
        "scope": "Binance USD-M 15m cross-section; fixed universe top25_30d_quotevol; lag1 execution; 1h hold",
        "signal": "score = z(liquidity_volatility_proxy) + z(illiquidity_level_proxy)",
        "execution_gate": "net_bps_24h_lag1_10bps > 0 AND net_bps_adv_0p25pct > 0",
        "capacity_gate": "participation <= 0.25% bar ADV",
        "source_artifacts": [
            "reports/artifacts/literature/liquidity_volatility_illiqlevel_probe_summary_2026-04-11.csv",
            "reports/artifacts/optimization_loop/rank382_filladjusted_capacity_check_2026-04-11.csv",
            "reports/artifacts/optimization_loop/rank382_p2_exit_honesty_delay_friction_consistency_2026-04-11.csv",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank382 liquidity-volatility x illiquidity-level paper runner")
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    if not args.refresh:
        parser.error("choose --refresh")

    required = [SUMMARY_PATH, CAPACITY_PATH, HONESTY_PATH]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError(f"rank382 source artifacts missing: {missing}")

    ensure_dir(ART_DIR)
    now = datetime.now(timezone.utc)

    spec = build_spec()
    write_json(SPEC_PATH, spec)

    summary = pd.read_csv(SUMMARY_PATH)
    capacity = pd.read_csv(CAPACITY_PATH)
    honesty = pd.read_csv(HONESTY_PATH)

    lane = summary[(summary["universe"] == "top25_30d_quotevol") & (summary["window"] == "24h")].copy()
    if lane.empty:
        raise RuntimeError("rank382 summary missing top25_30d_quotevol 24h lane")
    lane = lane.iloc[0]

    lag1_10 = honesty[(honesty["check"] == "delay_friction_consistency") & (honesty["mode"] == "lag1_exec_from_digest_spec") & (honesty["window"] == "24h") & (honesty["friction_bps"] == 10.0)].copy()
    if lag1_10.empty:
        raise RuntimeError("rank382 honesty artifact missing lag1 24h at 10bps row")
    lag1_10 = lag1_10.iloc[0]

    cap_025 = capacity[(capacity["tier"] == "0.25% bar ADV participation") & (capacity["assumed_roundtrip_cost_bps"] == 10)].copy()
    if cap_025.empty:
        raise RuntimeError("rank382 capacity artifact missing 0.25% ADV 10bps row")
    cap_025 = cap_025.iloc[0]

    gate_pass = bool(float(lag1_10["net_bps_per_1h"]) > 0 and float(cap_025["net_alpha_bps_per_1h"]) > 0)
    blocker = "none" if gate_pass else "lag1_10bps_or_0p25adv_gate_failed"

    snapshot = pd.DataFrame([
        {
            "captured_at_utc": iso_z(now),
            "candidate_rank": 382,
            "universe": "top25_30d_quotevol",
            "signal_interval": "15m",
            "hold_window": "1h",
            "execution_mode": "lag1",
            "friction_bps": 10.0,
            "capacity_tier": "<=0.25% bar ADV",
            "gross_bps_per_1h": float(lane["mean_ls_bps"]),
            "lag1_10bps_net_bps_per_1h": float(lag1_10["net_bps_per_1h"]),
            "capacity_0p25_net_bps_per_1h": float(cap_025["net_alpha_bps_per_1h"]),
            "estimated_max_notional_per_15m_usd": float(cap_025["est_max_notional_per_15m_usd"]),
            "t_stat": float(lane["t_ls"]),
            "n_obs": int(lane["n_obs"]),
            "gate_pass": gate_pass,
            "decisive_blocker": blocker,
        }
    ])
    snapshot.to_csv(SNAPSHOT_PATH, index=False)

    ledger_cols = list(snapshot.columns)
    prev = pd.read_csv(LEDGER_PATH) if LEDGER_PATH.exists() and LEDGER_PATH.stat().st_size > 0 else pd.DataFrame(columns=ledger_cols)
    ledger = pd.concat([prev, snapshot[ledger_cols]], ignore_index=True)
    ledger.to_csv(LEDGER_PATH, index=False)

    status = {
        "candidate_id": "rank382_liquidityvol_x_illiqlevel_xs",
        "candidate_rank": 382,
        "stage": "paper_runner_ready",
        "wiring_status": "runner_ready_local_dryrun_ok" if gate_pass else "blocked",
        "runner_mode": "frozen_scope_paper_refresh",
        "runner_script": "scripts/run_rank382_liquidityvol_illiqlevel_paper_runner.py",
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "fixed_universe": "top25_30d_quotevol",
        "signal_interval": "15m",
        "execution_mode": "lag1",
        "friction_bps": 10.0,
        "capacity_tier": "<=0.25% bar ADV",
        "lag1_10bps_net_bps_per_1h": float(lag1_10["net_bps_per_1h"]),
        "capacity_0p25_net_bps_per_1h": float(cap_025["net_alpha_bps_per_1h"]),
        "updated_at_utc": iso_z(now),
        "decisive_blocker": blocker,
    }
    pd.DataFrame([status]).to_csv(STATUS_PATH, index=False)

    state = {
        "candidate_id": status["candidate_id"],
        "candidate_rank": 382,
        "wiring_status": status["wiring_status"],
        "runner_mode": status["runner_mode"],
        "runner_script": status["runner_script"],
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "fixed_universe": status["fixed_universe"],
        "signal_interval": status["signal_interval"],
        "execution_mode": status["execution_mode"],
        "friction_bps": status["friction_bps"],
        "capacity_tier": status["capacity_tier"],
        "lag1_10bps_net_bps_per_1h": status["lag1_10bps_net_bps_per_1h"],
        "capacity_0p25_net_bps_per_1h": status["capacity_0p25_net_bps_per_1h"],
        "last_run_at_utc": iso_z(now),
        "decisive_blocker": blocker,
    }
    write_json(STATE_PATH, state)

    run_summary = {
        "run_at_utc": iso_z(now),
        "runner": "rank382_liquidityvol_illiqlevel_paper_runner",
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
