"""Governance staleness check — ensure active docs don't contain stale counts."""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

# Files that are actively maintained governance docs (not historical snapshots)
ACTIVE_GOVERNANCE_FILES = [
    "README.md",
    "scripts/README.md",
    "docs/DOCS_INDEX.md",
    "docs/FACTOR_LIBRARY_HOME.md",
    "docs/factor_library/START_HERE.md",
    "docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md",
    "docs/factor_library/PROJECT_HANDOFF_FACTOR_LIBRARY.md",
    "docs/factor_library/factor_library_manifest.json",
    "docs/factor_library/PHASE_13A_P0_CONTROL_SURFACE_REPAIR_SUMMARY.md",
]

ACTIVE_PUBLIC_HTML_FILES = [
    "reports/site/factor-library/index.html",
    "reports/site/factor-library/actual-script-map.html",
]

# Stale patterns that should NOT appear in active governance docs
STALE_PATTERNS = [
    "53 registered",
    "47 computed",
    "53 factors",
    "47 factors",
    "registered factors: 53",
    "computed factors: roughly 47",
    "\"total_registered\": 53",
    "\"with_factor_values\": 47",
    "\"computed_factors\": 47",
    "Phase 13 NOT STARTED",
    "Phase 13 not started",
]


def _grep_file(filepath: Path, pattern: str) -> list[str]:
    """Search for pattern in file, return matching lines."""
    try:
        content = filepath.read_text()
        return [line for line in content.split("\n") if pattern in line]
    except FileNotFoundError:
        return []


@pytest.mark.parametrize("pattern", STALE_PATTERNS)
def test_active_governance_docs_no_stale_counts(pattern):
    """Active governance docs must not contain stale factor counts."""
    for relpath in ACTIVE_GOVERNANCE_FILES:
        fpath = ROOT / relpath
        if not fpath.exists():
            continue
        matches = _grep_file(fpath, pattern)
        assert not matches, f"{relpath} contains stale pattern '{pattern}': {matches}"


@pytest.mark.parametrize("pattern", STALE_PATTERNS)
def test_active_public_html_no_stale_counts(pattern):
    """Active public HTML pages must not contain stale factor counts."""
    for relpath in ACTIVE_PUBLIC_HTML_FILES:
        fpath = ROOT / relpath
        if not fpath.exists():
            continue
        matches = _grep_file(fpath, pattern)
        assert not matches, f"{relpath} contains stale pattern '{pattern}': {matches}"


def test_factor_intake_is_documented_as_default_route():
    """Active docs should point new-factor work to run_factor_intake.py."""
    required_files = [
        "README.md",
        "scripts/README.md",
        "docs/factor_library/START_HERE.md",
        "docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md",
        "docs/factor_library/PROJECT_HANDOFF_FACTOR_LIBRARY.md",
    ]
    for relpath in required_files:
        content = (ROOT / relpath).read_text()
        assert "run_factor_intake.py" in content, f"{relpath} does not mention run_factor_intake.py"


def test_old_portals_marked_superseded():
    """Old portal docs must not look like current planning authority."""
    portal_files = [
        "docs/DOCS_INDEX.md",
        "docs/FACTOR_LIBRARY_HOME.md",
        "docs/factor_library_transparency/README.md",
    ]
    for relpath in portal_files:
        content = (ROOT / relpath).read_text()
        assert "SUPERSEDED" in content or "HISTORICAL_ARCHIVE" in content, (
            f"{relpath} must be marked as superseded or historical"
        )
