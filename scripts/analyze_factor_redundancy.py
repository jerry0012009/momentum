#!/usr/bin/env python3
"""Analyze pairwise factor redundancy via Spearman/Pearson correlation.

Phase 7F diagnostic script. Reads factor_values parquet files, computes
pairwise correlations, identifies redundancy groups, and writes CSV outputs.

No factor evaluation, no backtest, no alpha promotion.
"""
from __future__ import annotations

import argparse
import csv as _csv
import itertools
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]

# Redundancy thresholds
NEAR_DUPLICATE = 0.95
HIGH_REDUNDANCY = 0.85
MODERATE_REDUNDANCY = 0.70


def load_selected_factor_ids(candidate_csv: Path, status: str) -> list[str]:
    with open(candidate_csv) as f:
        rows = list(_csv.DictReader(f))
    return [r["factor_id"] for r in rows if r["status"] == status]


def load_metadata(candidate_csv: Path) -> dict[str, dict[str, str]]:
    """Load factor_id -> {family, expected_direction, tier} from candidate CSV + classification."""
    with open(candidate_csv) as f:
        rows = list(_csv.DictReader(f))
    meta = {}
    for r in rows:
        meta[r["factor_id"]] = {"family": r["factor_family"], "expected_direction": r["expected_direction"]}
    # Load tier from classification if available
    cls_path = candidate_csv.parent / "phase7e_factor_diagnostic_classification.csv"
    if cls_path.exists():
        with open(cls_path) as f:
            for r in _csv.DictReader(f):
                if r["factor_id"] in meta:
                    meta[r["factor_id"]]["tier"] = r.get("diagnostic_tier", "")
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
            xi = wide[fi]
            xj = wide[fj]
            # Use numpy for speed
            vi = xi.values
            vj = xj.values
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


def find_redundancy_groups(pairs_static: list[dict], pairs_dynamic: list[dict], factor_ids: list[str], meta: dict) -> list[dict]:
    """Find connected components where any pair has abs_spearman >= HIGH_REDUNDANCY in either regime."""
    # Build adjacency
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

    # BFS for connected components
    visited = set()
    groups = []
    for fid in factor_ids:
        if fid in visited:
            continue
        if not adj[fid]:
            continue
        component = set()
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

    # Build group rows
    group_rows = []
    for gid, members in enumerate(groups, 1):
        families = sorted(set(meta.get(m, {}).get("family", "") for m in members))
        # Find max and mean abs_corr
        max_s, max_d, mean_s, mean_d = 0, 0, [], []
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

        # Representative: prefer TIER_1, then lowest turnover, then highest coverage
        def rep_score(fid: str) -> tuple[int, float]:
            tier = meta.get(fid, {}).get("tier", "")
            tier_order = {"TIER_1_STABLE_DIAGNOSTIC": 0, "TIER_2_PROMISING_BUT_NEEDS_REVIEW": 1,
                          "TIER_3_WEAK_DIAGNOSTIC": 2, "TIER_4_UNSTABLE_OR_SIGN_FLIP": 3}
            return (tier_order.get(tier, 99), 0)  # turnover not available here, just use tier

        representative = sorted(members, key=rep_score)[0]

        # Basis
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
            "mean_abs_corr_static": round(np.mean(mean_s), 4) if mean_s else None,
            "mean_abs_corr_dynamic": round(np.mean(mean_d), 4) if mean_d else None,
            "redundancy_basis": "; ".join(basis_parts),
            "representative_candidate": representative,
            "group_notes": "",
        })
    return group_rows


def family_redundancy_summary(pairs: list[dict], meta: dict) -> list[dict]:
    """Summarize redundancy at family level."""
    fam_data: dict[str, list[dict]] = {}
    for p in pairs:
        fi_fam = p["family_i"]
        if fi_fam not in fam_data:
            fam_data[fi_fam] = []
        fam_data[fi_fam].append(p)

    rows = []
    for fam, p_list in sorted(fam_data.items()):
        n_pairs = len(p_list)
        max_s = max((p["abs_spearman_corr"] or 0) for p in p_list)
        n_high = sum(1 for p in p_list if (p["abs_spearman_corr"] or 0) >= HIGH_REDUNDANCY)
        n_mod = sum(1 for p in p_list if (p["abs_spearman_corr"] or 0) >= MODERATE_REDUNDANCY)
        if n_high > 0:
            assessment = "HIGH_REDUNDANCY"
        elif n_mod > 0:
            assessment = "MODERATE_REDUNDANCY"
        else:
            assessment = "LOW_REDUNDANCY"
        rows.append({
            "family": fam,
            "n_factors": len(set(p["factor_i"] for p in p_list) | set(p["factor_j"] for p in p_list)),
            "n_pairs": n_pairs,
            "max_abs_spearman": round(max_s, 4),
            "n_high_redundancy_pairs": n_high,
            "n_moderate_redundancy_pairs": n_mod,
            "redundancy_assessment": assessment,
            "notes": "",
        })
    return rows


def main() -> tuple[list[dict], dict, list[str]]:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dataset-id", required=True)
    p.add_argument("--candidate-csv", required=True)
    p.add_argument("--status", default="selected_for_7B")
    p.add_argument("--out-prefix", required=True, help="Output prefix for CSV files")
    p.add_argument("--sample-step", type=int, default=1, help="Sample every Nth timestamp (1=no sampling)")
    args = p.parse_args()

    candidate_csv = Path(args.candidate_csv)
    factor_ids = load_selected_factor_ids(candidate_csv, args.status)
    meta = load_metadata(candidate_csv)
    features_dir = ROOT / "data" / "features" / args.dataset_id

    print(f"Dataset: {args.dataset_id}")
    print(f"Factors: {len(factor_ids)}")
    print(f"Sample step: {args.sample_step}")

    # Load all factor_values and merge into wide table
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

    # Merge all on (timestamp, symbol)
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

    # Compute pairwise correlations
    available_ids = list(parts.keys())
    print("Computing pairwise correlations...")
    pairs = compute_pairwise(wide, available_ids, meta)
    print(f"Pairs computed: {len(pairs)}")

    # Write pairwise CSV
    out_prefix = Path(args.out_prefix)
    out_prefix.parent.mkdir(parents=True, exist_ok=True)
    pairwise_path = Path(f"{out_prefix}_pairwise_correlation.csv")
    pd.DataFrame(pairs).to_csv(pairwise_path, index=False)
    print(f"Pairwise -> {pairwise_path}")

    # Stats
    for level in ["NEAR_DUPLICATE", "HIGH_REDUNDANCY", "MODERATE_REDUNDANCY", "LOW_REDUNDANCY"]:
        cnt = sum(1 for p in pairs if p["redundancy_level"] == level)
        print(f"  {level}: {cnt}")

    return pairs, meta, factor_ids


if __name__ == "__main__":
    main()
