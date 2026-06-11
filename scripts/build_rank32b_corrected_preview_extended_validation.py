#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "rank32b_corrected_preview_extended_validation"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "rank32b_corrected_preview_extended_validation"
CACHE_DIR = ROOT / "reports" / "artifacts" / "rank32b_unclosed15m_preview_backtest" / "cache_1m"

EMA_FAST_1H = 20
EMA_SLOW_1H = 50
SLOPE_FLOOR = 0.0004
ATR_PERIOD = 14
HOLD_MIN = 120
DEFAULT_DAYS = 90
COSTS_DEFAULT = [10.0]
MAKER_TP_COST_BPS = 0.0
FETCH_LIMIT = 1500
MAX_RETRIES = 8
BASE_SLEEP = 0.03

UNIVERSES = {
    "core18": {
        "BTC-USD": "BTCUSDT",
        "ETH-USD": "ETHUSDT",
        "SOL-USD": "SOLUSDT",
        "LTC-USD": "LTCUSDT",
        "NEAR-USD": "NEARUSDT",
        "UNI-USD": "UNIUSDT",
        "XRP-USD": "XRPUSDT",
        "DOGE-USD": "DOGEUSDT",
        "BNB-USD": "BNBUSDT",
        "ADA-USD": "ADAUSDT",
        "AVAX-USD": "AVAXUSDT",
        "LINK-USD": "LINKUSDT",
        "BCH-USD": "BCHUSDT",
        "DOT-USD": "DOTUSDT",
        "ZEC-USD": "ZECUSDT",
        "AAVE-USD": "AAVEUSDT",
        "SUI-USD": "SUIUSDT",
        "WLD-USD": "WLDUSDT",
    },
    "rep5": {
        "BTC-USD": "BTCUSDT",
        "ETH-USD": "ETHUSDT",
        "SOL-USD": "SOLUSDT",
        "NEAR-USD": "NEARUSDT",
        "WLD-USD": "WLDUSDT",
    },
    "rep8": {
        "BTC-USD": "BTCUSDT",
        "ETH-USD": "ETHUSDT",
        "SOL-USD": "SOLUSDT",
        "NEAR-USD": "NEARUSDT",
        "DOGE-USD": "DOGEUSDT",
        "ZEC-USD": "ZECUSDT",
        "AAVE-USD": "AAVEUSDT",
        "WLD-USD": "WLDUSDT",
    },
}

EXIT_CONFIGS = [
    {"name": "fixed_hold_120m", "kind": "fixed_hold", "hold_min": 120},
    {"name": "atr_tp1.25_sl1.00_to120", "kind": "atr", "tp_atr": 1.25, "sl_atr": 1.00, "timeout_min": 120},
    {"name": "atr_tp1.50_sl1.00_to120", "kind": "atr", "tp_atr": 1.50, "sl_atr": 1.00, "timeout_min": 120},
    {"name": "atr_tp1.75_sl1.00_to120", "kind": "atr", "tp_atr": 1.75, "sl_atr": 1.00, "timeout_min": 120},
    {"name": "atr_tp1.50_sl0.75_to120", "kind": "atr", "tp_atr": 1.50, "sl_atr": 0.75, "timeout_min": 120},
    {"name": "atr_tp2.00_sl1.00_to120", "kind": "atr", "tp_atr": 2.00, "sl_atr": 1.00, "timeout_min": 120},
]


