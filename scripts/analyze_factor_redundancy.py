#!/usr/bin/env python3
"""Analyze pairwise factor redundancy via Spearman/Pearson correlation.

Two modes:
  1. Pairwise mode (default): read factor_values parquet, compute pairwise correlations.
  2. Aggregate mode (--aggregate-phase7f): read static + dynamic pairwise CSVs + classification CSV,
     generate redundancy groups and family-level summary.

Phase 7F diagnostic script. No factor evaluation, no backtest, no alpha promotion.
"""
from __future__ import annotations

import argparse
import csv as _csv
import itertools
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]

# Redundancy thresholds
NEAR_DUPLICATE = 0.95
HIGH_REDUNDANCY = 0.85
MODERATE_REDUNDANCY = 0.70

TIER_ORDER = {
    "TIER_1_STABLE_DIAGNOSTIC": 0,
    "TIER_2_PROMISING_BUT_NEEDS_REVIEW": 1,
    "TIER_3_WEAK_DIAGNOSTIC": 2,
    "TIER_4_UNSTABLE_OR_SIGN_FLIP": 3,
}


def load_selected_factor_ids(candidate_csv: Path, status: str) -> list[str]:
    with open(candidate_csv) as f:
        rows = list(_csv.DictReader(f))
    return [r["factor_id"] for r in rows if r["status"] == status]


def load_metadata(candidate_csv: Path) -> dict[str, dict[str, str]]:
    """Load factor_id -> {family, expected_direction, tier} from candidate CSV + classification."""
    with open(candidate_csv) as f:
        rows = list(_csv.DictReader(f))
    meta: dict[str, dict[str, str]] = {}
    for r in rows:
        meta[r["factor_id"]] = {
            "family": r["factor_family"],
            "expected_direction": r["expected_direction"],
        }
    cls_path = candidate_csv.parent / "phase7e_factor_diagnostic_classification.csv"
    if cls_path.exists():
        with open(cls_path) as f:
            for r in _csv.DictReader(f):
                fid = r["factor_id"]
                if fid in meta:
                    meta[fid]["tier"] = r.get("diagnostic_tier", "")
                    meta[fid]["max_turnover_1h"] = r.get("max_turnover_1h", "")
                    meta[fid]["min_coverage_1h"] = r.get("min_coverage_1h", "")
    return meta


def redundancy_level(abs_corr: float) -> str:
    if abs_corr >= NEAR_DUPLICATE:
        return "NEAR_DUPLICATE"
    elif abs_corr >= HIGH_REDUNDANCY:
        return "HIGH_REDUNDANCY"
    elif abs_corr >= MODERATE_REDUNDANCY:
        return "MODERATE_REDUNDANCY"
    else:
        return "LOW_REDUNDANCY"


def compute_pairwise(wide: pd.DataFrame, factor_ids: list[str], meta: dict) -> list[dict]:
    """Compute pairwise Pearson and Spearman correlations from wide table."""
    pairs = []
    n_factors = len(factor_ids)
    for i in range(n_factors):
        for j in range(i + 1, n_factors):
            fi, fj = factor_ids[i], factor_ids[j]
            vi = wide[fi].values
            vj = wide[fj].values
            valid = ~(np.isnan(vi) | np.isnan(vj))
            n = int(valid.sum())
            if n < 30:
                pairs.append({
                    "factor_i": fi, "factor_j": fj,
                    "family_i": meta.get(fi, {}).get("family", ""),
                    "family_j": meta.get(fj, {}).get("family", ""),
                    "same_family": meta.get(fi, {}).get("family", "") == meta.get(fj, {}).get("family", ""),
                    "tier_i": meta.get(fi, {}).get("tier", ""),
                    "tier_j": meta.get(fj, {}).get("tier", ""),
                    "pearson_corr": None, "spearman_corr": None, "abs_spearman_corr": None,
                    "n_pairwise_obs": n, "redundancy_level": "INSUFFICIENT_DATA",
                })
                continue
            a, b = vi[valid], vj[valid]
            pearson = float(np.corrcoef(a, b)[0, 1])
            spearman = float(stats.spearmanr(a, b)[0])
            abs_spearman = abs(spearman)
            pairs.append({
                "factor_i": fi, "factor_j": fj,
                "family_i": meta.get(fi, {}).get("family", ""),
                "family_j": meta.get(fj, {}).get("family", ""),
                "same_family": meta.get(fi, {}).get("family", "") == meta.get(fj, {}).get("family", ""),
                "tier_i": meta.get(fi, {}).get("tier", ""),
                "tier_j": meta.get(fj, {}).get("tier", ""),
                "pearson_corr": round(pearson, 6),
                "spearman_corr": round(spearman, 6),
                "abs_spearman_corr": round(abs_spearman, 6),
                "n_pairwise_obs": n,
                "redundancy_level": redundancy_level(abs_spearman),
            })
    return pairs


