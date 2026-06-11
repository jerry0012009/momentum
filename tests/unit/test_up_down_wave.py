import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.signals.up_down_wave import UpDownWaveConfig, compute_up_down_wave_signals


def test_upwave_triggers_on_defined_pattern():
    # Strong uptrend ensures close > MA20 near the end
    close = [float(i) for i in range(1, 31)]
    open_ = [c - 0.2 for c in close]

    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01", periods=30, freq="D", tz="UTC").astype(str),
            "symbol": ["TEST"] * 30,
            "open": open_,
            "close": close,
        }
    )

    out = compute_up_down_wave_signals(df, config=UpDownWaveConfig(ma_period=20))

    assert int(out.iloc[-1]["upwave"]) == 1
    assert int(out.iloc[-1]["downwave"]) == 0


def test_upwave_requires_t_minus_3_bullish():
    close = [float(i) for i in range(1, 31)]
    open_ = [c - 0.2 for c in close]

    # Make t-3 bearish while preserving "above MA" environment
    open_[-4] = close[-4] + 0.5

    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01", periods=30, freq="D", tz="UTC").astype(str),
            "symbol": ["TEST"] * 30,
            "open": open_,
            "close": close,
        }
    )

    out = compute_up_down_wave_signals(df, config=UpDownWaveConfig(ma_period=20))
    assert int(out.iloc[-1]["upwave"]) == 0


def test_downwave_triggers_on_defined_pattern():
    close = [float(i) for i in range(60, 30, -1)]
    open_ = [c + 0.2 for c in close]

    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01", periods=30, freq="D", tz="UTC").astype(str),
            "symbol": ["TEST"] * 30,
            "open": open_,
            "close": close,
        }
    )

    out = compute_up_down_wave_signals(df, config=UpDownWaveConfig(ma_period=20))

    assert int(out.iloc[-1]["downwave"]) == 1
