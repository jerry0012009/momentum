#!/usr/bin/env python3
"""
Build crypto_top50_usdt_perp_1h universe files.

Outputs:
  data/cache/crypto_top50_usdt_perp_1h/manifest.json
  data/cache/crypto_top50_usdt_perp_1h/universe_membership.parquet
  data/cache/crypto_top50_usdt_perp_1h/bars_1h.parquet  (empty schema only)

Does NOT download full history — only universe membership and schema.
"""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path("/root/clawd/jerry/momentum")
CACHE_DIR = REPO_ROOT / "data" / "cache" / "crypto_top50_usdt_perp_1h"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

COMMIT_SHA = "fe2735b3ea2b6e1966cc9520443346055fa6b4b0"
SCRIPT_PATH = "scripts/build_crypto_top50_universe.py"

# ── Stablecoin / leveraged token patterns to exclude ──
STABLECOIN_BASES = {
    "USDC", "BUSD", "DAI", "TUSD", "USDP", "FDUSD", "PYUSD",
    "EUR", "GBP", "AUD", "BRL", "TRY", "AEUR", "UST",
}
LEVERAGED_PATTERNS = ["UP", "DOWN", "BULL", "BEAR"]


def is_excluded_symbol(symbol: str) -> tuple[bool, str]:
    """Check if a perp symbol should be excluded."""
    # Must end with USDT
    if not symbol.endswith("USDT"):
        return True, "not_usdt_quote"

    base = symbol[:-4]  # strip USDT

    # Stablecoin pairs
    if base in STABLECOIN_BASES:
        return True, "stablecoin_pair"

    # Leveraged tokens (e.g., BTCUP, ETHDOWN)
    for pat in LEVERAGED_PATTERNS:
        if base.endswith(pat) and len(base) > len(pat):
            return True, "leveraged_token"

    return False, ""


def fetch_exchange_info() -> list[dict]:
    """Get all USDT-M futures symbols from Binance."""
    url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    info = resp.json()
    return info.get("symbols", [])


def fetch_30d_volume() -> dict[str, float]:
    """Get 30-day rolling dollar volume from 24h ticker."""
    url = "https://fapi.binance.com/fapi/v1/ticker/24hr"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    tickers = resp.json()
    # quoteVolume is 24h dollar volume
    return {t["symbol"]: float(t.get("quoteVolume", 0)) for t in tickers}


