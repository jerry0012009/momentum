#!/usr/bin/env python3
"""Build a review-priority list for the crypto industry taxonomy workbook.

This helper ranks symbols by observed quote volume so manual taxonomy review
can start with the symbols that matter most for Alpha101 IndNeutralize coverage.
It does not infer, fill, or validate taxonomy groups, and it does not build the
parquet artifact consumed by factor computation.
"""
from __future__ import annotations

import argparse
import math
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_ID = "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1"
DEFAULT_BARS = ROOT / "data" / "cache" / DEFAULT_DATASET_ID / "bars_1h.parquet"
DEFAULT_SOURCE = ROOT / "data" / "sources" / "crypto_industry_taxonomy_contract_v1" / "symbol_taxonomy.csv"
DEFAULT_COINGECKO_MAP = ROOT / "data" / "cache" / "crypto_market_cap_1h_contract_v1" / "symbol_id_map.csv"
DEFAULT_PUBLIC_MANIFEST = ROOT / "docs" / "factor_library" / "public_factor_candidate_manifest.csv"
DEFAULT_OUT_DIR = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_diagnostics"
DEFAULT_COINGECKO_CATEGORY_EVIDENCE = DEFAULT_OUT_DIR / "industry_taxonomy_coingecko_category_evidence.csv"
DEFAULT_REVIEW_BATCH_SIZE = 12
GROUP_COLUMNS = ["sector", "industry", "subindustry"]
SKIPPED_INDUSTRY_STATUS = "skipped_missing_industry_neutralization_20260627"
COINGECKO_COIN_URL = "https://api.coingecko.com/api/v3/coins/{coingecko_id}"
REQUEST_TIMEOUT = 30

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_crypto_industry_taxonomy_contract import REQUIRED_COLUMNS  # noqa: E402


def _empty_priority_frame() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "review_priority_rank",
            "symbol",
            "quality_flag",
            "bar_count",
            "bar_count_share",
            "cumulative_bar_count_share",
            "coverage_gate_98_reached_here",
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
            "coingecko_primary_category",
            "coingecko_categories",
            "coingecko_category_count",
            "coingecko_category_status",
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


def _empty_batch_plan_frame() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "review_batch_id",
            "review_rank_start",
            "review_rank_end",
            "symbol_count",
            "symbols",
            "batch_bar_count",
            "batch_bar_count_share",
            "cumulative_bar_count_share",
            "batch_quote_volume_sum",
            "batch_quote_volume_share",
            "cumulative_quote_volume_share",
            "contains_98pct_bar_gate",
            "review_batch_note",
        ]
    )


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


def _empty_category_evidence_frame() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "coingecko_id",
            "coingecko_symbol",
            "coingecko_name",
            "coingecko_primary_category",
            "coingecko_categories",
            "coingecko_category_count",
            "coingecko_category_status",
            "coingecko_category_source",
            "coingecko_category_fetched_at",
            "coingecko_category_error",
        ]
    )


def load_optional_coingecko_category_evidence(path: Path) -> pd.DataFrame:
    """Load optional CoinGecko category evidence for manual taxonomy review."""
    if not path.exists():
        return _empty_category_evidence_frame()
    df = pd.read_csv(path).fillna("")
    missing = {"coingecko_id"} - set(df.columns)
    if missing:
        raise ValueError(f"coingecko category evidence missing required columns: {sorted(missing)}")
    out = _empty_category_evidence_frame()
    for col in out.columns:
        out[col] = df[col] if col in df.columns else ""
    out["coingecko_id"] = out["coingecko_id"].astype(str)
    return out.drop_duplicates("coingecko_id", keep="last")


