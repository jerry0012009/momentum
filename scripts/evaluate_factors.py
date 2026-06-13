#!/usr/bin/env python3
"""Evaluate registered crypto research factors with cross-sectional IC and quintile spread.

V0 audit improvements:
- Excludes symbols with missing_bar_rate > 5% (gap symbols)
- Adds direction-adjusted spread based on factor catalog's expected_direction
- timestamp = bar_close_time (see build_labels.py)
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
UNIVERSE = "crypto_top50_usdt_perp_1h"
FEATURE = ROOT / "data" / "features" / UNIVERSE
CACHE = ROOT / "data" / "cache" / UNIVERSE
REPORT = ROOT / "reports" / "artifacts" / "factor_eval" / UNIVERSE
RUN = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"
LABELS = FEATURE / "labels.parquet"
CATALOG = RUN / "factor_catalog_v0_1.csv"
LABEL_NAMES = ["ret_fwd_1h", "ret_fwd_4h", "ret_fwd_24h", "ret_fwd_72h"]
MIN_N = 10
MISSING_BAR_RATE_THRESHOLD = 0.05  # exclude symbols with >5% missing bars


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
    """Compute missing_bar_rate per symbol from bars_1h.parquet.

    Returns dict: symbol -> missing_rate (0.0 to 1.0).
    Symbols not in the parquet are treated as 100% missing.
    """
    if bars_path is None:
        bars_path = CACHE / "bars_1h.parquet"
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
    """Return set of symbols exceeding the missing bar rate threshold."""
    return {sym for sym, rate in missing_rates.items() if rate > threshold}


def load_catalog_directions(catalog_path: Path | None = None) -> dict[str, str]:
    """Load expected_direction from factor catalog CSV.

    Returns dict: factor_id -> expected_direction (positive/negative/conditional).
    """
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
    """Vectorized evaluation using pivot tables + numpy quintile assignment.

    Now includes direction-adjusted spread:
    - positive: direction_adjusted_spread = Q5 - Q1
    - negative: direction_adjusted_spread = Q1 - Q5
    - conditional: direction_adjusted_spread = None
    """
    total = len(df)
    factor_coverage = clean_float(df["factor_value"].notna().mean()) if total else 0.0
    valid = df[["timestamp", "symbol", "factor_value", label]].dropna()
    if valid.empty:
        return _empty_metrics(label, factor_coverage, total, expected_direction)

    fv_pivot = valid.pivot_table(index="timestamp", columns="symbol", values="factor_value")
    lb_pivot = valid.pivot_table(index="timestamp", columns="symbol", values=label)
    n_ts = len(fv_pivot)

    # Vectorized IC and RankIC
    ics = fv_pivot.corrwith(lb_pivot, axis=1).dropna().tolist()
    rics = fv_pivot.rank(axis=1).corrwith(lb_pivot.rank(axis=1), axis=1).dropna().tolist()

    # Vectorized quintile spread using numpy
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
            # Direction-adjusted spread
            if expected_direction == "positive":
                dir_adj_spreads.append(raw_spread)  # Q5 - Q1
            elif expected_direction == "negative":
                dir_adj_spreads.append(q1_val - q5_val)  # Q1 - Q5
            # conditional: skip (dir_adj_spreads stays empty or partial)
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


def write_factor_md(factor: str, metrics: dict[str, Any], path: Path) -> None:
    lines = [
        f"# Factor Evaluation: `{factor}`",
        "",
        f"- universe: `{UNIVERSE}`",
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
    if not LABELS.exists():
        raise FileNotFoundError("labels.parquet not found; run build_labels.py first")
    if not CATALOG.exists():
        raise FileNotFoundError(CATALOG)

    catalog = pd.read_csv(CATALOG)
    factors = catalog[catalog["implementation_status"] == "IMPLEMENTED"]["factor_id"].tolist()
    print(f"Catalog: {len(factors)} IMPLEMENTED factors")

    # Load expected directions from catalog
    directions = load_catalog_directions(CATALOG)

    # Compute missing bar rates and exclude gap symbols
    missing_rates = compute_missing_bar_rates()
    excluded = get_excluded_symbols(missing_rates)
    if excluded:
        print(f"Excluded symbols (missing_bar_rate > {MISSING_BAR_RATE_THRESHOLD:.0%}): {sorted(excluded)}")
        for sym in sorted(excluded):
            print(f"  {sym}: {missing_rates[sym]:.1%} missing")
    else:
        print("No symbols excluded (all below 5% missing bar threshold)")

    labels = pd.read_parquet(LABELS)
    labels["timestamp"] = pd.to_datetime(labels["timestamp"], utc=True)

    # Exclude gap symbols from labels
    if excluded:
        labels = labels[~labels["symbol"].isin(excluded)]

    period = f"{labels['timestamp'].min()} ~ {labels['timestamp'].max()}"
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    master_rows = []

    for factor in factors:
        fpath = FEATURE / factor / "factor_values.parquet"
        if not fpath.exists():
            raise FileNotFoundError(fpath)
        fv = pd.read_parquet(fpath)
        fv["timestamp"] = pd.to_datetime(fv["timestamp"], utc=True)

        # Exclude gap symbols from factor values
        if excluded:
            fv = fv[~fv["symbol"].isin(excluded)]

        merged = fv[["timestamp", "symbol", "factor_value"]].merge(labels, on=["timestamp", "symbol"], how="left")
        expected_dir = directions.get(factor, "positive")
        label_metrics = {
            label: evaluate_one_label(merged, label, expected_direction=expected_dir)
            for label in LABEL_NAMES
        }
        metrics = {
            "factor_name": factor,
            "universe": UNIVERSE,
            "evaluation_period": period,
            "generated_at": generated_at,
            "excluded_symbols": sorted(excluded),
            "missing_bar_threshold": MISSING_BAR_RATE_THRESHOLD,
            "label_metrics": label_metrics,
        }
        outdir = REPORT / factor
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
        write_factor_md(factor, metrics, outdir / "result_summary.md")
        for label, m in label_metrics.items():
            master_rows.append((factor, label, m))
        print(f"{factor} -> {outdir}")

    RUN.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Crypto Top50 Factor Library — Batch V0.1 Result Summary",
        "",
        f"- universe: `{UNIVERSE}`",
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
    (RUN / "result_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"master summary -> {RUN / 'result_summary.md'}")


if __name__ == "__main__":
    main()
