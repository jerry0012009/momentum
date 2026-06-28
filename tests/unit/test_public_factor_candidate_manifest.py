"""Guards for the compact public Alpha101/Alpha158 intake manifest."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from factor_formula_registry import REGISTRY_BY_ID  # noqa: E402

MANIFEST = ROOT / "docs" / "factor_library" / "public_factor_candidate_manifest.csv"
SKIPPED_STATUSES = {
    "skipped_duplicate_20260627",
    "skipped_missing_industry_neutralization_20260627",
}
BACKFILL_STATUSES = {
    "existing_support_backfill_20260627",
    "existing_alpha158_family_backfill_20260627",
    "already_registered",
}

REQUIRED_COLUMNS = [
    "factor_id",
    "source_family",
    "exact_formula",
    "source_reference",
    "required_columns",
    "required_ops",
    "compute_scope",
    "timeframe_mapping",
    "lookback",
    "expected_direction",
    "implementation_status",
    "skip_reason",
]


@pytest.fixture
def rows() -> list[dict[str, str]]:
    with MANIFEST.open(newline="") as handle:
        return list(csv.DictReader(handle))


def test_manifest_schema(rows: list[dict[str, str]]) -> None:
    assert rows
    assert list(rows[0].keys()) == REQUIRED_COLUMNS


def test_public_manifest_registry_and_metadata_parity(rows: list[dict[str, str]]) -> None:
    valid_directions = {"positive", "negative", "conditional"}
    valid_scopes = {"single_symbol", "panel"}

    for row in rows:
        factor_id = row["factor_id"]
        status = row["implementation_status"]
        spec = REGISTRY_BY_ID.get(factor_id)
        assert row["source_family"] in {"alpha101", "alpha158"}
        assert row["compute_scope"] in valid_scopes
        assert row["expected_direction"] in valid_directions
        assert (
            status.startswith("implemented_batch_")
            or status in BACKFILL_STATUSES
            or status in SKIPPED_STATUSES
        ), f"{factor_id} has unknown implementation_status {status}"

        for column in REQUIRED_COLUMNS:
            if column == "skip_reason":
                continue
            assert row[column], f"{factor_id} missing {column}"

        if status in SKIPPED_STATUSES:
            assert factor_id.endswith("_skipped")
            assert spec is None, f"{factor_id} is skipped but exists in registry"
            assert row["skip_reason"], f"{factor_id} skipped without skip_reason"
            continue

        assert not factor_id.endswith("_skipped")
        assert spec is not None, f"{factor_id} missing from registry"
        assert not row["skip_reason"], f"{factor_id} implemented row has skip_reason"
        assert row["lookback"] == str(spec.lookback_window)


def test_public_registry_factors_are_manifested(rows: list[dict[str, str]]) -> None:
    manifest_ids = {row["factor_id"] for row in rows}
    public_registry_ids = {
        factor_id
        for factor_id, spec in REGISTRY_BY_ID.items()
        if (
            factor_id.startswith(("q158_", "a101_", "wq101_"))
            or spec.family.startswith(("alpha158", "alpha101"))
            or spec.family == "wq101"
        )
    }
    assert public_registry_ids <= manifest_ids


def test_public_manifest_counts_and_batch_sizes(rows: list[dict[str, str]]) -> None:
    implemented_counts = {
        family: sum(
            row["source_family"] == family
            and row["implementation_status"] not in SKIPPED_STATUSES
            for row in rows
        )
        for family in {"alpha101", "alpha158"}
    }
    total_counts = {
        family: sum(row["source_family"] == family for row in rows)
        for family in {"alpha101", "alpha158"}
    }
    assert implemented_counts == {"alpha101": 9, "alpha158": 79}
    assert total_counts == {"alpha101": 15, "alpha158": 85}

    batches: dict[str, int] = {}
    for row in rows:
        status = row["implementation_status"]
        if status.startswith("implemented_batch_"):
            batches[status] = batches.get(status, 0) + 1
        elif status in BACKFILL_STATUSES:
            batches[status] = batches.get(status, 0) + 1
        elif status in SKIPPED_STATUSES:
            batches[status] = batches.get(status, 0) + 1

    assert batches
    for batch_id, count in batches.items():
        assert 4 <= count <= 8, f"{batch_id} has {count} factors"
