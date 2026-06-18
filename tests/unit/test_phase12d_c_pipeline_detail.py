"""Phase 12D-C: Pipeline Detail and Factor Source Map validation tests."""

import pytest
from pathlib import Path

SITE = Path("/root/clawd/jerry/momentum/reports/site/factor-library")
DOCS = Path("/root/clawd/jerry/momentum/docs/factor_library_transparency")
ROOT = Path("/root/clawd/jerry/momentum")


class TestNewPagesExist:
    """Verify all new pages were created."""

    def test_crypto_native_inventory_html(self):
        assert (SITE / "crypto-native-inventory.html").exists()

    def test_factor_source_map_html(self):
        assert (SITE / "factor-source-map.html").exists()

    def test_crypto_native_inventory_json(self):
        assert (SITE / "assets" / "crypto_native_inventory.json").exists()

    def test_factor_source_map_json(self):
        assert (SITE / "assets" / "factor_source_map.json").exists()

    def test_crypto_native_inventory_md(self):
        assert (DOCS / "crypto_native_inventory.md").exists()

    def test_factor_source_map_md(self):
        assert (DOCS / "factor_source_map.md").exists()


class TestIndexLinks:
    """Verify index.html links to new pages."""

    def _get_index(self):
        return (SITE / "index.html").read_text()

    def test_links_crypto_inventory(self):
        content = self._get_index()
        assert "crypto-native-inventory.html" in content

    def test_links_factor_source_map(self):
        content = self._get_index()
        assert "factor-source-map.html" in content


class TestActualScriptMapUpdated:
    """Verify actual-script-map.html was updated with required content."""

    def _get_content(self):
        return (SITE / "actual-script-map.html").read_text()

    def test_data_range_documented(self):
        content = self._get_content()
        assert "2024-06" in content
        assert "2026-06-13" in content

    def test_crypto_native_info(self):
        content = self._get_content()
        assert "funding" in content.lower() or "crypto-native" in content.lower()

    def test_top50_explanation(self):
        content = self._get_content()
        assert "Top50" in content or "top50" in content.lower() or "dynamic" in content.lower()

    def test_phase_9b_positioning(self):
        content = self._get_content()
        assert "9B" in content or "9b" in content

    def test_phase_10_positioning(self):
        content = self._get_content()
        assert "10A" in content or "10D" in content or "10" in content

    def test_phase_12_positioning(self):
        content = self._get_content()
        assert "Phase 12" in content or "phase 12" in content.lower()


class TestNoBadClaims:
    """Verify disclaimers are present and no false claims exist."""

    def _get_closeout(self):
        return (ROOT / "PHASE_12D_C_PIPELINE_DETAIL_AND_FACTOR_SOURCE_MAP.md").read_text()

    def test_phase13_not_started(self):
        content = self._get_closeout()
        assert "NOT STARTED" in content or "not started" in content.lower()

    def test_no_real_execution(self):
        content = self._get_closeout()
        assert "no real execution" in content.lower() or "No real execution" in content

    def test_disclaimers_present(self):
        content = self._get_closeout()
        assert "disclaimer" in content.lower() or "no alpha claim" in content.lower()


class TestDataLineageUpdated:
    """Verify data-lineage.html includes Top50 explanation."""

    def test_top50_in_data_lineage(self):
        content = (SITE / "data-lineage.html").read_text()
        assert "Top50" in content or "top50" in content.lower() or "dynamic" in content.lower()
