#!/usr/bin/env python3
"""Build a review-priority list for the crypto industry taxonomy workbook.

This helper ranks symbols by observed quote volume so manual taxonomy review
can start with the symbols that matter most for Alpha101 IndNeutralize coverage.
It does not infer, fill, or validate taxonomy groups, and it does not build the
parquet artifact consumed by factor computation.
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
DEFAULT_SOURCE = ROOT / "data" / "sources" / "crypto_industry_taxonomy_contract_v1" / "symbol_taxonomy.csv"
DEFAULT_OUT_DIR = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_diagnostics"
GROUP_COLUMNS = ["sector", "industry", "subindustry"]

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_crypto_industry_taxonomy_contract import REQUIRED_COLUMNS  # noqa: E402


def _empty_priority_frame() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "review_priority_rank",
            "symbol",
            "quality_flag",
            "bar_count",
            "first_seen",
            "last_seen",
            "quote_volume_sum",
            "quote_volume_share",
            "cumulative_quote_volume_share",
            "missing_sector",
            "missing_industry",
            "missing_subindustry",
            "missing_group_count",
            "review_action",
        ]
    )


def _require_columns(df: pd.DataFrame, required: set[str], name: str) -> None:
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{name} missing required columns: {sorted(missing)}")


def summarize_bars_by_symbol(bars: pd.DataFrame) -> pd.DataFrame:
    """Return per-symbol bars stats used for review prioritization."""
    _require_columns(bars, {"timestamp", "symbol", "quote_volume"}, "bars")
    if bars.empty:
        raise ValueError("bars are empty")

    work = bars[["timestamp", "symbol", "quote_volume"]].copy()
    work["timestamp"] = pd.to_datetime(work["timestamp"], utc=True, errors="coerce")
    work["symbol"] = work["symbol"].astype(str)
    work["quote_volume"] = pd.to_numeric(work["quote_volume"], errors="coerce").fillna(0.0)
    work = work[work["symbol"].str.len() > 0]
    if work.empty:
        raise ValueError("bars have no non-empty symbols")

    return (
        work.groupby("symbol", as_index=False)
        .agg(
            bar_count=("timestamp", "size"),
            first_seen=("timestamp", "min"),
            last_seen=("timestamp", "max"),
            quote_volume_sum=("quote_volume", "sum"),
        )
    )


def build_review_priority(
    taxonomy: pd.DataFrame,
    bars: pd.DataFrame,
    group_columns: list[str] | None = None,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Join taxonomy review rows with bars stats and rank manual review priority."""
    group_columns = group_columns or GROUP_COLUMNS
    _require_columns(taxonomy, REQUIRED_COLUMNS, "taxonomy")
    stats = summarize_bars_by_symbol(bars)

    review = taxonomy.copy().fillna("")
    review["symbol"] = review["symbol"].astype(str)
    merged = review.merge(stats, on="symbol", how="outer", indicator=True)
    merged["quality_flag"] = merged["quality_flag"].fillna("MISSING_FROM_TAXONOMY")
    for col in group_columns:
        if col not in merged.columns:
            merged[col] = ""
        missing_col = f"missing_{col}"
        merged[missing_col] = merged[col].fillna("").astype(str).str.len().eq(0)

    merged["bar_count"] = merged["bar_count"].fillna(0).astype(int)
    merged["quote_volume_sum"] = merged["quote_volume_sum"].fillna(0.0).astype(float)
    total_quote_volume = float(merged["quote_volume_sum"].sum())
    if total_quote_volume > 0:
        merged["quote_volume_share"] = merged["quote_volume_sum"] / total_quote_volume
    else:
        merged["quote_volume_share"] = 0.0

    missing_cols = [f"missing_{col}" for col in group_columns]
    merged["missing_group_count"] = merged[missing_cols].sum(axis=1).astype(int)
    needs_review = (merged["quality_flag"] != "OK") | (merged["missing_group_count"] > 0)
    missing_from_taxonomy = merged["_merge"] == "right_only"
    merged["review_action"] = "already_ok"
    merged.loc[needs_review, "review_action"] = "review_groups"
    merged.loc[missing_from_taxonomy, "review_action"] = "add_taxonomy_row"

    merged = merged.sort_values(
        ["quote_volume_sum", "bar_count", "symbol"],
        ascending=[False, False, True],
        kind="mergesort",
    ).reset_index(drop=True)
    merged["review_priority_rank"] = range(1, len(merged) + 1)
    merged["cumulative_quote_volume_share"] = merged["quote_volume_share"].cumsum()

    for col in ["first_seen", "last_seen"]:
        merged[col] = pd.to_datetime(merged[col], utc=True, errors="coerce").dt.strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        merged[col] = merged[col].fillna("")

    out_cols = _empty_priority_frame().columns.tolist()
    priority = merged[out_cols].copy()
    summary = {
        "row_count": int(len(priority)),
        "taxonomy_rows": int(len(taxonomy)),
        "bar_symbols": int(stats["symbol"].nunique()),
        "symbols_missing_from_taxonomy": int((priority["review_action"] == "add_taxonomy_row").sum()),
        "symbols_needing_review": int((priority["review_action"] != "already_ok").sum()),
        "ok_symbols": int((priority["review_action"] == "already_ok").sum()),
        "quote_volume_sum": total_quote_volume,
        "top_symbol": str(priority.iloc[0]["symbol"]) if len(priority) else "",
        "top_20_quote_volume_share": float(priority.head(20)["quote_volume_share"].sum()) if len(priority) else 0.0,
        "top_50_quote_volume_share": float(priority.head(50)["quote_volume_share"].sum()) if len(priority) else 0.0,
    }
    return priority, summary


