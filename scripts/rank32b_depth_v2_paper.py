#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
KLINE_1M_CACHE_DIR = ROOT / "reports" / "artifacts" / "rank32b_shadow_kline_1m_cache"
FUTURES_DEPTH = "https://fapi.binance.com/fapi/v1/depth"
FUTURES_KLINES = "https://fapi.binance.com/fapi/v1/klines"
FETCH_LIMIT = 1500
DEFAULT_TAKER_FEE_BPS = 6.0
DEFAULT_DEPTH_LIMIT = 20
DEFAULT_ORDER_NOTIONAL_USDT = 500.0
DEFAULT_TIMEOUT_15M = 8


def parse_ts(value: Any) -> pd.Timestamp | None:
    if value is None:
        return None
    try:
        ts = pd.to_datetime(value, utc=True)
    except Exception:
        return None
    if pd.isna(ts):
        return None
    return ts


def iso(ts: pd.Timestamp | None) -> str | None:
    if ts is None or pd.isna(ts):
        return None
    return pd.Timestamp(ts).tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch_json(url: str, params: dict[str, Any], *, retries: int = 5, timeout: int = 10, base_sleep_seconds: float = 0.6) -> Any:
    query = urllib.parse.urlencode(params)
    req = urllib.request.Request(f"{url}?{query}", headers={"User-Agent": "Mozilla/5.0"})
    last_err: Exception | None = None
    for attempt in range(max(1, int(retries))):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            last_err = exc
            if exc.code in {403, 418, 429, 500, 502, 503, 504} and attempt < int(retries) - 1:
                retry_after = None
                try:
                    retry_after = exc.headers.get("Retry-After") if exc.headers is not None else None
                except Exception:
                    retry_after = None
                try:
                    wait_s = float(retry_after) if retry_after else min(60.0, max(1.0, base_sleep_seconds * (2 ** attempt) * (3.0 if exc.code in {403, 418} else 1.0)))
                except Exception:
                    wait_s = min(60.0, max(1.0, base_sleep_seconds * (2 ** attempt)))
                time.sleep(wait_s)
                continue
            raise
        except urllib.error.URLError as exc:
            last_err = exc
            if attempt < int(retries) - 1:
                time.sleep(min(30.0, max(1.0, base_sleep_seconds * (2 ** attempt))))
                continue
            raise
    if last_err is not None:
        raise last_err
    raise RuntimeError(f"failed to fetch json from {url}")


def fetch_depth(symbol: str, limit: int) -> dict[str, Any]:
    return fetch_json(FUTURES_DEPTH, {"symbol": symbol.upper(), "limit": int(limit)})


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def build_minute_cache_cfg(paper_cfg: dict[str, Any] | None = None) -> dict[str, Any]:
    paper_cfg = paper_cfg if isinstance(paper_cfg, dict) else {}
    live_parity_cfg = paper_cfg.get("live_parity") if isinstance(paper_cfg.get("live_parity"), dict) else {}
    raw = live_parity_cfg.get("kline_1m_cache") if isinstance(live_parity_cfg.get("kline_1m_cache"), dict) else {}
    return {
        "cooldown_seconds": int(raw.get("cooldown_seconds", 120)),
        "max_staleness_minutes": int(raw.get("max_staleness_minutes", 2)),
        "tail_overlap_minutes": int(raw.get("tail_overlap_minutes", 3)),
        "request_pause_seconds": float(raw.get("request_pause_seconds", 0.2)),
        "http_retries": int(raw.get("http_retries", 5)),
        "http_timeout_seconds": int(raw.get("http_timeout_seconds", 20)),
    }


def minute_cache_paths(symbol: str, days: int) -> tuple[Path, Path]:
    base = f"{symbol.upper()}__{int(days)}d__1m__perp"
    return KLINE_1M_CACHE_DIR / f"{base}.csv", KLINE_1M_CACHE_DIR / f"{base}.meta.json"


