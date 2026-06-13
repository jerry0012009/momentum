"""Batch 1 factor computation functions for crypto factor library.

Each function accepts a single-symbol DataFrame (already grouped by symbol)
and returns a pd.Series with the same index. All functions use only current
and past data — no shift(-k), no future leak, no cross-symbol mixing.

Functions:
    compute_wq101_alpha101   — intraday candle position
    compute_wq101_alpha12    — volume-price sign momentum
    compute_wq101_alpha53    — intraday position delta (9 bars)
    compute_q158_high_low_range — intraday range / close
    compute_tech_macd        — MACD histogram (EMA12-EMA26 signal)
    compute_tech_atr         — Average True Range (14 bars)
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def compute_wq101_alpha101(df: pd.DataFrame) -> pd.Series:
    """WQ101 Alpha#101: (close - open) / (high - low + 0.001)

    Intraday candle position. Positive = close above open (bullish).
    Epsilon 0.001 prevents division by zero on flat bars.
    No warmup required.
    """
    o, h, l, c = df["open"], df["high"], df["low"], df["close"]
    return (c - o) / (h - l + 0.001)


def compute_wq101_alpha12(df: pd.DataFrame) -> pd.Series:
    """WQ101 Alpha#12: sign(delta(volume, 1)) * (-1 * delta(close, 1))

    Rising volume + falling price = positive (distribution).
    sign() produces {-1, 0, +1}. First row per symbol is NaN (diff(1)).
    """
    v, c = df["volume"], df["close"]
    vol_delta = v.diff(1)
    close_delta = c.diff(1)
    return np.sign(vol_delta) * (-1 * close_delta)


def compute_wq101_alpha53(df: pd.DataFrame) -> pd.Series:
    """WQ101 Alpha#53: -1 * delta(pos, 9)

    pos = ((close - low) - (high - close)) / (close - low + 0.001)
    First 9 rows per symbol are NaN (diff(9)).
    expected_direction = conditional.
    """
    h, l, c = df["high"], df["low"], df["close"]
    pos = ((c - l) - (h - c)) / (c - l + 0.001)
    return -1 * pos.diff(9)


def compute_q158_high_low_range(df: pd.DataFrame) -> pd.Series:
    """Alpha158 High-Low Range: (high - low) / close

    Always non-negative. Direction-neutral volatility proxy.
    No warmup required.
    """
    h, l, c = df["high"], df["low"], df["close"]
    return (h - l) / c.replace(0, np.nan)


def compute_tech_macd(df: pd.DataFrame) -> pd.Series:
    """MACD histogram: EMA(close,12) - EMA(close,26) signal line.

    macd_line = EMA12 - EMA26
    signal    = EMA(macd_line, 9)
    histogram = macd_line - signal
    EMA warmup ~52 bars for stability. Use adjust=False to match TA-Lib.
    """
    c = df["close"]
    ema12 = c.ewm(span=12, adjust=False).mean()
    ema26 = c.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal = macd_line.ewm(span=9, adjust=False).mean()
    return macd_line - signal


def compute_tech_atr(df: pd.DataFrame) -> pd.Series:
    """Average True Range (14 bars).

    TR = max(high-low, |high-prev_close|, |low-prev_close|)
    ATR = SMA(TR, 14)
    First 14 rows per symbol are NaN (min_periods=14).
    Direction-neutral volatility proxy.
    """
    h, l, c = df["high"], df["low"], df["close"]
    prev_c = c.shift(1)
    tr1 = h - l
    tr2 = (h - prev_c).abs()
    tr3 = (l - prev_c).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(14, min_periods=14).mean()
