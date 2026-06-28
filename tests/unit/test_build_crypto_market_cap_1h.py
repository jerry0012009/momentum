"""Tests for crypto market-cap build helpers."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import build_crypto_market_cap_1h as cap_builder  # noqa: E402


def test_augment_supply_for_manual_overrides_fetches_only_missing_ids(monkeypatch):
    cg_supply = pd.DataFrame([
        {
            "coingecko_id": "bitcoin",
            "cg_symbol": "btc",
            "cg_name": "Bitcoin",
            "circulating_supply": 19_000_000,
            "total_supply": None,
            "max_supply": 21_000_000,
            "current_market_cap": 1,
            "current_price": 1,
        }
    ])
    overrides = pd.DataFrame({
        "symbol": ["BTCUSDT", "EDUUSDT", "EDUUSDT"],
        "coingecko_id": ["bitcoin", "open-campus", "open-campus"],
    })
    requested: list[list[str]] = []

    def fake_fetch(ids: list[str]) -> pd.DataFrame:
        requested.append(ids)
        return pd.DataFrame([
            {
                "coingecko_id": "open-campus",
                "cg_symbol": "edu",
                "cg_name": "Open Campus",
                "circulating_supply": 260_000_000,
                "total_supply": None,
                "max_supply": None,
                "current_market_cap": 1,
                "current_price": 1,
            }
        ])

    monkeypatch.setattr(cap_builder, "fetch_circulating_supply_by_ids", fake_fetch)

    result = cap_builder.augment_supply_for_manual_overrides(cg_supply, overrides)

    assert requested == [["open-campus"]]
    assert result["coingecko_id"].tolist() == ["bitcoin", "open-campus"]
    assert result.loc[result["coingecko_id"].eq("open-campus"), "circulating_supply"].item() == 260_000_000


def test_augment_supply_for_manual_overrides_handles_empty_supply(monkeypatch):
    overrides = pd.DataFrame({"symbol": ["EDUUSDT"], "coingecko_id": ["open-campus"]})

    monkeypatch.setattr(
        cap_builder,
        "fetch_circulating_supply_by_ids",
        lambda ids: pd.DataFrame({
            "coingecko_id": ids,
            "cg_symbol": ["edu"],
            "cg_name": ["Open Campus"],
            "circulating_supply": [260_000_000],
        }),
    )

    result = cap_builder.augment_supply_for_manual_overrides(pd.DataFrame(), overrides)

    assert result["coingecko_id"].tolist() == ["open-campus"]
