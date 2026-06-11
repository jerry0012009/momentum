import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.analytics.multi_tf_momentum_backtest import (  # noqa: E402
    MultiTfMomentumBacktestConfig,
    evaluate_multi_tf_momentum_reversal,
)


def _bars() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01 00:00:00", periods=6, freq="5min", tz="UTC").astype(str),
            "open": [100, 101, 102, 99, 98, 97],
            "close": [101, 102, 99, 98, 97, 96],
            "long_signal": [1, 0, 0, 0, 0, 0],
            "short_signal": [0, 0, 1, 0, 0, 0],
            "symbol": ["TEST"] * 6,
        }
    )


def test_reversal_backtest_generates_long_then_short():
    out = evaluate_multi_tf_momentum_reversal(
        _bars(),
        config=MultiTfMomentumBacktestConfig(fee_bps_per_side=0.0, slippage_bps_per_side=0.0),
    )
    trades = out.trades
    assert len(trades) == 2
    assert list(trades["side"]) == ["long", "short"]


def test_summary_has_trade_counts():
    out = evaluate_multi_tf_momentum_reversal(
        _bars(),
        config=MultiTfMomentumBacktestConfig(fee_bps_per_side=0.0, slippage_bps_per_side=0.0),
    )
    summary = out.summary.iloc[0]
    assert int(summary["trades"]) == 2
    assert int(summary["long_trades"]) == 1
    assert int(summary["short_trades"]) == 1
