"""Unit tests for build_dynamic_universe_monthly_volume.py (Phase 6B).

All tests use synthetic data — no Binance API access required.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from build_dynamic_universe_monthly_volume import (
    build_monthly_universe,
    normalize_base_asset,
    contract_multiplier_from_base,
    month_range,
    write_manifest,
)


# ── Helpers ───────────────────────────────────────────────────────

def _make_candidates(n=20, base_date="2024-01-01"):
    """Create synthetic candidate symbols."""
    rows = []
    for i in range(n):
        base = f"SYM{i:02d}"
        onboard = pd.Timestamp(base_date, tz="UTC") - pd.Timedelta(days=365 + i * 10)
        rows.append({
            "symbol": f"{base}USDT",
            "base_asset": base,
            "normalized_base": base.lower(),
            "contract_multiplier": 1.0,
            "onboard_utc": onboard.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "onboard_ms": int(onboard.timestamp() * 1000),
            "quote_asset": "USDT",
            "contract_type": "PERPETUAL",
            "status": "TRADING",
            "source": "test",
        })
    return pd.DataFrame(rows)


def _make_daily_data(candidates: pd.DataFrame, start: str, end: str, cache_dir: Path):
    """Create synthetic daily quote_volume data for each candidate."""
    rng = np.random.default_rng(42)
    start_ts = pd.Timestamp(start, tz="UTC") - pd.Timedelta(days=40)
    end_ts = pd.Timestamp(end, tz="UTC") + pd.Timedelta(days=7)
    dates = pd.date_range(start_ts, end_ts, freq="D", tz="UTC")

    for _, cand in candidates.iterrows():
        sym = cand["symbol"]
        qv = rng.exponential(1e8, size=len(dates))
        df = pd.DataFrame({"timestamp": dates, "quote_volume": qv})
        cache_path = cache_dir / "daily_1d" / f"{sym}.csv"
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(cache_path, index=False)


# ── Helper function tests ─────────────────────────────────────────

class TestHelpers:
    def test_normalize_base_asset(self):
        assert normalize_base_asset("1000PEPE") == "pepe"
        assert normalize_base_asset("BTC") == "btc"
        assert normalize_base_asset("ETH") == "eth"

    def test_contract_multiplier(self):
        assert contract_multiplier_from_base("1000PEPE") == 1000.0
        assert contract_multiplier_from_base("BTC") == 1.0
        assert contract_multiplier_from_base("ETH") == 1.0

    def test_month_range(self):
        start = pd.Timestamp("2024-06-13", tz="UTC")
        end = pd.Timestamp("2024-09-13", tz="UTC")
        months = month_range(start, end)
        assert months == ["2024-06", "2024-07", "2024-08", "2024-09"]


# ── Previous-month selection ──────────────────────────────────────

class TestPreviousMonthSelection:
    def test_uses_previous_month_only(self, tmp_path):
        """Selection for month M must use only month M-1 data."""
        candidates = _make_candidates(10)
        _make_daily_data(candidates, "2024-06-01", "2024-09-01", tmp_path)

        start = pd.Timestamp("2024-07-01", tz="UTC")
        end = pd.Timestamp("2024-09-01", tz="UTC")
        snapshots, detail = build_monthly_universe(
            candidates, start, end, top_n=5, rank_metric="quote_volume",
            universe_id="test", cache_dir=tmp_path,
        )

        # July selection should use June data
        july = detail[detail["month"] == "2024-07"]
        assert not july.empty
        assert july.iloc[0]["selection_time_start"].startswith("2024-06")
        assert july.iloc[0]["selection_time_end"].startswith("2024-07")

    def test_no_current_month_data_used(self, tmp_path):
        """asof_time and known_at must be month_start, not end."""
        candidates = _make_candidates(10)
        _make_daily_data(candidates, "2024-06-01", "2024-08-01", tmp_path)

        start = pd.Timestamp("2024-07-01", tz="UTC")
        end = pd.Timestamp("2024-08-01", tz="UTC")
        snapshots, _ = build_monthly_universe(
            candidates, start, end, top_n=5, rank_metric="quote_volume",
            universe_id="test", cache_dir=tmp_path,
        )

        # asof_time should equal month_start
        july_rows = snapshots[snapshots["asof_time"].str.startswith("2024-07")]
        assert len(july_rows) == 5
        for _, row in july_rows.iterrows():
            assert row["asof_time"] == row["known_at"]


# ── Top-N selection ───────────────────────────────────────────────

class TestTopNSelection:
    def test_top_n_correct(self, tmp_path):
        """Each month should have exactly top_n symbols."""
        candidates = _make_candidates(15)
        _make_daily_data(candidates, "2024-06-01", "2024-08-01", tmp_path)

        start = pd.Timestamp("2024-07-01", tz="UTC")
        end = pd.Timestamp("2024-08-01", tz="UTC")
        snapshots, detail = build_monthly_universe(
            candidates, start, end, top_n=5, rank_metric="quote_volume",
            universe_id="test", cache_dir=tmp_path,
        )

        for _, row in detail.iterrows():
            assert row["selected_count"] == 5

    def test_rank_ascending(self, tmp_path):
        """Ranks should be 1-based, top volume = rank 1."""
        candidates = _make_candidates(10)
        _make_daily_data(candidates, "2024-06-01", "2024-08-01", tmp_path)

        start = pd.Timestamp("2024-07-01", tz="UTC")
        end = pd.Timestamp("2024-08-01", tz="UTC")
        snapshots, _ = build_monthly_universe(
            candidates, start, end, top_n=5, rank_metric="quote_volume",
            universe_id="test", cache_dir=tmp_path,
        )

        july = snapshots[snapshots["asof_time"].str.startswith("2024-07")]
        assert sorted(july["rank"].tolist()) == [1, 2, 3, 4, 5]


# ── Onboard eligibility ───────────────────────────────────────────

class TestOnboardEligibility:
    def test_listed_after_month_excluded(self, tmp_path):
        """Symbol listed after month_start should not be in that month's universe."""
        candidates = _make_candidates(5)
        # Make SYM04USDT listed after August
        late_onboard = pd.Timestamp("2024-08-15", tz="UTC")
        candidates.loc[candidates["symbol"] == "SYM04USDT", "onboard_ms"] = int(late_onboard.timestamp() * 1000)
        candidates.loc[candidates["symbol"] == "SYM04USDT", "onboard_utc"] = late_onboard.strftime("%Y-%m-%dT%H:%M:%SZ")

        _make_daily_data(candidates, "2024-06-01", "2024-09-01", tmp_path)

        start = pd.Timestamp("2024-07-01", tz="UTC")
        end = pd.Timestamp("2024-09-01", tz="UTC")
        snapshots, _ = build_monthly_universe(
            candidates, start, end, top_n=5, rank_metric="quote_volume",
            universe_id="test", cache_dir=tmp_path,
        )

        # SYM04USDT should not appear in July or August
        july_aug = snapshots[snapshots["asof_time"].str.startswith(("2024-07", "2024-08"))]
        assert "SYM04USDT" not in july_aug["symbol"].values


