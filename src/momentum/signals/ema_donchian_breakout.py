"""EMA structure + Donchian breakout confirmation signals.

Learning baseline:
- Higher timeframe (1h) EMA structure defines direction bias.
- Lower timeframe (5m) Donchian breakout provides trigger.
- Consecutive close confirmation reduces short-term noise.

This module only generates entry signals. ATR stop / opposite-signal exit is handled in backtest.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


REQUIRED_COLUMNS = ["timestamp", "open", "high", "low", "close"]


@dataclass(frozen=True)
class EmaDonchianBreakoutConfig:
    market_resample_rule: str = "1h"
    ema_window_1h: int = 20
    donchian_lookback: int = 20
    confirm_bars: int = 3
    use_ema_slope: bool = True



def _validate_df(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")



def _validate_config(config: EmaDonchianBreakoutConfig) -> None:
    if config.ema_window_1h <= 1:
        raise ValueError("ema_window_1h must be > 1")
    if config.donchian_lookback <= 1:
        raise ValueError("donchian_lookback must be > 1")
    if config.confirm_bars <= 0:
        raise ValueError("confirm_bars must be > 0")



def _compute_single_symbol(df: pd.DataFrame, config: EmaDonchianBreakoutConfig) -> pd.DataFrame:
    out = df.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True)
    out = out.sort_values("timestamp").reset_index(drop=True)

    market = out[["timestamp", "close"]].copy().rename(columns={"close": "close_1h_src"}).set_index("timestamp")
    market = market.resample(config.market_resample_rule).last().dropna().reset_index()
    market["ema_1h"] = market["close_1h_src"].ewm(span=config.ema_window_1h, adjust=False).mean()
    market["ema_slope_up_1h"] = (market["ema_1h"] > market["ema_1h"].shift(1)).fillna(False).astype(int)
    market["ema_slope_down_1h"] = (market["ema_1h"] < market["ema_1h"].shift(1)).fillna(False).astype(int)

    out = pd.merge_asof(
        out.sort_values("timestamp"),
        market.sort_values("timestamp"),
        on="timestamp",
        direction="backward",
    )

    out["donchian_upper"] = out["high"].shift(1).rolling(config.donchian_lookback, min_periods=config.donchian_lookback).max()
    out["donchian_lower"] = out["low"].shift(1).rolling(config.donchian_lookback, min_periods=config.donchian_lookback).min()

    long_bias = (out["close_1h_src"] > out["ema_1h"]).fillna(False)
    short_bias = (out["close_1h_src"] < out["ema_1h"]).fillna(False)
    if config.use_ema_slope:
        long_bias = long_bias & (out["ema_slope_up_1h"] == 1)
        short_bias = short_bias & (out["ema_slope_down_1h"] == 1)
    out["long_bias"] = long_bias.astype(int)
    out["short_bias"] = short_bias.astype(int)

    out["close_above_upper"] = (out["close"] > out["donchian_upper"]).fillna(False).astype(int)
    out["close_below_lower"] = (out["close"] < out["donchian_lower"]).fillna(False).astype(int)

    out["long_confirm"] = (
        out["close_above_upper"].rolling(config.confirm_bars, min_periods=config.confirm_bars).sum() == config.confirm_bars
    ).fillna(False).astype(int)
    out["short_confirm"] = (
        out["close_below_lower"].rolling(config.confirm_bars, min_periods=config.confirm_bars).sum() == config.confirm_bars
    ).fillna(False).astype(int)

    long_ready = (out["long_bias"] == 1) & (out["long_confirm"] == 1)
    short_ready = (out["short_bias"] == 1) & (out["short_confirm"] == 1)

    out["long_signal"] = (long_ready & (~long_ready.shift(1).fillna(False))).astype(int)
    out["short_signal"] = (short_ready & (~short_ready.shift(1).fillna(False))).astype(int)

    return out



def compute_ema_donchian_breakout_signals(
    bars: pd.DataFrame,
    *,
    config: EmaDonchianBreakoutConfig = EmaDonchianBreakoutConfig(),
) -> pd.DataFrame:
    _validate_df(bars)
    _validate_config(config)

    df = bars.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    if "symbol" in df.columns:
        df = df.sort_values(["symbol", "timestamp"]).reset_index(drop=True)
        parts = []
        for _, g in df.groupby("symbol", sort=True):
            parts.append(_compute_single_symbol(g.reset_index(drop=True), config))
        out = pd.concat(parts, ignore_index=True)
    else:
        out = _compute_single_symbol(df, config)

    out["timestamp"] = out["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return out


__all__ = [
    "EmaDonchianBreakoutConfig",
    "compute_ema_donchian_breakout_signals",
]
