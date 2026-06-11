#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

ART_DIR = ROOT / "reports" / "artifacts" / "rank32b_global_live"
EVENTS_PATH = ART_DIR / "live_events.jsonl"
STATE_PATH = ART_DIR / "live_state.json"
STATUS_PATH = ART_DIR / "live_status.json"
RUN_SUMMARY_PATH = ART_DIR / "live_last_run_summary.json"
SIGNALS_PATH = ART_DIR / "live_recent_signals.json"
INTENTIONS_PATH = ART_DIR / "live_recent_intentions.json"
ORDERS_PATH = ART_DIR / "live_recent_orders.json"
REJECTIONS_PATH = ART_DIR / "live_recent_rejections.json"
POSITIONS_PATH = ART_DIR / "live_recent_positions.json"
CLOSED_TRADES_PATH = ART_DIR / "live_recent_closed_trades.json"
WARNINGS_PATH = ART_DIR / "live_warnings.json"
OPERATOR_PACKET_PATH = ART_DIR / "live_operator_packet.json"
COMPARE_PATH = ART_DIR / "live_vs_shadow.csv"
COMPARE_SUMMARY_PATH = ART_DIR / "live_vs_shadow_summary.json"
COMPARE_SAMPLE_LEDGER_PATH = ART_DIR / "live_vs_shadow_high_quality_samples.csv"
CONFIG_PATH = ROOT / "config" / "execution" / "rank32b_canary.yaml"
SHADOW_PAPER_TRADES_PATH = ROOT / "reports" / "artifacts" / "rank32b_shadow_global_winner" / "paper_trades.json"
SHADOW_SELECTED_SIGNALS_PATH = ROOT / "reports" / "artifacts" / "rank32b_shadow_global_winner" / "shadow_selected_signals.json"
SHADOW_RECENT_SIGNALS_PATH = ROOT / "reports" / "artifacts" / "rank32b_shadow_global_winner" / "shadow_recent_signals.json"
SELECTED_SIGNAL_LEDGER_PATH = ART_DIR / "live_selected_signal_ledger.jsonl"
DEFAULT_CORE3_STATE_PATH = ROOT / "reports" / "artifacts" / "rank32b_canary" / "phase6_state.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


phase6lib = load_module(ROOT / "scripts" / "run_rank32b_canary_phase6.py", "rank32b_global_live_phase6lib")
shadow_mod = load_module(ROOT / "scripts" / "run_rank32b_global_selector_shadow.py", "rank32b_global_live_shadow_mod")
depth_v2_mod = load_module(ROOT / "scripts" / "rank32b_depth_v2_paper.py", "rank32b_global_live_depth_v2_mod")


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def make_client_order_id(role: str, symbol: str, run_ctx: Any, trace_id: str | None = None) -> str:
    sym = symbol.replace("USDT", "").lower()[:4]
    stamp = run_ctx.now_dt.strftime("%H%M%S%f")[:9]
    trace_tail = (trace_id or "")[-4:].lower()
    cid = f"g32b-{role}-{sym}-{stamp}"
    if trace_tail:
        cid = f"{cid}-{trace_tail}"
    return cid[:36]


phase6lib.make_client_order_id = make_client_order_id


def load_global_live_cfg(cfg: dict[str, Any]) -> dict[str, Any]:
    phase6 = cfg.get("phase6", {}) if isinstance(cfg.get("phase6"), dict) else {}
    shadow_cfg = phase6.get("shadow_global", {}) if isinstance(phase6.get("shadow_global"), dict) else {}
    live_cfg = phase6.get("global_live", {}) if isinstance(phase6.get("global_live"), dict) else {}
    asset_to_symbol = (
        live_cfg.get("asset_to_symbol")
        if isinstance(live_cfg.get("asset_to_symbol"), dict)
        else shadow_cfg.get("asset_to_symbol")
        if isinstance(shadow_cfg.get("asset_to_symbol"), dict)
        else {}
    )
    base_sizing = phase6.get("sizing", {}) if isinstance(phase6.get("sizing"), dict) else {}
    desired = float(live_cfg.get("desired_notional_usdt", base_sizing.get("desired_notional_usdt", 100.0)))
    desired_by_symbol = {str(symbol).upper(): desired for symbol in asset_to_symbol.values()}
    overrides = live_cfg.get("desired_notional_usdt_by_symbol") if isinstance(live_cfg.get("desired_notional_usdt_by_symbol"), dict) else {}
    for key, value in overrides.items():
        try:
            num = float(value)
        except Exception:
            continue
        if math.isfinite(num) and num > 0:
            desired_by_symbol[str(key).upper()] = num
    conflict_cfg = live_cfg.get("conflict", {}) if isinstance(live_cfg.get("conflict"), dict) else {}
    state_paths = conflict_cfg.get("state_paths") if isinstance(conflict_cfg.get("state_paths"), list) else None
    if not state_paths:
        state_paths = [conflict_cfg.get("core3_state_path", DEFAULT_CORE3_STATE_PATH)]
    enabled_symbols = conflict_cfg.get("enabled_symbols") if isinstance(conflict_cfg.get("enabled_symbols"), list) else None
    if not enabled_symbols:
        enabled_symbols = conflict_cfg.get("core3_enabled_symbols") or cfg.get("universe", {}).get("symbols") or []
    return {
        "enabled": bool(live_cfg.get("enabled", True)),
        "name": str(live_cfg.get("name", "global32b_live") or "global32b_live"),
        "mode": str(live_cfg.get("mode", "global_live") or "global_live"),
        "asset_to_symbol": {str(asset): str(symbol).upper() for asset, symbol in asset_to_symbol.items()},
        "selection": shadow_cfg.get("selection", {}) if isinstance(shadow_cfg.get("selection"), dict) else {"strongest_only_per_bar": True, "strength_metric": "slope_strength"},
        "desired_notional_usdt": desired,
        "desired_notional_usdt_by_symbol": desired_by_symbol,
        "max_concurrent_positions": int(live_cfg.get("max_concurrent_positions", 1)),
        "max_daily_trades": int(live_cfg.get("max_daily_trades", cfg.get("risk", {}).get("max_daily_trades", 999))),
        "max_position_notional_per_symbol": float(live_cfg.get("max_position_notional_per_symbol", cfg.get("risk", {}).get("max_position_notional_per_symbol", 300.0))),
        "max_signal_age_minutes": int(live_cfg.get("max_signal_age_minutes", phase6.get("safety", {}).get("max_signal_age_minutes", 3))),
        "entry_cadence_minutes": int(live_cfg.get("entry_cadence_minutes", 15)),
        "entry_trigger_second": int(live_cfg.get("entry_trigger_second", 5)),
        "conflict_state_paths": [str(path) for path in state_paths if path],
        "conflict_enabled_symbols": [str(s).upper() for s in enabled_symbols],
    }


