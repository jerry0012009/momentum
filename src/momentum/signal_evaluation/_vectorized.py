"""
Vectorized fast paths for RankIC and Quantile Spread.

These replace the per-timestamp Python for-loop with matrix operations.
Results must match the reference implementations within float tolerance.
"""

import numpy as np
import pandas as pd


def _pivot_to_matrix(df, value_col, group_col="timestamp", symbol_col="symbol"):
    """Pivot long df to wide (timestamps × symbols) matrix. Returns (matrix, index, columns)."""
    wide = df.pivot_table(index=group_col, columns=symbol_col, values=value_col, aggfunc="first")
    return wide.values, wide.index, wide.columns


def _rank_rows(mat):
    """Rank each row (axis=1), NaN-aware. Returns float64 matrix of ranks."""
    # Use numpy for speed. NaN gets NaN rank.
    result = np.full_like(mat, np.nan, dtype=np.float64)
    for i in range(mat.shape[0]):
        row = mat[i]
        valid = ~np.isnan(row)
        n = valid.sum()
        if n < 2:
            continue
        # argsort twice gives ranks (0-based)
        valid_vals = row[valid]
        order = valid_vals.argsort()
        ranks = np.empty(n, dtype=np.float64)
        ranks[order] = np.arange(1, n + 1, dtype=np.float64)
        result[i, valid] = ranks
    return result


def _row_pearson(x, y):
    """Row-wise Pearson correlation. x, y: (n_timestamps, n_symbols). Returns (n_timestamps,)."""
    # Mask rows where either has NaN
    valid = ~(np.isnan(x) | np.isnan(y))
    n_per_row = valid.sum(axis=1)

    # Replace NaN with 0 for computation, then mask
    x_clean = np.where(valid, x, 0.0)
    y_clean = np.where(valid, y, 0.0)

    # Means
    n = np.maximum(n_per_row, 1).astype(np.float64)
    mean_x = x_clean.sum(axis=1) / n
    mean_y = y_clean.sum(axis=1) / n

    # Centered
    cx = x_clean - mean_x[:, None]
    cy = y_clean - mean_y[:, None]
    cx = np.where(valid, cx, 0.0)
    cy = np.where(valid, cy, 0.0)

    # Covariance and std
    cov = (cx * cy).sum(axis=1)
    var_x = (cx * cx).sum(axis=1)
    var_y = (cy * cy).sum(axis=1)

    denom = np.sqrt(var_x * var_y)
    with np.errstate(divide="ignore", invalid="ignore"):
        corr = np.where(denom > 0, cov / denom, np.nan)

    # Mark rows with too few symbols
    corr[n_per_row < 2] = np.nan
    return corr


def compute_rank_ic_vectorized(
    signal_df, label_df,
    signal_col="signal_value", return_col="forward_return",
    group_col="timestamp", min_symbols=3,
):
    """Vectorized RankIC: pivot → rank → row-wise Pearson."""
    merged = signal_df.merge(label_df, on=[group_col, "symbol"], how="inner")
    valid = merged[[group_col, "symbol", signal_col, return_col]].dropna(subset=[signal_col, return_col])

    sig_mat, idx, cols = _pivot_to_matrix(valid, signal_col, group_col)
    ret_mat, _, _ = _pivot_to_matrix(valid, return_col, group_col)

    sig_ranked = _rank_rows(sig_mat)
    ret_ranked = _rank_rows(ret_mat)

    corr = _row_pearson(sig_ranked, ret_ranked)
    n_symbols = (~np.isnan(sig_ranked) & ~np.isnan(ret_ranked)).sum(axis=1).astype(float)

    # Apply min_symbols filter
    corr[n_symbols < min_symbols] = np.nan

    result = pd.DataFrame({
        group_col: idx,
        "rank_ic": corr,
        "n_symbols": n_symbols,
    })
    return result


def compute_quantile_spread_legacy_vectorized(
    signal_df, label_df,
    signal_col="signal_value", return_col="forward_return",
    group_col="timestamp", quantile_frac=0.20, min_cross_section=10,
):
    """Vectorized legacy Phase 10A spread: pivot → sort rows → head/tail."""
    merged = signal_df.merge(label_df, on=[group_col, "symbol"], how="inner")
    valid = merged[[group_col, "symbol", signal_col, return_col]].dropna(subset=[signal_col, return_col])

    sig_mat, idx, cols = _pivot_to_matrix(valid, signal_col, group_col)
    ret_mat, _, _ = _pivot_to_matrix(valid, return_col, group_col)

    n_ts, n_sym = sig_mat.shape

    results = []
    for i in range(n_ts):
        row_sig = sig_mat[i]
        row_ret = ret_mat[i]
        valid_mask = ~np.isnan(row_sig) & ~np.isnan(row_ret)
        n = valid_mask.sum()

        if n < min_cross_section:
            results.append({
                group_col: idx[i], "top_mean": np.nan, "bottom_mean": np.nan,
                "spread": np.nan, "n_top": 0, "n_bottom": 0,
            })
            continue

        # Sort by signal descending
        valid_sig = row_sig[valid_mask]
        valid_ret = row_ret[valid_mask]
        order = valid_sig.argsort()[::-1]  # descending
        n_q = max(int(n * quantile_frac), 1)

        top_ret = valid_ret[order[:n_q]]
        bottom_ret = valid_ret[order[-n_q:]]

        top_mean = top_ret.mean()
        bottom_mean = bottom_ret.mean()
        spread = top_mean - bottom_mean

        results.append({
            group_col: idx[i], "top_mean": top_mean, "bottom_mean": bottom_mean,
            "spread": spread, "n_top": n_q, "n_bottom": n_q,
        })

    return pd.DataFrame(results)
