"""Tests for Phase 10B-lite Tail Diagnostics Addendum."""
import os
import pandas as pd
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
BASE = os.path.join(ROOT, "research", "factor_runs", "crypto_top50_factor_library")

class TestArtifactsExist:
    def test_closeout(self):
        assert os.path.isfile(os.path.join(BASE, "PHASE_10B_TAIL_ADDENDUM_CLOSEOUT.md"))
    def test_b0_contributors(self):
        assert os.path.isfile(os.path.join(BASE, "phase10b_bucket0_top_contributors.csv"))
    def test_robust_spread(self):
        assert os.path.isfile(os.path.join(BASE, "phase10b_robust_spread_addendum.csv"))
    def test_decision_matrix(self):
        assert os.path.isfile(os.path.join(BASE, "phase10b_pm_decision_matrix.csv"))
    def test_quality_checks(self):
        assert os.path.isfile(os.path.join(BASE, "phase10b_quality_checks.csv"))

class TestAddendum:
    @pytest.fixture(autouse=True)
    def load(self):
        self.df = pd.read_csv(os.path.join(BASE, "phase10b_robust_spread_addendum.csv"))
    def test_12_rows(self):
        assert len(self.df) == 12
    def test_3_signals(self):
        assert len(self.df["signal_id"].unique()) == 3
    def test_4_horizons(self):
        assert sorted(self.df["horizon"].unique()) == sorted(["1h", "4h", "24h", "72h"])

class TestDecisionMatrix:
    @pytest.fixture(autouse=True)
    def load(self):
        self.df = pd.read_csv(os.path.join(BASE, "phase10b_pm_decision_matrix.csv"))
    def test_12_rows(self):
        assert len(self.df) == 12
    def test_no_trade_conclusion(self):
        for col in ["recommended_next_action", "reason"]:
            for v in self.df[col]:
                assert "TRADE" not in str(v).upper()
                assert "LIVE" not in str(v).upper()

class TestQualityChecks:
    @pytest.fixture(autouse=True)
    def load(self):
        self.df = pd.read_csv(os.path.join(BASE, "phase10b_quality_checks.csv"))
    def test_no_fail(self):
        fails = self.df[self.df["status"] == "FAIL"]
        assert fails.empty, f"FAIL: {fails['check_name'].tolist()}"

class TestPreservation:
    def test_10a_original_exists(self):
        assert os.path.isfile(os.path.join(BASE, "phase10a_signal_rankic_summary.csv"))
        assert os.path.isfile(os.path.join(BASE, "phase10a_signal_quantile_spread_summary.csv"))
    def test_10ar_original_exists(self):
        assert os.path.isfile(os.path.join(BASE, "phase10a_r_direction_consistency_check.csv"))
        assert os.path.isfile(os.path.join(BASE, "phase10a_r_rankic_quantile_reconciliation.csv"))
