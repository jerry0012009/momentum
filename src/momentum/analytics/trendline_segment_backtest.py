"""Backtest helpers for segment-based trendline breakout/rebound strategies.

Strategy formalization (default):
- Breakout strategy:
  - breakout bar counts as confirmation #1
  - if 3 consecutive closes remain on the breakout side of the frozen prior trendline,
    trigger a continuation entry at the next bar open.
- Rebound strategy:
  - a breakout candidate fails if it does not reach 3 confirmations and closes back
    inside the prior range
  - after 1 additional inside-range close confirmation, trigger a reversal entry at
    the next bar open.

Optimization layers used by the report:
- Round A: core conclusion focuses on long timeframe only
- Round B: medium/short signals can be gated by the next higher timeframe trend
- Round C: ATR trailing stop can exit positions before reverse signals
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
import math

import numpy as np
import pandas as pd

from momentum.analytics.multi_tf_momentum_backtest import (
    MultiTfMomentumBacktestConfig,
)


@dataclass(frozen=True)
class TrendlineSegmentEventConfig:
    breakout_confirm_bars: int = 3
    rebound_confirm_bars: int = 1
    max_resolution_bars: int = 12
    only_final_segments: bool = True
    timeframes: tuple[str, ...] = ("short", "medium", "long")
    regime_filter_medium_short: bool = True


@dataclass(frozen=True)
class TrendlineSegmentStrategyResult:
    events: pd.DataFrame
    strategy_signals: pd.DataFrame
    trades: pd.DataFrame
    nav: pd.DataFrame
    summary: pd.DataFrame


def _line_value_at(seg: pd.Series, bar: int) -> float:
    return float(seg["anchor_price"] + seg["slope"] * (bar - int(seg["anchor_origin"])))


def _strategy_name_for_segment(side: int, strategy: str) -> tuple[str, str]:
    if strategy == "breakout":
        if side == -1:
            return "breakout_long", "long"
        return "breakout_short", "short"
    if strategy == "rebound":
        if side == -1:
            return "rebound_short", "short"
        return "rebound_long", "long"
    raise ValueError(f"Unsupported strategy: {strategy}")


def _required_cols(df: pd.DataFrame, cols: Iterable[str], name: str) -> None:
    missing = set(cols) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in {name}: {sorted(missing)}")


def _higher_timeframe_for(timeframe: str) -> str | None:
    if timeframe == "short":
        return "medium"
    if timeframe == "medium":
        return "long"
    return None


def extract_trendline_segment_strategy_events(
    bars: pd.DataFrame,
    segments: pd.DataFrame,
    *,
    config: TrendlineSegmentEventConfig = TrendlineSegmentEventConfig(),
) -> pd.DataFrame:
    _required_cols(bars, ["timestamp", "open", "close"], "bars")
    _required_cols(
        segments,
        [
            "timeframe",
            "segment_id",
            "start_bar",
            "end_bar",
            "end_reason",
            "side",
            "is_provisional",
            "anchor_origin",
            "anchor_price",
            "pivot_origin",
            "pivot_price",
            "slope",
        ],
        "segments",
    )

    df = bars.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    has_symbol = "symbol" in df.columns
    if not has_symbol:
        df["symbol"] = "ALL"
    df = df.sort_values(["symbol", "timestamp"]).reset_index(drop=True)

    seg = segments.copy()
    if seg.empty:
        return pd.DataFrame(
            columns=[
                "symbol",
                "strategy",
                "event_type",
                "direction",
                "timeframe",
                "segment_id",
                "side",
                "side_label",
                "candidate_bar",
                "candidate_ts",
                "signal_bar",
                "signal_ts",
                "entry_bar",
                "entry_ts",
                "entry_price",
                "confirm_bars",
                "resolution_bars",
                "end_reason",
                "line_value_candidate",
                "line_value_signal",
                "anchor_origin",
                "anchor_timestamp",
                "anchor_price",
                "pivot_origin",
                "pivot_timestamp",
                "pivot_price",
                "computed_timestamp",
                "segment_end_timestamp",
                "segment_is_provisional",
            ]
        )

    if "symbol" not in seg.columns:
        seg["symbol"] = "ALL"
    seg = seg.sort_values(["symbol", "timeframe", "start_bar", "segment_id"]).reset_index(drop=True)

    events: list[dict] = []

    for symbol, g in df.groupby("symbol", sort=True):
        g = g.reset_index(drop=True)
        n = len(g)
        sg = seg[seg["symbol"] == symbol].copy()
        if sg.empty or n < 5:
            continue

        for timeframe in config.timeframes:
            tf_all = sg[sg["timeframe"] == f"tbn_{timeframe}"].copy()
            if tf_all.empty:
                continue
            if config.only_final_segments:
                tf_all = tf_all[tf_all["is_provisional"] == 0].copy()
            if tf_all.empty:
                continue

            tf_all = tf_all.sort_values(["start_bar", "segment_id"]).reset_index(drop=True)
            tf_breakouts = tf_all[tf_all["end_reason"] == "breakout"].copy()
            if tf_breakouts.empty:
                continue

            for _, seg_row in tf_breakouts.iterrows():
                candidate_bar = int(seg_row["end_bar"])
                if candidate_bar >= n - 2:
                    continue

                next_candidates = tf_all[tf_all["start_bar"] > int(seg_row["start_bar"])]
                next_start = int(next_candidates.iloc[0]["start_bar"]) if not next_candidates.empty else n - 1
                monitor_last = min(n - 2, candidate_bar + config.max_resolution_bars, next_start - 1)
                if monitor_last <= candidate_bar:
                    continue

                side = int(seg_row["side"])
                if side not in (-1, 1):
                    continue

                def on_breakout(bar_idx: int) -> bool:
                    lv = _line_value_at(seg_row, bar_idx)
                    c = float(g.loc[bar_idx, "close"])
                    return c > lv if side == -1 else c < lv

                def inside_range(bar_idx: int) -> bool:
                    lv = _line_value_at(seg_row, bar_idx)
                    c = float(g.loc[bar_idx, "close"])
                    return c < lv if side == -1 else c > lv

                breakout_count = 1
                reentry_bar: int | None = None
                inside_count = 0
                resolved = False

                for bar_idx in range(candidate_bar + 1, monitor_last + 1):
                    if reentry_bar is None:
                        if on_breakout(bar_idx):
                            breakout_count += 1
                            if breakout_count >= config.breakout_confirm_bars:
                                event_type, direction = _strategy_name_for_segment(side, "breakout")
                                signal_bar = bar_idx
                                entry_bar = signal_bar + 1
                                if entry_bar >= n:
                                    break
                                events.append(
                                    {
                                        "symbol": symbol,
                                        "strategy": "breakout",
                                        "event_type": event_type,
                                        "direction": direction,
                                        "timeframe": timeframe,
                                        "segment_id": int(seg_row["segment_id"]),
                                        "side": side,
                                        "side_label": str(seg_row["side_label"]),
                                        "candidate_bar": candidate_bar,
                                        "candidate_ts": pd.to_datetime(g.loc[candidate_bar, "timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                        "signal_bar": signal_bar,
                                        "signal_ts": pd.to_datetime(g.loc[signal_bar, "timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                        "entry_bar": entry_bar,
                                        "entry_ts": pd.to_datetime(g.loc[entry_bar, "timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                        "entry_price": float(g.loc[entry_bar, "open"]),
                                        "confirm_bars": int(config.breakout_confirm_bars),
                                        "resolution_bars": int(signal_bar - candidate_bar),
                                        "end_reason": str(seg_row["end_reason"]),
                                        "line_value_candidate": _line_value_at(seg_row, candidate_bar),
                                        "line_value_signal": _line_value_at(seg_row, signal_bar),
                                        "anchor_origin": int(seg_row["anchor_origin"]),
                                        "anchor_timestamp": str(seg_row.get("anchor_timestamp", "")),
                                        "anchor_price": float(seg_row["anchor_price"]),
                                        "pivot_origin": int(seg_row["pivot_origin"]),
                                        "pivot_timestamp": str(seg_row.get("pivot_timestamp", "")),
                                        "pivot_price": float(seg_row["pivot_price"]) if pd.notna(seg_row["pivot_price"]) else np.nan,
                                        "computed_timestamp": str(seg_row.get("start_timestamp", "")),
                                        "segment_end_timestamp": str(seg_row.get("end_timestamp", "")),
                                        "segment_is_provisional": int(seg_row["is_provisional"]),
                                    }
                                )
                                resolved = True
                                break
                        elif inside_range(bar_idx):
                            reentry_bar = bar_idx
                            inside_count = 1
                    else:
                        if inside_range(bar_idx):
                            inside_count += 1
                            if inside_count >= config.rebound_confirm_bars + 1:
                                event_type, direction = _strategy_name_for_segment(side, "rebound")
                                signal_bar = bar_idx
                                entry_bar = signal_bar + 1
                                if entry_bar >= n:
                                    break
                                events.append(
                                    {
                                        "symbol": symbol,
                                        "strategy": "rebound",
                                        "event_type": event_type,
                                        "direction": direction,
                                        "timeframe": timeframe,
                                        "segment_id": int(seg_row["segment_id"]),
                                        "side": side,
                                        "side_label": str(seg_row["side_label"]),
                                        "candidate_bar": candidate_bar,
                                        "candidate_ts": pd.to_datetime(g.loc[candidate_bar, "timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                        "signal_bar": signal_bar,
                                        "signal_ts": pd.to_datetime(g.loc[signal_bar, "timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                        "entry_bar": entry_bar,
                                        "entry_ts": pd.to_datetime(g.loc[entry_bar, "timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                        "entry_price": float(g.loc[entry_bar, "open"]),
                                        "confirm_bars": int(config.rebound_confirm_bars + 1),
                                        "resolution_bars": int(signal_bar - candidate_bar),
                                        "end_reason": str(seg_row["end_reason"]),
                                        "line_value_candidate": _line_value_at(seg_row, candidate_bar),
                                        "line_value_signal": _line_value_at(seg_row, signal_bar),
                                        "anchor_origin": int(seg_row["anchor_origin"]),
                                        "anchor_timestamp": str(seg_row.get("anchor_timestamp", "")),
                                        "anchor_price": float(seg_row["anchor_price"]),
                                        "pivot_origin": int(seg_row["pivot_origin"]),
                                        "pivot_timestamp": str(seg_row.get("pivot_timestamp", "")),
                                        "pivot_price": float(seg_row["pivot_price"]) if pd.notna(seg_row["pivot_price"]) else np.nan,
                                        "computed_timestamp": str(seg_row.get("start_timestamp", "")),
                                        "segment_end_timestamp": str(seg_row.get("end_timestamp", "")),
                                        "segment_is_provisional": int(seg_row["is_provisional"]),
                                    }
                                )
                                resolved = True
                                break
                        else:
                            break

                if not resolved:
                    continue

    events_df = pd.DataFrame(events)
    if not has_symbol and not events_df.empty:
        events_df = events_df.drop(columns=["symbol"])
    return events_df


def build_strategy_signal_table(
    bars: pd.DataFrame,
    events: pd.DataFrame,
    *,
    strategy: str,
    timeframe: str,
    apply_regime_filter: bool = True,
) -> pd.DataFrame:
    _required_cols(bars, ["timestamp", "open", "close"], "bars")
    df = bars.copy()
    df.attrs = {}
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    has_symbol = "symbol" in df.columns
    if not has_symbol:
        df["symbol"] = "ALL"
    df = df.sort_values(["symbol", "timestamp"]).reset_index(drop=True)
    df["long_signal"] = 0
    df["short_signal"] = 0

    if events.empty:
        return df

    ev = events[(events["strategy"] == strategy) & (events["timeframe"] == timeframe)].copy()
    if ev.empty:
        return df

    higher_tf = _higher_timeframe_for(timeframe) if apply_regime_filter else None
    regime_col = f"tbn_trend_{higher_tf}" if higher_tf else None

    for symbol, g in df.groupby("symbol", sort=True):
        mask = ev["symbol"] == symbol if "symbol" in ev.columns else pd.Series(True, index=ev.index)
        es = ev[mask]
        if es.empty:
            continue
        idxs = g.index.to_numpy()
        for _, row in es.iterrows():
            signal_bar = int(row["signal_bar"])
            if signal_bar < 0 or signal_bar >= len(g):
                continue
            global_idx = int(idxs[signal_bar])

            if regime_col and regime_col in df.columns:
                regime_val = int(df.loc[global_idx, regime_col])
                if row["direction"] == "long" and regime_val <= 0:
                    continue
                if row["direction"] == "short" and regime_val >= 0:
                    continue

            if row["direction"] == "long":
                df.loc[global_idx, "long_signal"] = 1
            else:
                df.loc[global_idx, "short_signal"] = 1

    return df


def _attach_event_metadata_to_trades(trades: pd.DataFrame, events: pd.DataFrame, *, strategy: str, timeframe: str) -> pd.DataFrame:
    if trades.empty:
        return trades
    ev = events[(events["strategy"] == strategy) & (events["timeframe"] == timeframe)].copy()
    if ev.empty:
        out = trades.copy()
        out["event_type"] = ""
        out["segment_id"] = np.nan
        out["candidate_ts"] = ""
        out["anchor_timestamp"] = ""
        out["anchor_price"] = np.nan
        out["pivot_timestamp"] = ""
        out["pivot_price"] = np.nan
        out["computed_timestamp"] = ""
        out["signal_bar_index"] = np.nan
        out["entry_bar_index"] = np.nan
        return out

    out = trades.copy()
    out["direction"] = out["side"]
    merge_cols = ["symbol", "signal_ts", "direction"]
    meta_cols = [
        "symbol",
        "signal_ts",
        "direction",
        "event_type",
        "segment_id",
        "candidate_bar",
        "candidate_ts",
        "anchor_timestamp",
        "anchor_origin",
        "anchor_price",
        "pivot_timestamp",
        "pivot_origin",
        "pivot_price",
        "computed_timestamp",
        "segment_end_timestamp",
        "segment_is_provisional",
        "confirm_bars",
        "resolution_bars",
        "end_reason",
        "line_value_candidate",
        "line_value_signal",
        "signal_bar",
        "entry_bar",
        "timeframe",
        "strategy",
        "side_label",
    ]
    merged = out.merge(ev[meta_cols], on=merge_cols, how="left", suffixes=("", "_event"))
    merged = merged.rename(columns={"signal_bar": "signal_bar_index", "entry_bar": "entry_bar_index"})
    return merged


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


def _with_atr(signal_df: pd.DataFrame, period: int) -> pd.DataFrame:
    df = signal_df.copy()
    sort_cols = ["symbol", "timestamp"] if "symbol" in df.columns else ["timestamp"]
    df = df.sort_values(sort_cols).reset_index(drop=True)

    def _per_symbol(g: pd.DataFrame) -> pd.DataFrame:
        g = g.copy()
        prev_close = g["close"].shift(1)
        tr = np.nanmax(
            np.column_stack(
                [
                    (g["high"] - g["low"]).abs().to_numpy(dtype=float),
                    (g["high"] - prev_close).abs().to_numpy(dtype=float),
                    (g["low"] - prev_close).abs().to_numpy(dtype=float),
                ]
            ),
            axis=1,
        )
        g["atr"] = pd.Series(tr, index=g.index).rolling(period, min_periods=period).mean()
        return g

    if "symbol" in df.columns:
        return pd.concat([_per_symbol(g) for _, g in df.groupby("symbol", sort=True)], ignore_index=True)
    return _per_symbol(df)


def _evaluate_segment_signal_table(
    signal_df: pd.DataFrame,
    *,
    config: MultiTfMomentumBacktestConfig = MultiTfMomentumBacktestConfig(),
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    required = {"timestamp", "open", "high", "low", "close", "long_signal", "short_signal"}
    missing = required - set(signal_df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df = signal_df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = _with_atr(df, config.atr_period)

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

        current_pos = 0
        entry_price = None
        entry_ts = None
        entry_j = None
        signal_ts = None
        nav_value = 1.0
        nav_rows.append({"symbol": symbol, "timestamp": g.iloc[0]["timestamp"], "nav": nav_value})

        trail_stop = None
        highest_high = None
        lowest_low = None

        def close_position(*, exit_row: pd.Series, exit_price: float, desired_after: int, exit_reason: str, signal_ts_used):
            nonlocal current_pos, entry_price, entry_ts, entry_j, signal_ts, nav_value, trail_stop, highest_high, lowest_low
            if current_pos == 0 or entry_price is None or entry_ts is None or signal_ts_used is None:
                return
            side = "long" if current_pos == 1 else "short"
            gross_mult, net_mult = _calc_trade_mult(side, float(entry_price), float(exit_price), cost_rate)
            gross_ret = gross_mult - 1.0
            net_ret = net_mult - 1.0
            nav_value *= net_mult
            trades.append(
                {
                    "symbol": symbol,
                    "signal_ts": pd.to_datetime(signal_ts_used, utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "side": side,
                    "entry_ts": pd.to_datetime(entry_ts, utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "exit_ts": pd.to_datetime(exit_row["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "entry_price": float(entry_price),
                    "exit_price": float(exit_price),
                    "gross_ret": gross_ret,
                    "net_ret": net_ret,
                    "hold_bars": int(exit_row.name - entry_j) if entry_j is not None else np.nan,
                    "exit_reason": exit_reason,
                    "win": int(net_ret > 0),
                }
            )
            nav_rows.append({"symbol": symbol, "timestamp": exit_row["timestamp"], "nav": nav_value})
            current_pos = desired_after
            if desired_after == 0:
                entry_price = None
                entry_ts = None
                entry_j = None
                signal_ts = None
                trail_stop = None
                highest_high = None
                lowest_low = None

        for j in range(1, n):
            prev = g.iloc[j - 1]
            row = g.iloc[j]
            exec_price = _safe_float(row["open"])

            if config.enable_atr_trailing_stop and current_pos != 0 and trail_stop is not None:
                if current_pos == 1 and float(row["low"]) <= float(trail_stop):
                    stop_exit = min(exec_price, float(trail_stop)) if math.isfinite(exec_price) and exec_price > 0 else float(trail_stop)
                    close_position(exit_row=row, exit_price=stop_exit, desired_after=0, exit_reason="atr_trailing_stop", signal_ts_used=signal_ts)
                    continue
                if current_pos == -1 and float(row["high"]) >= float(trail_stop):
                    stop_exit = max(exec_price, float(trail_stop)) if math.isfinite(exec_price) and exec_price > 0 else float(trail_stop)
                    close_position(exit_row=row, exit_price=stop_exit, desired_after=0, exit_reason="atr_trailing_stop", signal_ts_used=signal_ts)
                    continue

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
                if current_pos != 0:
                    exit_reason = "reverse_to_long" if desired == 1 else "reverse_to_short" if desired == -1 else "flat"
                    close_position(exit_row=row, exit_price=exec_price, desired_after=0, exit_reason=exit_reason, signal_ts_used=signal_ts)

                if desired != 0:
                    current_pos = desired
                    entry_price = exec_price
                    entry_ts = row["timestamp"]
                    entry_j = j
                    signal_ts = prev["timestamp"]
                    trail_stop = None
                    highest_high = float(row["high"])
                    lowest_low = float(row["low"])

            if current_pos != 0:
                atr = _safe_float(row.get("atr", np.nan))
                if current_pos == 1:
                    highest_high = max(float(highest_high), float(row["high"])) if highest_high is not None else float(row["high"])
                    if config.enable_atr_trailing_stop and math.isfinite(atr) and atr > 0:
                        candidate = float(highest_high) - config.atr_trailing_mult * atr
                        trail_stop = candidate if trail_stop is None else max(float(trail_stop), candidate)
                else:
                    lowest_low = min(float(lowest_low), float(row["low"])) if lowest_low is not None else float(row["low"])
                    if config.enable_atr_trailing_stop and math.isfinite(atr) and atr > 0:
                        candidate = float(lowest_low) + config.atr_trailing_mult * atr
                        trail_stop = candidate if trail_stop is None else min(float(trail_stop), candidate)

        if current_pos != 0 and entry_price is not None and entry_ts is not None and signal_ts is not None:
            final_row = g.iloc[-1]
            exit_price = _safe_float(final_row["close"])
            if math.isfinite(exit_price) and exit_price > 0:
                close_position(exit_row=final_row, exit_price=exit_price, desired_after=0, exit_reason="force_close_final_bar", signal_ts_used=signal_ts)

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

    return pd.DataFrame(trades), pd.DataFrame(nav_rows), pd.DataFrame(summary_rows)


def evaluate_trendline_segment_strategy(
    bars: pd.DataFrame,
    segments: pd.DataFrame,
    *,
    event_config: TrendlineSegmentEventConfig = TrendlineSegmentEventConfig(),
    backtest_config: MultiTfMomentumBacktestConfig = MultiTfMomentumBacktestConfig(),
) -> TrendlineSegmentStrategyResult:
    events = extract_trendline_segment_strategy_events(bars, segments, config=event_config)

    signal_tables: list[pd.DataFrame] = []
    trade_tables: list[pd.DataFrame] = []
    nav_tables: list[pd.DataFrame] = []
    summary_tables: list[pd.DataFrame] = []

    for timeframe in event_config.timeframes:
        for strategy in ("breakout", "rebound"):
            apply_regime = bool(event_config.regime_filter_medium_short and timeframe in {"short", "medium"})
            sig = build_strategy_signal_table(
                bars,
                events,
                strategy=strategy,
                timeframe=timeframe,
                apply_regime_filter=apply_regime,
            )
            trades_df, nav_df, summary_df = _evaluate_segment_signal_table(sig, config=backtest_config)
            sig = sig.copy()
            sig.attrs = {}
            sig["strategy"] = strategy
            sig["timeframe"] = timeframe
            signal_tables.append(sig)

            if not trades_df.empty:
                t = trades_df.copy()
                t.attrs = {}
                t["strategy"] = strategy
                t["timeframe"] = timeframe
                t = _attach_event_metadata_to_trades(t, events, strategy=strategy, timeframe=timeframe)
                t.attrs = {}
                trade_tables.append(t)
            if not nav_df.empty:
                n = nav_df.copy()
                n.attrs = {}
                n["strategy"] = strategy
                n["timeframe"] = timeframe
                nav_tables.append(n)
            if not summary_df.empty:
                s = summary_df.copy()
                s.attrs = {}
                s["strategy"] = strategy
                s["timeframe"] = timeframe
                summary_tables.append(s)
            else:
                summary_tables.append(
                    pd.DataFrame(
                        [
                            {
                                "symbol": sig["symbol"].iloc[0] if "symbol" in sig.columns else "ALL",
                                "trades": 0,
                                "win_rate": np.nan,
                                "avg_ret": np.nan,
                                "median_ret": np.nan,
                                "total_return": 0.0,
                                "max_drawdown": 0.0,
                                "long_trades": 0,
                                "short_trades": 0,
                                "strategy": strategy,
                                "timeframe": timeframe,
                            }
                        ]
                    )
                )

    return TrendlineSegmentStrategyResult(
        events=events,
        strategy_signals=pd.concat(signal_tables, ignore_index=True) if signal_tables else pd.DataFrame(),
        trades=pd.concat(trade_tables, ignore_index=True) if trade_tables else pd.DataFrame(),
        nav=pd.concat(nav_tables, ignore_index=True) if nav_tables else pd.DataFrame(),
        summary=pd.concat(summary_tables, ignore_index=True) if summary_tables else pd.DataFrame(),
    )


__all__ = [
    "TrendlineSegmentEventConfig",
    "TrendlineSegmentStrategyResult",
    "extract_trendline_segment_strategy_events",
    "build_strategy_signal_table",
    "evaluate_trendline_segment_strategy",
]
