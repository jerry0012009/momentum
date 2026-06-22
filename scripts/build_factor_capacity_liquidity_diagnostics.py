#!/usr/bin/env python3
"""PM-29: Capacity / Liquidity Proxy Diagnostics.

Computes per-factor capacity and liquidity risk classifications by combining:
  - Turnover data (from single_factor_paper_turnover.csv)
  - Per-symbol hourly volume proxy (from bars_1h.parquet)
  - Cross-checks with existing factor quality metrics

Methodology:
  - Each factor holds ~36 long + ~36 short names
  - Hourly turnover_volume = avg_turnover * AUM
  - Per-name hourly turnover = turnover_volume / (avg_long_count + avg_short_count)
  - Participation rate = per_name_turnover / per_name_median_hourly_volume
  - Capacity = max AUM at which median participation hits 5% threshold
  - Volume uses per-symbol median hourly quote_volume (universe-wide or top-50)
  - Liquidity risk considers p10 per-symbol volume (worst-case name in portfolio)

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

# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------
# Capacity risk: based on median participation rate at $10M AUM
CAP_THRESHOLDS = {
    "CAPACITY_BLOCKED_BY_TURNOVER": 0.20,   # >20% participation at 10M
    "CAPACITY_FRAGILE": 0.10,                # >10%
    "MODERATE_CAPACITY_RISK": 0.02,          # >2%
    # else CAPACITY_FRIENDLY
}

# Liquidity risk: based on p10 hourly volume of the names in the portfolio
LIQ_THRESHOLDS = {
    "LIQUIDITY_FRAGILE": 500_000,            # p10 hourly vol < $500K
    "LOW_VOLUME_EXPOSURE": 2_000_000,        # median hourly vol < $2M
    # CONCENTRATED_LIQUIDITY if top-5 share > 80%
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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="PM-29 capacity/liquidity proxy diagnostics")
    parser.add_argument("--notionals", default="100000,1000000,10000000",
                        help="Comma-separated notional sizes in USD")
    args = parser.parse_args()
    notionals = sorted([int(x) for x in args.notionals.split(",")])

    print(f"[PM-29] Notionals: {notionals}")

    # -----------------------------------------------------------------------
    # 1. Load turnover data
    # -----------------------------------------------------------------------
    turnover_path = DIAG / "single_factor_paper_turnover.csv"
    to_df = pd.read_csv(turnover_path)
    factors_with_turnover = to_df["factor_id"].nunique()
    print(f"[PM-29] Loaded turnover data: {len(to_df)} rows, {factors_with_turnover} factors")

    # -----------------------------------------------------------------------
    # 2. Load volume data & compute per-symbol hourly volume distribution
    # -----------------------------------------------------------------------
    vol_df = pd.read_parquet(VOLUME_PARQUET)
    print(f"[PM-29] Loaded volume data: {len(vol_df)} rows, {vol_df['symbol'].nunique()} symbols")

    # Per-symbol total volume (used to select top-50 universe)
    per_sym_total = vol_df.groupby("symbol")["quote_volume"].sum().sort_values(ascending=False)
    top50_symbols = set(per_sym_total.head(50).index)

    # Filter to top-50 symbols (matching factor universe)
    vol_top50 = vol_df[vol_df["symbol"].isin(top50_symbols)]
    print(f"[PM-29] Filtered to top-50 symbols: {vol_top50.shape[0]:,} rows")

    # Per-symbol median hourly quote_volume (top-50 only)
    per_sym_hourly = vol_top50.groupby("symbol")["quote_volume"].median()
    per_sym_hourly_p10 = vol_top50.groupby("symbol")["quote_volume"].quantile(0.10)

    # Universe-level reference stats (top-50 symbols)
    universe_hourly_median = float(per_sym_hourly.median())       # median symbol's median hourly vol
    universe_hourly_p10 = float(np.percentile(per_sym_hourly.values, 10))  # p10 across symbols
    universe_hourly_mean = float(per_sym_hourly.mean())

    # Volume concentration: what share of total hourly volume is in top-5
    sorted_vols = per_sym_hourly.sort_values(ascending=False)
    total_hourly = sorted_vols.sum()
    concentration_ratio = float(sorted_vols.head(5).sum() / total_hourly) if total_hourly > 0 else 0

    print(f"[PM-29] Top-50 per-symbol hourly vol: median=${universe_hourly_median:,.0f}, "
          f"p10=${universe_hourly_p10:,.0f}")
    print(f"[PM-29] Top-5 volume concentration (within top-50): {concentration_ratio:.2%}")

    # Monthly volume (for monthly detail output)
    vol_df_copy = vol_df.copy()
    vol_df_copy["month"] = vol_df_copy["timestamp"].dt.to_period("M").astype(str)
    vol_monthly_sym = vol_df_copy.groupby(["symbol", "month"])["quote_volume"].agg(
        ["median", "sum"]
    ).reset_index()
    vol_monthly_sym.columns = ["symbol", "month", "median_hourly_vol", "total_vol"]

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

    all_factors = sorted(set(to_df["factor_id"].unique()))
    print(f"[PM-29] Processing {len(all_factors)} factors")

    # -----------------------------------------------------------------------
    # 4. Compute per-factor capacity/liquidity diagnostics
    # -----------------------------------------------------------------------
    summary_rows: list[dict] = []
    monthly_rows: list[dict] = []
    payload_factors: list[dict] = []

    for fid in all_factors:
        fto = to_df[to_df["factor_id"] == fid].copy()
        if fto.empty:
            continue

        # Turnover stats (across all months)
        avg_turnover = float(fto["avg_turnover"].mean())
        median_turnover = float(fto["avg_turnover"].median())
        p90_turnover = float(np.percentile(fto["avg_turnover"].values, 90))
        n_months = len(fto)

        # Get avg holding counts for this factor
        sl = summary_lookup.get(fid, {})
        avg_long_count = int(sl.get("avg_long_count", 36))
        avg_short_count = int(sl.get("avg_short_count", 36))
        avg_total_names = max(avg_long_count + avg_short_count, 1)

        # -------------------------------------------------------------------
        # Volume proxy: universe-level per-symbol hourly volumes
        # Since we don't know exact holdings, use universe distribution as proxy.
        # reference_volume_median = median per-symbol median hourly quote_volume
        # reference_volume_p10 = p10 across all symbols
        # These represent what a "typical" and "worst-case" name looks like.
        # -------------------------------------------------------------------
        ref_vol_median = universe_hourly_median    # per-name median hourly vol
        ref_vol_p10 = universe_hourly_p10          # per-name p10 hourly vol

        # Per-notional capacity estimates
        notional_details: dict[str, dict] = {}
        for notional in notionals:
            # Hourly turnover volume = avg_turnover * AUM
            hourly_turnover_vol = avg_turnover * notional

            # Per-name hourly turnover = total / n_names
            per_name_turnover = hourly_turnover_vol / avg_total_names

            # Participation rates
            median_participation = per_name_turnover / ref_vol_median if ref_vol_median > 0 else float("inf")
            p10_participation = per_name_turnover / ref_vol_p10 if ref_vol_p10 > 0 else float("inf")

            # Capacity estimate: AUM at which median participation = 5%
            # 0.05 = (avg_turnover * AUM / n_names) / ref_vol_median
            # AUM = 0.05 * n_names * ref_vol_median / avg_turnover
            target_participation = 0.05
            if avg_turnover > 0:
                capacity_usd = target_participation * avg_total_names * ref_vol_median / avg_turnover
            else:
                capacity_usd = float("inf")

            # Stress capacity: using p10 volume
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
        ref_notion_key = str(notionals[-1])  # largest notional
        ref_participation = notional_details[ref_notion_key]["median_participation_rate"]
        capacity_est = notional_details[ref_notion_key]["capacity_estimate_usd"]

        # Classify
        cap_cls = _classify_capacity(ref_participation)
        liq_cls = _classify_liquidity(ref_vol_median, ref_vol_p10, concentration_ratio)
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

        # Summary row
        row: dict[str, Any] = {
            "factor_id": fid,
            "family": sl.get("family"),
            "n_months": n_months,
            "avg_long_count": avg_long_count,
            "avg_short_count": avg_short_count,
            "avg_turnover": round(avg_turnover, 6),
            "median_turnover": round(median_turnover, 6),
            "p90_turnover": round(p90_turnover, 6),
            "ref_volume_median_hourly": round(ref_vol_median, 2),
            "ref_volume_p10_hourly": round(ref_vol_p10, 2),
            "volume_concentration_top5": round(concentration_ratio, 4),
            "capacity_risk_class": cap_cls,
            "liquidity_risk_class": liq_cls,
            "capacity_liquidity_class": combined_cls,
            "flags": flags_str,
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

        summary_rows.append(row)

        # Monthly rows
        for _, mrow in fto.iterrows():
            month_to = float(mrow["avg_turnover"])
            month_n = int(mrow.get("n_observations", 0))
            m_row: dict[str, Any] = {
                "factor_id": fid,
                "month": mrow["month"],
                "avg_turnover": round(month_to, 6),
                "median_turnover": round(float(mrow.get("median_turnover", month_to)), 6),
                "max_turnover": round(float(mrow.get("max_turnover", month_to)), 6),
                "n_observations": month_n,
            }
            # Per-notional monthly participation
            for notional in notionals:
                hourly_to = month_to * notional
                per_name_to = hourly_to / avg_total_names
                participation = per_name_to / ref_vol_median if ref_vol_median > 0 else float("inf")
                nkey = str(notional)
                m_row[f"participation_{nkey}"] = round(participation, 6)

            monthly_rows.append(m_row)

        # Payload (compact for PM-30)
        payload_factors.append({
            "factor_id": fid,
            "capacity_risk_class": cap_cls,
            "liquidity_risk_class": liq_cls,
            "capacity_liquidity_class": combined_cls,
            "flags": flags,
            "avg_turnover": round(avg_turnover, 4),
            "p90_turnover": round(p90_turnover, 4),
            "avg_total_names": avg_total_names,
            "participation_10m": ref_participation,
            "capacity_usd_10m": capacity_est,
            "gross_sharpe": round(gross_sharpe, 2) if gross_sharpe is not None else None,
            "cost_sensitivity_class": cost_cls,
            "stability_class": stability_cls,
            "regime_dependency_class": regime_cls,
        })

    # -----------------------------------------------------------------------
    # 5. Build DataFrames
    # -----------------------------------------------------------------------
    summary_out = pd.DataFrame(summary_rows)
    monthly_out = pd.DataFrame(monthly_rows)

    print(f"[PM-29] Summary: {len(summary_out)} factors")
    print(f"[PM-29] Monthly: {len(monthly_out)} rows")

    # -----------------------------------------------------------------------
    # 6. Write outputs
    # -----------------------------------------------------------------------
    DIAG.mkdir(parents=True, exist_ok=True)

    # CSV summary
    summary_csv_path = DIAG / "factor_capacity_liquidity_summary.csv"
    summary_out.to_csv(summary_csv_path, index=False)
    print(f"[PM-29] Wrote {summary_csv_path}")

    # JSON summary
    summary_json_path = DIAG / "factor_capacity_liquidity_summary.json"
    summary_json = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "n_factors": len(summary_out),
        "notionals": notionals,
        "volume_proxy_method": "per_symbol_median_hourly_quote_volume",
        "volume_proxy_description": (
            "Per-symbol median hourly quote_volume across full history. "
            "Universe median used as proxy for typical holding name. "
            "Participation = per_name_hourly_turnover / per_symbol_hourly_volume. "
            "Capacity = AUM at 5% median participation target."
        ),
        "universe_hourly_volume_median": universe_hourly_median,
        "universe_hourly_volume_p10": universe_hourly_p10,
        "universe_hourly_volume_mean": universe_hourly_mean,
        "volume_concentration_top5": concentration_ratio,
        "capacity_risk_distribution": summary_out["capacity_risk_class"].value_counts().to_dict(),
        "liquidity_risk_distribution": summary_out["liquidity_risk_class"].value_counts().to_dict(),
        "combined_distribution": summary_out["capacity_liquidity_class"].value_counts().to_dict(),
        "factors": summary_rows,
    }
    summary_json_path.write_text(json.dumps(summary_json, indent=2, default=str))
    print(f"[PM-29] Wrote {summary_json_path}")

    # Monthly CSV
    monthly_csv_path = DIAG / "factor_capacity_liquidity_monthly.csv"
    monthly_out.to_csv(monthly_csv_path, index=False)
    print(f"[PM-29] Wrote {monthly_csv_path}")

    # Payload JSON (compact)
    payload_path = DIAG / "factor_capacity_liquidity_payload.json"
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "n_factors": len(payload_factors),
        "notionals": notionals,
        "volume_proxy_method": "per_symbol_median_hourly_quote_volume",
        "universe_hourly_volume_median": universe_hourly_median,
        "universe_hourly_volume_p10": universe_hourly_p10,
        "capacity_risk_distribution": summary_out["capacity_risk_class"].value_counts().to_dict(),
        "liquidity_risk_distribution": summary_out["liquidity_risk_class"].value_counts().to_dict(),
        "combined_distribution": summary_out["capacity_liquidity_class"].value_counts().to_dict(),
        "factors": payload_factors,
    }
    payload_path.write_text(json.dumps(payload, indent=2, default=str))
    print(f"[PM-29] Wrote {payload_path}")

    # Manifest
    manifest_path = DIAG / "factor_capacity_liquidity_manifest.json"
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "script": "scripts/build_factor_capacity_liquidity_diagnostics.py",
        "inputs": {
            "turnover_csv": str(turnover_path.relative_to(ROOT)),
            "volume_parquet": str(VOLUME_PARQUET.relative_to(ROOT)),
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
            "volume_proxy_method": "per_symbol_median_hourly_quote_volume",
            "participation_threshold": 0.05,
            "avg_names_assumed": "from summary avg_long_count + avg_short_count",
        },
        "coverage": {
            "n_factors": len(summary_out),
            "n_monthly_rows": len(monthly_out),
            "n_volume_symbols": int(vol_df["symbol"].nunique()),
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, default=str))
    print(f"[PM-29] Wrote {manifest_path}")

    # -----------------------------------------------------------------------
    # 7. Print summary
    # -----------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("CAPACITY RISK DISTRIBUTION")
    print(summary_out["capacity_risk_class"].value_counts().to_string())
    print("\nLIQUIDITY RISK DISTRIBUTION")
    print(summary_out["liquidity_risk_class"].value_counts().to_string())
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

    print("\n" + "=" * 60)
    print(f"[PM-29] Done. {len(summary_out)} factors classified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
