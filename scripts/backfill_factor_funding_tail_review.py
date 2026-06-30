#!/usr/bin/env python3
"""Backfill funding-aware tail/review fields into canonical factor evaluation.

This is a lightweight companion to evaluate_factors.py. It reuses existing
canonical price-only RankIC/LS outputs and only computes the additional
after-funding long-short, tail, and review-reason fields needed by the factor
evaluation workflow.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from funding_adjusted_labels import add_funding_adjusted_returns, infer_funding_aligned_path
from evaluate_factors import LABEL_HORIZONS, LABEL_COLS, AFTER_FUNDING_LABEL_COLS, tail_abs_share, tail_diagnosis

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_ID = "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1"
EVAL_DIR = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_level_evaluation"
DIAG_DIR = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_diagnostics"
QUANTILE_BUCKETS = 5
MIN_SYMBOLS = 10


def load_registry_map() -> dict[str, dict[str, Any]]:
    sys.path.insert(0, str(ROOT / "scripts"))
    from factor_formula_registry import REGISTRY

    return {
        fs.factor_id: {
            "factor_name": fs.factor_id,
            "category": getattr(fs, "family", "unknown"),
            "expected_direction": getattr(fs, "expected_direction", "conditional"),
            "required_columns": "|".join(getattr(fs, "required_columns", []) or []),
            "lookback_window": getattr(fs, "lookback_window", None),
        }
        for fs in REGISTRY
    }


def safe_round(value: Any, digits: int = 8):
    if value is None or pd.isna(value):
        return np.nan
    return round(float(value), digits)


def bucket_mean_matrix_from_codes(ts_codes: np.ndarray, n_ts: int, buckets: np.ndarray, values: pd.Series) -> np.ndarray:
    bucket_arr = buckets.astype(np.int16, copy=False)
    value_arr = pd.to_numeric(values, errors="coerce").to_numpy(dtype=float, copy=False)
    valid = np.isfinite(value_arr) & (bucket_arr >= 0) & (bucket_arr < QUANTILE_BUCKETS) & (ts_codes >= 0)
    if n_ts == 0:
        return np.empty((0, QUANTILE_BUCKETS), dtype=float)
    group_id = ts_codes[valid] * QUANTILE_BUCKETS + bucket_arr[valid]
    size = n_ts * QUANTILE_BUCKETS
    sums = np.bincount(group_id, weights=value_arr[valid], minlength=size)
    counts = np.bincount(group_id, minlength=size)
    means = np.full(size, np.nan, dtype=float)
    np.divide(sums, counts, out=means, where=counts > 0)
    return means.reshape(n_ts, QUANTILE_BUCKETS)


def bucket_mean_matrix(timestamps: pd.Series, buckets: pd.Series, values: pd.Series) -> np.ndarray:
    ts_codes, _ = pd.factorize(timestamps, sort=False)
    n_ts = int(ts_codes.max() + 1) if len(ts_codes) else 0
    return bucket_mean_matrix_from_codes(ts_codes, n_ts, buckets.to_numpy(dtype=np.int16), values)


def compute_factor_rows(
    *,
    factor_id: str,
    spec: dict[str, Any],
    factor_values_path: Path,
    labels: pd.DataFrame,
) -> list[dict[str, Any]]:
    fv = pd.read_parquet(factor_values_path, columns=["timestamp", "symbol", "factor_value"])
    fv["timestamp"] = pd.to_datetime(fv["timestamp"], utc=True)
    fv["symbol"] = fv["symbol"].astype(str)
    fv = fv.dropna(subset=["factor_value"])
    if fv.empty:
        return []

    merged = fv.merge(labels, on=["timestamp", "symbol"], how="inner", sort=False, copy=False)
    if merged.empty:
        return []

    direction = spec.get("expected_direction", "conditional")
    merged["_sort_val"] = -merged["factor_value"] if direction == "negative" else merged["factor_value"]
    g = merged.groupby("timestamp", sort=False)["_sort_val"]
    merged["_rank"] = g.rank(method="first")
    merged["_count"] = g.transform("count")
    merged = merged[merged["_count"] >= MIN_SYMBOLS].copy()
    if merged.empty:
        return []
    merged["bucket"] = ((merged["_rank"] - 1) * QUANTILE_BUCKETS / merged["_count"]).astype(int).clip(0, QUANTILE_BUCKETS - 1)
    merged["_ts_code"], _ = pd.factorize(merged["timestamp"], sort=False)
    n_ts_total = int(merged["_ts_code"].max() + 1) if len(merged) else 0
    bucket_arr = merged["bucket"].to_numpy(dtype=np.int16, copy=False)
    ts_code_arr = merged["_ts_code"].to_numpy(dtype=np.int32, copy=False)

    rows: list[dict[str, Any]] = []
    for horizon in LABEL_HORIZONS:
        ret_col = LABEL_COLS[horizon]
        af_col = AFTER_FUNDING_LABEL_COLS[horizon]
        ret_values = pd.to_numeric(merged[ret_col], errors="coerce")
        valid_ret = ret_values.notna().to_numpy()
        if int(valid_ret.sum()) < MIN_SYMBOLS * QUANTILE_BUCKETS:
            continue

        bucket_means = bucket_mean_matrix_from_codes(
            ts_code_arr[valid_ret],
            n_ts_total,
            bucket_arr[valid_ret],
            ret_values[valid_ret],
        )
        if bucket_means.size == 0:
            continue
        ls_arr = bucket_means[:, QUANTILE_BUCKETS - 1] - bucket_means[:, 0]
        ls = pd.Series(ls_arr[np.isfinite(ls_arr)])
        if ls.empty:
            continue

        top = pd.Series(bucket_means[:, QUANTILE_BUCKETS - 1]).dropna()
        bottom = pd.Series(bucket_means[:, 0]).dropna()
        mean_spread = float(ls.mean())
        median_spread = float(ls.median())
        top_tail = tail_abs_share(top)
        bottom_tail = tail_abs_share(bottom)

        af_top_mean = af_bottom_mean = af_mean = af_median = af_t = af_win = af_cov = np.nan
        af_tail = "INSUFFICIENT"
        funding_flip = False
        if af_col in merged.columns:
            af_values = pd.to_numeric(merged[af_col], errors="coerce")
            valid_af = af_values.notna().to_numpy()
            if int(valid_af.sum()) >= MIN_SYMBOLS * QUANTILE_BUCKETS:
                bucket_means_af = bucket_mean_matrix_from_codes(
                    ts_code_arr[valid_af],
                    n_ts_total,
                    bucket_arr[valid_af],
                    af_values[valid_af],
                )
                af_ls_arr = bucket_means_af[:, QUANTILE_BUCKETS - 1] - bucket_means_af[:, 0]
                af_ls = pd.Series(af_ls_arr[np.isfinite(af_ls_arr)])
                if not af_ls.empty:
                    af_top = pd.Series(bucket_means_af[:, QUANTILE_BUCKETS - 1]).dropna()
                    af_bottom = pd.Series(bucket_means_af[:, 0]).dropna()
                    af_mean = float(af_ls.mean())
                    af_median = float(af_ls.median())
                    af_std = float(af_ls.std(ddof=1)) if len(af_ls) > 1 else 0.0
                    af_t = af_mean / (af_std / np.sqrt(len(af_ls))) if af_std > 0 else 0.0
                    af_win = float((af_ls > 0).mean())
                    af_top_mean = float(af_top.mean()) if len(af_top) else np.nan
                    af_bottom_mean = float(af_bottom.mean()) if len(af_bottom) else np.nan
                    af_cov = len(af_ls) / len(ls) if len(ls) else np.nan
                    af_tail = tail_diagnosis(
                        af_mean,
                        af_median,
                        tail_abs_share(af_top),
                        tail_abs_share(af_bottom),
                    )
                    funding_flip = (
                        np.sign(mean_spread) != 0
                        and np.sign(af_mean) != 0
                        and np.sign(mean_spread) != np.sign(af_mean)
                    )

        rows.append({
            "factor_name": factor_id,
            "horizon": horizon,
            "top_bucket_top1pct_abs_share": safe_round(top_tail, 6),
            "bottom_bucket_top1pct_abs_share": safe_round(bottom_tail, 6),
            "long_short_spread_mean": safe_round(mean_spread),
            "long_short_spread_median": safe_round(median_spread),
            "bucket_tail_diagnosis": tail_diagnosis(mean_spread, median_spread, top_tail, bottom_tail),
            "after_funding_top_bucket_mean_return": safe_round(af_top_mean),
            "after_funding_bottom_bucket_mean_return": safe_round(af_bottom_mean),
            "after_funding_long_short_spread_mean": safe_round(af_mean),
            "after_funding_long_short_spread_median": safe_round(af_median),
            "after_funding_long_short_spread_t_stat": safe_round(af_t, 4),
            "after_funding_long_short_win_rate": safe_round(af_win, 4),
            "after_funding_coverage_rate": safe_round(af_cov, 6),
            "after_funding_bucket_tail_diagnosis": af_tail,
            "funding_adjusted_edge_flip": bool(funding_flip),
        })
    return rows


def merge_fields(base: pd.DataFrame, extra: pd.DataFrame, keys: list[str], fields: list[str]) -> pd.DataFrame:
    if extra.empty:
        for field in fields:
            if field not in base.columns:
                base[field] = np.nan
        return base

    out = base.copy()
    for field in fields:
        if field not in out.columns:
            out[field] = np.nan
    update = extra[keys + fields].set_index(keys)
    out_indexed = out.set_index(keys)
    common = out_indexed.index.intersection(update.index)
    out_indexed.loc[common, fields] = update.loc[common, fields]
    return out_indexed.reset_index()


def build_candidate_review(base: pd.DataFrame, metric: pd.DataFrame, registry: dict[str, dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for _, base_row in base.iterrows():
        factor_id = str(base_row.get("factor_name", ""))
        existing = base[base["factor_name"] == factor_id]
        fdf = metric[metric["factor_name"] == factor_id]
        if existing.empty:
            continue
        row = existing.iloc[0].to_dict()
        best_ls = row.get("best_long_short_spread")
        best_adj_ic = row.get("best_adj_ic")
        direction_conflict = str(row.get("rankic_longshort_consistency", "")) == "DIVERGENT"

        review_reasons: list[str] = []
        best_af = np.nan
        best_af_horizon = ""
        best_af_cov = np.nan
        best_tail = ""
        best_af_tail = ""
        any_flip = False
        if not fdf.empty:
            by_abs = fdf.dropna(subset=["after_funding_long_short_spread_mean"]).copy()
            if not by_abs.empty:
                idx = by_abs["after_funding_long_short_spread_mean"].abs().idxmax()
                af_row = by_abs.loc[idx]
                best_af = af_row["after_funding_long_short_spread_mean"]
                best_af_horizon = str(af_row["horizon"])
                best_af_cov = af_row.get("after_funding_coverage_rate", np.nan)
                best_tail = str(af_row.get("bucket_tail_diagnosis", "") or "")
                best_af_tail = str(af_row.get("after_funding_bucket_tail_diagnosis", "") or "")
            any_flip = bool(fdf["funding_adjusted_edge_flip"].map(lambda x: str(x).lower() == "true").any())

        if pd.notna(best_af_cov) and float(best_af_cov) < 0.80:
            review_reasons.append("funding coverage insufficient")
        if any_flip:
            review_reasons.append("funding-adjusted edge flips")
        if pd.notna(best_ls) and pd.notna(best_af) and float(best_ls) > 0 and float(best_af) <= 0:
            review_reasons.append("positive price-only spread turns non-positive after funding")
        if direction_conflict:
            review_reasons.append("RankIC/spread direction conflict")
        for label in [best_tail, best_af_tail]:
            if label in {"TAIL_CONCENTRATED_NEGATIVE_MEAN", "MEAN_SPREAD_OUTLIER_DOMINATED"}:
                review_reasons.append(label.lower())
        if pd.notna(best_ls) and abs(float(best_ls)) < 0.0002:
            review_reasons.append("cost too thin")

        if any_flip or (
            pd.notna(best_ls) and pd.notna(best_af) and float(best_ls) > 0 and float(best_af) <= 0
        ):
            bucket = "FUNDING_ADJUSTED_REVIEW_REQUIRED"
            notes = "Price-only edge weakens or flips after funding adjustment. Do not use price-only spread as economic evidence."
        elif direction_conflict and pd.notna(best_adj_ic) and abs(float(best_adj_ic)) >= 0.02:
            bucket = "DIRECTION_REVIEW_REQUIRED"
            notes = "RankIC and long-short spread point in opposite directions. Direction semantics need review."
        elif best_tail in {"TAIL_CONCENTRATED_NEGATIVE_MEAN", "MEAN_SPREAD_OUTLIER_DOMINATED"}:
            bucket = "TAIL_OR_MONOTONICITY_REVIEW_REQUIRED"
            notes = "Bucket tail diagnostics show mean/median split or tail-concentrated negative mean."
        else:
            bucket = row.get("review_bucket", "METADATA_REVIEW")
            notes = row.get("review_notes", "")

        row.update({
            "best_after_funding_long_short_horizon": best_af_horizon,
            "best_after_funding_long_short_spread": safe_round(best_af),
            "best_after_funding_coverage_rate": safe_round(best_af_cov, 6),
            "best_bucket_tail_diagnosis": best_tail,
            "best_after_funding_bucket_tail_diagnosis": best_af_tail,
            "funding_adjusted_edge_flip": any_flip,
            "review_bucket": bucket,
            "review_reasons": "|".join(sorted(set(review_reasons))),
            "review_notes": notes,
        })
        rows.append(row)
    return pd.DataFrame(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-id", default=DEFAULT_DATASET_ID)
    parser.add_argument("--factor-ids", nargs="*", default=None)
    parser.add_argument("--funding-aligned-path", default=None)
    parser.add_argument("--only-missing", action="store_true",
                        help="Only process canonical factors missing after-funding/tail rows.")
    parser.add_argument("--max-factors", type=int, default=None,
                        help="Optional cap for resource-aware batch backfills.")
    args = parser.parse_args()

    features_dir = ROOT / "data" / "features" / args.dataset_id
    labels_path = features_dir / "labels.parquet"
    funding_path = Path(args.funding_aligned_path) if args.funding_aligned_path else infer_funding_aligned_path(ROOT, args.dataset_id)

    metric_path = EVAL_DIR / "factor_level_metric_panel.csv"
    ls_path = EVAL_DIR / "factor_level_long_short_summary.csv"
    review_path = EVAL_DIR / "factor_level_candidate_review.csv"

    metric = pd.read_csv(metric_path)
    ls = pd.read_csv(ls_path)
    review_base = pd.read_csv(review_path)

    registry = load_registry_map()
    if args.factor_ids:
        factor_ids = args.factor_ids
    else:
        factor_ids = sorted(set(metric["factor_name"].dropna().astype(str)))
    if args.only_missing:
        required = ["after_funding_long_short_spread_mean", "after_funding_coverage_rate", "bucket_tail_diagnosis"]
        for field in required:
            if field not in metric.columns:
                metric[field] = np.nan
        missing_mask = metric[required].isna().any(axis=1)
        missing_factor_ids = set(metric.loc[missing_mask, "factor_name"].dropna().astype(str))
        factor_ids = [fid for fid in factor_ids if fid in missing_factor_ids]
    factor_ids = [fid for fid in factor_ids if fid in registry]
    if args.max_factors is not None:
        factor_ids = factor_ids[: max(args.max_factors, 0)]

    t0 = time.time()
    labels = pd.read_parquet(labels_path)
    labels, funding_manifest = add_funding_adjusted_returns(labels, funding_path, LABEL_HORIZONS)
    label_cols = ["timestamp", "symbol"] + list(LABEL_COLS.values()) + [
        c for c in AFTER_FUNDING_LABEL_COLS.values() if c in labels.columns
    ]
    labels = labels[label_cols]

    rows: list[dict[str, Any]] = []
    missing: list[str] = []
    for i, factor_id in enumerate(factor_ids, start=1):
        path = features_dir / factor_id / "factor_values.parquet"
        if not path.exists():
            missing.append(factor_id)
            continue
        rows.extend(compute_factor_rows(
            factor_id=factor_id,
            spec=registry[factor_id],
            factor_values_path=path,
            labels=labels,
        ))
        print(f"[{i}/{len(factor_ids)}] {factor_id} funding/tail rows={len(rows)}", flush=True)

    extra = pd.DataFrame(rows)
    fields = [
        "top_bucket_top1pct_abs_share",
        "bottom_bucket_top1pct_abs_share",
        "long_short_spread_mean",
        "long_short_spread_median",
        "bucket_tail_diagnosis",
        "after_funding_top_bucket_mean_return",
        "after_funding_bottom_bucket_mean_return",
        "after_funding_long_short_spread_mean",
        "after_funding_long_short_spread_median",
        "after_funding_long_short_spread_t_stat",
        "after_funding_long_short_win_rate",
        "after_funding_coverage_rate",
        "after_funding_bucket_tail_diagnosis",
        "funding_adjusted_edge_flip",
    ]

    metric = merge_fields(metric, extra, ["factor_name", "horizon"], fields)
    ls = merge_fields(ls, extra, ["factor_name", "horizon"], fields)
    review = build_candidate_review(review_base, metric, registry)

    metric.to_csv(metric_path, index=False)
    ls.to_csv(ls_path, index=False)
    review.to_csv(review_path, index=False)

    metric_required = [
        "after_funding_long_short_spread_mean",
        "after_funding_coverage_rate",
        "bucket_tail_diagnosis",
        "after_funding_bucket_tail_diagnosis",
    ]
    metric_complete_mask = metric[metric_required].notna().all(axis=1)
    review_metric_missing = sorted(set(review["factor_name"].dropna().astype(str)) - set(metric["factor_name"].dropna().astype(str)))
    coverage_series = pd.to_numeric(metric["after_funding_coverage_rate"], errors="coerce")

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset_id": args.dataset_id,
        "labels_path": str(labels_path),
        "funding_adjustment": funding_manifest,
        "factors_requested": len(factor_ids),
        "factors_missing_values": missing,
        "factor_horizon_rows": int(len(extra)),
        "canonical_metric_rows_complete": int(metric_complete_mask.sum()),
        "canonical_metric_rows_total": int(len(metric)),
        "canonical_metric_factors_complete": int(metric.loc[metric_complete_mask, "factor_name"].nunique()),
        "canonical_metric_factors_total": int(metric["factor_name"].nunique()),
        "review_factors_missing_canonical_metric": review_metric_missing,
        "after_funding_coverage_rate_min": safe_round(coverage_series.min(), 6),
        "after_funding_coverage_rate_max": safe_round(coverage_series.max(), 6),
        "updated_outputs": [str(metric_path), str(ls_path), str(review_path)],
        "elapsed_seconds": round(time.time() - t0, 1),
        "disclaimer": "Research diagnostics only. Not production, not live trading, not investment advice.",
    }
    out_manifest = DIAG_DIR / "factor_funding_tail_review_backfill_manifest.json"
    out_manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {metric_path}")
    print(f"Wrote {ls_path}")
    print(f"Wrote {review_path}")
    print(f"Wrote {out_manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
