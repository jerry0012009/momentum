"""Endpoint / non-repainting Nadaraya-Watson smoothing.

Design goals:
- only use data that exists at calculation time (current + past)
- keep implementation lightweight (numpy + pandas only)
- return per-bar smoothed values that are prefix-stable under walk-forward recomputation

This module intentionally implements the endpoint / causal variant, not the
classic double-sided smoother used in many charting demos.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class EndpointNadarayaWatsonConfig:
    source_column: str = "close"
    bandwidth: float = 8.0
    lookback: int = 200
    result_column: str = "nw_smooth"


REQUIRED_COLUMNS = ["timestamp"]


def _validate_df(df: pd.DataFrame, config: EndpointNadarayaWatsonConfig) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    if config.source_column not in df.columns:
        raise ValueError(f"Missing required columns: ['{config.source_column}']")


def _validate_config(config: EndpointNadarayaWatsonConfig) -> None:
    if config.bandwidth <= 0:
        raise ValueError("bandwidth must be > 0")
    if config.lookback <= 0:
        raise ValueError("lookback must be > 0")


def _gauss(distance: np.ndarray, bandwidth: float) -> np.ndarray:
    return np.exp(-((distance**2) / (2.0 * bandwidth * bandwidth)))


def _compute_single_symbol(df: pd.DataFrame, config: EndpointNadarayaWatsonConfig) -> pd.DataFrame:
    out = df.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True)
    out = out.sort_values("timestamp").reset_index(drop=True)

    src = out[config.source_column].astype(float).to_numpy()
    n = len(src)
    max_k = min(config.lookback, n)
    weights = _gauss(np.arange(max_k, dtype=float), config.bandwidth)

    smoothed = np.full(n, np.nan, dtype=float)

    for t in range(n):
        available = min(t + 1, max_k)
        w = weights[:available]
        values = src[t - available + 1 : t + 1][::-1]
        denom = float(np.nansum(w))
        if denom <= 0:
            continue
        smoothed[t] = float(np.nansum(values * w) / denom)

    out[config.result_column] = smoothed
    return out


def compute_endpoint_nadaraya_watson(
    bars: pd.DataFrame,
    *,
    config: EndpointNadarayaWatsonConfig = EndpointNadarayaWatsonConfig(),
) -> pd.DataFrame:
    """Compute endpoint / causal Nadaraya-Watson smoothing.

    Expected columns:
    - timestamp
    - config.source_column (default: close)
    Optional:
    - symbol (per-symbol grouped computation)
    """

    _validate_df(bars, config)
    _validate_config(config)

    df = bars.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    if "symbol" in df.columns:
        df = df.sort_values(["symbol", "timestamp"]).reset_index(drop=True)
        parts: list[pd.DataFrame] = []
        for _, g in df.groupby("symbol", sort=True):
            parts.append(_compute_single_symbol(g.reset_index(drop=True), config))
        out = pd.concat(parts, ignore_index=True)
    else:
        out = _compute_single_symbol(df, config)

    out["timestamp"] = out["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return out


__all__ = [
    "EndpointNadarayaWatsonConfig",
    "compute_endpoint_nadaraya_watson",
]
