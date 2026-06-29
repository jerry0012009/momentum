#!/usr/bin/env python3
"""
PM-18: Full Pairwise Factor Redundancy Matrix Builder
=====================================================

Memory-safe pairwise correlation matrix builder.
Strategy: load each factor, align timestamps to daily grid, sample,
store as compact arrays, compute all pairwise correlations.

Usage:
    python scripts/build_factor_pairwise_redundancy_matrix.py
    python scripts/build_factor_pairwise_redundancy_matrix.py --sample-step 3
    python scripts/build_factor_pairwise_redundancy_matrix.py --factor-ids rev_2h,mom_vol_adjusted_20h
    python scripts/build_factor_pairwise_redundancy_matrix.py --only-missing
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from public_factor_manifest_guard import raise_for_skipped_public_factor_ids

ROOT = Path(__file__).resolve().parents[1]
FEATURES_DIR = ROOT / "data" / "features" / "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1"
BASE = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"
META_DIR = BASE / "factor_metadata"
STATE_PATH = BASE / "factor_library_state.json"
CARDS_PATH = META_DIR / "factor_bilingual_cards.csv"

NEAR_DUPLICATE_THRESH = 0.95
HIGH_REDUNDANCY_THRESH = 0.80
MODERATE_REDUNDANCY_THRESH = 0.60


def classify_redundancy(abs_s, n, min_obs):
    if n < min_obs: return "INSUFFICIENT_OVERLAP"
    if abs_s >= NEAR_DUPLICATE_THRESH: return "NEAR_DUPLICATE"
    if abs_s >= HIGH_REDUNDANCY_THRESH: return "HIGH_REDUNDANCY"
    if abs_s >= MODERATE_REDUNDANCY_THRESH: return "MODERATE_REDUNDANCY"
    return "LOW_REDUNDANCY"


def recommendation_for_level(level):
    if level == "INSUFFICIENT_OVERLAP": return "insufficient_overlap"
    if level in ("NEAR_DUPLICATE", "HIGH_REDUNDANCY"): return "highly_redundant"
    if level == "MODERATE_REDUNDANCY": return "moderately_redundant"
    return "likely_distinct"


def load_factor_metadata():
    with open(STATE_PATH) as f:
        state = json.load(f)
    factor_ids = sorted(state.get("registered_factor_ids", []))
    cards = pd.read_csv(CARDS_PATH)
    cards["factor_id"] = cards["factor_id"].astype(str).str.strip()
    family_map = dict(zip(cards["factor_id"], cards["family"]))
    return factor_ids, family_map


def load_and_sample_factor(fid, sample_step, max_rows):
    """Load factor, align timestamps to daily grid, sample."""
    fv_path = FEATURES_DIR / fid / "factor_values.parquet"
    if not fv_path.exists():
        return None
    fv = pd.read_parquet(fv_path, columns=["timestamp", "symbol", "factor_value"])
    fv = fv.dropna(subset=["factor_value"])

    # Align to daily grid: truncate timestamp to date
    fv["date"] = pd.to_datetime(fv["timestamp"]).dt.date

    # Sample every Nth unique date
    dates_all = np.sort(fv["date"].unique())
    dates_sampled = dates_all[::sample_step]
    dates_set = set(dates_sampled.tolist())
    fv = fv[fv["date"].isin(dates_set)]

    # Drop the helper column, keep original timestamp for merge
    fv = fv.drop(columns=["date"])

    # Cap rows
    if len(fv) > max_rows:
        fv = fv.head(max_rows)

    return fv


def load_all_factors_sampled(factor_ids, sample_step, max_rows):
    cache = {}
    for i, fid in enumerate(factor_ids):
        fv = load_and_sample_factor(fid, sample_step, max_rows)
        if fv is not None:
            cache[fid] = fv
        if (i + 1) % 20 == 0:
            print(f"  Loaded {i + 1}/{len(factor_ids)} ({len(cache)} valid)")
    print(f"  Loaded all {len(cache)} valid factors")
    return cache


def compute_all_pairs(factor_ids, cache, family_map, min_obs, target_ids=None):
    if target_ids is not None:
        pairs = [(fi, fj) for fi, fj in combinations(factor_ids, 2)
                 if fi in target_ids or fj in target_ids]
    else:
        pairs = list(combinations(factor_ids, 2))
    print(f"[PM-18] Computing {len(pairs)} pairwise correlations{' (incremental mode)' if target_ids else ''}...")
    t0 = time.time()

    rows = []
    for idx, (fi, fj) in enumerate(pairs):
        dfi = cache.get(fi)
        dfj = cache.get(fj)
        if dfi is None or dfj is None:
            rows.append(_insufficient(fi, fj, family_map))
            continue

        # Merge on (timestamp, symbol) — timestamps are now aligned to daily grid
        merged = dfi.merge(dfj, on=["timestamp", "symbol"], suffixes=("_i", "_j"))
        merged = merged.dropna(subset=["factor_value_i", "factor_value_j"])
        n = len(merged)

        if n < min_obs:
            rows.append(_insufficient(fi, fj, family_map, n))
            continue

        a = merged["factor_value_i"].values
        b = merged["factor_value_j"].values

        pearson = float(np.corrcoef(a, b)[0, 1])
        spearman = float(stats.spearmanr(a, b)[0])
        abs_p, abs_s = abs(pearson), abs(spearman)

        level = classify_redundancy(abs_s, n, min_obs)
        rows.append({
            "factor_i": fi, "factor_j": fj,
            "family_i": family_map.get(fi, ""), "family_j": family_map.get(fj, ""),
            "same_family": family_map.get(fi) == family_map.get(fj),
            "n_pairwise_obs": n,
            "pearson_corr": round(pearson, 6),
            "spearman_corr": round(spearman, 6),
            "abs_pearson_corr": round(abs_p, 6),
            "abs_spearman_corr": round(abs_s, 6),
            "redundancy_level": level,
            "recommendation": recommendation_for_level(level),
        })

        if (idx + 1) % 500 == 0:
            print(f"  {idx + 1}/{len(pairs)} pairs ({time.time()-t0:.1f}s)")

    print(f"  Done: {len(rows)} pairs in {time.time()-t0:.1f}s")
    return pd.DataFrame(rows)


def _insufficient(fi, fj, family_map, n=0):
    return {
        "factor_i": fi, "factor_j": fj,
        "family_i": family_map.get(fi, ""), "family_j": family_map.get(fj, ""),
        "same_family": family_map.get(fi) == family_map.get(fj),
        "n_pairwise_obs": n,
        "pearson_corr": None, "spearman_corr": None,
        "abs_pearson_corr": None, "abs_spearman_corr": None,
        "redundancy_level": "INSUFFICIENT_OVERLAP",
        "recommendation": "insufficient_overlap",
    }


def build_factor_summary(pairwise_df, factor_ids, family_map):
    rows = []
    for fid in factor_ids:
        mask = (pairwise_df["factor_i"] == fid) | (pairwise_df["factor_j"] == fid)
        all_pairs = pairwise_df[mask]
        if all_pairs.empty:
            rows.append({"factor_id": fid, "family": family_map.get(fid, ""),
                         "nearest_factor": "", "nearest_family": "",
                         "nearest_abs_spearman_corr": None, "nearest_abs_pearson_corr": None,
                         "strongest_redundancy_level": "INSUFFICIENT_OVERLAP",
                         "n_high_redundancy_pairs": 0, "n_moderate_redundancy_pairs": 0,
                         "n_low_redundancy_pairs": 0, "n_valid_pairs": 0,
                         "redundancy_confidence": "LOW", "novelty_assessment": "INSUFFICIENT_OVERLAP"})
            continue

        valid = all_pairs[all_pairs["redundancy_level"] != "INSUFFICIENT_OVERLAP"]
        n_valid, n_total = len(valid), len(all_pairs)
        n_insuf = n_total - n_valid

        if n_valid > 0:
            best_idx = valid["abs_spearman_corr"].idxmax()
            best = valid.loc[best_idx]
            nf = best["factor_j"] if best["factor_i"] == fid else best["factor_i"]
            nn = best["family_j"] if best["factor_i"] == fid else best["family_i"]
            ns = best["abs_spearman_corr"]
            np_ = best.get("abs_pearson_corr")
        else:
            nf, nn, ns, np_ = "", "", None, None

        nd = int((valid["redundancy_level"] == "NEAR_DUPLICATE").sum())
        nh = int((valid["redundancy_level"] == "HIGH_REDUNDANCY").sum())
        nm = int((valid["redundancy_level"] == "MODERATE_REDUNDANCY").sum())
        nl = int((valid["redundancy_level"] == "LOW_REDUNDANCY").sum())

        strongest = ("NEAR_DUPLICATE" if nd > 0 else "HIGH_REDUNDANCY" if nh > 0
                     else "MODERATE_REDUNDANCY" if nm > 0 else "LOW_REDUNDANCY" if nl > 0
                     else "INSUFFICIENT_OVERLAP")

        conf = "HIGH" if n_insuf == 0 else "MEDIUM" if n_insuf <= 5 else "LOW"

        if nd + nh > 0:
            novelty = "HIGHLY_REDUNDANT"
        elif nm >= 3:
            novelty = "MODERATELY_REDUNDANT"
        elif n_total > 0 and n_insuf > n_total * 0.5:
            novelty = "INSUFFICIENT_OVERLAP"
        elif nl > 0 and nd + nh + nm == 0:
            novelty = "LIKELY_DISTINCT"
        else:
            novelty = "NEEDS_REVIEW"

        rows.append({
            "factor_id": fid, "family": family_map.get(fid, ""),
            "nearest_factor": nf, "nearest_family": nn,
            "nearest_abs_spearman_corr": round(ns, 6) if ns is not None else None,
            "nearest_abs_pearson_corr": round(np_, 6) if np_ is not None else None,
            "strongest_redundancy_level": strongest,
            "n_high_redundancy_pairs": nd + nh,
            "n_moderate_redundancy_pairs": nm,
            "n_low_redundancy_pairs": nl,
            "n_valid_pairs": n_valid,
            "redundancy_confidence": conf,
            "novelty_assessment": novelty,
        })
    return pd.DataFrame(rows)


def build_correlation_matrix(pairwise_df, factor_ids, col):
    mat = pd.DataFrame(np.nan, index=factor_ids, columns=factor_ids)
    for fid in factor_ids:
        mat.loc[fid, fid] = 1.0
    for _, row in pairwise_df.iterrows():
        val = row.get(col)
        if val is not None and not (isinstance(val, float) and np.isnan(val)):
            mat.loc[row["factor_i"], row["factor_j"]] = val
            mat.loc[row["factor_j"], row["factor_i"]] = val
    return mat


def detect_clusters(pairwise_df, factor_ids, threshold=0.80):
    adj = {fid: set() for fid in factor_ids}
    for _, row in pairwise_df.iterrows():
        if row.get("abs_spearman_corr") is not None and row["abs_spearman_corr"] >= threshold:
            adj[row["factor_i"]].add(row["factor_j"])
            adj[row["factor_j"]].add(row["factor_i"])

    visited = set()
    clusters = []
    for fid in factor_ids:
        if fid in visited:
            continue
        comp = []
        queue = [fid]
        while queue:
            node = queue.pop(0)
            if node in visited:
                continue
            visited.add(node)
            comp.append(node)
            for nb in adj[node]:
                if nb not in visited:
                    queue.append(nb)
        clusters.append(sorted(comp))

    rows = []
    for cid, members in enumerate(clusters):
        ms = ";".join(sorted(members))
        for fid in sorted(members):
            rows.append({"factor_id": fid, "cluster_id": cid, "cluster_size": len(members), "cluster_members": ms})
    return pd.DataFrame(rows)


EVAL_MATRIX_CSV = BASE / "factor_diagnostics" / "factor_evaluation_evidence_matrix.csv"


def _resolve_target_ids(args):
    """Resolve --factor-ids and --only-missing into a set of target factor IDs."""
    target_ids = set()
    if args.factor_ids:
        target_ids = set(fid.strip() for fid in args.factor_ids.split(",") if fid.strip())
        print(f"[PM-18] --factor-ids: targeting {len(target_ids)} factors: {sorted(target_ids)}")
    if args.only_missing:
        ev = pd.read_csv(EVAL_MATRIX_CSV)
        missing = set(ev[ev["has_redundancy_summary"] == False]["factor_id"].tolist())
        print(f"[PM-18] --only-missing: {len(missing)} factors missing redundancy summary")
        target_ids |= missing
    return target_ids if target_ids else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-step", type=int, default=3)
    parser.add_argument("--max-sampled-rows", type=int, default=50000)
    parser.add_argument("--min-pairwise-obs", type=int, default=1000)
    parser.add_argument("--output-dir", type=str, default=str(BASE / "factor_diagnostics"))
    parser.add_argument("--factor-ids", type=str, default=None,
                        help="Comma-separated list of factor IDs to compute (incremental mode)")
    parser.add_argument("--only-missing", action="store_true",
                        help="Auto-detect factors missing redundancy summary from evidence matrix")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    target_ids = _resolve_target_ids(args)
    if target_ids:
        try:
            raise_for_skipped_public_factor_ids(
                sorted(target_ids),
                action="pairwise-redundancy diagnosed",
            )
        except ValueError as exc:
            print(f"ERROR: {exc}")
            return 1
    incremental = target_ids is not None

    print("=" * 70)
    print("PM-18: Full Pairwise Factor Redundancy Matrix Builder")
    if incremental:
        print("  MODE: INCREMENTAL (targeting specific factors)")
    print("=" * 70)
    print(f"  sample_step={args.sample_step}  max_rows={args.max_sampled_rows}  min_obs={args.min_pairwise_obs}")

    factor_ids, family_map = load_factor_metadata()
    print(f"[PM-18] {len(factor_ids)} registered factors")

    # Validate target IDs exist in registered factors
    if target_ids:
        unknown = target_ids - set(factor_ids)
        if unknown:
            print(f"  ⚠️  Unknown factor IDs (not in registry): {sorted(unknown)}")
            target_ids -= unknown

    t_start = time.time()

    print("[PM-18] Loading and sampling factors (daily grid alignment)...")
    cache = load_all_factors_sampled(factor_ids, args.sample_step, args.max_sampled_rows)
    loaded_ids = sorted(cache.keys())

    # Check sample sizes
    sample_sizes = {fid: len(df) for fid, df in cache.items()}
    print(f"  Sample sizes: min={min(sample_sizes.values())}, max={max(sample_sizes.values())}, median={np.median(list(sample_sizes.values())):.0f}")

    # Check timestamp alignment
    ts_sets = {fid: set(df["timestamp"].tolist()) for fid, df in cache.items()}
    all_ts = set()
    for ts in ts_sets.values():
        all_ts |= ts
    print(f"  Total unique timestamps across all factors: {len(all_ts)}")

    if incremental:
        # Incremental mode: compute only pairs involving target factors
        new_pairwise_df = compute_all_pairs(loaded_ids, cache, family_map, args.min_pairwise_obs, target_ids=target_ids)
        del cache

        new_pairwise_df = new_pairwise_df.sort_values("abs_spearman_corr", ascending=False, na_position="last").reset_index(drop=True)

        # Load existing pairwise data and merge
        existing_pw_path = output_dir / "factor_pairwise_redundancy.csv"
        if existing_pw_path.exists():
            print(f"[PM-18] Loading existing pairwise data from {existing_pw_path.name}...")
            old_pw = pd.read_csv(existing_pw_path)
            # Drop any old rows involving target factors
            mask = (old_pw["factor_i"].isin(target_ids)) | (old_pw["factor_j"].isin(target_ids))
            kept = old_pw[~mask]
            print(f"  Kept {len(kept)} existing rows, dropped {mask.sum()} rows involving target factors")
            # Merge: drop unnamed index column if present
            kept = kept.drop(columns=[c for c in kept.columns if c.startswith("Unnamed")], errors="ignore")
            new_pairwise_df = new_pairwise_df.drop(columns=[c for c in new_pairwise_df.columns if c.startswith("Unnamed")], errors="ignore")
            pairwise_df = pd.concat([kept, new_pairwise_df], ignore_index=True)
        else:
            print(f"[PM-18] No existing pairwise file found, starting fresh")
            pairwise_df = new_pairwise_df

        pairwise_df = pairwise_df.sort_values("abs_spearman_corr", ascending=False, na_position="last").reset_index(drop=True)

        # Rebuild summary/clusters/matrices from ALL factors in merged pairwise data
        all_pw_factors = sorted(set(pairwise_df["factor_i"].tolist() + pairwise_df["factor_j"].tolist()))
        print(f"[PM-18] Merged pairwise: {len(pairwise_df)} pairs covering {len(all_pw_factors)} factors")

        # Use loaded_ids (all registered) for summary so every factor gets a row
        summary_df = build_factor_summary(pairwise_df, loaded_ids, family_map)
        spearman_mat = build_correlation_matrix(pairwise_df, loaded_ids, "spearman_corr")
        pearson_mat = build_correlation_matrix(pairwise_df, loaded_ids, "pearson_corr")
        clusters_df = detect_clusters(pairwise_df, loaded_ids, threshold=HIGH_REDUNDANCY_THRESH)

    else:
        # Full mode: compute all pairs
        pairwise_df = compute_all_pairs(loaded_ids, cache, family_map, args.min_pairwise_obs)
        del cache

        pairwise_df = pairwise_df.sort_values("abs_spearman_corr", ascending=False, na_position="last").reset_index(drop=True)

        summary_df = build_factor_summary(pairwise_df, loaded_ids, family_map)
        spearman_mat = build_correlation_matrix(pairwise_df, loaded_ids, "spearman_corr")
        pearson_mat = build_correlation_matrix(pairwise_df, loaded_ids, "pearson_corr")
        clusters_df = detect_clusters(pairwise_df, loaded_ids, threshold=HIGH_REDUNDANCY_THRESH)

    elapsed = time.time() - t_start

    for name, df in [("factor_pairwise_redundancy.csv", pairwise_df),
                     ("factor_redundancy_summary.csv", summary_df),
                     ("factor_redundancy_matrix_spearman.csv", spearman_mat),
                     ("factor_redundancy_matrix_pearson.csv", pearson_mat),
                     ("factor_redundancy_clusters.csv", clusters_df)]:
        df.to_csv(output_dir / name)
        print(f"[PM-18] Wrote {name}: {df.shape}")

    manifest = {
        "framework_version": "pm18_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(elapsed, 1),
        "total_factors": len(loaded_ids),
        "total_pairs": len(pairwise_df),
        "expected_pairs": len(loaded_ids) * (len(loaded_ids) - 1) // 2,
        "incremental_mode": incremental,
        "target_factor_ids": sorted(target_ids) if target_ids else None,
        "sampling": {"sample_step": args.sample_step, "max_sampled_rows": args.max_sampled_rows, "min_pairwise_obs": args.min_pairwise_obs, "method": "daily_grid_alignment"},
        "thresholds": {"near_duplicate": NEAR_DUPLICATE_THRESH, "high_redundancy": HIGH_REDUNDANCY_THRESH, "moderate_redundancy": MODERATE_REDUNDANCY_THRESH},
        "redundancy_distribution": pairwise_df["redundancy_level"].value_counts().to_dict(),
        "novelty_distribution": summary_df["novelty_assessment"].value_counts().to_dict(),
        "confidence_distribution": summary_df["redundancy_confidence"].value_counts().to_dict(),
        "cluster_count": int(clusters_df["cluster_id"].nunique()),
    }
    with open(output_dir / "factor_pairwise_redundancy_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2, default=str)

    print()
    print("=" * 70)
    print("REDUNDANCY LEVELS:")
    for lv in ["NEAR_DUPLICATE", "HIGH_REDUNDANCY", "MODERATE_REDUNDANCY", "LOW_REDUNDANCY", "INSUFFICIENT_OVERLAP"]:
        print(f"  {lv}: {(pairwise_df['redundancy_level']==lv).sum()}")
    print("\nNOVELTY:")
    for nv in ["LIKELY_DISTINCT", "NEEDS_REVIEW", "MODERATELY_REDUNDANT", "HIGHLY_REDUNDANT", "INSUFFICIENT_OVERLAP"]:
        c = (summary_df["novelty_assessment"]==nv).sum()
        if c: print(f"  {nv}: {c}")
    print(f"\nCLUSTERS: {clusters_df['cluster_id'].nunique()}")
    print(f"Elapsed: {elapsed:.1f}s")

    if incremental:
        # Validate target factors appear in output
        pw_factors = set(pairwise_df["factor_i"].tolist() + pairwise_df["factor_j"].tolist())
        for tid in sorted(target_ids):
            in_pw = tid in pw_factors
            in_summary = tid in summary_df["factor_id"].values
            print(f"  ✅ {tid}: pairwise={in_pw}, summary={in_summary}")
        print(f"\n✅ INCREMENTAL PASS: {len(pairwise_df)} pairs, {len(summary_df)} factors")
    else:
        n_exp = len(loaded_ids) * (len(loaded_ids) - 1) // 2
        errs = []
        if len(pairwise_df) != n_exp:
            errs.append(f"Pairs {len(pairwise_df)} != {n_exp}")
        if len(summary_df) != len(loaded_ids):
            errs.append(f"Summary {len(summary_df)} != {len(loaded_ids)}")
        if errs:
            for e in errs: print(f"  ❌ {e}")
            return 1
        print(f"\n✅ PASS: {len(pairwise_df)} pairs, {len(summary_df)} factors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
