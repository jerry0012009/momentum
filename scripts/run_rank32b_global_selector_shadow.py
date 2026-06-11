#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import math
import sys
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.domain.canary32b_models import StrategyStatusSnapshot  # noqa: E402
from momentum.execution.canary32b.signal_adapter import Rank32BPerpSignalAdapter  # noqa: E402

ART_DIR = ROOT / "reports" / "artifacts" / "rank32b_shadow_global_winner"
STATUS_PATH = ART_DIR / "shadow_status.json"
RUN_SUMMARY_PATH = ART_DIR / "shadow_last_run_summary.json"
SIGNALS_PATH = ART_DIR / "shadow_recent_signals.json"
SELECTED_PATH = ART_DIR / "shadow_selected_signals.json"
SKIPPED_PATH = ART_DIR / "shadow_skipped_signals.json"
STATE_PATH = ART_DIR / "shadow_state.json"
PAPER_SUMMARY_PATH = ART_DIR / "paper_summary.json"
PAPER_TRADES_PATH = ART_DIR / "paper_trades.json"
PAPER_CLOSED_PATH = ART_DIR / "paper_closed_trades.json"
PAPER_OPEN_PATH = ART_DIR / "paper_open_positions.json"
PAPER_SKIPPED_PATH = ART_DIR / "paper_skipped_signals.json"
CONFIG_PATH = ROOT / "config" / "execution" / "rank32b_canary.yaml"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


phase6lib = load_module(ROOT / "scripts" / "run_rank32b_canary_phase6.py", "rank32b_phase6_global_shadow_lib")
exec_mod = load_module(ROOT / "scripts" / "build_rank32b_execution_probe.py", "rank32b_exec_mod_global_shadow")
depth_v2_mod = load_module(ROOT / "scripts" / "rank32b_depth_v2_paper.py", "rank32b_depth_v2_global_shadow")


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_shadow_cfg(cfg: dict[str, Any]) -> dict[str, Any]:
    phase6 = cfg.get("phase6", {}) if isinstance(cfg.get("phase6"), dict) else {}
    shadow_cfg = phase6.get("shadow_global", {}) if isinstance(phase6.get("shadow_global"), dict) else {}
    asset_to_symbol = shadow_cfg.get("asset_to_symbol") if isinstance(shadow_cfg.get("asset_to_symbol"), dict) else {}
    selection_cfg = shadow_cfg.get("selection") if isinstance(shadow_cfg.get("selection"), dict) else {}
    paper_cfg = shadow_cfg.get("paper") if isinstance(shadow_cfg.get("paper"), dict) else {}
    safety_cfg = phase6.get("safety", {}) if isinstance(phase6.get("safety"), dict) else {}
    live_parity_cfg = paper_cfg.get("live_parity") if isinstance(paper_cfg.get("live_parity"), dict) else {}
    return {
        "enabled": bool(shadow_cfg.get("enabled", True)),
        "name": str(shadow_cfg.get("name", "Global strongest-only shadow")),
        "bucket": str(shadow_cfg.get("bucket", "all26") or "all26"),
        "asset_to_symbol": {str(asset): str(symbol).upper() for asset, symbol in asset_to_symbol.items()},
        "recent_hours": int(shadow_cfg.get("recent_hours", 240)),
        "tail_signals": int(shadow_cfg.get("tail_signals", 1000)),
        "selection": {
            "strongest_only_per_bar": bool(selection_cfg.get("strongest_only_per_bar", True)),
            "strength_metric": str(selection_cfg.get("strength_metric", "slope_strength") or "slope_strength"),
        },
        "paper": {
            "enabled": bool(paper_cfg.get("enabled", True)),
            "entry_style": str(paper_cfg.get("entry_style", "taker") or "taker"),
            "entry_ttl_5m_bars": int(paper_cfg.get("entry_ttl_5m_bars", exec_mod.ENTRY_TTL_5M_BARS)),
            "market_cost_bps": float(paper_cfg.get("market_cost_bps", exec_mod.TAKER_FEE_BPS)),
            "tp_atr_mult": float(paper_cfg.get("tp_atr_mult", 1.25)),
            "sl_atr_mult": float(paper_cfg.get("sl_atr_mult", 1.0)),
            "timeout_15m": int(paper_cfg.get("timeout_15m", 8)),
            "max_concurrent_positions": int(paper_cfg.get("max_concurrent_positions", 1)),
            "fallback_tp_bps": float(paper_cfg.get("fallback_tp_bps", 40.0)),
            "fallback_sl_bps": float(paper_cfg.get("fallback_sl_bps", 40.0)),
            "depth_v2": {
                "enabled": bool((paper_cfg.get("depth_v2") or {}).get("enabled", False)) if isinstance(paper_cfg.get("depth_v2"), dict) else False,
                "order_notional_usdt": float((paper_cfg.get("depth_v2") or {}).get("order_notional_usdt", 500.0)) if isinstance(paper_cfg.get("depth_v2"), dict) else 500.0,
                "order_notional_usdt_by_symbol": ({str(k).upper(): float(v) for k, v in ((paper_cfg.get("depth_v2") or {}).get("order_notional_usdt_by_symbol", {}) or {}).items()} if isinstance(paper_cfg.get("depth_v2"), dict) and isinstance((paper_cfg.get("depth_v2") or {}).get("order_notional_usdt_by_symbol"), dict) else {}),
                "depth_limit": int((paper_cfg.get("depth_v2") or {}).get("depth_limit", 20)) if isinstance(paper_cfg.get("depth_v2"), dict) else 20,
                "reject_if_insufficient_depth": bool((paper_cfg.get("depth_v2") or {}).get("reject_if_insufficient_depth", True)) if isinstance(paper_cfg.get("depth_v2"), dict) else True,
                "min_depth_fill_ratio": float((paper_cfg.get("depth_v2") or {}).get("min_depth_fill_ratio", 0.98)) if isinstance(paper_cfg.get("depth_v2"), dict) else 0.98,
                "entry_fee_bps": float((paper_cfg.get("depth_v2") or {}).get("entry_fee_bps", paper_cfg.get("market_cost_bps", exec_mod.TAKER_FEE_BPS))) if isinstance(paper_cfg.get("depth_v2"), dict) else float(paper_cfg.get("market_cost_bps", exec_mod.TAKER_FEE_BPS)),
                "exit_fee_bps": float((paper_cfg.get("depth_v2") or {}).get("exit_fee_bps", paper_cfg.get("market_cost_bps", exec_mod.TAKER_FEE_BPS))) if isinstance(paper_cfg.get("depth_v2"), dict) else float(paper_cfg.get("market_cost_bps", exec_mod.TAKER_FEE_BPS)),
            },
            "live_parity": {
                "enabled": bool(live_parity_cfg.get("enabled", True)),
                "scheduler_interval_minutes": int(live_parity_cfg.get("scheduler_interval_minutes", 1)),
                "same_bar_once": bool(live_parity_cfg.get("same_bar_once", True)),
                "same_bar_minutes": int(live_parity_cfg.get("same_bar_minutes", 15)),
                "same_symbol_single_position": bool(live_parity_cfg.get("same_symbol_single_position", True)),
                "ignore_cross_lane": bool(live_parity_cfg.get("ignore_cross_lane", True)),
                "enforce_signal_freshness": bool(live_parity_cfg.get("enforce_signal_freshness", True)),
                "max_signal_age_minutes": int(live_parity_cfg.get("max_signal_age_minutes", safety_cfg.get("max_signal_age_minutes", 30))),
                "exit_check_interval_minutes": int(live_parity_cfg.get("exit_check_interval_minutes", 1)),
                "monitor_from_next_minute_bar": bool(live_parity_cfg.get("monitor_from_next_minute_bar", True)),
                "kline_1m_cache": {
                    "cooldown_seconds": int(((live_parity_cfg.get("kline_1m_cache") or {}) if isinstance(live_parity_cfg.get("kline_1m_cache"), dict) else {}).get("cooldown_seconds", 120)),
                    "max_staleness_minutes": int(((live_parity_cfg.get("kline_1m_cache") or {}) if isinstance(live_parity_cfg.get("kline_1m_cache"), dict) else {}).get("max_staleness_minutes", 2)),
                    "tail_overlap_minutes": int(((live_parity_cfg.get("kline_1m_cache") or {}) if isinstance(live_parity_cfg.get("kline_1m_cache"), dict) else {}).get("tail_overlap_minutes", 3)),
                    "request_pause_seconds": float(((live_parity_cfg.get("kline_1m_cache") or {}) if isinstance(live_parity_cfg.get("kline_1m_cache"), dict) else {}).get("request_pause_seconds", 0.2)),
                    "http_retries": int(((live_parity_cfg.get("kline_1m_cache") or {}) if isinstance(live_parity_cfg.get("kline_1m_cache"), dict) else {}).get("http_retries", 5)),
                    "http_timeout_seconds": int(((live_parity_cfg.get("kline_1m_cache") or {}) if isinstance(live_parity_cfg.get("kline_1m_cache"), dict) else {}).get("http_timeout_seconds", 20)),
                },
            },
        },
    }


