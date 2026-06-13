"""Lightweight factor building-block operators.

All functions are pure: they take a pd.Series (or DataFrame columns) and
return a pd.Series with the same index. No side effects, no cross-symbol
mixing, no shift(-k) future leak.

These are the primitive ops that higher-level factor formulas compose.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


# ── Time-series shifts ──────────────────────────────────────────────

def delay(series: pd.Series, n: int) -> pd.Series:
    """Value n periods ago. NaN for first n rows.

    Equivalent to series.shift(n). Always uses past data.
    """
    return series.shift(n)


def delta(series: pd.Series, n: int) -> pd.Series:
    """Change over n periods: series[t] - series[t-n].

    NaN for first n rows. No future leak.
    """
    return series - delay(series, n)


# ── Rolling statistics ──────────────────────────────────────────────

def rolling_mean(series: pd.Series, n: int) -> pd.Series:
    """Simple moving average over n periods."""
    return series.rolling(n, min_periods=n).mean()


def rolling_std(series: pd.Series, n: int) -> pd.Series:
    """Sample standard deviation over n periods (ddof=1)."""
    return series.rolling(n, min_periods=n).std(ddof=1)


def rolling_min(series: pd.Series, n: int) -> pd.Series:
    """Rolling minimum over n periods."""
    return series.rolling(n, min_periods=n).min()


def rolling_max(series: pd.Series, n: int) -> pd.Series:
    """Rolling maximum over n periods."""
    return series.rolling(n, min_periods=n).max()


def rolling_corr(x: pd.Series, y: pd.Series, n: int) -> pd.Series:
    """Rolling Pearson correlation over n periods."""
    return x.rolling(n, min_periods=n).corr(y)


# ── Ranking ─────────────────────────────────────────────────────────

def ts_rank(series: pd.Series, n: int) -> pd.Series:
    """Percentile rank of current value within last n observations.

    Returns value in [0, 1]. NaN for first n-1 rows.
    Uses rank(pct=True) on the rolling window.
    """
    return series.rolling(n, min_periods=n).apply(
        lambda x: pd.Series(x).rank(pct=True).iloc[-1], raw=False
    )


# ── Normalization ───────────────────────────────────────────────────

def zscore(series: pd.Series, n: int) -> pd.Series:
    """Rolling z-score: (series - mean_n) / std_n.

    NaN where std is zero or insufficient data.
    """
    mu = rolling_mean(series, n)
    sigma = rolling_std(series, n)
    return (series - mu) / sigma.replace(0, np.nan)


# ── Math transforms ─────────────────────────────────────────────────

def signed_power(series: pd.Series, a: float) -> pd.Series:
    """sign(x) * |x|^a.

    Preserves sign while applying power to magnitude.
    """
    return np.sign(series) * np.abs(series) ** a


def ema(series: pd.Series, span: int) -> pd.Series:
    """Exponential moving average.

    Uses adjust=False to match TA-Lib convention.
    """
    return series.ewm(span=span, adjust=False).mean()


# ── OHLCV-specific ──────────────────────────────────────────────────

def true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    """True Range: max(high-low, |high-prev_close|, |low-prev_close|).

    First row per symbol is NaN because prev_close is unavailable.
    Uses np.where to propagate NaN when prev_close is NaN (i.e. first row),
    even though pd.DataFrame.max(skipna=True) would otherwise return high-low.
    """
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    result = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    # Force NaN when prev_close is unavailable (first row per symbol)
    return pd.Series(
        np.where(prev_close.isna(), np.nan, result),
        index=high.index,
    )
