"""Tests for Phase 10C-R Metric Lineage & Direction Policy Repair."""
import os
import pandas as pd
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
BASE = os.path.join(ROOT, "research", "factor_runs", "crypto_top50_factor_library")

class TestArtifactsExist:
    def test_closeout(self):
        assert os.path.isfile(os.path.join(BASE, "PHASE_10C_R_METRIC_LINEAGE_AND_POLICY_REPAIR.md"))
    def test_metric_lineage(self):
        assert os.path.isfile(os.path.join(BASE, "phase10c_r_metric_lineage.csv"))
    def test_repaired_policy(self):
        assert os.path.isfile(os.path.join(BASE, "phase10c_r_horizon_direction_policy_repaired.csv"))
    def test_repaired_protocol(self):
        assert os.path.isfile(os.path.join(BASE, "phase10c_r_phase10d_protocol_repaired.csv"))
    def test_quality_checks(self):
        assert os.path.isfile(os.path.join(BASE, "phase10c_r_quality_checks.csv"))

class TestMetricLineage:
    @pytest.fixture(autouse=True)
    def load(self):
        self.df = pd.read_csv(os.path.join(BASE, "phase10c_r_metric_lineage.csv"))
    def test_not_empty(self):
        assert len(self.df) > 0
    def test_has_mean_rankic(self):
        assert "mean_rankic" in self.df["metric_name"].values
    def test_has_median_spread(self):
        assert "median_spread" in self.df["metric_name"].values
    def test_has_tail_trim(self):
        assert "tail_trim_spread" in self.df["metric_name"].values
    def test_has_inverted_metrics(self):
        assert "inverted_original_rankic" in self.df["metric_name"].values

class TestRepairedPolicy:
    @pytest.fixture(autouse=True)
    def load(self):
        self.df = pd.read_csv(os.path.join(BASE, "phase10c_r_horizon_direction_policy_repaired.csv"))
    def test_12_rows(self):
        assert len(self.df) == 12
    def test_3_signals(self):
        assert len(self.df["signal_id"].unique()) == 3
    def test_4_horizons(self):
        assert sorted(self.df["horizon"].unique()) == sorted(["1h", "4h", "24h", "72h"])
    def test_all_original_rankic_positive(self):
        for _, row in self.df.iterrows():
            assert row["original_rankic_direction"] == "POSITIVE", \
                f"{row['signal_id']} {row['horizon']}: original_rankic_direction={row['original_rankic_direction']}"
    def test_inverted_separated(self):
        assert "inverted_rankic_direction" in self.df.columns
        assert "inverted_spread_direction" in self.df.columns

class TestRepairedProtocol:
    @pytest.fixture(autouse=True)
    def load(self):
        self.df = pd.read_csv(os.path.join(BASE, "phase10c_r_phase10d_protocol_repaired.csv"))
    def test_48_rows(self):
        assert len(self.df) == 48
    def test_4_variants_per_signal_horizon(self):
        combos = self.df.groupby(["signal_id", "horizon"]).size()
        assert (combos == 4).all()
    def test_variant_types(self):
        variants = set(self.df["direction_variant"].unique())
        assert variants == {"original", "inverted"}
    def test_guard_types(self):
        guards = set(self.df["guard_variant"].unique())
        assert guards == {"no_guard", "bucket0_guard"}

class TestQualityChecks:
    @pytest.fixture(autouse=True)
    def load(self):
        self.df = pd.read_csv(os.path.join(BASE, "phase10c_r_quality_checks.csv"))
    def test_no_fail(self):
        fails = self.df[self.df["status"] == "FAIL"]
        assert fails.empty, f"FAIL: {fails['check_name'].tolist()}"
    def test_canonical_rankic_all_positive(self):
        row = self.df[self.df["check_name"] == "canonical_rankic_all_positive"]
        assert len(row) == 1 and row.iloc[0]["status"] == "PASS"

class TestNoPhase11:
    def test_no_signal_v1_parquet(self):
        assert not os.path.isfile(os.path.join(BASE, "phase10c_signal_v1.parquet"))
    def test_no_phase11_artifacts(self):
        for f in ["PHASE_11_COST_ANALYSIS.md", "phase11_cost_model.csv"]:
            assert not os.path.isfile(os.path.join(BASE, f)), f"Unexpected: {f}"
