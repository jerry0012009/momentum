"""Alpha101 Panel Operators — cross-sectional + time-series helpers for panel factors.

These operators work on *wide* DataFrames (index=timestamp, columns=symbols)
because Alpha101 factors require cross-sectional information at each timestamp.

Usage:
    from alpha101_panel_ops import (
        to_wide, from_wide, xs_zscore, xs_winsorize,
        ts_alpha_wide, rolling_mean_wide, rolling_min_wide, rolling_product_wide,
    )
"""
from __future__ import annotations

import numpy as np
import pandas as pd


# ── Pivot helpers ─────────────────────────────────────────────────────

def to_wide(df: pd.DataFrame, value_col: str) -> pd.DataFrame:
    """Pivot long-format bars to wide (index=timestamp, columns=symbol)."""
    return df.pivot_table(index="timestamp", columns="symbol", values=value_col)


def from_wide(wide: pd.DataFrame, factor_id: str) -> pd.DataFrame:
    """Melt wide factor values back to long format with [timestamp, symbol, factor_id]."""
    out = wide.stack().reset_index()
    out.columns = ["timestamp", "symbol", factor_id]
    return out.dropna(subset=[factor_id])


# ── Cross-sectional operators ─────────────────────────────────────────

def xs_zscore(wide: pd.DataFrame) -> pd.DataFrame:
    """Cross-sectional z-score at each timestamp.

    For each row (timestamp), compute (x - row_mean) / row_std.
    If row_std == 0, output 0 for that row.
    """
    row_mean = wide.mean(axis=1)
    row_std = wide.std(axis=1, ddof=0)
    # Avoid division by zero
    row_std = row_std.replace(0, np.nan)
    result = wide.sub(row_mean, axis=0).div(row_std, axis=0)
    return result.fillna(0.0)


def xs_winsorize(wide: pd.DataFrame, std: float = 4.0) -> pd.DataFrame:
    """Cross-sectional winsorization at each timestamp.

    Clip each symbol value to [row_mean - std * row_std, row_mean + std * row_std].
    Uses ddof=0 for row_std.
    """
    row_mean = wide.mean(axis=1)
    row_std = wide.std(axis=1, ddof=0)
    lower = row_mean - std * row_std
    upper = row_mean + std * row_std
    return wide.clip(lower=lower, upper=upper, axis=0)


# ── Time-series operators (wide format) ──────────────────────────────

def rolling_mean_wide(wide: pd.DataFrame, window: int) -> pd.DataFrame:
    """Rolling mean over time for each symbol column."""
    return wide.rolling(window=window, min_periods=window).mean()


def rolling_min_wide(wide: pd.DataFrame, window: int) -> pd.DataFrame:
    """Rolling min over time for each symbol column."""
    return wide.rolling(window=window, min_periods=window).min()


def rolling_product_wide(wide: pd.DataFrame, window: int) -> pd.DataFrame:
    """Rolling product over time for each symbol column.

    Preserves mathematical fidelity to Alpha101 ts_product.
    Uses cumprod/division for efficiency, with fallback for zeros.
    """
    result = wide.copy()
    for col in wide.columns:
        result[col] = _rolling_product_series(wide[col].values, window)
    return result


def _rolling_product_series(vals: np.ndarray, window: int) -> np.ndarray:
    """Rolling product for a single series using cumprod trick.

    For numerical stability, uses: prod(a[i-w+1:i+1]) = cumprod[i] / cumprod[i-w]
    Falls back to direct product when zeros are detected in window.
    """
    n = len(vals)
    out = np.full(n, np.nan)
    
    # Use log-cumsum for numerical stability when all values are positive
    # But since z-scores can be negative, use direct cumprod approach
    # with zero handling
    
    # Fast path: use pandas rolling apply with numpy prod
    # Convert to pandas Series for rolling
    s = pd.Series(vals)
    out_arr = s.rolling(window=window, min_periods=window).apply(np.prod, raw=True).values
    return out_arr


def ts_alpha_wide(y_wide: pd.DataFrame, x_wide: pd.DataFrame, window: int) -> pd.DataFrame:
    """Rolling regression intercept (alpha) for each symbol.

    For each symbol independently, over the rolling window:
        beta = cov(y, x) / var(x)
        alpha = mean(y) - beta * mean(x)
    If var(x) == 0, alpha = NaN.

    y_wide and x_wide may have different columns/index; aligned to intersection.
    """
    common_cols = y_wide.columns.intersection(x_wide.columns)
    common_idx = y_wide.index.intersection(x_wide.index)
    y_a = y_wide.loc[common_idx, common_cols]
    x_a = x_wide.loc[common_idx, common_cols]

    result = pd.DataFrame(np.nan, index=common_idx, columns=common_cols, dtype=float)
    for col in common_cols:
        y = y_a[col]
        x = x_a[col]
        result[col] = _rolling_alpha_vectorized(y.values, x.values, window)
    return result


