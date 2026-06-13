#!/usr/bin/env python3
"""Phase 6C: Audit dynamic universe data coverage against existing dataset.

Checks whether symbols selected by the dynamic universe are present in the
existing static bars/labels/factor_values dataset, and produces a coverage
report with a go/no-go decision for dynamic universe evaluation.

Usage:
    python scripts/audit_dynamic_universe_data_coverage.py \
        --universe-id crypto_usdt_perp_monthly_volume_top50_current_listed_v1 \
        --dataset-id crypto_top50_usdt_perp_1h_long_v1
"""
from __future__ import annotations

import argparse
import json
from datetime import timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"


def load_universe(universe_id: str) -> pd.DataFrame:
    path = ROOT / "data" / "universe" / universe_id / "universe_snapshots.parquet"
    if not path.exists():
        raise FileNotFoundError(f"universe_snapshots.parquet not found: {path}")
    return pd.read_parquet(path)


def load_bars(dataset_id: str) -> pd.DataFrame:
    path = ROOT / "data" / "cache" / dataset_id / "bars_1h.parquet"
    if not path.exists():
        raise FileNotFoundError(f"bars_1h.parquet not found: {path}")
    return pd.read_parquet(path)


def load_labels(dataset_id: str) -> pd.DataFrame | None:
    path = ROOT / "data" / "features" / dataset_id / "labels.parquet"
    if not path.exists():
        return None
    return pd.read_parquet(path)


def load_factor_symbols(dataset_id: str) -> dict[str, set[str]]:
    """Get symbol sets for each factor in the dataset."""
    features_dir = ROOT / "data" / "features" / dataset_id
    result = {}
    if not features_dir.exists():
        return result
    for d in sorted(features_dir.iterdir()):
        if not d.is_dir():
            continue
        parquet_files = list(d.glob("*.parquet"))
        if not parquet_files:
            continue
        df = pd.read_parquet(parquet_files[0])
        if "symbol" in df.columns:
            result[d.name] = set(df["symbol"].unique())
    return result


def build_monthly_coverage(
    universe_snap: pd.DataFrame,
    bars_symbols: set[str],
) -> pd.DataFrame:
    """For each month, compute coverage against bars dataset."""
    rows = []
    for asof, group in universe_snap.groupby("asof_time"):
        uni_syms = set(group["symbol"])
        intersection = uni_syms & bars_symbols
        missing = uni_syms - bars_symbols
        rows.append({
            "month": pd.Timestamp(asof).strftime("%Y-%m"),
            "asof_time": asof,
            "universe_symbols": len(uni_syms),
            "bars_symbols": len(bars_symbols),
            "intersection": len(intersection),
            "missing_from_bars": len(missing),
            "coverage_rate": len(intersection) / len(uni_syms) if uni_syms else 0.0,
        })
    return pd.DataFrame(rows)


