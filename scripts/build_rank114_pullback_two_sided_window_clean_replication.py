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
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank114_pullback_two_sided_window_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank114_pullback_two_sided_window_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank114_pullback_two_sided_window_clean_replication.html"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
TRAIN_FRACTION = 0.60
HOLD_BARS = 8
COSTS = [6.0, 10.0, 15.0]
PRIMARY_COST = 6.0
PULLBACK_BARS_CHOICES = [1, 2, 3]
WINDOW_BARS_CHOICES = [2, 4, 6]
OFFSET_ATR_CHOICES = [0.0, 0.10, 0.20]
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


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_bars(symbol, asset)
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema15"] = df["close"].ewm(span=15, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["vol_ma20"] = df["volume"].rolling(20, min_periods=20).mean()
    df["atr14"] = compute_atr(df)
    df["swing_high_30"] = df["high"].rolling(30, min_periods=30).max().shift(1)
    df["swing_low_30"] = df["low"].rolling(30, min_periods=30).min().shift(1)
    swing_range = (df["swing_high_30"] - df["swing_low_30"]).clip(lower=EPS)
    df["fib_618"] = df["swing_high_30"] - 0.618 * swing_range
    df["fib_500"] = df["swing_high_30"] - 0.500 * swing_range
    df["signal_distance_atr"] = ((df["close"] - df["fib_618"]) / df["atr14"]).replace([np.inf, -np.inf], np.nan)
    df["fib_retest_long_signal"] = (
        df["fib_618"].notna()
        & (df["ema9"] > df["ema15"])
        & (df["ema_slope"] > 0)
        & (df["close"] > df["fib_618"])
        & (df["close"].shift(1) <= df["fib_618"].shift(1))
        & (df["low"] <= df["fib_618"] + 0.2 * df["atr14"])
        & (df["close"] > df["fib_500"])
        & (df["volume"] > df["vol_ma20"])
        & df["signal_distance_atr"].notna()
    ).fillna(False)
    return df


def build_signal_rows(frame: pd.DataFrame, asset: str) -> pd.DataFrame:
    rows = []
    for idx in np.flatnonzero(frame["fib_retest_long_signal"].to_numpy()):
        if idx + 2 >= len(frame):
            continue
        row = frame.iloc[idx]
        if not np.isfinite(row["atr14"]) or float(row["atr14"]) <= 0:
            continue
        rows.append(
            {
                "asset": asset,
                "signal_idx": int(idx),
                "signal_time": row["timestamp"],
                "signal_close": float(row["close"]),
                "signal_low": float(row["low"]),
                "signal_high": float(row["high"]),
                "fib_500": float(row["fib_500"]),
                "atr14": float(row["atr14"]),
                "signal_distance_atr": float(row["signal_distance_atr"]),
            }
        )
    return pd.DataFrame(rows).sort_values(["asset", "signal_time"]).reset_index(drop=True)


def simulate_baseline(frame: pd.DataFrame, signals: pd.DataFrame, hold_bars: int = HOLD_BARS) -> pd.DataFrame:
    rows = []
    last_exit_idx = -1
    for _, sig in signals.iterrows():
        idx = int(sig["signal_idx"])
        if idx <= last_exit_idx:
            continue
        entry_idx = idx + 1
        if entry_idx >= len(frame):
            continue
        entry_px = float(frame.iloc[entry_idx]["open"])
        if not np.isfinite(entry_px) or entry_px <= 0:
            continue
        exit_idx = min(len(frame) - 1, entry_idx + hold_bars)
        window = frame.iloc[entry_idx : exit_idx + 1]
        early = frame.iloc[entry_idx : min(len(frame), entry_idx + 4)]
        actual_exit_idx = exit_idx
        exit_reason = "time_stop"
        for j in range(entry_idx, exit_idx + 1):
            if float(frame.iloc[j]["close"]) < float(sig["fib_500"]):
                actual_exit_idx = j
                exit_reason = "fib50_fail"
                break
        exit_px = float(frame.iloc[actual_exit_idx]["close"])
        gross = exit_px / entry_px - 1.0
        rows.append(
            {
                **sig.to_dict(),
                "variant": "baseline_direct_entry",
                "pullback_bars": 0,
                "window_bars": 0,
                "offset_atr": 0.0,
                "trigger_state": "baseline",
                "verdict": "entry",
                "retention_flag": 1,
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
                "exit_reason": exit_reason,
            }
        )
        last_exit_idx = actual_exit_idx
    return pd.DataFrame(rows)


