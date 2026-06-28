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


def rolling_sum_wide(wide: pd.DataFrame, window: int) -> pd.DataFrame:
    """Rolling sum over time for each symbol column."""
    return wide.rolling(window=window, min_periods=window).sum()


def ts_rank_wide(wide: pd.DataFrame, window: int) -> pd.DataFrame:
    """Percentile rank of the latest value within each symbol's rolling window."""
    def _rank_last_pct(x: np.ndarray) -> float:
        last = x[-1]
        if np.isnan(last):
            return np.nan
        valid = x[~np.isnan(x)]
        if len(valid) < window:
            return np.nan
        less = np.sum(valid < last)
        equal = np.sum(valid == last)
        return (less + (equal + 1) / 2) / len(valid)

    return wide.rolling(window=window, min_periods=window).apply(_rank_last_pct, raw=True)


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


def compute_wq101_alpha32(bars: pd.DataFrame) -> pd.DataFrame:
    """WQ101 Alpha#32: scale(mean(close,7)-close) + 20*scale(corr(vwap,delay(close,5),230))."""
    close = to_wide(bars, "close")
    vwap = _vwap_wide(bars)
    part1 = xs_scale(rolling_mean_wide(close, 7) - close)
    part2 = 20 * xs_scale(rolling_corr_wide(vwap, close.shift(5), 230))
    return from_wide(part1 + part2, "wq101_alpha32")


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