def audit(
    universe_id: str,
    dataset_id: str,
) -> tuple[dict, pd.DataFrame, list[str]]:
    """Run the full coverage audit."""
    # Load data
    snap = load_universe(universe_id)
    bars = load_bars(dataset_id)
    labels = load_labels(dataset_id)
    factor_syms = load_factor_symbols(dataset_id)

    # Symbol sets
    uni_symbols = set(snap["symbol"].unique())
    bars_symbols = set(bars["symbol"].unique()) if "symbol" in bars.columns else set()
    labels_symbols = set(labels["symbol"].unique()) if labels is not None and "symbol" in labels.columns else set()

    # Intersections
    intersection = uni_symbols & bars_symbols
    missing_from_bars = sorted(uni_symbols - bars_symbols)
    missing_from_labels = sorted(uni_symbols - labels_symbols) if labels_symbols else missing_from_bars
    extra_in_bars = sorted(bars_symbols - uni_symbols)

    # Monthly coverage
    monthly = build_monthly_coverage(snap, bars_symbols)

    # Factor coverage
    factor_coverage = {}
    for fname, fsyms in factor_syms.items():
        factor_intersection = uni_symbols & fsyms
        factor_missing = sorted(uni_symbols - fsyms)
        factor_coverage[fname] = {
            "factor_symbols": len(fsyms),
            "intersection": len(factor_intersection),
            "missing": len(factor_missing),
            "coverage_rate": len(factor_intersection) / len(uni_symbols) if uni_symbols else 0.0,
        }

    # Overall coverage rate
    coverage_rate = len(intersection) / len(uni_symbols) if uni_symbols else 0.0

    # Decision
    fully_covered = len(missing_from_bars) == 0
    if fully_covered:
        decision = "ALLOWED"
        decision_text = "Phase 6D: dynamic universe evaluation adapter is ALLOWED."
    else:
        decision = "NOT_ALLOWED"
        decision_text = (
            "Dynamic universe evaluation is NOT YET allowed. "
            "A new dataset must be built for the union of dynamic universe symbols."
        )

    # Build summary
    summary = {
        "universe_id": universe_id,
        "dataset_id": dataset_id,
        "dynamic_universe_months": int(snap["asof_time"].nunique()),
        "dynamic_universe_rows": len(snap),
        "dynamic_universe_unique_symbols": len(uni_symbols),
        "bars_dataset_symbols": len(bars_symbols),
        "labels_dataset_symbols": len(labels_symbols),
        "intersection_symbols": len(intersection),
        "missing_from_bars_count": len(missing_from_bars),
        "missing_from_labels_count": len(missing_from_labels),
        "extra_in_bars_count": len(extra_in_bars),
        "coverage_rate": round(coverage_rate, 6),
        "missing_from_bars": missing_from_bars,
        "extra_in_bars": extra_in_bars,
        "factor_coverage": factor_coverage,
        "decision": decision,
        "decision_text": decision_text,
        "recommendation": (
            "Option B: build a new 1h dataset for the union of dynamic universe selected symbols. "
            "This requires downloading bars_1h for all ~266 symbols, recomputing labels and factor_values."
        ),
        "generated_at": pd.Timestamp.now(timezone.utc).isoformat(),
    }

    return summary, monthly, missing_from_bars


