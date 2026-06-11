"""Chip distribution estimation utilities.

This module estimates cost-basis chip distribution from OHLCV bars.

Core update rule (discrete bins):
    C_t[i] = (1 - tau_t) * C_{t-1}[i] + tau_t * A_t[i]

Where:
- C_t[i] is chip proportion at price-bin i on day t
- tau_t is turnover ratio (volume / shares)
- A_t[i] is today's volume allocation over price bins
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

import numpy as np
import pandas as pd


REQUIRED_COLUMNS = ["timestamp", "symbol", "open", "high", "low", "close", "volume"]


@dataclass(frozen=True)
class ChipConfig:
    bin_size_pct: float = 0.005
    distribution: str = "triangular"  # triangular | uniform
    turnover_cap: float = 1.0
    min_price: float = 1e-8
    min_chip_pct: float = 1e-6

    def log_step(self) -> float:
        return math.log1p(self.bin_size_pct)


def _validate_inputs(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def _build_log_price_grid(
    min_price: float,
    max_price: float,
    step: float,
) -> tuple[np.ndarray, np.ndarray]:
    min_price = max(float(min_price), 1e-12)
    max_price = max(float(max_price), min_price * 1.0001)

    low_log = math.floor(math.log(min_price) / step) * step
    high_log = math.ceil(math.log(max_price) / step) * step

    edges_log = np.arange(low_log, high_log + step, step)
    if len(edges_log) < 2:
        edges_log = np.array([low_log, low_log + step], dtype=float)

    centers = np.exp((edges_log[:-1] + edges_log[1:]) / 2)
    return edges_log, centers


def _daily_allocation(
    low: float,
    high: float,
    close: float,
    centers: np.ndarray,
    distribution: str,
    min_price: float,
) -> np.ndarray:
    low = max(float(low), min_price)
    high = max(float(high), low)
    close = max(float(close), min_price)

    weights = np.zeros_like(centers, dtype=float)

    if high <= low:
        idx = int(np.argmin(np.abs(centers - close)))
        weights[idx] = 1.0
        return weights

    mask = (centers >= low) & (centers <= high)
    if not mask.any():
        idx = int(np.argmin(np.abs(centers - close)))
        weights[idx] = 1.0
        return weights

    x = centers[mask]

    if distribution == "uniform":
        w = np.ones_like(x)
    else:
        mode = (low + high + close) / 3.0
        mode = min(max(mode, low), high)

        # Degenerate triangular -> fallback to uniform
        if abs(mode - low) < 1e-12 or abs(high - mode) < 1e-12:
            w = np.ones_like(x)
        else:
            left = x <= mode
            w = np.zeros_like(x)
            w[left] = (x[left] - low) / (mode - low)
            w[~left] = (high - x[~left]) / (high - mode)
            w = np.clip(w, 0.0, None)
            if w.sum() <= 0:
                w = np.ones_like(x)

    w = w / w.sum()
    weights[mask] = w
    return weights


def _weighted_quantile(centers: np.ndarray, weights: np.ndarray, q: float) -> float:
    if weights.sum() <= 0:
        return float("nan")
    cdf = np.cumsum(weights)
    idx = int(np.searchsorted(cdf, q, side="left"))
    idx = min(max(idx, 0), len(centers) - 1)
    return float(centers[idx])


def estimate_chip_distribution_single(
    bars: pd.DataFrame,
    *,
    config: ChipConfig,
    shares: Iterable[float] | np.ndarray | pd.Series,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Estimate chip distribution for one symbol.

    Returns:
        (asset_distribution, normalized_distribution, daily_summary)
    """

    _validate_inputs(bars)

    df = bars.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values("timestamp").reset_index(drop=True)

    symbol = str(df["symbol"].iloc[0])

    shares_arr = np.asarray(list(shares), dtype=float)
    if len(shares_arr) != len(df):
        raise ValueError(f"shares length {len(shares_arr)} != rows {len(df)}")

    step = config.log_step()
    min_p = max(config.min_price, float(df["low"].min()))
    max_p = max(float(df["high"].max()), min_p * 1.01)
    edges_log, centers = _build_log_price_grid(min_p, max_p, step)

    chips = np.zeros_like(centers, dtype=float)

    dist_records: list[dict] = []
    summary_records: list[dict] = []

    for i, row in df.iterrows():
        low = float(row["low"])
        high = float(row["high"])
        close = float(row["close"])
        volume = float(row["volume"])
        sh = float(shares_arr[i])

        if not np.isfinite(sh) or sh <= 0:
            tau = 0.0
        else:
            tau = volume / sh

        if not np.isfinite(tau):
            tau = 0.0
        tau = float(np.clip(tau, 0.0, config.turnover_cap))

        alloc = _daily_allocation(
            low=low,
            high=high,
            close=close,
            centers=centers,
            distribution=config.distribution,
            min_price=config.min_price,
        )

        if i == 0:
            chips = alloc.copy()
        else:
            chips = (1.0 - tau) * chips + tau * alloc
            s = chips.sum()
            if s > 0:
                chips = chips / s

        keep = chips >= config.min_chip_pct
        idxs = np.where(keep)[0]
        ts = row["timestamp"]
        ts_iso = ts.strftime("%Y-%m-%dT%H:%M:%SZ")

        for idx in idxs:
            dist_records.append(
                {
                    "timestamp": ts_iso,
                    "symbol": symbol,
                    "price_bin": float(centers[idx]),
                    "chip_pct": float(chips[idx]),
                }
            )

        avg_cost = float(np.sum(chips * centers))
        p50 = _weighted_quantile(centers, chips, 0.50)
        p90 = _weighted_quantile(centers, chips, 0.90)
        winner_ratio = float(chips[centers <= close].sum())

        summary_records.append(
            {
                "timestamp": ts_iso,
                "symbol": symbol,
                "close": close,
                "shares": sh,
                "turnover": tau,
                "avg_cost": avg_cost,
                "cost_p50": p50,
                "cost_p90": p90,
                "winner_ratio": winner_ratio,
                "trapped_ratio": float(1.0 - winner_ratio),
            }
        )

    asset_df = pd.DataFrame(dist_records)
    summary_df = pd.DataFrame(summary_records)

    if asset_df.empty:
        norm_df = pd.DataFrame(columns=["timestamp", "symbol", "moneyness_bin", "chip_pct"])
        return asset_df, norm_df, summary_df

    close_map = summary_df.set_index(["timestamp", "symbol"])["close"]
    close_values = asset_df.set_index(["timestamp", "symbol"]).index.map(close_map)
    rel_log = np.log(asset_df["price_bin"].to_numpy() / np.asarray(close_values, dtype=float))

    moneyness_bin = np.round(rel_log / step) * step
    norm_df = asset_df.copy()
    norm_df["moneyness_bin"] = moneyness_bin
    norm_df = (
        norm_df.groupby(["timestamp", "symbol", "moneyness_bin"], as_index=False)["chip_pct"].sum()
        .sort_values(["timestamp", "symbol", "moneyness_bin"]) 
        .reset_index(drop=True)
    )

    return asset_df, norm_df, summary_df


