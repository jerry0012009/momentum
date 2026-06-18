"""Phase 12D-C-R: Factor lineage repair validation tests. Updated for product terminology."""

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

OVERLAY_FACTORS = ["xs_rank_vol", "range_1h", "range_4h", "price_pos_24h"]

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


class TestFactorSourceMapJSON:
    @pytest.fixture(autouse=True)
    def load(self):
        self.data = json.loads((SITE / "assets" / "factor_source_map.json").read_text())

    def test_contains_all_10_phase9b_factors(self):
        all_factors = (
            self.data["factors"]["phase9b_core"]
            + self.data["factors"]["phase9b_overlay"]
        )
        factor_names = [f["factor_name"] for f in all_factors]
        for f in PHASE9B_FACTORS:
            assert f in factor_names, f"Missing Phase 9B factor: {f}"

    def test_mom_20h_not_in_current_signal_library(self):
        for f in self.data["factors"]["historical_experimental"]:
            if f["factor_name"] == "mom_20h":
                assert f.get("included_in_current_signal_library") is False
                assert f.get("included_in_current_core_paper_signal") is False

    def test_wq101_not_in_core_signal(self):
        for f in self.data["factors"]["historical_experimental"]:
            if f["factor_name"] == "wq101_alpha101":
                assert f.get("included_in_current_core_paper_signal") is False

    def test_core_factors_marked_core(self):
        core = self.data["factors"]["phase9b_core"]
        for f in core:
            assert f.get("included_in_current_core_paper_signal") is True

    def test_overlay_factors_not_core(self):
        overlay_names = [f["factor_name"] for f in self.data["factors"]["phase9b_overlay"]]
        for f in OVERLAY_FACTORS:
            assert f in overlay_names
        for f in self.data["factors"]["phase9b_overlay"]:
            assert f.get("included_in_current_core_paper_signal") is False

    def test_crypto_native_not_in_signal_library(self):
        for f in self.data["factors"]["crypto_native_not_in_phase9b"]:
            assert f["included_in_current_signal_library"] is False
            assert f["included_in_current_core_paper_signal"] is False

    def test_data_ranges_have_source(self):
        assert "data_ranges" in self.data
        assert len(self.data["data_ranges"]) > 0

    def test_core_signal_panel_formula(self):
        sp = self.data["signal_panel"]
        assert any("0.60" in str(v) or "core" in str(v).lower() for v in sp.values())


class TestHTMLContent:
    @pytest.fixture(autouse=True)
    def load(self):
        self.content = (SITE / "factor-source-map.html").read_text()

    def test_product_terminology(self):
        assert "当前信号库" in self.content
        assert "当前核心纸面信号" in self.content

    def test_no_phase9b_as_main_title(self):
        assert "<h1>" in self.content
        import re
        h1_match = re.search(r"<h1>(.*?)</h1>", self.content, re.DOTALL)
        if h1_match:
            assert "Phase 9B" not in h1_match.group(1)

    def test_vol_5h_in_html(self):
        assert "vol_5h" in self.content

    def test_rsi_7h_in_html(self):
        assert "rsi_7h" in self.content

    def test_mom_20h_in_html(self):
        assert "mom_20h" in self.content

    def test_core_formula_in_html(self):
        assert "risk_pressure" in self.content
        assert "oscillator_exhaustion" in self.content
        assert "0.60" in self.content
        assert "0.40" in self.content

    def test_four_sections_present(self):
        assert "当前核心信号因子" in self.content
        assert "Overlay" in self.content
        assert "Crypto-Native" in self.content
        assert "历史/实验因子" in self.content

    def test_no_bad_claims(self):
        assert "production" not in self.content.lower() or "not" in self.content.lower()
        assert "实盘" not in self.content


class TestMarkdownContent:
    @pytest.fixture(autouse=True)
    def load(self):
        self.content = (DOCS / "factor_source_map.md").read_text()

    def test_core_factors_listed(self):
        for f in PHASE9B_FACTORS:
            assert f in self.content

    def test_historical_factors_excluded(self):
        for f in HISTORICAL:
            assert f in self.content


class TestNoBadClaims:
    def test_phase13_not_started(self):
        content = (ROOT / "PHASE_12D_C_R_FACTOR_LINEAGE_REPAIR.md").read_text()
        assert "NOT STARTED" in content or "NOT_STARTED" in content

    def test_no_real_execution(self):
        content = (ROOT / "PHASE_12D_C_R_FACTOR_LINEAGE_REPAIR.md").read_text()
        assert "No real execution" in content or "no real execution" in content.lower()
