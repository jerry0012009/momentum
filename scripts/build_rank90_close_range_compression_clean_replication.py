#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank90_close_range_compression_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank90_close_range_compression_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank90_close_range_compression_clean_replication.html"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
SETUPS = ["ema_psar_long", "fib_retest_long", "breakout_short"]
VARIANTS = ["baseline", "long_admission_only", "short_veto_or_halfsize"]
PRIMARY_VARIANT = "short_veto_or_halfsize"
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0]
HOLD_BARS = 8
EARLY_FAIL_BARS = 4
CONS_BARS = 13
CONS_PCT = 0.01
BREAK_LOOKBACK = 4
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


def build_compression_overlay(df: pd.DataFrame) -> pd.DataFrame:
    min_close = df["close"].rolling(CONS_BARS, min_periods=CONS_BARS).min().shift(1)
    max_close = df["close"].rolling(CONS_BARS, min_periods=CONS_BARS).max().shift(1)
    max_high = df["high"].rolling(CONS_BARS, min_periods=CONS_BARS).max().shift(1)
    min_low = df["low"].rolling(CONS_BARS, min_periods=CONS_BARS).min().shift(1)
    consolidating = (min_close > max_close * (1.0 - CONS_PCT)).fillna(False)
    up_break = consolidating & (df["close"] > max_high)
    down_break = consolidating & (df["close"] < min_low)

    out = df.copy()
    out["cons_min_close"] = min_close
    out["cons_max_close"] = max_close
    out["cons_range_high"] = max_high
    out["cons_range_low"] = min_low
    out["consolidating"] = consolidating
    out["compression_up_break"] = up_break
    out["compression_down_break"] = down_break
    out["recent_up_break"] = up_break.rolling(BREAK_LOOKBACK, min_periods=1).max().shift(1).fillna(0).astype(bool)
    out["recent_down_break"] = down_break.rolling(BREAK_LOOKBACK, min_periods=1).max().shift(1).fillna(0).astype(bool)
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

    return build_compression_overlay(df)


def variant_policy(row: pd.Series, setup: str, variant: str) -> tuple[bool, float, str]:
    if variant == "baseline":
        return True, 1.0, "baseline"
    is_long = setup.endswith("long")
    if variant == "long_admission_only":
        if not is_long:
            return True, 1.0, "short_unchanged"
        allow = bool(row.get("recent_up_break", False))
        return allow, 1.0, "recent_up_break" if allow else "no_recent_up_break"

    if is_long:
        allow = bool(row.get("recent_up_break", False))
        return allow, 1.0, "recent_up_break" if allow else "no_recent_up_break"
    if bool(row.get("recent_down_break", False)):
        return True, 0.5, "recent_down_break_halfsize"
    return True, 1.0, "short_no_compression_break"


def build_trades(frame: pd.DataFrame, asset: str, setup: str, variant: str) -> tuple[pd.DataFrame, int]:
    signal_col = f"{setup}_signal"
    rows = []
    signal_events = 0
    last_exit_idx = -1
    direction = -1.0 if setup.endswith("short") else 1.0

    ts = frame["timestamp"].to_numpy()
    opens = frame["open"].to_numpy(dtype=float)
    closes = frame["close"].to_numpy(dtype=float)
    signal_mask = frame[signal_col].to_numpy(dtype=bool)

    for idx in range(max(60, CONS_BARS + BREAK_LOOKBACK + 2), len(frame) - HOLD_BARS - 2):
        if idx <= last_exit_idx:
            continue
        if not bool(signal_mask[idx]):
            continue
        signal_events += 1
        row = frame.iloc[idx]
        allow, size_mult, gate_reason = variant_policy(row, setup, variant)
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
                "signal_ts": ts[idx],
                "entry_ts": ts[entry_idx],
                "exit_ts": ts[exit_idx],
                "entry_price": entry,
                "exit_price": exit_price,
                "gross_return": gross,
                "position_size_mult": size_mult,
                "scaled_gross_return": gross * size_mult,
                "early_fail_4bars": early_fail,
                "gate_reason": gate_reason,
                "recent_up_break": bool(row.get("recent_up_break", False)),
                "recent_down_break": bool(row.get("recent_down_break", False)),
                "consolidating": bool(row.get("consolidating", False)),
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


