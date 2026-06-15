"""Tests for Phase 9A-R2 PM Architecture Consistency & Docs Patch.

Validates:
- R2 closeout exists
- R2 basket plan exists with basket_6 as PM-preferred (priority=1)
- basket_6 includes all 10 CANDIDATE_REVIEW factors
- basket_3 is not pm_priority=1
- Weighting policy includes pm_full_structured_architecture_policy
- Weighting policy: optimization_used=FALSE, labels_or_returns_used=FALSE
- Transformation rules include liquidity gate cap and position overlay cap
- No backtest/PnL/portfolio result files
- Roadmap includes 9A-R2 and Phase 10 NOT STARTED
- DOCS_INDEX includes 9A-R and 9A-R2 artifacts
"""

import glob
import os

import pandas as pd
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
BASE = os.path.join(ROOT, "research", "factor_runs", "crypto_top50_factor_library")

APPROVED_10 = sorted([
    "vol_5h", "vol_40h", "range_1h", "range_4h",
    "price_pos_24h", "xs_rank_vol", "rsi_28h", "rsi_7h",
    "downside_vol_20h", "vol_of_vol_20h",
])


class TestR2CloseoutExists:
    def test_closeout_exists(self):
        path = os.path.join(BASE, "PHASE_9A_R2_PM_ARCHITECTURE_CONSISTENCY.md")
        assert os.path.isfile(path)

    def test_closeout_not_empty(self):
        with open(os.path.join(BASE, "PHASE_9A_R2_PM_ARCHITECTURE_CONSISTENCY.md")) as f:
            assert len(f.read()) > 100


class TestR2BasketPlan:
    def test_exists(self):
        assert os.path.isfile(os.path.join(BASE, "phase9a_r2_signal_basket_plan.csv"))

    def test_has_6_baskets(self):
        df = pd.read_csv(os.path.join(BASE, "phase9a_r2_signal_basket_plan.csv"))
        assert len(df) == 6

    def test_basket_6_exists(self):
        df = pd.read_csv(os.path.join(BASE, "phase9a_r2_signal_basket_plan.csv"))
        assert "basket_6_pm_full_structured_architecture" in df["basket_id"].values

    def test_basket_6_pm_priority_1(self):
        df = pd.read_csv(os.path.join(BASE, "phase9a_r2_signal_basket_plan.csv"))
        b6 = df[df["basket_id"] == "basket_6_pm_full_structured_architecture"]
        assert b6.iloc[0]["pm_priority"] == 1

    def test_basket_6_includes_all_10(self):
        df = pd.read_csv(os.path.join(BASE, "phase9a_r2_signal_basket_plan.csv"))
        b6 = df[df["basket_id"] == "basket_6_pm_full_structured_architecture"]
        factors = sorted(b6.iloc[0]["included_factors"].split(","))
        assert factors == APPROVED_10, f"Expected {APPROVED_10}, got {factors}"

    def test_basket_3_not_priority_1(self):
        df = pd.read_csv(os.path.join(BASE, "phase9a_r2_signal_basket_plan.csv"))
        b3 = df[df["basket_id"] == "basket_3_liquidity_gated_core"]
        assert b3.iloc[0]["pm_priority"] != 1

    def test_all_design_only(self):
        df = pd.read_csv(os.path.join(BASE, "phase9a_r2_signal_basket_plan.csv"))
        assert (df["construction_status"] == "DESIGN_ONLY").all()

    def test_priority_ordering(self):
        df = pd.read_csv(os.path.join(BASE, "phase9a_r2_signal_basket_plan.csv"))
        priorities = dict(zip(df["basket_id"], df["pm_priority"]))
        assert priorities["basket_6_pm_full_structured_architecture"] == 1
        assert priorities["basket_3_liquidity_gated_core"] == 2
        assert priorities["basket_1_core_risk_reversion"] == 3
        assert priorities["basket_2_position_timing_overlay"] == 4
        assert priorities["basket_5_minimal_robust_candidate"] == 5
        assert priorities["basket_4_family_balanced_all_candidate"] == 6


