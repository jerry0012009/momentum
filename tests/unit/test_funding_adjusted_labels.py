import numpy as np
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from funding_adjusted_labels import build_funding_cost_columns, horizon_to_hours


def test_horizon_to_hours():
    assert horizon_to_hours("1h") == 1
    assert horizon_to_hours("8h") == 8


def test_funding_events_are_summed_inside_forward_window():
    ts = pd.date_range("2026-01-01", periods=6, freq="h", tz="UTC")
    funding = pd.DataFrame({
        "timestamp": ts,
        "symbol": ["BTCUSDT"] * len(ts),
        "funding_rate": [np.nan, 0.0001, np.nan, 0.0002, np.nan, np.nan],
        "funding_interval_hours": [1.0] * len(ts),
        "funding_age_hours": [np.nan, 0.0, np.nan, 0.0, np.nan, np.nan],
    })

    out = build_funding_cost_columns(funding, ["1h", "4h"])
    first = out.iloc[0]

    assert np.isclose(first["funding_cost_fwd_1h"], 0.0001)
    assert np.isclose(first["funding_cost_fwd_4h"], 0.0003)
    assert first["funding_hours_covered_4h"] == 2


def test_window_without_settlement_event_has_zero_cost():
    ts = pd.date_range("2026-01-01", periods=5, freq="h", tz="UTC")
    funding = pd.DataFrame({
        "timestamp": ts,
        "symbol": ["BTCUSDT"] * len(ts),
        "funding_rate": [np.nan, 0.0001, np.nan, np.nan, np.nan],
        "funding_interval_hours": [1.0] * len(ts),
        "funding_age_hours": [np.nan, 0.0, np.nan, np.nan, np.nan],
    })

    out = build_funding_cost_columns(funding, ["4h"])
    first = out.iloc[0]

    assert first["funding_hours_covered_4h"] == 1
    assert np.isclose(first["funding_cost_fwd_4h"], 0.0001)
