#!/usr/bin/env python3
"""Build compact decision-support tables from trendline segment interval sweep artifacts.

Outputs:
- interval_long_asset_winners.csv
- rebound_long_interval_compare.csv

Purpose:
Keep the current Round A/B/C interval-sweep thread interpretable without rerunning
heavy backtests. We only consume the already-generated local summary CSV.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "reports" / "artifacts" / "trendline_segment_backtest_interval_sweep"
INPUT = ARTIFACT_DIR / "interval_strategy_summary.csv"
OUT_WINNERS = ARTIFACT_DIR / "interval_long_asset_winners.csv"
OUT_REBOUND = ARTIFACT_DIR / "rebound_long_interval_compare.csv"


def build_long_asset_winners(df: pd.DataFrame) -> pd.DataFrame:
    long_df = df[df["timeframe"] == "long"].copy()
    if long_df.empty:
        return long_df

    idx = long_df.groupby("symbol")["total_return"].idxmax()
    winners = (
        long_df.loc[idx, [
            "symbol",
            "interval",
            "strategy",
            "trades",
            "win_rate",
            "total_return",
            "max_drawdown",
            "long_trades",
            "short_trades",
        ]]
        .sort_values(["total_return", "trades"], ascending=[False, False])
        .reset_index(drop=True)
    )
    winners.insert(0, "rank", range(1, len(winners) + 1))
    return winners


def build_rebound_long_compare(df: pd.DataFrame) -> pd.DataFrame:
    sub = df[(df["timeframe"] == "long") & (df["strategy"] == "rebound")].copy()
    if sub.empty:
        return sub

    pivot = sub.pivot(index="symbol", columns="interval", values=["trades", "win_rate", "total_return", "max_drawdown"])
    pivot.columns = [f"{interval}_{metric}" for metric, interval in pivot.columns]
    pivot = pivot.reset_index()

    def safe_col(name: str) -> pd.Series:
        return pivot[name] if name in pivot.columns else pd.Series([pd.NA] * len(pivot))

    pivot["best_interval_by_return"] = pd.concat(
        {
            "5m": safe_col("5m_total_return"),
            "15m": safe_col("15m_total_return"),
            "30m": safe_col("30m_total_return"),
            "60m": safe_col("60m_total_return"),
        },
        axis=1,
    ).idxmax(axis=1)

    if "30m_total_return" in pivot.columns and "60m_total_return" in pivot.columns:
        pivot["ret_delta_30m_minus_60m"] = pivot["30m_total_return"] - pivot["60m_total_return"]
    if "30m_max_drawdown" in pivot.columns and "60m_max_drawdown" in pivot.columns:
        pivot["dd_delta_30m_minus_60m"] = pivot["30m_max_drawdown"] - pivot["60m_max_drawdown"]

    first_cols = [
        "symbol",
        "best_interval_by_return",
        "ret_delta_30m_minus_60m",
        "dd_delta_30m_minus_60m",
    ]
    remain = [c for c in pivot.columns if c not in first_cols]
    return pivot[first_cols + remain].sort_values("symbol").reset_index(drop=True)


def main() -> None:
    df = pd.read_csv(INPUT)
    winners = build_long_asset_winners(df)
    rebound = build_rebound_long_compare(df)

    OUT_WINNERS.parent.mkdir(parents=True, exist_ok=True)
    winners.to_csv(OUT_WINNERS, index=False)
    rebound.to_csv(OUT_REBOUND, index=False)

    print(f"wrote {OUT_WINNERS}")
    print(f"wrote {OUT_REBOUND}")


if __name__ == "__main__":
    main()
