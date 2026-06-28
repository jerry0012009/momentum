"""Tests for crypto industry taxonomy review-priority reports."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from build_crypto_industry_taxonomy_review_priority import (  # noqa: E402
    build_review_batch_plan,
    build_review_priority,
    fetch_coingecko_category_evidence,
    load_optional_coingecko_map,
    load_optional_coingecko_category_evidence,
    summarize_ok_review_coverage_preview,
    summarize_review_temporal_alignment,
    summarize_indneutralize_blockers,
    summarize_bars_by_symbol,
    write_coingecko_category_evidence,
    write_priority_reports,
)


def _taxonomy() -> pd.DataFrame:
    return pd.DataFrame({
        "symbol": ["AAAUSDT", "BBBUSDT", "CCCUSDT"],
        "known_at": ["2026-06-28T00:00:00Z"] * 3,
        "effective_from": ["2026-01-01T00:00:00Z"] * 3,
        "effective_to": ["", "", ""],
        "sector": ["Layer1", "", "Meme"],
        "industry": ["Layer1", "", "Meme"],
        "subindustry": ["Layer1", "", "Meme"],
        "taxonomy_version": ["reviewed_v1"] * 3,
        "source": ["manual_review"] * 3,
        "quality_flag": ["OK", "REVIEW", "OK"],
    })


def _taxonomy_known_before_bars() -> pd.DataFrame:
    taxonomy = _taxonomy()
    taxonomy["known_at"] = "2025-12-31T00:00:00Z"
    return taxonomy


def _bars() -> pd.DataFrame:
    return pd.DataFrame({
        "timestamp": pd.to_datetime([
            "2026-01-01 00:00Z",
            "2026-01-01 01:00Z",
            "2026-01-01 00:00Z",
            "2026-01-01 00:00Z",
            "2026-01-01 01:00Z",
            "2026-01-01 00:00Z",
        ]),
        "symbol": ["AAAUSDT", "AAAUSDT", "BBBUSDT", "CCCUSDT", "CCCUSDT", "DDDUSDT"],
        "quote_volume": [100.0, 200.0, 500.0, 25.0, 25.0, 175.0],
    })


def test_summarize_bars_by_symbol_uses_quote_volume_and_timestamps():
    stats = summarize_bars_by_symbol(_bars())

    aaa = stats[stats["symbol"] == "AAAUSDT"].iloc[0]
    assert aaa["bar_count"] == 2
    assert aaa["quote_volume_sum"] == 300.0
    assert str(aaa["first_seen"]) == "2026-01-01 00:00:00+00:00"
    assert str(aaa["last_seen"]) == "2026-01-01 01:00:00+00:00"


def test_review_priority_ranks_by_quote_volume_and_marks_actions():
    blocker_summary = {
        "required_groups": "industry|sector|subindustry",
        "blocked_factor_count": 18,
        "blocked_factor_ids": "wq101_alpha58_indneutralize_skipped|wq101_alpha59_indneutralize_skipped",
    }
    coingecko_map = pd.DataFrame({
        "symbol": ["AAAUSDT", "BBBUSDT", "CCCUSDT"],
        "coingecko_id": ["aaa-token", "bbb-token", "ccc-token"],
        "map_status": ["RESOLVED", "CHECK", "RESOLVED"],
        "map_source": ["manual_override", "auto", "auto"],
        "notes": ["reviewed", "ambiguous", ""],
    })
    category_evidence = pd.DataFrame({
        "coingecko_id": ["aaa-token", "bbb-token"],
        "coingecko_primary_category": ["Layer 1 (L1)", "Meme"],
        "coingecko_categories": ["Layer 1 (L1)|Smart Contract Platform", "Meme|AI"],
        "coingecko_category_count": [2, 2],
        "coingecko_category_status": ["OK", "OK"],
    })
    priority, summary = build_review_priority(
        _taxonomy(),
        _bars(),
        coingecko_map=coingecko_map,
        coingecko_category_evidence=category_evidence,
        blocker_summary=blocker_summary,
    )

    assert priority["symbol"].tolist() == ["BBBUSDT", "AAAUSDT", "DDDUSDT", "CCCUSDT"]
    assert priority["review_priority_rank"].tolist() == [1, 2, 3, 4]
    assert priority["bar_count_share"].round(6).tolist() == [
        round(1 / 6, 6),
        round(2 / 6, 6),
        round(1 / 6, 6),
        round(2 / 6, 6),
    ]
    assert priority["cumulative_bar_count_share"].round(6).tolist() == [
        round(1 / 6, 6),
        round(3 / 6, 6),
        round(4 / 6, 6),
        1.0,
    ]
    assert priority["coverage_gate_98_reached_here"].tolist() == [False, False, False, True]
    assert priority.loc[priority["symbol"] == "BBBUSDT", "review_action"].iloc[0] == "review_groups"
    assert priority.loc[priority["symbol"] == "AAAUSDT", "review_action"].iloc[0] == "already_ok"
    assert priority.loc[priority["symbol"] == "DDDUSDT", "review_action"].iloc[0] == "add_taxonomy_row"
    assert priority.loc[priority["symbol"] == "BBBUSDT", "missing_group_count"].iloc[0] == 3
    assert priority.loc[priority["symbol"] == "BBBUSDT", "coingecko_id"].iloc[0] == "bbb-token"
    assert priority.loc[priority["symbol"] == "BBBUSDT", "coingecko_map_status"].iloc[0] == "CHECK"
    assert priority.loc[priority["symbol"] == "BBBUSDT", "coingecko_primary_category"].iloc[0] == "Meme"
    assert priority.loc[priority["symbol"] == "BBBUSDT", "coingecko_category_count"].iloc[0] == 2
    assert priority.loc[priority["symbol"] == "DDDUSDT", "coingecko_id"].iloc[0] == ""
    assert priority.loc[priority["symbol"] == "AAAUSDT", "indneutralize_required_groups"].iloc[0] == "industry|sector|subindustry"
    assert priority.loc[priority["symbol"] == "AAAUSDT", "blocked_alpha101_factor_count_if_approved"].iloc[0] == 18
    assert "wq101_alpha58" in priority.loc[priority["symbol"] == "AAAUSDT", "blocked_alpha101_factor_ids"].iloc[0]
    assert summary["row_count"] == 4
    assert summary["taxonomy_rows"] == 3
    assert summary["bar_symbols"] == 4
    assert summary["bar_rows"] == 6
    assert summary["symbols_missing_from_taxonomy"] == 1
    assert summary["symbols_needing_review"] == 2
    assert summary["symbols_with_coingecko_mapping"] == 3
    assert summary["symbols_with_coingecko_categories"] == 2
    assert summary["blocked_alpha101_indneutralize_factor_count"] == 18
    assert summary["required_taxonomy_groups_for_unblock"] == "industry|sector|subindustry"
    assert summary["top_symbol"] == "BBBUSDT"
    assert summary["quote_volume_sum"] == 1025.0
    assert summary["top_20_bar_count_share"] == 1.0
    assert summary["top_50_bar_count_share"] == 1.0
    assert summary["review_priority_rank_to_98pct_bar_coverage"] == 4
    assert summary["quote_volume_share_at_98pct_bar_coverage"] == 1.0
    assert "bar rows" in summary["coverage_gate_note"]
    assert summary["review_ok_full_group_rows"] == 2
    assert summary["review_ok_full_group_symbols"] == 2
    assert summary["review_ok_covered_symbols"] == 0
    assert summary["review_ok_full_group_bar_rows"] == 0
    assert summary["review_ok_full_group_coverage_rate"] == 0.0
    assert summary["review_ok_bar_rows_needed_for_98pct"] == 6
    assert summary["review_ok_bar_rows_remaining_to_98pct"] == 6
    assert summary["review_ok_ready_to_build_artifact_preview"] is False
    assert summary["taxonomy_known_at_blocks_current_bars"] is True
    assert summary["taxonomy_rows_known_by_last_bar"] == 0
    assert summary["taxonomy_rows_known_after_last_bar"] == 3


def test_review_batch_plan_chunks_priority_without_approval():
    priority, _summary = build_review_priority(_taxonomy(), _bars())

    plan = build_review_batch_plan(priority, batch_size=2)

    assert plan["review_batch_id"].tolist() == [1, 2]
    assert plan["review_rank_start"].tolist() == [1, 3]
    assert plan["review_rank_end"].tolist() == [2, 4]
    assert plan["symbol_count"].tolist() == [2, 2]
    assert plan["symbols"].tolist() == ["BBBUSDT|AAAUSDT", "DDDUSDT|CCCUSDT"]
    assert plan["batch_bar_count"].tolist() == [3, 3]
    assert plan["batch_bar_count_share"].tolist() == pytest.approx([0.5, 0.5])
    assert plan["cumulative_bar_count_share"].tolist() == pytest.approx([0.5, 1.0])
    assert plan["contains_98pct_bar_gate"].tolist() == [False, True]
    assert all("manual_review_only" in note for note in plan["review_batch_note"])


def test_review_batch_plan_rejects_invalid_batch_size():
    priority, _summary = build_review_priority(_taxonomy(), _bars())

    with pytest.raises(ValueError, match="batch_size"):
        build_review_batch_plan(priority, batch_size=0)


def test_ok_review_coverage_preview_counts_only_ok_full_group_rows():
    preview = summarize_ok_review_coverage_preview(_taxonomy_known_before_bars(), _bars())

    assert preview["review_ok_full_group_rows"] == 2
    assert preview["review_ok_covered_symbols"] == 2
    assert preview["review_ok_symbol_coverage_rate"] == pytest.approx(2 / 4)
    assert preview["review_ok_full_group_bar_rows"] == 4
    assert preview["review_ok_full_group_coverage_rate"] == pytest.approx(4 / 6)
    assert preview["review_ok_full_group_coverage_pass_at_98pct"] is False
    assert "Preview only" in preview["review_ok_coverage_note"]


def test_ok_review_coverage_preview_respects_known_at():
    preview = summarize_ok_review_coverage_preview(_taxonomy(), _bars())

    assert preview["review_ok_full_group_rows"] == 2
    assert preview["review_ok_covered_symbols"] == 0
    assert preview["review_ok_full_group_bar_rows"] == 0
    assert preview["review_ok_bar_rows_remaining_to_98pct"] == 6
    assert preview["review_ok_ready_to_build_artifact_preview"] is False


def test_review_temporal_alignment_flags_known_at_after_bars():
    summary = summarize_review_temporal_alignment(_taxonomy(), _bars())

    assert summary["review_source_bar_last_timestamp"] == "2026-01-01T01:00:00Z"
    assert summary["taxonomy_known_at_min"] == "2026-06-28T00:00:00Z"
    assert summary["taxonomy_rows_known_by_last_bar"] == 0
    assert summary["taxonomy_rows_known_after_last_bar"] == 3
    assert summary["taxonomy_known_at_blocks_current_bars"] is True
    assert "after the latest bar" in summary["taxonomy_temporal_alignment_note"]


def test_review_temporal_alignment_passes_when_rows_are_known_by_bars():
    summary = summarize_review_temporal_alignment(_taxonomy_known_before_bars(), _bars())

    assert summary["taxonomy_rows_known_by_last_bar"] == 3
    assert summary["taxonomy_rows_known_after_last_bar"] == 0
    assert summary["taxonomy_known_at_blocks_current_bars"] is False


def test_ok_review_coverage_preview_reports_zero_before_manual_approval():
    taxonomy = _taxonomy()
    taxonomy["quality_flag"] = "REVIEW"

    preview = summarize_ok_review_coverage_preview(taxonomy, _bars())

    assert preview["review_ok_full_group_rows"] == 0
    assert preview["review_ok_covered_symbols"] == 0
    assert preview["review_ok_full_group_bar_rows"] == 0
    assert preview["review_ok_bar_rows_needed_for_98pct"] == 6
    assert preview["review_ok_bar_rows_remaining_to_98pct"] == 6
    assert preview["review_ok_ready_to_build_artifact_preview"] is False


def test_review_priority_does_not_fill_taxonomy_groups():
    priority, _summary = build_review_priority(_taxonomy(), _bars())

    bbb = priority[priority["symbol"] == "BBBUSDT"].iloc[0]
    assert bool(bbb["missing_sector"])
    assert bool(bbb["missing_industry"])
    assert bool(bbb["missing_subindustry"])
    assert pd.isna(bbb.get("sector")) or bbb.get("sector", "") == ""
    assert "review_only_not_approved" in bbb["review_packet_note"]


def test_load_optional_coingecko_map_handles_missing_file(tmp_path: Path):
    result = load_optional_coingecko_map(tmp_path / "missing.csv")

    assert result.empty
    assert {"symbol", "coingecko_id", "map_status", "map_source", "notes"} <= set(result.columns)


def test_load_optional_coingecko_category_evidence_handles_missing_file(tmp_path: Path):
    result = load_optional_coingecko_category_evidence(tmp_path / "missing.csv")

    assert result.empty
    assert {"coingecko_id", "coingecko_categories", "coingecko_category_status"} <= set(result.columns)


def test_fetch_coingecko_category_evidence_uses_cache_and_records_categories():
    class FakeResponse:
        def __init__(self, payload: dict[str, object]):
            self._payload = payload

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, object]:
            return self._payload

    requested: list[str] = []

    def fake_get(url: str, params: dict[str, str], timeout: int) -> FakeResponse:
        requested.append(url.rsplit("/", 1)[-1])
        return FakeResponse({
            "symbol": "bbb",
            "name": "BBB Token",
            "categories": ["Layer 1 (L1)", "Smart Contract Platform"],
        })

    existing = pd.DataFrame({
        "coingecko_id": ["aaa-token"],
        "coingecko_symbol": ["aaa"],
        "coingecko_name": ["AAA Token"],
        "coingecko_primary_category": ["Meme"],
        "coingecko_categories": ["Meme"],
        "coingecko_category_count": [1],
        "coingecko_category_status": ["OK"],
        "coingecko_category_source": ["coingecko_coins_id_categories"],
        "coingecko_category_fetched_at": ["2026-06-28T00:00:00+00:00"],
        "coingecko_category_error": [""],
    })

    result = fetch_coingecko_category_evidence(
        ["aaa-token", "bbb-token"],
        existing,
        delay_seconds=0,
        requests_get=fake_get,
    )

    assert requested == ["bbb-token"]
    bbb = result[result["coingecko_id"] == "bbb-token"].iloc[0]
    assert bbb["coingecko_primary_category"] == "Layer 1 (L1)"
    assert bbb["coingecko_categories"] == "Layer 1 (L1)|Smart Contract Platform"
    assert bbb["coingecko_category_count"] == 2
    assert bbb["coingecko_category_status"] == "OK"


def test_write_coingecko_category_evidence_persists_only_ok_rows(tmp_path: Path):
    evidence = pd.DataFrame({
        "coingecko_id": ["aaa-token", "bbb-token"],
        "coingecko_primary_category": ["Meme", ""],
        "coingecko_categories": ["Meme", ""],
        "coingecko_category_count": [1, 0],
        "coingecko_category_status": ["OK", "ERROR"],
    })

    out = write_coingecko_category_evidence(evidence, tmp_path / "category.csv")
    result = pd.read_csv(out)

    assert result["coingecko_id"].tolist() == ["aaa-token"]


def test_summarize_indneutralize_blockers_from_manifest(tmp_path: Path):
    manifest = tmp_path / "manifest.csv"
    pd.DataFrame([
        {
            "source_family": "alpha101",
            "factor_id": "wq101_alpha58_indneutralize_skipped",
            "required_columns": "vwap|sector",
            "required_ops": "indneutralize|rank",
            "implementation_status": "skipped_missing_industry_neutralization_20260627",
        },
        {
            "source_family": "alpha101",
            "factor_id": "wq101_alpha59_indneutralize_skipped",
            "required_columns": "vwap|industry",
            "required_ops": "indneutralize|rank",
            "implementation_status": "skipped_missing_industry_neutralization_20260627",
        },
        {
            "source_family": "alpha101",
            "factor_id": "wq101_alpha01",
            "required_columns": "close",
            "required_ops": "rank",
            "implementation_status": "implemented_alpha101_ohlcv_batch_01",
        },
    ]).to_csv(manifest, index=False)

    summary = summarize_indneutralize_blockers(manifest)

    assert summary["required_groups"] == "industry|sector"
    assert summary["blocked_factor_count"] == 2
    assert summary["blocked_factor_ids"] == (
        "wq101_alpha58_indneutralize_skipped|wq101_alpha59_indneutralize_skipped"
    )


def test_missing_quote_volume_column_fails():
    bars = _bars().drop(columns=["quote_volume"])

    with pytest.raises(ValueError, match="quote_volume"):
        build_review_priority(_taxonomy(), bars)


def test_priority_reports_are_written(tmp_path: Path):
    priority, summary = build_review_priority(_taxonomy(), _bars())
    batch_plan = build_review_batch_plan(priority, batch_size=2)

    out_json, out_csv, out_batch_csv = write_priority_reports(
        priority,
        batch_plan,
        summary,
        tmp_path / "out",
        tmp_path / "symbol_taxonomy.csv",
        tmp_path / "bars.parquet",
    )

    assert out_json.exists()
    assert out_csv.exists()
    assert out_batch_csv.exists()
    status = out_json.read_text()
    assert "No taxonomy groups are inferred" in status
    assert "industry_taxonomy_review_batch_plan.csv" in status
