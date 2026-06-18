"""Phase 12D-D: Factor Formula Cards validation tests. Updated for product terminology."""

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


class TestHTMLPagesExist:
    def test_factor_formula_cards_html(self):
        assert (SITE / "factor-formula-cards.html").exists()

    def test_crypto_native_factor_formulas_html(self):
        assert (SITE / "crypto-native-factor-formulas.html").exists()


class TestJSONFilesExist:
    def test_factor_formula_cards_json(self):
        assert (SITE / "assets" / "factor_formula_cards.json").exists()

    def test_crypto_native_factor_formulas_json(self):
        assert (SITE / "assets" / "crypto_native_factor_formulas.json").exists()


class TestFactorFormulaCardsJSON:
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

    def test_core_factors_marked_core(self):
        for f in self.data["phase9b_core"]:
            assert f.get("included_in_current_core_paper_signal") is True

    def test_overlay_factors_not_core(self):
        for f in self.data["phase9b_overlay"]:
            assert f.get("included_in_current_core_paper_signal") is False

    def test_historical_factors_not_in_signal_library(self):
        for f in self.data["historical_experimental"]:
            assert f.get("included_in_current_signal_library") is False

    def test_formulas_present(self):
        for cat in ["phase9b_core", "phase9b_overlay", "historical_experimental"]:
            for f in self.data.get(cat, []):
                assert "formula" in f, f"{f['factor_name']} missing formula"
                assert len(f["formula"]) > 3


class TestCryptoNativeJSON:
    @pytest.fixture(autouse=True)
    def load(self):
        self.data = json.loads((SITE / "assets" / "crypto_native_factor_formulas.json").read_text())

    def test_all_6_crypto_native_factors(self):
        names = [f["factor_name"] for f in self.data["factors"]]
        for f in CRYPTO_NATIVE:
            assert f in names

    def test_all_marked_not_in_signal_library(self):
        for f in self.data["factors"]:
            assert f.get("included_in_current_signal_library") is False
            assert f.get("included_in_current_core_paper_signal") is False

    def test_formulas_present(self):
        for f in self.data["factors"]:
            assert "formula" in f


class TestHTMLContent:
    def test_formula_cards_has_core_factors(self):
        content = (SITE / "factor-formula-cards.html").read_text()
        assert "vol_5h" in content
        assert "rsi_7h" in content
        assert "CORE_SIGNAL_FACTOR" in content

    def test_formula_cards_has_historical(self):
        content = (SITE / "factor-formula-cards.html").read_text()
        assert "mom_20h" in content
        assert "NOT_IN_CURRENT_SIGNAL" in content

    def test_crypto_native_marked_not_in_signal(self):
        content = (SITE / "crypto-native-factor-formulas.html").read_text()
        assert "NOT_IN_CURRENT_SIGNAL" in content or "未纳入当前信号" in content
        assert "funding_rate_change_24h" in content

    def test_formula_cards_has_info_box(self):
        content = (SITE / "factor-formula-cards.html").read_text()
        assert "factor_formula_registry.py" in content

    def test_index_links_new_pages(self):
        content = (SITE / "index.html").read_text()
        assert "factor-formula-cards.html" in content
        assert "crypto-native-factor-formulas.html" in content


class TestNoBadClaims:
    def test_phase13_not_started(self):
        content = (ROOT / "PHASE_12D_D_FACTOR_FORMULA_CARDS.md").read_text()
        assert "NOT STARTED" in content

    def test_no_real_execution(self):
        content = (ROOT / "PHASE_12D_D_FACTOR_FORMULA_CARDS.md").read_text()
        assert "No real execution" in content
