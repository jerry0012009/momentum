"""
Reusable Signal Evaluation Framework

Skeleton package for signal-level metrics.
Old phase scripts (10A/10B/10D) remain as historical audit entry points.
This package provides signal-agnostic evaluation functions.
"""

from .rank_ic import compute_rank_ic, summarize_rank_ic
from .quantile_spread import compute_quantile_spread, summarize_quantile_spread
from .consistency import check_rankic_spread_consistency
from .labels import select_forward_return

__all__ = [
    "compute_rank_ic",
    "summarize_rank_ic",
    "compute_quantile_spread",
    "summarize_quantile_spread",
    "check_rankic_spread_consistency",
    "select_forward_return",
]
