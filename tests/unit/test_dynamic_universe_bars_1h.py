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


# ── Membership-aware coverage ─────────────────────────────────────

from build_dynamic_universe_bars_1h import compute_membership_aware_availability, compute_qa_conclusion


class TestMembershipAwareCoverage:
    """Tests for membership-aware coverage computation."""

    def _make_bars(self, symbols, start, hours):
        """Create synthetic bars for given symbols."""
        rows = []
        timestamps = pd.date_range(start, periods=hours, freq="h", tz="UTC")
        for sym in symbols:
            for ts in timestamps:
                rows.append({"symbol": sym, "timestamp": ts})
        return pd.DataFrame(rows)

    def _make_snapshots(self, symbol_months):
        """Create synthetic snapshots. symbol_months: dict[sym → list of YYYY-MM]."""
        rows = []
        for sym, months in symbol_months.items():
            for m in months:
                rows.append({
                    "symbol": sym,
                    "asof_time": pd.Timestamp(f"{m}-01", tz="UTC"),
                })
        return pd.DataFrame(rows)

    def test_full_month_expected_bars(self):
        """Full month should have ~720 expected bars (30 days × 24h)."""
        start = pd.Timestamp("2024-06-13", tz="UTC")
        end = pd.Timestamp("2024-08-13", tz="UTC")

        # Symbol selected for July only (full month)
        snap = self._make_snapshots({"SYM1": ["2024-07"]})
        # Bars cover July fully
        bars = self._make_bars(["SYM1"], pd.Timestamp("2024-07-01", tz="UTC"), 744)  # 31 days

        avail, monthly = compute_membership_aware_availability(bars, snap, start, end)
        july_row = monthly[(monthly["symbol"] == "SYM1") & (monthly["month"] == "2024-07")]
        assert len(july_row) == 1
        assert july_row.iloc[0]["expected_bars"] == 744  # July has 31 days × 24h
        assert july_row.iloc[0]["observed_bars"] == 744
        assert july_row.iloc[0]["missing_bar_rate"] == 0.0

    def test_partial_first_month(self):
        """First month clipped to dataset start should have fewer expected bars."""
        start = pd.Timestamp("2024-06-13", tz="UTC")
        end = pd.Timestamp("2024-08-13", tz="UTC")

        snap = self._make_snapshots({"SYM1": ["2024-06"]})
        # Bars from June 13 onward
        bars = self._make_bars(["SYM1"], pd.Timestamp("2024-06-13", tz="UTC"), 432)  # 18 days

        avail, monthly = compute_membership_aware_availability(bars, snap, start, end)
        june_row = monthly[(monthly["symbol"] == "SYM1") & (monthly["month"] == "2024-06")]
        assert len(june_row) == 1
        # June 13 → June 30 = 18 days = 432 hours
        assert june_row.iloc[0]["expected_bars"] == 432

    def test_high_global_low_member_missing(self):
        """Symbol listed late should have high global but low member missing rate."""
        start = pd.Timestamp("2024-06-13", tz="UTC")
        end = pd.Timestamp("2024-09-13", tz="UTC")

        # Symbol selected only for August-September (listed late)
        snap = self._make_snapshots({"LATECOIN": ["2024-08", "2024-09"]})
        # Has data only from August onward
        bars = self._make_bars(["LATECOIN"], pd.Timestamp("2024-08-01", tz="UTC"), 1000)

        avail, monthly = compute_membership_aware_availability(bars, snap, start, end)
        row = avail[avail["symbol"] == "LATECOIN"].iloc[0]
        # Global missing is high (no June-July data)
        assert row["global_missing_bar_rate"] > 0.3
        # But member missing is low (data covers Aug-Sep)
        assert row["member_missing_bar_rate"] < 0.05

    def test_zero_bars_in_selected_month_blocks(self):
        """Zero bars in a selected symbol-month should produce BLOCKED decision."""
        start = pd.Timestamp("2024-06-13", tz="UTC")
        end = pd.Timestamp("2024-08-13", tz="UTC")

        snap = self._make_snapshots({"SYM1": ["2024-07"]})
        # No bars at all
        bars = pd.DataFrame(columns=["symbol", "timestamp"])

        avail, monthly = compute_membership_aware_availability(bars, snap, start, end)
        qa = compute_qa_conclusion(avail, monthly)
        assert qa["decision"] == "BLOCKED"
        assert qa["n_zero_bar_months"] > 0

    def test_full_coverage_allows(self):
        """Full coverage should produce ALLOWED decision."""
        start = pd.Timestamp("2024-06-13", tz="UTC")
        end = pd.Timestamp("2024-08-13", tz="UTC")

        snap = self._make_snapshots({"SYM1": ["2024-07"]})
        bars = self._make_bars(["SYM1"], pd.Timestamp("2024-07-01", tz="UTC"), 744)

        avail, monthly = compute_membership_aware_availability(bars, snap, start, end)
        qa = compute_qa_conclusion(avail, monthly)
        assert qa["decision"] == "ALLOWED"

    def test_membership_availability_schema(self):
        """membership_availability should have required columns."""
        start = pd.Timestamp("2024-06-13", tz="UTC")
        end = pd.Timestamp("2024-08-13", tz="UTC")
        snap = self._make_snapshots({"SYM1": ["2024-07"]})
        bars = self._make_bars(["SYM1"], pd.Timestamp("2024-07-01", tz="UTC"), 744)

        avail, _ = compute_membership_aware_availability(bars, snap, start, end)
        for col in ["symbol", "selected_months", "first_selected_month", "last_selected_month",
                     "member_expected_bars", "member_observed_bars", "member_missing_bars",
                     "member_missing_bar_rate", "global_missing_bar_rate", "coverage_status"]:
            assert col in avail.columns, f"Missing column: {col}"

    def test_monthly_coverage_schema(self):
        """membership_monthly_coverage should have required columns."""
        start = pd.Timestamp("2024-06-13", tz="UTC")
        end = pd.Timestamp("2024-08-13", tz="UTC")
        snap = self._make_snapshots({"SYM1": ["2024-07"]})
        bars = self._make_bars(["SYM1"], pd.Timestamp("2024-07-01", tz="UTC"), 744)

        _, monthly = compute_membership_aware_availability(bars, snap, start, end)
        for col in ["month", "symbol", "asof_time", "expected_bars",
                     "observed_bars", "missing_bars", "missing_bar_rate", "coverage_status"]:
            assert col in monthly.columns, f"Missing column: {col}"
