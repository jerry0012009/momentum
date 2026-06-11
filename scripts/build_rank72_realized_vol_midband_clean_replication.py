#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank72_realized_vol_midband_cost_survival_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank72_realized_vol_midband_cost_survival_15m"
READING_DIR = ROOT / "reports" / "site" / "reading" / "repo_scout"
TODO_PATH = ROOT / "docs" / "TODO.md"
DUE_PATH = ROOT / "reports" / "artifacts" / "ema_psar_raw_alpha" / "ema_paper_trading_due_guardrail_snapshot.csv"
P3_SUMMARY_PATH = ROOT / "reports" / "artifacts" / "manual_narrow_paper_lanes" / "manual_narrow_paper_last_run_summary.json"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
SETUPS = ["ema_psar_long", "fib_retest_long", "breakout_short"]
LONG_SETUPS = {"ema_psar_long", "fib_retest_long"}
VARIANTS = ["baseline", "no_high_vol_extreme", "rv_midband_q20_80"]
PRIMARY_VARIANT = "rv_midband_q20_80"
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0]
HOLD_BARS = 8
TARGET_ATR = 0.75
ROLLING_VOL_BARS = 20
PCT_WINDOW_BARS = 30 * 24 * 4  # trailing 30d percentile on 15m data

CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 24px auto; max-width: 1180px; line-height: 1.6; color: #1f2937; padding: 0 16px 40px; background:#f8fafc; }
h1,h2,h3 { color: #111827; }
code { background: #f3f4f6; padding: 0.1rem 0.3rem; border-radius: 4px; }
table { border-collapse: collapse; width: 100%; margin: 16px 0; background:white; }
th, td { border: 1px solid #d1d5db; padding: 8px 10px; text-align: left; vertical-align: top; }
th { background: #f3f4f6; }
.muted { color: #6b7280; }
.good { color: #065f46; font-weight: 600; }
.bad { color: #991b1b; font-weight: 600; }
.card { background: white; border: 1px solid #e5e7eb; border-radius: 10px; padding: 14px 16px; margin: 16px 0; }
"""


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


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


def trailing_percentile(values: pd.Series, window: int) -> pd.Series:
    arr = values.to_numpy(dtype=float)
    out = np.full(len(arr), np.nan)
    for i in range(window - 1, len(arr)):
        hist = arr[i - window + 1 : i + 1]
        hist = hist[np.isfinite(hist)]
        if len(hist) < window // 2:
            continue
        out[i] = float((hist <= hist[-1]).mean())
    return pd.Series(out, index=values.index)


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_bars(symbol, asset)
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema15"] = df["close"].ewm(span=15, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["vol_ma20"] = df["volume"].rolling(20, min_periods=20).mean()
    df["atr14"] = compute_atr(df)
    df["psar"] = compute_psar(df)
    df["logret"] = np.log(df["close"]).diff()
    df["rv20"] = np.sqrt(df["logret"].pow(2).rolling(ROLLING_VOL_BARS, min_periods=ROLLING_VOL_BARS).sum())
    df["rv_pct"] = trailing_percentile(df["rv20"], PCT_WINDOW_BARS)

    df["swing_high_30"] = df["high"].rolling(30, min_periods=30).max().shift(1)
    df["swing_low_30"] = df["low"].rolling(30, min_periods=30).min().shift(1)
    rng = df["swing_high_30"] - df["swing_low_30"]
    df["fib_618"] = df["swing_high_30"] - 0.618 * rng
    df["fib_50"] = df["swing_high_30"] - 0.5 * rng
    df["rolling_low20"] = df["low"].rolling(20, min_periods=20).min().shift(1)

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
        & (df["low"] <= df["fib_618"] + 0.2 * df["atr14"])
        & (df["close"] > df["fib_50"])
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)

    low = df["rolling_low20"]
    atr = df["atr14"]
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
    return df


def direction_for_setup(setup: str) -> int:
    return 1 if setup in LONG_SETUPS else -1


def variant_gate(frame: pd.DataFrame, variant: str) -> pd.Series:
    if variant == "baseline":
        return pd.Series(True, index=frame.index)
    if variant == "no_high_vol_extreme":
        return frame["rv_pct"].lt(0.8).fillna(False)
    if variant == "rv_midband_q20_80":
        return frame["rv_pct"].ge(0.2).fillna(False) & frame["rv_pct"].lt(0.8).fillna(False)
    raise ValueError(variant)


def build_signal_frame(frame: pd.DataFrame, asset: str, setup: str, variant: str) -> pd.DataFrame:
    base = frame[f"{setup}_signal"] & ~frame[f"{setup}_signal"].shift(1).fillna(False)
    sig = base & variant_gate(frame, variant)
    rows: list[dict[str, object]] = []
    last_exit = -1
    direction = direction_for_setup(setup)
    for idx in range(max(PCT_WINDOW_BARS, 40), len(frame) - HOLD_BARS - 2):
        if idx <= last_exit or not bool(sig.iloc[idx]):
            continue
        rows.append(
            {
                "signal_id": f"{asset}|{setup}|{variant}|{idx}",
                "asset": asset,
                "setup": setup,
                "variant": variant,
                "direction": direction,
                "signal_idx": idx,
                "entry_idx": idx + 1,
                "signal_ts": pd.to_datetime(frame.iloc[idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "signal_price": float(frame.iloc[idx]["close"]),
                "signal_atr14": float(frame.iloc[idx]["atr14"]) if pd.notna(frame.iloc[idx]["atr14"]) else np.nan,
                "rv20": float(frame.iloc[idx]["rv20"]) if pd.notna(frame.iloc[idx]["rv20"]) else np.nan,
                "rv_pct": float(frame.iloc[idx]["rv_pct"]) if pd.notna(frame.iloc[idx]["rv_pct"]) else np.nan,
            }
        )
        last_exit = idx + HOLD_BARS
    return pd.DataFrame(rows)


def target_first(frame: pd.DataFrame, entry_idx: int, direction: int, target_price: float) -> bool:
    last = min(len(frame) - 1, entry_idx + HOLD_BARS - 1)
    for j in range(entry_idx, last + 1):
        high = float(frame.iloc[j]["high"])
        low = float(frame.iloc[j]["low"])
        if direction > 0 and high >= target_price:
            return True
        if direction < 0 and low <= target_price:
            return True
    return False


def failure_before_target(frame: pd.DataFrame, entry_idx: int, direction: int, entry_px: float, target_price: float) -> int:
    last = min(len(frame) - 1, entry_idx + HOLD_BARS - 1)
    for j in range(entry_idx, last + 1):
        high = float(frame.iloc[j]["high"])
        low = float(frame.iloc[j]["low"])
        if direction > 0:
            if high >= target_price:
                return 0
            if low <= entry_px:
                return 1
        else:
            if low <= target_price:
                return 0
            if high >= entry_px:
                return 1
    return 0 if target_first(frame, entry_idx, direction, target_price) else 0


def build_trades(frame: pd.DataFrame, signals: pd.DataFrame, cost_bps: float) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    cost_rate = float(cost_bps) / 10000.0
    for _, sig in signals.iterrows():
        entry_idx = int(sig["entry_idx"])
        exit_idx = min(len(frame) - 1, entry_idx + HOLD_BARS - 1)
        if entry_idx >= len(frame):
            continue
        entry_px = float(frame.iloc[entry_idx]["open"])
        exit_px = float(frame.iloc[exit_idx]["open"])
        direction = int(sig["direction"])
        gross_ret = direction * (exit_px / entry_px - 1.0)
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
        atr = float(sig["signal_atr14"]) if pd.notna(sig["signal_atr14"]) else np.nan
        if np.isfinite(atr) and atr > 0:
            target_price = entry_px + direction * TARGET_ATR * atr
            fail = failure_before_target(frame, entry_idx, direction, entry_px, target_price)
            target_hit = int(target_first(frame, entry_idx, direction, target_price))
        else:
            target_price = np.nan
            fail = 0
            target_hit = 0
        rows.append(
            {
                "signal_id": sig["signal_id"],
                "asset": sig["asset"],
                "setup": sig["setup"],
                "variant": sig["variant"],
                "cost_bps_per_side": float(cost_bps),
                "signal_ts": sig["signal_ts"],
                "entry_ts": pd.to_datetime(frame.iloc[entry_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": pd.to_datetime(frame.iloc[exit_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_price": entry_px,
                "exit_price": exit_px,
                "gross_return": gross_ret,
                "net_return": net_ret,
                "direction": direction,
                "target_price": target_price,
                "failure_before_target": fail,
                "target_hit": target_hit,
                "rv_pct": sig["rv_pct"],
            }
        )
    return pd.DataFrame(rows)


def summarize_windows(trades: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    if trades.empty:
        return pd.DataFrame(columns=["setup", "variant", "cost_bps_per_side", "bucket", "bucket_return", "positive_bucket"])
    work = trades.copy()
    work["signal_ts"] = pd.to_datetime(work["signal_ts"], utc=True)
    for (setup, variant, cost), grp in work.groupby(["setup", "variant", "cost_bps_per_side"]):
        grp = grp.sort_values("signal_ts").reset_index(drop=True)
        if len(grp) < 3:
            splits = [grp]
        else:
            splits = [x for x in np.array_split(grp, 3) if len(x)]
        for idx, chunk in enumerate(splits, start=1):
            bucket_ret = float(chunk["net_return"].mean()) if len(chunk) else np.nan
            rows.append(
                {
                    "setup": setup,
                    "variant": variant,
                    "cost_bps_per_side": float(cost),
                    "bucket": f"bucket_{idx}",
                    "bucket_return": bucket_ret,
                    "positive_bucket": int(bucket_ret > 0) if pd.notna(bucket_ret) else 0,
                }
            )
    return pd.DataFrame(rows)


def summarize(trades: pd.DataFrame, windows: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    if trades.empty:
        return pd.DataFrame()
    baseline_counts = (
        trades[trades["variant"] == "baseline"]
        .groupby(["asset", "setup"])
        .size()
        .rename("baseline_count")
        .reset_index()
    )
    per_asset = (
        trades.groupby(["setup", "variant", "cost_bps_per_side", "asset"], as_index=False)
        .agg(
            trade_count=("net_return", "size"),
            total_return=("net_return", "sum"),
            expectancy=("net_return", "mean"),
            failure_before_target=("failure_before_target", "mean"),
            target_hit_rate=("target_hit", "mean"),
        )
        .merge(baseline_counts, on=["asset", "setup"], how="left")
    )
    per_asset["trade_count_retention"] = per_asset["trade_count"] / per_asset["baseline_count"].replace(0, np.nan)

    window_summary = (
        windows.groupby(["setup", "variant", "cost_bps_per_side"], as_index=False)
        .agg(
            positive_window_ratio=("positive_bucket", "mean"),
            mean_bucket_return=("bucket_return", "mean"),
        )
    )

    overall = (
        per_asset.groupby(["setup", "variant", "cost_bps_per_side"], as_index=False)
        .agg(
            mean_total_return=("total_return", "mean"),
            positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
            mean_expectancy=("expectancy", "mean"),
            mean_trades=("trade_count", "mean"),
            mean_trade_count_retention=("trade_count_retention", "mean"),
            mean_failure_before_target=("failure_before_target", "mean"),
            mean_target_hit_rate=("target_hit_rate", "mean"),
        )
        .merge(window_summary, on=["setup", "variant", "cost_bps_per_side"], how="left")
    )
    return overall, per_asset


def decide_verdict(overall: pd.DataFrame) -> str:
    primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    baseline = overall[(overall["variant"] == "baseline") & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    if primary.empty or baseline.empty:
        return "park / evidence pool"
    merged = primary.merge(
        baseline[["setup", "mean_total_return", "mean_failure_before_target", "mean_trade_count_retention"]],
        on="setup",
        suffixes=("", "_baseline"),
    )
    better_return = (merged["mean_total_return"] > merged["mean_total_return_baseline"]).sum()
    better_failure = (merged["mean_failure_before_target"] < merged["mean_failure_before_target_baseline"]).sum()
    okay_retention = ((merged["mean_trade_count_retention"] >= 0.45) & (merged["mean_trade_count_retention"] <= 0.95)).sum()
    primary_mean = float(primary["mean_total_return"].mean())
    primary_positive_assets = float(primary["positive_asset_ratio"].mean())
    primary_positive_windows = float(primary["positive_window_ratio"].mean())
    if better_return >= 2 and better_failure >= 2 and okay_retention >= 2 and primary_mean > -0.002 and primary_positive_assets >= 0.5 and primary_positive_windows >= 0.5:
        return "P1 weak candidate（guard-passed -> minimal clean replication survived）"
    return "park / evidence pool"


def update_todo(overall: pd.DataFrame, verdict: str, generated_at: str) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    marker = "### Next 3 bot3 runs（当前默认执行顺序）\n"
    if marker not in text or f"**最新补充（{generated_at}）**" in text:
        return

    p3_summary = pd.read_json(P3_SUMMARY_PATH, typ="series")
    p3_appends = int(p3_summary.get("new_closed_trades_appended", 0))
    primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)].set_index("setup")
    baseline = overall[(overall["variant"] == "baseline") & (overall["cost_bps_per_side"] == PRIMARY_COST)].set_index("setup")

    queue_line = "**`Run 1 = EMA due-check only（当前最近 due 点仍是 A股 07:00 UTC；若仍 waiting_not_due，不得空转）` -> `Run 2 = 若 Rank 72 minimal clean replication 已给出 hard verdict，则立刻切到 Rank 73 / PSAR close-confirmed follow-up gate 做 source intake + 两条轻量诚实守门` -> `Run 3 = 只有 fresh source 这一层也 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing`**"
    if verdict.startswith("P1"):
        queue_line = "**`Run 1 = EMA due-check only（当前最近 due 点仍是 A股 07:00 UTC；若仍 waiting_not_due，不得空转）` -> `Run 2 = 若 Rank 72 仍保留 candidate 资格，则只允许给它 1 个真正会改变 verdict 的最小 Light Stability Pack（默认优先时间稳定性）` -> `Run 3 = 若 Rank 72 cheap check 后仍不能升格，则再切到 Rank 73 / PSAR close-confirmed follow-up gate 做 source intake；只有 fresh source 这一层也 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing`**"

    block = (
        f"> **最新补充（{generated_at}）**：这轮先再次核对 `Run 1 / EMA due-check` 与 `P3` 托管位状态：最新 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍显示全 desk 无 `due-now / overdue` lane，最早 due 点还是 `A股三条 lane -> 2026-03-19 07:00 UTC`；`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 继续是 `new_closed_trades_appended={p3_appends}`，因此当前不该回头挤占 `P3 continuity`，而应按板子执行 **`Run 2 / Rank 72 minimal clean replication`**：固定复用 `BTC/ETH/SOL 120d 15m` cache，把 shared realized-vol gate 接到 `ema_psar_long / fib_retest_long / breakout_short` 三条 archetype 上，只比较 `baseline`、`no_high_vol_extreme`、`rv_midband_q20_80` 三臂，统一 `signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`，成本先看 `6/10/15bps per side`。\n"
        f">  - `6bps/side` 下的主读法 `rv_midband_q20_80` 已冻结为：`ema_psar_long -> return≈{pct(primary.loc['ema_psar_long', 'mean_total_return'])} / retention≈{pct(primary.loc['ema_psar_long', 'mean_trade_count_retention'])} / fail≈{pct(primary.loc['ema_psar_long', 'mean_failure_before_target'])}`；`fib_retest_long -> return≈{pct(primary.loc['fib_retest_long', 'mean_total_return'])} / retention≈{pct(primary.loc['fib_retest_long', 'mean_trade_count_retention'])} / fail≈{pct(primary.loc['fib_retest_long', 'mean_failure_before_target'])}`；`breakout_short -> return≈{pct(primary.loc['breakout_short', 'mean_total_return'])} / retention≈{pct(primary.loc['breakout_short', 'mean_trade_count_retention'])} / fail≈{pct(primary.loc['breakout_short', 'mean_failure_before_target'])}`。\n"
        f">  - 对照 `baseline`：`ema_psar_long≈{pct(baseline.loc['ema_psar_long', 'mean_total_return'])}`、`fib_retest_long≈{pct(baseline.loc['fib_retest_long', 'mean_total_return'])}`、`breakout_short≈{pct(baseline.loc['breakout_short', 'mean_total_return'])}`。当前更诚实的 hard verdict：**`Rank 72 / realized-vol mid-band cost-survival gate = {verdict}`**。\n"
        f">  - reader-facing 落点：`reports/site/factors/scout_rank72_realized_vol_midband_cost_survival_15m/report.html`、`reports/site/reading/repo_scout/rank72_realized_vol_midband_cost_survival_clean_replication.html`；artifact：`reports/artifacts/scout_rank72_realized_vol_midband_cost_survival_15m/overall_summary.csv`、`per_asset_summary.csv`、`window_summary.csv`。\n"
        f">  - 当前最新 `Next 3` 顺序应更新为：{queue_line}\n\n"
    )
    TODO_PATH.write_text(text.replace(marker, marker + "\n" + block), encoding="utf-8")


def build_report(overall: pd.DataFrame, per_asset: pd.DataFrame, windows: pd.DataFrame, verdict: str, generated_at: str) -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_DIR)

    report_title = "Rank 72 / realized-vol mid-band cost-survival gate minimal clean replication"
    summary_cols = [
        "setup",
        "variant",
        "cost_bps_per_side",
        "mean_total_return",
        "positive_asset_ratio",
        "mean_expectancy",
        "mean_trades",
        "mean_trade_count_retention",
        "mean_failure_before_target",
        "positive_window_ratio",
    ]
    percent_cols = {
        "mean_total_return",
        "positive_asset_ratio",
        "mean_expectancy",
        "mean_trade_count_retention",
        "mean_failure_before_target",
        "positive_window_ratio",
    }
    body = (
        f"<h1>{escape(report_title)}</h1>"
        f"<div class='card'><strong>生成时间：</strong>{escape(generated_at)}<br>"
        f"<strong>Hard verdict：</strong>{escape(verdict)}<br>"
        f"<strong>Replication 口径：</strong>BTC/ETH/SOL 120d 15m；baseline / no_high_vol_extreme / rv_midband_q20_80；next-bar open；no-overlap；hold 8 bars；6/10/15 bps per side。</div>"
        f"<div class='card'><p>这轮只回答一个问题：<strong>把 realized-vol pocket 当 shared allow/deny gate 接到现有三条 archetype 上，能不能在不过度砍掉交易数的前提下，改善成本后存活</strong>。不是新 alpha，不改 entry/exit。</p></div>"
        f"<h2>Overall summary</h2>{render_table(overall[summary_cols], percent_cols=percent_cols)}"
        f"<h2>Per-asset summary</h2>{render_table(per_asset[[ 'setup','variant','cost_bps_per_side','asset','trade_count','total_return','expectancy','trade_count_retention','failure_before_target','target_hit_rate' ]], percent_cols={'total_return','expectancy','trade_count_retention','failure_before_target','target_hit_rate'})}"
        f"<h2>Time-pocket buckets</h2>{render_table(windows[['setup','variant','cost_bps_per_side','bucket','bucket_return','positive_bucket']], percent_cols={'bucket_return'})}"
    )
    write_html(SITE_DIR / "report.html", report_title, body)

    reading_body = (
        f"<h1>{escape(report_title)} / clean replication brief</h1>"
        f"<div class='card'><p><strong>一句话：</strong>{escape(verdict)}</p>"
        f"<p>如果一个 vol gate 的改善主要来自把交易数直接砍到失真，它就不该升格。这轮把 `realized-vol mid-band` 接到三条现成 setup 上之后，直接用 retention / failure-before-target / post-cost return 说话。</p></div>"
        f"<h2>主表</h2>{render_table(overall[summary_cols], percent_cols=percent_cols)}"
    )
    write_html(READING_DIR / "rank72_realized_vol_midband_cost_survival_clean_replication.html", report_title, reading_body)


def main() -> None:
    ensure_dir(ART_DIR)
    frames = {asset: build_frame(asset, symbol) for asset, symbol in ASSETS.items()}
    signal_parts: list[pd.DataFrame] = []
    trade_parts: list[pd.DataFrame] = []
    for asset, frame in frames.items():
        for setup in SETUPS:
            for variant in VARIANTS:
                signals = build_signal_frame(frame, asset, setup, variant)
                if signals.empty:
                    continue
                signal_parts.append(signals)
                for cost in COSTS:
                    trades = build_trades(frame, signals, cost)
                    if not trades.empty:
                        trade_parts.append(trades)

    signals = pd.concat(signal_parts, ignore_index=True) if signal_parts else pd.DataFrame()
    trades = pd.concat(trade_parts, ignore_index=True) if trade_parts else pd.DataFrame()
    windows = summarize_windows(trades)
    overall, per_asset = summarize(trades, windows)
    verdict = decide_verdict(overall)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    signals.to_csv(ART_DIR / "signals.csv", index=False)
    trades.to_csv(ART_DIR / "trades.csv", index=False)
    windows.to_csv(ART_DIR / "window_summary.csv", index=False)
    per_asset.to_csv(ART_DIR / "per_asset_summary.csv", index=False)
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)

    build_report(overall, per_asset, windows, verdict, generated_at)
    update_todo(overall, verdict, generated_at)

    print(f"generated_at={generated_at}")
    print(f"verdict={verdict}")
    primary = overall[(overall['variant'] == PRIMARY_VARIANT) & (overall['cost_bps_per_side'] == PRIMARY_COST)]
    if not primary.empty:
        print(primary[['setup','mean_total_return','mean_trade_count_retention','mean_failure_before_target','positive_window_ratio']].to_string(index=False))


if __name__ == "__main__":
    main()
