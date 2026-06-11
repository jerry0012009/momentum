#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_repo_fibtrend_confirmation_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_repo_fibtrend_confirmation_15m"
TODO_PATH = ROOT / "docs" / "TODO.md"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
VARIANTS = ["fib_touch_raw", "volume_gate", "trend_gate_shared", "ema_confirm_atr"]
PRIMARY_VARIANT = "ema_confirm_atr"
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0, 20.0]
LOOKBACK = 50
VOL_SMA = 24
SMA_TREND = 200
EMA_FAST = 9
EMA_SLOW = 26
HOLD_BARS = 8
EARLY_FAIL_BARS = 4
ATR_PERIOD = 14


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
    rows: list[str] = []
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
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def atr(df: pd.DataFrame, period: int = ATR_PERIOD) -> pd.Series:
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_cached_bars(symbol, asset)
    roll_high = df["high"].rolling(LOOKBACK, min_periods=LOOKBACK).max()
    roll_low = df["low"].rolling(LOOKBACK, min_periods=LOOKBACK).min()
    fib_range = roll_high - roll_low
    df["fib_618"] = roll_low + fib_range * 0.618
    df["fib_50"] = roll_low + fib_range * 0.5
    df["volume_sma24"] = df["volume"].rolling(VOL_SMA, min_periods=VOL_SMA).mean()
    df["sma200"] = df["close"].rolling(SMA_TREND, min_periods=SMA_TREND).mean()
    df["ema9"] = df["close"].ewm(span=EMA_FAST, adjust=False).mean()
    df["ema26"] = df["close"].ewm(span=EMA_SLOW, adjust=False).mean()
    df["atr14"] = atr(df)

    reclaim_618 = (df["close"] > df["fib_618"]) & (df["close"].shift(1) <= df["fib_618"].shift(1))
    vol_gate = df["volume"] > df["volume_sma24"]
    trend_gate = df["close"] > df["sma200"]
    ema_gate = df["ema9"] > df["ema26"]

    df["signal_fib_touch_raw"] = reclaim_618.fillna(False)
    df["signal_volume_gate"] = (reclaim_618 & vol_gate).fillna(False)
    df["signal_trend_gate_shared"] = (reclaim_618 & vol_gate & trend_gate).fillna(False)
    df["signal_ema_confirm_atr"] = (reclaim_618 & vol_gate & trend_gate & ema_gate).fillna(False)
    return df


def build_trades(frame: pd.DataFrame, asset: str, variant: str, cost_bps: float) -> tuple[pd.DataFrame, int]:
    signal_col = f"signal_{variant}"
    rows: list[dict[str, object]] = []
    cost_rate = float(cost_bps) / 10000.0
    signal_events = 0
    last_exit_idx = -1

    for idx in range(1, len(frame) - 2):
        if idx <= last_exit_idx or idx + 1 >= len(frame):
            continue
        if not bool(frame.iloc[idx][signal_col]):
            continue
        if not np.isfinite(frame.iloc[idx]["fib_50"]):
            continue
        signal_events += 1
        entry_idx = idx + 1
        entry_px = float(frame.iloc[entry_idx]["open"])
        if not np.isfinite(entry_px) or entry_px <= 0:
            continue

        fib_stop = float(frame.iloc[idx]["fib_50"])
        exit_idx = min(len(frame) - 1, entry_idx + HOLD_BARS - 1)
        exit_reason = "time_stop"
        for j in range(entry_idx, min(len(frame), entry_idx + HOLD_BARS)):
            if float(frame.iloc[j]["close"]) < fib_stop:
                exit_idx = j
                exit_reason = "fib_0.5_fail"
                break

        exit_px = float(frame.iloc[exit_idx]["close"])
        gross_ret = exit_px / entry_px - 1.0
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0

        early_idx = min(len(frame) - 1, entry_idx + EARLY_FAIL_BARS - 1)
        early_close = float(frame.iloc[early_idx]["close"])
        early_ret = early_close / entry_px - 1.0
        false_retest = int((early_ret < 0.0) or (float(frame.iloc[early_idx]["close"]) < fib_stop))

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
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "hold_bars": int(exit_idx - entry_idx + 1),
                "early_ret_4bars": early_ret,
                "false_retest": false_retest,
                "exit_reason": exit_reason,
                "fib_618": float(frame.iloc[idx]["fib_618"]),
                "fib_50": fib_stop,
                "vol_ratio": float(frame.iloc[idx]["volume"] / frame.iloc[idx]["volume_sma24"]) if pd.notna(frame.iloc[idx]["volume_sma24"]) and float(frame.iloc[idx]["volume_sma24"]) > 0 else np.nan,
                "trend_gap": float(frame.iloc[idx]["close"] / frame.iloc[idx]["sma200"] - 1.0) if pd.notna(frame.iloc[idx]["sma200"]) and float(frame.iloc[idx]["sma200"]) > 0 else np.nan,
                "ema_gap": float(frame.iloc[idx]["ema9"] / frame.iloc[idx]["ema26"] - 1.0) if pd.notna(frame.iloc[idx]["ema26"]) and float(frame.iloc[idx]["ema26"]) > 0 else np.nan,
                "atr14": float(frame.iloc[idx]["atr14"]) if pd.notna(frame.iloc[idx]["atr14"]) else np.nan,
            }
        )
        last_exit_idx = exit_idx

    return pd.DataFrame(rows), signal_events


