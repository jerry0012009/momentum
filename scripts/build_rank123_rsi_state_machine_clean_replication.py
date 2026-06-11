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
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank123_rsi_state_machine_admission_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank123_rsi_state_machine_admission_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank123_rsi_state_machine_admission_clean_replication.html"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
SETUPS = ["fib_retest_long", "ema_psar_long"]
TRAIN_FRACTION = 0.60
LOOKBACK = 8
HOLD_BARS = 8
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0]
FLOOR_CHOICES = [40.0, 45.0]
RECOVERY_CHOICES = [48.0, 50.0, 52.0]
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


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    up = delta.clip(lower=0.0)
    down = -delta.clip(upper=0.0)
    avg_up = up.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_down = down.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    rs = avg_up / avg_down.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


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
    df["swing_high_30"] = df["high"].rolling(30, min_periods=30).max().shift(1)
    df["swing_low_30"] = df["low"].rolling(30, min_periods=30).min().shift(1)
    swing_range = (df["swing_high_30"] - df["swing_low_30"]).clip(lower=EPS)
    df["fib_618"] = df["swing_high_30"] - 0.618 * swing_range
    df["fib_500"] = df["swing_high_30"] - 0.500 * swing_range
    df["rsi14"] = compute_rsi(df["close"], 14)
    df["rsi_min_8"] = df["rsi14"].rolling(LOOKBACK, min_periods=LOOKBACK).min()

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
    return df


def collect_signals(frame: pd.DataFrame, asset: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for setup in SETUPS:
        col = f"{setup}_signal"
        signal_idx = np.flatnonzero(frame[col].to_numpy())
        for idx in signal_idx:
            if idx + 2 >= len(frame):
                continue
            row = frame.iloc[idx]
            if not np.isfinite(row["rsi14"]) or not np.isfinite(row["rsi_min_8"]):
                continue
            fail_level = float(row["fib_500"]) if setup == "fib_retest_long" else float(row["ema15"])
            rows.append(
                {
                    "asset": asset,
                    "setup": setup,
                    "signal_idx": int(idx),
                    "signal_time": row["timestamp"],
                    "signal_close": float(row["close"]),
                    "signal_rsi": float(row["rsi14"]),
                    "recent_rsi_min": float(row["rsi_min_8"]),
                    "fail_level": fail_level,
                    "atr14": float(row["atr14"]) if pd.notna(row["atr14"]) else np.nan,
                }
            )
    return pd.DataFrame(rows).sort_values(["setup", "asset", "signal_time"]).reset_index(drop=True)


def split_train_test(signals: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_parts = []
    test_parts = []
    for (setup, asset), grp in signals.groupby(["setup", "asset"], sort=True):
        cut = max(1, int(len(grp) * TRAIN_FRACTION))
        train_parts.append(grp.iloc[:cut])
        test_parts.append(grp.iloc[cut:])
    train = pd.concat(train_parts, ignore_index=True) if train_parts else pd.DataFrame(columns=signals.columns)
    test = pd.concat(test_parts, ignore_index=True) if test_parts else pd.DataFrame(columns=signals.columns)
    return train, test


def apply_gate_flags(signals: pd.DataFrame, floor: float, recovery: float) -> pd.DataFrame:
    out = signals.copy()
    out["relaxed_pass"] = (out["recent_rsi_min"] <= floor) & (out["signal_rsi"] >= recovery)
    return out


def simulate_variant(frame: pd.DataFrame, signals: pd.DataFrame, variant: str, hold_bars: int = HOLD_BARS) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    last_exit_idx_by_setup = {setup: -1 for setup in SETUPS}
    pass_col = None if variant == "baseline" else "relaxed_pass"
    for _, sig in signals.iterrows():
        setup = str(sig["setup"])
        idx = int(sig["signal_idx"])
        if idx <= last_exit_idx_by_setup[setup]:
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
        early = frame.iloc[entry_idx:min(len(frame), entry_idx + 4)]
        window = frame.iloc[entry_idx:exit_idx + 1]
        actual_exit_idx = exit_idx
        exit_reason = "time_stop"
        fail_level = float(sig["fail_level"])
        for j in range(entry_idx, exit_idx + 1):
            if float(frame.iloc[j]["close"]) < fail_level:
                actual_exit_idx = j
                exit_reason = "fail_level_break"
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
                "exit_reason": exit_reason,
            }
        )
        last_exit_idx_by_setup[setup] = actual_exit_idx
    return pd.DataFrame(rows)


