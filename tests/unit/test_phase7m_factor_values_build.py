"""Phase 7M-B: crypto-native factor_values build tests."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
REPORT = ROOT / "research/factor_runs/crypto_top50_factor_library"

TAKER_IDS = ["taker_buy_ratio_20h", "taker_buy_zscore_20h", "taker_buy_delta_5h"]
FUNDING_IDS = ["funding_rate_level_20h", "funding_rate_zscore_80h", "funding_rate_change_24h"]
ALL_IDS = TAKER_IDS + FUNDING_IDS

STATIC_ID = "crypto_top50_usdt_perp_1h_crypto_native_v1"
DYNAMIC_ID = "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1_crypto_native_v1"


class TestJoinSummary:
    def test_join_summary_exists(self):
        assert (REPORT / "phase7m_b_crypto_native_dataset_join_summary.csv").exists()

    def test_join_summary_2_rows(self):
        df = pd.read_csv(REPORT / "phase7m_b_crypto_native_dataset_join_summary.csv")
        assert len(df) == 2

    def test_row_count_match(self):
        df = pd.read_csv(REPORT / "phase7m_b_crypto_native_dataset_join_summary.csv")
        assert df["row_count_match"].all()

    def test_variants(self):
        df = pd.read_csv(REPORT / "phase7m_b_crypto_native_dataset_join_summary.csv")
        assert set(df["dataset_variant"]) == {"static", "dynamic"}


class TestStaticBuildSummary:
    def test_exists(self):
        assert (REPORT / "phase7m_b_static_factor_values_build_summary.csv").exists()

    def test_6_rows(self):
        df = pd.read_csv(REPORT / "phase7m_b_static_factor_values_build_summary.csv")
        assert len(df) == 6

    def test_only_7ma_factors(self):
        df = pd.read_csv(REPORT / "phase7m_b_static_factor_values_build_summary.csv")
        assert set(df["factor_id"]) == set(ALL_IDS)

    def test_gate_valid(self):
        df = pd.read_csv(REPORT / "phase7m_b_static_factor_values_build_summary.csv")
        assert set(df["gate"]).issubset({"PASS", "PARTIAL", "FAIL"})

    def test_dataset_id(self):
        df = pd.read_csv(REPORT / "phase7m_b_static_factor_values_build_summary.csv")
        assert (df["dataset_id"] == STATIC_ID).all()


class TestDynamicBuildSummary:
    def test_exists(self):
        assert (REPORT / "phase7m_b_dynamic_factor_values_build_summary.csv").exists()

    def test_6_rows(self):
        df = pd.read_csv(REPORT / "phase7m_b_dynamic_factor_values_build_summary.csv")
        assert len(df) == 6

    def test_only_7ma_factors(self):
        df = pd.read_csv(REPORT / "phase7m_b_dynamic_factor_values_build_summary.csv")
        assert set(df["factor_id"]) == set(ALL_IDS)

    def test_gate_valid(self):
        df = pd.read_csv(REPORT / "phase7m_b_dynamic_factor_values_build_summary.csv")
        assert set(df["gate"]).issubset({"PASS", "PARTIAL", "FAIL"})


class TestFactorValuesSchema:
    @pytest.mark.parametrize("factor_id", ALL_IDS)
    def test_static_schema(self, factor_id):
        path = ROOT / f"data/features/{STATIC_ID}/{factor_id}/factor_values.parquet"
        assert path.exists(), f"Missing {path}"
        df = pd.read_parquet(path)
        for col in ["timestamp", "symbol", "factor_name", "factor_value",
                     "known_at", "source_timeframe", "computed_at"]:
            assert col in df.columns, f"Missing column {col} in {factor_id}"

    @pytest.mark.parametrize("factor_id", ALL_IDS)
    def test_dynamic_schema(self, factor_id):
        path = ROOT / f"data/features/{DYNAMIC_ID}/{factor_id}/factor_values.parquet"
        assert path.exists(), f"Missing {path}"
        df = pd.read_parquet(path)
        for col in ["timestamp", "symbol", "factor_name", "factor_value",
                     "known_at", "source_timeframe", "computed_at"]:
            assert col in df.columns, f"Missing column {col} in {factor_id}"

    @pytest.mark.parametrize("factor_id", ALL_IDS)
    def test_factor_name_matches(self, factor_id):
        path = ROOT / f"data/features/{STATIC_ID}/{factor_id}/factor_values.parquet"
        df = pd.read_parquet(path)
        assert (df["factor_name"] == factor_id).all()


class TestCombinedBars:
    def test_static_combined_exists(self):
        path = ROOT / "data/cache/crypto_top50_usdt_perp_1h_crypto_native_v1/bars_1h.parquet"
        assert path.exists()

    def test_dynamic_combined_exists(self):
        path = ROOT / "data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1_crypto_native_v1/bars_1h.parquet"
        assert path.exists()

    def test_static_has_required_columns(self):
        df = pd.read_parquet(ROOT / "data/cache/crypto_top50_usdt_perp_1h_crypto_native_v1/bars_1h.parquet")
        for col in ["timestamp", "symbol", "taker_buy_quote_volume", "funding_rate"]:
            assert col in df.columns


class TestNoForbiddenOutputs:
    def test_no_eval_files(self):
        """No evaluation output files should exist for 7M-B factors."""
        for fid in ALL_IDS:
            eval_dir = ROOT / "data/eval" / STATIC_ID / fid
            assert not eval_dir.exists(), f"Unexpected eval dir: {eval_dir}"

    def test_no_backtest_files(self):
        for fid in ALL_IDS:
            bt_dir = ROOT / "data/backtest" / fid
            assert not bt_dir.exists(), f"Unexpected backtest dir: {bt_dir}"

    def test_no_forbidden_language(self):
        """Closeout should not contain forbidden terms."""
        closeout = REPORT / "PHASE_7M_B_CRYPTO_NATIVE_FACTOR_VALUES.md"
        if closeout.exists():
            text = closeout.read_text().upper()
            for word in ["CANDIDATE_REVIEW", "ALPHA", "TRADEABLE", "LIVE", "DEPLOY"]:
                assert word not in text, f"Forbidden word {word} in closeout"
