import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.analytics.wave_hold_backtest import WaveBacktestConfig, evaluate_wave_hold


def test_wave_hold_long_short_basic():
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01", periods=8, freq="D", tz="UTC").astype(str),
            "symbol": ["TEST"] * 8,
            "open": [10, 10, 11, 12, 13, 14, 15, 16],
            "close": [10, 11, 12, 13, 14, 15, 16, 17],
            "upwave": [1, 0, 0, 0, 0, 0, 0, 0],
            "downwave": [0, 1, 0, 0, 0, 0, 0, 0],
        }
    )

    trades, summary = evaluate_wave_hold(df, config=WaveBacktestConfig(hold_days=3))

    # signal at idx0 -> entry idx1 open=10, exit idx3 close=13 => long +30%
    # signal at idx1 -> entry idx2 open=11, exit idx4 close=14 => short 11/14-1=-21.43%
    assert len(trades) == 2

    up = trades[trades["signal"] == "upwave"].iloc[0]
    dn = trades[trades["signal"] == "downwave"].iloc[0]

    assert abs(up["net_ret"] - 0.3) < 1e-9
    assert abs(dn["net_ret"] - (11 / 14 - 1)) < 1e-9

    assert len(summary) == 2
