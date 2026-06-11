#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
EVENTS_PATH = ROOT / "reports" / "artifacts" / "literature" / "macro_event_overlay_quickcheck_events_2026-03-19.csv"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank88_macro_event_overlay_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank88_macro_event_overlay_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank88_macro_event_blackout_clean_replication.html"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
EVENT_ASSET_MAP = {"BTC-USD": "BTC", "ETH-USD": "ETH", "SOL-USD": "SOL"}
SETUPS = ["ema_psar_long", "fib_retest_long", "breakout_short"]
VARIANTS = ["baseline", "blackout_pm1h", "size_down_0p5x", "hybrid_blackout_then_size"]
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0]
HOLD_BARS = 8
EARLY_FAIL_BARS = 4
EPS = 1e-12
CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1180px; margin: 32px auto; padding: 0 18px 48px; line-height: 1.68; color: #111827; background: #f8fafc; }
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
    df["fib_382"] = df["swing_low_30"] + 0.382 * rng
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
    return df


def load_events() -> pd.DataFrame:
    events = pd.read_csv(EVENTS_PATH)
    events["event_ts"] = pd.to_datetime(events["event_ts"], utc=True)
    return events[["asset", "event_type", "event_ts"]].drop_duplicates().sort_values(["asset", "event_ts"]).reset_index(drop=True)


def nearest_event_info(asset: str, signal_ts: pd.Timestamp, events: pd.DataFrame) -> tuple[pd.Timestamp | pd.NaT, str | None, float | None]:
    sub = events[events["asset"] == EVENT_ASSET_MAP[asset]]
    if sub.empty:
        return pd.NaT, None, None
    deltas = (sub["event_ts"] - signal_ts).dt.total_seconds() / 60.0
    idx = deltas.abs().idxmin()
    row = sub.loc[idx]
    return row["event_ts"], row["event_type"], float(deltas.loc[idx])


def signal_policy(asset: str, signal_ts: pd.Timestamp, variant: str, events: pd.DataFrame) -> tuple[bool, float, pd.Timestamp | pd.NaT, str | None, float | None, str]:
    event_ts, event_type, mins_to_event = nearest_event_info(asset, signal_ts, events)
    if mins_to_event is None:
        return True, 1.0, pd.NaT, None, None, "no_event"

    phase = "outside"
    if -60 <= mins_to_event <= 60:
        phase = "pm1h"
    elif -30 <= mins_to_event <= 30:
        phase = "pm30m"
    elif 30 < mins_to_event <= 120:
        phase = "post_30_120"
    elif -120 <= mins_to_event < -60:
        phase = "pre_120_60"

    if variant == "baseline":
        return True, 1.0, event_ts, event_type, mins_to_event, phase
    if variant == "blackout_pm1h":
        allow = not (-60 <= mins_to_event <= 60)
        return allow, 1.0, event_ts, event_type, mins_to_event, phase
    if variant == "size_down_0p5x":
        size_mult = 0.5 if -60 <= mins_to_event <= 60 else 1.0
        return True, size_mult, event_ts, event_type, mins_to_event, phase
    if variant == "hybrid_blackout_then_size":
        if -30 <= mins_to_event <= 30:
            return False, 1.0, event_ts, event_type, mins_to_event, phase
        size_mult = 0.5 if 30 < mins_to_event <= 120 else 1.0
        return True, size_mult, event_ts, event_type, mins_to_event, phase
    raise ValueError(f"unknown variant: {variant}")


