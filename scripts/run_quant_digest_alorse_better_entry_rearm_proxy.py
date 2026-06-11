#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import time
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "reports" / "artifacts" / "quant_digests" / "2026-03-23_alorse_better_entry_rearm"
BINANCE_FAPI_KLINES = "https://fapi.binance.com/fapi/v1/klines"
BINANCE_DOC_URL = "https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data"
REPO_URL = "https://github.com/Alorse/pinescript-strategies"
RAW_STRATEGY_URL = "https://raw.githubusercontent.com/Alorse/pinescript-strategies/master/strategies/trend/Supertrend%20%2B%20EMA%20rebound%20%5BAlorse%5D.pine"

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
INTERVAL = "15m"
LOOKBACK_DAYS = 120
REQUEST_LIMIT = 1500
REQUEST_SLEEP_SEC = 0.15
HOLD_BARS = 8
EMA_LEN = 20
ATR_LEN = 10
ST_FACTOR = 3.0
FEE_PER_SIDE = 0.0006


def fetch_klines(symbol: str, interval: str = INTERVAL, lookback_days: int = LOOKBACK_DAYS) -> pd.DataFrame:
    end_ms = int(time.time() * 1000)
    start_ms = end_ms - lookback_days * 24 * 60 * 60 * 1000
    rows: list[list] = []
    while True:
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_ms,
            "endTime": end_ms,
            "limit": REQUEST_LIMIT,
        }
        resp = requests.get(BINANCE_FAPI_KLINES, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        rows.extend(data)
        last_open_ms = int(data[-1][0])
        start_ms = last_open_ms + 1
        if len(data) < REQUEST_LIMIT:
            break
        time.sleep(REQUEST_SLEEP_SEC)
    if not rows:
        raise RuntimeError(f"no klines fetched for {symbol}")
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
            "trade_count",
            "taker_buy_base_volume",
            "taker_buy_quote_volume",
            "ignore",
        ],
    )
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)
    df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    return df[["timestamp", "open", "high", "low", "close", "volume"]].copy()


def calc_atr(df: pd.DataFrame, n: int = ATR_LEN) -> pd.Series:
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def calc_supertrend(df: pd.DataFrame, n: int = ATR_LEN, factor: float = ST_FACTOR) -> tuple[pd.Series, pd.Series]:
    hl2 = (df["high"] + df["low"]) / 2.0
    atr = calc_atr(df, n)
    upper = hl2 + factor * atr
    lower = hl2 - factor * atr
    final_upper = upper.copy()
    final_lower = lower.copy()
    st = pd.Series(index=df.index, dtype=float)
    direction = pd.Series(index=df.index, dtype=int)  # +1 long, -1 short

    for i in range(len(df)):
        if i == 0:
            final_upper.iat[i] = upper.iat[i]
            final_lower.iat[i] = lower.iat[i]
            st.iat[i] = upper.iat[i]
            direction.iat[i] = -1
            continue

        if upper.iat[i] < final_upper.iat[i - 1] or df["close"].iat[i - 1] > final_upper.iat[i - 1]:
            final_upper.iat[i] = upper.iat[i]
        else:
            final_upper.iat[i] = final_upper.iat[i - 1]

        if lower.iat[i] > final_lower.iat[i - 1] or df["close"].iat[i - 1] < final_lower.iat[i - 1]:
            final_lower.iat[i] = lower.iat[i]
        else:
            final_lower.iat[i] = final_lower.iat[i - 1]

        prev_st = st.iat[i - 1]
        if prev_st == final_upper.iat[i - 1]:
            if df["close"].iat[i] <= final_upper.iat[i]:
                st.iat[i] = final_upper.iat[i]
                direction.iat[i] = -1
            else:
                st.iat[i] = final_lower.iat[i]
                direction.iat[i] = 1
        else:
            if df["close"].iat[i] >= final_lower.iat[i]:
                st.iat[i] = final_lower.iat[i]
                direction.iat[i] = 1
            else:
                st.iat[i] = final_upper.iat[i]
                direction.iat[i] = -1

    return st, direction


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ema20"] = out["close"].ewm(span=EMA_LEN, adjust=False).mean()
    out["supertrend"], out["direction"] = calc_supertrend(out)
    out["flip_long"] = (out["direction"] == 1) & (out["direction"].shift(1) == -1)
    out["flip_short"] = (out["direction"] == -1) & (out["direction"].shift(1) == 1)

    long_last_entry = math.nan
    short_last_entry = math.nan
    rebound_any_long: list[bool] = []
    rebound_better_long: list[bool] = []
    rebound_any_short: list[bool] = []
    rebound_better_short: list[bool] = []

    for i, row in out.iterrows():
        if i == 0:
            rebound_any_long.append(False)
            rebound_better_long.append(False)
            rebound_any_short.append(False)
            rebound_better_short.append(False)
            continue

        if bool(row["flip_long"]):
            long_last_entry = float(row["close"])
        if bool(row["flip_short"]):
            short_last_entry = float(row["close"])

        long_any = (
            row["direction"] == 1
            and out["close"].iat[i - 1] < out["ema20"].iat[i - 1]
            and row["close"] > row["ema20"]
        )
        short_any = (
            row["direction"] == -1
            and out["close"].iat[i - 1] > out["ema20"].iat[i - 1]
            and row["close"] < row["ema20"]
        )
        long_better = long_any and (not math.isnan(long_last_entry)) and float(row["close"]) < long_last_entry
        short_better = short_any and (not math.isnan(short_last_entry)) and float(row["close"]) > short_last_entry

        rebound_any_long.append(bool(long_any))
        rebound_better_long.append(bool(long_better))
        rebound_any_short.append(bool(short_any))
        rebound_better_short.append(bool(short_better))

        if long_any:
            long_last_entry = float(row["close"])
        if short_any:
            short_last_entry = float(row["close"])

    out["rebound_any_long"] = rebound_any_long
    out["rebound_better_long"] = rebound_better_long
    out["rebound_any_short"] = rebound_any_short
    out["rebound_better_short"] = rebound_better_short
    return out


