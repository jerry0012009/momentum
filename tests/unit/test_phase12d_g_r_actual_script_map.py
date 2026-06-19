"""Phase 12D-G-R4: Cost/Liquidity caution & conclusion precision tests."""

import json
import pytest
from pathlib import Path

SITE = Path("/root/clawd/jerry/momentum/reports/site/factor-library")
ROOT = Path("/root/clawd/jerry/momentum")


class TestCostLiquidityNotPass:
    def test_cost_sensitive_in_html(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "COST_SENSITIVE" in content or "MIXED" in content

    def test_no_pass_for_cost(self):
        content = (SITE / "actual-script-map.html").read_text()
        # Should not say "通过" for cost/liquidity bridge
        lines = content.split("\n")
        for line in lines:
            if "Cost / Liquidity Bridge" in line or "COST_SENSITIVE" in line:
                assert "通过" not in line or "COST_SENSITIVE" in line

    def test_phase12b_not_paper_trade(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "不是 future paper trade" in content or "不是 future paper trade" in content

    def test_not_final_backtest(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "不是最终交易回测" in content


class TestConclusionSummary:
    def test_continue_paper_diagnostic(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "继续 paper diagnostic" in content
        assert "不可解释为可交易策略" in content or "不可解释为可交易" in content

    def test_cost_core_constraint(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "成本仍是核心约束" in content

    def test_not_cleanly_validated(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "不是一个已经干净验证的 alpha" in content


class Test10CPolicyDesign:
    def test_10c_description(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "无独立通用 evaluator" in content or "设计记录" in content

    def test_10c_reusability(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "每个新信号都应重新设计" in content


class TestJSON:
    def test_cost_liquidity_status(self):
        data = json.loads((SITE / "assets" / "actual_script_map.json").read_text())
        clb = data["signal_evaluation_framework"]["current_results"]["cost_liquidity_bridge"]
        assert clb["status"] in ["COST_SENSITIVE", "MIXED"]

    def test_phase12b_status(self):
        data = json.loads((SITE / "assets" / "actual_script_map.json").read_text())
        clb = data["signal_evaluation_framework"]["current_results"]["cost_liquidity_bridge"]
        assert "RECENT_ROLLING_DIAGNOSTIC" in clb["phase12b"]
        assert "NOT" in clb["phase12b"]

    def test_conclusion(self):
        data = json.loads((SITE / "assets" / "actual_script_map.json").read_text())
        cr = data["signal_evaluation_framework"]["current_results"]
        assert cr["current_core_signal_conclusion"] == "CONTINUE_PAPER_DIAGNOSTIC_ONLY"
        assert cr["tradeable_alpha"] is False

    def test_no_pass_field(self):
        data = json.loads((SITE / "assets" / "actual_script_map.json").read_text())
        clb = data["signal_evaluation_framework"]["current_results"]["cost_liquidity_bridge"]
        assert "PASS" not in clb["status"]


class TestNoBadClaims:
    def test_no_real_execution(self):
        content = (ROOT / "docs" / "factor_library_transparency" / "actual_script_map.md").read_text()
        assert "No real execution" in content

    def test_phase13_not_started(self):
        content = (ROOT / "docs" / "factor_library_transparency" / "actual_script_map.md").read_text()
        assert "NOT STARTED" in content
