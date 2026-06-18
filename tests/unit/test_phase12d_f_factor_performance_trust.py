"""Phase 12D-F: Factor Performance & Trust Metrics validation tests."""

import json
import pytest
from pathlib import Path

SITE = Path("/root/clawd/jerry/momentum/reports/site/factor-library")
ROOT = Path("/root/clawd/jerry/momentum")


class TestFileExistence:
    def test_factor_performance_map_html(self):
        assert (SITE / "factor-performance-map.html").exists()

    def test_signal_evaluation_summary_html(self):
        assert (SITE / "signal-evaluation-summary.html").exists()

    def test_trust_metrics_checklist_html(self):
        assert (SITE / "trust-metrics-checklist.html").exists()

    def test_factor_performance_map_json(self):
        assert (SITE / "assets" / "factor_performance_map.json").exists()

    def test_signal_evaluation_summary_json(self):
        assert (SITE / "assets" / "signal_evaluation_summary.json").exists()

    def test_trust_metrics_checklist_json(self):
        assert (SITE / "assets" / "trust_metrics_checklist.json").exists()

    def test_factor_performance_map_md(self):
        assert (ROOT / "docs" / "factor_library_transparency" / "factor_performance_map.md").exists()

    def test_signal_evaluation_summary_md(self):
        assert (ROOT / "docs" / "factor_library_transparency" / "signal_evaluation_summary.md").exists()

    def test_trust_metrics_checklist_md(self):
        assert (ROOT / "docs" / "factor_library_transparency" / "trust_metrics_checklist.md").exists()


class TestICDefinitions:
    def test_html_has_ic_definitions(self):
        content = (SITE / "factor-performance-map.html").read_text()
        assert "IC" in content
        assert "RankIC" in content
        assert "ICIR" in content

    def test_json_has_ic_definitions(self):
        data = json.loads((SITE / "assets" / "factor_performance_map.json").read_text())
        assert "ic_definitions" in data
        assert "IC" in data["ic_definitions"]
        assert "RankIC" in data["ic_definitions"]


class TestNotComputed:
    def test_json_factors_not_computed(self):
        data = json.loads((SITE / "assets" / "factor_performance_map.json").read_text())
        for f in data["factors"]:
            assert f["IC"] == "NOT_COMPUTED"
            assert f["RankIC"] == "NOT_COMPUTED"
            assert f["ICIR"] == "NOT_COMPUTED"

    def test_html_not_computed(self):
        content = (SITE / "factor-performance-map.html").read_text()
        assert "NOT_COMPUTED" in content


class TestSignalEvaluation:
    def test_json_has_rankic(self):
        data = json.loads((SITE / "assets" / "signal_evaluation_summary.json").read_text())
        assert "signal_rankic" in data
        assert "signal_v0_core_only" in data["signal_rankic"]

    def test_html_has_rankic(self):
        content = (SITE / "signal-evaluation-summary.html").read_text()
        assert "RankIC" in content
        assert "0.0325" in content or "0.0385" in content


class TestTrustGates:
    def test_json_has_gates(self):
        data = json.loads((SITE / "assets" / "trust_metrics_checklist.json").read_text())
        assert "gates" in data
        assert len(data["gates"]) >= 5

    def test_html_has_gates(self):
        content = (SITE / "trust-metrics-checklist.html").read_text()
        assert "数据可信度" in content
        assert "时间对齐" in content
        assert "因子计算" in content


class TestNavigation:
    def test_index_links_to_new_pages(self):
        content = (SITE / "index.html").read_text()
        assert "factor-performance-map.html" in content
        assert "signal-evaluation-summary.html" in content
        assert "trust-metrics-checklist.html" in content


class TestNoBadClaims:
    def test_no_real_execution(self):
        for f in ["factor_performance_map.md", "signal_evaluation_summary.md", "trust_metrics_checklist.md"]:
            content = (ROOT / "docs" / "factor_library_transparency" / f).read_text()
            assert "No real execution" in content

    def test_phase13_not_started(self):
        for f in ["factor_performance_map.md", "signal_evaluation_summary.md", "trust_metrics_checklist.md"]:
            content = (ROOT / "docs" / "factor_library_transparency" / f).read_text()
            assert "NOT STARTED" in content
