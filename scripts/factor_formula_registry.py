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
    delay, delta, rolling_mean, rolling_std, rolling_max, rolling_min,
    rolling_quantile, rolling_corr, rolling_sum, rolling_skew, ts_rank,
    rolling_slope, rolling_rsquare, rolling_residual, rolling_idxmax,
    rolling_idxmin, zscore, ema, true_range, sign, where,
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


def _compute_q158_klen_open(df: pd.DataFrame) -> pd.Series:
    """Alpha158 KLEN: (high - low) / open."""
    o, h, l = df["open"], df["high"], df["low"]
    return (h - l) / o.replace(0, np.nan)


def _compute_q158_kmid_open(df: pd.DataFrame) -> pd.Series:
    """Alpha158 KMID: (close - open) / open."""
    o, c = df["open"], df["close"]
    return (c - o) / o.replace(0, np.nan)


def _compute_q158_kmid_range(df: pd.DataFrame) -> pd.Series:
    """Alpha158 KMID2: (close - open) / (high - low + eps)."""
    o, h, l, c = df["open"], df["high"], df["low"], df["close"]
    return (c - o) / (h - l + 1e-12)


def _compute_q158_kup_open(df: pd.DataFrame) -> pd.Series:
    """Alpha158 KUP: (high - max(open, close)) / open."""
    o, h, c = df["open"], df["high"], df["close"]
    return (h - pd.concat([o, c], axis=1).max(axis=1)) / o.replace(0, np.nan)


def _compute_q158_kup_range(df: pd.DataFrame) -> pd.Series:
    """Alpha158 KUP2: (high - max(open, close)) / (high - low + eps)."""
    o, h, l, c = df["open"], df["high"], df["low"], df["close"]
    return (h - pd.concat([o, c], axis=1).max(axis=1)) / (h - l + 1e-12)


def _compute_q158_klow_open(df: pd.DataFrame) -> pd.Series:
    """Alpha158 KLOW: (min(open, close) - low) / open."""
    o, l, c = df["open"], df["low"], df["close"]
    return (pd.concat([o, c], axis=1).min(axis=1) - l) / o.replace(0, np.nan)


def _compute_q158_klow_range(df: pd.DataFrame) -> pd.Series:
    """Alpha158 KLOW2: (min(open, close) - low) / (high - low + eps)."""
    o, h, l, c = df["open"], df["high"], df["low"], df["close"]
    return (pd.concat([o, c], axis=1).min(axis=1) - l) / (h - l + 1e-12)


def _compute_q158_ksft_open(df: pd.DataFrame) -> pd.Series:
    """Alpha158 KSFT: (2 * close - high - low) / open."""
    o, h, l, c = df["open"], df["high"], df["low"], df["close"]
    return (2 * c - h - l) / o.replace(0, np.nan)


def _compute_q158_ksft_range(df: pd.DataFrame) -> pd.Series:
    """Alpha158 KSFT2: (2 * close - high - low) / (high - low + eps)."""
    h, l, c = df["high"], df["low"], df["close"]
    return (2 * c - h - l) / (h - l + 1e-12)


def _compute_q158_rsv_20h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 RSV20: (close - LL20) / (HH20 - LL20 + eps)."""
    hh = rolling_max(df["high"], 20)
    ll = rolling_min(df["low"], 20)
    return (df["close"] - ll) / (hh - ll + 1e-12)


def _compute_q158_open_close_0h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 OPEN0: current open divided by current close."""
    return df["open"] / df["close"].replace(0, np.nan)


def _compute_q158_high_close_0h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 HIGH0: current high divided by current close."""
    return df["high"] / df["close"].replace(0, np.nan)


def _compute_q158_low_close_0h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 LOW0: current low divided by current close."""
    return df["low"] / df["close"].replace(0, np.nan)


def _compute_q158_open_close_1h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 OPEN1: previous open divided by current close."""
    return delay(df["open"], 1) / df["close"].replace(0, np.nan)


def _compute_q158_high_close_1h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 HIGH1: previous high divided by current close."""
    return delay(df["high"], 1) / df["close"].replace(0, np.nan)


def _compute_q158_low_close_1h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 LOW1: previous low divided by current close."""
    return delay(df["low"], 1) / df["close"].replace(0, np.nan)


def _compute_q158_open_close_2h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 OPEN2: open from two bars ago divided by current close."""
    return delay(df["open"], 2) / df["close"].replace(0, np.nan)


def _compute_q158_high_close_2h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 HIGH2: high from two bars ago divided by current close."""
    return delay(df["high"], 2) / df["close"].replace(0, np.nan)


def _compute_q158_low_close_2h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 LOW2: low from two bars ago divided by current close."""
    return delay(df["low"], 2) / df["close"].replace(0, np.nan)


def _compute_q158_open_close_3h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 OPEN3: open from three bars ago divided by current close."""
    return delay(df["open"], 3) / df["close"].replace(0, np.nan)


def _compute_q158_high_close_3h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 HIGH3: high from three bars ago divided by current close."""
    return delay(df["high"], 3) / df["close"].replace(0, np.nan)


def _compute_q158_low_close_3h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 LOW3: low from three bars ago divided by current close."""
    return delay(df["low"], 3) / df["close"].replace(0, np.nan)


def _compute_q158_open_close_4h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 OPEN4: open from four bars ago divided by current close."""
    return delay(df["open"], 4) / df["close"].replace(0, np.nan)


def _compute_q158_high_close_4h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 HIGH4: high from four bars ago divided by current close."""
    return delay(df["high"], 4) / df["close"].replace(0, np.nan)


def _compute_q158_low_close_4h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 LOW4: low from four bars ago divided by current close."""
    return delay(df["low"], 4) / df["close"].replace(0, np.nan)


def _compute_q158_close_close_4h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 CLOSE4: close from four bars ago divided by current close."""
    return delay(df["close"], 4) / df["close"].replace(0, np.nan)


def _compute_q158_volume_ratio_1h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 VOLUME1: previous volume divided by current volume."""
    return delay(df["volume"], 1) / (df["volume"] + 1e-12)


def _compute_q158_volume_ratio_2h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 VOLUME2: volume from two bars ago divided by current volume."""
    return delay(df["volume"], 2) / (df["volume"] + 1e-12)


def _compute_q158_volume_ratio_3h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 VOLUME3: volume from three bars ago divided by current volume."""
    return delay(df["volume"], 3) / (df["volume"] + 1e-12)


def _compute_q158_volume_ratio_4h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 VOLUME4: volume from four bars ago divided by current volume."""
    return delay(df["volume"], 4) / (df["volume"] + 1e-12)


def _compute_q158_qtlu_20h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 QTLU20: Quantile(close, 20, 0.8) / close."""
    c = df["close"]
    return rolling_quantile(c, 20, 0.8) / c.replace(0, np.nan)


def _compute_q158_qtld_20h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 QTLD20: Quantile(close, 20, 0.2) / close."""
    c = df["close"]
    return rolling_quantile(c, 20, 0.2) / c.replace(0, np.nan)


def _compute_q158_rank_close_20h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 RANK20: percentile rank of close within the past 20 bars."""
    return ts_rank(df["close"], 20)


def _compute_q158_cntp_20h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 CNTP20: fraction of the past 20 bars with close > previous close."""
    up = (df["close"] > delay(df["close"], 1)).astype(float)
    up = up.where(delay(df["close"], 1).notna(), np.nan)
    return rolling_mean(up, 20)


def _compute_q158_cntn_20h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 CNTN20: fraction of the past 20 bars with close < previous close."""
    down = (df["close"] < delay(df["close"], 1)).astype(float)
    down = down.where(delay(df["close"], 1).notna(), np.nan)
    return rolling_mean(down, 20)


def _compute_q158_sumd_20h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 SUMD20: (sum(up moves) - sum(down moves)) / sum(abs moves)."""
    d = delta(df["close"], 1)
    up = d.clip(lower=0)
    down = (-d).clip(lower=0)
    denom = rolling_sum(d.abs(), 20)
    return (rolling_sum(up, 20) - rolling_sum(down, 20)) / (denom + 1e-12)


def _compute_q158_beta_20h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 BETA20: Slope(close, 20) / close."""
    c = df["close"]
    return rolling_slope(c, 20) / c.replace(0, np.nan)


def _compute_q158_rsqr_20h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 RSQR20: R-squared of rolling close trend over 20 bars."""
    return rolling_rsquare(df["close"], 20)


def _compute_q158_resi_20h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 RESI20: latest residual from rolling close trend, normalized by close."""
    c = df["close"]
    return rolling_residual(c, 20) / c.replace(0, np.nan)


def _compute_q158_imax_20h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 IMAX20: bars since latest 20-bar high, divided by 20."""
    return rolling_idxmax(df["high"], 20) / 20.0


def _compute_q158_imin_20h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 IMIN20: bars since latest 20-bar low, divided by 20."""
    return rolling_idxmin(df["low"], 20) / 20.0


def _compute_q158_imxd_20h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 IMXD20: (IdxMax(high,20) - IdxMin(low,20)) / 20."""
    return (rolling_idxmax(df["high"], 20) - rolling_idxmin(df["low"], 20)) / 20.0


def _compute_q158_roc_20h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 ROC20: close 20 bars ago divided by current close."""
    c = df["close"]
    return delay(c, 20) / c.replace(0, np.nan)


def _compute_q158_ma_5h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 MA5: rolling mean close divided by current close."""
    c = df["close"]
    return rolling_mean(c, 5) / c.replace(0, np.nan)


def _compute_q158_std_5h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 STD5: rolling close standard deviation divided by current close."""
    c = df["close"]
    return rolling_std(c, 5) / c.replace(0, np.nan)


def _compute_q158_max_5h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 MAX5: rolling 5-bar high divided by current close."""
    c = df["close"]
    return rolling_max(df["high"], 5) / c.replace(0, np.nan)


def _compute_q158_min_5h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 MIN5: rolling 5-bar low divided by current close."""
    c = df["close"]
    return rolling_min(df["low"], 5) / c.replace(0, np.nan)


def _compute_q158_ma_10h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 MA10: rolling mean close divided by current close."""
    c = df["close"]
    return rolling_mean(c, 10) / c.replace(0, np.nan)


def _compute_q158_std_10h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 STD10: rolling close standard deviation divided by current close."""
    c = df["close"]
    return rolling_std(c, 10) / c.replace(0, np.nan)


def _compute_q158_max_10h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 MAX10: rolling 10-bar high divided by current close."""
    c = df["close"]
    return rolling_max(df["high"], 10) / c.replace(0, np.nan)


def _compute_q158_min_10h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 MIN10: rolling 10-bar low divided by current close."""
    c = df["close"]
    return rolling_min(df["low"], 10) / c.replace(0, np.nan)


def _compute_q158_ma_20h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 MA20: rolling mean close divided by current close."""
    c = df["close"]
    return rolling_mean(c, 20) / c.replace(0, np.nan)


def _compute_q158_std_20h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 STD20: rolling close standard deviation divided by current close."""
    c = df["close"]
    return rolling_std(c, 20) / c.replace(0, np.nan)


def _compute_q158_max_20h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 MAX20: rolling 20-bar high divided by current close."""
    c = df["close"]
    return rolling_max(df["high"], 20) / c.replace(0, np.nan)


def _compute_q158_min_20h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 MIN20: rolling 20-bar low divided by current close."""
    c = df["close"]
    return rolling_min(df["low"], 20) / c.replace(0, np.nan)


def _compute_q158_ma_30h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 MA30: rolling mean close divided by current close."""
    c = df["close"]
    return rolling_mean(c, 30) / c.replace(0, np.nan)


def _compute_q158_std_30h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 STD30: rolling close standard deviation divided by current close."""
    c = df["close"]
    return rolling_std(c, 30) / c.replace(0, np.nan)