def load_state() -> dict[str, Any]:
    raw = phase6lib.load_json(STATE_PATH, {})
    if not isinstance(raw, dict):
        raw = {}
    return {
        "seen_signal_ids": list(raw.get("seen_signal_ids", [])),
        "consumed_bar_keys": list(raw.get("consumed_bar_keys", [])),
        "last_run_utc": raw.get("last_run_utc"),
    }


def save_state(state: dict[str, Any], *, now_iso: str) -> None:
    payload = {
        "seen_signal_ids": list(state.get("seen_signal_ids", []))[-5000:],
        "consumed_bar_keys": list(state.get("consumed_bar_keys", []))[-5000:],
        "last_run_utc": now_iso,
    }
    phase6lib.save_json(STATE_PATH, payload)


def summarize_recent_signals(rows: list[dict[str, Any]]) -> dict[str, Any]:
    preview = 0
    official = 0
    latest_signal_time = None
    latest_symbol = None
    for row in rows:
        mode = str(((row.get("metadata") if isinstance(row.get("metadata"), dict) else {}) or {}).get("signal_mode") or row.get("signal_mode") or "")
        if mode == "preview_unclosed15m":
            preview += 1
        elif mode == "official_close":
            official += 1
        ts = row.get("timestamp")
        if ts and (latest_signal_time is None or str(ts) > str(latest_signal_time)):
            latest_signal_time = ts
            latest_symbol = row.get("symbol")
    return {
        "preview_signals": preview,
        "official_signals": official,
        "total_signals": len(rows),
        "latest_signal_time": latest_signal_time,
        "latest_signal_symbol": latest_symbol,
    }


