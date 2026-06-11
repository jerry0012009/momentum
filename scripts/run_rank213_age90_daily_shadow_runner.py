#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank213_age90_live"
SITE_PATH = ROOT / "reports" / "site" / "paper" / "rank213_age90_daily_shadow_runner.html"
ENGINE_PATH = ROOT / "scripts" / "rank213_age90_signal_engine.py"

CURRENT_DECISION_PATH = ART_DIR / "rank213_age90_shadow_current_decision.json"
STATUS_PATH = ART_DIR / "rank213_age90_shadow_status.json"
RECENT_DECISIONS_PATH = ART_DIR / "rank213_age90_shadow_recent_decisions.csv"
SIGNAL_SNAPSHOT_PATH = ART_DIR / "rank213_age90_signal_snapshot.json"
RUN_SUMMARY_PATH = ART_DIR / "rank213_age90_shadow_last_run_summary.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load module: {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


engine = load_module(ENGINE_PATH, "rank213_age90_signal_engine_mod")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def save_json(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_recent(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))
    except Exception:
        return []


def write_recent(path: Path, decision: dict[str, Any], signal: dict[str, Any], *, keep_last: int = 60) -> list[dict[str, Any]]:
    rows = read_recent(path)
    row = {
        "decision_ts": decision.get("decision_ts"),
        "planned_exit_ts": decision.get("planned_exit_ts"),
        "bar_key": decision.get("bar_key"),
        "decision": decision.get("decision"),
        "gate_on": str(bool(decision.get("gate_on"))),
        "longs": ",".join(decision.get("longs") or []),
        "shorts": ",".join(decision.get("shorts") or []),
        "eligible_universe_size": str(decision.get("eligible_universe_size")),
        "signal_hash": decision.get("signal_hash"),
        "universe": ",".join(signal.get("universe") or []),
    }
    rows = [r for r in rows if r.get("bar_key") != row["bar_key"]]
    rows.append(row)
    rows = rows[-keep_last:]
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        writer.writeheader()
        writer.writerows(rows)
    return rows


def write_html(status: dict[str, Any], decision: dict[str, Any], signal: dict[str, Any]) -> None:
    ensure_dir(SITE_PATH.parent)
    top_scores = signal.get("scores", [])[:10]
    score_rows = "".join(
        f"<tr><td>{item.get('symbol')}</td><td>{float(item.get('score')):.4f}</td></tr>"
        for item in top_scores
    )
    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Rank213 age90 top50 4x4 daily shadow</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 24px; line-height: 1.55; color: #172033; }}
    .card {{ border:1px solid #e2e8f0; border-radius:14px; padding:16px; margin:14px 0; }}
    code {{ background:#f1f5f9; padding:2px 6px; border-radius:6px; }}
    table {{ border-collapse: collapse; min-width: 520px; }}
    th,td {{ border-bottom:1px solid #e2e8f0; padding:8px 10px; text-align:left; }}
  </style>
</head>
<body>
  <h1>Rank213 age90 top50 4x4 daily shadow</h1>
  <div class="card">
    <p>status: <code>{status.get('status')}</code></p>
    <p>decision_ts: <code>{decision.get('decision_ts')}</code> · planned_exit_ts: <code>{decision.get('planned_exit_ts')}</code></p>
    <p>longs: <code>{','.join(decision.get('longs') or [])}</code></p>
    <p>shorts: <code>{','.join(decision.get('shorts') or [])}</code></p>
    <p>signal_hash: <code>{decision.get('signal_hash')}</code></p>
  </div>
  <div class="card">
    <h2>Top scores</h2>
    <table><thead><tr><th>symbol</th><th>score</th></tr></thead><tbody>{score_rows}</tbody></table>
  </div>
  <p><a href="/momentum/paper/rank213_age90_live_launch.html">age90 live launch parity</a> · <a href="/momentum/paper/rank213_age90_top50_4x4_execution_stability.html">Top50 4x4 stability</a> · <a href="/momentum/paper/rank213_age90_14d_fourth_round_benchmark_attribution.html">第四轮主报告</a></p>
</body>
</html>
"""
    SITE_PATH.write_text(html, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Publish Rank213 age90 daily shadow decision")
    ap.add_argument("--decision-date", help="UTC decision date, e.g. 2026-05-06")
    ap.add_argument("--no-download", action="store_true", help="Do not download missing Binance daily data")
    args = ap.parse_args()

    decision_ts = pd.Timestamp(args.decision_date, tz="UTC") if args.decision_date else None
    signal = engine.build_signal(decision_ts, allow_download=not args.no_download)
    decision = engine.current_decision_payload(signal)
    now = utc_now_iso()
    status = {
        "strategy_id": signal["strategy_id"],
        "runner": "rank213_age90_daily_shadow_runner",
        "status": "ok" if decision.get("gate_on") else "flat_or_incomplete",
        "updated_at_utc": now,
        "latest_decision_ts": decision.get("decision_ts"),
        "latest_bar_key": decision.get("bar_key"),
        "current_decision_source_mode": "recompute_recent",
        "frame_source_mode": "recompute_recent",
        "gate_on": bool(decision.get("gate_on")),
        "latest_longs": ",".join(decision.get("longs") or []),
        "latest_shorts": ",".join(decision.get("shorts") or []),
        "eligible_universe_size": decision.get("eligible_universe_size"),
        "signal_hash": decision.get("signal_hash"),
        "current_decision_path": str(CURRENT_DECISION_PATH.relative_to(ROOT)),
        "signal_snapshot_path": str(SIGNAL_SNAPSHOT_PATH.relative_to(ROOT)),
    }

    save_json(CURRENT_DECISION_PATH, decision)
    save_json(SIGNAL_SNAPSHOT_PATH, signal)
    save_json(STATUS_PATH, status)
    recent = write_recent(RECENT_DECISIONS_PATH, decision, signal)
    summary = {
        "generated_at_utc": now,
        "status": status["status"],
        "decision_ts": decision.get("decision_ts"),
        "planned_exit_ts": decision.get("planned_exit_ts"),
        "longs": decision.get("longs"),
        "shorts": decision.get("shorts"),
        "signal_hash": decision.get("signal_hash"),
        "recent_rows": len(recent),
    }
    save_json(RUN_SUMMARY_PATH, summary)
    write_html(status, decision, signal)
    print(f"wrote {CURRENT_DECISION_PATH.relative_to(ROOT)}")
    print(f"wrote {STATUS_PATH.relative_to(ROOT)}")
    print(f"wrote {SITE_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
