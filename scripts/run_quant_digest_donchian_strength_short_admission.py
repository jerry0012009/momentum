#!/usr/bin/env python3
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "reports" / "artifacts" / "quant_digests" / "2026-03-23_donchian_strength_short_admission"
BINANCE_FAPI_KLINES = "https://fapi.binance.com/fapi/v1/klines"


@dataclass
class Config:
    symbols: tuple[str, ...] = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
    interval: str = "15m"
    lookback_days: int = 120
    donchian_period: int = 20
    atr_period: int = 14
    horizon_bars: int = 8
    tp_atr: float = 1.5
    sl_atr: float = 1.0
    thresholds: tuple[float, ...] = (0.0, 0.2, 0.4, 0.6)
    request_limit: int = 1500
    sleep_sec: float = 0.08


def fetch_klines(symbol: str, interval: str, lookback_days: int, request_limit: int, sleep_sec: float) -> pd.DataFrame:
    end_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    start_ms = int((datetime.now(timezone.utc) - timedelta(days=lookback_days)).timestamp() * 1000)
    rows: list[list] = []
    cursor = start_ms

    while cursor < end_ms:
        resp = requests.get(
            BINANCE_FAPI_KLINES,
            params={
                "symbol": symbol,
                "interval": interval,
                "startTime": cursor,
                "endTime": end_ms,
                "limit": request_limit,
            },
            timeout=20,
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        rows.extend(batch)
        next_cursor = int(batch[-1][0]) + 1
        if next_cursor <= cursor:
            break
        cursor = next_cursor
        time.sleep(sleep_sec)

    cols = [
        "open_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "quote_volume",
        "trade_count",
        "taker_base_volume",
        "taker_quote_volume",
        "ignore",
    ]
    df = pd.DataFrame(rows, columns=cols)
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    return df.drop_duplicates("open_time").sort_values("open_time").reset_index(drop=True)


def add_features(df: pd.DataFrame, donchian_period: int, atr_period: int) -> pd.DataFrame:
    out = df.copy()
    prev_close = out["close"].shift(1)
    tr = pd.concat(
        [
            out["high"] - out["low"],
            (out["high"] - prev_close).abs(),
            (out["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    out["tr"] = tr
    out["atr"] = tr.ewm(alpha=1 / atr_period, adjust=False).mean()
    out["donchian_upper"] = out["high"].shift(1).rolling(donchian_period).max()
    out["donchian_lower"] = out["low"].shift(1).rolling(donchian_period).min()
    out["long_break"] = out["close"] > out["donchian_upper"]
    out["short_break"] = out["close"] < out["donchian_lower"]
    out["long_strength"] = (out["close"] - out["donchian_upper"]) / out["atr"]
    out["short_strength"] = (out["donchian_lower"] - out["close"]) / out["atr"]
    return out


def evaluate_side(
    df: pd.DataFrame,
    symbol: str,
    side: str,
    threshold: float,
    horizon_bars: int,
    tp_atr: float,
    sl_atr: float,
) -> pd.DataFrame:
    sign = 1 if side == "long" else -1
    sig_col = "long_break" if side == "long" else "short_break"
    strength_col = "long_strength" if side == "long" else "short_strength"
    mask = df[sig_col].fillna(False) & (df[strength_col].fillna(-999) > threshold)
    events: list[dict] = []

    for idx in np.flatnonzero(mask.to_numpy()):
        if idx + 1 >= len(df):
            continue
        atr = float(df.iloc[idx]["atr"])
        if not np.isfinite(atr) or atr <= 0:
            continue

        signal_row = df.iloc[idx]
        entry_row = df.iloc[idx + 1]
        entry_price = float(entry_row["open"])
        target_price = entry_price + sign * tp_atr * atr
        stop_price = entry_price - sign * sl_atr * atr
        verdict = "timeout"
        pnl_r = 0.0
        bars_held = 0

        for j in range(idx + 1, min(idx + 1 + horizon_bars, len(df))):
            bar = df.iloc[j]
            bars_held += 1
            if side == "long":
                hit_target = float(bar["high"]) >= target_price
                hit_stop = float(bar["low"]) <= stop_price
            else:
                hit_target = float(bar["low"]) <= target_price
                hit_stop = float(bar["high"]) >= stop_price

            if hit_target and hit_stop:
                verdict = "stop"
                pnl_r = -1.0
                break
            if hit_target:
                verdict = "target"
                pnl_r = tp_atr
                break
            if hit_stop:
                verdict = "stop"
                pnl_r = -1.0
                break

        events.append(
            {
                "symbol": symbol,
                "side": side,
                "threshold": threshold,
                "signal_time": signal_row["open_time"],
                "entry_time": entry_row["open_time"],
                "signal_close": float(signal_row["close"]),
                "strength": float(signal_row[strength_col]),
                "atr": atr,
                "entry_price": entry_price,
                "target_price": target_price,
                "stop_price": stop_price,
                "verdict": verdict,
                "pnl_r": pnl_r,
                "bars_held": bars_held,
            }
        )

    return pd.DataFrame(events)


def summarize_events(events: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        events.groupby(["symbol", "side", "threshold"], as_index=False)
        .agg(
            n=("verdict", "size"),
            target_rate=("verdict", lambda s: (s == "target").mean()),
            stop_rate=("verdict", lambda s: (s == "stop").mean()),
            timeout_rate=("verdict", lambda s: (s == "timeout").mean()),
            avg_pnl_r=("pnl_r", "mean"),
            median_bars=("bars_held", "median"),
            avg_strength=("strength", "mean"),
        )
    )
    return grouped.sort_values(["symbol", "side", "threshold"]).reset_index(drop=True)


def summarize_pooled(summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for (side, threshold), g in summary.groupby(["side", "threshold"]):
        weights = g["n"].to_numpy(dtype=float)
        rows.append(
            {
                "side": side,
                "threshold": threshold,
                "n": int(g["n"].sum()),
                "weighted_target_rate": float(np.average(g["target_rate"], weights=weights)),
                "weighted_stop_rate": float(np.average(g["stop_rate"], weights=weights)),
                "weighted_timeout_rate": float(np.average(g["timeout_rate"], weights=weights)),
                "weighted_avg_pnl_r": float(np.average(g["avg_pnl_r"], weights=weights)),
                "trade_retention_vs_base": float(g["n"].sum() / summary[(summary["side"] == side) & (summary["threshold"] == 0.0)]["n"].sum()),
            }
        )
    return pd.DataFrame(rows).sort_values(["side", "threshold"]).reset_index(drop=True)


def main() -> None:
    cfg = Config()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    all_events: list[pd.DataFrame] = []
    for symbol in cfg.symbols:
        df = fetch_klines(symbol, cfg.interval, cfg.lookback_days, cfg.request_limit, cfg.sleep_sec)
        df = add_features(df, cfg.donchian_period, cfg.atr_period)
        for side in ("long", "short"):
            for threshold in cfg.thresholds:
                events = evaluate_side(df, symbol, side, threshold, cfg.horizon_bars, cfg.tp_atr, cfg.sl_atr)
                if not events.empty:
                    all_events.append(events)

    events_df = pd.concat(all_events, ignore_index=True)
    summary_df = summarize_events(events_df)
    pooled_df = summarize_pooled(summary_df)

    events_df.to_csv(OUT_DIR / "events.csv", index=False)
    summary_df.to_csv(OUT_DIR / "summary_by_symbol_side_threshold.csv", index=False)
    pooled_df.to_csv(OUT_DIR / "summary_pooled.csv", index=False)

    meta = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "config": asdict(cfg),
        "source": "Binance USDⓈ-M Futures public klines",
        "notes": [
            "Signal on close, enter next-bar open.",
            "Donchian breakout uses previous N-bar high/low (shifted rolling window).",
            "Verdict uses first-hit within horizon bars: +1.5 ATR target / -1.0 ATR stop.",
            "If target and stop are both touched in the same bar, stop wins (conservative ordering).",
        ],
    }
    (OUT_DIR / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    print("[ok] wrote", OUT_DIR)
    print(summary_df.to_string(index=False))
    print("\n=== pooled ===")
    print(pooled_df.to_string(index=False))


if __name__ == "__main__":
    main()
