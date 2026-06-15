"""Phase 7N-R: readiness queue & documentation repair tests."""
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

KNOWN_CLEAN_T1 = {
    "vol_5h", "vol_40h", "range_1h", "range_4h", "price_pos_24h",
    "xs_rank_vol", "rsi_28h", "rsi_7h", "downside_vol_20h", "vol_of_vol_20h",
}


class TestRoadmapState:
    def test_7n_complete(self):
        roadmap = ROOT / "docs/FACTOR_LIBRARY_ROADMAP.md"
        text = roadmap.read_text()
        assert "Phase 7N" in text and "COMPLETE" in text

    def test_phase8_not_started(self):
        roadmap = ROOT / "docs/FACTOR_LIBRARY_ROADMAP.md"
        text = roadmap.read_text().upper()
        assert "PHASE 8 IS NOT STARTED" in text or "PHASE 8 NOT STARTED" in text or "PENDING PM" in text

    def test_no_candidate_review_in_roadmap(self):
        roadmap = ROOT / "docs/FACTOR_LIBRARY_ROADMAP.md"
        text = roadmap.read_text().upper()
        # Check section 6 only (next phase section)
        idx6 = text.find("## 6.")
        idx7 = text.find("## 7.")
        if idx6 > 0 and idx7 > 0:
            section6 = text[idx6:idx7]
            # "No factor has entered CANDIDATE_REVIEW" is a negative declaration, OK
            # Check that CANDIDATE_REVIEW doesn't appear as a status or promotion
            for line in section6.split("\n"):
                if "CANDIDATE_REVIEW" in line and "NO" not in line and "NOT" not in line and "NEVER" not in line:
                    assert False, f"CANDIDATE_REVIEW appears as positive status: {line}"


class TestDocsIndexState:
    def test_7n_complete(self):
        docs = ROOT / "docs/DOCS_INDEX.md"
        text = docs.read_text()
        assert "Phase 7N" in text and "complete" in text.lower()


class TestReviewQueueRepaired:
    def test_exists(self):
        assert (RUN / "phase7n_r_phase8_review_queue_repaired.csv").exists()

    def test_42_rows(self):
        df = pd.read_csv(RUN / "phase7n_r_phase8_review_queue_repaired.csv")
        assert len(df) == 42

    def test_no_candidate_review(self):
        df = pd.read_csv(RUN / "phase7n_r_phase8_review_queue_repaired.csv")
        for _, r in df.iterrows():
            assert "CANDIDATE_REVIEW" not in str(r["phase8_queue_category"]).upper()

    def test_no_alpha_language(self):
        df = pd.read_csv(RUN / "phase7n_r_phase8_review_queue_repaired.csv")
        for col in ["phase8_queue_category", "phase8_notes"]:
            vals = df[col].astype(str).str.upper()
            for v in vals:
                for word in ["ALPHA", "TRADEABLE", "LIVE", "DEPLOY"]:
                    assert word not in v

    def test_ready_for_human_review_exists(self):
        df = pd.read_csv(RUN / "phase7n_r_phase8_review_queue_repaired.csv")
        ready = df[df["phase8_queue_category"] == "PHASE8_READY_FOR_HUMAN_REVIEW"]
        assert len(ready) >= 1

    def test_ready_not_tier3_or_4(self):
        df = pd.read_csv(RUN / "phase7n_r_phase8_review_queue_repaired.csv")
        ready = df[df["phase8_queue_category"] == "PHASE8_READY_FOR_HUMAN_REVIEW"]
        for _, r in ready.iterrows():
            tier = str(r["diagnostic_tier"])
            assert "TIER_3" not in tier
            assert "TIER_4" not in tier

    def test_ready_no_bad_flags(self):
        df = pd.read_csv(RUN / "phase7n_r_phase8_review_queue_repaired.csv")
        ready = df[df["phase8_queue_category"] == "PHASE8_READY_FOR_HUMAN_REVIEW"]
        for _, r in ready.iterrows():
            flags = str(r["review_flags"]).upper()
            for bad in ["DIRECTION_MISMATCH", "EXPECTED_DIRECTION_MISMATCH", "WEAK_SIGNAL", "HIGH_TURNOVER"]:
                assert bad not in flags, f"{r['factor_id']} has {bad} in READY queue"

    def test_clean_t1_not_in_redundancy(self):
        df = pd.read_csv(RUN / "phase7n_r_phase8_review_queue_repaired.csv")
        for _, r in df.iterrows():
            fid = r["factor_id"]
            if fid in KNOWN_CLEAN_T1:
                assert r["phase8_queue_category"] != "REDUNDANCY_REVIEW_FIRST", \
                    f"{fid} is clean TIER_1 but assigned to REDUNDANCY_REVIEW_FIRST"

    def test_valid_categories(self):
        df = pd.read_csv(RUN / "phase7n_r_phase8_review_queue_repaired.csv")
        valid = {
            "PHASE8_READY_FOR_HUMAN_REVIEW",
            "REVIEW_DIRECTION_FIRST",
            "REDUNDANCY_REVIEW_FIRST",
            "WEAK_OR_LOW_PRIORITY",
            "DIAGNOSTIC_BASELINE_ONLY",
        }
        for _, r in df.iterrows():
            assert r["phase8_queue_category"] in valid


class TestV04Audit:
    def test_42_rows(self):
        df = pd.read_csv(RUN / "phase7n_v04_library_audit_summary.csv")
        assert len(df) == 42

    def test_unique_ids(self):
        df = pd.read_csv(RUN / "phase7n_v04_library_audit_summary.csv")
        assert df["factor_id"].is_unique


class TestNoForbiddenOutputs:
    def test_no_backtest_files(self):
        for fid in ALL_IDS:
            bt_dir = ROOT / "data/backtest" / fid
            assert not bt_dir.exists()