class TestR2WeightingPolicy:
    def test_exists(self):
        assert os.path.isfile(os.path.join(BASE, "phase9a_r2_weighting_policy.csv"))

    def test_has_pm_full_policy(self):
        df = pd.read_csv(os.path.join(BASE, "phase9a_r2_weighting_policy.csv"))
        assert "pm_full_structured_architecture_policy" in df["policy_id"].values

    def test_no_optimization(self):
        df = pd.read_csv(os.path.join(BASE, "phase9a_r2_weighting_policy.csv"))
        assert not df["optimization_used"].any()

    def test_no_labels_returns(self):
        df = pd.read_csv(os.path.join(BASE, "phase9a_r2_weighting_policy.csv"))
        assert not df["labels_or_returns_used"].any()


class TestR2TransformationRules:
    def test_exists(self):
        assert os.path.isfile(os.path.join(BASE, "phase9a_r2_transformation_rules.csv"))

    def test_has_liquidity_gate_cap(self):
        df = pd.read_csv(os.path.join(BASE, "phase9a_r2_transformation_rules.csv"))
        assert "liquidity_gate_cap" in df["rule_id"].values

    def test_has_position_overlay_cap(self):
        df = pd.read_csv(os.path.join(BASE, "phase9a_r2_transformation_rules.csv"))
        assert "position_overlay_cap" in df["rule_id"].values

    def test_has_pm_formula(self):
        df = pd.read_csv(os.path.join(BASE, "phase9a_r2_transformation_rules.csv"))
        assert "pm_full_architecture_formula" in df["rule_id"].values

    def test_forbids_forward_returns(self):
        df = pd.read_csv(os.path.join(BASE, "phase9a_r2_transformation_rules.csv"))
        forbidden = " ".join(df["forbidden_inputs"].dropna().tolist()).lower()
        assert "forward" in forbidden or "label" in forbidden

    def test_forbids_labels(self):
        df = pd.read_csv(os.path.join(BASE, "phase9a_r2_transformation_rules.csv"))
        forbidden = " ".join(df["forbidden_inputs"].dropna().tolist()).lower()
        assert "label" in forbidden


class TestNoBacktestFiles:
    def test_no_backtest_portfolio_files(self):
        for pattern in ["*backtest*", "*pnl*", "*strategy_result*", "*portfolio*"]:
            matches = glob.glob(os.path.join(BASE, pattern))
            assert not matches, f"Unexpected files: {matches}"


class TestDocsIndexPhase9AR:
    def test_docs_index_has_9ar_artifacts(self):
        with open(os.path.join(ROOT, "docs", "DOCS_INDEX.md")) as f:
            content = f.read()
        required = [
            "PHASE_9A_R_PM_SIGNAL_ARCHITECTURE.md",
            "phase9a_r_factor_role_map.csv",
            "phase9a_r_signal_basket_plan.csv",
            "test_phase9a_r_pm_signal_architecture.py",
        ]
        missing = [r for r in required if r not in content]
        assert not missing, f"DOCS_INDEX missing 9A-R: {missing}"

    def test_docs_index_has_9ar2_artifacts(self):
        with open(os.path.join(ROOT, "docs", "DOCS_INDEX.md")) as f:
            content = f.read()
        required = [
            "PHASE_9A_R2_PM_ARCHITECTURE_CONSISTENCY.md",
            "phase9a_r2_signal_basket_plan.csv",
        ]
        missing = [r for r in required if r not in content]
        assert not missing, f"DOCS_INDEX missing 9A-R2: {missing}"


class TestRoadmapPhase9AR2:
    def test_phase10_not_started(self):
        with open(os.path.join(ROOT, "docs", "FACTOR_LIBRARY_ROADMAP.md")) as f:
            content = f.read()
        for line in content.split("\n"):
            if line.strip().startswith("| Phase 10"):
                assert "NOT STARTED" in line, f"Phase 10 row: {line}"
                return
        pytest.fail("Phase 10 not found in roadmap")

    def test_roadmap_has_9ar2(self):
        with open(os.path.join(ROOT, "docs", "FACTOR_LIBRARY_ROADMAP.md")) as f:
            content = f.read()
        assert "9A-R2" in content, "Roadmap missing 9A-R2"
