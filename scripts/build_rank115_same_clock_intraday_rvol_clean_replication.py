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
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank115_same_clock_intraday_rvol_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank115_same_clock_intraday_rvol_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank115_same_clock_intraday_rvol_clean_replication.html"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
TRAIN_FRACTION = 0.60
HOLD_BARS = 8
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0]
LOOKBACK_CHOICES = [12, 20, 30]
SPIKE_CHOICES = [1.0, 1.2, 1.5]
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


def add_rvol_columns(df: pd.DataFrame, lookback: int) -> pd.DataFrame:
    out = df.copy()
    out["naive_avg_vol"] = out["volume"].shift(1).rolling(lookback, min_periods=lookback).mean()
    slot = out["timestamp"].dt.strftime("%H:%M")
    out["slot_avg_vol"] = (
        out.assign(slot=slot)
        .groupby("slot")["volume"]
        .transform(lambda s: s.shift(1).rolling(lookback, min_periods=lookback).mean())
    )
    out["naive_rvol"] = out["volume"] / out["naive_avg_vol"]
    out["slot_rvol"] = out["volume"] / out["slot_avg_vol"]
    return out


def build_frame(asset: str, symbol: str, lookback: int) -> pd.DataFrame:
    df = add_rvol_columns(load_bars(symbol, asset), lookback)
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


def collect_signals(frame: pd.DataFrame, asset: str, lookback: int, spike_thr: float) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    signal_idx = np.flatnonzero(frame["base_signal"].to_numpy())
    for idx in signal_idx:
        if idx + 2 >= len(frame):
            continue
        row = frame.iloc[idx]
        if not np.isfinite(row["atr14"]) or float(row["atr14"]) <= 0:
            continue
        rows.append(
            {
                "asset": asset,
                "lookback": lookback,
                "spike_thr": spike_thr,
                "signal_idx": int(idx),
                "signal_time": row["timestamp"],
                "signal_close": float(row["close"]),
                "fib_500": float(row["fib_500"]),
                "atr14": float(row["atr14"]),
                "naive_rvol": float(row["naive_rvol"]) if pd.notna(row["naive_rvol"]) else np.nan,
                "slot_rvol": float(row["slot_rvol"]) if pd.notna(row["slot_rvol"]) else np.nan,
                "naive_pass": bool(pd.notna(row["naive_rvol"]) and float(row["naive_rvol"]) >= spike_thr),
                "slot_pass": bool(pd.notna(row["slot_rvol"]) and float(row["slot_rvol"]) >= spike_thr),
            }
        )
    return pd.DataFrame(rows).sort_values(["asset", "signal_time"]).reset_index(drop=True)


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


def simulate_variant(frame: pd.DataFrame, signals: pd.DataFrame, variant: str, hold_bars: int = HOLD_BARS) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    last_exit_idx = -1
    pass_col = "naive_pass" if variant == "baseline_naive_rvol" else "slot_pass"
    for _, sig in signals.iterrows():
        idx = int(sig["signal_idx"])
        if idx <= last_exit_idx:
            continue
        if not bool(sig[pass_col]):
            rows.append({**sig.to_dict(), "variant": variant, "retention_flag": 0, "verdict": "veto"})
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
                "gate_conflict": int(bool(sig["naive_pass"]) != bool(sig["slot_pass"])),
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
                "gate_conflict_rate": float(asset_all["gate_conflict"].mean()) if "gate_conflict" in asset_all else np.nan,
                "win_rate": float((asset_entered["net_ret"] > 0).mean()) if not asset_entered.empty else np.nan,
                "mean_naive_rvol": float(asset_all["naive_rvol"].mean()) if asset_all["naive_rvol"].notna().any() else np.nan,
                "mean_slot_rvol": float(asset_all["slot_rvol"].mean()) if asset_all["slot_rvol"].notna().any() else np.nan,
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
                "mean_gate_conflict_rate": float(grp["gate_conflict_rate"].mean()),
                "mean_entries": float(grp["entries"].mean()),
                "mean_expectancy": float(grp["post_cost_expectancy"].mean()),
            }
        )
    return pd.DataFrame(rows).sort_values(["cost_bps_per_side", "mean_total_return", "mean_expectancy"], ascending=[True, False, False]).reset_index(drop=True)


