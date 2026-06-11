import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.signals.market_risk_on_off_filter import (  # noqa: E402
    MarketRiskOnOffFilterConfig,
    compute_market_risk_on_off_filter_signals,
)


def _smooth_uptrend_df() -> pd.DataFrame:
    close = [100 + i * 0.25 for i in range(360)]
    return pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01 00:00:00", periods=len(close), freq="5min", tz="UTC").astype(str),
            "symbol": ["TEST"] * len(close),
            "open": close,
            "high": [c + 0.1 for c in close],
            "low": [c - 0.1 for c in close],
            "close": close,
            "volume": [100] * len(close),
        }
    )


def _flat_then_small_bounce_df() -> pd.DataFrame:
    close = [100.0] * 320
    for i in range(40):
        close.append(100.0 + 0.05 * (i + 1))
    return pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01 00:00:00", periods=len(close), freq="5min", tz="UTC").astype(str),
            "symbol": ["TEST"] * len(close),
            "open": close,
            "high": [c + 0.1 for c in close],
            "low": [c - 0.1 for c in close],
            "close": close,
            "volume": [100] * len(close),
        }
    )


def test_smooth_uptrend_passes_risk_on_gate():
    out = compute_market_risk_on_off_filter_signals(
        _smooth_uptrend_df(),
        config=MarketRiskOnOffFilterConfig(
            window_5m=2,
            window_15m=2,
            threshold_5m=0.0,
            threshold_15m=0.0,
            trend_window_1h=12,
            trend_threshold_1h=0.005,
            ema_window_1h=12,
            vol_window_1h=6,
            vol_quantile_window_1h=24,
            vol_quantile_max=0.8,
            min_pass_count=2,
        ),
    )
    last = out.iloc[-1]
    assert int(last["base_long_signal"]) == 1
    assert int(last["risk_on_pass"]) == 1
    assert int(last["long_signal"]) == 1


def test_small_recent_bounce_does_not_force_risk_on():
    out = compute_market_risk_on_off_filter_signals(
        _flat_then_small_bounce_df(),
        config=MarketRiskOnOffFilterConfig(
            window_5m=2,
            window_15m=2,
            threshold_5m=0.0,
            threshold_15m=0.0,
            trend_window_1h=12,
            trend_threshold_1h=0.03,
            ema_window_1h=12,
            vol_window_1h=6,
            vol_quantile_window_1h=24,
            vol_quantile_max=0.8,
            min_pass_count=3,
        ),
    )
    last = out.iloc[-1]
    assert int(last["base_long_signal"]) == 1
    assert int(last["risk_on_pass"]) == 0
    assert int(last["long_filtered_out"]) == 1
