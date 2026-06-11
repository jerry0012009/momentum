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
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank35_vwap_pullback_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank35_vwap_pullback_15m"
READING_DIR = ROOT / "reports" / "site" / "reading" / "trendline_alpha_scout"
READING_REPORT = READING_DIR / "report.html"
TODO_PATH = ROOT / "docs" / "TODO.md"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
ANCHORS = ["utc_day", "funding_8h"]
VARIANTS = [
    "baseline_higher_tf_bias",
    "bias_plus_rsi_pullback",
    "bias_plus_vwap_reclaim",
    "combo_long_only",
]
PRIMARY_VARIANT = "combo_long_only"
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0, 20.0]
HOLD_BARS = 8
PULLBACK_LOOKBACK = 8
RSI_PERIOD = 14
RSI_PULLBACK_LEVEL = 35.0
RSI_RECLAIM_LEVEL = 40.0


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


def rsi(series: pd.Series, period: int = RSI_PERIOD) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    out = 100 - (100 / (1 + rs))
    return out.fillna(50.0)


def load_cached_bars(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def compute_anchor_vwap(df: pd.DataFrame, anchor: str) -> pd.Series:
    if anchor == "utc_day":
        bucket = df["timestamp"].dt.strftime("%Y-%m-%d")
    elif anchor == "funding_8h":
        hours = (df["timestamp"].dt.hour // 8) * 8
        bucket = df["timestamp"].dt.strftime("%Y-%m-%d") + "_" + hours.astype(str).str.zfill(2)
    else:
        raise ValueError(anchor)
    typical = (df["high"] + df["low"] + df["close"]) / 3.0
    pv = typical * df["volume"]
    cum_pv = pv.groupby(bucket).cumsum()
    cum_vol = df["volume"].groupby(bucket).cumsum().replace(0, np.nan)
    return cum_pv / cum_vol


def build_frame(asset: str, symbol: str, anchor: str) -> pd.DataFrame:
    df = load_cached_bars(symbol, asset)
    df["ema20_15m"] = ema(df["close"], 20)
    df["rsi14"] = rsi(df["close"])

    hourly = df.set_index("timestamp")["close"].resample("1h").last().dropna().to_frame("close_1h").reset_index()
    hourly["ema20_1h"] = ema(hourly["close_1h"], 20)
    hourly["ema50_1h"] = ema(hourly["close_1h"], 50)
    hourly["bias_1h"] = (hourly["close_1h"] > hourly["ema20_1h"]) & (hourly["ema20_1h"] > hourly["ema50_1h"])

    fourh = df.set_index("timestamp")["close"].resample("4h").last().dropna().to_frame("close_4h").reset_index()
    fourh["ema20_4h"] = ema(fourh["close_4h"], 20)
    fourh["bias_4h"] = fourh["close_4h"] > fourh["ema20_4h"]

    df = pd.merge_asof(df.sort_values("timestamp"), hourly[["timestamp", "bias_1h"]].sort_values("timestamp"), on="timestamp", direction="backward")
    df = pd.merge_asof(df.sort_values("timestamp"), fourh[["timestamp", "bias_4h"]].sort_values("timestamp"), on="timestamp", direction="backward")
    df["higher_tf_bias"] = (df["bias_1h"].fillna(False) & df["bias_4h"].fillna(False)).astype(bool)
    df["vwap"] = compute_anchor_vwap(df, anchor)
    df["anchor"] = anchor

    recent_rsi_min = df["rsi14"].rolling(PULLBACK_LOOKBACK, min_periods=1).min().shift(1)
    recent_vwap_gap_min = ((df["close"] / df["vwap"]) - 1.0).rolling(PULLBACK_LOOKBACK, min_periods=1).min().shift(1)

    df["signal_baseline_higher_tf_bias"] = (
        df["higher_tf_bias"]
        & (~df["higher_tf_bias"].shift(1).fillna(False))
    )
    df["signal_bias_plus_rsi_pullback"] = (
        df["higher_tf_bias"]
        & (recent_rsi_min <= RSI_PULLBACK_LEVEL)
        & (df["rsi14"].shift(1) < RSI_RECLAIM_LEVEL)
        & (df["rsi14"] >= RSI_RECLAIM_LEVEL)
    )
    df["signal_bias_plus_vwap_reclaim"] = (
        df["higher_tf_bias"]
        & (recent_vwap_gap_min < 0)
        & (df["close"].shift(1) <= df["vwap"].shift(1))
        & (df["close"] > df["vwap"])
    )
    df["signal_combo_long_only"] = (
        df["higher_tf_bias"]
        & (recent_rsi_min <= RSI_PULLBACK_LEVEL)
        & (df["rsi14"].shift(1) < RSI_RECLAIM_LEVEL)
        & (df["rsi14"] >= RSI_RECLAIM_LEVEL)
        & (recent_vwap_gap_min < 0)
        & (df["close"].shift(1) <= df["vwap"].shift(1))
        & (df["close"] > df["vwap"])
    )
    return df


def build_trades(frame: pd.DataFrame, asset: str, anchor: str, variant: str, cost_bps: float) -> tuple[pd.DataFrame, float]:
    rows: list[dict[str, object]] = []
    last_exit = -1
    cost_rate = cost_bps / 10000.0
    signal_col = f"signal_{variant}"
    eligible = int(frame["higher_tf_bias"].sum())
    signals_seen = 0
    for idx in range(1, len(frame) - HOLD_BARS - 1):
        if idx <= last_exit:
            continue
        if not bool(frame.iloc[idx][signal_col]):
            continue
        signals_seen += 1
        entry_idx = idx + 1
        exit_idx = min(entry_idx + HOLD_BARS - 1, len(frame) - 1)
        entry_price = float(frame.iloc[entry_idx]["open"])
        exit_price = float(frame.iloc[exit_idx]["close"])
        if not (math.isfinite(entry_price) and math.isfinite(exit_price) and entry_price > 0 and exit_price > 0):
            continue
        gross_ret = exit_price / entry_price - 1.0
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
        rows.append(
            {
                "asset": asset,
                "anchor": anchor,
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "event_ts": pd.to_datetime(frame.iloc[idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_ts": pd.to_datetime(frame.iloc[entry_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": pd.to_datetime(frame.iloc[exit_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_price": entry_price,
                "exit_price": exit_price,
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "rsi14": float(frame.iloc[idx]["rsi14"]),
                "vwap_gap": float(frame.iloc[idx]["close"] / frame.iloc[idx]["vwap"] - 1.0) if pd.notna(frame.iloc[idx]["vwap"]) and frame.iloc[idx]["vwap"] else np.nan,
            }
        )
        last_exit = exit_idx
    no_trade_ratio = 1.0 if eligible == 0 else max(0.0, 1.0 - (signals_seen / eligible))
    return pd.DataFrame(rows), no_trade_ratio


def summarize_asset(trades: pd.DataFrame, asset: str, anchor: str, variant: str, cost: float, no_trade_ratio: float) -> dict[str, object]:
    if trades.empty:
        return {
            "asset": asset,
            "anchor": anchor,
            "variant": variant,
            "cost_bps_per_side": float(cost),
            "trades": 0,
            "total_return": 0.0,
            "avg_net_ret": np.nan,
            "win_rate": np.nan,
            "no_trade_ratio": float(no_trade_ratio),
        }
    return {
        "asset": asset,
        "anchor": anchor,
        "variant": variant,
        "cost_bps_per_side": float(cost),
        "trades": int(len(trades)),
        "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
        "avg_net_ret": float(trades["net_ret"].mean()),
        "win_rate": float((trades["net_ret"] > 0).mean()),
        "no_trade_ratio": float(no_trade_ratio),
    }


def summarize_overall(asset_summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (anchor, variant, cost), grp in asset_summary.groupby(["anchor", "variant", "cost_bps_per_side"], sort=False):
        total_returns = grp["total_return"].to_numpy(dtype=float)
        rows.append(
            {
                "anchor": anchor,
                "variant": variant,
                "cost_bps_per_side": float(cost),
                "mean_total_return": float(np.nanmean(total_returns)) if len(total_returns) else np.nan,
                "positive_asset_ratio": float(np.nanmean(total_returns > 0)) if len(total_returns) else np.nan,
                "mean_trades": float(grp["trades"].mean()),
                "mean_no_trade_ratio": float(grp["no_trade_ratio"].mean()),
                "mean_win_rate": float(grp["win_rate"].mean()),
            }
        )
    return pd.DataFrame(rows)


def build_time_buckets(primary_trades: pd.DataFrame) -> pd.DataFrame:
    if primary_trades.empty:
        return pd.DataFrame()
    df = primary_trades.copy()
    df["entry_ts"] = pd.to_datetime(df["entry_ts"], utc=True)
    out = []
    for anchor, grp in df.groupby("anchor", sort=False):
        grp = grp.sort_values("entry_ts").reset_index(drop=True)
        if len(grp) < 6:
            continue
        grp["time_bucket"] = pd.qcut(grp.index + 1, q=3, labels=["bucket_1", "bucket_2", "bucket_3"])
        for bucket, sub in grp.groupby("time_bucket", sort=False):
            total = np.array([(1.0 + r) for r in sub["net_ret"].to_numpy(dtype=float)])
            out.append(
                {
                    "anchor": anchor,
                    "time_bucket": str(bucket),
                    "mean_total_return": float(total.prod() - 1.0),
                    "trades": int(len(sub)),
                    "win_rate": float((sub["net_ret"] > 0).mean()),
                }
            )
    return pd.DataFrame(out)


def build_verdict(overall: pd.DataFrame, time_buckets: pd.DataFrame) -> tuple[str, str]:
    focus = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)].copy()
    if focus.empty:
        return "park / evidence pool", "主变体没有形成可读样本，连最小 clean replication 都不足以支撑继续。"
    focus = focus.sort_values("anchor").reset_index(drop=True)
    all_positive = bool((focus["mean_total_return"] > 0).all())
    all_cross_asset = bool((focus["positive_asset_ratio"] >= (2.0 / 3.0)).all())
    all_trades = bool((focus["mean_trades"] >= 12).all())
    all_no_trade = bool((focus["mean_no_trade_ratio"] <= 0.985).all())
    bucket_ok = True
    if not time_buckets.empty:
        positives = time_buckets.groupby("anchor")["mean_total_return"].apply(lambda s: int((s > 0).sum()))
        bucket_ok = bool((positives >= 2).all())
    spread = float(focus["mean_total_return"].max() - focus["mean_total_return"].min())
    if all_positive and all_cross_asset and all_trades and all_no_trade and bucket_ok and spread <= 0.08:
        return "P1 weak candidate / evidence pool", "最小 clean replication 至少没直接塌掉：主变体在两个 VWAP anchor 下都保持成本后为正、跨资产不只剩单腿，而且 time-pocket 也不是只靠单一热像素。"
    best = focus.sort_values("mean_total_return", ascending=False).iloc[0]
    worst = focus.sort_values("mean_total_return", ascending=True).iloc[0]
    return (
        "park / evidence pool",
        f"主变体 `{PRIMARY_VARIANT}` 对 VWAP anchor 很敏感：最强的 `{best['anchor']}` 只有 mean_total_return≈{pct(best['mean_total_return'])}、positive_asset_ratio≈{pct(best['positive_asset_ratio'])}，而 `{worst['anchor']}` 已掉到 mean_total_return≈{pct(worst['mean_total_return'])}、positive_asset_ratio≈{pct(worst['positive_asset_ratio'])}；这说明当前 edge 还不够诚实，先压回 park 更稳。",
    )


def update_reading_report(verdict: str, generated_at: str, overall: pd.DataFrame) -> None:
    if not READING_REPORT.exists():
        return
    text = READING_REPORT.read_text(encoding="utf-8")
    old = '''<div class="card">
  <h2>Rank 35 · VWAP pullback + trend-template qualifier：fresh intake</h2>
  <p>在 <code>Rank 34</code> 已按最小 clean replication 诚实压回 <code>park</code> 之后，这轮没有重开旧 park，也没有继续补 P3 近义 wiring，而是切到一条新的 long-only pullback / reclaim 候补：<a href="rank35_vwap_pullback_source_intake.html">Rank 35 source intake</a>。</p>
  <ul>
    <li><b>为什么轮到它：</b><code>EMA</code> 继续处于 <code>waiting_not_due</code>；<code>Rank 17 / Rank 2 / Rank 29</code> 仍无真实 <code>append/review</code> need；<code>Rank 30~34</code> 都已完成当前允许动作并 park。</li>
    <li><b>来源边界：</b>来自开源脚本 <code>Advanced VWAP_Pullback Strategy_Trend-Template Qualifier</code>，但只吸收其中的 <code>higher-tf trend qualifier + RSI pullback + VWAP reclaim</code> 内核，不直接照搬股票式 <code>52-week / IBD RS</code> 语境。</li>
    <li><b>trade on：</b><code>higher_tf trend-template proxy = true</code>，最近出现一次 RSI pullback / oversold，然后短均线重新上穿 session VWAP；默认只做 <code>long-only</code>。</li>
    <li><b>当前 verdict：</b><code>fresh intake only / pending Stage A + clean replication</code>。</li>
    <li><b>下一轮约束：</b>若继续认领，默认只允许复用 <code>BTC/ETH/SOL 120d 15m</code> cache 做 1 次最小 clean replication，比较 <code>baseline_higher_tf_bias / bias_plus_rsi_pullback / bias_plus_vwap_reclaim / combo_long_only</code>，先回答 <code>post_cost_return / trade_count / time-pocket honesty / anchor sensitivity</code>。</li>
    <li><b>artifact：</b><code>reports/artifacts/literature/scout_rank35_vwap_pullback_source_intake_card.csv</code></li>
  </ul>
  <p class="muted">直白一点：这轮只是把下一条还值得花最小预算验证的来源压成 intake 卡；不是宣称它已经通过 clean replication，更不是提前给 paper candidate。</p>
</div>'''
    focus = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)].copy().sort_values("anchor")
    anchor_bits = []
    for _, row in focus.iterrows():
        anchor_bits.append(f"{row['anchor']} = <code>{pct(row['mean_total_return'])} / {pct(row['positive_asset_ratio'])} / {num(row['mean_trades'],1)}</code>")
    anchor_text = "；".join(anchor_bits) if anchor_bits else "-"
    new = f'''<div class="card">
  <h2>Rank 35 · VWAP pullback + trend-template qualifier：clean replication</h2>
  <p>这轮按 board 约束把 <code>Rank 35</code> 从 source intake 推到 1 次最小 clean replication：<a href="rank35_vwap_pullback_source_intake.html">source intake</a> ｜ <a href="rank35_vwap_pullback_clean_replication.html">clean replication</a>。</p>
  <ul>
    <li><b>只回答了什么：</b>固定复用 <code>BTC/ETH/SOL 120d 15m</code> cache，只比较 <code>baseline_higher_tf_bias / bias_plus_rsi_pullback / bias_plus_vwap_reclaim / combo_long_only</code>，先回答 <code>post_cost_return / trade_count / time-pocket honesty / anchor sensitivity</code>。</li>
    <li><b>冻结口径：</b>higher-tf trend proxy 固定为 <code>1h close>EMA20>EMA50</code> 且 <code>4h close>EMA20</code>；VWAP anchor 只比较 <code>utc_day</code> 与 <code>funding_8h</code>，不事后挑更好看的版本。</li>
    <li><b>主变体：</b><code>{PRIMARY_VARIANT}</code>；6bps/side 下 anchor 摘要（格式 = mean_total_return / positive_asset_ratio / mean_trades）：{anchor_text}。</li>
    <li><b>当前 verdict：</b><code>{escape(verdict)}</code>。</li>
    <li><b>为什么没更激进：</b>这轮最重要的诚实问题不是“再补多少说明页”，而是 <code>VWAP anchor</code> 一改，结论会不会翻脸；当前结果更适合作为 anchor-sensitive evidence，而不是直接升到 paper candidate。</li>
    <li><b>时间戳：</b>{escape(generated_at)}</li>
  </ul>
</div>'''
    if old in text:
        text = text.replace(old, new, 1)
    else:
        text = text.replace('rank35_vwap_pullback_source_intake.html">Rank 35 source intake</a>', 'rank35_vwap_pullback_source_intake.html">Rank 35 source intake</a> ｜ <a href="rank35_vwap_pullback_clean_replication.html">clean replication</a>', 1)
    READING_REPORT.write_text(text, encoding="utf-8")


def update_todo(verdict: str, generated_at: str, overall: pd.DataFrame, time_buckets: pd.DataFrame) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    focus = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)].copy().sort_values("anchor")
    stats_parts = []
    for _, row in focus.iterrows():
        stats_parts.append(
            f"`{row['anchor']} -> mean_total_return≈{pct(row['mean_total_return'])} / positive_asset_ratio≈{pct(row['positive_asset_ratio'])} / mean_trades≈{num(row['mean_trades'],1)}`"
        )
    stats = "；".join(stats_parts) if stats_parts else "主变体没有形成可用样本。"
    if time_buckets.empty:
        time_note = "time-pocket honesty 当前样本偏薄；这本身也不支持继续升格。"
    else:
        bucket_parts = []
        for _, row in time_buckets.iterrows():
            bucket_parts.append(f"{row['anchor']}/{row['time_bucket']}≈{pct(row['mean_total_return'])} / trades≈{int(row['trades'])}")
        time_note = "time-pocket honesty：" + "；".join(bucket_parts) + "。"

    old_summary = "**因此当前默认节奏应改为：`Paper Seat / EMA` 继续按 `waiting_not_due` 处理；`Rank 35` 当前状态 = `fresh intake only / pending Stage A + clean replication`。若 `Rank 29 / Rank 17 / Rank 2` 仍无真实 append/review row，则默认应先把 `Rank 35` 推进到 1 次最小 clean replication，而不是重开已 park 的 `Rank 30 / Rank 31 / Rank 32 / Rank 33 / Rank 34`。**"
    if verdict.startswith("P1"):
        new_summary = "**因此当前默认节奏应改为：`Paper Seat / EMA` 继续按 `waiting_not_due` 处理；`Rank 35` 的最小 clean replication 已如实落地并进入 `P1 weak candidate`。若 `Rank 29 / Rank 17 / Rank 2` 仍无真实 append/review row，则下一轮默认只允许给它那唯一 1 次便宜诚实检查预算；若这次检查也不能改变层级，就应压回 `park / evidence pool`。**"
    else:
        new_summary = "**因此当前默认节奏应改为：`Paper Seat / EMA` 继续按 `waiting_not_due` 处理；`Rank 35` 的最小 clean replication 已如实落地且当前维持 `park / evidence pool`。若 `Rank 29 / Rank 17 / Rank 2` 仍无真实 append/review row，则下一轮默认应回到新的 `paper / repo based 5m / 15m crypto` fresh intake，而不是继续重开已 park 的 `Rank 30 / Rank 31 / Rank 32 / Rank 33 / Rank 34`。**"
    if old_summary in text:
        text = text.replace(old_summary, new_summary, 1)

    old_run2 = "2z. `Rank 35 VWAP pullback + trend-template qualifier`：当前已完成 source intake，状态=`fresh intake only / pending Stage A + clean replication`。来源是开源脚本 `Advanced VWAP_Pullback Strategy_Trend-Template Qualifier`，但这轮只保留 `higher-tf trend qualifier + RSI pullback + VWAP reclaim` 的 long-only 内核，不直接搬股票式 `52-week / IBD RS` 语境。若继续认领，默认只允许复用 `BTC/ETH/SOL 120d 15m` cache 做 1 次最小 clean replication，比较 `baseline_higher_tf_bias / bias_plus_rsi_pullback / bias_plus_vwap_reclaim / combo_long_only`，先回答 `post_cost_return / trade_count / time-pocket honesty / anchor sensitivity`。网页落点：`reports/site/reading/trendline_alpha_scout/rank35_vwap_pullback_source_intake.html`。"
    new_run2 = (
        f"2z. `Rank 35 VWAP pullback + trend-template qualifier`：已完成 **fresh source intake -> 最小 clean replication**，固定复用 `BTC/ETH/SOL 120d 15m` cache；只比较 `baseline_higher_tf_bias`、`bias_plus_rsi_pullback`、`bias_plus_vwap_reclaim`、`combo_long_only`，不追新 bar，也不扩成完整 stability pack。"
        " 冻结后的 clean-room 规则：`baseline_higher_tf_bias = higher-tf trend proxy 从 false->true 时才允许 long`；`bias_plus_rsi_pullback = bias 保持为真，且 RSI14 先跌入 pullback 区、再重新站回 40 上方`；`bias_plus_vwap_reclaim = bias 保持为真，且价格在 pullback 后重新站回冻结 VWAP anchor`；`combo_long_only = RSI reclaim 与 VWAP reclaim 同时成立`。"
        f" 当前最诚实的主证据：主变体 `{PRIMARY_VARIANT}` 在 `6bps/side` 下的 anchor summary 为：{stats} {time_note}"
        f" **最新补充（{generated_at}）**：这轮最小 clean replication 的 hard verdict 是 **`{verdict}`**。更直白地说：这条线当前最关键的诚实门槛就是 `VWAP anchor sensitivity`；如果换个 anchor 结论就明显变形，就还不配直接进 `paper candidate pool`。"
        " 网页落点：`reports/site/factors/scout_rank35_vwap_pullback_15m/report.html`、`reports/site/reading/trendline_alpha_scout/rank35_vwap_pullback_source_intake.html`。"
    )
    if old_run2 in text:
        text = text.replace(old_run2, new_run2, 1)

    old_rank_block = "35. `Rank 35 VWAP pullback + trend-template qualifier`（open-source script `Advanced VWAP_Pullback Strategy_Trend-Template Qualifier`）→ **`fresh intake only / pending Stage A + clean replication`**\n    - 本轮只做 `source intake`，没有偷跑 clean replication。当前之所以轮到它，不是因为它证据已经很强，而是因为 `EMA` 仍是 `waiting_not_due`、`Rank 17 / Rank 2 / Rank 29` 没有新的真实 `append/review need`，且 `Rank 30~34` 都已完成当前允许动作并 park。\n    - 当前保留的 clean-room 内核是：`higher-tf trend qualifier + RSI pullback + VWAP reclaim`，并且默认 **只做 long-only**；不直接照搬原脚本里股票语境更重的 `52-week high/low`、`IBD relative strength`、`Minervini stock template` 全套资格筛选。\n    - 冻结后的 intake 规则：`trade on = higher_tf trend-template proxy 为真，最近 N 根出现 RSI oversold / weak-pullback，然后短均线重新上穿 session VWAP`；`trade off = higher_tf bias 缺失或反向、最近并无 pullback/oversold、短均线没有重新站回 VWAP、或 reclaim 很快跌回 VWAP 下方`。\n    - 当前最重要的诚实边界：对 15m crypto 来说，`VWAP anchor`（UTC-day / session window）与 `higher-tf trend proxy` 都必须提前冻结，不能事后挑最好看的版本；原脚本的股票式 qualifier 也不能原样搬进来冒充“同一规则”。\n    - 因此当前 hard verdict 仍只是 **`fresh intake only / pending Stage A + clean replication`**：若下一轮继续认领，默认只允许复用 `BTC/ETH/SOL 120d 15m` cache，比较 `baseline_higher_tf_bias / bias_plus_rsi_pullback / bias_plus_vwap_reclaim / combo_long_only` 这 4 档最小规则，先回答 `post_cost_return / trade_count / time-pocket honesty / anchor sensitivity`；若 anchor 或 qualifier 一改就失真，直接 `park`。\n    - 网页落点：`reports/site/reading/trendline_alpha_scout/rank35_vwap_pullback_source_intake.html`。"
    new_rank_block = (
        f"35. `Rank 35 VWAP pullback + trend-template qualifier`（open-source script `Advanced VWAP_Pullback Strategy_Trend-Template Qualifier`）→ **`{verdict}`**\n"
        "    - 已完成 `fresh source intake -> 最小 clean replication`，固定复用 `BTC/ETH/SOL 120d 15m` cache；只比较 `baseline_higher_tf_bias`、`bias_plus_rsi_pullback`、`bias_plus_vwap_reclaim`、`combo_long_only`，不追新 bar，也不扩成完整 stability pack。\n"
        "    - 冻结后的 clean-room 规则：`baseline_higher_tf_bias = higher-tf trend proxy 从 false->true 时才允许 long`；`bias_plus_rsi_pullback = bias 保持为真，且 RSI14 先跌入 pullback 区、再重新站回 40 上方`；`bias_plus_vwap_reclaim = bias 保持为真，且价格在 pullback 后重新站回冻结 VWAP anchor`；`combo_long_only = RSI reclaim 与 VWAP reclaim 同时成立`。\n"
        f"    - 当前最诚实的主证据：主变体 `{PRIMARY_VARIANT}` 在 `6bps/side` 下的 anchor summary 为：{stats}\n"
        f"    - {time_note}\n"
        f"    - **最新补充（{generated_at}）**：这轮最小 clean replication 的 hard verdict 是 **`{verdict}`**。更直白地说：这条线当前最关键的诚实门槛就是 `VWAP anchor sensitivity`；如果换个 anchor 结论就明显变形，就还不配直接进 `paper candidate pool`。\n"
        "    - 网页落点：`reports/site/factors/scout_rank35_vwap_pullback_15m/report.html`、`reports/site/reading/trendline_alpha_scout/rank35_vwap_pullback_source_intake.html`。"
    )
    if old_rank_block in text:
        text = text.replace(old_rank_block, new_rank_block, 1)

    TODO_PATH.write_text(text, encoding="utf-8")


def build_html(overall: pd.DataFrame, asset_summary: pd.DataFrame, time_buckets: pd.DataFrame, verdict: str, verdict_reason: str, generated_at: str) -> str:
    focus = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)].copy()
    headline = "主变体没有形成可用样本。"
    if not focus.empty:
        best = focus.sort_values("mean_total_return", ascending=False).iloc[0]
        worst = focus.sort_values("mean_total_return", ascending=True).iloc[0]
        headline = (
            f"主变体 {PRIMARY_VARIANT} 在 6bps/side 下最强的 `{best['anchor']}` 约为 mean_total_return≈{pct(best['mean_total_return'])}、positive_asset_ratio≈{pct(best['positive_asset_ratio'])}；"
            f"最弱的 `{worst['anchor']}` 约为 mean_total_return≈{pct(worst['mean_total_return'])}、positive_asset_ratio≈{pct(worst['positive_asset_ratio'])}。"
        )
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Rank 35 · VWAP pullback clean replication</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1120px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background: #f8fafc; }}
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
  <p><a href="../../reading/trendline_alpha_scout/report.html">← 返回 Trendline Alpha Scout</a></p>
  <h1>Rank 35 · VWAP pullback + trend-template qualifier</h1>
  <p class="muted">生成时间：{escape(generated_at)} ｜ 类型：最小 clean replication ｜ 角色：Scout Seat 的 long-only pullback / reclaim fast verdict</p>

  <div class="card">
    <h2>这轮只回答什么</h2>
    <ul>
      <li>固定复用 <code>BTC/ETH/SOL 120d 15m</code> cache，不追新 bar。</li>
      <li>只比较 <code>baseline_higher_tf_bias / bias_plus_rsi_pullback / bias_plus_vwap_reclaim / combo_long_only</code>。</li>
      <li>higher-tf trend proxy 提前冻结为 <code>1h close&gt;EMA20&gt;EMA50</code> 且 <code>4h close&gt;EMA20</code>。</li>
      <li>VWAP anchor 只比较两档：<code>utc_day</code> 与 <code>funding_8h</code>；先回答 <code>anchor sensitivity</code>，不事后挑更好看的 anchor。</li>
      <li>执行口径保持最小：next-bar open 进场，固定持有 <code>{HOLD_BARS}</code> 根 15m bar。</li>
    </ul>
  </div>

  <div class="card">
    <h2>clean-room 规则</h2>
    <ul>
      <li><b>baseline_higher_tf_bias：</b>higher-tf trend proxy 从 false→true 时才允许开一笔 long。</li>
      <li><b>bias_plus_rsi_pullback：</b>bias 保持为真，且 RSI14 先跌进 pullback 区（最近 {PULLBACK_LOOKBACK} 根出现 ≤ {int(RSI_PULLBACK_LEVEL)}），随后重新站回 {int(RSI_RECLAIM_LEVEL)} 上方。</li>
      <li><b>bias_plus_vwap_reclaim：</b>bias 保持为真，且价格在 pullback 后重新站回冻结 VWAP anchor。</li>
      <li><b>combo_long_only：</b>RSI reclaim 与 VWAP reclaim 同时成立，默认只做 long-only。</li>
    </ul>
  </div>

  <div class="card">
    <h2>hard verdict</h2>
    <p><span class="pill">{escape(verdict)}</span></p>
    <p><b>{escape(headline)}</b></p>
    <p class="muted">{escape(verdict_reason)}</p>
  </div>

  <div class="card">
    <h2>跨 anchor / 变体总表</h2>
    {render_table(overall[["anchor","variant","cost_bps_per_side","mean_total_return","positive_asset_ratio","mean_trades","mean_no_trade_ratio","mean_win_rate"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_no_trade_ratio","mean_win_rate"}, digits_cols={"cost_bps_per_side":0,"mean_trades":1})}
  </div>

  <div class="card">
    <h2>主变体分资产摘要（{escape(PRIMARY_VARIANT)}）</h2>
    {render_table(asset_summary[(asset_summary['variant'] == PRIMARY_VARIANT) & (asset_summary['cost_bps_per_side'] == PRIMARY_COST)][["anchor","asset","trades","total_return","avg_net_ret","win_rate","no_trade_ratio"]], percent_cols={"total_return","avg_net_ret","win_rate","no_trade_ratio"}, digits_cols={"trades":0})}
  </div>

  <div class="card">
    <h2>time-pocket honesty（主变体 6bps）</h2>
    {render_table(time_buckets[["anchor","time_bucket","mean_total_return","trades","win_rate"]] if not time_buckets.empty else pd.DataFrame(), percent_cols={"mean_total_return","win_rate"}, digits_cols={"trades":0})}
  </div>

  <div class="card">
    <h2>artifact</h2>
    <ul>
      <li><a href="../../../artifacts/scout_rank35_vwap_pullback_15m/overall_summary.csv">overall_summary.csv</a></li>
      <li><a href="../../../artifacts/scout_rank35_vwap_pullback_15m/asset_summary.csv">asset_summary.csv</a></li>
      <li><a href="../../../artifacts/scout_rank35_vwap_pullback_15m/time_bucket_summary.csv">time_bucket_summary.csv</a></li>
      <li><a href="../../../artifacts/scout_rank35_vwap_pullback_15m/primary_trades_6bps.csv">primary_trades_6bps.csv</a></li>
      <li><a href="../../../reading/trendline_alpha_scout/rank35_vwap_pullback_source_intake.html">source intake</a></li>
    </ul>
  </div>
</body>
</html>'''


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_DIR)
    asset_rows = []
    all_trades = []
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    for asset, symbol in ASSETS.items():
        for anchor in ANCHORS:
            frame = build_frame(asset, symbol, anchor)
            frame.to_csv(ART_DIR / f"{asset.lower().replace('-usd','')}_{anchor}_frame.csv", index=False)
            for variant in VARIANTS:
                for cost in COSTS:
                    trades, no_trade_ratio = build_trades(frame, asset, anchor, variant, cost)
                    if not trades.empty:
                        all_trades.append(trades)
                    asset_rows.append(summarize_asset(trades, asset, anchor, variant, cost, no_trade_ratio))

    trades_df = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    asset_summary = pd.DataFrame(asset_rows)
    overall = summarize_overall(asset_summary)
    primary_trades = pd.DataFrame()
    if not trades_df.empty:
        primary_trades = trades_df[(trades_df["variant"] == PRIMARY_VARIANT) & (trades_df["cost_bps_per_side"] == PRIMARY_COST)].copy()
    time_buckets = build_time_buckets(primary_trades)
    verdict, verdict_reason = build_verdict(overall, time_buckets)

    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    time_buckets.to_csv(ART_DIR / "time_bucket_summary.csv", index=False)
    primary_trades.to_csv(ART_DIR / "primary_trades_6bps.csv", index=False)
    pd.DataFrame([
        {
            "generated_at_utc": generated_at,
            "candidate_id": "rank35_vwap_pullback_15m",
            "primary_variant": PRIMARY_VARIANT,
            "hard_verdict": verdict,
            "verdict_reason": verdict_reason,
        }
    ]).to_csv(ART_DIR / "meta.csv", index=False)

    html = build_html(overall, asset_summary, time_buckets, verdict, verdict_reason, generated_at)
    (SITE_DIR / "report.html").write_text(html, encoding="utf-8")
    (READING_DIR / "rank35_vwap_pullback_clean_replication.html").write_text(html, encoding="utf-8")
    update_reading_report(verdict, generated_at, overall)
    update_todo(verdict, generated_at, overall, time_buckets)
    print(f"verdict={verdict}")
    print(overall[(overall['variant'] == PRIMARY_VARIANT) & (overall['cost_bps_per_side'] == PRIMARY_COST)].to_dict(orient='records'))


if __name__ == "__main__":
    main()
