#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.domain.canary32b_models import (  # noqa: E402
    EventRecord,
    EventType,
    PositionState,
    StrategyStatusSnapshot,
    SymbolRuntimeState,
    utc_now_iso,
)
from momentum.execution.canary32b.event_bus import JsonlEventBus  # noqa: E402
from momentum.execution.canary32b.frmonitor_bridge import load_frmonitor_bridge  # noqa: E402
from momentum.execution.canary32b.intention_layer import build_entry_intention  # noqa: E402
from momentum.execution.canary32b.signal_adapter import Rank32BPerpSignalAdapter  # noqa: E402
from momentum.execution.canary32b.state_store import JsonStateStore  # noqa: E402
from momentum.risk.canary32b_guard import (  # noqa: E402
    Canary32BMarketContext,
    Canary32BRiskConfig,
    evaluate_entry_risk,
    portfolio_state_from_runtime,
    symbol_bucket,
)

CONFIG_PATH = ROOT / "config" / "execution" / "rank32b_canary.yaml"
ART_DIR = ROOT / "reports" / "artifacts" / "rank32b_canary"

EVENTS_PATH = ART_DIR / "phase6_events.jsonl"
STATE_PATH = ART_DIR / "phase6_state.json"
STATUS_PATH = ART_DIR / "phase6_status.json"
RUN_SUMMARY_PATH = ART_DIR / "phase6_last_run_summary.json"
SIGNALS_PATH = ART_DIR / "phase6_recent_signals.json"
INTENTIONS_PATH = ART_DIR / "phase6_recent_intentions.json"
ORDERS_PATH = ART_DIR / "phase6_recent_orders.json"
REJECTIONS_PATH = ART_DIR / "phase6_recent_rejections.json"
POSITIONS_PATH = ART_DIR / "phase6_recent_positions.json"
CLOSED_TRADES_PATH = ART_DIR / "phase6_recent_closed_trades.json"
WARNINGS_PATH = ART_DIR / "phase6_warnings.json"
SYMBOL_STATE_PATH = ART_DIR / "phase6_symbol_state.json"
OPERATOR_PACKET_PATH = ART_DIR / "phase6_operator_packet.json"
SMALLCAP_ACTIVITY_CACHE_PATH = ART_DIR / "phase6_smallcap_activity_cache.json"


@dataclass(slots=True)
class RunContext:
    now_iso: str
    now_dt: datetime


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def merge_recent_rows(existing: list[dict[str, Any]], new_rows: list[dict[str, Any]], *, tail: int, key_fields: list[str]) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    seen: set[tuple[Any, ...]] = set()
    for row in list(existing or []) + list(new_rows or []):
        if not isinstance(row, dict):
            continue
        key = tuple(row.get(field) for field in key_fields)
        if any(part not in (None, "") for part in key):
            if key in seen:
                continue
            seen.add(key)
        merged.append(row)
    return merged[-tail:]


def append_recent_json(path: Path, new_rows: list[dict[str, Any]], *, tail: int, key_fields: list[str]) -> list[dict[str, Any]]:
    existing = load_json(path, [])
    if not isinstance(existing, list):
        existing = []
    merged = merge_recent_rows(existing, new_rows, tail=tail, key_fields=key_fields)
    save_json(path, merged)
    return merged


def config_hash(cfg: dict[str, Any]) -> str:
    normalized = json.dumps(cfg, ensure_ascii=False, sort_keys=True)
    return hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:16]


def code_version() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short=12", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"


def utcnow() -> RunContext:
    now_dt = datetime.now(timezone.utc)
    return RunContext(now_iso=now_dt.strftime("%Y-%m-%dT%H:%M:%SZ"), now_dt=now_dt)


