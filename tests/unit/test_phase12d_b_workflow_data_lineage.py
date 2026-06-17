"""
Phase 12D-B: Workflow Map & Data Lineage — Quality Checks

Verifies all Phase 12D-B deliverables exist and contain required content.
"""

import csv
import json
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]

FILES = {
    "workflow-map.html": PROJECT_ROOT / "reports/site/factor-library/workflow-map.html",
    "data-lineage.html": PROJECT_ROOT / "reports/site/factor-library/data-lineage.html",
    "pipeline-layers.html": PROJECT_ROOT / "reports/site/factor-library/pipeline-layers.html",
    "workflow_map.json": PROJECT_ROOT / "reports/site/factor-library/assets/workflow_map.json",
    "data_lineage.json": PROJECT_ROOT / "reports/site/factor-library/assets/data_lineage.json",
    "workflow_map_v2.md": PROJECT_ROOT / "docs/factor_library_transparency/workflow_map_v2.md",
    "data_lineage_v2.md": PROJECT_ROOT / "docs/factor_library_transparency/data_lineage_v2.md",
    "PHASE_12D_B": PROJECT_ROOT
    / "research/factor_runs/crypto_top50_factor_library/PHASE_12D_B_WORKFLOW_DATA_LINEAGE.md",
    "quality_checks": PROJECT_ROOT
    / "research/factor_runs/crypto_top50_factor_library/phase12d_b_quality_checks.csv",
    "index.html": PROJECT_ROOT / "reports/site/factor-library/index.html",
}


class TestFilesExist:
    @pytest.mark.parametrize("name,path", FILES.items(), ids=list(FILES.keys()))
    def test_file_exists_and_nonempty(self, name, path):
        assert path.exists(), f"Missing: {name}"
        assert path.stat().st_size > 0, f"Empty: {name}"


class TestWorkflowMapHtml:
    @pytest.fixture
    def html(self):
        return FILES["workflow-map.html"].read_text()

    def test_contains_phase12db(self, html):
        assert "12D-B" in html

    def test_contains_phase13_not_started(self, html):
        assert "NOT STARTED" in html or "NOT_STARTED" in html

    def test_contains_run_id(self, html):
        assert "crypto_top50_usdt_perp_1h" in html

    def test_contains_all_phases(self, html):
        for phase in ["Phase 2", "Phase 3", "Phase 4", "Phase 5", "Phase 6",
                       "Phase 7", "Phase 8", "Phase 9", "Phase 10", "Phase 11",
                       "Phase 12A", "Phase 12B", "Phase 12C", "Phase 12D"]:
            assert phase in html, f"Missing {phase}"

    def test_no_real_execution(self, html):
        assert "无实盘" in html or "No real execution" in html


class TestDataLineageHtml:
    @pytest.fixture
    def html(self):
        return FILES["data-lineage.html"].read_text()

    def test_contains_run_id(self, html):
        assert "crypto_top50_usdt_perp_1h" in html

    def test_contains_key_nodes(self, html):
        for node in ["OHLCV", "Factor Values", "Forward Return", "Signal Panel",
                      "Phase 10", "Phase 11", "Phase 12", "网站输出"]:
            assert node.lower() in html.lower(), f"Missing node: {node}"

    def test_site_is_generated(self, html):
        assert "生成" in html or "generated" in html.lower()


class TestPipelineLayersHtml:
    @pytest.fixture
    def html(self):
        return FILES["pipeline-layers.html"].read_text()

    def test_contains_run_id(self, html):
        assert "crypto_top50_usdt_perp_1h" in html

    def test_contains_all_layers(self, html):
        for layer in ["config", "src/momentum", "scripts", "data",
                       "research", "docs", "reports", "tests"]:
            assert layer in html, f"Missing layer: {layer}"

    def test_contains_phase13_not_started(self, html):
        assert "NOT STARTED" in html or "Phase 13" in html


