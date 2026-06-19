"""Tests for evaluate_signals.py: CLI args, imports, archive status."""

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "evaluate_signals.py"
SOURCE = SCRIPT.read_text()


def test_help_runs():
    """--help should exit 0."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "signal-panel" in result.stdout


def test_required_args():
    """Missing required args should fail."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True, text=True
    )
    assert result.returncode != 0


def test_imports_from_public_api():
    """Must import from momentum.signal_evaluation, not old scripts."""
    assert "from momentum.signal_evaluation import" in SOURCE
    assert "run_phase10a" not in SOURCE
    assert "run_phase10b" not in SOURCE
    assert "run_phase10d" not in SOURCE


def test_no_inline_rank_ic():
    """Must not define inline rank_ic functions."""
    assert "def fast_rank_ic" not in SOURCE
    assert "def compute_rankic" not in SOURCE


def test_no_inline_spread():
    """Must not define inline spread functions."""
    assert "def fast_quantile_spread" not in SOURCE


def test_spread_mode_arg():
    """Must support --spread-mode."""
    assert "--spread-mode" in SOURCE
    assert "standard" in SOURCE
    assert "legacy_phase10a" in SOURCE


def test_default_spread_mode_is_standard():
    """Default spread mode must be 'standard', not legacy."""
    assert 'default="standard"' in SOURCE


def test_writes_manifest():
    """Must write a manifest JSON."""
    assert "signal_evaluation_manifest.json" in SOURCE


def test_old_scripts_are_stubs():
    """Old Phase 10 scripts should be stubs (deprecated)."""
    stubs_dir = Path(__file__).resolve().parents[2] / "scripts"
    for name in [
        "run_phase10a_signal_backtest.py",
        "run_phase10a_r_diagnostics.py",
        "run_phase10b_tail_diagnostics.py",
        "run_phase10d_tail_aware_variants.py",
    ]:
        stub = stubs_dir / name
        if stub.exists():
            content = stub.read_text()
            assert "DEPRECATED" in content, f"{name} is not a stub"
            assert "evaluate_signals.py" in content, f"{name} doesn't reference new entrypoint"


def test_archive_readme_exists():
    """Archive README must exist."""
    readme = Path(__file__).resolve().parents[2] / "archive" / "legacy_phase_scripts" / "phase10" / "README.md"
    assert readme.exists()
    content = readme.read_text()
    assert "evaluate_signals.py" in content
