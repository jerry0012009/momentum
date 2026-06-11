#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVENTS_PATH = ROOT / "reports" / "artifacts" / "pytrendline_event_validation_v3" / "event_sample_purged.csv"
CACHE_DIR = ROOT / "reports" / "artifacts" / "pytrendline_event_validation_v3" / "cache"
CACHE_PERIOD = "45d"

V0_ART_DIR = ROOT / "reports" / "artifacts" / "support_breakout_v0_h24"
V0_SITE_DIR = ROOT / "reports" / "site" / "factors" / "support_breakout_v0_h24"
AB_ART_DIR = ROOT / "reports" / "artifacts" / "support_breakout_v0_fib_ab"
AB_SITE_DIR = ROOT / "reports" / "site" / "factors" / "support_breakout_v0_fib_ab"
REGIME_POLICY_ART_DIR = ROOT / "reports" / "artifacts" / "pytrendline_event_validation_v3_regime_policy_slice_v1"
REGIME_POLICY_OOS_PATH = REGIME_POLICY_ART_DIR / "support_breakout_raw_regime_policy_oos.csv"

HOLD_BARS = 24
SWING_LOOKBACK = 48
MAX_RETEST_WAIT = 36


@dataclass
class StrategyResult:
    name: str
    trades: pd.DataFrame
    summary: pd.DataFrame
    by_asset: pd.DataFrame
    by_split: pd.DataFrame
    by_regime: pd.DataFrame


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def pct(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def num(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}"


def int_str(v: float | int | None, default: str = "0") -> str:
    if v is None or pd.isna(v):
        return default
    try:
        return str(int(float(v)))
    except (TypeError, ValueError):
        return default


def short_return_from_long(long_ret: float) -> float:
    return -float(long_ret) / (1.0 + float(long_ret))


def classify_regime(pre_ret: float | None) -> str:
    if pre_ret is None or pd.isna(pre_ret):
        return "unknown"
    if pre_ret >= 0.02:
        return "up"
    if pre_ret <= -0.02:
        return "down"
    return "flat"


def compute_drawdown(rets: pd.Series) -> float:
    if rets.empty:
        return 0.0
    equity = (1.0 + rets.astype(float)).cumprod()
    peak = equity.cummax()
    dd = equity / peak - 1.0
    return float(dd.min())


def with_splits(df: pd.DataFrame, *, time_col: str) -> pd.DataFrame:
    out = df.sort_values(time_col).reset_index(drop=True).copy()
    if out.empty:
        out["split"] = []
        return out
    n = len(out)
    ranks = np.arange(n)
    train_cut = max(1, int(np.floor(n * 0.6)))
    validate_cut = max(train_cut + 1, int(np.floor(n * 0.8)))
    split = np.where(ranks < train_cut, "train", np.where(ranks < validate_cut, "validate", "test"))
    out["split"] = split
    return out


def summarize_trades(df: pd.DataFrame, *, name: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if df.empty:
        base = pd.DataFrame(
            [
                {
                    "strategy": name,
                    "trades": 0,
                    "assets": 0,
                    "mean_return": np.nan,
                    "median_return": np.nan,
                    "win_ratio": np.nan,
                    "cumulative_return": np.nan,
                    "max_drawdown": np.nan,
                    "avg_entry_delay_bars": np.nan,
                }
            ]
        )
        return base, pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    summary = pd.DataFrame(
        [
            {
                "strategy": name,
                "trades": int(len(df)),
                "assets": int(df["symbol"].nunique()),
                "mean_return": float(df["trade_return"].mean()),
                "median_return": float(df["trade_return"].median()),
                "win_ratio": float((df["trade_return"] > 0).mean()),
                "cumulative_return": float((1.0 + df["trade_return"]).prod() - 1.0),
                "max_drawdown": compute_drawdown(df["trade_return"]),
                "avg_entry_delay_bars": float(df["entry_delay_bars"].mean()),
            }
        ]
    )

    by_asset = (
        df.groupby("symbol", dropna=False)
        .agg(
            trades=("trade_return", "size"),
            mean_return=("trade_return", "mean"),
            median_return=("trade_return", "median"),
            win_ratio=("trade_return", lambda s: float((s > 0).mean())),
            cumulative_return=("trade_return", lambda s: float((1.0 + s).prod() - 1.0)),
            max_drawdown=("trade_return", lambda s: compute_drawdown(pd.Series(s))),
            avg_entry_delay_bars=("entry_delay_bars", "mean"),
        )
        .reset_index()
        .sort_values("symbol")
    )
    by_asset.insert(0, "strategy", name)

    by_split = (
        df.groupby("split", dropna=False)
        .agg(
            trades=("trade_return", "size"),
            mean_return=("trade_return", "mean"),
            median_return=("trade_return", "median"),
            win_ratio=("trade_return", lambda s: float((s > 0).mean())),
            cumulative_return=("trade_return", lambda s: float((1.0 + s).prod() - 1.0)),
            max_drawdown=("trade_return", lambda s: compute_drawdown(pd.Series(s))),
            avg_entry_delay_bars=("entry_delay_bars", "mean"),
        )
        .reset_index()
    )
    by_split.insert(0, "strategy", name)

    by_regime = (
        df.groupby("regime", dropna=False)
        .agg(
            trades=("trade_return", "size"),
            mean_return=("trade_return", "mean"),
            median_return=("trade_return", "median"),
            win_ratio=("trade_return", lambda s: float((s > 0).mean())),
            cumulative_return=("trade_return", lambda s: float((1.0 + s).prod() - 1.0)),
            max_drawdown=("trade_return", lambda s: compute_drawdown(pd.Series(s))),
            avg_entry_delay_bars=("entry_delay_bars", "mean"),
        )
        .reset_index()
    )
    by_regime.insert(0, "strategy", name)
    return summary, by_asset, by_split, by_regime


def load_inputs() -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    events = pd.read_csv(
        EVENTS_PATH,
        parse_dates=["event_timestamp", "confirm_timestamp", "action_timestamp", "snapshot_asof_timestamp"],
    )
    events = events[events["event_type"].isin(["support_breakout_raw", "support_breakout_confirm_1"])].copy()

    bars_by_symbol: dict[str, pd.DataFrame] = {}
    for symbol in sorted(events["symbol"].unique()):
        cache_path = CACHE_DIR / f"{symbol.replace('-', '_')}__{CACHE_PERIOD}__60m.csv"
        bars = pd.read_csv(cache_path, parse_dates=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
        bars_by_symbol[symbol] = bars
    return events, bars_by_symbol


def attach_confirm_trend_regime(events: pd.DataFrame, bars_by_symbol: dict[str, pd.DataFrame]) -> pd.DataFrame:
    out = events.copy()
    if out.empty:
        out["confirm_trend_regime"] = []
        out["trend_policy"] = []
        return out

    regimes: list[str] = []
    policies: list[str] = []
    for _, row in out.iterrows():
        symbol = row["symbol"]
        bars = bars_by_symbol[symbol]
        ts = pd.to_datetime(bars["timestamp"], utc=True)
        ts_to_idx = {stamp: idx for idx, stamp in enumerate(ts)}
        confirm_ts = pd.to_datetime(row["confirm_timestamp"], utc=True)
        confirm_idx = ts_to_idx.get(confirm_ts)
        if confirm_idx is None or confirm_idx < 24:
            regime = "unknown"
        else:
            close = bars["close"].astype(float)
            ema50 = close.ewm(span=50, adjust=False).mean()
            ema200 = close.ewm(span=200, adjust=False).mean()
            slope24 = float(ema50.iloc[confirm_idx] - ema50.iloc[confirm_idx - 24])
            if float(ema50.iloc[confirm_idx]) > float(ema200.iloc[confirm_idx]) and slope24 > 0:
                regime = "uptrend"
            elif float(ema50.iloc[confirm_idx]) < float(ema200.iloc[confirm_idx]) and slope24 < 0:
                regime = "downtrend"
            else:
                regime = "fluctuating"
        regimes.append(regime)
        policies.append("avoid_fluctuating" if regime != "fluctuating" else "drop_fluctuating")
    out["confirm_trend_regime"] = regimes
    out["trend_policy"] = policies
    return out


def build_simple_breakout_trades(
    events: pd.DataFrame,
    bars_by_symbol: dict[str, pd.DataFrame],
    *,
    event_type: str,
    strategy_name: str,
    setup_label: str,
) -> pd.DataFrame:
    scoped = events[events["event_type"].eq(event_type)].copy()
    if "split" not in scoped.columns:
        scoped = with_splits(scoped, time_col="action_timestamp")
    rows: list[dict] = []
    for symbol, group in scoped.sort_values("action_timestamp").groupby("symbol", sort=False):
        bars = bars_by_symbol[symbol]
        ts_to_idx = {ts: idx for idx, ts in enumerate(bars["timestamp"])}
        last_exit_index = -10**9
        for _, event in group.sort_values("action_index").iterrows():
            action_index = ts_to_idx.get(event["action_timestamp"])
            if action_index is None:
                continue
            exit_index = action_index + HOLD_BARS
            if action_index <= last_exit_index or exit_index >= len(bars):
                continue
            entry_open = float(event["action_open"])
            long_ret = float(event["fwd_ret_h24"])
            trade_ret = short_return_from_long(long_ret)
            exit_close = entry_open * (1.0 + long_ret)
            pre_idx = action_index - HOLD_BARS
            pre_ret = np.nan if pre_idx < 0 else float(bars.iloc[action_index - 1]["close"] / bars.iloc[pre_idx]["close"] - 1.0)
            rows.append(
                {
                    "strategy": strategy_name,
                    "symbol": symbol,
                    "source_event_timestamp": event["event_timestamp"],
                    "action_timestamp": event["action_timestamp"],
                    "entry_timestamp": event["action_timestamp"],
                    "exit_timestamp": bars.iloc[exit_index]["timestamp"],
                    "event_index": int(event["event_index"]),
                    "action_index": action_index,
                    "entry_index": action_index,
                    "exit_index": exit_index,
                    "entry_delay_bars": 0,
                    "split": event["split"],
                    "regime": classify_regime(pre_ret),
                    "pre_24bar_return": pre_ret,
                    "event_line_score": float(event["line_score"]),
                    "entry_open": entry_open,
                    "exit_close": exit_close,
                    "trade_return": trade_ret,
                    "benchmark_long_return": long_ret,
                    "setup_label": setup_label,
                    "fib38": np.nan,
                    "fib50": np.nan,
                    "swing_high": np.nan,
                    "swing_low": np.nan,
                }
            )
            last_exit_index = exit_index
    return pd.DataFrame(rows).sort_values(["entry_timestamp", "symbol"]).reset_index(drop=True)


def build_v0_trades(events: pd.DataFrame, bars_by_symbol: dict[str, pd.DataFrame]) -> pd.DataFrame:
    return build_simple_breakout_trades(
        events,
        bars_by_symbol,
        event_type="support_breakout_raw",
        strategy_name="v0_breakout",
        setup_label="break_on_action_open",
    )


def build_confirm1_trades(events: pd.DataFrame, bars_by_symbol: dict[str, pd.DataFrame]) -> pd.DataFrame:
    return build_simple_breakout_trades(
        events,
        bars_by_symbol,
        event_type="support_breakout_confirm_1",
        strategy_name="breakout_confirm_1",
        setup_label="confirm_1_on_action_open",
    )


def derive_short_swing(bars: pd.DataFrame, event_index: int, lookback: int) -> tuple[float, float, float, float] | None:
    start = max(0, event_index - lookback + 1)
    window = bars.iloc[start : event_index + 1].copy()
    if window.empty:
        return None
    high_idx = int(window["high"].idxmax())
    downswing = bars.iloc[high_idx : event_index + 1].copy()
    if downswing.empty:
        return None
    swing_high = float(bars.loc[high_idx, "high"])
    swing_low = float(downswing["low"].min())
    if swing_high <= swing_low:
        return None
    fib38 = swing_low + 0.382 * (swing_high - swing_low)
    fib50 = swing_low + 0.5 * (swing_high - swing_low)
    return swing_high, swing_low, fib38, fib50


def build_fib_trades(events: pd.DataFrame, bars_by_symbol: dict[str, pd.DataFrame]) -> pd.DataFrame:
    scoped = events[events["event_type"].eq("support_breakout_raw")].copy()
    scoped = with_splits(scoped, time_col="action_timestamp")
    rows: list[dict] = []
    for symbol, group in scoped.sort_values("action_timestamp").groupby("symbol", sort=False):
        bars = bars_by_symbol[symbol]
        ts_to_idx = {ts: idx for idx, ts in enumerate(bars["timestamp"])}
        last_exit_index = -10**9
        for _, event in group.sort_values("action_index").iterrows():
            action_index = ts_to_idx.get(event["action_timestamp"])
            event_index = ts_to_idx.get(event["event_timestamp"])
            if action_index is None or event_index is None:
                continue
            swing = derive_short_swing(bars, event_index, SWING_LOOKBACK)
            if swing is None:
                continue
            swing_high, swing_low, fib38, fib50 = swing
            zone_low = min(fib38, fib50)
            zone_high = max(fib38, fib50)
            entry_index = None
            for bar_index in range(action_index + 1, min(action_index + 1 + MAX_RETEST_WAIT, len(bars) - HOLD_BARS - 1)):
                row = bars.iloc[bar_index]
                overlaps = float(row["low"]) <= zone_high and float(row["high"]) >= zone_low
                reclaimed_lower = float(row["close"]) < fib38
                if overlaps and reclaimed_lower:
                    entry_index = bar_index + 1
                    break
            if entry_index is None:
                continue
            exit_index = entry_index + HOLD_BARS
            if entry_index <= last_exit_index or exit_index >= len(bars):
                continue
            entry_open = float(bars.iloc[entry_index]["open"])
            exit_close = float(bars.iloc[exit_index]["close"])
            long_ret = exit_close / entry_open - 1.0
            trade_ret = short_return_from_long(long_ret)
            pre_idx = entry_index - HOLD_BARS
            pre_ret = np.nan if pre_idx < 0 else float(bars.iloc[entry_index - 1]["close"] / bars.iloc[pre_idx]["close"] - 1.0)
            rows.append(
                {
                    "strategy": "breakout_plus_fib_retest_hold",
                    "symbol": symbol,
                    "source_event_timestamp": event["event_timestamp"],
                    "action_timestamp": event["action_timestamp"],
                    "entry_timestamp": bars.iloc[entry_index]["timestamp"],
                    "exit_timestamp": bars.iloc[exit_index]["timestamp"],
                    "event_index": event_index,
                    "action_index": action_index,
                    "entry_index": entry_index,
                    "exit_index": exit_index,
                    "entry_delay_bars": int(entry_index - action_index),
                    "split": event["split"],
                    "regime": classify_regime(pre_ret),
                    "pre_24bar_return": pre_ret,
                    "event_line_score": float(event["line_score"]),
                    "entry_open": entry_open,
                    "exit_close": exit_close,
                    "trade_return": trade_ret,
                    "benchmark_long_return": long_ret,
                    "setup_label": "retest_hold_after_breakout",
                    "fib38": fib38,
                    "fib50": fib50,
                    "swing_high": swing_high,
                    "swing_low": swing_low,
                }
            )
            last_exit_index = exit_index
    return pd.DataFrame(rows).sort_values(["entry_timestamp", "symbol"]).reset_index(drop=True)


def save_plot(trades_a: pd.DataFrame, trades_b: pd.DataFrame, out_path: Path) -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    for label, trades, color in [
        ("Breakout v0", trades_a, "#0f766e"),
        ("Breakout + Fib", trades_b, "#b45309"),
    ]:
        if trades.empty:
            continue
        equity = (1.0 + trades["trade_return"].astype(float)).cumprod()
        ax.plot(np.arange(1, len(equity) + 1), equity, label=label, linewidth=2.1, color=color)
    ax.axhline(1.0, color="#6b7280", linewidth=1, linestyle="--")
    ax.set_title("Equity Curve by Trade Order")
    ax.set_xlabel("Trade #")
    ax.set_ylabel("Equity")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def save_asset_plot(by_asset: pd.DataFrame, out_path: Path) -> None:
    if by_asset.empty:
        return
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    pivot = by_asset.pivot(index="symbol", columns="strategy", values="mean_return").fillna(0.0)
    x = np.arange(len(pivot.index))
    width = 0.34
    strategies = list(pivot.columns)
    colors = ["#0f766e", "#b45309"]
    for i, strategy in enumerate(strategies):
        ax.bar(x + (i - (len(strategies) - 1) / 2) * width, pivot[strategy].values, width=width, label=strategy, color=colors[i % len(colors)])
    ax.axhline(0.0, color="#374151", linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels(pivot.index)
    ax.set_ylabel("Mean trade return")
    ax.set_title("Mean Trade Return by Asset")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def html_table(df: pd.DataFrame, *, percent_cols: set[str] | None = None, float_cols: set[str] | None = None) -> str:
    percent_cols = percent_cols or set()
    float_cols = float_cols or set()
    if df.empty:
        return "<p class='muted'>无数据。</p>"
    head = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        tds = []
        for col in df.columns:
            val = row[col]
            if col in percent_cols:
                text = pct(val)
            elif col in float_cols:
                text = num(val)
            elif isinstance(val, pd.Timestamp):
                text = str(val)
            else:
                text = str(val)
            tds.append(f"<td>{escape(text)}</td>")
        rows.append("<tr>" + "".join(tds) + "</tr>")
    return "<table><thead><tr>" + head + "</tr></thead><tbody>" + "".join(rows) + "</tbody></table>"


def cost_sensitivity_table(trades: pd.DataFrame, *, cost_bps_list: list[int]) -> pd.DataFrame:
    rows: list[dict] = []
    if trades.empty:
        return pd.DataFrame(columns=["cost_bps", "trades", "mean_net_return", "median_net_return", "win_ratio", "cumulative_net_return"])
    for cost_bps in cost_bps_list:
        net = trades["trade_return"].astype(float) - (cost_bps / 10000.0)
        rows.append(
            {
                "cost_bps": int(cost_bps),
                "trades": int(len(net)),
                "mean_net_return": float(net.mean()),
                "median_net_return": float(net.median()),
                "win_ratio": float((net > 0).mean()),
                "cumulative_net_return": float((1.0 + net).prod() - 1.0),
            }
        )
    return pd.DataFrame(rows)


def context_net_table(trades: pd.DataFrame, *, group_col: str, cost_bps: int) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=[group_col, "trades", "mean_net_return", "median_net_return", "win_ratio", "cumulative_net_return"])
    df = trades.copy()
    df["net_return"] = df["trade_return"].astype(float) - (cost_bps / 10000.0)
    out = (
        df.groupby(group_col, dropna=False)
        .agg(
            trades=("net_return", "size"),
            mean_net_return=("net_return", "mean"),
            median_net_return=("net_return", "median"),
            win_ratio=("net_return", lambda s: float((s > 0).mean())),
            cumulative_net_return=("net_return", lambda s: float((1.0 + s).prod() - 1.0)),
        )
        .reset_index()
    )
    return out


def overlap_summary_table(trades: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    summary_cols = [
        "trades",
        "assets",
        "max_concurrent_positions",
        "mean_concurrent_at_entry",
        "share_entries_ge2",
        "share_entries_ge3",
        "share_active_hours_ge2",
        "share_active_hours_ge3",
        "share_active_hours_ge4",
    ]
    profile_cols = ["concurrent_positions", "hours", "share_active_hours"]
    if trades.empty:
        return pd.DataFrame(columns=summary_cols), pd.DataFrame(columns=profile_cols)

    df = trades.copy()
    df["entry_timestamp"] = pd.to_datetime(df["entry_timestamp"], utc=True)
    df["exit_timestamp"] = pd.to_datetime(df["exit_timestamp"], utc=True)

    timeline: list[tuple[pd.Timestamp, int]] = []
    for _, row in df.iterrows():
        timeline.append((row["entry_timestamp"], 1))
        timeline.append((row["exit_timestamp"], -1))
    timeline.sort(key=lambda x: (x[0], x[1]))

    active = 0
    last_ts: pd.Timestamp | None = None
    periods: list[tuple[pd.Timestamp, pd.Timestamp, int]] = []
    for ts, delta in timeline:
        if last_ts is not None and ts > last_ts:
            periods.append((last_ts, ts, active))
        active += delta
        last_ts = ts

    profile_rows: list[dict] = []
    active_hours_total = 0.0
    for concurrent in sorted({p[2] for p in periods if p[2] > 0}):
        hours = sum((end - start).total_seconds() / 3600.0 for start, end, c in periods if c == concurrent)
        active_hours_total += hours
        profile_rows.append({
            "concurrent_positions": int(concurrent),
            "hours": float(hours),
        })
    profile = pd.DataFrame(profile_rows)
    if not profile.empty:
        profile["share_active_hours"] = profile["hours"] / active_hours_total if active_hours_total > 0 else np.nan

    concurrent_at_entry = []
    for _, row in df.sort_values("entry_timestamp").iterrows():
        t = row["entry_timestamp"]
        already_open = ((df["entry_timestamp"] < t) & (df["exit_timestamp"] > t)).sum()
        concurrent_at_entry.append(int(already_open) + 1)
    concurrent_at_entry_s = pd.Series(concurrent_at_entry, dtype=float)

    def share_active_ge(threshold: int) -> float:
        if profile.empty or active_hours_total <= 0:
            return np.nan
        return float(profile.loc[profile["concurrent_positions"] >= threshold, "hours"].sum() / active_hours_total)

    summary = pd.DataFrame(
        [
            {
                "trades": int(len(df)),
                "assets": int(df["symbol"].nunique()),
                "max_concurrent_positions": int(max(concurrent_at_entry_s.max(), profile["concurrent_positions"].max() if not profile.empty else 1)),
                "mean_concurrent_at_entry": float(concurrent_at_entry_s.mean()),
                "share_entries_ge2": float((concurrent_at_entry_s >= 2).mean()),
                "share_entries_ge3": float((concurrent_at_entry_s >= 3).mean()),
                "share_active_hours_ge2": share_active_ge(2),
                "share_active_hours_ge3": share_active_ge(3),
                "share_active_hours_ge4": share_active_ge(4),
            }
        ]
    )
    return summary, profile


def capital_allocation_first_pass(trades: pd.DataFrame, *, cost_bps_list: list[int]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    summary_cols = [
        "mode",
        "cost_bps",
        "trades",
        "trade_keep_ratio_vs_independent",
        "skipped_due_to_overlap",
        "mean_effective_weight",
        "mean_net_return",
        "median_net_return",
        "win_ratio",
        "cumulative_net_return",
    ]
    selected_cols = [
        "symbol",
        "entry_timestamp",
        "exit_timestamp",
        "split",
        "regime",
        "trade_return",
    ]
    equal_weight_cols = [
        "symbol",
        "entry_timestamp",
        "exit_timestamp",
        "split",
        "regime",
        "entry_concurrent_positions",
        "effective_weight",
        "trade_return",
    ]
    if trades.empty:
        return (
            pd.DataFrame(columns=summary_cols),
            pd.DataFrame(columns=selected_cols),
            pd.DataFrame(columns=equal_weight_cols),
        )

    df = trades.copy().sort_values(["entry_timestamp", "symbol"]).reset_index(drop=True)
    df["entry_timestamp"] = pd.to_datetime(df["entry_timestamp"], utc=True)
    df["exit_timestamp"] = pd.to_datetime(df["exit_timestamp"], utc=True)

    entry_concurrent_positions = []
    for ts in df["entry_timestamp"]:
        concurrent = int(((df["entry_timestamp"] <= ts) & (df["exit_timestamp"] > ts)).sum())
        entry_concurrent_positions.append(max(concurrent, 1))
    equal_weight_detail = df[equal_weight_cols[:5] + ["trade_return"]].copy()
    equal_weight_detail["entry_concurrent_positions"] = entry_concurrent_positions
    equal_weight_detail["effective_weight"] = 1.0 / equal_weight_detail["entry_concurrent_positions"].astype(float)
    equal_weight_detail = equal_weight_detail[equal_weight_cols]

    selected_rows: list[dict] = []
    current_exit: pd.Timestamp | None = None
    for row in df.to_dict("records"):
        if current_exit is None or row["entry_timestamp"] >= current_exit:
            selected_rows.append(row)
            current_exit = row["exit_timestamp"]
    global_1slot = pd.DataFrame(selected_rows)

    total = len(df)
    summaries: list[dict] = []
    mode_frames = [
        ("per_asset_independent", df, pd.Series(1.0, index=df.index, dtype=float)),
        ("equal_weight_concurrent_entry", equal_weight_detail, equal_weight_detail["effective_weight"].astype(float)),
        ("1_slot_global", global_1slot, pd.Series(1.0, index=global_1slot.index, dtype=float)),
    ]
    for mode, sub, weights in mode_frames:
        keep_ratio = float(len(sub) / total) if total > 0 else np.nan
        skipped = int(total - len(sub))
        for cost_bps in cost_bps_list:
            base = sub["trade_return"].astype(float) - (cost_bps / 10000.0)
            net = base * weights.astype(float)
            summaries.append(
                {
                    "mode": mode,
                    "cost_bps": int(cost_bps),
                    "trades": int(len(sub)),
                    "trade_keep_ratio_vs_independent": keep_ratio,
                    "skipped_due_to_overlap": skipped,
                    "mean_effective_weight": float(weights.mean()) if len(sub) else np.nan,
                    "mean_net_return": float(net.mean()) if len(sub) else np.nan,
                    "median_net_return": float(net.median()) if len(sub) else np.nan,
                    "win_ratio": float((net > 0).mean()) if len(sub) else np.nan,
                    "cumulative_net_return": float((1.0 + net).prod() - 1.0) if len(sub) else np.nan,
                }
            )

    selected_display = global_1slot[selected_cols].copy() if not global_1slot.empty else pd.DataFrame(columns=selected_cols)
    return pd.DataFrame(summaries), selected_display, equal_weight_detail


def breakout_honesty_snapshot(
    trades: pd.DataFrame,
    *,
    label: str,
    bars_by_symbol: dict[str, pd.DataFrame] | None = None,
) -> pd.DataFrame:
    cols = [
        "strategy",
        "trades",
        "gross_cumulative_return",
        "cost20_cumulative_return",
        "test_cost20_cumulative_return",
        "up_cost20_cumulative_return",
        "equal_weight_cost20_cumulative_return",
        "equal_weight_mean_effective_weight",
        "hourly_path_cost20_cumulative_return",
        "hourly_path_max_drawdown",
        "slot1_cost20_cumulative_return",
        "slot1_trade_keep_ratio",
    ]
    if trades.empty:
        return pd.DataFrame(columns=cols)

    cost20 = cost_sensitivity_table(trades, cost_bps_list=[20])
    split20 = context_net_table(trades, group_col="split", cost_bps=20)
    regime20 = context_net_table(trades, group_col="regime", cost_bps=20)
    capital20, _, _ = capital_allocation_first_pass(trades, cost_bps_list=[20])
    hourly20_summary = pd.DataFrame()
    if bars_by_symbol is not None:
        hourly20_path = build_equal_weight_hourly_portfolio_path(trades, bars_by_symbol, cost_bps=20)
        hourly20_summary = summarize_hourly_portfolio_path(hourly20_path, mode=f"{label}_hourly", cost_bps=20)
    split_map = split20.set_index("split").to_dict("index") if not split20.empty else {}
    regime_map = regime20.set_index("regime").to_dict("index") if not regime20.empty else {}
    capital_map = {(row["mode"], int(row["cost_bps"])): row for _, row in capital20.iterrows()} if not capital20.empty else {}
    eq20 = capital_map.get(("equal_weight_concurrent_entry", 20), {})
    slot20 = capital_map.get(("1_slot_global", 20), {})
    overall20 = cost20.iloc[0] if not cost20.empty else {}
    hourly20 = hourly20_summary.iloc[0] if not hourly20_summary.empty else {}
    return pd.DataFrame([
        {
            "strategy": label,
            "trades": int(len(trades)),
            "gross_cumulative_return": float((1.0 + trades["trade_return"].astype(float)).prod() - 1.0),
            "cost20_cumulative_return": overall20.get("cumulative_net_return", np.nan),
            "test_cost20_cumulative_return": split_map.get("test", {}).get("cumulative_net_return", np.nan),
            "up_cost20_cumulative_return": regime_map.get("up", {}).get("cumulative_net_return", np.nan),
            "equal_weight_cost20_cumulative_return": eq20.get("cumulative_net_return", np.nan),
            "equal_weight_mean_effective_weight": eq20.get("mean_effective_weight", np.nan),
            "hourly_path_cost20_cumulative_return": hourly20.get("cumulative_net_return", np.nan),
            "hourly_path_max_drawdown": hourly20.get("max_drawdown", np.nan),
            "slot1_cost20_cumulative_return": slot20.get("cumulative_net_return", np.nan),
            "slot1_trade_keep_ratio": slot20.get("trade_keep_ratio_vs_independent", np.nan),
        }
    ], columns=cols)


def breakout_gate_hourly_snapshot(
    trades: pd.DataFrame,
    bars_by_symbol: dict[str, pd.DataFrame],
    *,
    label: str,
) -> pd.DataFrame:
    cols = [
        "strategy",
        "trades",
        "trade_retention_vs_raw",
        "per_asset_cost20_cumulative_return",
        "hourly_path_cost20_cumulative_return",
        "hourly_path_max_drawdown",
        "test_hourly_path_cost20_cumulative_return",
        "up_hourly_path_cost20_cumulative_return",
        "flat_hourly_path_cost20_cumulative_return",
        "mean_active_positions",
    ]
    if trades.empty:
        return pd.DataFrame(columns=cols)

    per_asset20 = cost_sensitivity_table(trades, cost_bps_list=[20])
    hourly20 = build_equal_weight_hourly_portfolio_path(trades, bars_by_symbol, cost_bps=20)
    hourly20_summary = summarize_hourly_portfolio_path(hourly20, mode=f"{label}_hourly", cost_bps=20)
    hourly_split20 = summarize_hourly_portfolio_groups(trades, bars_by_symbol, group_col="split", cost_bps=20)
    hourly_regime20 = summarize_hourly_portfolio_groups(trades, bars_by_symbol, group_col="regime", cost_bps=20)
    split_map = hourly_split20.set_index("split").to_dict("index") if not hourly_split20.empty else {}
    regime_map = hourly_regime20.set_index("regime").to_dict("index") if not hourly_regime20.empty else {}
    overall20 = per_asset20.iloc[0] if not per_asset20.empty else {}
    hourly_row = hourly20_summary.iloc[0] if not hourly20_summary.empty else {}
    return pd.DataFrame([
        {
            "strategy": label,
            "trades": int(len(trades)),
            "trade_retention_vs_raw": np.nan,
            "per_asset_cost20_cumulative_return": overall20.get("cumulative_net_return", np.nan),
            "hourly_path_cost20_cumulative_return": hourly_row.get("cumulative_net_return", np.nan),
            "hourly_path_max_drawdown": hourly_row.get("max_drawdown", np.nan),
            "test_hourly_path_cost20_cumulative_return": split_map.get("test", {}).get("cumulative_net_return", np.nan),
            "up_hourly_path_cost20_cumulative_return": regime_map.get("up", {}).get("cumulative_net_return", np.nan),
            "flat_hourly_path_cost20_cumulative_return": regime_map.get("flat", {}).get("cumulative_net_return", np.nan),
            "mean_active_positions": hourly_row.get("mean_active_positions", np.nan),
        }
    ], columns=cols)


def build_equal_weight_hourly_portfolio_path(
    trades: pd.DataFrame,
    bars_by_symbol: dict[str, pd.DataFrame],
    *,
    cost_bps: int,
) -> pd.DataFrame:
    cols = ["timestamp", "portfolio_ret", "active_positions", "equity"]
    if trades.empty:
        return pd.DataFrame(columns=cols)

    step_rows: list[dict] = []
    half_cost = cost_bps / 20000.0
    for trade_id, row in trades.sort_values(["entry_timestamp", "symbol"]).reset_index(drop=True).iterrows():
        symbol = row["symbol"]
        bars = bars_by_symbol[symbol]
        ts_to_idx = {ts: idx for idx, ts in enumerate(pd.to_datetime(bars["timestamp"], utc=True))}
        entry_ts = pd.to_datetime(row["entry_timestamp"], utc=True)
        exit_ts = pd.to_datetime(row["exit_timestamp"], utc=True)
        entry_idx = ts_to_idx.get(entry_ts)
        exit_idx = ts_to_idx.get(exit_ts)
        if entry_idx is None or exit_idx is None or exit_idx < entry_idx:
            continue

        first_long_ret = float(bars.iloc[entry_idx]["close"] / bars.iloc[entry_idx]["open"] - 1.0)
        step_rows.append(
            {
                "trade_id": int(trade_id),
                "timestamp": entry_ts,
                "trade_step_ret": short_return_from_long(first_long_ret) - half_cost,
            }
        )
        for idx in range(entry_idx + 1, exit_idx + 1):
            long_ret = float(bars.iloc[idx]["close"] / bars.iloc[idx - 1]["close"] - 1.0)
            step_rows.append(
                {
                    "trade_id": int(trade_id),
                    "timestamp": pd.to_datetime(bars.iloc[idx]["timestamp"], utc=True),
                    "trade_step_ret": short_return_from_long(long_ret) - (half_cost if idx == exit_idx else 0.0),
                }
            )

    if not step_rows:
        return pd.DataFrame(columns=cols)

    path = (
        pd.DataFrame(step_rows)
        .groupby("timestamp", as_index=False)
        .agg(portfolio_ret=("trade_step_ret", "mean"), active_positions=("trade_id", "nunique"))
        .sort_values("timestamp")
        .reset_index(drop=True)
    )
    path["equity"] = (1.0 + path["portfolio_ret"].astype(float)).cumprod()
    return path[cols]


def summarize_hourly_portfolio_path(path: pd.DataFrame, *, mode: str, cost_bps: int) -> pd.DataFrame:
    cols = [
        "mode",
        "cost_bps",
        "active_hours",
        "mean_active_positions",
        "max_active_positions",
        "mean_hourly_return",
        "cumulative_net_return",
        "max_drawdown",
    ]
    if path.empty:
        return pd.DataFrame(columns=cols)
    return pd.DataFrame(
        [
            {
                "mode": mode,
                "cost_bps": int(cost_bps),
                "active_hours": int(len(path)),
                "mean_active_positions": float(path["active_positions"].mean()),
                "max_active_positions": int(path["active_positions"].max()),
                "mean_hourly_return": float(path["portfolio_ret"].mean()),
                "cumulative_net_return": float((1.0 + path["portfolio_ret"].astype(float)).prod() - 1.0),
                "max_drawdown": compute_drawdown(path["portfolio_ret"].astype(float)),
            }
        ],
        columns=cols,
    )


def summarize_hourly_portfolio_groups(
    trades: pd.DataFrame,
    bars_by_symbol: dict[str, pd.DataFrame],
    *,
    group_col: str,
    cost_bps: int,
) -> pd.DataFrame:
    cols = [
        group_col,
        "cost_bps",
        "active_hours",
        "mean_active_positions",
        "max_active_positions",
        "mean_hourly_return",
        "cumulative_net_return",
        "max_drawdown",
    ]
    if trades.empty:
        return pd.DataFrame(columns=cols)

    rows: list[dict] = []
    for value, sub in trades.groupby(group_col, dropna=False):
        path = build_equal_weight_hourly_portfolio_path(sub, bars_by_symbol, cost_bps=cost_bps)
        summary = summarize_hourly_portfolio_path(path, mode=str(value), cost_bps=cost_bps)
        if summary.empty:
            continue
        row = summary.iloc[0].to_dict()
        row[group_col] = value
        row.pop("mode", None)
        rows.append(row)
    if not rows:
        return pd.DataFrame(columns=cols)
    return pd.DataFrame(rows, columns=cols)


def summarize_hourly_active_position_buckets(path: pd.DataFrame, *, label: str) -> pd.DataFrame:
    cols = [
        "strategy",
        "active_positions",
        "hours",
        "hour_share",
        "mean_hourly_return",
        "median_hourly_return",
        "negative_hour_share",
        "conditional_cumulative_return",
    ]
    if path.empty:
        return pd.DataFrame(columns=cols)

    rows: list[dict] = []
    total_hours = float(len(path))
    for active_positions, sub in path.groupby("active_positions", dropna=False):
        port = sub["portfolio_ret"].astype(float)
        rows.append(
            {
                "strategy": label,
                "active_positions": int(active_positions),
                "hours": int(len(sub)),
                "hour_share": float(len(sub) / total_hours) if total_hours else np.nan,
                "mean_hourly_return": float(port.mean()),
                "median_hourly_return": float(port.median()),
                "negative_hour_share": float((port < 0).mean()),
                "conditional_cumulative_return": float((1.0 + port).prod() - 1.0),
            }
        )
    return pd.DataFrame(rows, columns=cols).sort_values(["strategy", "active_positions"]).reset_index(drop=True)


def build_hourly_active_position_mix_detail(
    trades: pd.DataFrame,
    path: pd.DataFrame,
    *,
    label: str,
    target_active_positions: int,
) -> pd.DataFrame:
    cols = [
        "strategy",
        "timestamp",
        "active_positions",
        "portfolio_ret",
        "symbol_pair",
        "split_mix",
        "regime_mix",
    ]
    if trades.empty or path.empty:
        return pd.DataFrame(columns=cols)

    scoped_trades = trades.copy()
    scoped_trades["entry_timestamp"] = pd.to_datetime(scoped_trades["entry_timestamp"], utc=True)
    scoped_trades["exit_timestamp"] = pd.to_datetime(scoped_trades["exit_timestamp"], utc=True)
    scoped_path = path.copy()
    scoped_path["timestamp"] = pd.to_datetime(scoped_path["timestamp"], utc=True)

    rows: list[dict] = []
    for _, hour in scoped_path.iterrows():
        if int(hour["active_positions"]) != int(target_active_positions):
            continue
        ts = pd.to_datetime(hour["timestamp"], utc=True)
        active = scoped_trades[(scoped_trades["entry_timestamp"] <= ts) & (scoped_trades["exit_timestamp"] >= ts)].copy()
        if len(active) != int(target_active_positions):
            continue
        rows.append(
            {
                "strategy": label,
                "timestamp": ts,
                "active_positions": int(target_active_positions),
                "portfolio_ret": float(hour["portfolio_ret"]),
                "symbol_pair": " + ".join(sorted(active["symbol"].astype(str).tolist())),
                "split_mix": " + ".join(sorted(active["split"].astype(str).unique().tolist())),
                "regime_mix": " + ".join(sorted(active["regime"].astype(str).unique().tolist())),
            }
        )
    return pd.DataFrame(rows, columns=cols)


def build_hourly_active_context_detail(
    trades: pd.DataFrame,
    path: pd.DataFrame,
    *,
    label: str,
    symbol_scope: str = "ALL_ACTIVE",
) -> pd.DataFrame:
    cols = [
        "strategy",
        "timestamp",
        "active_positions",
        "portfolio_ret",
        "symbol_pair",
        "split_mix",
        "regime_mix",
    ]
    if trades.empty or path.empty:
        return pd.DataFrame(columns=cols)

    scoped_trades = trades.copy()
    scoped_trades["entry_timestamp"] = pd.to_datetime(scoped_trades["entry_timestamp"], utc=True)
    scoped_trades["exit_timestamp"] = pd.to_datetime(scoped_trades["exit_timestamp"], utc=True)
    scoped_path = path.copy()
    scoped_path["timestamp"] = pd.to_datetime(scoped_path["timestamp"], utc=True)

    rows: list[dict] = []
    for _, hour in scoped_path.iterrows():
        active_positions = int(hour["active_positions"])
        if active_positions <= 0:
            continue
        ts = pd.to_datetime(hour["timestamp"], utc=True)
        active = scoped_trades[(scoped_trades["entry_timestamp"] <= ts) & (scoped_trades["exit_timestamp"] >= ts)].copy()
        if len(active) != active_positions:
            continue
        rows.append(
            {
                "strategy": label,
                "timestamp": ts,
                "active_positions": active_positions,
                "portfolio_ret": float(hour["portfolio_ret"]),
                "symbol_pair": str(symbol_scope),
                "split_mix": " + ".join(sorted(active["split"].astype(str).unique().tolist())),
                "regime_mix": " + ".join(sorted(active["regime"].astype(str).unique().tolist())),
            }
        )
    return pd.DataFrame(rows, columns=cols)


def summarize_hourly_active_position_symbol_mix(detail: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "strategy",
        "active_positions",
        "symbol_pair",
        "hours",
        "hour_share_within_bucket",
        "mean_hourly_return",
        "negative_hour_share",
        "conditional_cumulative_return",
    ]
    if detail.empty:
        return pd.DataFrame(columns=cols)

    rows: list[dict] = []
    for (strategy, active_positions), scoped in detail.groupby(["strategy", "active_positions"], dropna=False):
        total_hours = float(len(scoped))
        for symbol_pair, sub in scoped.groupby("symbol_pair", dropna=False):
            port = sub["portfolio_ret"].astype(float)
            rows.append(
                {
                    "strategy": strategy,
                    "active_positions": int(active_positions),
                    "symbol_pair": str(symbol_pair),
                    "hours": int(len(sub)),
                    "hour_share_within_bucket": float(len(sub) / total_hours) if total_hours else np.nan,
                    "mean_hourly_return": float(port.mean()),
                    "negative_hour_share": float((port < 0).mean()),
                    "conditional_cumulative_return": float((1.0 + port).prod() - 1.0),
                }
            )
    return pd.DataFrame(rows, columns=cols).sort_values(["strategy", "mean_hourly_return", "hours"], ascending=[True, True, False]).reset_index(drop=True)


def summarize_hourly_active_position_pair_context(detail: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "strategy",
        "active_positions",
        "symbol_pair",
        "split_mix",
        "regime_mix",
        "hours",
        "hour_share_within_pair",
        "mean_hourly_return",
        "negative_hour_share",
        "conditional_cumulative_return",
    ]
    if detail.empty:
        return pd.DataFrame(columns=cols)

    rows: list[dict] = []
    for (strategy, active_positions, symbol_pair), scoped in detail.groupby(["strategy", "active_positions", "symbol_pair"], dropna=False):
        total_hours = float(len(scoped))
        for (split_mix, regime_mix), sub in scoped.groupby(["split_mix", "regime_mix"], dropna=False):
            port = sub["portfolio_ret"].astype(float)
            rows.append(
                {
                    "strategy": strategy,
                    "active_positions": int(active_positions),
                    "symbol_pair": str(symbol_pair),
                    "split_mix": str(split_mix),
                    "regime_mix": str(regime_mix),
                    "hours": int(len(sub)),
                    "hour_share_within_pair": float(len(sub) / total_hours) if total_hours else np.nan,
                    "mean_hourly_return": float(port.mean()),
                    "negative_hour_share": float((port < 0).mean()),
                    "conditional_cumulative_return": float((1.0 + port).prod() - 1.0),
                }
            )
    return pd.DataFrame(rows, columns=cols).sort_values(["strategy", "hours", "mean_hourly_return"], ascending=[True, False, True]).reset_index(drop=True)


def apply_hourly_pair_sizing_policy(
    path: pd.DataFrame,
    detail: pd.DataFrame,
    *,
    target_symbol_pair: str,
    size_multiplier: float,
    target_split_values: set[str] | None = None,
    target_regime_values: set[str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    path_cols = ["timestamp", "portfolio_ret", "active_positions", "equity"]
    affected_cols = [
        "timestamp",
        "symbol_pair",
        "split_mix",
        "regime_mix",
        "portfolio_ret_before",
        "portfolio_ret_after",
        "size_multiplier",
    ]
    if path.empty or detail.empty:
        return pd.DataFrame(columns=path_cols), pd.DataFrame(columns=affected_cols)

    scoped = detail[detail["symbol_pair"].astype(str).eq(target_symbol_pair)].copy()
    if target_split_values is not None:
        scoped = scoped[scoped["split_mix"].astype(str).isin(sorted(target_split_values))].copy()
    if target_regime_values is not None:
        scoped = scoped[scoped["regime_mix"].astype(str).isin(sorted(target_regime_values))].copy()
    if scoped.empty:
        return path.copy(), pd.DataFrame(columns=affected_cols)

    scoped["timestamp"] = pd.to_datetime(scoped["timestamp"], utc=True)
    target_ts = set(scoped["timestamp"].tolist())

    policy_path = path.copy()
    policy_path["timestamp"] = pd.to_datetime(policy_path["timestamp"], utc=True)
    sel = policy_path["timestamp"].isin(target_ts)
    policy_path.loc[sel, "portfolio_ret"] = policy_path.loc[sel, "portfolio_ret"].astype(float) * float(size_multiplier)
    policy_path["equity"] = (1.0 + policy_path["portfolio_ret"].astype(float)).cumprod()

    affected = policy_path.loc[sel, ["timestamp", "portfolio_ret"]].rename(columns={"portfolio_ret": "portfolio_ret_after"}).copy()
    affected = affected.merge(
        scoped[["timestamp", "symbol_pair", "split_mix", "regime_mix", "portfolio_ret"]].rename(columns={"portfolio_ret": "portfolio_ret_before"}),
        on="timestamp",
        how="left",
    )
    affected["size_multiplier"] = float(size_multiplier)
    affected = affected[["timestamp", "symbol_pair", "split_mix", "regime_mix", "portfolio_ret_before", "portfolio_ret_after", "size_multiplier"]]
    return policy_path[path_cols], affected[affected_cols]


def summarize_hourly_pair_sizing_compare(
    raw_path: pd.DataFrame,
    gate_path: pd.DataFrame,
    conditioned_path: pd.DataFrame,
    affected_hours: pd.DataFrame,
    *,
    conditioned_label: str,
) -> pd.DataFrame:
    cols = [
        "strategy",
        "active_hours",
        "mean_active_positions",
        "max_active_positions",
        "mean_hourly_return",
        "cumulative_net_return",
        "max_drawdown",
        "affected_hours",
        "affected_hour_share",
        "target_pair_conditional_return",
    ]

    rows: list[dict] = []
    for label, src in [
        ("raw_v0", raw_path),
        ("avoid_fluctuating", gate_path),
        (conditioned_label, conditioned_path),
    ]:
        summary = summarize_hourly_portfolio_path(src, mode=label, cost_bps=20)
        if summary.empty:
            continue
        row = summary.iloc[0].to_dict()
        row["strategy"] = label
        row["affected_hours"] = np.nan
        row["affected_hour_share"] = np.nan
        row["target_pair_conditional_return"] = np.nan
        if label in {"avoid_fluctuating", conditioned_label} and not affected_hours.empty:
            if label == "avoid_fluctuating":
                pair_port = affected_hours["portfolio_ret_before"].astype(float)
            else:
                pair_port = affected_hours["portfolio_ret_after"].astype(float)
            row["affected_hours"] = int(len(affected_hours))
            row["affected_hour_share"] = float(len(affected_hours) / max(1, len(src)))
            row["target_pair_conditional_return"] = float((1.0 + pair_port).prod() - 1.0)
        row.pop("mode", None)
        row.pop("cost_bps", None)
        rows.append(row)
    return pd.DataFrame(rows, columns=cols)


def summarize_policy_affected_hours_by_split(affected_hours: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "split_mix",
        "hours",
        "hour_share_within_target",
        "conditional_cumulative_before",
        "conditional_cumulative_after",
        "delta_pp",
        "mean_hourly_return_before",
        "mean_hourly_return_after",
    ]
    if affected_hours.empty:
        return pd.DataFrame(columns=cols)
    rows = []
    total = len(affected_hours)
    for split_mix, sub in affected_hours.groupby("split_mix", dropna=False):
        before = sub["portfolio_ret_before"].astype(float)
        after = sub["portfolio_ret_after"].astype(float)
        before_cum = float((1.0 + before).prod() - 1.0)
        after_cum = float((1.0 + after).prod() - 1.0)
        rows.append(
            {
                "split_mix": str(split_mix),
                "hours": int(len(sub)),
                "hour_share_within_target": float(len(sub) / total) if total else np.nan,
                "conditional_cumulative_before": before_cum,
                "conditional_cumulative_after": after_cum,
                "delta_pp": float((after_cum - before_cum) * 100.0),
                "mean_hourly_return_before": float(before.mean()),
                "mean_hourly_return_after": float(after.mean()),
            }
        )
    return pd.DataFrame(rows, columns=cols).sort_values(["hours", "split_mix"], ascending=[False, True]).reset_index(drop=True)


def summarize_policy_affected_hours_by_regime(affected_hours: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "regime_mix",
        "hours",
        "hour_share_within_target",
        "conditional_cumulative_before",
        "conditional_cumulative_after",
        "delta_pp",
        "mean_hourly_return_before",
        "mean_hourly_return_after",
    ]
    if affected_hours.empty:
        return pd.DataFrame(columns=cols)
    rows = []
    total = len(affected_hours)
    for regime_mix, sub in affected_hours.groupby("regime_mix", dropna=False):
        before = sub["portfolio_ret_before"].astype(float)
        after = sub["portfolio_ret_after"].astype(float)
        before_cum = float((1.0 + before).prod() - 1.0)
        after_cum = float((1.0 + after).prod() - 1.0)
        rows.append(
            {
                "regime_mix": str(regime_mix),
                "hours": int(len(sub)),
                "hour_share_within_target": float(len(sub) / total) if total else np.nan,
                "conditional_cumulative_before": before_cum,
                "conditional_cumulative_after": after_cum,
                "delta_pp": float((after_cum - before_cum) * 100.0),
                "mean_hourly_return_before": float(before.mean()),
                "mean_hourly_return_after": float(after.mean()),
            }
        )
    return pd.DataFrame(rows, columns=cols).sort_values(["hours", "regime_mix"], ascending=[False, True]).reset_index(drop=True)


def summarize_policy_affected_hours_by_split_regime(affected_hours: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "split_mix",
        "regime_mix",
        "hours",
        "hour_share_within_target",
        "conditional_cumulative_before",
        "conditional_cumulative_after",
        "delta_pp",
        "mean_hourly_return_before",
        "mean_hourly_return_after",
    ]
    if affected_hours.empty:
        return pd.DataFrame(columns=cols)
    rows = []
    total = len(affected_hours)
    for (split_mix, regime_mix), sub in affected_hours.groupby(["split_mix", "regime_mix"], dropna=False):
        before = sub["portfolio_ret_before"].astype(float)
        after = sub["portfolio_ret_after"].astype(float)
        before_cum = float((1.0 + before).prod() - 1.0)
        after_cum = float((1.0 + after).prod() - 1.0)
        rows.append(
            {
                "split_mix": str(split_mix),
                "regime_mix": str(regime_mix),
                "hours": int(len(sub)),
                "hour_share_within_target": float(len(sub) / total) if total else np.nan,
                "conditional_cumulative_before": before_cum,
                "conditional_cumulative_after": after_cum,
                "delta_pp": float((after_cum - before_cum) * 100.0),
                "mean_hourly_return_before": float(before.mean()),
                "mean_hourly_return_after": float(after.mean()),
            }
        )
    return pd.DataFrame(rows, columns=cols).sort_values(["hours", "split_mix", "regime_mix"], ascending=[False, True, True]).reset_index(drop=True)


def summarize_hourly_pair_walkforward_windows(
    gate_path: pd.DataFrame,
    conditioned_path: pd.DataFrame,
    affected_hours: pd.DataFrame,
    *,
    window_days: int = 10,
    step_days: int = 5,
    min_active_hours: int = 20,
) -> pd.DataFrame:
    cols = [
        "window_start",
        "window_end",
        "active_hours",
        "affected_hours",
        "affected_hour_share",
        "gate_cumulative_net_return",
        "conditioned_cumulative_net_return",
        "delta_vs_gate_pp",
        "gate_max_drawdown",
        "conditioned_max_drawdown",
        "drawdown_improve_pp",
        "reading",
    ]
    if gate_path.empty or conditioned_path.empty:
        return pd.DataFrame(columns=cols)

    gate = gate_path.copy()
    conditioned = conditioned_path.copy()
    gate["timestamp"] = pd.to_datetime(gate["timestamp"], utc=True)
    conditioned["timestamp"] = pd.to_datetime(conditioned["timestamp"], utc=True)
    affected = affected_hours.copy()
    if not affected.empty:
        affected["timestamp"] = pd.to_datetime(affected["timestamp"], utc=True)

    start = gate["timestamp"].min().floor("D")
    end = gate["timestamp"].max().ceil("D")
    window = pd.Timedelta(days=int(window_days))
    step = pd.Timedelta(days=int(step_days))

    rows: list[dict] = []
    cur = start
    while cur + window <= end + pd.Timedelta(seconds=1):
        window_end = cur + window
        gate_sub = gate[(gate["timestamp"] >= cur) & (gate["timestamp"] < window_end)].copy()
        conditioned_sub = conditioned[(conditioned["timestamp"] >= cur) & (conditioned["timestamp"] < window_end)].copy()
        affected_sub = affected[(affected["timestamp"] >= cur) & (affected["timestamp"] < window_end)].copy() if not affected.empty else pd.DataFrame()
        if len(gate_sub) < int(min_active_hours) or len(conditioned_sub) != len(gate_sub):
            cur += step
            continue

        gate_port = gate_sub["portfolio_ret"].astype(float)
        conditioned_port = conditioned_sub["portfolio_ret"].astype(float)
        gate_equity = (1.0 + gate_port).cumprod()
        conditioned_equity = (1.0 + conditioned_port).cumprod()
        delta_pp = float(((1.0 + conditioned_port).prod() - (1.0 + gate_port).prod()) * 100.0)
        gate_mdd = float((gate_equity / gate_equity.cummax() - 1.0).min())
        conditioned_mdd = float((conditioned_equity / conditioned_equity.cummax() - 1.0).min())
        drawdown_improve_pp = float((conditioned_mdd - gate_mdd) * 100.0)
        affected_count = int(len(affected_sub))
        if affected_count == 0:
            reading = "inactive_window"
        elif delta_pp > 0 and drawdown_improve_pp > 0:
            reading = "improved_when_active"
        elif delta_pp > 0:
            reading = "return_up_but_dd_not_better"
        else:
            reading = "active_but_not_better"
        rows.append(
            {
                "window_start": cur,
                "window_end": window_end,
                "active_hours": int(len(gate_sub)),
                "affected_hours": affected_count,
                "affected_hour_share": float(affected_count / max(1, len(gate_sub))),
                "gate_cumulative_net_return": float((1.0 + gate_port).prod() - 1.0),
                "conditioned_cumulative_net_return": float((1.0 + conditioned_port).prod() - 1.0),
                "delta_vs_gate_pp": delta_pp,
                "gate_max_drawdown": gate_mdd,
                "conditioned_max_drawdown": conditioned_mdd,
                "drawdown_improve_pp": drawdown_improve_pp,
                "reading": reading,
            }
        )
        cur += step
    return pd.DataFrame(rows, columns=cols)


def summarize_hourly_pair_forward_blocks(
    gate_path: pd.DataFrame,
    conditioned_path: pd.DataFrame,
    affected_hours: pd.DataFrame,
    *,
    block_days: int = 5,
    min_active_hours: int = 12,
) -> pd.DataFrame:
    cols = [
        "block_start",
        "block_end",
        "active_hours",
        "affected_hours",
        "affected_hour_share",
        "gate_cumulative_net_return",
        "conditioned_cumulative_net_return",
        "delta_vs_gate_pp",
        "gate_max_drawdown",
        "conditioned_max_drawdown",
        "drawdown_improve_pp",
        "conditional_cumulative_before",
        "conditional_cumulative_after",
        "conditional_delta_pp",
        "reading",
    ]
    if gate_path.empty or conditioned_path.empty or affected_hours.empty:
        return pd.DataFrame(columns=cols)

    gate = gate_path.copy()
    conditioned = conditioned_path.copy()
    affected = affected_hours.copy()
    gate["timestamp"] = pd.to_datetime(gate["timestamp"], utc=True)
    conditioned["timestamp"] = pd.to_datetime(conditioned["timestamp"], utc=True)
    affected["timestamp"] = pd.to_datetime(affected["timestamp"], utc=True)

    start = affected["timestamp"].min().floor("D")
    end = gate["timestamp"].max().ceil("D")
    block = pd.Timedelta(days=int(block_days))

    rows: list[dict] = []
    cur = start
    while cur < end:
        block_end = cur + block
        gate_sub = gate[(gate["timestamp"] >= cur) & (gate["timestamp"] < block_end)].copy()
        conditioned_sub = conditioned[(conditioned["timestamp"] >= cur) & (conditioned["timestamp"] < block_end)].copy()
        affected_sub = affected[(affected["timestamp"] >= cur) & (affected["timestamp"] < block_end)].copy()
        if len(gate_sub) < int(min_active_hours) or len(conditioned_sub) != len(gate_sub):
            cur = block_end
            continue

        gate_port = gate_sub["portfolio_ret"].astype(float)
        conditioned_port = conditioned_sub["portfolio_ret"].astype(float)
        gate_equity = (1.0 + gate_port).cumprod()
        conditioned_equity = (1.0 + conditioned_port).cumprod()
        delta_pp = float(((1.0 + conditioned_port).prod() - (1.0 + gate_port).prod()) * 100.0)
        gate_mdd = float((gate_equity / gate_equity.cummax() - 1.0).min())
        conditioned_mdd = float((conditioned_equity / conditioned_equity.cummax() - 1.0).min())
        drawdown_improve_pp = float((conditioned_mdd - gate_mdd) * 100.0)
        affected_count = int(len(affected_sub))
        if affected_count > 0:
            conditional_before = float((1.0 + affected_sub["portfolio_ret_before"].astype(float)).prod() - 1.0)
            conditional_after = float((1.0 + affected_sub["portfolio_ret_after"].astype(float)).prod() - 1.0)
            conditional_delta_pp = float((conditional_after - conditional_before) * 100.0)
        else:
            conditional_before = np.nan
            conditional_after = np.nan
            conditional_delta_pp = np.nan
        if affected_count == 0:
            reading = "inactive_block"
        elif delta_pp > 0 and drawdown_improve_pp > 0:
            reading = "better_return_and_dd"
        elif delta_pp > 0:
            reading = "better_return_only"
        else:
            reading = "worse_than_gate"
        rows.append(
            {
                "block_start": cur,
                "block_end": block_end,
                "active_hours": int(len(gate_sub)),
                "affected_hours": affected_count,
                "affected_hour_share": float(affected_count / max(1, len(gate_sub))),
                "gate_cumulative_net_return": float((1.0 + gate_port).prod() - 1.0),
                "conditioned_cumulative_net_return": float((1.0 + conditioned_port).prod() - 1.0),
                "delta_vs_gate_pp": delta_pp,
                "gate_max_drawdown": gate_mdd,
                "conditioned_max_drawdown": conditioned_mdd,
                "drawdown_improve_pp": drawdown_improve_pp,
                "conditional_cumulative_before": conditional_before,
                "conditional_cumulative_after": conditional_after,
                "conditional_delta_pp": conditional_delta_pp,
                "reading": reading,
            }
        )
        cur = block_end
    return pd.DataFrame(rows, columns=cols)


def summarize_hourly_pair_shadow_checkpoints(
    gate_path: pd.DataFrame,
    conditioned_path: pd.DataFrame,
    affected_hours: pd.DataFrame,
    *,
    review_days: list[int] | tuple[int, ...] = (5, 10, 15, 20),
    min_active_hours: int = 12,
) -> pd.DataFrame:
    cols = [
        "review_days",
        "checkpoint_start",
        "checkpoint_end",
        "active_hours",
        "affected_hours",
        "affected_hour_share",
        "gate_cumulative_net_return",
        "conditioned_cumulative_net_return",
        "delta_vs_gate_pp",
        "gate_max_drawdown",
        "conditioned_max_drawdown",
        "drawdown_improve_pp",
        "reading",
    ]
    if gate_path.empty or conditioned_path.empty or affected_hours.empty:
        return pd.DataFrame(columns=cols)

    gate = gate_path.copy()
    conditioned = conditioned_path.copy()
    affected = affected_hours.copy()
    gate["timestamp"] = pd.to_datetime(gate["timestamp"], utc=True)
    conditioned["timestamp"] = pd.to_datetime(conditioned["timestamp"], utc=True)
    affected["timestamp"] = pd.to_datetime(affected["timestamp"], utc=True)

    start = affected["timestamp"].min().floor("D")
    rows: list[dict] = []
    for days in review_days:
        checkpoint_end = start + pd.Timedelta(days=int(days))
        gate_sub = gate[(gate["timestamp"] >= start) & (gate["timestamp"] < checkpoint_end)].copy()
        conditioned_sub = conditioned[(conditioned["timestamp"] >= start) & (conditioned["timestamp"] < checkpoint_end)].copy()
        affected_sub = affected[(affected["timestamp"] >= start) & (affected["timestamp"] < checkpoint_end)].copy()
        if len(gate_sub) < int(min_active_hours) or len(conditioned_sub) != len(gate_sub):
            continue

        gate_port = gate_sub["portfolio_ret"].astype(float)
        conditioned_port = conditioned_sub["portfolio_ret"].astype(float)
        gate_equity = (1.0 + gate_port).cumprod()
        conditioned_equity = (1.0 + conditioned_port).cumprod()
        delta_pp = float(((1.0 + conditioned_port).prod() - (1.0 + gate_port).prod()) * 100.0)
        gate_mdd = float((gate_equity / gate_equity.cummax() - 1.0).min())
        conditioned_mdd = float((conditioned_equity / conditioned_equity.cummax() - 1.0).min())
        drawdown_improve_pp = float((conditioned_mdd - gate_mdd) * 100.0)
        affected_count = int(len(affected_sub))
        if affected_count == 0:
            reading = "inactive_checkpoint"
        elif delta_pp > 0 and drawdown_improve_pp > 0:
            reading = "checkpoint_still_positive"
        elif delta_pp > 0:
            reading = "positive_but_dd_not_better"
        else:
            reading = "checkpoint_negative"
        rows.append(
            {
                "review_days": int(days),
                "checkpoint_start": start,
                "checkpoint_end": checkpoint_end,
                "active_hours": int(len(gate_sub)),
                "affected_hours": affected_count,
                "affected_hour_share": float(affected_count / max(1, len(gate_sub))),
                "gate_cumulative_net_return": float((1.0 + gate_port).prod() - 1.0),
                "conditioned_cumulative_net_return": float((1.0 + conditioned_port).prod() - 1.0),
                "delta_vs_gate_pp": delta_pp,
                "gate_max_drawdown": gate_mdd,
                "conditioned_max_drawdown": conditioned_mdd,
                "drawdown_improve_pp": drawdown_improve_pp,
                "reading": reading,
            }
        )
    return pd.DataFrame(rows, columns=cols)


def summarize_hourly_pair_shadow_checkpoints_hours(
    gate_path: pd.DataFrame,
    conditioned_path: pd.DataFrame,
    affected_hours: pd.DataFrame,
    *,
    review_hours: list[int] | tuple[int, ...] = (6, 12, 18, 24),
    min_active_hours: int = 4,
) -> pd.DataFrame:
    cols = [
        "review_hours",
        "checkpoint_start",
        "checkpoint_end",
        "active_hours",
        "affected_hours",
        "affected_hour_share",
        "gate_cumulative_net_return",
        "conditioned_cumulative_net_return",
        "delta_vs_gate_pp",
        "gate_max_drawdown",
        "conditioned_max_drawdown",
        "drawdown_improve_pp",
        "reading",
    ]
    if gate_path.empty or conditioned_path.empty or affected_hours.empty:
        return pd.DataFrame(columns=cols)

    gate = gate_path.copy()
    conditioned = conditioned_path.copy()
    affected = affected_hours.copy()
    gate["timestamp"] = pd.to_datetime(gate["timestamp"], utc=True)
    conditioned["timestamp"] = pd.to_datetime(conditioned["timestamp"], utc=True)
    affected["timestamp"] = pd.to_datetime(affected["timestamp"], utc=True)

    start = affected["timestamp"].min()
    max_covered_end = gate["timestamp"].max() + pd.Timedelta(hours=1)
    rows: list[dict] = []
    for hours in review_hours:
        checkpoint_end = start + pd.Timedelta(hours=int(hours))
        if checkpoint_end > max_covered_end:
            continue
        gate_sub = gate[(gate["timestamp"] >= start) & (gate["timestamp"] < checkpoint_end)].copy()
        conditioned_sub = conditioned[(conditioned["timestamp"] >= start) & (conditioned["timestamp"] < checkpoint_end)].copy()
        affected_sub = affected[(affected["timestamp"] >= start) & (affected["timestamp"] < checkpoint_end)].copy()
        if len(gate_sub) < int(min_active_hours) or len(conditioned_sub) != len(gate_sub):
            continue

        gate_port = gate_sub["portfolio_ret"].astype(float)
        conditioned_port = conditioned_sub["portfolio_ret"].astype(float)
        gate_equity = (1.0 + gate_port).cumprod()
        conditioned_equity = (1.0 + conditioned_port).cumprod()
        delta_pp = float(((1.0 + conditioned_port).prod() - (1.0 + gate_port).prod()) * 100.0)
        gate_mdd = float((gate_equity / gate_equity.cummax() - 1.0).min())
        conditioned_mdd = float((conditioned_equity / conditioned_equity.cummax() - 1.0).min())
        drawdown_improve_pp = float((conditioned_mdd - gate_mdd) * 100.0)
        affected_count = int(len(affected_sub))
        if affected_count == 0:
            reading = "inactive_checkpoint"
        elif delta_pp > 0 and drawdown_improve_pp > 0:
            reading = "checkpoint_still_positive"
        elif delta_pp > 0:
            reading = "positive_but_dd_not_better"
        else:
            reading = "checkpoint_negative"
        rows.append(
            {
                "review_hours": int(hours),
                "checkpoint_start": start,
                "checkpoint_end": checkpoint_end,
                "active_hours": int(len(gate_sub)),
                "affected_hours": affected_count,
                "affected_hour_share": float(affected_count / max(1, len(gate_sub))),
                "gate_cumulative_net_return": float((1.0 + gate_port).prod() - 1.0),
                "conditioned_cumulative_net_return": float((1.0 + conditioned_port).prod() - 1.0),
                "delta_vs_gate_pp": delta_pp,
                "gate_max_drawdown": gate_mdd,
                "conditioned_max_drawdown": conditioned_mdd,
                "drawdown_improve_pp": drawdown_improve_pp,
                "reading": reading,
            }
        )
    return pd.DataFrame(rows, columns=cols)


def summarize_hourly_pair_forward_blocks_hours(
    gate_path: pd.DataFrame,
    conditioned_path: pd.DataFrame,
    affected_hours: pd.DataFrame,
    *,
    block_hours: int = 6,
    min_active_hours: int = 4,
) -> pd.DataFrame:
    cols = [
        "block_id",
        "block_start",
        "block_end",
        "active_hours",
        "affected_hours",
        "affected_hour_share",
        "gate_cumulative_net_return",
        "conditioned_cumulative_net_return",
        "delta_vs_gate_pp",
        "gate_max_drawdown",
        "conditioned_max_drawdown",
        "drawdown_improve_pp",
        "conditional_cumulative_before",
        "conditional_cumulative_after",
        "conditional_delta_pp",
        "reading",
    ]
    if gate_path.empty or conditioned_path.empty or affected_hours.empty:
        return pd.DataFrame(columns=cols)

    gate = gate_path.copy()
    conditioned = conditioned_path.copy()
    affected = affected_hours.copy()
    gate["timestamp"] = pd.to_datetime(gate["timestamp"], utc=True)
    conditioned["timestamp"] = pd.to_datetime(conditioned["timestamp"], utc=True)
    affected["timestamp"] = pd.to_datetime(affected["timestamp"], utc=True)

    start = affected["timestamp"].min()
    end = affected["timestamp"].max() + pd.Timedelta(hours=1)
    block = pd.Timedelta(hours=int(block_hours))

    rows: list[dict] = []
    cur = start
    block_id = 0
    while cur < end:
        block_end = cur + block
        gate_sub = gate[(gate["timestamp"] >= cur) & (gate["timestamp"] < block_end)].copy()
        conditioned_sub = conditioned[(conditioned["timestamp"] >= cur) & (conditioned["timestamp"] < block_end)].copy()
        affected_sub = affected[(affected["timestamp"] >= cur) & (affected["timestamp"] < block_end)].copy()
        if len(gate_sub) < int(min_active_hours) or len(conditioned_sub) != len(gate_sub):
            cur = block_end
            continue

        block_id += 1
        gate_port = gate_sub["portfolio_ret"].astype(float)
        conditioned_port = conditioned_sub["portfolio_ret"].astype(float)
        gate_equity = (1.0 + gate_port).cumprod()
        conditioned_equity = (1.0 + conditioned_port).cumprod()
        delta_pp = float(((1.0 + conditioned_port).prod() - (1.0 + gate_port).prod()) * 100.0)
        gate_mdd = float((gate_equity / gate_equity.cummax() - 1.0).min())
        conditioned_mdd = float((conditioned_equity / conditioned_equity.cummax() - 1.0).min())
        drawdown_improve_pp = float((conditioned_mdd - gate_mdd) * 100.0)
        affected_count = int(len(affected_sub))
        if affected_count > 0:
            conditional_before = float((1.0 + affected_sub["portfolio_ret_before"].astype(float)).prod() - 1.0)
            conditional_after = float((1.0 + affected_sub["portfolio_ret_after"].astype(float)).prod() - 1.0)
            conditional_delta_pp = float((conditional_after - conditional_before) * 100.0)
        else:
            conditional_before = np.nan
            conditional_after = np.nan
            conditional_delta_pp = np.nan

        if affected_count == 0:
            reading = "inactive_block"
        elif delta_pp > 0 and conditional_delta_pp > 0:
            reading = "positive_block"
        elif delta_pp > 0:
            reading = "positive_path_only"
        else:
            reading = "negative_block"

        rows.append(
            {
                "block_id": int(block_id),
                "block_start": cur,
                "block_end": block_end,
                "active_hours": int(len(gate_sub)),
                "affected_hours": affected_count,
                "affected_hour_share": float(affected_count / max(1, len(gate_sub))),
                "gate_cumulative_net_return": float((1.0 + gate_port).prod() - 1.0),
                "conditioned_cumulative_net_return": float((1.0 + conditioned_port).prod() - 1.0),
                "delta_vs_gate_pp": delta_pp,
                "gate_max_drawdown": gate_mdd,
                "conditioned_max_drawdown": conditioned_mdd,
                "drawdown_improve_pp": drawdown_improve_pp,
                "conditional_cumulative_before": conditional_before,
                "conditional_cumulative_after": conditional_after,
                "conditional_delta_pp": conditional_delta_pp,
                "reading": reading,
            }
        )
        cur = block_end

    return pd.DataFrame(rows, columns=cols)


def summarize_hourly_pair_tail_snapshot(
    gate_path: pd.DataFrame,
    conditioned_path: pd.DataFrame,
    affected_hours: pd.DataFrame,
    *,
    split_value: str = "test",
) -> pd.DataFrame:
    cols = [
        "slice_label",
        "slice_start",
        "slice_end",
        "active_hours",
        "affected_hours",
        "affected_hour_share",
        "gate_cumulative_net_return",
        "conditioned_cumulative_net_return",
        "delta_vs_gate_pp",
        "gate_max_drawdown",
        "conditioned_max_drawdown",
        "drawdown_improve_pp",
        "conditional_cumulative_before",
        "conditional_cumulative_after",
        "conditional_delta_pp",
        "up_hours",
        "flat_hours",
        "down_flat_hours",
        "down_hours",
        "reading",
    ]
    if gate_path.empty or conditioned_path.empty or affected_hours.empty:
        return pd.DataFrame(columns=cols)

    gate = gate_path.copy()
    conditioned = conditioned_path.copy()
    affected = affected_hours.copy()
    gate["timestamp"] = pd.to_datetime(gate["timestamp"], utc=True)
    conditioned["timestamp"] = pd.to_datetime(conditioned["timestamp"], utc=True)
    affected["timestamp"] = pd.to_datetime(affected["timestamp"], utc=True)

    target = affected[affected["split_mix"].astype(str).eq(split_value)].copy()
    if target.empty:
        return pd.DataFrame(columns=cols)

    start = target["timestamp"].min()
    end = gate["timestamp"].max()
    gate_sub = gate[gate["timestamp"] >= start].copy()
    conditioned_sub = conditioned[conditioned["timestamp"] >= start].copy()
    if gate_sub.empty or conditioned_sub.empty or len(gate_sub) != len(conditioned_sub):
        return pd.DataFrame(columns=cols)

    gate_port = gate_sub["portfolio_ret"].astype(float)
    conditioned_port = conditioned_sub["portfolio_ret"].astype(float)
    gate_equity = (1.0 + gate_port).cumprod()
    conditioned_equity = (1.0 + conditioned_port).cumprod()
    regime_counts = target["regime_mix"].astype(str).value_counts().to_dict()
    conditional_before = float((1.0 + target["portfolio_ret_before"].astype(float)).prod() - 1.0)
    conditional_after = float((1.0 + target["portfolio_ret_after"].astype(float)).prod() - 1.0)
    row = {
        "slice_label": f"{split_value}_tail_from_first_trigger",
        "slice_start": start,
        "slice_end": end,
        "active_hours": int(len(gate_sub)),
        "affected_hours": int(len(target)),
        "affected_hour_share": float(len(target) / max(1, len(gate_sub))),
        "gate_cumulative_net_return": float((1.0 + gate_port).prod() - 1.0),
        "conditioned_cumulative_net_return": float((1.0 + conditioned_port).prod() - 1.0),
        "delta_vs_gate_pp": float(((1.0 + conditioned_port).prod() - (1.0 + gate_port).prod()) * 100.0),
        "gate_max_drawdown": float((gate_equity / gate_equity.cummax() - 1.0).min()),
        "conditioned_max_drawdown": float((conditioned_equity / conditioned_equity.cummax() - 1.0).min()),
        "drawdown_improve_pp": float(((conditioned_equity / conditioned_equity.cummax() - 1.0).min() - (gate_equity / gate_equity.cummax() - 1.0).min()) * 100.0),
        "conditional_cumulative_before": conditional_before,
        "conditional_cumulative_after": conditional_after,
        "conditional_delta_pp": float((conditional_after - conditional_before) * 100.0),
        "up_hours": int(regime_counts.get("up", 0)),
        "flat_hours": int(regime_counts.get("flat", 0)),
        "down_flat_hours": int(regime_counts.get("down + flat", 0)),
        "down_hours": int(regime_counts.get("down", 0)),
        "reading": "positive_but_single_tail" if ((1.0 + conditioned_port).prod() - (1.0 + gate_port).prod()) > 0 else "tail_not_better",
    }
    return pd.DataFrame([row], columns=cols)


def summarize_pair_regime_coverage_audit(
    gate_regime_summary: pd.DataFrame,
    affected_regime_summary: pd.DataFrame,
) -> pd.DataFrame:
    cols = [
        "regime",
        "gate_active_hours",
        "gate_mean_hourly_return",
        "gate_cumulative_net_return",
        "policy_affected_hours",
        "policy_coverage_share",
        "policy_conditional_delta_pp",
        "reading",
    ]
    if gate_regime_summary is None or gate_regime_summary.empty:
        return pd.DataFrame(columns=cols)

    affected_map = affected_regime_summary.set_index("regime_mix").to_dict("index") if affected_regime_summary is not None and not affected_regime_summary.empty else {}
    rows: list[dict] = []
    for _, row in gate_regime_summary.iterrows():
        regime = str(row.get("regime", ""))
        gate_hours = int(row.get("active_hours", 0))
        affected = affected_map.get(regime, {})
        affected_hours = int(affected.get("hours", 0))
        coverage_share = float(affected_hours / max(1, gate_hours))
        delta_pp = affected.get("delta_pp", np.nan)
        if regime == "down" and affected_hours == 0:
            reading = "hard_gap_no_down_coverage"
        elif affected_hours == 0:
            reading = "not_targeted"
        elif pd.notna(delta_pp) and float(delta_pp) > 0:
            reading = "targeted_and_improving"
        else:
            reading = "targeted_but_not_better"
        rows.append(
            {
                "regime": regime,
                "gate_active_hours": gate_hours,
                "gate_mean_hourly_return": float(row.get("mean_hourly_return", np.nan)),
                "gate_cumulative_net_return": float(row.get("cumulative_net_return", np.nan)),
                "policy_affected_hours": affected_hours,
                "policy_coverage_share": coverage_share,
                "policy_conditional_delta_pp": float(delta_pp) if pd.notna(delta_pp) else np.nan,
                "reading": reading,
            }
        )

    return pd.DataFrame(rows, columns=cols)


def summarize_pair_predown_bridge_audit(
    gate_path: pd.DataFrame,
    conditioned_path: pd.DataFrame,
    active_context: pd.DataFrame,
    affected_hours: pd.DataFrame,
    *,
    lead_hours_list: list[int],
) -> pd.DataFrame:
    cols = [
        "lead_hours",
        "bridge_start",
        "bridge_end",
        "bridge_hours",
        "affected_hours",
        "coverage_share",
        "lead_to_first_down_min",
        "lead_to_first_down_max",
        "split_mix_values",
        "regime_mix_values",
        "gate_cumulative_net_return",
        "conditioned_cumulative_net_return",
        "delta_vs_gate_pp",
        "reading",
    ]
    if gate_path is None or conditioned_path is None or active_context is None or active_context.empty:
        return pd.DataFrame(columns=cols)

    gate = gate_path.copy()
    conditioned = conditioned_path.copy()
    context = active_context.copy()
    affected = affected_hours.copy() if affected_hours is not None else pd.DataFrame(columns=["timestamp"])
    for df in [gate, conditioned, context, affected]:
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    gate = gate.dropna(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
    conditioned = conditioned.dropna(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
    context = context.dropna(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
    affected = affected.dropna(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
    if gate.empty or conditioned.empty or context.empty or len(gate) != len(conditioned):
        return pd.DataFrame(columns=cols)

    pure_down_ts = set(context.loc[context["regime_mix"].astype(str).eq("down"), "timestamp"])
    if not pure_down_ts:
        return pd.DataFrame(columns=cols)

    rows: list[dict] = []
    non_down = context.loc[~context["regime_mix"].astype(str).eq("down")].copy()
    for lead_hours in lead_hours_list:
        scoped = non_down.copy()
        lead_values: list[int] = []
        keep_mask: list[bool] = []
        for _, row in scoped.iterrows():
            ts = pd.to_datetime(row["timestamp"], utc=True)
            hits = [h for h in range(1, int(lead_hours) + 1) if (ts + pd.Timedelta(hours=h)) in pure_down_ts]
            keep_mask.append(bool(hits))
            lead_values.append(min(hits) if hits else 0)
        scoped["keep"] = keep_mask
        scoped["lead_to_first_down"] = lead_values
        target = scoped.loc[scoped["keep"]].copy()
        if target.empty:
            rows.append(
                {
                    "lead_hours": int(lead_hours),
                    "bridge_start": pd.NaT,
                    "bridge_end": pd.NaT,
                    "bridge_hours": 0,
                    "affected_hours": 0,
                    "coverage_share": 0.0,
                    "lead_to_first_down_min": np.nan,
                    "lead_to_first_down_max": np.nan,
                    "split_mix_values": "",
                    "regime_mix_values": "",
                    "gate_cumulative_net_return": np.nan,
                    "conditioned_cumulative_net_return": np.nan,
                    "delta_vs_gate_pp": np.nan,
                    "reading": "no_predown_bridge_in_sample",
                }
            )
            continue

        timestamps = set(target["timestamp"])
        gate_sub = gate.loc[gate["timestamp"].isin(timestamps)].copy()
        conditioned_sub = conditioned.loc[conditioned["timestamp"].isin(timestamps)].copy()
        affected_sub = affected.loc[affected["timestamp"].isin(timestamps)].copy() if not affected.empty else pd.DataFrame(columns=["timestamp"])
        gate_port = gate_sub["portfolio_ret"].astype(float)
        conditioned_port = conditioned_sub["portfolio_ret"].astype(float)
        rows.append(
            {
                "lead_hours": int(lead_hours),
                "bridge_start": target["timestamp"].iloc[0],
                "bridge_end": target["timestamp"].iloc[-1],
                "bridge_hours": int(len(target)),
                "affected_hours": int(len(affected_sub)),
                "coverage_share": float(len(affected_sub) / max(1, len(target))),
                "lead_to_first_down_min": int(target["lead_to_first_down"].min()),
                "lead_to_first_down_max": int(target["lead_to_first_down"].max()),
                "split_mix_values": " / ".join(sorted(target["split_mix"].astype(str).dropna().unique().tolist())),
                "regime_mix_values": " / ".join(sorted(target["regime_mix"].astype(str).dropna().unique().tolist())),
                "gate_cumulative_net_return": float((1.0 + gate_port).prod() - 1.0),
                "conditioned_cumulative_net_return": float((1.0 + conditioned_port).prod() - 1.0),
                "delta_vs_gate_pp": float(((1.0 + conditioned_port).prod() - (1.0 + gate_port).prod()) * 100.0),
                "reading": "no_anticipatory_bridge_coverage" if affected_sub.empty else "anticipatory_bridge_present",
            }
        )

    return pd.DataFrame(rows, columns=cols)


def summarize_pair_downrisk_zone_audit(
    base_path: pd.DataFrame,
    conditioned_path: pd.DataFrame,
    active_context: pd.DataFrame,
    affected_hours: pd.DataFrame,
    *,
    lead_hours_list: list[int],
    policy: str,
    reference_policy: str,
) -> pd.DataFrame:
    cols = [
        "policy",
        "reference_policy",
        "lead_hours",
        "pure_down_hours",
        "bridge_hours",
        "risk_zone_hours",
        "affected_total_hours",
        "affected_pure_down_hours",
        "affected_bridge_hours",
        "coverage_share",
        "pure_down_coverage_share",
        "bridge_coverage_share",
        "base_cumulative_net_return",
        "conditioned_cumulative_net_return",
        "delta_vs_reference_pp",
        "reading",
    ]
    if base_path is None or conditioned_path is None or active_context is None or active_context.empty:
        return pd.DataFrame(columns=cols)

    base = base_path.copy()
    conditioned = conditioned_path.copy()
    context = active_context.copy()
    affected = affected_hours.copy() if affected_hours is not None else pd.DataFrame(columns=["timestamp"])
    for df in [base, conditioned, context, affected]:
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    base = base.dropna(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
    conditioned = conditioned.dropna(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
    context = context.dropna(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
    affected = affected.dropna(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
    if base.empty or conditioned.empty or context.empty or len(base) != len(conditioned):
        return pd.DataFrame(columns=cols)

    pure_down = context.loc[context["regime_mix"].astype(str).eq("down")].copy()
    pure_down_ts = set(pure_down["timestamp"].tolist())
    if not pure_down_ts:
        return pd.DataFrame(columns=cols)

    non_down = context.loc[~context["regime_mix"].astype(str).eq("down")].copy()
    rows: list[dict] = []
    for lead_hours in lead_hours_list:
        bridge = non_down.copy()
        keep_mask: list[bool] = []
        for _, row in bridge.iterrows():
            ts = pd.to_datetime(row["timestamp"], utc=True)
            hits = any((ts + pd.Timedelta(hours=h)) in pure_down_ts for h in range(1, int(lead_hours) + 1))
            keep_mask.append(bool(hits))
        bridge = bridge.loc[keep_mask].copy()
        risk_zone = pd.concat([pure_down, bridge], ignore_index=True).drop_duplicates(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
        risk_zone_ts = set(risk_zone["timestamp"].tolist())
        if not risk_zone_ts:
            rows.append(
                {
                    "policy": policy,
                    "reference_policy": reference_policy,
                    "lead_hours": int(lead_hours),
                    "pure_down_hours": 0,
                    "bridge_hours": 0,
                    "risk_zone_hours": 0,
                    "affected_total_hours": 0,
                    "affected_pure_down_hours": 0,
                    "affected_bridge_hours": 0,
                    "coverage_share": 0.0,
                    "pure_down_coverage_share": 0.0,
                    "bridge_coverage_share": 0.0,
                    "base_cumulative_net_return": np.nan,
                    "conditioned_cumulative_net_return": np.nan,
                    "delta_vs_reference_pp": np.nan,
                    "reading": "no_downrisk_zone_in_sample",
                }
            )
            continue

        pure_down_bridge_ts = set(bridge["timestamp"].tolist())
        base_sub = base.loc[base["timestamp"].isin(risk_zone_ts)].copy()
        conditioned_sub = conditioned.loc[conditioned["timestamp"].isin(risk_zone_ts)].copy()
        affected_sub = affected.loc[affected["timestamp"].isin(risk_zone_ts)].copy() if not affected.empty else pd.DataFrame(columns=["timestamp"])
        affected_pure_down = affected_sub.loc[affected_sub["timestamp"].isin(pure_down_ts)].copy() if not affected_sub.empty else pd.DataFrame(columns=["timestamp"])
        affected_bridge = affected_sub.loc[affected_sub["timestamp"].isin(pure_down_bridge_ts)].copy() if not affected_sub.empty else pd.DataFrame(columns=["timestamp"])
        base_port = base_sub["portfolio_ret"].astype(float)
        conditioned_port = conditioned_sub["portfolio_ret"].astype(float)
        if affected_sub.empty:
            reading = "no_downrisk_coverage"
        elif affected_pure_down.empty and not affected_bridge.empty:
            reading = "bridge_only_no_pure_down"
        elif float(((1.0 + conditioned_port).prod() - (1.0 + base_port).prod()) * 100.0) > 0:
            reading = "downrisk_zone_improved"
        else:
            reading = "downrisk_hit_but_not_better"
        rows.append(
            {
                "policy": policy,
                "reference_policy": reference_policy,
                "lead_hours": int(lead_hours),
                "pure_down_hours": int(len(pure_down)),
                "bridge_hours": int(len(bridge)),
                "risk_zone_hours": int(len(risk_zone)),
                "affected_total_hours": int(len(affected_sub)),
                "affected_pure_down_hours": int(len(affected_pure_down)),
                "affected_bridge_hours": int(len(affected_bridge)),
                "coverage_share": float(len(affected_sub) / max(1, len(risk_zone))),
                "pure_down_coverage_share": float(len(affected_pure_down) / max(1, len(pure_down))),
                "bridge_coverage_share": float(len(affected_bridge) / max(1, len(bridge))) if len(bridge) else 0.0,
                "base_cumulative_net_return": float((1.0 + base_port).prod() - 1.0),
                "conditioned_cumulative_net_return": float((1.0 + conditioned_port).prod() - 1.0),
                "delta_vs_reference_pp": float(((1.0 + conditioned_port).prod() - (1.0 + base_port).prod()) * 100.0),
                "reading": reading,
            }
        )

    return pd.DataFrame(rows, columns=cols)


def summarize_policy_future_pure_down_lead_audit(
    affected_hours: pd.DataFrame,
    active_context: pd.DataFrame,
    *,
    future_window_hours_list: list[int],
    policy: str,
    reference_policy: str,
) -> pd.DataFrame:
    cols = [
        "policy",
        "reference_policy",
        "future_window_hours",
        "policy_affected_hours",
        "matched_hours",
        "matched_share",
        "matched_test_hours",
        "matched_train_overlap_hours",
        "closest_lead_h",
        "median_lead_h",
        "furthest_lead_h",
        "split_mix_values",
        "regime_mix_values",
        "reading",
    ]
    if affected_hours is None or affected_hours.empty or active_context is None or active_context.empty:
        return pd.DataFrame(columns=cols)

    affected = affected_hours.copy()
    context = active_context.copy()
    for df in [affected, context]:
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    affected = affected.dropna(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
    context = context.dropna(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
    if affected.empty or context.empty:
        return pd.DataFrame(columns=cols)

    pure_down_ts = sorted(context.loc[context["regime_mix"].astype(str).eq("down"), "timestamp"].tolist())
    if not pure_down_ts:
        return pd.DataFrame(columns=cols)

    leads: list[float] = []
    for ts in affected["timestamp"]:
        future = [(down_ts - ts).total_seconds() / 3600.0 for down_ts in pure_down_ts if down_ts > ts]
        leads.append(min(future) if future else np.nan)
    affected["lead_to_next_pure_down_h"] = leads

    rows: list[dict] = []
    total_hours = int(len(affected))
    for future_window_hours in future_window_hours_list:
        scoped = affected.loc[affected["lead_to_next_pure_down_h"].le(float(future_window_hours))].copy()
        if scoped.empty:
            rows.append(
                {
                    "policy": policy,
                    "reference_policy": reference_policy,
                    "future_window_hours": int(future_window_hours),
                    "policy_affected_hours": total_hours,
                    "matched_hours": 0,
                    "matched_share": 0.0,
                    "matched_test_hours": 0,
                    "matched_train_overlap_hours": 0,
                    "closest_lead_h": np.nan,
                    "median_lead_h": np.nan,
                    "furthest_lead_h": np.nan,
                    "split_mix_values": "",
                    "regime_mix_values": "",
                    "reading": "no_future_pure_down_within_window",
                }
            )
            continue

        split_values = sorted(scoped["split_mix"].astype(str).dropna().unique().tolist()) if "split_mix" in scoped.columns else []
        regime_values = sorted(scoped["regime_mix"].astype(str).dropna().unique().tolist()) if "regime_mix" in scoped.columns else []
        matched_test = int(scoped["split_mix"].astype(str).str.contains("test", na=False).sum()) if "split_mix" in scoped.columns else 0
        matched_train_overlap = int(len(scoped) - matched_test)
        reading = "future_pure_down_includes_test" if matched_test > 0 else "future_pure_down_only_train_overlap"
        rows.append(
            {
                "policy": policy,
                "reference_policy": reference_policy,
                "future_window_hours": int(future_window_hours),
                "policy_affected_hours": total_hours,
                "matched_hours": int(len(scoped)),
                "matched_share": float(len(scoped) / max(1, total_hours)),
                "matched_test_hours": matched_test,
                "matched_train_overlap_hours": matched_train_overlap,
                "closest_lead_h": float(scoped["lead_to_next_pure_down_h"].min()),
                "median_lead_h": float(scoped["lead_to_next_pure_down_h"].median()),
                "furthest_lead_h": float(scoped["lead_to_next_pure_down_h"].max()),
                "split_mix_values": " / ".join(split_values),
                "regime_mix_values": " / ".join(regime_values),
                "reading": reading,
            }
        )

    return pd.DataFrame(rows, columns=cols)


def summarize_policy_affected_hour_episodes(affected_hours_df: pd.DataFrame | None) -> pd.DataFrame:
    cols = [
        "episode_id",
        "start_time",
        "end_time",
        "hours",
        "hour_share_within_target",
        "symbol_pair",
        "split_mix",
        "regime_mix",
        "conditional_cumulative_before",
        "conditional_cumulative_after",
        "delta_pp",
        "mean_hourly_return_before",
        "mean_hourly_return_after",
        "reading",
    ]
    if affected_hours_df is None or affected_hours_df.empty:
        return pd.DataFrame(columns=cols)

    df = affected_hours_df.copy()
    if "timestamp" not in df.columns:
        return pd.DataFrame(columns=cols)

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df = df.dropna(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
    if df.empty:
        return pd.DataFrame(columns=cols)

    split_key = df.get("split_mix", "").astype(str)
    regime_key = df.get("regime_mix", "").astype(str)
    symbol_key = df.get("symbol_pair", "").astype(str)
    prev_time = df["timestamp"].shift(1)
    contiguous = (df["timestamp"] - prev_time).dt.total_seconds().eq(3600)
    same_key = split_key.eq(split_key.shift(1)) & regime_key.eq(regime_key.shift(1)) & symbol_key.eq(symbol_key.shift(1))
    df["episode_id"] = (~(contiguous & same_key)).cumsum().astype(int)

    total_hours = int(len(df))
    rows: list[dict] = []
    for episode_id, grp in df.groupby("episode_id", sort=True):
        split_mix = str(grp["split_mix"].iloc[0]) if "split_mix" in grp.columns else ""
        regime_mix = str(grp["regime_mix"].iloc[0]) if "regime_mix" in grp.columns else ""
        conditional_before = float((1.0 + grp["portfolio_ret_before"].fillna(0.0)).prod() - 1.0)
        conditional_after = float((1.0 + grp["portfolio_ret_after"].fillna(0.0)).prod() - 1.0)
        if split_mix == "test" and regime_mix == "down + flat":
            reading = "late_mixed_tail_patch"
        elif split_mix == "test":
            reading = "thin_pre_mixed_tail"
        elif "validate" in split_mix:
            reading = "overlap_carry"
        elif split_mix == "train":
            reading = "train_residual"
        else:
            reading = "episode"
        rows.append(
            {
                "episode_id": int(episode_id),
                "start_time": grp["timestamp"].iloc[0],
                "end_time": grp["timestamp"].iloc[-1],
                "hours": int(len(grp)),
                "hour_share_within_target": float(len(grp) / max(1, total_hours)),
                "symbol_pair": str(grp["symbol_pair"].iloc[0]) if "symbol_pair" in grp.columns else "",
                "split_mix": split_mix,
                "regime_mix": regime_mix,
                "conditional_cumulative_before": conditional_before,
                "conditional_cumulative_after": conditional_after,
                "delta_pp": float((conditional_after - conditional_before) * 100.0),
                "mean_hourly_return_before": float(grp["portfolio_ret_before"].mean()),
                "mean_hourly_return_after": float(grp["portfolio_ret_after"].mean()),
                "reading": reading,
            }
        )

    return pd.DataFrame(rows, columns=cols)


def summarize_sizing_candidate_compare(
    pair_compare: pd.DataFrame,
    pair_holdout_split: pd.DataFrame,
    context_compare: pd.DataFrame,
    context_holdout_split: pd.DataFrame,
    pure_test_compare: pd.DataFrame | None = None,
    pure_test_holdout_split: pd.DataFrame | None = None,
) -> pd.DataFrame:
    cols = [
        "candidate",
        "affected_hours",
        "affected_hour_share",
        "overall_cumulative_net_return",
        "overall_delta_vs_gate_pp",
        "max_drawdown",
        "target_conditional_return",
        "pure_test_hours",
        "pure_test_delta_pp",
        "test_validate_overlap_hours",
        "test_validate_overlap_delta_pp",
        "reading",
    ]

    def build_row(candidate: str, compare_df: pd.DataFrame, holdout_df: pd.DataFrame) -> dict:
        compare_map = compare_df.set_index("strategy").to_dict("index") if not compare_df.empty else {}
        gate_row = compare_map.get("avoid_fluctuating", {})
        cand_row = compare_map.get(candidate, {})
        holdout_map = holdout_df.set_index("split_mix").to_dict("index") if not holdout_df.empty else {}
        pure_test = holdout_map.get("test", {})
        overlap = holdout_map.get("test + validate", {})
        delta_vs_gate = np.nan
        if cand_row and gate_row:
            delta_vs_gate = float((cand_row.get("cumulative_net_return", np.nan) - gate_row.get("cumulative_net_return", np.nan)) * 100.0)
        return {
            "candidate": candidate,
            "affected_hours": cand_row.get("affected_hours", np.nan),
            "affected_hour_share": cand_row.get("affected_hour_share", np.nan),
            "overall_cumulative_net_return": cand_row.get("cumulative_net_return", np.nan),
            "overall_delta_vs_gate_pp": delta_vs_gate,
            "max_drawdown": cand_row.get("max_drawdown", np.nan),
            "target_conditional_return": cand_row.get("target_pair_conditional_return", np.nan),
            "pure_test_hours": pure_test.get("hours", np.nan),
            "pure_test_delta_pp": pure_test.get("delta_pp", np.nan),
            "test_validate_overlap_hours": overlap.get("hours", np.nan),
            "test_validate_overlap_delta_pp": overlap.get("delta_pp", np.nan),
            "reading": (
                "default_candidate"
                if candidate.endswith("pair_halfsize")
                else "pure_test_only_too_thin"
                if candidate.endswith("test_up_halfsize")
                else "narrower_but_thinner"
            ),
        }

    rows = [
        build_row("avoid_fluctuating_eth_sol_pair_halfsize", pair_compare, pair_holdout_split),
        build_row("avoid_fluctuating_eth_sol_test_validate_up_halfsize", context_compare, context_holdout_split),
    ]
    if pure_test_compare is not None and pure_test_holdout_split is not None:
        rows.append(build_row("avoid_fluctuating_eth_sol_test_up_halfsize", pure_test_compare, pure_test_holdout_split))
    return pd.DataFrame(rows, columns=cols)


def summarize_breakout_policy_admission_queue(
    pair_compare: pd.DataFrame,
    pair_regime_coverage_audit: pd.DataFrame,
    pair_pure_test_tail_summary: pd.DataFrame,
    pair_forward_blocks: pd.DataFrame,
    pair_forward_blocks_10d: pd.DataFrame,
    pair_down_overlay_summary: pd.DataFrame,
    pair_down_overlay_affected_hours: pd.DataFrame,
    pair_downflat_overlay_summary: pd.DataFrame,
    pair_downflat_overlay_affected_hours: pd.DataFrame,
    pair_downflat_overlay_tail_summary: pd.DataFrame,
    pair_downflat_overlay_forward_blocks: pd.DataFrame,
    pair_downflat_overlay_forward_blocks_10d: pd.DataFrame,
) -> pd.DataFrame:
    cols = [
        "policy",
        "reference_policy",
        "affected_hours",
        "overall_cumulative_net_return",
        "overall_delta_vs_reference_pp",
        "max_drawdown",
        "strict_tail_active_hours",
        "strict_tail_affected_hours",
        "strict_tail_delta_vs_reference_pp",
        "down_tail_gate_hours",
        "down_tail_affected_hours",
        "down_tail_coverage_share",
        "forward_5d_positive_blocks",
        "forward_5d_active_blocks",
        "forward_10d_positive_blocks",
        "forward_10d_active_blocks",
        "verdict",
        "reading",
    ]

    pair_map = pair_compare.set_index("strategy").to_dict("index") if not pair_compare.empty else {}
    gate_row = pair_map.get("avoid_fluctuating", {})
    pair_row = pair_map.get("avoid_fluctuating_eth_sol_pair_halfsize", {})
    down_coverage_map = pair_regime_coverage_audit.set_index("regime").to_dict("index") if not pair_regime_coverage_audit.empty else {}
    down_coverage_row = down_coverage_map.get("down", {})
    pair_tail_row = pair_pure_test_tail_summary.iloc[0] if not pair_pure_test_tail_summary.empty else {}
    downflat_tail_row = pair_downflat_overlay_tail_summary.iloc[0] if not pair_downflat_overlay_tail_summary.empty else {}
    downflat_row = pair_downflat_overlay_summary.iloc[0] if not pair_downflat_overlay_summary.empty else pd.Series(dtype=float)
    down_overlay_row = pair_down_overlay_summary.iloc[0] if not pair_down_overlay_summary.empty else pd.Series(dtype=float)
    gate_has = bool(gate_row)
    pair_has = bool(pair_row)
    pair_tail_has = not pair_pure_test_tail_summary.empty
    downflat_has = not pair_downflat_overlay_summary.empty
    down_overlay_has = not pair_down_overlay_summary.empty

    def block_counts(df: pd.DataFrame) -> tuple[float, float]:
        if df.empty:
            return np.nan, np.nan
        active = df.loc[df["affected_hours"].gt(0)].copy()
        if active.empty:
            return 0.0, 0.0
        positive = active.loc[active["delta_vs_gate_pp"].gt(0)].copy()
        return float(len(positive)), float(len(active))

    pair_5_pos, pair_5_active = block_counts(pair_forward_blocks)
    pair_10_pos, pair_10_active = block_counts(pair_forward_blocks_10d)
    downflat_5_pos, downflat_5_active = block_counts(pair_downflat_overlay_forward_blocks)
    downflat_10_pos, downflat_10_active = block_counts(pair_downflat_overlay_forward_blocks_10d)

    down_gate_hours = float(down_coverage_row.get("gate_active_hours", np.nan)) if down_coverage_row else np.nan
    pair_down_affected = float(down_coverage_row.get("policy_affected_hours", np.nan)) if down_coverage_row else np.nan
    down_overlay_affected = float(len(pair_down_overlay_affected_hours)) if pair_down_overlay_affected_hours is not None else np.nan
    down_overlay_coverage = np.nan
    if pd.notna(down_gate_hours) and down_gate_hours > 0 and pd.notna(down_overlay_affected):
        down_overlay_coverage = float(down_overlay_affected / down_gate_hours)

    rows = [
        {
            "policy": "avoid_fluctuating",
            "reference_policy": "raw_v0",
            "affected_hours": np.nan,
            "overall_cumulative_net_return": gate_row.get("cumulative_net_return", np.nan),
            "overall_delta_vs_reference_pp": np.nan,
            "max_drawdown": gate_row.get("max_drawdown", np.nan),
            "strict_tail_active_hours": np.nan,
            "strict_tail_affected_hours": np.nan,
            "strict_tail_delta_vs_reference_pp": np.nan,
            "down_tail_gate_hours": down_gate_hours,
            "down_tail_affected_hours": np.nan,
            "down_tail_coverage_share": np.nan,
            "forward_5d_positive_blocks": np.nan,
            "forward_5d_active_blocks": np.nan,
            "forward_10d_positive_blocks": np.nan,
            "forward_10d_active_blocks": np.nan,
            "verdict": "baseline_only",
            "reading": "先保留成 sizing 前基线；还没回答 admission honesty。",
        },
        {
            "policy": "avoid_fluctuating_eth_sol_pair_halfsize",
            "reference_policy": "avoid_fluctuating",
            "affected_hours": pair_row.get("affected_hours", np.nan),
            "overall_cumulative_net_return": pair_row.get("cumulative_net_return", np.nan),
            "overall_delta_vs_reference_pp": float((pair_row.get("cumulative_net_return", np.nan) - gate_row.get("cumulative_net_return", np.nan)) * 100.0) if gate_has and pair_has else np.nan,
            "max_drawdown": pair_row.get("max_drawdown", np.nan),
            "strict_tail_active_hours": pair_tail_row.get("active_hours", np.nan),
            "strict_tail_affected_hours": pair_tail_row.get("affected_hours", np.nan),
            "strict_tail_delta_vs_reference_pp": pair_tail_row.get("delta_vs_gate_pp", np.nan),
            "down_tail_gate_hours": down_gate_hours,
            "down_tail_affected_hours": pair_down_affected,
            "down_tail_coverage_share": down_coverage_row.get("policy_coverage_share", np.nan) if down_coverage_row else np.nan,
            "forward_5d_positive_blocks": pair_5_pos,
            "forward_5d_active_blocks": pair_5_active,
            "forward_10d_positive_blocks": pair_10_pos,
            "forward_10d_active_blocks": pair_10_active,
            "verdict": "keep_default_candidate",
            "reading": "默认主候选仍值得保留，但正式 verdict 仍是 one_more_gate。",
        },
        {
            "policy": "avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay",
            "reference_policy": "avoid_fluctuating_eth_sol_pair_halfsize",
            "affected_hours": float(len(pair_downflat_overlay_affected_hours)) if pair_downflat_overlay_affected_hours is not None else np.nan,
            "overall_cumulative_net_return": downflat_row.get("cumulative_net_return", np.nan),
            "overall_delta_vs_reference_pp": float((downflat_row.get("cumulative_net_return", np.nan) - pair_row.get("cumulative_net_return", np.nan)) * 100.0) if pair_has and downflat_has else np.nan,
            "max_drawdown": downflat_row.get("max_drawdown", np.nan),
            "strict_tail_active_hours": downflat_tail_row.get("active_hours", np.nan),
            "strict_tail_affected_hours": downflat_tail_row.get("affected_hours", np.nan),
            "strict_tail_delta_vs_reference_pp": downflat_tail_row.get("delta_vs_gate_pp", np.nan),
            "down_tail_gate_hours": down_gate_hours,
            "down_tail_affected_hours": 0.0,
            "down_tail_coverage_share": 0.0 if pd.notna(down_gate_hours) else np.nan,
            "forward_5d_positive_blocks": downflat_5_pos,
            "forward_5d_active_blocks": downflat_5_active,
            "forward_10d_positive_blocks": downflat_10_pos,
            "forward_10d_active_blocks": downflat_10_active,
            "verdict": "shadow_only_mixed_gate",
            "reading": "方向没死，但更诚实的位置只能写成 shadow-only mixed gate candidate。",
        },
        {
            "policy": "avoid_fluctuating_eth_sol_pair_halfsize_down_overlay",
            "reference_policy": "avoid_fluctuating_eth_sol_pair_halfsize",
            "affected_hours": down_overlay_affected,
            "overall_cumulative_net_return": down_overlay_row.get("cumulative_net_return", np.nan),
            "overall_delta_vs_reference_pp": float((down_overlay_row.get("cumulative_net_return", np.nan) - pair_row.get("cumulative_net_return", np.nan)) * 100.0) if pair_has and down_overlay_has else np.nan,
            "max_drawdown": down_overlay_row.get("max_drawdown", np.nan),
            "strict_tail_active_hours": pair_tail_row.get("active_hours", np.nan),
            "strict_tail_affected_hours": pair_tail_row.get("down_hours", np.nan),
            "strict_tail_delta_vs_reference_pp": 0.0 if pair_tail_has and pd.notna(pair_tail_row.get("down_hours", np.nan)) and float(pair_tail_row.get("down_hours", 0)) == 0 else np.nan,
            "down_tail_gate_hours": down_gate_hours,
            "down_tail_affected_hours": down_overlay_affected,
            "down_tail_coverage_share": down_overlay_coverage,
            "forward_5d_positive_blocks": np.nan,
            "forward_5d_active_blocks": np.nan,
            "forward_10d_positive_blocks": np.nan,
            "forward_10d_active_blocks": np.nan,
            "verdict": "reject_blunt_patch",
            "reading": "能补 pure-down 覆盖，但 current strict pure-test tail 仍 untouched，且 overall path 回落。",
        },
    ]
    return pd.DataFrame(rows, columns=cols)


def summarize_breakout_admission_gate_checklist(
    policy_admission_queue: pd.DataFrame,
    pair_pure_test_tail_checkpoints: pd.DataFrame,
) -> pd.DataFrame:
    cols = ["gate", "status", "key_numbers", "deployment_reading"]
    if policy_admission_queue is None or policy_admission_queue.empty:
        return pd.DataFrame(columns=cols)

    queue_map = policy_admission_queue.set_index("policy").to_dict("index")
    pair_row = queue_map.get("avoid_fluctuating_eth_sol_pair_halfsize", {})
    mixed_row = queue_map.get("avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay", {})
    down_row = queue_map.get("avoid_fluctuating_eth_sol_pair_halfsize_down_overlay", {})
    tail_ckpt_row = pd.Series(dtype=float)
    if pair_pure_test_tail_checkpoints is not None and not pair_pure_test_tail_checkpoints.empty:
        tail_ckpt_row = pair_pure_test_tail_checkpoints.sort_values("review_hours").iloc[-1]

    pair_overall_delta = pair_row.get("overall_delta_vs_reference_pp", np.nan)
    pair_dd_improve = np.nan
    if pd.notna(pair_row.get("max_drawdown", np.nan)) and pd.notna(queue_map.get("avoid_fluctuating", {}).get("max_drawdown", np.nan)):
        pair_dd_improve = float((pair_row.get("max_drawdown", np.nan) - queue_map.get("avoid_fluctuating", {}).get("max_drawdown", np.nan)) * 100.0)

    rows = [
        {
            "gate": "组合层 hourly path 是否已不是主 blocker",
            "status": "已过 first-pass",
            "key_numbers": f"default pair 相对 gate-only 累计 +{num(pair_overall_delta, 2)}pp；maxDD 改善 {num(pair_dd_improve, 2)}pp",
            "deployment_reading": "breakout 不再只是 per-asset 幻觉，可以继续沿 default pair 主候选看 admission。",
        },
        {
            "gate": "更长 forward honesty 是否已从 lucky patch 提高到 usable",
            "status": "usable 但未放行",
            "key_numbers": f"5d={int_str(pair_row.get('forward_5d_positive_blocks', 0))}/{int_str(pair_row.get('forward_5d_active_blocks', 0))}；10d={int_str(pair_row.get('forward_10d_positive_blocks', 0))}/{int_str(pair_row.get('forward_10d_active_blocks', 0))}",
            "deployment_reading": "一般性 late-segment 焦虑在下降，但这还不是 admission clearance。",
        },
        {
            "gate": "pure-test tail 自身是否已经够厚",
            "status": "仍偏薄",
            "key_numbers": f"strict tail={num(pair_row.get('strict_tail_delta_vs_reference_pp', np.nan), 2)}pp on {int_str(pair_row.get('strict_tail_affected_hours', 0))}/{int_str(pair_row.get('strict_tail_active_hours', 0))}h；pre-mixed {int_str(tail_ckpt_row.get('review_hours', np.nan), default='nan')}h={num(tail_ckpt_row.get('delta_vs_gate_pp', np.nan), 2)}pp on {int_str(tail_ckpt_row.get('affected_hours', np.nan), default='nan')}h",
            "deployment_reading": "前半段 pure-test 仍更像“没翻负”，还不足以单独解除 one_more_gate。",
        },
        {
            "gate": "down-tail coverage hard gap 是否已补上",
            "status": "硬缺口未补",
            "key_numbers": f"{int_str(pair_row.get('down_tail_affected_hours', 0))}/{int_str(pair_row.get('down_tail_gate_hours', 0))} = {pct(pair_row.get('down_tail_coverage_share', np.nan))}",
            "deployment_reading": "这是 breakout 当前最硬的 blocker；不是 wording 问题。",
        },
        {
            "gate": "mixed-tail overlay 能否直接改写 verdict",
            "status": "shadow-only",
            "key_numbers": f"strict tail={num(mixed_row.get('strict_tail_delta_vs_reference_pp', np.nan), 2)}pp；5d={int_str(mixed_row.get('forward_5d_positive_blocks', 0))}/{int_str(mixed_row.get('forward_5d_active_blocks', 0))}；10d={int_str(mixed_row.get('forward_10d_positive_blocks', 0))}/{int_str(mixed_row.get('forward_10d_active_blocks', 0))}",
            "deployment_reading": "它可以继续当附加 gate 观察项，但还不能替代 default pair 主候选。",
        },
        {
            "gate": "blunt pure-down patch 能否当现成补丁",
            "status": "reject",
            "key_numbers": f"coverage={int_str(down_row.get('down_tail_affected_hours', 0))}/{int_str(down_row.get('down_tail_gate_hours', 0))}；overall delta={num(down_row.get('overall_delta_vs_reference_pp', np.nan), 2)}pp",
            "deployment_reading": "说明 blocker 虽然像 down-tail，却不能靠 pure-down 一刀切机械解除。",
        },
        {
            "gate": "最终 deployment verdict",
            "status": "one_more_gate",
            "key_numbers": "keep default pair / mixed-tail 仅 shadow-only / blunt pure-down reject",
            "deployment_reading": "还能继续推 breakout，但默认只该沿 default pair 主候选推进。",
        },
    ]
    return pd.DataFrame(rows, columns=cols)


def summarize_breakout_gate_clearance_protocol(
    policy_admission_queue: pd.DataFrame,
    pair_downflat_overlay_tail_blocks: pd.DataFrame,
) -> pd.DataFrame:
    cols = [
        "lane",
        "current_status",
        "clear_to_next_step_if",
        "stay_blocked_if",
        "park_or_reject_if",
    ]
    if policy_admission_queue is None or policy_admission_queue.empty:
        return pd.DataFrame(columns=cols)

    queue_map = policy_admission_queue.set_index("policy").to_dict("index")
    pair_row = queue_map.get("avoid_fluctuating_eth_sol_pair_halfsize", {})
    mixed_row = queue_map.get("avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay", {})
    down_row = queue_map.get("avoid_fluctuating_eth_sol_pair_halfsize_down_overlay", {})

    mixed_tail_active = pd.DataFrame()
    if pair_downflat_overlay_tail_blocks is not None and not pair_downflat_overlay_tail_blocks.empty and "affected_hours" in pair_downflat_overlay_tail_blocks.columns:
        mixed_tail_active = pair_downflat_overlay_tail_blocks.loc[pair_downflat_overlay_tail_blocks["affected_hours"].gt(0)].copy()
    mixed_tail_pos = int(mixed_tail_active["delta_vs_gate_pp"].gt(0).sum()) if not mixed_tail_active.empty else 0
    mixed_tail_active_count = int(len(mixed_tail_active)) if not mixed_tail_active.empty else 0

    rows = [
        {
            "lane": "default pair halfsize（主候选）",
            "current_status": "keep default candidate / one_more_gate",
            "clear_to_next_step_if": (
                f"后续更前瞻的 shadow/holdout 终于命中 pure down 小时（当前仅 {int_str(pair_row.get('down_tail_affected_hours', 0))}/{int_str(pair_row.get('down_tail_gate_hours', 0))}），"
                "且同一段 pure-test / down-tail 读法仍不翻负。"
            ),
            "stay_blocked_if": (
                f"strict pure-test 仍只像现在这样约 {num(pair_row.get('strict_tail_delta_vs_reference_pp', np.nan), 2)}pp on "
                f"{int(pair_row.get('strict_tail_affected_hours', 0))}/{int(pair_row.get('strict_tail_active_hours', 0))}h，"
                f"同时 pure down coverage 继续停在 {int(pair_row.get('down_tail_affected_hours', 0))}/{int(pair_row.get('down_tail_gate_hours', 0))}。"
            ),
            "park_or_reject_if": "若后续新增的 pure-test / down-tail slice 自身翻负，而 mixed-tail 也守不住，就该考虑 park，而不是继续补近义 wording。",
        },
        {
            "lane": "down+flat mixed-tail overlay（紧邻子点）",
            "current_status": "shadow-only mixed gate",
            "clear_to_next_step_if": (
                f"target mixed-tail pocket 自身不再给 split verdict：至少 forward blocks 不再停在当前 5d={int(mixed_row.get('forward_5d_positive_blocks', 0))}/{int(mixed_row.get('forward_5d_active_blocks', 0))}、"
                f"10d={int(mixed_row.get('forward_10d_positive_blocks', 0))}/{int(mixed_row.get('forward_10d_active_blocks', 0))}，"
                f"且 strict-tail 6h blocks 也不再只是 {mixed_tail_pos}/{mixed_tail_active_count} 为正。"
            ),
            "stay_blocked_if": "只要它仍主要靠单段 mixed tail / train carry，或 non-overlap blocks 继续正负对半开，就继续只配 shadow-only。",
            "park_or_reject_if": "若更长一点的 forward / conditional pocket 也持续转弱，就不该再把它当 admission clearance 候选。",
        },
        {
            "lane": "blunt pure-down overlay（反向 sanity check）",
            "current_status": "reject blunt patch",
            "clear_to_next_step_if": "默认不重开；除非未来出现更细的 down-tail protection，既能补 coverage，又不拖累 default pair 的 overall path。",
            "stay_blocked_if": (
                f"只要结果还像当前这样 coverage={int(down_row.get('down_tail_affected_hours', 0))}/{int(down_row.get('down_tail_gate_hours', 0))}，"
                f"但 overall delta={num(down_row.get('overall_delta_vs_reference_pp', np.nan), 2)}pp 为负，它就不是 admission 补丁。"
            ),
            "park_or_reject_if": "继续留作 reject sanity check，不再抢主资源。",
        },
        {
            "lane": "整条 breakout 线",
            "current_status": "continue, but only via default pair main lane",
            "clear_to_next_step_if": "下一次若能把主候选推进到更接近 shadow / paper admission，就该优先交真正命中 pure-test/down-tail 的前瞻证据，而不是再新增 board 近义层。",
            "stay_blocked_if": "如果新增工作仍主要只是 mixed-tail wording、近义 checklist，或不触及 pure-test / down-tail honesty，正式 verdict 继续维持 one_more_gate。",
            "park_or_reject_if": "若主候选后续连 pure-test / down-tail 也守不住，就该明确转 park，而不是无限续命。",
        },
    ]
    return pd.DataFrame(rows, columns=cols)


def load_optional_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def render_page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(title)}</title>
  <style>
    :root {{
      --bg: #f5f1e8;
      --paper: #fffdf8;
      --ink: #18212b;
      --muted: #5c6773;
      --line: #d7cfc0;
      --teal: #0f766e;
      --amber: #b45309;
      --rose: #b91c1c;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Iowan Old Style","Palatino Linotype","Noto Serif SC",serif;
      background:
        radial-gradient(circle at top left, rgba(15,118,110,0.08), transparent 24%),
        radial-gradient(circle at top right, rgba(180,83,9,0.09), transparent 22%),
        linear-gradient(180deg, #f7f3ea 0%, #efe8dc 100%);
      color: var(--ink);
      line-height: 1.68;
    }}
    main {{
      max-width: 1080px;
      margin: 0 auto;
      padding: 28px 18px 56px;
    }}
    .hero {{
      background: rgba(255,253,248,0.86);
      backdrop-filter: blur(6px);
      border: 1px solid rgba(215,207,192,0.9);
      border-radius: 22px;
      padding: 26px 24px 18px;
      box-shadow: 0 16px 36px rgba(24,33,43,0.08);
    }}
    .hero h1 {{ margin: 0 0 8px; font-size: 2rem; line-height: 1.2; }}
    .muted {{ color: var(--muted); }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin: 18px 0 10px;
    }}
    .card {{
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 14px 16px;
      box-shadow: 0 10px 24px rgba(24,33,43,0.05);
    }}
    .card .k {{ font-size: 0.88rem; color: var(--muted); }}
    .card .v {{ font-size: 1.45rem; font-weight: 700; margin-top: 6px; }}
    section {{
      margin-top: 18px;
      background: rgba(255,253,248,0.88);
      border: 1px solid rgba(215,207,192,0.95);
      border-radius: 22px;
      padding: 18px 20px;
      box-shadow: 0 10px 28px rgba(24,33,43,0.05);
    }}
    h2 {{ margin: 0 0 10px; font-size: 1.18rem; }}
    ul {{ margin: 0; padding-left: 20px; }}
    li + li {{ margin-top: 6px; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 10px;
      font-size: 0.95rem;
      background: #fff;
    }}
    th, td {{
      border: 1px solid #e5dfd2;
      padding: 8px 9px;
      text-align: left;
      vertical-align: top;
    }}
    th {{ background: #f4ede1; }}
    code {{
      background: #f0ebe2;
      padding: 2px 6px;
      border-radius: 6px;
      font-family: ui-monospace,SFMono-Regular,Menlo,monospace;
      font-size: 0.92em;
    }}
    .note {{
      border-left: 4px solid var(--amber);
      padding-left: 12px;
      color: var(--muted);
    }}
    img {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 16px;
      margin-top: 10px;
      background: #fff;
    }}
    .good {{ color: var(--teal); }}
    .bad {{ color: var(--rose); }}
    @media (max-width: 720px) {{
      main {{ padding: 18px 12px 40px; }}
      .hero h1 {{ font-size: 1.65rem; }}
    }}
  </style>
</head>
<body>
  <main>{body}</main>
</body>
</html>
"""


def regime_blurb(df: pd.DataFrame) -> str:
    if df.empty:
        return "暂无 regime 数据。"
    best = df.sort_values("mean_return", ascending=False).iloc[0]
    worst = df.sort_values("mean_return", ascending=True).iloc[0]
    return f"最好的是 {best['regime']} 行情（平均单笔 {pct(best['mean_return'])}），最弱的是 {worst['regime']} 行情（平均单笔 {pct(worst['mean_return'])}）。"


def build_v0_report(
    result: StrategyResult,
    report_path: Path,
    confirm_compare: pd.DataFrame | None = None,
    gate_compare: pd.DataFrame | None = None,
    hourly_portfolio_summary: pd.DataFrame | None = None,
    hourly_split_summary: pd.DataFrame | None = None,
    hourly_regime_summary: pd.DataFrame | None = None,
    gate_hourly_split_summary: pd.DataFrame | None = None,
    gate_hourly_regime_summary: pd.DataFrame | None = None,
    hourly_active_bucket_compare: pd.DataFrame | None = None,
    hourly_two_position_symbol_mix_compare: pd.DataFrame | None = None,
    hourly_two_position_pair_context_compare: pd.DataFrame | None = None,
    pair_sizing_compare: pd.DataFrame | None = None,
    pair_sizing_affected_hours: pd.DataFrame | None = None,
    sizing_candidate_compare: pd.DataFrame | None = None,
    pair_walkforward_windows: pd.DataFrame | None = None,
    pair_forward_blocks: pd.DataFrame | None = None,
    pair_forward_blocks_10d: pd.DataFrame | None = None,
    pair_shadow_checkpoints: pd.DataFrame | None = None,
    pair_pure_test_tail_summary: pd.DataFrame | None = None,
    pair_pure_test_tail_checkpoints: pd.DataFrame | None = None,
    pair_pure_test_tail_blocks: pd.DataFrame | None = None,
    pair_sizing_holdout_regime: pd.DataFrame | None = None,
    pair_sizing_holdout_split_regime: pd.DataFrame | None = None,
    pair_default_episode_summary: pd.DataFrame | None = None,
    pair_down_overlay_summary: pd.DataFrame | None = None,
    pair_down_overlay_affected_hours: pd.DataFrame | None = None,
    pair_downflat_overlay_summary: pd.DataFrame | None = None,
    pair_downflat_overlay_holdout_split: pd.DataFrame | None = None,
    pair_downflat_overlay_episode_summary: pd.DataFrame | None = None,
    pair_downflat_overlay_tail_summary: pd.DataFrame | None = None,
    pair_downflat_overlay_tail_checkpoints: pd.DataFrame | None = None,
    pair_downflat_overlay_tail_blocks: pd.DataFrame | None = None,
    pair_downflat_overlay_walkforward_windows: pd.DataFrame | None = None,
    pair_downflat_overlay_forward_blocks: pd.DataFrame | None = None,
    pair_downflat_overlay_forward_blocks_10d: pd.DataFrame | None = None,
    pair_downflat_overlay_shadow_checkpoints: pd.DataFrame | None = None,
    policy_admission_queue: pd.DataFrame | None = None,
    admission_gate_checklist: pd.DataFrame | None = None,
    gate_clearance_protocol: pd.DataFrame | None = None,
    pair_predown_bridge_audit: pd.DataFrame | None = None,
    downrisk_zone_audit_compare: pd.DataFrame | None = None,
    future_pure_down_lead_audit_compare: pd.DataFrame | None = None,
) -> None:
    summary = result.summary.iloc[0]
    cost_tbl = cost_sensitivity_table(result.trades, cost_bps_list=[0, 10, 20, 50])
    split_20_tbl = context_net_table(result.trades, group_col="split", cost_bps=20)
    regime_20_tbl = context_net_table(result.trades, group_col="regime", cost_bps=20)
    regime_policy_oos_tbl = load_optional_csv(REGIME_POLICY_OOS_PATH)
    overlap_summary_tbl, overlap_profile_tbl = overlap_summary_table(result.trades)
    capital_alloc_tbl, capital_alloc_selected_tbl, capital_alloc_equal_weight_tbl = capital_allocation_first_pass(result.trades, cost_bps_list=[0, 20])
    overlap_summary = overlap_summary_tbl.iloc[0] if not overlap_summary_tbl.empty else None
    overall_20 = cost_tbl[cost_tbl["cost_bps"] == 20].iloc[0] if not cost_tbl.empty else None
    split_20_map = split_20_tbl.set_index("split").to_dict("index") if not split_20_tbl.empty else {}
    regime_20_map = regime_20_tbl.set_index("regime").to_dict("index") if not regime_20_tbl.empty else {}
    regime_policy_map = regime_policy_oos_tbl.set_index("policy").to_dict("index") if not regime_policy_oos_tbl.empty else {}
    capital_alloc_map = {(row["mode"], int(row["cost_bps"])): row for _, row in capital_alloc_tbl.iterrows()} if not capital_alloc_tbl.empty else {}
    slot20 = capital_alloc_map.get(("1_slot_global", 20))
    indep20 = capital_alloc_map.get(("per_asset_independent", 20))
    eq20 = capital_alloc_map.get(("equal_weight_concurrent_entry", 20))
    cost_tbl_display = cost_tbl.copy()
    split_20_tbl_display = split_20_tbl.copy()
    regime_20_tbl_display = regime_20_tbl.copy()
    regime_policy_display = regime_policy_oos_tbl.copy()
    overlap_summary_display = overlap_summary_tbl.copy()
    overlap_profile_display = overlap_profile_tbl.copy()
    capital_alloc_display = capital_alloc_tbl.copy()
    capital_alloc_selected_display = capital_alloc_selected_tbl.copy()
    capital_alloc_equal_weight_display = capital_alloc_equal_weight_tbl.copy()
    confirm_compare_display = confirm_compare.copy() if confirm_compare is not None else pd.DataFrame()
    gate_compare_display = gate_compare.copy() if gate_compare is not None else pd.DataFrame()
    hourly_portfolio_summary_display = hourly_portfolio_summary.copy() if hourly_portfolio_summary is not None else pd.DataFrame()
    hourly_split_summary_display = hourly_split_summary.copy() if hourly_split_summary is not None else pd.DataFrame()
    hourly_regime_summary_display = hourly_regime_summary.copy() if hourly_regime_summary is not None else pd.DataFrame()
    gate_hourly_split_summary_display = gate_hourly_split_summary.copy() if gate_hourly_split_summary is not None else pd.DataFrame()
    gate_hourly_regime_summary_display = gate_hourly_regime_summary.copy() if gate_hourly_regime_summary is not None else pd.DataFrame()
    hourly_active_bucket_compare_display = hourly_active_bucket_compare.copy() if hourly_active_bucket_compare is not None else pd.DataFrame()
    hourly_two_position_symbol_mix_compare_display = hourly_two_position_symbol_mix_compare.copy() if hourly_two_position_symbol_mix_compare is not None else pd.DataFrame()
    hourly_two_position_pair_context_compare_display = hourly_two_position_pair_context_compare.copy() if hourly_two_position_pair_context_compare is not None else pd.DataFrame()
    pair_sizing_compare_display = pair_sizing_compare.copy() if pair_sizing_compare is not None else pd.DataFrame()
    pair_sizing_affected_hours_display = pair_sizing_affected_hours.copy() if pair_sizing_affected_hours is not None else pd.DataFrame()
    sizing_candidate_compare_display = sizing_candidate_compare.copy() if sizing_candidate_compare is not None else pd.DataFrame()
    pair_walkforward_windows_display = pair_walkforward_windows.copy() if pair_walkforward_windows is not None else pd.DataFrame()
    pair_forward_blocks_display = pair_forward_blocks.copy() if pair_forward_blocks is not None else pd.DataFrame()
    pair_forward_blocks_10d_display = pair_forward_blocks_10d.copy() if pair_forward_blocks_10d is not None else pd.DataFrame()
    pair_shadow_checkpoints_display = pair_shadow_checkpoints.copy() if pair_shadow_checkpoints is not None else pd.DataFrame()
    pair_pure_test_tail_summary_display = pair_pure_test_tail_summary.copy() if pair_pure_test_tail_summary is not None else pd.DataFrame()
    pair_pure_test_tail_checkpoints_display = pair_pure_test_tail_checkpoints.copy() if pair_pure_test_tail_checkpoints is not None else pd.DataFrame()
    pair_pure_test_tail_blocks_display = pair_pure_test_tail_blocks.copy() if pair_pure_test_tail_blocks is not None else pd.DataFrame()
    pair_default_episode_summary_display = pair_default_episode_summary.copy() if pair_default_episode_summary is not None else pd.DataFrame()
    policy_admission_queue_display = policy_admission_queue.copy() if policy_admission_queue is not None else pd.DataFrame()
    admission_gate_checklist_display = admission_gate_checklist.copy() if admission_gate_checklist is not None else pd.DataFrame()
    gate_clearance_protocol_display = gate_clearance_protocol.copy() if gate_clearance_protocol is not None else pd.DataFrame()
    pair_predown_bridge_audit_display = pair_predown_bridge_audit.copy() if pair_predown_bridge_audit is not None else pd.DataFrame()
    downrisk_zone_audit_compare_display = downrisk_zone_audit_compare.copy() if downrisk_zone_audit_compare is not None else pd.DataFrame()
    future_pure_down_lead_audit_compare_display = future_pure_down_lead_audit_compare.copy() if future_pure_down_lead_audit_compare is not None else pd.DataFrame()
    pair_sizing_holdout_regime_display = pair_sizing_holdout_regime.copy() if pair_sizing_holdout_regime is not None else pd.DataFrame()
    pair_sizing_holdout_split_regime_display = pair_sizing_holdout_split_regime.copy() if pair_sizing_holdout_split_regime is not None else pd.DataFrame()
    pair_down_overlay_summary_display = pair_down_overlay_summary.copy() if pair_down_overlay_summary is not None else pd.DataFrame()
    pair_down_overlay_affected_hours_display = pair_down_overlay_affected_hours.copy() if pair_down_overlay_affected_hours is not None else pd.DataFrame()
    pair_downflat_overlay_summary_display = pair_downflat_overlay_summary.copy() if pair_downflat_overlay_summary is not None else pd.DataFrame()
    pair_downflat_overlay_holdout_split_display = pair_downflat_overlay_holdout_split.copy() if pair_downflat_overlay_holdout_split is not None else pd.DataFrame()
    pair_downflat_overlay_episode_summary_display = pair_downflat_overlay_episode_summary.copy() if pair_downflat_overlay_episode_summary is not None else pd.DataFrame()
    pair_downflat_overlay_tail_summary_display = pair_downflat_overlay_tail_summary.copy() if pair_downflat_overlay_tail_summary is not None else pd.DataFrame()
    pair_downflat_overlay_tail_checkpoints_display = pair_downflat_overlay_tail_checkpoints.copy() if pair_downflat_overlay_tail_checkpoints is not None else pd.DataFrame()
    pair_downflat_overlay_tail_blocks_display = pair_downflat_overlay_tail_blocks.copy() if pair_downflat_overlay_tail_blocks is not None else pd.DataFrame()
    pair_downflat_overlay_walkforward_windows_display = pair_downflat_overlay_walkforward_windows.copy() if pair_downflat_overlay_walkforward_windows is not None else pd.DataFrame()
    pair_downflat_overlay_forward_blocks_display = pair_downflat_overlay_forward_blocks.copy() if pair_downflat_overlay_forward_blocks is not None else pd.DataFrame()
    pair_downflat_overlay_forward_blocks_10d_display = pair_downflat_overlay_forward_blocks_10d.copy() if pair_downflat_overlay_forward_blocks_10d is not None else pd.DataFrame()
    pair_downflat_overlay_shadow_checkpoints_display = pair_downflat_overlay_shadow_checkpoints.copy() if pair_downflat_overlay_shadow_checkpoints is not None else pd.DataFrame()
    if not policy_admission_queue_display.empty:
        policy_admission_queue_display["policy"] = policy_admission_queue_display["policy"].replace({
            "avoid_fluctuating": "gate-only baseline",
            "avoid_fluctuating_eth_sol_pair_halfsize": "default pair halfsize",
            "avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay": "pair + down+flat mixed-tail overlay",
            "avoid_fluctuating_eth_sol_pair_halfsize_down_overlay": "pair + blunt pure-down overlay",
        })
        policy_admission_queue_display["reference_policy"] = policy_admission_queue_display["reference_policy"].replace({
            "raw_v0": "raw_v0",
            "avoid_fluctuating": "gate-only baseline",
            "avoid_fluctuating_eth_sol_pair_halfsize": "default pair halfsize",
        })
        policy_admission_queue_display["verdict"] = policy_admission_queue_display["verdict"].replace({
            "baseline_only": "baseline only",
            "keep_default_candidate": "keep / default candidate",
            "shadow_only_mixed_gate": "shadow-only mixed gate",
            "reject_blunt_patch": "reject blunt patch",
        })
        for col in [
            "affected_hours",
            "strict_tail_active_hours",
            "strict_tail_affected_hours",
            "down_tail_gate_hours",
            "down_tail_affected_hours",
            "forward_5d_positive_blocks",
            "forward_5d_active_blocks",
            "forward_10d_positive_blocks",
            "forward_10d_active_blocks",
        ]:
            if col in policy_admission_queue_display.columns:
                policy_admission_queue_display[col] = policy_admission_queue_display[col].map(lambda x: "-" if pd.isna(x) else str(int(x)))
        policy_admission_queue_display = policy_admission_queue_display.rename(columns={
            "policy": "policy",
            "reference_policy": "对照基线",
            "affected_hours": "受影响小时",
            "overall_cumulative_net_return": "overall累计",
            "overall_delta_vs_reference_pp": "相对对照delta(pp)",
            "max_drawdown": "最大回撤",
            "strict_tail_active_hours": "strict tail总小时",
            "strict_tail_affected_hours": "strict tail命中小时",
            "strict_tail_delta_vs_reference_pp": "strict tail delta(pp)",
            "down_tail_gate_hours": "down-tail总小时",
            "down_tail_affected_hours": "down-tail命中小时",
            "down_tail_coverage_share": "down-tail覆盖率",
            "forward_5d_positive_blocks": "5d正向块",
            "forward_5d_active_blocks": "5d活跃块",
            "forward_10d_positive_blocks": "10d正向块",
            "forward_10d_active_blocks": "10d活跃块",
            "verdict": "当前verdict",
            "reading": "一句话读法",
        })
    if not admission_gate_checklist_display.empty:
        admission_gate_checklist_display = admission_gate_checklist_display.rename(columns={
            "gate": "gate",
            "status": "当前状态",
            "key_numbers": "关键证据",
            "deployment_reading": "deployment 读法",
        })
    if not gate_clearance_protocol_display.empty:
        gate_clearance_protocol_display = gate_clearance_protocol_display.rename(columns={
            "lane": "lane",
            "current_status": "当前位置",
            "clear_to_next_step_if": "什么情况下才算能往下一步走",
            "stay_blocked_if": "什么情况下继续卡住",
            "park_or_reject_if": "什么情况下该 park / reject",
        })
    if not pair_predown_bridge_audit_display.empty:
        for col in ["bridge_start", "bridge_end"]:
            if col in pair_predown_bridge_audit_display.columns:
                pair_predown_bridge_audit_display[col] = pd.to_datetime(pair_predown_bridge_audit_display[col], utc=True).dt.strftime("%Y-%m-%d %H:%M")
        for col in ["lead_hours", "bridge_hours", "affected_hours", "lead_to_first_down_min", "lead_to_first_down_max"]:
            if col in pair_predown_bridge_audit_display.columns:
                pair_predown_bridge_audit_display[col] = pair_predown_bridge_audit_display[col].map(lambda x: "-" if pd.isna(x) else str(int(x)))
        pair_predown_bridge_audit_display = pair_predown_bridge_audit_display.rename(columns={
            "lead_hours": "预看窗口(h)",
            "bridge_start": "bridge开始",
            "bridge_end": "bridge结束",
            "bridge_hours": "bridge小时",
            "affected_hours": "命中小时",
            "coverage_share": "bridge覆盖率",
            "lead_to_first_down_min": "距首个pure-down最短(h)",
            "lead_to_first_down_max": "距首个pure-down最长(h)",
            "split_mix_values": "split",
            "regime_mix_values": "regime",
            "gate_cumulative_net_return": "gate累计",
            "conditioned_cumulative_net_return": "default pair累计",
            "delta_vs_gate_pp": "相对gate delta(pp)",
            "reading": "一句话读法",
        })
    if not downrisk_zone_audit_compare_display.empty:
        downrisk_zone_audit_compare_display["policy"] = downrisk_zone_audit_compare_display["policy"].replace({
            "default_pair_halfsize": "default pair halfsize",
            "downflat_mixed_tail_overlay": "down+flat mixed-tail overlay",
        })
        downrisk_zone_audit_compare_display["reference_policy"] = downrisk_zone_audit_compare_display["reference_policy"].replace({
            "gate_only": "gate-only",
            "default_pair_halfsize": "default pair halfsize",
        })
        for col in [
            "lead_hours",
            "pure_down_hours",
            "bridge_hours",
            "risk_zone_hours",
            "affected_total_hours",
            "affected_pure_down_hours",
            "affected_bridge_hours",
        ]:
            if col in downrisk_zone_audit_compare_display.columns:
                downrisk_zone_audit_compare_display[col] = downrisk_zone_audit_compare_display[col].map(lambda x: "-" if pd.isna(x) else str(int(x)))
        downrisk_zone_audit_compare_display = downrisk_zone_audit_compare_display.rename(columns={
            "policy": "policy",
            "reference_policy": "对照基线",
            "lead_hours": "预看窗口(h)",
            "pure_down_hours": "pure-down小时",
            "bridge_hours": "bridge小时",
            "risk_zone_hours": "risk-zone小时",
            "affected_total_hours": "risk-zone命中小时",
            "affected_pure_down_hours": "命中的pure-down小时",
            "affected_bridge_hours": "命中的bridge小时",
            "coverage_share": "risk-zone覆盖率",
            "pure_down_coverage_share": "pure-down覆盖率",
            "bridge_coverage_share": "bridge覆盖率",
            "base_cumulative_net_return": "对照累计",
            "conditioned_cumulative_net_return": "policy累计",
            "delta_vs_reference_pp": "相对对照delta(pp)",
            "reading": "一句话读法",
        })
    if not future_pure_down_lead_audit_compare_display.empty:
        future_pure_down_lead_audit_compare_display["policy"] = future_pure_down_lead_audit_compare_display["policy"].replace({
            "default_pair_halfsize": "default pair halfsize",
            "downflat_mixed_tail_overlay": "down+flat mixed-tail overlay",
        })
        future_pure_down_lead_audit_compare_display["reference_policy"] = future_pure_down_lead_audit_compare_display["reference_policy"].replace({
            "gate_only": "gate-only",
            "default_pair_halfsize": "default pair halfsize",
        })
        for col in [
            "future_window_hours",
            "policy_affected_hours",
            "matched_hours",
            "matched_test_hours",
            "matched_train_overlap_hours",
            "closest_lead_h",
            "median_lead_h",
            "furthest_lead_h",
        ]:
            if col in future_pure_down_lead_audit_compare_display.columns:
                future_pure_down_lead_audit_compare_display[col] = future_pure_down_lead_audit_compare_display[col].map(lambda x: "-" if pd.isna(x) else str(int(round(float(x)))))
        future_pure_down_lead_audit_compare_display = future_pure_down_lead_audit_compare_display.rename(columns={
            "policy": "policy",
            "reference_policy": "对照基线",
            "future_window_hours": "未来窗口(h)",
            "policy_affected_hours": "policy受影响小时",
            "matched_hours": "未来会接上pure-down的小时",
            "matched_share": "命中占比",
            "matched_test_hours": "其中test小时",
            "matched_train_overlap_hours": "其中train/overlap小时",
            "closest_lead_h": "最近lead(h)",
            "median_lead_h": "中位lead(h)",
            "furthest_lead_h": "最远lead(h)",
            "split_mix_values": "split",
            "regime_mix_values": "regime",
            "reading": "一句话读法",
        })
    for df in [cost_tbl_display, split_20_tbl_display, regime_20_tbl_display]:
        if not df.empty and "trades" in df.columns:
            df["trades"] = df["trades"].astype(int).astype(str)
    if not cost_tbl_display.empty:
        cost_tbl_display["cost_bps"] = cost_tbl_display["cost_bps"].astype(int).astype(str)
    if not regime_policy_display.empty:
        for col in ["oos_events", "oos_neg_symbols_excess", "oos_pos_symbols_excess"]:
            if col in regime_policy_display.columns:
                regime_policy_display[col] = regime_policy_display[col].astype(int).astype(str)
    if not overlap_summary_display.empty:
        for col in ["trades", "assets", "max_concurrent_positions"]:
            overlap_summary_display[col] = overlap_summary_display[col].astype(int).astype(str)
    if not overlap_profile_display.empty:
        overlap_profile_display["concurrent_positions"] = overlap_profile_display["concurrent_positions"].astype(int).astype(str)
    if not capital_alloc_display.empty:
        for col in ["cost_bps", "trades", "skipped_due_to_overlap"]:
            capital_alloc_display[col] = capital_alloc_display[col].astype(int).astype(str)
    if not capital_alloc_selected_display.empty:
        capital_alloc_selected_display["entry_timestamp"] = pd.to_datetime(capital_alloc_selected_display["entry_timestamp"], utc=True).dt.strftime("%Y-%m-%d %H:%M")
        capital_alloc_selected_display["exit_timestamp"] = pd.to_datetime(capital_alloc_selected_display["exit_timestamp"], utc=True).dt.strftime("%Y-%m-%d %H:%M")
    if not capital_alloc_equal_weight_display.empty:
        capital_alloc_equal_weight_display["entry_timestamp"] = pd.to_datetime(capital_alloc_equal_weight_display["entry_timestamp"], utc=True).dt.strftime("%Y-%m-%d %H:%M")
        capital_alloc_equal_weight_display["exit_timestamp"] = pd.to_datetime(capital_alloc_equal_weight_display["exit_timestamp"], utc=True).dt.strftime("%Y-%m-%d %H:%M")
        capital_alloc_equal_weight_display["entry_concurrent_positions"] = capital_alloc_equal_weight_display["entry_concurrent_positions"].astype(int).astype(str)
    if not confirm_compare_display.empty:
        confirm_compare_display["trades"] = confirm_compare_display["trades"].astype(int).astype(str)
    if not gate_compare_display.empty:
        gate_compare_display["trades"] = gate_compare_display["trades"].astype(int).astype(str)
    if not hourly_portfolio_summary_display.empty:
        for col in ["cost_bps", "active_hours", "max_active_positions"]:
            if col in hourly_portfolio_summary_display.columns:
                hourly_portfolio_summary_display[col] = hourly_portfolio_summary_display[col].astype(int).astype(str)
    for df in [hourly_split_summary_display, hourly_regime_summary_display, gate_hourly_split_summary_display, gate_hourly_regime_summary_display]:
        if not df.empty:
            for col in ["cost_bps", "active_hours", "max_active_positions"]:
                if col in df.columns:
                    df[col] = df[col].astype(int).astype(str)
    if not hourly_active_bucket_compare_display.empty:
        for col in ["active_positions", "hours"]:
            if col in hourly_active_bucket_compare_display.columns:
                hourly_active_bucket_compare_display[col] = hourly_active_bucket_compare_display[col].astype(int).astype(str)
    if not hourly_two_position_symbol_mix_compare_display.empty:
        for col in ["active_positions", "hours"]:
            if col in hourly_two_position_symbol_mix_compare_display.columns:
                hourly_two_position_symbol_mix_compare_display[col] = hourly_two_position_symbol_mix_compare_display[col].astype(int).astype(str)
    if not hourly_two_position_pair_context_compare_display.empty:
        for col in ["active_positions", "hours"]:
            if col in hourly_two_position_pair_context_compare_display.columns:
                hourly_two_position_pair_context_compare_display[col] = hourly_two_position_pair_context_compare_display[col].astype(int).astype(str)
    if not pair_sizing_compare_display.empty:
        for col in ["active_hours", "max_active_positions", "affected_hours"]:
            if col in pair_sizing_compare_display.columns:
                pair_sizing_compare_display[col] = pair_sizing_compare_display[col].map(lambda x: "-" if pd.isna(x) else str(int(x)))
    if not pair_sizing_affected_hours_display.empty:
        pair_sizing_affected_hours_display["timestamp"] = pd.to_datetime(pair_sizing_affected_hours_display["timestamp"], utc=True).dt.strftime("%Y-%m-%d %H:%M")
    if not sizing_candidate_compare_display.empty:
        sizing_candidate_compare_display["candidate"] = sizing_candidate_compare_display["candidate"].replace({
            "avoid_fluctuating_eth_sol_pair_halfsize": "ETH+SOL pair halfsize",
            "avoid_fluctuating_eth_sol_test_validate_up_halfsize": "ETH+SOL test+validate×up context halfsize",
            "avoid_fluctuating_eth_sol_test_up_halfsize": "ETH+SOL pure-test×up context halfsize",
        })
        for col in ["affected_hours", "pure_test_hours", "test_validate_overlap_hours"]:
            if col in sizing_candidate_compare_display.columns:
                sizing_candidate_compare_display[col] = sizing_candidate_compare_display[col].map(lambda x: "-" if pd.isna(x) else str(int(x)))
    if not pair_walkforward_windows_display.empty:
        for col in ["window_start", "window_end"]:
            if col in pair_walkforward_windows_display.columns:
                pair_walkforward_windows_display[col] = pd.to_datetime(pair_walkforward_windows_display[col], utc=True).dt.strftime("%Y-%m-%d")
        for col in ["active_hours", "affected_hours"]:
            if col in pair_walkforward_windows_display.columns:
                pair_walkforward_windows_display[col] = pair_walkforward_windows_display[col].astype(int).astype(str)
    if not pair_forward_blocks_display.empty:
        for col in ["block_start", "block_end"]:
            if col in pair_forward_blocks_display.columns:
                pair_forward_blocks_display[col] = pd.to_datetime(pair_forward_blocks_display[col], utc=True).dt.strftime("%Y-%m-%d")
        for col in ["active_hours", "affected_hours"]:
            if col in pair_forward_blocks_display.columns:
                pair_forward_blocks_display[col] = pair_forward_blocks_display[col].astype(int).astype(str)
    if not pair_forward_blocks_10d_display.empty:
        for col in ["block_start", "block_end"]:
            if col in pair_forward_blocks_10d_display.columns:
                pair_forward_blocks_10d_display[col] = pd.to_datetime(pair_forward_blocks_10d_display[col], utc=True).dt.strftime("%Y-%m-%d")
        for col in ["active_hours", "affected_hours"]:
            if col in pair_forward_blocks_10d_display.columns:
                pair_forward_blocks_10d_display[col] = pair_forward_blocks_10d_display[col].astype(int).astype(str)
    if not pair_shadow_checkpoints_display.empty:
        for col in ["checkpoint_start", "checkpoint_end"]:
            if col in pair_shadow_checkpoints_display.columns:
                pair_shadow_checkpoints_display[col] = pd.to_datetime(pair_shadow_checkpoints_display[col], utc=True).dt.strftime("%Y-%m-%d")
        for col in ["review_days", "active_hours", "affected_hours"]:
            if col in pair_shadow_checkpoints_display.columns:
                pair_shadow_checkpoints_display[col] = pair_shadow_checkpoints_display[col].astype(int).astype(str)
    if not pair_pure_test_tail_summary_display.empty:
        for col in ["slice_start", "slice_end"]:
            if col in pair_pure_test_tail_summary_display.columns:
                pair_pure_test_tail_summary_display[col] = pd.to_datetime(pair_pure_test_tail_summary_display[col], utc=True).dt.strftime("%Y-%m-%d %H:%M")
        for col in ["active_hours", "affected_hours", "up_hours", "flat_hours", "down_flat_hours", "down_hours"]:
            if col in pair_pure_test_tail_summary_display.columns:
                pair_pure_test_tail_summary_display[col] = pair_pure_test_tail_summary_display[col].astype(int).astype(str)
    if not pair_pure_test_tail_checkpoints_display.empty:
        for col in ["checkpoint_start", "checkpoint_end"]:
            if col in pair_pure_test_tail_checkpoints_display.columns:
                pair_pure_test_tail_checkpoints_display[col] = pd.to_datetime(pair_pure_test_tail_checkpoints_display[col], utc=True).dt.strftime("%Y-%m-%d %H:%M")
        for col in ["review_hours", "active_hours", "affected_hours"]:
            if col in pair_pure_test_tail_checkpoints_display.columns:
                pair_pure_test_tail_checkpoints_display[col] = pair_pure_test_tail_checkpoints_display[col].astype(int).astype(str)
    if not pair_pure_test_tail_blocks_display.empty:
        for col in ["block_start", "block_end"]:
            if col in pair_pure_test_tail_blocks_display.columns:
                pair_pure_test_tail_blocks_display[col] = pd.to_datetime(pair_pure_test_tail_blocks_display[col], utc=True).dt.strftime("%Y-%m-%d %H:%M")
        for col in ["block_id", "active_hours", "affected_hours"]:
            if col in pair_pure_test_tail_blocks_display.columns:
                pair_pure_test_tail_blocks_display[col] = pair_pure_test_tail_blocks_display[col].astype(int).astype(str)
    if not pair_default_episode_summary_display.empty:
        for col in ["start_time", "end_time"]:
            if col in pair_default_episode_summary_display.columns:
                pair_default_episode_summary_display[col] = pd.to_datetime(pair_default_episode_summary_display[col], utc=True).dt.strftime("%Y-%m-%d %H:%M")
        for col in ["episode_id", "hours"]:
            if col in pair_default_episode_summary_display.columns:
                pair_default_episode_summary_display[col] = pair_default_episode_summary_display[col].astype(int).astype(str)
    if not pair_downflat_overlay_summary_display.empty:
        for col in ["cost_bps", "active_hours", "max_active_positions"]:
            if col in pair_downflat_overlay_summary_display.columns:
                pair_downflat_overlay_summary_display[col] = pair_downflat_overlay_summary_display[col].astype(int).astype(str)
    if not pair_downflat_overlay_holdout_split_display.empty and "hours" in pair_downflat_overlay_holdout_split_display.columns:
        pair_downflat_overlay_holdout_split_display["hours"] = pair_downflat_overlay_holdout_split_display["hours"].astype(int).astype(str)
    if not pair_downflat_overlay_episode_summary_display.empty:
        for col in ["start_time", "end_time"]:
            if col in pair_downflat_overlay_episode_summary_display.columns:
                pair_downflat_overlay_episode_summary_display[col] = pd.to_datetime(pair_downflat_overlay_episode_summary_display[col], utc=True).dt.strftime("%Y-%m-%d %H:%M")
        for col in ["episode_id", "hours"]:
            if col in pair_downflat_overlay_episode_summary_display.columns:
                pair_downflat_overlay_episode_summary_display[col] = pair_downflat_overlay_episode_summary_display[col].astype(int).astype(str)
    if not pair_downflat_overlay_tail_summary_display.empty:
        for col in ["slice_start", "slice_end"]:
            if col in pair_downflat_overlay_tail_summary_display.columns:
                pair_downflat_overlay_tail_summary_display[col] = pd.to_datetime(pair_downflat_overlay_tail_summary_display[col], utc=True).dt.strftime("%Y-%m-%d %H:%M")
        for col in ["active_hours", "affected_hours", "up_hours", "flat_hours", "down_flat_hours", "down_hours"]:
            if col in pair_downflat_overlay_tail_summary_display.columns:
                pair_downflat_overlay_tail_summary_display[col] = pair_downflat_overlay_tail_summary_display[col].astype(int).astype(str)
    if not pair_downflat_overlay_tail_checkpoints_display.empty:
        for col in ["checkpoint_start", "checkpoint_end"]:
            if col in pair_downflat_overlay_tail_checkpoints_display.columns:
                pair_downflat_overlay_tail_checkpoints_display[col] = pd.to_datetime(pair_downflat_overlay_tail_checkpoints_display[col], utc=True).dt.strftime("%Y-%m-%d %H:%M")
        for col in ["review_hours", "active_hours", "affected_hours"]:
            if col in pair_downflat_overlay_tail_checkpoints_display.columns:
                pair_downflat_overlay_tail_checkpoints_display[col] = pair_downflat_overlay_tail_checkpoints_display[col].astype(int).astype(str)
    if not pair_downflat_overlay_tail_blocks_display.empty:
        for col in ["block_start", "block_end"]:
            if col in pair_downflat_overlay_tail_blocks_display.columns:
                pair_downflat_overlay_tail_blocks_display[col] = pd.to_datetime(pair_downflat_overlay_tail_blocks_display[col], utc=True).dt.strftime("%Y-%m-%d %H:%M")
        for col in ["block_id", "active_hours", "affected_hours"]:
            if col in pair_downflat_overlay_tail_blocks_display.columns:
                pair_downflat_overlay_tail_blocks_display[col] = pair_downflat_overlay_tail_blocks_display[col].astype(int).astype(str)
    if not pair_downflat_overlay_walkforward_windows_display.empty:
        for col in ["window_start", "window_end"]:
            if col in pair_downflat_overlay_walkforward_windows_display.columns:
                pair_downflat_overlay_walkforward_windows_display[col] = pd.to_datetime(pair_downflat_overlay_walkforward_windows_display[col], utc=True).dt.strftime("%Y-%m-%d")
        for col in ["active_hours", "affected_hours"]:
            if col in pair_downflat_overlay_walkforward_windows_display.columns:
                pair_downflat_overlay_walkforward_windows_display[col] = pair_downflat_overlay_walkforward_windows_display[col].astype(int).astype(str)
    if not pair_downflat_overlay_forward_blocks_display.empty:
        for col in ["block_start", "block_end"]:
            if col in pair_downflat_overlay_forward_blocks_display.columns:
                pair_downflat_overlay_forward_blocks_display[col] = pd.to_datetime(pair_downflat_overlay_forward_blocks_display[col], utc=True).dt.strftime("%Y-%m-%d")
        for col in ["active_hours", "affected_hours"]:
            if col in pair_downflat_overlay_forward_blocks_display.columns:
                pair_downflat_overlay_forward_blocks_display[col] = pair_downflat_overlay_forward_blocks_display[col].astype(int).astype(str)
    if not pair_downflat_overlay_forward_blocks_10d_display.empty:
        for col in ["block_start", "block_end"]:
            if col in pair_downflat_overlay_forward_blocks_10d_display.columns:
                pair_downflat_overlay_forward_blocks_10d_display[col] = pd.to_datetime(pair_downflat_overlay_forward_blocks_10d_display[col], utc=True).dt.strftime("%Y-%m-%d")
        for col in ["active_hours", "affected_hours"]:
            if col in pair_downflat_overlay_forward_blocks_10d_display.columns:
                pair_downflat_overlay_forward_blocks_10d_display[col] = pair_downflat_overlay_forward_blocks_10d_display[col].astype(int).astype(str)
    if not pair_downflat_overlay_shadow_checkpoints_display.empty:
        for col in ["checkpoint_start", "checkpoint_end"]:
            if col in pair_downflat_overlay_shadow_checkpoints_display.columns:
                pair_downflat_overlay_shadow_checkpoints_display[col] = pd.to_datetime(pair_downflat_overlay_shadow_checkpoints_display[col], utc=True).dt.strftime("%Y-%m-%d")
        for col in ["review_days", "active_hours", "affected_hours"]:
            if col in pair_downflat_overlay_shadow_checkpoints_display.columns:
                pair_downflat_overlay_shadow_checkpoints_display[col] = pair_downflat_overlay_shadow_checkpoints_display[col].astype(int).astype(str)
    for df in [pair_sizing_holdout_regime_display, pair_sizing_holdout_split_regime_display]:
        if not df.empty and "hours" in df.columns:
            df["hours"] = df["hours"].astype(int).astype(str)
    hourly_summary_row = hourly_portfolio_summary.iloc[0] if hourly_portfolio_summary is not None and not hourly_portfolio_summary.empty else None
    hourly_split_map = hourly_split_summary.set_index("split").to_dict("index") if hourly_split_summary is not None and not hourly_split_summary.empty else {}
    hourly_regime_map = hourly_regime_summary.set_index("regime").to_dict("index") if hourly_regime_summary is not None and not hourly_regime_summary.empty else {}
    gate_hourly_split_map = gate_hourly_split_summary.set_index("split").to_dict("index") if gate_hourly_split_summary is not None and not gate_hourly_split_summary.empty else {}
    gate_hourly_regime_map = gate_hourly_regime_summary.set_index("regime").to_dict("index") if gate_hourly_regime_summary is not None and not gate_hourly_regime_summary.empty else {}
    raw_two_pos_mix = hourly_two_position_symbol_mix_compare.loc[
        hourly_two_position_symbol_mix_compare["strategy"].eq("raw_v0")
    ].copy() if hourly_two_position_symbol_mix_compare is not None and not hourly_two_position_symbol_mix_compare.empty else pd.DataFrame()
    gate_two_pos_mix = hourly_two_position_symbol_mix_compare.loc[
        hourly_two_position_symbol_mix_compare["strategy"].eq("avoid_fluctuating")
    ].copy() if hourly_two_position_symbol_mix_compare is not None and not hourly_two_position_symbol_mix_compare.empty else pd.DataFrame()
    raw_two_pos_main = raw_two_pos_mix.sort_values(["hours", "mean_hourly_return"], ascending=[False, True]).iloc[0] if not raw_two_pos_mix.empty else None
    raw_two_pos_worst = raw_two_pos_mix.sort_values(["mean_hourly_return", "hours"], ascending=[True, False]).iloc[0] if not raw_two_pos_mix.empty else None
    gate_two_pos_main = gate_two_pos_mix.sort_values(["hours", "mean_hourly_return"], ascending=[False, True]).iloc[0] if not gate_two_pos_mix.empty else None
    gate_two_pos_best = gate_two_pos_mix.sort_values(["mean_hourly_return", "hours"], ascending=[False, False]).iloc[0] if not gate_two_pos_mix.empty else None
    raw_two_pos_context = hourly_two_position_pair_context_compare.loc[
        hourly_two_position_pair_context_compare["strategy"].eq("raw_v0")
    ].copy() if hourly_two_position_pair_context_compare is not None and not hourly_two_position_pair_context_compare.empty else pd.DataFrame()
    gate_two_pos_context = hourly_two_position_pair_context_compare.loc[
        hourly_two_position_pair_context_compare["strategy"].eq("avoid_fluctuating")
    ].copy() if hourly_two_position_pair_context_compare is not None and not hourly_two_position_pair_context_compare.empty else pd.DataFrame()
    raw_two_pos_context_main = raw_two_pos_context.sort_values(["hours", "mean_hourly_return"], ascending=[False, True]).iloc[0] if not raw_two_pos_context.empty else None
    raw_two_pos_context_test_tail = raw_two_pos_context[raw_two_pos_context["split_mix"].astype(str).str.contains("test", na=False)].sort_values(["mean_hourly_return", "hours"], ascending=[True, False]).iloc[0] if not raw_two_pos_context[raw_two_pos_context["split_mix"].astype(str).str.contains("test", na=False)].empty else None
    gate_two_pos_context_main = gate_two_pos_context.sort_values(["hours", "mean_hourly_return"], ascending=[False, True]).iloc[0] if not gate_two_pos_context.empty else None
    gate_eth_sol_context = gate_two_pos_context[gate_two_pos_context["symbol_pair"].astype(str).eq("ETH-USD + SOL-USD")].copy() if not gate_two_pos_context.empty else pd.DataFrame()
    gate_eth_sol_target_context = gate_eth_sol_context[
        gate_eth_sol_context["split_mix"].astype(str).isin(["validate", "test"]) & gate_eth_sol_context["regime_mix"].astype(str).eq("up")
    ].copy() if not gate_eth_sol_context.empty else pd.DataFrame()
    gate_eth_sol_target_context_display = gate_eth_sol_target_context.copy()
    if not gate_eth_sol_target_context_display.empty:
        gate_eth_sol_target_context_display["hours"] = gate_eth_sol_target_context_display["hours"].astype(int).astype(str)
    gate_two_pos_context_residual = gate_eth_sol_context.sort_values(["hours", "mean_hourly_return"], ascending=[False, True]).iloc[0] if not gate_eth_sol_context.empty else None
    pair_sizing_map = pair_sizing_compare.set_index("strategy").to_dict("index") if pair_sizing_compare is not None and not pair_sizing_compare.empty else {}
    gate_pair_size_row = pair_sizing_map.get("avoid_fluctuating_eth_sol_test_validate_up_halfsize")
    sizing_candidate_map = sizing_candidate_compare.set_index("candidate").to_dict("index") if sizing_candidate_compare is not None and not sizing_candidate_compare.empty else {}
    pair_default_row = sizing_candidate_map.get("avoid_fluctuating_eth_sol_pair_halfsize")
    pure_test_context_row = sizing_candidate_map.get("avoid_fluctuating_eth_sol_test_up_halfsize")
    pair_sizing_holdout_split = summarize_policy_affected_hours_by_split(pair_sizing_affected_hours) if pair_sizing_affected_hours is not None else pd.DataFrame()
    pair_sizing_holdout_split_display = pair_sizing_holdout_split.copy()
    if not pair_sizing_holdout_split_display.empty:
        pair_sizing_holdout_split_display["hours"] = pair_sizing_holdout_split_display["hours"].astype(int).astype(str)
    pair_sizing_holdout_map = pair_sizing_holdout_split.set_index("split_mix").to_dict("index") if not pair_sizing_holdout_split.empty else {}
    pair_holdout_regime_map = pair_sizing_holdout_regime.set_index("regime_mix").to_dict("index") if pair_sizing_holdout_regime is not None and not pair_sizing_holdout_regime.empty else {}
    pair_regime_coverage_audit = summarize_pair_regime_coverage_audit(gate_hourly_regime_summary, pair_sizing_holdout_regime) if gate_hourly_regime_summary is not None else pd.DataFrame()
    pair_regime_coverage_audit_display = pair_regime_coverage_audit.copy()
    if not pair_regime_coverage_audit_display.empty:
        for col in ["gate_active_hours", "policy_affected_hours"]:
            if col in pair_regime_coverage_audit_display.columns:
                pair_regime_coverage_audit_display[col] = pair_regime_coverage_audit_display[col].astype(int).astype(str)
    pair_down_coverage_row = pair_regime_coverage_audit.loc[pair_regime_coverage_audit["regime"].astype(str).eq("down")].iloc[0] if not pair_regime_coverage_audit.empty and (pair_regime_coverage_audit["regime"].astype(str) == "down").any() else None
    pair_predown_bridge_audit_active = pair_predown_bridge_audit.copy() if pair_predown_bridge_audit is not None and not pair_predown_bridge_audit.empty else pd.DataFrame()
    pair_predown_bridge_6h = pair_predown_bridge_audit_active.loc[pair_predown_bridge_audit_active["lead_hours"].eq(6)].iloc[0] if not pair_predown_bridge_audit_active.empty and (pair_predown_bridge_audit_active["lead_hours"] == 6).any() else None
    pair_predown_bridge_12h = pair_predown_bridge_audit_active.loc[pair_predown_bridge_audit_active["lead_hours"].eq(12)].iloc[0] if not pair_predown_bridge_audit_active.empty and (pair_predown_bridge_audit_active["lead_hours"] == 12).any() else None
    pair_predown_bridge_24h = pair_predown_bridge_audit_active.loc[pair_predown_bridge_audit_active["lead_hours"].eq(24)].iloc[0] if not pair_predown_bridge_audit_active.empty and (pair_predown_bridge_audit_active["lead_hours"] == 24).any() else None
    downrisk_zone_audit_compare_active = downrisk_zone_audit_compare.copy() if downrisk_zone_audit_compare is not None and not downrisk_zone_audit_compare.empty else pd.DataFrame()
    downrisk_zone_map = {
        (str(row.get("policy", "")), int(row.get("lead_hours", 0))): row
        for _, row in downrisk_zone_audit_compare_active.iterrows()
        if pd.notna(row.get("lead_hours", np.nan))
    } if not downrisk_zone_audit_compare_active.empty else {}
    default_downrisk_12h = downrisk_zone_map.get(("default_pair_halfsize", 12))
    default_downrisk_24h = downrisk_zone_map.get(("default_pair_halfsize", 24))
    default_downrisk_48h = downrisk_zone_map.get(("default_pair_halfsize", 48))
    default_downrisk_72h = downrisk_zone_map.get(("default_pair_halfsize", 72))
    default_downrisk_96h = downrisk_zone_map.get(("default_pair_halfsize", 96))
    mixed_downrisk_12h = downrisk_zone_map.get(("downflat_mixed_tail_overlay", 12))
    mixed_downrisk_24h = downrisk_zone_map.get(("downflat_mixed_tail_overlay", 24))
    mixed_downrisk_48h = downrisk_zone_map.get(("downflat_mixed_tail_overlay", 48))
    mixed_downrisk_72h = downrisk_zone_map.get(("downflat_mixed_tail_overlay", 72))
    mixed_downrisk_96h = downrisk_zone_map.get(("downflat_mixed_tail_overlay", 96))
    future_pure_down_lead_audit_active = future_pure_down_lead_audit_compare.copy() if future_pure_down_lead_audit_compare is not None and not future_pure_down_lead_audit_compare.empty else pd.DataFrame()
    future_pure_down_lead_map = {
        (str(row.get("policy", "")), int(row.get("future_window_hours", 0))): row
        for _, row in future_pure_down_lead_audit_active.iterrows()
        if pd.notna(row.get("future_window_hours", np.nan))
    } if not future_pure_down_lead_audit_active.empty else {}
    default_future_down_24h = future_pure_down_lead_map.get(("default_pair_halfsize", 24))
    default_future_down_48h = future_pure_down_lead_map.get(("default_pair_halfsize", 48))
    default_future_down_72h = future_pure_down_lead_map.get(("default_pair_halfsize", 72))
    default_future_down_96h = future_pure_down_lead_map.get(("default_pair_halfsize", 96))
    mixed_future_down_24h = future_pure_down_lead_map.get(("downflat_mixed_tail_overlay", 24))
    mixed_future_down_48h = future_pure_down_lead_map.get(("downflat_mixed_tail_overlay", 48))
    mixed_future_down_72h = future_pure_down_lead_map.get(("downflat_mixed_tail_overlay", 72))
    mixed_future_down_96h = future_pure_down_lead_map.get(("downflat_mixed_tail_overlay", 96))
    pair_default_episode_summary_active = pair_default_episode_summary.copy() if pair_default_episode_summary is not None and not pair_default_episode_summary.empty else pd.DataFrame()
    pair_default_episode_count = int(len(pair_default_episode_summary_active)) if not pair_default_episode_summary_active.empty else 0
    pair_default_episode_best = pair_default_episode_summary_active.sort_values(["delta_pp", "hours"], ascending=[False, False]).iloc[0] if not pair_default_episode_summary_active.empty else None
    pair_default_episode_test_up = pair_default_episode_summary_active.loc[
        pair_default_episode_summary_active["split_mix"].astype(str).eq("test")
        & pair_default_episode_summary_active["regime_mix"].astype(str).eq("up")
    ].sort_values("start_time").iloc[0] if not pair_default_episode_summary_active.empty and not pair_default_episode_summary_active.loc[
        pair_default_episode_summary_active["split_mix"].astype(str).eq("test")
        & pair_default_episode_summary_active["regime_mix"].astype(str).eq("up")
    ].empty else None
    pair_default_episode_test_downflat = pair_default_episode_summary_active.loc[
        pair_default_episode_summary_active["split_mix"].astype(str).eq("test")
        & pair_default_episode_summary_active["regime_mix"].astype(str).eq("down + flat")
    ].sort_values("start_time").iloc[0] if not pair_default_episode_summary_active.empty and not pair_default_episode_summary_active.loc[
        pair_default_episode_summary_active["split_mix"].astype(str).eq("test")
        & pair_default_episode_summary_active["regime_mix"].astype(str).eq("down + flat")
    ].empty else None
    pair_walkforward_active = pair_walkforward_windows.loc[pair_walkforward_windows["affected_hours"].gt(0)].copy() if pair_walkforward_windows is not None and not pair_walkforward_windows.empty else pd.DataFrame()
    pair_walkforward_any = pair_walkforward_windows.copy() if pair_walkforward_windows is not None and not pair_walkforward_windows.empty else pd.DataFrame()
    pair_walkforward_active_first = pair_walkforward_active.iloc[0] if not pair_walkforward_active.empty else None
    pair_walkforward_active_last = pair_walkforward_active.iloc[-1] if not pair_walkforward_active.empty else None
    pair_forward_blocks_active = pair_forward_blocks.loc[pair_forward_blocks["affected_hours"].gt(0)].copy() if pair_forward_blocks is not None and not pair_forward_blocks.empty else pd.DataFrame()
    pair_forward_blocks_positive = pair_forward_blocks_active.loc[pair_forward_blocks_active["delta_vs_gate_pp"].gt(0)].copy() if not pair_forward_blocks_active.empty else pd.DataFrame()
    pair_forward_blocks_negative = pair_forward_blocks_active.loc[pair_forward_blocks_active["delta_vs_gate_pp"].le(0)].copy() if not pair_forward_blocks_active.empty else pd.DataFrame()
    pair_forward_blocks_best = pair_forward_blocks_active.sort_values(["delta_vs_gate_pp", "drawdown_improve_pp"], ascending=[False, False]).iloc[0] if not pair_forward_blocks_active.empty else None
    pair_forward_blocks_worst = pair_forward_blocks_active.sort_values(["delta_vs_gate_pp", "affected_hours"], ascending=[True, False]).iloc[0] if not pair_forward_blocks_active.empty else None
    pair_forward_blocks_10d_active = pair_forward_blocks_10d.loc[pair_forward_blocks_10d["affected_hours"].gt(0)].copy() if pair_forward_blocks_10d is not None and not pair_forward_blocks_10d.empty else pd.DataFrame()
    pair_forward_blocks_10d_positive = pair_forward_blocks_10d_active.loc[pair_forward_blocks_10d_active["delta_vs_gate_pp"].gt(0)].copy() if not pair_forward_blocks_10d_active.empty else pd.DataFrame()
    pair_forward_blocks_10d_best = pair_forward_blocks_10d_active.sort_values(["delta_vs_gate_pp", "drawdown_improve_pp"], ascending=[False, False]).iloc[0] if not pair_forward_blocks_10d_active.empty else None
    pair_forward_blocks_10d_worst = pair_forward_blocks_10d_active.sort_values(["delta_vs_gate_pp", "affected_hours"], ascending=[True, False]).iloc[0] if not pair_forward_blocks_10d_active.empty else None
    pair_shadow_checkpoints_active = pair_shadow_checkpoints.loc[pair_shadow_checkpoints["affected_hours"].gt(0)].copy() if pair_shadow_checkpoints is not None and not pair_shadow_checkpoints.empty else pd.DataFrame()
    pair_shadow_checkpoints_positive = pair_shadow_checkpoints_active.loc[pair_shadow_checkpoints_active["delta_vs_gate_pp"].gt(0)].copy() if not pair_shadow_checkpoints_active.empty else pd.DataFrame()
    pair_shadow_checkpoints_last = pair_shadow_checkpoints_active.sort_values("review_days").iloc[-1] if not pair_shadow_checkpoints_active.empty else None
    pair_shadow_checkpoints_best = pair_shadow_checkpoints_active.sort_values(["delta_vs_gate_pp", "drawdown_improve_pp"], ascending=[False, False]).iloc[0] if not pair_shadow_checkpoints_active.empty else None
    pair_shadow_checkpoints_worst = pair_shadow_checkpoints_active.sort_values(["delta_vs_gate_pp", "review_days"], ascending=[True, True]).iloc[0] if not pair_shadow_checkpoints_active.empty else None
    pair_pure_test_tail_row = pair_pure_test_tail_summary.iloc[0] if pair_pure_test_tail_summary is not None and not pair_pure_test_tail_summary.empty else None
    pair_pure_test_tail_checkpoints_active = pair_pure_test_tail_checkpoints.loc[pair_pure_test_tail_checkpoints["affected_hours"].gt(0)].copy() if pair_pure_test_tail_checkpoints is not None and not pair_pure_test_tail_checkpoints.empty else pd.DataFrame()
    pair_pure_test_tail_checkpoints_positive = pair_pure_test_tail_checkpoints_active.loc[pair_pure_test_tail_checkpoints_active["delta_vs_gate_pp"].gt(0)].copy() if not pair_pure_test_tail_checkpoints_active.empty else pd.DataFrame()
    pair_pure_test_tail_checkpoints_last = pair_pure_test_tail_checkpoints_active.sort_values("review_hours").iloc[-1] if not pair_pure_test_tail_checkpoints_active.empty else None
    pair_pure_test_tail_checkpoints_best = pair_pure_test_tail_checkpoints_active.sort_values(["delta_vs_gate_pp", "drawdown_improve_pp"], ascending=[False, False]).iloc[0] if not pair_pure_test_tail_checkpoints_active.empty else None
    pair_pure_test_tail_blocks_active = pair_pure_test_tail_blocks.loc[pair_pure_test_tail_blocks["affected_hours"].gt(0)].copy() if pair_pure_test_tail_blocks is not None and not pair_pure_test_tail_blocks.empty else pd.DataFrame()
    pair_pure_test_tail_blocks_positive = pair_pure_test_tail_blocks_active.loc[pair_pure_test_tail_blocks_active["delta_vs_gate_pp"].gt(0)].copy() if not pair_pure_test_tail_blocks_active.empty else pd.DataFrame()
    pair_pure_test_tail_blocks_best = pair_pure_test_tail_blocks_active.sort_values(["delta_vs_gate_pp", "drawdown_improve_pp"], ascending=[False, False]).iloc[0] if not pair_pure_test_tail_blocks_active.empty else None
    pair_pure_test_tail_blocks_worst = pair_pure_test_tail_blocks_active.sort_values(["delta_vs_gate_pp", "block_id"], ascending=[True, True]).iloc[0] if not pair_pure_test_tail_blocks_active.empty else None
    pair_pure_test_tail_blocks_total = int(len(pair_pure_test_tail_blocks)) if pair_pure_test_tail_blocks is not None and not pair_pure_test_tail_blocks.empty else 0
    pair_down_overlay_row = pair_down_overlay_summary.iloc[0] if pair_down_overlay_summary is not None and not pair_down_overlay_summary.empty else None
    pair_down_overlay_affected_count = int(len(pair_down_overlay_affected_hours)) if pair_down_overlay_affected_hours is not None else 0
    pair_downflat_overlay_row = pair_downflat_overlay_summary.iloc[0] if pair_downflat_overlay_summary is not None and not pair_downflat_overlay_summary.empty else None
    pair_downflat_overlay_holdout_split_map = pair_downflat_overlay_holdout_split.set_index("split_mix").to_dict("index") if pair_downflat_overlay_holdout_split is not None and not pair_downflat_overlay_holdout_split.empty else {}
    pair_downflat_overlay_episode_summary_active = pair_downflat_overlay_episode_summary.copy() if pair_downflat_overlay_episode_summary is not None and not pair_downflat_overlay_episode_summary.empty else pd.DataFrame()
    pair_downflat_overlay_episode_count = int(len(pair_downflat_overlay_episode_summary_active)) if not pair_downflat_overlay_episode_summary_active.empty else 0
    pair_downflat_overlay_episode_best = pair_downflat_overlay_episode_summary_active.sort_values(["delta_pp", "hours"], ascending=[False, False]).iloc[0] if not pair_downflat_overlay_episode_summary_active.empty else None
    pair_downflat_overlay_episode_test = pair_downflat_overlay_episode_summary_active.loc[
        pair_downflat_overlay_episode_summary_active["split_mix"].astype(str).eq("test")
    ].sort_values("start_time").iloc[0] if not pair_downflat_overlay_episode_summary_active.empty and not pair_downflat_overlay_episode_summary_active.loc[
        pair_downflat_overlay_episode_summary_active["split_mix"].astype(str).eq("test")
    ].empty else None
    pair_downflat_overlay_episode_train = pair_downflat_overlay_episode_summary_active.loc[
        pair_downflat_overlay_episode_summary_active["split_mix"].astype(str).eq("train")
    ].copy() if not pair_downflat_overlay_episode_summary_active.empty else pd.DataFrame()
    pair_downflat_overlay_episode_train_delta_pp = float(pair_downflat_overlay_episode_train["delta_pp"].sum()) if not pair_downflat_overlay_episode_train.empty else 0.0
    pair_downflat_overlay_episode_test_delta_pp = float(pair_downflat_overlay_episode_summary_active.loc[
        pair_downflat_overlay_episode_summary_active["split_mix"].astype(str).eq("test"), "delta_pp"
    ].sum()) if not pair_downflat_overlay_episode_summary_active.empty else 0.0
    pair_downflat_overlay_episode_total_delta_pp = float(pair_downflat_overlay_episode_summary_active["delta_pp"].sum()) if not pair_downflat_overlay_episode_summary_active.empty else 0.0
    pair_downflat_overlay_episode_test_delta_share = float(pair_downflat_overlay_episode_test_delta_pp / pair_downflat_overlay_episode_total_delta_pp) if pair_downflat_overlay_episode_total_delta_pp else np.nan
    pair_downflat_overlay_episode_train_delta_share = float(pair_downflat_overlay_episode_train_delta_pp / pair_downflat_overlay_episode_total_delta_pp) if pair_downflat_overlay_episode_total_delta_pp else np.nan
    pair_downflat_overlay_tail_row = pair_downflat_overlay_tail_summary.iloc[0] if pair_downflat_overlay_tail_summary is not None and not pair_downflat_overlay_tail_summary.empty else None
    pair_downflat_overlay_tail_checkpoints_active = pair_downflat_overlay_tail_checkpoints.loc[pair_downflat_overlay_tail_checkpoints["affected_hours"].gt(0)].copy() if pair_downflat_overlay_tail_checkpoints is not None and not pair_downflat_overlay_tail_checkpoints.empty else pd.DataFrame()
    pair_downflat_overlay_tail_checkpoints_positive = pair_downflat_overlay_tail_checkpoints_active.loc[pair_downflat_overlay_tail_checkpoints_active["delta_vs_gate_pp"].gt(0)].copy() if not pair_downflat_overlay_tail_checkpoints_active.empty else pd.DataFrame()
    pair_downflat_overlay_tail_checkpoints_last = pair_downflat_overlay_tail_checkpoints_active.sort_values("review_hours").iloc[-1] if not pair_downflat_overlay_tail_checkpoints_active.empty else None
    pair_downflat_overlay_tail_checkpoints_best = pair_downflat_overlay_tail_checkpoints_active.sort_values(["delta_vs_gate_pp", "drawdown_improve_pp"], ascending=[False, False]).iloc[0] if not pair_downflat_overlay_tail_checkpoints_active.empty else None
    pair_downflat_overlay_tail_checkpoints_worst = pair_downflat_overlay_tail_checkpoints_active.sort_values(["delta_vs_gate_pp", "review_hours"], ascending=[True, True]).iloc[0] if not pair_downflat_overlay_tail_checkpoints_active.empty else None
    pair_downflat_overlay_tail_blocks_active = pair_downflat_overlay_tail_blocks.loc[pair_downflat_overlay_tail_blocks["affected_hours"].gt(0)].copy() if pair_downflat_overlay_tail_blocks is not None and not pair_downflat_overlay_tail_blocks.empty else pd.DataFrame()
    pair_downflat_overlay_tail_blocks_positive = pair_downflat_overlay_tail_blocks_active.loc[pair_downflat_overlay_tail_blocks_active["delta_vs_gate_pp"].gt(0)].copy() if not pair_downflat_overlay_tail_blocks_active.empty else pd.DataFrame()
    pair_downflat_overlay_tail_blocks_non_improving = pair_downflat_overlay_tail_blocks_active.loc[pair_downflat_overlay_tail_blocks_active["delta_vs_gate_pp"].le(0)].copy() if not pair_downflat_overlay_tail_blocks_active.empty else pd.DataFrame()
    pair_downflat_overlay_tail_blocks_best = pair_downflat_overlay_tail_blocks_active.sort_values(["delta_vs_gate_pp", "drawdown_improve_pp"], ascending=[False, False]).iloc[0] if not pair_downflat_overlay_tail_blocks_active.empty else None
    pair_downflat_overlay_tail_blocks_worst = pair_downflat_overlay_tail_blocks_active.sort_values(["delta_vs_gate_pp", "block_id"], ascending=[True, True]).iloc[0] if not pair_downflat_overlay_tail_blocks_active.empty else None
    pair_downflat_overlay_walkforward_active = pair_downflat_overlay_walkforward_windows.loc[pair_downflat_overlay_walkforward_windows["affected_hours"].gt(0)].copy() if pair_downflat_overlay_walkforward_windows is not None and not pair_downflat_overlay_walkforward_windows.empty else pd.DataFrame()
    pair_downflat_overlay_walkforward_positive = pair_downflat_overlay_walkforward_active.loc[pair_downflat_overlay_walkforward_active["delta_vs_gate_pp"].gt(0)].copy() if not pair_downflat_overlay_walkforward_active.empty else pd.DataFrame()
    pair_downflat_overlay_walkforward_non_improving = pair_downflat_overlay_walkforward_active.loc[pair_downflat_overlay_walkforward_active["delta_vs_gate_pp"].le(0)].copy() if not pair_downflat_overlay_walkforward_active.empty else pd.DataFrame()
    pair_downflat_overlay_walkforward_first = pair_downflat_overlay_walkforward_active.iloc[0] if not pair_downflat_overlay_walkforward_active.empty else None
    pair_downflat_overlay_walkforward_last = pair_downflat_overlay_walkforward_active.iloc[-1] if not pair_downflat_overlay_walkforward_active.empty else None
    pair_downflat_overlay_walkforward_best = pair_downflat_overlay_walkforward_active.sort_values(["delta_vs_gate_pp", "drawdown_improve_pp"], ascending=[False, False]).iloc[0] if not pair_downflat_overlay_walkforward_active.empty else None
    pair_downflat_overlay_walkforward_worst = pair_downflat_overlay_walkforward_active.sort_values(["delta_vs_gate_pp", "affected_hours"], ascending=[True, False]).iloc[0] if not pair_downflat_overlay_walkforward_active.empty else None
    pair_downflat_overlay_forward_blocks_active = pair_downflat_overlay_forward_blocks.loc[pair_downflat_overlay_forward_blocks["affected_hours"].gt(0)].copy() if pair_downflat_overlay_forward_blocks is not None and not pair_downflat_overlay_forward_blocks.empty else pd.DataFrame()
    pair_downflat_overlay_forward_blocks_positive = pair_downflat_overlay_forward_blocks_active.loc[pair_downflat_overlay_forward_blocks_active["delta_vs_gate_pp"].gt(0)].copy() if not pair_downflat_overlay_forward_blocks_active.empty else pd.DataFrame()
    pair_downflat_overlay_forward_blocks_negative = pair_downflat_overlay_forward_blocks_active.loc[pair_downflat_overlay_forward_blocks_active["delta_vs_gate_pp"].le(0)].copy() if not pair_downflat_overlay_forward_blocks_active.empty else pd.DataFrame()
    pair_downflat_overlay_forward_blocks_conditional_positive = pair_downflat_overlay_forward_blocks_active.loc[pair_downflat_overlay_forward_blocks_active["conditional_delta_pp"].gt(0)].copy() if not pair_downflat_overlay_forward_blocks_active.empty else pd.DataFrame()
    pair_downflat_overlay_forward_blocks_conditional_negative = pair_downflat_overlay_forward_blocks_active.loc[pair_downflat_overlay_forward_blocks_active["conditional_delta_pp"].le(0)].copy() if not pair_downflat_overlay_forward_blocks_active.empty else pd.DataFrame()
    pair_downflat_overlay_forward_blocks_best = pair_downflat_overlay_forward_blocks_active.sort_values(["delta_vs_gate_pp", "drawdown_improve_pp"], ascending=[False, False]).iloc[0] if not pair_downflat_overlay_forward_blocks_active.empty else None
    pair_downflat_overlay_forward_blocks_worst = pair_downflat_overlay_forward_blocks_active.sort_values(["delta_vs_gate_pp", "affected_hours"], ascending=[True, False]).iloc[0] if not pair_downflat_overlay_forward_blocks_active.empty else None
    pair_downflat_overlay_forward_blocks_10d_active = pair_downflat_overlay_forward_blocks_10d.loc[pair_downflat_overlay_forward_blocks_10d["affected_hours"].gt(0)].copy() if pair_downflat_overlay_forward_blocks_10d is not None and not pair_downflat_overlay_forward_blocks_10d.empty else pd.DataFrame()
    pair_downflat_overlay_forward_blocks_10d_positive = pair_downflat_overlay_forward_blocks_10d_active.loc[pair_downflat_overlay_forward_blocks_10d_active["delta_vs_gate_pp"].gt(0)].copy() if not pair_downflat_overlay_forward_blocks_10d_active.empty else pd.DataFrame()
    pair_downflat_overlay_forward_blocks_10d_negative = pair_downflat_overlay_forward_blocks_10d_active.loc[pair_downflat_overlay_forward_blocks_10d_active["delta_vs_gate_pp"].le(0)].copy() if not pair_downflat_overlay_forward_blocks_10d_active.empty else pd.DataFrame()
    pair_downflat_overlay_forward_blocks_10d_conditional_positive = pair_downflat_overlay_forward_blocks_10d_active.loc[pair_downflat_overlay_forward_blocks_10d_active["conditional_delta_pp"].gt(0)].copy() if not pair_downflat_overlay_forward_blocks_10d_active.empty else pd.DataFrame()
    pair_downflat_overlay_forward_blocks_10d_conditional_negative = pair_downflat_overlay_forward_blocks_10d_active.loc[pair_downflat_overlay_forward_blocks_10d_active["conditional_delta_pp"].le(0)].copy() if not pair_downflat_overlay_forward_blocks_10d_active.empty else pd.DataFrame()
    pair_downflat_overlay_forward_blocks_10d_best = pair_downflat_overlay_forward_blocks_10d_active.sort_values(["delta_vs_gate_pp", "drawdown_improve_pp"], ascending=[False, False]).iloc[0] if not pair_downflat_overlay_forward_blocks_10d_active.empty else None
    pair_downflat_overlay_forward_blocks_10d_worst = pair_downflat_overlay_forward_blocks_10d_active.sort_values(["delta_vs_gate_pp", "affected_hours"], ascending=[True, False]).iloc[0] if not pair_downflat_overlay_forward_blocks_10d_active.empty else None
    pair_downflat_overlay_shadow_checkpoints_active = pair_downflat_overlay_shadow_checkpoints.loc[pair_downflat_overlay_shadow_checkpoints["affected_hours"].gt(0)].copy() if pair_downflat_overlay_shadow_checkpoints is not None and not pair_downflat_overlay_shadow_checkpoints.empty else pd.DataFrame()
    pair_downflat_overlay_shadow_checkpoints_positive = pair_downflat_overlay_shadow_checkpoints_active.loc[pair_downflat_overlay_shadow_checkpoints_active["delta_vs_gate_pp"].gt(0)].copy() if not pair_downflat_overlay_shadow_checkpoints_active.empty else pd.DataFrame()
    pair_downflat_overlay_shadow_checkpoints_last = pair_downflat_overlay_shadow_checkpoints_active.sort_values("review_days").iloc[-1] if not pair_downflat_overlay_shadow_checkpoints_active.empty else None
    pair_downflat_overlay_shadow_checkpoints_best = pair_downflat_overlay_shadow_checkpoints_active.sort_values(["delta_vs_gate_pp", "drawdown_improve_pp"], ascending=[False, False]).iloc[0] if not pair_downflat_overlay_shadow_checkpoints_active.empty else None
    pair_downflat_overlay_shadow_checkpoints_worst = pair_downflat_overlay_shadow_checkpoints_active.sort_values(["delta_vs_gate_pp", "review_days"], ascending=[True, True]).iloc[0] if not pair_downflat_overlay_shadow_checkpoints_active.empty else None
    body = f"""
    <section class="hero">
      <p class="muted">Fast small-loop deliverable / 因子实验 v0</p>
      <h1>support_breakout_raw @ h24 v0 回测页</h1>
      <p>这页只回答一个小问题：把 <code>support_breakout_raw</code> 当成一个最简单、每资产不重叠的 <strong>24 小时 continuation short</strong> 策略，结果到底长什么样。</p>
      <div class="grid">
        <div class="card"><div class="k">成交笔数</div><div class="v">{int(summary['trades'])}</div></div>
        <div class="card"><div class="k">平均单笔收益</div><div class="v">{pct(summary['mean_return'])}</div></div>
        <div class="card"><div class="k">胜率</div><div class="v">{pct(summary['win_ratio'])}</div></div>
        <div class="card"><div class="k">累计收益</div><div class="v">{pct(summary['cumulative_return'])}</div></div>
        <div class="card"><div class="k">最大回撤</div><div class="v">{pct(summary['max_drawdown'])}</div></div>
      </div>
      <p class="note">这页是 <a href="../pytrendline_event_validation_v3_final_verdict/report.html">v3 final verdict</a> 的后继原型页：前者回答“v3 最终留下了什么”，这页回答“把留下来的 <code>support_breakout_raw @ h24</code> 压成最小策略原型后，结果到底长什么样”。口径故意做得很朴素：事件触发后直接在 <code>action_open</code> 做空，固定持有 <code>24</code> 根 60m bar，不加成本模型，不做跨资产资金分配，只做同资产不重叠约束。</p>
    </section>
    <section>
      <h2>策略定义</h2>
      <ul>
        <li>样本来源：复用 <code>reports/artifacts/pytrendline_event_validation_v3/event_sample_purged.csv</code> 中的 <code>support_breakout_raw</code> 事件。</li>
        <li>入场：事件对应的 <code>action_timestamp</code> / <code>action_open</code> 直接做空。</li>
        <li>出场：固定持有 <code>h24</code>，即 <code>24</code> 根 60m bar 后按收盘价平仓。</li>
        <li>去重：同一资产若上一笔仍在持有，则跳过后续事件，保证单资产不重叠。</li>
        <li>收益定义：以精确短仓收益 <code>entry_open / exit_close - 1</code> 计算，而不是简单取负号近似。</li>
      </ul>
    </section>
    <section>
      <h2>结论</h2>
      <ul>
        <li class="good">这批样本下，最简单的 breakout v0 并不差：48 笔、4 个资产全覆盖、平均单笔约 {pct(summary['mean_return'])}。</li>
        <li class="good">它更像 <code>h24</code> continuation short，而不是需要复杂过滤器才能勉强成立的东西。</li>
        <li class="bad">但这仍只是事件样本上的“策略化读法”，不是正式投资组合回测：没有做手续费、资金占用、跨资产并发资金分摊，也没有扩大样本窗。</li>
      </ul>
    </section>
    <section>
      <h2>收口定位：这条线现在该怎么用？</h2>
      <ul>
        <li class="good"><b>保留：</b>把 <code>support_breakout_raw @ h24</code> 先作为一个 <b>条件性 alpha / v0 原型</b> 保留。</li>
        <li><b>适合的市场条件：</b>从这页的简单标签看，它在 <code>flat</code> 环境最顺手，在 <code>down</code> 环境也还能工作，但在 <code>up</code> 环境几乎没有边际。</li>
        <li><b>当前最值得优先验证的环境约束：</b>若要加 first-pass gate，现阶段更像样的是 <code>avoid_fluctuating</code>，而不是把它机械地限死在 <code>only_downtrend</code>；因为前者在 OOS 里还能保留大部分样本，同时比 <code>trade_all</code> 更干净。</li>
        <li><b>最诚实的产品定位：</b>它不是“全市场通吃”的成熟策略，而是一个更像 <b>条件性 alpha / strategy-facing breakout-short 原型</b>。</li>
        <li><b>研究线动作：</b>这条 v0 不再继续发散找新花样，而是转入后续更正式的成本、rolling OOS、non-overlap / capital allocation、环境约束验证。</li>
      </ul>
      <p class="note">配套对照页：<a href="../support_breakout_v0_fib_ab/report.html">Breakout v0 vs Breakout + Fibonacci Retest-Hold</a>。那一页的结论用于回答“要不要把 Fibonacci 过滤层继续留在主线上”。</p>
    </section>
    <section>
      <h2>如果继续做 follow-up，允许做什么，不允许做什么？</h2>
      <ul>
        <li><b>允许做的：</b>更接近策略层的 honesty 检查——例如 <code>cost / slippage sensitivity</code>、<code>rolling / OOS</code>、<code>non-overlap / capital allocation</code>、以及更窄的环境约束验证（当前优先看 <code>avoid_fluctuating</code>）。</li>
        <li><b>也允许做的：</b>把 <code>support_breakout_confirm_1</code> 作为紧邻确认变体，一起放进同样的成本 / 执行 / 环境约束框架里比较，但不要把它扩成第二条大而全独立研发主线。</li>
        <li><b>不允许再做的：</b>把这条线重新扩回 <code>v3</code> 式的大全参数搜索、泛跨市场大工程、或重新开一轮“谁才是 breakout 家族第一名”的排序游戏。</li>
        <li><b>为什么要收这么窄：</b>因为当前真正缺的不是再找新变体，而是回答这个 v0 原型在更真实的交易约束下还能不能站住。</li>
      </ul>
      <p class="note">一句话版：这条线现在进入的是 <b>更接近策略层的 honesty / execution follow-up</b>，不是重新回到研究发散模式。</p>
    </section>
    <section>
      <h2>成本 first-pass：扣掉 10 / 20 / 50bps 后，这条线还剩多少？</h2>
      <ul>
        <li><b>整体读法：</b>这条 breakout v0 并不是“轻微成本一扣就没了”。在 <code>20bps</code> 近似下，平均单笔仍约 <code>{pct(overall_20['mean_net_return']) if overall_20 is not None else 'nan'}</code>，累计仍约 <code>{pct(overall_20['cumulative_net_return']) if overall_20 is not None else 'nan'}</code>。</li>
        <li><b>但也不是已经稳到能直接上 production：</b><code>test split</code> 在 <code>20bps</code> 下累计约 <code>{pct(split_20_map.get('test', {}).get('cumulative_net_return'))}</code>；<code>up</code> 环境在同样口径下累计约 <code>{pct(regime_20_map.get('up', {}).get('cumulative_net_return'))}</code>，说明真正要警惕的不是 overall gross 太脆，而是后段稳定性与环境依赖。</li>
        <li><b>当前最诚实的结论：</b>这条线值得继续补 <code>rolling / OOS / environment gate</code>，因为 first-pass 成本并没有直接把它抹平；但也正因为 <code>test / up regime</code> 已经偏弱，所以更不该跳过 honesty 检查、直接把它包装成成熟 short 策略。</li>
      </ul>
      {html_table(cost_tbl_display, percent_cols={'mean_net_return','median_net_return','win_ratio','cumulative_net_return'})}
      <h3>20bps 下按 split 看</h3>
      {html_table(split_20_tbl_display, percent_cols={'mean_net_return','median_net_return','win_ratio','cumulative_net_return'})}
      <h3>20bps 下按 regime 看</h3>
      {html_table(regime_20_tbl_display, percent_cols={'mean_net_return','median_net_return','win_ratio','cumulative_net_return'})}
      <p class="note">一句话版：<code>20bps</code> 还没有把这条 v0 直接吞掉，但它也明确提醒了你——下一步该优先补的是 <b>split / regime honesty</b>，不是继续扩新变体。</p>
    </section>
    <section>
      <h2>如果下一步真做 split / regime honesty，应该怎么做才诚实？</h2>
      <ul>
        <li><b>先固定当前 v0 定义：</b>继续使用 <code>support_breakout_raw @ h24</code>、<code>action_open</code> 做空、固定持有 <code>24</code> 根 bar 的口径，不要因为某个 split / regime 表现差就临时改持有期或入场规则。</li>
        <li><b>至少同时看 gross 与 20bps：</b>因为 first-pass 已证明 overall 并不是被轻微成本直接抹平，下一步更该关心的是 <code>test</code> 与 <code>up regime</code> 在现实一点的成本口径下是否仍持续偏弱。</li>
        <li><b>split honesty 的核心问题：</b>不是 train / validate 漂不漂亮，而是 <code>test</code> 是否还持续接近或低于零；如果主要收益只靠前段样本抬起来，这条线就更该停留在条件性原型，而不是升格成主策略。</li>
        <li><b>regime honesty 的核心问题：</b>不是强行要求每个 regime 都赚钱，而是要诚实回答：它是不是主要只在 <code>flat</code> 环境成立、在 <code>up</code> 环境就明显失效。若答案是是，就应该明确把它标成 <b>conditional alpha</b>，而不是假装它是通用 short。</li>
        <li><b>当前最像样的通过标准：</b>这条线不需要每个 bucket 都赢，但至少不该只靠 <code>train + flat</code> 两块把 overall 结果抬起来；如果 <code>test</code> 在 <code>20bps</code> 下长期转负、且 <code>up regime</code> 没有任何可解释的约束办法，那就更像该停在 v0 原型页，而不是继续往 production short 包装。</li>
      </ul>
      <p class="note">一句话版：下一步不是再找新 breakout 变体，而是要先回答——这条 v0 在 <code>test</code> 与 <code>up regime</code> 的弱点，究竟是可接受的条件性 alpha 特征，还是已经足够说明它不配继续升格。</p>
    </section>
    <section>
      <h2>如果只先试一个最小环境 gate，为什么当前优先看 avoid_fluctuating？</h2>
      <ul>
        <li><b>先把口径说清：</b>下面这张表来自更早的 <code>v3 regime policy slice</code> 证据包，是 <b>event-level OOS gate 对照</b>，不是这页 v0 策略收益本身；它的作用只是回答“哪个环境 gate 更适合先拿来做最小 follow-up”。</li>
        <li><b>当前最有用的一点：</b><code>avoid_fluctuating</code> 在 OOS 里保留了约 <code>{pct(regime_policy_map.get('avoid_fluctuating', {}).get('oos_retention_vs_all'))}</code> 的事件（约 <code>{regime_policy_map.get('avoid_fluctuating', {}).get('oos_events', 'nan')}/19</code>），明显高于 <code>only_downtrend</code> 的约 <code>{pct(regime_policy_map.get('only_downtrend', {}).get('oos_retention_vs_all'))}</code>（约 <code>{regime_policy_map.get('only_downtrend', {}).get('oos_events', 'nan')}/19</code>）。</li>
        <li><b>而且没有因为少做一点就明显变钝：</b><code>avoid_fluctuating</code> 的 OOS 均值约 <code>{pct(regime_policy_map.get('avoid_fluctuating', {}).get('oos_mean_ret_h24'))}</code>、平均超额约 <code>{pct(regime_policy_map.get('avoid_fluctuating', {}).get('oos_avg_excess_ret_h24'))}</code>，与 <code>trade_all</code> 的约 <code>{pct(regime_policy_map.get('trade_all', {}).get('oos_mean_ret_h24'))}</code> / <code>{pct(regime_policy_map.get('trade_all', {}).get('oos_avg_excess_ret_h24'))}</code> 属于同一量级。</li>
        <li><b>所以当前更诚实的策略层读法是：</b>如果只拿一个最小环境 gate 继续做 breakout v0 follow-up，先试 <code>avoid_fluctuating</code>；<code>only_downtrend</code> 不是永远不看，而是现在更像过早把样本砍得太窄。</li>
      </ul>
      {html_table(regime_policy_display[["policy", "oos_events", "oos_retention_vs_all", "oos_mean_ret_h24", "oos_avg_excess_ret_h24", "oos_neg_symbols_excess", "oos_pos_symbols_excess"]] if not regime_policy_display.empty else regime_policy_display, percent_cols={'oos_retention_vs_all','oos_mean_ret_h24','oos_avg_excess_ret_h24'})}
      <p class="note">一句话版：<code>avoid_fluctuating</code> 当前最大的优势不是“神奇提效”，而是 <b>用约 84% 的 OOS 保留率保住了接近 trade_all 的方向性</b>；相比之下，<code>only_downtrend</code> 现在更像把样本过早砍窄。</p>
    </section>
    <section>
      <h2>真把 avoid_fluctuating 放进同一套 hourly portfolio path / sizing honesty 后，它比换 confirm_1 更像样吗？</h2>
      <ul>
        <li><b>先说结论：</b>有一点，而且方向是对的。把 <code>avoid_fluctuating</code> 真放进和 raw 完全同一套 <code>20bps hourly mark-to-market</code> 口径后，它比单纯换成 <code>confirm_1</code> 更直接改善了弱口袋，但还没有把 breakout 线洗成“无条件可做”。</li>
        <li><b>整体层面：</b><code>raw</code> 的 hourly path 累计约 <code>{pct(gate_compare_display.loc[gate_compare_display['strategy'].eq('raw_v0'), 'hourly_path_cost20_cumulative_return'].iloc[0]) if not gate_compare_display.empty else 'nan'}</code>、max drawdown 约 <code>{pct(gate_compare_display.loc[gate_compare_display['strategy'].eq('raw_v0'), 'hourly_path_max_drawdown'].iloc[0]) if not gate_compare_display.empty else 'nan'}</code>；<code>avoid_fluctuating</code> 对应约 <code>{pct(gate_compare_display.loc[gate_compare_display['strategy'].eq('avoid_fluctuating'), 'hourly_path_cost20_cumulative_return'].iloc[0]) if not gate_compare_display.empty else 'nan'}</code> / <code>{pct(gate_compare_display.loc[gate_compare_display['strategy'].eq('avoid_fluctuating'), 'hourly_path_max_drawdown'].iloc[0]) if not gate_compare_display.empty else 'nan'}</code>，说明它至少在统一资金曲线下没有把这条线做钝，反而略有改善。</li>
        <li><b>最有用的改进：</b><code>up</code> 弱口袋从 raw 的约 <code>{pct(gate_compare_display.loc[gate_compare_display['strategy'].eq('raw_v0'), 'up_hourly_path_cost20_cumulative_return'].iloc[0]) if not gate_compare_display.empty else 'nan'}</code>，改善到 <code>avoid_fluctuating</code> 的约 <code>{pct(gate_compare_display.loc[gate_compare_display['strategy'].eq('avoid_fluctuating'), 'up_hourly_path_cost20_cumulative_return'].iloc[0]) if not gate_compare_display.empty else 'nan'}</code>；同时平均活跃仓位也从约 <code>{num(gate_compare_display.loc[gate_compare_display['strategy'].eq('raw_v0'), 'mean_active_positions'].iloc[0]) if not gate_compare_display.empty else 'nan'}</code> 降到约 <code>{num(gate_compare_display.loc[gate_compare_display['strategy'].eq('avoid_fluctuating'), 'mean_active_positions'].iloc[0]) if not gate_compare_display.empty else 'nan'}</code>。</li>
        <li><b>但没被彻底修好：</b><code>test</code> 在同口径下仍约 <code>{pct(gate_compare_display.loc[gate_compare_display['strategy'].eq('avoid_fluctuating'), 'test_hourly_path_cost20_cumulative_return'].iloc[0]) if not gate_compare_display.empty else 'nan'}</code>，只是比 raw 的约 <code>{pct(gate_compare_display.loc[gate_compare_display['strategy'].eq('raw_v0'), 'test_hourly_path_cost20_cumulative_return'].iloc[0]) if not gate_compare_display.empty else 'nan'}</code> 略好一点；这说明它更像一个 <b>有帮助但不万能</b> 的最小环境 gate，而不是把整条线直接变成熟 short 的开关。</li>
      </ul>
      {html_table(gate_compare_display, percent_cols={'trade_retention_vs_raw','per_asset_cost20_cumulative_return','hourly_path_cost20_cumulative_return','hourly_path_max_drawdown','test_hourly_path_cost20_cumulative_return','up_hourly_path_cost20_cumulative_return','flat_hourly_path_cost20_cumulative_return'}, float_cols={'mean_active_positions'})}
      <p class="note">一句话版：如果只在“换 <code>confirm_1</code>”和“加 <code>avoid_fluctuating</code> gate”之间二选一，当前证据更支持后者。因为它至少能在不明显伤 overall path 的前提下，稍微改善 <code>up</code> 弱口袋和回撤；只是 <code>test</code> 仍没被真正修好。</p>
      <h3>把 gate 后的 hourly path 再拆开看：它到底还卡在哪？</h3>
      <ul>
        <li><b>先说结论：</b><code>avoid_fluctuating</code> 最明显修的是 <code>up</code>，但没有把后段稳定性完全修好；当前更像“帮你把最刺眼的弱口袋磨钝一点”，不是“把 breakout 线洗成通用 short”。</li>
        <li><b>split 维度：</b><code>train</code> 与 <code>validate</code> 在同一套 <code>20bps hourly path</code> 下仍为正（约 <code>{pct(gate_hourly_split_map.get('train', {}).get('cumulative_net_return'))}</code> / <code>{pct(gate_hourly_split_map.get('validate', {}).get('cumulative_net_return'))}</code>），但 <code>test</code> 仍约 <code>{pct(gate_hourly_split_map.get('test', {}).get('cumulative_net_return'))}</code>，说明 gate 只把后段伤口缝小了一点，还没缝好。</li>
        <li><b>regime 维度：</b><code>up</code> 已从 raw 的负值翻到约 <code>{pct(gate_hourly_regime_map.get('up', {}).get('cumulative_net_return'))}</code>，但 <code>down</code> 仍约 <code>{pct(gate_hourly_regime_map.get('down', {}).get('cumulative_net_return'))}</code>；真正最像样的仍是 <code>flat</code>，累计约 <code>{pct(gate_hourly_regime_map.get('flat', {}).get('cumulative_net_return'))}</code>。</li>
        <li><b>这对下一步意味着什么：</b>如果还继续补组合层 honesty，更值得问的已经不是“要不要换成 <code>confirm_1</code>”，而是：<b>能不能在保住 <code>avoid_fluctuating</code> 这点改进的同时，继续压低 <code>test/down</code> 的尾部风险。</b></li>
      </ul>
      <h4>avoid_fluctuating：按 split 看 hourly portfolio path（20bps）</h4>
      {html_table(gate_hourly_split_summary_display, percent_cols={'mean_hourly_return','cumulative_net_return','max_drawdown'}, float_cols={'mean_active_positions'})}
      <h4>avoid_fluctuating：按 regime 看 hourly portfolio path（20bps）</h4>
      {html_table(gate_hourly_regime_summary_display, percent_cols={'mean_hourly_return','cumulative_net_return','max_drawdown'}, float_cols={'mean_active_positions'})}
    </section>
    <section>
      <h2>cross-asset overlap first-pass：这条线一旦跨资产一起跑，会不会被并发仓位放大成另一回事？</h2>
      <ul>
        <li><b>先说结论：</b>会，至少不能再假装这只是“每次一笔、顺手可做”的小原型。当前 <code>48</code> 笔交易里，有约 <code>{pct(overlap_summary['share_entries_ge2']) if overlap_summary is not None else 'nan'}</code> 的入场发生在已经有别的仓位开着的时候，约 <code>{pct(overlap_summary['share_entries_ge3']) if overlap_summary is not None else 'nan'}</code> 的入场发生在当时已有至少两笔仓位的时候。</li>
        <li><b>最大并发仓位：</b>这条 v0 的 first-pass cross-asset 并发最高到 <code>{num(overlap_summary['max_concurrent_positions'], 0) if overlap_summary is not None else 'nan'}</code> 笔；而且活跃持仓时间里，约 <code>{pct(overlap_summary['share_active_hours_ge4']) if overlap_summary is not None else 'nan'}</code> 的小时数都处在 <code>4</code> 笔同时持有。</li>
        <li><b>这意味着什么：</b>当前页的收益更像“每个资产各自独立记账”的 prototype 读法，还不是“有统一资金约束的组合级结果”。如果后续要继续往策略层推进，就必须补 <code>non-overlap / capital allocation</code>，否则会高估这条线的可执行性。</li>
        <li><b>当前最诚实的 next step：</b>先做一个最小组合约束对照——至少比较 <code>per-asset independent</code> 与 <code>1-slot global / equal-weight concurrent</code> 两种口径，看看收益是不是主要靠高并发堆出来的。</li>
      </ul>
      {html_table(overlap_summary_display, percent_cols={'share_entries_ge2','share_entries_ge3','share_active_hours_ge2','share_active_hours_ge3','share_active_hours_ge4'}, float_cols={'mean_concurrent_at_entry'})}
      <h3>活跃持仓时间按并发仓位拆分</h3>
      {html_table(overlap_profile_display, percent_cols={'share_active_hours'}, float_cols={'hours'})}
      <p class="note">一句话版：这条 breakout v0 不只是“会不会赚钱”的问题，还包括 <b>仓位会不会扎堆</b>。当前 first-pass 已经说明：如果忽略 cross-asset 并发与资金分摊，就会把它读得比真实执行更轻松。</p>
    </section>
    <section>
      <h2>capital allocation first-pass：1-slot global / equal-weight concurrent 会把这条线压窄多少？</h2>
      <ul>
        <li><b>先说结论：</b>这条 breakout v0 不是“一加组合约束就归零”，但也不能继续按 <code>per-asset independent</code> 的漂亮累计收益去理解。更保守一点的组合层口径，会把它明显压窄。</li>
        <li><b>20bps 下的两种 first-pass：</b><code>1-slot global</code> 只保留约 <code>{int(slot20['trades']) if slot20 is not None else 'nan'}/48</code> 笔交易（约 <code>{pct(slot20['trade_keep_ratio_vs_independent']) if slot20 is not None else 'nan'}</code>），累计约 <code>{pct(slot20['cumulative_net_return']) if slot20 is not None else 'nan'}</code>；而 <code>equal-weight concurrent(entry)</code> 虽保留全部 <code>48</code> 笔，但因为入场时经常要把资金均分给并发仓位，平均有效仓位权重只约 <code>{pct(eq20['mean_effective_weight']) if eq20 is not None else 'nan'}</code>，<code>20bps</code> 下累计约 <code>{pct(eq20['cumulative_net_return']) if eq20 is not None else 'nan'}</code>。</li>
        <li><b>和当前页面主口径相比：</b><code>per-asset independent + 20bps</code> 的累计约 <code>{pct(indep20['cumulative_net_return']) if indep20 is not None else 'nan'}</code>；这说明当前高累计收益并不是“完全虚高”，但确实明显受益于跨资产并发展开后的读法。</li>
        <li><b>这轮最有用的判断：</b><code>equal-weight concurrent(entry)</code> 比 <code>1-slot global</code> 更接近“允许同时持有，但资金要分摊”的现实；它给出的 first-pass 结果大约落在两端之间，因此这条线仍可保留为 <b>组合层值得继续做 honesty check 的 conditional alpha</b>，但已经不适合再按独立记账结果去想象实盘空间。</li>
      </ul>
      {html_table(capital_alloc_display, percent_cols={'trade_keep_ratio_vs_independent','mean_effective_weight','mean_net_return','median_net_return','win_ratio','cumulative_net_return'})}
      <h3>1-slot global 保留下来的交易（first-pass）</h3>
      {html_table(capital_alloc_selected_display, percent_cols={'trade_return'})}
      <h3>equal-weight concurrent(entry) 明细（first-pass）</h3>
      {html_table(capital_alloc_equal_weight_display, percent_cols={'effective_weight','trade_return'})}
      <p class="note">这里的 <code>1-slot global</code> 是最朴素的 greedy first-pass；而 <code>equal-weight concurrent(entry)</code> 也是一个有意收窄的近似：只按 <b>入场时</b> 的并发仓位数给每笔交易分配权重，还不是逐小时重平衡的正式组合回测。但它已经足够回答一个关键问题——这条 v0 若允许并发、但资金必须分摊，大概会被压到什么量级。</p>
    </section>
    <section>
      <h2>更正式一点的组合级资金曲线 first-pass：把 equal-weight 从 entry-only 推到 hourly path 后，还剩多少？</h2>
      <ul>
        <li><b>先说结论：</b>把 `equal-weight concurrent(entry)` 再往前推半步，变成按每个活跃小时做 mark-to-market 的组合级资金曲线后，这条 breakout v0 的 <code>20bps</code> 累计约落在 <code>{pct(hourly_summary_row['cumulative_net_return']) if hourly_summary_row is not None else 'nan'}</code>，低于 entry-only 近似的约 <code>{pct(eq20['cumulative_net_return']) if eq20 is not None else 'nan'}</code>，但仍高于最保守 <code>1-slot global</code> 的约 <code>{pct(slot20['cumulative_net_return']) if slot20 is not None else 'nan'}</code>。</li>
        <li><b>这说明什么：</b>entry-only 的 <code>equal-weight</code> 还不是完全失真，但确实偏乐观；一旦把并发仓位真正放进统一资金曲线里，结果会再被压窄一截。</li>
        <li><b>当前这版 hourly path 的口径：</b>仍然很克制——只对当前已选中的 v0 交易做 hourly mark-to-market，按每个活跃小时的并发仓位等权持有，并把 <code>20bps</code> round-trip cost 拆成 entry / exit 各一半；它还不是最终 portfolio engine，但已经比 entry-only 更接近真实组合路径。</li>
        <li><b>关键量级：</b>这版 path 一共覆盖约 <code>{hourly_summary_row['active_hours'] if hourly_summary_row is not None else 'nan'}</code> 个活跃小时，平均活跃仓位约 <code>{num(hourly_summary_row['mean_active_positions']) if hourly_summary_row is not None else 'nan'}</code>，最大并发约 <code>{num(hourly_summary_row['max_active_positions'], 0) if hourly_summary_row is not None else 'nan'}</code>，对应 max drawdown 约 <code>{pct(hourly_summary_row['max_drawdown']) if hourly_summary_row is not None else 'nan'}</code>。</li>
      </ul>
      {html_table(hourly_portfolio_summary_display, percent_cols={'mean_hourly_return','cumulative_net_return','max_drawdown'}, float_cols={'mean_active_positions'})}
      <p class="note">一句话版：把 breakout v0 放进更正式一点的统一资金曲线后，`20bps` 下大约从 entry-only 的 <code>19.40%</code> 再压到约 <code>{pct(hourly_summary_row['cumulative_net_return']) if hourly_summary_row is not None else 'nan'}</code>。所以这条线仍没被组合约束直接抹掉，但也更不该再拿独立记账或 entry-only 近似去想象实盘空间。</p>
    </section>
    <section>
      <h2>把 split / regime honesty 也推进到 hourly portfolio path 后，弱点还在吗？</h2>
      <ul>
        <li><b>先说结论：</b>还在，而且读法更清楚了。把 breakout v0 放进统一资金曲线后，<code>test</code> 仍是负的，`20bps` hourly path 累计约 <code>{pct(hourly_split_map.get('test', {}).get('cumulative_net_return'))}</code>；而 <code>up</code> 环境也仍偏弱，累计约 <code>{pct(hourly_regime_map.get('up', {}).get('cumulative_net_return'))}</code>，max drawdown 约 <code>{pct(hourly_regime_map.get('up', {}).get('max_drawdown'))}</code>。</li>
        <li><b>哪块还站得住：</b><code>flat</code> 环境在同样口径下仍最像样，hourly path 累计约 <code>{pct(hourly_regime_map.get('flat', {}).get('cumulative_net_return'))}</code>；<code>validate</code> 也仍为正，累计约 <code>{pct(hourly_split_map.get('validate', {}).get('cumulative_net_return'))}</code>。</li>
        <li><b>这意味着什么：</b>把资金曲线做得更正式之后，breakout v0 依然更像 <b>conditional alpha</b>，而不是可以直接升格成通用 short。它的核心特征没有消失：更依赖 <code>flat</code>、更怕 <code>up</code>，后段 <code>test</code> 也还不够稳。</li>
      </ul>
      <h3>按 split 看 hourly portfolio path（20bps）</h3>
      {html_table(hourly_split_summary_display, percent_cols={'mean_hourly_return','cumulative_net_return','max_drawdown'}, float_cols={'mean_active_positions'})}
      <h3>按 regime 看 hourly portfolio path（20bps）</h3>
      {html_table(hourly_regime_summary_display, percent_cols={'mean_hourly_return','cumulative_net_return','max_drawdown'}, float_cols={'mean_active_positions'})}
      <p class="note">一句话版：`hourly path` 并没有推翻前面的 split / regime 读法，只是把它从“单笔统计偏弱”进一步落实成“统一资金曲线下依旧偏弱”。所以这条线目前更适合继续做环境 gate / sizing honesty，而不是升格成不分环境的通用 short。</p>
    </section>
    <section>
      <h2>把 hourly path 按活跃仓位数拆开后，真正拖累这条线的是“最拥挤时刻”吗？</h2>
      <ul>
        <li><b>先说结论：</b>目前看并不是。把 <code>raw / confirm_1 / avoid_fluctuating</code> 的 <code>20bps hourly path</code> 都按 <code>active_positions</code> 拆开后，最差的通常不是 <code>4</code> 仓同时持有，而更像是 <code>2</code> 仓并发这类“半拥挤、但没形成明显顺风”的小时段。</li>
        <li><b>raw 最明显的拖累桶：</b><code>2</code> 仓小时只占约 <code>{pct((hourly_active_bucket_compare.loc[(hourly_active_bucket_compare['strategy'].eq('raw_v0')) & (hourly_active_bucket_compare['active_positions'].eq(2)), 'hour_share'].iloc[0]) if hourly_active_bucket_compare is not None and not hourly_active_bucket_compare.empty and ((hourly_active_bucket_compare['strategy'] == 'raw_v0') & (hourly_active_bucket_compare['active_positions'] == 2)).any() else np.nan)}</code>，但 mean hourly return 约 <code>{pct((hourly_active_bucket_compare.loc[(hourly_active_bucket_compare['strategy'].eq('raw_v0')) & (hourly_active_bucket_compare['active_positions'].eq(2)), 'mean_hourly_return'].iloc[0]) if hourly_active_bucket_compare is not None and not hourly_active_bucket_compare.empty and ((hourly_active_bucket_compare['strategy'] == 'raw_v0') & (hourly_active_bucket_compare['active_positions'] == 2)).any() else np.nan)}</code>，负小时占比约 <code>{pct((hourly_active_bucket_compare.loc[(hourly_active_bucket_compare['strategy'].eq('raw_v0')) & (hourly_active_bucket_compare['active_positions'].eq(2)), 'negative_hour_share'].iloc[0]) if hourly_active_bucket_compare is not None and not hourly_active_bucket_compare.empty and ((hourly_active_bucket_compare['strategy'] == 'raw_v0') & (hourly_active_bucket_compare['active_positions'] == 2)).any() else np.nan)}</code>；相反 <code>4</code> 仓小时的 mean hourly return 仍约 <code>{pct((hourly_active_bucket_compare.loc[(hourly_active_bucket_compare['strategy'].eq('raw_v0')) & (hourly_active_bucket_compare['active_positions'].eq(4)), 'mean_hourly_return'].iloc[0]) if hourly_active_bucket_compare is not None and not hourly_active_bucket_compare.empty and ((hourly_active_bucket_compare['strategy'] == 'raw_v0') & (hourly_active_bucket_compare['active_positions'] == 4)).any() else np.nan)}</code>。</li>
        <li><b>confirm_1 / avoid_fluctuating 也给出同方向提示：</b><code>confirm_1</code> 的 <code>2</code> 仓小时 mean return 也仍为负（约 <code>{pct((hourly_active_bucket_compare.loc[(hourly_active_bucket_compare['strategy'].eq('confirm_1')) & (hourly_active_bucket_compare['active_positions'].eq(2)), 'mean_hourly_return'].iloc[0]) if hourly_active_bucket_compare is not None and not hourly_active_bucket_compare.empty and ((hourly_active_bucket_compare['strategy'] == 'confirm_1') & (hourly_active_bucket_compare['active_positions'] == 2)).any() else np.nan)}</code>），而 <code>avoid_fluctuating</code> 虽改善了 overall path，但 <code>2</code> 仓小时仍偏弱（约 <code>{pct((hourly_active_bucket_compare.loc[(hourly_active_bucket_compare['strategy'].eq('avoid_fluctuating')) & (hourly_active_bucket_compare['active_positions'].eq(2)), 'mean_hourly_return'].iloc[0]) if hourly_active_bucket_compare is not None and not hourly_active_bucket_compare.empty and ((hourly_active_bucket_compare['strategy'] == 'avoid_fluctuating') & (hourly_active_bucket_compare['active_positions'] == 2)).any() else np.nan)}</code>）。</li>
        <li><b>这对 sizing honesty 的含义：</b>当前更不支持“只要简单 cap 掉最拥挤的 <code>4</code> 仓时刻，问题就解决了”。更诚实的 next step 应该是：去看这些 <code>2</code> 仓弱小时到底更集中在哪类 <code>split / regime / symbol mix</code>，而不是先把所有高并发都当罪魁祸首。</li>
      </ul>
      {html_table(hourly_active_bucket_compare_display, percent_cols={'hour_share','mean_hourly_return','median_hourly_return','negative_hour_share','conditional_cumulative_return'})}
      <p class="note">表里的 <code>conditional_cumulative_return</code> 是“只把该活跃仓位桶对应的小时单独串起来复合”的条件性读法，不等于真实整条组合路径的收益贡献；它的作用只是帮助看清：当前最弱的小时桶究竟长什么样。</p>
      <h3>如果继续追 2 仓弱小时，它们更像卡在什么 symbol mix？</h3>
      <ul>
        <li><b>raw 的 2 仓弱小时并不是均匀撒开的：</b>按 symbol pair 拆开后，占比最大的就是 <code>{escape(str(raw_two_pos_main['symbol_pair'])) if raw_two_pos_main is not None else 'nan'}</code>，约占 raw 这类小时的 <code>{pct(raw_two_pos_main['hour_share_within_bucket']) if raw_two_pos_main is not None else 'nan'}</code>，mean hourly return 约 <code>{pct(raw_two_pos_main['mean_hourly_return']) if raw_two_pos_main is not None else 'nan'}</code>；而最差的 pair 是 <code>{escape(str(raw_two_pos_worst['symbol_pair'])) if raw_two_pos_worst is not None else 'nan'}</code>，mean hourly return 约 <code>{pct(raw_two_pos_worst['mean_hourly_return']) if raw_two_pos_worst is not None else 'nan'}</code>。</li>
        <li><b>avoid_fluctuating 的改善也更像“换了坏 pair 结构”，不是把所有 2 仓小时都修好：</b>gate 后占比最大的 pair 变成 <code>{escape(str(gate_two_pos_main['symbol_pair'])) if gate_two_pos_main is not None else 'nan'}</code>，mean hourly return 约 <code>{pct(gate_two_pos_main['mean_hourly_return']) if gate_two_pos_main is not None else 'nan'}</code>；同时最正向的 2 仓 pair 是 <code>{escape(str(gate_two_pos_best['symbol_pair'])) if gate_two_pos_best is not None else 'nan'}</code>，mean hourly return 约 <code>{pct(gate_two_pos_best['mean_hourly_return']) if gate_two_pos_best is not None else 'nan'}</code>。</li>
        <li><b>这对 sizing / gate follow-up 的含义：</b>当前更像是某些特定 pair mix（尤其带 <code>SOL</code> 的组合）在拖累 2 仓小时，而不是“所有 2 仓都天然差”。所以下一步比起盲目 cap 掉所有 2 仓或 4 仓，更该继续看这些 pair 到底集中在哪些 <code>split / regime</code> 里，再决定是否做更有针对性的 sizing / gate。</li>
      </ul>
      {html_table(hourly_two_position_symbol_mix_compare_display, percent_cols={'hour_share_within_bucket','mean_hourly_return','negative_hour_share','conditional_cumulative_return'})}
      <p class="note">这张表只看 <code>active_positions = 2</code> 的小时。它不是在说“某个币对组合本身可交易”，而是在告诉你：<b>当前 2 仓弱小时的拖累更像来自哪些并发 symbol mix</b>，从而帮助后面的 sizing / gate 设计少走弯路。</p>
      <h3>再把这些弱 pair 拆到 split / regime，它们更像后段问题还是环境问题？</h3>
      <ul>
        <li><b>raw 的最大覆盖拖累并不主要长在 test：</b>目前覆盖最大的弱 context 是 <code>{escape(str(raw_two_pos_context_main['symbol_pair'])) if raw_two_pos_context_main is not None else 'nan'}</code> 落在 <code>{escape(str(raw_two_pos_context_main['split_mix'])) if raw_two_pos_context_main is not None else 'nan'}</code> × <code>{escape(str(raw_two_pos_context_main['regime_mix'])) if raw_two_pos_context_main is not None else 'nan'}</code>，约 <code>{num(raw_two_pos_context_main['hours'], 0) if raw_two_pos_context_main is not None else 'nan'}</code> 小时、mean hourly return 约 <code>{pct(raw_two_pos_context_main['mean_hourly_return']) if raw_two_pos_context_main is not None else 'nan'}</code>。这说明 2 仓拖累并不只是“最后一段突然坏掉”，而是有一部分本来就长在训练阶段的特定环境里。</li>
        <li><b>真正像后段尾部的，是更窄的 ETH+SOL test pocket：</b>当前 raw 里最差的 test-context 是 <code>{escape(str(raw_two_pos_context_test_tail['symbol_pair'])) if raw_two_pos_context_test_tail is not None else 'nan'}</code> 落在 <code>{escape(str(raw_two_pos_context_test_tail['split_mix'])) if raw_two_pos_context_test_tail is not None else 'nan'}</code> × <code>{escape(str(raw_two_pos_context_test_tail['regime_mix'])) if raw_two_pos_context_test_tail is not None else 'nan'}</code>，虽然只有约 <code>{num(raw_two_pos_context_test_tail['hours'], 0) if raw_two_pos_context_test_tail is not None else 'nan'}</code> 小时，但 mean hourly return 约 <code>{pct(raw_two_pos_context_test_tail['mean_hourly_return']) if raw_two_pos_context_test_tail is not None else 'nan'}</code>，更像真正需要盯住的后段尾部口袋。</li>
        <li><b>avoid_fluctuating 修掉了一部分 broad drag，但残余问题更集中：</b>gate 后最大的残余弱 context 变成 <code>{escape(str(gate_two_pos_context_residual['symbol_pair'])) if gate_two_pos_context_residual is not None else 'nan'}</code> 落在 <code>{escape(str(gate_two_pos_context_residual['split_mix'])) if gate_two_pos_context_residual is not None else 'nan'}</code> × <code>{escape(str(gate_two_pos_context_residual['regime_mix'])) if gate_two_pos_context_residual is not None else 'nan'}</code>，约 <code>{num(gate_two_pos_context_residual['hours'], 0) if gate_two_pos_context_residual is not None else 'nan'}</code> 小时、mean hourly return 约 <code>{pct(gate_two_pos_context_residual['mean_hourly_return']) if gate_two_pos_context_residual is not None else 'nan'}</code>；这说明 gate 更像先把 <code>BTC+SOL</code> 这类 broad drag 压掉了，但 `ETH+SOL` 的 test / validate + up 残余还在。</li>
      </ul>
      {html_table(hourly_two_position_pair_context_compare_display, percent_cols={'hour_share_within_pair','mean_hourly_return','negative_hour_share','conditional_cumulative_return'})}
      <p class="note">这张表还是只看 <code>active_positions = 2</code> 的小时，但进一步把每个 weak pair 拆到了 <code>split_mix × regime_mix</code>。一句话版：当前 2 仓弱点既不是纯粹的“后段全线崩”，也不是单纯的“所有 up 都差”，而是已经收窄成几个更具体的 residual pockets——这正是下一刀最小条件化 sizing 应该瞄准的对象。</p>
      <h3>如果把动作收得更窄：只对 ETH+SOL 的 `test+validate × up` 残余口袋做半仓，会发生什么？</h3>
      <ul>
        <li><b>先说结论：</b>有改善，而且比“整块 ETH+SOL 都动手”更克制。不是把所有 <code>2</code> 仓都砍掉，也不是对全部 <code>ETH+SOL</code> 两仓小时做半仓，而只对 <code>avoid_fluctuating</code> 后仍出现的 <code>ETH-USD + SOL-USD @ validate/test × up</code> 做 <code>0.5x</code> 半仓；受影响约 <code>{num(gate_pair_size_row['affected_hours'], 0) if gate_pair_size_row is not None else 'nan'}</code>/<code>{num(pair_sizing_map.get('avoid_fluctuating', {}).get('active_hours'), 0)}</code> 个活跃小时（约 <code>{pct(gate_pair_size_row['affected_hour_share']) if gate_pair_size_row is not None else 'nan'}</code>）。</li>
        <li><b>整体路径：</b>gate-only 的 hourly path 在 <code>20bps</code> 下累计约 <code>{pct(pair_sizing_map.get('avoid_fluctuating', {}).get('cumulative_net_return'))}</code>、max drawdown 约 <code>{pct(pair_sizing_map.get('avoid_fluctuating', {}).get('max_drawdown'))}</code>；只在这块更窄的 residual context 上半仓后，对应约提升到 <code>{pct(gate_pair_size_row['cumulative_net_return']) if gate_pair_size_row is not None else 'nan'}</code>，而 max drawdown 基本维持在约 <code>{pct(gate_pair_size_row['max_drawdown']) if gate_pair_size_row is not None else 'nan'}</code>。</li>
        <li><b>被压的 pocket 本身：</b>这组 <code>validate/test × up</code> 小时原本条件累计约 <code>{pct(pair_sizing_map.get('avoid_fluctuating', {}).get('target_pair_conditional_return'))}</code>；做成 <code>0.5x</code> 后约收窄到 <code>{pct(gate_pair_size_row['target_pair_conditional_return']) if gate_pair_size_row is not None else 'nan'}</code>。也就是说，当前更像“只把最明确的 residual up 口袋磨钝一点”，而不是再次重写整条 breakout 路径。</li>
        <li><b>这意味着什么：</b>当前证据开始支持“<b>更窄的 context-conditioned sizing</b> 值得继续看”，但它仍只是比 pair-conditioned 再收一层的 first-pass 小切片，不是正式 sizing engine；下一步若继续，应该优先问这类改进是否能在更严格 holdout / walk-forward 下复现。</li>
      </ul>
      {html_table(pair_sizing_compare_display, percent_cols={'mean_hourly_return','cumulative_net_return','max_drawdown','affected_hour_share','target_pair_conditional_return'}, float_cols={'mean_active_positions'})}
      <h4>被半仓处理的 ETH+SOL `validate/test × up` 小时，主要长在哪些 context？</h4>
      {html_table(gate_eth_sol_target_context_display, percent_cols={'hour_share_within_pair','mean_hourly_return','negative_hour_share','conditional_cumulative_return'})}
      <p class="note">一句话版：在 <code>avoid_fluctuating</code> 已经落地的前提下，只再对 <code>ETH+SOL @ validate/test × up</code> 这块更窄的 residual context 做半仓，确实能把 hourly path 约从 <code>{pct(pair_sizing_map.get('avoid_fluctuating', {}).get('cumulative_net_return'))}</code> 再抬到约 <code>{pct(gate_pair_size_row['cumulative_net_return']) if gate_pair_size_row is not None else 'nan'}</code>；但这仍只是较晚段 promising slice，本身还不够成为默认候选。</p>
      <h4>如果把这刀更窄 sizing 放到更严格的 holdout 眼光下看，改善主要来自 validate，还是 pure test？</h4>
      <ul>
        <li><b>先说结论：</b>当前改善主要还是长在 <code>test + validate</code> overlap pocket，而不是已经在 pure <code>test</code> 里拿到很扎实的独立证据。</li>
        <li><b>影响小时分布：</b>这刀一共只动了 <code>{num(gate_pair_size_row['affected_hours'], 0) if gate_pair_size_row is not None else 'nan'}</code> 个小时，其中约 <code>{pair_sizing_holdout_map.get('test + validate', {}).get('hours', 'nan')}</code> 个属于 <code>test + validate</code> overlap，pure <code>test</code> 只有约 <code>{pair_sizing_holdout_map.get('test', {}).get('hours', 'nan')}</code> 个。</li>
        <li><b><code>test + validate</code> overlap：</b>条件累计约从 <code>{pct(pair_sizing_holdout_map.get('test + validate', {}).get('conditional_cumulative_before'))}</code> 收窄到 <code>{pct(pair_sizing_holdout_map.get('test + validate', {}).get('conditional_cumulative_after'))}</code>，改善约 <code>{num(pair_sizing_holdout_map.get('test + validate', {}).get('delta_pp'), 2)}pp</code>。</li>
        <li><b>pure <code>test</code>：</b>条件累计只从约 <code>{pct(pair_sizing_holdout_map.get('test', {}).get('conditional_cumulative_before'))}</code> 收窄到 <code>{pct(pair_sizing_holdout_map.get('test', {}).get('conditional_cumulative_after'))}</code>，改善约 <code>{num(pair_sizing_holdout_map.get('test', {}).get('delta_pp'), 2)}pp</code>；方向是对的，但样本还很薄。</li>
        <li><b>这意味着什么：</b>这刀更像“late-segment promising but not yet pure-test proven”。所以它已经值得保留为下一个 sizing 候选，但还不该直接升成 breakout 主原型的默认仓位规则。</li>
      </ul>
      {html_table(pair_sizing_holdout_split_display, percent_cols={'hour_share_within_target','conditional_cumulative_before','conditional_cumulative_after','mean_hourly_return_before','mean_hourly_return_after'}, float_cols={'delta_pp'})}
      <p class="note">一句话版：这刀更窄的 context-conditioned sizing 在更晚段确实有改善，但当前证据主要还是来自 <code>test + validate</code> overlap；pure <code>test</code> 只有很薄的一小段。所以它现在最像的下一步，不是直接升格，而是进更严格的 walk-forward / holdout honesty。</p>
      <h4>如果把它继续收窄到“只动 pure <code>test × up</code>”呢？</h4>
      <ul>
        <li><b>结果很克制，也说明证据确实还薄：</b>只对 <code>ETH+SOL @ test × up</code> 做半仓时，受影响约 <code>{str(int(pure_test_context_row['affected_hours'])) if pure_test_context_row is not None and not pd.isna(pure_test_context_row.get('affected_hours')) else 'nan'}</code>/<code>{pair_sizing_map.get('avoid_fluctuating', {}).get('active_hours', 'nan')}</code> 个活跃小时（约 <code>{pct(pure_test_context_row['affected_hour_share']) if pure_test_context_row is not None else 'nan'}</code>）。</li>
        <li><b>overall 路径：</b>gate-only 的 <code>20bps hourly path</code> 约从 <code>{pct(pair_sizing_map.get('avoid_fluctuating', {}).get('cumulative_net_return'))}</code> 只轻微抬到 <code>{pct(pure_test_context_row['overall_cumulative_net_return']) if pure_test_context_row is not None else 'nan'}</code>，增量约 <code>{num(pure_test_context_row['overall_delta_vs_gate_pp'], 2) if pure_test_context_row is not None else 'nan'}pp</code>；max drawdown 基本不变（仍约 <code>{pct(pure_test_context_row['max_drawdown']) if pure_test_context_row is not None else 'nan'}</code>）。</li>
        <li><b>pure <code>test</code> pocket 本身：</b>条件累计只从约 <code>{pct(pair_sizing_holdout_map.get('test', {}).get('conditional_cumulative_before'))}</code> 收窄到 <code>{pct(pair_sizing_holdout_map.get('test', {}).get('conditional_cumulative_after'))}</code>，改善约 <code>{num(pair_sizing_holdout_map.get('test', {}).get('delta_pp'), 2)}pp</code>；方向没错，但量级非常小。</li>
        <li><b>这意味着什么：</b>当前更窄的 context-conditioned branch 不能说无效，但它在更严格 <code>pure-test</code> 眼光下只剩一个很薄的 residual fix。它更像应该 <b>park 成诊断型分支</b>，而不是继续和 pair-conditioned 候选并列消耗主资源。</li>
      </ul>
      <h3>如果 breakout 线现在只能保留一个 sizing 候选，默认该留 pair-conditioned 还是更窄的 context-conditioned？</h3>
      <ul>
        <li><b>默认先留 pair-conditioned。</b> 原因不是它更“粗暴”，而是当前在同一套更严格口径下，它交出的整体改善更大、pure <code>test</code> 证据也没有比更窄 context 更薄。</li>
        <li><b>overall 路径：</b><code>ETH+SOL pair halfsize</code> 可把 gate-only 的 hourly path 约从 <code>{pct(pair_sizing_map.get('avoid_fluctuating', {}).get('cumulative_net_return'))}</code> 提到约 <code>{pct(sizing_candidate_compare.loc[sizing_candidate_compare['candidate'].eq('avoid_fluctuating_eth_sol_pair_halfsize'), 'overall_cumulative_net_return'].iloc[0]) if sizing_candidate_compare is not None and not sizing_candidate_compare.empty and (sizing_candidate_compare['candidate'] == 'avoid_fluctuating_eth_sol_pair_halfsize').any() else 'nan'}</code>，同时 max drawdown 约收窄到 <code>{pct(sizing_candidate_compare.loc[sizing_candidate_compare['candidate'].eq('avoid_fluctuating_eth_sol_pair_halfsize'), 'max_drawdown'].iloc[0]) if sizing_candidate_compare is not None and not sizing_candidate_compare.empty and (sizing_candidate_compare['candidate'] == 'avoid_fluctuating_eth_sol_pair_halfsize').any() else 'nan'}</code>；更窄的 <code>test+validate × up</code> context halfsize 则约到 <code>{pct(sizing_candidate_compare.loc[sizing_candidate_compare['candidate'].eq('avoid_fluctuating_eth_sol_test_validate_up_halfsize'), 'overall_cumulative_net_return'].iloc[0]) if sizing_candidate_compare is not None and not sizing_candidate_compare.empty and (sizing_candidate_compare['candidate'] == 'avoid_fluctuating_eth_sol_test_validate_up_halfsize').any() else 'nan'}</code>，但回撤基本没再改善。</li>
        <li><b>holdout 眼光：</b>pair-conditioned 的 pure <code>test</code> 约有 <code>{str(int(sizing_candidate_compare.loc[sizing_candidate_compare['candidate'].eq('avoid_fluctuating_eth_sol_pair_halfsize'), 'pure_test_hours'].iloc[0])) if sizing_candidate_compare is not None and not sizing_candidate_compare.empty and (sizing_candidate_compare['candidate'] == 'avoid_fluctuating_eth_sol_pair_halfsize').any() else 'nan'}</code> 小时、条件累计改善约 <code>{num(sizing_candidate_compare.loc[sizing_candidate_compare['candidate'].eq('avoid_fluctuating_eth_sol_pair_halfsize'), 'pure_test_delta_pp'].iloc[0], 2) if sizing_candidate_compare is not None and not sizing_candidate_compare.empty and (sizing_candidate_compare['candidate'] == 'avoid_fluctuating_eth_sol_pair_halfsize').any() else 'nan'}pp</code>；更窄的 <code>test+validate × up</code> context 只有约 <code>{str(int(sizing_candidate_compare.loc[sizing_candidate_compare['candidate'].eq('avoid_fluctuating_eth_sol_test_validate_up_halfsize'), 'pure_test_hours'].iloc[0])) if sizing_candidate_compare is not None and not sizing_candidate_compare.empty and (sizing_candidate_compare['candidate'] == 'avoid_fluctuating_eth_sol_test_validate_up_halfsize').any() else 'nan'}</code> 小时、改善约 <code>{num(sizing_candidate_compare.loc[sizing_candidate_compare['candidate'].eq('avoid_fluctuating_eth_sol_test_validate_up_halfsize'), 'pure_test_delta_pp'].iloc[0], 2) if sizing_candidate_compare is not None and not sizing_candidate_compare.empty and (sizing_candidate_compare['candidate'] == 'avoid_fluctuating_eth_sol_test_validate_up_halfsize').any() else 'nan'}pp</code>；继续收窄到 pure <code>test × up</code> 后，也只剩约 <code>{str(int(sizing_candidate_compare.loc[sizing_candidate_compare['candidate'].eq('avoid_fluctuating_eth_sol_test_up_halfsize'), 'affected_hours'].iloc[0])) if sizing_candidate_compare is not None and not sizing_candidate_compare.empty and (sizing_candidate_compare['candidate'] == 'avoid_fluctuating_eth_sol_test_up_halfsize').any() else 'nan'}</code> 个小时、overall 仅多约 <code>{num(sizing_candidate_compare.loc[sizing_candidate_compare['candidate'].eq('avoid_fluctuating_eth_sol_test_up_halfsize'), 'overall_delta_vs_gate_pp'].iloc[0], 2) if sizing_candidate_compare is not None and not sizing_candidate_compare.empty and (sizing_candidate_compare['candidate'] == 'avoid_fluctuating_eth_sol_test_up_halfsize').any() else 'nan'}pp</code>。这说明更窄 context 目前仍只是薄证据分支，而不是默认候选。</li>
        <li><b>更窄 context 仍有价值：</b>它影响面更小（约 <code>{pct(sizing_candidate_compare.loc[sizing_candidate_compare['candidate'].eq('avoid_fluctuating_eth_sol_test_validate_up_halfsize'), 'affected_hour_share'].iloc[0]) if sizing_candidate_compare is not None and not sizing_candidate_compare.empty and (sizing_candidate_compare['candidate'] == 'avoid_fluctuating_eth_sol_test_validate_up_halfsize').any() else 'nan'}</code> vs pair 的约 <code>{pct(sizing_candidate_compare.loc[sizing_candidate_compare['candidate'].eq('avoid_fluctuating_eth_sol_pair_halfsize'), 'affected_hour_share'].iloc[0]) if sizing_candidate_compare is not None and not sizing_candidate_compare.empty and (sizing_candidate_compare['candidate'] == 'avoid_fluctuating_eth_sol_pair_halfsize').any() else 'nan'}</code>），所以它更像后续 walk-forward 里值得继续观察的二级分支，而不是现在就该抢默认位。</li>
      </ul>
      {html_table(sizing_candidate_compare_display, percent_cols={'affected_hour_share','overall_cumulative_net_return','max_drawdown','target_conditional_return'}, float_cols={'overall_delta_vs_gate_pp','pure_test_delta_pp','test_validate_overlap_delta_pp'})}
      <p class="note">一句话版：在当前同一套更严格口径下，<code>ETH+SOL pair-conditioned halfsize</code> 仍应保留为 breakout 线的默认 sizing candidate；更窄的 context halfsize 分支在 pure-test 眼光下证据仍太薄，更适合先 park 成诊断型分支。</p>
      <h3>把默认候选再推进到更严格一点的 rolling / walk-forward honesty，会发现它是“全样本通吃”还是“只在后段发力”？</h3>
      <ul>
        <li><b>先说结论：</b>不是“全样本每一段都更好”，但也不只是随机 lucky patch。把 gate-only 与 <code>ETH+SOL pair-conditioned halfsize</code> 放进同一套 <code>10-day window / 5-day step</code> 的 rolling active-hour 对照后，前半段三格窗口基本没有触发 policy，因此结果与 gate-only 几乎重合；真正有动作的后半段 <code>{int(len(pair_walkforward_active)) if not pair_walkforward_active.empty else 0}</code> 个窗口里，pair-conditioned 都是 <b>收益更高、回撤更浅</b>。</li>
        <li><b>前半段为什么没有差异：</b>这不是“策略失灵”，而是那几格窗口里压根没有命中需要半仓的 `ETH+SOL` 两仓小时。所以更严格口径下最诚实的读法不是“6/6 全胜”，而是：<b>它的改善集中出现在 policy 真正触发的后半段</b>。</li>
        <li><b>后半段有动作的窗口：</b>从约 <code>{pair_walkforward_active_first['window_start'].strftime('%Y-%m-%d') if pair_walkforward_active_first is not None else 'nan'}</code> 开始到约 <code>{pair_walkforward_active_last['window_end'].strftime('%Y-%m-%d') if pair_walkforward_active_last is not None else 'nan'}</code>，每一格都比 gate-only 更好：累计提升大约在 <code>{num(pair_walkforward_active['delta_vs_gate_pp'].min(), 2) if not pair_walkforward_active.empty else 'nan'}pp ~ {num(pair_walkforward_active['delta_vs_gate_pp'].max(), 2) if not pair_walkforward_active.empty else 'nan'}pp</code>，回撤改善大约在 <code>{num(pair_walkforward_active['drawdown_improve_pp'].min(), 2) if not pair_walkforward_active.empty else 'nan'}pp ~ {num(pair_walkforward_active['drawdown_improve_pp'].max(), 2) if not pair_walkforward_active.empty else 'nan'}pp</code>。</li>
        <li><b>这意味着什么：</b>当前默认候选已经比“只在单张 overall 表里好看”更进一步——它至少经得住一个更严格的 rolling honesty slice；但它也还没强到能说成“所有时间段都稳定占优”。更诚实的结论是：<b>late-segment active windows 连续有效，足够继续保留默认位；同时仍应承认它是一个后段驱动、需继续观察迁移性的 sizing 候选。</b></li>
      </ul>
      {html_table(pair_walkforward_windows_display, percent_cols={'affected_hour_share','gate_cumulative_net_return','conditioned_cumulative_net_return','gate_max_drawdown','conditioned_max_drawdown'}, float_cols={'delta_vs_gate_pp','drawdown_improve_pp'})}
      <p class="note">这里的 rolling / walk-forward 仍是很克制的 first-pass：不是重新训练参数，而是在固定规则下按时间顺序做 <code>10-day / 5-day</code> 叠窗复核。它回答的是“改善是不是只靠一张总表幻觉”，不是正式 production walk-forward。</p>
      <h3>如果把 overlapping walk-forward 再压成更诚实的 non-overlap forward blocks，会发现它有多稳？</h3>
      <ul>
        <li><b>先说结论：</b>比前面的叠窗读法更克制，也更诚实。从第一次触发默认 <code>ETH+SOL pair halfsize</code> 的时点起，把后续 active period 压成 <code>4</code> 个不重叠的 <code>5-day</code> forward blocks 后，并不是 <code>4/4</code> 全都更好，而是约 <code>{int(len(pair_forward_blocks_positive)) if not pair_forward_blocks_positive.empty else 0}/{int(len(pair_forward_blocks_active)) if not pair_forward_blocks_active.empty else 0}</code> 个 block 改善、<code>{int(len(pair_forward_blocks_negative)) if not pair_forward_blocks_negative.empty else 0}</code> 个 block 略差。</li>
        <li><b>最好的 block：</b>约 <code>{pair_forward_blocks_best['block_start'].strftime('%Y-%m-%d') if pair_forward_blocks_best is not None else 'nan'}</code> 到 <code>{pair_forward_blocks_best['block_end'].strftime('%Y-%m-%d') if pair_forward_blocks_best is not None else 'nan'}</code>，相对 gate-only 的累计改善约 <code>{num(pair_forward_blocks_best['delta_vs_gate_pp'], 2) if pair_forward_blocks_best is not None else 'nan'}pp</code>，回撤也约改善 <code>{num(pair_forward_blocks_best['drawdown_improve_pp'], 2) if pair_forward_blocks_best is not None else 'nan'}pp</code>。</li>
        <li><b>最需要诚实承认的 block：</b>约 <code>{pair_forward_blocks_worst['block_start'].strftime('%Y-%m-%d') if pair_forward_blocks_worst is not None else 'nan'}</code> 到 <code>{pair_forward_blocks_worst['block_end'].strftime('%Y-%m-%d') if pair_forward_blocks_worst is not None else 'nan'}</code> 这格并没有继续变好，累计反而约比 gate-only 差 <code>{num(abs(pair_forward_blocks_worst['delta_vs_gate_pp']), 2) if pair_forward_blocks_worst is not None else 'nan'}pp</code>，而且回撤也没有额外改善。</li>
        <li><b>这意味着什么：</b>默认 sizing candidate 现在已经不只是“后半段碰巧一张总表更好”，因为 non-overlap blocks 里大多数仍是正向；但它也还不能写成“只要触发就稳定占优”。更诚实的 admission 读法应改成：<b>late-segment 证据从 hopeful 提高到 usable，但仍未强到可以跳过 one_more_gate。</b></li>
      </ul>
      {html_table(pair_forward_blocks_display, percent_cols={'affected_hour_share','gate_cumulative_net_return','conditioned_cumulative_net_return','gate_max_drawdown','conditioned_max_drawdown'}, float_cols={'delta_vs_gate_pp','drawdown_improve_pp'})}
      <p class="note">这张表和上面的 rolling 叠窗互补：前者回答“触发时方向是不是大体对的”，这张 non-overlap 表则回答“如果真按时间往前走，改善有没有一路单调延续”。当前答案是：<b>大体对，但不是单调稳定。</b></p>
      <h3>如果把 non-overlap forward block 再放长到 <code>10-day</code> 呢？</h3>
      <ul>
        <li><b>先说结论：</b>更长一点的 forward 眼光下，方向反而更整齐了，但样本也更少。从首个 sizing 触发时点开始，压成 <code>10-day</code> non-overlap blocks 后，当前有动作的约 <code>{int(len(pair_forward_blocks_10d_active)) if not pair_forward_blocks_10d_active.empty else 0}</code>/<code>{int(len(pair_forward_blocks_10d_display)) if pair_forward_blocks_10d_display is not None else 0}</code> 个 block 都仍优于 gate-only。</li>
        <li><b>最弱的那格也还是正向：</b>约 <code>{pair_forward_blocks_10d_worst['block_start'].strftime('%Y-%m-%d') if pair_forward_blocks_10d_worst is not None else 'nan'}</code> 到 <code>{pair_forward_blocks_10d_worst['block_end'].strftime('%Y-%m-%d') if pair_forward_blocks_10d_worst is not None else 'nan'}</code> 这格，相对 gate-only 的累计改善仍约 <code>{num(pair_forward_blocks_10d_worst['delta_vs_gate_pp'], 2) if pair_forward_blocks_10d_worst is not None else 'nan'}pp</code>，回撤也约改善 <code>{num(pair_forward_blocks_10d_worst['drawdown_improve_pp'], 2) if pair_forward_blocks_10d_worst is not None else 'nan'}pp</code>。</li>
        <li><b>最强 block：</b>约 <code>{pair_forward_blocks_10d_best['block_start'].strftime('%Y-%m-%d') if pair_forward_blocks_10d_best is not None else 'nan'}</code> 到 <code>{pair_forward_blocks_10d_best['block_end'].strftime('%Y-%m-%d') if pair_forward_blocks_10d_best is not None else 'nan'}</code>，累计改善约 <code>{num(pair_forward_blocks_10d_best['delta_vs_gate_pp'], 2) if pair_forward_blocks_10d_best is not None else 'nan'}pp</code>，回撤改善约 <code>{num(pair_forward_blocks_10d_best['drawdown_improve_pp'], 2) if pair_forward_blocks_10d_best is not None else 'nan'}pp</code>。</li>
        <li><b>这意味着什么：</b><code>5-day</code> block 告诉我们它不是单调稳定，<code>10-day</code> block 则说明把观察窗口稍微放长后，改善方向目前仍没有翻负。更诚实的 admission 读法因此应收紧成：<b>一般性的 late-segment transferability 担忧已经减弱，但 pure-test / down-tail 仍没被真正清掉。</b></li>
      </ul>
      {html_table(pair_forward_blocks_10d_display, percent_cols={'affected_hour_share','gate_cumulative_net_return','conditioned_cumulative_net_return','gate_max_drawdown','conditioned_max_drawdown'}, float_cols={'delta_vs_gate_pp','drawdown_improve_pp'})}
      <p class="note">一句话版：<code>5-day</code> non-overlap blocks 说明这刀不是“每小段都单调更好”；但把窗口放长到 <code>10-day</code> 后，当前有动作的 <code>{int(len(pair_forward_blocks_10d_positive)) if not pair_forward_blocks_10d_positive.empty else 0}/{int(len(pair_forward_blocks_10d_active)) if not pair_forward_blocks_10d_active.empty else 0}</code> 个 block 仍都优于 gate-only。也就是说，它现在更像“长一点仍大体站得住，但短一点仍会起伏”的 sizing candidate。</p>
      <h3>如果按 shadow review checkpoint 累积看：从首个触发日开始，5/10/15/20 天会不会中途翻负？</h3>
      <ul>
        <li><b>先说结论：</b>当前还没有翻负。把默认 <code>ETH+SOL pair halfsize</code> 从首个触发日开始，按更接近 shadow review 的累计 checkpoint 看，当前有动作的 <code>{int(len(pair_shadow_checkpoints_positive)) if not pair_shadow_checkpoints_positive.empty else 0}/{int(len(pair_shadow_checkpoints_active)) if not pair_shadow_checkpoints_active.empty else 0}</code> 个 <code>5/10/15/20-day</code> checkpoints 都仍优于 gate-only。</li>
        <li><b>最早的 checkpoint 也没有先甜后翻：</b><code>{int(pair_shadow_checkpoints_worst['review_days']) if pair_shadow_checkpoints_worst is not None else 'nan'}</code> 天 review 时，相对 gate-only 的累计改善仍约 <code>{num(pair_shadow_checkpoints_worst['delta_vs_gate_pp'], 2) if pair_shadow_checkpoints_worst is not None else 'nan'}pp</code>，回撤约改善 <code>{num(pair_shadow_checkpoints_worst['drawdown_improve_pp'], 2) if pair_shadow_checkpoints_worst is not None else 'nan'}pp</code>。</li>
        <li><b>更长一点的 cumulative read：</b>到 <code>{int(pair_shadow_checkpoints_last['review_days']) if pair_shadow_checkpoints_last is not None else 'nan'}</code> 天时，默认候选相对 gate-only 的累计改善约 <code>{num(pair_shadow_checkpoints_last['delta_vs_gate_pp'], 2) if pair_shadow_checkpoints_last is not None else 'nan'}pp</code>，回撤改善约 <code>{num(pair_shadow_checkpoints_last['drawdown_improve_pp'], 2) if pair_shadow_checkpoints_last is not None else 'nan'}pp</code>；最强 checkpoint 约出现在 <code>{int(pair_shadow_checkpoints_best['review_days']) if pair_shadow_checkpoints_best is not None else 'nan'}</code> 天，累计改善约 <code>{num(pair_shadow_checkpoints_best['delta_vs_gate_pp'], 2) if pair_shadow_checkpoints_best is not None else 'nan'}pp</code>。</li>
        <li><b>这意味着什么：</b>虽然 non-overlap <code>5-day</code> blocks 里仍出现过一格回吐，但如果按更 deployment-facing 的累计 shadow review 看，默认 sizing candidate 目前还没有出现“越往后看反而翻回 gate-only 下方”的现象。更诚实的读法因此是：<b>一般性 transferability 焦虑继续下降，但 blocker 仍主要卡在 pure-test / down-tail hard gap，而不是累计路径已经重新翻负。</b></li>
      </ul>
      {html_table(pair_shadow_checkpoints_display, percent_cols={'affected_hour_share','gate_cumulative_net_return','conditioned_cumulative_net_return','gate_max_drawdown','conditioned_max_drawdown'}, float_cols={'delta_vs_gate_pp','drawdown_improve_pp'})}
      <p class="note">一句话版：block 口径告诉我们它不是单调直线；但 cumulative shadow review checkpoints 目前是 <code>{int(len(pair_shadow_checkpoints_positive)) if not pair_shadow_checkpoints_positive.empty else 0}/{int(len(pair_shadow_checkpoints_active)) if not pair_shadow_checkpoints_active.empty else 0}</code> 持续为正，所以默认 <code>pair halfsize</code> 当前更像“还没过 gate，但 cumulative review 没翻负”的 shadow-admission 候选。</p>
      <h3>如果把视角再收紧成 strict pure-test tail：从首个 <code>test</code> 触发一直看到样本末尾，会发生什么？</h3>
      <ul>
        <li><b>先说结论：</b>方向暂时还是正的，但样本只剩一小段尾巴。从首个 pure <code>test</code> sizing 触发（约 <code>{pair_pure_test_tail_row['slice_start'].strftime('%Y-%m-%d %H:%M') if pair_pure_test_tail_row is not None else 'nan'}</code>）到当前样本末尾（约 <code>{pair_pure_test_tail_row['slice_end'].strftime('%Y-%m-%d %H:%M') if pair_pure_test_tail_row is not None else 'nan'}</code>），一共也只有约 <code>{int(pair_pure_test_tail_row['active_hours']) if pair_pure_test_tail_row is not None else 'nan'}</code> 个活跃小时，其中约 <code>{int(pair_pure_test_tail_row['affected_hours']) if pair_pure_test_tail_row is not None else 'nan'}</code> 个小时真的触发默认 <code>ETH+SOL pair halfsize</code>。</li>
        <li><b>这段 strict tail 的结果：</b>gate-only 的整段 tail 累计约 <code>{pct(pair_pure_test_tail_row['gate_cumulative_net_return']) if pair_pure_test_tail_row is not None else 'nan'}</code>，而默认 halfsize 约 <code>{pct(pair_pure_test_tail_row['conditioned_cumulative_net_return']) if pair_pure_test_tail_row is not None else 'nan'}</code>，相对改善约 <code>{num(pair_pure_test_tail_row['delta_vs_gate_pp'], 2) if pair_pure_test_tail_row is not None else 'nan'}pp</code>；回撤也约改善 <code>{num(pair_pure_test_tail_row['drawdown_improve_pp'], 2) if pair_pure_test_tail_row is not None else 'nan'}pp</code>。</li>
        <li><b>为什么这比“只看 5 个被动到的 test 小时”更硬一点：</b>因为它不是只盯条件 pocket 本身，而是把从首个 pure-test 触发到样本末尾的整段 portfolio tail 一起算进去。当前它没有翻负，说明 default sizing candidate 在 strict pure-test 眼光下还没被直接打穿。</li>
        <li><b>但为什么仍不能直接放行：</b>这整段 tail 本身也只有约 <code>{int(pair_pure_test_tail_row['active_hours']) if pair_pure_test_tail_row is not None else 'nan'}</code> 小时，而且受影响小时仍主要是 <code>up</code>（约 <code>{int(pair_pure_test_tail_row['up_hours']) if pair_pure_test_tail_row is not None else 'nan'}</code>）加少量 <code>down+flat</code>（约 <code>{int(pair_pure_test_tail_row['down_flat_hours']) if pair_pure_test_tail_row is not None else 'nan'}</code>），pure <code>down</code> 仍是 <code>{int(pair_pure_test_tail_row['down_hours']) if pair_pure_test_tail_row is not None else 'nan'}</code>。所以更诚实的读法应是：<b>strict pure-test tail 方向暂时为正，但证据仍太薄，不足以单独清掉 <code>one_more_gate</code>。</b></li>
      </ul>
      {html_table(pair_pure_test_tail_summary_display, percent_cols={'affected_hour_share','gate_cumulative_net_return','conditioned_cumulative_net_return','gate_max_drawdown','conditioned_max_drawdown','conditional_cumulative_before','conditional_cumulative_after'}, float_cols={'delta_vs_gate_pp','drawdown_improve_pp','conditional_delta_pp'})}
      <p class="note">一句话版：如果只看从首个 pure <code>test</code> 触发开始的严格尾段，这刀 default sizing 目前仍是正向的（约 <code>{num(pair_pure_test_tail_row['delta_vs_gate_pp'], 2) if pair_pure_test_tail_row is not None else 'nan'}pp</code>），但那也只是 <code>{int(pair_pure_test_tail_row['active_hours']) if pair_pure_test_tail_row is not None else 'nan'}</code> 小时的一小段 tail，不足以单独洗掉 admission blocker。</p>
      <h3>如果把 strict pure-test tail 再切成“晚段 mixed-tail pocket 进来前”的 <code>60/72h</code> checkpoints，会看到什么？</h3>
      <ul>
        <li><b>先说结论：</b>更克制地看，这段 tail 前半段其实只称得上“没翻负”，还称不上已经很厚。当前有动作的 <code>{'/'.join(pair_pure_test_tail_checkpoints_active['review_hours'].astype(int).astype(str).tolist()) if not pair_pure_test_tail_checkpoints_active.empty else '60/72'}</code> checkpoints 约有 <code>{int(len(pair_pure_test_tail_checkpoints_positive)) if not pair_pure_test_tail_checkpoints_positive.empty else 0}/{int(len(pair_pure_test_tail_checkpoints_active)) if not pair_pure_test_tail_checkpoints_active.empty else 0}</code> 个仍优于 gate-only，但最强也只有约 <code>{num(pair_pure_test_tail_checkpoints_best['delta_vs_gate_pp'], 2) if pair_pure_test_tail_checkpoints_best is not None else 'nan'}pp</code>，回撤改善约 <code>{num(pair_pure_test_tail_checkpoints_best['drawdown_improve_pp'], 2) if pair_pure_test_tail_checkpoints_best is not None else 'nan'}pp</code>。</li>
        <li><b>这比整段 tail 读法更诚实的地方：</b>如果先不把最后那段 <code>down + flat</code> mixed tail 算进去，到约 <code>{int(pair_pure_test_tail_checkpoints_last['review_hours']) if pair_pure_test_tail_checkpoints_last is not None else 'nan'}</code> 小时为止，default sizing 相对 gate-only 的累计改善其实还只有约 <code>{num(pair_pure_test_tail_checkpoints_last['delta_vs_gate_pp'], 2) if pair_pure_test_tail_checkpoints_last is not None else 'nan'}pp</code>；而整段 strict tail 最终约 <code>{num(pair_pure_test_tail_row['delta_vs_gate_pp'], 2) if pair_pure_test_tail_row is not None else 'nan'}pp</code> 的改善里，约 <code>{num(pair_pure_test_tail_row['delta_vs_gate_pp'] - pair_pure_test_tail_checkpoints_last['delta_vs_gate_pp'], 2) if pair_pure_test_tail_row is not None and pair_pure_test_tail_checkpoints_last is not None else 'nan'}pp</code> 是等到最后那两个 mixed-tail 小时才补上来的。</li>
        <li><b>所以怎么读：</b>这说明默认 <code>pair halfsize</code> 当前还不能写成“pure-test tail 自己已经厚实通过”。更准确的说法是：<b>前半段 pure-test tail 暂时没翻负，但 edge 仍很薄；后半段 mixed tail 虽补出增量，却也只够支撑 shadow-only gate。</b> 因此 breakout 的 blocker 仍是 <b>pure-test / down-tail honesty</b>，不是 wording 问题。</li>
      </ul>
      {html_table(pair_pure_test_tail_checkpoints_display, percent_cols={'affected_hour_share','gate_cumulative_net_return','conditioned_cumulative_net_return','gate_max_drawdown','conditioned_max_drawdown'}, float_cols={'delta_vs_gate_pp','drawdown_improve_pp'})}
      <p class="note">一句话版：strict pure-test tail 的总 delta 看起来约 <code>{num(pair_pure_test_tail_row['delta_vs_gate_pp'], 2) if pair_pure_test_tail_row is not None else 'nan'}pp</code>，但若先不把最后那两小时 mixed-tail pocket 算进去，前面 <code>{'/'.join(pair_pure_test_tail_checkpoints_active['review_hours'].astype(int).astype(str).tolist()) if not pair_pure_test_tail_checkpoints_active.empty else '60/72'}</code> checkpoints 其实都只有约 <code>{num(pair_pure_test_tail_checkpoints_best['delta_vs_gate_pp'], 2) if pair_pure_test_tail_checkpoints_best is not None else 'nan'}pp</code>。换句话说，default pair candidate 在更早的 pure-test tail 里还只是“没翻负”，不是“已经很厚”。</p>
      <h3>如果再强迫 strict pure-test tail 只按 non-overlap <code>6h</code> active blocks 讲话：它到底有几段真能独立站住？</h3>
      <ul>
        <li><b>先说结论：</b>目前几乎还站不成“多段可复用”的 pure-test honesty。把 strict pure-test tail 从首个 <code>test</code> 触发点起继续压成 non-overlap <code>6h</code> active blocks 后，当前真正满足最小 active block 门槛（至少 <code>4</code> 个活跃小时）的只有约 <code>{int(len(pair_pure_test_tail_blocks_active)) if not pair_pure_test_tail_blocks_active.empty else 0}</code>/<code>{pair_pure_test_tail_blocks_total}</code> 段，而且这唯一有动作的一段正好就是最后那格 <code>test × down+flat</code> mixed-tail pocket。</li>
        <li><b>这比 <code>60/72h</code> checkpoint 更苛刻的地方：</b>它不允许 sparse 小时靠前后静默区间一起凑累计结果。当前前面那 <code>3</code> 个 <code>test × up</code> 小时甚至连一个满足门槛的 <code>6h</code> active block 都凑不出来；真正能单独成块的，只有约 <code>{pair_pure_test_tail_blocks_best['block_start'].strftime('%Y-%m-%d %H:%M') if pair_pure_test_tail_blocks_best is not None else 'nan'}</code> 到 <code>{pair_pure_test_tail_blocks_best['block_end'].strftime('%Y-%m-%d %H:%M') if pair_pure_test_tail_blocks_best is not None else 'nan'}</code> 这段，delta 约 <code>{num(pair_pure_test_tail_blocks_best['delta_vs_gate_pp'], 2) if pair_pure_test_tail_blocks_best is not None else 'nan'}pp</code>，条件 pocket 自己约改善 <code>{num(pair_pure_test_tail_blocks_best['conditional_delta_pp'], 2) if pair_pure_test_tail_blocks_best is not None else 'nan'}pp</code>。</li>
        <li><b>所以 deployment-facing 该怎么读：</b>default pair candidate 当前还不能写成“strict pure-test tail 已经拆成多段都成立”。更诚实的版本是：<b>pure-test 前半段仍薄到连稳定 active block 都难以独立成形，最后那格 mixed-tail pocket 才是当前唯一能单独站住的 active block。</b> 这进一步说明 breakout 的 blocker 仍是 <b>pure-test / down-tail honesty</b>，不是页面措辞问题。</li>
      </ul>
      {html_table(pair_pure_test_tail_blocks_display, percent_cols={'affected_hour_share','gate_cumulative_net_return','conditioned_cumulative_net_return','gate_max_drawdown','conditioned_max_drawdown','conditional_cumulative_before','conditional_cumulative_after'}, float_cols={'delta_vs_gate_pp','drawdown_improve_pp','conditional_delta_pp'})}
      <p class="note">一句话版：strict pure-test tail 再压成 non-overlap <code>6h</code> active blocks 后，当前其实只剩 <code>{int(len(pair_pure_test_tail_blocks_active)) if not pair_pure_test_tail_blocks_active.empty else 0}</code> 段有动作，而且就是最后那格 <code>test × down+flat</code> mixed-tail pocket。也就是说，default pair candidate 还没有给出“多段独立可复用”的 pure-test honesty。</p>
      <h3>把这 44 个受影响小时按真实时间段拆开：default pair candidate 到底是靠哪几段在撑？</h3>
      <ul>
        <li><b>先说结论：</b>并不是一整段连续的 pure-test honesty。当前默认 <code>ETH+SOL pair halfsize</code> 的约 <code>{str(int(pair_default_row['affected_hours'])) if pair_default_row is not None and not pd.isna(pair_default_row.get('affected_hours')) else 'nan'}</code> 个受影响小时，按时间顺序实际只会塌缩成约 <code>{pair_default_episode_count}</code> 段连续 episode。</li>
        <li><b>最大的一段：</b>约 <code>{pair_default_episode_best['start_time'].strftime('%Y-%m-%d %H:%M') if pair_default_episode_best is not None else 'nan'}</code> 到 <code>{pair_default_episode_best['end_time'].strftime('%Y-%m-%d %H:%M') if pair_default_episode_best is not None else 'nan'}</code>，主要还是 <code>{pair_default_episode_best['split_mix'] if pair_default_episode_best is not None else 'nan'} × {pair_default_episode_best['regime_mix'] if pair_default_episode_best is not None else 'nan'}</code> 这段，条件累计改善约 <code>{num(pair_default_episode_best['delta_pp'], 2) if pair_default_episode_best is not None else 'nan'}pp</code>。</li>
        <li><b>对 admission 最关键的纯 test 读法：</b>真正的 pure <code>test</code> 其实只拆成两小段：前面那段 <code>test × up</code> 只有约 <code>{int(pair_default_episode_test_up['hours']) if pair_default_episode_test_up is not None else 'nan'}</code> 小时、条件累计改善约 <code>{num(pair_default_episode_test_up['delta_pp'], 2) if pair_default_episode_test_up is not None else 'nan'}pp</code>；最后那段 <code>test × down + flat</code> 只有约 <code>{int(pair_default_episode_test_downflat['hours']) if pair_default_episode_test_downflat is not None else 'nan'}</code> 小时，却贡献了约 <code>{num(pair_default_episode_test_downflat['delta_pp'], 2) if pair_default_episode_test_downflat is not None else 'nan'}pp</code>。</li>
        <li><b>这意味着什么：</b>更诚实的说法不是“default pair candidate 已经有一整段厚实 pure-test 证据”，而是：<b>它大头仍来自 overlap / earlier episodes，真正 pure-test 的前半段只给出 very thin 的约 <code>{num(pair_default_episode_test_up['delta_pp'], 2) if pair_default_episode_test_up is not None else 'nan'}pp</code>，最后再由那两小时 mixed-tail pocket 补上更多增量。</b> 所以 blocker 仍是 <b>pure-test / down-tail honesty</b>，不是页面措辞问题。</li>
      </ul>
      {html_table(pair_default_episode_summary_display, percent_cols={'hour_share_within_target','conditional_cumulative_before','conditional_cumulative_after','mean_hourly_return_before','mean_hourly_return_after'}, float_cols={'delta_pp'})}
      <p class="note">一句话版：把默认 pair candidate 的受影响小时按真实时间顺序拆开后，会发现它不是“整段 pure-test 都很厚”，而是 `train flat`、`test+validate up`、`test up`、`test down+flat` 这几段拼出来的；其中纯 test 前半段只有约 <code>{num(pair_default_episode_test_up['delta_pp'], 2) if pair_default_episode_test_up is not None else 'nan'}pp</code>，最后两小时 mixed-tail 才再补上约 <code>{num(pair_default_episode_test_downflat['delta_pp'], 2) if pair_default_episode_test_downflat is not None else 'nan'}pp</code>。</p>
      <h3>这刀默认 sizing 实际修到的是 <code>up/flat</code>，还是已经碰到 <code>down</code> 尾部？</h3>
      <ul>
        <li><b>先说结论：</b>目前主要修到的是 <code>up/flat</code>，还谈不上已经把 <code>down</code> 尾部洗干净。当前默认 <code>ETH+SOL pair halfsize</code> 一共只动到约 <code>{str(int(pair_default_row['affected_hours'])) if pair_default_row is not None and not pd.isna(pair_default_row.get('affected_hours')) else 'nan'}</code> 个小时，其中 <code>up</code> 约 <code>{pair_holdout_regime_map.get('up', {}).get('hours', 0)}</code> 个、<code>flat</code> 约 <code>{pair_holdout_regime_map.get('flat', {}).get('hours', 0)}</code> 个、<code>down + flat</code> 约 <code>{pair_holdout_regime_map.get('down + flat', {}).get('hours', 0)}</code> 个，而 pure <code>down</code> 当前是 <code>{pair_holdout_regime_map.get('down', {}).get('hours', 0)}</code> 个。</li>
        <li><b>改善量级：</b><code>up</code> 这块条件累计约从 <code>{pct(pair_holdout_regime_map.get('up', {}).get('conditional_cumulative_before'))}</code> 收窄到 <code>{pct(pair_holdout_regime_map.get('up', {}).get('conditional_cumulative_after'))}</code>，改善约 <code>{num(pair_holdout_regime_map.get('up', {}).get('delta_pp'), 2)}pp</code>；<code>flat</code> 约从 <code>{pct(pair_holdout_regime_map.get('flat', {}).get('conditional_cumulative_before'))}</code> 收窄到 <code>{pct(pair_holdout_regime_map.get('flat', {}).get('conditional_cumulative_after'))}</code>，改善约 <code>{num(pair_holdout_regime_map.get('flat', {}).get('delta_pp'), 2)}pp</code>。</li>
        <li><b>为什么这很关键：</b>这说明 pair-conditioned candidate 目前更像在修“后段里最明显的 <code>ETH+SOL</code> 反身性口袋”，而不是已经覆盖到 breakout 线 admission 最担心的 <code>down</code> regime tail。换句话说，当前 <code>one_more_gate</code> 的 blocker 之一不是抽象担忧，而是这刀默认 sizing <b>几乎还没真正碰到 pure <code>down</code> pocket</b>。</li>
      </ul>
      <h4>默认 pair-conditioned sizing：被动到的小时按 regime 看</h4>
      {html_table(pair_sizing_holdout_regime_display, percent_cols={'hour_share_within_target','conditional_cumulative_before','conditional_cumulative_after','mean_hourly_return_before','mean_hourly_return_after'}, float_cols={'delta_pp'})}
      <h4>默认 pair-conditioned sizing：被动到的小时按 split × regime 看</h4>
      {html_table(pair_sizing_holdout_split_regime_display, percent_cols={'hour_share_within_target','conditional_cumulative_before','conditional_cumulative_after','mean_hourly_return_before','mean_hourly_return_after'}, float_cols={'delta_pp'})}
      <p class="note">一句话版：默认 <code>ETH+SOL pair-conditioned halfsize</code> 这刀现在主要修到的是 <code>up</code> 和一部分 <code>flat</code> 小时；它对真正的 <code>down</code> 尾部几乎还没给出证据。所以 breakout 线当前最诚实的位置仍是 <b>shadow-admission queue / one_more_gate</b>，而不是“默认 policy 已可直接 shadow 跑”。</p>
      <h3>把它翻成 deployment hard-gate：当前 `down-tail coverage` 到底过线了吗？</h3>
      <ul>
        <li><b>先说结论：</b>还没过。默认 <code>ETH+SOL pair halfsize</code> 在 gate-only 的 <code>down</code> 小时里当前覆盖率约 <code>{pct(pair_down_coverage_row['policy_coverage_share']) if pair_down_coverage_row is not None else 'nan'}</code>（约 <code>{int(pair_down_coverage_row['policy_affected_hours']) if pair_down_coverage_row is not None else 'nan'}/{int(pair_down_coverage_row['gate_active_hours']) if pair_down_coverage_row is not None else 'nan'}</code>）。</li>
        <li><b>为什么这算 hard gap：</b>同一口径下 gate-only 的 <code>down</code> 段累计本身约 <code>{pct(pair_down_coverage_row['gate_cumulative_net_return']) if pair_down_coverage_row is not None else 'nan'}</code>，说明这是一个真实的尾部风险口袋；但当前默认 sizing 在 pure <code>down</code> 上没有任何触发点，因此还谈不上“已经对 down-tail 给出可验证的 admission 证据”。</li>
        <li><b>可执行读法：</b>在把这条线升格到 `shadow paper now` 之前，至少要先补出一刀能真正命中 <code>down</code> 小时的 sizing / protection honesty（哪怕只是 very small slice），否则 `one_more_gate` 不应被解除。</li>
      </ul>
      {html_table(pair_regime_coverage_audit_display, percent_cols={'gate_mean_hourly_return','gate_cumulative_net_return','policy_coverage_share'}, float_cols={'policy_conditional_delta_pp'})}
      <p class="note">一句话版：当前默认 sizing 在 <code>down</code> 的覆盖是 <code>0/100</code>。这不是文案问题，而是硬证据缺口；所以 `breakout` 还不能跳过 <code>one_more_gate</code>。</p>
      <h3>如果替它找更宽松的解释：它会不会其实在 pure <code>down</code> 到来前就提前减仓了？</h3>
      <ul>
        <li><b>先说结论：</b>当前样本里看不出这种“提前踩刹车”。把默认 <code>ETH+SOL pair halfsize</code> 的 active hours 里、所有“未来 <code>6/12/24h</code> 内会进入 pure <code>down</code>”的非-<code>down</code> bridge 小时单独拎出来看，命中数仍是 <code>{int(pair_predown_bridge_6h['affected_hours']) if pair_predown_bridge_6h is not None else 'nan'}/{int(pair_predown_bridge_6h['bridge_hours']) if pair_predown_bridge_6h is not None else 'nan'}</code>、<code>{int(pair_predown_bridge_12h['affected_hours']) if pair_predown_bridge_12h is not None else 'nan'}/{int(pair_predown_bridge_12h['bridge_hours']) if pair_predown_bridge_12h is not None else 'nan'}</code>、<code>{int(pair_predown_bridge_24h['affected_hours']) if pair_predown_bridge_24h is not None else 'nan'}/{int(pair_predown_bridge_24h['bridge_hours']) if pair_predown_bridge_24h is not None else 'nan'}</code>。</li>
        <li><b>最关键的一段：</b>离 pure <code>down</code> 最近的那段 bridge，其实就是一段 <code>{pair_predown_bridge_12h['split_mix_values'] if pair_predown_bridge_12h is not None else 'nan'}</code> × <code>{pair_predown_bridge_12h['regime_mix_values'] if pair_predown_bridge_12h is not None else 'nan'}</code> 的前置滑落；它在未来 <code>12h</code> 内会接上 pure <code>down</code>，自身累计却已经约 <code>{pct(pair_predown_bridge_12h['gate_cumulative_net_return']) if pair_predown_bridge_12h is not None else 'nan'}</code>，而 default pair 对这整段仍是 <code>0/{int(pair_predown_bridge_12h['bridge_hours']) if pair_predown_bridge_12h is not None else 'nan'}</code> 命中。</li>
        <li><b>deployment-facing 该怎么读：</b>这等于把一个潜在的借口也关掉了——当前缺口不只是“pure <code>down</code> 本身没碰到”，而是连样本里最接近 pure <code>down</code> 的前置 bridge 小时也几乎没被默认 pair candidate 识别。所以它暂时还不能被解释成“虽然没碰到 down，但至少有 anticipatory protection”。</li>
      </ul>
      {html_table(pair_predown_bridge_audit_display, percent_cols={'bridge覆盖率','gate累计','default pair累计'}, float_cols={'相对gate delta(pp)'})}
      <p class="note">一句话版：默认 pair candidate 现在不只是 <code>down-tail coverage = 0/100</code>；连未来 <code>6/12/24h</code> 会滑进 pure <code>down</code> 的 bridge 小时也还是 <code>0/x</code> 命中。也就是说，当前还不能把它解释成“提前减仓式”的 down-tail protection。</p>
      <h3>如果把 blocker 直接压成 <code>down-risk zone</code>（pure <code>down</code> + 会在未来滑进 pure <code>down</code> 的 bridge），mixed-tail 会不会更像诚实保护？</h3>
      <ul>
        <li><b>先说结论：</b>把 blocker 压成统一的 <code>down-risk zone</code> 之后，结果没有变松，反而只是把“有多远才勉强碰到”写得更清楚了：默认 pair candidate 在未来 <code>12/24/48h</code> 的 risk-zone 里仍是 <b>0 coverage</b>（分别约 <code>{int(default_downrisk_12h['affected_total_hours']) if default_downrisk_12h is not None else 'nan'}/{int(default_downrisk_12h['risk_zone_hours']) if default_downrisk_12h is not None else 'nan'}</code>、<code>{int(default_downrisk_24h['affected_total_hours']) if default_downrisk_24h is not None else 'nan'}/{int(default_downrisk_24h['risk_zone_hours']) if default_downrisk_24h is not None else 'nan'}</code>、<code>{int(default_downrisk_48h['affected_total_hours']) if default_downrisk_48h is not None else 'nan'}/{int(default_downrisk_48h['risk_zone_hours']) if default_downrisk_48h is not None else 'nan'}</code>）；直到放宽到 <code>72/96h</code> 才出现约 <code>{int(default_downrisk_72h['affected_total_hours']) if default_downrisk_72h is not None else 'nan'}/{int(default_downrisk_72h['risk_zone_hours']) if default_downrisk_72h is not None else 'nan'}</code>、<code>{int(default_downrisk_96h['affected_total_hours']) if default_downrisk_96h is not None else 'nan'}/{int(default_downrisk_96h['risk_zone_hours']) if default_downrisk_96h is not None else 'nan'}</code> 的命中，但这些也仍全部只是 bridge，而不是 pure <code>down</code>。</li>
        <li><b>mixed-tail 也只是更晚地擦到 bridge：</b>同一个 <code>down-risk zone</code> 用 <code>down+flat mixed-tail overlay</code> 再看，未来 <code>12/24/48h</code> 也仍是 <code>0/x</code>；到 <code>72/96h</code> 才各自约命中 <code>{int(mixed_downrisk_72h['affected_total_hours']) if mixed_downrisk_72h is not None else 'nan'}/{int(mixed_downrisk_72h['risk_zone_hours']) if mixed_downrisk_72h is not None else 'nan'}</code>、<code>{int(mixed_downrisk_96h['affected_total_hours']) if mixed_downrisk_96h is not None else 'nan'}/{int(mixed_downrisk_96h['risk_zone_hours']) if mixed_downrisk_96h is not None else 'nan'}</code>；其中 bridge 命中约 <code>{int(mixed_downrisk_72h['affected_bridge_hours']) if mixed_downrisk_72h is not None else 'nan'}/{int(mixed_downrisk_72h['bridge_hours']) if mixed_downrisk_72h is not None else 'nan'}</code>、<code>{int(mixed_downrisk_96h['affected_bridge_hours']) if mixed_downrisk_96h is not None else 'nan'}/{int(mixed_downrisk_96h['bridge_hours']) if mixed_downrisk_96h is not None else 'nan'}</code>，pure <code>down</code> 命中仍是 <code>{int(mixed_downrisk_96h['affected_pure_down_hours']) if mixed_downrisk_96h is not None else 'nan'}/{int(mixed_downrisk_96h['pure_down_hours']) if mixed_downrisk_96h is not None else 'nan'}</code>。</li>
        <li><b>deployment-facing 该怎么读：</b>这等于把 mixed-tail 的边界又收紧了一格——它不是 near-down protective gate，只是“要把窗口放宽到三四天，才开始擦到一点 bridge”的 shadow 观察项。因为不管看 pure <code>down</code> 本体，还是把 bridge 一并并进来，它当前都没有真正打到这条 hard blocker。</li>
      </ul>
      {html_table(downrisk_zone_audit_compare_display, percent_cols={'risk-zone覆盖率','pure-down覆盖率','bridge覆盖率','对照累计','policy累计'}, float_cols={'相对对照delta(pp)'})}
      <p class="note">一句话版：把 blocker 放宽到未来 <code>96h</code> 之后，default / mixed 终于会擦到一点 bridge，但 pure <code>down</code> 覆盖仍是 <code>0/63</code>。所以 mixed-tail 现在最多只能算“远距离 bridge shadow gate”，还不能被解释成真正碰到 near-down blocker 的 conditional policy。</p>
      <h3>反过来从 policy 自己的受影响小时看：它离下一段 pure <code>down</code> 到底有多远？</h3>
      <ul>
        <li><b>先说结论：</b>当前两条 policy 的受影响小时，离真正下一段 pure <code>down</code> 仍明显偏远。默认 <code>pair halfsize</code> 在未来 <code>24/48h</code> 内仍是 <code>{int(default_future_down_24h['matched_hours']) if default_future_down_24h is not None else 'nan'}/{int(default_future_down_24h['policy_affected_hours']) if default_future_down_24h is not None else 'nan'}</code>、<code>{int(default_future_down_48h['matched_hours']) if default_future_down_48h is not None else 'nan'}/{int(default_future_down_48h['policy_affected_hours']) if default_future_down_48h is not None else 'nan'}</code>；直到放宽到 <code>72/96h</code> 才变成 <code>{int(default_future_down_72h['matched_hours']) if default_future_down_72h is not None else 'nan'}/{int(default_future_down_72h['policy_affected_hours']) if default_future_down_72h is not None else 'nan'}</code>、<code>{int(default_future_down_96h['matched_hours']) if default_future_down_96h is not None else 'nan'}/{int(default_future_down_96h['policy_affected_hours']) if default_future_down_96h is not None else 'nan'}</code>。</li>
        <li><b>mixed-tail 也没有更贴近 blocker：</b>它在未来 <code>24/48h</code> 内同样还是 <code>{int(mixed_future_down_24h['matched_hours']) if mixed_future_down_24h is not None else 'nan'}/{int(mixed_future_down_24h['policy_affected_hours']) if mixed_future_down_24h is not None else 'nan'}</code>、<code>{int(mixed_future_down_48h['matched_hours']) if mixed_future_down_48h is not None else 'nan'}/{int(mixed_future_down_48h['policy_affected_hours']) if mixed_future_down_48h is not None else 'nan'}</code>；即便放到 <code>72/96h</code>，也只到 <code>{int(mixed_future_down_72h['matched_hours']) if mixed_future_down_72h is not None else 'nan'}/{int(mixed_future_down_72h['policy_affected_hours']) if mixed_future_down_72h is not None else 'nan'}</code>、<code>{int(mixed_future_down_96h['matched_hours']) if mixed_future_down_96h is not None else 'nan'}/{int(mixed_future_down_96h['policy_affected_hours']) if mixed_future_down_96h is not None else 'nan'}</code>。</li>
        <li><b>最关键的结构读法：</b>这些少量“未来终会接上 pure <code>down</code>”的命中，本质上也还是更早的 <code>{default_future_down_96h['split_mix_values'] if default_future_down_96h is not None else 'nan'}</code> × <code>{default_future_down_96h['regime_mix_values'] if default_future_down_96h is not None else 'nan'}</code>（default）与 <code>{mixed_future_down_96h['split_mix_values'] if mixed_future_down_96h is not None else 'nan'}</code> × <code>{mixed_future_down_96h['regime_mix_values'] if mixed_future_down_96h is not None else 'nan'}</code>（mixed）小时；最近 lead 也仍约是 <code>{int(default_future_down_96h['closest_lead_h']) if default_future_down_96h is not None else 'nan'}</code>h 与 <code>{int(mixed_future_down_96h['closest_lead_h']) if mixed_future_down_96h is not None else 'nan'}</code>h，而不是 near-down 的即时保护。</li>
        <li><b>deployment-facing 该怎么读：</b>这说明当前 blocker 不只是“risk-zone 里没 coverage”，而是 <b>policy 自己的 active hours 结构上就离 pure <code>down</code> 太远</b>；而且现有能勉强算 future-down-adjacent 的小时也都不是新的 <code>test</code> 证据。所以 mixed-tail 现在还不能被写成“更诚实地贴近 down-risk 的 conditional gate”。</li>
      </ul>
      {html_table(future_pure_down_lead_audit_compare_display, percent_cols={'命中占比'})}
      <p class="note">一句话版：就算反过来只看 policy 自己打到的小时，当前 default / mixed 也都不是在 near-down 口袋附近出手——<code>24/48h</code> 内仍是 <code>0/x</code>，真正能接上未来 pure <code>down</code> 的少量小时也还停留在更早的 train / overlap 残留里。于是 mixed-tail 还不能被包装成更诚实的 near-down conditional policy。</p>
      <h3>如果保留当前 pair candidate，再叠一刀最小 <code>down + flat</code> mixed-tail protection，会不会更像下一道 gate？</h3>
      <ul>
        <li><b>先说结论：</b>值得保留成 <b>one_more_gate candidate</b>，但还不够直接放行。做法很克制：不是推翻当前默认 <code>ETH+SOL pair halfsize</code>，而是只在它已经跑出来的 active hours 里，再对 <code>regime_mix = down + flat</code> 的小时额外做一次 <code>0.5x</code> protective halfsize。</li>
        <li><b>为什么盯这块而不是 pure <code>down</code>：</b>因为当前 strict pure-test tail 里，真正 forward-visible 的“偏下行”口袋本来就是一段 <code>down + flat</code> mixed tail；pure <code>down</code> 在这段 tail 里仍是 <code>{int(pair_downflat_overlay_tail_row['down_hours']) if pair_downflat_overlay_tail_row is not None else 0}</code> 小时。</li>
        <li><b>overall first-pass：</b>若在默认 pair candidate 上叠这刀 mixed-tail protection，统一 hourly path 累计可约从 <code>{pct(sizing_candidate_compare.loc[sizing_candidate_compare['candidate'].eq('avoid_fluctuating_eth_sol_pair_halfsize'), 'overall_cumulative_net_return'].iloc[0]) if sizing_candidate_compare is not None and not sizing_candidate_compare.empty and (sizing_candidate_compare['candidate'] == 'avoid_fluctuating_eth_sol_pair_halfsize').any() else 'nan'}</code> 抬到约 <code>{pct(pair_downflat_overlay_row['cumulative_net_return']) if pair_downflat_overlay_row is not None else 'nan'}</code>，max drawdown 也约从 <code>{pct(sizing_candidate_compare.loc[sizing_candidate_compare['candidate'].eq('avoid_fluctuating_eth_sol_pair_halfsize'), 'max_drawdown'].iloc[0]) if sizing_candidate_compare is not None and not sizing_candidate_compare.empty and (sizing_candidate_compare['candidate'] == 'avoid_fluctuating_eth_sol_pair_halfsize').any() else 'nan'}</code> 收窄到约 <code>{pct(pair_downflat_overlay_row['max_drawdown']) if pair_downflat_overlay_row is not None else 'nan'}</code>。</li>
        <li><b>别把 hard gap 误读成“pure <code>down</code> 一律砍半”：</b>若在同一个默认 pair candidate 上，机械地对所有 pure <code>down</code> active hours 也额外做一次 <code>0.5x</code>，虽然 max drawdown 会进一步约收窄到 <code>{pct(pair_down_overlay_row['max_drawdown']) if pair_down_overlay_row is not None else 'nan'}</code>，但 overall hourly path 反而会从约 <code>{pct(sizing_candidate_compare.loc[sizing_candidate_compare['candidate'].eq('avoid_fluctuating_eth_sol_pair_halfsize'), 'overall_cumulative_net_return'].iloc[0]) if sizing_candidate_compare is not None and not sizing_candidate_compare.empty and (sizing_candidate_compare['candidate'] == 'avoid_fluctuating_eth_sol_pair_halfsize').any() else 'nan'}</code> 回落到约 <code>{pct(pair_down_overlay_row['cumulative_net_return']) if pair_down_overlay_row is not None else 'nan'}</code>；而且这刀虽然打到了约 <code>{pair_down_overlay_affected_count}</code> 个 pure <code>down</code> 小时，却仍没有碰到当前 strict pure-test tail（那段 tail 里的 pure <code>down</code> 仍是 <code>{int(pair_pure_test_tail_row['down_hours']) if pair_pure_test_tail_row is not None else 0}</code>）。这说明 blunt pure-down overlay 现在更像过度保护，不是更好的 next gate。</li>
        <li><b>pure-test honesty：</b>当前这刀实际打到的 strict pure-test tail 就是一段约 <code>{int(pair_downflat_overlay_tail_row['active_hours']) if pair_downflat_overlay_tail_row is not None else 'nan'}</code> 小时的 mixed tail（其中受影响约 <code>{int(pair_downflat_overlay_tail_row['affected_hours']) if pair_downflat_overlay_tail_row is not None else 'nan'}</code> 小时）；该尾段累计约从 <code>{pct(pair_downflat_overlay_tail_row['gate_cumulative_net_return']) if pair_downflat_overlay_tail_row is not None else 'nan'}</code> 收窄到 <code>{pct(pair_downflat_overlay_tail_row['conditioned_cumulative_net_return']) if pair_downflat_overlay_tail_row is not None else 'nan'}</code>，delta 约 <code>{num(pair_downflat_overlay_tail_row['delta_vs_gate_pp'], 2) if pair_downflat_overlay_tail_row is not None else 'nan'}pp</code>，回撤也约改善 <code>{num(pair_downflat_overlay_tail_row['drawdown_improve_pp'], 2) if pair_downflat_overlay_tail_row is not None else 'nan'}pp</code>。</li>
        <li><b>为什么仍不能当 admission clearance：</b>因为这仍只是一个 very small protective overlay，而且证据仍主要从单段 <code>test</code> mixed tail 起家；它没有把 pure <code>down</code> coverage 缺口直接填平。即便再补上 rolling walk-forward shadow observation，当前也只能说明“不是单格 lucky pocket”，还不够把它升格成正式 clearance。</li>
      </ul>
      {html_table(pair_downflat_overlay_summary_display, percent_cols={'mean_hourly_return','cumulative_net_return','max_drawdown'})}
      <h4>这刀 mixed-tail overlay 打到哪些 split？</h4>
      {html_table(pair_downflat_overlay_holdout_split_display, percent_cols={'hour_share_within_target','conditional_cumulative_before','conditional_cumulative_after','mean_hourly_return_before','mean_hourly_return_after'}, float_cols={'delta_pp'})}
      <h4>strict pure-test mixed-tail snapshot</h4>
      {html_table(pair_downflat_overlay_tail_summary_display, percent_cols={'affected_hour_share','gate_cumulative_net_return','conditioned_cumulative_net_return','gate_max_drawdown','conditioned_max_drawdown','conditional_cumulative_before','conditional_cumulative_after'}, float_cols={'delta_vs_gate_pp','drawdown_improve_pp','conditional_delta_pp'})}
      <h4>如果只盯这段 strict pure-test mixed tail 的 <code>6/12/18/24h</code> 累计 checkpoints，它会不会很快失真？</h4>
      <ul>
        <li><b>先说结论：</b>目前还没有在这段尾巴里翻负，但 edge 衰减得很快。当前有动作的 <code>{int(len(pair_downflat_overlay_tail_checkpoints_positive)) if not pair_downflat_overlay_tail_checkpoints_positive.empty else 0}/{int(len(pair_downflat_overlay_tail_checkpoints_active)) if not pair_downflat_overlay_tail_checkpoints_active.empty else 0}</code> 个 <code>6/12/18/24h</code> checkpoints 仍优于默认 <code>pair halfsize</code> 基线。</li>
        <li><b>最强的一格：</b>约在 <code>{int(pair_downflat_overlay_tail_checkpoints_best['review_hours']) if pair_downflat_overlay_tail_checkpoints_best is not None else 'nan'}</code> 小时时，相对基线累计改善约 <code>{num(pair_downflat_overlay_tail_checkpoints_best['delta_vs_gate_pp'], 2) if pair_downflat_overlay_tail_checkpoints_best is not None else 'nan'}pp</code>，回撤改善约 <code>{num(pair_downflat_overlay_tail_checkpoints_best['drawdown_improve_pp'], 2) if pair_downflat_overlay_tail_checkpoints_best is not None else 'nan'}pp</code>。</li>
        <li><b>最需要诚实承认的一格：</b>到 <code>{int(pair_downflat_overlay_tail_checkpoints_worst['review_hours']) if pair_downflat_overlay_tail_checkpoints_worst is not None else 'nan'}</code> 小时时，相对基线累计改善已只剩约 <code>{num(pair_downflat_overlay_tail_checkpoints_worst['delta_vs_gate_pp'], 2) if pair_downflat_overlay_tail_checkpoints_worst is not None else 'nan'}pp</code>；也就是说，它虽然没立刻翻负，但到了更接近完整尾段的 checkpoint，edge 已经很薄。</li>
        <li><b>怎么读这层证据：</b>这说明 mixed-tail overlay 不是“只靠最后一个终点数字碰巧为正”的假 patch；但它在 strict pure-test tail 里的优势也没有稳定扩张，反而更像前几小时较明显、随后快速压扁的 protective edge。所以它仍更适合写成 <b>shadow-only mixed gate</b>，而不是 promotion-ready conditional policy。</li>
      </ul>
      {html_table(pair_downflat_overlay_tail_checkpoints_display, percent_cols={'affected_hour_share','gate_cumulative_net_return','conditioned_cumulative_net_return','gate_max_drawdown','conditioned_max_drawdown'}, float_cols={'delta_vs_gate_pp','drawdown_improve_pp'})}
      <p class="note">一句话版：strict pure-test mixed tail 的 <code>6/12/18/24h</code> checkpoints 当前虽然约 <code>{int(len(pair_downflat_overlay_tail_checkpoints_positive)) if not pair_downflat_overlay_tail_checkpoints_positive.empty else 0}/{int(len(pair_downflat_overlay_tail_checkpoints_active)) if not pair_downflat_overlay_tail_checkpoints_active.empty else 0}</code> 仍为正，但 edge 已从最强的约 <code>{num(pair_downflat_overlay_tail_checkpoints_best['delta_vs_gate_pp'], 2) if pair_downflat_overlay_tail_checkpoints_best is not None else 'nan'}pp</code> 收窄到最薄约 <code>{num(pair_downflat_overlay_tail_checkpoints_worst['delta_vs_gate_pp'], 2) if pair_downflat_overlay_tail_checkpoints_worst is not None else 'nan'}pp</code>。这更像“方向没塌，但很薄”，还不足以把 mixed-tail 从 shadow-only 提升成 clearance patch。</p>
      <h4>如果把这段 strict pure-test mixed tail 压成更前瞻的 non-overlap <code>6h</code> blocks，结论还会一致吗？</h4>
      <ul>
        <li><b>先说结论：</b>不会一致为正。当前有效的 <code>6h</code> active blocks 约有 <code>{int(len(pair_downflat_overlay_tail_blocks_positive)) if not pair_downflat_overlay_tail_blocks_positive.empty else 0}/{int(len(pair_downflat_overlay_tail_blocks_active)) if not pair_downflat_overlay_tail_blocks_active.empty else 0}</code> 个相对默认 <code>pair halfsize</code> 仍为正，另约 <code>{int(len(pair_downflat_overlay_tail_blocks_non_improving)) if not pair_downflat_overlay_tail_blocks_non_improving.empty else 0}</code> 个已转负。</li>
        <li><b>最好的 block：</b>第 <code>{int(pair_downflat_overlay_tail_blocks_best['block_id']) if pair_downflat_overlay_tail_blocks_best is not None else 'nan'}</code> 格（约 <code>{pair_downflat_overlay_tail_blocks_best['block_start'].strftime('%Y-%m-%d %H:%M') if pair_downflat_overlay_tail_blocks_best is not None else 'nan'}</code> 到 <code>{pair_downflat_overlay_tail_blocks_best['block_end'].strftime('%Y-%m-%d %H:%M') if pair_downflat_overlay_tail_blocks_best is not None else 'nan'}</code>）相对基线累计约改善 <code>{num(pair_downflat_overlay_tail_blocks_best['delta_vs_gate_pp'], 2) if pair_downflat_overlay_tail_blocks_best is not None else 'nan'}pp</code>，回撤约改善 <code>{num(pair_downflat_overlay_tail_blocks_best['drawdown_improve_pp'], 2) if pair_downflat_overlay_tail_blocks_best is not None else 'nan'}pp</code>。</li>
        <li><b>最弱的 block：</b>第 <code>{int(pair_downflat_overlay_tail_blocks_worst['block_id']) if pair_downflat_overlay_tail_blocks_worst is not None else 'nan'}</code> 格（约 <code>{pair_downflat_overlay_tail_blocks_worst['block_start'].strftime('%Y-%m-%d %H:%M') if pair_downflat_overlay_tail_blocks_worst is not None else 'nan'}</code> 到 <code>{pair_downflat_overlay_tail_blocks_worst['block_end'].strftime('%Y-%m-%d %H:%M') if pair_downflat_overlay_tail_blocks_worst is not None else 'nan'}</code>）相对基线累计约 <code>{num(pair_downflat_overlay_tail_blocks_worst['delta_vs_gate_pp'], 2) if pair_downflat_overlay_tail_blocks_worst is not None else 'nan'}pp</code>，说明它在更前瞻口径下会出现阶段性回吐。</li>
        <li><b>这层证据的 deployment 读法：</b>mixed-tail 不是“纯 lucky 一格”，但也还不是“每段都稳定更优”的 conditional policy；更诚实的位置仍是 <b>shadow-only mixed gate</b>。</li>
      </ul>
      {html_table(pair_downflat_overlay_tail_blocks_display, percent_cols={'affected_hour_share','gate_cumulative_net_return','conditioned_cumulative_net_return','gate_max_drawdown','conditioned_max_drawdown','conditional_cumulative_before','conditional_cumulative_after'}, float_cols={'delta_vs_gate_pp','drawdown_improve_pp','conditional_delta_pp'})}
      <p class="note">一句话版：把 strict pure-test mixed tail 再压成 non-overlap <code>6h</code> blocks 后，结果约是 <code>{int(len(pair_downflat_overlay_tail_blocks_positive)) if not pair_downflat_overlay_tail_blocks_positive.empty else 0}/{int(len(pair_downflat_overlay_tail_blocks_active)) if not pair_downflat_overlay_tail_blocks_active.empty else 0}</code> 正、<code>{int(len(pair_downflat_overlay_tail_blocks_non_improving)) if not pair_downflat_overlay_tail_blocks_non_improving.empty else 0}</code> 负。它说明 mixed-tail 方向没死，但仍不够稳，不能改写到 clearance verdict。</p>
      <h4>如果先按 <code>10-day window / 5-day step</code> 的 rolling walk-forward shadow observation 看，这刀会不会只是一格 lucky pocket？</h4>
      <ul>
        <li><b>先说结论：</b>至少目前看，不像只有一格 lucky pocket。当前真正触发 mixed-tail overlay 的 rolling active windows 约有 <code>{int(len(pair_downflat_overlay_walkforward_positive)) if not pair_downflat_overlay_walkforward_positive.empty else 0}/{int(len(pair_downflat_overlay_walkforward_active)) if not pair_downflat_overlay_walkforward_active.empty else 0}</code> 个仍优于默认 <code>pair halfsize</code> 基线，而且从约 <code>{pair_downflat_overlay_walkforward_first['window_start'].strftime('%Y-%m-%d') if pair_downflat_overlay_walkforward_first is not None else 'nan'}</code> 到 <code>{pair_downflat_overlay_walkforward_last['window_end'].strftime('%Y-%m-%d') if pair_downflat_overlay_walkforward_last is not None else 'nan'}</code> 的 active 段没有出现累计收益转负的窗口。</li>
        <li><b>最好的 rolling 窗口：</b>约 <code>{pair_downflat_overlay_walkforward_best['window_start'].strftime('%Y-%m-%d') if pair_downflat_overlay_walkforward_best is not None else 'nan'}</code> 到 <code>{pair_downflat_overlay_walkforward_best['window_end'].strftime('%Y-%m-%d') if pair_downflat_overlay_walkforward_best is not None else 'nan'}</code>，相对基线累计约改善 <code>{num(pair_downflat_overlay_walkforward_best['delta_vs_gate_pp'], 2) if pair_downflat_overlay_walkforward_best is not None else 'nan'}pp</code>，回撤约改善 <code>{num(pair_downflat_overlay_walkforward_best['drawdown_improve_pp'], 2) if pair_downflat_overlay_walkforward_best is not None else 'nan'}pp</code>。</li>
        <li><b>但为什么仍不能当 clearance：</b>因为这层 rolling 口径本身仍是 overlap windows，最弱 active 窗口虽然累计还约改善 <code>{num(pair_downflat_overlay_walkforward_worst['delta_vs_gate_pp'], 2) if pair_downflat_overlay_walkforward_worst is not None else 'nan'}pp</code>，但回撤改善并不稳定（最弱窗口约 <code>{num(pair_downflat_overlay_walkforward_worst['drawdown_improve_pp'], 2) if pair_downflat_overlay_walkforward_worst is not None else 'nan'}pp</code>），而且更克制的 non-overlap forward blocks 依然会给出 split verdict。</li>
      </ul>
      {html_table(pair_downflat_overlay_walkforward_windows_display, percent_cols={'affected_hour_share','gate_cumulative_net_return','conditioned_cumulative_net_return','gate_max_drawdown','conditioned_max_drawdown'}, float_cols={'delta_vs_gate_pp','drawdown_improve_pp'})}
      <h4>如果把这刀 mixed-tail overlay 再压成更前瞻的 non-overlap forward blocks，它还站得住吗？</h4>
      <ul>
        <li><b>先说结论：</b>比单段 tail 更诚实，但也还没强到能直接放行。把 <code>ETH+SOL pair halfsize</code> 当基线、把 mixed-tail overlay 当“下一刀 protective gate”后，当前有动作的 <code>5-day</code> forward blocks 约有 <code>{int(len(pair_downflat_overlay_forward_blocks_positive)) if not pair_downflat_overlay_forward_blocks_positive.empty else 0}/{int(len(pair_downflat_overlay_forward_blocks_active)) if not pair_downflat_overlay_forward_blocks_active.empty else 0}</code> 个仍优于基线；更长的 <code>10-day</code> blocks 则约有 <code>{int(len(pair_downflat_overlay_forward_blocks_10d_positive)) if not pair_downflat_overlay_forward_blocks_10d_positive.empty else 0}/{int(len(pair_downflat_overlay_forward_blocks_10d_active)) if not pair_downflat_overlay_forward_blocks_10d_active.empty else 0}</code> 个为正。</li>
        <li><b>最好的 <code>5-day</code> block：</b>约 <code>{pair_downflat_overlay_forward_blocks_best['block_start'].strftime('%Y-%m-%d') if pair_downflat_overlay_forward_blocks_best is not None else 'nan'}</code> 到 <code>{pair_downflat_overlay_forward_blocks_best['block_end'].strftime('%Y-%m-%d') if pair_downflat_overlay_forward_blocks_best is not None else 'nan'}</code>，相对基线累计改善约 <code>{num(pair_downflat_overlay_forward_blocks_best['delta_vs_gate_pp'], 2) if pair_downflat_overlay_forward_blocks_best is not None else 'nan'}pp</code>，回撤也约改善 <code>{num(pair_downflat_overlay_forward_blocks_best['drawdown_improve_pp'], 2) if pair_downflat_overlay_forward_blocks_best is not None else 'nan'}pp</code>；而且这格里真正被它打到的 mixed-tail target pocket 自己也约改善 <code>{num(pair_downflat_overlay_forward_blocks_best['conditional_delta_pp'], 2) if pair_downflat_overlay_forward_blocks_best is not None else 'nan'}pp</code>。</li>
        <li><b>最需要诚实承认的 <code>5-day</code> block：</b>约 <code>{pair_downflat_overlay_forward_blocks_worst['block_start'].strftime('%Y-%m-%d') if pair_downflat_overlay_forward_blocks_worst is not None else 'nan'}</code> 到 <code>{pair_downflat_overlay_forward_blocks_worst['block_end'].strftime('%Y-%m-%d') if pair_downflat_overlay_forward_blocks_worst is not None else 'nan'}</code>，相对基线累计约 <code>{num(pair_downflat_overlay_forward_blocks_worst['delta_vs_gate_pp'], 2) if pair_downflat_overlay_forward_blocks_worst is not None else 'nan'}pp</code>，而且 target pocket 自己的条件累计也约从 <code>{pct(pair_downflat_overlay_forward_blocks_worst['conditional_cumulative_before']) if pair_downflat_overlay_forward_blocks_worst is not None else 'nan'}</code> 回落到 <code>{pct(pair_downflat_overlay_forward_blocks_worst['conditional_cumulative_after']) if pair_downflat_overlay_forward_blocks_worst is not None else 'nan'}</code>（约 <code>{num(pair_downflat_overlay_forward_blocks_worst['conditional_delta_pp'], 2) if pair_downflat_overlay_forward_blocks_worst is not None else 'nan'}pp</code>）。这说明它现在不是“整体 path 被非目标小时稀释”这么简单，而是真正出现了 <b>conditional pocket 自己也会翻弱</b> 的 block。</li>
        <li><b>所以怎么读这张表：</b>有动作的 <code>5-day</code> active blocks 不只是 overall 路径上 `1/2` 正、`1/2` 负；就连 target mixed-tail pocket 自己也约是 <code>{int(len(pair_downflat_overlay_forward_blocks_conditional_positive)) if not pair_downflat_overlay_forward_blocks_conditional_positive.empty else 0}/{int(len(pair_downflat_overlay_forward_blocks_active)) if not pair_downflat_overlay_forward_blocks_active.empty else 0}</code> 正、<code>{int(len(pair_downflat_overlay_forward_blocks_conditional_negative)) if not pair_downflat_overlay_forward_blocks_conditional_negative.empty else 0}/{int(len(pair_downflat_overlay_forward_blocks_active)) if not pair_downflat_overlay_forward_blocks_active.empty else 0}</code> 负。换句话说，这刀现在还不能被包装成“target pocket 本身已稳定受益”的 conditional policy。</li>
        <li><b>更长一点看：</b><code>10-day</code> 口径下，最弱 active block 约 <code>{pair_downflat_overlay_forward_blocks_10d_worst['block_start'].strftime('%Y-%m-%d') if pair_downflat_overlay_forward_blocks_10d_worst is not None else 'nan'}</code> 到 <code>{pair_downflat_overlay_forward_blocks_10d_worst['block_end'].strftime('%Y-%m-%d') if pair_downflat_overlay_forward_blocks_10d_worst is not None else 'nan'}</code>，相对基线累计约 <code>{num(pair_downflat_overlay_forward_blocks_10d_worst['delta_vs_gate_pp'], 2) if pair_downflat_overlay_forward_blocks_10d_worst is not None else 'nan'}pp</code>，对应 target pocket 自己的条件累计也约 <code>{num(pair_downflat_overlay_forward_blocks_10d_worst['conditional_delta_pp'], 2) if pair_downflat_overlay_forward_blocks_10d_worst is not None else 'nan'}pp</code>；最好的一格约改善 <code>{num(pair_downflat_overlay_forward_blocks_10d_best['delta_vs_gate_pp'], 2) if pair_downflat_overlay_forward_blocks_10d_best is not None else 'nan'}pp</code>。这说明把窗口放长后，它也没有自动变成稳定单调的 gate，而仍是 <b>mixed-but-not-dead</b> 的 protective candidate。</li>
      </ul>
      {html_table(pair_downflat_overlay_forward_blocks_display, percent_cols={'affected_hour_share','gate_cumulative_net_return','conditioned_cumulative_net_return','gate_max_drawdown','conditioned_max_drawdown','conditional_cumulative_before','conditional_cumulative_after'}, float_cols={'delta_vs_gate_pp','drawdown_improve_pp','conditional_delta_pp'})}
      <h4>mixed-tail overlay 的 <code>10-day</code> forward blocks</h4>
      {html_table(pair_downflat_overlay_forward_blocks_10d_display, percent_cols={'affected_hour_share','gate_cumulative_net_return','conditioned_cumulative_net_return','gate_max_drawdown','conditioned_max_drawdown','conditional_cumulative_before','conditional_cumulative_after'}, float_cols={'delta_vs_gate_pp','drawdown_improve_pp','conditional_delta_pp'})}
      <p class="note">一句话版：<code>pair halfsize + down+flat mixed-tail protection</code> 这刀已经不只是单格 pocket——active rolling walk-forward 窗口当前约 <code>{int(len(pair_downflat_overlay_walkforward_positive)) if not pair_downflat_overlay_walkforward_positive.empty else 0}/{int(len(pair_downflat_overlay_walkforward_active)) if not pair_downflat_overlay_walkforward_active.empty else 0}</code> 个仍为正；但一压成更克制的 non-overlap forward blocks，<code>5-day</code> 与 <code>10-day</code> 仍都是 <code>1/2</code> 正、<code>1/2</code> 负。更关键的是，这个 split verdict 不是被非目标小时稀释出来的假象：target mixed-tail pocket 自己在 active <code>5-day</code> blocks 里也约是 <code>{int(len(pair_downflat_overlay_forward_blocks_conditional_positive)) if not pair_downflat_overlay_forward_blocks_conditional_positive.empty else 0}/{int(len(pair_downflat_overlay_forward_blocks_active)) if not pair_downflat_overlay_forward_blocks_active.empty else 0}</code> 正。更诚实的位置因此仍不是“快过 gate 了”，而是 <b>still shadow-only / promising but mixed gate candidate</b>。</p>
      <h4>如果把 mixed-tail overlay 也翻成 cumulative shadow review checkpoints，它会不会比 non-overlap blocks 更稳？</h4>
      <ul>
        <li><b>先说结论：</b>会更稳一些，但还没稳到能改写 verdict。把 mixed-tail overlay 从首个触发日开始，按 <code>5/10/15/20-day</code> cumulative review checkpoint 看，当前有动作的 <code>{int(len(pair_downflat_overlay_shadow_checkpoints_positive)) if not pair_downflat_overlay_shadow_checkpoints_positive.empty else 0}/{int(len(pair_downflat_overlay_shadow_checkpoints_active)) if not pair_downflat_overlay_shadow_checkpoints_active.empty else 0}</code> 个 checkpoint 仍优于默认 <code>pair halfsize</code> 基线。</li>
        <li><b>最需要诚实承认的 checkpoint：</b><code>{int(pair_downflat_overlay_shadow_checkpoints_worst['review_days']) if pair_downflat_overlay_shadow_checkpoints_worst is not None else 'nan'}</code> 天 review 时，相对基线累计仍只有约 <code>{num(pair_downflat_overlay_shadow_checkpoints_worst['delta_vs_gate_pp'], 2) if pair_downflat_overlay_shadow_checkpoints_worst is not None else 'nan'}pp</code>，回撤改善约 <code>{num(pair_downflat_overlay_shadow_checkpoints_worst['drawdown_improve_pp'], 2) if pair_downflat_overlay_shadow_checkpoints_worst is not None else 'nan'}pp</code>；这说明它就算没翻负，也还只是 very-thin edge。</li>
        <li><b>更长一点的 cumulative read：</b>到 <code>{int(pair_downflat_overlay_shadow_checkpoints_last['review_days']) if pair_downflat_overlay_shadow_checkpoints_last is not None else 'nan'}</code> 天时，相对默认基线的累计改善约 <code>{num(pair_downflat_overlay_shadow_checkpoints_last['delta_vs_gate_pp'], 2) if pair_downflat_overlay_shadow_checkpoints_last is not None else 'nan'}pp</code>，最强 checkpoint 约出现在 <code>{int(pair_downflat_overlay_shadow_checkpoints_best['review_days']) if pair_downflat_overlay_shadow_checkpoints_best is not None else 'nan'}</code> 天，累计改善约 <code>{num(pair_downflat_overlay_shadow_checkpoints_best['delta_vs_gate_pp'], 2) if pair_downflat_overlay_shadow_checkpoints_best is not None else 'nan'}pp</code>。</li>
        <li><b>所以怎么读：</b>这层 cumulative review 说明 mixed-tail overlay 不是“前瞻一看就塌”的假 gate；但一旦切回更克制的 non-overlap forward blocks 与 target-pocket conditional honesty，它仍会给出 split verdict。更诚实的写法因此仍是：<b>shadow honesty better than first glance, but not enough to replace default pair candidate</b>。</li>
      </ul>
      {html_table(pair_downflat_overlay_shadow_checkpoints_display, percent_cols={'affected_hour_share','gate_cumulative_net_return','conditioned_cumulative_net_return','gate_max_drawdown','conditioned_max_drawdown'}, float_cols={'delta_vs_gate_pp','drawdown_improve_pp'})}
      <p class="note">一句话版：mixed-tail overlay 的 cumulative checkpoints 如果只看累计路径，当前约是 <code>{int(len(pair_downflat_overlay_shadow_checkpoints_positive)) if not pair_downflat_overlay_shadow_checkpoints_positive.empty else 0}/{int(len(pair_downflat_overlay_shadow_checkpoints_active)) if not pair_downflat_overlay_shadow_checkpoints_active.empty else 0}</code> 仍为正；但因为 non-overlap blocks 与 target-pocket honesty 还是 split，所以它依然只能停在 <b>shadow-only gate</b>，不能改写 breakout 的 <code>one_more_gate</code>。</p>
      <h4>把这 37 个 mixed-tail 受影响小时按真实时间段拆开：这刀到底是 test 证据，还是主要靠 train carry？</h4>
      <ul>
        <li><b>先说结论：</b>更像后者。当前 <code>pair + down+flat mixed-tail overlay</code> 的约 <code>{int(pair_downflat_overlay_holdout_split_map.get('train', {}).get('hours', 0) + pair_downflat_overlay_holdout_split_map.get('test', {}).get('hours', 0))}</code> 个受影响小时，按真实时间顺序只会塌缩成约 <code>{pair_downflat_overlay_episode_count}</code> 段连续 episode；其中前两段都还是 <code>train × down + flat</code>，真正的 pure <code>test</code> 只有最后一段。</li>
        <li><b>最大的 episode：</b>约 <code>{pair_downflat_overlay_episode_best['start_time'].strftime('%Y-%m-%d %H:%M') if pair_downflat_overlay_episode_best is not None else 'nan'}</code> 到 <code>{pair_downflat_overlay_episode_best['end_time'].strftime('%Y-%m-%d %H:%M') if pair_downflat_overlay_episode_best is not None else 'nan'}</code>，持续约 <code>{int(pair_downflat_overlay_episode_best['hours']) if pair_downflat_overlay_episode_best is not None else 'nan'}</code> 小时，条件累计改善约 <code>{num(pair_downflat_overlay_episode_best['delta_pp'], 2) if pair_downflat_overlay_episode_best is not None else 'nan'}pp</code>；但这段本身其实还是 <code>{pair_downflat_overlay_episode_best['split_mix'] if pair_downflat_overlay_episode_best is not None else 'nan'} × {pair_downflat_overlay_episode_best['regime_mix'] if pair_downflat_overlay_episode_best is not None else 'nan'}</code>，并不是新鲜的 forward-only test 口袋。</li>
        <li><b>对 admission 最关键的 test 读法：</b>真正 pure <code>test × down + flat</code> 的 mixed-tail episode 只有约 <code>{int(pair_downflat_overlay_episode_test['hours']) if pair_downflat_overlay_episode_test is not None else 'nan'}</code> 小时（约 <code>{pair_downflat_overlay_episode_test['start_time'].strftime('%Y-%m-%d %H:%M') if pair_downflat_overlay_episode_test is not None else 'nan'}</code> 到 <code>{pair_downflat_overlay_episode_test['end_time'].strftime('%Y-%m-%d %H:%M') if pair_downflat_overlay_episode_test is not None else 'nan'}</code>），条件累计改善约 <code>{num(pair_downflat_overlay_episode_test['delta_pp'], 2) if pair_downflat_overlay_episode_test is not None else 'nan'}pp</code>。这说明 test 方向并没有死，但它依然只是单段小口袋，而不是多段重复出现的厚证据。</li>
        <li><b>更硬一点的来源拆解：</b>把这三段 episode 的条件累计改善加总后，当前 mixed-tail overlay 的总 conditional delta 约 <code>{num(pair_downflat_overlay_episode_total_delta_pp, 2)}pp</code>；其中 <code>train</code> 两段合计约 <code>{num(pair_downflat_overlay_episode_train_delta_pp, 2)}pp</code>（约占 <code>{pct(pair_downflat_overlay_episode_train_delta_share)}</code>），pure <code>test</code> 那一段约 <code>{num(pair_downflat_overlay_episode_test_delta_pp, 2)}pp</code>（约占 <code>{pct(pair_downflat_overlay_episode_test_delta_share)}</code>）。所以它现在更像“train carry + 单段 test mixed-tail pocket 仍为正”，还不能诚实地写成“已有多段 forward test honesty 的 conditional gate”。</li>
      </ul>
      {html_table(pair_downflat_overlay_episode_summary_display, percent_cols={'hour_share_within_target','conditional_cumulative_before','conditional_cumulative_after','mean_hourly_return_before','mean_hourly_return_after'}, float_cols={'delta_pp'})}
      <p class="note">一句话版：mixed-tail overlay 当前的约 <code>{num(pair_downflat_overlay_episode_total_delta_pp, 2)}pp</code> 条件改善里，大约 <code>{pct(pair_downflat_overlay_episode_train_delta_share)}</code> 仍来自两段 <code>train × down+flat</code>，真正 pure <code>test</code> mixed-tail 只贡献约 <code>{num(pair_downflat_overlay_episode_test_delta_pp, 2)}pp</code>。这让它更像“有方向但仍偏训练段 carry 的 shadow-only gate”，而不是已经能晋级的 admission patch。</p>
    </section>
    <section>
      <h2>如果把当前 breakout conditional policy 压成一张 admission queue，会得出什么排位？</h2>
      <ul>
        <li><b>先说结论：</b>今天最值得保留的还是 <code>gate-only -> default pair halfsize</code> 这条主链；<code>down+flat mixed-tail overlay</code> 只能排在它后面，作为 <b>shadow-only</b> 的下一道 gate；而 <code>blunt pure-down overlay</code> 则更像已经做过的反向 sanity check，不是待晋级候选。</li>
        <li><b>为什么这张 queue 有用：</b>它把“要不要继续往 strategy / paper admission 推”翻成了几条具体 policy 的对照，而不是继续在抽象 blocker 上打转。现在可以更明确地说：默认主候选已经够资格继续占着 breakout 的默认位，但 mixed-tail 这刀还只配 shadow 观察；pure-down 机械补丁则已经可以从主候选队列里移开。</li>
        <li><b>更硬一点的 deployment 读法：</b>如果 Jerry 现在只想知道“breakout 线还能不能继续往前推”，答案是 <b>能，但只能沿 default pair candidate 继续推</b>；mixed-tail overlay 只值得保留成 one-more-gate 的附加观察项，而不是把 admission verdict 从 <code>one_more_gate</code> 改写成 <code>shadow paper now</code>。</li>
      </ul>
      {html_table(policy_admission_queue_display, percent_cols={'overall累计','最大回撤','down-tail覆盖率'}, float_cols={'相对对照delta(pp)','strict tail delta(pp)'})}
      <p class="note">读这张表的方法很简单：<b>overall path</b> 看有没有把主路径继续抬起来；<b>strict tail</b> 看它有没有在更硬的尾段里给出诚实增量；<b>down-tail coverage</b> 看 hard gap 到底有没有真的被触碰；<b>forward 5d/10d</b> 则看这刀是不是一进更前瞻口径就散架。当前结果对应的最诚实排位就是：<b>default pair halfsize = keep；mixed-tail overlay = shadow-only；blunt pure-down = reject。</b></p>
    </section>
    <section>
      <h2>如果只看 deployment blocker：这条 breakout 线的 <code>one_more_gate</code> 到底卡在哪？</h2>
      <ul>
        <li><b>这节的目标：</b>不再继续堆近义解释，而是把已经做过的 evidence 压成一张 blocker checklist，让 Jerry 一眼看到“哪些已经过 first-pass、哪些还不能放行”。</li>
        <li><b>最重要的读法：</b>default pair candidate 已经足够说明 breakout 不是纯幻觉；但真正把它卡在 <code>one_more_gate</code> 的，已经收敛成 <b>pure-test tail 仍薄 + down-tail coverage 仍是 0/100</b> 这两件事。</li>
        <li><b>mixed-tail 与 blunt pure-down 怎么看：</b><code>mixed-tail overlay</code> 继续保留成 <b>shadow-only</b> 附加 gate；<code>blunt pure-down</code> 则可正式视为做过的 reject sanity check，不再误读成现成补丁。</li>
      </ul>
      {html_table(admission_gate_checklist_display)}
      <p class="note">一句话版：现在最需要补的已不再是“有没有统一资金曲线”，而是更具体的 admission blocker——<b>default pair 的 pure-test tail 还太薄，且 pure down coverage 仍是 0/100</b>。所以 breakout 还能继续推，但只能沿 default pair 主候选继续推。</p>
    </section>
    <section>
      <h2>如果不想再反复解释：这条 breakout 线的 <code>one_more_gate</code> 具体怎样才算过关？</h2>
      <ul>
        <li><b>这节只做一件事：</b>把当前 evidence 直接翻成执行型 protocol：默认主线怎么继续、mixed-tail 什么时候仍只能 shadow-only、以及 blunt pure-down 为什么继续只该留在 reject。</li>
        <li><b>最重要的读法：</b>现在并不是“breakout 不能继续”，而是 <b>只能沿 default pair 主候选继续</b>；除非后续 forward / shadow 证据终于真正碰到 pure <code>down</code>，否则这条线就不该从 <code>one_more_gate</code> 升成 <code>shadow paper now</code>。</li>
        <li><b>为什么这张表有用：</b>它直接回答 Jerry 接下来该怎么看——哪些结果算有效推进，哪些结果只是在继续补 wording，哪些分支已经可以明确当 reject sanity check 处理。</li>
      </ul>
      {html_table(gate_clearance_protocol_display)}
      <p class="note">一句话版：继续是可以继续的，但过关条件现在已经很明确——<b>default pair 必须终于交出 pure-test / down-tail 的前瞻证据</b>；mixed-tail 在 non-overlap / target-pocket honesty 没摆脱 split verdict 前，都继续只配 <b>shadow-only</b>。</p>
    </section>
    <section>
      <h2>admission verdict：这条 breakout 线今天够不够进 shadow paper？</h2>
      <ul>
        <li><b>先给结论：</b>还不够。当前更硬一点的 verdict 应该明确写成 <b><code>one_more_gate</code></b>，而不是 <code>shadow paper now</code>。</li>
        <li><b>为什么不是直接否掉：</b>这条线已经不再只是 per-asset 幻觉。现在至少已经补齐了 <code>20bps</code> 下的统一资金曲线、<code>avoid_fluctuating</code> gate、默认 <code>ETH+SOL pair-conditioned halfsize</code> sizing 候选，以及一刀更严格的 rolling honesty；对应 hourly path 已从 raw 的约 <code>{pct(confirm_compare_display.loc[confirm_compare_display['strategy'].eq('raw_v0'), 'hourly_path_cost20_cumulative_return'].iloc[0]) if not confirm_compare_display.empty else 'nan'}</code>，推进到 gate-only 的约 <code>{pct(pair_sizing_map.get('avoid_fluctuating', {}).get('cumulative_net_return'))}</code>，再到默认 sizing candidate 的约 <code>{pct(sizing_candidate_compare.loc[sizing_candidate_compare['candidate'].eq('avoid_fluctuating_eth_sol_pair_halfsize'), 'overall_cumulative_net_return'].iloc[0]) if sizing_candidate_compare is not None and not sizing_candidate_compare.empty and (sizing_candidate_compare['candidate'] == 'avoid_fluctuating_eth_sol_pair_halfsize').any() else 'nan'}</code>；max drawdown 也约从 <code>{pct(confirm_compare_display.loc[confirm_compare_display['strategy'].eq('raw_v0'), 'hourly_path_max_drawdown'].iloc[0]) if not confirm_compare_display.empty else 'nan'}</code> 收窄到约 <code>{pct(sizing_candidate_compare.loc[sizing_candidate_compare['candidate'].eq('avoid_fluctuating_eth_sol_pair_halfsize'), 'max_drawdown'].iloc[0]) if sizing_candidate_compare is not None and not sizing_candidate_compare.empty and (sizing_candidate_compare['candidate'] == 'avoid_fluctuating_eth_sol_pair_halfsize').any() else 'nan'}</code>。所以它已经比“只是个策略想法”更接近 shadow paper。</li>
        <li><b>但为什么还不能放行：</b>当前最缺的已经不是组合层资金曲线，而是 <b>默认 sizing candidate 的 pure-test / admission honesty</b>。它在更严格口径下的 late-segment 证据其实已经比前几轮更硬：<code>5-day</code> non-overlap blocks 是 <code>3/4</code> 改善、<code>1/4</code> 小回吐，而把窗口放长到 <code>10-day</code> 后，当前有动作的 <code>{int(len(pair_forward_blocks_10d_positive)) if not pair_forward_blocks_10d_positive.empty else 0}/{int(len(pair_forward_blocks_10d_active)) if not pair_forward_blocks_10d_active.empty else 0}</code> 个 block 都仍优于 gate-only；更严格地只看从首个 pure <code>test</code> 触发到样本末尾的 tail，这段也仍约改善 <code>{num(pair_pure_test_tail_row['delta_vs_gate_pp'], 2) if pair_pure_test_tail_row is not None else 'nan'}pp</code>。但问题是：pure <code>test</code> 真正被它修到的目标 pocket 仍只有约 <code>{str(int(sizing_candidate_compare.loc[sizing_candidate_compare['candidate'].eq('avoid_fluctuating_eth_sol_pair_halfsize'), 'pure_test_hours'].iloc[0])) if sizing_candidate_compare is not None and not sizing_candidate_compare.empty and (sizing_candidate_compare['candidate'] == 'avoid_fluctuating_eth_sol_pair_halfsize').any() else 'nan'}</code> 个小时，对应条件累计改善也只有约 <code>{num(sizing_candidate_compare.loc[sizing_candidate_compare['candidate'].eq('avoid_fluctuating_eth_sol_pair_halfsize'), 'pure_test_delta_pp'].iloc[0], 2) if sizing_candidate_compare is not None and not sizing_candidate_compare.empty and (sizing_candidate_compare['candidate'] == 'avoid_fluctuating_eth_sol_pair_halfsize').any() else 'nan'}pp</code>，strict tail 本身也只有约 <code>{int(pair_pure_test_tail_row['active_hours']) if pair_pure_test_tail_row is not None else 'nan'}</code> 个小时。更关键的是，若把 hard gap 粗暴地改成“所有 pure <code>down</code> active hours 一律再砍半”，overall path 反而会从约 <code>{pct(sizing_candidate_compare.loc[sizing_candidate_compare['candidate'].eq('avoid_fluctuating_eth_sol_pair_halfsize'), 'overall_cumulative_net_return'].iloc[0]) if sizing_candidate_compare is not None and not sizing_candidate_compare.empty and (sizing_candidate_compare['candidate'] == 'avoid_fluctuating_eth_sol_pair_halfsize').any() else 'nan'}</code> 回落到约 <code>{pct(pair_down_overlay_row['cumulative_net_return']) if pair_down_overlay_row is not None else 'nan'}</code>；这说明 blocker 虽然长得像 down-tail，却不能靠 blunt down-only overlay 机械解除。</li>
        <li><b>主缺口排位：</b><b>#1 = pure-test / down-tail honesty</b>；<b>#2 = 更长窗口下继续确认 transferability</b>（当前 <code>10-day</code> non-overlap 已是 <code>{int(len(pair_forward_blocks_10d_positive)) if not pair_forward_blocks_10d_positive.empty else 0}/{int(len(pair_forward_blocks_10d_active)) if not pair_forward_blocks_10d_active.empty else 0}</code> 改善，说明一般性 late-segment 焦虑在下降）；<b>#3 才不是 portfolio honesty</b>，因为统一 hourly path / 1-slot / equal-weight 这层现在已经有 first-pass 证据，不再是最主要的未知数。</li>
        <li><b>因此今天最诚实的 deployment scope：</b>只适合继续当 <b>breakout-short 的 shadow-admission candidate</b> 来观察，不适合现在就写成可直接开跑的默认 shadow paper policy。当前 pocket 也应明确写死在已有证据范围：<code>{', '.join(result.by_asset['symbol'].astype(str).tolist()) if not result.by_asset.empty else '当前样本资产'}</code>、<code>60m</code>、<code>support_breakout_raw @ h24</code>、先过 <code>avoid_fluctuating</code>，再在残余 <code>ETH+SOL</code> 两仓小时做 <code>0.5x</code>。</li>
      </ul>
      <table>
        <thead>
          <tr><th>admission 问题</th><th>当前答案</th><th>这意味着什么</th></tr>
        </thead>
        <tbody>
          <tr>
            <td>市场 / 频率 / policy scope 是否明确？</td>
            <td>是。当前只对应 <code>{', '.join(result.by_asset['symbol'].astype(str).tolist()) if not result.by_asset.empty else '当前样本资产'}</code>、<code>60m</code>、<code>support_breakout_raw @ h24</code>、<code>avoid_fluctuating + ETH+SOL pair halfsize</code>。</td>
            <td>这是一个很窄的 shadow-admission candidate，不是通用 breakout short 模板。</td>
          </tr>
          <tr>
            <td>组合 / 资金曲线 honesty 是否还是主 blocker？</td>
            <td>不是主 blocker。已有 raw / gate-only / pair-conditioned 的 <code>20bps hourly path</code>，以及 <code>1-slot</code> / <code>equal-weight</code> 对照。</td>
            <td>可以停止再问“是不是只靠 per-asset 幻觉”，把主精力转向 sizing 迁移性。</td>
          </tr>
          <tr>
            <td>默认 sizing candidate 是否已足够稳定？</td>
            <td>还不够。active rolling windows 里是 <code>{int(len(pair_walkforward_active)) if not pair_walkforward_active.empty else 0}</code>/<code>{int(len(pair_walkforward_windows_display)) if pair_walkforward_windows_display is not None else 0}</code> 个窗口真正触发且都改善；更诚实的 non-overlap 口径下，<code>5-day</code> blocks 是 <code>{int(len(pair_forward_blocks_positive)) if not pair_forward_blocks_positive.empty else 0}/{int(len(pair_forward_blocks_active)) if not pair_forward_blocks_active.empty else 0}</code> 改善，而 <code>10-day</code> blocks 当前有动作的 <code>{int(len(pair_forward_blocks_10d_positive)) if not pair_forward_blocks_10d_positive.empty else 0}/{int(len(pair_forward_blocks_10d_active)) if not pair_forward_blocks_10d_active.empty else 0}</code> 仍都为正；进一步只看 strict pure <code>test</code> tail，也仍约改善 <code>{num(pair_pure_test_tail_row['delta_vs_gate_pp'], 2) if pair_pure_test_tail_row is not None else 'nan'}pp</code>。但这段 tail 自己也只有约 <code>{int(pair_pure_test_tail_row['active_hours']) if pair_pure_test_tail_row is not None else 'nan'}</code> 个小时，而且 `down-tail coverage` 当前仍约 <code>{int(pair_down_coverage_row['policy_affected_hours']) if pair_down_coverage_row is not None else 0}/{int(pair_down_coverage_row['gate_active_hours']) if pair_down_coverage_row is not None else 0}</code>（约 <code>{pct(pair_down_coverage_row['policy_coverage_share']) if pair_down_coverage_row is not None else 'nan'}</code>）。</td>
            <td>说明它已经值得保留，但还不够升成“现在就去 shadow paper”的默认规则；一般性 late-segment 焦虑已减弱，剩下更像是 <code>pure-test / down-tail</code> 这类更具体的 blocker。</td>
          </tr>
          <tr>
            <td>最终 verdict</td>
            <td><b><code>one_more_gate</code></b>（closest breakout candidate, but not shadow-paper-ready）</td>
            <td>下一刀默认先盯 <b>pair candidate 上的 mixed down-tail protective gate</b> 是否能在更前瞻的 shadow / walk-forward 里守住；更长 forward windows 仍要继续看，但不必先回到泛化新变体。</td>
          </tr>
        </tbody>
      </table>
      <p class="note">一句话版：当前 breakout 线已经足够进入 <b>shadow-admission queue</b>，但还不够直接放行为默认 shadow paper policy；现在更诚实的说法已不是“它会不会只是后半段 lucky patch”，而是“它在更长窗口与 strict pure-test tail 里都暂时没翻负，但 <code>pure-test / down-tail</code> 证据仍太薄，还没过关”。</p>
    </section>
    <section>
      <h2>如果把 confirm_1 也放进同一套成本 / 执行框架，谁更像该继续保留的原型？</h2>
      <ul>
        <li><b>先说结论：</b>当前 first-pass 下，<code>support_breakout_confirm_1 @ h24</code> 还没有表现出比 <code>raw</code> 更诚实的执行层优势；它更像该保留的紧邻确认变体，而不是能取代 raw 的主原型。</li>
        <li><b>20bps、每资产独立记账：</b><code>raw</code> 累计约 <code>{pct(confirm_compare_display.loc[confirm_compare_display['strategy'].eq('raw_v0'), 'cost20_cumulative_return'].iloc[0]) if not confirm_compare_display.empty else 'nan'}</code>，高于 <code>confirm_1</code> 的约 <code>{pct(confirm_compare_display.loc[confirm_compare_display['strategy'].eq('confirm_1'), 'cost20_cumulative_return'].iloc[0]) if not confirm_compare_display.empty else 'nan'}</code>。</li>
        <li><b>允许并发但入场均分资金：</b><code>raw</code> 的 <code>equal-weight concurrent(entry)</code> 累计约 <code>{pct(confirm_compare_display.loc[confirm_compare_display['strategy'].eq('raw_v0'), 'equal_weight_cost20_cumulative_return'].iloc[0]) if not confirm_compare_display.empty else 'nan'}</code>，仍高于 <code>confirm_1</code> 的约 <code>{pct(confirm_compare_display.loc[confirm_compare_display['strategy'].eq('confirm_1'), 'equal_weight_cost20_cumulative_return'].iloc[0]) if not confirm_compare_display.empty else 'nan'}</code>。</li>
        <li><b>再往前推到更正式的 hourly mark-to-market path：</b><code>raw</code> 的统一资金曲线 <code>20bps</code> 累计约 <code>{pct(confirm_compare_display.loc[confirm_compare_display['strategy'].eq('raw_v0'), 'hourly_path_cost20_cumulative_return'].iloc[0]) if not confirm_compare_display.empty else 'nan'}</code>、max drawdown 约 <code>{pct(confirm_compare_display.loc[confirm_compare_display['strategy'].eq('raw_v0'), 'hourly_path_max_drawdown'].iloc[0]) if not confirm_compare_display.empty else 'nan'}</code>；<code>confirm_1</code> 对应约 <code>{pct(confirm_compare_display.loc[confirm_compare_display['strategy'].eq('confirm_1'), 'hourly_path_cost20_cumulative_return'].iloc[0]) if not confirm_compare_display.empty else 'nan'}</code> / <code>{pct(confirm_compare_display.loc[confirm_compare_display['strategy'].eq('confirm_1'), 'hourly_path_max_drawdown'].iloc[0]) if not confirm_compare_display.empty else 'nan'}</code>，说明一旦把两者都放进更正式一点的统一资金曲线里，`confirm_1` 也没有反超 raw。</li>
        <li><b>最保守的 1-slot global：</b><code>raw</code> 在 <code>20bps</code> 下累计约 <code>{pct(confirm_compare_display.loc[confirm_compare_display['strategy'].eq('raw_v0'), 'slot1_cost20_cumulative_return'].iloc[0]) if not confirm_compare_display.empty else 'nan'}</code>，而 <code>confirm_1</code> 约 <code>{pct(confirm_compare_display.loc[confirm_compare_display['strategy'].eq('confirm_1'), 'slot1_cost20_cumulative_return'].iloc[0]) if not confirm_compare_display.empty else 'nan'}</code>；同时 <code>confirm_1</code> 的 <code>test + 20bps</code> 也更弱（约 <code>{pct(confirm_compare_display.loc[confirm_compare_display['strategy'].eq('confirm_1'), 'test_cost20_cumulative_return'].iloc[0]) if not confirm_compare_display.empty else 'nan'}</code>）。</li>
      </ul>
      {html_table(confirm_compare_display, percent_cols={'gross_cumulative_return','cost20_cumulative_return','test_cost20_cumulative_return','up_cost20_cumulative_return','equal_weight_cost20_cumulative_return','equal_weight_mean_effective_weight','hourly_path_cost20_cumulative_return','hourly_path_max_drawdown','slot1_cost20_cumulative_return','slot1_trade_keep_ratio'})}
      <p class="note">一句话版：<code>confirm_1</code> 现在仍值得作为 <b>co-primary confirmation variant</b> 保留，但在同一套成本 / capital-allocation first-pass 下，它还没有证明自己比 <code>raw</code> 更像该继续押注的 breakout-short 主原型。</p>
    </section>
    <section>
      <h2>plain-language：raw / confirm_1 / feature-watch 到底怎么区分？</h2>
      <ul>
        <li><b><code>support_breakout_raw @ h24</code>：</b>当前最应该读成 <b>可交易原型 / 条件性 alpha</b>。原因不是它已经成熟，而是它已经能被压成一个最小、可解释、可继续补 honesty 的 v0 页面。</li>
        <li><b><code>support_breakout_confirm_1 @ h24</code>：</b>当前更像 <b>co-primary confirmation variant</b>，不是 feature/watchlist。它代表“同方向、但更保守一点”的 breakout-short 候选，后续若继续做执行/成本/环境约束验证，应该和 raw 一起被当成主保留对象，而不是被降成纯观察项。</li>
        <li><b>什么才叫 feature/watchlist？</b> 像 <code>support_rebound_confirm_1</code> 那样：保留一些信息价值，但目前不该直接往主 alpha / 原型页继续压。也就是说，当前 <code>raw / confirm_1</code> 不属于这一类。</li>
        <li><b>如果今天只能保留一个 strategy-facing 原型页：</b>先保留 <code>raw</code>，因为它更直接、入场不延迟，也已经能给出最小策略化读法。</li>
        <li><b>如果要保留一个紧邻确认变体做 next-step honesty check：</b>保留 <code>confirm_1</code>，但先不要把它扩成第二条大而全独立策略线。</li>
      </ul>
      <p class="note">一句话版：<code>raw</code> = 现在就值得当 v0 原型继续验证；<code>confirm_1</code> = 仍是主保留候选，但更像保守确认变体；<code>feature/watchlist</code> = 当前不该套在这两个对象上的标签。</p>
    </section>
    <section>
      <h2>总体指标</h2>
      {html_table(result.summary, percent_cols={'mean_return','median_return','win_ratio','cumulative_return','max_drawdown'}, float_cols={'avg_entry_delay_bars'})}
    </section>
    <section>
      <h2>按资产拆分</h2>
      {html_table(result.by_asset, percent_cols={'mean_return','median_return','win_ratio','cumulative_return','max_drawdown'}, float_cols={'avg_entry_delay_bars'})}
    </section>
    <section>
      <h2>按时间切分拆分</h2>
      <p class="muted">切分方式是按事件时间顺序做 60/20/20 的 train / validate / test，仅用于看方向是否在后段崩掉，不代表正式 walk-forward。</p>
      {html_table(result.by_split, percent_cols={'mean_return','median_return','win_ratio','cumulative_return','max_drawdown'}, float_cols={'avg_entry_delay_bars'})}
    </section>
    <section>
      <h2>按简单行情标签拆分</h2>
      <p class="muted">这里的行情标签不是复杂 regime 模型，只是按入场前 24 根 60m bar 的价格变化粗分为 <code>up / flat / down</code>，目的是快速回答“这条策略在哪种环境更顺手”。</p>
      <p class="note">{regime_blurb(result.by_regime)}</p>
      {html_table(result.by_regime, percent_cols={'mean_return','median_return','win_ratio','cumulative_return','max_drawdown'}, float_cols={'avg_entry_delay_bars'})}
    </section>
    """
    report_path.write_text(render_page("support_breakout_raw @ h24 v0 回测", body), encoding="utf-8")


def build_ab_report(v0: StrategyResult, fib: StrategyResult, report_path: Path, equity_img: str, asset_img: str, compare_df: pd.DataFrame) -> None:
    v0s = v0.summary.iloc[0]
    fibs = fib.summary.iloc[0]
    body = f"""
    <section class="hero">
      <p class="muted">Fast small-loop deliverable / A/B honesty check</p>
      <h1>Breakout v0 vs Breakout + Fibonacci Retest-Hold</h1>
      <p>这页不是为了证明 fib 一定有效，而是把一个<strong>最小、能解释清楚</strong>的 fib 叠加逻辑放到同样本里，直接和 breakout v0 做 A/B。</p>
      <div class="grid">
        <div class="card"><div class="k">A: v0 平均单笔</div><div class="v">{pct(v0s['mean_return'])}</div></div>
        <div class="card"><div class="k">A: v0 累计收益</div><div class="v">{pct(v0s['cumulative_return'])}</div></div>
        <div class="card"><div class="k">B: fib 平均单笔</div><div class="v">{pct(fibs['mean_return'])}</div></div>
        <div class="card"><div class="k">B: fib 累计收益</div><div class="v">{pct(fibs['cumulative_return'])}</div></div>
        <div class="card"><div class="k">B: 成交保留率</div><div class="v">{pct(fibs['trades'] / v0s['trades'])}</div></div>
      </div>
      <p class="note">这里的 Fibonacci 版属于<strong>假设型整合</strong>：不是现成主线 artifacts 的官方定义，而是为了做诚实对照，按固定规则把 breakout 事件延迟成“反抽到 fib 区后再做空”的最小变体。</p>
    </section>
    <section>
      <h2>Fib 版规则假设</h2>
      <ul>
        <li>仍然只从 <code>support_breakout_raw</code> 事件出发，不新增别的候选池。</li>
        <li>对每个 breakout，在事件前固定回看 <code>{SWING_LOOKBACK}</code> 根 60m bar，找到最近一段下跌 swing：先取窗口最高点，再取该高点之后到事件时刻的最低点。</li>
        <li>用这个 downswing 计算短空 retest 区：<code>38.2% ~ 50%</code> 反抽区。</li>
        <li>breakout 后最多等待 <code>{MAX_RETEST_WAIT}</code> 根 bar；只有价格反抽进入 fib 区且当根收盘重新压回 <code>fib38</code> 下方，下一根开盘才做空。</li>
        <li>随后仍固定持有 <code>{HOLD_BARS}</code> 根 bar，同资产不重叠。</li>
      </ul>
    </section>
    <section>
      <h2>A/B 结论</h2>
      <ul>
        <li class="good">A 组 breakout v0 在这批样本上更直接、更强：平均单笔 {pct(v0s['mean_return'])}，累计 {pct(v0s['cumulative_return'])}。</li>
        <li class="bad">B 组 fib 版虽然把样本压缩成 {int(fibs['trades'])} 笔，并把平均入场延迟拉到 {num(fibs['avg_entry_delay_bars'])} 根 bar，但没有跑赢 A 组；它更像“把一部分顺势直接跌下去的好机会等没了”。</li>
        <li class="muted">因此当前最诚实的读法不是“fib 增强 breakout”，而是“在这批小样本里，简单 breakout 比 breakout+fib retest 更值得先留作 v0 主线”。</li>
      </ul>
    </section>
    <section>
      <h2>Fibonacci 这条线的最终结论</h2>
      <ul>
        <li><b>它原本想解决什么：</b>给 breakout short 增加一个“别追在最差位置、等反抽确认后再做空”的过滤层。</li>
        <li><b>它确实改善了什么：</b>更像改善了“少追太早、少碰一部分噪声反抽”的机制表达；在这页里最直接的体现是把样本压缩成更少、更晚的交易。</li>
        <li><b>它没改善什么：</b>没有改善主线最关心的收益结果——A 组 v0 平均单笔约 <code>1.44%</code>、累计约 <code>92.45%</code>，而 fib 版只有约 <code>0.71%</code>、累计约 <code>20.00%</code>，同时平均入场还延迟到约 <code>12.5</code> 根 bar。</li>
        <li><b>为什么不再当主 alpha：</b><code>Fibonacci retest_hold</code> 这轮没有证明自己是更好的通用增强器；它更像把不少顺势直接下跌的好机会等没了，所以不进入主线 alpha。</li>
        <li><b>正式收口：</b>后续把它降级成 <b>optional filter candidate / archived idea</b>，不再继续单独开主研发回合。</li>
        <li><b>主线取舍：</b>这次收口后，breakout short 保留，Fibonacci 过滤层归档。</li>
      </ul>
      <p class="note">如果以后再回来看这条线，唯一合理的问题应该是：“在更明确的下跌 regime 里，它能不能当一个小过滤器？”——而不是把它重新包装成主 alpha。</p>
    </section>
    <section>
      <h2>它在当前项目里到底算什么？</h2>
      <ul>
        <li><b>当前正式标签：</b><code>optional filter candidate</code>。</li>
        <li><b>不是：</b>主 alpha，也不是当前还要单独继续投入主研发轮次的 active branch。</li>
        <li><b>比 teaching example 更强一点：</b>因为它确实教会了我们一件有用的事——“确认层可以改善机制诚实度，但不一定能救活 alpha”。</li>
        <li><b>比 future revisit candidate 更近一点：</b>因为它不是彻底作废；若以后明确只研究 <code>downtrend</code> / 更弱环境下的 breakout short filter，它仍有小概率被重新拿出来做窄验证。</li>
        <li><b>一句话：</b>当前最诚实的归类就是 <b>optional filter candidate with archived status</b>。</li>
      </ul>
    </section>
    <section>
      <h2>A/B 汇总表</h2>
      {html_table(compare_df, percent_cols={'mean_return','median_return','win_ratio','cumulative_return','max_drawdown','trade_keep_ratio_vs_v0'}, float_cols={'avg_entry_delay_bars'})}
    </section>
    <section>
      <h2>按 split 看 honesty</h2>
      {html_table(pd.concat([v0.by_split, fib.by_split], ignore_index=True), percent_cols={'mean_return','median_return','win_ratio','cumulative_return','max_drawdown'}, float_cols={'avg_entry_delay_bars'})}
    </section>
    <section>
      <h2>不同行情下表现如何</h2>
      <p class="muted">这里也用同样的简单标签：按入场前 24 根 60m bar 的价格变化，把样本粗分成 <code>up / flat / down</code>。这不是最终 regime 模型，只是帮我们快速判断 fib 过滤器是不是在某一种市场状态下更有价值。</p>
      {html_table(pd.concat([v0.by_regime, fib.by_regime], ignore_index=True), percent_cols={'mean_return','median_return','win_ratio','cumulative_return','max_drawdown'}, float_cols={'avg_entry_delay_bars'})}
      <p class="note">这张表最值得记住的点有两个：第一，<b>v0 在 flat 环境最强（平均单笔 2.41%）</b>，说明它更像震荡偏弱 / 刚转弱环境的短空 alpha；第二，fib 虽然在 <code>down</code> 行情里看起来更亮眼，但样本只有 4 笔，不足以支撑继续主线研发。</p>
    </section>
    <section>
      <h2>图：交易序列累计净值</h2>
      <img src="{escape(equity_img)}" alt="A/B equity curve" />
    </section>
    <section>
      <h2>图：各资产平均单笔收益</h2>
      <img src="{escape(asset_img)}" alt="A/B asset mean return" />
    </section>
    """
    report_path.write_text(render_page("Breakout v0 vs Fib A/B", body), encoding="utf-8")


def main() -> None:
    ensure_dir(V0_ART_DIR)
    ensure_dir(V0_SITE_DIR)
    ensure_dir(AB_ART_DIR)
    ensure_dir(AB_SITE_DIR)

    events, bars_by_symbol = load_inputs()
    raw_events = with_splits(events[events["event_type"].eq("support_breakout_raw")].copy(), time_col="action_timestamp")
    raw_events = attach_confirm_trend_regime(raw_events, bars_by_symbol)
    gated_events = raw_events[raw_events["trend_policy"].eq("avoid_fluctuating")].copy()

    v0_trades = build_v0_trades(raw_events, bars_by_symbol)
    gated_trades = build_simple_breakout_trades(
        gated_events,
        bars_by_symbol,
        event_type="support_breakout_raw",
        strategy_name="v0_breakout_avoid_fluctuating",
        setup_label="break_on_action_open_avoid_fluctuating",
    )
    confirm1_trades = build_confirm1_trades(events, bars_by_symbol)
    fib_trades = build_fib_trades(events, bars_by_symbol)

    v0_summary, v0_by_asset, v0_by_split, v0_by_regime = summarize_trades(v0_trades, name="v0_breakout")
    gated_summary, gated_by_asset, gated_by_split, gated_by_regime = summarize_trades(gated_trades, name="v0_breakout_avoid_fluctuating")
    confirm1_summary, confirm1_by_asset, confirm1_by_split, confirm1_by_regime = summarize_trades(confirm1_trades, name="breakout_confirm_1")
    fib_summary, fib_by_asset, fib_by_split, fib_by_regime = summarize_trades(fib_trades, name="breakout_plus_fib_retest_hold")

    v0_result = StrategyResult("v0_breakout", v0_trades, v0_summary, v0_by_asset, v0_by_split, v0_by_regime)
    fib_result = StrategyResult("breakout_plus_fib_retest_hold", fib_trades, fib_summary, fib_by_asset, fib_by_split, fib_by_regime)
    confirm1_hourly_portfolio_path_20 = build_equal_weight_hourly_portfolio_path(confirm1_trades, bars_by_symbol, cost_bps=20)
    confirm1_hourly_portfolio_summary_20 = summarize_hourly_portfolio_path(
        confirm1_hourly_portfolio_path_20,
        mode="equal_weight_concurrent_hourly_confirm1",
        cost_bps=20,
    )

    confirm_compare_df = pd.concat(
        [
            breakout_honesty_snapshot(v0_trades, label="raw_v0", bars_by_symbol=bars_by_symbol),
            breakout_honesty_snapshot(confirm1_trades, label="confirm_1", bars_by_symbol=bars_by_symbol),
        ],
        ignore_index=True,
    )
    gate_compare_df = pd.concat(
        [
            breakout_gate_hourly_snapshot(v0_trades, bars_by_symbol, label="raw_v0"),
            breakout_gate_hourly_snapshot(gated_trades, bars_by_symbol, label="avoid_fluctuating"),
        ],
        ignore_index=True,
    )
    if not gate_compare_df.empty and int(v0_summary.iloc[0]["trades"]) > 0:
        gate_compare_df["trade_retention_vs_raw"] = gate_compare_df["trades"] / float(v0_summary.iloc[0]["trades"])

    hourly_portfolio_path_20 = build_equal_weight_hourly_portfolio_path(v0_trades, bars_by_symbol, cost_bps=20)
    hourly_portfolio_summary_20 = summarize_hourly_portfolio_path(
        hourly_portfolio_path_20,
        mode="equal_weight_concurrent_hourly",
        cost_bps=20,
    )
    hourly_split_summary_20 = summarize_hourly_portfolio_groups(
        v0_trades,
        bars_by_symbol,
        group_col="split",
        cost_bps=20,
    )
    hourly_regime_summary_20 = summarize_hourly_portfolio_groups(
        v0_trades,
        bars_by_symbol,
        group_col="regime",
        cost_bps=20,
    )
    gated_hourly_portfolio_path_20 = build_equal_weight_hourly_portfolio_path(gated_trades, bars_by_symbol, cost_bps=20)
    gated_hourly_portfolio_summary_20 = summarize_hourly_portfolio_path(
        gated_hourly_portfolio_path_20,
        mode="equal_weight_concurrent_hourly_avoid_fluctuating",
        cost_bps=20,
    )
    gated_hourly_split_summary_20 = summarize_hourly_portfolio_groups(
        gated_trades,
        bars_by_symbol,
        group_col="split",
        cost_bps=20,
    )
    gated_hourly_regime_summary_20 = summarize_hourly_portfolio_groups(
        gated_trades,
        bars_by_symbol,
        group_col="regime",
        cost_bps=20,
    )
    hourly_active_bucket_compare_20 = pd.concat(
        [
            summarize_hourly_active_position_buckets(hourly_portfolio_path_20, label="raw_v0"),
            summarize_hourly_active_position_buckets(confirm1_hourly_portfolio_path_20, label="confirm_1"),
            summarize_hourly_active_position_buckets(gated_hourly_portfolio_path_20, label="avoid_fluctuating"),
        ],
        ignore_index=True,
    )
    raw_two_position_detail_20 = build_hourly_active_position_mix_detail(
        v0_trades,
        hourly_portfolio_path_20,
        label="raw_v0",
        target_active_positions=2,
    )
    confirm1_two_position_detail_20 = build_hourly_active_position_mix_detail(
        confirm1_trades,
        confirm1_hourly_portfolio_path_20,
        label="confirm_1",
        target_active_positions=2,
    )
    gated_two_position_detail_20 = build_hourly_active_position_mix_detail(
        gated_trades,
        gated_hourly_portfolio_path_20,
        label="avoid_fluctuating",
        target_active_positions=2,
    )
    hourly_two_position_symbol_mix_compare_20 = pd.concat(
        [
            summarize_hourly_active_position_symbol_mix(raw_two_position_detail_20),
            summarize_hourly_active_position_symbol_mix(confirm1_two_position_detail_20),
            summarize_hourly_active_position_symbol_mix(gated_two_position_detail_20),
        ],
        ignore_index=True,
    )
    hourly_two_position_pair_context_compare_20 = pd.concat(
        [
            summarize_hourly_active_position_pair_context(raw_two_position_detail_20),
            summarize_hourly_active_position_pair_context(gated_two_position_detail_20),
        ],
        ignore_index=True,
    )
    gated_eth_sol_pair_halfsize_path_20, gated_eth_sol_pair_halfsize_affected_20 = apply_hourly_pair_sizing_policy(
        gated_hourly_portfolio_path_20,
        gated_two_position_detail_20,
        target_symbol_pair="ETH-USD + SOL-USD",
        size_multiplier=0.5,
    )
    gated_eth_sol_pair_halfsize_summary_20 = summarize_hourly_portfolio_path(
        gated_eth_sol_pair_halfsize_path_20,
        mode="avoid_fluctuating_eth_sol_pair_halfsize",
        cost_bps=20,
    )
    pair_sizing_compare_pair_20 = summarize_hourly_pair_sizing_compare(
        hourly_portfolio_path_20,
        gated_hourly_portfolio_path_20,
        gated_eth_sol_pair_halfsize_path_20,
        gated_eth_sol_pair_halfsize_affected_20,
        conditioned_label="avoid_fluctuating_eth_sol_pair_halfsize",
    )
    pair_sizing_holdout_split_pair_20 = summarize_policy_affected_hours_by_split(gated_eth_sol_pair_halfsize_affected_20)
    pair_sizing_holdout_regime_pair_20 = summarize_policy_affected_hours_by_regime(gated_eth_sol_pair_halfsize_affected_20)
    pair_sizing_holdout_split_regime_pair_20 = summarize_policy_affected_hours_by_split_regime(gated_eth_sol_pair_halfsize_affected_20)
    pair_default_episode_summary_20 = summarize_policy_affected_hour_episodes(gated_eth_sol_pair_halfsize_affected_20)
    pair_regime_coverage_audit_20 = summarize_pair_regime_coverage_audit(gated_hourly_regime_summary_20, pair_sizing_holdout_regime_pair_20)
    pair_walkforward_windows_pair_20 = summarize_hourly_pair_walkforward_windows(
        gated_hourly_portfolio_path_20,
        gated_eth_sol_pair_halfsize_path_20,
        gated_eth_sol_pair_halfsize_affected_20,
        window_days=10,
        step_days=5,
        min_active_hours=20,
    )
    pair_forward_blocks_pair_20 = summarize_hourly_pair_forward_blocks(
        gated_hourly_portfolio_path_20,
        gated_eth_sol_pair_halfsize_path_20,
        gated_eth_sol_pair_halfsize_affected_20,
        block_days=5,
        min_active_hours=12,
    )
    pair_forward_blocks_pair_10d_20 = summarize_hourly_pair_forward_blocks(
        gated_hourly_portfolio_path_20,
        gated_eth_sol_pair_halfsize_path_20,
        gated_eth_sol_pair_halfsize_affected_20,
        block_days=10,
        min_active_hours=12,
    )
    pair_shadow_checkpoints_20 = summarize_hourly_pair_shadow_checkpoints(
        gated_hourly_portfolio_path_20,
        gated_eth_sol_pair_halfsize_path_20,
        gated_eth_sol_pair_halfsize_affected_20,
        review_days=[5, 10, 15, 20],
        min_active_hours=12,
    )
    pair_pure_test_tail_summary_20 = summarize_hourly_pair_tail_snapshot(
        gated_hourly_portfolio_path_20,
        gated_eth_sol_pair_halfsize_path_20,
        gated_eth_sol_pair_halfsize_affected_20,
        split_value="test",
    )
    pair_pure_test_tail_checkpoints_20 = summarize_hourly_pair_shadow_checkpoints_hours(
        gated_hourly_portfolio_path_20,
        gated_eth_sol_pair_halfsize_path_20,
        gated_eth_sol_pair_halfsize_affected_20.loc[
            gated_eth_sol_pair_halfsize_affected_20["split_mix"].astype(str).eq("test")
        ].copy(),
        review_hours=[60, 72],
        min_active_hours=4,
    )
    pair_pure_test_tail_blocks_20 = summarize_hourly_pair_forward_blocks_hours(
        gated_hourly_portfolio_path_20,
        gated_eth_sol_pair_halfsize_path_20,
        gated_eth_sol_pair_halfsize_affected_20.loc[
            gated_eth_sol_pair_halfsize_affected_20["split_mix"].astype(str).eq("test")
        ].copy(),
        block_hours=6,
        min_active_hours=4,
    )
    pair_all_active_context_20 = build_hourly_active_context_detail(
        gated_trades,
        gated_eth_sol_pair_halfsize_path_20,
        label="avoid_fluctuating_eth_sol_pair_halfsize",
    )
    gated_eth_sol_pair_down_overlay_path_20, gated_eth_sol_pair_down_overlay_affected_20 = apply_hourly_pair_sizing_policy(
        gated_eth_sol_pair_halfsize_path_20,
        pair_all_active_context_20,
        target_symbol_pair="ALL_ACTIVE",
        size_multiplier=0.5,
        target_regime_values={"down"},
    )
    gated_eth_sol_pair_down_overlay_summary_20 = summarize_hourly_portfolio_path(
        gated_eth_sol_pair_down_overlay_path_20,
        mode="avoid_fluctuating_eth_sol_pair_halfsize_down_overlay",
        cost_bps=20,
    )
    gated_eth_sol_pair_downflat_overlay_path_20, gated_eth_sol_pair_downflat_overlay_affected_20 = apply_hourly_pair_sizing_policy(
        gated_eth_sol_pair_halfsize_path_20,
        pair_all_active_context_20,
        target_symbol_pair="ALL_ACTIVE",
        size_multiplier=0.5,
        target_regime_values={"down + flat"},
    )
    gated_eth_sol_pair_downflat_overlay_summary_20 = summarize_hourly_portfolio_path(
        gated_eth_sol_pair_downflat_overlay_path_20,
        mode="avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay",
        cost_bps=20,
    )
    pair_downflat_overlay_holdout_split_20 = summarize_policy_affected_hours_by_split(gated_eth_sol_pair_downflat_overlay_affected_20)
    pair_downflat_overlay_episode_summary_20 = summarize_policy_affected_hour_episodes(gated_eth_sol_pair_downflat_overlay_affected_20)
    pair_downflat_overlay_tail_summary_20 = summarize_hourly_pair_tail_snapshot(
        gated_eth_sol_pair_halfsize_path_20,
        gated_eth_sol_pair_downflat_overlay_path_20,
        gated_eth_sol_pair_downflat_overlay_affected_20,
        split_value="test",
    )
    pair_downflat_overlay_tail_checkpoints_20 = summarize_hourly_pair_shadow_checkpoints_hours(
        gated_eth_sol_pair_halfsize_path_20,
        gated_eth_sol_pair_downflat_overlay_path_20,
        gated_eth_sol_pair_downflat_overlay_affected_20.loc[
            gated_eth_sol_pair_downflat_overlay_affected_20["split_mix"].astype(str).eq("test")
        ].copy(),
        review_hours=[6, 12, 18, 24],
        min_active_hours=4,
    )
    pair_downflat_overlay_tail_blocks_20 = summarize_hourly_pair_forward_blocks_hours(
        gated_eth_sol_pair_halfsize_path_20,
        gated_eth_sol_pair_downflat_overlay_path_20,
        gated_eth_sol_pair_downflat_overlay_affected_20.loc[
            gated_eth_sol_pair_downflat_overlay_affected_20["split_mix"].astype(str).eq("test")
        ].copy(),
        block_hours=6,
        min_active_hours=4,
    )
    pair_downflat_overlay_walkforward_windows_20 = summarize_hourly_pair_walkforward_windows(
        gated_eth_sol_pair_halfsize_path_20,
        gated_eth_sol_pair_downflat_overlay_path_20,
        gated_eth_sol_pair_downflat_overlay_affected_20,
        window_days=10,
        step_days=5,
        min_active_hours=20,
    )
    pair_downflat_overlay_forward_blocks_20 = summarize_hourly_pair_forward_blocks(
        gated_eth_sol_pair_halfsize_path_20,
        gated_eth_sol_pair_downflat_overlay_path_20,
        gated_eth_sol_pair_downflat_overlay_affected_20,
        block_days=5,
        min_active_hours=12,
    )
    pair_downflat_overlay_forward_blocks_10d_20 = summarize_hourly_pair_forward_blocks(
        gated_eth_sol_pair_halfsize_path_20,
        gated_eth_sol_pair_downflat_overlay_path_20,
        gated_eth_sol_pair_downflat_overlay_affected_20,
        block_days=10,
        min_active_hours=12,
    )
    pair_downflat_overlay_shadow_checkpoints_20 = summarize_hourly_pair_shadow_checkpoints(
        gated_eth_sol_pair_halfsize_path_20,
        gated_eth_sol_pair_downflat_overlay_path_20,
        gated_eth_sol_pair_downflat_overlay_affected_20,
        review_days=[5, 10, 15, 20],
        min_active_hours=12,
    )
    pair_predown_bridge_audit_20 = summarize_pair_predown_bridge_audit(
        gated_hourly_portfolio_path_20,
        gated_eth_sol_pair_halfsize_path_20,
        pair_all_active_context_20,
        gated_eth_sol_pair_halfsize_affected_20,
        lead_hours_list=[6, 12, 24],
    )
    pair_downrisk_zone_default_20 = summarize_pair_downrisk_zone_audit(
        gated_hourly_portfolio_path_20,
        gated_eth_sol_pair_halfsize_path_20,
        pair_all_active_context_20,
        gated_eth_sol_pair_halfsize_affected_20,
        lead_hours_list=[6, 12, 24, 48, 72, 96],
        policy="default_pair_halfsize",
        reference_policy="gate_only",
    )
    pair_downrisk_zone_mixed_20 = summarize_pair_downrisk_zone_audit(
        gated_eth_sol_pair_halfsize_path_20,
        gated_eth_sol_pair_downflat_overlay_path_20,
        pair_all_active_context_20,
        gated_eth_sol_pair_downflat_overlay_affected_20,
        lead_hours_list=[6, 12, 24, 48, 72, 96],
        policy="downflat_mixed_tail_overlay",
        reference_policy="default_pair_halfsize",
    )
    downrisk_zone_audit_compare_20 = pd.concat(
        [pair_downrisk_zone_default_20, pair_downrisk_zone_mixed_20],
        ignore_index=True,
    )
    pair_future_pure_down_default_20 = summarize_policy_future_pure_down_lead_audit(
        gated_eth_sol_pair_halfsize_affected_20,
        pair_all_active_context_20,
        future_window_hours_list=[24, 48, 72, 96],
        policy="default_pair_halfsize",
        reference_policy="gate_only",
    )
    pair_future_pure_down_mixed_20 = summarize_policy_future_pure_down_lead_audit(
        gated_eth_sol_pair_downflat_overlay_affected_20,
        pair_all_active_context_20,
        future_window_hours_list=[24, 48, 72, 96],
        policy="downflat_mixed_tail_overlay",
        reference_policy="default_pair_halfsize",
    )
    future_pure_down_lead_audit_compare_20 = pd.concat(
        [pair_future_pure_down_default_20, pair_future_pure_down_mixed_20],
        ignore_index=True,
    )

    gated_eth_sol_up_context_halfsize_path_20, gated_eth_sol_up_context_halfsize_affected_20 = apply_hourly_pair_sizing_policy(
        gated_hourly_portfolio_path_20,
        gated_two_position_detail_20,
        target_symbol_pair="ETH-USD + SOL-USD",
        size_multiplier=0.5,
        target_split_values={"validate", "test", "test + validate"},
        target_regime_values={"up"},
    )
    gated_eth_sol_up_context_halfsize_summary_20 = summarize_hourly_portfolio_path(
        gated_eth_sol_up_context_halfsize_path_20,
        mode="avoid_fluctuating_eth_sol_test_validate_up_halfsize",
        cost_bps=20,
    )
    pair_sizing_compare_20 = summarize_hourly_pair_sizing_compare(
        hourly_portfolio_path_20,
        gated_hourly_portfolio_path_20,
        gated_eth_sol_up_context_halfsize_path_20,
        gated_eth_sol_up_context_halfsize_affected_20,
        conditioned_label="avoid_fluctuating_eth_sol_test_validate_up_halfsize",
    )
    pair_sizing_holdout_split_20 = summarize_policy_affected_hours_by_split(gated_eth_sol_up_context_halfsize_affected_20)

    gated_eth_sol_test_up_halfsize_path_20, gated_eth_sol_test_up_halfsize_affected_20 = apply_hourly_pair_sizing_policy(
        gated_hourly_portfolio_path_20,
        gated_two_position_detail_20,
        target_symbol_pair="ETH-USD + SOL-USD",
        size_multiplier=0.5,
        target_split_values={"test"},
        target_regime_values={"up"},
    )
    gated_eth_sol_test_up_halfsize_summary_20 = summarize_hourly_portfolio_path(
        gated_eth_sol_test_up_halfsize_path_20,
        mode="avoid_fluctuating_eth_sol_test_up_halfsize",
        cost_bps=20,
    )
    pair_sizing_compare_test_20 = summarize_hourly_pair_sizing_compare(
        hourly_portfolio_path_20,
        gated_hourly_portfolio_path_20,
        gated_eth_sol_test_up_halfsize_path_20,
        gated_eth_sol_test_up_halfsize_affected_20,
        conditioned_label="avoid_fluctuating_eth_sol_test_up_halfsize",
    )
    pair_sizing_holdout_split_test_20 = summarize_policy_affected_hours_by_split(gated_eth_sol_test_up_halfsize_affected_20)

    sizing_candidate_compare_20 = summarize_sizing_candidate_compare(
        pair_sizing_compare_pair_20,
        pair_sizing_holdout_split_pair_20,
        pair_sizing_compare_20,
        pair_sizing_holdout_split_20,
        pair_sizing_compare_test_20,
        pair_sizing_holdout_split_test_20,
    )
    policy_admission_queue_20 = summarize_breakout_policy_admission_queue(
        pair_sizing_compare_pair_20,
        pair_regime_coverage_audit_20,
        pair_pure_test_tail_summary_20,
        pair_forward_blocks_pair_20,
        pair_forward_blocks_pair_10d_20,
        gated_eth_sol_pair_down_overlay_summary_20,
        gated_eth_sol_pair_down_overlay_affected_20,
        gated_eth_sol_pair_downflat_overlay_summary_20,
        gated_eth_sol_pair_downflat_overlay_affected_20,
        pair_downflat_overlay_tail_summary_20,
        pair_downflat_overlay_forward_blocks_20,
        pair_downflat_overlay_forward_blocks_10d_20,
    )
    admission_gate_checklist_20 = summarize_breakout_admission_gate_checklist(
        policy_admission_queue_20,
        pair_pure_test_tail_checkpoints_20,
    )
    gate_clearance_protocol_20 = summarize_breakout_gate_clearance_protocol(
        policy_admission_queue_20,
        pair_downflat_overlay_tail_blocks_20,
    )

    compare_df = pd.concat([v0_summary, fib_summary], ignore_index=True)
    compare_df["trade_keep_ratio_vs_v0"] = compare_df["trades"] / max(1, int(v0_summary.iloc[0]["trades"]))

    raw_events.to_csv(V0_ART_DIR / "raw_events_with_confirm_trend_regime.csv", index=False)
    gated_events.to_csv(V0_ART_DIR / "avoid_fluctuating_events.csv", index=False)
    v0_trades.to_csv(V0_ART_DIR / "trades.csv", index=False)
    v0_summary.to_csv(V0_ART_DIR / "summary.csv", index=False)
    v0_by_asset.to_csv(V0_ART_DIR / "summary_by_asset.csv", index=False)
    v0_by_split.to_csv(V0_ART_DIR / "summary_by_split.csv", index=False)
    v0_by_regime.to_csv(V0_ART_DIR / "summary_by_regime.csv", index=False)
    gated_trades.to_csv(V0_ART_DIR / "avoid_fluctuating_trades.csv", index=False)
    gated_summary.to_csv(V0_ART_DIR / "avoid_fluctuating_summary.csv", index=False)
    gated_by_asset.to_csv(V0_ART_DIR / "avoid_fluctuating_summary_by_asset.csv", index=False)
    gated_by_split.to_csv(V0_ART_DIR / "avoid_fluctuating_summary_by_split.csv", index=False)
    gated_by_regime.to_csv(V0_ART_DIR / "avoid_fluctuating_summary_by_regime.csv", index=False)
    confirm1_trades.to_csv(V0_ART_DIR / "confirm1_trades.csv", index=False)
    confirm1_summary.to_csv(V0_ART_DIR / "confirm1_summary.csv", index=False)
    confirm1_by_asset.to_csv(V0_ART_DIR / "confirm1_summary_by_asset.csv", index=False)
    confirm1_by_split.to_csv(V0_ART_DIR / "confirm1_summary_by_split.csv", index=False)
    confirm1_by_regime.to_csv(V0_ART_DIR / "confirm1_summary_by_regime.csv", index=False)
    confirm_compare_df.to_csv(V0_ART_DIR / "raw_confirm1_same_frame_compare.csv", index=False)
    cost_sensitivity_table(v0_trades, cost_bps_list=[0, 10, 20, 50]).to_csv(V0_ART_DIR / "cost_sensitivity.csv", index=False)
    context_net_table(v0_trades, group_col="split", cost_bps=20).to_csv(V0_ART_DIR / "cost_sensitivity_20bps_by_split.csv", index=False)
    context_net_table(v0_trades, group_col="regime", cost_bps=20).to_csv(V0_ART_DIR / "cost_sensitivity_20bps_by_regime.csv", index=False)
    overlap_summary, overlap_profile = overlap_summary_table(v0_trades)
    overlap_summary.to_csv(V0_ART_DIR / "cross_asset_overlap_summary.csv", index=False)
    overlap_profile.to_csv(V0_ART_DIR / "cross_asset_overlap_profile.csv", index=False)
    capital_alloc_summary, capital_alloc_selected, capital_alloc_equal_weight = capital_allocation_first_pass(v0_trades, cost_bps_list=[0, 20])
    capital_alloc_summary.to_csv(V0_ART_DIR / "capital_allocation_first_pass.csv", index=False)
    capital_alloc_selected.to_csv(V0_ART_DIR / "capital_allocation_1slot_selected_trades.csv", index=False)
    capital_alloc_equal_weight.to_csv(V0_ART_DIR / "capital_allocation_equal_weight_entry_first_pass.csv", index=False)
    hourly_portfolio_path_20.to_csv(V0_ART_DIR / "capital_allocation_equal_weight_hourly_path_20bps.csv", index=False)
    hourly_portfolio_summary_20.to_csv(V0_ART_DIR / "capital_allocation_equal_weight_hourly_summary_20bps.csv", index=False)
    hourly_split_summary_20.to_csv(V0_ART_DIR / "capital_allocation_equal_weight_hourly_by_split_20bps.csv", index=False)
    hourly_regime_summary_20.to_csv(V0_ART_DIR / "capital_allocation_equal_weight_hourly_by_regime_20bps.csv", index=False)
    confirm1_hourly_portfolio_path_20.to_csv(V0_ART_DIR / "confirm1_capital_allocation_equal_weight_hourly_path_20bps.csv", index=False)
    confirm1_hourly_portfolio_summary_20.to_csv(V0_ART_DIR / "confirm1_capital_allocation_equal_weight_hourly_summary_20bps.csv", index=False)
    gated_hourly_portfolio_path_20.to_csv(V0_ART_DIR / "avoid_fluctuating_capital_allocation_equal_weight_hourly_path_20bps.csv", index=False)
    gated_hourly_portfolio_summary_20.to_csv(V0_ART_DIR / "avoid_fluctuating_capital_allocation_equal_weight_hourly_summary_20bps.csv", index=False)
    gated_hourly_split_summary_20.to_csv(V0_ART_DIR / "avoid_fluctuating_capital_allocation_equal_weight_hourly_by_split_20bps.csv", index=False)
    gated_hourly_regime_summary_20.to_csv(V0_ART_DIR / "avoid_fluctuating_capital_allocation_equal_weight_hourly_by_regime_20bps.csv", index=False)
    gated_eth_sol_pair_halfsize_path_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_hourly_path_20bps.csv", index=False)
    gated_eth_sol_pair_halfsize_summary_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_hourly_summary_20bps.csv", index=False)
    gated_eth_sol_pair_halfsize_affected_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_affected_hours_20bps.csv", index=False)
    pair_sizing_compare_pair_20.to_csv(V0_ART_DIR / "raw_gate_eth_sol_pair_halfsize_compare_20bps.csv", index=False)
    pair_sizing_holdout_split_pair_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_holdout_split_20bps.csv", index=False)
    pair_sizing_holdout_regime_pair_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_holdout_regime_20bps.csv", index=False)
    pair_sizing_holdout_split_regime_pair_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_holdout_split_regime_20bps.csv", index=False)
    pair_default_episode_summary_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_episode_summary_20bps.csv", index=False)
    pair_regime_coverage_audit_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_regime_coverage_audit_20bps.csv", index=False)
    pair_walkforward_windows_pair_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_walkforward_windows_20bps.csv", index=False)
    pair_forward_blocks_pair_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_forward_blocks_20bps.csv", index=False)
    pair_forward_blocks_pair_10d_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_forward_blocks_10d_20bps.csv", index=False)
    pair_shadow_checkpoints_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_shadow_checkpoints_20bps.csv", index=False)
    pair_pure_test_tail_summary_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_pure_test_tail_20bps.csv", index=False)
    pair_pure_test_tail_checkpoints_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_pure_test_tail_checkpoints_20bps.csv", index=False)
    pair_pure_test_tail_blocks_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_pure_test_tail_forward_blocks_6h_20bps.csv", index=False)
    gated_eth_sol_pair_down_overlay_path_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_down_overlay_hourly_path_20bps.csv", index=False)
    gated_eth_sol_pair_down_overlay_summary_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_down_overlay_hourly_summary_20bps.csv", index=False)
    gated_eth_sol_pair_down_overlay_affected_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_down_overlay_affected_hours_20bps.csv", index=False)
    gated_eth_sol_pair_downflat_overlay_path_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_hourly_path_20bps.csv", index=False)
    gated_eth_sol_pair_downflat_overlay_summary_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_hourly_summary_20bps.csv", index=False)
    gated_eth_sol_pair_downflat_overlay_affected_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_affected_hours_20bps.csv", index=False)
    pair_downflat_overlay_holdout_split_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_holdout_split_20bps.csv", index=False)
    pair_downflat_overlay_episode_summary_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_episode_summary_20bps.csv", index=False)
    pair_downflat_overlay_tail_summary_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_pure_test_tail_20bps.csv", index=False)
    pair_downflat_overlay_tail_checkpoints_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_pure_test_tail_checkpoints_20bps.csv", index=False)
    pair_downflat_overlay_tail_blocks_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_pure_test_tail_forward_blocks_6h_20bps.csv", index=False)
    pair_downflat_overlay_walkforward_windows_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_walkforward_windows_20bps.csv", index=False)
    pair_downflat_overlay_forward_blocks_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_forward_blocks_20bps.csv", index=False)
    pair_downflat_overlay_forward_blocks_10d_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_forward_blocks_10d_20bps.csv", index=False)
    pair_downflat_overlay_shadow_checkpoints_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_shadow_checkpoints_20bps.csv", index=False)
    gated_eth_sol_up_context_halfsize_path_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_test_validate_up_halfsize_hourly_path_20bps.csv", index=False)
    gated_eth_sol_up_context_halfsize_summary_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_test_validate_up_halfsize_hourly_summary_20bps.csv", index=False)
    gated_eth_sol_up_context_halfsize_affected_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_test_validate_up_halfsize_affected_hours_20bps.csv", index=False)
    pair_sizing_compare_20.to_csv(V0_ART_DIR / "raw_gate_eth_sol_test_validate_up_halfsize_compare_20bps.csv", index=False)
    pair_sizing_holdout_split_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_test_validate_up_halfsize_holdout_split_20bps.csv", index=False)
    gated_eth_sol_test_up_halfsize_path_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_test_up_halfsize_hourly_path_20bps.csv", index=False)
    gated_eth_sol_test_up_halfsize_summary_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_test_up_halfsize_hourly_summary_20bps.csv", index=False)
    gated_eth_sol_test_up_halfsize_affected_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_test_up_halfsize_affected_hours_20bps.csv", index=False)
    pair_sizing_compare_test_20.to_csv(V0_ART_DIR / "raw_gate_eth_sol_test_up_halfsize_compare_20bps.csv", index=False)
    pair_sizing_holdout_split_test_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_test_up_halfsize_holdout_split_20bps.csv", index=False)
    sizing_candidate_compare_20.to_csv(V0_ART_DIR / "avoid_fluctuating_sizing_candidate_compare_20bps.csv", index=False)
    policy_admission_queue_20.to_csv(V0_ART_DIR / "avoid_fluctuating_policy_admission_queue_20bps.csv", index=False)
    admission_gate_checklist_20.to_csv(V0_ART_DIR / "avoid_fluctuating_admission_gate_checklist_20bps.csv", index=False)
    gate_clearance_protocol_20.to_csv(V0_ART_DIR / "avoid_fluctuating_gate_clearance_protocol_20bps.csv", index=False)
    pair_predown_bridge_audit_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_predown_bridge_audit_20bps.csv", index=False)
    pair_downrisk_zone_default_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_downrisk_zone_audit_20bps.csv", index=False)
    pair_downrisk_zone_mixed_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_downrisk_zone_audit_20bps.csv", index=False)
    downrisk_zone_audit_compare_20.to_csv(V0_ART_DIR / "avoid_fluctuating_downrisk_zone_audit_compare_20bps.csv", index=False)
    pair_future_pure_down_default_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_future_pure_down_lead_audit_20bps.csv", index=False)
    pair_future_pure_down_mixed_20.to_csv(V0_ART_DIR / "avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_future_pure_down_lead_audit_20bps.csv", index=False)
    future_pure_down_lead_audit_compare_20.to_csv(V0_ART_DIR / "avoid_fluctuating_future_pure_down_lead_audit_compare_20bps.csv", index=False)
    hourly_active_bucket_compare_20.to_csv(V0_ART_DIR / "hourly_active_position_bucket_compare_20bps.csv", index=False)
    hourly_two_position_symbol_mix_compare_20.to_csv(V0_ART_DIR / "hourly_active_position_2_symbol_mix_compare_20bps.csv", index=False)
    hourly_two_position_pair_context_compare_20.to_csv(V0_ART_DIR / "hourly_active_position_2_pair_context_compare_20bps.csv", index=False)
    gate_compare_df.to_csv(V0_ART_DIR / "raw_avoid_fluctuating_same_frame_compare.csv", index=False)

    fib_trades.to_csv(AB_ART_DIR / "fib_trades.csv", index=False)
    compare_df.to_csv(AB_ART_DIR / "ab_summary.csv", index=False)
    pd.concat([v0_by_asset, fib_by_asset], ignore_index=True).to_csv(AB_ART_DIR / "ab_summary_by_asset.csv", index=False)
    pd.concat([v0_by_split, fib_by_split], ignore_index=True).to_csv(AB_ART_DIR / "ab_summary_by_split.csv", index=False)
    pd.concat([v0_by_regime, fib_by_regime], ignore_index=True).to_csv(AB_ART_DIR / "ab_summary_by_regime.csv", index=False)

    equity_img_name = "ab_equity_curve.png"
    asset_img_name = "ab_asset_mean_return.png"
    save_plot(v0_trades, fib_trades, AB_SITE_DIR / equity_img_name)
    save_asset_plot(pd.concat([v0_by_asset, fib_by_asset], ignore_index=True), AB_SITE_DIR / asset_img_name)

    build_v0_report(
        v0_result,
        V0_SITE_DIR / "report.html",
        confirm_compare=confirm_compare_df,
        gate_compare=gate_compare_df,
        hourly_portfolio_summary=hourly_portfolio_summary_20,
        hourly_split_summary=hourly_split_summary_20,
        hourly_regime_summary=hourly_regime_summary_20,
        gate_hourly_split_summary=gated_hourly_split_summary_20,
        gate_hourly_regime_summary=gated_hourly_regime_summary_20,
        hourly_active_bucket_compare=hourly_active_bucket_compare_20,
        hourly_two_position_symbol_mix_compare=hourly_two_position_symbol_mix_compare_20,
        hourly_two_position_pair_context_compare=hourly_two_position_pair_context_compare_20,
        pair_sizing_compare=pair_sizing_compare_20,
        pair_sizing_affected_hours=gated_eth_sol_up_context_halfsize_affected_20,
        sizing_candidate_compare=sizing_candidate_compare_20,
        pair_walkforward_windows=pair_walkforward_windows_pair_20,
        pair_forward_blocks=pair_forward_blocks_pair_20,
        pair_forward_blocks_10d=pair_forward_blocks_pair_10d_20,
        pair_shadow_checkpoints=pair_shadow_checkpoints_20,
        pair_pure_test_tail_summary=pair_pure_test_tail_summary_20,
        pair_pure_test_tail_checkpoints=pair_pure_test_tail_checkpoints_20,
        pair_pure_test_tail_blocks=pair_pure_test_tail_blocks_20,
        pair_sizing_holdout_regime=pair_sizing_holdout_regime_pair_20,
        pair_sizing_holdout_split_regime=pair_sizing_holdout_split_regime_pair_20,
        pair_default_episode_summary=pair_default_episode_summary_20,
        pair_down_overlay_summary=gated_eth_sol_pair_down_overlay_summary_20,
        pair_down_overlay_affected_hours=gated_eth_sol_pair_down_overlay_affected_20,
        pair_downflat_overlay_summary=gated_eth_sol_pair_downflat_overlay_summary_20,
        pair_downflat_overlay_holdout_split=pair_downflat_overlay_holdout_split_20,
        pair_downflat_overlay_episode_summary=pair_downflat_overlay_episode_summary_20,
        pair_downflat_overlay_tail_summary=pair_downflat_overlay_tail_summary_20,
        pair_downflat_overlay_tail_checkpoints=pair_downflat_overlay_tail_checkpoints_20,
        pair_downflat_overlay_tail_blocks=pair_downflat_overlay_tail_blocks_20,
        pair_downflat_overlay_walkforward_windows=pair_downflat_overlay_walkforward_windows_20,
        pair_downflat_overlay_forward_blocks=pair_downflat_overlay_forward_blocks_20,
        pair_downflat_overlay_forward_blocks_10d=pair_downflat_overlay_forward_blocks_10d_20,
        pair_downflat_overlay_shadow_checkpoints=pair_downflat_overlay_shadow_checkpoints_20,
        policy_admission_queue=policy_admission_queue_20,
        admission_gate_checklist=admission_gate_checklist_20,
        gate_clearance_protocol=gate_clearance_protocol_20,
        pair_predown_bridge_audit=pair_predown_bridge_audit_20,
        downrisk_zone_audit_compare=downrisk_zone_audit_compare_20,
        future_pure_down_lead_audit_compare=future_pure_down_lead_audit_compare_20,
    )
    build_ab_report(v0_result, fib_result, AB_SITE_DIR / "report.html", equity_img_name, asset_img_name, compare_df)


if __name__ == "__main__":
    main()
