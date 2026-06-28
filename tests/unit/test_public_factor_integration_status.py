"""Tests for public Alpha101/Alpha158 integration status reporting."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from check_public_factor_integration_status import (  # noqa: E402
    OUT_DIR,
    build_status_report,
    write_status_report,
)


def _family(report: dict[str, object], name: str) -> dict[str, object]:
    return next(row for row in report["family_summary"] if row["source_family"] == name)


def test_public_factor_integration_status_matches_current_manifest_and_state():
    report = build_status_report()

    assert report["state"] == {
        "registered_factors": 198,
        "computed_factor_values": 198,
        "missing_factor_values": 0,
        "missing_input_factors": 0,
    }

    alpha101 = _family(report, "alpha101")
    assert alpha101["manifest_total"] == 43
    assert alpha101["accounted_non_skipped"] == 37
    assert alpha101["skipped"] == 6
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
    assert "q158_roc_5h_skipped" in skipped_ids
    alpha101_taxonomy_blocked = [
        row for row in report["skipped_rows"]
        if row["source_family"] == "alpha101" and row["taxonomy_blocker"]
    ]
    assert len(alpha101_taxonomy_blocked) == 6
    assert all(row["ready_for_unskip"] is False for row in alpha101_taxonomy_blocked)
    required_by_id = {
        row["factor_id"]: row["taxonomy_required_groups"]
        for row in alpha101_taxonomy_blocked
    }
    assert required_by_id["wq101_alpha58_indneutralize_skipped"] == "sector"
    assert required_by_id["wq101_alpha59_indneutralize_skipped"] == "industry"
    assert required_by_id["wq101_alpha67_indneutralize_skipped"] == "sector|subindustry"

    taxonomy = report["taxonomy_readiness"]
    assert taxonomy["source_exists"] is True
    assert taxonomy["source_rows"] == 266
    assert taxonomy["source_quality_counts"] == {"REVIEW": 266}
    assert taxonomy["source_ok_row_count"] == 0
    assert taxonomy["source_ready_to_build_artifact"] is False
    assert taxonomy["source_missing_required_ok_groups"] == "industry|sector|subindustry"
    assert taxonomy["artifact_exists"] is False
    assert taxonomy["contract_pass"] is False
    assert taxonomy["coverage_pass"] is False
    assert taxonomy["ready_for_indneutralize_unskip"] is False
    assert taxonomy["blocker"] == "taxonomy_review_has_no_ok_rows"
    assert taxonomy["blocked_alpha101_factor_count"] == 6
    assert taxonomy["required_taxonomy_groups"] == "industry|sector|subindustry"


def test_public_factor_integration_status_writes_reports(tmp_path: Path):
    report = build_status_report()

    out_json, out_summary, out_skipped = write_status_report(report, tmp_path)

    assert out_json.exists()
    assert out_summary.exists()
    assert out_skipped.exists()


def test_committed_public_factor_integration_status_is_current():
    current = build_status_report()
    committed = json.loads((OUT_DIR / "public_factor_integration_status.json").read_text())

    for key in ["state", "family_summary", "skipped_rows", "taxonomy_readiness"]:
        assert committed[key] == current[key]
