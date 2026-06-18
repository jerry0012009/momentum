"""Phase 12D-G-R: actual-script-map.html validation tests."""

import json
import pytest
from pathlib import Path

SITE = Path("/root/clawd/jerry/momentum/reports/site/factor-library")
ROOT = Path("/root/clawd/jerry/momentum")


class TestFileExistence:
    def test_html_exists(self):
        assert (SITE / "actual-script-map.html").exists()

    def test_json_exists(self):
        assert (SITE / "assets" / "actual_script_map.json").exists()

    def test_md_exists(self):
        assert (ROOT / "docs" / "factor_library_transparency" / "actual_script_map.md").exists()


class TestPageTitle:
    def test_title_changed(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "因子库真实执行链路与脚本地图" in content

    def test_subtitle(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "本页解释当前因子库" in content


class TestExecutionChain:
    def test_11_sections(self):
        content = (SITE / "actual-script-map.html").read_text()
        for i in range(1, 12):
            assert f">{i}." in content or f"> {i}." in content or f">{i}." in content

    def test_universe_top50(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "quote_volume" in content
        assert "Top50" in content

    def test_survivorship_partial(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "PARTIAL" in content
        # Should NOT have PASS near survivorship
        lines = content.split("\n")
        for line in lines:
            if "survivorship" in line.lower() or "Survivorship" in line:
                assert "PASS" not in line or "PARTIAL" in line

    def test_bars_filtered_vs_full(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "filtered" in content
        assert "full cache" in content

    def test_factor_values_3_builders(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "build_factor_values.py" in content
        assert "build_factor_values_batch.py" in content
        assert "build_crypto_native" in content

    def test_forward_labels_4_horizons(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "1h" in content
        assert "4h" in content
        assert "24h" in content
        assert "72h" in content
        assert "close-to-close" in content

    def test_signal_panel_not_backtest(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "不是回测" in content
        assert "不是交易" in content
        assert "不是 paper trade" in content

    def test_signal_variants(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "signal_v0_core_only" in content
        assert "signal_v0_pm_full_structured" in content
        assert "signal_v0_family_balanced_diagnostic" in content

    def test_evaluation_protocol(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "10A" in content
        assert "10D" in content
        assert "RankIC" in content

    def test_cost_liquidity_separate(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "Phase 11 不是最终交易回测" in content

    def test_paper_monitoring_not_future(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "不是当前后台定时任务" in content or "不是正经 future paper trade" in content

    def test_deployment_apache(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "Apache" in content
        assert "publish" in content.lower()

    def test_not_factor_library_mainline(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "NOT_FACTOR_LIBRARY_MAINLINE" in content


class TestNoBadClaims:
    def test_no_real_execution(self):
        content = (ROOT / "docs" / "factor_library_transparency" / "actual_script_map.md").read_text()
        assert "No real execution" in content

    def test_phase13_not_started(self):
        content = (ROOT / "docs" / "factor_library_transparency" / "actual_script_map.md").read_text()
        assert "NOT STARTED" in content
