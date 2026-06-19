"""
Label horizon adapter: converts tidy or wide labels to single-horizon format.

Tidy format: timestamp, symbol, horizon, forward_return
Wide format: timestamp, symbol, ret_fwd_1h, ret_fwd_4h, ret_fwd_24h, ret_fwd_72h

Output: timestamp, symbol, forward_return
"""

import pandas as pd
from typing import Optional
from .schema import WIDE_LABEL_COLUMNS, WIDE_LABEL_MAP


def select_forward_return(
    label_df: pd.DataFrame,
    horizon: str,
    timestamp_col: str = "timestamp",
    symbol_col: str = "symbol",
    horizon_col: str = "horizon",
    return_col: str = "forward_return",
    wide_column_map: Optional[dict] = None,
) -> pd.DataFrame:
    """
    Select a single horizon's forward returns from tidy or wide label data.

    Parameters
    ----------
    label_df : DataFrame in tidy or wide format
    horizon : e.g. "1h", "4h", "24h", "72h"
    timestamp_col, symbol_col, horizon_col, return_col : column names for tidy format
    wide_column_map : optional override for wide column mapping (default: WIDE_LABEL_MAP)

    Returns
    -------
    DataFrame with columns: [timestamp_col, symbol_col, "forward_return"]
    """
    wide_map = wide_column_map or WIDE_LABEL_MAP
    cols = set(label_df.columns)

    # --- Tidy format ---
    if horizon_col in cols and return_col in cols:
        subset = label_df[label_df[horizon_col] == horizon]
        if subset.empty:
            available = sorted(label_df[horizon_col].unique().tolist())
            raise ValueError(
                f"Horizon '{horizon}' not found. Available: {available}"
            )
        return subset[[timestamp_col, symbol_col, return_col]].rename(
            columns={return_col: "forward_return"}
        ).reset_index(drop=True)

    # --- Wide format ---
    if horizon in wide_map:
        wide_col = wide_map[horizon]
        if wide_col in cols:
            return label_df[[timestamp_col, symbol_col, wide_col]].rename(
                columns={wide_col: "forward_return"}
            ).reset_index(drop=True)

    # Neither format matched
    raise ValueError(
        f"Cannot find horizon '{horizon}'. "
        f"Tidy format requires columns: [{timestamp_col}, {symbol_col}, {horizon_col}, {return_col}]. "
        f"Wide format requires one of: {list(wide_map.values())}. "
        f"Label columns found: {sorted(cols)}"
    )
