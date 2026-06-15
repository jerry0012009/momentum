"""Tests for Phase 10D-R Bucket0 Guard Implementation Repair."""
import os
import pandas as pd
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
BASE = os.path.join(ROOT, "research", "factor_runs", "crypto_top50_factor_library")


def _f(name):
    return os.path.join(BASE, name)


# --- Closeout ---
def test_closeout_exists():
    assert os.path.exists(_f("PHASE_10D_R_BUCKET0_GUARD_REPAIR.md"))


def test_closeout_describes_bugs():
    t = open(_f("PHASE_10D_R_BUCKET0_GUARD_REPAIR.md")).read().lower()
    assert "bug" in t
    assert "bucket assignment" in t or "bucket0" in t


def test_closeout_no_alpha_claim():
    t = open(_f("PHASE_10D_R_BUCKET0_GUARD_REPAIR.md")).read().lower()
    assert "no alpha claim" in t


def test_closeout_phase11_not_started():
    t = open(_f("PHASE_10D_R_BUCKET0_GUARD_REPAIR.md")).read().lower()
    assert "not started" in t


# --- Summary ---
def test_summary_exists():
    assert os.path.exists(_f("phase10d_variant_evaluation_summary.csv"))


def test_summary_48_rows():
    df = pd.read_csv(_f("phase10d_variant_evaluation_summary.csv"))
    assert len(df) == 48


def test_summary_all_3_signals():
    df = pd.read_csv(_f("phase10d_variant_evaluation_summary.csv"))
    assert len(df["signal_id"].unique()) == 3


def test_summary_all_4_horizons():
    df = pd.read_csv(_f("phase10d_variant_evaluation_summary.csv"))
    assert len(df["horizon"].unique()) == 4


def test_summary_all_4_variants():
    df = pd.read_csv(_f("phase10d_variant_evaluation_summary.csv"))
    assert len(df["direction_variant"].unique()) == 2
    assert len(df["guard_variant"].unique()) == 2


# --- Bucket exposure ---
def test_bucket_exposure_exists():
    assert os.path.exists(_f("phase10d_variant_bucket_exposure.csv"))


def test_guarded_exposure_exactly_zero():
    """All guarded variants must have bucket0_lower_leg_exposure_fraction == 0."""
    df = pd.read_csv(_f("phase10d_variant_evaluation_summary.csv"))
    guarded = df[df["guard_variant"] == "bucket0_guard"]
    assert len(guarded) == 24
    assert (guarded["bucket0_lower_leg_exposure_fraction"] == 0).all(), \
        f"Non-zero guarded exposure: {guarded[guarded['bucket0_lower_leg_exposure_fraction'] != 0][['variant_id', 'bucket0_lower_leg_exposure_fraction']].to_string()}"


def test_no_guard_exposure_nonzero():
    """All no_guard variants must have nonzero bucket0 exposure (bucket 0 in short leg)."""
    df = pd.read_csv(_f("phase10d_variant_evaluation_summary.csv"))
    no_guard = df[df["guard_variant"] == "no_guard"]
    assert len(no_guard) == 24
    assert (no_guard["bucket0_lower_leg_exposure_fraction"] > 0).all(), \
        f"Zero no_guard exposure: {no_guard[no_guard['bucket0_lower_leg_exposure_fraction'] == 0][['variant_id']].to_string()}"


# --- Pass/fail ---
def test_pass_fail_exists():
    assert os.path.exists(_f("phase10d_variant_pass_fail_matrix.csv"))


def test_pass_fail_48_rows():
    df = pd.read_csv(_f("phase10d_variant_pass_fail_matrix.csv"))
    assert len(df) == 48


def test_guarded_pass_have_zero_exposure():
    """All PASS guarded variants must have zero bucket0 exposure."""
    df = pd.read_csv(_f("phase10d_variant_pass_fail_matrix.csv"))
    passed_guarded = df[(df["pass_status"] == "PASS") & (df["guard_variant"] == "bucket0_guard")]
    assert (passed_guarded["bucket0_lower_leg_exposure_fraction"] == 0).all()


def test_at_least_9_pass():
    df = pd.read_csv(_f("phase10d_variant_pass_fail_matrix.csv"))
    passed = df[df["pass_status"] == "PASS"]
    assert len(passed) >= 9, f"Expected >= 9 PASS, got {len(passed)}"


# --- Quality checks ---
def test_quality_checks_exist():
    assert os.path.exists(_f("phase10d_quality_checks.csv"))


def test_quality_checks_all_pass():
    df = pd.read_csv(_f("phase10d_quality_checks.csv"))
    failed = df[df["status"] != "PASS"]
    assert len(failed) == 0, f"Failed checks: {failed['check_name'].tolist()}"


def test_guarded_bucket0_exposure_zero_check():
    """Quality check must verify guarded exposure is zero, not nonzero."""
    df = pd.read_csv(_f("phase10d_quality_checks.csv"))
    row = df[df["check_name"] == "guarded_bucket0_exposure_zero"]
    assert len(row) == 1
    assert row.iloc[0]["status"] == "PASS"


def test_no_guard_bucket0_exposure_nonzero_check():
    """Quality check must verify no_guard exposure is nonzero."""
    df = pd.read_csv(_f("phase10d_quality_checks.csv"))
    row = df[df["check_name"] == "no_guard_bucket0_exposure_nonzero"]
    assert len(row) == 1
    assert row.iloc[0]["status"] == "PASS"


# --- Negative checks ---
def test_no_costs_slippage_capacity():
    for f_name in os.listdir(BASE):
        if "cost" in f_name.lower() or "slippage" in f_name.lower() or "capacity" in f_name.lower():
            if f_name.startswith("phase10d"):
                pytest.fail(f"Cost/slippage/capacity file found: {f_name}")


def test_no_final_model():
    for f_name in os.listdir(BASE):
        if "model" in f_name.lower() and f_name.startswith("phase10d"):
            pytest.fail(f"Model file found: {f_name}")


def test_phase11_not_started():
    assert not os.path.exists(_f("phase11_signal_v1_spec.md"))
    assert not os.path.exists(_f("phase11_backtest_results.csv"))
