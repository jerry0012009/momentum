#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "rank32b_unclosed15m_preview_backtest"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "rank32b_unclosed15m_preview_backtest"
CACHE_DIR = ART_DIR / "cache_1m"

SLOPE_FLOOR = 0.0004
EMA_FAST_1H = 20
EMA_SLOW_1H = 50
ATR_PERIOD = 14
TP_ATR_MULT = 1.25
SL_ATR_MULT = 1.00
TIMEOUT_MINUTES = 120
FALLBACK_TP_BPS = 40.0
FALLBACK_SL_BPS = 40.0
MARKET_COSTS_BPS = [6.0, 10.0, 15.0, 20.0]
MAKER_TP_COST_BPS = 0.0
DEFAULT_DAYS = 90
MAX_RETRIES = 8
BASE_SLEEP = 0.05

CANARY_CORE18 = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
    "LTC-USD": "LTCUSDT",
    "NEAR-USD": "NEARUSDT",
    "UNI-USD": "UNIUSDT",
    "XRP-USD": "XRPUSDT",
    "DOGE-USD": "DOGEUSDT",
    "BNB-USD": "BNBUSDT",
    "ADA-USD": "ADAUSDT",
    "AVAX-USD": "AVAXUSDT",
    "LINK-USD": "LINKUSDT",
    "BCH-USD": "BCHUSDT",
    "DOT-USD": "DOTUSDT",
    "ZEC-USD": "ZECUSDT",
    "AAVE-USD": "AAVEUSDT",
    "SUI-USD": "SUIUSDT",
    "WLD-USD": "WLDUSDT",
}

CANARY_ALL26 = {
    **CANARY_CORE18,
    "BEAT-USD": "BEATUSDT",
    "TRADOOR-USD": "TRADOORUSDT",
    "PIPPIN-USD": "PIPPINUSDT",
    "ACT-USD": "ACTUSDT",
    "BRETT-USD": "BRETTUSDT",
    "TURBO-USD": "TURBOUSDT",
    "FARTCOIN-USD": "FARTCOINUSDT",
    "1000PEPE-USD": "1000PEPEUSDT",
}

UNIVERSE_PRESETS: dict[str, dict[str, str]] = {
    "canary_core18": CANARY_CORE18,
    "canary_all26": CANARY_ALL26,
    "core5": {k: CANARY_CORE18[k] for k in ["BTC-USD", "ETH-USD", "SOL-USD", "DOGE-USD", "NEAR-USD"]},
}


