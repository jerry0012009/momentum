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
DEFAULT_COINGECKO_MAP = ROOT / "data" / "cache" / "crypto_market_cap_1h_contract_v1" / "symbol_id_map.csv"
DEFAULT_PUBLIC_MANIFEST = ROOT / "docs" / "factor_library" / "public_factor_candidate_manifest.csv"
DEFAULT_OUT_DIR = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_diagnostics"
GROUP_COLUMNS = ["sector", "industry", "subindustry"]
SKIPPED_INDUSTRY_STATUS = "skipped_missing_industry_neutralization_20260627"

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
            "coingecko_id",
            "coingecko_map_status",
            "coingecko_map_source",
            "coingecko_mapping_notes",
            "indneutralize_required_groups",
            "blocked_alpha101_factor_count_if_approved",
            "blocked_alpha101_factor_ids",
            "review_packet_note",
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


def load_optional_coingecko_map(path: Path) -> pd.DataFrame:
    """Load symbol->CoinGecko mapping evidence when the cap workflow has built it."""
    columns = ["symbol", "coingecko_id", "map_status", "map_source", "notes"]
    if not path.exists():
        return pd.DataFrame(columns=columns)
    df = pd.read_csv(path)
    missing = {"symbol", "coingecko_id"} - set(df.columns)
    if missing:
        raise ValueError(f"coingecko map missing required columns: {sorted(missing)}")
    for col in columns:
        if col not in df.columns:
            df[col] = ""
    out = df[columns].copy().fillna("")
    out["symbol"] = out["symbol"].astype(str)
    return out.drop_duplicates("symbol", keep="first")


def summarize_indneutralize_blockers(manifest_csv: Path) -> dict[str, object]:
    """Summarize currently skipped Alpha101 IndNeutralize rows for review context."""
    if not manifest_csv.exists():
        return {
            "required_groups": "",
            "blocked_factor_count": 0,
            "blocked_factor_ids": "",
        }
    manifest = pd.read_csv(manifest_csv).fillna("")
    required = {"source_family", "factor_id", "required_columns", "required_ops", "implementation_status"}
    missing = required - set(manifest.columns)
    if missing:
        raise ValueError(f"public manifest missing required columns: {sorted(missing)}")
    rows = manifest[
        (manifest["source_family"] == "alpha101")
        & (manifest["implementation_status"] == SKIPPED_INDUSTRY_STATUS)
        & manifest["required_ops"].astype(str).str.split("|").apply(lambda ops: "indneutralize" in ops)
    ].copy()
    groups = sorted({
        group
        for value in rows["required_columns"].astype(str)
        for group in value.split("|")
        if group in GROUP_COLUMNS
    })
    return {
        "required_groups": "|".join(groups),
        "blocked_factor_count": int(len(rows)),
        "blocked_factor_ids": "|".join(rows["factor_id"].astype(str).tolist()),
    }