def build_exec_cfg(cfg: dict[str, Any], live_cfg: dict[str, Any]) -> dict[str, Any]:
    out = json.loads(json.dumps(cfg))
    out.setdefault("phase6", {})
    out["phase6"]["selection"] = json.loads(json.dumps(live_cfg.get("selection", {})))
    out["phase6"]["smallcap"] = {"enabled": False, "symbols": []}
    out["phase6"]["mode"] = live_cfg.get("mode", "global_live")
    out["phase6"].setdefault("sizing", {})
    out["phase6"]["sizing"]["desired_notional_usdt"] = float(live_cfg["desired_notional_usdt"])
    out["phase6"]["sizing"]["desired_notional_usdt_by_symbol"] = dict(live_cfg["desired_notional_usdt_by_symbol"])
    out["phase6"]["max_new_signals_per_run"] = 0
    out["phase6"].setdefault("safety", {})
    out["phase6"]["safety"]["max_signal_age_minutes"] = int(live_cfg["max_signal_age_minutes"])
    out["universe"] = {
        "symbols": list(live_cfg["asset_to_symbol"].values()),
        "asset_to_symbol": dict(live_cfg["asset_to_symbol"]),
    }
    out.setdefault("risk", {})
    out["risk"]["max_concurrent_positions"] = int(live_cfg["max_concurrent_positions"])
    out["risk"]["max_core_positions"] = int(live_cfg["max_concurrent_positions"])
    out["risk"]["max_daily_trades"] = int(live_cfg["max_daily_trades"])
    out["risk"]["max_position_notional_per_symbol"] = float(live_cfg["max_position_notional_per_symbol"])
    return out


def save_state_local(state: Any, *, symbols: list[str], now_iso: str) -> None:
    state.refresh_symbol_state(symbols, now_iso)
    phase6lib.JsonStateStore(STATE_PATH).save(state.to_dict())


def load_signal_audit_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in (SHADOW_RECENT_SIGNALS_PATH, SHADOW_SELECTED_SIGNALS_PATH):
        selected = phase6lib.load_json(path, [])
        if isinstance(selected, list):
            rows.extend(row for row in selected if isinstance(row, dict))
    if SELECTED_SIGNAL_LEDGER_PATH.exists():
        for line in SELECTED_SIGNAL_LEDGER_PATH.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(row, dict):
                rows.append(row)
    return rows


def append_selected_signal_audit_row(
    *,
    signal: Any,
    bar_key: str,
    run_ctx: Any,
    allow_live: bool,
    code_version: str,
    config_version: str,
    risk_decision: Any,
    intended_notional_usdt: float,
) -> None:
    row = {
        **signal.to_dict(),
        "signal_confirmed_at": phase6lib.signal_confirmed_at(signal.timestamp, getattr(signal, "metadata", None)),
        "bar_key": bar_key,
        "audit_ledger": "rank32b_global_live_selected_signal_v1",
        "audit_recorded_at": run_ctx.now_iso,
        "allow_live_orders": bool(allow_live),
        "code_version": code_version,
        "config_version": config_version,
        "risk": risk_decision.to_dict() if hasattr(risk_decision, "to_dict") else risk_decision,
        "intended_notional_usdt": float(intended_notional_usdt),
    }
    SELECTED_SIGNAL_LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SELECTED_SIGNAL_LEDGER_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def load_priority_busy_symbols(live_cfg: dict[str, Any], bridge: Any, own_live_symbols: set[str]) -> tuple[set[str], list[dict[str, Any]]]:
    busy: set[str] = set()
    warnings: list[dict[str, Any]] = []

    for raw_path in live_cfg.get("conflict_state_paths") or [str(DEFAULT_CORE3_STATE_PATH)]:
        raw = phase6lib.load_json(Path(str(raw_path)), {})
        for bucket in ("pending_entries", "live_positions"):
            for row in raw.get(bucket, []) or []:
                symbol = str(row.get("symbol") or "").upper()
                if symbol:
                    busy.add(symbol)

    exchange_symbols = {str(s).upper() for s in live_cfg.get("conflict_enabled_symbols") or []}
    if not exchange_symbols:
        return busy, warnings

    try:
        positions_raw = bridge.get_binance_perp_positions()
        rows = positions_raw if isinstance(positions_raw, list) else [positions_raw]
        for row in rows:
            if not isinstance(row, dict):
                continue
            symbol = str(row.get("symbol") or "").upper()
            if symbol not in exchange_symbols:
                continue
            amt = abs(phase6lib.safe_float(row.get("positionAmt"), 0.0))
            if amt <= 0:
                continue
            if symbol in own_live_symbols:
                continue
            busy.add(symbol)
            warnings.append(
                {
                    "message": "exchange reports busy symbol on another lane",
                    "payload": {"symbol": symbol, "positionAmt": row.get("positionAmt"), "entryPrice": row.get("entryPrice")},
                }
            )
    except Exception as exc:  # noqa: BLE001
        warnings.append({"message": "failed to query exchange positions for cross-lane conflict scan", "payload": {"error": str(exc)}})

    return busy, warnings


def shadow_proxy_notional_usdt(live_cfg: dict[str, Any], symbol: str | None) -> float:
    symbol_key = str(symbol or "").upper()
    by_symbol = live_cfg.get("desired_notional_usdt_by_symbol") if isinstance(live_cfg.get("desired_notional_usdt_by_symbol"), dict) else {}
    if symbol_key in by_symbol:
        return float(by_symbol[symbol_key])
    return float(live_cfg["desired_notional_usdt"])


def evaluate_official_entry_window(now_dt: datetime, live_cfg: dict[str, Any]) -> dict[str, Any]:
    cadence_minutes = max(1, int(live_cfg.get("entry_cadence_minutes", 15)))
    trigger_second = max(0, int(live_cfg.get("entry_trigger_second", 5)))
    freshness_minutes = max(0, int(live_cfg.get("max_signal_age_minutes", 3)))
    freshness_seconds = freshness_minutes * 60
    minute_mod = int(now_dt.minute % cadence_minutes)
    second_of_minute = int(now_dt.second)
    eligible = minute_mod == 0 and trigger_second <= second_of_minute <= (trigger_second + freshness_seconds)
    return {
        "eligible": bool(eligible),
        "cadence_minutes": cadence_minutes,
        "trigger_second": trigger_second,
        "freshness_seconds": freshness_seconds,
        "minute_mod": minute_mod,
        "second_of_minute": second_of_minute,
        "window_end_second": trigger_second + freshness_seconds,
    }


def normalize_exit_bucket(reason: str | None) -> str:
    text = str(reason or "").lower()
    if any(token in text for token in ["take_profit", "target"]):
        return "tp"
    if any(token in text for token in ["stop_loss", "stop", "conflict_stop"]):
        return "sl"
    if "timeout" in text:
        return "timeout"
    return text or "unknown"