@dataclass(slots=True)
class ExitResult:
    exit_ts: pd.Timestamp
    exit_price: float
    exit_reason: str
    net_ret: float
    gross_ret: float


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
        return "<p class='muted'>暂无数据。</p>"
    percent_cols = percent_cols or set()
    digits_cols = digits_cols or {}
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows: list[str] = []
    for _, row in df.iterrows():
        cells: list[str] = []
        for col in df.columns:
            v = row[col]
            if col in percent_cols:
                text = pct(v)
            elif isinstance(v, (float, np.floating, int, np.integer)) and not isinstance(v, bool):
                text = num(v, digits_cols.get(col, 2))
            else:
                text = str(v)
            cells.append(f"<td>{escape(text)}</td>")
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def fetch_1m(symbol: str, days: int) -> pd.DataFrame:
    end_ms = int(time.time() * 1000)
    start_ms = end_ms - days * 24 * 60 * 60 * 1000
    current = start_ms
    rows: list[list] = []
    cols = [
        "open_time", "open", "high", "low", "close", "volume", "close_time", "quote_asset_volume", "num_trades", "taker_buy_base", "taker_buy_quote", "ignore"
    ]
    while current < end_ms:
        params = {"symbol": symbol, "interval": "1m", "startTime": current, "endTime": end_ms, "limit": FETCH_LIMIT}
        retry = 0
        while True:
            resp = requests.get("https://fapi.binance.com/fapi/v1/klines", params=params, timeout=30)
            if resp.status_code == 429:
                retry_after = resp.headers.get("Retry-After")
                wait_s = float(retry_after) if retry_after else min(30.0, (2**retry) * 0.6)
                time.sleep(wait_s)
                retry += 1
                if retry > MAX_RETRIES:
                    resp.raise_for_status()
                continue
            if resp.status_code >= 500:
                time.sleep(min(20.0, (2**retry) * 0.5))
                retry += 1
                if retry > MAX_RETRIES:
                    resp.raise_for_status()
                continue
            resp.raise_for_status()
            data = resp.json()
            break
        if not data:
            break
        rows.extend(data)
        current = int(data[-1][0]) + 60_000
        if len(data) < FETCH_LIMIT:
            break
        time.sleep(BASE_SLEEP)
    df = pd.DataFrame(rows, columns=cols)
    out = pd.DataFrame({
        "open_ts": pd.to_datetime(df["open_time"], unit="ms", utc=True),
        "open": pd.to_numeric(df["open"], errors="coerce"),
        "high": pd.to_numeric(df["high"], errors="coerce"),
        "low": pd.to_numeric(df["low"], errors="coerce"),
        "close": pd.to_numeric(df["close"], errors="coerce"),
        "volume": pd.to_numeric(df["volume"], errors="coerce"),
    }).dropna().sort_values("open_ts").drop_duplicates("open_ts").reset_index(drop=True)
    out["close_ts"] = out["open_ts"] + pd.Timedelta(minutes=1)
    return out


def load_or_fetch_1m(symbol: str, days: int, refresh: bool = False) -> pd.DataFrame:
    ensure_dir(CACHE_DIR)
    path = CACHE_DIR / f"{symbol}__{days}d__1m__perp.csv"
    if path.exists() and not refresh:
        df = pd.read_csv(path)
        df["open_ts"] = pd.to_datetime(df["open_ts"], utc=True)
        df["close_ts"] = pd.to_datetime(df["close_ts"], utc=True)
        return df.sort_values("open_ts").reset_index(drop=True)
    df = fetch_1m(symbol, days)
    df.to_csv(path, index=False)
    return df


def build_15m_from_1m(m1: pd.DataFrame) -> pd.DataFrame:
    work = m1.copy()
    work["timestamp"] = work["open_ts"].dt.floor("15min")
    return (
        work.groupby("timestamp", sort=True)
        .agg(open=("open", "first"), high=("high", "max"), low=("low", "min"), close=("close", "last"))
        .reset_index()
    )


def build_frame(bars: pd.DataFrame) -> pd.DataFrame:
    market = bars[["timestamp", "close"]].copy().rename(columns={"close": "close_1h_src"}).set_index("timestamp")
    market_1h = market.resample("1h").last().dropna().reset_index()
    market_1h["ema_fast_1h"] = market_1h["close_1h_src"].ewm(span=EMA_FAST_1H, adjust=False).mean()
    market_1h["ema_slow_1h"] = market_1h["close_1h_src"].ewm(span=EMA_SLOW_1H, adjust=False).mean()
    market_1h["fast_slope"] = market_1h["ema_fast_1h"].pct_change()
    market_1h["slow_slope"] = market_1h["ema_slow_1h"].pct_change()
    frame = pd.merge_asof(bars.sort_values("timestamp"), market_1h.sort_values("timestamp"), on="timestamp", direction="backward")
    frame["long_structure"] = (frame["ema_fast_1h"] > frame["ema_slow_1h"]).fillna(False)
    frame["short_structure"] = (frame["ema_fast_1h"] < frame["ema_slow_1h"]).fillna(False)
    frame["slope_floor_long"] = ((frame["fast_slope"] > SLOPE_FLOOR) & (frame["slow_slope"] > 0)).fillna(False)
    frame["slope_floor_short"] = ((frame["fast_slope"] < -SLOPE_FLOOR) & (frame["slow_slope"] < 0)).fillna(False)
    frame["prev_close"] = frame["close"].shift(1)
    frame["prev_fast"] = frame["ema_fast_1h"].shift(1)
    frame["official_dir"] = 0
    frame.loc[(frame["long_structure"] & frame["slope_floor_long"] & (frame["prev_close"] <= frame["prev_fast"]) & (frame["close"] > frame["ema_fast_1h"])).fillna(False), "official_dir"] = 1
    frame.loc[(frame["short_structure"] & frame["slope_floor_short"] & (frame["prev_close"] >= frame["prev_fast"]) & (frame["close"] < frame["ema_fast_1h"])).fillna(False), "official_dir"] = -1
    prev_close = frame["close"].shift(1)
    tr = pd.concat([(frame["high"] - frame["low"]).abs(), (frame["high"] - prev_close).abs(), (frame["low"] - prev_close).abs()], axis=1).max(axis=1)
    frame["tr15"] = tr
    frame["atr14"] = tr.rolling(ATR_PERIOD, min_periods=ATR_PERIOD).mean()
    return frame


