"""Tests for Phase 10D Tail-Aware Signal Variant Evaluation."""
import os
import pandas as pd
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
BASE = os.path.join(ROOT, "research", "factor_runs", "crypto_top50_factor_library")


def _f(name):
    return os.path.join(BASE, name)


# --- Closeout ---
def test_closeout_exists():
    assert os.path.exists(_f("PHASE_10D_TAIL_AWARE_SIGNAL_VARIANT_EVALUATION.md"))


def test_closeout_no_alpha_claim():
    t = open(_f("PHASE_10D_TAIL_AWARE_SIGNAL_VARIANT_EVALUATION.md")).read().lower()
    assert "no alpha claim" in t


def test_closeout_no_phase11():
    t = open(_f("PHASE_10D_TAIL_AWARE_SIGNAL_VARIANT_EVALUATION.md")).read().lower()
    assert "not started" in t


# --- Evaluation Summary ---
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


def test_summary_has_required_columns():
    df = pd.read_csv(_f("phase10d_variant_evaluation_summary.csv"))
    for col in ["variant_id", "signal_id", "horizon", "direction_variant", "guard_variant",
                 "mean_rankic", "median_spread", "bucket0_lower_leg_exposure_fraction"]:
        assert col in df.columns, f"Missing {col}"


# --- Original RankIC all positive ---
def test_original_rankic_all_positive():
    df = pd.read_csv(_f("phase10d_variant_evaluation_summary.csv"))
    orig = df[df["direction_variant"] == "original"]
    assert (orig["mean_rankic"] > 0).all(), \
        f"Original RankIC not all positive: {orig[['variant_id','mean_rankic']].to_string()}"


def test_inverted_rankic_all_negative():
    df = pd.read_csv(_f("phase10d_variant_evaluation_summary.csv"))
    inv = df[df["direction_variant"] == "inverted"]
    assert (inv["mean_rankic"] < 0).all()


# --- Pass/Fail ---
def test_pass_fail_exists():
    assert os.path.exists(_f("phase10d_variant_pass_fail_matrix.csv"))


def test_pass_fail_48_rows():
    df = pd.read_csv(_f("phase10d_variant_pass_fail_matrix.csv"))
    assert len(df) == 48


def test_pass_fail_has_pass_status():
    df = pd.read_csv(_f("phase10d_variant_pass_fail_matrix.csv"))
    assert "pass_status" in df.columns
    assert set(df["pass_status"].unique()).issubset({"PASS", "FAIL"})


def test_at_least_3_pass():
    df = pd.read_csv(_f("phase10d_variant_pass_fail_matrix.csv"))
    passed = df[df["pass_status"] == "PASS"]
    assert len(passed) >= 3, f"Expected >= 3 PASS, got {len(passed)}"


def test_all_pass_have_positive_rankic_and_spread():
    df = pd.read_csv(_f("phase10d_variant_pass_fail_matrix.csv"))
    passed = df[df["pass_status"] == "PASS"]
    assert (passed["mean_rankic"] > 0).all()
    assert (passed["median_spread"] > 0).all()


# --- Bucket Exposure ---
def test_bucket_exposure_exists():
    assert os.path.exists(_f("phase10d_variant_bucket_exposure.csv"))


def test_bucket_exposure_48_rows():
    df = pd.read_csv(_f("phase10d_variant_bucket_exposure.csv"))
    assert len(df) == 48


# --- Quality Checks ---
def test_quality_checks_exist():
    assert os.path.exists(_f("phase10d_quality_checks.csv"))


def test_quality_checks_all_pass():
    df = pd.read_csv(_f("phase10d_quality_checks.csv"))
    failed = df[df["status"] != "PASS"]
    assert len(failed) == 0, f"Failed checks: {failed['check_name'].tolist()}"


def test_guarded_bucket0_exposure_nonzero():
    """Guarded variants must have bucket0 in cross-section (guard removes it from short leg)."""
    df = pd.read_csv(_f("phase10d_variant_evaluation_summary.csv"))
    guarded = df[df["guard_variant"] == "bucket0_guard"]
    assert (guarded["bucket0_lower_leg_exposure_fraction"] > 0).all()


# --- Negative checks ---
def test_no_phase11_artifacts():
    assert not os.path.exists(_f("phase11_signal_v1_spec.md"))
    assert not os.path.exists(_f("phase11_backtest_results.csv"))


def test_no_alpha_tradeable_live():
    for f_name in os.listdir(BASE):
        if f_name.startswith("phase10d") and f_name.endswith(".csv"):
            df = pd.read_csv(os.path.join(BASE, f_name))
            for col in df.columns:
                if df[col].dtype == object:
                    vals = df[col].str.upper().dropna()
                    for bad in ["ALPHA", "TRADEABLE", "LIVE", "DEPLOY"]:
                        assert bad not in vals.values, f"{bad} found in {f_name}[{col}]"
