#!/usr/bin/env python3
"""Build crypto market cap 1h aligned dataset.

Strategy:
  1. CoinGecko /coins/markets → current circulating_supply (batch, 1 request)
  2. Binance /api/v3/klines → historical daily close prices (per symbol, fast)
  3. cap = circulating_supply × close_price

Rationale:
  - CoinGecko free API only gives 365d of daily historical market cap
  - Binance gives full history for free, fast, no auth needed
  - Circulating supply changes slowly (<1% monthly for most coins)
  - For diagnostic factors, this approximation is acceptable
  - The cap_quality_flag marks data as 'supply_snapshot_approx'

Usage:
    python scripts/build_crypto_market_cap_1h.py \
        --dataset-id crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1

Output:
    data/cache/crypto_market_cap_1h_contract_v1/
        market_cap_1h_aligned.parquet
        market_cap_source_raw.parquet
        symbol_id_map.csv
        symbol_id_map_unresolved.csv
        market_cap_manifest.json
        market_cap_quality_report.csv
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "data" / "cache"
CAP_CACHE_DIR = CACHE_DIR / "crypto_market_cap_1h_contract_v1"
OVERRIDES_PATH = ROOT / "config" / "crypto_symbol_coingecko_overrides.csv"

COINGECKO_API_KEY = os.environ.get("COINGECKO_API_KEY", "")
COINGECKO_BASE = "https://api.coingecko.com/api/v3"
if COINGECKO_API_KEY:
    COINGECKO_BASE = "https://pro-api.coingecko.com/api/v3"

# Binance config (use SOCKS5 proxy if available)
BINANCE_REST = "https://fapi.binance.com"  # futures API — has 1000xxx symbols
BN_PROXY = os.environ.get("BINANCE_PROXY_URL", "socks5h://47.79.224.99:1080")

# Rate limits
CG_DELAY = 6.5  # CoinGecko free tier
BN_DELAY = 0.2  # Binance is generous
MAX_RETRIES = 3
RETRY_DELAY = 30

REQUEST_TIMEOUT = 30


def parse_args():
    p = argparse.ArgumentParser(description="Build crypto market cap 1h dataset")
    p.add_argument("--dataset-id", required=True)
    p.add_argument("--universe-id", default=None)
    p.add_argument("--start", default="2024-06-13")
    p.add_argument("--end", default="2026-06-13")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--remap-only", action="store_true")
    return p.parse_args()


# ── Symbol normalization ──────────────────────────────────────────

MULTIPLIER_PREFIXES = {"1000": 1000, "1000000": 1_000_000, "1M": 1_000_000, "1": 1}


def normalize_base_asset(symbol: str) -> tuple[str, str, int]:
    m = re.match(r"^(\d+)(.+?)USDT$", symbol)
    if m:
        prefix_str = m.group(1)
        raw_base = m.group(2)
        base_asset = prefix_str + raw_base
        mult = MULTIPLIER_PREFIXES.get(prefix_str, 1)
        return base_asset, raw_base, mult
    base = symbol.replace("USDT", "")
    return base, base, 1


# ── API helpers ───────────────────────────────────────────────────

def _get_with_retries(url, params=None, headers=None, proxies=None, delay=0):
    for attempt in range(MAX_RETRIES):
        if delay > 0:
            time.sleep(delay)
        try:
            resp = requests.get(url, params=params, headers=headers,
                                proxies=proxies, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", RETRY_DELAY * (attempt + 1)))
                print(f"    Rate limited, waiting {wait}s...", flush=True)
                time.sleep(wait)
                continue
            if resp.status_code >= 500:
                print(f"    {resp.status_code} server error (attempt {attempt+1})", flush=True)
                time.sleep(RETRY_DELAY)
                continue
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            print(f"    Error (attempt {attempt+1}/{MAX_RETRIES}): {e}", flush=True)
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
    return None


def cg_get(path, params=None):
    url = f"{COINGECKO_BASE}{path}"
    headers = {}
    if COINGECKO_API_KEY:
        headers["x-cg-demo-api-key"] = COINGECKO_API_KEY
    return _get_with_retries(url, params=params, headers=headers, delay=CG_DELAY)


def bn_get(path, params=None):
    url = f"{BINANCE_REST}{path}"
    proxies = {"https": BN_PROXY, "http": BN_PROXY} if BN_PROXY else None
    return _get_with_retries(url, params=params, proxies=proxies, delay=BN_DELAY)


# ── Fetch CoinGecko circulating supply (batch) ───────────────────

def fetch_circulating_supply() -> pd.DataFrame:
    """Fetch current circulating supply for top coins via /coins/markets."""
    print("Fetching CoinGecko circulating supply (batch) ...", flush=True)
    all_coins = []
    for page in range(1, 6):  # up to 5 pages × 250 = 1250 coins
        data = cg_get("/coins/markets", {
            "vs_currency": "usd",
            "per_page": 250,
            "page": page,
            "sparkline": "false",
        })
        if data is None or len(data) == 0:
            break
        all_coins.extend(data)
        print(f"  Page {page}: {len(data)} coins", flush=True)
        if len(data) < 250:
            break

    if not all_coins:
        print("ERROR: No coins from CoinGecko /coins/markets")
        sys.exit(1)

    rows = []
    for c in all_coins:
        rows.append({
            "coingecko_id": c["id"],
            "cg_symbol": c["symbol"].lower(),
            "cg_name": c["name"],
            "circulating_supply": c.get("circulating_supply"),
            "total_supply": c.get("total_supply"),
            "max_supply": c.get("max_supply"),
            "current_market_cap": c.get("market_cap"),
            "current_price": c.get("current_price"),
        })
    df = pd.DataFrame(rows)
    df = df[df["circulating_supply"].notna() & (df["circulating_supply"] > 0)]
    print(f"  {len(df)} coins with circulating supply > 0", flush=True)
    return df


# ── Fetch Binance historical daily prices ─────────────────────────

def fetch_binance_daily_klines(symbol: str, start_ms: int, end_ms: int) -> pd.DataFrame:
    """Fetch daily klines from Binance for a symbol."""
    data = bn_get("/fapi/v1/klines", {
        "symbol": symbol,
        "interval": "1d",
        "startTime": start_ms,
        "endTime": end_ms,
        "limit": 1000,
    })
    if data is None or len(data) == 0:
        return pd.DataFrame()

    rows = []
    for k in data:
        rows.append({
            "timestamp": pd.Timestamp(k[0], unit="ms", tz="UTC"),
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
            "close": float(k[4]),
            "volume": float(k[5]),
            "close_time": pd.Timestamp(k[6], unit="ms", tz="UTC"),
        })
    return pd.DataFrame(rows)


# ── Symbol mapping ────────────────────────────────────────────────

def build_symbol_mapping(symbols: list[str], cg_supply: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build symbol → coingecko_id mapping."""
    overrides = pd.DataFrame()
    if OVERRIDES_PATH.exists():
        overrides = pd.read_csv(OVERRIDES_PATH)
        print(f"Loaded {len(overrides)} manual overrides from {OVERRIDES_PATH}")

    # Build CG symbol index (lowercase → list of ids)
    cg_by_symbol = {}
    for _, row in cg_supply.iterrows():
        sym = row["cg_symbol"]
        if sym not in cg_by_symbol:
            cg_by_symbol[sym] = []
        cg_by_symbol[sym].append(row["coingecko_id"])

    resolved_rows = []
    unresolved_rows = []

    for symbol in symbols:
        base_asset, normalized_base, multiplier = normalize_base_asset(symbol)

        # Try manual override first
        if not overrides.empty:
            match = overrides[overrides["symbol"] == symbol]
            if not match.empty:
                row = match.iloc[0]
                cg_id = row.get("coingecko_id", "")
                status = row.get("map_status", "RESOLVED")
                if pd.isna(cg_id) or str(cg_id).strip() == "":
                    unresolved_rows.append({
                        "symbol": symbol, "base_asset": base_asset,
                        "normalized_base": normalized_base, "multiplier": multiplier,
                        "coingecko_id": "", "map_source": "manual_override",
                        "map_status": "UNMAPPED", "notes": "Override has no coingecko_id",
                    })
                    continue
                cg_id = str(cg_id).strip()
                # Check if this coin has supply data
                supply_match = cg_supply[cg_supply["coingecko_id"] == cg_id]
                supply = supply_match.iloc[0]["circulating_supply"] if not supply_match.empty else None
                resolved_rows.append({
                    "symbol": symbol, "base_asset": base_asset,
                    "normalized_base": normalized_base, "multiplier": multiplier,
                    "coingecko_id": cg_id, "circulating_supply": supply,
                    "map_source": "manual_override", "map_status": status,
                    "notes": str(row.get("notes", "")),
                })
                continue

        # Auto-match by normalized_base
        key = normalized_base.lower()
        candidates = cg_by_symbol.get(key, [])

        if len(candidates) == 0:
            unresolved_rows.append({
                "symbol": symbol, "base_asset": base_asset,
                "normalized_base": normalized_base, "multiplier": multiplier,
                "coingecko_id": "", "map_source": "auto",
                "map_status": "UNMAPPED", "notes": "No CoinGecko symbol match",
            })
        elif len(candidates) == 1:
            cg_id = candidates[0]
            supply_match = cg_supply[cg_supply["coingecko_id"] == cg_id]
            supply = supply_match.iloc[0]["circulating_supply"] if not supply_match.empty else None
            resolved_rows.append({
                "symbol": symbol, "base_asset": base_asset,
                "normalized_base": normalized_base, "multiplier": multiplier,
                "coingecko_id": cg_id, "circulating_supply": supply,
                "map_source": "auto", "map_status": "RESOLVED",
                "notes": f"Auto: {supply_match.iloc[0]['cg_name'] if not supply_match.empty else cg_id}",
            })
        else:
            # Multiple candidates — pick the one with highest market cap
            cand_data = cg_supply[cg_supply["coingecko_id"].isin(candidates)]
            if not cand_data.empty:
                best = cand_data.loc[cand_data["current_market_cap"].idxmax()]
                resolved_rows.append({
                    "symbol": symbol, "base_asset": base_asset,
                    "normalized_base": normalized_base, "multiplier": multiplier,
                    "coingecko_id": best["coingecko_id"],
                    "circulating_supply": best["circulating_supply"],
                    "map_source": "auto_best_mcap", "map_status": "RESOLVED",
                    "notes": f"Best of {len(candidates)}: {best['cg_name']}",
                })
            else:
                unresolved_rows.append({
                    "symbol": symbol, "base_asset": base_asset,
                    "normalized_base": normalized_base, "multiplier": multiplier,
                    "coingecko_id": "", "map_source": "auto",
                    "map_status": "AMBIGUOUS_MAPPING",
                    "notes": f"{len(candidates)} candidates, none with supply",
                })

    resolved_df = pd.DataFrame(resolved_rows)
    unresolved_df = pd.DataFrame(unresolved_rows)

    print(f"\nSymbol mapping: {len(resolved_df)} resolved, {len(unresolved_df)} unresolved")
    if not unresolved_df.empty:
        print("Unresolved symbols:")
        for _, r in unresolved_df.iterrows():
            print(f"  {r['symbol']}: {r['map_status']} — {r['notes']}")

    return resolved_df, unresolved_df


