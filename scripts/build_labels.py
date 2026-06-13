#!/usr/bin/env python3
"""Build forward-return labels for crypto_top50_usdt_perp_1h.

Uses calendar-time join: ret_fwd_h = close[timestamp + h hours] / close[timestamp] - 1.
If the future timestamp does not exist for a symbol (gap), the label is NaN.
This avoids using row-shift which would produce incorrect returns across gaps.

V0 convention: timestamp = bar_close_time.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache" / "crypto_top50_usdt_perp_1h"
FEATURE = ROOT / "data" / "features" / "crypto_top50_usdt_perp_1h"
BARS = CACHE / "bars_1h.parquet"
LABELS = FEATURE / "labels.parquet"
HORIZONS = [1, 4, 24, 72]


def load_bars() -> pd.DataFrame:
    if not BARS.exists():
        raise FileNotFoundError(f"bars file not found: {BARS}")
    bars = pd.read_parquet(BARS)
    if bars.empty:
        raise ValueError("bars_1h.parquet is empty. Run scripts/fetch_crypto_top50_bars.py first.")
    missing = {"timestamp", "symbol", "close"} - set(bars.columns)
    if missing:
        raise ValueError(f"bars file missing columns: {sorted(missing)}")
    bars = bars.copy()
    bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True)
    return bars.sort_values(["symbol", "timestamp"])


def build_labels(bars: pd.DataFrame) -> pd.DataFrame:
    """Build forward-return labels using calendar-time join.

    For each (timestamp, symbol), look up close at timestamp + h hours.
    If that future bar does not exist, the label is NaN.
    This correctly handles gaps: we never substitute a nearby row for a missing hour.

    Implementation: create a lookup table of (timestamp, symbol) -> close,
    then for each row compute target = timestamp + h and merge to find close[target].
    """
    base = bars[["timestamp", "symbol", "close"]].copy()
    # Static lookup: (timestamp, symbol) -> close at that timestamp
    close_lookup = base[["timestamp", "symbol", "close"]].copy()

    for h in HORIZONS:
        target_col = f"_target_ts_{h}"
        # For each row at time t, the future time is t + h
        base[target_col] = base["timestamp"] + pd.Timedelta(hours=h)

        # Look up close at (t+h, symbol) from the lookup table
        future = close_lookup.rename(columns={
            "timestamp": target_col,
            "close": f"_close_at_t_plus_{h}",
        })
        base = base.merge(future, on=[target_col, "symbol"], how="left")
        base[f"ret_fwd_{h}h"] = base[f"_close_at_t_plus_{h}"] / base["close"] - 1.0
        base = base.drop(columns=[f"_close_at_t_plus_{h}", target_col])

    return base.drop(columns=["close"]).sort_values(["timestamp", "symbol"]).reset_index(drop=True)


def main() -> None:
    print("Build forward-return labels (calendar-time join)")
    bars = load_bars()
    labels = build_labels(bars)
    FEATURE.mkdir(parents=True, exist_ok=True)
    labels.to_parquet(LABELS, index=False)
    print(f"input rows:  {len(bars)}")
    print(f"output rows: {len(labels)}")
    print(f"output path: {LABELS}")
    print("missing rate:")
    print(labels[["ret_fwd_1h", "ret_fwd_4h", "ret_fwd_24h", "ret_fwd_72h"]].isna().mean().to_string())
    print(f"computed_at: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")


if __name__ == "__main__":
    main()
