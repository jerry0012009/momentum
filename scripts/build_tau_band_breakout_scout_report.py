#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_tau_band_breakout_15m"
CACHE_DIR = ART_DIR / "cache"
REPORT_PATH = SITE_DIR / "report.html"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
DAYS = 120
INTERVAL = "15m"
EMA_FAST = 20
EMA_SLOW = 50
DONCHIAN_LOOKBACK = 20
ATR_PERIOD = 14
STOP_ATR = 1.0
TARGET_ATR = 2.0
TIME_STOP_BARS = 8
COST_BPS_PER_SIDE = 6.0
CACHE_HOURS = 6

VARIANTS = [
    {"variant": "raw_breakout", "tau_atr": 0.00, "confirm_mode": "transition"},
    {"variant": "tau_005_breakout", "tau_atr": 0.05, "confirm_mode": "transition"},
    {"variant": "tau_010_breakout", "tau_atr": 0.10, "confirm_mode": "transition"},
    {"variant": "tau_020_breakout", "tau_atr": 0.20, "confirm_mode": "transition"},
    {"variant": "confirm2of3_tau_010", "tau_atr": 0.10, "confirm_mode": "2of3"},
]


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path



def pct(value: float | int | None, digits: int = 2) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{float(value) * 100:.{digits}f}%"



def num(value: float | int | None, digits: int = 2) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{float(value):.{digits}f}"



def fmt_ts(ts) -> str:
    if ts is None or pd.isna(ts):
        return "-"
    return pd.to_datetime(ts, utc=True).strftime("%Y-%m-%d %H:%M UTC")



def cache_path_for(symbol: str) -> Path:
    return CACHE_DIR / f"{symbol}__{DAYS}d__{INTERVAL}.csv"



def cache_is_fresh(path: Path) -> bool:
    if not path.exists():
        return False
    age_hours = (datetime.now(timezone.utc).timestamp() - path.stat().st_mtime) / 3600.0
    return age_hours <= CACHE_HOURS



def download_binance_bars(symbol: str) -> pd.DataFrame:
    ensure_dir(CACHE_DIR)
    cache_path = cache_path_for(symbol)
    if cache_is_fresh(cache_path):
        df = pd.read_csv(cache_path)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        return df.sort_values("timestamp").reset_index(drop=True)

    end_ms = int(pd.Timestamp.now("UTC").timestamp() * 1000)
    start_ms = end_ms - DAYS * 24 * 60 * 60 * 1000
    url = "https://api.binance.com/api/v3/klines"
    rows: list[list] = []
    current = start_ms

    while current < end_ms:
        qs = urlencode(
            {
                "symbol": symbol,
                "interval": INTERVAL,
                "startTime": current,
                "endTime": end_ms,
                "limit": 1000,
            }
        )
        with urlopen(f"{url}?{qs}", timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if not data:
            break
        rows.extend(data)
        current = int(data[-1][6]) + 1
        if len(data) < 1000:
            break

    if not rows:
        raise ValueError(f"No Binance bars downloaded for {symbol}")

    raw = pd.DataFrame(
        rows,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base_asset_volume",
            "taker_buy_quote_asset_volume",
            "ignore",
        ],
    )
    bars = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(raw["open_time"], unit="ms", utc=True),
            "open": pd.to_numeric(raw["open"], errors="coerce"),
            "high": pd.to_numeric(raw["high"], errors="coerce"),
            "low": pd.to_numeric(raw["low"], errors="coerce"),
            "close": pd.to_numeric(raw["close"], errors="coerce"),
            "volume": pd.to_numeric(raw["volume"], errors="coerce"),
        }
    ).dropna()
    bars = bars.sort_values("timestamp").reset_index(drop=True)
    bars.to_csv(cache_path, index=False)
    return bars



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
    return tr.rolling(period, min_periods=period).mean()



