"""Unit tests for factor_mining_candidates_v0_1.csv (Phase 7A).

Validates CSV structure, values, and 7B selection rules.
"""
import pandas as pd
import pytest
from pathlib import Path

RUN = Path(__file__).resolve().parents[2] / "research" / "factor_runs" / "crypto_top50_factor_library"
CSV_PATH = RUN / "factor_mining_candidates_v0_1.csv"

REQUIRED_FAMILIES = [
    "momentum", "reversal", "volatility", "range_position", "price_position",
    "volume_liquidity", "quote_volume_liquidity", "trend_ma", "breakout",
    "intraday_candle", "cross_sectional_normalized",
    "technical_indicators", "wq101_expansion", "alpha158_expansion",
    "realized_skew_kurtosis",
]


@pytest.fixture
def df():
    return pd.read_csv(CSV_PATH)


class TestCSVStructure:
    def test_file_exists(self):
        assert CSV_PATH.exists()

    def test_required_columns(self, df):
        required = [
            "factor_id", "factor_name", "factor_family", "formula_description",
            "required_columns", "lookback_window", "expected_direction",
            "direction_policy", "implementation_complexity", "source",
            "priority_batch", "status", "notes",
        ]
        for col in required:
            assert col in df.columns, f"Missing column: {col}"

    def test_factor_id_unique(self, df):
        assert df["factor_id"].is_unique

    def test_expected_direction_valid(self, df):
        valid = {"positive", "negative", "conditional", "unknown"}
        invalid = set(df["expected_direction"].unique()) - valid
        assert not invalid, f"Invalid expected_direction: {invalid}"

    def test_direction_policy_valid(self, df):
        valid = {"theory_prior", "structural_prior", "conditional_by_design", "unknown"}
        invalid = set(df["direction_policy"].unique()) - valid
        assert not invalid, f"Invalid direction_policy: {invalid}"

    def test_status_valid(self, df):
        valid = {"candidate", "selected_for_7B", "deferred", "rejected"}
        invalid = set(df["status"].unique()) - valid
        assert not invalid, f"Invalid status: {invalid}"

    def test_priority_batch_non_empty(self, df):
        assert df["priority_batch"].notna().all()
        assert (df["priority_batch"] != "").all()

    def test_lookback_window_positive(self, df):
        bad = df[(df["lookback_window"].isna() | (df["lookback_window"] <= 0)) & df["notes"].isna()]
        assert len(bad) == 0, f"Invalid lookback_window without notes: {bad['factor_id'].tolist()}"


class TestFamilyCoverage:
    def test_required_families_present(self, df):
        present = set(df["factor_family"].unique())
        for fam in REQUIRED_FAMILIES:
            assert fam in present, f"Missing family: {fam}"

    def test_each_family_at_least_3(self, df):
        counts = df.groupby("factor_family").size()
        for fam, count in counts.items():
            assert count >= 3, f"Family {fam} has only {count} candidates"


class Test7BSelection:
    def test_7b_count_between_20_and_30(self, df):
        """7B must have between 20 and 30 factors (PM acceptance criterion)."""
        selected = df[df["status"] == "selected_for_7B"]
        assert 20 <= len(selected) <= 30, f"7B has {len(selected)} factors, must be 20-30"

    def test_7b_covers_at_least_6_families(self, df):
        selected = df[df["status"] == "selected_for_7B"]
        families = selected["factor_family"].nunique()
        assert families >= 6, f"7B covers only {families} families"

    def test_7b_all_have_valid_direction(self, df):
        selected = df[df["status"] == "selected_for_7B"]
        valid = {"positive", "negative", "conditional", "unknown"}
        invalid = set(selected["expected_direction"].unique()) - valid
        assert not invalid, f"7B has invalid direction: {invalid}"


class TestAntiSnoopingDesign:
    def test_no_evaluation_driven_direction(self, df):
        """No candidate should have direction_policy = 'empirical' or 'evaluation'."""
        forbidden = {"empirical", "evaluation", "backtest", "data_driven"}
        found = set(df["direction_policy"].unique()) & forbidden
        assert not found, f"Forbidden direction_policy found: {found}"

    def test_all_factors_are_probe_status(self, df):
        """No factor should have status suggesting alpha."""
        forbidden = {"alpha", "live", "deployed", "shadow"}
        found = set(df["status"].unique()) & forbidden
        assert not found, f"Forbidden status found: {found}"
