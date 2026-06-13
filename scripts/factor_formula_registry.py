"""Factor Formula Registry — all registered FactorSpec objects.

This is the single source of truth for which factors exist in the library.
build_factor_values.py iterates REGISTRY to compute all factors.

To add a new factor:
1. Write its compute function (or compose from factor_ops)
2. Add a FactorSpec to REGISTRY
3. Run build_factor_values.py and evaluate_factors.py
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from factor_specs import FactorSpec
from factor_ops import (
    delay, delta, rolling_mean, rolling_std, rolling_corr,
    zscore, ema, true_range,
)

# ── V0 Original 5 Factors ──────────────────────────────────────────

def _compute_mom_20h(df: pd.DataFrame) -> pd.Series:
    """Momentum 20h: close / close_20h_ago - 1."""
    return df["close"] / delay(df["close"], 20) - 1.0


def _compute_reversal_5h(df: pd.DataFrame) -> pd.Series:
    """Reversal 5h: -(close / close_5h_ago - 1)."""
    return -(df["close"] / delay(df["close"], 5) - 1.0)


def _compute_volatility_20h(df: pd.DataFrame) -> pd.Series:
    """Volatility 20h: rolling std of returns over 20 bars."""
    ret = df["close"].pct_change()
    return rolling_std(ret, 20)


def _compute_rsi_14h(df: pd.DataFrame) -> pd.Series:
    """RSI 14h: classic Wilder RSI."""
    d = df["close"].diff()
    up = d.clip(lower=0)
    down = -d.clip(upper=0)
    avg_up = up.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    avg_down = down.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    rs = avg_up / avg_down.replace(0, np.nan)
    out = 100 - 100 / (1 + rs)
    out = out.where(avg_down != 0, 100.0)
    out = out.where(avg_up != 0, 0.0)
    return out


def _compute_bb_zscore_20h(df: pd.DataFrame) -> pd.Series:
    """Bollinger Band z-score 20h: (close - mean20) / std20."""
    return zscore(df["close"], 20)


# ── Batch 1: WQ101 / Alpha158 / Technical ──────────────────────────

def _compute_wq101_alpha101(df: pd.DataFrame) -> pd.Series:
    """WQ101 Alpha#101: (close - open) / (high - low + 0.001)."""
    o, h, l, c = df["open"], df["high"], df["low"], df["close"]
    return (c - o) / (h - l + 0.001)


def _compute_wq101_alpha12(df: pd.DataFrame) -> pd.Series:
    """WQ101 Alpha#12: sign(delta(volume, 1)) * (-delta(close, 1))."""
    vol_delta = delta(df["volume"], 1)
    close_delta = delta(df["close"], 1)
    return np.sign(vol_delta) * (-1 * close_delta)


def _compute_wq101_alpha53(df: pd.DataFrame) -> pd.Series:
    """WQ101 Alpha#53: -delta(pos, 9), pos = (c-l-(h-c))/(c-l+0.001)."""
    h, l, c = df["high"], df["low"], df["close"]
    pos = ((c - l) - (h - c)) / (c - l + 0.001)
    return -1 * pos.diff(9)


def _compute_q158_high_low_range(df: pd.DataFrame) -> pd.Series:
    """Alpha158 High-Low Range: (high - low) / close."""
    h, l, c = df["high"], df["low"], df["close"]
    return (h - l) / c.replace(0, np.nan)


def _compute_tech_macd(df: pd.DataFrame) -> pd.Series:
    """MACD histogram: EMA(close,12) - EMA(close,26) signal line."""
    c = df["close"]
    macd_line = ema(c, 12) - ema(c, 26)
    signal = ema(macd_line, 9)
    return macd_line - signal


def _compute_tech_atr(df: pd.DataFrame) -> pd.Series:
    """ATR 14h: rolling mean of True Range over 14 bars."""
    tr = true_range(df["high"], df["low"], df["close"])
    return rolling_mean(tr, 14)


# ── Registry ────────────────────────────────────────────────────────

REGISTRY: list[FactorSpec] = [
    # V0 Original
    FactorSpec(
        factor_id="mom_20h", family="momentum",
        required_columns=["close"], lookback_window=20,
        expected_direction="positive",
        compute_fn=_compute_mom_20h,
        notes="close / close_20h_ago - 1",
    ),
    FactorSpec(
        factor_id="reversal_5h", family="momentum",
        required_columns=["close"], lookback_window=5,
        expected_direction="negative",
        compute_fn=_compute_reversal_5h,
        notes="-(close / close_5h_ago - 1)",
    ),
    FactorSpec(
        factor_id="volatility_20h", family="volatility",
        required_columns=["close"], lookback_window=21,
        expected_direction="negative",
        compute_fn=_compute_volatility_20h,
        notes="rolling std of returns, 20 bars",
    ),
    FactorSpec(
        factor_id="rsi_14h", family="technical",
        required_columns=["close"], lookback_window=14,
        expected_direction="negative",
        compute_fn=_compute_rsi_14h,
        notes="Wilder RSI 14",
    ),
    FactorSpec(
        factor_id="bb_zscore_20h", family="technical",
        required_columns=["close"], lookback_window=20,
        expected_direction="negative",
        compute_fn=_compute_bb_zscore_20h,
        notes="(close - mean20) / std20",
    ),
    # Batch 1: WQ101
    FactorSpec(
        factor_id="wq101_alpha101", family="wq101",
        required_columns=["open", "high", "low", "close"], lookback_window=1,
        expected_direction="conditional",
        compute_fn=_compute_wq101_alpha101,
        notes="(close - open) / (high - low + eps); direction intentionally set to conditional to avoid post-hoc fitting",
    ),
    FactorSpec(
        factor_id="wq101_alpha12", family="wq101",
        required_columns=["volume", "close"], lookback_window=2,
        expected_direction="conditional",
        compute_fn=_compute_wq101_alpha12,
        notes="sign(dvol) * (-dclose); lookback=2 because delta(1) needs t and t-1",
    ),
    FactorSpec(
        factor_id="wq101_alpha53", family="wq101",
        required_columns=["high", "low", "close"], lookback_window=10,
        expected_direction="conditional",
        compute_fn=_compute_wq101_alpha53,
        notes="-delta(intraday_position, 9); lookback=10 because diff(9) needs t and t-9",
    ),
    # Batch 1: Alpha158
    FactorSpec(
        factor_id="q158_high_low_range", family="alpha158",
        required_columns=["high", "low", "close"], lookback_window=1,
        expected_direction="conditional",
        compute_fn=_compute_q158_high_low_range,
        notes="(high - low) / close",
    ),
    # Batch 1: Technical
    FactorSpec(
        factor_id="tech_macd", family="technical",
        required_columns=["close"], lookback_window=26,
        expected_direction="positive",
        compute_fn=_compute_tech_macd,
        notes="MACD histogram (EMA12-EMA26 signal)",
    ),
    FactorSpec(
        factor_id="tech_atr", family="technical",
        required_columns=["high", "low", "close"], lookback_window=15,
        expected_direction="conditional",
        compute_fn=_compute_tech_atr,
        notes="Average True Range 14 bars",
    ),
]

# Quick lookup by factor_id
REGISTRY_BY_ID: dict[str, FactorSpec] = {fs.factor_id: fs for fs in REGISTRY}