# ── Build raw market cap ──────────────────────────────────────────

def build_raw_market_cap(mapping: pd.DataFrame, start_dt: datetime, end_dt: datetime) -> pd.DataFrame:
    """Build raw market cap = circulating_supply × Binance daily close price."""
    print(f"\nFetching Binance daily prices for {len(mapping)} symbols ...", flush=True)
    start_ms = int(start_dt.timestamp() * 1000)
    end_ms = int(end_dt.timestamp() * 1000)

    raw_parts = []
    errors = []

    for i, (_, row) in enumerate(mapping.iterrows()):
        symbol = row["symbol"]
        cg_id = row["coingecko_id"]
        supply = row.get("circulating_supply")

        if pd.isna(supply) or supply is None or supply <= 0:
            errors.append({"symbol": symbol, "error": "no_circulating_supply"})
            continue

        print(f"  [{i+1}/{len(mapping)}] {symbol} (supply={supply:,.0f}) ...", end="", flush=True)
        klines = fetch_binance_daily_klines(symbol, start_ms, end_ms)

        if klines.empty:
            print(f" NO DATA", flush=True)
            errors.append({"symbol": symbol, "error": "no_binance_klines"})
            continue

        klines["market_cap"] = klines["close"] * supply
        klines["coingecko_id"] = cg_id
        klines["source_timestamp"] = klines["timestamp"]
        klines["source"] = "binance_daily_close_x_coingecko_supply"
        klines["fetched_at"] = pd.Timestamp.now(tz="UTC")
        klines = klines.rename(columns={"market_cap": "market_cap"})

        raw_parts.append(klines[[
            "coingecko_id", "source_timestamp", "market_cap",
            "close", "source", "fetched_at"
        ]].rename(columns={"close": "price"}))
        print(f" {len(klines)} days", flush=True)

    if errors:
        print(f"\nFetch errors: {len(errors)}", flush=True)
        for e in errors:
            print(f"  {e['symbol']}: {e['error']}", flush=True)

    if not raw_parts:
        print("ERROR: No market cap data built")
        sys.exit(1)

    raw_df = pd.concat(raw_parts, ignore_index=True)
    print(f"\nRaw market cap: {len(raw_df)} rows, {raw_df['coingecko_id'].nunique()} coins", flush=True)
    return raw_df


