"""Tests for taxonomy review packet validation rollups."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from build_crypto_industry_taxonomy_review_validation_rollup import (  # noqa: E402
    build_rollup,
    load_validation_rollup_rows,
    write_rollup_reports,
)


def _write_report(path: Path, batch_id: int, *, overall_pass: bool, approved_rows: int) -> Path:
    payload = {
        "generated_at": "2026-06-28T00:00:00+00:00",
        "packet_csv": f"industry_taxonomy_review_batch_{batch_id:03d}.csv",
        "packet_rows": 12,
        "approved_packet_rows": approved_rows,
        "approved_symbols": "AAAUSDT" if approved_rows else "",
        "approved_bar_count_share": 0.10 if approved_rows else 0.0,
        "approved_quote_volume_share": 0.25 if approved_rows else 0.0,
        "allow_no_ok": False,
        "latest_bar_timestamp": "2026-06-13T00:00:00Z",
        "overall_pass": overall_pass,
        "blocker": "" if overall_pass else "packet_has_no_ok_target_rows",
        "checks": [],
    }
    path.write_text(json.dumps(payload) + "\n")
    return path


def test_build_rollup_summarizes_ready_and_blocked_batches(tmp_path: Path):
    _write_report(tmp_path / "industry_taxonomy_review_batch_001_validation.json", 1, overall_pass=False, approved_rows=0)
    _write_report(tmp_path / "industry_taxonomy_review_batch_002_validation.json", 2, overall_pass=True, approved_rows=1)

    rollup = build_rollup(tmp_path)

    summary = rollup["summary"]
    assert summary["batch_report_count"] == 2
    assert summary["ready_to_apply_batch_count"] == 1
    assert summary["blocked_batch_count"] == 1
    assert summary["total_packet_rows"] == 24
    assert summary["total_approved_packet_rows"] == 1
    assert summary["approved_bar_count_share_sum"] == 0.10
    assert summary["approved_quote_volume_share_sum"] == 0.25
    assert summary["ready_to_apply_batch_ids"] == "2"
    assert summary["blocked_batch_ids"] == "1"
    rows = rollup["batches"]
    assert [row["review_batch_id"] for row in rows] == [1, 2]
    assert rows[0]["ready_to_apply"] is False
    assert rows[1]["ready_to_apply"] is True


def test_rollup_marks_invalid_json_as_blocked(tmp_path: Path):
    bad = tmp_path / "industry_taxonomy_review_batch_003_validation.json"
    bad.write_text("{not-json")

    rows = load_validation_rollup_rows([bad])

    assert rows[0]["review_batch_id"] == 3
    assert rows[0]["overall_pass"] is False
    assert rows[0]["ready_to_apply"] is False
    assert rows[0]["blocker"].startswith("validation_report_unreadable:")


def test_write_rollup_reports(tmp_path: Path):
    _write_report(tmp_path / "industry_taxonomy_review_batch_001_validation.json", 1, overall_pass=False, approved_rows=0)
    rollup = build_rollup(tmp_path)

    out_json, out_csv = write_rollup_reports(rollup, tmp_path)

    assert out_json.exists()
    assert out_csv.exists()
    assert out_json.name == "industry_taxonomy_review_batch_validation_rollup.json"
    assert out_csv.name == "industry_taxonomy_review_batch_validation_rollup.csv"