def fetch_coingecko_category_evidence(
    coingecko_ids: list[str],
    existing: pd.DataFrame | None = None,
    *,
    force: bool = False,
    delay_seconds: float = 6.5,
    limit: int | None = None,
    requests_get=requests.get,
) -> pd.DataFrame:
    """Fetch CoinGecko categories as review evidence, never as taxonomy approval."""
    existing = existing if existing is not None else _empty_category_evidence_frame()
    if existing.empty:
        existing = _empty_category_evidence_frame()
    existing_ids = set()
    if not force and "coingecko_id" in existing.columns and "coingecko_category_status" in existing.columns:
        ok_existing = existing[existing["coingecko_category_status"].astype(str).eq("OK")]
        existing_ids = set(ok_existing["coingecko_id"].astype(str))

    ids = []
    for coingecko_id in coingecko_ids:
        cid = str(coingecko_id).strip()
        if not cid or cid in existing_ids or cid in ids:
            continue
        ids.append(cid)
    if limit is not None:
        ids = ids[:max(0, int(limit))]

    fetched_rows = []
    for idx, coingecko_id in enumerate(ids, start=1):
        if idx > 1 and delay_seconds > 0:
            time.sleep(delay_seconds)
        fetched_at = datetime.now(timezone.utc).isoformat()
        try:
            resp = requests_get(
                COINGECKO_COIN_URL.format(coingecko_id=coingecko_id),
                params={
                    "localization": "false",
                    "tickers": "false",
                    "market_data": "false",
                    "community_data": "false",
                    "developer_data": "false",
                    "sparkline": "false",
                },
                timeout=REQUEST_TIMEOUT,
            )
            resp.raise_for_status()
            payload = resp.json()
            categories = [str(c).strip() for c in payload.get("categories", []) if str(c).strip()]
            fetched_rows.append({
                "coingecko_id": coingecko_id,
                "coingecko_symbol": str(payload.get("symbol", "")),
                "coingecko_name": str(payload.get("name", "")),
                "coingecko_primary_category": categories[0] if categories else "",
                "coingecko_categories": "|".join(categories),
                "coingecko_category_count": len(categories),
                "coingecko_category_status": "OK",
                "coingecko_category_source": "coingecko_coins_id_categories",
                "coingecko_category_fetched_at": fetched_at,
                "coingecko_category_error": "",
            })
        except Exception as exc:
            fetched_rows.append({
                "coingecko_id": coingecko_id,
                "coingecko_symbol": "",
                "coingecko_name": "",
                "coingecko_primary_category": "",
                "coingecko_categories": "",
                "coingecko_category_count": 0,
                "coingecko_category_status": "ERROR",
                "coingecko_category_source": "coingecko_coins_id_categories",
                "coingecko_category_fetched_at": fetched_at,
                "coingecko_category_error": str(exc),
            })

    fetched = pd.DataFrame(fetched_rows)
    if fetched.empty:
        return existing.copy()
    combined = pd.concat([existing, fetched], ignore_index=True)
    columns = _empty_category_evidence_frame().columns.tolist()
    for col in columns:
        if col not in combined.columns:
            combined[col] = ""
    return combined[columns].drop_duplicates("coingecko_id", keep="last")


