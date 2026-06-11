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
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank79_one_regime_per_session_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank79_one_regime_per_session_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank79_one_regime_per_session_clean_replication.html"
TODO_PATH = ROOT / "docs" / "TODO.md"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
SETUPS = ["ema_psar_long", "fib_retest_long", "breakout_short"]
CONTINUATION_SETUPS = {"ema_psar_long", "breakout_short"}
RETEST_SETUPS = {"fib_retest_long"}
VARIANTS = ["baseline_all_lanes", "continuation_only", "retest_only", "one_regime_per_session"]
PRIMARY_VARIANT = "one_regime_per_session"
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0]
HOLD_BARS = 8
EARLY_FAIL_BARS = 4
SESSION_SPECS = [
    ("asia", 0, 8),
    ("europe", 8, 13),
    ("us", 13, 24),
]
CSS = """
body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width:1150px; margin:40px auto; padding:0 18px 48px; line-height:1.72; color:#111827; background:#f8fafc; }
.card { border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }
.pill { display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }
.muted { color:#6b7280; }
code { background:#f3f4f6; padding:1px 5px; border-radius:6px; }
table { width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; background:white; }
th, td { border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }
a { color:#2563eb; text-decoration:none; }
"""


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def pct(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def num(v: float | int | None, digits: int = 2) -> str:
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


def load_bars(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    df = pd.read_csv(path)
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


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_bars(symbol, asset)
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema15"] = df["close"].ewm(span=15, adjust=False).mean()
    df["ema34"] = df["close"].ewm(span=34, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["vol_ma20"] = df["volume"].rolling(20, min_periods=20).mean()
    df["atr14"] = compute_atr(df)
    df["psar"] = compute_psar(df)
    df["atr_pct"] = (df["atr14"] / df["close"]).replace([np.inf, -np.inf], np.nan)

    df["swing_high_30"] = df["high"].rolling(30, min_periods=30).max().shift(1)
    df["swing_low_30"] = df["low"].rolling(30, min_periods=30).min().shift(1)
    rng = df["swing_high_30"] - df["swing_low_30"]
    df["fib_618"] = df["swing_high_30"] - 0.618 * rng
    df["fib_50"] = df["swing_high_30"] - 0.5 * rng
    df["rolling_low20"] = df["low"].rolling(20, min_periods=20).min().shift(1)
    atr = df["atr14"]

    df["ema_psar_long_signal"] = (
        (df["ema9"] > df["ema15"])
        & (df["ema_slope"] > 0.0003)
        & (df["psar"] < df["close"])
        & (df["close"] > df["high"].shift(1))
        & (df["close"].shift(1) < df["ema9"].shift(1))
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)

    df["fib_retest_long_signal"] = (
        df["fib_618"].notna()
        & (df["ema9"] > df["ema15"])
        & (df["ema_slope"] > 0)
        & (df["close"] > df["fib_618"])
        & (df["close"].shift(1) <= df["fib_618"].shift(1))
        & (df["low"] <= df["fib_618"] + 0.2 * atr)
        & (df["close"] > df["fib_50"])
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)

    low = df["rolling_low20"]
    df["breakout_short_signal"] = (
        low.notna()
        & (df["ema9"] < df["ema15"])
        & (df["ema_slope"] < -0.0003)
        & (df["close"].shift(1) > low.shift(1))
        & (df["close"].shift(2) > low.shift(2))
        & (df["close"] < low - 0.1 * atr)
        & (df["high"] <= low + 0.3 * atr)
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)

    df["session_name"] = df["timestamp"].apply(session_name)
    df["session_anchor"] = df["timestamp"].apply(session_anchor)
    df["session_id"] = df["session_anchor"].dt.strftime("%Y-%m-%dT%H:%MZ") + "|" + df["session_name"]
    session_meta = build_session_meta(df)
    df = df.merge(session_meta, on="session_id", how="left")
    return df


def session_name(ts: pd.Timestamp) -> str:
    hour = ts.hour
    for name, start, end in SESSION_SPECS:
        if start <= hour < end:
            return name
    return "us"


def session_anchor(ts: pd.Timestamp) -> pd.Timestamp:
    hour = ts.hour
    date = ts.floor("D")
    if hour < 8:
        return date
    if hour < 13:
        return date + pd.Timedelta(hours=8)
    return date + pd.Timedelta(hours=13)


def build_session_meta(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for session_id, g in df.groupby("session_id", sort=True):
        head = g.head(4).copy()
        if len(head) < 4 or head["atr14"].isna().any():
            regime = "unclear"
            feature_ready = False
            open_ret = np.nan
            range_atr = np.nan
            close_loc = np.nan
            vwap_dist = np.nan
        else:
            feature_ready = True
            open_px = float(head.iloc[0]["open"])
            close_px = float(head.iloc[-1]["close"])
            high_px = float(head["high"].max())
            low_px = float(head["low"].min())
            avg_atr = float(head["atr14"].mean())
            tp = (head["high"] + head["low"] + head["close"]) / 3.0
            vwap = float((tp * head["volume"]).sum() / head["volume"].sum()) if float(head["volume"].sum()) > 0 else float(tp.mean())
            rng = max(high_px - low_px, 1e-12)
            open_ret = close_px / open_px - 1.0
            range_atr = (high_px - low_px) / max(avg_atr, 1e-12)
            close_loc = (close_px - low_px) / rng
            vwap_dist = close_px / vwap - 1.0 if vwap else 0.0
            regime = classify_regime(open_ret, range_atr, close_loc, vwap_dist)
        rows.append(
            {
                "session_id": session_id,
                "session_regime": regime,
                "feature_ready": feature_ready,
                "session_first4_return": open_ret,
                "session_first4_range_atr": range_atr,
                "session_first4_close_loc": close_loc,
                "session_first4_vwap_dist": vwap_dist,
            }
        )
    return pd.DataFrame(rows)


def classify_regime(open_ret: float, range_atr: float, close_loc: float, vwap_dist: float) -> str:
    continuation_up = open_ret >= 0.003 and range_atr >= 1.2 and close_loc >= 0.65 and vwap_dist >= 0.0005
    continuation_down = open_ret <= -0.003 and range_atr >= 1.2 and close_loc <= 0.35 and vwap_dist <= -0.0005
    retest = abs(open_ret) <= 0.0025 and range_atr >= 0.8 and 0.35 <= close_loc <= 0.65 and abs(vwap_dist) <= 0.0015
    if continuation_up or continuation_down:
        return "continuation"
    if retest:
        return "retest"
    return "unclear"


def direction_for_setup(setup: str) -> int:
    return 1 if setup != "breakout_short" else -1


def build_signal_frame(frame: pd.DataFrame, asset: str, setup: str) -> pd.DataFrame:
    base = frame[f"{setup}_signal"] & ~frame[f"{setup}_signal"].shift(1).fillna(False)
    rows: list[dict[str, object]] = []
    last_exit = -1
    direction = direction_for_setup(setup)
    setup_group = "continuation" if setup in CONTINUATION_SETUPS else "retest"
    session_first_idx = frame.groupby("session_id").head(1).set_index("session_id").index.to_series()
    session_first_idx = {sid: int(frame.index[frame["session_id"] == sid][0]) for sid in session_first_idx.index}
    for idx in range(40, len(frame) - HOLD_BARS - 2):
        if idx <= last_exit or not bool(base.iloc[idx]):
            continue
        entry_idx = idx + 1
        exit_idx = entry_idx + HOLD_BARS
        if exit_idx >= len(frame):
            break
        signal_row = frame.iloc[idx]
        entry_price = float(frame.iloc[entry_idx]["open"])
        exit_price = float(frame.iloc[exit_idx]["open"])
        gross_return = direction * (exit_price / entry_price - 1.0)
        path = frame.iloc[entry_idx : entry_idx + EARLY_FAIL_BARS + 1]
        if direction == 1:
            early_fail = bool((path["close"] < path["ema34"]).any())
        else:
            early_fail = bool((path["close"] > path["ema34"]).any())
        rows.append(
            {
                "signal_id": f"{asset}|{setup}|{idx}",
                "asset": asset,
                "setup": setup,
                "setup_group": setup_group,
                "signal_idx": idx,
                "entry_idx": entry_idx,
                "exit_idx": exit_idx,
                "signal_ts": pd.to_datetime(signal_row["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_ts": pd.to_datetime(frame.iloc[entry_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": pd.to_datetime(frame.iloc[exit_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_price": entry_price,
                "exit_price": exit_price,
                "gross_return": gross_return,
                "early_fail": early_fail,
                "session_id": signal_row["session_id"],
                "session_name": signal_row["session_name"],
                "session_anchor": pd.to_datetime(signal_row["session_anchor"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "session_regime": signal_row["session_regime"],
                "feature_ready": bool(signal_row["feature_ready"]),
                "session_first4_return": signal_row["session_first4_return"],
                "session_first4_range_atr": signal_row["session_first4_range_atr"],
                "session_first4_close_loc": signal_row["session_first4_close_loc"],
                "session_first4_vwap_dist": signal_row["session_first4_vwap_dist"],
                "after_regime_ready": idx >= session_first_idx[str(signal_row["session_id"])] + 4,
            }
        )
        last_exit = exit_idx
    return pd.DataFrame(rows)


def allow_variant(df: pd.DataFrame, variant: str) -> pd.Series:
    if variant == "baseline_all_lanes":
        return pd.Series(True, index=df.index)
    if variant == "continuation_only":
        return df["setup_group"] == "continuation"
    if variant == "retest_only":
        return df["setup_group"] == "retest"
    if variant == "one_regime_per_session":
        return (
            df["feature_ready"].fillna(False)
            & df["after_regime_ready"].fillna(False)
            & (
                ((df["session_regime"] == "continuation") & (df["setup_group"] == "continuation"))
                | ((df["session_regime"] == "retest") & (df["setup_group"] == "retest"))
            )
        )
    raise ValueError(variant)


def build_variant_trades(raw_trades: pd.DataFrame) -> pd.DataFrame:
    outputs: list[pd.DataFrame] = []
    for variant in VARIANTS:
        allowed = raw_trades[allow_variant(raw_trades, variant)].copy()
        if allowed.empty:
            continue
        allowed["variant"] = variant
        allowed = allowed.sort_values(["asset", "session_id", "entry_idx", "setup"]).reset_index(drop=True)
        allowed["allowed_candidates_in_session"] = allowed.groupby(["asset", "session_id"])["signal_id"].transform("count")
        chosen = allowed.groupby(["asset", "session_id"], as_index=False).first()
        chosen["same_session_conflict"] = chosen["allowed_candidates_in_session"] > 1
        filtered_rows: list[pd.Series] = []
        for _, g in chosen.groupby(["asset", "variant"], sort=False):
            last_exit = -1
            for _, row in g.sort_values(["entry_idx", "setup"]).iterrows():
                if int(row["entry_idx"]) <= last_exit:
                    continue
                filtered_rows.append(row)
                last_exit = int(row["exit_idx"])
        if filtered_rows:
            outputs.append(pd.DataFrame(filtered_rows))
    return pd.concat(outputs, ignore_index=True) if outputs else pd.DataFrame()


def summarize(trades: pd.DataFrame, cost_bps_side: float) -> pd.DataFrame:
    cols = [
        "asset", "variant", "trade_count", "mean_net_return", "total_net_return",
        "positive_session_ratio", "same_session_conflict_rate", "early_fail_rate",
    ]
    if trades.empty:
        return pd.DataFrame(columns=cols)
    t = trades.copy()
    t["net_return"] = t["gross_return"] - (2.0 * cost_bps_side / 10000.0)
    t["is_positive"] = t["net_return"] > 0
    out = (
        t.groupby(["asset", "variant"], as_index=False)
        .agg(
            trade_count=("signal_id", "count"),
            mean_net_return=("net_return", "mean"),
            total_net_return=("net_return", "sum"),
            positive_session_ratio=("is_positive", "mean"),
            same_session_conflict_rate=("same_session_conflict", "mean"),
            early_fail_rate=("early_fail", "mean"),
        )
    )
    overall = (
        t.groupby(["variant"], as_index=False)
        .agg(
            trade_count=("signal_id", "count"),
            mean_net_return=("net_return", "mean"),
            total_net_return=("net_return", "sum"),
            positive_session_ratio=("is_positive", "mean"),
            same_session_conflict_rate=("same_session_conflict", "mean"),
            early_fail_rate=("early_fail", "mean"),
        )
    )
    overall.insert(0, "asset", "ALL")
    return pd.concat([out, overall], ignore_index=True)


def compare_vs_baseline(summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for asset, g in summary.groupby("asset"):
        baseline = g[g["variant"] == "baseline_all_lanes"]
        if baseline.empty:
            continue
        base = baseline.iloc[0]
        base_count = float(base["trade_count"])
        for _, row in g.iterrows():
            retention = float(row["trade_count"]) / base_count if base_count else np.nan
            rows.append(
                {
                    "asset": asset,
                    "variant": row["variant"],
                    "trade_count": row["trade_count"],
                    "trade_count_retention": retention,
                    "total_net_return": row["total_net_return"],
                    "positive_session_ratio": row["positive_session_ratio"],
                    "same_session_conflict_rate": row["same_session_conflict_rate"],
                    "early_fail_rate": row["early_fail_rate"],
                    "delta_total_vs_baseline": float(row["total_net_return"] - base["total_net_return"]),
                    "delta_positive_ratio_vs_baseline": float(row["positive_session_ratio"] - base["positive_session_ratio"]),
                    "delta_conflict_vs_baseline": float(row["same_session_conflict_rate"] - base["same_session_conflict_rate"]),
                    "delta_early_fail_vs_baseline": float(row["early_fail_rate"] - base["early_fail_rate"]),
                }
            )
    return pd.DataFrame(rows)


def build_window_summary(trades: pd.DataFrame, cost_bps_side: float) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["variant", "bucket", "trade_count", "mean_net_return", "positive_session_ratio", "same_session_conflict_rate"])
    t = trades.copy()
    t["net_return"] = t["gross_return"] - (2.0 * cost_bps_side / 10000.0)
    t["is_positive"] = t["net_return"] > 0
    ts = pd.to_datetime(t["entry_ts"], utc=True)
    q1, q2 = ts.quantile([1/3, 2/3])
    t["bucket"] = np.where(ts <= q1, "bucket_1", np.where(ts <= q2, "bucket_2", "bucket_3"))
    out = (
        t.groupby(["variant", "bucket"], as_index=False)
        .agg(
            trade_count=("signal_id", "count"),
            mean_net_return=("net_return", "mean"),
            positive_session_ratio=("is_positive", "mean"),
            same_session_conflict_rate=("same_session_conflict", "mean"),
        )
    )
    return out.sort_values(["variant", "bucket"]).reset_index(drop=True)


def render_html(title: str, compare: pd.DataFrame, summary: pd.DataFrame, windows: pd.DataFrame, session_meta: pd.DataFrame, verdict: str, why: str) -> str:
    body = [
        f"<h1>{escape(title)}</h1>",
        '<p class="muted">最小 clean replication：固定复用 BTC/ETH/SOL 120d 15m cache，把 baseline(all lanes on) / continuation-only / retest-only / one-regime-per-session 四臂放到同一套 session 预算约束里比较，统一 next-bar open + no-overlap + hold 8 bars。</p>',
        '<div class="card"><span class="pill">Run 2</span><span class="pill">Scout Seat</span><span class="pill">reader-facing</span>'
        f'<p><strong>Hard verdict：</strong>{escape(verdict)}</p><p>{escape(why)}</p></div>',
        '<div class="card"><h2>6bps/side 主对照</h2>' + render_table(compare, {
            "trade_count_retention", "total_net_return", "positive_session_ratio", "same_session_conflict_rate",
            "early_fail_rate", "delta_total_vs_baseline", "delta_positive_ratio_vs_baseline",
            "delta_conflict_vs_baseline", "delta_early_fail_vs_baseline"
        }) + '</div>',
        '<div class="card"><h2>完整汇总（含成本档）</h2>' + render_table(summary, {
            "mean_net_return", "total_net_return", "positive_session_ratio", "same_session_conflict_rate", "early_fail_rate"
        }) + '</div>',
        '<div class="card"><h2>时间稳定性（按时间三分桶）</h2>' + render_table(windows, {
            "mean_net_return", "positive_session_ratio", "same_session_conflict_rate"
        }) + '</div>',
        '<div class="card"><h2>session 首 4 根特征分布</h2>' + render_table(session_meta, {
            "continuation_share", "retest_share", "unclear_share", "mean_abs_first4_return", "mean_range_atr"
        }) + '</div>',
    ]
    return f"<!doctype html><html><head><meta charset='utf-8'><title>{escape(title)}</title><style>{CSS}</style></head><body>{''.join(body)}</body></html>"


def update_todo(verdict: str, overall_row: pd.Series, next_step: str) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    anchor = "### Next 3 bot3 runs（当前默认执行顺序）\n\n"
    new_block = (
        f"- **最新补充（2026-03-19 05:07 UTC）**：这轮先继续按 `Run 1 / EMA due-check only` 复核当前 guardrail：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍显示全 desk 无 `due-now / overdue` lane，最近 due 点仍是 `A股三条 lane -> 2026-03-19 07:00 UTC`；`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-19T04:33:36Z` 继续是 `new_closed_trades_appended=0`。因此本轮仍不得回头挤占 `P3 continuity`，而应按板子把 `Rank 79` 的唯一那手最小 clean replication 跑完。\n"
        f"  - 这轮固定复用 `BTC/ETH/SOL 120d 15m` cache，把 `baseline(all lanes on)`、`continuation-only`、`retest-only`、`one-regime-per-session` 四臂统一冻结到 **`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`**。`one-regime-per-session` 只允许用每段 session 前 `4` 根 `15m` 的 opening-range / VWAP / ATR 特征先分成 `continuation / retest / unclear`，再决定该 session 只放 continuation 还是 retest。\n"
        f"  - `6bps/side` 下，`Rank 79 / one-regime-per-session` 的 overall 结果为：`total≈{pct(overall_row['total_net_return'])}`、`retention≈{pct(overall_row['trade_count_retention'])}`、`positive_session_ratio≈{pct(overall_row['positive_session_ratio'])}`、`same_session_conflict_rate≈{pct(overall_row['same_session_conflict_rate'])}`、`delta_total_vs_baseline≈{pct(overall_row['delta_total_vs_baseline'])}`。\n"
        f"  - 因此当前更诚实的 hard verdict 是：**`Rank 79 / one-regime-per-session shared allocation overlay = {verdict}`**。这说明它当前更像 {next_step}。\n"
        f"  - 网页落点：`reports/site/factors/scout_rank79_one_regime_per_session_15m/report.html`、`reports/site/reading/repo_scout/rank79_one_regime_per_session_clean_replication.html`；artifact：`reports/artifacts/scout_rank79_one_regime_per_session_15m/overall_summary.csv`、`compare_vs_baseline.csv`、`window_summary.csv`。\n"
    )
    if verdict == "P2 paper candidate":
        new_block += "  - 因此当前最新 `Next 3` 顺序应更新为：**`Run 1 = EMA due-check only（若仍 waiting_not_due，不得空转）` -> `Run 2 = 若 Rank 79 已升到 P2，则只再给它 1 个真正会改变 verdict 的最小检查（默认优先时间稳定性 / 成本稳定性 二选一），并直接做 promote_to_narrow_paper_pilot / keep_P2 / park 判断` -> `Run 3 = 只有 Rank 79 的这次 P2 检查已完成后，才回到 first-30m impulse quality gate > RS+/RS- asymmetry gate > 其他 fresh source；`P3 continuity` 仍只算低频 sidecar`**。\n\n"
    elif verdict == "keep_P1 / evidence queue":
        new_block += "  - 因此当前最新 `Next 3` 顺序应更新为：**`Run 1 = EMA due-check only（若仍 waiting_not_due，不得空转）` -> `Run 2 = Rank 79 已完成最小 clean replication，但当前只够 keep_P1；下一轮若仍拿它，只允许 1 个真正会改变 verdict 的最小检查（默认优先时间稳定性），否则应切回 first-30m impulse quality gate > RS+/RS- asymmetry gate > 其他 fresh source` -> `Run 3 = 只有 fresh source 这一层也 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing`**。\n\n"
    else:
        new_block += "  - 因此当前最新 `Next 3` 顺序应更新为：**`Run 1 = EMA due-check only（若仍 waiting_not_due，不得空转）` -> `Run 2 = Rank 79 已给出 park / evidence pool 硬结论后，回到 first-30m impulse quality gate > RS+/RS- asymmetry gate > 其他 fresh source` -> `Run 3 = 只有 fresh source 这一层也 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing；`P3 continuity` 仍不得默认抢占 Scout 主资源`**。\n\n"
    if anchor not in text:
        raise SystemExit("Next 3 anchor not found")
    TODO_PATH.write_text(text.replace(anchor, anchor + new_block, 1), encoding="utf-8")


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    frames = {asset: build_frame(asset, symbol) for asset, symbol in ASSETS.items()}
    raw_parts = []
    session_parts = []
    for asset, frame in frames.items():
        for setup in SETUPS:
            raw_parts.append(build_signal_frame(frame, asset, setup))
        session_parts.append(
            frame[["session_id", "session_name", "session_regime", "feature_ready", "session_first4_return", "session_first4_range_atr"]]
            .drop_duplicates("session_id")
            .assign(asset=asset)
        )
    raw_trades = pd.concat(raw_parts, ignore_index=True) if raw_parts else pd.DataFrame()
    raw_trades.to_csv(ART_DIR / "raw_signal_candidates.csv", index=False)
    variant_trades = build_variant_trades(raw_trades)
    variant_trades.to_csv(ART_DIR / "selected_trades.csv", index=False)

    summaries = []
    for cost in COSTS:
        s = summarize(variant_trades, cost)
        s.insert(0, "cost_bps_side", cost)
        summaries.append(s)
    summary = pd.concat(summaries, ignore_index=True) if summaries else pd.DataFrame()
    summary.to_csv(ART_DIR / "overall_summary.csv", index=False)

    compare = compare_vs_baseline(summary[summary["cost_bps_side"] == PRIMARY_COST].copy())
    compare.to_csv(ART_DIR / "compare_vs_baseline.csv", index=False)
    windows = build_window_summary(variant_trades, PRIMARY_COST)
    windows.to_csv(ART_DIR / "window_summary.csv", index=False)

    session_meta_raw = pd.concat(session_parts, ignore_index=True)
    session_meta = (
        session_meta_raw.groupby("asset", as_index=False)
        .agg(
            continuation_share=("session_regime", lambda s: (s == "continuation").mean()),
            retest_share=("session_regime", lambda s: (s == "retest").mean()),
            unclear_share=("session_regime", lambda s: (s == "unclear").mean()),
            mean_abs_first4_return=("session_first4_return", lambda s: np.nanmean(np.abs(s))),
            mean_range_atr=("session_first4_range_atr", "mean"),
        )
    )
    session_meta.to_csv(ART_DIR / "session_meta_summary.csv", index=False)

    primary = compare[(compare["asset"] == "ALL") & (compare["variant"] == PRIMARY_VARIANT)]
    if primary.empty:
        raise SystemExit("primary compare row missing")
    row = primary.iloc[0]
    asset_primary = compare[(compare["asset"] != "ALL") & (compare["variant"] == PRIMARY_VARIANT)].copy()
    positive_assets = int((asset_primary["delta_total_vs_baseline"] > 0).sum())
    overall_improve = float(row["delta_total_vs_baseline"])
    retention = float(row["trade_count_retention"])
    conflict_delta = float(row["delta_conflict_vs_baseline"])

    verdict = "park / evidence pool"
    why = "one-regime-per-session 当前确实降低了同 session 冲突，但若收益改善不够稳定或主要靠砍掉太多交易数换来，就还不够诚实。"
    next_step = "还只是 evidence / backlog，不该继续抢默认 fast lane"
    if positive_assets >= 2 and overall_improve > 0 and retention >= 0.60 and conflict_delta <= -0.10:
        verdict = "P2 paper candidate"
        why = "one-regime-per-session 在至少 2/3 资产上带来正向 delta，同时显著压低同 session 冲突率，且没有把交易数砍到失真，已够升到 P2。"
        next_step = "已足够进入 paper candidate pool，下一轮只该给 1 个真正会改变 verdict 的最小检查"
    elif overall_improve > 0 and retention >= 0.45 and conflict_delta <= -0.05:
        verdict = "keep_P1 / evidence queue"
        why = "one-regime-per-session 有一定 desk 级改善，也确实压低同 session 冲突，但改善还不够跨资产稳定；更诚实的状态是 keep_P1，最多再给 1 个会改变 verdict 的最小检查。"
        next_step = "最多只配再拿 1 个 truly verdict-changing 的最小检查"

    title = "Rank 79 / one-regime-per-session shared allocation overlay"
    html = render_html(title, compare, summary, windows, session_meta, verdict, why)
    (SITE_DIR / "report.html").write_text(html, encoding="utf-8")
    READING_PATH.write_text(html, encoding="utf-8")

    meta = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "verdict": verdict,
        "why": why,
        "positive_assets": positive_assets,
        "overall_delta_total_vs_baseline": overall_improve,
        "retention": retention,
        "delta_conflict_vs_baseline": conflict_delta,
    }
    (ART_DIR / "summary.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    update_todo(verdict, row, next_step)
    print(json.dumps(meta, ensure_ascii=False))


if __name__ == "__main__":
    main()