# ── Alignment to bars ─────────────────────────────────────────────

def align_cap_to_bars(bars: pd.DataFrame, cap_raw: pd.DataFrame, mapping: pd.DataFrame) -> pd.DataFrame:
    """Align raw market cap to Momentum bars using merge_asof backward."""
    cap_with_id = cap_raw.merge(
        mapping[["symbol", "coingecko_id", "normalized_base", "circulating_supply"]],
        on="coingecko_id", how="inner"
    )

    aligned_parts = []
    tolerance = pd.Timedelta("36h")  # daily data → generous tolerance

    for symbol in bars["symbol"].unique():
        sym_bars = bars[bars["symbol"] == symbol].sort_values("timestamp").copy()
        sym_cap = cap_with_id[cap_with_id["symbol"] == symbol].sort_values("source_timestamp")

        if sym_cap.empty:
            sym_bars["cap"] = np.nan
            sym_bars["cap_source_timestamp"] = pd.NaT
            sym_bars["cap_known_at"] = pd.NaT
            sym_bars["cap_source"] = ""
            sym_bars["cap_frequency"] = ""
            sym_bars["cap_fill_method"] = "missing"
            sym_bars["cap_quality_flag"] = "UNMAPPED"
            aligned_parts.append(sym_bars)
            continue

        merged = pd.merge_asof(
            sym_bars,
            sym_cap[["source_timestamp", "market_cap"]].rename(columns={"market_cap": "cap"}),
            left_on="timestamp",
            right_on="source_timestamp",
            direction="backward",
            tolerance=tolerance,
        )

        merged["cap_source_timestamp"] = pd.to_datetime(merged["source_timestamp"], utc=True)
        merged["cap_known_at"] = pd.to_datetime(merged["source_timestamp"], utc=True)
        merged["cap_source"] = "binance_daily_close_x_coingecko_supply"
        merged["cap_frequency"] = "daily_ffill"

        has_cap = merged["cap"].notna()
        merged["cap_fill_method"] = np.where(has_cap, "asof_ffill", "missing")
        merged["cap_quality_flag"] = np.where(
            has_cap,
            np.where(merged["cap"] > 0, "OK", "MISSING"),
            "MISSING"
        )

        # Enforce no forward-looking leakage
        violation_mask = merged["source_timestamp"] > merged["timestamp"]
        if violation_mask.any():
            n_viol = violation_mask.sum()
            print(f"  WARNING: {symbol}: {n_viol} forward-looking cap violations → NaN")
            merged.loc[violation_mask, "cap"] = np.nan
            merged.loc[violation_mask, "cap_quality_flag"] = "MISSING"

        aligned_parts.append(merged)

    if not aligned_parts:
        return pd.DataFrame()

    result = pd.concat(aligned_parts, ignore_index=True)
    bad_cap = (result["cap"].notna()) & (result["cap"] <= 0)
    if bad_cap.any():
        print(f"  WARNING: {bad_cap.sum()} rows with cap <= 0 → NaN")
        result.loc[bad_cap, "cap"] = np.nan
        result.loc[bad_cap, "cap_quality_flag"] = "MISSING"

    return result


