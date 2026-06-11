#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank65_perp_stress_reset_rearm_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank65_perp_stress_reset_rearm_15m"
READING_DIR = ROOT / "reports" / "site" / "reading" / "repo_scout"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
SETUPS = ["ema_psar_long", "fib_retest_long", "breakout_short"]
LONG_SETUPS = {"ema_psar_long", "fib_retest_long"}
VARIANTS = ["no_gate", "stress_pause_only", "stress_pause_reset_rearm"]
COSTS = [6.0, 10.0, 15.0, 20.0]
PRIMARY_COST = 6.0
HOLD_BARS = 8
TARGET_BARS = 12
FALSE_LOOKAHEAD = 4
STRESS_LOOKBACK = 12
REQ_TIMEOUT = 20
BINANCE_LIMIT = 500
KLINE_PAGES = 26
OI_PAGES = 26

EMA_FAST = 9
EMA_SLOW = 15
EMA_SLOPE_LOOKBACK = 3
EMA_SLOPE_FLOOR = 0.0003
ATR_PERIOD = 14
BREAK_LOOKBACK = 20
BREAK_CONFIRM_ATR = 0.1
BREAK_RETEST_ATR = 0.3


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


def load_spot_bars(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def rolling_z(series: pd.Series, window: int) -> pd.Series:
    mean = series.rolling(window, min_periods=window).mean()
    std = series.rolling(window, min_periods=window).std(ddof=0)
    return (series - mean) / std.replace(0, np.nan)


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


def fetch_paginated_json(url: str, params: dict[str, object], pages: int, key_time: str | None = None) -> list:
    rows: list = []
    end_time: int | None = None
    for _ in range(pages):
        req = dict(params)
        if end_time is not None:
            req["endTime"] = end_time
        resp = requests.get(url, params=req, timeout=REQ_TIMEOUT)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        rows = batch + rows
        if isinstance(batch[0], list):
            earliest = int(batch[0][0])
        else:
            assert key_time is not None
            earliest = int(batch[0][key_time])
        next_end = earliest - 1
        if end_time is not None and next_end >= end_time:
            break
        end_time = next_end
    return rows


def fetch_perp_klines(symbol: str) -> pd.DataFrame:
    cache_path = ensure_dir(ART_DIR / "futures_cache") / f"{symbol}_perp_15m.csv"
    if cache_path.exists():
        df = pd.read_csv(cache_path)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        return df.sort_values("timestamp").reset_index(drop=True)
    url = "https://fapi.binance.com/fapi/v1/klines"
    rows = fetch_paginated_json(url, {"symbol": symbol, "interval": "15m", "limit": BINANCE_LIMIT}, KLINE_PAGES)
    df = pd.DataFrame(rows, columns=[
        "open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume",
        "count", "taker_buy_base", "taker_buy_quote", "ignore"
    ])
    df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    out = df[["timestamp", "open", "high", "low", "close", "volume"]].drop_duplicates("timestamp").sort_values("timestamp")
    out.to_csv(cache_path, index=False)
    return out.reset_index(drop=True)


def fetch_open_interest(symbol: str) -> pd.DataFrame:
    cache_path = ensure_dir(ART_DIR / "futures_cache") / f"{symbol}_oi_15m.csv"
    if cache_path.exists():
        df = pd.read_csv(cache_path)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        return df.sort_values("timestamp").reset_index(drop=True)
    url = "https://fapi.binance.com/futures/data/openInterestHist"
    rows = fetch_paginated_json(url, {"symbol": symbol, "period": "15m", "limit": BINANCE_LIMIT}, OI_PAGES, key_time="timestamp")
    if not rows:
        return pd.DataFrame(columns=["timestamp", "oi", "oi_chg_pct", "oi_chg_ema3"])
    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df["oi"] = pd.to_numeric(df["sumOpenInterest"], errors="coerce")
    df = df[["timestamp", "oi"]].dropna().drop_duplicates("timestamp").sort_values("timestamp").reset_index(drop=True)
    df["oi_chg_pct"] = df["oi"].pct_change()
    df["oi_chg_ema3"] = df["oi_chg_pct"].ewm(span=3, adjust=False).mean()
    df.to_csv(cache_path, index=False)
    return df


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    spot = load_spot_bars(symbol, asset)
    perp = fetch_perp_klines(symbol)
    oi = fetch_open_interest(symbol)
    frame = spot.merge(perp.rename(columns={
        "open": "perp_open",
        "high": "perp_high",
        "low": "perp_low",
        "close": "perp_close",
        "volume": "perp_volume",
    }), on="timestamp", how="left")
    frame = frame.merge(oi, on="timestamp", how="left")

    frame["ema9"] = frame["close"].ewm(span=EMA_FAST, adjust=False).mean()
    frame["ema15"] = frame["close"].ewm(span=EMA_SLOW, adjust=False).mean()
    frame["ema_slope"] = frame["ema9"].pct_change(EMA_SLOPE_LOOKBACK)
    frame["vol_ma20"] = frame["volume"].rolling(20, min_periods=20).mean()
    frame["atr14"] = compute_atr(frame)
    frame["atr_sma20"] = frame["atr14"].rolling(20, min_periods=20).mean()
    frame["psar"] = compute_psar(frame)
    frame["rolling_low20"] = frame["low"].rolling(BREAK_LOOKBACK, min_periods=BREAK_LOOKBACK).min().shift(1)
    frame["swing_high_30"] = frame["high"].rolling(30, min_periods=30).max().shift(1)
    frame["swing_low_30"] = frame["low"].rolling(30, min_periods=30).min().shift(1)
    rng = frame["swing_high_30"] - frame["swing_low_30"]
    frame["fib_618"] = frame["swing_high_30"] - 0.618 * rng
    frame["fib_50"] = frame["swing_high_30"] - 0.5 * rng

    upper_wick = frame["high"] - frame[["open", "close"]].max(axis=1)
    lower_wick = frame[["open", "close"]].min(axis=1) - frame["low"]
    frame["wick_abs"] = pd.concat([upper_wick.abs(), lower_wick.abs()], axis=1).max(axis=1)
    frame["basis_pct"] = (frame["perp_close"] - frame["close"]) / frame["close"]
    frame["stress_event"] = (
        frame["basis_pct"].abs().ge(0.0025)
        & frame["oi_chg_ema3"].ge(0.01)
        & frame["wick_abs"].ge(0.8 * frame["atr14"])
        & frame["volume"].ge(1.2 * frame["volume"].rolling(50, min_periods=50).mean())
    ).fillna(False)
    frame["reset_complete"] = (
        frame["basis_pct"].abs().le(0.0010)
        & frame["oi_chg_ema3"].le(-0.012)
        & frame["atr14"].lt(0.9 * frame["atr_sma20"])
    ).fillna(False)
    frame["recent_stress"] = frame["stress_event"].rolling(STRESS_LOOKBACK, min_periods=1).max().fillna(0).astype(bool)

    frame["ema_psar_long_signal"] = (
        (frame["ema9"] > frame["ema15"])
        & (frame["ema_slope"] > EMA_SLOPE_FLOOR)
        & (frame["psar"] < frame["close"])
        & (frame["close"] > frame["high"].shift(1))
        & (frame["close"].shift(1) < frame["ema9"].shift(1))
        & (frame["volume"] > frame["vol_ma20"])
    ).fillna(False)
    frame["fib_retest_long_signal"] = (
        frame["fib_618"].notna()
        & (frame["ema9"] > frame["ema15"])
        & (frame["ema_slope"] > 0)
        & (frame["close"] > frame["fib_618"])
        & (frame["close"].shift(1) <= frame["fib_618"].shift(1))
        & (frame["low"] <= frame["fib_618"] + 0.2 * frame["atr14"])
        & (frame["close"] > frame["fib_50"])
        & (frame["volume"] > frame["vol_ma20"])
    ).fillna(False)
    frame["breakout_short_signal"] = (
        frame["rolling_low20"].notna()
        & (frame["ema9"] < frame["ema15"])
        & (frame["ema_slope"] < -EMA_SLOPE_FLOOR)
        & (frame["close"].shift(1) > frame["rolling_low20"].shift(1))
        & (frame["close"].shift(2) > frame["rolling_low20"].shift(2))
        & (frame["close"] < frame["rolling_low20"] - BREAK_CONFIRM_ATR * frame["atr14"])
        & (frame["high"] <= frame["rolling_low20"] + BREAK_RETEST_ATR * frame["atr14"])
        & (frame["volume"] > frame["vol_ma20"])
    ).fillna(False)
    return frame.reset_index(drop=True)


def setup_signal_col(setup: str) -> str:
    return f"{setup}_signal"


def variant_mask(frame: pd.DataFrame, variant: str) -> pd.Series:
    if variant == "no_gate":
        return pd.Series(True, index=frame.index)
    if variant == "stress_pause_only":
        return (~frame["recent_stress"]).fillna(False)
    if variant == "stress_pause_reset_rearm":
        return ((~frame["recent_stress"]) | frame["reset_complete"]).fillna(False)
    raise ValueError(variant)


def build_trades(frame: pd.DataFrame, setup: str, variant: str, cost_bps: float) -> tuple[pd.DataFrame, int]:
    signal = (frame[setup_signal_col(setup)] & variant_mask(frame, variant)).fillna(False)
    rows: list[dict[str, object]] = []
    raw_events = 0
    last_exit_idx = -1
    cost_rate = float(cost_bps) / 10000.0
    is_long = setup in LONG_SETUPS

    for idx in range(35, len(frame) - 2):
        if idx <= last_exit_idx:
            continue
        if not bool(frame[setup_signal_col(setup)].iloc[idx]):
            continue
        raw_events += 1
        if not bool(signal.iloc[idx]):
            continue
        entry_idx = idx + 1
        if entry_idx >= len(frame):
            break
        exit_idx = min(len(frame) - 1, entry_idx + HOLD_BARS - 1)
        target_idx = min(len(frame) - 1, entry_idx + TARGET_BARS - 1)
        fail_idx = min(len(frame) - 1, entry_idx + FALSE_LOOKAHEAD - 1)

        entry_px = float(frame.iloc[entry_idx]["open"])
        exit_px = float(frame.iloc[exit_idx]["close"])
        atr_entry = float(frame.iloc[idx]["atr14"])

        if is_long:
            gross_ret = exit_px / entry_px - 1.0
            false_continuation = int(float(frame.iloc[fail_idx]["close"]) < entry_px)
            target_hit = int(float(frame.iloc[entry_idx:target_idx + 1]["high"].max()) >= entry_px + atr_entry)
        else:
            gross_ret = entry_px / exit_px - 1.0
            false_continuation = int(float(frame.iloc[fail_idx]["close"]) > entry_px)
            target_hit = int(float(frame.iloc[entry_idx:target_idx + 1]["low"].min()) <= entry_px - atr_entry)
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0

        rows.append(
            {
                "asset": frame.iloc[0]["asset"],
                "setup": setup,
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "signal_ts": pd.to_datetime(frame.iloc[idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_ts": pd.to_datetime(frame.iloc[entry_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": pd.to_datetime(frame.iloc[exit_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_price": entry_px,
                "exit_price": exit_px,
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "atr_at_signal": atr_entry,
                "recent_stress": int(bool(frame.iloc[idx]["recent_stress"])),
                "reset_complete": int(bool(frame.iloc[idx]["reset_complete"])),
                "stress_event": int(bool(frame.iloc[idx]["stress_event"])),
                "target_hit_12bars": target_hit,
                "false_continuation_4bars": false_continuation,
            }
        )
        last_exit_idx = exit_idx
    return pd.DataFrame(rows), raw_events


def summarize_variant(trades: pd.DataFrame, raw_signal_counts: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    if trades.empty:
        return pd.DataFrame(columns=[
            "asset", "setup", "variant", "cost_bps_per_side", "trades", "raw_signal_count", "trade_count_retention",
            "total_return", "avg_trade", "target_hit_rate_12bars", "after_stress_false_continuation_rate"
        ])
    for (asset, setup, variant, cost_bps), grp in trades.groupby(["asset", "setup", "variant", "cost_bps_per_side"]):
        raw_count = int(raw_signal_counts.loc[(raw_signal_counts["asset"] == asset) & (raw_signal_counts["setup"] == setup), "raw_signal_count"].iloc[0])
        stress_grp = grp[grp["recent_stress"] == 1]
        rows.append(
            {
                "asset": asset,
                "setup": setup,
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "trades": int(len(grp)),
                "raw_signal_count": raw_count,
                "trade_count_retention": len(grp) / raw_count if raw_count else np.nan,
                "total_return": float(grp["net_ret"].sum()),
                "avg_trade": float(grp["net_ret"].mean()),
                "target_hit_rate_12bars": float(grp["target_hit_12bars"].mean()),
                "after_stress_false_continuation_rate": float(stress_grp["false_continuation_4bars"].mean()) if len(stress_grp) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def overall_summary(summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    if summary.empty:
        return pd.DataFrame(columns=[
            "variant", "cost_bps_per_side", "mean_total_return", "positive_asset_ratio", "mean_trades",
            "mean_trade_count_retention", "mean_target_hit_rate_12bars", "mean_after_stress_false_continuation_rate"
        ])
    for (variant, cost_bps), grp in summary.groupby(["variant", "cost_bps_per_side"]):
        asset_return = grp.groupby("asset")["total_return"].sum()
        asset_trades = grp.groupby("asset")["trades"].sum()
        rows.append(
            {
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "mean_total_return": float(asset_return.mean()) if len(asset_return) else np.nan,
                "positive_asset_ratio": float((asset_return > 0).mean()) if len(asset_return) else np.nan,
                "mean_trades": float(asset_trades.mean()) if len(asset_trades) else np.nan,
                "mean_trade_count_retention": float(grp["trade_count_retention"].mean()),
                "mean_target_hit_rate_12bars": float(grp["target_hit_rate_12bars"].mean()),
                "mean_after_stress_false_continuation_rate": float(grp["after_stress_false_continuation_rate"].mean()),
            }
        )
    return pd.DataFrame(rows).sort_values(["cost_bps_per_side", "variant"]).reset_index(drop=True)


def setup_breakdown(summary: pd.DataFrame, cost_bps: float = PRIMARY_COST) -> pd.DataFrame:
    focus = summary[np.isclose(summary["cost_bps_per_side"], cost_bps)]
    rows: list[dict[str, object]] = []
    if focus.empty:
        return pd.DataFrame(columns=[
            "setup", "variant", "mean_total_return", "positive_asset_ratio", "mean_trade_count_retention",
            "mean_target_hit_rate_12bars", "mean_after_stress_false_continuation_rate"
        ])
    for (setup, variant), grp in focus.groupby(["setup", "variant"]):
        asset_return = grp.groupby("asset")["total_return"].sum()
        rows.append(
            {
                "setup": setup,
                "variant": variant,
                "mean_total_return": float(asset_return.mean()) if len(asset_return) else np.nan,
                "positive_asset_ratio": float((asset_return > 0).mean()) if len(asset_return) else np.nan,
                "mean_trade_count_retention": float(grp["trade_count_retention"].mean()),
                "mean_target_hit_rate_12bars": float(grp["target_hit_rate_12bars"].mean()),
                "mean_after_stress_false_continuation_rate": float(grp["after_stress_false_continuation_rate"].mean()),
            }
        )
    return pd.DataFrame(rows).sort_values(["setup", "variant"]).reset_index(drop=True)


def event_board(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for asset, frame in frames.items():
        stress_cnt = int(frame["stress_event"].sum())
        reset_cnt = int(frame["reset_complete"].sum())
        rows.append(
            {
                "asset": asset,
                "bars": int(len(frame)),
                "stress_events": stress_cnt,
                "reset_complete_bars": reset_cnt,
                "stress_bar_ratio": stress_cnt / len(frame) if len(frame) else np.nan,
                "recent_stress_ratio": float(frame["recent_stress"].mean()),
            }
        )
    return pd.DataFrame(rows)


def verdict_text(overall: pd.DataFrame) -> tuple[str, str]:
    focus = overall[np.isclose(overall["cost_bps_per_side"], PRIMARY_COST)].copy()
    if focus.empty:
        return "park / evidence pool", "没有拿到可用 summary。"
    base = focus[focus["variant"] == "no_gate"].iloc[0]
    gated = focus[focus["variant"] == "stress_pause_reset_rearm"].iloc[0]
    pause = focus[focus["variant"] == "stress_pause_only"].iloc[0]
    improved = (
        gated["mean_total_return"] > base["mean_total_return"]
        and gated["mean_after_stress_false_continuation_rate"] < base["mean_after_stress_false_continuation_rate"]
        and gated["mean_trade_count_retention"] >= 0.45
        and gated["positive_asset_ratio"] >= base["positive_asset_ratio"]
    )
    if improved:
        return "paper candidate / P2", (
            "resetComplete gate 在 6bps/side 下同时改善了总收益、after-stress 假延续率，且没有把样本砍得太狠。"
        )
    return "park / evidence pool", (
        "resetComplete gate 目前更像风险管制模板：若只是砍单却没有稳定改善 after-stress 假延续率或跨资产收益，就不该升格。"
    )


def write_html(report_table: str, setup_table: str, event_table: str, verdict: str, verdict_note: str, out_path: Path, title: str) -> None:
    html = f"""<!doctype html>
<html lang=\"zh\">
<head>
  <meta charset=\"utf-8\">
  <title>{escape(title)}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 24px auto; max-width: 1100px; line-height: 1.6; color: #1f2937; padding: 0 16px; }}
    table {{ border-collapse: collapse; width: 100%; margin: 16px 0 28px; }}
    th, td {{ border: 1px solid #d1d5db; padding: 8px 10px; text-align: left; font-size: 14px; }}
    th {{ background: #f3f4f6; }}
    code {{ background: #f3f4f6; padding: 2px 5px; border-radius: 4px; }}
    .muted {{ color: #6b7280; }}
    .callout {{ background: #eff6ff; border: 1px solid #bfdbfe; padding: 14px 16px; border-radius: 8px; }}
  </style>
</head>
<body>
  <h1>{escape(title)}</h1>
  <div class=\"callout\">
    <p><strong>Hard verdict：</strong>{escape(verdict)}</p>
    <p>{escape(verdict_note)}</p>
    <p class=\"muted\">最小 clean replication：BTC/ETH/SOL 120d 15m，spot cache + Binance futures klines/openInterestHist，统一 <code>signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars</code>。</p>
  </div>
  <h2>跨资产总览</h2>
  {report_table}
  <h2>按 setup 拆分（6bps/side）</h2>
  {setup_table}
  <h2>stress/reset 事件覆盖</h2>
  {event_table}
</body>
</html>"""
    out_path.write_text(html, encoding="utf-8")


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_DIR)

    frames: dict[str, pd.DataFrame] = {}
    all_trades: list[pd.DataFrame] = []
    raw_counts: list[dict[str, object]] = []

    for asset, symbol in ASSETS.items():
        frame = build_frame(asset, symbol)
        frames[asset] = frame
        for setup in SETUPS:
            raw_signal_count = int(frame[setup_signal_col(setup)].sum())
            raw_counts.append({"asset": asset, "setup": setup, "raw_signal_count": raw_signal_count})
            for cost in COSTS:
                for variant in VARIANTS:
                    trades, _ = build_trades(frame, setup, variant, cost)
                    if not trades.empty:
                        all_trades.append(trades)

    raw_signal_counts = pd.DataFrame(raw_counts)
    trades = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    summary = summarize_variant(trades, raw_signal_counts)
    overall = overall_summary(summary)
    by_setup = setup_breakdown(summary)
    events = event_board(frames)
    verdict, verdict_note = verdict_text(overall)

    raw_signal_counts.to_csv(ART_DIR / "raw_signal_counts.csv", index=False)
    trades.to_csv(ART_DIR / "trades.csv", index=False)
    summary.to_csv(ART_DIR / "summary_by_asset_setup.csv", index=False)
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    by_setup.to_csv(ART_DIR / "setup_summary.csv", index=False)
    events.to_csv(ART_DIR / "stress_event_board.csv", index=False)

    overall_view = overall.copy()
    if not overall_view.empty:
        overall_view = overall_view[[
            "variant", "cost_bps_per_side", "mean_total_return", "positive_asset_ratio", "mean_trades",
            "mean_trade_count_retention", "mean_target_hit_rate_12bars", "mean_after_stress_false_continuation_rate"
        ]]
    setup_view = by_setup.copy()
    event_view = events.copy()

    report_html = render_table(
        overall_view,
        percent_cols={
            "mean_total_return", "positive_asset_ratio", "mean_trade_count_retention",
            "mean_target_hit_rate_12bars", "mean_after_stress_false_continuation_rate"
        },
        digits_cols={"cost_bps_per_side": 1, "mean_trades": 1},
    )
    setup_html = render_table(
        setup_view,
        percent_cols={
            "mean_total_return", "positive_asset_ratio", "mean_trade_count_retention",
            "mean_target_hit_rate_12bars", "mean_after_stress_false_continuation_rate"
        },
    )
    event_html = render_table(
        event_view,
        percent_cols={"stress_bar_ratio", "recent_stress_ratio"},
    )

    write_html(
        report_html,
        setup_html,
        event_html,
        verdict,
        verdict_note,
        SITE_DIR / "report.html",
        "Rank 65 / perp-stress resetComplete / re-arm gate clean replication",
    )
    write_html(
        report_html,
        setup_html,
        event_html,
        verdict,
        verdict_note,
        READING_DIR / "rank65_perp_stress_reset_rearm_clean_replication.html",
        "Rank 65 / perp-stress resetComplete / re-arm gate clean replication",
    )

    snapshot = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "verdict": verdict,
        "verdict_note": verdict_note,
    }
    pd.Series(snapshot).to_json(ART_DIR / "snapshot.json", force_ascii=False, indent=2)
    print(f"Rank 65 clean replication done -> {verdict}")


if __name__ == "__main__":
    main()
