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
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank119_confirmed_swing_htf_long_context_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank119_confirmed_swing_htf_long_context_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank119_confirmed_swing_htf_long_context_clean_replication.html"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
TRAIN_FRACTION = 0.60
HOLD_BARS = 8
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0]
SWING_LOOKBACK = 5
MAX_AGE_15M_CHOICES = [8, 16, 24]
MAX_AGE_1H_CHOICES = [4, 8, 12]
EPS = 1e-12

CSS = """
body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width:1180px; margin:32px auto; padding:0 18px 48px; line-height:1.68; color:#111827; background:#f8fafc; }
h1,h2,h3 { color:#111827; }
.card { border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }
.muted { color:#6b7280; }
.good { color:#065f46; font-weight:600; }
.bad { color:#991b1b; font-weight:600; }
.warn { color:#92400e; font-weight:600; }
code { background:#f3f4f6; padding:1px 5px; border-radius:6px; }
table { width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; background:white; }
th, td { border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }
a { color:#2563eb; text-decoration:none; }
"""


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


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


def net_ret(gross: pd.Series | float, cost_bps: float) -> pd.Series | float:
    rate = float(cost_bps) / 10000.0
    return (1.0 + gross) * (1.0 - rate) * (1.0 - rate) - 1.0


def load_bars(symbol: str, asset: str) -> pd.DataFrame:
    df = pd.read_csv(CACHE_DIR / f"{symbol}__120d__15m.csv")
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


def build_base_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_bars(symbol, asset)
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema15"] = df["close"].ewm(span=15, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["atr14"] = compute_atr(df)
    df["swing_high_30"] = df["high"].rolling(30, min_periods=30).max().shift(1)
    df["swing_low_30"] = df["low"].rolling(30, min_periods=30).min().shift(1)
    swing_range = (df["swing_high_30"] - df["swing_low_30"]).clip(lower=EPS)
    df["fib_618"] = df["swing_high_30"] - 0.618 * swing_range
    df["fib_500"] = df["swing_high_30"] - 0.500 * swing_range
    df["base_signal"] = (
        df["fib_618"].notna()
        & df["atr14"].notna()
        & (df["ema9"] > df["ema15"])
        & (df["ema_slope"] > 0)
        & (df["close"] > df["fib_618"])
        & (df["close"].shift(1) <= df["fib_618"].shift(1))
        & (df["low"] <= df["fib_618"] + 0.2 * df["atr14"])
        & (df["close"] > df["fib_500"])
    ).fillna(False)
    return df


def apply_confirmed_structure(df: pd.DataFrame, lookback: int) -> pd.DataFrame:
    out = df.copy()
    n = int(lookback)
    out["pivot_low_candidate"] = (
        out["low"].rolling(2 * n + 1, center=True, min_periods=2 * n + 1).apply(lambda s: 1.0 if s.iloc[n] == s.min() else 0.0, raw=False)
    ).fillna(0.0)
    out["pivot_high_candidate"] = (
        out["high"].rolling(2 * n + 1, center=True, min_periods=2 * n + 1).apply(lambda s: 1.0 if s.iloc[n] == s.max() else 0.0, raw=False)
    ).fillna(0.0)

    out["confirmed_swing_low"] = np.where(out["pivot_low_candidate"] > 0.5, out["low"], np.nan)
    out["confirmed_swing_high"] = np.where(out["pivot_high_candidate"] > 0.5, out["high"], np.nan)
    out["confirmed_swing_low"] = out["confirmed_swing_low"].shift(n)
    out["confirmed_swing_high"] = out["confirmed_swing_high"].shift(n)
    out["confirmed_low_bar"] = np.where(out["confirmed_swing_low"].notna(), np.arange(len(out)), np.nan)
    out["confirmed_high_bar"] = np.where(out["confirmed_swing_high"].notna(), np.arange(len(out)), np.nan)

    out["last_low"] = out["confirmed_swing_low"].ffill()
    out["prev_low"] = out["confirmed_swing_low"].where(out["confirmed_swing_low"].notna()).ffill().shift(1)
    out["last_high"] = out["confirmed_swing_high"].ffill()
    out["prev_high"] = out["confirmed_swing_high"].where(out["confirmed_swing_high"].notna()).ffill().shift(1)

    out["last_low_bar"] = out["confirmed_low_bar"].ffill()
    out["last_high_bar"] = out["confirmed_high_bar"].ffill()
    bar_index = pd.Series(np.arange(len(out)), index=out.index)
    out["low_age"] = bar_index - out["last_low_bar"]
    out["high_age"] = bar_index - out["last_high_bar"]
    out["bullish_structure"] = (
        out["last_low"].notna()
        & out["prev_low"].notna()
        & out["last_high"].notna()
        & out["prev_high"].notna()
        & (out["last_low"] > out["prev_low"])
        & (out["last_high"] > out["prev_high"])
    )
    return out


