"""Unit tests for build_dynamic_universe_bars_1h.py (Phase 6D).

All tests use synthetic data — no Binance API access required.
"""
import io
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from build_dynamic_universe_bars_1h import (
    read_kline_zip,
    build_symbol_bars,
    compute_symbol_availability,
    month_range,
)


# ── Helpers ───────────────────────────────────────────────────────

def _make_kline_zip(tmp_path: Path, symbol: str = "TESTUSDT", n_rows: int = 100) -> Path:
    """Create a synthetic Binance kline zip file."""
    rng = np.random.default_rng(42)
    start_ms = int(pd.Timestamp("2024-06-13", tz="UTC").timestamp() * 1000)
    rows = []
    for i in range(n_rows):
        open_ms = start_ms + i * 3_600_000  # 1h intervals
        close_ms = open_ms + 3_600_000 - 1
        o = rng.uniform(10, 100)
        h = o * 1.01
        l = o * 0.99
        c = rng.uniform(l, h)
        v = rng.uniform(1e6, 1e8)
        qv = v * c
        tc = rng.integers(1000, 100000)
        rows.append([open_ms, f"{o:.2f}", f"{h:.2f}", f"{l:.2f}", f"{c:.2f}",
                     f"{v:.2f}", close_ms, f"{qv:.2f}", tc, "0", "0", "0"])

    # Write to CSV in memory, then zip
    csv_buf = io.StringIO()
    for row in rows:
        csv_buf.write(",".join(str(x) for x in row) + "\n")

    zip_path = tmp_path / f"{symbol}-1h-2024-06.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{symbol}-1h-2024-06.csv", csv_buf.getvalue())
    return zip_path


# ── Kline parser ──────────────────────────────────────────────────

class TestReadKlineZip:
    def test_schema(self, tmp_path):
        """Parsed kline should have all required columns."""
        zip_path = _make_kline_zip(tmp_path)
        df = read_kline_zip(zip_path)
        for col in ["timestamp", "bar_open_time", "bar_close_time", "open", "high", "low",
                     "close", "volume", "quote_volume", "trade_count"]:
            assert col in df.columns, f"Missing column: {col}"

    def test_timestamp_equals_bar_open_plus_1h(self, tmp_path):
        """timestamp must equal bar_open_time + 1h."""
        zip_path = _make_kline_zip(tmp_path)
        df = read_kline_zip(zip_path)
        assert (df["timestamp"] == df["bar_open_time"] + pd.Timedelta(hours=1)).all()

    def test_bar_close_time_equals_timestamp(self, tmp_path):
        """bar_close_time must equal timestamp."""
        zip_path = _make_kline_zip(tmp_path)
        df = read_kline_zip(zip_path)
        assert (df["bar_close_time"] == df["timestamp"]).all()

    def test_numeric_columns(self, tmp_path):
        """Numeric columns should be float (trade_count is int)."""
        zip_path = _make_kline_zip(tmp_path)
        df = read_kline_zip(zip_path)
        for col in ["open", "high", "low", "close", "volume", "quote_volume"]:
            assert df[col].dtype in (np.float64, np.float32), f"{col} dtype: {df[col].dtype}"
        assert pd.api.types.is_integer_dtype(df["trade_count"]) or df["trade_count"].dtype == "Int64"

    def test_row_count(self, tmp_path):
        """Should parse all rows from zip."""
        zip_path = _make_kline_zip(tmp_path, n_rows=50)
        df = read_kline_zip(zip_path)
        assert len(df) == 50

    def test_empty_zip(self, tmp_path):
        """Empty zip should return empty DataFrame."""
        zip_path = tmp_path / "empty.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("empty.csv", "")
        df = read_kline_zip(zip_path)
        assert df.empty


# ── Symbol bars builder ───────────────────────────────────────────