def _rep_score(fid: str, meta: dict[str, dict[str, str]]) -> tuple[int, float, float, str]:
    """Sort key for representative selection: tier, turnover asc, -coverage, alpha tiebreak."""
    m = meta.get(fid, {})
    tier = m.get("tier", "")
    try:
        turnover = float(m.get("max_turnover_1h", 99))
    except (ValueError, TypeError):
        turnover = 99.0
    try:
        coverage = float(m.get("min_coverage_1h", 0))
    except (ValueError, TypeError):
        coverage = 0.0
    return (TIER_ORDER.get(tier, 99), turnover, -coverage, fid)


def find_redundancy_groups(
    pairs_static: list[dict],
    pairs_dynamic: list[dict],
    factor_ids: list[str],
    meta: dict[str, dict[str, str]],
) -> list[dict]:
    """Find connected components where any pair has abs_spearman >= HIGH_REDUNDANCY in either regime."""
    adj: dict[str, set[str]] = {fid: set() for fid in factor_ids}
    pair_info: dict[tuple[str, str], dict] = {}

    for pairs, regime in [(pairs_static, "static"), (pairs_dynamic, "dynamic")]:
        for p in pairs:
            if p["abs_spearman_corr"] is None:
                continue
            fi, fj = p["factor_i"], p["factor_j"]
            key = (min(fi, fj), max(fi, fj))
            if key not in pair_info:
                pair_info[key] = {"static": None, "dynamic": None}
            pair_info[key][regime] = p
            if p["abs_spearman_corr"] >= HIGH_REDUNDANCY:
                adj[fi].add(fj)
                adj[fj].add(fi)

    visited: set[str] = set()
    groups: list[list[str]] = []
    for fid in factor_ids:
        if fid in visited or not adj[fid]:
            continue
        component: set[str] = set()
        queue = [fid]
        while queue:
            node = queue.pop(0)
            if node in component:
                continue
            component.add(node)
            visited.add(node)
            for neighbor in adj[node]:
                if neighbor not in component:
                    queue.append(neighbor)
        if len(component) >= 2:
            groups.append(sorted(component))

    group_rows = []
    for gid, members in enumerate(groups, 1):
        families = sorted(set(meta.get(m, {}).get("family", "") for m in members))
        max_s, max_d = 0.0, 0.0
        mean_s: list[float] = []
        mean_d: list[float] = []
        for fi, fj in itertools.combinations(members, 2):
            key = (min(fi, fj), max(fi, fj))
            info = pair_info.get(key, {})
            sp = info.get("static")
            dp = info.get("dynamic")
            if sp and sp["abs_spearman_corr"] is not None:
                max_s = max(max_s, sp["abs_spearman_corr"])
                mean_s.append(sp["abs_spearman_corr"])
            if dp and dp["abs_spearman_corr"] is not None:
                max_d = max(max_d, dp["abs_spearman_corr"])
                mean_d.append(dp["abs_spearman_corr"])

        representative = sorted(members, key=lambda f: _rep_score(f, meta))[0]

        basis_parts = []
        if max_s >= HIGH_REDUNDANCY:
            basis_parts.append(f"static_max={max_s:.3f}")
        if max_d >= HIGH_REDUNDANCY:
            basis_parts.append(f"dynamic_max={max_d:.3f}")

        group_rows.append({
            "group_id": f"RG{gid}",
            "factors": "; ".join(members),
            "families": "; ".join(families),
            "n_factors": len(members),
            "max_abs_corr_static": round(max_s, 4),
            "max_abs_corr_dynamic": round(max_d, 4),
            "mean_abs_corr_static": round(float(np.mean(mean_s)), 4) if mean_s else None,
            "mean_abs_corr_dynamic": round(float(np.mean(mean_d)), 4) if mean_d else None,
            "redundancy_basis": "; ".join(basis_parts),
            "representative_candidate": representative,
            "group_notes": "",
        })
    return group_rows


