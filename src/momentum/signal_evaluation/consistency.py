"""
Direction consistency check between RankIC and Quantile Spread.
"""

from typing import Literal


CONSISTENT_POSITIVE = "CONSISTENT_POSITIVE"
CONSISTENT_NEGATIVE = "CONSISTENT_NEGATIVE"
DIRECTION_CONFLICT = "DIRECTION_CONFLICT"
WEAK_SIGNAL = "WEAK_SIGNAL"


def check_rankic_spread_consistency(
    rankic_summary: dict,
    spread_summary: dict,
    threshold: float = 0.0,
) -> str:
    """
    Check whether RankIC direction and quantile spread direction agree.

    Parameters
    ----------
    rankic_summary : dict from summarize_rank_ic (must have 'mean_rank_ic')
    spread_summary : dict from summarize_quantile_spread (must have 'mean_spread')
    threshold : values within [-threshold, +threshold] are treated as ~zero

    Returns
    -------
    One of: CONSISTENT_POSITIVE, CONSISTENT_NEGATIVE, DIRECTION_CONFLICT, WEAK_SIGNAL
    """
    ic = rankic_summary.get("mean_rank_ic", 0.0)
    sp = spread_summary.get("mean_spread", 0.0)

    ic_pos = ic > threshold
    ic_neg = ic < -threshold
    sp_pos = sp > threshold
    sp_neg = sp < -threshold

    # Both positive
    if ic_pos and sp_pos:
        return CONSISTENT_POSITIVE
    # Both negative
    if ic_neg and sp_neg:
        return CONSISTENT_NEGATIVE
    # One positive, one negative → conflict
    if (ic_pos and sp_neg) or (ic_neg and sp_pos):
        return DIRECTION_CONFLICT
    # Both near zero or one near zero
    return WEAK_SIGNAL
