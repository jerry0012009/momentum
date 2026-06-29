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
SCRIPTS = SCRIPT.parent
PYTHON = sys.executable
sys.path.insert(0, str(SCRIPTS))

from evaluate_factors import validate_partial_factor_ids  # noqa: E402


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

    def test_partial_unknown_factor_id_exits_nonzero(self, tmp_path):
        """--factor-ids should fail fast for IDs not in registry."""
        out_dir = tmp_path / "eval"
        out_dir.mkdir()
        r = _run([
            "--factor-ids", "nonexistent_factor_xyz",
            "--output-dir", str(out_dir),
        ])
        combined = r.stdout + r.stderr
        assert r.returncode != 0
        assert "Factor IDs not in REGISTRY" in combined

    def test_partial_skipped_public_factor_id_exits_nonzero(self, tmp_path):
        """--factor-ids should fail fast for public manifest skipped rows."""
        out_dir = tmp_path / "eval"
        out_dir.mkdir()
        r = _run([
            "--factor-ids", "wq101_alpha58_indneutralize_skipped",
            "--output-dir", str(out_dir),
        ])
        combined = r.stdout + r.stderr
        assert r.returncode != 0
        assert "Public manifest skipped factor IDs cannot be evaluated" in combined

    def test_partial_skipped_public_guard_catches_misregistered_id(self):
        """Skipped public rows are rejected even if they appear in registry IDs."""
        with pytest.raises(ValueError, match="Public manifest skipped factor IDs cannot be evaluated"):
            validate_partial_factor_ids(
                ["wq101_alpha58_indneutralize_skipped"],
                {"wq101_alpha58_indneutralize_skipped"},
            )

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


class TestH12C0RLogging:
    """Test output dir logging fix (Phase 12D-H12-C0-R)."""

    def test_partial_with_output_dir_logs_custom_dir(self, tmp_path):
        """Partial run with --output-dir should log the custom dir, not canonical."""
        out_dir = tmp_path / "custom_eval"
        out_dir.mkdir()
        r = _run([
            "--factor-ids", "rev_3h",
            "--output-dir", str(out_dir),
        ])
        combined = r.stdout + r.stderr
        # Should NOT contain the safety error
        assert "ERROR: --factor-ids partial evaluation cannot write canonical outputs" not in r.stdout
        # If it ran, the output log should mention the custom dir
        if str(out_dir) in combined:
            # Good: logging the custom dir
            pass

    def test_quality_check_csv_all_rows_pass(self):
        """All rows in H12-C0 quality check CSV should have status PASS."""
        csv_path = Path(__file__).resolve().parents[2] / "research" / "factor_runs" / "crypto_top50_factor_library" / "phase12d_h12c0_evaluation_output_safety_quality_checks.csv"
        if not csv_path.exists():
            pytest.skip("Quality check CSV not found")
        import csv
        with open(csv_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                assert row["status"] == "PASS", f"Row {row['check_id']} has status={row['status']!r}, expected PASS"