def build_preview_table(m1: pd.DataFrame, frame: pd.DataFrame) -> pd.DataFrame:
    minute = m1[["open_ts", "close_ts", "high", "low", "close"]].copy()
    minute["timestamp"] = minute["open_ts"].dt.floor("15min")
    minute["cum_high"] = minute.groupby("timestamp")["high"].cummax()
    minute["cum_low"] = minute.groupby("timestamp")["low"].cummin()
    merge_cols = ["timestamp", "ema_fast_1h", "long_structure", "short_structure", "slope_floor_long", "slope_floor_short", "prev_close", "prev_fast", "official_dir", "tr15"]
    minute = minute.merge(frame[merge_cols], on="timestamp", how="left")
    # partial ATR uses previous 13 completed 15m TRs + current partial TR
    frame_hist = frame[["timestamp", "tr15"]].copy()
    hist_rows = []
    for _, row in frame_hist.iterrows():
        end = pd.Timestamp(row["timestamp"])
        hist = frame_hist[(frame_hist["timestamp"] < end)].tail(ATR_PERIOD - 1)["tr15"]
        hist_rows.append({"timestamp": end, "atr_hist_sum13": float(hist.sum()), "atr_hist_count13": int(len(hist))})
    hist_df = pd.DataFrame(hist_rows)
    minute = minute.merge(hist_df, on="timestamp", how="left")
    partial_tr = pd.concat([
        (minute["cum_high"] - minute["cum_low"]).abs(),
        (minute["cum_high"] - minute["prev_close"]).abs(),
        (minute["cum_low"] - minute["prev_close"]).abs(),
    ], axis=1).max(axis=1)
    minute["atr14_partial"] = np.where(minute["atr_hist_count13"] >= (ATR_PERIOD - 1), (minute["atr_hist_sum13"] + partial_tr) / ATR_PERIOD, np.nan)
    minute["preview_dir"] = 0
    minute.loc[(minute["long_structure"] & minute["slope_floor_long"] & (minute["prev_close"] <= minute["prev_fast"]) & (minute["close"] > minute["ema_fast_1h"])).fillna(False), "preview_dir"] = 1
    minute.loc[(minute["short_structure"] & minute["slope_floor_short"] & (minute["prev_close"] >= minute["prev_fast"]) & (minute["close"] < minute["ema_fast_1h"])).fillna(False), "preview_dir"] = -1
    preview = minute[minute["preview_dir"] != 0].groupby("timestamp", sort=True).head(1).copy()
    preview["entry_ts"] = preview["close_ts"]
    preview["confirmed_at_close"] = (preview["preview_dir"] == preview["official_dir"]).astype(int)
    preview["preview_only"] = (preview["preview_dir"] != preview["official_dir"]).astype(int)
    preview["lead_minutes"] = ((preview["timestamp"] + pd.Timedelta(minutes=15)) - preview["entry_ts"]).dt.total_seconds() / 60.0
    return preview


def simulate_fixed_hold(open_map: pd.Series, close_map: pd.Series, entry_ts: pd.Timestamp, direction: int, cost_bps: float) -> ExitResult | None:
    if entry_ts not in open_map.index:
        return None
    exit_ts = entry_ts + pd.Timedelta(minutes=HOLD_MIN)
    if exit_ts not in close_map.index:
        return None
    entry = float(open_map.loc[entry_ts])
    exit_px = float(close_map.loc[exit_ts])
    gross = (exit_px / entry - 1.0) * direction
    rate = cost_bps / 10000.0
    net = (1.0 + gross) * (1.0 - rate) * (1.0 - rate) - 1.0
    return ExitResult(exit_ts=exit_ts, exit_price=exit_px, exit_reason="fixed_hold", net_ret=float(net), gross_ret=float(gross))


