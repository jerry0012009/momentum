"""
Phase 12D-A-R: Repository Map Repair — Quality Checks

Verifies that all repairs from Phase 12D-A-R were correctly applied.
"""

import csv
import json
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]

FILES = {
    "FACTOR_LIBRARY_HOME.md": PROJECT_ROOT / "docs/FACTOR_LIBRARY_HOME.md",
    "PROJECT_TREE_UPDATED.md": PROJECT_ROOT / "docs/PROJECT_TREE_UPDATED.md",
    "repository-map.html": PROJECT_ROOT / "reports/site/factor-library/repository-map.html",
    "file-ownership.html": PROJECT_ROOT / "reports/site/factor-library/file-ownership.html",
    "repo_map.json": PROJECT_ROOT / "reports/site/factor-library/assets/repo_map.json",
    "PHASE_12D_A_REPOSITORY_MAP_AUDIT.md": PROJECT_ROOT
    / "research/factor_runs/crypto_top50_factor_library/PHASE_12D_A_REPOSITORY_MAP_AUDIT.md",
    "PHASE_12D_A_R_REPOSITORY_MAP_REPAIR.md": PROJECT_ROOT
    / "research/factor_runs/crypto_top50_factor_library/PHASE_12D_A_R_REPOSITORY_MAP_REPAIR.md",
    "phase12d_a_r_quality_checks.csv": PROJECT_ROOT
    / "research/factor_runs/crypto_top50_factor_library/phase12d_a_r_quality_checks.csv",
}


class TestRepairFilesExist:
    """Verify all repair deliverables exist and are non-empty."""

    @pytest.mark.parametrize("name,path", FILES.items(), ids=list(FILES.keys()))
    def test_file_exists(self, name, path):
        assert path.exists(), f"Missing: {name} at {path}"
        assert path.stat().st_size > 0, f"Empty: {name}"


class TestFrameworkVsRunDistinction:
    """Verify the framework vs current run distinction is clear."""

    @pytest.fixture
    def home(self):
        return FILES["FACTOR_LIBRARY_HOME.md"].read_text()

    @pytest.fixture
    def tree(self):
        return FILES["PROJECT_TREE_UPDATED.md"].read_text()

    @pytest.fixture
    def repo_html(self):
        return FILES["repository-map.html"].read_text()

    @pytest.fixture
    def ownership_html(self):
        return FILES["file-ownership.html"].read_text()

    def test_home_distinguishes_framework_from_run(self, home):
        assert "Factor Library Framework" in home or "factor library framework" in home.lower()
        assert "crypto_top50_usdt_perp_1h" in home

    def test_home_run_is_not_framework(self, home):
        """Home should say the run is not the entire framework."""
        assert "not the framework" in home.lower() or "not the entire" in home.lower() or "one run" in home.lower()

    def test_tree_distinguishes_framework_from_run(self, tree):
        assert "crypto_top50_usdt_perp_1h" in tree
        assert "one run" in tree.lower() or "not the entire" in tree.lower()

    def test_repo_html_rule1_mentions_run(self, repo_html):
        """Rule 1 should reference the specific run, not just 'the factor library'."""
        assert "crypto_top50_usdt_perp_1h" in repo_html

    def test_ownership_html_has_framework_note(self, ownership_html):
        """Should have a note distinguishing framework from run."""
        assert "crypto_top50_usdt_perp_1h" in ownership_html
        assert "不是因子库" in ownership_html or "not the" in ownership_html.lower() or "样例" in ownership_html


class TestRoadmapAuthorityCorrection:
    """Verify FACTOR_LIBRARY_ROADMAP.md is no longer called authoritative."""

    @pytest.fixture
    def home(self):
        return FILES["FACTOR_LIBRARY_HOME.md"].read_text()

    @pytest.fixture
    def tree(self):
        return FILES["PROJECT_TREE_UPDATED.md"].read_text()

    @pytest.fixture
    def ownership_html(self):
        return FILES["file-ownership.html"].read_text()

    def test_home_roadmap_not_authoritative(self, home):
        """ROADMAP should be called REFERENCE, not authoritative."""
        lines = [l for l in home.split('\n') if 'ROADMAP' in l]
        for line in lines:
            assert 'authoritative' not in line.lower() or 'reference' in line.lower() or 'historical' in line.lower(), \
                f"ROADMAP still called authoritative: {line}"

    def test_home_roadmap_has_reference_note(self, home):
        """Should have explicit note about ROADMAP being historical."""
        assert "REFERENCE" in home or "historical" in home.lower()

    def test_tree_roadmap_not_authoritative(self, tree):
        lines = [l for l in tree.split('\n') if 'ROADMAP' in l]
        for line in lines:
            assert 'authoritative' not in line.lower() or 'reference' in line.lower() or 'not current' in line.lower(), \
                f"ROADMAP still called authoritative: {line}"

    def test_ownership_roadmap_not_authoritative(self, ownership_html):
        assert "权威" not in ownership_html or "非当前权威" in ownership_html or "REFERENCE" in ownership_html


