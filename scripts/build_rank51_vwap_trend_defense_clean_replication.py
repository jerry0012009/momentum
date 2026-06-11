#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import re

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank51_vwap_trend_defense_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank51_vwap_trend_defense_15m"
READING_DIR = ROOT / "reports" / "site" / "reading" / "repo_scout"
TODO_PATH = ROOT / "docs" / "TODO.md"
READING_REPORT = READING_DIR / "report.html"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
VARIANTS = ["touch_only", "touch_plus_reclaim", "touch_reclaim_plus_breadth"]
PRIMARY_VARIANT = "touch_reclaim_plus_breadth"
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0, 20.0]
VWAP_TOL = 0.002
TREND_LOOKBACK = 4
HOLD_BARS = 8
FALSE_LOOKAHEAD = 4


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
    rows: list[str] = []
    for _, row in df.iterrows():
        cells: list[str] = []
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


def load_bars(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_bars(symbol, asset)
    df["typical_price"] = (df["high"] + df["low"] + df["close"]) / 3.0
    df["session_day"] = df["timestamp"].dt.strftime("%Y-%m-%d")
    df["cum_vol"] = df.groupby("session_day")["volume"].cumsum()
    df["cum_tp_vol"] = (df["typical_price"] * df["volume"]).groupby(df["session_day"]).cumsum()
    df["vwap"] = df["cum_tp_vol"] / df["cum_vol"].replace(0, np.nan)
    df["close_above_vwap"] = (df["close"] > df["vwap"]).astype(int)
    df["above_vwap_pct"] = df["close_above_vwap"].rolling(TREND_LOOKBACK, min_periods=TREND_LOOKBACK).mean()
    df["bullish_regime"] = (df["above_vwap_pct"] > 0.5).fillna(False)
    df["current_touch"] = (df["low"] <= df["vwap"] * (1.0 + VWAP_TOL)).fillna(False)
    df["prev_touch"] = df["current_touch"].shift(1).fillna(False)
    df["touched_vwap"] = (df["current_touch"] | df["prev_touch"]).fillna(False)
    df["green_candle"] = (df["close"] > df["open"]).fillna(False)
    df["reclaim"] = (df["touched_vwap"] & df["green_candle"] & (df["close"] > df["vwap"])).fillna(False)
    df["signal_touch_only"] = df["touched_vwap"].astype(int)
    df["signal_touch_plus_reclaim"] = df["reclaim"].astype(int)
    df["signal_touch_reclaim_plus_breadth"] = (df["reclaim"] & df["bullish_regime"]).astype(int)
    return df


def detect_false_retest(frame: pd.DataFrame, signal_idx: int, reclaim_level: float) -> int:
    last = min(len(frame) - 1, signal_idx + FALSE_LOOKAHEAD)
    for j in range(signal_idx + 1, last + 1):
        if float(frame.iloc[j]["close"]) < reclaim_level:
            return 1
    return 0


def build_trades(frame: pd.DataFrame, asset: str, variant: str, cost_bps: float) -> tuple[pd.DataFrame, int]:
    signal_col = f"signal_{variant}"
    cost_rate = float(cost_bps) / 10000.0
    rows: list[dict[str, object]] = []
    last_exit = -1
    signal_events = 0
    for idx in range(1, len(frame) - 2):
        if idx <= last_exit or int(frame.iloc[idx][signal_col]) != 1:
            continue
        signal_events += 1
        entry_idx = idx + 1
        exit_idx = min(len(frame) - 1, entry_idx + HOLD_BARS - 1)
        if entry_idx >= len(frame):
            break
        entry_px = float(frame.iloc[entry_idx]["open"])
        exit_px = float(frame.iloc[exit_idx]["close"])
        reclaim_level = float(frame.iloc[idx]["vwap"])
        gross_ret = exit_px / entry_px - 1.0
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
        rows.append(
            {
                "asset": asset,
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "signal_ts": pd.to_datetime(frame.iloc[idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_ts": pd.to_datetime(frame.iloc[entry_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": pd.to_datetime(frame.iloc[exit_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_price": entry_px,
                "exit_price": exit_px,
                "vwap_level": reclaim_level,
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "hold_bars": int(exit_idx - entry_idx + 1),
                "false_retest_4bars": int(detect_false_retest(frame, idx, reclaim_level)),
                "regime_above_vwap_pct": float(frame.iloc[idx]["above_vwap_pct"]) if pd.notna(frame.iloc[idx]["above_vwap_pct"]) else np.nan,
            }
        )
        last_exit = exit_idx
    return pd.DataFrame(rows), signal_events


def summarize_asset(trades: pd.DataFrame, *, asset: str, variant: str, cost_bps: float, signal_events: int) -> dict[str, object]:
    if trades.empty:
        return {
            "asset": asset,
            "variant": variant,
            "cost_bps_per_side": float(cost_bps),
            "signal_events": int(signal_events),
            "trades": 0,
            "trade_count_retention": np.nan,
            "total_return": 0.0,
            "avg_net_ret": np.nan,
            "win_rate": np.nan,
            "false_retest_4bars_rate": np.nan,
        }
    return {
        "asset": asset,
        "variant": variant,
        "cost_bps_per_side": float(cost_bps),
        "signal_events": int(signal_events),
        "trades": int(len(trades)),
        "trade_count_retention": np.nan,
        "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
        "avg_net_ret": float(trades["net_ret"].mean()),
        "win_rate": float((trades["net_ret"] > 0).mean()),
        "false_retest_4bars_rate": float(trades["false_retest_4bars"].mean()),
    }


def add_trade_retention(asset_df: pd.DataFrame) -> pd.DataFrame:
    out = asset_df.copy()
    for cost in sorted(out["cost_bps_per_side"].unique()):
        base_map = (
            out[(out["variant"] == "touch_only") & (out["cost_bps_per_side"] == cost)]
            .set_index("asset")["trades"]
            .to_dict()
        )
        mask = out["cost_bps_per_side"] == cost
        out.loc[mask, "trade_count_retention"] = out.loc[mask].apply(
            lambda r: (r["trades"] / base_map.get(r["asset"], np.nan)) if base_map.get(r["asset"], 0) else np.nan,
            axis=1,
        )
    return out


def build_time_pockets(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["variant", "bucket", "mean_total_return", "positive_asset_ratio", "mean_trades"])
    df = trades.copy()
    df["entry_ts"] = pd.to_datetime(df["entry_ts"], utc=True)
    q1 = df["entry_ts"].quantile(1 / 3)
    q2 = df["entry_ts"].quantile(2 / 3)

    def bucket(ts: pd.Timestamp) -> str:
        if ts <= q1:
            return "bucket_1"
        if ts <= q2:
            return "bucket_2"
        return "bucket_3"

    df["bucket"] = df["entry_ts"].map(bucket)
    rows: list[dict[str, object]] = []
    grouped = df.groupby(["variant", "bucket", "asset"], dropna=False)
    for (variant, bucket_name, asset), part in grouped:
        rows.append(
            {
                "variant": variant,
                "bucket": bucket_name,
                "asset": asset,
                "total_return": float((1.0 + part["net_ret"]).prod() - 1.0),
                "trades": int(len(part)),
            }
        )
    tmp = pd.DataFrame(rows)
    if tmp.empty:
        return pd.DataFrame(columns=["variant", "bucket", "mean_total_return", "positive_asset_ratio", "mean_trades"])
    return (
        tmp.groupby(["variant", "bucket"], dropna=False)
        .agg(
            mean_total_return=("total_return", "mean"),
            positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
            mean_trades=("trades", "mean"),
        )
        .reset_index()
        .sort_values(["variant", "bucket"])
        .reset_index(drop=True)
    )


def build_verdict(overall: pd.DataFrame) -> tuple[str, str]:
    primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    reclaim = overall[(overall["variant"] == "touch_plus_reclaim") & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    if primary.empty:
        return "park / evidence pool", "主变体没有形成可用结果，不值得继续占默认 fast lane。"
    p = primary.iloc[0]
    r = reclaim.iloc[0] if not reclaim.empty else None
    mean_ret = float(p["mean_total_return"]) if not pd.isna(p["mean_total_return"]) else -1.0
    pos_ratio = float(p["positive_asset_ratio"]) if not pd.isna(p["positive_asset_ratio"]) else 0.0
    mean_trades = float(p["mean_trades"]) if not pd.isna(p["mean_trades"]) else 0.0
    retention = float(p["mean_trade_count_retention"]) if not pd.isna(p["mean_trade_count_retention"]) else 0.0
    false_rate = float(p["mean_false_retest_4bars_rate"]) if not pd.isna(p["mean_false_retest_4bars_rate"]) else 1.0
    reclaim_false = float(r["mean_false_retest_4bars_rate"]) if r is not None and not pd.isna(r["mean_false_retest_4bars_rate"]) else 1.0
    if mean_ret > 0 and pos_ratio >= (2.0 / 3.0) and mean_trades >= 10 and retention >= 0.25 and false_rate <= reclaim_false:
        return "P1 weak candidate / evidence pool", "最小 clean replication 至少说明 breadth gate 不是纯砍样本：成本后为正、跨资产不只剩单腿，且假 retest 没比 reclaim-only 更差。"
    return "park / evidence pool", "最小 clean replication 没把它推到候选池：breadth 版要么成本后仍负，要么主要靠砍样本，或者跨资产/假 retest 指标仍不诚实。"


def update_reading_report() -> None:
    if not READING_REPORT.exists():
        return
    text = READING_REPORT.read_text(encoding="utf-8")
    if "rank51_vwap_trend_defense_clean_replication.html" in text:
        return
    anchor = 'rank51_vwap_trend_defense_source_intake.html">Rank 51 source intake</a>'
    if anchor not in text:
        return
    text = text.replace(anchor, anchor + ' ｜ <a href="rank51_vwap_trend_defense_clean_replication.html">clean replication</a>', 1)
    READING_REPORT.write_text(text, encoding="utf-8")


def update_todo(verdict: str, generated_at: str, overall: pd.DataFrame) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    reclaim = overall[(overall["variant"] == "touch_plus_reclaim") & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    base = overall[(overall["variant"] == "touch_only") & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    if primary.empty:
        stats = "主变体没有形成可用样本。"
    else:
        p = primary.iloc[0]
        parts = [
            f"`{PRIMARY_VARIANT}` 在 `6bps/side` 下跨资产 `mean_total_return≈{pct(p['mean_total_return'])}`",
            f"`positive_asset_ratio≈{pct(p['positive_asset_ratio'])}`",
            f"`mean_trades≈{num(p['mean_trades'],1)}`",
            f"`mean_trade_count_retention≈{pct(p['mean_trade_count_retention'])}`",
            f"`mean_false_retest_4bars_rate≈{pct(p['mean_false_retest_4bars_rate'])}`",
        ]
        if not reclaim.empty:
            r = reclaim.iloc[0]
            parts.append(f"对照 `touch_plus_reclaim≈{pct(r['mean_total_return'])} / false_retest≈{pct(r['mean_false_retest_4bars_rate'])}`")
        if not base.empty:
            b = base.iloc[0]
            parts.append(f"`touch_only≈{pct(b['mean_total_return'])}`")
        stats = "、".join(parts) + "。"

    old_line = "  - 排班含义：当前最新 `Next 3` 顺序应收紧为：**`Run 1 = EMA due-check only` -> `Run 2 = Rank 51 / vwap-trend-defense source intake（仅当 EMA 仍 waiting_not_due）` -> `Run 3 = Rank 35b / tiny-live plumbing（若 Rank 51 也不合格）`**。"
    new_line = f"  - 排班含义：当前最新 `Next 3` 顺序应收紧为：**`Run 1 = EMA due-check only` -> `Run 2 = fresh paper/repo intake（先从 RECENT_PAPER_SEEDS / quant_digests / validated shortlist 里认领 1 条新的 15m crypto source）` -> `Run 3 = Rank 35b / tiny-live plumbing（仅当 fresh intake 也真实 exhausted）`**。"
    if old_line in text:
        text = text.replace(old_line, old_line + f"\n- **最新补充（{generated_at}）**：这轮已把 `Rank 51 / vwap-trend-defense / session VWAP reclaim + breadth gate` 的唯一那手 **最小 clean replication** 跑完：固定复用 `BTC/ETH/SOL 120d 15m` cache，直接照 repo 的核心骨架只比较 `touch_only`、`touch_plus_reclaim`、`touch_reclaim_plus_breadth` 三臂，并统一冻结到 `UTC session VWAP reset + next-bar open + no-overlap + hold 8 bars`。{stats}\n  - 当前更诚实的 hard verdict：**`Rank 51 / vwap-trend-defense / session VWAP reclaim + breadth gate = {verdict}`**。直白地说，这条线已经不该再停在 source-intake queue：若后续继续认领，默认只能按这个 verdict 走，而不是继续磨 intake wording。\n  - reader-facing 落点：`reports/site/factors/scout_rank51_vwap_trend_defense_15m/report.html`、`reports/site/reading/repo_scout/rank51_vwap_trend_defense_clean_replication.html`；artifact：`reports/artifacts/scout_rank51_vwap_trend_defense_15m/overall_summary.csv`。\n" + new_line, 1)
    else:
        pattern = re.compile(r"- \*\*最新补充（2026-03-18 08:44 UTC）\*\*[\s\S]*?admit_to_clean_replication_queue`\*\*。")
        repl = r"\g<0>\n- **最新补充（" + generated_at + r"）**：这轮已完成 `Rank 51` 的最小 clean replication。"  # emergency fallback
        text = pattern.sub(repl, text, count=1)
        text = text.replace(old_line, new_line)

    TODO_PATH.write_text(text, encoding="utf-8")


def build_html(overall: pd.DataFrame, asset_summary: pd.DataFrame, pockets: pd.DataFrame, verdict: str, verdict_reason: str, generated_at: str) -> str:
    primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    headline = "主变体没有形成可用样本。"
    if not primary.empty:
        row = primary.iloc[0]
        headline = (
            f"主变体 {PRIMARY_VARIANT} 在 {int(PRIMARY_COST)}bps/side 下：跨资产 mean_total_return≈{pct(row['mean_total_return'])}、"
            f"positive_asset_ratio≈{pct(row['positive_asset_ratio'])}、mean_trades≈{num(row['mean_trades'],1)}、"
            f"mean_trade_count_retention≈{pct(row['mean_trade_count_retention'])}、mean_false_retest_4bars_rate≈{pct(row['mean_false_retest_4bars_rate'])}。"
        )
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 51 · vwap-trend-defense clean replication</title>
  <style>
    body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width:1100px; margin:40px auto; padding:0 18px; line-height:1.7; color:#111827; background:#f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }}
    .muted {{ color:#6b7280; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    ul {{ padding-left:20px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    a {{ color:#2563eb; text-decoration:none; }}
  </style>
</head>
<body>
  <p><a href='../../reading/repo_scout/report.html'>← 返回 Repo Scout</a></p>
  <h1>Rank 51 · vwap-trend-defense / session VWAP reclaim + breadth gate</h1>
  <p class='muted'>生成时间：{escape(generated_at)} ｜ 类型：最小 clean replication ｜ 角色：Scout Seat 的 repo-based 15m crypto fast verdict</p>

  <div class='card'>
    <h2>这轮只回答什么</h2>
    <ul>
      <li>固定复用 <code>BTC/ETH/SOL 120d 15m</code> cache，不追最新 bar。</li>
      <li>直接照 repo 核心骨架，只比较三臂：<code>touch_only</code>、<code>touch_plus_reclaim</code>、<code>touch_reclaim_plus_breadth</code>。</li>
      <li>执行口径固定：<code>UTC session VWAP reset -> signal bar close -> next-bar open -> no-overlap -> hold {HOLD_BARS} bars</code>。</li>
      <li>先回答四个便宜问题：<code>post_cost_return</code>、<code>false_retest_rate</code>、<code>trade_count_retention</code>、<code>positive_asset_ratio</code>。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>clean-room 规则</h2>
    <ul>
      <li><b>touch_only：</b>当前或前一根 low 触到 <code>session VWAP * (1 + 0.2%)</code> 就放行，不要求 reclaim，不要求 breadth。</li>
      <li><b>touch_plus_reclaim：</b>在上一臂基础上，必须是阳线且收盘重新站回 VWAP 上方。</li>
      <li><b>touch_reclaim_plus_breadth：</b>在 reclaim 基础上，再要求最近 <code>{TREND_LOOKBACK}</code> 根里超过一半 close 在 VWAP 上方。</li>
      <li><b>false retest：</b>入场后 {FALSE_LOOKAHEAD} 根内，只要任一收盘重新跌回 signal-bar 的 VWAP 下方，就记为假 retest。</li>
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
    {render_table(overall[["variant","cost_bps_per_side","mean_total_return","positive_asset_ratio","mean_trades","mean_trade_count_retention","mean_false_retest_4bars_rate","mean_win_rate"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_trade_count_retention","mean_false_retest_4bars_rate","mean_win_rate"}, digits_cols={"cost_bps_per_side":0,"mean_trades":1})}
  </div>

  <div class='card'>
    <h2>6bps 分资产摘要</h2>
    {render_table(asset_summary[asset_summary["cost_bps_per_side"] == PRIMARY_COST][["asset","variant","trades","trade_count_retention","total_return","false_retest_4bars_rate","win_rate"]], percent_cols={"trade_count_retention","total_return","false_retest_4bars_rate","win_rate"}, digits_cols={"trades":0})}
  </div>

  <div class='card'>
    <h2>time-pocket honesty</h2>
    {render_table(pockets, percent_cols={"mean_total_return","positive_asset_ratio"}, digits_cols={"mean_trades":1})}
  </div>

  <div class='card'>
    <h2>artifact</h2>
    <ul>
      <li><a href='../../../artifacts/scout_rank51_vwap_trend_defense_15m/overall_summary.csv'>overall_summary.csv</a></li>
      <li><a href='../../../artifacts/scout_rank51_vwap_trend_defense_15m/asset_summary.csv'>asset_summary.csv</a></li>
      <li><a href='../../../artifacts/scout_rank51_vwap_trend_defense_15m/trades_primary_6bps.csv'>trades_primary_6bps.csv</a></li>
      <li><a href='../../reading/repo_scout/rank51_vwap_trend_defense_source_intake.html'>source intake card</a></li>
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
    asset_rows: list[dict[str, object]] = []
    trade_frames: list[pd.DataFrame] = []

    for asset, frame in frames.items():
        frame.to_csv(ART_DIR / f"{asset.lower().replace('-usd','')}_frame.csv", index=False)
        for variant in VARIANTS:
            for cost in COSTS:
                trades, signal_events = build_trades(frame, asset, variant, cost)
                if not trades.empty:
                    trade_frames.append(trades)
                if variant == PRIMARY_VARIANT and cost == PRIMARY_COST:
                    trades.to_csv(ART_DIR / f"trades_primary_6bps_{asset.lower().replace('-usd','')}.csv", index=False)
                asset_rows.append(summarize_asset(trades, asset=asset, variant=variant, cost_bps=cost, signal_events=signal_events))

    all_trades = pd.concat([df for df in trade_frames if not df.empty], ignore_index=True) if trade_frames else pd.DataFrame()
    if all_trades.empty:
        pd.DataFrame().to_csv(ART_DIR / "trades_primary_6bps.csv", index=False)
    else:
        all_trades[(all_trades["variant"] == PRIMARY_VARIANT) & (all_trades["cost_bps_per_side"] == PRIMARY_COST)].to_csv(ART_DIR / "trades_primary_6bps.csv", index=False)
        all_trades.to_csv(ART_DIR / "trade_log.csv", index=False)

    asset_summary = add_trade_retention(pd.DataFrame(asset_rows)).sort_values(["variant", "cost_bps_per_side", "asset"]).reset_index(drop=True)
    overall = (
        asset_summary.groupby(["variant", "cost_bps_per_side"], dropna=False)
        .agg(
            mean_total_return=("total_return", "mean"),
            positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
            mean_trades=("trades", "mean"),
            mean_trade_count_retention=("trade_count_retention", "mean"),
            mean_false_retest_4bars_rate=("false_retest_4bars_rate", "mean"),
            mean_win_rate=("win_rate", "mean"),
        )
        .reset_index()
        .sort_values(["variant", "cost_bps_per_side"])
        .reset_index(drop=True)
    )
    pockets = build_time_pockets(all_trades)
    verdict, verdict_reason = build_verdict(overall)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    pockets.to_csv(ART_DIR / "time_pocket_summary.csv", index=False)
    pd.DataFrame([
        {
            "generated_at_utc": generated_at,
            "candidate_id": "rank51_vwap_trend_defense_15m",
            "hard_verdict": verdict,
            "verdict_reason": verdict_reason,
        }
    ]).to_csv(ART_DIR / "meta.csv", index=False)

    html = build_html(overall, asset_summary, pockets, verdict, verdict_reason, generated_at)
    (SITE_DIR / "report.html").write_text(html, encoding="utf-8")
    (READING_DIR / "rank51_vwap_trend_defense_clean_replication.html").write_text(html, encoding="utf-8")

    update_reading_report()
    update_todo(verdict, generated_at, overall)

    print(f"verdict={verdict}")
    primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    if not primary.empty:
        print(primary.iloc[0].to_dict())


if __name__ == "__main__":
    main()
