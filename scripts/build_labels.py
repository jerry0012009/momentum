#!/usr/bin/env python3
"""Build forward-return labels for crypto_top50_usdt_perp_1h."""
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
    out = bars[["timestamp", "symbol", "close"]].copy()
    close_by_symbol = out.groupby("symbol", sort=False)["close"]
    for h in HORIZONS:
        out[f"ret_fwd_{h}h"] = close_by_symbol.shift(-h) / out["close"] - 1.0
    return out.drop(columns=["close"]).sort_values(["timestamp", "symbol"]).reset_index(drop=True)


def main() -> None:
    print("Build forward-return labels")
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