def simulate_atr(open_map: pd.Series, minute_scope: pd.DataFrame, entry_ts: pd.Timestamp, direction: int, atr14: float, cost_bps: float, tp_atr: float, sl_atr: float, timeout_min: int) -> ExitResult | None:
    if entry_ts not in open_map.index or not math.isfinite(atr14) or atr14 <= 0:
        return None
    entry = float(open_map.loc[entry_ts])
    if direction > 0:
        tp_price = entry + tp_atr * atr14
        sl_price = entry - sl_atr * atr14
    else:
        tp_price = entry - tp_atr * atr14
        sl_price = entry + sl_atr * atr14
    timeout_ts = entry_ts + pd.Timedelta(minutes=timeout_min)
    rate = cost_bps / 10000.0
    scoped = minute_scope[(minute_scope["open_ts"] >= entry_ts) & (minute_scope["open_ts"] < timeout_ts)]
    for _, bar in scoped.iterrows():
        high = float(bar["high"])
        low = float(bar["low"])
        hit_tp = (high >= tp_price) if direction > 0 else (low <= tp_price)
        hit_sl = (low <= sl_price) if direction > 0 else (high >= sl_price)
        if hit_tp and hit_sl:
            exit_px = sl_price
            gross = (exit_px / entry - 1.0) * direction
            net = (1.0 + gross) * (1.0 - rate) * (1.0 - rate) - 1.0
            return ExitResult(exit_ts=pd.to_datetime(bar["close_ts"], utc=True), exit_price=float(exit_px), exit_reason="conflict_stop_first", net_ret=float(net), gross_ret=float(gross))
        if hit_tp:
            exit_px = tp_price
            gross = (exit_px / entry - 1.0) * direction
            tp_rate = MAKER_TP_COST_BPS / 10000.0
            net = (1.0 + gross) * (1.0 - rate) * (1.0 - tp_rate) - 1.0
            return ExitResult(exit_ts=pd.to_datetime(bar["close_ts"], utc=True), exit_price=float(exit_px), exit_reason="take_profit", net_ret=float(net), gross_ret=float(gross))
        if hit_sl:
            exit_px = sl_price
            gross = (exit_px / entry - 1.0) * direction
            net = (1.0 + gross) * (1.0 - rate) * (1.0 - rate) - 1.0
            return ExitResult(exit_ts=pd.to_datetime(bar["close_ts"], utc=True), exit_price=float(exit_px), exit_reason="stop_loss", net_ret=float(net), gross_ret=float(gross))
    if timeout_ts not in open_map.index:
        return None
    exit_px = float(open_map.loc[timeout_ts])
    gross = (exit_px / entry - 1.0) * direction
    net = (1.0 + gross) * (1.0 - rate) * (1.0 - rate) - 1.0
    return ExitResult(exit_ts=timeout_ts, exit_price=float(exit_px), exit_reason="timeout", net_ret=float(net), gross_ret=float(gross))


