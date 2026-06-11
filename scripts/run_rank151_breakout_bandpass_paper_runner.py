#!/usr/bin/env python3
from __future__ import annotations

"""Minimal dedicated paper runner for Rank 151 / EWMAC breakout band-pass gate.

What this does
- Takes the frozen breakout-short event digest for Rank 151 as the current execution source.
- Applies the admitted desk rule: short-side breakout family + band-pass gate (q20 < align_score <= q80).
- Maintains a watermark on closed events so the lane can be initialized and refreshed like other paper runners.
- Writes paper-style artifacts (ledger / status / state / run summary) so the next step can attach scheduler + status page.

What this does NOT do (yet)
- It does not stream live bars or place orders.
- It does not recompute the underlying breakout signal from raw exchange candles.
- Therefore the current mode is explicitly a "runner seed" for launch plumbing, backed by the frozen honest-gate digest.
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "reports" / "artifacts" / "quant_digests" / "ewmac_breakout_alignment_20260323"
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank151_breakout_bandpass_gate"
EVENTS_PATH = SRC_DIR / "event_table.csv"
THRESHOLDS_PATH = SRC_DIR / "thresholds.json"
LEDGER_PATH = ART_DIR / "rank151_paper_closed_trades.csv"
STATUS_PATH = ART_DIR / "rank151_paper_status.csv"
STATE_PATH = ART_DIR / "rank151_paper_state.json"
RUN_SUMMARY_PATH = ART_DIR / "rank151_paper_last_run_summary.json"

CANDIDATE_ID = "rank151_ewmac_breakout_bandpass_gate"
CANDIDATE_RANK = 151
PRIMARY_COST_BPS_PER_SIDE = 6.0
HOLD_BARS = 8
REFRESH_CADENCE = "15m"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_z(ts) -> str:
    return pd.to_datetime(ts, utc=True).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def save_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_csv_or_empty(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path)


def normalize_for_csv(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[col]):
            out[col] = out[col].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return out


def load_filtered_events() -> tuple[pd.DataFrame, dict[str, float]]:
    thresholds = read_json(THRESHOLDS_PATH)
    q20 = float(thresholds["q20"])
    q80 = float(thresholds["q80"])

    events = pd.read_csv(EVENTS_PATH)
    events["ts"] = pd.to_datetime(events["ts"], utc=True)
    events = events[events["event_side"] == -1].copy()
    events = events[(events["align_score"] > q20) & (events["align_score"] <= q80)].copy()
    events = events.sort_values(["ts", "symbol"]).reset_index(drop=True)

    events["candidate_id"] = CANDIDATE_ID
    events["candidate_rank"] = CANDIDATE_RANK
    events["stage"] = "running_autonomous_paper_digest_seed"
    events["scope_tag"] = "breakout_short_bandpass_gate_frozen_digest"
    events["venue_mode"] = "paper_digest_seed"
    events["signal_family"] = "breakout_short"
    events["variant"] = "band_pass"
    events["source"] = "ewmac_breakout_alignment_20260323"
    events["cost_bps_per_side"] = PRIMARY_COST_BPS_PER_SIDE
    events["hold_bars"] = HOLD_BARS
    events["entry_ts"] = events["ts"]
    events["exit_ts"] = events["ts"]
    events["side"] = "short"
    events["gross_bps"] = pd.to_numeric(events["signed_bps"], errors="coerce")
    events["net_bps"] = events["gross_bps"] - 2.0 * PRIMARY_COST_BPS_PER_SIDE
    events["gross_ret"] = events["gross_bps"] / 10000.0
    events["net_ret"] = events["net_bps"] / 10000.0
    events["complete_trade"] = True
    return events, {"q20": q20, "q80": q80}


def initialize_watermark(state: dict, trades: pd.DataFrame) -> None:
    state["watermark_exit_ts_utc"] = iso_z(trades["exit_ts"].max()) if not trades.empty else None


def append_new_rows(state: dict, trades: pd.DataFrame) -> pd.DataFrame:
    watermark = state.get("watermark_exit_ts_utc")
    if not watermark:
        return pd.DataFrame()
    new_rows = trades[trades["exit_ts"] > pd.to_datetime(watermark, utc=True)].copy()
    if not new_rows.empty:
        state["watermark_exit_ts_utc"] = iso_z(new_rows["exit_ts"].max())
    return new_rows


def build_status_row(trades: pd.DataFrame, thresholds: dict[str, float], new_trades_appended: int, state: dict) -> dict:
    total_return = float((1.0 + trades["net_ret"]).prod() - 1.0) if not trades.empty else 0.0
    return {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "stage": "running_autonomous_paper_digest_seed",
        "family": "breakout_short",
        "variant": "band_pass",
        "venue_mode": "paper_digest_seed",
        "runner_mode": "frozen_digest_runner_seed",
        "refresh_cadence": REFRESH_CADENCE,
        "source": "quant_digests/ewmac_breakout_alignment_20260323/event_table.csv",
        "threshold_q20": thresholds["q20"],
        "threshold_q80": thresholds["q80"],
        "cost_bps_per_side": PRIMARY_COST_BPS_PER_SIDE,
        "sample_start_utc": iso_z(trades["entry_ts"].min()) if not trades.empty else None,
        "sample_end_utc": iso_z(trades["exit_ts"].max()) if not trades.empty else None,
        "closed_trades": int(len(trades)),
        "new_trades_appended": int(new_trades_appended),
        "lifetime_total_return_6bps": total_return,
        "mean_net_bps": float(trades["net_bps"].mean()) if not trades.empty else 0.0,
        "win_rate": float((trades["net_bps"] > 0).mean()) if not trades.empty else 0.0,
        "asset_coverage": int(trades["symbol"].nunique()) if not trades.empty else 0,
        "open_position": "none",
        "watermark_exit_ts_utc": state.get("watermark_exit_ts_utc"),
        "note": "autonomous paper lane verified: host cron + status page are live; this remains a frozen-digest paper runner seed until a separate raw-bar scope is approved.",
        "updated_at_utc": iso_z(utc_now()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank151 breakout band-pass paper runner seed.")
    parser.add_argument("--init-from-now", action="store_true", help="Initialize watermark from current closed trades and start tracking from now.")
    parser.add_argument("--refresh", action="store_true", help="Append newly closed trades since stored watermark.")
    parser.add_argument("--force-reinit", action="store_true", help="Allow reinitialization even if state exists.")
    args = parser.parse_args()

    if not args.init_from_now and not args.refresh:
        parser.error("choose one of --init-from-now or --refresh")

    ensure_dir(ART_DIR)
    state = load_state()

    if args.init_from_now and state and not args.force_reinit:
        parser.error(f"state already exists at {STATE_PATH}; use --force-reinit to reset")
    if args.refresh and not state:
        parser.error(f"missing state at {STATE_PATH}; run --init-from-now first")

    trades, thresholds = load_filtered_events()
    trades = trades[[
        "candidate_id", "candidate_rank", "stage", "symbol", "variant", "signal_family", "venue_mode", "source",
        "entry_ts", "exit_ts", "side", "align_score", "gross_bps", "net_bps", "gross_ret", "net_ret",
        "cost_bps_per_side", "hold_bars", "complete_trade"
    ]].copy()

    if args.init_from_now:
        state = {
            "initialized_at_utc": iso_z(utc_now()),
            "mode": "rank151_breakout_bandpass_runner_seed",
            "source": "frozen_digest",
            "notes": "Current launch plumbing seed. Uses honest-gate digest, not raw-bar live recomputation.",
            "watermark_exit_ts_utc": None,
        }
        initialize_watermark(state, trades)
        save_state(state)
        if LEDGER_PATH.exists():
            LEDGER_PATH.unlink()
        appended = pd.DataFrame()
    else:
        appended = append_new_rows(state, trades)
        save_state(state)
        if not appended.empty:
            prior = read_csv_or_empty(LEDGER_PATH)
            combined = pd.concat([prior, normalize_for_csv(appended)], ignore_index=True) if not prior.empty else normalize_for_csv(appended)
            combined.to_csv(LEDGER_PATH, index=False)

    status_df = pd.DataFrame([build_status_row(trades, thresholds, len(appended), state)])
    normalize_for_csv(status_df).to_csv(STATUS_PATH, index=False)

    summary = {
        "run_at_utc": iso_z(utc_now()),
        "mode": "init_from_now" if args.init_from_now else "refresh",
        "runner": "rank151_breakout_bandpass_paper_runner_seed",
        "source": "frozen_digest",
        "closed_trades_total": int(len(trades)),
        "new_closed_trades_appended": int(len(appended)),
        "asset_coverage": int(trades["symbol"].nunique()) if not trades.empty else 0,
        "status_path": str(STATUS_PATH.relative_to(ROOT)),
        "ledger_path": str(LEDGER_PATH.relative_to(ROOT)),
        "state_path": str(STATE_PATH.relative_to(ROOT)),
    }
    RUN_SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
