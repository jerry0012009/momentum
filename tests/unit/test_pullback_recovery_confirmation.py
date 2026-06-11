import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.signals.pullback_recovery_confirmation import (  # noqa: E402
    PullbackRecoveryConfirmationConfig,
    compute_pullback_recovery_confirmation_signals,
)


def _long_case_df() -> pd.DataFrame:
    close = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 110, 112]
    high = [c + 0.4 for c in close]
    low = [c - 0.4 for c in close]
    open_ = [c - 0.1 for c in close]
    volume = [100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150, 155, 60, 320]
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


def _short_case_df() -> pd.DataFrame:
    close = [112, 111, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 102, 100]
    high = [c + 0.4 for c in close]
    low = [c - 0.4 for c in close]
    open_ = [c + 0.1 for c in close]
    volume = [100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150, 155, 60, 320]
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


def test_long_confirmation_triggers_on_pullback_then_recovery():
    out = compute_pullback_recovery_confirmation_signals(
        _long_case_df(),
        config=PullbackRecoveryConfirmationConfig(
            window_5m=2,
            window_15m=2,
            threshold_5m=0.0,
            threshold_15m=0.0,
            vol_window=3,
            pullback_lookback=2,
            vol_recover_th=0.5,
            breakout_lookback=1,
        ),
    )
    assert int(out.iloc[-1]["long_signal"]) == 1
    assert int(out.iloc[-1]["short_signal"]) == 0


def test_short_confirmation_triggers_on_rebound_then_breakdown():
    out = compute_pullback_recovery_confirmation_signals(
        _short_case_df(),
        config=PullbackRecoveryConfirmationConfig(
            window_5m=2,
            window_15m=2,
            threshold_5m=0.0,
            threshold_15m=0.0,
            vol_window=3,
            pullback_lookback=2,
            vol_recover_th=0.5,
            breakout_lookback=1,
        ),
    )
    assert int(out.iloc[-1]["short_signal"]) == 1
    assert int(out.iloc[-1]["long_signal"]) == 0


def test_larger_breakout_window_is_stricter():
    df = _long_case_df()
    out1 = compute_pullback_recovery_confirmation_signals(
        df,
        config=PullbackRecoveryConfirmationConfig(
            window_5m=2,
            window_15m=2,
            threshold_5m=0.0,
            threshold_15m=0.0,
            vol_window=3,
            pullback_lookback=2,
            vol_recover_th=0.5,
            breakout_lookback=1,
        ),
    )
    out3 = compute_pullback_recovery_confirmation_signals(
        df,
        config=PullbackRecoveryConfirmationConfig(
            window_5m=2,
            window_15m=2,
            threshold_5m=0.0,
            threshold_15m=0.0,
            vol_window=3,
            pullback_lookback=2,
            vol_recover_th=0.5,
            breakout_lookback=3,
        ),
    )
    assert int(out1.iloc[-1]["long_signal"]) >= int(out3.iloc[-1]["long_signal"])