def build_live_shadow_audit_rows(live_cfg: dict[str, Any], closed_trades: list[dict[str, Any]]) -> list[dict[str, Any]]:
    import pandas as pd

    cfg = phase6lib.load_yaml(CONFIG_PATH)
    shadow_cfg = shadow_mod.load_shadow_cfg(cfg)
    paper_cfg = shadow_cfg.get("paper", {}) if isinstance(shadow_cfg.get("paper"), dict) else {}
    signal_rows = load_signal_audit_rows()
    signal_by_id = {str(row.get("signal_id") or ""): row for row in signal_rows if isinstance(row, dict) and row.get("signal_id")}
    bars_cache: dict[str, pd.DataFrame] = {}
    minute_cache: dict[str, pd.DataFrame] = {}
    results: list[dict[str, Any]] = []

    ordered_trades = sorted(
        closed_trades,
        key=lambda row: (str(row.get("exit_time") or ""), str(row.get("signal_id") or "")),
    )
    for trade in ordered_trades:
        signal_id = str(trade.get("signal_id") or "")
        symbol = str(trade.get("symbol") or "").upper()
        side = str(trade.get("side") or "").lower()
        signal_row = signal_by_id.get(signal_id, {})
        signal_entry_ts = shadow_mod.get_signal_entry_ts(signal_row) if signal_row else None
        live_exit_ts = pd.to_datetime(trade.get("exit_time"), utc=True)
        if signal_entry_ts is None:
            continue
        timeout_minutes = int(paper_cfg.get("timeout_15m", 8)) * 15
        audit_now_ts = max(live_exit_ts, signal_entry_ts + pd.Timedelta(minutes=timeout_minutes + 2))
        days = max(3, int(math.ceil(max(1.0, (audit_now_ts - signal_entry_ts).total_seconds()) / 86400.0)) + 2)
        sub_df = shadow_mod.get_symbol_bars(symbol, days=days, now_ts=audit_now_ts, cache=bars_cache)
        ts_array = sub_df["timestamp"].to_numpy(dtype="datetime64[ns]") if not sub_df.empty else []
        direction_sign = shadow_mod.get_signal_direction_sign(signal_row) if signal_row else (1 if side == "long" else -1)
        entry_res = shadow_mod.exec_mod.simulate_entry(
            sub_df,
            ts_array,
            signal_entry_ts,
            direction_sign,
            entry_style=str(paper_cfg.get("entry_style", "taker")),
            entry_offset_bps=0.0,
            ttl_bars=int(paper_cfg.get("entry_ttl_5m_bars", shadow_mod.exec_mod.ENTRY_TTL_5M_BARS)),
        ) if not sub_df.empty else None
        if entry_res is None:
            continue
        audit_entry_ts = pd.to_datetime(entry_res.get("fill_ts"), utc=True, errors="coerce")
        if pd.isna(audit_entry_ts):
            audit_entry_ts = signal_entry_ts
        audit_entry_price = float(entry_res.get("fill_px") or 0.0)
        minute_days = max(3, int(math.ceil(max(1.0, (audit_now_ts - audit_entry_ts).total_seconds()) / 86400.0)) + 1)
        minute_df = depth_v2_mod.get_symbol_1m_bars(symbol, days=minute_days, now_ts=audit_now_ts, cache=minute_cache, paper_cfg=paper_cfg)
        atr14 = shadow_mod.get_signal_atr(signal_row) if signal_row else None
        shadow_notional = shadow_proxy_notional_usdt(live_cfg, symbol)
        shadow_qty = (shadow_notional / audit_entry_price) if audit_entry_price > 0 else 0.0
        audit_res = depth_v2_mod.simulate_exit_on_minute_bars(
            minute_df,
            entry_ts=audit_entry_ts,
            entry_price=audit_entry_price,
            position_side=side,
            atr_value=atr14,
            paper_cfg=paper_cfg,
            now_ts=audit_now_ts,
            entry_fee_bps=0.0,
            exit_fee_bps=0.0,
        )
        audit_exit_ts = audit_res.get("exit_ts") if audit_res.get("status") == "closed" else audit_res.get("mark_ts")
        audit_exit_price = float(audit_res.get("exit_price") or audit_res.get("mark_price") or audit_entry_price or 0.0)
        qty = float(shadow_qty)
        direction = 1 if side == "long" else -1
        gross_pnl = (audit_exit_price - audit_entry_price) * qty if direction > 0 else (audit_entry_price - audit_exit_price) * qty
        fee_usdt, audit_net_pnl, audit_net_return_bps = phase6lib.estimate_fee_and_net(
            entry_price=audit_entry_price,
            exit_price=audit_exit_price,
            qty=qty,
            gross_pnl=gross_pnl,
        )
        live_exit_bucket = normalize_exit_bucket(str(trade.get("exit_reason") or ""))
        audit_exit_bucket = normalize_exit_bucket(str(audit_res.get("exit_reason") or audit_res.get("mark_status") or ""))
        live_notional = float(trade.get("entry_price") or 0.0) * float(trade.get("qty") or 0.0)
        exit_time_diff_seconds = None
        try:
            audit_exit_ts_pd = pd.to_datetime(audit_exit_ts, utc=True)
            exit_time_diff_seconds = float((audit_exit_ts_pd - live_exit_ts).total_seconds())
        except Exception:
            audit_exit_ts_pd = None
        live_exit_price = float(trade.get("exit_price") or 0.0)
        exit_price_diff_bps = ((audit_exit_price - live_exit_price) / live_exit_price * 10000.0) if live_exit_price > 0 else math.nan
        pnl_delta = float(trade.get("net_pnl") or 0.0) - float(audit_net_pnl)
        pnl_delta_bps = (pnl_delta / shadow_notional * 10000.0) if shadow_notional > 0 else math.nan
        reason_match = live_exit_bucket == audit_exit_bucket
        close_match = bool(reason_match and exit_time_diff_seconds is not None and abs(exit_time_diff_seconds) <= 60.0 and abs(pnl_delta) <= 0.25)
        results.append(
            {
                "signal_id": signal_id,
                "symbol": symbol,
                "side": side,
                "signal_confirmed_at": trade.get("signal_confirmed_at") or signal_row.get("signal_confirmed_at"),
                "bar_key": signal_row.get("bar_key"),
                "live_entry_time": trade.get("entry_time"),
                "live_entry_price": float(trade.get("entry_price") or 0.0),
                "live_exit_time": trade.get("exit_time"),
                "live_exit_price": live_exit_price,
                "live_exit_reason": trade.get("exit_reason"),
                "live_net_pnl_usdt": float(trade.get("net_pnl") or 0.0),
                "live_code_version": trade.get("code_version"),
                "live_config_version": trade.get("config_version"),
                "shadow_proxy_notional_usdt": shadow_notional,
                "shadow_proxy_entry_basis": "historical_reconstructed_entry",
                "shadow_proxy_entry_time": audit_entry_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "shadow_proxy_entry_price": audit_entry_price,
                "shadow_proxy_exit_time": (audit_exit_ts_pd.strftime("%Y-%m-%dT%H:%M:%SZ") if audit_exit_ts_pd is not None else None),
                "shadow_proxy_exit_price": audit_exit_price,
                "shadow_proxy_exit_reason": audit_res.get("exit_reason") or audit_res.get("mark_status"),
                "shadow_proxy_exit_bucket": audit_exit_bucket,
                "shadow_proxy_fee_usdt": fee_usdt,
                "shadow_proxy_net_return_bps": audit_net_return_bps,
                "shadow_proxy_net_pnl_usdt": audit_net_pnl,
                "delta_vs_shadow_usdt": pnl_delta,
                "delta_vs_shadow_bps": pnl_delta_bps,
                "exit_time_diff_seconds": exit_time_diff_seconds,
                "exit_price_diff_bps": exit_price_diff_bps,
                "exit_bucket_match": reason_match,
                "close_match": close_match,
                "audit_atr14": atr14,
                "audit_barrier_type": audit_res.get("barrier_type"),
            }
        )
    cum_live = 0.0
    cum_shadow = 0.0
    for row in results:
        cum_live += float(row.get("live_net_pnl_usdt") or 0.0)
        cum_shadow += float(row.get("shadow_proxy_net_pnl_usdt") or 0.0)
        row["cum_live_net_pnl_usdt"] = cum_live
        row["cum_shadow_proxy_net_pnl_usdt"] = cum_shadow
        row["cum_delta_vs_shadow_usdt"] = cum_live - cum_shadow
    return results