# ── Output schema ─────────────────────────────────────────────────

class TestOutputSchema:
    def test_snapshot_schema(self, tmp_path):
        candidates = _make_candidates(10)
        _make_daily_data(candidates, "2024-06-01", "2024-08-01", tmp_path)

        start = pd.Timestamp("2024-07-01", tz="UTC")
        end = pd.Timestamp("2024-08-01", tz="UTC")
        snapshots, _ = build_monthly_universe(
            candidates, start, end, top_n=5, rank_metric="quote_volume",
            universe_id="test", cache_dir=tmp_path,
        )

        required_cols = {
            "universe_id", "asof_time", "selection_time_start", "selection_time_end",
            "symbol", "rank", "rank_metric", "rank_metric_value", "eligible",
            "known_at", "source", "universe_mode", "notes",
        }
        assert required_cols.issubset(set(snapshots.columns))

    def test_detail_schema(self, tmp_path):
        candidates = _make_candidates(10)
        _make_daily_data(candidates, "2024-06-01", "2024-08-01", tmp_path)

        start = pd.Timestamp("2024-07-01", tz="UTC")
        end = pd.Timestamp("2024-08-01", tz="UTC")
        _, detail = build_monthly_universe(
            candidates, start, end, top_n=5, rank_metric="quote_volume",
            universe_id="test", cache_dir=tmp_path,
        )

        required_cols = {
            "month", "month_start_utc", "selection_basis",
            "selection_time_start", "selection_time_end",
            "candidate_count", "selected_count",
            "selected_symbols", "entered_symbols", "exited_symbols",
        }
        assert required_cols.issubset(set(detail.columns))

    def test_universe_mode_value(self, tmp_path):
        candidates = _make_candidates(10)
        _make_daily_data(candidates, "2024-06-01", "2024-08-01", tmp_path)

        start = pd.Timestamp("2024-07-01", tz="UTC")
        end = pd.Timestamp("2024-08-01", tz="UTC")
        snapshots, _ = build_monthly_universe(
            candidates, start, end, top_n=5, rank_metric="quote_volume",
            universe_id="test", cache_dir=tmp_path,
        )

        assert (snapshots["universe_mode"] == "dynamic_from_current_listed_pool").all()


# ── Manifest ──────────────────────────────────────────────────────

class TestManifest:
    def test_manifest_includes_limitation(self, tmp_path):
        candidates = _make_candidates(10)
        _make_daily_data(candidates, "2024-06-01", "2024-08-01", tmp_path)

        start = pd.Timestamp("2024-07-01", tz="UTC")
        end = pd.Timestamp("2024-08-01", tz="UTC")
        snapshots, detail = build_monthly_universe(
            candidates, start, end, top_n=5, rank_metric="quote_volume",
            universe_id="test", cache_dir=tmp_path,
        )

        output_dir = tmp_path / "output"
        output_dir.mkdir()
        write_manifest("test", start, end, 5, "quote_volume", "monthly", candidates, snapshots, detail, output_dir)

        import json
        manifest = json.loads((output_dir / "universe_manifest.json").read_text())

        assert manifest["universe_mode"] == "dynamic_from_current_listed_pool"
        assert any("delisted" in lim.lower() for lim in manifest["known_limitations"])
        assert any("survivorship" in lim.lower() for lim in manifest["known_limitations"])
        assert any("point_in_time" in lim.lower() or "PIT" in lim for lim in manifest["known_limitations"])

    def test_manifest_parameters(self, tmp_path):
        candidates = _make_candidates(10)
        _make_daily_data(candidates, "2024-06-01", "2024-08-01", tmp_path)

        start = pd.Timestamp("2024-07-01", tz="UTC")
        end = pd.Timestamp("2024-08-01", tz="UTC")
        snapshots, detail = build_monthly_universe(
            candidates, start, end, top_n=10, rank_metric="quote_volume",
            universe_id="test", cache_dir=tmp_path,
        )

        output_dir = tmp_path / "output"
        output_dir.mkdir()
        write_manifest("test", start, end, 10, "quote_volume", "monthly", candidates, snapshots, detail, output_dir)

        import json
        manifest = json.loads((output_dir / "universe_manifest.json").read_text())
        assert manifest["parameters"]["top_n"] == 10
        assert manifest["candidate_count"] == len(candidates)
