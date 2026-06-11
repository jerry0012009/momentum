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
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank40_ema_pullback_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank40_ema_pullback_15m"
TODO_PATH = ROOT / "docs" / "TODO.md"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
VARIANTS = [
    ("ema20_100_200", 20, 100, 200),
    ("ema33_165_365", 33, 165, 365),
    ("ema40_200_440", 40, 200, 440),
]
PRIMARY_VARIANT = "ema33_165_365"
COSTS = [6.0, 10.0, 15.0, 20.0]
PRIMARY_COST = 6.0
RISK_LIMIT_LOW = 0.008
RISK_LIMIT_HIGH = 0.02
TP_RATIO = 2.06
MAX_HOLD_BARS = 24
TIME_BUCKETS = 3


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


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


def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def load_cached_bars(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def build_variant_frame(asset: str, symbol: str, fast: int, limit: int, trend: int) -> pd.DataFrame:
    df = load_cached_bars(symbol, asset)
    df["ema_fast"] = ema(df["close"], fast)
    df["ema_limit"] = ema(df["close"], limit)
    df["ema_trend"] = ema(df["close"], trend)
    return df


def generate_signals(frame: pd.DataFrame) -> pd.DataFrame:
    long_active = False
    short_active = False
    long_pull_low = math.nan
    long_pull_close_min = math.nan
    short_pull_high = math.nan
    short_pull_close_max = math.nan

    rows: list[dict[str, object]] = []
    for i in range(1, len(frame)):
        prev = frame.iloc[i - 1]
        row = frame.iloc[i]
        prev_close = float(prev["close"])
        close = float(row["close"])
        prev_fast = float(prev["ema_fast"])
        fast = float(row["ema_fast"])
        limit = float(row["ema_limit"])
        trend = float(row["ema_trend"])
        low = float(row["low"])
        high = float(row["high"])

        cross_above_fast = prev_close <= prev_fast and close > fast
        cross_below_fast = prev_close >= prev_fast and close < fast
        trend_up = fast > trend
        trend_down = fast < trend

        if cross_below_fast and trend_up:
            long_active = True
            long_pull_low = low
            long_pull_close_min = close
        elif long_active:
            long_pull_low = min(long_pull_low, low)
            long_pull_close_min = min(long_pull_close_min, close)
            if not trend_up:
                long_active = False

        if cross_above_fast and trend_down:
            short_active = True
            short_pull_high = high
            short_pull_close_max = close
        elif short_active:
            short_pull_high = max(short_pull_high, high)
            short_pull_close_max = max(short_pull_close_max, close)
            if not trend_down:
                short_active = False

        if cross_above_fast and long_active:
            stop_price = float(long_pull_low)
            allow = stop_price > limit
            rows.append({
                "signal_idx": i,
                "signal_ts": pd.to_datetime(row["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "direction": 1,
                "direction_label": "long",
                "stop_price": stop_price,
                "pullback_extreme": stop_price,
                "pullback_close_extreme": float(long_pull_close_min),
                "limit_price": limit,
                "trend_price": trend,
                "allow": int(allow),
                "rule_gate": "stop_above_limit_ema" if allow else "deep_pullback_fail",
            })
            long_active = False
            long_pull_low = math.nan
            long_pull_close_min = math.nan

        if cross_below_fast and short_active:
            stop_price = float(short_pull_high)
            allow = stop_price < limit
            rows.append({
                "signal_idx": i,
                "signal_ts": pd.to_datetime(row["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "direction": -1,
                "direction_label": "short",
                "stop_price": stop_price,
                "pullback_extreme": stop_price,
                "pullback_close_extreme": float(short_pull_close_max),
                "limit_price": limit,
                "trend_price": trend,
                "allow": int(allow),
                "rule_gate": "stop_below_limit_ema" if allow else "deep_pullback_fail",
            })
            short_active = False
            short_pull_high = math.nan
            short_pull_close_max = math.nan

    return pd.DataFrame(rows)


def backtest_variant(frame: pd.DataFrame, signals: pd.DataFrame, asset: str, variant: str, cost_bps: float) -> tuple[pd.DataFrame, float, int]:
    rows: list[dict[str, object]] = []
    last_exit_idx = -1
    eligible_signals = signals[signals["allow"] == 1].copy() if not signals.empty else pd.DataFrame()
    signals_seen = int(len(eligible_signals))
    cost_rate = float(cost_bps) / 10000.0

    for _, sig in eligible_signals.iterrows():
        sig_idx = int(sig["signal_idx"])
        if sig_idx <= last_exit_idx:
            continue
        entry_idx = sig_idx + 1
        if entry_idx >= len(frame):
            continue
        direction = int(sig["direction"])
        entry_price = float(frame.iloc[entry_idx]["open"])
        stop_price = float(sig["stop_price"])
        risk = (entry_price - stop_price) / entry_price if direction > 0 else (stop_price - entry_price) / entry_price
        if not math.isfinite(risk) or risk <= 0 or risk < RISK_LIMIT_LOW or risk > RISK_LIMIT_HIGH:
            continue
        target_price = entry_price * (1 + TP_RATIO * risk) if direction > 0 else entry_price * (1 - TP_RATIO * risk)
        exit_idx = min(entry_idx + MAX_HOLD_BARS - 1, len(frame) - 1)
        exit_reason = "time_exit"
        exit_price = float(frame.iloc[exit_idx]["close"])
        for j in range(entry_idx, min(entry_idx + MAX_HOLD_BARS, len(frame))):
            bar = frame.iloc[j]
            high = float(bar["high"])
            low = float(bar["low"])
            if direction > 0:
                if low <= stop_price:
                    exit_idx = j
                    exit_price = stop_price
                    exit_reason = "stop"
                    break
                if high >= target_price:
                    exit_idx = j
                    exit_price = target_price
                    exit_reason = "target"
                    break
            else:
                if high >= stop_price:
                    exit_idx = j
                    exit_price = stop_price
                    exit_reason = "stop"
                    break
                if low <= target_price:
                    exit_idx = j
                    exit_price = target_price
                    exit_reason = "target"
                    break
        gross_ret = (exit_price / entry_price - 1.0) * direction
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
        rows.append({
            "asset": asset,
            "variant": variant,
            "cost_bps_per_side": float(cost_bps),
            "signal_ts": sig["signal_ts"],
            "entry_ts": pd.to_datetime(frame.iloc[entry_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "exit_ts": pd.to_datetime(frame.iloc[exit_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "direction": sig["direction_label"],
            "entry_price": entry_price,
            "stop_price": stop_price,
            "target_price": target_price,
            "exit_price": exit_price,
            "risk": risk,
            "gross_ret": gross_ret,
            "net_ret": net_ret,
            "hold_bars": int(exit_idx - entry_idx + 1),
            "exit_reason": exit_reason,
        })
        last_exit_idx = exit_idx

    no_trade_ratio = 1.0 if signals_seen == 0 else max(0.0, 1.0 - (len(rows) / signals_seen))
    return pd.DataFrame(rows), no_trade_ratio, signals_seen


def summarize_asset(trades: pd.DataFrame, asset: str, variant: str, cost: float, no_trade_ratio: float, signals_seen: int) -> dict[str, object]:
    if trades.empty:
        return {
            "asset": asset,
            "variant": variant,
            "cost_bps_per_side": float(cost),
            "signals_seen": int(signals_seen),
            "trades": 0,
            "total_return": 0.0,
            "avg_net_ret": np.nan,
            "win_rate": np.nan,
            "stop_share": np.nan,
            "target_share": np.nan,
            "time_exit_share": np.nan,
            "avg_hold_bars": np.nan,
            "no_trade_ratio": float(no_trade_ratio),
            "long_share": np.nan,
            "short_share": np.nan,
        }
    return {
        "asset": asset,
        "variant": variant,
        "cost_bps_per_side": float(cost),
        "signals_seen": int(signals_seen),
        "trades": int(len(trades)),
        "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
        "avg_net_ret": float(trades["net_ret"].mean()),
        "win_rate": float((trades["net_ret"] > 0).mean()),
        "stop_share": float((trades["exit_reason"] == "stop").mean()),
        "target_share": float((trades["exit_reason"] == "target").mean()),
        "time_exit_share": float((trades["exit_reason"] == "time_exit").mean()),
        "avg_hold_bars": float(trades["hold_bars"].mean()),
        "no_trade_ratio": float(no_trade_ratio),
        "long_share": float((trades["direction"] == "long").mean()),
        "short_share": float((trades["direction"] == "short").mean()),
    }


def summarize_overall(asset_summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (variant, cost), grp in asset_summary.groupby(["variant", "cost_bps_per_side"], sort=False):
        rows.append({
            "variant": variant,
            "cost_bps_per_side": float(cost),
            "mean_total_return": float(grp["total_return"].mean()),
            "positive_asset_ratio": float((grp["total_return"] > 0).mean()),
            "mean_trades": float(grp["trades"].mean()),
            "mean_signals_seen": float(grp["signals_seen"].mean()),
            "mean_no_trade_ratio": float(grp["no_trade_ratio"].mean()),
            "mean_win_rate": float(grp["win_rate"].mean()) if grp["win_rate"].notna().any() else np.nan,
            "mean_stop_share": float(grp["stop_share"].mean()) if grp["stop_share"].notna().any() else np.nan,
            "mean_target_share": float(grp["target_share"].mean()) if grp["target_share"].notna().any() else np.nan,
            "mean_time_exit_share": float(grp["time_exit_share"].mean()) if grp["time_exit_share"].notna().any() else np.nan,
        })
    return pd.DataFrame(rows)


def build_time_buckets(primary_trades: pd.DataFrame) -> pd.DataFrame:
    if primary_trades.empty or len(primary_trades) < TIME_BUCKETS:
        return pd.DataFrame(columns=["time_bucket", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_win_rate"])
    df = primary_trades.copy().sort_values("entry_ts").reset_index(drop=True)
    df["time_bucket"] = pd.qcut(np.arange(len(df)), q=TIME_BUCKETS, labels=[f"bucket_{i+1}" for i in range(TIME_BUCKETS)])
    rows = []
    for bucket, grp in df.groupby("time_bucket", sort=False):
        asset_returns = grp.groupby("asset")["net_ret"].apply(lambda s: float((1.0 + s).prod() - 1.0))
        rows.append({
            "time_bucket": str(bucket),
            "mean_total_return": float(asset_returns.mean()),
            "positive_asset_ratio": float((asset_returns > 0).mean()),
            "mean_trades": float(grp.groupby("asset").size().mean()),
            "mean_win_rate": float(grp.groupby("asset")["net_ret"].apply(lambda s: float((s > 0).mean())).mean()),
        })
    return pd.DataFrame(rows)


def decide_verdict(overall: pd.DataFrame, time_buckets: pd.DataFrame) -> tuple[str, str]:
    row = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    if row.empty:
        return "park / evidence pool", "主变体没有形成足够样本，不能诚实升格。"
    r = row.iloc[0]
    positive_buckets = int((time_buckets["mean_total_return"] > 0).sum()) if not time_buckets.empty else 0
    if float(r["mean_total_return"]) > 0 and float(r["positive_asset_ratio"]) >= (2.0 / 3.0) and float(r["mean_trades"]) >= 10 and float(r["mean_no_trade_ratio"]) <= 0.6 and positive_buckets >= 2:
        return "P1 weak candidate / evidence pool", "最小 clean replication 至少没直接塌掉：成本后仍保留正 pocket，跨资产不是单腿存活，time-pocket 也不只靠单一热像素。"
    return "park / evidence pool", "最小 clean replication 没把这条 pullback 模板推成可继续给预算的候选：成本后主证据仍偏弱，且 time-pocket honesty 也没有一起站住。"


def update_todo(verdict: str, generated_at: str, overall: pd.DataFrame, time_buckets: pd.DataFrame) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    row = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    stats = (
        f"主变体 `{PRIMARY_VARIANT}` 在 `6bps/side` 下跨资产 `mean_total_return≈{pct(row['mean_total_return'])}`、"
        f"`positive_asset_ratio≈{pct(row['positive_asset_ratio'])}`、`mean_trades≈{num(row['mean_trades'],1)}`、"
        f"`mean_no_trade_ratio≈{pct(row['mean_no_trade_ratio'])}`。"
    )
    bucket_parts = []
    for _, b in time_buckets.iterrows():
        bucket_parts.append(f"{b['time_bucket']}≈{pct(b['mean_total_return'])} / {pct(b['positive_asset_ratio'])}")
    time_note = "time-pocket honesty：" + "；".join(bucket_parts) + "。" if bucket_parts else "当前样本不足以可靠拆成 3 桶，这本身也不支持升格。"

    old_rank_block = "40. `Rank 40 EMA pullback / three-EMA trend continuation`（open-source repo template `EMA-Pullback-Strategy`）→ **`admit_to_clean_replication_queue`**\n    - 这条线是本轮在外部 fresh repo source 里边际价值最高的一条：相比同轮的 `Keltner Channel Pullback`，它不只讲回抽方向，还至少给了 `pullback swing stop + 2R target` 这一层最小交易单元；相比 `VWAP deviation band + volatility filter`，它的规则更短、session 依赖更弱，更适合当前 fast-lane 先做 yes/no clean replication。\n    - source 可先冻结成最小读法：`trade on = 趋势仍偏多/偏空，价格先走出顺势方向、再回踩短 EMA 但不深穿过滤 EMA，并在形成更高低点/更低高点后重新站回短 EMA；trade off = 趋势过滤失效、回踩过深、或重新站回短 EMA 这件事没有发生`。\n    - 当前 source 描述未见一眼可判死刑的 `lookahead / repaint / data leakage`，而且比 `Rank 39` 更接近当前 desk 所需的 execution freeze：至少已把 `回调 swing stop` 与 `2R take-profit` 讲清。\n    - **最新补充（2026-03-17 18:06 UTC）**：这轮 intake-stage hard verdict 是 **`admit_to_clean_replication_queue`**，不是直接升到 `paper candidate`。更直白地说：它只是当前 fresh source 里最值得给下一手 `BTC/ETH/SOL 120d 15m` 最小 clean replication 预算的一条。若下一轮继续认领它，默认只允许做 `next-bar open + no-overlap + pullback swing stop + 2R target` 的最小 clean-room 检查；若结果不干净，应快速压回 `park / evidence pool`。\n    - 网页落点：`reports/site/reading/quant_digests/2026-03-17_1806_rank40-ema-pullback-intake.html`。"
    new_rank_block = (
        f"40. `Rank 40 EMA pullback / three-EMA trend continuation`（open-source repo template `EMA-Pullback-Strategy`）→ **`{verdict}`**\n"
        "    - 已完成 `fresh source intake -> 最小 clean replication`，固定复用 `BTC/ETH/SOL 120d 15m` cache；只比较 `20/100/200`、`33/165/365`、`40/200/440` 三组 EMA 邻近参数，不追新 bar，也不扩成完整 stability pack。\n"
        "    - 冻结后的 clean-room 规则：`trade on = EMA fast 与 EMA trend 同向，价格先回抽穿越 EMA fast，再在回抽极值仍未深穿 EMA limit 的前提下重新站回 EMA fast（short 镜像）`；执行口径固定为 `signal bar close -> next-bar open -> no-overlap`，并保留 `pullback swing stop + 2.06R target`。\n"
        f"    - 当前最诚实的主证据：{stats}\n"
        f"    - {time_note}\n"
        f"    - **最新补充（{generated_at}）**：这轮最小 clean replication 的 hard verdict 是 **`{verdict}`**。更直白地说：`Rank 40` 已不再只是 `admit_to_clean_replication_queue`；若后续继续认领，默认只能按这个 verdict 走——`P1` 才配拿那唯一允许的一次便宜诚实检查，`park` 则应回到 evidence pool，而不是继续停在 intake 文案上。\n"
        "    - 网页落点：`reports/site/factors/scout_rank40_ema_pullback_15m/report.html`、`reports/site/reading/quant_digests/2026-03-17_1806_rank40-ema-pullback-intake.html`。"
    )
    if old_rank_block in text:
        text = text.replace(old_rank_block, new_rank_block, 1)

    old_note = "> **最新补充（2026-03-17 18:06 UTC）**：本轮继续按 `Run 2 / Scout Fast Lane` 从新的 repo source 里比较了 `EMA Pullback Strategy`、`Keltner Channel Pullback Strategy`、`VWAP deviation band + volatility filter` 三条候选。当前边际价值最高的是新的 `Rank 40 / EMA pullback / three-EMA trend continuation`：它虽然还不是 `paper candidate`，但比 `Rank 39` 更接近 clean-room，因为至少把 `顺势回调 -> swing stop -> 2R target` 讲清了一层。因此这轮 authoritative hard verdict 不是继续 park，而是把 `Rank 40` 记为 **`admit_to_clean_replication_queue`**；更直白地说，若下一轮仍留在 `Run 2`，默认应先给它那 **1 次最小 clean replication**，而不是继续回头磨 `Rank 39` 或补新的 tiny-live 近义文档。若这一步 clean replication 结果不干净，再快速压回 `park / evidence pool`。"
    new_note = old_note + "\n>\n" + (
        f"> **最新补充（{generated_at}）**：本轮已按上一条指令把 `Rank 40` 的那 **1 次最小 clean replication** 如实跑完：固定 `BTC/ETH/SOL 120d 15m`、`next-bar open`、`no-overlap`、`pullback swing stop + 2.06R target`，并只比较 3 组 EMA 邻近参数。当前最诚实的主读法是 **`{verdict}`**，不是继续停在 `admit_to_clean_replication_queue`：{stats} {time_note} 因此若下一轮 `EMA` 仍是 `waiting_not_due`，默认应先比较是否还有新的合格 `paper / repo source` 可做 fresh intake；若这一轮确实拿不到合格 source，再诚实回退到 `Run 3 / tiny-live plumbing`。"
    )
    if old_note in text:
        text = text.replace(old_note, new_note, 1)

    TODO_PATH.write_text(text, encoding="utf-8")


def build_spec() -> pd.DataFrame:
    rows = [
        {"section": "candidate", "item": "candidate_id", "value": "rank40_ema_pullback_15m", "note": "外部 repo source 的最小 clean replication。"},
        {"section": "scope", "item": "assets", "value": "BTC-USD / ETH-USD / SOL-USD | Binance 120d cache | 15m", "note": "固定复用现有 cache，不追新 bar。"},
        {"section": "execution", "item": "entry_exit", "value": "signal bar close -> next-bar open -> no-overlap -> swing stop / 2.06R target / max 24 bars", "note": "stop 与 target 同 bar 触发时按 stop 优先。"},
        {"section": "risk_band", "item": "source_defaults", "value": "risk between 0.8% and 2.0%", "note": "保留 source 默认风险带，不做 position sizing。"},
        {"section": "params", "item": "ema_sets", "value": "20/100/200 ; 33/165/365 ; 40/200/440", "note": "只做极小邻近参数组。"},
    ]
    return pd.DataFrame(rows)


def write_html(overall: pd.DataFrame, asset_summary: pd.DataFrame, time_buckets: pd.DataFrame, verdict: str, reason: str, generated_at: str) -> None:
    ensure_dir(SITE_DIR)
    row = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    headline = (
        f"主变体 {PRIMARY_VARIANT} 在 6bps/side 下：跨资产 mean_total_return≈{pct(row['mean_total_return'])}、"
        f"positive_asset_ratio≈{pct(row['positive_asset_ratio'])}、mean_trades≈{num(row['mean_trades'],1)}、mean_no_trade_ratio≈{pct(row['mean_no_trade_ratio'])}。"
    )
    html = f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 40 · EMA pullback clean replication</title>
  <style>
    body {{ font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width: 1100px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background: #f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }}
    .muted {{ color:#6b7280; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    a {{ color:#2563eb; text-decoration:none; }}
  </style>
</head>
<body>
  <p><a href='../../plans/momentum_todo.html'>← 返回 TODO / desk board</a></p>
  <h1>Rank 40 · EMA pullback / three-EMA trend continuation</h1>
  <p class='muted'>生成时间：{escape(generated_at)} ｜ 类型：最小 clean replication ｜ 角色：Scout Seat / repo-based 15m crypto fast verdict</p>

  <div class='card'>
    <h2>这轮只回答什么</h2>
    <ul>
      <li>固定复用 <code>BTC/ETH/SOL 120d 15m</code> cache，不追新 bar。</li>
      <li>只比较三组 EMA 邻近参数：<code>20/100/200</code>、<code>33/165/365</code>、<code>40/200/440</code>。</li>
      <li>执行口径固定：<code>signal bar close -&gt; next-bar open -&gt; no-overlap</code>。</li>
      <li>风险管理保留 source 原意：<code>pullback swing stop + 2.06R target</code>，并保留 <code>0.8%~2.0%</code> 风险带。</li>
      <li>先只回答 <code>post-cost return / positive_asset_ratio / trade_count / time-pocket honesty</code>。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>clean-room 规则</h2>
    <ul>
      <li><b>long：</b>EMA fast 与 EMA trend 同向偏多，价格先回抽跌回 EMA fast 下方，再在回抽极值仍未深穿 EMA limit 的前提下重新站回 EMA fast；下一根 bar 开盘做多。</li>
      <li><b>short：</b>上面逻辑镜像。</li>
      <li><b>trade off：</b>回抽深穿 EMA limit、趋势过滤失效、风险带不在 <code>0.8%~2.0%</code>、或已有仓位未结束。</li>
      <li><b>exit：</b>优先看 <code>swing stop</code> 与 <code>2.06R target</code>；若 24 根 15m bar 内都没触发，则按时间退出。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>hard verdict</h2>
    <p><span class='pill'>{escape(verdict)}</span></p>
    <p><b>{escape(headline)}</b></p>
    <p class='muted'>{escape(reason)}</p>
  </div>

  <div class='card'>
    <h2>跨资产总表</h2>
    {render_table(overall[["variant","cost_bps_per_side","mean_total_return","positive_asset_ratio","mean_trades","mean_signals_seen","mean_no_trade_ratio","mean_win_rate","mean_stop_share","mean_target_share","mean_time_exit_share"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_no_trade_ratio","mean_win_rate","mean_stop_share","mean_target_share","mean_time_exit_share"}, digits_cols={"mean_trades":1,"mean_signals_seen":1})}
  </div>

  <div class='card'>
    <h2>分资产摘要</h2>
    {render_table(asset_summary[["asset","variant","cost_bps_per_side","signals_seen","trades","total_return","win_rate","no_trade_ratio","stop_share","target_share","time_exit_share","long_share","short_share"]], percent_cols={"total_return","win_rate","no_trade_ratio","stop_share","target_share","time_exit_share","long_share","short_share"}, digits_cols={"signals_seen":0,"trades":0})}
  </div>

  <div class='card'>
    <h2>time-pocket honesty（主变体 6bps）</h2>
    {render_table(time_buckets[["time_bucket","mean_total_return","positive_asset_ratio","mean_trades","mean_win_rate"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_win_rate"}, digits_cols={"mean_trades":1})}
  </div>
</body>
</html>
"""
    (SITE_DIR / "report.html").write_text(html, encoding="utf-8")


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    signal_frames: dict[tuple[str, str], pd.DataFrame] = {}
    asset_rows: list[dict[str, object]] = []
    all_trades: list[pd.DataFrame] = []

    for asset, symbol in ASSETS.items():
        for variant, fast, limit, trend in VARIANTS:
            frame = build_variant_frame(asset, symbol, fast, limit, trend)
            signals = generate_signals(frame)
            signal_frames[(asset, variant)] = signals
            for cost in COSTS:
                trades, no_trade_ratio, signals_seen = backtest_variant(frame, signals, asset, variant, cost)
                asset_rows.append(summarize_asset(trades, asset, variant, cost, no_trade_ratio, signals_seen))
                if not trades.empty:
                    all_trades.append(trades)

    asset_summary = pd.DataFrame(asset_rows).sort_values(["variant", "cost_bps_per_side", "asset"]).reset_index(drop=True)
    overall = summarize_overall(asset_summary).sort_values(["variant", "cost_bps_per_side"]).reset_index(drop=True)
    all_trades_df = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    primary_trades = all_trades_df[(all_trades_df["variant"] == PRIMARY_VARIANT) & (all_trades_df["cost_bps_per_side"] == PRIMARY_COST)].copy() if not all_trades_df.empty else pd.DataFrame()
    time_buckets = build_time_buckets(primary_trades)
    verdict, reason = decide_verdict(overall, time_buckets)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    spec_df = build_spec()
    spec_df.to_csv(ART_DIR / "clean_room_spec.csv", index=False)
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    time_buckets.to_csv(ART_DIR / "time_bucket_summary.csv", index=False)
    if not all_trades_df.empty:
        all_trades_df.sort_values(["variant", "cost_bps_per_side", "asset", "entry_ts"]).to_csv(ART_DIR / "all_trades.csv", index=False)
    if not primary_trades.empty:
        primary_trades.sort_values(["asset", "entry_ts"]).to_csv(ART_DIR / "trades_primary_6bps.csv", index=False)

    write_html(overall, asset_summary, time_buckets, verdict, reason, generated_at)
    update_todo(verdict, generated_at, overall, time_buckets)
    print(f"rank40 clean replication done: {verdict}")


if __name__ == "__main__":
    main()
