"""Tests for Phase 8A Candidate Review Packet.

Validates:
- Closeout exists
- Human review packet: 42 rows, correct columns
- Ready shortlist: 10 rows, exact factor_ids match 7N-R2 PHASE8_READY_FOR_HUMAN_REVIEW
- All human_decision_placeholder = PENDING_HUMAN_REVIEW
- No positive status values (CANDIDATE_REVIEW, ALPHA, TRADEABLE, LIVE, DEPLOY) in CSVs
- No backtest files created
- Closeout states no promotion, no backtest, no alpha claim
- Docs index includes Phase 8A artifacts
- Roadmap includes 7N-R2 and Phase 8A
"""

import csv
import os
import re

import pandas as pd
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
BASE = os.path.join(ROOT, "research", "factor_runs", "crypto_top50_factor_library")

# Expected 10 PHASE8_READY_FOR_HUMAN_REVIEW factor_ids from 7N-R2
EXPECTED_READY_IDS = sorted([
    "vol_5h", "vol_40h", "range_1h", "range_4h",
    "price_pos_24h", "xs_rank_vol", "rsi_28h", "rsi_7h",
    "downside_vol_20h", "vol_of_vol_20h",
])

# Positive status values that must NOT appear as active decisions
BANNED_STATUSES = {"CANDIDATE_REVIEW", "ALPHA", "TRADEABLE", "LIVE", "DEPLOY"}


class TestCloseoutExists:
    def test_closeout_file_exists(self):
        path = os.path.join(BASE, "PHASE_8A_CANDIDATE_REVIEW_PACKET.md")
        assert os.path.isfile(path), f"Closeout not found: {path}"

    def test_closeout_not_empty(self):
        path = os.path.join(BASE, "PHASE_8A_CANDIDATE_REVIEW_PACKET.md")
        with open(path) as f:
            content = f.read()
        assert len(content) > 100, "Closeout is suspiciously short"


class TestHumanReviewPacket:
    def test_packet_exists(self):
        path = os.path.join(BASE, "phase8a_human_review_packet.csv")
        assert os.path.isfile(path), "phase8a_human_review_packet.csv not found"

    def test_packet_has_42_rows(self):
        df = pd.read_csv(os.path.join(BASE, "phase8a_human_review_packet.csv"))
        assert len(df) == 42, f"Expected 42 rows, got {len(df)}"

    def test_packet_required_columns(self):
        df = pd.read_csv(os.path.join(BASE, "phase8a_human_review_packet.csv"))
        required = {
            "factor_id", "factor_family", "source_phase", "factor_type",
            "diagnostic_tier", "recommended_research_use", "redundancy_status",
            "review_flags", "phase8_queue_category", "evidence_summary",
            "key_risks", "suggested_human_review_focus", "human_decision_placeholder",
        }
        missing = required - set(df.columns)
        assert not missing, f"Missing columns: {missing}"

    def test_all_decision_placeholder_pending(self):
        df = pd.read_csv(os.path.join(BASE, "phase8a_human_review_packet.csv"))
        bad = df[df["human_decision_placeholder"] != "PENDING_HUMAN_REVIEW"]
        assert bad.empty, f"Non-pending decisions: {bad['factor_id'].tolist()}"


class TestReadyShortlist:
    def test_shortlist_exists(self):
        path = os.path.join(BASE, "phase8a_ready_for_human_review_shortlist.csv")
        assert os.path.isfile(path), "Shortlist not found"

    def test_shortlist_has_10_rows(self):
        df = pd.read_csv(os.path.join(BASE, "phase8a_ready_for_human_review_shortlist.csv"))
        assert len(df) == 10, f"Expected 10 rows, got {len(df)}"

    def test_shortlist_factor_ids_match_queue(self):
        """Shortlist factor_ids must exactly equal PHASE8_READY_FOR_HUMAN_REVIEW from 7N-R2."""
        df = pd.read_csv(os.path.join(BASE, "phase8a_ready_for_human_review_shortlist.csv"))
        actual = sorted(df["factor_id"].tolist())
        assert actual == EXPECTED_READY_IDS, (
            f"Factor ID mismatch.\nExpected: {EXPECTED_READY_IDS}\nActual:   {actual}"
        )

    def test_shortlist_all_decision_placeholder_pending(self):
        df = pd.read_csv(os.path.join(BASE, "phase8a_ready_for_human_review_shortlist.csv"))
        bad = df[df["human_decision_placeholder"] != "PENDING_HUMAN_REVIEW"]
        assert bad.empty, f"Non-pending: {bad['factor_id'].tolist()}"


class TestDecisionTemplate:
    def test_template_exists(self):
        path = os.path.join(BASE, "phase8a_review_decision_template.csv")
        assert os.path.isfile(path), "Decision template not found"

    def test_template_has_42_rows(self):
        df = pd.read_csv(os.path.join(BASE, "phase8a_review_decision_template.csv"))
        assert len(df) == 42, f"Expected 42, got {len(df)}"

    def test_template_columns(self):
        df = pd.read_csv(os.path.join(BASE, "phase8a_review_decision_template.csv"))
        required = {"factor_id", "proposed_human_decision", "reviewer_notes",
                     "decision_date", "reviewer"}
        missing = required - set(df.columns)
        assert not missing, f"Missing columns: {missing}"

    def test_template_all_pending(self):
        df = pd.read_csv(os.path.join(BASE, "phase8a_review_decision_template.csv"))
        bad = df[df["proposed_human_decision"] != "PENDING_HUMAN_REVIEW"]
        assert bad.empty, f"Non-pending decisions: {bad['factor_id'].tolist()}"


