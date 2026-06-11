#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.signals.trendline_breakout_navigator import (  # noqa: E402
    TrendlineBreakoutNavigatorConfig,
    compute_trendline_breakout_navigator,
)

ART_DIR = ROOT / "reports" / "artifacts" / "rank29_orderbook_shadow"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "rank29_orderbook_shadow"
STATE_PATH = ART_DIR / "shadow_state.json"
STATUS_PATH = ART_DIR / "shadow_status.csv"
OPEN_POSITIONS_PATH = ART_DIR / "shadow_open_positions.csv"
CLOSED_TRADES_PATH = ART_DIR / "shadow_closed_trades.csv"
RECENT_SIGNALS_PATH = ART_DIR / "shadow_recent_signals.csv"
REJECTS_PATH = ART_DIR / "shadow_recent_rejections.csv"
RUN_SUMMARY_PATH = ART_DIR / "shadow_last_run_summary.json"
REPORT_PATH = SITE_DIR / "report.html"
CONFIG_PATH = ROOT / "config" / "execution" / "rank29_shadow.json"
MAIN_REPORT_PATH = ROOT / "reports" / "site" / "factors" / "scout_rank29_trendline_breakout_navigator_15m" / "report.html"
BASE_SCRIPT_PATH = ROOT / "scripts" / "build_rank29_trendline_breakout_clean_replication.py"

FUTURES_KLINES = "https://fapi.binance.com/fapi/v1/klines"
FUTURES_DEPTH = "https://fapi.binance.com/fapi/v1/depth"

STATUS_FIELDS = [
    "strategy_id",
    "venue",
    "updated_at_utc",
    "configured_symbols",
    "active_positions",
    "pending_entries",
    "closed_trades",
    "recent_signal_count",
    "recent_rejection_count",
    "lifetime_total_return",
    "last_signal_ts_utc",
    "last_entry_ts_utc",
    "last_exit_ts_utc",
    "note"
]


def load_base_module():
    spec = importlib.util.spec_from_file_location("rank29_base_shadow", BASE_SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["rank29_base_shadow"] = mod
    spec.loader.exec_module(mod)
    return mod


base_mod = load_base_module()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_z(dt: datetime | pd.Timestamp | str | None) -> str | None:
    if dt is None:
        return None
    ts = pd.to_datetime(dt, utc=True, errors="coerce")
    if pd.isna(ts):
        return None
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def fetch_json(url: str, params: dict[str, Any]) -> Any:
    query = urllib.parse.urlencode(params)
    full = f"{url}?{query}"
    headers = {"User-Agent": "OpenClaw-Rank29-Shadow/1.0", "Accept": "application/json,text/plain,*/*"}
    last_err: Exception | None = None
    for attempt in range(5):
        try:
            req = urllib.request.Request(full, headers=headers)
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            last_err = exc
            time.sleep(1.5 + attempt)
    raise RuntimeError(f"fetch failed for {full}: {last_err}")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path)


def append_csv(path: Path, df: pd.DataFrame) -> None:
    if df.empty:
        return
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[col]):
            out[col] = out[col].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    if path.exists() and path.stat().st_size > 0:
        prior = pd.read_csv(path)
        out = pd.concat([prior, out], ignore_index=True)
    out.to_csv(path, index=False)


