#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import math
import re

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank53_close_confirmed_choch_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank53_close_confirmed_choch_15m"
READING_DIR = ROOT / "reports" / "site" / "reading" / "repo_scout"
READING_REPORT = READING_DIR / "report.html"
TODO_PATH = ROOT / "docs" / "TODO.md"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}

COSTS = [6.0]
PRIMARY_COST = 6.0
VARIANTS = [
    "base",
    "htf_close_trend_gate",
    "no_choch_no_flip",
    "liquidity_sweep_veto",
]
PRIMARY_VARIANT = "liquidity_sweep_veto"
SETUPS = ["ema_pullback_long", "breakdown_reclaim_short"]
PRIMARY_SETUP = "breakdown_reclaim_short"
HOLD_BARS = 8
FALSE_LOOKAHEAD = 4
SWING_LOOKBACK_1H = 3
SWEEP_LOOKBACK_HOURS = 6
EMA_FAST = 9
EMA_SLOW = 15
EMA_SLOPE_BARS = 3
VOL_MA = 20
ATR_PERIOD = 14


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
    return tr.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def confirmed_pivots(arr: np.ndarray, lookback: int) -> tuple[np.ndarray, np.ndarray]:
    n = len(arr)
    highs = np.full(n, np.nan, dtype=float)
    lows = np.full(n, np.nan, dtype=float)
    for center in range(lookback, n - lookback):
        v = float(arr[center])
        left = arr[center - lookback:center]
        right = arr[center + 1:center + lookback + 1]
        if np.all(v > left) and np.all(v > right):
            highs[center + lookback] = v
        if np.all(v < left) and np.all(v < right):
            lows[center + lookback] = v
    return highs, lows


