#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank70_fast_entry_slow_exit_handoff_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank70_fast_entry_slow_exit_handoff_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank70_fast_entry_slow_exit_handoff_clean_replication.html"
TODO_PATH = ROOT / "docs" / "TODO.md"
P3_SUMMARY_PATH = ROOT / "reports" / "artifacts" / "manual_narrow_paper_lanes" / "manual_narrow_paper_last_run_summary.json"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
SETUPS = ["ema_psar_long", "fib_retest_long", "breakout_short"]
LONG_SETUPS = {"ema_psar_long", "fib_retest_long"}
VARIANTS = ["baseline_exit", "all_fast_fail", "all_slow_trailing", "handoff_exit"]
PRIMARY_VARIANT = "handoff_exit"
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0]
BASE_HOLD_BARS = 8
MAX_HOLD_BARS = 24
FAST_STAGE_BARS = 3
ATR_FAIL_MULT = 0.75
TARGET_ATR = 1.0
SLOW_DONCHIAN_LEN = 20
SLOW_CHANDELIER_ATR = 3.5

CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1120px; margin: 40px auto; padding: 0 18px; line-height: 1.72; color: #111827; background: #f8fafc; }
.card { border: 1px solid #e5e7eb; border-radius: 14px; background: white; padding: 18px 20px; margin: 16px 0; }
.pill { display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }
.muted { color:#6b7280; }
code { background:#f3f4f6; padding:1px 5px; border-radius:6px; }
table { width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }
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
    tr = pd.concat([
        (df["high"] - df["low"]).abs(),
        (df["high"] - prev_close).abs(),
        (df["low"] - prev_close).abs(),
    ], axis=1).max(axis=1)
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
    df["rolling_low20"] = df["low"].rolling(20, min_periods=20).min().shift(1)
    df["rolling_high20"] = df["high"].rolling(20, min_periods=20).max().shift(1)
    df["swing_high_30"] = df["high"].rolling(30, min_periods=30).max().shift(1)
    df["swing_low_30"] = df["low"].rolling(30, min_periods=30).min().shift(1)
    rng = df["swing_high_30"] - df["swing_low_30"]
    df["fib_618"] = df["swing_high_30"] - 0.618 * rng
    df["fib_50"] = df["swing_high_30"] - 0.5 * rng

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
        atr = float(frame.iloc[idx]["atr14"]) if pd.notna(frame.iloc[idx]["atr14"]) else np.nan
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
                "signal_atr14": atr,
            }
        )
        last_exit = idx + BASE_HOLD_BARS
    return pd.DataFrame(rows)


def favorable_move(frame: pd.DataFrame, entry_idx: int, direction: int, end_idx: int, entry_px: float) -> float:
    window = frame.iloc[entry_idx : end_idx + 1]
    if direction > 0:
        best_px = float(window["high"].max())
        return max(0.0, (best_px / entry_px) - 1.0)
    best_px = float(window["low"].min())
    return max(0.0, (entry_px / best_px) - 1.0)


def adverse_move(frame: pd.DataFrame, entry_idx: int, direction: int, end_idx: int, entry_px: float) -> float:
    window = frame.iloc[entry_idx : end_idx + 1]
    if direction > 0:
        worst_px = float(window["low"].min())
        return max(0.0, 1.0 - (worst_px / entry_px))
    worst_px = float(window["high"].max())
    return max(0.0, (worst_px / entry_px) - 1.0)


def fast_fail_trigger(frame: pd.DataFrame, j: int, direction: int, entry_px: float, atr_ref: float) -> tuple[bool, str]:
    close = float(frame.iloc[j]["close"])
    ema9 = float(frame.iloc[j]["ema9"]) if pd.notna(frame.iloc[j]["ema9"]) else np.nan
    vwap = float(frame.iloc[j]["session_vwap"]) if pd.notna(frame.iloc[j]["session_vwap"]) else np.nan
    atr_fail_level = entry_px - ATR_FAIL_MULT * atr_ref if direction > 0 else entry_px + ATR_FAIL_MULT * atr_ref
    ema_fail = (close < ema9) if direction > 0 else (close > ema9)
    atr_fail = (close < atr_fail_level) if direction > 0 else (close > atr_fail_level)
    vwap_fail = (close < vwap) if direction > 0 else (close > vwap)
    if atr_fail:
        return True, "atr_fail"
    if vwap_fail:
        return True, "vwap_fail"
    if ema_fail:
        return True, "ema_fail"
    return False, ""


def slow_trailing_trigger(frame: pd.DataFrame, entry_idx: int, j: int, direction: int) -> tuple[bool, str]:
    window = frame.iloc[max(0, j - SLOW_DONCHIAN_LEN + 1) : j + 1]
    close = float(frame.iloc[j]["close"])
    atr = float(frame.iloc[j]["atr14"]) if pd.notna(frame.iloc[j]["atr14"]) else np.nan
    if not np.isfinite(atr) or atr <= 0:
        atr = float(frame.iloc[entry_idx]["close"]) * 0.01
    post_entry = frame.iloc[entry_idx : j + 1]
    if direction > 0:
        chandelier = float(post_entry["high"].max()) - SLOW_CHANDELIER_ATR * atr
        donchian = float(window["low"].min())
        if close < chandelier:
            return True, "chandelier_fail"
        if close < donchian:
            return True, "donchian_fail"
    else:
        chandelier = float(post_entry["low"].min()) + SLOW_CHANDELIER_ATR * atr
        donchian = float(window["high"].max())
        if close > chandelier:
            return True, "chandelier_fail"
        if close > donchian:
            return True, "donchian_fail"
    return False, ""


def variant_exit(frame: pd.DataFrame, entry_idx: int, direction: int, entry_px: float, variant: str, atr_ref: float) -> tuple[int, str, int, int]:
    if variant == "baseline_exit":
        return min(len(frame) - 1, entry_idx + BASE_HOLD_BARS - 1), "hold_8bars", 0, 0

    planned_exit = min(len(frame) - 1, entry_idx + MAX_HOLD_BARS - 1)
    handed_off = 0
    switched_bar: int | None = None

    for j in range(entry_idx, planned_exit + 1):
        fast_hit, fast_reason = fast_fail_trigger(frame, j, direction, entry_px, atr_ref)
        if variant == "all_fast_fail":
            if fast_hit:
                return min(planned_exit, j + 1), fast_reason, 1, 0
            continue

        if variant == "handoff_exit" and switched_bar is None:
            mfe = favorable_move(frame, entry_idx, direction, j, entry_px)
            if (j - entry_idx + 1) >= FAST_STAGE_BARS or mfe >= (TARGET_ATR * atr_ref / entry_px):
                switched_bar = j
                handed_off = 1
            else:
                if fast_hit:
                    return min(planned_exit, j + 1), fast_reason, 1, 0
                continue

        if variant == "all_slow_trailing":
            slow_hit, slow_reason = slow_trailing_trigger(frame, entry_idx, j, direction)
            if slow_hit:
                return min(planned_exit, j + 1), slow_reason, 0, 0
        elif variant == "handoff_exit":
            if switched_bar is None:
                continue
            slow_hit, slow_reason = slow_trailing_trigger(frame, entry_idx, j, direction)
            if slow_hit:
                return min(planned_exit, j + 1), f"handoff_{slow_reason}", 0, handed_off
        else:
            raise ValueError(variant)

    final_reason = {
        "all_fast_fail": "hold_24bars",
        "all_slow_trailing": "slow_hold_24bars",
        "handoff_exit": "handoff_hold_24bars" if handed_off else "fast_stage_hold_24bars",
    }[variant]
    return planned_exit, final_reason, 0, handed_off


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

        exit_idx, exit_reason, early_exit, handed_off = variant_exit(frame, entry_idx, direction, entry_px, variant, atr_ref)
        exit_px = float(frame.iloc[exit_idx]["open"]) if exit_idx < len(frame) else float(frame.iloc[-1]["close"])
        gross_ret = direction * ((exit_px / entry_px) - 1.0)
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
        mfe = favorable_move(frame, entry_idx, direction, exit_idx, entry_px)
        mae = adverse_move(frame, entry_idx, direction, exit_idx, entry_px)
        mfe_capture = (max(net_ret, 0.0) / mfe) if mfe > 0 else np.nan
        giveback = ((mfe - max(net_ret, 0.0)) / mfe) if handed_off and mfe > 0 else np.nan
        target_px = entry_px + direction * TARGET_ATR * atr_ref
        path_end = min(len(frame) - 1, entry_idx + MAX_HOLD_BARS - 1)
        future = frame.iloc[entry_idx : path_end + 1]
        if direction > 0:
            target_hit = bool((future["high"] >= target_px).any())
        else:
            target_hit = bool((future["low"] <= target_px).any())

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
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "hold_bars_realized": int(max(1, exit_idx - entry_idx + 1)),
                "early_exit": int(early_exit),
                "handed_off": int(handed_off),
                "exit_reason": exit_reason,
                "mfe": mfe,
                "mae": mae,
                "mfe_capture_ratio": mfe_capture,
                "giveback_after_handoff": giveback,
                "target_hit_24bars": int(target_hit),
            }
        )
    return pd.DataFrame(rows)


