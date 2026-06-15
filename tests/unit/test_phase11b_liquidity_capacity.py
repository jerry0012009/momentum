"""Tests for Phase 11B Canonical Liquidity Data & Capacity Analysis."""
import os
import pandas as pd
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
BASE = os.path.join(ROOT, "research", "factor_runs", "crypto_top50_factor_library")


def _f(name):
    return os.path.join(BASE, name)


EXPECTED_VARIANTS = [
    "signal_v0_core_only__1h__original_no_guard",
    "signal_v0_core_only__1h__original_bucket0_guard",
    "signal_v0_pm_full_structured__1h__original_no_guard",
    "signal_v0_family_balanced_diagnostic__1h__original_no_guard",
]

EXPECTED_PARTICIPATION = [0.001, 0.005, 0.01, 0.02, 0.05]
EXPECTED_NOTIONAL = [1000, 5000, 10000, 50000, 100000]


# --- Closeout ---
def test_closeout_exists():
    assert os.path.exists(_f("PHASE_11B_LIQUIDITY_CAPACITY_DIAGNOSTIC.md"))


def test_closeout_no_alpha():
    t = open(_f("PHASE_11B_LIQUIDITY_CAPACITY_DIAGNOSTIC.md")).read().lower()
    assert "no alpha claim" in t


def test_closeout_negative_declarations():
    t = open(_f("PHASE_11B_LIQUIDITY_CAPACITY_DIAGNOSTIC.md")).read().lower()
    for kw in ["no final model", "no paper execution", "no live execution", "phase 12 not started"]:
        assert kw in t, f"Missing: {kw}"


# --- Script ---
def test_script_exists():
    assert os.path.exists(os.path.join(ROOT, "scripts", "run_phase11b_liquidity_capacity.py"))


# --- Inventory ---
def test_inventory_exists():
    assert os.path.exists(_f("phase11b_liquidity_data_inventory.csv"))


def test_inventory_43_symbols():
    df = pd.read_csv(_f("phase11b_liquidity_data_inventory.csv"))
    assert len(df) == 43


def test_inventory_no_fabricated_data():
    """No symbol should be marked AVAILABLE without actual data."""
    df = pd.read_csv(_f("phase11b_liquidity_data_inventory.csv"))
    available = df[df["status"] == "AVAILABLE"]
    assert len(available) >= 30, f"Too few symbols with data: {len(available)}"


# --- Liquidity quality ---
def test_quality_exists():
    assert os.path.exists(_f("phase11b_liquidity_data_quality.csv"))


def test_quality_no_duplicates():
    df = pd.read_csv(_f("phase11b_liquidity_data_quality.csv"))
    row = df[df["metric"] == "duplicate_timestamp_symbol"]
    assert len(row) == 1
    assert int(row.iloc[0]["value"]) == 0


def test_quality_timestamp_overlap():
    df = pd.read_csv(_f("phase11b_liquidity_data_quality.csv"))
    row = df[df["metric"] == "timestamp_overlap_with_signal_panel"]
    assert len(row) == 1
    assert str(row.iloc[0]["value"]).lower() == "true"


# --- Capacity summary ---
def test_capacity_summary_exists():
    assert os.path.exists(_f("phase11b_capacity_summary.csv"))


def test_capacity_summary_4_variants():
    df = pd.read_csv(_f("phase11b_capacity_summary.csv"))
    assert len(df) == 4


def test_capacity_by_variant_exists():
    assert os.path.exists(_f("phase11b_capacity_by_variant.csv"))


def test_capacity_by_variant_participation_rates():
    df = pd.read_csv(_f("phase11b_capacity_by_variant.csv"))
    rates = sorted(df["participation_rate"].unique())
    assert rates == EXPECTED_PARTICIPATION, f"Unexpected rates: {rates}"


# --- Bottleneck ---
def test_bottleneck_exists():
    assert os.path.exists(_f("phase11b_bottleneck_symbols.csv"))


# --- Cost-capacity matrix ---
def test_matrix_exists():
    assert os.path.exists(_f("phase11b_cost_capacity_matrix.csv"))


def test_matrix_participation_rates():
    df = pd.read_csv(_f("phase11b_cost_capacity_matrix.csv"))
    rates = sorted(df["participation_rate"].unique())
    assert rates == EXPECTED_PARTICIPATION


def test_matrix_notional_assumptions():
    df = pd.read_csv(_f("phase11b_cost_capacity_matrix.csv"))
    notionals = sorted(df["notional_usd"].unique())
    assert notionals == EXPECTED_NOTIONAL


def test_matrix_fixed_scenarios():
    df = pd.read_csv(_f("phase11b_cost_capacity_matrix.csv"))
    assert sorted(df["fee_bps"].unique()) == [2, 5, 10]
    assert sorted(df["slippage_bps"].unique()) == [1, 5, 10, 25]


# --- PM decision ---
def test_pm_decision_exists():
    assert os.path.exists(_f("phase11b_pm_decision_matrix.csv"))


def test_pm_decision_no_forbidden_status():
    df = pd.read_csv(_f("phase11b_pm_decision_matrix.csv"))
    forbidden = {"ALPHA", "TRADEABLE", "LIVE", "DEPLOY", "PRODUCTION", "FINAL"}
    actual = set(df["phase11b_status"].unique())
    assert actual.isdisjoint(forbidden), f"Forbidden: {actual & forbidden}"


def test_pm_decision_allowed_statuses():
    df = pd.read_csv(_f("phase11b_pm_decision_matrix.csv"))
    allowed = {"PAPER_READY_DIAGNOSTIC_CANDIDATE", "CAPACITY_LIMITED_CANDIDATE",
               "COST_CAPACITY_SENSITIVE", "FAILS_CAPACITY_DIAGNOSTIC",
               "DATA_MISSING_BLOCKED", "RETURN_TO_SIGNAL_DESIGN"}
    actual = set(df["phase11b_status"].unique())
    assert actual.issubset(allowed), f"Unexpected: {actual - allowed}"


# --- Quality checks ---
def test_quality_checks_exist():
    assert os.path.exists(_f("phase11b_quality_checks.csv"))


def test_quality_checks_all_pass():
    df = pd.read_csv(_f("phase11b_quality_checks.csv"))
    failed = df[df["status"] != "PASS"]
    assert len(failed) == 0, f"Failed: {failed['check_name'].tolist()}"


# --- Negative checks ---
def test_no_final_model():
    assert not os.path.exists(_f("phase12_signal_spec.md"))
    assert not os.path.exists(_f("phase12_paper_execution.csv"))


def test_phase12_not_started():
    assert not os.path.exists(_f("phase12_*.csv"))


def test_phase13_not_started():
    assert not os.path.exists(_f("phase13_*.csv"))