class TestNoBannedStatusInCSVs:
    """No CSV file in Phase 8A outputs may contain CANDIDATE_REVIEW, ALPHA,
    TRADEABLE, LIVE, or DEPLOY as a decision/status value."""

    @pytest.fixture
    def csv_files(self):
        names = [
            "phase8a_human_review_packet.csv",
            "phase8a_ready_for_human_review_shortlist.csv",
            "phase8a_review_decision_template.csv",
        ]
        return [os.path.join(BASE, n) for n in names]

    def test_no_banned_status_values(self, csv_files):
        violations = []
        for path in csv_files:
            if not os.path.isfile(path):
                continue
            df = pd.read_csv(path)
            for col in df.select_dtypes(include="object").columns:
                # Skip factor_id, factor_family, and similar identifier columns
                if col in ("factor_id", "factor_family", "source_phase",
                           "factor_type", "evidence_summary", "key_risks",
                           "suggested_human_review_focus", "reviewer_notes",
                           "reviewer", "why_ready_for_human_review",
                           "remaining_risks", "phase8_notes"):
                    continue
                for val in df[col].dropna().unique():
                    val_str = str(val).strip()
                    # Check if any banned word appears as a standalone value
                    for banned in BANNED_STATUSES:
                        if val_str == banned:
                            violations.append(f"{os.path.basename(path)}.{col} = {val_str}")
        assert not violations, f"Banned status values found: {violations}"


class TestNoBacktestFiles:
    def test_no_backtest_output_files(self):
        """Phase 8A must not create backtest output files."""
        backtest_patterns = ["*backtest*", "*pnl*", "*strategy_result*", "*portfolio*"]
        for pattern in backtest_patterns:
            import glob
            matches = glob.glob(os.path.join(BASE, pattern))
            assert not matches, f"Backtest files found: {matches}"


class TestCloseoutDeclarations:
    """Closeout must state: no promotion, no backtest, no alpha claim."""

    @pytest.fixture
    def closeout_text(self):
        path = os.path.join(BASE, "PHASE_8A_CANDIDATE_REVIEW_PACKET.md")
        with open(path) as f:
            return f.read()

    def test_no_promotion_declared(self, closeout_text):
        assert "No factor was promoted" in closeout_text

    def test_no_backtest_declared(self, closeout_text):
        assert "No strategy backtest was run" in closeout_text

    def test_no_alpha_claim_declared(self, closeout_text):
        assert "No alpha claim was made" in closeout_text

    def test_no_candidate_review_declared(self, closeout_text):
        assert "No factor entered CANDIDATE_REVIEW" in closeout_text

    def test_v04_remains_diagnostic(self, closeout_text):
        assert "v0.4 remains a diagnostic" in closeout_text


class TestDocsIndexIncludesPhase8A:
    def test_docs_index_has_phase8a_artifacts(self):
        path = os.path.join(ROOT, "docs", "DOCS_INDEX.md")
        with open(path) as f:
            content = f.read()
        required = [
            "PHASE_8A_CANDIDATE_REVIEW_PACKET.md",
            "phase8a_human_review_packet.csv",
            "phase8a_ready_for_human_review_shortlist.csv",
            "phase8a_review_protocol.md",
            "phase8a_review_decision_template.csv",
        ]
        missing = [r for r in required if r not in content]
        assert not missing, f"DOCS_INDEX missing Phase 8A artifacts: {missing}"

    def test_docs_index_has_test_file(self):
        path = os.path.join(ROOT, "docs", "DOCS_INDEX.md")
        with open(path) as f:
            content = f.read()
        assert "test_phase8a_candidate_review_packet.py" in content


class TestRoadmapIncludes7NR2AndPhase8A:
    def test_roadmap_has_7nr2(self):
        path = os.path.join(ROOT, "docs", "FACTOR_LIBRARY_ROADMAP.md")
        with open(path) as f:
            content = f.read()
        assert "7N-R2" in content, "Roadmap missing 7N-R2"

    def test_roadmap_has_phase8a(self):
        path = os.path.join(ROOT, "docs", "FACTOR_LIBRARY_ROADMAP.md")
        with open(path) as f:
            content = f.read()
        assert "Phase 8A" in content or "8A" in content, "Roadmap missing Phase 8A"

    def test_roadmap_no_candidate_review_in_phase8(self):
        """Phase 8 status should not claim CANDIDATE_REVIEW for any factor."""
        path = os.path.join(ROOT, "docs", "FACTOR_LIBRARY_ROADMAP.md")
        with open(path) as f:
            content = f.read()
        # Check Section 6 for promotion language
        section6_start = content.find("## 6.")
        section7_start = content.find("## 7.")
        if section6_start > 0 and section7_start > 0:
            section6 = content[section6_start:section7_start]
            # Should say "no factor has entered CANDIDATE_REVIEW"
            assert "No factor has entered CANDIDATE_REVIEW" in section6 or \
                   "no factor has entered CANDIDATE_REVIEW" in section6 or \
                   "No factor has been promoted" in section6, \
                   "Section 6 should state no factor entered CANDIDATE_REVIEW"