def summarize_variant(trades: pd.DataFrame, variant: str, cost_bps: float) -> pd.DataFrame:
    work = trades[trades["variant"] == variant].copy()
    if work.empty:
        return pd.DataFrame()
    entered = work[work["retention_flag"] == 1].copy()
    if not entered.empty:
        entered["net_ret"] = net_ret(entered["gross_ret"], cost_bps)
    signal_counts = work.groupby(["setup", "asset"]).size().rename("signals_total")
    rows = []
    for (setup, asset), total_signals in signal_counts.items():
        asset_all = work[(work["setup"] == setup) & (work["asset"] == asset)]
        asset_entered = entered[(entered["setup"] == setup) & (entered["asset"] == asset)]
        total_return = float((1.0 + asset_entered["net_ret"].dropna()).prod() - 1.0) if not asset_entered.empty else 0.0
        rows.append(
            {
                "setup": setup,
                "asset": asset,
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "signals_total": int(total_signals),
                "entries": int(asset_entered.shape[0]),
                "retention": float(asset_entered.shape[0] / total_signals) if total_signals else np.nan,
                "mean_total_return": total_return,
                "avg_trade_return": float(asset_entered["net_ret"].mean()) if not asset_entered.empty else np.nan,
                "false_follow_4bars": float(asset_entered["false_follow_4bars"].mean()) if not asset_entered.empty else np.nan,
                "avg_best_move": float(asset_entered["best_move"].mean()) if not asset_entered.empty else np.nan,
                "avg_mae": float(asset_entered["mae"].mean()) if not asset_entered.empty else np.nan,
            }
        )
    return pd.DataFrame(rows)