def _compute_q158_max_30h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 MAX30: rolling 30-bar high divided by current close."""
    c = df["close"]
    return rolling_max(df["high"], 30) / c.replace(0, np.nan)


def _compute_q158_min_30h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 MIN30: rolling 30-bar low divided by current close."""
    c = df["close"]
    return rolling_min(df["low"], 30) / c.replace(0, np.nan)


def _compute_q158_ma_60h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 MA60: rolling mean close divided by current close."""
    c = df["close"]
    return rolling_mean(c, 60) / c.replace(0, np.nan)


def _compute_q158_std_60h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 STD60: rolling close standard deviation divided by current close."""
    c = df["close"]
    return rolling_std(c, 60) / c.replace(0, np.nan)


def _compute_q158_max_60h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 MAX60: rolling 60-bar high divided by current close."""
    c = df["close"]
    return rolling_max(df["high"], 60) / c.replace(0, np.nan)


def _compute_q158_min_60h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 MIN60: rolling 60-bar low divided by current close."""
    c = df["close"]
    return rolling_min(df["low"], 60) / c.replace(0, np.nan)


def _compute_q158_cntd_20h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 CNTD20: up-close fraction minus down-close fraction over 20 bars."""
    prev_close = delay(df["close"], 1)
    up = (df["close"] > prev_close).astype(float).where(prev_close.notna(), np.nan)
    down = (df["close"] < prev_close).astype(float).where(prev_close.notna(), np.nan)
    return rolling_mean(up, 20) - rolling_mean(down, 20)


def _compute_q158_corr_20h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 CORR20: corr(close, log(volume + 1), 20)."""
    log_volume = np.log(df["volume"].clip(lower=0) + 1.0)
    return rolling_corr(df["close"], log_volume, 20)


def _compute_q158_cord_20h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 CORD20: corr(close/Ref(close,1), log(volume/Ref(volume,1)+1), 20)."""
    close_ratio = df["close"] / delay(df["close"], 1).replace(0, np.nan)
    volume_ratio = df["volume"] / delay(df["volume"], 1).replace(0, np.nan)
    return rolling_corr(close_ratio, np.log(volume_ratio + 1.0), 20)


def _compute_q158_sump_20h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 SUMP20: total positive close move divided by total absolute close move."""
    d = delta(df["close"], 1)
    gain = d.clip(lower=0)
    denom = rolling_sum(d.abs(), 20)
    return rolling_sum(gain, 20) / (denom + 1e-12)


def _compute_q158_sumn_20h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 SUMN20: total negative close move divided by total absolute close move."""
    d = delta(df["close"], 1)
    loss = (-d).clip(lower=0)
    denom = rolling_sum(d.abs(), 20)
    return rolling_sum(loss, 20) / (denom + 1e-12)


def _compute_q158_vma_20h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 VMA20: rolling mean volume divided by current volume."""
    v = df["volume"]
    return rolling_mean(v, 20) / (v + 1e-12)


def _compute_q158_vstd_20h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 VSTD20: rolling volume standard deviation divided by current volume."""
    v = df["volume"]
    return rolling_std(v, 20) / (v + 1e-12)


def _compute_q158_wvma_20h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 WVMA20: std(abs(close/ref(close,1)-1)*volume,20) divided by its mean."""
    close_ratio = df["close"] / delay(df["close"], 1).replace(0, np.nan) - 1.0
    weighted_abs_ret = close_ratio.abs() * df["volume"]
    return rolling_std(weighted_abs_ret, 20) / (rolling_mean(weighted_abs_ret, 20) + 1e-12)


def _compute_q158_vsump_20h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 VSUMP20: positive volume change share of total absolute volume change."""
    d = delta(df["volume"], 1)
    gain = d.clip(lower=0)
    denom = rolling_sum(d.abs(), 20)
    return rolling_sum(gain, 20) / (denom + 1e-12)


def _compute_q158_vsumn_20h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 VSUMN20: negative volume change share of total absolute volume change."""
    d = delta(df["volume"], 1)
    loss = (-d).clip(lower=0)
    denom = rolling_sum(d.abs(), 20)
    return rolling_sum(loss, 20) / (denom + 1e-12)


def _compute_q158_vsumd_20h(df: pd.DataFrame) -> pd.Series:
    """Alpha158 VSUMD20: signed volume change dominance over total absolute volume change."""
    d = delta(df["volume"], 1)
    gain = d.clip(lower=0)
    loss = (-d).clip(lower=0)
    denom = rolling_sum(d.abs(), 20)
    return (rolling_sum(gain, 20) - rolling_sum(loss, 20)) / (denom + 1e-12)


# ── PM-09: Alpha158-Inspired Batch 1 ──────────────────────────────

def _compute_vwap_dev_20h(df: pd.DataFrame) -> pd.Series:
    """VWAP Deviation 20h: (close - vwap_20h) / vwap_20h."""
    c, v = df["close"], df["volume"]
    vwap = rolling_sum(c * v, 20) / rolling_sum(v, 20).replace(0, np.nan)
    return (c - vwap) / vwap.replace(0, np.nan)


def _compute_wvma_20h(df: pd.DataFrame) -> pd.Series:
    """Volume-Weighted Volatility 20h: std(ret*vol, 20) / mean(vol, 20)."""
    ret = df["close"].pct_change()
    v = df["volume"]
    numer = rolling_std(ret * v, 20)
    denom = rolling_mean(v, 20).replace(0, np.nan)
    return numer / denom


def _compute_vol_ret_corr_20h(df: pd.DataFrame) -> pd.Series:
    """Volume-Return Correlation 20h: corr(ret, delta(volume,1), 20)."""
    ret = df["close"].pct_change()
    vol_chg = delta(df["volume"], 1)
    return rolling_corr(ret, vol_chg, 20)


def _compute_intraday_ret(df: pd.DataFrame) -> pd.Series:
    """Intraday Return (1h bar): (close - open) / open."""
    o, c = df["open"], df["close"]
    return (c - o) / o.replace(0, np.nan)


def _compute_klow_close(df: pd.DataFrame) -> pd.Series:
    """Lower Wick / Close: (min(open, close) - low) / close."""
    o, l, c = df["open"], df["low"], df["close"]
    return (np.minimum(o, c) - l) / c.replace(0, np.nan)


def _compute_ksft_5h(df: pd.DataFrame) -> pd.Series:
    """Short-Window Skewness 5h: rolling skewness of 1h returns over 5 bars."""
    ret = df["close"].pct_change()
    return rolling_skew(ret, 5)


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


# ── Phase 7B: Momentum ────────────────────────────────────────────

def _compute_mom_5h(df: pd.DataFrame) -> pd.Series:
    """Momentum 5h: close / close_5h_ago - 1."""
    return df["close"] / delay(df["close"], 5) - 1.0


def _compute_mom_10h(df: pd.DataFrame) -> pd.Series:
    """Momentum 10h: close / close_10h_ago - 1."""
    return df["close"] / delay(df["close"], 10) - 1.0


def _compute_mom_40h(df: pd.DataFrame) -> pd.Series:
    """Momentum 40h: close / close_40h_ago - 1."""
    return df["close"] / delay(df["close"], 40) - 1.0


# ── Phase 7B: Reversal ────────────────────────────────────────────

def _compute_rev_3h(df: pd.DataFrame) -> pd.Series:
    """Reversal 3h: -(close / close_3h_ago - 1)."""
    return -(df["close"] / delay(df["close"], 3) - 1.0)


def _compute_rev_10h(df: pd.DataFrame) -> pd.Series:
    """Reversal 10h: -(close / close_10h_ago - 1)."""
    return -(df["close"] / delay(df["close"], 10) - 1.0)


def _compute_rev_24h(df: pd.DataFrame) -> pd.Series:
    """Reversal 24h: -(close / close_24h_ago - 1)."""
    return -(df["close"] / delay(df["close"], 24) - 1.0)


# ── Phase 7B: Volatility ──────────────────────────────────────────

def _compute_vol_5h(df: pd.DataFrame) -> pd.Series:
    """Volatility 5h: rolling std of returns over 5 bars."""
    ret = df["close"].pct_change()
    return rolling_std(ret, 5)


def _compute_vol_40h(df: pd.DataFrame) -> pd.Series:
    """Volatility 40h: rolling std of returns over 40 bars."""
    ret = df["close"].pct_change()
    return rolling_std(ret, 40)


def _compute_vol_ratio_5_20(df: pd.DataFrame) -> pd.Series:
    """Vol ratio: std(ret,5) / std(ret,20)."""
    ret = df["close"].pct_change()
    s5 = rolling_std(ret, 5)
    s20 = rolling_std(ret, 20)
    return s5 / s20.replace(0, np.nan)


# ── Phase 7B: Range Position ──────────────────────────────────────

def _compute_range_1h(df: pd.DataFrame) -> pd.Series:
    """Range 1h: (high - low) / close."""
    h, l, c = df["high"], df["low"], df["close"]
    return (h - l) / c.replace(0, np.nan)


def _compute_range_4h(df: pd.DataFrame) -> pd.Series:
    """Range 4h: (HH4 - LL4) / close."""
    hh = rolling_max(df["high"], 4)
    ll = rolling_min(df["low"], 4)
    return (hh - ll) / df["close"].replace(0, np.nan)


def _compute_range_24h(df: pd.DataFrame) -> pd.Series:
    """Range 24h: (HH24 - LL24) / close."""
    hh = rolling_max(df["high"], 24)
    ll = rolling_min(df["low"], 24)
    return (hh - ll) / df["close"].replace(0, np.nan)


# ── Phase 7B: Price Position ──────────────────────────────────────

def _compute_price_pos_24h(df: pd.DataFrame) -> pd.Series:
    """Price position 24h: (close - LL24) / (HH24 - LL24 + eps)."""
    hh = rolling_max(df["high"], 24)
    ll = rolling_min(df["low"], 24)
    return (df["close"] - ll) / (hh - ll + 1e-8)


def _compute_price_pos_72h(df: pd.DataFrame) -> pd.Series:
    """Price position 72h: (close - LL72) / (HH72 - LL72 + eps)."""
    hh = rolling_max(df["high"], 72)
    ll = rolling_min(df["low"], 72)
    return (df["close"] - ll) / (hh - ll + 1e-8)


# ── Phase 7B: Volume / Quote Volume Zscore ────────────────────────

def _compute_vol_zscore_20h(df: pd.DataFrame) -> pd.Series:
    """Volume z-score 20h: (volume - SMA20) / STD20."""
    return zscore(df["volume"], 20)


def _compute_vol_zscore_48h(df: pd.DataFrame) -> pd.Series:
    """Volume z-score 48h: (volume - SMA48) / STD48."""
    return zscore(df["volume"], 48)


def _compute_qvol_zscore_20h(df: pd.DataFrame) -> pd.Series:
    """Quote volume z-score 20h: (quote_volume - SMA20) / STD20."""
    return zscore(df["quote_volume"], 20)


def _compute_qvol_zscore_48h(df: pd.DataFrame) -> pd.Series:
    """Quote volume z-score 48h: (quote_volume - SMA48) / STD48."""
    return zscore(df["quote_volume"], 48)


# ── Phase 7B: Trend MA Gap ────────────────────────────────────────

def _compute_ma_gap_5_20(df: pd.DataFrame) -> pd.Series:
    """MA gap 5/20: (SMA5 - SMA20) / SMA20."""
    sma5 = rolling_mean(df["close"], 5)
    sma20 = rolling_mean(df["close"], 20)
    return (sma5 - sma20) / sma20.replace(0, np.nan)