def build_priority_from_paths(taxonomy_csv: Path, bars_path: Path) -> tuple[pd.DataFrame, dict[str, object]]:
    if not taxonomy_csv.exists():
        raise FileNotFoundError(f"Taxonomy source CSV not found: {taxonomy_csv}")
    if not bars_path.exists():
        raise FileNotFoundError(f"Bars parquet not found: {bars_path}")

    taxonomy = pd.read_csv(taxonomy_csv)
    bars = pd.read_parquet(bars_path, columns=["timestamp", "symbol", "quote_volume"])
    return build_review_priority(taxonomy, bars)


def write_priority_reports(
    priority: pd.DataFrame,
    summary: dict[str, object],
    out_dir: Path,
    taxonomy_csv: Path,
    bars_path: Path,
) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "taxonomy_csv": str(taxonomy_csv),
        "bars_path": str(bars_path),
        "summary": summary,
        "note": "Review priority only; no taxonomy groups are inferred or filled.",
    }
    out_json = out_dir / "industry_taxonomy_review_priority_status.json"
    out_csv = out_dir / "industry_taxonomy_review_priority.csv"
    out_json.write_text(json.dumps(result, indent=2, default=str) + "\n")
    priority.to_csv(out_csv, index=False)
    return out_json, out_csv


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-csv", default=str(DEFAULT_SOURCE), help="Taxonomy review source CSV")
    parser.add_argument("--bars-path", default=str(DEFAULT_BARS), help="Factor bars parquet path")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Output diagnostics directory")
    args = parser.parse_args()

    taxonomy_csv = Path(args.source_csv)
    bars_path = Path(args.bars_path)
    out_dir = Path(args.out_dir)
    print("Building crypto industry taxonomy review priority")
    print(f"  source_csv: {taxonomy_csv}")
    print(f"  bars:       {bars_path}")

    try:
        priority, summary = build_priority_from_paths(taxonomy_csv, bars_path)
    except Exception as exc:
        print(f"ERROR: {exc}", flush=True)
        return 1

    out_json, out_csv = write_priority_reports(priority, summary, out_dir, taxonomy_csv, bars_path)
    print(f"  rows: {summary['row_count']}")
    print(f"  symbols_needing_review: {summary['symbols_needing_review']}")
    print(f"  top_symbol: {summary['top_symbol']}")
    print(f"  top_20_quote_volume_share: {summary['top_20_quote_volume_share']:.4f}")
    print("  note: no taxonomy groups were inferred or filled")
    print(f"Saved: {out_json}")
    print(f"Saved: {out_csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