def write_compare_artifacts(live_cfg: dict[str, Any], closed_trades: list[dict[str, Any]]) -> None:
    if not closed_trades:
        COMPARE_PATH.write_text(
            "signal_id,symbol,side,live_entry_time,live_exit_time,live_net_pnl_usdt,shadow_proxy_notional_usdt,shadow_proxy_net_pnl_usdt,delta_vs_shadow_usdt\n",
            encoding="utf-8",
        )
        phase6lib.save_json(COMPARE_SUMMARY_PATH, {"status": "empty", "closed_trades": 0})
        return

    import pandas as pd

    merged = pd.DataFrame(build_live_shadow_audit_rows(live_cfg, closed_trades))
    merged.sort_values(["live_exit_time", "signal_id"], inplace=True)
    merged.to_csv(COMPARE_PATH, index=False)
    sample_rows = merged.copy()
    if not sample_rows.empty:
        live_entry = pd.to_datetime(sample_rows.get("live_entry_time"), utc=True, errors="coerce")
        shadow_entry = pd.to_datetime(sample_rows.get("shadow_proxy_entry_time"), utc=True, errors="coerce")
        shadow_exit = pd.to_datetime(sample_rows.get("shadow_proxy_exit_time"), utc=True, errors="coerce")
        entry_aligned = (shadow_entry - live_entry).dt.total_seconds().abs().le(300)
        minute_available = ~sample_rows.get("shadow_proxy_exit_reason", pd.Series([""] * len(sample_rows))).astype(str).str.contains("minute_bars_unavailable", case=False, na=False)
        quality_mask = live_entry.notna() & shadow_entry.notna() & shadow_exit.notna() & entry_aligned & minute_available
        new_samples = sample_rows[quality_mask].copy()
        if not new_samples.empty:
            generated_at = pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ")
            new_samples["sample_quality"] = "high_quality_1m_replay"
            new_samples["sample_recorded_at_utc"] = generated_at
            existing_samples = pd.read_csv(COMPARE_SAMPLE_LEDGER_PATH) if COMPARE_SAMPLE_LEDGER_PATH.exists() else pd.DataFrame()
            combined = pd.concat([existing_samples, new_samples], ignore_index=True)
            combined = combined.drop_duplicates(subset=["signal_id"], keep="last")
            combined.sort_values(["live_exit_time", "signal_id"], inplace=True)
            combined.to_csv(COMPARE_SAMPLE_LEDGER_PATH, index=False)
    shadow_exit_series = pd.to_datetime(merged.get("shadow_proxy_exit_time"), utc=True, errors="coerce") if "shadow_proxy_exit_time" in merged.columns else None
    phase6lib.save_json(
        COMPARE_SUMMARY_PATH,
        {
            "status": "ok",
            "generated_at_utc": pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ"),
            "method": "shadow_1m_replay_from_historical_reconstructed_entry",
            "closed_trades": int(len(merged)),
            "live_net_pnl_usdt": float(pd.to_numeric(merged.get("live_net_pnl_usdt"), errors="coerce").fillna(0.0).sum()),
            "shadow_proxy_net_pnl_usdt": float(pd.to_numeric(merged.get("shadow_proxy_net_pnl_usdt"), errors="coerce").fillna(0.0).sum()),
            "delta_vs_shadow_usdt": float(pd.to_numeric(merged.get("delta_vs_shadow_usdt"), errors="coerce").fillna(0.0).sum()),
            "exit_bucket_match_count": int((merged.get("exit_bucket_match") == True).sum()) if "exit_bucket_match" in merged.columns else 0,
            "close_match_count": int((merged.get("close_match") == True).sum()) if "close_match" in merged.columns else 0,
            "latest_live_exit_time": str(pd.to_datetime(merged["live_exit_time"], utc=True, errors="coerce").max().strftime("%Y-%m-%dT%H:%M:%SZ")) if not merged.empty and "live_exit_time" in merged.columns and pd.notna(pd.to_datetime(merged["live_exit_time"], utc=True, errors="coerce").max()) else None,
            "latest_shadow_exit_time": str(shadow_exit_series.max().strftime("%Y-%m-%dT%H:%M:%SZ")) if shadow_exit_series is not None and pd.notna(shadow_exit_series.max()) else None,
        },
    )


def refresh_local_dashboards() -> None:
    builders = [
        ROOT / "scripts" / "build_rank32b_global_live_dashboard.py",
        ROOT / "scripts" / "build_rank32b_canary_dashboard.py",
        ROOT / "scripts" / "build_live_trading_center.py",
        ROOT / "scripts" / "build_rank32b_global_live_like_3d_audit.py",
    ]
    for builder in builders:
        try:
            subprocess.run([sys.executable, str(builder)], cwd=str(ROOT), check=True, capture_output=True, text=True)
        except Exception:
            continue


