"""Governance staleness check — ensure active docs don't contain stale counts."""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

# Files that are actively maintained governance docs (not historical snapshots)
ACTIVE_GOVERNANCE_FILES = [
    "README.md",
    "docs/factor_library/START_HERE.md",
    "docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md",
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
