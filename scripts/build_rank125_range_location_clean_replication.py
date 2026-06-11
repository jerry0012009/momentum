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
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank125_range_location_veto_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank125_range_location_veto_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank125_range_location_veto_clean_replication.html"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
SETUPS = ["fib_retest_long", "ema_psar_long", "breakout_short"]
N_CHOICES = [8, 20, 32]
SHORT_THRESH_CHOICES = [0.10, 0.15, 0.20]
LONG_THRESH_CHOICES = [0.35, 0.40, 0.45]
TRAIN_FRACTION = 0.60
HOLD_BARS = 8
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0]
ATR_PERIOD = 14
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


def compute_atr(df: pd.DataFrame, period: int = ATR_PERIOD) -> pd.Series:
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
    df["prior20_high"] = df["high"].rolling(20, min_periods=20).max().shift(1)
    df["prior20_low"] = df["low"].rolling(20, min_periods=20).min().shift(1)
    df["swing_high_30"] = df["high"].rolling(30, min_periods=30).max().shift(1)
    df["swing_low_30"] = df["low"].rolling(30, min_periods=30).min().shift(1)
    swing_range = (df["swing_high_30"] - df["swing_low_30"]).clip(lower=EPS)
    df["fib_618"] = df["swing_high_30"] - 0.618 * swing_range
    df["fib_500"] = df["swing_high_30"] - 0.500 * swing_range
    for n in N_CHOICES:
        roll_high = df["high"].rolling(n, min_periods=n).max()
        roll_low = df["low"].rolling(n, min_periods=n).min()
        df[f"rl_{n}"] = (df["close"] - roll_low) / (roll_high - roll_low + EPS)

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


def collect_signals(frame: pd.DataFrame, asset: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for setup in SETUPS:
        for idx in np.flatnonzero(frame[f"{setup}_signal"].to_numpy()):
            if idx + HOLD_BARS + 1 >= len(frame):
                continue
            row = frame.iloc[idx]
            if not np.isfinite(row["atr14"]) or row["atr14"] <= 0:
                continue
            rec = {
                "asset": asset,
                "setup": setup,
                "signal_idx": int(idx),
                "signal_time": row["timestamp"],
                "atr14": float(row["atr14"]),
                "close": float(row["close"]),
            }
            for n in N_CHOICES:
                v = row[f"rl_{n}"]
                rec[f"rl_{n}"] = float(v) if np.isfinite(v) else np.nan
            rows.append(rec)
    out = pd.DataFrame(rows)
    return out.sort_values(["setup", "asset", "signal_time"]).reset_index(drop=True)


def gate_pass(sig: pd.Series, n: int, short_thr: float, long_thr: float) -> bool:
    rl = sig[f"rl_{n}"]
    if pd.isna(rl):
        return False
    if sig["setup"] == "breakout_short":
        return rl > short_thr
    return rl >= long_thr


def simulate_variant(frame: pd.DataFrame, signals: pd.DataFrame, variant: str, n: int | None = None, short_thr: float | None = None, long_thr: float | None = None) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    last_exit_by_setup = {setup: -1 for setup in SETUPS}
    for _, sig in signals.iterrows():
        setup = str(sig["setup"])
        idx = int(sig["signal_idx"])
        if idx <= last_exit_by_setup[setup]:
            continue
        if variant == "rl_gate" and not gate_pass(sig, int(n), float(short_thr), float(long_thr)):
            continue
        entry_idx = idx + 1
        exit_idx = idx + HOLD_BARS
        if exit_idx >= len(frame):
            continue
        direction = -1.0 if setup == "breakout_short" else 1.0
        entry = float(frame.iloc[entry_idx]["open"])
        exit_price = float(frame.iloc[exit_idx]["close"])
        gross = direction * (exit_price / entry - 1.0)
        atr = float(sig["atr14"])
        target = entry * (1.0 + direction * (atr / entry))
        failure = entry * (1.0 - direction * (atr / entry))
        path = frame.iloc[entry_idx: exit_idx + 1]
        target_hit = None
        failure_hit = None
        for bar_idx, bar in path.iterrows():
            if direction > 0:
                if target_hit is None and float(bar["high"]) >= target:
                    target_hit = int(bar_idx)
                if failure_hit is None and float(bar["low"]) <= failure:
                    failure_hit = int(bar_idx)
            else:
                if target_hit is None and float(bar["low"]) <= target:
                    target_hit = int(bar_idx)
                if failure_hit is None and float(bar["high"]) >= failure:
                    failure_hit = int(bar_idx)
        failure_before_target = bool(
            failure_hit is not None and (target_hit is None or failure_hit <= target_hit)
        )
        rows.append(
            {
                "asset": sig["asset"],
                "setup": setup,
                "variant": variant,
                "signal_idx": idx,
                "signal_time": sig["signal_time"],
                "entry_idx": entry_idx,
                "entry_time": frame.iloc[entry_idx]["timestamp"],
                "exit_idx": exit_idx,
                "exit_time": frame.iloc[exit_idx]["timestamp"],
                "entry_price": entry,
                "exit_price": exit_price,
                "gross_return": gross,
                "failure_before_target": failure_before_target,
                "rl_n": int(n) if n is not None else np.nan,
                "short_thr": float(short_thr) if short_thr is not None else np.nan,
                "long_thr": float(long_thr) if long_thr is not None else np.nan,
            }
        )
        last_exit_by_setup[setup] = exit_idx
    return pd.DataFrame(rows)


def metrics(trades: pd.DataFrame, cost_bps: float) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["setup", "variant", "cost_bps", "trades", "mean_total_return", "failure_before_target_rate"])
    tmp = trades.copy()
    tmp["net_return"] = net_ret(tmp["gross_return"], cost_bps)
    g = tmp.groupby(["setup", "variant"], dropna=False)
    out = g.agg(
        trades=("net_return", "size"),
        mean_total_return=("net_return", "mean"),
        failure_before_target_rate=("failure_before_target", "mean"),
    ).reset_index()
    out["cost_bps"] = cost_bps
    return out[["setup", "variant", "cost_bps", "trades", "mean_total_return", "failure_before_target_rate"]]