def build_review_priority(
    taxonomy: pd.DataFrame,
    bars: pd.DataFrame,
    group_columns: list[str] | None = None,
    coingecko_map: pd.DataFrame | None = None,
    blocker_summary: dict[str, object] | None = None,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Join taxonomy review rows with bars stats and rank manual review priority."""
    group_columns = group_columns or GROUP_COLUMNS
    blocker_summary = blocker_summary or {
        "required_groups": "|".join(group_columns),
        "blocked_factor_count": 0,
        "blocked_factor_ids": "",
    }
    _require_columns(taxonomy, REQUIRED_COLUMNS, "taxonomy")
    stats = summarize_bars_by_symbol(bars)

    review = taxonomy.copy().fillna("")
    review["symbol"] = review["symbol"].astype(str)
    merged = review.merge(stats, on="symbol", how="outer", indicator=True)
    if coingecko_map is not None and not coingecko_map.empty:
        cg = coingecko_map.copy().fillna("")
        _require_columns(cg, {"symbol", "coingecko_id"}, "coingecko_map")
        rename = {
            "map_status": "coingecko_map_status",
            "map_source": "coingecko_map_source",
            "notes": "coingecko_mapping_notes",
        }
        cg = cg.rename(columns=rename)
        for col in ["coingecko_map_status", "coingecko_map_source", "coingecko_mapping_notes"]:
            if col not in cg.columns:
                cg[col] = ""
        merged = merged.merge(
            cg[[
                "symbol",
                "coingecko_id",
                "coingecko_map_status",
                "coingecko_map_source",
                "coingecko_mapping_notes",
            ]],
            on="symbol",
            how="left",
        )
    else:
        merged["coingecko_id"] = ""
        merged["coingecko_map_status"] = ""
        merged["coingecko_map_source"] = ""
        merged["coingecko_mapping_notes"] = ""
    for col in ["coingecko_id", "coingecko_map_status", "coingecko_map_source", "coingecko_mapping_notes"]:
        merged[col] = merged[col].fillna("").astype(str)

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
    merged["indneutralize_required_groups"] = str(blocker_summary.get("required_groups", ""))
    merged["blocked_alpha101_factor_count_if_approved"] = int(
        blocker_summary.get("blocked_factor_count", 0) or 0
    )
    merged["blocked_alpha101_factor_ids"] = str(blocker_summary.get("blocked_factor_ids", ""))
    mapped = merged["coingecko_id"].fillna("").astype(str).str.len().gt(0)
    merged["review_packet_note"] = (
        "review_only_not_approved; fill sector/industry/subindustry manually before OK"
    )
    merged.loc[~mapped, "review_packet_note"] = (
        "review_only_not_approved; missing coingecko mapping evidence; fill groups manually before OK"
    )

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
        "symbols_with_coingecko_mapping": int(priority["coingecko_id"].astype(str).str.len().gt(0).sum()),
        "blocked_alpha101_indneutralize_factor_count": int(
            blocker_summary.get("blocked_factor_count", 0) or 0
        ),
        "blocked_alpha101_indneutralize_factor_ids": str(blocker_summary.get("blocked_factor_ids", "")),
        "required_taxonomy_groups_for_unblock": str(blocker_summary.get("required_groups", "")),
        "quote_volume_sum": total_quote_volume,
        "top_symbol": str(priority.iloc[0]["symbol"]) if len(priority) else "",
        "top_20_quote_volume_share": float(priority.head(20)["quote_volume_share"].sum()) if len(priority) else 0.0,
        "top_50_quote_volume_share": float(priority.head(50)["quote_volume_share"].sum()) if len(priority) else 0.0,
    }
    return priority, summary


def build_priority_from_paths(
    taxonomy_csv: Path,
    bars_path: Path,
    coingecko_map_csv: Path = DEFAULT_COINGECKO_MAP,
    manifest_csv: Path = DEFAULT_PUBLIC_MANIFEST,
) -> tuple[pd.DataFrame, dict[str, object]]:
    if not taxonomy_csv.exists():
        raise FileNotFoundError(f"Taxonomy source CSV not found: {taxonomy_csv}")
    if not bars_path.exists():
        raise FileNotFoundError(f"Bars parquet not found: {bars_path}")

    taxonomy = pd.read_csv(taxonomy_csv)
    bars = pd.read_parquet(bars_path, columns=["timestamp", "symbol", "quote_volume"])
    coingecko_map = load_optional_coingecko_map(coingecko_map_csv)
    blocker_summary = summarize_indneutralize_blockers(manifest_csv)
    return build_review_priority(taxonomy, bars, coingecko_map=coingecko_map, blocker_summary=blocker_summary)


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
        "note": "Review priority only; CoinGecko mapping is evidence, not approval. No taxonomy groups are inferred or filled.",
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
    parser.add_argument("--coingecko-map-csv", default=str(DEFAULT_COINGECKO_MAP), help="Optional symbol->CoinGecko evidence CSV")
    parser.add_argument("--public-manifest", default=str(DEFAULT_PUBLIC_MANIFEST), help="Public factor manifest for blocked-factor context")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Output diagnostics directory")
    args = parser.parse_args()

    taxonomy_csv = Path(args.source_csv)
    bars_path = Path(args.bars_path)
    out_dir = Path(args.out_dir)
    print("Building crypto industry taxonomy review priority")
    print(f"  source_csv: {taxonomy_csv}")
    print(f"  bars:       {bars_path}")

    try:
        priority, summary = build_priority_from_paths(
            taxonomy_csv,
            bars_path,
            Path(args.coingecko_map_csv),
            Path(args.public_manifest),
        )
    except Exception as exc:
        print(f"ERROR: {exc}", flush=True)
        return 1

    out_json, out_csv = write_priority_reports(priority, summary, out_dir, taxonomy_csv, bars_path)
    print(f"  rows: {summary['row_count']}")
    print(f"  symbols_needing_review: {summary['symbols_needing_review']}")
    print(f"  symbols_with_coingecko_mapping: {summary['symbols_with_coingecko_mapping']}")
    print(f"  blocked_indneutralize_factors: {summary['blocked_alpha101_indneutralize_factor_count']}")
    print(f"  top_symbol: {summary['top_symbol']}")
    print(f"  top_20_quote_volume_share: {summary['top_20_quote_volume_share']:.4f}")
    print("  note: no taxonomy groups were inferred or filled")
    print(f"Saved: {out_json}")
    print(f"Saved: {out_csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
