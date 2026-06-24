"""FactorSpec dataclass — metadata + compute function for each factor."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import pandas as pd


@dataclass
class FactorSpec:
    """Declares a factor: what it needs, how to compute it, and its status.

    Attributes:
        factor_id: Unique identifier (e.g. "mom_20h").
        family: Grouping (e.g. "momentum", "volatility", "wq101", "tech").
        required_columns: DataFrame columns the compute function reads.
        lookback_window: Bars required including current bar. E.g. delta(1)
            needs t and t-1 → lookback_window=2. diff(9) needs t and t-9 → 10.
        expected_direction: "positive", "negative", or "conditional".
            Must be set from domain knowledge, NOT from evaluation results.
        compute_fn: (DataFrame) -> Series. Receives a single-symbol group.
            Only used when compute_scope == "single_symbol".
        status: Current evaluation status (default "DIAGNOSTIC_PROBE").
        notes: Free-text notes.
        compute_scope: "single_symbol" (default) or "panel".
            If "panel", panel_compute_fn is called with the full multi-symbol bars.
        panel_compute_fn: (DataFrame) -> DataFrame. Receives full bars (all symbols).
            Must return DataFrame with [timestamp, symbol, factor_id] columns.
            Only used when compute_scope == "panel".
    """
    factor_id: str
    family: str
    required_columns: list[str]
    lookback_window: int
    expected_direction: str
    compute_fn: Callable[[pd.DataFrame], pd.Series] = None  # type: ignore[assignment]
    status: str = "DIAGNOSTIC_PROBE"
    notes: str = ""
    compute_scope: str = "single_symbol"
    panel_compute_fn: Callable[[pd.DataFrame], pd.DataFrame] | None = None
