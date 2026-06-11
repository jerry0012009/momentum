import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.factors.pytrendline_bridge import PyTrendlineConfig, detect_pytrendlines  # noqa: E402


def _base_df(n: int = 80) -> pd.DataFrame:
    idx = np.arange(n)
    close = 100.0 + 0.08 * idx + 1.2 * np.sin(idx / 5.0)
    return pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01 00:00:00", periods=n, freq="5min", tz="UTC").astype(str),
            "open": close - 0.05,
            "high": close + 0.25,
            "low": close - 0.25,
            "close": close,
            "volume": [100] * n,
        }
    )


def test_detect_pytrendlines_runs_on_small_window():
    result = detect_pytrendlines(
        _base_df(),
        config=PyTrendlineConfig(window_bars=48, min_points_required=2, all_pts_must_be_pivots=True),
    )
    assert "candles_df" in result
    assert len(result["candles_df"]) == 48
    assert "support_trendlines" in result
    assert "resistance_trendlines" in result