class TestPhase12C13Status:
    """Verify Phase 12C and Phase 13 status is correct."""

    @pytest.fixture
    def home(self):
        return FILES["FACTOR_LIBRARY_HOME.md"].read_text()

    def test_phase_12c_complete(self, home):
        assert "Phase 12C" in home
        assert "COMPLETE" in home

    def test_phase_13_not_started(self, home):
        assert "Phase 13" in home
        assert "NOT STARTED" in home

    def test_no_old_pm_decision_language(self, home):
        """Should not have the old 'PM decision required: Phase 12C...' language."""
        assert "PM decision required: Phase 12C" not in home


class TestDisclaimers:
    """Verify disclaimers are present in entry documents."""

    @pytest.fixture
    def home(self):
        return FILES["FACTOR_LIBRARY_HOME.md"].read_text()

    @pytest.fixture
    def repo_html(self):
        return FILES["repository-map.html"].read_text()

    def test_home_no_real_execution(self, home):
        assert "No real execution" in home or "no real execution" in home.lower() or "无实盘" in home

    def test_home_no_alpha_claim(self, home):
        assert "No alpha claim" in home or "no alpha claim" in home.lower() or "无 alpha" in home

    def test_home_no_production_claim(self, home):
        assert "No production claim" in home or "no production claim" in home.lower() or "无生产" in home

    def test_repo_html_disclaimers_present(self, repo_html):
        assert "无实盘" in repo_html or "No real execution" in repo_html
        assert "无 alpha" in repo_html or "No alpha claim" in repo_html


class TestRepoMapJson:
    """Verify repo_map.json has the repair data."""

    @pytest.fixture
    def data(self):
        with open(FILES["repo_map.json"]) as f:
            return json.load(f)

    def test_run_id_present(self, data):
        assert data['meta'].get('run_id') == 'crypto_top50_usdt_perp_1h'

    def test_disclaimers_present(self, data):
        assert 'disclaimers' in data
        assert len(data['disclaimers']) >= 3

    def test_document_status_labels(self, data):
        assert 'document_status_labels' in data
        labels = [l['label'] for l in data['document_status_labels']]
        assert 'CURRENT' in labels
        assert 'REFERENCE' in labels
        assert 'GENERATED' in labels

    def test_rule1_mentions_run(self, data):
        rule1 = data['source_of_truth_rules'][0]
        assert 'crypto_top50_usdt_perp_1h' in rule1['description']

    def test_folder_descriptions_updated(self, data):
        research = [f for f in data['folders'] if 'crypto_top50' in f['path']][0]
        assert 'crypto_top50_usdt_perp_1h' in research['purpose'] or 'run' in research['purpose'].lower()


class TestAuditDocSupplemented:
    """Verify PHASE_12D_A audit doc was supplemented."""

    @pytest.fixture
    def content(self):
        return FILES["PHASE_12D_A_REPOSITORY_MAP_AUDIT.md"].read_text()

    def test_framework_vs_run_section(self, content):
        assert "Framework vs Current Run" in content or "Factor Library Framework" in content

    def test_disclaimers_in_audit(self, content):
        assert "No real execution" in content or "no real execution" in content.lower()

    def test_run_id_in_audit(self, content):
        assert "crypto_top50_usdt_perp_1h" in content


class TestQualityChecksCsv:
    """Verify the quality checks CSV."""

    @pytest.fixture
    def checks(self):
        with open(FILES["phase12d_a_r_quality_checks.csv"]) as f:
            return list(csv.DictReader(f))

    def test_csv_not_empty(self, checks):
        assert len(checks) > 0

    def test_all_checks_pass(self, checks):
        failures = [c for c in checks if c.get("status") != "PASS"]
        assert len(failures) == 0, f"Failed: {[f['check_name'] for f in failures]}"

    def test_required_checks_present(self, checks):
        names = {c["check_name"] for c in checks}
        required = [
            "FACTOR_LIBRARY_HOME.md revised",
            "PROJECT_TREE_UPDATED.md revised",
            "repository-map.html revised",
            "file-ownership.html revised",
            "repo_map.json revised",
            "factor_library_framework_vs_run_distinguished",
            "ROADMAP_not_called_authoritative",
            "phase_12c_complete",
            "phase_13_not_started",
            "no_real_execution",
            "no_alpha_claim",
            "no_research_files_moved",
            "no_research_results_changed",
        ]
        for r in required:
            assert r in names, f"Missing check: {r}"


class TestNoDestructiveChanges:
    """Verify no destructive changes were made."""

    def test_no_phase_13_files(self):
        research = PROJECT_ROOT / "research/factor_runs/crypto_top50_factor_library"
        p13 = list(research.glob("PHASE_13*"))
        assert len(p13) == 0, f"Phase 13 files found: {p13}"

    def test_key_research_files_exist(self):
        research = PROJECT_ROOT / "research/factor_runs/crypto_top50_factor_library"
        key = [
            "phase7m_f_curated_crypto_native_library.csv",
            "phase8b_factor_library_v0_5_status.csv",
            "PHASE_12C_GRAND_TRANSPARENCY_CLOSEOUT.md",
        ]
        for fname in key:
            path = research / fname
            assert path.exists(), f"Key file missing: {fname}"
            assert path.stat().st_size > 0, f"Key file empty: {fname}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