def load_minute_cache_meta(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return raw if isinstance(raw, dict) else {}


def save_minute_cache_meta(path: Path, meta: dict[str, Any]) -> None:
    path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def normalize_1m_frame(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=["open_ts", "close_ts", "open", "high", "low", "close", "volume"])
    out = df.copy()
    out["open_ts"] = pd.to_datetime(out["open_ts"], utc=True)
    out["close_ts"] = pd.to_datetime(out["close_ts"], utc=True)
    for col in ["open", "high", "low", "close", "volume"]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    return out.dropna().sort_values("open_ts").drop_duplicates("open_ts", keep="last").reset_index(drop=True)


def load_minute_cache_frame(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame(columns=["open_ts", "close_ts", "open", "high", "low", "close", "volume"])
    return normalize_1m_frame(pd.read_csv(path))


def save_minute_cache_frame(path: Path, df: pd.DataFrame) -> None:
    normalize_1m_frame(df).to_csv(path, index=False)


def merge_minute_frames(existing: pd.DataFrame, new_rows: pd.DataFrame) -> pd.DataFrame:
    if existing is None or existing.empty:
        return normalize_1m_frame(new_rows)
    if new_rows is None or new_rows.empty:
        return normalize_1m_frame(existing)
    return normalize_1m_frame(pd.concat([existing, new_rows], ignore_index=True))


def trim_minute_window(df: pd.DataFrame, start_open_ts: pd.Timestamp, end_open_ts: pd.Timestamp) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=["open_ts", "close_ts", "open", "high", "low", "close", "volume"])
    out = normalize_1m_frame(df)
    return out[(out["open_ts"] >= start_open_ts) & (out["open_ts"] <= end_open_ts)].reset_index(drop=True)


def infer_missing_start_ts(df: pd.DataFrame, start_open_ts: pd.Timestamp, end_open_ts: pd.Timestamp) -> pd.Timestamp | None:
    if end_open_ts < start_open_ts:
        return None
    window = trim_minute_window(df, start_open_ts, end_open_ts)
    if window.empty:
        return start_open_ts
    first_open = parse_ts(window["open_ts"].min())
    last_open = parse_ts(window["open_ts"].max())
    if first_open is None or first_open > start_open_ts:
        return start_open_ts
    diffs = window["open_ts"].diff().dropna()
    gaps = diffs[diffs > pd.Timedelta(minutes=1)]
    if not gaps.empty:
        gap_idx = gaps.index[0]
        prev_open = parse_ts(window.loc[gap_idx - 1, "open_ts"])
        if prev_open is not None:
            return prev_open + pd.Timedelta(minutes=1)
    if last_open is None:
        return start_open_ts
    if last_open < end_open_ts:
        return last_open + pd.Timedelta(minutes=1)
    return None


def fetch_klines_1m(symbol: str, start_ms: int, end_ms: int, *, cache_cfg: dict[str, Any] | None = None) -> pd.DataFrame:
    rows: list[list[Any]] = []
    current = int(start_ms)
    cfg = cache_cfg if isinstance(cache_cfg, dict) else build_minute_cache_cfg({})
    while current <= int(end_ms):
        data = fetch_json(
            FUTURES_KLINES,
            {
                "symbol": symbol.upper(),
                "interval": "1m",
                "startTime": int(current),
                "endTime": int(end_ms),
                "limit": FETCH_LIMIT,
            },
            retries=int(cfg.get("http_retries", 5)),
            timeout=int(cfg.get("http_timeout_seconds", 20)),
            base_sleep_seconds=float(cfg.get("request_pause_seconds", 0.2)) + 0.4,
        )
        if not isinstance(data, list) or not data:
            break
        rows.extend(data)
        current = int(data[-1][0]) + 60_000
        if len(data) < FETCH_LIMIT:
            break
        time.sleep(float(cfg.get("request_pause_seconds", 0.2)))
    if not rows:
        return pd.DataFrame(columns=["open_ts", "close_ts", "open", "high", "low", "close", "volume"])
    cols = [
        "open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume", "trade_count",
        "taker_buy_base", "taker_buy_quote", "ignore",
    ]
    df = pd.DataFrame(rows, columns=cols)
    out = pd.DataFrame(
        {
            "open_ts": pd.to_datetime(df["open_time"], unit="ms", utc=True),
            "close_ts": pd.to_datetime(df["close_time"], unit="ms", utc=True),
            "open": pd.to_numeric(df["open"], errors="coerce"),
            "high": pd.to_numeric(df["high"], errors="coerce"),
            "low": pd.to_numeric(df["low"], errors="coerce"),
            "close": pd.to_numeric(df["close"], errors="coerce"),
            "volume": pd.to_numeric(df["volume"], errors="coerce"),
        }
    )
    return normalize_1m_frame(out)


def load_or_fetch_1m(symbol: str, days: int, *, refresh: bool = False, now_ts: pd.Timestamp | None = None, paper_cfg: dict[str, Any] | None = None) -> pd.DataFrame:
    ensure_dir(KLINE_1M_CACHE_DIR)
    now_ts = (now_ts if now_ts is not None else pd.Timestamp.now(tz="UTC")).tz_convert("UTC")
    cache_cfg = build_minute_cache_cfg(paper_cfg)
    csv_path, meta_path = minute_cache_paths(symbol, max(1, int(days)))
    meta = load_minute_cache_meta(meta_path)
    existing = load_minute_cache_frame(csv_path)
    end_open_ts = now_ts.floor("1min") - pd.Timedelta(minutes=1)
    start_open_ts = end_open_ts - pd.Timedelta(days=max(1, int(days))) + pd.Timedelta(minutes=1)
    if end_open_ts < start_open_ts:
        return trim_minute_window(existing, start_open_ts, end_open_ts)

    trimmed = trim_minute_window(existing, start_open_ts, end_open_ts)
    missing_start = infer_missing_start_ts(trimmed, start_open_ts, end_open_ts)
    if not refresh and missing_start is None:
        return trimmed

    last_attempt_ts = parse_ts(meta.get("last_attempt_utc"))
    cooldown_seconds = int(cache_cfg.get("cooldown_seconds", 120))
    max_staleness_minutes = int(cache_cfg.get("max_staleness_minutes", 2))
    latest_open = parse_ts(trimmed["open_ts"].max()) if not trimmed.empty else None
    stale_minutes = None if latest_open is None else max(0.0, (end_open_ts - latest_open).total_seconds() / 60.0)
    if not refresh and last_attempt_ts is not None and (now_ts - last_attempt_ts).total_seconds() < cooldown_seconds:
        if latest_open is not None and stale_minutes is not None and stale_minutes <= max_staleness_minutes:
            return trimmed

    overlap_minutes = int(cache_cfg.get("tail_overlap_minutes", 3))
    fetch_start_open_ts = missing_start or (latest_open + pd.Timedelta(minutes=1) if latest_open is not None else start_open_ts)
    if latest_open is not None:
        fetch_start_open_ts = min(fetch_start_open_ts, latest_open - pd.Timedelta(minutes=max(0, overlap_minutes - 1)))
    fetch_start_open_ts = max(start_open_ts, fetch_start_open_ts)
    fetch_end_open_ts = end_open_ts
    if fetch_end_open_ts < fetch_start_open_ts:
        return trimmed

    meta.update({
        "symbol": symbol.upper(),
        "days": int(days),
        "last_attempt_utc": iso(now_ts),
        "cache_window_start_utc": iso(start_open_ts),
        "cache_window_end_utc": iso(end_open_ts),
    })
    save_minute_cache_meta(meta_path, meta)

    try:
        new_rows = fetch_klines_1m(
            symbol,
            int(fetch_start_open_ts.timestamp() * 1000),
            int((fetch_end_open_ts + pd.Timedelta(minutes=1) - pd.Timedelta(milliseconds=1)).timestamp() * 1000),
            cache_cfg=cache_cfg,
        )
        merged = merge_minute_frames(existing, new_rows)
        merged = trim_minute_window(merged, start_open_ts, end_open_ts)
        save_minute_cache_frame(csv_path, merged)
        meta.update({
            "last_success_utc": iso(now_ts),
            "last_error": None,
            "last_fetch_start_utc": iso(fetch_start_open_ts),
            "last_fetch_end_utc": iso(fetch_end_open_ts),
            "latest_cached_open_utc": iso(parse_ts(merged["open_ts"].max()) if not merged.empty else None),
            "row_count": int(len(merged)),
        })
        save_minute_cache_meta(meta_path, meta)
        return merged
    except Exception as exc:
        meta.update({
            "last_error": str(exc),
            "latest_cached_open_utc": iso(latest_open),
            "row_count": int(len(trimmed)),
        })
        save_minute_cache_meta(meta_path, meta)
        if not trimmed.empty:
            return trimmed
        raise


def get_symbol_1m_bars(symbol: str, *, days: int, now_ts: pd.Timestamp, cache: dict[str, pd.DataFrame], paper_cfg: dict[str, Any] | None = None) -> pd.DataFrame:
    key = f"{symbol.upper()}|{int(days)}"
    end_open_ts = now_ts.floor("1min") - pd.Timedelta(minutes=1)
    start_open_ts = end_open_ts - pd.Timedelta(days=max(1, int(days))) + pd.Timedelta(minutes=1)
    cached = cache.get(key)
    if isinstance(cached, pd.DataFrame) and not cached.empty:
        cached = cached.sort_values("open_ts").reset_index(drop=True)
        cached_min = parse_ts(cached["open_ts"].min())
        cached_max = parse_ts(cached["open_ts"].max())
        if cached_min is not None and cached_max is not None and cached_min <= start_open_ts and cached_max >= end_open_ts:
            return cached
    try:
        df = load_or_fetch_1m(symbol, max(1, int(days)), refresh=False, now_ts=now_ts, paper_cfg=paper_cfg)
        df = df.sort_values("open_ts").reset_index(drop=True)
    except Exception:
        df = pd.DataFrame(columns=["open_ts", "close_ts", "open", "high", "low", "close", "volume"])
    cache[key] = df
    return df


def signal_bar_key(symbol: str, timestamp: Any, bar_minutes: int = 15) -> str:
    ts = parse_ts(timestamp)
    if ts is None:
        return f"{str(symbol or '').upper()}|unknown"
    bucket = ts.floor(f"{int(max(1, bar_minutes))}min")
    return f"{str(symbol or '').upper()}|{bucket.strftime('%Y-%m-%dT%H:%M:%SZ')}"


def build_live_parity_cfg(paper_cfg: dict[str, Any]) -> dict[str, Any]:
    raw = paper_cfg.get("live_parity") if isinstance(paper_cfg.get("live_parity"), dict) else {}
    return {
        "enabled": bool(raw.get("enabled", False)),
        "scheduler_interval_minutes": int(raw.get("scheduler_interval_minutes", 1)),
        "same_bar_once": bool(raw.get("same_bar_once", True)),
        "same_bar_minutes": int(raw.get("same_bar_minutes", 15)),
        "same_symbol_single_position": bool(raw.get("same_symbol_single_position", True)),
        "ignore_cross_lane": bool(raw.get("ignore_cross_lane", True)),
        "enforce_signal_freshness": bool(raw.get("enforce_signal_freshness", True)),
        "max_signal_age_minutes": int(raw.get("max_signal_age_minutes", 30)),
        "exit_check_interval_minutes": int(raw.get("exit_check_interval_minutes", 1)),
        "monitor_from_next_minute_bar": bool(raw.get("monitor_from_next_minute_bar", True)),
        "kline_1m_cache": build_minute_cache_cfg(paper_cfg),
    }


def depth_snapshot_metrics(depth: dict[str, Any]) -> dict[str, Any]:
    bids = depth.get("bids") or []
    asks = depth.get("asks") or []
    best_bid = float(bids[0][0]) if bids else None
    best_ask = float(asks[0][0]) if asks else None
    mid = None
    spread_bps = None
    if best_bid is not None and best_ask is not None:
        mid = (best_bid + best_ask) / 2.0
        if mid:
            spread_bps = ((best_ask - best_bid) / mid) * 10000.0
    return {
        "best_bid": best_bid,
        "best_ask": best_ask,
        "mid": mid,
        "spread_bps": spread_bps,
        "depth_levels": int(min(len(bids), len(asks))),
        "last_update_id": depth.get("lastUpdateId"),
    }


def simulate_fill_by_qty(depth: dict[str, Any], side: str, qty: float) -> dict[str, Any]:
    if qty <= 0:
        raise ValueError("qty must be positive")
    if side not in {"buy", "sell"}:
        raise ValueError("side must be buy/sell")
    levels = (depth.get("asks") or []) if side == "buy" else (depth.get("bids") or [])
    metrics = depth_snapshot_metrics(depth)
    remaining = float(qty)
    filled = 0.0
    quote = 0.0
    levels_used = 0
    level_rows: list[list[float]] = []
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
    top = metrics.get("best_ask") if side == "buy" else metrics.get("best_bid")
    impact_bps = abs(vwap - mid) / mid * 10000.0 if mid else None
    top_slip_bps = None
    if top:
        top_slip_bps = ((vwap / top - 1.0) * 10000.0) if side == "buy" else ((top / vwap - 1.0) * 10000.0)
    return {
        **metrics,
        "fill_model": "depth_v2_qty",
        "side": side,
        "target_qty": float(qty),
        "filled_qty": float(filled),
        "quote_value": float(quote),
        "vwap": float(vwap),
        "impact_bps": impact_bps,
        "slippage_bps_vs_top": top_slip_bps,
        "levels_used": int(levels_used),
        "levels_preview": json.dumps(level_rows[:5]),
    }


def simulate_fill_by_notional(depth: dict[str, Any], side: str, notional_usdt: float) -> dict[str, Any]:
    if notional_usdt <= 0:
        raise ValueError("notional_usdt must be positive")
    if side not in {"buy", "sell"}:
        raise ValueError("side must be buy/sell")
    levels = (depth.get("asks") or []) if side == "buy" else (depth.get("bids") or [])
    metrics = depth_snapshot_metrics(depth)
    remaining_quote = float(notional_usdt)
    filled_qty = 0.0
    quote = 0.0
    levels_used = 0
    level_rows: list[list[float]] = []
    for px_raw, qty_raw in levels:
        px = float(px_raw)
        lvl_qty = float(qty_raw)
        lvl_quote = px * lvl_qty
        take_quote = min(remaining_quote, lvl_quote)
        if take_quote <= 0:
            continue
        take_qty = take_quote / px
        filled_qty += take_qty
        quote += take_quote
        remaining_quote -= take_quote
        levels_used += 1
        level_rows.append([px, take_qty])
        if remaining_quote <= 1e-8:
            break
    if remaining_quote > 1e-5 or filled_qty <= 0:
        raise RuntimeError(f"insufficient depth to fill notional={notional_usdt:.2f}")
    vwap = quote / filled_qty
    mid = metrics.get("mid")
    top = metrics.get("best_ask") if side == "buy" else metrics.get("best_bid")
    impact_bps = abs(vwap - mid) / mid * 10000.0 if mid else None
    top_slip_bps = None
    if top:
        top_slip_bps = ((vwap / top - 1.0) * 10000.0) if side == "buy" else ((top / vwap - 1.0) * 10000.0)
    return {
        **metrics,
        "fill_model": "depth_v2_notional",
        "side": side,
        "target_notional_usdt": float(notional_usdt),
        "filled_qty": float(filled_qty),
        "quote_value": float(quote),
        "vwap": float(vwap),
        "impact_bps": impact_bps,
        "slippage_bps_vs_top": top_slip_bps,
        "levels_used": int(levels_used),
        "levels_preview": json.dumps(level_rows[:5]),
    }


def gross_return(entry_px: float, exit_px: float, direction_sign: int) -> float:
    return float((exit_px / entry_px - 1.0) * direction_sign)


def apply_fees(gross_ret: float, entry_fee_bps: float, exit_fee_bps: float) -> float:
    entry_fee = float(entry_fee_bps) / 10000.0
    exit_fee = float(exit_fee_bps) / 10000.0
    return float((1.0 + gross_ret) * (1.0 - entry_fee) * (1.0 - exit_fee) - 1.0)


def get_signal_entry_ts(row: dict[str, Any]) -> pd.Timestamp | None:
    return parse_ts(row.get("signal_confirmed_at")) or parse_ts(row.get("timestamp"))


def get_signal_atr(row: dict[str, Any]) -> float | None:
    meta = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
    atr = meta.get("atr14")
    try:
        value = float(atr)
    except Exception:
        return None
    if not math.isfinite(value) or value <= 0:
        return None
    return value


def get_direction_sign(side: str) -> int:
    return 1 if str(side or "").lower() == "long" else -1


def get_entry_depth_side(position_side: str) -> str:
    return "buy" if str(position_side).lower() == "long" else "sell"


def get_exit_depth_side(position_side: str) -> str:
    return "sell" if str(position_side).lower() == "long" else "buy"


def build_barriers(entry_price: float, direction_sign: int, atr_value: float | None, paper_cfg: dict[str, Any]) -> dict[str, Any]:
    if atr_value is not None and math.isfinite(atr_value) and atr_value > 0:
        target_px = float(entry_price + direction_sign * float(paper_cfg.get("tp_atr_mult", 1.25)) * atr_value)
        stop_px = float(entry_price - direction_sign * float(paper_cfg.get("sl_atr_mult", 1.0)) * atr_value)
        barrier_type = "atr"
    else:
        tp_bps = float(paper_cfg.get("fallback_tp_bps", 40.0)) / 10000.0
        sl_bps = float(paper_cfg.get("fallback_sl_bps", 40.0)) / 10000.0
        target_px = float(entry_price * (1.0 + direction_sign * tp_bps))
        stop_px = float(entry_price * (1.0 - direction_sign * sl_bps))
        barrier_type = "fallback_bps"
    return {"target_price": target_px, "stop_price": stop_px, "barrier_type": barrier_type}


def close_trigger_quote(depth: dict[str, Any], position_side: str) -> float | None:
    metrics = depth_snapshot_metrics(depth)
    if str(position_side).lower() == "long":
        return metrics.get("best_bid")
    return metrics.get("best_ask")


def simulate_exit_on_minute_bars(
    minute_df: pd.DataFrame,
    *,
    entry_ts: pd.Timestamp,
    entry_price: float,
    position_side: str,
    atr_value: float | None,
    paper_cfg: dict[str, Any],
    now_ts: pd.Timestamp,
    entry_fee_bps: float,
    exit_fee_bps: float,
) -> dict[str, Any]:
    direction_sign = get_direction_sign(position_side)
    barriers = build_barriers(entry_price, direction_sign, atr_value, paper_cfg)
    timeout_at = entry_ts + pd.Timedelta(minutes=int(paper_cfg.get("timeout_15m", DEFAULT_TIMEOUT_15M)) * 15)
    live_parity_cfg = build_live_parity_cfg(paper_cfg)
    monitor_start = entry_ts.floor("1min") + pd.Timedelta(minutes=1) if live_parity_cfg.get("monitor_from_next_minute_bar", True) else entry_ts.floor("1min")
    cutoff_ts = min(now_ts.floor("1min"), timeout_at.ceil("1min"))
    usable = minute_df.copy()
    if usable.empty:
        return {
            "status": "open",
            "mark_status": "minute_bars_unavailable",
            "exit_ts": None,
            "exit_price": None,
            "exit_reason": None,
            "gross_ret": None,
            "net_ret": None,
            "hold_minutes": 0,
            "same_bar_conflict": 0,
            "target_hit": 0,
            "stop_hit": 0,
            "timeout_hit": 0,
            "barrier_type": barriers["barrier_type"],
            "mark_ts": None,
            "mark_price": None,
            "mark_gross_ret": None,
            "mark_net_ret": None,
        }
    usable = usable[(usable["open_ts"] >= monitor_start) & (usable["open_ts"] <= cutoff_ts)].copy().sort_values("open_ts")
    last_mark_bar = None
    for _, bar in usable.iterrows():
        bar_open = parse_ts(bar.get("open_ts"))
        bar_close = parse_ts(bar.get("close_ts")) or (bar_open + pd.Timedelta(minutes=1) if bar_open is not None else None)
        high = float(bar["high"])
        low = float(bar["low"])
        if direction_sign > 0:
            hit_tp = high >= float(barriers["target_price"])
            hit_sl = low <= float(barriers["stop_price"])
        else:
            hit_tp = low <= float(barriers["target_price"])
            hit_sl = high >= float(barriers["stop_price"])
        if hit_tp and hit_sl:
            exit_px = float(barriers["stop_price"])
            gross_ret = gross_return(entry_price, exit_px, direction_sign)
            net_ret = apply_fees(gross_ret, entry_fee_bps, exit_fee_bps)
            hold_minutes = int(max(0.0, ((bar_close or now_ts) - entry_ts).total_seconds() / 60.0))
            return {
                "status": "closed",
                "mark_status": "realized",
                "exit_ts": bar_close,
                "exit_price": exit_px,
                "exit_reason": "conflict_stop_first_1m",
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "hold_minutes": hold_minutes,
                "same_bar_conflict": 1,
                "target_hit": 0,
                "stop_hit": 1,
                "timeout_hit": 0,
                "barrier_type": barriers["barrier_type"],
            }
        if hit_tp:
            exit_px = float(barriers["target_price"])
            gross_ret = gross_return(entry_price, exit_px, direction_sign)
            net_ret = apply_fees(gross_ret, entry_fee_bps, exit_fee_bps)
            hold_minutes = int(max(0.0, ((bar_close or now_ts) - entry_ts).total_seconds() / 60.0))
            return {
                "status": "closed",
                "mark_status": "realized",
                "exit_ts": bar_close,
                "exit_price": exit_px,
                "exit_reason": "target_1m",
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "hold_minutes": hold_minutes,
                "same_bar_conflict": 0,
                "target_hit": 1,
                "stop_hit": 0,
                "timeout_hit": 0,
                "barrier_type": barriers["barrier_type"],
            }
        if hit_sl:
            exit_px = float(barriers["stop_price"])
            gross_ret = gross_return(entry_price, exit_px, direction_sign)
            net_ret = apply_fees(gross_ret, entry_fee_bps, exit_fee_bps)
            hold_minutes = int(max(0.0, ((bar_close or now_ts) - entry_ts).total_seconds() / 60.0))
            return {
                "status": "closed",
                "mark_status": "realized",
                "exit_ts": bar_close,
                "exit_price": exit_px,
                "exit_reason": "stop_1m",
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "hold_minutes": hold_minutes,
                "same_bar_conflict": 0,
                "target_hit": 0,
                "stop_hit": 1,
                "timeout_hit": 0,
                "barrier_type": barriers["barrier_type"],
            }
        if bar_close is not None and bar_close >= timeout_at:
            exit_px = float(bar["close"])
            gross_ret = gross_return(entry_price, exit_px, direction_sign)
            net_ret = apply_fees(gross_ret, entry_fee_bps, exit_fee_bps)
            hold_minutes = int(max(0.0, (bar_close - entry_ts).total_seconds() / 60.0))
            return {
                "status": "closed",
                "mark_status": "realized",
                "exit_ts": bar_close,
                "exit_price": exit_px,
                "exit_reason": "timeout_1m",
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "hold_minutes": hold_minutes,
                "same_bar_conflict": 0,
                "target_hit": 0,
                "stop_hit": 0,
                "timeout_hit": 1,
                "barrier_type": barriers["barrier_type"],
            }
        last_mark_bar = bar
    if last_mark_bar is None:
        return {
            "status": "open",
            "mark_status": "awaiting_first_1m_bar",
            "exit_ts": None,
            "exit_price": None,
            "exit_reason": None,
            "gross_ret": None,
            "net_ret": None,
            "hold_minutes": 0,
            "same_bar_conflict": 0,
            "target_hit": 0,
            "stop_hit": 0,
            "timeout_hit": 0,
            "barrier_type": barriers["barrier_type"],
            "mark_ts": None,
            "mark_price": None,
            "mark_gross_ret": None,
            "mark_net_ret": None,
        }
    mark_close = parse_ts(last_mark_bar.get("close_ts")) or now_ts.floor("1min")
    mark_px = float(last_mark_bar["close"])
    gross_ret = gross_return(entry_price, mark_px, direction_sign)
    net_ret = apply_fees(gross_ret, entry_fee_bps, exit_fee_bps)
    hold_minutes = int(max(0.0, (mark_close - entry_ts).total_seconds() / 60.0))
    return {
        "status": "open",
        "mark_status": "marked_to_market_1m",
        "exit_ts": None,
        "exit_price": None,
        "exit_reason": None,
        "gross_ret": None,
        "net_ret": None,
        "hold_minutes": hold_minutes,
        "same_bar_conflict": 0,
        "target_hit": 0,
        "stop_hit": 0,
        "timeout_hit": 0,
        "barrier_type": barriers["barrier_type"],
        "mark_ts": mark_close,
        "mark_price": mark_px,
        "mark_gross_ret": gross_ret,
        "mark_net_ret": net_ret,
    }


def build_depth_cfg(paper_cfg: dict[str, Any]) -> dict[str, Any]:
    raw = paper_cfg.get("depth_v2") if isinstance(paper_cfg.get("depth_v2"), dict) else {}
    base_notional = float(raw.get("order_notional_usdt", DEFAULT_ORDER_NOTIONAL_USDT))
    by_symbol_raw = raw.get("order_notional_usdt_by_symbol") if isinstance(raw.get("order_notional_usdt_by_symbol"), dict) else {}
    by_symbol: dict[str, float] = {}
    for key, value in by_symbol_raw.items():
        try:
            num = float(value)
        except Exception:
            continue
        if math.isfinite(num) and num > 0:
            by_symbol[str(key).upper()] = num
    return {
        "enabled": bool(raw.get("enabled", False)),
        "order_notional_usdt": base_notional,
        "order_notional_usdt_by_symbol": by_symbol,
        "depth_limit": int(raw.get("depth_limit", DEFAULT_DEPTH_LIMIT)),
        "reject_if_insufficient_depth": bool(raw.get("reject_if_insufficient_depth", True)),
        "min_depth_fill_ratio": float(raw.get("min_depth_fill_ratio", 0.98)),
        "entry_fee_bps": float(raw.get("entry_fee_bps", paper_cfg.get("market_cost_bps", DEFAULT_TAKER_FEE_BPS))),
        "exit_fee_bps": float(raw.get("exit_fee_bps", paper_cfg.get("market_cost_bps", DEFAULT_TAKER_FEE_BPS))),
    }


def resolve_order_notional_usdt(depth_cfg: dict[str, Any], symbol: str | None) -> float:
    symbol_key = str(symbol or "").upper()
    overrides = depth_cfg.get("order_notional_usdt_by_symbol") if isinstance(depth_cfg.get("order_notional_usdt_by_symbol"), dict) else {}
    if symbol_key in overrides:
        return float(overrides[symbol_key])
    return float(depth_cfg["order_notional_usdt"])


def _fetch_depth_cached(symbol: str, depth_cfg: dict[str, Any], cache: dict[str, dict[str, Any]], now_ts: pd.Timestamp) -> dict[str, Any]:
    key = f"{symbol.upper()}|{depth_cfg['depth_limit']}"
    if key not in cache:
        depth = fetch_depth(symbol.upper(), int(depth_cfg["depth_limit"]))
        depth["snapshot_ts"] = iso(now_ts)
        cache[key] = depth
    return cache[key]


def _build_depth_reject_trade(
    row: dict[str, Any],
    *,
    symbol: str,
    side: str,
    signal_ts: Any,
    confirmed_at: Any,
    depth_cfg: dict[str, Any],
    reason: str,
    error: Exception,
) -> tuple[dict[str, Any], dict[str, Any]]:
    normalized_reason = str(reason or "depth_snapshot_unavailable")
    status = "rejected_insufficient_depth" if normalized_reason == "insufficient_depth" else "rejected_depth_snapshot_unavailable"
    skip_reason = "paper_rejected_by_insufficient_depth" if normalized_reason == "insufficient_depth" else "paper_rejected_by_depth_snapshot_error"
    order_notional_usdt = resolve_order_notional_usdt(depth_cfg, symbol)
    trade_row = {
        "signal_id": row.get("signal_id"),
        "symbol": symbol,
        "side": side,
        "mode": ((row.get("metadata") if isinstance(row.get("metadata"), dict) else {}) or {}).get("signal_mode"),
        "signal_ts": signal_ts,
        "signal_confirmed_at": confirmed_at,
        "paper_trade_state": "rejected",
        "status": status,
        "paper_effective_net_ret": 0.0,
        "paper_effective_gross_ret": 0.0,
        "shadow_model_version": "depth_v2",
        "entry_reject_reason": normalized_reason,
        "entry_reject_error": str(error),
        "order_notional_usdt": order_notional_usdt,
        "depth_limit": int(depth_cfg["depth_limit"]),
    }
    skip_row = {
        "timestamp": signal_ts,
        "signal_confirmed_at": confirmed_at,
        "signal_id": row.get("signal_id"),
        "symbol": symbol,
        "side": side,
        "reason": skip_reason,
        "paper_order_notional_usdt": order_notional_usdt,
        "paper_depth_limit": int(depth_cfg["depth_limit"]),
        "paper_depth_error": str(error),
    }
    return trade_row, skip_row



def _build_open_trade_from_signal(row: dict[str, Any], paper_cfg: dict[str, Any], depth_cfg: dict[str, Any], now_ts: pd.Timestamp, depth_cache: dict[str, dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any] | None]:
    symbol = str(row.get("symbol") or "").upper()
    side = str(row.get("side") or "").lower()
    signal_ts = row.get("timestamp")
    confirmed_at = row.get("signal_confirmed_at")
    atr14 = get_signal_atr(row)
    order_notional_usdt = resolve_order_notional_usdt(depth_cfg, symbol)
    try:
        depth = _fetch_depth_cached(symbol, depth_cfg, depth_cache, now_ts)
        entry_fill = simulate_fill_by_notional(depth, get_entry_depth_side(side), order_notional_usdt)
    except Exception as exc:
        error_text = str(exc).lower()
        reason = "insufficient_depth" if "insufficient depth" in error_text else "depth_snapshot_unavailable"
        return _build_depth_reject_trade(
            row,
            symbol=symbol,
            side=side,
            signal_ts=signal_ts,
            confirmed_at=confirmed_at,
            depth_cfg=depth_cfg,
            reason=reason,
            error=exc,
        )

    direction_sign = get_direction_sign(side)
    entry_price = float(entry_fill["vwap"])
    entry_qty = float(entry_fill["filled_qty"])
    barriers = build_barriers(entry_price, direction_sign, atr14, paper_cfg)
    timeout_at = now_ts + pd.Timedelta(minutes=int(paper_cfg.get("timeout_15m", DEFAULT_TIMEOUT_15M)) * 15)
    entry_fee_bps = float(depth_cfg["entry_fee_bps"])
    exit_fee_bps = float(depth_cfg["exit_fee_bps"])
    trade_row = {
        "signal_id": row.get("signal_id"),
        "symbol": symbol,
        "side": side,
        "mode": ((row.get("metadata") if isinstance(row.get("metadata"), dict) else {}) or {}).get("signal_mode"),
        "signal_ts": signal_ts,
        "signal_confirmed_at": confirmed_at,
        "entry_ts": iso(now_ts),
        "entry_price": entry_price,
        "entry_fee_bps": entry_fee_bps,
        "entry_depth_ts": depth.get("snapshot_ts"),
        "entry_best_bid": entry_fill.get("best_bid"),
        "entry_best_ask": entry_fill.get("best_ask"),
        "entry_mid": entry_fill.get("mid"),
        "entry_spread_bps": entry_fill.get("spread_bps"),
        "entry_impact_bps": entry_fill.get("impact_bps"),
        "entry_slippage_bps_vs_top": entry_fill.get("slippage_bps_vs_top"),
        "entry_levels_used": entry_fill.get("levels_used"),
        "entry_levels_preview": entry_fill.get("levels_preview"),
        "entry_depth_levels": entry_fill.get("depth_levels"),
        "entry_quote_value": entry_fill.get("quote_value"),
        "entry_qty": entry_qty,
        "order_notional_usdt": order_notional_usdt,
        "depth_limit": int(depth_cfg["depth_limit"]),
        "paper_trade_state": "open",
        "status": "marked_to_market",
        "target_price": barriers["target_price"],
        "stop_price": barriers["stop_price"],
        "timeout_at": iso(timeout_at),
        "barrier_type": barriers["barrier_type"],
        "atr14": atr14,
        "tp_atr_mult": float(paper_cfg.get("tp_atr_mult", 1.25)),
        "sl_atr_mult": float(paper_cfg.get("sl_atr_mult", 1.0)),
        "timeout_15m": int(paper_cfg.get("timeout_15m", DEFAULT_TIMEOUT_15M)),
        "max_concurrent_positions": int(paper_cfg.get("max_concurrent_positions", 1)),
        "exit_fee_bps": exit_fee_bps,
        "shadow_model_version": "depth_v2",
    }
    trade_row = _mark_or_close_trade(trade_row, paper_cfg, depth_cfg, now_ts, depth_cache, allow_timeout=False)
    return trade_row, None


def _mark_or_close_trade(trade_row: dict[str, Any], paper_cfg: dict[str, Any], depth_cfg: dict[str, Any], now_ts: pd.Timestamp, depth_cache: dict[str, dict[str, Any]], allow_timeout: bool = True, minute_cache: dict[str, pd.DataFrame] | None = None) -> dict[str, Any]:
    if str(trade_row.get("paper_trade_state")) == "closed":
        return trade_row
    symbol = str(trade_row.get("symbol") or "").upper()
    side = str(trade_row.get("side") or "").lower()
    minute_cache = minute_cache if minute_cache is not None else {}
    entry_ts = parse_ts(trade_row.get("entry_ts")) or parse_ts(trade_row.get("signal_confirmed_at")) or now_ts
    try:
        lookback_days = max(3, int(math.ceil(max(1.0, (now_ts - entry_ts).total_seconds()) / 86400.0)) + 2)
        minute_df = get_symbol_1m_bars(symbol, days=lookback_days, now_ts=now_ts, cache=minute_cache, paper_cfg=paper_cfg)
        minute_exit = simulate_exit_on_minute_bars(
            minute_df,
            entry_ts=entry_ts,
            entry_price=float(trade_row.get("entry_price") or 0.0),
            position_side=side,
            atr_value=trade_row.get("atr14"),
            paper_cfg=paper_cfg,
            now_ts=now_ts,
            entry_fee_bps=float(trade_row.get("entry_fee_bps") or depth_cfg["entry_fee_bps"]),
            exit_fee_bps=float(depth_cfg["exit_fee_bps"]),
        )
    except Exception as exc:
        trade_row.update({
            "paper_trade_state": "open",
            "status": "minute_mark_unavailable",
            "exit_ts": None,
            "exit_price": None,
            "exit_reason": None,
            "gross_ret": None,
            "net_ret": None,
            "mark_ts": iso(now_ts),
            "mark_price": None,
            "mark_gross_ret": None,
            "mark_net_ret": None,
            "paper_effective_gross_ret": 0.0,
            "paper_effective_net_ret": 0.0,
            "target_hit": 0,
            "stop_hit": 0,
            "timeout_hit": 0,
            "same_bar_conflict": 0,
            "depth_mark_error": str(exc),
        })
        return trade_row
    if not allow_timeout and str(minute_exit.get("exit_reason") or "").startswith("timeout"):
        minute_exit = {
            **minute_exit,
            "status": "open",
            "mark_status": "marked_to_market_1m",
            "exit_ts": None,
            "exit_price": None,
            "exit_reason": None,
            "gross_ret": None,
            "net_ret": None,
            "timeout_hit": 0,
        }
    common = {
        "exit_fee_bps": float(depth_cfg["exit_fee_bps"]),
        "hold_minutes": int(minute_exit.get("hold_minutes", 0)),
        "paper_effective_gross_ret": minute_exit.get("gross_ret") if minute_exit.get("status") == "closed" else minute_exit.get("mark_gross_ret", 0.0),
        "paper_effective_net_ret": minute_exit.get("net_ret") if minute_exit.get("status") == "closed" else minute_exit.get("mark_net_ret", 0.0),
        "exit_monitor_interval_minutes": int(build_live_parity_cfg(paper_cfg).get("exit_check_interval_minutes", 1)),
    }
    if minute_exit.get("status") == "closed":
        trade_row.update({
            **common,
            "paper_trade_state": "closed",
            "status": "realized",
            "exit_ts": iso(parse_ts(minute_exit.get("exit_ts"))),
            "exit_price": minute_exit.get("exit_price"),
            "exit_reason": minute_exit.get("exit_reason"),
            "gross_ret": minute_exit.get("gross_ret"),
            "net_ret": minute_exit.get("net_ret"),
            "mark_ts": None,
            "mark_price": None,
            "mark_gross_ret": None,
            "mark_net_ret": None,
            "target_hit": int(minute_exit.get("target_hit", 0)),
            "stop_hit": int(minute_exit.get("stop_hit", 0)),
            "timeout_hit": int(minute_exit.get("timeout_hit", 0)),
            "same_bar_conflict": int(minute_exit.get("same_bar_conflict", 0)),
        })
    else:
        trade_row.update({
            **common,
            "paper_trade_state": "open",
            "status": str(minute_exit.get("mark_status") or "marked_to_market_1m"),
            "exit_ts": None,
            "exit_price": None,
            "exit_reason": None,
            "gross_ret": None,
            "net_ret": None,
            "mark_ts": iso(parse_ts(minute_exit.get("mark_ts"))) if minute_exit.get("mark_ts") is not None else iso(now_ts),
            "mark_price": minute_exit.get("mark_price"),
            "mark_gross_ret": minute_exit.get("mark_gross_ret"),
            "mark_net_ret": minute_exit.get("mark_net_ret"),
            "target_hit": 0,
            "stop_hit": 0,
            "timeout_hit": 0,
            "same_bar_conflict": int(minute_exit.get("same_bar_conflict", 0)),
        })
    return trade_row


def _normalize_existing_trade(trade_row: dict[str, Any], paper_cfg: dict[str, Any], depth_cfg: dict[str, Any]) -> dict[str, Any]:
    out = dict(trade_row)
    out.setdefault("shadow_model_version", "legacy_v1")
    symbol = str(out.get("symbol") or "").upper()
    symbol_notional = resolve_order_notional_usdt(depth_cfg, symbol)
    if str(out.get("paper_trade_state")) == "open":
        entry_price = float(out.get("entry_price") or 0.0)
        if entry_price > 0 and not out.get("entry_qty"):
            out["entry_qty"] = symbol_notional / entry_price
        out.setdefault("order_notional_usdt", symbol_notional)
        out.setdefault("depth_limit", int(depth_cfg["depth_limit"]))
        direction_sign = get_direction_sign(str(out.get("side") or ""))
        barriers = build_barriers(entry_price, direction_sign, out.get("atr14"), paper_cfg)
        out.setdefault("target_price", barriers["target_price"])
        out.setdefault("stop_price", barriers["stop_price"])
        out.setdefault("barrier_type", barriers["barrier_type"])
        entry_ts = parse_ts(out.get("entry_ts")) or parse_ts(out.get("signal_confirmed_at")) or parse_ts(out.get("signal_ts"))
        if out.get("timeout_at") is None and entry_ts is not None:
            timeout_at = entry_ts + pd.Timedelta(minutes=int(paper_cfg.get("timeout_15m", DEFAULT_TIMEOUT_15M)) * 15)
            out["timeout_at"] = iso(timeout_at)
    return out


def build_depth_v2_paper_trades(
    signal_rows: list[dict[str, Any]],
    paper_cfg: dict[str, Any],
    now_ts: pd.Timestamp,
    existing_trades: list[dict[str, Any]] | None = None,
    *,
    replay_mode: str = "historical_replay",
    consumed_bar_keys: list[str] | set[str] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    depth_cfg = build_depth_cfg(paper_cfg)
    live_parity_cfg = build_live_parity_cfg(paper_cfg)
    if not depth_cfg["enabled"]:
        return existing_trades or [], [row for row in (existing_trades or []) if row.get("paper_trade_state") == "closed"], [row for row in (existing_trades or []) if row.get("paper_trade_state") == "open"], {"status": "disabled"}

    trade_by_id: dict[str, dict[str, Any]] = {}
    for row in (existing_trades or []):
        sid = str(row.get("signal_id") or "")
        if sid:
            trade_by_id[sid] = _normalize_existing_trade(row, paper_cfg, depth_cfg)

    usable_rows = [row for row in signal_rows if get_signal_entry_ts(row) is not None]
    usable_rows.sort(key=lambda row: (get_signal_entry_ts(row), str(row.get("symbol") or "")))

    depth_cache: dict[str, dict[str, Any]] = {}
    minute_cache: dict[str, pd.DataFrame] = {}
    skipped_signals: list[dict[str, Any]] = []
    rejected_trades: list[dict[str, Any]] = []
    consumed = set(str(x) for x in (consumed_bar_keys or []))

    # Update/close existing open positions first.
    for sid, trade in list(trade_by_id.items()):
        if str(trade.get("paper_trade_state")) != "open":
            continue
        trade_by_id[sid] = _mark_or_close_trade(trade, paper_cfg, depth_cfg, now_ts, depth_cache, allow_timeout=True, minute_cache=minute_cache)

    for row in usable_rows:
        sid = str(row.get("signal_id") or "")
        if not sid or sid in trade_by_id:
            continue
        symbol = str(row.get("symbol") or "").upper()
        side = row.get("side")
        entry_ts = get_signal_entry_ts(row)
        bar_key = str(row.get("bar_key") or signal_bar_key(symbol, row.get("timestamp") or row.get("signal_confirmed_at"), int(live_parity_cfg.get("same_bar_minutes", 15))))
        if live_parity_cfg.get("enabled", False) and live_parity_cfg.get("same_bar_once", True) and bar_key in consumed:
            skipped_signals.append({
                "timestamp": row.get("timestamp"),
                "signal_confirmed_at": row.get("signal_confirmed_at"),
                "signal_id": sid,
                "symbol": symbol,
                "side": side,
                "bar_key": bar_key,
                "reason": "same_bar_signal_already_consumed",
            })
            continue
        if live_parity_cfg.get("enabled", False) and replay_mode == "stateful_live" and live_parity_cfg.get("enforce_signal_freshness", True) and entry_ts is not None:
            age_seconds = max(0.0, (now_ts - entry_ts).total_seconds())
            max_age_seconds = max(0.0, float(live_parity_cfg.get("max_signal_age_minutes", 30)) * 60.0)
            if max_age_seconds > 0 and age_seconds > max_age_seconds:
                skipped_signals.append({
                    "timestamp": row.get("timestamp"),
                    "signal_confirmed_at": row.get("signal_confirmed_at"),
                    "signal_id": sid,
                    "symbol": symbol,
                    "side": side,
                    "bar_key": bar_key,
                    "reason": "signal_too_old",
                    "signal_age_seconds": round(age_seconds, 2),
                    "max_signal_age_seconds": round(max_age_seconds, 2),
                })
                if live_parity_cfg.get("same_bar_once", True):
                    consumed.add(bar_key)
                continue
        open_positions = sorted(
            [t for t in trade_by_id.values() if str(t.get("paper_trade_state")) == "open"],
            key=lambda t: (parse_ts(t.get("entry_ts")) or pd.Timestamp.min.tz_localize("UTC"), str(t.get("symbol") or "")),
        )
        if live_parity_cfg.get("enabled", False) and live_parity_cfg.get("same_symbol_single_position", True) and any(str(t.get("symbol") or "").upper() == symbol for t in open_positions):
            skipped_signals.append({
                "timestamp": row.get("timestamp"),
                "signal_confirmed_at": row.get("signal_confirmed_at"),
                "signal_id": sid,
                "symbol": symbol,
                "side": side,
                "bar_key": bar_key,
                "reason": "live_position_exists_for_symbol",
            })
            if live_parity_cfg.get("same_bar_once", True):
                consumed.add(bar_key)
            continue
        if len(open_positions) >= int(paper_cfg.get("max_concurrent_positions", 1)):
            skipped_signals.append({
                "timestamp": row.get("timestamp"),
                "signal_confirmed_at": row.get("signal_confirmed_at"),
                "signal_id": sid,
                "symbol": symbol,
                "side": side,
                "bar_key": bar_key,
                "reason": "paper_rejected_by_max_concurrent",
                "paper_active_positions": len(open_positions),
                "paper_max_concurrent_positions": int(paper_cfg.get("max_concurrent_positions", 1)),
            })
            if live_parity_cfg.get("same_bar_once", True):
                consumed.add(bar_key)
            continue
        trade_row, skip_row = _build_open_trade_from_signal(row, paper_cfg, depth_cfg, now_ts, depth_cache)
        if skip_row is not None:
            skip_row.setdefault("bar_key", bar_key)
            skipped_signals.append(skip_row)
            rejected_trades.append(trade_row)
            if live_parity_cfg.get("same_bar_once", True):
                consumed.add(bar_key)
            continue
        trade_row["bar_key"] = bar_key
        trade_by_id[sid] = trade_row
        if live_parity_cfg.get("same_bar_once", True):
            consumed.add(bar_key)

    all_trades = sorted(
        list(trade_by_id.values()) + rejected_trades,
        key=lambda row: (
            parse_ts(row.get("signal_confirmed_at")) or parse_ts(row.get("signal_ts")) or parse_ts(row.get("entry_ts")) or pd.Timestamp.min.tz_localize("UTC"),
            str(row.get("symbol") or ""),
        ),
    )
    closed_trades = [row for row in all_trades if row.get("paper_trade_state") == "closed"]
    open_positions = [row for row in all_trades if row.get("paper_trade_state") == "open"]
    realized_rets = [float(row.get("net_ret", 0.0)) for row in closed_trades if row.get("net_ret") is not None]
    effective_rets = [float(row.get("paper_effective_net_ret", 0.0)) for row in all_trades if row.get("paper_effective_net_ret") is not None and row.get("paper_trade_state") in {"open", "closed"}]

    def total_return(vals: list[float]) -> float:
        acc = 1.0
        for val in vals:
            acc *= 1.0 + float(val)
        return acc - 1.0

    assumptions = {
        "model_version": "depth_v2",
        "entry_style": "depth_v2_taker_vwap",
        "exit_style": "minute_kline_barrier_monitor" if live_parity_cfg.get("enabled", False) else "depth_v2_taker_vwap",
        "order_notional_usdt": float(depth_cfg["order_notional_usdt"]),
        "order_notional_usdt_by_symbol": depth_cfg.get("order_notional_usdt_by_symbol", {}),
        "depth_limit": int(depth_cfg["depth_limit"]),
        "entry_fee_bps": float(depth_cfg["entry_fee_bps"]),
        "exit_fee_bps": float(depth_cfg["exit_fee_bps"]),
        "tp_atr_mult": float(paper_cfg.get("tp_atr_mult", 1.25)),
        "sl_atr_mult": float(paper_cfg.get("sl_atr_mult", 1.0)),
        "timeout_15m": int(paper_cfg.get("timeout_15m", DEFAULT_TIMEOUT_15M)),
        "max_concurrent_positions": int(paper_cfg.get("max_concurrent_positions", 1)),
        "live_parity": live_parity_cfg,
        "replay_mode": replay_mode,
    }
    summary = {
        "status": "ok",
        "assumptions": assumptions,
        "paper_trades": len([row for row in all_trades if row.get("paper_trade_state") != "rejected"]),
        "paper_closed_trades": len(closed_trades),
        "paper_open_positions": len(open_positions),
        "paper_skipped_by_max_concurrent": len([row for row in skipped_signals if row.get("reason") == "paper_rejected_by_max_concurrent"]),
        "paper_rejected_by_insufficient_depth": len([row for row in skipped_signals if row.get("reason") == "paper_rejected_by_insufficient_depth"]),
        "paper_rejected_by_depth_snapshot_error": len([row for row in skipped_signals if row.get("reason") == "paper_rejected_by_depth_snapshot_error"]),
        "paper_rejected_same_bar_consumed": len([row for row in skipped_signals if row.get("reason") == "same_bar_signal_already_consumed"]),
        "paper_rejected_same_symbol_open": len([row for row in skipped_signals if row.get("reason") == "live_position_exists_for_symbol"]),
        "paper_rejected_signal_too_old": len([row for row in skipped_signals if row.get("reason") == "signal_too_old"]),
        "paper_realized_total_return": total_return(realized_rets),
        "paper_marked_total_return": total_return(effective_rets),
        "paper_closed_win_rate": float(sum(1 for x in realized_rets if x > 0) / len(realized_rets)) if realized_rets else None,
        "paper_avg_closed_net_ret": float(sum(realized_rets) / len(realized_rets)) if realized_rets else None,
        "paper_last_closed_symbol": closed_trades[-1].get("symbol") if closed_trades else None,
        "paper_last_closed_exit_ts": closed_trades[-1].get("exit_ts") if closed_trades else None,
        "paper_last_mark_symbol": open_positions[-1].get("symbol") if open_positions else None,
        "paper_last_mark_ts": open_positions[-1].get("mark_ts") if open_positions else None,
        "consumed_bar_keys": sorted(consumed)[-5000:],
        "skipped_rows": skipped_signals,
    }
    return all_trades, closed_trades, open_positions, summary
