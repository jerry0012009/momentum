#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank389_crossvenue_netcarry"
SOURCE_DIR = ROOT / "reports" / "artifacts" / "optimization_loop"

STATUS_PATH = ART_DIR / "rank389_status.csv"
STATE_PATH = ART_DIR / "rank389_state.json"
SPEC_PATH = ART_DIR / "rank389_frozen_launch_spec.json"
LEDGER_PATH = ART_DIR / "rank389_launch_checks.csv"
SNAPSHOT_PATH = ART_DIR / "rank389_current_snapshot.csv"
RUN_SUMMARY_PATH = ART_DIR / "rank389_last_run_summary.json"
RUNTIME_ARTIFACT_PATH = ART_DIR / "rank389_runtime_artifact.json"

RUNNER_SERVICE = "momentum-rank389-paper-refresh.service"
RUNNER_TIMER = "momentum-rank389-paper-refresh.timer"


def iso_z(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def latest_source() -> Path:
    matches = sorted(SOURCE_DIR.glob("rank389_survivor_followup_*.json"))
    if not matches:
        raise FileNotFoundError("missing rank389 survivor followup artifact under reports/artifacts/optimization_loop")
    return matches[-1]


def build_spec(source_rel: str) -> dict:
    return {
        "candidate_id": "rank389_crossvenue_netcarry_ranking_alpha",
        "candidate_rank": 389,
        "scope": "cross-venue net-carry pair ranking with collector_receive_ts same-window guard and unified funding+basis+fee+slippage accounting",
        "execution_gate": "collector_window_ms <= 800 and edge_after_cost_apr > 0",
        "source_artifacts": [source_rel],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank389 cross-venue net-carry paper runner")
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    if not args.refresh:
        parser.error("choose --refresh")

    source_path = latest_source()
    raw = json.loads(source_path.read_text(encoding="utf-8"))

    window_ms = int(raw.get("collector_window_ms", 10**9))
    pair = raw.get("pair") or {}
    edge_before = float(pair.get("edge_before_cost_apr", 0.0))
    edge_after = float(pair.get("edge_after_cost_apr", 0.0))
    earn = str(pair.get("earn", ""))
    hedge = str(pair.get("hedge", ""))
    venue_pair = f"{earn}->{hedge}" if earn and hedge else "unknown"

    gate_pass = bool(window_ms <= 800 and edge_after > 0)
    blocker = "none" if gate_pass else ("collector_window_too_wide" if window_ms > 800 else "edge_after_cost_non_positive")

    ensure_dir(ART_DIR)
    now = datetime.now(timezone.utc)

    spec = build_spec(str(source_path.relative_to(ROOT)))
    write_json(SPEC_PATH, spec)

    runtime_artifact = {
        "captured_at_utc": iso_z(now),
        "candidate_rank": 389,
        "source_artifact": str(source_path.relative_to(ROOT)),
        "window_ms": window_ms,
        "edge_before_cost": edge_before,
        "edge_after_cost": edge_after,
        "venue_pair": venue_pair,
        "gate_pass": gate_pass,
        "decisive_blocker": blocker,
    }
    write_json(RUNTIME_ARTIFACT_PATH, runtime_artifact)

    snapshot = pd.DataFrame([runtime_artifact])
    snapshot.to_csv(SNAPSHOT_PATH, index=False)

    ledger_cols = [
        "captured_at_utc",
        "candidate_rank",
        "window_ms",
        "edge_before_cost",
        "edge_after_cost",
        "venue_pair",
        "gate_pass",
        "decisive_blocker",
        "source_artifact",
    ]
    prev = pd.read_csv(LEDGER_PATH) if LEDGER_PATH.exists() and LEDGER_PATH.stat().st_size > 0 else pd.DataFrame(columns=ledger_cols)
    pd.concat([prev, snapshot[ledger_cols]], ignore_index=True).to_csv(LEDGER_PATH, index=False)

    status = {
        "candidate_id": "rank389_crossvenue_netcarry_ranking_alpha",
        "candidate_rank": 389,
        "stage": "paper_runner_ready",
        "wiring_status": "runner_ready_local_dryrun_ok" if gate_pass else "blocked",
        "runner_mode": "frozen_scope_paper_refresh",
        "runner_script": "scripts/run_rank389_crossvenue_netcarry_paper_runner.py",
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "scope": spec["scope"],
        "window_ms": window_ms,
        "edge_before_cost": edge_before,
        "edge_after_cost": edge_after,
        "venue_pair": venue_pair,
        "updated_at_utc": iso_z(now),
        "decisive_blocker": blocker,
    }
    pd.DataFrame([status]).to_csv(STATUS_PATH, index=False)

    state = {
        "candidate_id": status["candidate_id"],
        "candidate_rank": 389,
        "wiring_status": status["wiring_status"],
        "runner_mode": status["runner_mode"],
        "runner_script": status["runner_script"],
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "scope": spec["scope"],
        "last_run_at_utc": iso_z(now),
        "window_ms": window_ms,
        "edge_before_cost": edge_before,
        "edge_after_cost": edge_after,
        "venue_pair": venue_pair,
        "decisive_blocker": blocker,
        "source_artifact": str(source_path.relative_to(ROOT)),
    }
    write_json(STATE_PATH, state)

    summary = {
        "run_at_utc": iso_z(now),
        "runner": "rank389_crossvenue_netcarry_paper_runner",
        "wiring_status": status["wiring_status"],
        "decisive_blocker": blocker,
        "status_path": str(STATUS_PATH.relative_to(ROOT)),
        "state_path": str(STATE_PATH.relative_to(ROOT)),
        "spec_path": str(SPEC_PATH.relative_to(ROOT)),
        "runtime_artifact_path": str(RUNTIME_ARTIFACT_PATH.relative_to(ROOT)),
        "snapshot_path": str(SNAPSHOT_PATH.relative_to(ROOT)),
        "ledger_path": str(LEDGER_PATH.relative_to(ROOT)),
    }
    write_json(RUN_SUMMARY_PATH, summary)
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
