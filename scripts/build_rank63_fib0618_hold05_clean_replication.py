#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank63_fib0618_hold05_fail_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank63_fib0618_hold05_fail_15m"
READING_SITE_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank63_fib0618_hold05_fail_clean_replication.html"
TODO_PATH = ROOT / "docs" / "TODO.md"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
VARIANTS = [
    "fib618_reclaim_raw",
    "volume_gate",
    "volume_gate_fib50_fail",
    "volume_gate_fib50_fail_sma200",
]
PRIMARY_VARIANT = "volume_gate_fib50_fail_sma200"
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0, 20.0]
LOOKBACK = 50
VOL_SMA = 24
SMA_TREND = 200
ATR_PERIOD = 14
HOLD_BARS = 12
EARLY_FAIL_BARS = 4
TARGET_ATR = 1.0


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
    df["atr14"] = atr(df)

    reclaim_618 = (df["close"] > df["fib_618"]) & (df["close"].shift(1) <= df["fib_618"].shift(1))
    vol_gate = df["volume"] > df["volume_sma24"]
    trend_gate = df["close"] > df["sma200"]

    df["signal_fib618_reclaim_raw"] = reclaim_618.fillna(False)
    df["signal_volume_gate"] = (reclaim_618 & vol_gate).fillna(False)
    df["signal_volume_gate_fib50_fail"] = (reclaim_618 & vol_gate).fillna(False)
    df["signal_volume_gate_fib50_fail_sma200"] = (reclaim_618 & vol_gate & trend_gate).fillna(False)
    return df


def build_trades(frame: pd.DataFrame, asset: str, variant: str, cost_bps: float) -> tuple[pd.DataFrame, int]:
    signal_col = f"signal_{variant}"
    rows: list[dict[str, object]] = []
    signal_events = 0
    last_exit_idx = -1
    cost_rate = float(cost_bps) / 10000.0

    for idx in range(1, len(frame) - 2):
        if idx <= last_exit_idx:
            continue
        if not bool(frame.iloc[idx][signal_col]):
            continue
        fib618 = frame.iloc[idx]["fib_618"]
        fib50 = frame.iloc[idx]["fib_50"]
        atr14 = frame.iloc[idx]["atr14"]
        if not (np.isfinite(fib618) and np.isfinite(fib50) and np.isfinite(atr14) and atr14 > 0):
            continue

        signal_events += 1
        entry_idx = idx + 1
        if entry_idx >= len(frame):
            continue
        entry_px = float(frame.iloc[entry_idx]["open"])
        if not np.isfinite(entry_px) or entry_px <= 0:
            continue

        target_px = entry_px + TARGET_ATR * float(atr14)
        exit_idx = min(len(frame) - 1, entry_idx + HOLD_BARS - 1)
        exit_reason = "time_stop"
        target_hit = 0
        failure_before_target = 0
        max_adverse_atr = 0.0
        early_fail = 0

        for j in range(entry_idx, min(len(frame), entry_idx + HOLD_BARS)):
            row = frame.iloc[j]
            low = float(row["low"])
            high = float(row["high"])
            close = float(row["close"])
            max_adverse_atr = max(max_adverse_atr, max(entry_px - low, 0.0) / float(atr14))
            if j <= entry_idx + EARLY_FAIL_BARS - 1 and close < float(fib50):
                early_fail = 1
            if high >= target_px:
                exit_idx = j
                exit_reason = "target_1atr"
                target_hit = 1
                break
            if close < float(fib50):
                exit_idx = j
                exit_reason = "fib50_fail"
                failure_before_target = 1
                break

        exit_px = float(frame.iloc[exit_idx]["close"])
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
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "hold_bars": int(exit_idx - entry_idx + 1),
                "target_hit_12bars": int(target_hit),
                "failure_before_target": int(failure_before_target),
                "false_retest_4bars": int(early_fail),
                "mae_atr": float(max_adverse_atr),
                "exit_reason": exit_reason,
                "fib_618": float(fib618),
                "fib_50": float(fib50),
                "target_px": float(target_px),
                "vol_ratio": float(frame.iloc[idx]["volume"] / frame.iloc[idx]["volume_sma24"]) if pd.notna(frame.iloc[idx]["volume_sma24"]) and float(frame.iloc[idx]["volume_sma24"]) > 0 else np.nan,
                "trend_gap": float(frame.iloc[idx]["close"] / frame.iloc[idx]["sma200"] - 1.0) if pd.notna(frame.iloc[idx]["sma200"]) and float(frame.iloc[idx]["sma200"]) > 0 else np.nan,
                "atr14": float(atr14),
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
            "trade_count_retention": 0.0,
            "total_return": 0.0,
            "avg_net_ret": np.nan,
            "failure_before_target_rate": np.nan,
            "target_hit_within_12bars": np.nan,
            "mae_atr": np.nan,
            "false_retest_4bars_rate": np.nan,
        }
    return {
        "asset": asset,
        "variant": variant,
        "cost_bps_per_side": float(cost_bps),
        "signal_events": int(signal_events),
        "trades": int(len(trades)),
        "trade_count_retention": float(len(trades) / signal_events) if signal_events > 0 else np.nan,
        "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
        "avg_net_ret": float(trades["net_ret"].mean()),
        "failure_before_target_rate": float(trades["failure_before_target"].mean()),
        "target_hit_within_12bars": float(trades["target_hit_12bars"].mean()),
        "mae_atr": float(trades["mae_atr"].mean()),
        "false_retest_4bars_rate": float(trades["false_retest_4bars"].mean()),
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
                "mean_trade_count_retention": float(grp["trade_count_retention"].mean()) if grp["trade_count_retention"].notna().any() else np.nan,
                "mean_failure_before_target_rate": float(grp["failure_before_target_rate"].mean()) if grp["failure_before_target_rate"].notna().any() else np.nan,
                "mean_target_hit_within_12bars": float(grp["target_hit_within_12bars"].mean()) if grp["target_hit_within_12bars"].notna().any() else np.nan,
                "mean_mae_atr": float(grp["mae_atr"].mean()) if grp["mae_atr"].notna().any() else np.nan,
                "mean_false_retest_4bars_rate": float(grp["false_retest_4bars_rate"].mean()) if grp["false_retest_4bars_rate"].notna().any() else np.nan,
            }
        )
    return pd.DataFrame(rows)