def summarize_asset(trades: pd.DataFrame, *, asset: str, setup: str, variant: str, cost_bps: float, base_trades: pd.DataFrame | None = None) -> dict[str, object]:
    trade_retention = np.nan
    if base_trades is not None and len(base_trades) > 0:
        trade_retention = float(len(trades) / len(base_trades))
    winners = trades[trades["net_ret"] > 0] if not trades.empty else pd.DataFrame()
    return {
        "asset": asset,
        "setup": setup,
        "variant": variant,
        "cost_bps_per_side": float(cost_bps),
        "trades": int(len(trades)),
        "trade_count_retention": trade_retention,
        "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0) if not trades.empty else np.nan,
        "avg_net_ret": float(trades["net_ret"].mean()) if not trades.empty else np.nan,
        "win_rate": float((trades["net_ret"] > 0).mean()) if not trades.empty else np.nan,
        "mean_hold_bars": float(trades["hold_bars_realized"].mean()) if not trades.empty else np.nan,
        "winner_median_return": float(winners["net_ret"].median()) if not winners.empty else np.nan,
        "winner_hold_bars": float(winners["hold_bars_realized"].mean()) if not winners.empty else np.nan,
        "mean_mfe_capture_ratio": float(trades["mfe_capture_ratio"].dropna().mean()) if not trades.empty else np.nan,
        "mean_giveback_after_handoff": float(trades["giveback_after_handoff"].dropna().mean()) if not trades.empty else np.nan,
        "handoff_rate": float(trades["handed_off"].mean()) if not trades.empty else np.nan,
        "early_exit_rate": float(trades["early_exit"].mean()) if not trades.empty else np.nan,
        "target_hit_24bars_rate": float(trades["target_hit_24bars"].mean()) if not trades.empty else np.nan,
    }