def aggregate_setup(asset_summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (setup, variant, cost_bps), grp in asset_summary.groupby(["setup", "variant", "cost_bps_per_side"], sort=False):
        rows.append(
            {
                "setup": setup,
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "mean_total_return": float(grp["mean_total_return"].mean()),
                "mean_avg_trade_return": float(grp["avg_trade_return"].mean()),
                "mean_retention": float(grp["retention"].mean()),
                "mean_false_follow_4bars": float(grp["false_follow_4bars"].mean()),
                "mean_entries": float(grp["entries"].mean()),
                "positive_asset_ratio": float((grp["mean_total_return"] > 0).mean()),
            }
        )
    return pd.DataFrame(rows)


def aggregate_overall(setup_summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (variant, cost_bps), grp in setup_summary.groupby(["variant", "cost_bps_per_side"], sort=False):
        rows.append(
            {
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "mean_total_return": float(grp["mean_total_return"].mean()),
                "mean_avg_trade_return": float(grp["mean_avg_trade_return"].mean()),
                "mean_retention": float(grp["mean_retention"].mean()),
                "mean_false_follow_4bars": float(grp["mean_false_follow_4bars"].mean()),
                "mean_entries": float(grp["mean_entries"].mean()),
                "positive_setup_ratio": float((grp["mean_total_return"] > 0).mean()),
            }
        )
    return pd.DataFrame(rows)


def choose_params(train_signals: pd.DataFrame, frames: dict[str, pd.DataFrame]) -> tuple[tuple[float, float], pd.DataFrame]:
    grid_rows = []
    for floor in FLOOR_CHOICES:
        for recovery in RECOVERY_CHOICES:
            if recovery <= floor:
                continue
            train = apply_gate_flags(train_signals, floor, recovery)
            trades = []
            for asset, frame in frames.items():
                asset_train = train[train["asset"] == asset]
                for variant in ["baseline", "relaxed_gate"]:
                    trades.append(simulate_variant(frame, asset_train, variant))
            trade_log = pd.concat(trades, ignore_index=True)
            asset_summary = pd.concat(
                [summarize_variant(trade_log, variant, PRIMARY_COST) for variant in ["baseline", "relaxed_gate"]],
                ignore_index=True,
            )
            setup_summary = aggregate_setup(asset_summary)
            base = aggregate_overall(setup_summary)
            baseline = base[base["variant"] == "baseline"].iloc[0]
            gate = base[base["variant"] == "relaxed_gate"].iloc[0]
            grid_rows.append(
                {
                    "floor": floor,
                    "recovery": recovery,
                    "baseline_mean_total_return": float(baseline["mean_total_return"]),
                    "gate_mean_total_return": float(gate["mean_total_return"]),
                    "uplift_total_return": float(gate["mean_total_return"] - baseline["mean_total_return"]),
                    "gate_mean_retention": float(gate["mean_retention"]),
                    "gate_false_follow": float(gate["mean_false_follow_4bars"]),
                    "baseline_false_follow": float(baseline["mean_false_follow_4bars"]),
                    "positive_setup_ratio": float(gate["positive_setup_ratio"]),
                    "gate_mean_entries": float(gate["mean_entries"]),
                }
            )
    grid = pd.DataFrame(grid_rows).sort_values(
        ["uplift_total_return", "positive_setup_ratio", "gate_mean_retention", "gate_mean_entries"],
        ascending=[False, False, False, False],
    ).reset_index(drop=True)
    qualified = grid[
        grid["gate_mean_retention"].between(0.05, 0.65, inclusive="both")
        & (grid["positive_setup_ratio"] >= 0.5)
    ]
    chosen = qualified.iloc[0] if not qualified.empty else grid.iloc[0]
    return (float(chosen["floor"]), float(chosen["recovery"])), grid


def gate_coverage(signals: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (split_name, setup, asset), grp in signals.groupby(["split", "setup", "asset"], sort=True):
        rows.append(
            {
                "split": split_name,
                "setup": setup,
                "asset": asset,
                "signals": int(len(grp)),
                "gate_pass_rate": float(grp["relaxed_pass"].mean()) if len(grp) else np.nan,
                "avg_signal_rsi": float(grp["signal_rsi"].mean()) if len(grp) else np.nan,
                "avg_recent_rsi_min": float(grp["recent_rsi_min"].mean()) if len(grp) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def verdict_from(primary_setup: pd.DataFrame, primary_overall: pd.DataFrame) -> tuple[str, str]:
    baseline = primary_overall[primary_overall["variant"] == "baseline"].iloc[0]
    gate = primary_overall[primary_overall["variant"] == "relaxed_gate"].iloc[0]
    uplift = float(gate["mean_total_return"] - baseline["mean_total_return"])
    ff_delta = float(baseline["mean_false_follow_4bars"] - gate["mean_false_follow_4bars"])
    retention = float(gate["mean_retention"])
    positive = float(gate["positive_setup_ratio"])

    fib_gate = primary_setup[(primary_setup["setup"] == "fib_retest_long") & (primary_setup["variant"] == "relaxed_gate")].iloc[0]
    ema_gate = primary_setup[(primary_setup["setup"] == "ema_psar_long") & (primary_setup["variant"] == "relaxed_gate")].iloc[0]
    fib_base = primary_setup[(primary_setup["setup"] == "fib_retest_long") & (primary_setup["variant"] == "baseline")].iloc[0]
    ema_base = primary_setup[(primary_setup["setup"] == "ema_psar_long") & (primary_setup["variant"] == "baseline")].iloc[0]

    fib_uplift = float(fib_gate["mean_total_return"] - fib_base["mean_total_return"])
    ema_uplift = float(ema_gate["mean_total_return"] - ema_base["mean_total_return"])

    if uplift > 0.004 and ff_delta > 0.03 and retention >= 0.10 and positive >= 0.5 and fib_uplift > 0 and ema_uplift >= -0.001:
        verdict = "promote_to_P2 / paper candidate"
        summary = (
            "relaxed RSI state-machine 在测试段至少把 long-side sparse admission 做成了更诚实的过滤："
            "总 desk 结果和 false-follow 都改善，且不是只剩极少数孤例。"
        )
    elif uplift > -0.0015 and ff_delta >= 0 and fib_uplift > 0:
        verdict = "keep_P1 / honest long-side sparse admission"
        summary = (
            "这轮 clean replication 支持它继续保留为 long-side sparse admission 候选："
            "Fib 侧有 uplift，但整体还不够硬，更像窄口径 overlay，而不是可升 P2 的 shared upgrade。"
        )
    else:
        verdict = "park / evidence pool"
        summary = (
            "这轮 clean replication 没把 RSI state-machine 变成更硬的 desk 级 long-side admission："
            "若有改善也主要更像缩样本后的外观变化，而不是稳定 post-cost uplift。"
        )
    return verdict, summary


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    frames = {asset: build_frame(asset, symbol) for asset, symbol in ASSETS.items()}
    signals = pd.concat([collect_signals(frame, asset) for asset, frame in frames.items()], ignore_index=True)
    signals = signals.sort_values(["setup", "asset", "signal_time"]).reset_index(drop=True)
    train_signals, test_signals = split_train_test(signals)

    chosen_params, train_grid = choose_params(train_signals, frames)
    floor, recovery = chosen_params
    train_signals = apply_gate_flags(train_signals, floor, recovery).assign(split="train")
    test_signals = apply_gate_flags(test_signals, floor, recovery).assign(split="test")
    all_signals = pd.concat([train_signals, test_signals], ignore_index=True)

    test_trade_logs = []
    for asset, frame in frames.items():
        asset_test = test_signals[test_signals["asset"] == asset]
        for variant in ["baseline", "relaxed_gate"]:
            test_trade_logs.append(simulate_variant(frame, asset_test, variant))
    trade_log = pd.concat(test_trade_logs, ignore_index=True)

    asset_summary = pd.concat(
        [summarize_variant(trade_log, variant, cost) for cost in COSTS for variant in ["baseline", "relaxed_gate"]],
        ignore_index=True,
    )
    setup_summary = aggregate_setup(asset_summary)
    overall_summary = aggregate_overall(setup_summary)
    coverage = gate_coverage(all_signals)

    primary_setup = setup_summary[setup_summary["cost_bps_per_side"] == PRIMARY_COST].copy().reset_index(drop=True)
    primary_overall = overall_summary[overall_summary["cost_bps_per_side"] == PRIMARY_COST].copy().reset_index(drop=True)
    verdict, verdict_summary = verdict_from(primary_setup, primary_overall)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    summary = {
        "generated_at_utc": generated_at,
        "rank": 123,
        "candidate": "RSI enter→exit→re-enter state-machine admission",
        "base_setups": SETUPS,
        "sample": "BTC/ETH/SOL 120d 15m local cache",
        "execution": "signal当根及之前数据 + next-bar open + no-overlap + hold 8 bars",
        "frozen_params": {"lookback": LOOKBACK, "floor": floor, "recovery": recovery},
        "verdict": verdict,
        "summary": verdict_summary,
    }

    all_signals.to_csv(ART_DIR / "signal_catalog.csv", index=False)
    trade_log.to_csv(ART_DIR / "trade_log.csv", index=False)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    setup_summary.to_csv(ART_DIR / "setup_summary.csv", index=False)
    overall_summary.to_csv(ART_DIR / "overall_summary.csv", index=False)
    train_grid.to_csv(ART_DIR / "train_grid_summary.csv", index=False)
    coverage.to_csv(ART_DIR / "gate_coverage.csv", index=False)
    (ART_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    body = f"""
    <h1>Rank 123 / RSI enter→exit→re-enter state-machine admission · 最小 clean replication</h1>
    <p class='muted'>生成时间：{escape(generated_at)}</p>

    <div class='card'>
      <h2>本轮 hard verdict</h2>
      <p><strong>{escape(verdict)}</strong></p>
      <p>{escape(verdict_summary)}</p>
      <ul>
        <li>只挂两条 long-side base setup：<code>fib_retest_long</code> + <code>ema_psar_long</code></li>
        <li>样本：<code>BTC/ETH/SOL 120d 15m</code></li>
        <li>执行：<code>signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars</code></li>
        <li>训练段冻结参数：<code>lookback={LOOKBACK}</code> / <code>recent RSI min&lt;={floor:.0f}</code> / <code>signal RSI&gt;={recovery:.0f}</code></li>
        <li>比较两臂：<code>baseline</code> vs <code>relaxed_rsi_state_gate</code></li>
      </ul>
    </div>

    <div class='card'>
      <h2>desk 级测试段摘要</h2>
      {render_table(primary_overall, percent_cols={'mean_total_return','mean_avg_trade_return','mean_retention','mean_false_follow_4bars','positive_setup_ratio'}, digits_cols={'cost_bps_per_side':1,'mean_entries':2})}
    </div>

    <div class='card'>
      <h2>按 setup 的测试段摘要（6 bps/side）</h2>
      {render_table(primary_setup[['setup','variant','mean_total_return','mean_avg_trade_return','mean_retention','mean_false_follow_4bars','mean_entries','positive_asset_ratio']], percent_cols={'mean_total_return','mean_avg_trade_return','mean_retention','mean_false_follow_4bars','positive_asset_ratio'}, digits_cols={'mean_entries':2})}
    </div>

    <div class='card'>
      <h2>分资产摘要（6 bps/side）</h2>
      {render_table(asset_summary[asset_summary['cost_bps_per_side'] == PRIMARY_COST][['setup','asset','variant','signals_total','entries','retention','mean_total_return','avg_trade_return','false_follow_4bars']], percent_cols={'retention','mean_total_return','avg_trade_return','false_follow_4bars'}, digits_cols={'signals_total':0,'entries':0})}
    </div>

    <div class='card'>
      <h2>训练段冻结网格</h2>
      {render_table(train_grid, percent_cols={'baseline_mean_total_return','gate_mean_total_return','uplift_total_return','gate_mean_retention','gate_false_follow','baseline_false_follow','positive_setup_ratio'}, digits_cols={'floor':0,'recovery':0,'gate_mean_entries':2})}
    </div>

    <div class='card'>
      <h2>gate coverage（train/test）</h2>
      {render_table(coverage, percent_cols={'gate_pass_rate'})}
    </div>

    <div class='card'>
      <h2>诚实边界</h2>
      <ul>
        <li>它只测 <strong>long-side sparse admission</strong>；不 shared 到 <code>breakout_short</code>，也不独立开仓。</li>
        <li>RSI 状态只允许用 <code>signal 当根及之前</code> 的已完成 15m bar 构造。</li>
        <li>门槛只在训练段冻结，再去测试段验证；禁止按全样本最好看的版本回填。</li>
        <li>若 uplift 主要来自 retention 掉太狠，而不是成本后收益 / false-follow 更诚实，就应 park。</li>
      </ul>
    </div>
    """
    write_html(SITE_DIR / "report.html", "Rank 123 RSI state machine clean replication", body)

    reading_body = f"""
    <h1>Rank 123 / RSI state-machine admission · clean replication note</h1>
    <div class='card'>
      <p><strong>一句话：</strong>{escape(verdict_summary)}</p>
      <p>这轮不再停在 source intake，而是把 relaxed RSI 状态机直接挂到 <code>fib_retest_long + ema_psar_long</code> 两条最小 long-side clean-room 上，只比较 <code>baseline</code> 与 <code>relaxed_rsi_state_gate</code>。</p>
      <p><a href='../../factors/scout_rank123_rsi_state_machine_admission_15m/report.html'>打开完整 report</a></p>
    </div>
    <div class='card'>
      <h2>6 bps/side 总结</h2>
      {render_table(primary_setup[['setup','variant','mean_total_return','mean_retention','mean_false_follow_4bars','mean_entries']], percent_cols={'mean_total_return','mean_retention','mean_false_follow_4bars'}, digits_cols={'mean_entries':2})}
    </div>
    """
    write_html(READING_PATH, "Rank 123 RSI state machine clean replication", reading_body)

    print(json.dumps({
        "generated_at_utc": generated_at,
        "verdict": verdict,
        "frozen_params": {"lookback": LOOKBACK, "floor": floor, "recovery": recovery},
        "site_report": str(SITE_DIR / 'report.html'),
        "reading_report": str(READING_PATH),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