def _compute_ma_gap_10_40(df: pd.DataFrame) -> pd.Series:
    """MA gap 10/40: (SMA10 - SMA40) / SMA40."""
    sma10 = rolling_mean(df["close"], 10)
    sma40 = rolling_mean(df["close"], 40)
    return (sma10 - sma40) / sma40.replace(0, np.nan)


# ── Phase 7B: Breakout Distance ───────────────────────────────────

def _compute_breakout_dist_20h(df: pd.DataFrame) -> pd.Series:
    """Breakout distance 20h: (close - HH20) / (HH20 - LL20 + eps)."""
    hh = rolling_max(df["high"], 20)
    ll = rolling_min(df["low"], 20)
    return (df["close"] - hh) / (hh - ll + 1e-8)


def _compute_breakout_dist_48h(df: pd.DataFrame) -> pd.Series:
    """Breakout distance 48h: (close - HH48) / (HH48 - LL48 + eps)."""
    hh = rolling_max(df["high"], 48)
    ll = rolling_min(df["low"], 48)
    return (df["close"] - hh) / (hh - ll + 1e-8)


# ── Phase 7B: Intraday Candle ─────────────────────────────────────

def _compute_candle_body(df: pd.DataFrame) -> pd.Series:
    """Candle body: (close - open) / (high - low + eps)."""
    o, h, l, c = df["open"], df["high"], df["low"], df["close"]
    return (c - o) / (h - l + 1e-8)


def _compute_candle_wick_upper(df: pd.DataFrame) -> pd.Series:
    """Upper wick: (high - max(open, close)) / (high - low + eps)."""
    o, h, l, c = df["open"], df["high"], df["low"], df["close"]
    return (h - pd.concat([o, c], axis=1).max(axis=1)) / (h - l + 1e-8)


def _compute_candle_wick_lower(df: pd.DataFrame) -> pd.Series:
    """Lower wick: (min(open, close) - low) / (high - low + eps)."""
    o, h, l, c = df["open"], df["high"], df["low"], df["close"]
    return (pd.concat([o, c], axis=1).min(axis=1) - l) / (h - l + 1e-8)


# ── Phase 7B: Cross-Sectional Rank (per-symbol prep) ─────────────
# These compute the per-symbol metric. Cross-sectional ranking is
# done at the caller level (build_factor_values.py) after combining
# all symbols into one DataFrame and grouping by timestamp.

def _compute_xs_rank_ret_1h_prep(df: pd.DataFrame) -> pd.Series:
    """1h return for cross-sectional ranking."""
    return df["close"].pct_change()


def _compute_xs_rank_vol_prep(df: pd.DataFrame) -> pd.Series:
    """20h rolling mean volume for cross-sectional ranking."""
    return rolling_mean(df["volume"], 20)


# ── Phase 7I-A: Batch-2 Technical Indicators ─────────────────────

def _compute_ema_12_26_gap(df: pd.DataFrame) -> pd.Series:
    """EMA gap 12/26: (EMA12 - EMA26) / EMA26."""
    ema12 = ema(df["close"], 12)
    ema26 = ema(df["close"], 26)
    return (ema12 - ema26) / ema26.replace(0, np.nan)


def _compute_rsi_7h(df: pd.DataFrame) -> pd.Series:
    """RSI 7h: Wilder RSI with lookback=7."""
    d = df["close"].diff()
    up = d.clip(lower=0)
    down = -d.clip(upper=0)
    avg_up = up.ewm(alpha=1 / 7, adjust=False, min_periods=7).mean()
    avg_down = down.ewm(alpha=1 / 7, adjust=False, min_periods=7).mean()
    rs = avg_up / avg_down.replace(0, np.nan)
    out = 100 - 100 / (1 + rs)
    out = out.where(avg_down != 0, 100.0)
    out = out.where(avg_up != 0, 0.0)
    return out


def _compute_rsi_28h(df: pd.DataFrame) -> pd.Series:
    """RSI 28h: Wilder RSI with lookback=28."""
    d = df["close"].diff()
    up = d.clip(lower=0)
    down = -d.clip(upper=0)
    avg_up = up.ewm(alpha=1 / 28, adjust=False, min_periods=28).mean()
    avg_down = down.ewm(alpha=1 / 28, adjust=False, min_periods=28).mean()
    rs = avg_up / avg_down.replace(0, np.nan)
    out = 100 - 100 / (1 + rs)
    out = out.where(avg_down != 0, 100.0)
    out = out.where(avg_up != 0, 0.0)
    return out


def _compute_williams_r_14h(df: pd.DataFrame) -> pd.Series:
    """Williams %R 14h: (HH14 - close) / (HH14 - LL14 + eps), 0-1 scale."""
    hh = rolling_max(df["high"], 14)
    ll = rolling_min(df["low"], 14)
    return (hh - df["close"]) / (hh - ll + 1e-8)


# ── Phase 7I-A: Batch-2 Realized Skew/Kurtosis ──────────────────

def _compute_downside_vol_20h(df: pd.DataFrame) -> pd.Series:
    """Downside volatility 20h: std of negative 1h returns only."""
    ret = df["close"].pct_change()
    neg_ret = ret.clip(upper=0)
    return rolling_std(neg_ret, 20)


def _compute_vol_of_vol_20h(df: pd.DataFrame) -> pd.Series:
    """Vol-of-vol 20h: std of 5h rolling volatility over 20 bars."""
    ret = df["close"].pct_change()
    vol_5h = rolling_std(ret, 5)
    return rolling_std(vol_5h, 20)


# ── Phase 7I-A: Batch-2 Momentum / Trend / Volume ────────────────

def _compute_mom_accel_20h(df: pd.DataFrame) -> pd.Series:
    """Momentum acceleration 20h: mom_20h - delay(mom_20h, 5)."""
    mom_20h = df["close"] / delay(df["close"], 20) - 1.0
    return mom_20h - delay(mom_20h, 5)


def _compute_qvol_ma_ratio_5_20(df: pd.DataFrame) -> pd.Series:
    """Quote-volume MA ratio 5/20: SMA(qvol,5) / SMA(qvol,20) - 1."""
    sma5 = rolling_mean(df["quote_volume"], 5)
    sma20 = rolling_mean(df["quote_volume"], 20)
    return sma5 / sma20.replace(0, np.nan) - 1.0


def _compute_ma_gap_20_80(df: pd.DataFrame) -> pd.Series:
    """MA gap 20/80: (SMA20 - SMA80) / SMA80."""
    sma20 = rolling_mean(df["close"], 20)
    sma80 = rolling_mean(df["close"], 80)
    return (sma20 - sma80) / sma80.replace(0, np.nan)


# ── Phase 7M-A: Crypto-native (taker + funding) ────────────────────

def _compute_taker_buy_ratio_20h(df: pd.DataFrame) -> pd.Series:
    """Taker buy ratio 20h: rolling_mean(taker_buy_quote_volume / quote_volume, 20)."""
    ratio = df["taker_buy_quote_volume"] / df["quote_volume"].replace(0, np.nan)
    return rolling_mean(ratio, 20)


def _compute_taker_buy_zscore_20h(df: pd.DataFrame) -> pd.Series:
    """Taker buy z-score 20h: zscore(taker_buy_quote_volume / quote_volume, 20)."""
    ratio = df["taker_buy_quote_volume"] / df["quote_volume"].replace(0, np.nan)
    return zscore(ratio, 20)


def _compute_taker_buy_delta_5h(df: pd.DataFrame) -> pd.Series:
    """Taker buy delta 5h: ratio - delay(ratio, 5)."""
    ratio = df["taker_buy_quote_volume"] / df["quote_volume"].replace(0, np.nan)
    return ratio - delay(ratio, 5)


def _compute_funding_rate_level_20h(df: pd.DataFrame) -> pd.Series:
    """Funding rate level 20h: rolling_mean(funding_rate, 20)."""
    return rolling_mean(df["funding_rate"], 20)


def _compute_funding_rate_zscore_80h(df: pd.DataFrame) -> pd.Series:
    """Funding rate z-score 80h: zscore(funding_rate, 80)."""
    return zscore(df["funding_rate"], 80)


def _compute_funding_rate_change_24h(df: pd.DataFrame) -> pd.Series:
    """Funding rate change 24h: funding_rate - delay(funding_rate, 24)."""
    return df["funding_rate"] - delay(df["funding_rate"], 24)


# ── Phase 13A-P2: Sprint 1 Diagnostic Factors ────────────────────

def _compute_mom_72h(df: pd.DataFrame) -> pd.Series:
    """Momentum 72h: close / close_72h_ago - 1."""
    return df["close"] / delay(df["close"], 72) - 1.0


def _compute_mom_120h(df: pd.DataFrame) -> pd.Series:
    """Momentum 120h: close / close_120h_ago - 1."""
    return df["close"] / delay(df["close"], 120) - 1.0


def _compute_rev_1h(df: pd.DataFrame) -> pd.Series:
    """Reversal 1h: -(close / close_1h_ago - 1)."""
    return -(df["close"] / delay(df["close"], 1) - 1.0)


def _compute_rev_72h(df: pd.DataFrame) -> pd.Series:
    """Reversal 72h: -(close / close_72h_ago - 1)."""
    return -(df["close"] / delay(df["close"], 72) - 1.0)


def _compute_vol_ratio_20_80(df: pd.DataFrame) -> pd.Series:
    """Vol ratio 20/80: std(ret,20) / std(ret,80)."""
    ret = df["close"].pct_change()
    s20 = rolling_std(ret, 20)
    s80 = rolling_std(ret, 80)
    return s20 / s80.replace(0, np.nan)


def _compute_realized_skew_20h(df: pd.DataFrame) -> pd.Series:
    """Realized skewness 20h: rolling skewness of 1h returns over 20 bars."""
    ret = df["close"].pct_change()
    return ret.rolling(20, min_periods=20).skew()


def _compute_realized_kurt_20h(df: pd.DataFrame) -> pd.Series:
    """Realized kurtosis 20h: rolling kurtosis of 1h returns over 20 bars."""
    ret = df["close"].pct_change()
    return ret.rolling(20, min_periods=20).kurt()


def _compute_amihud_illiquidity_20h(df: pd.DataFrame) -> pd.Series:
    """Amihud illiquidity 20h: rolling mean(abs(ret) / quote_volume, 20)."""
    ret = df["close"].pct_change().abs()
    qvol = df["quote_volume"].replace(0, np.nan)
    illiq = ret / qvol
    return rolling_mean(illiq, 20)


def _compute_qvol_ma_ratio_20_80(df: pd.DataFrame) -> pd.Series:
    """Quote-volume MA ratio 20/80: SMA(qvol,20) / SMA(qvol,80) - 1."""
    sma20 = rolling_mean(df["quote_volume"], 20)
    sma80 = rolling_mean(df["quote_volume"], 80)
    return sma20 / sma80.replace(0, np.nan) - 1.0


def _compute_price_volume_corr_20h(df: pd.DataFrame) -> pd.Series:
    """Price-volume correlation 20h: rolling corr(ret, pct_change(qvol), 20)."""
    ret = df["close"].pct_change()
    qvol_pct = df["quote_volume"].pct_change()
    return rolling_corr(ret, qvol_pct, 20)


def _compute_trend_efficiency_24h(df: pd.DataFrame) -> pd.Series:
    """Trend efficiency 24h: |close/close_24h_ago - 1| / sum(|ret_1h|, 24)."""
    net_move = (df["close"] / delay(df["close"], 24) - 1.0).abs()
    ret = df["close"].pct_change().abs()
    path_len = rolling_sum(ret, 24)
    return net_move / path_len.replace(0, np.nan)


def _compute_price_pos_120h(df: pd.DataFrame) -> pd.Series:
    """Price position 120h: (close - LL120) / (HH120 - LL120 + eps)."""
    hh = rolling_max(df["high"], 120)
    ll = rolling_min(df["low"], 120)
    return (df["close"] - ll) / (hh - ll + 1e-8)


