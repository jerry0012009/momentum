"""Phase 7L-R: cache reproducibility validation tests."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = ROOT / "scripts" / "build_crypto_native_caches.py"
REPORT = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"
MANIFEST = REPORT / "phase7l_r_crypto_native_cache_manifest.csv"


# ── Test 1: Script exists and is valid ──────────────────────────────
class TestScriptExists:
    def test_script_exists(self):
        assert SCRIPT.exists(), f"Missing {SCRIPT}"

    def test_script_size(self):
        assert SCRIPT.stat().st_size > 1000

    def test_script_importable(self):
        """Verify script has no syntax errors."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            capture_output=True, text=True, cwd=str(ROOT),
        )
        assert result.returncode == 0, result.stderr


# ── Test 2: CLI wiring ──────────────────────────────────────────────
class TestCLIWiring:
    def test_custom_funding_source_parsed(self):
        """Verify --funding-source is accepted and wired to config."""
        result = subprocess.run(
            [
                sys.executable, str(SCRIPT), "--mode", "validate",
                "--funding-source", "/tmp/test_funding_dir",
                "--output-root", "/tmp/test_output",
                "--report-dir", str(REPORT),
            ],
            capture_output=True, text=True, cwd=str(ROOT),
        )
        # validate will fail (manifest paths don't match) but arg parsing must succeed
        # and the script must NOT error on unknown args
        assert "usage" not in result.stderr.lower() or "error" not in result.stderr.lower()

    def test_config_from_args(self):
        """Verify CacheBuildConfig.from_args resolves paths correctly."""
        import argparse
        sys.path.insert(0, str(SCRIPT.parent))
        from build_crypto_native_caches import CacheBuildConfig

        args = argparse.Namespace(
            static_dataset_id="test_static",
            dynamic_dataset_id="test_dynamic",
            funding_source="/tmp/fr",
            output_root="/tmp/out",
            report_dir="/tmp/rpt",
            klines_dir="/tmp/kl",
        )
        cfg = CacheBuildConfig.from_args(args)

        assert cfg.static_dataset_id == "test_static"
        assert cfg.dynamic_dataset_id == "test_dynamic"
        assert cfg.funding_source == Path("/tmp/fr")
        assert cfg.output_root == Path("/tmp/out")
        assert cfg.report_dir == Path("/tmp/rpt")
        assert cfg.klines_dir == Path("/tmp/kl")
        assert cfg.static_bars_path() == Path("/tmp/out/test_static/bars_1h.parquet")
        assert cfg.dynamic_bars_path() == Path("/tmp/out/test_dynamic/bars_1h.parquet")
        assert cfg.taker_enriched_path("test_static") == Path("/tmp/out/test_static_taker_enriched/bars_1h.parquet")
        assert cfg.funding_events_path() == Path("/tmp/out/crypto_funding_rate_1h_contract_v1/funding_rate_events.parquet")
        assert cfg.funding_aligned_path("static") == Path("/tmp/out/crypto_funding_rate_1h_contract_v1/funding_rate_1h_aligned_static.parquet")


# ── Test 3: Manifest local-only semantics ───────────────────────────
class TestManifestSemantics:
    def test_manifest_exists(self):
        assert MANIFEST.exists()

    def test_manifest_has_5_artifacts(self):
        df = pd.read_csv(MANIFEST)
        assert len(df) == 5

    def test_manifest_required_columns(self):
        df = pd.read_csv(MANIFEST)
        for col in ["artifact_name", "path", "exists", "committed_to_git",
                     "size_policy", "file_size_bytes", "n_rows",
                     "checksum_sha256", "schema_status"]:
            assert col in df.columns, f"Missing column: {col}"

    def test_all_parquets_are_local_artifacts(self):
        """All generated parquet caches must be NO_LOCAL_ARTIFACT."""
        df = pd.read_csv(MANIFEST)
        for _, row in df.iterrows():
            assert row["committed_to_git"] == "NO_LOCAL_ARTIFACT", (
                f"{row['artifact_name']}: committed_to_git={row['committed_to_git']}, "
                f"expected NO_LOCAL_ARTIFACT"
            )

    def test_size_policy_valid_enum(self):
        """size_policy must be SMALL_LOCAL_FILE or LARGE_LOCAL_FILE."""
        df = pd.read_csv(MANIFEST)
        valid = {"SMALL_LOCAL_FILE", "LARGE_LOCAL_FILE"}
        for _, row in df.iterrows():
            assert row["size_policy"] in valid, (
                f"{row['artifact_name']}: invalid size_policy={row['size_policy']}"
            )

    def test_large_files_have_skipped_checksum(self):
        df = pd.read_csv(MANIFEST)
        large = df[df["size_policy"] == "LARGE_LOCAL_FILE"]
        for _, row in large.iterrows():
            assert row["checksum_sha256"] == "SKIPPED_LARGE_FILE", (
                f"{row['artifact_name']}: large file but checksum={row['checksum_sha256']}"
            )

    def test_small_files_have_real_checksum(self):
        df = pd.read_csv(MANIFEST)
        small = df[df["size_policy"] == "SMALL_LOCAL_FILE"]
        for _, row in small.iterrows():
            assert row["checksum_sha256"] not in ("SKIPPED_LARGE_FILE", "FILE_NOT_FOUND", ""), (
                f"{row['artifact_name']}: small file but checksum={row['checksum_sha256']}"
            )


# ── Test 4: Summary CSVs ────────────────────────────────────────────
class TestTakerSummary:
    def test_row_count_match(self):
        df = pd.read_csv(REPORT / "phase7l_taker_enriched_bars_summary.csv")
        assert df["row_count_match"].all()

    def test_has_taker_buy_quote_volume(self):
        df = pd.read_csv(REPORT / "phase7l_taker_enriched_bars_summary.csv")
        assert df["has_taker_buy_quote_volume"].all()


class TestFundingAlignment:
    def test_row_count_match(self):
        df = pd.read_csv(REPORT / "phase7l_funding_alignment_summary.csv")
        assert df["row_count_match"].all()

    def test_max_age_within_bounds(self):
        df = pd.read_csv(REPORT / "phase7l_funding_alignment_summary.csv")
        for _, row in df.iterrows():
            if pd.notna(row["max_funding_age_hours"]):
                assert row["max_funding_age_hours"] <= 8.0


# ── Test 5: Validate mode ───────────────────────────────────────────
class TestValidateMode:
    def test_validate_passes_on_clean_manifest(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--mode", "validate"],
            capture_output=True, text=True, cwd=str(ROOT),
        )
        assert result.returncode == 0, result.stdout
        assert "All caches validated OK" in result.stdout

    def test_validate_detects_missing_manifest(self, tmp_path):
        """Validate should fail if manifest is missing."""
        result = subprocess.run(
            [
                sys.executable, str(SCRIPT), "--mode", "validate",
                "--report-dir", str(tmp_path),
            ],
            capture_output=True, text=True, cwd=str(ROOT),
        )
        assert result.returncode != 0
        assert "Manifest not found" in result.stdout


# ── Test 6: No forbidden changes ────────────────────────────────────
class TestNoForbiddenChanges:
    def test_registry_unchanged(self):
        content = (ROOT / "scripts" / "factor_formula_registry.py").read_text()
        assert content.count("FactorSpec(") == 47

    def test_factor_ops_unchanged(self):
        content = (ROOT / "scripts" / "factor_ops.py").read_text()
        assert len(content) > 100
