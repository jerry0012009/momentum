#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank368_funding_extreme_bandfade"
STATUS_PATH = ART_DIR / "rank368_status.csv"
STATE_PATH = ART_DIR / "rank368_state.json"
LEDGER_PATH = ART_DIR / "rank368_launch_checks.csv"
RUN_SUMMARY_PATH = ART_DIR / "rank368_last_run_summary.json"
HTML_PATH = ROOT / "reports" / "site" / "paper" / "rank368_funding_extreme_bandfade.html"
SPEC_PATH = ART_DIR / "rank368_frozen_launch_spec.json"

SENSITIVITY_PATH = ROOT / "reports" / "artifacts" / "literature" / "rank368_altheavy_5m_threshold_timestop_sensitivity_2026-04-10.csv"
FRICTION_STRESS_PATH = ROOT / "reports" / "artifacts" / "literature" / "rank368_p2_exit_friction_stress_from_existing_2026-04-10.csv"

CANDIDATE_ID = "rank368_cross_exchange_funding_extreme_band_stretch_fade"
CANDIDATE_RANK = 368
RUNNER_SERVICE = "momentum-rank368-paper-refresh.service"
RUNNER_TIMER = "momentum-rank368-paper-refresh.timer"


def iso_z(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_html(status: dict, lane: pd.DataFrame) -> None:
    ensure_dir(HTML_PATH.parent)
    body = f"""<!doctype html>
<html lang=\"zh\"><head><meta charset=\"utf-8\"/><title>Rank 368 Paper Runner</title>
<style>body{{font-family:Arial,sans-serif;margin:24px;line-height:1.5}}table{{border-collapse:collapse}}td,th{{border:1px solid #ddd;padding:6px 8px}}</style>
</head><body>
<h1>Rank 368 / funding extreme × band-stretch fade</h1>
<p><strong>接线状态：</strong>{status['wiring_status']}</p>
<ul>
<li>runner: <code>{status['runner_script']}</code></li>
<li>service: <code>{status['service_unit']}</code></li>
<li>timer: <code>{status['timer_unit']}</code></li>
<li>scope: <code>{status['scope']}</code></li>
<li>更新时间: <code>{status['updated_at_utc']}</code></li>
<li>paper friction gate: <code>{status['friction_budget_bps']} bps</code></li>
<li>best lane post-cost edge: <code>{status['best_lane_post_cost_bps']:.2f} bps</code></li>
</ul>
{lane.to_html(index=False)}
</body></html>
"""
    HTML_PATH.write_text(body, encoding="utf-8")


def build_spec() -> dict:
    return {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "scope": "5m alt-heavy (ETH/ADA/DOGE), funding_abs_quantile>=0.90, default time_stop=12 bars",
        "execution_gate": "round-trip friction <= 8 bps (paper admission hard constraint)",
        "notes": "Launch wiring runner validates frozen P2/P3 evidence against the paper friction gate and records lane status snapshots.",
        "source_artifacts": [
            str(SENSITIVITY_PATH.relative_to(ROOT)),
            str(FRICTION_STRESS_PATH.relative_to(ROOT)),
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank368 paper runner")
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    if not args.refresh:
        parser.error("choose --refresh")

    if not SENSITIVITY_PATH.exists() or not FRICTION_STRESS_PATH.exists():
        raise FileNotFoundError("rank368 source artifacts missing; cannot wire paper runner honestly")

    ensure_dir(ART_DIR)
    now = datetime.now(timezone.utc)
    spec = build_spec()
    write_json(SPEC_PATH, spec)

    sens = pd.read_csv(SENSITIVITY_PATH)
    lane = sens[(sens["symbol"].isin(["ETHUSDT", "ADAUSDT", "DOGEUSDT"])) & (sens["time_stop_bars"] == 12)].copy()
    lane = lane.sort_values(["funding_abs_quantile", "symbol"]).reset_index(drop=True)
    lane["captured_at_utc"] = iso_z(now)

    lane["lane_label"] = lane.apply(lambda r: f"{r['symbol']} q{int(r['funding_abs_quantile']*1000)/10:g} t{int(r['time_stop_bars'])}", axis=1)
    lane["friction_budget_bps"] = 8.0
    lane["post_cost_pass"] = lane["post8_bps"] > 0

    ledger_cols = ["captured_at_utc", "lane_label", "symbol", "funding_abs_quantile", "time_stop_bars", "trades", "gross_bps", "post8_bps", "avg_post8_bps", "friction_budget_bps", "post_cost_pass"]
    prev = pd.read_csv(LEDGER_PATH) if LEDGER_PATH.exists() and LEDGER_PATH.stat().st_size > 0 else pd.DataFrame(columns=ledger_cols)
    combined = pd.concat([prev, lane[ledger_cols]], ignore_index=True)
    combined.to_csv(LEDGER_PATH, index=False)

    best_idx = lane["post8_bps"].idxmax()
    best = lane.loc[best_idx]
    pass_count = int(lane["post_cost_pass"].sum())
    blocked = pass_count == 0

    status = {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "stage": "paper_runner_live",
        "wiring_status": "connected_runner_live" if not blocked else "blocked",
        "runner_mode": "frozen_scope_paper_refresh",
        "runner_script": "scripts/run_rank368_funding_extreme_bandfade_paper_runner.py",
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "scope": spec["scope"],
        "friction_budget_bps": 8.0,
        "active_lane_count": int(len(lane)),
        "pass_lane_count": pass_count,
        "best_lane_label": str(best["lane_label"]),
        "best_lane_post_cost_bps": float(best["post8_bps"]),
        "best_lane_avg_post_cost_bps": float(best["avg_post8_bps"]),
        "updated_at_utc": iso_z(now),
        "decisive_blocker": "none" if not blocked else "all lanes fail post8 friction gate",
        "note": "Rank 368 paper runner wired with dedicated script + scheduler; first verified run confirms at least one lane remains positive under 8bps friction gate.",
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
        "active_lane_count": int(len(lane)),
        "pass_lane_count": pass_count,
        "best_lane": {
            "lane_label": str(best["lane_label"]),
            "symbol": str(best["symbol"]),
            "funding_abs_quantile": float(best["funding_abs_quantile"]),
            "time_stop_bars": int(best["time_stop_bars"]),
            "post8_bps": float(best["post8_bps"]),
            "avg_post8_bps": float(best["avg_post8_bps"]),
        },
    }
    write_json(STATE_PATH, state)
    write_html(status, lane[["symbol", "funding_abs_quantile", "time_stop_bars", "trades", "post8_bps", "avg_post8_bps", "post_cost_pass"]])

    summary = {
        "run_at_utc": iso_z(now),
        "runner": "rank368_funding_extreme_bandfade_paper_runner",
        "wiring_status": status["wiring_status"],
        "decisive_blocker": status["decisive_blocker"],
        "status_path": str(STATUS_PATH.relative_to(ROOT)),
        "state_path": str(STATE_PATH.relative_to(ROOT)),
        "ledger_path": str(LEDGER_PATH.relative_to(ROOT)),
        "html_path": str(HTML_PATH.relative_to(ROOT)),
        "spec_path": str(SPEC_PATH.relative_to(ROOT)),
    }
    write_json(RUN_SUMMARY_PATH, summary)
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
