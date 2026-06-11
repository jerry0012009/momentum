#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank92_opening_drive_adaptive_offset_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank92_opening_drive_adaptive_offset_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank92_opening_drive_adaptive_offset_clean_replication.html"
TODO_PATH = ROOT / "docs" / "TODO.md"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
SETUPS = ["ema_psar_long", "fib_retest_long", "breakout_short"]
LONG_SETUPS = {"ema_psar_long", "fib_retest_long"}
VARIANTS = ["baseline", "adaptive_offset_gate", "adaptive_offset_halfsize"]
PRIMARY_VARIANT = "adaptive_offset_gate"
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0]
HOLD_BARS = 8
EARLY_FAIL_BARS = 4
OPENING_DRIVE_BARS = 4  # UTC 日内前 1h，作为 24/7 crypto 的最小代理锚点
MIN_OFFSET_PCT = 0.0005  # 5 bps，避免零偏移
CSS = """
body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width:1150px; margin:40px auto; padding:0 18px 48px; line-height:1.72; color:#111827; background:#f8fafc; }
.card { border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }
.pill { display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }
.muted { color:#6b7280; }
code { background:#f3f4f6; padding:1px 5px; border-radius:6px; }
table { width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; background:white; }
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


def session_vwap_features(day_df: pd.DataFrame) -> pd.DataFrame:
    out = day_df.copy()
    tp = (out["high"] + out["low"] + out["close"]) / 3.0
    cum_vol = out["volume"].cumsum().replace(0, np.nan)
    out["session_vwap"] = (tp * out["volume"]).cumsum() / cum_vol

    drive = out.iloc[:OPENING_DRIVE_BARS]
    if len(drive) < OPENING_DRIVE_BARS:
        out["drive_high"] = np.nan
        out["drive_low"] = np.nan
        out["drive_mid"] = np.nan
        out["drive_range"] = np.nan
        out["adaptive_offset_abs"] = np.nan
        out["drive_ready"] = False
        return out

    drive_high = float(drive["high"].max())
    drive_low = float(drive["low"].min())
    drive_mid = (drive_high + drive_low) / 2.0
    drive_range = max(drive_high - drive_low, 0.0)
    min_abs = max(drive_mid * MIN_OFFSET_PCT, 0.0)

    out["drive_high"] = drive_high
    out["drive_low"] = drive_low
    out["drive_mid"] = drive_mid
    out["drive_range"] = drive_range
    out["adaptive_offset_abs"] = np.maximum((out["session_vwap"] - drive_mid).abs(), 0.15 * drive_range)
    out["adaptive_offset_abs"] = np.maximum(out["adaptive_offset_abs"], min_abs)
    out["drive_ready"] = np.arange(len(out)) >= OPENING_DRIVE_BARS
    return out


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_bars(symbol, asset)
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema15"] = df["close"].ewm(span=15, adjust=False).mean()
    df["ema34"] = df["close"].ewm(span=34, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["vol_ma20"] = df["volume"].rolling(20, min_periods=20).mean()
    df["atr14"] = compute_atr(df)
    df["psar"] = compute_psar(df)
    df["day_utc"] = df["timestamp"].dt.floor("D")
    df = pd.concat([session_vwap_features(g) for _, g in df.groupby("day_utc", sort=True)], ignore_index=True)

    df["swing_high_30"] = df["high"].rolling(30, min_periods=30).max().shift(1)
    df["swing_low_30"] = df["low"].rolling(30, min_periods=30).min().shift(1)
    rng = df["swing_high_30"] - df["swing_low_30"]
    df["fib_618"] = df["swing_high_30"] - 0.618 * rng
    df["fib_50"] = df["swing_high_30"] - 0.5 * rng
    df["rolling_low20"] = df["low"].rolling(20, min_periods=20).min().shift(1)
    atr = df["atr14"]

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
        & (df["low"] <= df["fib_618"] + 0.2 * atr)
        & (df["close"] > df["fib_50"])
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)

    low = df["rolling_low20"]
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


def direction_for_setup(setup: str) -> int:
    return 1 if setup in LONG_SETUPS else -1


def gate_pass(frame: pd.DataFrame, setup: str) -> pd.Series:
    long_side = setup in LONG_SETUPS
    ready = frame["drive_ready"].fillna(False)
    if long_side:
        return ready & (frame["close"] > (frame["drive_high"] + frame["adaptive_offset_abs"]))
    return ready & (frame["close"] < (frame["drive_low"] - frame["adaptive_offset_abs"]))


def build_signal_frame(frame: pd.DataFrame, asset: str, setup: str, variant: str) -> pd.DataFrame:
    base = frame[f"{setup}_signal"] & ~frame[f"{setup}_signal"].shift(1).fillna(False)
    pass_gate = gate_pass(frame, setup).fillna(False)
    rows: list[dict[str, object]] = []
    last_exit = -1
    direction = direction_for_setup(setup)
    for idx in range(40, len(frame) - HOLD_BARS - 2):
        if idx <= last_exit or not bool(base.iloc[idx]):
            continue
        gate_ok = bool(pass_gate.iloc[idx])
        if variant == "adaptive_offset_gate" and not gate_ok:
            continue
        size_mult = 1.0 if (variant != "adaptive_offset_halfsize" or gate_ok) else 0.5
        entry_idx = idx + 1
        exit_idx = entry_idx + HOLD_BARS
        if exit_idx >= len(frame):
            break
        entry_price = float(frame.iloc[entry_idx]["open"])
        exit_price = float(frame.iloc[exit_idx]["open"])
        gross_return = direction * (exit_price / entry_price - 1.0) * size_mult
        path = frame.iloc[entry_idx : entry_idx + EARLY_FAIL_BARS + 1]
        if direction == 1:
            fail_back_inside4 = bool((path["close"] <= frame.iloc[idx]["drive_high"]).any())
            hold4 = bool((path["close"] > frame.iloc[idx]["drive_high"] + frame.iloc[idx]["adaptive_offset_abs"]).all())
        else:
            fail_back_inside4 = bool((path["close"] >= frame.iloc[idx]["drive_low"]).any())
            hold4 = bool((path["close"] < frame.iloc[idx]["drive_low"] - frame.iloc[idx]["adaptive_offset_abs"]).all())
        win8 = gross_return > 0
        rows.append(
            {
                "signal_id": f"{asset}|{setup}|{variant}|{idx}",
                "asset": asset,
                "setup": setup,
                "variant": variant,
                "direction": direction,
                "signal_idx": idx,
                "entry_idx": entry_idx,
                "exit_idx": exit_idx,
                "signal_ts": pd.to_datetime(frame.iloc[idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_ts": pd.to_datetime(frame.iloc[entry_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": pd.to_datetime(frame.iloc[exit_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_price": entry_price,
                "exit_price": exit_price,
                "gross_return": gross_return,
                "gate_pass": gate_ok,
                "size_mult": size_mult,
                "drive_high": float(frame.iloc[idx]["drive_high"]) if pd.notna(frame.iloc[idx]["drive_high"]) else np.nan,
                "drive_low": float(frame.iloc[idx]["drive_low"]) if pd.notna(frame.iloc[idx]["drive_low"]) else np.nan,
                "drive_mid": float(frame.iloc[idx]["drive_mid"]) if pd.notna(frame.iloc[idx]["drive_mid"]) else np.nan,
                "drive_range": float(frame.iloc[idx]["drive_range"]) if pd.notna(frame.iloc[idx]["drive_range"]) else np.nan,
                "session_vwap": float(frame.iloc[idx]["session_vwap"]) if pd.notna(frame.iloc[idx]["session_vwap"]) else np.nan,
                "adaptive_offset_abs": float(frame.iloc[idx]["adaptive_offset_abs"]) if pd.notna(frame.iloc[idx]["adaptive_offset_abs"]) else np.nan,
                "adaptive_offset_pct": float(frame.iloc[idx]["adaptive_offset_abs"] / frame.iloc[idx]["close"]) if pd.notna(frame.iloc[idx]["adaptive_offset_abs"]) and frame.iloc[idx]["close"] else np.nan,
                "fail_back_inside4": fail_back_inside4,
                "hold4": hold4,
                "win8": win8,
            }
        )
        last_exit = exit_idx
    return pd.DataFrame(rows)


def summarize_variant(trades: pd.DataFrame, cost_bps_side: float) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["setup", "variant", "trade_count", "mean_net_return", "total_net_return", "fail_back_inside4", "hold4", "win8", "mean_position_size", "mean_adaptive_offset_pct"])
    cost = 2.0 * cost_bps_side / 10000.0
    t = trades.copy()
    t["net_return"] = t["gross_return"] - cost * t["size_mult"]
    out = (
        t.groupby(["setup", "variant"], as_index=False)
        .agg(
            trade_count=("signal_id", "count"),
            mean_net_return=("net_return", "mean"),
            total_net_return=("net_return", "sum"),
            fail_back_inside4=("fail_back_inside4", "mean"),
            hold4=("hold4", "mean"),
            win8=("win8", "mean"),
            mean_position_size=("size_mult", "mean"),
            mean_adaptive_offset_pct=("adaptive_offset_pct", "mean"),
        )
    )
    return out.sort_values(["setup", "variant"]).reset_index(drop=True)


def compare_against_baseline(summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for setup, g in summary.groupby("setup"):
        base = g[g["variant"] == "baseline"]
        if base.empty:
            continue
        base_row = base.iloc[0]
        base_count = float(base_row["trade_count"]) if pd.notna(base_row["trade_count"]) else np.nan
        for _, row in g.iterrows():
            retention = np.nan
            if base_count and not pd.isna(base_count):
                retention = float(row["trade_count"]) / base_count
            rows.append(
                {
                    "setup": setup,
                    "variant": row["variant"],
                    "trade_count": row["trade_count"],
                    "retention": retention,
                    "mean_net_return": row["mean_net_return"],
                    "total_net_return": row["total_net_return"],
                    "fail_back_inside4": row["fail_back_inside4"],
                    "hold4": row["hold4"],
                    "win8": row["win8"],
                    "mean_position_size": row["mean_position_size"],
                    "mean_adaptive_offset_pct": row["mean_adaptive_offset_pct"],
                    "delta_total_vs_baseline": float(row["total_net_return"] - base_row["total_net_return"]),
                    "delta_hold4_vs_baseline": float(row["hold4"] - base_row["hold4"]),
                    "delta_fail_back_inside4_vs_baseline": float(row["fail_back_inside4"] - base_row["fail_back_inside4"]),
                }
            )
    return pd.DataFrame(rows)


def build_per_asset_summary(trades: pd.DataFrame, cost_bps_side: float) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame()
    cost = 2.0 * cost_bps_side / 10000.0
    t = trades.copy()
    t["net_return"] = t["gross_return"] - cost * t["size_mult"]
    out = (
        t.groupby(["asset", "setup", "variant"], as_index=False)
        .agg(
            trade_count=("signal_id", "count"),
            mean_net_return=("net_return", "mean"),
            total_net_return=("net_return", "sum"),
            fail_back_inside4=("fail_back_inside4", "mean"),
            hold4=("hold4", "mean"),
            win8=("win8", "mean"),
            mean_position_size=("size_mult", "mean"),
        )
    )
    return out.sort_values(["asset", "setup", "variant"]).reset_index(drop=True)


def build_overall_summary(summary6: pd.DataFrame, per_asset6: pd.DataFrame) -> pd.DataFrame:
    rows = []
    if summary6.empty:
        return pd.DataFrame()
    for variant in VARIANTS:
        hit = summary6[summary6["variant"] == variant].copy()
        asset_hit = per_asset6[per_asset6["variant"] == variant].copy() if not per_asset6.empty else pd.DataFrame()
        if hit.empty:
            continue
        asset_totals = asset_hit.groupby("asset")["total_net_return"].sum() if not asset_hit.empty else pd.Series(dtype=float)
        rows.append(
            {
                "variant": variant,
                "mean_total_return": float(hit["total_net_return"].mean()),
                "positive_asset_ratio": float((asset_totals > 0).mean()) if not asset_totals.empty else np.nan,
                "retention": float(hit["trade_count"].sum() / summary6[summary6["variant"] == "baseline"]["trade_count"].sum()) if summary6[summary6["variant"] == "baseline"]["trade_count"].sum() else np.nan,
                "mean_hold4": float(hit["hold4"].mean()),
                "mean_fail_back_inside4": float(hit["fail_back_inside4"].mean()),
                "mean_win8": float(hit["win8"].mean()),
                "mean_position_size": float(hit["mean_position_size"].mean()),
                "trade_count": int(hit["trade_count"].sum()),
            }
        )
    return pd.DataFrame(rows)


def build_time_bucket_summary(trades: pd.DataFrame, cost_bps_side: float) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame()
    cost = 2.0 * cost_bps_side / 10000.0
    t = trades.copy()
    t["net_return"] = t["gross_return"] - cost * t["size_mult"]
    ts = pd.to_datetime(t["entry_ts"], utc=True)
    q1, q2 = ts.quantile([1 / 3, 2 / 3])
    t["bucket"] = np.where(ts <= q1, "bucket_1", np.where(ts <= q2, "bucket_2", "bucket_3"))
    out = (
        t.groupby(["variant", "bucket"], as_index=False)
        .agg(
            trade_count=("signal_id", "count"),
            mean_net_return=("net_return", "mean"),
            hold4=("hold4", "mean"),
            fail_back_inside4=("fail_back_inside4", "mean"),
        )
    )
    return out.sort_values(["variant", "bucket"]).reset_index(drop=True)


def choose_verdict(overall: pd.DataFrame) -> tuple[str, str]:
    gate = overall[overall["variant"] == "adaptive_offset_gate"]
    half = overall[overall["variant"] == "adaptive_offset_halfsize"]
    if gate.empty or half.empty:
        return "park / evidence pool", "没有拿到完整三臂结果，当前不配升格。"
    gate_row = gate.iloc[0]
    half_row = half.iloc[0]
    if float(gate_row["mean_total_return"]) > 0 and float(gate_row["positive_asset_ratio"]) >= 2/3 and float(gate_row["retention"]) >= 0.75:
        return "promote_to_P2 / paper candidate", "gate 版在 desk 级给出正向 post-cost 改善、跨资产不坏且 retention 尚可，足以升到更窄 paper candidate。"
    if float(half_row["mean_total_return"]) > float(gate_row["mean_total_return"]) and float(half_row["positive_asset_ratio"]) >= float(gate_row["positive_asset_ratio"]):
        return "keep_P1", "完全 veto 的 gate 没有给出足够统一的改善，但 half-size 读法至少保留了更多样本，当前更诚实的是保留成 P1 弱候选，而不是直接吹成 P2。"
    return "park / evidence pool", "gate 与 half-size 都没把 desk 级结果真正拉正；若只在单 setup/单资产局部改善，就应直接 park。"


def render_html(title: str, compare: pd.DataFrame, per_asset: pd.DataFrame, overall: pd.DataFrame, buckets: pd.DataFrame, verdict: str, why: str) -> str:
    body = [
        f"<h1>{escape(title)}</h1>",
        '<p class="muted">Rank 92 / opening-drive adaptive offset continuation gate 的最小 clean replication。口径：BTC/ETH/SOL、120d、15m、signal 当根及之前数据、next-bar open、no-overlap、hold 8 bars；opening-drive 先冻结为 UTC 日内前 4 根 15m bar 的代理锚点。</p>',
        '<div class="card">'
        '<span class="pill">Run 2</span><span class="pill">Scout Seat</span><span class="pill">reader-facing</span>'
        f'<p><strong>Hard verdict：</strong>{escape(verdict)}</p>'
        f'<p>{escape(why)}</p>'
        '<p class="muted">三臂定义：baseline = 原始 setup；adaptive_offset_gate = 只有穿过 drive_edge ± adaptive_offset 才放行；adaptive_offset_halfsize = 没穿过时保留半仓。</p>'
        '</div>',
        '<div class="card"><h2>6bps/side desk 级主摘要</h2>' + render_table(overall, {"mean_total_return", "positive_asset_ratio", "retention", "mean_hold4", "mean_fail_back_inside4", "mean_win8"}, {"trade_count": 0, "mean_position_size": 2}) + '</div>',
        '<div class="card"><h2>按 setup 对 baseline 的增减</h2>' + render_table(compare, {"retention", "mean_net_return", "total_net_return", "fail_back_inside4", "hold4", "win8", "mean_adaptive_offset_pct", "delta_total_vs_baseline", "delta_hold4_vs_baseline", "delta_fail_back_inside4_vs_baseline"}, {"trade_count": 0, "mean_position_size": 2}) + '</div>',
        '<div class="card"><h2>按资产汇总</h2>' + render_table(per_asset, {"mean_net_return", "total_net_return", "fail_back_inside4", "hold4", "win8"}, {"trade_count": 0, "mean_position_size": 2}) + '</div>',
        '<div class="card"><h2>时间分桶（为下一轮 Light Stability Pack 预备）</h2>' + render_table(buckets, {"mean_net_return", "hold4", "fail_back_inside4"}, {"trade_count": 0}) + '</div>',
    ]
    return f"<!doctype html><html><head><meta charset='utf-8'><title>{escape(title)}</title><style>{CSS}</style></head><body>{''.join(body)}</body></html>"


def update_todo(verdict: str, overall: pd.DataFrame, compare: pd.DataFrame) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    target = "- **最新补充（2026-03-19 16:01 UTC）**：当前最新 `Next 3` 顺序应再次收紧为：**`Run 1 = EMA due-check only（若脚本仍返回 waiting_not_due，不得空转，也不得伪造 refresh）` -> `Run 2 = 若 EMA 仍 waiting_not_due，则只给 Rank 92 / opening-drive adaptive offset continuation gate 1 次最小 clean replication（固定 BTC/ETH/SOL 15m；比较 baseline / adaptive_offset_gate / adaptive_offset_halfsize；统一 signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars），并直接做 keep_P1 / promote_to_P2 / park 判断` -> `Run 3 = 分支执行：若 Rank 92 仍存活，则只给 1 个 truly verdict-changing 的 Light Stability Pack（默认先做时间稳定性，并直接回答 promote_to_P2 / keep_P1 / park）；若 Rank 92 在 clean replication 直接 hard-fail / park，则切 Rank 95 / Vajra controlled-pullback depth-budget 的 source intake + 两条轻量诚实守门；只有 fresh source 这一层也 exhausted，才允许继续回退到 Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool > P3 continuity > tiny-live plumbing`**。"
    gate_row = overall[overall["variant"] == "adaptive_offset_gate"].iloc[0]
    half_row = overall[overall["variant"] == "adaptive_offset_halfsize"].iloc[0]
    setup_bits = []
    for setup in ["ema_psar_long", "fib_retest_long", "breakout_short"]:
        hit = compare[(compare["setup"] == setup) & (compare["variant"] == "adaptive_offset_gate")]
        if hit.empty:
            continue
        row = hit.iloc[0]
        setup_bits.append(f"`{setup}`: total≈{pct(row['total_net_return'])} / retention≈{pct(row['retention'])} / hold4≈{pct(row['hold4'])} / fail_back_inside4≈{pct(row['fail_back_inside4'])}")
    setup_blob = "；".join(setup_bits)
    addition = (
        f"\n- **最新补充（2026-03-19 16:07 UTC）**：这轮继续严格按 `Run 1 -> Run 2` 执行：再次实际跑 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`，脚本仍返回 **`waiting_not_due`**（当前无 `due-now / overdue` lane；最近 due 约为 `美股 3.9h`、`Crypto 7.9h`、`A股 14.9h`），因此本轮合法主动作就是把 **`Rank 92 / opening-drive adaptive offset continuation gate`** 的那 1 次最小 clean replication 跑完。\n"
        f"  - 这轮固定复用 `BTC/ETH/SOL 120d 15m` 本地 cache，统一冻结到 **`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`**，比较 `baseline`、`adaptive_offset_gate`、`adaptive_offset_halfsize` 三臂；`opening-drive` 先诚实冻结成 **UTC 日内前 4 根 15m bar** 的 desk 代理锚点，`adaptive_offset = max(|drive_mid-sessionVWAP|, 0.15*drive_range, 5bps*price)`。\n"
        f"  - `6bps/side` 下，desk 级汇总为：`adaptive_offset_gate mean_total_return≈{pct(gate_row['mean_total_return'])}` / `positive_asset_ratio≈{pct(gate_row['positive_asset_ratio'])}` / `retention≈{pct(gate_row['retention'])}`；`adaptive_offset_halfsize mean_total_return≈{pct(half_row['mean_total_return'])}` / `positive_asset_ratio≈{pct(half_row['positive_asset_ratio'])}` / `retention≈{pct(half_row['retention'])}`。setup 侧读法：{setup_blob}。\n"
        f"  - 因此当前更诚实的 hard verdict 收口为：**`Rank 92 = {verdict}`**。如果 `adaptive_offset_gate` 没把 desk 级结果真正拉成统一 shared 改善，就不该继续把它写得比证据更大；若只剩 half-size 还能保留一点边际，就保留 `P1 weak candidate` 身份，下一轮再只给 1 个 truly verdict-changing 的 `Light Stability Pack / 时间稳定性`。\n"
        f"  - reader-facing 落点已补：`reports/site/factors/scout_rank92_opening_drive_adaptive_offset_15m/report.html`、`reports/site/reading/repo_scout/rank92_opening_drive_adaptive_offset_clean_replication.html`；artifact：`reports/artifacts/scout_rank92_opening_drive_adaptive_offset_15m/overall_summary.csv`、`setup_compare.csv`、`per_asset_summary.csv`。\n"
    )
    if verdict == "park / evidence pool":
        addition += "  - 当前 active Scout 顺序应同步改写为：**`Rank 95 / Vajra controlled-pullback depth-budget`** > **`Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool`** > **`Rank 92 park / evidence_pool`** > **`Rank 94 park / evidence_pool`** > **`P3 continuity`** > **`tiny-live plumbing`**。\n"
        addition += "  - 因此当前最新 `Next 3` 顺序应更新为：**`Run 1 = EMA due-check only` -> `Run 2 = 若 EMA 仍 waiting_not_due，则切 Rank 95 / Vajra controlled-pullback depth-budget 的 source intake + 两条轻量诚实守门` -> `Run 3 = 只有 Rank 95 intake 直接 hard-fail / exhausted，才允许回退到 Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool；P3 continuity 与 tiny-live plumbing 继续不得插队`**。"
    else:
        addition += "  - 当前 active Scout 顺序应同步改写为：**`Rank 92 = P1 weak candidate（minimal time-stability next）`** > **`Rank 95 / Vajra controlled-pullback depth-budget`** > **`Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool`** > **`Rank 94 park / evidence_pool`** > **`P3 continuity`** > **`tiny-live plumbing`**。\n"
        addition += "  - 因此当前最新 `Next 3` 顺序应更新为：**`Run 1 = EMA due-check only` -> `Run 2 = 若 EMA 仍 waiting_not_due，则只给 Rank 92 1 个 truly verdict-changing 的 Light Stability Pack（默认先做时间稳定性，并直接回答 promote_to_P2 / keep_P1 / park）` -> `Run 3 = 若 Rank 92 在时间稳定性后仍未 hard-fail，则再决定是否 promote_to_P2；若直接 hard-fail / park，则切 Rank 95 source intake`**。"
    if target not in text:
        raise SystemExit("TODO target block not found for Rank92 writeback")
    text = text.replace(target, target + "\n" + addition, 1)
    TODO_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    frames = {asset: build_frame(asset, symbol) for asset, symbol in ASSETS.items()}
    trades_all = []
    for asset, frame in frames.items():
        for setup in SETUPS:
            for variant in VARIANTS:
                sigs = build_signal_frame(frame, asset, setup, variant)
                trades_all.append(sigs)
    trades = pd.concat(trades_all, ignore_index=True) if trades_all else pd.DataFrame()
    trades.to_csv(ART_DIR / "trades.csv", index=False)

    summaries = []
    for cost in COSTS:
        s = summarize_variant(trades, cost)
        s.insert(0, "cost_bps_side", cost)
        summaries.append(s)
    summary = pd.concat(summaries, ignore_index=True) if summaries else pd.DataFrame()
    summary.to_csv(ART_DIR / "overall_summary.csv", index=False)

    summary6 = summary[summary["cost_bps_side"] == PRIMARY_COST].copy()
    compare = compare_against_baseline(summary6)
    compare.to_csv(ART_DIR / "setup_compare.csv", index=False)

    per_asset = build_per_asset_summary(trades, PRIMARY_COST)
    per_asset.to_csv(ART_DIR / "per_asset_summary.csv", index=False)

    overall = build_overall_summary(summary6, per_asset)
    overall.to_csv(ART_DIR / "desk_overall_summary.csv", index=False)

    buckets = build_time_bucket_summary(trades, PRIMARY_COST)
    buckets.to_csv(ART_DIR / "time_bucket_summary.csv", index=False)

    verdict, why = choose_verdict(overall)
    title = "Rank 92 / opening-drive adaptive offset continuation gate"
    html = render_html(title, compare, per_asset, overall, buckets, verdict, why)
    (SITE_DIR / "report.html").write_text(html, encoding="utf-8")
    READING_PATH.write_text(html, encoding="utf-8")

    meta = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "verdict": verdict,
        "why": why,
    }
    (ART_DIR / "summary.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    update_todo(verdict, overall, compare)
    print(json.dumps(meta, ensure_ascii=False))


if __name__ == "__main__":
    main()
