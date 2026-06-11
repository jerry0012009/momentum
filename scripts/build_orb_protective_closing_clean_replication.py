#!/usr/bin/env python3
from __future__ import annotations

import math
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

from build_volume_supportflip_higherlow_first_verdict import ASSETS, ensure_dir, pct, num, render_table

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_orb_protective_closing_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_orb_protective_closing_15m"
REPORT_PATH = SITE_DIR / "report.html"

SUMMARY_PATH = ART_DIR / "clean_replication_summary.csv"
ASSET_SUMMARY_PATH = ART_DIR / "clean_replication_asset_summary.csv"
TRADES_PATH = ART_DIR / "clean_replication_trades.csv"
TIME_STABILITY_PATH = ART_DIR / "time_stability.csv"
PARAM_STABILITY_PATH = ART_DIR / "parameter_stability.csv"
CROSS_ASSET_PATH = ART_DIR / "cross_asset_stability.csv"
COST_STABILITY_PATH = ART_DIR / "cost_trade_stability.csv"
META_PATH = ART_DIR / "clean_replication_meta.csv"

ATR_PERIOD = 14
STOP_ATR = 1.0
TARGET_ATR = 2.0
TIME_STOP_BARS = 8
BREAK_EVEN_R = 1.0
COSTS = [6.0, 10.0, 15.0, 20.0]
PRIMARY_COST = 6.0
PRIMARY_RANGE_BARS = 2
PRIMARY_TAU = 0.10
RANGE_BARS_GRID = [2, 3]
TAU_GRID = [0.00, 0.10, 0.20]
PSEUDO_OPENS = {(0, 0), (8, 0), (13, 30)}
VARIANTS = [
    "raw_orb",
    "confirm1_outside",
    "confirm2of3_outside",
    "retest_hold",
    "protective_close_overlay",
]
PRIMARY_VARIANT = "confirm1_outside"


