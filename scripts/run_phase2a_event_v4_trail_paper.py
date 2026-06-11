#!/usr/bin/env python3
from __future__ import annotations

"""Forward paper/shadow/live runner for Phase 2a Event + V4 + SL-only.

The strategy signal is shared across three ledgers:
- backtest reference fields for rule parity checks
- paper/shadow fills using public bookTicker bid/ask
- optional small live orders through the existing FR_Monitor bridge

Modes:
- --scan: detect live extreme events, evaluate completed-hour V4 signals, and
  open simulated paper positions; if live is armed, submit the linked live entry.
- --monitor: check completed 1h bars and close simulated positions on fixed
  stop-loss or hard timeout; if live positions exist, manage linked live exits.
- --status: rewrite status/report from current artifacts.
"""

import argparse
import fcntl
import hashlib
import importlib.util
import json
import math
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "config" / "execution" / "phase2a_event_v4_trail_paper.json"
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def load_script_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load module spec: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


phase6_mod = load_script_module(ROOT / "scripts" / "run_rank32b_canary_phase6.py", "rank32b_phase6_mod_for_phase2a")

FUTURES_EXCHANGE_INFO = "/fapi/v1/exchangeInfo"
FUTURES_TICKER_24H = "/fapi/v1/ticker/24hr"
FUTURES_KLINES = "/fapi/v1/klines"
FUTURES_BOOK_TICKER = "/fapi/v1/ticker/bookTicker"
FUTURES_PRICE_TICKER = "/fapi/v1/ticker/price"

STATUS_FIELDS = [
    "strategy_id",
    "stage",
    "runner_mode",
    "venue",
    "updated_at_utc",
    "last_scan_at_utc",
    "last_monitor_at_utc",
    "active_events",
    "open_positions",
    "live_open_positions",
    "closed_trades",
    "live_closed_trades",
    "event_log_rows",
    "signal_log_rows",
    "rejection_rows",
    "live_rejection_rows",
    "lifetime_paper_return",
    "lifetime_live_return",
    "median_closed_net_return",
    "median_live_closed_net_return",
    "win_rate",
    "live_win_rate",
    "avg_entry_slippage_bps",
    "avg_exit_slippage_bps",
    "live_avg_entry_slippage_bps",
    "live_avg_exit_slippage_bps",
    "latest_event_symbol",
    "latest_signal_symbol",
    "latest_closed_symbol",
    "latest_live_closed_symbol",
    "config_path",
    "state_path",
    "open_positions_path",
    "closed_trades_path",
    "event_log_path",
    "signal_log_path",
    "monitor_mark_log_path",
    "slippage_audit_path",
    "run_log_path",
    "report_path",
    "note",
]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_z(ts: Any) -> str:
    if ts is None:
        return ""
    return pd.to_datetime(ts, utc=True).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_ts(value: Any) -> pd.Timestamp:
    return pd.to_datetime(value, utc=True)


def exchange_ms_to_iso(value: Any) -> str:
    try:
        ms = int(float(value))
    except (TypeError, ValueError):
        return ""
    if ms <= 0:
        return ""
    return iso_z(pd.to_datetime(ms, unit="ms", utc=True))


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def pct(v: Any, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def num(v: Any, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):,.{digits}f}"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_config(path: Path) -> dict[str, Any]:
    path = path.resolve()
    cfg = json.loads(path.read_text(encoding="utf-8"))
    cfg["_config_path"] = str(path)
    return cfg


def paths(cfg: dict[str, Any]) -> dict[str, Path]:
    art_dir = ROOT / cfg.get("artifact_dir", "reports/artifacts/paper_phase2a_event_v4_trail")
    site_dir = ROOT / cfg.get("site_dir", "reports/site/factors/paper_phase2a_event_v4_trail")
    return {
        "art_dir": art_dir,
        "site_dir": site_dir,
        "state": art_dir / "state.json",
        "status": art_dir / "status.csv",
        "run_summary": art_dir / "last_run_summary.json",
        "run_log": art_dir / "run_log.csv",
        "open_positions": art_dir / "open_positions.csv",
        "closed_trades": art_dir / "closed_trades.csv",
        "event_log": art_dir / "event_log.csv",
        "signal_log": art_dir / "signal_log.csv",
        "monitor_marks": art_dir / "monitor_mark_log.csv",
        "rejections": art_dir / "rejections.csv",
        "slippage_audit": art_dir / "slippage_audit.csv",
        "live_open_positions": art_dir / "live_open_positions.csv",
        "live_closed_trades": art_dir / "live_closed_trades.csv",
        "live_orders": art_dir / "live_orders.csv",
        "live_monitor_marks": art_dir / "live_monitor_mark_log.csv",
        "live_rejections": art_dir / "live_rejections.csv",
        "lock": art_dir / "runner.lock",
        "report": site_dir / "report.html",
    }


@contextmanager
def file_lock(path: Path, timeout_sec: float = 55.0):
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as fh:
        deadline = time.monotonic() + timeout_sec
        while True:
            try:
                fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise TimeoutError(f"could not acquire runner lock within {timeout_sec:.0f}s: {path}")
                time.sleep(0.25)
        try:
            fh.write(iso_z(utc_now()) + "\n")
            fh.flush()
            yield
        finally:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)


def initial_state(now: datetime) -> dict[str, Any]:
    return {
        "initialized_at_utc": iso_z(now),
        "last_scan_at_utc": "",
        "last_monitor_at_utc": "",
        "active_events": {},
        "open_positions": {},
        "live_positions": {},
        "cooldowns": {},
        "processed_signal_ids": [],
        "closed_trade_ids": [],
        "closed_live_trade_ids": [],
    }


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return initial_state(utc_now())
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(path: Path, state: dict[str, Any]) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path)


def append_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    ensure_dir(path.parent)
    out = pd.DataFrame(rows)
    if path.exists() and path.stat().st_size > 0:
        old = pd.read_csv(path)
        out = pd.concat([old, out], ignore_index=True)
    out.to_csv(path, index=False)


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str] | None = None) -> None:
    ensure_dir(path.parent)
    pd.DataFrame(rows, columns=columns).to_csv(path, index=False)


def request_json(cfg: dict[str, Any], path: str, params: dict[str, Any] | None = None, *, retries: int = 4) -> Any:
    base_url = str(cfg.get("base_url", "https://fapi.binance.com")).rstrip("/")
    url = base_url + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) OpenClaw-Phase2a-Paper/1.0",
        "Accept": "application/json,text/plain,*/*",
    }
    last_err: Exception | None = None
    for attempt in range(retries):
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            last_err = exc
            if exc.code in {418, 429, 500, 502, 503, 504} and attempt < retries - 1:
                time.sleep((attempt + 1) * 1.5)
                continue
            raise
        except urllib.error.URLError as exc:
            last_err = exc
            if attempt < retries - 1:
                time.sleep((attempt + 1) * 1.5)
                continue
            raise
    if last_err:
        raise last_err
    raise RuntimeError(f"failed request: {url}")


def latest_completed_hour_close(now: datetime) -> datetime:
    return now.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0)


def position_first_monitor_bar_open(v4: dict[str, Any]) -> datetime:
    signal_bar_open = parse_ts(v4["signal_bar_open_ts_utc"]).to_pydatetime()
    return signal_bar_open + timedelta(hours=1)


def load_completed_bars_since(cfg: dict[str, Any], symbol: str, start_open_ts: datetime, *, limit: int) -> pd.DataFrame:
    bars = fetch_klines(cfg, symbol, limit=limit)
    if bars.empty:
        return bars
    start_ts = pd.Timestamp(start_open_ts)
    start_ts = start_ts.tz_localize("UTC") if start_ts.tzinfo is None else start_ts.tz_convert("UTC")
    return bars[bars["open_ts"] >= start_ts].copy().sort_values("open_ts").reset_index(drop=True)


def evaluate_sl_only_exit(
    cfg: dict[str, Any],
    symbol: str,
    pos: dict[str, Any],
) -> tuple[str, dict[str, Any] | None]:
    first_bar_open = parse_ts(pos["first_monitor_bar_open_ts_utc"]).to_pydatetime()
    timeout_bars = int(pos.get("timeout_bars") or cfg.get("hard_timeout_hours", 96))
    stop_loss_price = float(pos["stop_loss_price"])
    limit = max(timeout_bars + 4, int(cfg.get("v4_volume_avg_bars", 20)) + 2)
    bars = load_completed_bars_since(cfg, symbol, first_bar_open, limit=limit)
    if bars.empty:
        return "", None

    monitored = bars.iloc[:timeout_bars].copy()
    if monitored.empty:
        return "", None

    for _, bar in monitored.iterrows():
        if float(bar["low"]) <= stop_loss_price:
            return "stop_loss", {
                "bar_open_ts_utc": iso_z(bar["open_ts"]),
                "bar_close_ts_utc": iso_z(bar["close_ts"]),
                "reference_price": stop_loss_price,
                "last_completed_close": float(bar["close"]),
                "last_completed_low": float(bar["low"]),
                "monitored_bars": int(len(monitored)),
                "high_water_mark": float(monitored["high"].max()),
                "max_favorable_excursion": max(0.0, float(monitored["high"].max()) / float(pos["paper_entry_price"]) - 1.0),
            }

    if len(monitored) >= timeout_bars:
        bar = monitored.iloc[timeout_bars - 1]
        return "hard_timeout", {
            "bar_open_ts_utc": iso_z(bar["open_ts"]),
            "bar_close_ts_utc": iso_z(bar["close_ts"]),
            "reference_price": float(bar["close"]),
            "last_completed_close": float(bar["close"]),
            "last_completed_low": float(bar["low"]),
            "monitored_bars": int(len(monitored)),
            "high_water_mark": float(monitored["high"].max()),
            "max_favorable_excursion": max(0.0, float(monitored["high"].max()) / float(pos["paper_entry_price"]) - 1.0),
        }

    latest = monitored.iloc[-1]
    return "", {
        "bar_open_ts_utc": iso_z(latest["open_ts"]),
        "bar_close_ts_utc": iso_z(latest["close_ts"]),
        "reference_price": float(latest["close"]),
        "last_completed_close": float(latest["close"]),
        "last_completed_low": float(latest["low"]),
        "monitored_bars": int(len(monitored)),
        "high_water_mark": float(monitored["high"].max()),
        "max_favorable_excursion": max(0.0, float(monitored["high"].max()) / float(pos["paper_entry_price"]) - 1.0),
    }


def load_tradeable_symbols(cfg: dict[str, Any]) -> dict[str, dict[str, Any]]:
    stable_bases = set(cfg.get("stable_bases", []))
    raw = request_json(cfg, FUTURES_EXCHANGE_INFO)
    out: dict[str, dict[str, Any]] = {}
    for row in raw.get("symbols", []):
        symbol = str(row.get("symbol") or "")
        base = str(row.get("baseAsset") or symbol.removesuffix("USDT"))
        if row.get("status") != "TRADING":
            continue
        if row.get("contractType") != "PERPETUAL":
            continue
        if row.get("quoteAsset") != "USDT":
            continue
        if not symbol.endswith("USDT"):
            continue
        if base in stable_bases:
            continue
        out[symbol] = {
            "symbol": symbol,
            "base_asset": base,
            "onboard_date_ms": row.get("onboardDate"),
        }
    return out


def fetch_ticker_24h(cfg: dict[str, Any]) -> list[dict[str, Any]]:
    data = request_json(cfg, FUTURES_TICKER_24H)
    if not isinstance(data, list):
        raise RuntimeError("unexpected ticker/24hr response")
    return data


def fetch_klines(cfg: dict[str, Any], symbol: str, *, limit: int) -> pd.DataFrame:
    data = request_json(
        cfg,
        FUTURES_KLINES,
        {"symbol": symbol, "interval": cfg.get("bar_interval", "1h"), "limit": int(limit)},
    )
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
            "open_ts": pd.to_datetime(df["open_time"], unit="ms", utc=True),
            "close_ts": pd.to_datetime(df["close_time"], unit="ms", utc=True),
            "open": pd.to_numeric(df["open"], errors="coerce"),
            "high": pd.to_numeric(df["high"], errors="coerce"),
            "low": pd.to_numeric(df["low"], errors="coerce"),
            "close": pd.to_numeric(df["close"], errors="coerce"),
            "base_volume": pd.to_numeric(df["volume"], errors="coerce"),
            "quote_volume": pd.to_numeric(df["quote_asset_volume"], errors="coerce"),
            "number_of_trades": pd.to_numeric(df["number_of_trades"], errors="coerce"),
        }
    )
    return out.dropna().sort_values("open_ts").reset_index(drop=True)


def fetch_book_ticker(cfg: dict[str, Any], symbol: str | None = None) -> dict[str, Any] | list[dict[str, Any]]:
    params = {"symbol": symbol} if symbol else None
    return request_json(cfg, FUTURES_BOOK_TICKER, params)


def fetch_last_price(cfg: dict[str, Any], symbol: str) -> float:
    data = request_json(cfg, FUTURES_PRICE_TICKER, {"symbol": symbol})
    return float(data["price"])


_KLINE_5M_CACHE: dict[str, tuple[float, float]] = {}  # symbol -> (fetch_ts, close_price)


def fetch_latest_5m_close(cfg: dict[str, Any], symbol: str) -> float | None:
    """Return the close price of the most recently *completed* 5-minute bar.

    Results are cached for 30 seconds to avoid hammering the API when many
    positions are monitored in the same tick.  Returns None on failure so
    callers can fall back to tick-level prices.
    """
    now_ts = time.time()
    cached = _KLINE_5M_CACHE.get(symbol)
    if cached and (now_ts - cached[0]) < 30.0:
        return cached[1]
    try:
        data = request_json(cfg, FUTURES_KLINES, {"symbol": symbol, "interval": "5m", "limit": 3})
        # Binance returns [[open_ts, open, high, low, close, ...], ...]
        # We want the second-to-last bar (the last *completed* one).
        if len(data) >= 2:
            close_price = float(data[-2][4])  # index 4 = close
            _KLINE_5M_CACHE[symbol] = (now_ts, close_price)
            return close_price
        if len(data) == 1:
            close_price = float(data[0][4])
            _KLINE_5M_CACHE[symbol] = (now_ts, close_price)
            return close_price
    except Exception:
        pass
    return None


def quote_for_symbol(cfg: dict[str, Any], symbol: str) -> dict[str, Any]:
    try:
        if cfg.get("use_book_ticker_for_fills", True):
            raw = fetch_book_ticker(cfg, symbol)
            if isinstance(raw, list):
                raw = raw[0]
            bid = float(raw["bidPrice"])
            ask = float(raw["askPrice"])
            mid = (bid + ask) / 2.0
            spread_bps = ((ask - bid) / mid) * 10000.0 if mid > 0 else math.nan
            return {
                "symbol": symbol,
                "best_bid": bid,
                "best_ask": ask,
                "mid": mid,
                "last": mid,
                "spread_bps": spread_bps,
                "quote_source": "bookTicker",
            }
    except Exception:
        if not cfg.get("fallback_to_last_price", True):
            raise
    last = fetch_last_price(cfg, symbol)
    return {
        "symbol": symbol,
        "best_bid": last,
        "best_ask": last,
        "mid": last,
        "last": last,
        "spread_bps": 0.0,
        "quote_source": "lastPriceFallback",
    }


def safe_float(value: Any, default: float = math.nan) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


def live_cfg(cfg: dict[str, Any]) -> dict[str, Any]:
    raw = cfg.get("live_trading")
    return raw if isinstance(raw, dict) else {}


def live_ordering_enabled(cfg: dict[str, Any]) -> bool:
    live = live_cfg(cfg)
    return bool(live.get("enabled")) and bool(live.get("live_order_placement_enabled")) and not bool(live.get("kill_switch"))


def load_live_bridge(cfg: dict[str, Any]) -> Any:
    phase3 = cfg.get("phase3") if isinstance(cfg.get("phase3"), dict) else {}
    root = str(phase3.get("fr_monitor_root") or "").strip()
    private = str(phase3.get("local_private_path") or "").strip() or None
    if not root:
        raise RuntimeError("live trading enabled but phase3.fr_monitor_root is empty")
    from momentum.execution.canary32b.frmonitor_bridge import load_frmonitor_bridge

    return load_frmonitor_bridge(root, local_private_path=private)


def make_client_order_id(cfg: dict[str, Any], symbol: str, trade_id: str, role: str, now: datetime) -> str:
    prefix = str(live_cfg(cfg).get("client_order_prefix", "p2a")).strip() or "p2a"
    digest = hashlib.sha1(f"{trade_id}|{role}|{iso_z(now)}".encode("utf-8")).hexdigest()[:10]
    raw = f"{prefix}-{role[:2]}-{symbol.replace('USDT', '')[:10]}-{digest}"
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
    cleaned = "".join(ch for ch in raw if ch in allowed)
    return cleaned[:36]


