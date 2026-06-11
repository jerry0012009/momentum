"""Box consolidation / accumulation signal.

This module translates discretionary concepts into systematic rules for
index/stock markets:

1) Narrow consolidation accumulation (窄幅震荡建仓)
2) Box-range breakout accumulation (箱体震荡突破建仓)

Core ideas (mainstream mapping):
- "下跌后进入箱体" -> prior downtrend via rolling drawdown threshold.
- "窄幅震荡" -> low normalized range + low ATR ratio (volatility contraction).
- "箱体震荡" -> Donchian-like range, with swing non-break structure.
- "突破箱体最高点" -> bullish close breakout above prior box high.

Output signals:
- narrow_accum_ready: narrow-range accumulation confirmed.
- box_breakout_ready: wide-box structure + breakout confirmed.
- accumulation_ready: union of the above two (entry-ready state).
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .up_down_wave import UpDownWaveConfig, compute_up_down_wave_signals


REQUIRED_COLUMNS = ["open", "high", "low", "close"]


@dataclass(frozen=True)
class BoxConsolidationConfig:
    # Reuse Up/Down wave for structure confirmation.
    ma_period: int = 20

    # "进入箱体前一波下跌"
    decline_lookback: int = 60
    min_decline_pct: float = 0.12
    decline_recent_window: int = 20

    # "至少5日收盘高于历史阴线最低点"
    bearish_floor_lookback: int = 120
    floor_hold_days: int = 5

    # "窄幅震荡" proxy
    narrow_box_lookback: int = 20
    narrow_range_max: float = 0.08
    atr_period: int = 14
    narrow_atr_ratio_max: float = 0.025

    # "上涨浪信号确立"
    upwave_recent_window: int = 20

    # "箱体震荡" + 突破
    box_lookback: int = 30
    box_range_min: float = 0.08
    box_range_max: float = 0.30
    breakout_buffer: float = 0.0

    # Optional chip filter (if chip fields exist in bars)
    require_chip_filter: bool = False
    chip_winner_min: float = 0.30
    chip_winner_max: float = 0.80


def _validate_df(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def _atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int) -> pd.Series:
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.rolling(period, min_periods=period).mean()


def _event_non_break(close: pd.Series, event_flag: pd.Series, *, direction: str) -> pd.Series:
    """Compare latest event close with previous event close.

    direction='up': latest <= previous (no new higher high)
    direction='down': latest >= previous (no new lower low)
    """

    event_close = close.where(event_flag)
    prev_event_close = event_close.ffill().shift(1)

    if direction == "up":
        cond_on_event = event_close <= prev_event_close
    elif direction == "down":
        cond_on_event = event_close >= prev_event_close
    else:
        raise ValueError(f"Unknown direction: {direction}")

    # Keep the latest known event-state between event points.
    return cond_on_event.where(event_flag).ffill().fillna(False)


def _chip_ok(df: pd.DataFrame, cfg: BoxConsolidationConfig) -> pd.Series:
    if not cfg.require_chip_filter:
        return pd.Series(True, index=df.index)

    if "chip_bottom_locked" in df.columns:
        return df["chip_bottom_locked"].fillna(0).astype(int).astype(bool)

    if "winner_ratio" in df.columns:
        return df["winner_ratio"].astype(float).between(cfg.chip_winner_min, cfg.chip_winner_max, inclusive="both")

    # require_chip_filter=True but no usable chip columns.
    return pd.Series(False, index=df.index)


def compute_box_consolidation_signals(
    bars: pd.DataFrame,
    *,
    config: BoxConsolidationConfig = BoxConsolidationConfig(),
) -> pd.DataFrame:
    """Compute narrow-box and box-breakout accumulation signals.

    Expected columns:
    - open, high, low, close
    Optional:
    - timestamp (for sorting)
    - symbol (panel mode)
    - upwave/downwave (if absent, generated from UpDownWave)
    - chip_bottom_locked or winner_ratio (optional chip filter)
    """

    _validate_df(bars)

    df = bars.copy()
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    if "symbol" in df.columns:
        sort_cols = ["symbol"] + (["timestamp"] if "timestamp" in df.columns else [])
        df = df.sort_values(sort_cols).reset_index(drop=True)
        out_parts = []
        for _, g in df.groupby("symbol", sort=True):
            out_parts.append(_compute_single_symbol(g.reset_index(drop=True), config))
        out = pd.concat(out_parts, ignore_index=True)
    else:
        if "timestamp" in df.columns:
            df = df.sort_values(["timestamp"]).reset_index(drop=True)
        out = _compute_single_symbol(df, config)

    if "timestamp" in out.columns:
        out["timestamp"] = out["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    return out


def _compute_single_symbol(df: pd.DataFrame, cfg: BoxConsolidationConfig) -> pd.DataFrame:
    out = df.copy()

    # Ensure upwave/downwave exist.
    if ("upwave" not in out.columns) or ("downwave" not in out.columns):
        udw = compute_up_down_wave_signals(out, config=UpDownWaveConfig(ma_period=cfg.ma_period))
        out["upwave"] = udw["upwave"].astype(int)
        out["downwave"] = udw["downwave"].astype(int)

    # 1) prior decline before box.
    rolling_peak = out["close"].rolling(cfg.decline_lookback, min_periods=max(10, cfg.decline_lookback // 2)).max()
    out["drawdown_from_peak"] = out["close"] / rolling_peak - 1.0
    prior_decline = out["drawdown_from_peak"] <= (-cfg.min_decline_pct)
    out["prior_decline_recent"] = (
        prior_decline.rolling(cfg.decline_recent_window, min_periods=1).max().fillna(0).astype(int)
    )

    # 2) floor from bearish-candle lows.
    bearish_low = out["low"].where(out["close"] < out["open"])
    out["bearish_floor"] = bearish_low.rolling(cfg.bearish_floor_lookback, min_periods=1).min().ffill()
    out["close_above_bearish_floor"] = (out["close"] > out["bearish_floor"]).fillna(False).astype(int)
    out["floor_hold_ok"] = (
        out["close_above_bearish_floor"].rolling(cfg.floor_hold_days, min_periods=cfg.floor_hold_days).sum() >= cfg.floor_hold_days
    ).fillna(False).astype(int)

    # 3) narrow consolidation proxy.
    nh = out["high"].rolling(cfg.narrow_box_lookback, min_periods=cfg.narrow_box_lookback).max()
    nl = out["low"].rolling(cfg.narrow_box_lookback, min_periods=cfg.narrow_box_lookback).min()
    out["narrow_box_width"] = (nh - nl) / nl

    out["atr"] = _atr(out["high"], out["low"], out["close"], cfg.atr_period)
    out["atr_ratio"] = out["atr"] / out["close"]

    out["narrow_box_ok"] = (
        (out["narrow_box_width"] <= cfg.narrow_range_max)
        & (out["atr_ratio"] <= cfg.narrow_atr_ratio_max)
    ).fillna(False).astype(int)

    out["upwave_recent"] = (
        out["upwave"].rolling(cfg.upwave_recent_window, min_periods=1).max().fillna(0).astype(int)
    )

    chip_ok = _chip_ok(out, cfg).fillna(False)
    out["chip_ok"] = chip_ok.astype(int)

    # Narrow accumulation ready.
    out["narrow_accum_ready"] = (
        (out["prior_decline_recent"] == 1)
        & (out["floor_hold_ok"] == 1)
        & (out["narrow_box_ok"] == 1)
        & (out["upwave_recent"] == 1)
        & chip_ok
    ).astype(int)

    # 4) Box consolidation (larger amplitude) + breakout.
    box_high_prev = out["high"].rolling(cfg.box_lookback, min_periods=cfg.box_lookback).max().shift(1)
    box_low_prev = out["low"].rolling(cfg.box_lookback, min_periods=cfg.box_lookback).min().shift(1)
    out["box_high_prev"] = box_high_prev
    out["box_low_prev"] = box_low_prev
    out["box_width"] = (box_high_prev - box_low_prev) / box_low_prev

    out["box_width_ok"] = (
        (out["box_width"] >= cfg.box_range_min)
        & (out["box_width"] <= cfg.box_range_max)
    ).fillna(False).astype(int)

    up_recent = out["upwave"].rolling(cfg.box_lookback, min_periods=1).max().fillna(0).astype(int)
    down_recent = out["downwave"].rolling(cfg.box_lookback, min_periods=1).max().fillna(0).astype(int)
    out["box_has_upwave"] = up_recent
    out["box_has_downwave"] = down_recent

    up_non_break = _event_non_break(out["close"], out["upwave"] == 1, direction="up")
    down_non_break = _event_non_break(out["close"], out["downwave"] == 1, direction="down")
    out["up_non_break"] = up_non_break.astype(int)
    out["down_non_break"] = down_non_break.astype(int)

    bullish = out["close"] > out["open"]
    breakout = bullish & (out["close"] > (box_high_prev * (1.0 + cfg.breakout_buffer)))
    out["box_breakout"] = breakout.fillna(False).astype(int)

    out["box_breakout_ready"] = (
        (out["prior_decline_recent"] == 1)
        & (out["box_has_upwave"] == 1)
        & (out["box_has_downwave"] == 1)
        & (out["down_non_break"] == 1)
        & (out["up_non_break"] == 1)
        & (out["box_width_ok"] == 1)
        & (out["box_breakout"] == 1)
        & chip_ok
    ).astype(int)

    out["accumulation_ready"] = ((out["narrow_accum_ready"] == 1) | (out["box_breakout_ready"] == 1)).astype(int)

    return out


__all__ = [
    "BoxConsolidationConfig",
    "compute_box_consolidation_signals",
]