# ── PM-35: Batch-01 Controlled Factor Intake ─────────────────────

def _compute_rev_2h(df: pd.DataFrame) -> pd.Series:
    """Short-term reversal 2h: -(close / close_2h_ago - 1)."""
    return -(df["close"] / delay(df["close"], 2) - 1.0)


def _compute_mom_vol_adjusted_20h(df: pd.DataFrame) -> pd.Series:
    """Volatility-adjusted momentum 20h: mom_20h / rolling_std(ret, 20).

    Safe for zero/near-zero volatility: replaces zeros/NaNs with NaN.
    """
    mom_20h = df["close"] / delay(df["close"], 20) - 1.0
    ret = df["close"].pct_change()
    vol = rolling_std(ret, 20)
    return mom_20h / vol.replace(0, np.nan)


def _compute_range_breakout_vol_confirm_20h(df: pd.DataFrame) -> pd.Series:
    """Volume-confirmed range breakout 20h.

    Measures position in range [0,1] and multiplies by volume zscore when near high.
    breakout_dist = (close - low_20) / (high_20 - low_20)
    Returns breakout_dist * zscore(volume, 20) when breakout_dist > 0.8, else NaN.
    """
    hh = rolling_max(df["high"], 20)
    ll = rolling_min(df["low"], 20)
    breakout_dist = (df["close"] - ll) / (hh - ll + 1e-8)
    vol_z = zscore(df["volume"], 20)
    return where(breakout_dist > 0.8, breakout_dist * vol_z, np.nan)


def _compute_volume_pressure_20h(df: pd.DataFrame) -> pd.Series:
    """Volume pressure 20h: rolling_mean(sign(delta(close, 1)) * volume, 20)."""
    close_delta = delta(df["close"], 1)
    return rolling_mean(sign(close_delta) * df["volume"], 20)


def _compute_up_down_vol_ratio_20h(df: pd.DataFrame) -> pd.Series:
    """Up-down volume ratio 20h: sum(vol where ret>0, 20) / sum(vol, 20).

    Measures buying pressure as fraction of total volume.
    Higher values = more volume on up bars = bullish participation.
    """
    ret = df["close"].pct_change()
    up_vol = (df["volume"] * (ret > 0).astype(float))
    total_vol = rolling_sum(df["volume"], 20)
    return rolling_sum(up_vol, 20) / total_vol.replace(0, np.nan)


def _compute_xs_rank_mom_accel_prep(df: pd.DataFrame) -> pd.Series:
    """Momentum acceleration for cross-sectional ranking.

    Per-symbol: mom_20h - delay(mom_20h, 5).
    Cross-sectional rank applied by caller (build_factor_values.py).
    """
    mom_20h = df["close"] / delay(df["close"], 20) - 1.0
    return mom_20h - delay(mom_20h, 5)


