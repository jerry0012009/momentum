#!/usr/bin/env python3
"""Initialize a reviewed taxonomy CSV skeleton from factor bars.

The output is a review workbook, not a valid taxonomy artifact. Rows start with
quality_flag=REVIEW and empty group fields so they cannot be consumed by
build_factor_values.py until manually reviewed and changed to OK.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_ID = "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1"
DEFAULT_BARS = ROOT / "data" / "cache" / DEFAULT_DATASET_ID / "bars_1h.parquet"
DEFAULT_OUTPUT = ROOT / "data" / "sources" / "crypto_industry_taxonomy_contract_v1" / "symbol_taxonomy.csv"
TAXONOMY_COLUMNS = [
    "symbol",
    "known_at",
    "effective_from",
    "effective_to",
    "sector",
    "industry",
    "subindustry",
    "taxonomy_version",
    "source",
    "quality_flag",
]


def initialize_review_taxonomy(
    bars: pd.DataFrame,
    known_at: str,
    taxonomy_version: str,
    source: str,
) -> pd.DataFrame:
    """Build a REVIEW-status taxonomy skeleton from bars."""
    missing = {"timestamp", "symbol"} - set(bars.columns)
    if missing:
        raise ValueError(f"bars missing required columns: {missing}")
    if bars.empty:
        raise ValueError("bars are empty")

    work = bars[["timestamp", "symbol"]].copy()
    work["timestamp"] = pd.to_datetime(work["timestamp"], utc=True, errors="coerce")
    work["symbol"] = work["symbol"].astype(str)
    work = work[work["symbol"].str.len() > 0]
    if work.empty:
        raise ValueError("bars have no non-empty symbols")

    first_seen = (
        work.groupby("symbol", as_index=False)
        .agg(effective_from=("timestamp", "min"))
        .sort_values("symbol")
    )
    out = pd.DataFrame({
        "symbol": first_seen["symbol"],
        "known_at": known_at,
        "effective_from": first_seen["effective_from"].dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "effective_to": "",
        "sector": "",
        "industry": "",
        "subindustry": "",
        "taxonomy_version": taxonomy_version,
        "source": source,
        "quality_flag": "REVIEW",
    })
    return out[TAXONOMY_COLUMNS]


def init_review_csv(
    bars_path: Path,
    output_csv: Path,
    known_at: str,
    taxonomy_version: str,
    source: str,
    overwrite: bool = False,
) -> pd.DataFrame:
    if output_csv.exists() and not overwrite:
        raise FileExistsError(f"Output already exists: {output_csv}. Use --overwrite to replace it.")
    if not bars_path.exists():
        raise FileNotFoundError(f"Bars file not found: {bars_path}")

    bars = pd.read_parquet(bars_path, columns=["timestamp", "symbol"])
    review = initialize_review_taxonomy(bars, known_at, taxonomy_version, source)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    review.to_csv(output_csv, index=False)
    return review


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bars-path", default=str(DEFAULT_BARS), help="Factor bars parquet path")
    parser.add_argument("--output-csv", default=str(DEFAULT_OUTPUT), help="Review CSV output path")
    parser.add_argument("--known-at", required=True, help="UTC timestamp when this review file is known")
    parser.add_argument("--taxonomy-version", required=True, help="Immutable taxonomy version label")
    parser.add_argument("--source", required=True, help="Review source/provenance label")
    parser.add_argument("--overwrite", action="store_true", help="Replace existing output CSV")
    args = parser.parse_args()

    try:
        review = init_review_csv(
            Path(args.bars_path),
            Path(args.output_csv),
            args.known_at,
            args.taxonomy_version,
            args.source,
            args.overwrite,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", flush=True)
        return 1

    print(f"Initialized taxonomy review CSV: {args.output_csv}")
    print(f"Rows: {len(review)}")
    print("All rows start as quality_flag=REVIEW and must be manually reviewed before artifact build.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