def choose_plan(train_frames: dict[tuple[int, float], dict[str, pd.DataFrame]]) -> tuple[tuple[int, float], pd.DataFrame]:
    rows = []
    for (lookback, spike_thr), bundle in train_frames.items():
        train_asset = bundle["train_asset_summary"]
        overall = aggregate_variant(train_asset)
        base = overall[(overall["variant"] == "baseline_naive_rvol") & (overall["cost_bps_per_side"] == PRIMARY_COST)]
        slot = overall[(overall["variant"] == "same_clock_rvol") & (overall["cost_bps_per_side"] == PRIMARY_COST)]
        if base.empty or slot.empty:
            continue
        base = base.iloc[0]
        slot = slot.iloc[0]
        rows.append(
            {
                "lookback": lookback,
                "spike_thr": spike_thr,
                "baseline_mean_total_return": float(base["mean_total_return"]),
                "slot_mean_total_return": float(slot["mean_total_return"]),
                "uplift_total_return": float(slot["mean_total_return"] - base["mean_total_return"]),
                "slot_positive_asset_ratio": float(slot["positive_asset_ratio"]),
                "slot_mean_retention": float(slot["mean_retention"]),
                "slot_false_follow": float(slot["mean_false_follow_4bars"]),
                "base_false_follow": float(base["mean_false_follow_4bars"]),
                "slot_mean_expectancy": float(slot["mean_expectancy"]),
                "slot_mean_gate_conflict_rate": float(slot["mean_gate_conflict_rate"]),
            }
        )
    grid = pd.DataFrame(rows).sort_values(
        ["uplift_total_return", "slot_positive_asset_ratio", "slot_mean_expectancy", "slot_mean_retention"],
        ascending=[False, False, False, False],
    ).reset_index(drop=True)
    qualified = grid[
        grid["slot_mean_retention"].between(0.35, 0.95, inclusive="both")
        & (grid["slot_positive_asset_ratio"] >= (1 / 3))
    ]
    chosen = qualified.iloc[0] if not qualified.empty else grid.iloc[0]
    return (int(chosen["lookback"]), float(chosen["spike_thr"])), grid


