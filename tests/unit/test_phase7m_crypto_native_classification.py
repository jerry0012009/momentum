"""Phase 7M-D: crypto-native diagnostic classification tests."""
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


class TestComparisonOutputs:
    def test_ret_fwd_1h_exists(self):
        assert (RUN / "phase7m_d_static_vs_dynamic_comparison_ret_fwd_1h.csv").exists()

    def test_ret_fwd_1h_6_rows(self):
        df = pd.read_csv(RUN / "phase7m_d_static_vs_dynamic_comparison_ret_fwd_1h.csv")
        assert len(df) == 6

    def test_all_labels_exists(self):
        assert (RUN / "phase7m_d_static_vs_dynamic_comparison_all_labels.csv").exists()

    def test_all_labels_24_rows(self):
        df = pd.read_csv(RUN / "phase7m_d_static_vs_dynamic_comparison_all_labels.csv")
        assert len(df) == 24

    def test_factor_ids(self):
        df = pd.read_csv(RUN / "phase7m_d_static_vs_dynamic_comparison_ret_fwd_1h.csv")
        assert set(df["factor_id"]) == set(ALL_IDS)

    def test_direction_source(self):
        df = pd.read_csv(RUN / "phase7m_d_static_vs_dynamic_comparison_ret_fwd_1h.csv")
        assert (df["direction_source"] == "candidate_csv").all()


class TestClassification:
    def test_exists(self):
        assert (RUN / "phase7m_d_factor_diagnostic_classification.csv").exists()

    def test_6_rows(self):
        df = pd.read_csv(RUN / "phase7m_d_factor_diagnostic_classification.csv")
        assert len(df) == 6

    def test_factor_ids(self):
        df = pd.read_csv(RUN / "phase7m_d_factor_diagnostic_classification.csv")
        assert set(df["factor_id"]) == set(ALL_IDS)

    def test_tiers_valid(self):
        df = pd.read_csv(RUN / "phase7m_d_factor_diagnostic_classification.csv")
        valid_tiers = {"TIER_1_STABLE_DIAGNOSTIC", "TIER_2_PROMISING_BUT_NEEDS_REVIEW",
                       "TIER_3_WEAK_DIAGNOSTIC", "TIER_4_UNSTABLE_OR_SIGN_FLIP"}
        assert set(df["tier"]).issubset(valid_tiers)

    def test_direction_source(self):
        df = pd.read_csv(RUN / "phase7m_d_factor_diagnostic_classification.csv")
        assert (df["direction_source"] == "candidate_csv").all()

    def test_no_alpha_language(self):
        df = pd.read_csv(RUN / "phase7m_d_factor_diagnostic_classification.csv")
        # Check tier and review_flags columns only (notes column contains negative declarations)
        for col in ["tier", "review_flags"]:
            if col in df.columns:
                for val in df[col]:
                    if isinstance(val, str):
                        assert "alpha" not in val.lower()
                        assert "tradeable" not in val.lower()
                        assert "live" not in val.lower()


class TestFamilySummary:
    def test_exists(self):
        assert (RUN / "phase7m_d_family_diagnostic_summary.csv").exists()

    def test_2_families(self):
        df = pd.read_csv(RUN / "phase7m_d_family_diagnostic_summary.csv")
        assert len(df) == 2

    def test_family_names(self):
        df = pd.read_csv(RUN / "phase7m_d_family_diagnostic_summary.csv")
        assert set(df["family"]) == {"taker_imbalance", "funding_rate"}


class TestReviewFlags:
    def test_exists(self):
        assert (RUN / "phase7m_d_review_flags.csv").exists()

    def test_has_flags(self):
        df = pd.read_csv(RUN / "phase7m_d_review_flags.csv")
        assert len(df) > 0

    def test_valid_flags(self):
        df = pd.read_csv(RUN / "phase7m_d_review_flags.csv")
        valid_flags = {"STATIC_DYNAMIC_SIGN_MISMATCH", "EXPECTED_DIRECTION_MISMATCH",
                       "HIGH_TURNOVER", "LOW_COVERAGE", "WEAK_SIGNAL",
                       "MULTI_LABEL_INCONSISTENT", "CLOSEOUT_CSV_MISMATCH_FIXED", "NO_FLAGS"}
        assert set(df["flag"]).issubset(valid_flags)


class TestNoForbiddenOutputs:
    def test_no_backtest_files(self):
        for fid in ALL_IDS:
            bt_dir = ROOT / "data/backtest" / fid
            assert not bt_dir.exists(), f"Unexpected backtest dir: {bt_dir}"

    def test_no_candidate_review_in_closeout(self):
        closeout = RUN / "PHASE_7M_D_CRYPTO_NATIVE_CLASSIFICATION.md"
        if closeout.exists():
            text = closeout.read_text().upper()
            # Exclude sections with negative declarations
            for marker in ["NEGATIVE DECLARATIONS", "F. NEGATIVE", "NO ALPHA CLAIM"]:
                idx = text.find(marker)
                if idx > 0:
                    text = text[:idx]
            for word in ["CANDIDATE_REVIEW", "TRADEABLE", "LIVE", "DEPLOY"]:
                assert word not in text, f"Forbidden word {word} in closeout"
