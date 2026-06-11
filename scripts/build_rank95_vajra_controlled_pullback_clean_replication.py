#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank95_vajra_controlled_pullback_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank95_vajra_controlled_pullback_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank95_vajra_controlled_pullback_clean_replication.html"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
VARIANTS = [
    "baseline",
    "post_trigger_depth_1p0",
    "prearmed_depth_0p75",
    "prearmed_depth_1p0",
    "prearmed_depth_1p25",
    "prearmed_depth_1p0_plus_filters",
]
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0]
HOLD_BARS = 8
EARLY_FAIL_BARS = 4
LOOKBACK = 5
EPS = 1e-12
PRIMARY_VARIANT = "prearmed_depth_1p0"
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


def compute_adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high = df["high"]
    low = df["low"]
    close = df["close"]
    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            (high - low).abs(),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    atr_rma = tr.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    plus_di = 100 * pd.Series(plus_dm, index=df.index).ewm(alpha=1 / period, adjust=False, min_periods=period).mean() / atr_rma
    minus_di = 100 * pd.Series(minus_dm, index=df.index).ewm(alpha=1 / period, adjust=False, min_periods=period).mean() / atr_rma
    dx = ((plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)) * 100
    return dx.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_bars(symbol, asset)
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema15"] = df["close"].ewm(span=15, adjust=False).mean()
    df["ema21"] = df["close"].ewm(span=21, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["vol_ma20"] = df["volume"].rolling(20, min_periods=20).mean()
    df["atr14"] = atr(df)
    df["adx14"] = compute_adx(df)
    df["psar"] = compute_psar(df)

    df["hh5"] = df["high"].rolling(LOOKBACK, min_periods=LOOKBACK).max()
    df["ll5"] = df["low"].rolling(LOOKBACK, min_periods=LOOKBACK).min()
    df["post_trigger_depth_pct"] = ((df["hh5"] - df["close"]) / df["hh5"].clip(lower=EPS)) * 100.0
    df["post_trigger_near_ema"] = (df["low"] <= df["ema9"]) | (df["low"] <= df["ema15"]) | (df["low"] <= df["ema21"])
    df["green_candle"] = df["close"] > df["open"]
    df["vol_spike_12"] = df["volume"] > 1.2 * df["vol_ma20"]

    prev_high5 = df["high"].rolling(LOOKBACK, min_periods=LOOKBACK).max().shift(1)
    prev_low5 = df["low"].rolling(LOOKBACK, min_periods=LOOKBACK).min().shift(1)
    df["prearmed_depth_pct"] = ((prev_high5 - prev_low5) / prev_high5.clip(lower=EPS)) * 100.0
    recent_touch = ((df["low"] <= df["ema21"] * 1.0015) | (df["low"] <= df["ema9"] * 1.0015)).rolling(LOOKBACK, min_periods=1).max().shift(1).fillna(0).astype(bool)
    recent_green = (df["close"] > df["open"]).rolling(LOOKBACK, min_periods=1).max().shift(1).fillna(0).astype(bool)
    recent_vol_spike = (df["volume"] > 1.2 * df["vol_ma20"]).rolling(LOOKBACK, min_periods=1).max().shift(1).fillna(0).astype(bool)
    recent_adx = df["adx14"].rolling(LOOKBACK, min_periods=1).max().shift(1)
    df["prearmed_recent_touch"] = recent_touch
    df["prearmed_recent_green"] = recent_green
    df["prearmed_recent_vol_spike"] = recent_vol_spike
    df["prearmed_recent_adx_max"] = recent_adx

    df["ema_psar_long_signal"] = (
        (df["ema9"] > df["ema15"])
        & (df["ema_slope"] > 0.0003)
        & (df["psar"] < df["close"])
        & (df["close"] > df["high"].shift(1))
        & (df["close"].shift(1) < df["ema9"].shift(1))
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)
    return df


def variant_policy(row: pd.Series, variant: str) -> tuple[bool, str]:
    if variant == "baseline":
        return True, "baseline"
    if variant == "post_trigger_depth_1p0":
        allow = bool(row["post_trigger_depth_pct"] <= 1.0)
        return allow, "post_trigger_depth<=1.0" if allow else "post_trigger_depth>1.0"
    if variant == "prearmed_depth_0p75":
        allow = bool(row["prearmed_recent_touch"] and row["prearmed_depth_pct"] <= 0.75)
        return allow, "prearmed_touch+depth<=0.75" if allow else "no_prearmed_0.75"
    if variant == "prearmed_depth_1p0":
        allow = bool(row["prearmed_recent_touch"] and row["prearmed_depth_pct"] <= 1.0)
        return allow, "prearmed_touch+depth<=1.0" if allow else "no_prearmed_1.0"
    if variant == "prearmed_depth_1p25":
        allow = bool(row["prearmed_recent_touch"] and row["prearmed_depth_pct"] <= 1.25)
        return allow, "prearmed_touch+depth<=1.25" if allow else "no_prearmed_1.25"
    allow = bool(
        row["prearmed_recent_touch"]
        and row["prearmed_depth_pct"] <= 1.0
        and row["prearmed_recent_green"]
        and row["prearmed_recent_vol_spike"]
        and row["prearmed_recent_adx_max"] >= 25.0
    )
    return allow, "prearmed_1.0+filters" if allow else "no_prearmed_filters"


def build_candidates(frame: pd.DataFrame, asset: str, variant: str) -> tuple[pd.DataFrame, int]:
    rows = []
    signal_count = 0
    last_exit_idx = -1
    opens = frame["open"].to_numpy(dtype=float)
    highs = frame["high"].to_numpy(dtype=float)
    lows = frame["low"].to_numpy(dtype=float)
    closes = frame["close"].to_numpy(dtype=float)
    ts = frame["timestamp"].to_numpy()
    signal_mask = frame["ema_psar_long_signal"].to_numpy(dtype=bool)

    for idx in range(50, len(frame) - HOLD_BARS - 1):
        if idx <= last_exit_idx:
            continue
        if not bool(signal_mask[idx]):
            continue
        signal_count += 1
        row = frame.iloc[idx]
        allow, gate_reason = variant_policy(row, variant)
        if not allow:
            continue
        entry_idx = idx + 1
        exit_idx = idx + HOLD_BARS
        entry_price = float(opens[entry_idx])
        exit_price = float(opens[exit_idx])
        gross_return = exit_price / entry_price - 1.0
        path_closes = closes[entry_idx: exit_idx + 1]
        early_fail = bool((path_closes[:EARLY_FAIL_BARS] < entry_price).any())
        rows.append(
            {
                "asset": asset,
                "variant": variant,
                "signal_ts": ts[idx],
                "entry_ts": ts[entry_idx],
                "exit_ts": ts[exit_idx],
                "entry_price": entry_price,
                "exit_price": exit_price,
                "gross_return": gross_return,
                "early_fail_4bars": early_fail,
                "fwd3_ret": float(path_closes[min(3, len(path_closes)-1)] / entry_price - 1.0),
                "mae_8bar": float((lows[entry_idx: exit_idx + 1] / entry_price - 1.0).min()),
                "mfe_8bar": float((highs[entry_idx: exit_idx + 1] / entry_price - 1.0).max()),
                "post_trigger_depth_pct": float(row["post_trigger_depth_pct"]) if pd.notna(row["post_trigger_depth_pct"]) else np.nan,
                "prearmed_depth_pct": float(row["prearmed_depth_pct"]) if pd.notna(row["prearmed_depth_pct"]) else np.nan,
                "prearmed_recent_touch": bool(row["prearmed_recent_touch"]),
                "prearmed_recent_green": bool(row["prearmed_recent_green"]),
                "prearmed_recent_vol_spike": bool(row["prearmed_recent_vol_spike"]),
                "prearmed_recent_adx_max": float(row["prearmed_recent_adx_max"]) if pd.notna(row["prearmed_recent_adx_max"]) else np.nan,
                "gate_reason": gate_reason,
            }
        )
        last_exit_idx = exit_idx
    return pd.DataFrame(rows), signal_count


def summarize(trades: pd.DataFrame, signal_counts: dict[str, int]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    overall_rows = []
    asset_rows = []
    time_rows = []
    threshold_rows = []

    for cost in COSTS:
        cost_df = trades.copy()
        cost_df["net_return"] = cost_df["gross_return"] - 2.0 * cost / 10000.0
        for variant in VARIANTS:
            var_df = cost_df[cost_df["variant"] == variant].copy()
            asset_sums = var_df.groupby("asset")["net_return"].sum() if not var_df.empty else pd.Series(dtype=float)
            retention_parts = []
            for asset in ASSETS:
                total_sig = max(signal_counts.get(asset, 0), 1)
                retention_parts.append(len(var_df[var_df["asset"] == asset]) / total_sig)
            overall_rows.append(
                {
                    "variant": variant,
                    "cost_bps": cost,
                    "mean_total_return": asset_sums.mean() if not asset_sums.empty else np.nan,
                    "positive_asset_ratio": (asset_sums > 0).mean() if not asset_sums.empty else np.nan,
                    "mean_trades": var_df.groupby("asset").size().mean() if not var_df.empty else 0.0,
                    "trade_count_retention": float(np.mean(retention_parts)) if retention_parts else np.nan,
                    "mean_early_fail_4bars": var_df.groupby("asset")["early_fail_4bars"].mean().mean() if not var_df.empty else np.nan,
                    "median_fwd3_ret": var_df["fwd3_ret"].median() if not var_df.empty else np.nan,
                    "median_prearmed_depth_pct": var_df["prearmed_depth_pct"].median() if not var_df.empty else np.nan,
                }
            )
            if cost != PRIMARY_COST:
                continue
            for asset in ASSETS:
                sub = var_df[var_df["asset"] == asset]
                asset_rows.append(
                    {
                        "asset": asset,
                        "variant": variant,
                        "trades": len(sub),
                        "total_return": sub["net_return"].sum() if not sub.empty else np.nan,
                        "mean_return": sub["net_return"].mean() if not sub.empty else np.nan,
                        "early_fail_4bars": sub["early_fail_4bars"].mean() if not sub.empty else np.nan,
                        "median_prearmed_depth_pct": sub["prearmed_depth_pct"].median() if not sub.empty else np.nan,
                    }
                )
        if cost != PRIMARY_COST:
            continue
        primary = cost_df[cost_df["variant"] == PRIMARY_VARIANT].sort_values("entry_ts").reset_index(drop=True)
        if not primary.empty:
            primary["bucket"] = pd.qcut(np.arange(len(primary)), q=3, labels=["bucket_1", "bucket_2", "bucket_3"], duplicates="drop")
            for bucket, bucket_df in primary.groupby("bucket", observed=False):
                asset_sums = bucket_df.groupby("asset")["net_return"].sum()
                time_rows.append(
                    {
                        "bucket": bucket,
                        "mean_total_return": asset_sums.mean() if not asset_sums.empty else np.nan,
                        "positive_asset_ratio": (asset_sums > 0).mean() if not asset_sums.empty else np.nan,
                        "trades": len(bucket_df),
                        "mean_early_fail_4bars": bucket_df["early_fail_4bars"].mean(),
                        "median_fwd3_ret": bucket_df["fwd3_ret"].median(),
                    }
                )
        for thr in [0.75, 1.0, 1.25]:
            sub = cost_df[cost_df["variant"] == f"prearmed_depth_{str(thr).replace('.', 'p')}"]
            asset_sums = sub.groupby("asset")["net_return"].sum() if not sub.empty else pd.Series(dtype=float)
            threshold_rows.append(
                {
                    "threshold_pct": thr,
                    "mean_total_return": asset_sums.mean() if not asset_sums.empty else np.nan,
                    "positive_asset_ratio": (asset_sums > 0).mean() if not asset_sums.empty else np.nan,
                    "mean_trades": sub.groupby("asset").size().mean() if not sub.empty else 0.0,
                    "trade_count_retention": np.mean([len(sub[sub["asset"] == asset]) / max(signal_counts.get(asset, 0), 1) for asset in ASSETS]),
                    "mean_early_fail_4bars": sub.groupby("asset")["early_fail_4bars"].mean().mean() if not sub.empty else np.nan,
                }
            )

    return pd.DataFrame(overall_rows), pd.DataFrame(asset_rows), pd.DataFrame(time_rows), pd.DataFrame(threshold_rows)


def decide_verdict(overall: pd.DataFrame, time_summary: pd.DataFrame) -> tuple[str, str, str]:
    baseline = overall[(overall["variant"] == "baseline") & (overall["cost_bps"] == PRIMARY_COST)].iloc[0]
    candidates = overall[(overall["variant"] != "baseline") & (overall["cost_bps"] == PRIMARY_COST)].copy()
    candidates = candidates.sort_values(["mean_total_return", "positive_asset_ratio", "trade_count_retention"], ascending=[False, False, False])
    primary = candidates.iloc[0]
    best_variant = str(primary["variant"])
    b_ret = float(baseline["mean_total_return"]) if pd.notna(baseline["mean_total_return"]) else -999.0
    b_fail = float(baseline["mean_early_fail_4bars"]) if pd.notna(baseline["mean_early_fail_4bars"]) else 1.0
    p_ret = float(primary["mean_total_return"]) if pd.notna(primary["mean_total_return"]) else -999.0
    p_pos = float(primary["positive_asset_ratio"]) if pd.notna(primary["positive_asset_ratio"]) else 0.0
    p_retention = float(primary["trade_count_retention"]) if pd.notna(primary["trade_count_retention"]) else 0.0
    p_fail = float(primary["mean_early_fail_4bars"]) if pd.notna(primary["mean_early_fail_4bars"]) else 1.0
    pos_buckets = float((time_summary["mean_total_return"] > 0).mean()) if not time_summary.empty else 0.0

    if p_ret > 0 and p_pos >= 2 / 3 and p_retention >= 0.55 and p_fail <= b_fail * 0.92 and pos_buckets >= 2 / 3:
        return (
            "promote_to_P2 / paper candidate",
            f"{best_variant} 在成本后转正、跨资产至少 2/3 为正、retention 仍够厚，而且时间分桶也不是只剩单个口袋。",
            best_variant,
        )
    if p_ret > b_ret + 0.01 and p_retention >= 0.45 and (p_fail < b_fail or p_pos >= float(baseline['positive_asset_ratio'])):
        return (
            "keep_P1 / mixed but honest",
            f"{best_variant} 比 baseline 更诚实：不是再走 post-trigger 假过滤，而是前置 pre-armed depth budget；但改善还不够硬到升 P2。",
            best_variant,
        )
    return (
        "park / evidence_pool",
        f"{best_variant} 当前仍不够硬：要么改善太薄，要么 retention / 跨资产一致性不够，仍不足以继续占 active fast-lane。",
        best_variant,
    )


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    frames = {asset: build_frame(asset, symbol) for asset, symbol in ASSETS.items()}
    signal_counts: dict[str, int] = {}
    trade_frames = []
    for asset, frame in frames.items():
        signal_counts[asset] = int(frame["ema_psar_long_signal"].sum())
        for variant in VARIANTS:
            trades, _ = build_candidates(frame, asset, variant)
            if not trades.empty:
                trade_frames.append(trades)
    trades = pd.concat(trade_frames, ignore_index=True) if trade_frames else pd.DataFrame()

    overall, asset_summary, time_summary, threshold_summary = summarize(trades, signal_counts)
    verdict, verdict_reason, best_variant = decide_verdict(overall, time_summary)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    overall = overall.sort_values(["cost_bps", "variant"]).reset_index(drop=True)
    asset_summary = asset_summary.sort_values(["variant", "asset"]).reset_index(drop=True)
    time_summary = time_summary.sort_values(["bucket"]).reset_index(drop=True)
    threshold_summary = threshold_summary.sort_values(["threshold_pct"]).reset_index(drop=True)

    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    time_summary.to_csv(ART_DIR / "time_bucket_summary.csv", index=False)
    threshold_summary.to_csv(ART_DIR / "prearmed_threshold_summary.csv", index=False)
    trades.to_csv(ART_DIR / "trade_log.csv", index=False)
    pd.DataFrame([
        {
            "generated_at_utc": generated_at,
            "execution": "signal bar and earlier only + next-bar open + no-overlap + hold 8 bars",
            "universe": "BTC/ETH/SOL 120d 15m local cache",
            "variants": "baseline / post_trigger_depth_1p0 / prearmed_depth_0p75 / prearmed_depth_1p0 / prearmed_depth_1p25 / prearmed_depth_1p0_plus_filters",
            "primary_variant": PRIMARY_VARIANT,
            "best_variant": best_variant,
            "verdict": verdict,
            "verdict_reason": verdict_reason,
        }
    ]).to_csv(ART_DIR / "meta.csv", index=False)

    baseline = overall[(overall["variant"] == "baseline") & (overall["cost_bps"] == PRIMARY_COST)].iloc[0]
    post = overall[(overall["variant"] == "post_trigger_depth_1p0") & (overall["cost_bps"] == PRIMARY_COST)].iloc[0]
    pre = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps"] == PRIMARY_COST)].iloc[0]
    best = overall[(overall["variant"] == best_variant) & (overall["cost_bps"] == PRIMARY_COST)].iloc[0]
    filt = overall[(overall["variant"] == "prearmed_depth_1p0_plus_filters") & (overall["cost_bps"] == PRIMARY_COST)].iloc[0]

    body = f"""
<h1>Rank 95 / Vajra controlled-pullback depth-budget clean replication</h1>
<p class='muted'>生成时间：{escape(generated_at)} | 口径：固定 BTC/ETH/SOL 120d 15m 本地 cache，统一 <code>signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars</code>。这轮只回答一件事：depth budget 应该继续放在 trigger 后，还是该前置成 pre-armed 状态预算。</p>
<div class='card'>
  <h2>Hard verdict</h2>
  <p><strong>{escape(verdict)}</strong></p>
  <p>{escape(verdict_reason)}</p>
  <ul>
    <li>baseline @ 6bps：收益 {escape(pct(baseline['mean_total_return']))}，资产为正占比 {escape(pct(baseline['positive_asset_ratio']))}，retention {escape(pct(baseline['trade_count_retention']))}，4bar early-fail {escape(pct(baseline['mean_early_fail_4bars']))}</li>
    <li>post_trigger_depth_1p0 @ 6bps：收益 {escape(pct(post['mean_total_return']))}，资产为正占比 {escape(pct(post['positive_asset_ratio']))}，retention {escape(pct(post['trade_count_retention']))}</li>
    <li>{escape(best_variant)} @ 6bps（最佳 pre-armed 子臂）：收益 {escape(pct(best['mean_total_return']))}，资产为正占比 {escape(pct(best['positive_asset_ratio']))}，retention {escape(pct(best['trade_count_retention']))}，4bar early-fail {escape(pct(best['mean_early_fail_4bars']))}</li>
    <li>prearmed_depth_1p0_plus_filters @ 6bps：收益 {escape(pct(filt['mean_total_return']))}，资产为正占比 {escape(pct(filt['positive_asset_ratio']))}，retention {escape(pct(filt['trade_count_retention']))}</li>
  </ul>
</div>
<div class='card'>
  <h2>这次最小 clean replication 怎么做</h2>
  <ul>
    <li>base setup 固定为 <code>ema_psar_long</code>，不引入新的方向 trigger。</li>
    <li><code>post_trigger_depth_1p0</code>：信号出现后，直接用当根 rolling <code>{LOOKBACK}</code> bars 的 depth 是否 <code>&lt;=1.0%</code> 做 trigger 后 gate。</li>
    <li><code>prearmed_depth_x</code>：只读取信号前 <code>{LOOKBACK}</code> bars 的已完成信息；若最近出现 toward-EMA 回踩、touch EMA、且回踩深度预算 <code>&lt;=x%</code>，才允许后续 continuation trigger 放行。</li>
    <li><code>prearmed_depth_1p0_plus_filters</code>：只把 repo 的 <code>green / volume&gt;1.2x / ADX&gt;=25</code> 当邻近过滤臂，验证它是不是只会暴力缩样本。</li>
  </ul>
</div>
<div class='card'>
  <h2>Overall summary</h2>
  {render_table(overall, percent_cols={'mean_total_return','positive_asset_ratio','trade_count_retention','mean_early_fail_4bars','median_fwd3_ret'})}
</div>
<div class='card'>
  <h2>Pre-armed threshold summary ({int(PRIMARY_COST)}bps)</h2>
  {render_table(threshold_summary, percent_cols={'mean_total_return','positive_asset_ratio','trade_count_retention','mean_early_fail_4bars'})}
</div>
<div class='card'>
  <h2>Asset summary ({int(PRIMARY_COST)}bps)</h2>
  {render_table(asset_summary[asset_summary['variant'] == PRIMARY_VARIANT], percent_cols={'total_return','mean_return','early_fail_4bars'})}
</div>
<div class='card'>
  <h2>Time stability snapshot ({PRIMARY_VARIANT} @ {int(PRIMARY_COST)}bps)</h2>
  {render_table(time_summary, percent_cols={'mean_total_return','positive_asset_ratio','mean_early_fail_4bars','median_fwd3_ret'})}
</div>
<div class='card'>
  <h2>Artifacts</h2>
  <ul>
    <li><code>reports/artifacts/scout_rank95_vajra_controlled_pullback_15m/overall_summary.csv</code></li>
    <li><code>reports/artifacts/scout_rank95_vajra_controlled_pullback_15m/asset_summary.csv</code></li>
    <li><code>reports/artifacts/scout_rank95_vajra_controlled_pullback_15m/prearmed_threshold_summary.csv</code></li>
    <li><code>reports/artifacts/scout_rank95_vajra_controlled_pullback_15m/time_bucket_summary.csv</code></li>
    <li><code>reports/artifacts/scout_rank95_vajra_controlled_pullback_15m/trade_log.csv</code></li>
  </ul>
</div>
"""
    write_html(SITE_DIR / "report.html", "Rank 95 Vajra controlled-pullback clean replication", body)

    reading_body = f"""
<h1>Rank 95 / Vajra controlled-pullback depth-budget clean replication</h1>
<p class='muted'>这轮只回答：depth budget 该留在 trigger 后，还是前置成 pre-armed 状态预算。</p>
<div class='card'>
  <p><strong>结论：</strong>{escape(verdict)}</p>
  <p>{escape(verdict_reason)}</p>
  <p>最佳 pre-armed 子臂是 <code>{escape(best_variant)}</code> @ <code>{int(PRIMARY_COST)}bps/side</code>：mean_total_return={escape(pct(best['mean_total_return']))}，positive_asset_ratio={escape(pct(best['positive_asset_ratio']))}，trade_count_retention={escape(pct(best['trade_count_retention']))}，4bar early-fail={escape(pct(best['mean_early_fail_4bars']))}。</p>
  <p>对照 post-trigger：mean_total_return={escape(pct(post['mean_total_return']))}，trade_count_retention={escape(pct(post['trade_count_retention']))}。</p>
  <p><a href='../../factors/scout_rank95_vajra_controlled_pullback_15m/report.html'>查看完整报告页</a></p>
</div>
"""
    write_html(READING_PATH, "Rank 95 Vajra controlled-pullback clean replication", reading_body)

    print(f"hard_verdict={verdict}")
    print(f"best_variant={best_variant}")
    print(f"baseline_mean_total_return={baseline['mean_total_return']:.6f}")
    print(f"primary_mean_total_return={best['mean_total_return']:.6f}")
    print(f"primary_positive_asset_ratio={best['positive_asset_ratio']:.6f}")
    print(f"primary_trade_count_retention={best['trade_count_retention']:.6f}")


if __name__ == "__main__":
    main()
