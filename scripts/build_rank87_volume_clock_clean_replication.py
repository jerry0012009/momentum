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
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank87_volume_clock_cs_spread_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank87_volume_clock_cs_spread_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank87_volume_clock_cs_spread_clean_replication.html"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
SETUPS = ["ema_psar_long", "fib_retest_long", "breakout_short"]
VARIANTS = ["baseline", "fixed_clock_gate", "volume_clock_gate"]
PRIMARY_VARIANT = "volume_clock_gate"
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0]
HOLD_BARS = 8
EARLY_FAIL_BARS = 4
ROLL_30M_BARS = 48  # 24h on 30m bars
GATE_NEAR_MINUTES = 120
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


def cs_spread_proxy(high: pd.Series, low: pd.Series) -> pd.Series:
    hl = np.log((high / low).clip(lower=1 + EPS))
    beta = hl.pow(2) + hl.shift(1).pow(2)
    gamma = np.log((pd.concat([high, high.shift(1)], axis=1).max(axis=1) /
                    pd.concat([low, low.shift(1)], axis=1).min(axis=1)).clip(lower=1 + EPS)).pow(2)
    denom = 3 - 2 * math.sqrt(2)
    alpha = ((math.sqrt(2) - 1) * np.sqrt(beta.clip(lower=0))) / denom - np.sqrt(gamma.clip(lower=0) / denom)
    alpha = alpha.clip(lower=0)
    spread = 2 * (np.exp(alpha) - 1) / (1 + np.exp(alpha))
    return spread.replace([np.inf, -np.inf], np.nan)


def build_gate_frame(df15: pd.DataFrame) -> pd.DataFrame:
    bars30 = (
        df15.set_index("timestamp")[["open", "high", "low", "close", "volume"]]
        .resample("30min", label="right", closed="right")
        .agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
        .dropna()
        .reset_index()
    )
    bars30["impulse"] = bars30["close"] / bars30["open"] - 1.0
    bars30["cs_spread"] = cs_spread_proxy(bars30["high"], bars30["low"])
    spread_mean = bars30["cs_spread"].rolling(ROLL_30M_BARS, min_periods=12).mean()
    spread_std = bars30["cs_spread"].rolling(ROLL_30M_BARS, min_periods=12).std(ddof=0).replace(0, np.nan)
    bars30["spread_z"] = ((bars30["cs_spread"] - spread_mean) / spread_std).shift(1)
    bars30["calendar_anchor"] = bars30["timestamp"].dt.hour.isin([0, 8, 16]) & (bars30["timestamp"].dt.minute == 0)

    vol_rows = []
    fixed_rows = []
    for i, row in bars30.iterrows():
        hist = bars30.iloc[max(0, i - ROLL_30M_BARS + 1): i + 1]
        if hist.empty:
            vol_rows.append((pd.NaT, np.nan, np.nan))
        else:
            best = hist.loc[hist["volume"].idxmax()]
            vol_rows.append((best["timestamp"], best["impulse"], best["spread_z"]))
        fixed_hist = hist[hist["calendar_anchor"]]
        if fixed_hist.empty:
            fixed_rows.append((pd.NaT, np.nan, np.nan))
        else:
            best_fixed = fixed_hist.iloc[-1]
            fixed_rows.append((best_fixed["timestamp"], best_fixed["impulse"], best_fixed["spread_z"]))

    bars30[["volume_anchor_ts", "volume_anchor_impulse", "volume_anchor_spread_z"]] = pd.DataFrame(vol_rows, index=bars30.index)
    bars30[["fixed_anchor_ts", "fixed_anchor_impulse", "fixed_anchor_spread_z"]] = pd.DataFrame(fixed_rows, index=bars30.index)
    return bars30


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

    gate30 = build_gate_frame(df)
    gate_cols = [
        "timestamp",
        "volume_anchor_ts",
        "volume_anchor_impulse",
        "volume_anchor_spread_z",
        "fixed_anchor_ts",
        "fixed_anchor_impulse",
        "fixed_anchor_spread_z",
    ]
    gate30 = gate30[gate_cols].set_index("timestamp")
    # align each 15m bar to the latest completed 30m bar at or before timestamp
    align = gate30.reindex(df["timestamp"], method="ffill").reset_index(drop=False).rename(columns={"index": "timestamp"})
    df = pd.concat([df.reset_index(drop=True), align.drop(columns=["timestamp"])], axis=1)

    for prefix in ["volume", "fixed"]:
        ts_col = f"{prefix}_anchor_ts"
        diff_mins = (df["timestamp"] - pd.to_datetime(df[ts_col], utc=True)).dt.total_seconds() / 60.0
        df[f"{prefix}_anchor_near"] = diff_mins.between(0, GATE_NEAR_MINUTES, inclusive="both")
        df[f"{prefix}_long_support"] = (
            df[f"{prefix}_anchor_near"]
            & (df[f"{prefix}_anchor_impulse"] > 0)
            & (df[f"{prefix}_anchor_spread_z"] > 0)
        ).fillna(False)
        df[f"{prefix}_short_support"] = (
            df[f"{prefix}_anchor_near"]
            & (df[f"{prefix}_anchor_impulse"] < 0)
            & (df[f"{prefix}_anchor_spread_z"] > 0)
        ).fillna(False)
    return df