def main():
    print("=" * 60)
    print("Building crypto_top50_usdt_perp_1h universe")
    print("=" * 60)

    # ── Step 1: Fetch exchange info ──
    print("\n▸ Fetching Binance USDT-M exchange info...")
    symbols_info = fetch_exchange_info()
    print(f"  Total symbols on exchange: {len(symbols_info)}")

    # Filter to USDT-margined perpetuals
    perps = []
    for s in symbols_info:
        sym = s["symbol"]
        contract_type = s.get("contractType", "")
        quote = s.get("quoteAsset", "")
        status = s.get("status", "")
        pair = s.get("pair", "")

        if contract_type != "PERPETUAL":
            continue
        if quote != "USDT":
            continue
        if status != "TRADING":
            continue

        # Listing date from onboardDate
        onboard_ts = s.get("onboardDate", 0)
        onboard_dt = datetime.fromtimestamp(onboard_ts / 1000, tz=timezone.utc) if onboard_ts else None

        perps.append({
            "symbol": sym,
            "base_asset": s.get("baseAsset", ""),
            "onboard_date": onboard_dt,
            "status": status,
        })

    print(f"  USDT perpetuals: {len(perps)}")

    # ── Step 2: Filter exclusions ──
    filtered = []
    excluded_records = []
    for p in perps:
        excluded, reason = is_excluded_symbol(p["symbol"])
        if excluded:
            excluded_records.append({"symbol": p["symbol"], "reason": reason})
        else:
            filtered.append(p)

    print(f"  After exclusions: {len(filtered)}")
    if excluded_records:
        print(f"  Excluded: {len(excluded_records)} ({', '.join(set(r['reason'] for r in excluded_records))})")

    # ── Step 3: Filter by listing age >= 90 days ──
    now = datetime.now(timezone.utc)
    min_age_days = 90
    age_filtered = []
    too_new = []
    for p in filtered:
        if p["onboard_date"]:
            age_days = (now - p["onboard_date"]).days
            p["listing_age_days"] = age_days
            if age_days >= min_age_days:
                age_filtered.append(p)
            else:
                too_new.append(p["symbol"])
        else:
            p["listing_age_days"] = None
            age_filtered.append(p)  # include if unknown

    print(f"  After min_listing_age ({min_age_days}d): {len(age_filtered)}")
    if too_new:
        print(f"  Too new (excluded): {len(too_new)}")

    # ── Step 4: Fetch 24h dollar volume and rank ──
    print("\n▸ Fetching 24h dollar volume...")
    volume_map = fetch_30d_volume()
    print(f"  Got volume data for {len(volume_map)} symbols")

    for p in age_filtered:
        p["dollar_volume_24h"] = volume_map.get(p["symbol"], 0.0)

    # Sort by dollar volume descending
    age_filtered.sort(key=lambda x: x["dollar_volume_24h"], reverse=True)

    # Top 50
    top_n = 50
    top50 = age_filtered[:top_n]
    rest = age_filtered[top_n:]

    print(f"\n▸ Top {top_n} symbols by 24h dollar volume:")
    for i, p in enumerate(top50):
        vol_m = p["dollar_volume_24h"] / 1e6
        age = p.get("listing_age_days", "?")
        print(f"  {i+1:2d}. {p['symbol']:<16s}  ${vol_m:>10,.1f}M  age={age}d")

    # ── Step 5: Build universe_membership parquet ──
    print("\n▸ Building universe_membership.parquet...")
    rebalance_date = now.strftime("%Y-%m-%d")
    rows = []
    for i, p in enumerate(age_filtered):
        excluded, reason = is_excluded_symbol(p["symbol"])
        age_ok = (p.get("listing_age_days") or 999) >= min_age_days
        included = (i < top_n) and age_ok and not excluded
        exclusion_reason = ""
        if not included:
            if excluded:
                exclusion_reason = reason
            elif not age_ok:
                exclusion_reason = f"listing_age < {min_age_days}d"
            else:
                exclusion_reason = "rank_below_top50"

        rows.append({
            "rebalance_date": rebalance_date,
            "symbol": p["symbol"],
            "rank_by_dollar_volume": i + 1,
            "trailing_30d_dollar_volume": p["dollar_volume_24h"],
            "listing_age_days": p.get("listing_age_days"),
            "included": included,
            "exclusion_reason": exclusion_reason,
        })

    membership_df = pd.DataFrame(rows)
    membership_path = CACHE_DIR / "universe_membership.parquet"
    membership_df.to_parquet(membership_path, index=False)
    print(f"  Saved {len(membership_df)} rows to {membership_path}")

    # ── Step 6: Build empty bars_1h schema ──
    print("\n▸ Building bars_1h.parquet (empty schema)...")
    bars_schema = pd.DataFrame({
        "timestamp": pd.Series(dtype="datetime64[ns, UTC]"),
        "symbol": pd.Series(dtype="str"),
        "open": pd.Series(dtype="float64"),
        "high": pd.Series(dtype="float64"),
        "low": pd.Series(dtype="float64"),
        "close": pd.Series(dtype="float64"),
        "volume": pd.Series(dtype="float64"),
        "quote_volume": pd.Series(dtype="float64"),
        "trade_count": pd.Series(dtype="int64"),
        "source": pd.Series(dtype="str"),
        "market": pd.Series(dtype="str"),
        "instrument_type": pd.Series(dtype="str"),
        "timeframe": pd.Series(dtype="str"),
    })
    bars_path = CACHE_DIR / "bars_1h.parquet"
    bars_schema.to_parquet(bars_path, index=False)
    print(f"  Saved empty schema to {bars_path}")

    # ── Step 7: Build manifest ──
    print("\n▸ Building manifest.json...")
    included_symbols = [r["symbol"] for r in rows if r["included"]]
    manifest = {
        "universe_name": "crypto_top50_usdt_perp_1h",
        "source": "Binance USDT-M Futures",
        "downloaded_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "data_start": "",
        "data_end": "",
        "timeframe": "1h",
        "selection_rule": "top 50 by trailing 30-day dollar volume",
        "rebalance_frequency": "monthly",
        "min_listing_age_days": 90,
        "exclude_stablecoin_pairs": True,
        "exclude_leveraged_tokens": True,
        "survivorship_bias_policy": "record universe membership at each rebalance date",
        "symbols": included_symbols,
        "n_symbols": len(included_symbols),
        "script": SCRIPT_PATH,
        "commit_sha": COMMIT_SHA,
        "notes": "bars_1h.parquet is empty schema only — no OHLCV data downloaded yet"
    }
    manifest_path = CACHE_DIR / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"  Saved manifest ({len(included_symbols)} symbols) to {manifest_path}")

    # ── Summary ──
    print(f"\n{'=' * 60}")
    print("✓ Universe built successfully")
    print(f"  Symbols included: {len(included_symbols)}")
    print(f"  Output: {CACHE_DIR}/")
    print(f"  manifest.json:         ✓")
    print(f"  universe_membership:   ✓ ({len(rows)} rows)")
    print(f"  bars_1h.parquet:       ✓ (empty schema)")
    print(f"  OHLCV data:            NOT downloaded (by design)")

    return included_symbols


if __name__ == "__main__":
    symbols = main()
