#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import math

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank32_ema_slope_structure_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank32_ema_slope_structure_15m"
READING_DIR = ROOT / "reports" / "site" / "reading" / "trendline_alpha_scout"
READING_REPORT = READING_DIR / "report.html"
TODO_PATH = ROOT / "docs" / "TODO.md"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}

COSTS = [6.0, 10.0, 15.0, 20.0]
PRIMARY_COST = 6.0
VARIANTS = [
    "ema_cross_only",
    "ema_cross_plus_slope_floor",
    "ema_cross_plus_slope_reclaim",
]
PRIMARY_VARIANT = "ema_cross_plus_slope_reclaim"
HOLD_BARS = 8
RECLAIM_LOOKBACK = 4
EMA_FAST_1H = 20
EMA_SLOW_1H = 50
SLOPE_FLOOR = 0.0004


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


def render_table(df: pd.DataFrame, percent_cols: set[str] | None = None, digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    percent_cols = percent_cols or set()
    digits_cols = digits_cols or {}
    headers = ''.join(f'<th>{escape(str(c))}</th>' for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = []
        for col in df.columns:
            value = row[col]
            if col in percent_cols:
                text = pct(value)
            elif isinstance(value, (float, np.floating, int, np.integer)) and not isinstance(value, bool):
                text = num(value, digits_cols.get(col, 2))
            else:
                text = str(value)
            cells.append(f'<td>{escape(text)}</td>')
        rows.append(f'<tr>{"".join(cells)}</tr>')
    return f'<table><thead><tr>{headers}</tr></thead><tbody>{"".join(rows)}</tbody></table>'


def load_cached_bars(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    bars = load_cached_bars(symbol, asset)
    market = bars[["timestamp", "close"]].copy().rename(columns={"close": "close_1h_src"}).set_index("timestamp")
    market_1h = market.resample("1h").last().dropna().reset_index()
    market_1h["ema_fast_1h"] = market_1h["close_1h_src"].ewm(span=EMA_FAST_1H, adjust=False).mean()
    market_1h["ema_slow_1h"] = market_1h["close_1h_src"].ewm(span=EMA_SLOW_1H, adjust=False).mean()
    market_1h["fast_slope"] = market_1h["ema_fast_1h"].pct_change()
    market_1h["slow_slope"] = market_1h["ema_slow_1h"].pct_change()

    frame = pd.merge_asof(
        bars.sort_values("timestamp"),
        market_1h.sort_values("timestamp"),
        on="timestamp",
        direction="backward",
    )
    frame["spread_mid"] = (frame["ema_fast_1h"] + frame["ema_slow_1h"]) / 2.0
    frame["long_structure"] = (frame["ema_fast_1h"] > frame["ema_slow_1h"]).fillna(False).astype(int)
    frame["short_structure"] = (frame["ema_fast_1h"] < frame["ema_slow_1h"]).fillna(False).astype(int)
    frame["slope_floor_long"] = (
        (frame["fast_slope"] > SLOPE_FLOOR) & (frame["slow_slope"] > 0)
    ).fillna(False).astype(int)
    frame["slope_floor_short"] = (
        (frame["fast_slope"] < -SLOPE_FLOOR) & (frame["slow_slope"] < 0)
    ).fillna(False).astype(int)
    frame["slope_strength"] = (frame["fast_slope"].abs().fillna(0.0) + frame["slow_slope"].abs().fillna(0.0))

    prev_close = frame["close"].shift(1)
    prev_fast = frame["ema_fast_1h"].shift(1)
    prev_mid = frame["spread_mid"].shift(1)
    recent_low = frame["low"].shift(1).rolling(RECLAIM_LOOKBACK, min_periods=RECLAIM_LOOKBACK).min()
    recent_high = frame["high"].shift(1).rolling(RECLAIM_LOOKBACK, min_periods=RECLAIM_LOOKBACK).max()

    frame["cross_only_long"] = (
        (frame["long_structure"] == 1)
        & (prev_close <= prev_fast)
        & (frame["close"] > frame["ema_fast_1h"])
    ).fillna(False).astype(int)
    frame["cross_only_short"] = (
        (frame["short_structure"] == 1)
        & (prev_close >= prev_fast)
        & (frame["close"] < frame["ema_fast_1h"])
    ).fillna(False).astype(int)

    frame["slope_floor_long_signal"] = (
        (frame["cross_only_long"] == 1) & (frame["slope_floor_long"] == 1)
    ).astype(int)
    frame["slope_floor_short_signal"] = (
        (frame["cross_only_short"] == 1) & (frame["slope_floor_short"] == 1)
    ).astype(int)

    frame["reclaim_long_signal"] = (
        (frame["long_structure"] == 1)
        & (frame["slope_floor_long"] == 1)
        & (recent_low <= prev_mid)
        & (frame["close"] > frame["ema_fast_1h"])
        & (frame["close"] > frame["spread_mid"])
        & (prev_close <= prev_mid)
    ).fillna(False).astype(int)
    frame["reclaim_short_signal"] = (
        (frame["short_structure"] == 1)
        & (frame["slope_floor_short"] == 1)
        & (recent_high >= prev_mid)
        & (frame["close"] < frame["ema_fast_1h"])
        & (frame["close"] < frame["spread_mid"])
        & (prev_close >= prev_mid)
    ).fillna(False).astype(int)
    return frame


def get_signal(frame: pd.DataFrame, idx: int, variant: str) -> tuple[int, str] | None:
    row = frame.iloc[idx]
    if variant == "ema_cross_only":
        if int(row["cross_only_long"]) == 1:
            return 1, "ema_cross_only"
        if int(row["cross_only_short"]) == 1:
            return -1, "ema_cross_only"
    elif variant == "ema_cross_plus_slope_floor":
        if int(row["slope_floor_long_signal"]) == 1:
            return 1, "ema_cross_plus_slope_floor"
        if int(row["slope_floor_short_signal"]) == 1:
            return -1, "ema_cross_plus_slope_floor"
    elif variant == "ema_cross_plus_slope_reclaim":
        if int(row["reclaim_long_signal"]) == 1:
            return 1, "ema_cross_plus_slope_reclaim"
        if int(row["reclaim_short_signal"]) == 1:
            return -1, "ema_cross_plus_slope_reclaim"
    else:
        raise ValueError(f"unknown variant: {variant}")
    return None


def detect_false_reclaim(frame: pd.DataFrame, signal_idx: int, direction: int) -> int:
    level = float(frame.iloc[signal_idx]["spread_mid"])
    for step in range(1, 5):
        j = signal_idx + step
        if j >= len(frame):
            break
        close = float(frame.iloc[j]["close"])
        if direction > 0 and close < level:
            return 1
        if direction < 0 and close > level:
            return 1
    return 0


def build_trades(frame: pd.DataFrame, asset: str, variant: str, cost_bps: float) -> tuple[pd.DataFrame, float, int]:
    rows: list[dict[str, object]] = []
    cost_rate = float(cost_bps) / 10000.0
    last_exit = -1
    eligible_mask = ((frame["long_structure"] == 1) | (frame["short_structure"] == 1)).astype(int)
    eligible_bars = int(eligible_mask.sum())
    signals_seen = 0

    for idx in range(1, len(frame) - 1):
        if idx <= last_exit:
            continue
        signal = get_signal(frame, idx, variant)
        if signal is None:
            continue
        direction, trigger_name = signal
        signals_seen += 1
        entry_idx = idx + 1
        exit_idx = min(entry_idx + HOLD_BARS - 1, len(frame) - 1)
        entry_price = float(frame.iloc[entry_idx]["open"])
        exit_price = float(frame.iloc[exit_idx]["close"])
        if not (math.isfinite(entry_price) and math.isfinite(exit_price) and entry_price > 0 and exit_price > 0):
            continue
        gross_ret = (exit_price / entry_price - 1.0) * direction
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
        rows.append({
            "asset": asset,
            "variant": trigger_name,
            "cost_bps_per_side": float(cost_bps),
            "signal_idx": int(idx),
            "event_ts": pd.to_datetime(frame.iloc[idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "signal_confirmed_at": (pd.to_datetime(frame.iloc[idx]["timestamp"], utc=True) + pd.Timedelta(minutes=15)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "entry_ts": pd.to_datetime(frame.iloc[entry_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "exit_ts": pd.to_datetime(frame.iloc[exit_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "direction": "long" if direction > 0 else "short",
            "entry_price": entry_price,
            "exit_price": exit_price,
            "gross_ret": gross_ret,
            "net_ret": net_ret,
            "hold_bars": int(exit_idx - entry_idx + 1),
            "false_reclaim_ratio": int(detect_false_reclaim(frame, idx, direction)),
            "slope_strength": float(frame.iloc[idx]["slope_strength"]),
            "fast_slope": float(frame.iloc[idx]["fast_slope"]) if not pd.isna(frame.iloc[idx]["fast_slope"]) else np.nan,
            "slow_slope": float(frame.iloc[idx]["slow_slope"]) if not pd.isna(frame.iloc[idx]["slow_slope"]) else np.nan,
        })
        last_exit = exit_idx

    trades = pd.DataFrame(rows)
    no_trade_ratio = 1.0 if eligible_bars == 0 else max(0.0, 1.0 - (signals_seen / eligible_bars))
    return trades, no_trade_ratio, eligible_bars


def summarize_asset(trades: pd.DataFrame, *, asset: str, variant: str, cost_bps: float, no_trade_ratio: float, eligible_bars: int) -> dict[str, object]:
    if trades.empty:
        return {
            "asset": asset,
            "variant": variant,
            "cost_bps_per_side": float(cost_bps),
            "trades": 0,
            "win_rate": np.nan,
            "avg_net_ret": np.nan,
            "median_net_ret": np.nan,
            "total_return": 0.0,
            "false_reclaim_ratio": np.nan,
            "no_trade_ratio": float(no_trade_ratio),
            "eligible_structure_bars": int(eligible_bars),
            "avg_slope_strength": np.nan,
            "long_share": np.nan,
            "short_share": np.nan,
        }
    return {
        "asset": asset,
        "variant": variant,
        "cost_bps_per_side": float(cost_bps),
        "trades": int(len(trades)),
        "win_rate": float((trades["net_ret"] > 0).mean()),
        "avg_net_ret": float(trades["net_ret"].mean()),
        "median_net_ret": float(trades["net_ret"].median()),
        "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
        "false_reclaim_ratio": float(trades["false_reclaim_ratio"].mean()),
        "no_trade_ratio": float(no_trade_ratio),
        "eligible_structure_bars": int(eligible_bars),
        "avg_slope_strength": float(trades["slope_strength"].mean()),
        "long_share": float((trades["direction"] == "long").mean()),
        "short_share": float((trades["direction"] == "short").mean()),
    }


def summarize_overall(asset_summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (variant, cost), grp in asset_summary.groupby(["variant", "cost_bps_per_side"], sort=False):
        total_returns = grp["total_return"].to_numpy(dtype=float)
        rows.append({
            "variant": variant,
            "cost_bps_per_side": float(cost),
            "mean_total_return": float(np.nanmean(total_returns)) if len(total_returns) else np.nan,
            "median_total_return": float(np.nanmedian(total_returns)) if len(total_returns) else np.nan,
            "positive_asset_ratio": float(np.nanmean(total_returns > 0)) if len(total_returns) else np.nan,
            "mean_trades": float(grp["trades"].mean()),
            "mean_false_reclaim_ratio": float(grp["false_reclaim_ratio"].mean()),
            "mean_no_trade_ratio": float(grp["no_trade_ratio"].mean()),
            "mean_win_rate": float(grp["win_rate"].mean()),
            "mean_slope_strength": float(grp["avg_slope_strength"].mean()),
        })
    return pd.DataFrame(rows)


def build_slope_bucket_summary(primary_trades: pd.DataFrame) -> pd.DataFrame:
    if primary_trades.empty or primary_trades["slope_strength"].nunique() < 3:
        return pd.DataFrame(columns=["slope_bucket", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_win_rate"])

    work = primary_trades.copy()
    work["slope_bucket"] = pd.qcut(
        work["slope_strength"],
        q=3,
        labels=["bucket_1", "bucket_2", "bucket_3"],
        duplicates="drop",
    )
    rows = []
    for bucket, grp in work.groupby("slope_bucket", sort=False):
        asset_total = grp.groupby("asset")["net_ret"].apply(lambda s: float((1.0 + s).prod() - 1.0))
        rows.append({
            "slope_bucket": str(bucket),
            "mean_total_return": float(asset_total.mean()) if len(asset_total) else np.nan,
            "positive_asset_ratio": float((asset_total > 0).mean()) if len(asset_total) else np.nan,
            "mean_trades": float(grp.groupby("asset").size().mean()) if len(grp) else np.nan,
            "mean_win_rate": float(grp.groupby("asset")["net_ret"].apply(lambda s: (s > 0).mean()).mean()) if len(grp) else np.nan,
        })
    return pd.DataFrame(rows)


def build_verdict(overall: pd.DataFrame, slope_buckets: pd.DataFrame) -> tuple[str, str]:
    primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    if primary.empty:
        return "park / evidence pool", "主变体没有形成可用样本，连最小 clean replication 都不足以站住。"
    row = primary.iloc[0]
    mean_ret = float(row["mean_total_return"]) if not pd.isna(row["mean_total_return"]) else -1.0
    pos_ratio = float(row["positive_asset_ratio"]) if not pd.isna(row["positive_asset_ratio"]) else 0.0
    mean_trades = float(row["mean_trades"]) if not pd.isna(row["mean_trades"]) else 0.0
    false_ratio = float(row["mean_false_reclaim_ratio"]) if not pd.isna(row["mean_false_reclaim_ratio"]) else 1.0
    no_trade = float(row["mean_no_trade_ratio"]) if not pd.isna(row["mean_no_trade_ratio"]) else 1.0

    positive_buckets = 0
    if not slope_buckets.empty:
        positive_buckets = int((slope_buckets["mean_total_return"] > 0).sum())

    if mean_ret > 0 and pos_ratio >= (2.0 / 3.0) and mean_trades >= 12 and false_ratio <= 0.45 and no_trade <= 0.98 and positive_buckets >= 2:
        return "P1 weak candidate / evidence pool", "最小 clean replication 至少没直接塌掉：成本后仍为正、跨资产不只剩单腿，而且 slope pocket 也不只靠单个热像素。"
    return "park / evidence pool", "最小 clean replication 没把它拉进候选池：要么成本后仍偏弱，要么交易密度 / no-trade ratio / slope-pocket honesty 没能一起站住。"


def update_reading_report() -> None:
    if not READING_REPORT.exists():
        return
    text = READING_REPORT.read_text(encoding="utf-8")
    if "rank32_ema_slope_structure_clean_replication.html" in text:
        return
    anchor = 'rank32_ema_slope_structure_source_intake.html">Rank 32 source intake</a>'
    if anchor not in text:
        return
    text = text.replace(anchor, anchor + ' ｜ <a href="rank32_ema_slope_structure_clean_replication.html">clean replication</a>', 1)
    READING_REPORT.write_text(text, encoding="utf-8")


def update_todo(verdict: str, generated_at: str, overall: pd.DataFrame, slope_buckets: pd.DataFrame) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    if not primary.empty:
        row = primary.iloc[0]
        stats = (
            f"主变体 `{PRIMARY_VARIANT}` 在 `6bps/side` 下跨资产 `mean_total_return≈{pct(row['mean_total_return'])}`、"
            f"`positive_asset_ratio≈{pct(row['positive_asset_ratio'])}`、`mean_trades≈{num(row['mean_trades'],1)}`、"
            f"`mean_false_reclaim_ratio≈{pct(row['mean_false_reclaim_ratio'])}`、`mean_no_trade_ratio≈{pct(row['mean_no_trade_ratio'])}`。"
        )
    else:
        stats = "主变体没有形成可用样本。"

    if slope_buckets.empty:
        slope_note = "当前主变体样本过薄，尚不足以把 slope pocket 可靠拆成 3 桶；这本身也不支持升格。"
    else:
        bucket_parts = []
        for _, row in slope_buckets.iterrows():
            bucket_parts.append(
                f"{row['slope_bucket']}≈{pct(row['mean_total_return'])} / {pct(row['positive_asset_ratio'])}"
            )
        slope_note = "slope-pocket honesty：" + "；".join(bucket_parts) + "。"

    summary_old = "**因此当前默认节奏应改为：`Paper Seat / EMA` 继续按 `waiting_not_due` 处理；若 `Rank 29 / Rank 17 / Rank 2` 仍无真实 append/review row，则下一轮默认先给 `Rank 32` 做那 1 次最小 clean replication，而不是重开已 park 的旧线。**"
    if verdict.startswith("P1"):
        summary_new = "**因此当前默认节奏应改为：`Paper Seat / EMA` 继续按 `waiting_not_due` 处理；`Rank 32` 的最小 clean replication 已落地，若 `Rank 29 / Rank 17 / Rank 2` 仍无真实 append/review row，则下一轮默认只允许给 `Rank 32` 那唯一一次便宜诚实检查预算；若这次检查也不能改变层级，就应压回 `park / evidence pool`。**"
    else:
        summary_new = "**因此当前默认节奏应改为：`Paper Seat / EMA` 继续按 `waiting_not_due` 处理；`Rank 32` 的最小 clean replication 已如实落地且当前维持 `park / evidence pool`。若 `Rank 29 / Rank 17 / Rank 2` 仍无真实 append/review row，则下一轮默认应回到新的 `paper / repo based 5m / 15m crypto` fresh intake，而不是重开已 park 的 `Rank 30 / Rank 31 / Rank 32`。**"
    if summary_old in text:
        text = text.replace(summary_old, summary_new, 1)

    marker = "31. `Rank 31 chanlun-pro second-buy / breakout-retest continuation gate`"
    insert_after = text.find(marker)
    new_block = f"""

32. `Rank 32 EMA structure vs MA slope direction gate`（repo EMA baseline decomposition）→ **`{verdict}`**
     - 已完成 `fresh source intake -> 最小 clean replication`，固定复用 `BTC/ETH/SOL 120d 15m` cache；只比较 `ema_cross_only`、`ema_cross_plus_slope_floor`、`ema_cross_plus_slope_reclaim`，不追新 bar，也不扩成完整 stability pack。
     - 冻结后的 clean-room 规则：`ema_cross_only = higher_tf EMA fast > slow（空头反向）+ close 重新穿回 fast EMA`；`ema_cross_plus_slope_floor = 在前者基础上要求 fast/slow slope 同向且 fast slope 过最小门槛`；`ema_cross_plus_slope_reclaim = 再要求最近 {RECLAIM_LOOKBACK} 根里出现过一次向 spread mid 的回抽，并在当前 bar 重新站回 fast EMA 与 spread mid 同侧`。
     - 当前最诚实的主证据：{stats}
     - {slope_note}
     - **最新补充（{generated_at}）**：这轮最小 clean replication 的 hard verdict 是 **`{verdict}`**。更直白地说：`EMA structure vs MA slope` 已不再只是 `admit_to_clean_replication_queue`；若后续继续认领，默认只能按这个 verdict 走——`P1` 才配拿那唯一允许的一次便宜诚实检查，`park` 则应回到 evidence pool，而不是继续停在 intake 文案上。
     - 网页落点：`reports/site/factors/scout_rank32_ema_slope_structure_15m/report.html`、`reports/site/reading/trendline_alpha_scout/rank32_ema_slope_structure_source_intake.html`。
"""

    if "32. `Rank 32 EMA structure vs MA slope direction gate`" not in text and insert_after != -1:
        end = text.find("\n\n- **2026-03-17 Rank 4~20 park audit", insert_after)
        if end != -1:
            text = text[:end] + new_block + text[end:]

    TODO_PATH.write_text(text, encoding="utf-8")


def build_html(overall: pd.DataFrame, asset_summary: pd.DataFrame, slope_buckets: pd.DataFrame, verdict: str, verdict_reason: str, generated_at: str) -> str:
    primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    if primary.empty:
        headline = "主变体没有形成可用样本。"
    else:
        row = primary.iloc[0]
        headline = (
            f"主变体 {PRIMARY_VARIANT} 在 {int(PRIMARY_COST)}bps/side 下：跨资产 mean_total_return≈{pct(row['mean_total_return'])}、"
            f"positive_asset_ratio≈{pct(row['positive_asset_ratio'])}、mean_trades≈{num(row['mean_trades'],1)}、"
            f"mean_false_reclaim_ratio≈{pct(row['mean_false_reclaim_ratio'])}、mean_no_trade_ratio≈{pct(row['mean_no_trade_ratio'])}。"
        )
    overall_view = overall.copy()
    if not overall_view.empty:
        overall_view["cost_bps_per_side"] = overall_view["cost_bps_per_side"].astype(int)
    asset_view = asset_summary.copy()
    if not asset_view.empty:
        asset_view["cost_bps_per_side"] = asset_view["cost_bps_per_side"].astype(int)
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 32 · EMA structure vs MA slope clean replication</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1100px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background: #f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }}
    .muted {{ color:#6b7280; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    ul {{ padding-left: 20px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    a {{ color:#2563eb; text-decoration:none; }}
  </style>
</head>
<body>
  <p><a href='../../reading/trendline_alpha_scout/report.html'>← 返回 Trendline Alpha Scout</a></p>
  <h1>Rank 32 · EMA structure vs MA slope direction gate</h1>
  <p class='muted'>生成时间：{escape(generated_at)} ｜ 类型：最小 clean replication ｜ 角色：Scout Seat 的 repo-based 15m crypto fast verdict</p>

  <div class='card'>
    <h2>这轮只回答什么</h2>
    <ul>
      <li>固定复用 <code>BTC/ETH/SOL 120d 15m</code> cache，不追新 bar。</li>
      <li>只比较三档最小规则：<code>ema_cross_only</code>、<code>ema_cross_plus_slope_floor</code>、<code>ema_cross_plus_slope_reclaim</code>。</li>
      <li>先回答四个便宜问题：<code>post_cost_return</code>、<code>trade_count</code>、<code>no_trade_ratio</code>、<code>slope-pocket honesty</code>。</li>
      <li>执行口径固定：higher-tf 只用 1h completed bar 的 EMA20 / EMA50 与 slope；入场 = <code>next-bar open</code>；持有 = <code>{HOLD_BARS}</code> 根 15m bar；默认 non-overlap。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>clean-room 规则</h2>
    <ul>
      <li><b>ema_cross_only：</b><code>trade on = higher_tf EMA fast &gt; slow（空头反向）+ close 重新穿回 fast EMA</code>。</li>
      <li><b>ema_cross_plus_slope_floor：</b>在前者基础上，要求 <code>fast/slow slope</code> 同向，且 <code>|fast slope|</code> 过最小门槛 <code>{SLOPE_FLOOR:.4f}</code>。</li>
      <li><b>ema_cross_plus_slope_reclaim：</b>在 slope floor 基础上，再要求最近 <code>{RECLAIM_LOOKBACK}</code> 根出现过一次朝 <code>spread mid</code> 的回抽，并在当前 bar 重新站回 <code>fast EMA + spread mid</code> 同侧。</li>
      <li><b>lookahead guard：</b>所有结构、slope 与 reclaim 判断都只使用当前或更早的 completed bar，不允许回看未来 pocket 再挑斜率阈值。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>hard verdict</h2>
    <p><span class='pill'>{escape(verdict)}</span></p>
    <p><b>{escape(headline)}</b></p>
    <p class='muted'>{escape(verdict_reason)}</p>
  </div>

  <div class='card'>
    <h2>跨资产总表</h2>
    {render_table(overall_view[["variant","cost_bps_per_side","mean_total_return","positive_asset_ratio","mean_trades","mean_false_reclaim_ratio","mean_no_trade_ratio","mean_win_rate","mean_slope_strength"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_false_reclaim_ratio","mean_no_trade_ratio","mean_win_rate"}, digits_cols={"mean_trades":1,"mean_slope_strength":5})}
  </div>

  <div class='card'>
    <h2>分资产摘要</h2>
    {render_table(asset_view[["asset","variant","cost_bps_per_side","trades","total_return","false_reclaim_ratio","no_trade_ratio","win_rate","avg_slope_strength","long_share","short_share"]], percent_cols={"total_return","false_reclaim_ratio","no_trade_ratio","win_rate","long_share","short_share"}, digits_cols={"trades":0,"avg_slope_strength":5})}
  </div>

  <div class='card'>
    <h2>slope-pocket honesty（主变体 6bps）</h2>
    {render_table(slope_buckets[["slope_bucket","mean_total_return","positive_asset_ratio","mean_trades","mean_win_rate"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_win_rate"}, digits_cols={"mean_trades":1})}
  </div>

  <div class='card'>
    <h2>artifact</h2>
    <ul>
      <li><a href='../../../artifacts/scout_rank32_ema_slope_structure_15m/overall_summary.csv'>overall_summary.csv</a></li>
      <li><a href='../../../artifacts/scout_rank32_ema_slope_structure_15m/asset_summary.csv'>asset_summary.csv</a></li>
      <li><a href='../../../artifacts/scout_rank32_ema_slope_structure_15m/trades_primary_6bps.csv'>trades_primary_6bps.csv</a></li>
      <li><a href='../../../artifacts/scout_rank32_ema_slope_structure_15m/slope_bucket_summary.csv'>slope_bucket_summary.csv</a></li>
      <li><a href='../../../reading/trendline_alpha_scout/rank32_ema_slope_structure_source_intake.html'>source intake card</a></li>
    </ul>
  </div>
</body>
</html>
"""


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_DIR)

    frames = {asset: build_frame(asset, symbol) for asset, symbol in ASSETS.items()}
    asset_rows = []
    all_trades = []
    for asset, frame in frames.items():
        frame.to_csv(ART_DIR / f"{asset.lower().replace('-usd','')}_frame.csv", index=False)
        for variant in VARIANTS:
            for cost in COSTS:
                trades, no_trade_ratio, eligible_bars = build_trades(frame, asset, variant, cost)
                if variant == PRIMARY_VARIANT and cost == PRIMARY_COST:
                    trades.to_csv(ART_DIR / f"trades_primary_6bps_{asset.lower().replace('-usd','')}.csv", index=False)
                all_trades.append(trades)
                asset_rows.append(
                    summarize_asset(
                        trades,
                        asset=asset,
                        variant=variant,
                        cost_bps=cost,
                        no_trade_ratio=no_trade_ratio,
                        eligible_bars=eligible_bars,
                    )
                )

    non_empty = [df for df in all_trades if not df.empty]
    all_trades_df = pd.concat(non_empty, ignore_index=True) if non_empty else pd.DataFrame()
    if all_trades_df.empty:
        pd.DataFrame().to_csv(ART_DIR / "trades_primary_6bps.csv", index=False)
        slope_buckets = pd.DataFrame(columns=["slope_bucket", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_win_rate"])
    else:
        primary_trades = all_trades_df[
            (all_trades_df["variant"] == PRIMARY_VARIANT) & (all_trades_df["cost_bps_per_side"] == PRIMARY_COST)
        ].copy()
        primary_trades.to_csv(ART_DIR / "trades_primary_6bps.csv", index=False)
        slope_buckets = build_slope_bucket_summary(primary_trades)

    asset_summary = pd.DataFrame(asset_rows)
    overall = summarize_overall(asset_summary)
    verdict, verdict_reason = build_verdict(overall, slope_buckets)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    slope_buckets.to_csv(ART_DIR / "slope_bucket_summary.csv", index=False)
    pd.DataFrame([
        {
            "generated_at_utc": generated_at,
            "candidate_id": "rank32_ema_slope_structure_15m",
            "hard_verdict": verdict,
            "verdict_reason": verdict_reason,
        }
    ]).to_csv(ART_DIR / "meta.csv", index=False)

    html = build_html(overall, asset_summary, slope_buckets, verdict, verdict_reason, generated_at)
    (SITE_DIR / "report.html").write_text(html, encoding="utf-8")
    (READING_DIR / "rank32_ema_slope_structure_clean_replication.html").write_text(html, encoding="utf-8")

    update_reading_report()
    update_todo(verdict, generated_at, overall, slope_buckets)

    print(f"verdict={verdict}")
    if not overall.empty:
        primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
        if not primary.empty:
            print("primary_stats", primary.iloc[0].to_dict())
    if not slope_buckets.empty:
        print("slope_buckets", slope_buckets.to_dict(orient="records"))


if __name__ == "__main__":
    main()
