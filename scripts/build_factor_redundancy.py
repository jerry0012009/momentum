#!/usr/bin/env python3
"""Factor Redundancy Diagnostics — current library version.

Computes pairwise Spearman/Pearson correlations between factor_values.
Works with the current factor library (not Phase 7 candidate CSVs).

Usage:
    python scripts/build_factor_redundancy.py --factor-ids rev_1h mom_72h
    python scripts/build_factor_redundancy.py  # all computed factors
    python scripts/build_factor_redundancy.py --factor-ids rev_1h mom_72h --output /tmp/redundancy.csv

Phase 13A-P3. Not production. Not live trading.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
FEATURES_DIR = ROOT / "data" / "features" / "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1"
DEFAULT_OUTPUT = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_level_evaluation" / "factor_redundancy.csv"

sys.path.insert(0, str(SCRIPTS))

# Redundancy thresholds
NEAR_DUPLICATE = 0.95
HIGH_REDUNDANCY = 0.85
MODERATE_REDUNDANCY = 0.70

MIN_PAIRWISE_OBS = 30


def redundancy_level(abs_corr: float) -> str:
    if abs_corr >= NEAR_DUPLICATE:
        return "NEAR_DUPLICATE"
    elif abs_corr >= HIGH_REDUNDANCY:
        return "HIGH_REDUNDANCY"
    elif abs_corr >= MODERATE_REDUNDANCY:
        return "MODERATE_REDUNDANCY"
    else:
        return "LOW_REDUNDANCY"


def recommendation_for_pair(level: str, same_family: bool) -> str:
    if level == "NEAR_DUPLICATE":
        return "Drop one; keep the more interpretable or stable factor."
    elif level == "HIGH_REDUNDANCY":
        if same_family:
            return "Same-family high redundancy. Consider dropping the weaker factor."
        else:
            return "Cross-family high redundancy. Investigate shared signal source."
    elif level == "MODERATE_REDUNDANCY":
        return "Monitor. May provide diversification if combined carefully."
    else:
        return "Low redundancy. Independent signal sources."


def load_registry_metadata() -> dict[str, dict]:
    """Load factor_id -> {family, expected_direction} from registry."""
    for mod in ["factor_formula_registry"]:
        if mod in sys.modules:
            del sys.modules[mod]
    from factor_formula_registry import REGISTRY
    return {
        fs.factor_id: {
            "family": fs.family,
            "expected_direction": fs.expected_direction,
        }
        for fs in REGISTRY
    }


def compute_redundancy(
    factor_ids: list[str],
    output_path: Path,
    sample_step: int = 1,
) -> pd.DataFrame:
    """Compute pairwise redundancy for given factor IDs."""
    meta = load_registry_metadata()

    # Load factor_values into a wide table
    parts = {}
    for fid in factor_ids:
        fv_path = FEATURES_DIR / fid / "factor_values.parquet"
        if not fv_path.exists():
            print(f"  WARNING: missing {fv_path}, skipping {fid}")
            continue
        fv = pd.read_parquet(fv_path, columns=["timestamp", "symbol", "factor_value"])
        fv = fv.rename(columns={"factor_value": fid})
        parts[fid] = fv

    if len(parts) < 2:
        print(f"  ERROR: need at least 2 factors with factor_values, got {len(parts)}")
        return pd.DataFrame()

    print(f"  Merging {len(parts)} factor_values into wide table...")
    wide = None
    for fid, fv in parts.items():
        if wide is None:
            wide = fv
        else:
            wide = wide.merge(fv, on=["timestamp", "symbol"], how="outer")

    if sample_step > 1:
        ts_all = wide["timestamp"].unique()
        ts_sampled = ts_all[::sample_step]
        wide = wide[wide["timestamp"].isin(ts_sampled)]
        print(f"  Sampled: {len(ts_sampled)}/{len(ts_all)} timestamps")

    available_ids = list(parts.keys())
    print(f"  Wide table: {len(wide)} rows, {len(available_ids)} factor columns")

    # Compute pairwise
    pairs = []
    n_factors = len(available_ids)
    for i in range(n_factors):
        for j in range(i + 1, n_factors):
            fi, fj = available_ids[i], available_ids[j]
            vi = wide[fi].values
            vj = wide[fj].values
            valid = ~(np.isnan(vi) | np.isnan(vj))
            n = int(valid.sum())
            if n < MIN_PAIRWISE_OBS:
                pairs.append({
                    "factor_i": fi, "factor_j": fj,
                    "family_i": meta.get(fi, {}).get("family", ""),
                    "family_j": meta.get(fj, {}).get("family", ""),
                    "same_family": meta.get(fi, {}).get("family") == meta.get(fj, {}).get("family"),
                    "spearman_corr": None, "abs_spearman_corr": None,
                    "pearson_corr": None, "n_pairwise_obs": n,
                    "redundancy_level": "INSUFFICIENT_DATA",
                    "recommendation": "Insufficient pairwise observations.",
                })
                continue
            a, b = vi[valid], vj[valid]
            pearson = float(np.corrcoef(a, b)[0, 1])
            spearman = float(stats.spearmanr(a, b)[0])
            abs_spearman = abs(spearman)
            same_fam = meta.get(fi, {}).get("family") == meta.get(fj, {}).get("family")
            level = redundancy_level(abs_spearman)
            pairs.append({
                "factor_i": fi, "factor_j": fj,
                "family_i": meta.get(fi, {}).get("family", ""),
                "family_j": meta.get(fj, {}).get("family", ""),
                "same_family": same_fam,
                "spearman_corr": round(spearman, 6),
                "abs_spearman_corr": round(abs_spearman, 6),
                "pearson_corr": round(pearson, 6),
                "n_pairwise_obs": n,
                "redundancy_level": level,
                "recommendation": recommendation_for_pair(level, same_fam),
            })

    df = pd.DataFrame(pairs)
    df = df.sort_values("abs_spearman_corr", ascending=False, na_position="last")

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"  Output: {output_path} ({len(df)} pairs)")

    # Summary
    for level in ["NEAR_DUPLICATE", "HIGH_REDUNDANCY", "MODERATE_REDUNDANCY", "LOW_REDUNDANCY", "INSUFFICIENT_DATA"]:
        cnt = (df["redundancy_level"] == level).sum()
        if cnt > 0:
            print(f"    {level}: {cnt}")

    return df


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--factor-ids", nargs="*", default=None,
                        help="Factor IDs to compare (default: all computed)")
    parser.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT),
                        help="Output CSV path")
    parser.add_argument("--sample-step", type=int, default=1,
                        help="Sample every Nth timestamp (1=no sampling)")
    args = parser.parse_args()

    # Determine factor IDs
    if args.factor_ids:
        factor_ids = args.factor_ids
    else:
        for mod in ["factor_formula_registry"]:
            if mod in sys.modules:
                del sys.modules[mod]
        from factor_formula_registry import REGISTRY
        factor_ids = [fs.factor_id for fs in REGISTRY
                      if (FEATURES_DIR / fs.factor_id / "factor_values.parquet").exists()]

    print(f"Factor Redundancy Diagnostics")
    print(f"  Factors: {len(factor_ids)}")
    print(f"  Output: {args.output}")
    print()

    df = compute_redundancy(factor_ids, Path(args.output), args.sample_step)
    return df


if __name__ == "__main__":
    main()
