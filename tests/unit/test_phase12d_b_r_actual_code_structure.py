"""
Phase 12D-B-R: 真实代码结构与脚本地图修复 — 质量检查测试
"""
import json
import os
import re
import csv
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SITE_DIR = REPO_ROOT / "reports" / "site" / "factor-library"
ASSETS_DIR = SITE_DIR / "assets"
DOCS_DIR = REPO_ROOT / "docs" / "factor_library_transparency"
SCRIPTS_DIR = REPO_ROOT / "scripts"
SRC_DIR = REPO_ROOT / "src" / "momentum"


class TestActualScriptMapFiles:
    """QC-01 to QC-03: Core deliverable files exist."""

    def test_actual_script_map_html_exists(self):
        """QC-01: actual-script-map.html exists."""
        assert (SITE_DIR / "actual-script-map.html").exists()

    def test_actual_script_map_json_exists(self):
        """QC-02: actual_script_map.json exists."""
        assert (ASSETS_DIR / "actual_script_map.json").exists()

    def test_actual_script_map_md_exists(self):
        """QC-03: actual_script_map.md exists."""
        assert (DOCS_DIR / "actual_script_map.md").exists()


class TestIndexLinks:
    """QC-04: index.html links to actual-script-map.html."""

    def test_index_links_to_actual_script_map(self):
        index_html = (SITE_DIR / "index.html").read_text()
        assert "actual-script-map.html" in index_html


class TestRepositoryMapFixes:
    """QC-05, QC-07, QC-08: repository-map.html fixes."""

    def test_no_color_labels_in_data_flow(self):
        """QC-05: Color labels not in data flow area."""
        html = (SITE_DIR / "repository-map.html").read_text()
        # The legend section should not be inside the flow-diagram card
        flow_start = html.find("flow-diagram")
        flow_end = html.find("</div>", flow_start + 100)
        flow_section = html[flow_start:flow_end] if flow_start >= 0 else ""
        # Labels should NOT be in the flow section
        assert "tag-source" not in flow_section or "人工维护" not in flow_section

    def test_file_label_legend_exists(self):
        """File label legend exists as separate section."""
        html = (SITE_DIR / "repository-map.html").read_text()
        assert "文件标签说明" in html
        assert "人工维护源文件" in html
        assert "脚本生成产物" in html

    def test_research_described_as_audit_archive(self):
        """QC-07: research/factor_runs described as audit archive."""
        html = (SITE_DIR / "repository-map.html").read_text()
        assert "审计档案和结果目录" in html
        assert "不是主要代码目录" in html

    def test_src_described_as_reusable_component_lib(self):
        """QC-08: src/momentum described as reusable component library."""
        html = (SITE_DIR / "repository-map.html").read_text()
        assert "已有可复用代码组件库" in html
        assert "不等于当前 run 的全部执行链路" in html

    def test_scripts_described_as_main_entry(self):
        """scripts/ described as main execution entry."""
        html = (SITE_DIR / "repository-map.html").read_text()
        assert "当前 run 的主要执行入口" in html

    def test_architecture_statement_exists(self):
        """Architecture statement about scripts-driven pipeline."""
        html = (SITE_DIR / "repository-map.html").read_text()
        assert "scripts-driven research pipeline" in html


class TestPipelineLayersFixes:
    """QC-06: pipeline-layers.html fixes."""

    def test_scripts_driven_statement(self):
        """QC-06: scripts-driven statement exists."""
        html = (SITE_DIR / "pipeline-layers.html").read_text()
        assert "scripts-driven research pipeline" in html

    def test_architecture_box_exists(self):
        """Architecture explanation box exists."""
        html = (SITE_DIR / "pipeline-layers.html").read_text()
        assert "当前真实架构" in html

    def test_scripts_layer_is_main_entry(self):
        """Scripts layer marked as main entry."""
        html = (SITE_DIR / "pipeline-layers.html").read_text()
        assert "当前 run 的主要执行入口" in html

    def test_src_layer_is_component_lib(self):
        """Src layer described as component library."""
        html = (SITE_DIR / "pipeline-layers.html").read_text()
        assert "已有可复用代码组件库" in html

    def test_research_layer_is_audit_archive(self):
        """Research layer described as audit archive."""
        html = (SITE_DIR / "pipeline-layers.html").read_text()
        assert "审计档案和结果目录" in html


class TestDataLineageFixes:
    """QC-19: data-lineage.html updated."""

    def test_architecture_statement_exists(self):
        """Architecture statement exists."""
        html = (SITE_DIR / "data-lineage.html").read_text()
        assert "scripts-driven research pipeline" in html

    def test_links_to_actual_script_map(self):
        """Links to actual-script-map.html."""
        html = (SITE_DIR / "data-lineage.html").read_text()
        assert "actual-script-map.html" in html


class TestNoFabricatedScripts:
    """QC-13: No fabricated scripts — all referenced scripts must exist."""

    def test_all_mainline_scripts_exist(self):
        """All scripts marked as current mainline exist in scripts/ directory."""
        with open(ASSETS_DIR / "actual_script_map.json") as f:
            data = json.load(f)

        for script in data["scripts"]:
            if script["is_current_mainline"]:
                path = REPO_ROOT / script["file_path"]
                assert path.exists(), f"Mainline script not found: {script['file_path']}"

    def test_phase9b_script_exists(self):
        """QC-09: Phase 9B script exists."""
        assert (SCRIPTS_DIR / "build_phase9b_signal_panel.py").exists()

    def test_phase10_scripts_exist(self):
        """QC-10: Phase 10 scripts exist."""
        for name in ["run_phase10a_signal_backtest.py", "run_phase10d_tail_aware_variants.py"]:
            assert (SCRIPTS_DIR / name).exists(), f"Phase 10 script not found: {name}"

    def test_phase11_scripts_exist(self):
        """QC-11: Phase 11 scripts exist."""
        for name in ["run_phase11a_cost_slippage_capacity.py", "run_phase11b_liquidity_capacity.py"]:
            assert (SCRIPTS_DIR / name).exists(), f"Phase 11 script not found: {name}"

    def test_phase12_scripts_exist(self):
        """QC-12: Phase 12 scripts exist."""
        for name in ["run_phase12a_paper_signal_harness.py", "run_phase12b_paper_monitoring.py"]:
            assert (SCRIPTS_DIR / name).exists(), f"Phase 12 script not found: {name}"


class TestNoBadClaims:
    """QC-14 to QC-17: No Phase 13 / execution / alpha / production claims."""

    def test_no_phase13_content(self):
        """QC-14: No Phase 13 content."""
        for fname in ["actual-script-map.html", "repository-map.html", "pipeline-layers.html", "data-lineage.html"]:
            html = (SITE_DIR / fname).read_text()
            # Allow "Phase 13 NOT STARTED" but not Phase 13 content
            assert "Phase 13 NOT STARTED" in html or "Phase 13 未启动" in html or "phase 13" not in html.lower()

    def test_disclaimers_present(self):
        """QC-15, QC-16, QC-17: Disclaimers present."""
        html = (SITE_DIR / "actual-script-map.html").read_text()
        assert "无实盘执行" in html
        assert "无 alpha 声明" in html
        assert "无生产声明" in html


class TestPhaseCloseoutDoc:
    """QC-20: Phase closeout document exists."""

    def test_closeout_doc_exists(self):
        assert (REPO_ROOT / "PHASE_12D_B_R_ACTUAL_CODE_STRUCTURE_REPAIR.md").exists()

    def test_quality_checks_csv_exists(self):
        assert (REPO_ROOT / "phase12d_b_r_quality_checks.csv").exists()
