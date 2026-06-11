#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "reports" / "artifacts" / "quant_digests"
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank401_crowdedlong_fragility_cascade"

SUMMARY_PATH = SOURCE_DIR / "rank401_crowdedlong_followup_summary_2026-04-13.json"
EVENTS_PATH = SOURCE_DIR / "rank401_crowdedlong_followup_events_2026-04-13.csv"

STATUS_PATH = ART_DIR / "rank401_status.csv"
STATE_PATH = ART_DIR / "rank401_state.json"
SPEC_PATH = ART_DIR / "rank401_frozen_launch_spec.json"
LEDGER_PATH = ART_DIR / "rank401_launch_checks.csv"
SNAPSHOT_PATH = ART_DIR / "rank401_current_snapshot.csv"
RUN_SUMMARY_PATH = ART_DIR / "rank401_last_run_summary.json"

RUNNER_SERVICE = "momentum-rank401-paper-refresh.service"
RUNNER_TIMER = "momentum-rank401-paper-refresh.timer"


def iso_z(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_spec() -> dict:
    return {
        "candidate_id": "rank401_crowdedlong_fragility_cascade",
        "candidate_rank": 401,
        "scope": "BTC+ETH crowded-long fragility cascade short lane",
        "signal_interval": "15m",
        "entry_delay": "1 bar",
        "hold_bars": 4,
        "cost_lanes_bps_per_side": [2, 4, 6],
        "frozen_trigger": {
            "fund_abs_pct": 0.6,
            "oi_value_pct": 0.6,
            "tls_pct": 0.8,
            "ret1": -0.002,
            "oi_chg": -0.0025,
        },
        "execution_honesty": "signal uses current+historical fields only; forward returns only for evaluation; one-bar delayed entry required in launch lane",
        "source_artifacts": [
            "reports/artifacts/quant_digests/rank401_crowdedlong_followup_summary_2026-04-13.json",
            "reports/artifacts/quant_digests/rank401_crowdedlong_followup_events_2026-04-13.csv",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank401 crowded-long fragility cascade paper runner")
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    if not args.refresh:
        parser.error("choose --refresh")

    required = [SUMMARY_PATH, EVENTS_PATH]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError(f"rank401 source artifacts missing: {missing}")

    payload = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    events = pd.read_csv(EVENTS_PATH)

    metrics = payload.get("metrics", {})
    delay_h4 = metrics.get("ret_delay1_h4", {})
    delay_h1 = metrics.get("ret_delay1_h1", {})

    net2 = float(delay_h4.get("net_avg_bps_cost2x2", 0.0))
    net4 = float(delay_h4.get("net_avg_bps_cost4x2", 0.0))
    net6 = float(delay_h4.get("net_avg_bps_cost6x2", 0.0))

    event_count = int(payload.get("event_count_total", 0))
    symbols = payload.get("symbols", [])
    interval = str(payload.get("interval", "15m"))

    gate_pass = bool(event_count >= 10 and net4 > 0 and net6 >= 0)
    blocker = "none" if gate_pass else "delayed_h4_cost_lane_not_positive_or_sample_too_small"

    ensure_dir(ART_DIR)
    now = datetime.now(timezone.utc)

    spec = build_spec()
    write_json(SPEC_PATH, spec)

    snapshot = pd.DataFrame([
        {
            "captured_at_utc": iso_z(now),
            "candidate_rank": 401,
            "symbols": ",".join(symbols),
            "signal_interval": interval,
            "entry_delay": "1_bar",
            "hold_bars": 4,
            "event_count_total": event_count,
            "delay_h1_net_avg_bps_cost2x2": float(delay_h1.get("net_avg_bps_cost2x2", 0.0)),
            "delay_h1_net_avg_bps_cost4x2": float(delay_h1.get("net_avg_bps_cost4x2", 0.0)),
            "delay_h1_net_avg_bps_cost6x2": float(delay_h1.get("net_avg_bps_cost6x2", 0.0)),
            "delay_h4_net_avg_bps_cost2x2": net2,
            "delay_h4_net_avg_bps_cost4x2": net4,
            "delay_h4_net_avg_bps_cost6x2": net6,
            "recent_event_rows": int(len(events)),
            "gate_pass": gate_pass,
            "decisive_blocker": blocker,
        }
    ])
    snapshot.to_csv(SNAPSHOT_PATH, index=False)

    ledger_cols = list(snapshot.columns)
    prev = pd.read_csv(LEDGER_PATH) if LEDGER_PATH.exists() and LEDGER_PATH.stat().st_size > 0 else pd.DataFrame(columns=ledger_cols)
    pd.concat([prev, snapshot[ledger_cols]], ignore_index=True).to_csv(LEDGER_PATH, index=False)

    status = {
        "candidate_id": "rank401_crowdedlong_fragility_cascade",
        "candidate_rank": 401,
        "stage": "paper_runner_ready",
        "wiring_status": "runner_ready_local_dryrun_ok" if gate_pass else "blocked",
        "runner_mode": "frozen_scope_paper_refresh",
        "runner_script": "scripts/run_rank401_crowdedlong_fragility_paper_runner.py",
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "scope": "BTC+ETH crowded-long fragility cascade short lane",
        "signal_interval": interval,
        "entry_delay": "1_bar",
        "hold_bars": 4,
        "event_count_total": event_count,
        "delay_h4_net_avg_bps_cost2x2": net2,
        "delay_h4_net_avg_bps_cost4x2": net4,
        "delay_h4_net_avg_bps_cost6x2": net6,
        "updated_at_utc": iso_z(now),
        "decisive_blocker": blocker,
    }
    pd.DataFrame([status]).to_csv(STATUS_PATH, index=False)

    state = {
        "candidate_id": status["candidate_id"],
        "candidate_rank": 401,
        "wiring_status": status["wiring_status"],
        "runner_mode": status["runner_mode"],
        "runner_script": status["runner_script"],
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "scope": status["scope"],
        "signal_interval": interval,
        "entry_delay": "1_bar",
        "hold_bars": 4,
        "event_count_total": event_count,
        "delay_h4_net_avg_bps_cost2x2": net2,
        "delay_h4_net_avg_bps_cost4x2": net4,
        "delay_h4_net_avg_bps_cost6x2": net6,
        "decisive_blocker": blocker,
        "source_artifacts": spec["source_artifacts"],
        "last_run_at_utc": iso_z(now),
    }
    write_json(STATE_PATH, state)

    run_summary = {
        "run_at_utc": iso_z(now),
        "runner": "rank401_crowdedlong_fragility_paper_runner",
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
