#!/usr/bin/env python3
"""Build registered research factor values for the crypto Top50 1h universe.

Now uses factor_formula_registry.REGISTRY for all factor computation.
Iterates FactorSpec list — no hand-coded factor logic in this file.

Supports optional factor subset via --factor-ids or --candidate-csv + --status.
"""
from __future__ import annotations

import argparse
import csv as _csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_ID = "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1"
TAKER_BARS_PATH = ROOT / "data" / "cache" / f"{DEFAULT_DATASET_ID}_taker_enriched" / "bars_1h.parquet"
TAKER_REQUIRED_COLUMNS = {"taker_buy_volume", "taker_buy_quote_volume"}
FUNDING_RATE_PATH = ROOT / "data" / "cache" / "crypto_funding_rate_1h_contract_v1" / "funding_rate_1h_aligned_dynamic.parquet"
FUNDING_REQUIRED_COLUMNS = {"funding_rate"}
MARKET_CAP_PATH = ROOT / "data" / "cache" / "crypto_market_cap_1h_contract_v1" / "market_cap_1h_aligned.parquet"
CAP_REQUIRED_COLUMNS = {"cap"}

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))
from factor_formula_registry import REGISTRY, REGISTRY_BY_ID


def load_selected_factor_ids(candidate_csv: Path, status: str = "selected_for_7B") -> list[str]:
    """Load factor_ids from candidate CSV filtered by status."""
    with open(candidate_csv, newline="") as f:
        rows = list(_csv.DictReader(f))
    ids = [r["factor_id"] for r in rows if r["status"] == status]
    if not ids:
        raise ValueError(f"No factors with status={status!r} in {candidate_csv}")
    return ids


def validate_factor_ids(factor_ids: Sequence[str]) -> None:
    """Fail fast if any factor_id is not in REGISTRY."""
    registry_ids = set(REGISTRY_BY_ID.keys())
    missing = [fid for fid in factor_ids if fid not in registry_ids]
    if missing:
        raise ValueError(f"Factor IDs not in REGISTRY: {missing}")


def apply_cross_sectional_postprocess(wide: pd.DataFrame) -> pd.DataFrame:
    """Apply cross-sectional rank normalization to xs_rank_* factors.

    For factors that require ranking across symbols at each timestamp,
    this replaces the per-symbol raw metric with a percentile rank.
    """
    wide = wide.copy()
    xs_factors = ["xs_rank_ret_1h", "xs_rank_vol", "xs_rank_mom_accel"]
    for factor in xs_factors:
        if factor in wide.columns:
            wide[factor] = (
                wide.groupby("timestamp")[factor]
                .rank(pct=True, method="average")
            )
    return wide


def calc_group(g: pd.DataFrame, factor_ids: Sequence[str] | None = None) -> pd.DataFrame:
    """Compute registered factors for a single-symbol group.

    Args:
        g: DataFrame for one symbol (must have timestamp, OHLCV).
        factor_ids: If provided, only compute these factor_ids.
                    If None, compute all REGISTRY factors.
    """
    g = g.copy().sort_values("timestamp")
    result_cols = ["timestamp", "symbol"]
    specs = REGISTRY if factor_ids is None else [REGISTRY_BY_ID[fid] for fid in factor_ids]
    for spec in specs:
        g[spec.factor_id] = spec.compute_fn(g)
        result_cols.append(spec.factor_id)
    return g[result_cols]


def _needs_taker_source(spec) -> bool:
    """Check if a factor spec requires taker columns."""
    return bool(set(spec.required_columns) & TAKER_REQUIRED_COLUMNS)


def _needs_funding_source(spec) -> bool:
    """Check if a factor spec requires funding_rate column."""
    return bool(set(spec.required_columns) & FUNDING_REQUIRED_COLUMNS)


