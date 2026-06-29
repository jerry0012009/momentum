#!/usr/bin/env python3
"""Factor Redundancy Diagnostics — memory-safe pairwise version.

Computes pairwise Spearman/Pearson correlations between factor_values.
Supports two modes:
  - Library mode (--factor-ids): compare given factors against each other
  - Intake mode (--intake-factor-ids [--baseline-factor-ids]):
    compare intake factors against baseline (existing library) + each other

Memory-safe design: loads at most 2 factor parquets at a time (pairwise),
applies sample_step BEFORE join, never builds a full wide table.

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

from public_factor_manifest_guard import raise_for_skipped_public_factor_ids

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


def load_factor_series(fid: str, sample_step: int = 1) -> pd.DataFrame | None:
    """Load a single factor's values. Returns DataFrame with columns [timestamp, symbol, factor_value] or None."""
    fv_path = FEATURES_DIR / fid / "factor_values.parquet"
    if not fv_path.exists():
        print(f"  WARNING: missing {fv_path}, skipping {fid}")
        return None
    fv = pd.read_parquet(fv_path, columns=["timestamp", "symbol", "factor_value"])
    fv = fv.dropna(subset=["factor_value"])
    if sample_step > 1:
        ts_all = fv["timestamp"].unique()
        ts_sampled = set(ts_all[::sample_step])
        fv = fv[fv["timestamp"].isin(ts_sampled)]
    return fv


def compute_pair_from_series(
    fi_series: pd.DataFrame,
    fj_series: pd.DataFrame,
    fi: str,
    fj: str,
    meta: dict[str, dict],
    pair_type: str = "library",
) -> dict:
    """Compute redundancy metrics for a single pair from two individual factor DataFrames."""
    merged = fi_series.merge(fj_series, on=["timestamp", "symbol"], how="inner", suffixes=("_i", "_j"))
    merged = merged.dropna(subset=["factor_value_i", "factor_value_j"])
    n = len(merged)

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

    a = merged["factor_value_i"].values
    b = merged["factor_value_j"].values
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
    """Compute pairwise redundancy using memory-safe pairwise loading.

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

        intake_set = set(intake_factor_ids)
        baseline_set = set(baseline_factor_ids)

        # Pre-load intake factors (small set, keep in memory)
        print(f"  Pre-loading {len(intake_factor_ids)} intake factors...")
        intake_cache: dict[str, pd.DataFrame] = {}
        for fid in intake_factor_ids:
            s = load_factor_series(fid, sample_step)
            if s is not None:
                intake_cache[fid] = s
        intake_available = list(intake_cache.keys())

        if len(intake_available) < 1:
            print(f"  ERROR: no intake factors with factor_values")
            return pd.DataFrame()

        pairs = []

        # intake-vs-intake (small, pairwise)
        for i in range(len(intake_available)):
            for j in range(i + 1, len(intake_available)):
                fi, fj = intake_available[i], intake_available[j]
                pairs.append(compute_pair_from_series(
                    intake_cache[fi], intake_cache[fj], fi, fj, meta, "intake_vs_intake"
                ))

        # intake-vs-baseline (streaming: load one baseline at a time)
        baseline_available = [f for f in baseline_factor_ids if (FEATURES_DIR / f / "factor_values.parquet").exists()]
        print(f"  Comparing {len(intake_available)} intake × {len(baseline_available)} baseline (streaming)...")
        for fj in baseline_available:
            fj_series = load_factor_series(fj, sample_step)
            if fj_series is None:
                continue
            for fi in intake_available:
                pairs.append(compute_pair_from_series(
                    intake_cache[fi], fj_series, fi, fj, meta, "intake_vs_baseline"
                ))
            del fj_series  # free memory immediately

        print(f"  Intake mode: {len(intake_available)} intake × {len(baseline_available)} baseline = {len(pairs)} pairs")

    else:
        # Library mode — pairwise, no wide table
        available = []
        for fid in factor_ids:
            fv_path = FEATURES_DIR / fid / "factor_values.parquet"
            if fv_path.exists():
                available.append(fid)
            else:
                print(f"  WARNING: missing {fv_path}, skipping {fid}")

        if len(available) < 2:
            print(f"  ERROR: need at least 2 factors with factor_values, got {len(available)}")
            return pd.DataFrame()

        pairs = []
        for i in range(len(available)):
            fi_series = load_factor_series(available[i], sample_step)
            if fi_series is None:
                continue
            for j in range(i + 1, len(available)):
                fj_series = load_factor_series(available[j], sample_step)
                if fj_series is None:
                    continue
                pairs.append(compute_pair_from_series(
                    fi_series, fj_series, available[i], available[j], meta, "library"
                ))
                del fj_series
            del fi_series

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
    parser.add_argument("--sample-step", type=int, default=0,
                        help="Sample every Nth timestamp (0=auto: 5 for intake, 1 for library)")
    args = parser.parse_args()

    # Auto-determine sample_step for intake mode
    effective_sample_step = args.sample_step
    if effective_sample_step == 0:
        effective_sample_step = 5 if args.intake_factor_ids else 1
        if effective_sample_step > 1:
            print(f"  Auto sample_step={effective_sample_step} (intake mode default)")

    if args.intake_factor_ids:
        # Intake mode
        intake_ids = args.intake_factor_ids
        baseline_ids = args.baseline_factor_ids
        try:
            raise_for_skipped_public_factor_ids(
                [*intake_ids, *(baseline_ids or [])],
                action="redundancy checked",
            )
        except ValueError as exc:
            print(f"  ERROR: {exc}")
            sys.exit(1)
        print(f"Factor Redundancy Diagnostics (intake mode)")
        print(f"  Intake factors: {len(intake_ids)}")
        print(f"  Baseline factors: {'all computed (excl. intake)' if baseline_ids is None else len(baseline_ids)}")
        print(f"  Sample step: {effective_sample_step}")
        print(f"  Output: {args.output}")
        print()
        df = compute_redundancy(
            factor_ids=[],
            output_path=Path(args.output),
            sample_step=effective_sample_step,
            intake_factor_ids=intake_ids,
            baseline_factor_ids=baseline_ids,
        )
    else:
        # Library mode
        if args.factor_ids:
            factor_ids = args.factor_ids
            try:
                raise_for_skipped_public_factor_ids(factor_ids, action="redundancy checked")
            except ValueError as exc:
                print(f"  ERROR: {exc}")
                sys.exit(1)
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
        df = compute_redundancy(factor_ids, Path(args.output), effective_sample_step)

    return df


if __name__ == "__main__":
    main()
