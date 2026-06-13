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
        lookback_window: Max bars of history the function may access.
        expected_direction: "positive", "negative", or "conditional".
        compute_fn: (DataFrame) -> Series. Receives a single-symbol group.
        status: Current evaluation status (default "DIAGNOSTIC_PROBE").
        notes: Free-text notes.
    """
    factor_id: str
    family: str
    required_columns: list[str]
    lookback_window: int
    expected_direction: str
    compute_fn: Callable[[pd.DataFrame], pd.Series]
    status: str = "DIAGNOSTIC_PROBE"
    notes: str = ""
