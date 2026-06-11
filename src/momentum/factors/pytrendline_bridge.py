"""Bridge wrapper around the external MIT-licensed `pytrendline` package.

Why this module exists:
- keep third-party logic isolated behind a small local API
- add pandas 3 compatibility for pytrendline (which still uses DataFrame.append)
- make runtime constraints explicit: pytrendline is expensive, so we use it on a
  recent analysis window instead of a full large intraday sample
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class PyTrendlineConfig:
    window_bars: int = 96
    min_points_required: int = 3
    ignore_breakouts: bool = False
    trend_type: str = "BOTH"
    first_pt_must_be_pivot: bool = False
    last_pt_must_be_pivot: bool = False
    all_pts_must_be_pivots: bool = True
    trendline_must_include_global_maxmin_pt: bool = False
    time_interval: str = "5m"


REQUIRED_COLUMNS = ["timestamp", "open", "high", "low", "close"]


def _validate_df(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def _validate_config(config: PyTrendlineConfig) -> None:
    if config.window_bars < 20:
        raise ValueError("window_bars must be >= 20")
    if config.min_points_required < 2:
        raise ValueError("min_points_required must be >= 2")


def _ensure_pytrendline_compat() -> Any:
    import pandas as pd

    if not hasattr(pd.DataFrame, "append"):
        def _append(self, other, ignore_index=False, verify_integrity=False, sort=False):
            if isinstance(other, dict):
                other = pd.DataFrame([other])
            return pd.concat([self, other], ignore_index=ignore_index, sort=sort)
        pd.DataFrame.append = _append  # type: ignore[attr-defined]

    import pytrendline
    return pytrendline


def _to_candles(df: pd.DataFrame, config: PyTrendlineConfig) -> pd.DataFrame:
    out = df.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True)
    out = out.sort_values("timestamp").tail(config.window_bars).reset_index(drop=True)
    return out.rename(
        columns={
            "timestamp": "Date",
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume",
        }
    )


def _normalize_trendlines(df: pd.DataFrame, candles: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if out.empty:
        return out

    if "breakout_index" in out.columns and "breakout_date" in out.columns:
        idx_series = pd.to_numeric(out["breakout_index"], errors="coerce")
        valid = idx_series.notna() & (idx_series >= 0) & (idx_series < len(candles))
        if valid.any():
            mapped_dates = idx_series[valid].astype(int).map(lambda i: candles.iloc[i]["Date"])
            out.loc[valid, "breakout_date"] = mapped_dates.values

    if "score" in out.columns:
        out.sort_values(["is_best_from_duplicate_group", "score"], ascending=[False, False], inplace=True)
        out.reset_index(drop=True, inplace=True)
    return out


def detect_pytrendlines(
    bars: pd.DataFrame,
    *,
    config: PyTrendlineConfig = PyTrendlineConfig(),
) -> dict[str, Any]:
    """Run pytrendline on a recent analysis window.

    Returns a dict with:
    - candles_df
    - support_pivots
    - resistance_pivots
    - support_trendlines
    - resistance_trendlines
    """

    _validate_df(bars)
    _validate_config(config)
    pytrendline = _ensure_pytrendline_compat()

    candles = _to_candles(bars, config)
    candlestick_data = pytrendline.CandlestickData(
        df=candles,
        time_interval=config.time_interval,
        open_col="Open",
        high_col="High",
        low_col="Low",
        close_col="Close",
        datetime_col="Date",
    )

    trend_type = getattr(pytrendline.TrendlineTypes, config.trend_type)
    result = pytrendline.detect(
        candlestick_data=candlestick_data,
        trend_type=trend_type,
        first_pt_must_be_pivot=config.first_pt_must_be_pivot,
        last_pt_must_be_pivot=config.last_pt_must_be_pivot,
        all_pts_must_be_pivots=config.all_pts_must_be_pivots,
        trendline_must_include_global_maxmin_pt=config.trendline_must_include_global_maxmin_pt,
        min_points_required=config.min_points_required,
        ignore_breakouts=config.ignore_breakouts,
    )

    support = _normalize_trendlines(result.get("support_trendlines", pd.DataFrame()), candles)
    resistance = _normalize_trendlines(result.get("resistance_trendlines", pd.DataFrame()), candles)

    return {
        "candles_df": candles,
        "support_pivots": sorted(result.get("support_pivots", [])),
        "resistance_pivots": sorted(result.get("resistance_pivots", [])),
        "support_trendlines": support,
        "resistance_trendlines": resistance,
    }


__all__ = [
    "PyTrendlineConfig",
    "detect_pytrendlines",
]
