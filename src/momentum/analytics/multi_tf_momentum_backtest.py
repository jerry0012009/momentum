"""Backtest for multi-timeframe momentum reversal strategy.

Rules:
- Signal observed at 5m bar close t
- Execute at next 5m bar open (t+1)
- If flat: follow the signal direction
- If already in position: ignore same-direction signals
- If opposite signal appears: close and immediately reverse at next open
- Force-close any remaining position at the final close
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class MultiTfMomentumBacktestConfig:
    fee_bps_per_side: float = 4.0
    slippage_bps_per_side: float = 2.0
    flip_on_reverse_signal: bool = True
    enable_atr_trailing_stop: bool = False
    atr_period: int = 14
    atr_trailing_mult: float = 2.5


@dataclass(frozen=True)
class MultiTfMomentumBacktestResult:
    trades: pd.DataFrame
    nav: pd.DataFrame
    summary: pd.DataFrame


def _safe_float(x) -> float:
    try:
        v = float(x)
    except Exception:
        return float("nan")
    return v if math.isfinite(v) else float("nan")


def _calc_trade_mult(side: str, entry_price: float, exit_price: float, cost_rate: float) -> tuple[float, float]:
    if side == "long":
        gross_mult = exit_price / entry_price
    else:
        gross_mult = entry_price / exit_price
    net_mult = gross_mult * (1.0 - cost_rate) * (1.0 - cost_rate)
    return gross_mult, net_mult


def evaluate_multi_tf_momentum_reversal(
    signal_df: pd.DataFrame,
    *,
    config: MultiTfMomentumBacktestConfig = MultiTfMomentumBacktestConfig(),
) -> MultiTfMomentumBacktestResult:
    required = {"timestamp", "open", "close", "long_signal", "short_signal"}
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

    cost_rate = (config.fee_bps_per_side + config.slippage_bps_per_side) / 10000.0

    trades: list[dict] = []
    nav_rows: list[dict] = []
    summary_rows: list[dict] = []

    group_iter = df.groupby("symbol", sort=True) if has_symbol else [("ALL", df)]

    for symbol, g in group_iter:
        g = g.reset_index(drop=True)
        n = len(g)
        if n < 3:
            continue

        current_pos = 0  # 1 long, -1 short, 0 flat
        entry_price = None
        entry_ts = None
        entry_j = None
        signal_ts = None
        nav_value = 1.0
        nav_rows.append({"symbol": symbol, "timestamp": g.iloc[0]["timestamp"], "nav": nav_value})

        for j in range(1, n):
            prev = g.iloc[j - 1]
            exec_row = g.iloc[j]
            long_sig = int(prev["long_signal"]) == 1
            short_sig = int(prev["short_signal"]) == 1

            desired = current_pos
            if current_pos == 0:
                if long_sig and not short_sig:
                    desired = 1
                elif short_sig and not long_sig:
                    desired = -1
            elif current_pos == 1:
                if short_sig and not long_sig:
                    desired = -1 if config.flip_on_reverse_signal else 0
            elif current_pos == -1:
                if long_sig and not short_sig:
                    desired = 1 if config.flip_on_reverse_signal else 0

            exec_price = _safe_float(exec_row["open"])
            if desired != current_pos and math.isfinite(exec_price) and exec_price > 0:
                if current_pos != 0 and entry_price is not None and entry_ts is not None and signal_ts is not None:
                    side = "long" if current_pos == 1 else "short"
                    gross_mult, net_mult = _calc_trade_mult(side, entry_price, exec_price, cost_rate)
                    gross_ret = gross_mult - 1.0
                    net_ret = net_mult - 1.0
                    nav_value *= net_mult
                    exit_reason = "reverse_to_long" if desired == 1 else "reverse_to_short" if desired == -1 else "flat"
                    trades.append(
                        {
                            "symbol": symbol,
                            "signal_ts": pd.to_datetime(signal_ts, utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "side": side,
                            "entry_ts": pd.to_datetime(entry_ts, utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "exit_ts": pd.to_datetime(exec_row["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "entry_price": entry_price,
                            "exit_price": exec_price,
                            "gross_ret": gross_ret,
                            "net_ret": net_ret,
                            "hold_bars": int(j - entry_j) if entry_j is not None else np.nan,
                            "exit_reason": exit_reason,
                            "win": int(net_ret > 0),
                        }
                    )
                    nav_rows.append({"symbol": symbol, "timestamp": exec_row["timestamp"], "nav": nav_value})

                if desired != 0:
                    current_pos = desired
                    entry_price = exec_price
                    entry_ts = exec_row["timestamp"]
                    entry_j = j
                    signal_ts = prev["timestamp"]
                else:
                    current_pos = 0
                    entry_price = None
                    entry_ts = None
                    entry_j = None
                    signal_ts = None

        # force-close remaining position at final close
        if current_pos != 0 and entry_price is not None and entry_ts is not None and signal_ts is not None:
            final_row = g.iloc[-1]
            exit_price = _safe_float(final_row["close"])
            if math.isfinite(exit_price) and exit_price > 0:
                side = "long" if current_pos == 1 else "short"
                gross_mult, net_mult = _calc_trade_mult(side, entry_price, exit_price, cost_rate)
                gross_ret = gross_mult - 1.0
                net_ret = net_mult - 1.0
                nav_value *= net_mult
                trades.append(
                    {
                        "symbol": symbol,
                        "signal_ts": pd.to_datetime(signal_ts, utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "side": side,
                        "entry_ts": pd.to_datetime(entry_ts, utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "exit_ts": pd.to_datetime(final_row["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "entry_price": entry_price,
                        "exit_price": exit_price,
                        "gross_ret": gross_ret,
                        "net_ret": net_ret,
                        "hold_bars": int(n - entry_j) if entry_j is not None else np.nan,
                        "exit_reason": "force_close_final_bar",
                        "win": int(net_ret > 0),
                    }
                )
                nav_rows.append({"symbol": symbol, "timestamp": final_row["timestamp"], "nav": nav_value})

        tdf = pd.DataFrame([x for x in trades if x["symbol"] == symbol])
        ndf = pd.DataFrame([x for x in nav_rows if x["symbol"] == symbol]).sort_values("timestamp")
        if ndf.empty:
            summary_rows.append(
                {
                    "symbol": symbol,
                    "trades": 0,
                    "win_rate": np.nan,
                    "avg_ret": np.nan,
                    "median_ret": np.nan,
                    "total_return": 0.0,
                    "max_drawdown": 0.0,
                    "long_trades": 0,
                    "short_trades": 0,
                }
            )
            continue

        running_peak = ndf["nav"].cummax()
        drawdown = ndf["nav"] / running_peak - 1.0
        max_dd = float(drawdown.min()) if len(drawdown) else 0.0

        if tdf.empty:
            summary_rows.append(
                {
                    "symbol": symbol,
                    "trades": 0,
                    "win_rate": np.nan,
                    "avg_ret": np.nan,
                    "median_ret": np.nan,
                    "total_return": float(ndf["nav"].iloc[-1] - 1.0),
                    "max_drawdown": max_dd,
                    "long_trades": 0,
                    "short_trades": 0,
                }
            )
        else:
            summary_rows.append(
                {
                    "symbol": symbol,
                    "trades": int(len(tdf)),
                    "win_rate": float(tdf["win"].mean()),
                    "avg_ret": float(tdf["net_ret"].mean()),
                    "median_ret": float(tdf["net_ret"].median()),
                    "total_return": float((1.0 + tdf["net_ret"]).prod() - 1.0),
                    "max_drawdown": max_dd,
                    "long_trades": int((tdf["side"] == "long").sum()),
                    "short_trades": int((tdf["side"] == "short").sum()),
                }
            )

    trades_df = pd.DataFrame(trades)
    nav_df = pd.DataFrame(nav_rows)
    summary_df = pd.DataFrame(summary_rows)
    return MultiTfMomentumBacktestResult(trades=trades_df, nav=nav_df, summary=summary_df)


__all__ = [
    "MultiTfMomentumBacktestConfig",
    "MultiTfMomentumBacktestResult",
    "evaluate_multi_tf_momentum_reversal",
]
