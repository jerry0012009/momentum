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
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank126_deepest_retracement_hold_quality_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank126_deepest_retracement_hold_quality_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank126_deepest_retracement_hold_quality_clean_replication.html"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
LOOKBACK_CHOICES = [4, 8, 12]
CURRENT_THRESH_CHOICES = [0.50, 0.618, 0.79]
DEEPEST_THRESH_CHOICES = [0.50, 0.618, 0.79]
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
th, td { border-bottom:1px solid #e5eeb; padding:8px 10px; text-align:left; vertical-align:top; }
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
    df["atr14"] = compute_atr(df)
    df["vol_ma20"] = df["volume"].rolling(20, min_periods=20).mean()
    df["swing_high_30"] = df["high"].rolling(30, min_periods=30).max().shift(1)
    df["swing_low_30"] = df["low"].rolling(30, min_periods=30).min().shift(1)
    df["range_30"] = (df["swing_high_30"] - df["swing_low_30"]).clip(lower=EPS)
    df["fib_618"] = df["swing_high_30"] - 0.618 * df["range_30"]
    df["fib_500"] = df["swing_high_30"] - 0.500 * df["range_30"]
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
    return df


def collect_signals(frame: pd.DataFrame, asset: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for idx in np.flatnonzero(frame["fib_retest_long_signal"].to_numpy()):
        if idx + HOLD_BARS + 1 >= len(frame) or idx < max(LOOKBACK_CHOICES):
            continue
        row = frame.iloc[idx]
        if not np.isfinite(row["atr14"]) or row["atr14"] <= 0:
            continue
        signal_range = float(row["range_30"])
        if not np.isfinite(signal_range) or signal_range <= 0:
            continue
        rec: dict[str, object] = {
            "asset": asset,
            "setup": "fib_retest_long",
            "signal_idx": int(idx),
            "signal_time": row["timestamp"],
            "atr14": float(row["atr14"]),
            "entry_hint_close": float(row["close"]),
            "signal_low": float(row["low"]),
            "swing_high_30": float(row["swing_high_30"]),
            "swing_low_30": float(row["swing_low_30"]),
            "range_30": signal_range,
        }
        rec["current_retracement_pct"] = float((float(row["swing_high_30"]) - float(row["low"])) / signal_range)
        for lb in LOOKBACK_CHOICES:
            trailing_low = float(frame.iloc[idx - lb + 1: idx + 1]["low"].min())
            rec[f"deepest_retracement_pct_lb{lb}"] = float((float(row["swing_high_30"]) - trailing_low) / signal_range)
        rows.append(rec)
    out = pd.DataFrame(rows)
    return out.sort_values(["asset", "signal_time"]).reset_index(drop=True)


def split_signals(signals: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    cutoff = signals["signal_time"].sort_values().iloc[max(1, int(len(signals) * TRAIN_FRACTION)) - 1]
    train = signals[signals["signal_time"] <= cutoff].copy()
    test = signals[signals["signal_time"] > cutoff].copy()
    if test.empty:
        test = train.iloc[-max(1, len(train) // 3):].copy()
        train = train.iloc[:-len(test)].copy()
    return train, test


def pass_gate(sig: pd.Series, variant: str, current_thr: float, deepest_thr: float, lb: int) -> bool:
    current = sig["current_retracement_pct"]
    deepest = sig[f"deepest_retracement_pct_lb{lb}"]
    if pd.isna(current) or pd.isna(deepest):
        return False
    if variant == "current_only":
        return float(current) <= current_thr
    if variant == "current_plus_deepest":
        return float(current) <= current_thr and float(deepest) <= deepest_thr
    return True


def simulate_variant(frame: pd.DataFrame, signals: pd.DataFrame, variant: str, current_thr: float, deepest_thr: float, lb: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    last_exit = -1
    for _, sig in signals.iterrows():
        idx = int(sig["signal_idx"])
        if idx <= last_exit:
            continue
        if variant != "baseline" and not pass_gate(sig, variant, current_thr, deepest_thr, lb):
            continue
        entry_idx = idx + 1
        exit_idx = idx + HOLD_BARS
        if exit_idx >= len(frame):
            continue
        entry = float(frame.iloc[entry_idx]["open"])
        exit_price = float(frame.iloc[exit_idx]["close"])
        gross = exit_price / entry - 1.0
        atr = float(sig["atr14"])
        target = entry + atr
        failure = entry - atr
        path = frame.iloc[entry_idx: exit_idx + 1]
        target_hit = None
        failure_hit = None
        for bar_idx, bar in path.iterrows():
            if target_hit is None and float(bar["high"]) >= target:
                target_hit = int(bar_idx)
            if failure_hit is None and float(bar["low"]) <= failure:
                failure_hit = int(bar_idx)
        failure_before_target = bool(failure_hit is not None and (target_hit is None or failure_hit <= target_hit))
        false_hold = bool(failure_before_target and gross > -0.002)
        rows.append(
            {
                "asset": sig["asset"],
                "setup": "fib_retest_long",
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
                "current_retracement_pct": float(sig["current_retracement_pct"]),
                "deepest_retracement_pct": float(sig[f"deepest_retracement_pct_lb{lb}"]),
                "current_thr": current_thr,
                "deepest_thr": deepest_thr,
                "lookback_bars": lb,
                "failure_before_target": failure_before_target,
                "false_hold": false_hold,
            }
        )
        last_exit = exit_idx
    return pd.DataFrame(rows)


def summarize_variant(baseline: pd.DataFrame, variant_df: pd.DataFrame, cost_bps: float) -> dict[str, float]:
    b_net = net_ret(baseline["gross_return"], cost_bps) if len(baseline) else pd.Series(dtype=float)
    v_net = net_ret(variant_df["gross_return"], cost_bps) if len(variant_df) else pd.Series(dtype=float)
    return {
        "baseline_trades": int(len(baseline)),
        "variant_trades": int(len(variant_df)),
        "baseline_return": float(b_net.mean()) if len(b_net) else np.nan,
        "variant_return": float(v_net.mean()) if len(v_net) else np.nan,
        "return_delta": float(v_net.mean() - b_net.mean()) if len(b_net) and len(v_net) else np.nan,
        "baseline_failure_before_target": float(baseline["failure_before_target"].mean()) if len(baseline) else np.nan,
        "variant_failure_before_target": float(variant_df["failure_before_target"].mean()) if len(variant_df) else np.nan,
        "failure_delta": float(variant_df["failure_before_target"].mean() - baseline["failure_before_target"].mean()) if len(baseline) and len(variant_df) else np.nan,
        "baseline_false_hold": float(baseline["false_hold"].mean()) if len(baseline) else np.nan,
        "variant_false_hold": float(variant_df["false_hold"].mean()) if len(variant_df) else np.nan,
        "false_hold_delta": float(variant_df["false_hold"].mean() - baseline["false_hold"].mean()) if len(baseline) and len(variant_df) else np.nan,
        "trade_count_retention": float(len(variant_df) / max(len(baseline), 1)),
    }


def score_candidate(train_baseline: pd.DataFrame, train_variant: pd.DataFrame) -> float:
    s = summarize_variant(train_baseline, train_variant, PRIMARY_COST)
    if s["variant_trades"] < 8:
        return -999.0
    score = 0.0
    score += float(s["return_delta"] if pd.notna(s["return_delta"]) else -0.1) * 120.0
    score += float((s["baseline_failure_before_target"] - s["variant_failure_before_target"]) if pd.notna(s["variant_failure_before_target"]) else -0.1) * 4.0
    score += float((s["baseline_false_hold"] - s["variant_false_hold"]) if pd.notna(s["variant_false_hold"]) else -0.1) * 3.0
    score += (float(s["trade_count_retention"]) - 0.55) * 1.5
    return score


def pick_params(train_by_asset: dict[str, tuple[pd.DataFrame, pd.DataFrame]]) -> tuple[int, float, float, pd.DataFrame]:
    rows: list[dict[str, float]] = []
    for lb in LOOKBACK_CHOICES:
        for current_thr in CURRENT_THRESH_CHOICES:
            for deepest_thr in DEEPEST_THRESH_CHOICES:
                if deepest_thr + 1e-9 < current_thr:
                    continue
                train_base_all = []
                train_gate_all = []
                for asset, (frame, train_signals) in train_by_asset.items():
                    train_base_all.append(simulate_variant(frame, train_signals, "baseline", current_thr, deepest_thr, lb))
                    train_gate_all.append(simulate_variant(frame, train_signals, "current_plus_deepest", current_thr, deepest_thr, lb))
                train_base_df = pd.concat(train_base_all, ignore_index=True)
                train_gate_df = pd.concat(train_gate_all, ignore_index=True)
                rows.append(
                    {
                        "lookback_bars": lb,
                        "current_thr": current_thr,
                        "deepest_thr": deepest_thr,
                        "score": score_candidate(train_base_df, train_gate_df),
                        "train_baseline_trades": int(len(train_base_df)),
                        "train_gate_trades": int(len(train_gate_df)),
                    }
                )
    grid = pd.DataFrame(rows).sort_values(["score", "train_gate_trades"], ascending=[False, False]).reset_index(drop=True)
    best = grid.iloc[0]
    return int(best["lookback_bars"]), float(best["current_thr"]), float(best["deepest_thr"]), grid


def decide_verdict(test_variant_summary: dict[str, float], asset_summary: pd.DataFrame) -> tuple[str, str]:
    positive_assets = int((asset_summary["variant_return"] > asset_summary["baseline_return"]).fillna(False).sum())
    if (
        pd.notna(test_variant_summary["return_delta"])
        and test_variant_summary["return_delta"] > 0
        and pd.notna(test_variant_summary["failure_delta"])
        and test_variant_summary["failure_delta"] <= 0
        and pd.notna(test_variant_summary["false_hold_delta"])
        and test_variant_summary["false_hold_delta"] <= 0
        and test_variant_summary["trade_count_retention"] >= 0.55
        and positive_assets >= 2
    ):
        return "promote_P2", "deepest gate 在测试段里同时改善了成本后收益、failure-before-target 与 false-hold，且没有靠极端砍单，足够升到 paper candidate pool。"
    if (
        pd.notna(test_variant_summary["return_delta"])
        and test_variant_summary["return_delta"] > -0.0025
        and pd.notna(test_variant_summary["failure_delta"])
        and test_variant_summary["failure_delta"] <= 0.02
        and test_variant_summary["trade_count_retention"] >= 0.35
        and positive_assets >= 1
    ):
        return "keep_P1", "deepest gate 显示出局部 honest uplift，但跨资产还不够硬，先留在 P1，等待下一手真正会改 verdict 的检查。"
    return "park", "改善主要靠缩样本，或连测试段的 hold-quality 指标都没同步变好；当前更诚实的处理是 park。"


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    frames = {asset: build_frame(asset, symbol) for asset, symbol in ASSETS.items()}
    signals_by_asset = {asset: collect_signals(frame, asset) for asset, frame in frames.items()}
    train_test = {asset: split_signals(signals) for asset, signals in signals_by_asset.items()}
    train_by_asset = {asset: (frames[asset], split[0]) for asset, split in train_test.items()}

    best_lb, best_current, best_deepest, score_grid = pick_params(train_by_asset)
    score_grid.to_csv(ART_DIR / "parameter_grid_scores.csv", index=False)

    signal_catalog = pd.concat(
        [pd.concat([split[0].assign(split="train"), split[1].assign(split="test")], ignore_index=True) for split in train_test.values()],
        ignore_index=True,
    )
    signal_catalog.to_csv(ART_DIR / "signal_catalog.csv", index=False)

    variant_names = ["baseline", "current_only", "current_plus_deepest"]
    split_trade_parts = []
    overall_rows = []
    asset_rows = []
    per_cost_rows = []

    for split_name in ["train", "test"]:
        all_by_variant: dict[str, list[pd.DataFrame]] = {name: [] for name in variant_names}
        for asset in ASSETS:
            frame = frames[asset]
            signals = train_test[asset][0] if split_name == "train" else train_test[asset][1]
            for variant in variant_names:
                trades = simulate_variant(frame, signals, variant, best_current, best_deepest, best_lb)
                all_by_variant[variant].append(trades)
                if not trades.empty:
                    split_trade_parts.append(trades.assign(split=split_name))

            baseline_asset = all_by_variant["baseline"][-1]
            current_asset = all_by_variant["current_only"][-1]
            deepest_asset = all_by_variant["current_plus_deepest"][-1]
            for variant, variant_df in [("current_only", current_asset), ("current_plus_deepest", deepest_asset)]:
                summary = summarize_variant(baseline_asset, variant_df, PRIMARY_COST)
                asset_rows.append({"split": split_name, "asset": asset, "variant": variant, **summary})

        baseline_df = pd.concat(all_by_variant["baseline"], ignore_index=True)
        current_df = pd.concat(all_by_variant["current_only"], ignore_index=True)
        deepest_df = pd.concat(all_by_variant["current_plus_deepest"], ignore_index=True)

        for variant, variant_df in [("current_only", current_df), ("current_plus_deepest", deepest_df)]:
            overall_rows.append({"split": split_name, "variant": variant, **summarize_variant(baseline_df, variant_df, PRIMARY_COST)})

        for cost in COSTS:
            for variant, variant_df in [("current_only", current_df), ("current_plus_deepest", deepest_df)]:
                s = summarize_variant(baseline_df, variant_df, cost)
                per_cost_rows.append({"split": split_name, "variant": variant, "cost_bps_per_side": cost, **s})

    trade_log = pd.concat(split_trade_parts, ignore_index=True) if split_trade_parts else pd.DataFrame()
    trade_log.to_csv(ART_DIR / "trade_log.csv", index=False)

    overall_summary = pd.DataFrame(overall_rows)
    overall_summary.to_csv(ART_DIR / "overall_summary.csv", index=False)
    asset_summary = pd.DataFrame(asset_rows)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    cost_summary = pd.DataFrame(per_cost_rows)
    cost_summary.to_csv(ART_DIR / "cost_summary.csv", index=False)

    test_deepest = overall_summary[(overall_summary["split"] == "test") & (overall_summary["variant"] == "current_plus_deepest")].iloc[0].to_dict()
    asset_test_deepest = asset_summary[(asset_summary["split"] == "test") & (asset_summary["variant"] == "current_plus_deepest")].copy()
    verdict, verdict_reason = decide_verdict(test_deepest, asset_test_deepest)
    verdict_label = {
        "promote_P2": "promote_P2 / paper candidate",
        "keep_P1": "keep_P1 / weak candidate",
        "park": "park / evidence pool",
    }[verdict]

    summary_json = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "lookback_bars": best_lb,
        "current_threshold": best_current,
        "deepest_threshold": best_deepest,
        "verdict": verdict,
        "verdict_label": verdict_label,
        "verdict_reason": verdict_reason,
        "test_current_only": overall_summary[(overall_summary["split"] == "test") & (overall_summary["variant"] == "current_only")].iloc[0].to_dict(),
        "test_current_plus_deepest": test_deepest,
    }
    (ART_DIR / "summary.json").write_text(json.dumps(summary_json, ensure_ascii=False, indent=2), encoding="utf-8")

    test_table = overall_summary[overall_summary["split"] == "test"].copy()
    asset_table = asset_summary[asset_summary["split"] == "test"].copy()
    cost_table = cost_summary[cost_summary["split"] == "test"].copy()

    body = f"""
    <p><a href=\"../../plans/momentum_todo.html\">← 返回 TODO / desk board</a></p>
    <h1>Rank 126 · deepest retracement hold-quality gate · minimal clean replication</h1>
    <div class=\"card\">
      <p><b>冻结参数：</b><code>lookback={best_lb}</code> / <code>current&lt;={best_current:.3f}</code> / <code>deepest&lt;={best_deepest:.3f}</code></p>
      <p><b>执行口径：</b><code>BTC/ETH/SOL 120d 15m + fib_retest_long + signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars</code></p>
      <p><b>当前 hard verdict：</b><span class=\"{'good' if verdict == 'promote_P2' else 'warn' if verdict == 'keep_P1' else 'bad'}\">{escape(verdict_label)}</span></p>
      <p class=\"muted\">{escape(verdict_reason)}</p>
    </div>
    <div class=\"card\">
      <h2>一句话人话</h2>
      <p>这轮只回答一件事：把 fib retest 的“当前回踩够浅吗”升级成“当前回踩 + 最近几根里最深曾经扎到哪”，能不能更诚实地过滤掉假 hold。</p>
      <p>读法上，<code>current_only</code> 是只看信号当根 low 的回踩深度；<code>current_plus_deepest</code> 则额外要求最近 <code>{best_lb}</code> 根里的最深 low 也不过阈值。</p>
    </div>
    <div class=\"card\">
      <h2>测试段总表（6 bps / side）</h2>
      {render_table(test_table[["variant","baseline_trades","variant_trades","trade_count_retention","baseline_return","variant_return","return_delta","baseline_failure_before_target","variant_failure_before_target","failure_delta","baseline_false_hold","variant_false_hold","false_hold_delta"]], percent_cols={"trade_count_retention","baseline_return","variant_return","return_delta","baseline_failure_before_target","variant_failure_before_target","failure_delta","baseline_false_hold","variant_false_hold","false_hold_delta"})}
    </div>
    <div class=\"card\">
      <h2>测试段分资产对照（6 bps / side）</h2>
      {render_table(asset_table[["asset","variant","baseline_trades","variant_trades","trade_count_retention","baseline_return","variant_return","return_delta","baseline_failure_before_target","variant_failure_before_target","failure_delta","baseline_false_hold","variant_false_hold","false_hold_delta"]], percent_cols={"trade_count_retention","baseline_return","variant_return","return_delta","baseline_failure_before_target","variant_failure_before_target","failure_delta","baseline_false_hold","variant_false_hold","false_hold_delta"})}
    </div>
    <div class=\"card\">
      <h2>成本稳健性（测试段）</h2>
      {render_table(cost_table[["variant","cost_bps_per_side","baseline_trades","variant_trades","trade_count_retention","baseline_return","variant_return","return_delta","baseline_failure_before_target","variant_failure_before_target","failure_delta"]], percent_cols={"trade_count_retention","baseline_return","variant_return","return_delta","baseline_failure_before_target","variant_failure_before_target","failure_delta"})}
    </div>
    <div class=\"card\">
      <h2>训练段选参网格（Top 10）</h2>
      {render_table(score_grid.head(10), digits_cols={"score":3,"current_thr":3,"deepest_thr":3})}
    </div>
    <div class=\"card\">
      <h2>artifact</h2>
      <ul>
        <li><code>reports/artifacts/scout_rank126_deepest_retracement_hold_quality_15m/signal_catalog.csv</code></li>
        <li><code>reports/artifacts/scout_rank126_deepest_retracement_hold_quality_15m/trade_log.csv</code></li>
        <li><code>reports/artifacts/scout_rank126_deepest_retracement_hold_quality_15m/overall_summary.csv</code></li>
        <li><code>reports/artifacts/scout_rank126_deepest_retracement_hold_quality_15m/asset_summary.csv</code></li>
        <li><code>reports/artifacts/scout_rank126_deepest_retracement_hold_quality_15m/cost_summary.csv</code></li>
        <li><code>reports/artifacts/scout_rank126_deepest_retracement_hold_quality_15m/summary.json</code></li>
      </ul>
    </div>
    """

    write_html(SITE_DIR / "report.html", "Rank 126 · deepest retracement hold-quality gate", body)
    write_html(READING_PATH, "Rank 126 · deepest retracement hold-quality gate clean replication", body)
    print(json.dumps(summary_json, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
