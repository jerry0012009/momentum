"""Phase 12D-C-R: Factor lineage repair validation tests."""

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

HISTORICAL_FACTORS = [
    "mom_20h", "reversal_5h", "volatility_20h", "rsi_14h",
    "bb_zscore_20h", "wq101_alpha101", "wq101_alpha12",
    "wq101_alpha53", "q158_high_low_range", "tech_macd", "tech_atr",
]

CRYPTO_NATIVE_FACTORS = [
    "funding_rate_change_24h", "funding_rate_level_20h",
    "funding_rate_zscore_80h", "taker_buy_delta_5h",
    "taker_buy_ratio_20h", "taker_buy_zscore_20h",
]


class TestFactorSourceMapJSON:
    """Verify factor_source_map.json has correct factor data."""

    @pytest.fixture(autouse=True)
    def load_json(self):
        path = SITE / "assets" / "factor_source_map.json"
        assert path.exists(), f"Missing: {path}"
        self.data = json.loads(path.read_text())

    def _all_factor_names(self):
        names = []
        for category in ["phase9b_core", "phase9b_overlay", "historical_experimental", "crypto_native_not_in_phase9b"]:
            for f in self.data.get("factors", {}).get(category, []):
                names.append(f["factor_name"])
        return names

    def test_contains_all_10_phase9b_factors(self):
        all_names = self._all_factor_names()
        for f in PHASE9B_FACTORS:
            assert f in all_names, f"Missing Phase 9B factor: {f}"

    def test_mom_20h_not_in_phase9b(self):
        for f in self.data["factors"]["historical_experimental"]:
            if f["factor_name"] == "mom_20h":
                assert f["included_in_phase9b_signal_panel"] is False
                return
        pytest.fail("mom_20h not found in historical_experimental")

    def test_wq101_not_in_surviving(self):
        for f in self.data["factors"]["historical_experimental"]:
            if f["factor_name"] == "wq101_alpha101":
                assert f["included_in_surviving_candidate"] is False
                return
        pytest.fail("wq101_alpha101 not found in historical_experimental")

    def test_surviving_factors_are_vol_rsi(self):
        core = self.data["factors"]["phase9b_core"]
        surviving = [f["factor_name"] for f in core if f.get("included_in_surviving_candidate")]
        for f in SURVIVING_CORE:
            assert f in surviving, f"Missing surviving factor: {f}"
        assert len(surviving) == 6

    def test_core_formula_060_040(self):
        variant = self.data["signal_panel"]["signal_variants"]["signal_v0_core_only"]
        formula = variant["formula"]
        assert "0.60" in formula
        assert "0.40" in formula

    def test_overlay_factors_not_surviving(self):
        overlay_names = [f["factor_name"] for f in self.data["factors"]["phase9b_overlay"]]
        for f in OVERLAY_FACTORS:
            assert f in overlay_names, f"Missing overlay factor: {f}"
        for f in self.data["factors"]["phase9b_overlay"]:
            assert f.get("included_in_surviving_candidate") is False, f"{f['factor_name']} should not be surviving"

    def test_crypto_native_not_in_phase9b(self):
        for f in self.data["factors"]["crypto_native_not_in_phase9b"]:
            assert f["included_in_phase9b_signal_panel"] is False

    def test_data_ranges_have_source(self):
        ranges = self.data.get("data_ranges", {})
        for key, val in ranges.items():
            assert "source_of_range" in val, f"data_ranges.{key} missing source_of_range"


class TestHTMLContent:
    """Verify factor-source-map.html has correct content."""

    @pytest.fixture(autouse=True)
    def load_html(self):
        self.content = (SITE / "factor-source-map.html").read_text()

    def test_repair_notice(self):
        assert "12D-C-R" in self.content
        assert "build_phase9b_signal_panel.py" in self.content

    def test_vol_5h_in_html(self):
        assert "vol_5h" in self.content

    def test_rsi_7h_in_html(self):
        assert "rsi_7h" in self.content

    def test_mom_20h_marked_historical(self):
        assert "mom_20h" in self.content
        assert "Historical" in self.content or "historical" in self.content

    def test_core_formula_in_html(self):
        assert "0.60" in self.content
        assert "0.40" in self.content
        assert "risk_pressure" in self.content

    def test_surviving_candidate_6_factors(self):
        assert "vol_5h, vol_40h, downside_vol_20h, vol_of_vol_20h, rsi_7h, rsi_28h" in self.content

    def test_no_bad_claims(self):
        assert "PAPER_SIGNAL_DIAGNOSTIC_ONLY" in self.content or "NOT STARTED" in self.content
        assert "allowed_for_real_execution" in self.content


class TestMarkdownContent:
    """Verify factor_source_map.md has correct content."""

    @pytest.fixture(autouse=True)
    def load_md(self):
        self.content = (DOCS / "factor_source_map.md").read_text()

    def test_phase_9b_factors_listed(self):
        for f in PHASE9B_FACTORS:
            assert f in self.content, f"Missing factor in md: {f}"

    def test_historical_factors_excluded(self):
        assert "mom_20h" in self.content
        assert "Historical" in self.content or "historical" in self.content or "不属于 Phase 9B" in self.content

    def test_formula_present(self):
        assert "0.60" in self.content
        assert "0.40" in self.content


class TestNoBadClaims:
    """Verify disclaimers present."""

    def test_phase13_not_started(self):
        content = (ROOT / "PHASE_12D_C_R_FACTOR_LINEAGE_REPAIR.md").read_text()
        assert "NOT STARTED" in content

    def test_no_real_execution(self):
        content = (ROOT / "PHASE_12D_C_R_FACTOR_LINEAGE_REPAIR.md").read_text()
        assert "no real execution" in content.lower() or "No real execution" in content
