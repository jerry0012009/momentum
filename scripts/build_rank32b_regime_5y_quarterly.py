#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import time
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "rank32b_regime_5y_quarterly"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "rank32b_regime_5y_quarterly"
CACHE_DIR = ART_DIR / "cache_15m"

EMA_FAST_1H = 20
EMA_SLOW_1H = 50
SLOPE_FLOOR = 0.0004
RECLAIM_LOOKBACK = 4
HOLD_BARS = 8
COSTS = [6.0, 10.0, 15.0, 20.0]
PRIMARY_COST = 10.0
DEFAULT_DAYS = 365 * 5 + 5
LIMIT = 1500
BASE_SLEEP = 0.03
MAX_RETRIES = 8

ASSETS = {
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
}


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
    body: list[str] = []
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
        body.append(f"<tr>{''.join(cells)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def fetch_klines(symbol: str, interval: str, days: int) -> pd.DataFrame:
    end_ms = int(time.time() * 1000)
    start_ms = end_ms - days * 24 * 60 * 60 * 1000
    current = start_ms
    rows: list[list] = []
    cols = [
        "open_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "quote_asset_volume",
        "num_trades",
        "taker_buy_base",
        "taker_buy_quote",
        "ignore",
    ]
    while current < end_ms:
        params = {"symbol": symbol, "interval": interval, "startTime": current, "endTime": end_ms, "limit": LIMIT}
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
        current = int(data[-1][0]) + 1
        if len(data) < LIMIT:
            break
        time.sleep(BASE_SLEEP)
    if not rows:
        return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])
    df = pd.DataFrame(rows, columns=cols)
    out = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(df["open_time"], unit="ms", utc=True),
            "open": pd.to_numeric(df["open"], errors="coerce"),
            "high": pd.to_numeric(df["high"], errors="coerce"),
            "low": pd.to_numeric(df["low"], errors="coerce"),
            "close": pd.to_numeric(df["close"], errors="coerce"),
            "volume": pd.to_numeric(df["volume"], errors="coerce"),
        }
    )
    out = out.dropna().sort_values("timestamp").drop_duplicates("timestamp").reset_index(drop=True)
    out = out[(out[["open", "high", "low", "close"]] > 0).all(axis=1)].reset_index(drop=True)
    return out


def load_or_fetch_15m(symbol: str, days: int, refresh: bool = False) -> pd.DataFrame:
    ensure_dir(CACHE_DIR)
    path = CACHE_DIR / f"{symbol}__{days}d__15m__perp.csv"
    if path.exists() and not refresh:
        df = pd.read_csv(path)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        return df.sort_values("timestamp").reset_index(drop=True)
    df = fetch_klines(symbol, "15m", days)
    df.to_csv(path, index=False)
    return df


def build_frame_from_bars(asset: str, bars: pd.DataFrame) -> pd.DataFrame:
    market = bars[["timestamp", "close"]].copy().rename(columns={"close": "close_1h_src"}).set_index("timestamp")
    market_1h = market.resample("1h").last().dropna().reset_index()
    market_1h["ema_fast_1h"] = market_1h["close_1h_src"].ewm(span=EMA_FAST_1H, adjust=False).mean()
    market_1h["ema_slow_1h"] = market_1h["close_1h_src"].ewm(span=EMA_SLOW_1H, adjust=False).mean()
    market_1h["fast_slope"] = market_1h["ema_fast_1h"].pct_change()
    market_1h["slow_slope"] = market_1h["ema_slow_1h"].pct_change()

    frame = pd.merge_asof(bars.sort_values("timestamp"), market_1h.sort_values("timestamp"), on="timestamp", direction="backward")
    frame["asset"] = asset
    frame["spread_mid"] = (frame["ema_fast_1h"] + frame["ema_slow_1h"]) / 2.0
    frame["long_structure"] = (frame["ema_fast_1h"] > frame["ema_slow_1h"]).fillna(False).astype(int)
    frame["short_structure"] = (frame["ema_fast_1h"] < frame["ema_slow_1h"]).fillna(False).astype(int)
    frame["slope_floor_long"] = ((frame["fast_slope"] > SLOPE_FLOOR) & (frame["slow_slope"] > 0)).fillna(False).astype(int)
    frame["slope_floor_short"] = ((frame["fast_slope"] < -SLOPE_FLOOR) & (frame["slow_slope"] < 0)).fillna(False).astype(int)
    frame["slope_strength"] = frame["fast_slope"].abs().fillna(0.0) + frame["slow_slope"].abs().fillna(0.0)

    prev_close = frame["close"].shift(1)
    prev_fast = frame["ema_fast_1h"].shift(1)
    frame["slope_floor_long_signal"] = ((frame["long_structure"] == 1) & (frame["slope_floor_long"] == 1) & (prev_close <= prev_fast) & (frame["close"] > frame["ema_fast_1h"]))
    frame["slope_floor_short_signal"] = ((frame["short_structure"] == 1) & (frame["slope_floor_short"] == 1) & (prev_close >= prev_fast) & (frame["close"] < frame["ema_fast_1h"]))
    frame["official_dir"] = np.where(frame["slope_floor_long_signal"], 1, np.where(frame["slope_floor_short_signal"], -1, 0))
    return frame


