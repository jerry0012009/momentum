"""Event-style backtest for UpWave/DownWave signals with fixed holding period.

Rules:
- Signal observed at day t close
- Enter at next trading day open (t+1)
- Exit at day (t+hold_days) close
- UpWave -> long trade
- DownWave -> short trade
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import pandas as pd


@dataclass(frozen=True)
class WaveBacktestConfig:
    hold_days: int = 5
    fee_bps_roundtrip: float = 0.0


def _safe_float(x) -> float:
    try:
        v = float(x)
    except Exception:
        return float("nan")
    return v if math.isfinite(v) else float("nan")


def evaluate_wave_hold(
    signal_df: pd.DataFrame,
    *,
    config: WaveBacktestConfig = WaveBacktestConfig(),
) -> tuple[pd.DataFrame, pd.DataFrame]:
    required = {"timestamp", "open", "close", "upwave", "downwave"}
    missing = required - set(signal_df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df = signal_df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    sort_cols = ["timestamp"]
    has_symbol = "symbol" in df.columns
    if has_symbol:
        sort_cols = ["symbol", "timestamp"]

    df = df.sort_values(sort_cols).reset_index(drop=True)

    trades: list[dict] = []

    fee = config.fee_bps_roundtrip / 10000.0

    group_iter = df.groupby("symbol", sort=True) if has_symbol else [("ALL", df)]

    for symbol, g in group_iter:
        g = g.reset_index(drop=True)
        n = len(g)

        for i, row in g.iterrows():
            # Need entry at i+1 and exit at i+hold_days
            entry_i = i + 1
            exit_i = i + config.hold_days
            if exit_i >= n:
                continue

            up = int(row["upwave"]) == 1
            down = int(row["downwave"]) == 1
            if not up and not down:
                continue

            entry_open = _safe_float(g.iloc[entry_i]["open"])
            exit_close = _safe_float(g.iloc[exit_i]["close"])
            if not math.isfinite(entry_open) or not math.isfinite(exit_close) or entry_open <= 0 or exit_close <= 0:
                continue

            if up:
                side = "long"
                signal = "upwave"
                gross_ret = exit_close / entry_open - 1.0
            else:
                side = "short"
                signal = "downwave"
                gross_ret = entry_open / exit_close - 1.0

            net_ret = gross_ret - fee

            trades.append(
                {
                    "symbol": symbol,
                    "signal_ts": row["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "signal": signal,
                    "side": side,
                    "entry_ts": g.iloc[entry_i]["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "exit_ts": g.iloc[exit_i]["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "entry_open": entry_open,
                    "exit_close": exit_close,
                    "hold_days": int(config.hold_days),
                    "gross_ret": gross_ret,
                    "net_ret": net_ret,
                    "win": int(net_ret > 0),
                }
            )

    trades_df = pd.DataFrame(trades)

    if trades_df.empty:
        summary_df = pd.DataFrame(
            columns=[
                "symbol",
                "signal",
                "trades",
                "win_rate",
                "avg_ret",
                "median_ret",
                "cum_ret_mult",
            ]
        )
        return trades_df, summary_df

    summary = (
        trades_df.groupby(["symbol", "signal"], as_index=False)
        .agg(
            trades=("net_ret", "size"),
            win_rate=("win", "mean"),
            avg_ret=("net_ret", "mean"),
            median_ret=("net_ret", "median"),
            cum_ret_mult=("net_ret", lambda s: float((1.0 + s).prod() - 1.0)),
        )
        .sort_values(["symbol", "signal"])
        .reset_index(drop=True)
    )

    return trades_df, summary
