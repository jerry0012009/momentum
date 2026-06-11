"""Confirmed extrema detection on a causal / walk-forward basis.

The center point may lie in the past, but the extremum only becomes usable on
its confirmation bar:
    confirm_bar = center_bar + neighbor_bars

This keeps the output compatible with live / walk-forward evaluation and avoids
using data that was not available at the calculation time.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ConfirmedExtremaConfig:
    value_column: str = "nw_smooth"
    neighbor_bars: int = 5
    anchor_high_column: str | None = "high"
    anchor_low_column: str | None = "low"
    anchor_window_bars: int | None = None
    bar_index_column: str = "bar_index"
    high_flag_column: str = "confirmed_high"
    low_flag_column: str = "confirmed_low"
    high_value_column: str = "confirmed_high_value"
    low_value_column: str = "confirmed_low_value"
    high_origin_index_column: str = "confirmed_high_origin_index"
    low_origin_index_column: str = "confirmed_low_origin_index"
    high_structure_column: str = "confirmed_high_structure"
    low_structure_column: str = "confirmed_low_structure"


REQUIRED_COLUMNS = ["timestamp"]


def _validate_df(df: pd.DataFrame, config: ConfirmedExtremaConfig) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    required = [config.value_column]
    if config.anchor_high_column is not None:
        required.append(config.anchor_high_column)
    if config.anchor_low_column is not None:
        required.append(config.anchor_low_column)

    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def _validate_config(config: ConfirmedExtremaConfig) -> None:
    if config.neighbor_bars <= 0:
        raise ValueError("neighbor_bars must be > 0")
    if config.anchor_window_bars is not None and config.anchor_window_bars < 0:
        raise ValueError("anchor_window_bars must be >= 0")


def _is_confirmed_high(values: np.ndarray, center: int, neighbor_bars: int) -> bool:
    v = values[center]
    if not np.isfinite(v):
        return False
    left = values[center - neighbor_bars : center]
    right = values[center + 1 : center + neighbor_bars + 1]
    if len(left) != neighbor_bars or len(right) != neighbor_bars:
        return False
    if not np.isfinite(left).all() or not np.isfinite(right).all():
        return False
    return bool(np.all(v > left) and np.all(v > right))


def _is_confirmed_low(values: np.ndarray, center: int, neighbor_bars: int) -> bool:
    v = values[center]
    if not np.isfinite(v):
        return False
    left = values[center - neighbor_bars : center]
    right = values[center + 1 : center + neighbor_bars + 1]
    if len(left) != neighbor_bars or len(right) != neighbor_bars:
        return False
    if not np.isfinite(left).all() or not np.isfinite(right).all():
        return False
    return bool(np.all(v < left) and np.all(v < right))


def _anchor_high(
    raw_high: np.ndarray,
    center: int,
    window_bars: int,
) -> tuple[int, float]:
    start = max(0, center - window_bars)
    end = min(len(raw_high), center + window_bars + 1)
    window = raw_high[start:end]
    if len(window) == 0 or not np.isfinite(window).any():
        return center, float("nan")
    rel_idx = int(np.nanargmax(window))
    idx = start + rel_idx
    return idx, float(raw_high[idx])


def _anchor_low(
    raw_low: np.ndarray,
    center: int,
    window_bars: int,
) -> tuple[int, float]:
    start = max(0, center - window_bars)
    end = min(len(raw_low), center + window_bars + 1)
    window = raw_low[start:end]
    if len(window) == 0 or not np.isfinite(window).any():
        return center, float("nan")
    rel_idx = int(np.nanargmin(window))
    idx = start + rel_idx
    return idx, float(raw_low[idx])


def _compute_single_symbol(df: pd.DataFrame, config: ConfirmedExtremaConfig) -> pd.DataFrame:
    out = df.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True)
    out = out.sort_values("timestamp").reset_index(drop=True)
    out[config.bar_index_column] = np.arange(len(out), dtype=int)

    out[config.high_flag_column] = 0
    out[config.low_flag_column] = 0
    out[config.high_value_column] = np.nan
    out[config.low_value_column] = np.nan
    out[config.high_origin_index_column] = np.nan
    out[config.low_origin_index_column] = np.nan
    out[config.high_structure_column] = ""
    out[config.low_structure_column] = ""

    values = out[config.value_column].astype(float).to_numpy()
    raw_high = (
        out[config.anchor_high_column].astype(float).to_numpy()
        if config.anchor_high_column is not None
        else values
    )
    raw_low = (
        out[config.anchor_low_column].astype(float).to_numpy()
        if config.anchor_low_column is not None
        else values
    )
    anchor_window = config.neighbor_bars if config.anchor_window_bars is None else config.anchor_window_bars

    last_high_value: float | None = None
    last_low_value: float | None = None

    for center in range(config.neighbor_bars, len(out) - config.neighbor_bars):
        confirm_bar = center + config.neighbor_bars

        if _is_confirmed_high(values, center, config.neighbor_bars):
            anchor_idx, anchor_value = _anchor_high(raw_high, center, anchor_window)
            out.at[confirm_bar, config.high_flag_column] = 1
            out.at[confirm_bar, config.high_value_column] = anchor_value
            out.at[confirm_bar, config.high_origin_index_column] = int(anchor_idx)
            if last_high_value is not None:
                out.at[
                    confirm_bar,
                    config.high_structure_column,
                ] = "HH" if anchor_value > last_high_value else "LH"
            last_high_value = anchor_value

        if _is_confirmed_low(values, center, config.neighbor_bars):
            anchor_idx, anchor_value = _anchor_low(raw_low, center, anchor_window)
            out.at[confirm_bar, config.low_flag_column] = 1
            out.at[confirm_bar, config.low_value_column] = anchor_value
            out.at[confirm_bar, config.low_origin_index_column] = int(anchor_idx)
            if last_low_value is not None:
                out.at[
                    confirm_bar,
                    config.low_structure_column,
                ] = "HL" if anchor_value > last_low_value else "LL"
            last_low_value = anchor_value

    return out


def compute_confirmed_extrema(
    bars: pd.DataFrame,
    *,
    config: ConfirmedExtremaConfig = ConfirmedExtremaConfig(),
) -> pd.DataFrame:
    """Detect confirmed extrema on one or multiple symbols."""

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
    "ConfirmedExtremaConfig",
    "compute_confirmed_extrema",
]
