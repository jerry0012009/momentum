import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.signals.price_volume_divergence import (  # noqa: E402
    PriceVolumeDivergenceConfig,
    compute_price_volume_divergence_signals,
)


def _long_divergence_df() -> pd.DataFrame:
    close = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 123, 124.2]
    high = [c + 0.4 for c in close]
    low = [c - 0.4 for c in close]
    open_ = [c - 0.1 for c in close]
    volume = [100] * 24 + [450, 80, 105]
    return pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01 00:00:00", periods=len(close), freq="5min", tz="UTC").astype(str),
            "symbol": ["TEST"] * len(close),
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }
    )


def _short_divergence_df() -> pd.DataFrame:
    close = [124, 123, 122, 121, 120, 119, 118, 117, 116, 115, 114, 113, 112, 111, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100, 101, 99.8]
    high = [c + 0.4 for c in close]
    low = [c - 0.4 for c in close]
    open_ = [c + 0.1 for c in close]
    volume = [100] * 24 + [450, 80, 105]
    return pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01 00:00:00", periods=len(close), freq="5min", tz="UTC").astype(str),
            "symbol": ["TEST"] * len(close),
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }
    )


def test_long_divergence_warning_blocks_long_signal():
    out = compute_price_volume_divergence_signals(
        _long_divergence_df(),
        config=PriceVolumeDivergenceConfig(
            window_5m=2,
            window_15m=2,
            threshold_5m=0.0,
            threshold_15m=0.0,
            vol_window=5,
            breakout_lookback=12,
            divergence_delta_z=0.5,
            z_confirm=0.5,
            warning_active_bars=3,
        ),
    )
    last = out.iloc[-1]
    assert int(last["up_breakout_event"]) == 1
    assert int(last["bearish_divergence_event"]) == 1
    assert int(last["bearish_divergence_warning"]) == 1
    assert int(last["base_long_signal"]) == 1
    assert int(last["long_signal"]) == 0
    assert int(last["long_filtered_out"]) == 1


def test_short_divergence_warning_blocks_short_signal():
    out = compute_price_volume_divergence_signals(
        _short_divergence_df(),
        config=PriceVolumeDivergenceConfig(
            window_5m=2,
            window_15m=2,
            threshold_5m=0.0,
            threshold_15m=0.0,
            vol_window=5,
            breakout_lookback=12,
            divergence_delta_z=0.5,
            z_confirm=0.5,
            warning_active_bars=3,
        ),
    )
    last = out.iloc[-1]
    assert int(last["down_breakout_event"]) == 1
    assert int(last["bullish_divergence_event"]) == 1
    assert int(last["bullish_divergence_warning"]) == 1
    assert int(last["base_short_signal"]) == 1
    assert int(last["short_signal"]) == 0
    assert int(last["short_filtered_out"]) == 1


def test_warning_decays_after_active_bars():
    df = _long_divergence_df()
    extra = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01 02:15:00", periods=4, freq="5min", tz="UTC").astype(str),
            "symbol": ["TEST"] * 4,
            "open": [124.1, 124.2, 124.3, 124.4],
            "high": [124.5, 124.6, 124.7, 124.8],
            "low": [123.9, 124.0, 124.1, 124.2],
            "close": [124.2, 124.3, 124.4, 124.5],
            "volume": [110, 112, 114, 116],
        }
    )
    df = pd.concat([df, extra], ignore_index=True)
    out = compute_price_volume_divergence_signals(
        df,
        config=PriceVolumeDivergenceConfig(
            window_5m=2,
            window_15m=2,
            threshold_5m=0.0,
            threshold_15m=0.0,
            vol_window=5,
            breakout_lookback=12,
            divergence_delta_z=0.5,
            z_confirm=0.5,
            warning_active_bars=3,
        ),
    )
    assert int(out.iloc[-1]["bearish_divergence_warning"]) == 0
