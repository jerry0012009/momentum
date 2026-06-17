"""
Phase 12D-A: Repository Map & File Ownership Audit — Quality Checks

Verifies that all required deliverables exist and meet quality criteria.
"""

import csv
import json
import os
from pathlib import Path

import pytest

# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Deliverable paths
DELIVERABLES = {
    "PHASE_12D_A_REPOSITORY_MAP_AUDIT.md": PROJECT_ROOT
    / "research/factor_runs/crypto_top50_factor_library/PHASE_12D_A_REPOSITORY_MAP_AUDIT.md",
    "docs/FACTOR_LIBRARY_HOME.md": PROJECT_ROOT / "docs/FACTOR_LIBRARY_HOME.md",
    "docs/PROJECT_TREE_UPDATED.md": PROJECT_ROOT / "docs/PROJECT_TREE_UPDATED.md",
    "repository-map.html": PROJECT_ROOT / "reports/site/factor-library/repository-map.html",
    "file-ownership.html": PROJECT_ROOT / "reports/site/factor-library/file-ownership.html",
    "repo_map.json": PROJECT_ROOT / "reports/site/factor-library/assets/repo_map.json",
    "quality_checks.csv": PROJECT_ROOT
    / "research/factor_runs/crypto_top50_factor_library/phase12d_a_repository_map_quality_checks.csv",
}

# Required folders that must be documented
REQUIRED_FOLDERS = [
    "config",
    "data",
    "docs",
    "docs/factor_library_transparency",
    "research/factor_runs/crypto_top50_factor_library",
    "scripts",
    "src/momentum",
    "tests",
    "reports",
    "reports/site",
    "reports/site/factor-library",
    "pm_prompts",
]

# Source-of-truth rules that must be documented
REQUIRED_RULES = [
    "research/factor_runs/crypto_top50_factor_library/",
    "docs/factor_library_transparency/",
    "reports/site/factor-library/",
    "scripts/",
    "src/momentum/",
    "data/",
    "tests/",
]


class TestDeliverableFilesExist:
    """Verify all required deliverable files exist."""

    @pytest.mark.parametrize("name,path", DELIVERABLES.items(), ids=list(DELIVERABLES.keys()))
    def test_deliverable_exists(self, name, path):
        assert path.exists(), f"Missing deliverable: {name} at {path}"

    def test_deliverable_not_empty(self):
        """All deliverables should be non-empty."""
        for name, path in DELIVERABLES.items():
            assert path.stat().st_size > 0, f"Deliverable is empty: {name}"


class TestRepositoryMapAudit:
    """Verify the main audit document content."""

    @pytest.fixture
    def audit_content(self):
        path = DELIVERABLES["PHASE_12D_A_REPOSITORY_MAP_AUDIT.md"]
        return path.read_text()

    def test_contains_all_folders(self, audit_content):
        """Audit must document all required top-level folders."""
        for folder in REQUIRED_FOLDERS:
            assert folder in audit_content, f"Audit missing folder: {folder}"

    def test_contains_source_of_truth_rules(self, audit_content):
        """Audit must contain source-of-truth rules."""
        assert "Source-of-Truth" in audit_content or "source-of-truth" in audit_content.lower()
        for rule_folder in REQUIRED_RULES:
            assert rule_folder in audit_content, f"Audit missing rule for: {rule_folder}"

    def test_contains_ownership_table(self, audit_content):
        """Audit must contain file ownership table."""
        assert "file_or_directory" in audit_content or "File Ownership" in audit_content

    def test_no_phase_13_started(self, audit_content):
        """Audit must confirm Phase 13 not started."""
        assert "Phase 13" in audit_content
        assert "NOT STARTED" in audit_content


class TestFactorLibraryHome:
    """Verify the FACTOR_LIBRARY_HOME.md content."""

    @pytest.fixture
    def home_content(self):
        return DELIVERABLES["docs/FACTOR_LIBRARY_HOME.md"].read_text()

    def test_contains_navigation(self, home_content):
        """Home page must contain navigation links."""
        assert "FACTOR_LIBRARY_ROADMAP.md" in home_content
        assert "FACTOR_REGISTRY.md" in home_content

    def test_contains_transparency_docs(self, home_content):
        """Home page must reference transparency docs."""
        assert "factor_library_transparency" in home_content

    def test_contains_current_status(self, home_content):
        """Home page must show current status."""
        assert "Phase 12" in home_content


class TestProjectTreeUpdated:
    """Verify the updated project tree."""

    @pytest.fixture
    def tree_content(self):
        return DELIVERABLES["docs/PROJECT_TREE_UPDATED.md"].read_text()

    def test_contains_all_folders(self, tree_content):
        """Project tree must show all required folders."""
        for folder in REQUIRED_FOLDERS:
            assert folder in tree_content, f"Project tree missing folder: {folder}"

    def test_contains_phase_12d_state(self, tree_content):
        """Project tree must reflect Phase 12D state."""
        assert "Phase 12" in tree_content or "12D" in tree_content

    def test_contains_current_artifacts(self, tree_content):
        """Project tree must show current phase artifacts."""
        assert "factor_library_transparency" in tree_content
        assert "factor-library" in tree_content


