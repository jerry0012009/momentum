"""Pullback + recovery confirmation signals on top of multi-timeframe momentum.

Idea:
- Base trend comes from multi-timeframe momentum (5m / 15m).
- In an uptrend, require a recent pullback on weak volume, then a recovery breakout on strong volume.
- Symmetric logic applies for downtrend / short signals.

This module is intended as a research signal layer for studying whether
"缩量回调 + 放量恢复" improves signal quality versus naked momentum.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .multi_tf_momentum import MultiTfMomentumConfig, compute_multi_tf_momentum_signals


REQUIRED_COLUMNS = ["timestamp", "high", "low", "close", "volume"]


@dataclass(frozen=True)
class PullbackRecoveryConfirmationConfig:
    # base trend / baseline momentum
    window_5m: int = 6
    window_15m: int = 6
    threshold_5m: float = 0.003
    threshold_15m: float = 0.006
    resample_rule_15m: str = "15min"

    # volume anomaly
    vol_window: int = 20

    # confirmation structure
    pullback_lookback: int = 2
    pullback_vol_z_max: float = 0.0
    vol_recover_th: float = 1.0
    breakout_lookback: int = 1


def _validate_df(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def _validate_config(config: PullbackRecoveryConfirmationConfig) -> None:
    if config.window_5m <= 0 or config.window_15m <= 0:
        raise ValueError("momentum windows must be > 0")
    if config.vol_window <= 1:
        raise ValueError("vol_window must be > 1")
    if config.pullback_lookback <= 0:
        raise ValueError("pullback_lookback must be > 0")
    if config.breakout_lookback <= 0:
        raise ValueError("breakout_lookback must be > 0")
    if config.threshold_5m < 0 or config.threshold_15m < 0:
        raise ValueError("momentum thresholds must be >= 0")


def _compute_single_symbol(df: pd.DataFrame, config: PullbackRecoveryConfirmationConfig) -> pd.DataFrame:
    out = df.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True)
    out = out.sort_values(["timestamp"]).reset_index(drop=True)

    base = compute_multi_tf_momentum_signals(
        out,
        config=MultiTfMomentumConfig(
            window_5m=config.window_5m,
            window_15m=config.window_15m,
            threshold_5m=config.threshold_5m,
            threshold_15m=config.threshold_15m,
            resample_rule_15m=config.resample_rule_15m,
        ),
    )
    base["timestamp"] = pd.to_datetime(base["timestamp"], utc=True)
    out = out.merge(
        base[["timestamp", "mom_5m", "mom_15m", "long_signal", "short_signal"]].rename(
            columns={"long_signal": "base_long_signal", "short_signal": "base_short_signal"}
        ),
        on="timestamp",
        how="left",
    )

    vol_mean = out["volume"].rolling(config.vol_window, min_periods=config.vol_window).mean()
    vol_std = out["volume"].rolling(config.vol_window, min_periods=config.vol_window).std(ddof=0).replace(0.0, np.nan)
    out["vol_z"] = (out["volume"] - vol_mean) / vol_std

    down_bar = out["close"].diff() < 0
    up_bar = out["close"].diff() > 0

    down_count = down_bar.shift(1).rolling(config.pullback_lookback, min_periods=1).sum()
    up_count = up_bar.shift(1).rolling(config.pullback_lookback, min_periods=1).sum()

    down_vol_mean = out["vol_z"].where(down_bar).shift(1).rolling(config.pullback_lookback, min_periods=1).mean()
    up_vol_mean = out["vol_z"].where(up_bar).shift(1).rolling(config.pullback_lookback, min_periods=1).mean()

    out["long_pullback_ok"] = ((down_count > 0) & (down_vol_mean < config.pullback_vol_z_max)).fillna(False).astype(int)
    out["short_pullback_ok"] = ((up_count > 0) & (up_vol_mean < config.pullback_vol_z_max)).fillna(False).astype(int)

    out["breakout_ref_high"] = out["high"].shift(1).rolling(config.breakout_lookback, min_periods=config.breakout_lookback).max()
    out["breakout_ref_low"] = out["low"].shift(1).rolling(config.breakout_lookback, min_periods=config.breakout_lookback).min()

    out["long_recovery_ok"] = (
        (out["close"] > out["breakout_ref_high"]) & (out["vol_z"] > config.vol_recover_th)
    ).fillna(False).astype(int)
    out["short_recovery_ok"] = (
        (out["close"] < out["breakout_ref_low"]) & (out["vol_z"] > config.vol_recover_th)
    ).fillna(False).astype(int)

    out["long_signal"] = (
        (out["base_long_signal"] == 1)
        & (out["long_pullback_ok"] == 1)
        & (out["long_recovery_ok"] == 1)
    ).astype(int)
    out["short_signal"] = (
        (out["base_short_signal"] == 1)
        & (out["short_pullback_ok"] == 1)
        & (out["short_recovery_ok"] == 1)
    ).astype(int)

    return out


def compute_pullback_recovery_confirmation_signals(
    bars: pd.DataFrame,
    *,
    config: PullbackRecoveryConfirmationConfig = PullbackRecoveryConfirmationConfig(),
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
    "PullbackRecoveryConfirmationConfig",
    "compute_pullback_recovery_confirmation_signals",
]
