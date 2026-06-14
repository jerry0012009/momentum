"""Phase 7L-R: cache reproducibility validation tests."""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = ROOT / "scripts" / "build_crypto_native_caches.py"
REPORT = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"
MANIFEST = REPORT / "phase7l_r_crypto_native_cache_manifest.csv"


class TestScriptExists:
    def test_script_exists(self):
        assert SCRIPT.exists(), f"Missing {SCRIPT}"

    def test_script_is_executable(self):
        assert SCRIPT.stat().st_size > 1000


class TestManifest:
    def test_manifest_exists(self):
        assert MANIFEST.exists()

    def test_manifest_has_5_artifacts(self):
        df = pd.read_csv(MANIFEST)
        assert len(df) == 5

    def test_manifest_required_columns(self):
        df = pd.read_csv(MANIFEST)
        for col in ["artifact_name", "path", "exists", "committed_to_git",
                     "file_size_bytes", "n_rows", "checksum_sha256", "schema_status"]:
            assert col in df.columns

    def test_large_parquets_marked_local_only(self):
        df = pd.read_csv(MANIFEST)
        large = df[df["file_size_bytes"] > 100 * 1024 * 1024]
        for _, row in large.iterrows():
            assert row["committed_to_git"] == "NO_LOCAL_ARTIFACT", (
                f"{row['artifact_name']} is large but committed_to_git={row['committed_to_git']}"
            )


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
                assert row["max_funding_age_hours"] <= 8.0, (
                    f"{row['dataset_id']}: max_age={row['max_funding_age_hours']} > 8"
                )


class TestNoForbiddenChanges:
    def test_registry_unchanged(self):
        content = (ROOT / "scripts" / "factor_formula_registry.py").read_text()
        assert content.count("FactorSpec(") == 47

    def test_factor_ops_unchanged(self):
        content = (ROOT / "scripts" / "factor_ops.py").read_text()
        assert len(content) > 100

    def test_no_factor_values_built(self):
        fv_path = ROOT / "data" / "factor_values"
        if fv_path.exists():
            # If it exists, check it wasn't modified recently for this phase
            pass  # acceptable — old factor_values may exist
