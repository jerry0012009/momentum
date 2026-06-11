import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.signals.trendline_breakout_navigator import (  # noqa: E402
    TrendlineBreakoutNavigatorConfig,
    compute_trendline_breakout_navigator,
    extract_trendline_breakout_segments,
)


def _base_df(n: int = 240) -> pd.DataFrame:
    idx = np.arange(n)
    close = 100.0 + 0.05 * idx + 1.8 * np.sin(idx / 5.5)
    return pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01 00:00:00", periods=n, freq="5min", tz="UTC").astype(str),
            "symbol": ["TEST"] * n,
            "high": close + 0.30,
            "low": close - 0.30,
            "close": close,
        }
    )


def test_trendline_breakout_runs_and_outputs_columns():
    out = compute_trendline_breakout_navigator(
        _base_df(),
        config=TrendlineBreakoutNavigatorConfig(
            swing_long=20,
            swing_medium=10,
            swing_short=5,
            swing_right=1,
            min_pivot_gap=3,
        ),
    )
    required = [
        "tbn_long_trend",
        "tbn_medium_trend",
        "tbn_short_trend",
        "tbn_long_line_value",
        "tbn_medium_line_value",
        "tbn_short_line_value",
        "tbn_short_line_side",
        "tbn_short_anchor_origin",
        "tbn_short_anchor_price",
        "tbn_short_active_pivot_origin",
        "tbn_short_active_pivot_price",
        "tbn_short_line_is_provisional",
        "tbn_wick_bull",
        "tbn_wick_bear",
        "tbn_breakout_bull",
        "tbn_breakout_bear",
        "tbn_hh",
        "tbn_ll",
        "tbn_composite_trend",
        "tbn_signal",
    ]
    for col in required:
        assert col in out.columns
    assert len(out) == 240


def test_trendline_breakout_signal_is_bounded():
    out = compute_trendline_breakout_navigator(
        _base_df(),
        config=TrendlineBreakoutNavigatorConfig(
            swing_long=20,
            swing_medium=10,
            swing_short=5,
            swing_right=1,
            min_pivot_gap=3,
        ),
    )
    assert set(out["tbn_signal"].unique()).issubset({-1, 0, 1})
    assert out["tbn_composite_trend"].abs().max() <= 3


def test_active_line_starts_horizontal_after_hh_before_next_same_side_pivot():
    bars = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01 00:00:00", periods=11, freq="5min", tz="UTC").astype(str),
            "symbol": ["TEST"] * 11,
            "high": [10.0, 11.0, 13.0, 12.0, 11.0, 14.0, 13.0, 12.0, 13.0, 15.0, 14.0],
            "low": [9.0, 10.0, 11.0, 8.0, 9.0, 12.0, 11.0, 9.0, 10.0, 12.5, 11.5],
            "close": [9.5, 10.5, 12.5, 9.0, 10.0, 13.5, 12.5, 10.5, 11.5, 14.2, 12.8],
        }
    )

    out = compute_trendline_breakout_navigator(
        bars,
        config=TrendlineBreakoutNavigatorConfig(
            swing_long=20,
            swing_medium=20,
            swing_short=2,
            swing_right=1,
            min_pivot_gap=1,
            enable_long=False,
            enable_medium=False,
            enable_short=True,
        ),
    )

    hh_bar = int(out.index[out["tbn_hh"] == 1][0])
    assert hh_bar == 10
    assert out.loc[7:10, "tbn_short_line_value"].tolist() == [9.0, 9.0, 9.0, 9.0]
    assert out.loc[7:10, "tbn_short_line_slope"].tolist() == [0.0, 0.0, 0.0, 0.0]
    assert out.loc[7:10, "tbn_short_line_side"].tolist() == [1, 1, 1, 1]
    assert out.loc[7:10, "tbn_short_anchor_origin"].tolist() == [7, 7, 7, 7]
    assert out.loc[7:10, "tbn_short_active_pivot_origin"].tolist() == [-1, -1, -1, -1]
    assert out.loc[7:10, "tbn_short_line_is_provisional"].tolist() == [1, 1, 1, 1]



