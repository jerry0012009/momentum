"""Phase 7G: validation tests for curated factor library CSVs."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"

BANNED_REGISTRY = {"IMPLEMENTED_ALPHA", "ALPHA", "LIVE", "TRADEABLE", "DEPLOYED"}
BANNED_RESEARCH_USE = {"ALPHA", "TRADEABLE", "DEPLOY", "LIVE", "PORTFOLIO", "SIGNAL_TO_TRADE"}
BANNED_IN_FIELDS = {"alpha", "tradeable", "deploy", "live", "pnl", "portfolio", "signal_to_trade"}


@pytest.fixture(scope="module")
def curated() -> pd.DataFrame:
    p = RUN / "phase7g_curated_factor_library_v0_2.csv"
    if not p.exists():
        pytest.skip("Curated library CSV not found")
    return pd.read_csv(p)


def test_curated_has_27_rows(curated: pd.DataFrame):
    assert len(curated) == 27


def test_no_banned_registry_status(curated: pd.DataFrame):
    bad = set(curated["registry_status"].unique()) & BANNED_REGISTRY
    assert not bad, f"Banned registry_status values: {bad}"


def test_no_banned_research_use(curated: pd.DataFrame):
    bad = set(curated["recommended_research_use"].unique()) & BANNED_RESEARCH_USE
    assert not bad, f"Banned recommended_research_use values: {bad}"


def test_every_factor_has_diagnostic_tier(curated: pd.DataFrame):
    missing = curated[curated["diagnostic_tier"].isna() | (curated["diagnostic_tier"] == "")]
    assert len(missing) == 0, f"Missing diagnostic_tier: {list(missing['factor_id'])}"


def test_every_factor_has_redundancy_role(curated: pd.DataFrame):
    valid_roles = {"NOT_IN_REDUNDANCY_GROUP", "REPRESENTATIVE_CANDIDATE", "REDUNDANT_GROUP_MEMBER"}
    bad = set(curated["redundancy_role"].unique()) - valid_roles
    assert not bad, f"Invalid redundancy_role values: {bad}"


def test_no_forbidden_language_in_string_columns(curated: pd.DataFrame):
    for col in curated.select_dtypes(include="object").columns:
        for val in curated[col].dropna().unique():
            val_lower = str(val).lower()
            for banned in BANNED_IN_FIELDS:
                assert banned not in val_lower, f"Forbidden '{banned}' in {col}: {val}"


def test_family_summary_has_11_families():
    p = RUN / "phase7g_family_curation_summary.csv"
    if not p.exists():
        pytest.skip("Family summary CSV not found")
    df = pd.read_csv(p)
    assert len(df) == 11


def test_redundancy_review_queue_has_6_groups():
    p = RUN / "phase7g_redundancy_review_queue.csv"
    if not p.exists():
        pytest.skip("Redundancy review queue CSV not found")
    df = pd.read_csv(p)
    assert len(df) == 6


def test_redundancy_review_no_drop_or_remove():
    p = RUN / "phase7g_redundancy_review_queue.csv"
    if not p.exists():
        pytest.skip("Redundancy review queue CSV not found")
    df = pd.read_csv(p)
    for val in df["recommended_review"].unique():
        assert "drop" not in str(val).lower()
        assert "remove" not in str(val).lower()
