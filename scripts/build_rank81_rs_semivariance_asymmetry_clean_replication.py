#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_15M_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
CACHE_5M_DIR = ROOT / "reports" / "artifacts" / "scout_rank66_exec_tf_switch_alignment_15m" / "spot_cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank81_rs_semivariance_asymmetry_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank81_rs_semivariance_asymmetry_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank81_rs_semivariance_asymmetry_clean_replication.html"
TODO_PATH = ROOT / "docs" / "TODO.md"
DUE_PATH = ROOT / "reports" / "artifacts" / "ema_psar_raw_alpha" / "ema_paper_trading_due_guardrail_snapshot.csv"
P3_SUMMARY_PATH = ROOT / "reports" / "artifacts" / "manual_narrow_paper_lanes" / "manual_narrow_paper_last_run_summary.json"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
SETUPS = ["ema_psar_long", "fib_retest_long", "breakout_short"]
LONG_SETUPS = {"ema_psar_long", "fib_retest_long"}
VARIANTS = ["baseline", "rs_veto", "rs_halfsize"]
PRIMARY_VARIANT = "rs_halfsize"
STRICT_VARIANT = "rs_veto"
COSTS = [6.0, 10.0, 15.0]
PRIMARY_COST = 6.0
HOLD_BARS = 8
EARLY_FAIL_BARS = 4
RS_WINDOW_5M = 12
ROLL_WINDOW_15M = 960
ROLL_MIN_15M = 96
TAIL_Q = 0.80
ASYM_Q = 0.20
CSS = """
body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width:1180px; margin:32px auto; padding:0 18px 48px; line-height:1.68; color:#111827; background:#f8fafc; }
h1,h2,h3 { color:#111827; }
.card { border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }
.muted { color:#6b7280; }
.good { color:#065f46; font-weight:600; }
.bad { color:#991b1b; font-weight:600; }
code { background:#f3f4f6; padding:1px 5px; border-radius:6px; }
table { width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; background:white; }
th, td { border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }
a { color:#2563eb; text-decoration:none; }
"""


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


def write_html(path: Path, title: str, body: str) -> None:
    path.write_text(
        f"<!doctype html><html><head><meta charset='utf-8'><title>{escape(title)}</title><style>{CSS}</style></head><body>{body}</body></html>",
        encoding="utf-8",
    )