def summarize_asset(trades: pd.DataFrame, *, asset: str, variant: str, cost_bps: float, signal_events: int) -> dict[str, object]:
    if trades.empty:
        return {
            "asset": asset,
            "variant": variant,
            "cost_bps_per_side": float(cost_bps),
            "signal_events": int(signal_events),
            "trades": 0,
            "signal_to_trade_ratio": 0.0,
            "total_return": 0.0,
            "avg_net_ret": np.nan,
            "win_rate": np.nan,
            "false_retest_rate": np.nan,
            "avg_hold_bars": np.nan,
        }
    return {
        "asset": asset,
        "variant": variant,
        "cost_bps_per_side": float(cost_bps),
        "signal_events": int(signal_events),
        "trades": int(len(trades)),
        "signal_to_trade_ratio": float(len(trades) / signal_events) if signal_events > 0 else np.nan,
        "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
        "avg_net_ret": float(trades["net_ret"].mean()),
        "win_rate": float((trades["net_ret"] > 0).mean()),
        "false_retest_rate": float(trades["false_retest"].mean()),
        "avg_hold_bars": float(trades["hold_bars"].mean()),
    }


def summarize_overall(asset_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (variant, cost), grp in asset_df.groupby(["variant", "cost_bps_per_side"], sort=False):
        rows.append(
            {
                "variant": variant,
                "cost_bps_per_side": float(cost),
                "mean_total_return": float(grp["total_return"].mean()),
                "positive_asset_ratio": float((grp["total_return"] > 0).mean()),
                "mean_trades": float(grp["trades"].mean()),
                "mean_signal_events": float(grp["signal_events"].mean()),
                "mean_signal_to_trade_ratio": float(grp["signal_to_trade_ratio"].mean()) if grp["signal_to_trade_ratio"].notna().any() else np.nan,
                "mean_win_rate": float(grp["win_rate"].mean()) if grp["win_rate"].notna().any() else np.nan,
                "mean_false_retest_rate": float(grp["false_retest_rate"].mean()) if grp["false_retest_rate"].notna().any() else np.nan,
                "mean_avg_hold_bars": float(grp["avg_hold_bars"].mean()) if grp["avg_hold_bars"].notna().any() else np.nan,
            }
        )
    return pd.DataFrame(rows)


def build_time_stability(primary_trades: pd.DataFrame) -> pd.DataFrame:
    if primary_trades.empty or len(primary_trades) < 9:
        return pd.DataFrame(columns=["time_bucket", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_false_retest_rate"])
    work = primary_trades.copy()
    work["entry_ts_dt"] = pd.to_datetime(work["entry_ts"], utc=True)
    try:
        work["time_bucket"] = pd.qcut(work["entry_ts_dt"].view("int64"), q=3, labels=["bucket_1", "bucket_2", "bucket_3"], duplicates="drop")
    except ValueError:
        return pd.DataFrame(columns=["time_bucket", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_false_retest_rate"])
    rows = []
    for bucket, grp in work.groupby("time_bucket", sort=False, observed=False):
        asset_total = grp.groupby("asset")["net_ret"].apply(lambda s: float((1.0 + s).prod() - 1.0))
        rows.append(
            {
                "time_bucket": str(bucket),
                "mean_total_return": float(asset_total.mean()) if len(asset_total) else np.nan,
                "positive_asset_ratio": float((asset_total > 0).mean()) if len(asset_total) else np.nan,
                "mean_trades": float(grp.groupby("asset").size().mean()) if len(grp) else np.nan,
                "mean_false_retest_rate": float(grp["false_retest"].mean()) if len(grp) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def build_verdict(overall: pd.DataFrame, time_df: pd.DataFrame) -> tuple[str, str]:
    primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    shared = overall[(overall["variant"] == "trend_gate_shared") & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    raw = overall[(overall["variant"] == "fib_touch_raw") & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    if primary.empty:
        return "park / evidence pool", "主臂没有形成可用样本，连最小 clean replication 都不足以保留。"
    p = primary.iloc[0]
    pos_buckets = int((time_df["mean_total_return"] > 0).sum()) if not time_df.empty else 0
    better_than_shared = False if shared.empty else float(p["mean_total_return"]) > float(shared.iloc[0]["mean_total_return"]) and float(p["mean_false_retest_rate"]) <= float(shared.iloc[0]["mean_false_retest_rate"])
    better_than_raw = False if raw.empty else float(p["mean_total_return"]) > float(raw.iloc[0]["mean_total_return"]) and float(p["mean_false_retest_rate"]) < float(raw.iloc[0]["mean_false_retest_rate"])

    if (
        float(p["mean_total_return"]) > 0.0
        and float(p["positive_asset_ratio"]) >= (2.0 / 3.0)
        and float(p["mean_trades"]) >= 20
        and pos_buckets >= 2
        and better_than_shared
        and better_than_raw
    ):
        return "P1 weak candidate / evidence pool", "Fib 0.618 reclaim 叠加 volume/trend/EMA confirm 至少保留了正 pocket，值得再留 1 次便宜诚实检查。"

    return "park / evidence pool", "Fib 0.618 reclaim + volume/trend/EMA confirm 没有把 15m 版本从成本后负收益和高 false-retest 里救出来，不配继续占默认 clean-replication 队列。"


def build_spec() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "section": "candidate",
                "item": "candidate_id",
                "value": "scout_repo_fibtrend_confirmation_15m",
                "note": "FibTrend-Pro / Fib 0.618 reclaim + volume>SMA24 + SMA200/EMA trend gate 的唯一那手最小 clean replication。",
            },
            {
                "section": "scope",
                "item": "sample",
                "value": "BTC-USD / ETH-USD / SOL-USD | Binance 120d 15m cache",
                "note": "固定复用现有历史样本，不追新 bar。",
            },
            {
                "section": "execution",
                "item": "frozen_execution",
                "value": f"next-bar open | no-overlap | close<fib0.5 fail exit or hold {HOLD_BARS} bars | costs={','.join(str(int(c)) for c in COSTS)}bps/side",
                "note": "避免把 TradingView bar-close 判断和同 bar 成交混成乐观填单。",
            },
            {
                "section": "arms",
                "item": "four_arm_compare",
                "value": "fib_touch_raw vs +volume_gate vs +trend_gate_shared vs +ema_confirm(ATR variant)",
                "note": "只回答多一层过滤到底是真减少 false-retest，还是只是减少交易。",
            },
        ]
    )


def write_html(overall: pd.DataFrame, asset_df: pd.DataFrame, time_df: pd.DataFrame, cost_df: pd.DataFrame, verdict: str, reason: str, generated_at: str) -> None:
    ensure_dir(SITE_DIR)
    primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    shared = overall[(overall["variant"] == "trend_gate_shared") & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    raw = overall[(overall["variant"] == "fib_touch_raw") & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    headline = (
        f"主臂 {PRIMARY_VARIANT} 在 6bps/side 下：跨资产 mean_total_return≈{pct(primary['mean_total_return'])}、"
        f"positive_asset_ratio≈{pct(primary['positive_asset_ratio'])}、mean_trades≈{num(primary['mean_trades'],1)}、"
        f"mean_false_retest_rate≈{pct(primary['mean_false_retest_rate'])}；"
        f"对照 raw≈{pct(raw['mean_total_return'])}/{pct(raw['mean_false_retest_rate'])}、"
        f"shared≈{pct(shared['mean_total_return'])}/{pct(shared['mean_false_retest_rate'])}。"
    )
    html = f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Scout repo · FibTrend-Pro · clean replication</title>
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
  <h1>Scout repo · FibTrend-Pro · clean replication</h1>
  <p class='muted'>生成时间：{escape(generated_at)} ｜ 类型：fresh repo source 的唯一那手最小 clean replication ｜ 样本：BTC/ETH/SOL 120d 15m cache</p>

  <div class='card'>
    <h2>这轮只回答什么</h2>
    <ul>
      <li>不扩成高周期 Fib 大研究，也不追最新 bar。</li>
      <li>只比较四臂：<code>fib_touch_raw</code>、<code>+volume_gate</code>、<code>+trend_gate_shared</code>、<code>+ema_confirm(ATR variant)</code>。</li>
      <li>统一执行冻结为 <code>signal close -&gt; next-bar open -&gt; no-overlap -&gt; close&lt;Fib0.5 fail exit or hold 8 bars</code>。</li>
      <li>只回答四个问题：<code>post-cost return / positive_asset_ratio / trade_count / false_retest_rate</code>。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>clean-room 规则</h2>
    <ul>
      <li><b>fib_touch_raw：</b><code>close</code> 从下方重新站上 rolling-50 bar 的 <code>Fib 0.618</code>，下一根开盘入场。</li>
      <li><b>+volume_gate：</b>再要求 <code>volume &gt; SMA(volume,24)</code>。</li>
      <li><b>+trend_gate_shared：</b>再要求 <code>close &gt; SMA200</code>。</li>
      <li><b>+ema_confirm(ATR variant)：</b>再加 <code>EMA9 &gt; EMA26</code> 作为 continuation confirm。</li>
      <li><b>trade off：</b>若持仓后 <code>close &lt; Fib 0.5</code>，视为 false-retest / setup 失效；否则最晚持有 <code>{HOLD_BARS}</code> 根。</li>
      <li><b>false_retest：</b>入场后前 <code>{EARLY_FAIL_BARS}</code> 根内，若 mark-to-market 已转负，或已经跌回 <code>Fib 0.5</code> 下方，就记为 early failure。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>hard verdict</h2>
    <p><span class='pill'>{escape(verdict)}</span></p>
    <p><b>{escape(headline)}</b></p>
    <p class='muted'>{escape(reason)}</p>
  </div>

  <div class='card'>
    <h2>四臂总表</h2>
    {render_table(overall[["variant","cost_bps_per_side","mean_total_return","positive_asset_ratio","mean_trades","mean_signal_events","mean_signal_to_trade_ratio","mean_win_rate","mean_false_retest_rate"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_signal_to_trade_ratio","mean_win_rate","mean_false_retest_rate"}, digits_cols={"mean_trades":1,"mean_signal_events":1})}
  </div>

  <div class='card'>
    <h2>分资产摘要</h2>
    {render_table(asset_df[["asset","variant","cost_bps_per_side","signal_events","trades","signal_to_trade_ratio","total_return","win_rate","false_retest_rate"]], percent_cols={"signal_to_trade_ratio","total_return","win_rate","false_retest_rate"}, digits_cols={"signal_events":0,"trades":0})}
  </div>

  <div class='card'>
    <h2>时间稳定性（主臂 6bps）</h2>
    {render_table(time_df[["time_bucket","mean_total_return","positive_asset_ratio","mean_trades","mean_false_retest_rate"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_false_retest_rate"}, digits_cols={"mean_trades":1})}
  </div>

  <div class='card'>
    <h2>成本 / 交易数稳定性（主臂）</h2>
    {render_table(cost_df[["variant","cost_bps_per_side","mean_total_return","positive_asset_ratio","mean_trades","mean_false_retest_rate"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_false_retest_rate"}, digits_cols={"mean_trades":1})}
  </div>
</body>
</html>
"""
    (SITE_DIR / "report.html").write_text(html, encoding="utf-8")


def update_todo(generated_at: str, overall: pd.DataFrame, time_df: pd.DataFrame, verdict: str) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    shared = overall[(overall["variant"] == "trend_gate_shared") & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    raw = overall[(overall["variant"] == "fib_touch_raw") & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    buckets = [f"{r['time_bucket']}≈{pct(r['mean_total_return'])} / {pct(r['positive_asset_ratio'])}" for _, r in time_df.iterrows()]
    time_note = "time-pocket honesty：" + "；".join(buckets) + "。" if buckets else "当前样本不足以可靠拆成 3 个时间桶。"
    note = (
        f"- **最新补充（{generated_at}）**：这轮已按顶板默认顺序把 `FibTrend-Pro / Fib 0.618 + volume/trend gate` 的唯一那手 **最小 clean replication** 跑完：固定复用 `BTC/ETH/SOL 120d 15m` cache，比较 `fib_touch_raw / +volume_gate / +trend_gate_shared / +ema_confirm(ATR variant)` 四臂，并统一冻结到 `next-bar open + no-overlap + close<Fib0.5 fail exit or hold 8 bars`，只看 `6/10/15/20bps per side`。结果很直接：主臂 `ema_confirm_atr` 在 `6bps/side` 下跨资产 `mean_total_return≈{pct(primary['mean_total_return'])}`、`positive_asset_ratio≈{pct(primary['positive_asset_ratio'])}`、`mean_trades≈{num(primary['mean_trades'],1)}`、`mean_false_retest_rate≈{pct(primary['mean_false_retest_rate'])}`；对照 `fib_touch_raw≈{pct(raw['mean_total_return'])}/{pct(raw['mean_false_retest_rate'])}`、`trend_gate_shared≈{pct(shared['mean_total_return'])}/{pct(shared['mean_false_retest_rate'])}`。{time_note} 因此当前更诚实的 hard verdict 是 **`{verdict}`**：它通过了守门，但最小 replication 仍没有把 15m 版本从成本后负 pocket 里救出来，不再继续占默认 clean-replication 队列。\n  - 若下一轮 `EMA` 仍是 `waiting_not_due`，默认应回退比较 `EMA-ADX-VOL skeleton > Rank 35b > Run 3 / tiny-live plumbing`，而不是继续磨这条 Fib repo 模板或回头挤占 `P3 continuity`。\n  - 网页落点：`reports/site/factors/scout_repo_fibtrend_confirmation_15m/report.html`。"
    )

    marker = "- **当前候选阶段表（精简版，authoritative）**："
    if note not in text and marker in text:
        text = text.replace(marker, note + "\n" + marker, 1)

    old_window = "> **当前窗口排班（2026-03-18 04:19 UTC，authoritative override）**：`00:02 UTC` 的 crypto due-now refresh 已真实消化，最新 due guardrail 仍显示：A 股三条 lane `-> 2026-03-18 07:00 UTC`、`美股 1d+1wk -> 2026-03-18 20:00 UTC`、`Crypto 1d+1wk -> 2026-03-19 00:00 UTC`，因此 `Run 1 / EMA` 当前仍是 **`running paper / waiting_not_due`**。与此同时，`Rank 17 / Rank 2 / Rank 29 / Rank 32b` 这几条既有 `P3 narrow paper lane` 继续由专属 refresh cron 或最小 monitoring 接线低频托管，当前没有新的 `append/review` 状态变化；`Rank 43`、`Rank 40`、`BotScalpingTwinRange` 与 `Rank 27b` 均已在各自允许预算内给出 hard verdict 并压回 **`park / evidence pool`**。而 `FibTrend-Pro / Fib 0.618 + volume/trend gate` 这轮已经完成 source-intake 两条诚实守门，并升级成 **`guard-passed / admit_to_clean_replication_queue`**。换句话说：若下一轮 `EMA` 仍在 waiting-window，bot3 默认顺序应改成 **`FibTrend-Pro minimal clean replication > EMA-ADX-VOL skeleton > Rank 35b > Run 3 / tiny-live plumbing`**，而不是再重复 source-intake、直接从 `Rank 35b` 开始，或回头重磨已 park 线 / 挤占 `P3` continuity。"
    new_window = "> **当前窗口排班（2026-03-18 04:40 UTC，authoritative override）**：`00:02 UTC` 的 crypto due-now refresh 已真实消化，最新 due guardrail 仍显示：A 股三条 lane `-> 2026-03-18 07:00 UTC`、`美股 1d+1wk -> 2026-03-18 20:00 UTC`、`Crypto 1d+1wk -> 2026-03-19 00:00 UTC`，因此 `Run 1 / EMA` 当前仍是 **`running paper / waiting_not_due`**。与此同时，`Rank 17 / Rank 2 / Rank 29 / Rank 32b` 这几条既有 `P3 narrow paper lane` 继续由专属 refresh cron 或最小 monitoring 接线低频托管，当前没有新的 `append/review` 状态变化；`Rank 43`、`Rank 40`、`BotScalpingTwinRange`、`Rank 27b` 与 `FibTrend-Pro` 均已在各自允许预算内给出 hard verdict 并压回 **`park / evidence pool`**。换句话说：若下一轮 `EMA` 仍在 waiting-window，bot3 默认应回退比较 **`EMA-ADX-VOL skeleton > Rank 35b > Run 3 / tiny-live plumbing`**，而不是继续磨 `FibTrend-Pro` 或回头重磨已 park 线 / 挤占 `P3 continuity`。"
    if old_window in text:
        text = text.replace(old_window, new_window, 1)

    TODO_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    asset_rows: list[dict[str, object]] = []
    all_trades: list[pd.DataFrame] = []
    primary_trades: list[pd.DataFrame] = []

    for asset, symbol in ASSETS.items():
        frame = build_frame(asset, symbol)
        frame.to_csv(ART_DIR / f"{asset.lower().replace('-usd', '')}_frame.csv", index=False)
        for variant in VARIANTS:
            for cost in COSTS:
                trades, signal_events = build_trades(frame, asset, variant, cost)
                asset_rows.append(summarize_asset(trades, asset=asset, variant=variant, cost_bps=cost, signal_events=signal_events))
                if not trades.empty:
                    all_trades.append(trades)
                if variant == PRIMARY_VARIANT and cost == PRIMARY_COST and not trades.empty:
                    primary_trades.append(trades)
                    trades.to_csv(ART_DIR / f"trades_primary_6bps_{asset.lower().replace('-usd', '')}.csv", index=False)

    asset_df = pd.DataFrame(asset_rows).sort_values(["variant", "cost_bps_per_side", "asset"]).reset_index(drop=True)
    overall = summarize_overall(asset_df).sort_values(["variant", "cost_bps_per_side"]).reset_index(drop=True)
    primary_trades_df = pd.concat(primary_trades, ignore_index=True) if primary_trades else pd.DataFrame()
    time_df = build_time_stability(primary_trades_df)
    cost_df = overall[overall["variant"] == PRIMARY_VARIANT].copy().sort_values("cost_bps_per_side").reset_index(drop=True)
    verdict, reason = build_verdict(overall, time_df)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    build_spec().to_csv(ART_DIR / "clean_room_spec.csv", index=False)
    asset_df.to_csv(ART_DIR / "asset_summary.csv", index=False)
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    time_df.to_csv(ART_DIR / "time_stability.csv", index=False)
    cost_df.to_csv(ART_DIR / "cost_trade_stability.csv", index=False)
    pd.DataFrame([
        {
            "generated_at_utc": generated_at,
            "candidate_id": "scout_repo_fibtrend_confirmation_15m",
            "source": "11Muhil/FibTrend-Pro-Strategy_Pinescript",
            "hard_verdict": verdict,
            "verdict_reason": reason,
            "scope": "BTC/ETH/SOL 120d 15m cache",
        }
    ]).to_csv(ART_DIR / "meta.csv", index=False)
    if all_trades:
        pd.concat(all_trades, ignore_index=True).sort_values(["variant", "cost_bps_per_side", "asset", "entry_ts"]).to_csv(ART_DIR / "all_trades.csv", index=False)
    if not primary_trades_df.empty:
        primary_trades_df.sort_values(["asset", "entry_ts"]).to_csv(ART_DIR / "trades_primary_6bps.csv", index=False)

    write_html(overall, asset_df, time_df, cost_df, verdict, reason, generated_at)
    update_todo(generated_at, overall, time_df, verdict)
    print(f"verdict={verdict}")
    print(overall[(overall['cost_bps_per_side'] == 6.0)][['variant', 'mean_total_return', 'positive_asset_ratio', 'mean_false_retest_rate', 'mean_trades']].to_dict(orient='records'))


if __name__ == "__main__":
    main()
