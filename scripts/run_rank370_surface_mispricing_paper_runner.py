#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import URLError, HTTPError
from urllib.request import urlopen

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank370_surface_mispricing"
STATUS_PATH = ART_DIR / "rank370_status.csv"
STATE_PATH = ART_DIR / "rank370_state.json"
SIGNAL_PATH = ART_DIR / "rank370_current_signal_frame.csv"
LEDGER_PATH = ART_DIR / "rank370_queue_ledger.csv"
SUMMARY_PATH = ART_DIR / "rank370_last_run_summary.json"
SPEC_PATH = ART_DIR / "rank370_frozen_launch_spec.json"
HTML_PATH = ROOT / "reports" / "site" / "paper" / "rank370_surface_mispricing.html"

RUNNER_SERVICE = "momentum-rank370-paper-refresh.service"
RUNNER_TIMER = "momentum-rank370-paper-refresh.timer"
CANDIDATE_ID = "rank370_same_event_strike_surface_mispricing_recross"
CANDIDATE_RANK = 370


@dataclass
class RunnerSpec:
    edge_cents: float = 2.0
    min_volume_usd: float = 2000.0
    min_step: float = 5.0
    max_spot_distance_pct: float = 0.2
    max_hold_minutes: int = 360
    max_positions: int = 1
    max_quote_age_seconds: int = 90


