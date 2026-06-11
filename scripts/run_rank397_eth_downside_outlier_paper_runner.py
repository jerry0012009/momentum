#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "reports" / "artifacts" / "literature"
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank397_eth_downside_outlier_fade"

SUMMARY_PATH = SOURCE_DIR / "rank397_p2_admission_exit_summary_2026-04-13.csv"
MONTHLY_PATH = SOURCE_DIR / "rank397_p2_admission_exit_monthly_2026-04-13.csv"
HONESTY_PATH = SOURCE_DIR / "rank397_p2_honesty_execution_snapshot_2026-04-13.json"

STATUS_PATH = ART_DIR / "rank397_status.csv"
STATE_PATH = ART_DIR / "rank397_state.json"
SPEC_PATH = ART_DIR / "rank397_frozen_launch_spec.json"
LEDGER_PATH = ART_DIR / "rank397_launch_checks.csv"
SNAPSHOT_PATH = ART_DIR / "rank397_current_snapshot.csv"
RUN_SUMMARY_PATH = ART_DIR / "rank397_last_run_summary.json"


def iso_z(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_spec() -> dict:
    return {
        "candidate_id": "rank397_eth_downside_outlier_fade_europe_veto",
        "candidate_rank": 397,
        "signal": "ETHUSDT 15m downside outlier fade",
        "event_definition": "ret_15m <= -z * rolling_sigma_672",
        "frozen_params": {
            "symbol": "ETHUSDT",
            "z": 3.5,
            "hold_min": 30,
            "cost_roundtrip_bps": 12,
            "session_veto": "08:00-16:00 UTC",
            "allow_sessions_utc": ["00:00-08:00", "16:00-24:00"],
        },
        "execution_note": "P3 launch wiring runner seed based on frozen P2 admission outputs; scheduler and first verified run are separate steps.",
        "source_artifacts": [
            "reports/artifacts/literature/rank397_p2_admission_exit_summary_2026-04-13.csv",
            "reports/artifacts/literature/rank397_p2_admission_exit_monthly_2026-04-13.csv",
            "reports/artifacts/literature/rank397_p2_honesty_execution_snapshot_2026-04-13.json",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank397 ETH downside outlier fade paper runner")
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    if not args.refresh:
        parser.error("choose --refresh")

    required = [SUMMARY_PATH, MONTHLY_PATH, HONESTY_PATH]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError(f"rank397 source artifacts missing: {missing}")

    ensure_dir(ART_DIR)
    now = datetime.now(timezone.utc)

    spec = build_spec()
    write_json(SPEC_PATH, spec)

    summary = pd.read_csv(SUMMARY_PATH)
    lane = summary[(summary["z"] == 3.5) & (summary["hold_min"] == 30)].copy()
    if lane.empty:
        raise RuntimeError("rank397 summary missing frozen lane z=3.5 hold=30")
    lane_row = lane.iloc[0]

    monthly = pd.read_csv(MONTHLY_PATH)
    lane_monthly = monthly[(monthly["z"] == 3.5) & (monthly["hold_min"] == 30)].copy()
    if lane_monthly.empty:
        raise RuntimeError("rank397 monthly artifact missing frozen lane z=3.5 hold=30")
    lane_monthly = lane_monthly.sort_values("month").reset_index(drop=True)
    latest_month = lane_monthly.iloc[-1]

    honesty = json.loads(HONESTY_PATH.read_text(encoding="utf-8"))
    best_after_extra6 = float(honesty.get("best_config_net_after_extra6_bps", 0.0))
    delay_net_bps = float(honesty.get("delayed_proxy_net12_bps_z3", 0.0))

    gate_pass = bool(float(lane_row["net_mean_bps_12"]) > 0 and best_after_extra6 > 0 and delay_net_bps > 0)
    blocker = "none" if gate_pass else "frozen_lane_or_honesty_gate_failed"

    snapshot = pd.DataFrame([
        {
            "captured_at_utc": iso_z(now),
            "symbol": "ETHUSDT",
            "signal_interval": "15m",
            "execution_interval": "5m_immediate",
            "z": 3.5,
            "hold_min": 30,
            "session_veto_utc": "08:00-16:00",
            "events": int(float(lane_row["events"])),
            "gross_mean_bps": float(lane_row["gross_mean_bps"]),
            "net_mean_bps_12": float(lane_row["net_mean_bps_12"]),
            "win_rate": float(lane_row["win_rate"]),
            "latest_month": str(latest_month["month"]),
            "latest_month_net_bps_12": float(latest_month["mean"]),
            "honesty_best_net_after_extra6_bps": best_after_extra6,
            "honesty_delay_net_bps_12": delay_net_bps,
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
        "candidate_id": "rank397_eth_downside_outlier_fade_europe_veto",
        "candidate_rank": 397,
        "stage": "paper_runner_ready",
        "wiring_status": "runner_ready_local_dryrun_ok" if gate_pass else "blocked",
        "runner_mode": "frozen_scope_paper_refresh",
        "runner_script": "scripts/run_rank397_eth_downside_outlier_paper_runner.py",
        "scope": "ETH downside outlier fade with Europe-hours veto",
        "signal_interval": "15m",
        "execution_interval": "5m_immediate",
        "z": 3.5,
        "hold_min": 30,
        "cost_roundtrip_bps": 12,
        "session_veto_utc": "08:00-16:00",
        "net_mean_bps_12": float(lane_row["net_mean_bps_12"]),
        "latest_month": str(latest_month["month"]),
        "latest_month_net_bps_12": float(latest_month["mean"]),
        "updated_at_utc": iso_z(now),
        "decisive_blocker": blocker,
    }
    pd.DataFrame([status]).to_csv(STATUS_PATH, index=False)

    state = {
        "candidate_id": status["candidate_id"],
        "candidate_rank": 397,
        "wiring_status": status["wiring_status"],
        "runner_mode": status["runner_mode"],
        "runner_script": status["runner_script"],
        "scope": status["scope"],
        "signal_interval": "15m",
        "execution_interval": "5m_immediate",
        "z": 3.5,
        "hold_min": 30,
        "cost_roundtrip_bps": 12,
        "session_veto_utc": "08:00-16:00",
        "last_run_at_utc": iso_z(now),
        "net_mean_bps_12": float(lane_row["net_mean_bps_12"]),
        "latest_month": str(latest_month["month"]),
        "latest_month_net_bps_12": float(latest_month["mean"]),
        "decisive_blocker": blocker,
    }
    write_json(STATE_PATH, state)

    run_summary = {
        "run_at_utc": iso_z(now),
        "runner": "rank397_eth_downside_outlier_paper_runner",
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
