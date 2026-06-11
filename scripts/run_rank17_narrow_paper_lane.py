#!/usr/bin/env python3
from __future__ import annotations

"""Dedicated narrow paper lane runner for Rank 17 (ETH-USD + SOL-USD).

Why this exists
- Rank 17 already lives inside scripts/run_manual_narrow_paper_lanes.py (shared runner).
- This script isolates Rank 17 so it can be scheduled, monitored and debugged independently.

Behavior
- Recomputes the lane from a rolling Binance spot 15m window (default 150d).
- Maintains a state watermark per (candidate_id, asset).
- On refresh, appends only newly closed trades since the last watermark.

Notes
- This is paper-only. It does NOT place orders.
- It is intentionally strict about scope: ETH-USD + SOL-USD only.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.analytics.multi_tf_momentum_backtest import (  # noqa: E402
    MultiTfMomentumBacktestConfig,
    evaluate_multi_tf_momentum_reversal,
)
from momentum.signals.pullback_recovery_confirmation import (  # noqa: E402
    PullbackRecoveryConfirmationConfig,
    compute_pullback_recovery_confirmation_signals,
)

ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank17_pullback_ethsol_narrow_pilot"
LEDGER_PATH = ART_DIR / "rank17_paper_closed_trades.csv"
STATUS_PATH = ART_DIR / "rank17_paper_status.csv"
OPEN_POSITIONS_PATH = ART_DIR / "rank17_paper_open_positions.csv"
STATE_PATH = ART_DIR / "rank17_paper_state.json"
RUN_SUMMARY_PATH = ART_DIR / "rank17_paper_last_run_summary.json"

ASSET_TO_BINANCE = {
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_z(ts) -> str:
    return pd.to_datetime(ts, utc=True).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_csv_or_empty(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path)


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {}
    return json.loads(STATE_PATH.read_text())


def save_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True))


def download_binance_bars(symbol: str, *, interval: str = "15m", days: int = 150) -> pd.DataFrame:
    end_ms = int(pd.Timestamp.now("UTC").timestamp() * 1000)
    start_ms = end_ms - days * 24 * 60 * 60 * 1000
    url = "https://api.binance.com/api/v3/klines"
    rows: list[list] = []
    current = start_ms

    while current < end_ms:
        qs = urlencode(
            {
                "symbol": symbol,
                "interval": interval,
                "startTime": current,
                "endTime": end_ms,
                "limit": 1000,
            }
        )
        with urlopen(f"{url}?{qs}", timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if not data:
            break
        rows.extend(data)
        last_close_time = int(data[-1][6])
        current = last_close_time + 1
        if len(data) < 1000:
            break

    if not rows:
        raise ValueError(f"No Binance data for {symbol}")

    df = pd.DataFrame(
        rows,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base_asset_volume",
            "taker_buy_quote_asset_volume",
            "ignore",
        ],
    )
    out = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(df["open_time"], unit="ms", utc=True),
            "close_ts": pd.to_datetime(df["close_time"], unit="ms", utc=True),
            "open": pd.to_numeric(df["open"], errors="coerce"),
            "high": pd.to_numeric(df["high"], errors="coerce"),
            "low": pd.to_numeric(df["low"], errors="coerce"),
            "close": pd.to_numeric(df["close"], errors="coerce"),
            "volume": pd.to_numeric(df["volume"], errors="coerce"),
        }
    )
    out = out.dropna().sort_values("timestamp").reset_index(drop=True)
    now_ts = pd.Timestamp.now("UTC")
    out = out[out["close_ts"] < now_ts].copy()
    return out.reset_index(drop=True)


def build_rank17_signals(bars: pd.DataFrame) -> pd.DataFrame:
    sig = compute_pullback_recovery_confirmation_signals(
        bars,
        config=PullbackRecoveryConfirmationConfig(
            window_5m=6,
            window_15m=6,
            threshold_5m=0.003,
            threshold_15m=0.006,
            resample_rule_15m="15min",
            vol_window=20,
            pullback_lookback=2,
            pullback_vol_z_max=0.0,
            vol_recover_th=1.0,
            breakout_lookback=1,
        ),
    )
    sig["timestamp"] = pd.to_datetime(sig["timestamp"], utc=True)
    return sig


def compute_rank17_lane(asset: str, raw_bars: pd.DataFrame) -> tuple[pd.DataFrame, dict, dict | None]:
    bars = raw_bars.copy()
    bars["symbol"] = asset

    sig = build_rank17_signals(bars)
    bt = evaluate_multi_tf_momentum_reversal(
        sig,
        config=MultiTfMomentumBacktestConfig(
            fee_bps_per_side=6.0,
            slippage_bps_per_side=0.0,
            flip_on_reverse_signal=True,
        ),
    )
    trades = bt.trades.copy()
    if trades.empty:
        status = {
            "candidate_id": "rank17_pullback_ethsol_narrow_pilot",
            "candidate_rank": 17,
            "stage": "P3_narrow_paper_pilot",
            "asset": asset,
            "scope_tag": "narrow_paper_pilot_eth_sol_only",
            "venue_mode": "paper_binance_spot",
            "signal_family": "pullback_recovery_confirmation",
            "sample_end_utc": iso_z(bars["timestamp"].iloc[-1]),
            "latest_closed_exit_ts_utc": None,
            "lifetime_total_return_6bps": 0.0,
            "new_trades_appended": 0,
            "open_position": "none",
            "open_entry_ts_utc": None,
            "open_side": None,
        }
        return pd.DataFrame(), status, None

    for col in ["signal_ts", "entry_ts", "exit_ts"]:
        trades[col] = pd.to_datetime(trades[col], utc=True)
    trades["asset"] = asset
    trades["variant"] = "pullback2_vol1.0_break1"
    trades["cost_bps_per_side"] = 6.0
    trades["candidate_id"] = "rank17_pullback_ethsol_narrow_pilot"
    trades["candidate_rank"] = 17
    trades["stage"] = "P3_narrow_paper_pilot"
    trades["scope_tag"] = "narrow_paper_pilot_eth_sol_only"
    trades["venue_mode"] = "paper_binance_spot"
    trades["signal_family"] = "pullback_recovery_confirmation"
    trades["source"] = "binance_spot_15m"
    trades["complete_trade"] = trades["exit_reason"] != "force_close_final_bar"

    closed = trades[trades["complete_trade"]].copy().reset_index(drop=True)
    open_trade = trades[~trades["complete_trade"]].copy().sort_values("entry_ts").tail(1)
    open_row = None if open_trade.empty else open_trade.iloc[0].to_dict()

    if not closed.empty:
        latest_closed = closed.iloc[-1]
        lifetime = float((1.0 + closed["net_ret"]).prod() - 1.0)
        latest_closed_ts = iso_z(latest_closed["exit_ts"])
    else:
        lifetime = 0.0
        latest_closed_ts = None

    status = {
        "candidate_id": "rank17_pullback_ethsol_narrow_pilot",
        "candidate_rank": 17,
        "stage": "P3_narrow_paper_pilot",
        "asset": asset,
        "scope_tag": "narrow_paper_pilot_eth_sol_only",
        "venue_mode": "paper_binance_spot",
        "signal_family": "pullback_recovery_confirmation",
        "sample_end_utc": iso_z(bars["timestamp"].iloc[-1]),
        "latest_closed_exit_ts_utc": latest_closed_ts,
        "lifetime_total_return_6bps": lifetime,
        "new_trades_appended": 0,
        "open_position": "open" if open_row else "none",
        "open_entry_ts_utc": iso_z(open_row["entry_ts"]) if open_row else None,
        "open_side": open_row.get("side") if open_row else None,
    }
    return closed, status, open_row


def lane_key(candidate_id: str, asset: str) -> str:
    return f"{candidate_id}::{asset}"


def normalize_for_csv(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[col]):
            out[col] = out[col].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return out


def initialize_watermarks(state: dict, closed_df: pd.DataFrame) -> None:
    watermarks = state.setdefault("watermarks", {})
    if closed_df.empty:
        return
    for (candidate_id, asset), sub in closed_df.groupby(["candidate_id", "asset"], sort=False):
        sub = sub.sort_values("exit_ts")
        watermarks[lane_key(str(candidate_id), str(asset))] = iso_z(sub["exit_ts"].iloc[-1])


def append_new_rows(state: dict, closed_df: pd.DataFrame) -> tuple[pd.DataFrame, dict[int, int]]:
    if closed_df.empty:
        return pd.DataFrame(), {}
    watermarks = state.setdefault("watermarks", {})
    out_rows: list[pd.DataFrame] = []
    counts: dict[int, int] = {}

    for (candidate_id, asset), sub in closed_df.groupby(["candidate_id", "asset"], sort=False):
        key = lane_key(str(candidate_id), str(asset))
        watermark = watermarks.get(key)
        sub = sub.sort_values("exit_ts").copy()

        if watermark:
            sub = sub[sub["exit_ts"] > pd.to_datetime(watermark, utc=True)].copy()
            if sub.empty:
                continue
            out_rows.append(sub)
            watermarks[key] = iso_z(sub["exit_ts"].max())
            counts[int(sub.iloc[0]["candidate_rank"]) ] = counts.get(int(sub.iloc[0]["candidate_rank"]), 0) + len(sub)
        else:
            # Start tracking from current watermark without backfilling.
            watermarks[key] = iso_z(sub["exit_ts"].max())

    if not out_rows:
        return pd.DataFrame(), counts
    return pd.concat(out_rows, ignore_index=True), counts


def build_open_positions_frame(open_rows: list[dict | None]) -> pd.DataFrame:
    rows = []
    for item in open_rows:
        if not item:
            continue
        rows.append(
            {
                "candidate_id": item.get("candidate_id"),
                "candidate_rank": item.get("candidate_rank"),
                "asset": item.get("asset"),
                "entry_ts_utc": iso_z(item.get("entry_ts")),
                "exit_ts_marked_utc": iso_z(item.get("exit_ts")),
                "side": item.get("side") or item.get("direction"),
                "signal_family": item.get("signal_family"),
                "note": "open paper position inferred from incomplete final sample; wait for next refresh to confirm close",
            }
        )
    return pd.DataFrame(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Dedicated Rank 17 narrow paper lane runner (ETH-USD + SOL-USD) using Binance spot 15m data.")
    parser.add_argument("--init-from-now", action="store_true", help="Initialize watermarks from current closed trades and start tracking from now.")
    parser.add_argument("--refresh", action="store_true", help="Refresh from Binance and append new closed trades since initialization.")
    parser.add_argument("--days", type=int, default=150, help="Historical Binance window to recompute each lane.")
    parser.add_argument("--force-reinit", action="store_true", help="Allow reinitializing even if state already exists.")
    args = parser.parse_args()

    if not args.init_from_now and not args.refresh:
        parser.error("choose one of --init-from-now or --refresh")

    ensure_dir(ART_DIR)
    state = load_state()

    if args.init_from_now and state and not args.force_reinit:
        parser.error(f"state already exists at {STATE_PATH}; use --force-reinit to reset")
    if args.refresh and not state:
        parser.error(f"missing state at {STATE_PATH}; run --init-from-now first")

    bars_cache = {asset: download_binance_bars(symbol, interval="15m", days=args.days) for asset, symbol in ASSET_TO_BINANCE.items()}

    closed_frames: list[pd.DataFrame] = []
    status_rows: list[dict] = []
    open_rows: list[dict | None] = []

    for asset in ["ETH-USD", "SOL-USD"]:
        closed, status, open_row = compute_rank17_lane(asset, bars_cache[asset])
        closed_frames.append(closed)
        status_rows.append(status)
        open_rows.append(open_row)

    all_closed = pd.concat([df for df in closed_frames if not df.empty], ignore_index=True) if any(not df.empty for df in closed_frames) else pd.DataFrame()

    if args.init_from_now:
        state = {
            "initialized_at_utc": iso_z(utc_now()),
            "mode": "rank17_narrow_paper_only",
            "source": "binance_spot_15m",
            "notes": "Kickoff from current closed-trade watermark; later refresh appends only trades closed after init.",
            "watermarks": {},
        }
        initialize_watermarks(state, all_closed)
        save_state(state)
        if LEDGER_PATH.exists():
            LEDGER_PATH.unlink()
        appended = pd.DataFrame()
        append_counts: dict[int, int] = {}
    else:
        appended, append_counts = append_new_rows(state, all_closed)
        save_state(state)
        if not appended.empty:
            prior = read_csv_or_empty(LEDGER_PATH)
            combined = pd.concat([prior, normalize_for_csv(appended)], ignore_index=True) if not prior.empty else normalize_for_csv(appended)
            combined.to_csv(LEDGER_PATH, index=False)

    for row in status_rows:
        row["new_trades_appended"] = int(append_counts.get(int(row["candidate_rank"]), 0)) if args.refresh else 0
        key = lane_key(row["candidate_id"], row["asset"])
        row["watermark_exit_ts_utc"] = state.get("watermarks", {}).get(key)

    status_df = pd.DataFrame(status_rows).sort_values(["candidate_rank", "asset"]).reset_index(drop=True)
    normalize_for_csv(status_df).to_csv(STATUS_PATH, index=False)

    open_df = build_open_positions_frame(open_rows)
    if open_df.empty:
        OPEN_POSITIONS_PATH.write_text("candidate_id,candidate_rank,asset,entry_ts_utc,exit_ts_marked_utc,side,signal_family,note\n")
    else:
        normalize_for_csv(open_df).to_csv(OPEN_POSITIONS_PATH, index=False)

    summary = {
        "run_at_utc": iso_z(utc_now()),
        "mode": "init_from_now" if args.init_from_now else "refresh",
        "source": "binance_spot_15m",
        "days": int(args.days),
        "lanes_tracked": int(len(status_rows)),
        "new_closed_trades_appended": int(len(appended)) if args.refresh else 0,
        "status_path": str(STATUS_PATH.relative_to(ROOT)),
        "open_positions_path": str(OPEN_POSITIONS_PATH.relative_to(ROOT)),
        "ledger_path": str(LEDGER_PATH.relative_to(ROOT)),
        "state_path": str(STATE_PATH.relative_to(ROOT)),
    }
    RUN_SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))

    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