def run_validation(universe: dict[str, str], days: int, refresh: bool, costs: list[float]) -> tuple[pd.DataFrame, pd.DataFrame]:
    trades = []
    for idx, (asset, symbol) in enumerate(universe.items(), start=1):
        print(f"[{idx}/{len(universe)}] {asset} {symbol}", flush=True)
        m1 = load_or_fetch_1m(symbol, days=days, refresh=refresh)
        m1["open_ts"] = pd.to_datetime(m1["open_ts"], utc=True)
        m1["close_ts"] = pd.to_datetime(m1["close_ts"], utc=True)
        for c in ["open", "high", "low", "close"]:
            m1[c] = pd.to_numeric(m1[c], errors="coerce")
        bars = build_15m_from_1m(m1)
        frame = build_frame(bars)
        preview = build_preview_table(m1, frame)
        open_map = m1.set_index("open_ts")["open"]
        close_map = m1.set_index("close_ts")["close"]

        official = frame[frame["official_dir"] != 0][["timestamp", "official_dir", "atr14"]].copy()
        official["entry_ts"] = official["timestamp"] + pd.Timedelta(minutes=15)
        official["confirmed_at_close"] = 1
        official["preview_only"] = 0
        official["lead_minutes"] = 0.0
        official["entry_improve_bps"] = 0.0
        official["mode_entry"] = "official_close"

        preview = preview[["timestamp", "preview_dir", "atr14_partial", "confirmed_at_close", "preview_only", "lead_minutes"]].copy()
        preview["entry_ts"] = preview["timestamp"] + preview["lead_minutes"].apply(lambda m: pd.Timedelta(minutes=15 - m))
        # fix exact entry ts from first preview minute close
        minute_first = build_preview_table(m1, frame)[["timestamp", "entry_ts"]]
        preview = preview.drop(columns=["entry_ts"]).merge(minute_first, on="timestamp", how="left")
        preview["mode_entry"] = "preview_unclosed15m"

        for cfg in EXIT_CONFIGS:
            for cost in costs:
                # official
                last_exit = pd.Timestamp.min.tz_localize("UTC")
                for row in official.sort_values("entry_ts").itertuples(index=False):
                    if row.entry_ts <= last_exit:
                        continue
                    if cfg["kind"] == "fixed_hold":
                        ex = simulate_fixed_hold(open_map, close_map, row.entry_ts, int(row.official_dir), cost)
                    else:
                        ex = simulate_atr(open_map, m1, row.entry_ts, int(row.official_dir), float(row.atr14) if pd.notna(row.atr14) else np.nan, cost, cfg["tp_atr"], cfg["sl_atr"], cfg["timeout_min"])
                    if ex is None:
                        continue
                    trades.append({
                        "asset": asset,
                        "symbol": symbol,
                        "entry_mode": "official_close",
                        "exit_config": cfg["name"],
                        "market_cost_bps": float(cost),
                        "net_ret": ex.net_ret,
                        "gross_ret": ex.gross_ret,
                        "exit_reason": ex.exit_reason,
                        "confirmed_at_close": 1,
                        "preview_only": 0,
                        "lead_minutes": 0.0,
                    })
                    last_exit = ex.exit_ts
                # preview
                last_exit = pd.Timestamp.min.tz_localize("UTC")
                pre_first = build_preview_table(m1, frame)
                for row in pre_first.sort_values("entry_ts").itertuples(index=False):
                    if row.entry_ts <= last_exit:
                        continue
                    atr14 = float(row.atr14_partial) if pd.notna(row.atr14_partial) else np.nan
                    if cfg["kind"] == "fixed_hold":
                        ex = simulate_fixed_hold(open_map, close_map, row.entry_ts, int(row.preview_dir), cost)
                    else:
                        ex = simulate_atr(open_map, m1, row.entry_ts, int(row.preview_dir), atr14, cost, cfg["tp_atr"], cfg["sl_atr"], cfg["timeout_min"])
                    if ex is None:
                        continue
                    trades.append({
                        "asset": asset,
                        "symbol": symbol,
                        "entry_mode": "preview_unclosed15m",
                        "exit_config": cfg["name"],
                        "market_cost_bps": float(cost),
                        "net_ret": ex.net_ret,
                        "gross_ret": ex.gross_ret,
                        "exit_reason": ex.exit_reason,
                        "confirmed_at_close": int(row.confirmed_at_close),
                        "preview_only": int(row.preview_only),
                        "lead_minutes": float(row.lead_minutes),
                    })
                    last_exit = ex.exit_ts

    trades_df = pd.DataFrame(trades)
    summary_rows = []
    for (entry_mode, exit_config, cost), grp in trades_df.groupby(["entry_mode", "exit_config", "market_cost_bps"], sort=False):
        asset_total = grp.groupby("asset")["net_ret"].apply(lambda s: float((1.0 + s).prod() - 1.0))
        summary_rows.append({
            "entry_mode": entry_mode,
            "exit_config": exit_config,
            "market_cost_bps": float(cost),
            "mean_total_return": float(asset_total.mean()),
            "median_total_return": float(asset_total.median()),
            "positive_asset_ratio": float((asset_total > 0).mean()),
            "mean_trades": float(grp.groupby("asset").size().mean()),
            "mean_win_rate": float(grp.groupby("asset")["net_ret"].apply(lambda s: (s > 0).mean()).mean()),
            "confirmed_at_close_ratio": float(grp["confirmed_at_close"].mean()) if entry_mode == "preview_unclosed15m" else 1.0,
            "preview_only_ratio": float(grp["preview_only"].mean()) if entry_mode == "preview_unclosed15m" else 0.0,
            "mean_lead_minutes": float(grp["lead_minutes"].dropna().mean()) if grp["lead_minutes"].notna().any() else 0.0,
        })
    return trades_df, pd.DataFrame(summary_rows).sort_values(["exit_config", "market_cost_bps", "entry_mode"]).reset_index(drop=True)