def write_markdown_report(summary: dict, monthly: pd.DataFrame) -> str:
    """Generate markdown report."""
    lines = [
        "# Phase 6C — Dynamic Universe Data Coverage Audit",
        "",
        f"> Generated: {summary['generated_at']}",
        f"> Universe: `{summary['universe_id']}`",
        f"> Dataset: `{summary['dataset_id']}`",
        "",
        "---",
        "",
        "## 1. Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Dynamic universe months | {summary['dynamic_universe_months']} |",
        f"| Dynamic universe unique symbols | {summary['dynamic_universe_unique_symbols']} |",
        f"| Bars dataset symbols | {summary['bars_dataset_symbols']} |",
        f"| Intersection (covered) | {summary['intersection_symbols']} |",
        f"| Missing from bars | {summary['missing_from_bars_count']} |",
        f"| Extra in bars (never in universe) | {summary['extra_in_bars_count']} |",
        f"| **Coverage rate** | **{summary['coverage_rate']:.1%}** |",
        "",
        "## 2. Decision",
        "",
        f"**{summary['decision']}**",
        "",
        summary["decision_text"],
        "",
        "## 3. Recommendation",
        "",
        summary["recommendation"],
        "",
        "## 4. Missing Symbols",
        "",
        f"{summary['missing_from_bars_count']} symbols selected by dynamic universe but absent from bars dataset:",
        "",
    ]

    # Missing symbols table
    missing = summary["missing_from_bars"]
    if missing:
        lines.append("| Symbol |")
        lines.append("|--------|")
        for sym in missing[:50]:
            lines.append(f"| {sym} |")
        if len(missing) > 50:
            lines.append(f"| ... and {len(missing) - 50} more |")
    else:
        lines.append("None — all dynamic universe symbols are present in bars dataset. ✅")

    lines.extend([
        "",
        "## 5. Extra Symbols (in bars but never in universe)",
        "",
        f"{summary['extra_in_bars_count']} symbols in bars dataset but never selected by dynamic universe:",
        "",
    ])

    extra = summary["extra_in_bars"]
    if extra:
        lines.append("| Symbol |")
        lines.append("|--------|")
        for sym in extra:
            lines.append(f"| {sym} |")

    lines.extend([
        "",
        "## 6. Monthly Coverage",
        "",
        "| Month | Universe Symbols | Intersection | Missing | Coverage |",
        "|-------|-----------------|--------------|---------|----------|",
    ])

    for _, row in monthly.iterrows():
        lines.append(
            f"| {row['month']} | {row['universe_symbols']} | {row['intersection']} | "
            f"{row['missing_from_bars']} | {row['coverage_rate']:.1%} |"
        )

    lines.extend([
        "",
        "## 7. Factor Coverage",
        "",
        "| Factor | Factor Symbols | Intersection | Missing | Coverage |",
        "|--------|---------------|--------------|---------|----------|",
    ])

    for fname, fc in summary["factor_coverage"].items():
        lines.append(
            f"| {fname} | {fc['factor_symbols']} | {fc['intersection']} | "
            f"{fc['missing']} | {fc['coverage_rate']:.1%} |"
        )

    lines.extend([
        "",
        "## 8. Next Steps",
        "",
        "### Option A: Evaluate only intersection symbols",
        "- **REJECTED** unless explicitly marked as partial and biased",
        "- Would only evaluate ~43 symbols, missing 84% of dynamic universe",
        "",
        "### Option B: Build new dataset for union of dynamic universe symbols",
        "- **RECOMMENDED**",
        "- Download bars_1h for all ~266 symbols across 25 months",
        "- Recompute labels and factor_values",
        "- Then run evaluation on full dynamic universe",
        "",
        "### Option C: Abandon dynamic universe, keep static top50",
        "- **REJECTED** for Phase 6 purpose",
        "- Static top50 has known survivorship/look-ahead bias",
        "",
        "## 9. Limitations",
        "",
        "- This audit checks symbol presence only, not data quality or completeness",
        "- Missing_bar_rate per symbol not computed here (done in Phase 3)",
        "- Factor coverage assumes same symbol set as bars (true for current pipeline)",
    ])

    return "\n".join(lines) + "\n"


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--universe-id", default="crypto_usdt_perp_monthly_volume_top50_current_listed_v1")
    p.add_argument("--dataset-id", default="crypto_top50_usdt_perp_1h_long_v1")
    args = p.parse_args()

    print(f"Universe: {args.universe_id}")
    print(f"Dataset:  {args.dataset_id}")
    print()

    summary, monthly, missing = audit(args.universe_id, args.dataset_id)

    # Write outputs
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # JSON summary
    json_path = OUTPUT_DIR / "phase6c_dynamic_universe_coverage_summary.json"
    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")

    # Missing symbols CSV
    missing_df = pd.DataFrame({"symbol": missing})
    missing_csv_path = OUTPUT_DIR / "phase6c_dynamic_universe_missing_symbols.csv"
    missing_df.to_csv(missing_csv_path, index=False)

    # Monthly coverage CSV
    monthly_csv_path = OUTPUT_DIR / "phase6c_dynamic_universe_monthly_coverage.csv"
    monthly.to_csv(monthly_csv_path, index=False)

    # Markdown report
    md_path = OUTPUT_DIR / "PHASE_6C_DYNAMIC_UNIVERSE_DATA_COVERAGE.md"
    md_path.write_text(write_markdown_report(summary, monthly), encoding="utf-8")

    # Print summary
    print(f"Dynamic universe symbols: {summary['dynamic_universe_unique_symbols']}")
    print(f"Bars dataset symbols:     {summary['bars_dataset_symbols']}")
    print(f"Intersection:             {summary['intersection_symbols']}")
    print(f"Missing from bars:        {summary['missing_from_bars_count']}")
    print(f"Coverage rate:            {summary['coverage_rate']:.1%}")
    print()
    print(f"Decision: {summary['decision']}")
    print(f"  {summary['decision_text']}")
    print()
    print(f"Outputs:")
    print(f"  {json_path}")
    print(f"  {missing_csv_path}")
    print(f"  {monthly_csv_path}")
    print(f"  {md_path}")


if __name__ == "__main__":
    main()
