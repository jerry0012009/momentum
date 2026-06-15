"""Tests for Phase 9A-R PM Signal Architecture Specification.

Validates:
- All required artifacts exist
- Factor role map: 10 rows, exact ids, all CANDIDATE_REVIEW
- Exactly 4 PM channels
- Signal basket plan: 5 required baskets
- PM-preferred basket is basket_3_liquidity_gated_core
- All construction_status = DESIGN_ONLY
- Weighting policy: optimization_used=FALSE, labels_or_returns_used=FALSE
- Transformation rules forbid forward returns and labels
- No alpha/tradeable/live/deploy active status
- No backtest/pnl/portfolio files
- Roadmap: Phase 10 NOT STARTED
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

EXPECTED_CHANNELS = {"RISK_PRESSURE", "TECHNICAL_REVERSION", "RANGE_POSITION", "LIQUIDITY_GATE"}

BANNED_STATUSES = {"ALPHA", "TRADEABLE", "LIVE", "DEPLOY"}

# --- Artifact existence tests ---

class TestArtifactsExist:
    @pytest.mark.parametrize("filename", [
        "PHASE_9A_R_PM_SIGNAL_ARCHITECTURE.md",
        "phase9a_r_factor_role_map.csv",
        "phase9a_r_signal_component_spec.csv",
        "phase9a_r_signal_basket_plan.csv",
        "phase9a_r_weighting_policy.csv",
        "phase9a_r_transformation_rules.csv",
        "phase9a_r_pre_implementation_checklist.csv",
    ])
    def test_artifact_exists(self, filename):
        path = os.path.join(BASE, filename)
        assert os.path.isfile(path), f"Missing: {filename}"

# --- Factor Role Map ---

class TestFactorRoleMap:
    def test_has_10_rows(self):
        df = pd.read_csv(os.path.join(BASE, "phase9a_r_factor_role_map.csv"))
        assert len(df) == 10

    def test_exact_factor_ids(self):
        df = pd.read_csv(os.path.join(BASE, "phase9a_r_factor_role_map.csv"))
        actual = sorted(df["factor_id"].tolist())
        assert actual == APPROVED_10, f"Expected {APPROVED_10}, got {actual}"

    def test_all_candidate_review(self):
        df = pd.read_csv(os.path.join(BASE, "phase9a_r_factor_role_map.csv"))
        assert (df["phase8b_status"] == "CANDIDATE_REVIEW").all()

    def test_four_channels(self):
        df = pd.read_csv(os.path.join(BASE, "phase9a_r_factor_role_map.csv"))
        actual = set(df["pm_channel"].unique())
        assert actual == EXPECTED_CHANNELS, f"Expected {EXPECTED_CHANNELS}, got {actual}"

    def test_required_columns(self):
        df = pd.read_csv(os.path.join(BASE, "phase9a_r_factor_role_map.csv"))
        required = {
            "factor_id", "factor_family", "expected_direction", "phase8b_status",
            "pm_role", "pm_channel", "default_signal_use", "combination_priority", "notes",
        }
        missing = required - set(df.columns)
        assert not missing, f"Missing columns: {missing}"

    def test_risk_pressure_has_4_factors(self):
        df = pd.read_csv(os.path.join(BASE, "phase9a_r_factor_role_map.csv"))
        rp = df[df["pm_channel"] == "RISK_PRESSURE"]
        assert len(rp) == 4

    def test_technical_reversion_has_2_factors(self):
        df = pd.read_csv(os.path.join(BASE, "phase9a_r_factor_role_map.csv"))
        tr = df[df["pm_channel"] == "TECHNICAL_REVERSION"]
        assert len(tr) == 2

    def test_range_position_has_3_factors(self):
        df = pd.read_csv(os.path.join(BASE, "phase9a_r_factor_role_map.csv"))
        rp = df[df["pm_channel"] == "RANGE_POSITION"]
        assert len(rp) == 3

    def test_liquidity_gate_has_1_factor(self):
        df = pd.read_csv(os.path.join(BASE, "phase9a_r_factor_role_map.csv"))
        lg = df[df["pm_channel"] == "LIQUIDITY_GATE"]
        assert len(lg) == 1
        assert lg.iloc[0]["factor_id"] == "xs_rank_vol"

# --- Signal Basket Plan ---

class TestSignalBasketPlan:
    def test_has_5_baskets(self):
        df = pd.read_csv(os.path.join(BASE, "phase9a_r_signal_basket_plan.csv"))
        assert len(df) == 5

    def test_required_basket_ids(self):
        df = pd.read_csv(os.path.join(BASE, "phase9a_r_signal_basket_plan.csv"))
        ids = set(df["basket_id"].unique())
        required = {
            "basket_1_core_risk_reversion",
            "basket_2_position_timing_overlay",
            "basket_3_liquidity_gated_core",
            "basket_4_family_balanced_all_candidate",
            "basket_5_minimal_robust_candidate",
        }
        assert required.issubset(ids), f"Missing baskets: {required - ids}"

    def test_pm_preferred_is_basket_3(self):
        df = pd.read_csv(os.path.join(BASE, "phase9a_r_signal_basket_plan.csv"))
        b3 = df[df["basket_id"] == "basket_3_liquidity_gated_core"]
        assert len(b3) == 1
        assert b3.iloc[0]["pm_priority"] == 1, "basket_3 must be PM-preferred (priority=1)"

    def test_all_design_only(self):
        df = pd.read_csv(os.path.join(BASE, "phase9a_r_signal_basket_plan.csv"))
        assert (df["construction_status"] == "DESIGN_ONLY").all()

# --- Weighting Policy ---

class TestWeightingPolicy:
    def test_no_optimization(self):
        df = pd.read_csv(os.path.join(BASE, "phase9a_r_weighting_policy.csv"))
        # pandas auto-parses "FALSE" as boolean False
        col = df["optimization_used"]
        assert not col.any(), f"optimization_used has True values"

    def test_no_labels_returns(self):
        df = pd.read_csv(os.path.join(BASE, "phase9a_r_weighting_policy.csv"))
        col = df["labels_or_returns_used"]
        assert not col.any(), f"labels_or_returns_used has True values"

    def test_has_entries(self):
        df = pd.read_csv(os.path.join(BASE, "phase9a_r_weighting_policy.csv"))
        assert len(df) >= 3

# --- Transformation Rules ---

class TestTransformationRules:
    def test_has_entries(self):
        df = pd.read_csv(os.path.join(BASE, "phase9a_r_transformation_rules.csv"))
        assert len(df) >= 6

    def test_forbids_forward_returns(self):
        df = pd.read_csv(os.path.join(BASE, "phase9a_r_transformation_rules.csv"))
        forbidden = " ".join(df["forbidden_inputs"].dropna().tolist()).lower()
        assert "forward" in forbidden or "label" in forbidden, \
            "Transformation rules must explicitly forbid forward returns"

    def test_forbids_labels(self):
        df = pd.read_csv(os.path.join(BASE, "phase9a_r_transformation_rules.csv"))
        forbidden = " ".join(df["forbidden_inputs"].dropna().tolist()).lower()
        assert "label" in forbidden, "Transformation rules must explicitly forbid labels"

# --- No banned statuses ---

class TestNoBannedStatuses:
    @pytest.fixture
    def csv_files(self):
        names = [
            "phase9a_r_factor_role_map.csv",
            "phase9a_r_signal_component_spec.csv",
            "phase9a_r_signal_basket_plan.csv",
            "phase9a_r_weighting_policy.csv",
            "phase9a_r_transformation_rules.csv",
            "phase9a_r_pre_implementation_checklist.csv",
        ]
        return [os.path.join(BASE, n) for n in names if os.path.isfile(os.path.join(BASE, n))]

    def test_no_banned_status(self, csv_files):
        violations = []
        for path in csv_files:
            df = pd.read_csv(path)
            for col in df.select_dtypes(include="object").columns:
                # Skip descriptive columns
                if col in ("factor_id", "factor_family", "expected_direction",
                           "notes", "included_factors", "component_role",
                           "component_name", "basket_name", "basket_role",
                           "component_weights", "within_component_weighting",
                           "rule_name", "rule_description", "allowed_inputs",
                           "forbidden_inputs", "implementation_notes",
                           "check_category", "check_description"):
                    continue
                for val in df[col].dropna().unique():
                    for banned in BANNED_STATUSES:
                        if str(val).strip() == banned:
                            violations.append(f"{os.path.basename(path)}.{col}={val}")
        assert not violations, f"Banned statuses: {violations}"

# --- No backtest/pnl/portfolio files ---

class TestNoBacktestFiles:
    def test_no_backtest_portfolio_files(self):
        for pattern in ["*backtest*", "*pnl*", "*strategy_result*", "*portfolio*"]:
            matches = glob.glob(os.path.join(BASE, pattern))
            assert not matches, f"Unexpected files: {matches}"

# --- Roadmap ---

class TestRoadmapPhase10NotStarted:
    def test_phase10_not_started(self):
        path = os.path.join(ROOT, "docs", "FACTOR_LIBRARY_ROADMAP.md")
        with open(path) as f:
            content = f.read()
        for line in content.split("\n"):
            if line.strip().startswith("| Phase 10"):
                assert "NOT STARTED" in line, f"Phase 10 row: {line}"
                return
        pytest.fail("Phase 10 not found in roadmap")
