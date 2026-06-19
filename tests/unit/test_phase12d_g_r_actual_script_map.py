"""Phase 12D-G-R3: Signal Evaluation Framework verification tests."""

import json
import pytest
from pathlib import Path

SITE = Path("/root/clawd/jerry/momentum/reports/site/factor-library")
ROOT = Path("/root/clawd/jerry/momentum")


class TestSection7Renamed:
    def test_framework_title(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "Signal Evaluation Framework" in content
        assert "信号评价框架" in content


class TestRankICFormula:
    def test_formula_present(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "SpearmanCorr" in content
        assert "rank(signal_t)" in content

    def test_values_present(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "0.0325" in content
        assert "17.6" in content


class TestQuantileSpread:
    def test_formula_present(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "mean(return" in content or "mean(" in content

    def test_values_present(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "-0.000306" in content
        assert "-0.016623" in content


class TestRankICSpreadCaveat:
    def test_caveat_present(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "RankIC" in content
        assert "spread" in content.lower()
        assert "负" in content or "negative" in content.lower()


class TestPhaseMapping:
    def test_10a_mapped(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "SignalRankICEvaluator" in content
        assert "QuantileSpreadEvaluator" in content

    def test_10ar_mapped(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "DirectionConsistencyChecker" in content

    def test_10b_mapped(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "BucketTailDiagnostics" in content

    def test_10d_mapped(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "GenericVariantGridEvaluator" in content


class TestMLReusability:
    def test_reusable_schema(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "timestamp / symbol / signal_name / signal_value" in content

    def test_ml_section(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "机器学习" in content


class TestRefactorRecommendation:
    def test_refactor_present(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "signal-agnostic evaluation package" in content or "signal_evaluation" in content

    def test_stage_specific_wrappers(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "阶段脚本" in content or "stage-specific" in content.lower() or "wrappers" in content


class TestNoBadClaims:
    def test_not_tradeable_alpha(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "不是一个已经干净验证的 alpha" in content

    def test_no_real_execution(self):
        content = (ROOT / "docs" / "factor_library_transparency" / "actual_script_map.md").read_text()
        assert "No real execution" in content

    def test_phase13_not_started(self):
        content = (ROOT / "docs" / "factor_library_transparency" / "actual_script_map.md").read_text()
        assert "NOT STARTED" in content


class TestJSON:
    def test_signal_evaluation_framework(self):
        data = json.loads((SITE / "assets" / "actual_script_map.json").read_text())
        assert "signal_evaluation_framework" in data
        sef = data["signal_evaluation_framework"]
        assert "reusable_input_schema" in sef
        assert "metrics" in sef
        assert "current_results" in sef
        assert len(sef["metrics"]) == 6
        assert sef["current_results"]["rankic"]["1h"] == 0.0325
