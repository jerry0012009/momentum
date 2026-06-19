"""
Quantile Spread: Top-minus-bottom bucket forward return.

Two modes:
- "standard" (default): pd.qcut quintile boundaries (reference path)
- "legacy_phase10a": rank-based head/tail (vectorized fast path)
"""

import pandas as pd
import numpy as np


def compute_quantile_spread(
    signal_df: pd.DataFrame,
    label_df: pd.DataFrame,
    signal_col: str = "signal_value",
    return_col: str = "forward_return",
    group_col: str = "timestamp",
    n_quantiles: int = 5,
    mode: str = "standard",
    quantile_frac: float = 0.20,
    min_cross_section: int = 10,
) -> pd.DataFrame:
    """
    Compute per-timestamp top-minus-bottom quantile spread.

    Uses vectorized fast path for legacy_phase10a mode.

    Returns: DataFrame with [group_col, 'top_mean', 'bottom_mean', 'spread', 'n_top', 'n_bottom']
    """
    if mode not in ("standard", "legacy_phase10a", "qcut", "rank_head_tail"):
        raise ValueError(f"Unknown mode: {mode!r}. Use 'standard' or 'legacy_phase10a'.")

    is_legacy = mode in ("legacy_phase10a", "rank_head_tail")

    if is_legacy:
        try:
            from ._vectorized import compute_quantile_spread_legacy_vectorized
            return compute_quantile_spread_legacy_vectorized(
                signal_df, label_df, signal_col, return_col,
                group_col, quantile_frac, min_cross_section
            )
        except Exception:
            pass

    # Reference path (standard mode or legacy fallback)
    return _compute_quantile_spread_reference(
        signal_df, label_df, signal_col, return_col, group_col,
        n_quantiles, is_legacy, quantile_frac, min_cross_section
    )


def _compute_quantile_spread_reference(
    signal_df, label_df,
    signal_col="signal_value", return_col="forward_return",
    group_col="timestamp", n_quantiles=5, is_legacy=False,
    quantile_frac=0.20, min_cross_section=10,
):
    """Reference implementation: per-timestamp loop."""
    merged = signal_df.merge(label_df, on=[group_col, "symbol"], how="inner")
    results = []
    for ts, grp in merged.groupby(group_col):
        valid = grp[[signal_col, return_col]].dropna()
        n = len(valid)

        if is_legacy:
            if n < min_cross_section:
                results.append({
                    group_col: ts, "top_mean": np.nan, "bottom_mean": np.nan,
                    "spread": np.nan, "n_top": 0, "n_bottom": 0,
                })
                continue
            n_q = max(int(n * quantile_frac), 1)
            ranked = valid.sort_values(signal_col, ascending=False)
            top = ranked.head(n_q)
            bottom = ranked.tail(n_q)
            top_mean = top[return_col].mean()
            bottom_mean = bottom[return_col].mean()
            spread = top_mean - bottom_mean
            results.append({
                group_col: ts, "top_mean": top_mean, "bottom_mean": bottom_mean,
                "spread": spread, "n_top": len(top), "n_bottom": len(bottom),
            })
        else:
            if n < n_quantiles * 2:
                results.append({
                    group_col: ts, "top_mean": np.nan, "bottom_mean": np.nan,
                    "spread": np.nan, "n_top": 0, "n_bottom": 0,
                })
                continue
            try:
                buckets = pd.qcut(valid[signal_col], n_quantiles, labels=False, duplicates="drop")
            except ValueError:
                results.append({
                    group_col: ts, "top_mean": np.nan, "bottom_mean": np.nan,
                    "spread": np.nan, "n_top": 0, "n_bottom": 0,
                })
                continue
            top_mask = buckets == buckets.max()
            bottom_mask = buckets == buckets.min()
            top_mean = valid.loc[top_mask, return_col].mean()
            bottom_mean = valid.loc[bottom_mask, return_col].mean()
            spread = top_mean - bottom_mean
            results.append({
                group_col: ts, "top_mean": top_mean, "bottom_mean": bottom_mean,
                "spread": spread, "n_top": int(top_mask.sum()), "n_bottom": int(bottom_mask.sum()),
            })

    return pd.DataFrame(results)


def summarize_quantile_spread(spread_df: pd.DataFrame) -> dict:
    """Summarize a spread time series."""
    valid = spread_df["spread"].dropna()
    n = len(valid)
    return {
        "mean_spread": valid.mean() if n > 0 else np.nan,
        "median_spread": valid.median() if n > 0 else np.nan,
        "std_spread": valid.std() if n > 0 else np.nan,
        "positive_fraction": (valid > 0).mean() if n > 0 else np.nan,
        "n_periods": n,
    }