def load_config(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return {"initialized_at_utc": iso_z(utc_now()), "symbols": {}}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def reset_outputs() -> None:
    for path in [STATE_PATH, STATUS_PATH, OPEN_POSITIONS_PATH, CLOSED_TRADES_PATH, RECENT_SIGNALS_PATH, REJECTS_PATH, RUN_SUMMARY_PATH]:
        if path.exists():
            path.unlink()


def save_state(state: dict[str, Any]) -> None:
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fetch_futures_klines(symbol: str, limit: int) -> pd.DataFrame:
    data = fetch_json(FUTURES_KLINES, {"symbol": symbol, "interval": "15m", "limit": int(limit)})
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(
        data,
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
    now_ms = time.time() * 1000.0
    df = df[pd.to_numeric(df["close_time"], errors="coerce") < now_ms].copy()
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
    return out.dropna().sort_values("timestamp").reset_index(drop=True)


def fetch_depth(symbol: str, limit: int) -> dict[str, Any]:
    return fetch_json(FUTURES_DEPTH, {"symbol": symbol, "limit": int(limit)})


def build_signal_frame(symbol: str, lookback_bars: int) -> pd.DataFrame:
    bars = fetch_futures_klines(symbol, limit=lookback_bars)
    nav = compute_trendline_breakout_navigator(
        bars[["timestamp", "high", "low", "close"]].copy(),
        config=TrendlineBreakoutNavigatorConfig(),
    )
    frame = pd.concat(
        [bars.reset_index(drop=True), nav.drop(columns=["timestamp", "high", "low", "close"], errors="ignore").reset_index(drop=True)],
        axis=1,
    )
    frame["symbol"] = symbol
    return frame


def choose_event(row: pd.Series, min_abs_composite: int) -> tuple[str, int] | None:
    return base_mod.choose_breakout_event(row, min_abs_composite=min_abs_composite)


def build_signal_id(symbol: str, event_ts: pd.Timestamp, direction: int) -> str:
    return f"{symbol}|{event_ts.strftime('%Y-%m-%dT%H:%M:%SZ')}|{'L' if direction > 0 else 'S'}"


def depth_snapshot_metrics(depth: dict[str, Any]) -> dict[str, Any]:
    bids = depth.get("bids") or []
    asks = depth.get("asks") or []
    best_bid = float(bids[0][0]) if bids else None
    best_ask = float(asks[0][0]) if asks else None
    spread_bps = None
    mid = None
    if best_bid and best_ask:
        mid = (best_bid + best_ask) / 2.0
        spread_bps = ((best_ask - best_bid) / mid) * 10000.0 if mid else None
    return {
        "best_bid": best_bid,
        "best_ask": best_ask,
        "mid": mid,
        "spread_bps": spread_bps,
        "depth_levels": int(min(len(bids), len(asks))),
    }


def simulate_fill_by_qty(depth: dict[str, Any], side: str, qty: float) -> dict[str, Any]:
    bids = depth.get("bids") or []
    asks = depth.get("asks") or []
    if qty <= 0:
        raise ValueError("qty must be positive")
    if side not in {"buy", "sell"}:
        raise ValueError("side must be buy/sell")
    levels = asks if side == "buy" else bids
    metrics = depth_snapshot_metrics(depth)
    remaining = float(qty)
    filled = 0.0
    quote = 0.0
    levels_used = 0
    level_rows = []
    for px_raw, qty_raw in levels:
        px = float(px_raw)
        lvl_qty = float(qty_raw)
        take = min(remaining, lvl_qty)
        if take <= 0:
            continue
        filled += take
        quote += take * px
        remaining -= take
        levels_used += 1
        level_rows.append([px, take])
        if remaining <= 1e-12:
            break
    if remaining > 1e-9 or filled <= 0:
        raise RuntimeError(f"insufficient depth to fill qty={qty:.8f}")
    vwap = quote / filled
    mid = metrics.get("mid")
    impact_bps = abs(vwap - mid) / mid * 10000.0 if mid else None
    return {
        **metrics,
        "side": side,
        "target_qty": qty,
        "filled_qty": filled,
        "quote_value": quote,
        "vwap": vwap,
        "impact_bps": impact_bps,
        "levels_used": levels_used,
        "levels_preview": json.dumps(level_rows[:5]),
    }


def pct(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def usd(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"${float(v):,.{digits}f}"


def num(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}"


def render_table(df: pd.DataFrame, percent_cols: set[str] | None = None, usd_cols: set[str] | None = None, digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    percent_cols = percent_cols or set()
    usd_cols = usd_cols or set()
    digits_cols = digits_cols or {}
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = []
        for col in df.columns:
            v = row[col]
            if col in percent_cols:
                text = pct(v, digits_cols.get(col, 2))
            elif col in usd_cols:
                text = usd(v, digits_cols.get(col, 2))
            elif isinstance(v, (float, np.floating, int, np.integer)) and not isinstance(v, bool):
                text = num(v, digits_cols.get(col, 2))
            else:
                text = str(v)
            cells.append(f"<td>{escape(text)}</td>")
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def classify_readiness(signals: int, rejections: int, closed: int, total_return: float | None, avg_entry_impact: float | None, avg_exit_impact: float | None) -> tuple[str, str]:
    reject_rate = (rejections / signals) if signals > 0 else None
    if signals < 3 and closed == 0:
        return "WARMUP", "样本还太少，先收集信号。"
    if closed >= 8 and (total_return or 0.0) > 0 and (reject_rate is None or reject_rate <= 0.35) and (avg_entry_impact is None or avg_entry_impact <= 4.0) and (avg_exit_impact is None or avg_exit_impact <= 5.0):
        return "READY_SOON", "样本、收益和盘口冲击都接近 tiny-live 准入线。"
    if closed >= 4 and (total_return or 0.0) > -0.01 and (reject_rate is None or reject_rate <= 0.50):
        return "WATCH", "还值得继续 shadow，但先别急着上真钱。"
    return "RED", "要么样本不够，要么拒单/冲击/收益不理想，继续观察。"


def build_monitor_tables(cfg: dict[str, Any], open_df: pd.DataFrame, closed_df: pd.DataFrame, signal_df: pd.DataFrame, reject_df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    rows = []
    counts = {"ready": 0, "watch": 0, "warmup": 0, "red": 0}
    for symbol in cfg.get("symbols", []):
        sig = signal_df[signal_df["symbol"] == symbol].copy() if not signal_df.empty else pd.DataFrame()
        rej = reject_df[reject_df["symbol"] == symbol].copy() if not reject_df.empty else pd.DataFrame()
        clo = closed_df[closed_df["symbol"] == symbol].copy() if not closed_df.empty else pd.DataFrame()
        opn = open_df[open_df["symbol"] == symbol].copy() if not open_df.empty else pd.DataFrame()
        signal_count = int(len(sig))
        reject_count = int(len(rej))
        closed_count = int(len(clo))
        open_count = int(len(opn))
        normal_entries = int((clo.get("entry_mode", pd.Series(dtype=str)) == "normal").sum()) if closed_count else 0
        late_entries = int((clo.get("entry_mode", pd.Series(dtype=str)) == "late_fallback").sum()) if closed_count else 0
        reject_rate = (reject_count / signal_count) if signal_count > 0 else np.nan
        win_rate = float((clo["net_ret"] > 0).mean()) if closed_count else np.nan
        total_return = float((1.0 + clo["net_ret"]).prod() - 1.0) if closed_count else np.nan
        avg_net_ret_bps = float(clo["net_ret_bps"].mean()) if closed_count else np.nan
        avg_entry_impact = float(clo["entry_impact_bps"].mean()) if closed_count else np.nan
        avg_exit_impact = float(clo["exit_impact_bps"].mean()) if closed_count else np.nan
        avg_entry_spread = float(clo["entry_spread_bps"].mean()) if closed_count else np.nan
        avg_exit_spread = float(clo["exit_spread_bps"].mean()) if closed_count else np.nan
        avg_hold_notional = float(clo["target_notional_usdt"].mean()) if closed_count else float(cfg.get("notional_usdt_by_symbol", {}).get(symbol, np.nan))
        readiness, note = classify_readiness(signal_count, reject_count, closed_count, total_return if not pd.isna(total_return) else None, avg_entry_impact if not pd.isna(avg_entry_impact) else None, avg_exit_impact if not pd.isna(avg_exit_impact) else None)
        if readiness == "READY_SOON":
            counts["ready"] += 1
        elif readiness == "WATCH":
            counts["watch"] += 1
        elif readiness == "WARMUP":
            counts["warmup"] += 1
        else:
            counts["red"] += 1
        rows.append(
            {
                "symbol": symbol,
                "live_ready": readiness,
                "signals": signal_count,
                "rejections": reject_count,
                "reject_rate": reject_rate,
                "open_positions": open_count,
                "closed_trades": closed_count,
                "win_rate": win_rate,
                "total_return": total_return,
                "avg_net_ret_bps": avg_net_ret_bps,
                "avg_entry_spread_bps": avg_entry_spread,
                "avg_entry_impact_bps": avg_entry_impact,
                "avg_exit_spread_bps": avg_exit_spread,
                "avg_exit_impact_bps": avg_exit_impact,
                "avg_notional_usdt": avg_hold_notional,
                "normal_entries": normal_entries,
                "late_entries": late_entries,
                "note": note,
            }
        )
    return pd.DataFrame(rows), counts


def write_report(cfg: dict[str, Any], status_row: dict[str, Any]) -> None:
    ensure_dir(SITE_DIR)
    open_df = read_csv(OPEN_POSITIONS_PATH)
    closed_df = read_csv(CLOSED_TRADES_PATH)
    signal_df = read_csv(RECENT_SIGNALS_PATH)
    reject_df = read_csv(REJECTS_PATH)
    recent_closed = closed_df.tail(25).copy() if not closed_df.empty else pd.DataFrame()
    recent_reject = reject_df.tail(25).copy() if not reject_df.empty else pd.DataFrame()
    monitor_df, monitor_counts = build_monitor_tables(cfg, open_df, closed_df, signal_df, reject_df)
    reasons = cfg.get("symbol_reasons", {})
    exclusions = cfg.get("excluded_symbols", {})
    symbol_table = pd.DataFrame(
        [
            {"symbol": s, "notional_usdt": cfg.get("notional_usdt_by_symbol", {}).get(s), "reason": reasons.get(s, "")}
            for s in cfg.get("symbols", [])
        ]
    )
    exclusion_table = pd.DataFrame(
        [{"symbol": s, "reason": r} for s, r in exclusions.items()]
    )
    html = f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank29 Shadow Execution Plan</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1180px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background: #f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .muted {{ color:#6b7280; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    a {{ color:#2563eb; text-decoration:none; }}
  </style>
</head>
<body>
  <p><a href='../scout_rank29_trendline_breakout_navigator_15m/report.html'>← 返回 Rank29 主报告</a></p>
  <h1>Rank29 · Orderbook shadow execution</h1>
  <p class='muted'>更新时间：{escape(str(status_row.get('updated_at_utc') or '-'))}</p>

  <div class='card'>
    <h2>方案一句话</h2>
    <p>研究侧证明 Rank29 在 <b>10–15bps/side</b> 下仍有 edge；这条 shadow runner 则把它切换到 <b>Binance USDT-M perp</b> 的真实盘口环境，用 <b>L2 depth 逐档吃单</b> 模拟成交，回答“如果以后 tiny-live，上哪些币、按什么方式进出，会不会被订单簿打穿”。</p>
    <p><span class='pill'>venue = {escape(str(cfg.get('venue')))}</span><span class='pill'>hold = {escape(str(cfg.get('hold_bars')))} x 15m</span><span class='pill'>fee = {escape(str(cfg.get('taker_fee_bps_per_side')))} bps/side</span><span class='pill'>max concurrent = {escape(str(cfg.get('max_concurrent_positions')))}</span></p>
  </div>

  <div class='card'>
    <h2>它和 gate shadow 不是一回事</h2>
    <ul>
      <li><b>这页回答的是执行问题</b>：真实盘口的 <code>spread / impact / rejection</code> 会不会把策略打穿。</li>
      <li><b>它不是 manual narrow paper 里的 gate shadow</b>：后者是在 <code>Binance spot 15m</code> 的同一批 paper trades 上做 <code>low_trend_high_noise_w25</code> 降仓记账。</li>
      <li><b>这页会记录</b>：L2 depth、VWAP、spread_bps、impact_bps、拒单原因、perp fee。</li>
      <li><b>这页不会回答</b>：坏环境该不该降仓；那是 regime gate backtest / gate shadow 的职责。</li>
    </ul>
    <p class='muted'>如果你想看 Rank29 各条线的关系图，请回主报告页或读仓库文档 <code>docs/RANK29_SHADOWS.md</code>。</p>
  </div>

  <div class='card'>
    <h2>我为什么选这 7 个币</h2>
    <ul>
      <li>优先保留 <b>3y/5y 长样本里在 10–15bps 下仍然明显为正</b> 的币。</li>
      <li>同时要求盘口相对够深，适合 very-small live。于是保留：<code>{escape(', '.join(cfg.get('symbols', [])))}</code></li>
      <li>明确排除 <code>BTC/ETH/BNB</code> 这种“流动性虽好但 edge 太薄”的币，先不让它们拖累首轮 canary。</li>
    </ul>
    {render_table(symbol_table, usd_cols={'notional_usdt'}, digits_cols={'notional_usdt': 0})}
    <h3>当前排除 / waitlist</h3>
    {render_table(exclusion_table)}
  </div>

  <div class='card'>
    <h2>入场 / 离场规则</h2>
    <ul>
      <li><b>信号来源：</b> 对每个币抓 Binance UM perp 的已完成 15m bars，跑 <code>trendline_breakout_navigator</code>。</li>
      <li><b>开仓前置条件：</b> bar 被标为 <code>breakout_bull</code> 且 <code>composite_trend &gt;= +{cfg.get('signal_min_abs_composite')}</code>，或 <code>breakout_bear</code> 且 <code>composite_trend &lt;= -{cfg.get('signal_min_abs_composite')}</code>。</li>
      <li><b>入场时点：</b> 信号 bar 收完后，等 <code>{cfg.get('entry_delay_minutes')}</code> 分钟到下一根 15m 开盘附近；如果超过 <code>{cfg.get('entry_window_minutes')}</code> 分钟仍没执行，则放弃本次信号。</li>
      <li><b>成交模拟：</b> 用当时的 <code>{cfg.get('depth_limit')}</code> 档深度，按目标 base qty 逐档吃单，得到真实的 shadow VWAP、spread_bps 和 impact_bps。</li>
      <li><b>拒单条件：</b> 入场时如果 <code>spread_bps &gt; {cfg.get('entry_max_spread_bps')}</code> 或 <code>impact_bps &gt; {cfg.get('entry_max_impact_bps')}</code>，就拒绝这笔信号，不强行追。</li>
      <li><b>平仓原则：</b> 固定持有 <code>{cfg.get('hold_bars')}</code> 根 15m bar，到点后用相反方向的盘口深度逐档成交并计入实际退出滑点。</li>
      <li><b>no-overlap：</b> 每个币同一时间只允许 1 个仓位；全局最多同时 <code>{cfg.get('max_concurrent_positions')}</code> 个仓位。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>当前状态</h2>
    <ul>
      <li>closed trades: <b>{escape(str(status_row.get('closed_trades', 0)))}</b></li>
      <li>active positions: <b>{escape(str(status_row.get('active_positions', 0)))}</b></li>
      <li>pending entries: <b>{escape(str(status_row.get('pending_entries', 0)))}</b></li>
      <li>recent signals: <b>{escape(str(status_row.get('recent_signal_count', 0)))}</b></li>
      <li>recent rejections: <b>{escape(str(status_row.get('recent_rejection_count', 0)))}</b></li>
      <li>lifetime total return: <b>{escape(pct(status_row.get('lifetime_total_return')))}</b></li>
      <li>ready soon / watch / warmup / red: <b>{monitor_counts['ready']}</b> / <b>{monitor_counts['watch']}</b> / <b>{monitor_counts['warmup']}</b> / <b>{monitor_counts['red']}</b></li>
    </ul>
  </div>

  <div class='card'>
    <h2>shadow monitor 看板</h2>
    <p class='muted'>这张表是后续你持续跟进的主入口：看每个币的信号数、拒单率、平均盘口冲击、累计 shadow 收益，以及它离 tiny-live 还差多远。</p>
    {render_table(monitor_df[['symbol','live_ready','signals','rejections','reject_rate','open_positions','closed_trades','normal_entries','late_entries','win_rate','total_return','avg_net_ret_bps','avg_entry_spread_bps','avg_entry_impact_bps','avg_exit_spread_bps','avg_exit_impact_bps','avg_notional_usdt','note']] if not monitor_df.empty else monitor_df, percent_cols={'reject_rate','win_rate','total_return'}, usd_cols={'avg_notional_usdt'}, digits_cols={'signals':0,'rejections':0,'open_positions':0,'closed_trades':0,'normal_entries':0,'late_entries':0,'avg_net_ret_bps':1,'avg_entry_spread_bps':2,'avg_entry_impact_bps':2,'avg_exit_spread_bps':2,'avg_exit_impact_bps':2,'avg_notional_usdt':0})}
    <ul>
      <li><b>READY_SOON</b>：closed trades ≥ 8、总收益为正、拒单率不高、平均 entry/exit 冲击也没超线，已经接近 tiny-live 准入。</li>
      <li><b>WATCH</b>：值得继续 shadow，但样本或盘口质量还不够让人放心。</li>
      <li><b>WARMUP</b>：刚启动，信号/成交样本还太少。</li>
      <li><b>RED</b>：收益、拒单或盘口冲击明显不理想，先别推真钱。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>当前持仓</h2>
    {render_table(open_df[['symbol','side','entry_signal_ts_utc','planned_entry_ts_utc','planned_exit_ts_utc','entry_fill_price','entry_spread_bps','entry_impact_bps','target_notional_usdt']] if not open_df.empty else open_df, percent_cols=set(), usd_cols={'target_notional_usdt'}, digits_cols={'entry_fill_price': 6, 'entry_spread_bps': 2, 'entry_impact_bps': 2})}
  </div>

  <div class='card'>
    <h2>最近新信号</h2>
    {render_table(signal_df.tail(25)[['symbol','signal_ts_utc','planned_entry_ts_utc','planned_exit_ts_utc','side','trigger_tf','composite_trend','signal_close']] if not signal_df.empty else signal_df, digits_cols={'composite_trend':0,'signal_close':6})}
  </div>

  <div class='card'>
    <h2>最近 closed trades</h2>
    {render_table(recent_closed[['symbol','side','entry_mode','entry_age_minutes','entry_signal_ts_utc','entry_exec_ts_utc','exit_exec_ts_utc','gross_ret','net_ret','entry_impact_bps','exit_impact_bps','net_ret_bps']] if not recent_closed.empty else recent_closed, percent_cols={'gross_ret','net_ret'}, digits_cols={'entry_age_minutes':1,'entry_impact_bps': 2, 'exit_impact_bps': 2, 'net_ret_bps': 1})}
  </div>

  <div class='card'>
    <h2>最近拒绝的信号</h2>
    {render_table(recent_reject[['symbol','signal_ts_utc','side','reason','entry_age_minutes','spread_bps','impact_bps']] if not recent_reject.empty else recent_reject, digits_cols={'entry_age_minutes':1,'spread_bps': 2, 'impact_bps': 2})}
  </div>
</body>
</html>
"""
    REPORT_PATH.write_text(html, encoding="utf-8")


def build_signal_rows(frame: pd.DataFrame, symbol: str, min_abs_composite: int, hold_bars: int, entry_delay_minutes: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for _, row in frame.iterrows():
        chosen = choose_event(row, min_abs_composite)
        if chosen is None:
            continue
        prefix, direction = chosen
        signal_ts = pd.to_datetime(row["timestamp"], utc=True)
        rows.append(
            {
                "signal_id": build_signal_id(symbol, signal_ts, direction),
                "symbol": symbol,
                "signal_ts_utc": iso_z(signal_ts),
                "planned_entry_ts_utc": iso_z(signal_ts + pd.Timedelta(minutes=entry_delay_minutes)),
                "planned_exit_ts_utc": iso_z(signal_ts + pd.Timedelta(minutes=15 * (1 + hold_bars))),
                "side": "long" if direction > 0 else "short",
                "direction": int(direction),
                "trigger_tf": prefix.replace("tbn_", ""),
                "composite_trend": int(row["tbn_composite_trend"]),
                "signal_close": float(row["close"]),
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank29 orderbook shadow runner")
    parser.add_argument("--config", default=str(CONFIG_PATH))
    parser.add_argument("--init-from-now", action="store_true", help="Bootstrap from the latest completed bar and ignore older signals.")
    args = parser.parse_args()

    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    if args.init_from_now:
        reset_outputs()
    cfg = load_config(Path(args.config))
    state = load_state()
    symbols_state = state.setdefault("symbols", {})

    now = utc_now()
    new_signal_rows: list[dict[str, Any]] = []
    reject_rows: list[dict[str, Any]] = []
    closed_rows: list[dict[str, Any]] = []
    open_rows: list[dict[str, Any]] = []

    active_count = 0
    for symbol in cfg.get("symbols", []):
        sym_state = symbols_state.setdefault(symbol, {"last_seen_signal_ts_utc": None, "pending_entry": None, "position": None})
        frame = build_signal_frame(symbol, int(cfg.get("lookback_bars", 500)))
        signal_rows = build_signal_rows(
            frame,
            symbol,
            int(cfg.get("signal_min_abs_composite", 2)),
            int(cfg.get("hold_bars", 8)),
            int(cfg.get("entry_delay_minutes", 0)),
        )
        last_seen_raw = sym_state.get("last_seen_signal_ts_utc")
        last_seen = pd.to_datetime(last_seen_raw, utc=True, errors="coerce")
        if pd.isna(last_seen):
            latest_bar_ts = pd.to_datetime(frame["timestamp"].max(), utc=True)
            sym_state["last_seen_signal_ts_utc"] = iso_z(latest_bar_ts)
            continue
        for sig in signal_rows:
            sig_ts = pd.to_datetime(sig["signal_ts_utc"], utc=True)
            if sig_ts <= last_seen:
                continue
            last_seen = sig_ts
            if sym_state.get("position") is not None or sym_state.get("pending_entry") is not None:
                reject_rows.append({**sig, "reason": "skip_due_to_no_overlap_or_pending", "spread_bps": np.nan, "impact_bps": np.nan})
                continue
            sym_state["pending_entry"] = sig
            new_signal_rows.append(sig)
        sym_state["last_seen_signal_ts_utc"] = iso_z(last_seen)

    for symbol in cfg.get("symbols", []):
        sym_state = symbols_state[symbol]
        pending = sym_state.get("pending_entry")
        position = sym_state.get("position")
        if pending is not None and position is None:
            planned_entry = pd.to_datetime(pending["planned_entry_ts_utc"], utc=True)
            deadline = planned_entry + pd.Timedelta(minutes=int(cfg.get("entry_window_minutes", 5)))
            if now >= planned_entry.to_pydatetime():
                age_minutes = max(0.0, (now - planned_entry.to_pydatetime()).total_seconds() / 60.0)
                normal_window = float(cfg.get("entry_normal_window_minutes", 3))
                late_window = float(cfg.get("entry_late_window_minutes", 10))
                late_allowed = bool(cfg.get("allow_late_entry_fallback", True))
                if age_minutes > late_window or (age_minutes > normal_window and not late_allowed):
                    reject_rows.append({**pending, "reason": "entry_window_expired", "spread_bps": np.nan, "impact_bps": np.nan, "entry_age_minutes": age_minutes})
                    sym_state["pending_entry"] = None
                else:
                    if active_count >= int(cfg.get("max_concurrent_positions", 3)):
                        reject_rows.append({**pending, "reason": "max_concurrent_positions_reached", "spread_bps": np.nan, "impact_bps": np.nan, "entry_age_minutes": age_minutes})
                        sym_state["pending_entry"] = None
                    else:
                        depth = fetch_depth(symbol, int(cfg.get("depth_limit", 20)))
                        metrics = depth_snapshot_metrics(depth)
                        mid = metrics.get("mid")
                        target_notional = float(cfg.get("notional_usdt_by_symbol", {}).get(symbol, 75.0))
                        target_qty = target_notional / mid if mid else None
                        try:
                            fill = simulate_fill_by_qty(depth, "buy" if pending["direction"] > 0 else "sell", float(target_qty))
                            if (fill.get("spread_bps") or 0.0) > float(cfg.get("entry_max_spread_bps", 8.0)):
                                raise RuntimeError("entry_spread_too_wide")
                            if (fill.get("impact_bps") or 0.0) > float(cfg.get("entry_max_impact_bps", 6.0)):
                                raise RuntimeError("entry_impact_too_high")
                            position = {
                                **pending,
                                "entry_exec_ts_utc": iso_z(now),
                                "entry_fill_price": float(fill["vwap"]),
                                "entry_mid_price": float(fill["mid"]),
                                "entry_spread_bps": float(fill.get("spread_bps") or np.nan),
                                "entry_impact_bps": float(fill.get("impact_bps") or np.nan),
                                "entry_levels_used": int(fill["levels_used"]),
                                "entry_levels_preview": fill["levels_preview"],
                                "filled_qty": float(fill["filled_qty"]),
                                "quote_value": float(fill["quote_value"]),
                                "target_notional_usdt": target_notional,
                                "entry_age_minutes": age_minutes,
                                "entry_mode": "normal" if age_minutes <= normal_window else "late_fallback",
                            }
                            sym_state["position"] = position
                            sym_state["pending_entry"] = None
                            active_count += 1
                        except Exception as exc:  # noqa: BLE001
                            reject_rows.append({**pending, "reason": str(exc), "spread_bps": metrics.get("spread_bps"), "impact_bps": np.nan, "entry_age_minutes": age_minutes})
                            sym_state["pending_entry"] = None
        if sym_state.get("position") is not None:
            active_count += 1

    for symbol in cfg.get("symbols", []):
        sym_state = symbols_state[symbol]
        position = sym_state.get("position")
        if position is None:
            continue
        planned_exit = pd.to_datetime(position["planned_exit_ts_utc"], utc=True)
        if now < planned_exit.to_pydatetime():
            open_rows.append(position)
            continue
        depth = fetch_depth(symbol, int(cfg.get("depth_limit", 20)))
        exit_side = "sell" if position["direction"] > 0 else "buy"
        fill = simulate_fill_by_qty(depth, exit_side, float(position["filled_qty"]))
        entry_px = float(position["entry_fill_price"])
        exit_px = float(fill["vwap"])
        direction = int(position["direction"])
        gross_ret = (exit_px / entry_px - 1.0) if direction > 0 else (entry_px / exit_px - 1.0)
        fee_rate = float(cfg.get("taker_fee_bps_per_side", 5.0)) / 10000.0
        net_ret = (1.0 + gross_ret) * (1.0 - fee_rate) * (1.0 - fee_rate) - 1.0
        closed_rows.append(
            {
                **position,
                "exit_exec_ts_utc": iso_z(now),
                "exit_fill_price": exit_px,
                "exit_mid_price": float(fill["mid"]),
                "exit_spread_bps": float(fill.get("spread_bps") or np.nan),
                "exit_impact_bps": float(fill.get("impact_bps") or np.nan),
                "exit_levels_used": int(fill["levels_used"]),
                "exit_levels_preview": fill["levels_preview"],
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "net_ret_bps": net_ret * 10000.0,
            }
        )
        sym_state["position"] = None

    if new_signal_rows:
        append_csv(RECENT_SIGNALS_PATH, pd.DataFrame(new_signal_rows))
    if reject_rows:
        append_csv(REJECTS_PATH, pd.DataFrame(reject_rows))
    if closed_rows:
        append_csv(CLOSED_TRADES_PATH, pd.DataFrame(closed_rows))

    open_state_rows = []
    for symbol in cfg.get("symbols", []):
        pos = symbols_state[symbol].get("position")
        if pos is not None:
            open_state_rows.append(pos)
    open_df = pd.DataFrame(open_state_rows)
    if not open_df.empty:
        open_df.to_csv(OPEN_POSITIONS_PATH, index=False)
    else:
        pd.DataFrame(columns=["symbol","side","entry_signal_ts_utc","planned_entry_ts_utc","planned_exit_ts_utc","entry_fill_price","entry_spread_bps","entry_impact_bps","target_notional_usdt"]).to_csv(OPEN_POSITIONS_PATH, index=False)

    closed_df = read_csv(CLOSED_TRADES_PATH)
    lifetime_total_return = float((1.0 + closed_df["net_ret"]).prod() - 1.0) if not closed_df.empty else 0.0
    status_row = {
        "strategy_id": cfg.get("strategy_id"),
        "venue": cfg.get("venue"),
        "updated_at_utc": iso_z(now),
        "configured_symbols": len(cfg.get("symbols", [])),
        "active_positions": len(open_state_rows),
        "pending_entries": int(sum(1 for s in symbols_state.values() if s.get("pending_entry") is not None)),
        "closed_trades": int(len(closed_df)),
        "recent_signal_count": int(len(read_csv(RECENT_SIGNALS_PATH))),
        "recent_rejection_count": int(len(read_csv(REJECTS_PATH))),
        "lifetime_total_return": lifetime_total_return,
        "last_signal_ts_utc": max([row["signal_ts_utc"] for row in new_signal_rows], default=None),
        "last_entry_ts_utc": max([pos.get("entry_exec_ts_utc") for pos in open_state_rows if pos.get("entry_exec_ts_utc")], default=None),
        "last_exit_ts_utc": closed_df.iloc[-1]["exit_exec_ts_utc"] if not closed_df.empty else None,
        "note": "Binance UM perp shadow runner using L2 depth snapshots for entry/exit VWAP estimation.",
    }
    pd.DataFrame([status_row], columns=STATUS_FIELDS).to_csv(STATUS_PATH, index=False)
    save_state(state)
    write_report(cfg, status_row)

    summary = {
        "run_at_utc": iso_z(now),
        "new_signals": len(new_signal_rows),
        "new_rejections": len(reject_rows),
        "new_closed_trades": len(closed_rows),
        "active_positions": len(open_state_rows),
        "report_path": str(REPORT_PATH.relative_to(ROOT)),
        "status_path": str(STATUS_PATH.relative_to(ROOT)),
    }
    RUN_SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
