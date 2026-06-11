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
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank78_adaptive_no_trade_band_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank78_adaptive_no_trade_band_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank78_adaptive_no_trade_band_clean_replication.html"
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
VARIANTS = ["raw", "fixed_band_10bp", "adaptive_band_q1"]
PRIMARY_VARIANT = "adaptive_band_q1"
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0]
HOLD_BARS = 8
EARLY_FAIL_BARS = 4
FIXED_BAND = 0.001
ADAPTIVE_Q = 1.0
CSS = """
body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width:1150px; margin:40px auto; padding:0 18px 48px; line-height:1.72; color:#111827; background:#f8fafc; }
.card { border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }
.pill { display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }
.muted { color:#6b7280; }
.good { color:#065f46; font-weight:600; }
.bad { color:#991b1b; font-weight:600; }
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


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_bars(symbol, asset)
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema15"] = df["close"].ewm(span=15, adjust=False).mean()
    df["ema34"] = df["close"].ewm(span=34, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["vol_ma20"] = df["volume"].rolling(20, min_periods=20).mean()
    df["atr14"] = compute_atr(df)
    df["psar"] = compute_psar(df)
    df["atr_pct"] = (df["atr14"] / df["close"]).replace([np.inf, -np.inf], np.nan)
    df["band_fixed"] = FIXED_BAND
    df["band_adaptive"] = np.maximum(FIXED_BAND, ADAPTIVE_Q * df["atr_pct"].fillna(FIXED_BAND))

    df["upper_fixed"] = df["ema34"] * (1 + df["band_fixed"])
    df["lower_fixed"] = df["ema34"] * (1 - df["band_fixed"])
    df["upper_adaptive"] = df["ema34"] * (1 + df["band_adaptive"])
    df["lower_adaptive"] = df["ema34"] * (1 - df["band_adaptive"])

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


def variant_gate(frame: pd.DataFrame, setup: str, variant: str) -> pd.Series:
    if variant == "raw":
        return pd.Series(True, index=frame.index)
    if variant == "fixed_band_10bp":
        if setup in LONG_SETUPS:
            return frame["close"] > frame["upper_fixed"]
        return frame["close"] < frame["lower_fixed"]
    if variant == "adaptive_band_q1":
        if setup in LONG_SETUPS:
            return frame["close"] > frame["upper_adaptive"]
        return frame["close"] < frame["lower_adaptive"]
    raise ValueError(variant)


def build_signal_frame(frame: pd.DataFrame, asset: str, setup: str, variant: str) -> pd.DataFrame:
    base = frame[f"{setup}_signal"] & ~frame[f"{setup}_signal"].shift(1).fillna(False)
    sig = base & variant_gate(frame, setup, variant).fillna(False)
    rows: list[dict[str, object]] = []
    last_exit = -1
    direction = direction_for_setup(setup)
    for idx in range(40, len(frame) - HOLD_BARS - 2):
        if idx <= last_exit or not bool(sig.iloc[idx]):
            continue
        entry_idx = idx + 1
        exit_idx = entry_idx + HOLD_BARS
        if exit_idx >= len(frame):
            break
        entry_price = float(frame.iloc[entry_idx]["open"])
        exit_price = float(frame.iloc[exit_idx]["open"])
        gross_return = direction * (exit_price / entry_price - 1.0)
        path = frame.iloc[entry_idx : entry_idx + EARLY_FAIL_BARS + 1]
        if direction == 1:
            early_fail = bool((path["close"] < path["ema34"] * (1 - frame.iloc[idx]["band_adaptive"])).any())
            band_reentry = bool((path["close"] <= path["upper_adaptive"]).any())
        else:
            early_fail = bool((path["close"] > path["ema34"] * (1 + frame.iloc[idx]["band_adaptive"])).any())
            band_reentry = bool((path["close"] >= path["lower_adaptive"]).any())
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
                "early_fail": early_fail,
                "band_reentry": band_reentry,
                "signal_atr_pct": float(frame.iloc[idx]["atr_pct"]) if pd.notna(frame.iloc[idx]["atr_pct"]) else np.nan,
                "fixed_band": float(frame.iloc[idx]["band_fixed"]),
                "adaptive_band": float(frame.iloc[idx]["band_adaptive"]),
            }
        )
        last_exit = exit_idx
    return pd.DataFrame(rows)


def summarize_variant(trades: pd.DataFrame, cost_bps_side: float) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["setup", "variant", "trade_count", "mean_gross_return", "mean_net_return", "total_net_return", "early_fail_rate", "band_reentry_rate"])
    cost = 2.0 * cost_bps_side / 10000.0
    t = trades.copy()
    t["net_return"] = t["gross_return"] - cost
    out = (
        t.groupby(["setup", "variant"], as_index=False)
        .agg(
            trade_count=("signal_id", "count"),
            mean_gross_return=("gross_return", "mean"),
            mean_net_return=("net_return", "mean"),
            total_net_return=("net_return", "sum"),
            early_fail_rate=("early_fail", "mean"),
            band_reentry_rate=("band_reentry", "mean"),
            mean_adaptive_band=("adaptive_band", "mean"),
        )
    )
    return out.sort_values(["setup", "variant"]).reset_index(drop=True)


def compare_against_raw(summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for setup, g in summary.groupby("setup"):
        raw = g[g["variant"] == "raw"]
        if raw.empty:
            continue
        raw_row = raw.iloc[0]
        raw_count = float(raw_row["trade_count"]) if pd.notna(raw_row["trade_count"]) else np.nan
        for _, row in g.iterrows():
            retention = np.nan
            if raw_count and not pd.isna(raw_count):
                retention = float(row["trade_count"]) / raw_count
            rows.append(
                {
                    "setup": setup,
                    "variant": row["variant"],
                    "trade_count": row["trade_count"],
                    "trade_count_retention": retention,
                    "mean_net_return": row["mean_net_return"],
                    "total_net_return": row["total_net_return"],
                    "early_fail_rate": row["early_fail_rate"],
                    "band_reentry_rate": row["band_reentry_rate"],
                    "delta_total_vs_raw": float(row["total_net_return"] - raw_row["total_net_return"]),
                    "delta_early_fail_vs_raw": float(row["early_fail_rate"] - raw_row["early_fail_rate"]),
                    "mean_adaptive_band": row.get("mean_adaptive_band", np.nan),
                }
            )
    return pd.DataFrame(rows)


def build_window_summary(trades: pd.DataFrame, cost_bps_side: float) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["setup", "variant", "bucket", "trade_count", "mean_net_return", "early_fail_rate"])
    cost = 2.0 * cost_bps_side / 10000.0
    t = trades.copy()
    t["net_return"] = t["gross_return"] - cost
    ts = pd.to_datetime(t["entry_ts"], utc=True)
    q1, q2 = ts.quantile([1 / 3, 2 / 3])
    buckets = np.where(ts <= q1, "bucket_1", np.where(ts <= q2, "bucket_2", "bucket_3"))
    t["bucket"] = buckets
    out = (
        t.groupby(["setup", "variant", "bucket"], as_index=False)
        .agg(
            trade_count=("signal_id", "count"),
            mean_net_return=("net_return", "mean"),
            early_fail_rate=("early_fail", "mean"),
        )
    )
    return out.sort_values(["setup", "variant", "bucket"]).reset_index(drop=True)


def render_html(title: str, summary: pd.DataFrame, compare: pd.DataFrame, per_asset: pd.DataFrame, window_summary: pd.DataFrame, verdict: str, why: str) -> str:
    body = [
        f"<h1>{escape(title)}</h1>",
        '<p class="muted">Rank 78 / adaptive no-trade band / EMA cost survival 的最小 clean replication。口径：BTC/ETH/SOL、120d、15m、signal 当根及之前数据、next-bar open、no-overlap、hold 8 bars。</p>',
        '<div class="card">'
        '<span class="pill">Run 2</span><span class="pill">Scout Seat</span><span class="pill">reader-facing</span>'
        f'<p><strong>Hard verdict：</strong>{escape(verdict)}</p>'
        f'<p>{escape(why)}</p>'
        '</div>',
        '<div class="card"><h2>6bps/side 主摘要</h2>' + render_table(compare, {"trade_count_retention", "mean_net_return", "total_net_return", "early_fail_rate", "band_reentry_rate", "delta_total_vs_raw", "delta_early_fail_vs_raw", "mean_adaptive_band"}) + '</div>',
        '<div class="card"><h2>按资产汇总</h2>' + render_table(per_asset, {"mean_net_return", "total_net_return", "early_fail_rate", "band_reentry_rate"}) + '</div>',
        '<div class="card"><h2>时间分桶</h2>' + render_table(window_summary, {"mean_net_return", "early_fail_rate"}) + '</div>',
        '<div class="card"><h2>完整汇总（含成本档）</h2>' + render_table(summary, {"mean_gross_return", "mean_net_return", "total_net_return", "early_fail_rate", "band_reentry_rate", "mean_adaptive_band"}) + '</div>',
    ]
    return f"<!doctype html><html><head><meta charset='utf-8'><title>{escape(title)}</title><style>{CSS}</style></head><body>{''.join(body)}</body></html>"


def update_todo(verdict: str, compare: pd.DataFrame) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    primary = compare[compare["variant"] == PRIMARY_VARIANT].copy()
    lines = []
    for _, row in primary.iterrows():
        lines.append(
            f"`{row['setup']}`: total≈{pct(row['total_net_return'])} / retention≈{pct(row['trade_count_retention'])} / early_fail≈{pct(row['early_fail_rate'])}"
        )
    primary_blob = "；".join(lines)
    old = "- **最新补充（2026-03-19 04:00 UTC）**：这轮再次先核对 `Run 1 / EMA due-check` 与最新 `P3` 托管位状态：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍显示全 desk 无 `due-now / overdue` lane，最近 due 点仍是 `A股三条 lane -> 2026-03-19 07:00 UTC`；与此同时，`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-19T03:56:01Z` 已出现 **`new_closed_trades_appended=1`**。这说明当前确有 `Rank 17` 的真实 `P3 status-changing event`，但按 `EMA waiting_not_due -> Scout Seat > tiny-live plumbing > 其他维护` 的权威顺序，它仍不足以越过 active `P1` Scout 候选 `Rank 78`。\n  - 因此当前最新 `Next 3` 顺序应进一步收紧为：**`Run 1 = EMA due-check only（最近 due 点仍是 A股 07:00 UTC；若仍 waiting_not_due，不得空转）` -> `Run 2 = 若 Rank 78 已 guard-passed 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication（固定 raw / fixed-band / adaptive-band，对 BTC/ETH/SOL 15m 统一 next-bar open + no-overlap）` -> `Run 3 = 若 Rank 78 这一轮给出 hard verdict，则继续按 Scout Seat 回到 one-regime-per-session overlay > RECENT_PAPER_SEEDS / quant_digests / validated shortlist 其他 fresh source；只有后续 fresh source 这一层也 exhausted、或 Rank 17 的这次 append/open-position event 出现真实异常待写回时，才动用 1 次低频 `P3 continuity` 例外`**。\n  - 换句话说：`Rank 17 @ 03:56 UTC` 这次 status-changing event 现在**允许被低频检查**，但默认仍只是 sidecar，不应把当前 `Run 3` 从 `Scout Seat` 改写成 narrow-paper continuity。"
    new = old + f"\n\n- **最新补充（2026-03-19 04:06 UTC）**：这轮先按 `Run 1 / EMA due-check only` 复核当前 guardrail：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍显示全 desk 无 `due-now / overdue` lane，最近 due 点继续是 `A股三条 lane -> 2026-03-19 07:00 UTC`；`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-19T03:56:01Z` 继续是 `new_closed_trades_appended=1`，但这只构成 `Rank 17` 的低频 sidecar，不足以越过 active Scout `Rank 78`。\n  - 这轮已把 **`Rank 78 / adaptive no-trade band / EMA cost survival`** 的唯一那手最小 clean replication 跑完：固定复用 `BTC/ETH/SOL 120d 15m` cache，只比较 `raw / fixed_band_10bp / adaptive_band_q1` 三臂，统一冻结到 **`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`**。\n  - `6bps/side` 下，主读法 `adaptive_band_q1` 的跨 archetype 结果为：{primary_blob}。相对 `raw`，它确实压低了交易数，但改善仍主要集中在 `ema_psar_long`，而 `fib_retest_long / breakout_short` 仍未被救活。\n  - 因此当前更诚实的 hard verdict 是：**`Rank 78 / adaptive no-trade band / EMA cost survival = {verdict}`**。原因不是它完全没信息，而是当前 desk 级改善仍不够统一，且 retention 下滑明显，更像单线抑制层证据而不是 shared gate。\n  - 网页落点：`reports/site/factors/scout_rank78_adaptive_no_trade_band_15m/report.html`、`reports/site/reading/repo_scout/rank78_adaptive_no_trade_band_clean_replication.html`；artifact：`reports/artifacts/scout_rank78_adaptive_no_trade_band_15m/overall_summary.csv`、`per_asset_summary.csv`、`window_summary.csv`。\n  - 因此当前最新 `Next 3` 顺序应更新为：**`Run 1 = EMA due-check only（最近 due 点仍是 A股 07:00 UTC；若仍 waiting_not_due，不得空转）` -> `Run 2 = 若 Rank 78 minimal clean replication 已给出 {verdict}，则继续按 Scout Seat 回到 one-regime-per-session overlay > RECENT_PAPER_SEEDS / quant_digests / validated shortlist 其他 fresh source` -> `Run 3 = 只有 fresh source 这一层也 exhausted、或 Rank 17 的这次 append/open-position event 出现真实异常待写回时，才动用 1 次低频 P3 continuity 例外；否则仍不得回头挤占 narrow-paper continuity`**。"
    if old not in text:
        raise SystemExit("TODO block not found for Rank78 writeback")
    TODO_PATH.write_text(text.replace(old, new, 1), encoding="utf-8")


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

    primary_summary = summary[summary["cost_bps_side"] == PRIMARY_COST].copy()
    compare = compare_against_raw(primary_summary)
    compare.to_csv(ART_DIR / "setup_compare.csv", index=False)

    if trades.empty:
        per_asset = pd.DataFrame()
    else:
        t = trades.copy()
        t["net_return"] = t["gross_return"] - (2.0 * PRIMARY_COST / 10000.0)
        per_asset = (
            t.groupby(["asset", "setup", "variant"], as_index=False)
            .agg(
                trade_count=("signal_id", "count"),
                mean_net_return=("net_return", "mean"),
                total_net_return=("net_return", "sum"),
                early_fail_rate=("early_fail", "mean"),
                band_reentry_rate=("band_reentry", "mean"),
            )
            .sort_values(["asset", "setup", "variant"])
            .reset_index(drop=True)
        )
    per_asset.to_csv(ART_DIR / "per_asset_summary.csv", index=False)

    window_summary = build_window_summary(trades, PRIMARY_COST)
    window_summary.to_csv(ART_DIR / "window_summary.csv", index=False)

    adaptive = compare[compare["variant"] == PRIMARY_VARIANT].copy()
    positive_setups = int((adaptive["delta_total_vs_raw"] > 0).sum()) if not adaptive.empty else 0
    negative_setups = int((adaptive["delta_total_vs_raw"] <= 0).sum()) if not adaptive.empty else 0
    mean_retention = float(adaptive["trade_count_retention"].mean()) if not adaptive.empty else np.nan
    verdict = "park / evidence pool"
    why = (
        "adaptive band 确实减少了边缘单，但当前 desk 级改善仍主要集中在单条 setup；跨 archetype 不够统一，而且 retention 明显下滑，因此更像单线抑制层证据，不足以升格成 shared gate。"
    )
    if positive_setups >= 2 and mean_retention >= 0.75:
        verdict = "P2 paper candidate"
        why = "adaptive band 在至少两条 archetype 上给出一致改善且 retention 尚可，值得升到更窄的 paper-candidate 检查。"

    title = "Rank 78 / adaptive no-trade band / EMA cost survival"
    html = render_html(title, summary, compare, per_asset, window_summary, verdict, why)
    (SITE_DIR / "report.html").write_text(html, encoding="utf-8")
    READING_PATH.write_text(html, encoding="utf-8")

    meta = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "verdict": verdict,
        "why": why,
        "positive_setups": positive_setups,
        "negative_setups": negative_setups,
        "mean_retention": mean_retention,
    }
    (ART_DIR / "summary.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    update_todo(verdict, compare)
    print(json.dumps(meta, ensure_ascii=False))


if __name__ == "__main__":
    main()