def family_redundancy_summary_from_pairwise(pairwise_df: pd.DataFrame) -> list[dict]:
    """Summarize within-family redundancy using only same_family == True pairs."""
    same = pairwise_df[pairwise_df["same_family"] == True].copy()
    rows = []
    for fam in sorted(same["family_i"].unique()):
        p_list = same[same["family_i"] == fam]
        n_pairs = len(p_list)
        max_s = float(p_list["abs_spearman_corr"].max())
        n_high = int((p_list["abs_spearman_corr"] >= HIGH_REDUNDANCY).sum())
        n_mod = int((p_list["abs_spearman_corr"] >= MODERATE_REDUNDANCY).sum())
        if n_high > 0:
            assessment = "HIGH_REDUNDANCY"
        elif n_mod > 0:
            assessment = "MODERATE_REDUNDANCY"
        else:
            assessment = "LOW_REDUNDANCY"
        all_factors = set(p_list["factor_i"]) | set(p_list["factor_j"])
        rows.append({
            "family": fam,
            "n_factors": len(all_factors),
            "n_pairs": n_pairs,
            "max_abs_spearman_static": round(max_s, 4),
            "max_abs_spearman_dynamic": 0.0,  # filled by caller
            "n_high_redundancy_pairs_static": n_high,
            "n_high_redundancy_pairs_dynamic": 0,  # filled by caller
            "redundancy_assessment": assessment,
            "notes": "",
        })
    return rows


