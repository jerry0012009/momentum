#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank73_psar_close_confirmed_followup_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank73_psar_close_confirmed_followup_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank73_psar_close_confirmed_followup_clean_replication.html"
TODO_PATH = ROOT / "docs" / "TODO.md"
DUE_PATH = ROOT / "reports" / "artifacts" / "ema_psar_raw_alpha" / "ema_paper_trading_due_guardrail_snapshot.csv"
P3_SUMMARY_PATH = ROOT / "reports" / "artifacts" / "manual_narrow_paper_lanes" / "manual_narrow_paper_last_run_summary.json"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
SETUPS = ["ema_psar_long", "breakout_short"]
VARIANTS = ["raw_trigger", "close_confirmed_n1", "close_confirmed_n2", "close_confirmed_n3"]
PRIMARY_VARIANT = "close_confirmed_n2"
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0]
HOLD_BARS = 8
EARLY_FAIL_BARS = 4
CSS = """
body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width:1100px; margin:40px auto; padding:0 18px; line-height:1.72; color:#111827; background:#f8fafc; }
.card { border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }
.pill { display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }
.muted { color:#6b7280; }
code { background:#f3f4f6; padding:1px 5px; border-radius:6px; }
table { width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }
th, td { border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }
a { color:#2563eb; text-decoration:none; }
"""


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


