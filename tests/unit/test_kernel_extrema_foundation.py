import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.factors.confirmed_extrema import ConfirmedExtremaConfig, compute_confirmed_extrema  # noqa: E402
from momentum.factors.endpoint_nadaraya_watson import (  # noqa: E402
    EndpointNadarayaWatsonConfig,
    compute_endpoint_nadaraya_watson,
)


def _base_df(n: int = 220) -> pd.DataFrame:
    idx = np.arange(n)
    close = 100.0 + 0.06 * idx + 1.6 * np.sin(idx / 6.0)
    return pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01 00:00:00", periods=n, freq="5min", tz="UTC").astype(str),
            "symbol": ["TEST"] * n,
            "open": close - 0.05,
            "high": close + 0.20,
            "low": close - 0.20,
            "close": close,
            "volume": [100] * n,
        }
    )


def test_endpoint_nw_prefix_stable():
    full = compute_endpoint_nadaraya_watson(
        _base_df(),
        config=EndpointNadarayaWatsonConfig(bandwidth=4.0, lookback=40, result_column="nwe_middle"),
    )
    prefix = compute_endpoint_nadaraya_watson(
        _base_df().iloc[:140].copy(),
        config=EndpointNadarayaWatsonConfig(bandwidth=4.0, lookback=40, result_column="nwe_middle"),
    )
    assert np.allclose(
        full["nwe_middle"].iloc[:140].to_numpy(),
        prefix["nwe_middle"].to_numpy(),
        equal_nan=True,
        atol=1e-12,
    )


def test_confirmed_extrema_waits_for_right_bars_and_anchors_on_raw_prices():
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01", periods=9, freq="5min", tz="UTC").astype(str),
            "nwe_middle": [0.0, 1.0, 2.0, 5.0, 2.0, 1.0, 0.0, 1.0, 2.0],
            "high": [0.0, 1.0, 2.0, 5.5, 6.2, 1.0, 0.0, 1.0, 2.0],
            "low": [-1.0, -0.5, 0.0, 4.5, 1.8, 0.5, -2.5, -1.0, 0.0],
        }
    )
    out = compute_confirmed_extrema(
        df,
        config=ConfirmedExtremaConfig(
            value_column="nwe_middle",
            neighbor_bars=2,
            anchor_window_bars=2,
        ),
    )
    assert int(out["confirmed_high"].iloc[:5].sum()) == 0
    assert int(out["confirmed_high"].iloc[5]) == 1
    assert int(out["confirmed_high_origin_index"].iloc[5]) == 4
    assert float(out["confirmed_high_value"].iloc[5]) == 6.2


def test_confirmed_extrema_prefix_stable():
    smooth = compute_endpoint_nadaraya_watson(
        _base_df(),
        config=EndpointNadarayaWatsonConfig(bandwidth=4.0, lookback=40, result_column="nwe_middle"),
    )
    full = compute_confirmed_extrema(
        smooth,
        config=ConfirmedExtremaConfig(value_column="nwe_middle", neighbor_bars=3),
    )

    smooth_prefix = compute_endpoint_nadaraya_watson(
        _base_df().iloc[:160].copy(),
        config=EndpointNadarayaWatsonConfig(bandwidth=4.0, lookback=40, result_column="nwe_middle"),
    )
    prefix = compute_confirmed_extrema(
        smooth_prefix,
        config=ConfirmedExtremaConfig(value_column="nwe_middle", neighbor_bars=3),
    )

    for col in [
        "confirmed_high",
        "confirmed_low",
        "confirmed_high_value",
        "confirmed_low_value",
        "confirmed_high_origin_index",
        "confirmed_low_origin_index",
    ]:
        left = full[col].iloc[:160].to_numpy()
        right = prefix[col].to_numpy()
        assert np.allclose(left, right, equal_nan=True, atol=1e-12)
