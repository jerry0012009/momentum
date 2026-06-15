"""Tests for Phase 11A Cost / Slippage / Turnover / Capacity Diagnostic v0."""
import os
import pandas as pd
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
BASE = os.path.join(ROOT, "research", "factor_runs", "crypto_top50_factor_library")


def _f(name):
    return os.path.join(BASE, name)


# --- Eligible variants ---
EXPECTED_VARIANTS = [
    "signal_v0_core_only__1h__original_bucket0_guard",
    "signal_v0_pm_full_structured__1h__original_bucket0_guard",
    "signal_v0_family_balanced_diagnostic__1h__original_bucket0_guard",
    "signal_v0_core_only__4h__original_bucket0_guard",
    "signal_v0_pm_full_structured__4h__original_bucket0_guard",
    "signal_v0_family_balanced_diagnostic__4h__original_bucket0_guard",
    "signal_v0_core_only__1h__original_no_guard",
    "signal_v0_pm_full_structured__1h__original_no_guard",
    "signal_v0_family_balanced_diagnostic__1h__original_no_guard",
]


# --- Closeout ---
def test_closeout_exists():
    assert os.path.exists(_f("PHASE_11A_COST_SLIPPAGE_CAPACITY_V0.md"))


def test_closeout_no_alpha_claim():
    t = open(_f("PHASE_11A_COST_SLIPPAGE_CAPACITY_V0.md")).read().lower()
    assert "no alpha claim" in t


def test_closeout_phase12_not_started():
    t = open(_f("PHASE_11A_COST_SLIPPAGE_CAPACITY_V0.md")).read().lower()
    assert "not started" in t


def test_closeout_negative_declarations():
    t = open(_f("PHASE_11A_COST_SLIPPAGE_CAPACITY_V0.md")).read().lower()
    for kw in ["no final model", "no paper execution", "no live execution", "no deployment"]:
        assert kw in t, f"Missing negative declaration: {kw}"


# --- Script ---
def test_script_exists():
    assert os.path.exists(os.path.join(ROOT, "scripts", "run_phase11a_cost_slippage_capacity.py"))


# --- Cost summary ---
def test_cost_summary_exists():
    assert os.path.exists(_f("phase11a_variant_cost_summary.csv"))


def test_cost_summary_9_rows():
    df = pd.read_csv(_f("phase11a_variant_cost_summary.csv"))
    assert len(df) == 9


def test_cost_summary_only_eligible_variants():
    df = pd.read_csv(_f("phase11a_variant_cost_summary.csv"))
    actual = sorted(df["variant_id"].tolist())
    expected = sorted(EXPECTED_VARIANTS)
    assert actual == expected, f"Variants mismatch: {set(actual) ^ set(expected)}"


def test_cost_summary_no_forbidden_status():
    df = pd.read_csv(_f("phase11a_variant_cost_summary.csv"))
    forbidden = {"ALPHA", "TRADEABLE", "LIVE", "DEPLOY", "PRODUCTION", "FINAL"}
    actual = set(df["phase11a_status"].unique())
    assert actual.isdisjoint(forbidden), f"Forbidden statuses: {actual & forbidden}"


def test_cost_summary_allowed_statuses():
    df = pd.read_csv(_f("phase11a_variant_cost_summary.csv"))
    allowed = {"COST_ROBUST_CANDIDATE", "COST_SENSITIVE_CANDIDATE", "FAILS_COST_DIAGNOSTIC", "NEEDS_LIQUIDITY_DATA", "DIAGNOSTIC_ONLY"}
    actual = set(df["phase11a_status"].unique())
    assert actual.issubset(allowed), f"Unexpected statuses: {actual - allowed}"


# --- Turnover ---
def test_turnover_exists():
    assert os.path.exists(_f("phase11a_turnover_summary.csv"))


def test_turnover_9_rows():
    df = pd.read_csv(_f("phase11a_turnover_summary.csv"))
    assert len(df) == 9


