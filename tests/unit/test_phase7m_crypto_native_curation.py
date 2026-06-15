"""Phase 7M-F: crypto-native curation tests."""
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


class TestCryptoNativeLibrary:
    def test_exists(self):
        assert (RUN / "phase7m_f_curated_crypto_native_library.csv").exists()

    def test_6_rows(self):
        df = pd.read_csv(RUN / "phase7m_f_curated_crypto_native_library.csv")
        assert len(df) == 6

    def test_factor_ids(self):
        df = pd.read_csv(RUN / "phase7m_f_curated_crypto_native_library.csv")
        assert set(df["factor_id"]) == set(ALL_IDS)


class TestV04Library:
    def test_exists(self):
        assert (RUN / "phase7m_f_curated_factor_library_v0_4.csv").exists()

    def test_row_count(self):
        v03 = pd.read_csv(RUN / "phase7i_e_curated_factor_library_v0_3.csv")
        v04 = pd.read_csv(RUN / "phase7m_f_curated_factor_library_v0_4.csv")
        assert len(v04) == len(v03) + 6

    def test_no_duplicate_ids(self):
        df = pd.read_csv(RUN / "phase7m_f_curated_factor_library_v0_4.csv")
        assert df["factor_id"].is_unique

    def test_crypto_native_present(self):
        df = pd.read_csv(RUN / "phase7m_f_curated_factor_library_v0_4.csv")
        for fid in ALL_IDS:
            assert fid in df["factor_id"].values

    def test_all_diagnostic_only(self):
        df = pd.read_csv(RUN / "phase7m_f_curated_factor_library_v0_4.csv")
        cn = df[df["factor_type"] == "crypto_native"]
        for _, r in cn.iterrows():
            tier = str(r["diagnostic_tier"])
            assert "DIAGNOSTIC" in tier or "TIER" in tier

    def test_no_alpha_language(self):
        df = pd.read_csv(RUN / "phase7m_f_curated_factor_library_v0_4.csv")
        cn = df[df["factor_type"] == "crypto_native"]
        for col in ["diagnostic_tier", "recommended_research_use", "redundancy_status"]:
            vals = cn[col].astype(str).str.upper()
            for v in vals:
                for word in ["ALPHA", "TRADEABLE", "LIVE", "DEPLOY"]:
                    assert word not in v


class TestFamilyCatalog:
    def test_exists(self):
        assert (RUN / "phase7m_f_family_catalog_summary_v0_4.csv").exists()

    def test_includes_new_families(self):
        df = pd.read_csv(RUN / "phase7m_f_family_catalog_summary_v0_4.csv")
        families = set(df["family"])
        assert "taker_imbalance" in families
        assert "funding_rate" in families

    def test_family_count(self):
        df = pd.read_csv(RUN / "phase7m_f_family_catalog_summary_v0_4.csv")
        assert len(df) >= 15  # 13 existing + 2 new


class TestRedundancyQueue:
    def test_exists(self):
        assert (RUN / "phase7m_f_redundancy_review_queue_v0_4.csv").exists()

    def test_row_count(self):
        v03 = pd.read_csv(RUN / "phase7i_e_redundancy_review_queue_v0_3.csv")
        v04 = pd.read_csv(RUN / "phase7m_f_redundancy_review_queue_v0_4.csv")
        assert len(v04) == len(v03) + 2

    def test_no_deletion_label(self):
        df = pd.read_csv(RUN / "phase7m_f_redundancy_review_queue_v0_4.csv")
        for _, r in df.iterrows():
            label = str(r.get("recommended_review", "")).upper()
            assert "DELETE" not in label
            assert "REMOVE" not in label


class TestNoForbiddenOutputs:
    def test_no_backtest_files(self):
        for fid in ALL_IDS:
            bt_dir = ROOT / "data/backtest" / fid
            assert not bt_dir.exists()