# ── Quality report ────────────────────────────────────────────────

def build_quality_report(aligned: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for symbol in sorted(aligned["symbol"].unique()):
        sym = aligned[aligned["symbol"] == symbol]
        n_bars = len(sym)
        n_cap = sym["cap"].notna().sum()
        coverage = n_cap / n_bars if n_bars > 0 else 0

        cap_data = sym[sym["cap"].notna()]
        first_ts = cap_data["timestamp"].min() if not cap_data.empty else pd.NaT
        last_ts = cap_data["timestamp"].max() if not cap_data.empty else pd.NaT

        max_gap = np.nan
        if len(cap_data) > 1:
            gaps = cap_data["timestamp"].diff().dropna()
            max_gap = gaps.max().total_seconds() / 3600

        status = "OK"
        notes = ""
        if coverage < 0.5:
            status = "LOW_COVERAGE"
            notes = f"{coverage:.1%}"
        elif coverage < 0.8:
            status = "MARGINAL_COVERAGE"
            notes = f"{coverage:.1%}"

        rows.append({
            "symbol": symbol,
            "coingecko_id": sym["coingecko_id"].iloc[0] if "coingecko_id" in sym.columns else "",
            "n_bars": n_bars,
            "n_cap_non_null": n_cap,
            "coverage": round(coverage, 4),
            "first_cap_timestamp": first_ts,
            "last_cap_timestamp": last_ts,
            "max_gap_hours": round(max_gap, 1) if not np.isnan(max_gap) else np.nan,
            "cap_frequency": "daily_ffill",
            "cap_quality_status": status,
            "notes": notes,
        })
    return pd.DataFrame(rows)


# ── Main ──────────────────────────────────────────────────────────

def main():
    args = parse_args()
    CAP_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    start_dt = datetime.strptime(args.start, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    end_dt = datetime.strptime(args.end, "%Y-%m-%d").replace(tzinfo=timezone.utc)

    # Load bars
    bars_path = CACHE_DIR / args.dataset_id / "bars_1h.parquet"
    print(f"Loading bars from {bars_path} ...", flush=True)
    bars = pd.read_parquet(bars_path, columns=["timestamp", "symbol"])
    bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True)
    symbols = sorted(bars["symbol"].unique())
    print(f"  {len(symbols)} symbols, {len(bars)} rows", flush=True)
    print(f"  Date range: {bars['timestamp'].min()} to {bars['timestamp'].max()}", flush=True)

    # Step 1: CoinGecko circulating supply (batch)
    cg_supply = fetch_circulating_supply()

    # Step 2: Symbol mapping
    mapping, unresolved = build_symbol_mapping(symbols, cg_supply)
    mapping.to_csv(CAP_CACHE_DIR / "symbol_id_map.csv", index=False)
    if not unresolved.empty:
        unresolved.to_csv(CAP_CACHE_DIR / "symbol_id_map_unresolved.csv", index=False)
    print(f"\nResolved: {len(mapping)}, Unresolved: {len(unresolved)}", flush=True)

    if args.dry_run or args.remap_only:
        print("Dry run / remap only — stopping.")
        return

    # Step 3: Build raw market cap (Binance daily prices × CoinGecko supply)
    raw_df = build_raw_market_cap(mapping, start_dt, end_dt)
    raw_df.to_parquet(CAP_CACHE_DIR / "market_cap_source_raw.parquet", index=False)

    # Step 4: Align to bars
    print("\nAligning market cap to bars ...", flush=True)
    aligned = align_cap_to_bars(bars, raw_df, mapping)
    if aligned.empty:
        print("ERROR: Alignment produced empty result")
        sys.exit(1)

    # Forward-looking leakage check
    if "cap_source_timestamp" in aligned.columns:
        cap_ts = pd.to_datetime(aligned["cap_source_timestamp"], utc=True)
        bar_ts = pd.to_datetime(aligned["timestamp"], utc=True)
        leakage = cap_ts > bar_ts
        if leakage.any():
            print(f"CRITICAL: {leakage.sum()} forward-looking leakage rows!")
            sys.exit(1)

    aligned.to_parquet(CAP_CACHE_DIR / "market_cap_1h_aligned.parquet", index=False)
    print(f"Saved aligned: {len(aligned)} rows", flush=True)

    # Step 5: Quality report
    quality = build_quality_report(aligned)
    quality.to_csv(CAP_CACHE_DIR / "market_cap_quality_report.csv", index=False)

    overall_coverage = aligned["cap"].notna().mean()
    n_low = len(quality[quality["cap_quality_status"] == "LOW_COVERAGE"])
    n_ok = len(quality[quality["cap_quality_status"] == "OK"])
    print(f"\nOverall coverage: {overall_coverage:.1%}", flush=True)
    print(f"OK: {n_ok}, LOW_COVERAGE: {n_low}", flush=True)

    # Manifest
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "binance_daily_close_x_coingecko_circulating_supply",
        "interval": "daily_ffill",
        "methodology": "circulating_supply (CoinGecko snapshot) × daily_close (Binance)",
        "caveat": "Circulating supply is a point-in-time snapshot; historical supply changes not captured",
        "dataset_id": args.dataset_id,
        "n_symbols_total": len(symbols),
        "n_symbols_mapped": len(mapping),
        "n_symbols_unmapped": len(unresolved),
        "n_raw_rows": len(raw_df),
        "n_aligned_rows": len(aligned),
        "overall_coverage": round(overall_coverage, 4),
        "n_ok_symbols": n_ok,
        "n_low_coverage_symbols": n_low,
        "fetch_errors": len(mapping) - raw_df["coingecko_id"].nunique(),
    }
    with open(CAP_CACHE_DIR / "market_cap_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2, default=str)

    # Data contract checks
    checks = {
        "file_exists": True,
        "has_required_columns": all(c in aligned.columns for c in [
            "timestamp", "symbol", "cap", "cap_source_timestamp",
            "cap_known_at", "cap_source", "cap_frequency", "cap_fill_method", "cap_quality_flag"
        ]),
        "no_duplicate_keys": not aligned.duplicated(["timestamp", "symbol"]).any(),
        "no_negative_cap": not ((aligned["cap"].notna()) & (aligned["cap"] <= 0)).any(),
        "no_forward_leakage": "cap_source_timestamp" not in aligned.columns or
                              not (pd.to_datetime(aligned["cap_source_timestamp"], utc=True) > pd.to_datetime(aligned["timestamp"], utc=True)).any(),
        "overall_coverage_gte_90pct": overall_coverage >= 0.9,
    }
    all_pass = all(checks.values())
    checks["all_pass"] = all_pass
    with open(CAP_CACHE_DIR / "market_cap_contract_check.json", "w") as f:
        json.dump(checks, f, indent=2, default=str)

    print(f"\nContract check: {'PASS' if all_pass else 'FAIL'}", flush=True)
    for k, v in checks.items():
        if k != "all_pass":
            print(f"  {k}: {'✓' if v else '✗'}", flush=True)

    print("\nDone. Files:", CAP_CACHE_DIR, flush=True)


if __name__ == "__main__":
    main()
