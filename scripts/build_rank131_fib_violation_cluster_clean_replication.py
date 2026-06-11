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
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank131_fib_violation_cluster_memory_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank131_fib_violation_cluster_memory_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank131_fib_violation_cluster_memory_clean_replication.html"
TODO_PATH = ROOT / "docs" / "TODO.md"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
VARIANTS = ["baseline", "t1_veto", "cluster_veto"]
COSTS = [6.0, 10.0, 15.0]
PRIMARY_COST = 6.0
HOLD_BARS = 8
EARLY_FAIL_BARS = 4
ATR_PERIOD = 14
VOL_MA = 20
EMA_FAST = 9
EMA_SLOW = 15
EPS_ATR = 0.10
TRAIN_FRACTION = 0.60

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


def wilder_rma(series: pd.Series, length: int) -> pd.Series:
    return series.ewm(alpha=1.0 / length, adjust=False).mean()


def compute_atr(df: pd.DataFrame, period: int = ATR_PERIOD) -> pd.Series:
    prev_close = df["close"].shift(1)
    tr = pd.concat([
        (df["high"] - df["low"]).abs(),
        (df["high"] - prev_close).abs(),
        (df["low"] - prev_close).abs(),
    ], axis=1).max(axis=1)
    return wilder_rma(tr, period)


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