def parse_utc(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except Exception:
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except Exception:
            return None


def safe_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return float(default)


def load_phase6_conflict_busy_symbols(cfg: dict[str, Any], bridge: Any, own_busy_symbols: set[str]) -> tuple[set[str], list[dict[str, Any]]]:
    phase6 = cfg.get("phase6", {}) if isinstance(cfg.get("phase6"), dict) else {}
    conflict_cfg = phase6.get("conflict", {}) if isinstance(phase6.get("conflict"), dict) else {}
    state_paths = [str(path) for path in (conflict_cfg.get("state_paths") or []) if path]
    enabled_symbols = {str(s).upper() for s in (conflict_cfg.get("enabled_symbols") or cfg.get("universe", {}).get("symbols") or [])}

    busy: set[str] = set()
    warnings: list[dict[str, Any]] = []

    for raw_path in state_paths:
        raw = load_json(Path(raw_path), {})
        for bucket in ("pending_entries", "live_positions"):
            for row in raw.get(bucket, []) or []:
                symbol = str(row.get("symbol") or "").upper()
                if symbol:
                    busy.add(symbol)

    if not enabled_symbols:
        return busy, warnings

    try:
        positions_raw = bridge.get_binance_perp_positions()
        rows = positions_raw if isinstance(positions_raw, list) else [positions_raw]
        for row in rows:
            if not isinstance(row, dict):
                continue
            symbol = str(row.get("symbol") or "").upper()
            if symbol not in enabled_symbols:
                continue
            amt = abs(safe_float(row.get("positionAmt"), 0.0))
            if amt <= 0:
                continue
            if symbol in own_busy_symbols:
                continue
            busy.add(symbol)
            warnings.append(
                {
                    "message": "exchange reports busy symbol on another lane",
                    "payload": {"symbol": symbol, "positionAmt": row.get("positionAmt"), "entryPrice": row.get("entryPrice")},
                }
            )
    except Exception as exc:
        warnings.append({"message": "failed to query exchange positions for cross-lane conflict scan", "payload": {"error": str(exc)}})

    return busy, warnings


def load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def fetch_json_url(url: str) -> Any:
    with urllib.request.urlopen(url, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def make_trace_id(seed: str) -> str:
    return f"trace-{hashlib.sha1(seed.encode('utf-8')).hexdigest()[:12]}"


def signal_to_order_side(signal_side: str) -> str:
    return "BUY" if signal_side == "long" else "SELL"


def exit_order_side(signal_side: str) -> str:
    return "SELL" if signal_side == "long" else "BUY"


def hedge_position_side(signal_side: str) -> str:
    return "LONG" if signal_side == "long" else "SHORT"


def make_client_order_id(role: str, symbol: str, run_ctx: RunContext, trace_id: str | None = None) -> str:
    sym = symbol.replace("USDT", "").lower()[:4]
    stamp = run_ctx.now_dt.strftime("%H%M%S%f")[:9]
    trace_tail = (trace_id or "")[-4:].lower()
    cid = f"r32b6-{role}-{sym}-{stamp}"
    if trace_tail:
        cid = f"{cid}-{trace_tail}"
    return cid[:36]


def derive_tp_price(entry_price: float, side: str, atr14: float | None, tp_atr_mult: float, fallback_bps: float) -> float:
    if atr14 is not None and atr14 > 0:
        move = float(atr14) * float(tp_atr_mult)
        if side == "long":
            return float(entry_price + move)
        return float(entry_price - move)
    shift = float(entry_price) * float(fallback_bps) / 10000.0
    if side == "long":
        return float(entry_price + shift)
    return float(entry_price - shift)


def derive_sl_price(entry_price: float, side: str, atr14: float | None, sl_atr_mult: float, fallback_bps: float) -> float:
    if atr14 is not None and atr14 > 0:
        move = float(atr14) * float(sl_atr_mult)
        if side == "long":
            return float(max(0.0, entry_price - move))
        return float(entry_price + move)
    shift = float(entry_price) * float(fallback_bps) / 10000.0
    if side == "long":
        return float(max(0.0, entry_price - shift))
    return float(entry_price + shift)


def resolve_symbol_desired_notional_usdt(phase6: dict[str, Any], symbol: str) -> float:
    sizing = phase6.get("sizing", {}) if isinstance(phase6, dict) else {}
    base_notional = safe_float(sizing.get("desired_notional_usdt"), 8.0)
    if not math.isfinite(base_notional) or base_notional <= 0:
        base_notional = 8.0

    by_symbol = sizing.get("desired_notional_usdt_by_symbol", {})
    if isinstance(by_symbol, dict):
        target_key = str(symbol or "").upper()
        alt_key = target_key[:-4] if target_key.endswith("USDT") else target_key
        for key, value in by_symbol.items():
            norm = str(key or "").upper()
            if norm not in {target_key, alt_key}:
                continue
            override = safe_float(value, math.nan)
            if math.isfinite(override) and override > 0:
                return float(override)
            break
    return float(base_notional)


def phase6_smallcap_cfg(phase6: dict[str, Any]) -> dict[str, Any]:
    cfg = phase6.get("smallcap", {}) if isinstance(phase6, dict) else {}
    return cfg if isinstance(cfg, dict) else {}


def phase6_smallcap_symbols(phase6: dict[str, Any]) -> list[str]:
    cfg = phase6_smallcap_cfg(phase6)
    symbols = cfg.get("symbols", []) if isinstance(cfg, dict) else []
    if not isinstance(symbols, list):
        return []
    return [str(symbol).upper() for symbol in symbols if str(symbol or "").strip()]


def phase6_symbol_bucket(symbol: str, phase6: dict[str, Any]) -> str:
    return symbol_bucket(symbol, phase6_smallcap_symbols(phase6))


def annotate_signal_bucket(signal: Any, phase6: dict[str, Any]) -> str:
    bucket = phase6_symbol_bucket(str(getattr(signal, "symbol", "")), phase6)
    metadata = signal.metadata if hasattr(signal, "metadata") and isinstance(signal.metadata, dict) else None
    if metadata is None:
        metadata = {}
        signal.metadata = metadata
    metadata["symbol_bucket"] = bucket
    return bucket


def signal_strength_value(signal: Any, metric: str = "slope_strength") -> float:
    metadata = signal.metadata if hasattr(signal, "metadata") and isinstance(signal.metadata, dict) else {}
    metric_name = str(metric or "slope_strength").strip().lower()
    if metric_name == "slope_strength":
        value = safe_float(metadata.get("slope_strength"), math.nan)
        if math.isfinite(value):
            return float(value)
        fast = abs(safe_float(metadata.get("fast_slope"), 0.0))
        slow = abs(safe_float(metadata.get("slow_slope"), 0.0))
        return float(fast + slow)
    return float(abs(safe_float(metadata.get("fast_slope"), 0.0)) + abs(safe_float(metadata.get("slow_slope"), 0.0)))


def select_signals_for_execution(signals: list[Any], phase6: dict[str, Any]) -> tuple[list[Any], list[dict[str, Any]]]:
    selection_cfg = phase6.get("selection", {}) if isinstance(phase6, dict) else {}
    strongest_only_per_bar = bool(selection_cfg.get("strongest_only_per_bar", False))
    metric = str(selection_cfg.get("strength_metric", "slope_strength"))
    smallcap_enabled = bool(phase6_smallcap_cfg(phase6).get("enabled", False)) and bool(phase6_smallcap_symbols(phase6))

    for sig in signals:
        annotate_signal_bucket(sig, phase6)

    if not strongest_only_per_bar:
        return list(signals), []

    grouped: dict[str, list[Any]] = {}
    for sig in signals:
        grouped.setdefault(str(getattr(sig, "timestamp", "")), []).append(sig)

    selected: list[Any] = []
    skipped: list[dict[str, Any]] = []
    for ts in sorted(grouped.keys()):
        ts_bucket = grouped[ts]
        ranked_groups: dict[str, list[Any]] = {}
        if smallcap_enabled:
            for sig in ts_bucket:
                ranked_groups.setdefault(str(getattr(sig, "metadata", {}).get("symbol_bucket") or "core"), []).append(sig)
        else:
            ranked_groups = {"all": ts_bucket}

        for group_name, group_signals in ranked_groups.items():
            ranked = sorted(
                group_signals,
                key=lambda sig: (
                    -signal_strength_value(sig, metric),
                    str(getattr(sig, "symbol", "")),
                    str(getattr(sig, "signal_id", "")),
                ),
            )
            winner = ranked[0]
            selected.append(winner)
            winner_strength = signal_strength_value(winner, metric)
            for loser in ranked[1:]:
                skipped.append(
                    {
                        **loser.to_dict(),
                        "reason": "weaker_than_strongest_signal_in_same_bar_bucket" if smallcap_enabled else "weaker_than_strongest_signal_in_same_bar",
                        "selection_metric": metric,
                        "selection_bucket": group_name,
                        "signal_strength": signal_strength_value(loser, metric),
                        "selected_signal_id": winner.signal_id,
                        "selected_symbol": winner.symbol,
                        "selected_strength": winner_strength,
                        "selected_timestamp": winner.timestamp,
                    }
                )
    return selected, skipped


def limit_new_signals_for_execution(signals: list[Any], phase6: dict[str, Any]) -> list[Any]:
    sorted_signals = sorted(
        signals,
        key=lambda sig: parse_utc(str(getattr(sig, "timestamp", ""))) or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    smallcap_cfg = phase6_smallcap_cfg(phase6)
    smallcap_enabled = bool(smallcap_cfg.get("enabled", False)) and bool(phase6_smallcap_symbols(phase6))
    core_cap = int(phase6.get("max_new_signals_per_run", 1))
    if not smallcap_enabled:
        return sorted_signals[:core_cap] if core_cap > 0 else sorted_signals

    smallcap_cap = int(smallcap_cfg.get("max_new_signals_per_run", 1))
    selected: list[Any] = []
    core_count = 0
    smallcap_count = 0
    for sig in sorted_signals:
        bucket = annotate_signal_bucket(sig, phase6)
        if bucket == "smallcap":
            if smallcap_cap > 0 and smallcap_count >= smallcap_cap:
                continue
            selected.append(sig)
            smallcap_count += 1
        else:
            if core_cap > 0 and core_count >= core_cap:
                continue
            selected.append(sig)
            core_count += 1
        if (core_cap <= 0 or core_count >= core_cap) and (smallcap_cap <= 0 or smallcap_count >= smallcap_cap):
            break
    return selected


def smallcap_activity_snapshot(symbol: str, phase6: dict[str, Any], now_dt: datetime) -> dict[str, Any]:
    cfg = phase6_smallcap_cfg(phase6)
    activity_cfg = cfg.get("activity_filter", {}) if isinstance(cfg.get("activity_filter"), dict) else {}
    lookback_days = max(30, int(activity_cfg.get("lookback_days", 120)))
    recent_days = max(3, int(activity_cfg.get("recent_days", 7)))
    min_percentile = max(0.0, min(1.0, safe_float(activity_cfg.get("min_percentile", 0.35), 0.35)))
    cache_ttl_minutes = max(5, int(activity_cfg.get("cache_ttl_minutes", 360)))

    cache = load_json(SMALLCAP_ACTIVITY_CACHE_PATH, {})
    entry = cache.get(symbol, {}) if isinstance(cache, dict) else {}
    updated_at = parse_utc(str(entry.get("updated_at") or ""))
    is_fresh = updated_at is not None and (now_dt - updated_at).total_seconds() <= cache_ttl_minutes * 60
    if is_fresh and entry.get("lookback_days") == lookback_days and entry.get("recent_days") == recent_days:
        entry["cached"] = True
        return entry

    params = urllib.parse.urlencode({"symbol": symbol, "interval": "1d", "limit": lookback_days})
    url = f"https://fapi.binance.com/fapi/v1/klines?{params}"
    try:
        rows = fetch_json_url(url)
        quote_volumes = [float(row[7]) for row in rows]
        if len(quote_volumes) < recent_days:
            raise ValueError("not_enough_daily_volume_rows")
        baseline = sorted(quote_volumes)
        recent_median = float(sorted(quote_volumes[-recent_days:])[len(quote_volumes[-recent_days:]) // 2])
        rank = sum(1 for value in baseline if value <= recent_median)
        percentile = float(rank / len(baseline))
        snapshot = {
            "symbol": symbol,
            "updated_at": now_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "recent_days": recent_days,
            "lookback_days": lookback_days,
            "recent_median_quote_volume": recent_median,
            "percentile": percentile,
            "min_percentile": min_percentile,
            "allowed": percentile >= min_percentile,
            "cached": False,
        }
        if not isinstance(cache, dict):
            cache = {}
        cache[symbol] = snapshot
        save_json(SMALLCAP_ACTIVITY_CACHE_PATH, cache)
        return snapshot
    except Exception as exc:  # noqa: BLE001
        if isinstance(entry, dict) and entry:
            entry["cached"] = True
            entry["stale"] = True
            entry["error"] = str(exc)
            return entry
        return {
            "symbol": symbol,
            "updated_at": now_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "recent_days": recent_days,
            "lookback_days": lookback_days,
            "recent_median_quote_volume": None,
            "percentile": None,
            "min_percentile": min_percentile,
            "allowed": False,
            "cached": False,
            "error": str(exc),
        }


def build_default_symbol_state(symbols: list[str]) -> list[dict[str, Any]]:
    return [
        SymbolRuntimeState(symbol=symbol, position_state=PositionState.FLAT, active_signal_id=None, active_intention_id=None, last_event_time=None).to_dict()
        for symbol in symbols
    ]


def signal_bar_key(symbol: str, timestamp: str, bar_minutes: int = 15) -> str:
    ts = parse_utc(timestamp)
    if ts is None:
        return f"{symbol}|unknown"
    minute = (ts.minute // int(bar_minutes)) * int(bar_minutes)
    bucket = ts.replace(minute=minute, second=0, microsecond=0)
    return f"{symbol}|{bucket.strftime('%Y-%m-%dT%H:%M:%SZ')}"


def signal_confirmed_at(timestamp: str, metadata: dict[str, Any] | None = None, bar_minutes: int = 15) -> str | None:
    if metadata:
        override = metadata.get("signal_confirmed_at_override") or metadata.get("entry_ready_at")
        if override:
            return str(override)
    ts = parse_utc(timestamp)
    if ts is None:
        return None
    delay_minutes = 0
    if metadata and metadata.get("entry_delay_minutes") is not None:
        delay_minutes = int(safe_float(metadata.get("entry_delay_minutes"), 0.0) or 0)
    return (ts + timedelta(minutes=int(bar_minutes) + delay_minutes)).strftime("%Y-%m-%dT%H:%M:%SZ")


class Phase6State:
    def __init__(self, raw: dict[str, Any] | None = None) -> None:
        raw = raw or {}
        self.enabled_symbols: list[str] = list(raw.get("enabled_symbols", []))
        self.seen_signal_ids: list[str] = list(raw.get("seen_signal_ids", []))
        self.consumed_signal_bars: list[str] = list(raw.get("consumed_signal_bars", []))
        self.symbol_states: list[dict[str, Any]] = list(raw.get("symbol_states", []))
        self.daily_trade_count: int = int(raw.get("daily_trade_count", 0))
        self.daily_trade_date_utc: str | None = raw.get("daily_trade_date_utc")
        self.pending_entries: list[dict[str, Any]] = list(raw.get("pending_entries", []))
        self.live_positions: list[dict[str, Any]] = list(raw.get("live_positions", []))
        self.closed_trades: list[dict[str, Any]] = list(raw.get("closed_trades", []))
        self.last_run_utc: str | None = raw.get("last_run_utc")

    def reset_daily_counter_if_needed(self, now_dt: datetime) -> None:
        today = now_dt.strftime("%Y-%m-%d")
        if self.daily_trade_date_utc != today:
            self.daily_trade_count = 0
            self.daily_trade_date_utc = today

    def refresh_symbol_state(self, symbols: list[str], now_iso: str) -> None:
        state_map: dict[str, dict[str, Any]] = {
            s: SymbolRuntimeState(symbol=s, position_state=PositionState.FLAT, active_signal_id=None, active_intention_id=None, last_event_time=None).to_dict()
            for s in symbols
        }
        for row in self.pending_entries:
            symbol = str(row.get("symbol") or "")
            if symbol not in state_map:
                continue
            state_map[symbol] = SymbolRuntimeState(
                symbol=symbol,
                position_state=PositionState.ENTRY_PENDING,
                active_signal_id=row.get("signal_id"),
                active_intention_id=row.get("intention_id"),
                last_event_time=now_iso,
            ).to_dict()
        for row in self.live_positions:
            symbol = str(row.get("symbol") or "")
            if symbol not in state_map:
                continue
            state_map[symbol] = SymbolRuntimeState(
                symbol=symbol,
                position_state=PositionState.LIVE_POSITION,
                active_signal_id=row.get("signal_id"),
                active_intention_id=row.get("intention_id"),
                last_event_time=now_iso,
            ).to_dict()
        self.symbol_states = [state_map[s] for s in symbols]

    def to_dict(self) -> dict[str, Any]:
        return {
            "enabled_symbols": self.enabled_symbols,
            "seen_signal_ids": self.seen_signal_ids[-4000:],
            "consumed_signal_bars": self.consumed_signal_bars[-4000:],
            "symbol_states": self.symbol_states,
            "daily_trade_count": int(self.daily_trade_count),
            "daily_trade_date_utc": self.daily_trade_date_utc,
            "pending_entries": self.pending_entries[-200:],
            "live_positions": self.live_positions[-100:],
            "closed_trades": self.closed_trades[-400:],
            "last_run_utc": self.last_run_utc,
        }


def load_state(path: Path, symbols: list[str]) -> Phase6State:
    raw = JsonStateStore(path).load({})
    state = Phase6State(raw)
    state.enabled_symbols = list(symbols)
    state.refresh_symbol_state(symbols, raw.get("last_run_utc") or utc_now_iso())
    if not state.symbol_states:
        state.symbol_states = build_default_symbol_state(symbols)
    return state


def save_state_checkpoint(state: Phase6State, *, symbols: list[str], now_iso: str) -> None:
    state.refresh_symbol_state(symbols, now_iso)
    JsonStateStore(STATE_PATH).save(state.to_dict())


def append_event(event_bus: JsonlEventBus, events: list[dict[str, Any]], event: EventRecord) -> None:
    event_bus.append(event)
    events.append(event.to_dict())


def append_warning(
    warnings: list[dict[str, Any]],
    *,
    trace_id: str,
    symbol: str,
    message: str,
    payload: dict[str, Any] | None = None,
    level: str = "WARN",
) -> None:
    warnings.append(
        {
            "timestamp": utc_now_iso(),
            "trace_id": trace_id,
            "symbol": symbol,
            "level": level,
            "message": message,
            "payload": payload or {},
        }
    )


def classify_warning_bucket(warning: dict[str, Any]) -> str:
    message = str(warning.get("message") or "").strip().lower()
    if message == "exchange has non-whitelist open position":
        return "external_account"
    return "canary"


def summarize_warning_buckets(warnings: list[dict[str, Any]]) -> dict[str, int]:
    external_account = 0
    canary = 0
    for warning in warnings:
        bucket = classify_warning_bucket(warning)
        if bucket == "external_account":
            external_account += 1
        else:
            canary += 1
    return {
        "total": len(warnings),
        "external_account": external_account,
        "canary": canary,
    }


def detect_recent_exit_attach_failure_pause(
    state: Phase6State,
    *,
    now_dt: datetime,
    cooldown_minutes: int,
    current_code_version: str | None = None,
) -> dict[str, Any] | None:
    if cooldown_minutes <= 0:
        return None
    latest_row: dict[str, Any] | None = None
    latest_ts: datetime | None = None
    expected_code_version = str(current_code_version or "").strip()
    for row in state.closed_trades:
        exit_reason = str(row.get("exit_reason") or "").strip().lower()
        if not exit_reason.startswith("exit_attach_failed"):
            continue
        if expected_code_version:
            row_code_version = str(row.get("code_version") or "").strip()
            if not row_code_version or row_code_version != expected_code_version:
                continue
        ts = parse_utc(str(row.get("exit_time") or row.get("entry_time") or ""))
        if ts is None:
            continue
        if latest_ts is None or ts > latest_ts:
            latest_ts = ts
            latest_row = row
    if latest_row is None or latest_ts is None:
        return None
    age_minutes = max(0.0, (now_dt - latest_ts).total_seconds() / 60.0)
    if age_minutes > float(cooldown_minutes):
        return None
    until_dt = latest_ts + timedelta(minutes=int(cooldown_minutes))
    return {
        "reason": "recent_exit_attach_failure",
        "symbol": latest_row.get("symbol"),
        "signal_id": latest_row.get("signal_id"),
        "exit_reason": latest_row.get("exit_reason"),
        "code_version": latest_row.get("code_version"),
        "config_version": latest_row.get("config_version"),
        "last_failure_time": latest_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "age_minutes": round(age_minutes, 2),
        "cooldown_minutes": int(cooldown_minutes),
        "cooldown_until": until_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def normalize_order_payload(payload: dict[str, Any], *, source: str) -> dict[str, Any]:
    raw = payload.get("payload") if isinstance(payload.get("payload"), dict) else payload
    status = raw.get("status") if isinstance(raw, dict) else None
    return {
        "source": source,
        "http_status": payload.get("http_status"),
        "endpoint": payload.get("endpoint"),
        "transport": payload.get("transport") or "fapi_order",
        "type": payload.get("type") or (raw.get("type") if isinstance(raw, dict) else None),
        "symbol": payload.get("symbol") or (raw.get("symbol") if isinstance(raw, dict) else None),
        "side": payload.get("side") or (raw.get("side") if isinstance(raw, dict) else None),
        "order_id": payload.get("order_id") or payload.get("strategy_id") or payload.get("algo_id") or (raw.get("orderId") if isinstance(raw, dict) else None) or (raw.get("strategyId") if isinstance(raw, dict) else None) or (raw.get("algoId") if isinstance(raw, dict) else None),
        "client_order_id": payload.get("client_order_id") or payload.get("client_algo_id") or (raw.get("clientOrderId") if isinstance(raw, dict) else None) or (raw.get("newClientStrategyId") if isinstance(raw, dict) else None) or (raw.get("clientAlgoId") if isinstance(raw, dict) else None),
        "status": payload.get("status") or status or (raw.get("strategyStatus") if isinstance(raw, dict) else None) or (raw.get("algoStatus") if isinstance(raw, dict) else None),
        "price": payload.get("price") or (raw.get("price") if isinstance(raw, dict) else None),
        "stop_price": payload.get("stop_price") or payload.get("trigger_price") or (raw.get("stopPrice") if isinstance(raw, dict) else None) or (raw.get("triggerPrice") if isinstance(raw, dict) else None),
        "orig_qty": payload.get("quantity") or (raw.get("origQty") if isinstance(raw, dict) else None) or (raw.get("quantity") if isinstance(raw, dict) else None),
        "executed_qty": payload.get("executed_qty") or (raw.get("executedQty") if isinstance(raw, dict) else None) or (raw.get("executedQuantity") if isinstance(raw, dict) else None),
        "avg_price": payload.get("avg_price") or (raw.get("avgPrice") if isinstance(raw, dict) else None) or (raw.get("avgFillPrice") if isinstance(raw, dict) else None),
        "reduce_only": payload.get("reduce_only"),
        "time_in_force": payload.get("timeInForce") or (raw.get("timeInForce") if isinstance(raw, dict) else None),
        "working_type": payload.get("workingType") or (raw.get("workingType") if isinstance(raw, dict) else None),
        "raw": raw,
    }


def query_order_with_retry(
    bridge,
    *,
    symbol: str,
    order_id: Any,
    client_order_id: str | None,
    attempts: int,
    sleep_seconds: float,
    transport: str | None = None,
) -> dict[str, Any]:
    last_error: Exception | None = None
    for idx in range(max(1, attempts)):
        try:
            if transport == "papi_conditional":
                try:
                    payload = bridge.get_binance_perp_conditional_order(symbol, strategy_id=order_id, client_order_id=client_order_id, history=False)
                except Exception:
                    payload = bridge.get_binance_perp_conditional_order(symbol, strategy_id=order_id, client_order_id=client_order_id, history=True)
            elif transport == "fapi_algo":
                payload = bridge.get_binance_perp_algo_order(algo_id=order_id, client_algo_id=client_order_id)
            else:
                payload = bridge.get_binance_perp_order(symbol, order_id=order_id, client_order_id=client_order_id)
            if isinstance(payload, dict):
                return payload
            return {"raw": payload}
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if idx < attempts - 1:
                time.sleep(max(0.0, sleep_seconds))
    raise RuntimeError(f"order query failed after retry: {last_error}")


def order_snapshot_status(snapshot: dict[str, Any] | None) -> str:
    if not isinstance(snapshot, dict):
        return ""
    return str(snapshot.get("status") or snapshot.get("strategyStatus") or snapshot.get("algoStatus") or "").upper()


def order_snapshot_executed_qty(snapshot: dict[str, Any] | None) -> float:
    if not isinstance(snapshot, dict):
        return 0.0
    return max(
        safe_float(snapshot.get("executedQty")),
        safe_float(snapshot.get("executedQuantity")),
    )


def order_snapshot_algo_triggered(snapshot: dict[str, Any] | None) -> bool:
    if not isinstance(snapshot, dict):
        return False
    return bool(snapshot.get("actualOrderId")) or safe_float(snapshot.get("actualPrice")) > 0 or safe_float(snapshot.get("triggerTime")) > 0


def take_profit_snapshot_filled(snapshot: dict[str, Any] | None) -> bool:
    status = order_snapshot_status(snapshot)
    return status == "FILLED" or order_snapshot_executed_qty(snapshot) > 0


def stop_loss_snapshot_filled(snapshot: dict[str, Any] | None) -> bool:
    status = order_snapshot_status(snapshot)
    return (
        status in {"FILLED", "TRIGGERED", "FINISHED"}
        or order_snapshot_executed_qty(snapshot) > 0
        or order_snapshot_algo_triggered(snapshot)
    )


def ensure_binance_leverage(
    bridge,
    *,
    symbol: str,
    signal_side: str,
    target_leverage: int,
) -> dict[str, Any]:
    leverage_value = int(target_leverage)
    if leverage_value <= 0:
        raise ValueError(f"invalid target leverage: {target_leverage}")

    response = bridge.set_binance_perp_leverage(symbol=symbol, leverage=leverage_value)
    rows = bridge.get_binance_perp_positions(symbol=symbol)
    target_position_side = hedge_position_side(signal_side)
    matched_row = None
    for row in rows or []:
        if str(row.get("symbol") or "").upper() != str(symbol or "").upper():
            continue
        if str(row.get("positionSide") or "BOTH").upper() == target_position_side:
            matched_row = row
            break
    if matched_row is None and rows:
        matched_row = rows[0]

    leverage_seen = None if matched_row is None else safe_float(matched_row.get("leverage"), math.nan)
    if matched_row is None or math.isnan(leverage_seen) or int(leverage_seen) != leverage_value:
        raise RuntimeError(
            f"binance leverage verify failed for {symbol} {target_position_side}: expected {leverage_value}x, "
            f"got {None if matched_row is None else matched_row.get('leverage')}"
        )

    return {
        "requested_leverage": leverage_value,
        "verified_leverage": int(leverage_seen),
        "position_side": target_position_side,
        "set_response": response,
        "position_snapshot": {
            "symbol": matched_row.get("symbol"),
            "positionSide": matched_row.get("positionSide"),
            "positionAmt": matched_row.get("positionAmt"),
            "entryPrice": matched_row.get("entryPrice"),
            "leverage": matched_row.get("leverage"),
            "marginType": matched_row.get("marginType"),
            "isolated": matched_row.get("isolated"),
            "updateTime": matched_row.get("updateTime"),
        },
    }


def cancel_order_quietly(
    bridge,
    *,
    symbol: str,
    order_id: Any = None,
    client_order_id: str | None = None,
    transport: str | None = None,
) -> None:
    if order_id is None and not client_order_id:
        return
    try:
        if transport == "papi_conditional":
            bridge.cancel_binance_perp_conditional_order(symbol=symbol, strategy_id=order_id, client_order_id=client_order_id)
        elif transport == "fapi_algo":
            bridge.cancel_binance_perp_algo_order(algo_id=order_id, client_algo_id=client_order_id)
        else:
            bridge.cancel_binance_perp_order(symbol=symbol, order_id=order_id, client_order_id=client_order_id)
    except Exception:
        pass


def attach_exit_plan(
    bridge,
    *,
    phase6: dict[str, Any],
    symbol: str,
    side: str,
    signal_timestamp: str | None,
    signal_confirmed_at_override: str | None,
    signal_price: float | None,
    entry_price: float,
    executed_qty: float,
    atr14: float | None,
    run_ctx: RunContext,
    trace_id: str,
    signal_id: str | None,
    intention_id: str | None,
    entry_order_id: Any,
    entry_client_order_id: str | None,
    code_version: str | None,
    config_version: str | None,
) -> dict[str, Any]:
    exit_cfg = phase6["exit"]
    atr14_val = atr14 if atr14 is not None and math.isfinite(atr14) and atr14 > 0 else None
    tp_atr_mult = safe_float(exit_cfg.get("tp_atr_mult", 1.0), 1.0)
    sl_atr_mult = safe_float(exit_cfg.get("sl_atr_mult", 1.0), 1.0)
    if sl_atr_mult <= 0:
        raise ValueError("phase6 exit sl_atr_mult must be > 0")

    allow_soft_sl_fallback = bool(exit_cfg.get("allow_soft_sl_fallback_on_attach_failure", True))

    tp_price = derive_tp_price(
        entry_price=entry_price,
        side=side,
        atr14=atr14_val,
        tp_atr_mult=tp_atr_mult,
        fallback_bps=safe_float(exit_cfg.get("fallback_tp_bps_if_no_atr", 40.0), 40.0),
    )
    sl_price = derive_sl_price(
        entry_price=entry_price,
        side=side,
        atr14=atr14_val,
        sl_atr_mult=sl_atr_mult,
        fallback_bps=safe_float(exit_cfg.get("fallback_sl_bps_if_no_atr", 40.0), 40.0),
    )

    exit_side = exit_order_side(side)
    position_side = hedge_position_side(side)
    sl_cid = make_client_order_id("sl", symbol, run_ctx, trace_id)
    tp_cid = make_client_order_id("tp", symbol, run_ctx, trace_id)

    sl_n = None
    tp_n = None
    sl_attach_error = None
    sl_soft_fallback_active = False

    # 先放 TP；如果 TP 都放不出，直接 hard-fail，避免裸仓暴露。
    try:
        tp_order = bridge.place_binance_perp_live_limit_order(
            symbol=symbol,
            side=exit_side,
            quantity=executed_qty,
            price=tp_price,
            reduce_only=None,
            position_side=position_side,
            client_order_id=tp_cid,
            time_in_force=str(exit_cfg.get("tp_time_in_force", "GTC")),
        )
        tp_n = normalize_order_payload(tp_order, source="take_profit")
    except Exception:
        cancel_order_quietly(
            bridge,
            symbol=symbol,
            order_id=None,
            client_order_id=None,
        )
        raise

    # 再尝试放 SL。若交易所端 STOP/conditional 接口不可用，允许降级到本地软止损轮询。
    try:
        sl_order = bridge.place_binance_perp_live_stop_market_order(
            symbol=symbol,
            side=exit_side,
            quantity=executed_qty,
            stop_price=sl_price,
            reduce_only=None,
            position_side=position_side,
            client_order_id=sl_cid,
            working_type=str(exit_cfg.get("sl_working_type", "CONTRACT_PRICE")),
        )
        sl_n = normalize_order_payload(sl_order, source="stop_loss")
    except Exception as exc:  # noqa: BLE001
        sl_attach_error = str(exc)
        if not allow_soft_sl_fallback:
            # strict 模式下不允许无交易所 SL；撤掉 TP 后抛错给上层执行 emergency flatten。
            cancel_order_quietly(
                bridge,
                symbol=symbol,
                order_id=None if tp_n is None else tp_n.get("order_id"),
                client_order_id=None if tp_n is None else tp_n.get("client_order_id"),
            )
            raise
        sl_soft_fallback_active = True

    timeout_minutes = int(exit_cfg.get("timeout_minutes", 240))
    live_row = {
        "trace_id": trace_id,
        "signal_id": signal_id,
        "signal_timestamp": signal_timestamp,
        "signal_price": signal_price,
        "symbol_bucket": phase6_symbol_bucket(symbol, phase6),
        "signal_confirmed_at": signal_confirmed_at(
            signal_timestamp or "",
            {"signal_confirmed_at_override": signal_confirmed_at_override} if signal_confirmed_at_override else None,
        ),
        "intention_id": intention_id,
        "symbol": symbol,
        "side": side,
        "code_version": code_version,
        "config_version": config_version,
        "entry_order_id": entry_order_id,
        "entry_client_order_id": entry_client_order_id,
        "entry_time": run_ctx.now_iso,
        "entry_price": entry_price,
        "entry_qty": executed_qty,
        "entry_notional": executed_qty * entry_price,
        "atr14": atr14_val,
        "tp_atr_mult": tp_atr_mult,
        "sl_atr_mult": sl_atr_mult,
        "tp_price": tp_price,
        "sl_price": sl_price,
        "tp_order_id": None if tp_n is None else tp_n.get("order_id"),
        "tp_client_order_id": (None if tp_n is None else tp_n.get("client_order_id")) or tp_cid,
        "tp_transport": (None if tp_n is None else tp_n.get("transport")) or "fapi_order",
        "sl_order_id": None if sl_n is None else sl_n.get("order_id"),
        "sl_client_order_id": (None if sl_n is None else sl_n.get("client_order_id")) or (None if sl_n is None else sl_cid),
        "sl_transport": (None if sl_n is None else sl_n.get("transport")) or ("local_soft_stop" if sl_soft_fallback_active else "fapi_order"),
        "sl_soft_fallback_active": sl_soft_fallback_active,
        "sl_attach_error": sl_attach_error,
        "timeout_minutes": timeout_minutes,
        "timeout_at": (run_ctx.now_dt + timedelta_minutes(timeout_minutes)).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    order_rows: list[dict[str, Any]] = []
    if sl_n is not None:
        order_rows.append(
            {
                "timestamp": run_ctx.now_iso,
                "symbol": symbol,
                "side": exit_side,
                "order_role": "stop_loss",
                "order_type": sl_n.get("type") or "STOP_MARKET",
                "price": sl_n.get("stop_price") or sl_n.get("price"),
                "qty": sl_n.get("orig_qty"),
                "status": sl_n.get("status"),
                "exchange_order_id": sl_n.get("order_id"),
                "client_order_id": sl_n.get("client_order_id"),
                "transport": sl_n.get("transport"),
            }
        )

    if tp_n is not None:
        order_rows.append(
            {
                "timestamp": run_ctx.now_iso,
                "symbol": symbol,
                "side": exit_side,
                "order_role": "take_profit",
                "order_type": tp_n.get("type") or "LIMIT",
                "price": tp_n.get("price"),
                "qty": tp_n.get("orig_qty"),
                "status": tp_n.get("status"),
                "exchange_order_id": tp_n.get("order_id"),
                "client_order_id": tp_n.get("client_order_id"),
            }
        )

    warnings: list[dict[str, Any]] = []
    if sl_soft_fallback_active:
        warnings.append(
            {
                "trace_id": trace_id,
                "symbol": symbol,
                "message": "sl_attach_failed_soft_fallback_enabled",
                "payload": {
                    "error": sl_attach_error,
                    "sl_price": sl_price,
                    "fallback": "local_price_poll",
                },
            }
        )

    return {
        "live_row": live_row,
        "tp_order": tp_n,
        "sl_order": sl_n,
        "order_rows": order_rows,
        "warnings": warnings,
    }


ESTIMATED_FEE_BPS_ROUND_TRIP = 6.0


def estimate_fee_and_net(*, entry_price: float, exit_price: float, qty: float, gross_pnl: float) -> tuple[float, float, float]:
    entry_notional = max(0.0, float(entry_price) * float(qty))
    exit_notional = max(0.0, float(exit_price) * float(qty))
    avg_notional = (entry_notional + exit_notional) / 2.0 if (entry_notional + exit_notional) > 0 else 0.0
    fee_usdt = avg_notional * (ESTIMATED_FEE_BPS_ROUND_TRIP / 10000.0)
    net_pnl = float(gross_pnl) - float(fee_usdt)
    avg_notional = (entry_notional + exit_notional) / 2.0 if (entry_notional + exit_notional) > 0 else 0.0
    net_return_bps = (net_pnl / avg_notional * 10000.0) if avg_notional > 0 else 0.0
    return fee_usdt, net_pnl, net_return_bps


def close_position_record(*, pos: dict[str, Any], exit_price: float, exit_time_iso: str, exit_reason: str) -> dict[str, Any]:
    qty = safe_float(pos.get("entry_qty"))
    entry_price = safe_float(pos.get("entry_price"))
    side = str(pos.get("side") or "long")
    pnl = (exit_price - entry_price) * qty if side == "long" else (entry_price - exit_price) * qty
    fee_usdt, net_pnl, net_return_bps = estimate_fee_and_net(entry_price=entry_price, exit_price=exit_price, qty=qty, gross_pnl=pnl)
    entry_time = parse_utc(str(pos.get("entry_time") or ""))
    exit_time = parse_utc(exit_time_iso)
    holding_minutes = None
    if entry_time and exit_time:
        holding_minutes = round((exit_time - entry_time).total_seconds() / 60.0, 2)
    return {
        "trace_id": pos.get("trace_id"),
        "signal_id": pos.get("signal_id"),
        "signal_timestamp": pos.get("signal_timestamp"),
        "signal_price": pos.get("signal_price"),
        "signal_confirmed_at": pos.get("signal_confirmed_at"),
        "symbol": pos.get("symbol"),
        "side": side,
        "entry_time": pos.get("entry_time"),
        "entry_price": entry_price,
        "exit_time": exit_time_iso,
        "exit_price": exit_price,
        "qty": qty,
        "holding_minutes": holding_minutes,
        "exit_reason": exit_reason,
        "gross_pnl": pnl,
        "fee": fee_usdt,
        "fee_is_estimated": True,
        "fee_bps_round_trip": ESTIMATED_FEE_BPS_ROUND_TRIP,
        "net_pnl": net_pnl,
        "net_return_bps": net_return_bps,
        "code_version": pos.get("code_version"),
        "config_version": pos.get("config_version"),
        "entry_order_id": pos.get("entry_order_id"),
        "tp_order_id": pos.get("tp_order_id"),
        "sl_order_id": pos.get("sl_order_id"),
        "timeout_exit_order_id": pos.get("timeout_exit_order_id"),
    }


def exchange_open_qty_for_position(positions_payload: Any, *, symbol: str, side: str) -> float:
    rows = positions_payload if isinstance(positions_payload, list) else [positions_payload]
    pair = symbol.upper()
    normalized_side = str(side or "").strip().lower()
    if normalized_side in {"buy", "long"}:
        normalized_side = "long"
    else:
        normalized_side = "short"
    target_position_side = "LONG" if normalized_side == "long" else "SHORT"
    signed_amt = 0.0
    for row in rows:
        if not isinstance(row, dict):
            continue
        if str(row.get("symbol") or "").upper() != pair:
            continue
        pos_side = str(row.get("positionSide") or "BOTH").upper()
        amt = safe_float(row.get("positionAmt"))
        if pos_side == target_position_side:
            signed_amt += amt
        elif pos_side == "BOTH":
            if normalized_side == "long" and amt > 0:
                signed_amt += amt
            if normalized_side == "short" and amt < 0:
                signed_amt += amt
    return abs(signed_amt)


def extract_exchange_open_positions(positions_payload: Any) -> list[dict[str, Any]]:
    rows = positions_payload if isinstance(positions_payload, list) else [positions_payload]
    out: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        qty = abs(safe_float(row.get("positionAmt")))
        if qty <= 0:
            continue
        symbol = str(row.get("symbol") or "").upper()
        pos_side = str(row.get("positionSide") or "BOTH").upper()
        if pos_side == "LONG":
            side = "long"
        elif pos_side == "SHORT":
            side = "short"
        else:
            amt = safe_float(row.get("positionAmt"))
            side = "long" if amt >= 0 else "short"
        out.append(
            {
                "symbol": symbol,
                "side": side,
                "qty": qty,
                "position_side": pos_side,
                "entry_price": safe_float(row.get("entryPrice")),
                "unrealized_pnl": safe_float(row.get("unRealizedProfit")),
                "raw": row,
            }
        )
    return out


def append_exchange_sanity_warnings(
    *,
    bridge,
    state: Phase6State,
    enabled_symbols: list[str],
    warnings_out: list[dict[str, Any]],
) -> dict[str, int]:
    trace_id = make_trace_id("phase6-exchange-sanity")
    try:
        positions_payload = bridge.get_binance_perp_positions()
    except Exception as exc:  # noqa: BLE001
        append_warning(
            warnings_out,
            trace_id=trace_id,
            symbol="ACCOUNT",
            message="exchange position snapshot query failed",
            payload={"error": str(exc)},
        )
        return {"exchange_open_positions": 0, "unexpected_exchange_positions": 0}

    exchange_positions = extract_exchange_open_positions(positions_payload)
    enabled = {str(symbol).upper() for symbol in enabled_symbols}
    local_qty_by_key: dict[tuple[str, str], float] = {}
    for pos in state.live_positions:
        symbol = str(pos.get("symbol") or "").upper()
        side = str(pos.get("side") or "long").lower()
        key = (symbol, side)
        local_qty_by_key[key] = local_qty_by_key.get(key, 0.0) + abs(safe_float(pos.get("entry_qty")))

    unexpected = 0
    for row in exchange_positions:
        symbol = str(row.get("symbol") or "").upper()
        side = str(row.get("side") or "long").lower()
        key = (symbol, side)
        local_qty = local_qty_by_key.get(key)
        exchange_qty = abs(safe_float(row.get("qty")))
        tolerance = max(1e-9, exchange_qty * 0.01)

        if symbol not in enabled:
            unexpected += 1
            append_warning(
                warnings_out,
                trace_id=trace_id,
                symbol=symbol,
                message="exchange has non-whitelist open position",
                payload={
                    "exchange_position": row,
                    "enabled_symbols": sorted(enabled),
                },
            )
            continue

        if local_qty is None:
            unexpected += 1
            append_warning(
                warnings_out,
                trace_id=trace_id,
                symbol=symbol,
                message="exchange has open position missing from local phase6 state",
                payload={"exchange_position": row},
            )
            continue

        if abs(local_qty - exchange_qty) > tolerance:
            unexpected += 1
            append_warning(
                warnings_out,
                trace_id=trace_id,
                symbol=symbol,
                message="exchange/local position qty mismatch",
                payload={
                    "exchange_position": row,
                    "local_qty": local_qty,
                },
            )

    return {
        "exchange_open_positions": len(exchange_positions),
        "unexpected_exchange_positions": unexpected,
    }


def manage_live_positions(
    *,
    bridge,
    cfg: dict[str, Any],
    state: Phase6State,
    run_ctx: RunContext,
    event_bus: JsonlEventBus,
    events_written: list[dict[str, Any]],
    orders_out: list[dict[str, Any]],
    emitted_orders: list[dict[str, Any]],
    closed_out: list[dict[str, Any]],
    warnings_out: list[dict[str, Any]],
) -> tuple[int, int]:
    managed = 0
    closed = 0
    phase6 = cfg["phase6"]
    query_retry_attempts = int(phase6.get("query_retry_attempts", 3))
    query_retry_sleep = float(phase6.get("query_retry_sleep_seconds", 0.5))

    keep_positions: list[dict[str, Any]] = []
    for pos in state.live_positions:
        managed += 1
        trace_id = str(pos.get("trace_id") or make_trace_id(str(pos.get("signal_id") or "phase6-live")))
        symbol = str(pos.get("symbol"))
        side = str(pos.get("side") or "long")
        exit_done = False

        exchange_qty = None
        try:
            positions_payload = bridge.get_binance_perp_positions(symbol=symbol)
            exchange_qty = exchange_open_qty_for_position(positions_payload, symbol=symbol, side=side)
        except Exception as exc:  # noqa: BLE001
            append_warning(warnings_out, trace_id=trace_id, symbol=symbol, message="position snapshot query failed", payload={"error": str(exc)})

        tp_order_id = pos.get("tp_order_id")
        tp_client_order_id = pos.get("tp_client_order_id")
        tp_transport = pos.get("tp_transport") or "fapi_order"
        sl_order_id = pos.get("sl_order_id")
        sl_client_order_id = pos.get("sl_client_order_id")
        sl_transport = pos.get("sl_transport") or "fapi_order"
        tp_snapshot = None
        sl_snapshot = None

        if tp_order_id or tp_client_order_id:
            try:
                tp_snapshot = query_order_with_retry(
                    bridge,
                    symbol=symbol,
                    order_id=tp_order_id,
                    client_order_id=tp_client_order_id,
                    attempts=query_retry_attempts,
                    sleep_seconds=query_retry_sleep,
                    transport=tp_transport,
                )
            except Exception as exc:  # noqa: BLE001
                append_warning(warnings_out, trace_id=trace_id, symbol=symbol, message="tp order query failed", payload={"error": str(exc)})

        if sl_order_id or sl_client_order_id:
            try:
                sl_snapshot = query_order_with_retry(
                    bridge,
                    symbol=symbol,
                    order_id=sl_order_id,
                    client_order_id=sl_client_order_id,
                    attempts=query_retry_attempts,
                    sleep_seconds=query_retry_sleep,
                    transport=sl_transport,
                )
            except Exception as exc:  # noqa: BLE001
                append_warning(warnings_out, trace_id=trace_id, symbol=symbol, message="sl order query failed", payload={"error": str(exc)})

        tp_filled = False
        sl_filled = False
        if isinstance(tp_snapshot, dict):
            tp_filled = take_profit_snapshot_filled(tp_snapshot)
            if not tp_filled:
                orders_out.append(
                    {
                        "timestamp": run_ctx.now_iso,
                        "symbol": symbol,
                        "side": tp_snapshot.get("side"),
                        "order_role": "take_profit",
                        "order_type": tp_snapshot.get("type"),
                        "price": tp_snapshot.get("price"),
                        "qty": tp_snapshot.get("origQty"),
                        "status": order_snapshot_status(tp_snapshot),
                        "exchange_order_id": tp_snapshot.get("orderId"),
                        "client_order_id": tp_snapshot.get("clientOrderId"),
                    }
                )
        if isinstance(sl_snapshot, dict):
            sl_filled = stop_loss_snapshot_filled(sl_snapshot)
            if not sl_filled:
                orders_out.append(
                    {
                        "timestamp": run_ctx.now_iso,
                        "symbol": symbol,
                        "side": sl_snapshot.get("side"),
                        "order_role": "stop_loss",
                        "order_type": sl_snapshot.get("type") or sl_snapshot.get("strategyType") or sl_snapshot.get("orderType"),
                        "price": sl_snapshot.get("stopPrice") or sl_snapshot.get("triggerPrice") or sl_snapshot.get("price"),
                        "qty": sl_snapshot.get("origQty") or sl_snapshot.get("quantity"),
                        "status": order_snapshot_status(sl_snapshot),
                        "exchange_order_id": sl_snapshot.get("orderId") or sl_snapshot.get("strategyId") or sl_snapshot.get("algoId"),
                        "client_order_id": sl_snapshot.get("clientOrderId") or sl_snapshot.get("newClientStrategyId") or sl_snapshot.get("clientAlgoId"),
                    }
                )

        if tp_filled:
            if exchange_qty is not None and exchange_qty > 0:
                append_warning(
                    warnings_out,
                    trace_id=trace_id,
                    symbol=symbol,
                    message="tp_marked_filled_but_exchange_position_still_open",
                    payload={
                        "exchange_qty": exchange_qty,
                        "tp_status": order_snapshot_status(tp_snapshot),
                        "tp_order_id": tp_order_id,
                    },
                )
            else:
                cancel_order_quietly(bridge, symbol=symbol, order_id=sl_order_id, client_order_id=sl_client_order_id, transport=sl_transport)
                exit_price = safe_float(tp_snapshot.get("avgPrice"), safe_float(tp_snapshot.get("price"), safe_float(pos.get("tp_price"))))
                if exit_price <= 0:
                    exit_price = safe_float(pos.get("tp_price"))
                close_row = close_position_record(
                    pos=pos,
                    exit_price=exit_price,
                    exit_time_iso=run_ctx.now_iso,
                    exit_reason="take_profit",
                )
                closed_out.append(close_row)
                append_event(
                    event_bus,
                    events_written,
                    EventRecord(
                        timestamp=run_ctx.now_iso,
                        event_type=EventType.POSITION_CLOSED,
                        symbol=symbol,
                        side=str(pos.get("side")),
                        trace_id=trace_id,
                        message="phase6 take-profit filled",
                        payload=close_row,
                    ),
                )
                closed += 1
                exit_done = True

        if not exit_done and sl_filled:
            if exchange_qty is not None and exchange_qty > 0:
                append_warning(
                    warnings_out,
                    trace_id=trace_id,
                    symbol=symbol,
                    message="sl_marked_filled_but_exchange_position_still_open",
                    payload={
                        "exchange_qty": exchange_qty,
                        "sl_status": order_snapshot_status(sl_snapshot),
                        "sl_order_id": sl_order_id,
                    },
                )
            else:
                cancel_order_quietly(bridge, symbol=symbol, order_id=tp_order_id, client_order_id=tp_client_order_id, transport=tp_transport)
                exit_price = safe_float(sl_snapshot.get("avgPrice"), safe_float(sl_snapshot.get("stopPrice"), safe_float(pos.get("sl_price"), safe_float(pos.get("entry_price")))))
                close_row = close_position_record(
                    pos=pos,
                    exit_price=exit_price,
                    exit_time_iso=run_ctx.now_iso,
                    exit_reason="stop_loss",
                )
                closed_out.append(close_row)
                append_event(
                    event_bus,
                    events_written,
                    EventRecord(
                        timestamp=run_ctx.now_iso,
                        event_type=EventType.POSITION_CLOSED,
                        symbol=symbol,
                        side=str(pos.get("side")),
                        trace_id=trace_id,
                        message="phase6 stop-loss filled",
                        payload=close_row,
                    ),
                )
                closed += 1
                exit_done = True

        if exit_done:
            continue

        if exchange_qty is not None and exchange_qty <= 0:
            # Second-chance reconciliation: when exchange position is already flat, re-query exits once
            # so we can classify TP/SL instead of collapsing everything into external_flat_reconciled.
            tp_snapshot_recheck = tp_snapshot
            sl_snapshot_recheck = sl_snapshot
            quick_attempts = max(1, min(2, int(query_retry_attempts)))
            quick_sleep = max(0.0, min(float(query_retry_sleep), 0.25))

            if (tp_order_id or tp_client_order_id) and not take_profit_snapshot_filled(tp_snapshot_recheck):
                try:
                    tp_snapshot_recheck = query_order_with_retry(
                        bridge,
                        symbol=symbol,
                        order_id=tp_order_id,
                        client_order_id=tp_client_order_id,
                        attempts=quick_attempts,
                        sleep_seconds=quick_sleep,
                        transport=tp_transport,
                    )
                except Exception as exc:  # noqa: BLE001
                    append_warning(warnings_out, trace_id=trace_id, symbol=symbol, message="tp recheck query failed", payload={"error": str(exc)})

            if (sl_order_id or sl_client_order_id) and not stop_loss_snapshot_filled(sl_snapshot_recheck):
                try:
                    sl_snapshot_recheck = query_order_with_retry(
                        bridge,
                        symbol=symbol,
                        order_id=sl_order_id,
                        client_order_id=sl_client_order_id,
                        attempts=quick_attempts,
                        sleep_seconds=quick_sleep,
                        transport=sl_transport,
                    )
                except Exception as exc:  # noqa: BLE001
                    append_warning(warnings_out, trace_id=trace_id, symbol=symbol, message="sl recheck query failed", payload={"error": str(exc)})

            tp_filled_recheck = take_profit_snapshot_filled(tp_snapshot_recheck)
            sl_filled_recheck = stop_loss_snapshot_filled(sl_snapshot_recheck)

            exit_reason_reconciled = "external_flat_reconciled"
            exit_price_reconciled = safe_float(pos.get("entry_price"))

            tp_px = safe_float(
                (tp_snapshot_recheck or {}).get("avgPrice"),
                safe_float((tp_snapshot_recheck or {}).get("price"), safe_float(pos.get("tp_price"), safe_float(pos.get("entry_price")))),
            )
            sl_px = safe_float(
                (sl_snapshot_recheck or {}).get("actualPrice"),
                safe_float(
                    (sl_snapshot_recheck or {}).get("avgPrice"),
                    safe_float(
                        (sl_snapshot_recheck or {}).get("stopPrice") or (sl_snapshot_recheck or {}).get("triggerPrice"),
                        safe_float(pos.get("sl_price"), safe_float(pos.get("entry_price"))),
                    ),
                ),
            )

            if tp_filled_recheck and not sl_filled_recheck:
                exit_reason_reconciled = "take_profit"
                exit_price_reconciled = tp_px
            elif sl_filled_recheck and not tp_filled_recheck:
                exit_reason_reconciled = "stop_loss"
                exit_price_reconciled = sl_px
            elif tp_filled_recheck and sl_filled_recheck:
                # Rare ambiguous case: both look filled. Prefer closer price to current mark; fallback risk-first.
                mark_px = math.nan
                try:
                    mark_px = bridge.get_binance_perp_last_price(symbol)
                except Exception:
                    pass
                if math.isfinite(mark_px) and tp_px > 0 and sl_px > 0:
                    if abs(mark_px - tp_px) <= abs(mark_px - sl_px):
                        exit_reason_reconciled = "take_profit"
                        exit_price_reconciled = tp_px
                    else:
                        exit_reason_reconciled = "stop_loss"
                        exit_price_reconciled = sl_px
                else:
                    exit_reason_reconciled = "stop_loss"
                    exit_price_reconciled = sl_px if sl_px > 0 else safe_float(pos.get("sl_price"), safe_float(pos.get("entry_price")))
                append_warning(
                    warnings_out,
                    trace_id=trace_id,
                    symbol=symbol,
                    message="flat_reconcile_both_tp_sl_marked_filled",
                    payload={
                        "tp_status": order_snapshot_status(tp_snapshot_recheck),
                        "sl_status": order_snapshot_status(sl_snapshot_recheck),
                    },
                )
            else:
                exit_price_reconciled = safe_float(pos.get("tp_price"), safe_float(pos.get("entry_price")))
                try:
                    exit_price_reconciled = bridge.get_binance_perp_last_price(symbol)
                except Exception:
                    pass

            if exit_price_reconciled <= 0:
                exit_price_reconciled = safe_float(pos.get("entry_price"))

            cancel_order_quietly(bridge, symbol=symbol, order_id=tp_order_id, client_order_id=tp_client_order_id, transport=tp_transport)
            cancel_order_quietly(bridge, symbol=symbol, order_id=sl_order_id, client_order_id=sl_client_order_id, transport=sl_transport)

            close_row = close_position_record(
                pos=pos,
                exit_price=exit_price_reconciled,
                exit_time_iso=run_ctx.now_iso,
                exit_reason=exit_reason_reconciled,
            )
            closed_out.append(close_row)
            append_event(
                event_bus,
                events_written,
                EventRecord(
                    timestamp=run_ctx.now_iso,
                    event_type=EventType.POSITION_CLOSED,
                    symbol=symbol,
                    side=side,
                    trace_id=trace_id,
                    message=(
                        "phase6 reconciled exchange-flat as take-profit"
                        if exit_reason_reconciled == "take_profit"
                        else "phase6 reconciled exchange-flat as stop-loss"
                        if exit_reason_reconciled == "stop_loss"
                        else "phase6 reconciled externally flattened position"
                    ),
                    payload=close_row,
                ),
            )
            closed += 1
            continue

        # soft SL fallback: when exchange-side STOP order is unavailable, enforce SL via local price polling.
        sl_price_val = safe_float(pos.get("sl_price"), math.nan)
        sl_soft_fallback_active = bool(pos.get("sl_soft_fallback_active")) or (
            not sl_order_id and not sl_client_order_id and math.isfinite(sl_price_val) and sl_price_val > 0
        )
        if sl_soft_fallback_active and math.isfinite(sl_price_val) and sl_price_val > 0:
            try:
                mark_price = bridge.get_binance_perp_last_price(symbol)
            except Exception as exc:  # noqa: BLE001
                append_warning(
                    warnings_out,
                    trace_id=trace_id,
                    symbol=symbol,
                    message="soft_sl_price_poll_failed",
                    payload={"error": str(exc), "sl_price": sl_price_val},
                )
            else:
                sl_triggered = (side == "long" and mark_price <= sl_price_val) or (side == "short" and mark_price >= sl_price_val)
                if sl_triggered:
                    cancel_order_quietly(
                        bridge,
                        symbol=symbol,
                        order_id=tp_order_id,
                        client_order_id=tp_client_order_id,
                        transport=tp_transport,
                    )
                    close_side = exit_order_side(side)
                    close_qty = safe_float(pos.get("entry_qty"))
                    close_cid = make_client_order_id("ss", symbol, run_ctx, trace_id)
                    market_close = bridge.place_binance_perp_live_market_order(
                        symbol=symbol,
                        side=close_side,
                        quantity=close_qty,
                        reduce_only=None,
                        position_side=hedge_position_side(side),
                        client_order_id=close_cid,
                    )
                    market_close_n = normalize_order_payload(market_close, source="soft_stop_fallback")
                    close_row = close_position_record(
                        pos=pos,
                        exit_price=safe_float(
                            market_close_n.get("avg_price"),
                            safe_float(market_close_n.get("price"), sl_price_val),
                        ),
                        exit_time_iso=run_ctx.now_iso,
                        exit_reason="soft_stop_poll_market",
                    )
                    closed_out.append(close_row)
                    timeout_order_row = {
                        "timestamp": run_ctx.now_iso,
                        "symbol": symbol,
                        "side": close_side,
                        "order_role": "soft_stop_fallback_exit",
                        "order_type": "MARKET",
                        "price": market_close_n.get("avg_price") or market_close_n.get("price"),
                        "qty": market_close_n.get("executed_qty") or market_close_n.get("orig_qty"),
                        "status": market_close_n.get("status"),
                        "exchange_order_id": market_close_n.get("order_id"),
                        "client_order_id": market_close_n.get("client_order_id"),
                    }
                    orders_out.append(timeout_order_row)
                    emitted_orders.append(timeout_order_row)
                    append_event(
                        event_bus,
                        events_written,
                        EventRecord(
                            timestamp=run_ctx.now_iso,
                            event_type=EventType.POSITION_CLOSED,
                            symbol=symbol,
                            side=str(pos.get("side")),
                            trace_id=trace_id,
                            message="phase6 soft stop fallback triggered market close",
                            payload={
                                "sl_price": sl_price_val,
                                "mark_price": mark_price,
                                "close_order": market_close_n,
                                "close_row": close_row,
                            },
                        ),
                    )
                    closed += 1
                    continue

        timeout_at = parse_utc(str(pos.get("timeout_at") or ""))
        if timeout_at is not None and run_ctx.now_dt >= timeout_at:
            cancel_order_quietly(bridge, symbol=symbol, order_id=tp_order_id, client_order_id=tp_client_order_id, transport=tp_transport)
            cancel_order_quietly(bridge, symbol=symbol, order_id=sl_order_id, client_order_id=sl_client_order_id, transport=sl_transport)

            close_side = exit_order_side(str(pos.get("side") or "long"))
            close_qty = safe_float(pos.get("entry_qty"))
            close_cid = make_client_order_id("to", symbol, run_ctx, trace_id)
            market_close = bridge.place_binance_perp_live_market_order(
                symbol=symbol,
                side=close_side,
                quantity=close_qty,
                reduce_only=None,
                position_side=hedge_position_side(side),
                client_order_id=close_cid,
            )
            market_close_n = normalize_order_payload(market_close, source="timeout_exit")
            timeout_order_row = {
                "timestamp": run_ctx.now_iso,
                "symbol": symbol,
                "side": close_side,
                "order_role": "timeout_exit",
                "order_type": "MARKET",
                "price": market_close_n.get("avg_price") or market_close_n.get("price"),
                "qty": market_close_n.get("executed_qty") or market_close_n.get("orig_qty"),
                "status": market_close_n.get("status"),
                "exchange_order_id": market_close_n.get("order_id"),
                "client_order_id": market_close_n.get("client_order_id"),
            }
            orders_out.append(timeout_order_row)
            emitted_orders.append(timeout_order_row)
            exit_price = safe_float(market_close_n.get("avg_price"), safe_float(market_close_n.get("price"), safe_float(pos.get("entry_price"))))
            pos["timeout_exit_order_id"] = market_close_n.get("order_id")
            close_row = close_position_record(
                pos=pos,
                exit_price=exit_price,
                exit_time_iso=run_ctx.now_iso,
                exit_reason="timeout_market",
            )
            closed_out.append(close_row)
            append_event(
                event_bus,
                events_written,
                EventRecord(
                    timestamp=run_ctx.now_iso,
                    event_type=EventType.POSITION_CLOSED,
                    symbol=symbol,
                    side=str(pos.get("side")),
                    trace_id=trace_id,
                    message="phase6 timeout triggered market close",
                    payload=close_row,
                ),
            )
            closed += 1
            continue

        keep_positions.append(pos)

    state.live_positions = keep_positions
    return managed, closed


def manage_pending_entries(
    *,
    bridge,
    cfg: dict[str, Any],
    state: Phase6State,
    run_ctx: RunContext,
    event_bus: JsonlEventBus,
    events_written: list[dict[str, Any]],
    orders_out: list[dict[str, Any]],
    emitted_orders: list[dict[str, Any]],
    warnings_out: list[dict[str, Any]],
) -> tuple[int, int]:
    phase6 = cfg["phase6"]
    current_config_version = config_hash(cfg)
    current_code_version = code_version()
    query_retry_attempts = int(phase6.get("query_retry_attempts", 3))
    query_retry_sleep = float(phase6.get("query_retry_sleep_seconds", 0.5))
    fallback_to_market = bool(phase6["entry"].get("fallback_to_market_on_ttl", True))
    target_leverage = max(1, int(safe_float(phase6.get("default_leverage", 1), 1)))

    moved_to_live = 0
    managed = 0
    keep_pending: list[dict[str, Any]] = []

    for pending in state.pending_entries:
        managed += 1
        trace_id = str(pending.get("trace_id") or make_trace_id(str(pending.get("signal_id") or "phase6-pending")))
        symbol = str(pending.get("symbol"))
        side = str(pending.get("side"))
        entry_order_id = pending.get("entry_order_id")
        entry_client_order_id = pending.get("entry_client_order_id")

        try:
            snap = query_order_with_retry(
                bridge,
                symbol=symbol,
                order_id=entry_order_id,
                client_order_id=entry_client_order_id,
                attempts=query_retry_attempts,
                sleep_seconds=query_retry_sleep,
            )
        except Exception as exc:  # noqa: BLE001
            append_warning(warnings_out, trace_id=trace_id, symbol=symbol, message="entry order query failed", payload={"error": str(exc)})
            keep_pending.append(pending)
            continue

        status = str(snap.get("status") or "").upper()
        executed_qty = safe_float(snap.get("executedQty"))
        avg_price = safe_float(snap.get("avgPrice"), safe_float(snap.get("price"), safe_float(pending.get("signal_price"))))
        orders_out.append(
            {
                "timestamp": run_ctx.now_iso,
                "symbol": symbol,
                "side": snap.get("side"),
                "order_role": "entry",
                "order_type": snap.get("type"),
                "price": snap.get("price"),
                "qty": snap.get("origQty"),
                "status": snap.get("status"),
                "exchange_order_id": snap.get("orderId"),
                "client_order_id": snap.get("clientOrderId"),
            }
        )

        is_filled = status == "FILLED" or (executed_qty > 0 and status in {"PARTIALLY_FILLED", "FILLED"})
        if not is_filled:
            expire_at = parse_utc(str(pending.get("entry_expires_at") or ""))
            if expire_at is not None and run_ctx.now_dt >= expire_at:
                try:
                    bridge.cancel_binance_perp_order(symbol=symbol, order_id=entry_order_id, client_order_id=entry_client_order_id)
                except Exception:
                    pass

                if fallback_to_market:
                    remaining_qty = max(0.0, safe_float(pending.get("planned_qty")) - executed_qty)
                    if remaining_qty > 0:
                        leverage_guard = ensure_binance_leverage(
                            bridge,
                            symbol=symbol,
                            signal_side=side,
                            target_leverage=target_leverage,
                        )
                        append_event(
                            event_bus,
                            events_written,
                            EventRecord(
                                timestamp=run_ctx.now_iso,
                                event_type=EventType.ORDER_STATUS_SYNC,
                                symbol=symbol,
                                side=side,
                                trace_id=trace_id,
                                message="phase6 leverage enforced before fallback market entry",
                                payload=leverage_guard,
                            ),
                        )
                        fallback_cid = make_client_order_id("fb", symbol, run_ctx, trace_id)
                        market_entry = bridge.place_binance_perp_live_market_order(
                            symbol=symbol,
                            side=signal_to_order_side(side),
                            quantity=remaining_qty,
                            reduce_only=None,
                            position_side=hedge_position_side(side),
                            client_order_id=fallback_cid,
                        )
                        market_entry_n = normalize_order_payload(market_entry, source="entry_fallback_market")
                        executed_qty = safe_float(market_entry_n.get("executed_qty"), remaining_qty)
                        avg_price = safe_float(market_entry_n.get("avg_price"), avg_price)
                        fallback_order_row = {
                            "timestamp": run_ctx.now_iso,
                            "symbol": symbol,
                            "side": signal_to_order_side(side),
                            "order_role": "entry_fallback",
                            "order_type": "MARKET",
                            "price": market_entry_n.get("avg_price") or market_entry_n.get("price"),
                            "qty": market_entry_n.get("executed_qty") or market_entry_n.get("orig_qty"),
                            "status": market_entry_n.get("status"),
                            "exchange_order_id": market_entry_n.get("order_id"),
                            "client_order_id": market_entry_n.get("client_order_id"),
                        }
                        orders_out.append(fallback_order_row)
                        emitted_orders.append(fallback_order_row)
                        is_filled = executed_qty > 0
                if not is_filled:
                    append_warning(
                        warnings_out,
                        trace_id=trace_id,
                        symbol=symbol,
                        message="entry expired without fill",
                        payload={"order_id": entry_order_id, "status": status},
                    )
                    append_event(
                        event_bus,
                        events_written,
                        EventRecord(
                            timestamp=run_ctx.now_iso,
                            event_type=EventType.ORDER_CANCELLED,
                            symbol=symbol,
                            side=side,
                            trace_id=trace_id,
                            message="phase6 pending entry expired and canceled",
                            payload={"order_id": entry_order_id, "status": status},
                        ),
                    )
                    continue
            else:
                keep_pending.append(pending)
                continue

        if executed_qty <= 0:
            keep_pending.append(pending)
            continue

        atr14 = safe_float(pending.get("atr14"), math.nan)
        atr14_val = atr14 if math.isfinite(atr14) and atr14 > 0 else None
        try:
            exit_plan = attach_exit_plan(
                bridge,
                phase6=phase6,
                symbol=symbol,
                side=side,
                signal_timestamp=str(pending.get("signal_timestamp") or ""),
                signal_confirmed_at_override=str(pending.get("signal_confirmed_at") or "") or None,
                signal_price=pending.get("signal_price"),
                entry_price=avg_price,
                executed_qty=executed_qty,
                atr14=atr14_val,
                run_ctx=run_ctx,
                trace_id=trace_id,
                signal_id=str(pending.get("signal_id") or ""),
                intention_id=str(pending.get("intention_id") or ""),
                entry_order_id=entry_order_id,
                entry_client_order_id=entry_client_order_id,
                code_version=str(pending.get("code_version") or current_code_version),
                config_version=str(pending.get("config_version") or current_config_version),
            )
        except Exception as exc:  # noqa: BLE001
            append_warning(
                warnings_out,
                trace_id=trace_id,
                symbol=symbol,
                message="exit attach failed after pending entry fill; emergency flatten triggered",
                payload={"error": str(exc), "entry_order_id": entry_order_id},
            )
            emergency_cid = make_client_order_id("ec", symbol, run_ctx, trace_id)
            emergency_close = bridge.place_binance_perp_live_market_order(
                symbol=symbol,
                side=exit_order_side(side),
                quantity=executed_qty,
                reduce_only=None,
                position_side=hedge_position_side(side),
                client_order_id=emergency_cid,
            )
            emergency_n = normalize_order_payload(emergency_close, source="emergency_flatten")
            exit_price = safe_float(emergency_n.get("avg_price"), safe_float(emergency_n.get("price"), avg_price))
            gross_pnl = (exit_price - avg_price) * executed_qty if side == "long" else (avg_price - exit_price) * executed_qty
            fee_usdt, net_pnl, net_return_bps = estimate_fee_and_net(entry_price=avg_price, exit_price=exit_price, qty=executed_qty, gross_pnl=gross_pnl)
            close_row = {
                "trace_id": trace_id,
                "signal_id": pending.get("signal_id"),
                "signal_timestamp": pending.get("signal_timestamp"),
                "signal_price": pending.get("signal_price"),
                "symbol": symbol,
                "side": side,
                "code_version": pending.get("code_version") or current_code_version,
                "config_version": pending.get("config_version") or current_config_version,
                "entry_time": run_ctx.now_iso,
                "entry_price": avg_price,
                "exit_time": run_ctx.now_iso,
                "exit_price": exit_price,
                "qty": executed_qty,
                "holding_minutes": 0.0,
                "exit_reason": "exit_attach_failed_market_close",
                "gross_pnl": gross_pnl,
                "fee": fee_usdt,
                "fee_is_estimated": True,
                "fee_bps_round_trip": ESTIMATED_FEE_BPS_ROUND_TRIP,
                "net_pnl": net_pnl,
                "net_return_bps": net_return_bps,
                "entry_order_id": entry_order_id,
                "tp_order_id": None,
                "sl_order_id": None,
                "timeout_exit_order_id": emergency_n.get("order_id"),
            }
            state.closed_trades.append(close_row)
            emergency_order_rows = [
                {
                    "timestamp": run_ctx.now_iso,
                    "symbol": symbol,
                    "side": snap.get("side"),
                    "order_role": "entry",
                    "order_type": snap.get("type"),
                    "price": snap.get("avgPrice") or snap.get("price"),
                    "qty": executed_qty,
                    "status": snap.get("status"),
                    "exchange_order_id": snap.get("orderId"),
                    "client_order_id": snap.get("clientOrderId"),
                },
                {
                    "timestamp": run_ctx.now_iso,
                    "symbol": symbol,
                    "side": exit_order_side(side),
                    "order_role": "emergency_flatten",
                    "order_type": "MARKET",
                    "price": emergency_n.get("avg_price") or emergency_n.get("price"),
                    "qty": emergency_n.get("executed_qty") or emergency_n.get("orig_qty"),
                    "status": emergency_n.get("status"),
                    "exchange_order_id": emergency_n.get("order_id"),
                    "client_order_id": emergency_n.get("client_order_id"),
                },
            ]
            orders_out.extend(emergency_order_rows)
            emitted_orders.extend(emergency_order_rows)
            append_event(
                event_bus,
                events_written,
                EventRecord(
                    timestamp=run_ctx.now_iso,
                    event_type=EventType.POSITION_CLOSED,
                    symbol=symbol,
                    side=side,
                    trace_id=trace_id,
                    message="phase6 exit attach failed after pending fill; emergency market flatten executed",
                    payload={"entry": snap, "emergency_close": emergency_n, "error": str(exc)},
                    level="WARN",
                ),
            )
            continue

        live_row = exit_plan["live_row"]
        tp_n = exit_plan["tp_order"]
        sl_n = exit_plan["sl_order"]
        state.live_positions.append(live_row)
        moved_to_live += 1

        for warn in exit_plan.get("warnings", []):
            append_warning(
                warnings_out,
                trace_id=str(warn.get("trace_id") or trace_id),
                symbol=str(warn.get("symbol") or symbol),
                message=str(warn.get("message") or "exit_plan_warning"),
                payload=warn.get("payload"),
            )

        orders_out.extend(exit_plan["order_rows"])
        emitted_orders.extend(exit_plan["order_rows"])
        append_event(
            event_bus,
            events_written,
            EventRecord(
                timestamp=run_ctx.now_iso,
                event_type=EventType.POSITION_OPENED,
                symbol=symbol,
                side=side,
                trace_id=trace_id,
                message="phase6 entry filled and exit plan placed",
                payload={
                    "entry_order_id": entry_order_id,
                    "entry_qty": executed_qty,
                    "entry_price": avg_price,
                    "tp_order_id": None if tp_n is None else tp_n.get("order_id"),
                    "tp_price": live_row.get("tp_price"),
                    "sl_order_id": None if sl_n is None else sl_n.get("order_id"),
                    "sl_price": live_row.get("sl_price"),
                    "sl_soft_fallback_active": bool(live_row.get("sl_soft_fallback_active")),
                },
            ),
        )

    state.pending_entries = keep_pending
    return managed, moved_to_live


def timedelta_minutes(minutes: int) -> timedelta:
    return timedelta(minutes=int(minutes))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Rank 32b canary Phase-6 auto strategy runner.")
    parser.add_argument("--config", default=str(CONFIG_PATH))
    parser.add_argument("--force-replay", action="store_true", help="Ignore seen signal ids and replay current recent window.")
    args = parser.parse_args()

    ensure_dir(ART_DIR)
    cfg = load_yaml(Path(args.config))
    phase3 = cfg["phase3"]
    phase6 = cfg["phase6"]
    current_config_version = config_hash(cfg)
    current_code_version = code_version()

    bridge = load_frmonitor_bridge(
        phase3["fr_monitor_root"],
        local_private_path=phase3.get("local_private_path"),
    )

    run_ctx = utcnow()
    state = load_state(STATE_PATH, list(cfg["universe"]["symbols"]))
    state.reset_daily_counter_if_needed(run_ctx.now_dt)
    event_bus = JsonlEventBus(EVENTS_PATH)

    events_written: list[dict[str, Any]] = []
    warnings_out: list[dict[str, Any]] = []
    intentions_out: list[dict[str, Any]] = []
    orders_out: list[dict[str, Any]] = []
    emitted_orders: list[dict[str, Any]] = []
    rejections_out: list[dict[str, Any]] = []
    closed_out: list[dict[str, Any]] = []

    managed_pending, moved_to_live = manage_pending_entries(
        bridge=bridge,
        cfg=cfg,
        state=state,
        run_ctx=run_ctx,
        event_bus=event_bus,
        events_written=events_written,
        orders_out=orders_out,
        emitted_orders=emitted_orders,
        warnings_out=warnings_out,
    )

    managed_live, closed_count = manage_live_positions(
        bridge=bridge,
        cfg=cfg,
        state=state,
        run_ctx=run_ctx,
        event_bus=event_bus,
        events_written=events_written,
        orders_out=orders_out,
        emitted_orders=emitted_orders,
        closed_out=closed_out,
        warnings_out=warnings_out,
    )
    state.closed_trades.extend(closed_out)
    save_state_checkpoint(state, symbols=list(cfg["universe"]["symbols"]), now_iso=run_ctx.now_iso)

    exchange_sanity = append_exchange_sanity_warnings(
        bridge=bridge,
        state=state,
        enabled_symbols=list(cfg["universe"]["symbols"]),
        warnings_out=warnings_out,
    )
    own_busy_symbols = {
        str(row.get("symbol") or "").upper()
        for row in [*(state.live_positions or []), *(state.pending_entries or [])]
        if row.get("symbol")
    }
    conflict_busy_symbols, conflict_warnings = load_phase6_conflict_busy_symbols(cfg, bridge, own_busy_symbols)
    for warning in conflict_warnings:
        append_warning(
            warnings_out,
            trace_id=make_trace_id(f"phase6-cross-lane-{warning.get('payload', {}).get('symbol', 'system') or 'system'}"),
            symbol=str((warning.get("payload") or {}).get("symbol") or "SYSTEM"),
            message=str(warning.get("message") or "cross_lane_conflict_warning"),
            payload=warning.get("payload") or {},
        )
    safety_cfg = phase6.get("safety", {}) if isinstance(phase6.get("safety"), dict) else {}
    exit_attach_failure_pause = detect_recent_exit_attach_failure_pause(
        state,
        now_dt=run_ctx.now_dt,
        cooldown_minutes=int(safety_cfg.get("pause_new_entries_minutes_after_exit_attach_failure", 1440)),
        current_code_version=current_code_version,
    )
    if exit_attach_failure_pause:
        append_warning(
            warnings_out,
            trace_id=make_trace_id("phase6-entry-safety-pause"),
            symbol=str(exit_attach_failure_pause.get("symbol") or "SYSTEM"),
            message="entry_safety_pause_recent_exit_attach_failure",
            payload=exit_attach_failure_pause,
        )

    adapter = Rank32BPerpSignalAdapter(
        asset_to_symbol=cfg["universe"]["asset_to_symbol"],
        days=int(cfg["signal_adapter"]["lookback_days"]),
        recent_hours=int(cfg["signal_adapter"]["recent_hours"]),
        variant=str(cfg["signal_adapter"]["variant"]),
        refresh_bars=bool(cfg["signal_adapter"].get("refresh_bars", True)),
        refresh_tail_days=(
            int(cfg["signal_adapter"]["refresh_tail_days"])
            if cfg["signal_adapter"].get("refresh_tail_days") is not None
            else None
        ),
        preview_unclosed_15m=bool(cfg["signal_adapter"].get("preview_unclosed_15m", False)),
        preview_fetch_limit=int(cfg["signal_adapter"].get("preview_fetch_limit", 30)),
        entry_delay_minutes=int(cfg["signal_adapter"].get("entry_delay_minutes", 1)),
        official_signal_ttl_minutes=int(safety_cfg.get("max_signal_age_minutes", 30)),
    )
    snapshot = adapter.load_recent_signals()
    recent_signals = [sig.to_dict() for sig in snapshot.signals]
    seen = set() if args.force_replay else set(state.seen_signal_ids)
    if not args.force_replay:
        seen.update(str(row.get("signal_id")) for row in state.pending_entries if row.get("signal_id"))
        seen.update(str(row.get("signal_id")) for row in state.live_positions if row.get("signal_id"))
        seen.update(str(row.get("signal_id")) for row in state.closed_trades if row.get("signal_id"))
    consumed_bar_keys = set() if args.force_replay else set(state.consumed_signal_bars)
    run_consumed_bar_keys: set[str] = set()
    new_signals = [sig for sig in snapshot.signals if sig.signal_id not in seen]
    new_signals, skipped_weaker_signals = select_signals_for_execution(new_signals, phase6)

    max_signal_age_minutes = safe_float(safety_cfg.get("max_signal_age_minutes", 30), 30.0)
    max_signal_age_seconds = max(0.0, max_signal_age_minutes * 60.0)
    filtered_signals: list[Any] = []
    stale_signals: list[tuple[Any, float]] = []
    for sig in new_signals:
        confirmed_ts = signal_confirmed_at(
            str(getattr(sig, "timestamp", "")),
            getattr(sig, "metadata", None),
        ) or str(getattr(sig, "timestamp", ""))
        signal_ts = parse_utc(confirmed_ts) or run_ctx.now_dt
        if signal_ts > run_ctx.now_dt:
            continue
        age_seconds = max(0.0, (run_ctx.now_dt - signal_ts).total_seconds())
        if max_signal_age_seconds > 0 and age_seconds > max_signal_age_seconds:
            stale_signals.append((sig, age_seconds))
        else:
            filtered_signals.append(sig)
    new_signals = limit_new_signals_for_execution(filtered_signals, phase6)

    for sig, age_seconds in stale_signals:
        trace_id = make_trace_id(sig.signal_id)
        reject_row = {
            **sig.to_dict(),
            "signal_confirmed_at": signal_confirmed_at(sig.timestamp, getattr(sig, "metadata", None)),
            "risk": {
                "allowed": False,
                "reason": "signal_too_old",
                "signal_age_seconds": round(age_seconds, 2),
                "max_signal_age_seconds": round(max_signal_age_seconds, 2),
            },
        }
        rejections_out.append(reject_row)
        append_warning(
            warnings_out,
            trace_id=trace_id,
            symbol=sig.symbol,
            message="signal_too_old",
            payload=reject_row["risk"],
        )
        append_event(
            event_bus,
            events_written,
            EventRecord(
                timestamp=run_ctx.now_iso,
                event_type=EventType.RISK_REJECTED,
                symbol=sig.symbol,
                side=sig.side.value,
                trace_id=trace_id,
                message="signal_too_old",
                payload=reject_row,
                level="WARN",
            ),
        )
        state.seen_signal_ids.append(sig.signal_id)

    for skipped in skipped_weaker_signals:
        signal_id = str(skipped.get("signal_id") or "")
        if signal_id:
            state.seen_signal_ids.append(signal_id)
        bar_key = signal_bar_key(str(skipped.get("symbol") or ""), str(skipped.get("timestamp") or ""))
        if bar_key not in consumed_bar_keys:
            state.consumed_signal_bars.append(bar_key)
            consumed_bar_keys.add(bar_key)
        rejections_out.append(
            {
                **skipped,
                "risk": {
                    "allowed": False,
                    "reason": skipped.get("reason"),
                    "selection_metric": skipped.get("selection_metric"),
                    "signal_strength": skipped.get("signal_strength"),
                    "selected_signal_id": skipped.get("selected_signal_id"),
                    "selected_symbol": skipped.get("selected_symbol"),
                    "selected_strength": skipped.get("selected_strength"),
                },
            }
        )

    smallcap_cfg = phase6_smallcap_cfg(phase6)
    smallcap_symbols = phase6_smallcap_symbols(phase6)
    risk_cfg = Canary32BRiskConfig(
        kill_switch=bool(cfg["risk"]["kill_switch"]),
        trade_enabled=bool(cfg["risk"]["trade_enabled"]),
        enabled_symbols=list(cfg["universe"]["symbols"]),
        max_concurrent_positions=int(cfg["risk"]["max_concurrent_positions"]),
        max_daily_trades=int(cfg["risk"]["max_daily_trades"]),
        max_position_notional_per_symbol=float(cfg["risk"]["max_position_notional_per_symbol"]),
        allow_entry_fallback_to_taker=bool(cfg["execution"]["entry"]["allow_fallback_to_taker"]),
        max_data_delay_seconds=int(cfg["risk"]["max_data_delay_seconds"]),
        require_atr=bool(cfg["risk"].get("require_atr", True)),
        smallcap_symbols=smallcap_symbols,
        max_core_positions=int(cfg["risk"].get("max_core_positions", 1)),
        max_smallcap_positions=int(smallcap_cfg.get("max_concurrent_positions", 1)) if smallcap_symbols else None,
    )

    for signal in new_signals:
        trace_id = make_trace_id(signal.signal_id)
        signal_bucket = annotate_signal_bucket(signal, phase6)
        bar_key = signal_bar_key(signal.symbol, signal.timestamp, bar_minutes=15)
        append_event(
            event_bus,
            events_written,
            EventRecord(
                timestamp=run_ctx.now_iso,
                event_type=EventType.SIGNAL_RECEIVED,
                symbol=signal.symbol,
                side=signal.side.value,
                trace_id=trace_id,
                message="phase6 received signal",
                payload={**signal.to_dict(), "signal_confirmed_at": signal_confirmed_at(signal.timestamp, getattr(signal, "metadata", None)), "bar_key": bar_key},
            ),
        )

        if bar_key in consumed_bar_keys or bar_key in run_consumed_bar_keys:
            reject_row = {**signal.to_dict(), "bar_key": bar_key, "reason": "same_bar_signal_already_consumed"}
            rejections_out.append(reject_row)
            append_warning(
                warnings_out,
                trace_id=trace_id,
                symbol=signal.symbol,
                message="same_bar_signal_already_consumed",
                payload={"bar_key": bar_key},
            )
            append_event(
                event_bus,
                events_written,
                EventRecord(
                    timestamp=run_ctx.now_iso,
                    event_type=EventType.RISK_REJECTED,
                    symbol=signal.symbol,
                    side=signal.side.value,
                    trace_id=trace_id,
                    message="same_bar_signal_already_consumed",
                    payload=reject_row,
                    level="WARN",
                ),
            )
            state.seen_signal_ids.append(signal.signal_id)
            save_state_checkpoint(state, symbols=list(cfg["universe"]["symbols"]), now_iso=run_ctx.now_iso)
            continue

        if signal.symbol in conflict_busy_symbols:
            reject_row = {
                **signal.to_dict(),
                "signal_confirmed_at": signal_confirmed_at(signal.timestamp, getattr(signal, "metadata", None)),
                "bar_key": bar_key,
                "risk": {"allowed": False, "reason": "cross_lane_symbol_busy", "conflict_symbols": sorted(conflict_busy_symbols)},
            }
            rejections_out.append(reject_row)
            append_warning(
                warnings_out,
                trace_id=trace_id,
                symbol=signal.symbol,
                message="cross_lane_symbol_busy",
                payload={"conflict_busy_symbols": sorted(conflict_busy_symbols)},
            )
            append_event(
                event_bus,
                events_written,
                EventRecord(
                    timestamp=run_ctx.now_iso,
                    event_type=EventType.RISK_REJECTED,
                    symbol=signal.symbol,
                    side=signal.side.value,
                    trace_id=trace_id,
                    message="cross_lane_symbol_busy",
                    payload=reject_row,
                    level="WARN",
                ),
            )
            state.seen_signal_ids.append(signal.signal_id)
            state.consumed_signal_bars.append(bar_key)
            consumed_bar_keys.add(bar_key)
            save_state_checkpoint(state, symbols=list(cfg["universe"]["symbols"]), now_iso=run_ctx.now_iso)
            continue

        if exit_attach_failure_pause:
            reject_row = {
                **signal.to_dict(),
                "signal_confirmed_at": signal_confirmed_at(signal.timestamp, getattr(signal, "metadata", None)),
                "bar_key": bar_key,
                "risk": {
                    "allowed": False,
                    "reason": "entry_safety_pause_recent_exit_attach_failure",
                    "pause": exit_attach_failure_pause,
                },
            }
            rejections_out.append(reject_row)
            append_event(
                event_bus,
                events_written,
                EventRecord(
                    timestamp=run_ctx.now_iso,
                    event_type=EventType.RISK_REJECTED,
                    symbol=signal.symbol,
                    side=signal.side.value,
                    trace_id=trace_id,
                    message="entry_safety_pause_recent_exit_attach_failure",
                    payload=reject_row,
                    level="WARN",
                ),
            )
            state.seen_signal_ids.append(signal.signal_id)
            save_state_checkpoint(state, symbols=list(cfg["universe"]["symbols"]), now_iso=run_ctx.now_iso)
            continue

        signal_ts = parse_utc(signal_confirmed_at(signal.timestamp, getattr(signal, "metadata", None)) or signal.timestamp) or run_ctx.now_dt
        age_seconds = max(0.0, (run_ctx.now_dt - signal_ts).total_seconds())
        market_ctx = Canary32BMarketContext(
            atr_available=bool(signal.metadata.get("atr_ready", False)),
            data_delay_seconds=age_seconds,
            metadata={"variant": signal.metadata.get("variant"), "symbol_bucket": signal_bucket},
        )
        portfolio = portfolio_state_from_runtime(
            state.symbol_states,
            state.daily_trade_count,
            api_healthy=True,
            live_positions=state.live_positions,
            pending_entries=state.pending_entries,
            smallcap_symbols=smallcap_symbols,
        )
        if signal_bucket == "smallcap" and bool(smallcap_cfg.get("enabled", False)):
            activity_snapshot = smallcap_activity_snapshot(signal.symbol, phase6, run_ctx.now_dt)
            signal.metadata["smallcap_activity"] = activity_snapshot
            if not bool(activity_snapshot.get("allowed", False)):
                reject_row = {
                    **signal.to_dict(),
                    "risk": {
                        "allowed": False,
                        "reason": "smallcap_activity_percentile_below_floor",
                        "activity": activity_snapshot,
                    },
                }
                rejections_out.append(reject_row)
                append_warning(warnings_out, trace_id=trace_id, symbol=signal.symbol, message="smallcap_activity_percentile_below_floor", payload=activity_snapshot)
                append_event(
                    event_bus,
                    events_written,
                    EventRecord(
                        timestamp=run_ctx.now_iso,
                        event_type=EventType.RISK_REJECTED,
                        symbol=signal.symbol,
                        side=signal.side.value,
                        trace_id=trace_id,
                        message="smallcap_activity_percentile_below_floor",
                        payload=reject_row,
                        level="WARN",
                    ),
                )
                state.seen_signal_ids.append(signal.signal_id)
                save_state_checkpoint(state, symbols=list(cfg["universe"]["symbols"]), now_iso=run_ctx.now_iso)
                continue
        decision = evaluate_entry_risk(signal, trace_id=trace_id, config=risk_cfg, portfolio=portfolio, market=market_ctx)
        if not decision.accepted:
            reject_row = {**signal.to_dict(), "risk": decision.to_dict()}
            rejections_out.append(reject_row)
            append_warning(warnings_out, trace_id=trace_id, symbol=signal.symbol, message=decision.reason, payload=decision.to_dict())
            append_event(
                event_bus,
                events_written,
                EventRecord(
                    timestamp=run_ctx.now_iso,
                    event_type=EventType.RISK_REJECTED,
                    symbol=signal.symbol,
                    side=signal.side.value,
                    trace_id=trace_id,
                    message=decision.reason,
                    payload=reject_row,
                    level="WARN",
                ),
            )
            state.seen_signal_ids.append(signal.signal_id)
            save_state_checkpoint(state, symbols=list(cfg["universe"]["symbols"]), now_iso=run_ctx.now_iso)
            continue

        run_consumed_bar_keys.add(bar_key)
        state.consumed_signal_bars.append(bar_key)

        signal_side = signal.side.value
        symbol = signal.symbol
        notional_cfg = resolve_symbol_desired_notional_usdt(phase6, symbol)
        rules = bridge.get_binance_perp_trade_rules(symbol)
        last_price = bridge.get_binance_perp_last_price(symbol)
        sizing_floor = bridge.estimate_binance_min_trade_floor(symbol, last_price=last_price, rules=rules)
        floor_notional = safe_float(sizing_floor.get("effective_min_notional"), 5.0)
        buffer_mult = max(1.0, float(phase6["sizing"].get("min_notional_buffer_mult", 1.0)))
        target_notional = max(notional_cfg, floor_notional * buffer_mult)
        qty_info = bridge.derive_binance_qty_from_notional(symbol, target_notional, last_price=last_price, rules=rules)
        quantity = safe_float(qty_info.get("quantity"))

        intention_id = f"intent-{hashlib.sha1((signal.signal_id + '|phase6').encode('utf-8')).hexdigest()[:14]}"
        intended_price = safe_float(signal.signal_price)
        if str(phase6["entry"].get("order_type", "market")).lower() == "limit_gtx":
            offset_bps = safe_float(phase6["entry"].get("limit_offset_bps", 2.0), 2.0)
            if signal_side == "long":
                intended_price = intended_price * (1.0 - offset_bps / 10000.0)
            else:
                intended_price = intended_price * (1.0 + offset_bps / 10000.0)

        intention = build_entry_intention(
            signal,
            intention_id=intention_id,
            trace_id=trace_id,
            qty=quantity,
            target_price=float(intended_price),
            ttl_minutes=int(phase6["entry"].get("ttl_minutes", 15)),
            fallback_to_taker=bool(phase6["entry"].get("fallback_to_market_on_ttl", True)),
            config_version=current_config_version,
        )
        intentions_out.append(intention.to_dict())
        append_event(
            event_bus,
            events_written,
            EventRecord(
                timestamp=run_ctx.now_iso,
                event_type=EventType.INTENTION_CREATED,
                symbol=symbol,
                side=signal_side,
                trace_id=trace_id,
                message="phase6 entry intention created",
                payload=intention.to_dict(),
            ),
        )

        target_leverage = max(1, int(safe_float(phase6.get("default_leverage", 1), 1)))
        leverage_guard = ensure_binance_leverage(
            bridge,
            symbol=symbol,
            signal_side=signal_side,
            target_leverage=target_leverage,
        )
        append_event(
            event_bus,
            events_written,
            EventRecord(
                timestamp=run_ctx.now_iso,
                event_type=EventType.ORDER_STATUS_SYNC,
                symbol=symbol,
                side=signal_side,
                trace_id=trace_id,
                message="phase6 leverage enforced before entry",
                payload=leverage_guard,
            ),
        )

        order_side = signal_to_order_side(signal_side)
        client_order_id = make_client_order_id("en", symbol, run_ctx, trace_id)
        order_type = str(phase6["entry"].get("order_type", "market")).lower()

        if order_type == "limit_gtx":
            entry_order = bridge.place_binance_perp_live_limit_gtx_order(
                symbol=symbol,
                side=order_side,
                quantity=quantity,
                price=intended_price,
                reduce_only=None,
                position_side=hedge_position_side(signal_side),
                client_order_id=client_order_id,
                time_in_force=str(phase6["entry"].get("time_in_force", "GTX")),
            )
            entry_n = normalize_order_payload(entry_order, source="entry_limit")
            append_event(
                event_bus,
                events_written,
                EventRecord(
                    timestamp=run_ctx.now_iso,
                    event_type=EventType.ORDER_PLACED,
                    symbol=symbol,
                    side=signal_side,
                    trace_id=trace_id,
                    message="phase6 placed limit entry order",
                    payload=entry_n,
                ),
            )
            limit_entry_row = {
                "timestamp": run_ctx.now_iso,
                "symbol": symbol,
                "symbol_bucket": signal.metadata.get("symbol_bucket"),
                "side": order_side,
                "order_role": "entry",
                "order_type": "LIMIT",
                "price": entry_n.get("price"),
                "qty": entry_n.get("orig_qty"),
                "status": entry_n.get("status"),
                "exchange_order_id": entry_n.get("order_id"),
                "client_order_id": entry_n.get("client_order_id"),
            }
            orders_out.append(limit_entry_row)
            emitted_orders.append(limit_entry_row)
            state.pending_entries.append(
                {
                    "trace_id": trace_id,
                    "signal_id": signal.signal_id,
                    "signal_timestamp": signal.timestamp,
                    "symbol_bucket": signal.metadata.get("symbol_bucket"),
                    "signal_confirmed_at": signal_confirmed_at(signal.timestamp, getattr(signal, "metadata", None)),
                    "intention_id": intention_id,
                    "symbol": symbol,
                    "side": signal_side,
                    "code_version": current_code_version,
                    "config_version": current_config_version,
                    "entry_order_id": entry_n.get("order_id"),
                    "entry_client_order_id": entry_n.get("client_order_id") or client_order_id,
                    "planned_qty": quantity,
                    "planned_notional": target_notional,
                    "signal_price": signal.signal_price,
                    "atr14": signal.metadata.get("atr14"),
                    "tp_atr_mult": phase6["exit"].get("tp_atr_mult", 1.0),
                    "entry_submit_at": run_ctx.now_iso,
                    "entry_expires_at": (run_ctx.now_dt + timedelta_minutes(int(phase6["entry"].get("ttl_minutes", 15)))).strftime("%Y-%m-%dT%H:%M:%SZ"),
                }
            )
        else:
            entry_order = bridge.place_binance_perp_live_market_order(
                symbol=symbol,
                side=order_side,
                quantity=quantity,
                reduce_only=None,
                position_side=hedge_position_side(signal_side),
                client_order_id=client_order_id,
            )
            entry_n = normalize_order_payload(entry_order, source="entry_market")
            filled_qty = safe_float(entry_n.get("executed_qty"), quantity)
            entry_price = safe_float(entry_n.get("avg_price"), safe_float(entry_n.get("price"), signal.signal_price))

            try:
                exit_plan = attach_exit_plan(
                    bridge,
                    phase6=phase6,
                    symbol=symbol,
                    side=signal_side,
                    signal_price=signal.signal_price,
                    entry_price=entry_price,
                    executed_qty=filled_qty,
                    atr14=safe_float(signal.metadata.get("atr14"), math.nan),
                    run_ctx=run_ctx,
                    trace_id=trace_id,
                    signal_id=signal.signal_id,
                    signal_timestamp=signal.timestamp,
                    signal_confirmed_at_override=signal_confirmed_at(signal.timestamp, getattr(signal, "metadata", None)),
                    intention_id=intention_id,
                    entry_order_id=entry_n.get("order_id"),
                    entry_client_order_id=entry_n.get("client_order_id") or client_order_id,
                    code_version=current_code_version,
                    config_version=current_config_version,
                )
            except Exception as exc:  # noqa: BLE001
                append_warning(
                    warnings_out,
                    trace_id=trace_id,
                    symbol=symbol,
                    message="exit attach failed after market entry; emergency flatten triggered",
                    payload={"error": str(exc), "entry_order_id": entry_n.get("order_id")},
                )
                emergency_cid = make_client_order_id("ec", symbol, run_ctx, trace_id)
                emergency_close = bridge.place_binance_perp_live_market_order(
                    symbol=symbol,
                    side=exit_order_side(signal_side),
                    quantity=filled_qty,
                    reduce_only=None,
                    position_side=hedge_position_side(signal_side),
                    client_order_id=emergency_cid,
                )
                emergency_n = normalize_order_payload(emergency_close, source="emergency_flatten")
                exit_price = safe_float(emergency_n.get("avg_price"), safe_float(emergency_n.get("price"), entry_price))
                gross_pnl = (exit_price - entry_price) * filled_qty if signal_side == "long" else (entry_price - exit_price) * filled_qty
                fee_usdt, net_pnl, net_return_bps = estimate_fee_and_net(entry_price=entry_price, exit_price=exit_price, qty=filled_qty, gross_pnl=gross_pnl)
                close_row = {
                    "trace_id": trace_id,
                    "signal_id": signal.signal_id,
                    "signal_timestamp": signal.timestamp,
                    "signal_price": signal.signal_price,
                    "signal_confirmed_at": signal_confirmed_at(signal.timestamp, getattr(signal, "metadata", None)),
                    "symbol": symbol,
                    "side": signal_side,
                    "code_version": current_code_version,
                    "config_version": current_config_version,
                    "entry_time": run_ctx.now_iso,
                    "entry_price": entry_price,
                    "exit_time": run_ctx.now_iso,
                    "exit_price": exit_price,
                    "qty": filled_qty,
                    "holding_minutes": 0.0,
                    "exit_reason": "exit_attach_failed_market_close",
                    "gross_pnl": gross_pnl,
                    "fee": fee_usdt,
                    "fee_is_estimated": True,
                    "fee_bps_round_trip": ESTIMATED_FEE_BPS_ROUND_TRIP,
                    "net_pnl": net_pnl,
                    "net_return_bps": net_return_bps,
                    "entry_order_id": entry_n.get("order_id"),
                    "tp_order_id": None,
                    "sl_order_id": None,
                    "timeout_exit_order_id": emergency_n.get("order_id"),
                }
                state.closed_trades.append(close_row)
                closed_out.append(close_row)
                emergency_order_rows = [
                    {
                        "timestamp": run_ctx.now_iso,
                        "symbol": symbol,
                        "side": order_side,
                        "order_role": "entry",
                        "order_type": "MARKET",
                        "price": entry_n.get("avg_price") or entry_n.get("price"),
                        "qty": entry_n.get("executed_qty") or entry_n.get("orig_qty"),
                        "status": entry_n.get("status"),
                        "exchange_order_id": entry_n.get("order_id"),
                        "client_order_id": entry_n.get("client_order_id"),
                    },
                    {
                        "timestamp": run_ctx.now_iso,
                        "symbol": symbol,
                        "side": exit_order_side(signal_side),
                        "order_role": "emergency_flatten",
                        "order_type": "MARKET",
                        "price": emergency_n.get("avg_price") or emergency_n.get("price"),
                        "qty": emergency_n.get("executed_qty") or emergency_n.get("orig_qty"),
                        "status": emergency_n.get("status"),
                        "exchange_order_id": emergency_n.get("order_id"),
                        "client_order_id": emergency_n.get("client_order_id"),
                    },
                ]
                orders_out.extend(emergency_order_rows)
                emitted_orders.extend(emergency_order_rows)
                append_event(
                    event_bus,
                    events_written,
                    EventRecord(
                        timestamp=run_ctx.now_iso,
                        event_type=EventType.POSITION_CLOSED,
                        symbol=symbol,
                        side=signal_side,
                        trace_id=trace_id,
                        message="phase6 exit attach failed; emergency market flatten executed",
                        payload={"entry": entry_n, "emergency_close": emergency_n, "error": str(exc)},
                        level="WARN",
                    ),
                )
                state.daily_trade_count += 1
                state.seen_signal_ids.append(signal.signal_id)
                save_state_checkpoint(state, symbols=list(cfg["universe"]["symbols"]), now_iso=run_ctx.now_iso)
                continue

            state.live_positions.append(exit_plan["live_row"])
            for warn in exit_plan.get("warnings", []):
                append_warning(
                    warnings_out,
                    trace_id=str(warn.get("trace_id") or trace_id),
                    symbol=str(warn.get("symbol") or symbol),
                    message=str(warn.get("message") or "exit_plan_warning"),
                    payload=warn.get("payload"),
                )
            append_event(
                event_bus,
                events_written,
                EventRecord(
                    timestamp=run_ctx.now_iso,
                    event_type=EventType.POSITION_OPENED,
                    symbol=symbol,
                    side=signal_side,
                    trace_id=trace_id,
                    message="phase6 market entry filled and exit plan placed",
                    payload={
                        "entry": entry_n,
                        "tp": exit_plan["tp_order"],
                        "sl": exit_plan["sl_order"],
                        "sl_soft_fallback_active": bool(exit_plan["live_row"].get("sl_soft_fallback_active")),
                    },
                ),
            )

            new_order_rows = [
                {
                    "timestamp": run_ctx.now_iso,
                    "symbol": symbol,
                    "side": order_side,
                    "order_role": "entry",
                    "order_type": "MARKET",
                    "price": entry_n.get("avg_price") or entry_n.get("price"),
                    "qty": entry_n.get("executed_qty") or entry_n.get("orig_qty"),
                    "status": entry_n.get("status"),
                    "exchange_order_id": entry_n.get("order_id"),
                    "client_order_id": entry_n.get("client_order_id"),
                }
            ]
            orders_out.extend(new_order_rows)
            emitted_orders.extend(new_order_rows)
            orders_out.extend(exit_plan["order_rows"])
            emitted_orders.extend(exit_plan["order_rows"])

        state.daily_trade_count += 1
        state.seen_signal_ids.append(signal.signal_id)
        save_state_checkpoint(state, symbols=list(cfg["universe"]["symbols"]), now_iso=run_ctx.now_iso)

    state.enabled_symbols = list(cfg["universe"]["symbols"])
    state.refresh_symbol_state(list(cfg["universe"]["symbols"]), run_ctx.now_iso)
    state.closed_trades = state.closed_trades[-400:]
    state.last_run_utc = run_ctx.now_iso
    JsonStateStore(STATE_PATH).save(state.to_dict())

    recent_positions = state.live_positions[-80:]
    recent_closed = state.closed_trades[-120:]
    existing_recent_positions = load_json(POSITIONS_PATH, [])
    if not isinstance(existing_recent_positions, list):
        existing_recent_positions = []
    recent_positions_history = merge_recent_rows(
        existing_recent_positions,
        recent_positions + recent_closed,
        tail=120,
        key_fields=["trace_id", "signal_id", "entry_time"],
    )
    warning_summary = summarize_warning_buckets(warnings_out)
    if warning_summary["total"] == 0:
        system_health = "ok"
    elif warning_summary["canary"] == 0:
        system_health = "warn_external_account"
    else:
        system_health = "degraded"

    status_notes = [
        "Phase 6 = auto runner (signal -> risk -> entry -> exit plan -> state sync).",
        "Default entry mode is market for deterministic one-shot admission/fill in canary scale.",
        "Exit prefers protective stop-market + reduce-only TP limit + timeout market close; if exchange-side SL attach fails, it degrades to local soft-stop polling.",
    ]
    if exit_attach_failure_pause:
        status_notes.append(
            "Safety pause active for new entries after recent exit-attach failure: "
            f"{exit_attach_failure_pause.get('symbol')} @ {exit_attach_failure_pause.get('last_failure_time')} "
            f"(cooldown until {exit_attach_failure_pause.get('cooldown_until')})."
        )

    status = StrategyStatusSnapshot(
        alpha_name="rank32b_slope_floor_continuation",
        version="phase6_live_auto_v1",
        mode=str(phase6.get("mode", "live_canary")),
        enabled_symbols=list(cfg["universe"]["symbols"]),
        current_config_hash=current_config_version,
        last_signal_time=snapshot.latest_observed_signal_utc,
        system_health=system_health,
        last_run_utc=run_ctx.now_iso,
        trade_enabled=bool(cfg["risk"]["trade_enabled"]),
        kill_switch=bool(cfg["risk"]["kill_switch"]),
        recent_signal_count=len(recent_signals),
        recent_intention_count=len(intentions_out),
        recent_reject_count=len(rejections_out),
        latest_evaluated_bar_time=snapshot.latest_bar_utc,
        notes=status_notes,
    )

    run_finished_at = utc_now_iso()
    operator_packet = {
        "candidate_id": "rank32b_canary",
        "phase": 6,
        "mode": phase6.get("mode", "live_canary"),
        "entry_order_type": phase6["entry"].get("order_type", "market"),
        "default_leverage": max(1, int(safe_float(phase6.get("default_leverage", 1), 1))),
        "desired_notional_usdt": safe_float(phase6.get("sizing", {}).get("desired_notional_usdt", 8.0), 8.0),
        "desired_notional_usdt_by_symbol": {
            str(k).upper(): safe_float(v)
            for k, v in (phase6.get("sizing", {}).get("desired_notional_usdt_by_symbol", {}) or {}).items()
            if math.isfinite(safe_float(v)) and safe_float(v) > 0
        },
        "tp_atr_mult": safe_float(phase6["exit"].get("tp_atr_mult", 1.0), 1.0),
        "sl_atr_mult": safe_float(phase6["exit"].get("sl_atr_mult", 1.0), 1.0),
        "timeout_minutes": int(phase6["exit"].get("timeout_minutes", 240)),
        "signals_in_window": len(recent_signals),
        "latest_evaluated_bar_time": snapshot.latest_bar_utc,
        "latest_observed_signal_time": snapshot.latest_observed_signal_utc,
        "latest_actionable_signal_time": snapshot.latest_signal_utc,
        "selection_mode": str(phase6.get("selection", {}).get("mode", "all_signals")),
        "selection_strength_metric": str(phase6.get("selection", {}).get("strength_metric", "slope_strength")),
        "skipped_weaker_signals": len(skipped_weaker_signals),
        "new_signals_processed": len(new_signals),
        "intentions_created": len(intentions_out),
        "orders_emitted": len(emitted_orders),
        "risk_rejections": len(rejections_out),
        "pending_entries": len(state.pending_entries),
        "live_positions": len(state.live_positions),
        "closed_trades_new": len(closed_out),
        "closed_trades_total": len(state.closed_trades),
        "warnings": warning_summary["total"],
        "canary_warnings": warning_summary["canary"],
        "external_account_warnings": warning_summary["external_account"],
        "managed_pending_entries": managed_pending,
        "managed_live_positions": managed_live,
        "moved_to_live_from_pending": moved_to_live,
        "closed_positions_this_run": closed_count,
        "exchange_open_positions": exchange_sanity["exchange_open_positions"],
        "unexpected_exchange_positions": exchange_sanity["unexpected_exchange_positions"],
        "entry_safety_pause": exit_attach_failure_pause,
        "generated_at_utc": run_finished_at,
    }

    save_json(STATUS_PATH, status.to_dict())
    save_json(
        RUN_SUMMARY_PATH,
        {
            "generated_at_utc": run_finished_at,
            "run_started_at": run_ctx.now_iso,
            "run_finished_at": run_finished_at,
            "mode": phase6.get("mode", "live_canary"),
            "desired_notional_usdt": safe_float(phase6.get("sizing", {}).get("desired_notional_usdt", 8.0), 8.0),
            "desired_notional_usdt_by_symbol": {
                str(k).upper(): safe_float(v)
                for k, v in (phase6.get("sizing", {}).get("desired_notional_usdt_by_symbol", {}) or {}).items()
                if math.isfinite(safe_float(v)) and safe_float(v) > 0
            },
            "signals_seen_this_window": len(recent_signals),
            "latest_evaluated_bar_time": snapshot.latest_bar_utc,
            "latest_observed_signal_time": snapshot.latest_observed_signal_utc,
            "latest_actionable_signal_time": snapshot.latest_signal_utc,
            "selection_mode": str(phase6.get("selection", {}).get("mode", "all_signals")),
            "selection_strength_metric": str(phase6.get("selection", {}).get("strength_metric", "slope_strength")),
            "skipped_weaker_signals": len(skipped_weaker_signals),
            "new_signals_processed": len(new_signals),
            "intentions_created": len(intentions_out),
            "orders_emitted": len(emitted_orders),
            "risk_rejections": len(rejections_out),
            "pending_entries": len(state.pending_entries),
            "live_positions": len(state.live_positions),
            "closed_trades_new": len(closed_out),
            "closed_trades_total": len(state.closed_trades),
            "warnings": warning_summary["total"],
            "canary_warnings": warning_summary["canary"],
            "external_account_warnings": warning_summary["external_account"],
            "managed_pending_entries": managed_pending,
            "managed_live_positions": managed_live,
            "moved_to_live_from_pending": moved_to_live,
            "closed_positions_this_run": closed_count,
            "exchange_open_positions": exchange_sanity["exchange_open_positions"],
            "unexpected_exchange_positions": exchange_sanity["unexpected_exchange_positions"],
            "entry_safety_pause": exit_attach_failure_pause,
        },
    )
    append_recent_json(SIGNALS_PATH, recent_signals, tail=180, key_fields=["signal_id", "timestamp"])
    save_json(INTENTIONS_PATH, intentions_out[-120:])
    append_recent_json(
        ORDERS_PATH,
        orders_out,
        tail=240,
        key_fields=["exchange_order_id", "client_order_id", "order_role", "timestamp"],
    )
    append_recent_json(
        REJECTIONS_PATH,
        rejections_out,
        tail=180,
        key_fields=["signal_id", "reason", "timestamp"],
    )
    save_json(POSITIONS_PATH, recent_positions_history)
    save_json(CLOSED_TRADES_PATH, recent_closed)
    append_recent_json(WARNINGS_PATH, warnings_out, tail=200, key_fields=["trace_id", "message", "timestamp"])
    save_json(SYMBOL_STATE_PATH, state.symbol_states)
    save_json(OPERATOR_PACKET_PATH, operator_packet)

    print(
        {
            "generated_at_utc": run_ctx.now_iso,
            "signals_seen_this_window": len(recent_signals),
            "latest_evaluated_bar_time": snapshot.latest_bar_utc,
            "latest_observed_signal_time": snapshot.latest_observed_signal_utc,
            "latest_actionable_signal_time": snapshot.latest_signal_utc,
            "selection_mode": str(phase6.get("selection", {}).get("mode", "all_signals")),
            "selection_strength_metric": str(phase6.get("selection", {}).get("strength_metric", "slope_strength")),
            "skipped_weaker_signals": len(skipped_weaker_signals),
            "new_signals_processed": len(new_signals),
            "intentions_created": len(intentions_out),
            "orders_emitted": len(emitted_orders),
            "risk_rejections": len(rejections_out),
            "pending_entries": len(state.pending_entries),
            "live_positions": len(state.live_positions),
            "closed_trades_new": len(closed_out),
            "warnings": warning_summary["total"],
            "canary_warnings": warning_summary["canary"],
            "external_account_warnings": warning_summary["external_account"],
            "exchange_open_positions": exchange_sanity["exchange_open_positions"],
            "unexpected_exchange_positions": exchange_sanity["unexpected_exchange_positions"],
            "entry_safety_pause": exit_attach_failure_pause,
        }
    )


if __name__ == "__main__":
    main()