def split_signals(signals: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    cutoff = signals["signal_time"].sort_values().iloc[max(1, int(len(signals) * TRAIN_FRACTION)) - 1]
    train = signals[signals["signal_time"] <= cutoff].copy()
    test = signals[signals["signal_time"] > cutoff].copy()
    if test.empty:
        test = train.iloc[-max(1, len(train) // 3):].copy()
        train = train.iloc[:-len(test)].copy()
    return train, test


def score_candidate(train_metrics: pd.DataFrame, train_base_counts: dict[str, int], train_gate_counts: dict[str, int]) -> float:
    score = 0.0
    for setup in SETUPS:
        base_row = train_metrics[(train_metrics["setup"] == setup) & (train_metrics["variant"] == "baseline")]
        gate_row = train_metrics[(train_metrics["setup"] == setup) & (train_metrics["variant"] == "rl_gate")]
        if base_row.empty or gate_row.empty:
            score -= 5.0
            continue
        base = base_row.iloc[0]
        gate = gate_row.iloc[0]
        retention = train_gate_counts.get(setup, 0) / max(train_base_counts.get(setup, 0), 1)
        score += float(gate["mean_total_return"] - base["mean_total_return"]) * 100.0
        score += float(base["failure_before_target_rate"] - gate["failure_before_target_rate"]) * 2.0
        score += (retention - 0.65) * 0.5
        if retention < 0.35:
            score -= 1.0
    return score


def pick_params(train_by_asset: dict[str, tuple[pd.DataFrame, pd.DataFrame]]) -> tuple[int, float, float, pd.DataFrame]:
    all_scores: list[dict[str, object]] = []
    for n in N_CHOICES:
        for short_thr in SHORT_THRESH_CHOICES:
            for long_thr in LONG_THRESH_CHOICES:
                all_metrics = []
                base_counts: dict[str, int] = {s: 0 for s in SETUPS}
                gate_counts: dict[str, int] = {s: 0 for s in SETUPS}
                for asset, (frame, train_signals) in train_by_asset.items():
                    base = simulate_variant(frame, train_signals, "baseline")
                    gate = simulate_variant(frame, train_signals, "rl_gate", n=n, short_thr=short_thr, long_thr=long_thr)
                    m = metrics(pd.concat([base, gate], ignore_index=True), PRIMARY_COST)
                    all_metrics.append(m)
                    for setup in SETUPS:
                        base_counts[setup] += int((base["setup"] == setup).sum())
                        gate_counts[setup] += int((gate["setup"] == setup).sum())
                merged = pd.concat(all_metrics, ignore_index=True)
                agg = merged.groupby(["setup", "variant"], dropna=False).agg(
                    trades=("trades", "sum"),
                    mean_total_return=("mean_total_return", "mean"),
                    failure_before_target_rate=("failure_before_target_rate", "mean"),
                ).reset_index()
                all_scores.append(
                    {
                        "n": n,
                        "short_thr": short_thr,
                        "long_thr": long_thr,
                        "score": score_candidate(agg, base_counts, gate_counts),
                    }
                )
    score_df = pd.DataFrame(all_scores).sort_values("score", ascending=False).reset_index(drop=True)
    best = score_df.iloc[0]
    return int(best["n"]), float(best["short_thr"]), float(best["long_thr"]), score_df


def build_summary_table(base_df: pd.DataFrame, gate_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for setup in SETUPS:
        b = base_df[base_df["setup"] == setup]
        g = gate_df[gate_df["setup"] == setup]
        if b.empty or g.empty:
            rows.append({"setup": setup, "baseline_return": np.nan, "gate_return": np.nan, "return_delta": np.nan, "baseline_failure": np.nan, "gate_failure": np.nan, "failure_delta": np.nan, "trade_retention": np.nan, "baseline_trades": int(len(b)), "gate_trades": int(len(g))})
            continue
        b_cost = net_ret(b["gross_return"], PRIMARY_COST)
        g_cost = net_ret(g["gross_return"], PRIMARY_COST)
        rows.append(
            {
                "setup": setup,
                "baseline_return": float(b_cost.mean()),
                "gate_return": float(g_cost.mean()),
                "return_delta": float(g_cost.mean() - b_cost.mean()),
                "baseline_failure": float(b["failure_before_target"].mean()),
                "gate_failure": float(g["failure_before_target"].mean()),
                "failure_delta": float(g["failure_before_target"].mean() - b["failure_before_target"].mean()),
                "trade_retention": float(len(g) / max(len(b), 1)),
                "baseline_trades": int(len(b)),
                "gate_trades": int(len(g)),
            }
        )
    return pd.DataFrame(rows)


def decide_verdict(test_summary: pd.DataFrame) -> tuple[str, str]:
    improved = test_summary[
        (test_summary["return_delta"] > 0)
        & (test_summary["failure_delta"] <= 0.05)
        & (test_summary["trade_retention"] >= 0.50)
    ]
    strong = test_summary[
        (test_summary["return_delta"] > 0.001)
        & (test_summary["failure_delta"] <= 0.0)
        & (test_summary["trade_retention"] >= 0.65)
    ]
    overall_return = float(test_summary["return_delta"].fillna(0).mean())
    overall_failure = float(test_summary["failure_delta"].fillna(0).mean())
    if len(strong) >= 2 and overall_return > 0 and overall_failure <= 0:
        return "promote_P2", "至少两条 baseline 在不过度掉交易数的前提下同时改善了成本后收益和失败率，足够升到 paper candidate pool。"
    if len(improved) >= 1 and overall_return > -0.0005:
        return "keep_P1", "有局部 honest uplift，但跨 setup 还不够稳，先保留在 P1，暂不升 P2。"
    return "park", "改善主要来自砍交易数或只在单条 baseline 上成立，当前不够诚实地支撑 shared overlay 升格。"


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    frames = {asset: build_frame(asset, symbol) for asset, symbol in ASSETS.items()}
    signals_by_asset = {asset: collect_signals(frame, asset) for asset, frame in frames.items()}
    train_test = {asset: split_signals(signals) for asset, signals in signals_by_asset.items()}
    train_by_asset = {asset: (frames[asset], split[0]) for asset, split in train_test.items()}
    test_by_asset = {asset: (frames[asset], split[1]) for asset, split in train_test.items()}

    best_n, best_short, best_long, score_grid = pick_params(train_by_asset)

    train_base_all = []
    train_gate_all = []
    test_base_all = []
    test_gate_all = []
    signal_catalog_parts = []
    for asset in ASSETS:
        frame = frames[asset]
        train_signals, test_signals = train_test[asset]
        train_base = simulate_variant(frame, train_signals, "baseline")
        train_gate = simulate_variant(frame, train_signals, "rl_gate", n=best_n, short_thr=best_short, long_thr=best_long)
        test_base = simulate_variant(frame, test_signals, "baseline")
        test_gate = simulate_variant(frame, test_signals, "rl_gate", n=best_n, short_thr=best_short, long_thr=best_long)
        train_base_all.append(train_base)
        train_gate_all.append(train_gate)
        test_base_all.append(test_base)
        test_gate_all.append(test_gate)
        cat = pd.concat([train_signals.assign(split="train"), test_signals.assign(split="test")], ignore_index=True)
        signal_catalog_parts.append(cat)

    signal_catalog = pd.concat(signal_catalog_parts, ignore_index=True)
    signal_catalog.to_csv(ART_DIR / "signal_catalog.csv", index=False)
    score_grid.to_csv(ART_DIR / "parameter_grid_scores.csv", index=False)

    train_base_df = pd.concat(train_base_all, ignore_index=True)
    train_gate_df = pd.concat(train_gate_all, ignore_index=True)
    test_base_df = pd.concat(test_base_all, ignore_index=True)
    test_gate_df = pd.concat(test_gate_all, ignore_index=True)
    trade_log = pd.concat([train_base_df.assign(split="train"), train_gate_df.assign(split="train"), test_base_df.assign(split="test"), test_gate_df.assign(split="test")], ignore_index=True)
    trade_log.to_csv(ART_DIR / "trade_log.csv", index=False)

    metric_frames = []
    for cost in COSTS:
        metric_frames.append(metrics(pd.concat([train_base_df, train_gate_df], ignore_index=True), cost).assign(split="train"))
        metric_frames.append(metrics(pd.concat([test_base_df, test_gate_df], ignore_index=True), cost).assign(split="test"))
    metrics_df = pd.concat(metric_frames, ignore_index=True)
    metrics_df.to_csv(ART_DIR / "metrics_by_setup_cost_split.csv", index=False)

    test_summary = build_summary_table(test_base_df, test_gate_df)
    train_summary = build_summary_table(train_base_df, train_gate_df)
    train_summary.to_csv(ART_DIR / "train_setup_summary.csv", index=False)
    test_summary.to_csv(ART_DIR / "test_setup_summary.csv", index=False)

    asset_rows = []
    for asset in ASSETS:
        b = test_base_df[test_base_df["asset"] == asset]
        g = test_gate_df[test_gate_df["asset"] == asset]
        base_ret = net_ret(b["gross_return"], PRIMARY_COST)
        gate_ret = net_ret(g["gross_return"], PRIMARY_COST)
        asset_rows.append(
            {
                "asset": asset,
                "baseline_trades": int(len(b)),
                "gate_trades": int(len(g)),
                "trade_retention": float(len(g) / max(len(b), 1)),
                "baseline_return": float(base_ret.mean()) if len(b) else np.nan,
                "gate_return": float(gate_ret.mean()) if len(g) else np.nan,
                "return_delta": float(gate_ret.mean() - base_ret.mean()) if len(b) and len(g) else np.nan,
            }
        )
    asset_summary = pd.DataFrame(asset_rows)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)

    verdict, verdict_reason = decide_verdict(test_summary)
    verdict_label = {
        "promote_P2": "promote_P2 / paper candidate",
        "keep_P1": "keep_P1 / weak candidate",
        "park": "park / evidence pool",
    }[verdict]

    overall = {
        "best_n": best_n,
        "best_short_thr": best_short,
        "best_long_thr": best_long,
        "verdict": verdict,
        "verdict_label": verdict_label,
        "verdict_reason": verdict_reason,
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "test_mean_return_delta": float(test_summary["return_delta"].fillna(0).mean()),
        "test_mean_failure_delta": float(test_summary["failure_delta"].fillna(0).mean()),
        "test_mean_retention": float(test_summary["trade_retention"].fillna(0).mean()),
    }
    (ART_DIR / "summary.json").write_text(json.dumps(overall, ensure_ascii=False, indent=2), encoding="utf-8")

    body = f"""
    <p><a href=\"../../plans/momentum_todo.html\">← 返回 TODO / desk board</a></p>
    <h1>Rank 125 · range location veto gate · minimal clean replication</h1>
    <div class=\"card\">
      <p><b>冻结参数：</b><code>n={best_n}</code> / <code>short_veto=RL&lt;={best_short:.2f}</code> / <code>long_confirm=RL&gt;={best_long:.2f}</code></p>
      <p><b>执行口径：</b><code>signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars</code></p>
      <p><b>当前 hard verdict：</b><span class=\"{'good' if verdict == 'promote_P2' else 'warn' if verdict == 'keep_P1' else 'bad'}\">{escape(verdict_label)}</span></p>
      <p class=\"muted\">{escape(verdict_reason)}</p>
    </div>
    <div class=\"card\">
      <h2>一句话人话</h2>
      <p>{'RL 这层目前足够像一个可继续保留的 shared veto/confirm 候选，但还不到直接上 narrow paper 的程度。' if verdict == 'keep_P1' else 'RL 这层已经跨 baseline 保留了比较诚实的 uplift，可以直接升到 paper candidate pool。' if verdict == 'promote_P2' else 'RL 这层在这次 clean-room 里没有证明自己是更诚实的 shared overlay，更像样本筛选；先 park。'}</p>
    </div>
    <div class=\"card\">
      <h2>测试段主表（6 bps / side）</h2>
      {render_table(test_summary.rename(columns={
        'setup':'setup',
        'baseline_return':'baseline_return',
        'gate_return':'rl_gate_return',
        'return_delta':'return_delta',
        'baseline_failure':'baseline_failure',
        'gate_failure':'rl_gate_failure',
        'failure_delta':'failure_delta',
        'trade_retention':'trade_retention',
        'baseline_trades':'baseline_trades',
        'gate_trades':'rl_gate_trades',
      }), percent_cols={'baseline_return','rl_gate_return','return_delta','baseline_failure','rl_gate_failure','failure_delta','trade_retention'})}
    </div>
    <div class=\"card\">
      <h2>分资产测试段摘要</h2>
      {render_table(asset_summary, percent_cols={'trade_retention','baseline_return','gate_return','return_delta'})}
    </div>
    <div class=\"card\">
      <h2>训练段选参网格（Top 10）</h2>
      {render_table(score_grid.head(10), digits_cols={'score':3, 'short_thr':2, 'long_thr':2})}
    </div>
    <div class=\"card\">
      <h2>artifact</h2>
      <ul>
        <li><code>reports/artifacts/scout_rank125_range_location_veto_15m/signal_catalog.csv</code></li>
        <li><code>reports/artifacts/scout_rank125_range_location_veto_15m/trade_log.csv</code></li>
        <li><code>reports/artifacts/scout_rank125_range_location_veto_15m/test_setup_summary.csv</code></li>
        <li><code>reports/artifacts/scout_rank125_range_location_veto_15m/asset_summary.csv</code></li>
        <li><code>reports/artifacts/scout_rank125_range_location_veto_15m/summary.json</code></li>
      </ul>
    </div>
    """
    write_html(SITE_DIR / "report.html", "Rank 125 · range location veto gate", body)
    write_html(READING_PATH, "Rank 125 · range location veto gate clean replication", body)
    print(json.dumps(overall, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
