"""Tests for the crypto industry taxonomy contract checker."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from check_crypto_industry_taxonomy_contract import validate_taxonomy_contract  # noqa: E402


def _valid_taxonomy() -> pd.DataFrame:
    return pd.DataFrame({
        "symbol": ["AAAUSDT", "AAAUSDT", "BBBUSDT", "CCCUSDT"],
        "known_at": pd.to_datetime([
            "2025-12-31 00:00Z",
            "2026-02-01 00:00Z",
            "2025-12-31 00:00Z",
            "2025-12-31 00:00Z",
        ]),
        "effective_from": pd.to_datetime([
            "2026-01-01 00:00Z",
            "2026-02-01 00:00Z",
            "2026-01-01 00:00Z",
            "2026-01-01 00:00Z",
        ]),
        "effective_to": pd.to_datetime([
            "2026-02-01 00:00Z",
            None,
            None,
            None,
        ], utc=True),
        "sector": ["L1", "L1", "L2", None],
        "industry": ["L1a", "L1b", "L2a", None],
        "subindustry": ["L1a1", "L1b1", "L2a1", None],
        "taxonomy_version": ["v1", "v2", "v1", "v1"],
        "source": ["manual_review", "manual_review", "manual_review", "manual_review"],
        "quality_flag": ["OK", "OK", "OK", "REVIEW"],
    })


def _status(checks, name: str) -> bool:
    return next(c for c in checks if c["check"] == name)["passed"]


def test_valid_contract_passes_core_checks():
    checks = validate_taxonomy_contract(_valid_taxonomy())

    assert all(c["passed"] for c in checks), checks


def test_missing_required_column_fails_fast():
    checks = validate_taxonomy_contract(_valid_taxonomy().drop(columns=["known_at"]))

    assert not _status(checks, "required_columns")
    assert len(checks) == 1


def test_bad_quality_flag_fails_domain_check():
    df = _valid_taxonomy()
    df.loc[0, "quality_flag"] = "APPROVED"

    checks = validate_taxonomy_contract(df)

    assert not _status(checks, "quality_flag_domain")


def test_ok_rows_must_have_group_fields():
    df = _valid_taxonomy()
    df.loc[0, "sector"] = None

    checks = validate_taxonomy_contract(df)

    assert not _status(checks, "ok_rows_have_sector")


def test_overlapping_ok_windows_fail():
    df = _valid_taxonomy()
    extra = df.iloc[[0]].copy()
    extra["effective_from"] = pd.Timestamp("2026-01-15 00:00Z")
    extra["effective_to"] = pd.Timestamp("2026-03-01 00:00Z")
    df = pd.concat([df, extra], ignore_index=True)

    checks = validate_taxonomy_contract(df)

    assert not _status(checks, "no_overlapping_ok_effective_windows")


def test_non_ok_rows_do_not_need_group_fields():
    df = _valid_taxonomy()
    df.loc[df["quality_flag"] == "REVIEW", ["sector", "industry", "subindustry"]] = None

    checks = validate_taxonomy_contract(df)

    assert _status(checks, "ok_rows_have_sector")
    assert _status(checks, "ok_rows_have_industry")
    assert _status(checks, "ok_rows_have_subindustry")
