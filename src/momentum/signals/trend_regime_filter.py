"""Trend/chop regime gate on top of multi-timeframe momentum.

Idea:
- Base entry comes from multi-timeframe momentum.
- A separate regime gate decides whether the market has enough directional strength
  and not too much noise.
- Gate is symmetric for long / short; it filters environment, not direction.

Baseline regime metrics:
- ret[t] = close[t] / close[t-1] - 1
- trend_return[t] = close[t] / close[t-N] - 1
- trend_strength[t] = abs(trend_return[t])
- noise_level[t] = rolling_std(ret, N)
- regime_score[t] = trend_strength[t] / noise_level[t]

Pass condition:
- trend_strength > trend_threshold
- regime_score > regime_score_threshold
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .multi_tf_momentum import MultiTfMomentumConfig, compute_multi_tf_momentum_signals


REQUIRED_COLUMNS = ["timestamp", "close"]


@dataclass(frozen=True)
class TrendRegimeFilterConfig:
    # base trend / baseline momentum
    window_5m: int = 6
    window_15m: int = 6
    threshold_5m: float = 0.003
    threshold_15m: float = 0.006
    resample_rule_15m: str = "15min"

    # regime gate
    regime_window: int = 36
    trend_threshold: float = 0.015
    regime_score_threshold: float = 2.0


def _validate_df(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")



def _validate_config(config: TrendRegimeFilterConfig) -> None:
    if config.window_5m <= 0 or config.window_15m <= 0:
        raise ValueError("momentum windows must be > 0")
    if config.threshold_5m < 0 or config.threshold_15m < 0:
        raise ValueError("momentum thresholds must be >= 0")
    if config.regime_window <= 1:
        raise ValueError("regime_window must be > 1")
    if config.trend_threshold < 0:
        raise ValueError("trend_threshold must be >= 0")
    if config.regime_score_threshold < 0:
        raise ValueError("regime_score_threshold must be >= 0")



def _compute_single_symbol(df: pd.DataFrame, config: TrendRegimeFilterConfig) -> pd.DataFrame:
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

    out["ret_1"] = out["close"].pct_change()
    out["trend_return"] = out["close"] / out["close"].shift(config.regime_window) - 1.0
    out["trend_strength"] = out["trend_return"].abs()
    out["noise_level"] = out["ret_1"].rolling(config.regime_window, min_periods=config.regime_window).std(ddof=0)
    out["regime_score"] = out["trend_strength"] / out["noise_level"].replace(0.0, np.nan)

    out["regime_filter_pass"] = (
        (out["trend_strength"] > config.trend_threshold)
        & (out["regime_score"] > config.regime_score_threshold)
    ).fillna(False).astype(int)

    out["long_signal"] = (
        (out["base_long_signal"] == 1)
        & (out["regime_filter_pass"] == 1)
    ).astype(int)
    out["short_signal"] = (
        (out["base_short_signal"] == 1)
        & (out["regime_filter_pass"] == 1)
    ).astype(int)

    out["long_filtered_out"] = (
        (out["base_long_signal"] == 1) & (out["long_signal"] == 0)
    ).astype(int)
    out["short_filtered_out"] = (
        (out["base_short_signal"] == 1) & (out["short_signal"] == 0)
    ).astype(int)

    return out



def compute_trend_regime_filter_signals(
    bars: pd.DataFrame,
    *,
    config: TrendRegimeFilterConfig = TrendRegimeFilterConfig(),
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
    "TrendRegimeFilterConfig",
    "compute_trend_regime_filter_signals",
]
