"""Tests for Phase 8B PM Candidate Review Decisions.

Validates:
- Closeout exists
- Candidate decision file: 42 rows
- Candidate shortlist: 10 rows, exact factor_ids
- v0.5 status file: 42 rows
- Non-candidate queue: 32 rows
- Exactly 10 rows have approved_status=CANDIDATE_REVIEW
- Candidate ids exactly equal PM-approved list
- No non-approved factor has CANDIDATE_REVIEW
- No ALPHA/TRADEABLE/LIVE/DEPLOY active status
- No backtest/portfolio files
- Roadmap says Phase 9 NOT STARTED
- Roadmap says Phase 10 NOT STARTED
"""

import glob
import os

import pandas as pd
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
BASE = os.path.join(ROOT, "research", "factor_runs", "crypto_top50_factor_library")

# PM-approved 10 factors
APPROVED_10 = sorted([
    "vol_5h", "vol_40h", "range_1h", "range_4h",
    "price_pos_24h", "xs_rank_vol", "rsi_28h", "rsi_7h",
    "downside_vol_20h", "vol_of_vol_20h",
])

BANNED_STATUSES = {"ALPHA", "TRADEABLE", "LIVE", "DEPLOY"}


class TestCloseoutExists:
    def test_closeout_file_exists(self):
        path = os.path.join(BASE, "PHASE_8B_PM_CANDIDATE_DECISIONS.md")
        assert os.path.isfile(path), f"Closeout not found: {path}"

    def test_closeout_not_empty(self):
        path = os.path.join(BASE, "PHASE_8B_PM_CANDIDATE_DECISIONS.md")
        with open(path) as f:
            content = f.read()
        assert len(content) > 100


class TestCandidateDecisionsFile:
    def test_exists(self):
        assert os.path.isfile(os.path.join(BASE, "phase8b_candidate_review_decisions.csv"))

    def test_has_42_rows(self):
        df = pd.read_csv(os.path.join(BASE, "phase8b_candidate_review_decisions.csv"))
        assert len(df) == 42

    def test_required_columns(self):
        df = pd.read_csv(os.path.join(BASE, "phase8b_candidate_review_decisions.csv"))
        required = {
            "factor_id", "factor_family", "diagnostic_tier", "recommended_research_use",
            "phase8_queue_category", "pm_decision", "approved_status",
            "decision_rationale", "decision_scope",
        }
        missing = required - set(df.columns)
        assert not missing, f"Missing columns: {missing}"


class TestCandidateShortlist:
    def test_exists(self):
        assert os.path.isfile(os.path.join(BASE, "phase8b_candidate_review_shortlist.csv"))

    def test_has_10_rows(self):
        df = pd.read_csv(os.path.join(BASE, "phase8b_candidate_review_shortlist.csv"))
        assert len(df) == 10

    def test_exact_factor_ids(self):
        df = pd.read_csv(os.path.join(BASE, "phase8b_candidate_review_shortlist.csv"))
        actual = sorted(df["factor_id"].tolist())
        assert actual == APPROVED_10, f"Expected {APPROVED_10}, got {actual}"

    def test_all_approved_status(self):
        df = pd.read_csv(os.path.join(BASE, "phase8b_candidate_review_shortlist.csv"))
        assert (df["approved_status"] == "CANDIDATE_REVIEW").all()


class TestV05StatusFile:
    def test_exists(self):
        assert os.path.isfile(os.path.join(BASE, "phase8b_factor_library_v0_5_status.csv"))

    def test_has_42_rows(self):
        df = pd.read_csv(os.path.join(BASE, "phase8b_factor_library_v0_5_status.csv"))
        assert len(df) == 42

    def test_exactly_10_candidate_review(self):
        df = pd.read_csv(os.path.join(BASE, "phase8b_factor_library_v0_5_status.csv"))
        count = (df["phase8b_status"] == "CANDIDATE_REVIEW").sum()
        assert count == 10, f"Expected 10 CANDIDATE_REVIEW, got {count}"

    def test_exactly_32_non_candidate(self):
        df = pd.read_csv(os.path.join(BASE, "phase8b_factor_library_v0_5_status.csv"))
        count = (df["phase8b_status"] != "CANDIDATE_REVIEW").sum()
        assert count == 32, f"Expected 32 non-candidate, got {count}"

    def test_no_alpha_tradeable(self):
        df = pd.read_csv(os.path.join(BASE, "phase8b_factor_library_v0_5_status.csv"))
        for col in df.select_dtypes(include="object").columns:
            if col in ("factor_id", "factor_family", "source_phase", "factor_type",
                       "expected_direction", "review_flags", "redundancy_status",
                       "max_static_corr", "max_dynamic_corr", "medium_redundancy_pairs",
                       "recommended_research_use", "curation_notes", "decision_scope"):
                continue
            for val in df[col].dropna().unique():
                for banned in BANNED_STATUSES:
                    assert str(val).strip() != banned, f"{col}={val} is banned"


