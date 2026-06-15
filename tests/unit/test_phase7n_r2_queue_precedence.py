"""Phase 7N-R2: queue category precedence tests."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
RUN = ROOT / "research/factor_runs/crypto_top50_factor_library"


class TestQueuePrecedence:
    """Test that category precedence is correct in the repaired queue."""

    @pytest.fixture(autouse=True)
    def load(self):
        self.df = pd.read_csv(RUN / "phase7n_r2_phase8_review_queue_repaired.csv")
        self.summary = pd.read_csv(RUN / "phase7n_r2_queue_category_summary.csv")

    def test_42_rows(self):
        assert len(self.df) == 42

    def test_ready_exists(self):
        ready = self.df[self.df["phase8_queue_category"] == "PHASE8_READY_FOR_HUMAN_REVIEW"]
        assert len(ready) >= 1

    def test_ready_is_tier1_core(self):
        ready = self.df[self.df["phase8_queue_category"] == "PHASE8_READY_FOR_HUMAN_REVIEW"]
        for _, r in ready.iterrows():
            assert "TIER_1" in str(r["diagnostic_tier"]), f"{r['factor_id']} not TIER_1"
            assert "CORE_DIAGNOSTIC" in str(r["recommended_research_use"]), f"{r['factor_id']} not CORE"

    def test_ready_no_bad_flags(self):
        ready = self.df[self.df["phase8_queue_category"] == "PHASE8_READY_FOR_HUMAN_REVIEW"]
        for _, r in ready.iterrows():
            flags = str(r["review_flags"]).upper()
            for bad in ["DIRECTION_MISMATCH", "EXPECTED_DIRECTION_MISMATCH", "WEAK_SIGNAL", "HIGH_TURNOVER"]:
                assert bad not in flags, f"{r['factor_id']} has {bad}"

    def test_weak_includes_low_priority(self):
        weak = self.df[self.df["phase8_queue_category"] == "WEAK_OR_LOW_PRIORITY"]
        fids = set(weak["factor_id"])
        # PM specified these must be WEAK_OR_LOW_PRIORITY
        for must_be in ["funding_rate_change_24h", "qvol_ma_ratio_5_20", "ma_gap_20_80",
                        "vol_ratio_5_20", "taker_buy_delta_5h", "funding_rate_zscore_80h"]:
            assert must_be in fids, f"{must_be} should be WEAK_OR_LOW_PRIORITY"

    def test_all_low_priority_research_in_weak(self):
        """All LOW_PRIORITY_RESEARCH factors must be WEAK_OR_LOW_PRIORITY."""
        for _, r in self.df.iterrows():
            if "LOW_PRIORITY" in str(r["recommended_research_use"]):
                assert r["phase8_queue_category"] == "WEAK_OR_LOW_PRIORITY", \
                    f"{r['factor_id']} is LOW_PRIORITY_RESEARCH but {r['phase8_queue_category']}"

    def test_all_weak_diagnostic_in_weak(self):
        """All WEAK_DIAGNOSTIC_ONLY factors must be WEAK_OR_LOW_PRIORITY."""
        for _, r in self.df.iterrows():
            if "WEAK_DIAGNOSTIC" in str(r["recommended_research_use"]):
                assert r["phase8_queue_category"] == "WEAK_OR_LOW_PRIORITY", \
                    f"{r['factor_id']} is WEAK_DIAGNOSTIC_ONLY but {r['phase8_queue_category']}"

    def test_funding_change_not_direction_first(self):
        row = self.df[self.df["factor_id"] == "funding_rate_change_24h"]
        assert len(row) == 1
        assert row.iloc[0]["phase8_queue_category"] != "REVIEW_DIRECTION_FIRST"

    def test_no_candidate_review(self):
        for _, r in self.df.iterrows():
            assert "CANDIDATE_REVIEW" not in str(r["phase8_queue_category"]).upper()

    def test_no_alpha_language(self):
        for col in ["phase8_queue_category", "phase8_notes"]:
            vals = self.df[col].astype(str).str.upper()
            for v in vals:
                for word in ["ALPHA", "TRADEABLE", "LIVE", "DEPLOY"]:
                    assert word not in v

    def test_valid_categories(self):
        valid = {
            "PHASE8_READY_FOR_HUMAN_REVIEW",
            "REVIEW_DIRECTION_FIRST",
            "REDUNDANCY_REVIEW_FIRST",
            "WEAK_OR_LOW_PRIORITY",
            "DIAGNOSTIC_BASELINE_ONLY",
        }
        for _, r in self.df.iterrows():
            assert r["phase8_queue_category"] in valid

    def test_category_counts_match_summary(self):
        """Category counts in summary CSV must match queue CSV."""
        for _, s in self.summary.iterrows():
            cat = s["category"]
            expected = s["count"]
            actual = len(self.df[self.df["phase8_queue_category"] == cat])
            assert actual == expected, f"{cat}: summary={expected}, actual={actual}"


class TestCloseoutConsistency:
    def test_closeout_counts_match_csv(self):
        closeout = RUN / "PHASE_7N_R2_READINESS_QUEUE_REPAIR.md"
        if closeout.exists():
            summary = pd.read_csv(RUN / "phase7n_r2_queue_category_summary.csv")
            text = closeout.read_text()
            for _, s in summary.iterrows():
                cat = s["category"]
                count = str(s["count"])
                assert count in text, f"Count {count} for {cat} not in closeout"

    def test_no_candidate_review_in_closeout(self):
        closeout = RUN / "PHASE_7N_R2_READINESS_QUEUE_REPAIR.md"
        if closeout.exists():
            text = closeout.read_text().upper()
            # Check body (before negative declarations)
            for marker in ["## D.", "## E."]:
                idx = text.find(marker)
                if idx > 0:
                    body = text[:idx]
                    break
            else:
                body = text
            # "not CANDIDATE_REVIEW" is OK
            for line in body.split("\n"):
                if "CANDIDATE_REVIEW" in line and "NOT" not in line and "NO" not in line:
                    assert False, f"CANDIDATE_REVIEW as positive status: {line}"


class TestNoForbiddenOutputs:
    ALL_IDS = [
        "taker_buy_ratio_20h", "taker_buy_zscore_20h", "taker_buy_delta_5h",
        "funding_rate_level_20h", "funding_rate_zscore_80h", "funding_rate_change_24h",
    ]

    def test_no_backtest_files(self):
        for fid in self.ALL_IDS:
            bt_dir = ROOT / "data/backtest" / fid
            assert not bt_dir.exists()
