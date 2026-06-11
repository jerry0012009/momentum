#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
import re
import time

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank52_trade_flow_imbalance_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank52_trade_flow_imbalance_15m"
READING_DIR = ROOT / "reports" / "site" / "reading" / "repo_scout"
TODO_PATH = ROOT / "docs" / "TODO.md"
AGG_CACHE_DIR = ART_DIR / "aggtrades_cache"
AGG_URL = "https://fapi.binance.com/fapi/v1/aggTrades"
REQ_TIMEOUT = 20
HOLD_BARS = 8
FALSE_LOOKAHEAD = 4
FLOW_WINDOW_MINUTES = 5
FLOW_BUCKET_MINUTES = 1
COSTS = [6.0, 10.0]
PRIMARY_COST = 6.0
SETUPS = ["ema_pullback_long", "breakdown_reclaim_short"]
VARIANTS = ["base", "same_direction_flow_gate", "strong_flow_gate", "opposite_flow_veto"]
PRIMARY_SETUP = "breakdown_reclaim_short"
PRIMARY_VARIANT = "opposite_flow_veto"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}


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
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def compute_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [
            (df["high"] - df["low"]).abs(),
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_bars(symbol, asset)
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema15"] = df["close"].ewm(span=15, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["vol_ma20"] = df["volume"].rolling(20, min_periods=20).mean()
    df["atr14"] = compute_atr(df)
    df["rolling_low20"] = df["low"].rolling(20, min_periods=20).min().shift(1)

    df["ema_pullback_long_signal"] = (
        (df["ema9"] > df["ema15"])
        & (df["ema_slope"] > 0.0003)
        & (df["close"] > df["ema9"])
        & (df["close"] > df["high"].shift(1))
        & (df["close"].shift(1) < df["ema9"].shift(1))
        & (df["close"].shift(2) < df["ema9"].shift(2))
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)

    low = df["rolling_low20"]
    atr = df["atr14"]
    df["breakdown_reclaim_short_signal"] = (
        low.notna()
        & (df["ema9"] < df["ema15"])
        & (df["ema_slope"] < -0.0003)
        & (df["close"].shift(1) > low.shift(1))
        & (df["close"].shift(2) > low.shift(2))
        & (df["close"] < low - 0.1 * atr)
        & (df["high"] <= low + 0.3 * atr)
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)
    return df


def direction_for_setup(setup: str) -> int:
    return 1 if setup == "ema_pullback_long" else -1


def setup_signal_col(setup: str) -> str:
    return f"{setup}_signal"


def flow_cache_path(symbol: str, signal_ts: pd.Timestamp) -> Path:
    stamp = signal_ts.strftime("%Y%m%dT%H%M%SZ")
    return AGG_CACHE_DIR / f"{symbol}_{stamp}.json"


def fetch_agg_window(symbol: str, signal_ts: pd.Timestamp) -> list[dict]:
    ensure_dir(AGG_CACHE_DIR)
    cache_path = flow_cache_path(symbol, signal_ts)
    if cache_path.exists():
        return json.loads(cache_path.read_text(encoding="utf-8"))

    end_ms = int(signal_ts.timestamp() * 1000)
    start_ms = int((signal_ts - timedelta(minutes=FLOW_WINDOW_MINUTES)).timestamp() * 1000)
    cursor = start_ms
    rows: list[dict] = []

    while cursor < end_ms:
        params = {
            "symbol": symbol,
            "startTime": cursor,
            "endTime": end_ms - 1,
            "limit": 1000,
        }
        resp = None
        for attempt in range(6):
            resp = requests.get(AGG_URL, params=params, timeout=REQ_TIMEOUT, headers={"User-Agent": "OpenClaw/1.0"})
            if resp.status_code != 429:
                break
            retry_after = resp.headers.get("Retry-After")
            wait_s = float(retry_after) if retry_after else min(20.0, 2 ** attempt)
            time.sleep(wait_s)
        assert resp is not None
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        rows.extend(batch)
        last_ts = int(batch[-1]["T"])
        if last_ts < cursor:
            break
        cursor = last_ts + 1
        if len(batch) < 1000:
            break
        time.sleep(0.2)

    cache_path.write_text(json.dumps(rows), encoding="utf-8")
    return rows


def summarize_flow(symbol: str, signal_ts: pd.Timestamp) -> dict[str, float | int | str]:
    rows = fetch_agg_window(symbol, signal_ts)
    if not rows:
        return {
            "flow_align": 0.0,
            "abs_flow_align": 0.0,
            "buy_sell_ratio": np.nan,
            "window_trades": 0,
            "window_notional": 0.0,
            "window_buy_vol": 0.0,
            "window_sell_vol": 0.0,
        }

    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["T"], unit="ms", utc=True)
    df["qty"] = pd.to_numeric(df["q"], errors="coerce").fillna(0.0)
    df["sell_aggressor"] = df["m"].astype(bool)
    df["buy_vol"] = np.where(df["sell_aggressor"], 0.0, df["qty"])
    df["sell_vol"] = np.where(df["sell_aggressor"], df["qty"], 0.0)
    bucket = df["timestamp"].dt.floor(f"{FLOW_BUCKET_MINUTES}min")
    minute = (
        df.assign(bucket=bucket)
        .groupby("bucket", dropna=False)
        .agg(buy_vol=("buy_vol", "sum"), sell_vol=("sell_vol", "sum"), trades=("timestamp", "count"))
        .reset_index()
    )
    minute["flow_imb"] = (minute["buy_vol"] - minute["sell_vol"]) / (minute["buy_vol"] + minute["sell_vol"] + 1e-8)
    buy_vol = float(minute["buy_vol"].sum())
    sell_vol = float(minute["sell_vol"].sum())
    flow_align = float(minute["flow_imb"].mean()) if not minute.empty else 0.0
    return {
        "flow_align": flow_align,
        "abs_flow_align": abs(flow_align),
        "buy_sell_ratio": float(buy_vol / sell_vol) if sell_vol > 0 else np.nan,
        "window_trades": int(minute["trades"].sum()) if not minute.empty else 0,
        "window_notional": float(buy_vol + sell_vol),
        "window_buy_vol": buy_vol,
        "window_sell_vol": sell_vol,
    }


