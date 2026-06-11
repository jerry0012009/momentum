#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import importlib.util
import json
import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "ema_psar_raw_alpha"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "ema_psar_raw_alpha"
SITE_PATH = SITE_DIR / "report.html"
EMA_REFRESH_HISTORY_PATH = ART_DIR / "ema_paper_trading_refresh_history.csv"
EMA_REFRESH_HISTORY_AUDIT_PATH = ART_DIR / "ema_paper_trading_refresh_history_audit.csv"

REPL_ART_DIR = ROOT / "reports" / "artifacts" / "regime_switch_indicator_stack_replication"
CROSS_PATH = REPL_ART_DIR / "cross_market_results.csv"
PAPER_PATH = REPL_ART_DIR / "paper_window_btc_2018_2022_metrics.csv"
REPL_SCRIPT_PATH = ROOT / "scripts" / "build_regime_switch_indicator_stack_replication_report.py"
COST_ART_DIR = ROOT / "reports" / "artifacts" / "ema_psar_cost_budget_v1"
COST_SUMMARY_PATH = COST_ART_DIR / "ema_psar_cost_budget_summary.csv"
COST_STRATEGY_SUMMARY_PATH = COST_ART_DIR / "ema_psar_cost_budget_strategy_summary.csv"
COST_BY_COMBO_PATH = COST_ART_DIR / "ema_psar_cost_budget_by_combo.csv"

BASE_ORDER = ["EMA", "PSAR", "BB", "RSI"]
FREQ_ORDER = ["日频(1d)", "周频(1wk)", "小时频(60m)"]
CLASS_ORDER = ["Crypto", "美股", "A股"]
FREQ_LABEL_MAP = {"1d": "日频(1d)", "1wk": "周频(1wk)", "60m": "小时频(60m)"}
CRYPTO_ROLLING_CACHE_DIR = ROOT / "reports" / "artifacts" / "pytrendline_event_validation_v3_crypto_180d" / "cache"
EMA60M_ROLLING_WINDOW_DAYS = 45
EMA60M_ROLLING_STEP_DAYS = 15
EMA60M_ROLLING_COST_BPS = 20
EMA60M_ROLLING_CACHE_FILES = {
    "BTC": CRYPTO_ROLLING_CACHE_DIR / "BTC_USD__180d__60m.csv",
    "ETH": CRYPTO_ROLLING_CACHE_DIR / "ETH_USD__180d__60m.csv",
    "SOL": CRYPTO_ROLLING_CACHE_DIR / "SOL_USD__180d__60m.csv",
}
ASHARE_FRONTIER_CACHE_DIR = ART_DIR / "ashare_frontier_cache"
EMA_REFRESH_BOOTSTRAP_CACHE_DIR = ART_DIR / "refresh_bootstrap_cache"
EMA_DAILY_REFRESH_SCOPE_CONFIG = {
    ("创业板ETF 1d", "A股-1d"): {
        "members": [
            {"asset": "创业板ETF", "ticker": "159915.SZ", "source": "eastmoney_cn_daily", "interval": "1d"},
        ],
        "row_kind": "primary",
    },
    ("美股 1d+1wk（SPY/QQQ/AAPL）", "美股-1d"): {
        "members": [
            {"asset": "SPY", "ticker": "SPY", "source": "stooq", "interval": "1d"},
            {"asset": "QQQ", "ticker": "QQQ", "source": "stooq", "interval": "1d"},
            {"asset": "AAPL", "ticker": "AAPL", "source": "stooq", "interval": "1d"},
        ],
        "row_kind": "secondary_front_queue",
    },
    ("Crypto 1d+1wk（BTC/ETH/SOL）", "Crypto-1d"): {
        "members": [
            {"asset": "BTC", "ticker": "BTCUSDT", "source": "binance_spot", "interval": "1d"},
            {"asset": "ETH", "ticker": "ETHUSDT", "source": "binance_spot", "interval": "1d"},
            {"asset": "SOL", "ticker": "SOLUSDT", "source": "binance_spot", "interval": "1d"},
        ],
        "row_kind": "secondary_backstop",
    },
    ("贵州茅台 1d+1wk", "A股-1d"): {
        "members": [
            {"asset": "贵州茅台", "ticker": "600519.cn", "source": "stooq_direct", "interval": "1d"},
        ],
        "row_kind": "secondary_mid_queue",
    },
    ("沪深300ETF 1d", "A股-1d"): {
        "members": [
            {"asset": "沪深300ETF", "ticker": "510300.SS", "source": "eastmoney_cn_daily", "interval": "1d"},
        ],
        "row_kind": "shadow",
    },
}
EMA_FIRST_REFRESH_TOP_SCOPE_KEYS = {
    ("创业板ETF 1d", "A股-1d"),
    ("美股 1d+1wk（SPY/QQQ/AAPL）", "美股-1d"),
    ("沪深300ETF 1d", "A股-1d"),
}
EMA_NON60M_ASHARE_FRONTIER_CONFIG = [
    {"asset": "沪深300ETF", "ticker": "510300.SS", "interval": "1d", "asset_class": "A股"},
    {"asset": "沪深300ETF", "ticker": "510300.SS", "interval": "1wk", "asset_class": "A股"},
    {"asset": "创业板ETF", "ticker": "159915.SZ", "interval": "1d", "asset_class": "A股"},
    {"asset": "创业板ETF", "ticker": "159915.SZ", "interval": "1wk", "asset_class": "A股"},
]
EMA_NON60M_ASHARE_WINDOW_DAYS = 730
EMA_NON60M_ASHARE_STEP_DAYS = 180
EMA_NON60M_ASHARE_COST_BPS = 20
EMA_NON60M_ASHARE_MIN_BARS = {"1d": 200, "1wk": 60}
EMA_NON60M_ASHARE_WEEKLY_HOLDOUT_TRAIN_DAYS = 730
EMA_NON60M_ASHARE_WEEKLY_HOLDOUT_DAYS = 365
EMA_NON60M_ASHARE_WEEKLY_HOLDOUT_STEP_DAYS = 365
EMA_NON60M_ASHARE_DAILY_HOLDOUT_TRAIN_DAYS = 730
EMA_NON60M_ASHARE_DAILY_HOLDOUT_DAYS = 365
EMA_NON60M_ASHARE_DAILY_HOLDOUT_STEP_DAYS = 365


def ensure_dirs() -> None:
    ART_DIR.mkdir(parents=True, exist_ok=True)
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    ASHARE_FRONTIER_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    EMA_REFRESH_BOOTSTRAP_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def fmt_pct(v: float | int | None) -> str:
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "-"
    return f"{float(v):.2f}%"


def fmt_num(v: float | int | None, d: int = 2) -> str:
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "-"
    return f"{float(v):.{d}f}"


def fmt_bps(v: float | int | None, d: int = 1) -> str:
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "-"
    return f"{float(v):.{d}f}bps"


def load_optional_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def normalize_refresh_bars(raw: pd.DataFrame) -> pd.DataFrame:
    bars = raw.rename(
        columns={
            "Date": "timestamp",
            "Datetime": "timestamp",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }
    ).copy()
    if "volume" not in bars.columns:
        bars["volume"] = 0.0
    need = ["timestamp", "open", "high", "low", "close", "volume"]
    missing = [c for c in need if c not in bars.columns]
    if missing:
        raise ValueError(f"missing refresh columns: {missing}")
    bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True)
    bars = bars[need].dropna(subset=["open", "high", "low", "close"])
    bars = bars[(bars["open"] > 0) & (bars["high"] > 0) & (bars["low"] > 0) & (bars["close"] > 0)]
    bars["volume"] = pd.to_numeric(bars["volume"], errors="coerce").fillna(0.0)
    bars = bars.sort_values("timestamp").reset_index(drop=True)
    if len(bars) < 120:
        raise ValueError(f"too few refresh bars ({len(bars)})")
    return bars


def load_stooq_daily_bars(symbol: str, *, suffix: str = ".us", cache_key: str | None = None) -> tuple[pd.DataFrame, str]:
    symbol_query = f"{symbol.lower()}{suffix}" if suffix else symbol.lower()
    cache_label = cache_key or symbol_query.replace('.', '_')
    cache_path = EMA_REFRESH_BOOTSTRAP_CACHE_DIR / f"stooq_{cache_label}_1d.csv"
    url = f"https://stooq.com/q/d/l/?s={symbol_query}&i=d"
    try:
        raw = pd.read_csv(url)
        if raw.empty or "No data" in raw.columns:
            raise ValueError(f"no stooq data: {symbol_query}")
        bars = normalize_refresh_bars(raw)
        bars.to_csv(cache_path, index=False)
        return bars, "stooq_live"
    except Exception:
        if cache_path.exists():
            bars = pd.read_csv(cache_path, parse_dates=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
            return bars, "stooq_cache_fallback"
        raise


def eastmoney_secid_from_ticker(ticker: str) -> str:
    clean = str(ticker or "").strip().upper()
    if not clean:
        raise ValueError("empty eastmoney ticker")
    if "." not in clean:
        raise ValueError(f"eastmoney ticker missing market suffix: {ticker}")
    code, market = clean.split(".", 1)
    market = market.upper()
    if market in {"SZ"}:
        market_id = "0"
    elif market in {"SS", "SH"}:
        market_id = "1"
    elif market in {"BJ"}:
        market_id = "0"
    else:
        raise ValueError(f"unsupported eastmoney market suffix: {ticker}")
    return f"{market_id}.{code}"


def load_eastmoney_daily_bars(ticker: str) -> tuple[pd.DataFrame, str]:
    secid = eastmoney_secid_from_ticker(ticker)
    cache_key = ticker.replace('-', '_').replace('.', '_').lower()
    cache_path = EMA_REFRESH_BOOTSTRAP_CACHE_DIR / f"eastmoney_{cache_key}_1d.csv"
    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get?" + urlencode(
        {
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58",
            "klt": "101",
            "fqt": "1",
            "secid": secid,
            "beg": "20100101",
            "end": "20500101",
        }
    )
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=20) as resp:
            payload = json.load(resp)
        klines = ((payload or {}).get("data") or {}).get("klines") or []
        if not klines:
            raise ValueError(f"no eastmoney data: {ticker}")
        rows = []
        for line in klines:
            parts = str(line).split(",")
            if len(parts) < 6:
                continue
            rows.append(
                {
                    "timestamp": parts[0],
                    "open": float(parts[1]),
                    "close": float(parts[2]),
                    "high": float(parts[3]),
                    "low": float(parts[4]),
                    "volume": float(parts[5]),
                }
            )
        bars = normalize_refresh_bars(pd.DataFrame(rows))
        bars.to_csv(cache_path, index=False)
        return bars, "eastmoney_live"
    except Exception:
        if cache_path.exists():
            bars = pd.read_csv(cache_path, parse_dates=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
            return bars, "eastmoney_cache_fallback"
        raise


def load_binance_daily_bars(symbol: str, *, limit: int = 1500) -> tuple[pd.DataFrame, str]:
    cache_path = EMA_REFRESH_BOOTSTRAP_CACHE_DIR / f"binance_{symbol.lower()}_1d.csv"
    url = "https://api.binance.com/api/v3/klines?" + urlencode({"symbol": symbol.upper(), "interval": "1d", "limit": limit})
    try:
        with urlopen(url, timeout=20) as resp:
            raw = json.load(resp)
        if not isinstance(raw, list) or not raw:
            raise ValueError(f"no binance data: {symbol}")
        bars = pd.DataFrame(
            {
                "timestamp": [pd.to_datetime(int(row[0]), unit="ms", utc=True) for row in raw],
                "open": [float(row[1]) for row in raw],
                "high": [float(row[2]) for row in raw],
                "low": [float(row[3]) for row in raw],
                "close": [float(row[4]) for row in raw],
                "volume": [float(row[5]) for row in raw],
            }
        )
        bars = normalize_refresh_bars(bars)
        now_utc = pd.Timestamp.now(tz="UTC")
        if not bars.empty and pd.Timestamp(bars.iloc[-1]["timestamp"]).date() >= now_utc.date():
            bars = bars.iloc[:-1].reset_index(drop=True)
        if len(bars) < 120:
            raise ValueError(f"too few binance refresh bars after drop-open-bar ({len(bars)})")
        bars.to_csv(cache_path, index=False)
        return bars, "binance_live"
    except Exception:
        if cache_path.exists():
            bars = pd.read_csv(cache_path, parse_dates=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
            return bars, "binance_cache_fallback"
        raise


def load_yfinance_refresh_bars(ticker: str, interval: str, *, period: str = "10y") -> tuple[pd.DataFrame, str]:
    cache_path = EMA_REFRESH_BOOTSTRAP_CACHE_DIR / f"yf_{ticker.replace('-', '_').replace('.', '_')}__{period}__{interval}.csv"
    frontier_cache_path = ASHARE_FRONTIER_CACHE_DIR / f"{ticker.replace('-', '_').replace('.', '_')}__10y__{interval}.csv"
    try:
        mod = load_replication_module()
        bars = mod.download_bars(ticker, period=period, interval=interval)
        bars = bars.sort_values("timestamp").reset_index(drop=True)
        bars.to_csv(cache_path, index=False)
        return bars, "yfinance_live"
    except Exception:
        if cache_path.exists():
            bars = pd.read_csv(cache_path, parse_dates=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
            return bars, "yfinance_cache_fallback"
        if frontier_cache_path.exists():
            bars = pd.read_csv(frontier_cache_path, parse_dates=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
            return bars, "frontier_cache_fallback"
        raise


def load_first_refresh_member_bars(member_cfg: dict[str, str]) -> tuple[pd.DataFrame, str]:
    source = str(member_cfg.get("source", "") or "")
    ticker = str(member_cfg.get("ticker", "") or "")
    interval = str(member_cfg.get("interval", "1d") or "1d")
    if source == "stooq":
        return load_stooq_daily_bars(ticker)
    if source == "stooq_direct":
        return load_stooq_daily_bars(ticker, suffix="", cache_key=ticker.lower().replace('.', '_'))
    if source == "binance_spot":
        return load_binance_daily_bars(ticker)
    if source == "eastmoney_cn_daily":
        return load_eastmoney_daily_bars(ticker)
    if source == "yfinance_live":
        return load_yfinance_refresh_bars(ticker, interval)
    raise ValueError(f"unsupported first refresh source: {source}")


def summarize_long_only_live_state(df: pd.DataFrame, strategy: str) -> dict[str, object]:
    feat = build_ema_only_feature_frame(df)
    if feat.empty:
        return {
            "signal": "HOLD",
            "in_position": False,
            "entry_ts": pd.NaT,
            "entry_price": np.nan,
            "latest_ts": pd.NaT,
            "latest_close": np.nan,
            "unrealized_pct": np.nan,
        }

    in_pos = False
    entry_ts = pd.NaT
    entry_price = np.nan
    signal = "HOLD"

    for _, row in feat.iterrows():
        px = float(row["close"])
        if strategy == "EMA":
            buy_sig = bool(row["ema9"] > row["ema20"])
            sell_sig = bool(row["ema9"] < row["ema20"])
            signal = "BUY" if buy_sig else ("SELL" if sell_sig else "HOLD")
        else:
            buy_sig = bool((not pd.isna(row["prev_high"])) and (not pd.isna(row["psar"])) and (row["psar"] <= row["close"]) and (row["high"] > row["prev_high"]))
            sell_sig = bool((not pd.isna(row["prev_low"])) and (not pd.isna(row["psar"])) and (row["psar"] > row["close"]) and (row["low"] < row["prev_low"]))
            signal = "BUY" if buy_sig else ("SELL" if sell_sig else "HOLD")

        if buy_sig and (not in_pos) and px > 0:
            in_pos = True
            entry_ts = row["timestamp"]
            entry_price = px
        elif sell_sig and in_pos and px > 0:
            in_pos = False
            entry_ts = pd.NaT
            entry_price = np.nan

    latest = feat.iloc[-1]
    unrealized_pct = float((float(latest["close"]) / entry_price - 1.0) * 100.0) if in_pos and pd.notna(entry_price) else 0.0
    return {
        "signal": signal,
        "in_position": bool(in_pos),
        "entry_ts": entry_ts,
        "entry_price": float(entry_price) if pd.notna(entry_price) else np.nan,
        "latest_ts": latest["timestamp"],
        "latest_close": float(latest["close"]),
        "unrealized_pct": unrealized_pct,
    }


def describe_scope_live_state(member_states: list[dict[str, object]], strategy: str) -> tuple[str, str, float]:
    if not member_states:
        return ("HOLD 0/0", "flat_no_members", np.nan)

    buy_count = sum(1 for state in member_states if state["signal"] == "BUY")
    sell_count = sum(1 for state in member_states if state["signal"] == "SELL")
    hold_count = sum(1 for state in member_states if state["signal"] == "HOLD")
    open_count = sum(1 for state in member_states if bool(state["in_position"]))
    label = f"{strategy} BUY {buy_count}/{len(member_states)} | SELL {sell_count}/{len(member_states)} | HOLD {hold_count}/{len(member_states)}"
    if len(member_states) == 1:
        state = member_states[0]
        pos_label = "long_open" if bool(state["in_position"]) else "flat"
        entry_ts = state.get("entry_ts")
        if bool(state["in_position"]) and pd.notna(entry_ts):
            pos_label = f"long_open_since_{pd.Timestamp(entry_ts).date()}"
        return (label, pos_label, float(state.get("unrealized_pct", np.nan)))

    if open_count == 0:
        pos_label = f"flat_{len(member_states)}/{len(member_states)}"
    elif open_count == len(member_states):
        pos_label = f"long_open_{len(member_states)}/{len(member_states)}"
    else:
        pos_label = f"mixed_open_{open_count}/{len(member_states)}"
    unrealized_values = [float(state.get("unrealized_pct", np.nan)) for state in member_states]
    finite_values = [v for v in unrealized_values if np.isfinite(v)]
    unrealized = float(np.mean(finite_values)) if finite_values else 0.0
    return (label, pos_label, unrealized)


def classify_refresh_data_health(member_sources: list[str]) -> str:
    if any("load_failed" in src for src in member_sources):
        return "refresh_data_unavailable"
    if any("fallback" in src for src in member_sources):
        return "ok_refresh_with_cache_fallback"
    return "ok_live_refresh"


def resolve_live_refresh_status(row_kind: str, *, signal_after: str, position_after: str) -> tuple[str, str, str]:
    if row_kind == "primary":
        return (
            "refresh_green_primary_live",
            "keep_primary_start_weekly_review",
            f"primary 日频账位已进入真实续写状态：当前 {signal_after}，{position_after}；后续应继续沿同一张 primary 账本做 market-close refresh，并等待首个 weekly review。",
        )
    if row_kind == "secondary_front_queue":
        return (
            "refresh_yellow_front_queue_live",
            "keep_secondary_then_stricter_front_recheck",
            f"front-queue secondary 已写实：当前 {signal_after}，{position_after}；它可以继续保留在 active secondary，但仍应优先接受 stricter front recheck，不能再靠 family 总体叙事遮盖。",
        )
    if row_kind == "secondary_mid_queue":
        return (
            "refresh_yellow_mid_queue_live",
            "keep_secondary_then_recheck_mid",
            f"mid-queue secondary 已落首份真实日频状态：当前 {signal_after}，{position_after}；这格可以继续独立记账，但资源顺序仍应排在 front queue 之后。",
        )
    if row_kind == "secondary_backstop":
        return (
            "refresh_green_backstop_live",
            "keep_secondary_backstop",
            f"backstop secondary 已有真实 market-close 状态：当前 {signal_after}，{position_after}；只要账本能稳定续写，就继续保留 backstop 身份，不抢 front-queue 资源。",
        )
    return (
        "refresh_green_shadow_live",
        "keep_shadow_until_promotion_gate",
        f"shadow lane 已写实成独立账位：当前 {signal_after}，{position_after}；recent-forward 改善仍不等于 promotion，继续只做 shadow 记账。",
    )


def collect_refresh_scope_states(cfg: dict[str, object]) -> tuple[list[str], list[str], list[dict[str, object]], list[dict[str, object]], list[pd.Timestamp]]:
    member_names: list[str] = []
    member_sources: list[str] = []
    ema_states: list[dict[str, object]] = []
    psar_states: list[dict[str, object]] = []
    latest_ts_list: list[pd.Timestamp] = []

    for member_cfg in cfg.get("members", []):
        member_names.append(str(member_cfg["asset"]))
        try:
            bars, source_mode = load_first_refresh_member_bars(member_cfg)
        except Exception:
            bars = pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])
            source_mode = "load_failed_no_cache"
        member_sources.append(source_mode)
        ema_state = summarize_long_only_live_state(bars, "EMA")
        psar_state = summarize_long_only_live_state(bars, "PSAR")
        ema_states.append(ema_state)
        psar_states.append(psar_state)
        if pd.notna(ema_state["latest_ts"]):
            latest_ts_list.append(pd.Timestamp(ema_state["latest_ts"]))

    return member_names, member_sources, ema_states, psar_states, latest_ts_list


def build_ema_paper_trading_first_refresh_delta(
    day0_snapshot_df: pd.DataFrame,
    first_refresh_queue_df: pd.DataFrame,
) -> pd.DataFrame:
    cols = [
        "refresh_rank",
        "refresh_clock_utc",
        "deployment_scope",
        "market_freq_book",
        "tracked_members",
        "latest_completed_bar_utc",
        "data_source",
        "signal_state_before",
        "signal_state_after",
        "position_state_before",
        "position_state_after",
        "benchmark_psar_state",
        "open_unrealized_pct",
        "monitor_status_before",
        "monitor_status_after",
        "review_action_before",
        "review_action_after",
        "data_health_after",
        "delta_note",
    ]
    if day0_snapshot_df.empty or first_refresh_queue_df.empty:
        return pd.DataFrame(columns=cols)

    snapshot_lookup = {
        (str(r["deployment_scope"]), str(r["market_freq_book"])): r
        for _, r in day0_snapshot_df.iterrows()
    }
    rows: list[dict[str, object]] = []
    refresh_clock = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    for _, queue_row in first_refresh_queue_df.sort_values("queue_rank").head(3).iterrows():
        scope = str(queue_row.get("deployment_scope", "-") or "-")
        market_freq_book = str(queue_row.get("market_freq_book", "-") or "-")
        if (scope, market_freq_book) not in EMA_FIRST_REFRESH_TOP_SCOPE_KEYS:
            continue
        cfg = EMA_DAILY_REFRESH_SCOPE_CONFIG.get((scope, market_freq_book))
        snapshot_row = snapshot_lookup.get((scope, market_freq_book))
        if cfg is None or snapshot_row is None:
            continue

        member_names, member_sources, ema_states, psar_states, latest_ts_list = collect_refresh_scope_states(cfg)
        signal_after, position_after, unrealized_pct = describe_scope_live_state(ema_states, "EMA")
        psar_signal_after, psar_position_after, _ = describe_scope_live_state(psar_states, "PSAR")
        benchmark_state = f"{psar_signal_after} | {psar_position_after}"
        latest_completed_bar_utc = max(latest_ts_list).strftime("%Y-%m-%d %H:%M UTC") if latest_ts_list else "-"
        data_health_after = classify_refresh_data_health(member_sources)
        monitor_after, review_after, delta_note = resolve_live_refresh_status(
            str(cfg.get("row_kind", "") or ""),
            signal_after=signal_after,
            position_after=position_after,
        )
        if data_health_after == "refresh_data_unavailable":
            monitor_after = "refresh_red_data_unavailable"
            review_after = "pause_refresh_fix_data_source"
            delta_note = f"本次 refresh 发生数据断流：{scope} 当前没有可用 live/cache 数据，需先修复数据源再继续按 runbook 续写。"

        rows.append(
            {
                "refresh_rank": int(queue_row.get("queue_rank", len(rows) + 1)),
                "refresh_clock_utc": refresh_clock,
                "deployment_scope": scope,
                "market_freq_book": market_freq_book,
                "tracked_members": " / ".join(member_names),
                "latest_completed_bar_utc": latest_completed_bar_utc,
                "data_source": " + ".join(sorted(set(member_sources))),
                "signal_state_before": str(snapshot_row.get("signal_state", "-") or "-"),
                "signal_state_after": signal_after,
                "position_state_before": str(snapshot_row.get("position_state", "-") or "-"),
                "position_state_after": position_after,
                "benchmark_psar_state": benchmark_state,
                "open_unrealized_pct": unrealized_pct,
                "monitor_status_before": str(snapshot_row.get("monitor_status", "-") or "-"),
                "monitor_status_after": monitor_after,
                "review_action_before": str(snapshot_row.get("review_action", "-") or "-"),
                "review_action_after": review_after,
                "data_health_after": data_health_after,
                "delta_note": delta_note,
            }
        )

    return pd.DataFrame(rows, columns=cols)


def build_ema_paper_trading_daily_refresh_snapshot(day0_snapshot_df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "refresh_rank",
        "refresh_clock_utc",
        "deployment_scope",
        "paper_status",
        "market_freq_book",
        "tracked_members",
        "latest_completed_bar_utc",
        "data_source",
        "signal_state",
        "position_state",
        "benchmark_psar_state",
        "open_unrealized_pct",
        "monitor_status",
        "review_action",
        "data_health",
        "refresh_note",
    ]
    if day0_snapshot_df.empty:
        return pd.DataFrame(columns=cols)

    refresh_clock = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    rows: list[dict[str, object]] = []

    active_rows = day0_snapshot_df.loc[
        day0_snapshot_df["market_freq_book"].astype(str).str.endswith("-1d")
        & day0_snapshot_df["paper_status"].astype(str).ne("exclude_stoplist")
    ].sort_values("snapshot_rank")

    for _, snapshot_row in active_rows.iterrows():
        scope = str(snapshot_row.get("deployment_scope", "-") or "-")
        market_freq_book = str(snapshot_row.get("market_freq_book", "-") or "-")
        cfg = EMA_DAILY_REFRESH_SCOPE_CONFIG.get((scope, market_freq_book))
        if cfg is None:
            continue

        member_names, member_sources, ema_states, psar_states, latest_ts_list = collect_refresh_scope_states(cfg)
        signal_state, position_state, unrealized_pct = describe_scope_live_state(ema_states, "EMA")
        psar_signal_state, psar_position_state, _ = describe_scope_live_state(psar_states, "PSAR")
        monitor_status, review_action, refresh_note = resolve_live_refresh_status(
            str(cfg.get("row_kind", "") or ""),
            signal_after=signal_state,
            position_after=position_state,
        )
        data_health = classify_refresh_data_health(member_sources)
        if data_health == "refresh_data_unavailable":
            monitor_status = "refresh_red_data_unavailable"
            review_action = "pause_refresh_fix_data_source"
            refresh_note = f"{scope} 当前 refresh 数据不可用（无 live 且无可用 cache），先修复数据源再继续写账。"

        rows.append(
            {
                "refresh_rank": int(snapshot_row.get("snapshot_rank", len(rows) + 1)),
                "refresh_clock_utc": refresh_clock,
                "deployment_scope": scope,
                "paper_status": str(snapshot_row.get("paper_status", "-") or "-"),
                "market_freq_book": market_freq_book,
                "tracked_members": " / ".join(member_names),
                "latest_completed_bar_utc": max(latest_ts_list).strftime("%Y-%m-%d %H:%M UTC") if latest_ts_list else "-",
                "data_source": " + ".join(sorted(set(member_sources))),
                "signal_state": signal_state,
                "position_state": position_state,
                "benchmark_psar_state": f"{psar_signal_state} | {psar_position_state}",
                "open_unrealized_pct": unrealized_pct,
                "monitor_status": monitor_status,
                "review_action": review_action,
                "data_health": data_health,
                "refresh_note": refresh_note,
            }
        )

    return pd.DataFrame(rows, columns=cols)




def build_ema_paper_trading_refresh_dependency_audit(daily_refresh_snapshot_df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "dependency_rank",
        "deployment_scope",
        "paper_status",
        "market_freq_book",
        "data_source",
        "latest_completed_bar_utc",
        "data_health",
        "dependency_status",
        "ops_priority",
        "deployment_read",
        "next_action",
        "why_it_matters",
    ]
    if daily_refresh_snapshot_df.empty:
        return pd.DataFrame(columns=cols)

    rows: list[dict[str, object]] = []

    for _, row in daily_refresh_snapshot_df.sort_values(["refresh_rank", "deployment_scope"]).iterrows():
        scope = str(row.get("deployment_scope", "-") or "-")
        paper_status = str(row.get("paper_status", "-") or "-")
        market_freq_book = str(row.get("market_freq_book", "-") or "-")
        data_source = str(row.get("data_source", "-") or "-")
        latest_completed_bar_utc = str(row.get("latest_completed_bar_utc", "-") or "-")
        data_health = str(row.get("data_health", "-") or "-")
        monitor_status = str(row.get("monitor_status", "-") or "-")
        review_action = str(row.get("review_action", "-") or "-")

        dependency_status = "live"
        ops_priority = "p4_keep_live_refresh"
        deployment_read = "当前 lane 已有 live refresh，后续重点不在修数据源，而在继续按既定 honesty / review 节奏续跑。"
        next_action = "继续沿同一张账本做 market-close refresh；若 verdict 变差，再按 runbook 的 demote / rollback 规则处理。"
        why_it_matters = "这格现在更像运行中 lane，而不是 source blocker。"
        priority_rank = 40

        if "load_failed" in data_source or data_health == "refresh_data_unavailable":
            dependency_status = "broken"
            ops_priority = "p0_fix_data_source_now"
            deployment_read = "这不是 alpha 问题，而是账本已经断流；不先修源，就不能继续把这条 lane 当成真实 paper/shadow 观察对象。"
            next_action = "先修复 live/cache 数据源，再恢复常规 refresh；在此之前默认暂停这条 lane 的日常续写。"
            why_it_matters = "断流会直接让后续 review 与 ledger 失真。"
            priority_rank = 0
        elif "fallback" in data_source and paper_status == "active_primary":
            dependency_status = "cache_fallback"
            ops_priority = "p1_primary_live_source_upgrade"
            deployment_read = "EMA 现在已经能继续 paper/shadow 续写，但唯一 primary pilot 仍靠 cache fallback；当前最像 deployment blocker 的已经是 source-risk，而不是新的 alpha wording。"
            next_action = "优先把唯一 primary `创业板ETF 1d` 从 cache fallback 升成可重复的 live source；在那之前每次 refresh 都必须复核 cache freshness。"
            why_it_matters = "`closest to paper` 若长期停在 fallback，会让 primary ledger 的运行诚实度变差。"
            priority_rank = 10
        elif "fallback" in data_source and paper_status == "shadow_watch":
            dependency_status = "cache_fallback"
            ops_priority = "p2_shadow_fallback_watch"
            deployment_read = "这格仍只做 shadow；fallback 依赖值得记录，但资源顺序应排在 primary 修源之后。"
            next_action = "继续保留 shadow 账位；若之后要补 live source，默认跟在 primary A股日频之后，不抢主资源。"
            why_it_matters = "shadow lane 的职责是独立观察，不是抢先升级；source 风险要管，但不应盖过 primary。"
            priority_rank = 20
        elif "fallback" in data_source:
            dependency_status = "cache_fallback"
            ops_priority = "p3_nonprimary_fallback_watch"
            deployment_read = "这格可继续跑，但 source 仍有 fallback 依赖；如果后续还要继续扩 active lanes，先把 fallback SLA 说清更诚实。"
            next_action = "继续运行，但把 refresh freshness 与 fallback 可用性写进日常 review；必要时再升级 live source。"
            why_it_matters = "非 primary 的 fallback 不会立刻否掉 lane，但会增加运营摩擦。"
            priority_rank = 30
        elif paper_status == "active_secondary_backstop" and "front_queue" in monitor_status:
            dependency_status = "live"
            ops_priority = "p3_front_queue_honesty_recheck"
            deployment_read = "这格的 live source 已到位；当前更该优先盯的是 front-queue honesty，而不是再为数据源加工作量。"
            next_action = "继续按 front-queue 做 stricter honesty recheck；除非数据再次断流，否则不必把 source 修复排在最前。"
            why_it_matters = "front queue 的 blocker 已从 source 转到是否还能继续留在 active secondary。"
            priority_rank = 31
        elif paper_status == "active_secondary_backstop" and "mid_queue" in monitor_status:
            dependency_status = "live"
            ops_priority = "p4_mid_queue_keep_live"
            deployment_read = "这格已经 live 且仍属 mid-queue secondary；默认先保持独立记账，不需要额外 source 工作。"
            next_action = "继续按 mid-queue 节奏 refresh，并等待 front queue 之后的更严格 recheck。"
            why_it_matters = "mid-queue 当前更像‘继续看’，不是运营硬阻塞。"
            priority_rank = 41
        elif paper_status == "active_secondary_backstop":
            dependency_status = "live"
            ops_priority = "p5_backstop_keep_live"
            deployment_read = "这格 live + backstop 状态已经足够支撑日常续写；现在不必为了它再开新的运营支线。"
            next_action = "继续保留 live refresh；只在 front / mid queue 稳住后，再考虑是否需要更严格 recheck。"
            why_it_matters = "backstop 的价值在于稳定续写，而不是抢前排资源。"
            priority_rank = 50
        elif paper_status == "active_primary":
            dependency_status = "live"
            ops_priority = "p2_primary_keep_live"
            deployment_read = "唯一 primary 已是 live；当前下一刀应回到连续 refresh / weekly review，而不是 source 修复。"
            next_action = "继续沿 primary ledger 做 market-close refresh，并按周复核是否仍守住 active_primary。"
            why_it_matters = "当 primary 已 live 时，真正的 deployment 重点会回到前瞻表现，而不是数据可用性。"
            priority_rank = 21
        elif paper_status == "shadow_watch":
            dependency_status = "live"
            ops_priority = "p4_shadow_keep_live"
            deployment_read = "shadow lane 已 live；继续 shadow 观察即可，不需要额外 source 动作。"
            next_action = "继续 shadow refresh；只有 promotion gate 真补齐时，才讨论升格。"
            why_it_matters = "live shadow 的意义是继续诚实观察，而不是提前 promotion。"
            priority_rank = 42

        rows.append(
            {
                "dependency_rank": priority_rank,
                "deployment_scope": scope,
                "paper_status": paper_status,
                "market_freq_book": market_freq_book,
                "data_source": data_source,
                "latest_completed_bar_utc": latest_completed_bar_utc,
                "data_health": data_health,
                "dependency_status": dependency_status,
                "ops_priority": ops_priority,
                "deployment_read": deployment_read,
                "next_action": next_action,
                "why_it_matters": why_it_matters,
            }
        )

    return pd.DataFrame(rows, columns=cols).sort_values(["dependency_rank", "deployment_scope"]).reset_index(drop=True)


def parse_utc_label(value: object) -> datetime | None:
    text = str(value or "").strip()
    if not text or text == "-":
        return None
    for fmt in ["%Y-%m-%d %H:%M UTC", "%Y-%m-%d %H:%M:%S UTC"]:
        try:
            return datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None



def next_daily_close_utc(now_utc: datetime, market_freq_book: str) -> tuple[datetime | None, str]:
    market = str(market_freq_book or "")
    if market == "Crypto-1d":
        candidate = now_utc.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        return candidate, "UTC 日线收盘"

    if market == "A股-1d":
        close_hour = 7
        label = "A股日线收盘"
    elif market == "美股-1d":
        close_hour = 20
        label = "美股日线收盘"
    else:
        return None, "manual"

    candidate = now_utc.replace(hour=close_hour, minute=0, second=0, microsecond=0)
    if candidate <= now_utc:
        candidate += timedelta(days=1)
    while candidate.weekday() >= 5:
        candidate += timedelta(days=1)
    return candidate, label



def fmt_time_gap(now_utc: datetime, target_utc: datetime | None) -> str:
    if target_utc is None:
        return "-"
    hours = max((target_utc - now_utc).total_seconds() / 3600.0, 0.0)
    if hours >= 48:
        return f"约 {hours / 24.0:.1f} 天"
    if hours >= 24:
        return f"约 {hours / 24.0:.1f} 天"
    return f"约 {hours:.1f} 小时"



def fmt_signed_time_gap(now_utc: datetime, target_utc: datetime | None) -> str:
    if target_utc is None:
        return "-"
    delta_hours = (target_utc - now_utc).total_seconds() / 3600.0
    abs_hours = abs(delta_hours)
    if abs_hours >= 48:
        gap = f"约 {abs_hours / 24.0:.1f} 天"
    elif abs_hours >= 24:
        gap = f"约 {abs_hours / 24.0:.1f} 天"
    else:
        gap = f"约 {abs_hours:.1f} 小时"
    if delta_hours > 0:
        return f"{gap} 后到点"
    if delta_hours < 0:
        return f"已过 {gap}"
    return "现在到点"



def build_ema_paper_trading_refresh_clock_audit(
    daily_refresh_snapshot_df: pd.DataFrame,
    day0_snapshot_df: pd.DataFrame,
) -> pd.DataFrame:
    cols = [
        "clock_rank",
        "deployment_scope",
        "paper_status",
        "market_freq_book",
        "refresh_clock_utc",
        "latest_completed_bar_utc",
        "data_source",
        "clock_status",
        "next_expected_close_utc",
        "time_to_next_close",
        "week1_review_due_utc",
        "time_to_week1_review",
        "week1_status",
        "current_clock_read",
        "next_gate",
        "why_it_matters",
    ]
    if daily_refresh_snapshot_df.empty:
        return pd.DataFrame(columns=cols)

    now_utc = datetime.now(timezone.utc)
    day0_lookup = {
        str(row.get("deployment_scope", "-")): parse_utc_label(row.get("snapshot_clock_utc", "-"))
        for row in day0_snapshot_df.to_dict("records")
    }

    rows: list[dict[str, object]] = []
    for _, row in daily_refresh_snapshot_df.sort_values(["refresh_rank", "deployment_scope"]).iterrows():
        scope = str(row.get("deployment_scope", "-") or "-")
        paper_status = str(row.get("paper_status", "-") or "-")
        market_freq_book = str(row.get("market_freq_book", "-") or "-")
        refresh_clock_utc = str(row.get("refresh_clock_utc", "-") or "-")
        latest_completed_bar_utc = str(row.get("latest_completed_bar_utc", "-") or "-")
        data_source = str(row.get("data_source", "-") or "-")
        monitor_status = str(row.get("monitor_status", "-") or "-")
        data_health = str(row.get("data_health", "-") or "-")

        next_close_utc, close_label = next_daily_close_utc(now_utc, market_freq_book)
        week1_due_utc = None
        day0_clock = day0_lookup.get(scope)
        if day0_clock is not None:
            week1_due_utc = day0_clock + timedelta(days=7)

        if data_health == "refresh_data_unavailable":
            clock_status = "blocked_data_issue"
        else:
            clock_status = "on_clock_waiting_next_close"

        if week1_due_utc is None:
            week1_status = "week1_not_configured"
        elif now_utc >= week1_due_utc:
            week1_status = "week1_due_now"
        else:
            week1_status = "week1_not_due"

        if paper_status == "active_primary":
            current_clock_read = f"当前没有新的已收盘 bar 可继续写；primary ledger 现在是在按计划等待下一次 {close_label}，不是 stale 掉。"
        elif paper_status == "active_secondary_backstop" and "front_queue" in monitor_status:
            current_clock_read = f"front-queue secondary 现在不是卡在 source，而是在按时等待下一次 {close_label}；那之后才该继续判 keep / stricter recheck / demote。"
        elif paper_status == "active_secondary_backstop" and "mid_queue" in monitor_status:
            current_clock_read = f"mid-queue secondary 当前同样 on-clock；先等下一次 {close_label}，再决定是否需要更严格 recheck。"
        elif paper_status == "active_secondary_backstop":
            current_clock_read = f"backstop secondary 当前也在按计划等待下一次 {close_label}；今天没有新 bar 不等于它停转。"
        elif paper_status == "shadow_watch":
            current_clock_read = f"shadow lane 当前也是按计划等待下一次 {close_label}；在 promotion gate 真过线前，正确动作仍是继续记 shadow。"
        else:
            current_clock_read = "当前 lane 不在常规 on-clock refresh 范围内。"

        next_gate = "等待下一次真实 completed bar。"
        if next_close_utc is not None:
            next_gate = f"先等 {next_close_utc.strftime('%Y-%m-%d %H:%M UTC')} 左右的{close_label}（距今 {fmt_time_gap(now_utc, next_close_utc)}）再续写同一张 ledger。"
        if week1_due_utc is not None:
            next_gate += f" week-1 review 最早约在 {week1_due_utc.strftime('%Y-%m-%d %H:%M UTC')}（距今 {fmt_time_gap(now_utc, week1_due_utc)}）。"

        why_it_matters = "它把“现在没新 refresh”与“账本真的停了”区分开，避免在周末/非收盘时段误判 ledger 断续。"
        if paper_status == "active_primary":
            why_it_matters = "primary 现在更需要真实下一笔 forward refresh，而不是被周末/非收盘时段的空窗误读成停转。"
        elif paper_status == "shadow_watch":
            why_it_matters = "shadow lane 的职责是继续诚实观察；当前最重要的是别把‘暂时没新 bar’误读成可以偷渡 promotion。"

        rows.append(
            {
                "clock_rank": int(row.get("refresh_rank", len(rows) + 1)),
                "deployment_scope": scope,
                "paper_status": paper_status,
                "market_freq_book": market_freq_book,
                "refresh_clock_utc": refresh_clock_utc,
                "latest_completed_bar_utc": latest_completed_bar_utc,
                "data_source": data_source,
                "clock_status": clock_status,
                "next_expected_close_utc": next_close_utc.strftime("%Y-%m-%d %H:%M UTC") if next_close_utc is not None else "-",
                "time_to_next_close": fmt_time_gap(now_utc, next_close_utc),
                "week1_review_due_utc": week1_due_utc.strftime("%Y-%m-%d %H:%M UTC") if week1_due_utc is not None else "-",
                "time_to_week1_review": fmt_time_gap(now_utc, week1_due_utc),
                "week1_status": week1_status,
                "current_clock_read": current_clock_read,
                "next_gate": next_gate,
                "why_it_matters": why_it_matters,
            }
        )

    return pd.DataFrame(rows, columns=cols).sort_values(["clock_rank", "deployment_scope"]).reset_index(drop=True)


def build_ema_paper_trading_next_close_action_queue(
    refresh_clock_audit_df: pd.DataFrame,
) -> pd.DataFrame:
    cols = [
        "queue_rank",
        "deployment_scope",
        "paper_status",
        "next_expected_close_utc",
        "time_to_next_close",
        "action_when_due",
        "if_not_due",
        "if_blocked",
        "why_this_step",
    ]
    if refresh_clock_audit_df.empty:
        return pd.DataFrame(columns=cols)

    rows: list[dict[str, object]] = []
    active = refresh_clock_audit_df[
        refresh_clock_audit_df["paper_status"].isin(["active_primary", "active_secondary_backstop", "shadow_watch"])
    ].copy()
    if active.empty:
        return pd.DataFrame(columns=cols)

    active["_next_ts"] = pd.to_datetime(active["next_expected_close_utc"], utc=True, errors="coerce")
    active = active.sort_values(["_next_ts", "clock_rank", "deployment_scope"], na_position="last")

    for i, row in enumerate(active.to_dict("records"), start=1):
        scope = str(row.get("deployment_scope", "-") or "-")
        paper_status = str(row.get("paper_status", "-") or "-")
        clock_status = str(row.get("clock_status", "-") or "-")
        week1_status = str(row.get("week1_status", "-") or "-")

        if paper_status == "active_primary":
            action_when_due = "新 completed bar 到达后，先更新 primary ledger（signal/position/return），再判 monitor_status 是否仍可 keep_primary。"
            why_this_step = "primary 是 closest-to-paper 的核心位；下一笔真实 refresh 直接影响 paper admission 可信度。"
        elif paper_status == "active_secondary_backstop":
            action_when_due = "按同一收盘时点更新 secondary lane，并按 queue 判 keep / stricter recheck / demote。"
            why_this_step = "secondary 不能再整批口头维持，必须逐 lane 用真实 refresh 决策升降级。"
        else:
            action_when_due = "更新 shadow ledger 并复核 promotion gate；默认继续 stay shadow，不偷渡升格。"
            why_this_step = "shadow 的价值是诚实观察，不是用局部好转提前改写 admission 结论。"

        if week1_status == "week1_due_now":
            action_when_due += " 同步触发 week-1 review（green/yellow/red -> keep/demote/stop）。"

        if_not_due = "保持 waiting_next_close；不补伪 forward，不新增近义 runbook wording。"
        if clock_status == "blocked_data_issue":
            if_blocked = "先修数据连续性（data_source / refresh_clock）再写账；未修复前维持 shadow-only 或 stop。"
        else:
            if_blocked = "若执行时发现时点错位/数据缺口，立即记为 blocked 并回到 runbook 的 rollback 路径。"

        rows.append(
            {
                "queue_rank": i,
                "deployment_scope": scope,
                "paper_status": paper_status,
                "next_expected_close_utc": str(row.get("next_expected_close_utc", "-") or "-"),
                "time_to_next_close": str(row.get("time_to_next_close", "-") or "-"),
                "action_when_due": action_when_due,
                "if_not_due": if_not_due,
                "if_blocked": if_blocked,
                "why_this_step": why_this_step,
            }
        )

    return pd.DataFrame(rows, columns=cols)



def build_ema_paper_trading_due_guardrail_snapshot(
    refresh_clock_audit_df: pd.DataFrame,
) -> pd.DataFrame:
    cols = [
        "guardrail_rank",
        "deployment_scope",
        "paper_status",
        "latest_completed_bar_utc",
        "next_expected_close_utc",
        "relative_due_gap",
        "due_bucket",
        "week1_status",
        "guardrail_action",
        "if_missed",
        "why_it_matters",
    ]
    if refresh_clock_audit_df.empty:
        return pd.DataFrame(columns=cols)

    now_utc = datetime.now(timezone.utc)
    rows: list[dict[str, object]] = []
    active = refresh_clock_audit_df[
        refresh_clock_audit_df["paper_status"].isin(["active_primary", "active_secondary_backstop", "shadow_watch"])
    ].copy()
    if active.empty:
        return pd.DataFrame(columns=cols)

    active["_next_ts"] = pd.to_datetime(active["next_expected_close_utc"], utc=True, errors="coerce")
    active = active.sort_values(["_next_ts", "clock_rank", "deployment_scope"], na_position="last")

    for i, row in enumerate(active.to_dict("records"), start=1):
        paper_status = str(row.get("paper_status", "-") or "-")
        clock_status = str(row.get("clock_status", "-") or "-")
        week1_status = str(row.get("week1_status", "-") or "-")
        next_close_utc = parse_utc_label(row.get("next_expected_close_utc", "-"))
        due_hours = None if next_close_utc is None else (next_close_utc - now_utc).total_seconds() / 3600.0

        if clock_status == "blocked_data_issue":
            due_bucket = "blocked_before_due"
            guardrail_action = "先修数据连续性与 refresh 时点，再谈续写；未修复前不允许把 lane 假装成正常 waiting。"
            if_missed = "若 close 已过且仍 blocked，直接记成 blocked refresh，并按 runbook 走 shadow-only / rollback。"
            why_it_matters = "它先把真 blocker 钉死，避免把数据问题包装成‘只是还没到点’。"
        elif next_close_utc is None or due_hours is None:
            due_bucket = "unscheduled"
            guardrail_action = "先补齐 market close 时点定义，再决定 refresh；在 schedule 缺失前不应继续累计 narrative。"
            if_missed = "若 schedule 长期缺失，应把 lane 视为配置问题，而不是继续口头维持 active。"
            why_it_matters = "没有明确 close，就无法判断 waiting / due / overdue。"
        elif due_hours > 6:
            due_bucket = "waiting_not_due"
            guardrail_action = "继续 waiting_next_close；保持 queue 就绪，但不补伪 refresh。"
            if_missed = "若后续 close 已过仍没新 ledger，再从 waiting 切到 due-now / overdue 检查。"
            why_it_matters = "这说明当前是真的还没到 refresh 时点，不该硬做不存在的新 bar。"
        elif due_hours > 0:
            due_bucket = "due_soon"
            guardrail_action = "这条 lane 已进入 due-soon 窗口；下一次 close 一到，优先按 next-close action queue 落账。"
            if_missed = "若 close 过后还停在 waiting，就不该继续补说明页，而要先核查 refresh 是否漏跑。"
            why_it_matters = "它把‘今天晚些时候该刷’单独拎出来，避免在最后几小时还把任务当成纯等待。"
        elif due_hours >= -12:
            due_bucket = "due_now_refresh_window"
            guardrail_action = "预计 close 已到；现在默认应先写同一张 ledger。若 week-1 也到时，则同步做 green/yellow/red review。"
            if_missed = "若执行时仍拿不到新 completed bar 或 refresh 结果，立即记 blocked，并回到 runbook 的 rollback 路径。"
            why_it_matters = "这一步把‘已经该刷了’从 waiting 状态里剥出来，避免真正到点后还在写近义说明。"
        else:
            due_bucket = "overdue_refresh_check"
            guardrail_action = "这条 lane 已过预计 close 较久；应优先核查是否漏记 refresh / close 时点错位，并暂停新增 narrative。"
            if_missed = "若确认 close 已过且无新 ledger，默认记为 missed refresh check；未解释清楚前不应继续把它当正常 active。"
            why_it_matters = "它把迟到 refresh 变成显式异常，而不是让 stale 继续伪装成 waiting。"

        if paper_status == "active_primary" and due_bucket in {"due_soon", "due_now_refresh_window", "overdue_refresh_check"}:
            guardrail_action += " primary lane 优先级最高。"
        elif paper_status == "shadow_watch" and due_bucket in {"due_now_refresh_window", "overdue_refresh_check"}:
            guardrail_action += " shadow lane 默认仍只记 shadow，不偷渡 promotion。"

        rows.append(
            {
                "guardrail_rank": i,
                "deployment_scope": str(row.get("deployment_scope", "-") or "-"),
                "paper_status": paper_status,
                "latest_completed_bar_utc": str(row.get("latest_completed_bar_utc", "-") or "-"),
                "next_expected_close_utc": str(row.get("next_expected_close_utc", "-") or "-"),
                "relative_due_gap": fmt_signed_time_gap(now_utc, next_close_utc),
                "due_bucket": due_bucket,
                "week1_status": week1_status,
                "guardrail_action": guardrail_action,
                "if_missed": if_missed,
                "why_it_matters": why_it_matters,
            }
        )

    return pd.DataFrame(rows, columns=cols)


def build_ema_paper_trading_refresh_history_audit(
    refresh_history_df: pd.DataFrame,
) -> pd.DataFrame:
    cols = [
        "history_rank",
        "deployment_scope",
        "paper_status",
        "market_freq_book",
        "rows_recorded",
        "distinct_completed_bars",
        "latest_completed_bar_utc",
        "latest_history_recorded_at_utc",
        "latest_data_source",
        "latest_signal_state",
        "latest_position_state",
        "history_status",
        "continuity_read",
        "next_needed_to_advance",
    ]
    if refresh_history_df.empty:
        return pd.DataFrame(columns=cols)

    history = refresh_history_df.copy()
    for col in ["latest_completed_bar_utc", "history_recorded_at_utc"]:
        history[f"_{col}_ts"] = pd.to_datetime(history.get(col), utc=True, errors="coerce")

    rows: list[dict[str, object]] = []
    grouped = history.groupby(["deployment_scope", "market_freq_book"], dropna=False, sort=False)
    for i, ((scope, market_freq_book), group) in enumerate(grouped, start=1):
        group = group.sort_values(["_latest_completed_bar_utc_ts", "_history_recorded_at_utc_ts"], na_position="last")
        latest = group.iloc[-1].to_dict()
        rows_recorded = int(len(group))
        distinct_completed_bars = int(group["latest_completed_bar_utc"].astype(str).nunique())
        distinct_history_keys = int(group.get("history_key", pd.Series(dtype=str)).astype(str).nunique())

        if distinct_history_keys < rows_recorded or distinct_completed_bars < rows_recorded:
            history_status = "duplicate_bar_warning"
            continuity_read = "这格 append-only ledger 出现重复 bar / key 痕迹；下一轮 refresh 前应先查重与 dedupe，不宜直接把它当正常连续续写。"
            next_needed = "先修 history 去重，再继续同一张 ledger。"
        elif rows_recorded <= 1:
            history_status = "seed_only_history"
            continuity_read = "这格的 append-only ledger 已经建好，但目前还只有 1 条 completed-bar 记录；它更像 day-0/首刷 seed，尚未进入真正连续续写。"
            next_needed = "等待下一根真实 completed bar，把单条 seed history 推成 2+ 条连续记录。"
        else:
            history_status = "append_only_continuing"
            continuity_read = "这格已经不只是一张覆盖式 snapshot，而是在同一张 append-only ledger 上累计 completed-bar 历史；可继续用它看 refresh / review 是否真的连续。"
            next_needed = "继续沿同一张 ledger 续写，并关注是否出现 missed refresh / duplicate key。"

        rows.append(
            {
                "history_rank": i,
                "deployment_scope": str(scope or "-"),
                "paper_status": str(latest.get("paper_status", "-") or "-"),
                "market_freq_book": str(market_freq_book or "-"),
                "rows_recorded": rows_recorded,
                "distinct_completed_bars": distinct_completed_bars,
                "latest_completed_bar_utc": str(latest.get("latest_completed_bar_utc", "-") or "-"),
                "latest_history_recorded_at_utc": str(latest.get("history_recorded_at_utc", "-") or "-"),
                "latest_data_source": str(latest.get("data_source", "-") or "-"),
                "latest_signal_state": str(latest.get("signal_state", "-") or "-"),
                "latest_position_state": str(latest.get("position_state", "-") or "-"),
                "history_status": history_status,
                "continuity_read": continuity_read,
                "next_needed_to_advance": next_needed,
            }
        )

    return pd.DataFrame(rows, columns=cols)


def build_baseline_family_survivor_slice(cost_combo_df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "strategy",
        "baseline_bucket",
        "combos",
        "positive_gross_share",
        "median_profit_pct",
        "median_trades",
        "positive_only_median_breakeven_cost_bps",
        "survive_20bps_share",
        "survive_50bps_share",
    ]
    if cost_combo_df.empty:
        return pd.DataFrame(columns=cols)

    rows: list[dict] = []
    for strategy in ["EMA", "PSAR"]:
        for bucket, mask in [
            ("non60m (1d+1wk)", cost_combo_df["interval"].astype(str) != "60m"),
            ("60m only", cost_combo_df["interval"].astype(str) == "60m"),
        ]:
            sub = cost_combo_df[(cost_combo_df["strategy"] == strategy) & mask].copy()
            if sub.empty:
                continue
            pos = sub[sub["profit_pct"] > 0].copy()
            rows.append(
                {
                    "strategy": strategy,
                    "baseline_bucket": bucket,
                    "combos": int(len(sub)),
                    "positive_gross_share": float((sub["profit_pct"] > 0).mean()),
                    "median_profit_pct": float(sub["profit_pct"].median()),
                    "median_trades": float(sub["nt"].median()),
                    "positive_only_median_breakeven_cost_bps": float(pos["breakeven_roundtrip_cost_bps"].median()) if not pos.empty else np.nan,
                    "survive_20bps_share": float((sub["breakeven_roundtrip_cost_bps"] >= 20).mean()),
                    "survive_50bps_share": float((sub["breakeven_roundtrip_cost_bps"] >= 50).mean()),
                }
            )
    return pd.DataFrame(rows, columns=cols)


def build_ema_final_survivor_map(
    cost_combo_df: pd.DataFrame,
    rolling_overall_df: pd.DataFrame,
    daily_holdout_pocket_df: pd.DataFrame,
    weekly_holdout_pocket_df: pd.DataFrame,
) -> pd.DataFrame:
    cols = [
        "sort_key",
        "pocket_scope",
        "evidence_tier",
        "current_label",
        "family_bucket",
        "key_numbers",
        "project_read",
    ]
    rows: list[dict] = []

    def add(
        sort_key: int,
        pocket_scope: str,
        evidence_tier: str,
        current_label: str,
        family_bucket: str,
        key_numbers: str,
        project_read: str,
    ) -> None:
        rows.append(
            {
                "sort_key": sort_key,
                "pocket_scope": pocket_scope,
                "evidence_tier": evidence_tier,
                "current_label": current_label,
                "family_bucket": family_bucket,
                "key_numbers": key_numbers,
                "project_read": project_read,
            }
        )

    ema = cost_combo_df[cost_combo_df["strategy"] == "EMA"].copy()

    if not rolling_overall_df.empty:
        row = rolling_overall_df.iloc[0]
        add(
            1,
            "Crypto 60m（BTC/ETH/SOL rolling）",
            "rolling falsification",
            "fail pocket",
            "移出 EMA family",
            f"net20 正窗口 {fmt_pct(float(row['net20_positive_window_share']) * 100.0)}；多数窗口为正资产 {int(row['majority_net20_assets'])}/{int(row['assets'])}",
            "这块已经不该再被拿来当 EMA baseline 的支持证据。",
        )

    static_groups = [
        (
            6,
            "贵州茅台 1d+1wk",
            (ema["asset"] == "贵州茅台") & (ema["interval"].astype(str) != "60m"),
            "暂保留 / 非前线 backstop",
            "保留在 EMA family（次级 backstop）",
            "这两格目前不在最薄 frontier 上，说明 A股并不只剩 frontier 两格在替 EMA 撑着。",
        ),
        (
            7,
            "美股 1d+1wk（SPY/QQQ/AAPL）",
            (ema["asset_class"] == "美股") & (ema["interval"].astype(str) != "60m"),
            "保留 / 厚 backstop survivor",
            "保留在 EMA family（厚 backstop）",
            "这批更像 family 仍然厚实的 backstop，而不是下一刀最该先 falsify 的前线。",
        ),
        (
            8,
            "Crypto 1d+1wk（BTC/ETH/SOL）",
            (ema["asset_class"] == "Crypto") & (ema["interval"].astype(str) != "60m"),
            "保留 / 厚 backstop survivor",
            "保留在 EMA family（厚 backstop）",
            "当前更像 EMA family 的远端 backstop，说明这条线并没有被 recent 60m fail 一刀全灭。",
        ),
    ]
    for sort_key, label, mask, current_label, family_bucket, project_read in static_groups:
        sub = ema[mask].copy()
        if sub.empty:
            continue
        add(
            sort_key,
            label,
            "长样本 gross / cost backstop",
            current_label,
            family_bucket,
            f"{len(sub)}/{len(sub)} 组合 gross 为正；median breakeven {fmt_bps(float(sub['breakeven_roundtrip_cost_bps'].median()))}",
            project_read,
        )

    daily_meta = {
        "创业板ETF": (2, "keep: daily survivor", "保留在 EMA family", "这是 strict holdout 下仍能替 EMA 守门的 daily pocket。"),
        "沪深300ETF": (3, "mixed / watch", "保留但降级为 mixed", "这格比 weekly 诚实，但还不够厚，不该再被当成 family 的硬支撑。"),
    }
    for asset, (sort_key, current_label, family_bucket, project_read) in daily_meta.items():
        sub = daily_holdout_pocket_df[daily_holdout_pocket_df["asset"] == asset].copy()
        if sub.empty:
            continue
        row = sub.iloc[0]
        add(
            sort_key,
            f"{asset} 1d",
            "strict holdout",
            current_label,
            family_bucket,
            "；".join(
                [
                    f"EMA 正 holdout {fmt_pct(float(row['ema_net20_positive_holdout_share']) * 100.0)} / median net20 {fmt_pct(float(row['ema_net20_median_profit_pct']))}",
                    f"PSAR {fmt_pct(float(row['psar_net20_positive_holdout_share']) * 100.0)} / {fmt_pct(float(row['psar_net20_median_profit_pct']))}",
                ]
            ),
            project_read,
        )

    for sort_key, asset in [(4, "沪深300ETF"), (5, "创业板ETF")]:
        sub = weekly_holdout_pocket_df[weekly_holdout_pocket_df["asset"] == asset].copy()
        if sub.empty:
            continue
        row = sub.iloc[0]
        add(
            sort_key,
            f"{asset} 1wk",
            "strict holdout",
            "remove / PSAR-lean",
            "移出 EMA family",
            "；".join(
                [
                    f"EMA 正 holdout {fmt_pct(float(row['ema_net20_positive_holdout_share']) * 100.0)} / median net20 {fmt_pct(float(row['ema_net20_median_profit_pct']))}",
                    f"PSAR {fmt_pct(float(row['psar_net20_positive_holdout_share']) * 100.0)} / {fmt_pct(float(row['psar_net20_median_profit_pct']))}",
                ]
            ),
            "这格已经更像 PSAR / mixed branch，不该再继续算作 EMA baseline family 的支持 pocket。",
        )

    out = pd.DataFrame(rows, columns=cols)
    if out.empty:
        return out
    return out.sort_values("sort_key").reset_index(drop=True)


def build_ema_paper_candidate_spec(final_map_df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "admission_rank",
        "admission_bucket",
        "deployment_scope",
        "default_mode",
        "evidence_anchor",
        "why_now",
        "operating_note",
    ]
    if final_map_df.empty:
        return pd.DataFrame(columns=cols)

    final_map_lookup = final_map_df.set_index("pocket_scope").to_dict("index")
    rows: list[dict] = []

    def add(
        admission_rank: int,
        admission_bucket: str,
        deployment_scope: str,
        default_mode: str,
        why_now: str,
        operating_note: str,
    ) -> None:
        evidence_anchor = final_map_lookup.get(deployment_scope, {}).get("key_numbers", "-")
        rows.append(
            {
                "admission_rank": admission_rank,
                "admission_bucket": admission_bucket,
                "deployment_scope": deployment_scope,
                "default_mode": default_mode,
                "evidence_anchor": evidence_anchor,
                "why_now": why_now,
                "operating_note": operating_note,
            }
        )

    add(
        1,
        "paper_now_primary",
        "创业板ETF 1d",
        "直接进入 EMA baseline paper pilot",
        "这是当前 strict holdout 下最干净、最像样的 daily survivor，适合作为 A股侧的主试点口袋。",
        "单独建一条 paper 曲线；先不要和 mixed pocket 合并成 A股 bundle。",
    )
    add(
        2,
        "paper_now_secondary",
        "美股 1d+1wk（SPY/QQQ/AAPL）",
        "进入 secondary baseline paper batch",
        "这批 nonfrontier backstop 仍然厚，适合提供跨市场 baseline 对照。",
        "1d 与 1wk 分开记账，先当 family backstop 批次，不和 A股试点混成一条总曲线。",
    )
    add(
        3,
        "paper_now_secondary",
        "Crypto 1d+1wk（BTC/ETH/SOL）",
        "进入 secondary baseline paper batch",
        "recent 60m fail 并没有把更高频率以外的 crypto baseline 全部打掉，这批仍是远端厚 backstop。",
        "只做 1d/1wk；明确排除 60m 变体，避免让 fail pocket 混回 baseline。",
    )
    add(
        4,
        "paper_now_secondary",
        "贵州茅台 1d+1wk",
        "进入 A股非前线 secondary batch",
        "A股并不只剩 frontier 两格在撑 EMA，这两格可作为非前线 A股 backstop 观察对象。",
        "继续和 frontier 分开看；若后续要收窄 A股范围，优先保留这类非前线 backstop。",
    )
    add(
        5,
        "shadow_only",
        "沪深300ETF 1d",
        "只做 shadow watch，不进入正式 paper batch",
        "它比 weekly 诚实，但当前仍是 mixed / watch pocket，不够厚，尚不足以并入 baseline 正式范围。",
        "保留信号与净值观察，但默认不和 primary/secondary baseline 汇总。",
    )
    add(
        6,
        "exclude",
        "沪深300ETF 1wk",
        "移出 EMA paper scope",
        "strict holdout 下已更像 PSAR-lean / mixed branch，不该继续算 EMA baseline family 支撑。",
        "若要继续看，只能放在 PSAR/mixed 支线，不进入 EMA baseline paper。",
    )
    add(
        7,
        "exclude",
        "创业板ETF 1wk",
        "移出 EMA paper scope",
        "strict holdout 下也已更像 PSAR-lean，而不是 EMA baseline 的支持口袋。",
        "不进入 EMA paper；若后续 reopen，也只能当 weekly mixed/PSAR 支线重验。",
    )
    add(
        8,
        "exclude",
        "Crypto 60m（BTC/ETH/SOL rolling）",
        "移出 EMA paper scope",
        "rolling falsification 已把它打进 fail pocket，当前不应再拿去做 baseline paper。",
        "明确排除 60m crypto，避免以 overlay 或个别窗口反弹重新包装 fail pocket。",
    )

    return pd.DataFrame(rows, columns=cols)


def build_ema_paper_operating_spec(candidate_spec_df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "monitor_rank",
        "deployment_scope",
        "paper_track",
        "recording_rule",
        "continue_rule",
        "promotion_or_demotion_rule",
    ]
    if candidate_spec_df.empty:
        return pd.DataFrame(columns=cols)

    rows: list[dict] = []

    def add(
        monitor_rank: int,
        deployment_scope: str,
        paper_track: str,
        recording_rule: str,
        continue_rule: str,
        promotion_or_demotion_rule: str,
    ) -> None:
        rows.append(
            {
                "monitor_rank": monitor_rank,
                "deployment_scope": deployment_scope,
                "paper_track": paper_track,
                "recording_rule": recording_rule,
                "continue_rule": continue_rule,
                "promotion_or_demotion_rule": promotion_or_demotion_rule,
            }
        )

    add(
        1,
        "创业板ETF 1d",
        "primary paper pilot",
        "单独记一条 A股 pilot 曲线；不与 secondary batch、mixed pocket、weekly/exclude 口袋合并。",
        "只要它还能独立代表 strict-holdout survivor，就继续让它承担 EMA baseline 的 primary pilot。",
        "若后续更严格复核开始滑向 mixed/watch 或明显转成 PSAR-lean，就从 primary 降到 shadow，而不是继续拿 secondary/backstop 来稀释主试点结果。",
    )
    add(
        2,
        "美股 1d+1wk（SPY/QQQ/AAPL）",
        "secondary backstop batch",
        "1d 与 1wk 分开记账；只作为跨市场 backstop，对外汇总时不得和 primary pilot 合成一条“EMA family 总曲线”。",
        "继续当厚 backstop，用来回答 EMA baseline 是否不只在 A股 daily 成立。",
        "若后续更严格 honesty 把其中任一 pocket 打回 mixed/watch 或 fail，就把该 pocket 直接移出 secondary，而不是继续靠同批别的口袋遮盖。",
    )
    add(
        3,
        "Crypto 1d+1wk（BTC/ETH/SOL）",
        "secondary backstop batch",
        "只运行 1d / 1wk；明确禁止把 60m 重新混回 baseline paper 范围。",
        "继续作为 crypto 侧的高频外 backstop，证明 recent 60m fail 不等于更高周期也一起失效。",
        "若后续复核发现 secondary 结果主要靠单一资产/单一周期支撑，就收窄到更具体 pocket；60m fail pocket 则保持排除，不因 overlay 或局部窗口反弹 reopen。",
    )
    add(
        4,
        "贵州茅台 1d+1wk",
        "secondary A股 nonfrontier batch",
        "和 frontier A股分开记账；只当非前线 backstop，不和 primary pilot 混成一个 A股 bundle。",
        "继续承担“A股并不只剩 frontier 两格在撑 EMA”这一层 backstop 证明。",
        "若后续 stricter recheck 也转弱，就直接从 A股 secondary 移出；不要再借它去替 mixed 的沪深300ETF 1d 站台。",
    )
    add(
        5,
        "沪深300ETF 1d",
        "shadow watch only",
        "只保留独立 shadow 观察，不并入任何正式 paper batch。",
        "继续当 mixed pocket 观察项，回答它会不会在下一轮更严格 recheck 中转强。",
        "若继续原地踏步或更像 weekly 那样转向 PSAR/mixed，就直接移出；若真的转强，再单独申请从 shadow 升级，而不是自动并回 baseline batch。",
    )
    add(
        6,
        "沪深300ETF 1wk",
        "hard exclude",
        "默认停用，不进入 EMA baseline paper。",
        "当前只保留为历史反证：这格更像 PSAR-lean / mixed branch。",
        "除非有新的、更强证据包明确 overturn 当前 holdout 结论，否则保持 exclude，不做“先挂着看看”。",
    )
    add(
        7,
        "创业板ETF 1wk",
        "hard exclude",
        "默认停用，不进入 EMA baseline paper。",
        "当前同样只保留为历史反证，而不是 EMA family 的 live pocket。",
        "除非未来有全新证据能推翻当前 weekly holdout 读法，否则保持 exclude，不因 A股 daily 表现较好就顺带重开。",
    )
    add(
        8,
        "Crypto 60m（BTC/ETH/SOL rolling）",
        "hard exclude",
        "默认停用，不进入任何 EMA baseline paper / shadow 汇总。",
        "它当前的角色是 fail-pocket 反证，用来提醒别把高频幻觉混回 baseline。",
        "只有新的、独立证据包明确推翻 rolling fail，才允许 reopen；在那之前，不得靠 PSAR overlay、局部窗口反弹或 family 汇总重新包装。",
    )

    return pd.DataFrame(rows, columns=cols)


def build_ema_paper_monitoring_board(
    candidate_spec_df: pd.DataFrame,
    operating_spec_df: pd.DataFrame,
    shadow_promotion_df: pd.DataFrame,
) -> pd.DataFrame:
    cols = [
        "review_rank",
        "deployment_scope",
        "paper_status",
        "evidence_anchor",
        "monitor_focus",
        "keep_running_if",
        "escalate_or_stop_if",
        "current_read",
    ]
    if candidate_spec_df.empty or operating_spec_df.empty:
        return pd.DataFrame(columns=cols)

    op_lookup = operating_spec_df.set_index("deployment_scope").to_dict("index")
    shadow_lookup = shadow_promotion_df.set_index("asset").to_dict("index") if not shadow_promotion_df.empty else {}
    rows: list[dict] = []

    for _, row in candidate_spec_df.sort_values("admission_rank").iterrows():
        scope = str(row["deployment_scope"])
        bucket = str(row["admission_bucket"])
        op = op_lookup.get(scope, {})
        evidence_anchor = str(row.get("evidence_anchor", "-"))

        if bucket == "paper_now_primary":
            paper_status = "active_primary"
            monitor_focus = "单独盯 primary pilot 是否仍保住 strict-holdout survivor 身份；不许和 secondary/backstop 混成 family 总曲线。"
            keep_running_if = str(op.get("continue_rule", "-"))
            escalate_or_stop_if = str(op.get("promotion_or_demotion_rule", "-"))
            current_read = "当前唯一 primary paper pilot；核心任务不是扩 family，而是先守住这格 daily survivor 的 deployment 身份。"
        elif bucket == "paper_now_secondary":
            paper_status = "active_secondary_backstop"
            monitor_focus = "按 market × freq 分开记账；任何单 pocket 转弱就单独移出，不许靠同批别的口袋遮盖。"
            keep_running_if = str(op.get("continue_rule", "-"))
            escalate_or_stop_if = str(op.get("promotion_or_demotion_rule", "-"))
            current_read = "当前只当 secondary backstop；存在意义是证明 EMA baseline 不只剩一格 A股 daily，而不是拿来稀释 primary。"
        elif bucket == "shadow_only":
            paper_status = "shadow_watch"
            asset = scope.replace(" 1d", "")
            shadow = shadow_lookup.get(asset, {})
            gate_hits = shadow.get("gate_hits", np.nan)
            gate_hits_text = f"{int(gate_hits)}/5" if pd.notna(gate_hits) else "-"
            overall_pos = shadow.get("overall_ema_positive_holdout_share", np.nan)
            overall_beats = shadow.get("overall_ema_beats_psar_share", np.nan)
            pos_text = fmt_pct(float(overall_pos) * 100.0) if pd.notna(overall_pos) else "-"
            beats_text = fmt_pct(float(overall_beats) * 100.0) if pd.notna(overall_beats) else "-"
            monitor_focus = "优先盯 overall 正 holdout 占比与 overall 跑赢 PSAR 占比能否同时补到 ≥62.5%；recent 单窗变好还不够。"
            keep_running_if = str(op.get("recording_rule", "-"))
            escalate_or_stop_if = "若 shadow promotion gate 升到 4/5 以上且 overall 两项同时过线，再单独申请升格；若继续原地踏步或转弱，则维持 shadow/移出。"
            current_read = f"当前 promotion gate 约 {gate_hits_text}；overall 正 holdout 约 {pos_text}、overall 跑赢 PSAR 约 {beats_text}，所以更诚实的位置仍是 shadow。"
        else:
            paper_status = "exclude_stoplist"
            monitor_focus = "默认不做日常 paper admission 跟踪；只在出现新的 overturn evidence 时才 reopen。"
            keep_running_if = str(op.get("recording_rule", "默认停用"))
            escalate_or_stop_if = str(op.get("promotion_or_demotion_rule", "-"))
            current_read = "当前属于 hard exclude / fail-mixed stoplist；不应再靠 family 汇总、overlay 或局部窗口反弹重新混回 baseline paper。"

        rows.append(
            {
                "review_rank": int(row["admission_rank"]),
                "deployment_scope": scope,
                "paper_status": paper_status,
                "evidence_anchor": evidence_anchor,
                "monitor_focus": monitor_focus,
                "keep_running_if": keep_running_if,
                "escalate_or_stop_if": escalate_or_stop_if,
                "current_read": current_read,
            }
        )

    return pd.DataFrame(rows, columns=cols)


def build_ema_paper_trading_runbook(
    candidate_spec_df: pd.DataFrame,
    operating_spec_df: pd.DataFrame,
    monitoring_board_df: pd.DataFrame,
    recent_forward_audit_df: pd.DataFrame,
    daily_overlay_pocket_df: pd.DataFrame,
) -> pd.DataFrame:
    cols = [
        "runbook_rank",
        "deployment_scope",
        "runbook_status",
        "data_source",
        "refresh_frequency",
        "ledger_rule",
        "review_rule",
        "promote_or_demote_rule",
        "kill_switch_or_rollback",
        "current_runbook_read",
    ]
    if candidate_spec_df.empty or operating_spec_df.empty or monitoring_board_df.empty:
        return pd.DataFrame(columns=cols)

    op_lookup = operating_spec_df.set_index("deployment_scope").to_dict("index")
    board_lookup = monitoring_board_df.set_index("deployment_scope").to_dict("index")
    recent_lookup = recent_forward_audit_df.set_index("asset").to_dict("index") if not recent_forward_audit_df.empty else {}
    overlay_lookup = daily_overlay_pocket_df.set_index("asset").to_dict("index") if not daily_overlay_pocket_df.empty else {}
    rows: list[dict] = []

    for _, row in candidate_spec_df.sort_values("admission_rank").iterrows():
        scope = str(row["deployment_scope"])
        bucket = str(row["admission_bucket"])
        op = op_lookup.get(scope, {})
        board = board_lookup.get(scope, {})
        status = str(board.get("paper_status", bucket))
        ledger_rule = str(op.get("recording_rule", "-"))
        current_read = str(board.get("current_read", "-"))

        if scope == "创业板ETF 1d":
            recent = recent_lookup.get("创业板ETF", {})
            overlay = overlay_lookup.get("创业板ETF", {})
            recent_verdict = str(recent.get("forward_honesty_verdict", "-"))
            overlay_verdict = str(overlay.get("overlay_verdict", "-"))
            overlay_reading = str(overlay.get("deployment_reading", "-"))
            data_source = "优先走 Eastmoney A 股日线 live K线（`159915.SZ -> 0.159915`）；若接口暂时不可用，则回退到 `reports/artifacts/ema_psar_raw_alpha/refresh_bootstrap_cache/eastmoney_159915_sz_1d.csv` 缓存，避免 primary ledger 断流。"
            refresh_frequency = "每个 A 股日线收盘后刷新 1 次；每周固定做 1 次 monitoring review。"
            review_rule = f"primary pilot 单独记账、单独看路径；周 review 重点看 monitoring board 是否仍是 active_primary，月度再复核 recent-forward 是否仍保持 `{recent_verdict}`；PSAR 快退出若继续观察，也只允许按 `ema_chinext_daily_psar_shadow_protocol.csv` 做 sidecar shadow review，不改默认 EMA 持有规则。"
            promote_or_demote_rule = "继续保留 primary 的前提，是 recent-forward 仍为正且 monitoring board 不连续转红；若两次 review 连续转 red 或更像 mixed/watch，则从 primary 降回 shadow。"
            kill_switch_or_rollback = "数据断流、规则无法更新、或 review 无法按时落账时，立即暂停 primary，退回 shadow-only；在真实 paper 开始前，真钱始终保持 0。"
            current_read = f"{current_read}；PSAR overlay 当前读法：`{overlay_verdict}`——{overlay_reading}；若继续推进，也只按 `创业板ETF 1d` 的 narrow shadow protective protocol 做 sidecar 观察，不提前改默认规则。"
        elif scope == "美股 1d+1wk（SPY/QQQ/AAPL）":
            data_source = "复用 `regime_switch_indicator_stack_replication` 的美股 bars 与 `cross_market_results / ema_psar_cost_budget_by_combo` 证据；1d 与 1wk 分账维护。"
            refresh_frequency = "1d 在每个美股收盘后刷新；1wk 在周线收盘后刷新；每周做 1 次 secondary backstop review。"
            review_rule = "按 market × freq 双账本更新，不允许把 1d / 1wk 混成一条总曲线；周 review 只看这组 backstop 自己是否继续成立。"
            promote_or_demote_rule = "若任一单 pocket 连续两次 weekly review 转 red，或后续更严格 honesty 把它打回 mixed/watch，就把该 pocket 从 active_secondary_backstop 降回 shadow，而不是继续和同批别的 pocket 合讲。"
            kill_switch_or_rollback = "任一单 pocket 出现数据断流、执行口径缺失、或无法按 market × freq 继续独立记账时，该 pocket 立即退回 shadow；不得拿同批别的口袋遮盖。"
        elif scope == "Crypto 1d+1wk（BTC/ETH/SOL）":
            data_source = "复用 `regime_switch_indicator_stack_replication` 的 crypto 1d/1wk bars 与 cost-budget 证据；明确排除 60m fail pocket。"
            refresh_frequency = "1d 按 UTC 日线收盘后刷新；1wk 在周线收盘后刷新；每周做 1 次 secondary review。"
            review_rule = "1d 与 1wk 分账；review 时单独检查 1d / 1wk 是否仍能当 crypto backstop，严禁把 60m overlay 或 fail pocket 混回 baseline。"
            promote_or_demote_rule = "若 backstop 结果开始主要依赖单一资产 / 单一周期，或任一 pocket 被更严格 honesty 打回 mixed/watch，就把该 pocket 降回 shadow；60m 仍保持 exclude。"
            kill_switch_or_rollback = "一旦出现数据更新失败、1d/1wk 无法分账、或 60m fail pocket 被误混回报表，就立即停止该组 active_secondary_backstop，回到 shadow-only。"
        elif scope == "贵州茅台 1d+1wk":
            data_source = "复用上游 replication bars 与 cost-budget 证据；按 A 股 1d / 1wk 双账本维护，不与 frontier A 股 pilot 合并。"
            refresh_frequency = "1d 每个 A 股收盘后刷新；1wk 周线收盘后刷新；每周做 1 次 secondary A 股 backstop review。"
            review_rule = "这组的任务是证明 A 股并不只剩 frontier 两格在撑 EMA；因此 review 时必须与创业板ETF primary、沪深300ETF shadow 分开看。"
            promote_or_demote_rule = "若更严格复核后转弱，直接从 active_secondary_backstop 降回 shadow；不能再借这组结果去替 mixed 的沪深300ETF 1d 站台。"
            kill_switch_or_rollback = "若双账本无法独立维护、数据断流、或 review 发现它只剩个别口袋在硬撑，则立刻退回 shadow，不再作为 active secondary 汇报。"
        elif scope == "沪深300ETF 1d":
            recent = recent_lookup.get("沪深300ETF", {})
            overlay = overlay_lookup.get("沪深300ETF", {})
            recent_verdict = str(recent.get("forward_honesty_verdict", "-"))
            overlay_verdict = str(overlay.get("overlay_verdict", "-"))
            overlay_reading = str(overlay.get("deployment_reading", "-"))
            data_source = "优先走 Eastmoney A 股日线 live K线（`510300.SS -> 1.510300`）；若接口暂时不可用，则回退到 `reports/artifacts/ema_psar_raw_alpha/refresh_bootstrap_cache/eastmoney_510300_ss_1d.csv` 缓存，保持 shadow 账本连续。"
            refresh_frequency = "每个 A 股日线收盘后刷新 1 次；每周固定做 1 次 shadow-promotion review。"
            review_rule = f"继续独立记 shadow 曲线；review 时先看 overall 正 holdout 占比与 overall 跑赢 PSAR 占比能否同时补到 ≥62.5%，再看 recent-forward 是否仍停在 `{recent_verdict}`；PSAR overlay 不能拿来替代 promotion gate。"
            promote_or_demote_rule = "只有当 shadow promotion gate 升到 4/5 以上、overall 两项同时过线，且 recent-forward 不再落后 PSAR，才允许单独申请升格；否则继续 stay shadow。"
            kill_switch_or_rollback = "若 recent-forward 再翻负、继续落后 PSAR、或 shadow 账本无法独立维护，就维持 / 降出 shadow，不得靠 recent 单窗好转偷渡升格。"
            current_read = f"{current_read}；recent-forward 当前仍是 `{recent_verdict}`；PSAR overlay 当前读法：`{overlay_verdict}`——{overlay_reading}"
        else:
            data_source = "当前只保留历史反证：weekly frontier 与 crypto 60m 维持 stoplist，不进入日常 paper 数据流。"
            refresh_frequency = "不做常规刷新；只有出现新的 overturn evidence 时才重开。"
            review_rule = "默认不进日常 runbook review，只在独立新证据包真正挑战当前 fail/mixed verdict 时复核。"
            promote_or_demote_rule = "保持 exclude_stoplist；除非新的、独立证据包明确推翻现有 holdout / rolling 结论，否则不进入 paper/shadow admission。"
            kill_switch_or_rollback = "这里没有‘继续跑一跑看看’；默认就是停用。若被误混回 baseline 汇报，应立即回滚到 stoplist。"

        rows.append(
            {
                "runbook_rank": int(row["admission_rank"]),
                "deployment_scope": scope,
                "runbook_status": status,
                "data_source": data_source,
                "refresh_frequency": refresh_frequency,
                "ledger_rule": ledger_rule,
                "review_rule": review_rule,
                "promote_or_demote_rule": promote_or_demote_rule,
                "kill_switch_or_rollback": kill_switch_or_rollback,
                "current_runbook_read": current_read,
            }
        )

    return pd.DataFrame(rows, columns=cols)


def build_ema_paper_trading_kickoff_checklist(
    runbook_df: pd.DataFrame,
    monitoring_board_df: pd.DataFrame,
) -> pd.DataFrame:
    cols = [
        "step_rank",
        "check_item",
        "when_to_do",
        "pass_if",
        "why_it_exists",
    ]
    if runbook_df.empty or monitoring_board_df.empty:
        return pd.DataFrame(columns=cols)

    def scopes_with(status: str) -> str:
        scopes = runbook_df.loc[runbook_df["runbook_status"] == status, "deployment_scope"].astype(str).tolist()
        return " / ".join(scopes) if scopes else "-"

    primary_scope = scopes_with("active_primary")
    secondary_scopes = scopes_with("active_secondary_backstop")
    shadow_scopes = scopes_with("shadow_watch")
    stoplist_scopes = scopes_with("exclude_stoplist")

    rows = [
        {
            "step_rank": 1,
            "check_item": "冻结 day-0 scope roster",
            "when_to_do": "启动前一次性",
            "pass_if": f"primary 只含 `{primary_scope}`；secondary 只含 `{secondary_scopes}`；shadow 只含 `{shadow_scopes}`；stoplist 继续排除 `{stoplist_scopes}`。",
            "why_it_exists": "先把 keep / shadow / exclude 的边界写死，避免 mixed 或 fail pocket 被偷渡进 paper 账本。",
        },
        {
            "step_rank": 2,
            "check_item": "按 scope 建 4 类独立账本",
            "when_to_do": "启动当天",
            "pass_if": "至少同时有 `primary_paper`、`secondary_backstop`、`shadow_watch`、`stoplist/reopen-only` 四类 ledger，不允许把 market × freq 混成一条总曲线。",
            "why_it_exists": "runbook 已要求分 market × freq 记账；这一步把‘怎么记’落实成 day-0 的执行边界。",
        },
        {
            "step_rank": 3,
            "check_item": "把 refresh cadence 写进日历",
            "when_to_do": "启动当天",
            "pass_if": "A 股 / 美股 / crypto 的 1d、1wk 刷新时点都已落到固定日历；weekly review 也有固定检查点。",
            "why_it_exists": "没有固定刷新时点，forward ledger 很容易事后补记，破坏 honesty。",
        },
        {
            "step_rank": 4,
            "check_item": "强制记录 monitoring status + review action",
            "when_to_do": "每次 weekly review",
            "pass_if": "每次 review 都必须同时填 `monitor_status`（green/yellow/red）与 `review_action`（keep/demote/stop/reopen）；缺一视为 review 无效。",
            "why_it_exists": "这一步把 monitoring board 真接到 promote / demote / rollback，而不是只留静态标签。",
        },
        {
            "step_rank": 5,
            "check_item": "先用数据健康检查代替‘继续观察’借口",
            "when_to_do": "每次 refresh",
            "pass_if": "若 `data_health` 不是 `ok`，或账本字段缺失，就直接记成暂停 / rollback，不允许先口头继续跑。",
            "why_it_exists": "让 kill switch 从概念变成 day-0 就能执行的硬动作。",
        },
    ]
    return pd.DataFrame(rows, columns=cols)


def build_ema_paper_trading_ledger_template(runbook_df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "field_order",
        "field_name",
        "fill_for",
        "update_cadence",
        "example_or_rule",
        "why_it_matters",
    ]
    if runbook_df.empty:
        return pd.DataFrame(columns=cols)

    def scopes_with(status: str) -> str:
        scopes = runbook_df.loc[runbook_df["runbook_status"] == status, "deployment_scope"].astype(str).tolist()
        return " / ".join(scopes) if scopes else "-"

    primary_scope = scopes_with("active_primary")
    secondary_scopes = scopes_with("active_secondary_backstop")
    shadow_scopes = scopes_with("shadow_watch")
    stoplist_scopes = scopes_with("exclude_stoplist")

    rows = [
        {
            "field_order": 1,
            "field_name": "asof_date_utc",
            "fill_for": "所有 active / shadow 账本",
            "update_cadence": "每次 refresh",
            "example_or_rule": "例如 `2026-03-15`；统一按当次 bar close / review 截止时点记。",
            "why_it_matters": "固定前瞻记账时点，避免事后补账或回头改口径。",
        },
        {
            "field_order": 2,
            "field_name": "deployment_scope",
            "fill_for": "所有账本",
            "update_cadence": "初始化 + 每次 refresh",
            "example_or_rule": f"只允许来自当前 runbook：`{primary_scope}` / `{secondary_scopes}` / `{shadow_scopes}` / `{stoplist_scopes}`。",
            "why_it_matters": "把 pocket 边界写死，防止把 keep / shadow / exclude 混成同一条曲线。",
        },
        {
            "field_order": 3,
            "field_name": "ledger_book",
            "fill_for": "所有账本",
            "update_cadence": "初始化 + 每次 refresh",
            "example_or_rule": "`primary_paper` / `secondary_backstop` / `shadow_watch` / `stoplist_reopen_only` 四选一。",
            "why_it_matters": "明确这笔记录属于哪类 admission 状态，后续 promote/demote 才可审计。",
        },
        {
            "field_order": 4,
            "field_name": "market_freq_book",
            "fill_for": "所有 active / shadow 账本",
            "update_cadence": "每次 refresh",
            "example_or_rule": "例如 `A股-1d`、`美股-1wk`、`Crypto-1d`；不允许把 1d / 1wk 混成一行。",
            "why_it_matters": "runbook 已要求 market × freq 分账；这列是防止稀释 pocket honesty 的硬钉子。",
        },
        {
            "field_order": 5,
            "field_name": "signal_state",
            "fill_for": "所有 active / shadow 账本",
            "update_cadence": "每次 refresh",
            "example_or_rule": "`flat` / `long` / `hold`；若 stoplist 则写 `excluded`。",
            "why_it_matters": "先把信号状态和研究 verdict 对齐，避免只记结果不记当时该不该持有。",
        },
        {
            "field_order": 6,
            "field_name": "position_state",
            "fill_for": "所有 active / shadow 账本",
            "update_cadence": "每次 refresh",
            "example_or_rule": "记录当前是否持仓、仓位方向、是否刚开 / 刚平。",
            "why_it_matters": "paper / shadow 的最小记账单位不是观点，而是可追溯的持仓状态。",
        },
        {
            "field_order": 7,
            "field_name": "gross_pnl_pct",
            "fill_for": "所有 active / shadow 账本",
            "update_cadence": "每次 refresh",
            "example_or_rule": "记录当前持仓或已平仓周期的 gross 路径。",
            "why_it_matters": "先保留原始路径，方便和历史研究基线对照。",
        },
        {
            "field_order": 8,
            "field_name": "net_pnl_pct_20bps",
            "fill_for": "所有 active / shadow 账本",
            "update_cadence": "每次 refresh",
            "example_or_rule": "沿用当前研究默认 `20bps` 近似；若未来升级净值引擎，再保持字段名但更新口径说明。",
            "why_it_matters": "确保 daily/weekly ledger 与当前报告里的 net 口径可直接对上。",
        },
        {
            "field_order": 9,
            "field_name": "benchmark_psar_net20_pct",
            "fill_for": "primary / shadow / mixed pocket review",
            "update_cadence": "每次 weekly review",
            "example_or_rule": "尤其用于 `沪深300ETF 1d`：不能只看 EMA 自己转正，还要看是否仍落后 PSAR。",
            "why_it_matters": "让 shadow promotion / demotion 继续锚定当前项目的 head-to-head honesty。",
        },
        {
            "field_order": 10,
            "field_name": "monitor_status",
            "fill_for": "所有 active / shadow 账本",
            "update_cadence": "每次 weekly review",
            "example_or_rule": "`green` / `yellow` / `red`；必须与 monitoring board 的当前状态一致。",
            "why_it_matters": "这是把 monitoring board 接进真实运行的核心字段。",
        },
        {
            "field_order": 11,
            "field_name": "review_action",
            "fill_for": "所有账本",
            "update_cadence": "每次 weekly review",
            "example_or_rule": "`keep` / `demote_to_shadow` / `stop` / `reopen_for_review`。",
            "why_it_matters": "没有 action 字段，就无法审计 promote / demote / rollback 是否真的执行。",
        },
        {
            "field_order": 12,
            "field_name": "data_health",
            "fill_for": "所有账本",
            "update_cadence": "每次 refresh",
            "example_or_rule": "`ok` / `missing` / `stale`；若不是 `ok`，直接触发暂停或 rollback。",
            "why_it_matters": "把 kill switch 从‘提醒’变成可以日常打钩的执行条件。",
        },
        {
            "field_order": 13,
            "field_name": "note",
            "fill_for": "所有账本",
            "update_cadence": "按需",
            "example_or_rule": "只记录当次最关键原因：例如‘secondary pocket 连续两周 red -> 降回 shadow’。",
            "why_it_matters": "保留最小审计注释，方便后续回看为什么升降级。",
        },
    ]
    return pd.DataFrame(rows, columns=cols)


def build_ema_paper_trading_day0_seed_rows(runbook_df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "seed_rank",
        "deployment_scope",
        "ledger_book",
        "market_freq_book",
        "refresh_cadence",
        "signal_state",
        "position_state",
        "monitor_status",
        "review_action",
        "data_health",
        "seed_rule",
    ]
    if runbook_df.empty:
        return pd.DataFrame(columns=cols)

    ledger_book_map = {
        "active_primary": "primary_paper",
        "active_secondary_backstop": "secondary_backstop",
        "shadow_watch": "shadow_watch",
        "exclude_stoplist": "stoplist_reopen_only",
    }

    def infer_market(scope: str) -> str:
        if "美股" in scope:
            return "美股"
        if "Crypto" in scope:
            return "Crypto"
        return "A股"

    def infer_intervals(scope: str) -> list[str]:
        if "1d+1wk" in scope:
            return ["1d", "1wk"]
        if "1wk" in scope:
            return ["1wk"]
        if "60m" in scope:
            return ["60m"]
        return ["1d"]

    rows: list[dict[str, str]] = []
    seed_rank = 1
    for _, row in runbook_df.sort_values("runbook_rank").iterrows():
        scope = str(row.get("deployment_scope", "-") or "-")
        status = str(row.get("runbook_status", "-") or "-")
        refresh = str(row.get("refresh_frequency", "-") or "-")
        ledger_book = ledger_book_map.get(status, "shadow_watch")
        market = infer_market(scope)
        intervals = infer_intervals(scope)

        for interval in intervals:
            is_stoplist = status == "exclude_stoplist"
            rows.append(
                {
                    "seed_rank": seed_rank,
                    "deployment_scope": scope,
                    "ledger_book": ledger_book,
                    "market_freq_book": f"{market}-{interval}",
                    "refresh_cadence": refresh,
                    "signal_state": "excluded" if is_stoplist else "flat",
                    "position_state": "excluded" if is_stoplist else "flat_waiting_first_signal",
                    "monitor_status": "stopped" if is_stoplist else "pending_day0_review",
                    "review_action": "keep_excluded" if is_stoplist else "kickoff_freeze",
                    "data_health": "n/a_stoplist" if is_stoplist else "pending_first_refresh",
                    "seed_rule": (
                        "stoplist 默认不启动，只保留 reopen-only 审计位。"
                        if is_stoplist
                        else "先建 seed row，再按 market × freq 开始前瞻记账；未首刷前不允许补历史。"
                    ),
                }
            )
            seed_rank += 1

    return pd.DataFrame(rows, columns=cols)


def build_ema_paper_first_week_review_scorecard(
    runbook_df: pd.DataFrame,
    monitoring_board_df: pd.DataFrame,
) -> pd.DataFrame:
    cols = [
        "review_rank",
        "deployment_scope",
        "first_review_clock",
        "must_fill_fields",
        "green_if",
        "yellow_if",
        "red_if",
        "default_action",
        "why_it_matters",
    ]
    if runbook_df.empty or monitoring_board_df.empty:
        return pd.DataFrame(columns=cols)

    board_lookup = monitoring_board_df.set_index("deployment_scope").to_dict("index")
    rows: list[dict[str, str]] = []

    for _, row in runbook_df.sort_values("runbook_rank").iterrows():
        scope = str(row.get("deployment_scope", "-") or "-")
        status = str(row.get("runbook_status", "-") or "-")
        refresh = str(row.get("refresh_frequency", "-") or "-")
        current_read = str(board_lookup.get(scope, {}).get("current_read", "-") or "-")

        if status == "active_primary":
            green_if = "`data_health = ok`，primary 账本仍独立，且 review 读法没有从 `active_primary` 滑回 mixed/watch。"
            yellow_if = "首周出现 1 次 refresh 缺失、或路径明显变薄但还没推翻 current read；允许继续跑，但必须加做一次补充 review。"
            red_if = "账本无法独立维护、连续 red、或 review 已更像 `mixed/watch` / `shadow`。"
            default_action = "green = keep_primary；yellow = keep + extra review；red = demote_to_shadow。"
            why_it_matters = "primary pilot 的目标不是‘先跑起来再说’，而是第一周就证明自己还能独立代表 EMA baseline。"
        elif status == "active_secondary_backstop":
            green_if = "`market × freq` 分账完整，单 pocket 的 `data_health` 都是 `ok`，且没有 pocket 在首周就被打回 mixed/watch。"
            yellow_if = "个别 pocket 首周缺 1 次 refresh、或 edge 变薄但还没被更严格 honesty 明确打回 mixed/watch。"
            red_if = "任一 pocket 连续 red、无法继续独立分账、或已经明显落入 mixed/watch / fail。"
            default_action = "green = keep_secondary；yellow = keep_that_pocket_with_watch；red = demote_that_pocket_to_shadow（不是整批一起遮盖）。"
            why_it_matters = "secondary 的作用只是 backstop；第一周最怕的不是亏一点，而是又把坏 pocket 混进‘secondary 总曲线’。"
        elif status == "shadow_watch":
            green_if = "`data_health = ok`，shadow 账本独立，且 review 仍能诚实写成 `positive_but_not_promotable / stay shadow`。"
            yellow_if = "recent-forward 方向没塌，但 overall gate 仍未同时补到 promotion 阈值；继续 stay shadow。"
            red_if = "recent-forward 再翻负、继续落后 PSAR，或 shadow 账本都无法独立维护。"
            default_action = "green = keep_shadow；yellow = keep_shadow；red = keep_or_drop_shadow（默认不准偷渡升格）。"
            why_it_matters = "沪深300ETF 1d 当前最容易被‘最近转正了’误读成快能晋升；这张表就是把这个错觉拦在第一周。"
        else:
            green_if = "stoplist 继续保持排除、没有被误混回 active / shadow 账本。"
            yellow_if = "出现新的独立证据包想 challenge 旧 verdict，但本周还没到 reopen 标准；继续 keep excluded。"
            red_if = "fail/mixed pocket 被误混回 baseline 汇报，或 stoplist 账位缺失导致 reopen 审计断档。"
            default_action = "green = keep_excluded；yellow = hold_for_reopen_review；red = rollback_to_stoplist_now。"
            why_it_matters = "weekly frontier 与 crypto 60m 当前最重要的职责就是当反证；第一周也不能把这道边界放松。"

        rows.append(
            {
                "review_rank": int(row.get("runbook_rank", len(rows) + 1)),
                "deployment_scope": scope,
                "first_review_clock": refresh,
                "must_fill_fields": "`data_health / monitor_status / review_action / net_pnl_pct_20bps`；primary/shadow 另加 `benchmark_psar_net20_pct`，secondary 必须逐个 `market_freq_book` 分账。",
                "green_if": green_if,
                "yellow_if": yellow_if,
                "red_if": red_if,
                "default_action": default_action,
                "why_it_matters": f"{why_it_matters} 当前读法：{current_read}",
            }
        )

    return pd.DataFrame(rows, columns=cols)


def build_ema_paper_trading_day0_snapshot(
    day0_seed_rows_df: pd.DataFrame,
    monitoring_board_df: pd.DataFrame,
    first_week_review_df: pd.DataFrame,
    secondary_recheck_df: pd.DataFrame,
    *,
    snapshot_clock_utc: str,
) -> pd.DataFrame:
    cols = [
        "snapshot_rank",
        "snapshot_clock_utc",
        "deployment_scope",
        "paper_status",
        "ledger_book",
        "market_freq_book",
        "signal_state",
        "position_state",
        "monitor_status",
        "review_action",
        "data_health",
        "first_review_clock",
        "day0_note",
    ]
    if day0_seed_rows_df.empty or monitoring_board_df.empty:
        return pd.DataFrame(columns=cols)

    board_lookup = monitoring_board_df.set_index("deployment_scope").to_dict("index")
    review_lookup = first_week_review_df.set_index("deployment_scope").to_dict("index") if not first_week_review_df.empty else {}
    secondary_df = secondary_recheck_df.copy() if not secondary_recheck_df.empty else pd.DataFrame()
    rows: list[dict[str, str]] = []

    for _, row in day0_seed_rows_df.sort_values("seed_rank").iterrows():
        scope = str(row.get("deployment_scope", "-") or "-")
        ledger_book = str(row.get("ledger_book", "-") or "-")
        market_freq_book = str(row.get("market_freq_book", "-") or "-")
        interval = market_freq_book.split("-", 1)[-1] if "-" in market_freq_book else market_freq_book
        paper_status = str(board_lookup.get(scope, {}).get("paper_status", "exclude_stoplist" if ledger_book == "stoplist_reopen_only" else "-"))
        first_review_clock = str(review_lookup.get(scope, {}).get("first_review_clock", board_lookup.get(scope, {}).get("review_cadence", "-")) or "-")

        secondary_bucket = "-"
        if paper_status == "active_secondary_backstop" and not secondary_df.empty:
            match = secondary_df[
                (secondary_df["secondary_group"].astype(str) == scope)
                & (secondary_df["pocket_scope"].astype(str).str.endswith(f" {interval}"))
            ]
            if not match.empty:
                secondary_bucket = str(match.iloc[0]["recheck_bucket"])

        if paper_status == "active_primary":
            monitor_status = "kickoff_green"
            review_action = "start_primary_paper"
            data_health = "ok_scope_frozen"
            day0_note = "唯一 primary pilot；day-0 先冻结 roster 并落首笔快照，等待首刷后进入真实 weekly review。"
        elif paper_status == "active_secondary_backstop":
            if secondary_bucket == "front-of-queue":
                monitor_status = "kickoff_yellow_front_queue"
                review_action = "start_secondary_then_recheck_front"
                day0_note = "secondary 已开账，但这格属于 front queue；首轮资源应优先补 stricter honesty，若转弱就直接降回 shadow。"
            elif secondary_bucket == "mid-queue":
                monitor_status = "kickoff_yellow_mid_queue"
                review_action = "start_secondary_then_recheck_mid"
                day0_note = "secondary 已开账；当前 buffer 尚可，但仍应在 front queue 之后尽快复核。"
            else:
                monitor_status = "kickoff_green_backstop"
                review_action = "start_secondary_backstop"
                day0_note = "这格属于更厚的 backstop pocket；day-0 先独立开账，后续只在 front / mid queue 稳住后再做更严格复核。"
            data_health = "ok_scope_frozen"
        elif paper_status == "shadow_watch":
            monitor_status = "kickoff_yellow_shadow"
            review_action = "stay_shadow_until_promotion_gate"
            data_health = "ok_scope_frozen"
            day0_note = "这格只记 shadow，不申请 day-0 升格；只有 promotion gate 补齐后才允许单独申请进入 active。"
        else:
            monitor_status = "stopped"
            review_action = "keep_excluded"
            data_health = "n_a_stoplist"
            day0_note = "stoplist / reopen-only 审计位：day-0 只保留占位快照，不启动前瞻刷新，也不允许误混回 baseline。"

        rows.append(
            {
                "snapshot_rank": int(row.get("seed_rank", len(rows) + 1)),
                "snapshot_clock_utc": snapshot_clock_utc,
                "deployment_scope": scope,
                "paper_status": paper_status,
                "ledger_book": ledger_book,
                "market_freq_book": market_freq_book,
                "signal_state": str(row.get("signal_state", "-") or "-"),
                "position_state": str(row.get("position_state", "-") or "-"),
                "monitor_status": monitor_status,
                "review_action": review_action,
                "data_health": data_health,
                "first_review_clock": first_review_clock,
                "day0_note": day0_note,
            }
        )

    return pd.DataFrame(rows, columns=cols)


def build_ema_paper_trading_first_refresh_queue(
    day0_snapshot_df: pd.DataFrame,
    first_week_review_df: pd.DataFrame,
    secondary_recheck_df: pd.DataFrame,
) -> pd.DataFrame:
    cols = [
        "queue_rank",
        "queue_bucket",
        "deployment_scope",
        "market_freq_book",
        "first_refresh_trigger",
        "immediate_action",
        "week1_focus",
        "if_ok_then",
        "if_fail_then",
        "why_now",
    ]
    if day0_snapshot_df.empty:
        return pd.DataFrame(columns=cols)

    review_lookup = first_week_review_df.set_index("deployment_scope").to_dict("index") if not first_week_review_df.empty else {}
    secondary_df = secondary_recheck_df.copy() if not secondary_recheck_df.empty else pd.DataFrame()
    rows: list[dict[str, str | int]] = []

    for _, row in day0_snapshot_df.sort_values(["snapshot_rank", "market_freq_book"]).iterrows():
        scope = str(row.get("deployment_scope", "-") or "-")
        market_freq_book = str(row.get("market_freq_book", "-") or "-")
        interval = market_freq_book.split("-", 1)[-1] if "-" in market_freq_book else market_freq_book
        paper_status = str(row.get("paper_status", "-") or "-")
        monitor_status = str(row.get("monitor_status", "-") or "-")
        trigger = str(row.get("first_review_clock", "-") or "-")
        day0_note = str(row.get("day0_note", "-") or "-")

        queue_bucket = "stoplist_audit_only"
        bucket_rank = 90
        immediate_action = "不做常规 refresh；继续保留 reopen-only 审计位。"
        week1_focus = "确认 stoplist 没被误混回 baseline / shadow 账本。"
        if_ok_then = "继续 keep_excluded。"
        if_fail_then = "若被误混回 baseline，立即 rollback_to_stoplist_now。"

        if paper_status == "active_primary":
            queue_bucket = "p0_primary_first_refresh"
            bucket_rank = 10
            immediate_action = "首个 A 股日线收盘后先补首刷，把 `signal_state / position_state / data_health` 沿同一张账本写下去。"
            week1_focus = "守住 strict-holdout survivor 身份；primary 账本继续单独看，不和 secondary 合并。"
            if_ok_then = "继续 keep_primary，并进入首个 weekly review。"
            if_fail_then = "若首刷后连续转 red / 更像 mixed-watch，就 demote_to_shadow。"
        elif paper_status == "active_secondary_backstop":
            pocket_fail = "若转弱就把该 pocket 从 active_secondary_backstop 降回 shadow。"
            if not secondary_df.empty:
                match = secondary_df[
                    (secondary_df["secondary_group"].astype(str) == scope)
                    & (secondary_df["pocket_scope"].astype(str).str.endswith(f" {interval}"))
                ]
                if not match.empty:
                    pocket_fail = str(match.iloc[0].get("if_fail_then_action", pocket_fail) or pocket_fail)

            if monitor_status == "kickoff_yellow_front_queue":
                queue_bucket = "p1_secondary_front_queue"
                bucket_rank = 20 if interval == "1d" else 60
                immediate_action = "首个收盘后先补首刷，并把这格排进第一轮 stricter honesty front queue。"
                week1_focus = "先查最薄 buffer 的 active secondary pocket，避免整批结果遮盖弱 pocket。"
            elif monitor_status == "kickoff_yellow_mid_queue":
                queue_bucket = "p2_secondary_mid_queue"
                bucket_rank = 40 if interval == "1d" else 70
                immediate_action = "先完成首刷；front queue 稳住后，再把这格排进第二轮 stricter honesty。"
                week1_focus = "继续按 market × freq 分账，别让 mid queue 提前抢走 front queue 资源。"
            else:
                queue_bucket = "p3_secondary_backstop_watch"
                bucket_rank = 50 if interval == "1d" else 80
                immediate_action = "先独立开账并完成首刷；暂不抢第一轮 stricter honesty 资源。"
                week1_focus = "先确认厚 backstop 账本能稳定独立维护，再考虑更严格复核。"

            if_ok_then = "账本首刷正常则继续 keep_secondary_backstop。"
            if_fail_then = pocket_fail
        elif paper_status == "shadow_watch":
            queue_bucket = "p1_shadow_refresh_only"
            bucket_rank = 30
            immediate_action = "只更新 shadow 账本，不申请升格；首刷重点是继续把 `stay_shadow` 写实。"
            week1_focus = "promotion gate 还没过线；recent-forward 转正也不等于能进入 active。"
            if_ok_then = "继续 keep_shadow_until_promotion_gate。"
            if_fail_then = "若 recent-forward 再翻负或账本维护失真，就 keep_or_drop_shadow，但不准偷渡升格。"

        review_row = review_lookup.get(scope, {})
        if review_row:
            review_focus = str(review_row.get("why_it_matters", "") or "")
            if review_focus and week1_focus == "确认 stoplist 没被误混回 baseline / shadow 账本。":
                week1_focus = review_focus

        rows.append(
            {
                "queue_rank": int(bucket_rank + len(rows) + 1),
                "queue_bucket": queue_bucket,
                "deployment_scope": scope,
                "market_freq_book": market_freq_book,
                "first_refresh_trigger": trigger,
                "immediate_action": immediate_action,
                "week1_focus": week1_focus,
                "if_ok_then": if_ok_then,
                "if_fail_then": if_fail_then,
                "why_now": day0_note,
            }
        )

    out = pd.DataFrame(rows, columns=cols)
    if out.empty:
        return out
    return out.sort_values(["queue_rank", "deployment_scope", "market_freq_book"]).reset_index(drop=True)


def build_ema_non60m_honesty_queue(cost_combo_df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "priority_rank",
        "asset",
        "asset_class",
        "interval",
        "profit_pct",
        "trades",
        "max_dd_pct",
        "breakeven_roundtrip_cost_bps",
        "approx_net_profit_pct_20bps",
        "approx_net_profit_pct_50bps",
    ]
    if cost_combo_df.empty:
        return pd.DataFrame(columns=cols)

    sub = cost_combo_df[
        (cost_combo_df["strategy"] == "EMA")
        & (cost_combo_df["interval"].astype(str) != "60m")
    ].copy()
    if sub.empty:
        return pd.DataFrame(columns=cols)

    sub = sub.sort_values(
        ["breakeven_roundtrip_cost_bps", "nt", "profit_pct"],
        ascending=[True, False, False],
    ).reset_index(drop=True)
    sub["priority_rank"] = np.arange(1, len(sub) + 1)
    sub = sub.rename(columns={"nt": "trades"})
    return sub[cols]


def build_ema_non60m_frontier_head_to_head(cost_combo_df: pd.DataFrame, queue_df: pd.DataFrame, *, top_n: int = 6) -> pd.DataFrame:
    cols = [
        "priority_rank",
        "asset",
        "asset_class",
        "interval",
        "ema_trades",
        "ema_breakeven_roundtrip_cost_bps",
        "psar_trades",
        "psar_breakeven_roundtrip_cost_bps",
        "ema_minus_psar_profit_pp",
        "ema_minus_psar_breakeven_bps",
        "reading",
    ]
    if cost_combo_df.empty or queue_df.empty:
        return pd.DataFrame(columns=cols)

    frontier = queue_df.head(top_n)[["priority_rank", "asset", "asset_class", "interval"]].copy()
    ema_sub = cost_combo_df[cost_combo_df["strategy"] == "EMA"][
        ["asset", "interval", "profit_pct", "nt", "breakeven_roundtrip_cost_bps"]
    ].copy()
    psar_sub = cost_combo_df[cost_combo_df["strategy"] == "PSAR"][
        ["asset", "interval", "profit_pct", "nt", "breakeven_roundtrip_cost_bps"]
    ].copy()

    merged = frontier.merge(ema_sub, on=["asset", "interval"], how="left").merge(
        psar_sub,
        on=["asset", "interval"],
        how="left",
        suffixes=("_ema", "_psar"),
    )
    if merged.empty:
        return pd.DataFrame(columns=cols)

    merged = merged.rename(
        columns={
            "nt_ema": "ema_trades",
            "nt_psar": "psar_trades",
            "breakeven_roundtrip_cost_bps_ema": "ema_breakeven_roundtrip_cost_bps",
            "breakeven_roundtrip_cost_bps_psar": "psar_breakeven_roundtrip_cost_bps",
        }
    )
    merged["ema_minus_psar_profit_pp"] = merged["profit_pct_ema"] - merged["profit_pct_psar"]
    merged["ema_minus_psar_breakeven_bps"] = merged["ema_breakeven_roundtrip_cost_bps"] - merged["psar_breakeven_roundtrip_cost_bps"]

    def label_row(row: pd.Series) -> str:
        profit_delta = float(row["ema_minus_psar_profit_pp"])
        buffer_delta = float(row["ema_minus_psar_breakeven_bps"])
        if profit_delta > 0 and buffer_delta > 0:
            return "EMA 更像主 baseline"
        if profit_delta < 0 and buffer_delta < 0:
            return "PSAR 在这口袋更强"
        return "mixed：EMA 少交易 / PSAR 边际更像样"

    merged["reading"] = merged.apply(label_row, axis=1)
    return merged[cols]


def build_ema_secondary_backstop_recheck_queue(
    honesty_queue_df: pd.DataFrame,
    candidate_spec_df: pd.DataFrame,
    operating_spec_df: pd.DataFrame,
) -> pd.DataFrame:
    cols = [
        "recheck_rank",
        "global_honesty_rank",
        "secondary_group",
        "pocket_scope",
        "asset_class",
        "profit_pct",
        "trades",
        "breakeven_roundtrip_cost_bps",
        "approx_net_profit_pct_20bps",
        "recheck_bucket",
        "why_recheck_now",
        "if_fail_then_action",
    ]
    if honesty_queue_df.empty or candidate_spec_df.empty or operating_spec_df.empty:
        return pd.DataFrame(columns=cols)

    active_secondary = candidate_spec_df[candidate_spec_df["admission_bucket"] == "paper_now_secondary"]["deployment_scope"].astype(str).tolist()
    if not active_secondary:
        return pd.DataFrame(columns=cols)

    group_map = {
        "美股 1d+1wk（SPY/QQQ/AAPL）": {"assets": {"SPY", "QQQ", "AAPL"}},
        "Crypto 1d+1wk（BTC/ETH/SOL）": {"assets": {"BTC", "ETH", "SOL"}},
        "贵州茅台 1d+1wk": {"assets": {"贵州茅台"}},
    }
    op_lookup = operating_spec_df.set_index("deployment_scope").to_dict("index")

    rows: list[dict] = []
    for group in active_secondary:
        meta = group_map.get(group)
        if not meta:
            continue
        sub = honesty_queue_df[
            honesty_queue_df["asset"].astype(str).isin(meta["assets"])
            & honesty_queue_df["interval"].astype(str).isin(["1d", "1wk"])
        ].copy()
        if sub.empty:
            continue
        for _, row in sub.sort_values("priority_rank").iterrows():
            bps = float(row["breakeven_roundtrip_cost_bps"])
            interval = str(row["interval"])
            pocket_scope = f"{row['asset']} {interval}"
            if bps < 500:
                bucket = "front-of-queue"
                why = "这是当前 active_secondary_backstop 里最薄的一层，若要先做 stricter honesty，默认应先查这格。"
            elif bps < 2500:
                bucket = "mid-queue"
                why = "这格仍明显为正，但 buffer 已不算特别厚；适合在 front queue 之后做第二批复核。"
            else:
                bucket = "back-of-queue"
                why = "这格当前更像远端厚 backstop，除非前排口袋先出问题，否则不抢第一轮复核资源。"
            if interval == "1d" and bucket != "back-of-queue":
                why = f"{why.rstrip('。')}；而且它还是日频口袋，更接近日常 paper 运行节奏。"

            rows.append(
                {
                    "recheck_rank": 0,
                    "global_honesty_rank": int(row["priority_rank"]),
                    "secondary_group": group,
                    "pocket_scope": pocket_scope,
                    "asset_class": str(row["asset_class"]),
                    "profit_pct": float(row["profit_pct"]),
                    "trades": float(row["trades"]),
                    "breakeven_roundtrip_cost_bps": bps,
                    "approx_net_profit_pct_20bps": float(row["approx_net_profit_pct_20bps"]),
                    "recheck_bucket": bucket,
                    "why_recheck_now": why,
                    "if_fail_then_action": str(op_lookup.get(group, {}).get("promotion_or_demotion_rule", "若更严格 honesty 转弱，就把该 pocket 从 secondary 降回 shadow。")),
                }
            )

    out = pd.DataFrame(rows, columns=cols)
    if out.empty:
        return out
    out = out.sort_values(["global_honesty_rank", "breakeven_roundtrip_cost_bps", "pocket_scope"]).reset_index(drop=True)
    out["recheck_rank"] = np.arange(1, len(out) + 1)
    return out[cols]


def ema_roll(s: pd.Series, span: int) -> pd.Series:
    return s.ewm(span=span, adjust=False).mean()


def psar(high: pd.Series, low: pd.Series, step: float = 0.02, max_step: float = 0.2) -> pd.Series:
    n = len(high)
    out = np.full(n, np.nan, dtype=float)
    if n < 2:
        return pd.Series(out, index=high.index)

    trend_up = True
    af = step
    ep = float(high.iloc[0])
    sar = float(low.iloc[0])
    out[0] = sar

    for i in range(1, n):
        prev_sar = sar
        sar = prev_sar + af * (ep - prev_sar)

        if trend_up:
            sar = min(sar, float(low.iloc[i - 1]))
            if i >= 2:
                sar = min(sar, float(low.iloc[i - 2]))
            if float(low.iloc[i]) < sar:
                trend_up = False
                sar = ep
                ep = float(low.iloc[i])
                af = step
            else:
                if float(high.iloc[i]) > ep:
                    ep = float(high.iloc[i])
                    af = min(af + step, max_step)
        else:
            sar = max(sar, float(high.iloc[i - 1]))
            if i >= 2:
                sar = max(sar, float(high.iloc[i - 2]))
            if float(high.iloc[i]) > sar:
                trend_up = True
                sar = ep
                ep = float(high.iloc[i])
                af = step
            else:
                if float(low.iloc[i]) < ep:
                    ep = float(low.iloc[i])
                    af = min(af + step, max_step)

        out[i] = sar

    return pd.Series(out, index=high.index)


def build_ema_only_feature_frame(bars: pd.DataFrame) -> pd.DataFrame:
    df = bars.copy()
    df["ema9"] = ema_roll(df["close"], 9)
    df["ema20"] = ema_roll(df["close"], 20)
    df["psar"] = psar(df["high"], df["low"], step=0.02, max_step=0.2)
    df["prev_high"] = df["high"].shift(1)
    df["prev_low"] = df["low"].shift(1)
    return df


def run_ema_long_only_window(df: pd.DataFrame, *, cost_bps: int = EMA60M_ROLLING_COST_BPS) -> dict[str, float]:
    cash = 1.0
    qty = 0.0
    in_pos = False
    entry_price = np.nan
    trade_rets: list[float] = []

    for _, row in df.iterrows():
        px = float(row["close"])
        sig = "BUY" if row["ema9"] > row["ema20"] else ("SELL" if row["ema9"] < row["ema20"] else "HOLD")
        if sig == "BUY" and (not in_pos) and px > 0:
            qty = cash / px
            cash = 0.0
            in_pos = True
            entry_price = px
        elif sig == "SELL" and in_pos and px > 0:
            cash = qty * px
            trade_rets.append(px / entry_price - 1.0)
            qty = 0.0
            in_pos = False
            entry_price = np.nan

    if in_pos and qty > 0:
        final_px = float(df.iloc[-1]["close"])
        cash = qty * final_px
        trade_rets.append(final_px / entry_price - 1.0)

    gross_return = cash - 1.0
    if trade_rets:
        net20_return = float(np.prod([1.0 + r - (cost_bps / 10000.0) for r in trade_rets]) - 1.0)
    else:
        net20_return = 0.0

    return {
        "gross_profit_pct": float(gross_return * 100.0),
        "net20_profit_pct": float(net20_return * 100.0),
        "trades": float(len(trade_rets)),
        "gross_positive": float(gross_return > 0),
        "net20_positive": float(net20_return > 0),
    }


def run_psar_long_only_window(df: pd.DataFrame, *, cost_bps: int = EMA60M_ROLLING_COST_BPS) -> dict[str, float]:
    cash = 1.0
    qty = 0.0
    in_pos = False
    entry_price = np.nan
    trade_rets: list[float] = []

    for _, row in df.iterrows():
        px = float(row["close"])
        buy_sig = (not pd.isna(row["prev_high"])) and (not pd.isna(row["psar"])) and (row["psar"] <= row["close"]) and (row["high"] > row["prev_high"])
        sell_sig = (not pd.isna(row["prev_low"])) and (not pd.isna(row["psar"])) and (row["psar"] > row["close"]) and (row["low"] < row["prev_low"])
        if buy_sig and (not in_pos) and px > 0:
            qty = cash / px
            cash = 0.0
            in_pos = True
            entry_price = px
        elif sell_sig and in_pos and px > 0:
            cash = qty * px
            trade_rets.append(px / entry_price - 1.0)
            qty = 0.0
            in_pos = False
            entry_price = np.nan

    if in_pos and qty > 0:
        final_px = float(df.iloc[-1]["close"])
        cash = qty * final_px
        trade_rets.append(final_px / entry_price - 1.0)

    gross_return = cash - 1.0
    if trade_rets:
        net20_return = float(np.prod([1.0 + r - (cost_bps / 10000.0) for r in trade_rets]) - 1.0)
    else:
        net20_return = 0.0

    return {
        "gross_profit_pct": float(gross_return * 100.0),
        "net20_profit_pct": float(net20_return * 100.0),
        "trades": float(len(trade_rets)),
        "gross_positive": float(gross_return > 0),
        "net20_positive": float(net20_return > 0),
    }


def load_cached_or_download_frontier_bars(ticker: str, interval: str) -> pd.DataFrame:
    cache_path = ASHARE_FRONTIER_CACHE_DIR / f"{ticker.replace('-', '_').replace('.', '_')}__10y__{interval}.csv"
    if cache_path.exists():
        return pd.read_csv(cache_path, parse_dates=["timestamp"]).sort_values("timestamp").reset_index(drop=True)

    mod = load_replication_module()
    bars = mod.download_bars(ticker, period="10y", interval=interval)
    bars = bars.sort_values("timestamp").reset_index(drop=True)
    bars.to_csv(cache_path, index=False)
    return bars


def build_ema_non60m_ashare_frontier_rolling_slice() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    window_rows: list[dict] = []
    for cfg in EMA_NON60M_ASHARE_FRONTIER_CONFIG:
        bars = load_cached_or_download_frontier_bars(cfg["ticker"], cfg["interval"])
        if bars.empty:
            continue
        feat = build_ema_only_feature_frame(bars)
        start = feat["timestamp"].min().floor("D")
        end = feat["timestamp"].max().ceil("D")
        cur = start
        win_id = 0
        while cur + pd.Timedelta(days=EMA_NON60M_ASHARE_WINDOW_DAYS) <= end:
            win_end = cur + pd.Timedelta(days=EMA_NON60M_ASHARE_WINDOW_DAYS)
            sub = feat[(feat["timestamp"] >= cur) & (feat["timestamp"] < win_end)].copy()
            if len(sub) < EMA_NON60M_ASHARE_MIN_BARS[cfg["interval"]]:
                cur += pd.Timedelta(days=EMA_NON60M_ASHARE_STEP_DAYS)
                win_id += 1
                continue
            ema_metrics = run_ema_long_only_window(sub, cost_bps=EMA_NON60M_ASHARE_COST_BPS)
            psar_metrics = run_psar_long_only_window(sub, cost_bps=EMA_NON60M_ASHARE_COST_BPS)
            window_rows.append(
                {
                    "asset": cfg["asset"],
                    "ticker": cfg["ticker"],
                    "asset_class": cfg["asset_class"],
                    "interval": cfg["interval"],
                    "window_id": int(win_id),
                    "window_start": cur,
                    "window_end": win_end,
                    "bars": int(len(sub)),
                    "ema_net20_profit_pct": ema_metrics["net20_profit_pct"],
                    "ema_trades": ema_metrics["trades"],
                    "ema_net20_positive": ema_metrics["net20_positive"],
                    "psar_net20_profit_pct": psar_metrics["net20_profit_pct"],
                    "psar_trades": psar_metrics["trades"],
                    "psar_net20_positive": psar_metrics["net20_positive"],
                    "ema_minus_psar_net20_pp": float(ema_metrics["net20_profit_pct"] - psar_metrics["net20_profit_pct"]),
                    "ema_beats_psar_net20": float(ema_metrics["net20_profit_pct"] > psar_metrics["net20_profit_pct"]),
                }
            )
            cur += pd.Timedelta(days=EMA_NON60M_ASHARE_STEP_DAYS)
            win_id += 1

    window_df = pd.DataFrame(window_rows)
    if window_df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    pocket_rows: list[dict] = []
    for (asset, ticker, asset_class, interval), g in window_df.sort_values("window_start").groupby(["asset", "ticker", "asset_class", "interval"], sort=False):
        ema_pos_share = float(g["ema_net20_positive"].mean())
        psar_pos_share = float(g["psar_net20_positive"].mean())
        delta_med = float(g["ema_minus_psar_net20_pp"].median())
        if ema_pos_share > psar_pos_share and delta_med > 0:
            reading = "EMA 仍更像 baseline"
        elif ema_pos_share < psar_pos_share and delta_med < 0:
            reading = "PSAR 在这口袋更稳"
        else:
            reading = "mixed：要继续收窄到 pocket 级"
        pocket_rows.append(
            {
                "asset": asset,
                "ticker": ticker,
                "asset_class": asset_class,
                "interval": interval,
                "windows": int(len(g)),
                "ema_net20_positive_window_share": ema_pos_share,
                "psar_net20_positive_window_share": psar_pos_share,
                "ema_net20_median_profit_pct": float(g["ema_net20_profit_pct"].median()),
                "psar_net20_median_profit_pct": float(g["psar_net20_profit_pct"].median()),
                "ema_median_trades": float(g["ema_trades"].median()),
                "psar_median_trades": float(g["psar_trades"].median()),
                "ema_vs_psar_median_net20_delta_pp": delta_med,
                "ema_better_window_share": float(g["ema_beats_psar_net20"].mean()),
                "reading": reading,
            }
        )
    pocket_df = pd.DataFrame(pocket_rows)

    ema_majority_pockets = int((pocket_df["ema_net20_positive_window_share"] > 0.5).sum()) if not pocket_df.empty else 0
    psar_majority_pockets = int((pocket_df["psar_net20_positive_window_share"] > 0.5).sum()) if not pocket_df.empty else 0
    overall_df = pd.DataFrame(
        [
            {
                "pockets": int(len(pocket_df)),
                "windows": int(len(window_df)),
                "ema_net20_positive_window_share": float(window_df["ema_net20_positive"].mean()),
                "psar_net20_positive_window_share": float(window_df["psar_net20_positive"].mean()),
                "ema_better_window_share": float(window_df["ema_beats_psar_net20"].mean()),
                "ema_majority_positive_pockets": ema_majority_pockets,
                "psar_majority_positive_pockets": psar_majority_pockets,
                "verdict": "mixed" if ema_majority_pockets >= 2 and float(window_df["ema_beats_psar_net20"].mean()) >= 0.5 else ("pass" if ema_majority_pockets >= 3 else "fail"),
            }
        ]
    )

    window_df.to_csv(ART_DIR / "ema_non60m_ashare_frontier_rolling_window_metrics.csv", index=False)
    pocket_df.to_csv(ART_DIR / "ema_non60m_ashare_frontier_rolling_pocket_summary.csv", index=False)
    overall_df.to_csv(ART_DIR / "ema_non60m_ashare_frontier_rolling_overall_summary.csv", index=False)
    return window_df, pocket_df, overall_df


def build_ema_non60m_ashare_daily_holdout_slice() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    holdout_rows: list[dict] = []
    daily_cfgs = [cfg for cfg in EMA_NON60M_ASHARE_FRONTIER_CONFIG if cfg["interval"] == "1d"]
    for cfg in daily_cfgs:
        bars = load_cached_or_download_frontier_bars(cfg["ticker"], cfg["interval"])
        if bars.empty:
            continue
        feat = build_ema_only_feature_frame(bars)
        start = feat["timestamp"].min().floor("D")
        end = feat["timestamp"].max().ceil("D")
        cur = start
        holdout_id = 0
        while cur + pd.Timedelta(days=EMA_NON60M_ASHARE_DAILY_HOLDOUT_TRAIN_DAYS + EMA_NON60M_ASHARE_DAILY_HOLDOUT_DAYS) <= end:
            train_end = cur + pd.Timedelta(days=EMA_NON60M_ASHARE_DAILY_HOLDOUT_TRAIN_DAYS)
            holdout_end = train_end + pd.Timedelta(days=EMA_NON60M_ASHARE_DAILY_HOLDOUT_DAYS)
            sub = feat[(feat["timestamp"] >= train_end) & (feat["timestamp"] < holdout_end)].copy()
            if len(sub) < max(120, EMA_NON60M_ASHARE_MIN_BARS[cfg["interval"]] // 2):
                cur += pd.Timedelta(days=EMA_NON60M_ASHARE_DAILY_HOLDOUT_STEP_DAYS)
                holdout_id += 1
                continue
            ema_metrics = run_ema_long_only_window(sub, cost_bps=EMA_NON60M_ASHARE_COST_BPS)
            psar_metrics = run_psar_long_only_window(sub, cost_bps=EMA_NON60M_ASHARE_COST_BPS)
            holdout_rows.append(
                {
                    "asset": cfg["asset"],
                    "ticker": cfg["ticker"],
                    "asset_class": cfg["asset_class"],
                    "interval": cfg["interval"],
                    "holdout_id": int(holdout_id),
                    "train_start": cur,
                    "train_end": train_end,
                    "holdout_start": train_end,
                    "holdout_end": holdout_end,
                    "bars": int(len(sub)),
                    "ema_net20_profit_pct": ema_metrics["net20_profit_pct"],
                    "ema_trades": ema_metrics["trades"],
                    "ema_net20_positive": ema_metrics["net20_positive"],
                    "psar_net20_profit_pct": psar_metrics["net20_profit_pct"],
                    "psar_trades": psar_metrics["trades"],
                    "psar_net20_positive": psar_metrics["net20_positive"],
                    "ema_minus_psar_net20_pp": float(ema_metrics["net20_profit_pct"] - psar_metrics["net20_profit_pct"]),
                    "ema_beats_psar_net20": float(ema_metrics["net20_profit_pct"] > psar_metrics["net20_profit_pct"]),
                }
            )
            cur += pd.Timedelta(days=EMA_NON60M_ASHARE_DAILY_HOLDOUT_STEP_DAYS)
            holdout_id += 1

    holdout_df = pd.DataFrame(holdout_rows)
    if holdout_df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    pocket_rows: list[dict] = []
    for (asset, ticker, asset_class, interval), g in holdout_df.sort_values("holdout_start").groupby(["asset", "ticker", "asset_class", "interval"], sort=False):
        ema_pos_share = float(g["ema_net20_positive"].mean())
        psar_pos_share = float(g["psar_net20_positive"].mean())
        delta_med = float(g["ema_minus_psar_net20_pp"].median())
        if ema_pos_share >= 0.6 and delta_med > 0:
            reading = "EMA 仍可保留"
        elif psar_pos_share >= 0.6 and delta_med < 0:
            reading = "PSAR 更稳，EMA 只宜保留观察"
        else:
            reading = "mixed：仍需更广 holdout 才能定性"
        pocket_rows.append(
            {
                "asset": asset,
                "ticker": ticker,
                "asset_class": asset_class,
                "interval": interval,
                "holdouts": int(len(g)),
                "ema_net20_positive_holdout_share": ema_pos_share,
                "psar_net20_positive_holdout_share": psar_pos_share,
                "ema_net20_median_profit_pct": float(g["ema_net20_profit_pct"].median()),
                "psar_net20_median_profit_pct": float(g["psar_net20_profit_pct"].median()),
                "ema_median_trades": float(g["ema_trades"].median()),
                "psar_median_trades": float(g["psar_trades"].median()),
                "ema_vs_psar_median_net20_delta_pp": delta_med,
                "ema_better_holdout_share": float(g["ema_beats_psar_net20"].mean()),
                "reading": reading,
            }
        )
    pocket_df = pd.DataFrame(pocket_rows)

    overall_df = pd.DataFrame(
        [
            {
                "pockets": int(len(pocket_df)),
                "holdouts": int(len(holdout_df)),
                "ema_net20_positive_holdout_share": float(holdout_df["ema_net20_positive"].mean()),
                "psar_net20_positive_holdout_share": float(holdout_df["psar_net20_positive"].mean()),
                "ema_better_holdout_share": float(holdout_df["ema_beats_psar_net20"].mean()),
                "ema_majority_positive_pockets": int((pocket_df["ema_net20_positive_holdout_share"] >= 0.5).sum()) if not pocket_df.empty else 0,
                "psar_majority_positive_pockets": int((pocket_df["psar_net20_positive_holdout_share"] >= 0.5).sum()) if not pocket_df.empty else 0,
                "verdict": "EMA-lean" if float(holdout_df["ema_net20_positive"].mean()) >= 0.6 and float(holdout_df["ema_beats_psar_net20"].mean()) >= 0.6 else "mixed",
            }
        ]
    )

    holdout_df.to_csv(ART_DIR / "ema_non60m_ashare_daily_holdout_window_metrics.csv", index=False)
    pocket_df.to_csv(ART_DIR / "ema_non60m_ashare_daily_holdout_pocket_summary.csv", index=False)
    overall_df.to_csv(ART_DIR / "ema_non60m_ashare_daily_holdout_overall_summary.csv", index=False)
    return holdout_df, pocket_df, overall_df


def build_ema_ashare_daily_shadow_promotion_scorecard(holdout_df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "asset",
        "current_role",
        "holdouts",
        "overall_ema_positive_holdout_share",
        "overall_ema_beats_psar_share",
        "recent3_ema_positive_holdout_share",
        "recent3_ema_median_net20_profit_pct",
        "latest_holdout_net20_profit_pct",
        "latest_holdout_ema_minus_psar_net20_pp",
        "gate_hits",
        "promotion_verdict",
        "promotion_reading",
    ]
    if holdout_df.empty:
        return pd.DataFrame(columns=cols)

    rows: list[dict] = []
    for asset, g in holdout_df.sort_values("holdout_start").groupby("asset", sort=False):
        g = g.sort_values("holdout_start").reset_index(drop=True)
        recent = g.tail(3).copy()
        latest = g.iloc[-1]
        overall_pos_share = float(g["ema_net20_positive"].mean())
        overall_beats_share = float(g["ema_beats_psar_net20"].mean())
        recent3_pos_share = float(recent["ema_net20_positive"].mean())
        recent3_median_net20 = float(recent["ema_net20_profit_pct"].median())
        latest_profit = float(latest["ema_net20_profit_pct"])
        latest_delta = float(latest["ema_minus_psar_net20_pp"])
        gate_hits = int(
            (overall_pos_share >= 0.625)
            + (overall_beats_share >= 0.625)
            + (recent3_pos_share >= (2.0 / 3.0))
            + (latest_profit > 0)
            + (latest_delta > 0)
        )
        current_role = "primary pilot" if asset == "创业板ETF" else "shadow watch"
        if current_role == "primary pilot":
            promotion_verdict = "keep_primary" if gate_hits >= 5 else ("primary_under_watch" if gate_hits >= 4 else "demote_to_shadow")
        else:
            promotion_verdict = "promotable_shadow" if gate_hits >= 4 else ("stay_shadow_not_promote" if gate_hits >= 3 else "demote_or_exclude")

        if promotion_verdict == "keep_primary":
            promotion_reading = "仍可继续当 primary：overall 与当前 holdout 都够厚。"
        elif promotion_verdict == "primary_under_watch":
            promotion_reading = "仍保留 primary，但 recent/overall 边界已变薄。"
        elif promotion_verdict == "promotable_shadow":
            promotion_reading = "已接近 shadow 升格线，可继续做更严格前瞻复核。"
        elif promotion_verdict == "stay_shadow_not_promote":
            promotion_reading = "recent 有改善，但 overall 还不够厚，先继续 shadow。"
        else:
            promotion_reading = "当前不宜继续留在 paper scope。"

        rows.append(
            {
                "asset": asset,
                "current_role": current_role,
                "holdouts": int(len(g)),
                "overall_ema_positive_holdout_share": overall_pos_share,
                "overall_ema_beats_psar_share": overall_beats_share,
                "recent3_ema_positive_holdout_share": recent3_pos_share,
                "recent3_ema_median_net20_profit_pct": recent3_median_net20,
                "latest_holdout_net20_profit_pct": latest_profit,
                "latest_holdout_ema_minus_psar_net20_pp": latest_delta,
                "gate_hits": gate_hits,
                "promotion_verdict": promotion_verdict,
                "promotion_reading": promotion_reading,
            }
        )

    return pd.DataFrame(rows, columns=cols)


def build_ema_ashare_daily_recent_forward_audit(holdout_df: pd.DataFrame, *, tail_holdouts: int = 2) -> pd.DataFrame:
    cols = [
        "asset",
        "current_role",
        "tail_holdouts",
        "forward_start",
        "forward_end",
        "ema_tail_cum_net20_profit_pct",
        "psar_tail_cum_net20_profit_pct",
        "tail_ema_minus_psar_cum_pp",
        "tail_ema_positive_holdout_share",
        "tail_ema_beats_psar_share",
        "tail_worst_ema_holdout_pct",
        "forward_honesty_verdict",
        "forward_honesty_reading",
    ]
    if holdout_df.empty:
        return pd.DataFrame(columns=cols)

    rows: list[dict] = []
    for asset, g in holdout_df.sort_values("holdout_start").groupby("asset", sort=False):
        g = g.sort_values("holdout_start").tail(tail_holdouts).reset_index(drop=True)
        if g.empty:
            continue
        ema_tail_cum = float((1.0 + g["ema_net20_profit_pct"] / 100.0).prod() - 1.0) * 100.0
        psar_tail_cum = float((1.0 + g["psar_net20_profit_pct"] / 100.0).prod() - 1.0) * 100.0
        tail_delta = ema_tail_cum - psar_tail_cum
        tail_pos_share = float(g["ema_net20_positive"].mean())
        tail_beats_share = float(g["ema_beats_psar_net20"].mean())
        tail_worst = float(g["ema_net20_profit_pct"].min())
        current_role = "primary pilot" if asset == "创业板ETF" else "shadow watch"

        if current_role == "primary pilot":
            if tail_pos_share >= 1.0 and ema_tail_cum > 0:
                verdict = "keep_primary_recent_forward_ok"
                reading = "最近 forward tail 仍连续为正，primary 口径继续成立。"
            else:
                verdict = "primary_recent_forward_under_watch"
                reading = "recent forward tail 已转薄，primary 需继续严盯。"
        else:
            if tail_pos_share >= 1.0 and tail_beats_share >= 1.0 and tail_delta > 0:
                verdict = "promote_candidate"
                reading = "recent forward tail 连续为正且持续跑赢 PSAR，可进入下一道 promotion 复核。"
            elif tail_pos_share >= 1.0 and ema_tail_cum > 0:
                verdict = "positive_but_not_promotable"
                reading = "recent forward tail 虽为正，但仍没形成足够升格诚实度，继续留在 shadow。"
            else:
                verdict = "not_ready_for_promotion"
                reading = "recent forward tail 仍不稳，不宜 promotion。"

        rows.append(
            {
                "asset": asset,
                "current_role": current_role,
                "tail_holdouts": int(len(g)),
                "forward_start": str(pd.to_datetime(g["holdout_start"].iloc[0], utc=True).date()),
                "forward_end": str(pd.to_datetime(g["holdout_end"].iloc[-1], utc=True).date()),
                "ema_tail_cum_net20_profit_pct": ema_tail_cum,
                "psar_tail_cum_net20_profit_pct": psar_tail_cum,
                "tail_ema_minus_psar_cum_pp": tail_delta,
                "tail_ema_positive_holdout_share": tail_pos_share,
                "tail_ema_beats_psar_share": tail_beats_share,
                "tail_worst_ema_holdout_pct": tail_worst,
                "forward_honesty_verdict": verdict,
                "forward_honesty_reading": reading,
            }
        )

    return pd.DataFrame(rows, columns=cols)


def build_ema_ashare_daily_psar_overlay_audit() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    window_rows: list[dict] = []
    daily_cfgs = [cfg for cfg in EMA_NON60M_ASHARE_FRONTIER_CONFIG if cfg["interval"] == "1d"]
    for cfg in daily_cfgs:
        bars = load_cached_or_download_frontier_bars(cfg["ticker"], cfg["interval"])
        if bars.empty:
            continue
        feat = build_ema_only_feature_frame(bars)
        start = feat["timestamp"].min().floor("D")
        end = feat["timestamp"].max().ceil("D")
        cur = start
        holdout_id = 0
        while cur + pd.Timedelta(days=EMA_NON60M_ASHARE_DAILY_HOLDOUT_TRAIN_DAYS + EMA_NON60M_ASHARE_DAILY_HOLDOUT_DAYS) <= end:
            train_end = cur + pd.Timedelta(days=EMA_NON60M_ASHARE_DAILY_HOLDOUT_TRAIN_DAYS)
            holdout_end = train_end + pd.Timedelta(days=EMA_NON60M_ASHARE_DAILY_HOLDOUT_DAYS)
            sub = feat[(feat["timestamp"] >= train_end) & (feat["timestamp"] < holdout_end)].copy()
            if len(sub) < max(120, EMA_NON60M_ASHARE_MIN_BARS[cfg["interval"]] // 2):
                cur += pd.Timedelta(days=EMA_NON60M_ASHARE_DAILY_HOLDOUT_STEP_DAYS)
                holdout_id += 1
                continue
            ema_metrics = run_ema_long_only_window(sub, cost_bps=EMA_NON60M_ASHARE_COST_BPS)
            overlay_metrics = run_ema_psar_exit_overlay_window(sub, cost_bps=EMA_NON60M_ASHARE_COST_BPS)
            current_role = "primary pilot" if cfg["asset"] == "创业板ETF" else "shadow watch"
            window_rows.append(
                {
                    "asset": cfg["asset"],
                    "ticker": cfg["ticker"],
                    "asset_class": cfg["asset_class"],
                    "interval": cfg["interval"],
                    "current_role": current_role,
                    "holdout_id": int(holdout_id),
                    "holdout_start": train_end,
                    "holdout_end": holdout_end,
                    "bars": int(len(sub)),
                    "ema_net20_profit_pct": ema_metrics["net20_profit_pct"],
                    "ema_trades": ema_metrics["trades"],
                    "overlay_net20_profit_pct": overlay_metrics["net20_profit_pct"],
                    "overlay_trades": overlay_metrics["trades"],
                    "net20_delta_pp": float(overlay_metrics["net20_profit_pct"] - ema_metrics["net20_profit_pct"]),
                    "trade_delta": float(overlay_metrics["trades"] - ema_metrics["trades"]),
                    "overlay_better_net20": float(overlay_metrics["net20_profit_pct"] > ema_metrics["net20_profit_pct"]),
                }
            )
            cur += pd.Timedelta(days=EMA_NON60M_ASHARE_DAILY_HOLDOUT_STEP_DAYS)
            holdout_id += 1

    window_df = pd.DataFrame(window_rows)
    if window_df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    pocket_rows: list[dict] = []
    for asset, g in window_df.sort_values("holdout_start").groupby("asset", sort=False):
        current_role = str(g["current_role"].iloc[0])
        holdouts = int(len(g))
        better_share = float(g["overlay_better_net20"].mean())
        ema_med = float(g["ema_net20_profit_pct"].median())
        overlay_med = float(g["overlay_net20_profit_pct"].median())
        delta_med = float(g["net20_delta_pp"].median())
        delta_best = float(g["net20_delta_pp"].max())
        delta_worst = float(g["net20_delta_pp"].min())
        trade_med = float(g["trade_delta"].median())

        if current_role == "primary pilot":
            if better_share >= 0.6 and delta_med > 0:
                verdict = "candidate_protective_overlay"
                reading = "多数 strict holdout 都改善，PSAR 可继续当 primary 的 shadow protective 候选，但还不该直接改写默认 EMA 持有规则。"
            else:
                verdict = "keep_ema_only_default"
                reading = "primary strict holdout 里 PSAR 快退出没有稳定跑赢单跑 EMA；默认继续 EMA-only runbook，PSAR 只保留 benchmark/shadow 观察位。"
        else:
            if better_share >= 0.6 and delta_med > 0:
                verdict = "shadow_only_overlay_watch"
                reading = "shadow pocket 可继续观察 PSAR 快退出，但仍只配 shadow-only，不等于 promotion clear。"
            else:
                verdict = "not_a_promotion_patch"
                reading = "overlay 还不能当 shadow promotion 的补丁；默认继续单跑 EMA shadow 记账，把 PSAR 留在 benchmark 位。"

        pocket_rows.append(
            {
                "asset": asset,
                "current_role": current_role,
                "holdouts": holdouts,
                "overlay_better_holdout_share": better_share,
                "ema_net20_median_profit_pct": ema_med,
                "overlay_net20_median_profit_pct": overlay_med,
                "median_net20_delta_pp": delta_med,
                "best_net20_delta_pp": delta_best,
                "worst_net20_delta_pp": delta_worst,
                "median_trade_delta": trade_med,
                "overlay_verdict": verdict,
                "deployment_reading": reading,
            }
        )
    pocket_df = pd.DataFrame(pocket_rows)

    primary_row = pocket_df[pocket_df["current_role"] == "primary pilot"]
    primary_verdict = str(primary_row.iloc[0]["overlay_verdict"]) if not primary_row.empty else "-"
    overall_better_share = float(window_df["overlay_better_net20"].mean())
    overall_delta_med = float(window_df["net20_delta_pp"].median())
    if primary_verdict == "candidate_protective_overlay" and overall_better_share >= 0.6 and overall_delta_med > 0:
        overall_verdict = "candidate_primary_shadow_protocol"
        overall_reading = "primary pilot 与整体 holdout 都给出正向增量，PSAR 可进入 primary 的 shadow protective protocol。"
    elif primary_verdict == "candidate_protective_overlay":
        overall_verdict = "mixed_shadow_only_not_default"
        overall_reading = "primary pilot 虽有改善，但跨 A股 daily 合并后仍偏 mixed；PSAR 目前只配 shadow protective 观察位，不应焊进默认 runbook。"
    else:
        overall_verdict = "keep_psar_out_of_default_runbook"
        overall_reading = "当前 primary pilot 没给出足够多数 holdout 改善；PSAR 不应焊进 A股 daily 的默认 EMA runbook。"

    overall_df = pd.DataFrame(
        [
            {
                "assets": int(len(pocket_df)),
                "holdouts": int(len(window_df)),
                "overlay_better_holdout_share": float(window_df["overlay_better_net20"].mean()),
                "median_net20_delta_pp": float(window_df["net20_delta_pp"].median()),
                "median_trade_delta": float(window_df["trade_delta"].median()),
                "overall_verdict": overall_verdict,
                "overall_reading": overall_reading,
            }
        ]
    )

    window_df.to_csv(ART_DIR / "ema_ashare_daily_psar_overlay_holdout_window_metrics.csv", index=False)
    pocket_df.to_csv(ART_DIR / "ema_ashare_daily_psar_overlay_pocket_summary.csv", index=False)
    overall_df.to_csv(ART_DIR / "ema_ashare_daily_psar_overlay_overall_summary.csv", index=False)
    return window_df, pocket_df, overall_df


def build_ema_non60m_ashare_weekly_holdout_slice() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    holdout_rows: list[dict] = []
    weekly_cfgs = [cfg for cfg in EMA_NON60M_ASHARE_FRONTIER_CONFIG if cfg["interval"] == "1wk"]
    for cfg in weekly_cfgs:
        bars = load_cached_or_download_frontier_bars(cfg["ticker"], cfg["interval"])
        if bars.empty:
            continue
        feat = build_ema_only_feature_frame(bars)
        start = feat["timestamp"].min().floor("D")
        end = feat["timestamp"].max().ceil("D")
        cur = start
        holdout_id = 0
        while cur + pd.Timedelta(days=EMA_NON60M_ASHARE_WEEKLY_HOLDOUT_TRAIN_DAYS + EMA_NON60M_ASHARE_WEEKLY_HOLDOUT_DAYS) <= end:
            train_end = cur + pd.Timedelta(days=EMA_NON60M_ASHARE_WEEKLY_HOLDOUT_TRAIN_DAYS)
            holdout_end = train_end + pd.Timedelta(days=EMA_NON60M_ASHARE_WEEKLY_HOLDOUT_DAYS)
            sub = feat[(feat["timestamp"] >= train_end) & (feat["timestamp"] < holdout_end)].copy()
            if len(sub) < max(26, EMA_NON60M_ASHARE_MIN_BARS[cfg["interval"]] // 2):
                cur += pd.Timedelta(days=EMA_NON60M_ASHARE_WEEKLY_HOLDOUT_STEP_DAYS)
                holdout_id += 1
                continue
            ema_metrics = run_ema_long_only_window(sub, cost_bps=EMA_NON60M_ASHARE_COST_BPS)
            psar_metrics = run_psar_long_only_window(sub, cost_bps=EMA_NON60M_ASHARE_COST_BPS)
            holdout_rows.append(
                {
                    "asset": cfg["asset"],
                    "ticker": cfg["ticker"],
                    "asset_class": cfg["asset_class"],
                    "interval": cfg["interval"],
                    "holdout_id": int(holdout_id),
                    "train_start": cur,
                    "train_end": train_end,
                    "holdout_start": train_end,
                    "holdout_end": holdout_end,
                    "bars": int(len(sub)),
                    "ema_net20_profit_pct": ema_metrics["net20_profit_pct"],
                    "ema_trades": ema_metrics["trades"],
                    "ema_net20_positive": ema_metrics["net20_positive"],
                    "psar_net20_profit_pct": psar_metrics["net20_profit_pct"],
                    "psar_trades": psar_metrics["trades"],
                    "psar_net20_positive": psar_metrics["net20_positive"],
                    "ema_minus_psar_net20_pp": float(ema_metrics["net20_profit_pct"] - psar_metrics["net20_profit_pct"]),
                    "ema_beats_psar_net20": float(ema_metrics["net20_profit_pct"] > psar_metrics["net20_profit_pct"]),
                }
            )
            cur += pd.Timedelta(days=EMA_NON60M_ASHARE_WEEKLY_HOLDOUT_STEP_DAYS)
            holdout_id += 1

    holdout_df = pd.DataFrame(holdout_rows)
    if holdout_df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    pocket_rows: list[dict] = []
    for (asset, ticker, asset_class, interval), g in holdout_df.sort_values("holdout_start").groupby(["asset", "ticker", "asset_class", "interval"], sort=False):
        ema_pos_share = float(g["ema_net20_positive"].mean())
        psar_pos_share = float(g["psar_net20_positive"].mean())
        delta_med = float(g["ema_minus_psar_net20_pp"].median())
        if ema_pos_share >= 0.5 and delta_med > 0:
            reading = "EMA 仍可保留"
        elif psar_pos_share >= 0.7 and delta_med < 0:
            reading = "PSAR 更稳，EMA 应继续收窄"
        else:
            reading = "mixed：仍需更晚段验证"
        pocket_rows.append(
            {
                "asset": asset,
                "ticker": ticker,
                "asset_class": asset_class,
                "interval": interval,
                "holdouts": int(len(g)),
                "ema_net20_positive_holdout_share": ema_pos_share,
                "psar_net20_positive_holdout_share": psar_pos_share,
                "ema_net20_median_profit_pct": float(g["ema_net20_profit_pct"].median()),
                "psar_net20_median_profit_pct": float(g["psar_net20_profit_pct"].median()),
                "ema_median_trades": float(g["ema_trades"].median()),
                "psar_median_trades": float(g["psar_trades"].median()),
                "ema_vs_psar_median_net20_delta_pp": delta_med,
                "ema_better_holdout_share": float(g["ema_beats_psar_net20"].mean()),
                "reading": reading,
            }
        )
    pocket_df = pd.DataFrame(pocket_rows)

    overall_df = pd.DataFrame(
        [
            {
                "pockets": int(len(pocket_df)),
                "holdouts": int(len(holdout_df)),
                "ema_net20_positive_holdout_share": float(holdout_df["ema_net20_positive"].mean()),
                "psar_net20_positive_holdout_share": float(holdout_df["psar_net20_positive"].mean()),
                "ema_better_holdout_share": float(holdout_df["ema_beats_psar_net20"].mean()),
                "ema_majority_positive_pockets": int((pocket_df["ema_net20_positive_holdout_share"] >= 0.5).sum()) if not pocket_df.empty else 0,
                "psar_majority_positive_pockets": int((pocket_df["psar_net20_positive_holdout_share"] >= 0.5).sum()) if not pocket_df.empty else 0,
                "verdict": "PSAR-lean" if float(holdout_df["psar_net20_positive"].mean()) >= 0.7 and float(holdout_df["ema_beats_psar_net20"].mean()) < 0.5 else "mixed",
            }
        ]
    )

    holdout_df.to_csv(ART_DIR / "ema_non60m_ashare_weekly_holdout_window_metrics.csv", index=False)
    pocket_df.to_csv(ART_DIR / "ema_non60m_ashare_weekly_holdout_pocket_summary.csv", index=False)
    overall_df.to_csv(ART_DIR / "ema_non60m_ashare_weekly_holdout_overall_summary.csv", index=False)
    return holdout_df, pocket_df, overall_df


def psar_sell_cond(row: pd.Series) -> bool:
    if pd.isna(row["prev_low"]) or pd.isna(row["psar"]):
        return False
    return (row["psar"] > row["close"]) and (row["low"] < row["prev_low"])


def longest_negative_streak(flag_s: pd.Series) -> int:
    longest = 0
    cur = 0
    for ok in flag_s.astype(bool).tolist():
        if ok:
            cur = 0
        else:
            cur += 1
            longest = max(longest, cur)
    return int(longest)


def build_ema60m_crypto_rolling_slice() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    window_rows: list[dict] = []
    for asset, path in EMA60M_ROLLING_CACHE_FILES.items():
        if not path.exists():
            continue
        bars = pd.read_csv(path, parse_dates=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
        feat = build_ema_only_feature_frame(bars)
        start = feat["timestamp"].min().floor("D")
        end = feat["timestamp"].max().ceil("D")
        win_id = 0
        cur = start
        while cur + pd.Timedelta(days=EMA60M_ROLLING_WINDOW_DAYS) <= end:
            win_end = cur + pd.Timedelta(days=EMA60M_ROLLING_WINDOW_DAYS)
            sub = feat[(feat["timestamp"] >= cur) & (feat["timestamp"] < win_end)].copy()
            if len(sub) < 100:
                cur += pd.Timedelta(days=EMA60M_ROLLING_STEP_DAYS)
                win_id += 1
                continue
            metrics = run_ema_long_only_window(sub, cost_bps=EMA60M_ROLLING_COST_BPS)
            window_rows.append(
                {
                    "asset": asset,
                    "window_id": int(win_id),
                    "window_start": cur,
                    "window_end": win_end,
                    "bars": int(len(sub)),
                    **metrics,
                }
            )
            cur += pd.Timedelta(days=EMA60M_ROLLING_STEP_DAYS)
            win_id += 1

    window_df = pd.DataFrame(window_rows)
    if window_df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    asset_rows: list[dict] = []
    for asset, g in window_df.sort_values("window_start").groupby("asset", sort=False):
        asset_rows.append(
            {
                "asset": asset,
                "windows": int(len(g)),
                "gross_positive_window_share": float(g["gross_positive"].mean()),
                "net20_positive_window_share": float(g["net20_positive"].mean()),
                "gross_median_profit_pct": float(g["gross_profit_pct"].median()),
                "net20_median_profit_pct": float(g["net20_profit_pct"].median()),
                "best_net20_window_pct": float(g["net20_profit_pct"].max()),
                "worst_net20_window_pct": float(g["net20_profit_pct"].min()),
                "longest_net20_negative_streak": int(longest_negative_streak(g["net20_positive"])),
            }
        )
    asset_df = pd.DataFrame(asset_rows)

    majority_gross_assets = int((asset_df["gross_positive_window_share"] > 0.5).sum()) if not asset_df.empty else 0
    majority_net_assets = int((asset_df["net20_positive_window_share"] > 0.5).sum()) if not asset_df.empty else 0
    overall_df = pd.DataFrame(
        [
            {
                "assets": int(asset_df["asset"].nunique()) if not asset_df.empty else 0,
                "windows": int(len(window_df)),
                "gross_positive_window_share": float(window_df["gross_positive"].mean()),
                "net20_positive_window_share": float(window_df["net20_positive"].mean()),
                "majority_gross_assets": majority_gross_assets,
                "majority_net20_assets": majority_net_assets,
                "gate": "pass" if majority_net_assets >= max(1, int(np.ceil(len(asset_df) / 2))) and float(window_df["net20_positive"].mean()) >= 0.5 else ("yellow" if float(window_df["gross_positive"].mean()) >= 0.5 or float(window_df["net20_positive"].mean()) >= 0.25 else "fail"),
            }
        ]
    )

    window_df.to_csv(ART_DIR / "ema60m_crypto_rolling_window_metrics.csv", index=False)
    asset_df.to_csv(ART_DIR / "ema60m_crypto_rolling_asset_summary.csv", index=False)
    overall_df.to_csv(ART_DIR / "ema60m_crypto_rolling_overall_summary.csv", index=False)
    return window_df, asset_df, overall_df


def run_ema_psar_exit_overlay_window(df: pd.DataFrame, *, cost_bps: int = EMA60M_ROLLING_COST_BPS) -> dict[str, float]:
    cash = 1.0
    qty = 0.0
    in_pos = False
    entry_price = np.nan
    trade_rets: list[float] = []

    for _, row in df.iterrows():
        px = float(row["close"])
        ema_buy = row["ema9"] > row["ema20"]
        ema_sell = row["ema9"] < row["ema20"]
        overlay_sell = ema_sell or psar_sell_cond(row)

        if ema_buy and (not in_pos) and px > 0:
            qty = cash / px
            cash = 0.0
            in_pos = True
            entry_price = px
        elif overlay_sell and in_pos and px > 0:
            cash = qty * px
            trade_rets.append(px / entry_price - 1.0)
            qty = 0.0
            in_pos = False
            entry_price = np.nan

    if in_pos and qty > 0:
        final_px = float(df.iloc[-1]["close"])
        cash = qty * final_px
        trade_rets.append(final_px / entry_price - 1.0)

    gross_return = cash - 1.0
    if trade_rets:
        net20_return = float(np.prod([1.0 + r - (cost_bps / 10000.0) for r in trade_rets]) - 1.0)
    else:
        net20_return = 0.0

    return {
        "gross_profit_pct": float(gross_return * 100.0),
        "net20_profit_pct": float(net20_return * 100.0),
        "trades": float(len(trade_rets)),
        "gross_positive": float(gross_return > 0),
        "net20_positive": float(net20_return > 0),
    }


def build_ema60m_psar_exit_overlay_slice() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    window_rows: list[dict] = []
    for asset, path in EMA60M_ROLLING_CACHE_FILES.items():
        if not path.exists():
            continue
        bars = pd.read_csv(path, parse_dates=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
        feat = build_ema_only_feature_frame(bars)
        start = feat["timestamp"].min().floor("D")
        end = feat["timestamp"].max().ceil("D")
        win_id = 0
        cur = start
        while cur + pd.Timedelta(days=EMA60M_ROLLING_WINDOW_DAYS) <= end:
            win_end = cur + pd.Timedelta(days=EMA60M_ROLLING_WINDOW_DAYS)
            sub = feat[(feat["timestamp"] >= cur) & (feat["timestamp"] < win_end)].copy()
            if len(sub) < 100:
                cur += pd.Timedelta(days=EMA60M_ROLLING_STEP_DAYS)
                win_id += 1
                continue
            ema_metrics = run_ema_long_only_window(sub, cost_bps=EMA60M_ROLLING_COST_BPS)
            overlay_metrics = run_ema_psar_exit_overlay_window(sub, cost_bps=EMA60M_ROLLING_COST_BPS)
            window_rows.append(
                {
                    "asset": asset,
                    "window_id": int(win_id),
                    "window_start": cur,
                    "window_end": win_end,
                    "bars": int(len(sub)),
                    "ema_gross_profit_pct": ema_metrics["gross_profit_pct"],
                    "ema_net20_profit_pct": ema_metrics["net20_profit_pct"],
                    "ema_trades": ema_metrics["trades"],
                    "overlay_gross_profit_pct": overlay_metrics["gross_profit_pct"],
                    "overlay_net20_profit_pct": overlay_metrics["net20_profit_pct"],
                    "overlay_trades": overlay_metrics["trades"],
                    "gross_delta_pp": float(overlay_metrics["gross_profit_pct"] - ema_metrics["gross_profit_pct"]),
                    "net20_delta_pp": float(overlay_metrics["net20_profit_pct"] - ema_metrics["net20_profit_pct"]),
                    "trade_delta": float(overlay_metrics["trades"] - ema_metrics["trades"]),
                    "overlay_better_gross": float(overlay_metrics["gross_profit_pct"] > ema_metrics["gross_profit_pct"]),
                    "overlay_better_net20": float(overlay_metrics["net20_profit_pct"] > ema_metrics["net20_profit_pct"]),
                }
            )
            cur += pd.Timedelta(days=EMA60M_ROLLING_STEP_DAYS)
            win_id += 1

    window_df = pd.DataFrame(window_rows)
    if window_df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    asset_rows: list[dict] = []
    for asset, g in window_df.sort_values("window_start").groupby("asset", sort=False):
        asset_rows.append(
            {
                "asset": asset,
                "windows": int(len(g)),
                "overlay_better_net20_share": float(g["overlay_better_net20"].mean()),
                "ema_net20_median_profit_pct": float(g["ema_net20_profit_pct"].median()),
                "overlay_net20_median_profit_pct": float(g["overlay_net20_profit_pct"].median()),
                "median_net20_delta_pp": float(g["net20_delta_pp"].median()),
                "best_net20_delta_pp": float(g["net20_delta_pp"].max()),
                "worst_net20_delta_pp": float(g["net20_delta_pp"].min()),
                "median_trade_delta": float(g["trade_delta"].median()),
            }
        )
    asset_df = pd.DataFrame(asset_rows)

    improving_assets = int((asset_df["median_net20_delta_pp"] > 0).sum()) if not asset_df.empty else 0
    overall_df = pd.DataFrame(
        [
            {
                "assets": int(asset_df["asset"].nunique()) if not asset_df.empty else 0,
                "windows": int(len(window_df)),
                "overlay_better_net20_windows": int(window_df["overlay_better_net20"].sum()),
                "overlay_better_net20_share": float(window_df["overlay_better_net20"].mean()),
                "ema_net20_positive_window_share": float((window_df["ema_net20_profit_pct"] > 0).mean()),
                "overlay_net20_positive_window_share": float((window_df["overlay_net20_profit_pct"] > 0).mean()),
                "median_net20_delta_pp": float(window_df["net20_delta_pp"].median()),
                "median_trade_delta": float(window_df["trade_delta"].median()),
                "improving_assets": improving_assets,
                "verdict": "helps" if improving_assets >= max(1, int(np.ceil(len(asset_df) / 2))) and float(window_df["overlay_better_net20"].mean()) >= 0.5 else ("mixed" if float(window_df["overlay_better_net20"].mean()) >= 0.33 else "hurts"),
            }
        ]
    )

    window_df.to_csv(ART_DIR / "ema60m_psar_exit_overlay_window_metrics.csv", index=False)
    asset_df.to_csv(ART_DIR / "ema60m_psar_exit_overlay_asset_summary.csv", index=False)
    overall_df.to_csv(ART_DIR / "ema60m_psar_exit_overlay_overall_summary.csv", index=False)
    return window_df, asset_df, overall_df


def build_ema_psar_overlay_deployment_matrix(
    overlay_overall_df: pd.DataFrame,
    ashare_daily_overlay_pocket_df: pd.DataFrame,
    ashare_daily_overlay_overall_df: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict] = []
    if not overlay_overall_df.empty:
        overall = overlay_overall_df.iloc[0]
        rows.append(
            {
                "scope": "Crypto 60m（BTC/ETH/SOL）",
                "current_role": "fail pocket / hard exclude",
                "samples": f"{int(overall['windows'])} rolling windows",
                "overlay_better_share": float(overall["overlay_better_net20_share"]),
                "median_net20_delta_pp": float(overall["median_net20_delta_pp"]),
                "median_trade_delta": float(overall["median_trade_delta"]),
                "deployment_verdict": "reject_rescue_overlay" if str(overall.get("verdict", "-")) == "hurts" else str(overall.get("verdict", "-")),
                "current_read": "PSAR 快退出显著加交易但整体更差；不得把它当成 60m fail pocket 的补救层。",
                "what_to_do_now": "继续把 60m 留在 exclude / fail stoplist，不因 overlay reopen。",
            }
        )

    if not ashare_daily_overlay_pocket_df.empty:
        lookup = ashare_daily_overlay_pocket_df.set_index("asset").to_dict("index")
        for asset in ["创业板ETF", "沪深300ETF"]:
            pocket = lookup.get(asset)
            if pocket is None:
                continue
            rows.append(
                {
                    "scope": f"A股 daily｜{asset} 1d",
                    "current_role": str(pocket.get("current_role", "-")),
                    "samples": f"{int(pocket['holdouts'])} strict holdouts",
                    "overlay_better_share": float(pocket["overlay_better_holdout_share"]),
                    "median_net20_delta_pp": float(pocket["median_net20_delta_pp"]),
                    "median_trade_delta": float(pocket["median_trade_delta"]),
                    "deployment_verdict": str(pocket.get("overlay_verdict", "-")),
                    "current_read": str(pocket.get("deployment_reading", "-")),
                    "what_to_do_now": (
                        "继续只把 PSAR 留在 primary lane 的 shadow protective 观察位；默认 EMA 持有规则不改。"
                        if asset == "创业板ETF"
                        else "继续单跑 EMA shadow 记账；PSAR 不得充当 promotion patch。"
                    ),
                }
            )

    if not ashare_daily_overlay_overall_df.empty:
        overall = ashare_daily_overlay_overall_df.iloc[0]
        rows.append(
            {
                "scope": "A股 daily overall",
                "current_role": "paper/shadow aggregate check",
                "samples": f"{int(overall['holdouts'])} strict holdouts",
                "overlay_better_share": float(overall["overlay_better_holdout_share"]),
                "median_net20_delta_pp": float(overall["median_net20_delta_pp"]),
                "median_trade_delta": float(overall["median_trade_delta"]),
                "deployment_verdict": str(overall.get("overall_verdict", "-")),
                "current_read": str(overall.get("overall_reading", "-")),
                "what_to_do_now": "项目级默认仍是 EMA 负责方向；PSAR 只配 pocket-specific shadow watch，不是 default family overlay。",
            }
        )

    return pd.DataFrame(rows)


def build_ema_chinext_daily_psar_shadow_protocol(
    ashare_daily_overlay_pocket_df: pd.DataFrame,
    ashare_daily_overlay_overall_df: pd.DataFrame,
) -> pd.DataFrame:
    cols = [
        "protocol_rank",
        "protocol_step",
        "scope_or_cadence",
        "concrete_rule",
        "go_if",
        "else_action",
        "why_it_exists",
    ]
    if ashare_daily_overlay_pocket_df.empty:
        return pd.DataFrame(columns=cols)

    lookup = ashare_daily_overlay_pocket_df.set_index("asset").to_dict("index")
    pocket = lookup.get("创业板ETF")
    if pocket is None:
        return pd.DataFrame(columns=cols)

    overall = ashare_daily_overlay_overall_df.iloc[0].to_dict() if not ashare_daily_overlay_overall_df.empty else {}
    better_share = float(pocket.get("overlay_better_holdout_share", np.nan)) * 100.0
    delta_med = float(pocket.get("median_net20_delta_pp", np.nan))
    trade_med = float(pocket.get("median_trade_delta", np.nan))
    overall_better = float(overall.get("overlay_better_holdout_share", np.nan)) * 100.0 if overall else np.nan
    overall_delta = float(overall.get("median_net20_delta_pp", np.nan)) if overall else np.nan

    rows = [
        {
            "protocol_rank": 1,
            "protocol_step": "scope freeze",
            "scope_or_cadence": "只限 `创业板ETF 1d`；默认 EMA-only primary ledger 不改；每个 A 股日线收盘后才允许更新 sidecar。",
            "concrete_rule": "PSAR overlay 只作为 primary lane 的 sidecar shadow protective 观察位；不得外推到 `沪深300ETF 1d`、`A股 daily family` 或 `Crypto 60m`，也不得提前改写默认持有规则。",
            "go_if": f"当前历史证据仍保持 primary pocket 候选：strict holdout 改善占比约 {better_share:.2f}%，median net20 delta 约 {delta_med:.2f}pp。",
            "else_action": "若尝试把 overlay 提前焊进默认 runbook 或推广到其他 pocket，立即回滚成 benchmark-only 注记。",
            "why_it_exists": "先把唯一可观察 pocket 与不可偷渡范围写死，避免 primary 局部改善被误读成 family-wide default overlay。",
        },
        {
            "protocol_rank": 2,
            "protocol_step": "market-close sidecar refresh",
            "scope_or_cadence": "与主账本共用 Eastmoney A 股日线 live source；每个 completed daily close 更新 1 次。",
            "concrete_rule": "每次只补 sidecar comparator：`ema_signal / psar_state / overlay_exit_flag / relative_net_delta_pp / trade_delta / review_note`；没有 completed bar 就保持 `waiting next close`，不补伪 forward。",
            "go_if": "主账本与 sidecar 能在同一收盘时点同步更新，且 default EMA position 完全不受 shadow overlay 影响。",
            "else_action": "任一数据断流、时点不一致或需要事后补记时，sidecar 暂停；primary 继续按 EMA-only runbook 记账。",
            "why_it_exists": "把‘只做 shadow protective 观察’落实到真实 refresh 动作，避免一边等真收盘、一边又在说明页里偷跑未来结果。",
        },
        {
            "protocol_rank": 3,
            "protocol_step": "weekly shadow review",
            "scope_or_cadence": "与 `创业板ETF 1d` primary weekly review 同步；只做 relative review，不改默认 admission。",
            "concrete_rule": "每周只看 sidecar 相对 EMA-only 的 `cumulative relative delta / added trade churn / drawdown delta / execution mismatch`；在没有连续两次 relative red 之前，overlay 继续只留 shadow protective watch。",
            "go_if": f"relative review 仍未连续两次 red，且 extra churn 没明显恶化到把当前约 +{trade_med:.0f} 笔的历史增交易读法打成反向证据。",
            "else_action": "若连续两次 relative red、或出现 execution mismatch，就降回 benchmark-only，不再单列 shadow watch。",
            "why_it_exists": "当前 primary pocket 只是候选，不是默认层；真正该做的是先在 live ledger 里验证它会不会因为额外 churn 把纸面改善吃掉。",
        },
        {
            "protocol_rank": 4,
            "protocol_step": "promotion / default-overlay gate",
            "scope_or_cadence": "只有在 live shadow 已积累到项目级最短观察期后，才允许申请有限 default-overlay trial。",
            "concrete_rule": "先同时满足 overlay-specific gate（live review 的改善占比 ≥ 60% 且 median relative delta > 0）与项目级 `paper_live_promotion_gate_v1`（默认 `30d + >=20` closed cycles、drawdown 不突破 `max(1.25x, +3pp)` guardrail、无 execution mismatch），才允许讨论把 overlay 从 sidecar 提升成 primary 的有限试跑规则。",
            "go_if": f"当前还不满足 promotion：A股 daily overall 目前仅约 {overall_better:.2f}% holdout 改善、median delta 约 {overall_delta:.2f}pp，因此更诚实的位置仍是 shadow-only。",
            "else_action": "继续 shadow-only；不要把 `创业板ETF 1d` 单格改善偷渡成整个 A股 daily 的默认 protective layer。",
            "why_it_exists": "把 ‘候选 protective overlay’ 与 ‘可以接进默认 runbook’ 明确分层，真正缩短 time-to-paper，而不是靠模糊 wording 提前升格。",
        },
    ]
    return pd.DataFrame(rows, columns=cols)


def html_table(df: pd.DataFrame, cols: list[str]) -> str:
    if df.empty:
        return "<p>无数据</p>"
    return df[cols].to_html(index=False, border=0, classes="data-table", justify="left", escape=False)


def load_replication_module():
    spec = importlib.util.spec_from_file_location("regime_repl_mod", REPL_SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["regime_repl_mod"] = mod
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def make_base_median_bar(base_summary: pd.DataFrame, out_path: Path) -> None:
    d = base_summary.set_index("strategy").reindex(BASE_ORDER).reset_index()
    plt.figure(figsize=(8, 4.5))
    colors = ["#2563eb", "#7c3aed", "#f59e0b", "#64748b"]
    plt.bar(d["strategy"], d["median_profit_pct"], color=colors)
    plt.axhline(0, color="#334155", linewidth=1)
    plt.ylabel("Median Profit %")
    plt.title("Raw strategies | median Profit % across markets x frequencies")
    plt.tight_layout()
    plt.savefig(out_path, dpi=170)
    plt.close()


def make_head_to_head_scatter(pair_df: pd.DataFrame, out_path: Path) -> None:
    plt.figure(figsize=(7.6, 6.2))
    colors = {"Crypto": "#f59e0b", "美股": "#2563eb", "A股": "#dc2626"}
    for asset_class, g in pair_df.groupby("asset_class"):
        plt.scatter(g["psar_profit_pct"], g["ema_profit_pct"], s=65, alpha=0.85, label=asset_class, color=colors.get(asset_class, "#475569"))
    lo = min(pair_df["psar_profit_pct"].min(), pair_df["ema_profit_pct"].min()) - 10
    hi = max(pair_df["psar_profit_pct"].max(), pair_df["ema_profit_pct"].max()) + 10
    plt.plot([lo, hi], [lo, hi], "k--", linewidth=1)
    plt.xlim(lo, hi)
    plt.ylim(lo, hi)
    plt.xlabel("PSAR Profit %")
    plt.ylabel("EMA Profit %")
    plt.title("EMA vs PSAR | head-to-head by asset x frequency")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=170)
    plt.close()


def make_delta_heatmap(pair_df: pd.DataFrame, out_path: Path) -> None:
    pivot = pair_df.pivot(index="asset_label", columns="freq", values="ema_minus_psar_pp")
    cols = [c for c in FREQ_ORDER if c in pivot.columns]
    pivot = pivot[cols]
    arr = pivot.values.astype(float)
    vmax = np.nanmax(np.abs(arr)) if np.isfinite(arr).any() else 1.0
    plt.figure(figsize=(7.8, max(4.8, 0.45 * len(pivot.index))))
    im = plt.imshow(arr, aspect="auto", cmap="RdYlGn", vmin=-vmax, vmax=vmax)
    plt.colorbar(im, label="EMA - PSAR (Profit %)")
    plt.xticks(np.arange(len(pivot.columns)), pivot.columns)
    plt.yticks(np.arange(len(pivot.index)), pivot.index)
    plt.title("Where EMA beats PSAR (green) / loses to PSAR (red)")
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            if np.isfinite(arr[i, j]):
                plt.text(j, i, f"{arr[i, j]:.0f}", ha="center", va="center", fontsize=8, color="#111827")
    plt.tight_layout()
    plt.savefig(out_path, dpi=170)
    plt.close()


def make_class_freq_heatmaps(cf_df: pd.DataFrame, out_path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), constrained_layout=True)
    for ax, strategy in zip(axes, ["EMA", "PSAR"]):
        d = cf_df[cf_df["strategy"] == strategy].pivot(index="asset_class", columns="freq", values="median_profit_pct")
        d = d.reindex(CLASS_ORDER)
        d = d[[c for c in FREQ_ORDER if c in d.columns]]
        arr = d.values.astype(float)
        vmax = np.nanmax(np.abs(arr)) if np.isfinite(arr).any() else 1.0
        im = ax.imshow(arr, aspect="auto", cmap="RdYlGn", vmin=-vmax, vmax=vmax)
        ax.set_xticks(np.arange(len(d.columns)))
        ax.set_xticklabels(d.columns)
        ax.set_yticks(np.arange(len(d.index)))
        ax.set_yticklabels(d.index)
        ax.set_title(f"{strategy} median Profit %")
        for i in range(arr.shape[0]):
            for j in range(arr.shape[1]):
                if np.isfinite(arr[i, j]):
                    ax.text(j, i, f"{arr[i, j]:.0f}", ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=axes.ravel().tolist(), fraction=0.03, pad=0.03)
    fig.savefig(out_path, dpi=170)
    plt.close(fig)


def make_profit_vs_trades(pair_df: pd.DataFrame, out_path: Path) -> None:
    plt.figure(figsize=(8, 5.4))
    plt.scatter(pair_df["ema_trades"], pair_df["ema_profit_pct"], label="EMA", color="#2563eb", s=65, alpha=0.8)
    plt.scatter(pair_df["psar_trades"], pair_df["psar_profit_pct"], label="PSAR", color="#7c3aed", s=65, alpha=0.8)
    plt.axhline(0, color="#334155", linewidth=1)
    plt.xlabel("Trade count")
    plt.ylabel("Profit %")
    plt.title("Profit vs trade count | EMA vs PSAR")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=170)
    plt.close()


def make_btc_equity_chart(out_path: Path) -> None:
    if out_path.exists():
        return

    mod = load_replication_module()
    bars = mod.download_bars("BTC-USD", start="2018-01-01", end="2023-01-01", interval="1d")
    feat = mod.build_feature_frame(bars)
    bt = mod.run_strategy_suite(feat)

    buy_hold = 100000.0 * (feat["close"] / feat["close"].iloc[0])
    plt.figure(figsize=(10, 4.8))
    plt.plot(pd.to_datetime(feat["timestamp"], utc=True), bt["EMA"].equity.values, label="EMA", linewidth=1.9, color="#2563eb")
    plt.plot(pd.to_datetime(feat["timestamp"], utc=True), bt["PSAR"].equity.values, label="PSAR", linewidth=1.9, color="#7c3aed")
    plt.plot(pd.to_datetime(feat["timestamp"], utc=True), buy_hold.values, label="Buy & Hold", linewidth=1.6, color="#94a3b8")
    plt.title("BTC daily 2018-2022 | equity curves")
    plt.ylabel("Equity")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=170)
    plt.close()


def main() -> int:
    ensure_dirs()
    if not CROSS_PATH.exists() or not PAPER_PATH.exists():
        raise SystemExit("Replication artifacts not found. Run build_regime_switch_indicator_stack_replication_report.py first.")

    cross = pd.read_csv(CROSS_PATH)
    paper = pd.read_csv(PAPER_PATH)

    base = cross[cross["group"] == "unfiltered"].copy()
    base = base[base["strategy"].isin(BASE_ORDER)].copy()
    focus = base[base["strategy"].isin(["EMA", "PSAR"])].copy()
    focus["asset_label"] = focus["ticker"]

    base_summary = (
        base.groupby("strategy", as_index=False)
        .agg(
            combos=("asset", "count"),
            mean_profit_pct=("profit_pct", "mean"),
            median_profit_pct=("profit_pct", "median"),
            positive_ratio=("profit_pct", lambda s: float((s > 0).mean())),
            median_trades=("nt", "median"),
        )
    )
    winner_idx = base.groupby(["asset", "freq"])["profit_pct"].idxmax()
    winner_counts = base.loc[winner_idx].groupby("strategy").size().to_dict()
    base_summary["winner_count"] = base_summary["strategy"].map(winner_counts).fillna(0).astype(int)
    base_summary = base_summary.sort_values("median_profit_pct", ascending=False)
    base_summary.to_csv(ART_DIR / "base_strategy_summary.csv", index=False)

    focus_summary = (
        focus.groupby("strategy", as_index=False)
        .agg(
            combos=("asset", "count"),
            mean_profit_pct=("profit_pct", "mean"),
            median_profit_pct=("profit_pct", "median"),
            positive_ratio=("profit_pct", lambda s: float((s > 0).mean())),
            mean_trades=("nt", "mean"),
            median_trades=("nt", "median"),
            mean_cagr_pct=("cagr_pct", "mean"),
            median_max_dd_pct=("max_dd_pct", "median"),
        )
    )
    focus_summary.to_csv(ART_DIR / "ema_psar_summary.csv", index=False)

    class_freq = (
        focus.groupby(["strategy", "asset_class", "freq"], as_index=False)
        .agg(
            combos=("asset", "count"),
            mean_profit_pct=("profit_pct", "mean"),
            median_profit_pct=("profit_pct", "median"),
            positive_ratio=("profit_pct", lambda s: float((s > 0).mean())),
            median_trades=("nt", "median"),
        )
    )
    class_freq.to_csv(ART_DIR / "ema_psar_by_class_freq.csv", index=False)

    pair = (
        focus.pivot_table(index=["asset", "ticker", "asset_class", "freq", "asset_label"], columns="strategy", values=["profit_pct", "nt"], aggfunc="first")
        .reset_index()
    )
    pair.columns = [
        (c if isinstance(c, str) else (c[0] if c[1] == "" else f"{c[0]}_{str(c[1]).lower()}"))
        for c in pair.columns.to_flat_index()
    ]
    pair = pair.rename(
        columns={
            "profit_pct_ema": "ema_profit_pct",
            "profit_pct_psar": "psar_profit_pct",
            "nt_ema": "ema_trades",
            "nt_psar": "psar_trades",
        }
    )
    pair["ema_minus_psar_pp"] = pair["ema_profit_pct"] - pair["psar_profit_pct"]
    pair["faster_strategy"] = np.where(pair["psar_trades"] > pair["ema_trades"], "PSAR", "EMA")
    pair["profit_winner"] = np.where(pair["ema_profit_pct"] >= pair["psar_profit_pct"], "EMA", "PSAR")
    pair.to_csv(ART_DIR / "ema_psar_head_to_head.csv", index=False)

    q_focus = paper[paper["strategy"].isin(["EMA", "PSAR"])]
    q_focus.to_csv(ART_DIR / "btc_paper_window_ema_psar.csv", index=False)

    cost_strategy_summary = load_optional_csv(COST_STRATEGY_SUMMARY_PATH)
    cost_freq_summary = load_optional_csv(COST_SUMMARY_PATH)
    cost_by_combo = load_optional_csv(COST_BY_COMBO_PATH)
    if not cost_freq_summary.empty:
        cost_freq_summary["interval"] = cost_freq_summary["interval"].map(lambda x: FREQ_LABEL_MAP.get(str(x), str(x)))
    baseline_family_df = build_baseline_family_survivor_slice(cost_by_combo)
    if not baseline_family_df.empty:
        baseline_family_df.to_csv(ART_DIR / "ema_psar_baseline_family_survivors.csv", index=False)
    ema_non60m_queue_df = build_ema_non60m_honesty_queue(cost_by_combo)
    if not ema_non60m_queue_df.empty:
        ema_non60m_queue_df.to_csv(ART_DIR / "ema_non60m_honesty_queue.csv", index=False)
    ema_non60m_frontier_h2h_df = build_ema_non60m_frontier_head_to_head(cost_by_combo, ema_non60m_queue_df, top_n=6)
    if not ema_non60m_frontier_h2h_df.empty:
        ema_non60m_frontier_h2h_df.to_csv(ART_DIR / "ema_non60m_frontier_vs_psar.csv", index=False)

    ashare_frontier_window_df, ashare_frontier_pocket_df, ashare_frontier_overall_df = build_ema_non60m_ashare_frontier_rolling_slice()
    ashare_daily_holdout_window_df, ashare_daily_holdout_pocket_df, ashare_daily_holdout_overall_df = build_ema_non60m_ashare_daily_holdout_slice()
    ashare_daily_shadow_promotion_df = build_ema_ashare_daily_shadow_promotion_scorecard(ashare_daily_holdout_window_df)
    if not ashare_daily_shadow_promotion_df.empty:
        ashare_daily_shadow_promotion_df.to_csv(ART_DIR / "ema_ashare_daily_shadow_promotion_scorecard.csv", index=False)
    ashare_daily_recent_forward_audit_df = build_ema_ashare_daily_recent_forward_audit(ashare_daily_holdout_window_df, tail_holdouts=2)
    if not ashare_daily_recent_forward_audit_df.empty:
        ashare_daily_recent_forward_audit_df.to_csv(ART_DIR / "ema_ashare_daily_recent_forward_audit.csv", index=False)
    ashare_daily_overlay_window_df, ashare_daily_overlay_pocket_df, ashare_daily_overlay_overall_df = build_ema_ashare_daily_psar_overlay_audit()
    ashare_weekly_holdout_window_df, ashare_weekly_holdout_pocket_df, ashare_weekly_holdout_overall_df = build_ema_non60m_ashare_weekly_holdout_slice()
    rolling_window_df, rolling_asset_df, rolling_overall_df = build_ema60m_crypto_rolling_slice()
    overlay_window_df, overlay_asset_df, overlay_overall_df = build_ema60m_psar_exit_overlay_slice()
    overlay_deployment_matrix_df = build_ema_psar_overlay_deployment_matrix(
        overlay_overall_df,
        ashare_daily_overlay_pocket_df,
        ashare_daily_overlay_overall_df,
    )
    if not overlay_deployment_matrix_df.empty:
        overlay_deployment_matrix_df.to_csv(ART_DIR / "ema_psar_overlay_deployment_matrix.csv", index=False)
    ema_chinext_shadow_protocol_df = build_ema_chinext_daily_psar_shadow_protocol(
        ashare_daily_overlay_pocket_df,
        ashare_daily_overlay_overall_df,
    )
    if not ema_chinext_shadow_protocol_df.empty:
        ema_chinext_shadow_protocol_df.to_csv(ART_DIR / "ema_chinext_daily_psar_shadow_protocol.csv", index=False)
    ema_final_survivor_map_df = build_ema_final_survivor_map(
        cost_by_combo,
        rolling_overall_df,
        ashare_daily_holdout_pocket_df,
        ashare_weekly_holdout_pocket_df,
    )
    if not ema_final_survivor_map_df.empty:
        ema_final_survivor_map_df.to_csv(ART_DIR / "ema_baseline_family_final_survivor_map.csv", index=False)
    ema_paper_candidate_spec_df = build_ema_paper_candidate_spec(ema_final_survivor_map_df)
    if not ema_paper_candidate_spec_df.empty:
        ema_paper_candidate_spec_df.to_csv(ART_DIR / "ema_paper_trading_candidate_spec.csv", index=False)
    ema_paper_operating_spec_df = build_ema_paper_operating_spec(ema_paper_candidate_spec_df)
    if not ema_paper_operating_spec_df.empty:
        ema_paper_operating_spec_df.to_csv(ART_DIR / "ema_paper_trading_operating_spec.csv", index=False)
    ema_secondary_backstop_recheck_df = build_ema_secondary_backstop_recheck_queue(
        ema_non60m_queue_df,
        ema_paper_candidate_spec_df,
        ema_paper_operating_spec_df,
    )
    if not ema_secondary_backstop_recheck_df.empty:
        ema_secondary_backstop_recheck_df.to_csv(ART_DIR / "ema_secondary_backstop_recheck_queue.csv", index=False)
    ema_paper_monitoring_board_df = build_ema_paper_monitoring_board(
        ema_paper_candidate_spec_df,
        ema_paper_operating_spec_df,
        ashare_daily_shadow_promotion_df,
    )
    if not ema_paper_monitoring_board_df.empty:
        ema_paper_monitoring_board_df.to_csv(ART_DIR / "ema_paper_trading_monitoring_board.csv", index=False)
    ema_paper_runbook_df = build_ema_paper_trading_runbook(
        ema_paper_candidate_spec_df,
        ema_paper_operating_spec_df,
        ema_paper_monitoring_board_df,
        ashare_daily_recent_forward_audit_df,
        ashare_daily_overlay_pocket_df,
    )
    if not ema_paper_runbook_df.empty:
        ema_paper_runbook_df.to_csv(ART_DIR / "ema_paper_trading_runbook.csv", index=False)
    ema_paper_kickoff_checklist_df = build_ema_paper_trading_kickoff_checklist(
        ema_paper_runbook_df,
        ema_paper_monitoring_board_df,
    )
    if not ema_paper_kickoff_checklist_df.empty:
        ema_paper_kickoff_checklist_df.to_csv(ART_DIR / "ema_paper_trading_kickoff_checklist.csv", index=False)
    ema_paper_ledger_template_df = build_ema_paper_trading_ledger_template(ema_paper_runbook_df)
    if not ema_paper_ledger_template_df.empty:
        ema_paper_ledger_template_df.to_csv(ART_DIR / "ema_paper_trading_ledger_template.csv", index=False)
    ema_paper_day0_seed_rows_df = build_ema_paper_trading_day0_seed_rows(ema_paper_runbook_df)
    if not ema_paper_day0_seed_rows_df.empty:
        ema_paper_day0_seed_rows_df.to_csv(ART_DIR / "ema_paper_trading_day0_seed_rows.csv", index=False)
    ema_paper_first_week_review_df = build_ema_paper_first_week_review_scorecard(
        ema_paper_runbook_df,
        ema_paper_monitoring_board_df,
    )
    if not ema_paper_first_week_review_df.empty:
        ema_paper_first_week_review_df.to_csv(ART_DIR / "ema_paper_trading_first_week_review_scorecard.csv", index=False)
    snapshot_clock_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    ema_paper_day0_snapshot_df = build_ema_paper_trading_day0_snapshot(
        ema_paper_day0_seed_rows_df,
        ema_paper_monitoring_board_df,
        ema_paper_first_week_review_df,
        ema_secondary_backstop_recheck_df,
        snapshot_clock_utc=snapshot_clock_utc,
    )
    if not ema_paper_day0_snapshot_df.empty:
        ema_paper_day0_snapshot_df.to_csv(ART_DIR / "ema_paper_trading_day0_snapshot.csv", index=False)
    ema_paper_first_refresh_queue_df = build_ema_paper_trading_first_refresh_queue(
        ema_paper_day0_snapshot_df,
        ema_paper_first_week_review_df,
        ema_secondary_backstop_recheck_df,
    )
    if not ema_paper_first_refresh_queue_df.empty:
        ema_paper_first_refresh_queue_df.to_csv(ART_DIR / "ema_paper_trading_first_refresh_queue.csv", index=False)
    ema_paper_first_refresh_delta_df = build_ema_paper_trading_first_refresh_delta(
        ema_paper_day0_snapshot_df,
        ema_paper_first_refresh_queue_df,
    )
    if not ema_paper_first_refresh_delta_df.empty:
        ema_paper_first_refresh_delta_df.to_csv(ART_DIR / "ema_paper_trading_first_refresh_delta.csv", index=False)
    ema_paper_daily_refresh_snapshot_df = build_ema_paper_trading_daily_refresh_snapshot(
        ema_paper_day0_snapshot_df,
    )
    if not ema_paper_daily_refresh_snapshot_df.empty:
        ema_paper_daily_refresh_snapshot_df.to_csv(ART_DIR / "ema_paper_trading_daily_refresh_snapshot.csv", index=False)
    ema_paper_refresh_dependency_audit_df = build_ema_paper_trading_refresh_dependency_audit(
        ema_paper_daily_refresh_snapshot_df,
    )
    if not ema_paper_refresh_dependency_audit_df.empty:
        ema_paper_refresh_dependency_audit_df.to_csv(ART_DIR / "ema_paper_trading_refresh_dependency_audit.csv", index=False)
    ema_paper_refresh_clock_audit_df = build_ema_paper_trading_refresh_clock_audit(
        ema_paper_daily_refresh_snapshot_df,
        ema_paper_day0_snapshot_df,
    )
    if not ema_paper_refresh_clock_audit_df.empty:
        ema_paper_refresh_clock_audit_df.to_csv(ART_DIR / "ema_paper_trading_refresh_clock_audit.csv", index=False)
    ema_paper_next_close_action_queue_df = build_ema_paper_trading_next_close_action_queue(
        ema_paper_refresh_clock_audit_df,
    )
    if not ema_paper_next_close_action_queue_df.empty:
        ema_paper_next_close_action_queue_df.to_csv(ART_DIR / "ema_paper_trading_next_close_action_queue.csv", index=False)
    ema_paper_due_guardrail_snapshot_df = build_ema_paper_trading_due_guardrail_snapshot(
        ema_paper_refresh_clock_audit_df,
    )
    if not ema_paper_due_guardrail_snapshot_df.empty:
        ema_paper_due_guardrail_snapshot_df.to_csv(ART_DIR / "ema_paper_trading_due_guardrail_snapshot.csv", index=False)
    ema_paper_refresh_history_df = load_optional_csv(EMA_REFRESH_HISTORY_PATH)
    ema_paper_refresh_history_audit_df = build_ema_paper_trading_refresh_history_audit(
        ema_paper_refresh_history_df,
    )
    if not ema_paper_refresh_history_audit_df.empty:
        ema_paper_refresh_history_audit_df.to_csv(EMA_REFRESH_HISTORY_AUDIT_PATH, index=False)

    make_base_median_bar(base_summary, ART_DIR / "01_base_strategy_median_bar.png")
    make_head_to_head_scatter(pair, ART_DIR / "02_ema_psar_head_to_head_scatter.png")
    make_delta_heatmap(pair, ART_DIR / "03_ema_psar_delta_heatmap.png")
    make_class_freq_heatmaps(class_freq, ART_DIR / "04_ema_psar_class_freq_heatmaps.png")
    make_profit_vs_trades(pair, ART_DIR / "05_profit_vs_trades.png")

    make_btc_equity_chart(ART_DIR / "06_btc_ema_psar_equity.png")

    base_tbl = base_summary.copy()
    for c in ["mean_profit_pct", "median_profit_pct", "positive_ratio"]:
        if c == "positive_ratio":
            base_tbl[c] = base_tbl[c].map(lambda x: fmt_pct(x * 100.0))
        else:
            base_tbl[c] = base_tbl[c].map(fmt_pct)
    base_tbl["median_trades"] = base_tbl["median_trades"].map(fmt_num)
    base_tbl["winner_count"] = base_tbl["winner_count"].map(lambda x: str(int(x)))
    base_tbl["combos"] = base_tbl["combos"].map(lambda x: str(int(x)))

    focus_tbl = focus_summary.copy()
    for c in ["mean_profit_pct", "median_profit_pct", "mean_cagr_pct", "median_max_dd_pct"]:
        focus_tbl[c] = focus_tbl[c].map(fmt_pct)
    focus_tbl["positive_ratio"] = focus_tbl["positive_ratio"].map(lambda x: fmt_pct(x * 100.0))
    focus_tbl["mean_trades"] = focus_tbl["mean_trades"].map(fmt_num)
    focus_tbl["median_trades"] = focus_tbl["median_trades"].map(fmt_num)
    focus_tbl["combos"] = focus_tbl["combos"].map(lambda x: str(int(x)))

    class_freq_tbl = class_freq.copy()
    for c in ["mean_profit_pct", "median_profit_pct"]:
        class_freq_tbl[c] = class_freq_tbl[c].map(fmt_pct)
    class_freq_tbl["positive_ratio"] = class_freq_tbl["positive_ratio"].map(lambda x: fmt_pct(x * 100.0))
    class_freq_tbl["median_trades"] = class_freq_tbl["median_trades"].map(fmt_num)
    class_freq_tbl["combos"] = class_freq_tbl["combos"].map(lambda x: str(int(x)))

    pair_tbl = pair.copy().sort_values(["asset_class", "asset_label", "freq"])
    for c in ["ema_profit_pct", "psar_profit_pct", "ema_minus_psar_pp"]:
        pair_tbl[c] = pair_tbl[c].map(fmt_pct)
    for c in ["ema_trades", "psar_trades"]:
        pair_tbl[c] = pair_tbl[c].map(lambda x: str(int(x)))

    paper_tbl = q_focus.copy()
    for c in ["profit_pct", "np_pct", "cagr_pct", "max_dd_pct"]:
        paper_tbl[c] = paper_tbl[c].map(fmt_pct)
    paper_tbl["nt"] = paper_tbl["nt"].map(lambda x: str(int(x)))

    cost_strategy_tbl = cost_strategy_summary.copy()
    if not cost_strategy_tbl.empty:
        cost_strategy_tbl["positive_gross_share"] = cost_strategy_tbl["positive_gross_share"].map(lambda x: fmt_pct(x * 100.0))
        cost_strategy_tbl["median_profit_pct"] = cost_strategy_tbl["median_profit_pct"].map(fmt_pct)
        cost_strategy_tbl["median_trades"] = cost_strategy_tbl["median_trades"].map(fmt_num)
        for c in ["median_breakeven_cost_bps", "positive_only_median_breakeven_cost_bps"]:
            cost_strategy_tbl[c] = cost_strategy_tbl[c].map(fmt_bps)
        for c in ["survive_10bps_share", "survive_20bps_share", "survive_50bps_share"]:
            cost_strategy_tbl[c] = cost_strategy_tbl[c].map(lambda x: fmt_pct(x * 100.0))
        cost_strategy_tbl["combos"] = cost_strategy_tbl["combos"].map(lambda x: str(int(x)))

    cost_freq_tbl = cost_freq_summary.copy()
    if not cost_freq_tbl.empty:
        cost_freq_tbl["positive_gross_share"] = cost_freq_tbl["positive_gross_share"].map(lambda x: fmt_pct(x * 100.0))
        cost_freq_tbl["median_profit_pct"] = cost_freq_tbl["median_profit_pct"].map(fmt_pct)
        cost_freq_tbl["median_trades"] = cost_freq_tbl["median_trades"].map(fmt_num)
        for c in ["median_breakeven_cost_bps", "positive_only_median_breakeven_cost_bps"]:
            cost_freq_tbl[c] = cost_freq_tbl[c].map(fmt_bps)
        for c in ["survive_10bps_share", "survive_20bps_share", "survive_50bps_share"]:
            cost_freq_tbl[c] = cost_freq_tbl[c].map(lambda x: fmt_pct(x * 100.0))
        cost_freq_tbl["combos"] = cost_freq_tbl["combos"].map(lambda x: str(int(x)))

    baseline_family_tbl = baseline_family_df.copy()
    if not baseline_family_tbl.empty:
        baseline_family_tbl["combos"] = baseline_family_tbl["combos"].map(lambda x: str(int(x)))
        baseline_family_tbl["positive_gross_share"] = baseline_family_tbl["positive_gross_share"].map(lambda x: fmt_pct(x * 100.0))
        baseline_family_tbl["median_profit_pct"] = baseline_family_tbl["median_profit_pct"].map(fmt_pct)
        baseline_family_tbl["median_trades"] = baseline_family_tbl["median_trades"].map(fmt_num)
        baseline_family_tbl["positive_only_median_breakeven_cost_bps"] = baseline_family_tbl["positive_only_median_breakeven_cost_bps"].map(fmt_bps)
        for c in ["survive_20bps_share", "survive_50bps_share"]:
            baseline_family_tbl[c] = baseline_family_tbl[c].map(lambda x: fmt_pct(x * 100.0))

    ema_non60m_queue_tbl = ema_non60m_queue_df.copy()
    if not ema_non60m_queue_tbl.empty:
        ema_non60m_queue_tbl = ema_non60m_queue_tbl.head(8).copy()
        ema_non60m_queue_tbl["priority_rank"] = ema_non60m_queue_tbl["priority_rank"].map(lambda x: str(int(x)))
        ema_non60m_queue_tbl["trades"] = ema_non60m_queue_tbl["trades"].map(lambda x: str(int(x)))
        for c in ["profit_pct", "max_dd_pct", "approx_net_profit_pct_20bps", "approx_net_profit_pct_50bps"]:
            ema_non60m_queue_tbl[c] = ema_non60m_queue_tbl[c].map(fmt_pct)
        ema_non60m_queue_tbl["breakeven_roundtrip_cost_bps"] = ema_non60m_queue_tbl["breakeven_roundtrip_cost_bps"].map(fmt_bps)
    ema_non60m_queue_head = ema_non60m_queue_df.head(5).to_dict("records") if not ema_non60m_queue_df.empty else []

    ema_non60m_frontier_h2h_tbl = ema_non60m_frontier_h2h_df.copy()
    if not ema_non60m_frontier_h2h_tbl.empty:
        ema_non60m_frontier_h2h_tbl["priority_rank"] = ema_non60m_frontier_h2h_tbl["priority_rank"].map(lambda x: str(int(x)))
        for c in ["ema_trades", "psar_trades"]:
            ema_non60m_frontier_h2h_tbl[c] = ema_non60m_frontier_h2h_tbl[c].map(lambda x: str(int(x)))
        for c in ["ema_breakeven_roundtrip_cost_bps", "psar_breakeven_roundtrip_cost_bps", "ema_minus_psar_breakeven_bps"]:
            ema_non60m_frontier_h2h_tbl[c] = ema_non60m_frontier_h2h_tbl[c].map(fmt_bps)
        ema_non60m_frontier_h2h_tbl["ema_minus_psar_profit_pp"] = ema_non60m_frontier_h2h_tbl["ema_minus_psar_profit_pp"].map(fmt_pct)
    ema_frontier_h2h_head = ema_non60m_frontier_h2h_df.to_dict("records") if not ema_non60m_frontier_h2h_df.empty else []

    ashare_frontier_pocket_tbl = ashare_frontier_pocket_df.copy()
    if not ashare_frontier_pocket_tbl.empty:
        ashare_frontier_pocket_tbl["windows"] = ashare_frontier_pocket_tbl["windows"].map(lambda x: str(int(x)))
        for c in ["ema_median_trades", "psar_median_trades"]:
            ashare_frontier_pocket_tbl[c] = ashare_frontier_pocket_tbl[c].map(lambda x: str(int(x)))
        for c in [
            "ema_net20_positive_window_share",
            "psar_net20_positive_window_share",
            "ema_better_window_share",
        ]:
            ashare_frontier_pocket_tbl[c] = ashare_frontier_pocket_tbl[c].map(lambda x: fmt_pct(x * 100.0))
        for c in [
            "ema_net20_median_profit_pct",
            "psar_net20_median_profit_pct",
            "ema_vs_psar_median_net20_delta_pp",
        ]:
            ashare_frontier_pocket_tbl[c] = ashare_frontier_pocket_tbl[c].map(fmt_pct)
    ashare_frontier_overall = ashare_frontier_overall_df.iloc[0].to_dict() if not ashare_frontier_overall_df.empty else {}
    ashare_frontier_head = ashare_frontier_pocket_df.to_dict("records") if not ashare_frontier_pocket_df.empty else []
    ashare_daily_holdout_tbl = ashare_daily_holdout_pocket_df.copy()
    if not ashare_daily_holdout_tbl.empty:
        ashare_daily_holdout_tbl["holdouts"] = ashare_daily_holdout_tbl["holdouts"].map(lambda x: str(int(x)))
        for c in ["ema_median_trades", "psar_median_trades"]:
            ashare_daily_holdout_tbl[c] = ashare_daily_holdout_tbl[c].map(lambda x: str(int(x)))
        for c in ["ema_net20_positive_holdout_share", "psar_net20_positive_holdout_share", "ema_better_holdout_share"]:
            ashare_daily_holdout_tbl[c] = ashare_daily_holdout_tbl[c].map(lambda x: fmt_pct(x * 100.0))
        for c in ["ema_net20_median_profit_pct", "psar_net20_median_profit_pct", "ema_vs_psar_median_net20_delta_pp"]:
            ashare_daily_holdout_tbl[c] = ashare_daily_holdout_tbl[c].map(fmt_pct)
    ashare_daily_holdout_overall = ashare_daily_holdout_overall_df.iloc[0].to_dict() if not ashare_daily_holdout_overall_df.empty else {}
    ashare_daily_shadow_promotion_tbl = ashare_daily_shadow_promotion_df.copy()
    if not ashare_daily_shadow_promotion_tbl.empty:
        ashare_daily_shadow_promotion_tbl["holdouts"] = ashare_daily_shadow_promotion_tbl["holdouts"].map(lambda x: str(int(x)))
        for c in [
            "overall_ema_positive_holdout_share",
            "overall_ema_beats_psar_share",
            "recent3_ema_positive_holdout_share",
        ]:
            ashare_daily_shadow_promotion_tbl[c] = ashare_daily_shadow_promotion_tbl[c].map(lambda x: fmt_pct(x * 100.0))
        for c in [
            "recent3_ema_median_net20_profit_pct",
            "latest_holdout_net20_profit_pct",
            "latest_holdout_ema_minus_psar_net20_pp",
        ]:
            ashare_daily_shadow_promotion_tbl[c] = ashare_daily_shadow_promotion_tbl[c].map(fmt_pct)
        ashare_daily_shadow_promotion_tbl["gate_hits"] = ashare_daily_shadow_promotion_tbl["gate_hits"].map(lambda x: f"{int(x)}/5")
    ashare_daily_shadow_promotion_lookup = ashare_daily_shadow_promotion_df.set_index("asset").to_dict("index") if not ashare_daily_shadow_promotion_df.empty else {}
    ashare_daily_recent_forward_audit_tbl = ashare_daily_recent_forward_audit_df.copy()
    if not ashare_daily_recent_forward_audit_tbl.empty:
        ashare_daily_recent_forward_audit_tbl["tail_holdouts"] = ashare_daily_recent_forward_audit_tbl["tail_holdouts"].map(lambda x: str(int(x)))
        for c in ["ema_tail_cum_net20_profit_pct", "psar_tail_cum_net20_profit_pct", "tail_ema_minus_psar_cum_pp", "tail_worst_ema_holdout_pct"]:
            ashare_daily_recent_forward_audit_tbl[c] = ashare_daily_recent_forward_audit_tbl[c].map(fmt_pct)
        for c in ["tail_ema_positive_holdout_share", "tail_ema_beats_psar_share"]:
            ashare_daily_recent_forward_audit_tbl[c] = ashare_daily_recent_forward_audit_tbl[c].map(lambda x: fmt_pct(x * 100.0))
    ashare_daily_recent_forward_audit_lookup = ashare_daily_recent_forward_audit_df.set_index("asset").to_dict("index") if not ashare_daily_recent_forward_audit_df.empty else {}
    ashare_daily_overlay_tbl = ashare_daily_overlay_pocket_df.copy()
    if not ashare_daily_overlay_tbl.empty:
        ashare_daily_overlay_tbl["holdouts"] = ashare_daily_overlay_tbl["holdouts"].map(lambda x: str(int(x)))
        ashare_daily_overlay_tbl["overlay_better_holdout_share"] = ashare_daily_overlay_tbl["overlay_better_holdout_share"].map(lambda x: fmt_pct(x * 100.0))
        for c in [
            "ema_net20_median_profit_pct",
            "overlay_net20_median_profit_pct",
            "median_net20_delta_pp",
            "best_net20_delta_pp",
            "worst_net20_delta_pp",
        ]:
            ashare_daily_overlay_tbl[c] = ashare_daily_overlay_tbl[c].map(fmt_pct)
        ashare_daily_overlay_tbl["median_trade_delta"] = ashare_daily_overlay_tbl["median_trade_delta"].map(lambda x: fmt_num(x, 0))
    ashare_daily_overlay_lookup = ashare_daily_overlay_pocket_df.set_index("asset").to_dict("index") if not ashare_daily_overlay_pocket_df.empty else {}
    ashare_daily_overlay_overall = ashare_daily_overlay_overall_df.iloc[0].to_dict() if not ashare_daily_overlay_overall_df.empty else {}
    overlay_deployment_tbl = overlay_deployment_matrix_df.copy()
    if not overlay_deployment_tbl.empty:
        overlay_deployment_tbl["overlay_better_share"] = overlay_deployment_tbl["overlay_better_share"].map(lambda x: fmt_pct(x * 100.0))
        overlay_deployment_tbl["median_net20_delta_pp"] = overlay_deployment_tbl["median_net20_delta_pp"].map(fmt_pct)
        overlay_deployment_tbl["median_trade_delta"] = overlay_deployment_tbl["median_trade_delta"].map(lambda x: fmt_num(x, 0))
    ema_chinext_shadow_protocol_tbl = ema_chinext_shadow_protocol_df.copy()
    if not ema_chinext_shadow_protocol_tbl.empty:
        ema_chinext_shadow_protocol_tbl["protocol_rank"] = ema_chinext_shadow_protocol_tbl["protocol_rank"].map(lambda x: str(int(x)))
    ashare_weekly_holdout_tbl = ashare_weekly_holdout_pocket_df.copy()
    if not ashare_weekly_holdout_tbl.empty:
        ashare_weekly_holdout_tbl["holdouts"] = ashare_weekly_holdout_tbl["holdouts"].map(lambda x: str(int(x)))
        for c in ["ema_median_trades", "psar_median_trades"]:
            ashare_weekly_holdout_tbl[c] = ashare_weekly_holdout_tbl[c].map(lambda x: str(int(x)))
        for c in ["ema_net20_positive_holdout_share", "psar_net20_positive_holdout_share", "ema_better_holdout_share"]:
            ashare_weekly_holdout_tbl[c] = ashare_weekly_holdout_tbl[c].map(lambda x: fmt_pct(x * 100.0))
        for c in ["ema_net20_median_profit_pct", "psar_net20_median_profit_pct", "ema_vs_psar_median_net20_delta_pp"]:
            ashare_weekly_holdout_tbl[c] = ashare_weekly_holdout_tbl[c].map(fmt_pct)
    ashare_weekly_holdout_overall = ashare_weekly_holdout_overall_df.iloc[0].to_dict() if not ashare_weekly_holdout_overall_df.empty else {}

    ema_final_survivor_map_tbl = ema_final_survivor_map_df.copy()
    ema_final_survivor_map_lookup = ema_final_survivor_map_df.set_index("pocket_scope").to_dict("index") if not ema_final_survivor_map_df.empty else {}
    ema_paper_candidate_spec_tbl = ema_paper_candidate_spec_df.copy()
    if not ema_paper_candidate_spec_tbl.empty:
        ema_paper_candidate_spec_tbl["admission_rank"] = ema_paper_candidate_spec_tbl["admission_rank"].map(lambda x: str(int(x)))
    ema_paper_candidate_spec_lookup = ema_paper_candidate_spec_df.set_index("deployment_scope").to_dict("index") if not ema_paper_candidate_spec_df.empty else {}
    ema_paper_operating_spec_tbl = ema_paper_operating_spec_df.copy()
    if not ema_paper_operating_spec_tbl.empty:
        ema_paper_operating_spec_tbl["monitor_rank"] = ema_paper_operating_spec_tbl["monitor_rank"].map(lambda x: str(int(x)))
    ema_paper_operating_spec_lookup = ema_paper_operating_spec_df.set_index("deployment_scope").to_dict("index") if not ema_paper_operating_spec_df.empty else {}
    ema_paper_monitoring_board_tbl = ema_paper_monitoring_board_df.copy()
    if not ema_paper_monitoring_board_tbl.empty:
        ema_paper_monitoring_board_tbl["review_rank"] = ema_paper_monitoring_board_tbl["review_rank"].map(lambda x: str(int(x)))
    ema_paper_monitoring_board_lookup = ema_paper_monitoring_board_df.set_index("deployment_scope").to_dict("index") if not ema_paper_monitoring_board_df.empty else {}
    ema_paper_runbook_tbl = ema_paper_runbook_df.copy()
    if not ema_paper_runbook_tbl.empty:
        ema_paper_runbook_tbl["runbook_rank"] = ema_paper_runbook_tbl["runbook_rank"].map(lambda x: str(int(x)))
    ema_paper_runbook_lookup = ema_paper_runbook_df.set_index("deployment_scope").to_dict("index") if not ema_paper_runbook_df.empty else {}
    ema_paper_kickoff_checklist_tbl = ema_paper_kickoff_checklist_df.copy()
    if not ema_paper_kickoff_checklist_tbl.empty:
        ema_paper_kickoff_checklist_tbl["step_rank"] = ema_paper_kickoff_checklist_tbl["step_rank"].map(lambda x: str(int(x)))
    ema_paper_ledger_template_tbl = ema_paper_ledger_template_df.copy()
    if not ema_paper_ledger_template_tbl.empty:
        ema_paper_ledger_template_tbl["field_order"] = ema_paper_ledger_template_tbl["field_order"].map(lambda x: str(int(x)))
    ema_paper_day0_seed_rows_tbl = ema_paper_day0_seed_rows_df.copy()
    if not ema_paper_day0_seed_rows_tbl.empty:
        ema_paper_day0_seed_rows_tbl["seed_rank"] = ema_paper_day0_seed_rows_tbl["seed_rank"].map(lambda x: str(int(x)))
    ema_paper_first_week_review_tbl = ema_paper_first_week_review_df.copy()
    if not ema_paper_first_week_review_tbl.empty:
        ema_paper_first_week_review_tbl["review_rank"] = ema_paper_first_week_review_tbl["review_rank"].map(lambda x: str(int(x)))
    ema_paper_day0_snapshot_tbl = ema_paper_day0_snapshot_df.copy()
    if not ema_paper_day0_snapshot_tbl.empty:
        ema_paper_day0_snapshot_tbl["snapshot_rank"] = ema_paper_day0_snapshot_tbl["snapshot_rank"].map(lambda x: str(int(x)))
    ema_paper_first_refresh_queue_tbl = ema_paper_first_refresh_queue_df.copy()
    refresh_queue_first = "-"
    refresh_queue_second = "-"
    refresh_queue_third = "-"
    if not ema_paper_first_refresh_queue_tbl.empty:
        for c in ["queue_rank"]:
            ema_paper_first_refresh_queue_tbl[c] = ema_paper_first_refresh_queue_tbl[c].map(lambda x: str(int(x)))
        preview_rows = ema_paper_first_refresh_queue_df.head(3).to_dict("records")
        preview_labels = [f"{r['deployment_scope']} / {r['market_freq_book']}" for r in preview_rows]
        if len(preview_labels) >= 1:
            refresh_queue_first = preview_labels[0]
        if len(preview_labels) >= 2:
            refresh_queue_second = preview_labels[1]
        if len(preview_labels) >= 3:
            refresh_queue_third = preview_labels[2]
    ema_paper_first_refresh_delta_tbl = ema_paper_first_refresh_delta_df.copy()
    first_refresh_delta_first = "-"
    first_refresh_delta_second = "-"
    first_refresh_delta_third = "-"
    if not ema_paper_first_refresh_delta_tbl.empty:
        ema_paper_first_refresh_delta_tbl["refresh_rank"] = ema_paper_first_refresh_delta_tbl["refresh_rank"].map(lambda x: str(int(x)))
        delta_rows = ema_paper_first_refresh_delta_df.to_dict("records")
        if len(delta_rows) >= 1:
            first_refresh_delta_first = str(delta_rows[0].get("delta_note", "-") or "-")
        if len(delta_rows) >= 2:
            first_refresh_delta_second = str(delta_rows[1].get("delta_note", "-") or "-")
        if len(delta_rows) >= 3:
            first_refresh_delta_third = str(delta_rows[2].get("delta_note", "-") or "-")
    ema_paper_daily_refresh_snapshot_tbl = ema_paper_daily_refresh_snapshot_df.copy()
    daily_refresh_primary_note = "-"
    daily_refresh_secondary_summary = "-"
    daily_refresh_shadow_note = "-"
    daily_refresh_live_count = 0
    daily_refresh_fallback_count = 0
    daily_refresh_failed_count = 0
    daily_refresh_long_count = 0
    daily_refresh_flat_count = 0
    if not ema_paper_daily_refresh_snapshot_tbl.empty:
        ema_paper_daily_refresh_snapshot_tbl["refresh_rank"] = ema_paper_daily_refresh_snapshot_tbl["refresh_rank"].map(lambda x: str(int(x)))
        daily_rows = ema_paper_daily_refresh_snapshot_df.to_dict("records")
        daily_refresh_live_count = int(sum(("fallback" not in str(r.get("data_source", ""))) and ("load_failed" not in str(r.get("data_source", ""))) for r in daily_rows))
        daily_refresh_fallback_count = int(sum("fallback" in str(r.get("data_source", "")) for r in daily_rows))
        daily_refresh_failed_count = int(sum("load_failed" in str(r.get("data_source", "")) for r in daily_rows))
        daily_refresh_long_count = int(sum(str(r.get("position_state", "")).startswith(("long_open", "mixed_open")) for r in daily_rows))
        daily_refresh_flat_count = int(sum(str(r.get("position_state", "")).startswith("flat") for r in daily_rows))
        daily_lookup = {
            (str(r.get("deployment_scope", "-")), str(r.get("market_freq_book", "-"))): r
            for r in daily_rows
        }
        primary_row = daily_lookup.get(("创业板ETF 1d", "A股-1d"))
        front_row = daily_lookup.get(("美股 1d+1wk（SPY/QQQ/AAPL）", "美股-1d"))
        mid_row = daily_lookup.get(("贵州茅台 1d+1wk", "A股-1d"))
        backstop_row = daily_lookup.get(("Crypto 1d+1wk（BTC/ETH/SOL）", "Crypto-1d"))
        shadow_row = daily_lookup.get(("沪深300ETF 1d", "A股-1d"))
        if primary_row is not None:
            daily_refresh_primary_note = str(primary_row.get("refresh_note", "-") or "-")
        secondary_bits: list[str] = []
        if front_row is not None:
            secondary_bits.append(f"美股日频={front_row.get('signal_state', '-')} / {front_row.get('position_state', '-')}")
        if mid_row is not None:
            secondary_bits.append(f"茅台日频={mid_row.get('signal_state', '-')} / {mid_row.get('position_state', '-')}")
        if backstop_row is not None:
            secondary_bits.append(f"crypto 日频={backstop_row.get('signal_state', '-')} / {backstop_row.get('position_state', '-')}")
        if secondary_bits:
            daily_refresh_secondary_summary = "；".join(secondary_bits)
        if shadow_row is not None:
            daily_refresh_shadow_note = str(shadow_row.get("refresh_note", "-") or "-")

    ema_paper_refresh_dependency_audit_tbl = ema_paper_refresh_dependency_audit_df.copy()
    refresh_dependency_primary_note = "-"
    refresh_dependency_shadow_note = "-"
    refresh_dependency_live_summary = "-"
    refresh_dependency_verdict = "-"
    refresh_dependency_deployment_line = "EMA 当前更像已经进入 `can-run / can-ledger`，但还没到“source-risk 也清零”的更稳 paper-ready；下一刀若继续 EMA，默认更该先压 A股日频 fallback 依赖，而不是继续补近义 runbook 页面。"
    if not ema_paper_refresh_dependency_audit_tbl.empty:
        ema_paper_refresh_dependency_audit_tbl["dependency_rank"] = ema_paper_refresh_dependency_audit_tbl["dependency_rank"].map(lambda x: str(int(x)))
        dep_rows = ema_paper_refresh_dependency_audit_df.to_dict("records")
        dep_lookup = {str(r.get("deployment_scope", "-")): r for r in dep_rows}
        primary_dep = dep_lookup.get("创业板ETF 1d")
        shadow_dep = dep_lookup.get("沪深300ETF 1d")
        live_dep_rows = [
            r for r in dep_rows
            if str(r.get("dependency_status", "-")) == "live"
            and str(r.get("paper_status", "-")) == "active_secondary_backstop"
        ]
        if primary_dep is not None:
            refresh_dependency_primary_note = str(primary_dep.get("deployment_read", "-") or "-")
        if shadow_dep is not None:
            refresh_dependency_shadow_note = str(shadow_dep.get("deployment_read", "-") or "-")
        if live_dep_rows:
            refresh_dependency_live_summary = "；".join(
                f"{r.get('deployment_scope', '-')}={r.get('ops_priority', '-')}"
                for r in live_dep_rows[:3]
            )
        fallback_scopes = [
            str(r.get("deployment_scope", "-"))
            for r in dep_rows
            if str(r.get("dependency_status", "-")) == "cache_fallback"
        ]
        if fallback_scopes:
            refresh_dependency_verdict = f"当前 active `1d` lanes 里仍有 {len(fallback_scopes)}/{len(dep_rows)} 条依赖 cache fallback（{', '.join(fallback_scopes)}）；其中唯一 primary lane 仍在 fallback，所以 EMA 更像 `可续跑但仍有 primary source-risk`，而不是已经完全 paper-ready。"
            refresh_dependency_deployment_line = "EMA 当前更像已经进入 `can-run / can-ledger`，但还没到“source-risk 也清零”的更稳 paper-ready；下一刀若继续 EMA，默认更该先压 A股日频 fallback 依赖，而不是继续补近义 runbook 页面。"
        else:
            refresh_dependency_verdict = "当前 active `1d` lanes 已全部 live；下一步重点应回到连续 refresh / weekly review，而不是 source 依赖。"
            refresh_dependency_deployment_line = "A股 daily 的 primary / shadow source-risk 已显著下降；EMA 这条线下一刀更该回到连续 refresh、week-1 review、以及 front-queue honesty，而不是继续把时间花在修同类数据源说明。"

    ema_paper_refresh_clock_audit_tbl = ema_paper_refresh_clock_audit_df.copy()
    refresh_clock_primary_note = "-"
    refresh_clock_secondary_summary = "-"
    refresh_clock_week1_line = "-"
    refresh_clock_verdict = "当前还没有新的 on-clock 审计输出。"
    if not ema_paper_refresh_clock_audit_tbl.empty:
        ema_paper_refresh_clock_audit_tbl["clock_rank"] = ema_paper_refresh_clock_audit_tbl["clock_rank"].map(lambda x: str(int(x)))
        clock_rows = ema_paper_refresh_clock_audit_df.to_dict("records")
        clock_lookup = {str(r.get("deployment_scope", "-")): r for r in clock_rows}
        primary_clock = clock_lookup.get("创业板ETF 1d")
        front_clock = clock_lookup.get("美股 1d+1wk（SPY/QQQ/AAPL）")
        mid_clock = clock_lookup.get("贵州茅台 1d+1wk")
        back_clock = clock_lookup.get("Crypto 1d+1wk（BTC/ETH/SOL）")
        shadow_clock = clock_lookup.get("沪深300ETF 1d")
        if primary_clock is not None:
            refresh_clock_primary_note = str(primary_clock.get("current_clock_read", "-") or "-")
        secondary_bits: list[str] = []
        if front_clock is not None:
            secondary_bits.append(f"front-queue 美股={front_clock.get('next_expected_close_utc', '-')} 前等待真 close")
        if mid_clock is not None:
            secondary_bits.append(f"mid-queue 茅台={mid_clock.get('next_expected_close_utc', '-')} 前保持 on-clock")
        if back_clock is not None:
            secondary_bits.append(f"crypto backstop={back_clock.get('next_expected_close_utc', '-')} 前继续等待 UTC close")
        if shadow_clock is not None:
            secondary_bits.append(f"shadow 沪深300ETF={shadow_clock.get('next_expected_close_utc', '-')} 前继续记 shadow")
        if secondary_bits:
            refresh_clock_secondary_summary = "；".join(secondary_bits)
        week1_due_values = [
            str(r.get("week1_review_due_utc", "-") or "-")
            for r in clock_rows
            if str(r.get("week1_review_due_utc", "-") or "-") != "-"
        ]
        if week1_due_values:
            unique_due = sorted(set(week1_due_values))
            refresh_clock_week1_line = f"当前首个 week-1 review 还没到时；最早约在 {unique_due[0]}，在那之前更诚实的动作是等下一次真实 completed bar，而不是伪造不存在的新 review。"
        waiting_next_close = int(sum(str(r.get("clock_status", "-")) == "on_clock_waiting_next_close" for r in clock_rows))
        week1_not_due = int(sum(str(r.get("week1_status", "-")) == "week1_not_due" for r in clock_rows))
        refresh_clock_verdict = f"当前 active `1d` lanes 约 {waiting_next_close}/{len(clock_rows)} 条都处在 `on-clock waiting next close`；同时 week-1 review 约 {week1_not_due}/{len(clock_rows)} 条仍未到时。也就是说，EMA 现在更像是在按计划等待下一次真实市场 close，而不是账本停在半路。"

    ema_paper_next_close_action_queue_tbl = ema_paper_next_close_action_queue_df.copy()
    next_close_queue_verdict = "当前还没有可执行的 next-close action queue。"
    if not ema_paper_next_close_action_queue_tbl.empty:
        ema_paper_next_close_action_queue_tbl["queue_rank"] = ema_paper_next_close_action_queue_tbl["queue_rank"].map(lambda x: str(int(x)))
        queue_rows = ema_paper_next_close_action_queue_df.to_dict("records")
        queue_head = queue_rows[0]
        next_close_queue_verdict = (
            f"当前 next-close queue 已按时序排好；首位是 {queue_head.get('deployment_scope', '-')}，"
            f"预计在 {queue_head.get('next_expected_close_utc', '-')} 左右进入可执行 refresh 窗口。"
        )

    ema_paper_due_guardrail_tbl = ema_paper_due_guardrail_snapshot_df.copy()
    due_guardrail_verdict = "当前还没有 due-now / overdue 守门快照。"
    if not ema_paper_due_guardrail_tbl.empty:
        ema_paper_due_guardrail_tbl["guardrail_rank"] = ema_paper_due_guardrail_tbl["guardrail_rank"].map(lambda x: str(int(x)))
        due_rows = ema_paper_due_guardrail_snapshot_df.to_dict("records")
        due_soon = [r for r in due_rows if str(r.get("due_bucket", "-")) == "due_soon"]
        due_now = [r for r in due_rows if str(r.get("due_bucket", "-")) == "due_now_refresh_window"]
        overdue = [r for r in due_rows if str(r.get("due_bucket", "-")) == "overdue_refresh_check"]
        blocked = [r for r in due_rows if str(r.get("due_bucket", "-")) == "blocked_before_due"]
        if overdue:
            first = overdue[0]
            due_guardrail_verdict = (
                f"当前已有 {len(overdue)}/{len(due_rows)} 条 lane 落入 `overdue_refresh_check`；"
                f"其中最靠前的是 {first.get('deployment_scope', '-')}，{first.get('relative_due_gap', '-')}。"
            )
        elif due_now:
            first = due_now[0]
            due_guardrail_verdict = (
                f"当前已有 {len(due_now)}/{len(due_rows)} 条 lane 进入 `due_now_refresh_window`；"
                f"其中最靠前的是 {first.get('deployment_scope', '-')}，现在不该再把它当纯 waiting。"
            )
        elif due_soon:
            first = due_soon[0]
            due_guardrail_verdict = (
                f"当前最近的 close 已进入 `due_soon`：{first.get('deployment_scope', '-')} 约 {first.get('relative_due_gap', '-')}；"
                f"这一步的价值是把“还在等”与“马上该刷”分开。"
            )
        elif blocked:
            due_guardrail_verdict = f"当前有 {len(blocked)}/{len(due_rows)} 条 lane 先卡在数据或时点问题；应先修 blocker，再谈 waiting / due。"
        else:
            due_guardrail_verdict = "当前所有 active lane 仍处在 `waiting_not_due`，说明现在更像正常等 close，而不是漏掉 refresh。"

    ema_paper_refresh_history_audit_tbl = ema_paper_refresh_history_audit_df.copy()
    refresh_history_verdict = "当前还没有 append-only refresh history 输出。"
    refresh_history_seed_note = "-"
    refresh_history_latest_note = "-"
    refresh_history_deployment_line = "append-only history 还没落表前，snapshot 只能回答当前状态，不能回答这张账本有没有连续续写。"
    if not ema_paper_refresh_history_df.empty:
        history_rows = ema_paper_refresh_history_df.copy()
        history_total_rows = int(len(history_rows))
        history_unique_keys = int(history_rows["history_key"].astype(str).nunique()) if "history_key" in history_rows.columns else history_total_rows
        history_duplicate_keys = max(history_total_rows - history_unique_keys, 0)
        history_rows["_completed_ts"] = pd.to_datetime(history_rows.get("latest_completed_bar_utc"), utc=True, errors="coerce")
        history_rows["_recorded_ts"] = pd.to_datetime(history_rows.get("history_recorded_at_utc"), utc=True, errors="coerce")
        latest_row = history_rows.sort_values(["_completed_ts", "_recorded_ts"], na_position="last").iloc[-1].to_dict()
        if not ema_paper_refresh_history_audit_tbl.empty:
            ema_paper_refresh_history_audit_tbl["history_rank"] = ema_paper_refresh_history_audit_tbl["history_rank"].map(lambda x: str(int(x)))
            for c in ["rows_recorded", "distinct_completed_bars"]:
                ema_paper_refresh_history_audit_tbl[c] = ema_paper_refresh_history_audit_tbl[c].map(lambda x: str(int(x)))
            audit_rows = ema_paper_refresh_history_audit_df.to_dict("records")
            seed_only = [r for r in audit_rows if str(r.get("history_status", "-")) == "seed_only_history"]
            continuing = [r for r in audit_rows if str(r.get("history_status", "-")) == "append_only_continuing"]
            warnings = [r for r in audit_rows if str(r.get("history_status", "-")) == "duplicate_bar_warning"]
            if warnings:
                refresh_history_verdict = (
                    f"当前 history 里已有 {len(warnings)}/{len(audit_rows)} 条 lane 出现 duplicate bar/key 警告；"
                    f"在修完去重前，不应把这张 ledger 当成正常连续续写。"
                )
            elif continuing:
                refresh_history_verdict = (
                    f"当前 append-only history 已有 {len(continuing)}/{len(audit_rows)} 条 lane 进入 2+ 条 completed-bar 连续记录；"
                    f"它已经不只是覆盖式 snapshot，而是可审计的续写账本。"
                )
            else:
                refresh_history_verdict = (
                    f"当前 append-only history 已落下 {history_total_rows} 条 rows，覆盖 {len(audit_rows)} 条 active/shadow lanes，"
                    f"duplicate history key 约 {history_duplicate_keys}；但各 lane 仍基本只有 seed 级 1 条记录，下一根真实 close 才会开始检验连续续写。"
                )
            if seed_only:
                refresh_history_seed_note = (
                    f"当前约 {len(seed_only)}/{len(audit_rows)} 条 lane 仍是 `seed_only_history`：账本骨架已建好，"
                    "但还没进入 2+ 条 completed-bar 的真正连续记录。"
                )
            else:
                refresh_history_seed_note = "当前所有已入 history 的 lane 都已超过单条 seed 记录，可以直接检查连续 refresh / missed refresh。"
        refresh_history_latest_note = (
            f"最近一条 history 记录来自 {latest_row.get('deployment_scope', '-')} / {latest_row.get('market_freq_book', '-')}，"
            f"latest completed bar = {latest_row.get('latest_completed_bar_utc', '-')}, recorded at = {latest_row.get('history_recorded_at_utc', '-')}。"
        )
        refresh_history_deployment_line = "这一步把‘当前 snapshot 长什么样’与‘同一张 ledger 有没有连续续写’分开；下一次真实 close 到来后，默认应先看 history rows 是否从 1 条 seed 增长到 2+ 条连续记录，而不是只盯最新覆盖式 snapshot。"

    ema_secondary_backstop_recheck_tbl = ema_secondary_backstop_recheck_df.copy()
    secondary_front_count = 0
    secondary_mid_count = 0
    secondary_back_count = 0
    secondary_first_target = "-"
    if not ema_secondary_backstop_recheck_tbl.empty:
        secondary_front_count = int((ema_secondary_backstop_recheck_df["recheck_bucket"] == "front-of-queue").sum())
        secondary_mid_count = int((ema_secondary_backstop_recheck_df["recheck_bucket"] == "mid-queue").sum())
        secondary_back_count = int((ema_secondary_backstop_recheck_df["recheck_bucket"] == "back-of-queue").sum())
        secondary_first_target = str(ema_secondary_backstop_recheck_df.sort_values("recheck_rank").iloc[0]["pocket_scope"])
        for c in ["recheck_rank", "global_honesty_rank", "trades"]:
            ema_secondary_backstop_recheck_tbl[c] = ema_secondary_backstop_recheck_tbl[c].map(lambda x: str(int(x)))
        for c in ["profit_pct", "approx_net_profit_pct_20bps", "breakeven_roundtrip_cost_bps"]:
            if c == "breakeven_roundtrip_cost_bps":
                ema_secondary_backstop_recheck_tbl[c] = ema_secondary_backstop_recheck_tbl[c].map(fmt_bps)
            else:
                ema_secondary_backstop_recheck_tbl[c] = ema_secondary_backstop_recheck_tbl[c].map(fmt_pct)

    rolling_asset_tbl = rolling_asset_df.copy()
    if not rolling_asset_tbl.empty:
        rolling_asset_tbl["windows"] = rolling_asset_tbl["windows"].map(lambda x: str(int(x)))
        for c in ["gross_positive_window_share", "net20_positive_window_share"]:
            rolling_asset_tbl[c] = rolling_asset_tbl[c].map(lambda x: fmt_pct(x * 100.0))
        for c in ["gross_median_profit_pct", "net20_median_profit_pct", "best_net20_window_pct", "worst_net20_window_pct"]:
            rolling_asset_tbl[c] = rolling_asset_tbl[c].map(fmt_pct)
        rolling_asset_tbl["longest_net20_negative_streak"] = rolling_asset_tbl["longest_net20_negative_streak"].map(lambda x: str(int(x)))

    rolling_window_tbl = rolling_window_df.copy()
    if not rolling_window_tbl.empty:
        rolling_window_tbl = rolling_window_tbl.sort_values("net20_profit_pct").head(9).copy()
        rolling_window_tbl["window_start"] = pd.to_datetime(rolling_window_tbl["window_start"], utc=True).dt.strftime("%Y-%m-%d")
        rolling_window_tbl["window_end"] = pd.to_datetime(rolling_window_tbl["window_end"], utc=True).dt.strftime("%Y-%m-%d")
        rolling_window_tbl["bars"] = rolling_window_tbl["bars"].map(lambda x: str(int(x)))
        rolling_window_tbl["trades"] = rolling_window_tbl["trades"].map(lambda x: str(int(x)))
        for c in ["gross_profit_pct", "net20_profit_pct"]:
            rolling_window_tbl[c] = rolling_window_tbl[c].map(fmt_pct)

    rolling_overall = rolling_overall_df.iloc[0].to_dict() if not rolling_overall_df.empty else {}

    overlay_asset_tbl = overlay_asset_df.copy()
    if not overlay_asset_tbl.empty:
        overlay_asset_tbl["windows"] = overlay_asset_tbl["windows"].map(lambda x: str(int(x)))
        overlay_asset_tbl["overlay_better_net20_share"] = overlay_asset_tbl["overlay_better_net20_share"].map(lambda x: fmt_pct(x * 100.0))
        for c in ["ema_net20_median_profit_pct", "overlay_net20_median_profit_pct", "median_net20_delta_pp", "best_net20_delta_pp", "worst_net20_delta_pp"]:
            overlay_asset_tbl[c] = overlay_asset_tbl[c].map(fmt_pct)
        overlay_asset_tbl["median_trade_delta"] = overlay_asset_tbl["median_trade_delta"].map(lambda x: fmt_num(x, 0))

    overlay_window_tbl = overlay_window_df.copy()
    if not overlay_window_tbl.empty:
        overlay_window_tbl = overlay_window_tbl.sort_values("net20_delta_pp").head(9).copy()
        overlay_window_tbl["window_start"] = pd.to_datetime(overlay_window_tbl["window_start"], utc=True).dt.strftime("%Y-%m-%d")
        overlay_window_tbl["window_end"] = pd.to_datetime(overlay_window_tbl["window_end"], utc=True).dt.strftime("%Y-%m-%d")
        overlay_window_tbl["bars"] = overlay_window_tbl["bars"].map(lambda x: str(int(x)))
        for c in ["ema_trades", "overlay_trades", "trade_delta"]:
            overlay_window_tbl[c] = overlay_window_tbl[c].map(lambda x: fmt_num(x, 0))
        for c in ["ema_net20_profit_pct", "overlay_net20_profit_pct", "net20_delta_pp"]:
            overlay_window_tbl[c] = overlay_window_tbl[c].map(fmt_pct)

    overlay_overall = overlay_overall_df.iloc[0].to_dict() if not overlay_overall_df.empty else {}

    overlay_trade_corr = np.nan
    overlay_trade_diag_df = pd.DataFrame()
    if not overlay_window_df.empty:
        overlay_trade_corr = float(overlay_window_df["trade_delta"].corr(overlay_window_df["net20_delta_pp"]))
        diag = overlay_window_df.copy()
        diag["trade_delta_bucket"] = pd.cut(
            diag["trade_delta"],
            bins=[-1, 44, 49, 10**9],
            labels=["<45", "45-49", ">=50"],
        )
        overlay_trade_diag_df = (
            diag.groupby("trade_delta_bucket", observed=False)
            .agg(
                windows=("trade_delta_bucket", "size"),
                overlay_better_net20_share=("overlay_better_net20", "mean"),
                median_net20_delta_pp=("net20_delta_pp", "median"),
                median_trade_delta=("trade_delta", "median"),
            )
            .reset_index()
        )

    if not overlay_trade_diag_df.empty:
        overlay_trade_diag_df.to_csv(ART_DIR / "ema60m_psar_exit_overlay_trade_delta_buckets.csv", index=False)

    overlay_trade_diag_tbl = overlay_trade_diag_df.copy()
    if not overlay_trade_diag_tbl.empty:
        overlay_trade_diag_tbl["windows"] = overlay_trade_diag_tbl["windows"].map(lambda x: str(int(x)))
        overlay_trade_diag_tbl["overlay_better_net20_share"] = overlay_trade_diag_tbl["overlay_better_net20_share"].map(lambda x: fmt_pct(x * 100.0))
        overlay_trade_diag_tbl["median_net20_delta_pp"] = overlay_trade_diag_tbl["median_net20_delta_pp"].map(fmt_pct)
        overlay_trade_diag_tbl["median_trade_delta"] = overlay_trade_diag_tbl["median_trade_delta"].map(lambda x: fmt_num(x, 0))

    helped = pair.sort_values("ema_minus_psar_pp", ascending=False).head(6).copy()
    hurt = pair.sort_values("ema_minus_psar_pp", ascending=True).head(6).copy()
    for d in [helped, hurt]:
        for c in ["ema_profit_pct", "psar_profit_pct", "ema_minus_psar_pp"]:
            d[c] = d[c].map(fmt_pct)
        for c in ["ema_trades", "psar_trades"]:
            d[c] = d[c].map(lambda x: str(int(x)))

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    html = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>EMA / PSAR Raw Alpha Focus Report</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background:#f8fafc; color:#0f172a; margin:0; padding:24px; }}
    .wrap {{ max-width: 1260px; margin: 0 auto; }}
    .card {{ background:white; border:1px solid #e2e8f0; border-radius:14px; padding:18px 20px; margin-bottom:18px; }}
    .muted {{ color:#475569; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eff6ff; color:#1d4ed8; font-size:12px; margin-right:6px; }}
    .q {{ font-weight:700; color:#0f172a; margin-top:2px; }}
    .a {{ color:#1e293b; margin-top:8px; }}
    .data-table {{ width:100%; border-collapse: collapse; font-size: 14px; }}
    .data-table th,.data-table td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    img {{ max-width:100%; border:1px solid #e2e8f0; border-radius:10px; }}
    code {{ background:#f1f5f9; padding:1px 4px; border-radius:6px; }}
    ul,ol {{ padding-left:20px; }}
    a {{ color:#2563eb; text-decoration:none; }}
  </style>
</head>
<body>
<div class=\"wrap\">
  <p><a href=\"../../index.html\">← 返回首页</a></p>

  <div class=\"card\">
    <h1>EMA / PSAR Raw Alpha Focus Report</h1>
    <p class=\"muted\">生成时间：{generated_at}</p>
    <p>
      <span class=\"pill\">raw alpha focus</span>
      <span class=\"pill\">EMA</span>
      <span class=\"pill\">PSAR</span>
      <span class=\"pill\">Q&A</span>
    </p>
    <p class=\"muted\">这页不再讨论 regime gate / MIHS / MIHCS，而是把视角收回到论文里的两个原始策略候选：<b>EMA</b> 和 <b>PSAR</b>。目标是回答：如果先不做趋势筛选，它们谁更值得继续追，为什么，收益从哪里来，代价又是什么。</p>
  </div>

  <div class=\"card\">
    <h2>先给结论</h2>
    <ul>
      <li><b>EMA 更像主 raw alpha baseline</b>：跨市场/跨频率更稳，胜场更多，适合继续当主干研究对象。</li>
      <li><b>PSAR 更像快反应 / loss-protection 候选</b>：也值得研究，但更适合作为第二原始策略，或后续与 EMA 组合。</li>
      <li>如果只在这篇论文的原始策略里选两个继续投资源，当前推荐顺序是：<b>EMA → PSAR</b>。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>收口定位：这条线现在该怎么读？</h2>
    <ul>
      <li><b>当前核心结论：</b><code>EMA</code> 应先被当成当前项目的 <b>raw alpha baseline candidate</b>；<code>PSAR</code> 则更像 <b>fast reaction / loss-protection candidate</b>。</li>
      <li><b>当前最强证据：</b>EMA 和 PSAR 的正收益覆盖率都很高（都约 <code>92.59%</code>），但 EMA 在 asset×freq 组合里拿第一的次数更多（<code>14</code> vs <code>8</code>），同时交易频率明显更低（median trades 约 <code>53</code> vs <code>113</code>），说明它更适合作为主 baseline；PSAR 的价值更像“更快反应”，而不是“更稳主干”。</li>
      <li><b>当前不支持什么结论：</b>这页还不支持把 <code>PSAR</code> 直接升成与 EMA 同等级的主 alpha，也不支持把 EMA / PSAR 任一条线直接包装成可实盘生产策略。</li>
      <li><b>当前更像什么角色：</b>EMA = <b>main alpha / raw baseline</b>；PSAR = <b>secondary alpha / protective layer</b>。</li>
      <li><b>下一步最值得做什么：</b>先补 EMA 的成本 / rolling / OOS honesty；再单独做 PSAR 的角色审计与交易频率敏感性，最后只做一版最小 <code>EMA + PSAR</code> 组合研究。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>先把交易逻辑讲清楚：这页到底在回测什么？</h2>
    <p class=\"a\">这页做的是 <b>raw alpha focus</b>，意思是：先不加趋势状态门控、也不加额外过滤器，只看策略本身最基础的信号能不能工作。还有一个很重要的前提：<b>这页的回测是 long-only</b>，也就是只有 <code>BUY=开多</code>、<code>SELL=平多</code>，没有做空。</p>
    <ul>
      <li><b>前置条件：</b>没有额外 regime filter，没有外部确认器，没有附加结构条件。</li>
      <li><b>执行方式：</b>每根 bar 算一次信号；空仓时看到 <code>BUY</code> 才开仓；持仓时看到 <code>SELL</code> 才平仓。</li>
      <li><b>如果空仓时出现 SELL：</b>什么都不做，因为这页不是做空系统。</li>
      <li><b>如果持仓时再次出现 BUY：</b>也什么都不做，因为已经在仓里了。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>EMA：普通人也能看懂的基础交易逻辑</h2>
    <p class=\"a\">你可以把 EMA 策略理解成：<b>看两条“平滑过的价格线”谁在上面</b>。短线更快的 EMA9 在上面，说明最近价格更强，就给 <code>BUY</code>；短线 EMA9 在下面，说明最近价格转弱，就给 <code>SELL</code>。</p>
    <ul>
      <li><b>使用的信号：</b><code>EMA9</code> 和 <code>EMA20</code></li>
      <li><b>开仓条件：</b><code>EMA9 &gt; EMA20</code>，且当前还没有持仓 → 开多</li>
      <li><b>平仓条件：</b><code>EMA9 &lt; EMA20</code>，且当前已经持仓 → 平多</li>
      <li><b>有没有过滤器：</b>这页里 <b>没有</b>。只看这两条 EMA 的相对位置。</li>
      <li><b>普通话解释：</b>短期趋势明显强于中期趋势时进场；短期趋势掉到中期趋势下面时离场。</li>
      <li><b>优点：</b>规则简单，方向感强，容易跨市场迁移。</li>
      <li><b>缺点：</b>会慢半拍，震荡时容易来回打脸。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>PSAR：普通人也能看懂的基础交易逻辑</h2>
    <p class=\"a\">你可以把 PSAR 策略理解成：<b>先看一个“跟踪点”是不是已经翻到价格下面，再看价格有没有真的往上冲出去</b>。只有两件事都发生了，它才给 <code>BUY</code>；反过来，如果跟踪点跑到价格上面，而且价格又往下跌破前一根低点，就给 <code>SELL</code>。</p>
    <ul>
      <li><b>使用的信号：</b><code>PSAR(0.02 ~ 0.2)</code> + 当前 bar 对前一根高/低点的突破</li>
      <li><b>开仓条件：</b><code>PSAR ≤ 收盘价</code>，并且 <code>当根最高价 &gt; 前一根最高价</code>，且当前空仓 → 开多</li>
      <li><b>平仓条件：</b><code>PSAR &gt; 收盘价</code>，并且 <code>当根最低价 &lt; 前一根最低价</code>，且当前持仓 → 平多</li>
      <li><b>有没有过滤器：</b>这页里 <b>没有</b>。只看 PSAR 和价格/前高前低的关系。</li>
      <li><b>普通话解释：</b>它不是看到“好像转强”就买，而是要同时看到“方向翻上来”+“价格真的冲过前高”；卖出也是同理，要同时看到“方向翻弱”+“价格真的跌破前低”。</li>
      <li><b>优点：</b>反应快，对转折更敏感。</li>
      <li><b>缺点：</b>更容易频繁交易，信号更碎。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>EMA 和 PSAR 的差别，最简版怎么记？</h2>
    <ul>
      <li><b>EMA：</b>更像“慢一点，但更稳一点”的趋势跟随。</li>
      <li><b>PSAR：</b>更像“快一点，但更容易抖”的转折跟随。</li>
      <li><b>EMA 更适合什么时候：</b>你更想先抓住大方向，不急着抢最早那一下。</li>
      <li><b>PSAR 更适合什么时候：</b>你更想快一点发现转向，愿意接受更高交易频率。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>Q1. 为什么只把 EMA 和 PSAR 拿出来继续看？</h2>
    <p class=\"a\">因为在这次跨市场 × 多频率的 unfiltered 回测里，它们是四个原始策略里最像“可继续研究的 raw alpha”那两个：收益中位数更高、正收益覆盖率更高、并且在 asset×freq 组合里拿第一的次数明显更多。</p>
    {html_table(base_tbl, ["strategy", "combos", "mean_profit_pct", "median_profit_pct", "positive_ratio", "median_trades", "winner_count"])}
    <p><img src=\"../../../artifacts/ema_psar_raw_alpha/01_base_strategy_median_bar.png\" alt=\"base strategy median\" /></p>
  </div>

  <div class=\"card\">
    <h2>Q2. EMA 的策略逻辑到底是什么？为什么它值得当主 baseline？</h2>
    <p class=\"a\">论文里的 EMA 原始策略很简单：<code>EMA9 &gt; EMA20 → BUY</code>，<code>EMA9 &lt; EMA20 → SELL</code>。它的优点不是“神奇”，而是足够朴素：本质上是在追随中期趋势，而不是赌均值回归或局部震荡。对你现在“先找靠谱 alpha”的目标来说，这种结构更像一个可扩展母体。</p>
    <ul>
      <li>优点：跨市场可迁移性好，解释成本低，后续容易叠加结构过滤或风险控制。</li>
      <li>缺点：会滞后，强震荡环境容易被来回打脸。</li>
      <li>更适合扮演的角色：<b>raw trend alpha baseline</b>。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>Q3. PSAR 的策略逻辑到底是什么？为什么它排第二？</h2>
    <p class=\"a\">论文里的 PSAR 策略本质是在用一个更快、更敏感的 stop-and-reverse 机制判断价格是否转向。它会更早反应，所以更像快速趋势 / 保护性策略，而不像 EMA 那样是稳定的趋势骨架。</p>
    <ul>
      <li>优点：反应快，对下跌/反转更敏感。</li>
      <li>缺点：交易次数通常更多，容易把趋势做得更碎。</li>
      <li>更适合扮演的角色：<b>fast reaction alpha / loss-protection layer</b>。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>Q4. 从数据上看，EMA 和 PSAR 谁更强？</h2>
    <p class=\"a\">整体上 EMA 更像第一选择，PSAR 是很强的第二选择。EMA 在 27 个 asset×freq 组合里拿了更多第一；PSAR 也很强，但更像“快而碎”的第二策略。</p>
    {html_table(focus_tbl, ["strategy", "combos", "mean_profit_pct", "median_profit_pct", "positive_ratio", "mean_trades", "median_trades", "mean_cagr_pct", "median_max_dd_pct"])}
    <p><img src=\"../../../artifacts/ema_psar_raw_alpha/02_ema_psar_head_to_head_scatter.png\" alt=\"ema vs psar scatter\" /></p>
    <p><img src=\"../../../artifacts/ema_psar_raw_alpha/05_profit_vs_trades.png\" alt=\"profit vs trades\" /></p>
    <ul>
      <li>如果一个点落在散点图对角线上方，表示那组样本里 <b>EMA 比 PSAR 更赚</b>。</li>
      <li>Profit vs trades 图则帮助你看清一个很关键的现实：<b>PSAR 往往不是不赚钱，而是更依赖更高交易频率去换收益。</b></li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>Q5. 它们分别在什么市场 / 频率更强？</h2>
    <p class=\"a\">EMA 和 PSAR 都不是只在一个市场有效，但风格不同：EMA 更像普适趋势骨架；PSAR 在某些更需要快速反应的场景里会更占优。</p>
    {html_table(class_freq_tbl, ["strategy", "asset_class", "freq", "combos", "mean_profit_pct", "median_profit_pct", "positive_ratio", "median_trades"])}
    <p><img src=\"../../../artifacts/ema_psar_raw_alpha/04_ema_psar_class_freq_heatmaps.png\" alt=\"class freq heatmaps\" /></p>
    <p><img src=\"../../../artifacts/ema_psar_raw_alpha/03_ema_psar_delta_heatmap.png\" alt=\"delta heatmap\" /></p>
    <ul>
      <li>绿色表示 <b>EMA 比 PSAR 更强</b>；红色表示 <b>PSAR 更强</b>。</li>
      <li>你可以把这张图直接当成“后续研究资源怎么分配”的地图。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>Q6. 在论文窗口（BTC 日频 2018-2022）里，它们的效果是什么样？</h2>
    <p class=\"a\">如果只看论文原始样本窗口，EMA 的 clean-room 复现值与论文很接近；PSAR 则与论文差异较大，说明 PSAR 分支对实现细节更敏感。这进一步支持一个判断：<b>EMA 更适合先作为主 baseline 推进；PSAR 则值得继续做忠实复核和组合研究。</b></p>
    {html_table(paper_tbl, ["strategy", "profit_pct", "np_pct", "nt", "cagr_pct", "max_dd_pct"])}
    <p><img src=\"../../../artifacts/ema_psar_raw_alpha/06_btc_ema_psar_equity.png\" alt=\"btc equity\" /></p>
  </div>

  <div class=\"card\">
    <h2>Q7. 哪些样本里 EMA 明显更值得追？哪些样本里 PSAR 更像赢家？</h2>
    <h3>EMA 明显更强的组合</h3>
    {html_table(helped, ["asset_label", "asset_class", "freq", "ema_profit_pct", "psar_profit_pct", "ema_minus_psar_pp", "ema_trades", "psar_trades"])}
    <h3>PSAR 明显更强的组合</h3>
    {html_table(hurt, ["asset_label", "asset_class", "freq", "ema_profit_pct", "psar_profit_pct", "ema_minus_psar_pp", "ema_trades", "psar_trades"])}
  </div>

  <div class=\"card\">
    <h2>Q8. 这对你后面的研究决策意味着什么？</h2>
    <ol>
      <li><b>EMA 先升格为主 raw alpha baseline</b>：后续你要评估新结构、过滤器、确认层时，都应该先问一句：它有没有稳定优于 EMA baseline？</li>
      <li><b>PSAR 作为第二重点保留</b>：但更适合往“快反应趋势 / 保护性退出 / 与 EMA 组合”方向推进，而不是直接压成主干。</li>
      <li><b>如果要做因子库 intake</b>：EMA 更像 alpha candidate；PSAR 更像 alpha/filter hybrid candidate。</li>
    </ol>
  </div>

  <div class=\"card\">
    <h2>Q9. 成本一扣之后，这两条线还站得住吗？</h2>
    <p class=\"a\">当前 first-pass 成本页的读法很清楚：<b>日/周频都还够厚，真正脆的是 60m，而且 PSAR 比 EMA 更脆。</b> 这不会推翻“EMA 比 PSAR 更像主 baseline”的结论，反而让这个排序更稳了。</p>
    <ul>
      <li><b>整体层面：</b>EMA / PSAR 的 gross 正收益覆盖率都约 <code>92.59%</code>，但 EMA 的 positive-only median breakeven round-trip cost 约 <code>383.2bps</code>，高于 PSAR 的约 <code>300.9bps</code>，说明 EMA 的成本缓冲更厚。</li>
      <li><b>60m 层面：</b>EMA 正 gross 组合的 median breakeven cost 约 <code>27.5bps</code>，扣 <code>20bps</code> 后仍约有 <code>4/9</code> 组合存活；PSAR 对应约 <code>15.4bps</code>，扣 <code>20bps</code> 后只剩约 <code>2/9</code>，到 <code>50bps</code> 时已 <code>0/9</code>。</li>
      <li><b>策略含义：</b>EMA 现在更像可以继续往 net / OOS / rolling 补完整性的主 baseline；PSAR 则更像适合拿来做快反应 / protective layer，而不是单独扛主 alpha 期待。</li>
    </ul>
    <h3>策略级成本空间摘要</h3>
    {html_table(cost_strategy_tbl, ["strategy", "combos", "positive_gross_share", "median_profit_pct", "median_trades", "positive_only_median_breakeven_cost_bps", "survive_10bps_share", "survive_20bps_share", "survive_50bps_share"])}
    <h3>按频率看成本敏感性</h3>
    {html_table(cost_freq_tbl, ["strategy", "interval", "combos", "positive_gross_share", "median_profit_pct", "median_trades", "positive_only_median_breakeven_cost_bps", "survive_10bps_share", "survive_20bps_share", "survive_50bps_share"])}
  </div>

  <div class=\"card\">
    <h2>Q10. 如果今天就要排研发优先级，EMA 和 PSAR 应该怎么投资源？</h2>
    <ul>
      <li><b>第一优先级：</b>继续投给 <code>EMA</code>，而且目标要收得很窄——不是再讲一遍它为什么好，而是补 <b>rolling / OOS honesty</b>，确认它不是只在长牛样本里好看。</li>
      <li><b>第二优先级：</b>不要单独把 <code>PSAR</code> 扩成第二条主 alpha 线，而是优先做最小 <code>EMA + PSAR</code> 组合验证，回答它当快退出 / protective layer 时，是否比单跑 EMA 更诚实。</li>
      <li><b>当前不建议做的事：</b>不建议现在就把 PSAR 当独立主策略继续包装；也不建议在 rolling / OOS 还没补之前，直接把 EMA 升格成 production baseline。</li>
      <li><b>更像 go / no-go gate 的读法：</b>如果 EMA 在下一轮 rolling / OOS 里还能保住大部分日/周频优势，它就有资格正式成为项目的 raw alpha baseline；如果这一步明显塌掉，那么这条线就该回退成“有启发的 research branch”，而不是主入口。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>Q11. 如果下一步真把 EMA 当主 baseline，rolling / OOS 应该怎么做才诚实？</h2>
    <p class=\"a\">当前最小诚实协议应该是：<b>固定 EMA9/EMA20，不再二次调参；把每个 asset×freq 组合切成 rolling / walk-forward 窗口；同时报告 gross 与低成本净值近似；再看它是否还能稳定活下来。</b> 这一步的目标不是再证明一次 EMA 在全样本里“看起来不错”，而是回答：它是不是一个值得后续所有结构层都拿来对比的 baseline。</p>
    <ul>
      <li><b>参数纪律：</b>固定现有 EMA 规则，不因为某个市场或频率表现差就临时改窗口长度。</li>
      <li><b>窗口纪律：</b>按 <code>asset × freq</code> 做 rolling / walk-forward 检查，优先关心“正收益窗口占比”与“坏窗口会不会连续扎堆”，而不是只看整段累计收益。</li>
      <li><b>成本纪律：</b>至少同时报告 <code>gross</code> 与一个现实一点的低成本口径（当前 first-pass 可先看 <code>20bps</code> 近似），避免只在无成本世界里成立。</li>
      <li><b>比较纪律：</b>不是只问 EMA 赚不赚钱，还要问它在 rolling / OOS 下是否仍比 <code>PSAR</code> 更像稳定主干，以及后续结构过滤层能否稳定优于这个 baseline。</li>
      <li><b>如果只先做一个最小切片：</b>优先先做 <code>EMA 60m</code> 的 <code>gross vs 20bps</code> rolling / walk-forward。原因不是它最漂亮，而是它现在最脆、最容易先把 baseline 幻觉打掉：first-pass 成本里，<code>EMA 60m</code> 的 positive-only median breakeven cost 约 <code>27.5bps</code>，扣 <code>20bps</code> 后只剩约 <code>4/9</code> 组合存活，所以它最适合先当 falsification slice。</li>
      <li><b>当前最像样的通过标准：</b>EMA 不需要在每个窗口都赢，但至少不该只靠少数大牛段抬起来；若 rolling 后大多数窗口仍为正、且 60m 没被轻微成本全面吞掉，它才更配叫 <code>raw alpha baseline candidate</code>。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>Q12. 如果要做最小 `EMA + PSAR` 组合，怎样才算诚实？</h2>
    <p class=\"a\">当前最小诚实版本不该把它做成“两个 alpha 拼盘”，而应先把问题收窄成：<b>`EMA` 负责主方向 / 主持仓逻辑，`PSAR` 只负责更快退出或保护性反应；然后拿它和单跑 EMA 在同一资产、同一频率、同一成本假设下正面对比。</b></p>
    <ul>
      <li><b>角色纪律：</b><code>EMA</code> 决定主方向与默认持有；<code>PSAR</code> 不单独抢主 alpha 位，只用来回答“更快退出会不会让 EMA 更诚实”。</li>
      <li><b>比较纪律：</b>组合版必须和 <code>单跑 EMA</code> 用同一组资产、同一频率、同一资金口径比，不能一边换 universe、一边换执行规则。</li>
      <li><b>成本纪律：</b>至少同时报告 <code>gross</code> 与 <code>20bps</code> 近似，因为 <code>PSAR</code> 的价值如果只存在于无成本世界，就不配叫 protective layer。</li>
      <li><b>默认第一刀：</b>优先先做 <code>EMA 60m + PSAR exit overlay</code> 对比 <code>单跑 EMA 60m</code>。理由不是它最稳，而是这里同时满足两点：<code>EMA 60m</code> 本来就最脆（扣 <code>20bps</code> 后只剩约 <code>4/9</code> 组合存活），而 <code>PSAR 60m</code> 又正是交易更快、最可能提供“更早止损 / 退出”价值、但也最容易被成本吞掉的地方。</li>
      <li><b>当前更像样的通过标准：</b>不是只看组合后 gross 收益有没有更高，而是看它是否在 <code>20bps</code> 下改善了坏窗口扎堆、回撤/误伤、或窗口存活率；如果只是换来更多交易次数，却没有更好的 cost-adjusted honesty，那它就不算组合增益。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>Q13. 真做一版 EMA 60m rolling falsification slice 后，现有缓存样本在说什么？</h2>
    <p class=\"a\">这轮不再只写协议，而是先用手头现成缓存交一个真实结果切片：复用 <code>pytrendline_event_validation_v3_crypto_180d/cache</code> 里的 <code>BTC / ETH / SOL</code> 60m 数据，固定 <code>EMA9/EMA20</code>，做 <code>45d rolling window + 15d step</code>，同时报告 <code>gross</code> 与 <code>20bps</code> 近似。它不是完整 cross-market 结论，但已经足够先回答：<b>EMA 60m 这块最脆口袋，到底像 pass / yellow / fail 哪一档。</b></p>
    <ul>
      <li><b>整体结果：</b>这批 cached crypto slice 一共 <code>{int(rolling_overall.get('windows', 0))}</code> 个窗口，gross 为正的只约 <code>{fmt_pct(float(rolling_overall.get('gross_positive_window_share', np.nan)) * 100.0)}</code>，扣 <code>20bps</code> 后只剩约 <code>{fmt_pct(float(rolling_overall.get('net20_positive_window_share', np.nan)) * 100.0)}</code> 为正；而且 <code>{int(rolling_overall.get('majority_net20_assets', 0))}/3</code> 个资产达到“多数窗口 net 为正”，当前门槛读法明显更接近 <b><code>{rolling_overall.get('gate', '-')}</code></b>。</li>
      <li><b>按资产看：</b><code>BTC / ETH / SOL</code> 的 median window net20 分别约 <code>{fmt_pct(rolling_asset_df.loc[rolling_asset_df['asset'].eq('BTC'), 'net20_median_profit_pct'].iloc[0]) if not rolling_asset_df.empty else '-'}</code>、<code>{fmt_pct(rolling_asset_df.loc[rolling_asset_df['asset'].eq('ETH'), 'net20_median_profit_pct'].iloc[0]) if not rolling_asset_df.empty else '-'}</code>、<code>{fmt_pct(rolling_asset_df.loc[rolling_asset_df['asset'].eq('SOL'), 'net20_median_profit_pct'].iloc[0]) if not rolling_asset_df.empty else '-'}</code>；三者都不是“轻成本还能多数窗口站住”的样子。</li>
      <li><b>更致命的点：</b>net20 的负窗口不是零星出现，而是会连续扎堆——当前 longest negative streak 分别大约是 <code>{rolling_asset_df.loc[rolling_asset_df['asset'].eq('BTC'), 'longest_net20_negative_streak'].iloc[0] if not rolling_asset_df.empty else '-'}</code>、<code>{rolling_asset_df.loc[rolling_asset_df['asset'].eq('ETH'), 'longest_net20_negative_streak'].iloc[0] if not rolling_asset_df.empty else '-'}</code>、<code>{rolling_asset_df.loc[rolling_asset_df['asset'].eq('SOL'), 'longest_net20_negative_streak'].iloc[0] if not rolling_asset_df.empty else '-'}</code> 个窗口，说明它不是靠一两个坏点，而是 recent slice 本身就很脆。</li>
      <li><b>当前最诚实的读法：</b>这不等于“EMA 全部作废”，因为它只是 <b>crypto-only / cached 180d / 60m</b> 的 first falsification slice；但它已经足够说明：<code>EMA 60m</code> 当前不能再被当成支持 baseline 的证据，反而更像需要被 <code>EMA + PSAR exit overlay</code> 去尝试救的最弱口袋。</li>
    </ul>
    <h3>按资产汇总</h3>
    {html_table(rolling_asset_tbl, ["asset", "windows", "gross_positive_window_share", "net20_positive_window_share", "gross_median_profit_pct", "net20_median_profit_pct", "worst_net20_window_pct", "longest_net20_negative_streak"])}
    <h3>最差窗口（按 net20）</h3>
    {html_table(rolling_window_tbl, ["asset", "window_start", "window_end", "bars", "trades", "gross_profit_pct", "net20_profit_pct"])}
  </div>

  <div class=\"card\">
    <h2>Q14. 真把 `EMA 60m + PSAR exit overlay` 落成结果切片后，它有救到这块最弱口袋吗？</h2>
    <p class=\"a\">这轮继续按同一批 <code>BTC / ETH / SOL</code> 60m cache、同样的 <code>45d window + 15d step</code>，把 <code>PSAR</code> 真正放进组合里，但只让它做一件事：<b>当 <code>EMA</code> 还没翻空时，若 <code>PSAR sell</code> 先出现，就提前退出。</b> 也就是：<code>EMA</code> 负责方向与默认持有，<code>PSAR</code> 只负责更快退出，不抢主 alpha 位。</p>
    <ul>
      <li><b>整体结果：</b>这批窗口里，<code>PSAR exit overlay</code> 只在 <code>{int(overlay_overall.get('overlay_better_net20_windows', 0))}/{int(overlay_overall.get('windows', 0))}</code> 个窗口里把 net20 做得比单跑 <code>EMA</code> 更好（约 <code>{fmt_pct(float(overlay_overall.get('overlay_better_net20_share', np.nan)) * 100.0)}</code>）；而 <code>EMA</code> 自己至少还有约 <code>{fmt_pct(float(overlay_overall.get('ema_net20_positive_window_share', np.nan)) * 100.0)}</code> 的窗口在 <code>20bps</code> 下为正，但 overlay 后直接变成约 <code>{fmt_pct(float(overlay_overall.get('overlay_net20_positive_window_share', np.nan)) * 100.0)}</code>。</li>
      <li><b>成本后的中位数变化：</b>整体 median window net20 delta 大约是 <code>{fmt_num(overlay_overall.get('median_net20_delta_pp'), 2)}pp</code>，而且 median trade delta 约 <code>+{fmt_num(overlay_overall.get('median_trade_delta'), 0)}</code> 笔，说明它更像是用大幅增交易次数换来了更差的 cost-adjusted 结果。</li>
      <li><b>按资产看：</b><code>BTC / ETH / SOL</code> 的 median net20 delta 大约分别是 <code>{fmt_pct(overlay_asset_df.loc[overlay_asset_df['asset'].eq('BTC'), 'median_net20_delta_pp'].iloc[0]) if not overlay_asset_df.empty else '-'}</code>、<code>{fmt_pct(overlay_asset_df.loc[overlay_asset_df['asset'].eq('ETH'), 'median_net20_delta_pp'].iloc[0]) if not overlay_asset_df.empty else '-'}</code>、<code>{fmt_pct(overlay_asset_df.loc[overlay_asset_df['asset'].eq('SOL'), 'median_net20_delta_pp'].iloc[0]) if not overlay_asset_df.empty else '-'}</code>；当前 <code>{int(overlay_overall.get('improving_assets', 0))}/3</code> 个资产出现“median delta 为正”，已经更接近“明显拖后腿”，而不是 rescue。</li>
      <li><b>当前最诚实的读法：</b>在这块最脆的 crypto 60m 口袋里，<code>PSAR</code> 现在还没有证明自己是能把 <code>EMA</code> 从 fail 边缘救回来的 protective layer；相反，它更像先把交易次数抬高了，但没有给出足够的 net 改善。</li>
    </ul>
    <h3>按资产汇总</h3>
    {html_table(overlay_asset_tbl, ["asset", "windows", "overlay_better_net20_share", "ema_net20_median_profit_pct", "overlay_net20_median_profit_pct", "median_net20_delta_pp", "worst_net20_delta_pp", "median_trade_delta"])}
    <h3>最差窗口（按 overlay net20 delta）</h3>
    {html_table(overlay_window_tbl, ["asset", "window_start", "window_end", "bars", "ema_trades", "overlay_trades", "trade_delta", "ema_net20_profit_pct", "overlay_net20_profit_pct", "net20_delta_pp"])}
  </div>

  <div class=\"card\">
    <h2>Q15. `PSAR exit overlay` 这次为什么更像是在放大交易次数，而不是在修复 EMA？</h2>
    <p class=\"a\">如果只看页面上一句“median trade delta 约 <code>+{fmt_num(overlay_overall.get('median_trade_delta'), 0)}</code> 笔、median net20 delta 约 <code>{fmt_num(overlay_overall.get('median_net20_delta_pp'), 2)}pp</code>”，还不够直观。更有用的读法是：<b>这批窗口里，overlay 越是明显抬高交易次数，净结果通常越差。</b></p>
    <ul>
      <li><b>整体相关性：</b><code>trade_delta</code> 与 <code>net20_delta</code> 的相关系数约 <code>{fmt_num(overlay_trade_corr, 2)}</code>，已经是明显负相关；换句话说，额外交易越多，cost-adjusted 改善通常越不容易出现。</li>
      <li><b>高换手窗口几乎没救到：</b>当 overlay 比单跑 EMA 多出至少 <code>50</code> 笔交易时，这类窗口约占 <code>{fmt_pct(((overlay_window_df['trade_delta'] >= 50).mean() * 100.0) if not overlay_window_df.empty else np.nan)}</code>，但 <code>0%</code> 窗口出现 net20 改善，中位 net20 delta 约 <code>{fmt_pct(overlay_trade_diag_df.loc[overlay_trade_diag_df['trade_delta_bucket'].astype(str).eq('>=50'), 'median_net20_delta_pp'].iloc[0]) if not overlay_trade_diag_df.empty and (overlay_trade_diag_df['trade_delta_bucket'].astype(str) == '>=50').any() else '-'}</code>。</li>
      <li><b>少加一点交易时，偶尔还能勉强改善：</b>如果额外交易还控制在 <code>&lt;45</code> 笔，这类窗口里约有 <code>{fmt_pct((overlay_trade_diag_df.loc[overlay_trade_diag_df['trade_delta_bucket'].astype(str).eq('<45'), 'overlay_better_net20_share'].iloc[0] * 100.0) if not overlay_trade_diag_df.empty and (overlay_trade_diag_df['trade_delta_bucket'].astype(str) == '<45').any() else np.nan)}</code> 能把 net20 做得更好，但中位 delta 仍约 <code>{fmt_pct(overlay_trade_diag_df.loc[overlay_trade_diag_df['trade_delta_bucket'].astype(str).eq('<45'), 'median_net20_delta_pp'].iloc[0]) if not overlay_trade_diag_df.empty and (overlay_trade_diag_df['trade_delta_bucket'].astype(str) == '<45').any() else '-'}</code>，说明它顶多是“少伤一点”，还不是稳定 rescue。</li>
      <li><b>当前最诚实的解释：</b><code>PSAR</code> 在这批 60m crypto cache 上，更多像是把 EMA 原本就不稳的区间切得更碎、更频繁出入；如果这些更快退出没有换来足够多的坏窗口修复，那成本就会先把它吃掉。</li>
    </ul>
    <h3>按 trade delta bucket 看 overlay 结果</h3>
    {html_table(overlay_trade_diag_tbl, ["trade_delta_bucket", "windows", "overlay_better_net20_share", "median_net20_delta_pp", "median_trade_delta"])}
  </div>

  <div class=\"card\">
    <h2>Q16. 如果明确把 60m 剔掉，EMA / PSAR 的 baseline family 还剩什么？</h2>
    <p class=\"a\">既然 <code>EMA 60m crypto</code> 已经被 rolling falsification slice 打进 fail 口袋，一个更有用的问题就变成：<b>若暂时不再纠缠 60m，日/周频这批更厚的组合里，`EMA / PSAR` 各自还剩下什么 baseline family survivors？</b> 这轮直接用现成 <code>ema_psar_cost_budget_by_combo.csv</code> 做一刀很窄的 survivors slice：只把 <code>1d + 1wk</code> 汇成一个 <code>non60m</code> 桶，与 <code>60m</code> 正面对照。</p>
    <ul>
      <li><b>EMA 的 non60m family 还很厚：</b><code>1d + 1wk</code> 共 <code>{int(baseline_family_df[(baseline_family_df['strategy'] == 'EMA') & (baseline_family_df['baseline_bucket'] == 'non60m (1d+1wk)')]['combos'].iloc[0]) if not baseline_family_df.empty else 0}</code> 个组合里，gross 正收益覆盖率仍是 <code>{fmt_pct(float(baseline_family_df[(baseline_family_df['strategy'] == 'EMA') & (baseline_family_df['baseline_bucket'] == 'non60m (1d+1wk)')]['positive_gross_share'].iloc[0]) * 100.0) if not baseline_family_df.empty else '-'}</code>；positive-only median breakeven cost 约 <code>{fmt_bps(baseline_family_df[(baseline_family_df['strategy'] == 'EMA') & (baseline_family_df['baseline_bucket'] == 'non60m (1d+1wk)')]['positive_only_median_breakeven_cost_bps'].iloc[0]) if not baseline_family_df.empty else '-'}</code>，扣 <code>20bps</code> 后仍是 <code>{fmt_pct(float(baseline_family_df[(baseline_family_df['strategy'] == 'EMA') & (baseline_family_df['baseline_bucket'] == 'non60m (1d+1wk)')]['survive_20bps_share'].iloc[0]) * 100.0) if not baseline_family_df.empty else '-'}</code> 存活。</li>
      <li><b>和 60m 的对比是断层级的：</b><code>EMA 60m</code> 的 positive-only median breakeven cost 只有约 <code>{fmt_bps(baseline_family_df[(baseline_family_df['strategy'] == 'EMA') & (baseline_family_df['baseline_bucket'] == '60m only')]['positive_only_median_breakeven_cost_bps'].iloc[0]) if not baseline_family_df.empty else '-'}</code>，<code>20bps</code> 后只剩约 <code>{fmt_pct(float(baseline_family_df[(baseline_family_df['strategy'] == 'EMA') & (baseline_family_df['baseline_bucket'] == '60m only')]['survive_20bps_share'].iloc[0]) * 100.0) if not baseline_family_df.empty else '-'}</code>；这说明“EMA 这条线还值不值得继续”与“EMA 60m 值不值得继续”已经不是同一个问题。</li>
      <li><b>PSAR 的 non60m 也活着，但更像副线对照：</b><code>PSAR</code> 的 non60m 组合同样是 <code>18/18</code> gross 为正、<code>20bps</code> 也 <code>18/18</code> 存活，但 positive-only median breakeven cost 大约只有 <code>{fmt_bps(baseline_family_df[(baseline_family_df['strategy'] == 'PSAR') & (baseline_family_df['baseline_bucket'] == 'non60m (1d+1wk)')]['positive_only_median_breakeven_cost_bps'].iloc[0]) if not baseline_family_df.empty else '-'}</code>，仍明显低于 EMA 的约 <code>{fmt_bps(baseline_family_df[(baseline_family_df['strategy'] == 'EMA') & (baseline_family_df['baseline_bucket'] == 'non60m (1d+1wk)')]['positive_only_median_breakeven_cost_bps'].iloc[0]) if not baseline_family_df.empty else '-'}</code>。</li>
      <li><b>当前更诚实的读法：</b>如果后面还要继续追 `raw alpha baseline family`，默认应该把注意力移到 <code>EMA 1d / 1wk</code> 这批厚口袋，而不是继续围着 <code>EMA 60m crypto</code> 打转；<code>PSAR</code> 则更适合作为 non60m 的次级对照 / protective layer 候选，而不是靠 60m overlay 去救场。</li>
    </ul>
    <h3>Baseline family survivors（non60m vs 60m）</h3>
    {html_table(baseline_family_tbl, ["strategy", "baseline_bucket", "combos", "positive_gross_share", "median_profit_pct", "median_trades", "positive_only_median_breakeven_cost_bps", "survive_20bps_share", "survive_50bps_share"])}
  </div>

  <div class=\"card\">
    <h2>Q17. 如果不想在 18 个 non60m 组合上平均用力，EMA family-level honesty 应该先看哪几个口袋？</h2>
    <p class=\"a\">既然当前更值得继续的是 <code>EMA 1d / 1wk</code> 这批 non60m family，一个更实用的问题就变成：<b>后面的 rolling / OOS 应该先看哪几个口袋，最能决定这条 family 还值不值得继续？</b> 当前最诚实的做法不是先去看最厚的 crypto 周频，而是先看 <b>non60m 里最薄、但还没正式倒下的 survivor frontier</b>。</p>
    <ul>
      <li><b>最薄的边界口袋已经很清楚：</b>当前排序最前的是 <code>{ema_non60m_queue_head[0]['asset'] if len(ema_non60m_queue_head) >= 1 else '-'}</code> <code>{ema_non60m_queue_head[0]['interval'] if len(ema_non60m_queue_head) >= 1 else '-'}</code>（breakeven 约 <code>{fmt_bps(ema_non60m_queue_head[0]['breakeven_roundtrip_cost_bps']) if len(ema_non60m_queue_head) >= 1 else '-'}</code>，<code>50bps</code> 近似下已约 <code>{fmt_pct(ema_non60m_queue_head[0]['approx_net_profit_pct_50bps']) if len(ema_non60m_queue_head) >= 1 else '-'}</code>），它其实已经接近“non60m family 里最先该被 falsify 的薄边”。</li>
      <li><b>接下来最值得优先复核的 frontier：</b><code>{ema_non60m_queue_head[1]['asset'] if len(ema_non60m_queue_head) >= 2 else '-'}</code> <code>{ema_non60m_queue_head[1]['interval'] if len(ema_non60m_queue_head) >= 2 else '-'}</code>（约 <code>{fmt_bps(ema_non60m_queue_head[1]['breakeven_roundtrip_cost_bps']) if len(ema_non60m_queue_head) >= 2 else '-'}</code>）、<code>{ema_non60m_queue_head[2]['asset'] if len(ema_non60m_queue_head) >= 3 else '-'}</code> <code>{ema_non60m_queue_head[2]['interval'] if len(ema_non60m_queue_head) >= 3 else '-'}</code>（约 <code>{fmt_bps(ema_non60m_queue_head[2]['breakeven_roundtrip_cost_bps']) if len(ema_non60m_queue_head) >= 3 else '-'}</code>）、<code>{ema_non60m_queue_head[3]['asset'] if len(ema_non60m_queue_head) >= 4 else '-'}</code> <code>{ema_non60m_queue_head[3]['interval'] if len(ema_non60m_queue_head) >= 4 else '-'}</code>（约 <code>{fmt_bps(ema_non60m_queue_head[3]['breakeven_roundtrip_cost_bps']) if len(ema_non60m_queue_head) >= 4 else '-'}</code>）、以及 <code>{ema_non60m_queue_head[4]['asset'] if len(ema_non60m_queue_head) >= 5 else '-'}</code> <code>{ema_non60m_queue_head[4]['interval'] if len(ema_non60m_queue_head) >= 5 else '-'}</code>（约 <code>{fmt_bps(ema_non60m_queue_head[4]['breakeven_roundtrip_cost_bps']) if len(ema_non60m_queue_head) >= 5 else '-'}</code>）。它们都还活着，但离“厚到不用优先怀疑”还很远。</li>
      <li><b>为什么不是先看最厚的 crypto 周频：</b><code>BTC / SOL 1wk</code> 这类口袋的 breakeven 已经厚到 <code>10k+ bps</code> 甚至更高，它们更像 family 还活着的 backstop，而不是当前最能决定“这条 family 需不需要继续收窄”的前线。</li>
      <li><b>当前最有用的 next step framing：</b>如果后面只做一刀 non60m 的 rolling / OOS honesty，默认应先从这批薄边 survivor frontier 开始；如果连它们都过不了，`EMA baseline family` 就该继续收窄，而不是再拿最厚的口袋给自己壮胆。</li>
    </ul>
    <h3>EMA non60m survivor frontier（按 breakeven 从薄到厚排序）</h3>
    {html_table(ema_non60m_queue_tbl, ["priority_rank", "asset", "asset_class", "interval", "trades", "breakeven_roundtrip_cost_bps", "approx_net_profit_pct_20bps", "approx_net_profit_pct_50bps", "max_dd_pct"])}
  </div>

  <div class=\"card\">
    <h2>Q18. 如果把这批 non60m 薄边 pocket 和 PSAR 正面对照，EMA 的 baseline family 还站得住吗？</h2>
    <p class=\"a\">光知道 frontier 排序还不够，下一步更关键的是：<b>这些最薄的 non60m pocket 里，EMA 还是不是默认更像 baseline 的那条线？</b> 这轮直接把 frontier 前 6 名拿去和同口径 <code>PSAR</code> 做 head-to-head，对读法会更诚实。</p>
    <ul>
      <li><b>EMA 明显更像 baseline 的口袋：</b><code>创业板ETF 1d</code>、<code>SPY 1d</code>、<code>QQQ 1d</code> 这三格里，EMA 不只是 gross 更高，连 breakeven cost buffer 也明显更厚——例如 <code>SPY 1d</code> 约比 PSAR 多出 <code>{fmt_bps(ema_frontier_h2h_head[4]['ema_minus_psar_breakeven_bps']) if len(ema_frontier_h2h_head) >= 5 else '-'}</code> 的缓冲，<code>QQQ 1d</code> 约多出 <code>{fmt_bps(ema_frontier_h2h_head[5]['ema_minus_psar_breakeven_bps']) if len(ema_frontier_h2h_head) >= 6 else '-'}</code>。</li>
      <li><b>真正更值得先做 rolling / OOS honesty 的，是 A股 frontier：</b><code>沪深300ETF 1wk</code> 与 <code>创业板ETF 1wk</code> 这两格里，PSAR 当前反而略占优；<code>沪深300ETF 1d</code> 则更像双方都偏薄、但 EMA 因交易更少而稍厚一点的 mixed pocket。</li>
      <li><b>项目级含义：</b>这说明 `EMA non60m family` 不是“所有 pocket 都同样支持 EMA baseline”。更诚实的读法是：<b>美股 1d pocket 仍在支持 EMA，但 A股 frontier 才是当前真正该先拿去验真伪的 family 前线。</b></li>
      <li><b>因此下一棒怎么收：</b>如果只做一刀 non60m 的更正式 honesty，默认不该平均撒在 18 个口袋上，而该优先去做 `沪深300ETF / 创业板ETF` 这批 frontier 的 rolling / OOS；因为它们最可能决定 `EMA baseline family` 是继续保留，还是要进一步收窄。</li>
    </ul>
    <h3>EMA non60m survivor frontier：与 PSAR 的同口径 head-to-head</h3>
    {html_table(ema_non60m_frontier_h2h_tbl, ["priority_rank", "asset", "asset_class", "interval", "ema_trades", "ema_breakeven_roundtrip_cost_bps", "psar_trades", "psar_breakeven_roundtrip_cost_bps", "ema_minus_psar_profit_pp", "ema_minus_psar_breakeven_bps", "reading"])}
  </div>

  <div class=\"card\">
    <h2>Q19. 真把 A股 frontier 推到第一刀 rolling / OOS honesty 后，EMA baseline family 还剩什么？</h2>
    <p class=\"a\">这轮不再只停在 `frontier queue` 或 `EMA vs PSAR` 静态 head-to-head，而是把最该先验真伪的 A股 frontier 直接推进到一版真实 rolling 切片：复用 `10y` 的 `沪深300ETF / 创业板ETF` 日周频数据，固定 `EMA9/EMA20`，做 `730d window + 180d step`，并用同口径 `PSAR` 做并排对照。它不是整条 non60m family 的最终判决，但已经足够回答：<b>A股 frontier 到底是在帮 EMA 守住 baseline family，还是在逼这条线继续收窄。</b></p>
    <ul>
      <li><b>整体结果是 mixed，不是全线塌掉：</b>当前一共 <code>{int(ashare_frontier_overall.get('windows', 0))}</code> 个窗口，`EMA` 的 net20 正窗口占比约 <code>{fmt_pct(float(ashare_frontier_overall.get('ema_net20_positive_window_share', np.nan)) * 100.0)}</code>，`PSAR` 约 <code>{fmt_pct(float(ashare_frontier_overall.get('psar_net20_positive_window_share', np.nan)) * 100.0)}</code>；两边都只有 <code>{int(ashare_frontier_overall.get('ema_majority_positive_pockets', 0))}/4</code> 与 <code>{int(ashare_frontier_overall.get('psar_majority_positive_pockets', 0))}/4</code> 个 pocket 达到“多数窗口 net 为正”，当前更像 <b><code>{ashare_frontier_overall.get('verdict', '-')}</code></b>，而不是“一边倒支持 EMA”或“一刀否掉 whole family”。</li>
      <li><b>EMA 仍守得住的口袋：</b><code>沪深300ETF 1d</code> 的 median window net20 约 <code>{fmt_pct(ashare_frontier_pocket_df.loc[(ashare_frontier_pocket_df['asset'].eq('沪深300ETF')) & (ashare_frontier_pocket_df['interval'].eq('1d')), 'ema_net20_median_profit_pct'].iloc[0]) if not ashare_frontier_pocket_df.empty else '-'}</code>，高于同口径 `PSAR` 的约 <code>{fmt_pct(ashare_frontier_pocket_df.loc[(ashare_frontier_pocket_df['asset'].eq('沪深300ETF')) & (ashare_frontier_pocket_df['interval'].eq('1d')), 'psar_net20_median_profit_pct'].iloc[0]) if not ashare_frontier_pocket_df.empty else '-'}</code>；<code>创业板ETF 1d</code> 虽然还没达到多数正窗口，但 median net20 也约 <code>{fmt_pct(ashare_frontier_pocket_df.loc[(ashare_frontier_pocket_df['asset'].eq('创业板ETF')) & (ashare_frontier_pocket_df['interval'].eq('1d')), 'ema_net20_median_profit_pct'].iloc[0]) if not ashare_frontier_pocket_df.empty else '-'}</code>，明显好于 `PSAR` 的约 <code>{fmt_pct(ashare_frontier_pocket_df.loc[(ashare_frontier_pocket_df['asset'].eq('创业板ETF')) & (ashare_frontier_pocket_df['interval'].eq('1d')), 'psar_net20_median_profit_pct'].iloc[0]) if not ashare_frontier_pocket_df.empty else '-'}</code>。</li>
      <li><b>真正该被继续收窄审查的，是 A股 weekly frontier：</b><code>创业板ETF 1wk</code> 这格里 `EMA` 的 median window net20 约 <code>{fmt_pct(ashare_frontier_pocket_df.loc[(ashare_frontier_pocket_df['asset'].eq('创业板ETF')) & (ashare_frontier_pocket_df['interval'].eq('1wk')), 'ema_net20_median_profit_pct'].iloc[0]) if not ashare_frontier_pocket_df.empty else '-'}</code>，而 `PSAR` 约 <code>{fmt_pct(ashare_frontier_pocket_df.loc[(ashare_frontier_pocket_df['asset'].eq('创业板ETF')) & (ashare_frontier_pocket_df['interval'].eq('1wk')), 'psar_net20_median_profit_pct'].iloc[0]) if not ashare_frontier_pocket_df.empty else '-'}</code>；<code>沪深300ETF 1wk</code> 则更像 mixed——`EMA` 的 median net20 约 <code>{fmt_pct(ashare_frontier_pocket_df.loc[(ashare_frontier_pocket_df['asset'].eq('沪深300ETF')) & (ashare_frontier_pocket_df['interval'].eq('1wk')), 'ema_net20_median_profit_pct'].iloc[0]) if not ashare_frontier_pocket_df.empty else '-'}</code>，但 `PSAR` 的正窗口占比更高（约 <code>{fmt_pct(float(ashare_frontier_pocket_df.loc[(ashare_frontier_pocket_df['asset'].eq('沪深300ETF')) & (ashare_frontier_pocket_df['interval'].eq('1wk')), 'psar_net20_positive_window_share'].iloc[0]) * 100.0) if not ashare_frontier_pocket_df.empty else '-'}</code>）。</li>
      <li><b>项目级含义：</b>`EMA baseline family` 还没有被 A股 frontier 直接打死，但它也不能再靠“non60m overall 18/18 存活”这种大桶口径自证。当前更诚实的读法是：<b>A股日频还在勉强帮 EMA 守门，真正最该先继续收窄的，是 A股 weekly frontier，尤其 `创业板ETF 1wk`。</b></li>
    </ul>
    <h3>A股 frontier rolling / OOS honesty（EMA vs PSAR, net20）</h3>
    {html_table(ashare_frontier_pocket_tbl, ["asset", "interval", "windows", "ema_net20_positive_window_share", "psar_net20_positive_window_share", "ema_net20_median_profit_pct", "psar_net20_median_profit_pct", "ema_vs_psar_median_net20_delta_pp", "ema_better_window_share", "reading"])}
  </div>

  <div class=\"card\">
    <h2>Q20. 如果把 A股 weekly frontier 再推进到更严格 holdout honesty，EMA 还该不该继续把它算进 baseline family？</h2>
    <p class=\"a\">这轮不再停在 overlap rolling，而是把最该先出结论的 <code>A股 weekly frontier</code> 单独推进到一版更严格的 holdout slice：固定 <code>EMA9/EMA20</code> 与 <code>PSAR</code> 规则，用 <code>730d lookback + 365d forward holdout</code>、按年滚动，直接看“下一年”是否还站得住。因为参数本来就是固定的，这一刀的意义不是训练，而是避免再让同一段样本一边提供背景、一边给自己打分。</p>
    <ul>
      <li><b>整体读法更偏向 PSAR-lean：</b>当前两格 weekly pocket 一共 <code>{int(ashare_weekly_holdout_overall.get('holdouts', 0))}</code> 个 holdout，`EMA` 的 net20 正 holdout 占比只约 <code>{fmt_pct(float(ashare_weekly_holdout_overall.get('ema_net20_positive_holdout_share', np.nan)) * 100.0)}</code>，而 `PSAR` 约 <code>{fmt_pct(float(ashare_weekly_holdout_overall.get('psar_net20_positive_holdout_share', np.nan)) * 100.0)}</code>；`EMA` 只在约 <code>{fmt_pct(float(ashare_weekly_holdout_overall.get('ema_better_holdout_share', np.nan)) * 100.0)}</code> 的 holdout 里优于 `PSAR`，当前整体更像 <b><code>{ashare_weekly_holdout_overall.get('verdict', '-')}</code></b>，而不是 EMA 还能把 weekly frontier 一并守住。</li>
      <li><b>创业板ETF 1wk：</b>在更严格 holdout 下已经很难继续替 `EMA baseline family` 辩护——`EMA` 的正 holdout 占比只约 <code>{fmt_pct(float(ashare_weekly_holdout_pocket_df.loc[ashare_weekly_holdout_pocket_df['asset'].eq('创业板ETF'), 'ema_net20_positive_holdout_share'].iloc[0]) * 100.0) if not ashare_weekly_holdout_pocket_df.empty else '-'}</code>，median net20 约 <code>{fmt_pct(ashare_weekly_holdout_pocket_df.loc[ashare_weekly_holdout_pocket_df['asset'].eq('创业板ETF'), 'ema_net20_median_profit_pct'].iloc[0]) if not ashare_weekly_holdout_pocket_df.empty else '-'}</code>；而 `PSAR` 对应约 <code>{fmt_pct(float(ashare_weekly_holdout_pocket_df.loc[ashare_weekly_holdout_pocket_df['asset'].eq('创业板ETF'), 'psar_net20_positive_holdout_share'].iloc[0]) * 100.0) if not ashare_weekly_holdout_pocket_df.empty else '-'}</code> 与 <code>{fmt_pct(ashare_weekly_holdout_pocket_df.loc[ashare_weekly_holdout_pocket_df['asset'].eq('创业板ETF'), 'psar_net20_median_profit_pct'].iloc[0]) if not ashare_weekly_holdout_pocket_df.empty else '-'}</code>。这格当前更像应从 `EMA baseline family pocket` 里剔出去，至少降级成 `PSAR/mixed pocket`。</li>
      <li><b>沪深300ETF 1wk：</b>也不再只是“mixed 但 EMA 勉强还行”。更严格 holdout 下，`EMA` 的正 holdout 占比约 <code>{fmt_pct(float(ashare_weekly_holdout_pocket_df.loc[ashare_weekly_holdout_pocket_df['asset'].eq('沪深300ETF'), 'ema_net20_positive_holdout_share'].iloc[0]) * 100.0) if not ashare_weekly_holdout_pocket_df.empty else '-'}</code>，median net20 约 <code>{fmt_pct(ashare_weekly_holdout_pocket_df.loc[ashare_weekly_holdout_pocket_df['asset'].eq('沪深300ETF'), 'ema_net20_median_profit_pct'].iloc[0]) if not ashare_weekly_holdout_pocket_df.empty else '-'}</code>；而 `PSAR` 对应约 <code>{fmt_pct(float(ashare_weekly_holdout_pocket_df.loc[ashare_weekly_holdout_pocket_df['asset'].eq('沪深300ETF'), 'psar_net20_positive_holdout_share'].iloc[0]) * 100.0) if not ashare_weekly_holdout_pocket_df.empty else '-'}</code> 与 <code>{fmt_pct(ashare_weekly_holdout_pocket_df.loc[ashare_weekly_holdout_pocket_df['asset'].eq('沪深300ETF'), 'psar_net20_median_profit_pct'].iloc[0]) if not ashare_weekly_holdout_pocket_df.empty else '-'}</code>。它现在更像 `mixed but PSAR-lean`，不再适合继续算作 EMA 的稳定支撑口袋。</li>
      <li><b>项目级含义：</b>这刀不会推翻 `EMA` 在日频 survivor 上的资格，但它已经足够把 <b>A股 weekly frontier 从 `EMA baseline family` 里继续收窄出去</b>。如果还要继续讲 EMA family，更诚实的口径应该变成：`A股 daily` 仍可保留观察，`A股 weekly` 目前更像 `PSAR/mixed branch`，而不是 EMA 的支持证据。</li>
    </ul>
    <h3>A股 weekly frontier strict holdout（EMA vs PSAR, net20）</h3>
    {html_table(ashare_weekly_holdout_tbl, ["asset", "holdouts", "ema_net20_positive_holdout_share", "psar_net20_positive_holdout_share", "ema_net20_median_profit_pct", "psar_net20_median_profit_pct", "ema_vs_psar_median_net20_delta_pp", "ema_better_holdout_share", "reading"])}
  </div>

  <div class=\"card\">
    <h2>Q21. 如果把 A股 daily 也推进到 strict holdout，EMA baseline family 还剩什么？</h2>
    <p class=\"a\">weekly frontier 已经被更严格 holdout 收窄成 `PSAR/mixed branch`，所以这轮继续把 `A股 daily` 用同样更严格的口径走一遍：固定 <code>EMA9/EMA20</code> 与 <code>PSAR</code>，用 <code>730d lookback + 365d forward holdout</code>、按年滚动，只看下一年。它的意义很直接——不是再证明 EMA 在某些历史片段里“总体还行”，而是回答：<b>如果把 A股 weekly 拿掉后，daily pockets 还能不能继续替 `EMA baseline family` 守门。</b></p>
    <ul>
      <li><b>整体读法更偏向 EMA-lean：</b>当前两格 daily pocket 一共 <code>{int(ashare_daily_holdout_overall.get('holdouts', 0))}</code> 个 holdout，`EMA` 的 net20 正 holdout 占比约 <code>{fmt_pct(float(ashare_daily_holdout_overall.get('ema_net20_positive_holdout_share', np.nan)) * 100.0)}</code>，高于 `PSAR` 的约 <code>{fmt_pct(float(ashare_daily_holdout_overall.get('psar_net20_positive_holdout_share', np.nan)) * 100.0)}</code>；`EMA` 也在约 <code>{fmt_pct(float(ashare_daily_holdout_overall.get('ema_better_holdout_share', np.nan)) * 100.0)}</code> 的 holdout 里跑赢 `PSAR`，当前整体更像 <b><code>{ashare_daily_holdout_overall.get('verdict', '-')}</code></b>。</li>
      <li><b>创业板ETF 1d：</b>现在仍是 `EMA daily pocket` 里最像样的一格——`EMA` 的正 holdout 占比约 <code>{fmt_pct(float(ashare_daily_holdout_pocket_df.loc[ashare_daily_holdout_pocket_df['asset'].eq('创业板ETF'), 'ema_net20_positive_holdout_share'].iloc[0]) * 100.0) if not ashare_daily_holdout_pocket_df.empty else '-'}</code>，median net20 约 <code>{fmt_pct(ashare_daily_holdout_pocket_df.loc[ashare_daily_holdout_pocket_df['asset'].eq('创业板ETF'), 'ema_net20_median_profit_pct'].iloc[0]) if not ashare_daily_holdout_pocket_df.empty else '-'}</code>；对应 `PSAR` 约 <code>{fmt_pct(float(ashare_daily_holdout_pocket_df.loc[ashare_daily_holdout_pocket_df['asset'].eq('创业板ETF'), 'psar_net20_positive_holdout_share'].iloc[0]) * 100.0) if not ashare_daily_holdout_pocket_df.empty else '-'}</code> 与 <code>{fmt_pct(ashare_daily_holdout_pocket_df.loc[ashare_daily_holdout_pocket_df['asset'].eq('创业板ETF'), 'psar_net20_median_profit_pct'].iloc[0]) if not ashare_daily_holdout_pocket_df.empty else '-'}</code>。这格当前仍能继续替 EMA family 辩护。</li>
      <li><b>沪深300ETF 1d：</b>不算强，但比 weekly 诚实得多——`EMA` 的正 holdout 占比约 <code>{fmt_pct(float(ashare_daily_holdout_pocket_df.loc[ashare_daily_holdout_pocket_df['asset'].eq('沪深300ETF'), 'ema_net20_positive_holdout_share'].iloc[0]) * 100.0) if not ashare_daily_holdout_pocket_df.empty else '-'}</code>，median net20 约 <code>{fmt_pct(ashare_daily_holdout_pocket_df.loc[ashare_daily_holdout_pocket_df['asset'].eq('沪深300ETF'), 'ema_net20_median_profit_pct'].iloc[0]) if not ashare_daily_holdout_pocket_df.empty else '-'}</code>；虽然仍偏 mixed，但同格 `PSAR` 约 <code>{fmt_pct(ashare_daily_holdout_pocket_df.loc[ashare_daily_holdout_pocket_df['asset'].eq('沪深300ETF'), 'psar_net20_median_profit_pct'].iloc[0]) if not ashare_daily_holdout_pocket_df.empty else '-'}</code>，并没有形成像 weekly 那样的明显反超。</li>
      <li><b>项目级含义：</b>这刀之后，`EMA baseline family` 的更诚实说法已经能收成一句话：<b>`A股 weekly` 该移出 family，但 `A股 daily` 还可暂时保留，尤其 `创业板ETF 1d` 仍是能替 EMA 守门的 pocket。</b> 也就是说，这条线现在不是“EMA family 全灭”，而是已经被压缩成更窄、但还没被完全打死的 daily survivors。</li>
    </ul>
    <h3>A股 daily strict holdout（EMA vs PSAR, net20）</h3>
    {html_table(ashare_daily_holdout_tbl, ["asset", "holdouts", "ema_net20_positive_holdout_share", "psar_net20_positive_holdout_share", "ema_net20_median_profit_pct", "psar_net20_median_profit_pct", "ema_vs_psar_median_net20_delta_pp", "ema_better_holdout_share", "reading"])}
  </div>

  <div class="card">
    <h2>Q22. 把前面的结果压成一张 final survivor map 后，EMA baseline family 现在到底还剩什么？</h2>
    <p class="a">到这一步，`EMA / PSAR` 线最值钱的已经不是再补一个 protocol，而是把前面几刀真实结果收成一张更严格、可执行的 family 边界图：<b>哪些 pocket 还应继续保留在 `EMA baseline family`，哪些只能降级成 mixed / watch，哪些已经该明确移出。</b> 这里把 `60m crypto rolling fail`、`A股 daily/weekly strict holdout`、以及其余 non60m 厚口袋的长样本 cost/backstop 一起压进同一张 survivor map。</p>
    <ul>
      <li><b>明确移出的口袋已经固定：</b><code>{ema_final_survivor_map_lookup.get('Crypto 60m（BTC/ETH/SOL rolling）', {}).get('key_numbers', '-')}</code>；`沪深300ETF 1wk` 与 `创业板ETF 1wk` 当前也都应移出 `EMA family`，对应分别是 <code>{ema_final_survivor_map_lookup.get('沪深300ETF 1wk', {}).get('key_numbers', '-')}</code> 与 <code>{ema_final_survivor_map_lookup.get('创业板ETF 1wk', {}).get('key_numbers', '-')}</code>。</li>
      <li><b>当前最像样的 strict-holdout survivor 仍集中在 daily：</b><code>{ema_final_survivor_map_lookup.get('创业板ETF 1d', {}).get('key_numbers', '-')}</code>；`沪深300ETF 1d` 也还没像 weekly 那样倒向 PSAR，但更诚实的读法已是 <b>mixed / watch</b>，对应 <code>{ema_final_survivor_map_lookup.get('沪深300ETF 1d', {}).get('key_numbers', '-')}</code>。</li>
      <li><b>family 也不只剩 A股 daily 一口气：</b>`贵州茅台 1d+1wk`、`美股 1d+1wk`、`Crypto 1d+1wk` 这些非前线厚口袋当前仍可暂时保留，分别对应 <code>{ema_final_survivor_map_lookup.get('贵州茅台 1d+1wk', {}).get('key_numbers', '-')}</code>、<code>{ema_final_survivor_map_lookup.get('美股 1d+1wk（SPY/QQQ/AAPL）', {}).get('key_numbers', '-')}</code>、<code>{ema_final_survivor_map_lookup.get('Crypto 1d+1wk（BTC/ETH/SOL）', {}).get('key_numbers', '-')}</code>。更诚实的说法不是“EMA family 只剩 daily”，而是：<b>前线 survivors 已收窄到 daily / mixed pockets，但更远端的 non60m backstops 还在。</b></li>
      <li><b>因此这条线现在的 final boundary 已经可以写死：</b><b>`60m crypto` = fail pocket；`A股 weekly frontier` = remove / PSAR-lean；`沪深300ETF 1d` = mixed / watch；`创业板ETF 1d` + 其余更厚的 nonfrontier non60m pockets = keep。</b> 如果以后还继续 EMA 线，默认只该去挑战这些 remaining keep/watch pockets，而不是再把已移出的 weekly / 60m 口袋拿回来当 hopeful 证据。</li>
    </ul>
    <h3>EMA baseline family final survivor map</h3>
    {html_table(ema_final_survivor_map_tbl, ["pocket_scope", "evidence_tier", "current_label", "family_bucket", "key_numbers", "project_read"])}
  </div>

  <div class="card">
    <h2>Q23. 如果把 final survivor map 再压成 `paper-trading candidate spec`，今天该怎么部署 EMA baseline？</h2>
    <p class="a">只把 family 边界讲清楚还不够；如果当前目标是判断谁最接近 `paper trading / 伪实盘`，那还需要把 survivor map 再往前压一步，明确回答：<b>哪些 pocket 现在就能进入 EMA baseline 的 paper 范围，哪些只能 shadow 观察，哪些必须直接排除。</b> 这里的原则不是“谁看起来都还能活”，而是优先让 strict-holdout survivor 先上场，让厚 backstop 做 secondary batch，让 mixed pocket 只影子跟踪，让已失败口袋彻底退出。</p>
    <ul>
      <li><b>primary pilot：</b><code>创业板ETF 1d</code> 当前可直接进入 `EMA baseline paper pilot`，对应 <code>{ema_paper_candidate_spec_lookup.get('创业板ETF 1d', {}).get('evidence_anchor', '-')}</code>；这格是目前最像样的 strict-holdout daily survivor，适合作为 A股侧的主试点。</li>
      <li><b>secondary paper batch：</b><code>美股 1d+1wk</code>、<code>Crypto 1d+1wk</code>、<code>贵州茅台 1d+1wk</code> 当前都可进入 secondary baseline paper 批次，分别对应 <code>{ema_paper_candidate_spec_lookup.get('美股 1d+1wk（SPY/QQQ/AAPL）', {}).get('evidence_anchor', '-')}</code>、<code>{ema_paper_candidate_spec_lookup.get('Crypto 1d+1wk（BTC/ETH/SOL）', {}).get('evidence_anchor', '-')}</code>、<code>{ema_paper_candidate_spec_lookup.get('贵州茅台 1d+1wk', {}).get('evidence_anchor', '-')}</code>。更诚实的读法不是“它们已经和 strict holdout pocket 一样硬”，而是：这些是当前 family 里仍然足够厚、可以先拿来做跨市场 baseline shadow/paper 的 backstops。</li>
      <li><b>shadow only：</b><code>沪深300ETF 1d</code> 当前更适合只做 shadow watch，不并入正式 paper batch，原因是 <code>{ema_paper_candidate_spec_lookup.get('沪深300ETF 1d', {}).get('evidence_anchor', '-')}</code>；它比 weekly 诚实，但还不够厚，继续观察比直接 admission 更稳妥。</li>
      <li><b>hard exclude：</b><code>Crypto 60m</code>、<code>沪深300ETF 1wk</code>、<code>创业板ETF 1wk</code> 当前都应直接排除在 EMA baseline paper scope 外，分别对应 <code>{ema_paper_candidate_spec_lookup.get('Crypto 60m（BTC/ETH/SOL rolling）', {}).get('evidence_anchor', '-')}</code>、<code>{ema_paper_candidate_spec_lookup.get('沪深300ETF 1wk', {}).get('evidence_anchor', '-')}</code>、<code>{ema_paper_candidate_spec_lookup.get('创业板ETF 1wk', {}).get('evidence_anchor', '-')}</code>。这几格不是“先挂着看看”的问题，而是当前项目口径下已经不该再继续被当成 EMA baseline 的部署对象。</li>
      <li><b>PSAR 在这版 spec 里的位置：</b>仍然不是主 baseline pocket。更诚实的做法是：把 `PSAR` 继续留在 shadow comparator / protective hypothesis 位上，不和 EMA baseline batch 混成同一 admission 口径。</li>
    </ul>
    <h3>EMA paper-trading candidate spec</h3>
    {html_table(ema_paper_candidate_spec_tbl, ["admission_rank", "admission_bucket", "deployment_scope", "default_mode", "evidence_anchor", "why_now", "operating_note"])}
  </div>

  <div class="card">
    <h2>Q24. 如果今天真要开一版 EMA baseline paper，运行纪律应该怎么写？</h2>
    <p class="a">`paper-trading candidate spec` 只回答“谁进 scope”；要避免后面又把 mixed/watch 和 fail pocket 混回 baseline，还需要把 <b>怎么分账、什么条件下继续、什么条件下必须降级或停掉</b> 写死。这一步没有新增回测，而是把现有 survivor/admission 证据压成一版更可执行的 operating spec。</p>
    <ul>
      <li><b>primary pilot 必须单独记账：</b><code>创业板ETF 1d</code> 当前的运行纪律已明确成 <code>{ema_paper_operating_spec_lookup.get('创业板ETF 1d', {}).get('recording_rule', '-')}</code>；它继续留在 primary 的条件也写死为 <code>{ema_paper_operating_spec_lookup.get('创业板ETF 1d', {}).get('continue_rule', '-')}</code>。</li>
      <li><b>secondary batch 只当 backstop，不许稀释 primary 结果：</b><code>美股 1d+1wk</code>、<code>Crypto 1d+1wk</code>、<code>贵州茅台 1d+1wk</code> 当前都应按 market × freq 分开记账，核心纪律分别是 <code>{ema_paper_operating_spec_lookup.get('美股 1d+1wk（SPY/QQQ/AAPL）', {}).get('recording_rule', '-')}</code>、<code>{ema_paper_operating_spec_lookup.get('Crypto 1d+1wk（BTC/ETH/SOL）', {}).get('recording_rule', '-')}</code>、<code>{ema_paper_operating_spec_lookup.get('贵州茅台 1d+1wk', {}).get('recording_rule', '-')}</code>。如果后续 stricter honesty 把其中某格打回 mixed/watch，就应直接从 secondary 移出，而不是继续和 primary 合讲“EMA family 仍然很稳”。</li>
      <li><b>shadow 与 exclude 的纪律也要写死：</b><code>沪深300ETF 1d</code> 当前只能按 <code>{ema_paper_operating_spec_lookup.get('沪深300ETF 1d', {}).get('recording_rule', '-')}</code> 运行；而 <code>Crypto 60m</code>、<code>沪深300ETF 1wk</code>、<code>创业板ETF 1wk</code> 则保持 hard exclude——对应 stop 纪律分别是 <code>{ema_paper_operating_spec_lookup.get('Crypto 60m（BTC/ETH/SOL rolling）', {}).get('promotion_or_demotion_rule', '-')}</code>、<code>{ema_paper_operating_spec_lookup.get('沪深300ETF 1wk', {}).get('promotion_or_demotion_rule', '-')}</code>、<code>{ema_paper_operating_spec_lookup.get('创业板ETF 1wk', {}).get('promotion_or_demotion_rule', '-')}</code>。</li>
      <li><b>项目级含义：</b>这版 operating spec 的价值不是多一个 protocol 名词，而是把 EMA 线当前最接近部署的问题压成一句可执行的话：<b>primary / secondary / shadow / exclude 必须分开记账、分开讲，不允许再靠 family 汇总把 mixed 或 fail pocket 混回 baseline paper 叙事。</b></li>
    </ul>
    <h3>EMA baseline paper-trading operating spec</h3>
    {html_table(ema_paper_operating_spec_tbl, ["monitor_rank", "deployment_scope", "paper_track", "recording_rule", "continue_rule", "promotion_or_demotion_rule"])}
  </div>

  <div class="card">
    <h2>Q25. 如果只在 A股 daily 里给 EMA 一个 primary 和一个 shadow，沪深300ETF 1d 现在够不够升格？</h2>
    <p class="a">`candidate spec / operating spec` 已经把 <code>创业板ETF 1d</code> 定成 primary、把 <code>沪深300ETF 1d</code> 定成 shadow，但真正更接近 deployment 的问题还差最后一句：<b>这个 shadow pocket 现在到底是“快能升格”，还是“先别急着放进正式 paper batch”。</b> 这轮不新增回测，只把现有 strict-holdout 窗口压成一张很小的 promotion scorecard，用 5 个最小门槛来判断 A股 daily 两格口袋：<b>1) overall 正 holdout 占比 ≥ 62.5%；2) overall 跑赢 PSAR 占比 ≥ 62.5%；3) recent 3 个 holdout 至少 2/3 为正；4) 最新 holdout 为正；5) 最新 holdout 仍跑赢 PSAR。</b></p>
    <ul>
      <li><b>创业板ETF 1d：</b>当前约命中 <code>{ashare_daily_shadow_promotion_lookup.get('创业板ETF', {}).get('gate_hits', 0)}/5</code> 个 gate，overall 正 holdout 约 <code>{fmt_pct(float(ashare_daily_shadow_promotion_lookup.get('创业板ETF', {}).get('overall_ema_positive_holdout_share', np.nan)) * 100.0)}</code>、overall 跑赢 PSAR 约 <code>{fmt_pct(float(ashare_daily_shadow_promotion_lookup.get('创业板ETF', {}).get('overall_ema_beats_psar_share', np.nan)) * 100.0)}</code>，latest holdout net20 约 <code>{fmt_pct(ashare_daily_shadow_promotion_lookup.get('创业板ETF', {}).get('latest_holdout_net20_profit_pct', np.nan))}</code>。它当前最诚实的位置仍是 <b><code>keep_primary</code></b>。</li>
      <li><b>沪深300ETF 1d：</b>当前只约命中 <code>{ashare_daily_shadow_promotion_lookup.get('沪深300ETF', {}).get('gate_hits', 0)}/5</code> 个 gate——recent 3 个 holdout 里约有 <code>{fmt_pct(float(ashare_daily_shadow_promotion_lookup.get('沪深300ETF', {}).get('recent3_ema_positive_holdout_share', np.nan)) * 100.0)}</code> 为正，latest holdout net20 约 <code>{fmt_pct(ashare_daily_shadow_promotion_lookup.get('沪深300ETF', {}).get('latest_holdout_net20_profit_pct', np.nan))}</code>，也重新跑赢 PSAR 约 <code>{fmt_pct(ashare_daily_shadow_promotion_lookup.get('沪深300ETF', {}).get('latest_holdout_ema_minus_psar_net20_pp', np.nan))}</code>；但 overall 正 holdout 仍只有约 <code>{fmt_pct(float(ashare_daily_shadow_promotion_lookup.get('沪深300ETF', {}).get('overall_ema_positive_holdout_share', np.nan)) * 100.0)}</code>，overall 跑赢 PSAR 也只有约 <code>{fmt_pct(float(ashare_daily_shadow_promotion_lookup.get('沪深300ETF', {}).get('overall_ema_beats_psar_share', np.nan)) * 100.0)}</code>。这说明它更像 <b>recently improving，但还不够从 shadow 升格</b>。</li>
      <li><b>最重要的 deployment 含义：</b>如果 EMA 线下一刀只追一个 A股 daily pocket，默认不该再问“创业板ETF 与沪深300ETF 要不要一起升”；更诚实的做法是：<b>继续让 <code>创业板ETF 1d</code> 单独承担 primary，<code>沪深300ETF 1d</code> 只保留 `shadow promotion candidate` 身份。</b></li>
      <li><b>因此下一步最像样的 challenge：</b>不是重新讨论 whole family，而是继续盯 <code>沪深300ETF 1d</code> 能不能在下一轮更严格 holdout / forward slice 里把 <code>overall 50% / overall 50% beats-PSAR</code> 这两项补厚；如果补不厚，就该继续停在 shadow，而不是靠 recent 两个窗口好转就偷渡升格。</li>
    </ul>
    <h3>A股 daily shadow-promotion scorecard</h3>
    {html_table(ashare_daily_shadow_promotion_tbl, ["asset", "current_role", "holdouts", "overall_ema_positive_holdout_share", "overall_ema_beats_psar_share", "recent3_ema_positive_holdout_share", "recent3_ema_median_net20_profit_pct", "latest_holdout_net20_profit_pct", "latest_holdout_ema_minus_psar_net20_pp", "gate_hits", "promotion_verdict", "promotion_reading"])}
  </div>

  <div class="card">
    <h2>Q26. 如果明天就开始盯 EMA baseline paper，最小 monitoring board 应该长什么样？</h2>
    <p class="a">`candidate spec` 解决了“谁进 scope”，`operating spec` 解决了“怎么分账、怎么继续/降级”，`shadow-promotion scorecard` 解决了“沪深300ETF 1d 够不够升格”。但如果真的要开始伪实盘，还差最后一个 deployment-facing 压缩动作：<b>把这三张表并成一张最小 monitoring board，明确每个 pocket 今天属于 active / shadow / stoplist 中哪一档，平时该盯什么，不达标时该怎么处理。</b></p>
    <ul>
      <li><b>primary 现在只有一格：</b><code>创业板ETF 1d</code> 当前的 board 读法是 <code>{ema_paper_monitoring_board_lookup.get('创业板ETF 1d', {}).get('paper_status', '-')}</code>；它的 monitor focus 已压成 <code>{ema_paper_monitoring_board_lookup.get('创业板ETF 1d', {}).get('monitor_focus', '-')}</code>。</li>
      <li><b>secondary 仍是 backstop，不是稀释 primary 的缓冲垫：</b><code>美股 1d+1wk</code>、<code>Crypto 1d+1wk</code>、<code>贵州茅台 1d+1wk</code> 都统一压成 <code>{ema_paper_monitoring_board_lookup.get('美股 1d+1wk（SPY/QQQ/AAPL）', {}).get('paper_status', '-')}</code> / <code>{ema_paper_monitoring_board_lookup.get('Crypto 1d+1wk（BTC/ETH/SOL）', {}).get('paper_status', '-')}</code> / <code>{ema_paper_monitoring_board_lookup.get('贵州茅台 1d+1wk', {}).get('paper_status', '-')}</code>；它们真正该盯的是 <code>{ema_paper_monitoring_board_lookup.get('美股 1d+1wk（SPY/QQQ/AAPL）', {}).get('monitor_focus', '-')}</code>。</li>
      <li><b>shadow 现在只剩一个最该追的 pocket：</b><code>沪深300ETF 1d</code> 当前 board 读法已压成 <code>{ema_paper_monitoring_board_lookup.get('沪深300ETF 1d', {}).get('current_read', '-')}</code>；这也把下一刀该追的问题固定成：先补厚 overall，而不是再被 latest 单窗好转带偏。</li>
      <li><b>exclude 要明确当成 stoplist：</b><code>Crypto 60m</code>、<code>沪深300ETF 1wk</code>、<code>创业板ETF 1wk</code> 现在都统一压成 <code>exclude_stoplist</code>。更诚实的做法不是“继续挂着看看”，而是按 board 里的 <code>escalate_or_stop_if</code> 字段把 reopen 门槛写死。</li>
      <li><b>项目级含义：</b>这张 board 的价值不是再造一个 protocol 名词，而是把 EMA 线离 paper 最近的那部分真正压成一句执行话：<b>谁今天该 active、谁只 shadow、谁就是 stoplist，以及这些判断平时要盯哪几列。</b></li>
    </ul>
    <h3>EMA baseline paper-trading monitoring board</h3>
    {html_table(ema_paper_monitoring_board_tbl, ["review_rank", "deployment_scope", "paper_status", "evidence_anchor", "monitor_focus", "keep_running_if", "escalate_or_stop_if", "current_read"])}
  </div>

  <div class="card">
    <h2>Q27. 如果真的只追 `沪深300ETF 1d` 的 shadow-promotion honesty，最近两段真实 forward holdout 在说什么？</h2>
    <p class="a">前面的 `shadow-promotion scorecard` 还是偏 board 式压缩；如果要补一刀更像样的 <b>真实前瞻 / honesty</b> 证据，更该问：<b>把视角只收在最近两段已经发生的 strict forward holdout（约最近两年）里，`沪深300ETF 1d` 这个 shadow pocket 到底有没有表现得像“该升格”的对象。</b> 这里不新增下载，也不改参数，只复用现成 A 股 daily strict holdout，把最近 <code>2</code> 段 forward holdout 压成一张小审计表。</p>
    <ul>
      <li><b>创业板ETF 1d：</b>最近两段 forward holdout（<code>{ashare_daily_recent_forward_audit_lookup.get('创业板ETF', {}).get('forward_start', '-')}</code> → <code>{ashare_daily_recent_forward_audit_lookup.get('创业板ETF', {}).get('forward_end', '-')}</code>）下，EMA 累计 net20 约 <code>{fmt_pct(ashare_daily_recent_forward_audit_lookup.get('创业板ETF', {}).get('ema_tail_cum_net20_profit_pct', np.nan))}</code>，仍高于 PSAR 的约 <code>{fmt_pct(ashare_daily_recent_forward_audit_lookup.get('创业板ETF', {}).get('psar_tail_cum_net20_profit_pct', np.nan))}</code>，两段都为正，当前 recent-forward verdict 仍是 <b><code>{ashare_daily_recent_forward_audit_lookup.get('创业板ETF', {}).get('forward_honesty_verdict', '-')}</code></b>。</li>
      <li><b>沪深300ETF 1d：</b>最近两段 forward holdout（<code>{ashare_daily_recent_forward_audit_lookup.get('沪深300ETF', {}).get('forward_start', '-')}</code> → <code>{ashare_daily_recent_forward_audit_lookup.get('沪深300ETF', {}).get('forward_end', '-')}</code>）下，EMA 累计 net20 约 <code>{fmt_pct(ashare_daily_recent_forward_audit_lookup.get('沪深300ETF', {}).get('ema_tail_cum_net20_profit_pct', np.nan))}</code>，确实已经转正；但 PSAR 同期约 <code>{fmt_pct(ashare_daily_recent_forward_audit_lookup.get('沪深300ETF', {}).get('psar_tail_cum_net20_profit_pct', np.nan))}</code>，EMA 两年累计反而仍约落后 <code>{fmt_pct(abs(float(ashare_daily_recent_forward_audit_lookup.get('沪深300ETF', {}).get('tail_ema_minus_psar_cum_pp', np.nan))))}</code>，而且最近两段里只有 <code>{fmt_pct(float(ashare_daily_recent_forward_audit_lookup.get('沪深300ETF', {}).get('tail_ema_beats_psar_share', np.nan)) * 100.0)}</code> 跑赢 PSAR，最弱那段也只有约 <code>{fmt_pct(ashare_daily_recent_forward_audit_lookup.get('沪深300ETF', {}).get('tail_worst_ema_holdout_pct', np.nan))}</code>。</li>
      <li><b>最重要的 admission 读法：</b><code>沪深300ETF 1d</code> 现在可以写成 <b>recent-forward 已转正</b>，但还不能写成 <b>promotion honesty 已过线</b>。因为它并不是“最近两段都正，所以就该升格”——同一段真实 forward 里，它仍没有持续跑赢 PSAR，也还缺一段更厚、更不贴边的正 holdout 来证明这不是短暂回暖。</li>
      <li><b>因此这轮后的更诚实 verdict：</b><b>`沪深300ETF 1d = positive_but_not_promotable`</b>。这比之前单看 `3/5 gate` 更硬：现在不是泛泛地说“overall 还不够厚”，而是可以明确说——<b>连最近这两段真实 forward holdout 都还没把 promotion honesty 补够，所以它仍应停在 shadow watch。</b></li>
    </ul>
    <h3>A股 daily recent-forward honesty audit（latest 2 holdouts）</h3>
    {html_table(ashare_daily_recent_forward_audit_tbl, ["asset", "current_role", "tail_holdouts", "forward_start", "forward_end", "ema_tail_cum_net20_profit_pct", "psar_tail_cum_net20_profit_pct", "tail_ema_minus_psar_cum_pp", "tail_ema_positive_holdout_share", "tail_ema_beats_psar_share", "tail_worst_ema_holdout_pct", "forward_honesty_verdict", "forward_honesty_reading"])}
  </div>

  <div class="card">
    <h2>Q28. 如果今天真要把 EMA baseline 从 board 接成一版可执行 runbook，最小 shadow/paper 操作规则该怎么写？</h2>
    <p class="a">`candidate spec / operating spec / monitoring board` 还只是“该怎么看”的研究页；如果下一步真要进入 `paper trading / shadow run`，还需要把它们接成一版能日常执行的最小 runbook，明确回答：<b>数据从哪里来、什么时候刷新、账怎么记、什么时候升降级、什么时候立即暂停或回滚。</b> 这一刀不再新增回测，而是把现有 deployment-facing verdict 压成一张更接近真实运行的操作表。</p>
    <ul>
      <li><b>primary pilot 已经能写成单独 runbook：</b><code>创业板ETF 1d</code> 当前不再只是“closest to paper”的抽象判断，而是已经能压成 <code>{ema_paper_runbook_lookup.get('创业板ETF 1d', {}).get('runbook_status', '-')}</code>：数据源、日更节奏、单独记账规则、以及何时从 primary 降回 shadow 都已写清；最近两段真实 forward holdout 也仍支持 <code>{ashare_daily_recent_forward_audit_lookup.get('创业板ETF', {}).get('forward_honesty_verdict', '-')}</code>。</li>
      <li><b>secondary backstop 现在也终于有了“降回 shadow”的硬规则：</b><code>美股 1d+1wk</code>、<code>Crypto 1d+1wk</code>、<code>贵州茅台 1d+1wk</code> 不再只是挂在 monitoring board 上的 active 标签，而是都明确写成：<b>按 market × freq 分账，每周 review；只要任一单 pocket 连续转红或被更严格 honesty 打回 mixed/watch，就从 <code>active_secondary_backstop</code> 降回 shadow，不能继续拿同批别的 pocket 稀释。</b></li>
      <li><b>shadow pocket 的升格门槛也更硬了：</b><code>沪深300ETF 1d</code> 当前 runbook 继续写死为 <code>shadow_watch</code>。它要想升格，不只是 gate 从 <code>3/5</code> 补到更高，还必须同时满足 <b>overall 正 holdout 占比 ≥ 62.5%、overall 跑赢 PSAR 占比 ≥ 62.5%、且 recent-forward 不再落后 PSAR</b>；否则就继续停在 <code>positive_but_not_promotable</code>。</li>
      <li><b>exclude stoplist 也终于被写成操作规则，而不是口头结论：</b><code>沪深300ETF 1wk</code>、<code>创业板ETF 1wk</code>、<code>Crypto 60m</code> 现在统一进入 stoplist runbook——默认不做常规刷新，不进入日常 paper/shadow admission；只有新的、独立证据包真正 overturn 当前 holdout / rolling verdict，才允许 reopen。</li>
      <li><b>项目级含义：</b>EMA 这条线现在终于不只是“离 paper 最近”，而是已经补齐到一句更可执行的话：<b>先按这版 runbook 启动 `0` 真资金的 shadow / paper 账本，再用项目级 `promotion gate v1` 约束后面的 small-live 资格；在这之前，不要再扩近义 board 页面。</b></li>
    </ul>
    <h3>EMA baseline paper-trading runbook</h3>
    {html_table(ema_paper_runbook_tbl, ["runbook_rank", "deployment_scope", "runbook_status", "data_source", "refresh_frequency", "ledger_rule", "review_rule", "promote_or_demote_rule", "kill_switch_or_rollback", "current_runbook_read"])}
  </div>

  <div class="card">
    <h2>Q29. 如果明天就要启动 `0` 真资金的 shadow / paper 账本，day-0 checklist 与记账模板最小该长什么样？</h2>
    <p class="a">Q28 解决的是 runbook 层：谁能进、多久复核、什么时候升降级。真正启动前还差最后一小步：把这些规则压成 <b>day-0 kickoff checklist</b> 与 <b>ledger template</b>，确保第一天就不会把 pocket 混账、漏记 monitoring status、或把 kill switch 留在口头层。</p>
    <ul>
      <li><b>先冻结 scope roster，再开账：</b>primary / secondary / shadow / stoplist 四类口袋必须先分清，不能边跑边补边界。</li>
      <li><b>账本必须按 market × freq 分开：</b>尤其 `美股/crypto/贵州茅台 1d+1wk` 这批 secondary backstop，不能再混成一条“secondary 总曲线”稀释坏 pocket。</li>
      <li><b>review 不只记结果，还要记动作：</b><code>monitor_status</code> 与 <code>review_action</code> 是 day-0 就必须落表的字段，不然 promote / demote / rollback 之后都不可审计。</li>
      <li><b>data health 要进账本：</b>如果数据断流或字段缺失，正确动作不是“先继续观察”，而是直接记成暂停 / rollback。</li>
      <li><b>项目级含义：</b>到这一步，EMA 线离真正启动 paper/shadow 已经不差“再补一张 board”，而只差按同一张 checklist 与模板开始前瞻记账。</li>
    </ul>
    <h3>EMA paper/shadow day-0 kickoff checklist</h3>
    {html_table(ema_paper_kickoff_checklist_tbl, ["step_rank", "check_item", "when_to_do", "pass_if", "why_it_exists"])}
    <h3>EMA paper/shadow ledger template</h3>
    {html_table(ema_paper_ledger_template_tbl, ["field_order", "field_name", "fill_for", "update_cadence", "example_or_rule", "why_it_matters"])}
  </div>

  <div class="card">
    <h2>Q30. 如果今天就真开账，day-0 launch seed rows 应该先建哪几条？</h2>
    <p class="a">Q29 说明了“字段长什么样”；但真正启动时，最容易出错的不是字段设计，而是 <b>第一天到底该先建哪几条 ledger row</b>。因此这里把 runbook 再压成一张可直接照抄的 <b>day-0 launch seed</b>：先把需要存在的账本行建好，再开始前瞻刷新，避免把 `1d / 1wk`、`primary / secondary / shadow / stoplist` 混成一锅。</p>
    <ul>
      <li><b>primary 只有 1 条 seed：</b><code>创业板ETF 1d</code> 对应 <code>A股-1d / primary_paper</code>，它是当前唯一允许直接以 primary 口径开账的 EMA pocket。</li>
      <li><b>secondary 不是 3 条，而是 6 条：</b><code>美股 / Crypto / 贵州茅台</code> 这 3 组都必须拆成 <code>1d</code> 与 <code>1wk</code> 两条 seed row，防止把坏 pocket 混进“secondary 总曲线”。</li>
      <li><b>shadow 与 stoplist 也必须占位：</b><code>沪深300ETF 1d</code> 虽未 admission，但要有独立 <code>shadow_watch</code> seed；`沪深300ETF 1wk / 创业板ETF 1wk / Crypto 60m` 也要各有 1 条 <code>stoplist_reopen_only</code> 审计位，避免后续被误混回 baseline。</li>
      <li><b>总行数是固定的 launch roster：</b>当前 day-0 应先建 <b>11</b> 条 seed rows（primary `1` + secondary `6` + shadow `1` + stoplist `3`），然后才开始第一轮真实 refresh。</li>
      <li><b>项目级含义：</b>EMA 线现在不只知道“该怎么跑”，还知道“第一天具体要先建哪几行账本”；这比再补一层近义 board 更接近真正的 paper/shadow 启动。</li>
    </ul>
    <h3>EMA paper/shadow day-0 launch seed rows</h3>
    {html_table(ema_paper_day0_seed_rows_tbl, ["seed_rank", "deployment_scope", "ledger_book", "market_freq_book", "refresh_cadence", "signal_state", "position_state", "monitor_status", "review_action", "data_health", "seed_rule"])}
  </div>

  <div class="card">
    <h2>Q31. 如果 day-0 后第一轮 weekly review 真要执行，最小 red/yellow/green scorecard 应该怎么填？</h2>
    <p class="a">Q30 解决的是“第一天先建哪几行账”；但真正让 paper / shadow 像在运行的，不是 seed rows 本身，而是 <b>首个 weekly review 到底按什么标准判 green / yellow / red、以及判完之后具体该 keep / demote / stop 什么</b>。这轮不新增回测，而是把 runbook、monitoring board、day-0 账本再压成一张更执行型的首周 review scorecard，避免 `paper-ready` 还停留在概念层。</p>
    <ul>
      <li><b>primary 首周不是“先跑着看”：</b><code>创业板ETF 1d</code> 的 red 不是轻飘飘提醒，而是要直接 <code>demote_to_shadow</code>；yellow 也必须触发一次额外补充 review。</li>
      <li><b>secondary 首周最怕的仍是混账：</b><code>美股 / Crypto / 贵州茅台 1d+1wk</code> 这 6 条 row 必须逐个 <code>market × freq</code> 记账；red 是降对应 pocket，不是继续拿整批别的口袋遮盖。</li>
      <li><b>沪深300ETF 1d 首周也不该被 recent-positive 幻觉抬走：</b>它即便首周顺利，也默认仍是 <code>keep_shadow</code>，因为 promotion gate 不是靠一周顺眼就能过。</li>
      <li><b>stoplist 也有首周动作：</b>weekly frontier 与 crypto 60m 只要被误混回 active/shadow 汇报，就应立即 <code>rollback_to_stoplist_now</code>。</li>
      <li><b>项目级含义：</b>EMA 线现在不只知道怎么开账，也知道开账后一周内该怎样诚实地判继续、降级或回滚；这比再补一层近义 board 更接近真实 paper 运营。</li>
    </ul>
    <h3>EMA paper/shadow first weekly review scorecard</h3>
    {html_table(ema_paper_first_week_review_tbl, ["review_rank", "deployment_scope", "first_review_clock", "must_fill_fields", "green_if", "yellow_if", "red_if", "default_action", "why_it_matters"])}
  </div>

  <div class="card">
    <h2>Q32. 如果不再补近义 board，`active_secondary_backstop` 下一轮该先复核谁？</h2>
    <p class="a">到 Q31 为止，EMA 线的 paper/shadow 启动链条已经补齐（candidate / operating / monitoring / runbook / day-0 / week-1）。如果还要在这条线上补一刀 deployment-facing 的诚实推进，更合理的动作不是再写一层近义规范，而是把 <code>active_secondary_backstop</code> 压成一张可执行复核队列：<b>哪几格该先做 stricter honesty，哪几格暂时可放后。</b> 这轮不新增下载，直接复用现成 <code>ema_non60m_honesty_queue.csv</code> + operating spec 的降级规则。</p>
    <ul>
      <li><b>当前 first target 已固定：</b>若下一轮只能先查一格，默认先查 <code>{secondary_first_target}</code>（global honesty rank 最靠前、buffer 最薄）。</li>
      <li><b>队列已分成 3 档：</b><code>front / mid / back</code> 当前分别约为 <code>{secondary_front_count}</code> / <code>{secondary_mid_count}</code> / <code>{secondary_back_count}</code> 个 pocket。这样就不会再把 secondary batch 当一整坨“都挺稳”的口头结论。</li>
      <li><b>动作规则不再含糊：</b>每一格都绑定了对应 secondary group 的 <code>if_fail_then_action</code>，核心是同一条硬纪律：<b>任一 pocket 被更严格 honesty 打回 mixed/watch，就从 <code>active_secondary_backstop</code> 降回 shadow，不允许继续靠同组别的口袋遮盖。</b></li>
      <li><b>deployment 含义：</b>这张表不是“新 protocol 页面”，而是把 runbook 的 secondary 部分变成可排班执行的 recheck 队列。Jerry 现在可以直接判断：该不该继续给 secondary 批次配资源、先查哪里、查坏了怎么降级。</li>
    </ul>
    <h3>EMA active secondary backstop recheck queue</h3>
    {html_table(ema_secondary_backstop_recheck_tbl, ["recheck_rank", "global_honesty_rank", "secondary_group", "pocket_scope", "asset_class", "profit_pct", "trades", "breakeven_roundtrip_cost_bps", "approx_net_profit_pct_20bps", "recheck_bucket", "why_recheck_now", "if_fail_then_action"])}
  </div>

  <div class="card">
    <h2>Q33. 如果今天就真的把 `0` 真资金 shadow / paper 账本开出来，首份 day-0 ledger snapshot 应该长什么样？</h2>
    <p class="a">Q32 解决的是“secondary 下一步先查谁”；但当前 TODO 里真正还差的不是再补一层 board，而是 <b>把现有 `11` 条 day-0 seed rows 真落成首份前瞻账本快照</b>。所以这里直接把 primary / secondary / shadow / stoplist 的 launch roster 写成一张真实 snapshot：同一时刻冻结 scope，给每条 row 明确的 <code>monitor_status / review_action / data_health</code>，作为后续真实 refresh 的第 `0` 笔记录。</p>
    <ul>
      <li><b>这不是历史回填：</b>snapshot 只记录 day-0 当下该存在的 roster 与状态，不补任何事后 PnL；因此 active/shadow 仍统一停在 <code>flat / waiting first signal</code>。</li>
      <li><b>primary / secondary / shadow / stoplist 的 day-0 动作已分开：</b><code>创业板ETF 1d</code> 直接标成 <code>start_primary_paper</code>；secondary 会按 recheck 队列厚薄落成不同 kickoff 状态；<code>沪深300ETF 1d</code> 明确只记成 <code>stay_shadow_until_promotion_gate</code>；stoplist 则继续 <code>keep_excluded</code>。</li>
      <li><b>monitor_status 不再空着等以后想：</b>front-queue secondary 在 day-0 就先落成 <code>kickoff_yellow_front_queue</code>，等于提前承认“它能开账，但首轮就该优先复核”；这比事后再口头解释更诚实。</li>
      <li><b>data health 也真的落表：</b>active / shadow 账位当前统一先记成 <code>ok_scope_frozen</code>，stoplist 记成 <code>n_a_stoplist</code>；后续只要刷新断档，就能沿同一张账本继续写，不用再造新模板。</li>
      <li><b>项目级含义：</b>EMA 线现在已经从“paper-ready 文档”真正跨到“首笔 `0` 真资金 ledger 记录已落表”；下一步默认该继续做真实 forward refresh / week-1 review，而不是继续补近义 spec 页。</li>
    </ul>
    <h3>EMA paper/shadow day-0 ledger snapshot</h3>
    {html_table(ema_paper_day0_snapshot_tbl, ["snapshot_rank", "snapshot_clock_utc", "deployment_scope", "paper_status", "ledger_book", "market_freq_book", "signal_state", "position_state", "monitor_status", "review_action", "data_health", "first_review_clock", "day0_note"])}
  </div>

  <div class="card">
    <h2>Q34. 如果现在就要沿同一张账本继续跑，`day-0 snapshot` 之后的 first-refresh queue 该怎么排？</h2>
    <p class="a">Q33 把首份账本快照真正落表后，剩下最容易继续卡在口头层的就是：<b>第一轮 refresh / week-1 到底先做哪几步、谁先、谁后、谁只是审计位。</b> 这轮不再新增 board，而是把 <code>day-0 snapshot + first-week scorecard + secondary recheck queue</code> 直接压成一张可执行的 first-refresh queue，让后续 paper/shadow 不会又停在“理论上下一步该 refresh”的抽象句子里。</p>
    <ul>
      <li><b>第一优先级已写死：</b>默认先做 <code>{refresh_queue_first}</code> 的首刷；这不是因为它最热闹，而是因为它是唯一 primary pilot，最该先证明账本能沿同一张 ledger 继续跑。</li>
      <li><b>第二优先级不再含糊：</b><code>{refresh_queue_second}</code> 与 <code>{refresh_queue_third}</code> 被提前钉在前排，等于明确承认：front-queue secondary 虽然可以开账，但第一轮就该优先补 stricter honesty，而不是先被“secondary 总体还行”掩过去。</li>
      <li><b>shadow / stoplist 也被放回正确位置：</b><code>沪深300ETF 1d</code> 现在只配进 `refresh-only shadow lane`，而 stoplist 统一落到 `audit-only`；这样就不会把“有账位”误读成“都要同强度推进”。</li>
      <li><b>deployment 含义：</b>Jerry 现在不只知道 scope 已冻结，还知道下一轮真实 refresh 时，哪些行是必须先写的，哪些行出问题要直接 demote / rollback，哪些行只需要保持审计位。</li>
    </ul>
    <h3>EMA paper/shadow first-refresh queue</h3>
    {html_table(ema_paper_first_refresh_queue_tbl, ["queue_rank", "queue_bucket", "deployment_scope", "market_freq_book", "first_refresh_trigger", "immediate_action", "week1_focus", "if_ok_then", "if_fail_then", "why_now"])}
  </div>

  <div class="card">
    <h2>Q35. 如果现在就沿同一张账本把 top-3 lanes 落成首份真实 refresh delta，第一笔会写出什么？</h2>
    <p class="a">Q34 已经把 first-refresh queue 排好，但如果还停在“下一步该怎么 refresh”，这条线就仍然卡在 protocol 层。更 deployment-facing 的做法，是直接把队首 3 条 lane 用 <b>最新已完成 bar</b> 写成首份真实 refresh delta：不假装已经等到了下一周，只把 day-0 当时故意留空的 <code>signal_state / position_state / review_action</code> 换成当前真实状态，让账本从抽象 roster 变成真正可续写的 ledger。</p>
    <ul>
      <li><b>primary 已经从“等待首刷”变成真实在跑：</b>{first_refresh_delta_first}</li>
      <li><b>front-queue secondary 的首刷也不再靠 family 叙事遮盖：</b>{first_refresh_delta_second}</li>
      <li><b>shadow lane 也被写实成“不升格就是不升格”：</b>{first_refresh_delta_third}</li>
      <li><b>deployment 含义：</b>Jerry 现在不只知道 queue 怎么排，还知道这 3 条最关键 lane 在同一张账本上的第一笔真实状态到底长什么样——哪个已经开出 long，哪个仍该 flat / stay shadow，哪个需要继续按 front-queue honesty 盯。</li>
    </ul>
    <h3>EMA paper/shadow top-3 first-refresh delta</h3>
    {html_table(ema_paper_first_refresh_delta_tbl, ["refresh_rank", "refresh_clock_utc", "deployment_scope", "market_freq_book", "tracked_members", "latest_completed_bar_utc", "data_source", "signal_state_before", "signal_state_after", "position_state_before", "position_state_after", "benchmark_psar_state", "open_unrealized_pct", "monitor_status_before", "monitor_status_after", "review_action_before", "review_action_after", "data_health_after", "delta_note"])}
  </div>

  <div class="card">
    <h2>Q35b. 如果把 top-3 首刷扩到全部 active `1d` lanes，今天这张 daily refresh snapshot 会告诉我们什么？</h2>
    <p class="a">Q35 只覆盖 queue top-3，足够证明“账本开始动了”；但如果要更接近日常 paper/shadow 运行，下一步要看的不是再补一层 board，而是 <b>同一天里全部 active `1d` lanes 的真实 refresh 状态</b>。这张 snapshot 直接回答：今天哪些 lane 真的有 live bar、哪些还在缓存 fallback、哪些已经开出 long、哪些仍 flat。</p>
    <ul>
      <li><b>primary lane：</b>{daily_refresh_primary_note}</li>
      <li><b>secondary 日频总览：</b>{daily_refresh_secondary_summary}</li>
      <li><b>shadow lane：</b>{daily_refresh_shadow_note}</li>
      <li><b>数据健康：</b>当前 `1d` active lanes 约 <code>{daily_refresh_live_count}</code> 条 live refresh、<code>{daily_refresh_fallback_count}</code> 条 cache fallback、<code>{daily_refresh_failed_count}</code> 条数据断流（需先修源）。</li>
      <li><b>仓位状态：</b>当前约 <code>{daily_refresh_long_count}</code> 条在 `long_open/mixed_open`，<code>{daily_refresh_flat_count}</code> 条仍是 flat。</li>
      <li><b>deployment 含义：</b>Jerry 现在能直接看见“这条线今天到底在不在跑”，而不需要再从 top-3 局部状态外推全盘。</li>
    </ul>
    <h3>EMA paper/shadow daily refresh snapshot（all active 1d lanes）</h3>
    {html_table(ema_paper_daily_refresh_snapshot_tbl, ["refresh_rank", "refresh_clock_utc", "deployment_scope", "paper_status", "market_freq_book", "tracked_members", "latest_completed_bar_utc", "data_source", "signal_state", "position_state", "benchmark_psar_state", "open_unrealized_pct", "monitor_status", "review_action", "data_health", "refresh_note"])}
  </div>

  <div class="card">
    <h2>Q35c. 如果把 active `1d` lanes 的 live/fallback 依赖也压成一张运行审计表，EMA 离更稳的 paper/shadow 还差什么？</h2>
    <p class="a">Q35b 已经告诉我们“今天在不在跑”，但 deployment 上真正更接近下一刀的问题是：<b>哪些 lane 只是 live，哪些 lane 仍然靠 fallback 勉强续写，资源顺序该先修哪里。</b> 这张 audit 不再新增 alpha 结论，而是把当前 all active `1d` lanes 的 source 依赖压成一张可执行表，避免继续在 runbook 近义层打转。</p>
    <ul>
      <li><b>primary blocker 已经收敛：</b>{refresh_dependency_primary_note}</li>
      <li><b>shadow fallback 继续留在正确位置：</b>{refresh_dependency_shadow_note}</li>
      <li><b>live secondary 现在更该盯 honesty，不是 source：</b>{refresh_dependency_live_summary}</li>
      <li><b>项目级读法：</b>{refresh_dependency_verdict}</li>
      <li><b>deployment 含义：</b>{refresh_dependency_deployment_line}</li>
    </ul>
    <h3>EMA paper/shadow refresh dependency audit</h3>
    {html_table(ema_paper_refresh_dependency_audit_tbl, ["dependency_rank", "deployment_scope", "paper_status", "market_freq_book", "data_source", "latest_completed_bar_utc", "data_health", "dependency_status", "ops_priority", "deployment_read", "next_action", "why_it_matters"])}
  </div>

  <div class="card">
    <h2>Q35d. 如果今天还没有新的已收盘日线，这张 live ledger 现在是在按时等下一次 close，还是已经 stale 掉了？</h2>
    <p class="a">Q35c 把 source-risk 先压掉以后，下一步最容易被误读的，是“现在没有新 refresh 结果”到底表示系统停了，还是只是周末 / 非收盘时段还没到下一根 completed bar。这张 on-clock audit 不去假装生成不存在的新 forward 结果，而是把 <b>下一次 close 在什么时候、首个 week-1 review 什么时候才真的到时、现在该等什么</b> 写成一张运行审计表。</p>
    <ul>
      <li><b>primary on-clock 读法：</b>{refresh_clock_primary_note}</li>
      <li><b>secondary / shadow 当前在等什么：</b>{refresh_clock_secondary_summary}</li>
      <li><b>week-1 review 节奏：</b>{refresh_clock_week1_line}</li>
      <li><b>项目级读法：</b>{refresh_clock_verdict}</li>
      <li><b>deployment 含义：</b>这一步的价值不是伪造一笔不存在的新 forward refresh，而是把“什么时候该刷、什么时候只是正常等待”写死，避免周末/非收盘时段把没新 bar 误判成 ledger 停转。</li>
    </ul>
    <h3>EMA paper/shadow refresh clock audit</h3>
    {html_table(ema_paper_refresh_clock_audit_tbl, ["clock_rank", "deployment_scope", "paper_status", "market_freq_book", "refresh_clock_utc", "latest_completed_bar_utc", "data_source", "clock_status", "next_expected_close_utc", "time_to_next_close", "week1_review_due_utc", "time_to_week1_review", "week1_status", "current_clock_read", "next_gate", "why_it_matters"])}
  </div>

  <div class="card">
    <h2>Q35e. 如果把 PSAR 快退出直接焊进当前 A股 daily 的 paper/shadow runbook，它真会让 admission 更诚实吗？</h2>
    <p class="a">Q35d 说明当前没新 completed bar 只是正常等时钟，不代表这轮没别的 deployment-facing 动作可做。更像样的一刀是直接回答：<b>既然 `创业板ETF 1d` 已经是 primary、`沪深300ETF 1d` 还在 shadow，那 PSAR 快退出要不要现在就写进 A股 daily 的默认运行规则。</b> 这里不新增下载，只复用同一批 A股 daily strict holdout，把 <code>单跑 EMA</code> 与 <code>EMA + PSAR exit overlay</code> 放到同一口径下比较。</p>
    <ul>
      <li><b>创业板ETF 1d / primary pilot：</b>在 <code>{ashare_daily_overlay_lookup.get('创业板ETF', {}).get('holdouts', '-')}</code> 个 strict holdout 里，overlay 约只有 <code>{fmt_pct(float(ashare_daily_overlay_lookup.get('创业板ETF', {}).get('overlay_better_holdout_share', np.nan)) * 100.0)}</code> 能把 net20 做得更好；median net20 delta 约 <code>{fmt_pct(ashare_daily_overlay_lookup.get('创业板ETF', {}).get('median_net20_delta_pp', np.nan))}</code>，median trade delta 约 <code>{fmt_num(ashare_daily_overlay_lookup.get('创业板ETF', {}).get('median_trade_delta', np.nan), 0)}</code> 笔。当前更诚实的 runbook 读法是 <b><code>{ashare_daily_overlay_lookup.get('创业板ETF', {}).get('overlay_verdict', '-')}</code></b>——{ashare_daily_overlay_lookup.get('创业板ETF', {}).get('deployment_reading', '-')}</li>
      <li><b>沪深300ETF 1d / shadow watch：</b>在 <code>{ashare_daily_overlay_lookup.get('沪深300ETF', {}).get('holdouts', '-')}</code> 个 strict holdout 里，overlay 约有 <code>{fmt_pct(float(ashare_daily_overlay_lookup.get('沪深300ETF', {}).get('overlay_better_holdout_share', np.nan)) * 100.0)}</code> 把 net20 做得更好；median net20 delta 约 <code>{fmt_pct(ashare_daily_overlay_lookup.get('沪深300ETF', {}).get('median_net20_delta_pp', np.nan))}</code>，median trade delta 约 <code>{fmt_num(ashare_daily_overlay_lookup.get('沪深300ETF', {}).get('median_trade_delta', np.nan), 0)}</code> 笔。也就是说，哪怕 recent-forward 已转正，PSAR overlay 目前也不能当成 shadow promotion 的补丁。</li>
      <li><b>项目级结果：</b>这批 A股 daily holdout 合起来，overlay 约只有 <code>{fmt_pct(float(ashare_daily_overlay_overall.get('overlay_better_holdout_share', np.nan)) * 100.0)}</code> 能改善 net20，整体 median net20 delta 约 <code>{fmt_pct(ashare_daily_overlay_overall.get('median_net20_delta_pp', np.nan))}</code>，median trade delta 约 <code>{fmt_num(ashare_daily_overlay_overall.get('median_trade_delta', np.nan), 0)}</code> 笔；当前 overall verdict 是 <b><code>{ashare_daily_overlay_overall.get('overall_verdict', '-')}</code></b>。</li>
      <li><b>deployment 含义：</b>{ashare_daily_overlay_overall.get('overall_reading', '-')} 换句话说，A股 daily 当前更合理的规则仍是 <b>EMA 负责方向与默认持有、PSAR 继续留在 benchmark / shadow 观察位</b>，而不是急着把快退出焊进 primary 或 shadow 的 admission runbook。</li>
    </ul>
    <h3>A股 daily PSAR exit overlay audit（strict holdouts）</h3>
    {html_table(ashare_daily_overlay_tbl, ["asset", "current_role", "holdouts", "overlay_better_holdout_share", "ema_net20_median_profit_pct", "overlay_net20_median_profit_pct", "median_net20_delta_pp", "best_net20_delta_pp", "worst_net20_delta_pp", "median_trade_delta", "overlay_verdict", "deployment_reading"])}
  </div>

  <div class="card">
    <h2>Q35f. 如果把当前 `EMA + PSAR` 结果收成一张 deployment matrix，哪些 pocket 还能继续，哪些应该直接封存？</h2>
    <p class="a">到 Q35e 为止，这条线已经分别回答了两个最关键 pocket：<code>Crypto 60m</code> 这块最弱口袋能不能靠 overlay 救回来，以及 <code>A股 daily</code> 这块最接近 paper 的口袋该不该把 overlay 焊进 runbook。更接近 deployment 的下一步，不是再堆近义板块，而是把这些答案压成一张矩阵：<b>哪些 pocket 允许继续 shadow 观察，哪些 pocket 必须继续拒绝默认接线。</b></p>
    <ul>
      <li><b>先给项目级结论：</b>这版最小组合研究现在已经足够回答 first-pass 问题——<b>`EMA + PSAR` 并没有在项目级上变成“比单跑 EMA 更诚实的默认组合”</b>。当前更诚实的 deployment 写法是：<code>EMA</code> 继续负责方向与默认持有；<code>PSAR</code> 只在极少数 pocket 保留 `shadow protective watch` 身份。</li>
      <li><b>必须继续封存的 pocket：</b><code>Crypto 60m</code> 目前只有 <code>{int(overlay_overall.get('overlay_better_net20_windows', 0))}/{int(overlay_overall.get('windows', 0))}</code> 个窗口改善，median net20 delta 约 <code>{fmt_pct(overlay_overall.get('median_net20_delta_pp', np.nan))}</code>，median trade delta 约 <code>{fmt_num(overlay_overall.get('median_trade_delta', np.nan), 0)}</code> 笔；所以它只能继续算 <b>reject rescue overlay</b>，不能拿来 reopen `60m fail pocket`。</li>
      <li><b>唯一还能继续观察的 pocket：</b><code>创业板ETF 1d</code> 当前约 <code>{fmt_pct(float(ashare_daily_overlay_lookup.get('创业板ETF', {}).get('overlay_better_holdout_share', np.nan)) * 100.0)}</code> strict holdout 改善，median net20 delta 约 <code>{fmt_pct(ashare_daily_overlay_lookup.get('创业板ETF', {}).get('median_net20_delta_pp', np.nan))}</code>；因此它可以继续保留成 <b>primary lane 的 shadow protective 候选</b>，但默认 EMA 持有规则仍不应直接改写。</li>
      <li><b>不能被偷渡成补丁的 pocket：</b><code>沪深300ETF 1d</code> 当前只有约 <code>{fmt_pct(float(ashare_daily_overlay_lookup.get('沪深300ETF', {}).get('overlay_better_holdout_share', np.nan)) * 100.0)}</code> holdout 改善，median net20 delta 约 <code>{fmt_pct(ashare_daily_overlay_lookup.get('沪深300ETF', {}).get('median_net20_delta_pp', np.nan))}</code>；所以它继续只配 `shadow watch`，PSAR 不能当 promotion patch。</li>
      <li><b>项目级默认规则：</b>A股 daily overall 当前约只有 <code>{fmt_pct(float(ashare_daily_overlay_overall.get('overlay_better_holdout_share', np.nan)) * 100.0)}</code> holdout 改善，median net20 delta 约 <code>{fmt_pct(ashare_daily_overlay_overall.get('median_net20_delta_pp', np.nan))}</code>；更诚实的项目级 call 仍是：<b>默认单跑 EMA，PSAR 不升格成 family-wide default overlay。</b></li>
    </ul>
    <h3>EMA + PSAR overlay deployment matrix</h3>
    {html_table(overlay_deployment_tbl, ["scope", "current_role", "samples", "overlay_better_share", "median_net20_delta_pp", "median_trade_delta", "deployment_verdict", "current_read", "what_to_do_now"])}
  </div>

  <div class="card">
    <h2>Q35g. 如果只保留 `创业板ETF 1d` 这一格，PSAR overlay 的 narrow shadow protective protocol 该怎么写？</h2>
    <p class="a">Q35f 已经把 `EMA + PSAR` 的项目级结论写死：默认仍是单跑 <code>EMA</code>，<code>PSAR</code> 不升格成 family-wide default overlay。既然如此，更接近 deployment 的下一刀就不该再补近义 wording，而是把唯一还能继续观察的 pocket——<code>创业板ETF 1d</code>——压成一张<b>窄口径 shadow protective protocol</b>：下一次真实 market close 到来时，到底该怎么记、怎么 review、什么情况下继续 shadow-only、什么情况下直接 rollback。</p>
    <ul>
      <li><b>先钉死边界：</b><code>创业板ETF 1d</code> 当前虽有约 <code>{fmt_pct(float(ashare_daily_overlay_lookup.get('创业板ETF', {}).get('overlay_better_holdout_share', np.nan)) * 100.0)}</code> strict holdout 改善、median net20 delta 约 <code>{fmt_pct(ashare_daily_overlay_lookup.get('创业板ETF', {}).get('median_net20_delta_pp', np.nan))}</code>，但 <code>A股 daily overall</code> 仍只有约 <code>{fmt_pct(float(ashare_daily_overlay_overall.get('overlay_better_holdout_share', np.nan)) * 100.0)}</code> 改善、median delta 约 <code>{fmt_pct(ashare_daily_overlay_overall.get('median_net20_delta_pp', np.nan))}</code>。所以这格最多只配 <b>primary lane 的 sidecar shadow protective watch</b>，不能偷渡成整个 family 的默认 protective layer。</li>
      <li><b>真实运行规则：</b>overlay sidecar 必须和 primary 主账本共用同一次 A 股收盘 refresh，只记录相对 <code>EMA-only</code> 的 comparator 字段（例如 <code>relative_net_delta_pp / trade_delta / review_note</code>），<b>不改变默认 EMA 持有规则</b>，也不允许在没有新 completed bar 时补伪 forward。</li>
      <li><b>继续 or rollback 的读法：</b>在 live shadow 里，默认先按 weekly relative review 看 <code>cumulative relative delta / added trade churn / drawdown delta / execution mismatch</code>。只要没出现连续两次 relative red，就继续 shadow-only 观察；一旦连续转 red 或出现执行口径不一致，就直接退回 benchmark-only。</li>
      <li><b>唯一允许升格的路径：</b>只有当 live shadow 也复现 overlay-specific gate（改善占比 <code>&gt;= 60%</code> 且 median relative delta <code>&gt; 0</code>），并同时通过项目级 <code>paper_live_promotion_gate_v1</code> 的最短观察期与 drawdown / execution guardrail，才配讨论非常有限的 default-overlay trial；在那之前，默认仍是 <b>EMA-only primary + PSAR sidecar shadow</b>。</li>
    </ul>
    <h3>创业板ETF 1d PSAR shadow protective protocol</h3>
    {html_table(ema_chinext_shadow_protocol_tbl, ["protocol_rank", "protocol_step", "scope_or_cadence", "concrete_rule", "go_if", "else_action", "why_it_exists"])}
  </div>

  <div class="card">
    <h2>Q35h. 下一次真实收盘一到，EMA 这张账本要按什么顺序落 refresh，避免“知道该做什么但执行时漂移”？</h2>
    <p class="a">Q35d 说明了现在是 on-clock waiting next close，Q35g 也把 `创业板ETF 1d` 的 overlay 观察位规则写死了。真正离 deployment 更近的一步，是把“下一次真实收盘一到就该怎么做”再压成一张 <b>next-close action queue</b>，避免执行时回到口头层，或把 `primary / secondary / shadow` 的动作混在一起。</p>
    <ul>
      <li><b>当前状态：</b>{next_close_queue_verdict}</li>
      <li><b>队列含义：</b>这张 queue 不是新 admission 结论，而是把已有 runbook 变成“到点就能执行”的动作顺序：谁先记账、谁只做 shadow refresh、谁在 blocked 时先修数据再续写。</li>
      <li><b>与未完成主线的关系：</b>它不能替代真实 forward refresh / week-1 review，但能显著降低下一次 close 到来时的执行漂移，让 line-299 那条未完成任务更容易一次性落成。</li>
    </ul>
    <h3>EMA paper/shadow next-close action queue</h3>
    {html_table(ema_paper_next_close_action_queue_tbl, ["queue_rank", "deployment_scope", "paper_status", "next_expected_close_utc", "time_to_next_close", "action_when_due", "if_not_due", "if_blocked", "why_this_step"])}
  </div>

  <div class="card">
    <h2>Q35i. 如果不想在下一次 close 之后还把这张账本误当成 `waiting`，该用什么 due-now / overdue 守门快照？</h2>
    <p class="a">Q35h 已经把“到点后按什么顺序做”排好了，但实际运行里还差一个很容易漏掉的 deployment 问题：<b>什么时候应该继续等，什么时候其实已经该刷、甚至已经迟到。</b> 这张 guardrail snapshot 不新增任何 alpha 结论；它只负责把 <code>waiting_not_due / due_soon / due_now_refresh_window / overdue_refresh_check</code> 明确区分开，避免下一根真实 close 过后还继续把账本写成“只是正常等待”。</p>
    <ul>
      <li><b>当前状态：</b>{due_guardrail_verdict}</li>
      <li><b>它和 Q35h 的分工：</b>Q35h 回答“到点后先做什么”；Q35i 回答“现在到底还是正常 waiting，还是已经该停止写近义说明、转去做 refresh / blocked 检查”。</li>
      <li><b>为什么这刀有用：</b>它把“正常等 close”与“close 已过还没续写”分开；前者不该伪造 forward，后者也不该继续伪装成 on-clock waiting。</li>
      <li><b>deployment 含义：</b>这不是新 board，也不是新 alpha；它只是给下一轮真实收盘后的执行留一个硬守门：一旦进入 <code>due_now</code> 或 <code>overdue</code>，默认先写 ledger / 查 blocked，不再补近义 narrative。</li>
    </ul>
    <h3>EMA paper/shadow due guardrail snapshot</h3>
    {html_table(ema_paper_due_guardrail_tbl, ["guardrail_rank", "deployment_scope", "paper_status", "latest_completed_bar_utc", "next_expected_close_utc", "relative_due_gap", "due_bucket", "week1_status", "guardrail_action", "if_missed", "why_it_matters"])}
  </div>

  <div class="card">
    <h2>Q35j. 如果不想只看覆盖式 snapshot，还想确认这张 EMA 账本真的是 append-only 在续写，该看什么 history audit？</h2>
    <p class="a">Q35i 解决的是“什么时候该刷”；但对最接近 paper 的这条线来说，还差一个更像记账层的问题：<b>我们现在看到的只是最新覆盖式 snapshot，还是已经在同一张账本上把 completed-bar 历史一笔一笔累计下来。</b> 这张 history audit 不新增任何 alpha 结论；它只是把 <code>ema_paper_trading_refresh_history.csv</code> 压成一张更可读的 append-only 审计表，让 Jerry 可以直接看出：每条 lane 目前是只有 seed 级 1 条记录，还是已经进入真正连续续写。</p>
    <ul>
      <li><b>当前状态：</b>{refresh_history_verdict}</li>
      <li><b>seed vs 连续续写：</b>{refresh_history_seed_note}</li>
      <li><b>最近一条 ledger 记录：</b>{refresh_history_latest_note}</li>
      <li><b>deployment 含义：</b>{refresh_history_deployment_line}</li>
    </ul>
    <h3>EMA paper/shadow refresh history audit</h3>
    {html_table(ema_paper_refresh_history_audit_tbl, ["history_rank", "deployment_scope", "paper_status", "market_freq_book", "rows_recorded", "distinct_completed_bars", "latest_completed_bar_utc", "latest_history_recorded_at_utc", "latest_data_source", "history_status", "continuity_read", "next_needed_to_advance"])}
  </div>

  <div class="card">
    <h2>Q36. 这页的边界是什么？</h2>
    <ul>
      <li>当前还是论文规则的 first-pass clean-room 扩展，不是最终生产策略。</li>
      <li>成本部分目前是 <b>基于 gross 汇总结果的线性近似</b>，适合先看“空间厚不厚”，还不能替代逐笔净值回放。</li>
      <li>day-0 ledger snapshot、first-refresh queue、top-3 first-refresh delta、以及 refresh clock audit 只代表首笔 paper/shadow 记账动作已经从空白 roster 进入真实状态、并且当前在按时等下一次真实 close，<b>不代表已经拿到了更长的新 forward alpha 证据</b>；真正改变 verdict 仍要靠后续 market-close refresh / weekly review。</li>
      <li>当前新增的 overlay deployment matrix、`创业板ETF 1d` narrow shadow protocol、next-close action queue、due-guardrail snapshot、以及 refresh-history audit，只代表 `EMA + PSAR` 最小组合研究的 first-pass deployment 结论：它已经足够回答“哪些 pocket 还能继续 shadow、哪些必须拒绝默认接线、唯一剩下的 pocket 该怎么按 sidecar 运行、下一次 close 到来时按什么顺序执行 refresh、close 过后何时不该再把账本误写成 waiting、以及 append-only ledger 目前到底只是 seed 还是已经连续续写”，但并没有证明 PSAR 在所有 non60m pocket 上都没用，更不等于完成了全量参数化组合研究。</li>
      <li>下一轮真正决定是否入库，还需要：<b>rolling / OOS honesty、正式 net backtest、参数稳定性、与现有 breakout/retest 线的组合价值</b>。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>相关产物</h2>
    <ul>
      <li><code>reports/artifacts/ema_psar_raw_alpha/base_strategy_summary.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_psar_summary.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_psar_by_class_freq.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_psar_head_to_head.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/btc_paper_window_ema_psar.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema60m_crypto_rolling_window_metrics.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema60m_crypto_rolling_asset_summary.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema60m_crypto_rolling_overall_summary.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema60m_psar_exit_overlay_window_metrics.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema60m_psar_exit_overlay_asset_summary.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema60m_psar_exit_overlay_overall_summary.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema60m_psar_exit_overlay_trade_delta_buckets.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_psar_baseline_family_survivors.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_baseline_family_final_survivor_map.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_candidate_spec.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_operating_spec.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_monitoring_board.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_runbook.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_kickoff_checklist.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_ledger_template.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_day0_seed_rows.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_first_week_review_scorecard.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_day0_snapshot.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_first_refresh_queue.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_first_refresh_delta.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_daily_refresh_snapshot.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_refresh_dependency_audit.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_refresh_clock_audit.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_next_close_action_queue.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_refresh_history.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_refresh_history_audit.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_secondary_backstop_recheck_queue.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_non60m_honesty_queue.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_non60m_frontier_vs_psar.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_non60m_ashare_frontier_rolling_window_metrics.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_non60m_ashare_frontier_rolling_pocket_summary.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_non60m_ashare_frontier_rolling_overall_summary.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_non60m_ashare_daily_holdout_window_metrics.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_non60m_ashare_daily_holdout_pocket_summary.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_ashare_daily_shadow_promotion_scorecard.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_ashare_daily_recent_forward_audit.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_ashare_daily_psar_overlay_holdout_window_metrics.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_ashare_daily_psar_overlay_pocket_summary.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_ashare_daily_psar_overlay_overall_summary.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_psar_overlay_deployment_matrix.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_chinext_daily_psar_shadow_protocol.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_non60m_ashare_daily_holdout_overall_summary.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_ashare_daily_shadow_promotion_scorecard.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_non60m_ashare_weekly_holdout_window_metrics.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_non60m_ashare_weekly_holdout_pocket_summary.csv</code></li>
      <li><code>reports/artifacts/ema_psar_raw_alpha/ema_non60m_ashare_weekly_holdout_overall_summary.csv</code></li>
      <li><code>reports/artifacts/ema_psar_cost_budget_v1/ema_psar_cost_budget_strategy_summary.csv</code></li>
      <li><code>reports/artifacts/ema_psar_cost_budget_v1/ema_psar_cost_budget_summary.csv</code></li>
    </ul>
    <p class=\"muted\">上游依赖：<a href=\"../../reading/regime_switch_indicator_stack_replication/report.html\">Regime Switch Indicator Stack Replication</a></p>
  </div>
</div>
</body>
</html>
"""

    SITE_PATH.write_text(html, encoding="utf-8")
    print(f"[ok] report generated: {SITE_PATH}")
    print(f"[ok] artifacts dir: {ART_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