def build_html(title: str, generated_at: str, verdict: str, summary_text: str, chosen_params: dict[str, object], overall_test: pd.DataFrame, asset_test: pd.DataFrame, train_grid: pd.DataFrame, disagreement_summary: pd.DataFrame) -> str:
    return f"""
<h1>{escape(title)}</h1>
<div class='card'>
  <p><strong>生成时间：</strong>{escape(generated_at)}</p>
  <p><strong>最小 clean replication 口径：</strong>固定 BTC/ETH/SOL 120d 15m 本地 cache；只挂 <code>fib_retest_long</code> 这 1 条 archetype；训练段冻结 <code>lookback</code> 与 <code>slot_spike</code>，测试段统一 <code>signal 当根及之前数据 + next-bar open + no-overlap + hold {HOLD_BARS} bars</code>。</p>
  <p><strong>当前 hard verdict：</strong><span class='{'good' if 'promote' in verdict else 'warn' if 'keep_P1' in verdict else 'bad'}'>{escape(verdict)}</span></p>
  <p>{escape(summary_text)}</p>
</div>
<div class='card'>
  <h2>冻结下来的唯一方案</h2>
  <ul>
    <li><strong>lookback</strong>: <code>{escape(str(chosen_params.get('lookback')))}</code></li>
    <li><strong>slot_spike threshold</strong>: <code>{escape(str(chosen_params.get('spike_thr')))}</code></li>
    <li><strong>比较两臂</strong>: <code>baseline_naive_rvol</code> vs <code>same_clock_rvol</code></li>
  </ul>
</div>
<div class='card'>
  <h2>测试段总表</h2>
  {render_table(overall_test, percent_cols={'mean_total_return','positive_asset_ratio','mean_retention','mean_false_follow_4bars','mean_gate_conflict_rate','mean_expectancy'}, digits_cols={'cost_bps_per_side':1,'mean_entries':2})}
</div>
<div class='card'>
  <h2>测试段分资产</h2>
  {render_table(asset_test, percent_cols={'retention','mean_total_return','post_cost_expectancy','false_follow_4bars_rate','gate_conflict_rate','win_rate'}, digits_cols={'cost_bps_per_side':1,'signals_total':0,'entries':0,'mean_naive_rvol':2,'mean_slot_rvol':2})}
</div>
<div class='card'>
  <h2>训练段冻结网格（6bps）</h2>
  {render_table(train_grid, percent_cols={'baseline_mean_total_return','slot_mean_total_return','uplift_total_return','slot_positive_asset_ratio','slot_mean_retention','slot_false_follow','base_false_follow','slot_mean_expectancy','slot_mean_gate_conflict_rate'}, digits_cols={'lookback':0,'spike_thr':2})}
</div>
<div class='card'>
  <h2>测试段 gate 分歧摘要（6bps）</h2>
  {render_table(disagreement_summary, percent_cols={'signal_share','naive_only_share','slot_only_share','both_pass_share','both_fail_share'}, digits_cols={'signals_total':0,'naive_only_count':0,'slot_only_count':0,'both_pass_count':0,'both_fail_count':0})}
</div>
<div class='card'>
  <h2>诚实边界</h2>
  <ul>
    <li><code>slot_rvol</code> 只允许用 signal 当根及之前、同 symbol、同 <code>HH:MM</code> 的历史已完成 bar 构造；没有足够历史就不判通过。</li>
    <li>本轮只把 volume gate 作为共享 confirmation 层；它不是独立 alpha，也不偷渡 repo 原始股票 breakout 参数。</li>
    <li>所有比较统一用 <code>next-bar open + no-overlap</code>，禁止同 bar 既判 gate 又按同 bar 成交。</li>
    <li>若 uplift 主要来自砍样本、而不是更好的 post-cost expectancy / false-follow 压降，就应直接 park。</li>
  </ul>
</div>
"""


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    train_frames: dict[tuple[int, float], dict[str, pd.DataFrame]] = {}
    for lookback in LOOKBACK_CHOICES:
        frames = {asset: build_frame(asset, symbol, lookback) for asset, symbol in ASSETS.items()}
        for spike_thr in SPIKE_CHOICES:
            signal_rows = pd.concat([collect_signals(frame, asset, lookback, spike_thr) for asset, frame in frames.items()], ignore_index=True)
            if signal_rows.empty:
                continue
            train_signals, test_signals = split_train_test(signal_rows)
            train_asset_parts = []
            test_asset_parts = []
            all_trades = []
            for asset, frame in frames.items():
                asset_train = train_signals[train_signals["asset"] == asset]
                asset_test = test_signals[test_signals["asset"] == asset]
                for variant in ["baseline_naive_rvol", "same_clock_rvol"]:
                    vt_train = simulate_variant(frame, asset_train, variant)
                    vt_test = simulate_variant(frame, asset_test, variant)
                    all_trades.extend([vt_train.assign(split="train"), vt_test.assign(split="test")])
                    for cost in COSTS:
                        train_asset_parts.append(summarize_variant(vt_train, variant, cost))
                        test_asset_parts.append(summarize_variant(vt_test, variant, cost))
            train_frames[(lookback, spike_thr)] = {
                "frames": frames,
                "signals": signal_rows,
                "train_signals": train_signals,
                "test_signals": test_signals,
                "train_asset_summary": pd.concat(train_asset_parts, ignore_index=True),
                "test_asset_summary": pd.concat(test_asset_parts, ignore_index=True),
                "all_trades": pd.concat(all_trades, ignore_index=True),
            }

    chosen_key, train_grid = choose_plan(train_frames)
    lookback, spike_thr = chosen_key
    chosen = train_frames[chosen_key]
    frames = chosen["frames"]
    signal_rows = chosen["signals"]
    test_signals = chosen["test_signals"]
    test_asset_summary = chosen["test_asset_summary"]
    all_trades = chosen["all_trades"]

    overall_test = aggregate_variant(test_asset_summary)
    focus_overall = overall_test[overall_test["cost_bps_per_side"] == PRIMARY_COST].copy().reset_index(drop=True)
    focus_asset = test_asset_summary[test_asset_summary["cost_bps_per_side"] == PRIMARY_COST].copy().reset_index(drop=True)

    base_6 = focus_overall[focus_overall["variant"] == "baseline_naive_rvol"].iloc[0]
    slot_6 = focus_overall[focus_overall["variant"] == "same_clock_rvol"].iloc[0]
    uplift = float(slot_6["mean_total_return"] - base_6["mean_total_return"])
    false_delta = float(base_6["mean_false_follow_4bars"] - slot_6["mean_false_follow_4bars"])
    retention = float(slot_6["mean_retention"])
    pos_ratio = float(slot_6["positive_asset_ratio"])

    if uplift > 0.0025 and false_delta > 0.05 and retention >= 0.55 and pos_ratio >= (2 / 3):
        verdict = "promote_to_P2 / paper candidate pool"
        summary_text = f"same-clock RVOL 在测试段 6bps 下相对 naive gate 取得约 {pct(uplift)} 的 desk 级 total-return 改善，同时 false-follow 压低约 {pct(false_delta)}，且 retention 仍有 {pct(retention)}，够资格升到 P2。"
    elif uplift > -0.0010 and false_delta > 0.03 and retention >= 0.45:
        verdict = "keep_P1 / honest measurement candidate"
        summary_text = f"same-clock RVOL 至少把 false-follow 压低约 {pct(false_delta)}，而收益没有显著恶化；它更像诚实 measurement upgrade，但 uplift 还不够硬，先留在 P1。"
    else:
        verdict = "park / evidence pool"
        summary_text = f"测试段 6bps 下，same-clock RVOL 相对 naive gate 的 total-return 改善约 {pct(uplift)}、retention {pct(retention)}、false-follow 改善约 {pct(false_delta)}；更像样本重排，不足以继续占 fast lane。"

    disagreement_rows = []
    for asset, grp in test_signals.groupby("asset", sort=True):
        total = len(grp)
        naive_only = int((grp["naive_pass"] & ~grp["slot_pass"]).sum())
        slot_only = int((grp["slot_pass"] & ~grp["naive_pass"]).sum())
        both_pass = int((grp["naive_pass"] & grp["slot_pass"]).sum())
        both_fail = int((~grp["naive_pass"] & ~grp["slot_pass"]).sum())
        disagreement_rows.append({
            "asset": asset,
            "signals_total": total,
            "naive_only_count": naive_only,
            "slot_only_count": slot_only,
            "both_pass_count": both_pass,
            "both_fail_count": both_fail,
            "signal_share": 1.0,
            "naive_only_share": naive_only / total if total else np.nan,
            "slot_only_share": slot_only / total if total else np.nan,
            "both_pass_share": both_pass / total if total else np.nan,
            "both_fail_share": both_fail / total if total else np.nan,
        })
    disagreement_summary = pd.DataFrame(disagreement_rows)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    title = "Rank 115 · same-clock intraday RVOL volume gate · minimal clean replication"
    html = build_html(title, generated_at, verdict, summary_text, {"lookback": lookback, "spike_thr": spike_thr}, focus_overall, focus_asset, train_grid, disagreement_summary)
    write_html(SITE_DIR / "report.html", title, html)

    reading_body = f"""
<h1>{escape(title)}</h1>
<div class='card'>
  <p><strong>一句话结论：</strong><span class='{'good' if 'promote' in verdict else 'warn' if 'keep_P1' in verdict else 'bad'}'>{escape(verdict)}</span></p>
  <p>{escape(summary_text)}</p>
  <p>这轮只问一件事：把 <code>fib_retest_long</code> 的 volume confirm 从 <code>rolling RVOL</code> 换成 <code>same-clock RVOL</code> 后，是不是更诚实。</p>
  <p><a href='../../factors/scout_rank115_same_clock_intraday_rvol_15m/report.html'>打开完整 report</a></p>
</div>
"""
    write_html(READING_PATH, title, reading_body)

    focus_overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    focus_asset.to_csv(ART_DIR / "asset_summary.csv", index=False)
    train_grid.to_csv(ART_DIR / "train_grid_summary.csv", index=False)
    disagreement_summary.to_csv(ART_DIR / "test_disagreement_summary.csv", index=False)
    all_trades.sort_values(["split", "variant", "asset", "signal_time"]).to_csv(ART_DIR / "trade_log.csv", index=False)
    signal_rows.to_csv(ART_DIR / "signal_catalog.csv", index=False)
    (ART_DIR / "summary.json").write_text(
        json.dumps(
            {
                "generated_at_utc": generated_at,
                "sample": "BTC/ETH/SOL 120d 15m",
                "base_archetype": "fib_retest_long",
                "train_fraction": TRAIN_FRACTION,
                "hold_bars": HOLD_BARS,
                "chosen_params": {"lookback": lookback, "spike_thr": spike_thr},
                "verdict": verdict,
                "summary_text": summary_text,
                "baseline_6bps": base_6.to_dict(),
                "same_clock_6bps": slot_6.to_dict(),
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
        "chosen_params": {"lookback": lookback, "spike_thr": spike_thr},
        "site_report": str(SITE_DIR / "report.html"),
        "reading_report": str(READING_PATH),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