def estimate_chip_distribution_panel(
    bars: pd.DataFrame,
    *,
    config: ChipConfig,
    shares_by_symbol: dict[str, float] | None = None,
    default_shares: float | None = None,
    shares_col: str | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Estimate chip distribution for one or multiple symbols.

    shares priority:
    1) shares_col in bars (per-row)
    2) shares_by_symbol[symbol]
    3) default_shares
    """

    _validate_inputs(bars)
    shares_by_symbol = shares_by_symbol or {}

    df = bars.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values(["symbol", "timestamp"]).reset_index(drop=True)

    all_asset = []
    all_norm = []
    all_summary = []

    for symbol, g in df.groupby("symbol", sort=True):
        g = g.sort_values("timestamp").reset_index(drop=True)

        shares_series: pd.Series
        if shares_col and shares_col in g.columns and g[shares_col].notna().any():
            shares_series = g[shares_col].astype(float).ffill().bfill()
        elif symbol in shares_by_symbol:
            shares_series = pd.Series([float(shares_by_symbol[symbol])] * len(g))
        elif default_shares is not None:
            shares_series = pd.Series([float(default_shares)] * len(g))
        else:
            raise ValueError(
                f"Missing shares for symbol={symbol}. Provide shares_col or shares_by_symbol/default_shares."
            )

        asset_df, norm_df, summary_df = estimate_chip_distribution_single(
            g,
            config=config,
            shares=shares_series.to_numpy(),
        )

        all_asset.append(asset_df)
        all_norm.append(norm_df)
        all_summary.append(summary_df)

    asset_out = pd.concat(all_asset, ignore_index=True) if all_asset else pd.DataFrame()
    norm_out = pd.concat(all_norm, ignore_index=True) if all_norm else pd.DataFrame()
    summary_out = pd.concat(all_summary, ignore_index=True) if all_summary else pd.DataFrame()

    return asset_out, norm_out, summary_out
