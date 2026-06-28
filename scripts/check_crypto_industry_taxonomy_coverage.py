#!/usr/bin/env python3
"""Check point-in-time taxonomy coverage against factor bars.

This is a QA gate for Alpha101 IndNeutralize readiness. It does not register
factors or compute factor_values.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_ID = "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1"
DEFAULT_BARS = ROOT / "data" / "cache" / DEFAULT_DATASET_ID / "bars_1h.parquet"
DEFAULT_TAXONOMY = ROOT / "data" / "cache" / "crypto_industry_taxonomy_contract_v1" / "symbol_taxonomy.parquet"
GROUP_COLUMNS = ["sector", "industry", "subindustry"]

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_factor_values import merge_point_in_time_taxonomy  # noqa: E402


def _coverage_checks(summary: dict[str, object], min_full_coverage: float) -> list[dict[str, object]]:
    return [
        {
            "check": "non_empty_bars",
            "passed": int(summary["bar_rows"]) > 0,
            "detail": f"{summary['bar_rows']} bars",
        },
        {
            "check": "taxonomy_symbol_coverage",
            "passed": float(summary["symbol_coverage_rate"]) >= min_full_coverage,
            "detail": f"{summary['covered_symbols']}/{summary['bar_symbols']} symbols",
        },
        {
            "check": "taxonomy_full_group_coverage",
            "passed": float(summary["full_group_coverage_rate"]) >= min_full_coverage,
            "detail": f"{float(summary['full_group_coverage_rate']):.4f} >= {min_full_coverage:.4f}",
        },
    ]


def summarize_taxonomy_coverage(
    bars: pd.DataFrame,
    taxonomy: pd.DataFrame,
    min_full_coverage: float = 0.98,
) -> tuple[dict[str, object], list[dict[str, object]], pd.DataFrame]:
    """Return coverage summary, checks, and per-symbol coverage."""
    merged = merge_point_in_time_taxonomy(bars, taxonomy)
    full_group = merged[GROUP_COLUMNS].notna().all(axis=1)
    symbol_full = (
        merged.assign(full_group=full_group)
        .groupby("symbol", as_index=False)
        .agg(
            bar_rows=("timestamp", "size"),
            full_group_rows=("full_group", "sum"),
            first_timestamp=("timestamp", "min"),
            last_timestamp=("timestamp", "max"),
        )
    )
    symbol_full["full_group_coverage_rate"] = (
        symbol_full["full_group_rows"] / symbol_full["bar_rows"]
    )
    covered_symbols = int((symbol_full["full_group_coverage_rate"] > 0).sum())
    bar_symbols = int(symbol_full["symbol"].nunique())
    summary = {
        "bar_rows": int(len(merged)),
        "bar_symbols": bar_symbols,
        "covered_symbols": covered_symbols,
        "symbol_coverage_rate": covered_symbols / bar_symbols if bar_symbols else 0.0,
        "full_group_rows": int(full_group.sum()),
        "full_group_coverage_rate": float(full_group.mean()) if len(merged) else 0.0,
        "min_full_coverage": float(min_full_coverage),
    }
    checks = _coverage_checks(summary, min_full_coverage)
    return summary, checks, symbol_full


def check_coverage(
    bars_path: Path = DEFAULT_BARS,
    taxonomy_path: Path = DEFAULT_TAXONOMY,
    min_full_coverage: float = 0.98,
) -> tuple[dict[str, object], list[dict[str, object]], pd.DataFrame]:
    if not bars_path.exists():
        raise FileNotFoundError(f"Bars file not found: {bars_path}")
    if not taxonomy_path.exists():
        raise FileNotFoundError(f"Taxonomy file not found: {taxonomy_path}")

    bars = pd.read_parquet(bars_path)
    taxonomy = pd.read_parquet(taxonomy_path)
    return summarize_taxonomy_coverage(bars, taxonomy, min_full_coverage)


def write_coverage_reports(
    summary: dict[str, object],
    checks: list[dict[str, object]],
    symbol_coverage: pd.DataFrame,
    out_dir: Path,
    bars_path: Path,
    taxonomy_path: Path,
) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "bars_path": str(bars_path),
        "taxonomy_path": str(taxonomy_path),
        "overall_pass": all(bool(c["passed"]) for c in checks),
        "summary": summary,
        "checks": checks,
    }
    out_json = out_dir / "industry_taxonomy_coverage_check.json"
    out_csv = out_dir / "industry_taxonomy_symbol_coverage.csv"
    out_json.write_text(json.dumps(result, indent=2, default=str))
    symbol_coverage.to_csv(out_csv, index=False)
    return out_json, out_csv


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bars-path", default=str(DEFAULT_BARS), help="Factor bars parquet path")
    parser.add_argument("--taxonomy-path", default=str(DEFAULT_TAXONOMY), help="Taxonomy parquet path")
    parser.add_argument("--min-full-coverage", type=float, default=0.98, help="Required full group coverage")
    args = parser.parse_args()

    bars_path = Path(args.bars_path)
    taxonomy_path = Path(args.taxonomy_path)
    print("Checking crypto industry taxonomy coverage")
    print(f"  bars:     {bars_path}")
    print(f"  taxonomy: {taxonomy_path}")

    try:
        summary, checks, symbol_coverage = check_coverage(
            bars_path,
            taxonomy_path,
            args.min_full_coverage,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", flush=True)
        return 1

    for check in checks:
        status = "PASS" if check["passed"] else "FAIL"
        print(f"  {status} {check['check']}: {check['detail']}")
    print(f"Overall: {'PASS' if all(c['passed'] for c in checks) else 'FAIL'}")

    out_json, out_csv = write_coverage_reports(
        summary,
        checks,
        symbol_coverage,
        taxonomy_path.parent,
        bars_path,
        taxonomy_path,
    )
    print(f"Saved: {out_json}")
    print(f"Saved: {out_csv}")
    return 0 if all(bool(c["passed"]) for c in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
