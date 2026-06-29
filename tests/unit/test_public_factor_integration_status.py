"""Tests for public Alpha101/Alpha158 integration status reporting."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from check_public_factor_integration_status import (  # noqa: E402
    OUT_DIR,
    build_status_report,
    mark_skipped_rows_ready,
    summarize_taxonomy_packet_rollup,
    write_status_report,
)


def _family(report: dict[str, object], name: str) -> dict[str, object]:
    return next(row for row in report["family_summary"] if row["source_family"] == name)


def test_public_factor_integration_status_matches_current_manifest_and_state():
    report = build_status_report()

    assert report["state"] == {
        "registered_factors": 249,
        "computed_factor_values": 249,
        "missing_factor_values": 0,
        "missing_input_factors": 0,
    }

    alpha101 = _family(report, "alpha101")
    assert alpha101["manifest_total"] == 107
    assert alpha101["accounted_non_skipped"] == 88
    assert alpha101["skipped"] == 19
    assert alpha101["registry_missing_non_skipped"] == 0
    assert alpha101["skipped_present_in_registry"] == 0

    alpha158 = _family(report, "alpha158")
    assert alpha158["manifest_total"] == 101
    assert alpha158["accounted_non_skipped"] == 95
    assert alpha158["skipped"] == 6
    assert alpha158["registry_missing_non_skipped"] == 0
    assert alpha158["skipped_present_in_registry"] == 0

    skipped_ids = {row["factor_id"] for row in report["skipped_rows"]}
    assert "wq101_alpha58_indneutralize_skipped" in skipped_ids
    assert "wq101_alpha56_cap_skipped" not in skipped_ids
    assert "q158_roc_5h_skipped" in skipped_ids
    cap_blocked = [
        row for row in report["skipped_rows"]
        if row["source_family"] == "alpha101" and row["cap_blocker"]
    ]
    assert cap_blocked == []
    alpha101_taxonomy_blocked = [
        row for row in report["skipped_rows"]
        if row["source_family"] == "alpha101" and row["taxonomy_blocker"]
    ]
    assert len(alpha101_taxonomy_blocked) == 18
    assert all(row["ready_for_unskip"] is False for row in alpha101_taxonomy_blocked)
    required_by_id = {
        row["factor_id"]: row["taxonomy_required_groups"]
        for row in alpha101_taxonomy_blocked
    }
    assert required_by_id["wq101_alpha58_indneutralize_skipped"] == "sector"
    assert required_by_id["wq101_alpha59_indneutralize_skipped"] == "industry"
    assert required_by_id["wq101_alpha67_indneutralize_skipped"] == "sector|subindustry"
    assert required_by_id["wq101_alpha48_indneutralize_skipped"] == "subindustry"

    taxonomy = report["taxonomy_readiness"]
    rollup_summary = json.loads((OUT_DIR / "industry_taxonomy_review_batch_validation_rollup.json").read_text())["summary"]
    coverage_summary = json.loads((OUT_DIR / "industry_taxonomy_review_packet_coverage.json").read_text())
    assert taxonomy["source_exists"] is True
    assert taxonomy["source_rows"] == 266
    assert taxonomy["source_quality_counts"] == {"REVIEW": 266}
    assert taxonomy["source_ok_row_count"] == 0
    assert taxonomy["source_ready_to_build_artifact"] is False
    assert taxonomy["source_missing_required_ok_groups"] == "industry|sector|subindustry"
    assert taxonomy["source_bar_last_timestamp"] == "2026-06-13T00:00:00Z"
    assert taxonomy["source_ok_rows_known_by_last_bar"] == 0
    assert taxonomy["source_ok_symbols_known_by_last_bar"] == 0
    assert taxonomy["source_ok_rows_known_after_last_bar"] == 0
    assert taxonomy["source_ok_known_at_blocks_bars"] is False
    assert taxonomy["packet_validation_exists"] is True
    assert taxonomy["packet_validation_pass"] is False
    assert taxonomy["packet_validation_blocker"] == "packet_has_no_ok_target_rows"
    assert taxonomy["packet_rows"] == 12
    assert taxonomy["packet_approved_rows"] == 0
    assert taxonomy["packet_approved_symbols"] == ""
    assert taxonomy["packet_approved_bar_count_share"] == 0.0
    assert taxonomy["packet_approved_quote_volume_share"] == 0.0
    assert taxonomy["packet_latest_bar_timestamp"] == "2026-06-13T00:00:00Z"
    assert taxonomy["packet_allow_no_ok"] is False
    assert taxonomy["packet_rollup_exists"] is True
    assert taxonomy["packet_rollup_blocker"] == ""
    assert taxonomy["packet_rollup_batch_count"] == rollup_summary["batch_report_count"]
    assert taxonomy["packet_rollup_ready_to_apply_batch_count"] == rollup_summary["ready_to_apply_batch_count"]
    assert taxonomy["packet_rollup_blocked_batch_count"] == rollup_summary["blocked_batch_count"]
    assert taxonomy["packet_rollup_total_packet_rows"] == rollup_summary["total_packet_rows"]
    assert taxonomy["packet_rollup_total_approved_rows"] == rollup_summary["total_approved_packet_rows"]
    assert taxonomy["packet_rollup_approved_bar_count_share_sum"] == rollup_summary["approved_bar_count_share_sum"]
    assert taxonomy["packet_rollup_approved_quote_volume_share_sum"] == rollup_summary["approved_quote_volume_share_sum"]
    assert taxonomy["packet_rollup_ready_to_apply_batch_ids"] == rollup_summary["ready_to_apply_batch_ids"]
    assert taxonomy["packet_rollup_blocked_batch_ids"] == rollup_summary["blocked_batch_ids"]
    assert taxonomy["reviewed_packet_rollup_exists"] is False
    assert taxonomy["reviewed_packet_rollup_blocker"] == "reviewed_packet_rollup_missing"
    assert taxonomy["reviewed_packet_rollup_batch_count"] == 0
    assert taxonomy["reviewed_packet_rollup_ready_to_apply_batch_count"] == 0
    assert taxonomy["reviewed_packet_rollup_blocked_batch_count"] == 0
    assert taxonomy["reviewed_packet_rollup_total_packet_rows"] == 0
    assert taxonomy["reviewed_packet_rollup_total_approved_rows"] == 0
    assert taxonomy["reviewed_packet_rollup_ready_to_apply_batch_ids"] == ""
    assert taxonomy["reviewed_packet_rollup_blocked_batch_ids"] == ""
    assert taxonomy["packet_coverage_exists"] is True
    assert taxonomy["packet_coverage_pass"] is True
    assert taxonomy["packet_coverage_blocker"] == ""
    assert taxonomy["packet_coverage_candidate_file_count"] == coverage_summary["candidate_file_count"]
    assert taxonomy["packet_coverage_file_count"] == coverage_summary["packet_file_count"]
    assert taxonomy["packet_coverage_source_rows"] == coverage_summary["source_rows"]
    assert taxonomy["packet_coverage_rows"] == coverage_summary["packet_rows"]
    assert taxonomy["packet_coverage_unique_symbols"] == coverage_summary["unique_packet_symbols"]
    assert taxonomy["packet_coverage_missing_source_symbols"] == ""
    assert taxonomy["packet_coverage_extra_symbols"] == ""
    assert taxonomy["packet_coverage_duplicate_symbols"] == ""
    assert taxonomy["artifact_exists"] is False
    assert taxonomy["contract_pass"] is False
    assert taxonomy["coverage_pass"] is False
    assert taxonomy["ready_for_indneutralize_unskip"] is False
    assert taxonomy["blocker"] == "taxonomy_review_has_no_ok_rows"
    assert taxonomy["blocked_alpha101_factor_count"] == 18
    assert taxonomy["required_taxonomy_groups"] == "industry|sector|subindustry"
    group_readiness = {
        row["taxonomy_group"]: row
        for row in taxonomy["taxonomy_group_readiness"]
    }
    assert set(group_readiness) == {"industry", "sector", "subindustry"}
    assert group_readiness["industry"]["ready"] is False
    assert group_readiness["industry"]["blocker"] == "taxonomy_review_missing_ok_industry"
    assert group_readiness["industry"]["blocked_alpha101_factor_count"] == 10
    assert "wq101_alpha59_indneutralize_skipped" in group_readiness["industry"]["blocked_alpha101_factor_ids"]
    assert group_readiness["sector"]["ready"] is False
    assert group_readiness["sector"]["blocker"] == "taxonomy_review_missing_ok_sector"
    assert group_readiness["sector"]["blocked_alpha101_factor_count"] == 5
    assert "wq101_alpha58_indneutralize_skipped" in group_readiness["sector"]["blocked_alpha101_factor_ids"]
    assert group_readiness["subindustry"]["ready"] is False
    assert group_readiness["subindustry"]["blocker"] == "taxonomy_review_missing_ok_subindustry"
    assert group_readiness["subindustry"]["blocked_alpha101_factor_count"] == 4
    assert "wq101_alpha48_indneutralize_skipped" in group_readiness["subindustry"]["blocked_alpha101_factor_ids"]

    cap = report["cap_readiness"]
    assert cap["artifact_exists"] is True
    assert cap["contract_check_exists"] is True
    assert cap["contract_pass"] is True
    assert cap["ready_for_cap_unskip"] is True
    assert cap["blocker"] == ""
    assert cap["overall_coverage"] == "90.2% (PASS)"
    assert cap["symbol_coverage_summary"] == "237 symbols >= 90%, 29 symbols < 80%"
    assert cap["low_coverage_symbol_count"] == 28
    assert "EDUUSDT" in cap["low_coverage_symbols"]
    assert cap["blocked_alpha101_factor_count"] == 0
    assert cap["blocked_alpha101_factor_ids"] == ""


def test_public_factor_integration_status_writes_reports(tmp_path: Path):
    report = build_status_report()

    out_json, out_summary, out_skipped = write_status_report(report, tmp_path)

    assert out_json.exists()
    assert out_summary.exists()
    assert out_skipped.exists()


def test_taxonomy_packet_rollup_supports_reviewed_prefix(tmp_path: Path):
    rollup_path = tmp_path / "industry_taxonomy_review_batch_validation_rollup.json"
    rollup_path.write_text(json.dumps({
        "summary": {
            "batch_report_count": 2,
            "ready_to_apply_batch_count": 1,
            "blocked_batch_count": 1,
            "total_packet_rows": 20,
            "total_approved_packet_rows": 8,
            "approved_bar_count_share_sum": 0.25,
            "approved_quote_volume_share_sum": 0.3,
            "ready_to_apply_batch_ids": "1",
            "blocked_batch_ids": "2",
        },
        "batches": [],
    }))

    summary = summarize_taxonomy_packet_rollup(
        rollup_path,
        prefix="reviewed_packet_rollup",
    )

    assert summary == {
        "reviewed_packet_rollup_path": str(rollup_path),
        "reviewed_packet_rollup_exists": True,
        "reviewed_packet_rollup_blocker": "",
        "reviewed_packet_rollup_batch_count": 2,
        "reviewed_packet_rollup_ready_to_apply_batch_count": 1,
        "reviewed_packet_rollup_blocked_batch_count": 1,
        "reviewed_packet_rollup_total_packet_rows": 20,
        "reviewed_packet_rollup_total_approved_rows": 8,
        "reviewed_packet_rollup_approved_bar_count_share_sum": 0.25,
        "reviewed_packet_rollup_approved_quote_volume_share_sum": 0.3,
        "reviewed_packet_rollup_ready_to_apply_batch_ids": "1",
        "reviewed_packet_rollup_blocked_batch_ids": "2",
    }


def test_mark_skipped_rows_ready_uses_required_gate_statuses():
    rows = [
        {"factor_id": "tax", "taxonomy_blocker": True, "cap_blocker": False, "ready_for_unskip": False},
        {"factor_id": "cap", "taxonomy_blocker": False, "cap_blocker": True, "ready_for_unskip": False},
        {"factor_id": "both", "taxonomy_blocker": True, "cap_blocker": True, "ready_for_unskip": False},
        {"factor_id": "other", "taxonomy_blocker": False, "cap_blocker": False, "ready_for_unskip": False},
    ]

    marked = mark_skipped_rows_ready(
        rows,
        taxonomy_readiness={"ready_for_indneutralize_unskip": True},
        cap_readiness={"ready_for_cap_unskip": False},
    )
    ready_by_id = {row["factor_id"]: row["ready_for_unskip"] for row in marked}

    assert ready_by_id == {
        "tax": True,
        "cap": False,
        "both": False,
        "other": False,
    }

    marked = mark_skipped_rows_ready(
        rows,
        taxonomy_readiness={"ready_for_indneutralize_unskip": True},
        cap_readiness={"ready_for_cap_unskip": True},
    )
    ready_by_id = {row["factor_id"]: row["ready_for_unskip"] for row in marked}

    assert ready_by_id == {
        "tax": True,
        "cap": True,
        "both": True,
        "other": False,
    }


def test_committed_public_factor_integration_status_is_current():
    current = build_status_report()
    committed = json.loads((OUT_DIR / "public_factor_integration_status.json").read_text())

    for key in ["state", "family_summary", "skipped_rows", "taxonomy_readiness", "cap_readiness"]:
        assert committed[key] == current[key]