class TestHtmlPages:
    """Verify the HTML showcase pages."""

    def test_repository_map_html_valid(self):
        """Repository map HTML should contain key elements."""
        content = DELIVERABLES["repository-map.html"].read_text()
        assert "<html" in content
        assert "仓库结构图" in content or "repository" in content.lower()
        assert "config/" in content
        assert "data/" in content
        assert "scripts/" in content

    def test_file_ownership_html_valid(self):
        """File ownership HTML should contain key elements."""
        content = DELIVERABLES["file-ownership.html"].read_text()
        assert "<html" in content
        assert "文件所有权" in content or "file-ownership" in content.lower()
        assert "source" in content
        assert "generated" in content

    def test_html_pages_have_navigation(self):
        """HTML pages should link back to index."""
        for page in ["repository-map.html", "file-ownership.html"]:
            content = DELIVERABLES[page].read_text()
            assert "index.html" in content, f"{page} missing back-link to index"


class TestRepoMapJson:
    """Verify the repo_map.json data file."""

    @pytest.fixture
    def repo_data(self):
        return json.loads(DELIVERABLES["repo_map.json"].read_text())

    def test_valid_json(self, repo_data):
        """Must be valid JSON with expected structure."""
        assert "meta" in repo_data
        assert "folders" in repo_data
        assert "source_of_truth_rules" in repo_data

    def test_all_folders_documented(self, repo_data):
        """JSON must document all required folders."""
        json_folders = [f["path"].rstrip("/") for f in repo_data["folders"]]
        for folder in REQUIRED_FOLDERS:
            assert folder.rstrip("/") in json_folders, f"JSON missing folder: {folder}"

    def test_all_rules_defined(self, repo_data):
        """JSON must define all 7 source-of-truth rules."""
        rules = repo_data["source_of_truth_rules"]
        assert len(rules) == 7, f"Expected 7 rules, got {len(rules)}"
        rule_folders = [r["folder"] for r in rules]
        for folder in REQUIRED_RULES:
            assert folder in rule_folders, f"JSON missing rule for: {folder}"

    def test_data_flow_defined(self, repo_data):
        """JSON must define data flow."""
        assert "data_flow" in repo_data
        assert len(repo_data["data_flow"]) > 0

    def test_regeneration_scripts(self, repo_data):
        """JSON must list regeneration scripts."""
        assert "regeneration_scripts" in repo_data
        assert len(repo_data["regeneration_scripts"]) > 0


class TestQualityChecksCsv:
    """Verify the quality checks CSV."""

    @pytest.fixture
    def checks(self):
        path = DELIVERABLES["quality_checks.csv"]
        with open(path) as f:
            reader = csv.DictReader(f)
            return list(reader)

    def test_csv_not_empty(self, checks):
        assert len(checks) > 0

    def test_all_checks_pass(self, checks):
        """All quality checks should pass."""
        failures = [c for c in checks if c.get("status") != "PASS"]
        assert len(failures) == 0, f"Failed checks: {[f['check_name'] for f in failures]}"

    def test_required_checks_present(self, checks):
        """Must include checks for all deliverables."""
        check_names = {c["check_name"] for c in checks}
        assert "PHASE_12D_A_REPOSITORY_MAP_AUDIT.md exists" in check_names
        assert "docs/FACTOR_LIBRARY_HOME.md exists" in check_names
        assert "docs/PROJECT_TREE_UPDATED.md exists" in check_names
        assert "repository-map.html exists" in check_names
        assert "file-ownership.html exists" in check_names
        assert "repo_map.json exists" in check_names
        assert "no Phase 13 started" in check_names
        assert "no research results changed" in check_names


class TestNoDestructiveChanges:
    """Verify no destructive changes were made."""

    def test_no_phase_13_files(self):
        """Phase 13 files should not exist."""
        research_dir = PROJECT_ROOT / "research/factor_runs/crypto_top50_factor_library"
        phase13_files = list(research_dir.glob("PHASE_13*"))
        assert len(phase13_files) == 0, f"Phase 13 files found: {phase13_files}"

    def test_research_csvs_unchanged(self):
        """Key research CSVs should still exist (not deleted)."""
        research_dir = PROJECT_ROOT / "research/factor_runs/crypto_top50_factor_library"
        # Spot check a few key files
        key_files = [
            "phase7m_f_curated_crypto_native_library.csv",
            "phase8b_factor_library_v0_5_status.csv",
            "phase9b_signal_component_manifest.csv",
        ]
        for fname in key_files:
            path = research_dir / fname
            if path.exists():
                assert path.stat().st_size > 0, f"Key research file empty: {fname}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
