"""Phase 7J: Batch-3 planning validation tests."""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
RUN = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"

BANNED_IMPLEMENT = {"CANDIDATE_REVIEW", "ALPHA", "TRADEABLE", "LIVE", "DEPLOY"}
BANNED_PM_REC = {"IMPLEMENT", "SELECTED_FOR_IMPLEMENTATION", "ALPHA", "TRADEABLE", "LIVE", "DEPLOY"}

@pytest.fixture
def fam_gap():
    return pd.read_csv(RUN / "phase7j_family_gap_analysis.csv")

@pytest.fixture
def data_ready():
    return pd.read_csv(RUN / "phase7j_crypto_native_data_readiness.csv")

@pytest.fixture
def batch3():
    return pd.read_csv(RUN / "phase7j_batch3_candidate_plan.csv")

def test_family_gap_exists(fam_gap):
    assert len(fam_gap) >= 13

def test_data_readiness_exists(data_ready):
    assert len(data_ready) >= 10

def test_batch3_candidates_exist(batch3):
    assert len(batch3) >= 10

def test_no_banned_pm_recommendation(batch3):
    for val in batch3["pm_recommendation"]:
        for banned in BANNED_PM_REC:
            assert banned not in str(val).upper(), f"{banned} in pm_recommendation: {val}"

def test_known_at_implies_not_yes(data_ready):
    for _, r in data_ready.iterrows():
        if str(r["known_at_defined"]).upper() == "NO":
            assert str(r["usable_for_phase7k"]).upper() != "YES", \
                f"{r['data_type']}: known_at=NO but usable=YES"

def test_no_registry_modification():
    """Verify factor registry was not modified (still 47 factors)."""
    reg = ROOT / "scripts" / "factor_formula_registry.py"
    content = reg.read_text()
    assert "REGISTRY" in content
    # Count FactorSpec entries
    count = content.count("FactorSpec(")
    assert count == 47, f"Registry has {count} factors, expected 47"
