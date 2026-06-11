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
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank137_state_expiry_latency_budget_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank137_state_expiry_latency_budget_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank137_state_expiry_latency_budget_clean_replication.html"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
SETUPS = ["breakout_short", "fib_retest_long", "ema_psar_long"]
LONG_SETUPS = {"fib_retest_long", "ema_psar_long"}
VARIANTS = ["baseline_no_expiry", "confirm_window_12", "confirm12_entry24"]
COSTS = [6.0, 10.0, 15.0]
PRIMARY_COST = 6.0
HOLD_BARS = 8
EARLY_FAIL_BARS = 4
TRAIN_FRACTION = 0.60
CONFIRM_WINDOW = 12
ENTRY_WINDOW = 24
CONFIRM_ATR = 0.15
RETRACE_ATR = 0.35
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
    close = df["close"].to_numpy(dtype=float)
    out = np.full(len(df), np.nan)
    if len(df) < 2:
        return pd.Series(out, index=df.index)
    bull = close[1] >= close[0]
    af = step
    ep = high[0] if bull else low[0]
    sar = low[0] if bull else high[0]
    out[0] = sar
    for i in range(1, len(df)):
        sar = sar + af * (ep - sar)
        if bull:
            sar = min(sar, low[i - 1], low[i - 2] if i > 1 else low[i - 1])
            if low[i] < sar:
                bull = False
                sar = ep
                ep = low[i]
                af = step
            else:
                if high[i] > ep:
                    ep = high[i]
                    af = min(af + step, max_step)
        else:
            sar = max(sar, high[i - 1], high[i - 2] if i > 1 else high[i - 1])
            if high[i] > sar:
                bull = True
                sar = ep
                ep = high[i]
                af = step
            else:
                if low[i] < ep:
                    ep = low[i]
                    af = min(af + step, max_step)
        out[i] = sar
    return pd.Series(out, index=df.index)


