"""Phase 7H: validation tests for Batch-2 candidate selection."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"

VALID_DECISIONS = {"SELECT_NOW", "DEFER_REDUNDANT", "DEFER_DATA", "DEFER_OPS",
                   "DEFER_LEAKAGE_RISK", "DEFER_DIRECTION_UNCLEAR", "REJECT_FOR_NOW"}
VALID_STATUS = {"SELECTED_FOR_7I_IMPLEMENTATION", "DEFERRED", "REJECTED_FOR_NOW"}
BANNED_STATUS = {"ALPHA", "CANDIDATE_REVIEW", "TRADEABLE", "LIVE", "DEPLOY", "PORTFOLIO"}
BANNED_FIELD_CONTENT = {"alpha", "tradeable", "deploy", "live", "pnl", "portfolio", "signal_to_trade"}


@pytest.fixture(scope="module")
def sel() -> pd.DataFrame:
    p = RUN / "phase7h_batch2_candidate_selection.csv"
    if not p.exists():
        pytest.skip("Selection CSV not found")
    return pd.read_csv(p)


@pytest.fixture(scope="module")
def curated() -> set[str]:
    p = RUN / "phase7g_curated_factor_library_v0_2.csv"
    if not p.exists():
        return set()
    return set(pd.read_csv(p)["factor_id"])


def test_selection_csv_exists(sel: pd.DataFrame):
    assert len(sel) > 0


def test_no_forbidden_decisions(sel: pd.DataFrame):
    bad = set(sel["batch2_decision"].unique()) - VALID_DECISIONS
    assert not bad, f"Forbidden decisions: {bad}"


def test_no_forbidden_proposed_status(sel: pd.DataFrame):
    bad = set(sel["proposed_next_status"].unique()) - VALID_STATUS
    assert not bad, f"Forbidden proposed_next_status: {bad}"


def test_no_banned_status_values(sel: pd.DataFrame):
    for col in ["batch2_decision", "proposed_next_status"]:
        bad = set(sel[col].unique()) & BANNED_STATUS
        assert not bad, f"Banned values in {col}: {bad}"


def test_select_now_count(sel: pd.DataFrame):
    sn = sel[sel["batch2_decision"] == "SELECT_NOW"]
    assert 12 <= len(sn) <= 18, f"SELECT_NOW count {len(sn)} not in 12-18 range"


def test_no_batch1_factors_selected(sel: pd.DataFrame, curated: set[str]):
    if not curated:
        pytest.skip("No curated library found")
    sn = sel[sel["batch2_decision"] == "SELECT_NOW"]
    overlap = set(sn["factor_id"]) & curated
    assert not overlap, f"Batch-1 factors in SELECT_NOW: {overlap}"


def test_no_forbidden_language_in_fields(sel: pd.DataFrame):
    """Check that decision/status fields don't contain alpha/tradeable/deploy language."""
    BANNED = {"ALPHA", "TRADEABLE", "DEPLOY", "LIVE", "PORTFOLIO", "SIGNAL_TO_TRADE"}
    for col in ["batch2_decision", "proposed_next_status"]:
        bad = set(sel[col].unique()) & BANNED
        assert not bad, f"Banned values in {col}: {bad}"


def test_select_now_have_clear_direction(sel: pd.DataFrame):
    sn = sel[sel["batch2_decision"] == "SELECT_NOW"]
    unclear = sn[sn["direction_clarity"] != "CLEAR"]
    assert len(unclear) == 0, f"SELECT_NOW with unclear direction: {list(unclear['factor_id'])}"


def test_operator_gap_analysis_exists():
    p = RUN / "phase7h_operator_gap_analysis.csv"
    assert p.exists(), "Operator gap analysis CSV not found"
    df = pd.read_csv(p)
    assert len(df) > 0
    valid_gaps = {"NO_GAP", "SMALL_EXTENSION", "MEDIUM_EXTENSION", "NOT_SUPPORTED_NOW", "DATA_DEPENDENT"}
    bad = set(df["gap_type"].unique()) - valid_gaps
    assert not bad, f"Invalid gap_type values: {bad}"