def build_signal_frame(frame: pd.DataFrame, asset: str, symbol: str, setup: str) -> pd.DataFrame:
    sig = frame[setup_signal_col(setup)] & ~frame[setup_signal_col(setup)].shift(1).fillna(False)
    rows: list[dict[str, object]] = []
    last_exit = -1
    direction = direction_for_setup(setup)
    for idx in range(2, len(frame) - 2):
        if idx <= last_exit or not bool(sig.iloc[idx]):
            continue
        signal_ts = pd.to_datetime(frame.iloc[idx]["timestamp"], utc=True)
        flow = summarize_flow(symbol, signal_ts)
        signal_price = float(frame.iloc[idx]["close"])
        entry_idx = idx + 1
        rows.append(
            {
                "asset": asset,
                "symbol": symbol,
                "setup": setup,
                "direction": direction,
                "signal_idx": idx,
                "entry_idx": entry_idx,
                "signal_ts": signal_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "signal_price": signal_price,
                **flow,
            }
        )
        last_exit = entry_idx + HOLD_BARS - 1

    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out["strong_flow_threshold"] = (
        out.groupby(["asset", "setup"], dropna=False)["abs_flow_align"]
        .transform(lambda s: s.rolling(20, min_periods=10).median().shift(1))
    )
    out["same_direction"] = (out["direction"] * out["flow_align"]) > 0
    out["opposite_direction"] = (out["direction"] * out["flow_align"]) < 0
    out["strong_flow"] = out["same_direction"] & (out["abs_flow_align"] >= out["strong_flow_threshold"].fillna(np.inf))
    return out


