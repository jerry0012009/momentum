#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
INTERVAL = "15m"
SAMPLE_DAYS = 45
LOOKAHEAD_BARS = 8
WINDOWS = (128, 192)
MC_PATHS = 80
ACTUAL_STEP = 4
MC_SEED = 15023
BINANCE_URL = "https://fapi.binance.com/fapi/v1/klines"
OUT_DIR = Path("reports/artifacts/scout_rank150_dfa_hurst_persistence_gate_15m")


@dataclass
class CalibrationRow:
    window: int
    mc_paths: int
    mc_series_length: int
    random_walk_mu: float
    random_walk_sigma: float
    low_threshold: float
    high_threshold: float


def dfa_alpha(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    if len(x) < 16 or not np.isfinite(x).all():
        return math.nan
    x = x - np.mean(x)
    y = np.cumsum(x)
    n = len(y)
    max_scale = n // 4
    if max_scale < 8:
        return math.nan
    scales = np.unique(np.floor(np.logspace(np.log10(8), np.log10(max_scale), 8)).astype(int))
    flucts = []
    good_scales = []
    idx_cache = {}
    for scale in scales:
        segments = n // scale
        if segments < 2:
            continue
        trimmed = y[: segments * scale].reshape(segments, scale)
        if scale not in idx_cache:
            idx_cache[scale] = np.arange(scale, dtype=float)
        t = idx_cache[scale]
        rms_vals = []
        for seg in trimmed:
            coeffs = np.polyfit(t, seg, 1)
            trend = coeffs[0] * t + coeffs[1]
            resid = seg - trend
            rms = math.sqrt(float(np.mean(resid * resid)))
            if np.isfinite(rms) and rms > 0:
                rms_vals.append(rms)
        if rms_vals:
            flucts.append(float(np.mean(rms_vals)))
            good_scales.append(scale)
    if len(good_scales) < 2:
        return math.nan
    slope = np.polyfit(np.log(good_scales), np.log(flucts), 1)[0]
    return float(slope)


def rolling_dfa_sparse(close: pd.Series, window: int, step: int = ACTUAL_STEP) -> pd.Series:
    values = close.to_numpy(dtype=float)
    out = np.full(len(values), np.nan)
    for i in range(window - 1, len(values), step):
        out[i] = dfa_alpha(values[i - window + 1 : i + 1])
    return pd.Series(out, index=close.index)


def fetch_klines(symbol: str, days: int = SAMPLE_DAYS, interval: str = INTERVAL) -> pd.DataFrame:
    session = requests.Session()
    end_ms = int(time.time() * 1000)
    start_ms = end_ms - int(days * 24 * 60 * 60 * 1000)
    rows: list[list] = []
    cursor = start_ms
    while True:
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": cursor,
            "endTime": end_ms,
            "limit": 1500,
        }
        resp = session.get(BINANCE_URL, params=params, timeout=30)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        rows.extend(batch)
        last_open = int(batch[-1][0])
        next_cursor = last_open + 1
        if len(batch) < 1500 or next_cursor >= end_ms:
            break
        cursor = next_cursor
        time.sleep(0.08)
    if not rows:
        raise RuntimeError(f"no klines fetched for {symbol}")
    df = pd.DataFrame(rows, columns=[
        "open_time","open","high","low","close","volume","close_time","quote_volume",
        "trade_count","taker_buy_base","taker_buy_quote","ignore"
    ])
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)
    df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    return df[["timestamp", "open", "high", "low", "close", "volume"]].drop_duplicates("timestamp").sort_values("timestamp").reset_index(drop=True)


