#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
OUT_DIR = ROOT / "reports" / "artifacts" / "quant_digests" / "fib_zone_depth_proxy"

ASSETS = {
    "BTCUSDT": "BTC",
    "ETHUSDT": "ETH",
    "SOLUSDT": "SOL",
}

LOOKBACK = 20
POST_WINDOW = 12
HOLD_BARS = 8
COST_BPS_PER_SIDE = 6.0
COST_RATE = COST_BPS_PER_SIDE / 10000.0
BANDS: list[tuple[str, float, float]] = [
    ("38_50", 0.38, 0.50),
    ("50_62", 0.50, 0.62),
    ("62_71", 0.62, 0.71),
    ("71_79", 0.71, 0.79),
]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_bars(symbol: str, asset: str) -> pd.DataFrame:
    df = pd.read_csv(CACHE_DIR / f"{symbol}__120d__15m.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def build_breakout_frame(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["prev_high_20"] = out["high"].rolling(LOOKBACK, min_periods=LOOKBACK).max().shift(1)
    out["prev_low_20"] = out["low"].rolling(LOOKBACK, min_periods=LOOKBACK).min().shift(1)
    prev_close = out["close"].shift(1)
    tr = pd.concat(
        [
            out["high"] - out["low"],
            (out["high"] - prev_close).abs(),
            (out["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    out["atr14"] = tr.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    body = out["close"] - out["open"]
    candle_range = (out["high"] - out["low"]).replace(0, np.nan)
    out["body_ratio"] = body / candle_range
    out["breakout_extension_atr"] = (out["close"] - out["prev_high_20"]) / out["atr14"]
    out["fresh_breakout"] = (
        (out["close"] > out["prev_high_20"])
        & (out["close"] > out["open"])
        & (out["body_ratio"] >= 0.40)
        & (out["breakout_extension_atr"] >= 0.20)
    ).fillna(False)
    return out


def simulate_asset(frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    last_exit_by_band = {band: -1 for band, _, _ in BANDS}

    for i in range(max(LOOKBACK + 20, 30), len(frame) - POST_WINDOW - 2):
        if not bool(frame.iloc[i]["fresh_breakout"]):
            continue

        anchor_low = float(frame.iloc[i]["prev_low_20"])
        anchor_high = float(frame.iloc[i]["high"])
        if not np.isfinite(anchor_low) or not np.isfinite(anchor_high) or anchor_high <= anchor_low:
            continue
        fib_range = anchor_high - anchor_low

        for band, band_lo, band_hi in BANDS:
            if i <= last_exit_by_band[band]:
                continue

            zone_upper = anchor_high - fib_range * band_lo
            zone_lower = anchor_high - fib_range * band_hi

            touch_idx: int | None = None
            for j in range(i + 1, min(len(frame) - 1, i + POST_WINDOW + 1)):
                lo_px = float(frame.iloc[j]["low"])
                hi_px = float(frame.iloc[j]["high"])
                if lo_px <= zone_upper and hi_px >= zone_lower:
                    touch_idx = j
                    break

            if touch_idx is None or touch_idx + 1 >= len(frame):
                continue

            entry_idx = touch_idx + 1
            entry_px = float(frame.iloc[entry_idx]["open"])
            if not np.isfinite(entry_px) or entry_px <= 0:
                continue

            exit_idx = min(len(frame) - 1, entry_idx + HOLD_BARS - 1)
            exit_px = float(frame.iloc[exit_idx]["close"])
            exit_reason = "time_stop"
            success = 0

            for k in range(entry_idx, min(len(frame), entry_idx + HOLD_BARS)):
                lo_px = float(frame.iloc[k]["low"])
                hi_px = float(frame.iloc[k]["high"])
                if lo_px <= anchor_low:
                    exit_idx = k
                    exit_px = anchor_low
                    exit_reason = "stop_100"
                    success = 0
                    break
                if hi_px >= anchor_high:
                    exit_idx = k
                    exit_px = anchor_high
                    exit_reason = "tp_0"
                    success = 1
                    break

            gross_ret = exit_px / entry_px - 1.0
            net_ret = (1.0 + gross_ret) * (1.0 - COST_RATE) * (1.0 - COST_RATE) - 1.0

            rows.append(
                {
                    "asset": frame.iloc[i]["asset"],
                    "band": band,
                    "signal_ts": pd.to_datetime(frame.iloc[i]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "touch_ts": pd.to_datetime(frame.iloc[touch_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "entry_ts": pd.to_datetime(frame.iloc[entry_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "exit_ts": pd.to_datetime(frame.iloc[exit_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "bars_to_touch": int(touch_idx - i),
                    "entry_price": entry_px,
                    "exit_price": exit_px,
                    "gross_ret": gross_ret,
                    "net_ret": net_ret,
                    "success": int(success),
                    "exit_reason": exit_reason,
                    "anchor_low": anchor_low,
                    "anchor_high": anchor_high,
                    "anchor_range_pct": fib_range / anchor_low,
                    "breakout_body_ratio": float(frame.iloc[i]["body_ratio"]),
                    "breakout_extension_atr": float(frame.iloc[i]["breakout_extension_atr"]),
                }
            )
            last_exit_by_band[band] = exit_idx

    return pd.DataFrame(rows)


def summarize(trades: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame()
    rows: list[dict[str, object]] = []
    grouped = trades.groupby(group_cols, sort=False)
    for key, grp in grouped:
        if not isinstance(key, tuple):
            key = (key,)
        row = dict(zip(group_cols, key))
        row.update(
            {
                "trades": int(len(grp)),
                "avg_net_ret": float(grp["net_ret"].mean()),
                "win_rate": float((grp["net_ret"] > 0).mean()),
                "success_rate": float(grp["success"].mean()),
                "total_return": float((1.0 + grp["net_ret"]).prod() - 1.0),
                "median_bars_to_touch": float(grp["bars_to_touch"].median()),
                "avg_anchor_range_pct": float(grp["anchor_range_pct"].mean()),
            }
        )
        rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    ensure_dir(OUT_DIR)

    trade_frames: list[pd.DataFrame] = []
    for symbol, asset in ASSETS.items():
        frame = build_breakout_frame(load_bars(symbol, asset))
        trades = simulate_asset(frame)
        if not trades.empty:
            trade_frames.append(trades)

    all_trades = pd.concat(trade_frames, ignore_index=True) if trade_frames else pd.DataFrame()
    all_trades.to_csv(OUT_DIR / "trade_log.csv", index=False)

    asset_summary = summarize(all_trades, ["band", "asset"]).sort_values(["band", "asset"]).reset_index(drop=True)
    overall_summary = summarize(all_trades, ["band"]).sort_values(["band"]).reset_index(drop=True)

    pooled = all_trades.copy()
    pooled["depth_bucket"] = np.where(pooled["band"].isin(["38_50", "50_62"]), "shallow_mid_38_62", "deep_62_79")
    depth_bucket_summary = summarize(pooled, ["depth_bucket"]).sort_values(["depth_bucket"]).reset_index(drop=True)

    if not asset_summary.empty:
        positive_assets = asset_summary.groupby("band")["total_return"].apply(lambda s: float((s > 0).mean())).rename("positive_asset_ratio")
        overall_summary = overall_summary.merge(positive_assets, on="band", how="left")

    asset_summary.to_csv(OUT_DIR / "asset_summary.csv", index=False)
    overall_summary.to_csv(OUT_DIR / "overall_summary.csv", index=False)
    depth_bucket_summary.to_csv(OUT_DIR / "depth_bucket_summary.csv", index=False)

    snapshot = {
        "spec": {
            "sample": "BTC/ETH/SOL | Binance 120d 15m cache",
            "trigger": "fresh_breakout := close > prev_high_20 and bullish body_ratio>=0.40 and breakout_extension_atr>=0.20",
            "entry": "first touch of fib zone within next 12 bars -> next-bar open",
            "exit": "tp at breakout high / stop at breakout-anchor low / else hold 8 bars",
            "bands": [band for band, _, _ in BANDS],
            "cost_bps_per_side": COST_BPS_PER_SIDE,
            "no_overlap": True,
        },
        "headline": overall_summary.to_dict(orient="records"),
        "depth_bucket": depth_bucket_summary.to_dict(orient="records"),
    }
    (OUT_DIR / "summary_snapshot.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")

    print("[ok] fib zone depth proxy built")
    print((OUT_DIR / "overall_summary.csv").as_posix())
    print(overall_summary.to_string(index=False))
    if not depth_bucket_summary.empty:
        print(depth_bucket_summary.to_string(index=False))


if __name__ == "__main__":
    main()