def prepare_bars(asset: str, symbol: str) -> pd.DataFrame:
    bars = download_binance_bars(symbol).copy()
    bars["asset"] = asset
    bars["ema_fast"] = bars["close"].ewm(span=EMA_FAST, adjust=False).mean()
    bars["ema_slow"] = bars["close"].ewm(span=EMA_SLOW, adjust=False).mean()
    bars["long_bias"] = (bars["ema_fast"] > bars["ema_slow"]).astype(int)
    bars["short_bias"] = (bars["ema_fast"] < bars["ema_slow"]).astype(int)
    bars["donchian_upper"] = bars["high"].shift(1).rolling(DONCHIAN_LOOKBACK, min_periods=DONCHIAN_LOOKBACK).max()
    bars["donchian_lower"] = bars["low"].shift(1).rolling(DONCHIAN_LOOKBACK, min_periods=DONCHIAN_LOOKBACK).min()
    bars["atr"] = compute_atr(bars, ATR_PERIOD)
    return bars



def build_variant_signals(bars: pd.DataFrame, *, tau_atr: float, confirm_mode: str, variant: str) -> pd.DataFrame:
    out = bars.copy()
    out["tau_atr"] = float(tau_atr)
    out["variant"] = variant
    out["threshold_upper"] = out["donchian_upper"] + float(tau_atr) * out["atr"]
    out["threshold_lower"] = out["donchian_lower"] - float(tau_atr) * out["atr"]

    out["long_outside"] = ((out["long_bias"] == 1) & (out["close"] > out["threshold_upper"])).fillna(False)
    out["short_outside"] = ((out["short_bias"] == 1) & (out["close"] < out["threshold_lower"])).fillna(False)

    if confirm_mode == "2of3":
        out["long_ready"] = (
            out["long_outside"]
            & (out["long_outside"].rolling(3, min_periods=3).sum() >= 2)
        ).fillna(False)
        out["short_ready"] = (
            out["short_outside"]
            & (out["short_outside"].rolling(3, min_periods=3).sum() >= 2)
        ).fillna(False)
    else:
        out["long_ready"] = out["long_outside"].fillna(False)
        out["short_ready"] = out["short_outside"].fillna(False)

    out["long_signal"] = (out["long_ready"] & (~out["long_ready"].shift(1).fillna(False))).astype(int)
    out["short_signal"] = (out["short_ready"] & (~out["short_ready"].shift(1).fillna(False))).astype(int)
    return out



def _safe_float(value) -> float:
    try:
        out = float(value)
    except Exception:
        return float("nan")
    return out if math.isfinite(out) else float("nan")



