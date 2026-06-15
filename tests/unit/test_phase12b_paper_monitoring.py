"""Tests for Phase 12B Paper Signal Monitoring Backfill & Rolling Diagnostics."""
import os
import pandas as pd
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
BASE = os.path.join(ROOT, "research", "factor_runs", "crypto_top50_factor_library")
SCRIPT = os.path.join(ROOT, "scripts", "run_phase12b_paper_monitoring.py")


def _f(name):
    return os.path.join(BASE, name)


# --- Closeout ---
def test_closeout_exists():
    assert os.path.exists(_f("PHASE_12B_PAPER_MONITORING_DIAGNOSTIC.md"))


def test_closeout_required_wording():
    t = open(_f("PHASE_12B_PAPER_MONITORING_DIAGNOSTIC.md")).read().lower()
    for kw in ["no real execution", "no exchange connection", "no final model", "phase 13"]:
        assert kw in t, f"Missing: {kw}"


# --- Script ---
def test_script_exists():
    assert os.path.exists(SCRIPT)


def test_script_no_exchange_api():
    t = open(SCRIPT).read().lower()
    for kw in ["binance", "bybit", "okx", "ftx", "place_order", "submit_order"]:
        assert kw not in t, f"Script contains execution code: {kw}"


def test_script_no_credentials():
    t = open(SCRIPT).read().lower()
    for kw in ["api_key", "api_secret", "load_credentials", "read_token"]:
        assert kw not in t, f"Script may read credentials: {kw}"


def test_script_no_shift_for_labels():
    """Script must not use shift(-) to compute forward labels."""
    t = open(SCRIPT).read()
    # Allow shift(1) but not shift(-N)
    import re
    neg_shifts = re.findall(r'shift\s*\(\s*-', t)
    assert len(neg_shifts) == 0, f"Script uses shift(-N) to compute labels: {neg_shifts}"


# --- Paper signal log ---
def test_paper_signal_log_exists():
    assert os.path.exists(_f("phase12b_paper_signal_log.csv"))


def test_paper_signal_log_has_columns():
    df = pd.read_csv(_f("phase12b_paper_signal_log.csv"))
    for col in ["timestamp", "symbol", "signal_value", "signal_rank", "side_label",
                "diagnostic_weight", "quote_volume", "notional_volume", "liquidity_status",
                "data_freshness_status"]:
        assert col in df, f"Missing: {col}"


def test_paper_signal_log_only_core_only():
    """Only signal_v0_core_only should be used (check side labels are valid)."""
    df = pd.read_csv(_f("phase12b_paper_signal_log.csv"))
    allowed = {"UPPER_SIDE", "LOWER_SIDE", "NEUTRAL"}
    assert set(df["side_label"].unique()).issubset(allowed)


# --- Monitoring summaries ---
def test_stability_summary_exists():
    assert os.path.exists(_f("phase12b_signal_stability_summary.csv"))


def test_turnover_monitoring_exists():
    assert os.path.exists(_f("phase12b_turnover_monitoring.csv"))


def test_exposure_monitoring_exists():
    assert os.path.exists(_f("phase12b_exposure_monitoring.csv"))


def test_liquidity_monitoring_exists():
    assert os.path.exists(_f("phase12b_liquidity_monitoring.csv"))


def test_data_freshness_exists():
    assert os.path.exists(_f("phase12b_data_freshness_monitoring.csv"))


# --- Realized returns ---
def test_realized_return_tracking_exists():
    assert os.path.exists(_f("phase12b_realized_paper_return_tracking.csv"))


def test_realized_return_summary_exists():
    assert os.path.exists(_f("phase12b_realized_return_summary.csv"))


# --- Alerts ---
def test_alerts_file_exists():
    assert os.path.exists(_f("phase12b_monitoring_alerts.csv"))


def test_alerts_has_required_columns():
    df = pd.read_csv(_f("phase12b_monitoring_alerts.csv"))
    for col in ["timestamp", "alert_type", "severity", "detail", "recommended_action"]:
        assert col in df, f"Missing: {col}"


# --- Quality checks ---
def test_quality_checks_exist():
    assert os.path.exists(_f("phase12b_quality_checks.csv"))


def test_quality_checks_all_pass():
    df = pd.read_csv(_f("phase12b_quality_checks.csv"))
    failed = df[df["status"] != "PASS"]
    assert len(failed) == 0, f"Failed: {failed['check_name'].tolist()}"


# --- Exposure ---
def test_gross_exposure_approx_one():
    df = pd.read_csv(_f("phase12b_exposure_monitoring.csv"))
    assert abs(df["gross_exposure"].mean() - 1.0) < 0.01


def test_net_exposure_approx_zero():
    df = pd.read_csv(_f("phase12b_exposure_monitoring.csv"))
    assert abs(df["net_exposure"].mean()) < 0.01


# --- Liquidity ---
def test_liquidity_coverage():
    df = pd.read_csv(_f("phase12b_liquidity_monitoring.csv"))
    assert df["weighted_symbol_count"].min() > 0


# --- Negative checks ---
def test_phase13_not_started():
    assert not os.path.exists(_f("phase13_*.csv"))