def find_pullback_bar(frame: pd.DataFrame, signal_idx: int, max_pullback_bars: int) -> int | None:
    signal_close = float(frame.iloc[signal_idx]["close"])
    limit = min(len(frame) - 2, signal_idx + max_pullback_bars)
    chosen = None
    for j in range(signal_idx + 1, limit + 1):
        bar = frame.iloc[j]
        if float(bar["close"]) < float(bar["open"]) or float(bar["low"]) < signal_close:
            chosen = j
    return chosen


def simulate_window_variant(
    frame: pd.DataFrame,
    signals: pd.DataFrame,
    pullback_bars: int,
    window_bars: int,
    offset_atr: float,
    hold_bars: int = HOLD_BARS,
) -> pd.DataFrame:
    rows = []
    last_exit_idx = -1
    variant = f"window_pb{pullback_bars}_w{window_bars}_o{int(round(offset_atr*100)):02d}"
    for _, sig in signals.iterrows():
        idx = int(sig["signal_idx"])
        if idx <= last_exit_idx:
            continue
        pb_idx = find_pullback_bar(frame, idx, pullback_bars)
        if pb_idx is None:
            rows.append({**sig.to_dict(), "variant": variant, "pullback_bars": pullback_bars, "window_bars": window_bars, "offset_atr": offset_atr, "trigger_state": "no_pullback", "verdict": "skip", "retention_flag": 0})
            continue
        pb_bar = frame.iloc[pb_idx]
        success_edge = float(pb_bar["high"]) + offset_atr * float(sig["atr14"])
        failure_edge = float(pb_bar["low"]) - offset_atr * float(sig["atr14"])
        verdict = "timeout"
        success_idx = None
        fail_idx = None
        end_idx = min(len(frame) - 2, pb_idx + window_bars)
        for j in range(pb_idx + 1, end_idx + 1):
            bar = frame.iloc[j]
            if float(bar["low"]) <= failure_edge:
                verdict = "failure"
                fail_idx = j
                break
            if float(bar["high"]) >= success_edge:
                verdict = "success"
                success_idx = j
                break
        if verdict != "success":
            rows.append(
                {
                    **sig.to_dict(),
                    "variant": variant,
                    "pullback_bars": pullback_bars,
                    "window_bars": window_bars,
                    "offset_atr": offset_atr,
                    "trigger_state": "armed",
                    "verdict": verdict,
                    "retention_flag": 0,
                    "pullback_idx": pb_idx,
                    "pullback_time": pb_bar["timestamp"],
                    "success_edge": success_edge,
                    "failure_edge": failure_edge,
                    "blocked_idx": fail_idx if fail_idx is not None else end_idx,
                }
            )
            continue
        entry_idx = success_idx + 1
        if entry_idx >= len(frame):
            continue
        entry_px = float(frame.iloc[entry_idx]["open"])
        if not np.isfinite(entry_px) or entry_px <= 0:
            continue
        exit_idx = min(len(frame) - 1, entry_idx + hold_bars)
        window = frame.iloc[entry_idx : exit_idx + 1]
        early = frame.iloc[entry_idx : min(len(frame), entry_idx + 4)]
        actual_exit_idx = exit_idx
        exit_reason = "time_stop"
        for j in range(entry_idx, exit_idx + 1):
            if float(frame.iloc[j]["close"]) < float(sig["fib_500"]):
                actual_exit_idx = j
                exit_reason = "fib50_fail"
                break
        exit_px = float(frame.iloc[actual_exit_idx]["close"])
        gross = exit_px / entry_px - 1.0
        rows.append(
            {
                **sig.to_dict(),
                "variant": variant,
                "pullback_bars": pullback_bars,
                "window_bars": window_bars,
                "offset_atr": offset_atr,
                "trigger_state": "armed",
                "verdict": "entry",
                "retention_flag": 1,
                "pullback_idx": pb_idx,
                "pullback_time": pb_bar["timestamp"],
                "success_idx": success_idx,
                "success_time": frame.iloc[success_idx]["timestamp"],
                "success_edge": success_edge,
                "failure_edge": failure_edge,
                "entry_idx": entry_idx,
                "entry_time": frame.iloc[entry_idx]["timestamp"],
                "entry_price": entry_px,
                "exit_idx": actual_exit_idx,
                "exit_time": frame.iloc[actual_exit_idx]["timestamp"],
                "exit_price": exit_px,
                "gross_ret": gross,
                "false_follow_4bars": int((early["close"] < success_edge).any()) if len(early) else 0,
                "best_move": float(window["high"].max() / entry_px - 1.0) if len(window) else np.nan,
                "mae": float((window["low"] / entry_px - 1.0).min()) if len(window) else np.nan,
                "exit_reason": exit_reason,
            }
        )
        last_exit_idx = actual_exit_idx
    return pd.DataFrame(rows)


