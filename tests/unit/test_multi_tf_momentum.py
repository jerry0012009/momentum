import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.signals.multi_tf_momentum import (  # noqa: E402
    MultiTfMomentumConfig,
    compute_multi_tf_momentum_signals,
)


def _make_df(close_values: list[float], symbol: str = "TEST") -> pd.DataFrame:
    return pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01 00:05:00", periods=len(close_values), freq="5min", tz="UTC").astype(str),
            "symbol": [symbol] * len(close_values),
            "close": close_values,
        }
    )


def test_long_signal_triggers_on_uptrend():
    df = _make_df([float(i) for i in range(1, 25)])

    out = compute_multi_tf_momentum_signals(
        df,
        config=MultiTfMomentumConfig(window_5m=2, window_15m=2, threshold_5m=0.0, threshold_15m=0.0),
    )

    assert out.iloc[-1]["mom_5m"] > 0
    assert out.iloc[-1]["mom_15m"] > 0
    assert int(out.iloc[-1]["long_signal"]) == 1
    assert int(out.iloc[-1]["short_signal"]) == 0


def test_short_signal_triggers_on_downtrend():
    df = _make_df([float(i) for i in range(24, 0, -1)])

    out = compute_multi_tf_momentum_signals(
        df,
        config=MultiTfMomentumConfig(window_5m=2, window_15m=2, threshold_5m=0.0, threshold_15m=0.0),
    )

    assert out.iloc[-1]["mom_5m"] < 0
    assert out.iloc[-1]["mom_15m"] < 0
    assert int(out.iloc[-1]["long_signal"]) == 0
    assert int(out.iloc[-1]["short_signal"]) == 1


def test_threshold_filters_weak_signals():
    close_values = [100.0 + 0.05 * i for i in range(24)]
    df = _make_df(close_values)

    out = compute_multi_tf_momentum_signals(
        df,
        config=MultiTfMomentumConfig(window_5m=2, window_15m=2, threshold_5m=0.01, threshold_15m=0.02),
    )

    assert int(out.iloc[-1]["long_signal"]) == 0
    assert int(out.iloc[-1]["short_signal"]) == 0


def test_groupby_symbol_isolated():
    up_df = _make_df([float(i) for i in range(1, 25)], symbol="UP")
    down_df = _make_df([float(i) for i in range(24, 0, -1)], symbol="DOWN")
    df = pd.concat([up_df, down_df], ignore_index=True)

    out = compute_multi_tf_momentum_signals(
        df,
        config=MultiTfMomentumConfig(window_5m=2, window_15m=2, threshold_5m=0.0, threshold_15m=0.0),
    )

    last_up = out[out["symbol"] == "UP"].iloc[-1]
    last_down = out[out["symbol"] == "DOWN"].iloc[-1]

    assert int(last_up["long_signal"]) == 1
    assert int(last_up["short_signal"]) == 0
    assert int(last_down["long_signal"]) == 0
    assert int(last_down["short_signal"]) == 1