def resample_to_1h(df15: pd.DataFrame) -> pd.DataFrame:
    out = (
        df15.set_index("timestamp")[["open", "high", "low", "close", "volume"]]
        .resample("1H", label="right", closed="right")
        .agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
        .dropna()
        .reset_index()
    )
    return out


def build_structured_frames(asset: str, symbol: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    base15 = build_base_frame(asset, symbol)
    struct15 = apply_confirmed_structure(base15[["timestamp", "open", "high", "low", "close", "volume"]], SWING_LOOKBACK)
    bars1h = resample_to_1h(base15)
    struct1h = apply_confirmed_structure(bars1h, SWING_LOOKBACK)
    htf_cols = struct1h[["timestamp", "bullish_structure", "low_age", "high_age", "last_low", "last_high"]].rename(
        columns={
            "bullish_structure": "htf_bullish_structure",
            "low_age": "htf_low_age",
            "high_age": "htf_high_age",
            "last_low": "htf_last_low",
            "last_high": "htf_last_high",
        }
    )
    merged = pd.merge_asof(base15.sort_values("timestamp"), htf_cols.sort_values("timestamp"), on="timestamp", direction="backward")
    merged = merged.merge(
        struct15[["timestamp", "bullish_structure", "low_age", "high_age", "last_low", "last_high"]].rename(
            columns={
                "bullish_structure": "ltf_bullish_structure",
                "low_age": "ltf_low_age",
                "high_age": "ltf_high_age",
                "last_low": "ltf_last_low",
                "last_high": "ltf_last_high",
            }
        ),
        on="timestamp",
        how="left",
    )
    return merged, struct15, struct1h


def collect_signals(frame: pd.DataFrame, asset: str, max_age_15m: int, max_age_1h: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    signal_idx = np.flatnonzero(frame["base_signal"].to_numpy())
    for idx in signal_idx:
        if idx + 2 >= len(frame):
            continue
        row = frame.iloc[idx]
        if not np.isfinite(row["atr14"]) or float(row["atr14"]) <= 0:
            continue
        ltf_ok = bool(
            row["ltf_bullish_structure"]
            and pd.notna(row["ltf_low_age"])
            and pd.notna(row["ltf_high_age"])
            and float(row["ltf_low_age"]) <= max_age_15m
            and float(row["ltf_high_age"]) <= max_age_15m
        )
        htf_ok = bool(
            row.get("htf_bullish_structure", False)
            and pd.notna(row.get("htf_low_age"))
            and pd.notna(row.get("htf_high_age"))
            and float(row["htf_low_age"]) <= max_age_1h
            and float(row["htf_high_age"]) <= max_age_1h
        )
        rows.append(
            {
                "asset": asset,
                "max_age_15m": max_age_15m,
                "max_age_1h": max_age_1h,
                "signal_idx": int(idx),
                "signal_time": row["timestamp"],
                "signal_close": float(row["close"]),
                "fib_500": float(row["fib_500"]),
                "fib_618": float(row["fib_618"]),
                "atr14": float(row["atr14"]),
                "ltf_low_age": float(row["ltf_low_age"]) if pd.notna(row["ltf_low_age"]) else np.nan,
                "ltf_high_age": float(row["ltf_high_age"]) if pd.notna(row["ltf_high_age"]) else np.nan,
                "htf_low_age": float(row["htf_low_age"]) if pd.notna(row["htf_low_age"]) else np.nan,
                "htf_high_age": float(row["htf_high_age"]) if pd.notna(row["htf_high_age"]) else np.nan,
                "ltf_bullish_structure": bool(row["ltf_bullish_structure"]),
                "htf_bullish_structure": bool(row.get("htf_bullish_structure", False)),
                "long_context_only_pass": bool(ltf_ok and htf_ok),
            }
        )
    return pd.DataFrame(rows).sort_values(["asset", "signal_time"]).reset_index(drop=True)


def split_train_test(signals: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_parts = []
    test_parts = []
    for _, grp in signals.groupby("asset", sort=True):
        cut = max(1, int(len(grp) * TRAIN_FRACTION))
        train_parts.append(grp.iloc[:cut])
        test_parts.append(grp.iloc[cut:])
    train = pd.concat(train_parts, ignore_index=True) if train_parts else pd.DataFrame(columns=signals.columns)
    test = pd.concat(test_parts, ignore_index=True) if test_parts else pd.DataFrame(columns=signals.columns)
    return train, test


def simulate_variant(frame: pd.DataFrame, signals: pd.DataFrame, variant: str, hold_bars: int = HOLD_BARS) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    last_exit_idx = -1
    pass_col = None if variant == "baseline" else "long_context_only_pass"
    for _, sig in signals.iterrows():
        idx = int(sig["signal_idx"])
        if idx <= last_exit_idx:
            continue
        if pass_col and not bool(sig[pass_col]):
            rows.append({**sig.to_dict(), "variant": variant, "retention_flag": 0, "verdict": "veto"})
            continue
        entry_idx = idx + 1
        if entry_idx >= len(frame):
            continue
        entry_px = float(frame.iloc[entry_idx]["open"])
        if not np.isfinite(entry_px) or entry_px <= 0:
            continue
        exit_idx = min(len(frame) - 1, entry_idx + hold_bars)
        window = frame.iloc[entry_idx: exit_idx + 1]
        early = frame.iloc[entry_idx: min(len(frame), entry_idx + 4)]
        actual_exit_idx = exit_idx
        exit_reason = "time_stop"
        fail_level = float(sig["fib_500"])
        for j in range(entry_idx, exit_idx + 1):
            if float(frame.iloc[j]["close"]) < fail_level:
                actual_exit_idx = j
                exit_reason = "fib50_fail"
                break
        exit_px = float(frame.iloc[actual_exit_idx]["close"])
        gross = exit_px / entry_px - 1.0
        rows.append(
            {
                **sig.to_dict(),
                "variant": variant,
                "retention_flag": 1,
                "verdict": "entry",
                "entry_idx": entry_idx,
                "entry_time": frame.iloc[entry_idx]["timestamp"],
                "entry_price": entry_px,
                "exit_idx": actual_exit_idx,
                "exit_time": frame.iloc[actual_exit_idx]["timestamp"],
                "exit_price": exit_px,
                "gross_ret": gross,
                "false_follow_4bars": int((early["close"] < float(sig["signal_close"])).any()) if len(early) else 0,
                "best_move": float(window["high"].max() / entry_px - 1.0) if len(window) else np.nan,
                "mae": float((window["low"] / entry_px - 1.0).min()) if len(window) else np.nan,
                "context_conflict": int(bool(sig["long_context_only_pass"]) is False),
                "exit_reason": exit_reason,
            }
        )
        last_exit_idx = actual_exit_idx
    return pd.DataFrame(rows)


def summarize_variant(trades: pd.DataFrame, variant: str, cost_bps: float) -> pd.DataFrame:
    work = trades[trades["variant"] == variant].copy()
    if work.empty:
        return pd.DataFrame()
    signal_counts = work.groupby("asset").size().rename("signals_total")
    entered = work[work["retention_flag"] == 1].copy()
    rows = []
    for asset in signal_counts.index:
        asset_all = work[work["asset"] == asset]
        asset_entered = entered[entered["asset"] == asset]
        total_signals = int(signal_counts.loc[asset])
        net = net_ret(asset_entered["gross_ret"], cost_bps) if not asset_entered.empty else pd.Series(dtype=float)
        total_return = float((1.0 + net).prod() - 1.0) if len(net) else 0.0
        rows.append(
            {
                "asset": asset,
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "signals_total": total_signals,
                "entries": int(len(asset_entered)),
                "retention": float(len(asset_entered) / total_signals) if total_signals else np.nan,
                "mean_total_return": total_return,
                "post_cost_expectancy": float(net.mean()) if len(net) else np.nan,
                "false_follow_4bars_rate": float(asset_entered["false_follow_4bars"].mean()) if not asset_entered.empty else np.nan,
                "context_conflict_rate": float(asset_all["context_conflict"].mean()) if "context_conflict" in asset_all else np.nan,
                "win_rate": float((net > 0).mean()) if len(net) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def aggregate_variant(asset_summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (variant, cost_bps), grp in asset_summary.groupby(["variant", "cost_bps_per_side"], dropna=False):
        rows.append(
            {
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "mean_total_return": float(grp["mean_total_return"].mean()),
                "positive_asset_ratio": float((grp["mean_total_return"] > 0).mean()),
                "mean_retention": float(grp["retention"].mean()),
                "mean_false_follow_4bars": float(grp["false_follow_4bars_rate"].mean()),
                "mean_context_conflict_rate": float(grp["context_conflict_rate"].mean()),
                "mean_entries": float(grp["entries"].mean()),
                "mean_expectancy": float(grp["post_cost_expectancy"].mean()),
            }
        )
    return pd.DataFrame(rows).sort_values(["cost_bps_per_side", "mean_total_return", "mean_expectancy"], ascending=[True, False, False]).reset_index(drop=True)


def choose_plan(train_frames: dict[tuple[int, int], dict[str, pd.DataFrame]]) -> tuple[tuple[int, int], pd.DataFrame]:
    rows = []
    for (max_age_15m, max_age_1h), bundle in train_frames.items():
        overall = aggregate_variant(bundle["train_asset_summary"])
        base = overall[(overall["variant"] == "baseline") & (overall["cost_bps_per_side"] == PRIMARY_COST)]
        ctx = overall[(overall["variant"] == "long_context_only") & (overall["cost_bps_per_side"] == PRIMARY_COST)]
        if base.empty or ctx.empty:
            continue
        base = base.iloc[0]
        ctx = ctx.iloc[0]
        rows.append(
            {
                "max_age_15m": max_age_15m,
                "max_age_1h": max_age_1h,
                "baseline_mean_total_return": float(base["mean_total_return"]),
                "context_mean_total_return": float(ctx["mean_total_return"]),
                "uplift_total_return": float(ctx["mean_total_return"] - base["mean_total_return"]),
                "context_positive_asset_ratio": float(ctx["positive_asset_ratio"]),
                "context_mean_retention": float(ctx["mean_retention"]),
                "context_false_follow": float(ctx["mean_false_follow_4bars"]),
                "base_false_follow": float(base["mean_false_follow_4bars"]),
                "context_mean_expectancy": float(ctx["mean_expectancy"]),
            }
        )
    grid = pd.DataFrame(rows).sort_values(
        ["uplift_total_return", "context_positive_asset_ratio", "context_mean_expectancy", "context_mean_retention"],
        ascending=[False, False, False, False],
    ).reset_index(drop=True)
    qualified = grid[
        grid["context_mean_retention"].between(0.35, 0.95, inclusive="both")
        & (grid["context_positive_asset_ratio"] >= (1 / 3))
    ]
    chosen = qualified.iloc[0] if not qualified.empty else grid.iloc[0]
    return (int(chosen["max_age_15m"]), int(chosen["max_age_1h"])), grid


def build_html(title: str, generated_at: str, verdict: str, summary_text: str, chosen_params: dict[str, object], overall_test: pd.DataFrame, asset_test: pd.DataFrame, train_grid: pd.DataFrame, disagreement_summary: pd.DataFrame) -> str:
    verdict_class = "good" if "promote" in verdict else "warn" if "keep_P1" in verdict else "bad"
    return f"""
<h1>{escape(title)}</h1>
<div class='card'>
  <p><strong>生成时间：</strong>{escape(generated_at)}</p>
  <p><strong>最小 clean replication 口径：</strong>固定 BTC/ETH/SOL 120d 15m 本地 cache；只挂 <code>fib_retest_long</code> 这 1 条 archetype；15m/1h 结构都按 <code>confirmed swing</code> 实现，再用 <code>merge_asof(backward)</code> 把已收盘 1h 结构并回 15m；测试段统一 <code>signal 当根及之前数据 + next-bar open + no-overlap + hold {HOLD_BARS} bars</code>。</p>
  <p><strong>当前 hard verdict：</strong><span class='{verdict_class}'>{escape(verdict)}</span></p>
  <p>{escape(summary_text)}</p>
</div>
<div class='card'>
  <h2>冻结下来的唯一方案</h2>
  <ul>
    <li><strong>swing lookback</strong>: <code>{SWING_LOOKBACK}</code></li>
    <li><strong>15m structure max age</strong>: <code>{escape(str(chosen_params.get('max_age_15m')))}</code></li>
    <li><strong>1h structure max age</strong>: <code>{escape(str(chosen_params.get('max_age_1h')))}</code></li>
    <li><strong>比较两臂</strong>: <code>baseline</code> vs <code>long_context_only</code></li>
  </ul>
</div>
<div class='card'>
  <h2>测试段总表</h2>
  {render_table(overall_test, percent_cols={'mean_total_return','positive_asset_ratio','mean_retention','mean_false_follow_4bars','mean_context_conflict_rate','mean_expectancy'}, digits_cols={'cost_bps_per_side':1,'mean_entries':2})}
</div>
<div class='card'>
  <h2>测试段分资产</h2>
  {render_table(asset_test, percent_cols={'retention','mean_total_return','post_cost_expectancy','false_follow_4bars_rate','context_conflict_rate','win_rate'}, digits_cols={'cost_bps_per_side':1,'signals_total':0,'entries':0})}
</div>
<div class='card'>
  <h2>训练段冻结网格（6bps）</h2>
  {render_table(train_grid, percent_cols={'baseline_mean_total_return','context_mean_total_return','uplift_total_return','context_positive_asset_ratio','context_mean_retention','context_false_follow','base_false_follow','context_mean_expectancy'}, digits_cols={'max_age_15m':0,'max_age_1h':0})}
</div>
<div class='card'>
  <h2>测试段 context 分歧摘要</h2>
  {render_table(disagreement_summary, percent_cols={'signal_share','context_pass_share','baseline_only_share','both_entry_share','context_veto_share'}, digits_cols={'signals_total':0,'context_pass_count':0,'baseline_only_count':0,'both_entry_count':0,'context_veto_count':0})}
</div>
<div class='card'>
  <h2>诚实边界</h2>
  <ul>
    <li><code>confirmed swing</code> 必须等确认后才可用，不能把还未确认的局部高低点倒灌给当前信号。</li>
    <li>1h 结构只能来自已收盘 1h bar，并用 <code>merge_asof(backward)</code> 并回 15m。</li>
    <li>这条线只测 <strong>Fib / EMA 的 long-side context</strong>；不允许外推成 breakout-short 的 shared short gate，更不是独立 alpha。</li>
    <li>若 uplift 主要来自砍样本、而不是更好的 post-cost expectancy / false-follow 压降，就应直接 park。</li>
  </ul>
</div>
"""


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    structured_frames = {asset: build_structured_frames(asset, symbol)[0] for asset, symbol in ASSETS.items()}
    train_frames: dict[tuple[int, int], dict[str, pd.DataFrame]] = {}

    for max_age_15m in MAX_AGE_15M_CHOICES:
        for max_age_1h in MAX_AGE_1H_CHOICES:
            signal_rows = pd.concat(
                [collect_signals(frame, asset, max_age_15m, max_age_1h) for asset, frame in structured_frames.items()],
                ignore_index=True,
            )
            if signal_rows.empty:
                continue
            train_signals, test_signals = split_train_test(signal_rows)
            train_asset_parts = []
            test_asset_parts = []
            all_trades = []
            for asset, frame in structured_frames.items():
                asset_train = train_signals[train_signals["asset"] == asset]
                asset_test = test_signals[test_signals["asset"] == asset]
                for variant in ["baseline", "long_context_only"]:
                    vt_train = simulate_variant(frame, asset_train, variant)
                    vt_test = simulate_variant(frame, asset_test, variant)
                    all_trades.extend([vt_train.assign(split="train"), vt_test.assign(split="test")])
                    for cost in COSTS:
                        train_asset_parts.append(summarize_variant(vt_train, variant, cost))
                        test_asset_parts.append(summarize_variant(vt_test, variant, cost))
            train_frames[(max_age_15m, max_age_1h)] = {
                "signals": signal_rows,
                "train_signals": train_signals,
                "test_signals": test_signals,
                "train_asset_summary": pd.concat(train_asset_parts, ignore_index=True),
                "test_asset_summary": pd.concat(test_asset_parts, ignore_index=True),
                "all_trades": pd.concat(all_trades, ignore_index=True),
            }

    chosen_key, train_grid = choose_plan(train_frames)
    max_age_15m, max_age_1h = chosen_key
    chosen = train_frames[chosen_key]
    signal_rows = chosen["signals"]
    test_signals = chosen["test_signals"]
    test_asset_summary = chosen["test_asset_summary"]
    all_trades = chosen["all_trades"]

    overall_test = aggregate_variant(test_asset_summary)
    focus_overall = overall_test[overall_test["cost_bps_per_side"] == PRIMARY_COST].copy().reset_index(drop=True)
    focus_asset = test_asset_summary[test_asset_summary["cost_bps_per_side"] == PRIMARY_COST].copy().reset_index(drop=True)

    base_6 = focus_overall[focus_overall["variant"] == "baseline"].iloc[0]
    ctx_6 = focus_overall[focus_overall["variant"] == "long_context_only"].iloc[0]
    uplift = float(ctx_6["mean_total_return"] - base_6["mean_total_return"])
    false_delta = float(base_6["mean_false_follow_4bars"] - ctx_6["mean_false_follow_4bars"])
    retention = float(ctx_6["mean_retention"])
    pos_ratio = float(ctx_6["positive_asset_ratio"])

    if uplift > 0.003 and false_delta > 0.05 and retention >= 0.55 and pos_ratio >= (2 / 3):
        verdict = "promote_to_P2 / paper candidate pool"
        summary_text = f"long-side context 在测试段 6bps 下相对 baseline 取得约 {pct(uplift)} 的 desk 级 total-return 改善，同时 false-follow 压低约 {pct(false_delta)}，且 retention 仍有 {pct(retention)}，够资格升到 P2。"
    elif uplift > -0.001 and false_delta > 0.03 and retention >= 0.45:
        verdict = "keep_P1 / honest long-context candidate"
        summary_text = f"confirmed swing + HTF 至少把 false-follow 压低约 {pct(false_delta)}，而收益没有明显恶化；它更像诚实 long-side context，但 uplift 还不够硬，先留在 P1。"
    else:
        verdict = "park / evidence pool"
        summary_text = f"测试段 6bps 下，long-side context 相对 baseline 的 total-return 改善约 {pct(uplift)}、retention {pct(retention)}、false-follow 改善约 {pct(false_delta)}；更像样本重排，不足以继续占 fast lane。"

    disagreement_rows = []
    for asset, grp in test_signals.groupby("asset", sort=True):
        total = len(grp)
        context_pass = int(grp["long_context_only_pass"].sum())
        context_veto = total - context_pass
        disagreement_rows.append(
            {
                "asset": asset,
                "signals_total": total,
                "context_pass_count": context_pass,
                "baseline_only_count": context_veto,
                "both_entry_count": context_pass,
                "context_veto_count": context_veto,
                "signal_share": 1.0,
                "context_pass_share": context_pass / total if total else np.nan,
                "baseline_only_share": context_veto / total if total else np.nan,
                "both_entry_share": context_pass / total if total else np.nan,
                "context_veto_share": context_veto / total if total else np.nan,
            }
        )
    disagreement_summary = pd.DataFrame(disagreement_rows)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    title = "Rank 119 · confirmed swing + HTF alignment long-side context · minimal clean replication"
    html = build_html(
        title,
        generated_at,
        verdict,
        summary_text,
        {"max_age_15m": max_age_15m, "max_age_1h": max_age_1h},
        focus_overall,
        focus_asset,
        train_grid,
        disagreement_summary,
    )
    write_html(SITE_DIR / "report.html", title, html)

    reading_body = f"""
<h1>{escape(title)}</h1>
<div class='card'>
  <p><strong>一句话结论：</strong><span class='{'good' if 'promote' in verdict else 'warn' if 'keep_P1' in verdict else 'bad'}'>{escape(verdict)}</span></p>
  <p>{escape(summary_text)}</p>
  <p>这轮只问一件事：把 <code>confirmed swing + backward-merged 1h structure</code> 当成 <code>fib_retest_long</code> 的 long-side context 后，是不是比 baseline 更诚实。</p>
  <p><a href='../../factors/scout_rank119_confirmed_swing_htf_long_context_15m/report.html'>打开完整 report</a></p>
</div>
"""
    write_html(READING_PATH, title, reading_body)

    focus_overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    focus_asset.to_csv(ART_DIR / "asset_summary.csv", index=False)
    train_grid.to_csv(ART_DIR / "train_grid_summary.csv", index=False)
    disagreement_summary.to_csv(ART_DIR / "test_context_summary.csv", index=False)
    all_trades.sort_values(["split", "variant", "asset", "signal_time"]).to_csv(ART_DIR / "trade_log.csv", index=False)
    signal_rows.to_csv(ART_DIR / "signal_catalog.csv", index=False)
    (ART_DIR / "summary.json").write_text(
        json.dumps(
            {
                "generated_at_utc": generated_at,
                "sample": "BTC/ETH/SOL 120d 15m + backward-merged 1h",
                "base_archetype": "fib_retest_long",
                "train_fraction": TRAIN_FRACTION,
                "hold_bars": HOLD_BARS,
                "swing_lookback": SWING_LOOKBACK,
                "chosen_params": {"max_age_15m": max_age_15m, "max_age_1h": max_age_1h},
                "verdict": verdict,
                "summary_text": summary_text,
                "baseline_6bps": base_6.to_dict(),
                "long_context_6bps": ctx_6.to_dict(),
            },
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    print(json.dumps({
        "generated_at_utc": generated_at,
        "verdict": verdict,
        "chosen_params": {"max_age_15m": max_age_15m, "max_age_1h": max_age_1h},
        "site_report": str(SITE_DIR / "report.html"),
        "reading_report": str(READING_PATH),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
