#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "reports" / "artifacts" / "literature"
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank379_intraday_entropy_xs"

SUMMARY_PATH = SOURCE_DIR / "intraday_entropy_probe_summary_2026-04-11.csv"
PATH_15M = SOURCE_DIR / "intraday_entropy_probe_path_2026-04-11_15m.csv"
DETAIL_15M = SOURCE_DIR / "intraday_entropy_probe_detail_2026-04-11_15m.csv"

STATUS_PATH = ART_DIR / "rank379_status.csv"
STATE_PATH = ART_DIR / "rank379_state.json"
SPEC_PATH = ART_DIR / "rank379_frozen_launch_spec.json"
LEDGER_PATH = ART_DIR / "rank379_launch_checks.csv"
SNAPSHOT_PATH = ART_DIR / "rank379_current_snapshot.csv"
RUN_SUMMARY_PATH = ART_DIR / "rank379_last_run_summary.json"
SIGNAL_PATH = ART_DIR / "rank379_live_signal_snapshot.csv"
HTML_PATH = ROOT / "reports" / "site" / "paper" / "rank379_intraday_entropy_xs.html"

RUNNER_SERVICE = "momentum-rank379-paper-refresh.service"
RUNNER_TIMER = "momentum-rank379-paper-refresh.timer"


