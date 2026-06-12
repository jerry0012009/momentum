#!/usr/bin/env python3
"""Evaluate registered crypto research factors with cross-sectional IC and quintile spread."""
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
REPORT = ROOT / "reports" / "artifacts" / "factor_eval" / UNIVERSE
RUN = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"
LABELS = FEATURE / "labels.parquet"
FACTORS = ["mom_20h", "reversal_5h", "volatility_20h", "rsi_14h", "bb_zscore_20h"]
LABEL_NAMES = ["ret_fwd_1h", "ret_fwd_4h", "ret_fwd_24h", "ret_fwd_72h"]
MIN_N = 10


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


def evaluate_one_label(df: pd.DataFrame, label: str) -> dict[str, Any]:
    total = len(df)
    factor_coverage = clean_float(df["factor_value"].notna().mean()) if total else 0.0
    valid = df[["timestamp", "symbol", "factor_value", label]].dropna()
    ics: list[float] = []
    rics: list[float] = []
    spreads: list[float] = []
    ns: list[float] = []
    top_sets: list[set[str]] = []
    bottom_sets: list[set[str]] = []
    qmeans = {str(i): [] for i in range(1, 6)}

    for _, g in valid.groupby("timestamp", sort=True):
        if len(g) < MIN_N:
            continue
        ic = corr(g["factor_value"], g[label])
        ric = corr(g["factor_value"].rank(), g[label].rank())
        if ic is not None:
            ics.append(ic)
        if ric is not None:
            rics.append(ric)
        try:
            g = g.copy()
            g["q"] = qcut(g["factor_value"])
        except ValueError:
            continue
        qr = g.groupby("q", observed=True)[label].mean()
        for q in range(1, 6):
            if q in qr.index and clean_float(qr.loc[q]) is not None:
                qmeans[str(q)].append(float(qr.loc[q]))
        if 1 in qr.index and 5 in qr.index:
            q1 = clean_float(qr.loc[1])
            q5 = clean_float(qr.loc[5])
            if q1 is not None and q5 is not None:
                spreads.append(q5 - q1)
                bottom_sets.append(set(g.loc[g["q"] == 1, "symbol"]))
                top_sets.append(set(g.loc[g["q"] == 5, "symbol"]))
        ns.append(float(len(g)))

    icm, icsd = avg(ics), std(ics)
    ricm, ricsd = avg(rics), std(rics)
    top_to, bottom_to = turnover(top_sets), turnover(bottom_sets)
    return {
        "label": label,
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
        "quantile_spread_mean": avg(spreads),
        "quantile_spread_tstat": tstat(spreads),
        "quantile_mean_returns": {k: avg(v) for k, v in qmeans.items()},
        "turnover": avg([x for x in [top_to, bottom_to] if x is not None]),
        "top_turnover": top_to,
        "bottom_turnover": bottom_to,
        "n_timestamps": len(ics),
        "n_symbols_avg": avg(ns),
        "n_merged_rows": int(total),
        "n_valid_rows": int(len(valid)),
    }


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
        "",
        "| label | IC_mean | ICIR | RankIC_mean | RankICIR | spread_mean | spread_t | turnover | coverage | n_ts |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for label, m in metrics["label_metrics"].items():
        lines.append(f"| {label} | {fmt(m.get('IC_mean'))} | {fmt(m.get('ICIR'))} | {fmt(m.get('RankIC_mean'))} | {fmt(m.get('RankICIR'))} | {fmt(m.get('quantile_spread_mean'))} | {fmt(m.get('quantile_spread_tstat'))} | {fmt(m.get('turnover'))} | {fmt(m.get('coverage'))} | {m.get('n_timestamps', 0)} |")
    lines += ["", "This is factor evaluation, not strategy PnL.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not LABELS.exists():
        raise FileNotFoundError("labels.parquet not found; run build_labels.py first")
    labels = pd.read_parquet(LABELS)
    labels["timestamp"] = pd.to_datetime(labels["timestamp"], utc=True)
    period = f"{labels['timestamp'].min()} ~ {labels['timestamp'].max()}"
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    master_rows = []

    for factor in FACTORS:
        fpath = FEATURE / factor / "factor_values.parquet"
        if not fpath.exists():
            raise FileNotFoundError(fpath)
        fv = pd.read_parquet(fpath)
        fv["timestamp"] = pd.to_datetime(fv["timestamp"], utc=True)
        merged = fv[["timestamp", "symbol", "factor_value"]].merge(labels, on=["timestamp", "symbol"], how="left")
        label_metrics = {label: evaluate_one_label(merged, label) for label in LABEL_NAMES}
        metrics = {"factor_name": factor, "universe": UNIVERSE, "evaluation_period": period, "generated_at": generated_at, "label_metrics": label_metrics}
        outdir = REPORT / factor
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
        write_factor_md(factor, metrics, outdir / "result_summary.md")
        for label, m in label_metrics.items():
            master_rows.append((factor, label, m))
        print(f"{factor} -> {outdir}")

    RUN.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Crypto Top50 Factor Library — V0 Result Summary",
        "",
        f"- universe: `{UNIVERSE}`",
        f"- evaluation_period: `{period}`",
        f"- generated_at: `{generated_at}`",
        "- caveat: Static current Top50 diagnostic universe; debug and initial screening only.",
        "",
        "| factor | label | IC_mean | ICIR | RankIC_mean | RankICIR | spread_mean | spread_t | turnover | coverage | n_ts |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for factor, label, m in master_rows:
        lines.append(f"| {factor} | {label} | {fmt(m.get('IC_mean'))} | {fmt(m.get('ICIR'))} | {fmt(m.get('RankIC_mean'))} | {fmt(m.get('RankICIR'))} | {fmt(m.get('quantile_spread_mean'))} | {fmt(m.get('quantile_spread_tstat'))} | {fmt(m.get('turnover'))} | {fmt(m.get('coverage'))} | {m.get('n_timestamps', 0)} |")
    lines += ["", "Next: inspect NaN, timestamp alignment, and IC signs before V1.", ""]
    (RUN / "result_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"master summary -> {RUN / 'result_summary.md'}")


if __name__ == "__main__":
    main()
