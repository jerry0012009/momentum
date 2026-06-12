#!/usr/bin/env python3
"""Batch factor builder — reads factor_catalog_v0_1.csv, computes all IMPLEMENTED factors."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BARS = ROOT / "data" / "cache" / "crypto_top50_usdt_perp_1h" / "bars_1h.parquet"
FEATURE = ROOT / "data" / "features" / "crypto_top50_usdt_perp_1h"
CATALOG = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_catalog_v0_1.csv"


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


def calc_atr(high: pd.Series, low: pd.Series, close: pd.Series, n: int = 14) -> pd.Series:
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()


def build_factors(g: pd.DataFrame, factors: list[dict]) -> pd.DataFrame:
    """Compute all factors for a single symbol group."""
    g = g.copy().sort_values("timestamp")
    c = g["close"]
    h = g["high"]
    lo = g["low"]
    vol = g["volume"]
    qvol = g["quote_volume"] if "quote_volume" in g.columns else vol * c
    r = c.pct_change()

    result = g[["timestamp", "symbol"]].copy()

    for f in factors:
        fid = f["factor_id"]
        w = f["window"]

        if fid.startswith("mom_"):
            result[fid] = c / c.shift(w) - 1.0

        elif fid.startswith("reversal_"):
            result[fid] = -(c / c.shift(w) - 1.0)

        elif fid == "volatility_20h":
            result[fid] = r.rolling(20, min_periods=20).std(ddof=1)
        elif fid.startswith("volatility_"):
            result[fid] = r.rolling(w, min_periods=w).std(ddof=1)

        elif fid == "rsi_14h":
            result[fid] = calc_rsi(c, 14)

        elif fid == "bb_zscore_20h":
            mean20 = c.rolling(20, min_periods=20).mean()
            std20 = c.rolling(20, min_periods=20).std(ddof=1)
            result[fid] = (c - mean20) / std20.replace(0, np.nan)

        elif fid == "volume_zscore_20h":
            mv = vol.rolling(20, min_periods=20).mean()
            sv = vol.rolling(20, min_periods=20).std(ddof=1)
            result[fid] = (vol - mv) / sv.replace(0, np.nan)

        elif fid == "volume_ratio_20h":
            mv = vol.rolling(20, min_periods=20).mean()
            result[fid] = vol / mv.replace(0, np.nan)

        elif fid == "quote_volume_zscore_20h":
            mv = qvol.rolling(20, min_periods=20).mean()
            sv = qvol.rolling(20, min_periods=20).std(ddof=1)
            result[fid] = (qvol - mv) / sv.replace(0, np.nan)

        elif fid == "hl_range_20h":
            rng = (h - lo) / c.replace(0, np.nan)
            result[fid] = rng.rolling(20, min_periods=20).mean()

        elif fid == "close_to_high_20h":
            hh = h.rolling(20, min_periods=20).max()
            result[fid] = c / hh.replace(0, np.nan)

        elif fid == "close_to_low_20h":
            ll = lo.rolling(20, min_periods=20).min()
            result[fid] = c / ll.replace(0, np.nan)

        elif fid == "atr_14h":
            atr = calc_atr(h, lo, c, 14)
            result[fid] = atr / c.replace(0, np.nan)  # normalize by price

        elif fid == "ma_gap_20h":
            ma = c.rolling(20, min_periods=20).mean()
            result[fid] = (c - ma) / ma.replace(0, np.nan)

        else:
            print(f"  WARNING: unknown factor_id {fid}, skipping")

    return result


def main() -> None:
    # load catalog
    catalog = pd.read_csv(CATALOG)
    factors = catalog[catalog["implementation_status"] == "IMPLEMENTED"].to_dict("records")
    factor_ids = [f["factor_id"] for f in factors]
    print(f"Catalog: {len(catalog)} total, {len(factors)} IMPLEMENTED")

    # load bars
    if not BARS.exists():
        raise FileNotFoundError(BARS)
    bars = pd.read_parquet(BARS)
    bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True)
    bars = bars.sort_values(["symbol", "timestamp"])
    print(f"Bars: {len(bars)} rows, {bars['symbol'].nunique()} symbols")

    # compute per symbol
    parts = []
    for sym, g in bars.groupby("symbol", sort=False):
        parts.append(build_factors(g, factors))
    wide = pd.concat(parts, ignore_index=True)

    # write per-factor parquet
    computed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for fid in factor_ids:
        if fid not in wide.columns:
            print(f"  SKIP {fid}: not computed")
            continue
        out = wide[["timestamp", "symbol", fid]].rename(columns={fid: "factor_value"}).copy()
        out.insert(2, "factor_name", fid)
        out["known_at"] = out["timestamp"]
        out["source_timeframe"] = "1h"
        out["computed_at"] = computed_at
        out = out[["timestamp", "symbol", "factor_name", "factor_value", "known_at", "source_timeframe", "computed_at"]]
        target_dir = FEATURE / fid
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / "factor_values.parquet"
        out.to_parquet(target, index=False)
        cov = out["factor_value"].notna().mean()
        print(f"  {fid}: rows={len(out)} coverage={cov:.3%}")

    print(f"\n✓ {len(factor_ids)} factors written to {FEATURE}/")


if __name__ == "__main__":
    main()
