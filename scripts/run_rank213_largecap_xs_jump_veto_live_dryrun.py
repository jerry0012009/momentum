#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "execution" / "rank213_live_canary.yaml"
ASOF_REVIEW_PATH = ROOT / "scripts" / "build_rank213_asof_universe_long_history_review.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


asof_mod = load_module(ASOF_REVIEW_PATH, "rank213_asof_review_mod")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_z(ts: Any) -> str | None:
    if ts is None or pd.isna(ts):
        return None
    return pd.to_datetime(ts, utc=True).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def save_json(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_jsonl(path: Path, row: dict[str, Any], *, keep_last: int = 200) -> None:
    ensure_dir(path.parent)
    rows: list[str] = []
    if path.exists():
        rows = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    rows.append(json.dumps(row, ensure_ascii=False))
    rows = rows[-keep_last:]
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def append_recent_json(path: Path, new_rows: list[dict[str, Any]], *, tail: int, key_fields: list[str]) -> list[dict[str, Any]]:
    existing = read_json(path, [])
    if not isinstance(existing, list):
        existing = []
    merged: list[dict[str, Any]] = []
    seen: set[tuple[Any, ...]] = set()
    for row in existing + new_rows:
        if not isinstance(row, dict):
            continue
        key = tuple(row.get(field) for field in key_fields)
        if any(part not in (None, "") for part in key):
            if key in seen:
                continue
            seen.add(key)
        merged.append(row)
    merged = merged[-tail:]
    save_json(path, merged)
    return merged


def load_state(path: Path) -> dict[str, Any]:
    raw = read_json(path, {})
    if not isinstance(raw, dict):
        return {}
    return raw


def parse_ts(value: Any) -> pd.Timestamp | None:
    if value in (None, ""):
        return None
    try:
        ts = pd.to_datetime(value, utc=True)
    except Exception:
        return None
    if pd.isna(ts):
        return None
    return ts


def _normalize_side(value: Any) -> str:
    side = str(value or "").strip().lower()
    if side in {"buy", "long"}:
        return "long"
    if side in {"sell", "short"}:
        return "short"
    return side


def cooldown_active(state: dict[str, Any], cfg: dict[str, Any], *, now_ts: pd.Timestamp) -> dict[str, Any] | None:
    controls = cfg.get("canary_controls", {}) if isinstance(cfg.get("canary_controls"), dict) else {}
    cooldown_minutes = int(controls.get("cooldown_minutes_after_rejection", 15))
    if cooldown_minutes <= 0:
        return None
    last_rejection_ts = parse_ts(state.get("last_rejection_at_utc"))
    if last_rejection_ts is None:
        return None
    last_reasons = [str(x) for x in state.get("last_rejection_reasons", []) if x]
    if last_reasons and all(
        reason in {
            "artifact_not_published_yet",
            "before_entry_window",
            "entry_window_closed",
            "shadow_bar_mismatch",
            "stale_signal",
            "same_bar_once",
            "cooldown_active",
            "preview_signal",
            "active_basket_exists",
            "basket_safety_blocked_pretrade",
            "turnover_close_only",
        }
        for reason in last_reasons
    ):
        return None
    elapsed = (now_ts - last_rejection_ts).total_seconds() / 60.0
    if elapsed >= cooldown_minutes:
        return None
    return {
        "last_rejection_at_utc": iso_z(last_rejection_ts),
        "cooldown_minutes": cooldown_minutes,
        "remaining_minutes": round(max(0.0, cooldown_minutes - elapsed), 3),
        "last_rejection_reasons": last_reasons,
    }


def build_artifact_paths(cfg: dict[str, Any]) -> dict[str, Path]:
    artifacts = cfg.get("artifacts", {}) if isinstance(cfg.get("artifacts"), dict) else {}
    root = Path(str(artifacts.get("root") or ROOT / "reports" / "artifacts" / "rank213_live_canary"))
    return {
        "root": root,
        "events": root / str(artifacts.get("events_name", "live_events.jsonl")),
        "status": root / str(artifacts.get("status_name", "live_status.json")),
        "state": root / str(artifacts.get("state_name", "live_state.json")),
        "intentions": root / str(artifacts.get("intentions_name", "live_recent_intentions.json")),
        "orders": root / str(artifacts.get("orders_name", "live_recent_orders.json")),
        "rejections": root / str(artifacts.get("rejections_name", "live_recent_rejections.json")),
        "warnings": root / str(artifacts.get("warnings_name", "live_warnings.json")),
        "compare": root / str(artifacts.get("compare_name", "live_vs_shadow.csv")),
        "compare_summary": root / str(artifacts.get("compare_summary_name", "live_vs_shadow_summary.json")),
        "operator_packet": root / "live_operator_packet.json",
        "run_summary": root / "live_last_run_summary.json",
        "config_snapshot": root / str(artifacts.get("config_snapshot_name", "rank213_live_canary_config_snapshot.yaml")),
    }


def compute_freshness_minutes(ts: str | None, *, now_ts: pd.Timestamp | None = None) -> float | None:
    if not ts:
        return None
    ref = now_ts if now_ts is not None else pd.Timestamp(utc_now())
    return max(0.0, (ref - pd.Timestamp(ts)).total_seconds() / 60.0)


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        num = float(value)
    except Exception:
        return float(default)
    if not math.isfinite(num):
        return float(default)
    return num


def expected_official_bar_ts(now_ts: pd.Timestamp, cadence_minutes: int) -> pd.Timestamp:
    return now_ts.floor(f"{max(1, int(cadence_minutes))}min")


def evaluate_official_entry_window(current: dict[str, Any], shadow_status: dict[str, Any], cfg: dict[str, Any], *, now_ts: pd.Timestamp) -> dict[str, Any]:
    execution = cfg.get("execution", {}) if isinstance(cfg.get("execution"), dict) else {}
    cadence_minutes = int(execution.get("entry_cadence_minutes", 15))
    expected_bar_ts = expected_official_bar_ts(now_ts, cadence_minutes)
    expected_bar_key = iso_z(expected_bar_ts)
    current_bar_key = str(current.get("bar_key") or "")
    age_seconds = max(0.0, (now_ts - expected_bar_ts).total_seconds())
    start_after = int(execution.get("official_entry_start_seconds_after_close", execution.get("entry_trigger_second", 5)))
    end_after = int(execution.get("official_entry_end_seconds_after_close", max(start_after, int(float(execution.get("max_signal_age_minutes", 3)) * 60) - 1)))
    publish_grace = int(execution.get("shadow_publish_grace_seconds", end_after))
    updated_at_utc = shadow_status.get("updated_at_utc") if isinstance(shadow_status, dict) else None
    updated_at_ts = parse_ts(updated_at_utc)

    if current_bar_key != expected_bar_key:
        if age_seconds <= publish_grace and (updated_at_ts is None or updated_at_ts < expected_bar_ts):
            return {
                "eligible": False,
                "reason": "artifact_not_published_yet",
                "detail": {
                    "expected_bar_key": expected_bar_key,
                    "current_bar_key": current_bar_key or None,
                    "shadow_updated_at_utc": updated_at_utc,
                    "seconds_since_expected_close": round(age_seconds, 3),
                    "publish_grace_seconds": publish_grace,
                },
            }
        return {
            "eligible": False,
            "reason": "shadow_bar_mismatch",
            "detail": {
                "expected_bar_key": expected_bar_key,
                "current_bar_key": current_bar_key or None,
                "shadow_updated_at_utc": updated_at_utc,
                "seconds_since_expected_close": round(age_seconds, 3),
            },
        }
    if age_seconds < start_after:
        return {
            "eligible": False,
            "reason": "before_entry_window",
            "detail": {
                "bar_key": current_bar_key,
                "seconds_since_expected_close": round(age_seconds, 3),
                "window_start_seconds": start_after,
            },
        }
    if age_seconds > end_after:
        return {
            "eligible": False,
            "reason": "entry_window_closed",
            "detail": {
                "bar_key": current_bar_key,
                "seconds_since_expected_close": round(age_seconds, 3),
                "window_end_seconds": end_after,
            },
        }
    return {
        "eligible": True,
        "reason": "within_entry_window",
        "detail": {
            "bar_key": current_bar_key,
            "seconds_since_expected_close": round(age_seconds, 3),
            "window_start_seconds": start_after,
            "window_end_seconds": end_after,
        },
    }


def load_conflict_exposures(cfg: dict[str, Any]) -> tuple[dict[str, dict[str, list[dict[str, Any]]]], list[dict[str, Any]]]:
    conflict = cfg.get("conflict", {}) if isinstance(cfg.get("conflict"), dict) else {}
    if not bool(conflict.get("enabled", False)):
        return {}, []
    state_paths = [Path(str(p)) for p in conflict.get("state_paths", []) if p]
    exposures: dict[str, dict[str, list[dict[str, Any]]]] = {}
    warnings: list[dict[str, Any]] = []

    def add_exposure(symbol_value: Any, side_value: Any, *, source_path: Path, bucket: str, detail: dict[str, Any] | None = None) -> None:
        symbol = str(symbol_value or "").upper().strip()
        side = str(side_value or "").strip().lower()
        if side in {"buy", "long"}:
            side = "long"
        elif side in {"sell", "short"}:
            side = "short"
        if not symbol or side not in {"long", "short"}:
            return
        symbol_exposures = exposures.setdefault(symbol, {"long": [], "short": []})
        symbol_exposures[side].append({
            "symbol": symbol,
            "side": side,
            "bucket": bucket,
            "source_path": str(source_path),
            **(detail or {}),
        })

    for path in state_paths:
        raw = read_json(path, {})
        if not isinstance(raw, dict):
            warnings.append({"kind": "conflict_scan_invalid", "message": f"conflict state is not a dict: {path}"})
            continue
        for bucket in ("pending_entries", "live_positions"):
            for row in raw.get(bucket, []) or []:
                if not isinstance(row, dict):
                    continue
                add_exposure(
                    row.get("symbol"),
                    row.get("side"),
                    source_path=path,
                    bucket=bucket,
                    detail={
                        "basket_id": row.get("basket_id"),
                        "trace_id": row.get("trace_id"),
                    },
                )
        exchange_reconciliation = raw.get("exchange_reconciliation") if isinstance(raw.get("exchange_reconciliation"), dict) else {}
        for row in exchange_reconciliation.get("positions", []) or []:
            if not isinstance(row, dict):
                continue
            classification = str(row.get("reconciliation_classification") or "")
            if classification not in {"claimed_by_local_state", "close_conflict_residual", "residual_open_on_exchange"}:
                continue
            add_exposure(
                row.get("symbol"),
                row.get("side"),
                source_path=path,
                bucket="exchange_reconciliation",
                detail={
                    "reconciliation_classification": classification,
                    "rank213_owned": bool(row.get("rank213_owned")),
                    "matched_basket_ids": row.get("matched_basket_ids"),
                },
            )
        for row in raw.get("exchange_open_positions", []) or []:
            if not isinstance(row, dict):
                continue
            add_exposure(
                row.get("symbol"),
                row.get("side"),
                source_path=path,
                bucket="exchange_open_positions",
            )
    return exposures, warnings


def compute_basket_metrics(current: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    capital = cfg.get("capital", {}) if isinstance(cfg.get("capital"), dict) else {}
    basket = cfg.get("basket_controls", {}) if isinstance(cfg.get("basket_controls"), dict) else {}
    longs = [str(x).upper() for x in current.get("longs", []) if x]
    shorts = [str(x).upper() for x in current.get("shorts", []) if x]
    per_leg_default = safe_float(capital.get("desired_leg_notional_usdt", 20.0), 20.0)
    per_leg_min = safe_float(capital.get("min_leg_notional_usdt", per_leg_default), per_leg_default)
    by_symbol = capital.get("desired_leg_notional_usdt_by_symbol", {}) if isinstance(capital.get("desired_leg_notional_usdt_by_symbol"), dict) else {}

    long_nominal = sum(max(per_leg_min, safe_float(by_symbol.get(symbol), per_leg_default),) for symbol in longs)
    short_nominal = sum(max(per_leg_min, safe_float(by_symbol.get(symbol), per_leg_default),) for symbol in shorts)
    gross_nominal = long_nominal + short_nominal
    nominal_imbalance = abs(long_nominal - short_nominal)
    missing_total = abs(int(basket.get("target_long_legs", 3)) - len(longs)) + abs(int(basket.get("target_short_legs", 3)) - len(shorts))
    side_imbalance = nominal_imbalance
    return {
        "long_count": len(longs),
        "short_count": len(shorts),
        "filled_legs_total": len(longs) + len(shorts),
        "long_nominal_usdt": round(long_nominal, 6),
        "short_nominal_usdt": round(short_nominal, 6),
        "gross_nominal_usdt": round(gross_nominal, 6),
        "nominal_imbalance_usdt": round(nominal_imbalance, 6),
        "side_imbalance_usdt": round(side_imbalance, 6),
        "missing_legs_total": int(missing_total),
        "target_leg_notional_floor_usdt": round(per_leg_min, 6),
    }


def derive_basket_id(current: dict[str, Any]) -> str | None:
    bar_key = str(current.get("bar_key") or "").strip()
    if not bar_key:
        return None
    return f"rank213-{bar_key}"


def _load_horizon_panel(symbols: list[str], start_ts: pd.Timestamp, end_ts: pd.Timestamp) -> pd.DataFrame:
    frames: list[pd.Series] = []
    for symbol in symbols:
        try:
            df = asof_mod.load_or_build_symbol(symbol, start_ts, end_ts)
        except Exception:
            continue
        if df.empty:
            continue
        series = df.set_index("timestamp")["close"].astype(float).rename(symbol)
        frames.append(series)
    if not frames:
        return pd.DataFrame()
    panel = pd.concat(frames, axis=1).sort_index()
    panel.index = pd.to_datetime(panel.index, utc=True)
    return panel[~panel.index.duplicated(keep="last")].sort_index()


def _lookup_horizon_price(panel: pd.DataFrame, symbol: str, target_ts: pd.Timestamp) -> tuple[float | None, str | None]:
    if panel.empty or symbol not in panel.columns:
        return None, None
    series = panel[symbol].dropna()
    if series.empty:
        return None, None
    eligible = series[series.index >= target_ts]
    if eligible.empty:
        return None, None
    ts = eligible.index[0]
    px = safe_float(eligible.iloc[0], 0.0)
    if px <= 0:
        return None, None
    return px, iso_z(ts)


def build_basket_parity_payload(*, current: dict[str, Any], basket_metrics: dict[str, Any], intentions: list[dict[str, Any]], submitted_rows: list[dict[str, Any]] | None = None, live_rows: list[dict[str, Any]] | None = None, closed_rows: list[dict[str, Any]] | None = None, leg_failures: list[dict[str, Any]] | None = None, submit_stats: dict[str, int] | None = None, fallback_taker_count: int = 0, maker_reject_symbols: list[str] | None = None, fallback_taker_symbols: list[str] | None = None, suppression_reasons: list[dict[str, Any]] | None = None, exchange_positions: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    submitted_rows = submitted_rows or []
    live_rows = live_rows or []
    closed_rows = closed_rows or []
    leg_failures = leg_failures or []
    submit_stats = submit_stats or {}
    maker_reject_symbols = [str(symbol).upper() for symbol in (maker_reject_symbols or []) if str(symbol or "").strip()]
    fallback_taker_symbols = [str(symbol).upper() for symbol in (fallback_taker_symbols or []) if str(symbol or "").strip()]
    suppression_reasons = suppression_reasons or []
    exchange_positions = exchange_positions or []

    intended_longs = [str(x).upper() for x in current.get("longs", []) if x]
    intended_shorts = [str(x).upper() for x in current.get("shorts", []) if x]
    intended_symbols = intended_longs + intended_shorts
    planned_exit_ts = parse_ts(current.get("planned_exit_ts"))
    fill_times = [parse_ts(row.get("entry_time")) for row in [*live_rows, *closed_rows] if row.get("entry_time")]
    fill_times = [ts for ts in fill_times if ts is not None]
    horizon_start_ts = min(fill_times) if fill_times else None
    horizon_panel = pd.DataFrame()
    if planned_exit_ts is not None and horizon_start_ts is not None and intended_symbols:
        lookback_start = horizon_start_ts.floor(f"{int(asof_mod.BAR_MINUTES)}min") - pd.Timedelta(minutes=int(asof_mod.BAR_MINUTES) * 2)
        lookahead_end = planned_exit_ts + pd.Timedelta(minutes=int(asof_mod.BAR_MINUTES) * 2)
        horizon_panel = _load_horizon_panel(sorted(set(intended_symbols)), lookback_start, lookahead_end)

    def _ordered_unique_symbols(rows: list[dict[str, Any]]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for row in rows:
            symbol = str(row.get("symbol") or "").upper()
            if not symbol or symbol in seen:
                continue
            seen.add(symbol)
            out.append(symbol)
        return out

    def _summarize_suppression(rows: list[dict[str, Any]]) -> dict[str, Any]:
        by_reason: dict[str, int] = {}
        by_class: dict[str, int] = {}
        details: list[dict[str, Any]] = []
        for row in rows:
            reason = str(row.get("reason") or "unknown")
            if reason in {"cooldown_active", "same_bar_once", "cross_lane_conflict_busy", "cross_lane_symbol_busy", "cross_lane_same_side_busy", "cross_lane_opposite_side_conflict", "active_basket_busy", "active_basket_exists"}:
                suppression_class = "operational"
            elif reason in {"basket_incomplete", "side_imbalance_exceeded", "nominal_drift_exceeded"}:
                suppression_class = "basket_safety"
            elif reason in {"gate_off", "no_trade_decision"}:
                suppression_class = "strategy"
            elif reason in {"artifact_not_published_yet", "entry_window_closed", "outside_entry_window"}:
                suppression_class = "timing"
            else:
                suppression_class = "other"
            by_reason[reason] = by_reason.get(reason, 0) + 1
            by_class[suppression_class] = by_class.get(suppression_class, 0) + 1
            details.append({
                "reason": reason,
                "class": suppression_class,
                "detail": row,
            })
        return {
            "count": len(rows),
            "by_reason": by_reason,
            "by_class": by_class,
            "details": details,
        }

    submitted_symbols = _ordered_unique_symbols([*submitted_rows, *live_rows, *closed_rows])
    live_symbols = _ordered_unique_symbols(live_rows)
    closed_symbols = _ordered_unique_symbols(closed_rows)
    failed_symbols = _ordered_unique_symbols(leg_failures)
    materialized_symbols = _ordered_unique_symbols([
        row for row in [*submitted_rows, *live_rows, *closed_rows]
        if bool((row or {}).get("basket_leg_materialized", True))
    ])
    failed_symbol_reasons = {
        str(row.get("symbol") or "").upper(): str(row.get("reason") or "submit_failed")
        for row in leg_failures
        if isinstance(row, dict) and str(row.get("symbol") or "").strip()
    }

    intended_count = len(intended_symbols)
    submitted_count = len(submitted_symbols)
    live_count = len(live_symbols)
    closed_count = len(closed_symbols)
    failed_count = len(failed_symbols)
    unmaterialized_symbols = sorted(set(intended_symbols) - set(materialized_symbols))
    maker_reject_count = int(submit_stats.get("legs_failed_post_only", 0))

    lifecycle_by_symbol: dict[str, dict[str, Any]] = {}
    intended_meta = {str(row.get("symbol") or "").upper(): row for row in intentions if row.get("symbol")}
    for symbol in intended_symbols:
        meta = intended_meta.get(symbol, {})
        inferred_side = "long" if symbol in intended_longs else ("short" if symbol in intended_shorts else None)
        lifecycle_by_symbol[symbol] = {
            "symbol": symbol,
            "basket_role": meta.get("basket_role"),
            "intended_side": meta.get("side") or inferred_side,
            "target_notional_usdt": meta.get("target_notional_usdt"),
            "entry_style": meta.get("entry_style"),
            "status": "not_submitted",
        }

    for row in submitted_rows:
        symbol = str(row.get("symbol") or "").upper()
        if not symbol:
            continue
        lifecycle = lifecycle_by_symbol.setdefault(symbol, {"symbol": symbol})
        lifecycle.update({
            "basket_role": lifecycle.get("basket_role") or row.get("basket_role"),
            "intended_side": lifecycle.get("intended_side") or row.get("side"),
            "status": "pending_entry",
            "entry_order_id": row.get("entry_order_id"),
            "entry_client_order_id": row.get("entry_client_order_id"),
            "entry_expires_at": row.get("entry_expires_at"),
        })

    for row in live_rows:
        symbol = str(row.get("symbol") or "").upper()
        if not symbol:
            continue
        lifecycle = lifecycle_by_symbol.setdefault(symbol, {"symbol": symbol})
        lifecycle.update({
            "basket_role": lifecycle.get("basket_role") or row.get("basket_role"),
            "intended_side": lifecycle.get("intended_side") or row.get("side"),
            "status": "live_open",
            "entry_time": row.get("entry_time"),
            "entry_price": row.get("entry_price"),
            "entry_qty": row.get("entry_qty") or row.get("qty"),
            "entry_notional": row.get("entry_notional"),
            "signal_price": row.get("signal_price"),
            "planned_exit_ts": row.get("planned_exit_ts"),
            "target_notional_usdt": lifecycle.get("target_notional_usdt") or row.get("target_notional_usdt") or row.get("planned_notional"),
            "tp_price": row.get("tp_price"),
            "sl_price": row.get("sl_price"),
            "sl_soft_fallback_active": bool(row.get("sl_soft_fallback_active", False)),
        })

    for row in closed_rows:
        symbol = str(row.get("symbol") or "").upper()
        if not symbol:
            continue
        lifecycle = lifecycle_by_symbol.setdefault(symbol, {"symbol": symbol})
        lifecycle.update({
            "basket_role": lifecycle.get("basket_role") or row.get("basket_role"),
            "intended_side": lifecycle.get("intended_side") or row.get("side"),
            "status": "closed",
            "entry_time": row.get("entry_time"),
            "entry_price": row.get("entry_price"),
            "entry_notional": row.get("entry_notional"),
            "signal_price": row.get("signal_price"),
            "planned_exit_ts": row.get("planned_exit_ts"),
            "target_notional_usdt": lifecycle.get("target_notional_usdt") or row.get("target_notional_usdt") or row.get("planned_notional"),
            "exit_time": row.get("exit_time"),
            "exit_price": row.get("exit_price"),
            "qty": row.get("qty"),
            "exit_reason": row.get("exit_reason"),
            "net_pnl": row.get("net_pnl"),
            "net_return_bps": row.get("net_return_bps"),
        })

    for row in leg_failures:
        symbol = str(row.get("symbol") or "").upper()
        if not symbol:
            continue
        lifecycle = lifecycle_by_symbol.setdefault(symbol, {"symbol": symbol})
        lifecycle.update({
            "basket_role": lifecycle.get("basket_role") or row.get("basket_role"),
            "intended_side": lifecycle.get("intended_side") or row.get("side"),
            "status": str(row.get("reason") or "submit_failed"),
            "failure_reason": row.get("reason"),
            "failure_detail": row.get("error"),
        })

    if submitted_count == intended_count and fallback_taker_count == 0 and failed_count == 0 and intended_count > 0:
        execution_regime = "full_maker"
    elif submitted_count > 0 and fallback_taker_count > 0:
        execution_regime = "mixed_maker_fallback"
    elif submitted_count > 0 and failed_count > 0:
        execution_regime = "partial_submit"
    elif failed_count > 0 and submitted_count == 0:
        execution_regime = "submit_failed"
    else:
        execution_regime = "not_submitted"

    missing_legs_total = int(basket_metrics.get("missing_legs_total", 0) or 0)
    nominal_imbalance_usdt = safe_float(basket_metrics.get("nominal_imbalance_usdt"), 0.0)
    if intended_count == 0:
        basket_safety_classification = "no_basket"
    elif missing_legs_total > 0:
        basket_safety_classification = "incomplete"
    elif nominal_imbalance_usdt > 0:
        basket_safety_classification = "imbalanced"
    else:
        basket_safety_classification = "balanced_complete"

    suppression_summary = _summarize_suppression(suppression_reasons)
    lifecycle_rows = [lifecycle_by_symbol[symbol] for symbol in intended_symbols if symbol in lifecycle_by_symbol]
    pending_count = sum(1 for row in lifecycle_rows if row.get("status") == "pending_entry")
    live_open_count = sum(1 for row in lifecycle_rows if row.get("status") == "live_open")
    closed_count_from_lifecycle = sum(1 for row in lifecycle_rows if row.get("status") == "closed")

    actual_live_basket_net_pnl = 0.0
    actual_live_basket_notional = 0.0
    synthetic_horizon_basket_net_pnl = 0.0
    synthetic_horizon_basket_notional = 0.0
    actual_closed_leg_count = 0
    synthetic_ready_leg_count = 0
    realized_long_notional = 0.0
    realized_short_notional = 0.0
    intended_notional_total = sum(safe_float(row.get("target_notional_usdt"), 0.0) for row in intentions if isinstance(row, dict))
    if intended_notional_total <= 0:
        intended_notional_total = safe_float(basket_metrics.get("gross_nominal_usdt"), 0.0)
    realized_notional_total = 0.0
    submitted_notional_total = 0.0
    total_entry_slippage_bps = 0.0
    entry_slippage_leg_count = 0
    entry_slippage_missing_reasons: list[str] = []

    for row in lifecycle_rows:
        side = str(row.get("intended_side") or row.get("side") or "")
        entry_price = safe_float(row.get("entry_price"), 0.0)
        signal_price = safe_float(row.get("signal_price"), 0.0)
        qty = safe_float(row.get("qty"), safe_float(row.get("entry_qty"), 0.0))
        target_notional = safe_float(row.get("target_notional_usdt"), 0.0)
        entry_notional = safe_float(row.get("entry_notional"), entry_price * qty if entry_price > 0 and qty > 0 else 0.0)
        submitted_like = str(row.get("status") or "") in {"pending_entry", "live_open", "closed"}
        realized_like = str(row.get("status") or "") in {"live_open", "closed"}
        if submitted_like:
            submitted_notional_total += target_notional if target_notional > 0 else entry_notional
        if realized_like:
            realized_notional_total += entry_notional
            if _normalize_side(side) == "long":
                realized_long_notional += entry_notional
            elif _normalize_side(side) == "short":
                realized_short_notional += entry_notional
        if signal_price > 0 and entry_price > 0:
            if _normalize_side(side) == "long":
                slippage_bps = (entry_price / signal_price - 1.0) * 10000.0
            elif _normalize_side(side) == "short":
                slippage_bps = (signal_price / entry_price - 1.0) * 10000.0
            else:
                slippage_bps = 0.0
            row["entry_slippage_bps"] = round(slippage_bps, 6)
            total_entry_slippage_bps += slippage_bps
            entry_slippage_leg_count += 1
        else:
            row["entry_slippage_bps"] = None
            if entry_price <= 0:
                entry_slippage_missing_reasons.append("missing_live_entry_price")
            if signal_price <= 0:
                entry_slippage_missing_reasons.append("missing_signal_price")
        if str(row.get("status") or "") == "closed":
            actual_closed_leg_count += 1
            actual_live_basket_net_pnl += safe_float(row.get("net_pnl"), 0.0)
            actual_live_basket_notional += entry_notional
        entry_time_ts = parse_ts(row.get("entry_time"))
        symbol = str(row.get("symbol") or "").upper()
        if entry_time_ts is None or planned_exit_ts is None or not symbol:
            continue
        horizon_price, horizon_price_ts = _lookup_horizon_price(horizon_panel, symbol, planned_exit_ts)
        if horizon_price is None or horizon_price <= 0:
            continue
        synthetic_ready_leg_count += 1
        row["synthetic_horizon_exit_ts"] = horizon_price_ts
        row["synthetic_horizon_exit_price"] = round(horizon_price, 12)
        if entry_price > 0 and qty > 0:
            gross_pnl = (horizon_price - entry_price) * qty if _normalize_side(side) == "long" else (entry_price - horizon_price) * qty
            avg_notional = ((entry_price * qty) + (horizon_price * qty)) / 2.0 if qty > 0 else 0.0
            fee_usdt = avg_notional * (6.0 / 10000.0) if avg_notional > 0 else 0.0
            net_pnl = gross_pnl - fee_usdt
            net_return_bps = (net_pnl / avg_notional * 10000.0) if avg_notional > 0 else 0.0
            row["synthetic_horizon_net_pnl"] = round(net_pnl, 12)
            row["synthetic_horizon_net_return_bps"] = round(net_return_bps, 6)
            synthetic_horizon_basket_net_pnl += net_pnl
            synthetic_horizon_basket_notional += entry_notional
            if str(row.get("status") or "") == "closed":
                row["exit_policy_delta_bps"] = round(safe_float(row.get("net_return_bps"), 0.0) - net_return_bps, 6)
        else:
            row["synthetic_horizon_net_pnl"] = None
            row["synthetic_horizon_net_return_bps"] = None

    avg_entry_slippage_bps = round((total_entry_slippage_bps / entry_slippage_leg_count), 6) if entry_slippage_leg_count else None
    realized_notional_drift_usdt = realized_notional_total - intended_notional_total
    submitted_notional_drift_usdt = submitted_notional_total - intended_notional_total
    side_notional_imbalance_usdt = abs(realized_long_notional - realized_short_notional)

    economic_empty_reasons: list[str] = []
    if intended_count <= 0:
        economic_empty_reasons.append("no_intended_basket")
    if submitted_count <= 0:
        economic_empty_reasons.append("no_submitted_legs_yet")
    if realized_notional_total <= 0:
        economic_empty_reasons.append("no_live_fills_yet")
    if entry_slippage_leg_count <= 0:
        economic_empty_reasons.extend(sorted(set(entry_slippage_missing_reasons)) or ["no_live_fills_with_signal_price"])

    residual_rows: list[dict[str, Any]] = []
    reconciled_rows: list[dict[str, Any]] = []
    for row in exchange_positions:
        symbol = str(row.get("symbol") or "").upper()
        side = str(row.get("side") or "").lower()
        if not symbol or not side:
            continue
        payload = {
            "symbol": symbol,
            "side": side,
            "qty": row.get("qty"),
            "entry_price": row.get("entry_price"),
            "unrealized_pnl": row.get("unrealized_pnl"),
            "reconciliation_classification": row.get("reconciliation_classification"),
            "matched_local_statuses": row.get("matched_local_statuses"),
            "matched_basket_ids": row.get("matched_basket_ids"),
        }
        classification = str(row.get("reconciliation_classification") or "")
        if classification in {"claimed_by_local_state", "close_conflict_residual"}:
            reconciled_rows.append(payload)
        else:
            residual_rows.append({
                **payload,
                "status": classification or "residual_open_on_exchange",
            })

    return {
        "decision_bar_key": current.get("bar_key"),
        "decision_ts": current.get("decision_ts"),
        "planned_exit_ts": current.get("planned_exit_ts"),
        "intended_basket": {
            "basket_id": derive_basket_id(current),
            "decision": current.get("decision"),
            "gate_on": bool(current.get("gate_on", False)),
            "is_preview": bool(current.get("is_preview", False)),
            "long_symbols": intended_longs,
            "short_symbols": intended_shorts,
            "symbol_count": intended_count,
            "basket_metrics": basket_metrics,
        },
        "basket_safety": {
            "classification": basket_safety_classification,
            "missing_legs_total": missing_legs_total,
            "nominal_imbalance_usdt": round(nominal_imbalance_usdt, 6),
            "side_imbalance_usdt": safe_float(basket_metrics.get("side_imbalance_usdt"), 0.0),
            "target_leg_notional_floor_usdt": basket_metrics.get("target_leg_notional_floor_usdt"),
            "safe_to_compare_economics": bool(intended_count > 0 and missing_legs_total == 0),
            "comparability_classification": "comparable" if intended_count > 0 and missing_legs_total == 0 else "incomplete_non_comparable",
            "require_complete_basket": bool(submit_stats.get("require_complete_basket", False)),
            "materialized_leg_count": len(materialized_symbols),
            "unmaterialized_leg_count": len(unmaterialized_symbols),
        },
        "submitted_basket": {
            "symbols": submitted_symbols,
            "symbol_count": submitted_count,
            "materialized_symbols": materialized_symbols,
            "materialized_symbol_count": len(materialized_symbols),
            "unmaterialized_symbols": unmaterialized_symbols,
            "materialization_gap_count": len(unmaterialized_symbols),
            "failed_symbols": failed_symbols,
            "failed_symbol_count": failed_count,
            "failed_symbol_reasons": failed_symbol_reasons,
            "maker_reject_symbols": _ordered_unique_symbols([{"symbol": symbol} for symbol in maker_reject_symbols]),
            "fallback_taker_symbols": _ordered_unique_symbols([{"symbol": symbol} for symbol in fallback_taker_symbols]),
            "legs_attempted": int(submit_stats.get("legs_attempted", 0)),
            "legs_submitted": int(submit_stats.get("legs_submitted", submitted_count)),
            "legs_submit_failed": int(submit_stats.get("legs_submit_failed", failed_count)),
            "maker_reject_count": maker_reject_count,
            "fallback_taker_count": int(fallback_taker_count),
            "partial_submit_count": 1 if submitted_count > 0 and failed_count > 0 else 0,
            "execution_regime": execution_regime,
        },
        "realized_basket": {
            "live_symbols": live_symbols,
            "live_symbol_count": live_count,
            "closed_symbols": closed_symbols,
            "closed_symbol_count": closed_count,
            "lifecycle": lifecycle_rows,
            "pending_entry_count": pending_count,
            "live_open_count": live_open_count,
            "closed_count": closed_count_from_lifecycle,
        },
        "residual_reconciliation": {
            "exchange_open_count": len(exchange_positions),
            "exchange_reconciled_count": len([row for row in exchange_positions if str(row.get("reconciliation_classification") or "") in {"claimed_by_local_state", "close_conflict_residual"}]),
            "exchange_residual_count": len(residual_rows),
            "exchange_reconciled_positions": [row for row in exchange_positions if str(row.get("reconciliation_classification") or "") in {"claimed_by_local_state", "close_conflict_residual"}],
            "exchange_residual_positions": residual_rows,
            "residual_status": "open_residual_detected" if residual_rows else "fully_reconciled",
        },
        "suppression_summary": suppression_summary,
        "horizon_exit_parity": {
            "status": (
                "ready"
                if synthetic_ready_leg_count > 0 and actual_closed_leg_count > 0
                else ("partial_overlay" if synthetic_ready_leg_count > 0 else "pending_overlay")
            ),
            "planned_exit_ts": current.get("planned_exit_ts"),
            "actual_exit_available": bool(closed_count_from_lifecycle > 0),
            "synthetic_hold_to_horizon_ready": bool(synthetic_ready_leg_count > 0),
            "actual_closed_leg_count": actual_closed_leg_count,
            "synthetic_ready_leg_count": synthetic_ready_leg_count,
            "actual_live_basket_net_pnl": round(actual_live_basket_net_pnl, 12),
            "synthetic_horizon_basket_net_pnl": round(synthetic_horizon_basket_net_pnl, 12),
            "actual_live_basket_return_bps": round((actual_live_basket_net_pnl / actual_live_basket_notional * 10000.0), 6) if actual_live_basket_notional > 0 else None,
            "synthetic_horizon_basket_return_bps": round((synthetic_horizon_basket_net_pnl / synthetic_horizon_basket_notional * 10000.0), 6) if synthetic_horizon_basket_notional > 0 else None,
            "exit_policy_delta_bps": round(((actual_live_basket_net_pnl / actual_live_basket_notional * 10000.0) - (synthetic_horizon_basket_net_pnl / synthetic_horizon_basket_notional * 10000.0)), 6) if actual_live_basket_notional > 0 and synthetic_horizon_basket_notional > 0 else None,
            "notes": [
                "Synthetic horizon uses actual live entry fills and rank213 planned_exit_ts.",
                "Exit-policy drift is kept separate from entry slippage, basket construction, and suppression drift.",
            ],
        },
        "economic_parity": {
            "intended_leg_count": intended_count,
            "submitted_leg_count": submitted_count,
            "missed_leg_count": max(0, intended_count - submitted_count),
            "submitted_ratio": round((submitted_count / intended_count), 6) if intended_count else 0.0,
            "live_ratio": round((live_count / intended_count), 6) if intended_count else 0.0,
            "close_ratio": round((closed_count / intended_count), 6) if intended_count else 0.0,
            "maker_reject_count": maker_reject_count,
            "maker_reject_symbols": _ordered_unique_symbols([{"symbol": symbol} for symbol in maker_reject_symbols]),
            "fallback_taker_count": int(fallback_taker_count),
            "fallback_taker_symbols": _ordered_unique_symbols([{"symbol": symbol} for symbol in fallback_taker_symbols]),
            "partial_submit_count": 1 if submitted_count > 0 and failed_count > 0 else 0,
            "intended_notional_usdt": round(intended_notional_total, 6),
            "submitted_notional_usdt": round(submitted_notional_total, 6),
            "submitted_notional_drift_usdt": round(submitted_notional_drift_usdt, 6),
            "realized_notional_usdt": round(realized_notional_total, 6),
            "realized_notional_drift_usdt": round(realized_notional_drift_usdt, 6),
            "realized_long_notional_usdt": round(realized_long_notional, 6),
            "realized_short_notional_usdt": round(realized_short_notional, 6),
            "side_notional_imbalance_usdt": round(side_notional_imbalance_usdt, 6),
            "avg_entry_slippage_bps": avg_entry_slippage_bps,
            "entry_slippage_leg_count": entry_slippage_leg_count,
            "economic_empty_reasons": sorted(set(economic_empty_reasons)),
            "suppressed_reasons": suppression_reasons,
            "suppressed_reason_count": len(suppression_reasons),
            "suppression_summary": suppression_summary,
            "horizon_parity_pending": not bool(synthetic_ready_leg_count > 0),
            "basket_safety_classification": basket_safety_classification,
            "residual_open_on_exchange_count": len(residual_rows),
        },
    }


def build_intention_rows(current: dict[str, Any], cfg: dict[str, Any], *, run_at_utc: str) -> list[dict[str, Any]]:
    capital = cfg.get("capital", {}) if isinstance(cfg.get("capital"), dict) else {}
    per_leg_default = safe_float(capital.get("desired_leg_notional_usdt", 20.0), 20.0)
    per_leg_min = safe_float(capital.get("min_leg_notional_usdt", per_leg_default), per_leg_default)
    by_symbol = capital.get("desired_leg_notional_usdt_by_symbol", {}) if isinstance(capital.get("desired_leg_notional_usdt_by_symbol"), dict) else {}
    longs = [str(x).upper() for x in current.get("longs", []) if x]
    shorts = [str(x).upper() for x in current.get("shorts", []) if x]
    bar_key = str(current.get("bar_key") or "")
    basket_id = derive_basket_id(current)
    rows: list[dict[str, Any]] = []
    for side, symbols in (("long", longs), ("short", shorts)):
        for idx, symbol in enumerate(symbols, start=1):
            target_leg_notional = max(per_leg_min, safe_float(by_symbol.get(symbol), per_leg_default))
            rows.append({
                "intention_id": f"rank213-{bar_key}-{side}-{idx}",
                "basket_id": basket_id,
                "bar_key": bar_key,
                "decision_ts": current.get("decision_ts"),
                "planned_exit_ts": current.get("planned_exit_ts"),
                "symbol": symbol,
                "side": side,
                "target_notional_usdt": target_leg_notional,
                "basket_role": f"{side}_{idx}",
                "entry_style": "maker_first_then_taker_fallback",
                "dry_run_only": True,
                "generated_at_utc": run_at_utc,
            })
    return rows


def evaluate_rejections(current: dict[str, Any], shadow_status: dict[str, Any], cfg: dict[str, Any], state: dict[str, Any], *, now_ts: pd.Timestamp | None = None, mode: str = "dryrun") -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    safety = cfg.get("safety", {}) if isinstance(cfg.get("safety"), dict) else {}
    basket = cfg.get("basket_controls", {}) if isinstance(cfg.get("basket_controls"), dict) else {}
    execution = cfg.get("execution", {}) if isinstance(cfg.get("execution"), dict) else {}
    warnings: list[dict[str, Any]] = []
    rejections: list[dict[str, Any]] = []
    reasons: list[dict[str, Any]] = []

    bar_key = str(current.get("bar_key") or "")
    longs = [str(x).upper() for x in current.get("longs", []) if x]
    shorts = [str(x).upper() for x in current.get("shorts", []) if x]
    freshness_minutes = compute_freshness_minutes(current.get("decision_ts"), now_ts=now_ts)
    processed = set(str(x) for x in state.get("accepted_bar_keys", []))
    basket_metrics = compute_basket_metrics(current, cfg)
    is_preview = bool(current.get("is_preview", False))
    official_window = evaluate_official_entry_window(current, shadow_status, cfg, now_ts=now_ts or pd.Timestamp(utc_now()))
    conflict_exposures, conflict_warnings = load_conflict_exposures(cfg)
    warnings.extend(conflict_warnings)

    def add_reject(reason: str, detail: dict[str, Any]) -> None:
        row = {
            "timestamp": iso_z(utc_now()),
            "bar_key": bar_key,
            "reason": reason,
            "detail": detail,
        }
        rejections.append(row)
        reasons.append({"reason": reason, **detail})

    current_source_mode = str(shadow_status.get("current_decision_source_mode") or "") if isinstance(shadow_status, dict) else ""
    frame_source_mode = str(shadow_status.get("frame_source_mode") or "") if isinstance(shadow_status, dict) else ""
    if current_source_mode != "recompute_recent":
        add_reject("shadow_provenance_mismatch", {
            "expected_current_decision_source_mode": "recompute_recent",
            "actual_current_decision_source_mode": current_source_mode or None,
            "actual_frame_source_mode": frame_source_mode or None,
        })
    if mode == "dryrun":
        if not bool(safety.get("dry_run_only", False)):
            warnings.append({"kind": "unsafe_mode", "message": "config dry_run_only is False; runner will still refuse to trade."})
        if bool(safety.get("trade_enabled", False)):
            add_reject("trade_enabled_must_remain_False_for_dry_run", {"trade_enabled": True})
    if not bool(current.get("gate_on", False)):
        add_reject("gate_off_flat", {"decision": current.get("decision")})
    if is_preview:
        warnings.append({"kind": "preview_signal", "message": "shadow current decision is a preview basket built from the latest official-close bar; realized hold return is not available yet."})
        add_reject("preview_signal", {"is_preview": True})
    if not bool(official_window.get("eligible", False)):
        add_reject(str(official_window.get("reason") or "entry_window_reject"), dict(official_window.get("detail") or {}))
    if bar_key and bar_key in processed and not bool(official_window.get("eligible", False)):
        add_reject("same_bar_once", {"bar_key": bar_key})
    current_basket = state.get("current_basket") if isinstance(state.get("current_basket"), dict) else None
    current_basket_status = str((current_basket or {}).get("basket_status") or "").lower()
    state_pending_entries = state.get("pending_entries") if isinstance(state.get("pending_entries"), list) else []
    state_live_positions = state.get("live_positions") if isinstance(state.get("live_positions"), list) else []
    active_basket_ids = {
        str(row.get("basket_id") or "")
        for row in [*state_pending_entries, *state_live_positions]
        if isinstance(row, dict) and str(row.get("basket_id") or "")
    }
    active_basket_id = sorted(active_basket_ids)[0] if active_basket_ids else str((current_basket or {}).get("basket_id") or "")
    active_pending_count = sum(1 for row in state_pending_entries if isinstance(row, dict) and str(row.get("basket_id") or "") == active_basket_id)
    active_live_count = sum(1 for row in state_live_positions if isinstance(row, dict) and str(row.get("basket_id") or "") == active_basket_id)
    has_active_basket_ledger = bool(active_pending_count or active_live_count)
    if current_basket_status in {"planned", "pending_entries", "partially_filled", "live", "flattening"} or has_active_basket_ledger:
        add_reject("active_basket_exists", {
            "basket_id": active_basket_id or (current_basket or {}).get("basket_id"),
            "basket_status": current_basket_status if current_basket_status in {"planned", "pending_entries", "partially_filled", "live", "flattening"} else ("live" if active_live_count else "pending_entries"),
            "pending_entry_count": active_pending_count,
            "live_position_count": active_live_count,
        })
    basket_symbols = set(longs + shorts)
    same_side_conflicts: list[dict[str, Any]] = []
    opposite_side_conflicts: list[dict[str, Any]] = []
    for symbol in sorted(basket_symbols):
        intended_side = "long" if symbol in longs else "short"
        exposure = conflict_exposures.get(symbol, {})
        same_side_rows = list(exposure.get(intended_side, []))
        opposite_side = "short" if intended_side == "long" else "long"
        opposite_side_rows = list(exposure.get(opposite_side, []))
        if same_side_rows:
            same_side_conflicts.append({
                "symbol": symbol,
                "intended_side": intended_side,
                "existing_side": intended_side,
                "existing_count": len(same_side_rows),
                "exposures": same_side_rows,
            })
        if opposite_side_rows:
            opposite_side_conflicts.append({
                "symbol": symbol,
                "intended_side": intended_side,
                "existing_side": opposite_side,
                "existing_count": len(opposite_side_rows),
                "exposures": opposite_side_rows,
            })
    if same_side_conflicts:
        add_reject("cross_lane_same_side_busy", {"conflicts": same_side_conflicts, "symbols": [row["symbol"] for row in same_side_conflicts]})
    if opposite_side_conflicts:
        add_reject("cross_lane_opposite_side_conflict", {"conflicts": opposite_side_conflicts, "symbols": [row["symbol"] for row in opposite_side_conflicts]})

    total_legs = len(longs) + len(shorts)
    if total_legs == 0:
        add_reject("empty_basket", {"longs": len(longs), "shorts": len(shorts)})
    if len(longs) != int(basket.get("target_long_legs", 3)):
        add_reject("unexpected_long_leg_count", {"expected": int(basket.get("target_long_legs", 3)), "actual": len(longs)})
    if len(shorts) != int(basket.get("target_short_legs", 3)):
        add_reject("unexpected_short_leg_count", {"expected": int(basket.get("target_short_legs", 3)), "actual": len(shorts)})
    if basket_metrics["filled_legs_total"] < int(basket.get("min_filled_legs_total", 4)):
        add_reject("insufficient_filled_legs_total", {"actual": basket_metrics["filled_legs_total"], "min_required": int(basket.get("min_filled_legs_total", 4))})
    if basket_metrics["long_count"] < int(basket.get("min_filled_legs_per_side", 2)):
        add_reject("insufficient_long_legs", {"actual": basket_metrics["long_count"], "min_required": int(basket.get("min_filled_legs_per_side", 2))})
    if basket_metrics["short_count"] < int(basket.get("min_filled_legs_per_side", 2)):
        add_reject("insufficient_short_legs", {"actual": basket_metrics["short_count"], "min_required": int(basket.get("min_filled_legs_per_side", 2))})
    if basket_metrics["missing_legs_total"] > int(basket.get("max_missing_legs_total", 2)):
        add_reject("too_many_missing_legs", {"actual": basket_metrics["missing_legs_total"], "max_allowed": int(basket.get("max_missing_legs_total", 2))})
    if basket_metrics["nominal_imbalance_usdt"] > safe_float(basket.get("max_nominal_imbalance_usdt", 8.0), 8.0):
        add_reject("nominal_imbalance_too_large", {"actual": basket_metrics["nominal_imbalance_usdt"], "max_allowed": safe_float(basket.get("max_nominal_imbalance_usdt", 8.0), 8.0)})
    if basket_metrics["side_imbalance_usdt"] > safe_float(basket.get("max_side_imbalance_usdt", 6.0), 6.0):
        add_reject("side_imbalance_too_large", {"actual": basket_metrics["side_imbalance_usdt"], "max_allowed": safe_float(basket.get("max_side_imbalance_usdt", 6.0), 6.0)})

    return warnings, rejections, reasons, basket_metrics, official_window


def write_compare_csv(path: Path, *, run_at_utc: str, current: dict[str, Any], accepted: bool, rejection_reasons: list[dict[str, Any]], basket_metrics: dict[str, Any], official_window: dict[str, Any]) -> None:
    ensure_dir(path.parent)
    rows = [{
        "run_at_utc": run_at_utc,
        "bar_key": current.get("bar_key"),
        "decision_ts": current.get("decision_ts"),
        "planned_exit_ts": current.get("planned_exit_ts"),
        "shadow_decision": current.get("decision"),
        "shadow_gate_on": current.get("gate_on"),
        "shadow_longs": ",".join(current.get("longs", [])),
        "shadow_shorts": ",".join(current.get("shorts", [])),
        "live_dryrun_status": "accepted" if accepted else "rejected",
        "official_entry_window_reason": official_window.get("reason"),
        "rejection_reasons": ";".join(sorted({str(x.get('reason')) for x in rejection_reasons})),
        "intent_leg_count": len(current.get("longs", [])) + len(current.get("shorts", [])),
        "long_nominal_usdt": basket_metrics.get("long_nominal_usdt"),
        "short_nominal_usdt": basket_metrics.get("short_nominal_usdt"),
        "gross_nominal_usdt": basket_metrics.get("gross_nominal_usdt"),
        "nominal_imbalance_usdt": basket_metrics.get("nominal_imbalance_usdt"),
        "side_imbalance_usdt": basket_metrics.get("side_imbalance_usdt"),
        "missing_legs_total": basket_metrics.get("missing_legs_total"),
        "target_leg_notional_floor_usdt": basket_metrics.get("target_leg_notional_floor_usdt"),
    }]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    ap = argparse.ArgumentParser(description="Run rank213 live dry-run lane")
    ap.add_argument("--config", default=str(CONFIG_PATH))
    args = ap.parse_args()

    cfg = load_yaml(Path(args.config))
    paths = build_artifact_paths(cfg)
    ensure_dir(paths["root"])
    paths["config_snapshot"].write_text(Path(args.config).read_text(encoding="utf-8"), encoding="utf-8")

    shadow_cfg = cfg.get("shadow_parity", {}) if isinstance(cfg.get("shadow_parity"), dict) else {}
    shadow_status_path = Path(str(shadow_cfg.get("shadow_status_path") or ""))
    shadow_current_path = Path(str(shadow_cfg.get("shadow_current_decision_path") or ""))
    shadow_warnings_path = shadow_status_path.with_name("rank213_shadow_warnings.json") if str(shadow_status_path) else Path()
    shadow_status = read_json(shadow_status_path, {})
    shadow_current = read_json(shadow_current_path, {})
    shadow_warnings = read_json(shadow_warnings_path, [])
    if not isinstance(shadow_status, dict):
        shadow_status = {}
    if not isinstance(shadow_current, dict):
        shadow_current = {}
    if not isinstance(shadow_warnings, list):
        shadow_warnings = []

    run_at_utc = iso_z(utc_now())
    run_now_ts = parse_ts(run_at_utc) or pd.Timestamp.utcnow().tz_localize("UTC")
    state = load_state(paths["state"])
    cooldown = cooldown_active(state, cfg, now_ts=run_now_ts)
    warnings, rejections, rejection_reasons, basket_metrics, official_window = evaluate_rejections(shadow_current, shadow_status, cfg, state, now_ts=run_now_ts)
    if cooldown is not None:
        rejections.append({
            "timestamp": run_at_utc,
            "bar_key": shadow_current.get("bar_key"),
            "reason": "cooldown_active",
            "detail": cooldown,
        })
        rejection_reasons.append({"reason": "cooldown_active", **cooldown})
    accepted = len(rejections) == 0
    intentions = build_intention_rows(shadow_current, cfg, run_at_utc=run_at_utc) if accepted else []
    orders: list[dict[str, Any]] = []
    submit_stats = {
        "legs_attempted": len(intentions),
        "legs_submitted": 0,
        "legs_submit_failed": 0,
        "legs_failed_post_only": 0,
    }

    merged_intentions = append_recent_json(paths["intentions"], intentions, tail=120, key_fields=["intention_id"])
    merged_rejections = append_recent_json(paths["rejections"], rejections, tail=180, key_fields=["bar_key", "reason"])
    save_json(paths["orders"], orders)
    save_json(paths["warnings"], warnings)

    write_compare_csv(paths["compare"], run_at_utc=run_at_utc, current=shadow_current, accepted=accepted, rejection_reasons=rejection_reasons, basket_metrics=basket_metrics, official_window=official_window)
    basket_parity = build_basket_parity_payload(
        current=shadow_current,
        basket_metrics=basket_metrics,
        intentions=intentions,
        submitted_rows=[],
        live_rows=[],
        closed_rows=[],
        leg_failures=[],
        submit_stats=submit_stats,
        fallback_taker_count=0,
        suppression_reasons=rejection_reasons,
        exchange_positions=[],
    )
    compare_summary = {
        "generated_at_utc": run_at_utc,
        "scope": "rank213 dry-run live vs shadow current-decision parity",
        "accepted": accepted,
        "rejection_count": len(rejections),
        "intentions_created": len(intentions),
        "shadow_bar_key": shadow_current.get("bar_key"),
        "shadow_decision": shadow_current.get("decision"),
        "shadow_gate_on": shadow_current.get("gate_on"),
        "official_entry_window": official_window,
        "basket_metrics": basket_metrics,
        "execution_audit": {
            "mode": "dryrun_only",
            "bridge_connected": False,
            "maker_first_configured": bool(cfg.get("execution", {}).get("maker_first", True)),
            "fallback_to_taker_configured": bool(cfg.get("execution", {}).get("allow_fallback_to_taker", True)),
            "preview_signal": bool(shadow_current.get("is_preview", False)),
            "maker_fill_count": 0,
            "fallback_taker_count": 0,
            "partial_basket_count": 0,
            "missed_leg_count": basket_parity["economic_parity"]["missed_leg_count"],
        },
        "basket_parity": basket_parity,
    }
    save_json(paths["compare_summary"], compare_summary)

    event = {
        "event_at_utc": run_at_utc,
        "runner": "rank213_live_dryrun",
        "event_kind": "dryrun_intentions_created" if accepted else "dryrun_rejected",
        "bar_key": shadow_current.get("bar_key"),
        "decision_ts": shadow_current.get("decision_ts"),
        "accepted": accepted,
        "intentions_created": len(intentions),
        "rejections": rejection_reasons,
    }
    append_jsonl(paths["events"], event)

    accepted_bar_keys = [str(x) for x in state.get("accepted_bar_keys", []) if x]
    bar_key = str(shadow_current.get("bar_key") or "")
    if accepted and bar_key and bar_key not in accepted_bar_keys:
        accepted_bar_keys.append(bar_key)
    accepted_bar_keys = accepted_bar_keys[-256:]
    new_state = {
        "runner": "rank213_live_dryrun",
        "last_run_at_utc": run_at_utc,
        "last_bar_key": bar_key or None,
        "last_decision_ts": shadow_current.get("decision_ts"),
        "last_event_kind": event["event_kind"],
        "accepted_last_run": accepted,
        "accepted_bar_keys": accepted_bar_keys,
        "last_rejection_at_utc": run_at_utc if rejections else state.get("last_rejection_at_utc"),
        "last_rejection_reasons": [str(x.get("reason")) for x in rejection_reasons],
    }
    save_json(paths["state"], new_state)

    basket_id = derive_basket_id(shadow_current)
    basket_status = "planned" if accepted else "aborted"
    basket_runtime = {
        "basket_id": basket_id,
        "basket_status": basket_status,
        "bar_key": shadow_current.get("bar_key"),
        "decision_ts": shadow_current.get("decision_ts"),
        "planned_exit_ts": shadow_current.get("planned_exit_ts"),
        "entry_window": official_window,
        "legs_planned": len(intentions),
        "legs_pending": len(intentions) if accepted else 0,
        "legs_live": 0,
        "legs_closed": 0,
        "legs_failed": 0,
        "pending_entry_symbols": [row.get("symbol") for row in intentions],
        "live_symbols": [],
        "closed_symbols": [],
        "flatten_reason": None,
        "runtime_mode": "dryrun_preview",
        "bridge_connected": False,
    }

    new_state["current_basket"] = basket_runtime if basket_id else None

    status = {
        "strategy_id": cfg.get("meta", {}).get("strategy_id"),
        "mode": "live_dryrun",
        "runner_script": "scripts/run_rank213_largecap_xs_jump_veto_live_dryrun.py",
        "config_path": str(Path(args.config).relative_to(ROOT)),
        "system_health": "ok",
        "trade_enabled": False,
        "dry_run_only": True,
        "last_run_utc": run_at_utc,
        "shadow_decision_ts": shadow_current.get("decision_ts"),
        "shadow_bar_key": shadow_current.get("bar_key"),
        "shadow_gate_on": shadow_current.get("gate_on"),
        "intentions_created": len(intentions),
        "recent_reject_count": len(merged_rejections),
        "recent_intention_count": len(merged_intentions),
        "accepted": accepted,
        "official_entry_window": official_window,
        "basket_runtime": basket_runtime,
        "basket_metrics": basket_metrics,
        "basket_parity": basket_parity,
        "cooldown": cooldown,
        "notes": [
            "This lane is dry-run only and never sends orders.",
            "It consumes rank213 shadow current decision and emits intention/rejection/audit artifacts.",
            "Live capital must remain disabled until shadow parity and execution audit are stable.",
        ],
    }
    save_json(paths["status"], status)

    operator_packet = {
        "generated_at_utc": run_at_utc,
        "strategy_id": cfg.get("meta", {}).get("strategy_id"),
        "operator_note": cfg.get("operator", {}).get("note"),
        "readiness_note": cfg.get("operator", {}).get("readiness_note"),
        "shadow_status": shadow_status,
        "shadow_current_decision": shadow_current,
        "shadow_warnings_visible": shadow_warnings,
        "dryrun_status": status,
        "basket_metrics": basket_metrics,
        "basket_runtime": basket_runtime,
        "basket_parity": basket_parity,
        "cooldown": cooldown,
        "shadow_current_is_preview": bool(shadow_current.get("is_preview", False)),
        "dryrun_rejections": rejections,
        "dryrun_warnings": warnings,
    }
    save_json(paths["operator_packet"], operator_packet)

    run_summary = {
        "generated_at_utc": run_at_utc,
        "runner": "rank213_live_dryrun",
        "config_path": str(Path(args.config).relative_to(ROOT)),
        "accepted": accepted,
        "intentions_created": len(intentions),
        "rejections": len(rejections),
        "status_path": str(paths["status"].relative_to(ROOT)),
        "state_path": str(paths["state"].relative_to(ROOT)),
        "intentions_path": str(paths["intentions"].relative_to(ROOT)),
        "rejections_path": str(paths["rejections"].relative_to(ROOT)),
        "warnings_path": str(paths["warnings"].relative_to(ROOT)),
        "compare_path": str(paths["compare"].relative_to(ROOT)),
        "compare_summary_path": str(paths["compare_summary"].relative_to(ROOT)),
        "operator_packet_path": str(paths["operator_packet"].relative_to(ROOT)),
    }
    save_json(paths["run_summary"], run_summary)
    print(json.dumps(run_summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
