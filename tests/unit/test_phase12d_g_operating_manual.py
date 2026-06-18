"""Phase 12D-G: Operating Manual & Master Registry validation tests."""

import json
import pytest
from pathlib import Path

SITE = Path("/root/clawd/jerry/momentum/reports/site/factor-library")
ROOT = Path("/root/clawd/jerry/momentum")


class TestFileExistence:
    @pytest.mark.parametrize("page", [
        "factor-library-operating-manual.html",
        "universe-data-contract.html",
        "label-horizon-contract.html",
        "signal-panel-explainer.html",
        "signal-evaluation-protocol.html",
        "cost-liquidity-vs-backtest.html",
        "paper-monitoring-explainer.html",
        "deployment-model.html",
        "master-factor-registry.html",
    ])
    def test_html_exists(self, page):
        assert (SITE / page).exists(), f"{page} missing"

    @pytest.mark.parametrize("jfile", [
        "factor_library_operating_manual.json",
        "universe_data_contract.json",
        "label_horizon_contract.json",
        "signal_panel_explainer.json",
        "signal_evaluation_protocol.json",
        "cost_liquidity_vs_backtest.json",
        "paper_monitoring_explainer.json",
        "deployment_model.json",
        "master_factor_registry.json",
    ])
    def test_json_exists(self, jfile):
        assert (SITE / "assets" / jfile).exists(), f"{jfile} missing"


class TestIndexLinks:
    def test_links_to_all_new_pages(self):
        content = (SITE / "index.html").read_text()
        for page in [
            "factor-library-operating-manual.html",
            "universe-data-contract.html",
            "label-horizon-contract.html",
            "signal-panel-explainer.html",
            "signal-evaluation-protocol.html",
            "cost-liquidity-vs-backtest.html",
            "paper-monitoring-explainer.html",
            "deployment-model.html",
            "master-factor-registry.html",
        ]:
            assert page in content, f"index.html missing link to {page}"


class TestPhaseReadable:
    def test_operating_manual_has_readable_phases(self):
        content = (SITE / "factor-library-operating-manual.html").read_text()
        # Should have readable explanations, not just Phase numbers
        assert "研究运行账本" in content or "research run ledger" in content

    def test_signal_evaluation_protocol_has_translations(self):
        content = (SITE / "signal-evaluation-protocol.html").read_text()
        assert "RankIC" in content
        assert "10A" in content


class TestSurvivorshipBias:
    def test_trust_checklist_not_pass_survivorship(self):
        content = (SITE / "trust-metrics-checklist.html").read_text()
        # Should NOT have PASS for survivorship bias
        lines = content.split("\n")
        for line in lines:
            if "survivorship" in line.lower():
                assert "PASS" not in line or "PARTIAL" in line

    def test_trust_json_not_pass_survivorship(self):
        data = json.loads((SITE / "assets" / "trust_metrics_checklist.json").read_text())
        for gate in data["gates"]:
            for item in gate["items"]:
                if "survivorship" in item["item"].lower():
                    assert item["status"] != "PASS"


class TestNoFabricatedMetrics:
    def test_master_registry_not_computed(self):
        data = json.loads((SITE / "assets" / "master_factor_registry.json").read_text())
        for f in data["factors"]:
            assert f["IC"] == "NOT_COMPUTED"


class TestNoBadClaims:
    def test_no_real_execution(self):
        for f in ["factor_library_operating_manual.md", "universe_data_contract.md", "master_factor_registry.md"]:
            content = (ROOT / "docs" / "factor_library_transparency" / f).read_text()
            assert "No real execution" in content

    def test_phase13_not_started(self):
        for f in ["factor_library_operating_manual.md", "universe_data_contract.md", "master_factor_registry.md"]:
            content = (ROOT / "docs" / "factor_library_transparency" / f).read_text()
            assert "NOT STARTED" in content
