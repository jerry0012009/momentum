#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank94_two_bar_outside_followthrough_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank94_two_bar_outside_followthrough_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank94_two_bar_outside_followthrough_clean_replication.html"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
SETUPS = ["ema_psar_long", "fib_retest_long", "breakout_short"]
VARIANTS = ["baseline", "ft_gate", "sft_lite_gate", "baseline_half_ft_full"]
PRIMARY_VARIANT = "baseline_half_ft_full"
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0]
HOLD_BARS = 8
EARLY_FAIL_BARS = 4
FOLLOW_BARS = 2
AVG_RANGE_LOOKBACK = 10
EPS = 1e-12
CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1180px; margin: 32px auto; padding: 0 18px 48px; line-height: 1.68; color: #111827; background: #f8fafc; }
h1,h2,h3 { color:#111827; }
.card { border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }
.muted { color:#6b7280; }
code { background:#f3f4f6; padding:1px 5px; border-radius:6px; }
table { width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; background:white; }
th, td { border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }
a { color:#2563eb; text-decoration:none; }
"""


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def pct(v, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def num(v, digits: int = 2) -> str:
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


def write_html(path: Path, title: str, body: str) -> None:
    path.write_text(
        f"<!doctype html><html><head><meta charset='utf-8'><title>{escape(title)}</title><style>{CSS}</style></head><body>{body}</body></html>",
        encoding="utf-8",
    )


def load_bars(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
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


def build_followthrough_overlay(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["avg_range_10"] = (out["high"] - out["low"]).rolling(AVG_RANGE_LOOKBACK, min_periods=AVG_RANGE_LOOKBACK).mean()
    out["bar_range"] = (out["high"] - out["low"]).clip(lower=EPS)
    out["body_signed"] = out["close"] - out["open"]
    out["parent_high"] = out[["high"]].shift(1).join(out[["high"]].shift(2), rsuffix="_2").max(axis=1)
    out["parent_low"] = out[["low"]].shift(1).join(out[["low"]].shift(2), rsuffix="_2").min(axis=1)

    close_p1 = out["close"].shift(-1)
    close_p2 = out["close"].shift(-2)
    body_p1 = out["body_signed"].shift(-1)
    body_p2 = out["body_signed"].shift(-2)
    range_p1 = out["bar_range"].shift(-1)
    range_p2 = out["bar_range"].shift(-2)
    avg_range = out["avg_range_10"]

    out["ft_long"] = (
        out["parent_high"].notna()
        & (close_p1 > out["parent_high"])
        & (close_p2 > out["parent_high"])
    ).fillna(False)
    out["ft_short"] = (
        out["parent_low"].notna()
        & (close_p1 < out["parent_low"])
        & (close_p2 < out["parent_low"])
    ).fillna(False)

    out["sft_lite_long"] = (
        out["ft_long"]
        & (body_p1 > 0)
        & (body_p2 > 0)
        & (((range_p1 >= 1.5 * avg_range) | (range_p2 >= 1.5 * avg_range)).fillna(False))
    ).fillna(False)
    out["sft_lite_short"] = (
        out["ft_short"]
        & (body_p1 < 0)
        & (body_p2 < 0)
        & (((range_p1 >= 1.5 * avg_range) | (range_p2 >= 1.5 * avg_range)).fillna(False))
    ).fillna(False)
    return out


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_bars(symbol, asset)
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema21"] = df["close"].ewm(span=21, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["atr14"] = atr(df)
    df["vol_ma20"] = df["volume"].rolling(20, min_periods=20).mean()
    df["psar"] = compute_psar(df)
    df["swing_high_30"] = df["high"].rolling(30, min_periods=30).max().shift(1)
    df["swing_low_30"] = df["low"].rolling(30, min_periods=30).min().shift(1)
    rng = (df["swing_high_30"] - df["swing_low_30"]).clip(lower=EPS)
    df["fib_500"] = df["swing_low_30"] + 0.500 * rng
    df["fib_618"] = df["swing_low_30"] + 0.618 * rng
    df["donchian_low"] = df["low"].rolling(20, min_periods=20).min().shift(1)

    df["ema_psar_long_signal"] = (
        (df["ema9"] > df["ema21"])
        & (df["ema_slope"] > 0.0002)
        & (df["psar"] < df["close"])
        & (df["close"].shift(1) < df["ema9"].shift(1))
        & (df["close"] > df["ema9"])
        & (df["close"] > df["high"].shift(1) - 0.15 * df["atr14"])
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)

    df["fib_retest_long_signal"] = (
        df["fib_618"].notna()
        & (df["ema9"] > df["ema21"])
        & (df["ema_slope"] > 0)
        & (df["low"] <= df["fib_618"] + 0.15 * df["atr14"])
        & (df["close"] > df["fib_500"])
        & (df["close"].shift(1) <= df["fib_500"].shift(1))
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)

    df["breakout_short_signal"] = (
        df["donchian_low"].notna()
        & (df["ema9"] < df["ema21"])
        & (df["ema_slope"] < -0.0002)
        & (df["close"].shift(1) > df["donchian_low"].shift(1))
        & (df["close"] < df["donchian_low"] - 0.1 * df["atr14"])
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)

    return build_followthrough_overlay(df)


def variant_policy(row: pd.Series, setup: str, variant: str) -> tuple[bool, float, str]:
    is_long = setup.endswith("long")
    ft = bool(row["ft_long"] if is_long else row["ft_short"])
    sft = bool(row["sft_lite_long"] if is_long else row["sft_lite_short"])

    if variant == "baseline":
        return True, 1.0, "delayed_baseline"
    if variant == "ft_gate":
        return ft, 1.0, "ft_pass" if ft else "ft_fail"
    if variant == "sft_lite_gate":
        return sft, 1.0, "sft_lite_pass" if sft else "sft_lite_fail"
    return True, (1.0 if ft else 0.5), ("ft_fullsize" if ft else "baseline_halfsize")


def build_trades(frame: pd.DataFrame, asset: str, setup: str, variant: str) -> pd.DataFrame:
    signal_col = f"{setup}_signal"
    rows = []
    last_exit_idx = -1
    direction = -1.0 if setup.endswith("short") else 1.0

    ts = frame["timestamp"].to_numpy()
    opens = frame["open"].to_numpy(dtype=float)
    highs = frame["high"].to_numpy(dtype=float)
    lows = frame["low"].to_numpy(dtype=float)
    closes = frame["close"].to_numpy(dtype=float)
    signal_mask = frame[signal_col].to_numpy(dtype=bool)

    min_idx = max(60, AVG_RANGE_LOOKBACK + 3)
    max_idx = len(frame) - HOLD_BARS - FOLLOW_BARS - 2
    for idx in range(min_idx, max_idx):
        if idx <= last_exit_idx:
            continue
        if not bool(signal_mask[idx]):
            continue
        row = frame.iloc[idx]
        allow, size_mult, gate_reason = variant_policy(row, setup, variant)
        if not allow:
            continue
        entry_idx = idx + FOLLOW_BARS + 1
        exit_idx = entry_idx + HOLD_BARS - 1
        if exit_idx >= len(frame):
            continue
        entry_price = opens[entry_idx]
        exit_price = closes[exit_idx]
        gross_return = direction * (exit_price - entry_price) / max(entry_price, EPS)
        if direction > 0:
            early_fail = float(np.min(lows[entry_idx: min(exit_idx + 1, entry_idx + EARLY_FAIL_BARS)]) < entry_price)
            hold4 = float(closes[min(exit_idx, entry_idx + EARLY_FAIL_BARS - 1)] > entry_price)
        else:
            early_fail = float(np.max(highs[entry_idx: min(exit_idx + 1, entry_idx + EARLY_FAIL_BARS)]) > entry_price)
            hold4 = float(closes[min(exit_idx, entry_idx + EARLY_FAIL_BARS - 1)] < entry_price)
        rows.append(
            {
                "asset": asset,
                "setup": setup,
                "variant": variant,
                "signal_timestamp": ts[idx],
                "entry_timestamp": ts[entry_idx],
                "exit_timestamp": ts[exit_idx],
                "entry_price": entry_price,
                "exit_price": exit_price,
                "gross_return": gross_return,
                "position_size_mult": size_mult,
                "scaled_gross_return": gross_return * size_mult,
                "hold4": hold4,
                "early_fail_4bars": early_fail,
                "gate_reason": gate_reason,
                "ft_pass": bool(row["ft_long"] if setup.endswith("long") else row["ft_short"]),
                "sft_lite_pass": bool(row["sft_lite_long"] if setup.endswith("long") else row["sft_lite_short"]),
                "parent_high": row["parent_high"],
                "parent_low": row["parent_low"],
            }
        )
        last_exit_idx = exit_idx
    return pd.DataFrame(rows)


def summarize(trades: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    overall_rows = []
    setup_rows = []
    asset_rows = []
    time_rows = []

    for cost in COSTS:
        cost_df = trades.copy()
        cost_df["net_return"] = cost_df["scaled_gross_return"] - cost_df["position_size_mult"] * (2.0 * cost / 10000.0)
        base_counts_by_asset = cost_df[cost_df["variant"] == "baseline"].groupby("asset").size().to_dict()
        base_counts_by_setup = cost_df[cost_df["variant"] == "baseline"].groupby("setup").size().to_dict()
        for variant in VARIANTS:
            subset = cost_df[cost_df["variant"] == variant]
            grouped = subset.groupby("asset")["net_return"].sum() if not subset.empty else pd.Series(dtype=float)
            trade_ret_parts = []
            for asset in ASSETS:
                denom = max(base_counts_by_asset.get(asset, 0), 1)
                trade_ret_parts.append(subset[subset["asset"] == asset].shape[0] / denom)
            overall_rows.append(
                {
                    "variant": variant,
                    "cost_bps": cost,
                    "mean_total_return": grouped.mean() if not grouped.empty else np.nan,
                    "positive_asset_ratio": (grouped > 0).mean() if not grouped.empty else np.nan,
                    "mean_trades": subset.groupby("asset").size().mean() if not subset.empty else 0.0,
                    "trade_count_retention": float(np.mean(trade_ret_parts)) if trade_ret_parts else np.nan,
                    "mean_position_size_mult": subset.groupby("asset")["position_size_mult"].mean().mean() if not subset.empty else np.nan,
                    "mean_hold4": subset["hold4"].mean() if not subset.empty else np.nan,
                    "mean_early_fail_4bars": subset["early_fail_4bars"].mean() if not subset.empty else np.nan,
                    "ft_pass_rate": subset["ft_pass"].mean() if not subset.empty else np.nan,
                    "sft_lite_pass_rate": subset["sft_lite_pass"].mean() if not subset.empty else np.nan,
                }
            )
        if cost != PRIMARY_COST:
            continue
        primary = cost_df[cost_df["variant"] == PRIMARY_VARIANT].copy()
        if primary.empty:
            continue
        for setup, setup_df in primary.groupby("setup"):
            base_setup_n = max(base_counts_by_setup.get(setup, 0), 1)
            setup_rows.append(
                {
                    "setup": setup,
                    "trades": len(setup_df),
                    "baseline_trades": base_counts_by_setup.get(setup, 0),
                    "trade_count_retention": len(setup_df) / base_setup_n,
                    "mean_return": setup_df["net_return"].mean(),
                    "total_return": setup_df["net_return"].sum(),
                    "positive_asset_ratio": (setup_df.groupby("asset")["net_return"].sum() > 0).mean(),
                    "mean_position_size_mult": setup_df["position_size_mult"].mean(),
                    "hold4": setup_df["hold4"].mean(),
                    "early_fail_4bars": setup_df["early_fail_4bars"].mean(),
                    "ft_pass_rate": setup_df["ft_pass"].mean(),
                    "sft_lite_pass_rate": setup_df["sft_lite_pass"].mean(),
                }
            )
        for asset, asset_df in primary.groupby("asset"):
            asset_rows.append(
                {
                    "asset": asset,
                    "trades": len(asset_df),
                    "total_return": asset_df["net_return"].sum(),
                    "mean_return": asset_df["net_return"].mean(),
                    "mean_position_size_mult": asset_df["position_size_mult"].mean(),
                    "hold4": asset_df["hold4"].mean(),
                    "early_fail_4bars": asset_df["early_fail_4bars"].mean(),
                    "ft_pass_rate": asset_df["ft_pass"].mean(),
                    "sft_lite_pass_rate": asset_df["sft_lite_pass"].mean(),
                }
            )
        ordered = primary.sort_values("entry_timestamp").reset_index(drop=True)
        if not ordered.empty:
            ordered["bucket"] = pd.qcut(np.arange(len(ordered)), q=3, labels=["bucket_1", "bucket_2", "bucket_3"], duplicates="drop")
            for bucket, bucket_df in ordered.groupby("bucket"):
                bucket_grouped = bucket_df.groupby("asset")["net_return"].sum()
                time_rows.append(
                    {
                        "bucket": bucket,
                        "mean_total_return": bucket_grouped.mean(),
                        "positive_asset_ratio": (bucket_grouped > 0).mean(),
                        "trades": len(bucket_df),
                        "mean_position_size_mult": bucket_df["position_size_mult"].mean(),
                        "mean_hold4": bucket_df["hold4"].mean(),
                        "mean_early_fail_4bars": bucket_df["early_fail_4bars"].mean(),
                        "ft_pass_rate": bucket_df["ft_pass"].mean(),
                        "sft_lite_pass_rate": bucket_df["sft_lite_pass"].mean(),
                    }
                )

    return (
        pd.DataFrame(overall_rows),
        pd.DataFrame(setup_rows),
        pd.DataFrame(asset_rows),
        pd.DataFrame(time_rows),
    )


def decide_verdict(overall: pd.DataFrame, setup_summary: pd.DataFrame) -> tuple[str, str]:
    baseline = overall[(overall["variant"] == "baseline") & (overall["cost_bps"] == PRIMARY_COST)].iloc[0]
    primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps"] == PRIMARY_COST)].iloc[0]
    sft = overall[(overall["variant"] == "sft_lite_gate") & (overall["cost_bps"] == PRIMARY_COST)].iloc[0]
    p_ret = float(primary["mean_total_return"])
    b_ret = float(baseline["mean_total_return"])
    p_pos = float(primary["positive_asset_ratio"])
    p_retention = float(primary["trade_count_retention"])
    p_fail = float(primary["mean_early_fail_4bars"])
    b_fail = float(baseline["mean_early_fail_4bars"])
    best_setup = float(setup_summary["total_return"].max()) if not setup_summary.empty else -999.0
    sft_ret = float(sft["mean_total_return"])

    if p_ret > 0 and p_pos >= 2 / 3 and p_retention >= 0.45 and p_fail <= b_fail * 0.92:
        return (
            "promote_to_P2 / paper candidate",
            "FT-based delayed entry 在成本后转正、跨资产一致性过线，且 retention 仍够厚，不只是缩样本少亏。",
        )
    if (p_ret > b_ret + 0.01 and p_retention >= 0.50 and (p_fail <= b_fail or best_setup > 0)) or (sft_ret > b_ret + 0.02 and best_setup > 0):
        return (
            "keep_P1 / mixed but honest",
            "follow-through gate 对 baseline 有诚实增量，但更像 shared path-persistence overlay；跨资产一致性与 setup 结构还不够硬到升 P2。",
        )
    return (
        "park / evidence_pool",
        "延后两根后的 FT / SFT-lite 结果仍不足以改变 desk judgment，改善主要来自缩样本或局部 pocket。",
    )


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    frames = {asset: build_frame(asset, symbol) for asset, symbol in ASSETS.items()}
    trade_frames = []
    for asset, frame in frames.items():
        for setup in SETUPS:
            for variant in VARIANTS:
                trades = build_trades(frame, asset, setup, variant)
                if not trades.empty:
                    trade_frames.append(trades)
    trades = pd.concat(trade_frames, ignore_index=True) if trade_frames else pd.DataFrame()

    overall, setup_summary, asset_summary, time_summary = summarize(trades)
    verdict, verdict_reason = decide_verdict(overall, setup_summary)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    overall = overall.sort_values(["cost_bps", "variant"]).reset_index(drop=True)
    setup_summary = setup_summary.sort_values(["setup"]).reset_index(drop=True)
    asset_summary = asset_summary.sort_values(["asset"]).reset_index(drop=True)
    time_summary = time_summary.sort_values(["bucket"]).reset_index(drop=True)

    cost_df = trades.copy()
    cost_df["net_return_6bps"] = cost_df["scaled_gross_return"] - cost_df["position_size_mult"] * (2.0 * PRIMARY_COST / 10000.0)

    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    setup_summary.to_csv(ART_DIR / "setup_summary.csv", index=False)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    time_summary.to_csv(ART_DIR / "time_bucket_summary.csv", index=False)
    cost_df[cost_df["variant"] == PRIMARY_VARIANT].to_csv(ART_DIR / "trades_primary_6bps.csv", index=False)
    pd.DataFrame([
        {
            "generated_at_utc": generated_at,
            "execution": "signal bar and earlier only + wait 2 follow-through bars + next eligible open + no-overlap + hold 8 bars",
            "follow_bars": FOLLOW_BARS,
            "avg_range_lookback": AVG_RANGE_LOOKBACK,
            "variants": "baseline / ft_gate / sft_lite_gate / baseline_half_ft_full",
            "primary_variant": PRIMARY_VARIANT,
            "verdict": verdict,
            "verdict_reason": verdict_reason,
        }
    ]).to_csv(ART_DIR / "meta.csv", index=False)

    baseline = overall[(overall["variant"] == "baseline") & (overall["cost_bps"] == PRIMARY_COST)].iloc[0]
    ft = overall[(overall["variant"] == "ft_gate") & (overall["cost_bps"] == PRIMARY_COST)].iloc[0]
    sft = overall[(overall["variant"] == "sft_lite_gate") & (overall["cost_bps"] == PRIMARY_COST)].iloc[0]
    hybrid = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps"] == PRIMARY_COST)].iloc[0]

    body = f"""
<h1>Rank 94 / two-bar outside-range follow-through clean replication</h1>
<p class='muted'>生成时间：{escape(generated_at)} | 口径：固定 BTC/ETH/SOL 120d 15m 本地 cache，统一 <code>signal 当根及之前数据 + follow-through 等待窗口 + next eligible open + no-overlap + hold 8 bars</code>。</p>
<div class='card'>
  <h2>Hard verdict</h2>
  <p><strong>{escape(verdict)}</strong></p>
  <p>{escape(verdict_reason)}</p>
  <ul>
    <li>baseline @ 6bps：收益 {escape(pct(baseline['mean_total_return']))}，资产为正占比 {escape(pct(baseline['positive_asset_ratio']))}，retention {escape(pct(baseline['trade_count_retention']))}，平均仓位 {escape(pct(baseline['mean_position_size_mult']))}</li>
    <li>ft_gate @ 6bps：收益 {escape(pct(ft['mean_total_return']))}，资产为正占比 {escape(pct(ft['positive_asset_ratio']))}，retention {escape(pct(ft['trade_count_retention']))}</li>
    <li>sft_lite_gate @ 6bps：收益 {escape(pct(sft['mean_total_return']))}，资产为正占比 {escape(pct(sft['positive_asset_ratio']))}，retention {escape(pct(sft['trade_count_retention']))}</li>
    <li>{escape(PRIMARY_VARIANT)} @ 6bps：收益 {escape(pct(hybrid['mean_total_return']))}，资产为正占比 {escape(pct(hybrid['positive_asset_ratio']))}，retention {escape(pct(hybrid['trade_count_retention']))}，平均仓位 {escape(pct(hybrid['mean_position_size_mult']))}</li>
  </ul>
</div>
<div class='card'>
  <h2>这次最小 clean replication 怎么做</h2>
  <ul>
    <li>setup 固定为 <code>ema_psar_long</code> / <code>fib_retest_long</code> / <code>breakout_short</code>。</li>
    <li><code>parent_range</code> 固定为 signal 前两根 bar 的 high / low。</li>
    <li><code>FT</code>：signal 后连续两根 close 都仍站在 parent range 外；<code>SFT-lite</code>：在 FT 基础上，再要求两根同向实体推进，且至少一根 <code>range &gt;= 1.5 * avg_range_10</code>。</li>
    <li>所有变体统一等待两根 follow-through bar 完成后，才在下一根 open 入场；不偷看更远路径，也不把 repo 的其他 kill-zone / ML 叙事一并搬进来。</li>
    <li><code>baseline_half_ft_full</code>：FT 通过给 <code>1.0x</code>，否则只保留 <code>0.5x</code>，用于测试“不是全删单，而是 path-persistence size-up”是否更诚实。</li>
  </ul>
</div>
<div class='card'>
  <h2>Overall summary</h2>
  {render_table(overall, percent_cols={'mean_total_return','positive_asset_ratio','trade_count_retention','mean_position_size_mult','mean_hold4','mean_early_fail_4bars','ft_pass_rate','sft_lite_pass_rate'})}
</div>
<div class='card'>
  <h2>Setup summary ({PRIMARY_VARIANT} @ 6bps)</h2>
  {render_table(setup_summary, percent_cols={'trade_count_retention','mean_return','total_return','positive_asset_ratio','mean_position_size_mult','hold4','early_fail_4bars','ft_pass_rate','sft_lite_pass_rate'})}
</div>
<div class='card'>
  <h2>Asset summary ({PRIMARY_VARIANT} @ 6bps)</h2>
  {render_table(asset_summary, percent_cols={'total_return','mean_return','mean_position_size_mult','hold4','early_fail_4bars','ft_pass_rate','sft_lite_pass_rate'})}
</div>
<div class='card'>
  <h2>Time pocket summary ({PRIMARY_VARIANT} @ 6bps)</h2>
  {render_table(time_summary, percent_cols={'mean_total_return','positive_asset_ratio','mean_position_size_mult','mean_hold4','mean_early_fail_4bars','ft_pass_rate','sft_lite_pass_rate'})}
</div>
<div class='card'>
  <h2>Artifacts</h2>
  <ul>
    <li><code>reports/artifacts/scout_rank94_two_bar_outside_followthrough_15m/overall_summary.csv</code></li>
    <li><code>reports/artifacts/scout_rank94_two_bar_outside_followthrough_15m/setup_summary.csv</code></li>
    <li><code>reports/artifacts/scout_rank94_two_bar_outside_followthrough_15m/asset_summary.csv</code></li>
    <li><code>reports/artifacts/scout_rank94_two_bar_outside_followthrough_15m/time_bucket_summary.csv</code></li>
    <li><code>reports/artifacts/scout_rank94_two_bar_outside_followthrough_15m/trades_primary_6bps.csv</code></li>
  </ul>
</div>
"""
    write_html(SITE_DIR / "report.html", "Rank 94 two-bar outside-range follow-through clean replication", body)

    reading_body = f"""
<h1>Rank 94 / two-bar outside-range follow-through clean replication</h1>
<p class='muted'>这轮只回答一件事：Rank 94 在 desk 共用 setup 上，是该升、留，还是直接 park。</p>
<div class='card'>
  <p><strong>结论：</strong>{escape(verdict)}</p>
  <p>{escape(verdict_reason)}</p>
  <p>primary 口径固定为 <code>{PRIMARY_VARIANT}</code> @ <code>{int(PRIMARY_COST)}bps/side</code>：mean_total_return={escape(pct(hybrid['mean_total_return']))}，positive_asset_ratio={escape(pct(hybrid['positive_asset_ratio']))}，trade_count_retention={escape(pct(hybrid['trade_count_retention']))}，mean_position_size={escape(pct(hybrid['mean_position_size_mult']))}。</p>
  <p>对照 delayed baseline：mean_total_return={escape(pct(baseline['mean_total_return']))}，positive_asset_ratio={escape(pct(baseline['positive_asset_ratio']))}，trade_count_retention={escape(pct(baseline['trade_count_retention']))}。</p>
  <p><a href='../../factors/scout_rank94_two_bar_outside_followthrough_15m/report.html'>查看完整报告页</a></p>
</div>
"""
    write_html(READING_PATH, "Rank 94 two-bar outside-range follow-through clean replication", reading_body)

    print(f"hard_verdict={verdict}")
    print(f"baseline_mean_total_return={baseline['mean_total_return']:.6f}")
    print(f"primary_mean_total_return={hybrid['mean_total_return']:.6f}")
    print(f"primary_positive_asset_ratio={hybrid['positive_asset_ratio']:.6f}")
    print(f"primary_trade_count_retention={hybrid['trade_count_retention']:.6f}")
    print(f"primary_mean_position_size_mult={hybrid['mean_position_size_mult']:.6f}")


if __name__ == "__main__":
    main()