def monte_carlo_calibration(window: int, rng: np.random.Generator) -> CalibrationRow:
    vals = []
    for _ in range(MC_PATHS):
        increments = rng.normal(0.0, 1.0, size=window)
        walk = np.cumsum(increments)
        vals.append(dfa_alpha(walk))
    arr = np.asarray([v for v in vals if np.isfinite(v)], dtype=float)
    mu = float(arr.mean())
    sigma = float(arr.std(ddof=1))
    return CalibrationRow(
        window=window,
        mc_paths=len(arr),
        mc_series_length=window,
        random_walk_mu=mu,
        random_walk_sigma=sigma,
        low_threshold=float(mu - 0.5 * sigma),
        high_threshold=float(mu + 0.5 * sigma),
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(MC_SEED)
    calibration_rows = [monte_carlo_calibration(w, rng) for w in WINDOWS]
    cal_df = pd.DataFrame([asdict(r) for r in calibration_rows])
    cal_df.to_csv(OUT_DIR / "estimator_calibration_summary.csv", index=False)

    per_asset_rows = []
    pooled_rows = []
    for asset, symbol in ASSETS.items():
        df = fetch_klines(symbol)
        df["fwd_ret_bps_8"] = (df["close"].shift(-LOOKAHEAD_BARS) / df["close"] - 1.0) * 10000.0
        for row in calibration_rows:
            h_col = f"dfa_{row.window}"
            bucket_col = f"bucket_{row.window}"
            df[h_col] = rolling_dfa_sparse(df["close"], row.window)
            df[bucket_col] = np.where(
                df[h_col] < row.low_threshold,
                "low",
                np.where(df[h_col] > row.high_threshold, "high", "mid"),
            )
            usable = df[df[h_col].notna() & df["fwd_ret_bps_8"].notna()].copy()
            for bucket, g in usable.groupby(bucket_col):
                rec = {
                    "asset": asset,
                    "symbol": symbol,
                    "window": row.window,
                    "bucket": bucket,
                    "n": int(len(g)),
                    "share": float(len(g) / len(usable)) if len(usable) else math.nan,
                    "mean_h": float(g[h_col].mean()),
                    "mean_fwd_ret_bps_8": float(g["fwd_ret_bps_8"].mean()),
                    "median_fwd_ret_bps_8": float(g["fwd_ret_bps_8"].median()),
                    "win_rate": float((g["fwd_ret_bps_8"] > 0).mean()),
                }
                per_asset_rows.append(rec)
                pooled_rows.append({k: rec[k] for k in ["window", "bucket", "n", "mean_h", "mean_fwd_ret_bps_8", "median_fwd_ret_bps_8", "win_rate"]})

    pd.DataFrame(per_asset_rows).to_csv(OUT_DIR / "bucket_diagnostics_by_asset.csv", index=False)
    pooled_df = pd.DataFrame(pooled_rows)
    pooled = (
        pooled_df.groupby(["window", "bucket"], as_index=False)
        .apply(lambda g: pd.Series({
            "n": int(g["n"].sum()),
            "mean_h": np.average(g["mean_h"], weights=g["n"]),
            "mean_fwd_ret_bps_8": np.average(g["mean_fwd_ret_bps_8"], weights=g["n"]),
            "median_fwd_ret_bps_8": float(np.nan),
            "win_rate": np.average(g["win_rate"], weights=g["n"]),
        }))
        .reset_index(drop=True)
    )
    totals = pooled.groupby("window")["n"].transform("sum")
    pooled["share"] = pooled["n"] / totals
    pooled.to_csv(OUT_DIR / "bucket_diagnostics_pooled.csv", index=False)

    best_window_row = pooled.sort_values(["mean_fwd_ret_bps_8", "n"], ascending=[False, False]).iloc[0]
    meta = {
        "sample": "BTC/ETH/SOL Binance Futures 120d 15m",
        "lookahead_bars": LOOKAHEAD_BARS,
        "estimator": "local DFA implementation (linear detrend on integrated demeaned price path)",
        "calibration_rule": "random-walk Monte Carlo; low=mu-0.5sigma, high=mu+0.5sigma",
        "windows_tested": list(WINDOWS),
        "mc_paths": MC_PATHS,
        "seed": MC_SEED,
        "decision": f"keep_P1; estimator-specific calibration is now local and auditable. Best cheap next step is reuse window {int(best_window_row['window'])} for one desk-family A/B/C gate, not threshold-tuning.",
        "best_proxy_bucket": {
            "window": int(best_window_row["window"]),
            "bucket": str(best_window_row["bucket"]),
            "mean_fwd_ret_bps_8": float(best_window_row["mean_fwd_ret_bps_8"]),
            "share": float(best_window_row["share"]),
        },
    }
    (OUT_DIR / "estimator_calibration_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("wrote:")
    for name in [
        "estimator_calibration_summary.csv",
        "bucket_diagnostics_by_asset.csv",
        "bucket_diagnostics_pooled.csv",
        "estimator_calibration_meta.json",
    ]:
        print(OUT_DIR / name)


if __name__ == "__main__":
    main()
