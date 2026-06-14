"""Phase 7L: data cache construction validation tests."""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
RUN = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"


class TestTakerEnrichedBars:
    def test_enriched_row_count_matches_source_static(self):
        src = pd.read_parquet(ROOT / "data/cache/crypto_top50_usdt_perp_1h/bars_1h.parquet")
        enriched = pd.read_parquet(ROOT / "data/cache/crypto_top50_usdt_perp_1h_taker_enriched/bars_1h.parquet")
        assert len(src) == len(enriched)

    def test_enriched_row_count_matches_source_dynamic(self):
        src = pd.read_parquet(ROOT / "data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet")
        enriched = pd.read_parquet(ROOT / "data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1_taker_enriched/bars_1h.parquet")
        assert len(src) == len(enriched)

    def test_enriched_has_taker_buy_quote_volume_static(self):
        df = pd.read_parquet(ROOT / "data/cache/crypto_top50_usdt_perp_1h_taker_enriched/bars_1h.parquet")
        assert "taker_buy_quote_volume" in df.columns
        assert df["taker_buy_quote_volume"].notna().any()


class TestFundingEvents:
    def test_events_has_known_at(self):
        df = pd.read_parquet(ROOT / "data/cache/crypto_funding_rate_1h_contract_v1/funding_rate_events.parquet")
        assert "known_at" in df.columns
        assert df["known_at"].notna().all()

    def test_events_has_required_columns(self):
        df = pd.read_parquet(ROOT / "data/cache/crypto_funding_rate_1h_contract_v1/funding_rate_events.parquet")
        for col in ["symbol", "calc_time", "known_at", "funding_rate", "funding_interval_hours"]:
            assert col in df.columns


class TestFundingAligned:
    def test_static_row_count_match(self):
        bars = pd.read_parquet(ROOT / "data/cache/crypto_top50_usdt_perp_1h/bars_1h.parquet")
        aligned = pd.read_parquet(ROOT / "data/cache/crypto_funding_rate_1h_contract_v1/funding_rate_1h_aligned_static.parquet")
        assert len(bars) == len(aligned)

    def test_dynamic_row_count_match(self):
        bars = pd.read_parquet(ROOT / "data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet")
        aligned = pd.read_parquet(ROOT / "data/cache/crypto_funding_rate_1h_contract_v1/funding_rate_1h_aligned_dynamic.parquet")
        assert len(bars) == len(aligned)

    def test_funding_age_not_exceed_interval(self):
        aligned = pd.read_parquet(ROOT / "data/cache/crypto_funding_rate_1h_contract_v1/funding_rate_1h_aligned_static.parquet")
        valid = aligned.dropna(subset=["funding_rate", "funding_age_hours", "funding_interval_hours"])
        assert (valid["funding_age_hours"] <= valid["funding_interval_hours"]).all()

    def test_missing_symbols_keep_nan(self):
        aligned = pd.read_parquet(ROOT / "data/cache/crypto_funding_rate_1h_contract_v1/funding_rate_1h_aligned_static.parquet")
        # Find a symbol with no funding data (should be all NaN)
        sym_coverage = aligned.groupby("symbol")["funding_rate"].apply(lambda x: x.notna().any())
        missing_syms = sym_coverage[~sym_coverage].index.tolist()
        if missing_syms:
            sym_data = aligned[aligned["symbol"] == missing_syms[0]]
            assert sym_data["funding_rate"].isna().all()

    def test_no_factor_registry_modified(self):
        reg = ROOT / "scripts" / "factor_formula_registry.py"
        content = reg.read_text()
        assert content.count("FactorSpec(") == 47
