"""Phase 7M-D-R: crypto-native diagnostic classification repair tests."""
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
METADATA = RUN / "phase7m_crypto_native_factor_metadata.csv"


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


class TestAllLabelMergeIntegrity:
    """Verify all-label comparison merges on (factor_id, label), not just factor_id."""

    def test_static_rankic_matches_source(self):
        """Static RankIC in comparison must equal source CSV per (factor_id, label)."""
        comp = pd.read_csv(RUN / "phase7m_d_static_vs_dynamic_comparison_all_labels.csv")
        src = pd.read_csv(RUN / "phase7m_c_static_eval_summary_all_labels.csv")
        merged = comp.merge(src, on=["factor_id", "label"], suffixes=("_comp", "_src"))
        pd.testing.assert_series_equal(
            merged["static_RankIC_mean"], merged["RankIC_mean"],
            check_names=False, atol=1e-10,
        )

    def test_dynamic_rankic_matches_source(self):
        """Dynamic RankIC in comparison must equal source CSV per (factor_id, label)."""
        comp = pd.read_csv(RUN / "phase7m_d_static_vs_dynamic_comparison_all_labels.csv")
        src = pd.read_csv(RUN / "phase7m_c_dynamic_eval_summary_all_labels.csv")
        merged = comp.merge(src, on=["factor_id", "label"], suffixes=("_comp", "_src"))
        pd.testing.assert_series_equal(
            merged["dynamic_RankIC_mean"], merged["RankIC_mean"],
            check_names=False, atol=1e-10,
        )

    def test_dynamic_non_1h_not_repeated(self):
        """Dynamic RankIC for non-1h labels must differ from ret_fwd_1h (unless genuinely equal)."""
        comp = pd.read_csv(RUN / "phase7m_d_static_vs_dynamic_comparison_all_labels.csv")
        src = pd.read_csv(RUN / "phase7m_c_dynamic_eval_summary_all_labels.csv")
        for fid in ALL_IDS:
            src_fid = src[src["factor_id"] == fid].set_index("label")["RankIC_mean"]
            if src_fid["ret_fwd_1h"] != src_fid["ret_fwd_4h"]:
                comp_fid = comp[comp["factor_id"] == fid].set_index("label")["dynamic_RankIC_mean"]
                assert comp_fid["ret_fwd_4h"] == src_fid["ret_fwd_4h"], (
                    f"{fid}: dynamic ret_fwd_4h mismatch — likely repeated ret_fwd_1h")

    def test_ret_fwd_1h_subset_matches(self):
        """ret_fwd_1h comparison must equal all-label subset."""
        comp_1h = pd.read_csv(RUN / "phase7m_d_static_vs_dynamic_comparison_ret_fwd_1h.csv")
        comp_all = pd.read_csv(RUN / "phase7m_d_static_vs_dynamic_comparison_all_labels.csv")
        subset = comp_all[comp_all["label"] == "ret_fwd_1h"].reset_index(drop=True)
        for col in ["static_RankIC_mean", "dynamic_RankIC_mean", "factor_id"]:
            assert list(comp_1h[col]) == list(subset[col]), f"Mismatch in {col}"


class TestClassification:
    def test_exists(self):
        assert (RUN / "phase7m_d_factor_diagnostic_classification.csv").exists()

    def test_6_rows(self):
        df = pd.read_csv(RUN / "phase7m_d_factor_diagnostic_classification.csv")
        assert len(df) == 6

    def test_factor_ids_match_metadata(self):
        df = pd.read_csv(RUN / "phase7m_d_factor_diagnostic_classification.csv")
        meta = pd.read_csv(METADATA)
        assert set(df["factor_id"]) == set(meta["factor_id"])

    def test_tiers_valid(self):
        df = pd.read_csv(RUN / "phase7m_d_factor_diagnostic_classification.csv")
        valid_tiers = {"TIER_1_STABLE_DIAGNOSTIC", "TIER_2_PROMISING_BUT_NEEDS_REVIEW",
                       "TIER_3_WEAK_DIAGNOSTIC", "TIER_4_UNSTABLE_OR_SIGN_FLIP"}
        assert set(df["tier"]).issubset(valid_tiers)

    def test_direction_source(self):
        df = pd.read_csv(RUN / "phase7m_d_factor_diagnostic_classification.csv")
        assert (df["direction_source"] == "candidate_csv").all()

    def test_no_alpha_in_tier_or_flags(self):
        df = pd.read_csv(RUN / "phase7m_d_factor_diagnostic_classification.csv")
        for col in ["tier", "review_flags"]:
            for val in df[col]:
                if isinstance(val, str):
                    assert "alpha" not in val.lower()
                    assert "tradeable" not in val.lower()
                    assert "live" not in val.lower()
                    assert "deploy" not in val.lower()
                    assert "candidate_review" not in val.lower()


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
        for name in ["PHASE_7M_D_CRYPTO_NATIVE_CLASSIFICATION.md",
                      "PHASE_7M_D_R_CLASSIFICATION_REPAIR.md"]:
            closeout = RUN / name
            if closeout.exists():
                text = closeout.read_text().upper()
                for marker in ["NEGATIVE DECLARATIONS", "NEGATIVE DECLARATIONS", "NO ALPHA CLAIM"]:
                    idx = text.find(marker)
                    if idx > 0:
                        text = text[:idx]
                for word in ["CANDIDATE_REVIEW", "TRADEABLE", "LIVE", "DEPLOY"]:
                    assert word not in text, f"Forbidden word {word} in {name}"
