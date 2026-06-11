#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import requests

BINANCE_URL = "https://fapi.binance.com/fapi/v1/klines"
ASSETS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
INTERVAL = "15m"
DAYS = 120
LIMIT = 1500
LOOKAHEAD_BARS = 8
LOOKBACK_BARS = 8
TARGET_ATR = 1.5
STOP_ATR = 1.0
OUTDIR = Path("/root/clawd/jerry/momentum/reports/artifacts/quant_digest_caizongxun_pattern_retest_proxy")


def fetch_klines(symbol: str, days: int = DAYS) -> pd.DataFrame:
    end_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    start_ms = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp() * 1000)
    rows: List[list] = []
    cursor = start_ms
    session = requests.Session()
    while cursor < end_ms:
        params = {
            "symbol": symbol,
            "interval": INTERVAL,
            "startTime": cursor,
            "endTime": end_ms,
            "limit": LIMIT,
        }
        resp = session.get(BINANCE_URL, params=params, timeout=30)
        resp.raise_for_status()
        chunk = resp.json()
        if not chunk:
            break
        rows.extend(chunk)
        last_open = int(chunk[-1][0])
        next_cursor = last_open + 15 * 60 * 1000
        if next_cursor <= cursor:
            break
        cursor = next_cursor
        if len(chunk) < LIMIT:
            break
        time.sleep(0.15)
    if not rows:
        raise RuntimeError(f"no rows for {symbol}")
    cols = [
        "open_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "quote_asset_volume",
        "number_of_trades",
        "taker_buy_base",
        "taker_buy_quote",
        "ignore",
    ]
    df = pd.DataFrame(rows, columns=cols)
    df = df.drop_duplicates(subset=["open_time"]).sort_values("open_time").reset_index(drop=True)
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)
    df["ts"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    return df


def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["sma5"] = out["close"].rolling(5).mean()
    out["sma20"] = out["close"].rolling(20).mean()
    out["sma60"] = out["close"].rolling(60).mean()

    ema12 = ema(out["close"], 12)
    ema26 = ema(out["close"], 26)
    out["macd"] = ema12 - ema26
    out["macd_signal"] = ema(out["macd"], 9)
    out["macd_hist"] = out["macd"] - out["macd_signal"]

    delta = out["close"].diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1 / 14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / 14, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    out["rsi"] = 100 - (100 / (1 + rs))

    prev_close = out["close"].shift(1)
    tr = pd.concat(
        [
            out["high"] - out["low"],
            (out["high"] - prev_close).abs(),
            (out["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    out["atr"] = tr.ewm(alpha=1 / 14, adjust=False).mean()
    return out


def bullish_hammer(row: pd.Series) -> bool:
    rng = row.high - row.low
    if rng <= 0:
        return False
    upper = row.high - max(row.open, row.close)
    lower = min(row.open, row.close) - row.low
    body = abs(row.close - row.open)
    return lower >= 0.6 * rng and upper <= 0.1 * rng and body <= 0.45 * rng and row.close >= row.open


def bearish_inverted_hammer(row: pd.Series) -> bool:
    rng = row.high - row.low
    if rng <= 0:
        return False
    upper = row.high - max(row.open, row.close)
    lower = min(row.open, row.close) - row.low
    body = abs(row.close - row.open)
    return upper >= 0.6 * rng and lower <= 0.1 * rng and body <= 0.45 * rng and row.close <= row.open


def bullish_engulf(curr: pd.Series, prev: pd.Series) -> bool:
    return (
        prev.close < prev.open
        and curr.close > curr.open
        and curr.open <= prev.close
        and curr.close >= prev.open
    )


def bearish_engulf(curr: pd.Series, prev: pd.Series) -> bool:
    return (
        prev.close > prev.open
        and curr.close < curr.open
        and curr.open >= prev.close
        and curr.close <= prev.open
    )


def eval_event(df: pd.DataFrame, i: int, side: str) -> Dict[str, float] | None:
    if i + 1 >= len(df) or i + 1 + LOOKAHEAD_BARS >= len(df):
        return None
    entry = float(df.iloc[i + 1].open)
    atr = float(df.iloc[i].atr)
    if not math.isfinite(atr) or atr <= 0:
        return None
    if side == "long":
        target = entry + TARGET_ATR * atr
        stop = entry - STOP_ATR * atr
    else:
        target = entry - TARGET_ATR * atr
        stop = entry + STOP_ATR * atr

    horizon = df.iloc[i + 1 : i + 1 + LOOKAHEAD_BARS + 1]
    outcome = "timeout"
    exit_px = float(horizon.iloc[-1].close)
    hit_bar = None
    for j, row in horizon.iterrows():
        if side == "long":
            hit_target = row.high >= target
            hit_stop = row.low <= stop
        else:
            hit_target = row.low <= target
            hit_stop = row.high >= stop
        if hit_target and hit_stop:
            outcome = "stop_first_ambiguous"
            exit_px = stop
            hit_bar = int(j)
            break
        if hit_stop:
            outcome = "stop"
            exit_px = stop
            hit_bar = int(j)
            break
        if hit_target:
            outcome = "target"
            exit_px = target
            hit_bar = int(j)
            break
    if side == "long":
        fwd_atr = (exit_px - entry) / atr
        pnl_r = TARGET_ATR if outcome == "target" else (-STOP_ATR if outcome.startswith("stop") else fwd_atr)
    else:
        fwd_atr = (entry - exit_px) / atr
        pnl_r = TARGET_ATR if outcome == "target" else (-STOP_ATR if outcome.startswith("stop") else fwd_atr)
    return {
        "entry": entry,
        "atr": atr,
        "outcome": outcome,
        "fwd_atr": fwd_atr,
        "pnl_r": pnl_r,
        "hit_bar": hit_bar if hit_bar is not None else i + 1 + LOOKAHEAD_BARS,
    }


def run_symbol(symbol: str) -> Tuple[pd.DataFrame, List[Dict[str, object]]]:
    df = compute_indicators(fetch_klines(symbol))
    events: List[Dict[str, object]] = []
    next_ok = {"long_base": 0, "long_pattern": 0, "short_base": 0, "short_pattern": 0}
    for i in range(max(60, LOOKBACK_BARS + 2), len(df) - LOOKAHEAD_BARS - 2):
        row = df.iloc[i]
        prev = df.iloc[i - 1]
        vals = [float(row.sma5), float(row.sma20), float(row.sma60), float(row.atr)]
        if any(not math.isfinite(v) for v in vals):
            continue
        uptrend = row.sma5 > row.sma20 > row.sma60
        downtrend = row.sma5 < row.sma20 < row.sma60
        prior_excursion_long = df.iloc[i - LOOKBACK_BARS : i]["close"].max() >= row.sma20 + row.atr
        prior_excursion_short = df.iloc[i - LOOKBACK_BARS : i]["close"].min() <= row.sma20 - row.atr
        long_base = (
            uptrend
            and prior_excursion_long
            and row.low <= row.sma20 <= row.close
            and row.close >= row.open
        )
        short_base = (
            downtrend
            and prior_excursion_short
            and row.high >= row.sma20 >= row.close
            and row.close <= row.open
        )
        long_hammer = bullish_hammer(row)
        long_engulf = bullish_engulf(row, prev)
        short_hammer = bearish_inverted_hammer(row)
        short_engulf = bearish_engulf(row, prev)
        long_pattern = long_base and (long_hammer or long_engulf)
        short_pattern = short_base and (short_hammer or short_engulf)

        pattern_kind = {
            ("long", "base"): "none",
            ("long", "pattern"): "hammer+engulf" if long_hammer and long_engulf else ("hammer" if long_hammer else ("engulf" if long_engulf else "none")),
            ("short", "base"): "none",
            ("short", "pattern"): "hammer+engulf" if short_hammer and short_engulf else ("hammer" if short_hammer else ("engulf" if short_engulf else "none")),
        }
        candidates = [
            ("long", "base", long_base),
            ("long", "pattern", long_pattern),
            ("short", "base", short_base),
            ("short", "pattern", short_pattern),
        ]
        for side, variant, cond in candidates:
            key = f"{side}_{variant}"
            if not cond or i < next_ok[key]:
                continue
            result = eval_event(df, i, side)
            if result is None:
                continue
            next_ok[key] = int(result["hit_bar"])
            events.append(
                {
                    "symbol": symbol,
                    "ts": row.ts.isoformat(),
                    "side": side,
                    "variant": variant,
                    "pattern_kind": pattern_kind[(side, variant)],
                    "signal_close": float(row.close),
                    "sma20": float(row.sma20),
                    "atr": float(row.atr),
                    "volume": float(row.volume),
                    **result,
                }
            )
    return df, events


def summarize(events: pd.DataFrame) -> pd.DataFrame:
    if events.empty:
        return pd.DataFrame()
    out = []
    for (side, variant), g in events.groupby(["side", "variant"]):
        trades = len(g)
        target_rate = (g["outcome"] == "target").mean()
        stop_rate = g["outcome"].astype(str).str.startswith("stop").mean()
        timeout_rate = (g["outcome"] == "timeout").mean()
        out.append(
            {
                "side": side,
                "variant": variant,
                "trades": trades,
                "target_rate": target_rate,
                "stop_rate": stop_rate,
                "timeout_rate": timeout_rate,
                "avg_fwd_atr": g["fwd_atr"].mean(),
                "median_fwd_atr": g["fwd_atr"].median(),
                "avg_pnl_r": g["pnl_r"].mean(),
            }
        )
    return pd.DataFrame(out).sort_values(["side", "variant"])


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    all_events: List[Dict[str, object]] = []
    source_rows = []
    for symbol in ASSETS:
        df, events = run_symbol(symbol)
        all_events.extend(events)
        source_rows.append({"symbol": symbol, "bars": int(len(df)), "start": df.iloc[0].ts.isoformat(), "end": df.iloc[-1].ts.isoformat()})
    events_df = pd.DataFrame(all_events)
    summary_df = summarize(events_df)
    events_path = OUTDIR / "event_log.csv"
    summary_path = OUTDIR / "summary.csv"
    meta_path = OUTDIR / "meta.json"
    if not events_df.empty:
        events_df.to_csv(events_path, index=False)
    summary_df.to_csv(summary_path, index=False)
    meta = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "sample": f"Binance Futures {DAYS}d {INTERVAL} | BTC/ETH/SOL",
        "lookback_bars": LOOKBACK_BARS,
        "lookahead_bars": LOOKAHEAD_BARS,
        "entry": "next-bar open after signal close",
        "barrier": {"target_atr": TARGET_ATR, "stop_atr": STOP_ATR},
        "variants": ["base mid-MA retest", "pattern gate = hammer OR engulfing on signal bar"],
        "sources": source_rows,
    }
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    print(summary_df.to_string(index=False))
    print(f"\nWrote: {summary_path}")


if __name__ == "__main__":
    main()
