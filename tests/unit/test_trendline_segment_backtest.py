import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.analytics.trendline_segment_backtest import (  # noqa: E402
    TrendlineSegmentEventConfig,
    build_strategy_signal_table,
    evaluate_trendline_segment_strategy,
    extract_trendline_segment_strategy_events,
)
from momentum.analytics.multi_tf_momentum_backtest import MultiTfMomentumBacktestConfig  # noqa: E402


def _breakout_bars() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01 00:00:00", periods=7, freq="5min", tz="UTC").astype(str),
            "symbol": ["TEST"] * 7,
            "open": [99.8, 99.9, 100.1, 100.4, 100.7, 101.0, 101.3],
            "close": [99.9, 100.0, 100.2, 100.5, 100.8, 101.1, 101.2],
        }
    )


def _breakout_segments() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "symbol": "TEST",
                "timeframe": "tbn_short",
                "segment_id": 1,
                "start_bar": 1,
                "end_bar": 2,
                "bars_visible": 2,
                "end_reason": "breakout",
                "side": -1,
                "side_label": "resistance",
                "is_provisional": 0,
                "anchor_origin": 0,
                "anchor_price": 100.0,
                "pivot_origin": 1,
                "pivot_price": 100.0,
                "slope": 0.0,
                "start_value": 100.0,
                "end_value": 100.0,
                "start_timestamp": "2026-01-01T00:05:00Z",
                "end_timestamp": "2026-01-01T00:10:00Z",
                "anchor_timestamp": "2026-01-01T00:00:00Z",
                "pivot_timestamp": "2026-01-01T00:05:00Z",
            }
        ]
    )


def _rebound_bars() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01 00:00:00", periods=7, freq="5min", tz="UTC").astype(str),
            "symbol": ["TEST"] * 7,
            "open": [100.3, 100.2, 99.8, 100.1, 100.3, 100.5, 100.7],
            "close": [100.2, 100.1, 99.8, 100.2, 100.4, 100.6, 100.8],
        }
    )


def _rebound_segments() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "symbol": "TEST",
                "timeframe": "tbn_short",
                "segment_id": 2,
                "start_bar": 1,
                "end_bar": 2,
                "bars_visible": 2,
                "end_reason": "breakout",
                "side": 1,
                "side_label": "support",
                "is_provisional": 0,
                "anchor_origin": 0,
                "anchor_price": 100.0,
                "pivot_origin": 1,
                "pivot_price": 100.0,
                "slope": 0.0,
                "start_value": 100.0,
                "end_value": 100.0,
                "start_timestamp": "2026-01-01T00:05:00Z",
                "end_timestamp": "2026-01-01T00:10:00Z",
                "anchor_timestamp": "2026-01-01T00:00:00Z",
                "pivot_timestamp": "2026-01-01T00:05:00Z",
            }
        ]
    )


def test_extract_breakout_event_after_three_close_confirmation():
    events = extract_trendline_segment_strategy_events(
        _breakout_bars(),
        _breakout_segments(),
        config=TrendlineSegmentEventConfig(timeframes=("short",), max_resolution_bars=6),
    )
    sub = events[events["strategy"] == "breakout"]
    assert len(sub) == 1
    row = sub.iloc[0]
    assert row["event_type"] == "breakout_long"
    assert int(row["signal_bar"]) == 4
    assert row["entry_ts"] == "2026-01-01T00:25:00Z"


def test_extract_rebound_event_after_failed_breakout_returns_inside_range():
    events = extract_trendline_segment_strategy_events(
        _rebound_bars(),
        _rebound_segments(),
        config=TrendlineSegmentEventConfig(timeframes=("short",), max_resolution_bars=6),
    )
    sub = events[events["strategy"] == "rebound"]
    assert len(sub) == 1
    row = sub.iloc[0]
    assert row["event_type"] == "rebound_long"
    assert int(row["signal_bar"]) == 4
    assert row["entry_ts"] == "2026-01-01T00:25:00Z"


def test_signal_table_and_backtest_produce_trade_rows():
    bars = _breakout_bars()
    seg = _breakout_segments()
    result = evaluate_trendline_segment_strategy(
        bars,
        seg,
        event_config=TrendlineSegmentEventConfig(timeframes=("short",), max_resolution_bars=6),
        backtest_config=MultiTfMomentumBacktestConfig(fee_bps_per_side=0.0, slippage_bps_per_side=0.0),
    )
    assert len(result.events) == 1
    sig = build_strategy_signal_table(bars, result.events, strategy="breakout", timeframe="short")
    assert int(sig["long_signal"].sum()) == 1
    assert len(result.trades) == 1
    assert result.trades.iloc[0]["side"] == "long"