def enrich_signal(signal: Any, *, cfg: dict[str, Any], shadow_cfg: dict[str, Any], selected_ids: set[str], skipped_by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    signal_dict = signal.to_dict()
    metadata = signal_dict.get("metadata") if isinstance(signal_dict.get("metadata"), dict) else {}
    symbol = str(signal_dict.get("symbol") or "").upper()
    trace_id = phase6lib.make_trace_id(str(signal_dict.get("signal_id") or f"shadow-global-{symbol}"))
    phase6 = cfg.get("phase6", {}) if isinstance(cfg.get("phase6"), dict) else {}
    live_universe_symbols = [str(s).upper() for s in cfg.get("universe", {}).get("symbols", [])]
    live_bucket = phase6lib.phase6_symbol_bucket(symbol, phase6)
    bar_key = phase6lib.signal_bar_key(symbol, str(signal_dict.get("timestamp") or ""))
    confirmed_at = phase6lib.signal_confirmed_at(str(signal_dict.get("timestamp") or ""), metadata)
    skipped = skipped_by_id.get(str(signal_dict.get("signal_id") or ""), {})
    return {
        **signal_dict,
        "trace_id": trace_id,
        "bar_key": bar_key,
        "signal_confirmed_at": confirmed_at,
        "shadow_name": shadow_cfg.get("name"),
        "shadow_bucket": shadow_cfg.get("bucket"),
        "shadow_live_universe_enabled": symbol in live_universe_symbols,
        "shadow_live_bucket_now": live_bucket,
        "shadow_selected": str(signal_dict.get("signal_id") or "") in selected_ids,
        "shadow_selection_reason": "selected_global_strongest" if str(signal_dict.get("signal_id") or "") in selected_ids else skipped.get("reason"),
        "shadow_selection_metric": shadow_cfg.get("selection", {}).get("strength_metric"),
        "shadow_selected_symbol": skipped.get("selected_symbol"),
        "shadow_selected_signal_id": skipped.get("selected_signal_id"),
        "shadow_selected_strength": skipped.get("selected_strength"),
        "shadow_signal_strength": skipped.get("signal_strength"),
        "config_version": phase6lib.config_hash(cfg),
        "code_version": phase6lib.code_version(),
    }


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


def get_signal_direction_sign(row: dict[str, Any]) -> int:
    return 1 if str(row.get("side") or "").lower() == "long" else -1


def get_symbol_bars(symbol: str, *, days: int, now_ts: pd.Timestamp, cache: dict[str, pd.DataFrame]) -> pd.DataFrame:
    if symbol in cache:
        return cache[symbol]
    df = exec_mod.load_or_fetch_perp_5m(symbol, days=days, refresh=False)
    last_ts = parse_ts(df["timestamp"].max()) if not df.empty else None
    if last_ts is None or last_ts < (now_ts.floor("5min") - pd.Timedelta(minutes=10)):
        df = exec_mod.load_or_fetch_perp_5m(symbol, days=days, refresh=True)
    df = df.sort_values("timestamp").reset_index(drop=True)
    cache[symbol] = df
    return df


def simulate_exit_5m_fallback(sub_df: pd.DataFrame, fill_idx: int, fill_px: float, direction_sign: int, atr_value: float | None, paper_cfg: dict[str, Any]) -> dict[str, Any]:
    timeout_5m_bars = int(max(1, int(paper_cfg.get("timeout_15m", 8)) * 3))
    last_idx = len(sub_df) - 1
    end_idx = min(last_idx, fill_idx + timeout_5m_bars - 1)
    if atr_value is not None and math.isfinite(atr_value) and atr_value > 0:
        target_px = float(fill_px + direction_sign * float(paper_cfg.get("tp_atr_mult", 1.25)) * atr_value)
        stop_px = float(fill_px - direction_sign * float(paper_cfg.get("sl_atr_mult", 1.0)) * atr_value)
        barrier_label = "atr"
    else:
        tp_bps = float(paper_cfg.get("fallback_tp_bps", 40.0)) / 10000.0
        sl_bps = float(paper_cfg.get("fallback_sl_bps", 40.0)) / 10000.0
        target_px = float(fill_px * (1.0 + direction_sign * tp_bps))
        stop_px = float(fill_px * (1.0 - direction_sign * sl_bps))
        barrier_label = "fallback_bps"

    for idx in range(fill_idx, end_idx + 1):
        bar = sub_df.iloc[idx]
        high = float(bar["high"])
        low = float(bar["low"])
        if direction_sign > 0:
            hit_tp = high >= target_px
            hit_sl = low <= stop_px
        else:
            hit_tp = low <= target_px
            hit_sl = high >= stop_px
        if hit_tp and hit_sl:
            exit_px = stop_px
            gross_ret = exec_mod.gross_return(fill_px, exit_px, direction_sign)
            net_ret = exec_mod.apply_fees(gross_ret, exec_mod.TAKER_FEE_BPS, exec_mod.TAKER_FEE_BPS)
            return {"status": "closed", "mark_status": "realized", "exit_ts": parse_ts(bar["timestamp"]), "exit_price": exit_px, "exit_reason": "conflict_stop_first", "exit_fee_bps": exec_mod.TAKER_FEE_BPS, "gross_ret": gross_ret, "net_ret": net_ret, "hold_minutes": int((idx - fill_idx + 1) * 5), "same_bar_conflict": 1, "target_hit": 0, "stop_hit": 1, "timeout_hit": 0, "barrier_type": barrier_label}
        if hit_tp:
            exit_px = target_px
            gross_ret = exec_mod.gross_return(fill_px, exit_px, direction_sign)
            net_ret = exec_mod.apply_fees(gross_ret, exec_mod.TAKER_FEE_BPS, exec_mod.MAKER_FEE_BPS)
            return {"status": "closed", "mark_status": "realized", "exit_ts": parse_ts(bar["timestamp"]), "exit_price": exit_px, "exit_reason": "target_limit", "exit_fee_bps": exec_mod.MAKER_FEE_BPS, "gross_ret": gross_ret, "net_ret": net_ret, "hold_minutes": int((idx - fill_idx + 1) * 5), "same_bar_conflict": 0, "target_hit": 1, "stop_hit": 0, "timeout_hit": 0, "barrier_type": barrier_label}
        if hit_sl:
            exit_px = stop_px
            gross_ret = exec_mod.gross_return(fill_px, exit_px, direction_sign)
            net_ret = exec_mod.apply_fees(gross_ret, exec_mod.TAKER_FEE_BPS, exec_mod.TAKER_FEE_BPS)
            return {"status": "closed", "mark_status": "realized", "exit_ts": parse_ts(bar["timestamp"]), "exit_price": exit_px, "exit_reason": "stop_loss", "exit_fee_bps": exec_mod.TAKER_FEE_BPS, "gross_ret": gross_ret, "net_ret": net_ret, "hold_minutes": int((idx - fill_idx + 1) * 5), "same_bar_conflict": 0, "target_hit": 0, "stop_hit": 1, "timeout_hit": 0, "barrier_type": barrier_label}

    if end_idx >= fill_idx + timeout_5m_bars - 1:
        bar = sub_df.iloc[end_idx]
        exit_px = float(bar["close"])
        gross_ret = exec_mod.gross_return(fill_px, exit_px, direction_sign)
        net_ret = exec_mod.apply_fees(gross_ret, exec_mod.TAKER_FEE_BPS, exec_mod.TAKER_FEE_BPS)
        return {"status": "closed", "mark_status": "realized", "exit_ts": parse_ts(bar["timestamp"]), "exit_price": exit_px, "exit_reason": "timeout_close", "exit_fee_bps": exec_mod.TAKER_FEE_BPS, "gross_ret": gross_ret, "net_ret": net_ret, "hold_minutes": int((end_idx - fill_idx + 1) * 5), "same_bar_conflict": 0, "target_hit": 0, "stop_hit": 0, "timeout_hit": 1, "barrier_type": barrier_label}

    bar = sub_df.iloc[last_idx]
    mark_px = float(bar["close"])
    gross_ret = exec_mod.gross_return(fill_px, mark_px, direction_sign)
    net_ret = exec_mod.apply_fees(gross_ret, exec_mod.TAKER_FEE_BPS, exec_mod.TAKER_FEE_BPS)
    return {"status": "open", "mark_status": "marked_to_market", "exit_ts": None, "exit_price": None, "exit_reason": None, "exit_fee_bps": exec_mod.TAKER_FEE_BPS, "gross_ret": None, "net_ret": None, "hold_minutes": int((last_idx - fill_idx + 1) * 5), "same_bar_conflict": 0, "target_hit": 0, "stop_hit": 0, "timeout_hit": 0, "barrier_type": barrier_label, "mark_ts": parse_ts(bar["timestamp"]), "mark_price": mark_px, "mark_gross_ret": gross_ret, "mark_net_ret": net_ret}


def simulate_exit(minute_df: pd.DataFrame, *, entry_ts: pd.Timestamp, fill_px: float, side: str, atr_value: float | None, paper_cfg: dict[str, Any], now_ts: pd.Timestamp) -> dict[str, Any]:
    return depth_v2_mod.simulate_exit_on_minute_bars(
        minute_df,
        entry_ts=entry_ts,
        entry_price=float(fill_px),
        position_side=side,
        atr_value=atr_value,
        paper_cfg=paper_cfg,
        now_ts=now_ts,
        entry_fee_bps=float(exec_mod.TAKER_FEE_BPS),
        exit_fee_bps=float(exec_mod.TAKER_FEE_BPS),
    )


def build_paper_trades(
    selected_rows: list[dict[str, Any]],
    shadow_cfg: dict[str, Any],
    now_ts: pd.Timestamp,
    *,
    replay_mode: str = "historical_replay",
    consumed_bar_keys: list[str] | set[str] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    paper_cfg = shadow_cfg.get("paper", {}) if isinstance(shadow_cfg.get("paper"), dict) else {}
    live_parity_cfg = depth_v2_mod.build_live_parity_cfg(paper_cfg)
    if not paper_cfg.get("enabled", True):
        return [], [], [], {"status": "disabled"}

    usable_rows = [row for row in selected_rows if get_signal_entry_ts(row) is not None]
    usable_rows.sort(key=lambda row: (get_signal_entry_ts(row), str(row.get("symbol") or "")))
    if bool(((paper_cfg.get("depth_v2") or {}).get("enabled", False)) if isinstance(paper_cfg.get("depth_v2"), dict) else False):
        existing_trades = phase6lib.load_json(PAPER_TRADES_PATH, [])
        if not isinstance(existing_trades, list):
            existing_trades = []
        trades, closed, open_positions, summary = depth_v2_mod.build_depth_v2_paper_trades(
            usable_rows,
            paper_cfg,
            now_ts,
            existing_trades,
            replay_mode=replay_mode,
            consumed_bar_keys=consumed_bar_keys,
        )
        summary.setdefault("selected_winners", len(usable_rows))
        return trades, closed, open_positions, summary
    if not usable_rows:
        return [], [], [], {
            "status": "ok",
            "selected_winners": 0,
            "paper_trades": 0,
            "paper_closed_trades": 0,
            "paper_open_positions": 0,
            "paper_skipped_by_max_concurrent": 0,
            "paper_realized_total_return": 0.0,
            "paper_marked_total_return": 0.0,
            "consumed_bar_keys": list(consumed_bar_keys or []),
        }

    oldest_ts = min(get_signal_entry_ts(row) for row in usable_rows if get_signal_entry_ts(row) is not None)
    days = max(3, int(math.ceil((now_ts - oldest_ts) / pd.Timedelta(days=1))) + 2)
    bars_cache: dict[str, pd.DataFrame] = {}
    minute_cache: dict[str, pd.DataFrame] = {}
    active_positions: list[dict[str, Any]] = []
    paper_trades: list[dict[str, Any]] = []
    skipped_signals: list[dict[str, Any]] = []
    consumed = set(str(x) for x in (consumed_bar_keys or []))

    for row in usable_rows:
        entry_ts = get_signal_entry_ts(row)
        symbol = str(row.get("symbol") or "").upper()
        side = str(row.get("side") or "").lower()
        direction_sign = get_signal_direction_sign(row)
        bar_key = str(row.get("bar_key") or depth_v2_mod.signal_bar_key(symbol, row.get("timestamp") or row.get("signal_confirmed_at"), int(live_parity_cfg.get("same_bar_minutes", 15))))
        active_positions = [pos for pos in active_positions if pos.get("active_until") and pos["active_until"] > entry_ts]
        if live_parity_cfg.get("enabled", False) and live_parity_cfg.get("same_bar_once", True) and bar_key in consumed:
            skipped_signals.append({
                "timestamp": row.get("timestamp"),
                "signal_confirmed_at": row.get("signal_confirmed_at"),
                "signal_id": row.get("signal_id"),
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
                    "signal_id": row.get("signal_id"),
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
        if live_parity_cfg.get("enabled", False) and live_parity_cfg.get("same_symbol_single_position", True) and any(str(pos.get("symbol") or "").upper() == symbol for pos in active_positions):
            skipped_signals.append({
                "timestamp": row.get("timestamp"),
                "signal_confirmed_at": row.get("signal_confirmed_at"),
                "signal_id": row.get("signal_id"),
                "symbol": symbol,
                "side": side,
                "bar_key": bar_key,
                "reason": "live_position_exists_for_symbol",
            })
            if live_parity_cfg.get("same_bar_once", True):
                consumed.add(bar_key)
            continue
        if len(active_positions) >= int(paper_cfg.get("max_concurrent_positions", 1)):
            skipped_signals.append({
                "timestamp": row.get("timestamp"),
                "signal_confirmed_at": row.get("signal_confirmed_at"),
                "signal_id": row.get("signal_id"),
                "symbol": symbol,
                "side": side,
                "bar_key": bar_key,
                "reason": "paper_rejected_by_max_concurrent",
                "paper_active_positions": len(active_positions),
                "paper_max_concurrent_positions": int(paper_cfg.get("max_concurrent_positions", 1)),
            })
            if live_parity_cfg.get("same_bar_once", True):
                consumed.add(bar_key)
            continue

        sub_df = get_symbol_bars(symbol, days=days, now_ts=now_ts, cache=bars_cache)
        ts_array = sub_df["timestamp"].to_numpy(dtype="datetime64[ns]") if not sub_df.empty else []
        entry_res = exec_mod.simulate_entry(
            sub_df,
            ts_array,
            entry_ts,
            direction_sign,
            entry_style=str(paper_cfg.get("entry_style", "taker")),
            entry_offset_bps=0.0,
            ttl_bars=int(paper_cfg.get("entry_ttl_5m_bars", exec_mod.ENTRY_TTL_5M_BARS)),
        ) if not sub_df.empty else None
        if entry_res is None:
            paper_trades.append({
                "signal_id": row.get("signal_id"),
                "symbol": symbol,
                "side": row.get("side"),
                "mode": ((row.get("metadata") if isinstance(row.get("metadata"), dict) else {}) or {}).get("signal_mode"),
                "signal_ts": row.get("timestamp"),
                "signal_confirmed_at": row.get("signal_confirmed_at"),
                "bar_key": bar_key,
                "status": "entry_pending",
                "paper_trade_state": "entry_pending",
                "paper_effective_net_ret": 0.0,
                "paper_effective_gross_ret": 0.0,
            })
            if live_parity_cfg.get("same_bar_once", True):
                consumed.add(bar_key)
            continue

        minute_df = depth_v2_mod.get_symbol_1m_bars(symbol, days=days, now_ts=now_ts, cache=minute_cache, paper_cfg=paper_cfg)
        if minute_df.empty:
            exit_res = simulate_exit_5m_fallback(sub_df, int(entry_res["fill_idx"]), float(entry_res["fill_px"]), direction_sign, get_signal_atr(row), paper_cfg)
        else:
            exit_res = simulate_exit(
                minute_df,
                entry_ts=parse_ts(entry_res.get("fill_ts")) or entry_ts,
                fill_px=float(entry_res.get("fill_px")),
                side=side,
                atr_value=get_signal_atr(row),
                paper_cfg=paper_cfg,
                now_ts=now_ts,
            )
        trade_row = {
            "signal_id": row.get("signal_id"),
            "symbol": symbol,
            "side": row.get("side"),
            "mode": ((row.get("metadata") if isinstance(row.get("metadata"), dict) else {}) or {}).get("signal_mode"),
            "signal_ts": row.get("timestamp"),
            "signal_confirmed_at": row.get("signal_confirmed_at"),
            "bar_key": bar_key,
            "entry_ts": iso(parse_ts(entry_res.get("fill_ts"))),
            "entry_price": float(entry_res.get("fill_px")),
            "entry_fee_bps": float(entry_res.get("entry_fee_bps", exec_mod.TAKER_FEE_BPS)),
            "entry_maker": int(entry_res.get("entry_maker", 0)),
            "paper_trade_state": str(exit_res.get("status") or "unknown"),
            "status": str(exit_res.get("mark_status") or exit_res.get("status") or "unknown"),
            "exit_ts": iso(exit_res.get("exit_ts")),
            "exit_price": exit_res.get("exit_price"),
            "exit_reason": exit_res.get("exit_reason"),
            "mark_ts": iso(exit_res.get("mark_ts")),
            "mark_price": exit_res.get("mark_price"),
            "gross_ret": exit_res.get("gross_ret"),
            "net_ret": exit_res.get("net_ret"),
            "mark_gross_ret": exit_res.get("mark_gross_ret"),
            "mark_net_ret": exit_res.get("mark_net_ret"),
            "paper_effective_gross_ret": exit_res.get("gross_ret") if exit_res.get("status") == "closed" else exit_res.get("mark_gross_ret", 0.0),
            "paper_effective_net_ret": exit_res.get("net_ret") if exit_res.get("status") == "closed" else exit_res.get("mark_net_ret", 0.0),
            "hold_minutes": int(exit_res.get("hold_minutes", 0)),
            "target_hit": int(exit_res.get("target_hit", 0)),
            "stop_hit": int(exit_res.get("stop_hit", 0)),
            "timeout_hit": int(exit_res.get("timeout_hit", 0)),
            "same_bar_conflict": int(exit_res.get("same_bar_conflict", 0)),
            "barrier_type": exit_res.get("barrier_type"),
            "atr14": get_signal_atr(row),
            "tp_atr_mult": float(paper_cfg.get("tp_atr_mult", 1.25)),
            "sl_atr_mult": float(paper_cfg.get("sl_atr_mult", 1.0)),
            "timeout_15m": int(paper_cfg.get("timeout_15m", 8)),
            "max_concurrent_positions": int(paper_cfg.get("max_concurrent_positions", 1)),
            "exit_monitor_interval_minutes": int(live_parity_cfg.get("exit_check_interval_minutes", 1)),
        }
        paper_trades.append(trade_row)
        trade_end_ts = parse_ts(trade_row.get("exit_ts")) or parse_ts(trade_row.get("mark_ts")) or now_ts
        active_positions.append({"symbol": symbol, "active_until": trade_end_ts})
        active_positions.sort(key=lambda pos: (pos.get("active_until") or now_ts, pos.get("symbol") or ""))
        if live_parity_cfg.get("same_bar_once", True):
            consumed.add(bar_key)

    closed_trades = [row for row in paper_trades if row.get("paper_trade_state") == "closed"]
    open_positions = [row for row in paper_trades if row.get("paper_trade_state") == "open"]
    realized_rets = [float(row.get("net_ret", 0.0)) for row in closed_trades if row.get("net_ret") is not None]
    effective_rets = [float(row.get("paper_effective_net_ret", 0.0)) for row in paper_trades if row.get("paper_effective_net_ret") is not None]

    def total_return(vals: list[float]) -> float:
        acc = 1.0
        for val in vals:
            acc *= 1.0 + float(val)
        return acc - 1.0

    summary = {
        "status": "ok",
        "assumptions": {
            "entry_style": paper_cfg.get("entry_style"),
            "entry_ttl_5m_bars": int(paper_cfg.get("entry_ttl_5m_bars", exec_mod.ENTRY_TTL_5M_BARS)),
            "market_cost_bps": float(paper_cfg.get("market_cost_bps", exec_mod.TAKER_FEE_BPS)),
            "tp_atr_mult": float(paper_cfg.get("tp_atr_mult", 1.25)),
            "sl_atr_mult": float(paper_cfg.get("sl_atr_mult", 1.0)),
            "timeout_15m": int(paper_cfg.get("timeout_15m", 8)),
            "max_concurrent_positions": int(paper_cfg.get("max_concurrent_positions", 1)),
            "live_parity": live_parity_cfg,
            "replay_mode": replay_mode,
            "exit_style": "minute_kline_barrier_monitor",
        },
        "selected_winners": len(usable_rows),
        "paper_trades": len(paper_trades),
        "paper_closed_trades": len(closed_trades),
        "paper_open_positions": len(open_positions),
        "paper_skipped_by_max_concurrent": len([row for row in skipped_signals if row.get("reason") == "paper_rejected_by_max_concurrent"]),
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
    }
    return paper_trades, closed_trades, open_positions, {**summary, "skipped_rows": skipped_signals}


def main() -> int:
    ap = argparse.ArgumentParser(description="Run rank32b global strongest-only selector shadow.")
    ap.add_argument("--config", default=str(CONFIG_PATH))
    args = ap.parse_args()

    ensure_dir(ART_DIR)
    run_ctx = phase6lib.utcnow()
    now_ts = parse_ts(run_ctx.now_iso) or pd.Timestamp.utcnow().tz_localize("UTC")
    cfg = phase6lib.load_yaml(Path(args.config))
    shadow_cfg = load_shadow_cfg(cfg)
    if not shadow_cfg.get("enabled", True):
        phase6lib.save_json(RUN_SUMMARY_PATH, {"generated_at_utc": run_ctx.now_iso, "status": "disabled", "message": "phase6.shadow_global.enabled=false"})
        return 0

    state = load_state()
    seen = set(str(x) for x in state.get("seen_signal_ids", []))
    consumed_bar_keys = set(str(x) for x in state.get("consumed_bar_keys", []))

    signal_cfg = cfg.get("signal_adapter", {}) if isinstance(cfg.get("signal_adapter"), dict) else {}
    safety_cfg = cfg.get("phase6", {}).get("safety", {}) if isinstance(cfg.get("phase6", {}).get("safety"), dict) else {}
    adapter = Rank32BPerpSignalAdapter(
        asset_to_symbol=shadow_cfg["asset_to_symbol"],
        days=int(signal_cfg.get("lookback_days", 30)),
        recent_hours=int(shadow_cfg.get("recent_hours", signal_cfg.get("recent_hours", 72))),
        variant=str(signal_cfg.get("variant", "ema_cross_plus_slope_floor")),
        refresh_bars=bool(signal_cfg.get("refresh_bars", True)),
        refresh_tail_days=(int(signal_cfg["refresh_tail_days"]) if signal_cfg.get("refresh_tail_days") is not None else None),
        preview_unclosed_15m=bool(signal_cfg.get("preview_unclosed_15m", False)),
        preview_fetch_limit=int(signal_cfg.get("preview_fetch_limit", 30)),
        entry_delay_minutes=int(signal_cfg.get("entry_delay_minutes", 0)),
        official_signal_ttl_minutes=int(safety_cfg.get("max_signal_age_minutes", 30)),
    )
    snapshot = adapter.load_recent_signals()

    selection_phase6 = {
        "selection": shadow_cfg.get("selection", {}),
        "smallcap": {"enabled": False, "symbols": []},
        "max_new_signals_per_run": 0,
    }
    selected_signals, skipped_rows = phase6lib.select_signals_for_execution(list(snapshot.signals), selection_phase6)
    selected_ids = {str(getattr(sig, "signal_id", "")) for sig in selected_signals}
    skipped_by_id = {str(row.get("signal_id") or ""): row for row in skipped_rows}

    recent_rows: list[dict[str, Any]] = []
    selected_rows: list[dict[str, Any]] = []
    skipped_enriched_rows: list[dict[str, Any]] = []
    new_rows: list[dict[str, Any]] = []
    new_selected_rows: list[dict[str, Any]] = []
    for signal in snapshot.signals:
        enriched = enrich_signal(signal, cfg=cfg, shadow_cfg=shadow_cfg, selected_ids=selected_ids, skipped_by_id=skipped_by_id)
        recent_rows.append(enriched)
        if enriched.get("shadow_selected"):
            selected_rows.append(enriched)
        if str(enriched.get("signal_id") or "") in skipped_by_id:
            skipped_enriched_rows.append({**enriched, **skipped_by_id[str(enriched.get("signal_id") or "")]})
        signal_id = str(getattr(signal, "signal_id", ""))
        if signal_id in seen:
            continue
        seen.add(signal_id)
        new_rows.append(enriched)
        if enriched.get("shadow_selected"):
            new_selected_rows.append(enriched)

    merged_signals = phase6lib.append_recent_json(SIGNALS_PATH, recent_rows, tail=int(shadow_cfg.get("tail_signals", 1000)), key_fields=["signal_id"])
    merged_selected = phase6lib.append_recent_json(SELECTED_PATH, selected_rows, tail=int(shadow_cfg.get("tail_signals", 1000)), key_fields=["signal_id"])
    merged_skipped = phase6lib.append_recent_json(SKIPPED_PATH, skipped_enriched_rows, tail=int(shadow_cfg.get("tail_signals", 1000)), key_fields=["signal_id", "reason"])

    paper_trades, paper_closed, paper_open, paper_summary = build_paper_trades(
        new_selected_rows,
        shadow_cfg,
        now_ts,
        replay_mode="stateful_live",
        consumed_bar_keys=consumed_bar_keys,
    )
    paper_summary_payload = {
        "generated_at_utc": run_ctx.now_iso,
        "shadow_name": shadow_cfg.get("name"),
        "shadow_bucket": shadow_cfg.get("bucket"),
        "code_version": phase6lib.code_version(),
        "config_version": phase6lib.config_hash(cfg),
        **{k: v for k, v in paper_summary.items() if k != "skipped_rows"},
    }
    phase6lib.save_json(PAPER_SUMMARY_PATH, paper_summary_payload)
    phase6lib.save_json(PAPER_TRADES_PATH, paper_trades)
    phase6lib.save_json(PAPER_CLOSED_PATH, paper_closed)
    phase6lib.save_json(PAPER_OPEN_PATH, paper_open)
    phase6lib.save_json(PAPER_SKIPPED_PATH, paper_summary.get("skipped_rows", []))

    summary_bits = summarize_recent_signals(merged_signals if isinstance(merged_signals, list) else [])
    run_summary = {
        "generated_at_utc": run_ctx.now_iso,
        "status": "ok",
        "shadow_name": shadow_cfg.get("name"),
        "shadow_bucket": shadow_cfg.get("bucket"),
        "shadow_symbols": shadow_cfg.get("asset_to_symbol"),
        "selection": shadow_cfg.get("selection"),
        "paper": shadow_cfg.get("paper"),
        "code_version": phase6lib.code_version(),
        "config_version": phase6lib.config_hash(cfg),
        "signal_adapter_latest_bar_utc": snapshot.latest_bar_utc,
        "signal_adapter_latest_signal_utc": snapshot.latest_signal_utc,
        "signal_adapter_latest_observed_signal_utc": snapshot.latest_observed_signal_utc,
        "snapshot_signal_count": len(snapshot.signals),
        "selected_signal_count": len(selected_rows),
        "new_signal_count": len(new_rows),
        "new_selected_signal_count": len(new_selected_rows),
        "recent_selected_signal_count": len(merged_selected if isinstance(merged_selected, list) else []),
        "recent_skipped_signal_count": len(merged_skipped if isinstance(merged_skipped, list) else []),
        **summary_bits,
        "paper_closed_trades": paper_summary_payload.get("paper_closed_trades"),
        "paper_open_positions": paper_summary_payload.get("paper_open_positions"),
        "paper_realized_total_return": paper_summary_payload.get("paper_realized_total_return"),
        "paper_marked_total_return": paper_summary_payload.get("paper_marked_total_return"),
    }
    phase6lib.save_json(RUN_SUMMARY_PATH, run_summary)

    status = StrategyStatusSnapshot(
        alpha_name="rank32b_global_selector_shadow",
        version=phase6lib.code_version(),
        mode="shadow_selector_paper",
        enabled_symbols=list(shadow_cfg.get("asset_to_symbol", {}).values()),
        current_config_hash=phase6lib.config_hash(cfg),
        last_signal_time=snapshot.latest_signal_utc,
        system_health="ok",
        last_run_utc=run_ctx.now_iso,
        trade_enabled=False,
        kill_switch=False,
        recent_signal_count=int(run_summary.get("total_signals", 0)),
        recent_intention_count=0,
        recent_reject_count=int(run_summary.get("recent_skipped_signal_count", 0)),
        notes=[
            "Global strongest-only selector shadow now includes paper PnL with ATR OCO + timeout exits.",
            "Live-parity mode enforces same-bar consume, same-symbol single-position, and signal freshness gates.",
            "Open shadow positions are monitored on 1m bars for TP/SL/timeout, closer to live than 15m-bar checks.",
            "Paper portfolio uses max_concurrent_positions from phase6.shadow_global.paper.",
        ],
        latest_evaluated_bar_time=snapshot.latest_bar_utc,
    )
    phase6lib.save_json(STATUS_PATH, status.to_dict())

    state["seen_signal_ids"] = list(seen)[-5000:]
    state["consumed_bar_keys"] = list(paper_summary.get("consumed_bar_keys", list(consumed_bar_keys)))[-5000:]
    save_state(state, now_iso=run_ctx.now_iso)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        now_iso = phase6lib.utcnow().now_iso
        ensure_dir(ART_DIR)
        cfg_hash = None
        code_version = None
        try:
            cfg = phase6lib.load_yaml(Path(CONFIG_PATH))
            cfg_hash = phase6lib.config_hash(cfg)
        except Exception:
            cfg = None
        try:
            code_version = phase6lib.code_version()
        except Exception:
            code_version = None
        phase6lib.save_json(
            RUN_SUMMARY_PATH,
            {
                "generated_at_utc": now_iso,
                "status": "error_degraded",
                "shadow_name": "Global strongest-only shadow",
                "code_version": code_version,
                "config_version": cfg_hash,
                "error": str(exc),
            },
        )
        phase6lib.save_json(
            STATUS_PATH,
            {
                "alpha_name": "rank32b_global_selector_shadow",
                "version": code_version,
                "mode": "shadow_selector_paper",
                "current_config_hash": cfg_hash,
                "system_health": "degraded",
                "last_run_utc": now_iso,
                "trade_enabled": False,
                "kill_switch": False,
                "recent_signal_count": 0,
                "recent_intention_count": 0,
                "recent_reject_count": 0,
                "notes": [f"shadow runner degraded: {exc}"],
            },
        )
        print(
            {
                "level": "ERROR",
                "component": "rank32b_global_selector_shadow",
                "message": "shadow_runner_degraded_not_failing_service",
                "error": str(exc),
            },
            flush=True,
        )
        raise SystemExit(0)