def summarize_variant(trades: pd.DataFrame, variant: str, cost_bps: float) -> pd.DataFrame:
    work = trades[trades["variant"] == variant].copy()
    if work.empty:
        return pd.DataFrame()
    work["net_ret"] = net_ret(work["gross_ret"], cost_bps) if "gross_ret" in work else np.nan
    signal_counts = work.groupby("asset").size().rename("signals_total")
    entered = work[work["retention_flag"] == 1].copy()
    rows = []
    for asset in signal_counts.index:
        asset_all = work[work["asset"] == asset]
        asset_entered = entered[entered["asset"] == asset]
        total_signals = int(signal_counts.loc[asset])
        total_return = float((1.0 + asset_entered["net_ret"].dropna()).prod() - 1.0) if not asset_entered.empty else 0.0
        rows.append(
            {
                "asset": asset,
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "signals_total": total_signals,
                "entries": int(len(asset_entered)),
                "retention": float(len(asset_entered) / total_signals) if total_signals else np.nan,
                "mean_total_return": total_return,
                "post_cost_expectancy": float(asset_entered["net_ret"].mean()) if not asset_entered.empty else np.nan,
                "false_follow_4bars_rate": float(asset_entered["false_follow_4bars"].mean()) if not asset_entered.empty else np.nan,
                "timeout_or_fail_rate": float((asset_all["retention_flag"] == 0).mean()) if len(asset_all) else np.nan,
                "win_rate": float((asset_entered["net_ret"] > 0).mean()) if not asset_entered.empty else np.nan,
                "mean_best_move": float(asset_entered["best_move"].mean()) if not asset_entered.empty else np.nan,
                "mean_mae": float(asset_entered["mae"].mean()) if not asset_entered.empty else np.nan,
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
                "mean_timeout_or_fail_rate": float(grp["timeout_or_fail_rate"].mean()),
                "mean_entries": float(grp["entries"].mean()),
                "mean_expectancy": float(grp["post_cost_expectancy"].mean()),
            }
        )
    return pd.DataFrame(rows).sort_values(["cost_bps_per_side", "mean_total_return", "mean_expectancy"], ascending=[True, False, False]).reset_index(drop=True)


