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


def rolling_quantile(series: pd.Series, n: int, q: float) -> pd.Series:
    """Rolling quantile over n periods."""
    return series.rolling(n, min_periods=n).quantile(q)


def _rolling_regression_components(series: pd.Series, n: int) -> tuple[pd.Series, pd.Series, float]:
    """Return centered Sxy, centered Syy, and fixed Sxx for y ~ x over rolling windows."""
    pos = pd.Series(np.arange(len(series), dtype=float), index=series.index)
    sum_y = rolling_sum(series, n)
    sum_y2 = rolling_sum(series * series, n)
    sum_iy_global = rolling_sum(series * pos, n)

    window_start = pos - n + 1
    sum_xy = sum_iy_global - window_start * sum_y

    sum_x = n * (n - 1) / 2.0
    sum_x2 = n * (n - 1) * (2 * n - 1) / 6.0
    sxx = sum_x2 - (sum_x * sum_x) / n
    sxy = sum_xy - (sum_x * sum_y) / n
    syy = sum_y2 - (sum_y * sum_y) / n
    return sxy, syy, sxx


def rolling_slope(series: pd.Series, n: int) -> pd.Series:
    """Rolling linear-regression slope for y ~ x, where x is 0..n-1."""
    sxy, _, sxx = _rolling_regression_components(series, n)
    return sxy / sxx


def rolling_rsquare(series: pd.Series, n: int) -> pd.Series:
    """Rolling linear-regression R-squared for y ~ x, where x is 0..n-1."""
    sxy, syy, sxx = _rolling_regression_components(series, n)
    denom = sxx * syy
    return (sxy * sxy) / denom.replace(0, np.nan)


def rolling_residual(series: pd.Series, n: int) -> pd.Series:
    """Latest-point residual from rolling linear regression y ~ x over n periods."""
    slope = rolling_slope(series, n)
    mean_y = rolling_mean(series, n)
    mean_x = (n - 1) / 2.0
    intercept = mean_y - slope * mean_x
    fitted_latest = intercept + slope * (n - 1)
    return series - fitted_latest


def rolling_idxmax(series: pd.Series, n: int) -> pd.Series:
    """Bars since the latest maximum inside each rolling window, scaled by caller if needed."""
    return series.rolling(n, min_periods=n).apply(
        lambda x: int(np.nanargmax(x[::-1])),
        raw=True,
    )


def rolling_idxmin(series: pd.Series, n: int) -> pd.Series:
    """Bars since the latest minimum inside each rolling window, scaled by caller if needed."""
    return series.rolling(n, min_periods=n).apply(
        lambda x: int(np.nanargmin(x[::-1])),
        raw=True,
    )


def rolling_corr(x: pd.Series, y: pd.Series, n: int) -> pd.Series:
    """Rolling Pearson correlation over n periods."""
    return x.rolling(n, min_periods=n).corr(y)


def rolling_sum(series: pd.Series, n: int) -> pd.Series:
    """Rolling sum over n periods."""
    return series.rolling(n, min_periods=n).sum()


def rolling_skew(series: pd.Series, n: int) -> pd.Series:
    """Rolling skewness over n periods (Fisher definition, bias=True)."""
    return series.rolling(n, min_periods=n).skew()


# ── Ranking ─────────────────────────────────────────────────────────

def ts_rank(series: pd.Series, n: int) -> pd.Series:
    """Percentile rank of current value within last n observations.

    Returns value in [0, 1]. NaN for first n-1 rows.
    Uses rank(pct=True) on the rolling window.
    """
    def _rank_last_pct(x: np.ndarray) -> float:
        last = x[-1]
        if np.isnan(last):
            return np.nan
        valid = x[~np.isnan(x)]
        if len(valid) < n:
            return np.nan
        less = np.sum(valid < last)
        equal = np.sum(valid == last)
        # Match pandas rank(pct=True) with method="average" for the last value.
        return (less + (equal + 1) / 2) / len(valid)

    return series.rolling(n, min_periods=n).apply(_rank_last_pct, raw=True)


# ── Normalization ───────────────────────────────────────────────────

def zscore(series: pd.Series, n: int) -> pd.Series:
    """Rolling z-score: (series - mean_n) / std_n.

    NaN where std is zero or insufficient data.
    """
    mu = rolling_mean(series, n)
    sigma = rolling_std(series, n)
    return (series - mu) / sigma.replace(0, np.nan)


def panel_indneutralize(
    values: pd.Series,
    groups: pd.Series,
    timestamps: pd.Series,
    min_group_size: int = 2,
) -> pd.Series:
    """Cross-sectional group demeaning within each timestamp.

    This is the reusable primitive for Alpha101-style IndNeutralize once an
    approved point-in-time crypto taxonomy is available. It does not load or
    infer groups; callers must pass already validated group membership.
    """
    if not (len(values) == len(groups) == len(timestamps)):
        raise ValueError("values, groups, and timestamps must have the same length")
    if min_group_size < 1:
        raise ValueError("min_group_size must be >= 1")

    frame = pd.DataFrame({
        "value": values,
        "group": groups,
        "timestamp": timestamps,
    }, index=values.index)
    valid = frame["value"].notna() & frame["group"].notna() & frame["timestamp"].notna()
    group_keys = [frame.loc[valid, "timestamp"], frame.loc[valid, "group"]]
    counts = frame.loc[valid, "value"].groupby(group_keys, sort=False).transform("count")
    means = frame.loc[valid, "value"].groupby(group_keys, sort=False).transform("mean")

    out = pd.Series(np.nan, index=values.index, dtype=float)
    neutralized = frame.loc[valid, "value"] - means
    neutralized = neutralized.where(counts >= min_group_size)
    out.loc[neutralized.index] = neutralized
    return out


# ── Math transforms ─────────────────────────────────────────────────

def sign(series: pd.Series) -> pd.Series:
    """Element-wise sign: -1, 0, or +1.

    Returns NaN where input is NaN.
    """
    return pd.Series(np.sign(series), index=series.index)


def where(cond: pd.Series, x: pd.Series, y: pd.Series | float) -> pd.Series:
    """Conditional element-wise selection.

    Returns x[i] where cond[i] is True, y[i] otherwise.
    NaN propagates: if cond is NaN, result is NaN.
    Supports scalar y (default value when cond is False/NaN).
    """
    return x.where(cond, y)


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
