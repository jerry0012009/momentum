"""Phase 7K: data contract validation tests."""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
RUN = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"

BANNED = {"CANDIDATE_REVIEW", "ALPHA", "TRADEABLE", "LIVE", "DEPLOY"}
VALID_READINESS_BARS = {"READY", "PARTIAL", "MISSING_REQUIRED_FIELDS", "FILE_NOT_FOUND", "ERROR"}
VALID_READINESS_TAKER = {"READY_AS_DEFINED", "READY_WITH_QUOTE_VOLUME_VARIANT", "NEEDS_SCHEMA_FIX", "NOT_READY"}
VALID_READINESS_FR = {"READY_FOR_CONTRACT", "NEEDS_DATA_CONTRACT", "NEEDS_INGESTION", "NOT_FOUND", "ERROR"}

@pytest.fixture
def bars_audit():
    return pd.read_csv(RUN / "phase7k_bars_schema_audit.csv")

@pytest.fixture
def taker_ready():
    return pd.read_csv(RUN / "phase7k_taker_field_readiness.csv")

@pytest.fixture
def fr_audit():
    return pd.read_csv(RUN / "phase7k_funding_rate_schema_audit.csv")

def test_bars_audit_exists(bars_audit):
    assert len(bars_audit) == 2

def test_taker_readiness_exists(taker_ready):
    assert len(taker_ready) == 6  # 3 candidates x 2 datasets

def test_funding_audit_exists(fr_audit):
    assert len(fr_audit) >= 1

def test_bars_schema_status_valid(bars_audit):
    for val in bars_audit["schema_status"]:
        assert val in VALID_READINESS_BARS, f"Invalid: {val}"

def test_taker_readiness_valid(taker_ready):
    for val in taker_ready["readiness_status"]:
        assert val in VALID_READINESS_TAKER, f"Invalid: {val}"

def test_funding_readiness_valid(fr_audit):
    for val in fr_audit["readiness_status"]:
        assert val in VALID_READINESS_FR, f"Invalid: {val}"

def test_missing_column_not_ready_as_defined(taker_ready):
    for _, r in taker_ready.iterrows():
        if r["missing_columns"] and str(r["missing_columns"]).strip():
            assert r["readiness_status"] != "READY_AS_DEFINED", \
                f"{r['candidate_factor']}: missing columns but marked READY_AS_DEFINED"

def test_no_banned_status_in_docs():
    """Verify docs don't claim alpha/tradeable/etc — negative declarations are OK."""
    for doc_name in [
        "PHASE_7K_DATA_CONTRACT_SCHEMA_VERIFICATION.md",
        "phase7k_crypto_native_data_contract.md",
    ]:
        doc = (RUN / doc_name).read_text()
        lines = doc.split("\n")
        for line in lines:
            upper = line.upper()
            # Skip negative declarations (lines starting with "No " or containing "not")
            if upper.strip().startswith("NO ") or "WAS NOT" in upper or "NOT UPGRADED" in upper:
                continue
            for banned in BANNED:
                if banned in upper:
                    # Check it's not in a negative context
                    if "NO " + banned not in upper and "NOT " not in upper:
                        pytest.fail(f"{doc_name}: '{banned}' found in non-negative context: {line.strip()}")

def test_no_registry_modification():
    reg = ROOT / "scripts" / "factor_formula_registry.py"
    content = reg.read_text()
    count = content.count("FactorSpec(")
    assert count == 47, f"Registry has {count} factors, expected 47"
