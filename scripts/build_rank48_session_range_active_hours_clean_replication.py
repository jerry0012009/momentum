#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank48_session_range_active_hours_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank48_session_range_active_hours_15m"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
BASE_SETUPS = ["ema_psar", "fib_retest", "breakout_reclaim"]
OVERLAYS = [
    "raw_all_day",
    "active_hours_only",
    "session_structure_gate",
    "session_structure_plus_volume",
    "session_structure_plus_volume_trend",
]
PRIMARY_OVERLAY = "session_structure_plus_volume_trend"
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0, 20.0]
HOLD_BARS = 8
EARLY_FAIL_BARS = 4
FOLLOW_THROUGH_BARS = [4, 8, 12]
VOL_SMA = 20
VOL_MULT = 1.3
EMA_FAST = 20
EMA_SLOW = 50
EMA_SLOPE_LOOKBACK = 3
EMA_SLOPE_FLOOR = 0.0003
ADX_LEN = 21
ADX_THRESHOLD = 20.0
LOOKBACK = 50
FIB_VOL_SMA = 24
FIB_SMA_TREND = 200
FIB_EMA_FAST = 9
FIB_EMA_SLOW = 26
ATR_PERIOD = 14
BREAKOUT_ATR_WIDTH = 0.5
BREAKOUT_RECLAIM = 0.1
SESSION_BREAK_LOOKBACK = 4
ACTIVE_HOURS = set(list(range(8, 22)))


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


