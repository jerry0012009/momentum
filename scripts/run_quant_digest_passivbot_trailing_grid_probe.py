#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import time

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "literature"
CACHE_DIR = ART_DIR / "passivbot_trailing_grid_probe_cache"
BINANCE_URL = "https://fapi.binance.com/fapi/v1/klines"
LIMIT = 1500
START_TS = pd.Timestamp("2025-10-01T00:00:00Z")
END_TS = pd.Timestamp.now(tz="UTC").floor("min")
ASSETS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT"]
TIMEFRAMES = {
    "5m": {"minutes": 5, "hold_bars": 6},
    "15m": {"minutes": 15, "hold_bars": 4},
}
MAKER_RT_BPS = 8.0
MIXED_RT_BPS = 18.0

# Canonical long config inspiration from passivbot v7.9 default example:
EMA_SPAN_0_MIN = 210
EMA_SPAN_1_MIN = 770
TP_PCT = 0.00634
VOL_EMA_MIN = 225
MIN_STRETCH_PCT = 0.004
VOL_STRETCH_MULT = 1.8
RETRACE_FRACTION = 0.55
COOLDOWN_BARS = 2


@dataclass
class ProbeResult:
    timeframe: str
    symbol: str
    timestamp: pd.Timestamp
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    entry_px: float
    exit_px: float
    gross_ret: float
    maker_net_ret: float
    mixed_net_ret: float
    tp_hit: bool
    stretch_pct: float
    stretch_threshold: float
    close_in_range: float
    ema_lower: float
    ema_upper: float
    hold_bars_used: int


def ensure_dirs() -> None:
    ART_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def fetch_klines(symbol: str, interval: str) -> pd.DataFrame:
    ensure_dirs()
    cache_path = CACHE_DIR / f"{symbol}_{interval}_{START_TS:%Y%m%d}_{END_TS:%Y%m%d}.csv"
    if cache_path.exists():
        df = pd.read_csv(cache_path)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        if not df.empty and df["timestamp"].max() >= END_TS - pd.Timedelta(hours=6):
            return df

    start_ms = int(START_TS.timestamp() * 1000)
    end_ms = int(END_TS.timestamp() * 1000)
    rows: list[list[object]] = []
    session = requests.Session()
    while start_ms < end_ms:
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_ms,
            "limit": LIMIT,
        }
        for attempt in range(8):
            resp = session.get(BINANCE_URL, params=params, timeout=30)
            if resp.status_code != 429:
                resp.raise_for_status()
                break
            wait_s = min(60, 3 * (attempt + 1))
            time.sleep(wait_s)
        else:
            resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        rows.extend(batch)
        last_open = int(batch[-1][0])
        start_ms = last_open + 1
        if len(batch) < LIMIT:
            break
        time.sleep(0.2)

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
            "quote_volume",
            "n_trades",
            "taker_base",
            "taker_quote",
            "ignore",
        ],
    )
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df = df[["timestamp", "open", "high", "low", "close", "volume"]].drop_duplicates("timestamp").sort_values("timestamp")
    df.to_csv(cache_path, index=False)
    return df


