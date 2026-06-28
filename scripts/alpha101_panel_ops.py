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
from numpy.lib.stride_tricks import sliding_window_view


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


def xs_rank(wide: pd.DataFrame) -> pd.DataFrame:
    """Cross-sectional percentile rank at each timestamp."""
    return wide.rank(axis=1, pct=True, method="average")


def xs_scale(wide: pd.DataFrame) -> pd.DataFrame:
    """WorldQuant-style cross-sectional scale: x / sum(abs(x)) per timestamp."""
    denom = wide.abs().sum(axis=1).replace(0, np.nan)
    return wide.div(denom, axis=0)


# ── Time-series operators (wide format) ──────────────────────────────

def rolling_mean_wide(wide: pd.DataFrame, window: int) -> pd.DataFrame:
    """Rolling mean over time for each symbol column."""
    return wide.rolling(window=window, min_periods=window).mean()


def rolling_min_wide(wide: pd.DataFrame, window: int) -> pd.DataFrame:
    """Rolling min over time for each symbol column."""
    return wide.rolling(window=window, min_periods=window).min()


def rolling_max_wide(wide: pd.DataFrame, window: int) -> pd.DataFrame:
    """Rolling max over time for each symbol column."""
    return wide.rolling(window=window, min_periods=window).max()


def rolling_std_wide(wide: pd.DataFrame, window: int) -> pd.DataFrame:
    """Rolling sample standard deviation over time for each symbol column."""
    return wide.rolling(window=window, min_periods=window).std(ddof=1)


def rolling_idxmin_wide(wide: pd.DataFrame, window: int) -> pd.DataFrame:
    """Bars since the latest rolling minimum for each symbol column."""
    return wide.rolling(window=window, min_periods=window).apply(lambda x: int(np.nanargmin(x[::-1])), raw=True)


def rolling_idxmax_wide(wide: pd.DataFrame, window: int) -> pd.DataFrame:
    """Bars since the latest rolling maximum for each symbol column."""
    return wide.rolling(window=window, min_periods=window).apply(lambda x: int(np.nanargmax(x[::-1])), raw=True)


def rolling_product_wide(wide: pd.DataFrame, window: int) -> pd.DataFrame:
    """Rolling product over time for each symbol column.

    Preserves mathematical fidelity to Alpha101 ts_product.
    Uses cumprod/division for efficiency, with fallback for zeros.
    """
    result = wide.copy()
    for col in wide.columns:
        result[col] = _rolling_product_series(wide[col].values, window)
    return result


def rolling_corr_wide(x_wide: pd.DataFrame, y_wide: pd.DataFrame, window: int) -> pd.DataFrame:
    """Rolling Pearson correlation over time for aligned wide panels."""
    common_cols = x_wide.columns.intersection(y_wide.columns)
    common_idx = x_wide.index.intersection(y_wide.index)
    x_a = x_wide.loc[common_idx, common_cols]
    y_a = y_wide.loc[common_idx, common_cols]
    out = pd.DataFrame(np.nan, index=common_idx, columns=common_cols, dtype=float)
    for col in common_cols:
        out[col] = x_a[col].rolling(window=window, min_periods=window).corr(y_a[col])
    return out


def rolling_cov_wide(x_wide: pd.DataFrame, y_wide: pd.DataFrame, window: int) -> pd.DataFrame:
    """Rolling sample covariance over time for aligned wide panels."""
    common_cols = x_wide.columns.intersection(y_wide.columns)
    common_idx = x_wide.index.intersection(y_wide.index)
    x_a = x_wide.loc[common_idx, common_cols]
    y_a = y_wide.loc[common_idx, common_cols]
    out = pd.DataFrame(np.nan, index=common_idx, columns=common_cols, dtype=float)
    for col in common_cols:
        out[col] = x_a[col].rolling(window=window, min_periods=window).cov(y_a[col])
    return out


def rolling_sum_wide(wide: pd.DataFrame, window: int) -> pd.DataFrame:
    """Rolling sum over time for each symbol column."""
    return wide.rolling(window=window, min_periods=window).sum()


def decay_linear_wide(wide: pd.DataFrame, window: int) -> pd.DataFrame:
    """Linear-decay weighted moving average over time for each symbol column."""
    weights = np.arange(1, window + 1, dtype=float)
    weights = weights / weights.sum()
    result = pd.DataFrame(np.nan, index=wide.index, columns=wide.columns, dtype=float)
    for col in wide.columns:
        vals = wide[col].to_numpy(dtype=float, copy=False)
        if len(vals) < window:
            continue
        windows = sliding_window_view(vals, window_shape=window)
        valid = np.isfinite(windows).all(axis=1)
        out = np.full(len(vals), np.nan)
        dot = np.full(len(windows), np.nan)
        dot[valid] = windows[valid] @ weights
        out[window - 1:] = dot
        result[col] = out
    return result


def ts_rank_wide(wide: pd.DataFrame, window: int) -> pd.DataFrame:
    """Percentile rank of the latest value within each symbol's rolling window."""
    result = pd.DataFrame(np.nan, index=wide.index, columns=wide.columns, dtype=float)
    for col in wide.columns:
        vals = wide[col].to_numpy(dtype=float, copy=False)
        if len(vals) < window:
            continue
        windows = sliding_window_view(vals, window_shape=window)
        valid = np.isfinite(windows).all(axis=1)
        last = windows[:, -1]
        less = (windows < last[:, None]).sum(axis=1)
        equal = (windows == last[:, None]).sum(axis=1)
        ranks = (less + (equal + 1) / 2) / window
        out = np.full(len(vals), np.nan)
        out[window - 1:] = np.where(valid & np.isfinite(last), ranks, np.nan)
        result[col] = out
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


def _vwap_wide(bars: pd.DataFrame) -> pd.DataFrame:
    if "quote_volume" in bars.columns:
        work = bars.copy()
        work["_vwap"] = work["quote_volume"] / work["volume"].replace(0, np.nan)
        return to_wide(work, "_vwap")
    return to_wide(bars, "close")


def _min_wide(left: pd.DataFrame, right: pd.DataFrame) -> pd.DataFrame:
    """Elementwise minimum after aligning two wide panels."""
    left, right = left.align(right, join="inner", axis=None)
    result = left.where(left <= right, right)
    result[left.isna() | right.isna()] = np.nan
    return result


