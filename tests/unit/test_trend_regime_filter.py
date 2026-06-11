import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.signals.trend_regime_filter import (  # noqa: E402
    TrendRegimeFilterConfig,
    compute_trend_regime_filter_signals,
)


def _smooth_trend_df() -> pd.DataFrame:
    close = [100 + i * 0.5 for i in range(40)]
    return pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01 00:00:00", periods=len(close), freq="5min", tz="UTC").astype(str),
            "symbol": ["TEST"] * len(close),
            "open": close,
            "high": [c + 0.2 for c in close],
            "low": [c - 0.2 for c in close],
            "close": close,
            "volume": [100] * len(close),
        }
    )


def _choppy_df() -> pd.DataFrame:
    close = []
    price = 100.0
    deltas = [1.2, -1.0, 1.1, -0.9, 1.0, -0.8, 1.0, -0.7] * 5
    for d in deltas:
        price += d
        close.append(price)
    return pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01 00:00:00", periods=len(close), freq="5min", tz="UTC").astype(str),
            "symbol": ["TEST"] * len(close),
            "open": close,
            "high": [c + 0.2 for c in close],
            "low": [c - 0.2 for c in close],
            "close": close,
            "volume": [100] * len(close),
        }
    )


def test_smooth_trend_passes_regime_filter():
    out = compute_trend_regime_filter_signals(
        _smooth_trend_df(),
        config=TrendRegimeFilterConfig(
            window_5m=2,
            window_15m=2,
            threshold_5m=0.0,
            threshold_15m=0.0,
            regime_window=12,
            trend_threshold=0.01,
            regime_score_threshold=2.0,
        ),
    )
    last = out.iloc[-1]
    assert int(last["base_long_signal"]) == 1
    assert int(last["regime_filter_pass"]) == 1
    assert int(last["long_signal"]) == 1


def test_choppy_market_gets_filtered():
    out = compute_trend_regime_filter_signals(
        _choppy_df(),
        config=TrendRegimeFilterConfig(
            window_5m=2,
            window_15m=2,
            threshold_5m=0.0,
            threshold_15m=0.0,
            regime_window=12,
            trend_threshold=0.01,
            regime_score_threshold=2.0,
        ),
    )
    last = out.iloc[-1]
    assert int(last["base_long_signal"]) == 1
    assert int(last["regime_filter_pass"]) == 0
    assert int(last["long_filtered_out"]) == 1
