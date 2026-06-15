"""Phase 7M-E: crypto-native redundancy diagnostics tests."""
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


class TestPairwiseCorrelation:
    def test_static_exists(self):
        assert (RUN / "phase7m_e_static_pairwise_correlation.csv").exists()

    def test_static_15_rows(self):
        df = pd.read_csv(RUN / "phase7m_e_static_pairwise_correlation.csv")
        assert len(df) == 15

    def test_dynamic_exists(self):
        assert (RUN / "phase7m_e_dynamic_pairwise_correlation.csv").exists()

    def test_dynamic_15_rows(self):
        df = pd.read_csv(RUN / "phase7m_e_dynamic_pairwise_correlation.csv")
        assert len(df) == 15

    def test_no_self_pairs(self):
        df = pd.read_csv(RUN / "phase7m_e_dynamic_pairwise_correlation.csv")
        assert (df["factor_1"] != df["factor_2"]).all()

    def test_unique_pairs(self):
        df = pd.read_csv(RUN / "phase7m_e_dynamic_pairwise_correlation.csv")
        pairs = df.apply(lambda r: tuple(sorted([r["factor_1"], r["factor_2"]])), axis=1)
        assert len(pairs.unique()) == 15

    def test_all_factors_present(self):
        df = pd.read_csv(RUN / "phase7m_e_dynamic_pairwise_correlation.csv")
        all_factors = set(df["factor_1"]) | set(df["factor_2"])
        assert all_factors == set(ALL_IDS)


class TestRedundancyGroups:
    def test_exists(self):
        assert (RUN / "phase7m_e_redundancy_groups.csv").exists()

    def test_has_rows(self):
        df = pd.read_csv(RUN / "phase7m_e_redundancy_groups.csv")
        assert len(df) >= 1


class TestFamilySummary:
    def test_exists(self):
        assert (RUN / "phase7m_e_family_redundancy_summary.csv").exists()

    def test_has_rows(self):
        df = pd.read_csv(RUN / "phase7m_e_family_redundancy_summary.csv")
        assert len(df) >= 3  # taker + funding + cross


class TestNoForbiddenOutputs:
    def test_no_backtest_files(self):
        for fid in ALL_IDS:
            bt_dir = ROOT / "data/backtest" / fid
            assert not bt_dir.exists()

    def test_no_candidate_review_in_closeout(self):
        closeout = RUN / "PHASE_7M_E_CRYPTO_NATIVE_REDUNDANCY.md"
        if closeout.exists():
            text = closeout.read_text().upper()
            # Only check sections A-C (before status/negative declarations)
            idx = text.find("## D.")
            if idx > 0:
                text = text[:idx]
            # "no CANDIDATE_REVIEW" in scope is OK; check for promotion language
            for word in ["CANDIDATE_REVIEW:", "PROMOTED TO", "UPGRADED TO"]:
                assert word not in text, f"Forbidden word {word} in closeout"