def gate_allows(row: pd.Series, setup: str, variant: str) -> bool:
    if variant == "baseline":
        return True
    direction = "long" if setup.endswith("long") else "short"
    prefix = "fixed" if variant == "fixed_clock_gate" else "volume"
    return bool(row.get(f"{prefix}_{direction}_support", False))


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

    for idx in range(60, len(frame) - HOLD_BARS - 2):
        if idx <= last_exit_idx:
            continue
        if not bool(signal_mask[idx]):
            continue
        signal_events += 1
        row = frame.iloc[idx]
        if not gate_allows(row, setup, variant):
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
                "early_fail_4bars": early_fail,
                "volume_anchor_ts": row.get("volume_anchor_ts"),
                "fixed_anchor_ts": row.get("fixed_anchor_ts"),
                "volume_anchor_impulse": row.get("volume_anchor_impulse"),
                "fixed_anchor_impulse": row.get("fixed_anchor_impulse"),
                "volume_anchor_spread_z": row.get("volume_anchor_spread_z"),
                "fixed_anchor_spread_z": row.get("fixed_anchor_spread_z"),
            }
        )
        last_exit_idx = exit_idx
    return pd.DataFrame(rows), signal_events


def summarize(trades: pd.DataFrame, signal_counts: dict[tuple[str, str], int]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    overall_rows = []
    setup_rows = []
    asset_rows = []

    for cost in COSTS:
        cost_rate = 2.0 * cost / 10000.0
        cost_df = trades.copy()
        if not cost_df.empty:
            cost_df["net_return"] = cost_df["gross_return"] - cost_rate
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
                        "early_fail_4bars": sub["early_fail_4bars"].mean() if not sub.empty else np.nan,
                    }
                )

    return pd.DataFrame(overall_rows), pd.DataFrame(setup_rows), pd.DataFrame(asset_rows)