def compute_signal_frame(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    minutes = TIMEFRAMES[timeframe]["minutes"]
    out = df.copy().reset_index(drop=True)
    span0 = max(2, round(EMA_SPAN_0_MIN / minutes))
    span1 = max(3, round(EMA_SPAN_1_MIN / minutes))
    span_mid = max(2, round((EMA_SPAN_0_MIN * EMA_SPAN_1_MIN) ** 0.5 / minutes))
    vol_span = max(5, round(VOL_EMA_MIN / minutes))

    out["ema0"] = out["close"].ewm(span=span0, adjust=False).mean()
    out["ema1"] = out["close"].ewm(span=span1, adjust=False).mean()
    out["ema_mid"] = out["close"].ewm(span=span_mid, adjust=False).mean()
    out["ema_lower"] = out[["ema0", "ema1", "ema_mid"]].min(axis=1)
    out["ema_upper"] = out[["ema0", "ema1", "ema_mid"]].max(axis=1)
    out["norm_range"] = ((out["high"] - out["low"]) / out["close"]).ewm(span=vol_span, adjust=False).mean()
    out["stretch_pct"] = (out["ema_lower"] - out["low"]) / out["ema_lower"]
    out["stretch_threshold"] = np.maximum(MIN_STRETCH_PCT, VOL_STRETCH_MULT * out["norm_range"])
    rng = (out["high"] - out["low"]).replace(0, np.nan)
    out["close_in_range"] = (out["close"] - out["low"]) / rng
    out["signal"] = (
        (out["stretch_pct"] >= out["stretch_threshold"])
        & (out["close_in_range"] >= RETRACE_FRACTION)
        & (out["close"] < out["ema_lower"])
    )
    return out


def apply_cost(ret: float, rt_bps: float) -> float:
    c = rt_bps / 10000.0
    return (1.0 + ret) * (1.0 - c) - 1.0


def simulate_symbol(df: pd.DataFrame, timeframe: str, symbol: str) -> list[ProbeResult]:
    hold_bars = TIMEFRAMES[timeframe]["hold_bars"]
    work = compute_signal_frame(df, timeframe)
    results: list[ProbeResult] = []
    last_entry_idx = -999999
    for i in range(len(work) - hold_bars - 1):
        if not bool(work.loc[i, "signal"]):
            continue
        if i - last_entry_idx <= COOLDOWN_BARS:
            continue
        entry_idx = i + 1
        entry_px = float(work.loc[entry_idx, "open"])
        tp_px = entry_px * (1.0 + TP_PCT)
        exit_idx = entry_idx + hold_bars
        exit_px = float(work.loc[exit_idx, "close"])
        tp_hit = False
        for j in range(entry_idx, entry_idx + hold_bars + 1):
            if float(work.loc[j, "high"]) >= tp_px:
                exit_idx = j
                exit_px = tp_px
                tp_hit = True
                break
        gross = exit_px / entry_px - 1.0
        results.append(
            ProbeResult(
                timeframe=timeframe,
                symbol=symbol,
                timestamp=work.loc[i, "timestamp"],
                entry_time=work.loc[entry_idx, "timestamp"],
                exit_time=work.loc[exit_idx, "timestamp"],
                entry_px=entry_px,
                exit_px=exit_px,
                gross_ret=gross,
                maker_net_ret=apply_cost(gross, MAKER_RT_BPS),
                mixed_net_ret=apply_cost(gross, MIXED_RT_BPS),
                tp_hit=tp_hit,
                stretch_pct=float(work.loc[i, "stretch_pct"]),
                stretch_threshold=float(work.loc[i, "stretch_threshold"]),
                close_in_range=float(work.loc[i, "close_in_range"]),
                ema_lower=float(work.loc[i, "ema_lower"]),
                ema_upper=float(work.loc[i, "ema_upper"]),
                hold_bars_used=exit_idx - entry_idx,
            )
        )
        last_entry_idx = entry_idx
    return results


def summarize(detail: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for timeframe, g in detail.groupby("timeframe"):
        for label, ret_col in [("gross", "gross_ret"), ("maker_net", "maker_net_ret"), ("mixed_net", "mixed_net_ret")]:
            rets = g[ret_col].astype(float)
            eq = (1.0 + rets).cumprod()
            dd = eq / eq.cummax() - 1.0
            rows.append(
                {
                    "timeframe": timeframe,
                    "variant": label,
                    "trades": int(len(g)),
                    "win_rate": float((rets > 0).mean()) if len(rets) else np.nan,
                    "mean_bps": float(rets.mean() * 10000.0) if len(rets) else np.nan,
                    "median_bps": float(rets.median() * 10000.0) if len(rets) else np.nan,
                    "tp_hit_rate": float(g["tp_hit"].mean()) if len(g) else np.nan,
                    "cum_return_pct": float((eq.iloc[-1] - 1.0) * 100.0) if len(eq) else np.nan,
                    "max_drawdown_pct": float(dd.min() * 100.0) if len(dd) else np.nan,
                    "avg_stretch_pct": float(g["stretch_pct"].mean() * 100.0) if len(g) else np.nan,
                    "avg_threshold_pct": float(g["stretch_threshold"].mean() * 100.0) if len(g) else np.nan,
                    "avg_hold_bars": float(g["hold_bars_used"].mean()) if len(g) else np.nan,
                }
            )
    return pd.DataFrame(rows)


def summarize_by_asset(detail: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (timeframe, symbol), g in detail.groupby(["timeframe", "symbol"]):
        rets = g["maker_net_ret"].astype(float)
        rows.append(
            {
                "timeframe": timeframe,
                "symbol": symbol,
                "trades": int(len(g)),
                "win_rate": float((rets > 0).mean()) if len(rets) else np.nan,
                "maker_net_mean_bps": float(rets.mean() * 10000.0) if len(rets) else np.nan,
                "gross_mean_bps": float(g["gross_ret"].mean() * 10000.0) if len(g) else np.nan,
                "tp_hit_rate": float(g["tp_hit"].mean()) if len(g) else np.nan,
                "avg_stretch_pct": float(g["stretch_pct"].mean() * 100.0) if len(g) else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values(["timeframe", "maker_net_mean_bps"], ascending=[True, False])


def main() -> None:
    ensure_dirs()
    detail_rows: list[dict[str, object]] = []
    for timeframe in TIMEFRAMES:
        for symbol in ASSETS:
            df = fetch_klines(symbol, timeframe)
            results = simulate_symbol(df, timeframe, symbol)
            for item in results:
                detail_rows.append(item.__dict__)

    detail = pd.DataFrame(detail_rows).sort_values(["timeframe", "timestamp", "symbol"]).reset_index(drop=True)
    summary = summarize(detail)
    asset_summary = summarize_by_asset(detail)

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    detail_path = ART_DIR / f"passivbot_trailing_grid_probe_{stamp}_detail.csv"
    summary_path = ART_DIR / f"passivbot_trailing_grid_probe_{stamp}_summary.csv"
    asset_path = ART_DIR / f"passivbot_trailing_grid_probe_{stamp}_asset.csv"
    detail.to_csv(detail_path, index=False)
    summary.to_csv(summary_path, index=False)
    asset_summary.to_csv(asset_path, index=False)

    print(summary.to_string(index=False))
    print("\nasset breakdown:\n")
    print(asset_summary.to_string(index=False))
    print(f"\nWrote: {summary_path}\nWrote: {asset_path}\nWrote: {detail_path}")


if __name__ == "__main__":
    main()