def _compute_clv_20h(df: pd.DataFrame) -> pd.Series:
    """Close Location Value 20h: mean(((close - low) - (high - close)) / (high - low + eps), 20).

    CLV measures where the close is within the high-low range of each bar.
    - CLV = +1: close at high (buyers dominate)
    - CLV = -1: close at low (sellers dominate)
    - CLV = 0: close at midpoint

    Taking the 20h mean captures sustained buying/selling pressure.
    """
    h, l, c = df["high"], df["low"], df["close"]
    clv_single = ((c - l) - (h - c)) / (h - l + 1e-8)
    return rolling_mean(clv_single, 20)


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
        expected_direction="positive",
        compute_fn=_compute_reversal_5h,
        notes="-(close / close_5h_ago - 1); formula is already sign-inverted to represent reversal hypothesis; higher factor_value means stronger prior loser / stronger reversal signal. expected_direction set to positive to avoid double inversion in direction-adjusted IC.",
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
    # Public Alpha158 kbar pilot batch
    FactorSpec(
        factor_id="q158_klen_open", family="alpha158_kbar",
        required_columns=["open", "high", "low"], lookback_window=1,
        expected_direction="conditional",
        compute_fn=_compute_q158_klen_open,
        notes="Alpha158 KLEN: (high - low) / open; 1h kbar range length normalized by open",
    ),
    # Public Alpha158 kbar / price batch 06
    FactorSpec(
        factor_id="q158_kmid_open", family="alpha158_kbar",
        required_columns=["open", "close"], lookback_window=1,
        expected_direction="positive",
        compute_fn=_compute_q158_kmid_open,
        notes="Alpha158 KMID: (close - open) / open; 1h candle body return normalized by open",
    ),
    FactorSpec(
        factor_id="q158_kmid_range", family="alpha158_kbar",
        required_columns=["open", "high", "low", "close"], lookback_window=1,
        expected_direction="positive",
        compute_fn=_compute_q158_kmid_range,
        notes="Alpha158 KMID2: (close - open) / (high - low + eps); signed candle body normalized by range",
    ),
    FactorSpec(
        factor_id="q158_kup_open", family="alpha158_kbar",
        required_columns=["open", "high", "close"], lookback_window=1,
        expected_direction="negative",
        compute_fn=_compute_q158_kup_open,
        notes="Alpha158 KUP: (high - max(open, close)) / open; upper shadow normalized by open",
    ),
    FactorSpec(
        factor_id="q158_kup_range", family="alpha158_kbar",
        required_columns=["open", "high", "low", "close"], lookback_window=1,
        expected_direction="negative",
        compute_fn=_compute_q158_kup_range,
        notes="Alpha158 KUP2: (high - max(open, close)) / (high - low + eps); upper shadow normalized by range",
    ),
    FactorSpec(
        factor_id="q158_klow_open", family="alpha158_kbar",
        required_columns=["open", "low", "close"], lookback_window=1,
        expected_direction="positive",
        compute_fn=_compute_q158_klow_open,
        notes="Alpha158 KLOW: (min(open, close) - low) / open; lower shadow normalized by open",
    ),
    FactorSpec(
        factor_id="q158_klow_range", family="alpha158_kbar",
        required_columns=["open", "high", "low", "close"], lookback_window=1,
        expected_direction="positive",
        compute_fn=_compute_q158_klow_range,
        notes="Alpha158 KLOW2: (min(open, close) - low) / (high - low + eps); lower shadow normalized by range",
    ),
    FactorSpec(
        factor_id="q158_ksft_open", family="alpha158_kbar",
        required_columns=["open", "high", "low", "close"], lookback_window=1,
        expected_direction="positive",
        compute_fn=_compute_q158_ksft_open,
        notes="Alpha158 KSFT: (2*close - high - low) / open; signed close-location shift normalized by open",
    ),
    FactorSpec(
        factor_id="q158_ksft_range", family="alpha158_kbar",
        required_columns=["high", "low", "close"], lookback_window=1,
        expected_direction="positive",
        compute_fn=_compute_q158_ksft_range,
        notes="Alpha158 KSFT2: (2*close - high - low) / (high - low + eps); signed close-location shift normalized by range",
    ),
    FactorSpec(
        factor_id="q158_rsv_20h", family="alpha158_rolling",
        required_columns=["high", "low", "close"], lookback_window=20,
        expected_direction="conditional",
        compute_fn=_compute_q158_rsv_20h,
        notes="Alpha158 RSV20: (close - Min(low,20)) / (Max(high,20) - Min(low,20) + eps); 1h adaptation of rolling price position",
    ),
    FactorSpec(
        factor_id="q158_open_close_0h", family="alpha158_price",
        required_columns=["open", "close"], lookback_window=1,
        expected_direction="conditional",
        compute_fn=_compute_q158_open_close_0h,
        notes="Alpha158 OPEN0: open / close; current open normalized by current close from Alpha158 price feature block",
    ),
    # Public Alpha158 price batch 07
    FactorSpec(
        factor_id="q158_high_close_0h", family="alpha158_price",
        required_columns=["high", "close"], lookback_window=1,
        expected_direction="conditional",
        compute_fn=_compute_q158_high_close_0h,
        notes="Alpha158 HIGH0: high / close; current high normalized by current close from Alpha158 price feature block",
    ),
    FactorSpec(
        factor_id="q158_low_close_0h", family="alpha158_price",
        required_columns=["low", "close"], lookback_window=1,
        expected_direction="conditional",
        compute_fn=_compute_q158_low_close_0h,
        notes="Alpha158 LOW0: low / close; current low normalized by current close from Alpha158 price feature block",
    ),
    FactorSpec(
        factor_id="q158_open_close_1h", family="alpha158_price",
        required_columns=["open", "close"], lookback_window=2,
        expected_direction="conditional",
        compute_fn=_compute_q158_open_close_1h,
        notes="Alpha158 OPEN1: Ref(open,1) / close; previous open normalized by current close from Alpha158 price feature block",
    ),
    FactorSpec(
        factor_id="q158_high_close_1h", family="alpha158_price",
        required_columns=["high", "close"], lookback_window=2,
        expected_direction="conditional",
        compute_fn=_compute_q158_high_close_1h,
        notes="Alpha158 HIGH1: Ref(high,1) / close; previous high normalized by current close from Alpha158 price feature block",
    ),
    FactorSpec(
        factor_id="q158_low_close_1h", family="alpha158_price",
        required_columns=["low", "close"], lookback_window=2,
        expected_direction="conditional",
        compute_fn=_compute_q158_low_close_1h,
        notes="Alpha158 LOW1: Ref(low,1) / close; previous low normalized by current close from Alpha158 price feature block",
    ),
    # Public Alpha158 price batch 08
    FactorSpec(
        factor_id="q158_open_close_2h", family="alpha158_price",
        required_columns=["open", "close"], lookback_window=3,
        expected_direction="conditional",
        compute_fn=_compute_q158_open_close_2h,
        notes="Alpha158 OPEN2: Ref(open,2) / close; two-bar lagged open normalized by current close from Alpha158 price feature block",
    ),
    FactorSpec(
        factor_id="q158_high_close_2h", family="alpha158_price",
        required_columns=["high", "close"], lookback_window=3,
        expected_direction="conditional",
        compute_fn=_compute_q158_high_close_2h,
        notes="Alpha158 HIGH2: Ref(high,2) / close; two-bar lagged high normalized by current close from Alpha158 price feature block",
    ),
    FactorSpec(
        factor_id="q158_low_close_2h", family="alpha158_price",
        required_columns=["low", "close"], lookback_window=3,
        expected_direction="conditional",
        compute_fn=_compute_q158_low_close_2h,
        notes="Alpha158 LOW2: Ref(low,2) / close; two-bar lagged low normalized by current close from Alpha158 price feature block",
    ),
    FactorSpec(
        factor_id="q158_open_close_3h", family="alpha158_price",
        required_columns=["open", "close"], lookback_window=4,
        expected_direction="conditional",
        compute_fn=_compute_q158_open_close_3h,
        notes="Alpha158 OPEN3: Ref(open,3) / close; three-bar lagged open normalized by current close from Alpha158 price feature block",
    ),
    FactorSpec(
        factor_id="q158_high_close_3h", family="alpha158_price",
        required_columns=["high", "close"], lookback_window=4,
        expected_direction="conditional",
        compute_fn=_compute_q158_high_close_3h,
        notes="Alpha158 HIGH3: Ref(high,3) / close; three-bar lagged high normalized by current close from Alpha158 price feature block",
    ),
    FactorSpec(
        factor_id="q158_low_close_3h", family="alpha158_price",
        required_columns=["low", "close"], lookback_window=4,
        expected_direction="conditional",
        compute_fn=_compute_q158_low_close_3h,
        notes="Alpha158 LOW3: Ref(low,3) / close; three-bar lagged low normalized by current close from Alpha158 price feature block",
    ),
    # Public Alpha158 price batch 10
    FactorSpec(
        factor_id="q158_open_close_4h", family="alpha158_price",
        required_columns=["open", "close"], lookback_window=5,
        expected_direction="conditional",
        compute_fn=_compute_q158_open_close_4h,
        notes="Alpha158 OPEN4: Ref(open,4) / close; four-bar lagged open normalized by current close from Alpha158 price feature block",
    ),
    FactorSpec(
        factor_id="q158_high_close_4h", family="alpha158_price",
        required_columns=["high", "close"], lookback_window=5,
        expected_direction="conditional",
        compute_fn=_compute_q158_high_close_4h,
        notes="Alpha158 HIGH4: Ref(high,4) / close; four-bar lagged high normalized by current close from Alpha158 price feature block",
    ),
    FactorSpec(
        factor_id="q158_low_close_4h", family="alpha158_price",
        required_columns=["low", "close"], lookback_window=5,
        expected_direction="conditional",
        compute_fn=_compute_q158_low_close_4h,
        notes="Alpha158 LOW4: Ref(low,4) / close; four-bar lagged low normalized by current close from Alpha158 price feature block",
    ),
    FactorSpec(
        factor_id="q158_close_close_4h", family="alpha158_price",
        required_columns=["close"], lookback_window=5,
        expected_direction="conditional",
        compute_fn=_compute_q158_close_close_4h,
        notes="Alpha158 CLOSE4: Ref(close,4) / close; four-bar lagged close normalized by current close from Alpha158 price feature block",
    ),
    # Public Alpha158 volume batch 09
    FactorSpec(
        factor_id="q158_volume_ratio_1h", family="alpha158_volume",
        required_columns=["volume"], lookback_window=2,
        expected_direction="conditional",
        compute_fn=_compute_q158_volume_ratio_1h,
        notes="Alpha158 VOLUME1: Ref(volume,1)/(volume+1e-12); previous volume normalized by current volume from Alpha158 volume feature block",
    ),
    FactorSpec(
        factor_id="q158_volume_ratio_2h", family="alpha158_volume",
        required_columns=["volume"], lookback_window=3,
        expected_direction="conditional",
        compute_fn=_compute_q158_volume_ratio_2h,
        notes="Alpha158 VOLUME2: Ref(volume,2)/(volume+1e-12); two-bar lagged volume normalized by current volume from Alpha158 volume feature block",
    ),
    FactorSpec(
        factor_id="q158_volume_ratio_3h", family="alpha158_volume",
        required_columns=["volume"], lookback_window=4,
        expected_direction="conditional",
        compute_fn=_compute_q158_volume_ratio_3h,
        notes="Alpha158 VOLUME3: Ref(volume,3)/(volume+1e-12); three-bar lagged volume normalized by current volume from Alpha158 volume feature block",
    ),
    FactorSpec(
        factor_id="q158_volume_ratio_4h", family="alpha158_volume",
        required_columns=["volume"], lookback_window=5,
        expected_direction="conditional",
        compute_fn=_compute_q158_volume_ratio_4h,
        notes="Alpha158 VOLUME4: Ref(volume,4)/(volume+1e-12); four-bar lagged volume normalized by current volume from Alpha158 volume feature block",
    ),
    # Public Alpha158 rolling batch 02
    FactorSpec(
        factor_id="q158_qtlu_20h", family="alpha158_rolling",
        required_columns=["close"], lookback_window=20,
        expected_direction="conditional",
        compute_fn=_compute_q158_qtlu_20h,
        notes="Alpha158 QTLU20: Quantile(close,20,0.8) / close; 1h adaptation of upper rolling close quantile",
    ),
    FactorSpec(
        factor_id="q158_qtld_20h", family="alpha158_rolling",
        required_columns=["close"], lookback_window=20,
        expected_direction="conditional",
        compute_fn=_compute_q158_qtld_20h,
        notes="Alpha158 QTLD20: Quantile(close,20,0.2) / close; 1h adaptation of lower rolling close quantile",
    ),
    FactorSpec(
        factor_id="q158_rank_close_20h", family="alpha158_rolling",
        required_columns=["close"], lookback_window=20,
        expected_direction="conditional",
        compute_fn=_compute_q158_rank_close_20h,
        notes="Alpha158 RANK20: Rank(close,20); current close percentile within the past 20 one-hour bars",
    ),
    FactorSpec(
        factor_id="q158_cntp_20h", family="alpha158_rolling",
        required_columns=["close"], lookback_window=21,
        expected_direction="positive",
        compute_fn=_compute_q158_cntp_20h,
        notes="Alpha158 CNTP20: Mean(close > Ref(close,1),20); fraction of up bars over the past 20 one-hour bars",
    ),
    FactorSpec(
        factor_id="q158_cntn_20h", family="alpha158_rolling",
        required_columns=["close"], lookback_window=21,
        expected_direction="negative",
        compute_fn=_compute_q158_cntn_20h,
        notes="Alpha158 CNTN20: Mean(close < Ref(close,1),20); fraction of down bars over the past 20 one-hour bars",
    ),
    FactorSpec(
        factor_id="q158_sumd_20h", family="alpha158_rolling",
        required_columns=["close"], lookback_window=21,
        expected_direction="positive",
        compute_fn=_compute_q158_sumd_20h,
        notes="Alpha158 SUMD20: (Sum(up moves,20)-Sum(down moves,20))/(Sum(abs moves,20)+eps); signed move dominance",
    ),
    # Public Alpha158 rolling batch 03
    FactorSpec(
        factor_id="q158_beta_20h", family="alpha158_rolling_regression",
        required_columns=["close"], lookback_window=20,
        expected_direction="conditional",
        compute_fn=_compute_q158_beta_20h,
        notes="Alpha158 BETA20: Slope(close,20) / close; rolling linear trend slope normalized by current close",
    ),
    FactorSpec(
        factor_id="q158_rsqr_20h", family="alpha158_rolling_regression",
        required_columns=["close"], lookback_window=20,
        expected_direction="conditional",
        compute_fn=_compute_q158_rsqr_20h,
        notes="Alpha158 RSQR20: Rsquare(close,20); rolling linear trend fit quality",
    ),
    FactorSpec(
        factor_id="q158_resi_20h", family="alpha158_rolling_regression",
        required_columns=["close"], lookback_window=20,
        expected_direction="conditional",
        compute_fn=_compute_q158_resi_20h,
        notes="Alpha158 RESI20: Resi(close,20) / close; latest residual from rolling linear trend normalized by current close",
    ),
    FactorSpec(
        factor_id="q158_imax_20h", family="alpha158_rolling_position",
        required_columns=["high"], lookback_window=20,
        expected_direction="conditional",
        compute_fn=_compute_q158_imax_20h,
        notes="Alpha158 IMAX20: IdxMax(high,20) / 20; bars since latest 20h high, scaled by window",
    ),
    FactorSpec(
        factor_id="q158_imin_20h", family="alpha158_rolling_position",
        required_columns=["low"], lookback_window=20,
        expected_direction="conditional",
        compute_fn=_compute_q158_imin_20h,
        notes="Alpha158 IMIN20: IdxMin(low,20) / 20; bars since latest 20h low, scaled by window",
    ),
    FactorSpec(
        factor_id="q158_imxd_20h", family="alpha158_rolling_position",
        required_columns=["high", "low"], lookback_window=20,
        expected_direction="conditional",
        compute_fn=_compute_q158_imxd_20h,
        notes="Alpha158 IMXD20: (IdxMax(high,20)-IdxMin(low,20)) / 20; relative recency of high versus low",
    ),
    # Public Alpha158 rolling batch 04
    FactorSpec(
        factor_id="q158_roc_20h", family="alpha158_rolling_price",
        required_columns=["close"], lookback_window=21,
        expected_direction="conditional",
        compute_fn=_compute_q158_roc_20h,
        notes="Alpha158 ROC20: Ref(close,20) / close; 1h adaptation of 20-bar rate-of-change ratio",
    ),
    # Public Alpha158 rolling price batch 11
    FactorSpec(
        factor_id="q158_ma_5h", family="alpha158_rolling_price",
        required_columns=["close"], lookback_window=5,
        expected_direction="conditional",
        compute_fn=_compute_q158_ma_5h,
        notes="Alpha158 MA5: Mean(close,5) / close; 1h adaptation of short rolling average normalized by current close",
    ),
    FactorSpec(
        factor_id="q158_std_5h", family="alpha158_rolling_price",
        required_columns=["close"], lookback_window=5,
        expected_direction="negative",
        compute_fn=_compute_q158_std_5h,
        notes="Alpha158 STD5: Std(close,5) / close; short rolling close dispersion normalized by current close",
    ),
    FactorSpec(
        factor_id="q158_max_5h", family="alpha158_rolling_price",
        required_columns=["high", "close"], lookback_window=5,
        expected_direction="conditional",
        compute_fn=_compute_q158_max_5h,
        notes="Alpha158 MAX5: Max(high,5) / close; short rolling high normalized by current close",
    ),
    FactorSpec(
        factor_id="q158_min_5h", family="alpha158_rolling_price",
        required_columns=["low", "close"], lookback_window=5,
        expected_direction="conditional",
        compute_fn=_compute_q158_min_5h,
        notes="Alpha158 MIN5: Min(low,5) / close; short rolling low normalized by current close",
    ),
    # Public Alpha158 rolling price batch 12
    FactorSpec(
        factor_id="q158_ma_10h", family="alpha158_rolling_price",
        required_columns=["close"], lookback_window=10,
        expected_direction="conditional",
        compute_fn=_compute_q158_ma_10h,
        notes="Alpha158 MA10: Mean(close,10) / close; 1h adaptation of medium-short rolling average normalized by current close",
    ),
    FactorSpec(
        factor_id="q158_std_10h", family="alpha158_rolling_price",
        required_columns=["close"], lookback_window=10,
        expected_direction="negative",
        compute_fn=_compute_q158_std_10h,
        notes="Alpha158 STD10: Std(close,10) / close; medium-short rolling close dispersion normalized by current close",
    ),
    FactorSpec(
        factor_id="q158_max_10h", family="alpha158_rolling_price",
        required_columns=["high", "close"], lookback_window=10,
        expected_direction="conditional",
        compute_fn=_compute_q158_max_10h,
        notes="Alpha158 MAX10: Max(high,10) / close; medium-short rolling high normalized by current close",
    ),
    FactorSpec(
        factor_id="q158_min_10h", family="alpha158_rolling_price",
        required_columns=["low", "close"], lookback_window=10,
        expected_direction="conditional",
        compute_fn=_compute_q158_min_10h,
        notes="Alpha158 MIN10: Min(low,10) / close; medium-short rolling low normalized by current close",
    ),
    FactorSpec(
        factor_id="q158_ma_20h", family="alpha158_rolling_price",
        required_columns=["close"], lookback_window=20,
        expected_direction="conditional",
        compute_fn=_compute_q158_ma_20h,
        notes="Alpha158 MA20: Mean(close,20) / close; rolling average normalized by current close",
    ),
    FactorSpec(
        factor_id="q158_std_20h", family="alpha158_rolling_price",
        required_columns=["close"], lookback_window=20,
        expected_direction="negative",
        compute_fn=_compute_q158_std_20h,
        notes="Alpha158 STD20: Std(close,20) / close; rolling close dispersion normalized by current close",
    ),
    FactorSpec(
        factor_id="q158_max_20h", family="alpha158_rolling_price",
        required_columns=["high", "close"], lookback_window=20,
        expected_direction="conditional",
        compute_fn=_compute_q158_max_20h,
        notes="Alpha158 MAX20: Max(high,20) / close; rolling high normalized by current close",
    ),
    FactorSpec(
        factor_id="q158_min_20h", family="alpha158_rolling_price",
        required_columns=["low", "close"], lookback_window=20,
        expected_direction="conditional",
        compute_fn=_compute_q158_min_20h,
        notes="Alpha158 MIN20: Min(low,20) / close; rolling low normalized by current close",
    ),
    # Public Alpha158 rolling price batch 13
    FactorSpec(
        factor_id="q158_ma_30h", family="alpha158_rolling_price",
        required_columns=["close"], lookback_window=30,
        expected_direction="conditional",
        compute_fn=_compute_q158_ma_30h,
        notes="Alpha158 MA30: Mean(close,30) / close; 1h adaptation of medium rolling average normalized by current close",
    ),
    FactorSpec(
        factor_id="q158_std_30h", family="alpha158_rolling_price",
        required_columns=["close"], lookback_window=30,
        expected_direction="negative",
        compute_fn=_compute_q158_std_30h,
        notes="Alpha158 STD30: Std(close,30) / close; medium rolling close dispersion normalized by current close",
    ),
    FactorSpec(
        factor_id="q158_max_30h", family="alpha158_rolling_price",
        required_columns=["high", "close"], lookback_window=30,
        expected_direction="conditional",
        compute_fn=_compute_q158_max_30h,
        notes="Alpha158 MAX30: Max(high,30) / close; medium rolling high normalized by current close",
    ),
    FactorSpec(
        factor_id="q158_min_30h", family="alpha158_rolling_price",
        required_columns=["low", "close"], lookback_window=30,
        expected_direction="conditional",
        compute_fn=_compute_q158_min_30h,
        notes="Alpha158 MIN30: Min(low,30) / close; medium rolling low normalized by current close",
    ),
    # Public Alpha158 rolling price batch 14
    FactorSpec(
        factor_id="q158_ma_60h", family="alpha158_rolling_price",
        required_columns=["close"], lookback_window=60,
        expected_direction="conditional",
        compute_fn=_compute_q158_ma_60h,
        notes="Alpha158 MA60: Mean(close,60) / close; 1h adaptation of medium-long rolling average normalized by current close",
    ),
    FactorSpec(
        factor_id="q158_std_60h", family="alpha158_rolling_price",
        required_columns=["close"], lookback_window=60,
        expected_direction="negative",
        compute_fn=_compute_q158_std_60h,
        notes="Alpha158 STD60: Std(close,60) / close; medium-long rolling close dispersion normalized by current close",
    ),
    FactorSpec(
        factor_id="q158_max_60h", family="alpha158_rolling_price",
        required_columns=["high", "close"], lookback_window=60,
        expected_direction="conditional",
        compute_fn=_compute_q158_max_60h,
        notes="Alpha158 MAX60: Max(high,60) / close; medium-long rolling high normalized by current close",
    ),
    FactorSpec(
        factor_id="q158_min_60h", family="alpha158_rolling_price",
        required_columns=["low", "close"], lookback_window=60,
        expected_direction="conditional",
        compute_fn=_compute_q158_min_60h,
        notes="Alpha158 MIN60: Min(low,60) / close; medium-long rolling low normalized by current close",
    ),
    FactorSpec(
        factor_id="q158_cntd_20h", family="alpha158_rolling_direction",
        required_columns=["close"], lookback_window=21,
        expected_direction="positive",
        compute_fn=_compute_q158_cntd_20h,
        notes="Alpha158 CNTD20: Mean(close > Ref(close,1),20) - Mean(close < Ref(close,1),20); signed up/down bar balance",
    ),
    FactorSpec(
        factor_id="q158_corr_20h", family="alpha158_rolling_volume_price",
        required_columns=["close", "volume"], lookback_window=20,
        expected_direction="conditional",
        compute_fn=_compute_q158_corr_20h,
        notes="Alpha158 CORR20: Corr(close, Log(volume+1),20); rolling price-volume level correlation",
    ),
    FactorSpec(
        factor_id="q158_cord_20h", family="alpha158_rolling_volume_price",
        required_columns=["close", "volume"], lookback_window=21,
        expected_direction="conditional",
        compute_fn=_compute_q158_cord_20h,
        notes="Alpha158 CORD20: Corr(close/Ref(close,1), Log(volume/Ref(volume,1)+1),20); rolling return-volume change correlation",
    ),
    # Public Alpha158 rolling batch 05
    FactorSpec(
        factor_id="q158_sump_20h", family="alpha158_rolling_direction",
        required_columns=["close"], lookback_window=21,
        expected_direction="positive",
        compute_fn=_compute_q158_sump_20h,
        notes="Alpha158 SUMP20: Sum(max(close-Ref(close,1),0),20)/(Sum(abs(close-Ref(close,1)),20)+eps); positive close-move share",
    ),
    FactorSpec(
        factor_id="q158_sumn_20h", family="alpha158_rolling_direction",
        required_columns=["close"], lookback_window=21,
        expected_direction="negative",
        compute_fn=_compute_q158_sumn_20h,
        notes="Alpha158 SUMN20: Sum(max(Ref(close,1)-close,0),20)/(Sum(abs(close-Ref(close,1)),20)+eps); negative close-move share",
    ),
    FactorSpec(
        factor_id="q158_vma_20h", family="alpha158_rolling_volume",
        required_columns=["volume"], lookback_window=20,
        expected_direction="conditional",
        compute_fn=_compute_q158_vma_20h,
        notes="Alpha158 VMA20: Mean(volume,20)/(volume+eps); rolling average volume normalized by current volume",
    ),
    FactorSpec(
        factor_id="q158_vstd_20h", family="alpha158_rolling_volume",
        required_columns=["volume"], lookback_window=20,
        expected_direction="conditional",
        compute_fn=_compute_q158_vstd_20h,
        notes="Alpha158 VSTD20: Std(volume,20)/(volume+eps); rolling volume dispersion normalized by current volume",
    ),
    FactorSpec(
        factor_id="q158_wvma_20h", family="alpha158_rolling_volume",
        required_columns=["close", "volume"], lookback_window=21,
        expected_direction="negative",
        compute_fn=_compute_q158_wvma_20h,
        notes="Alpha158 WVMA20: Std(abs(close/Ref(close,1)-1)*volume,20)/(Mean(abs(close/Ref(close,1)-1)*volume,20)+eps); volume-weighted absolute-return volatility ratio",
    ),
    FactorSpec(
        factor_id="q158_vsump_20h", family="alpha158_rolling_volume",
        required_columns=["volume"], lookback_window=21,
        expected_direction="conditional",
        compute_fn=_compute_q158_vsump_20h,
        notes="Alpha158 VSUMP20: Sum(max(volume-Ref(volume,1),0),20)/(Sum(abs(volume-Ref(volume,1)),20)+eps); positive volume-change share",
    ),
    FactorSpec(
        factor_id="q158_vsumn_20h", family="alpha158_rolling_volume",
        required_columns=["volume"], lookback_window=21,
        expected_direction="conditional",
        compute_fn=_compute_q158_vsumn_20h,
        notes="Alpha158 VSUMN20: Sum(max(Ref(volume,1)-volume,0),20)/(Sum(abs(volume-Ref(volume,1)),20)+eps); negative volume-change share",
    ),
    FactorSpec(
        factor_id="q158_vsumd_20h", family="alpha158_rolling_volume",
        required_columns=["volume"], lookback_window=21,
        expected_direction="conditional",
        compute_fn=_compute_q158_vsumd_20h,
        notes="Alpha158 VSUMD20: (Sum(max(volume-Ref(volume,1),0),20)-Sum(max(Ref(volume,1)-volume,0),20))/(Sum(abs(volume-Ref(volume,1)),20)+eps); signed volume-change dominance",
    ),
    # PM-09: Alpha158-Inspired Batch 1
    FactorSpec(
        factor_id="vwap_dev_20h", family="alpha158_ohlcv",
        required_columns=["close", "volume"], lookback_window=20,
        expected_direction="conditional",
        compute_fn=_compute_vwap_dev_20h,
        notes="(close - vwap_20h) / vwap_20h; vwap_20h = sum(close*vol,20)/sum(vol,20)",
    ),
    FactorSpec(
        factor_id="wvma_20h", family="alpha158_ohlcv",
        required_columns=["close", "volume"], lookback_window=21,
        expected_direction="negative",
        compute_fn=_compute_wvma_20h,
        notes="rolling_std(ret*vol,20) / rolling_mean(vol,20); volume-weighted volatility",
    ),
    FactorSpec(
        factor_id="vol_ret_corr_20h", family="alpha158_ohlcv",
        required_columns=["close", "volume"], lookback_window=21,
        expected_direction="conditional",
        compute_fn=_compute_vol_ret_corr_20h,
        notes="rolling_corr(ret_1h, delta(volume,1), 20); return-volume correlation",
    ),
    FactorSpec(
        factor_id="intraday_ret", family="alpha158_ohlcv",
        required_columns=["open", "close"], lookback_window=1,
        expected_direction="conditional",
        compute_fn=_compute_intraday_ret,
        notes="(close - open) / open; 1h bar open-to-close return",
    ),
    FactorSpec(
        factor_id="klow_close", family="alpha158_ohlcv",
        required_columns=["open", "low", "close"], lookback_window=1,
        expected_direction="positive",
        compute_fn=_compute_klow_close,
        notes="(min(open,close) - low) / close; lower wick as fraction of close",
    ),
    FactorSpec(
        factor_id="ksft_5h", family="alpha158_ohlcv",
        required_columns=["close"], lookback_window=6,
        expected_direction="conditional",
        compute_fn=_compute_ksft_5h,
        notes="rolling_skewness(ret_1h, 5); short-window return skewness",
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
    # ── Phase 7B: Momentum (3) ───────────────────────────────────
    FactorSpec(
        factor_id="mom_5h", family="momentum",
        required_columns=["close"], lookback_window=5,
        expected_direction="positive",
        compute_fn=_compute_mom_5h,
        notes="close / close_5h_ago - 1",
    ),
    FactorSpec(
        factor_id="mom_10h", family="momentum",
        required_columns=["close"], lookback_window=10,
        expected_direction="positive",
        compute_fn=_compute_mom_10h,
        notes="close / close_10h_ago - 1",
    ),
    FactorSpec(
        factor_id="mom_40h", family="momentum",
        required_columns=["close"], lookback_window=40,
        expected_direction="positive",
        compute_fn=_compute_mom_40h,
        notes="close / close_40h_ago - 1",
    ),
    # ── Phase 7B: Reversal (3) ───────────────────────────────────
    FactorSpec(
        factor_id="rev_3h", family="reversal",
        required_columns=["close"], lookback_window=3,
        expected_direction="positive",
        compute_fn=_compute_rev_3h,
        notes="-(close / close_3h_ago - 1); formula is already sign-inverted to represent reversal hypothesis; higher factor_value means stronger prior loser / stronger reversal signal. expected_direction set to positive to avoid double inversion in direction-adjusted IC.",
    ),
    FactorSpec(
        factor_id="rev_10h", family="reversal",
        required_columns=["close"], lookback_window=10,
        expected_direction="positive",
        compute_fn=_compute_rev_10h,
        notes="-(close / close_10h_ago - 1); formula is already sign-inverted to represent reversal hypothesis; higher factor_value means stronger prior loser / stronger reversal signal. expected_direction set to positive to avoid double inversion in direction-adjusted IC.",
    ),
    FactorSpec(
        factor_id="rev_24h", family="reversal",
        required_columns=["close"], lookback_window=24,
        expected_direction="positive",
        compute_fn=_compute_rev_24h,
        notes="-(close / close_24h_ago - 1); formula is already sign-inverted to represent reversal hypothesis; higher factor_value means stronger prior loser / stronger reversal signal. expected_direction set to positive to avoid double inversion in direction-adjusted IC.",
    ),
    # ── Phase 7B: Volatility (3) ─────────────────────────────────
    FactorSpec(
        factor_id="vol_5h", family="volatility",
        required_columns=["close"], lookback_window=6,
        expected_direction="negative",
        compute_fn=_compute_vol_5h,
        notes="rolling std of 1h returns, 5 bars (lookback=6: pct_change needs t-1)",
    ),
    FactorSpec(
        factor_id="vol_40h", family="volatility",
        required_columns=["close"], lookback_window=41,
        expected_direction="negative",
        compute_fn=_compute_vol_40h,
        notes="rolling std of 1h returns, 40 bars (lookback=41)",
    ),
    FactorSpec(
        factor_id="vol_ratio_5_20", family="volatility",
        required_columns=["close"], lookback_window=21,
        expected_direction="conditional",
        compute_fn=_compute_vol_ratio_5_20,
        notes="std(ret,5) / std(ret,20)",
    ),
    # ── Phase 7B: Range Position (3) ─────────────────────────────
    FactorSpec(
        factor_id="range_1h", family="range_position",
        required_columns=["high", "low", "close"], lookback_window=1,
        expected_direction="conditional",
        compute_fn=_compute_range_1h,
        notes="(high - low) / close",
    ),
    FactorSpec(
        factor_id="range_4h", family="range_position",
        required_columns=["high", "low", "close"], lookback_window=4,
        expected_direction="conditional",
        compute_fn=_compute_range_4h,
        notes="(HH4 - LL4) / close",
    ),
    FactorSpec(
        factor_id="range_24h", family="range_position",
        required_columns=["high", "low", "close"], lookback_window=24,
        expected_direction="conditional",
        compute_fn=_compute_range_24h,
        notes="(HH24 - LL24) / close",
    ),
    # ── Phase 7B: Price Position (2) ─────────────────────────────
    FactorSpec(
        factor_id="price_pos_24h", family="price_position",
        required_columns=["high", "low", "close"], lookback_window=24,
        expected_direction="conditional",
        compute_fn=_compute_price_pos_24h,
        notes="(close - LL24) / (HH24 - LL24 + eps)",
    ),
    FactorSpec(
        factor_id="price_pos_72h", family="price_position",
        required_columns=["high", "low", "close"], lookback_window=72,
        expected_direction="conditional",
        compute_fn=_compute_price_pos_72h,
        notes="(close - LL72) / (HH72 - LL72 + eps)",
    ),
    # ── Phase 7B: Volume Zscore (2) ──────────────────────────────
    FactorSpec(
        factor_id="vol_zscore_20h", family="volume_liquidity",
        required_columns=["volume"], lookback_window=20,
        expected_direction="positive",
        compute_fn=_compute_vol_zscore_20h,
        notes="(volume - SMA20) / STD20",
    ),
    FactorSpec(
        factor_id="vol_zscore_48h", family="volume_liquidity",
        required_columns=["volume"], lookback_window=48,
        expected_direction="positive",
        compute_fn=_compute_vol_zscore_48h,
        notes="(volume - SMA48) / STD48",
    ),
    # ── Phase 7B: Quote Volume Zscore (2) ────────────────────────
    FactorSpec(
        factor_id="qvol_zscore_20h", family="quote_volume_liquidity",
        required_columns=["quote_volume"], lookback_window=20,
        expected_direction="positive",
        compute_fn=_compute_qvol_zscore_20h,
        notes="(quote_volume - SMA20) / STD20",
    ),
    FactorSpec(
        factor_id="qvol_zscore_48h", family="quote_volume_liquidity",
        required_columns=["quote_volume"], lookback_window=48,
        expected_direction="positive",
        compute_fn=_compute_qvol_zscore_48h,
        notes="(quote_volume - SMA48) / STD48",
    ),
    # ── Phase 7B: Trend MA Gap (2) ───────────────────────────────
    FactorSpec(
        factor_id="ma_gap_5_20", family="trend_ma",
        required_columns=["close"], lookback_window=20,
        expected_direction="positive",
        compute_fn=_compute_ma_gap_5_20,
        notes="(SMA5 - SMA20) / SMA20",
    ),
    FactorSpec(
        factor_id="ma_gap_10_40", family="trend_ma",
        required_columns=["close"], lookback_window=40,
        expected_direction="positive",
        compute_fn=_compute_ma_gap_10_40,
        notes="(SMA10 - SMA40) / SMA40",
    ),
    # ── Phase 7B: Breakout Distance (2) ──────────────────────────
    FactorSpec(
        factor_id="breakout_dist_20h", family="breakout",
        required_columns=["high", "low", "close"], lookback_window=20,
        expected_direction="positive",
        compute_fn=_compute_breakout_dist_20h,
        notes="(close - HH20) / (HH20 - LL20 + eps)",
    ),
    FactorSpec(
        factor_id="breakout_dist_48h", family="breakout",
        required_columns=["high", "low", "close"], lookback_window=48,
        expected_direction="positive",
        compute_fn=_compute_breakout_dist_48h,
        notes="(close - HH48) / (HH48 - LL48 + eps)",
    ),
    # ── Phase 7B: Intraday Candle (3) ────────────────────────────
    FactorSpec(
        factor_id="candle_body", family="intraday_candle",
        required_columns=["open", "high", "low", "close"], lookback_window=1,
        expected_direction="conditional",
        compute_fn=_compute_candle_body,
        notes="(close - open) / (high - low + eps)",
    ),
    FactorSpec(
        factor_id="candle_wick_upper", family="intraday_candle",
        required_columns=["open", "high", "low", "close"], lookback_window=1,
        expected_direction="negative",
        compute_fn=_compute_candle_wick_upper,
        notes="(high - max(open, close)) / (high - low + eps)",
    ),
    FactorSpec(
        factor_id="candle_wick_lower", family="intraday_candle",
        required_columns=["open", "high", "low", "close"], lookback_window=1,
        expected_direction="positive",
        compute_fn=_compute_candle_wick_lower,
        notes="(min(open, close) - low) / (high - low + eps)",
    ),
    # ── Phase 7B: Cross-Sectional Normalized (2) ─────────────────
    FactorSpec(
        factor_id="xs_rank_ret_1h", family="cross_sectional_normalized",
        required_columns=["close"], lookback_window=2,
        expected_direction="conditional",
        compute_fn=_compute_xs_rank_ret_1h_prep,
        notes="Per-symbol 1h return; cross-sectional rank applied by caller",
    ),
    FactorSpec(
        factor_id="xs_rank_vol", family="cross_sectional_normalized",
        required_columns=["volume"], lookback_window=20,
        expected_direction="conditional",
        compute_fn=_compute_xs_rank_vol_prep,
        notes="Per-symbol 20h rolling mean volume; cross-sectional rank applied by caller",
    ),
    # ── Phase 7I-A: Technical Indicators (4) ────────────────────
    FactorSpec(
        factor_id="ema_12_26_gap", family="technical_indicators",
        required_columns=["close"], lookback_window=26,
        expected_direction="positive",
        compute_fn=_compute_ema_12_26_gap,
        notes="(EMA12 - EMA26) / EMA26",
    ),
    FactorSpec(
        factor_id="rsi_7h", family="technical_indicators",
        required_columns=["close"], lookback_window=8,
        expected_direction="negative",
        compute_fn=_compute_rsi_7h,
        notes="Wilder RSI lookback=7, 0-100 scale; lookback_window=8 for diff(1)+ewm(7)",
    ),
    FactorSpec(
        factor_id="rsi_28h", family="technical_indicators",
        required_columns=["close"], lookback_window=29,
        expected_direction="negative",
        compute_fn=_compute_rsi_28h,
        notes="Wilder RSI lookback=28, 0-100 scale; lookback_window=29 for diff(1)+ewm(28)",
    ),
    FactorSpec(
        factor_id="williams_r_14h", family="technical_indicators",
        required_columns=["high", "low", "close"], lookback_window=14,
        expected_direction="negative",
        compute_fn=_compute_williams_r_14h,
        notes="(HH14 - close) / (HH14 - LL14 + eps), 0-1 scale",
    ),
    # ── Phase 7I-A: Realized Skew/Kurtosis (2) ─────────────────
    FactorSpec(
        factor_id="downside_vol_20h", family="realized_skew_kurtosis",
        required_columns=["close"], lookback_window=21,
        expected_direction="negative",
        compute_fn=_compute_downside_vol_20h,
        notes="rolling_std(min(ret_1h, 0), 20); lookback=21 for pct_change+std(20)",
    ),
    FactorSpec(
        factor_id="vol_of_vol_20h", family="realized_skew_kurtosis",
        required_columns=["close"], lookback_window=26,
        expected_direction="negative",
        compute_fn=_compute_vol_of_vol_20h,
        notes="rolling_std(rolling_std(ret, 5), 20); lookback=26 for pct_change+std(5)+std(20)",
    ),
    # ── Phase 7I-A: Momentum / Trend / Volume (3) ──────────────
    FactorSpec(
        factor_id="mom_accel_20h", family="momentum",
        required_columns=["close"], lookback_window=25,
        expected_direction="positive",
        compute_fn=_compute_mom_accel_20h,
        notes="mom_20h - delay(mom_20h, 5); lookback=25 for lag(20)+delay(5)",
    ),
    FactorSpec(
        factor_id="qvol_ma_ratio_5_20", family="quote_volume_liquidity",
        required_columns=["quote_volume"], lookback_window=20,
        expected_direction="positive",
        compute_fn=_compute_qvol_ma_ratio_5_20,
        notes="SMA(quote_volume, 5) / SMA(quote_volume, 20) - 1",
    ),
    FactorSpec(
        factor_id="ma_gap_20_80", family="trend_ma",
        required_columns=["close"], lookback_window=80,
        expected_direction="positive",
        compute_fn=_compute_ma_gap_20_80,
        notes="(SMA20 - SMA80) / SMA80",
    ),
    # ── Phase 7M-A: Taker Imbalance (3) ────────────────────────
    FactorSpec(
        factor_id="taker_buy_ratio_20h", family="taker_imbalance",
        required_columns=["taker_buy_quote_volume", "quote_volume"], lookback_window=20,
        expected_direction="positive",
        compute_fn=_compute_taker_buy_ratio_20h,
        status="DIAGNOSTIC_PROBE",
        notes="rolling_mean(taker_buy_quote_volume / quote_volume, 20); Requires Phase 7L-R canonical crypto-native cache.",
    ),
    FactorSpec(
        factor_id="taker_buy_zscore_20h", family="taker_imbalance",
        required_columns=["taker_buy_quote_volume", "quote_volume"], lookback_window=20,
        expected_direction="positive",
        compute_fn=_compute_taker_buy_zscore_20h,
        status="DIAGNOSTIC_PROBE",
        notes="zscore(taker_buy_quote_volume / quote_volume, 20); Requires Phase 7L-R canonical crypto-native cache.",
    ),
    FactorSpec(
        factor_id="taker_buy_delta_5h", family="taker_imbalance",
        required_columns=["taker_buy_quote_volume", "quote_volume"], lookback_window=6,
        expected_direction="positive",
        compute_fn=_compute_taker_buy_delta_5h,
        status="DIAGNOSTIC_PROBE",
        notes="ratio - delay(ratio, 5); lookback=6 for ratio(1)+delay(5); Requires Phase 7L-R canonical crypto-native cache.",
    ),
    # ── Phase 7M-A: Funding Rate (3) ───────────────────────────
    FactorSpec(
        factor_id="funding_rate_level_20h", family="funding_rate",
        required_columns=["funding_rate"], lookback_window=20,
        expected_direction="negative",
        compute_fn=_compute_funding_rate_level_20h,
        status="DIAGNOSTIC_PROBE",
        notes="rolling_mean(funding_rate, 20); high funding = crowded long, mean-revert; Requires Phase 7L-R canonical crypto-native cache.",
    ),
    FactorSpec(
        factor_id="funding_rate_zscore_80h", family="funding_rate",
        required_columns=["funding_rate"], lookback_window=80,
        expected_direction="negative",
        compute_fn=_compute_funding_rate_zscore_80h,
        status="DIAGNOSTIC_PROBE",
        notes="zscore(funding_rate, 80); Requires Phase 7L-R canonical crypto-native cache.",
    ),
    FactorSpec(
        factor_id="funding_rate_change_24h", family="funding_rate",
        required_columns=["funding_rate"], lookback_window=25,
        expected_direction="negative",
        compute_fn=_compute_funding_rate_change_24h,
        status="DIAGNOSTIC_PROBE",
        notes="funding_rate - delay(funding_rate, 24); fast rise = crowded, expect reversal; Requires Phase 7L-R canonical crypto-native cache.",
    ),
    # ── Phase 13A-P2: Sprint 1 Diagnostic Factors (12) ───────────
    FactorSpec(
        factor_id="mom_72h", family="momentum",
        required_columns=["close"], lookback_window=72,
        expected_direction="positive",
        compute_fn=_compute_mom_72h,
        notes="close / close_72h_ago - 1; medium-horizon trend continuation diagnostic",
    ),
    FactorSpec(
        factor_id="mom_120h", family="momentum",
        required_columns=["close"], lookback_window=120,
        expected_direction="positive",
        compute_fn=_compute_mom_120h,
        notes="close / close_120h_ago - 1; longer-horizon trend continuation diagnostic",
    ),
    FactorSpec(
        factor_id="rev_1h", family="reversal",
        required_columns=["close"], lookback_window=1,
        expected_direction="positive",
        compute_fn=_compute_rev_1h,
        notes="-(close / close_1h_ago - 1); very short-term reversal diagnostic",
    ),
    FactorSpec(
        factor_id="rev_72h", family="reversal",
        required_columns=["close"], lookback_window=72,
        expected_direction="positive",
        compute_fn=_compute_rev_72h,
        notes="-(close / close_72h_ago - 1); medium-horizon reversal diagnostic",
    ),
    FactorSpec(
        factor_id="vol_ratio_20_80", family="volatility",
        required_columns=["close"], lookback_window=81,
        expected_direction="conditional",
        compute_fn=_compute_vol_ratio_20_80,
        notes="std(ret,20) / std(ret,80); short-vs-long volatility regime diagnostic",
    ),
    FactorSpec(
        factor_id="realized_skew_20h", family="realized_shape",
        required_columns=["close"], lookback_window=21,
        expected_direction="conditional",
        compute_fn=_compute_realized_skew_20h,
        notes="rolling skewness of 1h returns over 20 bars; asymmetry diagnostic",
    ),
    FactorSpec(
        factor_id="realized_kurt_20h", family="realized_shape",
        required_columns=["close"], lookback_window=21,
        expected_direction="conditional",
        compute_fn=_compute_realized_kurt_20h,
        notes="rolling kurtosis of 1h returns over 20 bars; tail risk / jumpiness diagnostic",
    ),
    FactorSpec(
        factor_id="amihud_illiquidity_20h", family="liquidity",
        required_columns=["close", "quote_volume"], lookback_window=21,
        expected_direction="negative",
        compute_fn=_compute_amihud_illiquidity_20h,
        notes="rolling_mean(abs(ret_1h) / quote_volume, 20); higher illiquidity penalized",
    ),
    FactorSpec(
        factor_id="qvol_ma_ratio_20_80", family="quote_volume_liquidity",
        required_columns=["quote_volume"], lookback_window=80,
        expected_direction="conditional",
        compute_fn=_compute_qvol_ma_ratio_20_80,
        notes="SMA(quote_volume,20) / SMA(quote_volume,80) - 1; medium-vs-long liquidity regime",
    ),
    FactorSpec(
        factor_id="price_volume_corr_20h", family="volume_price",
        required_columns=["close", "quote_volume"], lookback_window=21,
        expected_direction="conditional",
        compute_fn=_compute_price_volume_corr_20h,
        notes="rolling_corr(ret_1h, pct_change(quote_volume), 20); attention diagnostic",
    ),
    FactorSpec(
        factor_id="trend_efficiency_24h", family="trend_quality",
        required_columns=["close"], lookback_window=24,
        expected_direction="positive",
        compute_fn=_compute_trend_efficiency_24h,
        notes="abs(close/close_24h_ago-1) / sum(abs(ret_1h),24); cleaner directional move",
    ),
    FactorSpec(
        factor_id="price_pos_120h", family="price_position",
        required_columns=["high", "low", "close"], lookback_window=120,
        expected_direction="conditional",
        compute_fn=_compute_price_pos_120h,
        notes="(close - LL120) / (HH120 - LL120 + eps); long-window price location diagnostic",
    ),
    # ── PM-35: Batch-01 Controlled Factor Intake (5) ───────────────
    FactorSpec(
        factor_id="rev_2h", family="reversal",
        required_columns=["close"], lookback_window=2,
        expected_direction="positive",
        compute_fn=_compute_rev_2h,
        notes="-(close / close_2h_ago - 1); short-term reversal",
    ),
    FactorSpec(
        factor_id="mom_vol_adjusted_20h", family="momentum",
        required_columns=["close"], lookback_window=21,
        expected_direction="positive",
        compute_fn=_compute_mom_vol_adjusted_20h,
        notes="mom_20h / rolling_std(pct_change(close), 20); volatility-adjusted momentum; safe for zero vol",
    ),
    FactorSpec(
        factor_id="range_breakout_vol_confirm_20h", family="breakout",
        required_columns=["high", "low", "close", "volume"], lookback_window=20,
        expected_direction="positive",
        compute_fn=_compute_range_breakout_vol_confirm_20h,
        notes="breakout_dist_20h * zscore(volume, 20) when breakout_dist_20h > 0; volume-confirmed breakout",
    ),
    FactorSpec(
        factor_id="volume_pressure_20h", family="volume_price",
        required_columns=["close", "volume"], lookback_window=21,
        expected_direction="positive",
        compute_fn=_compute_volume_pressure_20h,
        notes="rolling_mean(sign(delta(close, 1)) * volume, 20); directional volume pressure",
    ),
    # PM-45: Batch02 — Alpha158-derived single factor
    FactorSpec(
        factor_id="up_down_vol_ratio_20h", family="alpha158_ohlcv",
        required_columns=["close", "volume"], lookback_window=20,
        expected_direction="positive",
        compute_fn=_compute_up_down_vol_ratio_20h,
        notes="sum(vol*(ret>0),20)/sum(vol,20); buying pressure ratio; higher = bullish volume dominance",
    ),
    FactorSpec(
        factor_id="xs_rank_mom_accel", family="cross_sectional_normalized",
        required_columns=["close"], lookback_window=25,
        expected_direction="positive",
        compute_fn=_compute_xs_rank_mom_accel_prep,
        notes="Per-symbol momentum acceleration (mom_20h - delay(mom_20h, 5)); cross-sectional rank applied by caller",
    ),
    # PM-47: Batch03 — Alpha158 OHLC range/location factor
    FactorSpec(
        factor_id="clv_20h", family="alpha158_ohlc_range",
        required_columns=["high", "low", "close"], lookback_window=20,
        expected_direction="positive",
        compute_fn=_compute_clv_20h,
        notes="mean(((close-low)-(high-close))/(high-low+eps), 20); Close Location Value; +1=close at high, -1=close at low",
    ),
    # ── Alpha101 Curated Panel Factors (4h→1h time-equivalent migration) ──
    FactorSpec(
        factor_id="a101_volume_xs_z_mean_neg_112h", family="alpha101_curated_volume_crowding",
        required_columns=["volume"], lookback_window=112,
        expected_direction="positive",
        status="DIAGNOSTIC_PROBE",
        notes="-rolling_mean(xs_zscore(volume), 112); low relative-volume / low crowding; migrated from alpha101 volume_zscore_mean_neg_28",
        compute_scope="panel",
        panel_compute_fn=lambda bars: __import__('alpha101_panel_ops').compute_a101_volume_xs_z_mean_neg_112h(bars),
    ),
    FactorSpec(
        factor_id="a101_vol_xs_z_product_112h", family="alpha101_curated_volume_regime",
        required_columns=["volume"], lookback_window=112,
        expected_direction="conditional",
        status="DIAGNOSTIC_PROBE",
        notes="rolling_product(xs_zscore(volume), 112); nonlinear persistent volume-regime detector; mathematically awkward; migrated from alpha101 vol_zscore_product_28",
        compute_scope="panel",
        panel_compute_fn=lambda bars: __import__('alpha101_panel_ops').compute_a101_vol_xs_z_product_112h(bars),
    ),
    FactorSpec(
        factor_id="a101_volume_low_alpha_min_84_120", family="alpha101_curated_volume_price_regression",
        required_columns=["volume", "low"], lookback_window=203,
        expected_direction="conditional",
        status="DIAGNOSTIC_PROBE",
        notes="rolling_min(ts_alpha(volume, xs_winsorize(low), 84), 120); volume-adjusted low-price stress; migrated from alpha101 volume_low_alpha_min_21_30",
        compute_scope="panel",
        panel_compute_fn=lambda bars: __import__('alpha101_panel_ops').compute_a101_volume_low_alpha_min_84_120(bars),
    ),
    FactorSpec(
        factor_id="a101_volume_cap_alpha_min_80_80", family="alpha101_curated_volume_cap_regression",
        required_columns=["volume", "cap"], lookback_window=159,
        expected_direction="conditional",
        status="DIAGNOSTIC_PROBE",
        notes="rolling_min(ts_alpha(volume, cap, 80), 80); volume-cap relation; Requires market_cap_1h_aligned.parquet merged as cap. cap = underlying coin USD market cap, not futures quote_volume proxy. migrated from alpha101 volume_cap_alpha_min_20_20",
        compute_scope="panel",
        panel_compute_fn=lambda bars: __import__('alpha101_panel_ops').compute_a101_volume_cap_alpha_min_80_80(bars),
    ),
    FactorSpec(
        factor_id="a101_volume_cap_alpha_min_56_84", family="alpha101_curated_volume_cap_regression",
        required_columns=["volume", "cap"], lookback_window=139,
        expected_direction="conditional",
        status="DIAGNOSTIC_PROBE",
        notes="rolling_min(ts_alpha(volume, cap, 56), 84); faster volume-cap relation; Requires market_cap_1h_aligned.parquet merged as cap. cap = underlying coin USD market cap, not futures quote_volume proxy. migrated from alpha101 volume_cap_alpha_min_14_21",
        compute_scope="panel",
        panel_compute_fn=lambda bars: __import__('alpha101_panel_ops').compute_a101_volume_cap_alpha_min_56_84(bars),
    ),
    FactorSpec(
        factor_id="a101_volume_high_alpha_min_84_84", family="alpha101_curated_volume_price_regression",
        required_columns=["volume", "high"], lookback_window=167,
        expected_direction="conditional",
        status="DIAGNOSTIC_PROBE",
        notes="rolling_min(ts_alpha(volume, high, 84), 84); volume-adjusted high-price compression; migrated from alpha101 volume_high_alpha_min_21_21",
        compute_scope="panel",
        panel_compute_fn=lambda bars: __import__('alpha101_panel_ops').compute_a101_volume_high_alpha_min_84_84(bars),
    ),
]

# Quick lookup by factor_id
REGISTRY_BY_ID: dict[str, FactorSpec] = {fs.factor_id: fs for fs in REGISTRY}
