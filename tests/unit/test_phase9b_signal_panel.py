"""Tests for Phase 9B Deterministic Signal Panel Implementation."""

import glob
import os

import pandas as pd
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
BASE = os.path.join(ROOT, "research", "factor_runs", "crypto_top50_factor_library")
SCRIPTS = os.path.join(ROOT, "scripts")


class TestArtifactsExist:
    def test_script_exists(self):
        assert os.path.isfile(os.path.join(SCRIPTS, "build_phase9b_signal_panel.py"))

    def test_closeout_exists(self):
        assert os.path.isfile(os.path.join(BASE, "PHASE_9B_DETERMINISTIC_SIGNAL_PANEL.md"))

    def test_parquet_exists(self):
        assert os.path.isfile(os.path.join(BASE, "phase9b_signal_panel.parquet"))

    def test_manifest_exists(self):
        assert os.path.isfile(os.path.join(BASE, "phase9b_signal_panel_manifest.csv"))

    def test_component_manifest_exists(self):
        assert os.path.isfile(os.path.join(BASE, "phase9b_signal_component_manifest.csv"))

    def test_coverage_exists(self):
        assert os.path.isfile(os.path.join(BASE, "phase9b_signal_coverage_summary.csv"))

    def test_quality_checks_exists(self):
        assert os.path.isfile(os.path.join(BASE, "phase9b_signal_quality_checks.csv"))


class TestManifest:
    @pytest.fixture(autouse=True)
    def load(self):
        self.df = pd.read_csv(os.path.join(BASE, "phase9b_signal_panel_manifest.csv"))

    def test_has_3_signals(self):
        assert len(self.df) == 3

    def test_required_signal_ids(self):
        expected = sorted(["signal_v0_core_only", "signal_v0_pm_full_structured",
                           "signal_v0_family_balanced_diagnostic"])
        assert sorted(self.df["signal_id"].tolist()) == expected

    def test_no_optimization(self):
        assert not self.df["optimization_used"].any()

    def test_no_labels_returns(self):
        assert not self.df["labels_or_returns_used"].any()

    def test_backtest_not_started(self):
        assert (self.df["backtest_status"] == "NOT_STARTED").all()

    def test_no_alpha_claim(self):
        assert (self.df["alpha_claim_status"] == "NO_ALPHA_CLAIM").all()


class TestSignalPanel:
    @pytest.fixture(autouse=True)
    def load(self):
        self.df = pd.read_parquet(os.path.join(BASE, "phase9b_signal_panel.parquet"))

    def test_required_columns(self):
        required = [
            "timestamp", "symbol",
            "risk_pressure_component", "oscillator_exhaustion_component",
            "raw_core_score", "liquidity_gate",
            "position_timing_overlay", "position_overlay_multiplier",
            "signal_v0_core_only", "signal_v0_pm_full_structured",
            "signal_v0_family_balanced_diagnostic",
            "valid_factor_count", "signal_construction_version",
        ]
        missing = [c for c in required if c not in self.df.columns]
        assert not missing, f"Missing columns: {missing}"

    def test_no_label_columns(self):
        assert not any("label" in c.lower() for c in self.df.columns)

    def test_no_forward_return_columns(self):
        assert not any("forward" in c.lower() or "fwd" in c.lower() for c in self.df.columns)

    def test_no_non_candidate_factors(self):
        # Signal panel should not contain raw factor columns
        raw_factors = ["vol_5h", "vol_40h", "downside_vol_20h", "vol_of_vol_20h",
                       "rsi_7h", "rsi_28h", "xs_rank_vol", "range_1h", "range_4h", "price_pos_24h"]
        for f in raw_factors:
            assert f not in self.df.columns, f"Raw factor {f} should not be in signal panel"

    def test_liquidity_gate_bounded(self):
        lg = self.df["liquidity_gate"].dropna()
        assert (lg >= 0.50).all() and (lg <= 1.00).all()

    def test_position_overlay_multiplier_bounded(self):
        pom = self.df["position_overlay_multiplier"].dropna()
        assert (pom >= 0.85).all() and (pom <= 1.15).all()

    def test_has_data(self):
        assert len(self.df) > 100000, f"Expected >100k rows, got {len(self.df)}"


class TestNoBacktestFiles:
    def test_no_backtest_portfolio(self):
        for pat in ["*backtest*", "*pnl*", "*strategy_result*", "*portfolio*"]:
            matches = glob.glob(os.path.join(BASE, pat))
            assert not matches, f"Unexpected files: {matches}"


class TestRoadmap:
    def test_phase10_not_started(self):
        with open(os.path.join(ROOT, "docs", "FACTOR_LIBRARY_ROADMAP.md")) as f:
            content = f.read()
        for line in content.split("\n"):
            if line.strip().startswith("| Phase 10"):
                assert "NOT STARTED" in line, f"Phase 10 row: {line}"
                return
        pytest.fail("Phase 10 not found in roadmap")
