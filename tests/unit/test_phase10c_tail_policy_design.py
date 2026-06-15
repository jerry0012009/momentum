"""Tests for Phase 10C Tail-Aware Signal Policy Design."""
import os
import pandas as pd
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
BASE = os.path.join(ROOT, "research", "factor_runs", "crypto_top50_factor_library")

class TestArtifactsExist:
    def test_closeout(self):
        assert os.path.isfile(os.path.join(BASE, "PHASE_10C_TAIL_AWARE_SIGNAL_POLICY_DESIGN.md"))
    def test_policy_options(self):
        assert os.path.isfile(os.path.join(BASE, "phase10c_tail_policy_options.csv"))
    def test_horizon_direction(self):
        assert os.path.isfile(os.path.join(BASE, "phase10c_horizon_direction_policy.csv"))
    def test_design_spec(self):
        assert os.path.isfile(os.path.join(BASE, "phase10c_signal_v1_design_spec.md"))
    def test_evaluation_protocol(self):
        assert os.path.isfile(os.path.join(BASE, "phase10c_phase10d_evaluation_protocol.csv"))
    def test_quality_checks(self):
        assert os.path.isfile(os.path.join(BASE, "phase10c_quality_checks.csv"))

class TestPolicyOptions:
    @pytest.fixture(autouse=True)
    def load(self):
        self.df = pd.read_csv(os.path.join(BASE, "phase10c_tail_policy_options.csv"))
    def test_at_least_5_policies(self):
        assert len(self.df) >= 5
    def test_required_policies_present(self):
        ids = set(self.df["policy_id"])
        for p in ["POLICY_A", "POLICY_B", "POLICY_C", "POLICY_E"]:
            assert p in ids, f"Missing {p}"
    def test_pm_recommendation_populated(self):
        assert self.df["pm_recommendation"].notna().all()

class TestHorizonDirectionPolicy:
    @pytest.fixture(autouse=True)
    def load(self):
        self.df = pd.read_csv(os.path.join(BASE, "phase10c_horizon_direction_policy.csv"))
    def test_12_rows(self):
        assert len(self.df) == 12
    def test_3_signals(self):
        assert len(self.df["signal_id"].unique()) == 3
    def test_4_horizons(self):
        assert sorted(self.df["horizon"].unique()) == sorted(["1h", "4h", "24h", "72h"])
    def test_allowed_policies(self):
        allowed = {"KEEP_ORIGINAL_FOR_DIAGNOSTIC", "DO_NOT_SHORT_BUCKET0",
                    "INVERSION_REVIEW_24_72_ONLY", "HORIZON_SPECIFIC_REVIEW",
                    "BLOCK_SIGNAL_FOR_PHASE11"}
        for v in self.df["proposed_direction_policy"]:
            assert v in allowed, f"Unexpected policy: {v}"

class TestDesignSpec:
    def test_not_empty(self):
        with open(os.path.join(BASE, "phase10c_signal_v1_design_spec.md")) as f:
            content = f.read()
        assert len(content) > 500
    def test_mentions_bucket0_guard(self):
        with open(os.path.join(BASE, "phase10c_signal_v1_design_spec.md")) as f:
            assert "bucket 0 guard" in f.read().lower()

class TestEvaluationProtocol:
    @pytest.fixture(autouse=True)
    def load(self):
        self.df = pd.read_csv(os.path.join(BASE, "phase10c_phase10d_evaluation_protocol.csv"))
    def test_at_least_15_items(self):
        assert len(self.df) >= 15
    def test_required_items(self):
        items = set(self.df["protocol_item"])
        for r in ["signals_to_evaluate", "horizons", "rankic", "median_spread",
                  "tail_trim_spread", "bucket0_guard_check", "no_cost_slippage",
                  "no_phase11", "no_alpha_claim"]:
            assert r in items, f"Missing {r}"

class TestQualityChecks:
    @pytest.fixture(autouse=True)
    def load(self):
        self.df = pd.read_csv(os.path.join(BASE, "phase10c_quality_checks.csv"))
    def test_no_fail(self):
        fails = self.df[self.df["status"] == "FAIL"]
        assert fails.empty, f"FAIL: {fails['check_name'].tolist()}"

class TestNoPhase11:
    def test_no_signal_v1_parquet(self):
        assert not os.path.isfile(os.path.join(BASE, "phase10c_signal_v1.parquet"))
    def test_no_phase11_artifacts(self):
        for f in ["PHASE_11_COST_ANALYSIS.md", "phase11_cost_model.csv"]:
            assert not os.path.isfile(os.path.join(BASE, f)), f"Unexpected: {f}"