def decide_verdict(overall: pd.DataFrame, setup_summary: pd.DataFrame) -> tuple[str, str]:
    primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps"] == PRIMARY_COST)].iloc[0]
    baseline = overall[(overall["variant"] == "baseline") & (overall["cost_bps"] == PRIMARY_COST)].iloc[0]
    fixed = overall[(overall["variant"] == "fixed_clock_gate") & (overall["cost_bps"] == PRIMARY_COST)].iloc[0]
    p_ret = float(primary["trade_count_retention"]) if pd.notna(primary["trade_count_retention"]) else 0.0
    p_ret_total = float(primary["mean_total_return"]) if pd.notna(primary["mean_total_return"]) else -999.0
    p_pos = float(primary["positive_asset_ratio"]) if pd.notna(primary["positive_asset_ratio"]) else 0.0
    p_fail = float(primary["mean_early_fail_4bars"]) if pd.notna(primary["mean_early_fail_4bars"]) else 1.0
    b_total = float(baseline["mean_total_return"]) if pd.notna(baseline["mean_total_return"]) else -999.0
    b_fail = float(baseline["mean_early_fail_4bars"]) if pd.notna(baseline["mean_early_fail_4bars"]) else 1.0
    f_total = float(fixed["mean_total_return"]) if pd.notna(fixed["mean_total_return"]) else -999.0

    best_setup = setup_summary[(setup_summary["variant"] == PRIMARY_VARIANT) & (setup_summary["cost_bps"] == PRIMARY_COST)]["mean_total_return"].max()
    if pd.isna(best_setup):
        return "park / evidence_pool", "volume-clock gate 几乎没有形成可交易样本，当前不配继续占 fast-lane 预算。"
    if p_ret_total > 0 and p_pos >= 2/3 and p_ret >= 0.35 and p_fail <= b_fail and p_ret_total >= max(b_total, f_total):
        return "keep_P1 / worth one Light Stability Pack check", "volume-clock 主臂在 6bps 下已转成正口袋、跨资产至少 2/3 为正，且相对 baseline / fixed-clock 都更诚实，值得再给 1 次真正会改 verdict 的稳定性检查。"
    if p_ret_total > b_total + 0.01 and p_ret >= 0.20 and (p_fail < b_fail or best_setup > 0):
        return "keep_P1 / mixed but not dead", "volume-clock gate 相比 baseline 有一定去亏损 / 去 early-fail 改善，但 retention 与跨资产一致性还不够，先保留在 P1 evidence_pool。"
    return "park / evidence_pool", "volume-clock gate 目前主要靠砍样本换少亏，跨资产与 retention 都不够诚实；不如 baseline / fixed-clock 的改善也不够稳，应该直接压回 park。"


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
    verdict, verdict_reason = decide_verdict(overall, setup_summary)
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
            "universe": "BTC/ETH/SOL 120d 15m local cache; 30m gate derived from 15m bars",
            "execution": "signal-bar-and-earlier only + next-bar open + no-overlap + hold 8 bars",
            "variants": "baseline / fixed_clock_gate / volume_clock_gate",
            "verdict": verdict,
            "verdict_reason": verdict_reason,
        }
    ])
    meta.to_csv(ART_DIR / "meta.csv", index=False)

    primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps"] == PRIMARY_COST)].iloc[0]
    baseline = overall[(overall["variant"] == "baseline") & (overall["cost_bps"] == PRIMARY_COST)].iloc[0]
    fixed = overall[(overall["variant"] == "fixed_clock_gate") & (overall["cost_bps"] == PRIMARY_COST)].iloc[0]

    body = f"""
<h1>Rank 87 / volume-clock + CS spread interaction gate</h1>
<p class='muted'>生成时间：{escape(generated_at)} | 口径：只复用本地 BTC/ETH/SOL 120d 15m cache，先把 15m 聚成 30m gate，再回写到 15m 执行；统一 <code>next-bar open + no-overlap + hold 8 bars</code>。</p>
<div class='card'>
  <h2>Hard verdict</h2>
  <p><strong>{escape(verdict)}</strong></p>
  <p>{escape(verdict_reason)}</p>
  <ul>
    <li>baseline @ 6bps：收益 {escape(pct(baseline['mean_total_return']))}，资产为正占比 {escape(pct(baseline['positive_asset_ratio']))}，retention {escape(pct(baseline['trade_count_retention']))}，4bar early-fail {escape(pct(baseline['mean_early_fail_4bars']))}</li>
    <li>fixed-clock @ 6bps：收益 {escape(pct(fixed['mean_total_return']))}，资产为正占比 {escape(pct(fixed['positive_asset_ratio']))}，retention {escape(pct(fixed['trade_count_retention']))}，4bar early-fail {escape(pct(fixed['mean_early_fail_4bars']))}</li>
    <li>volume-clock @ 6bps：收益 {escape(pct(primary['mean_total_return']))}，资产为正占比 {escape(pct(primary['positive_asset_ratio']))}，retention {escape(pct(primary['trade_count_retention']))}，4bar early-fail {escape(pct(primary['mean_early_fail_4bars']))}</li>
  </ul>
</div>
<div class='card'>
  <h2>这次最小 clean replication 怎么做</h2>
  <ul>
    <li>base setups：<code>ema_psar_long</code>、<code>fib_retest_long</code>、<code>breakout_short</code></li>
    <li>对照三臂：<code>baseline</code> / <code>fixed_clock_gate</code> / <code>volume_clock_gate</code></li>
    <li>fixed-clock：仅允许使用最近一个 <code>00 / 08 / 16 UTC</code> 的 30m anchor，且需要同向 impulse + 正向 spread z-score + 2h 内邻近</li>
    <li>volume-clock：改成最近 24h 成交量最大的 30m anchor，其余条件保持同样口径</li>
    <li>说明：由于本轮严格避免额外重下载，30m gate 来自 15m 本地 cache 聚合，不是假装完整分钟级 replication。</li>
  </ul>
</div>
<div class='card'>
  <h2>Overall summary</h2>
  {render_table(overall, percent_cols={'mean_total_return','positive_asset_ratio','trade_count_retention','mean_early_fail_4bars'})}
</div>
<div class='card'>
  <h2>Setup summary</h2>
  {render_table(setup_summary, percent_cols={'mean_total_return','positive_asset_ratio','trade_count_retention','mean_early_fail_4bars'})}
</div>
<div class='card'>
  <h2>Asset summary</h2>
  {render_table(asset_summary, percent_cols={'total_return','early_fail_4bars'})}
</div>
<div class='card'>
  <h2>Artifacts</h2>
  <ul>
    <li><code>reports/artifacts/scout_rank87_volume_clock_cs_spread_15m/overall_summary.csv</code></li>
    <li><code>reports/artifacts/scout_rank87_volume_clock_cs_spread_15m/setup_summary.csv</code></li>
    <li><code>reports/artifacts/scout_rank87_volume_clock_cs_spread_15m/asset_summary.csv</code></li>
    <li><code>reports/artifacts/scout_rank87_volume_clock_cs_spread_15m/trade_samples.csv</code></li>
  </ul>
</div>
"""
    write_html(SITE_DIR / "report.html", "Rank 87 volume-clock + CS spread clean replication", body)
    write_html(READING_PATH, "Rank 87 volume-clock + CS spread clean replication", body)


if __name__ == "__main__":
    main()