def variant_allowed(row: pd.Series, variant: str) -> bool:
    if variant == "base":
        return True
    if variant == "same_direction_flow_gate":
        return bool(row["same_direction"])
    if variant == "strong_flow_gate":
        return bool(row["strong_flow"])
    if variant == "opposite_flow_veto":
        return not bool(row["opposite_direction"])
    raise ValueError(variant)


def build_trades(frame: pd.DataFrame, signals: pd.DataFrame, variant: str, cost_bps: float) -> tuple[pd.DataFrame, int]:
    if signals.empty:
        return pd.DataFrame(), 0
    rows: list[dict[str, object]] = []
    signal_events = 0
    cost_rate = float(cost_bps) / 10000.0
    direction = int(signals.iloc[0]["direction"])

    for _, sig in signals.iterrows():
        if not variant_allowed(sig, variant):
            continue
        signal_events += 1
        entry_idx = int(sig["entry_idx"])
        if entry_idx >= len(frame):
            continue
        exit_idx = min(len(frame) - 1, entry_idx + HOLD_BARS - 1)
        entry_px = float(frame.iloc[entry_idx]["open"])
        exit_px = float(frame.iloc[exit_idx]["close"])
        if direction == 1:
            gross_ret = exit_px / entry_px - 1.0
        else:
            gross_ret = entry_px / exit_px - 1.0
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0

        ft2_idx = min(len(frame) - 1, entry_idx + 1)
        ft4_idx = min(len(frame) - 1, entry_idx + 3)
        ft2 = (float(frame.iloc[ft2_idx]["close"]) / entry_px - 1.0) if direction == 1 else (entry_px / float(frame.iloc[ft2_idx]["close"]) - 1.0)
        ft4 = (float(frame.iloc[ft4_idx]["close"]) / entry_px - 1.0) if direction == 1 else (entry_px / float(frame.iloc[ft4_idx]["close"]) - 1.0)

        probe_last = min(len(frame) - 1, int(sig["signal_idx"]) + FALSE_LOOKAHEAD)
        false_flag = 0
        for j in range(int(sig["signal_idx"]) + 1, probe_last + 1):
            close_j = float(frame.iloc[j]["close"])
            if direction == 1 and close_j < float(sig["signal_price"]):
                false_flag = 1
                break
            if direction == -1 and close_j > float(sig["signal_price"]):
                false_flag = 1
                break

        rows.append(
            {
                "asset": sig["asset"],
                "setup": sig["setup"],
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "direction": direction,
                "signal_ts": sig["signal_ts"],
                "entry_ts": pd.to_datetime(frame.iloc[entry_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": pd.to_datetime(frame.iloc[exit_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_price": entry_px,
                "exit_price": exit_px,
                "signal_price": float(sig["signal_price"]),
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "follow_through_2bars": ft2,
                "follow_through_4bars": ft4,
                "false_break_or_hold_4bars": false_flag,
                "flow_align": float(sig["flow_align"]),
                "abs_flow_align": float(sig["abs_flow_align"]),
                "buy_sell_ratio": float(sig["buy_sell_ratio"]) if pd.notna(sig["buy_sell_ratio"]) else np.nan,
                "window_trades": int(sig["window_trades"]),
                "window_notional": float(sig["window_notional"]),
            }
        )
    return pd.DataFrame(rows), signal_events


def summarize_asset(trades: pd.DataFrame, *, asset: str, setup: str, variant: str, cost_bps: float, base_signals: int, admitted_signals: int) -> dict[str, object]:
    if trades.empty:
        return {
            "asset": asset,
            "setup": setup,
            "variant": variant,
            "cost_bps_per_side": float(cost_bps),
            "base_signals": int(base_signals),
            "admitted_signals": int(admitted_signals),
            "trades": 0,
            "trade_count_retention": np.nan,
            "signal_retention": np.nan,
            "total_return": 0.0,
            "avg_net_ret": np.nan,
            "win_rate": np.nan,
            "false_break_or_hold_4bars_rate": np.nan,
            "follow_through_2bars": np.nan,
            "follow_through_4bars": np.nan,
            "mean_abs_flow_align": np.nan,
        }
    return {
        "asset": asset,
        "setup": setup,
        "variant": variant,
        "cost_bps_per_side": float(cost_bps),
        "base_signals": int(base_signals),
        "admitted_signals": int(admitted_signals),
        "trades": int(len(trades)),
        "trade_count_retention": np.nan,
        "signal_retention": (admitted_signals / base_signals) if base_signals else np.nan,
        "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
        "avg_net_ret": float(trades["net_ret"].mean()),
        "win_rate": float((trades["net_ret"] > 0).mean()),
        "false_break_or_hold_4bars_rate": float(trades["false_break_or_hold_4bars"].mean()),
        "follow_through_2bars": float(trades["follow_through_2bars"].mean()),
        "follow_through_4bars": float(trades["follow_through_4bars"].mean()),
        "mean_abs_flow_align": float(trades["abs_flow_align"].mean()),
    }


def add_retentions(asset_df: pd.DataFrame) -> pd.DataFrame:
    out = asset_df.copy()
    for setup in sorted(out["setup"].unique()):
        for cost in sorted(out["cost_bps_per_side"].unique()):
            base_map = (
                out[(out["setup"] == setup) & (out["variant"] == "base") & (out["cost_bps_per_side"] == cost)]
                .set_index("asset")["trades"]
                .to_dict()
            )
            mask = (out["setup"] == setup) & (out["cost_bps_per_side"] == cost)
            out.loc[mask, "trade_count_retention"] = out.loc[mask].apply(
                lambda r: (r["trades"] / base_map.get(r["asset"], np.nan)) if base_map.get(r["asset"], 0) else np.nan,
                axis=1,
            )
    return out


def build_time_pockets(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["setup", "variant", "bucket", "mean_total_return", "positive_asset_ratio", "mean_trades"])
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
    grouped = df.groupby(["setup", "variant", "bucket", "asset"], dropna=False)
    for (setup, variant, bucket_name, asset), part in grouped:
        rows.append(
            {
                "setup": setup,
                "variant": variant,
                "bucket": bucket_name,
                "asset": asset,
                "total_return": float((1.0 + part["net_ret"]).prod() - 1.0),
                "trades": int(len(part)),
            }
        )
    tmp = pd.DataFrame(rows)
    return (
        tmp.groupby(["setup", "variant", "bucket"], dropna=False)
        .agg(
            mean_total_return=("total_return", "mean"),
            positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
            mean_trades=("trades", "mean"),
        )
        .reset_index()
        .sort_values(["setup", "variant", "bucket"])
        .reset_index(drop=True)
    )


def build_verdict(overall: pd.DataFrame) -> tuple[str, str, str]:
    primary = overall[(overall["setup"] == PRIMARY_SETUP) & (overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    secondary = overall[(overall["setup"] == "ema_pullback_long") & (overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    if primary.empty:
        return "park / evidence pool", "主读法没有形成可用样本。", "主读法没有产出有效结果，因此不能继续占默认 clean-replication 队列。"
    p = primary.iloc[0]
    s = secondary.iloc[0] if not secondary.empty else None
    headline = (
        f"`{PRIMARY_SETUP} + {PRIMARY_VARIANT} @ {int(PRIMARY_COST)}bps`：mean_total_return≈{pct(p['mean_total_return'])}、"
        f"positive_asset_ratio≈{pct(p['positive_asset_ratio'])}、mean_trades≈{num(p['mean_trades'],1)}、"
        f"mean_trade_count_retention≈{pct(p['mean_trade_count_retention'])}、mean_false_break_or_hold_4bars_rate≈{pct(p['mean_false_break_or_hold_4bars_rate'])}。"
    )
    primary_bad = (
        (float(p["mean_total_return"]) <= 0)
        or (float(p["positive_asset_ratio"]) < (2 / 3))
        or (float(p["mean_trade_count_retention"]) < 0.35)
    )
    secondary_bad = True
    if s is not None:
        secondary_bad = (
            (float(s["mean_total_return"]) <= 0)
            or (float(s["positive_asset_ratio"]) < (2 / 3))
            or (float(s["mean_trade_count_retention"]) < 0.35)
        )
    if primary_bad and secondary_bad:
        return (
            "park / evidence pool",
            headline,
            "这次最小 clean replication 更像在证明：trade-flow veto 有时能少亏或降假动作，但当前改善仍主要靠砍样本，跨资产也没有形成足够干净的正 pocket，不该继续冒充默认可升格候选。",
        )
    return (
        "P1 weak candidate / evidence pool",
        headline,
        "最小 clean replication 至少说明 trade-flow veto 不是纯噪音：它在当前两条 archetype 里有一条拿到了成本后更干净的 pocket，可以保留为便宜过滤层证据，但仍不够直接升 P2。",
    )


def build_html(overall: pd.DataFrame, asset_summary: pd.DataFrame, pockets: pd.DataFrame, verdict: str, headline: str, reason: str, generated_at: str) -> str:
    overall_view = overall[[
        "setup",
        "variant",
        "cost_bps_per_side",
        "mean_total_return",
        "positive_asset_ratio",
        "mean_trades",
        "mean_trade_count_retention",
        "mean_false_break_or_hold_4bars_rate",
        "mean_follow_through_2bars",
        "mean_follow_through_4bars",
    ]].copy()
    asset_view = asset_summary[asset_summary["cost_bps_per_side"] == PRIMARY_COST][[
        "asset",
        "setup",
        "variant",
        "trades",
        "trade_count_retention",
        "signal_retention",
        "total_return",
        "false_break_or_hold_4bars_rate",
    ]].copy()
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 52 · trade-flow imbalance veto clean replication</title>
  <style>
    body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width:1100px; margin:40px auto; padding:0 18px; line-height:1.72; color:#111827; background:#f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }}
    .muted {{ color:#6b7280; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th, td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    a {{ color:#2563eb; text-decoration:none; }}
  </style>
</head>
<body>
  <p><a href='../../reading/repo_scout/rank52_trade_flow_imbalance_source_intake.html'>← 返回 source intake</a></p>
  <h1>Rank 52 · trade-flow imbalance veto（minimal clean replication）</h1>
  <p class='muted'>生成时间：{escape(generated_at)} ｜ 固定 BTC/ETH/SOL 120d 15m cache；flow 只看 signal 前最后 {FLOW_WINDOW_MINUTES} 分钟 Binance Futures aggTrades 摘要；执行统一 <code>next-bar open + no-overlap + hold {HOLD_BARS} bars</code>。</p>

  <div class='card'>
    <h2>这轮只回答一个问题</h2>
    <p>当 `EMA = waiting_not_due` 时，Rank 52 只拿 1 次最小预算：<b>setup 前最后几分钟的主动买卖量失衡</b>，能不能在不过度砍样本的前提下，减少当前 desk archetype 的假动作？</p>
    <ul>
      <li><b>archetype A / ema_pullback_long：</b>EMA 顺势 + 两根回抽后重新放量上破前高。</li>
      <li><b>archetype B / breakdown_reclaim_short：</b>弱趋势下跌破 20-bar low，并保持在 breakdown 之下。</li>
      <li><b>变体：</b><code>base</code>、<code>same_direction_flow_gate</code>、<code>strong_flow_gate</code>、<code>opposite_flow_veto</code>。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>冻结规则</h2>
    <ul>
      <li>flow 只取 signal 发生前最后 {FLOW_WINDOW_MINUTES} 分钟的 <code>aggTrades</code>，按主动买/卖量汇总成 <code>flow_align=(buy-sell)/(buy+sell)</code>。</li>
      <li><code>same_direction_flow_gate</code>：long 要 flow_align &gt; 0，short 要 flow_align &lt; 0。</li>
      <li><code>strong_flow_gate</code>：在同向基础上，还要绝对 flow 强度不低于该资产该 archetype 最近 20 次 signal 的 rolling median。</li>
      <li><code>opposite_flow_veto</code>：只 veto 明显反向 flow；中性 flow 不强制砍掉。</li>
      <li>repo 名字虽然叫 order-book imbalance，但这里最诚实可复刻的是 <b>aggTrades trade-flow proxy</b>，不是完整 L2 深度失衡。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>hard verdict</h2>
    <p><span class='pill'>{escape(verdict)}</span></p>
    <p><b>{escape(headline)}</b></p>
    <p class='muted'>{escape(reason)}</p>
  </div>

  <div class='card'>
    <h2>overall summary</h2>
    {render_table(overall_view, percent_cols={'mean_total_return','positive_asset_ratio','mean_trade_count_retention','mean_false_break_or_hold_4bars_rate','mean_follow_through_2bars','mean_follow_through_4bars'}, digits_cols={'cost_bps_per_side':0,'mean_trades':1})}
  </div>

  <div class='card'>
    <h2>primary cost（6bps）asset-level</h2>
    {render_table(asset_view, percent_cols={'trade_count_retention','signal_retention','total_return','false_break_or_hold_4bars_rate'}, digits_cols={'trades':0})}
  </div>

  <div class='card'>
    <h2>time-pocket honesty</h2>
    {render_table(pockets, percent_cols={'mean_total_return','positive_asset_ratio'}, digits_cols={'mean_trades':1})}
  </div>
</body>
</html>
"""


def update_reading_report() -> None:
    report_path = READING_DIR / "report.html"
    if not report_path.exists():
        return
    text = report_path.read_text(encoding="utf-8")
    anchor = 'rank52_trade_flow_imbalance_source_intake.html">Rank 52 source intake</a>'
    if 'rank52_trade_flow_imbalance_clean_replication.html' in text or anchor not in text:
        return
    text = text.replace(anchor, anchor + ' ｜ <a href="rank52_trade_flow_imbalance_clean_replication.html">clean replication</a>', 1)
    report_path.write_text(text, encoding="utf-8")


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError("target block not found")
    return text.replace(old, new, 1)


def update_todo(overall: pd.DataFrame, verdict: str, generated_at: str) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    primary = overall[(overall["setup"] == PRIMARY_SETUP) & (overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    secondary = overall[(overall["setup"] == "ema_pullback_long") & (overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    secondary_text = ""
    if not secondary.empty:
        s = secondary.iloc[0]
        secondary_text = f"；对照 `ema_pullback_long + opposite_flow_veto≈{pct(s['mean_total_return'])} / retention≈{pct(s['mean_trade_count_retention'])} / false≈{pct(s['mean_false_break_or_hold_4bars_rate'])}`"
    insert_block = f"""- **最新补充（{generated_at}）**：这轮已按顶板顺序把 `Rank 52 / trade-flow imbalance veto` 的唯一那手 **最小 clean replication** 跑完：固定复用 `BTC/ETH/SOL 120d 15m` cache，只在两条最小 archetype（`ema_pullback_long`、`breakdown_reclaim_short`）上比较 `base`、`same_direction_flow_gate`、`strong_flow_gate`、`opposite_flow_veto` 四臂；flow 一律冻结到 **signal 前最后 5 分钟 aggTrades summary + next-bar open + no-overlap + hold 8 bars**。主读法 `breakdown_reclaim_short + opposite_flow_veto` 在 `6bps/side` 下跨资产 `mean_total_return≈{pct(primary['mean_total_return'])}`、`positive_asset_ratio≈{pct(primary['positive_asset_ratio'])}`、`mean_trades≈{num(primary['mean_trades'],1)}`、`mean_trade_count_retention≈{pct(primary['mean_trade_count_retention'])}`、`mean_false_break_or_hold_4bars_rate≈{pct(primary['mean_false_break_or_hold_4bars_rate'])}`{secondary_text}。
  - 当前更诚实的 hard verdict：**`Rank 52 / trade-flow imbalance veto = {verdict}`**。更直白地说：它现在已经不该再停在 source-intake queue；若后续继续认领，默认只能按这个 verdict 走，而不是继续磨 intake wording。
  - reader-facing 落点：`reports/site/factors/scout_rank52_trade_flow_imbalance_15m/report.html`、`reports/site/reading/repo_scout/rank52_trade_flow_imbalance_clean_replication.html`；artifact：`reports/artifacts/scout_rank52_trade_flow_imbalance_15m/overall_summary.csv`。
  - 排班含义：当前最新 `Next 3` 顺序应收紧为：**`Run 1 = EMA due-check only` -> `Run 2 = fresh paper/repo intake（按 7.10 先查 RECENT_PAPER_SEEDS / quant_digests / validated shortlist，只认领 1 条新的 5m / 15m crypto source）` -> `Run 3 = 若 fresh intake 也 exhausted，再比较 Rank 35b > Rank 16b > tiny-live plumbing`**。"""

    old_block = """- **最新补充（2026-03-18 09:49 UTC）**：这轮按 `Run 2 / fresh paper-repo intake` 重新比较了当前允许动作的边际价值：`Rank 52 / trade-flow imbalance veto`（来自 `2026-03-18 09:41 UTC` 新 quant digest，对 breakout / Fib / EMA-PSAR 三条现有主线都能复用的主动成交压力 veto） `>` `Rank 35b`（queue-only fallback） `>` `Run 3 / tiny-live plumbing`。
  - 为遵守“进入 queue-facing 层必须先拿顺序 Rank”的规则，这条新方向已冻结为 **`Rank 52 / trade-flow imbalance veto`**，source=`tsuithomas/crypto_research_order_book_imbalance`。
  - 当前最诚实的初始分级：`Rank 52 / trade-flow imbalance veto` → **`P1 weak candidate（source intake / 两条轻量诚实守门已过）`**。
  - 这轮 hard verdict：**`Rank 52 / trade-flow imbalance veto = guard-passed / admit_to_clean_replication_queue`**。`trade on / trade off` 已能冻结成：base setup 继续负责方向与价位，主动买卖量失衡只负责回答“这一下有没有真跟随盘”；若 flow 与方向相反或接近中性，则直接 veto。源码层当前也未见一眼可判死刑的 `lookahead / repaint / leakage`，但必须明确降级表达：repo 真正可复刻的是 **aggTrades trade-flow imbalance**，不是完整 L2 `order-book imbalance`；下一轮 clean replication 也必须统一冻结到 **setup 前最后 3~5 分钟 flow summary + next-bar open + no-overlap**，避免把 setup 后成交量倒灌回入场判断。
  - 对应 source-intake artifact：`reports/artifacts/literature/scout_rank52_trade_flow_imbalance_source_intake_card.csv`；reader-facing 页面：`reports/site/reading/repo_scout/rank52_trade_flow_imbalance_source_intake.html`。
  - 排班含义：当前最新 `Next 3` 顺序应收紧为：**`Run 1 = EMA due-check only` -> `Run 2 = Rank 52 / trade-flow imbalance veto minimal clean replication（仅当 EMA 仍 waiting_not_due）` -> `Run 3 = Rank 35b / tiny-live plumbing（仅当 Rank 52 也不合格）`**。"""
    text = replace_once(text, old_block, old_block + "\n" + insert_block)
    TODO_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_DIR)
    ensure_dir(AGG_CACHE_DIR)

    frames = {asset: build_frame(asset, symbol) for asset, symbol in ASSETS.items()}
    signal_tables: list[pd.DataFrame] = []
    for asset, symbol in ASSETS.items():
        frame = frames[asset]
        for setup in SETUPS:
            signal_tables.append(build_signal_frame(frame, asset, symbol, setup))
    all_signals = pd.concat([df for df in signal_tables if not df.empty], ignore_index=True) if signal_tables else pd.DataFrame()
    if all_signals.empty:
        raise RuntimeError("no signals formed for Rank 52 clean replication")
    all_signals.to_csv(ART_DIR / "signal_windows_with_flow.csv", index=False)

    trade_frames: list[pd.DataFrame] = []
    asset_rows: list[dict[str, object]] = []

    for asset, symbol in ASSETS.items():
        frame = frames[asset]
        for setup in SETUPS:
            sigs = all_signals[(all_signals["asset"] == asset) & (all_signals["setup"] == setup)].copy().reset_index(drop=True)
            base_signals = int(len(sigs))
            for variant in VARIANTS:
                admitted_count = int(sigs.apply(lambda r: variant_allowed(r, variant), axis=1).sum()) if not sigs.empty else 0
                for cost in COSTS:
                    trades, signal_events = build_trades(frame, sigs, variant, cost)
                    if not trades.empty:
                        trade_frames.append(trades)
                    asset_rows.append(
                        summarize_asset(
                            trades,
                            asset=asset,
                            setup=setup,
                            variant=variant,
                            cost_bps=cost,
                            base_signals=base_signals,
                            admitted_signals=signal_events,
                        )
                    )

    all_trades = pd.concat(trade_frames, ignore_index=True) if trade_frames else pd.DataFrame()
    if not all_trades.empty:
        all_trades.to_csv(ART_DIR / "trade_log.csv", index=False)

    asset_summary = add_retentions(pd.DataFrame(asset_rows)).sort_values(["setup", "variant", "cost_bps_per_side", "asset"]).reset_index(drop=True)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)

    overall = (
        asset_summary.groupby(["setup", "variant", "cost_bps_per_side"], dropna=False)
        .agg(
            mean_total_return=("total_return", "mean"),
            positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
            mean_trades=("trades", "mean"),
            mean_trade_count_retention=("trade_count_retention", "mean"),
            mean_signal_retention=("signal_retention", "mean"),
            mean_false_break_or_hold_4bars_rate=("false_break_or_hold_4bars_rate", "mean"),
            mean_follow_through_2bars=("follow_through_2bars", "mean"),
            mean_follow_through_4bars=("follow_through_4bars", "mean"),
            mean_avg_net_ret=("avg_net_ret", "mean"),
        )
        .reset_index()
        .sort_values(["setup", "variant", "cost_bps_per_side"])
        .reset_index(drop=True)
    )
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)

    pockets = build_time_pockets(all_trades)
    pockets.to_csv(ART_DIR / "time_pocket_summary.csv", index=False)

    verdict, headline, reason = build_verdict(overall)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    meta = pd.DataFrame([
        {
            "generated_at_utc": generated_at,
            "candidate_id": "rank52_trade_flow_imbalance_15m",
            "hard_verdict": verdict,
            "headline": headline,
            "reason": reason,
        }
    ])
    meta.to_csv(ART_DIR / "meta.csv", index=False)

    html = build_html(overall, asset_summary, pockets, verdict, headline, reason, generated_at)
    (SITE_DIR / "report.html").write_text(html, encoding="utf-8")
    (READING_DIR / "rank52_trade_flow_imbalance_clean_replication.html").write_text(html, encoding="utf-8")

    update_reading_report()
    update_todo(overall, verdict, generated_at)

    print(f"verdict={verdict}")
    print(headline)


if __name__ == "__main__":
    main()