def simulate_variant_trades(signal_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = signal_df.copy().reset_index(drop=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    cost_rate = COST_BPS_PER_SIDE / 10000.0
    trades: list[dict] = []
    nav = 1.0
    nav_rows = [{"asset": df.iloc[0]["asset"], "variant": df.iloc[0]["variant"], "timestamp": df.iloc[0]["timestamp"], "nav": nav}]

    j = 1
    n = len(df)
    while j < n:
        signal_row = df.iloc[j - 1]
        if int(signal_row["long_signal"]) == 1 and int(signal_row["short_signal"]) == 0:
            side = "long"
        elif int(signal_row["short_signal"]) == 1 and int(signal_row["long_signal"]) == 0:
            side = "short"
        else:
            j += 1
            continue

        entry_row = df.iloc[j]
        entry_price = _safe_float(entry_row["open"])
        atr = _safe_float(signal_row["atr"])
        if not (math.isfinite(entry_price) and entry_price > 0 and math.isfinite(atr) and atr > 0):
            j += 1
            continue

        signal_idx = j - 1
        entry_idx = j
        raw_edge = _safe_float(signal_row["donchian_upper"] if side == "long" else signal_row["donchian_lower"])
        threshold_edge = _safe_float(signal_row["threshold_upper"] if side == "long" else signal_row["threshold_lower"])
        stop_price = entry_price - STOP_ATR * atr if side == "long" else entry_price + STOP_ATR * atr
        target_price = entry_price + TARGET_ATR * atr if side == "long" else entry_price - TARGET_ATR * atr

        future = df.iloc[signal_idx + 1 : min(signal_idx + 4, n)].copy()
        if side == "long":
            false_break = int((future["close"] <= raw_edge).any()) if math.isfinite(raw_edge) else np.nan
            outside_persist = int((future["close"] > threshold_edge).sum()) if math.isfinite(threshold_edge) else np.nan
        else:
            false_break = int((future["close"] >= raw_edge).any()) if math.isfinite(raw_edge) else np.nan
            outside_persist = int((future["close"] < threshold_edge).sum()) if math.isfinite(threshold_edge) else np.nan

        exit_idx = None
        exit_price = None
        exit_reason = None
        last_bar_idx = min(entry_idx + TIME_STOP_BARS - 1, n - 1)
        for k in range(entry_idx, last_bar_idx + 1):
            bar = df.iloc[k]
            low = _safe_float(bar["low"])
            high = _safe_float(bar["high"])
            if side == "long":
                if math.isfinite(low) and low <= stop_price:
                    exit_idx = k
                    exit_price = stop_price
                    exit_reason = "atr_stop"
                    break
                if math.isfinite(high) and high >= target_price:
                    exit_idx = k
                    exit_price = target_price
                    exit_reason = "atr_target"
                    break
            else:
                if math.isfinite(high) and high >= stop_price:
                    exit_idx = k
                    exit_price = stop_price
                    exit_reason = "atr_stop"
                    break
                if math.isfinite(low) and low <= target_price:
                    exit_idx = k
                    exit_price = target_price
                    exit_reason = "atr_target"
                    break

        if exit_idx is None:
            exit_idx = last_bar_idx
            exit_price = _safe_float(df.iloc[exit_idx]["close"])
            exit_reason = "time_stop"

        if not (math.isfinite(exit_price) and exit_price > 0):
            j = exit_idx + 1
            continue

        if side == "long":
            gross_mult = exit_price / entry_price
        else:
            gross_mult = entry_price / exit_price
        net_mult = gross_mult * (1.0 - cost_rate) * (1.0 - cost_rate)
        net_ret = net_mult - 1.0
        nav *= net_mult
        trades.append(
            {
                "asset": signal_row["asset"],
                "variant": signal_row["variant"],
                "tau_atr": signal_row["tau_atr"],
                "confirm_mode": "2of3" if "confirm2of3" in str(signal_row["variant"]) else "transition",
                "side": side,
                "signal_ts": signal_row["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_ts": entry_row["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": df.iloc[exit_idx]["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_price": entry_price,
                "exit_price": exit_price,
                "atr_at_signal": atr,
                "raw_edge": raw_edge,
                "threshold_edge": threshold_edge,
                "false_break_3bars": false_break,
                "outside_persistence_3bars": outside_persist,
                "gross_ret": gross_mult - 1.0,
                "net_ret": net_ret,
                "hold_bars": int(exit_idx - entry_idx + 1),
                "exit_reason": exit_reason,
                "win": int(net_ret > 0),
            }
        )
        nav_rows.append({"asset": signal_row["asset"], "variant": signal_row["variant"], "timestamp": df.iloc[exit_idx]["timestamp"], "nav": nav})
        j = exit_idx + 1

    return pd.DataFrame(trades), pd.DataFrame(nav_rows)



def summarize_trades(trades: pd.DataFrame, nav: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(
            [
                {
                    "asset": nav.iloc[0]["asset"] if not nav.empty else "-",
                    "variant": nav.iloc[0]["variant"] if not nav.empty else "-",
                    "trades": 0,
                    "win_rate": np.nan,
                    "avg_net_ret": np.nan,
                    "median_net_ret": np.nan,
                    "total_return": 0.0,
                    "max_drawdown": 0.0,
                    "false_break_ratio": np.nan,
                    "outside_persistence_3bars": np.nan,
                    "avg_hold_bars": np.nan,
                    "long_trades": 0,
                    "short_trades": 0,
                }
            ]
        )

    running_peak = nav["nav"].cummax() if not nav.empty else pd.Series(dtype=float)
    drawdown = nav["nav"] / running_peak - 1.0 if not nav.empty else pd.Series(dtype=float)
    max_dd = float(drawdown.min()) if len(drawdown) else 0.0
    return pd.DataFrame(
        [
            {
                "asset": str(trades.iloc[0]["asset"]),
                "variant": str(trades.iloc[0]["variant"]),
                "trades": int(len(trades)),
                "win_rate": float(trades["win"].mean()),
                "avg_net_ret": float(trades["net_ret"].mean()),
                "median_net_ret": float(trades["net_ret"].median()),
                "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
                "max_drawdown": max_dd,
                "false_break_ratio": float(trades["false_break_3bars"].mean()),
                "outside_persistence_3bars": float(trades["outside_persistence_3bars"].mean()),
                "avg_hold_bars": float(trades["hold_bars"].mean()),
                "long_trades": int((trades["side"] == "long").sum()),
                "short_trades": int((trades["side"] == "short").sum()),
            }
        ]
    )



def build_variant_aggregate(asset_summary: pd.DataFrame) -> pd.DataFrame:
    if asset_summary.empty:
        return pd.DataFrame()
    out = (
        asset_summary.groupby("variant", as_index=False)
        .agg(
            assets_tested=("asset", "nunique"),
            positive_assets=("total_return", lambda s: int((s > 0).sum())),
            mean_total_return=("total_return", "mean"),
            median_total_return=("total_return", "median"),
            mean_max_drawdown=("max_drawdown", "mean"),
            mean_false_break_ratio=("false_break_ratio", "mean"),
            mean_outside_persistence_3bars=("outside_persistence_3bars", "mean"),
            mean_trades=("trades", "mean"),
            mean_win_rate=("win_rate", "mean"),
        )
        .sort_values(["mean_total_return", "mean_false_break_ratio"], ascending=[False, True])
        .reset_index(drop=True)
    )
    out["positive_asset_ratio"] = out["positive_assets"] / out["assets_tested"].replace(0, np.nan)
    return out



def render_table(df: pd.DataFrame, *, percent_cols: set[str], digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return "<p class=\"muted\">暂无数据。</p>"
    digits_cols = digits_cols or {}
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    body_rows = []
    for _, row in df.iterrows():
        cells = []
        for col in df.columns:
            value = row[col]
            if col in percent_cols:
                text = pct(value)
            elif isinstance(value, (float, np.floating, int, np.integer)) and not isinstance(value, bool):
                text = num(value, digits_cols.get(col, 2))
            else:
                text = str(value)
            cells.append(f"<td>{escape(text)}</td>")
        body_rows.append(f"<tr>{''.join(cells)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"



def derive_verdict(variant_aggregate: pd.DataFrame) -> tuple[str, list[str]]:
    if variant_aggregate.empty:
        return "无结果", ["样本为空，未能生成 first verdict。"]

    raw = variant_aggregate[variant_aggregate["variant"] == "raw_breakout"]
    raw_row = raw.iloc[0] if not raw.empty else None
    challengers = variant_aggregate[variant_aggregate["variant"] != "raw_breakout"].copy()
    beaters = challengers
    if raw_row is not None:
        beaters = challengers[
            (challengers["mean_total_return"] > float(raw_row["mean_total_return"]))
            & (challengers["mean_false_break_ratio"] < float(raw_row["mean_false_break_ratio"]))
        ]
    if beaters.empty:
        headline = "hard verdict：本轮没有出现 replace-ready winner；τ-band 更像 execution guard challenger。"
    else:
        best = beaters.sort_values(["mean_total_return", "mean_false_break_ratio"], ascending=[False, True]).iloc[0]
        if float(best["mean_total_return"]) <= 0 or float(best.get("positive_asset_ratio", 0.0) or 0.0) <= 0:
            headline = (
                f"hard verdict：{best['variant']} 只是相对 raw 更不差，但绝对 post-cost return 仍为负；"
                "保留为 scout follow-up / execution guard 候选，不是 replace-ready winner。"
            )
        else:
            headline = f"hard verdict：{best['variant']} 同时提高平均 post-cost return 且降低假突破率，可进入下一轮更正式复核。"

    bullets: list[str] = []
    if raw_row is not None:
        best_guard = challengers.sort_values("mean_false_break_ratio", ascending=True).iloc[0] if not challengers.empty else None
        best_return = challengers.sort_values("mean_total_return", ascending=False).iloc[0] if not challengers.empty else None
        bullets.append(
            f"baseline raw_breakout：mean_total_return {pct(raw_row['mean_total_return'])}，mean_false_break_ratio {pct(raw_row['mean_false_break_ratio'])}，mean_trades {num(raw_row['mean_trades'])}。"
        )
        if best_guard is not None:
            bullets.append(
                f"最强 guard 是 {best_guard['variant']}：假突破率 {pct(best_guard['mean_false_break_ratio'])}，但平均收益 {pct(best_guard['mean_total_return'])}。"
            )
        if best_return is not None:
            bullets.append(
                f"收益最好的 challenger 是 {best_return['variant']}：mean_total_return {pct(best_return['mean_total_return'])}，假突破率 {pct(best_return['mean_false_break_ratio'])}。"
            )
        if beaters.empty:
            bullets.append("因此它还不该直接替换当前 Live Seat；更合理身份是 breakout 的 confirmation / no-trade execution guard 候选。")
        else:
            best = beaters.sort_values(["mean_total_return", "mean_false_break_ratio"], ascending=[False, True]).iloc[0]
            if float(best["mean_total_return"]) <= 0 or float(best.get("positive_asset_ratio", 0.0) or 0.0) <= 0:
                bullets.append("它可以作为相对更稳的 filter 继续复核，但当前绝对收益仍为负，不足以改写成 replace-ready / tiny-live 候选。")
            else:
                bullets.append("因此它已具备进入下一轮更正式 review continuation 的资格，但还不是 tiny-live 直接准入。")
    return headline, bullets



def write_report(variant_aggregate: pd.DataFrame, asset_summary: pd.DataFrame, trial_meta: pd.DataFrame) -> None:
    ensure_dir(SITE_DIR)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    verdict_headline, verdict_bullets = derive_verdict(variant_aggregate)
    meta = trial_meta.iloc[0].to_dict() if not trial_meta.empty else {}

    summary_cols = [
        "variant",
        "assets_tested",
        "positive_assets",
        "positive_asset_ratio",
        "mean_total_return",
        "median_total_return",
        "mean_max_drawdown",
        "mean_false_break_ratio",
        "mean_outside_persistence_3bars",
        "mean_trades",
        "mean_win_rate",
    ]
    asset_cols = [
        "asset",
        "variant",
        "trades",
        "win_rate",
        "total_return",
        "max_drawdown",
        "false_break_ratio",
        "outside_persistence_3bars",
        "avg_hold_bars",
    ]
    summary_table = render_table(
        variant_aggregate[summary_cols],
        percent_cols={"positive_asset_ratio", "mean_total_return", "median_total_return", "mean_max_drawdown", "mean_false_break_ratio", "mean_win_rate"},
        digits_cols={"mean_trades": 1, "mean_outside_persistence_3bars": 2},
    )
    asset_table = render_table(
        asset_summary[asset_cols],
        percent_cols={"win_rate", "total_return", "max_drawdown", "false_break_ratio"},
        digits_cols={"trades": 0, "outside_persistence_3bars": 2, "avg_hold_bars": 2},
    )
    bullets_html = "".join(f"<li>{escape(item)}</li>" for item in verdict_bullets)

    html = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Scout τ-band breakout filter · 15m crypto</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1120px; margin: 40px auto; padding: 0 18px; line-height: 1.68; color: #111827; background: #f8fafc; }}
    h1,h2,h3 {{ line-height: 1.25; }}
    .muted {{ color:#6b7280; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    ul,ol {{ padding-left: 20px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    a {{ color:#2563eb; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
  </style>
</head>
<body>
  <p><a href=\"../../index.html\">← 返回首页</a></p>
  <h1>Scout Seat · τ-band / no-trade breakout filter · 15m crypto first verdict</h1>
  <p class=\"muted\">生成时间：{generated_at} ｜ 本页对应 `TODO.md` 当前窗口的 Run 2：在 EMA waiting-window + breakout cooldown 下，对 Rank 1 的 τ-band/no-trade breakout filter 做一刀本地最小实验。</p>

  <div class=\"card\">
    <h2>hard verdict</h2>
    <p><b>{escape(verdict_headline)}</b></p>
    <ul>{bullets_html}</ul>
  </div>

  <div class=\"card\">
    <h2>本轮实验口径</h2>
    <ul>
      <li>资产：<code>{escape(str(meta.get('assets', 'BTC-USD, ETH-USD, SOL-USD')))}</code></li>
      <li>样本：<code>{escape(str(meta.get('sample_window', 'Binance 120d 15m')))}</code></li>
      <li>方向层：<code>EMA{EMA_FAST} &gt; EMA{EMA_SLOW}</code> 只做多，反之只做空</li>
      <li>触发层：<code>Donchian({DONCHIAN_LOOKBACK})</code> 上下沿</li>
      <li>对照组：<code>raw_breakout</code>、<code>tau_005/010/020_breakout</code>、<code>confirm2of3_tau_010</code></li>
      <li>出场：<code>1 ATR stop / 2 ATR target / 8-bar time stop</code></li>
      <li>成本：<code>{COST_BPS_PER_SIDE:.0f}bps/side</code>（fee+slippage 合并口径）</li>
      <li>假突破定义：信号后 3 根内重新收回原始 Donchian 区间；站稳度量：未来 3 根里仍站在 threshold 外的收盘根数</li>
    </ul>
    <p class=\"muted\">artifact：<code>reports/artifacts/scout_tau_band_breakout_15m/variant_aggregate.csv</code>、<code>asset_summary.csv</code>、<code>trades.csv</code>、<code>trial_meta.csv</code></p>
  </div>

  <div class=\"card\">
    <h2>variant aggregate（按跨资产 mean_total_return 排序）</h2>
    {summary_table}
  </div>

  <div class=\"card\">
    <h2>per-asset summary</h2>
    {asset_table}
  </div>

  <div class=\"card\">
    <h2>怎么读这页</h2>
    <ul>
      <li>如果某个 τ-band 版本只是单纯把交易砍少、但收益和假突破都没一起改善，那它更像过度过滤。</li>
      <li>如果某个版本把 <code>false_break_ratio</code> 压下来了、但收益没有跟着塌，就值得继续当 execution guard 复核。</li>
      <li>本页只回答最小 first verdict：它是不是比 raw 更像值得继续看的 confirmation / no-trade 候选；不在这里直接宣称可以替换当前 Live Seat。</li>
    </ul>
  </div>
</body>
</html>
"""
    REPORT_PATH.write_text(html, encoding="utf-8")



def main() -> int:
    ensure_dir(ART_DIR)
    all_trades = []
    all_nav = []
    all_summaries = []
    cache_meta = []

    for asset, symbol in ASSETS.items():
        bars = prepare_bars(asset, symbol)
        cache_meta.append(
            {
                "asset": asset,
                "symbol": symbol,
                "cache_path": str(cache_path_for(symbol).relative_to(ROOT)),
                "bars": int(len(bars)),
                "first_bar_utc": fmt_ts(bars["timestamp"].min()),
                "last_bar_utc": fmt_ts(bars["timestamp"].max()),
            }
        )
        for variant_cfg in VARIANTS:
            sig = build_variant_signals(bars, **variant_cfg)
            trades, nav = simulate_variant_trades(sig)
            summary = summarize_trades(trades, nav)
            all_trades.append(trades)
            all_nav.append(nav)
            all_summaries.append(summary)

    trades_df = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    nav_df = pd.concat(all_nav, ignore_index=True) if all_nav else pd.DataFrame()
    asset_summary = pd.concat(all_summaries, ignore_index=True) if all_summaries else pd.DataFrame()
    variant_aggregate = build_variant_aggregate(asset_summary)
    verdict_headline, _ = derive_verdict(variant_aggregate)

    trial_meta = pd.DataFrame(
        [
            {
                "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                "assets": ", ".join(ASSETS.keys()),
                "sample_window": f"Binance {DAYS}d {INTERVAL}",
                "ema_fast": EMA_FAST,
                "ema_slow": EMA_SLOW,
                "donchian_lookback": DONCHIAN_LOOKBACK,
                "atr_period": ATR_PERIOD,
                "stop_atr": STOP_ATR,
                "target_atr": TARGET_ATR,
                "time_stop_bars": TIME_STOP_BARS,
                "cost_bps_per_side": COST_BPS_PER_SIDE,
                "verdict": verdict_headline,
            }
        ]
    )

    trades_df.to_csv(ART_DIR / "trades.csv", index=False)
    nav_df.to_csv(ART_DIR / "nav.csv", index=False)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    variant_aggregate.to_csv(ART_DIR / "variant_aggregate.csv", index=False)
    trial_meta.to_csv(ART_DIR / "trial_meta.csv", index=False)
    pd.DataFrame(cache_meta).to_csv(ART_DIR / "cache_meta.csv", index=False)
    write_report(variant_aggregate, asset_summary.sort_values(["variant", "asset"]).reset_index(drop=True), trial_meta)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