def write_coingecko_category_evidence(evidence: pd.DataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if "coingecko_category_status" in evidence.columns:
        evidence = evidence[evidence["coingecko_category_status"].astype(str).eq("OK")].copy()
    evidence.to_csv(path, index=False)
    return path


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


def summarize_ok_review_coverage_preview(
    taxonomy: pd.DataFrame,
    bars: pd.DataFrame,
    group_columns: list[str] | None = None,
    min_full_coverage: float = 0.98,
) -> dict[str, object]:
    """Preview coverage from OK review rows without building an artifact.

    This mirrors the point-in-time eligibility used by factor computation, but
    it is review-only. The parquet artifact and formal coverage gate still have
    to pass before IndNeutralize factors can be unskipped.
    """
    group_columns = group_columns or GROUP_COLUMNS
    _require_columns(taxonomy, REQUIRED_COLUMNS, "taxonomy")
    _require_columns(bars, {"timestamp", "symbol"}, "bars")

    bars_work = bars[["timestamp", "symbol"]].copy()
    bars_work["timestamp"] = pd.to_datetime(bars_work["timestamp"], utc=True, errors="coerce")
    bars_work["symbol"] = bars_work["symbol"].astype(str)
    bars_work["_review_bar_row_id"] = range(len(bars_work))

    bar_rows = int(len(bars_work))
    bar_symbols = int(bars_work["symbol"].nunique())
    threshold_rows = int(math.ceil(bar_rows * min_full_coverage)) if bar_rows else 0

    tax = taxonomy.copy().fillna("")
    tax["symbol"] = tax["symbol"].astype(str)
    for col in ["known_at", "effective_from", "effective_to"]:
        tax[col] = pd.to_datetime(tax[col], utc=True, errors="coerce")
    full_group = tax[group_columns].apply(lambda s: s.astype(str).str.strip().str.len().gt(0)).all(axis=1)
    ok_full = tax[(tax["quality_flag"].astype(str).eq("OK")) & full_group].copy()

    if ok_full.empty or bars_work.empty:
        return {
            "review_ok_full_group_rows": int(len(ok_full)),
            "review_ok_full_group_symbols": int(ok_full["symbol"].nunique()) if "symbol" in ok_full else 0,
            "review_ok_covered_symbols": 0,
            "review_ok_symbol_coverage_rate": 0.0,
            "review_ok_full_group_bar_rows": 0,
            "review_ok_full_group_coverage_rate": 0.0,
            "review_ok_bar_rows_needed_for_98pct": threshold_rows,
            "review_ok_bar_rows_remaining_to_98pct": threshold_rows,
            "review_ok_symbol_coverage_pass_at_98pct": False,
            "review_ok_full_group_coverage_pass_at_98pct": False,
            "review_ok_ready_to_build_artifact_preview": False,
            "review_ok_coverage_note": "Preview only; formal artifact contract and coverage checks are still required.",
        }

    merged = bars_work.merge(ok_full, on="symbol", how="left")
    valid = (
        merged["known_at"].notna()
        & (merged["known_at"] <= merged["timestamp"])
        & merged["effective_from"].notna()
        & (merged["effective_from"] <= merged["timestamp"])
        & (merged["effective_to"].isna() | (merged["timestamp"] < merged["effective_to"]))
    )
    covered = merged.loc[valid, ["_review_bar_row_id", "symbol"]].drop_duplicates("_review_bar_row_id")
    covered_rows = int(len(covered))
    covered_symbols = int(covered["symbol"].nunique()) if covered_rows else 0
    symbol_coverage_rate = covered_symbols / bar_symbols if bar_symbols else 0.0
    full_group_coverage_rate = covered_rows / bar_rows if bar_rows else 0.0
    symbol_pass = symbol_coverage_rate >= min_full_coverage
    full_group_pass = full_group_coverage_rate >= min_full_coverage
    return {
        "review_ok_full_group_rows": int(len(ok_full)),
        "review_ok_full_group_symbols": int(ok_full["symbol"].nunique()),
        "review_ok_covered_symbols": covered_symbols,
        "review_ok_symbol_coverage_rate": float(symbol_coverage_rate),
        "review_ok_full_group_bar_rows": covered_rows,
        "review_ok_full_group_coverage_rate": float(full_group_coverage_rate),
        "review_ok_bar_rows_needed_for_98pct": threshold_rows,
        "review_ok_bar_rows_remaining_to_98pct": max(0, threshold_rows - covered_rows),
        "review_ok_symbol_coverage_pass_at_98pct": bool(symbol_pass),
        "review_ok_full_group_coverage_pass_at_98pct": bool(full_group_pass),
        "review_ok_ready_to_build_artifact_preview": bool(symbol_pass and full_group_pass),
        "review_ok_coverage_note": "Preview only; formal artifact contract and coverage checks are still required.",
    }


def summarize_review_temporal_alignment(
    taxonomy: pd.DataFrame,
    bars: pd.DataFrame,
) -> dict[str, object]:
    """Summarize whether taxonomy known_at can cover the current bars window."""
    _require_columns(taxonomy, {"symbol", "known_at"}, "taxonomy")
    _require_columns(bars, {"timestamp", "symbol"}, "bars")

    bar_ts = pd.to_datetime(bars["timestamp"], utc=True, errors="coerce").dropna()
    tax = taxonomy[["symbol", "known_at"]].copy().fillna("")
    tax["symbol"] = tax["symbol"].astype(str)
    tax["known_at"] = pd.to_datetime(tax["known_at"], utc=True, errors="coerce")

    if bar_ts.empty:
        return {
            "review_source_bar_first_timestamp": "",
            "review_source_bar_last_timestamp": "",
            "taxonomy_known_at_min": "",
            "taxonomy_known_at_max": "",
            "taxonomy_rows_known_by_last_bar": 0,
            "taxonomy_symbols_known_by_last_bar": 0,
            "taxonomy_rows_known_after_last_bar": int(len(tax)),
            "taxonomy_known_at_blocks_current_bars": True,
            "taxonomy_temporal_alignment_note": "Bars timestamps are unavailable; cannot prove point-in-time taxonomy coverage.",
        }

    first_bar = bar_ts.min()
    last_bar = bar_ts.max()
    known = tax["known_at"].notna()
    known_by_last_bar = known & (tax["known_at"] <= last_bar)
    known_after_last_bar = known & (tax["known_at"] > last_bar)
    blocks_current = bool(len(tax) > 0 and not known_by_last_bar.any())
    return {
        "review_source_bar_first_timestamp": first_bar.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "review_source_bar_last_timestamp": last_bar.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "taxonomy_known_at_min": tax.loc[known, "known_at"].min().strftime("%Y-%m-%dT%H:%M:%SZ") if known.any() else "",
        "taxonomy_known_at_max": tax.loc[known, "known_at"].max().strftime("%Y-%m-%dT%H:%M:%SZ") if known.any() else "",
        "taxonomy_rows_known_by_last_bar": int(known_by_last_bar.sum()),
        "taxonomy_symbols_known_by_last_bar": int(tax.loc[known_by_last_bar, "symbol"].nunique()),
        "taxonomy_rows_known_after_last_bar": int(known_after_last_bar.sum()),
        "taxonomy_known_at_blocks_current_bars": blocks_current,
        "taxonomy_temporal_alignment_note": (
            "Current taxonomy known_at is after the latest bar; approved rows would not cover this historical evaluation window."
            if blocks_current
            else "Some taxonomy rows are known by the latest bar; formal point-in-time coverage checks still apply."
        ),
    }


def build_review_batch_plan(priority: pd.DataFrame, batch_size: int = DEFAULT_REVIEW_BATCH_SIZE) -> pd.DataFrame:
    """Chunk review priority rows into manual batches without approving rows."""
    _require_columns(
        priority,
        {
            "review_priority_rank",
            "symbol",
            "bar_count",
            "bar_count_share",
            "quote_volume_sum",
            "quote_volume_share",
            "coverage_gate_98_reached_here",
        },
        "priority",
    )
    if batch_size < 1:
        raise ValueError("batch_size must be >= 1")
    if priority.empty:
        return _empty_batch_plan_frame()

    work = priority.sort_values("review_priority_rank", kind="mergesort").reset_index(drop=True).copy()
    work["review_batch_id"] = (work.index // int(batch_size)) + 1
    work["_cumulative_bar_count_share"] = work["bar_count_share"].cumsum()
    work["_cumulative_quote_volume_share"] = work["quote_volume_share"].cumsum()
    rows = []
    for batch_id, group in work.groupby("review_batch_id", sort=True):
        rows.append({
            "review_batch_id": int(batch_id),
            "review_rank_start": int(group["review_priority_rank"].min()),
            "review_rank_end": int(group["review_priority_rank"].max()),
            "symbol_count": int(len(group)),
            "symbols": "|".join(group["symbol"].astype(str).tolist()),
            "batch_bar_count": int(group["bar_count"].sum()),
            "batch_bar_count_share": float(group["bar_count_share"].sum()),
            "cumulative_bar_count_share": float(group["_cumulative_bar_count_share"].iloc[-1]),
            "batch_quote_volume_sum": float(group["quote_volume_sum"].sum()),
            "batch_quote_volume_share": float(group["quote_volume_share"].sum()),
            "cumulative_quote_volume_share": float(group["_cumulative_quote_volume_share"].iloc[-1]),
            "contains_98pct_bar_gate": bool(group["coverage_gate_98_reached_here"].any()),
            "review_batch_note": "manual_review_only; does_not_approve_or_fill_taxonomy",
        })
    return pd.DataFrame(rows, columns=_empty_batch_plan_frame().columns)


def build_review_priority(
    taxonomy: pd.DataFrame,
    bars: pd.DataFrame,
    group_columns: list[str] | None = None,
    coingecko_map: pd.DataFrame | None = None,
    coingecko_category_evidence: pd.DataFrame | None = None,
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
    if coingecko_category_evidence is not None and not coingecko_category_evidence.empty:
        cat = coingecko_category_evidence.copy().fillna("")
        _require_columns(cat, {"coingecko_id"}, "coingecko_category_evidence")
        keep_cols = [
            "coingecko_id",
            "coingecko_primary_category",
            "coingecko_categories",
            "coingecko_category_count",
            "coingecko_category_status",
        ]
        for col in keep_cols:
            if col not in cat.columns:
                cat[col] = ""
        merged = merged.merge(cat[keep_cols], on="coingecko_id", how="left")
    else:
        merged["coingecko_primary_category"] = ""
        merged["coingecko_categories"] = ""
        merged["coingecko_category_count"] = 0
        merged["coingecko_category_status"] = ""
    for col in ["coingecko_primary_category", "coingecko_categories", "coingecko_category_status"]:
        merged[col] = merged[col].fillna("").astype(str)
    merged["coingecko_category_count"] = pd.to_numeric(
        merged["coingecko_category_count"],
        errors="coerce",
    ).fillna(0).astype(int)

    merged["quality_flag"] = merged["quality_flag"].fillna("MISSING_FROM_TAXONOMY")
    for col in group_columns:
        if col not in merged.columns:
            merged[col] = ""
        missing_col = f"missing_{col}"
        merged[missing_col] = merged[col].fillna("").astype(str).str.len().eq(0)

    merged["bar_count"] = merged["bar_count"].fillna(0).astype(int)
    total_bar_count = int(merged["bar_count"].sum())
    if total_bar_count > 0:
        merged["bar_count_share"] = merged["bar_count"] / total_bar_count
    else:
        merged["bar_count_share"] = 0.0
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
    has_categories = merged["coingecko_category_count"].gt(0)
    merged["review_packet_note"] = (
        "review_only_not_approved; fill sector/industry/subindustry manually before OK"
    )
    merged.loc[~mapped, "review_packet_note"] = (
        "review_only_not_approved; missing coingecko mapping evidence; fill groups manually before OK"
    )
    merged.loc[mapped & ~has_categories, "review_packet_note"] = (
        "review_only_not_approved; mapped coingecko id but no category evidence; fill groups manually before OK"
    )

    merged = merged.sort_values(
        ["quote_volume_sum", "bar_count", "symbol"],
        ascending=[False, False, True],
        kind="mergesort",
    ).reset_index(drop=True)
    merged["review_priority_rank"] = range(1, len(merged) + 1)
    merged["cumulative_bar_count_share"] = merged["bar_count_share"].cumsum()
    merged["coverage_gate_98_reached_here"] = (
        (merged["cumulative_bar_count_share"] >= 0.98)
        & (merged["cumulative_bar_count_share"].shift(fill_value=0.0) < 0.98)
    )
    merged["cumulative_quote_volume_share"] = merged["quote_volume_share"].cumsum()

    for col in ["first_seen", "last_seen"]:
        merged[col] = pd.to_datetime(merged[col], utc=True, errors="coerce").dt.strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        merged[col] = merged[col].fillna("")

    out_cols = _empty_priority_frame().columns.tolist()
    priority = merged[out_cols].copy()
    gate_rows = priority[priority["coverage_gate_98_reached_here"]]
    rank_to_98 = int(gate_rows.iloc[0]["review_priority_rank"]) if len(gate_rows) else 0
    quote_at_98 = float(gate_rows.iloc[0]["cumulative_quote_volume_share"]) if len(gate_rows) else 0.0
    summary = {
        "row_count": int(len(priority)),
        "taxonomy_rows": int(len(taxonomy)),
        "bar_symbols": int(stats["symbol"].nunique()),
        "bar_rows": total_bar_count,
        "symbols_missing_from_taxonomy": int((priority["review_action"] == "add_taxonomy_row").sum()),
        "symbols_needing_review": int((priority["review_action"] != "already_ok").sum()),
        "ok_symbols": int((priority["review_action"] == "already_ok").sum()),
        "symbols_with_coingecko_mapping": int(priority["coingecko_id"].astype(str).str.len().gt(0).sum()),
        "symbols_with_coingecko_categories": int(priority["coingecko_category_count"].gt(0).sum()),
        "blocked_alpha101_indneutralize_factor_count": int(
            blocker_summary.get("blocked_factor_count", 0) or 0
        ),
        "blocked_alpha101_indneutralize_factor_ids": str(blocker_summary.get("blocked_factor_ids", "")),
        "required_taxonomy_groups_for_unblock": str(blocker_summary.get("required_groups", "")),
        "quote_volume_sum": total_quote_volume,
        "top_symbol": str(priority.iloc[0]["symbol"]) if len(priority) else "",
        "top_20_quote_volume_share": float(priority.head(20)["quote_volume_share"].sum()) if len(priority) else 0.0,
        "top_50_quote_volume_share": float(priority.head(50)["quote_volume_share"].sum()) if len(priority) else 0.0,
        "top_20_bar_count_share": float(priority.head(20)["bar_count_share"].sum()) if len(priority) else 0.0,
        "top_50_bar_count_share": float(priority.head(50)["bar_count_share"].sum()) if len(priority) else 0.0,
        "review_priority_rank_to_98pct_bar_coverage": rank_to_98,
        "quote_volume_share_at_98pct_bar_coverage": quote_at_98,
        "coverage_gate_note": "Coverage gate uses bar rows and symbol coverage; quote-volume priority alone is not sufficient.",
    }
    summary.update(summarize_ok_review_coverage_preview(taxonomy, bars, group_columns=group_columns))
    summary.update(summarize_review_temporal_alignment(taxonomy, bars))
    return priority, summary


def build_priority_from_paths(
    taxonomy_csv: Path,
    bars_path: Path,
    coingecko_map_csv: Path = DEFAULT_COINGECKO_MAP,
    coingecko_category_csv: Path = DEFAULT_COINGECKO_CATEGORY_EVIDENCE,
    manifest_csv: Path = DEFAULT_PUBLIC_MANIFEST,
) -> tuple[pd.DataFrame, dict[str, object]]:
    if not taxonomy_csv.exists():
        raise FileNotFoundError(f"Taxonomy source CSV not found: {taxonomy_csv}")
    if not bars_path.exists():
        raise FileNotFoundError(f"Bars parquet not found: {bars_path}")

    taxonomy = pd.read_csv(taxonomy_csv)
    bars = pd.read_parquet(bars_path, columns=["timestamp", "symbol", "quote_volume"])
    coingecko_map = load_optional_coingecko_map(coingecko_map_csv)
    coingecko_category_evidence = load_optional_coingecko_category_evidence(coingecko_category_csv)
    blocker_summary = summarize_indneutralize_blockers(manifest_csv)
    return build_review_priority(
        taxonomy,
        bars,
        coingecko_map=coingecko_map,
        coingecko_category_evidence=coingecko_category_evidence,
        blocker_summary=blocker_summary,
    )


def write_priority_reports(
    priority: pd.DataFrame,
    batch_plan: pd.DataFrame,
    summary: dict[str, object],
    out_dir: Path,
    taxonomy_csv: Path,
    bars_path: Path,
) -> tuple[Path, Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_dir / "industry_taxonomy_review_priority_status.json"
    out_csv = out_dir / "industry_taxonomy_review_priority.csv"
    out_batch_csv = out_dir / "industry_taxonomy_review_batch_plan.csv"
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "taxonomy_csv": str(taxonomy_csv),
        "bars_path": str(bars_path),
        "priority_csv": str(out_csv),
        "batch_plan_csv": str(out_batch_csv),
        "summary": summary,
        "note": "Review priority only; CoinGecko mapping and batch plans are evidence, not approval. No taxonomy groups are inferred or filled.",
    }
    out_json.write_text(json.dumps(result, indent=2, default=str) + "\n")
    priority.to_csv(out_csv, index=False)
    batch_plan.to_csv(out_batch_csv, index=False)
    return out_json, out_csv, out_batch_csv


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-csv", default=str(DEFAULT_SOURCE), help="Taxonomy review source CSV")
    parser.add_argument("--bars-path", default=str(DEFAULT_BARS), help="Factor bars parquet path")
    parser.add_argument("--coingecko-map-csv", default=str(DEFAULT_COINGECKO_MAP), help="Optional symbol->CoinGecko evidence CSV")
    parser.add_argument("--coingecko-category-csv", default=str(DEFAULT_COINGECKO_CATEGORY_EVIDENCE), help="Optional CoinGecko category evidence CSV")
    parser.add_argument("--public-manifest", default=str(DEFAULT_PUBLIC_MANIFEST), help="Public factor manifest for blocked-factor context")
    parser.add_argument("--fetch-coingecko-categories", action="store_true", help="Fetch and cache CoinGecko category evidence before building the review packet")
    parser.add_argument("--category-fetch-delay", type=float, default=6.5, help="Seconds between CoinGecko category requests")
    parser.add_argument("--category-fetch-limit", type=int, default=None, help="Optional max CoinGecko ids to fetch this run")
    parser.add_argument("--force-category-refresh", action="store_true", help="Refetch CoinGecko categories even when cached OK evidence exists")
    parser.add_argument("--review-batch-size", type=int, default=DEFAULT_REVIEW_BATCH_SIZE, help="Manual taxonomy review symbols per batch")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Output diagnostics directory")
    args = parser.parse_args()

    taxonomy_csv = Path(args.source_csv)
    bars_path = Path(args.bars_path)
    out_dir = Path(args.out_dir)
    print("Building crypto industry taxonomy review priority")
    print(f"  source_csv: {taxonomy_csv}")
    print(f"  bars:       {bars_path}")

    try:
        category_csv = Path(args.coingecko_category_csv)
        if args.fetch_coingecko_categories:
            coingecko_map = load_optional_coingecko_map(Path(args.coingecko_map_csv))
            existing_categories = load_optional_coingecko_category_evidence(category_csv)
            taxonomy = pd.read_csv(taxonomy_csv)
            bars = pd.read_parquet(bars_path, columns=["timestamp", "symbol", "quote_volume"])
            blocker_summary = summarize_indneutralize_blockers(Path(args.public_manifest))
            base_priority, _base_summary = build_review_priority(
                taxonomy,
                bars,
                coingecko_map=coingecko_map,
                coingecko_category_evidence=existing_categories,
                blocker_summary=blocker_summary,
            )
            ordered_ids = base_priority["coingecko_id"].dropna().astype(str).tolist()
            category_evidence = fetch_coingecko_category_evidence(
                ordered_ids,
                existing_categories,
                force=args.force_category_refresh,
                delay_seconds=args.category_fetch_delay,
                limit=args.category_fetch_limit,
            )
            write_coingecko_category_evidence(category_evidence, category_csv)
            print(f"  category_evidence_rows: {len(category_evidence)}")
            print(f"Saved category evidence: {category_csv}")
        priority, summary = build_priority_from_paths(
            taxonomy_csv,
            bars_path,
            Path(args.coingecko_map_csv),
            category_csv,
            Path(args.public_manifest),
        )
    except Exception as exc:
        print(f"ERROR: {exc}", flush=True)
        return 1

    try:
        batch_plan = build_review_batch_plan(priority, batch_size=args.review_batch_size)
    except Exception as exc:
        print(f"ERROR: {exc}", flush=True)
        return 1
    summary["review_batch_size"] = int(args.review_batch_size)
    summary["review_batch_count"] = int(len(batch_plan))
    gate_batches = batch_plan[batch_plan["contains_98pct_bar_gate"]] if not batch_plan.empty else pd.DataFrame()
    summary["review_batch_id_to_98pct_bar_coverage"] = int(gate_batches.iloc[0]["review_batch_id"]) if len(gate_batches) else 0

    out_json, out_csv, out_batch_csv = write_priority_reports(
        priority,
        batch_plan,
        summary,
        out_dir,
        taxonomy_csv,
        bars_path,
    )
    print(f"  rows: {summary['row_count']}")
    print(f"  symbols_needing_review: {summary['symbols_needing_review']}")
    print(f"  symbols_with_coingecko_mapping: {summary['symbols_with_coingecko_mapping']}")
    print(f"  symbols_with_coingecko_categories: {summary['symbols_with_coingecko_categories']}")
    print(f"  blocked_indneutralize_factors: {summary['blocked_alpha101_indneutralize_factor_count']}")
    print(f"  top_symbol: {summary['top_symbol']}")
    print(f"  top_20_quote_volume_share: {summary['top_20_quote_volume_share']:.4f}")
    print(f"  top_20_bar_count_share: {summary['top_20_bar_count_share']:.4f}")
    print(f"  rank_to_98pct_bar_coverage: {summary['review_priority_rank_to_98pct_bar_coverage']}")
    print(f"  review_ok_full_group_coverage_rate: {summary['review_ok_full_group_coverage_rate']:.4f}")
    print(f"  review_ok_bar_rows_remaining_to_98pct: {summary['review_ok_bar_rows_remaining_to_98pct']}")
    print(f"  review_batch_size: {summary['review_batch_size']}")
    print(f"  review_batch_count: {summary['review_batch_count']}")
    print(f"  batch_to_98pct_bar_coverage: {summary['review_batch_id_to_98pct_bar_coverage']}")
    print("  note: no taxonomy groups were inferred or filled")
    print(f"Saved: {out_json}")
    print(f"Saved: {out_csv}")
    print(f"Saved: {out_batch_csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