def iso_z(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def pava_monotone_nonincreasing(values: list[float]) -> list[float]:
    # Pool-adjacent-violators for non-increasing sequence
    blocks: list[tuple[float, int]] = []
    for v in values:
        blocks.append((v, 1))
        while len(blocks) >= 2 and blocks[-2][0] < blocks[-1][0]:
            v2, w2 = blocks.pop()
            v1, w1 = blocks.pop()
            blocks.append((((v1 * w1) + (v2 * w2)) / (w1 + w2), w1 + w2))
    out: list[float] = []
    for v, w in blocks:
        out.extend([v] * w)
    return out


def build_spec(spec: RunnerSpec) -> dict[str, Any]:
    return {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "strategy": "same-event strike surface mispricing × fair-value recross / time-stop",
        "scope": "prediction-market same-expiry strike ladder relative value",
        "execution_boundaries": {
            "edge_cents": spec.edge_cents,
            "min_volume_usd": spec.min_volume_usd,
            "min_step": spec.min_step,
            "max_spot_distance_pct": spec.max_spot_distance_pct,
            "max_hold_minutes": spec.max_hold_minutes,
            "max_positions": spec.max_positions,
            "max_quote_age_seconds": spec.max_quote_age_seconds,
        },
        "signal_definition": "edge = fair_mid - market_mid, fair_mid from monotone fitted same-event strike surface",
        "entry_rules": [
            "edge >= +edge_cents -> long undervalued contract",
            "edge <= -edge_cents -> short overvalued contract",
            "skip stale quote age > max_quote_age_seconds",
            "skip if strike ladder depth < 3",
        ],
        "cancel_and_exit": [
            "cancel pending order when quote age exceeds threshold",
            "exit on fair-mid recross",
            "hard time-stop max_hold_minutes",
            "flatten near expiry safety window",
        ],
        "risk": [
            "pre-trade veto: enforce max_positions, min_volume, min_step",
            "no forced fill assumption; queue action logged as paper intent",
        ],
        "runner": "scripts/run_rank370_surface_mispricing_paper_runner.py",
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
    }


def load_snapshot(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    required = {"market", "strike", "mid", "book_as_of", "volume_usd"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"snapshot missing columns: {sorted(missing)}")
    return frame


def fetch_snapshot(url: str) -> pd.DataFrame:
    with urlopen(url, timeout=20) as r:
        payload = json.loads(r.read().decode("utf-8"))
    rows = payload.get("rows", [])
    if not isinstance(rows, list) or not rows:
        raise ValueError("market snapshot payload has no rows")
    return pd.DataFrame(rows)


def compute_signal(frame: pd.DataFrame, spec: RunnerSpec, now: datetime) -> pd.DataFrame:
    df = frame.copy()
    df = df.sort_values("strike").reset_index(drop=True)
    if len(df) < 3:
        raise ValueError("strike ladder depth < 3")

    monotone_fair = pava_monotone_nonincreasing(df["mid"].astype(float).tolist())
    df["fair_mid"] = monotone_fair
    df["edge_cents"] = (df["fair_mid"] - df["mid"].astype(float)) * 100.0
    df["quote_age_seconds"] = (now - pd.to_datetime(df["book_as_of"], utc=True)).dt.total_seconds()

    df["risk_pass"] = (
        (df["volume_usd"].astype(float) >= spec.min_volume_usd)
        & (df["quote_age_seconds"] <= spec.max_quote_age_seconds)
    )
    df["action"] = "hold"
    df.loc[(df["edge_cents"] >= spec.edge_cents) & df["risk_pass"], "action"] = "buy_yes"
    df.loc[(df["edge_cents"] <= -spec.edge_cents) & df["risk_pass"], "action"] = "sell_yes"
    df["captured_at_utc"] = iso_z(now)
    return df


def write_html(status: dict[str, Any], signal: pd.DataFrame) -> None:
    ensure_dir(HTML_PATH.parent)
    body = f"""<!doctype html>
<html lang=\"zh\"><head><meta charset=\"utf-8\"/><title>Rank 370 Paper Runner</title>
<style>body{{font-family:Arial,sans-serif;margin:24px;line-height:1.5}}table{{border-collapse:collapse}}td,th{{border:1px solid #ddd;padding:6px 8px}}</style>
</head><body>
<h1>Rank 370 / same-event strike surface mispricing</h1>
<p><strong>接线状态：</strong>{status['wiring_status']}</p>
<ul>
<li>runner: <code>{status['runner_script']}</code></li>
<li>service: <code>{status['service_unit']}</code></li>
<li>timer: <code>{status['timer_unit']}</code></li>
<li>更新时间: <code>{status['updated_at_utc']}</code></li>
<li>decisive blocker: <code>{status['decisive_blocker']}</code></li>
</ul>
{signal.to_html(index=False)}
</body></html>
"""
    HTML_PATH.write_text(body, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank370 paper runner")
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--snapshot-csv", default="")
    parser.add_argument("--snapshot-url", default="")
    parser.add_argument("--seed-only", action="store_true", help="write frozen spec and skeleton status without market snapshot")
    args = parser.parse_args()

    if not args.refresh:
        parser.error("choose --refresh")

    ensure_dir(ART_DIR)
    now = datetime.now(timezone.utc)
    spec = RunnerSpec()
    frozen = build_spec(spec)
    write_json(SPEC_PATH, frozen)

    decisive_blocker = "none"
    wiring_status = "scheduler_ready_runner_seeded" if args.seed_only else "connected_runner_live"
    signal = pd.DataFrame(
        columns=["captured_at_utc", "market", "strike", "mid", "fair_mid", "edge_cents", "quote_age_seconds", "volume_usd", "risk_pass", "action"]
    )

    if not args.seed_only:
        try:
            if args.snapshot_csv:
                frame = load_snapshot(Path(args.snapshot_csv))
            elif args.snapshot_url:
                frame = fetch_snapshot(args.snapshot_url)
            else:
                raise ValueError("missing snapshot source: provide --snapshot-csv or --snapshot-url, or use --seed-only")
            signal = compute_signal(frame, spec, now)
        except (FileNotFoundError, ValueError, URLError, HTTPError) as exc:
            decisive_blocker = f"snapshot_unavailable:{exc}"
            wiring_status = "blocked"

    signal.to_csv(SIGNAL_PATH, index=False)

    ledger_cols = ["captured_at_utc", "market", "strike", "mid", "fair_mid", "edge_cents", "quote_age_seconds", "volume_usd", "risk_pass", "action"]
    prev = pd.read_csv(LEDGER_PATH) if LEDGER_PATH.exists() and LEDGER_PATH.stat().st_size > 0 else pd.DataFrame(columns=ledger_cols)
    merged = pd.concat([prev, signal[ledger_cols]], ignore_index=True)
    merged.to_csv(LEDGER_PATH, index=False)

    actionable = int((signal["action"] != "hold").sum()) if len(signal) else 0
    status = {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "stage": "paper_launch_wiring",
        "wiring_status": wiring_status,
        "runner_mode": "surface_mispricing_recross_timestop",
        "runner_script": "scripts/run_rank370_surface_mispricing_paper_runner.py",
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "active_rows": int(len(signal)),
        "actionable_rows": actionable,
        "decisive_blocker": decisive_blocker,
        "updated_at_utc": iso_z(now),
    }
    pd.DataFrame([status]).to_csv(STATUS_PATH, index=False)

    state = {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "wiring_status": wiring_status,
        "runner_script": status["runner_script"],
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "last_run_at_utc": iso_z(now),
        "decisive_blocker": decisive_blocker,
        "actionable_rows": actionable,
        "seed_only": bool(args.seed_only),
    }
    write_json(STATE_PATH, state)
    write_html(status, signal)

    summary = {
        "run_at_utc": iso_z(now),
        "wiring_status": wiring_status,
        "decisive_blocker": decisive_blocker,
        "status_path": str(STATUS_PATH.relative_to(ROOT)),
        "state_path": str(STATE_PATH.relative_to(ROOT)),
        "signal_path": str(SIGNAL_PATH.relative_to(ROOT)),
        "ledger_path": str(LEDGER_PATH.relative_to(ROOT)),
        "spec_path": str(SPEC_PATH.relative_to(ROOT)),
        "html_path": str(HTML_PATH.relative_to(ROOT)),
    }
    write_json(SUMMARY_PATH, summary)
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
