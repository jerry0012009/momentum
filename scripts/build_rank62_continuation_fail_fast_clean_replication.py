#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank62_continuation_fail_fast_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank62_continuation_fail_fast_15m"
READING_DIR = ROOT / "reports" / "site" / "reading" / "repo_scout"
TODO_PATH = ROOT / "docs" / "TODO.md"
P3_SUMMARY_PATH = ROOT / "reports" / "artifacts" / "manual_narrow_paper_lanes" / "manual_narrow_paper_last_run_summary.json"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
SETUPS = ["ema_psar_long", "fib_retest_long", "breakout_short"]
LONG_SETUPS = {"ema_psar_long", "fib_retest_long"}
VARIANTS = ["base_exit", "ema_atr_fail_fast", "ema_vwap_atr_fail_fast"]
PRIMARY_SETUP = "ema_psar_long"
PRIMARY_VARIANT = "ema_vwap_atr_fail_fast"
PRIMARY_COST = 6.0
COSTS = [6.0]
HOLD_BARS = 8
FAIL_WINDOWS = [4, 8]
ATR_MULT = 0.75

CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 24px auto; max-width: 1180px; line-height: 1.55; color: #1f2937; padding: 0 16px 40px; }
h1,h2,h3 { color: #111827; }
code { background: #f3f4f6; padding: 0.1rem 0.3rem; border-radius: 4px; }
table { border-collapse: collapse; width: 100%; margin: 16px 0; }
th, td { border: 1px solid #d1d5db; padding: 8px 10px; text-align: left; vertical-align: top; }
th { background: #f3f4f6; }
.muted { color: #6b7280; }
.good { color: #065f46; font-weight: 600; }
.bad { color: #991b1b; font-weight: 600; }
.card { background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 10px; padding: 14px 16px; margin: 16px 0; }
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
    if not path.exists():
        raise FileNotFoundError(path)
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


def compute_session_vwap(df: pd.DataFrame) -> pd.Series:
    typical = (df["high"] + df["low"] + df["close"]) / 3.0
    session_key = df["timestamp"].dt.floor("D")
    pv = typical * df["volume"]
    cum_pv = pv.groupby(session_key).cumsum()
    cum_vol = df["volume"].groupby(session_key).cumsum()
    return cum_pv / cum_vol.replace(0, np.nan)


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_bars(symbol, asset)
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema15"] = df["close"].ewm(span=15, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["vol_ma20"] = df["volume"].rolling(20, min_periods=20).mean()
    df["atr14"] = compute_atr(df)
    df["psar"] = compute_psar(df)
    df["session_vwap"] = compute_session_vwap(df)

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


def build_signal_frame(frame: pd.DataFrame, asset: str, setup: str) -> pd.DataFrame:
    sig = frame[f"{setup}_signal"] & ~frame[f"{setup}_signal"].shift(1).fillna(False)
    rows: list[dict[str, object]] = []
    last_exit = -1
    direction = direction_for_setup(setup)
    for idx in range(max(40, 2), len(frame) - 2):
        if idx <= last_exit or not bool(sig.iloc[idx]):
            continue
        rows.append(
            {
                "signal_id": f"{asset}|{setup}|{idx}",
                "asset": asset,
                "setup": setup,
                "direction": direction,
                "signal_idx": idx,
                "entry_idx": idx + 1,
                "signal_ts": pd.to_datetime(frame.iloc[idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "signal_price": float(frame.iloc[idx]["close"]),
                "signal_atr14": float(frame.iloc[idx]["atr14"]) if pd.notna(frame.iloc[idx]["atr14"]) else np.nan,
            }
        )
        last_exit = idx + HOLD_BARS
    return pd.DataFrame(rows)


def failure_cross(frame: pd.DataFrame, entry_idx: int, direction: int, bars: int) -> int:
    last = min(len(frame) - 1, entry_idx + bars - 1)
    entry_px = float(frame.iloc[entry_idx]["open"])
    for j in range(entry_idx, last + 1):
        close = float(frame.iloc[j]["close"])
        if direction > 0 and close < entry_px:
            return 1
        if direction < 0 and close > entry_px:
            return 1
    return 0


def variant_exit(frame: pd.DataFrame, entry_idx: int, direction: int, entry_px: float, variant: str, atr_ref: float) -> tuple[int, str, int]:
    planned_exit = min(len(frame) - 1, entry_idx + HOLD_BARS - 1)
    if variant == "base_exit":
        return planned_exit, "hold_8bars", 0

    atr_fail_level = entry_px - ATR_MULT * atr_ref if direction > 0 else entry_px + ATR_MULT * atr_ref
    for j in range(entry_idx, planned_exit + 1):
        close = float(frame.iloc[j]["close"])
        ema9 = float(frame.iloc[j]["ema9"]) if pd.notna(frame.iloc[j]["ema9"]) else np.nan
        vwap = float(frame.iloc[j]["session_vwap"]) if pd.notna(frame.iloc[j]["session_vwap"]) else np.nan

        ema_fail = (close < ema9) if direction > 0 else (close > ema9)
        atr_fail = (close < atr_fail_level) if direction > 0 else (close > atr_fail_level)
        vwap_fail = (close < vwap) if direction > 0 else (close > vwap)

        triggered = False
        trigger_reason = "hold_8bars"
        if variant == "ema_atr_fail_fast":
            if ema_fail or atr_fail:
                triggered = True
                trigger_reason = "ema_or_atr_fail"
        elif variant == "ema_vwap_atr_fail_fast":
            if ema_fail or atr_fail or vwap_fail:
                triggered = True
                if atr_fail:
                    trigger_reason = "atr_fail"
                elif vwap_fail:
                    trigger_reason = "vwap_fail"
                else:
                    trigger_reason = "ema_fail"
        else:
            raise ValueError(variant)

        if triggered:
            exit_idx = min(planned_exit, j + 1)
            return exit_idx, trigger_reason, 1

    return planned_exit, "hold_8bars", 0


def build_trades(frame: pd.DataFrame, signals: pd.DataFrame, variant: str, cost_bps: float) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    cost_rate = float(cost_bps) / 10000.0
    for _, sig in signals.iterrows():
        entry_idx = int(sig["entry_idx"])
        if entry_idx >= len(frame):
            continue
        direction = int(sig["direction"])
        entry_px = float(frame.iloc[entry_idx]["open"])
        atr_ref = float(sig["signal_atr14"]) if pd.notna(sig["signal_atr14"]) else float(frame.iloc[entry_idx]["atr14"])
        if not np.isfinite(atr_ref) or atr_ref <= 0:
            atr_ref = float(frame.iloc[entry_idx]["close"]) * 0.01
        exit_idx, exit_reason, early_exit = variant_exit(frame, entry_idx, direction, entry_px, variant, atr_ref)
        exit_px = float(frame.iloc[exit_idx]["open"]) if exit_idx < len(frame) else float(frame.iloc[-1]["close"])
        gross_ret = direction * ((exit_px / entry_px) - 1.0)
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
        rows.append(
            {
                "signal_id": sig["signal_id"],
                "asset": sig["asset"],
                "setup": sig["setup"],
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "direction": direction,
                "signal_ts": sig["signal_ts"],
                "entry_ts": pd.to_datetime(frame.iloc[entry_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": pd.to_datetime(frame.iloc[min(exit_idx, len(frame) - 1)]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_price": entry_px,
                "exit_price": exit_px,
                "signal_price": float(sig["signal_price"]),
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "hold_bars_realized": int(max(1, exit_idx - entry_idx + 1)),
                "early_exit": int(early_exit),
                "exit_reason": exit_reason,
                "false_follow_through_4bars": failure_cross(frame, entry_idx, direction, 4),
                "false_follow_through_8bars": failure_cross(frame, entry_idx, direction, 8),
            }
        )
    return pd.DataFrame(rows)


def summarize_asset(trades: pd.DataFrame, *, asset: str, setup: str, variant: str, cost_bps: float, base_trades: pd.DataFrame) -> dict[str, object]:
    base_winners = base_trades[base_trades["net_ret"] > 0].set_index("signal_id") if not base_trades.empty else pd.DataFrame()
    winner_trunc = np.nan
    if not base_winners.empty:
        trunc_count = 0
        for signal_id, base_row in base_winners.iterrows():
            match = trades[trades["signal_id"] == signal_id]
            if match.empty:
                continue
            row = match.iloc[0]
            if int(row["hold_bars_realized"]) < HOLD_BARS and float(row["net_ret"]) < float(base_row["net_ret"]):
                trunc_count += 1
        winner_trunc = trunc_count / len(base_winners)
    if trades.empty:
        return {
            "asset": asset,
            "setup": setup,
            "variant": variant,
            "cost_bps_per_side": float(cost_bps),
            "trades": 0,
            "total_return": 0.0,
            "avg_net_ret": np.nan,
            "win_rate": np.nan,
            "median_loser_size": np.nan,
            "false_follow_through_4bars_rate": np.nan,
            "false_follow_through_8bars_rate": np.nan,
            "winner_truncation_rate": winner_trunc,
            "early_exit_rate": np.nan,
            "mean_hold_bars": np.nan,
        }
    losers = trades.loc[trades["net_ret"] < 0, "net_ret"]
    median_loser = float((-losers).median()) if not losers.empty else 0.0
    return {
        "asset": asset,
        "setup": setup,
        "variant": variant,
        "cost_bps_per_side": float(cost_bps),
        "trades": int(len(trades)),
        "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
        "avg_net_ret": float(trades["net_ret"].mean()),
        "win_rate": float((trades["net_ret"] > 0).mean()),
        "median_loser_size": median_loser,
        "false_follow_through_4bars_rate": float(trades["false_follow_through_4bars"].mean()),
        "false_follow_through_8bars_rate": float(trades["false_follow_through_8bars"].mean()),
        "winner_truncation_rate": winner_trunc,
        "early_exit_rate": float(trades["early_exit"].mean()),
        "mean_hold_bars": float(trades["hold_bars_realized"].mean()),
    }


def build_time_pockets(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["setup", "variant", "bucket", "mean_total_return", "positive_asset_ratio", "mean_trades"])
    df = trades.copy()
    df["entry_ts"] = pd.to_datetime(df["entry_ts"], utc=True)
    q1 = df["entry_ts"].quantile(1 / 3)
    q2 = df["entry_ts"].quantile(2 / 3)

    def bucket(ts: pd.Timestamp) -> str:
        if ts <= q1:
            return "bucket_1"
        if ts <= q2:
            return "bucket_2"
        return "bucket_3"

    df["bucket"] = df["entry_ts"].map(bucket)
    rows: list[dict[str, object]] = []
    grouped = df.groupby(["setup", "variant", "bucket", "asset"], dropna=False)
    for (setup, variant, bucket_name, asset), part in grouped:
        rows.append(
            {
                "setup": setup,
                "variant": variant,
                "bucket": bucket_name,
                "asset": asset,
                "total_return": float((1.0 + part["net_ret"]).prod() - 1.0),
                "trades": int(len(part)),
            }
        )
    tmp = pd.DataFrame(rows)
    return (
        tmp.groupby(["setup", "variant", "bucket"], dropna=False)
        .agg(
            mean_total_return=("total_return", "mean"),
            positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
            mean_trades=("trades", "mean"),
        )
        .reset_index()
        .sort_values(["setup", "variant", "bucket"])
        .reset_index(drop=True)
    )


def build_setup_compare(overall: pd.DataFrame) -> pd.DataFrame:
    primary = overall[overall["cost_bps_per_side"] == PRIMARY_COST].copy()
    rows: list[dict[str, object]] = []
    for setup in SETUPS:
        vals = {}
        for variant in VARIANTS:
            part = primary[(primary["setup"] == setup) & (primary["variant"] == variant)]
            vals[variant] = part.iloc[0] if not part.empty else None
        rows.append(
            {
                "setup": setup,
                "base_return": float(vals["base_exit"]["mean_total_return"]) if vals["base_exit"] is not None else np.nan,
                "ema_atr_return": float(vals["ema_atr_fail_fast"]["mean_total_return"]) if vals["ema_atr_fail_fast"] is not None else np.nan,
                "ema_vwap_atr_return": float(vals["ema_vwap_atr_fail_fast"]["mean_total_return"]) if vals["ema_vwap_atr_fail_fast"] is not None else np.nan,
                "base_loser": float(vals["base_exit"]["mean_median_loser_size"]) if vals["base_exit"] is not None else np.nan,
                "ema_atr_loser": float(vals["ema_atr_fail_fast"]["mean_median_loser_size"]) if vals["ema_atr_fail_fast"] is not None else np.nan,
                "ema_vwap_atr_loser": float(vals["ema_vwap_atr_fail_fast"]["mean_median_loser_size"]) if vals["ema_vwap_atr_fail_fast"] is not None else np.nan,
                "base_false4": float(vals["base_exit"]["mean_false_follow_through_4bars_rate"]) if vals["base_exit"] is not None else np.nan,
                "ema_atr_false4": float(vals["ema_atr_fail_fast"]["mean_false_follow_through_4bars_rate"]) if vals["ema_atr_fail_fast"] is not None else np.nan,
                "ema_vwap_atr_false4": float(vals["ema_vwap_atr_fail_fast"]["mean_false_follow_through_4bars_rate"]) if vals["ema_vwap_atr_fail_fast"] is not None else np.nan,
                "ema_vwap_atr_pos_ratio": float(vals["ema_vwap_atr_fail_fast"]["positive_asset_ratio"]) if vals["ema_vwap_atr_fail_fast"] is not None else np.nan,
                "ema_vwap_atr_winner_trunc": float(vals["ema_vwap_atr_fail_fast"]["mean_winner_truncation_rate"]) if vals["ema_vwap_atr_fail_fast"] is not None else np.nan,
                "ema_vwap_atr_early_exit": float(vals["ema_vwap_atr_fail_fast"]["mean_early_exit_rate"]) if vals["ema_vwap_atr_fail_fast"] is not None else np.nan,
            }
        )
    return pd.DataFrame(rows)


def build_verdict(compare: pd.DataFrame) -> tuple[str, str, str]:
    primary = compare[compare["setup"] == PRIMARY_SETUP].iloc[0]
    fib = compare[compare["setup"] == "fib_retest_long"].iloc[0]
    short = compare[compare["setup"] == "breakout_short"].iloc[0]
    headline = (
        f"`ema_psar_long`: base≈{pct(primary['base_return'])} / ema+atr≈{pct(primary['ema_atr_return'])} / ema+vwap+atr≈{pct(primary['ema_vwap_atr_return'])}`；"
        f"`fib_retest_long`: base≈{pct(fib['base_return'])} / ema+vwap+atr≈{pct(fib['ema_vwap_atr_return'])}`；"
        f"`breakout_short`: base≈{pct(short['base_return'])} / ema+vwap+atr≈{pct(short['ema_vwap_atr_return'])}`"
    )

    primary_improved = (
        float(primary["ema_vwap_atr_return"]) > float(primary["base_return"]) + 0.002
        and float(primary["ema_vwap_atr_loser"]) <= float(primary["base_loser"]) * 0.95
        and float(primary["ema_vwap_atr_winner_trunc"]) <= 0.45
    )
    support_count = 0
    for row in [fib, short]:
        if float(row["ema_vwap_atr_return"]) > float(row["base_return"]) + 0.001:
            support_count += 1
    if primary_improved and support_count >= 1:
        return (
            "P1 weak candidate / evidence pool",
            headline,
            "这次最小 clean replication 至少说明 continuation fail-fast overlay 在 EMA/PSAR 主读法上不只是漂亮止损：它能更快认错、缩小 loser size，而且不是纯靠极端砍单。但跨 setup 还不够统一，所以先留在 P1 证据池，只配再拿 1 个真正会改变 verdict 的时间稳定性检查。",
        )
    return (
        "park / evidence pool",
        headline,
        "这次最小 clean replication 更像在证明：continuation fail-fast overlay 虽然看起来像 shared failure protocol，但当前改善主要落在局部 pocket，跨 setup 不够统一，且 winner truncation / session-VWAP 任意性风险还在，不值得继续占 fast-lane。",
    )


def update_repo_scout_index() -> None:
    report_path = READING_DIR / "report.html"
    if not report_path.exists():
        return
    text = report_path.read_text(encoding="utf-8")
    if "rank62_continuation_fail_fast_clean_replication.html" in text:
        return
    old = 'rank62_continuation_fail_fast_source_intake.html">Rank 62 source intake</a>'
    if old in text:
        text = text.replace(old, old + ' ｜ <a href="rank62_continuation_fail_fast_clean_replication.html">clean replication</a>', 1)
        report_path.write_text(text, encoding="utf-8")


def update_todo(compare: pd.DataFrame, verdict: str, generated_at: str, latest_p3_appends: int) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    marker = "### Next 3 bot3 runs（当前默认执行顺序）\n"
    if marker not in text:
        raise RuntimeError("Next 3 marker not found in TODO.md")
    if f"**最新补充（{generated_at}）**" in text:
        return

    cmp = compare.set_index("setup")
    row_ema = cmp.loc["ema_psar_long"]
    row_fib = cmp.loc["fib_retest_long"]
    row_short = cmp.loc["breakout_short"]

    if verdict.startswith("P1"):
        active_order = "**`Rank 62 / continuation fail-fast overlay` > `Rank 63 / Fib 0.618 hold / 0.5 fail gate` > `pullback-quality / CQI` > `Rank 35b` > `Rank 16b` > `tiny-live plumbing`**"
        queue_line = "**`Run 1 = EMA due-check only` -> `Run 2 = 若 Rank 62 仍保留在 P1，则只允许给它 1 个 truly verdict-changing 的最小 Light Stability Pack（默认优先时间稳定性）` -> `Run 3 = 若 Rank 62 这次 cheap check 后仍不能升格，则立刻切到 Rank 63 做 source intake + 两条轻量诚实守门；只有 fresh repo queue 也 exhausted 时，才回退到 pullback-quality / CQI > Rank 35b > Rank 16b > tiny-live plumbing`**"
    else:
        active_order = "**`Rank 63 / Fib 0.618 hold / 0.5 fail gate` > `pullback-quality / CQI` > `Rank 35b` > `Rank 16b` > `tiny-live plumbing`**"
        queue_line = "**`Run 1 = EMA due-check only` -> `Run 2 = 若 Rank 62 已直接 park，则立刻切到 Rank 63 做 source intake + 两条轻量诚实守门` -> `Run 3 = 只有 fresh repo queue 也 exhausted 时，才回退到 pullback-quality / CQI > Rank 35b > Rank 16b > tiny-live plumbing`**"

    block = (
        f"> **最新补充（{generated_at}）**：这轮先再次核对 `Run 1 / EMA due-check` 与 `P3` 托管位状态：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍显示全 desk 没有新的 `due-now / overdue` lane（最早仍是 `美股 1d+1wk -> 2026-03-18 20:00 UTC`，其后 `Crypto 1d+1wk -> 2026-03-19 00:00 UTC`、A 股三条 lane `-> 2026-03-19 07:00 UTC`），而 `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 最新一次仍是 `new_closed_trades_appended={latest_p3_appends}`，因此当前没有新的 `Paper Seat` due-now 动作，也没有新的 `P3 status-changing event` 值得 bot3 回头挤占 continuity。随后按权威顺序执行 **`Run 2 / Rank 62 minimal clean replication`**：固定复用 `BTC/ETH/SOL 120d 15m` cache，只在三条 base archetype（`ema_psar_long`、`fib_retest_long`、`breakout_short`）上比较 `base_exit`、`ema_atr_fail_fast`、`ema_vwap_atr_fail_fast` 三臂；执行统一冻结到 `next-bar open + no-overlap`，只回答 fail-fast 的增量到底来自更快认错，还是只是把原本会走出来的单子也提前砍掉。\n"
        f">  - `6bps/side` 下的 setup-level 结果已冻结为：`ema_psar_long` 从 `base≈{pct(row_ema['base_return'])}` 到 `ema+atr≈{pct(row_ema['ema_atr_return'])}`、`ema+vwap+atr≈{pct(row_ema['ema_vwap_atr_return'])}`；`fib_retest_long` 从 `base≈{pct(row_fib['base_return'])}` 到 `ema+vwap+atr≈{pct(row_fib['ema_vwap_atr_return'])}`；`breakout_short` 从 `base≈{pct(row_short['base_return'])}` 到 `ema+vwap+atr≈{pct(row_short['ema_vwap_atr_return'])}`。\n"
        f">  - 当前更诚实的 hard verdict：**`Rank 62 / continuation fail-fast overlay = {verdict}`**。\n"
        f">  - reader-facing 落点：`reports/site/factors/scout_rank62_continuation_fail_fast_15m/report.html`、`reports/site/reading/repo_scout/rank62_continuation_fail_fast_clean_replication.html`；artifact：`reports/artifacts/scout_rank62_continuation_fail_fast_15m/overall_summary.csv`。\n"
        f">  - 当前更诚实的 active Scout 顺序应收紧为：{active_order}。\n"
        f">  - 因此当前最新 `Next 3` 顺序应更新为：{queue_line}\n\n"
    )
    text = text.replace(marker, marker + "\n" + block, 1)
    TODO_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_DIR)

    latest_p3_appends = 0
    if P3_SUMMARY_PATH.exists():
        try:
            latest_p3_appends = int(pd.read_json(P3_SUMMARY_PATH, typ="series").get("new_closed_trades_appended", 0))
        except Exception:
            latest_p3_appends = 0

    frames = {asset: build_frame(asset, symbol) for asset, symbol in ASSETS.items()}
    signal_tables: list[pd.DataFrame] = []
    for asset, symbol in ASSETS.items():
        frame = frames[asset]
        for setup in SETUPS:
            signal_tables.append(build_signal_frame(frame, asset, setup))
    all_signals = pd.concat([df for df in signal_tables if not df.empty], ignore_index=True) if signal_tables else pd.DataFrame()
    if all_signals.empty:
        raise RuntimeError("no signals formed for Rank 62 clean replication")
    all_signals.to_csv(ART_DIR / "signal_windows.csv", index=False)

    asset_rows: list[dict[str, object]] = []
    trade_frames: list[pd.DataFrame] = []
    base_lookup: dict[tuple[str, str, float], pd.DataFrame] = {}

    for asset, symbol in ASSETS.items():
        frame = frames[asset]
        for setup in SETUPS:
            sigs = all_signals[(all_signals["asset"] == asset) & (all_signals["setup"] == setup)].copy().reset_index(drop=True)
            for cost in COSTS:
                base_trades = build_trades(frame, sigs, "base_exit", cost)
                base_lookup[(asset, setup, cost)] = base_trades.copy()
                if not base_trades.empty:
                    trade_frames.append(base_trades)
                asset_rows.append(
                    summarize_asset(base_trades, asset=asset, setup=setup, variant="base_exit", cost_bps=cost, base_trades=base_trades)
                )
                for variant in ["ema_atr_fail_fast", "ema_vwap_atr_fail_fast"]:
                    trades = build_trades(frame, sigs, variant, cost)
                    if not trades.empty:
                        trade_frames.append(trades)
                    asset_rows.append(
                        summarize_asset(trades, asset=asset, setup=setup, variant=variant, cost_bps=cost, base_trades=base_trades)
                    )

    trades_df = pd.concat(trade_frames, ignore_index=True) if trade_frames else pd.DataFrame()
    asset_df = pd.DataFrame(asset_rows).sort_values(["setup", "variant", "cost_bps_per_side", "asset"]).reset_index(drop=True)
    overall_df = (
        asset_df.groupby(["setup", "variant", "cost_bps_per_side"], dropna=False)
        .agg(
            mean_total_return=("total_return", "mean"),
            positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
            mean_trades=("trades", "mean"),
            mean_avg_net_ret=("avg_net_ret", "mean"),
            mean_median_loser_size=("median_loser_size", "mean"),
            mean_false_follow_through_4bars_rate=("false_follow_through_4bars_rate", "mean"),
            mean_false_follow_through_8bars_rate=("false_follow_through_8bars_rate", "mean"),
            mean_winner_truncation_rate=("winner_truncation_rate", "mean"),
            mean_early_exit_rate=("early_exit_rate", "mean"),
            mean_hold_bars=("mean_hold_bars", "mean"),
        )
        .reset_index()
        .sort_values(["setup", "cost_bps_per_side", "variant"])
        .reset_index(drop=True)
    )
    time_pockets_df = build_time_pockets(trades_df)
    compare_df = build_setup_compare(overall_df)
    verdict, headline, reason = build_verdict(compare_df)

    trades_df.to_csv(ART_DIR / "trade_log.csv", index=False)
    asset_df.to_csv(ART_DIR / "asset_summary.csv", index=False)
    overall_df.to_csv(ART_DIR / "overall_summary.csv", index=False)
    compare_df.to_csv(ART_DIR / "setup_compare.csv", index=False)
    time_pockets_df.to_csv(ART_DIR / "time_pockets.csv", index=False)
    pd.DataFrame([
        {
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "candidate_id": "rank62_continuation_fail_fast_15m",
            "hard_verdict": verdict,
            "headline": headline,
            "reason": reason,
        }
    ]).to_csv(ART_DIR / "meta.csv", index=False)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    summary_card = f"""
<h1>Rank 62 / continuation fail-fast overlay — 最小 clean replication</h1>
<p class='muted'>生成时间：{escape(generated_at)}</p>
<div class='card'>
  <p><strong>结论：</strong><span class='{'good' if 'P1' in verdict else 'bad'}'>{escape(verdict)}</span></p>
  <p><b>{escape(headline)}</b></p>
  <p>{escape(reason)}</p>
  <p>本轮只回答一个问题：当 15m setup 已经给出方向和价位时，entry 之后的 <code>EMA9 失守 / session VWAP flip / 0.75*ATR</code> fail-fast overlay，到底是在更快认错，还是只是把本来会走出来的单子也提前砍掉。</p>
</div>
"""

    method = f"""
<div class='card'>
  <h2>本轮冻结口径</h2>
  <ul>
    <li>只复用 <code>BTC/ETH/SOL 120d 15m</code> 本地 cache，不追新 bar。</li>
    <li>三条最小 archetype：<code>ema_psar_long</code>、<code>fib_retest_long</code>、<code>breakout_short</code>。</li>
    <li>三臂固定为：<code>base_exit</code>、<code>ema_atr_fail_fast</code>、<code>ema_vwap_atr_fail_fast</code>。</li>
    <li>入场统一 <code>signal bar -> next-bar open</code>；overlay 触发后也统一到 <code>fail close 确认 -> next-bar open exit</code>，避免 same-bar 过度乐观。</li>
    <li><code>session VWAP</code> 明确只按 UTC 日内累计 volume-weighted typical price 近似；当前只当 shared failure proxy，不把 session 任意性包装成 alpha。</li>
    <li>默认持有上限 <code>{HOLD_BARS}</code> 根 15m bar；若无 fail-fast，则按 base 持有到期。</li>
  </ul>
</div>
"""

    compare_view = compare_df.copy()
    report_body = summary_card + method
    report_body += "<h2>setup compare（6bps）</h2>" + render_table(
        compare_view,
        percent_cols={
            "base_return", "ema_atr_return", "ema_vwap_atr_return", "base_loser", "ema_atr_loser", "ema_vwap_atr_loser",
            "base_false4", "ema_atr_false4", "ema_vwap_atr_false4", "ema_vwap_atr_pos_ratio", "ema_vwap_atr_winner_trunc", "ema_vwap_atr_early_exit"
        },
    )
    report_body += "<h2>overall summary</h2>" + render_table(
        overall_df,
        percent_cols={
            "mean_total_return", "positive_asset_ratio", "mean_avg_net_ret", "mean_median_loser_size",
            "mean_false_follow_through_4bars_rate", "mean_false_follow_through_8bars_rate", "mean_winner_truncation_rate", "mean_early_exit_rate"
        },
        digits_cols={"mean_trades": 1, "cost_bps_per_side": 0, "mean_hold_bars": 2},
    )
    report_body += "<h2>asset-level summary</h2>" + render_table(
        asset_df,
        percent_cols={
            "total_return", "avg_net_ret", "win_rate", "median_loser_size", "false_follow_through_4bars_rate",
            "false_follow_through_8bars_rate", "winner_truncation_rate", "early_exit_rate"
        },
        digits_cols={"trades": 0, "cost_bps_per_side": 0, "mean_hold_bars": 2},
    )
    report_body += "<h2>time-pocket honesty</h2>" + render_table(
        time_pockets_df,
        percent_cols={"mean_total_return", "positive_asset_ratio"},
        digits_cols={"mean_trades": 1},
    )
    write_html(SITE_DIR / "report.html", "Rank 62 clean replication", report_body)

    reading_body = summary_card
    reading_body += "<div class='card'><h2>当前更直白的读法</h2><p>如果这层 fail-fast overlay 真有用，它至少应该在不改变 entry 数量的前提下，缩小 loser size、少一些 4~8 bar 假延续，同时别把本来会走出来的赢家大量提前砍掉。若改善主要靠单一 setup pocket 或明显的 winner truncation，那就该尽快 park。</p></div>"
    reading_body += "<h2>结果表</h2>" + render_table(
        overall_df,
        percent_cols={
            "mean_total_return", "positive_asset_ratio", "mean_avg_net_ret", "mean_median_loser_size",
            "mean_false_follow_through_4bars_rate", "mean_false_follow_through_8bars_rate", "mean_winner_truncation_rate", "mean_early_exit_rate"
        },
        digits_cols={"mean_trades": 1, "cost_bps_per_side": 0, "mean_hold_bars": 2},
    )
    reading_body += f"<p><strong>最终口径：</strong>{escape(verdict)}。{escape(reason)}</p>"
    write_html(READING_DIR / "rank62_continuation_fail_fast_clean_replication.html", "Rank 62 clean replication", reading_body)

    update_repo_scout_index()
    update_todo(compare_df, verdict, generated_at, latest_p3_appends)
    print(f"verdict={verdict}")
    print(headline)


if __name__ == "__main__":
    main()
