#!/usr/bin/env python3
"""Factor Redundancy Diagnostics — current library version.

Computes pairwise Spearman/Pearson correlations between factor_values.
Supports two modes:
  - Library mode (--factor-ids): compare given factors against each other
  - Intake mode (--intake-factor-ids [--baseline-factor-ids]):
    compare intake factors against baseline (existing library) + each other

Usage:
    # Library mode: compare specific factors
    python scripts/build_factor_redundancy.py --factor-ids rev_1h mom_72h

    # Intake mode: compare intake factors against all existing library
    python scripts/build_factor_redundancy.py --intake-factor-ids rev_1h mom_72h

    # Intake mode: compare intake factors against specific baseline
    python scripts/build_factor_redundancy.py --intake-factor-ids rev_1h --baseline-factor-ids mom_20h vol_20h

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


def recommendation_for_pair(level: str, same_family: bool, pair_type: str = "library") -> str:
    if level == "NEAR_DUPLICATE":
        if pair_type == "intake_vs_baseline":
            return "NEAR_DUPLICATE with existing library factor. Likely redundant. Drop or justify unique contribution."
        return "Drop one; keep the more interpretable or stable factor."
    elif level == "HIGH_REDUNDANCY":
        if pair_type == "intake_vs_baseline":
            return "REDUNDANT_WITH_EXISTING. High correlation with existing library factor."
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


def load_factor_wide(factor_ids: list[str], sample_step: int = 1) -> tuple[pd.DataFrame, list[str]]:
    """Load factor_values into a wide table. Returns (wide_df, available_ids)."""
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
        return pd.DataFrame(), []

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
    return wide, available_ids


def compute_pair(
    wide: pd.DataFrame,
    fi: str,
    fj: str,
    meta: dict[str, dict],
    pair_type: str = "library",
) -> dict:
    """Compute redundancy metrics for a single pair."""
    vi = wide[fi].values
    vj = wide[fj].values
    valid = ~(np.isnan(vi) | np.isnan(vj))
    n = int(valid.sum())
    if n < MIN_PAIRWISE_OBS:
        return {
            "factor_i": fi, "factor_j": fj,
            "family_i": meta.get(fi, {}).get("family", ""),
            "family_j": meta.get(fj, {}).get("family", ""),
            "same_family": meta.get(fi, {}).get("family") == meta.get(fj, {}).get("family"),
            "spearman_corr": None, "abs_spearman_corr": None,
            "pearson_corr": None, "n_pairwise_obs": n,
            "redundancy_level": "INSUFFICIENT_DATA",
            "recommendation": "Insufficient pairwise observations.",
            "pair_type": pair_type,
        }
    a, b = vi[valid], vj[valid]
    pearson = float(np.corrcoef(a, b)[0, 1])
    spearman = float(stats.spearmanr(a, b)[0])
    abs_spearman = abs(spearman)
    same_fam = meta.get(fi, {}).get("family") == meta.get(fj, {}).get("family")
    level = redundancy_level(abs_spearman)
    return {
        "factor_i": fi, "factor_j": fj,
        "family_i": meta.get(fi, {}).get("family", ""),
        "family_j": meta.get(fj, {}).get("family", ""),
        "same_family": same_fam,
        "spearman_corr": round(spearman, 6),
        "abs_spearman_corr": round(abs_spearman, 6),
        "pearson_corr": round(pearson, 6),
        "n_pairwise_obs": n,
        "redundancy_level": level,
        "recommendation": recommendation_for_pair(level, same_fam, pair_type),
        "pair_type": pair_type,
    }


def compute_redundancy(
    factor_ids: list[str],
    output_path: Path,
    sample_step: int = 1,
    intake_factor_ids: list[str] | None = None,
    baseline_factor_ids: list[str] | None = None,
) -> pd.DataFrame:
    """Compute pairwise redundancy.

    Modes:
      - Library mode: factor_ids compared against each other
      - Intake mode: intake_factor_ids compared against baseline_factor_ids + each other
    """
    meta = load_registry_metadata()

    if intake_factor_ids is not None:
        # Intake mode
        if baseline_factor_ids is None:
            # Default baseline: all computed factors excluding intake
            for mod in ["factor_formula_registry"]:
                if mod in sys.modules:
                    del sys.modules[mod]
            from factor_formula_registry import REGISTRY
            baseline_factor_ids = [
                fs.factor_id for fs in REGISTRY
                if (FEATURES_DIR / fs.factor_id / "factor_values.parquet").exists()
                and fs.factor_id not in set(intake_factor_ids)
            ]
        # Merge all unique factor IDs for loading
        all_ids = list(dict.fromkeys(intake_factor_ids + baseline_factor_ids))
        wide, available = load_factor_wide(all_ids, sample_step)
        if wide.empty:
            return pd.DataFrame()

        intake_set = set(intake_factor_ids)
        baseline_set = set(baseline_factor_ids)
        available_set = set(available)

        pairs = []
        # intake-vs-intake
        intake_avail = [f for f in intake_factor_ids if f in available_set]
        for i in range(len(intake_avail)):
            for j in range(i + 1, len(intake_avail)):
                pairs.append(compute_pair(wide, intake_avail[i], intake_avail[j], meta, "intake_vs_intake"))

        # intake-vs-baseline
        baseline_avail = [f for f in baseline_factor_ids if f in available_set]
        for fi in intake_avail:
            for fj in baseline_avail:
                pairs.append(compute_pair(wide, fi, fj, meta, "intake_vs_baseline"))

        print(f"  Intake mode: {len(intake_avail)} intake × {len(baseline_avail)} baseline = {len(pairs)} pairs")

    else:
        # Library mode
        wide, available = load_factor_wide(factor_ids, sample_step)
        if wide.empty:
            return pd.DataFrame()

        pairs = []
        for i in range(len(available)):
            for j in range(i + 1, len(available)):
                pairs.append(compute_pair(wide, available[i], available[j], meta, "library"))

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
                        help="Factor IDs to compare (library mode)")
    parser.add_argument("--intake-factor-ids", nargs="*", default=None,
                        help="Intake factor IDs (intake mode)")
    parser.add_argument("--baseline-factor-ids", nargs="*", default=None,
                        help="Baseline factor IDs (intake mode, default: all computed non-intake)")
    parser.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT),
                        help="Output CSV path")
    parser.add_argument("--sample-step", type=int, default=1,
                        help="Sample every Nth timestamp (1=no sampling)")
    args = parser.parse_args()

    if args.intake_factor_ids:
        # Intake mode
        intake_ids = args.intake_factor_ids
        baseline_ids = args.baseline_factor_ids
        print(f"Factor Redundancy Diagnostics (intake mode)")
        print(f"  Intake factors: {len(intake_ids)}")
        print(f"  Baseline factors: {'all computed (excl. intake)' if baseline_ids is None else len(baseline_ids)}")
        print(f"  Output: {args.output}")
        print()
        df = compute_redundancy(
            factor_ids=[],
            output_path=Path(args.output),
            sample_step=args.sample_step,
            intake_factor_ids=intake_ids,
            baseline_factor_ids=baseline_ids,
        )
    else:
        # Library mode
        if args.factor_ids:
            factor_ids = args.factor_ids
        else:
            for mod in ["factor_formula_registry"]:
                if mod in sys.modules:
                    del sys.modules[mod]
            from factor_formula_registry import REGISTRY
            factor_ids = [fs.factor_id for fs in REGISTRY
                          if (FEATURES_DIR / fs.factor_id / "factor_values.parquet").exists()]
        print(f"Factor Redundancy Diagnostics (library mode)")
        print(f"  Factors: {len(factor_ids)}")
        print(f"  Output: {args.output}")
        print()
        df = compute_redundancy(factor_ids, Path(args.output), args.sample_step)

    return df


if __name__ == "__main__":
    main()
