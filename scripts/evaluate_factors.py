#!/usr/bin/env python3
"""Evaluate registered crypto research factors with cross-sectional IC and quintile spread.

V0 audit improvements:
- Excludes symbols with missing_bar_rate > 5% (gap symbols)
- Adds direction-adjusted spread based on factor catalog's expected_direction
- timestamp = bar_close_time (see build_labels.py)

Phase 7D-A additions:
- --factor-ids / --candidate-csv / --status for factor subset selection
- candidate CSV direction source (priority: candidate CSV > old catalog > fallback positive)
- fail-fast on missing factor_values / count / direction in explicit/candidate mode
- machine-readable summary CSV output
"""
from __future__ import annotations

import json
import argparse
import csv as _csv
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"
CATALOG = RUN / "factor_catalog_v0_1.csv"
CANDIDATE_CSV_DEFAULT = RUN / "factor_mining_candidates_v0_1.csv"
LABEL_NAMES = ["ret_fwd_1h", "ret_fwd_4h", "ret_fwd_24h", "ret_fwd_72h"]
MIN_N = 10
MISSING_BAR_RATE_THRESHOLD = 0.05  # exclude symbols with >5% missing bars


# ---------------------------------------------------------------------------
# Phase 7D-A: factor subset + direction helpers
# ---------------------------------------------------------------------------

def load_selected_factor_ids(candidate_csv: Path, status: str = "selected_for_7B") -> list[str]:
    """Load factor_ids from candidate CSV with given status."""
    with open(candidate_csv) as f:
        rows = list(_csv.DictReader(f))
    ids = [r["factor_id"] for r in rows if r["status"] == status]
    return ids


def load_candidate_directions(candidate_csv: Path) -> dict[str, str]:
    """Load expected_direction from candidate CSV.

    Returns dict: factor_id -> expected_direction.
    """
    with open(candidate_csv) as f:
        rows = list(_csv.DictReader(f))
    return {r["factor_id"]: r["expected_direction"] for r in rows}


def validate_factor_ids(factor_ids: list[str], registry: dict[str, Any]) -> None:
    """Raise ValueError if any factor_id is not in REGISTRY."""
    missing = [fid for fid in factor_ids if fid not in registry]
    if missing:
        raise ValueError(f"Factor IDs not in REGISTRY: {missing}")


# ---------------------------------------------------------------------------
# Original helpers
# ---------------------------------------------------------------------------

def clean_float(x: Any) -> float | None:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    if math.isnan(v) or math.isinf(v):
        return None
    return v


def avg(xs: list[float]) -> float | None:
    xs = [x for x in xs if clean_float(x) is not None]
    return clean_float(np.mean(xs)) if xs else None


def std(xs: list[float]) -> float | None:
    xs = [x for x in xs if clean_float(x) is not None]
    return clean_float(np.std(xs, ddof=1)) if len(xs) > 1 else None


def tstat(xs: list[float]) -> float | None:
    xs = [x for x in xs if clean_float(x) is not None]
    if len(xs) < 2:
        return None
    s = np.std(xs, ddof=1)
    return clean_float(np.mean(xs) / s * math.sqrt(len(xs))) if s else None


def ratio(m: float | None, s: float | None) -> float | None:
    return clean_float(m / s) if m is not None and s not in (None, 0) else None


def corr(x: pd.Series, y: pd.Series) -> float | None:
    if x.nunique(dropna=True) < 2 or y.nunique(dropna=True) < 2:
        return None
    return clean_float(x.corr(y))


def qcut(values: pd.Series) -> pd.Series:
    return pd.qcut(values.rank(method="first"), 5, labels=[1, 2, 3, 4, 5])


def turnover(sets: list[set[str]]) -> float | None:
    vals = []
    for prev, cur in zip(sets[:-1], sets[1:]):
        if cur:
            vals.append(1.0 - len(prev & cur) / len(cur))
    return avg(vals)


def compute_missing_bar_rates(bars_path: Path | None = None) -> dict[str, float]:
    """Compute missing_bar_rate per symbol from bars_1h.parquet."""
    if not bars_path.exists():
        return {}
    bars = pd.read_parquet(bars_path)
    bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True)
    ts_min = bars["timestamp"].min()
    ts_max = bars["timestamp"].max()
    n_hours = int((ts_max - ts_min).total_seconds() / 3600) + 1
    if n_hours <= 0:
        return {}
    counts = bars.groupby("symbol").size()
    rates = {}
    for sym, cnt in counts.items():
        rates[sym] = 1.0 - cnt / n_hours
    return rates