def main() -> int:
    ap = argparse.ArgumentParser(description="Run rank32b global strongest-only live lane")
    ap.add_argument("--config", default=str(CONFIG_PATH))
    ap.add_argument("--allow-live", action="store_true", help="Actually place live orders")
    args = ap.parse_args()

    ensure_dir(ART_DIR)
    run_ctx = phase6lib.utcnow()
    cfg = phase6lib.load_yaml(Path(args.config))
    live_cfg = load_global_live_cfg(cfg)
    if not live_cfg.get("enabled", True):
        phase6lib.save_json(RUN_SUMMARY_PATH, {"generated_at_utc": run_ctx.now_iso, "status": "disabled", "message": "phase6.global_live.enabled=false"})
        return 0

    exec_cfg = build_exec_cfg(cfg, live_cfg)
    symbols = list(exec_cfg["universe"]["symbols"])
    current_code_version = phase6lib.code_version()
    current_config_version = phase6lib.config_hash(exec_cfg)
    state = phase6lib.load_state(STATE_PATH, symbols)
    state.reset_daily_counter_if_needed(run_ctx.now_dt)

    phase3 = cfg.get("phase3", {}) if isinstance(cfg.get("phase3"), dict) else {}
    bridge = phase6lib.load_frmonitor_bridge(
        phase3["fr_monitor_root"],
        local_private_path=phase3.get("local_private_path"),
    )
    event_bus = phase6lib.JsonlEventBus(EVENTS_PATH)

    events_written: list[dict[str, Any]] = []
    warnings_out: list[dict[str, Any]] = []
    intentions_out: list[dict[str, Any]] = []
    orders_out: list[dict[str, Any]] = []
    emitted_orders: list[dict[str, Any]] = []
    rejections_out: list[dict[str, Any]] = []
    closed_out: list[dict[str, Any]] = []

    managed_pending = 0
    moved_to_live = 0
    managed_live = 0
    closed_count = 0
    if args.allow_live:
        managed_pending, moved_to_live = phase6lib.manage_pending_entries(
            bridge=bridge,
            cfg=exec_cfg,
            state=state,
            run_ctx=run_ctx,
            event_bus=event_bus,
            events_written=events_written,
            orders_out=orders_out,
            emitted_orders=emitted_orders,
            warnings_out=warnings_out,
        )
        managed_live, closed_count = phase6lib.manage_live_positions(
            bridge=bridge,
            cfg=exec_cfg,
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
        save_state_local(state, symbols=symbols, now_iso=run_ctx.now_iso)

    own_live_symbols = {str(row.get("symbol") or "").upper() for row in state.live_positions if row.get("symbol")}
    core3_busy_symbols, priority_warnings = load_priority_busy_symbols(live_cfg, bridge, own_live_symbols)
    for warning in priority_warnings:
        phase6lib.append_warning(
            warnings_out,
            trace_id=phase6lib.make_trace_id("global32b-priority-scan"),
            symbol=str((warning.get("payload") or {}).get("symbol") or "SYSTEM"),
            message=str(warning.get("message") or "priority_scan_warning"),
            payload=(warning.get("payload") if isinstance(warning.get("payload"), dict) else {}),
        )

    safety_cfg = exec_cfg.get("phase6", {}).get("safety", {}) if isinstance(exec_cfg.get("phase6", {}).get("safety"), dict) else {}
    exit_attach_failure_pause = phase6lib.detect_recent_exit_attach_failure_pause(
        state,
        now_dt=run_ctx.now_dt,
        cooldown_minutes=int(safety_cfg.get("pause_new_entries_minutes_after_exit_attach_failure", 0)),
        current_code_version=current_code_version,
    )
    if exit_attach_failure_pause:
        phase6lib.append_warning(
            warnings_out,
            trace_id=phase6lib.make_trace_id("global32b-entry-safety-pause"),
            symbol=str(exit_attach_failure_pause.get("symbol") or "SYSTEM"),
            message="entry_safety_pause_recent_exit_attach_failure",
            payload=exit_attach_failure_pause,
        )

    entry_window = evaluate_official_entry_window(run_ctx.now_dt, live_cfg)
    signal_cfg = cfg.get("signal_adapter", {}) if isinstance(cfg.get("signal_adapter"), dict) else {}
    snapshot = type(
        "GlobalLiveSignalSnapshot",
        (),
        {"signals": [], "latest_bar_utc": None, "latest_signal_utc": None, "latest_observed_signal_utc": None},
    )()
    recent_signals: list[dict[str, Any]] = []
    seen = set(state.seen_signal_ids)
    seen.update(str(row.get("signal_id")) for row in state.pending_entries if row.get("signal_id"))
    seen.update(str(row.get("signal_id")) for row in state.live_positions if row.get("signal_id"))
    seen.update(str(row.get("signal_id")) for row in state.closed_trades if row.get("signal_id"))
    consumed_bar_keys = set(state.consumed_signal_bars)
    run_consumed_bar_keys: set[str] = set()
    skipped_weaker_signals: list[dict[str, Any]] = []
    stale_signals: list[tuple[Any, float]] = []
    new_signals: list[Any] = []
    max_signal_age_minutes = phase6lib.safe_float(live_cfg.get("max_signal_age_minutes", 3), 3.0)
    max_signal_age_seconds = max(0.0, max_signal_age_minutes * 60.0)

    if entry_window["eligible"]:
        adapter = phase6lib.Rank32BPerpSignalAdapter(
            asset_to_symbol=exec_cfg["universe"]["asset_to_symbol"],
            days=int(signal_cfg.get("lookback_days", 30)),
            recent_hours=int(cfg.get("phase6", {}).get("shadow_global", {}).get("recent_hours", signal_cfg.get("recent_hours", 72))),
            variant=str(signal_cfg.get("variant", "ema_cross_plus_slope_floor")),
            refresh_bars=bool(signal_cfg.get("refresh_bars", True)),
            refresh_tail_days=(int(signal_cfg["refresh_tail_days"]) if signal_cfg.get("refresh_tail_days") is not None else None),
            preview_unclosed_15m=bool(signal_cfg.get("preview_unclosed_15m", False)),
            preview_fetch_limit=int(signal_cfg.get("preview_fetch_limit", 30)),
            entry_delay_minutes=int(signal_cfg.get("entry_delay_minutes", 0)),
            official_signal_ttl_minutes=int(live_cfg.get("max_signal_age_minutes", 3)),
        )
        snapshot = adapter.load_recent_signals()
        recent_signals = [sig.to_dict() for sig in snapshot.signals]

        new_signals = [sig for sig in snapshot.signals if sig.signal_id not in seen]
        selection_phase6 = {
            "selection": live_cfg.get("selection", {}),
            "smallcap": {"enabled": False, "symbols": []},
            "max_new_signals_per_run": 0,
        }
        new_signals, skipped_weaker_signals = phase6lib.select_signals_for_execution(new_signals, selection_phase6)

        filtered_signals: list[Any] = []
        for sig in new_signals:
            confirmed_ts = phase6lib.signal_confirmed_at(str(getattr(sig, "timestamp", "")), getattr(sig, "metadata", None)) or str(getattr(sig, "timestamp", ""))
            signal_ts = phase6lib.parse_utc(confirmed_ts) or run_ctx.now_dt
            if signal_ts > run_ctx.now_dt:
                continue
            age_seconds = max(0.0, (run_ctx.now_dt - signal_ts).total_seconds())
            if max_signal_age_seconds > 0 and age_seconds > max_signal_age_seconds:
                stale_signals.append((sig, age_seconds))
            else:
                filtered_signals.append(sig)
        new_signals = phase6lib.limit_new_signals_for_execution(filtered_signals, exec_cfg.get("phase6", {}))
    else:
        phase6lib.append_warning(
            warnings_out,
            trace_id=phase6lib.make_trace_id("global32b-official-window"),
            symbol="SYSTEM",
            message="entry_window_closed_official_close_mode",
            payload=entry_window,
        )

    for sig, age_seconds in stale_signals:
        trace_id = phase6lib.make_trace_id(sig.signal_id)
        reject_row = {
            **sig.to_dict(),
            "signal_confirmed_at": phase6lib.signal_confirmed_at(sig.timestamp, getattr(sig, "metadata", None)),
            "risk": {
                "allowed": False,
                "reason": "signal_too_old",
                "signal_age_seconds": round(age_seconds, 2),
                "max_signal_age_seconds": round(max_signal_age_seconds, 2),
            },
        }
        rejections_out.append(reject_row)
        phase6lib.append_warning(warnings_out, trace_id=trace_id, symbol=sig.symbol, message="signal_too_old", payload=reject_row["risk"])
        state.seen_signal_ids.append(sig.signal_id)

    for skipped in skipped_weaker_signals:
        signal_id = str(skipped.get("signal_id") or "")
        if signal_id:
            state.seen_signal_ids.append(signal_id)
        bar_key = phase6lib.signal_bar_key(str(skipped.get("symbol") or ""), str(skipped.get("timestamp") or ""))
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

    risk_cfg = phase6lib.Canary32BRiskConfig(
        kill_switch=bool(exec_cfg["risk"]["kill_switch"]),
        trade_enabled=bool(exec_cfg["risk"]["trade_enabled"]),
        enabled_symbols=symbols,
        max_concurrent_positions=int(exec_cfg["risk"]["max_concurrent_positions"]),
        max_daily_trades=int(exec_cfg["risk"]["max_daily_trades"]),
        max_position_notional_per_symbol=float(exec_cfg["risk"]["max_position_notional_per_symbol"]),
        allow_entry_fallback_to_taker=bool(exec_cfg["execution"]["entry"].get("allow_fallback_to_taker", True)),
        max_data_delay_seconds=int(exec_cfg["risk"].get("max_data_delay_seconds", 259200)),
        require_atr=bool(exec_cfg["risk"].get("require_atr", True)),
        smallcap_symbols=[],
        max_core_positions=int(exec_cfg["risk"]["max_core_positions"]),
        max_smallcap_positions=None,
    )

    for signal in new_signals:
        trace_id = phase6lib.make_trace_id(signal.signal_id)
        if not isinstance(getattr(signal, "metadata", None), dict):
            signal.metadata = {}
        signal.metadata["symbol_bucket"] = "global"
        bar_key = phase6lib.signal_bar_key(signal.symbol, signal.timestamp, bar_minutes=15)

        if bar_key in consumed_bar_keys or bar_key in run_consumed_bar_keys:
            reject_row = {**signal.to_dict(), "bar_key": bar_key, "reason": "same_bar_signal_already_consumed"}
            rejections_out.append(reject_row)
            phase6lib.append_warning(warnings_out, trace_id=trace_id, symbol=signal.symbol, message="same_bar_signal_already_consumed", payload={"bar_key": bar_key})
            state.seen_signal_ids.append(signal.signal_id)
            save_state_local(state, symbols=symbols, now_iso=run_ctx.now_iso)
            continue

        if signal.symbol in core3_busy_symbols:
            reject_row = {
                **signal.to_dict(),
                "signal_confirmed_at": phase6lib.signal_confirmed_at(signal.timestamp, getattr(signal, "metadata", None)),
                "bar_key": bar_key,
                "risk": {"allowed": False, "reason": "cross_lane_symbol_busy", "conflict_symbols": sorted(core3_busy_symbols)},
            }
            rejections_out.append(reject_row)
            phase6lib.append_warning(warnings_out, trace_id=trace_id, symbol=signal.symbol, message="cross_lane_symbol_busy", payload={"conflict_busy_symbols": sorted(core3_busy_symbols)})
            state.seen_signal_ids.append(signal.signal_id)
            state.consumed_signal_bars.append(bar_key)
            consumed_bar_keys.add(bar_key)
            save_state_local(state, symbols=symbols, now_iso=run_ctx.now_iso)
            continue

        if exit_attach_failure_pause:
            reject_row = {
                **signal.to_dict(),
                "signal_confirmed_at": phase6lib.signal_confirmed_at(signal.timestamp, getattr(signal, "metadata", None)),
                "bar_key": bar_key,
                "risk": {"allowed": False, "reason": "entry_safety_pause_recent_exit_attach_failure", "pause": exit_attach_failure_pause},
            }
            rejections_out.append(reject_row)
            state.seen_signal_ids.append(signal.signal_id)
            save_state_local(state, symbols=symbols, now_iso=run_ctx.now_iso)
            continue

        signal_ts = phase6lib.parse_utc(phase6lib.signal_confirmed_at(signal.timestamp, getattr(signal, "metadata", None)) or signal.timestamp) or run_ctx.now_dt
        age_seconds = max(0.0, (run_ctx.now_dt - signal_ts).total_seconds())
        market_ctx = phase6lib.Canary32BMarketContext(
            atr_available=bool(signal.metadata.get("atr_ready", False)),
            data_delay_seconds=age_seconds,
            metadata={"variant": signal.metadata.get("variant"), "symbol_bucket": "global"},
        )
        portfolio = phase6lib.portfolio_state_from_runtime(
            state.symbol_states,
            state.daily_trade_count,
            api_healthy=True,
            live_positions=state.live_positions,
            pending_entries=state.pending_entries,
            smallcap_symbols=[],
        )
        decision = phase6lib.evaluate_entry_risk(signal, trace_id=trace_id, config=risk_cfg, portfolio=portfolio, market=market_ctx)
        if not decision.accepted:
            reject_row = {**signal.to_dict(), "risk": decision.to_dict()}
            rejections_out.append(reject_row)
            phase6lib.append_warning(warnings_out, trace_id=trace_id, symbol=signal.symbol, message=decision.reason, payload=decision.to_dict())
            state.seen_signal_ids.append(signal.signal_id)
            save_state_local(state, symbols=symbols, now_iso=run_ctx.now_iso)
            continue

        run_consumed_bar_keys.add(bar_key)
        state.consumed_signal_bars.append(bar_key)

        signal_side = signal.side.value
        symbol = signal.symbol
        notional_cfg = phase6lib.resolve_symbol_desired_notional_usdt(exec_cfg["phase6"], symbol)
        rules = bridge.get_binance_perp_trade_rules(symbol)
        last_price = bridge.get_binance_perp_last_price(symbol)
        sizing_floor = bridge.estimate_binance_min_trade_floor(symbol, last_price=last_price, rules=rules)
        floor_notional = phase6lib.safe_float(sizing_floor.get("effective_min_notional"), 5.0)
        buffer_mult = max(1.0, float(exec_cfg["phase6"]["sizing"].get("min_notional_buffer_mult", 1.0)))
        target_notional = max(notional_cfg, floor_notional * buffer_mult)
        append_selected_signal_audit_row(
            signal=signal,
            bar_key=bar_key,
            run_ctx=run_ctx,
            allow_live=bool(args.allow_live),
            code_version=current_code_version,
            config_version=current_config_version,
            risk_decision=decision,
            intended_notional_usdt=target_notional,
        )
        qty_info = bridge.derive_binance_qty_from_notional(symbol, target_notional, last_price=last_price, rules=rules)
        quantity = phase6lib.safe_float(qty_info.get("quantity"))

        intention_id = f"intent-{hashlib.sha1((signal.signal_id + '|g32b').encode('utf-8')).hexdigest()[:14]}"
        intended_price = phase6lib.safe_float(signal.signal_price)
        intention = phase6lib.build_entry_intention(
            signal,
            intention_id=intention_id,
            trace_id=trace_id,
            qty=quantity,
            target_price=float(intended_price),
            ttl_minutes=int(exec_cfg["phase6"]["entry"].get("ttl_minutes", 15)),
            fallback_to_taker=bool(exec_cfg["phase6"]["entry"].get("fallback_to_market_on_ttl", True)),
            config_version=current_config_version,
        )
        intentions_out.append(intention.to_dict())

        target_leverage = max(1, int(phase6lib.safe_float(exec_cfg["phase6"].get("default_leverage", 1), 1)))
        phase6lib.ensure_binance_leverage(
            bridge,
            symbol=symbol,
            signal_side=signal_side,
            target_leverage=target_leverage,
        )

        order_side = phase6lib.signal_to_order_side(signal_side)
        client_order_id = make_client_order_id("en", symbol, run_ctx, trace_id)
        if not args.allow_live:
            orders_out.append(
                {
                    "timestamp": run_ctx.now_iso,
                    "symbol": symbol,
                    "side": order_side,
                    "order_role": "entry_preview",
                    "order_type": "MARKET",
                    "price": last_price,
                    "qty": quantity,
                    "status": "DRY_RUN",
                    "client_order_id": client_order_id,
                    "planned_notional": target_notional,
                }
            )
            state.seen_signal_ids.append(signal.signal_id)
            save_state_local(state, symbols=symbols, now_iso=run_ctx.now_iso)
            continue

        entry_order = bridge.place_binance_perp_live_market_order(
            symbol=symbol,
            side=order_side,
            quantity=quantity,
            reduce_only=None,
            position_side=phase6lib.hedge_position_side(signal_side),
            client_order_id=client_order_id,
        )
        entry_n = phase6lib.normalize_order_payload(entry_order, source="entry_market")
        filled_qty = phase6lib.safe_float(entry_n.get("executed_qty"), quantity)
        entry_price = phase6lib.safe_float(entry_n.get("avg_price"), phase6lib.safe_float(entry_n.get("price"), signal.signal_price))

        try:
            exit_plan = phase6lib.attach_exit_plan(
                bridge,
                phase6=exec_cfg["phase6"],
                symbol=symbol,
                side=signal_side,
                signal_price=signal.signal_price,
                entry_price=entry_price,
                executed_qty=filled_qty,
                atr14=phase6lib.safe_float(signal.metadata.get("atr14"), math.nan),
                run_ctx=run_ctx,
                trace_id=trace_id,
                signal_id=signal.signal_id,
                signal_timestamp=signal.timestamp,
                signal_confirmed_at_override=phase6lib.signal_confirmed_at(signal.timestamp, getattr(signal, "metadata", None)),
                intention_id=intention_id,
                entry_order_id=entry_n.get("order_id"),
                entry_client_order_id=entry_n.get("client_order_id") or client_order_id,
                code_version=current_code_version,
                config_version=current_config_version,
            )
        except Exception as exc:  # noqa: BLE001
            phase6lib.append_warning(
                warnings_out,
                trace_id=trace_id,
                symbol=symbol,
                message="exit attach failed after market entry; emergency flatten triggered",
                payload={"error": str(exc), "entry_order_id": entry_n.get("order_id")},
            )
            emergency_cid = make_client_order_id("ec", symbol, run_ctx, trace_id)
            emergency_close = bridge.place_binance_perp_live_market_order(
                symbol=symbol,
                side=phase6lib.exit_order_side(signal_side),
                quantity=filled_qty,
                reduce_only=None,
                position_side=phase6lib.hedge_position_side(signal_side),
                client_order_id=emergency_cid,
            )
            emergency_n = phase6lib.normalize_order_payload(emergency_close, source="emergency_flatten")
            exit_price = phase6lib.safe_float(emergency_n.get("avg_price"), phase6lib.safe_float(emergency_n.get("price"), entry_price))
            gross_pnl = (exit_price - entry_price) * filled_qty if signal_side == "long" else (entry_price - exit_price) * filled_qty
            fee_usdt, net_pnl, net_return_bps = phase6lib.estimate_fee_and_net(entry_price=entry_price, exit_price=exit_price, qty=filled_qty, gross_pnl=gross_pnl)
            close_row = {
                "trace_id": trace_id,
                "signal_id": signal.signal_id,
                "signal_timestamp": signal.timestamp,
                "signal_price": signal.signal_price,
                "signal_confirmed_at": phase6lib.signal_confirmed_at(signal.timestamp, getattr(signal, "metadata", None)),
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
                "fee_bps_round_trip": phase6lib.ESTIMATED_FEE_BPS_ROUND_TRIP,
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
                    "side": phase6lib.exit_order_side(signal_side),
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
            state.daily_trade_count += 1
            state.seen_signal_ids.append(signal.signal_id)
            save_state_local(state, symbols=symbols, now_iso=run_ctx.now_iso)
            continue

        state.live_positions.append(exit_plan["live_row"])
        for warn in exit_plan.get("warnings", []):
            phase6lib.append_warning(
                warnings_out,
                trace_id=str(warn.get("trace_id") or trace_id),
                symbol=str(warn.get("symbol") or symbol),
                message=str(warn.get("message") or "exit_plan_warning"),
                payload=warn.get("payload"),
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
        save_state_local(state, symbols=symbols, now_iso=run_ctx.now_iso)

    state.enabled_symbols = symbols
    state.refresh_symbol_state(symbols, run_ctx.now_iso)
    state.closed_trades = state.closed_trades[-400:]
    state.last_run_utc = run_ctx.now_iso
    phase6lib.JsonStateStore(STATE_PATH).save(state.to_dict())

    recent_positions = state.live_positions[-80:]
    recent_closed = state.closed_trades[-120:]
    existing_recent_positions = phase6lib.load_json(POSITIONS_PATH, [])
    if not isinstance(existing_recent_positions, list):
        existing_recent_positions = []
    recent_positions_history = phase6lib.merge_recent_rows(
        existing_recent_positions,
        recent_positions + recent_closed,
        tail=120,
        key_fields=["trace_id", "signal_id", "entry_time"],
    )

    warning_summary = phase6lib.summarize_warning_buckets(warnings_out)
    system_health = "ok" if warning_summary["total"] == 0 else "degraded"
    status_notes = [
        "Global32b live = strongest-only all-26 live lane, independent from core3.",
        "Priority rule: core3 > global32b_live > rank29_gate_live. Lower-priority lanes skip without waiting.",
        "Execution style follows phase6 market entry + TP/SL/timeout exit plan.",
        f"Entry gate: official-close only, cadence={entry_window['cadence_minutes']}m, trigger_second={entry_window['trigger_second']}, freshness_seconds={entry_window['freshness_seconds']}.",
    ]
    if exit_attach_failure_pause:
        status_notes.append(
            "Safety pause active after recent exit-attach failure: "
            f"{exit_attach_failure_pause.get('symbol')} @ {exit_attach_failure_pause.get('last_failure_time')}"
        )

    status = phase6lib.StrategyStatusSnapshot(
        alpha_name="rank32b_global_live",
        version="global32b_live_v1",
        mode=str(live_cfg.get("mode", "global_live")),
        enabled_symbols=symbols,
        current_config_hash=current_config_version,
        last_signal_time=snapshot.latest_observed_signal_utc,
        system_health=system_health,
        last_run_utc=run_ctx.now_iso,
        trade_enabled=bool(exec_cfg["risk"]["trade_enabled"]) and bool(args.allow_live),
        kill_switch=bool(exec_cfg["risk"]["kill_switch"]),
        recent_signal_count=len(recent_signals),
        recent_intention_count=len(intentions_out),
        recent_reject_count=len(rejections_out),
        latest_evaluated_bar_time=snapshot.latest_bar_utc,
        notes=status_notes,
    )
    run_finished_at = phase6lib.utc_now_iso()
    operator_packet = {
        "candidate_id": "rank32b_global_live",
        "mode": live_cfg.get("mode", "global_live"),
        "allow_live_orders": bool(args.allow_live),
        "desired_notional_usdt": float(live_cfg["desired_notional_usdt"]),
        "selection_mode": "strongest_signal_only_global",
        "selection_strength_metric": str(live_cfg.get("selection", {}).get("strength_metric", "slope_strength")),
        "signals_in_window": len(recent_signals),
        "entry_window": entry_window,
        "latest_evaluated_bar_time": snapshot.latest_bar_utc,
        "latest_observed_signal_time": snapshot.latest_observed_signal_utc,
        "latest_actionable_signal_time": snapshot.latest_signal_utc,
        "new_signals_processed": len(new_signals),
        "skipped_weaker_signals": len(skipped_weaker_signals),
        "intentions_created": len(intentions_out),
        "orders_emitted": len(emitted_orders),
        "risk_rejections": len(rejections_out),
        "pending_entries": len(state.pending_entries),
        "live_positions": len(state.live_positions),
        "closed_trades_new": len(closed_out),
        "closed_trades_total": len(state.closed_trades),
        "warnings": warning_summary["total"],
        "managed_pending_entries": managed_pending,
        "managed_live_positions": managed_live,
        "moved_to_live_from_pending": moved_to_live,
        "closed_positions_this_run": closed_count,
        "core3_busy_symbols": sorted(core3_busy_symbols),
        "conflict_busy_symbols": sorted(core3_busy_symbols),
        "generated_at_utc": run_finished_at,
    }

    phase6lib.save_json(STATUS_PATH, status.to_dict())
    phase6lib.save_json(
        RUN_SUMMARY_PATH,
        {
            "generated_at_utc": run_finished_at,
            "run_started_at": run_ctx.now_iso,
            "run_finished_at": run_finished_at,
            "mode": live_cfg.get("mode", "global_live"),
            "allow_live_orders": bool(args.allow_live),
            "desired_notional_usdt": float(live_cfg["desired_notional_usdt"]),
            "desired_notional_usdt_by_symbol": live_cfg["desired_notional_usdt_by_symbol"],
            "signals_seen_this_window": len(recent_signals),
            "entry_window": entry_window,
            "latest_evaluated_bar_time": snapshot.latest_bar_utc,
            "latest_observed_signal_time": snapshot.latest_observed_signal_utc,
            "latest_actionable_signal_time": snapshot.latest_signal_utc,
            "selection_mode": "strongest_signal_only_global",
            "selection_strength_metric": live_cfg.get("selection", {}).get("strength_metric", "slope_strength"),
            "skipped_weaker_signals": len(skipped_weaker_signals),
            "new_signals_processed": len(new_signals),
            "intentions_created": len(intentions_out),
            "orders_emitted": len(emitted_orders),
            "risk_rejections": len(rejections_out),
            "pending_entries": len(state.pending_entries),
            "live_positions": len(state.live_positions),
            "closed_positions_this_run": closed_count,
            "closed_trades_total": len(state.closed_trades),
            "warnings": warning_summary["total"],
            "core3_busy_symbols": sorted(core3_busy_symbols),
            "conflict_busy_symbols": sorted(core3_busy_symbols),
            "status": "ok",
        },
    )
    phase6lib.save_json(OPERATOR_PACKET_PATH, operator_packet)
    phase6lib.save_json(SIGNALS_PATH, recent_signals[-120:])
    phase6lib.save_json(INTENTIONS_PATH, intentions_out[-120:])
    phase6lib.save_json(ORDERS_PATH, phase6lib.merge_recent_rows(phase6lib.load_json(ORDERS_PATH, []), orders_out, tail=160, key_fields=["timestamp", "symbol", "order_role", "client_order_id"]))
    phase6lib.save_json(REJECTIONS_PATH, phase6lib.merge_recent_rows(phase6lib.load_json(REJECTIONS_PATH, []), rejections_out, tail=160, key_fields=["signal_id", "reason", "bar_key"]))
    phase6lib.save_json(CLOSED_TRADES_PATH, recent_closed)
    phase6lib.save_json(POSITIONS_PATH, recent_positions_history)
    phase6lib.save_json(WARNINGS_PATH, phase6lib.merge_recent_rows(phase6lib.load_json(WARNINGS_PATH, []), warnings_out, tail=160, key_fields=["timestamp", "trace_id", "message", "symbol"]))
    write_compare_artifacts(live_cfg, state.closed_trades)
    refresh_local_dashboards()

    print(
        json.dumps(
            {
                "generated_at_utc": run_ctx.now_iso,
                "artifacts_root": str(ART_DIR.relative_to(ROOT)),
                "allow_live_orders": bool(args.allow_live),
                "core3_busy_symbols": sorted(core3_busy_symbols),
                "conflict_busy_symbols": sorted(core3_busy_symbols),
                "live_positions": len(state.live_positions),
                "closed_trades": len(state.closed_trades),
            },
            ensure_ascii=False,
        )
    )
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
            live_cfg = load_global_live_cfg(cfg)
            cfg_hash = phase6lib.config_hash(build_exec_cfg(cfg, live_cfg))
        except Exception:
            pass
        try:
            code_version = phase6lib.code_version()
        except Exception:
            pass
        phase6lib.save_json(
            RUN_SUMMARY_PATH,
            {
                "generated_at_utc": now_iso,
                "status": "error_degraded",
                "lane_name": "global32b_live",
                "code_version": code_version,
                "config_version": cfg_hash,
                "error": str(exc),
            },
        )
        phase6lib.save_json(
            STATUS_PATH,
            {
                "alpha_name": "rank32b_global_live",
                "version": code_version,
                "mode": "global_live",
                "current_config_hash": cfg_hash,
                "system_health": "degraded",
                "last_run_utc": now_iso,
                "trade_enabled": False,
                "kill_switch": False,
                "recent_signal_count": 0,
                "recent_intention_count": 0,
                "recent_reject_count": 0,
                "notes": [f"global32b live degraded: {exc}"],
            },
        )
        raise
