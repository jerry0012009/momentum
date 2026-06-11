import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.factors.chip_distribution import ChipConfig, estimate_chip_distribution_panel


def test_chip_distribution_summary_ranges():
    bars = pd.DataFrame(
        {
            "timestamp": [
                "2026-01-01T00:00:00Z",
                "2026-01-02T00:00:00Z",
                "2026-01-03T00:00:00Z",
            ],
            "symbol": ["TEST"] * 3,
            "open": [10.0, 10.2, 10.3],
            "high": [10.5, 10.6, 10.7],
            "low": [9.8, 10.0, 10.1],
            "close": [10.2, 10.3, 10.4],
            "volume": [1000, 1200, 900],
        }
    )

    asset, norm, summary = estimate_chip_distribution_panel(
        bars,
        config=ChipConfig(bin_size_pct=0.005),
        default_shares=100_000,
    )

    assert not asset.empty
    assert not norm.empty
    assert len(summary) == 3

    assert summary["winner_ratio"].between(0, 1).all()
    assert summary["trapped_ratio"].between(0, 1).all()
    assert ((summary["winner_ratio"] + summary["trapped_ratio"]).round(8) == 1.0).all()


def test_chip_pct_per_day_sums_near_one():
    bars = pd.DataFrame(
        {
            "timestamp": [
                "2026-01-01T00:00:00Z",
                "2026-01-02T00:00:00Z",
            ],
            "symbol": ["TEST"] * 2,
            "open": [20.0, 20.2],
            "high": [20.5, 20.6],
            "low": [19.7, 20.0],
            "close": [20.3, 20.4],
            "volume": [500, 700],
        }
    )

    asset, _, _ = estimate_chip_distribution_panel(
        bars,
        config=ChipConfig(bin_size_pct=0.005, min_chip_pct=1e-12),
        default_shares=50_000,
    )

    sums = asset.groupby(["timestamp", "symbol"]) ["chip_pct"].sum()
    assert ((sums - 1.0).abs() < 1e-6).all()