def iso_z(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_spec() -> dict:
    return {
        "candidate_id": "rank379_intraday_entropy_ratio_xs_reversal",
        "candidate_rank": 379,
        "scope": "fixed_15m_input; session_to_session_xs_long_short; long=lowest_EntR, short=highest_EntR; cost_assumption=6bps(two-leg)",
        "execution_gate": "avg_bps_15m_minus_cost_bps > 0 and latest_signal_nonempty",
        "source_artifacts": [
            "reports/artifacts/literature/intraday_entropy_probe_summary_2026-04-11.csv",
            "reports/artifacts/literature/intraday_entropy_probe_path_2026-04-11_15m.csv",
            "reports/artifacts/literature/intraday_entropy_probe_detail_2026-04-11_15m.csv",
        ],
    }


def write_html(status: dict, signal: pd.DataFrame) -> None:
    ensure_dir(HTML_PATH.parent)
    body = f"""<!doctype html>
<html lang=\"zh\"><head><meta charset=\"utf-8\"/><title>Rank 379 Paper Runner</title>
<style>body{{font-family:Arial,sans-serif;margin:24px;line-height:1.5}}table{{border-collapse:collapse}}td,th{{border:1px solid #ddd;padding:6px 8px}}</style>
</head><body>
<h1>Rank 379 / intraday entropy-ratio XS reversal</h1>
<p><strong>接线状态：</strong>{status['wiring_status']}</p>
<ul>
<li>runner: <code>{status['runner_script']}</code></li>
<li>service: <code>{status['service_unit']}</code></li>
<li>timer: <code>{status['timer_unit']}</code></li>
<li>scope: <code>{status['scope']}</code></li>
<li>更新时间: <code>{status['updated_at_utc']}</code></li>
<li>avg_bps_15m: <code>{status['avg_bps_15m']:.3f}</code></li>
<li>net_after_cost_bps: <code>{status['net_after_cost_bps']:.3f}</code></li>
<li>latest_day: <code>{status['latest_signal_day_utc']}</code></li>
</ul>
{signal.to_html(index=False)}
</body></html>
"""
    HTML_PATH.write_text(body, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank379 intraday entropy XS paper runner")
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    if not args.refresh:
        parser.error("choose --refresh")

    required = [SUMMARY_PATH, PATH_15M, DETAIL_15M]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError(f"rank379 source artifacts missing: {missing}")

    ensure_dir(ART_DIR)
    now = datetime.now(timezone.utc)

    spec = build_spec()
    write_json(SPEC_PATH, spec)

    summary = pd.read_csv(SUMMARY_PATH)
    row = summary.loc[(summary["interval"] == "15m") & (summary["variant"] == "low_Entr_minus_high_Entr")]
    if row.empty:
        raise RuntimeError("summary missing 15m low_Entr_minus_high_Entr row")
    row = row.iloc[0]
    avg_bps_15m = float(row["avg_bps"])
    win_rate_15m = float(row["win_rate"])
    days_15m = int(row["days"])

    cost_bps = 6.0
    net_after_cost_bps = avg_bps_15m - cost_bps

    detail = pd.read_csv(DETAIL_15M)
    detail["day"] = pd.to_datetime(detail["day"], utc=True)
    latest_day = detail["day"].max()
    latest = detail.loc[detail["day"] == latest_day].copy()
    if latest.empty:
        raise RuntimeError("detail_15m has no latest-day signal rows")

    signal = latest[["day", "side", "symbol", "entr", "entropy", "ret_d", "next_ret"]].copy()
    signal.rename(columns={"day": "signal_day_utc"}, inplace=True)
    signal["captured_at_utc"] = iso_z(now)
    signal = signal[["captured_at_utc", "signal_day_utc", "side", "symbol", "entr", "entropy", "ret_d", "next_ret"]]
    signal.to_csv(SIGNAL_PATH, index=False)

    pass_gate = bool(net_after_cost_bps > 0 and len(signal) >= 2)
    blocker = "none" if pass_gate else "avg_bps_15m_minus_cost_bps<=0_or_signal_empty"

    snapshot = pd.DataFrame([
        {
            "captured_at_utc": iso_z(now),
            "interval": "15m",
            "avg_bps": avg_bps_15m,
            "cost_bps": cost_bps,
            "net_after_cost_bps": net_after_cost_bps,
            "win_rate": win_rate_15m,
            "days": days_15m,
            "signal_rows": int(len(signal)),
            "gate_pass": pass_gate,
            "decisive_blocker": blocker,
        }
    ])
    snapshot.to_csv(SNAPSHOT_PATH, index=False)

    ledger_cols = ["captured_at_utc", "interval", "avg_bps", "cost_bps", "net_after_cost_bps", "win_rate", "days", "signal_rows", "gate_pass", "decisive_blocker"]
    if LEDGER_PATH.exists() and LEDGER_PATH.stat().st_size > 0:
        prev = pd.read_csv(LEDGER_PATH)
        ledger = pd.concat([prev, snapshot[ledger_cols]], ignore_index=True)
    else:
        ledger = snapshot[ledger_cols].copy()
    ledger.to_csv(LEDGER_PATH, index=False)

    status = {
        "candidate_id": "rank379_intraday_entropy_ratio_xs_reversal",
        "candidate_rank": 379,
        "stage": "paper_runner_ready",
        "wiring_status": "runner_ready_local_dryrun_ok" if pass_gate else "blocked",
        "runner_mode": "frozen_scope_paper_refresh",
        "runner_script": "scripts/run_rank379_intraday_entropy_xs_paper_runner.py",
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "scope": spec["scope"],
        "avg_bps_15m": avg_bps_15m,
        "net_after_cost_bps": net_after_cost_bps,
        "signal_rows": int(len(signal)),
        "latest_signal_day_utc": latest_day.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "updated_at_utc": iso_z(now),
        "decisive_blocker": blocker,
    }
    pd.DataFrame([status]).to_csv(STATUS_PATH, index=False)

    state = {
        "candidate_id": status["candidate_id"],
        "candidate_rank": 379,
        "wiring_status": status["wiring_status"],
        "runner_mode": status["runner_mode"],
        "runner_script": status["runner_script"],
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "scope": spec["scope"],
        "last_run_at_utc": iso_z(now),
        "avg_bps_15m": avg_bps_15m,
        "net_after_cost_bps": net_after_cost_bps,
        "latest_signal_day_utc": status["latest_signal_day_utc"],
        "signal_snapshot_path": str(SIGNAL_PATH.relative_to(ROOT)),
        "decisive_blocker": blocker,
    }
    write_json(STATE_PATH, state)
    write_html(status, signal)

    run_summary = {
        "run_at_utc": iso_z(now),
        "runner": "rank379_intraday_entropy_xs_paper_runner",
        "wiring_status": status["wiring_status"],
        "decisive_blocker": blocker,
        "status_path": str(STATUS_PATH.relative_to(ROOT)),
        "state_path": str(STATE_PATH.relative_to(ROOT)),
        "ledger_path": str(LEDGER_PATH.relative_to(ROOT)),
        "signal_path": str(SIGNAL_PATH.relative_to(ROOT)),
        "snapshot_path": str(SNAPSHOT_PATH.relative_to(ROOT)),
        "spec_path": str(SPEC_PATH.relative_to(ROOT)),
        "html_path": str(HTML_PATH.relative_to(ROOT)),
    }
    write_json(RUN_SUMMARY_PATH, run_summary)
    print(json.dumps(run_summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