def _needs_cap_source(spec) -> bool:
    """Check if a factor spec requires cap column."""
    return bool(set(spec.required_columns) & CAP_REQUIRED_COLUMNS)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset-id", default=DEFAULT_DATASET_ID,
                    help="Dataset ID under data/cache/ and data/features/")
    p.add_argument("--factor-ids", default=None,
                    help="Comma-separated factor_ids to build (default: all REGISTRY)")
    p.add_argument("--candidate-csv", default=None,
                    help="Path to candidate CSV; use with --status to select factors")
    p.add_argument("--status", default="selected_for_7B",
                    help="Status filter for --candidate-csv (default: selected_for_7B)")
    p.add_argument("--allow-blocked", action="store_true",
                    help="Allow blocked factors (e.g. missing cap) without non-zero exit")
    args = p.parse_args()

    # Determine which factors to build
    if args.factor_ids:
        factor_ids = [s.strip() for s in args.factor_ids.split(",")]
    elif args.candidate_csv:
        csv_path = Path(args.candidate_csv)
        if not csv_path.is_absolute():
            csv_path = ROOT / csv_path
        factor_ids = load_selected_factor_ids(csv_path, args.status)
    else:
        factor_ids = [spec.factor_id for spec in REGISTRY]

    validate_factor_ids(factor_ids)

    cache = ROOT / "data" / "cache" / args.dataset_id
    feature = ROOT / "data" / "features" / args.dataset_id
    bars_path = cache / "bars_1h.parquet"

    print(f"Build factor values (registry mode)")
    print(f"Dataset: {args.dataset_id}")
    print(f"Building {len(factor_ids)} factors: {factor_ids}")

    if not bars_path.exists():
        print(f"ERROR: bars file not found: {bars_path}", flush=True)
        print(f"  Dataset ID: {args.dataset_id}", flush=True)
        print(f"  Expected:   data/cache/{args.dataset_id}/bars_1h.parquet", flush=True)
        print(f"  Hint: pass --dataset-id explicitly if using a non-default dataset", flush=True)
        _sys.exit(1)

    # Split factors into taker, funding, ordinary, and panel groups
    taker_factor_ids = [fid for fid in factor_ids if _needs_taker_source(REGISTRY_BY_ID[fid])]
    funding_factor_ids = [fid for fid in factor_ids if _needs_funding_source(REGISTRY_BY_ID[fid])]
    panel_factor_ids = [fid for fid in factor_ids if REGISTRY_BY_ID[fid].compute_scope == "panel"]
    ordinary_factor_ids = [fid for fid in factor_ids if fid not in taker_factor_ids and fid not in funding_factor_ids and fid not in panel_factor_ids]

    bars = pd.read_parquet(bars_path)
    if bars.empty:
        raise ValueError("bars_1h.parquet is empty; fetch bars first")
    bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True)
    bars = bars.sort_values(["symbol", "timestamp"])

    parts = []
    # Build ordinary factors from canonical bars
    if ordinary_factor_ids:
        print(f"  Source: canonical bars ({len(ordinary_factor_ids)} factors)")
        for _sym, g in bars.groupby("symbol", sort=False):
            parts.append(calc_group(g, ordinary_factor_ids))

    # Build taker factors from taker-enriched bars
    if taker_factor_ids:
        if not TAKER_BARS_PATH.exists():
            print(f"ERROR: taker-enriched bars not found: {TAKER_BARS_PATH}")
            _sys.exit(1)
        taker_bars = pd.read_parquet(TAKER_BARS_PATH)
        taker_bars["timestamp"] = pd.to_datetime(taker_bars["timestamp"], utc=True)
        taker_bars = taker_bars.sort_values(["symbol", "timestamp"])
        missing_cols = TAKER_REQUIRED_COLUMNS - set(taker_bars.columns)
        if missing_cols:
            print(f"ERROR: taker-enriched bars missing columns: {missing_cols}")
            _sys.exit(1)
        print(f"  Source: taker-enriched bars ({len(taker_factor_ids)} factors)")
        for _sym, g in taker_bars.groupby("symbol", sort=False):
            parts.append(calc_group(g, taker_factor_ids))

    # Build funding factors from canonical bars merged with funding data
    if funding_factor_ids:
        if not FUNDING_RATE_PATH.exists():
            print(f"ERROR: funding rate file not found: {FUNDING_RATE_PATH}")
            _sys.exit(1)
        funding = pd.read_parquet(FUNDING_RATE_PATH, columns=["timestamp", "symbol", "funding_rate"])
        funding["timestamp"] = pd.to_datetime(funding["timestamp"], utc=True)
        if funding.duplicated(["timestamp", "symbol"]).any():
            print("ERROR: funding rate file has duplicate row keys")
            _sys.exit(1)
        funding_null_rate = funding["funding_rate"].isna().mean()
        print(f"  Source: canonical bars + funding_rate (dynamic) ({len(funding_factor_ids)} factors, funding null={funding_null_rate:.1%})")
        # Merge funding into bars in memory
        merged = bars.merge(funding[["timestamp", "symbol", "funding_rate"]], on=["timestamp", "symbol"], how="left")
        for _sym, g in merged.groupby("symbol", sort=False):
            parts.append(calc_group(g, funding_factor_ids))

    # Build panel factors (cross-sectional, need all symbols at once)
    blocked_factors = []
    if panel_factor_ids:
        print(f"  Source: panel computation ({len(panel_factor_ids)} factors)")
        # Split panel factors into cap-needing and non-cap-needing
        cap_panel_ids = [fid for fid in panel_factor_ids if _needs_cap_source(REGISTRY_BY_ID[fid])]
        non_cap_panel_ids = [fid for fid in panel_factor_ids if not _needs_cap_source(REGISTRY_BY_ID[fid])]

        # Load cap data if needed
        bars_with_cap = None
        if cap_panel_ids:
            if not MARKET_CAP_PATH.exists():
                print(f"  ERROR: Market cap file not found: {MARKET_CAP_PATH}")
                print(f"  Run: python scripts/build_crypto_market_cap_1h.py first")
                for fid in cap_panel_ids:
                    blocked_factors.append((fid, f"Missing market cap file: {MARKET_CAP_PATH}"))
                    print(f"  BLOCKED: {fid} — missing market cap file")
                cap_panel_ids = []
            else:
                cap_df = pd.read_parquet(MARKET_CAP_PATH, columns=["timestamp", "symbol", "cap", "cap_source_timestamp", "cap_known_at", "cap_quality_flag"])
                cap_df["timestamp"] = pd.to_datetime(cap_df["timestamp"], utc=True)
                if cap_df.duplicated(["timestamp", "symbol"]).any():
                    print("  ERROR: Market cap file has duplicate row keys")
                    _sys.exit(1)
                cap_coverage = cap_df["cap"].notna().mean()
                print(f"  Market cap loaded: {len(cap_df)} rows, coverage={cap_coverage:.1%}")
                bars_with_cap = bars.merge(cap_df, on=["timestamp", "symbol"], how="left")
                print(f"  bars_with_cap: {len(bars_with_cap)} rows, cap coverage after merge={bars_with_cap['cap'].notna().mean():.1%}")

        # Process non-cap panel factors
        for fid in non_cap_panel_ids:
            spec = REGISTRY_BY_ID[fid]
            missing_cols = set(spec.required_columns) - set(bars.columns)
            if missing_cols:
                blocked_factors.append((fid, f"Missing columns: {missing_cols}"))
                print(f"  BLOCKED: {fid} — missing columns: {missing_cols}")
                continue
            try:
                factor_df = spec.panel_compute_fn(bars)
                expected_cols = {"timestamp", "symbol", fid}
                if not expected_cols.issubset(set(factor_df.columns)):
                    print(f"  ERROR: {fid} — panel_compute_fn returned columns {factor_df.columns.tolist()}, expected {expected_cols}")
                    blocked_factors.append((fid, f"Bad output columns: {factor_df.columns.tolist()}"))
                    continue
                factor_df = factor_df[["timestamp", "symbol", fid]]
                parts.append(factor_df)
                print(f"  {fid}: panel computed, rows={len(factor_df)} coverage={factor_df[fid].notna().mean():.3%}")
            except Exception as e:
                blocked_factors.append((fid, str(e)))
                print(f"  BLOCKED: {fid} — {e}")

        # Process cap panel factors
        for fid in cap_panel_ids:
            if bars_with_cap is None:
                blocked_factors.append((fid, "bars_with_cap not available"))
                print(f"  BLOCKED: {fid} — bars_with_cap not available")
                continue
            spec = REGISTRY_BY_ID[fid]
            try:
                factor_df = spec.panel_compute_fn(bars_with_cap)
                expected_cols = {"timestamp", "symbol", fid}
                if not expected_cols.issubset(set(factor_df.columns)):
                    print(f"  ERROR: {fid} — panel_compute_fn returned columns {factor_df.columns.tolist()}, expected {expected_cols}")
                    blocked_factors.append((fid, f"Bad output columns: {factor_df.columns.tolist()}"))
                    continue
                factor_df = factor_df[["timestamp", "symbol", fid]]
                parts.append(factor_df)
                print(f"  {fid}: panel computed (with cap), rows={len(factor_df)} coverage={factor_df[fid].notna().mean():.3%}")
            except Exception as e:
                blocked_factors.append((fid, str(e)))
                print(f"  BLOCKED: {fid} — {e}")

    wide = pd.concat(parts, ignore_index=True)
    wide = apply_cross_sectional_postprocess(wide)

    computed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Track which factors were actually computed
    computed_factor_ids = set()
    for name in factor_ids:
        if name not in wide.columns:
            continue
        computed_factor_ids.add(name)
        out = wide[["timestamp", "symbol", name]].rename(columns={name: "factor_value"})
        out.insert(2, "factor_name", name)
        out["known_at"] = out["timestamp"]
        out["source_timeframe"] = "1h"
        out["computed_at"] = computed_at
        out = out[["timestamp", "symbol", "factor_name", "factor_value",
                    "known_at", "source_timeframe", "computed_at"]]
        target_dir = feature / name
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / "factor_values.parquet"
        out.to_parquet(target, index=False)
        print(f"  {name}: rows={len(out)} coverage={out['factor_value'].notna().mean():.3%}")

    # Report blocked factors
    if blocked_factors:
        print(f"\nBlocked factors: {len(blocked_factors)}")
        for fid, reason in blocked_factors:
            print(f"  {fid}: {reason}")
        if not args.allow_blocked:
            _sys.exit(1)

    # Report which requested factors were not computed
    missed = [fid for fid in factor_ids if fid not in computed_factor_ids and fid not in [b[0] for b in blocked_factors]]
    if missed:
        print(f"\nWARNING: These requested factors were not computed and not blocked: {missed}")


if __name__ == "__main__":
    main()