def build_html(generated_at: str, meta: dict[str, object], summary: pd.DataFrame, current10: pd.DataFrame, candidate10: pd.DataFrame) -> str:
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank32b corrected preview extended validation</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1200px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background: #f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .muted {{ color:#6b7280; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
  </style>
</head>
<body>
  <h1>Rank32b · corrected preview extended validation</h1>
  <p class='muted'>生成时间：{escape(generated_at)} ｜ universe={escape(str(meta['universe']))} ｜ days={escape(str(meta['days']))}</p>

  <div class='card'>
    <h2>回答的问题</h2>
    <ul>
      <li>corrected preview（只提前看未收盘 15m，1h 结构不漂移）在更大样本上是否仍成立？</li>
      <li>如果改成 TP/SL/timeout 的 live-like exits，preview 结论是否仍成立？</li>
      <li>既然 preview 让单笔利润变厚，现有 TP/SL 线是否需要调整？</li>
    </ul>
  </div>

  <div class='card'>
    <h2>整体汇总</h2>
    {render_table(summary[['entry_mode','exit_config','market_cost_bps','mean_total_return','median_total_return','positive_asset_ratio','mean_trades','mean_win_rate','confirmed_at_close_ratio','preview_only_ratio','mean_lead_minutes']], percent_cols={'mean_total_return','median_total_return','positive_asset_ratio','mean_win_rate','confirmed_at_close_ratio','preview_only_ratio'}, digits_cols={'market_cost_bps':0,'mean_trades':1,'mean_lead_minutes':2})}
  </div>

  <div class='card'>
    <h2>当前 live-like 参数（10bps）</h2>
    {render_table(current10[['entry_mode','exit_config','market_cost_bps','mean_total_return','median_total_return','positive_asset_ratio','mean_trades','mean_win_rate','confirmed_at_close_ratio','preview_only_ratio','mean_lead_minutes']], percent_cols={'mean_total_return','median_total_return','positive_asset_ratio','mean_win_rate','confirmed_at_close_ratio','preview_only_ratio'}, digits_cols={'market_cost_bps':0,'mean_trades':1,'mean_lead_minutes':2})}
  </div>

  <div class='card'>
    <h2>更优候选参数（10bps）</h2>
    {render_table(candidate10[['entry_mode','exit_config','market_cost_bps','mean_total_return','median_total_return','positive_asset_ratio','mean_trades','mean_win_rate','confirmed_at_close_ratio','preview_only_ratio','mean_lead_minutes']], percent_cols={'mean_total_return','median_total_return','positive_asset_ratio','mean_win_rate','confirmed_at_close_ratio','preview_only_ratio'}, digits_cols={'market_cost_bps':0,'mean_trades':1,'mean_lead_minutes':2})}
  </div>
</body>
</html>
"""


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Rank32b corrected preview extended validation")
    parser.add_argument("--universe", default="core18", choices=sorted(UNIVERSES.keys()))
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--costs", default=",".join(str(x) for x in COSTS_DEFAULT))
    parser.add_argument("--tag", default="")
    args = parser.parse_args()

    costs = [float(x) for x in args.costs.split(",") if x.strip()]
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    tag = args.tag.strip() or f"{args.universe}_{args.days}d"
    run_dir = ensure_dir(ART_DIR / tag)

    trades_df, summary_df = run_validation(UNIVERSES[args.universe], args.days, args.refresh, costs)
    trades_df.to_csv(run_dir / "trades.csv", index=False)
    summary_df.to_csv(run_dir / "summary.csv", index=False)

    current10 = summary_df[(summary_df["market_cost_bps"] == 10.0) & (summary_df["exit_config"] == "atr_tp1.25_sl1.00_to120")].copy().reset_index(drop=True)
    candidate10 = summary_df[(summary_df["market_cost_bps"] == 10.0) & (summary_df["entry_mode"] == "preview_unclosed15m")].sort_values("mean_total_return", ascending=False).head(4).copy().reset_index(drop=True)
    meta = {"generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"), "universe": args.universe, "days": int(args.days), "costs": costs}
    (run_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    html = build_html(meta["generated_at"], meta, summary_df, current10, candidate10)
    site_path = SITE_DIR / f"{tag}.html"
    site_path.write_text(html, encoding="utf-8")
    print(summary_df.to_string(index=False))
    print(f"\nartifacts: {run_dir}")
    print(f"site: {site_path}")


if __name__ == "__main__":
    main()