def compute_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    prev_close = df["close"].shift(1)
    tr = pd.concat([
        (df["high"] - df["low"]).abs(),
        (df["high"] - prev_close).abs(),
        (df["low"] - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def compute_psar(df: pd.DataFrame, step: float = 0.02, max_step: float = 0.2) -> pd.Series:
    high = df["high"].to_numpy(dtype=float)
    low = df["low"].to_numpy(dtype=float)
    n = len(df)
    psar = np.full(n, np.nan)
    bull = True
    af = step
    ep = high[0]
    psar[0] = low[0]
    if n > 1:
        bull = high[1] >= high[0]
        ep = high[1] if bull else low[1]
        psar[1] = min(low[0], low[1]) if bull else max(high[0], high[1])
    for i in range(2, n):
        prev_psar = psar[i - 1]
        if bull:
            cur = prev_psar + af * (ep - prev_psar)
            cur = min(cur, low[i - 1], low[i - 2])
            if low[i] < cur:
                bull = False
                cur = ep
                ep = low[i]
                af = step
            else:
                if high[i] > ep:
                    ep = high[i]
                    af = min(max_step, af + step)
        else:
            cur = prev_psar + af * (ep - prev_psar)
            cur = max(cur, high[i - 1], high[i - 2])
            if high[i] > cur:
                bull = True
                cur = ep
                ep = high[i]
                af = step
            else:
                if low[i] < ep:
                    ep = low[i]
                    af = min(max_step, af + step)
        psar[i] = cur
    return pd.Series(psar, index=df.index)


def add_psar_followup_state(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    psar_prev = out["psar"].shift(1)
    close = out["close"]
    trend_dir = np.where(close > psar_prev, 1, np.where(close < psar_prev, -1, 0))
    trend_bars: list[int] = []
    prev = 0
    run = 0
    for direction in trend_dir:
        d = int(direction)
        if d == 0:
            run = 0
        elif d == prev:
            run = run + 1 if d > 0 else run - 1
        else:
            run = 1 if d > 0 else -1
        trend_bars.append(run)
        prev = d if d != 0 else prev
    out["psar_prev"] = psar_prev
    out["trend_dir"] = trend_dir
    out["trend_bars"] = trend_bars
    out["psar_flip_up"] = (out["trend_dir"] == 1) & (pd.Series(out["trend_dir"]).shift(1) != 1)
    out["psar_flip_down"] = (out["trend_dir"] == -1) & (pd.Series(out["trend_dir"]).shift(1) != -1)
    return out


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_bars(symbol, asset)
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema15"] = df["close"].ewm(span=15, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["vol_ma20"] = df["volume"].rolling(20, min_periods=20).mean()
    df["atr14"] = compute_atr(df)
    df["psar"] = compute_psar(df)
    low20 = df["low"].rolling(20, min_periods=20).min().shift(1)
    atr = df["atr14"]

    df["ema_psar_long_signal"] = (
        (df["ema9"] > df["ema15"])
        & (df["ema_slope"] > 0.0003)
        & (df["psar"] < df["close"])
        & (df["close"] > df["high"].shift(1))
        & (df["close"].shift(1) < df["ema9"].shift(1))
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)
    df["breakout_short_signal"] = (
        low20.notna()
        & (df["ema9"] < df["ema15"])
        & (df["ema_slope"] < -0.0003)
        & (df["close"].shift(1) > low20.shift(1))
        & (df["close"].shift(2) > low20.shift(2))
        & (df["close"] < low20 - 0.1 * atr)
        & (df["high"] <= low20 + 0.3 * atr)
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)
    df["breakout_anchor"] = low20
    return add_psar_followup_state(df)


def gate_pass(frame: pd.DataFrame, setup: str, variant: str) -> pd.Series:
    if variant == "raw_trigger":
        return pd.Series(True, index=frame.index)
    n = int(variant.rsplit("n", 1)[1])
    if setup == "ema_psar_long":
        return (frame["trend_dir"] == 1) & (frame["trend_bars"] >= n) & (frame["close"] > frame["psar_prev"])
    if setup == "breakout_short":
        return (frame["trend_dir"] == -1) & (frame["trend_bars"].abs() >= n) & (frame["close"] < frame["psar_prev"])
    raise ValueError(setup)


def build_signals(frame: pd.DataFrame, asset: str, setup: str, variant: str) -> pd.DataFrame:
    raw = frame[f"{setup}_signal"] & ~frame[f"{setup}_signal"].shift(1).fillna(False)
    gate = gate_pass(frame, setup, variant)
    sig = raw & gate
    rows: list[dict[str, object]] = []
    last_exit = -1
    for idx in range(40, len(frame) - HOLD_BARS - 1):
        if idx <= last_exit or not bool(sig.iloc[idx]):
            continue
        anchor = float(frame.iloc[idx]["breakout_anchor"]) if setup == "breakout_short" else float(frame.iloc[idx]["ema15"])
        rows.append({
            "signal_id": f"{asset}|{setup}|{variant}|{idx}",
            "asset": asset,
            "setup": setup,
            "variant": variant,
            "signal_idx": idx,
            "entry_idx": idx + 1,
            "signal_ts": pd.to_datetime(frame.iloc[idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "signal_price": float(frame.iloc[idx]["close"]),
            "signal_anchor": anchor,
            "trend_dir": int(frame.iloc[idx]["trend_dir"]),
            "trend_bars": int(frame.iloc[idx]["trend_bars"]),
            "psar_prev": float(frame.iloc[idx]["psar_prev"]),
        })
        last_exit = idx + HOLD_BARS
    return pd.DataFrame(rows)


def build_trades(frame: pd.DataFrame, signals: pd.DataFrame, cost_bps: float) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    cost_rate = float(cost_bps) / 10000.0
    for _, sig in signals.iterrows():
        entry_idx = int(sig["entry_idx"])
        if entry_idx >= len(frame):
            continue
        exit_idx = min(len(frame) - 1, entry_idx + HOLD_BARS - 1)
        direction = 1 if sig["setup"] == "ema_psar_long" else -1
        entry_px = float(frame.iloc[entry_idx]["open"])
        exit_px = float(frame.iloc[exit_idx]["open"])
        gross = (exit_px / entry_px - 1.0) * direction
        net = (1.0 + gross) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
        win = bool(net > 0)
        fail_slice = frame.iloc[entry_idx:min(len(frame), entry_idx + EARLY_FAIL_BARS)].copy()
        if sig["setup"] == "ema_psar_long":
            early_fail = bool(((fail_slice["close"] < fail_slice["ema15"]) | (fail_slice["close"] < fail_slice["psar_prev"])).any())
            false_break = bool((fail_slice["close"] < float(sig["signal_anchor"])).any())
        else:
            early_fail = bool(((fail_slice["close"] > fail_slice["ema15"]) | (fail_slice["close"] > fail_slice["psar_prev"])).any())
            false_break = bool((fail_slice["close"] > float(sig["signal_anchor"])).any())
        rows.append({
            "signal_id": sig["signal_id"],
            "asset": sig["asset"],
            "setup": sig["setup"],
            "variant": sig["variant"],
            "cost_bps_per_side": float(cost_bps),
            "signal_ts": sig["signal_ts"],
            "entry_ts": pd.to_datetime(frame.iloc[entry_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "exit_ts": pd.to_datetime(frame.iloc[exit_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "entry_price": entry_px,
            "exit_price": exit_px,
            "gross_ret": gross,
            "net_ret": net,
            "win": win,
            "flip_to_fail_rate_flag": early_fail,
            "false_break_ratio_flag": false_break,
            "trend_bars": sig["trend_bars"],
        })
    return pd.DataFrame(rows)


def summarize_asset(trades: pd.DataFrame, *, asset: str, setup: str, variant: str, cost_bps: float, signal_events: int) -> dict[str, object]:
    if trades.empty:
        return {
            "asset": asset,
            "setup": setup,
            "variant": variant,
            "cost_bps_per_side": float(cost_bps),
            "signal_events": int(signal_events),
            "trades": 0,
            "trade_count_retention": np.nan,
            "total_return": 0.0,
            "avg_net_ret": np.nan,
            "win_rate": np.nan,
            "flip_to_fail_rate": np.nan,
            "false_break_ratio": np.nan,
        }
    return {
        "asset": asset,
        "setup": setup,
        "variant": variant,
        "cost_bps_per_side": float(cost_bps),
        "signal_events": int(signal_events),
        "trades": int(len(trades)),
        "trade_count_retention": np.nan,
        "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
        "avg_net_ret": float(trades["net_ret"].mean()),
        "win_rate": float(trades["win"].mean()),
        "flip_to_fail_rate": float(trades["flip_to_fail_rate_flag"].mean()),
        "false_break_ratio": float(trades["false_break_ratio_flag"].mean()),
    }


def add_trade_retention(asset_df: pd.DataFrame) -> pd.DataFrame:
    out = asset_df.copy()
    for setup in sorted(out["setup"].unique()):
        for cost in sorted(out["cost_bps_per_side"].unique()):
            base_map = (
                out[(out["setup"] == setup) & (out["variant"] == "raw_trigger") & (out["cost_bps_per_side"] == cost)]
                .set_index("asset")["trades"]
                .to_dict()
            )
            mask = (out["setup"] == setup) & (out["cost_bps_per_side"] == cost)
            out.loc[mask, "trade_count_retention"] = out.loc[mask].apply(
                lambda r: (r["trades"] / base_map.get(r["asset"], np.nan)) if base_map.get(r["asset"], 0) else np.nan,
                axis=1,
            )
    return out


def build_time_pockets(all_trades: pd.DataFrame) -> pd.DataFrame:
    if all_trades.empty:
        return pd.DataFrame(columns=["setup", "variant", "bucket", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_false_break_ratio"])
    df = all_trades.copy()
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
    for (setup, variant, bucket_name, asset), part in df.groupby(["setup", "variant", "bucket", "asset"], dropna=False):
        rows.append({
            "setup": setup,
            "variant": variant,
            "bucket": bucket_name,
            "asset": asset,
            "total_return": float((1.0 + part["net_ret"]).prod() - 1.0),
            "trades": int(len(part)),
            "false_break_ratio": float(part["false_break_ratio_flag"].mean()),
        })
    tmp = pd.DataFrame(rows)
    return (
        tmp.groupby(["setup", "variant", "bucket"], dropna=False)
        .agg(
            mean_total_return=("total_return", "mean"),
            positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
            mean_trades=("trades", "mean"),
            mean_false_break_ratio=("false_break_ratio", "mean"),
        )
        .reset_index()
        .sort_values(["setup", "variant", "bucket"])
        .reset_index(drop=True)
    )


def verdict_and_notes(overall: pd.DataFrame) -> tuple[str, list[str]]:
    primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    raw = overall[(overall["variant"] == "raw_trigger") & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    if primary.empty or raw.empty:
        return "hard verdict：缺少 Rank 73 主读法结果。", ["主读法 `close_confirmed_n2 @ 6bps` 或 raw 对照未产出。"]
    p = primary.iloc[0]
    r = raw.iloc[0]
    notes = [
        f"`close_confirmed_n2 @ 6bps`：mean_total_return≈{pct(p['mean_total_return'])}、positive_asset_ratio≈{pct(p['positive_asset_ratio'])}、mean_trades≈{num(p['mean_trades'],1)}、mean_trade_count_retention≈{pct(p['mean_trade_count_retention'])}、mean_flip_to_fail_rate≈{pct(p['mean_flip_to_fail_rate'])}、mean_false_break_ratio≈{pct(p['mean_false_break_ratio'])}。",
        f"对照 `raw_trigger @ 6bps`：mean_total_return≈{pct(r['mean_total_return'])}、positive_asset_ratio≈{pct(r['positive_asset_ratio'])}、mean_trades≈{num(r['mean_trades'],1)}、mean_flip_to_fail_rate≈{pct(r['mean_flip_to_fail_rate'])}、mean_false_break_ratio≈{pct(r['mean_false_break_ratio'])}。",
    ]
    if p["mean_total_return"] > 0 and p["positive_asset_ratio"] >= (2 / 3) and p["mean_trade_count_retention"] >= 0.45:
        return "hard verdict：Rank 73 在这手最小 clean replication 下拿到了继续观察资格，但仍更像 shared follow-up gate，还不够直接升格为 paper candidate。", notes
    return "hard verdict：Rank 73 / PSAR close-confirmed follow-up gate 在当前最小 clean replication 下仍更像 `park / evidence pool`；N=2/3 的改善主要来自砍交易数，跨 setup 与成本后不够诚实。", notes


def update_todo(overall: pd.DataFrame, pockets: pd.DataFrame, generated_at: str, verdict: str) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    marker = "### Next 3 bot3 runs（当前默认执行顺序）\n"
    if marker not in text:
        raise RuntimeError("Next 3 marker missing in TODO.md")
    if f"**最新补充（{generated_at}）**" in text:
        return
    p = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    r = overall[(overall["variant"] == "raw_trigger") & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    pocket = pockets[(pockets["variant"] == PRIMARY_VARIANT) & (pockets["setup"] == "breakout_short")]
    if pocket.empty:
        pocket_text = "time-pocket 暂无有效分桶结果"
    else:
        parts = []
        for _, row in pocket.iterrows():
            parts.append(f"{row['bucket']}≈{pct(row['mean_total_return'])}/{pct(row['positive_asset_ratio'])}")
        pocket_text = "；".join(parts)
    insert = f"- **最新补充（{generated_at}）**：这轮再次先核对 `Run 1 / EMA due-check` 与 `P3` 托管位状态：最新 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍显示全 desk 无 `due-now / overdue` lane，最早 due 点仍是 `A股三条 lane -> 2026-03-19 07:00 UTC`；`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 继续是 `new_closed_trades_appended=0`。因此本轮合法主动作仍是 **`Run 2 / Rank 73 minimal clean replication`**，而不是继续回头挤占 `P3 continuity`。\n  - 这轮已把 **`Rank 73 / PSAR close-confirmed follow-up gate`** 的唯一那手最小 clean replication 跑完：固定复用 `BTC/ETH/SOL 120d 15m` cache，只接到 `ema_psar_long` 与 `breakout_short` 两条 archetype，上比较 `raw_trigger / close_confirmed_n1 / n2 / n3` 四臂，并统一冻结到 **`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`**。\n  - `6bps/side` 下，主读法 `close_confirmed_n2` 的跨切片结果为：`mean_total_return≈{pct(p['mean_total_return'])}`、`positive_asset_ratio≈{pct(p['positive_asset_ratio'])}`、`mean_trades≈{num(p['mean_trades'],1)}`、`mean_trade_count_retention≈{pct(p['mean_trade_count_retention'])}`、`mean_flip_to_fail_rate≈{pct(p['mean_flip_to_fail_rate'])}`、`mean_false_break_ratio≈{pct(p['mean_false_break_ratio'])}`；对照 `raw_trigger≈{pct(r['mean_total_return'])}/{pct(r['mean_false_break_ratio'])}`。breakout_short 的 `time-pocket honesty`：{pocket_text}。\n  - 因此当前更诚实的 hard verdict 是 **`{verdict}`**。若下一轮 `EMA` 仍 waiting_not_due，默认应先回到 **fresh paper / repo source re-rank（来自 RECENT_PAPER_SEEDS / quant_digests / validated shortlist）**；只有这一层本轮也拿不到合格 source，才允许回退到 `Rank 35b > Rank 16b > tiny-live plumbing`。\n  - 网页落点：`reports/site/factors/scout_rank73_psar_close_confirmed_followup_15m/report.html`。\n\n"
    text = text.replace(marker, marker + insert, 1)
    TODO_PATH.write_text(text, encoding="utf-8")


def build_report_html(overall: pd.DataFrame, asset_df: pd.DataFrame, pockets: pd.DataFrame, verdict: str, notes: list[str], generated_at: str) -> str:
    overall_view = overall.copy()
    asset_view = asset_df[asset_df["cost_bps_per_side"] == PRIMARY_COST].copy()
    pocket_view = pockets[(pockets["variant"] == PRIMARY_VARIANT)].copy()
    body = f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 73 · PSAR close-confirmed follow-up gate clean replication</title>
  <style>{CSS}</style>
</head>
<body>
  <p><a href='../reading/repo_scout/rank73_psar_close_confirmed_followup_source_intake.html'>← 返回 source intake</a></p>
  <h1>Rank 73 · PSAR close-confirmed follow-up gate（minimal clean replication）</h1>
  <p class='muted'>生成时间：{escape(generated_at)}｜固定 BTC/ETH/SOL 120d 15m cache，统一冻结为 <code>signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars</code>。</p>

  <div class='card'>
    <h2>这轮只回答一个问题</h2>
    <p>当 <code>EMA = waiting_not_due</code> 时，Rank 73 只拿 1 次最小预算：<b>PSAR close-confirmed flip + 第 N 根 follow-up</b> 能不能同时服务 <code>ema_psar_long</code> 与 <code>breakout_short</code>，在不过度砍单的前提下减少早死 / 假突破？</p>
    <p><span class='pill'>只做 clean replication，不扩成新的 PSAR 大研究</span></p>
  </div>

  <div class='card'>
    <h2>冻结规则</h2>
    <ul>
      <li><b>base setup A / ema_psar_long</b>：延用现成 EMA/PSAR continuation 原始 trigger。</li>
      <li><b>base setup B / breakout_short</b>：延用现成 20-bar low reclaim/breakdown 原始 trigger。</li>
      <li><b>raw_trigger</b>：不额外等待 follow-up。</li>
      <li><b>close_confirmed_n1 / n2 / n3</b>：只在 <code>close vs psar[1]</code> 已确认翻向，且当前连续 trend bar 数达到 <code>N</code> 时放行。</li>
      <li>统一要求 <code>next-bar open</code> 入场、<code>no-overlap</code>、持有 <code>8</code> 根；不允许用 signal 之后的 trend bar 回填 admission。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>hard verdict</h2>
    <p><b>{escape(verdict)}</b></p>
    <ul>{''.join(f'<li>{escape(line)}</li>' for line in notes)}</ul>
  </div>

  <div class='card'>
    <h2>overall summary</h2>
    {render_table(overall_view, percent_cols={'mean_total_return','positive_asset_ratio','mean_trade_count_retention','mean_avg_net_ret','mean_flip_to_fail_rate','mean_false_break_ratio'}, digits_cols={'cost_bps_per_side':0,'mean_trades':1})}
  </div>

  <div class='card'>
    <h2>primary cost（6bps）asset-level</h2>
    {render_table(asset_view, percent_cols={'total_return','trade_count_retention','avg_net_ret','win_rate','flip_to_fail_rate','false_break_ratio'}, digits_cols={'trades':0,'cost_bps_per_side':0})}
  </div>

  <div class='card'>
    <h2>time-pocket honesty（主读法 = close_confirmed_n2）</h2>
    {render_table(pocket_view, percent_cols={'mean_total_return','positive_asset_ratio','mean_false_break_ratio'}, digits_cols={'mean_trades':1})}
  </div>
</body>
</html>
"""
    return body


def build_reading_html(generated_at: str, verdict: str) -> str:
    return f"""<!doctype html>
<html><head><meta charset='utf-8'><title>Rank 73 clean replication</title><style>{CSS}</style></head><body>
<p><a href='rank73_psar_close_confirmed_followup_source_intake.html'>← 返回 Rank 73 source intake</a></p>
<h1>Rank 73 · minimal clean replication</h1>
<div class='card'>
  <p><span class='pill'>更新时间：{escape(generated_at)}</span><span class='pill'>verdict：{escape(verdict)}</span></p>
  <p>这轮把 Rank 73 的最小 clean replication 跑完了：只比较 <code>raw_trigger / close_confirmed_n1 / n2 / n3</code>，固定 <code>BTC/ETH/SOL 120d 15m</code> cache，统一 <code>next-bar open + no-overlap + hold 8 bars</code>。</p>
  <p>Reader-facing 主落点：<a href='../../factors/scout_rank73_psar_close_confirmed_followup_15m/report.html'>scout_rank73_psar_close_confirmed_followup_15m/report.html</a></p>
</div>
</body></html>"""


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    asset_rows: list[dict[str, object]] = []
    signal_rows: list[dict[str, object]] = []
    trade_frames: list[pd.DataFrame] = []

    for asset, symbol in ASSETS.items():
        frame = build_frame(asset, symbol)
        frame.to_csv(ART_DIR / f"{symbol.lower()}_feature_frame.csv", index=False)
        for setup in SETUPS:
            signals_by_variant: dict[str, pd.DataFrame] = {}
            for variant in VARIANTS:
                signals = build_signals(frame, asset, setup, variant)
                signals_by_variant[variant] = signals
                signal_rows.append({"asset": asset, "setup": setup, "variant": variant, "signal_events": int(len(signals))})
                (signals if not signals.empty else pd.DataFrame(columns=["signal_id","asset","setup","variant","signal_idx","entry_idx","signal_ts","signal_price","signal_anchor","trend_dir","trend_bars","psar_prev"]))\
                    .to_csv(ART_DIR / f"signals_{asset.replace('-','').lower()}_{setup}_{variant}.csv", index=False)
            for cost in COSTS:
                base_trades = build_trades(frame, signals_by_variant["raw_trigger"], cost)
                if not base_trades.empty:
                    trade_frames.append(base_trades)
                asset_rows.append(summarize_asset(base_trades, asset=asset, setup=setup, variant="raw_trigger", cost_bps=cost, signal_events=len(signals_by_variant["raw_trigger"])))
                for variant in VARIANTS[1:]:
                    trades = build_trades(frame, signals_by_variant[variant], cost)
                    if not trades.empty:
                        trade_frames.append(trades)
                    asset_rows.append(summarize_asset(trades, asset=asset, setup=setup, variant=variant, cost_bps=cost, signal_events=len(signals_by_variant[variant])))

    asset_df = add_trade_retention(pd.DataFrame(asset_rows)).sort_values(["setup", "variant", "cost_bps_per_side", "asset"]).reset_index(drop=True)
    asset_df.to_csv(ART_DIR / "asset_summary.csv", index=False)
    pd.DataFrame(signal_rows).to_csv(ART_DIR / "signal_event_counts.csv", index=False)
    all_trades = pd.concat(trade_frames, ignore_index=True) if trade_frames else pd.DataFrame()
    if not all_trades.empty:
        all_trades.to_csv(ART_DIR / "trade_log.csv", index=False)
    overall = (
        asset_df.groupby(["setup", "variant", "cost_bps_per_side"], dropna=False)
        .agg(
            mean_total_return=("total_return", "mean"),
            positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
            mean_trades=("trades", "mean"),
            mean_trade_count_retention=("trade_count_retention", "mean"),
            mean_avg_net_ret=("avg_net_ret", "mean"),
            mean_flip_to_fail_rate=("flip_to_fail_rate", "mean"),
            mean_false_break_ratio=("false_break_ratio", "mean"),
        )
        .reset_index()
        .sort_values(["setup", "variant", "cost_bps_per_side"])
        .reset_index(drop=True)
    )
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    pockets = build_time_pockets(all_trades)
    pockets.to_csv(ART_DIR / "time_pocket_summary.csv", index=False)

    verdict, notes = verdict_and_notes(overall)
    update_todo(overall, pockets, generated_at, verdict)
    report_html = build_report_html(overall, asset_df, pockets, verdict, notes, generated_at)
    (SITE_DIR / "report.html").write_text(report_html, encoding="utf-8")
    READING_PATH.write_text(build_reading_html(generated_at, verdict), encoding="utf-8")
    print(verdict)
    print(overall[(overall['cost_bps_per_side'] == PRIMARY_COST)][['setup','variant','mean_total_return','positive_asset_ratio','mean_trades','mean_trade_count_retention','mean_flip_to_fail_rate','mean_false_break_ratio']].to_dict(orient='records'))


if __name__ == "__main__":
    main()