def iter_events(df: pd.DataFrame, signal_col: str, side: str) -> Iterable[dict]:
    next_ok = 0
    warmup = max(EMA_LEN + 5, ATR_LEN + 5)
    for i, is_signal in enumerate(df[signal_col].fillna(False).tolist()):
        if not is_signal:
            continue
        if i < warmup or i + HOLD_BARS + 1 >= len(df):
            continue
        if i < next_ok:
            continue
        entry_idx = i + 1
        exit_idx = i + HOLD_BARS
        entry_px = float(df["open"].iat[entry_idx])
        exit_px = float(df["close"].iat[exit_idx])
        gross = (exit_px / entry_px - 1.0) if side == "long" else (entry_px / exit_px - 1.0)
        net = gross - 2 * FEE_PER_SIDE
        yield {
            "timestamp": df["timestamp"].iat[i].isoformat(),
            "side": side,
            "signal_idx": int(i),
            "entry_idx": int(entry_idx),
            "exit_idx": int(exit_idx),
            "entry_price": entry_px,
            "exit_price": exit_px,
            "gross_return": gross,
            "net_return": net,
        }
        next_ok = i + HOLD_BARS


def summarize(events: pd.DataFrame) -> pd.DataFrame:
    if events.empty:
        return pd.DataFrame(columns=["symbol", "arm", "side", "trades", "mean_net_return", "positive_ratio"])
    out = (
        events.groupby(["symbol", "arm", "side"], dropna=False)
        .agg(
            trades=("net_return", "size"),
            mean_net_return=("net_return", "mean"),
            positive_ratio=("net_return", lambda s: float((s > 0).mean())),
        )
        .reset_index()
        .sort_values(["symbol", "arm"])
    )
    return out


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    arm_side = {
        "flip_long": "long",
        "rebound_any_long": "long",
        "rebound_better_long": "long",
        "flip_short": "short",
        "rebound_any_short": "short",
        "rebound_better_short": "short",
    }

    event_rows: list[dict] = []
    for symbol in SYMBOLS:
        df = add_signals(fetch_klines(symbol))
        for arm, side in arm_side.items():
            for row in iter_events(df, arm, side):
                row["symbol"] = symbol
                row["arm"] = arm
                event_rows.append(row)

    events = pd.DataFrame(event_rows)
    events.to_csv(OUT_DIR / "events.csv", index=False)

    by_symbol = summarize(events)
    by_symbol.to_csv(OUT_DIR / "summary_by_symbol_arm.csv", index=False)

    equal_weight = (
        by_symbol.groupby(["arm", "side"], dropna=False)
        .agg(
            mean_trades=("trades", "mean"),
            mean_net_return=("mean_net_return", "mean"),
            mean_positive_ratio=("positive_ratio", "mean"),
        )
        .reset_index()
        .sort_values(["side", "arm"])
    )

    any_lookup = {
        (row.side, row.arm): row.mean_trades
        for row in equal_weight.itertuples()
    }
    retentions = []
    for row in equal_weight.itertuples(index=False):
        baseline_arm = f"rebound_any_{row.side}"
        baseline_trades = any_lookup.get((row.side, baseline_arm))
        retention = np.nan
        if row.arm.startswith("rebound_better_") and baseline_trades:
            retention = float(row.mean_trades / baseline_trades)
        retentions.append(retention)
    equal_weight["trade_retention_vs_any"] = retentions
    equal_weight.to_csv(OUT_DIR / "summary_equal_weight.csv", index=False)

    pooled = (
        events.groupby(["arm", "side"], dropna=False)
        .agg(
            trades=("net_return", "size"),
            mean_net_return=("net_return", "mean"),
            positive_ratio=("net_return", lambda s: float((s > 0).mean())),
        )
        .reset_index()
        .sort_values(["side", "arm"])
    )
    pooled.to_csv(OUT_DIR / "summary_pooled.csv", index=False)

    meta = {
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "source": {
            "repo_url": REPO_URL,
            "raw_strategy_url": RAW_STRATEGY_URL,
            "market_data_url": BINANCE_DOC_URL,
        },
        "universe": SYMBOLS,
        "interval": INTERVAL,
        "lookback_days": LOOKBACK_DAYS,
        "hold_bars": HOLD_BARS,
        "fee_per_side": FEE_PER_SIDE,
        "ema_len": EMA_LEN,
        "atr_len": ATR_LEN,
        "supertrend_factor": ST_FACTOR,
    }
    (OUT_DIR / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    print("wrote:")
    for name in ["events.csv", "summary_by_symbol_arm.csv", "summary_equal_weight.csv", "summary_pooled.csv", "meta.json"]:
        print(OUT_DIR / name)
    print("\nEqual-weight summary:")
    print(equal_weight.to_string(index=False, float_format=lambda x: f"{x:.4%}" if abs(x) < 1 else f"{x:.1f}"))


if __name__ == "__main__":
    main()