def build_time_stability(primary_trades: pd.DataFrame) -> pd.DataFrame:
    if primary_trades.empty or len(primary_trades) < 9:
        return pd.DataFrame(columns=["time_bucket", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_failure_before_target_rate", "mean_target_hit_within_12bars"])
    work = primary_trades.copy()
    work["entry_ts_dt"] = pd.to_datetime(work["entry_ts"], utc=True)
    try:
        work["time_bucket"] = pd.qcut(work["entry_ts_dt"].view("int64"), q=3, labels=["bucket_1", "bucket_2", "bucket_3"], duplicates="drop")
    except ValueError:
        return pd.DataFrame(columns=["time_bucket", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_failure_before_target_rate", "mean_target_hit_within_12bars"])
    rows = []
    for bucket, grp in work.groupby("time_bucket", sort=False, observed=False):
        asset_total = grp.groupby("asset")["net_ret"].apply(lambda s: float((1.0 + s).prod() - 1.0))
        rows.append(
            {
                "time_bucket": str(bucket),
                "mean_total_return": float(asset_total.mean()) if len(asset_total) else np.nan,
                "positive_asset_ratio": float((asset_total > 0).mean()) if len(asset_total) else np.nan,
                "mean_trades": float(grp.groupby("asset").size().mean()) if len(grp) else np.nan,
                "mean_failure_before_target_rate": float(grp["failure_before_target"].mean()) if len(grp) else np.nan,
                "mean_target_hit_within_12bars": float(grp["target_hit_12bars"].mean()) if len(grp) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def build_verdict(overall: pd.DataFrame, time_df: pd.DataFrame) -> tuple[str, str]:
    primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    raw = overall[(overall["variant"] == "fib618_reclaim_raw") & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    volume = overall[(overall["variant"] == "volume_gate") & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    fibfail = overall[(overall["variant"] == "volume_gate_fib50_fail") & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    if primary.empty:
        return "park / evidence pool", "主臂没有形成可用样本，连最小 clean replication 都不足以保留。"
    p = primary.iloc[0]
    raw_p = raw.iloc[0] if not raw.empty else None
    volume_p = volume.iloc[0] if not volume.empty else None
    fibfail_p = fibfail.iloc[0] if not fibfail.empty else None
    pos_buckets = int((time_df["mean_total_return"] > 0).sum()) if not time_df.empty else 0

    better_than_raw = bool(raw_p is not None and float(p["mean_total_return"]) > float(raw_p["mean_total_return"]) and float(p["mean_failure_before_target_rate"]) <= float(raw_p["mean_failure_before_target_rate"]))
    better_than_volume = bool(volume_p is not None and float(p["mean_total_return"]) >= float(volume_p["mean_total_return"]) and float(p["mean_failure_before_target_rate"]) <= float(volume_p["mean_failure_before_target_rate"]))
    better_than_fibfail = bool(fibfail_p is not None and float(p["mean_total_return"]) >= float(fibfail_p["mean_total_return"]) and float(p["mean_failure_before_target_rate"]) <= float(fibfail_p["mean_failure_before_target_rate"]))

    if (
        float(p["mean_total_return"]) > 0.0
        and float(p["positive_asset_ratio"]) >= (2.0 / 3.0)
        and float(p["mean_trades"]) >= 12.0
        and float(p["mean_trade_count_retention"]) >= 0.35
        and float(p["mean_failure_before_target_rate"]) <= 0.45
        and float(p["mean_target_hit_within_12bars"]) >= 0.40
        and pos_buckets >= 2
        and better_than_raw and better_than_volume and better_than_fibfail
    ):
        return "P1 weak candidate / evidence pool", "Fib 0.618 hold / 0.5 fail + volume + SMA200 至少保留了正 pocket，值得在下一轮只给 1 次 truly verdict-changing 的时间稳定性检查。"

    return "park / evidence pool", "Fib 0.618 hold / 0.5 fail + volume + SMA200 没把 15m 版本从成本后负 pocket / 高失败率里救出来，不配继续占默认 clean-replication 队列。"


def build_spec() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "section": "candidate",
            "item": "candidate_id",
            "value": "scout_rank63_fib0618_hold05_fail_15m",
            "note": "Rank 63 / Fib 0.618 hold / 0.5 fail gate 的唯一那手最小 clean replication。",
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
            "value": f"next-bar open | no-overlap | 1 ATR target within {HOLD_BARS} bars | close<fib0.5 fail exit | costs={','.join(str(int(c)) for c in COSTS)}bps/side",
            "note": "避免把 bar-close 判断和同 bar 成交混成乐观填单。",
        },
        {
            "section": "arms",
            "item": "four_arm_compare",
            "value": "fib618_reclaim_raw vs +volume_gate vs +volume_gate+fib50_fail vs +volume_gate+fib50_fail+sma200_filter",
            "note": "只回答更多 through/fail 约束到底是真降低 failure-before-target，还是只是砍掉 trade count。",
        },
    ])


def write_html(overall: pd.DataFrame, asset_df: pd.DataFrame, time_df: pd.DataFrame, cost_df: pd.DataFrame, verdict: str, reason: str, generated_at: str) -> None:
    ensure_dir(SITE_DIR)
    primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    raw = overall[(overall["variant"] == "fib618_reclaim_raw") & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    volume = overall[(overall["variant"] == "volume_gate") & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    fibfail = overall[(overall["variant"] == "volume_gate_fib50_fail") & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    headline = (
        f"主臂 {PRIMARY_VARIANT} 在 6bps/side 下：跨资产 mean_total_return≈{pct(primary['mean_total_return'])}、"
        f"positive_asset_ratio≈{pct(primary['positive_asset_ratio'])}、mean_trades≈{num(primary['mean_trades'],1)}、"
        f"failure_before_target≈{pct(primary['mean_failure_before_target_rate'])}、target_hit_12bars≈{pct(primary['mean_target_hit_within_12bars'])}；"
        f"对照 raw≈{pct(raw['mean_total_return'])}/{pct(raw['mean_failure_before_target_rate'])}、"
        f"+volume≈{pct(volume['mean_total_return'])}/{pct(volume['mean_failure_before_target_rate'])}、"
        f"+fib50_fail≈{pct(fibfail['mean_total_return'])}/{pct(fibfail['mean_failure_before_target_rate'])}。"
    )
    html = f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 63 · Fib 0.618 hold / 0.5 fail gate · clean replication</title>
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
  <h1>Rank 63 · Fib 0.618 hold / 0.5 fail gate · clean replication</h1>
  <p class='muted'>生成时间：{escape(generated_at)} ｜ 类型：fresh repo source 的唯一那手最小 clean replication ｜ 样本：BTC/ETH/SOL 120d 15m cache</p>

  <div class='card'>
    <h2>这轮只回答什么</h2>
    <ul>
      <li>不把整套 FibTrend 高周期叙事搬进 15m，也不追最新 bar。</li>
      <li>只比较四臂：<code>fib618_reclaim_raw</code>、<code>+volume_gate</code>、<code>+volume_gate+fib50_fail</code>、<code>+volume_gate+fib50_fail+sma200_filter</code>。</li>
      <li>统一执行冻结为 <code>signal close -&gt; next-bar open -&gt; no-overlap -&gt; 1 ATR target or close&lt;Fib0.5 fail or hold {HOLD_BARS} bars</code>。</li>
      <li>只回答五个问题：<code>post-cost return / failure_before_target_rate / target_hit_within_12bars / MAE/ATR / trade_count_retention</code>。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>clean-room 规则</h2>
    <ul>
      <li><b>fib618_reclaim_raw：</b><code>close</code> 从下方重新站上 rolling-50 bar 的 <code>Fib 0.618</code>，下一根开盘入场。</li>
      <li><b>+volume_gate：</b>再要求 <code>volume &gt; SMA(volume,24)</code>。</li>
      <li><b>+volume_gate+fib50_fail：</b>执行层承认 <code>close &lt; Fib 0.5</code> 就是回踩失败；否则最多持有 <code>{HOLD_BARS}</code> 根，目标先只看 <code>+1 ATR</code>。</li>
      <li><b>+volume_gate+fib50_fail+sma200_filter：</b>再要求 <code>close &gt; SMA200</code>，只回答大方向不逆风时 through/fail band 有没有更诚实。</li>
      <li><b>false / fail 指标：</b><code>failure_before_target</code> 指 <code>{HOLD_BARS}</code> 根内先出现 <code>close &lt; Fib0.5</code>；<code>false_retest_4bars</code> 指前 <code>{EARLY_FAIL_BARS}</code> 根内已经跌回 <code>Fib0.5</code> 下方。</li>
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
    {render_table(overall[["variant","cost_bps_per_side","mean_total_return","positive_asset_ratio","mean_trades","mean_trade_count_retention","mean_failure_before_target_rate","mean_target_hit_within_12bars","mean_mae_atr"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_trade_count_retention","mean_failure_before_target_rate","mean_target_hit_within_12bars"}, digits_cols={"mean_trades":1,"mean_mae_atr":2})}
  </div>

  <div class='card'>
    <h2>分资产摘要</h2>
    {render_table(asset_df[["asset","variant","cost_bps_per_side","signal_events","trades","trade_count_retention","total_return","failure_before_target_rate","target_hit_within_12bars","mae_atr"]], percent_cols={"trade_count_retention","total_return","failure_before_target_rate","target_hit_within_12bars"}, digits_cols={"signal_events":0,"trades":0,"mae_atr":2})}
  </div>

  <div class='card'>
    <h2>时间稳定性（主臂 6bps）</h2>
    {render_table(time_df[["time_bucket","mean_total_return","positive_asset_ratio","mean_trades","mean_failure_before_target_rate","mean_target_hit_within_12bars"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_failure_before_target_rate","mean_target_hit_within_12bars"}, digits_cols={"mean_trades":1})}
  </div>

  <div class='card'>
    <h2>成本 / 交易数稳定性（主臂）</h2>
    {render_table(cost_df[["variant","cost_bps_per_side","mean_total_return","positive_asset_ratio","mean_trades","mean_trade_count_retention","mean_failure_before_target_rate","mean_target_hit_within_12bars"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_trade_count_retention","mean_failure_before_target_rate","mean_target_hit_within_12bars"}, digits_cols={"mean_trades":1})}
  </div>
</body>
</html>
"""
    (SITE_DIR / "report.html").write_text(html, encoding="utf-8")
    READING_SITE_PATH.write_text(html.replace("../../plans/momentum_todo.html", "../../plans/momentum_todo.html"), encoding="utf-8")


def update_todo(generated_at: str, overall: pd.DataFrame, time_df: pd.DataFrame, verdict: str) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    section_header = "### Next 3 bot3 runs（当前默认执行顺序）"
    primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    raw = overall[(overall["variant"] == "fib618_reclaim_raw") & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    volume = overall[(overall["variant"] == "volume_gate") & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    buckets = [f"{r['time_bucket']}≈{pct(r['mean_total_return'])} / {pct(r['positive_asset_ratio'])}" for _, r in time_df.iterrows()]
    time_note = "time-pocket：" + "；".join(buckets) + "。" if buckets else "time-pocket：当前样本不足以可靠拆成 3 个时间桶。"
    note = (
        f"> **最新补充（{generated_at}）**：这轮先再次核对 `Run 1 / EMA due-check` 与 `P3` 托管位状态：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍显示全 desk 没有新的 `due-now / overdue` lane（最早仍是 `美股 1d+1wk -> 2026-03-18 20:00 UTC`，其后 `Crypto 1d+1wk -> 2026-03-19 00:00 UTC`、A 股三条 lane `-> 2026-03-19 07:00 UTC`），而 `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 最新一次仍是 `new_closed_trades_appended=0`，因此当前没有新的 `Paper Seat` due-now 动作，也没有新的 `P3 status-changing event` 值得 bot3 回头挤占 continuity。随后按权威顺序执行 **`Run 2 / Rank 63 minimal clean replication`**：固定复用 `BTC/ETH/SOL 120d 15m` cache，只比较 `fib618_reclaim_raw`、`+volume_gate`、`+volume_gate+fib50_fail`、`+volume_gate+fib50_fail+sma200_filter` 四臂，统一冻结到 `next-bar open + no-overlap + 1 ATR target or close<Fib0.5 fail or hold 12 bars`。\n"
        f">  - `6bps/side` 下的主读法 `volume_gate+fib50_fail+sma200_filter` 结果为：`mean_total_return≈{pct(primary['mean_total_return'])}`、`positive_asset_ratio≈{pct(primary['positive_asset_ratio'])}`、`mean_trades≈{num(primary['mean_trades'],1)}`、`trade_count_retention≈{pct(primary['mean_trade_count_retention'])}`、`failure_before_target≈{pct(primary['mean_failure_before_target_rate'])}`、`target_hit_12bars≈{pct(primary['mean_target_hit_within_12bars'])}`；对照 `fib618_reclaim_raw≈{pct(raw['mean_total_return'])}/{pct(raw['mean_failure_before_target_rate'])}`、`+volume_gate≈{pct(volume['mean_total_return'])}/{pct(volume['mean_failure_before_target_rate'])}`。\n"
        f">  - {time_note}\n"
        f">  - 当前更诚实的 hard verdict：**`Rank 63 / Fib 0.618 hold / 0.5 fail gate = {verdict}`**。\n"
        f">  - reader-facing 落点：`reports/site/factors/scout_rank63_fib0618_hold05_fail_15m/report.html`、`reports/site/reading/repo_scout/rank63_fib0618_hold05_fail_clean_replication.html`；artifact：`reports/artifacts/scout_rank63_fib0618_hold05_fail_15m/overall_summary.csv`。\n"
        f">  - 因此当前最新 `Next 3` 顺序应更新为：**`Run 1 = EMA due-check only` -> `Run 2 = 若 Rank 63 已直接 park，则回到 fresh paper/repo intake（优先 pullback-quality / CQI，再比较 fresh pool 其他 source）` -> `Run 3 = 只有 fresh repo queue 也 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing`**。"
    )
    if note in text:
        return
    idx = text.find(section_header)
    if idx == -1:
        return
    insert_pos = idx + len(section_header)
    text = text[:insert_pos] + "\n\n" + note + text[insert_pos:]
    TODO_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_SITE_PATH.parent)

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
            "candidate_id": "scout_rank63_fib0618_hold05_fail_15m",
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
    print(overall[overall["cost_bps_per_side"] == 6.0][["variant", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_failure_before_target_rate", "mean_target_hit_within_12bars"]].to_dict(orient="records"))


if __name__ == "__main__":
    main()