def load_15m(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_15M_DIR / f"{symbol}__120d__15m.csv"
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def load_5m(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_5M_DIR / f"{symbol}_120d_5m.csv"
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


def build_base_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_15m(symbol, asset)
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema15"] = df["close"].ewm(span=15, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["vol_ma20"] = df["volume"].rolling(20, min_periods=20).mean()
    df["atr14"] = compute_atr(df)
    df["psar"] = compute_psar(df)
    df["rolling_low20"] = df["low"].rolling(20, min_periods=20).min().shift(1)
    df["swing_high_30"] = df["high"].rolling(30, min_periods=30).max().shift(1)
    df["swing_low_30"] = df["low"].rolling(30, min_periods=30).min().shift(1)
    rng = df["swing_high_30"] - df["swing_low_30"]
    df["fib_618"] = df["swing_high_30"] - 0.618 * rng
    df["fib_50"] = df["swing_high_30"] - 0.5 * rng
    df["ema_psar_long_signal"] = (
        (df["ema9"] > df["ema15"])
        & (df["ema_slope"] > 0.0003)
        & (df["psar"] < df["close"])
        & (df["close"] > df["high"].shift(1))
        & (df["close"].shift(1) < df["ema9"].shift(1))
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)
    df["fib_retest_long_signal"] = (
        df["fib_618"].notna()
        & (df["ema9"] > df["ema15"])
        & (df["ema_slope"] > 0)
        & (df["close"] > df["fib_618"])
        & (df["close"].shift(1) <= df["fib_618"].shift(1))
        & (df["low"] <= df["fib_618"] + 0.2 * df["atr14"])
        & (df["close"] > df["fib_50"])
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)
    low = df["rolling_low20"]
    atr = df["atr14"]
    df["breakout_short_signal"] = (
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


def build_rs_features(asset: str, symbol: str) -> pd.DataFrame:
    df = load_5m(symbol, asset)
    df["ret"] = df["close"].pct_change().fillna(0.0)
    df["rs_plus"] = np.square(np.clip(df["ret"], 0.0, None)).rolling(RS_WINDOW_5M, min_periods=RS_WINDOW_5M).sum()
    df["rs_minus"] = np.square(np.clip(-df["ret"], 0.0, None)).rolling(RS_WINDOW_5M, min_periods=RS_WINDOW_5M).sum()
    total = df["rs_plus"] + df["rs_minus"]
    df["asymmetry_score"] = (df["rs_plus"] - df["rs_minus"]) / total.replace(0.0, np.nan)
    out = df[["asset", "timestamp", "rs_plus", "rs_minus", "asymmetry_score"]].copy()
    out = out.rename(columns={"timestamp": "feature_timestamp"})
    return out


def direction_for_setup(setup: str) -> int:
    return 1 if setup in LONG_SETUPS else -1


def merge_feature_frame(base: pd.DataFrame, feat: pd.DataFrame) -> pd.DataFrame:
    merged = pd.merge_asof(
        base.sort_values("timestamp"),
        feat.sort_values("feature_timestamp"),
        left_on="timestamp",
        right_on="feature_timestamp",
        by="asset",
        direction="backward",
    )
    merged["asym_q20"] = merged["asymmetry_score"].shift(1).rolling(ROLL_WINDOW_15M, min_periods=ROLL_MIN_15M).quantile(ASYM_Q)
    merged["rs_plus_q80"] = merged["rs_plus"].shift(1).rolling(ROLL_WINDOW_15M, min_periods=ROLL_MIN_15M).quantile(TAIL_Q)
    merged["rs_minus_q80"] = merged["rs_minus"].shift(1).rolling(ROLL_WINDOW_15M, min_periods=ROLL_MIN_15M).quantile(TAIL_Q)
    merged["mixed_tail_extreme"] = (
        merged["rs_plus"].gt(merged["rs_plus_q80"])
        & merged["rs_minus"].gt(merged["rs_minus_q80"])
    ).fillna(False)
    merged["long_tail_ok"] = (
        merged["asymmetry_score"].ge(merged["asym_q20"])
        & ~merged["mixed_tail_extreme"]
    ).fillna(False)
    merged["short_tail_ok"] = (
        merged["asymmetry_score"].le(-merged["asym_q20"])
        & ~merged["mixed_tail_extreme"]
    ).fillna(False)
    merged["tail_ready"] = merged[["asym_q20", "rs_plus_q80", "rs_minus_q80"]].notna().all(axis=1)
    return merged


def variant_size(row: pd.Series, setup: str, variant: str) -> float:
    if variant == "baseline":
        return 1.0
    if not bool(row.get("tail_ready", False)):
        return 1.0 if variant == "rs_halfsize" else 0.0
    if bool(row.get("mixed_tail_extreme", False)):
        return 0.0
    is_long = direction_for_setup(setup) == 1
    tail_ok = bool(row.get("long_tail_ok", False) if is_long else row.get("short_tail_ok", False))
    if variant == "rs_veto":
        return 1.0 if tail_ok else 0.0
    if variant == "rs_halfsize":
        return 1.0 if tail_ok else 0.5
    raise ValueError(variant)


def build_signal_frame(frame: pd.DataFrame, setup: str, variant: str) -> pd.DataFrame:
    base = frame[f"{setup}_signal"] & ~frame[f"{setup}_signal"].shift(1).fillna(False)
    rows: list[dict[str, object]] = []
    last_exit = -1
    direction = direction_for_setup(setup)
    for idx in range(40, len(frame) - HOLD_BARS - 2):
        if idx <= last_exit or not bool(base.iloc[idx]):
            continue
        entry_idx = idx + 1
        exit_idx = entry_idx + HOLD_BARS
        if exit_idx >= len(frame):
            break
        size = variant_size(frame.iloc[idx], setup, variant)
        if size <= 0:
            continue
        entry_price = float(frame.iloc[entry_idx]["open"])
        exit_price = float(frame.iloc[exit_idx]["open"])
        gross_return = direction * (exit_price / entry_price - 1.0) * size
        path = frame.iloc[entry_idx : entry_idx + EARLY_FAIL_BARS + 1]
        if direction == 1:
            running = path["low"] / entry_price - 1.0
            early_fail = bool((path["close"] < frame.iloc[idx]["ema15"]).any())
        else:
            running = -(path["high"] / entry_price - 1.0)
            early_fail = bool((path["close"] > frame.iloc[idx]["ema15"]).any())
        rows.append(
            {
                "asset": frame.iloc[idx]["asset"],
                "setup": setup,
                "variant": variant,
                "timestamp": frame.iloc[idx]["timestamp"],
                "size": size,
                "gross_return": gross_return,
                "mae": float(running.min()) * size,
                "early_fail": early_fail,
                "tail_ready": bool(frame.iloc[idx].get("tail_ready", False)),
                "mixed_tail_extreme": bool(frame.iloc[idx].get("mixed_tail_extreme", False)),
                "asymmetry_score": float(frame.iloc[idx].get("asymmetry_score", np.nan)),
                "asym_q20": float(frame.iloc[idx].get("asym_q20", np.nan)),
                "rs_plus": float(frame.iloc[idx].get("rs_plus", np.nan)),
                "rs_minus": float(frame.iloc[idx].get("rs_minus", np.nan)),
                "tail_ok": bool(frame.iloc[idx].get("long_tail_ok", False) if direction == 1 else frame.iloc[idx].get("short_tail_ok", False)),
            }
        )
        last_exit = exit_idx
    return pd.DataFrame(rows)


def summarize_cost(trades: pd.DataFrame, cost_bps: float) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["asset", "setup", "variant", "trades", "avg_size", "trade_count_retention", "total_return", "expectancy", "early_fail_rate", "mae_mean", "tail_ready_ratio", "extreme_tail_ratio", "tail_ok_ratio"])
    cost = 2.0 * cost_bps / 10000.0
    df = trades.copy()
    df["net_return"] = df["gross_return"] - cost * df["size"]
    base_counts = (
        df[df["variant"] == "baseline"]
        .groupby(["asset", "setup"], as_index=False)
        .agg(base_trades=("timestamp", "count"))
    )
    out = (
        df.groupby(["asset", "setup", "variant"], as_index=False)
        .agg(
            trades=("timestamp", "count"),
            avg_size=("size", "mean"),
            total_return=("net_return", "sum"),
            expectancy=("net_return", "mean"),
            early_fail_rate=("early_fail", "mean"),
            mae_mean=("mae", "mean"),
            tail_ready_ratio=("tail_ready", "mean"),
            extreme_tail_ratio=("mixed_tail_extreme", "mean"),
            tail_ok_ratio=("tail_ok", "mean"),
        )
        .merge(base_counts, on=["asset", "setup"], how="left")
    )
    out["trade_count_retention"] = out["trades"] / out["base_trades"].replace(0, np.nan)
    return out.drop(columns=["base_trades"])


def overall_summary(summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for variant, g in summary.groupby("variant", sort=False):
        rows.append(
            {
                "variant": variant,
                "mean_total_return": g["total_return"].mean(),
                "mean_expectancy": g["expectancy"].mean(),
                "mean_trade_count_retention": g["trade_count_retention"].mean(),
                "mean_avg_size": g["avg_size"].mean(),
                "mean_early_fail_rate": g["early_fail_rate"].mean(),
                "mean_mae": g["mae_mean"].mean(),
                "mean_tail_ready_ratio": g["tail_ready_ratio"].mean(),
                "mean_extreme_tail_ratio": g["extreme_tail_ratio"].mean(),
                "mean_tail_ok_ratio": g["tail_ok_ratio"].mean(),
                "positive_cell_ratio": (g["total_return"] > 0).mean(),
                "cells": len(g),
            }
        )
    return pd.DataFrame(rows)


def by_setup_summary(summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (setup, variant), g in summary.groupby(["setup", "variant"], sort=False):
        rows.append(
            {
                "setup": setup,
                "variant": variant,
                "mean_total_return": g["total_return"].mean(),
                "mean_expectancy": g["expectancy"].mean(),
                "mean_trade_count_retention": g["trade_count_retention"].mean(),
                "mean_avg_size": g["avg_size"].mean(),
                "mean_early_fail_rate": g["early_fail_rate"].mean(),
                "mean_tail_ok_ratio": g["tail_ok_ratio"].mean(),
                "positive_asset_ratio": (g["total_return"] > 0).mean(),
            }
        )
    return pd.DataFrame(rows)


def verdict_from_overall(overall: pd.DataFrame) -> tuple[str, str]:
    base = overall.loc[overall["variant"].eq("baseline")].iloc[0]
    half = overall.loc[overall["variant"].eq(PRIMARY_VARIANT)].iloc[0]
    veto = overall.loc[overall["variant"].eq(STRICT_VARIANT)].iloc[0]
    improve_half = float(half["mean_expectancy"] - base["mean_expectancy"])
    improve_fail = float(base["mean_early_fail_rate"] - half["mean_early_fail_rate"])
    retention = float(half["mean_trade_count_retention"])
    pos_ratio = float(half["positive_cell_ratio"])
    veto_retention = float(veto["mean_trade_count_retention"])
    if improve_half > 0.00015 and improve_fail > 0.01 and retention >= 0.55 and pos_ratio >= 0.55:
        return (
            "promote_to_P2 / paper_candidate_pool",
            "half-size 版在交易保留率仍过半的前提下，同时改善了成本后 expectancy 与 4-bar fail；它已不只是概念证明，更像值得进入下一手决定性检查的 shared directional gate。",
        )
    if improve_half > -0.00010 and retention >= 0.45 and (improve_fail >= 0 or veto_retention < 0.35):
        return (
            "keep_P1 / evidence_pool",
            "RS+/RS- 非对称信息并非没用，但当前更像共享 veto / sizing 线索：half-size 比全 veto 更诚实，yet desk 级改善还不够统一，不足以直接升到 P2。",
        )
    return (
        "park / evidence_pool",
        "这轮最小 clean replication 没把方向尾部 gate 稳定地变成 desk 级提升；当前更诚实的位置是先 park，而不是继续默认占用 fast-lane 预算。",
    )


def read_due_text() -> str:
    due = pd.read_csv(DUE_PATH)
    earliest = due.sort_values("next_expected_close_utc").iloc[0]
    return f"全 desk 仍无 due-now / overdue；最近 due 点仍是 {earliest['deployment_scope']} -> {earliest['next_expected_close_utc']}。"


def read_p3_text() -> str:
    meta = json.loads(P3_SUMMARY_PATH.read_text(encoding="utf-8"))
    return f"manual narrow-paper 最新 refresh @ {meta.get('run_at_utc')}，new_closed_trades_appended={meta.get('new_closed_trades_appended', 0)}。"


def update_todo(generated_at: str, verdict: str, note: str) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    old_seat = "  - 因此当前更诚实的 seat 分级应同步读成：**`Rank 81 = P1 weak candidate（guard-passed / minimal clean replication next）`**、**`Rank 80 = P1（cheap honest check 已用 / keep_P1 / evidence_pool）`**、**`ETF lead regime gate` / `Fib trend-strength admission layer` = `P0 intake pool`**、**`Rank 78 = P3 narrow paper pilot（EMA-only suppression overlay）`**、**`Rank 17 / 2 / 29 / 32b = P3 narrow paper continuity`**、**`Rank 79 / 77 / 76 / 75 / 74 / 73 / 72 = P0 park / evidence pool`**；当前 **`P2` 仍空、`P4` 仍空**。"
    if "promote_to_P2" in verdict:
        new_seat = "  - 因此当前更诚实的 seat 分级应同步读成：**`Rank 81 = P2 paper candidate（minimal clean replication passed / ready for one decisive check）`**、**`Rank 80 = P1（cheap honest check 已用 / keep_P1 / evidence_pool）`**、**`ETF lead regime gate` / `Fib trend-strength admission layer` = `P0 intake pool`**、**`Rank 78 = P3 narrow paper pilot（EMA-only suppression overlay）`**、**`Rank 17 / 2 / 29 / 32b = P3 narrow paper continuity`**、**`Rank 79 / 77 / 76 / 75 / 74 / 73 / 72 = P0 park / evidence pool`**；当前 **`P2 = Rank 81`**、**`P4` 仍空**。"
    elif "keep_P1" in verdict:
        new_seat = "  - 因此当前更诚实的 seat 分级应同步读成：**`Rank 81 = P1（minimal clean replication done / keep_P1 / evidence_pool）`**、**`Rank 80 = P1（cheap honest check 已用 / keep_P1 / evidence_pool）`**、**`ETF lead regime gate` / `Fib trend-strength admission layer` = `P0 intake pool`**、**`Rank 78 = P3 narrow paper pilot（EMA-only suppression overlay）`**、**`Rank 17 / 2 / 29 / 32b = P3 narrow paper continuity`**、**`Rank 79 / 77 / 76 / 75 / 74 / 73 / 72 = P0 park / evidence pool`**；当前 **`P2` 仍空、`P4` 仍空**。"
    else:
        new_seat = "  - 因此当前更诚实的 seat 分级应同步读成：**`Rank 81 = P0 park / evidence pool`**、**`Rank 80 = P1（cheap honest check 已用 / keep_P1 / evidence_pool）`**、**`ETF lead regime gate` / `Fib trend-strength admission layer` = `P0 intake pool`**、**`Rank 78 = P3 narrow paper pilot（EMA-only suppression overlay）`**、**`Rank 17 / 2 / 29 / 32b = P3 narrow paper continuity`**、**`Rank 79 / 77 / 76 / 75 / 74 / 73 / 72 = P0 park / evidence pool`**；当前 **`P2` 仍空、`P4` 仍空**。"
    text = text.replace(old_seat, new_seat)

    marker = "### Next 3 bot3 runs（当前默认执行顺序）"
    old_block = "- **最新补充（2026-03-19 06:10 UTC）**：这轮已按顶板顺序完成 `Rank 81 / RS+/RS- realized-semivariance asymmetry gate` 的 source intake 与两条轻量诚实守门。当前更诚实的 hard verdict 是：**`Rank 81 = guard-passed / admit_to_clean_replication_queue`**。\n  - 因此当前最新 `Next 3` 顺序应更新为：**`Run 1 = EMA due-check only（若仍 waiting_not_due，不得空转）` -> `Run 2 = Rank 81 / RS+/RS- asymmetry gate minimal clean replication（仅当 EMA 仍 waiting_not_due）` -> `Run 3 = ETF lead regime gate > Fib trend-strength admission layer > 其他 fresh source；只有 Rank 81 这次最小 clean replication 已完成且 fresh source 这一层也 exhausted 时，才允许回退到 Rank 35b > Rank 16b > tiny-live plumbing；P3 continuity 仍不得默认抢占 Scout 主资源`**。"
    if "promote_to_P2" in verdict:
        next3 = "`Run 1 = EMA due-check only（若仍 waiting_not_due，不得空转）` -> `Run 2 = Rank 81 已升到 P2 后，只允许再做 1 个真正会改变 verdict 的最小检查；若本轮不继续做 P2，则切到 ETF lead regime gate > Fib trend-strength admission layer > 其他 fresh source` -> `Run 3 = 只有 Rank 81 决定性检查也完成或暂不值得继续时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing；P3 continuity 仍不得默认抢占 Scout 主资源`"
    else:
        next3 = "`Run 1 = EMA due-check only（若仍 waiting_not_due，不得空转）` -> `Run 2 = ETF lead regime gate > Fib trend-strength admission layer > 其他 fresh source` -> `Run 3 = 只有 fresh source 这一层也 exhausted 时，才允许回退到 Rank 35b > Rank 16b > tiny-live plumbing；P3 continuity 仍不得默认抢占 Scout 主资源`"
    new_block = (
        f"- **最新补充（{generated_at}）**：这轮已按顶板顺序完成 `Rank 81 / RS+/RS- realized-semivariance asymmetry gate` 的唯一那手最小 clean replication：固定复用 `BTC/ETH/SOL 120d 15m + 5m` 本地 cache，只比较 `baseline / rs_veto / rs_halfsize` 三臂，统一冻结到 **`signal 当根及之前数据 + next-bar open + no-overlap + hold {HOLD_BARS} bars`**；其中 `RS+ / RS-` 只使用信号当根及之前最近 `12` 根 `5m` 收益构造，阈值统一走 `15m` 级 trailing quantile，不允许 future tail 信息倒灌。当前更诚实的 hard verdict 是：**`Rank 81 = {verdict}`**；{note}\n"
        f"  - 因此当前最新 `Next 3` 顺序应更新为：**{next3}**。"
    )
    if old_block in text:
        text = text.replace(old_block, new_block)
    elif marker in text:
        start = text.find(marker)
        line_end = text.find("\n", start)
        text = text[: line_end + 1] + new_block + "\n\n" + text[line_end + 1 :]
    TODO_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    trade_frames = []
    feature_rows = []
    for asset, symbol in ASSETS.items():
        base = build_base_frame(asset, symbol)
        feat = build_rs_features(asset, symbol)
        merged = merge_feature_frame(base, feat)
        feature_rows.append(merged[["asset", "timestamp", "rs_plus", "rs_minus", "asymmetry_score", "asym_q20", "rs_plus_q80", "rs_minus_q80", "mixed_tail_extreme", "long_tail_ok", "short_tail_ok", "tail_ready"]].copy())
        for setup in SETUPS:
            for variant in VARIANTS:
                trade_frames.append(build_signal_frame(merged, setup, variant))

    all_trades = pd.concat(trade_frames, ignore_index=True)
    all_features = pd.concat(feature_rows, ignore_index=True)

    cost_summaries: list[pd.DataFrame] = []
    overall_frames: list[pd.DataFrame] = []
    by_setup_frames: list[pd.DataFrame] = []
    for cost in COSTS:
        s = summarize_cost(all_trades, cost)
        s["cost_bps_per_side"] = cost
        cost_summaries.append(s)
        o = overall_summary(s)
        o["cost_bps_per_side"] = cost
        overall_frames.append(o)
        bs = by_setup_summary(s)
        bs["cost_bps_per_side"] = cost
        by_setup_frames.append(bs)

    summary = pd.concat(cost_summaries, ignore_index=True)
    overall = pd.concat(overall_frames, ignore_index=True)
    by_setup = pd.concat(by_setup_frames, ignore_index=True)
    primary_overall = overall[overall["cost_bps_per_side"].eq(PRIMARY_COST)].reset_index(drop=True)
    verdict, verdict_note = verdict_from_overall(primary_overall)

    all_features.to_csv(ART_DIR / "rs_feature_snapshot.csv", index=False)
    all_trades.to_csv(ART_DIR / "trade_samples.csv", index=False)
    summary.to_csv(ART_DIR / "per_asset_setup_summary.csv", index=False)
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    by_setup.to_csv(ART_DIR / "by_setup_summary.csv", index=False)

    base = primary_overall.loc[primary_overall["variant"].eq("baseline")].iloc[0]
    veto = primary_overall.loc[primary_overall["variant"].eq("rs_veto")].iloc[0]
    half = primary_overall.loc[primary_overall["variant"].eq("rs_halfsize")].iloc[0]

    body = f"""
<h1>Rank 81 / RS+/RS- realized-semivariance asymmetry gate</h1>
<p class='muted'>生成时间：{escape(generated_at)} ｜ 最小 clean replication：固定复用 BTC/ETH/SOL 120d 15m + 5m 本地 cache；比较 baseline / rs_veto / rs_halfsize；执行统一 <code>signal 当根及之前数据 + next-bar open + no-overlap + hold {HOLD_BARS} bars</code>。</p>
<div class='card'>
  <p><strong>先核对 desk 状态：</strong>{escape(read_due_text())} {escape(read_p3_text())}</p>
  <p><strong>RS 冻结口径：</strong>每个 15m 决策时点只使用当根及之前最近 <code>{RS_WINDOW_5M}</code> 根 <code>5m</code> 收益构造 <code>RS+</code>、<code>RS-</code> 与 <code>A=(RS+-RS-)/(RS++RS-)</code>；阈值全部来自过去 <code>{ROLL_WINDOW_15M}</code> 个 15m 时点的 trailing quantile。它只做 directional veto / half-size，不偷渡成独立 alpha。</p>
</div>
<div class='card'>
  <p><strong>6bps/side desk 级结果：</strong></p>
  <ul>
    <li><code>baseline</code>：mean total return ≈ <strong>{pct(base['mean_total_return'])}</strong>，mean expectancy ≈ <strong>{pct(base['mean_expectancy'], 3)}</strong>，early-fail ≈ <strong>{pct(base['mean_early_fail_rate'])}</strong></li>
    <li><code>rs_veto</code>：mean total return ≈ <strong>{pct(veto['mean_total_return'])}</strong>，expectancy ≈ <strong>{pct(veto['mean_expectancy'], 3)}</strong>，retention ≈ <strong>{pct(veto['mean_trade_count_retention'])}</strong></li>
    <li><code>rs_halfsize</code>：mean total return ≈ <strong>{pct(half['mean_total_return'])}</strong>，expectancy ≈ <strong>{pct(half['mean_expectancy'], 3)}</strong>，retention ≈ <strong>{pct(half['mean_trade_count_retention'])}</strong>，avg size ≈ <strong>{num(half['mean_avg_size'], 2)}x</strong>，early-fail ≈ <strong>{pct(half['mean_early_fail_rate'])}</strong></li>
  </ul>
  <p><strong>Hard verdict：</strong><span class='{'good' if 'promote' in verdict else 'bad' if 'park' in verdict else 'muted'}'>{escape(verdict)}</span>。{escape(verdict_note)}</p>
</div>
<div class='card'>
  <h2>Overall summary</h2>
  {render_table(primary_overall[["variant", "mean_total_return", "mean_expectancy", "mean_trade_count_retention", "mean_avg_size", "mean_early_fail_rate", "mean_mae", "mean_tail_ready_ratio", "mean_extreme_tail_ratio", "mean_tail_ok_ratio", "positive_cell_ratio", "cells"]], percent_cols={"mean_total_return", "mean_expectancy", "mean_trade_count_retention", "mean_early_fail_rate", "mean_mae", "mean_tail_ready_ratio", "mean_extreme_tail_ratio", "mean_tail_ok_ratio", "positive_cell_ratio"}, digits_cols={"mean_avg_size": 2})}
</div>
<div class='card'>
  <h2>By setup @ 6bps/side</h2>
  {render_table(by_setup[by_setup['cost_bps_per_side'].eq(PRIMARY_COST)][["setup", "variant", "mean_total_return", "mean_expectancy", "mean_trade_count_retention", "mean_avg_size", "mean_early_fail_rate", "mean_tail_ok_ratio", "positive_asset_ratio"]], percent_cols={"mean_total_return", "mean_expectancy", "mean_trade_count_retention", "mean_early_fail_rate", "mean_tail_ok_ratio", "positive_asset_ratio"}, digits_cols={"mean_avg_size": 2})}
</div>
"""
    write_html(SITE_DIR / "report.html", "Rank 81 RS asymmetry clean replication", body)

    reading_body = f"""
<h1>Rank 81 clean replication：RS+/RS- 非对称像 shared directional gate，不是新 alpha</h1>
<p class='muted'>生成时间：{escape(generated_at)}｜只做 1 次最小 clean replication。</p>
<div class='card'>
  <p>这轮没有回头挤占 EMA paper continuity。原因很简单：{escape(read_due_text())} {escape(read_p3_text())}</p>
  <p>因此本轮合法主动作就是 <strong>Run 2 / Rank 81</strong>：固定复用本地 <code>BTC/ETH/SOL 120d 15m + 5m</code> cache，把 <code>RS+ / RS-</code> 非对称只接成 shared directional veto / half-size，并直接比较 <code>baseline / rs_veto / rs_halfsize</code> 三臂。</p>
  <p>当前最诚实的结论是：<strong>{escape(verdict)}</strong>。{escape(verdict_note)}</p>
  <p>网页落点：<a href="../factors/scout_rank81_rs_semivariance_asymmetry_15m/report.html">factor report</a></p>
</div>
"""
    write_html(READING_PATH, "Rank 81 RS asymmetry clean replication", reading_body)
    update_todo(generated_at, verdict, verdict_note)


if __name__ == "__main__":
    main()
