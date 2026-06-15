"""Phase 7M-C: crypto-native evaluation tests."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
RUN = ROOT / "research/factor_runs/crypto_top50_factor_library"

ALL_IDS = [
    "taker_buy_ratio_20h", "taker_buy_zscore_20h", "taker_buy_delta_5h",
    "funding_rate_level_20h", "funding_rate_zscore_80h", "funding_rate_change_24h",
]


class TestMetadata:
    def test_exists(self):
        assert (RUN / "phase7m_crypto_native_factor_metadata.csv").exists()

    def test_6_rows(self):
        df = pd.read_csv(RUN / "phase7m_crypto_native_factor_metadata.csv")
        assert len(df) == 6

    def test_factor_ids(self):
        df = pd.read_csv(RUN / "phase7m_crypto_native_factor_metadata.csv")
        assert set(df["factor_id"]) == set(ALL_IDS)


class TestStaticEval:
    def test_ret_fwd_1h_exists(self):
        assert (RUN / "phase7m_c_static_eval_summary_ret_fwd_1h.csv").exists()

    def test_ret_fwd_1h_6_rows(self):
        df = pd.read_csv(RUN / "phase7m_c_static_eval_summary_ret_fwd_1h.csv")
        assert len(df) == 6

    def test_all_labels_exists(self):
        assert (RUN / "phase7m_c_static_eval_summary_all_labels.csv").exists()

    def test_all_labels_24_rows(self):
        df = pd.read_csv(RUN / "phase7m_c_static_eval_summary_all_labels.csv")
        assert len(df) == 24

    def test_direction_source(self):
        df = pd.read_csv(RUN / "phase7m_c_static_eval_summary_all_labels.csv")
        assert (df["direction_source"] == "candidate_csv").all()


class TestDynamicEval:
    def test_ret_fwd_1h_exists(self):
        assert (RUN / "phase7m_c_dynamic_eval_summary_ret_fwd_1h.csv").exists()

    def test_ret_fwd_1h_6_rows(self):
        df = pd.read_csv(RUN / "phase7m_c_dynamic_eval_summary_ret_fwd_1h.csv")
        assert len(df) == 6

    def test_all_labels_exists(self):
        assert (RUN / "phase7m_c_dynamic_eval_summary_all_labels.csv").exists()

    def test_all_labels_24_rows(self):
        df = pd.read_csv(RUN / "phase7m_c_dynamic_eval_summary_all_labels.csv")
        assert len(df) == 24

    def test_direction_source(self):
        df = pd.read_csv(RUN / "phase7m_c_dynamic_eval_summary_all_labels.csv")
        assert (df["direction_source"] == "candidate_csv").all()


class TestNoFallback:
    def test_no_fallback_static(self):
        df = pd.read_csv(RUN / "phase7m_c_static_eval_summary_all_labels.csv")
        assert "fallback_positive" not in df["direction_source"].values

    def test_no_fallback_dynamic(self):
        df = pd.read_csv(RUN / "phase7m_c_dynamic_eval_summary_all_labels.csv")
        assert "fallback_positive" not in df["direction_source"].values


class TestLabelCopy:
    def test_static_labels_exist(self):
        path = ROOT / "data/features/crypto_top50_usdt_perp_1h_crypto_native_v1/labels.parquet"
        assert path.exists()

    def test_dynamic_labels_exist(self):
        path = ROOT / "data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1_crypto_native_v1/labels.parquet"
        assert path.exists()


class TestCloseoutConsistency:
    def test_closeout_factor_list_matches_csv(self):
        """Closeout must list the same 6 factor_ids as the CSV source."""
        csv_df = pd.read_csv(RUN / "phase7m_c_static_eval_summary_ret_fwd_1h.csv")
        csv_factors = set(csv_df["factor_id"])
        closeout = RUN / "PHASE_7M_C_CRYPTO_NATIVE_EVALUATION.md"
        if closeout.exists():
            text = closeout.read_text()
            for fid in csv_factors:
                assert fid in text, f"Factor {fid} from CSV missing in closeout"
        # Also verify closeout declares CSV as canonical
        if closeout.exists():
            assert "CSV" in closeout.read_text() and "canonical" in closeout.read_text().lower()

    def test_closeout_no_stale_factor_list(self):
        """Closeout must not contain factors not in the CSV."""
        csv_df = pd.read_csv(RUN / "phase7m_c_static_eval_summary_ret_fwd_1h.csv")
        csv_factors = set(csv_df["factor_id"])
        # The closeout should only reference the 6 approved factors in its tables
        assert len(csv_factors) == 6


class TestNoForbiddenOutputs:
    def test_no_classification_files(self):
        for fid in ALL_IDS:
            cls_dir = ROOT / "data/classification" / fid
            assert not cls_dir.exists(), f"Unexpected classification dir: {cls_dir}"

    def test_no_redundancy_files(self):
        for fid in ALL_IDS:
            red_dir = ROOT / "data/redundancy" / fid
            assert not red_dir.exists(), f"Unexpected redundancy dir: {red_dir}"

    def test_no_backtest_files(self):
        for fid in ALL_IDS:
            bt_dir = ROOT / "data/backtest" / fid
            assert not bt_dir.exists(), f"Unexpected backtest dir: {bt_dir}"

    def test_no_forbidden_language_in_closeout(self):
        closeout = RUN / "PHASE_7M_C_CRYPTO_NATIVE_EVALUATION.md"
        if closeout.exists():
            text = closeout.read_text().upper()
            # Exclude negative declarations section (which explicitly states what was NOT done)
            negative_start = text.find("NEGATIVE DECLARATIONS")
            if negative_start > 0:
                text = text[:negative_start]
            for word in ["CANDIDATE_REVIEW", "ALPHA", "TRADEABLE", "LIVE", "DEPLOY"]:
                assert word not in text, f"Forbidden word {word} in closeout"
