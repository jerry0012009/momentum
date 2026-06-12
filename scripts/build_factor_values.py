#!/usr/bin/env python3
"""Build registered research factor values for the crypto Top50 1h universe."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BARS = ROOT / "data" / "cache" / "crypto_top50_usdt_perp_1h" / "bars_1h.parquet"
FEATURE = ROOT / "data" / "features" / "crypto_top50_usdt_perp_1h"
NAMES = ["mom_20h", "reversal_5h", "volatility_20h", "rsi_14h", "bb_zscore_20h"]


def calc_rsi(close: pd.Series, n: int = 14) -> pd.Series:
    d = close.diff()
    up = d.clip(lower=0)
    down = -d.clip(upper=0)
    avg_up = up.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    avg_down = down.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    rs = avg_up / avg_down.replace(0, np.nan)
    out = 100 - 100 / (1 + rs)
    out = out.where(avg_down != 0, 100.0)
    out = out.where(avg_up != 0, 0.0)
    return out


def calc_group(g: pd.DataFrame) -> pd.DataFrame:
    g = g.copy().sort_values("timestamp")
    c = g["close"]
    r = c.pct_change()
    g["mom_20h"] = c / c.shift(20) - 1.0
    g["reversal_5h"] = -(c / c.shift(5) - 1.0)
    g["volatility_20h"] = r.rolling(20, min_periods=20).std(ddof=1)
    g["rsi_14h"] = calc_rsi(c, 14)
    mean20 = c.rolling(20, min_periods=20).mean()
    std20 = c.rolling(20, min_periods=20).std(ddof=1)
    g["bb_zscore_20h"] = (c - mean20) / std20.replace(0, np.nan)
    return g[["timestamp", "symbol", *NAMES]]


def main() -> None:
    if not BARS.exists():
        raise FileNotFoundError(BARS)
    bars = pd.read_parquet(BARS)
    if bars.empty:
        raise ValueError("bars_1h.parquet is empty; fetch bars first")
    bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True)
    bars = bars.sort_values(["symbol", "timestamp"])
    wide = bars.groupby("symbol", group_keys=False, sort=False).apply(calc_group).reset_index(drop=True)
    computed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for name in NAMES:
        out = wide[["timestamp", "symbol", name]].rename(columns={name: "factor_value"}).copy()
        out.insert(2, "factor_name", name)
        out["known_at"] = out["timestamp"]
        out["source_timeframe"] = "1h"
        out["computed_at"] = computed_at
        out = out[["timestamp", "symbol", "factor_name", "factor_value", "known_at", "source_timeframe", "computed_at"]]
        target_dir = FEATURE / name
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / "factor_values.parquet"
        out.to_parquet(target, index=False)
        print(f"{name}: rows={len(out)} coverage={out['factor_value'].notna().mean():.3%} path={target}")


if __name__ == "__main__":
    main()