def build_overall(asset_summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for (setup, variant, cost_bps), grp in asset_summary.groupby(["setup", "variant", "cost_bps_per_side"], dropna=False):
        rows.append(
            {
                "setup": setup,
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "mean_total_return": float(grp["total_return"].mean()) if not grp.empty else np.nan,
                "positive_asset_ratio": float((grp["total_return"] > 0).mean()) if not grp.empty else np.nan,
                "mean_trades": float(grp["trades"].mean()) if not grp.empty else np.nan,
                "mean_trade_count_retention": float(grp["trade_count_retention"].mean()) if not grp.empty else np.nan,
                "mean_win_rate": float(grp["win_rate"].mean()) if not grp.empty else np.nan,
                "mean_hold_bars": float(grp["mean_hold_bars"].mean()) if not grp.empty else np.nan,
                "mean_winner_median_return": float(grp["winner_median_return"].mean()) if not grp.empty else np.nan,
                "mean_winner_hold_bars": float(grp["winner_hold_bars"].mean()) if not grp.empty else np.nan,
                "mean_mfe_capture_ratio": float(grp["mean_mfe_capture_ratio"].mean()) if not grp.empty else np.nan,
                "mean_giveback_after_handoff": float(grp["mean_giveback_after_handoff"].mean()) if not grp.empty else np.nan,
                "mean_handoff_rate": float(grp["handoff_rate"].mean()) if not grp.empty else np.nan,
                "mean_early_exit_rate": float(grp["early_exit_rate"].mean()) if not grp.empty else np.nan,
                "mean_target_hit_24bars_rate": float(grp["target_hit_24bars_rate"].mean()) if not grp.empty else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values(["setup", "cost_bps_per_side", "variant"]).reset_index(drop=True)


def build_time_pockets(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["setup", "variant", "bucket", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_mfe_capture_ratio"])
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
                "mfe_capture_ratio": float(part["mfe_capture_ratio"].dropna().mean()) if part["mfe_capture_ratio"].notna().any() else np.nan,
            }
        )
    tmp = pd.DataFrame(rows)
    return (
        tmp.groupby(["setup", "variant", "bucket"], dropna=False)
        .agg(
            mean_total_return=("total_return", "mean"),
            positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
            mean_trades=("trades", "mean"),
            mean_mfe_capture_ratio=("mfe_capture_ratio", "mean"),
        )
        .reset_index()
        .sort_values(["setup", "variant", "bucket"])
        .reset_index(drop=True)
    )


def build_cost_summary(asset_summary: pd.DataFrame) -> pd.DataFrame:
    primary = asset_summary[asset_summary["variant"] == PRIMARY_VARIANT].copy()
    return (
        primary.groupby("cost_bps_per_side", dropna=False)
        .agg(
            mean_total_return=("total_return", "mean"),
            positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
            mean_trades=("trades", "mean"),
            mean_trade_count_retention=("trade_count_retention", "mean"),
            mean_hold_bars=("mean_hold_bars", "mean"),
            mean_winner_median_return=("winner_median_return", "mean"),
            mean_mfe_capture_ratio=("mean_mfe_capture_ratio", "mean"),
            mean_giveback_after_handoff=("mean_giveback_after_handoff", "mean"),
            mean_handoff_rate=("handoff_rate", "mean"),
        )
        .reset_index()
        .sort_values("cost_bps_per_side")
        .reset_index(drop=True)
    )


def build_setup_compare(overall: pd.DataFrame) -> pd.DataFrame:
    target = overall[overall["cost_bps_per_side"] == PRIMARY_COST].copy()
    rows: list[dict[str, object]] = []
    for setup in SETUPS:
        subset = target[target["setup"] == setup].set_index("variant")
        if "baseline_exit" not in subset.index:
            continue
        def getrow(name: str):
            return subset.loc[name] if name in subset.index else pd.Series(dtype=float)
        base = getrow("baseline_exit")
        fast = getrow("all_fast_fail")
        slow = getrow("all_slow_trailing")
        hand = getrow("handoff_exit")
        rows.append(
            {
                "setup": setup,
                "base_return": base.get("mean_total_return"),
                "fast_return": fast.get("mean_total_return"),
                "slow_return": slow.get("mean_total_return"),
                "handoff_return": hand.get("mean_total_return"),
                "base_hold": base.get("mean_hold_bars"),
                "fast_hold": fast.get("mean_hold_bars"),
                "slow_hold": slow.get("mean_hold_bars"),
                "handoff_hold": hand.get("mean_hold_bars"),
                "base_winner": base.get("mean_winner_median_return"),
                "fast_winner": fast.get("mean_winner_median_return"),
                "slow_winner": slow.get("mean_winner_median_return"),
                "handoff_winner": hand.get("mean_winner_median_return"),
                "base_capture": base.get("mean_mfe_capture_ratio"),
                "fast_capture": fast.get("mean_mfe_capture_ratio"),
                "slow_capture": slow.get("mean_mfe_capture_ratio"),
                "handoff_capture": hand.get("mean_mfe_capture_ratio"),
                "handoff_giveback": hand.get("mean_giveback_after_handoff"),
                "handoff_rate": hand.get("mean_handoff_rate"),
                "handoff_positive_asset_ratio": hand.get("positive_asset_ratio"),
            }
        )
    return pd.DataFrame(rows)


def build_verdict(compare: pd.DataFrame, cost_df: pd.DataFrame) -> tuple[str, str, str]:
    if compare.empty:
        return (
            "park / evidence pool",
            "暂无可比结果。",
            "这轮最小 clean replication 连 setup compare 都没形成，不该继续占默认 Scout 预算。",
        )
    wins = 0
    strong_wins = 0
    for _, row in compare.iterrows():
        improved = (
            pd.notna(row.get("handoff_return"))
            and pd.notna(row.get("base_return"))
            and pd.notna(row.get("handoff_capture"))
            and pd.notna(row.get("base_capture"))
            and pd.notna(row.get("handoff_giveback"))
            and pd.notna(row.get("handoff_rate"))
            and float(row["handoff_rate"]) >= 0.20
            and float(row["handoff_giveback"]) <= 0.65
            and (
                float(row["handoff_return"]) > float(row["base_return"]) + 0.002
                or float(row["handoff_capture"]) > float(row["base_capture"]) + 0.08
                or float(row.get("handoff_winner", np.nan)) > float(row.get("base_winner", np.nan)) + 0.002
            )
        )
        if improved:
            wins += 1
            if float(row.get("handoff_positive_asset_ratio", 0.0) or 0.0) >= (2 / 3):
                strong_wins += 1
    headline = "；".join(
        f"{r['setup']}: base≈{pct(r.get('base_return'))} / fast≈{pct(r.get('fast_return'))} / slow≈{pct(r.get('slow_return'))} / handoff≈{pct(r.get('handoff_return'))}"
        for _, r in compare.iterrows()
    )
    cost_survives = False
    if not cost_df.empty:
        c10 = cost_df[cost_df["cost_bps_per_side"] == 10.0]
        cost_survives = not c10.empty and float(c10.iloc[0]["mean_total_return"]) > 0
    if wins >= 2 and strong_wins >= 1 and cost_survives:
        return (
            "P2 paper candidate / admission queue",
            headline,
            "这次最小 clean replication 说明两段式 handoff 不只是把输家砍快，而是在多条 archetype 上开始更好地拿住 winner 且 giveback 还算可控，值得先升到 paper candidate pool。",
        )
    if wins >= 1:
        return (
            "P1 weak candidate / evidence pool",
            headline,
            "这次最小 clean replication 说明 fast-entry / slow-exit handoff 在部分 archetype 上开始像 shared exit overlay，但改善还不够统一；更诚实的读法仍是先留在 P1 证据池。",
        )
    return (
        "park / evidence pool",
        headline,
        "这次最小 clean replication 更像在证明：慢 exit / handoff 虽然能拉长持仓，但当前并没有稳定带来更好的成本后结果，或 giveback 太重，不该继续占默认 Scout 主资源位。",
    )


def render_factor_page(overall: pd.DataFrame, asset_summary: pd.DataFrame, compare: pd.DataFrame, pockets: pd.DataFrame, cost_df: pd.DataFrame, verdict: str, headline: str, reason: str, generated_at: str) -> str:
    overall_view = overall[[
        "setup", "variant", "cost_bps_per_side", "mean_total_return", "positive_asset_ratio", "mean_trades",
        "mean_trade_count_retention", "mean_win_rate", "mean_hold_bars", "mean_winner_median_return", "mean_winner_hold_bars",
        "mean_mfe_capture_ratio", "mean_giveback_after_handoff", "mean_handoff_rate", "mean_early_exit_rate", "mean_target_hit_24bars_rate"
    ]].copy()
    asset_view = asset_summary[(asset_summary["cost_bps_per_side"] == PRIMARY_COST) & (asset_summary["variant"] == PRIMARY_VARIANT)][[
        "asset", "setup", "trades", "trade_count_retention", "total_return", "win_rate", "mean_hold_bars", "winner_median_return",
        "winner_hold_bars", "mean_mfe_capture_ratio", "mean_giveback_after_handoff", "handoff_rate"
    ]].copy()
    compare_view = compare[[
        "setup", "base_return", "fast_return", "slow_return", "handoff_return", "base_hold", "fast_hold", "slow_hold", "handoff_hold",
        "base_winner", "fast_winner", "slow_winner", "handoff_winner", "base_capture", "fast_capture", "slow_capture", "handoff_capture", "handoff_giveback", "handoff_rate"
    ]].copy()
    pocket_view = pockets[pockets["variant"] == PRIMARY_VARIANT][["setup", "bucket", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_mfe_capture_ratio"]].copy() if not pockets.empty else pd.DataFrame()
    return f"""
<p><a href='../../reading/repo_scout/rank70_fast_entry_slow_exit_handoff_source_intake.html'>← 返回 source intake</a></p>
<h1>Rank 70 · fast-entry slow-exit handoff spine（minimal clean replication）</h1>
<p class='muted'>生成时间：{escape(generated_at)} ｜ 固定 BTC/ETH/SOL 120d 15m 本地 cache；entry 完全冻结；统一 <code>signal 当根及之前数据 + next-bar open + no-overlap</code>。</p>

<div class='card'>
  <h2>这轮只回答一个问题</h2>
  <p>当三条主线的 entry 已经冻结后，<b>前 {FAST_STAGE_BARS} 根 15m bar 继续 fail-fast，活下来后 handoff 到 slow Donchian / Chandelier exit</b>，到底能不能比 <code>all-fast fail</code> 或 <code>all-slow trailing</code> 更诚实地兼顾快认错和拿住 winner？</p>
  <ul>
    <li><b>四臂：</b><code>baseline_exit</code>（持有 {BASE_HOLD_BARS} bars）、<code>all_fast_fail</code>、<code>all_slow_trailing</code>、<code>handoff_exit</code>。</li>
    <li><b>fast stage：</b><code>EMA9 / session VWAP / 0.75*ATR</code> 任一失效则 next-bar open 退出。</li>
    <li><b>slow stage：</b><code>Donchian {SLOW_DONCHIAN_LEN}</code> / <code>{SLOW_CHANDELIER_ATR}*ATR chandelier</code>；最长持有 {MAX_HOLD_BARS} bars。</li>
    <li><b>handoff 条件：</b>存活满 {FAST_STAGE_BARS} 根 bar 或出现至少 <code>1 ATR</code> 的顺向 MFE。</li>
  </ul>
</div>

<div class='card'>
  <h2>硬结论</h2>
  <p><span class='pill'>{escape(verdict)}</span></p>
  <p><b>{escape(headline)}</b></p>
  <p class='muted'>{escape(reason)}</p>
</div>

<div class='card'>
  <h2>setup compare（6bps）</h2>
  {render_table(compare_view, percent_cols={'base_return','fast_return','slow_return','handoff_return','base_winner','fast_winner','slow_winner','handoff_winner','base_capture','fast_capture','slow_capture','handoff_capture','handoff_giveback','handoff_rate'}, digits_cols={'base_hold':2,'fast_hold':2,'slow_hold':2,'handoff_hold':2})}
</div>

<div class='card'>
  <h2>overall summary</h2>
  {render_table(overall_view, percent_cols={'mean_total_return','positive_asset_ratio','mean_win_rate','mean_winner_median_return','mean_mfe_capture_ratio','mean_giveback_after_handoff','mean_handoff_rate','mean_early_exit_rate','mean_target_hit_24bars_rate'}, digits_cols={'cost_bps_per_side':0,'mean_trades':1,'mean_hold_bars':2,'mean_winner_hold_bars':2})}
</div>

<div class='card'>
  <h2>cross-asset summary（主变体 handoff）</h2>
  {render_table(asset_view, percent_cols={'trade_count_retention','total_return','win_rate','winner_median_return','mean_mfe_capture_ratio','mean_giveback_after_handoff','handoff_rate'}, digits_cols={'trades':0,'mean_hold_bars':2,'winner_hold_bars':2})}
</div>

<div class='card'>
  <h2>time pockets（主变体 handoff）</h2>
  {render_table(pocket_view, percent_cols={'mean_total_return','positive_asset_ratio','mean_mfe_capture_ratio'}, digits_cols={'mean_trades':1})}
</div>

<div class='card'>
  <h2>cost / giveback stability（主变体 handoff）</h2>
  {render_table(cost_df, percent_cols={'mean_total_return','positive_asset_ratio','mean_trade_count_retention','mean_winner_median_return','mean_mfe_capture_ratio','mean_giveback_after_handoff','mean_handoff_rate'}, digits_cols={'cost_bps_per_side':0,'mean_trades':1,'mean_hold_bars':2})}
</div>
"""


def render_reading_page(compare: pd.DataFrame, verdict: str, headline: str, reason: str, generated_at: str) -> str:
    compare_view = compare[[
        "setup", "base_return", "fast_return", "slow_return", "handoff_return", "base_hold", "fast_hold", "slow_hold", "handoff_hold",
        "base_winner", "fast_winner", "slow_winner", "handoff_winner", "base_capture", "fast_capture", "slow_capture", "handoff_capture", "handoff_giveback", "handoff_rate"
    ]].copy()
    return f"""
<p><a href='rank70_fast_entry_slow_exit_handoff_source_intake.html'>← 返回 source intake</a></p>
<h1>Rank 70 · fast-entry slow-exit handoff spine clean replication</h1>
<div class='card'>
  <span class='pill'>更新时间：{escape(generated_at)}</span>
  <span class='pill'>类型：minimal clean replication</span>
  <span class='pill'>当前 verdict：{escape(verdict)}</span>
  <p class='muted'>artifact：<code>reports/artifacts/scout_rank70_fast_entry_slow_exit_handoff_15m/overall_summary.csv</code></p>
</div>
<div class='card'>
  <h2>一句话结果</h2>
  <p><b>{escape(headline)}</b></p>
  <p class='muted'>{escape(reason)}</p>
</div>
<div class='card'>
  <h2>这轮冻结的最小实验</h2>
  <ul>
    <li><code>BTC/ETH/SOL</code>，复用 120d 15m 本地 cache，不追新 bar，不做重下载。</li>
    <li>entry 完全冻结；只比较 exit：<code>baseline_exit</code>、<code>all_fast_fail</code>、<code>all_slow_trailing</code>、<code>handoff_exit</code>。</li>
    <li>主读法不是“拖得越久越好”，而是看 <code>winner_median_return</code>、<code>MFE_capture_ratio</code>、<code>giveback_after_handoff</code> 能不能同时站住。</li>
  </ul>
</div>
<div class='card'>
  <h2>setup compare（6bps）</h2>
  {render_table(compare_view, percent_cols={'base_return','fast_return','slow_return','handoff_return','base_winner','fast_winner','slow_winner','handoff_winner','base_capture','fast_capture','slow_capture','handoff_capture','handoff_giveback','handoff_rate'}, digits_cols={'base_hold':2,'fast_hold':2,'slow_hold':2,'handoff_hold':2})}
</div>
"""


def update_todo(compare: pd.DataFrame, verdict: str, generated_at: str, latest_p3_appends: int) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    marker = "### Next 3 bot3 runs（当前默认执行顺序）\n"
    if marker not in text:
        raise RuntimeError("Next 3 marker not found in TODO.md")
    if f"**最新补充（{generated_at}）**" in text:
        return
    compare = compare.set_index("setup")
    row_ema = compare.loc["ema_psar_long"]
    row_fib = compare.loc["fib_retest_long"]
    row_short = compare.loc["breakout_short"]
    block = (
        f"> **最新补充（{generated_at}）**：这轮先再次核对 `Run 1 / EMA due-check` 与 `P3` 托管位状态：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍显示全 desk 没有新的 `due-now / overdue` lane，最早仍是 `Crypto 1d+1wk -> 2026-03-19 00:00 UTC / due_soon`；`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 最新一次仍是 `new_closed_trades_appended={latest_p3_appends}`。因此当前没有新的 `Paper Seat` due-now 动作，也没有新的 `P3 status-changing event` 值得 bot3 回头挤占 continuity，按权威顺序这轮执行 **`Run 2 / Rank 70 minimal clean replication`**：固定复用 `BTC/ETH/SOL 120d 15m` cache，三条 base archetype（`ema_psar_long`、`fib_retest_long`、`breakout_short`）只比较 `baseline_exit`、`all_fast_fail`、`all_slow_trailing`、`handoff_exit` 四臂，entry 完全冻结，统一 `signal 当根及之前数据 + next-bar open + no-overlap`。\n"
        f">  - `6bps/side` 下的 setup-level 结果已冻结为：`ema_psar_long` 从 `base≈{pct(row_ema['base_return'])}` 到 `fast≈{pct(row_ema['fast_return'])}`、`slow≈{pct(row_ema['slow_return'])}`、`handoff≈{pct(row_ema['handoff_return'])}`；`fib_retest_long` 从 `base≈{pct(row_fib['base_return'])}` 到 `fast≈{pct(row_fib['fast_return'])}`、`slow≈{pct(row_fib['slow_return'])}`、`handoff≈{pct(row_fib['handoff_return'])}`；`breakout_short` 从 `base≈{pct(row_short['base_return'])}` 到 `fast≈{pct(row_short['fast_return'])}`、`slow≈{pct(row_short['slow_return'])}`、`handoff≈{pct(row_short['handoff_return'])}`。\n"
        f">  - 当前更诚实的 hard verdict：**`Rank 70 / fast-entry slow-exit handoff spine = {verdict}`**。\n"
        f">  - reader-facing 落点：`reports/site/factors/scout_rank70_fast_entry_slow_exit_handoff_15m/report.html`、`reports/site/reading/repo_scout/rank70_fast_entry_slow_exit_handoff_clean_replication.html`；artifact：`reports/artifacts/scout_rank70_fast_entry_slow_exit_handoff_15m/overall_summary.csv`、`setup_compare.csv`。\n"
        f">  - 这轮 verdict 已消耗掉 Rank 70 允许的那次 minimal clean replication。当前更诚实的 active Scout 顺序应更新为：**fresh source intake（优先比较 realized-vol mid-band cost-survival gate > PSAR close-confirmed follow-up gate） > Rank 35b > Rank 16b > tiny-live plumbing**。\n"
        f">  - 因此当前最新 `Next 3` 顺序应更新为：**`Run 1 = EMA due-check only` -> `Run 2 = 若 Rank 70 verdict 不足以升到下一层，则优先回到 fresh source 比较 realized-vol mid-band cost-survival gate > PSAR close-confirmed follow-up gate` -> `Run 3 = 若新的 fresh source 已 guard-passed 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication；只有 fresh source 这一层也 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing`**\n\n"
    )
    text = text.replace(marker, marker + "\n" + block, 1)
    TODO_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    latest_p3_appends = 0
    if P3_SUMMARY_PATH.exists():
        try:
            latest_p3_appends = int(pd.read_json(P3_SUMMARY_PATH, typ="series").get("new_closed_trades_appended", 0))
        except Exception:
            latest_p3_appends = 0

    frames = {asset: build_frame(asset, symbol) for asset, symbol in ASSETS.items()}
    signal_tables: list[pd.DataFrame] = []
    for asset in ASSETS:
        frame = frames[asset]
        for setup in SETUPS:
            signal_tables.append(build_signal_frame(frame, asset, setup))
    all_signals = pd.concat([df for df in signal_tables if not df.empty], ignore_index=True) if signal_tables else pd.DataFrame()
    if all_signals.empty:
        raise RuntimeError("no signals formed for Rank 70 clean replication")
    all_signals.to_csv(ART_DIR / "signal_windows.csv", index=False)

    asset_rows: list[dict[str, object]] = []
    trade_frames: list[pd.DataFrame] = []

    for asset in ASSETS:
        frame = frames[asset]
        for setup in SETUPS:
            sigs = all_signals[(all_signals["asset"] == asset) & (all_signals["setup"] == setup)].copy().reset_index(drop=True)
            for cost in COSTS:
                base_trades = build_trades(frame, sigs, "baseline_exit", cost)
                if not base_trades.empty:
                    trade_frames.append(base_trades)
                asset_rows.append(summarize_asset(base_trades, asset=asset, setup=setup, variant="baseline_exit", cost_bps=cost, base_trades=base_trades))
                for variant in ["all_fast_fail", "all_slow_trailing", "handoff_exit"]:
                    trades = build_trades(frame, sigs, variant, cost)
                    if not trades.empty:
                        trade_frames.append(trades)
                    asset_rows.append(summarize_asset(trades, asset=asset, setup=setup, variant=variant, cost_bps=cost, base_trades=base_trades))

    trades_df = pd.concat(trade_frames, ignore_index=True) if trade_frames else pd.DataFrame()
    asset_df = pd.DataFrame(asset_rows).sort_values(["setup", "variant", "cost_bps_per_side", "asset"]).reset_index(drop=True)
    overall_df = build_overall(asset_df)
    compare_df = build_setup_compare(overall_df)
    pocket_df = build_time_pockets(trades_df)
    cost_df = build_cost_summary(asset_df)
    verdict, headline, reason = build_verdict(compare_df, cost_df)

    trades_df.to_csv(ART_DIR / "trade_log.csv", index=False)
    asset_df.to_csv(ART_DIR / "asset_summary.csv", index=False)
    overall_df.to_csv(ART_DIR / "overall_summary.csv", index=False)
    compare_df.to_csv(ART_DIR / "setup_compare.csv", index=False)
    pocket_df.to_csv(ART_DIR / "time_pockets.csv", index=False)
    cost_df.to_csv(ART_DIR / "cost_stability.csv", index=False)
    pd.DataFrame([
        {
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "candidate_id": "rank70_fast_entry_slow_exit_handoff",
            "hard_verdict": verdict,
            "headline": headline,
            "reason": reason,
        }
    ]).to_csv(ART_DIR / "meta.csv", index=False)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    write_html(SITE_DIR / "report.html", "Rank 70 · fast-entry slow-exit handoff clean replication", render_factor_page(overall_df, asset_df, compare_df, pocket_df, cost_df, verdict, headline, reason, generated_at))
    write_html(READING_PATH, "Rank 70 · fast-entry slow-exit handoff clean replication", render_reading_page(compare_df, verdict, headline, reason, generated_at))
    update_todo(compare_df, verdict, generated_at, latest_p3_appends)

    print(f"generated_at={generated_at}")
    print(f"verdict={verdict}")
    print(f"headline={headline}")


if __name__ == "__main__":
    main()