def build_trades(frame: pd.DataFrame, asset: str, cost_bps: float) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    last_exit = -1
    cost_rate = float(cost_bps) / 10000.0
    for idx in range(1, len(frame) - 1):
        if idx <= last_exit:
            continue
        direction = int(frame.iloc[idx]["official_dir"])
        if direction == 0:
            continue
        entry_idx = idx + 1
        exit_idx = min(entry_idx + HOLD_BARS - 1, len(frame) - 1)
        entry_price = float(frame.iloc[entry_idx]["open"])
        exit_price = float(frame.iloc[exit_idx]["close"])
        if not (math.isfinite(entry_price) and math.isfinite(exit_price) and entry_price > 0 and exit_price > 0):
            continue
        gross_ret = (exit_price / entry_price - 1.0) * direction
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
        rows.append(
            {
                "asset": asset,
                "event_ts": pd.to_datetime(frame.iloc[idx]["timestamp"], utc=True),
                "entry_ts": pd.to_datetime(frame.iloc[entry_idx]["timestamp"], utc=True),
                "exit_ts": pd.to_datetime(frame.iloc[exit_idx]["timestamp"], utc=True),
                "direction": "long" if direction > 0 else "short",
                "direction_sign": direction,
                "entry_price": entry_price,
                "exit_price": exit_price,
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "hold_bars": int(exit_idx - entry_idx + 1),
                "slope_strength": float(frame.iloc[idx]["slope_strength"]),
            }
        )
        last_exit = exit_idx
    return pd.DataFrame(rows)


def summarize_asset_window(trades: pd.DataFrame, available: bool) -> dict[str, object]:
    if not available:
        return {"asset_return": np.nan, "trades": 0, "win_rate": np.nan, "active": 0}
    if trades.empty:
        return {"asset_return": 0.0, "trades": 0, "win_rate": np.nan, "active": 1}
    return {
        "asset_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
        "trades": int(len(trades)),
        "win_rate": float((trades["net_ret"] > 0).mean()),
        "active": 1,
    }


def build_benchmark_features(bar_map: dict[str, pd.DataFrame]) -> pd.DataFrame:
    close_frames = []
    for asset, bars in bar_map.items():
        close_frames.append(bars[["timestamp", "close"]].rename(columns={"close": asset}).set_index("timestamp"))
    merged = pd.concat(close_frames, axis=1).sort_index()
    rets = merged.pct_change(fill_method=None).replace([np.inf, -np.inf], np.nan)
    eq_ret = rets.mean(axis=1, skipna=True)
    eq_close = (1.0 + eq_ret.fillna(0.0)).cumprod()
    out = pd.DataFrame({"timestamp": eq_close.index, "eq_close": eq_close.values, "eq_ret": eq_ret.values})
    if "BTC-USD" in merged.columns:
        out = out.merge(merged[["BTC-USD"]].reset_index().rename(columns={"BTC-USD": "btc_close"}), on="timestamp", how="left")
    else:
        out["btc_close"] = np.nan
    return out.sort_values("timestamp").reset_index(drop=True)


