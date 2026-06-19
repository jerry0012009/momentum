"""Tests for schema and labels module."""

import pandas as pd
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from momentum.signal_evaluation.schema import (
    WIDE_LABEL_COLUMNS, WIDE_LABEL_MAP, SIGNAL_EVALUATION_VERSION,
)
from momentum.signal_evaluation.labels import select_forward_return


class TestSchemaConsistency:
    def test_wide_columns_match_map(self):
        """WIDE_LABEL_COLUMNS and WIDE_LABEL_MAP must agree."""
        map_cols = list(WIDE_LABEL_MAP.values())
        assert WIDE_LABEL_COLUMNS == map_cols

    def test_wide_columns_format(self):
        """All wide columns follow ret_fwd_{h} pattern."""
        for col in WIDE_LABEL_COLUMNS:
            assert col.startswith("ret_fwd_"), f"{col} does not match ret_fwd_{{h}}"

    def test_horizons(self):
        """Map covers 1h, 4h, 24h, 72h."""
        assert set(WIDE_LABEL_MAP.keys()) == {"1h", "4h", "24h", "72h"}


class TestSelectForwardReturnTidy:
    def setup_method(self):
        self.tidy_df = pd.DataFrame({
            "timestamp": pd.Timestamp("2025-01-01"),
            "symbol": ["A", "B", "C", "A", "B", "C"],
            "horizon": ["1h", "1h", "1h", "4h", "4h", "4h"],
            "forward_return": [0.01, 0.02, 0.03, 0.04, 0.05, 0.06],
        })

    def test_filter_1h(self):
        result = select_forward_return(self.tidy_df, "1h")
        assert len(result) == 3
        assert set(result.columns) == {"timestamp", "symbol", "forward_return"}
        assert result["forward_return"].tolist() == [0.01, 0.02, 0.03]

    def test_filter_4h(self):
        result = select_forward_return(self.tidy_df, "4h")
        assert len(result) == 3
        assert result["forward_return"].tolist() == [0.04, 0.05, 0.06]


class TestSelectForwardReturnWide:
    def setup_method(self):
        self.wide_df = pd.DataFrame({
            "timestamp": pd.Timestamp("2025-01-01"),
            "symbol": ["A", "B", "C"],
            "ret_fwd_1h": [0.01, 0.02, 0.03],
            "ret_fwd_4h": [0.04, 0.05, 0.06],
            "ret_fwd_24h": [0.07, 0.08, 0.09],
            "ret_fwd_72h": [0.10, 0.11, 0.12],
        })

    def test_filter_1h(self):
        result = select_forward_return(self.wide_df, "1h")
        assert len(result) == 3
        assert result["forward_return"].tolist() == [0.01, 0.02, 0.03]

    def test_filter_72h(self):
        result = select_forward_return(self.wide_df, "72h")
        assert result["forward_return"].tolist() == [0.10, 0.11, 0.12]


class TestSelectForwardReturnErrors:
    def test_invalid_horizon_tidy(self):
        df = pd.DataFrame({
            "timestamp": [pd.Timestamp("2025-01-01")],
            "symbol": ["A"], "horizon": ["1h"], "forward_return": [0.01],
        })
        with pytest.raises(ValueError, match="999h"):
            select_forward_return(df, "999h")

    def test_invalid_horizon_wide(self):
        df = pd.DataFrame({
            "timestamp": [pd.Timestamp("2025-01-01")],
            "symbol": ["A"], "ret_fwd_1h": [0.01],
        })
        with pytest.raises(ValueError, match="999h"):
            select_forward_return(df, "999h")

    def test_invalid_schema(self):
        df = pd.DataFrame({
            "timestamp": [pd.Timestamp("2025-01-01")],
            "symbol": ["A"], "random_col": [0.01],
        })
        with pytest.raises(ValueError, match="Cannot find horizon"):
            select_forward_return(df, "1h")
