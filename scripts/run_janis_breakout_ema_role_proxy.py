#!/usr/bin/env python3
"""
Minimal proxy check for Janis174756/Binance-Futures-Trading-Bot breakout logic.

- Data: Binance public klines (spot), 15m
- Symbols: BTCUSDT, ETHUSDT, SOLUSDT
- Sample: recent 120 days
- Compare:
  A) raw breakout (20-bar recent high/low, fixed ±2% SL/TP)
  B) breakout + EMA stack gate (9/21/50)
  C) breakout + EMA stack + RSI clamp (long<70, short>30)
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import pandas as pd
import requests


SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
INTERVAL = "15m"
DAYS = 120
LOOKAHEAD_BARS = 24  # 6h on 15m
OUTDIR = Path("reports/artifacts/quant_digests/2026-03-22_janis_breakout_ema_role")


@dataclass
class VariantConfig:
    name: str
    use_ema_gate: bool = False
    use_rsi_clamp: bool = False


VARIANTS = [
    VariantConfig("raw", use_ema_gate=False, use_rsi_clamp=False),
    VariantConfig("ema", use_ema_gate=True, use_rsi_clamp=False),
    VariantConfig("ema_rsi", use_ema_gate=True, use_rsi_clamp=True),
]


def fetch_klines(symbol: str, days: int = DAYS) -> pd.DataFrame:
    total_bars = int(days * 24 * 60 / 15)
    rows: List[List] = []
    end_time = None

    while len(rows) < total_bars + 300:
        params = {"symbol": symbol, "interval": INTERVAL, "limit": 1000}
        if end_time is not None:
            params["endTime"] = end_time

        resp = requests.get("https://api.binance.com/api/v3/klines", params=params, timeout=20)
        resp.raise_for_status()
        chunk = resp.json()
        if not chunk:
            break

        rows = chunk + rows
        end_time = chunk[0][0] - 1

        if len(chunk) < 1000:
            break

    rows = rows[-(total_bars + 300) :]
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
            "qv",
            "trades",
            "tb",
            "tq",
            "ignore",
        ],
    )
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    return df


def apply_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ema9"] = out["close"].ewm(span=9, adjust=False).mean()
    out["ema21"] = out["close"].ewm(span=21, adjust=False).mean()
    out["ema50"] = out["close"].ewm(span=50, adjust=False).mean()

    delta = out["close"].diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    rs = up.ewm(alpha=1 / 14, adjust=False).mean() / (down.ewm(alpha=1 / 14, adjust=False).mean() + 1e-12)
    out["rsi14"] = 100 - 100 / (1 + rs)

    out["recent_high_20"] = out["high"].rolling(20).max().shift(1)
    out["recent_low_20"] = out["low"].rolling(20).min().shift(1)
    return out


def evaluate_variant(df: pd.DataFrame, variant: VariantConfig, symbol: str) -> pd.DataFrame:
    rows: List[Dict] = []
    d = df.reset_index(drop=True)

    for i in range(60, len(d) - LOOKAHEAD_BARS):
        c = float(d.at[i, "close"])
        long_sig = c > float(d.at[i, "recent_high_20"])
        short_sig = c < float(d.at[i, "recent_low_20"])
        if not (long_sig or short_sig):
            continue

        for side, hit in (("long", long_sig), ("short", short_sig)):
            if not hit:
                continue

            if variant.use_ema_gate:
                if side == "long" and not (d.at[i, "ema9"] > d.at[i, "ema21"] > d.at[i, "ema50"]):
                    continue
                if side == "short" and not (d.at[i, "ema9"] < d.at[i, "ema21"] < d.at[i, "ema50"]):
                    continue

            if variant.use_rsi_clamp:
                if side == "long" and not (d.at[i, "rsi14"] < 70):
                    continue
                if side == "short" and not (d.at[i, "rsi14"] > 30):
                    continue

            entry = c
            if side == "long":
                sl = entry * 0.98
                tp = entry * 1.02
            else:
                sl = entry * 1.02
                tp = entry * 0.98

            outcome = "timeout"
            decision_bars = LOOKAHEAD_BARS
            for j in range(1, LOOKAHEAD_BARS + 1):
                hi = float(d.at[i + j, "high"])
                lo = float(d.at[i + j, "low"])
                if side == "long":
                    tp_hit = hi >= tp
                    sl_hit = lo <= sl
                else:
                    tp_hit = lo <= tp
                    sl_hit = hi >= sl

                # conservative: ambiguous same-bar first hit -> fail
                if tp_hit and sl_hit:
                    outcome = "fail"
                    decision_bars = j
                    break
                if tp_hit:
                    outcome = "continue"
                    decision_bars = j
                    break
                if sl_hit:
                    outcome = "fail"
                    decision_bars = j
                    break

            rows.append(
                {
                    "symbol": symbol,
                    "variant": variant.name,
                    "side": side,
                    "entry_time": d.at[i, "open_time"],
                    "outcome": outcome,
                    "decision_bars": decision_bars,
                    "score_r": 1 if outcome == "continue" else (-1 if outcome == "fail" else 0),
                }
            )

    return pd.DataFrame(rows)


def summarize(events: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    grouped = events.groupby("variant", as_index=False).agg(
        n=("outcome", "size"),
        continue_rate=("outcome", lambda x: (x == "continue").mean()),
        fail_rate=("outcome", lambda x: (x == "fail").mean()),
        timeout_rate=("outcome", lambda x: (x == "timeout").mean()),
        mean_decision_bars=("decision_bars", "mean"),
        exp_r=("score_r", "mean"),
    )
    grouped["trades_per_day_per_symbol"] = grouped["n"] / (DAYS * len(SYMBOLS))

    grouped_side = events.groupby(["variant", "side"], as_index=False).agg(
        n=("outcome", "size"),
        continue_rate=("outcome", lambda x: (x == "continue").mean()),
        fail_rate=("outcome", lambda x: (x == "fail").mean()),
        timeout_rate=("outcome", lambda x: (x == "timeout").mean()),
        mean_decision_bars=("decision_bars", "mean"),
        exp_r=("score_r", "mean"),
    )

    return {"by_variant": grouped, "by_variant_side": grouped_side}


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)

    all_events = []
    for symbol in SYMBOLS:
        df = fetch_klines(symbol)
        df = apply_indicators(df)
        for variant in VARIANTS:
            events = evaluate_variant(df, variant, symbol=symbol)
            all_events.append(events)

    events = pd.concat(all_events, ignore_index=True)
    summaries = summarize(events)

    events.to_csv(OUTDIR / "events.csv", index=False)
    summaries["by_variant"].to_csv(OUTDIR / "summary_by_variant.csv", index=False)
    summaries["by_variant_side"].to_csv(OUTDIR / "summary_by_variant_side.csv", index=False)

    payload = {
        "symbols": SYMBOLS,
        "interval": INTERVAL,
        "days": DAYS,
        "lookahead_bars": LOOKAHEAD_BARS,
        "n_events": int(len(events)),
        "by_variant": summaries["by_variant"].to_dict(orient="records"),
        "by_variant_side": summaries["by_variant_side"].to_dict(orient="records"),
    }
    (OUTDIR / "summary.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote: {OUTDIR}")


if __name__ == "__main__":
    main()