def classify_direction(eq_ret: float, breadth: float) -> str:
    if pd.notna(eq_ret) and pd.notna(breadth):
        if eq_ret >= 0.15 and breadth >= 0.60:
            return "bull"
        if eq_ret <= -0.15 and breadth <= 0.40:
            return "bear"
    return "flat_mixed"


def bucketize(series: pd.Series, labels: list[str]) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    valid = s.dropna()
    if valid.empty:
        return pd.Series([np.nan] * len(s), index=s.index)
    uniq = valid.nunique()
    if uniq == 1:
        return pd.Series([labels[len(labels)//2]] * len(s), index=s.index)
    q = min(len(labels), uniq)
    cut = pd.qcut(valid.rank(method="first"), q=q, labels=labels[:q])
    out = pd.Series(index=s.index, dtype=object)
    out.loc[valid.index] = cut.astype(str)
    return out


def build_window_tables(bar_map: dict[str, pd.DataFrame], trade_map_by_cost: dict[float, dict[str, pd.DataFrame]]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, object]]:
    benchmark = build_benchmark_features(bar_map)
    quarter_index = benchmark.copy()
    quarter_index["quarter"] = quarter_index["timestamp"].dt.tz_convert(None).dt.to_period("Q").astype(str)
    win_rows: list[dict[str, object]] = []

    for quarter, grp in quarter_index.groupby("quarter", sort=True):
        start_ts = pd.to_datetime(grp["timestamp"].min(), utc=True)
        end_ts = pd.to_datetime(grp["timestamp"].max(), utc=True)
        window_days = int((end_ts - start_ts).total_seconds() // 86400) + 1
        is_full_window = int(window_days >= 75)
        eq_close = grp["eq_close"].dropna()
        btc_close = grp["btc_close"].dropna()
        eq_ret_3m = float(eq_close.iloc[-1] / eq_close.iloc[0] - 1.0) if len(eq_close) >= 2 else np.nan
        btc_ret_3m = float(btc_close.iloc[-1] / btc_close.iloc[0] - 1.0) if len(btc_close) >= 2 else np.nan
        eq_bar_ret = pd.to_numeric(grp["eq_ret"], errors="coerce").dropna()
        ew_vol_ann = float(eq_bar_ret.std(ddof=0) * math.sqrt(365 * 24 * 4)) if len(eq_bar_ret) >= 2 else np.nan
        ew_eff = float(abs(eq_ret_3m) / eq_bar_ret.abs().sum()) if len(eq_bar_ret) >= 2 and eq_bar_ret.abs().sum() > 0 else np.nan

        asset_rets = []
        listed_assets = 0
        for asset, bars in bar_map.items():
            sub = bars[(bars["timestamp"] >= start_ts) & (bars["timestamp"] <= end_ts)]
            if len(sub) >= 2:
                listed_assets += 1
                asset_rets.append(float(sub.iloc[-1]["close"] / sub.iloc[0]["close"] - 1.0))
        breadth_pos = float(np.mean(np.array(asset_rets) > 0)) if asset_rets else np.nan
        dispersion = float(np.std(asset_rets, ddof=0)) if len(asset_rets) >= 2 else np.nan

        for cost, trade_map in trade_map_by_cost.items():
            asset_rows = []
            for asset, bars in bar_map.items():
                available = len(bars[(bars["timestamp"] >= start_ts) & (bars["timestamp"] <= end_ts)]) >= 2
                trades = trade_map[asset]
                sub_trades = trades[(trades["entry_ts"] >= start_ts) & (trades["entry_ts"] <= end_ts)].copy()
                s = summarize_asset_window(sub_trades, available)
                asset_rows.append({"asset": asset, **s})
            window_asset = pd.DataFrame(asset_rows)
            active = window_asset[window_asset["active"] == 1].copy()
            mean_total_return = float(active["asset_return"].dropna().mean()) if not active.empty else np.nan
            median_total_return = float(active["asset_return"].dropna().median()) if not active.empty else np.nan
            positive_asset_ratio = float((active["asset_return"].fillna(-np.inf) > 0).mean()) if not active.empty else np.nan
            active_asset_ratio = float((window_asset["trades"] > 0).mean()) if not window_asset.empty else np.nan
            mean_trades_per_asset = float(window_asset["trades"].mean()) if not window_asset.empty else np.nan
            win_rows.append(
                {
                    "quarter": quarter,
                    "quarter_start": start_ts.strftime("%Y-%m-%d"),
                    "quarter_end": end_ts.strftime("%Y-%m-%d"),
                    "window_days": int(window_days),
                    "is_full_window": int(is_full_window),
                    "market_cost_bps": float(cost),
                    "listed_asset_count": int(listed_assets),
                    "eq_ret_3m": eq_ret_3m,
                    "btc_ret_3m": btc_ret_3m,
                    "breadth_pos": breadth_pos,
                    "ew_vol_ann": ew_vol_ann,
                    "ew_efficiency": ew_eff,
                    "dispersion": dispersion,
                    "mean_total_return": mean_total_return,
                    "median_total_return": median_total_return,
                    "positive_asset_ratio": positive_asset_ratio,
                    "active_asset_ratio": active_asset_ratio,
                    "mean_trades_per_asset": mean_trades_per_asset,
                }
            )
    window_df = pd.DataFrame(win_rows).sort_values(["market_cost_bps", "quarter"]).reset_index(drop=True)

    primary = window_df[(window_df["market_cost_bps"] == PRIMARY_COST) & (window_df["is_full_window"] == 1)].copy().reset_index(drop=True)
    primary["direction_bucket"] = primary.apply(lambda r: classify_direction(r["eq_ret_3m"], r["breadth_pos"]), axis=1)
    primary["efficiency_bucket"] = bucketize(primary["ew_efficiency"], ["choppy", "mid", "trendy"])
    primary["vol_bucket"] = bucketize(primary["ew_vol_ann"], ["low_vol", "mid_vol", "high_vol"])
    primary["dispersion_bucket"] = bucketize(primary["dispersion"], ["low_disp", "mid_disp", "high_disp"])
    primary["regime_combo"] = primary["direction_bucket"].astype(str) + " | " + primary["efficiency_bucket"].astype(str)

    def agg_summary(df: pd.DataFrame, by: list[str]) -> pd.DataFrame:
        rows = []
        for key, grp in df.groupby(by, sort=False, dropna=False):
            if not isinstance(key, tuple):
                key = (key,)
            row = {col: val for col, val in zip(by, key)}
            row.update(
                {
                    "windows": int(len(grp)),
                    "mean_strategy_return": float(grp["mean_total_return"].mean()),
                    "median_strategy_return": float(grp["mean_total_return"].median()),
                    "positive_window_ratio": float((grp["mean_total_return"] > 0).mean()),
                    "mean_positive_asset_ratio": float(grp["positive_asset_ratio"].mean()),
                    "mean_active_asset_ratio": float(grp["active_asset_ratio"].mean()),
                    "mean_eq_ret_3m": float(grp["eq_ret_3m"].mean()),
                    "mean_breadth_pos": float(grp["breadth_pos"].mean()),
                    "mean_ew_vol_ann": float(grp["ew_vol_ann"].mean()),
                    "mean_ew_efficiency": float(grp["ew_efficiency"].mean()),
                }
            )
            rows.append(row)
        return pd.DataFrame(rows)

    direction_summary = agg_summary(primary, ["direction_bucket"])
    efficiency_summary = agg_summary(primary, ["efficiency_bucket"])
    combo_summary = agg_summary(primary, ["direction_bucket", "efficiency_bucket"])

    rankable = primary.dropna(subset=["mean_total_return"]).copy()
    rankable = rankable.sort_values("mean_total_return").reset_index(drop=True)
    top_n = max(len(rankable) // 3, 1)
    bottom_slice = rankable.head(top_n)
    top_slice = rankable.tail(top_n)
    contrast = {
        "top_windows": top_slice["quarter"].tolist(),
        "bottom_windows": bottom_slice["quarter"].tolist(),
        "top_mean_strategy_return": float(top_slice["mean_total_return"].mean()) if not top_slice.empty else np.nan,
        "bottom_mean_strategy_return": float(bottom_slice["mean_total_return"].mean()) if not bottom_slice.empty else np.nan,
        "top_mean_eq_ret_3m": float(top_slice["eq_ret_3m"].mean()) if not top_slice.empty else np.nan,
        "bottom_mean_eq_ret_3m": float(bottom_slice["eq_ret_3m"].mean()) if not bottom_slice.empty else np.nan,
        "top_mean_breadth_pos": float(top_slice["breadth_pos"].mean()) if not top_slice.empty else np.nan,
        "bottom_mean_breadth_pos": float(bottom_slice["breadth_pos"].mean()) if not bottom_slice.empty else np.nan,
        "top_mean_ew_efficiency": float(top_slice["ew_efficiency"].mean()) if not top_slice.empty else np.nan,
        "bottom_mean_ew_efficiency": float(bottom_slice["ew_efficiency"].mean()) if not bottom_slice.empty else np.nan,
        "top_mean_ew_vol_ann": float(top_slice["ew_vol_ann"].mean()) if not top_slice.empty else np.nan,
        "bottom_mean_ew_vol_ann": float(bottom_slice["ew_vol_ann"].mean()) if not bottom_slice.empty else np.nan,
    }
    return window_df, primary, direction_summary, combo_summary, contrast


def build_html(generated_at: str, meta: dict[str, object], overall: pd.DataFrame, primary_windows: pd.DataFrame, direction_summary: pd.DataFrame, combo_summary: pd.DataFrame, contrast: dict[str, object]) -> str:
    headline = (
        f"5 年按季度拆开后，Rank32b（固定持有 8 根 15m、{int(PRIMARY_COST)}bps/side）更偏向在 "
        f"<b>{escape(str(combo_summary.sort_values('mean_strategy_return', ascending=False).iloc[0]['direction_bucket']))}</b> 且 "
        f"<b>{escape(str(combo_summary.sort_values('mean_strategy_return', ascending=False).iloc[0]['efficiency_bucket']))}</b> 的窗口里工作；"
        f"最差窗口更常见于 <b>{escape(str(combo_summary.sort_values('mean_strategy_return', ascending=True).iloc[0]['direction_bucket']))}</b> + "
        f"<b>{escape(str(combo_summary.sort_values('mean_strategy_return', ascending=True).iloc[0]['efficiency_bucket']))}</b>。"
    ) if not combo_summary.empty else "暂无 headline。"
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank32b 5y quarterly regime study</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1200px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background: #f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .muted {{ color:#6b7280; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
  </style>
</head>
<body>
  <h1>Rank32b · 5 年 × 3 个月 regime 研究</h1>
  <p class='muted'>生成时间：{escape(generated_at)} ｜ universe={escape(str(meta['asset_count']))} assets ｜ days={escape(str(meta['days']))} ｜ baseline=official close + fixed hold {HOLD_BARS} bars</p>

  <div class='card'>
    <h2>研究设计</h2>
    <ul>
      <li>先只研究 32b alpha 本体，不把 live TP/SL/timeout 混进来。</li>
      <li>执行口径固定：<code>15m official close -> next-bar open -> hold {HOLD_BARS} bars -> non-overlap</code>。</li>
      <li>把过去 5 年按自然季度（3 个月）拆开，回答：哪些市场季度更适合它、哪些季度不适合。</li>
      <li>regime 不用未来标签瞎分，而是只用季度内可观察统计：<code>equal-weight 3m return / breadth / realized vol / efficiency ratio</code>。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>一句话结论</h2>
    <p><b>{headline}</b></p>
    <ul>
      <li>Top tercile 季度：strategy mean return≈{pct(contrast.get('top_mean_strategy_return'))}，eq 3m return≈{pct(contrast.get('top_mean_eq_ret_3m'))}，breadth≈{pct(contrast.get('top_mean_breadth_pos'))}，efficiency≈{num(contrast.get('top_mean_ew_efficiency'), 3)}。</li>
      <li>Bottom tercile 季度：strategy mean return≈{pct(contrast.get('bottom_mean_strategy_return'))}，eq 3m return≈{pct(contrast.get('bottom_mean_eq_ret_3m'))}，breadth≈{pct(contrast.get('bottom_mean_breadth_pos'))}，efficiency≈{num(contrast.get('bottom_mean_ew_efficiency'), 3)}。</li>
      <li>直白点：如果市场是<b>同向更整齐、breadth 更广、路径更顺</b>，32b 更像 continuation；如果市场是<b>震荡混合 / 路径更碎</b>，它更容易被来回打脸。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>成本总览</h2>
    {render_table(overall[['market_cost_bps','quarters','mean_strategy_return','median_strategy_return','positive_quarter_ratio','mean_positive_asset_ratio','mean_active_asset_ratio','mean_trades_per_asset']], percent_cols={'mean_strategy_return','median_strategy_return','positive_quarter_ratio','mean_positive_asset_ratio','mean_active_asset_ratio'}, digits_cols={'market_cost_bps':0,'quarters':0,'mean_trades_per_asset':2})}
  </div>

  <div class='card'>
    <h2>按方向 bucket 看（primary = {int(PRIMARY_COST)}bps/side）</h2>
    {render_table(direction_summary[['direction_bucket','windows','mean_strategy_return','median_strategy_return','positive_window_ratio','mean_positive_asset_ratio','mean_active_asset_ratio','mean_eq_ret_3m','mean_breadth_pos','mean_ew_vol_ann','mean_ew_efficiency']], percent_cols={'mean_strategy_return','median_strategy_return','positive_window_ratio','mean_positive_asset_ratio','mean_active_asset_ratio','mean_eq_ret_3m','mean_breadth_pos','mean_ew_vol_ann'}, digits_cols={'windows':0,'mean_ew_efficiency':3})}
  </div>

  <div class='card'>
    <h2>按方向 × 路径平滑度看</h2>
    {render_table(combo_summary[['direction_bucket','efficiency_bucket','windows','mean_strategy_return','median_strategy_return','positive_window_ratio','mean_positive_asset_ratio','mean_eq_ret_3m','mean_breadth_pos','mean_ew_vol_ann','mean_ew_efficiency']], percent_cols={'mean_strategy_return','median_strategy_return','positive_window_ratio','mean_positive_asset_ratio','mean_eq_ret_3m','mean_breadth_pos','mean_ew_vol_ann'}, digits_cols={'windows':0,'mean_ew_efficiency':3})}
  </div>

  <div class='card'>
    <h2>季度明细（primary = {int(PRIMARY_COST)}bps/side）</h2>
    {render_table(primary_windows[['quarter','quarter_start','quarter_end','window_days','direction_bucket','efficiency_bucket','vol_bucket','listed_asset_count','eq_ret_3m','btc_ret_3m','breadth_pos','ew_vol_ann','ew_efficiency','mean_total_return','positive_asset_ratio','active_asset_ratio','mean_trades_per_asset']], percent_cols={'eq_ret_3m','btc_ret_3m','breadth_pos','ew_vol_ann','mean_total_return','positive_asset_ratio','active_asset_ratio'}, digits_cols={'window_days':0,'listed_asset_count':0,'mean_trades_per_asset':2,'ew_efficiency':3})}
  </div>
</body>
</html>
"""


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description='Rank32b 5y quarterly regime study')
    parser.add_argument('--days', type=int, default=DEFAULT_DAYS)
    parser.add_argument('--refresh', action='store_true')
    parser.add_argument('--max-symbols', type=int, default=0)
    parser.add_argument('--tag', default='')
    args = parser.parse_args()

    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(CACHE_DIR)

    assets = dict(ASSETS)
    if args.max_symbols and args.max_symbols > 0:
        assets = dict(list(assets.items())[:args.max_symbols])
    tag = args.tag.strip() or f"{len(assets)}assets_{args.days}d"
    run_dir = ensure_dir(ART_DIR / tag)
    site_path = SITE_DIR / f"{tag}.html"

    bar_map: dict[str, pd.DataFrame] = {}
    trade_map_by_cost: dict[float, dict[str, pd.DataFrame]] = {cost: {} for cost in COSTS}
    meta_rows: list[dict[str, object]] = []

    for i, (asset, symbol) in enumerate(assets.items(), start=1):
        print(f"[{i}/{len(assets)}] {asset} {symbol}", flush=True)
        bars = load_or_fetch_15m(symbol, days=args.days, refresh=args.refresh)
        if bars.empty or len(bars) < 2000:
            meta_rows.append({"asset": asset, "symbol": symbol, "status": 'empty'})
            continue
        bar_map[asset] = bars
        frame = build_frame_from_bars(asset, bars)
        frame.to_csv(run_dir / f"frame_{asset.lower().replace('-usd','')}.csv", index=False)
        meta_rows.append({
            'asset': asset,
            'symbol': symbol,
            'status': 'ok',
            'bars': int(len(bars)),
            'start': pd.to_datetime(bars['timestamp'].min(), utc=True).strftime('%Y-%m-%d'),
            'end': pd.to_datetime(bars['timestamp'].max(), utc=True).strftime('%Y-%m-%d'),
        })
        for cost in COSTS:
            trades = build_trades(frame, asset=asset, cost_bps=cost)
            trade_map_by_cost[cost][asset] = trades
    if not bar_map:
        raise SystemExit('No bars loaded')

    window_df, primary_windows, direction_summary, combo_summary, contrast = build_window_tables(bar_map, trade_map_by_cost)
    overall_rows = []
    full_window_df = window_df[window_df['is_full_window'] == 1].copy()
    for cost, grp in full_window_df.groupby('market_cost_bps', sort=True):
        overall_rows.append({
            'market_cost_bps': float(cost),
            'quarters': int(len(grp)),
            'mean_strategy_return': float(grp['mean_total_return'].mean()),
            'median_strategy_return': float(grp['mean_total_return'].median()),
            'positive_quarter_ratio': float((grp['mean_total_return'] > 0).mean()),
            'mean_positive_asset_ratio': float(grp['positive_asset_ratio'].mean()),
            'mean_active_asset_ratio': float(grp['active_asset_ratio'].mean()),
            'mean_trades_per_asset': float(grp['mean_trades_per_asset'].mean()),
        })
    overall = pd.DataFrame(overall_rows)

    meta = {
        'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
        'days': int(args.days),
        'asset_count': len(bar_map),
        'assets': list(bar_map.keys()),
        'tag': tag,
        'primary_cost_bps': PRIMARY_COST,
        'hold_bars': HOLD_BARS,
        'meta_rows': meta_rows,
        'contrast': contrast,
    }

    pd.DataFrame(meta_rows).to_csv(run_dir / 'asset_meta.csv', index=False)
    overall.to_csv(run_dir / 'overall_summary.csv', index=False)
    window_df.to_csv(run_dir / 'quarter_window_summary.csv', index=False)
    primary_windows.to_csv(run_dir / 'quarter_window_primary.csv', index=False)
    direction_summary.to_csv(run_dir / 'direction_bucket_summary.csv', index=False)
    combo_summary.to_csv(run_dir / 'direction_efficiency_summary.csv', index=False)
    (run_dir / 'meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    site_path.write_text(build_html(meta['generated_at'], meta, overall, primary_windows, direction_summary, combo_summary, contrast), encoding='utf-8')

    print('\n=== overall_summary ===')
    print(overall.to_string(index=False))
    print(f'\nartifacts: {run_dir}')
    print(f'site: {site_path}')


if __name__ == '__main__':
    main()
