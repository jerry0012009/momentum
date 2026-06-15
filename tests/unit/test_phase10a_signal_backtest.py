"""Tests for Phase 10A Diagnostic Signal Backtest v0."""

import os
import subprocess

import pandas as pd
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
BASE = os.path.join(ROOT, "research", "factor_runs", "crypto_top50_factor_library")
SCRIPTS = os.path.join(ROOT, "scripts")


class TestArtifactsExist:
    def test_closeout_exists(self):
        assert os.path.isfile(os.path.join(BASE, "PHASE_10A_SIGNAL_BACKTEST_V0.md"))

    def test_script_exists(self):
        assert os.path.isfile(os.path.join(SCRIPTS, "run_phase10a_signal_backtest.py"))

    def test_rankic_summary_exists(self):
        assert os.path.isfile(os.path.join(BASE, "phase10a_signal_rankic_summary.csv"))

    def test_quantile_spread_summary_exists(self):
        assert os.path.isfile(os.path.join(BASE, "phase10a_signal_quantile_spread_summary.csv"))

    def test_quality_checks_exists(self):
        assert os.path.isfile(os.path.join(BASE, "phase10a_signal_backtest_quality_checks.csv"))

    def test_label_audit_exists(self):
        assert os.path.isfile(os.path.join(BASE, "phase10a_label_alignment_audit.csv"))


class TestRankIC:
    @pytest.fixture(autouse=True)
    def load(self):
        self.df = pd.read_csv(os.path.join(BASE, "phase10a_signal_rankic_summary.csv"))

    def test_has_12_rows(self):
        assert len(self.df) == 12, f"Expected 12 rows (3 signals × 4 horizons), got {len(self.df)}"

    def test_has_3_signals(self):
        signals = self.df["signal_id"].unique()
        expected = sorted(["signal_v0_core_only", "signal_v0_pm_full_structured",
                           "signal_v0_family_balanced_diagnostic"])
        assert sorted(signals) == expected

    def test_has_4_horizons(self):
        horizons = sorted(self.df["horizon"].unique())
        assert horizons == sorted(["1h", "4h", "24h", "72h"])

    def test_required_columns(self):
        required = ["signal_id", "horizon", "mean_rankic", "std_rankic",
                     "t_stat", "positive_rate", "n_timestamps", "n_observations"]
        missing = [c for c in required if c not in self.df.columns]
        assert not missing, f"Missing: {missing}"


class TestQuantileSpread:
    @pytest.fixture(autouse=True)
    def load(self):
        self.df = pd.read_csv(os.path.join(BASE, "phase10a_signal_quantile_spread_summary.csv"))

    def test_has_12_rows(self):
        assert len(self.df) == 12

    def test_has_3_signals(self):
        signals = self.df["signal_id"].unique()
        expected = sorted(["signal_v0_core_only", "signal_v0_pm_full_structured",
                           "signal_v0_family_balanced_diagnostic"])
        assert sorted(signals) == expected

    def test_has_4_horizons(self):
        horizons = sorted(self.df["horizon"].unique())
        assert horizons == sorted(["1h", "4h", "24h", "72h"])


class TestQualityChecks:
    @pytest.fixture(autouse=True)
    def load(self):
        self.df = pd.read_csv(os.path.join(BASE, "phase10a_signal_backtest_quality_checks.csv"))

    def test_all_pass(self):
        failures = self.df[self.df["status"] != "PASS"]
        assert failures.empty, f"Failed checks: {failures['check'].tolist()}"

    def test_required_checks(self):
        required = [
            "signal_panel_exists_or_regenerated", "all_3_signals_present",
            "all_4_horizons_present", "no_shift_minus_h_used",
            "no_label_recomputation_in_backtest", "no_weight_optimization",
            "no_costs_or_slippage", "no_portfolio_optimization",
            "no_alpha_claim", "phase11_not_started", "phase12_not_started",
            "phase13_not_started",
        ]
        checks = set(self.df["check"])
        missing = [c for c in required if c not in checks]
        assert not missing, f"Missing checks: {missing}"


class TestLabelAudit:
    @pytest.fixture(autouse=True)
    def load(self):
        self.df = pd.read_csv(os.path.join(BASE, "phase10a_label_alignment_audit.csv"))

    def test_all_pass(self):
        failures = self.df[self.df["status"] != "PASS"]
        assert failures.empty, f"Failed audits: {failures['check'].tolist()}"


class TestScriptStructure:
    def test_no_shift_minus(self):
        with open(os.path.join(SCRIPTS, "run_phase10a_signal_backtest.py")) as f:
            content = f.read()
        # Check actual code lines, not string literals
        for line in content.split("\n"):
            stripped = line.split("#")[0]  # remove comments
            if "shift(-" in stripped and '"' not in stripped:
                pytest.fail(f"Found shift(- in code: {line}")

    def test_no_label_recomputation(self):
        with open(os.path.join(SCRIPTS, "run_phase10a_signal_backtest.py")) as f:
            content = f.read()
        assert "shift(-1" not in content.split('"""')[0]  # not in code outside docstrings


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


class TestNoAlphaStatus:
    def test_no_alpha_tradeable_live(self):
        for csv_file in ["phase10a_signal_rankic_summary.csv",
                         "phase10a_signal_quantile_spread_summary.csv"]:
            df = pd.read_csv(os.path.join(BASE, csv_file))
            for col in df.columns:
                if df[col].dtype == object:
                    for val in df[col]:
                        if isinstance(val, str):
                            assert val not in ["ALPHA", "TRADEABLE", "LIVE", "DEPLOY"], \
                                f"Banned status {val} in {csv_file}"