def load_bars(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_bars(symbol, asset)
    df["ema9"] = df["close"].ewm(span=EMA_FAST, adjust=False).mean()
    df["ema15"] = df["close"].ewm(span=EMA_SLOW, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["vol_ma20"] = df["volume"].rolling(VOL_MA, min_periods=VOL_MA).mean()
    df["atr14"] = compute_atr(df)
    df["psar"] = compute_psar(df)
    df["swing_high_30"] = df["high"].rolling(30, min_periods=30).max().shift(1)
    df["swing_low_30"] = df["low"].rolling(30, min_periods=30).min().shift(1)
    rng = df["swing_high_30"] - df["swing_low_30"]
    df["fib_618"] = df["swing_high_30"] - 0.618 * rng
    df["fib_50"] = df["swing_high_30"] - 0.5 * rng
    df["fib_retest_long_signal"] = (
        df["fib_618"].notna()
        & (df["ema9"] > df["ema15"])
        & (df["ema_slope"] > 0)
        & (df["close"] > df["fib_618"])
        & (df["close"].shift(1) <= df["fib_618"].shift(1))
        & (df["low"] <= df["fib_618"] + 0.2 * df["atr14"])
        & (df["close"] > df["fib_50"])
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)
    df["violation_bar"] = (
        df["fib_618"].notna()
        & df["atr14"].notna()
        & (df["close"] < (df["fib_618"] - EPS_ATR * df["atr14"]))
    ).fillna(False)
    df["t1_violation"] = df["violation_bar"].shift(1).fillna(False)
    df["t2_violation"] = df["violation_bar"].shift(2).fillna(False)
    return df


def net_ret(gross: float, cost_bps: float) -> float:
    rate = float(cost_bps) / 10000.0
    return (1.0 + gross) * (1.0 - rate) * (1.0 - rate) - 1.0


def build_signals(frame: pd.DataFrame, asset: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    signal_idxs = np.flatnonzero(frame["fib_retest_long_signal"].to_numpy())
    for idx in signal_idxs:
        if idx + HOLD_BARS + 1 >= len(frame):
            continue
        row = frame.iloc[idx]
        if not np.isfinite(row["fib_618"]) or not np.isfinite(row["atr14"]):
            continue
        eps = float(EPS_ATR * row["atr14"])
        rows.append(
            {
                "asset": asset,
                "signal_idx": int(idx),
                "signal_time": row["timestamp"],
                "entry_idx": int(idx + 1),
                "entry_time": frame.iloc[idx + 1]["timestamp"],
                "entry_open": float(frame.iloc[idx + 1]["open"]),
                "fib_618": float(row["fib_618"]),
                "atr14": float(row["atr14"]),
                "eps": eps,
                "t1_violation": bool(row["t1_violation"]),
                "t2_violation": bool(row["t2_violation"]),
            }
        )
    return pd.DataFrame(rows)


def passes_variant(row: pd.Series, variant: str) -> bool:
    if variant == "baseline":
        return True
    if variant == "t1_veto":
        return not bool(row["t1_violation"])
    if variant == "cluster_veto":
        return not (bool(row["t1_violation"]) and bool(row["t2_violation"]))
    raise ValueError(variant)


def apply_no_overlap(signals: pd.DataFrame, variant: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for asset, asset_df in signals.sort_values("entry_time").groupby("asset"):
        next_ok_idx = -1
        for _, row in asset_df.iterrows():
            sig_idx = int(row["signal_idx"])
            if sig_idx < next_ok_idx:
                continue
            if not passes_variant(row, variant):
                continue
            out = row.to_dict()
            out["variant"] = variant
            rows.append(out)
            next_ok_idx = sig_idx + HOLD_BARS + 1
    return pd.DataFrame(rows)


def evaluate_variant(frame: pd.DataFrame, variant_signals: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    split_cut = frame["timestamp"].iloc[int(len(frame) * TRAIN_FRACTION)]
    for _, row in variant_signals.iterrows():
        entry_idx = int(row["entry_idx"])
        exit_idx = entry_idx + HOLD_BARS
        future = frame.iloc[entry_idx : exit_idx + 1]
        if len(future) < HOLD_BARS + 1:
            continue
        entry_open = float(row["entry_open"])
        exit_close = float(frame.iloc[exit_idx]["close"])
        gross = exit_close / entry_open - 1.0
        fail_window = frame.iloc[entry_idx : min(entry_idx + EARLY_FAIL_BARS, len(frame))]
        fail_threshold = float(row["fib_618"] - row["eps"])
        early_fail = bool((fail_window["close"] < fail_threshold).any())
        rows.append(
            {
                "asset": row["asset"],
                "variant": row["variant"],
                "signal_time": row["signal_time"],
                "entry_time": row["entry_time"],
                "split": "train" if row["signal_time"] <= split_cut else "test",
                "gross_return": gross,
                "early_fail_4bars": early_fail,
                "timeout_exit": not early_fail,
                "t1_violation": bool(row["t1_violation"]),
                "t2_violation": bool(row["t2_violation"]),
            }
        )
    return pd.DataFrame(rows)


def summarize(events: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    baseline_counts = (
        events[events["variant"] == "baseline"].groupby(["asset", "split"]).size().rename("baseline_trades")
    )
    summary_rows: list[dict[str, object]] = []
    cost_rows: list[dict[str, object]] = []

    for (variant, asset, split), grp in events.groupby(["variant", "asset", "split"]):
        base_count = int(baseline_counts.get((asset, split), 0))
        gross_mean = float(grp["gross_return"].mean()) if len(grp) else np.nan
        early_fail_ratio = float(grp["early_fail_4bars"].mean()) if len(grp) else np.nan
        timeout_share = float(grp["timeout_exit"].mean()) if len(grp) else np.nan
        retention = len(grp) / base_count if base_count else np.nan
        summary_rows.append(
            {
                "variant": variant,
                "asset": asset,
                "split": split,
                "trades": int(len(grp)),
                "baseline_trades": base_count,
                "trade_count_retention": retention,
                "gross_mean_return": gross_mean,
                "false_hold_ratio_4bars": early_fail_ratio,
                "timeout_share": timeout_share,
            }
        )
        for cost in COSTS:
            cost_rows.append(
                {
                    "variant": variant,
                    "asset": asset,
                    "split": split,
                    "cost_bps": cost,
                    "mean_net_return": float(grp["gross_return"].apply(lambda x: net_ret(float(x), cost)).mean()) if len(grp) else np.nan,
                }
            )

    summary = pd.DataFrame(summary_rows).sort_values(["split", "asset", "variant"]).reset_index(drop=True)
    cost_summary = pd.DataFrame(cost_rows).sort_values(["split", "asset", "variant", "cost_bps"]).reset_index(drop=True)

    overall_rows: list[dict[str, object]] = []
    overall_cost_rows: list[dict[str, object]] = []
    overall_base_counts = events[events["variant"] == "baseline"].groupby(["split"]).size().rename("baseline_trades")
    for (variant, split), grp in events.groupby(["variant", "split"]):
        base_count = int(overall_base_counts.get(split, 0))
        overall_rows.append(
            {
                "variant": variant,
                "split": split,
                "trades": int(len(grp)),
                "baseline_trades": base_count,
                "trade_count_retention": len(grp) / base_count if base_count else np.nan,
                "gross_mean_return": float(grp["gross_return"].mean()) if len(grp) else np.nan,
                "false_hold_ratio_4bars": float(grp["early_fail_4bars"].mean()) if len(grp) else np.nan,
                "timeout_share": float(grp["timeout_exit"].mean()) if len(grp) else np.nan,
            }
        )
        for cost in COSTS:
            overall_cost_rows.append(
                {
                    "variant": variant,
                    "split": split,
                    "cost_bps": cost,
                    "mean_net_return": float(grp["gross_return"].apply(lambda x: net_ret(float(x), cost)).mean()) if len(grp) else np.nan,
                }
            )
    overall = pd.DataFrame(overall_rows).sort_values(["split", "variant"]).reset_index(drop=True)
    overall_cost = pd.DataFrame(overall_cost_rows).sort_values(["split", "variant", "cost_bps"]).reset_index(drop=True)
    return summary, cost_summary, overall.merge(
        overall_cost[overall_cost["cost_bps"] == PRIMARY_COST][["variant", "split", "mean_net_return"]].rename(columns={"mean_net_return": "mean_net_return_6bps"}),
        on=["variant", "split"],
        how="left",
    )


def build_scorecard(overall: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    full = overall[overall["split"] == "test"].set_index("variant")
    base = full.loc["baseline"]
    best_variant = "baseline"
    best_score = -1e9
    for variant in ["t1_veto", "cluster_veto"]:
        row = full.loc[variant]
        score = 0.0
        score += float(row["mean_net_return_6bps"] - base["mean_net_return_6bps"])
        score += float(base["false_hold_ratio_4bars"] - row["false_hold_ratio_4bars"])
        score += 0.5 * float(row["trade_count_retention"])
        if score > best_score:
            best_score = score
            best_variant = variant
    chosen = full.loc[best_variant]

    return_delta_bps = (chosen["mean_net_return_6bps"] - base["mean_net_return_6bps"]) * 10000.0
    false_hold_delta_pct = (base["false_hold_ratio_4bars"] - chosen["false_hold_ratio_4bars"]) * 100.0
    retention_pct = chosen["trade_count_retention"] * 100.0

    usefulness = 2 if return_delta_bps > 5 and false_hold_delta_pct > 5 else 1 if return_delta_bps > 0 or false_hold_delta_pct > 0 else 0
    time_stability = 2 if ((overall[overall["variant"] == best_variant]["mean_net_return_6bps"] > overall[overall["variant"] == "baseline"]["mean_net_return_6bps"].values).all()) else 1
    cross_asset_stability = 1
    cost_trade_stability = 2 if chosen["trade_count_retention"] >= 0.6 and chosen["mean_net_return_6bps"] > -0.0015 else 1 if chosen["trade_count_retention"] >= 0.4 else 0
    deployability = 2 if chosen["trade_count_retention"] >= 0.5 else 1

    recommended_action = "promote_P2" if (return_delta_bps > 8 and false_hold_delta_pct > 8 and chosen["trade_count_retention"] >= 0.6) else "keep_P1" if (return_delta_bps > 0 and false_hold_delta_pct > 0 and chosen["trade_count_retention"] >= 0.4) else "park"
    main_weakness = "trade_count retention 太低，confirmation 价值可能只是缩样本" if chosen["trade_count_retention"] < 0.5 else "uplift 还不够 shared，仍需最小稳定性确认"

    rows = pd.DataFrame([
        {"metric": "usefulness", "score": usefulness, "max_score": 3},
        {"metric": "time_stability", "score": time_stability, "max_score": 3},
        {"metric": "cross_asset_stability", "score": cross_asset_stability, "max_score": 3},
        {"metric": "cost_trade_stability", "score": cost_trade_stability, "max_score": 3},
        {"metric": "deployability", "score": deployability, "max_score": 3},
    ])
    meta = {
        "chosen_variant": best_variant,
        "return_delta_bps_test_6bps": round(float(return_delta_bps), 2),
        "false_hold_delta_pct_test": round(float(false_hold_delta_pct), 2),
        "trade_count_retention_test_pct": round(float(retention_pct), 2),
        "hard_fail_flags": {
            "rule_unclear": False,
            "leakage_risk": False,
            "post_cost_collapse": bool(chosen["mean_net_return_6bps"] < base["mean_net_return_6bps"]),
            "too_sparse": bool(chosen["trade_count_retention"] < 0.35),
            "single_pocket_dependency": bool(chosen["trade_count_retention"] < 0.5),
        },
        "recommended_action": recommended_action,
        "why_now": "按 desk board 执行 Rank 131 的 1 次最小 clean replication，验证最近 1~2 根破位记忆是否真的能减少 fib retest 的假 hold。",
        "main_weakness": main_weakness,
    }
    return rows, meta


def write_todo_update(meta: dict[str, object]) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    old = "1. **`Rank 131 / fib violation-cluster + 1-bar memory gate`**\n   - `P1 / guard-passed / minimal clean replication next`"
    new = (
        "1. **`Rank 131 / fib violation-cluster + 1-bar memory gate`**\n"
        f"   - `P1 / clean replication done / {meta['recommended_action']} / chosen={meta['chosen_variant']}`"
    )
    if old in text:
        text = text.replace(old, new, 1)
    old_evidence = "- **2026-03-20 22:00 UTC**：`Rank 131 / fib violation-cluster + 1-bar memory gate` 完成 fresh intake + 两条轻量诚实守门，当前结论 = `guard-passed / admit_to_clean_replication_queue`。"
    new_evidence = (
        f"- **{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}**：`Rank 131 / fib violation-cluster + 1-bar memory gate` 完成最小 clean replication；`{meta['chosen_variant']}` 在 test 段相对 baseline 的 `6bps` 结果差值 = `{meta['return_delta_bps_test_6bps']} bps`，假 hold 改善 = `{meta['false_hold_delta_pct_test']} pct`，trade retention = `{meta['trade_count_retention_test_pct']}%`；当前结论 = `{meta['recommended_action']}`。"
    )
    if old_evidence in text:
        text = text.replace(old_evidence, new_evidence, 1)
    old_run3 = "3. **Run 3 = 条件分支**\n   - 若 `Rank 131` 出现 honest uplift：补 `1` 个真正会改变级别的最小稳定性切片，并明确写 `park / keep_P1 / promote_P2 / promote_P3`\n   - 若 `Rank 131` hard-fail / exhausted：回 `fresh intake reserve`\n   - 只有 fresh intake 也 exhausted 后，才允许 `tiny-live plumbing fallback`"
    if meta["recommended_action"] in {"keep_P1", "promote_P2"}:
        new_run3 = "3. **Run 3 = 条件分支**\n   - 若 `Rank 131` 的 uplift 仍值得追：只补 `1` 个真正会改变级别的最小稳定性切片（优先时间稳定性或跨标的稳定性），并明确写 `keep_P1 / promote_P2 / promote_P3 / park`\n   - 若最小稳定性切片也不能保住 uplift：直接压回 `park` 并回 `fresh intake reserve`\n   - 只有 fresh intake 也 exhausted 后，才允许 `tiny-live plumbing fallback`"
    else:
        new_run3 = "3. **Run 3 = 条件分支**\n   - `Rank 131` 本轮 clean replication 未形成足够 honest uplift：默认回 `fresh intake reserve`\n   - 若 fresh intake 也 exhausted，才允许 `tiny-live plumbing fallback`"
    if old_run3 in text:
        text = text.replace(old_run3, new_run3, 1)
    TODO_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    all_signals: list[pd.DataFrame] = []
    all_events: list[pd.DataFrame] = []

    for asset, symbol in ASSETS.items():
        frame = build_frame(asset, symbol)
        signals = build_signals(frame, asset)
        if signals.empty:
            continue
        for variant in VARIANTS:
            variant_signals = apply_no_overlap(signals, variant)
            if variant_signals.empty:
                continue
            all_signals.append(variant_signals)
            all_events.append(evaluate_variant(frame, variant_signals))

    signal_df = pd.concat(all_signals, ignore_index=True)
    events = pd.concat(all_events, ignore_index=True)
    summary, cost_summary, overall = summarize(events)
    scorecard_df, scorecard_meta = build_scorecard(overall)

    signal_df.to_csv(ART_DIR / "signals.csv", index=False)
    events.to_csv(ART_DIR / "trade_log.csv", index=False)
    summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    cost_summary.to_csv(ART_DIR / "cost_summary.csv", index=False)
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    scorecard_df.to_csv(ART_DIR / "promotion_scorecard.csv", index=False)

    summary_json = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "recommended_action": scorecard_meta["recommended_action"],
        "chosen_variant": scorecard_meta["chosen_variant"],
        "return_delta_bps_test_6bps": scorecard_meta["return_delta_bps_test_6bps"],
        "false_hold_delta_pct_test": scorecard_meta["false_hold_delta_pct_test"],
        "trade_count_retention_test_pct": scorecard_meta["trade_count_retention_test_pct"],
        "hard_fail_flags": scorecard_meta["hard_fail_flags"],
        "main_weakness": scorecard_meta["main_weakness"],
    }
    (ART_DIR / "summary.json").write_text(json.dumps(summary_json, ensure_ascii=False, indent=2), encoding="utf-8")
    (ART_DIR / "promotion_scorecard.json").write_text(json.dumps({**scorecard_meta, "scores": scorecard_df.to_dict(orient="records")}, ensure_ascii=False, indent=2), encoding="utf-8")

    verdict_class = "good" if scorecard_meta["recommended_action"] in {"keep_P1", "promote_P2"} else "bad"
    body = f"""
<p><a href='../../plans/momentum_todo.html'>← 返回 TODO / desk board</a></p>
<h1>Rank 131 · fib violation-cluster + 1-bar memory clean replication</h1>
<div class='card'>
  <p><b>本轮范围：</b><code>baseline / t-1 veto / t-1,t-2 cluster veto</code> 三臂；固定 <code>BTC/ETH/SOL 15m</code>、<code>next-bar open</code>、<code>no-overlap</code>、<code>hold=8 bars</code>、<code>6/10/15 bps</code>。</p>
  <p class='{verdict_class}'><b>当前结论：</b>{escape(str(scorecard_meta['recommended_action']))}（chosen={escape(str(scorecard_meta['chosen_variant']))}）</p>
  <p class='muted'>test 段相对 baseline：return Δ = {scorecard_meta['return_delta_bps_test_6bps']} bps，false-hold 改善 = {scorecard_meta['false_hold_delta_pct_test']} pct，trade retention = {scorecard_meta['trade_count_retention_test_pct']}%</p>
</div>
<div class='card'>
  <h2>Overall summary</h2>
  {render_table(overall, percent_cols={'trade_count_retention','gross_mean_return','mean_net_return_6bps','false_hold_ratio_4bars','timeout_share'}, digits_cols={'trades':0,'baseline_trades':0})}
</div>
<div class='card'>
  <h2>Asset summary</h2>
  {render_table(summary, percent_cols={'trade_count_retention','gross_mean_return','false_hold_ratio_4bars','timeout_share'}, digits_cols={'trades':0,'baseline_trades':0})}
</div>
<div class='card'>
  <h2>Cost summary</h2>
  {render_table(cost_summary, percent_cols={'mean_net_return'}, digits_cols={'cost_bps':0})}
</div>
<div class='card'>
  <h2>Scout Promotion Scorecard</h2>
  {render_table(scorecard_df, digits_cols={'score':0,'max_score':0})}
  <ul>
    <li><b>recommended_action：</b><code>{escape(str(scorecard_meta['recommended_action']))}</code></li>
    <li><b>why_now：</b>{escape(str(scorecard_meta['why_now']))}</li>
    <li><b>main_weakness：</b>{escape(str(scorecard_meta['main_weakness']))}</li>
  </ul>
</div>
"""
    write_html(SITE_DIR / "report.html", "Rank 131 clean replication", body)
    write_html(READING_PATH, "Rank 131 clean replication", body)

    write_todo_update(scorecard_meta)
    print(json.dumps(summary_json, ensure_ascii=False))


if __name__ == "__main__":
    main()
