"""Phase 12D-D: Factor Formula Cards validation tests."""

import json
import pytest
from pathlib import Path

SITE = Path("/root/clawd/jerry/momentum/reports/site/factor-library")
DOCS = Path("/root/clawd/jerry/momentum/docs/factor_library_transparency")
ROOT = Path("/root/clawd/jerry/momentum")

PHASE9B_FACTORS = [
    "vol_5h", "vol_40h", "downside_vol_20h", "vol_of_vol_20h",
    "rsi_7h", "rsi_28h", "xs_rank_vol",
    "range_1h", "range_4h", "price_pos_24h",
]

SURVIVING_CORE = ["vol_5h", "vol_40h", "downside_vol_20h", "vol_of_vol_20h", "rsi_7h", "rsi_28h"]

CRYPTO_NATIVE = [
    "funding_rate_change_24h", "funding_rate_level_20h",
    "funding_rate_zscore_80h", "taker_buy_delta_5h",
    "taker_buy_ratio_20h", "taker_buy_zscore_20h",
]

HISTORICAL = [
    "mom_20h", "reversal_5h", "volatility_20h", "rsi_14h",
    "bb_zscore_20h", "wq101_alpha101", "wq101_alpha12",
    "wq101_alpha53", "q158_high_low_range", "tech_macd", "tech_atr",
]


class TestHTMLPagesExist:
    """Verify HTML pages exist."""

    def test_factor_formula_cards_html(self):
        assert (SITE / "factor-formula-cards.html").exists()

    def test_crypto_native_factor_formulas_html(self):
        assert (SITE / "crypto-native-factor-formulas.html").exists()


class TestJSONFilesExist:
    """Verify JSON data files exist."""

    def test_factor_formula_cards_json(self):
        assert (SITE / "assets" / "factor_formula_cards.json").exists()

    def test_crypto_native_factor_formulas_json(self):
        assert (SITE / "assets" / "crypto_native_factor_formulas.json").exists()


class TestFactorFormulaCardsJSON:
    """Verify factor_formula_cards.json content."""

    @pytest.fixture(autouse=True)
    def load(self):
        self.data = json.loads((SITE / "assets" / "factor_formula_cards.json").read_text())

    def _all_factor_names(self):
        names = []
        for cat in ["phase9b_core", "phase9b_overlay", "historical_experimental"]:
            for f in self.data.get(cat, []):
                names.append(f["factor_name"])
        return names

    def test_all_10_phase9b_factors_present(self):
        all_names = self._all_factor_names()
        for f in PHASE9B_FACTORS:
            assert f in all_names, f"Missing: {f}"

    def test_all_6_surviving_factors_present(self):
        core = [f["factor_name"] for f in self.data["phase9b_core"]]
        for f in SURVIVING_CORE:
            assert f in core, f"Missing surviving: {f}"

    def test_core_factors_marked_surviving(self):
        for f in self.data["phase9b_core"]:
            assert f.get("in_surviving_candidate") is True, f"{f['factor_name']} not marked surviving"

    def test_overlay_factors_not_surviving(self):
        for f in self.data["phase9b_overlay"]:
            assert f.get("in_surviving_candidate") is False, f"{f['factor_name']} should not be surviving"

    def test_historical_factors_not_phase9b(self):
        for f in self.data["historical_experimental"]:
            assert f.get("in_phase9b") is False, f"{f['factor_name']} should not be in Phase 9B"

    def test_formulas_present(self):
        for cat in ["phase9b_core", "phase9b_overlay", "historical_experimental"]:
            for f in self.data.get(cat, []):
                assert "formula" in f, f"{f['factor_name']} missing formula"
                assert len(f["formula"]) > 3, f"{f['factor_name']} formula too short"


class TestCryptoNativeJSON:
    """Verify crypto_native_factor_formulas.json content."""

    @pytest.fixture(autouse=True)
    def load(self):
        self.data = json.loads((SITE / "assets" / "crypto_native_factor_formulas.json").read_text())

    def test_all_6_crypto_native_factors(self):
        names = [f["factor_name"] for f in self.data["factors"]]
        for f in CRYPTO_NATIVE:
            assert f in names, f"Missing: {f}"

    def test_all_marked_not_phase9b(self):
        for f in self.data["factors"]:
            assert f.get("in_phase9b") is False, f"{f['factor_name']} should not be in Phase 9B"
            assert f.get("in_surviving_candidate") is False

    def test_formulas_present(self):
        for f in self.data["factors"]:
            assert "formula" in f, f"{f['factor_name']} missing formula"


class TestHTMLContent:
    """Verify HTML pages contain key content."""

    def test_formula_cards_has_phase9b_info(self):
        content = (SITE / "factor-formula-cards.html").read_text()
        assert "vol_5h" in content
        assert "rsi_7h" in content
        assert "SURVIVING_CANDIDATE" in content

    def test_formula_cards_has_historical(self):
        content = (SITE / "factor-formula-cards.html").read_text()
        assert "mom_20h" in content
        assert "NOT_PHASE9B" in content

    def test_crypto_native_has_not_phase9b(self):
        content = (SITE / "crypto-native-factor-formulas.html").read_text()
        assert "NOT_PHASE9B" in content
        assert "funding_rate_change_24h" in content
        assert "taker_buy_delta_5h" in content

    def test_formula_cards_has_info_box(self):
        content = (SITE / "factor-formula-cards.html").read_text()
        assert "factor_formula_registry.py" in content

    def test_index_links_new_pages(self):
        content = (SITE / "index.html").read_text()
        assert "factor-formula-cards.html" in content
        assert "crypto-native-factor-formulas.html" in content


class TestNoBadClaims:
    """Verify disclaimers present."""

    def test_phase13_not_started(self):
        content = (ROOT / "PHASE_12D_D_FACTOR_FORMULA_CARDS.md").read_text()
        assert "NOT STARTED" in content

    def test_no_real_execution(self):
        content = (ROOT / "PHASE_12D_D_FACTOR_FORMULA_CARDS.md").read_text()
        assert "No real execution" in content
