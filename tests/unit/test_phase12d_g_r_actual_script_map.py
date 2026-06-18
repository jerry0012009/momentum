"""Phase 12D-G-R2: actual-script-map.html verification-level tests."""

import json
import pytest
from pathlib import Path

SITE = Path("/root/clawd/jerry/momentum/reports/site/factor-library")
ROOT = Path("/root/clawd/jerry/momentum")


class TestNoVagueLanguage:
    def test_no_needs_confirmation(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "需人工确认" not in content

    def test_no_or_similar(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "或类似" not in content

    def test_no_uncertain(self):
        content = (SITE / "actual-script-map.html").read_text()
        # "不确定" should not appear unless followed by UNKNOWN_WITH_REASON
        lines = content.split("\n")
        for line in lines:
            if "不确定" in line:
                assert "UNKNOWN_WITH_REASON" in line


class TestVerifiedScripts:
    def test_download_script(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "download_full_binance_1h_universe.py" in content

    def test_universe_script(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "build_crypto_top50_universe.py" in content

    def test_label_script(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "build_labels.py" in content

    def test_phase11_script(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "run_phase11a_cost_slippage_capacity.py" in content

    def test_phase12a_script(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "run_phase12a_paper_signal_harness.py" in content

    def test_phase12b_script(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "run_phase12b_paper_monitoring.py" in content


class TestDataCounts:
    def test_bars_counts(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "3,316,259" in content
        assert "17,808" in content
        assert "266" in content

    def test_taker_columns_verified(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "否" in content  # taker columns = no

    def test_label_counts(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "215,061" in content
        assert "215,011" in content  # ret_fwd_1h non-null

    def test_signal_panel_counts(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "3,314,397" in content
        assert "17,801" in content


class TestSurvivorshipBias:
    def test_not_pass(self):
        content = (SITE / "actual-script-map.html").read_text()
        lines = content.split("\n")
        for line in lines:
            if "survivorship" in line.lower() or "Survivorship" in line:
                assert "PASS" not in line or "PARTIAL" in line


class TestEvaluationProtocol:
    def test_all_phases_with_scripts(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "run_phase10a_signal_backtest.py" in content
        assert "run_phase10a_r_diagnostics.py" in content
        assert "run_phase10b_tail_diagnostics.py" in content
        assert "run_phase10d_tail_aware_variants.py" in content


class TestResearchRunLedger:
    def test_ledger_explained(self):
        content = (SITE / "actual-script-map.html").read_text()
        assert "研究运行账本" in content
        assert "signal panel parquet" in content
        assert "RankIC CSV" in content


class TestNoBadClaims:
    def test_no_real_execution(self):
        content = (ROOT / "docs" / "factor_library_transparency" / "actual_script_map.md").read_text()
        assert "No real execution" in content

    def test_phase13_not_started(self):
        content = (ROOT / "docs" / "factor_library_transparency" / "actual_script_map.md").read_text()
        assert "NOT STARTED" in content