def _max_wide(left: pd.DataFrame, right: pd.DataFrame) -> pd.DataFrame:
    """Elementwise maximum after aligning two wide panels."""
    left, right = left.align(right, join="inner", axis=None)
    result = left.where(left >= right, right)
    result[left.isna() | right.isna()] = np.nan
    return result


def _signed_power_wide(base: pd.DataFrame, exponent: pd.DataFrame) -> pd.DataFrame:
    """WorldQuant signedpower(base, exponent) on aligned wide panels."""
    base, exponent = base.align(exponent, join="inner", axis=None)
    base_values = base.to_numpy(dtype=float)
    exponent_values = exponent.to_numpy(dtype=float)
    out = np.full(base_values.shape, np.nan, dtype=float)
    finite = np.isfinite(base_values) & np.isfinite(exponent_values)
    valid = finite & ((base_values != 0) | (exponent_values > 0))
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        out[valid] = np.sign(base_values[valid]) * np.power(np.abs(base_values[valid]), exponent_values[valid])
    return pd.DataFrame(out, index=base.index, columns=base.columns)


def compute_wq101_alpha32(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#32: scale(mean(close,7)-close) + 20*scale(corr(vwap,delay(close,5),230))."""
    close = to_wide(bars, "close")
    vwap = _vwap_wide(bars)
    part1 = xs_scale(rolling_mean_wide(close, 7) - close)
    part2 = 20 * xs_scale(rolling_corr_wide(vwap, close.shift(5), 230))
    return from_wide(part1 + part2, "wq101_alpha32")


def compute_wq101_alpha1(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#1: rank(ts_argmax(signedpower((returns<0?stddev(returns,20):close),2),5))-0.5."""
    close = to_wide(bars, "close")
    returns = close / close.shift(1) - 1.0
    volatility = rolling_std_wide(returns, 20)
    base = close.where(returns >= 0, volatility)
    powered = np.sign(base) * (base.abs() ** 2)
    result = xs_rank(rolling_idxmax_wide(powered, 5)) - 0.5
    return from_wide(result, "wq101_alpha1")


def compute_wq101_alpha2(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#2: -corr(rank(delta(log(volume),2)), rank((close-open)/open), 6)."""
    open_w = to_wide(bars, "open")
    close = to_wide(bars, "close")
    volume = to_wide(bars, "volume")
    log_volume = np.log(volume.replace(0, np.nan))
    vol_delta = log_volume - log_volume.shift(2)
    intrabar_return = (close - open_w) / open_w.replace(0, np.nan)
    result = -1 * rolling_corr_wide(xs_rank(vol_delta), xs_rank(intrabar_return), 6)
    return from_wide(result, "wq101_alpha2")


def compute_wq101_alpha3(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#3: -corr(rank(open), rank(volume), 10)."""
    open_w = to_wide(bars, "open")
    volume = to_wide(bars, "volume")
    return from_wide(-1 * rolling_corr_wide(xs_rank(open_w), xs_rank(volume), 10), "wq101_alpha3")


def compute_wq101_alpha4(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#4: -ts_rank(rank(low), 9)."""
    low = to_wide(bars, "low")
    return from_wide(-1 * ts_rank_wide(xs_rank(low), 9), "wq101_alpha4")


def compute_wq101_alpha5(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#5: rank(open-mean(vwap,10)) * -abs(rank(close-vwap))."""
    open_w = to_wide(bars, "open")
    close = to_wide(bars, "close")
    vwap = _vwap_wide(bars)
    result = xs_rank(open_w - rolling_sum_wide(vwap, 10) / 10) * (-1 * xs_rank(close - vwap).abs())
    return from_wide(result, "wq101_alpha5")


def compute_wq101_alpha7(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#7: if adv20<volume then -ts_rank(abs(delta(close,7)),60)*sign(delta(close,7)) else -1."""
    close = to_wide(bars, "close")
    volume = to_wide(bars, "volume")
    adv20 = rolling_mean_wide(volume, 20)
    close_delta = close - close.shift(7)
    active = adv20 < volume
    branch = -1 * ts_rank_wide(close_delta.abs(), 60) * np.sign(close_delta)
    result = pd.DataFrame(np.nan, index=close.index, columns=close.columns, dtype=float)
    result[active] = branch[active]
    result[~active & adv20.notna() & volume.notna()] = -1.0
    return from_wide(result, "wq101_alpha7")


def compute_wq101_alpha8(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#8: -rank(sum(open,5)*sum(returns,5)-delay(sum(open,5)*sum(returns,5),10))."""
    open_w = to_wide(bars, "open")
    close = to_wide(bars, "close")
    returns = close / close.shift(1) - 1.0
    raw = rolling_sum_wide(open_w, 5) * rolling_sum_wide(returns, 5)
    result = -1 * xs_rank(raw - raw.shift(10))
    return from_wide(result, "wq101_alpha8")


def compute_wq101_alpha10(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#10: rank(conditional signed close delta over four bars)."""
    close = to_wide(bars, "close")
    close_delta = close - close.shift(1)
    valid = rolling_min_wide(close_delta, 4).notna() & rolling_max_wide(close_delta, 4).notna()
    trend_agrees = (rolling_min_wide(close_delta, 4) > 0) | (rolling_max_wide(close_delta, 4) < 0)
    raw = pd.DataFrame(np.nan, index=close.index, columns=close.columns, dtype=float)
    raw[valid & trend_agrees] = close_delta[valid & trend_agrees]
    raw[valid & ~trend_agrees] = -close_delta[valid & ~trend_agrees]
    return from_wide(xs_rank(raw), "wq101_alpha10")


def compute_wq101_alpha11(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#11: (rank(ts_max(vwap-close,3))+rank(ts_min(vwap-close,3)))*rank(delta(volume,3))."""
    close = to_wide(bars, "close")
    volume = to_wide(bars, "volume")
    vwap = _vwap_wide(bars)
    spread = vwap - close
    result = (xs_rank(rolling_max_wide(spread, 3)) + xs_rank(rolling_min_wide(spread, 3))) * xs_rank(volume - volume.shift(3))
    return from_wide(result, "wq101_alpha11")


def compute_wq101_alpha13(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#13: -rank(covariance(rank(close), rank(volume), 5))."""
    close = to_wide(bars, "close")
    volume = to_wide(bars, "volume")
    result = -1 * xs_rank(rolling_cov_wide(xs_rank(close), xs_rank(volume), 5))
    return from_wide(result, "wq101_alpha13")


def compute_wq101_alpha14(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#14: -rank(delta(returns,3)) * corr(open, volume, 10)."""
    open_w = to_wide(bars, "open")
    close = to_wide(bars, "close")
    volume = to_wide(bars, "volume")
    returns = close / close.shift(1) - 1.0
    result = -1 * xs_rank(returns - returns.shift(3)) * rolling_corr_wide(open_w, volume, 10)
    return from_wide(result, "wq101_alpha14")


def compute_wq101_alpha15(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#15: -sum(rank(corr(rank(high), rank(volume), 3)), 3)."""
    high = to_wide(bars, "high")
    volume = to_wide(bars, "volume")
    corr = rolling_corr_wide(xs_rank(high), xs_rank(volume), 3)
    result = -1 * rolling_sum_wide(xs_rank(corr), 3)
    return from_wide(result, "wq101_alpha15")


def compute_wq101_alpha16(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#16: -rank(covariance(rank(high), rank(volume), 5))."""
    high = to_wide(bars, "high")
    volume = to_wide(bars, "volume")
    result = -1 * xs_rank(rolling_cov_wide(xs_rank(high), xs_rank(volume), 5))
    return from_wide(result, "wq101_alpha16")


def compute_wq101_alpha17(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#17: -rank(ts_rank(close,10)) * rank(delta(delta(close,1),1)) * rank(ts_rank(volume/adv20,5))."""
    close = to_wide(bars, "close")
    volume = to_wide(bars, "volume")
    close_delta = close - close.shift(1)
    adv20 = rolling_mean_wide(volume, 20)
    result = (
        -1
        * xs_rank(ts_rank_wide(close, 10))
        * xs_rank(close_delta - close_delta.shift(1))
        * xs_rank(ts_rank_wide(volume / adv20.replace(0, np.nan), 5))
    )
    return from_wide(result, "wq101_alpha17")


def compute_wq101_alpha18(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#18: -rank(stddev(abs(close-open),5)+(close-open)+corr(close,open,10))."""
    open_w = to_wide(bars, "open")
    close = to_wide(bars, "close")
    spread = close - open_w
    raw = rolling_std_wide(spread.abs(), 5) + spread + rolling_corr_wide(close, open_w, 10)
    return from_wide(-1 * xs_rank(raw), "wq101_alpha18")


def compute_wq101_alpha19(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#19: -sign((close-delay(close,7))+delta(close,7)) * (1+rank(1+sum(returns,250)))."""
    close = to_wide(bars, "close")
    returns = close / close.shift(1) - 1.0
    close_delta7 = close - close.shift(7)
    direction = -1 * np.sign(close_delta7 + close_delta7)
    result = direction * (1 + xs_rank(1 + rolling_sum_wide(returns, 250)))
    return from_wide(result, "wq101_alpha19")


def compute_wq101_alpha20(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#20: -rank(open-delay(high,1))*rank(open-delay(close,1))*rank(open-delay(low,1))."""
    open_w = to_wide(bars, "open")
    high = to_wide(bars, "high")
    low = to_wide(bars, "low")
    close = to_wide(bars, "close")
    result = -1 * xs_rank(open_w - high.shift(1)) * xs_rank(open_w - close.shift(1)) * xs_rank(open_w - low.shift(1))
    return from_wide(result, "wq101_alpha20")


def compute_wq101_alpha22(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#22: -delta(corr(high,volume,5),5) * rank(stddev(close,20))."""
    close = to_wide(bars, "close")
    high = to_wide(bars, "high")
    volume = to_wide(bars, "volume")
    corr = rolling_corr_wide(high, volume, 5)
    result = -1 * (corr - corr.shift(5)) * xs_rank(rolling_std_wide(close, 20))
    return from_wide(result, "wq101_alpha22")


def compute_wq101_alpha26(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#26: -ts_max(corr(ts_rank(volume,5), ts_rank(high,5), 5), 3)."""
    high = to_wide(bars, "high")
    volume = to_wide(bars, "volume")
    corr = rolling_corr_wide(ts_rank_wide(volume, 5), ts_rank_wide(high, 5), 5)
    result = -1 * rolling_max_wide(corr, 3)
    return from_wide(result, "wq101_alpha26")


def compute_wq101_alpha27(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#27: if rank(mean(corr(rank(volume),rank(vwap),6),2)) > 0.5 then -1 else 1."""
    volume = to_wide(bars, "volume")
    vwap = _vwap_wide(bars)
    raw = rolling_sum_wide(rolling_corr_wide(xs_rank(volume), xs_rank(vwap), 6), 2) / 2.0
    ranked = xs_rank(raw)
    result = pd.DataFrame(np.nan, index=ranked.index, columns=ranked.columns, dtype=float)
    result[ranked.notna() & (ranked > 0.5)] = -1.0
    result[ranked.notna() & (ranked <= 0.5)] = 1.0
    return from_wide(result, "wq101_alpha27")


def compute_wq101_alpha29(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#29: nested close-delta rank scale plus delayed negative return ts-rank."""
    close = to_wide(bars, "close")
    returns = close / close.shift(1) - 1.0
    close_delta5 = close - close.shift(5)
    ranked_delta = xs_rank(xs_rank(-1 * xs_rank(close_delta5)))
    scaled = xs_scale(np.log(rolling_min_wide(ranked_delta, 2).replace(0, np.nan)))
    left = rolling_min_wide(xs_rank(xs_rank(scaled)), 5)
    right = ts_rank_wide((-1 * returns).shift(6), 5)
    return from_wide(left + right, "wq101_alpha29")


def compute_wq101_alpha31(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#31: decayed close-delta rank plus short delta rank and ADV-low corr scale sign."""
    close = to_wide(bars, "close")
    low = to_wide(bars, "low")
    volume = to_wide(bars, "volume")
    close_delta10 = close - close.shift(10)
    rank1 = xs_rank(xs_rank(xs_rank(decay_linear_wide(-1 * xs_rank(xs_rank(close_delta10)), 10))))
    rank2 = xs_rank(-1 * (close - close.shift(3)))
    adv20 = rolling_mean_wide(volume, 20)
    corr_scale_sign = np.sign(xs_scale(rolling_corr_wide(adv20, low, 12)))
    return from_wide(rank1 + rank2 + corr_scale_sign, "wq101_alpha31")


def compute_wq101_alpha36(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#36: weighted blend of candle/volume correlation, return rank, VWAP/ADV corr, and mean-close state."""
    open_w = to_wide(bars, "open")
    close = to_wide(bars, "close")
    volume = to_wide(bars, "volume")
    vwap = _vwap_wide(bars)
    returns = close / close.shift(1) - 1.0
    adv20 = rolling_mean_wide(volume, 20)
    part1 = 2.21 * xs_rank(rolling_corr_wide(close - open_w, volume.shift(1), 15))
    part2 = 0.7 * xs_rank(open_w - close)
    part3 = 0.73 * xs_rank(ts_rank_wide((-1 * returns).shift(6), 5))
    part4 = xs_rank(rolling_corr_wide(vwap, adv20, 6).abs())
    part5 = 0.6 * xs_rank((rolling_sum_wide(close, 200) / 200 - open_w) * (close - open_w))
    return from_wide(part1 + part2 + part3 + part4 + part5, "wq101_alpha36")


def compute_wq101_alpha39(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#39: close delta gated by decayed relative volume rank and long return-sum rank."""
    close = to_wide(bars, "close")
    volume = to_wide(bars, "volume")
    returns = close / close.shift(1) - 1.0
    adv20 = rolling_mean_wide(volume, 20)
    rel_vol_decay = decay_linear_wide(volume / adv20.replace(0, np.nan), 9)
    left = -1 * xs_rank((close - close.shift(7)) * (1 - xs_rank(rel_vol_decay)))
    right = 1 + xs_rank(rolling_sum_wide(returns, 250))
    return from_wide(left * right, "wq101_alpha39")


def compute_wq101_alpha57(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#57: -(close-vwap) divided by decayed rank of close ts-argmax."""
    close = to_wide(bars, "close")
    vwap = _vwap_wide(bars)
    denom = decay_linear_wide(xs_rank(rolling_idxmax_wide(close, 30)), 2).replace(0, np.nan)
    return from_wide(-1 * (close - vwap) / denom, "wq101_alpha57")


def compute_wq101_alpha62(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#62: -1 gate comparing VWAP/ADV correlation rank with an OHLC rank condition."""
    open_w = to_wide(bars, "open")
    high = to_wide(bars, "high")
    low = to_wide(bars, "low")
    volume = to_wide(bars, "volume")
    vwap = _vwap_wide(bars)
    adv20 = rolling_mean_wide(volume, 20)
    left = xs_rank(rolling_corr_wide(vwap, rolling_sum_wide(adv20, 22), 10))
    rank_condition = ((xs_rank(open_w) + xs_rank(open_w)) < (xs_rank((high + low) / 2) + xs_rank(high))).astype(float)
    rank_condition[open_w.isna() | high.isna() | low.isna()] = np.nan
    right = xs_rank(rank_condition)
    left, right = left.align(right, join="inner", axis=None)
    result = -1 * (left < right).astype(float)
    result[left.isna() | right.isna()] = np.nan
    return from_wide(result, "wq101_alpha62")


def compute_wq101_alpha64(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#64: -1 gate comparing decayed open/low ADV correlation with blended mid/VWAP delta rank."""
    open_w = to_wide(bars, "open")
    high = to_wide(bars, "high")
    low = to_wide(bars, "low")
    volume = to_wide(bars, "volume")
    vwap = _vwap_wide(bars)
    adv120 = rolling_mean_wide(volume, 120)
    left_blend = open_w * 0.178404 + low * (1 - 0.178404)
    left = xs_rank(rolling_corr_wide(rolling_sum_wide(left_blend, 13), rolling_sum_wide(adv120, 13), 17))
    right_blend = ((high + low) / 2) * 0.178404 + vwap * (1 - 0.178404)
    right = xs_rank(right_blend - right_blend.shift(4))
    left, right = left.align(right, join="inner", axis=None)
    result = -1 * (left < right).astype(float)
    result[left.isna() | right.isna()] = np.nan
    return from_wide(result, "wq101_alpha64")


def compute_wq101_alpha66(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#66: negative sum of decayed VWAP-delta rank and decayed intrabar-location ts-rank."""
    open_w = to_wide(bars, "open")
    high = to_wide(bars, "high")
    low = to_wide(bars, "low")
    vwap = _vwap_wide(bars)
    left = xs_rank(decay_linear_wide(vwap - vwap.shift(4), 7))
    location = (low - vwap) / (open_w - ((high + low) / 2)).replace(0, np.nan)
    right = ts_rank_wide(decay_linear_wide(location, 11), 7)
    left, right = left.align(right, join="inner", axis=None)
    result = -1 * (left + right)
    result[left.isna() | right.isna()] = np.nan
    return from_wide(result, "wq101_alpha66")


def compute_wq101_alpha71(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#71: max of two decayed time-rank branches using close/ADV corr and low-open/VWAP rank."""
    open_w = to_wide(bars, "open")
    close = to_wide(bars, "close")
    low = to_wide(bars, "low")
    volume = to_wide(bars, "volume")
    vwap = _vwap_wide(bars)
    adv180 = rolling_mean_wide(volume, 180)
    left_corr = rolling_corr_wide(ts_rank_wide(close, 3), ts_rank_wide(adv180, 12), 18)
    left = ts_rank_wide(decay_linear_wide(left_corr, 4), 16)
    right = ts_rank_wide(decay_linear_wide(xs_rank((low + open_w) - (vwap + vwap)).pow(2), 16), 4)
    return from_wide(_max_wide(left, right), "wq101_alpha71")


def compute_wq101_alpha72(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#72: ratio of decayed mid/ADV correlation rank to decayed VWAP/volume ts-rank correlation rank."""
    high = to_wide(bars, "high")
    low = to_wide(bars, "low")
    volume = to_wide(bars, "volume")
    vwap = _vwap_wide(bars)
    adv40 = rolling_mean_wide(volume, 40)
    left = xs_rank(decay_linear_wide(rolling_corr_wide((high + low) / 2, adv40, 9), 10))
    right = xs_rank(decay_linear_wide(rolling_corr_wide(ts_rank_wide(vwap, 4), ts_rank_wide(volume, 19), 7), 3))
    left, right = left.align(right, join="inner", axis=None)
    result = left / right.replace(0, np.nan)
    result[left.isna() | right.isna()] = np.nan
    return from_wide(result, "wq101_alpha72")


def compute_wq101_alpha73(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#73: negative max of two decayed rank branches using VWAP and open/low blend."""
    open_w = to_wide(bars, "open")
    low = to_wide(bars, "low")
    vwap = _vwap_wide(bars)
    left = xs_rank(decay_linear_wide(vwap - vwap.shift(5), 3))
    blend = open_w * 0.147155 + low * (1 - 0.147155)
    right_raw = ((blend - blend.shift(2)) / blend.replace(0, np.nan)) * -1
    right = ts_rank_wide(decay_linear_wide(right_raw, 3), 17)
    return from_wide(-1 * _max_wide(left, right), "wq101_alpha73")


def compute_wq101_alpha81(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#81: -1 gate comparing ADV/VWAP ranked product with VWAP-volume rank correlation."""
    volume = to_wide(bars, "volume")
    vwap = _vwap_wide(bars)
    adv10 = rolling_mean_wide(volume, 10)
    left_corr = rolling_corr_wide(vwap, rolling_sum_wide(adv10, 50), 8)
    product_input = xs_rank(xs_rank(left_corr).pow(4))
    left = xs_rank(np.log(rolling_product_wide(product_input, 15).replace(0, np.nan)))
    right = xs_rank(rolling_corr_wide(xs_rank(vwap), xs_rank(volume), 5))
    left, right = left.align(right, join="inner", axis=None)
    result = -1 * (left < right).astype(float)
    result[left.isna() | right.isna()] = np.nan
    return from_wide(result, "wq101_alpha81")


def compute_wq101_alpha84(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#84: signedpower(ts_rank(vwap-ts_max(vwap,15),21), delta(close,5))."""
    close = to_wide(bars, "close")
    vwap = _vwap_wide(bars)
    base = ts_rank_wide(vwap - rolling_max_wide(vwap, 15), 21)
    exponent = close - close.shift(5)
    return from_wide(_signed_power_wide(base, exponent), "wq101_alpha84")


def compute_wq101_alpha98(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#98: decayed VWAP/ADV correlation rank minus decayed open/ADV argmin rank."""
    open_w = to_wide(bars, "open")
    volume = to_wide(bars, "volume")
    vwap = _vwap_wide(bars)
    adv5 = rolling_mean_wide(volume, 5)
    adv15 = rolling_mean_wide(volume, 15)
    left = xs_rank(decay_linear_wide(rolling_corr_wide(vwap, rolling_sum_wide(adv5, 26), 5), 7))
    right_corr = rolling_corr_wide(xs_rank(open_w), xs_rank(adv15), 21)
    right = xs_rank(decay_linear_wide(ts_rank_wide(rolling_idxmin_wide(right_corr, 9), 7), 8))
    left, right = left.align(right, join="inner", axis=None)
    result = left - right
    result[left.isna() | right.isna()] = np.nan
    return from_wide(result, "wq101_alpha98")


def compute_wq101_alpha33(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#33: rank(-1 * (1 - open / close))."""
    open_w = to_wide(bars, "open")
    close = to_wide(bars, "close")
    raw = -1 * (1 - (open_w / close.replace(0, np.nan)))
    return from_wide(xs_rank(raw), "wq101_alpha33")


def compute_wq101_alpha37(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#37: rank(corr(delay(open-close,1),close,200)) + rank(open-close)."""
    open_w = to_wide(bars, "open")
    close = to_wide(bars, "close")
    spread = open_w - close
    corr = rolling_corr_wide(spread.shift(1), close, 200)
    return from_wide(xs_rank(corr) + xs_rank(spread), "wq101_alpha37")


def compute_wq101_alpha38(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#38: -rank(ts_rank(close,10)) * rank(close/open)."""
    open_w = to_wide(bars, "open")
    close = to_wide(bars, "close")
    tsr = ts_rank_wide(close, 10)
    ratio = close / open_w.replace(0, np.nan)
    return from_wide(-1 * xs_rank(tsr) * xs_rank(ratio), "wq101_alpha38")


def compute_wq101_alpha44(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#44: -correlation(high, rank(volume), 5)."""
    high = to_wide(bars, "high")
    volume = to_wide(bars, "volume")
    return from_wide(-1 * rolling_corr_wide(high, xs_rank(volume), 5), "wq101_alpha44")


def compute_wq101_alpha45(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#45: -rank(mean(delay(close,5),20))*corr(close,volume,2)*rank(corr(sum(close,5),sum(close,20),2))."""
    close = to_wide(bars, "close")
    volume = to_wide(bars, "volume")
    delayed_mean = rolling_mean_wide(close.shift(5), 20)
    corr_cv = rolling_corr_wide(close, volume, 2)
    corr_sum = rolling_corr_wide(rolling_sum_wide(close, 5), rolling_sum_wide(close, 20), 2)
    result = -1 * xs_rank(delayed_mean) * corr_cv * xs_rank(corr_sum)
    return from_wide(result, "wq101_alpha45")


def compute_wq101_alpha34(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#34: rank((1-rank(std(ret,2)/std(ret,5))) + (1-rank(delta(close,1))))."""
    close = to_wide(bars, "close")
    returns = close / close.shift(1) - 1.0
    vol_ratio = rolling_std_wide(returns, 2) / rolling_std_wide(returns, 5).replace(0, np.nan)
    close_delta = close - close.shift(1)
    result = xs_rank((1 - xs_rank(vol_ratio)) + (1 - xs_rank(close_delta)))
    return from_wide(result, "wq101_alpha34")


def compute_wq101_alpha40(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#40: -rank(std(high,10)) * corr(high,volume,10)."""
    high = to_wide(bars, "high")
    volume = to_wide(bars, "volume")
    result = -1 * xs_rank(rolling_std_wide(high, 10)) * rolling_corr_wide(high, volume, 10)
    return from_wide(result, "wq101_alpha40")


def compute_wq101_alpha42(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#42: rank(vwap-close) / rank(vwap+close)."""
    close = to_wide(bars, "close")
    vwap = _vwap_wide(bars)
    result = xs_rank(vwap - close) / xs_rank(vwap + close).replace(0, np.nan)
    return from_wide(result, "wq101_alpha42")


def compute_wq101_alpha50(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#50: -ts_max(rank(corr(rank(volume),rank(vwap),5)),5)."""
    volume = to_wide(bars, "volume")
    vwap = _vwap_wide(bars)
    corr = rolling_corr_wide(xs_rank(volume), xs_rank(vwap), 5)
    result = -1 * rolling_max_wide(xs_rank(corr), 5)
    return from_wide(result, "wq101_alpha50")


def compute_wq101_alpha55(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#55: -corr(rank((close-ts_min(low,12))/(ts_max(high,12)-ts_min(low,12))),rank(volume),6)."""
    close = to_wide(bars, "close")
    high = to_wide(bars, "high")
    low = to_wide(bars, "low")
    volume = to_wide(bars, "volume")
    low_12 = rolling_min_wide(low, 12)
    denom = (rolling_max_wide(high, 12) - low_12).replace(0, np.nan)
    position = (close - low_12) / denom
    result = -1 * rolling_corr_wide(xs_rank(position), xs_rank(volume), 6)
    return from_wide(result, "wq101_alpha55")


def compute_wq101_alpha60(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#60: -((2*scale(rank(clv*volume)))-scale(rank(ts_argmax(close,10))))."""
    close = to_wide(bars, "close")
    high = to_wide(bars, "high")
    low = to_wide(bars, "low")
    volume = to_wide(bars, "volume")
    clv = ((close - low) - (high - close)) / (high - low).replace(0, np.nan)
    ranked_flow = xs_rank(clv * volume)
    argmax_close = close.rolling(window=10, min_periods=10).apply(lambda x: int(np.nanargmax(x[::-1])), raw=True)
    result = -1 * ((2 * xs_scale(ranked_flow)) - xs_scale(xs_rank(argmax_close)))
    return from_wide(result, "wq101_alpha60")


def compute_wq101_alpha25(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#25: rank((-returns * adv20 * vwap) * (high-close))."""
    close = to_wide(bars, "close")
    high = to_wide(bars, "high")
    volume = to_wide(bars, "volume")
    vwap = _vwap_wide(bars)
    returns = close / close.shift(1) - 1.0
    adv20 = rolling_mean_wide(volume, 20)
    result = xs_rank((-1 * returns * adv20 * vwap) * (high - close))
    return from_wide(result, "wq101_alpha25")


def compute_wq101_alpha28(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#28: scale(corr(adv20,low,5) + ((high+low)/2) - close)."""
    close = to_wide(bars, "close")
    high = to_wide(bars, "high")
    low = to_wide(bars, "low")
    volume = to_wide(bars, "volume")
    adv20 = rolling_mean_wide(volume, 20)
    result = xs_scale(rolling_corr_wide(adv20, low, 5) + ((high + low) / 2) - close)
    return from_wide(result, "wq101_alpha28")


def compute_wq101_alpha30(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#30: (((1-rank(sign(close_delta)+sign(delay(close_delta,1))+sign(delay(close_delta,2))))*sum(volume,5))/sum(volume,20))."""
    close = to_wide(bars, "close")
    volume = to_wide(bars, "volume")
    close_delta = close - close.shift(1)
    sign_sum = np.sign(close_delta) + np.sign(close_delta.shift(1)) + np.sign(close_delta.shift(2))
    result = ((1 - xs_rank(sign_sum)) * rolling_sum_wide(volume, 5)) / rolling_sum_wide(volume, 20).replace(0, np.nan)
    return from_wide(result, "wq101_alpha30")


def compute_wq101_alpha35(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#35: ts_rank(volume,32) * (1-ts_rank(close+high-low,16)) * (1-ts_rank(returns,32))."""
    close = to_wide(bars, "close")
    high = to_wide(bars, "high")
    low = to_wide(bars, "low")
    volume = to_wide(bars, "volume")
    returns = close / close.shift(1) - 1.0
    result = ts_rank_wide(volume, 32) * (1 - ts_rank_wide(close + high - low, 16)) * (1 - ts_rank_wide(returns, 32))
    return from_wide(result, "wq101_alpha35")


def compute_wq101_alpha43(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#43: ts_rank(volume/adv20,20) * ts_rank(-delta(close,7),8)."""
    close = to_wide(bars, "close")
    volume = to_wide(bars, "volume")
    adv20 = rolling_mean_wide(volume, 20)
    result = ts_rank_wide(volume / adv20.replace(0, np.nan), 20) * ts_rank_wide(-1 * (close - close.shift(7)), 8)
    return from_wide(result, "wq101_alpha43")


def compute_wq101_alpha52(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#52: -delta(ts_min(low,5),5) * rank((sum(returns,240)-sum(returns,20))/220) * ts_rank(volume,5)."""
    close = to_wide(bars, "close")
    low = to_wide(bars, "low")
    volume = to_wide(bars, "volume")
    returns = close / close.shift(1) - 1.0
    min_low_5 = rolling_min_wide(low, 5)
    ret_mean_gap = (rolling_sum_wide(returns, 240) - rolling_sum_wide(returns, 20)) / 220
    result = -1 * (min_low_5 - min_low_5.shift(5)) * xs_rank(ret_mean_gap) * ts_rank_wide(volume, 5)
    return from_wide(result, "wq101_alpha52")


def compute_wq101_alpha47(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#47: rank(1/close)*volume/adv20*high*rank(high-close)/(sum(high,5)/5)-rank(vwap-delay(vwap,5))."""
    close = to_wide(bars, "close")
    high = to_wide(bars, "high")
    volume = to_wide(bars, "volume")
    vwap = _vwap_wide(bars)
    adv20 = rolling_mean_wide(volume, 20)
    high_mean_5 = rolling_sum_wide(high, 5) / 5
    part1 = xs_rank(1 / close.replace(0, np.nan)) * (volume / adv20.replace(0, np.nan)) * high * xs_rank(high - close)
    result = (part1 / high_mean_5.replace(0, np.nan)) - xs_rank(vwap - vwap.shift(5))
    return from_wide(result, "wq101_alpha47")


def compute_wq101_alpha61(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#61: rank(vwap-ts_min(vwap,16)) < rank(corr(vwap,adv180,18))."""
    volume = to_wide(bars, "volume")
    vwap = _vwap_wide(bars)
    adv180 = rolling_mean_wide(volume, 180)
    part1 = xs_rank(vwap - rolling_min_wide(vwap, 16))
    part2 = xs_rank(rolling_corr_wide(vwap, adv180, 18))
    result = (part1 < part2).astype(float)
    result[part1.isna() | part2.isna()] = np.nan
    return from_wide(result, "wq101_alpha61")


def compute_wq101_alpha65(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#65: (rank(corr(open*0.00817205+vwap*0.99182795,sum(adv60,9),6)) < rank(open-ts_min(open,14))) * -1."""
    open_w = to_wide(bars, "open")
    volume = to_wide(bars, "volume")
    vwap = _vwap_wide(bars)
    adv60 = rolling_mean_wide(volume, 60)
    blended = open_w * 0.00817205 + vwap * (1 - 0.00817205)
    part1 = xs_rank(rolling_corr_wide(blended, rolling_sum_wide(adv60, 9), 6))
    part2 = xs_rank(open_w - rolling_min_wide(open_w, 14))
    result = -1 * (part1 < part2).astype(float)
    result[part1.isna() | part2.isna()] = np.nan
    return from_wide(result, "wq101_alpha65")


def compute_wq101_alpha68(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#68: (ts_rank(corr(rank(high),rank(adv15),9),14) < rank(delta(close*0.518371+low*0.481629,1))) * -1."""
    close = to_wide(bars, "close")
    high = to_wide(bars, "high")
    low = to_wide(bars, "low")
    volume = to_wide(bars, "volume")
    adv15 = rolling_mean_wide(volume, 15)
    part1 = ts_rank_wide(rolling_corr_wide(xs_rank(high), xs_rank(adv15), 9), 14)
    blended = close * 0.518371 + low * (1 - 0.518371)
    part2 = xs_rank(blended - blended.shift(1))
    result = -1 * (part1 < part2).astype(float)
    result[part1.isna() | part2.isna()] = np.nan
    return from_wide(result, "wq101_alpha68")


def compute_wq101_alpha74(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#74: (rank(corr(close,sum(adv30,37),15)) < rank(corr(rank(high*0.0261661+vwap*0.9738339),rank(volume),11))) * -1."""
    close = to_wide(bars, "close")
    high = to_wide(bars, "high")
    volume = to_wide(bars, "volume")
    vwap = _vwap_wide(bars)
    adv30 = rolling_mean_wide(volume, 30)
    blended = high * 0.0261661 + vwap * (1 - 0.0261661)
    part1 = xs_rank(rolling_corr_wide(close, rolling_sum_wide(adv30, 37), 15))
    part2 = xs_rank(rolling_corr_wide(xs_rank(blended), xs_rank(volume), 11))
    result = -1 * (part1 < part2).astype(float)
    result[part1.isna() | part2.isna()] = np.nan
    return from_wide(result, "wq101_alpha74")


def compute_wq101_alpha75(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#75: rank(corr(vwap,volume,4)) < rank(corr(rank(low),rank(adv50),12))."""
    low = to_wide(bars, "low")
    volume = to_wide(bars, "volume")
    vwap = _vwap_wide(bars)
    adv50 = rolling_mean_wide(volume, 50)
    left = xs_rank(rolling_corr_wide(vwap, volume, 4))
    right = xs_rank(rolling_corr_wide(xs_rank(low), xs_rank(adv50), 12))
    left, right = left.align(right, join="inner", axis=None)
    result = (left < right).astype(float)
    result[left.isna() | right.isna()] = np.nan
    return from_wide(result, "wq101_alpha75")


def compute_wq101_alpha77(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#77: min(rank(decay_linear(mid-vwap,20)), rank(decay_linear(corr(mid,adv40,3),6)))."""
    high = to_wide(bars, "high")
    low = to_wide(bars, "low")
    volume = to_wide(bars, "volume")
    vwap = _vwap_wide(bars)
    mid = (high + low) / 2
    adv40 = rolling_mean_wide(volume, 40)
    left = xs_rank(decay_linear_wide((((mid + high) - (vwap + high))), 20))
    right = xs_rank(decay_linear_wide(rolling_corr_wide(mid, adv40, 3), 6))
    return from_wide(_min_wide(left, right), "wq101_alpha77")


def compute_wq101_alpha78(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#78: rank(corr(sum(low/vwap blend,20),sum(adv40,20),7)) ^ rank(corr(rank(vwap),rank(volume),6))."""
    low = to_wide(bars, "low")
    volume = to_wide(bars, "volume")
    vwap = _vwap_wide(bars)
    adv40 = rolling_mean_wide(volume, 40)
    blended = low * 0.352233 + vwap * (1 - 0.352233)
    left = xs_rank(rolling_corr_wide(rolling_sum_wide(blended, 20), rolling_sum_wide(adv40, 20), 7))
    right = xs_rank(rolling_corr_wide(xs_rank(vwap), xs_rank(volume), 6))
    left, right = left.align(right, join="inner", axis=None)
    result = left.pow(right)
    result[left.isna() | right.isna()] = np.nan
    return from_wide(result, "wq101_alpha78")


def compute_wq101_alpha83(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#83: rank(delay(range/avg_close,2))*rank(rank(volume)) / ((range/avg_close)/(vwap-close))."""
    close = to_wide(bars, "close")
    high = to_wide(bars, "high")
    low = to_wide(bars, "low")
    volume = to_wide(bars, "volume")
    vwap = _vwap_wide(bars)
    range_scaled = (high - low) / (rolling_sum_wide(close, 5) / 5).replace(0, np.nan)
    denom = (range_scaled / (vwap - close).replace(0, np.nan)).replace(0, np.nan)
    result = (xs_rank(range_scaled.shift(2)) * xs_rank(xs_rank(volume))) / denom
    return from_wide(result, "wq101_alpha83")


def compute_wq101_alpha85(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#85: rank(corr(high/close blend,adv30,10)) ^ rank(corr(ts_rank(mid,4),ts_rank(volume,10),7))."""
    close = to_wide(bars, "close")
    high = to_wide(bars, "high")
    low = to_wide(bars, "low")
    volume = to_wide(bars, "volume")
    adv30 = rolling_mean_wide(volume, 30)
    blended = high * 0.876703 + close * (1 - 0.876703)
    left = xs_rank(rolling_corr_wide(blended, adv30, 10))
    right = xs_rank(rolling_corr_wide(ts_rank_wide((high + low) / 2, 4), ts_rank_wide(volume, 10), 7))
    left, right = left.align(right, join="inner", axis=None)
    result = left.pow(right)
    result[left.isna() | right.isna()] = np.nan
    return from_wide(result, "wq101_alpha85")


def compute_wq101_alpha86(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#86: -1 * (ts_rank(corr(close,sum(adv20,15),6),20) < rank(close-vwap))."""
    open_w = to_wide(bars, "open")
    close = to_wide(bars, "close")
    volume = to_wide(bars, "volume")
    vwap = _vwap_wide(bars)
    adv20 = rolling_mean_wide(volume, 20)
    left = ts_rank_wide(rolling_corr_wide(close, rolling_sum_wide(adv20, 15), 6), 20)
    right = xs_rank((open_w + close) - (vwap + open_w))
    left, right = left.align(right, join="inner", axis=None)
    result = -1 * (left < right).astype(float)
    result[left.isna() | right.isna()] = np.nan
    return from_wide(result, "wq101_alpha86")


def compute_wq101_alpha88(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#88: min(rank(decay_linear(rank(open)+rank(low)-rank(high)-rank(close),8)), ts_rank(decay_linear(corr(ts_rank(close,8),ts_rank(adv60,21),8),7),3))."""
    open_w = to_wide(bars, "open")
    close = to_wide(bars, "close")
    high = to_wide(bars, "high")
    low = to_wide(bars, "low")
    volume = to_wide(bars, "volume")
    adv60 = rolling_mean_wide(volume, 60)
    left_raw = (xs_rank(open_w) + xs_rank(low)) - (xs_rank(high) + xs_rank(close))
    left = xs_rank(decay_linear_wide(left_raw, 8))
    right_corr = rolling_corr_wide(ts_rank_wide(close, 8), ts_rank_wide(adv60, 21), 8)
    right = ts_rank_wide(decay_linear_wide(right_corr, 7), 3)
    return from_wide(_min_wide(left, right), "wq101_alpha88")


def compute_wq101_alpha92(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#92: min(ts_rank(decay_linear(mid+close < low+open,15),19), ts_rank(decay_linear(corr(rank(low),rank(adv30),8),7),7))."""
    open_w = to_wide(bars, "open")
    close = to_wide(bars, "close")
    high = to_wide(bars, "high")
    low = to_wide(bars, "low")
    volume = to_wide(bars, "volume")
    adv30 = rolling_mean_wide(volume, 30)
    condition = ((((high + low) / 2) + close) < (low + open_w)).astype(float)
    condition[open_w.isna() | close.isna() | high.isna() | low.isna()] = np.nan
    left = ts_rank_wide(decay_linear_wide(condition, 15), 19)
    right = ts_rank_wide(decay_linear_wide(rolling_corr_wide(xs_rank(low), xs_rank(adv30), 8), 7), 7)
    return from_wide(_min_wide(left, right), "wq101_alpha92")


def compute_wq101_alpha94(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#94: -rank(vwap-ts_min(vwap,12)) ^ ts_rank(corr(ts_rank(vwap,20),ts_rank(adv60,4),18),3)."""
    volume = to_wide(bars, "volume")
    vwap = _vwap_wide(bars)
    adv60 = rolling_mean_wide(volume, 60)
    left = xs_rank(vwap - rolling_min_wide(vwap, 12))
    right = ts_rank_wide(rolling_corr_wide(ts_rank_wide(vwap, 20), ts_rank_wide(adv60, 4), 18), 3)
    left, right = left.align(right, join="inner", axis=None)
    result = -1 * left.pow(right)
    result[left.isna() | right.isna()] = np.nan
    return from_wide(result, "wq101_alpha94")


def compute_wq101_alpha95(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#95: rank(open-ts_min(open,12)) < ts_rank(rank(corr(sum(mid,19),sum(adv40,19),13))^5,12)."""
    open_w = to_wide(bars, "open")
    high = to_wide(bars, "high")
    low = to_wide(bars, "low")
    volume = to_wide(bars, "volume")
    adv40 = rolling_mean_wide(volume, 40)
    mid = (high + low) / 2
    left = xs_rank(open_w - rolling_min_wide(open_w, 12))
    corr = rolling_corr_wide(rolling_sum_wide(mid, 19), rolling_sum_wide(adv40, 19), 13)
    right = ts_rank_wide(xs_rank(corr).pow(5), 12)
    left, right = left.align(right, join="inner", axis=None)
    result = (left < right).astype(float)
    result[left.isna() | right.isna()] = np.nan
    return from_wide(result, "wq101_alpha95")


def compute_wq101_alpha99(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#99: -1 * (rank(corr(sum(mid,20),sum(adv60,20),9)) < rank(corr(low,volume,6)))."""
    high = to_wide(bars, "high")
    low = to_wide(bars, "low")
    volume = to_wide(bars, "volume")
    adv60 = rolling_mean_wide(volume, 60)
    mid = (high + low) / 2
    left = xs_rank(rolling_corr_wide(rolling_sum_wide(mid, 20), rolling_sum_wide(adv60, 20), 9))
    right = xs_rank(rolling_corr_wide(low, volume, 6))
    left, right = left.align(right, join="inner", axis=None)
    result = -1 * (left < right).astype(float)
    result[left.isna() | right.isna()] = np.nan
    return from_wide(result, "wq101_alpha99")