def normalize_live_order(payload: Any, source: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {"source": source, "raw": payload}
    raw = payload.get("payload") if isinstance(payload.get("payload"), dict) else payload
    if not isinstance(raw, dict):
        raw = {}
    return {
        "source": source,
        "http_status": payload.get("http_status"),
        "endpoint": payload.get("endpoint"),
        "transport": payload.get("transport") or "fapi_order",
        "type": payload.get("type") or raw.get("type"),
        "symbol": payload.get("symbol") or raw.get("symbol"),
        "side": payload.get("side") or raw.get("side"),
        "order_id": payload.get("order_id") or raw.get("orderId"),
        "client_order_id": payload.get("client_order_id") or raw.get("clientOrderId"),
        "status": payload.get("status") or raw.get("status"),
        "price": payload.get("price") or raw.get("price"),
        "orig_qty": payload.get("quantity") or raw.get("origQty") or raw.get("quantity"),
        "executed_qty": payload.get("executed_qty") or raw.get("executedQty") or raw.get("executedQuantity"),
        "avg_price": payload.get("avg_price") or raw.get("avgPrice") or raw.get("avgFillPrice"),
        "raw": raw,
    }


def resolve_live_market_fill(
    bridge: Any,
    cfg: dict[str, Any],
    symbol: str,
    order_n: dict[str, Any],
    *,
    source: str,
    base_url: str,
    attempts: int = 3,
) -> dict[str, Any]:
    """Market orders should fill immediately; query a few times if the submit payload is incomplete."""
    out = dict(order_n)
    for attempt in range(max(1, attempts)):
        status = str(out.get("status") or "").upper()
        executed_qty = safe_float(out.get("executed_qty"), 0.0)
        avg_price = safe_float(out.get("avg_price"), math.nan)
        if status == "FILLED" and executed_qty > 0 and avg_price > 0:
            return out
        if status in {"CANCELED", "EXPIRED", "REJECTED"}:
            return out
        if attempt > 0:
            time.sleep(0.35)
        order_id = out.get("order_id")
        client_order_id = out.get("client_order_id")
        if not order_id and not client_order_id:
            continue
        try:
            snap = bridge.get_binance_perp_order(
                symbol,
                order_id=order_id,
                client_order_id=str(client_order_id) if client_order_id else None,
                base_url=base_url,
            )
            snap_n = normalize_live_order(snap, source)
            for key in ("status", "executed_qty", "avg_price", "orig_qty", "price", "order_id", "client_order_id"):
                if snap_n.get(key) not in (None, "", 0, "0"):
                    out[key] = snap_n.get(key)
        except Exception:
            continue
    return out


def append_live_rejection(p: dict[str, Path], *, now: datetime, trade_id: str = "", symbol: str = "", reason: str, **extra: Any) -> None:
    append_csv(
        p["live_rejections"],
        [
            {
                "checked_at_utc": iso_z(now),
                "trade_id": trade_id,
                "symbol": symbol,
                "reason": reason,
                **extra,
            }
        ],
    )


def prune_state(state: dict[str, Any], now: datetime) -> None:
    active = state.get("active_events", {})
    for event_id, event in list(active.items()):
        expires = parse_ts(event.get("expires_at_utc"))
        if expires.to_pydatetime() < now:
            active.pop(event_id, None)

    cooldowns = state.get("cooldowns", {})
    cooldown_hours = 0.0
    # Cooldown expiry is stored directly, so remove stale keys.
    for symbol, expiry in list(cooldowns.items()):
        if parse_ts(expiry).to_pydatetime() < now:
            cooldowns.pop(symbol, None)

    processed = state.get("processed_signal_ids", [])
    if len(processed) > 5000:
        state["processed_signal_ids"] = processed[-2500:]
    closed_ids = state.get("closed_trade_ids", [])
    if len(closed_ids) > 5000:
        state["closed_trade_ids"] = closed_ids[-2500:]
    _ = cooldown_hours


def detect_events(cfg: dict[str, Any], state: dict[str, Any], now: datetime) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    tradeable = load_tradeable_symbols(cfg)
    tickers = fetch_ticker_24h(cfg)
    rows: list[dict[str, Any]] = []
    for t in tickers:
        symbol = str(t.get("symbol") or "")
        if symbol not in tradeable:
            continue
        try:
            ret24 = float(t.get("priceChangePercent", 0.0)) / 100.0
            quote_volume = float(t.get("quoteVolume", 0.0))
            last_price = float(t.get("lastPrice", 0.0))
        except (TypeError, ValueError):
            continue
        rows.append(
            {
                "symbol": symbol,
                "ret24": ret24,
                "quote_volume_24h": quote_volume,
                "last_price": last_price,
            }
        )
    rows.sort(key=lambda r: r["ret24"], reverse=True)
    for idx, row in enumerate(rows, start=1):
        row["event_rank"] = idx

    event_ts = latest_completed_hour_close(now)
    new_events: list[dict[str, Any]] = []
    event_logs: list[dict[str, Any]] = []
    rank_max = int(cfg.get("event_rank_max", 20))
    ret_min = float(cfg.get("event_ret24_min", 0.30))
    vol_min = float(cfg.get("event_quote_volume_min", 5_000_000.0))
    cooldown_hours = float(cfg.get("event_cooldown_hours", 24))
    watch_hours = float(cfg.get("event_watch_hours", 48))
    active = state.setdefault("active_events", {})
    cooldowns = state.setdefault("cooldowns", {})

    for row in rows[: max(rank_max, 50)]:
        qualifies = row["event_rank"] <= rank_max and row["ret24"] >= ret_min and row["quote_volume_24h"] >= vol_min
        if not qualifies:
            continue
        symbol = row["symbol"]
        event_id = f"{symbol}|{iso_z(event_ts)}"
        cooldown_expiry = cooldowns.get(symbol)
        rejection_reason = ""
        accepted = True
        if cooldown_expiry and parse_ts(cooldown_expiry).to_pydatetime() > now:
            accepted = False
            rejection_reason = "symbol_in_event_cooldown"
        if event_id in active:
            accepted = False
            rejection_reason = "event_already_active"

        log = {
            "detected_at_utc": iso_z(now),
            "event_ts_utc": iso_z(event_ts),
            "event_id": event_id,
            "symbol": symbol,
            "event_rank": row["event_rank"],
            "event_ret24": row["ret24"],
            "event_quote_volume_24h": row["quote_volume_24h"],
            "last_price": row["last_price"],
            "accepted": accepted,
            "rejection_reason": rejection_reason,
            "event_detection_mode": cfg.get("event_detection_mode"),
        }
        event_logs.append(log)
        if not accepted:
            continue

        event = {
            **log,
            "expires_at_utc": iso_z(event_ts + timedelta(hours=watch_hours)),
            "entered": False,
            "entry_trade_id": "",
        }
        active[event_id] = event
        cooldowns[symbol] = iso_z(event_ts + timedelta(hours=cooldown_hours))
        new_events.append(event)
    return new_events, event_logs


def evaluate_v4(cfg: dict[str, Any], symbol: str) -> dict[str, Any]:
    avg_bars = int(cfg.get("v4_volume_avg_bars", 20))
    limit = max(int(cfg.get("v4_klines_limit", 32)), avg_bars + 2)
    bars = fetch_klines(cfg, symbol, limit=limit)
    if len(bars) < avg_bars:
        return {
            "symbol": symbol,
            "v4_triggered": False,
            "v4_rejection_reason": "insufficient_completed_bars",
            "completed_bars": int(len(bars)),
        }
    latest = bars.iloc[-1]
    baseline = bars.iloc[-avg_bars:]
    avg_quote_volume = float(baseline["quote_volume"].mean())
    latest_quote_volume = float(latest["quote_volume"])
    vol_ratio = latest_quote_volume / avg_quote_volume if avg_quote_volume > 0 else math.nan
    prev_close = float(bars.iloc[-2]["close"]) if len(bars) >= 2 else math.nan
    ret_1h = float(latest["close"] / prev_close - 1.0) if prev_close > 0 else math.nan
    triggered = bool(
        vol_ratio >= float(cfg.get("v4_volume_ratio_min", 3.0))
        and ret_1h >= float(cfg.get("v4_return_min", 0.01))
    )
    return {
        "symbol": symbol,
        "v4_triggered": triggered,
        "v4_rejection_reason": "" if triggered else "v4_threshold_not_met",
        "signal_bar_open_ts_utc": iso_z(latest["open_ts"]),
        "signal_bar_close_ts_utc": iso_z(latest["close_ts"]),
        "signal_open": float(latest["open"]),
        "signal_close": float(latest["close"]),
        "signal_high": float(latest["high"]),
        "signal_low": float(latest["low"]),
        "signal_quote_volume": latest_quote_volume,
        "v4_volume_baseline": "rolling20_including_current_completed_bar",
        "v4_return_basis": "close_to_previous_close",
        "trailing_avg_quote_volume": avg_quote_volume,
        "vol_ratio": vol_ratio,
        "ret_1h": ret_1h,
        "completed_bars": int(len(bars)),
    }


def has_open_symbol(state: dict[str, Any], symbol: str) -> bool:
    return any(pos.get("symbol") == symbol for pos in state.get("open_positions", {}).values())


def calc_entry_fill(cfg: dict[str, Any], symbol: str, signal_close: float) -> dict[str, Any]:
    quote = quote_for_symbol(cfg, symbol)
    extra = float(cfg.get("extra_market_slippage_bps_per_side", 0.0)) / 10000.0
    fill = float(quote["best_ask"]) * (1.0 + extra)
    slippage_bps_vs_signal_close = (fill / signal_close - 1.0) * 10000.0 if signal_close > 0 else math.nan
    return {
        **quote,
        "paper_entry_price": fill,
        "entry_slippage_bps_vs_signal_close": slippage_bps_vs_signal_close,
    }


def open_position(cfg: dict[str, Any], state: dict[str, Any], event: dict[str, Any], v4: dict[str, Any], now: datetime) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    symbol = event["symbol"]
    open_positions = state.setdefault("open_positions", {})
    if len(open_positions) >= int(cfg.get("max_concurrent_positions", 5)):
        return None, {"reason": "max_concurrent_positions_reached"}
    if int(cfg.get("max_positions_per_symbol", 1)) <= 1 and has_open_symbol(state, symbol):
        return None, {"reason": "symbol_already_has_open_position"}
    if cfg.get("one_entry_per_event", True) and event.get("entered"):
        return None, {"reason": "event_already_entered"}

    fill = calc_entry_fill(cfg, symbol, float(v4["signal_close"]))
    spread_bps = float(fill.get("spread_bps") or 0.0)
    if spread_bps > float(cfg.get("reject_entry_if_spread_bps_gt", 50.0)):
        return None, {"reason": "entry_spread_too_wide", "spread_bps": spread_bps}

    signed_entry_slippage_bps = float(fill.get("entry_slippage_bps_vs_signal_close") or 0.0)
    adverse_entry_slippage_bps = max(0.0, signed_entry_slippage_bps)
    max_slip = float(cfg.get("max_entry_slippage_bps", 50.0))
    if adverse_entry_slippage_bps > max_slip:
        return None, {
            "reason": "entry_slippage_too_high",
            "entry_slippage_bps": signed_entry_slippage_bps,
            "adverse_entry_slippage_bps": adverse_entry_slippage_bps,
            "max_entry_slippage_bps": max_slip,
        }

    entry_ts = now
    trade_id = f"{symbol}|{v4['signal_bar_close_ts_utc']}|{event['event_id']}"
    notional = float(cfg.get("notional_usdt", 1000.0))
    paper_entry_price = float(fill["paper_entry_price"])
    qty = notional / paper_entry_price if paper_entry_price > 0 else 0.0
    first_monitor_bar_open = position_first_monitor_bar_open(v4)
    timeout_hours = int(float(cfg.get("hard_timeout_hours", 96)))
    hard_timeout = first_monitor_bar_open + timedelta(hours=timeout_hours)
    stop_loss_pct = float(cfg.get("stop_loss_pct", 0.08))
    stop_loss_price = paper_entry_price * (1.0 - stop_loss_pct)
    position = {
        "trade_id": trade_id,
        "event_id": event["event_id"],
        "symbol": symbol,
        "direction": "LONG",
        "state": "open",
        "event_ts_utc": event["event_ts_utc"],
        "event_rank": int(event["event_rank"]),
        "event_ret24": float(event["event_ret24"]),
        "event_quote_volume_24h": float(event["event_quote_volume_24h"]),
        "signal_bar_open_ts_utc": v4["signal_bar_open_ts_utc"],
        "signal_bar_close_ts_utc": v4["signal_bar_close_ts_utc"],
        "decision_ts_utc": iso_z(now),
        "entry_ts_utc": iso_z(entry_ts),
        "signal_close_price": float(v4["signal_close"]),
        "theoretical_entry_price": float(v4["signal_close"]),
        "paper_entry_price": paper_entry_price,
        "entry_best_bid": float(fill.get("best_bid") or math.nan),
        "entry_best_ask": float(fill.get("best_ask") or math.nan),
        "entry_mid": float(fill.get("mid") or math.nan),
        "entry_spread_bps": spread_bps,
        "entry_slippage_bps_vs_signal_close": float(fill["entry_slippage_bps_vs_signal_close"]),
        "entry_quote_source": fill.get("quote_source"),
        "qty": qty,
        "notional_usdt": notional,
        "first_monitor_bar_open_ts_utc": iso_z(first_monitor_bar_open),
        "stop_loss_pct": stop_loss_pct,
        "stop_loss_price": stop_loss_price,
        "timeout_bars": timeout_hours,
        "hard_timeout_at_utc": iso_z(hard_timeout),
        "last_completed_bar_open_ts_utc": "",
        "last_completed_bar_close_ts_utc": "",
        "last_completed_close": math.nan,
        "last_completed_low": math.nan,
        "monitored_bars": 0,
        "high_water_mark": paper_entry_price,
        "max_favorable_excursion": 0.0,
        "v4_vol_ratio": float(v4["vol_ratio"]),
        "v4_ret_1h": float(v4["ret_1h"]),
        "v4_signal_quote_volume": float(v4["signal_quote_volume"]),
        "v4_trailing_avg_quote_volume": float(v4["trailing_avg_quote_volume"]),
    }
    open_positions[trade_id] = position
    event["entered"] = True
    event["entry_trade_id"] = trade_id
    return position, None


def has_live_open_symbol(state: dict[str, Any], symbol: str) -> bool:
    return any(pos.get("symbol") == symbol for pos in state.get("live_positions", {}).values())


def maybe_open_live_position(
    cfg: dict[str, Any],
    state: dict[str, Any],
    p: dict[str, Path],
    paper_pos: dict[str, Any],
    now: datetime,
) -> dict[str, Any]:
    live = live_cfg(cfg)
    symbol = str(paper_pos["symbol"])
    trade_id = str(paper_pos["trade_id"])
    if not bool(live.get("enabled")):
        return {"live_entry_status": "disabled"}
    if bool(live.get("kill_switch")):
        append_live_rejection(p, now=now, trade_id=trade_id, symbol=symbol, reason="live_kill_switch_on")
        return {"live_entry_status": "rejected", "live_entry_reason": "live_kill_switch_on"}
    if not bool(live.get("live_order_placement_enabled")):
        append_live_rejection(p, now=now, trade_id=trade_id, symbol=symbol, reason="live_order_placement_disabled")
        return {"live_entry_status": "rejected", "live_entry_reason": "live_order_placement_disabled"}

    live_positions = state.setdefault("live_positions", {})
    if trade_id in live_positions:
        return {"live_entry_status": "already_open"}
    if len(live_positions) >= int(live.get("max_concurrent_positions", 1)):
        append_live_rejection(p, now=now, trade_id=trade_id, symbol=symbol, reason="live_max_concurrent_positions_reached")
        return {"live_entry_status": "rejected", "live_entry_reason": "live_max_concurrent_positions_reached"}
    if int(live.get("max_positions_per_symbol", 1)) <= 1 and has_live_open_symbol(state, symbol):
        append_live_rejection(p, now=now, trade_id=trade_id, symbol=symbol, reason="live_symbol_already_open")
        return {"live_entry_status": "rejected", "live_entry_reason": "live_symbol_already_open"}

    quote = quote_for_symbol(cfg, symbol)
    spread_bps = safe_float(quote.get("spread_bps"), 0.0)
    if spread_bps > float(live.get("reject_entry_if_spread_bps_gt", 30.0)):
        append_live_rejection(p, now=now, trade_id=trade_id, symbol=symbol, reason="live_entry_spread_too_wide", spread_bps=spread_bps)
        return {"live_entry_status": "rejected", "live_entry_reason": "live_entry_spread_too_wide", "live_entry_spread_bps": spread_bps}

    target_notional = float(live.get("notional_usdt", 75.0))
    max_notional = float(live.get("max_effective_notional_usdt", 80.0))
    if target_notional <= 0 or target_notional > max_notional:
        append_live_rejection(p, now=now, trade_id=trade_id, symbol=symbol, reason="live_target_notional_out_of_bounds", target_notional_usdt=target_notional, max_effective_notional_usdt=max_notional)
        return {"live_entry_status": "rejected", "live_entry_reason": "live_target_notional_out_of_bounds"}

    client_id = make_client_order_id(cfg, symbol, trade_id, "entry", now)
    order_row_base = {
        "timestamp_utc": iso_z(now),
        "trade_id": trade_id,
        "paper_trade_id": trade_id,
        "symbol": symbol,
        "side": "BUY",
        "order_role": "live_entry",
        "order_type": str(live.get("order_type", "market")).upper(),
        "target_notional_usdt": target_notional,
        "max_effective_notional_usdt": max_notional,
        "client_order_id": client_id,
        "best_bid": quote.get("best_bid"),
        "best_ask": quote.get("best_ask"),
        "spread_bps": spread_bps,
    }
    if bool(live.get("dry_run_only")):
        append_csv(p["live_orders"], [{**order_row_base, "status": "DRY_RUN_ONLY"}])
        return {"live_entry_status": "dry_run_only"}

    bridge = load_live_bridge(cfg)
    base_url = str(cfg.get("base_url", "https://fapi.binance.com"))
    leverage = max(1, int(float(live.get("default_leverage", 1))))
    bridge.set_binance_perp_leverage(symbol, leverage)
    rules = bridge.get_binance_perp_trade_rules(symbol, base_url=base_url)
    last_price = safe_float(quote.get("best_ask"), safe_float(quote.get("mid")))
    qty_info = bridge.derive_binance_qty_from_notional(symbol, target_notional, last_price=last_price, rules=rules, base_url=base_url)
    quantity = str(qty_info.get("quantity"))
    effective_notional = safe_float(quantity, 0.0) * last_price
    if effective_notional <= 0 or effective_notional > max_notional:
        append_csv(p["live_orders"], [{**order_row_base, "status": "REJECTED_SIZE_GUARD", "quantity": quantity, "effective_notional_usdt": effective_notional}])
        append_live_rejection(p, now=now, trade_id=trade_id, symbol=symbol, reason="live_effective_notional_exceeds_cap", quantity=quantity, effective_notional_usdt=effective_notional, max_effective_notional_usdt=max_notional)
        return {"live_entry_status": "rejected", "live_entry_reason": "live_effective_notional_exceeds_cap"}

    order = bridge.place_binance_perp_live_market_order(
        symbol=symbol,
        side="BUY",
        quantity=quantity,
        reduce_only=None,
        position_side=str(live.get("position_side", "LONG")).upper() or "LONG",
        client_order_id=client_id,
        base_url=base_url,
    )
    order_n = normalize_live_order(order, "phase2a_live_entry_market")
    order_n = resolve_live_market_fill(bridge, cfg, symbol, order_n, source="phase2a_live_entry_market_query", base_url=base_url)
    status = str(order_n.get("status") or "").upper()
    executed_qty = safe_float(order_n.get("executed_qty"), 0.0)
    avg_price = safe_float(order_n.get("avg_price"), math.nan)
    if status != "FILLED" or executed_qty <= 0 or avg_price <= 0:
        append_csv(
            p["live_orders"],
            [
                {
                    **order_row_base,
                    "status": order_n.get("status") or "UNKNOWN",
                    "order_id": order_n.get("order_id"),
                    "quantity": quantity,
                    "executed_qty": order_n.get("executed_qty"),
                    "avg_price": order_n.get("avg_price"),
                    "effective_notional_usdt": math.nan,
                    "source": order_n.get("source"),
                }
            ],
        )
        append_live_rejection(
            p,
            now=now,
            trade_id=trade_id,
            symbol=symbol,
            reason="live_entry_fill_unconfirmed",
            order_status=order_n.get("status"),
            order_id=order_n.get("order_id"),
            client_order_id=order_n.get("client_order_id") or client_id,
        )
        return {"live_entry_status": "rejected", "live_entry_reason": "live_entry_fill_unconfirmed"}
    live_entry_notional = executed_qty * avg_price
    if live_entry_notional > max_notional:
        append_live_rejection(
            p,
            now=now,
            trade_id=trade_id,
            symbol=symbol,
            reason="live_filled_notional_exceeds_cap_audit",
            live_entry_notional_usdt=live_entry_notional,
            max_effective_notional_usdt=max_notional,
            order_id=order_n.get("order_id"),
        )
    stop_loss_price = float(paper_pos["stop_loss_price"])
    sl_client_id = make_client_order_id(cfg, symbol, trade_id, "sl", now)
    sl_order = bridge.place_binance_perp_live_stop_market_order(
        symbol=symbol,
        side="SELL",
        quantity=str(executed_qty),
        stop_price=stop_loss_price,
        reduce_only=bool(live.get("use_reduce_only_on_exit", True)),
        position_side=str(live.get("position_side", "LONG")).upper() or "LONG",
        client_order_id=sl_client_id,
        base_url=base_url,
    )
    sl_order_n = normalize_live_order(sl_order, "phase2a_live_exit_stop_market")
    live_pos = {
        "trade_id": trade_id,
        "paper_trade_id": trade_id,
        "event_id": paper_pos.get("event_id"),
        "symbol": symbol,
        "direction": "LONG",
        "state": "open",
        "entry_ts_utc": iso_z(now),
        "live_entry_price": avg_price,
        "live_qty": executed_qty,
        "live_notional_usdt": live_entry_notional,
        "entry_order_id": order_n.get("order_id"),
        "entry_client_order_id": order_n.get("client_order_id") or client_id,
        "entry_status": order_n.get("status"),
        "entry_best_bid": quote.get("best_bid"),
        "entry_best_ask": quote.get("best_ask"),
        "entry_spread_bps": spread_bps,
        "paper_entry_price": paper_pos.get("paper_entry_price"),
        "signal_close_price": paper_pos.get("signal_close_price"),
        "entry_slippage_bps_vs_paper": (avg_price / float(paper_pos["paper_entry_price"]) - 1.0) * 10000.0 if float(paper_pos["paper_entry_price"]) > 0 else math.nan,
        "entry_slippage_bps_vs_signal_close": (avg_price / float(paper_pos["signal_close_price"]) - 1.0) * 10000.0 if float(paper_pos["signal_close_price"]) > 0 else math.nan,
        "stop_loss_pct": paper_pos.get("stop_loss_pct"),
        "stop_loss_price": stop_loss_price,
        "hard_timeout_at_utc": paper_pos.get("hard_timeout_at_utc"),
        "first_monitor_bar_open_ts_utc": paper_pos.get("first_monitor_bar_open_ts_utc"),
        "timeout_bars": paper_pos.get("timeout_bars"),
        "v4_vol_ratio": paper_pos.get("v4_vol_ratio"),
        "v4_ret_1h": paper_pos.get("v4_ret_1h"),
        "live_order_mode": "market",
        "live_leverage": leverage,
        "sl_order_id": sl_order_n.get("order_id"),
        "sl_client_order_id": sl_order_n.get("client_order_id") or sl_client_id,
        "sl_order_status": sl_order_n.get("status"),
        "sl_transport": sl_order_n.get("transport"),
        "timeout_exit_order_id": None,
        "timeout_exit_client_order_id": None,
    }
    live_positions[trade_id] = live_pos
    append_csv(
        p["live_orders"],
        [
            {
                **order_row_base,
                "status": order_n.get("status"),
                "order_id": order_n.get("order_id"),
                "quantity": quantity,
                "executed_qty": executed_qty,
                "avg_price": avg_price,
                "effective_notional_usdt": live_entry_notional,
                "source": order_n.get("source"),
            }
        ],
    )
    append_csv(
        p["live_orders"],
        [
            {
                "timestamp_utc": iso_z(now),
                "trade_id": trade_id,
                "paper_trade_id": trade_id,
                "symbol": symbol,
                "side": "SELL",
                "order_role": "live_stop_loss",
                "order_type": sl_order_n.get("type") or "STOP_MARKET",
                "target_notional_usdt": live_entry_notional,
                "max_effective_notional_usdt": max_notional,
                "client_order_id": sl_order_n.get("client_order_id") or sl_client_id,
                "order_id": sl_order_n.get("order_id"),
                "quantity": str(executed_qty),
                "executed_qty": sl_order_n.get("executed_qty"),
                "avg_price": sl_order_n.get("avg_price"),
                "effective_notional_usdt": math.nan,
                "best_bid": quote.get("best_bid"),
                "best_ask": quote.get("best_ask"),
                "spread_bps": spread_bps,
                "status": sl_order_n.get("status"),
                "source": sl_order_n.get("source"),
                "stop_price": stop_loss_price,
            }
        ],
    )
    write_live_open_positions(p, state)
    return {"live_entry_status": str(order_n.get("status") or "submitted"), "live_entry_notional_usdt": live_entry_notional}


def scan(cfg: dict[str, Any], state: dict[str, Any], p: dict[str, Path], now: datetime) -> dict[str, Any]:
    prune_state(state, now)
    new_events, event_logs = detect_events(cfg, state, now)
    append_csv(p["event_log"], event_logs)

    signal_rows: list[dict[str, Any]] = []
    rejection_rows: list[dict[str, Any]] = []
    slippage_rows: list[dict[str, Any]] = []
    new_positions: list[dict[str, Any]] = []
    processed_ids = set(state.setdefault("processed_signal_ids", []))

    active_events = list(state.get("active_events", {}).values())
    for event in active_events:
        symbol = event["symbol"]
        event_ts = parse_ts(event["event_ts_utc"])
        expires = parse_ts(event["expires_at_utc"])
        if expires.to_pydatetime() < now:
            continue
        try:
            v4 = evaluate_v4(cfg, symbol)
            signal_open_ts = parse_ts(v4.get("signal_bar_open_ts_utc")) if v4.get("signal_bar_open_ts_utc") else None
            first_eligible_signal_open = event_ts
            in_window = bool(
                signal_open_ts is not None
                and signal_open_ts >= first_eligible_signal_open
                and signal_open_ts <= expires
            )
            signal_id = f"{event['event_id']}|{v4.get('signal_bar_close_ts_utc', '')}"
            already_processed = signal_id in processed_ids
            entry_block_reasons: list[str] = []
            if signal_open_ts is None:
                entry_block_reasons.append("missing_signal_bar")
            elif signal_open_ts < first_eligible_signal_open:
                entry_block_reasons.append("signal_before_first_eligible_bar")
            elif signal_open_ts > expires:
                entry_block_reasons.append("signal_after_event_window")
            if not v4.get("v4_triggered"):
                entry_block_reasons.append(str(v4.get("v4_rejection_reason") or "v4_not_triggered"))
            if already_processed:
                entry_block_reasons.append("signal_already_processed")
            row = {
                "checked_at_utc": iso_z(now),
                "event_id": event["event_id"],
                "symbol": symbol,
                "event_ts_utc": event["event_ts_utc"],
                "event_rank": event["event_rank"],
                "event_ret24": event["event_ret24"],
                "event_quote_volume_24h": event["event_quote_volume_24h"],
                "signal_id": signal_id,
                "in_event_window": in_window,
                "first_eligible_signal_open_ts_utc": iso_z(first_eligible_signal_open),
                "event_window_expires_at_utc": iso_z(expires),
                "already_processed": already_processed,
                "entry_block_reason": ";".join(dict.fromkeys(entry_block_reasons)),
                **v4,
            }
            signal_rows.append(row)
            if not v4.get("v4_triggered") or not in_window or already_processed:
                continue
            position, rejection = open_position(cfg, state, event, v4, now)
            processed_ids.add(signal_id)
            state["processed_signal_ids"].append(signal_id)
            if rejection is not None:
                rejection_rows.append({**row, **rejection})
                continue
            if position is not None:
                new_positions.append(position)
                try:
                    live_result = maybe_open_live_position(cfg, state, p, position, now)
                except Exception as exc:  # noqa: BLE001
                    append_live_rejection(
                        p,
                        now=now,
                        trade_id=str(position.get("trade_id") or ""),
                        symbol=str(position.get("symbol") or ""),
                        reason=f"live_entry_error:{type(exc).__name__}:{exc}",
                    )
                    live_result = {"live_entry_status": "rejected", "live_entry_reason": f"live_entry_error:{type(exc).__name__}"}
                if live_result.get("live_entry_status"):
                    position.update(live_result)
                slippage_rows.append(
                    {
                        "captured_at_utc": iso_z(now),
                        "trade_id": position["trade_id"],
                        "symbol": symbol,
                        "side": "entry",
                        "reference_price": position["signal_close_price"],
                        "paper_fill_price": position["paper_entry_price"],
                        "slippage_bps": position["entry_slippage_bps_vs_signal_close"],
                        "spread_bps": position["entry_spread_bps"],
                        "quote_source": position["entry_quote_source"],
                    }
                )
        except Exception as exc:  # noqa: BLE001
            rejection_rows.append(
                {
                    "checked_at_utc": iso_z(now),
                    "event_id": event.get("event_id"),
                    "symbol": symbol,
                    "reason": f"scan_error:{type(exc).__name__}:{exc}",
                }
            )

    append_csv(p["signal_log"], signal_rows)
    append_csv(p["rejections"], rejection_rows)
    append_csv(p["slippage_audit"], slippage_rows)
    state["last_scan_at_utc"] = iso_z(now)
    write_open_positions(p, state)
    return {
        "mode": "scan",
        "new_events": len(new_events),
        "events_logged": len(event_logs),
        "signals_checked": len(signal_rows),
        "new_positions": len(new_positions),
        "rejections": len(rejection_rows),
    }


def exit_fill(cfg: dict[str, Any], symbol: str) -> dict[str, Any]:
    quote = quote_for_symbol(cfg, symbol)
    extra = float(cfg.get("extra_market_slippage_bps_per_side", 0.0)) / 10000.0
    fill = float(quote["best_bid"]) * (1.0 - extra)
    return {**quote, "paper_exit_price": fill}


def close_position(cfg: dict[str, Any], pos: dict[str, Any], fill: dict[str, Any], now: datetime, reason: str) -> tuple[dict[str, Any], dict[str, Any]]:
    entry = float(pos["paper_entry_price"])
    exit_px = float(fill["paper_exit_price"])
    gross_ret = exit_px / entry - 1.0
    fee_rate = float(cfg.get("taker_fee_bps_per_side", 4.0)) / 10000.0
    net_ret = (1.0 + gross_ret) * (1.0 - fee_rate) * (1.0 - fee_rate) - 1.0
    theoretical_entry = float(pos.get("theoretical_entry_price") or pos.get("signal_close_price") or entry)
    theoretical_exit = exit_px
    theoretical_ret = theoretical_exit / theoretical_entry - 1.0 if theoretical_entry > 0 else math.nan
    exit_ts = parse_ts(fill.get("exit_ts_utc") or iso_z(now)).to_pydatetime()
    hold_hours = (exit_ts - parse_ts(pos["entry_ts_utc"]).to_pydatetime()).total_seconds() / 3600.0
    high_water = float(pos.get("high_water_mark") or entry)
    closed = {
        **pos,
        "state": "closed",
        "exit_ts_utc": fill.get("exit_ts_utc") or iso_z(now),
        "exit_reason": reason,
        "paper_exit_price": exit_px,
        "exit_best_bid": float(fill.get("best_bid") or math.nan),
        "exit_best_ask": float(fill.get("best_ask") or math.nan),
        "exit_mid": float(fill.get("mid") or math.nan),
        "exit_spread_bps": float(fill.get("spread_bps") or math.nan),
        "exit_quote_source": fill.get("quote_source"),
        "theoretical_exit_price": theoretical_exit,
        "gross_return": gross_ret,
        "net_return": net_ret,
        "theoretical_return_before_fees": theoretical_ret,
        "fee_bps_round_trip": float(cfg.get("taker_fee_bps_per_side", 4.0)) * 2.0,
        "hold_hours": hold_hours,
        "giveback_from_high_water_pct": (high_water / exit_px - 1.0) if exit_px > 0 else math.nan,
        "entry_to_exit_slippage_drag": net_ret - theoretical_ret if not math.isnan(theoretical_ret) else math.nan,
        "exit_bar_open_ts_utc": fill.get("exit_bar_open_ts_utc"),
        "exit_bar_close_ts_utc": fill.get("exit_bar_close_ts_utc"),
        "monitored_bars": fill.get("monitored_bars", pos.get("monitored_bars")),
    }
    slip = {
        "captured_at_utc": fill.get("exit_ts_utc") or iso_z(now),
        "trade_id": pos["trade_id"],
        "symbol": pos["symbol"],
        "side": "exit",
        "reference_price": theoretical_exit,
        "paper_fill_price": exit_px,
        "slippage_bps": (exit_px / theoretical_exit - 1.0) * 10000.0 if theoretical_exit > 0 else math.nan,
        "spread_bps": closed["exit_spread_bps"],
        "quote_source": closed["exit_quote_source"],
        "exit_reason": reason,
    }
    return closed, slip


def close_live_position(
    cfg: dict[str, Any],
    state: dict[str, Any],
    p: dict[str, Path],
    pos: dict[str, Any],
    quote: dict[str, Any],
    now: datetime,
    reason: str,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    live = live_cfg(cfg)
    symbol = str(pos["symbol"])
    trade_id = str(pos["trade_id"])
    qty = safe_float(pos.get("live_qty"), 0.0)
    if qty <= 0:
        append_live_rejection(p, now=now, trade_id=trade_id, symbol=symbol, reason="live_close_invalid_qty", live_qty=pos.get("live_qty"))
        return None, {"reason": "live_close_invalid_qty"}

    client_id = make_client_order_id(cfg, symbol, trade_id, "timeout", now)
    base_url = str(cfg.get("base_url", "https://fapi.binance.com"))
    bridge = load_live_bridge(cfg)
    sl_order_id = pos.get("sl_order_id")
    sl_client_order_id = pos.get("sl_client_order_id")
    sl_transport = str(pos.get("sl_transport") or "")
    if sl_order_id or sl_client_order_id:
        try:
            phase6_mod.cancel_order_quietly(
                bridge,
                symbol=symbol,
                order_id=sl_order_id,
                client_order_id=sl_client_order_id,
                transport=sl_transport or None,
            )
        except Exception:
            pass
    order = bridge.place_binance_perp_live_market_order(
        symbol=symbol,
        side="SELL",
        quantity=str(pos.get("live_qty")),
        reduce_only=bool(live.get("use_reduce_only_on_exit", True)),
        position_side=str(live.get("position_side", "LONG")).upper() or "LONG",
        client_order_id=client_id,
        base_url=base_url,
    )
    order_n = normalize_live_order(order, "phase2a_live_exit_market")
    order_n = resolve_live_market_fill(bridge, cfg, symbol, order_n, source="phase2a_live_exit_market_query", base_url=base_url)
    status = str(order_n.get("status") or "").upper()
    exit_qty = safe_float(order_n.get("executed_qty"), 0.0)
    exit_px = safe_float(order_n.get("avg_price"), math.nan)
    if status != "FILLED" or exit_qty <= 0 or exit_px <= 0:
        append_csv(
            p["live_orders"],
            [
                {
                    "timestamp_utc": iso_z(now),
                    "trade_id": trade_id,
                    "paper_trade_id": trade_id,
                    "symbol": symbol,
                    "side": "SELL",
                    "order_role": "live_exit",
                    "order_type": "MARKET",
                    "exit_reason": reason,
                    "client_order_id": client_id,
                    "status": order_n.get("status") or "UNKNOWN",
                    "order_id": order_n.get("order_id"),
                    "quantity": str(pos.get("live_qty")),
                    "executed_qty": order_n.get("executed_qty"),
                    "avg_price": order_n.get("avg_price"),
                    "effective_notional_usdt": math.nan,
                    "best_bid": quote.get("best_bid"),
                    "best_ask": quote.get("best_ask"),
                    "spread_bps": quote.get("spread_bps"),
                    "source": order_n.get("source"),
                }
            ],
        )
        append_live_rejection(
            p,
            now=now,
            trade_id=trade_id,
            symbol=symbol,
            reason="live_exit_fill_unconfirmed",
            order_status=order_n.get("status"),
            order_id=order_n.get("order_id"),
            client_order_id=order_n.get("client_order_id") or client_id,
        )
        return None, {"reason": "live_exit_fill_unconfirmed"}
    entry_px = safe_float(pos.get("live_entry_price"))
    gross_ret = exit_px / entry_px - 1.0 if entry_px > 0 else math.nan
    fee_rate = float(live.get("fee_bps_per_side", cfg.get("taker_fee_bps_per_side", 4.0))) / 10000.0
    net_ret = (1.0 + gross_ret) * (1.0 - fee_rate) * (1.0 - fee_rate) - 1.0 if math.isfinite(gross_ret) else math.nan
    hold_hours = (now - parse_ts(pos["entry_ts_utc"]).to_pydatetime()).total_seconds() / 3600.0
    paper_closed = read_csv(p["closed_trades"])
    matched_paper = paper_closed[paper_closed["trade_id"].astype(str).eq(trade_id)].tail(1) if not paper_closed.empty and "trade_id" in paper_closed else pd.DataFrame()
    paper_net = safe_float(matched_paper.iloc[-1].get("net_return")) if not matched_paper.empty else math.nan
    closed = {
        **pos,
        "state": "closed",
        "exit_ts_utc": iso_z(now),
        "exit_reason": reason,
        "live_exit_price": exit_px,
        "live_exit_qty": exit_qty,
        "exit_order_id": order_n.get("order_id"),
        "exit_client_order_id": order_n.get("client_order_id") or client_id,
        "exit_status": order_n.get("status"),
        "exit_best_bid": quote.get("best_bid"),
        "exit_best_ask": quote.get("best_ask"),
        "exit_spread_bps": quote.get("spread_bps"),
        "live_gross_return": gross_ret,
        "live_net_return": net_ret,
        "live_pnl_usdt": (exit_px - entry_px) * exit_qty if entry_px > 0 else math.nan,
        "fee_bps_round_trip": float(live.get("fee_bps_per_side", cfg.get("taker_fee_bps_per_side", 4.0))) * 2.0,
        "hold_hours": hold_hours,
        "paper_net_return": paper_net,
        "live_minus_paper_return": net_ret - paper_net if math.isfinite(net_ret) and math.isfinite(paper_net) else math.nan,
        "exit_slippage_bps_vs_paper": math.nan,
        "sl_order_id": sl_order_id,
        "sl_client_order_id": sl_client_order_id,
    }
    append_csv(
        p["live_orders"],
        [
            {
                "timestamp_utc": iso_z(now),
                "trade_id": trade_id,
                "paper_trade_id": trade_id,
                "symbol": symbol,
                "side": "SELL",
                "order_role": "live_exit",
                "order_type": "MARKET",
                "exit_reason": reason,
                "client_order_id": client_id,
                "status": order_n.get("status"),
                "order_id": order_n.get("order_id"),
                "quantity": str(pos.get("live_qty")),
                "executed_qty": exit_qty,
                "avg_price": exit_px,
                "effective_notional_usdt": exit_qty * exit_px,
                "best_bid": quote.get("best_bid"),
                "best_ask": quote.get("best_ask"),
                "spread_bps": quote.get("spread_bps"),
                "source": order_n.get("source"),
            }
        ],
    )
    state.setdefault("closed_live_trade_ids", []).append(trade_id)
    state.setdefault("live_positions", {}).pop(trade_id, None)
    return closed, None


def monitor_live_positions(cfg: dict[str, Any], state: dict[str, Any], p: dict[str, Path], now: datetime) -> dict[str, Any]:
    live_positions = state.setdefault("live_positions", {})
    if not live_positions:
        write_live_open_positions(p, state)
        return {"live_open_positions": 0, "live_new_closed_trades": 0, "live_rejections": 0}

    live = live_cfg(cfg)
    closed_rows: list[dict[str, Any]] = []
    mark_rows: list[dict[str, Any]] = []
    rejections = 0
    closed_ids = set(state.setdefault("closed_live_trade_ids", []))
    for trade_id, pos in list(live_positions.items()):
        symbol = str(pos["symbol"])
        try:
            quote = quote_for_symbol(cfg, symbol)
            spread_bps = safe_float(quote.get("spread_bps"), 0.0)
            current_exit_ref = safe_float(quote.get("best_bid"), safe_float(quote.get("mid")))
            pos["last_mark_ts_utc"] = iso_z(now)
            pos["last_mark_price"] = current_exit_ref
            hard_timeout = parse_ts(pos["hard_timeout_at_utc"]).to_pydatetime()
            reason = ""
            sl_status = ""
            sl_snapshot: dict[str, Any] | None = None
            sl_order_id = pos.get("sl_order_id")
            sl_client_order_id = pos.get("sl_client_order_id")
            sl_transport = str(pos.get("sl_transport") or "")
            if sl_order_id or sl_client_order_id:
                try:
                    sl_snapshot = phase6_mod.query_order_with_retry(
                        bridge=load_live_bridge(cfg),
                        symbol=symbol,
                        order_id=sl_order_id,
                        client_order_id=sl_client_order_id,
                        attempts=3,
                        sleep_seconds=0.35,
                        transport=sl_transport or None,
                    )
                    sl_status = phase6_mod.order_snapshot_status(sl_snapshot)
                except Exception as exc:  # noqa: BLE001
                    append_live_rejection(p, now=now, trade_id=trade_id, symbol=symbol, reason=f"live_stop_query_error:{type(exc).__name__}:{exc}")
                    rejections += 1
                    continue
            if phase6_mod.stop_loss_snapshot_filled(sl_snapshot):
                reason = "stop_loss"
            elif now >= hard_timeout:
                if spread_bps > float(live.get("reject_exit_if_spread_bps_gt", 80.0)):
                    append_live_rejection(p, now=now, trade_id=trade_id, symbol=symbol, reason="live_exit_spread_too_wide", spread_bps=spread_bps)
                    rejections += 1
                    continue
                reason = "hard_timeout"
            mark_rows.append(
                {
                    "checked_at_utc": iso_z(now),
                    "trade_id": trade_id,
                    "paper_trade_id": pos.get("paper_trade_id"),
                    "symbol": symbol,
                    "live_entry_price": pos.get("live_entry_price"),
                    "current_exit_ref": current_exit_ref,
                    "best_bid": quote.get("best_bid"),
                    "best_ask": quote.get("best_ask"),
                    "mid": quote.get("mid"),
                    "spread_bps": quote.get("spread_bps"),
                    "stop_loss_price": pos.get("stop_loss_price"),
                    "stop_order_id": sl_order_id,
                    "stop_order_status": sl_status,
                    "hard_timeout_at_utc": pos.get("hard_timeout_at_utc"),
                    "triggered_exit": bool(reason),
                    "exit_reason": reason,
                    "quote_source": quote.get("quote_source"),
                }
            )
            if not reason:
                continue
            if trade_id in closed_ids:
                live_positions.pop(trade_id, None)
                continue
            if reason == "stop_loss":
                entry_px = safe_float(pos.get("live_entry_price"))
                exit_ts_utc = (
                    exchange_ms_to_iso((sl_snapshot or {}).get("updateTime"))
                    or exchange_ms_to_iso((sl_snapshot or {}).get("triggerTime"))
                    or iso_z(now)
                )
                exit_px = max(
                    safe_float((sl_snapshot or {}).get("avgPrice"), 0.0),
                    safe_float((sl_snapshot or {}).get("actualPrice"), 0.0),
                    safe_float((sl_snapshot or {}).get("stopPrice"), 0.0),
                    safe_float((sl_snapshot or {}).get("triggerPrice"), 0.0),
                    safe_float(pos.get("stop_loss_price"), entry_px),
                )
                exit_qty = max(
                    safe_float((sl_snapshot or {}).get("executedQty"), 0.0),
                    safe_float((sl_snapshot or {}).get("actualQty"), 0.0),
                    safe_float(pos.get("live_qty"), 0.0),
                )
                fee_rate = float(live.get("fee_bps_per_side", cfg.get("taker_fee_bps_per_side", 4.0))) / 10000.0
                gross_ret = exit_px / entry_px - 1.0 if entry_px > 0 else math.nan
                net_ret = (1.0 + gross_ret) * (1.0 - fee_rate) * (1.0 - fee_rate) - 1.0 if math.isfinite(gross_ret) else math.nan
                hold_hours = (parse_ts(exit_ts_utc).to_pydatetime() - parse_ts(pos["entry_ts_utc"]).to_pydatetime()).total_seconds() / 3600.0
                paper_closed = read_csv(p["closed_trades"])
                matched_paper = paper_closed[paper_closed["trade_id"].astype(str).eq(trade_id)].tail(1) if not paper_closed.empty and "trade_id" in paper_closed else pd.DataFrame()
                paper_net = safe_float(matched_paper.iloc[-1].get("net_return")) if not matched_paper.empty else math.nan
                closed = {
                    **pos,
                    "state": "closed",
                    "exit_ts_utc": exit_ts_utc,
                    "exit_reason": reason,
                    "live_exit_price": exit_px,
                    "live_exit_qty": exit_qty,
                    "exit_order_id": sl_order_id,
                    "exit_client_order_id": sl_client_order_id,
                    "exit_status": sl_status,
                    "exit_best_bid": quote.get("best_bid"),
                    "exit_best_ask": quote.get("best_ask"),
                    "exit_spread_bps": quote.get("spread_bps"),
                    "live_gross_return": gross_ret,
                    "live_net_return": net_ret,
                    "live_pnl_usdt": (exit_px - entry_px) * exit_qty if entry_px > 0 else math.nan,
                    "fee_bps_round_trip": float(live.get("fee_bps_per_side", cfg.get("taker_fee_bps_per_side", 4.0))) * 2.0,
                    "hold_hours": hold_hours,
                    "paper_net_return": paper_net,
                    "live_minus_paper_return": net_ret - paper_net if math.isfinite(net_ret) and math.isfinite(paper_net) else math.nan,
                    "exit_slippage_bps_vs_paper": math.nan,
                }
                closed_rows.append(closed)
                state.setdefault("closed_live_trade_ids", []).append(trade_id)
                live_positions.pop(trade_id, None)
                append_csv(
                    p["live_orders"],
                    [
                        {
                            "timestamp_utc": iso_z(now),
                            "trade_id": trade_id,
                            "paper_trade_id": trade_id,
                            "symbol": symbol,
                            "side": "SELL",
                            "order_role": "live_stop_loss_fill",
                            "order_type": "STOP_MARKET",
                            "target_notional_usdt": pos.get("live_notional_usdt"),
                            "max_effective_notional_usdt": pos.get("live_notional_usdt"),
                            "client_order_id": sl_client_order_id,
                            "order_id": sl_order_id,
                            "quantity": str(pos.get("live_qty")),
                            "executed_qty": exit_qty,
                            "avg_price": exit_px,
                            "effective_notional_usdt": exit_qty * exit_px,
                            "best_bid": quote.get("best_bid"),
                            "best_ask": quote.get("best_ask"),
                            "spread_bps": quote.get("spread_bps"),
                            "status": sl_status,
                            "source": "phase2a_live_stop_market_query",
                            "stop_price": pos.get("stop_loss_price"),
                        }
                    ],
                )
                continue
            closed, rejection = close_live_position(cfg, state, p, pos, quote, now, reason)
            if rejection:
                rejections += 1
                continue
            if closed:
                closed_rows.append(closed)
        except Exception as exc:  # noqa: BLE001
            append_live_rejection(p, now=now, trade_id=trade_id, symbol=symbol, reason=f"live_monitor_error:{type(exc).__name__}:{exc}")
            rejections += 1

    append_csv(p["live_closed_trades"], closed_rows)
    append_csv(p["live_monitor_marks"], mark_rows)
    write_live_open_positions(p, state)
    return {
        "live_open_positions": len(state.get("live_positions", {})),
        "live_new_closed_trades": len(closed_rows),
        "live_rejections": rejections,
    }


def monitor(cfg: dict[str, Any], state: dict[str, Any], p: dict[str, Path], now: datetime) -> dict[str, Any]:
    prune_state(state, now)
    closed_rows: list[dict[str, Any]] = []
    slippage_rows: list[dict[str, Any]] = []
    rejection_rows: list[dict[str, Any]] = []
    monitor_mark_rows: list[dict[str, Any]] = []
    open_positions = state.setdefault("open_positions", {})
    closed_ids = set(state.setdefault("closed_trade_ids", []))

    for trade_id, pos in list(open_positions.items()):
        symbol = pos["symbol"]
        try:
            reason, bar_state = evaluate_sl_only_exit(cfg, symbol, pos)
            if bar_state is None:
                continue
            pos["last_mark_ts_utc"] = iso_z(now)
            pos["last_mark_price"] = bar_state.get("reference_price")
            pos["last_completed_bar_open_ts_utc"] = bar_state.get("bar_open_ts_utc")
            pos["last_completed_bar_close_ts_utc"] = bar_state.get("bar_close_ts_utc")
            pos["last_completed_close"] = bar_state.get("last_completed_close")
            pos["last_completed_low"] = bar_state.get("last_completed_low")
            pos["monitored_bars"] = bar_state.get("monitored_bars")
            pos["high_water_mark"] = bar_state.get("high_water_mark")
            pos["max_favorable_excursion"] = bar_state.get("max_favorable_excursion")
            monitor_mark_rows.append(
                {
                    "checked_at_utc": iso_z(now),
                    "trade_id": trade_id,
                    "symbol": symbol,
                    "paper_entry_price": pos.get("paper_entry_price"),
                    "current_exit_ref": bar_state.get("reference_price"),
                    "high_water_mark": bar_state.get("high_water_mark"),
                    "stop_loss_price": pos.get("stop_loss_price"),
                    "last_completed_close": bar_state.get("last_completed_close"),
                    "last_completed_low": bar_state.get("last_completed_low"),
                    "monitored_bars": bar_state.get("monitored_bars"),
                    "max_favorable_excursion": pos.get("max_favorable_excursion"),
                    "hard_timeout_at_utc": pos.get("hard_timeout_at_utc"),
                    "triggered_exit": bool(reason),
                    "exit_reason": reason,
                    "quote_source": "completed_1h_bar",
                    "bar_open_ts_utc": bar_state.get("bar_open_ts_utc"),
                    "bar_close_ts_utc": bar_state.get("bar_close_ts_utc"),
                }
            )
            if not reason:
                continue
            if trade_id in closed_ids:
                open_positions.pop(trade_id, None)
                continue
            if reason == "hard_timeout":
                fill = exit_fill(cfg, symbol)
                spread_bps = float(fill.get("spread_bps") or 0.0)
                if spread_bps > float(cfg.get("reject_exit_if_spread_bps_gt", 100.0)):
                    rejection_rows.append(
                        {
                            "checked_at_utc": iso_z(now),
                            "trade_id": trade_id,
                            "symbol": symbol,
                            "reason": "exit_spread_too_wide",
                            "spread_bps": spread_bps,
                        }
                    )
                    continue
                fill = {
                    **fill,
                    "paper_exit_price": float(bar_state["reference_price"]),
                    "exit_ts_utc": bar_state["bar_close_ts_utc"],
                    "exit_bar_open_ts_utc": bar_state["bar_open_ts_utc"],
                    "exit_bar_close_ts_utc": bar_state["bar_close_ts_utc"],
                    "monitored_bars": bar_state["monitored_bars"],
                    "mid": float(bar_state["reference_price"]),
                    "quote_source": "completed_1h_bar",
                }
            else:
                fill = {
                    "paper_exit_price": float(pos["stop_loss_price"]),
                    "best_bid": float(pos["stop_loss_price"]),
                    "best_ask": float(pos["stop_loss_price"]),
                    "mid": float(pos["stop_loss_price"]),
                    "spread_bps": 0.0,
                    "quote_source": "completed_1h_bar_low<=sl",
                    "exit_ts_utc": bar_state["bar_close_ts_utc"],
                    "exit_bar_open_ts_utc": bar_state["bar_open_ts_utc"],
                    "exit_bar_close_ts_utc": bar_state["bar_close_ts_utc"],
                    "monitored_bars": bar_state["monitored_bars"],
                }
            closed, slip = close_position(cfg, pos, fill, now, reason)
            closed_rows.append(closed)
            slippage_rows.append(slip)
            state["closed_trade_ids"].append(trade_id)
            open_positions.pop(trade_id, None)
        except Exception as exc:  # noqa: BLE001
            rejection_rows.append(
                {
                    "checked_at_utc": iso_z(now),
                    "trade_id": trade_id,
                    "symbol": symbol,
                    "reason": f"monitor_error:{type(exc).__name__}:{exc}",
                }
            )

    append_csv(p["closed_trades"], closed_rows)
    append_csv(p["monitor_marks"], monitor_mark_rows)
    append_csv(p["slippage_audit"], slippage_rows)
    append_csv(p["rejections"], rejection_rows)
    live_result = monitor_live_positions(cfg, state, p, now) if live_cfg(cfg).get("enabled") else {"live_open_positions": len(state.get("live_positions", {})), "live_new_closed_trades": 0, "live_rejections": 0}
    state["last_monitor_at_utc"] = iso_z(now)
    write_open_positions(p, state)
    return {
        "mode": "monitor",
        "open_positions": len(state.get("open_positions", {})),
        "new_closed_trades": len(closed_rows),
        "rejections": len(rejection_rows),
        **live_result,
    }


def write_open_positions(p: dict[str, Path], state: dict[str, Any]) -> None:
    rows = list(state.get("open_positions", {}).values())
    columns = [
        "trade_id",
        "symbol",
        "event_ts_utc",
        "signal_bar_close_ts_utc",
        "entry_ts_utc",
        "paper_entry_price",
        "last_mark_price",
        "last_completed_close",
        "last_completed_low",
        "high_water_mark",
        "stop_loss_price",
        "max_favorable_excursion",
        "monitored_bars",
        "first_monitor_bar_open_ts_utc",
        "hard_timeout_at_utc",
        "notional_usdt",
        "qty",
    ]
    write_csv(p["open_positions"], rows, columns=columns if not rows else None)


def write_live_open_positions(p: dict[str, Path], state: dict[str, Any]) -> None:
    rows = list(state.get("live_positions", {}).values())
    columns = [
        "trade_id",
        "paper_trade_id",
        "symbol",
        "entry_ts_utc",
        "live_entry_price",
        "paper_entry_price",
        "last_mark_price",
        "stop_loss_price",
        "hard_timeout_at_utc",
        "live_notional_usdt",
        "live_qty",
        "entry_order_id",
        "entry_status",
        "entry_slippage_bps_vs_paper",
        "sl_order_id",
        "sl_order_status",
    ]
    write_csv(p["live_open_positions"], rows, columns=columns if not rows else None)


def latest_value(df: pd.DataFrame, col: str) -> Any:
    if df.empty or col not in df.columns:
        return ""
    val = df.iloc[-1].get(col)
    return "" if pd.isna(val) else val


def build_status(cfg: dict[str, Any], state: dict[str, Any], p: dict[str, Path], now: datetime) -> dict[str, Any]:
    events = read_csv(p["event_log"])
    signals = read_csv(p["signal_log"])
    closed = read_csv(p["closed_trades"])
    live_closed = read_csv(p["live_closed_trades"])
    rejects = read_csv(p["rejections"])
    live_rejects = read_csv(p["live_rejections"])
    slips = read_csv(p["slippage_audit"])
    monitor_marks = read_csv(p["monitor_marks"])
    open_count = len(state.get("open_positions", {}))
    live_open_count = len(state.get("live_positions", {}))
    closed_count = int(len(closed))
    live_closed_count = int(len(live_closed))
    lifetime = float((1.0 + closed["net_return"]).prod() - 1.0) if not closed.empty and "net_return" in closed else 0.0
    live_lifetime = float((1.0 + live_closed["live_net_return"]).prod() - 1.0) if not live_closed.empty and "live_net_return" in live_closed else 0.0
    median_ret = float(closed["net_return"].median()) if not closed.empty and "net_return" in closed else math.nan
    live_median_ret = float(live_closed["live_net_return"].median()) if not live_closed.empty and "live_net_return" in live_closed else math.nan
    win_rate = float((closed["net_return"] > 0).mean()) if not closed.empty and "net_return" in closed else math.nan
    live_win_rate = float((live_closed["live_net_return"] > 0).mean()) if not live_closed.empty and "live_net_return" in live_closed else math.nan
    entry_slip = slips[slips["side"].eq("entry")] if not slips.empty and "side" in slips else pd.DataFrame()
    exit_slip = slips[slips["side"].eq("exit")] if not slips.empty and "side" in slips else pd.DataFrame()
    live_entry_slip = read_csv(p["live_orders"])
    live_entry_avg = safe_float(live_entry_slip[live_entry_slip["order_role"].astype(str).eq("live_entry")]["spread_bps"].mean()) if not live_entry_slip.empty and "order_role" in live_entry_slip and "spread_bps" in live_entry_slip else math.nan
    live_exit_avg = safe_float(live_entry_slip[live_entry_slip["order_role"].astype(str).eq("live_exit")]["spread_bps"].mean()) if not live_entry_slip.empty and "order_role" in live_entry_slip and "spread_bps" in live_entry_slip else math.nan
    status = {
        "strategy_id": cfg.get("strategy_id"),
        "stage": "paper_shadow_live_canary_running" if live_cfg(cfg).get("enabled") else "paper_shadow_running",
        "runner_mode": cfg.get("runner_mode"),
        "venue": cfg.get("venue"),
        "updated_at_utc": iso_z(now),
        "last_scan_at_utc": state.get("last_scan_at_utc", ""),
        "last_monitor_at_utc": state.get("last_monitor_at_utc", ""),
        "active_events": len(state.get("active_events", {})),
        "open_positions": open_count,
        "live_open_positions": live_open_count,
        "closed_trades": closed_count,
        "live_closed_trades": live_closed_count,
        "event_log_rows": int(len(events)),
        "signal_log_rows": int(len(signals)),
        "rejection_rows": int(len(rejects)),
        "live_rejection_rows": int(len(live_rejects)),
        "lifetime_paper_return": lifetime,
        "lifetime_live_return": live_lifetime,
        "median_closed_net_return": median_ret,
        "median_live_closed_net_return": live_median_ret,
        "win_rate": win_rate,
        "live_win_rate": live_win_rate,
        "avg_entry_slippage_bps": float(entry_slip["slippage_bps"].mean()) if not entry_slip.empty else math.nan,
        "avg_exit_slippage_bps": float(exit_slip["slippage_bps"].mean()) if not exit_slip.empty else math.nan,
        "live_avg_entry_slippage_bps": live_entry_avg,
        "live_avg_exit_slippage_bps": live_exit_avg,
        "latest_event_symbol": latest_value(events, "symbol"),
        "latest_signal_symbol": latest_value(signals, "symbol"),
        "latest_closed_symbol": latest_value(closed, "symbol"),
        "latest_live_closed_symbol": latest_value(live_closed, "symbol"),
        "config_path": rel(Path(cfg["_config_path"])),
        "state_path": rel(p["state"]),
        "open_positions_path": rel(p["open_positions"]),
        "closed_trades_path": rel(p["closed_trades"]),
        "event_log_path": rel(p["event_log"]),
        "signal_log_path": rel(p["signal_log"]),
        "monitor_mark_log_path": rel(p["monitor_marks"]),
        "slippage_audit_path": rel(p["slippage_audit"]),
        "run_log_path": rel(p["run_log"]),
        "report_path": rel(p["report"]),
        "note": "paper/shadow plus optional small live canary; strict completed 1h V4; live orders logged when armed",
    }
    _ = monitor_marks
    write_csv(p["status"], [status], columns=STATUS_FIELDS)
    return status


def truthy_count(df: pd.DataFrame, col: str) -> int:
    if df.empty or col not in df.columns:
        return 0
    s = df[col]
    if s.dtype == bool:
        return int(s.sum())
    return int(s.astype(str).str.lower().isin({"true", "1", "yes"}).sum())


COLUMN_LABELS = {
    "trade_id": "交易ID",
    "event_id": "事件ID",
    "symbol": "标的",
    "entry_ts_utc": "入场时间UTC",
    "exit_ts_utc": "退出时间UTC",
    "exit_reason": "退出原因",
    "paper_entry_price": "Paper入场价",
    "paper_exit_price": "Paper退出价",
    "paper_trade_id": "Paper交易ID",
    "live_entry_price": "Live入场价",
    "live_exit_price": "Live退出价",
    "live_qty": "Live数量",
    "live_notional_usdt": "Live名义本金USDT",
    "live_net_return": "Live扣费后收益",
    "live_gross_return": "Live毛收益",
    "live_pnl_usdt": "Live盈亏USDT",
    "live_minus_paper_return": "Live-Paper收益差",
    "paper_net_return": "Paper扣费收益",
    "entry_slippage_bps_vs_paper": "Live入场相对Paper滑点bps",
    "entry_slippage_bps_vs_signal_close": "Live入场相对信号滑点bps",
    "net_return": "扣费后收益",
    "theoretical_return_before_fees": "回测参考收益",
    "entry_to_exit_slippage_drag": "执行拖累",
    "hold_hours": "持仓小时",
    "max_favorable_excursion": "最大浮盈",
    "last_mark_price": "最近监控价",
    "high_water_mark": "最高可执行价",
    "stop_loss_price": "止损价",
    "hard_timeout_at_utc": "硬超时时间UTC",
    "notional_usdt": "名义本金USDT",
    "qty": "数量",
    "checked_at_utc": "检查时间UTC",
    "current_exit_ref": "当前退出参考价",
    "last_completed_close": "最近完成K线收盘",
    "last_completed_low": "最近完成K线最低",
    "monitored_bars": "已监控K线数",
    "first_monitor_bar_open_ts_utc": "起始监控K线UTC",
    "bar_open_ts_utc": "K线开盘UTC",
    "bar_close_ts_utc": "K线收盘UTC",
    "stop_order_id": "止损单ID",
    "stop_order_status": "止损单状态",
    "stop_price": "触发止损价",
    "triggered_exit": "是否触发退出",
    "spread_bps": "盘口价差bps",
    "quote_source": "报价来源",
    "detected_at_utc": "发现时间UTC",
    "event_ts_utc": "事件时间UTC",
    "expires_at_utc": "观察到期UTC",
    "event_rank": "事件排名",
    "event_ret24": "24h涨幅",
    "event_quote_volume_24h": "24h成交额",
    "last_price": "发现时价格",
    "accepted": "是否纳入观察",
    "rejection_reason": "拒绝原因",
    "event_detection_mode": "事件检测口径",
    "entered": "是否已入场",
    "entry_trade_id": "入场交易ID",
    "signal_bar_open_ts_utc": "信号K线开盘UTC",
    "signal_bar_close_ts_utc": "信号K线收盘UTC",
    "in_event_window": "是否在事件窗口",
    "first_eligible_signal_open_ts_utc": "最早允许信号K线UTC",
    "event_window_expires_at_utc": "事件窗口到期UTC",
    "already_processed": "是否已处理",
    "entry_block_reason": "未入场阻塞原因",
    "v4_triggered": "V4是否触发",
    "v4_rejection_reason": "V4未触发原因",
    "signal_close": "信号收盘价",
    "signal_quote_volume": "信号K线成交额",
    "v4_volume_baseline": "V4量能基准",
    "v4_return_basis": "V4涨幅基准",
    "trailing_avg_quote_volume": "rolling20均额",
    "vol_ratio": "量能倍数",
    "ret_1h": "1h涨幅",
    "completed_bars": "已完成K线数",
    "captured_at_utc": "记录时间UTC",
    "side": "方向",
    "reference_price": "参考价",
    "paper_fill_price": "Paper成交价",
    "slippage_bps": "滑点bps",
    "timestamp_utc": "时间UTC",
    "order_role": "订单角色",
    "order_type": "订单类型",
    "target_notional_usdt": "目标名义本金USDT",
    "max_effective_notional_usdt": "最大名义本金USDT",
    "client_order_id": "ClientOrderID",
    "order_id": "OrderID",
    "status": "状态",
    "quantity": "下单数量",
    "executed_qty": "成交数量",
    "avg_price": "平均成交价",
    "effective_notional_usdt": "实际名义本金USDT",
    "entry_order_id": "入场订单ID",
    "entry_status": "入场订单状态",
    "exit_order_id": "退出订单ID",
    "exit_status": "退出订单状态",
    "run_at_utc": "运行时间UTC",
    "ok": "是否成功",
    "modes": "运行模式",
    "scan_new_events": "新增事件",
    "scan_signals_checked": "检查信号数",
    "scan_new_positions": "新增持仓",
    "monitor_open_positions": "监控后持仓",
    "monitor_new_closed_trades": "新增平仓",
    "error_type": "错误类型",
    "error": "错误内容",
}


VALUE_LABELS = {
    "True": "是",
    "False": "否",
    "true": "是",
    "false": "否",
    "scan": "扫描",
    "monitor": "监控",
    "status": "刷新状态",
    "entry": "入场",
    "exit": "退出",
    "bookTicker": "bookTicker盘口",
    "lastPriceFallback": "最新价兜底",
    "ticker_24hr_rank_at_hourly_scan": "实时rolling 24h ticker排名",
    "event_already_active": "事件已在观察中",
    "symbol_in_event_cooldown": "标的仍在冷却期",
    "v4_threshold_not_met": "V4阈值未满足",
    "insufficient_completed_bars": "已完成K线不足",
    "max_concurrent_positions_reached": "达到最大同时持仓",
    "symbol_already_has_open_position": "该标的已有持仓",
    "event_already_entered": "该事件已入场过",
    "entry_spread_too_wide": "入场盘口价差过大",
    "exit_spread_too_wide": "退出盘口价差过大",
    "stop_loss": "固定止损",
    "hard_timeout": "96小时超时",
    "live_entry": "Live入场",
    "live_exit": "Live退出",
    "NEW": "已提交",
    "FILLED": "已成交",
    "PARTIALLY_FILLED": "部分成交",
    "DRY_RUN_ONLY": "仅预演",
    "REJECTED_SIZE_GUARD": "名义本金保护拒绝",
    "live_kill_switch_on": "Live kill switch开启",
    "live_order_placement_disabled": "Live真实下单未开启",
    "live_max_concurrent_positions_reached": "Live达到最大同时持仓",
    "live_symbol_already_open": "Live该标的已有持仓",
    "live_entry_spread_too_wide": "Live入场价差过大",
    "live_exit_spread_too_wide": "Live退出价差过大",
    "live_effective_notional_exceeds_cap": "Live名义本金超过上限",
    "live_target_notional_out_of_bounds": "Live目标本金越界",
}

PCT_COLUMNS = {
    "event_ret24",
    "ret_1h",
    "net_return",
    "live_net_return",
    "live_gross_return",
    "live_minus_paper_return",
    "paper_net_return",
    "theoretical_return_before_fees",
    "entry_to_exit_slippage_drag",
    "max_favorable_excursion",
    "stop_loss_pct",
}

BPS_COLUMNS = {"spread_bps", "slippage_bps", "entry_slippage_bps_vs_paper", "entry_slippage_bps_vs_signal_close"}


def format_cell_value(col: str, val: Any) -> str:
    if pd.isna(val):
        return ""
    if isinstance(val, bool):
        return "是" if val else "否"
    raw = str(val)
    if raw in VALUE_LABELS:
        return VALUE_LABELS[raw]
    if "," in raw and col == "modes":
        return ",".join(VALUE_LABELS.get(part, part) for part in raw.split(","))
    try:
        numeric = float(val)
    except (TypeError, ValueError):
        return raw
    if col in PCT_COLUMNS:
        return f"{numeric * 100:.2f}%"
    if col in BPS_COLUMNS:
        return f"{numeric:.2f}"
    if col in {"event_quote_volume_24h", "signal_quote_volume", "trailing_avg_quote_volume", "notional_usdt", "live_notional_usdt", "target_notional_usdt", "max_effective_notional_usdt", "effective_notional_usdt", "live_pnl_usdt"}:
        return f"{numeric:,.2f}"
    if col in {"vol_ratio"}:
        return f"{numeric:.3f}x"
    return raw


def render_table(df: pd.DataFrame, max_rows: int = 20, columns: list[str] | None = None) -> str:
    if df.empty:
        return "<p class='muted'>暂无记录。</p>"
    view = df.tail(max_rows).copy()
    if columns is not None:
        keep = [c for c in columns if c in view.columns]
        view = view[keep] if keep else view
    out = "<table><thead><tr>" + "".join(f"<th>{escape(COLUMN_LABELS.get(str(c), str(c)))}</th>" for c in view.columns) + "</tr></thead><tbody>"
    for _, row in view.iterrows():
        cells = []
        for c in view.columns:
            val = format_cell_value(str(c), row[c])
            cells.append(f"<td>{escape(val)}</td>")
        out += "<tr>" + "".join(cells) + "</tr>"
    out += "</tbody></table>"
    return out


def render_kv_table(rows: list[tuple[str, Any, str]]) -> str:
    out = "<table><thead><tr><th>项目</th><th>当前值</th><th>说明</th></tr></thead><tbody>"
    for item, value, meaning in rows:
        out += f"<tr><td>{escape(str(item))}</td><td>{escape(str(value))}</td><td>{escape(str(meaning))}</td></tr>"
    out += "</tbody></table>"
    return out


def render_rule_parity(cfg: dict[str, Any]) -> str:
    live = live_cfg(cfg)
    live_state = "开启" if live_ordering_enabled(cfg) else "关闭"
    rows = [
        (
            "市场范围 / 事件来源",
            f"回测：Binance 全量 1h 历史；Paper：{VALUE_LABELS.get(str(cfg.get('event_detection_mode')), cfg.get('event_detection_mode'))}",
            "Paper 使用实盘可获得的 rolling 24h ticker 排名；V4 仍只使用已完成 1h K线，避免偷看未完成K线。",
        ),
        ("事件排名", f"≤ {cfg.get('event_rank_max')}", "与 Phase2a 报告一致，只看 24h 涨幅排名最靠前的标的。"),
        ("24h涨幅", f"≥ {pct(cfg.get('event_ret24_min'), 0)}", "阈值与回测一致；Paper 中来自 Binance 扫描时刻 rolling 24h ticker。"),
        ("24h成交额", f"≥ ${float(cfg.get('event_quote_volume_min')):,.0f}", "与回测一致的流动性过滤，避免太小的币。"),
        ("事件冷却期", f"{cfg.get('event_cooldown_hours')}小时/标的", "同一标的短期不重复触发事件，避免重复计数。"),
        ("V4量能倍数", f"≥ {cfg.get('v4_volume_ratio_min')}x，基准为 rolling{cfg.get('v4_volume_avg_bars')} 已完成1h quote volume均值，包含信号K线", "与 v1.6a 历史回测主口径对齐。"),
        ("V4价格动量", f"已完成1h close-to-close 涨幅 ≥ {pct(cfg.get('v4_return_min'), 0)}", "使用信号K线收盘价相对上一根已完成K线收盘价，不使用 open-to-close 盘内涨幅。"),
        ("信号窗口", f"最早 signal_open_ts ≥ event_ts，直到事件后{cfg.get('event_watch_hours')}小时", "例如 12:02 发现 event_ts=12:00 的事件，禁止用 11:00-12:00 K线开仓，最早检查 12:00-13:00 K线。"),
        ("回测参考入场", "信号K线收盘价", "记录在 theoretical_entry_price，用来和回测口径对照。"),
        ("Paper入场", "bookTicker ask", "模拟市价买入，更接近实盘；同时记录相对信号收盘价的滑点。"),
        ("回测参考退出", f"固定止损 {pct(cfg.get('stop_loss_pct', 0.08), 0)} / 最长 {cfg.get('hard_timeout_hours')}h", "止损按完成的1h K线 low<=SL 触发；否则到超时按最后收盘价结算。"),
        ("Paper退出", "固定止损价或完成K线收盘价", "SL 命中时按止损价结算；超时按最后一根完成K线收盘价结算。"),
        ("手续费", f"单边 {cfg.get('taker_fee_bps_per_side')} bps", "Paper 的 net return 已扣除配置中的 taker 手续费。"),
        (
            "Live实盘入场/退出",
            f"{live_state}；市价单；目标≤${float(live.get('notional_usdt', 0.0)):,.0f}，硬上限≤${float(live.get('max_effective_notional_usdt', 0.0)):,.0f}",
            "Live 使用与 paper 完全相同的事件和V4信号；入场后立即挂真实 STOP_MARKET 止损，若未触发则到 96h 再市价平仓。",
        ),
    ]
    return render_kv_table(rows)


def render_live_controls(cfg: dict[str, Any]) -> str:
    live = live_cfg(cfg)
    rows = [
        ("Live总开关", "开启" if live.get("enabled") else "关闭", "关闭时不创建新的实盘订单，也不会展示新的live持仓。"),
        ("真实下单开关", "开启" if live.get("live_order_placement_enabled") else "关闭", "只有 enabled 和 live_order_placement_enabled 同时为真，才允许真实下单。"),
        ("Kill switch", "开启" if live.get("kill_switch") else "关闭", "开启时禁止新的live入场；已存在live仓位仍允许按退出规则减仓。"),
        ("订单类型", str(live.get("order_type", "market")).upper(), "Phase2a 默认用市价单，因为策略追求二次点火后的即时成交确定性。"),
        ("单笔目标名义本金", f"${float(live.get('notional_usdt', 0.0)):,.2f}", "当前按小仓位 canary 跑，不追求收益规模，先验证流程和执行差异。"),
        ("单笔名义本金硬上限", f"${float(live.get('max_effective_notional_usdt', 0.0)):,.2f}", "数量取整后若实际名义本金超过该上限，直接拒绝下单。"),
        ("最大同时live持仓", live.get("max_concurrent_positions", 1), "防止多个事件同时触发时实盘风险叠加。"),
        ("杠杆", f"{live.get('default_leverage', 1)}x", "启动前设置 Binance U本位合约杠杆，当前用1x。"),
        ("入场价差保护", f"{live.get('reject_entry_if_spread_bps_gt', 30)} bps", "盘口过宽时不追单。"),
        ("退出价差保护", f"{live.get('reject_exit_if_spread_bps_gt', 80)} bps", "极端盘口下先记录拒绝，下一分钟继续尝试；硬风控仍以人工/账户监控兜底。"),
    ]
    return render_kv_table(rows)


def render_backtest_paper_live_comparison(status: dict[str, Any]) -> str:
    rows = [
        ("回测", "历史模拟", "事件+V4+SL-only：固定 8% 止损 + 96h timeout", "用于定义前向验证的唯一规则口径，不再复用旧的 trailing 版本统计。"),
        (
            "Paper",
            f"{status.get('closed_trades', 0)} 笔已平仓",
            f"中位数 {pct(status.get('median_closed_net_return'))}，胜率 {pct(status.get('win_rate'), 1)}，累计 {pct(status.get('lifetime_paper_return'))}",
            "用 bookTicker ask/bid 模拟成交，是和回测最重要的前向对照账本。",
        ),
        (
            "Live",
            f"{status.get('live_closed_trades', 0)} 笔已平仓",
            f"中位数 {pct(status.get('median_live_closed_net_return'))}，胜率 {pct(status.get('live_win_rate'), 1)}，累计 {pct(status.get('lifetime_live_return'))}",
            "真实交易所成交，小仓位验证滑点、下单失败、账户模式和止损执行。",
        ),
    ]
    out = "<table><thead><tr><th>账本</th><th>样本</th><th>当前指标</th><th>用途</th></tr></thead><tbody>"
    for ledger, sample, metrics, use in rows:
        out += f"<tr><td>{escape(ledger)}</td><td>{escape(str(sample))}</td><td>{escape(str(metrics))}</td><td>{escape(use)}</td></tr>"
    out += "</tbody></table>"
    return out


def latest_row_value(df: pd.DataFrame, column: str, default: Any = "") -> Any:
    if df.empty or column not in df.columns:
        return default
    val = df.iloc[-1].get(column)
    return default if pd.isna(val) else val


def latest_reason_time(df: pd.DataFrame, reason_fragment: str, time_column: str) -> tuple[str, str]:
    if df.empty or "reason" not in df.columns or time_column not in df.columns:
        return "", ""
    mask = df["reason"].astype(str).str.contains(reason_fragment, regex=False, na=False)
    if not bool(mask.any()):
        return "", ""
    row = df[mask].iloc[-1]
    return str(row.get(time_column) or ""), str(row.get("reason") or "")


def render_autoclose_incident_audit(
    *,
    status: dict[str, Any],
    run_df: pd.DataFrame,
    rejection_df: pd.DataFrame,
    live_rejection_df: pd.DataFrame,
) -> str:
    monitor_runs = run_df[run_df["modes"].astype(str).eq("monitor")].copy() if not run_df.empty and "modes" in run_df.columns else pd.DataFrame()
    latest_monitor_at = latest_row_value(monitor_runs, "run_at_utc", status.get("last_monitor_at_utc", ""))
    latest_paper_rej = latest_row_value(monitor_runs, "monitor_rejections", "")
    latest_live_rej = latest_row_value(monitor_runs, "monitor_live_rejections", "")
    latest_open = latest_row_value(monitor_runs, "monitor_open_positions", status.get("open_positions", ""))
    latest_live_open = latest_row_value(monitor_runs, "monitor_live_open_positions", status.get("live_open_positions", ""))
    paper_err_at, paper_err_reason = latest_reason_time(rejection_df, "monitor_error:", "checked_at_utc")
    live_err_at, live_err_reason = latest_reason_time(live_rejection_df, "live_stop_query_error:", "checked_at_utc")
    rows = [
        (
            "事故结论",
            "已确认为自动退出监控/记账链路故障，已修复",
            "问题不在 SL-only 规则本身，而在 forward monitor 没有成功把已触发的退出写进账本。",
        ),
        (
            "Paper根因",
            paper_err_at or "未发现历史 monitor_error",
            paper_err_reason or "当前没有 paper monitor 异常记录。",
        ),
        (
            "Live根因",
            live_err_at or "未发现历史 live_stop_query_error",
            live_err_reason or "当前没有 live stop 查询异常记录。",
        ),
        (
            "已落地修复",
            "timezone 统一 + phase6 模块导入 + STOP_MARKET 成交识别",
            "paper 读取完成1h K线时先 tz_convert；live 查询止损单时复用 phase6 的 stop_loss_snapshot_filled，并读取 actualPrice/actualQty/triggerTime。",
        ),
        (
            "最新monitor健康",
            f"{latest_monitor_at}；paper_rejections={latest_paper_rej}，live_rejections={latest_live_rej}",
            "若这里再次非0，先看本页下方“拒绝与错误”和“Live拒绝与错误”。",
        ),
        (
            "当前账本状态",
            f"paper_open={latest_open}，live_open={latest_live_open}",
            "本地 live 账本为0不等于免查账户；关键事故后仍应额外用交易所仓位接口核对非零仓位。",
        ),
    ]
    return render_kv_table(rows)


def render_strategy_lifecycle(cfg: dict[str, Any]) -> str:
    rows = [
        (
            "“已接收事件”是什么意思",
            f"某次每小时扫描时，该标的同时满足 rank≤{cfg.get('event_rank_max')}、24h涨幅≥{pct(cfg.get('event_ret24_min'), 0)}、24h成交额≥${float(cfg.get('event_quote_volume_min')):,.0f}，并且没有被重复事件或冷却期挡掉",
            "它表示这个事件被纳入观察窗口；不表示此时此刻该币仍然满足这三个条件。",
        ),
        (
            "“观察中的事件”是什么意思",
            "已接收且尚未过期的事件",
            f"当前实现中，事件有效观察期为 {cfg.get('event_watch_hours')} 小时。",
        ),
        (
            "事件时间怎么定",
            "扫描时对应的最近已完成小时边界",
            "例如 02:02:15 扫描，事件时间通常记为 02:00:00 UTC；后续只允许事件时间之后的V4信号入场。",
        ),
        (
            "事件有效存续期",
            f"事件时间 + {cfg.get('event_watch_hours')} 小时",
            "过期后即使该币再次出现V4，也不会归属于这个事件；需要未来的新事件重新进入观察。",
        ),
        (
            "V4允许入场窗口",
            f"事件后第1根小时K到事件后第{cfg.get('event_watch_hours')}小时",
            "事件检测完成后，从下一根完整 1h K线开始允许信号入场。",
        ),
        (
            "同币冷却期",
            f"{cfg.get('event_cooldown_hours')} 小时",
            "同一标的刚触发过事件后，冷却期内不会创建新的独立事件，避免重复计数。",
        ),
        (
            "每个事件最多入场次数",
            "1次",
            "当前 one_entry_per_event=true；同一事件一旦paper入场，就不再重复入场。",
        ),
        (
            "Paper入场和退出",
            "入场用 bookTicker ask；退出按 SL 价或完成K线收盘价",
            "这样保留回测的 SL-only 语义，同时把入场滑点单独记录到审计表。",
        ),
        (
            "退出有效期",
            f"固定止损 {pct(cfg.get('stop_loss_pct', 0.08), 0)}；最长持仓 {cfg.get('hard_timeout_hours')} 小时",
            "如果完成K线 low 命中止损则按 SL 退出；否则到 96h 按最后完成K线收盘价退出。",
        ),
    ]
    return render_kv_table(rows)


def render_event_definition(cfg: dict[str, Any]) -> str:
    rows = [
        (
            "涨幅榜检查频率",
            f"每小时一次，当前 systemd timer 在每小时 :02:15 UTC 运行",
            "等1h K线完成后再扫描，避免使用未完成小时数据。",
        ),
        (
            "涨幅榜来源",
            "Binance USDⓈ-M Futures public /fapi/v1/ticker/24hr",
            "这是实盘可获得的 rolling 24h ticker，不是离线回测文件。",
        ),
        (
            "排名方向",
            "按 24h priceChangePercent 从高到低排序",
            "排名第1就是当次扫描时24h涨幅最高的可交易USDT永续合约。",
        ),
        (
            "当前事件rank阈值",
            f"rank≤{cfg.get('event_rank_max')}",
            "注意：当前配置是前20，不是前30。如果要改成前30，需要改配置并重新标注为新实验口径。",
        ),
        (
            "当前事件涨幅阈值",
            f"24h涨幅≥{pct(cfg.get('event_ret24_min'), 0)}",
            "只有涨幅足够极端，才认为它具备事件上下文。",
        ),
        (
            "当前事件成交额阈值",
            f"24h quote volume≥${float(cfg.get('event_quote_volume_min')):,.0f}",
            "这是成交额门槛，不是成交量枚数；用于过滤流动性过低的标的。",
        ),
        (
            "事件是否等于交易",
            "不等于",
            "事件只让标的进入48小时观察窗口；必须后续再出现V4二次点火，才会paper入场。",
        ),
    ]
    return render_kv_table(rows)


def render_process_flowchart(cfg: dict[str, Any]) -> str:
    return f"""
<div class="flow">
  <div class="flow-row">
    <div class="flow-box"><b>1. 每小时触发扫描</b><br>systemd timer<br><code>:02:15 UTC</code></div>
    <div class="flow-arrow">→</div>
    <div class="flow-box"><b>2. 拉取涨幅榜</b><br><code>/fapi/v1/ticker/24hr</code><br>全部可交易USDT永续</div>
    <div class="flow-arrow">→</div>
    <div class="flow-box"><b>3. 排名与事件过滤</b><br>24h涨幅降序排名<br><code>rank≤{cfg.get('event_rank_max')}</code><br><code>涨幅≥{pct(cfg.get('event_ret24_min'), 0)}</code><br><code>成交额≥${float(cfg.get('event_quote_volume_min')):,.0f}</code></div>
  </div>
  <div class="flow-row">
    <div class="flow-box decision"><b>4. 是否可接收事件？</b><br>检查同币冷却期 {cfg.get('event_cooldown_hours')}h<br>检查同一事件是否已存在</div>
    <div class="flow-arrow">→</div>
    <div class="flow-box"><b>5. 进入观察窗口</b><br>事件有效期 {cfg.get('event_watch_hours')}h<br>记录 <code>event_log.csv</code><br>状态写入 <code>state.json</code></div>
    <div class="flow-arrow">→</div>
    <div class="flow-box"><b>6. 拉取1h K线</b><br><code>/fapi/v1/klines</code><br>只使用已完成K线<br>当前limit={cfg.get('v4_klines_limit')}</div>
  </div>
  <div class="flow-row">
    <div class="flow-box"><b>7. 计算V4信号</b><br>最新已完成1h quote volume<br>÷ 前{cfg.get('v4_volume_avg_bars')}根均值<br><code>量能倍数&gt;{cfg.get('v4_volume_ratio_min')}</code><br><code>1h涨幅&gt;{pct(cfg.get('v4_return_min'), 0)}</code></div>
    <div class="flow-arrow">→</div>
    <div class="flow-box decision"><b>8. 是否允许入场？</b><br>必须在事件后1~{cfg.get('event_watch_hours')}h<br>V4触发<br>信号未处理过<br>同币无持仓</div>
    <div class="flow-arrow">→</div>
    <div class="flow-box"><b>9. 读取盘口</b><br><code>/fapi/v1/ticker/bookTicker</code><br>买入参考 ask<br>记录 bid/ask/mid/spread</div>
  </div>
  <div class="flow-row">
    <div class="flow-box decision"><b>10. 入场价差/滑点检查</b><br>若 spread &gt; {cfg.get('reject_entry_if_spread_bps_gt')} bps<br>或不利入场滑点 &gt; {cfg.get('max_entry_slippage_bps')} bps<br>拒绝入场并写入rejections<br>有利滑点不拒绝</div>
    <div class="flow-arrow">→</div>
    <div class="flow-box"><b>11. Paper开仓</b><br>用ask模拟成交<br>paper notional=${float(cfg.get('notional_usdt')):,.0f}<br>最多同时{cfg.get('max_concurrent_positions')}仓</div>
    <div class="flow-arrow">→</div>
    <div class="flow-box"><b>12. Live小仓位分支</b><br>同一trade_id<br>市价BUY真实下单<br>立即挂STOP_MARKET止损<br>目标≤${float(live_cfg(cfg).get('notional_usdt', 0.0)):,.0f}<br>硬上限≤${float(live_cfg(cfg).get('max_effective_notional_usdt', 0.0)):,.0f}</div>
  </div>
  <div class="flow-row">
    <div class="flow-box"><b>13. 写入审计</b><br><code>open_positions.csv</code><br><code>live_open_positions.csv</code><br><code>live_orders.csv</code><br><code>slippage_audit.csv</code></div>
    <div class="flow-arrow">→</div>
    <div class="flow-box"><b>14. 每分钟监控</b><br>systemd timer<br><code>:20 UTC</code><br>同时处理paper和live open positions</div>
    <div class="flow-arrow">→</div>
    <div class="flow-box"><b>15. 读取完成K线/止损单状态</b><br>paper：完成1h K线 low/close<br>live：查询 STOP_MARKET + 超时盘口</div>
  </div>
  <div class="flow-row">
    <div class="flow-box decision"><b>16. 是否退出？</b><br>paper：完成1h low ≤ 止损价<br>或持仓超过{cfg.get('hard_timeout_hours')}h<br>live：STOP_MARKET已成交或到期市价平仓</div>
    <div class="flow-arrow">→</div>
    <div class="flow-box"><b>17. Paper/Live平仓</b><br>paper：SL价或完成K线收盘价<br>live：止损成交价或超时市价SELL<br>扣除手续费计算收益</div>
    <div class="flow-arrow">→</div>
    <div class="flow-box"><b>18. 页面透明展示</b><br>回测/Paper/Live三账本<br>信号/订单/止损/滑点/拒绝<br>runner运行日志</div>
  </div>
</div>
"""


def render_v4_definition(cfg: dict[str, Any]) -> str:
    rows = [
        (
            "V4检查对象",
            "每个仍在48小时观察窗口内的事件标的",
            "事件只是先证明该币过去24h已经足够强；V4是在事件之后继续寻找新的1小时二次点火。",
        ),
        (
            "V4使用哪根K线",
            "最新一根已完成的1h K线",
            "不使用正在形成中的小时K线，避免盘中信号回撤后消失。",
        ),
        (
            "量能倍数公式",
            "signal_quote_volume / mean(previous_20_quote_volume)",
            "分子是信号这根1h K线的quote volume；分母是它前20根已完成1h K线的平均quote volume。",
        ),
        (
            "量能倍数>3.0是什么意思",
            "当前1小时成交额 > 过去20小时平均每小时成交额的3倍",
            "3.0不是相对24h成交额，也不是相对全市场成交额；它是同一个币自己的短期成交额突增。",
        ),
        (
            "1h涨幅公式",
            "signal_close / signal_open - 1",
            "涨幅只看信号这根1h K线自身的收盘价相对开盘价，不是24h涨幅。",
        ),
        (
            "1h涨幅>1%是什么意思",
            "信号这根1小时K线本身上涨超过1%",
            "它要求成交量突增时价格也同向上涨，过滤掉放量下跌或放量横盘。",
        ),
        (
            "为什么不是和24h涨幅重复",
            "24h涨幅≥30%定义事件背景；1h涨幅>1%定义事件后的即时二次点火",
            "一个币过去24h涨了30%，但接下来1小时可能下跌、横盘或继续上冲；V4只接受继续上冲的小时。",
        ),
        (
            "为什么1%看起来不大",
            "因为它不是单独使用，而是叠加在30%事件和3倍量能突增之后",
            "1%的作用是确认方向，不是单独提供alpha；真正的过滤来自事件上下文+量能突增+正向价格响应。",
        ),
        (
            "当前V4触发条件",
            f"量能倍数>{cfg.get('v4_volume_ratio_min')} 且 1h涨幅>{pct(cfg.get('v4_return_min'), 0)}",
            "两个条件必须同时满足，任一不满足都不会paper入场。",
        ),
    ]
    return render_kv_table(rows)


def render_v4_example() -> str:
    rows = [
        ("前20小时平均成交额", "$2,000,000 / 小时", "这是分母。"),
        ("最新已完成1h成交额", "$7,000,000", "这是分子。"),
        ("量能倍数", "7,000,000 / 2,000,000 = 3.5x", "3.5 > 3.0，量能条件通过。"),
        ("这根1h开盘价", "0.1000", "信号K线open。"),
        ("这根1h收盘价", "0.1015", "信号K线close。"),
        ("1h涨幅", "0.1015 / 0.1000 - 1 = +1.50%", "1.50% > 1%，价格条件通过。"),
        ("V4结果", "触发", "如果该K线在事件后1~48小时内，且未处理过，就会进入paper入场流程。"),
    ]
    return render_kv_table(rows)


def render_v4_threshold_discussion() -> str:
    rows = [
        (
            "1%是不是太小",
            "单独看确实不强；放在本策略中，它不是独立信号，而是二次确认条件",
            "如果没有事件上下文，V4裸信号中位数只有约+0.04%，说明1%本身不足以构成强alpha。",
        ),
        (
            "为什么回测仍采用1%",
            "回测发现事件+V4后，固定止损下中位数显著高于裸V4",
            "这说明1%阈值的作用是捕捉事件后的继续点火，而不是过滤所有普通1%上涨。",
        ),
        (
            "调高到2%/3%的潜在好处",
            "信号更强，可能减少噪音和追高失败",
            "但样本会减少，可能错过刚开始点火的交易；需要重新回测，不应直接手改。",
        ),
        (
            "调低到0%/0.5%的潜在问题",
            "信号更多，入场更早",
            "但可能包含大量放量但方向不够明确的噪音，滑点后优势更容易消失。",
        ),
        (
            "下一步讨论方式",
            "可以单独做 V4 return threshold sensitivity：0.5%、1%、1.5%、2%、3%",
            "每个阈值都要看样本数、中位数、PF、胜率、年份稳定性、滑点压力和paper可执行性。",
        ),
    ]
    return render_kv_table(rows)


def render_same_hour_backtest_audit() -> str:
    rows = [
        (
            "审计问题",
            "如果实盘在 12:02 扫描，是否允许立刻用 11:00-12:00 已完成K线作为事件+V4信号",
            "历史上等价于把事件窗口从 signal_ts > event_ts 放宽到 signal_ts >= event_ts，也就是允许 lag=0 同小时V4。",
        ),
        (
            "当前正确SL-only基准",
            "1,951 笔；均值 +1.77%；中位数 -8.07%；胜率 16.8%；PF 1.27；收益求和 +34.50",
            "这是当前采用的 post-event 口径：事件后第1~48小时内找第一个V4，8% SL / 96h timeout，4bps/side。",
        ),
        (
            "允许同小时V4",
            "2,703 笔；均值 +0.88%；中位数 -8.07%；胜率 15.3%；PF 1.13；收益求和 +23.74",
            "交易更多，但每笔质量明显下降；不是盈利更多，而是盈利更少。",
        ),
        (
            "为什么会变差",
            "新增 752 笔同小时交易均值 -6.06%，中位数 -8.07%，胜率 7.2%，PF 0.18，收益求和 -45.58",
            "新增交易主要是事件爆发当小时的追高噪音，绝大多数直接或很快触发8%止损。",
        ),
        (
            "一个细节",
            "对已有后续V4的 465 个事件，同小时提前入场的成对收益差为 +34.82；但新增同小时交易亏损 -45.58，最终净效果为负",
            "这说明不能只看“提前入场可能更好”的个例；放宽规则会引入大量当前基准本来不会交易的差样本。",
        ),
        (
            "结论",
            "不要把当前策略改成允许同小时V4入场",
            "保持事件后第1根小时K开始等待V4，更符合当前回测优势来源，也避免把事件当小时的爆发K线当作确认信号追进去。",
        ),
    ]
    return render_kv_table(rows)


def render_backtest_snapshot() -> str:
    rows = [
        (
            "核心回测结论",
            "事件上下文 + V4 + 固定止损，是目前 Phase2a 中最值得 paper 验证的组合",
            "V4 裸信号在全市场出现太频繁，事件上下文才是把噪音过滤成二次点火信号的关键。",
        ),
        (
            "事件检测审计",
            "全量扫描 4,605 个事件，与现有事件叠加层 100% 一致，仅发现 1 个小时边界差异",
            "说明历史事件层不是 rank450 预筛选造成的伪结果；事件来源本身相对可信。",
        ),
        (
            "V4裸信号 + 固定止损",
            "样本 88,889；均值 +1.02%；中位数 +0.04%；胜率 58.4%；PF 9.82",
            "能从负期望翻正，但中位数极薄，说明裸信号大多只是噪声或短暂流动性冲击。",
        ),
        (
            "事件 + V4 + 固定止损",
            "回测中位数约 +0.82%，约为 V4 裸信号中位数的 20 倍",
            "这说明 alpha 主要来自“已经暴涨后的二次点火”条件概率，而不是单纯成交量放大。",
        ),
        (
            "30bps滑点压力测试",
            "8% SL 在 30bps 单边滑点下仍保持正中位数，PF 约 6.33，5/5 年正中位数",
            "这是选择 8% SL 而不是更窄或更宽参数的重要理由。",
        ),
        (
            "同小时V4时间口径审计",
            "允许事件当小时V4后，均值从 +1.77% 降到 +0.88%，PF 从 1.27 降到 1.13",
            "新增 752 笔同小时交易均值 -6.06%、PF 0.18，说明 12:02 立刻交易刚完成的事件K线会拉低历史收益。",
        ),
        (
            "落地前提",
            "只在 paper/live 都严格复刻这套 SL-only 语义后，再讨论是否扩大仓位或改参数",
            "任何重新加回 trailing、分钟级止盈或本地修补的改动，都应视为新策略而不是当前策略的延续。",
        ),
    ]
    return render_kv_table(rows)


def render_same_vs_different(cfg: dict[str, Any]) -> str:
    live_cap = float(live_cfg(cfg).get("max_effective_notional_usdt", 0.0))
    rows = [
        ("一致", "事件阈值", "rank≤20、24h涨幅≥30%、24h成交额≥$5M，与回测主口径一致。"),
        ("一致", "V4定义", "已完成1h K线：quote volume > 前20根已完成1h均值的3倍，且1h涨幅>1%。"),
        ("一致", "事件窗口", "事件后1到48小时内等待V4，事件本身那根K线不入场。"),
        ("一致", "方向", "只做多，交易逻辑是强势事件后的延续/二次点火。"),
        ("一致", "退出思想", "使用固定止损 + 96h 超时退出，目标是保留延续段、截断回撤。"),
        ("一致", "Paper与Live信号源", "Live不单独产生信号，只复用同一个paper trade_id 下的事件、V4和退出判定。"),
        ("不一致", "事件排名数据源", "回测使用离线全量1h历史重建；paper使用实盘可获得的 Binance rolling 24h ticker。"),
        ("不一致", "事件时间对齐", "paper按每小时:02:15扫描时的最近小时边界记事件；历史回测可在完整数据上精确重建。"),
        ("不一致", "入场成交", "回测参考信号K线收盘价；paper用bookTicker ask模拟市价买入，并记录滑点。"),
        ("不一致", "退出成交", "回测只知道完成K线 low 触发了固定 SL；paper 用完成1h K线复现该语义，live 用交易所 STOP_MARKET 成交。"),
        ("不一致", "盘口深度和冲击", "paper只用best bid/ask和固定notional，不模拟订单簿深度、大额冲击、交易失败和撮合排队。"),
        ("不一致", "资金费率/借贷/保证金", "当前paper主要记录价格收益和taker费，未把资金费率、保证金占用、爆仓风险作为收益项。"),
        ("不一致", "Live真实撮合", "Live使用交易所真实市价单和 STOP_MARKET，可能出现部分成交、API拒绝、平均成交价与bookTicker不同、账户模式差异等paper没有的情况。"),
        ("不一致", "Live仓位规模", f"Live是 ${live_cap:,.0f} 以内小仓位canary，不等同于paper的纸面名义本金；它用于验证执行质量，不用于放大收益。"),
    ]
    out = "<table><thead><tr><th>类别</th><th>项目</th><th>说明</th></tr></thead><tbody>"
    for cls, item, note in rows:
        out += f"<tr><td>{escape(cls)}</td><td>{escape(item)}</td><td>{escape(note)}</td></tr>"
    out += "</tbody></table>"
    return out


def render_profitability_judgement(status: dict[str, Any], cfg: dict[str, Any]) -> str:
    live_cap = float(live_cfg(cfg).get("max_effective_notional_usdt", 0.0))
    closed = int(status.get("closed_trades") or 0)
    live_closed = int(status.get("live_closed_trades") or 0)
    if closed == 0:
        paper_state = "当前 paper 尚无平仓样本，不能用实盘样本证明盈利。"
    elif closed < 30:
        paper_state = f"当前 paper 已平仓 {closed} 笔，样本仍太少，只能做运行质量检查，不能做统计结论。"
    elif closed < 50:
        paper_state = f"当前 paper 已平仓 {closed} 笔，可做初筛复盘，但仍未达到正式放行样本。"
    else:
        paper_state = f"当前 paper 已平仓 {closed} 笔，可以开始和回测中位数、胜率、PF、滑点分布做正式对照。"
    rows = [
        (
            "是否有把握盈利",
            "没有到“有把握”的级别；只能说回测支持正期望假设，paper正在验证",
            "原因是当前paper样本不足，且实盘口径与回测存在执行、滑点、事件时间和监控频率差异。",
        ),
        (
            "为什么仍值得验证",
            "事件+V4组合的中位数显著高于V4裸信号，并且30bps压力测试仍为正",
            "这说明策略不是只靠少数极端大赚，也不是只靠无成本假设；但仍需paper样本确认。",
        ),
        (
            "当前paper证据",
            paper_state,
            "在没有足够平仓交易前，页面上的重点应是信号是否按口径产生、是否漏信号、滑点是否异常。",
        ),
        (
            "当前live证据",
            f"当前 live 已平仓 {live_closed} 笔；live 只用于验证真实下单链路和执行差异，样本不足前不能代表策略盈利能力。",
            f"Live每笔 ${live_cap:,.0f} 以内，能暴露账户模式、撮合、价差、API失败等paper看不到的问题；但仓位小且样本少，不应外推为稳定收益。",
        ),
        (
            "建议放行标准",
            "至少30笔做初筛，50笔以上做正式复盘；同时要求中位数为正、滑点可控、无系统性漏信号",
            "若paper中位数接近0或滑点持续吞噬收益，应暂停实盘化并回到规则审计。",
        ),
    ]
    return render_kv_table(rows)


def render_strengths_weaknesses_risks(cfg: dict[str, Any]) -> str:
    live_cap = float(live_cfg(cfg).get("max_effective_notional_usdt", 0.0))
    rows = [
        ("优势", "事件上下文强", "不是全市场追每一个量价异动，而是在30%+强势事件后寻找二次点火，条件概率更好。"),
        ("优势", "回测审计较充分", "事件层经过全量宇宙复扫验证，未发现预筛选偏差；V4裸信号与事件+V4也做了对照。"),
        ("优势", "退出规则单一", "固定 8% SL + 96h timeout 避免了 trailing 在回测与实盘之间的巨大解释差异。"),
        ("优势", "paper透明度高", "事件、V4检查、入场、退出、滑点、拒绝、runner日志均落CSV并在页面展示。"),
        ("劣势", "事件很少，样本积累慢", "等待30到50笔paper交易可能需要较长时间，短期表现噪声会很大。"),
        ("劣势", "边际收益可能被执行吞噬", "虽然回测30bps仍好，但真实小币瞬时价差、跳价、盘口深度可能比假设更差。"),
        ("劣势", "rolling ticker 与历史重建不完全一致", "paper使用实盘ticker的滚动24h口径，可能与离线1h回测事件边界不同。"),
        ("劣势", "只做多且依赖市场风险偏好", "熊市、系统性去杠杆或交易所风险事件中，强势小币也可能快速反转。"),
        ("风险", "追高风险", "事件本身已经上涨30%+，V4入场可能发生在情绪后段，若二次点火失败会快速回撤。"),
        ("风险", "小币流动性/滑点风险", "$5M 24h成交额只是底线，不代表盘口深度足够；实盘notional放大后风险非线性增加。"),
        ("风险", "K线粒度风险", "paper 止损按完成 1h K线 low 判定，live 用真实 stop market；两者已尽量映射，但仍不等于逐笔成交路径。"),
        ("风险", "参数过拟合风险", "8% SL / 96h timeout 仍然是研究口径，不应在小样本 live 里擅自加回 trailing 或其它本地修补。"),
        ("风险", "交易所/API风险", "Binance API延迟、限速、维护、下架、异常价格都可能导致漏信号或错误退出。"),
        ("风险", "Live订单风险", f"市价单保证成交优先，但在小币上可能出现跳价；因此当前强制 ${live_cap:,.0f} 以内、1x、最多1个live持仓，并完整记录订单回报。"),
    ]
    out = "<table><thead><tr><th>类型</th><th>点位</th><th>审计说明</th></tr></thead><tbody>"
    for kind, item, note in rows:
        out += f"<tr><td>{escape(kind)}</td><td>{escape(item)}</td><td>{escape(note)}</td></tr>"
    out += "</tbody></table>"
    return out


def render_charts(
    closed_df: pd.DataFrame,
    monitor_df: pd.DataFrame,
    accepted_events: int,
    v4_triggers: int,
    paper_entry_count: int,
    paper_exit_count: int,
) -> str:
    """Render interactive Chart.js visualizations for the report."""
    parts: list[str] = []

    # --- Section open ---
    parts.append(
        '<h2>交易可视化</h2>'
        '<p class="small">交互式图表：悬停查看详情，点击图例切换显示。数据来自 paper 影子账本。</p>'
        '<div class="chart-grid">'
    )

    # --- 1. Signal Funnel ---
    funnel_labels = json.dumps(["事件接收", "V4触发", "Paper入场", "Paper退出"])
    funnel_data = json.dumps([accepted_events, v4_triggers, paper_entry_count, paper_exit_count])
    parts.append(
        '<div class="chart-card">'
        '<h3>信号漏斗</h3>'
        '<canvas id="funnelChart" height="220"></canvas>'
        '</div>'
    )

    # --- 2. P&L Breakdown ---
    has_pnl = not closed_df.empty
    pnl_json = "[]"
    if has_pnl:
        trades = []
        for _, row in closed_df.iterrows():
            trades.append({
                "label": str(row.get("symbol", ""))[:10],
                "net": round(float(row.get("net_return", 0)) * 100, 2),
                "theo": round(float(row.get("theoretical_return_before_fees", 0)) * 100, 2),
                "drag": round(float(row.get("entry_to_exit_slippage_drag", 0)) * 100, 2),
            })
        pnl_json = json.dumps(trades)
        parts.append(
            '<div class="chart-card">'
            '<h3>盈亏分解 (%)</h3>'
            '<canvas id="pnlChart" height="220"></canvas>'
            '</div>'
        )

    # --- 3. Price + Stop Loss ---
    has_price = not monitor_df.empty
    price_json = "{}"
    if has_price:
        price_data: dict[str, dict[str, list]] = {}
        for _, row in monitor_df.iterrows():
            tid = str(row.get("trade_id", ""))
            if not tid:
                continue
            sym = tid.split("|")[0]
            if tid not in price_data:
                price_data[tid] = {"sym": sym, "times": [], "prices": [], "stops": [], "hwms": []}
            t = str(row.get("checked_at_utc", ""))
            price_data[tid]["times"].append(t[11:16] if len(t) > 16 else t)
            price_data[tid]["prices"].append(float(row.get("current_exit_ref", 0)))
            price_data[tid]["stops"].append(float(row.get("stop_loss_price", 0)))
            price_data[tid]["hwms"].append(float(row.get("high_water_mark", 0)))
        price_json = json.dumps(price_data)
        parts.append(
            '<div class="chart-card chart-wide">'
            '<h3>价格走势 vs 固定止损线</h3>'
            '<canvas id="priceChart" height="300"></canvas>'
            '</div>'
        )

    parts.append('</div>')  # close chart-grid

    # --- Chart.js scripts ---
    sp: list[str] = []
    sp.append('<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>')
    sp.append('<script>(function(){')
    sp.append(
        'var C={green:"#86efac",red:"#fca5a5",blue:"#7dd3fc",'
        'yellow:"#fde68a",purple:"#c4b5fd",orange:"#fdba74"};'
        'Chart.defaults.color="#94a3b8";Chart.defaults.borderColor="#334155";'
    )

    # Funnel
    sp.append(
        'var fc=document.getElementById("funnelChart");'
        'if(fc){new Chart(fc,{type:"bar",'
        'data:{labels:' + funnel_labels + ','
        'datasets:[{data:' + funnel_data + ','
        'backgroundColor:[C.blue,C.yellow,C.green,C.purple],borderRadius:6}]},'
        'options:{responsive:true,plugins:{legend:{display:false}},'
        'scales:{y:{beginAtZero:true,ticks:{stepSize:1}}}}});}'
    )

    # P&L
    if has_pnl:
        sp.append(
            'var pc=document.getElementById("pnlChart");'
            'if(pc){var td=' + pnl_json + ';'
            'new Chart(pc,{type:"bar",'
            'data:{labels:td.map(function(t){return t.label}),'
            'datasets:['
            '{label:"Paper净收益%",data:td.map(function(t){return t.net}),'
            'backgroundColor:td.map(function(t){return t.net>=0?C.green:C.red}),borderRadius:4},'
            '{label:"回测参考%",data:td.map(function(t){return t.theo}),'
            'backgroundColor:C.blue+"80",borderRadius:4},'
            '{label:"执行拖累%",data:td.map(function(t){return t.drag}),'
            'backgroundColor:C.orange+"80",borderRadius:4}'
            ']},options:{responsive:true,plugins:{legend:{position:"bottom"}},'
            'scales:{y:{beginAtZero:true,ticks:{callback:function(v){return v+"%"}}}}}});}'
        )

    # Price + Trail
    if has_price:
        sp.append(
            'var pp=document.getElementById("priceChart");'
            'if(pp){var pd=' + price_json + ';'
            'var ds=[];var pl=[C.green,C.blue,C.yellow,C.purple,C.orange];var ci=0;'
            'var fk=Object.keys(pd)[0];'
            'for(var k in pd){var d=pd[k];var c=pl[ci%pl.length];'
            'ds.push({label:d.sym+" 价格",data:d.prices,'
            'borderColor:c,backgroundColor:c+"20",fill:false,tension:0.3,pointRadius:2});'
            'ds.push({label:d.sym+" 止损线",data:d.stops,'
            'borderColor:c,borderDash:[5,5],fill:false,pointRadius:0});ci++;}'
            'new Chart(pp,{type:"line",'
            'data:{labels:pd[fk].times,datasets:ds},'
            'options:{responsive:true,interaction:{mode:"index",intersect:false},'
            'plugins:{legend:{position:"bottom"}},'
            'scales:{y:{ticks:{callback:function(v){return v.toFixed(6)}}}}}});}'
        )

    sp.append('})();</script>')

    return "\n".join(parts) + "\n" + "\n".join(sp)


def write_report(cfg: dict[str, Any], p: dict[str, Path], status: dict[str, Any]) -> None:
    ensure_dir(p["report"].parent)
    open_df = read_csv(p["open_positions"])
    closed_df = read_csv(p["closed_trades"])
    event_df = read_csv(p["event_log"])
    signal_df = read_csv(p["signal_log"])
    monitor_df = read_csv(p["monitor_marks"])
    rejection_df = read_csv(p["rejections"])
    slippage_df = read_csv(p["slippage_audit"])
    live_open_df = read_csv(p["live_open_positions"])
    live_closed_df = read_csv(p["live_closed_trades"])
    live_orders_df = read_csv(p["live_orders"])
    live_monitor_df = read_csv(p["live_monitor_marks"])
    live_rejection_df = read_csv(p["live_rejections"])
    run_df = read_csv(p["run_log"])
    state = load_state(p["state"])
    active_event_df = pd.DataFrame(list(state.get("active_events", {}).values()))
    accepted_events = truthy_count(event_df, "accepted")
    active_signal_checks = truthy_count(signal_df, "in_event_window")
    v4_triggers = truthy_count(signal_df, "v4_triggered")
    paper_entry_count = int((slippage_df["side"].astype(str) == "entry").sum()) if not slippage_df.empty and "side" in slippage_df else 0
    paper_exit_count = int((slippage_df["side"].astype(str) == "exit").sum()) if not slippage_df.empty and "side" in slippage_df else 0
    systemd_rows = [
        ("服务安装位置", "/etc/systemd/system/momentum-phase2a-event-v4-trail-*.service", "旧 service 文件名暂保留；执行口径已切换为 SL-only，新账本落在 sl_only 目录。"),
        ("扫描频率", "每小时 :02:15 UTC", "检测极端事件、检查已完成1h K线的V4信号，并在满足条件时记录paper入场；live开启时同步小仓位真实入场。"),
        ("退出/超时监控频率", "每分钟 :20 UTC", "paper 按完成1h K线检查固定止损和96小时硬超时；live 查询 STOP_MARKET 状态，超时才真实市价退出。"),
        ("状态写锁", rel(p["lock"]), "单写者文件锁，避免 scan 和 monitor 同时写 state.json。"),
        ("运行日志", "journalctl -u momentum-phase2a-event-v4-trail-*.service", "旧 service 名称仍可查日志；若后续改名为 sl_only，再同步替换这里。"),
    ]
    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Phase2a 事件+V4 SL-only Paper/Live 审计面板</title>
<style>
body{{margin:0;background:#0b1220;color:#e5e7eb;font:14px/1.65 -apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans SC',sans-serif}}
.wrap{{max-width:1280px;margin:0 auto;padding:26px 18px 60px}} a{{color:#7dd3fc}} h1{{margin:0 0 8px}} h2{{margin:28px 0 10px;color:#cbd5e1;border-bottom:1px solid #334155;padding-bottom:5px}} h3{{margin:18px 0 8px;color:#dbeafe}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin:14px 0}} .card{{background:#111827;border:1px solid #243044;border-radius:8px;padding:12px}}
.k{{font-size:12px;color:#94a3b8}} .v{{font-size:20px;font-weight:800}} .muted{{color:#94a3b8}} .ok{{color:#86efac}} .warn{{color:#fde68a}} code{{background:#020617;color:#fde68a;padding:2px 5px;border-radius:5px}}
table{{width:100%;border-collapse:collapse;background:#111827;border:1px solid #243044;margin:10px 0 22px}} th,td{{border-bottom:1px solid #243044;padding:7px 8px;text-align:left;font-size:12px;vertical-align:top}} th{{background:#0f172a;color:#cbd5e1}}
.scroll{{overflow-x:auto}} .note{{background:#0f172a;border-left:3px solid #38bdf8;padding:10px 12px;margin:12px 0;color:#cbd5e1}} .lead{{max-width:980px;color:#cbd5e1}} .small{{font-size:12px;color:#94a3b8}}
.flow{{display:flex;flex-direction:column;gap:12px;margin:12px 0 24px}} .flow-row{{display:grid;grid-template-columns:minmax(190px,1fr) 24px minmax(190px,1fr) 24px minmax(190px,1fr);gap:8px;align-items:stretch}} .flow-box{{background:#111827;border:1px solid #334155;border-radius:8px;padding:10px 12px;color:#dbeafe;font-size:12px;line-height:1.55}} .flow-box b{{color:#f8fafc;font-size:13px}} .flow-box.decision{{border-color:#f59e0b;background:#15130b}} .flow-arrow{{display:flex;align-items:center;justify-content:center;color:#7dd3fc;font-weight:800}} @media(max-width:820px){{.flow-row{{grid-template-columns:1fr}} .flow-arrow{{transform:rotate(90deg);height:18px}}}}
.chart-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:16px;margin:14px 0}} .chart-card{{background:#111827;border:1px solid #243044;border-radius:8px;padding:16px}} .chart-card h3{{margin:0 0 12px;color:#dbeafe;font-size:14px}} .chart-wide{{grid-column:1/-1}}
</style>
</head>
<body><div class="wrap">
<h1>Phase2a 事件 + V4 + SL-only Paper/Live 审计面板</h1>
<p class="muted">更新时间 {escape(str(status.get('updated_at_utc')))} · Paper影子账本 + 小仓位Live canary · Live仅在配置开启且账户桥接可用时真实下单</p>
<p class="lead">这页用来回答三个问题：第一，系统现在有没有稳定地按宿主机 timer 跑；第二，每一个事件、信号、paper成交、live订单和退出判断是否都能追溯；第三，回测、paper和live三本账哪里一致、哪里仍然存在执行差异。</p>
<div class="grid">
<div class="card"><div class="k">观察中的事件</div><div class="v">{status.get('active_events')}</div></div>
<div class="card"><div class="k">当前持仓</div><div class="v">{status.get('open_positions')}</div></div>
<div class="card"><div class="k">Live当前持仓</div><div class="v">{status.get('live_open_positions')}</div></div>
<div class="card"><div class="k">已平仓交易</div><div class="v">{status.get('closed_trades')}</div></div>
<div class="card"><div class="k">Live已平仓</div><div class="v">{status.get('live_closed_trades')}</div></div>
<div class="card"><div class="k">累计接收事件</div><div class="v">{accepted_events}</div></div>
<div class="card"><div class="k">V4触发次数</div><div class="v">{v4_triggers}</div></div>
<div class="card"><div class="k">Paper入场次数</div><div class="v">{paper_entry_count}</div></div>
<div class="card"><div class="k">Paper退出次数</div><div class="v">{paper_exit_count}</div></div>
<div class="card"><div class="k">已平仓中位收益</div><div class="v">{pct(status.get('median_closed_net_return'))}</div></div>
<div class="card"><div class="k">Live中位收益</div><div class="v">{pct(status.get('median_live_closed_net_return'))}</div></div>
<div class="card"><div class="k">已平仓胜率</div><div class="v">{pct(status.get('win_rate'), 1)}</div></div>
<div class="card"><div class="k">Live胜率</div><div class="v">{pct(status.get('live_win_rate'), 1)}</div></div>
<div class="card"><div class="k">平均入场滑点</div><div class="v">{num(status.get('avg_entry_slippage_bps'), 1)} bps</div></div>
</div>
<p>固定规则：<code>rank≤{cfg.get('event_rank_max')}</code>，<code>24h涨幅≥{pct(cfg.get('event_ret24_min'),0)}</code>，<code>24h成交额≥${float(cfg.get('event_quote_volume_min')):,.0f}</code>，V4 <code>量能倍数≥{cfg.get('v4_volume_ratio_min')}，基准为 rolling{cfg.get('v4_volume_avg_bars')} 已完成小时且包含信号K线</code> + <code>close-to-close 1h涨幅≥{pct(cfg.get('v4_return_min'),0)}</code>，固定止损 <code>{pct(cfg.get('stop_loss_pct', 0.08),0)}</code>，最长持仓 <code>{cfg.get('hard_timeout_hours')}</code>h。</p>
<div class="note">时间硬约束：若 12:02 发现 <code>event_ts=12:00</code>，则 11:00-12:00 的已完成K线只用于发现事件，不允许作为V4入场信号；最早检查 12:00-13:00 K线，即 13:02 才可能开仓。</div>
{render_charts(closed_df, monitor_df, accepted_events, v4_triggers, paper_entry_count, paper_exit_count)}
<div class="note">怎么看：先看“信号漏斗”判断系统卡在哪一步；再看“事件记录”和“V4检查记录”确认为什么没有入场；有持仓后同时看 paper 监控、live 订单和 live 退出监控，检查真实成交是否偏离 paper 和回测参考口径。</div>
<h2>运行状态</h2>
<p class="small">这一段确认程序是否以宿主机 systemd timer 方式持续运行，而不是临时 shell 或沙箱后台进程。</p>
{render_kv_table(systemd_rows)}
<h2>自动平仓事故复盘</h2>
<p class="small">这段是针对 2026-05-20/21 排查出的自动退出异常补充的透明审计。重点区分两件事：真实账户当前是否还有风险，以及本地 paper/live 账本是否曾经漏记退出。</p>
{render_autoclose_incident_audit(status=status, run_df=run_df, rejection_df=rejection_df, live_rejection_df=live_rejection_df)}
<h2>策略生命周期说明</h2>
<p class="small">这一段专门解释容易混淆的概念：事件不是交易，已接收事件也不等于“此刻仍满足事件条件”；事件只是后续等待V4二次点火的上下文。</p>
{render_strategy_lifecycle(cfg)}
<h2>当前事件定义</h2>
<p class="small">这里回答最基础的问题：到底什么叫一个事件、多久检查一次、现在用的是前20还是前30。</p>
{render_event_definition(cfg)}
<h2>完整执行流程图</h2>
<p class="small">这张图从每小时事件扫描开始，一直到V4计算、盘口检查、paper入场、每分钟退出监控、paper平仓和审计落盘。黄色边框表示关键判断点。</p>
{render_process_flowchart(cfg)}
<h2>Live小仓位实盘控制</h2>
<p class="small">Live不是新策略，而是同一 Phase2a 信号的真实成交账本。当前目标是用配置上限 ${float(live_cfg(cfg).get('max_effective_notional_usdt', 0.0)):,.0f} 以内小仓位验证“能不能按回测/paper口径真实执行”，不是用小样本证明盈利。</p>
{render_live_controls(cfg)}
<h2>回测 vs Paper vs Live 统一对照</h2>
<p class="small">三本账用同一 trade_id 串起来：回测给历史基准，paper给前向可执行模拟，live给交易所真实成交。真正复盘时重点看 live 是否系统性劣于 paper。</p>
{render_backtest_paper_live_comparison(status)}
<h2>当前审计结论</h2>
<p class="small">现在这页的结论不是“没有问题”，而是“策略语义已经收敛到 SL-only，但纸面执行和真实执行仍存在需要持续盯紧的差异”。</p>
{render_kv_table([
    ("当前状态", f"paper_open={status.get('open_positions')}，live_open={status.get('live_open_positions')}", "paper 是前向影子账本，live 是真实小仓位账本；两者需要分开看。"),
    ("当前口径", "SL-only", "固定 8% 止损 + 96h timeout 是当前唯一认可的前向口径。"),
    ("仍需盯紧的差异", "事件源、入场价、退出价、超时成交", "这些差异不会消失，只能在审计里显式展示并逐笔对账。"),
    ("不再接受的改动", "trailing / 分钟级止盈 / 本地修补", "这些都会重新制造回测-实盘错位，若要重做必须视为新策略。"),
])}
<h2>V4信号到底怎么算</h2>
<p class="small">V4不是“24h已经涨30%以后再随便追1%”。它检查的是事件发生之后，最新一根已完成1h K线是否出现“成交额突然放大，同时价格继续向上”的二次点火。</p>
{render_v4_definition(cfg)}
<h2>V4计算示例</h2>
<p class="small">下面是一个简化例子，用来说明“3.0倍”和“1h涨幅1%”分别是谁相对于谁。</p>
{render_v4_example()}
<h2>关于1h涨幅1%的解释</h2>
<p class="small">1%阈值需要谨慎理解：它不是单独的入场理由，而是叠加在“24h涨幅≥30%的事件”和“当前小时成交额超过过去20小时均值3倍”之后的方向确认。</p>
{render_v4_threshold_discussion()}
<h2>回测证据摘要</h2>
<p class="small">这一段回答“为什么选择这条策略”。它不是盈利保证，而是说明回测中哪些证据支持继续做paper验证。</p>
{render_backtest_snapshot()}
<h2>同小时V4入场审计</h2>
<p class="small">这段专门回答“12:02 是否可以直接用 11:00-12:00 完成K线决定V4并入场”。结果基于同一份历史事件、同一份V4信号、同一个正确SL-only退出函数。</p>
{render_same_hour_backtest_audit()}
<p class="small">完整实验页：<a href="../phase2a_same_hour_sl_only_audit/report.html">Phase2a 同小时V4 SL-only 回测审计</a>；可复跑脚本：<code>scripts/backtest_phase2a_same_hour_sl_only_audit.py</code>。</p>
<h2>一致与不一致</h2>
<p class="small">这里是最关键的口径审计：左边“一致”说明paper在复刻回测规则；“不一致”说明实盘环境无法完全等同回测，后续复盘必须重点盯这些差异。</p>
{render_same_vs_different(cfg)}
<h2>可盈利性判断</h2>
<p class="small">结论要保守：回测说明它值得验证，但paper样本尚未证明它已经能稳定赚钱。真正的放行条件应来自后续paper交易样本。</p>
{render_profitability_judgement(status, cfg)}
<h2>优势、劣势与风险</h2>
<p class="small">这一段按批判性视角列出。优势说明为什么它可能有效；劣势和风险说明为什么不能直接从回测跳到实盘重仓。</p>
{render_strengths_weaknesses_risks(cfg)}
<h2>回测口径 vs Paper口径</h2>
<p class="small">这一段用于质量把控。Paper 无法完全等同回测，因为实盘只能看到当下 rolling ticker、且成交要按 bid/ask 模拟；但每个差异都在这里明示并记录。</p>
{render_rule_parity(cfg)}
<h2>信号漏斗</h2>
<p class="small">从左到右理解：先发现事件，再在事件窗口内等待V4二次点火；V4触发后才记录paper入场；之后由 monitor 按完成的 1h K线管理固定止损和平仓。</p>
{render_kv_table([
    ('事件记录行数', len(event_df), '每次符合基础事件条件的 ticker 快照都会记录；重复事件、冷却期拒绝也会记录。'),
    ('累计接收事件', accepted_events, '历史上被纳入观察窗口的事件数量；不等于此刻仍满足事件三条件。'),
    ('当前观察中事件', status.get('active_events'), f'已接收且尚未超过{cfg.get("event_watch_hours")}小时观察期的事件。'),
    ('V4检查次数', len(signal_df), '对观察中事件检查已完成1h K线的次数。'),
    ('事件窗口内检查', active_signal_checks, '时间上允许入场的V4检查次数；事件本身那根K线不算。'),
    ('V4触发次数', v4_triggers, '量能倍数和1h涨幅两个条件同时通过。'),
    ('Paper入场', paper_entry_count, 'V4触发后按 bookTicker ask 记录模拟买入。'),
    ('Paper退出', paper_exit_count, '按 bookTicker bid，由固定止损或96小时超时模拟卖出。'),
    ('拒绝/错误', len(rejection_df), '包括盘口价差过大、API错误、状态异常等运行层问题。'),
])}
<h2>当前观察中的事件</h2>
<p class="small">这里展示还在有效观察期内的事件。只要未到“观察到期UTC”，系统就会继续等待后续已完成1h K线是否触发V4。</p>
<div class="scroll">{render_table(active_event_df, columns=['event_id','symbol','event_ts_utc','expires_at_utc','event_rank','event_ret24','event_quote_volume_24h','last_price','entered','entry_trade_id'])}</div>
<h2>当前持仓</h2>
<p class="small">有持仓时，这里展示入场价、最近监控价、高水位、止损线和硬超时时间。核心看“最近监控价”和“止损线”的距离。</p>
<div class="scroll">{render_table(open_df, columns=['trade_id','symbol','entry_ts_utc','paper_entry_price','last_mark_price','high_water_mark','stop_loss_price','max_favorable_excursion','hard_timeout_at_utc','notional_usdt','qty'])}</div>
<h2>当前Live实盘持仓</h2>
<p class="small">这里是真实账户中由本策略创建并仍由本策略管理的live小仓位。核心看 live 入场价、paper入场价、当前高水位和止损线。</p>
<div class="scroll">{render_table(live_open_df, columns=['trade_id','symbol','entry_ts_utc','live_entry_price','paper_entry_price','last_mark_price','high_water_mark','stop_loss_price','hard_timeout_at_utc','live_notional_usdt','live_qty','entry_order_id','entry_status','entry_slippage_bps_vs_paper'])}</div>
<h2>最近平仓交易</h2>
<p class="small">平仓后重点看扣费后收益、回测参考收益和执行拖累。执行拖累持续偏大时，说明实盘滑点/价差正在侵蚀回测优势。</p>
<div class="scroll">{render_table(closed_df, columns=['trade_id','symbol','entry_ts_utc','exit_ts_utc','exit_reason','paper_entry_price','paper_exit_price','net_return','theoretical_return_before_fees','entry_to_exit_slippage_drag','hold_hours','max_favorable_excursion'])}</div>
<h2>最近Live实盘平仓</h2>
<p class="small">这里展示真实成交后的收益。重点看 live_net_return 与 paper_net_return 的差值：若持续为负，说明真实执行正在吞噬回测优势。</p>
<div class="scroll">{render_table(live_closed_df, columns=['trade_id','symbol','entry_ts_utc','exit_ts_utc','exit_reason','live_entry_price','live_exit_price','live_net_return','paper_net_return','live_minus_paper_return','live_pnl_usdt','hold_hours','entry_order_id','exit_order_id'])}</div>
<h2>每分钟退出监控</h2>
<p class="small">每分钟 monitor 会按 completed 1h bars 更新当前可退出价格、高水位和固定止损线。这里是检查退出执行是否及时的主日志。</p>
<div class="scroll">{render_table(monitor_df, columns=['checked_at_utc','trade_id','symbol','current_exit_ref','high_water_mark','stop_loss_price','stop_loss_pct','triggered_exit','exit_reason','spread_bps','quote_source'])}</div>
<h2>Live每分钟退出监控</h2>
<p class="small">Live监控使用同样的固定止损和96小时硬超时。触发后会通过已有账户桥接发真实市价SELL退出，并写入live_orders。</p>
<div class="scroll">{render_table(live_monitor_df, columns=['checked_at_utc','trade_id','symbol','live_entry_price','current_exit_ref','high_water_mark','stop_loss_price','stop_loss_pct','triggered_exit','exit_reason','spread_bps','quote_source'])}</div>
<h2>事件记录</h2>
<p class="small">事件来自 Binance rolling 24h ticker 排名。“是否纳入观察=是”表示进入观察窗口；“否”通常是重复事件或冷却期。</p>
<div class="scroll">{render_table(event_df, columns=['detected_at_utc','event_ts_utc','event_id','symbol','event_rank','event_ret24','event_quote_volume_24h','last_price','accepted','rejection_reason','event_detection_mode'])}</div>
<h2>V4信号检查</h2>
<p class="small">V4 只检查已完成1h K线。入场必须同时满足：在事件窗口内、未处理过、量能倍数&gt;阈值、1h涨幅&gt;阈值。</p>
<div class="scroll">{render_table(signal_df, columns=['checked_at_utc','symbol','event_ts_utc','first_eligible_signal_open_ts_utc','signal_bar_open_ts_utc','signal_bar_close_ts_utc','in_event_window','already_processed','v4_triggered','entry_block_reason','signal_close','signal_quote_volume','trailing_avg_quote_volume','vol_ratio','ret_1h','v4_volume_baseline','v4_return_basis','completed_bars'])}</div>
<h2>Paper成交与滑点审计</h2>
<p class="small">入场参考价是信号K线收盘价，paper成交价是 ask；退出参考价是止损线或退出参考价，paper成交价是 bid。滑点用 bps 记录。</p>
<div class="scroll">{render_table(slippage_df, columns=['captured_at_utc','trade_id','symbol','side','reference_price','paper_fill_price','slippage_bps','spread_bps','quote_source','exit_reason'])}</div>
<h2>Live订单记录</h2>
<p class="small">所有真实订单都会出现在这里，包括入场和退出。它是核对交易所成交、client order id、成交数量、平均成交价和名义本金是否≤配置硬上限的主表。</p>
<div class="scroll">{render_table(live_orders_df, columns=['timestamp_utc','trade_id','symbol','order_role','side','order_type','target_notional_usdt','max_effective_notional_usdt','quantity','executed_qty','avg_price','effective_notional_usdt','status','client_order_id','order_id','spread_bps'])}</div>
<h2>拒绝与错误</h2>
<p class="small">这里用于快速定位问题：如果有 API 错误、价差过大、状态冲突或其它异常，会优先出现在这里。</p>
<div class="scroll">{render_table(rejection_df, max_rows=30)}</div>
<h2>Live拒绝与错误</h2>
<p class="small">Live下单链路的拒绝会独立记录，例如价差过大、名义本金保护、账户桥接失败或交易所API异常。出现记录时优先看这一段。</p>
<div class="scroll">{render_table(live_rejection_df, max_rows=30)}</div>
<h2>Runner运行日志</h2>
<p class="small">每次 scan、monitor 或手动 status 刷新都会写入一行。若 ok=false，优先看错误类型和错误内容。</p>
<div class="scroll">{render_table(run_df, columns=['run_at_utc','ok','modes','scan_new_events','scan_signals_checked','scan_new_positions','monitor_open_positions','monitor_new_closed_trades','error_type','error'])}</div>
<h2>底层CSV/状态文件</h2>
<p class="small">页面只是这些文件的可读展示。后续排查时以这些 CSV 和 state.json 为准，可以复现每一步。</p>
<ul>
<li><code>{escape(rel(p['state']))}</code></li>
<li><code>{escape(rel(p['status']))}</code></li>
<li><code>{escape(rel(p['run_log']))}</code></li>
<li><code>{escape(rel(p['open_positions']))}</code></li>
<li><code>{escape(rel(p['closed_trades']))}</code></li>
<li><code>{escape(rel(p['event_log']))}</code></li>
<li><code>{escape(rel(p['signal_log']))}</code></li>
<li><code>{escape(rel(p['monitor_marks']))}</code></li>
<li><code>{escape(rel(p['rejections']))}</code></li>
<li><code>{escape(rel(p['slippage_audit']))}</code></li>
<li><code>{escape(rel(p['live_open_positions']))}</code></li>
<li><code>{escape(rel(p['live_closed_trades']))}</code></li>
<li><code>{escape(rel(p['live_orders']))}</code></li>
<li><code>{escape(rel(p['live_monitor_marks']))}</code></li>
<li><code>{escape(rel(p['live_rejections']))}</code></li>
</ul>
</div></body></html>"""
    p["report"].write_text(html, encoding="utf-8")


def write_summary(p: dict[str, Path], payload: dict[str, Any]) -> None:
    ensure_dir(p["run_summary"].parent)
    p["run_summary"].write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_run_log(p: dict[str, Path], payload: dict[str, Any]) -> None:
    results = payload.get("results") or []
    row: dict[str, Any] = {
        "run_at_utc": payload.get("run_at_utc"),
        "ok": payload.get("ok"),
        "modes": ",".join(str(r.get("mode", "")) for r in results if isinstance(r, dict)),
        "error_type": payload.get("error_type", ""),
        "error": payload.get("error", ""),
    }
    for result in results:
        if not isinstance(result, dict):
            continue
        mode = str(result.get("mode", "unknown"))
        for key, value in result.items():
            if key == "mode":
                continue
            row[f"{mode}_{key}"] = value
    append_csv(p["run_log"], [row])


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase2a Event+V4+SL-only paper/shadow runner")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--scan", action="store_true", help="detect events/V4 and open paper positions")
    parser.add_argument("--monitor", action="store_true", help="monitor fixed stop-loss / timeout and close paper positions")
    parser.add_argument("--status", action="store_true", help="rewrite status/report only")
    args = parser.parse_args()

    if not (args.scan or args.monitor or args.status):
        parser.error("choose at least one of --scan, --monitor, --status")

    cfg = load_config(Path(args.config))
    p = paths(cfg)
    ensure_dir(p["art_dir"])
    ensure_dir(p["site_dir"])
    now = utc_now()
    results: list[dict[str, Any]] = []

    try:
        with file_lock(p["lock"]):
            state = load_state(p["state"])
            if args.scan:
                results.append(scan(cfg, state, p, now))
            if args.monitor:
                results.append(monitor(cfg, state, p, now))
            save_state(p["state"], state)
            status = build_status(cfg, state, p, now)
            summary = {
                "run_at_utc": iso_z(now),
                "ok": True,
                "results": results or [{"mode": "status"}],
                "status_path": rel(p["status"]),
                "state_path": rel(p["state"]),
                "report_path": rel(p["report"]),
            }
            write_summary(p, summary)
            write_run_log(p, summary)
            status = build_status(cfg, state, p, now)
            write_report(cfg, p, status)
        print(json.dumps(summary, ensure_ascii=False))
        return 0
    except Exception as exc:  # noqa: BLE001
        summary = {
            "run_at_utc": iso_z(now),
            "ok": False,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "results": results,
            "state_path": rel(p["state"]),
        }
        write_summary(p, summary)
        write_run_log(p, summary)
        print(json.dumps(summary, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
