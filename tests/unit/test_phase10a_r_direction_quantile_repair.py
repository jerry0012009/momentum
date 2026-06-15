"""Tests for Phase 10A-R Direction & Quantile Consistency Repair."""

import os

import pandas as pd
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
BASE = os.path.join(ROOT, "research", "factor_runs", "crypto_top50_factor_library")


class TestArtifactsExist:
    def test_closeout_exists(self):
        assert os.path.isfile(os.path.join(BASE, "PHASE_10A_R_DIRECTION_QUANTILE_REPAIR.md"))

    def test_direction_check_exists(self):
        assert os.path.isfile(os.path.join(BASE, "phase10a_r_direction_consistency_check.csv"))

    def test_bucket_returns_exists(self):
        assert os.path.isfile(os.path.join(BASE, "phase10a_r_quantile_bucket_returns.csv"))

    def test_inverted_diagnostic_exists(self):
        assert os.path.isfile(os.path.join(BASE, "phase10a_r_inverted_signal_diagnostic.csv"))

    def test_reconciliation_exists(self):
        assert os.path.isfile(os.path.join(BASE, "phase10a_r_rankic_quantile_reconciliation.csv"))

    def test_quality_checks_exists(self):
        assert os.path.isfile(os.path.join(BASE, "phase10a_r_quality_checks.csv"))


class TestDirectionConsistency:
    @pytest.fixture(autouse=True)
    def load(self):
        self.df = pd.read_csv(os.path.join(BASE, "phase10a_r_direction_consistency_check.csv"))

    def test_has_12_rows(self):
        assert len(self.df) == 12, f"Expected 12 (3×4), got {len(self.df)}"

    def test_has_3_signals(self):
        signals = sorted(self.df["signal_id"].unique())
        assert signals == sorted(["signal_v0_core_only", "signal_v0_pm_full_structured",
                                   "signal_v0_family_balanced_diagnostic"])

    def test_has_4_horizons(self):
        assert sorted(self.df["horizon"].unique()) == sorted(["1h", "4h", "24h", "72h"])

    def test_required_columns(self):
        required = ["signal_id", "horizon", "mean_rankic", "rankic_sign",
                     "quantile_mean_spread", "quantile_spread_sign",
                     "sign_consistent", "diagnostic_status", "likely_issue", "notes"]
        missing = [c for c in required if c not in self.df.columns]
        assert not missing, f"Missing: {missing}"


class TestInvertedDiagnostic:
    @pytest.fixture(autouse=True)
    def load(self):
        self.df = pd.read_csv(os.path.join(BASE, "phase10a_r_inverted_signal_diagnostic.csv"))

    def test_has_12_rows(self):
        assert len(self.df) == 12

    def test_has_3_signals(self):
        signals = sorted(self.df["signal_id"].unique())
        assert signals == sorted(["signal_v0_core_only", "signal_v0_pm_full_structured",
                                   "signal_v0_family_balanced_diagnostic"])

    def test_has_4_horizons(self):
        assert sorted(self.df["horizon"].unique()) == sorted(["1h", "4h", "24h", "72h"])


class TestBucketReturns:
    @pytest.fixture(autouse=True)
    def load(self):
        self.df = pd.read_csv(os.path.join(BASE, "phase10a_r_quantile_bucket_returns.csv"))

    def test_has_data(self):
        assert len(self.df) > 0

    def test_has_3_signals(self):
        signals = sorted(self.df["signal_id"].unique())
        assert signals == sorted(["signal_v0_core_only", "signal_v0_pm_full_structured",
                                   "signal_v0_family_balanced_diagnostic"])

    def test_has_4_horizons(self):
        assert sorted(self.df["horizon"].unique()) == sorted(["1h", "4h", "24h", "72h"])

    def test_has_5_and_10_buckets(self):
        assert sorted(self.df["n_buckets"].unique()) == [5, 10]


class TestQualityChecks:
    @pytest.fixture(autouse=True)
    def load(self):
        self.df = pd.read_csv(os.path.join(BASE, "phase10a_r_quality_checks.csv"))

    def test_all_pass(self):
        failures = self.df[self.df["status"] != "PASS"]
        assert failures.empty, f"Failed: {failures['check'].tolist()}"


class TestNoBacktestFiles:
    def test_no_cost_slippage_capacity(self):
        import glob
        for pat in ["*cost*", "*slippage*", "*capacity*", "*paper_trade*"]:
            matches = glob.glob(os.path.join(BASE, pat))
            assert not matches, f"Unexpected files: {matches}"


class TestBacktestScript:
    def test_no_shift_minus(self):
        script_path = os.path.join(ROOT, "scripts", "run_phase10a_signal_backtest.py")
        with open(script_path) as f:
            for line in f:
                code = line.split("#")[0]
                if "shift(-" in code and '"' not in code:
                    pytest.fail(f"Found shift(- in code: {line}")


class TestRoadmapPhases:
    def test_phase11_not_started(self):
        with open(os.path.join(ROOT, "docs", "FACTOR_LIBRARY_ROADMAP.md")) as f:
            content = f.read()
        for line in content.split("\n"):
            if line.strip().startswith("| Phase 11"):
                assert "NOT STARTED" in line, f"Phase 11: {line}"
                return
        pytest.fail("Phase 11 not in roadmap")

    def test_phase12_not_started(self):
        with open(os.path.join(ROOT, "docs", "FACTOR_LIBRARY_ROADMAP.md")) as f:
            content = f.read()
        for line in content.split("\n"):
            if line.strip().startswith("| Phase 12"):
                assert "NOT STARTED" in line, f"Phase 12: {line}"
                return
        pytest.fail("Phase 12 not in roadmap")

    def test_phase13_not_started(self):
        with open(os.path.join(ROOT, "docs", "FACTOR_LIBRARY_ROADMAP.md")) as f:
            content = f.read()
        for line in content.split("\n"):
            if line.strip().startswith("| Phase 13"):
                assert "NOT STARTED" in line, f"Phase 13: {line}"
                return
        pytest.fail("Phase 13 not in roadmap")
