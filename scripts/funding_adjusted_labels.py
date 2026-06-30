#!/usr/bin/env python3
"""Funding-adjusted forward-return helpers for factor evaluation.

Funding rates are paid at settlement events, not continuously every bar.  The
aligned cache is hourly-indexed for easy joins, but rows with funding_age_hours
near zero identify actual settlement hours.  Forward funding cost therefore
sums settlement funding_rate events inside the forward holding window. Missing
events stay missing.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def horizon_to_hours(horizon: str) -> int:
    text = str(horizon).strip().lower()
    if not text.endswith("h"):
        raise ValueError(f"Unsupported horizon format: {horizon}")
    hours = int(text[:-1])
    if hours <= 0:
        raise ValueError(f"Horizon must be positive: {horizon}")
    return hours


def infer_funding_aligned_path(root: Path, dataset_id: str) -> Path:
    kind = "dynamic" if "monthly_volume" in dataset_id else "static"
    return (
        root
        / "data"
        / "cache"
        / "crypto_funding_rate_1h_contract_v1"
        / f"funding_rate_1h_aligned_{kind}.parquet"
    )


def _forward_sum(cost: np.ndarray, valid: np.ndarray, hours: int) -> tuple[np.ndarray, np.ndarray]:
    n = len(cost)
    out = np.full(n, np.nan, dtype=float)
    counts = np.zeros(n, dtype=np.int16)
    if n <= hours:
        return out, counts

    cost_clean = np.where(valid, cost, 0.0)
    csum = np.concatenate([[0.0], np.cumsum(cost_clean)])
    vsum = np.concatenate([[0], np.cumsum(valid.astype(np.int32))])
    idx = np.arange(0, n - hours)
    start = idx + 1
    end = idx + hours + 1
    sums = csum[end] - csum[start]
    cov = vsum[end] - vsum[start]
    counts[idx] = cov
    out[idx] = sums
    return out, counts


def build_funding_cost_columns(
    funding: pd.DataFrame,
    horizons: list[str],
) -> pd.DataFrame:
    required = {"timestamp", "symbol", "funding_rate", "funding_interval_hours"}
    missing = required - set(funding.columns)
    if missing:
        raise ValueError(f"Funding data missing columns: {sorted(missing)}")

    frame = funding[list(required)].copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
    frame["symbol"] = frame["symbol"].astype(str)
    frame = frame.sort_values(["symbol", "timestamp"]).drop_duplicates(["symbol", "timestamp"], keep="last")
    interval = pd.to_numeric(frame["funding_interval_hours"], errors="coerce")
    rate = pd.to_numeric(frame["funding_rate"], errors="coerce")
    if "funding_age_hours" in funding.columns:
        frame["funding_age_hours"] = pd.to_numeric(funding["funding_age_hours"], errors="coerce")
        is_event_row = frame["funding_age_hours"].abs() < 1e-9
        frame["_funding_event_cost"] = rate.where(is_event_row)
    else:
        frame["_funding_event_cost"] = rate
    frame.loc[(interval <= 0) | frame["_funding_event_cost"].isna(), "_funding_event_cost"] = np.nan

    hours_by_horizon = {h: horizon_to_hours(h) for h in horizons}
    pieces: list[pd.DataFrame] = []
    for symbol, grp in frame.sort_values(["symbol", "timestamp"]).groupby("symbol", sort=False):
        idx = pd.date_range(grp["timestamp"].min(), grp["timestamp"].max(), freq="h", tz="UTC")
        hourly = grp.set_index("timestamp").reindex(idx)
        hourly["symbol"] = symbol
        cost = hourly["_funding_event_cost"].to_numpy(dtype=float)
        valid = np.isfinite(cost)
        out = pd.DataFrame({"timestamp": idx, "symbol": symbol})
        for horizon, hours in hours_by_horizon.items():
            sums, counts = _forward_sum(cost, valid, hours)
            out[f"funding_cost_fwd_{horizon}"] = sums
            out[f"funding_hours_covered_{horizon}"] = counts
        pieces.append(out)

    if not pieces:
        return pd.DataFrame(columns=["timestamp", "symbol"])
    return pd.concat(pieces, ignore_index=True)


def add_funding_adjusted_returns(
    labels: pd.DataFrame,
    funding_aligned_path: Path,
    horizons: list[str],
) -> tuple[pd.DataFrame, dict]:
    out = labels.copy()
    if not funding_aligned_path.exists():
        return out, {
            "status": "FUNDING_ALIGNED_NOT_FOUND",
            "funding_aligned_path": str(funding_aligned_path),
            "coverage_by_horizon": [],
        }

    funding = pd.read_parquet(funding_aligned_path)
    costs = build_funding_cost_columns(funding, horizons)
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True)
    out["symbol"] = out["symbol"].astype(str)
    out = out.merge(costs, on=["timestamp", "symbol"], how="left")

    coverage = []
    for horizon in horizons:
        ret_col = f"ret_fwd_{horizon}"
        cost_col = f"funding_cost_fwd_{horizon}"
        after_col = f"ret_fwd_{horizon}_after_funding"
        if ret_col not in out.columns or cost_col not in out.columns:
            continue
        out[after_col] = out[ret_col] - out[cost_col]
        active = int(out[ret_col].notna().sum())
        covered = int(out[after_col].notna().sum())
        coverage.append({
            "horizon": horizon,
            "required_hourly_funding_rows": horizon_to_hours(horizon),
            "active_rows": active,
            "covered_rows": covered,
            "coverage_rate": covered / active if active else 0.0,
        })

    return out, {
        "status": "FUNDING_ADJUSTED_LABELS_COMPUTED",
        "funding_aligned_path": str(funding_aligned_path),
        "coverage_by_horizon": coverage,
        "note": (
            "Funding cost is summed from actual settlement funding_rate events inside each "
            "forward window. Missing settlement events stay null."
        ),
    }
