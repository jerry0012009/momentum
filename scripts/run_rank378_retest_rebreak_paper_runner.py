#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "reports" / "artifacts" / "rank378_execution_realism"
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank378_retest_rebreak"

STATUS_PATH = ART_DIR / "rank378_status.csv"
STATE_PATH = ART_DIR / "rank378_state.json"
SPEC_PATH = ART_DIR / "rank378_frozen_launch_spec.json"
LEDGER_PATH = ART_DIR / "rank378_launch_checks.csv"
RUN_SUMMARY_PATH = ART_DIR / "rank378_last_run_summary.json"
SNAPSHOT_PATH = ART_DIR / "rank378_current_snapshot.csv"
HTML_PATH = ROOT / "reports" / "site" / "paper" / "rank378_retest_rebreak.html"

RUNNER_SERVICE = "momentum-rank378-paper-refresh.service"
RUNNER_TIMER = "momentum-rank378-paper-refresh.timer"


def iso_z(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_spec() -> dict:
    return {
        "candidate_id": "rank378_retest_window_impulse_rebreak_confirmation",
        "candidate_rank": 378,
        "scope": "BTC/ETH/SOL; 15m; short continuation; next-open lag=1; hold=8 bars; N=6",
        "execution_gate": "avg_net_at_50k_notional > 0",
        "source_artifacts": [
            "reports/artifacts/rank378_execution_realism/rank378_event_ledger.csv",
            "reports/artifacts/rank378_execution_realism/rank378_trade_ledger.csv",
            "reports/artifacts/rank378_execution_realism/rank378_portfolio_summary.csv",
            "reports/artifacts/rank378_execution_realism/rank378_p2_admission_exit_summary.json",
        ],
    }


def write_html(status: dict, snapshot: pd.DataFrame) -> None:
    ensure_dir(HTML_PATH.parent)
    body = f"""<!doctype html>
<html lang=\"zh\"><head><meta charset=\"utf-8\"/><title>Rank 378 Paper Runner</title>
<style>body{{font-family:Arial,sans-serif;margin:24px;line-height:1.5}}table{{border-collapse:collapse}}td,th{{border:1px solid #ddd;padding:6px 8px}}</style>
</head><body>
<h1>Rank 378 / retest-window impulse re-break confirmation</h1>
<p><strong>接线状态：</strong>{status['wiring_status']}</p>
<ul>
<li>runner: <code>{status['runner_script']}</code></li>
<li>service: <code>{status['service_unit']}</code></li>
<li>timer: <code>{status['timer_unit']}</code></li>
<li>scope: <code>{status['scope']}</code></li>
<li>更新时间: <code>{status['updated_at_utc']}</code></li>
<li>50k avg net: <code>{status['avg_net_50k']:.6f}</code></li>
<li>trades: <code>{status['trades_50k']}</code></li>
</ul>
{snapshot.to_html(index=False)}
</body></html>
"""
    HTML_PATH.write_text(body, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank378 paper runner")
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    if not args.refresh:
        parser.error("choose --refresh")

    required = [
        SOURCE_DIR / "rank378_portfolio_summary.csv",
        SOURCE_DIR / "rank378_p2_admission_exit_summary.json",
        SOURCE_DIR / "rank378_trade_ledger.csv",
        SOURCE_DIR / "rank378_event_ledger.csv",
    ]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError(f"rank378 source artifacts missing: {missing}")

    now = datetime.now(timezone.utc)
    ensure_dir(ART_DIR)

    spec = build_spec()
    write_json(SPEC_PATH, spec)

    portfolio = pd.read_csv(SOURCE_DIR / "rank378_portfolio_summary.csv")
    row_50k = portfolio.loc[portfolio["notional_usd"] == 50000]
    if row_50k.empty:
        raise RuntimeError("rank378 portfolio summary missing 50k notional row")
    row_50k = row_50k.iloc[0]

    with (SOURCE_DIR / "rank378_p2_admission_exit_summary.json").open("r", encoding="utf-8") as f:
        admission = json.load(f)

    avg_net_50k = float(row_50k["avg_net"])
    trades_50k = int(row_50k["trades"])
    pass_gate = bool(trades_50k > 0 and avg_net_50k > 0)

    snapshot = pd.DataFrame([
        {
            "captured_at_utc": iso_z(now),
            "notional_usd": 50000,
            "trades": trades_50k,
            "avg_net": avg_net_50k,
            "total_net": float(row_50k["total_net"]),
            "win_rate": float(row_50k["win_rate"]),
            "gate_pass": pass_gate,
            "decisive_blocker": "none" if pass_gate else "avg_net_50k_notional<=0",
        }
    ])
    snapshot.to_csv(SNAPSHOT_PATH, index=False)

    ledger_cols = ["captured_at_utc", "notional_usd", "trades", "avg_net", "total_net", "win_rate", "gate_pass", "decisive_blocker"]
    prev = pd.read_csv(LEDGER_PATH) if LEDGER_PATH.exists() and LEDGER_PATH.stat().st_size > 0 else pd.DataFrame(columns=ledger_cols)
    combined = pd.concat([prev, snapshot[ledger_cols]], ignore_index=True)
    combined.to_csv(LEDGER_PATH, index=False)

    status = {
        "candidate_id": "rank378_retest_window_impulse_rebreak_confirmation",
        "candidate_rank": 378,
        "stage": "paper_runner_live",
        "wiring_status": "connected_runner_live" if pass_gate else "blocked",
        "runner_mode": "frozen_scope_paper_refresh",
        "runner_script": "scripts/run_rank378_retest_rebreak_paper_runner.py",
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "scope": spec["scope"],
        "trades_50k": trades_50k,
        "avg_net_50k": avg_net_50k,
        "updated_at_utc": iso_z(now),
        "decisive_blocker": "none" if pass_gate else "avg_net_50k_notional<=0",
        "admission_effectiveness_avg_net": float(admission["effectiveness"]["avg_net"]),
    }
    pd.DataFrame([status]).to_csv(STATUS_PATH, index=False)

    state = {
        "candidate_id": status["candidate_id"],
        "candidate_rank": 378,
        "wiring_status": status["wiring_status"],
        "runner_mode": status["runner_mode"],
        "runner_script": status["runner_script"],
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "scope": spec["scope"],
        "last_run_at_utc": iso_z(now),
        "trades_50k": trades_50k,
        "avg_net_50k": avg_net_50k,
        "decisive_blocker": status["decisive_blocker"],
    }
    write_json(STATE_PATH, state)
    write_html(status, snapshot)

    summary = {
        "run_at_utc": iso_z(now),
        "runner": "rank378_retest_rebreak_paper_runner",
        "wiring_status": status["wiring_status"],
        "decisive_blocker": status["decisive_blocker"],
        "status_path": str(STATUS_PATH.relative_to(ROOT)),
        "state_path": str(STATE_PATH.relative_to(ROOT)),
        "ledger_path": str(LEDGER_PATH.relative_to(ROOT)),
        "snapshot_path": str(SNAPSHOT_PATH.relative_to(ROOT)),
        "spec_path": str(SPEC_PATH.relative_to(ROOT)),
        "html_path": str(HTML_PATH.relative_to(ROOT)),
    }
    write_json(RUN_SUMMARY_PATH, summary)
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
