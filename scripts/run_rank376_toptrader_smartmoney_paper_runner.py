#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank376_toptrader_smartmoney"
STATUS_PATH = ART_DIR / "rank376_status.csv"
STATE_PATH = ART_DIR / "rank376_state.json"
LEDGER_PATH = ART_DIR / "rank376_launch_checks.csv"
RUN_SUMMARY_PATH = ART_DIR / "rank376_last_run_summary.json"
SIGNAL_FRAME_PATH = ART_DIR / "rank376_current_signal_frame.csv"
SPEC_PATH = ART_DIR / "rank376_frozen_launch_spec.json"
HTML_PATH = ROOT / "reports" / "site" / "paper" / "rank376_toptrader_smartmoney.html"

SOURCE_PATH = ROOT / "reports" / "artifacts" / "literature" / "binance_toptrader_smartmoney_probe_detail_2026-04-10.csv"

CANDIDATE_ID = "rank376_toptrader_smartmoney_skew_continuation"
CANDIDATE_RANK = 376
RUNNER_SERVICE = "momentum-rank376-paper-refresh.service"
RUNNER_TIMER = "momentum-rank376-paper-refresh.timer"


def iso_z(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_html(status: dict, view: pd.DataFrame) -> None:
    ensure_dir(HTML_PATH.parent)
    body = f"""<!doctype html>
<html lang=\"zh\"><head><meta charset=\"utf-8\"/><title>Rank 376 Paper Runner</title>
<style>body{{font-family:Arial,sans-serif;margin:24px;line-height:1.5}}table{{border-collapse:collapse}}td,th{{border:1px solid #ddd;padding:6px 8px}}</style>
</head><body>
<h1>Rank 376 / top-trader smartmoney skew continuation（BTC+ETH scoped）</h1>
<p><strong>接线状态：</strong>{status['wiring_status']}</p>
<ul>
<li>runner: <code>{status['runner_script']}</code></li>
<li>service: <code>{status['service_unit']}</code></li>
<li>timer: <code>{status['timer_unit']}</code></li>
<li>scope: <code>{status['scope']}</code></li>
<li>更新时间: <code>{status['updated_at_utc']}</code></li>
<li>friction gate: <code>{status['friction_budget_bps']} bps</code></li>
<li>best lane avg net edge: <code>{status['best_lane_avg_net_bps']:.2f} bps/笔</code></li>
</ul>
{view.to_html(index=False)}
</body></html>
"""
    HTML_PATH.write_text(body, encoding="utf-8")


def build_spec() -> dict:
    return {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "scope": "BTC+ETH only; 5m bars; lag=1 bar entry; fixed 12-bar time-stop; ETH short when top_log_z<-2.0, BTC long when top_log_z>2.0",
        "execution_gate": "round-trip friction <= 12 bps (paper launch hard gate)",
        "notes": "SOL leg removed due to time-stability break in P2 exit decision; launch runner tracks only BTC+ETH scoped lanes.",
        "source_artifacts": [str(SOURCE_PATH.relative_to(ROOT))],
    }


def lane_stats(df: pd.DataFrame, symbol: str, side: str, z_rule: str, z_col: str, friction_bps: float) -> dict:
    part = df[df["symbol"] == symbol].copy()
    if side == "long":
        sig = part[part[z_col] > float(z_rule)]
        net = sig["fwd_ret"] * 10000 - friction_bps
    else:
        sig = part[part[z_col] < float(z_rule)]
        net = -sig["fwd_ret"] * 10000 - friction_bps
    trades = int(len(sig))
    avg_net = float(net.mean()) if trades > 0 else float("nan")
    gross = float((net + friction_bps).mean()) if trades > 0 else float("nan")
    return {
        "symbol": symbol,
        "side": side,
        "z_col": z_col,
        "z_rule": z_rule,
        "trades": trades,
        "gross_bps": gross,
        "avg_net_bps": avg_net,
        "friction_budget_bps": friction_bps,
        "post_cost_pass": bool(trades > 0 and avg_net > 0),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank376 paper runner")
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    if not args.refresh:
        parser.error("choose --refresh")

    if not SOURCE_PATH.exists():
        raise FileNotFoundError("rank376 source artifact missing; cannot wire paper runner honestly")

    ensure_dir(ART_DIR)
    now = datetime.now(timezone.utc)
    spec = build_spec()
    write_json(SPEC_PATH, spec)

    df = pd.read_csv(SOURCE_PATH)
    df = df[df["interval"] == "5m"].copy()
    df["ts"] = pd.to_datetime(df["ts"], utc=True, errors="coerce")
    df = df.sort_values(["symbol", "ts"]).reset_index(drop=True)

    lanes = [
        lane_stats(df, "ETHUSDT", "short", "-2.0", "top_log_z", 12.0),
        lane_stats(df, "BTCUSDT", "long", "2.0", "top_log_z", 12.0),
    ]
    lane_df = pd.DataFrame(lanes)
    lane_df["captured_at_utc"] = iso_z(now)
    lane_df.to_csv(SIGNAL_FRAME_PATH, index=False)

    ledger_cols = ["captured_at_utc", "symbol", "side", "z_col", "z_rule", "trades", "gross_bps", "avg_net_bps", "friction_budget_bps", "post_cost_pass"]
    prev = pd.read_csv(LEDGER_PATH) if LEDGER_PATH.exists() and LEDGER_PATH.stat().st_size > 0 else pd.DataFrame(columns=ledger_cols)
    combined = pd.concat([prev, lane_df[ledger_cols]], ignore_index=True)
    combined.to_csv(LEDGER_PATH, index=False)

    pass_count = int(lane_df["post_cost_pass"].sum())
    blocked = pass_count == 0
    best_row = lane_df.sort_values("avg_net_bps", ascending=False).iloc[0]

    status = {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "stage": "paper_runner_live",
        "wiring_status": "connected_runner_live" if not blocked else "blocked",
        "runner_mode": "frozen_scope_paper_refresh",
        "runner_script": "scripts/run_rank376_toptrader_smartmoney_paper_runner.py",
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "scope": spec["scope"],
        "friction_budget_bps": 12.0,
        "active_lane_count": int(len(lane_df)),
        "pass_lane_count": pass_count,
        "best_lane": f"{best_row['symbol']} {best_row['side']} z{best_row['z_rule']}",
        "best_lane_avg_net_bps": float(best_row["avg_net_bps"]),
        "updated_at_utc": iso_z(now),
        "decisive_blocker": "none" if not blocked else "all scoped lanes fail post-cost gate",
        "note": "Rank 376 runner wired with BTC+ETH scoped lanes only; first run verifies post-cost pass status under 12bps friction.",
    }
    pd.DataFrame([status]).to_csv(STATUS_PATH, index=False)

    state = {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "wiring_status": status["wiring_status"],
        "runner_mode": status["runner_mode"],
        "runner_script": status["runner_script"],
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "scope": spec["scope"],
        "last_run_at_utc": iso_z(now),
        "active_lane_count": int(len(lane_df)),
        "pass_lane_count": pass_count,
        "best_lane": {
            "symbol": str(best_row["symbol"]),
            "side": str(best_row["side"]),
            "z_col": str(best_row["z_col"]),
            "z_rule": str(best_row["z_rule"]),
            "avg_net_bps": float(best_row["avg_net_bps"]),
            "gross_bps": float(best_row["gross_bps"]),
            "trades": int(best_row["trades"]),
        },
    }
    write_json(STATE_PATH, state)

    write_html(status, lane_df[["symbol", "side", "z_col", "z_rule", "trades", "gross_bps", "avg_net_bps", "post_cost_pass"]])

    summary = {
        "run_at_utc": iso_z(now),
        "runner": "rank376_toptrader_smartmoney_paper_runner",
        "wiring_status": status["wiring_status"],
        "decisive_blocker": status["decisive_blocker"],
        "status_path": str(STATUS_PATH.relative_to(ROOT)),
        "state_path": str(STATE_PATH.relative_to(ROOT)),
        "ledger_path": str(LEDGER_PATH.relative_to(ROOT)),
        "signal_frame_path": str(SIGNAL_FRAME_PATH.relative_to(ROOT)),
        "html_path": str(HTML_PATH.relative_to(ROOT)),
        "spec_path": str(SPEC_PATH.relative_to(ROOT)),
    }
    write_json(RUN_SUMMARY_PATH, summary)
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
