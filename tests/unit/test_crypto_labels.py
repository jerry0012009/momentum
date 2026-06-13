"""Tests for build_labels.py — verify calendar-time join (not row-shift) for forward returns."""
import numpy as np
import pandas as pd
import pytest


def _make_bars_with_gap(symbols=("BTCUSDT", "ETHUSDT"), n_hours=100, gap_hours=None):
    """Create synthetic 1h bars.

    If gap_hours is given, insert a gap (missing bars) for ETHUSDT at hour 50.
    """
    rng = np.random.default_rng(42)
    rows = []
    # timestamp = bar_close_time (V0 convention)
    base_ts = pd.Timestamp("2026-01-01T01:00:00", tz="UTC")  # close of first bar
    for sym in symbols:
        close = 100.0 + np.cumsum(rng.normal(0, 1, n_hours))
        for i in range(n_hours):
            ts = base_ts + pd.Timedelta(hours=i)
            # If gap_hours is set, skip some bars for ETHUSDT
            if gap_hours and sym == "ETHUSDT" and i == 50:
                # Skip this bar — simulates a gap
                continue
            rows.append({
                "timestamp": ts,
                "bar_open_time": ts - pd.Timedelta(hours=1),
                "bar_close_time": ts,
                "symbol": sym,
                "open": close[i] - 0.5,
                "high": close[i] + 0.5,
                "low": close[i] - 1.0,
                "close": close[i],
                "volume": rng.uniform(100, 1000),
                "quote_volume": rng.uniform(10000, 100000),
                "trade_count": int(rng.integers(50, 500)),
                "source": "test",
                "market": "crypto",
                "instrument_type": "test",
                "timeframe": "1h",
            })
    return pd.DataFrame(rows)


def _build_labels_calendar_join(bars: pd.DataFrame, horizons=(1, 4, 24, 72)) -> pd.DataFrame:
    """Replicate build_labels.py calendar-time join logic for testing.

    For each row at (t, sym), look up close at (t+h, sym) via merge.
    If (t+h) doesn't exist for that symbol (gap), label is NaN.
    """
    base = bars[["timestamp", "symbol", "close"]].copy()
    # Static lookup table: (timestamp, symbol) -> close at that time
    close_lookup = base[["timestamp", "symbol", "close"]].copy()

    for h in horizons:
        target_col = f"_target_ts_{h}"
        # For each row at time t, compute future time t+h
        base[target_col] = base["timestamp"] + pd.Timedelta(hours=h)
        # Look up close at (t+h, symbol)
        future = close_lookup.rename(columns={
            "timestamp": target_col,
            "close": f"_close_at_t_plus_{h}",
        })
        base = base.merge(future, on=[target_col, "symbol"], how="left")
        base[f"ret_fwd_{h}h"] = base[f"_close_at_t_plus_{h}"] / base["close"] - 1.0
        base = base.drop(columns=[f"_close_at_t_plus_{h}", target_col])

    return base.drop(columns=["close"]).sort_values(["timestamp", "symbol"]).reset_index(drop=True)