def get_excluded_symbols(missing_rates: dict[str, float], threshold: float = MISSING_BAR_RATE_THRESHOLD) -> set[str]:
    return {sym for sym, rate in missing_rates.items() if rate > threshold}


def load_catalog_directions(catalog_path: Path | None = None) -> dict[str, str]:
    """Load expected_direction from factor catalog CSV."""
    if catalog_path is None:
        catalog_path = CATALOG
    if not catalog_path.exists():
        return {}
    cat = pd.read_csv(catalog_path)
    directions = {}
    for _, row in cat.iterrows():
        fid = row.get("factor_id")
        d = row.get("expected_direction", "positive")
        if pd.isna(d):
            d = "positive"
        directions[str(fid)] = str(d).strip().lower()
    return directions


def evaluate_one_label(
    df: pd.DataFrame,
    label: str,
    expected_direction: str = "positive",
) -> dict[str, Any]:
    """Vectorized evaluation using pivot tables + numpy quintile assignment."""
    total = len(df)
    factor_coverage = clean_float(df["factor_value"].notna().mean()) if total else 0.0
    valid = df[["timestamp", "symbol", "factor_value", label]].dropna()
    if valid.empty:
        return _empty_metrics(label, factor_coverage, total, expected_direction)

    fv_pivot = valid.pivot_table(index="timestamp", columns="symbol", values="factor_value")
    lb_pivot = valid.pivot_table(index="timestamp", columns="symbol", values=label)
    n_ts = len(fv_pivot)

    ics = fv_pivot.corrwith(lb_pivot, axis=1).dropna().tolist()
    rics = fv_pivot.rank(axis=1).corrwith(lb_pivot.rank(axis=1), axis=1).dropna().tolist()

    fv_arr = fv_pivot.values
    lb_arr = lb_pivot.values
    fv_pctile = np.full_like(fv_arr, np.nan)
    for i in range(n_ts):
        row = fv_arr[i]
        mask = ~np.isnan(row)
        n_valid = mask.sum()
        if n_valid >= MIN_N:
            ranked = np.argsort(np.argsort(row[mask])) + 1
            fv_pctile[i, mask] = ranked / n_valid

    q = np.floor(fv_pctile * 5).clip(0, 4).astype(float) + 1
    q[np.isnan(fv_pctile)] = np.nan

    raw_spreads = []
    dir_adj_spreads = []
    qmeans = {str(qi): [] for qi in range(1, 6)}
    top_sets: list[set[str]] = []
    bottom_sets: list[set[str]] = []
    symbols = fv_pivot.columns.tolist()

    for i in range(n_ts):
        q_row = q[i]
        lb_row = lb_arr[i]
        for qi in range(1, 6):
            m = q_row == qi
            if np.any(m & ~np.isnan(lb_row)):
                qmeans[str(qi)].append(float(np.nanmean(lb_row[m])))
        q1_m = q_row == 1
        q5_m = q_row == 5
        q1_val = np.nanmean(lb_row[q1_m]) if np.any(q1_m) else np.nan
        q5_val = np.nanmean(lb_row[q5_m]) if np.any(q5_m) else np.nan
        if not np.isnan(q1_val) and not np.isnan(q5_val):
            raw_spread = q5_val - q1_val
            raw_spreads.append(raw_spread)
            if expected_direction == "positive":
                dir_adj_spreads.append(raw_spread)
            elif expected_direction == "negative":
                dir_adj_spreads.append(q1_val - q5_val)
            bottom_sets.append({symbols[j] for j in range(len(symbols)) if q1_m[j] and not np.isnan(lb_arr[i, j])})
            top_sets.append({symbols[j] for j in range(len(symbols)) if q5_m[j] and not np.isnan(lb_arr[i, j])})

    icm, icsd = avg(ics), std(ics)
    ricm, ricsd = avg(rics), std(rics)
    top_to, bottom_to = turnover(top_sets), turnover(bottom_sets)

    dir_spread_mean = avg(dir_adj_spreads) if dir_adj_spreads else None
    dir_spread_t = tstat(dir_adj_spreads) if dir_adj_spreads else None

    return {
        "label": label,
        "expected_direction": expected_direction,
        "coverage": factor_coverage,
        "missing_rate": clean_float(1 - factor_coverage) if factor_coverage is not None else None,
        "IC_mean": icm,
        "IC_std": icsd,
        "ICIR": ratio(icm, icsd),
        "IC_positive_ratio": clean_float(np.mean([x > 0 for x in ics])) if ics else None,
        "RankIC_mean": ricm,
        "RankIC_std": ricsd,
        "RankICIR": ratio(ricm, ricsd),
        "RankIC_positive_ratio": clean_float(np.mean([x > 0 for x in rics])) if rics else None,
        "quantile_spread_mean": avg(raw_spreads),
        "quantile_spread_tstat": tstat(raw_spreads),
        "direction_adjusted_spread": dir_spread_mean,
        "direction_adjusted_tstat": dir_spread_t,
        "quantile_mean_returns": {k: avg(v) for k, v in qmeans.items()},
        "turnover": avg([x for x in [top_to, bottom_to] if x is not None]),
        "top_turnover": top_to,
        "bottom_turnover": bottom_to,
        "n_timestamps": len(ics),
        "n_symbols_avg": clean_float(fv_pivot.count(axis=1).mean()),
        "n_merged_rows": int(total),
        "n_valid_rows": int(len(valid)),
    }


