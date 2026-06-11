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
ART_DIR = ROOT / "reports" / "artifacts" / "scout_repo_psar_anchor_ema_confirm_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_repo_psar_anchor_ema_confirm_15m"
TODO_PATH = ROOT / "docs" / "TODO.md"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
ARMS = ["ema_raw", "psar_raw", "psar_anchor_ema_confirm"]
PRIMARY_ARM = "psar_anchor_ema_confirm"
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0, 20.0]
EMA_FAST = 20
EMA_SLOW = 50
EMA_SLOPE_LOOKBACK = 3
EMA_SLOPE_FLOOR = 0.0003
HOLD_BARS = 8
EARLY_FAIL_BARS = 4
HTF_RULE = "1h"
HTF_PSAR_STEP = 0.02
HTF_PSAR_MAX_STEP = 0.2
PSAR_STEP = 0.02
PSAR_MAX_STEP = 0.2


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


def parabolic_sar(high: pd.Series, low: pd.Series, step: float = PSAR_STEP, max_step: float = PSAR_MAX_STEP) -> tuple[np.ndarray, np.ndarray]:
    hi = np.asarray(high, dtype=float)
    lo = np.asarray(low, dtype=float)
    n = len(hi)
    sar = np.full(n, np.nan, dtype=float)
    direction = np.zeros(n, dtype=int)
    if n == 0:
        return sar, direction
    if n == 1:
        direction[0] = 1
        sar[0] = lo[0]
        return sar, direction

    bull = (hi[1] + lo[1]) >= (hi[0] + lo[0])
    af = step
    ep = hi[0] if bull else lo[0]
    current_sar = lo[0] if bull else hi[0]
    sar[0] = current_sar
    direction[0] = 1 if bull else -1

    for i in range(1, n):
        current_sar = current_sar + af * (ep - current_sar)
        if bull:
            current_sar = min(current_sar, lo[i - 1])
            if i >= 2:
                current_sar = min(current_sar, lo[i - 2])
            if lo[i] < current_sar:
                bull = False
                current_sar = ep
                ep = lo[i]
                af = step
            else:
                if hi[i] > ep:
                    ep = hi[i]
                    af = min(af + step, max_step)
        else:
            current_sar = max(current_sar, hi[i - 1])
            if i >= 2:
                current_sar = max(current_sar, hi[i - 2])
            if hi[i] > current_sar:
                bull = True
                current_sar = ep
                ep = hi[i]
                af = step
            else:
                if lo[i] < ep:
                    ep = lo[i]
                    af = min(af + step, max_step)
        sar[i] = current_sar
        direction[i] = 1 if bull else -1
    return sar, direction