def decide_verdict(overall: pd.DataFrame, setup_summary: pd.DataFrame) -> tuple[str, str, str]:
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

    best_setup = setup_summary[(setup_summary["variant"] == best_variant) & (setup_summary["cost_bps"] == PRIMARY_COST)]["mean_total_return"].max()
    if pd.isna(best_setup):
        best_setup = -999.0

    if p_ret > 0 and p_pos >= 2/3 and p_retention >= 0.40 and p_fail <= b_fail * 0.92:
        return "promote_to_P2 / paper-candidate pool", (
            f"{best_variant} 在 6bps 下不是单纯靠砍样本少亏：成本后均值转正、跨资产至少 2/3 为正、retention 仍 >= 40%，且 4-bar early-fail 相对 baseline 明显改善。"
        ), best_variant
    if p_ret > b_ret + 0.005 and p_retention >= 0.18 and (p_fail < b_fail or best_setup > 0):
        return "keep_P1 / mixed but honest", (
            f"{best_variant} 相比 baseline 有一定 long-admission / short-veto 改善，但 retention 与跨资产一致性还不够硬，先留在 P1 evidence_pool。"
        ), best_variant
    return "park / evidence_pool", (
        f"{best_variant} 当前仍主要靠缩样本或局部 setup 少亏，trade_count_retention / 跨资产一致性都不够，仍不足以诚实占住 fast-lane。"
    ), best_variant


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    frames = {asset: build_frame(asset, symbol) for asset, symbol in ASSETS.items()}
    signal_counts: dict[tuple[str, str], int] = {}
    trade_frames = []

    for asset, frame in frames.items():
        for setup in SETUPS:
            signal_counts[(asset, setup)] = int(frame[f"{setup}_signal"].sum())
            for variant in VARIANTS:
                trades, _ = build_trades(frame, asset, setup, variant)
                if not trades.empty:
                    trade_frames.append(trades)

    trades = pd.concat(trade_frames, ignore_index=True) if trade_frames else pd.DataFrame()
    overall, setup_summary, asset_summary = summarize(trades, signal_counts)
    verdict, verdict_reason, best_variant = decide_verdict(overall, setup_summary)
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
            "universe": "BTC/ETH/SOL 120d 15m local cache",
            "execution": "signal-bar-and-earlier only + next-bar open + no-overlap + hold 8 bars",
            "cons_bars": CONS_BARS,
            "cons_pct": CONS_PCT,
            "break_lookback_bars": BREAK_LOOKBACK,
            "variants": "baseline / long_admission_only / short_veto_or_halfsize",
            "best_variant": best_variant,
            "verdict": verdict,
            "verdict_reason": verdict_reason,
        }
    ])
    meta.to_csv(ART_DIR / "meta.csv", index=False)

    baseline = overall[(overall["variant"] == "baseline") & (overall["cost_bps"] == PRIMARY_COST)].iloc[0]
    long_only = overall[(overall["variant"] == "long_admission_only") & (overall["cost_bps"] == PRIMARY_COST)].iloc[0]
    hybrid = overall[(overall["variant"] == "short_veto_or_halfsize") & (overall["cost_bps"] == PRIMARY_COST)].iloc[0]

    body = f"""
<h1>Rank 90 / close-range compression asymmetry</h1>
<p class='muted'>生成时间：{escape(generated_at)} | 口径：固定复用 BTC/ETH/SOL 120d 15m 本地 cache；统一 <code>signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars</code>。</p>
<div class='card'>
  <h2>Hard verdict</h2>
  <p><strong>{escape(verdict)}</strong></p>
  <p>{escape(verdict_reason)}</p>
  <ul>
    <li>baseline @ 6bps：收益 {escape(pct(baseline['mean_total_return']))}，资产为正占比 {escape(pct(baseline['positive_asset_ratio']))}，retention {escape(pct(baseline['trade_count_retention']))}，4bar early-fail {escape(pct(baseline['mean_early_fail_4bars']))}</li>
    <li>long-admission-only：收益 {escape(pct(long_only['mean_total_return']))}，资产为正占比 {escape(pct(long_only['positive_asset_ratio']))}，retention {escape(pct(long_only['trade_count_retention']))}，4bar early-fail {escape(pct(long_only['mean_early_fail_4bars']))}</li>
    <li>short-veto-or-halfsize：收益 {escape(pct(hybrid['mean_total_return']))}，资产为正占比 {escape(pct(hybrid['positive_asset_ratio']))}，retention {escape(pct(hybrid['trade_count_retention']))}，平均仓位 {escape(pct(hybrid['mean_position_size_mult']))}，4bar early-fail {escape(pct(hybrid['mean_early_fail_4bars']))}</li>
  </ul>
</div>
<div class='card'>
  <h2>这次最小 clean replication 怎么做</h2>
  <ul>
    <li>base setups：<code>ema_psar_long</code>、<code>fib_retest_long</code>、<code>breakout_short</code></li>
    <li>压缩判定：前 <code>{CONS_BARS}</code> 根收盘压在 <code>{pct(CONS_PCT)}</code> 窄区间内，且全部 <code>shift(1)</code>，避免同 bar 偷看。</li>
    <li>up-break：当前收盘 <code>&gt;</code> 前窗最高价；down-break：当前收盘 <code>&lt;</code> 前窗最低价。</li>
    <li><code>long_admission_only</code>：long setup 只有在最近 <code>{BREAK_LOOKBACK}</code> 根内出现过压缩后的 up-break 才放行；short 保持 baseline。</li>
    <li><code>short_veto_or_halfsize</code>：在 long admission 基础上，若 short setup 最近 <code>{BREAK_LOOKBACK}</code> 根内出现过压缩后的 down-break，则只给 <code>0.5x</code>；否则维持 <code>1.0x</code>。</li>
  </ul>
</div>
<div class='card'>
  <h2>Overall summary</h2>
  {render_table(overall, percent_cols={'mean_total_return','positive_asset_ratio','trade_count_retention','mean_position_size_mult','mean_early_fail_4bars'})}
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
    <li><code>reports/artifacts/scout_rank90_close_range_compression_15m/overall_summary.csv</code></li>
    <li><code>reports/artifacts/scout_rank90_close_range_compression_15m/setup_summary.csv</code></li>
    <li><code>reports/artifacts/scout_rank90_close_range_compression_15m/asset_summary.csv</code></li>
    <li><code>reports/artifacts/scout_rank90_close_range_compression_15m/trade_samples.csv</code></li>
    <li><code>reports/artifacts/scout_rank90_close_range_compression_15m/meta.csv</code></li>
  </ul>
</div>
"""
    write_html(SITE_DIR / "report.html", "Rank 90 close-range compression clean replication", body)
    write_html(READING_PATH, "Rank 90 close-range compression clean replication", body)


if __name__ == "__main__":
    main()
