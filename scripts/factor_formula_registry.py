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
    rolling_corr, zscore, ema, true_range,
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
        expected_direction="negative",
        compute_fn=_compute_rev_3h,
        notes="-(close / close_3h_ago - 1)",
    ),
    FactorSpec(
        factor_id="rev_10h", family="reversal",
        required_columns=["close"], lookback_window=10,
        expected_direction="negative",
        compute_fn=_compute_rev_10h,
        notes="-(close / close_10h_ago - 1)",
    ),
    FactorSpec(
        factor_id="rev_24h", family="reversal",
        required_columns=["close"], lookback_window=24,
        expected_direction="negative",
        compute_fn=_compute_rev_24h,
        notes="-(close / close_24h_ago - 1)",
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
]

# Quick lookup by factor_id
REGISTRY_BY_ID: dict[str, FactorSpec] = {fs.factor_id: fs for fs in REGISTRY}
