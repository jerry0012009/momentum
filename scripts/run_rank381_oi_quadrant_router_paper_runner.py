#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "reports" / "artifacts" / "literature"
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank381_oi_quadrant_router"

FRICTION_PATH = SOURCE_DIR / "rank381_p2_admission_friction_sweep_2026-04-11.csv"
CROSSASSET_PATH = SOURCE_DIR / "rank381_p2_admission_crossasset_2026-04-11.csv"

STATUS_PATH = ART_DIR / "rank381_status.csv"
STATE_PATH = ART_DIR / "rank381_state.json"
SPEC_PATH = ART_DIR / "rank381_frozen_launch_spec.json"
LEDGER_PATH = ART_DIR / "rank381_launch_checks.csv"
SNAPSHOT_PATH = ART_DIR / "rank381_current_snapshot.csv"
SIGNAL_PATH = ART_DIR / "rank381_live_signal_snapshot.csv"
RUN_SUMMARY_PATH = ART_DIR / "rank381_last_run_summary.json"

RUNNER_SERVICE = "momentum-rank381-paper-refresh.service"
RUNNER_TIMER = "momentum-rank381-paper-refresh.timer"


def iso_z(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_spec() -> dict:
    return {
        "candidate_id": "rank381_perp_price_x_oi_quadrant_router",
        "candidate_rank": 381,
        "scope": "15m perp; lag1 OI timestamp; green+OI_up continuation with red+OI_up short-veto; hold in [4,8] bars",
        "execution_gate": "lag1_exec net_bps_at_10bps_friction > 0 and positive_symbols>=5/7",
        "source_artifacts": [
            "reports/artifacts/literature/rank381_p2_admission_friction_sweep_2026-04-11.csv",
            "reports/artifacts/literature/rank381_p2_admission_crossasset_2026-04-11.csv",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank381 OI quadrant router paper runner")
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    if not args.refresh:
        parser.error("choose --refresh")

    required = [FRICTION_PATH, CROSSASSET_PATH]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError(f"rank381 source artifacts missing: {missing}")

    ensure_dir(ART_DIR)
    now = datetime.now(timezone.utc)

    spec = build_spec()
    write_json(SPEC_PATH, spec)

    friction = pd.read_csv(FRICTION_PATH)
    cross = pd.read_csv(CROSSASSET_PATH)

    lane = friction[(friction["mode"] == "lag1_exec") & (friction["friction_bps"] == 10) & (friction["hold_bars"].isin([4, 8]))].copy()
    if lane.empty:
        raise RuntimeError("rank381 friction sweep missing lag1_exec hold=4/8 at 10bps")

    lane = lane.sort_values(["hold_bars"]).reset_index(drop=True)
    lane["captured_at_utc"] = iso_z(now)
    lane["honesty_mode"] = "lag1_exec"
    lane["signal_interval"] = "15m"
    lane.to_csv(SIGNAL_PATH, index=False)

    cross_lanes = cross[cross["hold_bars"].isin([4, 8])].copy()
    if cross_lanes.empty:
        raise RuntimeError("rank381 crossasset artifact missing hold=4/8 rows")

    hold4 = lane[lane["hold_bars"] == 4]
    hold8 = lane[lane["hold_bars"] == 8]
    if hold4.empty or hold8.empty:
        raise RuntimeError("rank381 lane missing hold=4 or hold=8 row")

    hold4 = hold4.iloc[0]
    hold8 = hold8.iloc[0]
    gate_pass = bool(float(hold4["net_bps"]) > 0 and float(hold8["net_bps"]) > 0 and int(hold4["positive_symbols"]) >= 5 and int(hold8["positive_symbols"]) >= 5)
    blocker = "none" if gate_pass else "lane_4_8_net_or_crossasset_below_launch_gate"

    snapshot = pd.DataFrame([
        {
            "captured_at_utc": iso_z(now),
            "signal_interval": "15m",
            "honesty_mode": "lag1_exec",
            "friction_bps": 10,
            "hold4_net_bps": float(hold4["net_bps"]),
            "hold8_net_bps": float(hold8["net_bps"]),
            "hold4_positive_symbols": int(hold4["positive_symbols"]),
            "hold8_positive_symbols": int(hold8["positive_symbols"]),
            "hold4_signals_n": int(float(hold4["signals_n"])),
            "hold8_signals_n": int(float(hold8["signals_n"])),
            "gate_pass": gate_pass,
            "decisive_blocker": blocker,
        }
    ])
    snapshot.to_csv(SNAPSHOT_PATH, index=False)

    ledger_cols = [
        "captured_at_utc",
        "signal_interval",
        "honesty_mode",
        "friction_bps",
        "hold4_net_bps",
        "hold8_net_bps",
        "hold4_positive_symbols",
        "hold8_positive_symbols",
        "hold4_signals_n",
        "hold8_signals_n",
        "gate_pass",
        "decisive_blocker",
    ]
    prev = pd.read_csv(LEDGER_PATH) if LEDGER_PATH.exists() and LEDGER_PATH.stat().st_size > 0 else pd.DataFrame(columns=ledger_cols)
    ledger = pd.concat([prev, snapshot[ledger_cols]], ignore_index=True)
    ledger.to_csv(LEDGER_PATH, index=False)

    status = {
        "candidate_id": "rank381_perp_price_x_oi_quadrant_router",
        "candidate_rank": 381,
        "stage": "paper_runner_ready",
        "wiring_status": "runner_ready_local_dryrun_ok" if gate_pass else "blocked",
        "runner_mode": "frozen_scope_paper_refresh",
        "runner_script": "scripts/run_rank381_oi_quadrant_router_paper_runner.py",
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "scope": spec["scope"],
        "signal_interval": "15m",
        "honesty_mode": "lag1_exec",
        "friction_bps": 10,
        "hold4_net_bps": float(hold4["net_bps"]),
        "hold8_net_bps": float(hold8["net_bps"]),
        "hold4_positive_symbols": int(hold4["positive_symbols"]),
        "hold8_positive_symbols": int(hold8["positive_symbols"]),
        "updated_at_utc": iso_z(now),
        "decisive_blocker": blocker,
    }
    pd.DataFrame([status]).to_csv(STATUS_PATH, index=False)

    state = {
        "candidate_id": status["candidate_id"],
        "candidate_rank": 381,
        "wiring_status": status["wiring_status"],
        "runner_mode": status["runner_mode"],
        "runner_script": status["runner_script"],
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "scope": spec["scope"],
        "last_run_at_utc": iso_z(now),
        "signal_interval": "15m",
        "honesty_mode": "lag1_exec",
        "friction_bps": 10,
        "hold4_net_bps": float(hold4["net_bps"]),
        "hold8_net_bps": float(hold8["net_bps"]),
        "decisive_blocker": blocker,
    }
    write_json(STATE_PATH, state)

    run_summary = {
        "run_at_utc": iso_z(now),
        "runner": "rank381_oi_quadrant_router_paper_runner",
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