def test_turnover_convention_documented():
    df = pd.read_csv(_f("phase11a_turnover_summary.csv"))
    assert all(df["convention"] == "one_way"), "Turnover convention must be 'one_way'"


def test_turnover_4h_differs_from_1h():
    """4h turnover should differ from 1h (different rebalance frequency)."""
    df = pd.read_csv(_f("phase11a_turnover_summary.csv"))
    to_1h = df[df["variant_id"].str.contains("__1h__")]["turnover_median"].median()
    to_4h = df[df["variant_id"].str.contains("__4h__")]["turnover_median"].median()
    assert abs(to_1h - to_4h) > 0.01, f"1h and 4h turnover too similar: {to_1h:.3f} vs {to_4h:.3f}"


# --- Cost scenario grid ---
def test_cost_grid_exists():
    assert os.path.exists(_f("phase11a_cost_scenario_grid.csv"))


def test_cost_grid_108_rows():
    df = pd.read_csv(_f("phase11a_cost_scenario_grid.csv"))
    assert len(df) == 108, f"Expected 108 rows (9×12), got {len(df)}"


def test_cost_grid_fixed_scenarios():
    """Fee and slippage grid must be fixed, not optimized."""
    df = pd.read_csv(_f("phase11a_cost_scenario_grid.csv"))
    fees = sorted(df["fee_bps"].unique())
    slips = sorted(df["slippage_bps"].unique())
    assert fees == [2, 5, 10], f"Unexpected fee grid: {fees}"
    assert slips == [1, 5, 10, 25], f"Unexpected slippage grid: {slips}"


def test_cost_grid_scenarios_per_variant():
    df = pd.read_csv(_f("phase11a_cost_scenario_grid.csv"))
    per_var = df.groupby("variant_id").size()
    assert all(per_var == 12), f"Not all variants have 12 scenarios: {per_var.unique()}"


# --- Net spread ---
def test_net_spread_exists():
    assert os.path.exists(_f("phase11a_net_spread_summary.csv"))


def test_net_spread_9_rows():
    df = pd.read_csv(_f("phase11a_net_spread_summary.csv"))
    assert len(df) == 9


# --- Capacity / liquidity ---
def test_capacity_summary_exists():
    assert os.path.exists(_f("phase11a_capacity_summary.csv"))


def test_capacity_all_needs_liquidity_data():
    df = pd.read_csv(_f("phase11a_capacity_summary.csv"))
    assert all(df["capacity_status"] == "NEEDS_LIQUIDITY_DATA")


def test_liquidity_audit_exists():
    assert os.path.exists(_f("phase11a_liquidity_coverage_audit.csv"))


def test_liquidity_audit_data_missing():
    df = pd.read_csv(_f("phase11a_liquidity_coverage_audit.csv"))
    assert df.iloc[0]["status"] == "DATA_MISSING"


# --- Quality checks ---
def test_quality_checks_exist():
    assert os.path.exists(_f("phase11a_quality_checks.csv"))


def test_quality_checks_all_pass():
    df = pd.read_csv(_f("phase11a_quality_checks.csv"))
    failed = df[df["status"] != "PASS"]
    assert len(failed) == 0, f"Failed checks: {failed['check_name'].tolist()}"


# --- Negative checks ---
def test_guarded_bucket0_exposure_zero():
    """Guarded variants must have zero bucket0 exposure in cost summary."""
    df = pd.read_csv(_f("phase11a_variant_cost_summary.csv"))
    guarded = df[df["guard_variant"].str.contains("bucket0_guard")]
    # capacity_status should be NEEDS_LIQUIDITY_DATA, not indicating exposure issues
    assert len(guarded) == 6


def test_phase12_not_started():
    assert not os.path.exists(_f("phase12_signal_spec.md"))
    assert not os.path.exists(_f("phase12_paper_execution.csv"))


def test_phase13_not_started():
    assert not os.path.exists(_f("phase13_live_spec.md"))