def build_htf_state(frame: pd.DataFrame) -> pd.DataFrame:
    htf = (
        frame[["timestamp", "open", "high", "low", "close"]]
        .set_index("timestamp")
        .resample("1h")
        .agg({"open": "first", "high": "max", "low": "min", "close": "last"})
        .dropna()
        .reset_index()
        .rename(columns={
            "open": "open_1h",
            "high": "high_1h",
            "low": "low_1h",
            "close": "close_1h",
        })
    )
    htf["pivot_high"], htf["pivot_low"] = confirmed_pivots(htf["close_1h"].to_numpy(dtype=float), SWING_LOOKBACK_1H)

    last_high = np.full(len(htf), np.nan)
    last_low = np.full(len(htf), np.nan)
    state = np.zeros(len(htf), dtype=int)
    bull_choch = np.zeros(len(htf), dtype=int)
    bear_choch = np.zeros(len(htf), dtype=int)
    sweep_up = np.zeros(len(htf), dtype=int)
    sweep_down = np.zeros(len(htf), dtype=int)

    current_high = np.nan
    current_low = np.nan
    current_state = 0

    for i in range(len(htf)):
        if pd.notna(htf.iloc[i]["pivot_high"]):
            current_high = float(htf.iloc[i]["pivot_high"])
        if pd.notna(htf.iloc[i]["pivot_low"]):
            current_low = float(htf.iloc[i]["pivot_low"])
        last_high[i] = current_high
        last_low[i] = current_low
        close = float(htf.iloc[i]["close_1h"])
        high = float(htf.iloc[i]["high_1h"])
        low = float(htf.iloc[i]["low_1h"])
        prev_close = float(htf.iloc[i - 1]["close_1h"]) if i > 0 else close
        if math.isfinite(current_high) and prev_close <= current_high and close > current_high:
            current_state = 1
            bull_choch[i] = 1
        if math.isfinite(current_low) and prev_close >= current_low and close < current_low:
            current_state = -1
            bear_choch[i] = 1
        if math.isfinite(current_high) and high > current_high and close <= current_high:
            sweep_up[i] = 1
        if math.isfinite(current_low) and low < current_low and close >= current_low:
            sweep_down[i] = 1
        state[i] = current_state

    htf["last_confirmed_high"] = last_high
    htf["last_confirmed_low"] = last_low
    htf["htf_state"] = state
    htf["bull_choch"] = bull_choch
    htf["bear_choch"] = bear_choch
    htf["sweep_up"] = sweep_up
    htf["sweep_down"] = sweep_down
    htf["recent_sweep_up"] = htf["sweep_up"].rolling(SWEEP_LOOKBACK_HOURS, min_periods=1).max()
    htf["recent_sweep_down"] = htf["sweep_down"].rolling(SWEEP_LOOKBACK_HOURS, min_periods=1).max()
    return htf


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_bars(symbol, asset)
    df["ema9"] = df["close"].ewm(span=EMA_FAST, adjust=False).mean()
    df["ema15"] = df["close"].ewm(span=EMA_SLOW, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(EMA_SLOPE_BARS)
    df["vol_ma20"] = df["volume"].rolling(VOL_MA, min_periods=VOL_MA).mean()
    df["atr14"] = compute_atr(df)
    df["rolling_low20"] = df["low"].rolling(20, min_periods=20).min().shift(1)
    df["rolling_high20"] = df["high"].rolling(20, min_periods=20).max().shift(1)

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
    high = df["rolling_high20"]
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

    htf = build_htf_state(df)
    df = pd.merge_asof(df.sort_values("timestamp"), htf.sort_values("timestamp"), on="timestamp", direction="backward")
    return df.reset_index(drop=True)


def direction_for_setup(setup: str) -> int:
    return 1 if setup == "ema_pullback_long" else -1


def setup_signal_col(setup: str) -> str:
    return f"{setup}_signal"


def get_signal(frame: pd.DataFrame, idx: int, setup: str, variant: str) -> tuple[int, float] | None:
    direction = direction_for_setup(setup)
    row = frame.iloc[idx]
    prev = frame.iloc[idx - 1]
    if not bool(row[setup_signal_col(setup)]) or bool(prev[setup_signal_col(setup)]):
        return None

    htf_state = int(row.get("htf_state", 0))
    recent_sweep_up = int(row.get("recent_sweep_up", 0))
    recent_sweep_down = int(row.get("recent_sweep_down", 0))

    if variant == "htf_close_trend_gate":
        if htf_state != direction:
            return None
    elif variant == "no_choch_no_flip":
        if htf_state == -direction:
            return None
    elif variant == "liquidity_sweep_veto":
        if htf_state == -direction:
            return None
        if direction > 0 and recent_sweep_up == 1:
            return None
        if direction < 0 and recent_sweep_down == 1:
            return None

    fail_level = float(row["low"] if direction > 0 else row["high"])
    return direction, fail_level


def detect_false_hold(frame: pd.DataFrame, signal_idx: int, direction: int, fail_level: float) -> int:
    last = min(len(frame) - 1, signal_idx + FALSE_LOOKAHEAD)
    for j in range(signal_idx + 1, last + 1):
        close = float(frame.iloc[j]["close"])
        if direction > 0 and close < fail_level:
            return 1
        if direction < 0 and close > fail_level:
            return 1
    return 0


def build_trades(frame: pd.DataFrame, asset: str, setup: str, variant: str, cost_bps: float) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    last_exit = -1
    direction = direction_for_setup(setup)
    cost_rate = float(cost_bps) / 10000.0
    for idx in range(2, len(frame) - 2):
        if idx <= last_exit:
            continue
        signal = get_signal(frame, idx, setup, variant)
        if signal is None:
            continue
        signal_dir, fail_level = signal
        entry_idx = idx + 1
        exit_idx = min(len(frame) - 1, entry_idx + HOLD_BARS - 1)
        entry_px = float(frame.iloc[entry_idx]["open"])
        exit_px = float(frame.iloc[exit_idx]["close"])
        if not (math.isfinite(entry_px) and math.isfinite(exit_px) and entry_px > 0 and exit_px > 0):
            continue
        gross_ret = (exit_px / entry_px - 1.0) * signal_dir
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
        rows.append(
            {
                "asset": asset,
                "setup": setup,
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "signal_idx": int(idx),
                "signal_ts": pd.to_datetime(frame.iloc[idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_ts": pd.to_datetime(frame.iloc[entry_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": pd.to_datetime(frame.iloc[exit_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "direction": "long" if direction > 0 else "short",
                "entry_price": entry_px,
                "exit_price": exit_px,
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "false_hold_4bars": int(detect_false_hold(frame, idx, signal_dir, fail_level)),
            }
        )
        last_exit = exit_idx
    return pd.DataFrame(rows)


def summarize_asset(trades: pd.DataFrame, *, asset: str, setup: str, variant: str, cost_bps: float, base_count: int) -> dict[str, object]:
    trade_count = int(len(trades))
    retention = (trade_count / base_count) if base_count > 0 else np.nan
    if trades.empty:
        return {
            "asset": asset,
            "setup": setup,
            "variant": variant,
            "cost_bps_per_side": float(cost_bps),
            "trades": 0,
            "total_return": 0.0,
            "win_rate": np.nan,
            "avg_net_ret": np.nan,
            "false_hold_4bars_rate": np.nan,
            "trade_count_retention": retention,
        }
    return {
        "asset": asset,
        "setup": setup,
        "variant": variant,
        "cost_bps_per_side": float(cost_bps),
        "trades": trade_count,
        "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
        "win_rate": float((trades["net_ret"] > 0).mean()),
        "avg_net_ret": float(trades["net_ret"].mean()),
        "false_hold_4bars_rate": float(trades["false_hold_4bars"].mean()),
        "trade_count_retention": retention,
    }


def summarize_overall(asset_summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for (setup, variant, cost), grp in asset_summary.groupby(["setup", "variant", "cost_bps_per_side"], sort=False):
        totals = grp["total_return"].to_numpy(dtype=float)
        rows.append(
            {
                "setup": setup,
                "variant": variant,
                "cost_bps_per_side": float(cost),
                "mean_total_return": float(np.nanmean(totals)) if len(totals) else np.nan,
                "positive_asset_ratio": float(np.nanmean(totals > 0)) if len(totals) else np.nan,
                "mean_trades": float(grp["trades"].mean()),
                "mean_false_hold_4bars_rate": float(grp["false_hold_4bars_rate"].mean()),
                "mean_trade_count_retention": float(grp["trade_count_retention"].mean()),
                "mean_win_rate": float(grp["win_rate"].mean()),
            }
        )
    return pd.DataFrame(rows)


def summarize_time_pockets(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["setup", "variant", "cost_bps_per_side", "bucket", "mean_total_return", "positive_asset_ratio", "mean_trades"])
    df = trades.copy()
    df["signal_ts"] = pd.to_datetime(df["signal_ts"], utc=True)
    rows: list[dict[str, object]] = []
    for (setup, variant, cost), grp in df.groupby(["setup", "variant", "cost_bps_per_side"], sort=False):
        grp = grp.sort_values("signal_ts").reset_index(drop=True)
        if grp.empty:
            continue
        buckets = np.array_split(grp.index.to_numpy(), 3)
        for idx, bucket in enumerate(buckets, start=1):
            part = grp.loc[bucket]
            if part.empty:
                continue
            by_asset = part.groupby("asset")["net_ret"].apply(lambda s: float((1.0 + s).prod() - 1.0))
            rows.append(
                {
                    "setup": setup,
                    "variant": variant,
                    "cost_bps_per_side": float(cost),
                    "bucket": f"bucket_{idx}",
                    "mean_total_return": float(by_asset.mean()) if len(by_asset) else np.nan,
                    "positive_asset_ratio": float((by_asset > 0).mean()) if len(by_asset) else np.nan,
                    "mean_trades": float(part.groupby("asset").size().mean()) if not part.empty else np.nan,
                }
            )
    return pd.DataFrame(rows)


def build_verdict(overall: pd.DataFrame) -> tuple[str, str]:
    primary = overall[
        (overall["setup"] == PRIMARY_SETUP)
        & (overall["variant"] == PRIMARY_VARIANT)
        & (overall["cost_bps_per_side"] == PRIMARY_COST)
    ]
    if primary.empty:
        return "park / evidence pool", "主读法没有形成可用样本，最小 clean replication 不足以支撑 admission。"
    row = primary.iloc[0]
    mean_ret = float(row["mean_total_return"]) if pd.notna(row["mean_total_return"]) else -1.0
    pos_ratio = float(row["positive_asset_ratio"]) if pd.notna(row["positive_asset_ratio"]) else 0.0
    mean_trades = float(row["mean_trades"]) if pd.notna(row["mean_trades"]) else 0.0
    false_rate = float(row["mean_false_hold_4bars_rate"]) if pd.notna(row["mean_false_hold_4bars_rate"]) else 1.0
    retention = float(row["mean_trade_count_retention"]) if pd.notna(row["mean_trade_count_retention"]) else 0.0
    if mean_ret > 0 and pos_ratio >= (2.0 / 3.0) and mean_trades >= 12 and false_rate <= 0.52 and retention >= 0.45:
        return "P1 weak candidate / evidence pool", "最小 clean replication 至少没有直接塌掉：成本后仍为正，跨资产不只剩单腿，而且 trade retention 还没被砍穿。"
    return "park / evidence pool", "这条 CHoCH/压缩 gate 更像筛样本的结构 veto：成本后 pocket 仍不够统一，或 retention/false-hold 说明改善主要来自砍样本。"


def update_reading_report() -> None:
    if not READING_REPORT.exists():
        return
    text = READING_REPORT.read_text(encoding="utf-8")
    if "rank53_close_confirmed_choch_clean_replication.html" in text:
        return
    anchor = 'rank53_close_confirmed_choch_source_intake.html">Rank 53 source intake</a>'
    if anchor not in text:
        return
    text = text.replace(anchor, anchor + ' ｜ <a href="rank53_close_confirmed_choch_clean_replication.html">clean replication</a>', 1)
    READING_REPORT.write_text(text, encoding="utf-8")


def update_todo(verdict: str, generated_at: str, overall: pd.DataFrame, time_pockets: pd.DataFrame) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    primary = overall[
        (overall["setup"] == PRIMARY_SETUP)
        & (overall["variant"] == PRIMARY_VARIANT)
        & (overall["cost_bps_per_side"] == PRIMARY_COST)
    ]
    if primary.empty:
        stats = "主读法没有形成可用样本。"
    else:
        row = primary.iloc[0]
        stats = (
            f"主读法 `{PRIMARY_SETUP} + {PRIMARY_VARIANT}` 在 `6bps/side` 下跨资产 "
            f"`mean_total_return≈{pct(row['mean_total_return'])}`、`positive_asset_ratio≈{pct(row['positive_asset_ratio'])}`、"
            f"`mean_trades≈{num(row['mean_trades'],1)}`、`mean_trade_count_retention≈{pct(row['mean_trade_count_retention'])}`、"
            f"`mean_false_hold_4bars_rate≈{pct(row['mean_false_hold_4bars_rate'])}`。"
        )
    tp = time_pockets[
        (time_pockets["setup"] == PRIMARY_SETUP)
        & (time_pockets["variant"] == PRIMARY_VARIANT)
        & (time_pockets["cost_bps_per_side"] == PRIMARY_COST)
    ].copy()
    if tp.empty:
        pocket_text = "time-pocket 暂无可用样本。"
    else:
        parts = []
        for _, r in tp.iterrows():
            parts.append(
                f"{r['bucket']}≈{pct(r['mean_total_return'])} / {pct(r['positive_asset_ratio'])}"
            )
        pocket_text = "；".join(parts)

    anchor = "- **最新补充（2026-03-18 10:34 UTC）**：这轮已按 `Run 2 / fresh paper-repo intake` 完成 `Rank 53 / close-confirmed CHoCH compression gate` 的 `source intake + 两条轻量诚实守门`"
    if anchor not in text:
        raise RuntimeError("failed to find Rank 53 source-intake block anchor")
    insert = f"\n- **最新补充（{generated_at}）**：这轮已按顶板顺序把 `Rank 53 / close-confirmed CHoCH compression gate` 的唯一那手 **最小 clean replication** 跑完：固定复用 `BTC/ETH/SOL 120d 15m` cache，并重采样 `1h` confirmed pivot close，只在两条最小 archetype（`ema_pullback_long`、`breakdown_reclaim_short`）上比较 `base`、`htf_close_trend_gate`、`no_choch_no_flip`、`liquidity_sweep_veto` 四臂，统一冻结到 `15m next-bar open + no-overlap + hold 8 bars`。{stats}\n  - time-pocket：{pocket_text}。\n  - 当前更诚实的 hard verdict：**`Rank 53 / close-confirmed CHoCH compression gate = {verdict}`**。更直白地说：这条线已经不该继续停在 clean-replication 队列；若后续继续认领，默认只能按这个 verdict 走，而不是继续磨 intake wording。\n  - reader-facing 落点：`reports/site/factors/scout_rank53_close_confirmed_choch_15m/report.html`、`reports/site/reading/repo_scout/rank53_close_confirmed_choch_clean_replication.html`；artifact：`reports/artifacts/scout_rank53_close_confirmed_choch_15m/overall_summary.csv`。\n  - 排班含义：当前最新 `Next 3` 顺序应收紧为：**`Run 1 = EMA due-check only` -> `Run 2 = fresh paper/repo intake（若 EMA 仍 waiting_not_due，则先从 RECENT_PAPER_SEEDS / quant_digests / validated shortlist 再认领 1 条新的 5m / 15m crypto source）` -> `Run 3 = 若 fresh intake 也 exhausted，再比较 Rank 35b > Rank 16b > tiny-live plumbing`**。"
    text = text.replace(anchor, insert + "\n" + anchor, 1)
    TODO_PATH.write_text(text, encoding="utf-8")


def build_html(overall: pd.DataFrame, asset_summary: pd.DataFrame, time_pockets: pd.DataFrame, verdict: str, verdict_reason: str, generated_at: str) -> str:
    primary = overall[
        (overall["setup"] == PRIMARY_SETUP)
        & (overall["variant"] == PRIMARY_VARIANT)
        & (overall["cost_bps_per_side"] == PRIMARY_COST)
    ]
    if primary.empty:
        headline = "主读法没有形成可用样本。"
    else:
        row = primary.iloc[0]
        headline = (
            f"主读法 {PRIMARY_SETUP} + {PRIMARY_VARIANT} 在 {int(PRIMARY_COST)}bps/side 下：跨资产 mean_total_return≈{pct(row['mean_total_return'])}、"
            f"positive_asset_ratio≈{pct(row['positive_asset_ratio'])}、mean_trades≈{num(row['mean_trades'],1)}、"
            f"mean_trade_count_retention≈{pct(row['mean_trade_count_retention'])}、mean_false_hold_4bars_rate≈{pct(row['mean_false_hold_4bars_rate'])}。"
        )
    overall_view = overall.copy()
    overall_view["cost_bps_per_side"] = overall_view["cost_bps_per_side"].astype(int)
    asset_view = asset_summary.copy()
    asset_view["cost_bps_per_side"] = asset_view["cost_bps_per_side"].astype(int)
    pocket_view = time_pockets.copy()
    if not pocket_view.empty:
        pocket_view["cost_bps_per_side"] = pocket_view["cost_bps_per_side"].astype(int)
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 53 · close-confirmed CHoCH clean replication</title>
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
  <p><a href='../../reading/repo_scout/report.html'>← 返回 Repo Scout</a></p>
  <h1>Rank 53 · close-confirmed CHoCH compression gate</h1>
  <p class='muted'>生成时间：{escape(generated_at)} ｜ 类型：最小 clean replication ｜ 角色：Scout Seat 的 repo-based 15m crypto fast verdict</p>

  <div class='card'>
    <h2>这轮只回答什么</h2>
    <ul>
      <li>固定复用 <code>BTC/ETH/SOL 120d 15m</code> cache，不追新 bar。</li>
      <li>只比较两条 archetype：<code>ema_pullback_long</code>、<code>breakdown_reclaim_short</code>。</li>
      <li>结构 gate 只看 <code>1h confirmed pivot close</code>，并统一冻结为 <code>15m next-bar open -> no-overlap -> hold {HOLD_BARS} bars</code>。</li>
      <li>先回答四个便宜问题：<code>post_cost_return</code>、<code>false_hold_4bars_rate</code>、<code>trade_count_retention</code>、<code>time-pocket honesty</code>。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>clean-room 规则</h2>
    <ul>
      <li><b>base：</b>不看 1h CHoCH，只执行 15m base setup。</li>
      <li><b>htf_close_trend_gate：</b>只有当最新已确认 1h close-CHoCH 状态与 15m 方向一致时才允许入场。</li>
      <li><b>no_choch_no_flip：</b>若最新 1h close-CHoCH 已明确站到反方向，则拒绝 15m 入场；否则允许继续按原方向。</li>
      <li><b>liquidity_sweep_veto：</b>在上一臂基础上，再 veto 最近 {SWEEP_LOOKBACK_HOURS} 小时内出现的 wick-only 假突破/假跌破（上破不收上、下破不收下）。</li>
      <li><b>false hold：</b>触发后 {FALSE_LOOKAHEAD} 根内，若收盘反向跌破/涨破 signal bar 的失效位，则记为 early fail。</li>
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
    {render_table(overall_view[["setup","variant","cost_bps_per_side","mean_total_return","positive_asset_ratio","mean_trades","mean_trade_count_retention","mean_false_hold_4bars_rate","mean_win_rate"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_trade_count_retention","mean_false_hold_4bars_rate","mean_win_rate"}, digits_cols={"mean_trades":1})}
  </div>

  <div class='card'>
    <h2>分资产摘要</h2>
    {render_table(asset_view[["asset","setup","variant","cost_bps_per_side","trades","total_return","trade_count_retention","false_hold_4bars_rate","win_rate"]], percent_cols={"total_return","trade_count_retention","false_hold_4bars_rate","win_rate"}, digits_cols={"trades":0})}
  </div>

  <div class='card'>
    <h2>time-pocket honesty</h2>
    {render_table(pocket_view[["setup","variant","cost_bps_per_side","bucket","mean_total_return","positive_asset_ratio","mean_trades"]], percent_cols={"mean_total_return","positive_asset_ratio"}, digits_cols={"mean_trades":1})}
  </div>

  <div class='card'>
    <h2>artifact</h2>
    <ul>
      <li><a href='../../../artifacts/scout_rank53_close_confirmed_choch_15m/overall_summary.csv'>overall_summary.csv</a></li>
      <li><a href='../../../artifacts/scout_rank53_close_confirmed_choch_15m/asset_summary.csv'>asset_summary.csv</a></li>
      <li><a href='../../../artifacts/scout_rank53_close_confirmed_choch_15m/time_pocket_summary.csv'>time_pocket_summary.csv</a></li>
      <li><a href='../../../artifacts/scout_rank53_close_confirmed_choch_15m/trades_primary_6bps.csv'>trades_primary_6bps.csv</a></li>
      <li><a href='../../reading/repo_scout/rank53_close_confirmed_choch_source_intake.html'>source intake card</a></li>
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
    all_trades: list[pd.DataFrame] = []

    for asset, frame in frames.items():
        frame.to_csv(ART_DIR / f"{asset.lower().replace('-usd', '')}_frame.csv", index=False)
        for setup in SETUPS:
            base_count = int(sum(1 for idx in range(2, len(frame) - 2) if get_signal(frame, idx, setup, "base") is not None))
            for variant in VARIANTS:
                for cost in COSTS:
                    trades = build_trades(frame, asset, setup, variant, cost)
                    if setup == PRIMARY_SETUP and variant == PRIMARY_VARIANT and cost == PRIMARY_COST:
                        trades.to_csv(ART_DIR / f"trades_primary_6bps_{asset.lower().replace('-usd', '')}.csv", index=False)
                    all_trades.append(trades)
                    asset_rows.append(summarize_asset(trades, asset=asset, setup=setup, variant=variant, cost_bps=cost, base_count=base_count))

    non_empty = [df for df in all_trades if not df.empty]
    all_trades_df = pd.concat(non_empty, ignore_index=True) if non_empty else pd.DataFrame()
    if all_trades_df.empty:
        pd.DataFrame().to_csv(ART_DIR / "trades_primary_6bps.csv", index=False)
    else:
        all_trades_df[
            (all_trades_df["setup"] == PRIMARY_SETUP)
            & (all_trades_df["variant"] == PRIMARY_VARIANT)
            & (all_trades_df["cost_bps_per_side"] == PRIMARY_COST)
        ].to_csv(ART_DIR / "trades_primary_6bps.csv", index=False)

    asset_summary = pd.DataFrame(asset_rows)
    overall = summarize_overall(asset_summary)
    time_pockets = summarize_time_pockets(all_trades_df)
    verdict, verdict_reason = build_verdict(overall)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    time_pockets.to_csv(ART_DIR / "time_pocket_summary.csv", index=False)
    pd.DataFrame([
        {
            "generated_at_utc": generated_at,
            "candidate_id": "rank53_close_confirmed_choch_15m",
            "hard_verdict": verdict,
            "verdict_reason": verdict_reason,
        }
    ]).to_csv(ART_DIR / "meta.csv", index=False)

    html = build_html(overall, asset_summary, time_pockets, verdict, verdict_reason, generated_at)
    (SITE_DIR / "report.html").write_text(html, encoding="utf-8")
    (READING_DIR / "rank53_close_confirmed_choch_clean_replication.html").write_text(html, encoding="utf-8")

    update_reading_report()
    update_todo(verdict, generated_at, overall, time_pockets)

    print(f"verdict={verdict}")
    primary = overall[
        (overall["setup"] == PRIMARY_SETUP)
        & (overall["variant"] == PRIMARY_VARIANT)
        & (overall["cost_bps_per_side"] == PRIMARY_COST)
    ]
    if not primary.empty:
        print(primary.iloc[0].to_dict())


if __name__ == "__main__":
    main()
