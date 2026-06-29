#!/usr/bin/env python3
"""PM-29B: Capacity / Liquidity Proxy Diagnostics (Selected-Basket Upgrade).

Upgrades PM-29 from universe-wide volume proxy to selected-basket proxy.
For each factor, at each sampled timestamp, we:
  1. Load factor values, rank cross-section by factor value (direction-adjusted)
  2. Select long basket (top 20%) and short basket (bottom 20%) matching paper convention
  3. Join with hourly bar volume and compute selected-basket liquidity metrics

Performance: Uses deterministic 4-hourly sampling (~17K timestamps → ~4.3K) to keep
runtime manageable while covering the full universe. The sampling is every 4th hour
starting from the first available timestamp in the volume data.

Outputs 5 files into factor_diagnostics/:
  - factor_capacity_liquidity_summary.csv
  - factor_capacity_liquidity_summary.json
  - factor_capacity_liquidity_monthly.csv
  - factor_capacity_liquidity_payload.json  (compact, for PM-30 page integration)
  - factor_capacity_liquidity_manifest.json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from public_factor_manifest_guard import raise_for_skipped_public_factor_ids

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DIAG = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_diagnostics"
VOLUME_PARQUET = (
    ROOT / "data" / "cache"
    / "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1"
    / "bars_1h.parquet"
)
DATA_BASE = ROOT / "data" / "features" / "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1"
STATE_PATH = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_library_state.json"

# Basket selection: match paper portfolio convention
TOP_FRAC = 0.20
BOTTOM_FRAC = 0.20
MIN_NAMES = 10  # minimum cross-section size to consider

# Sampling: every N-th hour timestamp for performance
SAMPLE_EVERY_N_HOURS = 4

# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------
# Capacity risk: based on median participation rate at $10M AUM using selected-basket volume
CAP_THRESHOLDS = {
    "CAPACITY_BLOCKED_BY_TURNOVER": 0.20,
    "CAPACITY_FRAGILE": 0.10,
    "MODERATE_CAPACITY_RISK": 0.02,
    # else CAPACITY_FRIENDLY
}

# Liquidity risk: based on p10 hourly volume of names in the selected basket
LIQ_THRESHOLDS = {
    "LIQUIDITY_FRAGILE": 500_000,            # p10 hourly vol < $500K
    "LOW_VOLUME_EXPOSURE": 2_000_000,        # median hourly vol < $2M
    # CONCENTRATED_LIQUIDITY if top-5 share > 80%
}

# Volume concentration thresholds
CONC_THRESHOLDS = {
    "DIVERSIFIED_LIQUIDITY": 0.50,       # top symbol share < 50%
    "MODERATE_CONCENTRATION": 0.70,      # < 70%
    "HIGH_CONCENTRATION": 0.85,          # < 85%
    # else EXTREME_CONCENTRATION
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_float(v: Any) -> float | None:
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    return float(v)


def _classify_capacity(median_participation_10m: float) -> str:
    """Classify capacity risk based on participation rate at $10M AUM."""
    if median_participation_10m >= CAP_THRESHOLDS["CAPACITY_BLOCKED_BY_TURNOVER"]:
        return "CAPACITY_BLOCKED_BY_TURNOVER"
    if median_participation_10m >= CAP_THRESHOLDS["CAPACITY_FRAGILE"]:
        return "CAPACITY_FRAGILE"
    if median_participation_10m >= CAP_THRESHOLDS["MODERATE_CAPACITY_RISK"]:
        return "MODERATE_CAPACITY_RISK"
    return "CAPACITY_FRIENDLY"


def _classify_liquidity(median_hourly_vol: float, p10_hourly_vol: float,
                        concentration_ratio: float) -> str:
    """Classify liquidity risk based on per-symbol volume distribution."""
    if median_hourly_vol <= 0 or np.isnan(median_hourly_vol):
        return "INSUFFICIENT_DATA"
    if concentration_ratio > 0.80:
        return "CONCENTRATED_LIQUIDITY"
    if p10_hourly_vol < LIQ_THRESHOLDS["LIQUIDITY_FRAGILE"]:
        return "LIQUIDITY_FRAGILE"
    if median_hourly_vol < LIQ_THRESHOLDS["LOW_VOLUME_EXPOSURE"]:
        return "LOW_VOLUME_EXPOSURE"
    return "LIQUIDITY_FRIENDLY"


def _classify_volume_concentration(top_symbol_share_median: float) -> str:
    """Classify volume concentration of selected basket."""
    if np.isnan(top_symbol_share_median) or top_symbol_share_median <= 0:
        return "INSUFFICIENT_DATA"
    if top_symbol_share_median < CONC_THRESHOLDS["DIVERSIFIED_LIQUIDITY"]:
        return "DIVERSIFIED_LIQUIDITY"
    if top_symbol_share_median < CONC_THRESHOLDS["MODERATE_CONCENTRATION"]:
        return "MODERATE_CONCENTRATION"
    if top_symbol_share_median < CONC_THRESHOLDS["HIGH_CONCENTRATION"]:
        return "HIGH_CONCENTRATION"
    return "EXTREME_CONCENTRATION"


def _classify_combined(cap_cls: str, liq_cls: str) -> str:
    if cap_cls == "INSUFFICIENT_DATA" or liq_cls == "INSUFFICIENT_DATA":
        return "INSUFFICIENT_DATA"
    cap_ok = cap_cls in ("CAPACITY_FRIENDLY", "MODERATE_CAPACITY_RISK")
    liq_ok = liq_cls in ("LIQUIDITY_FRIENDLY",)
    if cap_ok and liq_ok:
        return "CAPACITY_LIQUIDITY_OK"
    if not cap_ok and not liq_ok:
        return "WATCH_BOTH"
    if not cap_ok:
        return "WATCH_TURNOVER"
    return "WATCH_LIQUIDITY"


def _assign_flags(
    cap_cls: str,
    liq_cls: str,
    combined_cls: str,
    gross_sharpe: float | None,
    cost_cls: str | None,
    stability_cls: str | None,
) -> list[str]:
    flags: list[str] = []
    has_good_alpha = gross_sharpe is not None and gross_sharpe > 1.5
    is_stable = stability_cls in ("STABLE_POSITIVE", "STABLE_WEAK")
    is_fragile_cap = cap_cls in ("CAPACITY_FRAGILE", "CAPACITY_BLOCKED_BY_TURNOVER")
    is_fragile_liq = liq_cls in ("LIQUIDITY_FRAGILE", "CONCENTRATED_LIQUIDITY")
    is_cheap = cost_cls in ("LOW_COST_SENSITIVE",)
    is_weak_signal = gross_sharpe is not None and gross_sharpe < 1.0

    if has_good_alpha and is_fragile_cap:
        flags.append("GOOD_ALPHA_BUT_CAPACITY_FRAGILE")
    if is_stable and is_fragile_liq:
        flags.append("STABLE_BUT_TOO_ILLIQUID")
    if is_cheap and is_weak_signal:
        flags.append("CHEAP_TO_TRADE_BUT_WEAK_SIGNAL")
    if not flags and combined_cls == "CAPACITY_LIQUIDITY_OK":
        flags.append("BALANCED_CANDIDATE")

    return flags


def load_registered_factors() -> list[str]:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return state.get("registered_factor_ids", [])


def load_factor_directions() -> dict[str, str]:
    directions = {}
    try:
        sc = pd.read_csv(DIAG / "factor_quality_scorecard.csv")
        for _, row in sc.iterrows():
            directions[row["factor_id"]] = row.get("expected_direction", "positive")
    except Exception:
        pass
    return directions


def compute_selected_basket_volume_metrics(
    factor_df: pd.DataFrame,
    vol_lookup: dict[str, pd.DataFrame],
    direction: str,
) -> list[dict[str, float]]:
    """For each timestamp in factor_df, rank cross-section, select long/short baskets,
    and compute volume metrics using actual hourly volume data.

    Returns a list of dicts (one per timestamp) with:
      - timestamp, n_total, n_long, n_short
      - long_basket_volume_median, short_basket_volume_median
      - long_basket_volume_p10, short_basket_volume_p10
      - selected_basket_volume_median, selected_basket_volume_p10
      - long_top_symbol_volume_share, short_top_symbol_volume_share
      - selected_top_symbol_volume_share
      - low_volume_symbol_share (fraction of selected basket with vol < $100K)
    """
    fv = factor_df.copy()
    if direction == "negative":
        fv["factor_value"] = -fv["factor_value"]

    # Group by timestamp
    records = []
    for ts, grp in fv.groupby("timestamp"):
        grp = grp.dropna(subset=["factor_value"])
        n = len(grp)
        if n < MIN_NAMES:
            continue

        # Rank descending
        grp = grp.sort_values("factor_value", ascending=False).reset_index(drop=True)
        n_long = max(int(n * TOP_FRAC), 1)
        n_short = max(int(n * BOTTOM_FRAC), 1)

        long_symbols = set(grp["symbol"].iloc[:n_long].values)
        short_symbols = set(grp["symbol"].iloc[-n_short:].values)

        # Look up hourly volume for this timestamp
        ts_key = ts
        if isinstance(ts_key, pd.Timestamp):
            ts_key = ts_key
        vol_at_ts = vol_lookup.get(ts_key)
        if vol_at_ts is None:
            continue

        # Get volumes for selected basket symbols
        all_selected = long_symbols | short_symbols
        vol_selected = vol_at_ts[vol_at_ts["symbol"].isin(all_selected)]
        vol_long = vol_at_ts[vol_at_ts["symbol"].isin(long_symbols)]
        vol_short = vol_at_ts[vol_at_ts["symbol"].isin(short_symbols)]

        if vol_selected.empty:
            continue

        # Volume stats for selected baskets
        def _vol_stats(vol_series: pd.Series) -> dict:
            if vol_series.empty:
                return {"median": np.nan, "p10": np.nan, "top_share": np.nan}
            s = vol_series.values
            total = s.sum()
            top_share = float(np.max(s) / total) if total > 0 else np.nan
            return {
                "median": float(np.median(s)),
                "p10": float(np.percentile(s, 10)),
                "top_share": top_share,
            }

        long_stats = _vol_stats(vol_long["quote_volume"]) if not vol_long.empty else {"median": np.nan, "p10": np.nan, "top_share": np.nan}
        short_stats = _vol_stats(vol_short["quote_volume"]) if not vol_short.empty else {"median": np.nan, "p10": np.nan, "top_share": np.nan}
        selected_stats = _vol_stats(vol_selected["quote_volume"])

        # Low volume share: fraction of selected basket symbols with hourly vol < $100K
        low_vol_count = (vol_selected["quote_volume"] < 100_000).sum()
        low_vol_share = low_vol_count / len(vol_selected) if len(vol_selected) > 0 else np.nan

        records.append({
            "timestamp": ts,
            "n_total": n,
            "n_long": n_long,
            "n_short": n_short,
            "selected_symbol_count": len(all_selected),
            "long_basket_volume_median": long_stats["median"],
            "long_basket_volume_p10": long_stats["p10"],
            "short_basket_volume_median": short_stats["median"],
            "short_basket_volume_p10": short_stats["p10"],
            "selected_basket_volume_median": selected_stats["median"],
            "selected_basket_volume_p10": selected_stats["p10"],
            "long_top_symbol_volume_share": long_stats["top_share"],
            "short_top_symbol_volume_share": short_stats["top_share"],
            "selected_top_symbol_volume_share": selected_stats["top_share"],
            "low_volume_symbol_share": low_vol_share,
        })

    return records


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _resolve_target_factor_ids(
    args: argparse.Namespace, diag_dir: Path,
) -> tuple[list[str] | None, bool]:
    """Return (target_ids, is_subset_mode) based on CLI args.

    If neither --factor-ids nor --only-missing is set, returns (None, False)
    meaning "process all factors" (original behavior).
    """
    if args.factor_ids:
        ids = [s.strip() for s in args.factor_ids.split(",") if s.strip()]
        return ids, True
    if args.only_missing:
        evidence_path = diag_dir / "factor_evaluation_evidence_matrix.csv"
        if not evidence_path.exists():
            print(f"  WARNING: evidence matrix not found at {evidence_path}, falling back to all factors")
            return None, False
        ev = pd.read_csv(evidence_path)
        if "has_capacity_liquidity" not in ev.columns:
            print("  WARNING: 'has_capacity_liquidity' column not in evidence matrix, falling back to all factors")
            return None, False
        missing = ev[ev["has_capacity_liquidity"] == False]["factor_id"].tolist()  # noqa: E712
        print(f"  --only-missing: {len(missing)} factors missing capacity/liquidity")
        if not missing:
            return [], True
        return missing, True
    return None, False


def main():
    parser = argparse.ArgumentParser(description="PM-29B capacity/liquidity diagnostics (selected-basket proxy)")
    parser.add_argument("--notionals", default="100000,1000000,10000000",
                        help="Comma-separated notional sizes in USD")
    parser.add_argument("--sample-hours", type=int, default=SAMPLE_EVERY_N_HOURS,
                        help="Sample every N hours (default: 4, set to 1 for full precision)")
    parser.add_argument("--max-factors", type=int, default=0,
                        help="Limit number of factors (0=all)")
    parser.add_argument("--factor-ids", type=str, default=None,
                        help="PM-36: Comma-separated factor IDs to compute (subset mode)")
    parser.add_argument("--only-missing", action="store_true", default=False,
                        help="PM-36: Auto-detect factors missing capacity/liquidity from evidence matrix")
    args = parser.parse_args()
    notionals = sorted([int(x) for x in args.notionals.split(",")])
    sample_hours = args.sample_hours

    # PM-36: Resolve subset mode
    target_factor_ids, is_subset_mode = _resolve_target_factor_ids(args, DIAG)
    if is_subset_mode:
        print(f"[PM-29B] SUBSET MODE: processing {len(target_factor_ids or [])} target factor(s)")
    if target_factor_ids:
        try:
            raise_for_skipped_public_factor_ids(
                target_factor_ids,
                action="capacity/liquidity diagnosed",
            )
        except ValueError as exc:
            print(f"ERROR: {exc}")
            return 1

    print(f"[PM-29B] Notionals: {notionals}")
    print(f"[PM-29B] Sample interval: every {sample_hours}h")
    print(f"[PM-29B] Basket selection: top {TOP_FRAC:.0%} long, bottom {BOTTOM_FRAC:.0%} short")

    # -----------------------------------------------------------------------
    # 1. Load turnover data
    # -----------------------------------------------------------------------
    turnover_path = DIAG / "single_factor_paper_turnover.csv"
    to_df = pd.read_csv(turnover_path)
    factors_with_turnover = to_df["factor_id"].nunique()
    print(f"[PM-29B] Loaded turnover data: {len(to_df)} rows, {factors_with_turnover} factors")

    # -----------------------------------------------------------------------
    # 2. Load volume data
    # -----------------------------------------------------------------------
    vol_df = pd.read_parquet(VOLUME_PARQUET)
    print(f"[PM-29B] Loaded volume data: {len(vol_df)} rows, {vol_df['symbol'].nunique()} symbols")

    # Build timestamp-indexed volume lookup for fast per-timestamp queries
    vol_df["timestamp"] = pd.to_datetime(vol_df["timestamp"])
    all_vol_ts = vol_df["timestamp"].sort_values().unique()

    # Sample timestamps deterministically: every N hours
    # IMPORTANT: keep as pandas Timestamp (with tz) to match factor_value timestamps
    ts_series = pd.Series(all_vol_ts)
    if sample_hours > 1:
        sampled_ts_series = ts_series.iloc[::sample_hours]
        print(f"[PM-29B] Volume timestamps: {len(all_vol_ts)} total, sampling every {sample_hours}h → {len(sampled_ts_series)} timestamps")
    else:
        sampled_ts_series = ts_series
        print(f"[PM-29B] Volume timestamps: {len(all_vol_ts)} total, using all (no sampling)")
    sampled_vol_ts: list = list(sampled_ts_series)  # list of pd.Timestamp with tz

    # Build lookup dict: timestamp → DataFrame with symbol, quote_volume
    # Use groupby for speed instead of per-timestamp filtering
    vol_lookup: dict = {}
    vol_grouped = vol_df.groupby("timestamp")
    for ts in sampled_vol_ts:
        if ts in vol_grouped.groups:
            chunk = vol_grouped.get_group(ts)[["symbol", "quote_volume"]].copy()
            vol_lookup[ts] = chunk

    print(f"[PM-29B] Built volume lookup for {len(vol_lookup)} timestamps")

    # Also compute universe-wide stats for fallback
    per_sym_hourly = vol_df.groupby("symbol")["quote_volume"].median()
    universe_hourly_median = float(per_sym_hourly.median())
    universe_hourly_p10 = float(np.percentile(per_sym_hourly.values, 10))
    universe_hourly_mean = float(per_sym_hourly.mean())
    sorted_vols = per_sym_hourly.sort_values(ascending=False)
    total_hourly = sorted_vols.sum()
    concentration_ratio = float(sorted_vols.head(5).sum() / total_hourly) if total_hourly > 0 else 0

    print(f"[PM-29B] Universe ref (top-50): median=${universe_hourly_median:,.0f}, p10=${universe_hourly_p10:,.0f}")

    # -----------------------------------------------------------------------
    # 3. Load cross-check data
    # -----------------------------------------------------------------------
    summary_df = pd.read_csv(DIAG / "single_factor_paper_summary.csv")
    quality_df = pd.read_csv(DIAG / "factor_quality_scorecard.csv")
    regime_df = pd.read_csv(DIAG / "factor_regime_exposure_summary.csv")

    # Shape stability payload
    with open(DIAG / "factor_shape_stability_payload.json") as f:
        shape_payload = json.load(f)
    shape_map: dict[str, dict] = {}
    for entry in shape_payload["factors"]:
        fid = entry["factor_id"]
        h = entry.get("horizons", {})
        if isinstance(h, dict) and "1h" in h:
            shape_map[fid] = {
                "quantile_shape_class": h["1h"].get("shape", {}).get("quantile_shape_class"),
                "stability_class": h["1h"].get("stability", {}).get("stability_class"),
                "stability_score": h["1h"].get("stability", {}).get("stability_score"),
            }

    # Decile shape payload
    with open(DIAG / "factor_decile_shape_payload.json") as f:
        decile_payload = json.load(f)
    decile_map: dict[str, dict] = {}
    for entry in decile_payload["factors"]:
        fid = entry["factor_id"]
        h = entry.get("horizons", {})
        if isinstance(h, dict) and "1h" in h:
            decile_map[fid] = {
                "decile_shape_class": h["1h"].get("decile_shape_class"),
            }

    # Build lookup dicts
    summary_lookup = summary_df.set_index("factor_id").to_dict("index")
    regime_lookup = regime_df.set_index("factor_id").to_dict("index")
    quality_lookup = quality_df.set_index("factor_id").to_dict("index")

    # Factor list
    directions = load_factor_directions()
    all_factors = load_registered_factors()
    if args.max_factors > 0:
        all_factors = all_factors[:args.max_factors]

    # PM-36: Filter to target subset if requested
    if is_subset_mode and target_factor_ids is not None:
        all_factor_set = set(all_factors)
        valid_targets = [fid for fid in target_factor_ids if fid in all_factor_set]
        invalid = [fid for fid in target_factor_ids if fid not in all_factor_set]
        if invalid:
            print(f"[PM-29B] WARNING: {len(invalid)} target IDs not in registered list (skipped): {invalid[:5]}...")
        all_factors = valid_targets
        print(f"[PM-29B] Target factors to compute: {len(all_factors)}")
        if not all_factors:
            print("[PM-29B] No factors need computation. Outputs already up to date.")
            return 0

    print(f"[PM-29B] Processing {len(all_factors)} factors")

    # -----------------------------------------------------------------------
    # 4. Compute per-factor capacity/liquidity diagnostics (selected-basket)
    # -----------------------------------------------------------------------
    summary_rows: list[dict] = []
    monthly_rows: list[dict] = []
    payload_factors: list[dict] = []
    processed = 0
    errors = 0

    import time as _time
    t0 = _time.time()

    for fi, fid in enumerate(all_factors):
        fto = to_df[to_df["factor_id"] == fid].copy()
        if fto.empty:
            errors += 1
            continue

        # Load factor values
        fv_path = DATA_BASE / fid / "factor_values.parquet"
        if not fv_path.exists():
            errors += 1
            continue
        fv = pd.read_parquet(fv_path, columns=["timestamp", "symbol", "factor_value"])
        fv = fv.dropna(subset=["factor_value"])
        if fv.empty:
            errors += 1
            continue

        fv["timestamp"] = pd.to_datetime(fv["timestamp"])

        # Filter to sampled volume timestamps that exist in fv
        fv_ts_set = set(fv["timestamp"].unique())
        overlap_ts = [ts for ts in sampled_vol_ts if ts in fv_ts_set]
        if not overlap_ts:
            errors += 1
            continue
        fv_sampled = fv[fv["timestamp"].isin(set(overlap_ts))]

        direction = directions.get(fid, "positive")

        # Compute selected-basket volume metrics
        basket_records = compute_selected_basket_volume_metrics(
            fv_sampled, vol_lookup, direction
        )

        if not basket_records:
            # Fallback to universe proxy
            liquidity_proxy_method = "universe_volume_proxy"
            ref_vol_median = universe_hourly_median
            ref_vol_p10 = universe_hourly_p10
            vol_concentration = concentration_ratio
            selected_sym_count_median = float("nan")
            long_vol_median = universe_hourly_median
            short_vol_median = universe_hourly_median
            long_vol_p10 = universe_hourly_p10
            short_vol_p10 = universe_hourly_p10
            sel_vol_median = universe_hourly_median
            sel_vol_p10 = universe_hourly_p10
            long_top_share_median = concentration_ratio
            short_top_share_median = concentration_ratio
            sel_top_share_median = concentration_ratio
            low_vol_share_median = float("nan")
            vol_conc_class = "INSUFFICIENT_DATA"
        else:
            liquidity_proxy_method = "selected_basket_proxy"
            br = pd.DataFrame(basket_records)

            selected_sym_count_median = float(br["selected_symbol_count"].median())
            long_vol_median = float(np.nanmedian(br["long_basket_volume_median"]))
            short_vol_median = float(np.nanmedian(br["short_basket_volume_median"]))
            long_vol_p10 = float(np.nanpercentile(br["long_basket_volume_p10"].dropna(), 10))
            short_vol_p10 = float(np.nanpercentile(br["short_basket_volume_p10"].dropna(), 10))
            sel_vol_median = float(np.nanmedian(br["selected_basket_volume_median"]))
            sel_vol_p10 = float(np.nanpercentile(br["selected_basket_volume_p10"].dropna(), 10))
            long_top_share_median = float(np.nanmedian(br["long_top_symbol_volume_share"]))
            short_top_share_median = float(np.nanmedian(br["short_top_symbol_volume_share"]))
            sel_top_share_median = float(np.nanmedian(br["selected_top_symbol_volume_share"]))
            low_vol_share_median = float(np.nanmedian(br["low_volume_symbol_share"]))

            # Use selected basket median volume as the reference for capacity
            ref_vol_median = sel_vol_median
            ref_vol_p10 = sel_vol_p10

            # Volume concentration class based on selected basket top-symbol share
            vol_conc_class = _classify_volume_concentration(sel_top_share_median)

        # Turnover stats
        avg_turnover = float(fto["avg_turnover"].mean())
        median_turnover = float(fto["avg_turnover"].median())
        p90_turnover = float(np.percentile(fto["avg_turnover"].values, 90))
        n_months = len(fto)

        # Get avg holding counts
        sl = summary_lookup.get(fid, {})
        avg_long_count = int(sl.get("avg_long_count", 36))
        avg_short_count = int(sl.get("avg_short_count", 36))
        avg_total_names = max(avg_long_count + avg_short_count, 1)

        # Per-notional capacity estimates using selected-basket volume
        notional_details: dict[str, dict] = {}
        for notional in notionals:
            hourly_turnover_vol = avg_turnover * notional
            per_name_turnover = hourly_turnover_vol / avg_total_names

            median_participation = per_name_turnover / ref_vol_median if ref_vol_median > 0 else float("inf")
            p10_participation = per_name_turnover / ref_vol_p10 if ref_vol_p10 > 0 else float("inf")

            # Capacity: AUM at which median participation = 5%
            target_participation = 0.05
            if avg_turnover > 0:
                capacity_usd = target_participation * avg_total_names * ref_vol_median / avg_turnover
            else:
                capacity_usd = float("inf")
            if avg_turnover > 0:
                stress_capacity_usd = target_participation * avg_total_names * ref_vol_p10 / avg_turnover
            else:
                stress_capacity_usd = float("inf")

            nkey = str(notional)
            notional_details[nkey] = {
                "notional_usd": notional,
                "hourly_turnover_vol": round(hourly_turnover_vol, 2),
                "per_name_hourly_turnover": round(per_name_turnover, 2),
                "median_participation_rate": round(median_participation, 6),
                "p10_participation_rate": round(p10_participation, 6),
                "capacity_estimate_usd": round(capacity_usd, 2),
                "stress_capacity_usd": round(stress_capacity_usd, 2),
            }

        # Use $10M notional participation for classification
        ref_notion_key = str(notionals[-1])
        ref_participation = notional_details[ref_notion_key]["median_participation_rate"]
        capacity_est = notional_details[ref_notion_key]["capacity_estimate_usd"]

        # Classify
        cap_cls = _classify_capacity(ref_participation)
        liq_cls = _classify_liquidity(ref_vol_median, ref_vol_p10, sel_top_share_median if liquidity_proxy_method == "selected_basket_proxy" else concentration_ratio)
        combined_cls = _classify_combined(cap_cls, liq_cls)

        # Cross-check fields
        gross_sharpe = _safe_float(sl.get("gross_sharpe"))
        cost_cls = sl.get("cost_sensitivity_class")
        paper_viability = sl.get("paper_viability_class")

        rl = regime_lookup.get(fid, {})
        regime_cls = rl.get("regime_dependency_class")

        sm = shape_map.get(fid, {})
        quantile_shape_cls = sm.get("quantile_shape_class")
        stability_cls = sm.get("stability_class")
        stability_score = _safe_float(sm.get("stability_score"))

        dm = decile_map.get(fid, {})
        decile_shape_cls = dm.get("decile_shape_class")

        ql = quality_lookup.get(fid, {})
        final_quality_cls = ql.get("final_quality_class")
        quality_score = _safe_float(ql.get("final_quality_score"))
        novelty_assessment = ql.get("novelty_assessment")

        # Assign flags
        flags = _assign_flags(cap_cls, liq_cls, combined_cls, gross_sharpe, cost_cls, stability_cls)
        flags_str = "|".join(flags) if flags else "NONE"

        # Factor quality cross flag
        factor_quality_cross_flag = None
        if has_good := (gross_sharpe is not None and gross_sharpe > 1.5):
            if cap_cls in ("CAPACITY_FRAGILE", "CAPACITY_BLOCKED_BY_TURNOVER"):
                factor_quality_cross_flag = "GOOD_ALPHA_BUT_CAPACITY_FRAGILE"
        is_stable = stability_cls in ("STABLE_POSITIVE", "STABLE_WEAK")
        if is_stable and liq_cls in ("LIQUIDITY_FRAGILE", "CONCENTRATED_LIQUIDITY"):
            factor_quality_cross_flag = "STABLE_BUT_TOO_ILLIQUID"
        is_cheap = cost_cls in ("LOW_COST_SENSITIVE",)
        is_weak = gross_sharpe is not None and gross_sharpe < 1.0
        if is_cheap and is_weak:
            factor_quality_cross_flag = "CHEAP_TO_TRADE_BUT_WEAK_SIGNAL"
        if factor_quality_cross_flag is None and combined_cls == "CAPACITY_LIQUIDITY_OK":
            factor_quality_cross_flag = "BALANCED_CANDIDATE"

        # Summary row
        row: dict[str, Any] = {
            "factor_id": fid,
            "family": sl.get("family"),
            "liquidity_proxy_method": liquidity_proxy_method,
            "n_months": n_months,
            "avg_long_count": avg_long_count,
            "avg_short_count": avg_short_count,
            "avg_turnover": round(avg_turnover, 6),
            "median_turnover": round(median_turnover, 6),
            "p90_turnover": round(p90_turnover, 6),
            # Selected-basket volume metrics
            "selected_symbol_count_median": round(selected_sym_count_median, 1) if not np.isnan(selected_sym_count_median) else None,
            "long_basket_volume_median": round(long_vol_median, 2),
            "short_basket_volume_median": round(short_vol_median, 2),
            "long_basket_volume_p10": round(long_vol_p10, 2),
            "short_basket_volume_p10": round(short_vol_p10, 2),
            "selected_basket_volume_median": round(sel_vol_median, 2),
            "selected_basket_volume_p10": round(sel_vol_p10, 2),
            "long_top_symbol_volume_share_median": round(long_top_share_median, 4) if not np.isnan(long_top_share_median) else None,
            "short_top_symbol_volume_share_median": round(short_top_share_median, 4) if not np.isnan(short_top_share_median) else None,
            "selected_top_symbol_volume_share_median": round(sel_top_share_median, 4) if not np.isnan(sel_top_share_median) else None,
            "low_volume_symbol_share": round(low_vol_share_median, 4) if not np.isnan(low_vol_share_median) else None,
            "volume_concentration_class": vol_conc_class,
            # Universe reference (for fallback comparison)
            "universe_hourly_volume_median": universe_hourly_median,
            "universe_hourly_volume_p10": universe_hourly_p10,
            "universe_volume_concentration_top5": concentration_ratio,
            # Capacity/liquidity classifications
            "capacity_risk_class": cap_cls,
            "liquidity_risk_class": liq_cls,
            "capacity_liquidity_class": combined_cls,
            "flags": flags_str,
            "factor_quality_cross_flag": factor_quality_cross_flag,
            # Cross-check
            "gross_sharpe": round(gross_sharpe, 4) if gross_sharpe is not None else None,
            "cost_sensitivity_class": cost_cls,
            "paper_viability_class": paper_viability,
            "regime_dependency_class": regime_cls,
            "quantile_shape_class": quantile_shape_cls,
            "stability_class": stability_cls,
            "stability_score": round(stability_score, 1) if stability_score is not None else None,
            "decile_shape_class": decile_shape_cls,
            "final_quality_class": final_quality_cls,
            "quality_score": round(quality_score, 1) if quality_score is not None else None,
            "novelty_assessment": novelty_assessment,
        }
        # Per-notional columns
        for nkey, nd in notional_details.items():
            row[f"participation_{nkey}"] = nd["median_participation_rate"]
            row[f"p10_participation_{nkey}"] = nd["p10_participation_rate"]
            row[f"capacity_usd_{nkey}"] = nd["capacity_estimate_usd"]
            row[f"stress_capacity_usd_{nkey}"] = nd["stress_capacity_usd"]

        # Selected-basket participation rate columns
        if liquidity_proxy_method == "selected_basket_proxy":
            for notional in notionals:
                nkey = str(notional)
                hourly_to = avg_turnover * notional
                per_name_to = hourly_to / avg_total_names
                # Median and p10 participation using selected basket volume
                med_part = per_name_to / sel_vol_median if sel_vol_median > 0 else float("inf")
                p10_part = per_name_to / sel_vol_p10 if sel_vol_p10 > 0 else float("inf")
                row[f"participation_{nkey}_selected_median"] = round(med_part, 6)
                row[f"participation_{nkey}_selected_p10"] = round(p10_part, 6)
            # Capacity at fixed participation rates
            for pct_label, pct in [("1pct", 0.01), ("5pct", 0.05), ("10pct", 0.10)]:
                if avg_turnover > 0 and sel_vol_median > 0:
                    cap = pct * avg_total_names * sel_vol_median / avg_turnover
                else:
                    cap = float("inf")
                row[f"capacity_at_{pct_label}_participation_selected"] = round(cap, 2)

        summary_rows.append(row)

        # Monthly rows
        for _, mrow in fto.iterrows():
            month_to = float(mrow["avg_turnover"])
            month_n = int(mrow.get("n_observations", 0))
            m_row: dict[str, Any] = {
                "factor_id": fid,
                "month": mrow["month"],
                "liquidity_proxy_method": liquidity_proxy_method,
                "avg_turnover": round(month_to, 6),
                "median_turnover": round(float(mrow.get("median_turnover", month_to)), 6),
                "max_turnover": round(float(mrow.get("max_turnover", month_to)), 6),
                "n_observations": month_n,
                "selected_basket_volume_median": round(sel_vol_median, 2),
                "selected_basket_volume_p10": round(sel_vol_p10, 2),
            }
            for notional in notionals:
                hourly_to = month_to * notional
                per_name_to = hourly_to / avg_total_names
                participation = per_name_to / ref_vol_median if ref_vol_median > 0 else float("inf")
                nkey = str(notional)
                m_row[f"participation_{nkey}"] = round(participation, 6)
                # Selected-basket participation
                part_sel = per_name_to / sel_vol_median if sel_vol_median > 0 else float("inf")
                m_row[f"participation_{nkey}_selected_median"] = round(part_sel, 6)

            monthly_rows.append(m_row)

        # Payload (compact for PM-30)
        payload_factors.append({
            "factor_id": fid,
            "liquidity_proxy_method": liquidity_proxy_method,
            "capacity_risk_class": cap_cls,
            "liquidity_risk_class": liq_cls,
            "capacity_liquidity_class": combined_cls,
            "volume_concentration_class": vol_conc_class,
            "factor_quality_cross_flag": factor_quality_cross_flag,
            "flags": flags,
            "avg_turnover": round(avg_turnover, 4),
            "p90_turnover": round(p90_turnover, 4),
            "avg_total_names": avg_total_names,
            "selected_symbol_count_median": round(selected_sym_count_median, 1) if not np.isnan(selected_sym_count_median) else None,
            "selected_basket_volume_median": round(sel_vol_median, 2),
            "selected_basket_volume_p10": round(sel_vol_p10, 2),
            "selected_top_symbol_volume_share_median": round(sel_top_share_median, 4) if not np.isnan(sel_top_share_median) else None,
            "low_volume_symbol_share": round(low_vol_share_median, 4) if not np.isnan(low_vol_share_median) else None,
            "participation_10m": ref_participation,
            "capacity_usd_10m": capacity_est,
            "gross_sharpe": round(gross_sharpe, 2) if gross_sharpe is not None else None,
            "cost_sensitivity_class": cost_cls,
            "stability_class": stability_cls,
            "regime_dependency_class": regime_cls,
        })

        processed += 1
        if (fi + 1) % 10 == 0:
            print(f"  [{fi+1}/{len(all_factors)}] {processed} processed, {_time.time()-t0:.1f}s")

    elapsed = _time.time() - t0
    print(f"[PM-29B] Processed {processed} factors in {elapsed:.1f}s ({errors} errors)")

    # -----------------------------------------------------------------------
    # 5. Build DataFrames
    # -----------------------------------------------------------------------
    summary_out = pd.DataFrame(summary_rows)
    monthly_out = pd.DataFrame(monthly_rows)

    # ── PM-36: Merge with existing outputs if in subset mode ──────────────
    if is_subset_mode and target_factor_ids:
        target_set = set(target_factor_ids)

        # Merge summary
        existing_summary_path = DIAG / "factor_capacity_liquidity_summary.csv"
        if existing_summary_path.exists():
            existing_summary = pd.read_csv(existing_summary_path)
            existing_summary = existing_summary[~existing_summary["factor_id"].isin(target_set)]
            summary_out = pd.concat([existing_summary, summary_out], ignore_index=True)
            print(f"[PM-29B] MERGED summary: {len(summary_out)} factors ({len(existing_summary)} existing + new)")

        # Merge monthly
        existing_monthly_path = DIAG / "factor_capacity_liquidity_monthly.csv"
        if existing_monthly_path.exists():
            existing_monthly = pd.read_csv(existing_monthly_path)
            existing_monthly = existing_monthly[~existing_monthly["factor_id"].isin(target_set)]
            monthly_out = pd.concat([existing_monthly, monthly_out], ignore_index=True)
            print(f"[PM-29B] MERGED monthly: {len(monthly_out)} rows ({len(existing_monthly)} existing + new)")

        # Rebuild summary_rows and payload_factors from merged data for JSON output
        summary_rows = summary_out.to_dict("records")
        # Rebuild payload_factors from merged summary_out
        payload_factors = []
        for _, srow in summary_out.iterrows():
            pf = {
                "factor_id": srow["factor_id"],
                "liquidity_proxy_method": srow.get("liquidity_proxy_method"),
                "capacity_risk_class": srow.get("capacity_risk_class"),
                "liquidity_risk_class": srow.get("liquidity_risk_class"),
                "capacity_liquidity_class": srow.get("capacity_liquidity_class"),
                "volume_concentration_class": srow.get("volume_concentration_class"),
                "factor_quality_cross_flag": srow.get("factor_quality_cross_flag"),
                "flags": srow.get("flags", "NONE").split("|") if srow.get("flags") and srow.get("flags") != "NONE" else [],
                "avg_turnover": round(float(srow.get("avg_turnover", 0)), 4),
                "p90_turnover": round(float(srow.get("p90_turnover", 0)), 4),
                "avg_total_names": int(srow.get("avg_total_names", 36)),
                "selected_symbol_count_median": round(float(srow.get("selected_symbol_count_median", 0)), 1) if pd.notna(srow.get("selected_symbol_count_median")) else None,
                "selected_basket_volume_median": round(float(srow.get("selected_basket_volume_median", 0)), 2),
                "selected_basket_volume_p10": round(float(srow.get("selected_basket_volume_p10", 0)), 2),
                "selected_top_symbol_volume_share_median": round(float(srow.get("selected_top_symbol_volume_share_median", 0)), 4) if pd.notna(srow.get("selected_top_symbol_volume_share_median")) else None,
                "low_volume_symbol_share": round(float(srow.get("low_volume_symbol_share", 0)), 4) if pd.notna(srow.get("low_volume_symbol_share")) else None,
                "participation_10m": srow.get("participation_10000000"),
                "capacity_usd_10m": srow.get("capacity_usd_10000000"),
                "gross_sharpe": round(float(srow.get("gross_sharpe", 0)), 2) if pd.notna(srow.get("gross_sharpe")) else None,
                "cost_sensitivity_class": srow.get("cost_sensitivity_class"),
                "stability_class": srow.get("stability_class"),
                "regime_dependency_class": srow.get("regime_dependency_class"),
            }
            payload_factors.append(pf)

    if summary_out.empty:
        print("[PM-29B] ERROR: No factors processed. Check factor values and volume overlap.")
        return 1

    print(f"[PM-29B] Summary: {len(summary_out)} factors")
    print(f"[PM-29B] Monthly: {len(monthly_out)} rows")

    # -----------------------------------------------------------------------
    # 6. Write outputs
    # -----------------------------------------------------------------------
    DIAG.mkdir(parents=True, exist_ok=True)

    # CSV summary
    summary_csv_path = DIAG / "factor_capacity_liquidity_summary.csv"
    summary_out.to_csv(summary_csv_path, index=False)
    print(f"[PM-29B] Wrote {summary_csv_path}")

    # JSON summary
    summary_json_path = DIAG / "factor_capacity_liquidity_summary.json"
    summary_json = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "n_factors": len(summary_out),
        "notionals": notionals,
        "sampling_method": f"every_{sample_hours}h_deterministic",
        "volume_proxy_method": "selected_basket_proxy",
        "volume_proxy_description": (
            "For each factor, at each sampled timestamp, factor values are ranked cross-sectionally. "
            f"Long basket = top {TOP_FRAC:.0%}, short basket = bottom {BOTTOM_FRAC:.0%} (matching paper convention). "
            "Hourly quote_volume is joined for the selected symbols. "
            "Selected-basket median/p10 volume is used as the liquidity denominator for capacity estimation. "
            f"Sampling: every {sample_hours}h for performance. "
            f"Universe-wide median (${universe_hourly_median:,.0f}) used as fallback when basket data unavailable."
        ),
        "basket_selection": {
            "top_frac": TOP_FRAC,
            "bottom_frac": BOTTOM_FRAC,
            "min_cross_section": MIN_NAMES,
        },
        "universe_hourly_volume_median": universe_hourly_median,
        "universe_hourly_volume_p10": universe_hourly_p10,
        "universe_hourly_volume_mean": universe_hourly_mean,
        "universe_volume_concentration_top5": concentration_ratio,
        "capacity_risk_distribution": summary_out["capacity_risk_class"].value_counts().to_dict(),
        "liquidity_risk_distribution": summary_out["liquidity_risk_class"].value_counts().to_dict(),
        "combined_distribution": summary_out["capacity_liquidity_class"].value_counts().to_dict(),
        "volume_concentration_distribution": summary_out["volume_concentration_class"].value_counts().to_dict() if "volume_concentration_class" in summary_out.columns else {},
        "liquidity_proxy_distribution": summary_out["liquidity_proxy_method"].value_counts().to_dict(),
        "factors": summary_rows,
    }
    summary_json_path.write_text(json.dumps(summary_json, indent=2, default=str))
    print(f"[PM-29B] Wrote {summary_json_path}")

    # Monthly CSV
    monthly_csv_path = DIAG / "factor_capacity_liquidity_monthly.csv"
    monthly_out.to_csv(monthly_csv_path, index=False)
    print(f"[PM-29B] Wrote {monthly_csv_path}")

    # Payload JSON (compact)
    payload_path = DIAG / "factor_capacity_liquidity_payload.json"
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "n_factors": len(payload_factors),
        "notionals": notionals,
        "sampling_method": f"every_{sample_hours}h_deterministic",
        "volume_proxy_method": "selected_basket_proxy",
        "universe_hourly_volume_median": universe_hourly_median,
        "universe_hourly_volume_p10": universe_hourly_p10,
        "capacity_risk_distribution": summary_out["capacity_risk_class"].value_counts().to_dict(),
        "liquidity_risk_distribution": summary_out["liquidity_risk_class"].value_counts().to_dict(),
        "combined_distribution": summary_out["capacity_liquidity_class"].value_counts().to_dict(),
        "factors": payload_factors,
    }
    payload_path.write_text(json.dumps(payload, indent=2, default=str))
    print(f"[PM-29B] Wrote {payload_path}")

    # Manifest
    manifest_path = DIAG / "factor_capacity_liquidity_manifest.json"
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "script": "scripts/build_factor_capacity_liquidity_diagnostics.py",
        "version": "PM-29B",
        "inputs": {
            "turnover_csv": str(turnover_path.relative_to(ROOT)),
            "volume_parquet": str(VOLUME_PARQUET.relative_to(ROOT)),
            "factor_values_base": str(DATA_BASE.relative_to(ROOT)),
            "summary_csv": str((DIAG / "single_factor_paper_summary.csv").relative_to(ROOT)),
            "quality_scorecard_csv": str((DIAG / "factor_quality_scorecard.csv").relative_to(ROOT)),
            "regime_exposure_csv": str((DIAG / "factor_regime_exposure_summary.csv").relative_to(ROOT)),
            "shape_stability_json": str((DIAG / "factor_shape_stability_payload.json").relative_to(ROOT)),
            "decile_shape_json": str((DIAG / "factor_decile_shape_payload.json").relative_to(ROOT)),
        },
        "outputs": {
            "summary_csv": str(summary_csv_path.relative_to(ROOT)),
            "summary_json": str(summary_json_path.relative_to(ROOT)),
            "monthly_csv": str(monthly_csv_path.relative_to(ROOT)),
            "payload_json": str(payload_path.relative_to(ROOT)),
            "manifest_json": str(manifest_path.relative_to(ROOT)),
        },
        "parameters": {
            "notionals": notionals,
            "volume_proxy_method": "selected_basket_proxy",
            "sampling_method": f"every_{sample_hours}h_deterministic",
            "top_frac": TOP_FRAC,
            "bottom_frac": BOTTOM_FRAC,
            "min_cross_section": MIN_NAMES,
            "participation_threshold": 0.05,
        },
        "coverage": {
            "n_factors": len(summary_out),
            "n_monthly_rows": len(monthly_out),
            "n_volume_symbols": int(vol_df["symbol"].nunique()),
            "n_sampled_timestamps": len(sampled_vol_ts),
            "n_total_timestamps": int(len(all_vol_ts)),
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, default=str))
    print(f"[PM-29B] Wrote {manifest_path}")

    # -----------------------------------------------------------------------
    # 7. Print summary
    # -----------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("LIQUIDITY PROXY METHODS")
    print(summary_out["liquidity_proxy_method"].value_counts().to_string())
    print("\nCAPACITY RISK DISTRIBUTION")
    print(summary_out["capacity_risk_class"].value_counts().to_string())
    print("\nLIQUIDITY RISK DISTRIBUTION")
    print(summary_out["liquidity_risk_class"].value_counts().to_string())
    print("\nVOLUME CONCENTRATION DISTRIBUTION")
    if "volume_concentration_class" in summary_out.columns:
        print(summary_out["volume_concentration_class"].value_counts().to_string())
    print("\nCOMBINED DISTRIBUTION")
    print(summary_out["capacity_liquidity_class"].value_counts().to_string())

    print("\nFLAGS")
    flag_counts: dict[str, int] = {}
    for _, r in summary_out.iterrows():
        for flag in r["flags"].split("|"):
            flag_counts[flag] = flag_counts.get(flag, 0) + 1
    for k, v in sorted(flag_counts.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")

    # Representative examples
    print("\n" + "=" * 60)
    print("REPRESENTATIVE EXAMPLES")
    for cls_name in ["CAPACITY_LIQUIDITY_OK", "WATCH_TURNOVER", "WATCH_LIQUIDITY", "WATCH_BOTH"]:
        subset = summary_out[summary_out["capacity_liquidity_class"] == cls_name]
        if not subset.empty:
            ex = subset.iloc[0]
            print(f"\n  {cls_name}: {ex['factor_id']}")
            print(f"    turnover={ex['avg_turnover']:.4f}, sharpe={ex.get('gross_sharpe')}, "
                  f"cost={ex.get('cost_sensitivity_class')}, stability={ex.get('stability_class')}")
            print(f"    sel_vol_median=${ex.get('selected_basket_volume_median', 0):,.0f}, "
                  f"proxy={ex.get('liquidity_proxy_method')}")

    print("\n" + "=" * 60)
    print(f"[PM-29B] Done. {len(summary_out)} factors classified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
