"""Phase 7N: v0.4 library audit tests."""
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


class TestV04LibraryAudit:
    def test_exists(self):
        assert (RUN / "phase7n_v04_library_audit_summary.csv").exists()

    def test_42_rows(self):
        df = pd.read_csv(RUN / "phase7n_v04_library_audit_summary.csv")
        assert len(df) == 42

    def test_unique_ids(self):
        df = pd.read_csv(RUN / "phase7n_v04_library_audit_summary.csv")
        assert df["factor_id"].is_unique

    def test_crypto_native_present(self):
        df = pd.read_csv(RUN / "phase7n_v04_library_audit_summary.csv")
        for fid in ALL_IDS:
            assert fid in df["factor_id"].values

    def test_15_families(self):
        df = pd.read_csv(RUN / "phase7n_v04_library_audit_summary.csv")
        assert df["factor_family"].nunique() == 15


class TestFamilyReadiness:
    def test_exists(self):
        assert (RUN / "phase7n_family_readiness_summary.csv").exists()

    def test_15_families(self):
        df = pd.read_csv(RUN / "phase7n_family_readiness_summary.csv")
        assert len(df) == 15

    def test_new_families_present(self):
        df = pd.read_csv(RUN / "phase7n_family_readiness_summary.csv")
        assert "taker_imbalance" in df["family"].values
        assert "funding_rate" in df["family"].values


class TestPhase8ReviewQueue:
    def test_exists(self):
        assert (RUN / "phase7n_phase8_review_queue.csv").exists()

    def test_42_rows(self):
        df = pd.read_csv(RUN / "phase7n_phase8_review_queue.csv")
        assert len(df) == 42

    def test_no_candidate_review(self):
        df = pd.read_csv(RUN / "phase7n_phase8_review_queue.csv")
        for _, r in df.iterrows():
            assert "CANDIDATE_REVIEW" not in str(r["phase8_queue_category"]).upper()

    def test_valid_categories(self):
        df = pd.read_csv(RUN / "phase7n_phase8_review_queue.csv")
        valid = {
            "PHASE8_READY_FOR_HUMAN_REVIEW",
            "REVIEW_DIRECTION_FIRST",
            "REDUNDANCY_REVIEW_FIRST",
            "WEAK_OR_LOW_PRIORITY",
            "DIAGNOSTIC_BASELINE_ONLY",
        }
        for _, r in df.iterrows():
            assert r["phase8_queue_category"] in valid


class TestBlockers:
    def test_exists(self):
        assert (RUN / "phase7n_blockers_and_constraints.csv").exists()

    def test_has_blockers(self):
        df = pd.read_csv(RUN / "phase7n_blockers_and_constraints.csv")
        assert len(df) >= 5


class TestNoForbiddenOutputs:
    def test_no_backtest_files(self):
        for fid in ALL_IDS:
            bt_dir = ROOT / "data/backtest" / fid
            assert not bt_dir.exists()

    def test_no_alpha_in_audit(self):
        df = pd.read_csv(RUN / "phase7n_v04_library_audit_summary.csv")
        for col in ["diagnostic_tier", "recommended_research_use", "redundancy_status"]:
            vals = df[col].astype(str).str.upper()
            for v in vals:
                for word in ["ALPHA", "TRADEABLE", "LIVE", "DEPLOY"]:
                    assert word not in v


class TestRoadmapConsistency:
    def test_v04_mentioned(self):
        roadmap = ROOT / "docs/FACTOR_LIBRARY_ROADMAP.md"
        if roadmap.exists():
            text = roadmap.read_text()
            assert "v0.4" in text
            assert "42" in text

    def test_7n_next_phase(self):
        roadmap = ROOT / "docs/FACTOR_LIBRARY_ROADMAP.md"
        if roadmap.exists():
            text = roadmap.read_text()
            assert "7N" in text
