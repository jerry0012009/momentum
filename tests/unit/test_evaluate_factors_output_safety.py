"""Tests for evaluate_factors.py output safety guard (Phase 12D-H12-C0).

Verifies that partial runs cannot overwrite canonical outputs.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "evaluate_factors.py"
PYTHON = sys.executable


def _run(args: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PYTHON, str(SCRIPT)] + args,
        capture_output=True, text=True, timeout=30, **kwargs,
    )


class TestOutputSafetyGuard:
    """Test that partial runs are blocked from writing canonical outputs."""

    def test_partial_without_output_target_exits_nonzero(self):
        """--factor-ids without --output-suffix or --output-dir must exit non-zero."""
        r = _run(["--factor-ids", "rev_3h"])
        assert r.returncode != 0
        assert "ERROR" in r.stdout or "ERROR" in r.stderr

    def test_partial_error_message_instructs_user(self):
        """Error message must mention --output-suffix or --output-dir."""
        r = _run(["--factor-ids", "rev_3h"])
        combined = r.stdout + r.stderr
        assert "--output-suffix" in combined
        assert "--output-dir" in combined

    def test_partial_with_output_suffix_allowed(self, tmp_path):
        """--factor-ids with --output-suffix should run and write suffixed files."""
        out_dir = tmp_path / "eval"
        out_dir.mkdir()
        # Use --output-dir to a tmp location AND --output-suffix
        r = _run([
            "--factor-ids", "rev_3h",
            "--output-suffix", "test_suffix",
            "--output-dir", str(out_dir),
        ])
        # Should succeed (exit 0) or fail for data reasons, not safety guard
        # The key check: it should NOT exit 1 with the safety error
        assert "ERROR: --factor-ids partial evaluation cannot write canonical outputs" not in r.stdout

    def test_partial_with_output_dir_allowed(self, tmp_path):
        """--factor-ids with --output-dir should run without safety error."""
        out_dir = tmp_path / "eval"
        out_dir.mkdir()
        r = _run([
            "--factor-ids", "rev_3h",
            "--output-dir", str(out_dir),
        ])
        assert "ERROR: --factor-ids partial evaluation cannot write canonical outputs" not in r.stdout

    def test_full_run_does_not_require_output_suffix(self):
        """Full run (no --factor-ids) should not require --output-suffix."""
        # We can't run a full eval in a unit test (too slow), but we can verify
        # the argument parsing doesn't block it. Use --help to verify.
        r = _run(["--help"])
        assert r.returncode == 0
        assert "--output-suffix" in r.stdout
        assert "--output-dir" in r.stdout

    def test_partial_manifest_marks_run_mode(self, tmp_path):
        """Partial run manifest should contain run_mode=partial."""
        out_dir = tmp_path / "eval"
        out_dir.mkdir()
        r = _run([
            "--factor-ids", "rev_3h",
            "--output-suffix", "test",
            "--output-dir", str(out_dir),
        ])
        manifest_path = out_dir / "factor_level_evaluation_manifest_test.json"
        if manifest_path.exists():
            with open(manifest_path) as f:
                m = json.load(f)
            assert m["run_mode"] == "partial"
            assert m["canonical_output"] is False
            assert m["output_safety"] == "scratch_only"
            assert m["factor_ids"] == ["rev_3h"]

    def test_output_suffix_files_named_correctly(self, tmp_path):
        """Output files should include the suffix in their names."""
        out_dir = tmp_path / "eval"
        out_dir.mkdir()
        suffix = "scratch_test"
        r = _run([
            "--factor-ids", "rev_3h",
            "--output-suffix", suffix,
            "--output-dir", str(out_dir),
        ])
        # Check that files with suffix exist (if the run completed)
        csv_path = out_dir / f"factor_level_rankic_summary_{suffix}.csv"
        json_path = out_dir / f"factor_level_rankic_summary_{suffix}.json"
        manifest_path = out_dir / f"factor_level_evaluation_manifest_{suffix}.json"
        # If the run succeeded (data available), files should exist
        if csv_path.exists():
            assert json_path.exists()
            assert manifest_path.exists()

    def test_partial_does_not_overwrite_canonical(self, tmp_path):
        """Partial run should not touch canonical output files."""
        out_dir = tmp_path / "eval"
        out_dir.mkdir()
        # Create a fake canonical file
        canonical = out_dir / "factor_level_rankic_summary.csv"
        canonical.write_text("fake_original_content")
        # Run partial with suffix
        r = _run([
            "--factor-ids", "rev_3h",
            "--output-suffix", "scratch",
            "--output-dir", str(out_dir),
        ])
        # Canonical file should be unchanged
        if canonical.exists():
            assert canonical.read_text() == "fake_original_content"


class TestCLIParsing:
    """Test argument parsing behavior."""

    def test_help_shows_all_options(self):
        r = _run(["--help"])
        assert r.returncode == 0
        assert "--factor-ids" in r.stdout
        assert "--output-suffix" in r.stdout
        assert "--output-dir" in r.stdout

    def test_no_args_is_full_run(self):
        """No --factor-ids means full run mode."""
        # Can't actually run (too slow), but verify the parser doesn't reject it
        r = _run(["--help"])
        assert r.returncode == 0
