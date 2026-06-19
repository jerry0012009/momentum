"""
RankIC: Cross-sectional Spearman correlation between signal and forward return.

Uses vectorized fast path internally. Falls back to reference on error.
"""

import pandas as pd
import numpy as np


def compute_rank_ic(
    signal_df: pd.DataFrame,
    label_df: pd.DataFrame,
    signal_col: str = "signal_value",
    return_col: str = "forward_return",
    group_col: str = "timestamp",
    method: str = "spearman",
    min_symbols: int = 3,
) -> pd.DataFrame:
    """
    Compute per-timestamp cross-sectional RankIC (Spearman correlation).

    Internally uses vectorized fast path. Falls back to reference on error.

    Returns: DataFrame with columns: [group_col, 'rank_ic', 'n_symbols']
    """
    try:
        from ._vectorized import compute_rank_ic_vectorized
        return compute_rank_ic_vectorized(
            signal_df, label_df, signal_col, return_col, group_col, min_symbols
        )
    except Exception:
        return _compute_rank_ic_reference(
            signal_df, label_df, signal_col, return_col, group_col, method, min_symbols
        )


def _compute_rank_ic_reference(
    signal_df, label_df,
    signal_col="signal_value", return_col="forward_return",
    group_col="timestamp", method="spearman", min_symbols=3,
):
    """Reference implementation: per-timestamp loop."""
    merged = signal_df.merge(label_df, on=[group_col, "symbol"], how="inner")
    results = []
    for ts, grp in merged.groupby(group_col):
        valid = grp[[signal_col, return_col]].dropna()
        n = len(valid)
        if n < min_symbols:
            results.append({group_col: ts, "rank_ic": np.nan, "n_symbols": n})
            continue
        corr = valid[signal_col].corr(valid[return_col], method=method)
        results.append({group_col: ts, "rank_ic": corr, "n_symbols": n})
    return pd.DataFrame(results)


def summarize_rank_ic(rank_ic_df: pd.DataFrame) -> dict:
    """Summarize a rank_ic time series."""
    valid = rank_ic_df["rank_ic"].dropna()
    n = len(valid)
    mean = valid.mean()
    std = valid.std()
    t_stat = (mean / std * np.sqrt(n)) if std > 0 and n > 0 else np.nan
    pos_frac = (valid > 0).mean() if n > 0 else np.nan
    return {
        "mean_rank_ic": mean,
        "std_rank_ic": std,
        "n_periods": n,
        "t_stat": t_stat,
        "positive_fraction": pos_frac,
    }
