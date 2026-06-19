"""Tests for H3-R: verify stubs removed, archive intact, docs updated."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_no_phase10_stubs_in_scripts():
    """Active scripts/ must not contain Phase 10 files."""
    scripts = ROOT / "scripts"
    for name in [
        "run_phase10a_signal_backtest.py",
        "run_phase10a_r_diagnostics.py",
        "run_phase10b_tail_diagnostics.py",
        "run_phase10d_tail_aware_variants.py",
    ]:
        assert not (scripts / name).exists(), f"{name} should not be in scripts/"


def test_archive_has_all_files():
    """Archive must contain all 4 legacy scripts + README."""
    archive = ROOT / "archive" / "legacy_phase_scripts" / "phase10"
    assert archive.exists()
    for name in [
        "run_phase10a_signal_backtest.py",
        "run_phase10a_r_diagnostics.py",
        "run_phase10b_tail_diagnostics.py",
        "run_phase10d_tail_aware_variants.py",
        "README.md",
    ]:
        assert (archive / name).exists(), f"{name} missing from archive"


def test_evaluate_signals_exists():
    """Canonical entrypoint must exist."""
    assert (ROOT / "scripts" / "evaluate_signals.py").exists()


def test_active_pipeline_doc_exists():
    """ACTIVE_SIGNAL_EVALUATION_PIPELINE.md must exist."""
    doc = ROOT / "docs" / "refactor" / "ACTIVE_SIGNAL_EVALUATION_PIPELINE.md"
    assert doc.exists()
    content = doc.read_text()
    assert "evaluate_signals.py" in content
    assert "archive" in content


def test_actual_script_map_mentions_archived():
    """actual_script_map.md must mention archived scripts."""
    doc = ROOT / "docs" / "factor_library_transparency" / "actual_script_map.md"
    assert doc.exists()
    content = doc.read_text()
    assert "归档" in content or "archived" in content.lower()
    assert "evaluate_signals.py" in content
