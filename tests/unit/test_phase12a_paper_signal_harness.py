"""Tests for Phase 12A Paper Signal Generation Harness v0."""
import os
import pandas as pd
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
BASE = os.path.join(ROOT, "research", "factor_runs", "crypto_top50_factor_library")
SCRIPT = os.path.join(ROOT, "scripts", "run_phase12a_paper_signal_harness.py")


def _f(name):
    return os.path.join(BASE, name)


# --- Closeout ---
def test_closeout_exists():
    assert os.path.exists(_f("PHASE_12A_PAPER_SIGNAL_HARNESS_V0.md"))


def test_closeout_required_wording():
    t = open(_f("PHASE_12A_PAPER_SIGNAL_HARNESS_V0.md")).read().lower()
    for kw in ["paper signal harness only", "no real execution", "no exchange connection",
               "no final model", "no alpha claim", "phase 13 not started"]:
        assert kw in t, f"Missing: {kw}"


# --- Script ---
def test_script_exists():
    assert os.path.exists(SCRIPT)


def test_script_no_exchange_api():
    """Script must not contain exchange API calls."""
    t = open(SCRIPT).read().lower()
    for kw in ["binance", "bybit", "okx", "ftx", "api_key", "api_secret", "place_order", "submit_order"]:
        assert kw not in t, f"Script contains execution-related code: {kw}"


def test_script_no_credentials():
    t = open(SCRIPT).read().lower()
    for kw in ["api_key", "api_secret", "password", "load_credentials", "read_token"]:
        assert kw not in t, f"Script may read credentials: {kw}"


# --- Candidate freeze ---
def test_freeze_exists():
    assert os.path.exists(_f("phase12a_candidate_freeze.csv"))


def test_freeze_only_one_candidate():
    df = pd.read_csv(_f("phase12a_candidate_freeze.csv"))
    assert len(df) == 1


def test_freeze_correct_candidate():
    df = pd.read_csv(_f("phase12a_candidate_freeze.csv"))
    assert df.iloc[0]["candidate_id"] == "signal_v0_core_only__1h__original_no_guard"


def test_freeze_paper_only():
    df = pd.read_csv(_f("phase12a_candidate_freeze.csv"))
    assert df.iloc[0]["status"] == "PAPER_SIGNAL_DIAGNOSTIC_ONLY"
    assert df.iloc[0]["allowed_for_real_execution"] == False


def test_freeze_allowed_for_paper():
    df = pd.read_csv(_f("phase12a_candidate_freeze.csv"))
    assert df.iloc[0]["allowed_for_paper_signal"] == True


# --- Signal snapshot ---
def test_snapshot_exists():
    assert os.path.exists(_f("phase12a_latest_signal_snapshot.csv"))


def test_snapshot_has_required_columns():
    df = pd.read_csv(_f("phase12a_latest_signal_snapshot.csv"))
    required = ["timestamp", "symbol", "signal_value", "signal_rank", "signal_percentile",
                "side_label", "raw_weight", "diagnostic_weight", "quote_volume",
                "notional_volume", "liquidity_status", "notes"]
    for col in required:
        assert col in df, f"Missing column: {col}"


def test_snapshot_side_labels():
    df = pd.read_csv(_f("phase12a_latest_signal_snapshot.csv"))
    allowed = {"UPPER_SIDE", "LOWER_SIDE", "NEUTRAL", "EXCLUDED_NO_LIQUIDITY"}
    actual = set(df["side_label"].unique())
    assert actual.issubset(allowed), f"Unexpected labels: {actual - allowed}"


def test_snapshot_has_upper_and_lower():
    df = pd.read_csv(_f("phase12a_latest_signal_snapshot.csv"))
    assert (df["side_label"] == "UPPER_SIDE").sum() > 0
    assert (df["side_label"] == "LOWER_SIDE").sum() > 0


# --- Paper weights ---
def test_weights_exists():
    assert os.path.exists(_f("phase12a_paper_weights.csv"))


def test_weights_only_core_only():
    df = pd.read_csv(_f("phase12a_paper_weights.csv"))
    assert all(df["candidate_id"] == "signal_v0_core_only__1h__original_no_guard")


def test_weights_net_exposure_zero():
    df = pd.read_csv(_f("phase12a_paper_weights.csv"))
    net = df["diagnostic_weight"].sum()
    assert abs(net) < 0.01, f"Net weight not zero: {net}"


def test_weights_gross_exposure_one():
    df = pd.read_csv(_f("phase12a_paper_weights.csv"))
    gross = df["gross_exposure"].sum()
    assert abs(gross - 1.0) < 0.01, f"Gross exposure not 1.0: {gross}"


def test_weights_all_have_volume():
    df = pd.read_csv(_f("phase12a_paper_weights.csv"))
    assert all(df["notional_volume"] > 0), "Some weighted symbols have zero volume"


# --- Liquidity overlay ---
def test_overlay_exists():
    assert os.path.exists(_f("phase12a_liquidity_overlay.csv"))


def test_overlay_has_capacity_columns():
    df = pd.read_csv(_f("phase12a_liquidity_overlay.csv"))
    for col in ["participation_capacity_0_5pct", "participation_capacity_1pct", "participation_capacity_5pct"]:
        assert col in df


# --- Preflight checks ---
def test_preflight_exists():
    assert os.path.exists(_f("phase12a_preflight_checks.csv"))


def test_preflight_all_pass():
    df = pd.read_csv(_f("phase12a_preflight_checks.csv"))
    failed = df[df["status"] == "FAIL"]
    assert len(failed) == 0, f"Failed: {failed['check_name'].tolist()}"


# --- Quality checks ---
def test_quality_checks_exist():
    assert os.path.exists(_f("phase12a_quality_checks.csv"))


def test_quality_checks_all_pass():
    df = pd.read_csv(_f("phase12a_quality_checks.csv"))
    failed = df[df["status"] != "PASS"]
    assert len(failed) == 0, f"Failed: {failed['check_name'].tolist()}"


# --- Negative checks ---
def test_phase13_not_started():
    assert not os.path.exists(_f("phase13_*.csv"))
    assert not os.path.exists(_f("phase13_live_spec.md"))