def test_followup_pivot_low_turns_horizontal_support_into_low_to_low_line():
    bars = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01 00:00:00", periods=14, freq="5min", tz="UTC").astype(str),
            "symbol": ["TEST"] * 14,
            "high": [10.0, 11.0, 13.0, 12.0, 11.0, 14.0, 13.0, 12.0, 13.0, 15.0, 14.0, 13.0, 14.0, 13.5],
            "low": [9.0, 10.0, 11.0, 8.0, 9.0, 12.0, 11.0, 9.0, 10.0, 12.5, 11.5, 10.5, 11.0, 11.2],
            "close": [9.5, 10.5, 12.5, 9.0, 10.0, 13.5, 12.5, 10.5, 11.5, 14.2, 12.8, 11.0, 12.2, 12.0],
        }
    )

    out = compute_trendline_breakout_navigator(
        bars,
        config=TrendlineBreakoutNavigatorConfig(
            swing_long=20,
            swing_medium=20,
            swing_short=2,
            swing_right=1,
            min_pivot_gap=1,
            enable_long=False,
            enable_medium=False,
            enable_short=True,
        ),
    )

    assert int(out.index[out["tbn_hh"] == 1][0]) == 10
    assert out.loc[7, "tbn_short_line_value"] == 9.0
    assert out.loc[8, "tbn_short_line_value"] > out.loc[7, "tbn_short_line_value"]
    assert out.loc[12, "tbn_short_line_slope"] > 0.0
    assert out.loc[8:13, "tbn_short_line_side"].tolist() == [1, 1, 1, 1, 1, 1]
    assert out.loc[8:13, "tbn_short_anchor_origin"].tolist() == [7, 7, 7, 7, 7, 7]
    assert out.loc[8:13, "tbn_short_active_pivot_origin"].tolist() == [11, 11, 11, 11, 11, 11]
    assert out.loc[8:13, "tbn_short_line_is_provisional"].tolist() == [0, 0, 0, 0, 0, 0]



def test_close_below_support_is_marked_as_true_breakout_bear():
    bars = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01 00:00:00", periods=12, freq="5min", tz="UTC").astype(str),
            "symbol": ["TEST"] * 12,
            "high": [10.0, 11.0, 13.0, 12.0, 11.0, 14.0, 13.0, 12.0, 13.0, 15.0, 14.0, 10.0],
            "low": [9.0, 10.0, 11.0, 8.0, 9.0, 12.0, 11.0, 9.0, 10.0, 12.5, 11.5, 8.4],
            "close": [9.5, 10.5, 12.5, 9.0, 10.0, 13.5, 12.5, 10.5, 11.5, 14.2, 12.8, 8.6],
        }
    )

    out = compute_trendline_breakout_navigator(
        bars,
        config=TrendlineBreakoutNavigatorConfig(
            swing_long=20,
            swing_medium=20,
            swing_short=2,
            swing_right=1,
            min_pivot_gap=1,
            enable_long=False,
            enable_medium=False,
            enable_short=True,
        ),
    )

    assert out.loc[11, "tbn_breakout_bear"] == 1
    assert out.loc[11, "tbn_short_line_side"] == 1
    assert not pd.isna(out.loc[11, "tbn_short_line_value"])



def test_close_above_resistance_is_marked_as_true_breakout_bull():
    base = 30.0
    high_src = [10.0, 11.0, 13.0, 12.0, 11.0, 14.0, 13.0, 12.0, 13.0, 15.0, 14.0, 10.0]
    low_src = [9.0, 10.0, 11.0, 8.0, 9.0, 12.0, 11.0, 9.0, 10.0, 12.5, 11.5, 8.4]
    close_src = [9.5, 10.5, 12.5, 9.0, 10.0, 13.5, 12.5, 10.5, 11.5, 14.2, 12.8, 8.6]
    bars = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01 00:00:00", periods=12, freq="5min", tz="UTC").astype(str),
            "symbol": ["TEST"] * 12,
            "high": [base - v for v in low_src],
            "low": [base - v for v in high_src],
            "close": [base - v for v in close_src],
        }
    )

    out = compute_trendline_breakout_navigator(
        bars,
        config=TrendlineBreakoutNavigatorConfig(
            swing_long=20,
            swing_medium=20,
            swing_short=2,
            swing_right=1,
            min_pivot_gap=1,
            enable_long=False,
            enable_medium=False,
            enable_short=True,
        ),
    )

    assert out.loc[11, "tbn_breakout_bull"] == 1
    assert out.loc[11, "tbn_short_line_side"] == -1
    assert not pd.isna(out.loc[11, "tbn_short_line_value"])



def test_extract_segments_returns_segment_state_with_end_reason():
    bars = _base_df()
    cfg = TrendlineBreakoutNavigatorConfig(
        swing_long=20,
        swing_medium=10,
        swing_short=5,
        swing_right=1,
        min_pivot_gap=3,
    )
    seg = extract_trendline_breakout_segments(bars, config=cfg)

    required = {
        "timeframe",
        "segment_id",
        "start_bar",
        "end_bar",
        "end_reason",
        "side",
        "side_label",
        "anchor_origin",
        "anchor_price",
        "pivot_origin",
        "pivot_price",
        "slope",
        "start_timestamp",
        "end_timestamp",
    }
    assert required.issubset(set(seg.columns))
    assert len(seg) > 0
    assert set(seg["end_reason"].unique()).issubset({"breakout", "pivot_update", "trend_switch", "window_end"})
    assert (seg["end_bar"] >= seg["start_bar"]).all()