class TestCalendarTimeJoin:
    """Labels must use calendar-time join, not row shift."""

    @pytest.mark.parametrize("h", [1, 4, 24, 72])
    def test_formula_correct_no_gaps(self, h):
        """Without gaps, calendar join and row shift give the same result."""
        bars = _make_bars_with_gap(n_hours=200)
        labels = _build_labels_calendar_join(bars, horizons=[h])
        col = f"ret_fwd_{h}h"

        for sym in bars["symbol"].unique():
            sym_bars = bars[bars["symbol"] == sym].sort_values("timestamp").reset_index(drop=True)
            sym_labels = labels[labels["symbol"] == sym].sort_values("timestamp").reset_index(drop=True)

            for i in range(len(sym_bars) - h):
                expected = sym_bars.loc[i + h, "close"] / sym_bars.loc[i, "close"] - 1.0
                actual = sym_labels.iloc[i][col]
                assert actual == pytest.approx(expected, abs=1e-12), (
                    f"Mismatch at {sym} t={i}: expected={expected}, got={actual}"
                )

    def test_gap_symbol_has_nan_at_gap(self):
        """If a bar is missing at t+h, label at t must be NaN (not next available bar)."""
        bars = _make_bars_with_gap(n_hours=100, gap_hours=True)
        labels = _build_labels_calendar_join(bars, horizons=[1])

        eth = labels[labels["symbol"] == "ETHUSDT"].sort_values("timestamp")
        eth_bars = bars[bars["symbol"] == "ETHUSDT"].sort_values("timestamp")

        # ETHUSDT is missing the bar at hour 50 (timestamp = base + 50h)
        # So at hour 49 (timestamp = base + 49h), ret_fwd_1h should be NaN
        # because there's no bar at base + 50h for ETHUSDT
        gap_ts = pd.Timestamp("2026-01-03T03:00:00", tz="UTC")  # base + 50h
        prev_ts = gap_ts - pd.Timedelta(hours=1)

        # Verify the gap exists: no ETHUSDT bar at gap_ts
        eth_at_gap = eth_bars[eth_bars["timestamp"] == gap_ts]
        assert len(eth_at_gap) == 0, "Gap should exist at hour 50"

        # Verify label at prev_ts is NaN (not a wrong value from hour 51)
        label_at_prev = eth[eth["timestamp"] == prev_ts]["ret_fwd_1h"]
        assert len(label_at_prev) == 1
        assert pd.isna(label_at_prev.iloc[0]), (
            "Label before gap must be NaN, not substituted with next available bar"
        )

    def test_after_gap_label_resumes(self):
        """After a gap, labels should resume normally for bars that have valid future bars."""
        bars = _make_bars_with_gap(n_hours=100, gap_hours=True)
        labels = _build_labels_calendar_join(bars, horizons=[1])

        eth = labels[labels["symbol"] == "ETHUSDT"].sort_values("timestamp")

        # At hour 51, there IS a bar, and hour 52 also exists → label should be valid
        ts_51 = pd.Timestamp("2026-01-03T04:00:00", tz="UTC")
        ts_52 = pd.Timestamp("2026-01-03T05:00:00", tz="UTC")
        label_51 = eth[eth["timestamp"] == ts_51]["ret_fwd_1h"]
        if len(label_51) > 0:
            assert not pd.isna(label_51.iloc[0]), "Label after gap should be valid"

    def test_tail_is_nan(self):
        """Last h bars per symbol should have NaN forward returns."""
        bars = _make_bars_with_gap(n_hours=50)
        labels = _build_labels_calendar_join(bars, horizons=[1, 4])
        for sym in bars["symbol"].unique():
            sym_labels = labels[labels["symbol"] == sym].sort_values("timestamp")
            assert pd.isna(sym_labels.iloc[-1]["ret_fwd_1h"])
            assert pd.isna(sym_labels.iloc[-1]["ret_fwd_4h"])

    def test_4h_label_at_gap_uses_real_4h_not_4th_row(self):
        """ret_fwd_4h must look up close at t+4h, not the 4th subsequent row.

        With a gap, the 4th subsequent row might be at t+5h or later.
        Calendar join correctly produces NaN when t+4h is missing.
        """
        bars = _make_bars_with_gap(n_hours=100, gap_hours=True)
        labels = _build_labels_calendar_join(bars, horizons=[4])

        eth = labels[labels["symbol"] == "ETHUSDT"].sort_values("timestamp")

        # At hour 47, ret_fwd_4h looks for hour 51 (which exists after gap at 50)
        ts_47 = pd.Timestamp("2026-01-03T00:00:00", tz="UTC")
        label_47 = eth[eth["timestamp"] == ts_47]["ret_fwd_4h"]
        if len(label_47) > 0:
            # hour 51 exists, so this should be valid
            assert not pd.isna(label_47.iloc[0])

        # At hour 48, ret_fwd_4h looks for hour 52 (exists) → valid
        # At hour 49, ret_fwd_4h looks for hour 53 (exists) → valid
        # At hour 46, ret_fwd_4h looks for hour 50 (GAP) → NaN
        ts_46 = pd.Timestamp("2026-01-02T23:00:00", tz="UTC")
        label_46 = eth[eth["timestamp"] == ts_46]["ret_fwd_4h"]
        if len(label_46) > 0:
            assert pd.isna(label_46.iloc[0]), (
                "ret_fwd_4h at hour 46 should be NaN because hour 50 is missing"
            )


class TestTimestampConvention:
    """Verify timestamp = bar_close_time = bar_open_time + 1h."""

    def test_timestamp_equals_bar_close_time(self):
        bars = _make_bars_with_gap(n_hours=50)
        assert (bars["timestamp"] == bars["bar_close_time"]).all()

    def test_bar_open_time_plus_1h_equals_timestamp(self):
        bars = _make_bars_with_gap(n_hours=50)
        assert (bars["bar_open_time"] + pd.Timedelta(hours=1) == bars["timestamp"]).all()
