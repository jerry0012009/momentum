"""Phase 12D-E: Signal Walkthrough validation tests."""

import json
import pytest
from pathlib import Path

SITE = Path("/root/clawd/jerry/momentum/reports/site/factor-library")
DOCS = Path("/root/clawd/jerry/momentum/docs/factor_library_transparency")
ROOT = Path("/root/clawd/jerry/momentum")

CORE_FACTORS = ["vol_5h", "vol_40h", "downside_vol_20h", "vol_of_vol_20h", "rsi_7h", "rsi_28h"]


class TestFilesExist:
    def test_html_exists(self):
        assert (SITE / "signal-walkthrough.html").exists()

    def test_json_exists(self):
        assert (SITE / "assets" / "signal_walkthrough.json").exists()

    def test_md_exists(self):
        assert (DOCS / "signal_walkthrough.md").exists()


class TestJSONContent:
    @pytest.fixture(autouse=True)
    def load(self):
        self.data = json.loads((SITE / "assets" / "signal_walkthrough.json").read_text())

    def test_timestamp_documented(self):
        assert self.data["walkthrough_timestamp"] is not None

    def test_long_example(self):
        long = self.data["symbols"]["long_example"]
        assert long["side"] == "LONG"
        assert long["symbol"] == "BCHUSDT"
        assert long["raw_weight"] > 0

    def test_short_example(self):
        short = self.data["symbols"]["short_example"]
        assert short["side"] == "SHORT"
        assert short["symbol"] == "HUSDT"
        assert short["raw_weight"] < 0

    def test_neutral_example(self):
        neutral = self.data["symbols"]["neutral_example"]
        assert neutral["side"] == "NEUTRAL"
        assert neutral["raw_weight"] == 0.0

    def test_all_6_factors_shown(self):
        for sym_key in ["long_example", "short_example", "neutral_example"]:
            factors = self.data["symbols"][sym_key]["factors"]
            for f in CORE_FACTORS:
                assert f in factors, f"Missing {f} in {sym_key}"
                assert "raw_value" in factors[f]

    def test_components_shown(self):
        long = self.data["symbols"]["long_example"]
        assert "component_derivation" in long
        assert "risk_pressure" in long["component_derivation"]
        assert "oscillator_exhaustion" in long["component_derivation"]

    def test_signal_composition(self):
        comp = self.data["signal_composition"]
        assert "0.60" in comp["raw_core_score"]
        assert "0.40" in comp["raw_core_score"]


class TestHTMLContent:
    @pytest.fixture(autouse=True)
    def load(self):
        self.content = (SITE / "signal-walkthrough.html").read_text()

    def test_long_symbol(self):
        assert "BCHUSDT" in self.content

    def test_short_symbol(self):
        assert "HUSDT" in self.content

    def test_neutral_symbol(self):
        assert "DOGEUSDT" in self.content

    def test_all_factors(self):
        for f in CORE_FACTORS:
            assert f in self.content

    def test_components(self):
        assert "risk_pressure" in self.content
        assert "oscillator_exhaustion" in self.content

    def test_signal_value(self):
        assert "1.087" in self.content
        assert "-4.695" in self.content

    def test_formula_links(self):
        assert "factor-formula-cards.html" in self.content

    def test_no_phase9b_main_title(self):
        import re
        h1 = re.search(r"<h1>(.*?)</h1>", self.content, re.DOTALL)
        if h1:
            assert "Phase 9B" not in h1.group(1)

    def test_disclaimer(self):
        assert "不是实盘" in self.content
        assert "不是交易建议" in self.content


class TestNoBadClaims:
    def test_phase13_not_started(self):
        content = (ROOT / "PHASE_12D_E_SIGNAL_WALKTHROUGH.md").read_text()
        assert "NOT STARTED" in content

    def test_no_real_execution(self):
        content = (ROOT / "PHASE_12D_E_SIGNAL_WALKTHROUGH.md").read_text()
        assert "No real execution" in content

    def test_index_links_walkthrough(self):
        content = (SITE / "index.html").read_text()
        assert "signal-walkthrough.html" in content