def _empty_metrics(label: str, coverage: float | None, total: int, expected_direction: str = "positive") -> dict:
    return {"label": label, "expected_direction": expected_direction, "coverage": coverage, "missing_rate": None,
            "IC_mean": None, "IC_std": None, "ICIR": None, "IC_positive_ratio": None,
            "RankIC_mean": None, "RankIC_std": None, "RankICIR": None, "RankIC_positive_ratio": None,
            "quantile_spread_mean": None, "quantile_spread_tstat": None,
            "direction_adjusted_spread": None, "direction_adjusted_tstat": None,
            "quantile_mean_returns": {},
            "turnover": None, "top_turnover": None, "bottom_turnover": None,
            "n_timestamps": 0, "n_symbols_avg": None, "n_merged_rows": total, "n_valid_rows": 0}


def fmt(x: Any) -> str:
    v = clean_float(x)
    return "" if v is None else f"{v:.6f}"


def write_factor_md(factor: str, metrics: dict[str, Any], path: Path, universe: str = "crypto_top50_usdt_perp_1h") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Factor Evaluation: `{factor}`",
        "",
        f"- universe: `{universe}`",
        f"- evaluation_period: `{metrics['evaluation_period']}`",
        f"- generated_at: `{metrics['generated_at']}`",
        "- caveat: Static current Top50 diagnostic universe; debug and initial screening only.",
        f"- excluded_symbols (missing_bar_rate > 5%): {metrics.get('excluded_symbols', [])}",
        "",
        "| label | direction | IC_mean | ICIR | RankIC_mean | RankICIR | raw_spread | raw_spread_t | dir_adj_spread | dir_adj_t | turnover | coverage | n_ts |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for label, m in metrics["label_metrics"].items():
        lines.append(
            f"| {label} | {m.get('expected_direction', '')} "
            f"| {fmt(m.get('IC_mean'))} | {fmt(m.get('ICIR'))} "
            f"| {fmt(m.get('RankIC_mean'))} | {fmt(m.get('RankICIR'))} "
            f"| {fmt(m.get('quantile_spread_mean'))} | {fmt(m.get('quantile_spread_tstat'))} "
            f"| {fmt(m.get('direction_adjusted_spread'))} | {fmt(m.get('direction_adjusted_tstat'))} "
            f"| {fmt(m.get('turnover'))} | {fmt(m.get('coverage'))} | {m.get('n_timestamps', 0)} |"
        )
    lines += ["", "This is factor evaluation, not strategy PnL.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset-id", default="crypto_top50_usdt_perp_1h", help="Dataset ID under data/cache/ and data/features/")
    p.add_argument("--factor-ids", default=None, help="Comma-separated factor IDs to evaluate")
    p.add_argument("--candidate-csv", default=None, help="Path to candidate CSV for factor selection and direction lookup")
    p.add_argument("--status", default="selected_for_7B", help="Status filter for candidate CSV (default: selected_for_7B)")
    args = p.parse_args()

    dataset = args.dataset_id
    feature = ROOT / "data" / "features" / dataset
    cache = ROOT / "data" / "cache" / dataset
    report = ROOT / "reports" / "artifacts" / "factor_eval" / dataset
    labels_path = feature / "labels.parquet"

    # Determine if explicit/candidate mode
    explicit_mode = bool(args.factor_ids or args.candidate_csv)

    print(f"Evaluate factors (static)")
    print(f"Dataset: {dataset}")

    if not labels_path.exists():
        raise FileNotFoundError("labels.parquet not found; run build_labels.py first")

    # Import REGISTRY for factor lookup
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    from factor_formula_registry import REGISTRY, REGISTRY_BY_ID

    # Determine factor list
    if args.factor_ids:
        factors = [s.strip() for s in args.factor_ids.split(",") if s.strip()]
    elif args.candidate_csv:
        cand_path = Path(args.candidate_csv)
        if not cand_path.exists():
            raise FileNotFoundError(f"Candidate CSV not found: {cand_path}")
        factors = load_selected_factor_ids(cand_path, args.status)
    else:
        # Legacy mode: from old catalog
        if not CATALOG.exists():
            raise FileNotFoundError(CATALOG)
        catalog = pd.read_csv(CATALOG)
        factors = catalog[catalog["implementation_status"] == "IMPLEMENTED"]["factor_id"].tolist()

    # Validate all factors are in REGISTRY
    validate_factor_ids(factors, REGISTRY_BY_ID)

    # Expected count check for selected_for_7B
    if args.candidate_csv and args.status == "selected_for_7B":
        if len(factors) != 27:
            raise ValueError(f"Expected exactly 27 selected_for_7B factors, got {len(factors)}")

    print(f"Factors to evaluate: {len(factors)}")

    # Direction lookup: candidate CSV > old catalog > fallback positive
    candidate_directions: dict[str, str] = {}
    if args.candidate_csv:
        candidate_directions = load_candidate_directions(Path(args.candidate_csv))

    catalog_directions = load_catalog_directions(CATALOG) if CATALOG.exists() else {}

    direction_sources: dict[str, str] = {}
    fallback_factors: list[str] = []

    def get_direction(fid: str) -> tuple[str, str]:
        if fid in candidate_directions:
            return candidate_directions[fid], "candidate_csv"
        if fid in catalog_directions:
            return catalog_directions[fid], "catalog_csv"
        return "positive", "fallback_positive"

    for fid in factors:
        d, src = get_direction(fid)
        direction_sources[fid] = src
        if src == "fallback_positive":
            if explicit_mode:
                raise ValueError(f"Factor '{fid}' has no direction in candidate CSV or catalog; fallback to positive not allowed in explicit mode")
            fallback_factors.append(fid)

    if fallback_factors:
        print(f"WARNING: {len(fallback_factors)} factors using fallback positive direction: {fallback_factors}")

    # Verify all have factor_values
    features_dir = ROOT / "data" / "features" / dataset
    available = []
    missing_fv = []
    for fid in factors:
        fv_path = features_dir / fid / "factor_values.parquet"
        if fv_path.exists():
            available.append(fid)
        else:
            missing_fv.append(fid)

    if missing_fv:
        if explicit_mode:
            raise FileNotFoundError(f"Missing factor_values for explicitly requested factors: {missing_fv}")
        print(f"WARNING: {len(missing_fv)} factors missing factor_values, skipping: {missing_fv}")
    factors = available

    # Compute missing bar rates and exclude gap symbols
    missing_rates = compute_missing_bar_rates(cache / "bars_1h.parquet")
    excluded = get_excluded_symbols(missing_rates)
    if excluded:
        print(f"Excluded symbols (missing_bar_rate > {MISSING_BAR_RATE_THRESHOLD:.0%}): {sorted(excluded)}")
        for sym in sorted(excluded):
            print(f"  {sym}: {missing_rates[sym]:.1%} missing")
    else:
        print("No symbols excluded (all below 5% missing bar threshold)")

    labels = pd.read_parquet(labels_path)
    labels["timestamp"] = pd.to_datetime(labels["timestamp"], utc=True)

    if excluded:
        labels = labels[~labels["symbol"].isin(excluded)]

    period = f"{labels['timestamp'].min()} ~ {labels['timestamp'].max()}"
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    master_rows = []
    summary_rows = []

    for factor in factors:
        fpath = feature / factor / "factor_values.parquet"
        fv = pd.read_parquet(fpath)
        fv["timestamp"] = pd.to_datetime(fv["timestamp"], utc=True)

        if excluded:
            fv = fv[~fv["symbol"].isin(excluded)]

        merged = fv[["timestamp", "symbol", "factor_value"]].merge(labels, on=["timestamp", "symbol"], how="left")
        expected_dir = get_direction(factor)[0]
        label_metrics = {
            label: evaluate_one_label(merged, label, expected_direction=expected_dir)
            for label in LABEL_NAMES
        }
        metrics = {
            "factor_name": factor,
            "universe": dataset,
            "evaluation_period": period,
            "generated_at": generated_at,
            "excluded_symbols": sorted(excluded),
            "missing_bar_threshold": MISSING_BAR_RATE_THRESHOLD,
            "label_metrics": label_metrics,
        }
        outdir = report / factor
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
        write_factor_md(factor, metrics, outdir / "result_summary.md", universe=dataset)

        # Get family from candidate CSV
        family = ""
        if args.candidate_csv:
            with open(args.candidate_csv) as f:
                for row in _csv.DictReader(f):
                    if row["factor_id"] == factor:
                        family = row.get("factor_family", "")
                        break

        for label, m in label_metrics.items():
            master_rows.append((factor, label, m))
            summary_rows.append({
                "factor_id": factor,
                "family": family,
                "label": label,
                "expected_direction": m.get("expected_direction", ""),
                "direction_source": direction_sources.get(factor, ""),
                "IC_mean": m.get("IC_mean", ""),
                "ICIR": m.get("ICIR", ""),
                "RankIC_mean": m.get("RankIC_mean", ""),
                "RankICIR": m.get("RankICIR", ""),
                "quantile_spread_mean": m.get("quantile_spread_mean", ""),
                "direction_adjusted_spread": m.get("direction_adjusted_spread", ""),
                "turnover": m.get("turnover", ""),
                "coverage": m.get("coverage", ""),
                "n_timestamps": m.get("n_timestamps", ""),
                "n_symbols_avg": m.get("n_symbols_avg", ""),
                "n_valid_rows": m.get("n_valid_rows", ""),
            })
        print(f"  {factor} -> {outdir}")

    # Write summary CSV
    if summary_rows:
        summary_df = pd.DataFrame(summary_rows)
        summary_csv_path = report / "factor_eval_static_summary_all_labels.csv"
        summary_df.to_csv(summary_csv_path, index=False)
        print(f"Static eval summary (all labels) -> {summary_csv_path} ({len(summary_df)} rows)")

        # Also write ret_fwd_1h only
        ret_1h_df = summary_df[summary_df["label"] == "ret_fwd_1h"]
        ret_1h_path = report / "factor_eval_static_summary.csv"
        ret_1h_df.to_csv(ret_1h_path, index=False)
        print(f"Static eval summary (ret_fwd_1h) -> {ret_1h_path} ({len(ret_1h_df)} rows)")

    # Write result summary markdown
    suffix = f"_{dataset}" if dataset != "crypto_top50_usdt_perp_1h" else ""
    lines = [
        f"# Crypto Top50 Factor Library — Result Summary {'(' + dataset + ')' if suffix else '(V0.1)'}",
        "",
        f"- universe: `{dataset}`",
        f"- evaluation_period: `{period}`",
        f"- generated_at: `{generated_at}`",
        "- caveat: Static current Top50 diagnostic universe; debug and initial screening only.",
        f"- excluded_symbols (missing_bar_rate > 5%): {sorted(excluded)}",
        f"- timestamp_convention: timestamp = bar_close_time; factor known_at = bar_close_time",
        f"- label_convention: calendar-time forward returns (no row-shift across gaps)",
        "",
        "| factor | label | direction | IC_mean | ICIR | RankIC_mean | RankICIR | raw_spread | raw_spread_t | dir_adj_spread | dir_adj_t | turnover | coverage | n_ts |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for factor, label, m in master_rows:
        lines.append(
            f"| {factor} | {label} | {m.get('expected_direction', '')} "
            f"| {fmt(m.get('IC_mean'))} | {fmt(m.get('ICIR'))} "
            f"| {fmt(m.get('RankIC_mean'))} | {fmt(m.get('RankICIR'))} "
            f"| {fmt(m.get('quantile_spread_mean'))} | {fmt(m.get('quantile_spread_tstat'))} "
            f"| {fmt(m.get('direction_adjusted_spread'))} | {fmt(m.get('direction_adjusted_tstat'))} "
            f"| {fmt(m.get('turnover'))} | {fmt(m.get('coverage'))} | {m.get('n_timestamps', 0)} |"
        )
    lines += ["", "Next: inspect NaN, timestamp alignment, and IC signs before V1.", ""]
    result_path = RUN / f"result_summary{suffix}.md"
    result_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"master summary -> {result_path}")


if __name__ == "__main__":
    main()