def aggregate_phase7f(
    static_csv: Path,
    dynamic_csv: Path,
    classification_csv: Path,
    out_dir: Path,
) -> None:
    """Read pairwise CSVs + classification, generate groups and family summary."""
    ps = pd.read_csv(static_csv)
    pd_ = pd.read_csv(dynamic_csv)

    # Load classification for tier/turnover/coverage
    cls = pd.read_csv(classification_csv)
    meta: dict[str, dict[str, str]] = {}
    for _, r in cls.iterrows():
        meta[r["factor_id"]] = {
            "family": r.get("family", ""),
            "tier": r.get("diagnostic_tier", ""),
            "max_turnover_1h": str(r.get("max_turnover_1h", "")),
            "min_coverage_1h": str(r.get("min_coverage_1h", "")),
        }

    factor_ids = sorted(set(ps["factor_i"]) | set(ps["factor_j"]))

    # Convert DataFrames to list-of-dicts for find_redundancy_groups
    ps_list = ps.to_dict("records")
    pd_list = pd_.to_dict("records")

    groups = find_redundancy_groups(ps_list, pd_list, factor_ids, meta)
    out_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(groups).to_csv(out_dir / "phase7f_redundancy_groups.csv", index=False)
    print(f"Redundancy groups: {len(groups)}")

    # Family summary: merge static and dynamic same-family pairs
    fam_s = family_redundancy_summary_from_pairwise(ps)
    fam_d = family_redundancy_summary_from_pairwise(pd_)

    fam_d_map = {r["family"]: r for r in fam_d}
    for row in fam_s:
        fam = row["family"]
        if fam in fam_d_map:
            row["max_abs_spearman_dynamic"] = fam_d_map[fam]["max_abs_spearman_static"]
            row["n_high_redundancy_pairs_dynamic"] = fam_d_map[fam]["n_high_redundancy_pairs_static"]
            dyn_assess = fam_d_map[fam]["redundancy_assessment"]
            if dyn_assess == "HIGH_REDUNDANCY" or row["redundancy_assessment"] == "HIGH_REDUNDANCY":
                row["redundancy_assessment"] = "HIGH_REDUNDANCY"
            elif dyn_assess == "MODERATE_REDUNDANCY" or row["redundancy_assessment"] == "MODERATE_REDUNDANCY":
                row["redundancy_assessment"] = "MODERATE_REDUNDANCY"

    pd.DataFrame(fam_s).to_csv(out_dir / "phase7f_family_redundancy_summary.csv", index=False)
    print(f"Family summary: {len(fam_s)} families")

    for g in groups:
        print(f"  {g['group_id']}: {g['factors']} | rep={g['representative_candidate']}")
    for r in fam_s:
        print(f"  {r['family']}: {r['n_factors']}f {r['n_pairs']}p {r['redundancy_assessment']}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dataset-id", help="Dataset ID for pairwise mode")
    p.add_argument("--candidate-csv", help="Candidate CSV path for pairwise mode")
    p.add_argument("--status", default="selected_for_7B")
    p.add_argument("--out-prefix", help="Output prefix for pairwise CSV")
    p.add_argument("--sample-step", type=int, default=1, help="Sample every Nth timestamp (1=no sampling)")
    p.add_argument("--aggregate-phase7f", action="store_true", help="Aggregate mode: generate groups + family summary")
    p.add_argument("--static-pairwise", help="Static pairwise CSV (aggregate mode)")
    p.add_argument("--dynamic-pairwise", help="Dynamic pairwise CSV (aggregate mode)")
    p.add_argument("--classification-csv", help="Classification CSV (aggregate mode)")
    p.add_argument("--out-dir", help="Output directory (aggregate mode)")
    args = p.parse_args()

    if args.aggregate_phase7f:
        aggregate_phase7f(
            static_csv=Path(args.static_pairwise),
            dynamic_csv=Path(args.dynamic_pairwise),
            classification_csv=Path(args.classification_csv),
            out_dir=Path(args.out_dir),
        )
        return

    # Pairwise mode
    candidate_csv = Path(args.candidate_csv)
    factor_ids = load_selected_factor_ids(candidate_csv, args.status)
    meta = load_metadata(candidate_csv)
    features_dir = ROOT / "data" / "features" / args.dataset_id

    print(f"Dataset: {args.dataset_id}")
    print(f"Factors: {len(factor_ids)}")
    print(f"Sample step: {args.sample_step}")

    parts = {}
    for fid in factor_ids:
        fv_path = features_dir / fid / "factor_values.parquet"
        if not fv_path.exists():
            print(f"  WARNING: missing {fv_path}, skipping {fid}")
            continue
        fv = pd.read_parquet(fv_path, columns=["timestamp", "symbol", "factor_value"])
        fv = fv.rename(columns={"factor_value": fid})
        parts[fid] = fv

    if len(parts) != len(factor_ids):
        print(f"WARNING: only {len(parts)}/{len(factor_ids)} factor_values found")

    print("Merging factor_values into wide table...")
    wide = None
    for fid, fv in parts.items():
        if wide is None:
            wide = fv
        else:
            wide = wide.merge(fv, on=["timestamp", "symbol"], how="outer")

    if args.sample_step > 1:
        ts_all = wide["timestamp"].unique()
        ts_sampled = ts_all[::args.sample_step]
        wide = wide[wide["timestamp"].isin(ts_sampled)]
        print(f"Sampled: {len(ts_sampled)}/{len(ts_all)} timestamps")

    print(f"Wide table: {len(wide)} rows, {len(parts)} factor columns")

    available_ids = list(parts.keys())
    print("Computing pairwise correlations...")
    pairs = compute_pairwise(wide, available_ids, meta)
    print(f"Pairs computed: {len(pairs)}")

    out_prefix = Path(args.out_prefix)
    out_prefix.parent.mkdir(parents=True, exist_ok=True)
    pairwise_path = Path(f"{out_prefix}_pairwise_correlation.csv")
    pd.DataFrame(pairs).to_csv(pairwise_path, index=False)
    print(f"Pairwise -> {pairwise_path}")

    for level in ["NEAR_DUPLICATE", "HIGH_REDUNDANCY", "MODERATE_REDUNDANCY", "LOW_REDUNDANCY"]:
        cnt = sum(1 for p in pairs if p["redundancy_level"] == level)
        print(f"  {level}: {cnt}")


if __name__ == "__main__":
    main()
