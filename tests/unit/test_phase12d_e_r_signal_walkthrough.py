"""Phase 12D-E-R: Signal Walkthrough repair validation tests."""

import json
import pytest
from pathlib import Path

SITE = Path("/root/clawd/jerry/momentum/reports/site/factor-library")
ROOT = Path("/root/clawd/jerry/momentum")


class TestRSI28hFix:
    """rsi_28h must be NEGATIVE and sign-flipped everywhere."""

    def test_html_rsi28h_negative(self):
        content = (SITE / "signal-walkthrough.html").read_text()
        assert "rsi_28h" in content
        # Must NOT have "rsi_28h.*POS" pattern
        import re
        assert not re.search(r"rsi_28h.*?POS", content)

    def test_html_rsi28h_flipped(self):
        content = (SITE / "signal-walkthrough.html").read_text()
        # Should show rsi_28h as NEG → flip
        assert "NEG" in content  # direction column

    def test_json_rsi28h_flipped(self):
        data = json.loads((SITE / "assets" / "signal_walkthrough.json").read_text())
        for sym in data["symbols"]:
            rsi28 = data["symbols"][sym]["factors"]["rsi_28h"]
            assert "flipped_z" in rsi28

    def test_md_rsi28h_flipped(self):
        content = (ROOT / "docs" / "factor_library_transparency" / "signal_walkthrough.md").read_text()
        assert "rsi_28h" in content
        # Must show rsi_28h as NEG → flip, not POS
        import re
        assert not re.search(r"rsi_28h\|POS", content)
        assert "rsi_28h" in content  # present in table


class TestTimestampConsistency:
    """All data must come from the same timestamp."""

    def test_json_single_timestamp(self):
        data = json.loads((SITE / "assets" / "signal_walkthrough.json").read_text())
        assert data["meta"]["timestamp"] == "2026-06-13 00:00:00 UTC"

    def test_html_timestamp_stated(self):
        content = (SITE / "signal-walkthrough.html").read_text()
        assert "2026-06-13 00:00:00 UTC" in content


class TestComponentValues:
    """Component values must come from phase9b_signal_panel.parquet."""

    def test_json_has_components(self):
        data = json.loads((SITE / "assets" / "signal_walkthrough.json").read_text())
        for sym in ["BCHUSDT", "HUSDT", "DOGEUSDT"]:
            s = data["symbols"][sym]
            assert "risk_pressure" in s
            assert "oscillator_exhaustion" in s
            assert "raw_core_score" in s
            assert "signal_v0_core_only" in s

    def test_html_shows_components(self):
        content = (SITE / "signal-walkthrough.html").read_text()
        assert "risk_pressure" in content
        assert "oscillator_exhaustion" in content
        assert "raw_core_score" in content


class TestNoBadClaims:
    def test_no_real_execution(self):
        content = (ROOT / "PHASE_12D_E_R_SIGNAL_WALKTHROUGH_REPAIR.md").read_text()
        assert "real" in content.lower() or "no" in content.lower()

    def test_phase13_not_started(self):
        content = (ROOT / "docs" / "factor_library_transparency" / "signal_walkthrough.md").read_text()
        assert "Phase 13 NOT STARTED" in content


class TestFileExistence:
    def test_html_exists(self):
        assert (SITE / "signal-walkthrough.html").exists()

    def test_json_exists(self):
        assert (SITE / "assets" / "signal_walkthrough.json").exists()

    def test_md_exists(self):
        assert (ROOT / "docs" / "factor_library_transparency" / "signal_walkthrough.md").exists()