@dataclass(slots=True)
class ExitResult:
    exit_ts: pd.Timestamp
    exit_price: float
    exit_reason: str
    gross_ret: float
    net_ret: float
    exit_fee_bps: float
    hold_minutes: int
    tp_hit: int
    sl_hit: int
    timeout_hit: int
    same_bar_conflict: int


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def pct(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def num(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}"


def render_table(df: pd.DataFrame, percent_cols: set[str] | None = None, digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return "<p class='muted'>暂无数据。</p>"
    percent_cols = percent_cols or set()
    digits_cols = digits_cols or {}
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows: list[str] = []
    for _, row in df.iterrows():
        cells: list[str] = []
        for col in df.columns:
            value = row[col]
            if col in percent_cols:
                text = pct(value)
            elif isinstance(value, (float, np.floating, int, np.integer)) and not isinstance(value, bool):
                text = num(value, digits_cols.get(col, 2))
            else:
                text = str(value)
            cells.append(f"<td>{escape(text)}</td>")
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def parse_csv_floats(text: str) -> list[float]:
    return [float(x.strip()) for x in text.split(",") if x.strip()]


def parse_symbols(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in text.split(","):
        sym = raw.strip().upper()
        if not sym:
            continue
        asset = sym.replace("USDT", "-USD")
        out[asset] = sym
    return out


def fetch_futures_1m(symbol: str, days: int) -> pd.DataFrame:
    end_ms = int(time.time() * 1000)
    start_ms = end_ms - days * 24 * 60 * 60 * 1000
    rows: list[list] = []
    current = start_ms
    limit = 1500
    cols = [
        "open_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "quote_asset_volume",
        "num_trades",
        "taker_buy_base",
        "taker_buy_quote",
        "ignore",
    ]

    while current < end_ms:
        params = {
            "symbol": symbol,
            "interval": "1m",
            "startTime": current,
            "endTime": end_ms,
            "limit": limit,
        }
        retry = 0
        while True:
            resp = requests.get("https://fapi.binance.com/fapi/v1/klines", params=params, timeout=30)
            if resp.status_code == 429:
                retry_after = resp.headers.get("Retry-After")
                wait_s = float(retry_after) if retry_after else min(30.0, (2**retry) * 0.6)
                time.sleep(wait_s)
                retry += 1
                if retry > MAX_RETRIES:
                    resp.raise_for_status()
                continue
            if resp.status_code >= 500:
                time.sleep(min(20.0, (2**retry) * 0.5))
                retry += 1
                if retry > MAX_RETRIES:
                    resp.raise_for_status()
                continue
            resp.raise_for_status()
            data = resp.json()
            break
        if not data:
            break
        rows.extend(data)
        current = int(data[-1][0]) + 60_000
        if len(data) < limit:
            break
        time.sleep(BASE_SLEEP)

    if not rows:
        return pd.DataFrame(columns=["open_ts", "close_ts", "open", "high", "low", "close", "volume"])

    df = pd.DataFrame(rows, columns=cols)
    out = pd.DataFrame(
        {
            "open_ts": pd.to_datetime(df["open_time"], unit="ms", utc=True),
            "open": pd.to_numeric(df["open"], errors="coerce"),
            "high": pd.to_numeric(df["high"], errors="coerce"),
            "low": pd.to_numeric(df["low"], errors="coerce"),
            "close": pd.to_numeric(df["close"], errors="coerce"),
            "volume": pd.to_numeric(df["volume"], errors="coerce"),
        }
    )
    out["close_ts"] = out["open_ts"] + pd.Timedelta(minutes=1)
    return out.dropna().sort_values("open_ts").drop_duplicates("open_ts").reset_index(drop=True)


def load_or_fetch_1m(symbol: str, days: int, refresh: bool = False) -> pd.DataFrame:
    ensure_dir(CACHE_DIR)
    path = CACHE_DIR / f"{symbol}__{days}d__1m__perp.csv"
    if path.exists() and not refresh:
        df = pd.read_csv(path)
        df["open_ts"] = pd.to_datetime(df["open_ts"], utc=True)
        df["close_ts"] = pd.to_datetime(df["close_ts"], utc=True)
        return df.sort_values("open_ts").reset_index(drop=True)
    df = fetch_futures_1m(symbol, days=days)
    df.to_csv(path, index=False)
    return df


def ema_update(prev_ema: float, value: float, span: int) -> float:
    alpha = 2.0 / (span + 1.0)
    return alpha * value + (1.0 - alpha) * prev_ema


def build_completed_hours(minute_df: pd.DataFrame) -> pd.DataFrame:
    work = minute_df.copy()
    work["hour_start"] = work["open_ts"].dt.floor("1h")
    hours = (
        work.groupby("hour_start", sort=True)
        .agg(hour_close=("close", "last"))
        .reset_index()
        .sort_values("hour_start")
        .reset_index(drop=True)
    )
    fast_vals: list[float] = []
    slow_vals: list[float] = []
    prev_fast = math.nan
    prev_slow = math.nan
    for close in hours["hour_close"].astype(float):
        if not math.isfinite(prev_fast):
            prev_fast = close
            prev_slow = close
        else:
            prev_fast = ema_update(prev_fast, close, EMA_FAST_1H)
            prev_slow = ema_update(prev_slow, close, EMA_SLOW_1H)
        fast_vals.append(prev_fast)
        slow_vals.append(prev_slow)
    hours["ema_fast_hour"] = fast_vals
    hours["ema_slow_hour"] = slow_vals
    return hours


def build_completed_15m(minute_df: pd.DataFrame, hour_df: pd.DataFrame) -> pd.DataFrame:
    work = minute_df.copy()
    work["bucket_start"] = work["open_ts"].dt.floor("15min")
    bars = (
        work.groupby("bucket_start", sort=True)
        .agg(open=("open", "first"), high=("high", "max"), low=("low", "min"), close=("close", "last"), volume=("volume", "sum"))
        .reset_index()
        .rename(columns={"bucket_start": "timestamp"})
    )
    bars["signal_confirmed_at"] = bars["timestamp"] + pd.Timedelta(minutes=15)
    bars["hour_start"] = bars["signal_confirmed_at"].dt.floor("1h")
    hour_map = hour_df[["hour_start", "ema_fast_hour", "ema_slow_hour"]].copy()
    hour_map["prev_hour_start"] = hour_map["hour_start"] + pd.Timedelta(hours=1)
    hour_map = hour_map[["prev_hour_start", "ema_fast_hour", "ema_slow_hour"]].rename(
        columns={"prev_hour_start": "hour_start", "ema_fast_hour": "prev_hour_fast", "ema_slow_hour": "prev_hour_slow"}
    )
    bars = bars.merge(hour_map, on="hour_start", how="left")

    alpha_fast = 2.0 / (EMA_FAST_1H + 1.0)
    alpha_slow = 2.0 / (EMA_SLOW_1H + 1.0)
    bars["ema_fast_1h"] = alpha_fast * bars["close"] + (1.0 - alpha_fast) * bars["prev_hour_fast"]
    bars["ema_slow_1h"] = alpha_slow * bars["close"] + (1.0 - alpha_slow) * bars["prev_hour_slow"]
    bars["fast_slope"] = bars["ema_fast_1h"] / bars["prev_hour_fast"] - 1.0
    bars["slow_slope"] = bars["ema_slow_1h"] / bars["prev_hour_slow"] - 1.0
    bars["long_structure"] = (bars["ema_fast_1h"] > bars["ema_slow_1h"]).fillna(False)
    bars["short_structure"] = (bars["ema_fast_1h"] < bars["ema_slow_1h"]).fillna(False)
    bars["slope_floor_long"] = ((bars["fast_slope"] > SLOPE_FLOOR) & (bars["slow_slope"] > 0)).fillna(False)
    bars["slope_floor_short"] = ((bars["fast_slope"] < -SLOPE_FLOOR) & (bars["slow_slope"] < 0)).fillna(False)
    bars["slope_strength"] = bars["fast_slope"].abs().fillna(0.0) + bars["slow_slope"].abs().fillna(0.0)

    prev_close = bars["close"].shift(1)
    prev_fast = bars["ema_fast_1h"].shift(1)
    bars["official_long"] = ((bars["long_structure"]) & (bars["slope_floor_long"]) & (prev_close <= prev_fast) & (bars["close"] > bars["ema_fast_1h"]))
    bars["official_short"] = ((bars["short_structure"]) & (bars["slope_floor_short"]) & (prev_close >= prev_fast) & (bars["close"] < bars["ema_fast_1h"]))
    bars["official_dir"] = np.where(bars["official_long"], 1, np.where(bars["official_short"], -1, 0))

    prev_close_15 = bars["close"].shift(1)
    tr = pd.concat(
        [
            (bars["high"] - bars["low"]).abs(),
            (bars["high"] - prev_close_15).abs(),
            (bars["low"] - prev_close_15).abs(),
        ],
        axis=1,
    ).max(axis=1)
    bars["tr15"] = tr
    bars["atr14"] = tr.rolling(ATR_PERIOD, min_periods=ATR_PERIOD).mean()
    return bars


def build_preview_minutes(minute_df: pd.DataFrame, hour_df: pd.DataFrame, bars15: pd.DataFrame) -> pd.DataFrame:
    work = minute_df.copy()
    work["bucket_start"] = work["open_ts"].dt.floor("15min")
    work["hour_start"] = work["close_ts"].dt.floor("1h")
    work["cum_high"] = work.groupby("bucket_start")["high"].cummax()
    work["cum_low"] = work.groupby("bucket_start")["low"].cummin()

    hour_map = hour_df[["hour_start", "ema_fast_hour", "ema_slow_hour"]].copy()
    hour_map["next_hour_start"] = hour_map["hour_start"] + pd.Timedelta(hours=1)
    hour_map = hour_map[["next_hour_start", "ema_fast_hour", "ema_slow_hour"]].rename(
        columns={"next_hour_start": "hour_start", "ema_fast_hour": "prev_hour_fast", "ema_slow_hour": "prev_hour_slow"}
    )
    work = work.merge(hour_map, on="hour_start", how="left")

    alpha_fast = 2.0 / (EMA_FAST_1H + 1.0)
    alpha_slow = 2.0 / (EMA_SLOW_1H + 1.0)
    work["ema_fast_1h"] = alpha_fast * work["close"] + (1.0 - alpha_fast) * work["prev_hour_fast"]
    work["ema_slow_1h"] = alpha_slow * work["close"] + (1.0 - alpha_slow) * work["prev_hour_slow"]
    work["fast_slope"] = work["ema_fast_1h"] / work["prev_hour_fast"] - 1.0
    work["slow_slope"] = work["ema_slow_1h"] / work["prev_hour_slow"] - 1.0
    work["long_structure"] = (work["ema_fast_1h"] > work["ema_slow_1h"]).fillna(False)
    work["short_structure"] = (work["ema_fast_1h"] < work["ema_slow_1h"]).fillna(False)
    work["slope_floor_long"] = ((work["fast_slope"] > SLOPE_FLOOR) & (work["slow_slope"] > 0)).fillna(False)
    work["slope_floor_short"] = ((work["fast_slope"] < -SLOPE_FLOOR) & (work["slow_slope"] < 0)).fillna(False)
    work["slope_strength"] = work["fast_slope"].abs().fillna(0.0) + work["slow_slope"].abs().fillna(0.0)

    prev15 = bars15[["timestamp", "close", "ema_fast_1h", "tr15"]].copy().rename(
        columns={"timestamp": "prev_bucket_start", "close": "prev15_close", "ema_fast_1h": "prev15_fast", "tr15": "prev15_tr"}
    )
    work["prev_bucket_start"] = work["bucket_start"] - pd.Timedelta(minutes=15)
    work = work.merge(prev15, on="prev_bucket_start", how="left")

    tr_hist = bars15[["timestamp", "tr15"]].copy().rename(columns={"timestamp": "hist_bucket_start"})
    hist_sums: list[float] = []
    hist_counts: list[int] = []
    bars15_ts = list(bars15["timestamp"])
    tr_lookup = {ts: float(v) for ts, v in zip(bars15["timestamp"], bars15["tr15"])}
    rolling_vals: list[float] = []
    for ts in bars15_ts:
        prev_ts = ts - pd.Timedelta(minutes=15)
        if prev_ts in tr_lookup:
            rolling_vals.append(tr_lookup[prev_ts])
        if len(rolling_vals) > ATR_PERIOD - 1:
            rolling_vals.pop(0)
        hist_sums.append(float(sum(rolling_vals)))
        hist_counts.append(len(rolling_vals))
    atr_hist = pd.DataFrame({"bucket_start": bars15_ts, "atr_hist_sum13": hist_sums, "atr_hist_count13": hist_counts})
    work = work.merge(atr_hist, on="bucket_start", how="left")

    partial_prev_close = work["prev15_close"]
    partial_tr = pd.concat(
        [
            (work["cum_high"] - work["cum_low"]).abs(),
            (work["cum_high"] - partial_prev_close).abs(),
            (work["cum_low"] - partial_prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    work["partial_tr15"] = partial_tr
    work["atr14_partial"] = np.where(
        work["atr_hist_count13"] >= (ATR_PERIOD - 1),
        (work["atr_hist_sum13"] + work["partial_tr15"]) / ATR_PERIOD,
        np.nan,
    )

    work["preview_long"] = (
        work["long_structure"]
        & work["slope_floor_long"]
        & (work["prev15_close"] <= work["prev15_fast"])
        & (work["close"] > work["ema_fast_1h"])
    )
    work["preview_short"] = (
        work["short_structure"]
        & work["slope_floor_short"]
        & (work["prev15_close"] >= work["prev15_fast"])
        & (work["close"] < work["ema_fast_1h"])
    )
    work["preview_dir"] = np.where(work["preview_long"], 1, np.where(work["preview_short"], -1, 0))
    return work


def derive_tp_sl(entry_price: float, direction: int, atr14: float | None) -> tuple[float, float]:
    if atr14 is not None and math.isfinite(atr14) and atr14 > 0:
        tp_move = TP_ATR_MULT * float(atr14)
        sl_move = SL_ATR_MULT * float(atr14)
        if direction > 0:
            return entry_price + tp_move, entry_price - sl_move
        return entry_price - tp_move, entry_price + sl_move
    tp_rate = FALLBACK_TP_BPS / 10000.0
    sl_rate = FALLBACK_SL_BPS / 10000.0
    if direction > 0:
        return entry_price * (1.0 + tp_rate), entry_price * (1.0 - sl_rate)
    return entry_price * (1.0 - tp_rate), entry_price * (1.0 + sl_rate)


def simulate_exit(
    minute_df: pd.DataFrame,
    open_map: pd.Series,
    entry_ts: pd.Timestamp,
    direction: int,
    entry_price: float,
    atr14: float | None,
    market_cost_bps: float,
) -> ExitResult | None:
    if entry_ts not in open_map.index:
        return None
    timeout_ts = entry_ts + pd.Timedelta(minutes=TIMEOUT_MINUTES)
    tp_price, sl_price = derive_tp_sl(entry_price, direction, atr14)
    entry_fee = market_cost_bps / 10000.0
    exit_scope = minute_df[(minute_df["open_ts"] >= entry_ts) & (minute_df["open_ts"] < timeout_ts)].copy()
    for _, bar in exit_scope.iterrows():
        high = float(bar["high"])
        low = float(bar["low"])
        if direction > 0:
            hit_tp = high >= tp_price
            hit_sl = low <= sl_price
        else:
            hit_tp = low <= tp_price
            hit_sl = high >= sl_price
        if hit_tp and hit_sl:
            exit_price = sl_price
            exit_fee = market_cost_bps / 10000.0
            gross = (exit_price / entry_price - 1.0) * direction
            net = (1.0 + gross) * (1.0 - entry_fee) * (1.0 - exit_fee) - 1.0
            return ExitResult(
                exit_ts=pd.to_datetime(bar["close_ts"], utc=True),
                exit_price=float(exit_price),
                exit_reason="conflict_stop_first",
                gross_ret=float(gross),
                net_ret=float(net),
                exit_fee_bps=market_cost_bps,
                hold_minutes=int((pd.to_datetime(bar["close_ts"], utc=True) - entry_ts).total_seconds() // 60),
                tp_hit=0,
                sl_hit=1,
                timeout_hit=0,
                same_bar_conflict=1,
            )
        if hit_tp:
            exit_price = tp_price
            exit_fee = MAKER_TP_COST_BPS / 10000.0
            gross = (exit_price / entry_price - 1.0) * direction
            net = (1.0 + gross) * (1.0 - entry_fee) * (1.0 - exit_fee) - 1.0
            return ExitResult(
                exit_ts=pd.to_datetime(bar["close_ts"], utc=True),
                exit_price=float(exit_price),
                exit_reason="take_profit",
                gross_ret=float(gross),
                net_ret=float(net),
                exit_fee_bps=MAKER_TP_COST_BPS,
                hold_minutes=int((pd.to_datetime(bar["close_ts"], utc=True) - entry_ts).total_seconds() // 60),
                tp_hit=1,
                sl_hit=0,
                timeout_hit=0,
                same_bar_conflict=0,
            )
        if hit_sl:
            exit_price = sl_price
            exit_fee = market_cost_bps / 10000.0
            gross = (exit_price / entry_price - 1.0) * direction
            net = (1.0 + gross) * (1.0 - entry_fee) * (1.0 - exit_fee) - 1.0
            return ExitResult(
                exit_ts=pd.to_datetime(bar["close_ts"], utc=True),
                exit_price=float(exit_price),
                exit_reason="stop_loss",
                gross_ret=float(gross),
                net_ret=float(net),
                exit_fee_bps=market_cost_bps,
                hold_minutes=int((pd.to_datetime(bar["close_ts"], utc=True) - entry_ts).total_seconds() // 60),
                tp_hit=0,
                sl_hit=1,
                timeout_hit=0,
                same_bar_conflict=0,
            )
    if timeout_ts not in open_map.index:
        return None
    exit_price = float(open_map.loc[timeout_ts])
    exit_fee = market_cost_bps / 10000.0
    gross = (exit_price / entry_price - 1.0) * direction
    net = (1.0 + gross) * (1.0 - entry_fee) * (1.0 - exit_fee) - 1.0
    return ExitResult(
        exit_ts=timeout_ts,
        exit_price=float(exit_price),
        exit_reason="timeout_close",
        gross_ret=float(gross),
        net_ret=float(net),
        exit_fee_bps=market_cost_bps,
        hold_minutes=TIMEOUT_MINUTES,
        tp_hit=0,
        sl_hit=0,
        timeout_hit=1,
        same_bar_conflict=0,
    )


def official_signal_rows(asset: str, symbol: str, bars15: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for i in range(1, len(bars15)):
        row = bars15.iloc[i]
        direction = int(row["official_dir"])
        if direction == 0:
            continue
        rows.append(
            {
                "asset": asset,
                "symbol": symbol,
                "bucket_start": pd.to_datetime(row["timestamp"], utc=True),
                "signal_ts": pd.to_datetime(row["timestamp"], utc=True),
                "signal_confirmed_at": pd.to_datetime(row["signal_confirmed_at"], utc=True),
                "direction": direction,
                "signal_price": float(row["close"]),
                "atr14": float(row["atr14"]) if pd.notna(row["atr14"]) else np.nan,
                "slope_strength": float(row["slope_strength"]),
                "fast_slope": float(row["fast_slope"]) if pd.notna(row["fast_slope"]) else np.nan,
                "slow_slope": float(row["slow_slope"]) if pd.notna(row["slow_slope"]) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def first_preview_rows(asset: str, symbol: str, preview_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    scoped = preview_df[preview_df["preview_dir"] != 0].copy()
    if scoped.empty:
        return pd.DataFrame(columns=["asset", "symbol", "bucket_start", "preview_ts", "preview_dir", "preview_price", "preview_atr14"])
    firsts = scoped.groupby("bucket_start", sort=True).head(1)
    for _, row in firsts.iterrows():
        rows.append(
            {
                "asset": asset,
                "symbol": symbol,
                "bucket_start": pd.to_datetime(row["bucket_start"], utc=True),
                "preview_ts": pd.to_datetime(row["close_ts"], utc=True),
                "preview_dir": int(row["preview_dir"]),
                "preview_price": float(row["close"]),
                "preview_atr14": float(row["atr14_partial"]) if pd.notna(row["atr14_partial"]) else np.nan,
                "preview_slope_strength": float(row["slope_strength"]),
                "preview_fast_slope": float(row["fast_slope"]) if pd.notna(row["fast_slope"]) else np.nan,
                "preview_slow_slope": float(row["slow_slope"]) if pd.notna(row["slow_slope"]) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def build_preview_diagnostics(asset: str, symbol: str, open_map: pd.Series, official_df: pd.DataFrame, preview_first_df: pd.DataFrame) -> pd.DataFrame:
    off = official_df[["bucket_start", "direction", "signal_confirmed_at"]].rename(columns={"direction": "official_dir"})
    merged = preview_first_df.merge(off, on="bucket_start", how="left")
    merged["confirmed_same_dir"] = (merged["preview_dir"] == merged["official_dir"]).astype(int)
    merged["preview_only"] = ((merged["official_dir"].fillna(0) != merged["preview_dir"]).astype(int))
    entry_improve: list[float] = []
    lead_min: list[float] = []
    for _, row in merged.iterrows():
        preview_ts = pd.to_datetime(row["preview_ts"], utc=True)
        official_ts = pd.to_datetime(row["signal_confirmed_at"], utc=True) if pd.notna(row["signal_confirmed_at"]) else pd.NaT
        if pd.isna(official_ts) or preview_ts not in open_map.index or official_ts not in open_map.index:
            entry_improve.append(np.nan)
            lead_min.append(np.nan)
            continue
        preview_px = float(open_map.loc[preview_ts])
        official_px = float(open_map.loc[official_ts])
        direction = int(row["preview_dir"])
        improve = (official_px / preview_px - 1.0) * 10000.0 if direction > 0 else (preview_px / official_px - 1.0) * 10000.0
        entry_improve.append(float(improve))
        lead_min.append(float((official_ts - preview_ts).total_seconds() / 60.0))
    merged["lead_minutes"] = lead_min
    merged["entry_improve_bps"] = entry_improve
    merged["asset"] = asset
    merged["symbol"] = symbol
    return merged


def simulate_mode(
    *,
    asset: str,
    symbol: str,
    minute_df: pd.DataFrame,
    open_map: pd.Series,
    signals: pd.DataFrame,
    official_lookup: pd.DataFrame,
    mode: str,
    market_cost_bps: float,
) -> pd.DataFrame:
    if signals.empty:
        return pd.DataFrame()
    rows: list[dict[str, object]] = []
    last_exit_ts = pd.Timestamp.min.tz_localize("UTC")
    official_by_bucket = official_lookup.set_index("bucket_start") if not official_lookup.empty else pd.DataFrame()
    for _, sig in signals.sort_values("entry_candidate_ts").iterrows():
        entry_ts = pd.to_datetime(sig["entry_candidate_ts"], utc=True)
        if entry_ts <= last_exit_ts:
            continue
        if entry_ts not in open_map.index:
            continue
        direction = int(sig["direction"])
        entry_price = float(open_map.loc[entry_ts])
        atr14 = float(sig["atr14"]) if pd.notna(sig["atr14"]) else np.nan
        exit_result = simulate_exit(minute_df, open_map, entry_ts, direction, entry_price, atr14, market_cost_bps)
        if exit_result is None:
            continue
        bucket_start = pd.to_datetime(sig["bucket_start"], utc=True)
        official_dir = 0
        if not official_by_bucket.empty and bucket_start in official_by_bucket.index:
            maybe = official_by_bucket.loc[bucket_start]
            if isinstance(maybe, pd.DataFrame):
                maybe = maybe.iloc[0]
            official_dir = int(maybe["direction"])
        rows.append(
            {
                "asset": asset,
                "symbol": symbol,
                "mode": mode,
                "market_cost_bps": float(market_cost_bps),
                "bucket_start": bucket_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "signal_ts": pd.to_datetime(sig["signal_ts"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "signal_confirmed_at": pd.to_datetime(sig["signal_confirmed_at"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ") if pd.notna(sig["signal_confirmed_at"]) else None,
                "entry_ts": entry_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": exit_result.exit_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "direction": "long" if direction > 0 else "short",
                "direction_sign": int(direction),
                "signal_price": float(sig["signal_price"]),
                "entry_price": float(entry_price),
                "exit_price": float(exit_result.exit_price),
                "gross_ret": float(exit_result.gross_ret),
                "net_ret": float(exit_result.net_ret),
                "exit_reason": exit_result.exit_reason,
                "hold_minutes": int(exit_result.hold_minutes),
                "tp_hit": int(exit_result.tp_hit),
                "sl_hit": int(exit_result.sl_hit),
                "timeout_hit": int(exit_result.timeout_hit),
                "same_bar_conflict": int(exit_result.same_bar_conflict),
                "atr14": atr14,
                "slope_strength": float(sig["slope_strength"]),
                "official_same_bar_dir": int(official_dir),
                "confirmed_at_close": int(official_dir == direction),
                "lead_minutes": float(sig.get("lead_minutes", np.nan)),
                "entry_improve_bps": float(sig.get("entry_improve_bps", np.nan)),
                "preview_only": int(sig.get("preview_only", 0)),
            }
        )
        last_exit_ts = exit_result.exit_ts
    return pd.DataFrame(rows)


def summarize_asset(trades: pd.DataFrame, *, asset: str, mode: str, market_cost_bps: float) -> dict[str, object]:
    if trades.empty:
        return {
            "asset": asset,
            "mode": mode,
            "market_cost_bps": float(market_cost_bps),
            "trades": 0,
            "total_return": 0.0,
            "win_rate": np.nan,
            "avg_net_ret": np.nan,
            "avg_hold_minutes": np.nan,
            "tp_hit_rate": np.nan,
            "sl_hit_rate": np.nan,
            "timeout_rate": np.nan,
            "same_bar_conflict_rate": np.nan,
            "confirmed_at_close_ratio": np.nan,
            "preview_only_ratio": np.nan,
            "avg_lead_minutes": np.nan,
            "avg_entry_improve_bps": np.nan,
        }
    return {
        "asset": asset,
        "mode": mode,
        "market_cost_bps": float(market_cost_bps),
        "trades": int(len(trades)),
        "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
        "win_rate": float((trades["net_ret"] > 0).mean()),
        "avg_net_ret": float(trades["net_ret"].mean()),
        "avg_hold_minutes": float(trades["hold_minutes"].mean()),
        "tp_hit_rate": float(trades["tp_hit"].mean()),
        "sl_hit_rate": float(trades["sl_hit"].mean()),
        "timeout_rate": float(trades["timeout_hit"].mean()),
        "same_bar_conflict_rate": float(trades["same_bar_conflict"].mean()),
        "confirmed_at_close_ratio": float(trades["confirmed_at_close"].mean()) if "confirmed_at_close" in trades else np.nan,
        "preview_only_ratio": float(trades["preview_only"].mean()) if "preview_only" in trades else np.nan,
        "avg_lead_minutes": float(trades["lead_minutes"].dropna().mean()) if trades["lead_minutes"].notna().any() else np.nan,
        "avg_entry_improve_bps": float(trades["entry_improve_bps"].dropna().mean()) if trades["entry_improve_bps"].notna().any() else np.nan,
    }


def summarize_overall(asset_summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    if asset_summary.empty:
        return pd.DataFrame()
    for (mode, cost), grp in asset_summary.groupby(["mode", "market_cost_bps"], sort=False):
        vals = grp["total_return"].to_numpy(dtype=float)
        rows.append(
            {
                "mode": mode,
                "market_cost_bps": float(cost),
                "asset_count": int(len(grp)),
                "positive_asset_ratio": float(np.mean(vals > 0)) if len(vals) else np.nan,
                "mean_total_return": float(np.nanmean(vals)) if len(vals) else np.nan,
                "median_total_return": float(np.nanmedian(vals)) if len(vals) else np.nan,
                "mean_trades": float(grp["trades"].mean()),
                "mean_win_rate": float(grp["win_rate"].mean()),
                "mean_avg_net_ret": float(grp["avg_net_ret"].mean()),
                "mean_tp_hit_rate": float(grp["tp_hit_rate"].mean()),
                "mean_sl_hit_rate": float(grp["sl_hit_rate"].mean()),
                "mean_timeout_rate": float(grp["timeout_rate"].mean()),
                "mean_confirmed_at_close_ratio": float(grp["confirmed_at_close_ratio"].mean()),
                "mean_preview_only_ratio": float(grp["preview_only_ratio"].mean()),
                "mean_lead_minutes": float(grp["avg_lead_minutes"].mean()),
                "mean_entry_improve_bps": float(grp["avg_entry_improve_bps"].mean()),
            }
        )
    return pd.DataFrame(rows)


def build_window_summary(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty or len(trades) < 24:
        return pd.DataFrame(columns=["mode", "market_cost_bps", "window", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_win_rate"])
    work = trades.copy()
    work["entry_ts"] = pd.to_datetime(work["entry_ts"], utc=True)
    rows: list[dict[str, object]] = []
    for (mode, cost), grp0 in work.groupby(["mode", "market_cost_bps"], sort=False):
        grp0 = grp0.sort_values("entry_ts").copy()
        grp0["window"] = pd.qcut(grp0["entry_ts"].view("int64"), q=3, labels=["older", "middle", "recent"], duplicates="drop")
        for window, grp in grp0.groupby("window", sort=False, observed=False):
            if grp.empty:
                continue
            asset_total = grp.groupby("asset")["net_ret"].apply(lambda s: float((1.0 + s).prod() - 1.0))
            rows.append(
                {
                    "mode": mode,
                    "market_cost_bps": float(cost),
                    "window": str(window),
                    "mean_total_return": float(asset_total.mean()) if len(asset_total) else np.nan,
                    "positive_asset_ratio": float((asset_total > 0).mean()) if len(asset_total) else np.nan,
                    "mean_trades": float(grp.groupby("asset").size().mean()) if len(grp) else np.nan,
                    "mean_win_rate": float(grp.groupby("asset")["net_ret"].apply(lambda s: (s > 0).mean()).mean()) if len(grp) else np.nan,
                }
            )
    return pd.DataFrame(rows)


def build_html(tag: str, generated_at: str, overall: pd.DataFrame, asset_summary: pd.DataFrame, windows: pd.DataFrame, diagnostics: pd.DataFrame, meta: dict[str, object]) -> str:
    headline = "暂无结果。"
    preview6 = overall[(overall["mode"] == "preview_unclosed15m") & (overall["market_cost_bps"] == 6.0)]
    official6 = overall[(overall["mode"] == "official_close") & (overall["market_cost_bps"] == 6.0)]
    if not preview6.empty and not official6.empty:
        p = preview6.iloc[0]
        o = official6.iloc[0]
        headline = (
            f"在 {int(meta['days'])}d / {meta['universe']} / market cost {int(6)}bps 下，preview 版 mean_total_return≈{pct(p['mean_total_return'])}，"
            f"official 版≈{pct(o['mean_total_return'])}；preview 的 mean_lead≈{num(p['mean_lead_minutes'], 2)} 分钟，"
            f"mean_entry_improve≈{num(p['mean_entry_improve_bps'], 2)} bps。"
        )
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank32b 未收盘 15m 预判版回测</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1200px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background: #f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .muted {{ color:#6b7280; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
  </style>
</head>
<body>
  <h1>Rank32b · 未收盘 15m 预判版回测</h1>
  <p class='muted'>生成时间：{escape(generated_at)} ｜ tag={escape(tag)} ｜ universe={escape(str(meta['universe']))} ｜ days={escape(str(meta['days']))}</p>

  <div class='card'>
    <h2>这轮回答什么</h2>
    <ul>
      <li><b>official_close：</b>只在 15m bar 正式收盘时确认信号，然后立刻按 1m 开盘近似入场。</li>
      <li><b>preview_unclosed15m：</b>每分钟检查一次，把当前未收盘 15m bar 的临时 close/high/low 当成最后一根 bar 来计算同一套 32b slope-floor continuation 信号。</li>
      <li><b>离场：</b>TP={TP_ATR_MULT:.2f} ATR（maker 近似），SL={SL_ATR_MULT:.2f} ATR（market），timeout={TIMEOUT_MINUTES}m（market）。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>headline</h2>
    <p><b>{escape(headline)}</b></p>
  </div>

  <div class='card'>
    <h2>整体结果</h2>
    {render_table(overall[["mode","market_cost_bps","asset_count","positive_asset_ratio","mean_total_return","median_total_return","mean_trades","mean_win_rate","mean_avg_net_ret","mean_tp_hit_rate","mean_sl_hit_rate","mean_timeout_rate","mean_confirmed_at_close_ratio","mean_preview_only_ratio","mean_lead_minutes","mean_entry_improve_bps"]], percent_cols={"positive_asset_ratio","mean_total_return","median_total_return","mean_win_rate","mean_avg_net_ret","mean_tp_hit_rate","mean_sl_hit_rate","mean_timeout_rate","mean_confirmed_at_close_ratio","mean_preview_only_ratio"}, digits_cols={"asset_count":0, "mean_trades":1, "mean_lead_minutes":2, "mean_entry_improve_bps":2})}
  </div>

  <div class='card'>
    <h2>分资产摘要</h2>
    {render_table(asset_summary[["asset","mode","market_cost_bps","trades","total_return","win_rate","avg_net_ret","tp_hit_rate","sl_hit_rate","timeout_rate","confirmed_at_close_ratio","preview_only_ratio","avg_lead_minutes","avg_entry_improve_bps"]], percent_cols={"total_return","win_rate","avg_net_ret","tp_hit_rate","sl_hit_rate","timeout_rate","confirmed_at_close_ratio","preview_only_ratio"}, digits_cols={"trades":0, "avg_lead_minutes":2, "avg_entry_improve_bps":2})}
  </div>

  <div class='card'>
    <h2>时间窗稳定性</h2>
    {render_table(windows[["mode","market_cost_bps","window","mean_total_return","positive_asset_ratio","mean_trades","mean_win_rate"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_win_rate"}, digits_cols={"mean_trades":1})}
  </div>

  <div class='card'>
    <h2>Preview 诊断</h2>
    {render_table(diagnostics[["asset","symbol","bucket_start","preview_ts","preview_dir","official_dir","confirmed_same_dir","preview_only","lead_minutes","entry_improve_bps"]].head(120), percent_cols=set(), digits_cols={"lead_minutes":2, "entry_improve_bps":2})}
    <p class='muted'>仅展示前 120 行；完整诊断见 artifacts CSV。</p>
  </div>
</body>
</html>
"""


def run_symbol(asset: str, symbol: str, days: int, refresh: bool, costs: list[float]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    minute_df = load_or_fetch_1m(symbol, days=days, refresh=refresh)
    if minute_df.empty or len(minute_df) < 10_000:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    open_map = minute_df.set_index("open_ts")["open"]
    hour_df = build_completed_hours(minute_df)
    bars15 = build_completed_15m(minute_df, hour_df)
    preview_df = build_preview_minutes(minute_df, hour_df, bars15)
    official_df = official_signal_rows(asset, symbol, bars15)
    preview_first_df = first_preview_rows(asset, symbol, preview_df)
    diagnostics = build_preview_diagnostics(asset, symbol, open_map, official_df, preview_first_df)

    official_lookup = official_df[["bucket_start", "direction"]].copy() if not official_df.empty else pd.DataFrame(columns=["bucket_start", "direction"])
    official_signals = official_df.copy()
    if not official_signals.empty:
        official_signals["entry_candidate_ts"] = official_signals["signal_confirmed_at"]
    preview_signals = diagnostics.copy()
    if not preview_signals.empty:
        preview_signals = preview_signals.rename(columns={"preview_ts": "entry_candidate_ts", "preview_dir": "direction", "preview_price": "signal_price", "preview_atr14": "atr14", "preview_slope_strength": "slope_strength"})
        preview_signals["signal_ts"] = preview_signals["entry_candidate_ts"]
        preview_signals["signal_confirmed_at"] = preview_signals["bucket_start"] + pd.Timedelta(minutes=15)

    all_trades: list[pd.DataFrame] = []
    for cost in costs:
        if not official_signals.empty:
            all_trades.append(simulate_mode(asset=asset, symbol=symbol, minute_df=minute_df, open_map=open_map, signals=official_signals, official_lookup=official_lookup, mode="official_close", market_cost_bps=cost))
        if not preview_signals.empty:
            all_trades.append(simulate_mode(asset=asset, symbol=symbol, minute_df=minute_df, open_map=open_map, signals=preview_signals, official_lookup=official_lookup, mode="preview_unclosed15m", market_cost_bps=cost))
    trades = pd.concat([df for df in all_trades if not df.empty], ignore_index=True) if all_trades else pd.DataFrame()
    return trades, diagnostics, bars15


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank32b 未收盘 15m 预判版回测")
    parser.add_argument("--universe", default="canary_core18", choices=sorted(UNIVERSE_PRESETS.keys()))
    parser.add_argument("--symbols", default="", help="逗号分隔，例如 BTCUSDT,ETHUSDT")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS)
    parser.add_argument("--market-costs", default=",".join(str(x) for x in MARKET_COSTS_BPS))
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--tag", default="")
    parser.add_argument("--max-symbols", type=int, default=0)
    args = parser.parse_args()

    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(CACHE_DIR)

    assets = parse_symbols(args.symbols) if args.symbols.strip() else dict(UNIVERSE_PRESETS[args.universe])
    if args.max_symbols and args.max_symbols > 0:
        assets = dict(list(assets.items())[: args.max_symbols])
    costs = parse_csv_floats(args.market_costs)
    tag = args.tag.strip() or f"{args.universe}_{args.days}d"
    run_dir = ensure_dir(ART_DIR / tag)
    site_path = SITE_DIR / f"{tag}.html"

    all_trades: list[pd.DataFrame] = []
    all_diags: list[pd.DataFrame] = []
    summary_rows: list[dict[str, object]] = []
    symbol_meta: list[dict[str, object]] = []

    for idx, (asset, symbol) in enumerate(assets.items(), start=1):
        print(f"[{idx}/{len(assets)}] {asset} {symbol} ...", flush=True)
        try:
            trades, diags, bars15 = run_symbol(asset, symbol, days=args.days, refresh=args.refresh, costs=costs)
        except Exception as exc:  # noqa: BLE001
            print(f"  ! failed: {exc}", flush=True)
            symbol_meta.append({"asset": asset, "symbol": symbol, "status": "failed", "error": str(exc)})
            continue
        if not trades.empty:
            all_trades.append(trades)
        if not diags.empty:
            all_diags.append(diags)
        symbol_meta.append({"asset": asset, "symbol": symbol, "status": "ok", "bars15": int(len(bars15)), "trade_rows": int(len(trades)), "diag_rows": int(len(diags))})
        for mode in ["official_close", "preview_unclosed15m"]:
            for cost in costs:
                part = trades[(trades["mode"] == mode) & (trades["market_cost_bps"] == cost)].copy() if not trades.empty else pd.DataFrame()
                summary_rows.append(summarize_asset(part, asset=asset, mode=mode, market_cost_bps=cost))

    trades_df = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    diag_df = pd.concat(all_diags, ignore_index=True) if all_diags else pd.DataFrame()
    asset_summary = pd.DataFrame(summary_rows)
    overall = summarize_overall(asset_summary)
    windows = build_window_summary(trades_df)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    meta = {
        "generated_at": generated_at,
        "universe": args.universe if not args.symbols.strip() else "custom",
        "days": int(args.days),
        "market_costs": costs,
        "tp_atr_mult": TP_ATR_MULT,
        "sl_atr_mult": SL_ATR_MULT,
        "timeout_minutes": TIMEOUT_MINUTES,
        "fallback_tp_bps": FALLBACK_TP_BPS,
        "fallback_sl_bps": FALLBACK_SL_BPS,
        "maker_tp_cost_bps": MAKER_TP_COST_BPS,
        "symbols": assets,
        "symbol_meta": symbol_meta,
    }

    if not trades_df.empty:
        trades_df.to_csv(run_dir / "trades.csv", index=False)
    if not diag_df.empty:
        diag_df.to_csv(run_dir / "preview_diagnostics.csv", index=False)
    if not asset_summary.empty:
        asset_summary.to_csv(run_dir / "asset_summary.csv", index=False)
    if not overall.empty:
        overall.to_csv(run_dir / "overall_summary.csv", index=False)
    if not windows.empty:
        windows.to_csv(run_dir / "window_summary.csv", index=False)
    (run_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    site_path.write_text(build_html(tag, generated_at, overall, asset_summary, windows, diag_df, meta), encoding="utf-8")

    print("\n=== overall_summary ===")
    if overall.empty:
        print("(empty)")
    else:
        print(overall.to_string(index=False))
    print(f"\nartifacts: {run_dir}")
    print(f"site: {site_path}")


if __name__ == "__main__":
    main()