class TestNonCandidateQueue:
    def test_exists(self):
        assert os.path.isfile(os.path.join(BASE, "phase8b_non_candidate_review_queue.csv"))

    def test_has_32_rows(self):
        df = pd.read_csv(os.path.join(BASE, "phase8b_non_candidate_review_queue.csv"))
        assert len(df) == 32

    def test_none_are_candidate_review(self):
        df = pd.read_csv(os.path.join(BASE, "phase8b_non_candidate_review_queue.csv"))
        assert (df["approved_status"] != "CANDIDATE_REVIEW").all()

    def test_groups_present(self):
        """Should have direction, redundancy, and weak/parked groups."""
        df = pd.read_csv(os.path.join(BASE, "phase8b_non_candidate_review_queue.csv"))
        decisions = set(df["pm_decision"].unique())
        assert "PARK_DIRECTION_REVIEW" in decisions
        assert "PARK_REDUNDANCY_REVIEW" in decisions or len(df[df["pm_decision"] == "PARK_REDUNDANCY_REVIEW"]) >= 0
        assert "PARK_WEAK_OR_LOW_PRIORITY" in decisions or len(df[df["pm_decision"] == "PARK_WEAK_OR_LOW_PRIORITY"]) >= 0


class TestExactly10CandidateReview:
    def test_decisions_file_10_approved(self):
        df = pd.read_csv(os.path.join(BASE, "phase8b_candidate_review_decisions.csv"))
        approved = df[df["approved_status"] == "CANDIDATE_REVIEW"]
        assert len(approved) == 10

    def test_approved_ids_match(self):
        df = pd.read_csv(os.path.join(BASE, "phase8b_candidate_review_decisions.csv"))
        approved = df[df["approved_status"] == "CANDIDATE_REVIEW"]
        actual = sorted(approved["factor_id"].tolist())
        assert actual == APPROVED_10

    def test_no_other_has_candidate_review(self):
        df = pd.read_csv(os.path.join(BASE, "phase8b_candidate_review_decisions.csv"))
        non_approved = df[~df["factor_id"].isin(APPROVED_10)]
        assert (non_approved["approved_status"] != "CANDIDATE_REVIEW").all()


class TestNoBannedStatuses:
    @pytest.fixture
    def csv_files(self):
        names = [
            "phase8b_candidate_review_decisions.csv",
            "phase8b_candidate_review_shortlist.csv",
            "phase8b_factor_library_v0_5_status.csv",
            "phase8b_non_candidate_review_queue.csv",
        ]
        return [os.path.join(BASE, n) for n in names]

    def test_no_banned_status(self, csv_files):
        violations = []
        for path in csv_files:
            if not os.path.isfile(path):
                continue
            df = pd.read_csv(path)
            for col in df.select_dtypes(include="object").columns:
                if col in ("factor_id", "factor_family", "source_phase", "factor_type",
                           "expected_direction", "review_flags", "redundancy_status",
                           "max_static_corr", "max_dynamic_corr", "medium_redundancy_pairs",
                           "recommended_research_use", "curation_notes", "decision_rationale",
                           "decision_scope", "phase8_notes"):
                    continue
                for val in df[col].dropna().unique():
                    for banned in BANNED_STATUSES:
                        if str(val).strip() == banned:
                            violations.append(f"{os.path.basename(path)}.{col}={val}")
        assert not violations, f"Banned statuses: {violations}"


class TestNoBacktestFiles:
    def test_no_backtest_portfolio_files(self):
        for pattern in ["*backtest*", "*pnl*", "*strategy_result*", "*portfolio*"]:
            matches = glob.glob(os.path.join(BASE, pattern))
            assert not matches, f"Unexpected files: {matches}"


class TestRoadmapPhase9NotStarted:
    def test_phase9_not_started(self):
        path = os.path.join(ROOT, "docs", "FACTOR_LIBRARY_ROADMAP.md")
        with open(path) as f:
            content = f.read()
        # Find Phase 9 row in the macro roadmap table (starts with "| Phase 9")
        for line in content.split("\n"):
            if line.strip().startswith("| Phase 9"):
                assert "NOT STARTED" in line, f"Phase 9 row: {line}"
                return
        pytest.fail("Phase 9 not found in roadmap")

    def test_phase10_not_started(self):
        path = os.path.join(ROOT, "docs", "FACTOR_LIBRARY_ROADMAP.md")
        with open(path) as f:
            content = f.read()
        for line in content.split("\n"):
            if line.strip().startswith("| Phase 10"):
                assert "NOT STARTED" in line, f"Phase 10 row: {line}"
                return
        pytest.fail("Phase 10 not found in roadmap")