def _rolling_alpha_vectorized(y: np.ndarray, x: np.ndarray, window: int) -> np.ndarray:
    """Vectorized rolling regression intercept using pandas rolling cov/var."""
    n = len(y)
    out = np.full(n, np.nan)
    
    y_s = pd.Series(y)
    x_s = pd.Series(x)
    
    # Rolling means
    y_mean = y_s.rolling(window=window, min_periods=window).mean()
    x_mean = x_s.rolling(window=window, min_periods=window).mean()
    
    # Rolling covariance and variance
    # cov(y,x) = E[(y - Ey)(x - Ex)] = rolling mean of (y - y_mean)(x - x_mean)
    # But we can use pandas rolling cov
    cov_yx = y_s.rolling(window=window, min_periods=window).cov(x_s)
    var_x = x_s.rolling(window=window, min_periods=window).var()
    
    # beta = cov(y,x) / var(x)
    beta = cov_yx / var_x
    
    # alpha = mean(y) - beta * mean(x)
    alpha = y_mean - beta * x_mean
    
    # Set to NaN where var(x) == 0
    alpha[var_x == 0] = np.nan
    
    return alpha.values


# ── Panel factor compute functions ────────────────────────────────────

def compute_a101_volume_xs_z_mean_neg_112h(bars: pd.DataFrame) -> pd.DataFrame:
    """-rolling_mean(xs_zscore(volume), 112).

    Low relative-volume / low crowding factor.
    """
    vol_wide = to_wide(bars, "volume")
    z = xs_zscore(vol_wide)
    mean_z = rolling_mean_wide(z, 112)
    result = -mean_z
    return from_wide(result, "a101_volume_xs_z_mean_neg_112h")


def compute_a101_vol_xs_z_product_112h(bars: pd.DataFrame) -> pd.DataFrame:
    """rolling_product(xs_zscore(volume), 112).

    Nonlinear persistent volume-regime detector.
    """
    vol_wide = to_wide(bars, "volume")
    z = xs_zscore(vol_wide)
    result = rolling_product_wide(z, 112)
    return from_wide(result, "a101_vol_xs_z_product_112h")


def compute_a101_volume_low_alpha_min_84_120(bars: pd.DataFrame) -> pd.DataFrame:
    """rolling_min(ts_alpha(volume, xs_winsorize(low), 84), 120).

    Volume-adjusted low-price / liquidity-stress state.
    """
    vol_wide = to_wide(bars, "volume")
    low_wide = to_wide(bars, "low")
    low_winsorized = xs_winsorize(low_wide)
    alpha = ts_alpha_wide(vol_wide, low_winsorized, 84)
    result = rolling_min_wide(alpha, 120)
    return from_wide(result, "a101_volume_low_alpha_min_84_120")


def compute_a101_volume_cap_alpha_min_80_80(bars: pd.DataFrame) -> pd.DataFrame:
    """rolling_min(ts_alpha(volume, cap, 80), 80).

    Volume-cap relation: recent low extreme of rolling intercept.
    Requires 'cap' column.
    """
    if "cap" not in bars.columns:
        raise ValueError("Column 'cap' not found in bars. Cannot compute a101_volume_cap_alpha_min_80_80.")
    vol_wide = to_wide(bars, "volume")
    cap_wide = to_wide(bars, "cap")
    alpha = ts_alpha_wide(vol_wide, cap_wide, 80)
    result = rolling_min_wide(alpha, 80)
    return from_wide(result, "a101_volume_cap_alpha_min_80_80")


def compute_a101_volume_cap_alpha_min_56_84(bars: pd.DataFrame) -> pd.DataFrame:
    """rolling_min(ts_alpha(volume, cap, 56), 84).

    Faster version of volume-cap relation factor.
    Requires 'cap' column.
    """
    if "cap" not in bars.columns:
        raise ValueError("Column 'cap' not found in bars. Cannot compute a101_volume_cap_alpha_min_56_84.")
    vol_wide = to_wide(bars, "volume")
    cap_wide = to_wide(bars, "cap")
    alpha = ts_alpha_wide(vol_wide, cap_wide, 56)
    result = rolling_min_wide(alpha, 84)
    return from_wide(result, "a101_volume_cap_alpha_min_56_84")


def compute_a101_volume_high_alpha_min_84_84(bars: pd.DataFrame) -> pd.DataFrame:
    """rolling_min(ts_alpha(volume, high, 84), 84).

    Volume-adjusted high-price compression / liquidity-price interaction.
    """
    vol_wide = to_wide(bars, "volume")
    high_wide = to_wide(bars, "high")
    alpha = ts_alpha_wide(vol_wide, high_wide, 84)
    result = rolling_min_wide(alpha, 84)
    return from_wide(result, "a101_volume_high_alpha_min_84_84")