def load_cached_bars(symbol: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df.sort_values("timestamp").reset_index(drop=True)



def compute_atr(df: pd.DataFrame, period: int = ATR_PERIOD) -> pd.Series:
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



def prepare_bars(asset: str, symbol: str) -> pd.DataFrame:
    bars = load_cached_bars(symbol).copy()
    bars["asset"] = asset
    bars["atr"] = compute_atr(bars, ATR_PERIOD)
    return bars



def pseudo_session_starts(bars: pd.DataFrame) -> list[int]:
    starts: list[int] = []
    for idx, ts in enumerate(bars["timestamp"]):
        ts = pd.to_datetime(ts, utc=True)
        if (int(ts.hour), int(ts.minute)) in PSEUDO_OPENS:
            starts.append(idx)
    return starts



def build_events_for_config(bars: pd.DataFrame, *, range_bars: int, tau_atr: float) -> pd.DataFrame:
    starts = pseudo_session_starts(bars)
    rows: list[dict] = []
    for s_idx, start_idx in enumerate(starts):
        next_start = starts[s_idx + 1] if s_idx + 1 < len(starts) else len(bars)
        range_end = start_idx + range_bars - 1
        if range_end + 1 >= next_start:
            continue
        range_slice = bars.iloc[start_idx : range_end + 1]
        if range_slice.empty:
            continue
        range_high = float(range_slice["high"].max())
        range_low = float(range_slice["low"].min())
        range_mid = 0.5 * (range_high + range_low)
        breakout_idx = None
        threshold_at_break = None
        atr_at_break = None
        for idx in range(range_end + 1, next_start):
            atr_here = float(bars.iloc[idx]["atr"]) if pd.notna(bars.iloc[idx]["atr"]) else float("nan")
            if not math.isfinite(atr_here) or atr_here <= 0:
                continue
            threshold = range_high + tau_atr * atr_here
            if float(bars.iloc[idx]["close"]) > threshold:
                breakout_idx = idx
                threshold_at_break = threshold
                atr_at_break = atr_here
                break
        if breakout_idx is None or threshold_at_break is None or atr_at_break is None:
            continue

        session_rows = []
        future_end = min(breakout_idx + 3, next_start - 1)
        future = bars.iloc[breakout_idx + 1 : future_end + 1]
        false_break = float((future["close"] < range_mid).any()) if not future.empty else np.nan

        session_rows.append(
            {
                "asset": bars.iloc[0]["asset"],
                "session_start_ts": bars.iloc[start_idx]["timestamp"],
                "variant": "raw_orb",
                "range_bars": int(range_bars),
                "tau_atr": float(tau_atr),
                "range_high": range_high,
                "range_low": range_low,
                "range_mid": range_mid,
                "breakout_idx": int(breakout_idx),
                "signal_idx": int(breakout_idx),
                "signal_ts": bars.iloc[breakout_idx]["timestamp"],
                "atr_at_signal": float(atr_at_break),
                "threshold_at_signal": float(threshold_at_break),
                "false_break_ratio": false_break,
            }
        )

        invalid = False
        confirm_hits = 0
        confirm1_idx = None
        confirm2_idx = None
        retest_idx = None
        for idx in range(breakout_idx + 1, future_end + 1):
            row = bars.iloc[idx]
            close = float(row["close"])
            low = float(row["low"])
            atr_here = float(row["atr"]) if pd.notna(row["atr"]) else float(atr_at_break)
            if close < range_mid:
                invalid = True
                break
            threshold_here = range_high + tau_atr * atr_here
            if close > threshold_here:
                confirm_hits += 1
                if idx == breakout_idx + 1 and confirm1_idx is None:
                    confirm1_idx = idx
                if confirm_hits >= 2 and confirm2_idx is None:
                    confirm2_idx = idx
            touch = low <= range_high + 0.05 * atr_here
            hold = close >= range_high + 0.03 * atr_here
            if touch and hold and retest_idx is None:
                retest_idx = idx
        if not invalid and confirm1_idx is not None:
            session_rows.append(
                {
                    **session_rows[0],
                    "variant": "confirm1_outside",
                    "signal_idx": int(confirm1_idx),
                    "signal_ts": bars.iloc[confirm1_idx]["timestamp"],
                    "atr_at_signal": float(bars.iloc[confirm1_idx]["atr"]),
                    "threshold_at_signal": float(range_high + tau_atr * float(bars.iloc[confirm1_idx]["atr"])),
                }
            )
            session_rows.append(
                {
                    **session_rows[0],
                    "variant": "protective_close_overlay",
                    "signal_idx": int(confirm1_idx),
                    "signal_ts": bars.iloc[confirm1_idx]["timestamp"],
                    "atr_at_signal": float(bars.iloc[confirm1_idx]["atr"]),
                    "threshold_at_signal": float(range_high + tau_atr * float(bars.iloc[confirm1_idx]["atr"])),
                }
            )
        if not invalid and confirm2_idx is not None:
            session_rows.append(
                {
                    **session_rows[0],
                    "variant": "confirm2of3_outside",
                    "signal_idx": int(confirm2_idx),
                    "signal_ts": bars.iloc[confirm2_idx]["timestamp"],
                    "atr_at_signal": float(bars.iloc[confirm2_idx]["atr"]),
                    "threshold_at_signal": float(range_high + tau_atr * float(bars.iloc[confirm2_idx]["atr"])),
                }
            )
        if not invalid and retest_idx is not None:
            session_rows.append(
                {
                    **session_rows[0],
                    "variant": "retest_hold",
                    "signal_idx": int(retest_idx),
                    "signal_ts": bars.iloc[retest_idx]["timestamp"],
                    "atr_at_signal": float(bars.iloc[retest_idx]["atr"]),
                    "threshold_at_signal": float(range_high + tau_atr * float(bars.iloc[retest_idx]["atr"])),
                }
            )
        rows.extend(session_rows)
    if not rows:
        return pd.DataFrame(
            columns=[
                "asset","session_start_ts","variant","range_bars","tau_atr","range_high","range_low","range_mid",
                "breakout_idx","signal_idx","signal_ts","atr_at_signal","threshold_at_signal","false_break_ratio"
            ]
        )
    return pd.DataFrame(rows).sort_values(["asset", "signal_idx", "variant"]).reset_index(drop=True)



def simulate_events(bars: pd.DataFrame, events: pd.DataFrame, *, cost_bps_per_side: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    asset = str(bars.iloc[0]["asset"])
    if events.empty:
        nav = pd.DataFrame([
            {"asset": asset, "variant": PRIMARY_VARIANT, "timestamp": bars.iloc[0]["timestamp"], "nav": 1.0, "cost_bps_per_side": float(cost_bps_per_side)}
        ])
        return pd.DataFrame(), nav

    cost_rate = float(cost_bps_per_side) / 10000.0
    trades: list[dict] = []
    nav_rows: list[dict] = []
    last_exit_by_variant = {variant: -1 for variant in VARIANTS}
    nav_by_variant = {variant: 1.0 for variant in VARIANTS}

    for variant in VARIANTS:
        nav_rows.append({"asset": asset, "variant": variant, "timestamp": bars.iloc[0]["timestamp"], "nav": 1.0, "cost_bps_per_side": float(cost_bps_per_side)})

    for _, event in events.sort_values(["variant", "signal_idx"]).iterrows():
        variant = str(event["variant"])
        signal_idx = int(event["signal_idx"])
        if signal_idx <= last_exit_by_variant[variant]:
            continue
        entry_idx = signal_idx + 1
        if entry_idx >= len(bars):
            continue
        atr = float(event["atr_at_signal"]) if pd.notna(event["atr_at_signal"]) else float("nan")
        entry_price = float(bars.iloc[entry_idx]["open"])
        if not math.isfinite(atr) or atr <= 0 or not math.isfinite(entry_price) or entry_price <= 0:
            continue

        stop_price = entry_price - STOP_ATR * atr
        target_price = entry_price + TARGET_ATR * atr
        protective_stop = stop_price
        hit_break_even = False
        last_bar_idx = min(entry_idx + TIME_STOP_BARS - 1, len(bars) - 1)
        exit_idx = None
        exit_price = None
        exit_reason = None

        for idx in range(entry_idx, last_bar_idx + 1):
            probe = bars.iloc[idx]
            low = float(probe["low"])
            high = float(probe["high"])

            if variant == "protective_close_overlay":
                if (not hit_break_even) and high >= entry_price + BREAK_EVEN_R * atr:
                    protective_stop = max(protective_stop, entry_price)
                    hit_break_even = True
                if low <= protective_stop:
                    exit_idx = idx
                    exit_price = protective_stop
                    exit_reason = "breakeven_lift" if hit_break_even and protective_stop >= entry_price else "atr_stop"
                    break
            else:
                if low <= stop_price:
                    exit_idx = idx
                    exit_price = stop_price
                    exit_reason = "atr_stop"
                    break
                if high >= target_price:
                    exit_idx = idx
                    exit_price = target_price
                    exit_reason = "atr_target"
                    break

        if exit_idx is None:
            exit_idx = last_bar_idx
            exit_price = float(bars.iloc[exit_idx]["close"])
            exit_reason = "time_stop"

        gross_mult = exit_price / entry_price
        net_mult = gross_mult * (1.0 - cost_rate) * (1.0 - cost_rate)
        net_ret = net_mult - 1.0
        nav_by_variant[variant] *= net_mult
        trades.append(
            {
                "asset": asset,
                "variant": variant,
                "cost_bps_per_side": float(cost_bps_per_side),
                "session_start_ts": pd.to_datetime(event["session_start_ts"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "signal_ts": pd.to_datetime(event["signal_ts"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_ts": bars.iloc[entry_idx]["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": bars.iloc[exit_idx]["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "range_bars": int(event["range_bars"]),
                "tau_atr": float(event["tau_atr"]),
                "signal_idx": signal_idx,
                "entry_price": entry_price,
                "exit_price": exit_price,
                "gross_ret": gross_mult - 1.0,
                "net_ret": net_ret,
                "hold_bars": int(exit_idx - entry_idx + 1),
                "false_break_ratio": float(event["false_break_ratio"]) if pd.notna(event["false_break_ratio"]) else np.nan,
                "exit_reason": exit_reason,
                "win": int(net_ret > 0),
            }
        )
        nav_rows.append(
            {
                "asset": asset,
                "variant": variant,
                "timestamp": bars.iloc[exit_idx]["timestamp"],
                "nav": nav_by_variant[variant],
                "cost_bps_per_side": float(cost_bps_per_side),
            }
        )
        last_exit_by_variant[variant] = exit_idx
    return pd.DataFrame(trades), pd.DataFrame(nav_rows)



def max_drawdown(nav: pd.DataFrame) -> float:
    if nav.empty or "nav" not in nav:
        return float("nan")
    series = pd.to_numeric(nav["nav"], errors="coerce").dropna()
    if series.empty:
        return float("nan")
    peak = series.cummax()
    dd = series / peak - 1.0
    return float(dd.min())



def summarize_variant(asset: str, variant: str, cost: float, trades: pd.DataFrame, nav: pd.DataFrame, event_count: int) -> dict:
    if trades.empty:
        return {
            "asset": asset,
            "variant": variant,
            "cost_bps_per_side": float(cost),
            "events": int(event_count),
            "trades": 0,
            "trade_accept_ratio": 0.0 if event_count else np.nan,
            "no_trade_ratio": 1.0 if event_count else np.nan,
            "win_rate": np.nan,
            "avg_net_ret": np.nan,
            "total_return": 0.0,
            "false_break_ratio": np.nan,
            "max_drawdown": 0.0,
            "avg_hold_bars": np.nan,
        }
    return {
        "asset": asset,
        "variant": variant,
        "cost_bps_per_side": float(cost),
        "events": int(event_count),
        "trades": int(len(trades)),
        "trade_accept_ratio": float(len(trades) / event_count) if event_count else np.nan,
        "no_trade_ratio": float(1.0 - len(trades) / event_count) if event_count else np.nan,
        "win_rate": float(trades["win"].mean()),
        "avg_net_ret": float(trades["net_ret"].mean()),
        "total_return": float(np.prod(1.0 + trades["net_ret"].to_numpy()) - 1.0),
        "false_break_ratio": float(trades["false_break_ratio"].mean()) if trades["false_break_ratio"].notna().any() else np.nan,
        "max_drawdown": float(max_drawdown(nav)),
        "avg_hold_bars": float(trades["hold_bars"].mean()),
    }



def run_grid() -> tuple[pd.DataFrame, pd.DataFrame]:
    summary_rows: list[dict] = []
    trade_frames: list[pd.DataFrame] = []

    for asset, symbol in ASSETS.items():
        bars = prepare_bars(asset, symbol)
        for range_bars in RANGE_BARS_GRID:
            for tau_atr in TAU_GRID:
                events = build_events_for_config(bars, range_bars=range_bars, tau_atr=tau_atr)
                for cost in COSTS:
                    trades, nav = simulate_events(bars, events, cost_bps_per_side=cost)
                    for variant in VARIANTS:
                        variant_events = events[events["variant"] == variant].copy()
                        variant_trades = trades[trades["variant"] == variant].copy() if not trades.empty else pd.DataFrame()
                        variant_nav = nav[nav["variant"] == variant].copy() if not nav.empty else pd.DataFrame()
                        row = summarize_variant(asset, variant, cost, variant_trades, variant_nav, len(variant_events))
                        row["range_bars"] = int(range_bars)
                        row["tau_atr"] = float(tau_atr)
                        summary_rows.append(row)
                    if not trades.empty:
                        trade_frames.append(trades)
    summary_df = pd.DataFrame(summary_rows)
    trades_df = pd.concat(trade_frames, ignore_index=True) if trade_frames else pd.DataFrame()
    return summary_df, trades_df



def overall_by_variant(summary_df: pd.DataFrame, *, range_bars: int, tau_atr: float, cost: float) -> pd.DataFrame:
    scope = summary_df[
        (summary_df["range_bars"] == int(range_bars))
        & (summary_df["tau_atr"].round(4) == round(float(tau_atr), 4))
        & (summary_df["cost_bps_per_side"] == float(cost))
    ].copy()
    rows = []
    for variant, g in scope.groupby("variant"):
        rows.append(
            {
                "variant": variant,
                "range_bars": int(range_bars),
                "tau_atr": float(tau_atr),
                "cost_bps_per_side": float(cost),
                "mean_total_return": float(g["total_return"].mean()),
                "positive_asset_ratio": float((g["total_return"] > 0).mean()),
                "mean_trades": float(g["trades"].mean()),
                "mean_no_trade_ratio": float(g["no_trade_ratio"].mean()),
                "mean_false_break_ratio": float(g["false_break_ratio"].mean()) if g["false_break_ratio"].notna().any() else np.nan,
                "mean_max_drawdown": float(g["max_drawdown"].mean()),
            }
        )
    return pd.DataFrame(rows).sort_values("mean_total_return", ascending=False).reset_index(drop=True)



def build_time_stability(summary_df: pd.DataFrame, trades_df: pd.DataFrame) -> pd.DataFrame:
    base = summary_df[
        (summary_df["variant"] == PRIMARY_VARIANT)
        & (summary_df["range_bars"] == PRIMARY_RANGE_BARS)
        & (summary_df["tau_atr"].round(4) == round(PRIMARY_TAU, 4))
        & (summary_df["cost_bps_per_side"] == PRIMARY_COST)
    ].copy()
    if trades_df.empty:
        return pd.DataFrame()
    trades = trades_df[
        (trades_df["variant"] == PRIMARY_VARIANT)
        & (trades_df["range_bars"] == PRIMARY_RANGE_BARS)
        & (trades_df["tau_atr"].round(4) == round(PRIMARY_TAU, 4))
        & (trades_df["cost_bps_per_side"] == PRIMARY_COST)
    ].copy()
    if trades.empty:
        return pd.DataFrame()
    trades["signal_ts"] = pd.to_datetime(trades["signal_ts"], utc=True)
    rows = []
    for asset in sorted(trades["asset"].unique()):
        asset_trades = trades[trades["asset"] == asset].sort_values("signal_ts").reset_index(drop=True)
        n = len(asset_trades)
        cut = max(1, int(math.ceil(n * 0.6)))
        for label, part in [("first60", asset_trades.iloc[:cut]), ("last40", asset_trades.iloc[cut:])]:
            if part.empty:
                continue
            rows.append(
                {
                    "asset": asset,
                    "window": label,
                    "trades": int(len(part)),
                    "total_return": float(np.prod(1.0 + part["net_ret"].to_numpy()) - 1.0),
                    "win_rate": float(part["win"].mean()),
                    "avg_net_ret": float(part["net_ret"].mean()),
                    "mean_false_break_ratio": float(part["false_break_ratio"].mean()) if part["false_break_ratio"].notna().any() else np.nan,
                }
            )
    return pd.DataFrame(rows)



def build_param_stability(summary_df: pd.DataFrame) -> pd.DataFrame:
    scope = summary_df[
        (summary_df["variant"] == PRIMARY_VARIANT)
        & (summary_df["cost_bps_per_side"] == PRIMARY_COST)
    ].copy()
    rows = []
    for (range_bars, tau_atr), g in scope.groupby(["range_bars", "tau_atr"]):
        rows.append(
            {
                "range_bars": int(range_bars),
                "tau_atr": float(tau_atr),
                "mean_total_return": float(g["total_return"].mean()),
                "positive_asset_ratio": float((g["total_return"] > 0).mean()),
                "mean_trades": float(g["trades"].mean()),
                "mean_no_trade_ratio": float(g["no_trade_ratio"].mean()),
                "mean_false_break_ratio": float(g["false_break_ratio"].mean()) if g["false_break_ratio"].notna().any() else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values("mean_total_return", ascending=False).reset_index(drop=True)



def build_cross_asset(summary_df: pd.DataFrame) -> pd.DataFrame:
    return summary_df[
        (summary_df["variant"] == PRIMARY_VARIANT)
        & (summary_df["range_bars"] == PRIMARY_RANGE_BARS)
        & (summary_df["tau_atr"].round(4) == round(PRIMARY_TAU, 4))
        & (summary_df["cost_bps_per_side"] == PRIMARY_COST)
    ][["asset", "total_return", "trades", "no_trade_ratio", "false_break_ratio", "max_drawdown"]].sort_values("total_return", ascending=False).reset_index(drop=True)



def build_cost_stability(summary_df: pd.DataFrame) -> pd.DataFrame:
    scope = summary_df[
        (summary_df["variant"] == PRIMARY_VARIANT)
        & (summary_df["range_bars"] == PRIMARY_RANGE_BARS)
        & (summary_df["tau_atr"].round(4) == round(PRIMARY_TAU, 4))
    ].copy()
    rows = []
    for cost, g in scope.groupby("cost_bps_per_side"):
        rows.append(
            {
                "cost_bps_per_side": float(cost),
                "mean_total_return": float(g["total_return"].mean()),
                "positive_asset_ratio": float((g["total_return"] > 0).mean()),
                "mean_trades": float(g["trades"].mean()),
                "mean_no_trade_ratio": float(g["no_trade_ratio"].mean()),
                "mean_false_break_ratio": float(g["false_break_ratio"].mean()) if g["false_break_ratio"].notna().any() else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values("cost_bps_per_side").reset_index(drop=True)



def decide_verdict(summary_primary: pd.DataFrame) -> tuple[str, str]:
    if summary_primary.empty:
        return "park / evidence pool", "clean replication 没产出可交易样本，直接 park。"
    best = summary_primary.iloc[0]
    better_than_raw = False
    raw = summary_primary[summary_primary["variant"] == "raw_orb"]
    if not raw.empty:
        better_than_raw = (
            float(best["mean_total_return"]) > float(raw.iloc[0]["mean_total_return"])
            and float(best["mean_false_break_ratio"]) < float(raw.iloc[0]["mean_false_break_ratio"])
        )
    if (
        float(best["mean_total_return"]) > 0
        and float(best["positive_asset_ratio"]) >= 2 / 3
        and float(best["mean_no_trade_ratio"]) <= 0.80
        and better_than_raw
    ):
        return "paper candidate", f"最佳变体 {best['variant']} 在 6bps 下仍保留正向均值，且不是单靠不交易在冒充稳定。"
    return "park / evidence pool", f"最佳变体 {best['variant']} 仍未同时满足收益、跨资产与不靠 no-trade 伪改善的最小门槛。"



def write_report(summary_primary: pd.DataFrame, time_df: pd.DataFrame, param_df: pd.DataFrame, cross_df: pd.DataFrame, cost_df: pd.DataFrame, verdict: str, rationale: str) -> None:
    ensure_dir(SITE_DIR)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    best_variant = summary_primary.iloc[0]["variant"] if not summary_primary.empty else "-"
    best_return = pct(summary_primary.iloc[0]["mean_total_return"]) if not summary_primary.empty else "-"
    best_pos = pct(summary_primary.iloc[0]["positive_asset_ratio"]) if not summary_primary.empty else "-"
    best_no_trade = pct(summary_primary.iloc[0]["mean_no_trade_ratio"]) if not summary_primary.empty else "-"

    html = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Scout Seat · ORB protective closing · clean replication</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1180px; margin: 40px auto; padding: 0 18px; line-height: 1.68; color: #111827; background: #f8fafc; }}
    h1,h2 {{ line-height: 1.25; }}
    .muted {{ color:#6b7280; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    a {{ color:#2563eb; text-decoration:none; }}
  </style>
</head>
<body>
  <p><a href="../../index.html">← 返回首页</a></p>
  <h1>Scout Seat · ORB threshold + protective closing · clean replication</h1>
  <p class="muted">生成时间：{escape(generated_at)} ｜ 数据：Binance 120d / 15m / BTC-USD, ETH-USD, SOL-USD ｜ 当前默认不把它当 breakout 主线复活，而是当作 session-threshold 候选做快筛。</p>

  <div class="card">
    <h2>hard verdict</h2>
    <p><b>{escape(verdict)}</b></p>
    <p>{escape(rationale)}</p>
    <ul>
      <li>当前最佳 6bps 变体：<b>{escape(str(best_variant))}</b></li>
      <li>跨资产平均总收益：<b>{escape(best_return)}</b></li>
      <li>正收益资产占比：<b>{escape(best_pos)}</b></li>
      <li>平均不交易占比：<b>{escape(best_no_trade)}</b></li>
    </ul>
  </div>

  <div class="card">
    <h2>clean replication：五档最小对照（primary config = range 2 bars, τ=0.10 ATR, 6bps）</h2>
    {render_table(summary_primary, percent_cols={'mean_total_return','positive_asset_ratio','mean_no_trade_ratio','mean_false_break_ratio','mean_max_drawdown'}, digits_cols={'mean_trades':1})}
  </div>

  <div class="card">
    <h2>Light Stability Pack · 参数稳定性</h2>
    {render_table(param_df, percent_cols={'mean_total_return','positive_asset_ratio','mean_no_trade_ratio','mean_false_break_ratio'}, digits_cols={'mean_trades':1,'tau_atr':2})}
  </div>

  <div class="card">
    <h2>Light Stability Pack · 时间稳定性</h2>
    {render_table(time_df, percent_cols={'total_return','win_rate','avg_net_ret','mean_false_break_ratio'}, digits_cols={'trades':0})}
  </div>

  <div class="card">
    <h2>Light Stability Pack · 跨标的稳定性</h2>
    {render_table(cross_df, percent_cols={'total_return','no_trade_ratio','false_break_ratio','max_drawdown'}, digits_cols={'trades':0})}
  </div>

  <div class="card">
    <h2>Light Stability Pack · 成本 / 交易数稳定性</h2>
    {render_table(cost_df, percent_cols={'mean_total_return','positive_asset_ratio','mean_no_trade_ratio','mean_false_break_ratio'}, digits_cols={'mean_trades':1,'cost_bps_per_side':0})}
  </div>

  <div class="card">
    <h2>怎么读</h2>
    <ul>
      <li><b>看收益不够，要同时看 no-trade ratio。</b> ORB 很容易靠“更少出手”伪装稳定。</li>
      <li><b>protective_close_overlay</b> 这里是拿 <code>confirm1_outside</code> 的入场，加 <code>+1R 抬 break-even + 8 bars time stop</code> 的退出叠层。</li>
      <li>若下一轮没有 bot2 明确重开指令，且这页结论仍是 <code>park</code>，就不该继续给它默认主资源。</li>
    </ul>
  </div>
</body>
</html>
'''
    REPORT_PATH.write_text(html, encoding="utf-8")



def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    summary_df, trades_df = run_grid()
    summary_df.to_csv(ASSET_SUMMARY_PATH, index=False)
    trades_df.to_csv(TRADES_PATH, index=False)

    summary_primary = overall_by_variant(summary_df, range_bars=PRIMARY_RANGE_BARS, tau_atr=PRIMARY_TAU, cost=PRIMARY_COST)
    time_df = build_time_stability(summary_df, trades_df)
    param_df = build_param_stability(summary_df)
    cross_df = build_cross_asset(summary_df)
    cost_df = build_cost_stability(summary_df)
    verdict, rationale = decide_verdict(summary_primary)

    summary_primary.to_csv(SUMMARY_PATH, index=False)
    time_df.to_csv(TIME_STABILITY_PATH, index=False)
    param_df.to_csv(PARAM_STABILITY_PATH, index=False)
    cross_df.to_csv(CROSS_ASSET_PATH, index=False)
    cost_df.to_csv(COST_STABILITY_PATH, index=False)
    pd.DataFrame([
        {
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "candidate_id": "scout_orb_protective_closing_15m_v1",
            "primary_variant": PRIMARY_VARIANT,
            "primary_range_bars": PRIMARY_RANGE_BARS,
            "primary_tau_atr": PRIMARY_TAU,
            "primary_cost_bps": PRIMARY_COST,
            "hard_verdict": verdict,
            "rationale": rationale,
        }
    ]).to_csv(META_PATH, index=False)

    write_report(summary_primary, time_df, param_df, cross_df, cost_df, verdict, rationale)
    print("[ok] orb protective-closing clean replication generated")
    print("[artifact]", SUMMARY_PATH)
    print("[site]", REPORT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
