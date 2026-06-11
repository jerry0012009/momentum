import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.signals.ema_donchian_breakout import (  # noqa: E402
    EmaDonchianBreakoutConfig,
    compute_ema_donchian_breakout_signals,
)


def _trend_breakout_df() -> pd.DataFrame:
    close = []
    price = 100.0
    for i in range(180):
        if i < 120:
            price += 0.05
        else:
            price += 0.25
        close.append(price)
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


def test_breakout_signal_fires_in_uptrend():
    out = compute_ema_donchian_breakout_signals(
        _trend_breakout_df(),
        config=EmaDonchianBreakoutConfig(
            ema_window_1h=8,
            donchian_lookback=12,
            confirm_bars=2,
            use_ema_slope=True,
        ),
    )
    assert int(out["long_signal"].sum()) >= 1
    sig_rows = out[out["long_signal"] == 1]
    assert (sig_rows["long_bias"] == 1).all()


def test_confirmation_reduces_signal_count():
    df = _trend_breakout_df()
    fast = compute_ema_donchian_breakout_signals(
        df,
        config=EmaDonchianBreakoutConfig(
            ema_window_1h=8,
            donchian_lookback=12,
            confirm_bars=1,
            use_ema_slope=False,
        ),
    )
    slow = compute_ema_donchian_breakout_signals(
        df,
        config=EmaDonchianBreakoutConfig(
            ema_window_1h=8,
            donchian_lookback=12,
            confirm_bars=3,
            use_ema_slope=False,
        ),
    )
    assert int(slow["long_signal"].sum()) <= int(fast["long_signal"].sum())