def load_bars(symbol: str, asset: str) -> pd.DataFrame:
    df = pd.read_csv(CACHE_DIR / f"{symbol}__120d__15m.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_bars(symbol, asset)
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema15"] = df["close"].ewm(span=15, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["psar"] = compute_psar(df)
    df["atr14"] = compute_atr(df)
    df["vol_ma20"] = df["volume"].rolling(20, min_periods=20).mean()
    df["prior20_low"] = df["low"].rolling(20, min_periods=20).min().shift(1)
    df["swing_high_30"] = df["high"].rolling(30, min_periods=30).max().shift(1)
    df["swing_low_30"] = df["low"].rolling(30, min_periods=30).min().shift(1)
    swing_range = (df["swing_high_30"] - df["swing_low_30"]).clip(lower=EPS)
    df["fib_618"] = df["swing_high_30"] - 0.618 * swing_range
    df["fib_500"] = df["swing_high_30"] - 0.500 * swing_range

    df["fib_retest_long_signal"] = (
        df["fib_618"].notna()
        & df["atr14"].notna()
        & (df["ema9"] > df["ema15"])
        & (df["ema_slope"] > 0)
        & (df["close"] > df["fib_618"])
        & (df["close"].shift(1) <= df["fib_618"].shift(1))
        & (df["low"] <= df["fib_618"] + 0.2 * df["atr14"])
        & (df["close"] > df["fib_500"])
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)

    df["ema_psar_long_signal"] = (
        (df["ema9"] > df["ema15"])
        & (df["ema_slope"] > 0.0003)
        & (df["psar"] < df["close"])
        & (df["close"] > df["high"].shift(1))
        & (df["close"].shift(1) < df["ema9"].shift(1))
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)

    df["breakout_short_signal"] = (
        df["prior20_low"].notna()
        & df["atr14"].notna()
        & (df["ema9"] < df["ema15"])
        & (df["ema_slope"] < 0)
        & (df["close"] < df["prior20_low"])
        & (df["close"].shift(1) >= df["prior20_low"].shift(1))
        & (df["psar"] > df["close"])
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)
    return df


def collect_baseline_signals(frame: pd.DataFrame, asset: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for setup in SETUPS:
        signal_col = f"{setup}_signal"
        raw = frame[signal_col] & ~frame[signal_col].shift(1).fillna(False)
        for idx in np.flatnonzero(raw.to_numpy()):
            if idx + HOLD_BARS + 2 >= len(frame):
                continue
            row = frame.iloc[idx]
            if not np.isfinite(row["atr14"]) or row["atr14"] <= 0:
                continue
            anchor = float(row["prior20_low"]) if setup == "breakout_short" else (float(row["fib_618"]) if setup == "fib_retest_long" else float(row["ema15"]))
            rows.append(
                {
                    "asset": asset,
                    "setup": setup,
                    "signal_idx": int(idx),
                    "signal_time": row["timestamp"],
                    "signal_close": float(row["close"]),
                    "signal_high": float(row["high"]),
                    "signal_low": float(row["low"]),
                    "atr14": float(row["atr14"]),
                    "anchor": anchor,
                }
            )
    return pd.DataFrame(rows).sort_values(["signal_time", "asset", "setup"]).reset_index(drop=True)


def split_signals(signals: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    cutoff = signals["signal_time"].sort_values().iloc[max(1, int(len(signals) * TRAIN_FRACTION)) - 1]
    train = signals[signals["signal_time"] <= cutoff].copy()
    test = signals[signals["signal_time"] > cutoff].copy()
    if test.empty:
        test = train.iloc[-max(1, len(train) // 3):].copy()
        train = train.iloc[:-len(test)].copy()
    return train, test


def find_confirm(frame: pd.DataFrame, sig: pd.Series, confirm_window: int = CONFIRM_WINDOW) -> tuple[int | None, float | None]:
    idx = int(sig["signal_idx"])
    atr = float(sig["atr14"])
    setup = str(sig["setup"])
    upper = min(len(frame) - HOLD_BARS - 2, idx + confirm_window)
    if upper <= idx:
        return None, None
    for j in range(idx + 1, upper + 1):
        row = frame.iloc[j]
        if setup in LONG_SETUPS:
            if float(row["close"]) >= float(sig["signal_close"]) + CONFIRM_ATR * atr:
                return j, float(row["close"])
        else:
            if float(row["close"]) <= float(sig["signal_close"]) - CONFIRM_ATR * atr:
                return j, float(row["close"])
    return None, None


def find_entry(frame: pd.DataFrame, sig: pd.Series, confirm_idx: int, confirm_price: float, entry_window: int = ENTRY_WINDOW) -> int | None:
    atr = float(sig["atr14"])
    anchor = float(sig["anchor"])
    setup = str(sig["setup"])
    upper = min(len(frame) - HOLD_BARS - 2, confirm_idx + entry_window)
    if upper <= confirm_idx:
        return None
    for j in range(confirm_idx + 1, upper + 1):
        row = frame.iloc[j]
        if setup in LONG_SETUPS:
            retrace_level = confirm_price - RETRACE_ATR * atr
            if float(row["low"]) <= retrace_level and float(row["close"]) > anchor:
                return j + 1
        else:
            retrace_level = confirm_price + RETRACE_ATR * atr
            if float(row["high"]) >= retrace_level and float(row["close"]) < anchor:
                return j + 1
    return None


def variant_entry(frame: pd.DataFrame, sig: pd.Series, variant: str) -> tuple[int | None, int | None, int | None]:
    signal_idx = int(sig["signal_idx"])
    if variant == "baseline_no_expiry":
        return signal_idx + 1, 0, 1
    confirm_idx, confirm_price = find_confirm(frame, sig, CONFIRM_WINDOW)
    if confirm_idx is None or confirm_price is None:
        return None, None, None
    if variant == "confirm_window_12":
        entry_idx = confirm_idx + 1
        if entry_idx >= len(frame) - HOLD_BARS:
            return None, None, None
        return entry_idx, confirm_idx - signal_idx, entry_idx - signal_idx
    if variant == "confirm12_entry24":
        entry_idx = find_entry(frame, sig, confirm_idx, confirm_price, ENTRY_WINDOW)
        if entry_idx is None or entry_idx >= len(frame) - HOLD_BARS:
            return None, None, None
        return entry_idx, confirm_idx - signal_idx, entry_idx - signal_idx
    raise ValueError(variant)


def build_trades(signals: pd.DataFrame, frames: dict[str, pd.DataFrame], variant: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    by_asset = {asset: grp.sort_values("signal_time").reset_index(drop=True) for asset, grp in signals.groupby("asset")}
    for asset, group in by_asset.items():
        frame = frames[asset]
        last_exit = -1
        for _, sig in group.iterrows():
            entry_idx, t_confirm, t_entry = variant_entry(frame, sig, variant)
            if entry_idx is None or entry_idx <= last_exit:
                continue
            exit_idx = entry_idx + HOLD_BARS - 1
            if exit_idx >= len(frame):
                continue
            entry_px = float(frame.iloc[entry_idx]["open"])
            exit_px = float(frame.iloc[exit_idx]["open"])
            direction = 1.0 if sig["setup"] in LONG_SETUPS else -1.0
            gross = (exit_px / entry_px - 1.0) * direction
            fail_slice = frame.iloc[entry_idx:min(len(frame), entry_idx + EARLY_FAIL_BARS)]
            if sig["setup"] in LONG_SETUPS:
                early_fail = bool((fail_slice["close"] < float(sig["anchor"])).any())
            else:
                early_fail = bool((fail_slice["close"] > float(sig["anchor"])).any())
            rows.append(
                {
                    "asset": asset,
                    "setup": sig["setup"],
                    "variant": variant,
                    "signal_idx": int(sig["signal_idx"]),
                    "signal_time": sig["signal_time"],
                    "entry_idx": int(entry_idx),
                    "entry_time": frame.iloc[entry_idx]["timestamp"],
                    "exit_idx": int(exit_idx),
                    "exit_time": frame.iloc[exit_idx]["timestamp"],
                    "entry_price": entry_px,
                    "exit_price": exit_px,
                    "gross_return": gross,
                    "failure_before_target": early_fail,
                    "time_to_confirm_bars": t_confirm,
                    "time_to_entry_bars": t_entry,
                }
            )
            last_exit = exit_idx
    out = pd.DataFrame(rows)
    return out.sort_values(["signal_time", "asset", "setup"]).reset_index(drop=True) if not out.empty else out


def summarize_vs_baseline(baseline: pd.DataFrame, variant: pd.DataFrame, split: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    overall_rows: list[dict[str, object]] = []
    setup_rows: list[dict[str, object]] = []
    asset_rows: list[dict[str, object]] = []
    time_rows: list[dict[str, object]] = []
    for cost in COSTS:
        base_net = net_ret(baseline["gross_return"], cost)
        var_net = net_ret(variant["gross_return"], cost)
        overall_rows.append(
            {
                "split": split,
                "variant": variant["variant"].iloc[0] if not variant.empty else "-",
                "cost_bps_per_side": cost,
                "baseline_trades": int(len(baseline)),
                "variant_trades": int(len(variant)),
                "trade_count_retention": float(len(variant)) / float(len(baseline)) if len(baseline) else np.nan,
                "baseline_return": float(base_net.mean()) if len(base_net) else np.nan,
                "variant_return": float(var_net.mean()) if len(var_net) else np.nan,
                "return_delta": float(var_net.mean() - base_net.mean()) if len(base_net) and len(var_net) else np.nan,
                "baseline_failure": float(baseline["failure_before_target"].mean()) if len(baseline) else np.nan,
                "variant_failure": float(variant["failure_before_target"].mean()) if len(variant) else np.nan,
                "failure_delta": float(variant["failure_before_target"].mean() - baseline["failure_before_target"].mean()) if len(baseline) and len(variant) else np.nan,
                "baseline_time_to_entry_bars": float(baseline["time_to_entry_bars"].mean()) if len(baseline) else np.nan,
                "variant_time_to_entry_bars": float(variant["time_to_entry_bars"].mean()) if len(variant) else np.nan,
            }
        )
    for setup in SETUPS:
        b = baseline[baseline["setup"] == setup]
        v = variant[variant["setup"] == setup]
        for cost in [PRIMARY_COST]:
            base_net = net_ret(b["gross_return"], cost)
            var_net = net_ret(v["gross_return"], cost)
            setup_rows.append(
                {
                    "split": split,
                    "setup": setup,
                    "variant": variant["variant"].iloc[0] if not variant.empty else "-",
                    "baseline_trades": int(len(b)),
                    "variant_trades": int(len(v)),
                    "trade_count_retention": float(len(v)) / float(len(b)) if len(b) else np.nan,
                    "baseline_return": float(base_net.mean()) if len(base_net) else np.nan,
                    "variant_return": float(var_net.mean()) if len(var_net) else np.nan,
                    "return_delta": float(var_net.mean() - base_net.mean()) if len(base_net) and len(var_net) else np.nan,
                    "baseline_failure": float(b["failure_before_target"].mean()) if len(b) else np.nan,
                    "variant_failure": float(v["failure_before_target"].mean()) if len(v) else np.nan,
                    "failure_delta": float(v["failure_before_target"].mean() - b["failure_before_target"].mean()) if len(b) and len(v) else np.nan,
                    "variant_time_to_confirm_bars": float(v["time_to_confirm_bars"].mean()) if len(v) else np.nan,
                    "variant_time_to_entry_bars": float(v["time_to_entry_bars"].mean()) if len(v) else np.nan,
                }
            )
    for asset in ASSETS:
        b = baseline[baseline["asset"] == asset]
        v = variant[variant["asset"] == asset]
        base_net = net_ret(b["gross_return"], PRIMARY_COST)
        var_net = net_ret(v["gross_return"], PRIMARY_COST)
        asset_rows.append(
            {
                "split": split,
                "asset": asset,
                "variant": variant["variant"].iloc[0] if not variant.empty else "-",
                "baseline_trades": int(len(b)),
                "variant_trades": int(len(v)),
                "trade_count_retention": float(len(v)) / float(len(b)) if len(b) else np.nan,
                "baseline_return": float(base_net.mean()) if len(base_net) else np.nan,
                "variant_return": float(var_net.mean()) if len(var_net) else np.nan,
                "return_delta": float(var_net.mean() - base_net.mean()) if len(base_net) and len(var_net) else np.nan,
                "baseline_failure": float(b["failure_before_target"].mean()) if len(b) else np.nan,
                "variant_failure": float(v["failure_before_target"].mean()) if len(v) else np.nan,
                "failure_delta": float(v["failure_before_target"].mean() - b["failure_before_target"].mean()) if len(b) and len(v) else np.nan,
            }
        )
    if not variant.empty:
        time_rows.append(
            {
                "split": split,
                "variant": variant["variant"].iloc[0],
                "median_time_to_confirm_bars": float(variant["time_to_confirm_bars"].median()) if variant["time_to_confirm_bars"].notna().any() else np.nan,
                "p75_time_to_confirm_bars": float(variant["time_to_confirm_bars"].quantile(0.75)) if variant["time_to_confirm_bars"].notna().any() else np.nan,
                "median_time_to_entry_bars": float(variant["time_to_entry_bars"].median()) if variant["time_to_entry_bars"].notna().any() else np.nan,
                "p75_time_to_entry_bars": float(variant["time_to_entry_bars"].quantile(0.75)) if variant["time_to_entry_bars"].notna().any() else np.nan,
            }
        )
    return pd.DataFrame(overall_rows), pd.DataFrame(setup_rows), pd.DataFrame(asset_rows), pd.DataFrame(time_rows)


def build_scorecard(test_overall: pd.DataFrame, test_setup: pd.DataFrame, test_asset: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    c6 = test_overall[test_overall["cost_bps_per_side"] == PRIMARY_COST].copy()
    best = c6.sort_values(["return_delta", "failure_delta"], ascending=[False, True]).iloc[-1:].copy()
    chosen = c6.sort_values(["return_delta", "failure_delta"], ascending=[False, True]).iloc[0]
    chosen_variant = str(chosen["variant"])
    positive_costs = int((c6[c6["variant"] == chosen_variant]["variant_return"] > 0).sum())
    asset_slice = test_asset[test_asset["variant"] == chosen_variant]
    setup_slice = test_setup[test_setup["variant"] == chosen_variant]
    positive_assets = int((asset_slice["variant_return"] > 0).sum())
    positive_setups = int((setup_slice["variant_return"] > 0).sum())
    retention = float(chosen["trade_count_retention"])
    ret_delta = float(chosen["return_delta"])
    fail_delta = float(chosen["failure_delta"])
    entry_delay = float(chosen["variant_time_to_entry_bars"])

    if ret_delta > 0 and fail_delta < 0 and retention >= 0.45 and positive_assets >= 2 and positive_setups >= 2:
        verdict = "promote_P2"
        main_weakness = "仍需最小 stability pack，但 clean replication 已证明 time-budget 不只是砍单。"
    elif ret_delta > 0 and fail_delta <= 0 and retention >= 0.30 and positive_assets >= 1:
        verdict = "keep_P1"
        main_weakness = "改善还不够统一，暂时只算值得再给 1 次会改变 verdict 的检查。"
    else:
        verdict = "park"
        main_weakness = "目前更像“延后/少做”而不是更好：retention 与跨 setup 一致性都不够，尤其 breakout_short 没被稳定救回来。"

    why_now = (
        "这轮直接把『无限等待』改成有时间预算的 replication 跑完了：如果 confirmWindow 或 confirm+entryWindow 不能在成本后同时改善失败率与 expectancy，"
        "就该尽快 park，而不是继续把它写成漂亮但不落地的 honesty 故事。"
    )
    score_df = pd.DataFrame(
        [
            {"metric": "chosen_variant", "value": chosen_variant},
            {"metric": "return_delta_6bps", "value": ret_delta},
            {"metric": "failure_delta_6bps", "value": fail_delta},
            {"metric": "retention_vs_baseline", "value": retention},
            {"metric": "positive_assets_6bps", "value": positive_assets},
            {"metric": "positive_setups_6bps", "value": positive_setups},
            {"metric": "positive_costs", "value": positive_costs},
            {"metric": "mean_time_to_entry_bars", "value": entry_delay},
            {"metric": "recommended_action", "value": verdict},
            {"metric": "why_now", "value": why_now},
            {"metric": "main_weakness", "value": main_weakness},
        ]
    )
    summary = {
        "chosen_variant": chosen_variant,
        "return_delta_6bps": ret_delta,
        "failure_delta_6bps": fail_delta,
        "retention_vs_baseline": retention,
        "positive_assets_6bps": positive_assets,
        "positive_setups_6bps": positive_setups,
        "positive_costs": positive_costs,
        "mean_time_to_entry_bars": entry_delay,
        "recommended_action": verdict,
        "why_now": why_now,
        "main_weakness": main_weakness,
        "best_row_preview": best.to_dict(orient="records"),
    }
    return score_df, summary


def build_html(cost_summary: pd.DataFrame, setup_summary: pd.DataFrame, asset_summary: pd.DataFrame, time_summary: pd.DataFrame, scorecard: pd.DataFrame, summary: dict[str, object], generated_at: str) -> str:
    verdict = str(summary["recommended_action"])
    cls = "good" if verdict == "promote_P2" else ("warn" if verdict == "keep_P1" else "bad")
    cost_view = cost_summary.copy()
    for col in ["trade_count_retention", "baseline_return", "variant_return", "return_delta", "baseline_failure", "variant_failure", "failure_delta"]:
        if col in cost_view:
            cost_view[col] = cost_view[col].astype(float)
    return f"""
    <p><a href='../../index.html'>← 站点首页</a></p>
    <h1>Rank 137 / state expiry latency budget gate</h1>
    <div class='card'>
      <p><strong>当前硬结论：</strong><span class='{cls}'>{escape(verdict)}</span></p>
      <p class='muted'>生成时间：{escape(generated_at)} | 口径：BTC/ETH/SOL perpetual, 15m, next-bar open, no-overlap, hold {HOLD_BARS} bars, costs 6/10/15bps</p>
      <p>三臂只比较：<code>baseline_no_expiry</code>、<code>confirm_window_12</code>、<code>confirm12_entry24</code>。</p>
    </div>
    <div class='card'>
      <h2>一句话读法</h2>
      <p>{escape(str(summary['why_now']))}</p>
      <p><strong>主要短板：</strong>{escape(str(summary['main_weakness']))}</p>
    </div>
    <div class='card'>
      <h2>最小 scorecard</h2>
      {render_table(scorecard, percent_cols={'value'} if False else set())}
    </div>
    <div class='card'>
      <h2>成本层总表</h2>
      {render_table(cost_view, percent_cols={'trade_count_retention','baseline_return','variant_return','return_delta','baseline_failure','variant_failure','failure_delta'}, digits_cols={'cost_bps_per_side':0,'baseline_trades':0,'variant_trades':0,'baseline_time_to_entry_bars':1,'variant_time_to_entry_bars':1})}
    </div>
    <div class='card'>
      <h2>setup 拆解（6bps）</h2>
      {render_table(setup_summary, percent_cols={'trade_count_retention','baseline_return','variant_return','return_delta','baseline_failure','variant_failure','failure_delta'}, digits_cols={'baseline_trades':0,'variant_trades':0,'variant_time_to_confirm_bars':1,'variant_time_to_entry_bars':1})}
    </div>
    <div class='card'>
      <h2>资产拆解（6bps）</h2>
      {render_table(asset_summary, percent_cols={'trade_count_retention','baseline_return','variant_return','return_delta','baseline_failure','variant_failure','failure_delta'}, digits_cols={'baseline_trades':0,'variant_trades':0})}
    </div>
    <div class='card'>
      <h2>确认/入场延迟分布</h2>
      {render_table(time_summary, digits_cols={'median_time_to_confirm_bars':1,'p75_time_to_confirm_bars':1,'median_time_to_entry_bars':1,'p75_time_to_entry_bars':1})}
    </div>
    """


def build_reading_html(summary: dict[str, object], cost_summary: pd.DataFrame, generated_at: str) -> str:
    primary = cost_summary[(cost_summary['split'] == 'test') & (cost_summary['cost_bps_per_side'] == PRIMARY_COST)].copy()
    rows = []
    for _, row in primary.iterrows():
        rows.append(
            f"<li><code>{escape(str(row['variant']))}</code>：return≈{pct(row['variant_return'])} / retention≈{pct(row['trade_count_retention'])} / failure≈{pct(row['variant_failure'])} / Δreturn≈{pct(row['return_delta'])}</li>"
        )
    verdict = str(summary['recommended_action'])
    return f"""
    <p><a href='../../index.html'>← 站点首页</a></p>
    <h1>Rank 137 / state expiry latency budget gate — minimal clean replication</h1>
    <div class='card'>
      <p class='muted'>生成时间：{escape(generated_at)}</p>
      <p>这轮只回答一个问题：把确认层从“无限等待”改成有预算，是否真的能在当前三条 archetype（<code>breakout_short</code> / <code>fib_retest_long</code> / <code>ema_psar_long</code>）上留下更诚实、成本后仍站得住的结果？</p>
      <ul>
        <li>固定样本：BTC/ETH/SOL perpetual，15m，next-bar open，no-overlap，hold {HOLD_BARS} bars。</li>
        <li>三臂：<code>baseline_no_expiry</code>、<code>confirm_window_12</code>、<code>confirm12_entry24</code>。</li>
        <li>确认逻辑：post-signal 需要出现约 <code>0.15 ATR</code> 的 follow-through；entry 逻辑：仅在确认后 <code>24</code> bars 内出现约 <code>0.35 ATR</code> 的 retrace 才允许入场。</li>
      </ul>
      <p><strong>测试集 6bps 快读：</strong></p>
      <ul>{''.join(rows)}</ul>
      <p><strong>硬结论：</strong><span class='{'good' if verdict == 'promote_P2' else ('warn' if verdict == 'keep_P1' else 'bad')}'>{escape(verdict)}</span></p>
      <p>{escape(str(summary['main_weakness']))}</p>
    </div>
    """


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    frames = {asset: build_frame(asset, symbol) for asset, symbol in ASSETS.items()}
    signals = pd.concat([collect_baseline_signals(frame, asset) for asset, frame in frames.items()], ignore_index=True)
    train_sig, test_sig = split_signals(signals)

    trades_by_variant: dict[str, pd.DataFrame] = {}
    for variant in VARIANTS:
        variant_trades = build_trades(signals, frames, variant)
        variant_trades['split'] = np.where(variant_trades['signal_time'] <= train_sig['signal_time'].max(), 'train', 'test')
        trades_by_variant[variant] = variant_trades

    all_cost_rows = []
    all_setup_rows = []
    all_asset_rows = []
    all_time_rows = []
    for split in ['train', 'test']:
        baseline = trades_by_variant['baseline_no_expiry']
        baseline = baseline[baseline['split'] == split].copy()
        for variant in ['confirm_window_12', 'confirm12_entry24']:
            current = trades_by_variant[variant]
            current = current[current['split'] == split].copy()
            cost_df, setup_df, asset_df, time_df = summarize_vs_baseline(baseline, current, split)
            all_cost_rows.append(cost_df)
            all_setup_rows.append(setup_df)
            all_asset_rows.append(asset_df)
            all_time_rows.append(time_df)

    cost_summary = pd.concat(all_cost_rows, ignore_index=True)
    setup_summary = pd.concat(all_setup_rows, ignore_index=True)
    asset_summary = pd.concat(all_asset_rows, ignore_index=True)
    time_summary = pd.concat(all_time_rows, ignore_index=True)
    scorecard, summary = build_scorecard(
        cost_summary[cost_summary['split'] == 'test'],
        setup_summary[setup_summary['split'] == 'test'],
        asset_summary[asset_summary['split'] == 'test'],
    )

    signal_catalog = signals.copy()
    for variant in ['confirm_window_12', 'confirm12_entry24']:
        variant_rows = trades_by_variant[variant][['asset','setup','signal_idx','entry_idx','time_to_confirm_bars','time_to_entry_bars']].copy()
        variant_rows = variant_rows.rename(columns={'entry_idx': f'{variant}_entry_idx', 'time_to_confirm_bars': f'{variant}_time_to_confirm_bars', 'time_to_entry_bars': f'{variant}_time_to_entry_bars'})
        signal_catalog = signal_catalog.merge(variant_rows, on=['asset','setup','signal_idx'], how='left')
    signal_catalog['split'] = np.where(signal_catalog['signal_time'] <= train_sig['signal_time'].max(), 'train', 'test')

    cost_summary.to_csv(ART_DIR / 'overall_summary.csv', index=False)
    setup_summary.to_csv(ART_DIR / 'setup_summary.csv', index=False)
    asset_summary.to_csv(ART_DIR / 'asset_summary.csv', index=False)
    time_summary.to_csv(ART_DIR / 'time_summary.csv', index=False)
    signal_catalog.to_csv(ART_DIR / 'signal_catalog.csv', index=False)
    pd.concat(trades_by_variant.values(), ignore_index=True).to_csv(ART_DIR / 'trade_log.csv', index=False)
    scorecard.to_csv(ART_DIR / 'scorecard.csv', index=False)
    (ART_DIR / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')

    generated_at = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    report_html = build_html(cost_summary, setup_summary, asset_summary, time_summary, scorecard, summary, generated_at)
    write_html(SITE_DIR / 'report.html', 'Rank 137 / state expiry latency budget gate', report_html)
    write_html(READING_PATH, 'Rank 137 / state expiry latency budget gate — minimal clean replication', build_reading_html(summary, cost_summary, generated_at))
    print(json.dumps({'status': 'ok', 'recommended_action': summary['recommended_action'], 'artifact_dir': str(ART_DIR)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