def choose_plan(train_asset_summary: pd.DataFrame) -> tuple[str, pd.DataFrame]:
    train_overall = aggregate_variant(train_asset_summary)
    candidates = train_overall[train_overall["variant"] != "baseline_direct_entry"].copy()
    candidates = candidates[candidates["cost_bps_per_side"] == PRIMARY_COST].copy()
    if candidates.empty:
        return "baseline_direct_entry", train_overall
    qualified = candidates[
        candidates["mean_retention"].between(0.30, 0.90, inclusive="both")
        & (candidates["positive_asset_ratio"] >= (1 / 3))
        & (candidates["mean_timeout_or_fail_rate"] <= 0.70)
    ].copy()
    ranking = qualified if not qualified.empty else candidates
    ranking = ranking.sort_values(["mean_total_return", "mean_expectancy", "mean_false_follow_4bars", "mean_retention"], ascending=[False, False, True, False]).reset_index(drop=True)
    return str(ranking.iloc[0]["variant"]), train_overall


def split_train_test(signals: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_parts = []
    test_parts = []
    for asset, grp in signals.groupby("asset", sort=True):
        cut = max(1, int(len(grp) * TRAIN_FRACTION))
        train_parts.append(grp.iloc[:cut])
        test_parts.append(grp.iloc[cut:])
    train = pd.concat(train_parts, ignore_index=True) if train_parts else pd.DataFrame(columns=signals.columns)
    test = pd.concat(test_parts, ignore_index=True) if test_parts else pd.DataFrame(columns=signals.columns)
    return train, test


def build_html(title: str, generated_at: str, verdict: str, summary_text: str, overall_test: pd.DataFrame, asset_test: pd.DataFrame, train_grid: pd.DataFrame, chosen_variant: str, chosen_params: dict[str, object]) -> str:
    return f"""
<h1>{escape(title)}</h1>
<div class='card'>
  <p><strong>生成时间：</strong>{escape(generated_at)}</p>
  <p><strong>最小 clean replication 口径：</strong>固定 BTC/ETH/SOL 120d 15m 本地 cache；只挂 <code>fib_retest_long</code> 这 1 条 archetype；训练段冻结参数，测试段统一 <code>signal 当根及之前数据 + next-bar open + no-overlap + hold {HOLD_BARS} bars</code>。</p>
  <p><strong>当前 hard verdict：</strong><span class='{"good" if "keep_P1" in verdict else "bad" if "park" in verdict else "warn"}'>{escape(verdict)}</span></p>
  <p>{escape(summary_text)}</p>
</div>
<div class='card'>
  <h2>冻结下来的唯一方案</h2>
  <ul>
    <li><strong>chosen_variant</strong>: <code>{escape(chosen_variant)}</code></li>
    <li><strong>pullback_bars</strong>: <code>{escape(str(chosen_params.get('pullback_bars', '-')))}</code></li>
    <li><strong>window_bars</strong>: <code>{escape(str(chosen_params.get('window_bars', '-')))}</code></li>
    <li><strong>offset_atr</strong>: <code>{escape(str(chosen_params.get('offset_atr', '-')))}</code></li>
  </ul>
</div>
<div class='card'>
  <h2>测试段总表</h2>
  {render_table(overall_test, percent_cols={'mean_total_return','positive_asset_ratio','mean_retention','mean_false_follow_4bars','mean_timeout_or_fail_rate','mean_expectancy'}, digits_cols={'cost_bps_per_side':1,'mean_entries':2})}
</div>
<div class='card'>
  <h2>测试段分资产</h2>
  {render_table(asset_test, percent_cols={'retention','mean_total_return','post_cost_expectancy','false_follow_4bars_rate','timeout_or_fail_rate','win_rate','mean_best_move','mean_mae'}, digits_cols={'cost_bps_per_side':1,'signals_total':0,'entries':0})}
</div>
<div class='card'>
  <h2>训练段参数冻结网格（6bps）</h2>
  {render_table(train_grid[train_grid['cost_bps_per_side'] == {PRIMARY_COST}].copy(), percent_cols={'mean_total_return','positive_asset_ratio','mean_retention','mean_false_follow_4bars','mean_timeout_or_fail_rate','mean_expectancy'}, digits_cols={'cost_bps_per_side':1,'mean_entries':2})}
</div>
<div class='card'>
  <h2>诚实边界</h2>
  <ul>
    <li>只用 signal 当根及之前已知的 OHLC / ATR / rolling fib 位置来定义 <code>fib_retest_long</code>。</li>
    <li>pullback bar 只允许在 signal 后前 <code>1~3</code> 根里寻找，且必须是当时已发生的 counter bar；不能回看更远 future 重选。</li>
    <li>success / failure / timeout 三态是一级结果；测试段统一 next-bar open 执行，禁止同 bar 判定 + 同 bar 成交。</li>
    <li>本轮只回答 entry skeleton 值不值得留在 P1/P2 队列，不把它偷渡成独立 alpha。</li>
  </ul>
</div>
"""


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    frames = {asset: build_frame(asset, symbol) for asset, symbol in ASSETS.items()}
    signal_rows = pd.concat([build_signal_rows(frame, asset) for asset, frame in frames.items()], ignore_index=True)
    signal_rows = signal_rows.sort_values(["asset", "signal_time"]).reset_index(drop=True)
    train_signals, test_signals = split_train_test(signal_rows)

    all_variant_trades = []
    train_asset_parts = []
    test_asset_parts = []
    chosen_params = {"pullback_bars": None, "window_bars": None, "offset_atr": None}

    for asset, frame in frames.items():
        asset_train = train_signals[train_signals["asset"] == asset]
        asset_test = test_signals[test_signals["asset"] == asset]

        base_train = simulate_baseline(frame, asset_train)
        base_test = simulate_baseline(frame, asset_test)
        all_variant_trades.extend([base_train.assign(split="train"), base_test.assign(split="test")])
        for cost in COSTS:
            train_asset_parts.append(summarize_variant(base_train, "baseline_direct_entry", cost))
            test_asset_parts.append(summarize_variant(base_test, "baseline_direct_entry", cost))

        for pb in PULLBACK_BARS_CHOICES:
            for wb in WINDOW_BARS_CHOICES:
                for off in OFFSET_ATR_CHOICES:
                    variant = f"window_pb{pb}_w{wb}_o{int(round(off*100)):02d}"
                    vt_train = simulate_window_variant(frame, asset_train, pb, wb, off)
                    vt_test = simulate_window_variant(frame, asset_test, pb, wb, off)
                    all_variant_trades.extend([vt_train.assign(split="train"), vt_test.assign(split="test")])
                    for cost in COSTS:
                        train_asset_parts.append(summarize_variant(vt_train, variant, cost))
                        test_asset_parts.append(summarize_variant(vt_test, variant, cost))

    train_asset_summary = pd.concat(train_asset_parts, ignore_index=True)
    test_asset_summary = pd.concat(test_asset_parts, ignore_index=True)
    chosen_variant, train_grid = choose_plan(train_asset_summary)
    if chosen_variant != "baseline_direct_entry":
        pb_txt, wb_txt, off_txt = chosen_variant.split("_")[1:]
        chosen_params = {
            "pullback_bars": int(pb_txt.replace("pb", "")),
            "window_bars": int(wb_txt.replace("w", "")),
            "offset_atr": int(off_txt.replace("o", "")) / 100.0,
        }

    train_overall = aggregate_variant(train_asset_summary)
    test_overall = aggregate_variant(test_asset_summary)
    focus_variants = ["baseline_direct_entry", chosen_variant] if chosen_variant != "baseline_direct_entry" else ["baseline_direct_entry"]
    focus_test_overall = test_overall[test_overall["variant"].isin(focus_variants)].copy().reset_index(drop=True)
    focus_test_asset = test_asset_summary[test_asset_summary["variant"].isin(focus_variants)].copy().reset_index(drop=True)

    overall_6bps = focus_test_overall[focus_test_overall["cost_bps_per_side"] == PRIMARY_COST].copy()
    base_6 = overall_6bps[overall_6bps["variant"] == "baseline_direct_entry"].iloc[0]
    chosen_6 = overall_6bps[overall_6bps["variant"] == chosen_variant].iloc[0] if chosen_variant in set(overall_6bps["variant"]) else base_6

    if chosen_variant == "baseline_direct_entry":
        verdict = "park / evidence pool"
        summary_text = "训练段没有选出比 baseline 更诚实的窗口参数；这条 repo skeleton 在当前 fib_retest_long clean-room 下没有形成值得继续保留的 admission uplift。"
    else:
        uplift = float(chosen_6["mean_total_return"] - base_6["mean_total_return"])
        retention = float(chosen_6["mean_retention"])
        false_delta = float(base_6["mean_false_follow_4bars"] - chosen_6["mean_false_follow_4bars"])
        if uplift > 0.0025 and float(chosen_6["positive_asset_ratio"]) >= (2/3) and retention >= 0.45:
            verdict = "promote_to_P2 / paper candidate pool"
            summary_text = f"冻结后的窗口版本在测试段 6bps 下相对 baseline 取得约 {pct(uplift)} 的 desk 级 mean_total_return 改善，且 positive_asset_ratio / retention 仍过得去，值得从 P1 升到 P2。"
        elif uplift > -0.0025 and false_delta > 0.05 and retention >= 0.35:
            verdict = "keep_P1 / honest skeleton but not enough yet"
            summary_text = f"窗口版本主要贡献是把 false-follow-through 压低约 {pct(false_delta)}，但收益改善不够硬；先保留在 P1，当共享 entry skeleton 继续观察，不直接升 P2。"
        else:
            verdict = "park / evidence pool"
            summary_text = f"测试段 6bps 下，冻结后的窗口版相对 baseline 的 mean_total_return 改善只有 {pct(uplift)}，retention 约 {pct(retention)}；更像靠砍样本换平滑，不足以继续占默认 fast lane。"

    all_trades = pd.concat(all_variant_trades, ignore_index=True)
    all_trades["net_ret_6bps"] = net_ret(all_trades.get("gross_ret", pd.Series(dtype=float)), PRIMARY_COST)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    title = "Rank 114 · pullback → two-sided breakout window verdict · minimal clean replication"
    html = build_html(title, generated_at, verdict, summary_text, focus_test_overall, focus_test_asset, train_grid, chosen_variant, chosen_params)
    write_html(SITE_DIR / "report.html", title, html)
    write_html(READING_PATH, title, html)

    focus_test_overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    focus_test_asset.to_csv(ART_DIR / "asset_summary.csv", index=False)
    train_grid.to_csv(ART_DIR / "train_grid_summary.csv", index=False)
    all_trades.to_csv(ART_DIR / "trade_log.csv", index=False)
    signal_rows.to_csv(ART_DIR / "signal_catalog.csv", index=False)
    (ART_DIR / "summary.json").write_text(
        json.dumps(
            {
                "generated_at_utc": generated_at,
                "sample": "BTC/ETH/SOL 120d 15m",
                "base_archetype": "fib_retest_long",
                "train_fraction": TRAIN_FRACTION,
                "hold_bars": HOLD_BARS,
                "chosen_variant": chosen_variant,
                "chosen_params": chosen_params,
                "verdict": verdict,
                "summary_text": summary_text,
                "baseline_6bps": base_6.to_dict(),
                "chosen_6bps": chosen_6.to_dict(),
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
        "chosen_variant": chosen_variant,
        "chosen_params": chosen_params,
        "site_report": str(SITE_DIR / "report.html"),
        "reading_report": str(READING_PATH),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
