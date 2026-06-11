"""Backtest for EMA-Donchian breakout with ATR stop and opposite-signal reversal."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class EmaDonchianBacktestConfig:
    fee_bps_per_side: float = 4.0
    slippage_bps_per_side: float = 2.0
    atr_period: int = 14
    atr_mult: float = 1.5
    flip_on_reverse_signal: bool = True


@dataclass(frozen=True)
class EmaDonchianBacktestResult:
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



def _compute_atr(df: pd.DataFrame, period: int) -> pd.Series:
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [
            (df["high"] - df["low"]).abs(),
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.rolling(period, min_periods=period).mean()



def evaluate_ema_donchian_breakout(
    signal_df: pd.DataFrame,
    *,
    config: EmaDonchianBacktestConfig = EmaDonchianBacktestConfig(),
) -> EmaDonchianBacktestResult:
    required = {"timestamp", "open", "high", "low", "close", "long_signal", "short_signal"}
    missing = required - set(signal_df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df = signal_df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    has_symbol = "symbol" in df.columns
    sort_cols = ["symbol", "timestamp"] if has_symbol else ["timestamp"]
    df = df.sort_values(sort_cols).reset_index(drop=True)

    cost_rate = (config.fee_bps_per_side + config.slippage_bps_per_side) / 10000.0
    trades: list[dict] = []
    nav_rows: list[dict] = []
    summary_rows: list[dict] = []

    group_iter = df.groupby("symbol", sort=True) if has_symbol else [("ALL", df)]

    for symbol, g in group_iter:
        g = g.copy().reset_index(drop=True)
        g["atr"] = _compute_atr(g, config.atr_period)
        n = len(g)
        if n < max(5, config.atr_period + 2):
            continue

        current_pos = 0
        entry_price = None
        entry_ts = None
        entry_j = None
        signal_ts = None
        stop_price = None
        nav_value = 1.0
        nav_rows.append({"symbol": symbol, "timestamp": g.iloc[0]["timestamp"], "nav": nav_value})

        for j in range(1, n):
            prev = g.iloc[j - 1]
            row = g.iloc[j]
            exec_price = _safe_float(row["open"])

            # execute reversal / new entry based on previous bar close signal
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

            if desired != current_pos and math.isfinite(exec_price) and exec_price > 0:
                if current_pos != 0 and entry_price is not None and entry_ts is not None and signal_ts is not None:
                    side = "long" if current_pos == 1 else "short"
                    gross_mult, net_mult = _calc_trade_mult(side, entry_price, exec_price, cost_rate)
                    net_ret = net_mult - 1.0
                    nav_value *= net_mult
                    trades.append(
                        {
                            "symbol": symbol,
                            "signal_ts": pd.to_datetime(signal_ts, utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "side": side,
                            "entry_ts": pd.to_datetime(entry_ts, utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "exit_ts": pd.to_datetime(row["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "entry_price": entry_price,
                            "exit_price": exec_price,
                            "net_ret": net_ret,
                            "hold_bars": int(j - entry_j) if entry_j is not None else np.nan,
                            "exit_reason": "reverse_or_flat",
                            "win": int(net_ret > 0),
                        }
                    )
                    nav_rows.append({"symbol": symbol, "timestamp": row["timestamp"], "nav": nav_value})
                if desired != 0:
                    atr = _safe_float(row["atr"])
                    if not (math.isfinite(atr) and atr > 0):
                        desired = 0
                    else:
                        current_pos = desired
                        entry_price = exec_price
                        entry_ts = row["timestamp"]
                        entry_j = j
                        signal_ts = prev["timestamp"]
                        stop_price = entry_price - config.atr_mult * atr if current_pos == 1 else entry_price + config.atr_mult * atr
                if desired == 0:
                    current_pos = 0
                    entry_price = None
                    entry_ts = None
                    entry_j = None
                    signal_ts = None
                    stop_price = None

            # intrabar ATR stop
            if current_pos != 0 and stop_price is not None and entry_price is not None and entry_ts is not None and signal_ts is not None:
                stop_hit = False
                exit_price = None
                if current_pos == 1 and _safe_float(row["low"]) <= stop_price:
                    stop_hit = True
                    exit_price = stop_price
                elif current_pos == -1 and _safe_float(row["high"]) >= stop_price:
                    stop_hit = True
                    exit_price = stop_price
                if stop_hit and math.isfinite(exit_price) and exit_price > 0:
                    side = "long" if current_pos == 1 else "short"
                    gross_mult, net_mult = _calc_trade_mult(side, entry_price, exit_price, cost_rate)
                    net_ret = net_mult - 1.0
                    nav_value *= net_mult
                    trades.append(
                        {
                            "symbol": symbol,
                            "signal_ts": pd.to_datetime(signal_ts, utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "side": side,
                            "entry_ts": pd.to_datetime(entry_ts, utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "exit_ts": pd.to_datetime(row["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "entry_price": entry_price,
                            "exit_price": exit_price,
                            "net_ret": net_ret,
                            "hold_bars": int(j - entry_j) if entry_j is not None else np.nan,
                            "exit_reason": "atr_stop",
                            "win": int(net_ret > 0),
                        }
                    )
                    nav_rows.append({"symbol": symbol, "timestamp": row["timestamp"], "nav": nav_value})
                    current_pos = 0
                    entry_price = None
                    entry_ts = None
                    entry_j = None
                    signal_ts = None
                    stop_price = None

        if current_pos != 0 and entry_price is not None and entry_ts is not None and signal_ts is not None:
            final_row = g.iloc[-1]
            exit_price = _safe_float(final_row["close"])
            if math.isfinite(exit_price) and exit_price > 0:
                side = "long" if current_pos == 1 else "short"
                gross_mult, net_mult = _calc_trade_mult(side, entry_price, exit_price, cost_rate)
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
                        "net_ret": net_ret,
                        "hold_bars": int(n - entry_j) if entry_j is not None else np.nan,
                        "exit_reason": "force_close_final_bar",
                        "win": int(net_ret > 0),
                    }
                )
                nav_rows.append({"symbol": symbol, "timestamp": final_row["timestamp"], "nav": nav_value})

        tdf = pd.DataFrame([x for x in trades if x["symbol"] == symbol])
        ndf = pd.DataFrame([x for x in nav_rows if x["symbol"] == symbol]).sort_values("timestamp")
        running_peak = ndf["nav"].cummax() if not ndf.empty else pd.Series(dtype=float)
        drawdown = ndf["nav"] / running_peak - 1.0 if not ndf.empty else pd.Series(dtype=float)
        max_dd = float(drawdown.min()) if len(drawdown) else 0.0

        if tdf.empty:
            summary_rows.append(
                {
                    "symbol": symbol,
                    "trades": 0,
                    "win_rate": np.nan,
                    "avg_ret": np.nan,
                    "median_ret": np.nan,
                    "total_return": float(ndf["nav"].iloc[-1] - 1.0) if not ndf.empty else 0.0,
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

    return EmaDonchianBacktestResult(
        trades=pd.DataFrame(trades),
        nav=pd.DataFrame(nav_rows),
        summary=pd.DataFrame(summary_rows),
    )


__all__ = [
    "EmaDonchianBacktestConfig",
    "EmaDonchianBacktestResult",
    "evaluate_ema_donchian_breakout",
]
