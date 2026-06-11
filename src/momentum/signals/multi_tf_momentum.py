"""Multi-timeframe momentum signal implementation.

Definitions (at 5m bar close t):
- mom_5m(t)  = close_5m[t] / close_5m[t-M] - 1
- mom_15m(T) = close_15m[T] / close_15m[T-N] - 1
  where T is the latest completed 15m bar at or before t.

Signals:
- long_signal:  mom_5m > th_5m and mom_15m > th_15m
- short_signal: mom_5m < -th_5m and mom_15m < -th_15m

Provides:
- Pandas batch computation for offline feature generation.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


REQUIRED_COLUMNS = ["timestamp", "close"]


@dataclass(frozen=True)
class MultiTfMomentumConfig:
    window_5m: int = 6
    window_15m: int = 6
    threshold_5m: float = 0.0
    threshold_15m: float = 0.0
    resample_rule_15m: str = "15min"


def _validate_df(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def _validate_config(config: MultiTfMomentumConfig) -> None:
    if config.window_5m <= 0:
        raise ValueError("window_5m must be > 0")
    if config.window_15m <= 0:
        raise ValueError("window_15m must be > 0")
    if config.threshold_5m < 0:
        raise ValueError("threshold_5m must be >= 0")
    if config.threshold_15m < 0:
        raise ValueError("threshold_15m must be >= 0")


def _compute_single_symbol(df: pd.DataFrame, config: MultiTfMomentumConfig) -> pd.DataFrame:
    out = df.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True)
    out = out.sort_values(["timestamp"]).reset_index(drop=True)

    out["mom_5m"] = out["close"] / out["close"].shift(config.window_5m) - 1.0

    close_15m = (
        out.set_index("timestamp")[["close"]]
        .resample(config.resample_rule_15m, label="right", closed="right")
        .last()
        .dropna()
        .reset_index()
        .rename(columns={"close": "close_15m"})
    )
    close_15m["mom_15m"] = close_15m["close_15m"] / close_15m["close_15m"].shift(config.window_15m) - 1.0

    out = pd.merge_asof(
        out,
        close_15m[["timestamp", "mom_15m"]].sort_values("timestamp"),
        on="timestamp",
        direction="backward",
    )

    out["long_signal"] = (
        (out["mom_5m"] > config.threshold_5m) & (out["mom_15m"] > config.threshold_15m)
    ).fillna(False).astype(int)
    out["short_signal"] = (
        (out["mom_5m"] < -config.threshold_5m) & (out["mom_15m"] < -config.threshold_15m)
    ).fillna(False).astype(int)

    return out


def compute_multi_tf_momentum_signals(
    bars: pd.DataFrame,
    *,
    config: MultiTfMomentumConfig = MultiTfMomentumConfig(),
) -> pd.DataFrame:
    """Compute multi-timeframe momentum signals for one or multiple symbols.

    Expected columns:
    - timestamp, close
    Optional:
    - symbol (for per-symbol grouped computation)
    - any other columns are preserved in the output
    """

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
    "MultiTfMomentumConfig",
    "compute_multi_tf_momentum_signals",
]