def build_trades(frame: pd.DataFrame, asset: str, setup: str, variant: str, events: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    signal_col = f"{setup}_signal"
    rows = []
    last_exit_idx = -1
    signal_events = 0
    direction = -1.0 if setup.endswith("short") else 1.0

    ts = frame["timestamp"].to_numpy()
    opens = frame["open"].to_numpy(dtype=float)
    closes = frame["close"].to_numpy(dtype=float)
    signal_mask = frame[signal_col].to_numpy(dtype=bool)

    for idx in range(60, len(frame) - HOLD_BARS - 2):
        if idx <= last_exit_idx:
            continue
        if not bool(signal_mask[idx]):
            continue
        signal_events += 1
        signal_ts = pd.Timestamp(ts[idx])
        allow, size_mult, event_ts, event_type, mins_to_event, phase = signal_policy(asset, signal_ts, variant, events)
        if not allow:
            continue
        entry_idx = idx + 1
        exit_idx = idx + HOLD_BARS
        entry = float(opens[entry_idx])
        exit_price = float(closes[exit_idx])
        gross = direction * (exit_price / entry - 1.0)
        signed_path = direction * (closes[entry_idx: exit_idx + 1] / entry - 1.0)
        early_fail = bool((signed_path[:EARLY_FAIL_BARS] < 0).any())
        rows.append(
            {
                "asset": asset,
                "setup": setup,
                "variant": variant,
                "signal_ts": signal_ts,
                "entry_ts": ts[entry_idx],
                "exit_ts": ts[exit_idx],
                "entry_price": entry,
                "exit_price": exit_price,
                "gross_return": gross,
                "position_size_mult": size_mult,
                "scaled_gross_return": gross * size_mult,
                "early_fail_4bars": early_fail,
                "nearest_event_ts": event_ts,
                "nearest_event_type": event_type,
                "mins_to_event": mins_to_event,
                "event_phase": phase,
                "within_pm1h": mins_to_event is not None and (-60 <= mins_to_event <= 60),
                "within_hybrid_size_window": mins_to_event is not None and (30 < mins_to_event <= 120),
            }
        )
        last_exit_idx = exit_idx
    return pd.DataFrame(rows), signal_events


def summarize(trades: pd.DataFrame, signal_counts: dict[tuple[str, str], int]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    overall_rows = []
    setup_rows = []
    asset_rows = []

    for cost in COSTS:
        cost_df = trades.copy()
        if not cost_df.empty:
            cost_df["net_return"] = cost_df["scaled_gross_return"] - cost_df["position_size_mult"] * (2.0 * cost / 10000.0)
        for variant in VARIANTS:
            var_df = cost_df[cost_df["variant"] == variant]
            asset_means = var_df.groupby("asset")["net_return"].sum() if not var_df.empty else pd.Series(dtype=float)
            retention_parts = []
            for setup in SETUPS:
                total_sig = sum(signal_counts.get((asset, setup), 0) for asset in ASSETS)
                kept = len(var_df[var_df["setup"] == setup])
                retention_parts.append(kept / total_sig if total_sig else np.nan)
            overall_rows.append(
                {
                    "variant": variant,
                    "cost_bps": cost,
                    "mean_total_return": asset_means.mean() if not asset_means.empty else np.nan,
                    "positive_asset_ratio": (asset_means > 0).mean() if not asset_means.empty else np.nan,
                    "mean_trades": var_df.groupby("asset").size().mean() if not var_df.empty else 0.0,
                    "trade_count_retention": np.nanmean(retention_parts) if retention_parts else np.nan,
                    "mean_position_size_mult": var_df.groupby("asset")["position_size_mult"].mean().mean() if not var_df.empty else np.nan,
                    "mean_early_fail_4bars": var_df.groupby("asset")["early_fail_4bars"].mean().mean() if not var_df.empty else np.nan,
                    "pm1h_trade_share": var_df.groupby("asset")["within_pm1h"].mean().mean() if not var_df.empty else np.nan,
                }
            )
            for setup in SETUPS:
                sub = var_df[var_df["setup"] == setup]
                asset_setup = sub.groupby("asset")["net_return"].sum() if not sub.empty else pd.Series(dtype=float)
                total_sig = sum(signal_counts.get((asset, setup), 0) for asset in ASSETS)
                setup_rows.append(
                    {
                        "setup": setup,
                        "variant": variant,
                        "cost_bps": cost,
                        "mean_total_return": asset_setup.mean() if not asset_setup.empty else np.nan,
                        "positive_asset_ratio": (asset_setup > 0).mean() if not asset_setup.empty else np.nan,
                        "mean_trades": sub.groupby("asset").size().mean() if not sub.empty else 0.0,
                        "trade_count_retention": len(sub) / total_sig if total_sig else np.nan,
                        "mean_position_size_mult": sub.groupby("asset")["position_size_mult"].mean().mean() if not sub.empty else np.nan,
                        "mean_early_fail_4bars": sub.groupby("asset")["early_fail_4bars"].mean().mean() if not sub.empty else np.nan,
                    }
                )
            for asset in ASSETS:
                sub = var_df[var_df["asset"] == asset]
                asset_rows.append(
                    {
                        "asset": asset,
                        "variant": variant,
                        "cost_bps": cost,
                        "total_return": sub["net_return"].sum() if not sub.empty else np.nan,
                        "trades": len(sub),
                        "mean_position_size_mult": sub["position_size_mult"].mean() if not sub.empty else np.nan,
                        "early_fail_4bars": sub["early_fail_4bars"].mean() if not sub.empty else np.nan,
                    }
                )
    return pd.DataFrame(overall_rows), pd.DataFrame(setup_rows), pd.DataFrame(asset_rows)


def decide_verdict(overall: pd.DataFrame) -> tuple[str, str, str]:
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
    p_trade_share = float(primary["pm1h_trade_share"]) if pd.notna(primary["pm1h_trade_share"]) else 0.0

    if p_ret > 0 and p_pos >= 2/3 and p_retention >= 0.60 and p_fail <= b_fail and p_trade_share >= 0.08:
        return "promote_to_P2 / paper-candidate pool", (
            f"{best_variant} 在 6bps 下已经不是单纯靠砍样本少亏：成本后均值转正、跨资产至少 2/3 为正、retention 仍 >= 60%，且 early-fail 没比 baseline 更坏，"
            "足够升到 paper-candidate pool。"
        ), best_variant
    if p_ret > b_ret + 0.005 and p_retention >= 0.45 and (p_fail < b_fail or p_pos >= 1/3) and p_trade_share >= 0.05:
        return "keep_P1 / mixed but honest", (
            f"{best_variant} 相比 baseline 有一定去亏损/去坏交易改善，但跨资产与 retention 还不够硬，先留在 P1 evidence_pool，"
            "不直接升到 paper candidate。"
        ), best_variant
    return "park / evidence_pool", (
        f"{best_variant} 当前主要还是靠回避极少数事件窗或轻微缩仓换少亏，保留率/跨资产一致性不够，"
        "还不足以诚实占住 fast-lane。"
    ), best_variant


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    events = load_events()
    frames = {asset: build_frame(asset, symbol) for asset, symbol in ASSETS.items()}
    signal_counts: dict[tuple[str, str], int] = {}
    trade_frames = []

    for asset, frame in frames.items():
        for setup in SETUPS:
            signal_counts[(asset, setup)] = int(frame[f"{setup}_signal"].sum())
            for variant in VARIANTS:
                trades, _ = build_trades(frame, asset, setup, variant, events)
                if not trades.empty:
                    trade_frames.append(trades)

    trades = pd.concat(trade_frames, ignore_index=True) if trade_frames else pd.DataFrame()
    overall, setup_summary, asset_summary = summarize(trades, signal_counts)
    verdict, verdict_reason, best_variant = decide_verdict(overall)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    overall = overall.sort_values(["cost_bps", "variant"]).reset_index(drop=True)
    setup_summary = setup_summary.sort_values(["cost_bps", "setup", "variant"]).reset_index(drop=True)
    asset_summary = asset_summary.sort_values(["cost_bps", "asset", "variant"]).reset_index(drop=True)

    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    setup_summary.to_csv(ART_DIR / "setup_summary.csv", index=False)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    if not trades.empty:
        trades.to_csv(ART_DIR / "trade_samples.csv", index=False)

    meta = pd.DataFrame([
        {
            "generated_at_utc": generated_at,
            "universe": "BTC/ETH/SOL 120d 15m local cache + pre-listed FOMC/CPI timestamps from public schedule",
            "execution": "signal-bar-and-earlier only + next-bar open + no-overlap + hold 8 bars",
            "variants": "baseline / blackout[-1h,+1h] / size_down_0.5x / hybrid[-30m,+30m]+(+30m,+120m size)",
            "best_variant": best_variant,
            "verdict": verdict,
            "verdict_reason": verdict_reason,
        }
    ])
    meta.to_csv(ART_DIR / "meta.csv", index=False)

    baseline = overall[(overall["variant"] == "baseline") & (overall["cost_bps"] == PRIMARY_COST)].iloc[0]
    blackout = overall[(overall["variant"] == "blackout_pm1h") & (overall["cost_bps"] == PRIMARY_COST)].iloc[0]
    size_down = overall[(overall["variant"] == "size_down_0p5x") & (overall["cost_bps"] == PRIMARY_COST)].iloc[0]
    hybrid = overall[(overall["variant"] == "hybrid_blackout_then_size") & (overall["cost_bps"] == PRIMARY_COST)].iloc[0]

    body = f"""
<h1>Rank 88 / macro-event blackout + size-down risk overlay</h1>
<p class='muted'>生成时间：{escape(generated_at)} | 口径：固定复用 BTC/ETH/SOL 120d 15m 本地 cache，与公开、事前可得的 FOMC/CPI 发布时间；统一 <code>next-bar open + no-overlap + hold 8 bars</code>。</p>
<div class='card'>
  <h2>Hard verdict</h2>
  <p><strong>{escape(verdict)}</strong></p>
  <p>{escape(verdict_reason)}</p>
  <ul>
    <li>baseline @ 6bps：收益 {escape(pct(baseline['mean_total_return']))}，资产为正占比 {escape(pct(baseline['positive_asset_ratio']))}，retention {escape(pct(baseline['trade_count_retention']))}，4bar early-fail {escape(pct(baseline['mean_early_fail_4bars']))}</li>
    <li>blackout[-1h,+1h]：收益 {escape(pct(blackout['mean_total_return']))}，资产为正占比 {escape(pct(blackout['positive_asset_ratio']))}，retention {escape(pct(blackout['trade_count_retention']))}，4bar early-fail {escape(pct(blackout['mean_early_fail_4bars']))}</li>
    <li>size_down_0.5x：收益 {escape(pct(size_down['mean_total_return']))}，资产为正占比 {escape(pct(size_down['positive_asset_ratio']))}，retention {escape(pct(size_down['trade_count_retention']))}，平均仓位 {escape(pct(size_down['mean_position_size_mult']))}，4bar early-fail {escape(pct(size_down['mean_early_fail_4bars']))}</li>
    <li>hybrid：收益 {escape(pct(hybrid['mean_total_return']))}，资产为正占比 {escape(pct(hybrid['positive_asset_ratio']))}，retention {escape(pct(hybrid['trade_count_retention']))}，平均仓位 {escape(pct(hybrid['mean_position_size_mult']))}，4bar early-fail {escape(pct(hybrid['mean_early_fail_4bars']))}</li>
  </ul>
</div>
<div class='card'>
  <h2>这次最小 clean replication 怎么做</h2>
  <ul>
    <li>base setups：<code>ema_psar_long</code>、<code>fib_retest_long</code>、<code>breakout_short</code></li>
    <li>只比较四臂：<code>baseline</code> / <code>blackout_pm1h</code> / <code>size_down_0p5x</code> / <code>hybrid_blackout_then_size</code></li>
    <li>事件时间只取公开日程里的 <code>FOMC / CPI</code> 发布时间，不用事后波动回填窗口。</li>
    <li><code>blackout_pm1h</code>：信号时间落在 <code>[-60m,+60m]</code> 直接不做。</li>
    <li><code>size_down_0p5x</code>：仅在 <code>[-60m,+60m]</code> 把仓位乘数降到 <code>0.5x</code>，其余不变。</li>
    <li><code>hybrid</code>：<code>[-30m,+30m]</code> blackout；<code>(+30m,+120m]</code> size-down 0.5x。</li>
  </ul>
</div>
<div class='card'>
  <h2>Overall summary</h2>
  {render_table(overall, percent_cols={'mean_total_return','positive_asset_ratio','trade_count_retention','mean_position_size_mult','mean_early_fail_4bars','pm1h_trade_share'})}
</div>
<div class='card'>
  <h2>Setup summary</h2>
  {render_table(setup_summary, percent_cols={'mean_total_return','positive_asset_ratio','trade_count_retention','mean_position_size_mult','mean_early_fail_4bars'})}
</div>
<div class='card'>
  <h2>Asset summary</h2>
  {render_table(asset_summary, percent_cols={'total_return','mean_position_size_mult','early_fail_4bars'})}
</div>
<div class='card'>
  <h2>Artifacts</h2>
  <ul>
    <li><code>reports/artifacts/scout_rank88_macro_event_overlay_15m/overall_summary.csv</code></li>
    <li><code>reports/artifacts/scout_rank88_macro_event_overlay_15m/setup_summary.csv</code></li>
    <li><code>reports/artifacts/scout_rank88_macro_event_overlay_15m/asset_summary.csv</code></li>
    <li><code>reports/artifacts/scout_rank88_macro_event_overlay_15m/trade_samples.csv</code></li>
    <li><code>reports/artifacts/scout_rank88_macro_event_overlay_15m/meta.csv</code></li>
  </ul>
</div>
"""
    write_html(SITE_DIR / "report.html", "Rank 88 macro-event blackout clean replication", body)
    write_html(READING_PATH, "Rank 88 macro-event blackout clean replication", body)


if __name__ == "__main__":
    main()