class TestWorkflowMapJson:
    @pytest.fixture
    def data(self):
        with open(FILES["workflow_map.json"]) as f:
            return json.load(f)

    def test_run_id(self, data):
        assert data["meta"]["run_id"] == "crypto_top50_usdt_perp_1h"

    def test_phases_2_through_12d(self, data):
        phase_ids = [p["id"] for p in data["phases"]]
        for p in ["phase2", "phase3", "phase4", "phase5", "phase6",
                   "phase7", "phase8", "phase9", "phase10", "phase11",
                   "phase12a", "phase12b", "phase12c", "phase12d", "phase13"]:
            assert p in phase_ids, f"Missing phase: {p}"

    def test_phase13_not_started(self, data):
        p13 = [p for p in data["phases"] if p["id"] == "phase13"][0]
        assert p13["status"] == "NOT_STARTED"

    def test_disclaimer_present(self, data):
        assert "disclaimer" in data["meta"]


class TestDataLineageJson:
    @pytest.fixture
    def data(self):
        with open(FILES["data_lineage.json"]) as f:
            return json.load(f)

    def test_run_id(self, data):
        assert data["meta"]["run_id"] == "crypto_top50_usdt_perp_1h"

    def test_key_nodes_present(self, data):
        node_ids = [n["id"] for n in data["nodes"]]
        for nid in ["raw_klines", "factor_values", "forward_returns",
                     "signal_panel", "phase10_evaluation", "phase11_cost_liquidity",
                     "paper_monitoring", "website_output"]:
            assert nid in node_ids, f"Missing node: {nid}"

    def test_flow_edges_exist(self, data):
        assert len(data["flow_edges"]) >= 8

    def test_site_is_generated(self, data):
        website = [n for n in data["nodes"] if n["id"] == "website_output"][0]
        assert website["generated"] is True


class TestQualityChecksCsv:
    @pytest.fixture
    def checks(self):
        with open(FILES["quality_checks"]) as f:
            return list(csv.DictReader(f))

    def test_all_pass(self, checks):
        failures = [c for c in checks if c.get("status") != "PASS"]
        assert len(failures) == 0, f"Failed: {[f['check_name'] for f in failures]}"

    def test_required_checks(self, checks):
        names = {c["check_name"] for c in checks}
        required = [
            "workflow-map.html exists",
            "data-lineage.html exists",
            "pipeline-layers.html exists",
            "workflow_map.json exists",
            "data_lineage.json exists",
            "workflow_map_v2.md exists",
            "data_lineage_v2.md exists",
            "phase2_to_12d_documented",
            "all_layers_documented",
            "run_id_documented",
            "phase_13_not_started",
            "no_real_execution",
            "no_research_results_changed",
        ]
        for r in required:
            assert r in names, f"Missing check: {r}"


class TestIndexUpdated:
    @pytest.fixture
    def html(self):
        return FILES["index.html"].read_text()

    def test_workflow_map_link(self, html):
        assert "workflow-map.html" in html

    def test_data_lineage_link(self, html):
        assert "data-lineage.html" in html

    def test_pipeline_layers_link(self, html):
        assert "pipeline-layers.html" in html


class TestNoDestructiveChanges:
    def test_v1_files_preserved(self):
        v1_workflow = PROJECT_ROOT / "docs/factor_library_transparency/workflow_map.md"
        v1_lineage = PROJECT_ROOT / "docs/factor_library_transparency/data_lineage.md"
        assert v1_workflow.exists(), "v1 workflow_map.md was deleted"
        assert v1_lineage.exists(), "v1 data_lineage.md was deleted"

    def test_no_real_execution_string(self):
        for fpath in [FILES["workflow-map.html"], FILES["data-lineage.html"]]:
            content = fpath.read_text()
            assert "real execution enabled" not in content.lower()
            assert "alpha claim" not in content.lower() or "no alpha claim" in content.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
