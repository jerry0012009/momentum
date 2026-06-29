"""Tests for shared public factor manifest lifecycle guards."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from public_factor_manifest_guard import (  # noqa: E402
    find_skipped_public_factor_ids,
    load_skipped_public_factor_ids,
    raise_for_skipped_public_factor_ids,
)


def test_load_skipped_public_factor_ids_from_current_manifest():
    skipped = load_skipped_public_factor_ids()

    assert "wq101_alpha58_indneutralize_skipped" in skipped
    assert "q158_roc_5h_skipped" in skipped
    assert "wq101_alpha56" not in skipped


def test_load_skipped_public_factor_ids_missing_manifest_returns_empty(tmp_path: Path):
    assert load_skipped_public_factor_ids(tmp_path / "missing.csv") == set()


def test_find_skipped_public_factor_ids_preserves_requested_order():
    skipped = {"a_skipped", "c_skipped"}

    assert find_skipped_public_factor_ids(
        ["ok", "c_skipped", "a_skipped"],
        skipped,
    ) == ["c_skipped", "a_skipped"]


def test_raise_for_skipped_public_factor_ids_uses_action_word():
    with pytest.raises(ValueError, match="cannot be evaluated"):
        raise_for_skipped_public_factor_ids(
            ["wq101_alpha58_indneutralize_skipped"],
            action="evaluated",
            skipped_public_factor_ids={"wq101_alpha58_indneutralize_skipped"},
        )