def load_cached_bars(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def wilder_rma(series: pd.Series, length: int) -> pd.Series:
    return series.ewm(alpha=1.0 / length, adjust=False).mean()


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


def parabolic_sar(high: pd.Series, low: pd.Series, step: float = 0.02, max_step: float = 0.2) -> tuple[np.ndarray, np.ndarray]:
    hi = np.asarray(high, dtype=float)
    lo = np.asarray(low, dtype=float)
    n = len(hi)
    sar = np.full(n, np.nan, dtype=float)
    direction = np.zeros(n, dtype=int)
    if n == 0:
        return sar, direction
    if n == 1:
        direction[0] = 1
        sar[0] = lo[0]
        return sar, direction
    bull = (hi[1] + lo[1]) >= (hi[0] + lo[0])
    af = step
    ep = hi[0] if bull else lo[0]
    current_sar = lo[0] if bull else hi[0]
    sar[0] = current_sar
    direction[0] = 1 if bull else -1
    for i in range(1, n):
        current_sar = current_sar + af * (ep - current_sar)
        if bull:
            current_sar = min(current_sar, lo[i - 1])
            if i >= 2:
                current_sar = min(current_sar, lo[i - 2])
            if lo[i] < current_sar:
                bull = False
                current_sar = ep
                ep = lo[i]
                af = step
            else:
                if hi[i] > ep:
                    ep = hi[i]
                    af = min(af + step, max_step)
        else:
            current_sar = max(current_sar, hi[i - 1])
            if i >= 2:
                current_sar = max(current_sar, hi[i - 2])
            if hi[i] > current_sar:
                bull = True
                current_sar = ep
                ep = hi[i]
                af = step
            else:
                if lo[i] < ep:
                    ep = lo[i]
                    af = min(af + step, max_step)
        sar[i] = current_sar
        direction[i] = 1 if bull else -1
    return sar, direction


def add_session_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["hour"] = out["timestamp"].dt.hour
    out["is_active_hour"] = out["hour"].isin(sorted(ACTIVE_HOURS))
    def bucket(hour: int) -> str:
        if 0 <= hour < 8:
            return "asia"
        if 8 <= hour < 13:
            return "london"
        if 13 <= hour < 16:
            return "overlap"
        if 16 <= hour < 22:
            return "newyork"
        return "dead"
    out["session_bucket"] = out["hour"].map(bucket)
    out["session_date"] = out["timestamp"].dt.strftime("%Y-%m-%d")
    out["session_key"] = out["session_date"] + "|" + out["session_bucket"]
    session_stats = (
        out.groupby("session_key", dropna=False)
        .agg(
            session_start=("timestamp", "min"),
            session_high=("high", "max"),
            session_low=("low", "min"),
            session_bucket=("session_bucket", "first"),
        )
        .reset_index()
        .sort_values("session_start")
        .reset_index(drop=True)
    )
    active_stats = session_stats[session_stats["session_bucket"] != "dead"].copy().reset_index(drop=True)
    active_stats["prev_session_high"] = active_stats["session_high"].shift(1)
    active_stats["prev_session_low"] = active_stats["session_low"].shift(1)
    out = out.merge(active_stats[["session_key", "prev_session_high", "prev_session_low"]], on="session_key", how="left")
    out["recent_prev_session_break_long"] = (
        (out["high"] > out["prev_session_high"]).fillna(False).rolling(SESSION_BREAK_LOOKBACK, min_periods=1).max() > 0
    )
    out["recent_prev_session_break_short"] = (
        (out["low"] < out["prev_session_low"]).fillna(False).rolling(SESSION_BREAK_LOOKBACK, min_periods=1).max() > 0
    )
    out["session_structure_long"] = (
        out["is_active_hour"]
        & out["prev_session_high"].notna()
        & out["recent_prev_session_break_long"]
        & (out["close"] > out["prev_session_high"])
    )
    out["session_structure_short"] = (
        out["is_active_hour"]
        & out["prev_session_low"].notna()
        & out["recent_prev_session_break_short"]
        & (out["close"] < out["prev_session_low"])
    )
    return out


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_cached_bars(symbol, asset)
    close = df["close"]
    high = df["high"]
    low = df["low"]
    prev_close = close.shift(1)

    df["ema_fast"] = close.ewm(span=EMA_FAST, adjust=False).mean()
    df["ema_slow"] = close.ewm(span=EMA_SLOW, adjust=False).mean()
    df["ema_slope"] = df["ema_fast"].pct_change(EMA_SLOPE_LOOKBACK)
    df["ema50"] = close.ewm(span=50, adjust=False).mean()
    df["vol_sma20"] = df["volume"].rolling(VOL_SMA, min_periods=VOL_SMA).mean()
    df["atr14"] = compute_atr(df)

    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = pd.Series(np.where((up_move > down_move) & (up_move > 0), up_move, 0.0), index=df.index)
    minus_dm = pd.Series(np.where((down_move > up_move) & (down_move > 0), down_move, 0.0), index=df.index)
    tr = pd.concat([
        (high - low),
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    truerange = wilder_rma(tr, ADX_LEN)
    plus = 100.0 * wilder_rma(plus_dm, ADX_LEN) / truerange.replace(0, np.nan)
    minus = 100.0 * wilder_rma(minus_dm, ADX_LEN) / truerange.replace(0, np.nan)
    dx = 100.0 * (plus - minus).abs() / (plus + minus).replace(0, np.nan)
    df["adx"] = wilder_rma(dx.fillna(0.0), ADX_LEN)

    df["fib_618"] = low.rolling(LOOKBACK, min_periods=LOOKBACK).min() + (high.rolling(LOOKBACK, min_periods=LOOKBACK).max() - low.rolling(LOOKBACK, min_periods=LOOKBACK).min()) * 0.618
    df["fib_50"] = low.rolling(LOOKBACK, min_periods=LOOKBACK).min() + (high.rolling(LOOKBACK, min_periods=LOOKBACK).max() - low.rolling(LOOKBACK, min_periods=LOOKBACK).min()) * 0.5
    df["volume_sma24"] = df["volume"].rolling(FIB_VOL_SMA, min_periods=FIB_VOL_SMA).mean()
    df["sma200"] = close.rolling(FIB_SMA_TREND, min_periods=FIB_SMA_TREND).mean()
    df["ema9"] = close.ewm(span=FIB_EMA_FAST, adjust=False).mean()
    df["ema26"] = close.ewm(span=FIB_EMA_SLOW, adjust=False).mean()

    sar_15m, psar_dir_15m = parabolic_sar(df["high"], df["low"])
    df["psar_15m"] = sar_15m
    df["psar_dir_15m"] = psar_dir_15m
    htf = (
        df.set_index("timestamp")[["open", "high", "low", "close"]]
        .resample("1h")
        .agg({"open": "first", "high": "max", "low": "min", "close": "last"})
        .dropna()
        .reset_index()
    )
    _, psar_dir_htf = parabolic_sar(htf["high"], htf["low"])
    htf["psar_dir_htf"] = psar_dir_htf
    df = pd.merge_asof(
        df.sort_values("timestamp"),
        htf[["timestamp", "psar_dir_htf"]].sort_values("timestamp"),
        on="timestamp",
        direction="backward",
    )
    df = add_session_features(df)
    return df.reset_index(drop=True)


def base_signals(frame: pd.DataFrame, setup: str) -> tuple[pd.Series, pd.Series]:
    if setup == "ema_psar":
        long_sig = (
            (frame["psar_dir_htf"] == 1)
            & (frame["ema_fast"] > frame["ema_slow"])
            & (frame["ema_slope"] > EMA_SLOPE_FLOOR)
            & (frame["close"] > frame["ema_fast"])
            & ~((frame["psar_dir_htf"] == 1)
                & (frame["ema_fast"] > frame["ema_slow"])
                & (frame["ema_slope"] > EMA_SLOPE_FLOOR)
                & (frame["close"] > frame["ema_fast"])).shift(1).fillna(False)
        )
        short_sig = (
            (frame["psar_dir_htf"] == -1)
            & (frame["ema_fast"] < frame["ema_slow"])
            & (frame["ema_slope"] < -EMA_SLOPE_FLOOR)
            & (frame["close"] < frame["ema_fast"])
            & ~((frame["psar_dir_htf"] == -1)
                & (frame["ema_fast"] < frame["ema_slow"])
                & (frame["ema_slope"] < -EMA_SLOPE_FLOOR)
                & (frame["close"] < frame["ema_fast"])).shift(1).fillna(False)
        )
        return long_sig.fillna(False), short_sig.fillna(False)

    if setup == "fib_retest":
        reclaim_618 = (frame["close"] > frame["fib_618"]) & (frame["close"].shift(1) <= frame["fib_618"].shift(1))
        long_sig = (reclaim_618 & (frame["volume"] > frame["volume_sma24"]) & (frame["close"] > frame["sma200"]) & (frame["ema9"] > frame["ema26"])).fillna(False)
        short_sig = pd.Series(False, index=frame.index)
        return long_sig, short_sig

    if setup == "breakout_reclaim":
        rolling_high = frame["high"].rolling(20, min_periods=20).max().shift(1)
        breakout = frame["close"] > rolling_high
        atr = frame["atr14"]
        retest_zone = (frame["low"] <= rolling_high + BREAKOUT_ATR_WIDTH * atr) & (frame["low"] >= rolling_high - BREAKOUT_ATR_WIDTH * atr)
        reclaim = frame["close"] >= rolling_high + BREAKOUT_RECLAIM * atr
        long_sig = (breakout & retest_zone & reclaim).fillna(False)
        short_sig = pd.Series(False, index=frame.index)
        return long_sig, short_sig

    raise ValueError(setup)


def overlay_mask(frame: pd.DataFrame, setup: str, overlay: str, direction: str) -> pd.Series:
    if overlay == "raw_all_day":
        return pd.Series(True, index=frame.index)
    active = frame["is_active_hour"]
    if overlay == "active_hours_only":
        return active
    structure = frame["session_structure_long"] if direction == "long" else frame["session_structure_short"]
    if overlay == "session_structure_gate":
        return structure.fillna(False)
    volume_gate = (frame["volume"] > frame["vol_sma20"] * VOL_MULT).fillna(False)
    if overlay == "session_structure_plus_volume":
        return (structure & volume_gate).fillna(False)
    trend_gate = ((frame["adx"] > ADX_THRESHOLD) | ((frame["close"] > frame["ema50"]) if direction == "long" else (frame["close"] < frame["ema50"]))).fillna(False)
    if overlay == PRIMARY_OVERLAY:
        return (structure & volume_gate & trend_gate).fillna(False)
    raise ValueError(overlay)


def build_trades(frame: pd.DataFrame, setup: str, overlay: str, cost_bps: float) -> tuple[pd.DataFrame, int]:
    long_base, short_base = base_signals(frame, setup)
    long_sig = (long_base & overlay_mask(frame, setup, overlay, "long")).fillna(False)
    short_sig = (short_base & overlay_mask(frame, setup, overlay, "short")).fillna(False)
    rows: list[dict[str, object]] = []
    signal_events = 0
    last_exit_idx = -1
    cost_rate = float(cost_bps) / 10000.0

    for idx in range(1, len(frame) - 2):
        if idx <= last_exit_idx or idx + 1 >= len(frame):
            continue
        direction = 1 if bool(long_sig.iloc[idx]) else -1 if bool(short_sig.iloc[idx]) else 0
        if direction == 0:
            continue
        signal_events += 1
        entry_idx = idx + 1
        exit_idx = min(len(frame) - 1, entry_idx + HOLD_BARS - 1)
        entry_px = float(frame.iloc[entry_idx]["open"])
        exit_px = float(frame.iloc[exit_idx]["close"])
        gross_ret = (exit_px / entry_px - 1.0) * direction
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
        ft = {}
        for bars in FOLLOW_THROUGH_BARS:
            probe_idx = min(len(frame) - 1, entry_idx + bars - 1)
            ft[bars] = (float(frame.iloc[probe_idx]["close"]) / entry_px - 1.0) * direction
        probe_idx = min(len(frame) - 1, entry_idx + EARLY_FAIL_BARS - 1)
        early_ret = (float(frame.iloc[probe_idx]["close"]) / entry_px - 1.0) * direction
        opposite_seen = bool(short_sig.iloc[entry_idx:probe_idx + 1].any()) if direction > 0 else bool(long_sig.iloc[entry_idx:probe_idx + 1].any())
        early_fail = int((early_ret < 0.0) or opposite_seen)
        rows.append(
            {
                "asset": str(frame.iloc[0]["asset"]),
                "setup": setup,
                "overlay": overlay,
                "cost_bps_per_side": float(cost_bps),
                "signal_ts": pd.to_datetime(frame.iloc[idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_ts": pd.to_datetime(frame.iloc[entry_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": pd.to_datetime(frame.iloc[exit_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "direction": "long" if direction > 0 else "short",
                "entry_price": entry_px,
                "exit_price": exit_px,
                "net_ret": net_ret,
                "follow_through_4bars": ft[4],
                "follow_through_8bars": ft[8],
                "follow_through_12bars": ft[12],
                "early_fail_4bars": early_fail,
                "session_bucket": str(frame.iloc[idx]["session_bucket"]),
                "is_active_hour": int(bool(frame.iloc[idx]["is_active_hour"])),
            }
        )
        last_exit_idx = exit_idx
    return pd.DataFrame(rows), signal_events


def summarize_asset(trades: pd.DataFrame, *, asset: str, setup: str, overlay: str, cost_bps: float, signal_events: int) -> dict[str, object]:
    if trades.empty:
        return {
            "asset": asset,
            "setup": setup,
            "overlay": overlay,
            "cost_bps_per_side": float(cost_bps),
            "signal_events": int(signal_events),
            "trades": 0,
            "trade_count_retention": 0.0,
            "total_return": 0.0,
            "win_rate": np.nan,
            "early_fail_4bars_rate": np.nan,
            "follow_through_4bars": np.nan,
            "follow_through_8bars": np.nan,
            "follow_through_12bars": np.nan,
        }
    return {
        "asset": asset,
        "setup": setup,
        "overlay": overlay,
        "cost_bps_per_side": float(cost_bps),
        "signal_events": int(signal_events),
        "trades": int(len(trades)),
        "trade_count_retention": float(len(trades) / signal_events) if signal_events > 0 else np.nan,
        "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
        "win_rate": float((trades["net_ret"] > 0).mean()),
        "early_fail_4bars_rate": float(trades["early_fail_4bars"].mean()),
        "follow_through_4bars": float(trades["follow_through_4bars"].mean()),
        "follow_through_8bars": float(trades["follow_through_8bars"].mean()),
        "follow_through_12bars": float(trades["follow_through_12bars"].mean()),
    }


def summarize_overall(asset_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (setup, overlay, cost), grp in asset_df.groupby(["setup", "overlay", "cost_bps_per_side"], sort=False):
        rows.append(
            {
                "setup": setup,
                "overlay": overlay,
                "cost_bps_per_side": float(cost),
                "mean_total_return": float(grp["total_return"].mean()),
                "positive_asset_ratio": float((grp["total_return"] > 0).mean()),
                "mean_trades": float(grp["trades"].mean()),
                "mean_trade_count_retention": float(grp["trade_count_retention"].mean()),
                "mean_win_rate": float(grp["win_rate"].mean()),
                "mean_early_fail_4bars_rate": float(grp["early_fail_4bars_rate"].mean()),
                "mean_follow_through_4bars": float(grp["follow_through_4bars"].mean()),
                "mean_follow_through_8bars": float(grp["follow_through_8bars"].mean()),
                "mean_follow_through_12bars": float(grp["follow_through_12bars"].mean()),
            }
        )
    return pd.DataFrame(rows)


def build_setup_scorecard(overall: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for setup in BASE_SETUPS:
        base = overall[(overall["setup"] == setup) & (overall["overlay"] == "raw_all_day") & (overall["cost_bps_per_side"] == PRIMARY_COST)]
        gated = overall[(overall["setup"] == setup) & (overall["overlay"] == PRIMARY_OVERLAY) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
        if base.empty or gated.empty:
            continue
        b = base.iloc[0]
        g = gated.iloc[0]
        raw_trades = float(b["mean_trades"])
        gated_trades = float(g["mean_trades"])
        rows.append(
            {
                "setup": setup,
                "raw_total_return": float(b["mean_total_return"]),
                "gated_total_return": float(g["mean_total_return"]),
                "return_delta": float(g["mean_total_return"] - b["mean_total_return"]),
                "raw_early_fail_4bars_rate": float(b["mean_early_fail_4bars_rate"]),
                "gated_early_fail_4bars_rate": float(g["mean_early_fail_4bars_rate"]),
                "fail_delta": float(g["mean_early_fail_4bars_rate"] - b["mean_early_fail_4bars_rate"]),
                "gated_trade_count_retention": float(gated_trades / raw_trades) if raw_trades > 0 else np.nan,
                "gated_positive_asset_ratio": float(g["positive_asset_ratio"]),
            }
        )
    return pd.DataFrame(rows)


def build_session_bucket_summary(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["setup", "overlay", "session_bucket", "trades", "mean_net_ret", "win_rate"])
    rows = []
    grouped = trades[(trades["cost_bps_per_side"] == PRIMARY_COST)].groupby(["setup", "overlay", "session_bucket"], sort=False)
    for (setup, overlay, bucket), grp in grouped:
        rows.append(
            {
                "setup": setup,
                "overlay": overlay,
                "session_bucket": bucket,
                "trades": int(len(grp)),
                "mean_net_ret": float(grp["net_ret"].mean()),
                "win_rate": float((grp["net_ret"] > 0).mean()),
            }
        )
    return pd.DataFrame(rows)


def pick_verdict(scorecard: pd.DataFrame) -> tuple[str, str]:
    if scorecard.empty:
        return "park / evidence pool", "Rank 48 的共用 overlay 没有形成可解释样本。"
    improved = scorecard[
        (scorecard["return_delta"] > 0.0)
        & (scorecard["fail_delta"] < 0.0)
        & (scorecard["gated_trade_count_retention"] >= 0.35)
    ]
    strong = improved[improved["gated_positive_asset_ratio"] >= (2 / 3)]
    if len(strong) >= 1 and len(improved) >= 2:
        return "P1 weak candidate / evidence pool", "session-range / active-hours overlay 至少在两条 base setup 上同时减少了 4-bar early-fail，且没有靠极端砍样本才成立，值得保留一次后续便宜诚实检查。"
    return "park / evidence pool", "session-range / active-hours overlay 虽可能减少部分 dead-hour 噪音，但目前更像切样本后的执行模板，没有在足够多 base setup 上同时改善成本后表现与 4-bar early-fail。"


def write_report(overall: pd.DataFrame, scorecard: pd.DataFrame, session_df: pd.DataFrame, verdict: str, reason: str, generated_at: str) -> None:
    ensure_dir(SITE_DIR)
    primary = overall[(overall["overlay"] == PRIMARY_OVERLAY) & (overall["cost_bps_per_side"] == PRIMARY_COST)].copy()
    raw = overall[(overall["overlay"] == "raw_all_day") & (overall["cost_bps_per_side"] == PRIMARY_COST)].copy()
    headline_parts = []
    for setup in BASE_SETUPS:
        pr = primary[primary["setup"] == setup]
        rw = raw[raw["setup"] == setup]
        if pr.empty or rw.empty:
            continue
        p = pr.iloc[0]
        r = rw.iloc[0]
        headline_parts.append(
            f"{setup}: gated≈{pct(p['mean_total_return'])}/{pct(p['mean_early_fail_4bars_rate'])}/保留{pct(p['mean_trade_count_retention'])} vs raw≈{pct(r['mean_total_return'])}/{pct(r['mean_early_fail_4bars_rate'])}"
        )
    headline = "；".join(headline_parts)

    html = f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 48 · session-range active-hours gate clean replication</title>
  <style>
    body {{ font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width: 1180px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background: #f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }}
    .muted {{ color:#6b7280; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    a {{ color:#2563eb; text-decoration:none; }}
  </style>
</head>
<body>
  <p><a href='../../plans/momentum_todo.html'>← 返回 TODO / desk board</a></p>
  <h1>Rank 48 · session-range + active-hours gate</h1>
  <p class='muted'>生成时间：{escape(generated_at)} ｜ 本轮类型：Run 2 / fresh Scout 最小 clean replication</p>

  <div class='card'>
    <h2>这轮只回答一个问题</h2>
    <ul>
      <li>不新造 alpha，只把 <code>session/time-of-day</code> 当成共用 overlay。</li>
      <li>固定复用 <code>BTC/ETH/SOL 120d 15m</code> cache，统一 <code>next-bar open + no-overlap + hold 8 bars</code>。</li>
      <li>三个 base setup：<code>ema_psar</code>、<code>fib_retest</code>、<code>breakout_reclaim</code>。</li>
      <li>五档对照：<code>raw_all_day</code>、<code>active_hours_only</code>、<code>session_structure_gate</code>、<code>+volume</code>、<code>+volume+ADX/EMA50</code>。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>hard verdict</h2>
    <p><span class='pill'>{escape(verdict)}</span></p>
    <p><b>{escape(headline)}</b></p>
    <p class='muted'>{escape(reason)}</p>
  </div>

  <div class='card'>
    <h2>6bps/side 总览</h2>
    {render_table(overall[overall['cost_bps_per_side'] == PRIMARY_COST][['setup','overlay','mean_total_return','positive_asset_ratio','mean_trades','mean_trade_count_retention','mean_early_fail_4bars_rate','mean_follow_through_4bars','mean_follow_through_8bars']], percent_cols={'mean_total_return','positive_asset_ratio','mean_trade_count_retention','mean_early_fail_4bars_rate','mean_follow_through_4bars','mean_follow_through_8bars'}, digits_cols={'mean_trades':1})}
  </div>

  <div class='card'>
    <h2>raw vs gated 对照</h2>
    {render_table(scorecard[['setup','raw_total_return','gated_total_return','return_delta','raw_early_fail_4bars_rate','gated_early_fail_4bars_rate','fail_delta','gated_trade_count_retention','gated_positive_asset_ratio']], percent_cols={'raw_total_return','gated_total_return','return_delta','raw_early_fail_4bars_rate','gated_early_fail_4bars_rate','fail_delta','gated_trade_count_retention','gated_positive_asset_ratio'}, digits_cols={})}
  </div>

  <div class='card'>
    <h2>session bucket 贡献（6bps）</h2>
    {render_table(session_df[['setup','overlay','session_bucket','trades','mean_net_ret','win_rate']], percent_cols={'mean_net_ret','win_rate'}, digits_cols={'trades':0})}
  </div>
</body>
</html>
"""
    (SITE_DIR / 'report.html').write_text(html, encoding='utf-8')


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    all_trades = []
    asset_rows = []
    for asset, symbol in ASSETS.items():
        frame = build_frame(asset, symbol)
        frame.to_csv(ART_DIR / f"{asset.replace('-USD','').lower()}_frame.csv", index=False)
        for setup in BASE_SETUPS:
            for overlay in OVERLAYS:
                for cost in COSTS:
                    trades, signal_events = build_trades(frame, setup, overlay, cost)
                    if not trades.empty:
                        all_trades.append(trades)
                    asset_rows.append(summarize_asset(trades, asset=asset, setup=setup, overlay=overlay, cost_bps=cost, signal_events=signal_events))

    asset_df = pd.DataFrame(asset_rows)
    overall = summarize_overall(asset_df)
    all_trades_df = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    session_df = build_session_bucket_summary(all_trades_df)
    scorecard = build_setup_scorecard(overall)
    verdict, reason = pick_verdict(scorecard)
    generated_at = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

    asset_df.to_csv(ART_DIR / 'asset_summary.csv', index=False)
    overall.to_csv(ART_DIR / 'overall_summary.csv', index=False)
    scorecard.to_csv(ART_DIR / 'setup_scorecard.csv', index=False)
    session_df.to_csv(ART_DIR / 'session_bucket_summary.csv', index=False)
    if not all_trades_df.empty:
        all_trades_df.to_csv(ART_DIR / 'all_trades.csv', index=False)
    pd.DataFrame([
        {
            'generated_at_utc': generated_at,
            'verdict': verdict,
            'reason': reason,
            'data_scope': 'BTC/ETH/SOL | 120d | 15m',
            'execution': 'next-bar open + no-overlap + hold 8 bars',
            'overlays': 'raw_all_day | active_hours_only | session_structure_gate | session_structure_plus_volume | session_structure_plus_volume_trend',
        }
    ]).to_csv(ART_DIR / 'meta.csv', index=False)
    write_report(overall, scorecard, session_df, verdict, reason, generated_at)
    print(f'WROTE {ART_DIR}')
    print(f'VERDICT {verdict}')
    print(f'REASON {reason}')


if __name__ == '__main__':
    main()
