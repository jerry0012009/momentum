"""Unit tests for export_alphalens_factor_data.py."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from export_alphalens_factor_data import (
    build_factor_series,
    build_prices_wide,
    build_forward_returns,
    build_alphalens_factor_data,
    build_manifest,
)

DATASET_ID = "crypto_top50_usdt_perp_1h_long_v1"
EXPORT_BASE = (
    Path(__file__).resolve().parents[2]
    / "research/factor_runs/crypto_top50_factor_library/alphalens_exports"
)


# ── Helpers ────────────────────────────────────────────────────────

def _make_sample_df(n=500, n_symbols=5):
    rng = np.random.default_rng(42)
    symbols = [f"S{i}USDT" for i in range(n_symbols)]
    ts = pd.date_range("2025-01-01", periods=n, freq="h", tz="UTC")
    rows = []
    for sym in symbols:
        close = 100 + np.cumsum(rng.normal(0, 1, n))
        high = close + rng.uniform(0.1, 2.0, n)
        low = close - rng.uniform(0.1, 2.0, n)
        for i, t in enumerate(ts):
            rows.append({
                "timestamp": t, "symbol": sym,
                "open": close[i], "high": high[i], "low": low[i], "close": close[i],
                "volume": rng.uniform(100, 10000),
            })
    return pd.DataFrame(rows)


def _make_labels(df):
    rng = np.random.default_rng(99)
    labels = df[["timestamp", "symbol"]].copy()
    labels["ret_fwd_1h"] = rng.normal(0, 0.01, len(labels))
    labels["ret_fwd_4h"] = rng.normal(0, 0.02, len(labels))
    labels["ret_fwd_24h"] = rng.normal(0, 0.05, len(labels))
    labels["ret_fwd_72h"] = rng.normal(0, 0.1, len(labels))
    return labels


def _make_factor_values(df, factor_name="test_factor"):
    fv = df[["timestamp", "symbol"]].copy()
    fv["factor_name"] = factor_name
    fv["factor_value"] = np.random.default_rng(77).normal(0, 1, len(fv))
    fv["known_at"] = fv["timestamp"]
    fv["source_timeframe"] = "1h"
    fv["computed_at"] = pd.Timestamp.now(tz="UTC")
    return fv


# ── factor_series tests ────────────────────────────────────────────

class TestFactorSeries:
    def test_row_count_positive(self):
        df = _make_sample_df(n=100, n_symbols=3)
        fv = _make_factor_values(df)
        fs = build_factor_series(fv)
        assert len(fs) > 0

    def test_columns(self):
        df = _make_sample_df(n=100, n_symbols=3)
        fv = _make_factor_values(df)
        fs = build_factor_series(fv)
        assert set(fs.columns) == {"timestamp", "symbol", "factor_value"}


# ── prices_wide tests ──────────────────────────────────────────────

class TestPricesWide:
    def test_index_is_timestamp(self):
        df = _make_sample_df(n=100, n_symbols=3)
        pw = build_prices_wide(df)
        assert pw.index.name == "timestamp"

    def test_columns_are_symbols(self):
        df = _make_sample_df(n=100, n_symbols=3)
        pw = build_prices_wide(df)
        assert all(isinstance(c, str) for c in pw.columns)

    def test_shape(self):
        df = _make_sample_df(n=100, n_symbols=5)
        pw = build_prices_wide(df)
        assert pw.shape == (100, 5)


# ── forward_returns tests ──────────────────────────────────────────

class TestForwardReturns:
    def test_has_horizon_columns(self):
        df = _make_sample_df(n=100, n_symbols=3)
        labels = _make_labels(df)
        fr = build_forward_returns(labels, ["1h", "4h", "24h", "72h"])
        for col in ["ret_fwd_1h", "ret_fwd_4h", "ret_fwd_24h", "ret_fwd_72h"]:
            assert col in fr.columns

    def test_row_count(self):
        df = _make_sample_df(n=100, n_symbols=3)
        labels = _make_labels(df)
        fr = build_forward_returns(labels, ["1h"])
        assert len(fr) == 300  # 100 * 3 symbols


# ── alphalens_factor_data tests ────────────────────────────────────

class TestAlphalensFactorData:
    def test_contains_factor_and_returns(self):
        df = _make_sample_df(n=100, n_symbols=5)
        fv = _make_factor_values(df)
        labels = _make_labels(df)
        fs = build_factor_series(fv)
        fr = build_forward_returns(labels, ["1h", "4h"])
        afd = build_alphalens_factor_data(fs, fr, ["1h", "4h"])
        assert "factor" in afd.columns
        assert "forward_return_1h" in afd.columns
        assert "forward_return_4h" in afd.columns

    def test_quantile_in_range(self):
        df = _make_sample_df(n=100, n_symbols=5)
        fv = _make_factor_values(df)
        labels = _make_labels(df)
        fs = build_factor_series(fv)
        fr = build_forward_returns(labels, ["1h"])
        afd = build_alphalens_factor_data(fs, fr, ["1h"])
        assert afd["factor_quantile"].min() >= 1
        assert afd["factor_quantile"].max() <= 5

    def test_no_future_leak_in_exporter(self):
        """Exporter must not use shift(-k) — forward returns come from labels, not recomputed."""
        df = _make_sample_df(n=100, n_symbols=3)
        fv = _make_factor_values(df)
        labels = _make_labels(df)
        fs = build_factor_series(fv)
        fr = build_forward_returns(labels, ["1h"])
        afd = build_alphalens_factor_data(fs, fr, ["1h"])
        # Factor values should be unchanged (not shifted) — sort both by (timestamp, symbol)
        original_fv = fv.sort_values(["timestamp", "symbol"])["factor_value"].values
        exported_factor = afd.sort_values(["timestamp", "symbol"])["factor"].values
        np.testing.assert_array_equal(original_fv, exported_factor)


# ── Exported file tests ────────────────────────────────────────────

class TestExportedFiles:
    """Test actual exported files if they exist."""

    @pytest.fixture(autouse=True)
    def check_exports_exist(self):
        self.export_dir = EXPORT_BASE / DATASET_ID
        if not self.export_dir.exists():
            pytest.skip("Exports not generated yet")

    def _load(self, factor_id, filename):
        path = self.export_dir / factor_id / filename
        if not path.exists():
            pytest.skip(f"{filename} not found for {factor_id}")
        if filename.endswith(".json"):
            return json.loads(path.read_text())
        return pd.read_parquet(path)

    @pytest.mark.parametrize("factor_id", ["mom_20h", "wq101_alpha53"])
    def test_factor_series_exists(self, factor_id):
        fs = self._load(factor_id, "factor_series.parquet")
        assert len(fs) > 0

    @pytest.mark.parametrize("factor_id", ["mom_20h", "wq101_alpha53"])
    def test_prices_wide_shape(self, factor_id):
        pw = self._load(factor_id, "prices_wide.parquet")
        assert pw.index.name == "timestamp"
        assert pw.shape[1] == 50  # 50 symbols

    @pytest.mark.parametrize("factor_id", ["mom_20h", "wq101_alpha53"])
    def test_forward_returns_columns(self, factor_id):
        fr = self._load(factor_id, "forward_returns_long.parquet")
        for col in ["ret_fwd_1h", "ret_fwd_4h", "ret_fwd_24h", "ret_fwd_72h"]:
            assert col in fr.columns

    @pytest.mark.parametrize("factor_id", ["mom_20h", "wq101_alpha53"])
    def test_alphalens_factor_data_columns(self, factor_id):
        afd = self._load(factor_id, "alphalens_factor_data.parquet")
        assert "factor" in afd.columns
        assert "forward_return_1h" in afd.columns
        assert "factor_quantile" in afd.columns

    @pytest.mark.parametrize("factor_id", ["mom_20h", "wq101_alpha53"])
    def test_quantile_range(self, factor_id):
        afd = self._load(factor_id, "alphalens_factor_data.parquet")
        assert afd["factor_quantile"].min() >= 1
        assert afd["factor_quantile"].max() <= 5

    @pytest.mark.parametrize("factor_id", ["mom_20h", "wq101_alpha53"])
    def test_manifest_exists(self, factor_id):
        manifest = self._load(factor_id, "export_manifest.json")
        assert manifest["factor_id"] == factor_id
        assert manifest["dataset_id"] == DATASET_ID
        assert manifest["no_status_upgrade_from_alphalens"] is True
        assert manifest["source_of_truth"] == "evaluate_factors.py (not Alphalens)"