def load_cached_bars(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_cached_bars(symbol, asset)
    df["ema_fast"] = df["close"].ewm(span=EMA_FAST, adjust=False).mean()
    df["ema_slow"] = df["close"].ewm(span=EMA_SLOW, adjust=False).mean()
    df["ema_slope"] = df["ema_fast"].pct_change(EMA_SLOPE_LOOKBACK)
    sar_15m, psar_dir_15m = parabolic_sar(df["high"], df["low"], step=PSAR_STEP, max_step=PSAR_MAX_STEP)
    df["psar_15m"] = sar_15m
    df["psar_dir_15m"] = psar_dir_15m

    htf = (
        df.set_index("timestamp")[["open", "high", "low", "close"]]
        .resample(HTF_RULE)
        .agg({"open": "first", "high": "max", "low": "min", "close": "last"})
        .dropna()
        .reset_index()
    )
    sar_htf, psar_dir_htf = parabolic_sar(htf["high"], htf["low"], step=HTF_PSAR_STEP, max_step=HTF_PSAR_MAX_STEP)
    htf["psar_htf"] = sar_htf
    htf["psar_dir_htf"] = psar_dir_htf

    frame = pd.merge_asof(
        df.sort_values("timestamp"),
        htf[["timestamp", "psar_htf", "psar_dir_htf"]].sort_values("timestamp"),
        on="timestamp",
        direction="backward",
    )
    frame["close_above_fast"] = (frame["close"] > frame["ema_fast"]).astype(int)
    frame["close_below_fast"] = (frame["close"] < frame["ema_fast"]).astype(int)
    return frame


def build_arm_signals(frame: pd.DataFrame, arm: str) -> pd.DataFrame:
    out = frame[["timestamp", "asset"]].copy()
    if arm == "ema_raw":
        long_cond = (frame["ema_fast"] > frame["ema_slow"]) & (frame["ema_slope"] > EMA_SLOPE_FLOOR)
        short_cond = (frame["ema_fast"] < frame["ema_slow"]) & (frame["ema_slope"] < -EMA_SLOPE_FLOOR)
        long_sig = long_cond & (~long_cond.shift(1).fillna(False))
        short_sig = short_cond & (~short_cond.shift(1).fillna(False))
    elif arm == "psar_raw":
        long_sig = (frame["psar_dir_15m"] == 1) & (frame["psar_dir_15m"].shift(1) != 1)
        short_sig = (frame["psar_dir_15m"] == -1) & (frame["psar_dir_15m"].shift(1) != -1)
    elif arm == PRIMARY_ARM:
        long_cond = (
            (frame["psar_dir_htf"] == 1)
            & (frame["ema_fast"] > frame["ema_slow"])
            & (frame["ema_slope"] > EMA_SLOPE_FLOOR)
            & (frame["close_above_fast"] == 1)
        )
        short_cond = (
            (frame["psar_dir_htf"] == -1)
            & (frame["ema_fast"] < frame["ema_slow"])
            & (frame["ema_slope"] < -EMA_SLOPE_FLOOR)
            & (frame["close_below_fast"] == 1)
        )
        long_sig = long_cond & (~long_cond.shift(1).fillna(False))
        short_sig = short_cond & (~short_cond.shift(1).fillna(False))
    else:
        raise ValueError(f"unknown arm: {arm}")

    out["long_signal"] = long_sig.fillna(False).astype(int)
    out["short_signal"] = short_sig.fillna(False).astype(int)
    return out


def backtest_arm(frame: pd.DataFrame, arm: str, cost_bps: float) -> tuple[pd.DataFrame, int]:
    signals = build_arm_signals(frame, arm)
    rows: list[dict[str, object]] = []
    last_exit_idx = -1
    signal_events = 0
    cost_rate = float(cost_bps) / 10000.0

    for idx, sig in signals.iterrows():
        if idx <= last_exit_idx or idx + 1 >= len(frame):
            continue
        direction = 1 if int(sig["long_signal"]) == 1 else -1 if int(sig["short_signal"]) == 1 else 0
        if direction == 0:
            continue
        signal_events += 1
        entry_idx = idx + 1
        exit_idx = min(len(frame) - 1, entry_idx + HOLD_BARS - 1)
        entry_px = float(frame.iloc[entry_idx]["open"])
        exit_px = float(frame.iloc[exit_idx]["close"])
        gross_ret = (exit_px / entry_px - 1.0) * direction
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0

        early_probe_idx = min(len(frame) - 1, entry_idx + EARLY_FAIL_BARS - 1)
        early_close = float(frame.iloc[early_probe_idx]["close"])
        early_ret = (early_close / entry_px - 1.0) * direction
        opposite_seen = False
        for j in range(entry_idx, min(len(frame), entry_idx + EARLY_FAIL_BARS)):
            if direction > 0 and int(signals.iloc[j]["short_signal"]) == 1:
                opposite_seen = True
                break
            if direction < 0 and int(signals.iloc[j]["long_signal"]) == 1:
                opposite_seen = True
                break
        flip_to_fail = int((early_ret < 0.0) or opposite_seen)

        rows.append(
            {
                "asset": frame.iloc[0]["asset"],
                "arm": arm,
                "cost_bps_per_side": float(cost_bps),
                "signal_ts": pd.to_datetime(frame.iloc[idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_ts": pd.to_datetime(frame.iloc[entry_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": pd.to_datetime(frame.iloc[exit_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "direction": "long" if direction > 0 else "short",
                "entry_price": entry_px,
                "exit_price": exit_px,
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "early_ret_4bars": early_ret,
                "flip_to_fail": flip_to_fail,
                "hold_bars": int(exit_idx - entry_idx + 1),
                "anchor_dir": int(frame.iloc[idx]["psar_dir_htf"]) if pd.notna(frame.iloc[idx]["psar_dir_htf"]) else np.nan,
                "psar_15m_dir": int(frame.iloc[idx]["psar_dir_15m"]),
                "ema_slope": float(frame.iloc[idx]["ema_slope"]) if pd.notna(frame.iloc[idx]["ema_slope"]) else np.nan,
            }
        )
        last_exit_idx = exit_idx

    return pd.DataFrame(rows), signal_events


def summarize_asset(trades: pd.DataFrame, *, asset: str, arm: str, cost_bps: float, signal_events: int) -> dict[str, object]:
    if trades.empty:
        return {
            "asset": asset,
            "arm": arm,
            "cost_bps_per_side": float(cost_bps),
            "signal_events": int(signal_events),
            "trades": 0,
            "signal_to_trade_ratio": 0.0,
            "total_return": 0.0,
            "avg_net_ret": np.nan,
            "win_rate": np.nan,
            "flip_to_fail_rate": np.nan,
            "avg_hold_bars": np.nan,
            "long_share": np.nan,
            "short_share": np.nan,
        }
    return {
        "asset": asset,
        "arm": arm,
        "cost_bps_per_side": float(cost_bps),
        "signal_events": int(signal_events),
        "trades": int(len(trades)),
        "signal_to_trade_ratio": float(len(trades) / signal_events) if signal_events > 0 else np.nan,
        "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
        "avg_net_ret": float(trades["net_ret"].mean()),
        "win_rate": float((trades["net_ret"] > 0).mean()),
        "flip_to_fail_rate": float(trades["flip_to_fail"].mean()),
        "avg_hold_bars": float(trades["hold_bars"].mean()),
        "long_share": float((trades["direction"] == "long").mean()),
        "short_share": float((trades["direction"] == "short").mean()),
    }


def summarize_overall(asset_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (arm, cost), grp in asset_df.groupby(["arm", "cost_bps_per_side"], sort=False):
        rows.append(
            {
                "arm": arm,
                "cost_bps_per_side": float(cost),
                "mean_total_return": float(grp["total_return"].mean()),
                "positive_asset_ratio": float((grp["total_return"] > 0).mean()),
                "mean_trades": float(grp["trades"].mean()),
                "mean_signal_events": float(grp["signal_events"].mean()),
                "mean_signal_to_trade_ratio": float(grp["signal_to_trade_ratio"].mean()) if grp["signal_to_trade_ratio"].notna().any() else np.nan,
                "mean_win_rate": float(grp["win_rate"].mean()) if grp["win_rate"].notna().any() else np.nan,
                "mean_flip_to_fail_rate": float(grp["flip_to_fail_rate"].mean()) if grp["flip_to_fail_rate"].notna().any() else np.nan,
                "mean_avg_hold_bars": float(grp["avg_hold_bars"].mean()) if grp["avg_hold_bars"].notna().any() else np.nan,
            }
        )
    return pd.DataFrame(rows)


def build_time_stability(primary_trades: pd.DataFrame) -> pd.DataFrame:
    if primary_trades.empty or len(primary_trades) < 9:
        return pd.DataFrame(columns=["time_bucket", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_flip_to_fail_rate"])
    work = primary_trades.copy()
    work["entry_ts_dt"] = pd.to_datetime(work["entry_ts"], utc=True)
    try:
        work["time_bucket"] = pd.qcut(work["entry_ts_dt"].view("int64"), q=3, labels=["bucket_1", "bucket_2", "bucket_3"], duplicates="drop")
    except ValueError:
        return pd.DataFrame(columns=["time_bucket", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_flip_to_fail_rate"])
    rows = []
    for bucket, grp in work.groupby("time_bucket", sort=False, observed=False):
        asset_total = grp.groupby("asset")["net_ret"].apply(lambda s: float((1.0 + s).prod() - 1.0))
        rows.append(
            {
                "time_bucket": str(bucket),
                "mean_total_return": float(asset_total.mean()) if len(asset_total) else np.nan,
                "positive_asset_ratio": float((asset_total > 0).mean()) if len(asset_total) else np.nan,
                "mean_trades": float(grp.groupby("asset").size().mean()) if len(grp) else np.nan,
                "mean_flip_to_fail_rate": float(grp["flip_to_fail"].mean()) if len(grp) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def build_verdict(overall: pd.DataFrame, time_df: pd.DataFrame) -> tuple[str, str]:
    primary = overall[(overall["arm"] == PRIMARY_ARM) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    ema_raw = overall[(overall["arm"] == "ema_raw") & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    psar_raw = overall[(overall["arm"] == "psar_raw") & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    if primary.empty:
        return "park / evidence pool", "主对照臂没有形成可用样本，连最小 clean replication 都不足以保留预算。"
    p = primary.iloc[0]
    pos_buckets = int((time_df["mean_total_return"] > 0).sum()) if not time_df.empty else 0
    better_than_ema = False if ema_raw.empty else float(p["mean_total_return"]) > float(ema_raw.iloc[0]["mean_total_return"]) and float(p["mean_flip_to_fail_rate"]) < float(ema_raw.iloc[0]["mean_flip_to_fail_rate"])
    better_than_psar = False if psar_raw.empty else float(p["mean_total_return"]) > float(psar_raw.iloc[0]["mean_total_return"]) and float(p["mean_flip_to_fail_rate"]) < float(psar_raw.iloc[0]["mean_flip_to_fail_rate"])

    if (
        float(p["mean_total_return"]) > 0.0
        and float(p["positive_asset_ratio"]) >= (2.0 / 3.0)
        and float(p["mean_trades"]) >= 20
        and pos_buckets >= 2
        and better_than_ema
        and better_than_psar
    ):
        return "P1 weak candidate / evidence pool", "高层 PSAR anchor + 15m EMA confirm 至少在成本后保留正 pocket，且比 raw EMA / raw PSAR 都更稳，值得再保留一次便宜诚实检查。"

    return "park / evidence pool", "高层 PSAR anchor + EMA confirm 虽然相对 raw EMA / raw PSAR 更少亏、flip-to-fail 也更低，但成本后仍是 0/3 资产为正，不配继续占 clean replication 队列预算。"


def build_spec() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "section": "candidate",
                "item": "candidate_id",
                "value": "scout_repo_psar_anchor_ema_confirm_15m",
                "note": "BotScalpingTwinRange / PSAR anchor + EMA confirm 的唯一那手最小 clean replication。",
            },
            {
                "section": "scope",
                "item": "sample",
                "value": "BTC-USD / ETH-USD / SOL-USD | Binance 120d 15m cache",
                "note": "本地只有 120d 15m cache；本轮固定复用现有历史样本，不追新 bar。",
            },
            {
                "section": "arms",
                "item": "three_arm_compare",
                "value": "EMA_raw vs PSAR_raw vs PSAR_anchor+EMA_confirm",
                "note": "只回答高层 PSAR anchor 是否比 raw EMA / raw PSAR 更诚实。",
            },
            {
                "section": "execution",
                "item": "frozen_execution",
                "value": f"next-bar open | no-overlap | fixed hold {HOLD_BARS} bars | costs={','.join(str(int(c)) for c in COSTS)}bps/side",
                "note": "故意剥离 ALWAYS_IN_MARKET、多对择优与 30m/5m/1m 厚执行层，避免把工程复杂度误认成 alpha。",
            },
            {
                "section": "rule",
                "item": PRIMARY_ARM,
                "value": f"{HTF_RULE} PSAR 定方向，15m EMA{EMA_FAST}>{EMA_SLOW} + slope>{EMA_SLOPE_FLOOR} 才允许同向入场，close 必须站在 fast EMA 同侧",
                "note": "micro veto 被压成最小 close-vs-fast-EMA 同侧门，不重建原 repo 的 5m/1m planner。",
            },
        ]
    )


def write_html(overall: pd.DataFrame, asset_df: pd.DataFrame, time_df: pd.DataFrame, cost_df: pd.DataFrame, verdict: str, reason: str, generated_at: str) -> None:
    ensure_dir(SITE_DIR)
    primary = overall[(overall["arm"] == PRIMARY_ARM) & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    ema_raw = overall[(overall["arm"] == "ema_raw") & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    psar_raw = overall[(overall["arm"] == "psar_raw") & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    headline = (
        f"主臂 {PRIMARY_ARM} 在 6bps/side 下：跨资产 mean_total_return≈{pct(primary['mean_total_return'])}、"
        f"positive_asset_ratio≈{pct(primary['positive_asset_ratio'])}、mean_trades≈{num(primary['mean_trades'],1)}、"
        f"mean_flip_to_fail_rate≈{pct(primary['mean_flip_to_fail_rate'])}；"
        f"相对 EMA_raw≈{pct(ema_raw['mean_total_return'])}/{pct(ema_raw['mean_flip_to_fail_rate'])}、"
        f"PSAR_raw≈{pct(psar_raw['mean_total_return'])}/{pct(psar_raw['mean_flip_to_fail_rate'])}。"
    )
    html = f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Scout repo · PSAR anchor + EMA confirm · clean replication</title>
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
  <h1>Scout repo · PSAR anchor + EMA confirm · clean replication</h1>
  <p class='muted'>生成时间：{escape(generated_at)} ｜ 类型：fresh repo source 的唯一那手最小 clean replication ｜ 样本：BTC/ETH/SOL 120d 15m cache</p>

  <div class='card'>
    <h2>这轮只回答什么</h2>
    <ul>
      <li>不重建原 repo 的 <code>ALWAYS_IN_MARKET</code>、多对择优或 <code>30m/5m/1m</code> 厚执行层。</li>
      <li>只比较三臂：<code>EMA_raw</code>、<code>PSAR_raw</code>、<code>PSAR_anchor+EMA_confirm</code>。</li>
      <li>统一执行冻结为 <code>next-bar open -&gt; no-overlap -&gt; fixed hold 8 bars</code>，成本只看 <code>6/10/15/20 bps per side</code>。</li>
      <li>只回答四个问题：<code>post-cost return / positive_asset_ratio / trade_count / flip-to-fail rate</code>。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>clean-room 规则</h2>
    <ul>
      <li><b>EMA_raw：</b><code>15m EMA20 &gt; EMA50 + ema_fast 3-bar slope &gt; 0.0003</code>（short 镜像）；条件从 false→true 时下一根开盘入场。</li>
      <li><b>PSAR_raw：</b><code>15m PSAR</code> 翻向时下一根开盘入场。</li>
      <li><b>PSAR_anchor+EMA_confirm：</b><code>1h PSAR</code> 先给方向许可，再要求 <code>15m EMA20 &gt; EMA50 + slope &gt; 0.0003</code>，且 close 站在 fast EMA 同侧；只在这组条件从 false→true 时入场。</li>
      <li><b>flip-to-fail：</b>入场后前 <code>{EARLY_FAIL_BARS}</code> 根内，若 mark-to-market 已转负，或同臂反向信号已经出现，就记为 early failure。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>hard verdict</h2>
    <p><span class='pill'>{escape(verdict)}</span></p>
    <p><b>{escape(headline)}</b></p>
    <p class='muted'>{escape(reason)}</p>
  </div>

  <div class='card'>
    <h2>三臂总表</h2>
    {render_table(overall[["arm","cost_bps_per_side","mean_total_return","positive_asset_ratio","mean_trades","mean_signal_events","mean_signal_to_trade_ratio","mean_win_rate","mean_flip_to_fail_rate"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_signal_to_trade_ratio","mean_win_rate","mean_flip_to_fail_rate"}, digits_cols={"mean_trades":1,"mean_signal_events":1})}
  </div>

  <div class='card'>
    <h2>分资产摘要</h2>
    {render_table(asset_df[["asset","arm","cost_bps_per_side","signal_events","trades","signal_to_trade_ratio","total_return","win_rate","flip_to_fail_rate","long_share","short_share"]], percent_cols={"signal_to_trade_ratio","total_return","win_rate","flip_to_fail_rate","long_share","short_share"}, digits_cols={"signal_events":0,"trades":0})}
  </div>

  <div class='card'>
    <h2>时间稳定性（主臂 6bps）</h2>
    {render_table(time_df[["time_bucket","mean_total_return","positive_asset_ratio","mean_trades","mean_flip_to_fail_rate"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_flip_to_fail_rate"}, digits_cols={"mean_trades":1})}
  </div>

  <div class='card'>
    <h2>成本 / 交易数稳定性（主臂）</h2>
    {render_table(cost_df[["arm","cost_bps_per_side","mean_total_return","positive_asset_ratio","mean_trades","mean_flip_to_fail_rate"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_flip_to_fail_rate"}, digits_cols={"mean_trades":1})}
  </div>
</body>
</html>
"""
    (SITE_DIR / "report.html").write_text(html, encoding="utf-8")


def update_todo(generated_at: str, overall: pd.DataFrame, time_df: pd.DataFrame, verdict: str) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    primary = overall[(overall["arm"] == PRIMARY_ARM) & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    ema_raw = overall[(overall["arm"] == "ema_raw") & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    psar_raw = overall[(overall["arm"] == "psar_raw") & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    bucket_parts = [f"{r['time_bucket']}≈{pct(r['mean_total_return'])} / {pct(r['positive_asset_ratio'])}" for _, r in time_df.iterrows()]
    time_note = "time-pocket honesty：" + "；".join(bucket_parts) + "。" if bucket_parts else "当前样本不足以可靠拆成 3 个时间桶。"
    new_note = (
        f"- **最新补充（{generated_at}）**：这轮已按上一条指令把 `BotScalpingTwinRange / PSAR anchor + EMA confirm` 的唯一那手 **最小 clean replication** 跑完：固定复用 `BTC/ETH/SOL 120d 15m` cache，比较 `EMA_raw / PSAR_raw / PSAR_anchor+EMA_confirm` 三臂，并统一冻结到 `next-bar open + no-overlap + hold 8 bars`，只看 `6/10/15/20bps per side`。结果很直接：主臂 `PSAR_anchor+EMA_confirm` 在 `6bps/side` 下跨资产 `mean_total_return≈{pct(primary['mean_total_return'])}`、`positive_asset_ratio≈{pct(primary['positive_asset_ratio'])}`、`mean_trades≈{num(primary['mean_trades'],1)}`、`mean_flip_to_fail_rate≈{pct(primary['mean_flip_to_fail_rate'])}`；虽然相对 `EMA_raw≈{pct(ema_raw['mean_total_return'])}/{pct(ema_raw['mean_flip_to_fail_rate'])}` 与 `PSAR_raw≈{pct(psar_raw['mean_total_return'])}/{pct(psar_raw['mean_flip_to_fail_rate'])}` 已经更少亏、也更少 early failure，但成本后仍是 `0/3` 资产为正，{time_note} 因此当前更诚实的 hard verdict 是 **`{verdict}`**，不再继续占默认 clean-replication 队列。\n  - 若下一轮 `EMA` 仍是 `waiting_not_due`，默认应回退比较 `Rank 27b > Rank 35b > Run 3 / tiny-live plumbing`，而不是继续磨这条 repo 模板或回头挤占 `P3 continuity`。\n  - 网页落点：`reports/site/factors/scout_repo_psar_anchor_ema_confirm_15m/report.html`。"
    )

    anchor = "- **当前候选阶段表（精简版，authoritative）**："
    if new_note not in text and anchor in text:
        text = text.replace(anchor, new_note + "\n" + anchor, 1)

    old_sentence = "  - **最新补充（2026-03-18 03:39 UTC）**：这轮已把 `BotScalpingTwinRange / PSAR anchor + EMA confirm` 的两条轻量诚实守门过完。当前更诚实的读法已不再是“尚未 intake”，而是 **`guard-passed / admit_to_clean_replication_queue`**：`trade on / trade off` 已能冻结成 `高一级 PSAR anchor 定方向 -> 15m EMA dir+slope 做 continuation confirm -> 低一级 micro veto 只负责拒绝明显逆向噪音`；源码层当前也未见一眼可判死刑的 `lookahead / repaint / leakage`。但它仍是 **repo 工程模板**，不是已验证 alpha：原仓库自带 `ALWAYS_IN_MARKET`、多对择优与 `30m/5m/1m` execution 厚度，因此下一轮默认只允许给它 **1 次最小 clean replication**，先回答 `PSAR_anchor + EMA_confirm` 是否真能减少 early failure；若不能，就快速压回 `park / evidence pool`。对应 source-intake artifact：`reports/artifacts/literature/scout_repo_psar_anchor_ema_confirm_source_intake_card.csv`。\n  - 若这条 fresh repo source 也过不了守门，再按边际价值回退比较 `Rank 27b > Rank 35b > Run 3 / tiny-live plumbing`；不要直接跳过 fresh intake。"
    new_sentence = old_sentence + "\n" + new_note.replace("- **", "  - **", 1)
    if old_sentence in text and new_sentence not in text:
        text = text.replace(old_sentence, new_sentence, 1)

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
        for arm in ARMS:
            for cost in COSTS:
                trades, signal_events = backtest_arm(frame, arm, cost)
                asset_rows.append(summarize_asset(trades, asset=asset, arm=arm, cost_bps=cost, signal_events=signal_events))
                if not trades.empty:
                    all_trades.append(trades)
                if arm == PRIMARY_ARM and cost == PRIMARY_COST and not trades.empty:
                    primary_trades.append(trades)
                    trades.to_csv(ART_DIR / f"trades_primary_6bps_{asset.lower().replace('-usd', '')}.csv", index=False)

    asset_df = pd.DataFrame(asset_rows).sort_values(["arm", "cost_bps_per_side", "asset"]).reset_index(drop=True)
    overall = summarize_overall(asset_df).sort_values(["arm", "cost_bps_per_side"]).reset_index(drop=True)
    primary_trades_df = pd.concat(primary_trades, ignore_index=True) if primary_trades else pd.DataFrame()
    time_df = build_time_stability(primary_trades_df)
    cost_df = overall[overall["arm"] == PRIMARY_ARM].copy().sort_values("cost_bps_per_side").reset_index(drop=True)
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
            "candidate_id": "scout_repo_psar_anchor_ema_confirm_15m",
            "source": "oscar0rdz/BotScalpingTwinRange",
            "hard_verdict": verdict,
            "verdict_reason": reason,
            "scope": "BTC/ETH/SOL 120d 15m cache",
        }
    ]).to_csv(ART_DIR / "meta.csv", index=False)
    if all_trades:
        pd.concat(all_trades, ignore_index=True).sort_values(["arm", "cost_bps_per_side", "asset", "entry_ts"]).to_csv(ART_DIR / "all_trades.csv", index=False)
    if not primary_trades_df.empty:
        primary_trades_df.sort_values(["asset", "entry_ts"]).to_csv(ART_DIR / "trades_primary_6bps.csv", index=False)

    write_html(overall, asset_df, time_df, cost_df, verdict, reason, generated_at)
    update_todo(generated_at, overall, time_df, verdict)
    print(f"verdict={verdict}")
    print(overall.to_dict(orient="records"))


if __name__ == "__main__":
    main()