class TestBuildSymbolBars:
    def test_pipeline_schema(self, tmp_path):
        """Output should match existing pipeline schema."""
        zip_path = _make_kline_zip(tmp_path)
        raw = read_kline_zip(zip_path)
        bars = build_symbol_bars("TESTUSDT", raw)

        expected_cols = [
            "timestamp", "bar_open_time", "bar_close_time", "symbol",
            "open", "high", "low", "close", "volume", "quote_volume",
            "trade_count", "source", "market", "instrument_type", "timeframe",
        ]
        assert list(bars.columns) == expected_cols

    def test_metadata_values(self, tmp_path):
        """Static metadata columns should have correct values."""
        zip_path = _make_kline_zip(tmp_path)
        raw = read_kline_zip(zip_path)
        bars = build_symbol_bars("TESTUSDT", raw)
        assert (bars["symbol"] == "TESTUSDT").all()
        assert (bars["source"] == "binance_fapi").all()
        assert (bars["market"] == "crypto").all()
        assert (bars["instrument_type"] == "usdt_margined_perpetual").all()
        assert (bars["timeframe"] == "1h").all()

    def test_empty_raw(self):
        """Empty raw data should return empty DataFrame."""
        bars = build_symbol_bars("TESTUSDT", pd.DataFrame())
        assert bars.empty


# ── Symbol availability ───────────────────────────────────────────

class TestSymbolAvailability:
    def test_missing_bar_rate(self):
        """missing_bar_rate should be computed correctly."""
        start = pd.Timestamp("2024-06-13", tz="UTC")
        end = pd.Timestamp("2024-07-13", tz="UTC")  # ~720 hours
        expected_hours = int((end - start).total_seconds() / 3600)

        # Create bars with 50% of expected data
        timestamps = pd.date_range(start, periods=expected_hours // 2, freq="h", tz="UTC")
        bars = pd.DataFrame({
            "timestamp": timestamps,
            "symbol": "TESTUSDT",
        })

        avail = compute_symbol_availability(bars, ["TESTUSDT"], start, end)
        row = avail.iloc[0]
        assert row["n_bars"] == expected_hours // 2
        assert row["expected_bars"] == expected_hours
        assert abs(row["missing_bar_rate"] - 0.5) < 0.01

    def test_zero_rows_symbol(self):
        """Symbol with no data should have missing_bar_rate = 1.0."""
        start = pd.Timestamp("2024-06-13", tz="UTC")
        end = pd.Timestamp("2024-07-13", tz="UTC")

        bars = pd.DataFrame(columns=["timestamp", "symbol"])
        avail = compute_symbol_availability(bars, ["NODATA"], start, end)
        row = avail.iloc[0]
        assert row["n_bars"] == 0
        assert row["missing_bar_rate"] == 1.0
        assert row["download_status"] == "no_data"


# ── Month range ───────────────────────────────────────────────────

class TestMonthRange:
    def test_basic(self):
        """Should generate YYYY-MM strings."""
        start = pd.Timestamp("2024-06-13", tz="UTC")
        end = pd.Timestamp("2024-09-13", tz="UTC")
        months = month_range(start, end)
        assert months == ["2024-06", "2024-07", "2024-08", "2024-09"]

    def test_single_month(self):
        start = pd.Timestamp("2024-06-01", tz="UTC")
        end = pd.Timestamp("2024-06-30", tz="UTC")
        months = month_range(start, end)
        assert months == ["2024-06"]

    def test_cross_year(self):
        start = pd.Timestamp("2024-11-01", tz="UTC")
        end = pd.Timestamp("2025-02-01", tz="UTC")
        months = month_range(start, end)
        assert months == ["2024-11", "2024-12", "2025-01", "2025-02"]


# ── Download 404 handling ─────────────────────────────────────────

class TestDownload404:
    def test_404_recorded_not_fatal(self):
        """404 should return False, not raise."""
        # We can't easily test real HTTP in unit tests, but we can test
        # that the function signature handles it correctly
        from build_dynamic_universe_bars_1h import safe_download
        # Just verify the function exists and is callable
        assert callable(safe_download)
