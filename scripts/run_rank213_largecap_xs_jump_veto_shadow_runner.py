#!/usr/bin/env python3
from __future__ import annotations

"""Rank213 raw-bar shadow runner scaffold.

This runner is intentionally separated from the frozen-seed paper lane:
- it always recomputes a recent raw-bar window from cached/downloaded 15m bars
- formal gate is always applied from the frozen formal strategy definition
- outputs runner-grade shadow artifacts for status / state / recent decisions / operator packet / html

It is a shadow/audit lane only. It does not place trades.
"""

import argparse
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank213_largecap_xs_jump_veto"
SITE_PATH = ROOT / "reports" / "site" / "paper" / "rank213_largecap_xs_jump_veto_shadow_runner.html"
ADMISSION_SUMMARY_PATH = ROOT / "reports" / "artifacts" / "optimization_loop" / "rank213_p2_admission_20260328" / "summary.json"
READINESS_PATH = ART_DIR / "rank213_readiness_note_summary.json"
FORMAL_SUMMARY_PATH = ART_DIR / "rank213_formal_threeway_backtest_summary.json"

STATE_PATH = ART_DIR / "rank213_shadow_state.json"
STATUS_PATH = ART_DIR / "rank213_shadow_status.json"
RUN_SUMMARY_PATH = ART_DIR / "rank213_shadow_last_run_summary.json"
CURRENT_DECISION_PATH = ART_DIR / "rank213_shadow_current_decision.json"
RECENT_DECISIONS_PATH = ART_DIR / "rank213_shadow_recent_decisions.csv"
OPERATOR_PACKET_PATH = ART_DIR / "rank213_shadow_operator_packet.json"
WARNINGS_PATH = ART_DIR / "rank213_shadow_warnings.json"
RECOMPUTED_DETAIL_PATH = ART_DIR / "rank213_shadow_recent_recomputed_detail.csv"
EVENTS_PATH = ART_DIR / "rank213_shadow_events.jsonl"

RUNNER_MODE = "raw_bar_shadow_formal_gate"
RUNNER_NAME = "rank213_largecap_xs_jump_veto_shadow_runner"
VARIANT = "f64_h12_floor150_mult2p0"
TAIL_ROWS = 96
GATE_LOOKBACK_DAYS = 30
MIN_RECOMPUTE_DAYS = 45
INCREMENTAL_OVERLAP_DAYS = 2
PANEL_WARMUP_DAYS = 2
FRESHNESS_WARN_MINUTES = 20
MAX_EVENT_ROWS = 200
MAX_CONSUMED_BAR_KEYS = 256


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


asof_mod = load_module(ROOT / "scripts" / "build_rank213_asof_universe_long_history_review.py", "rank213_shadow_asof_mod")
formal_mod = load_module(ROOT / "scripts" / "build_rank213_formal_strategy_pack.py", "rank213_shadow_formal_mod")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_jsonl(path: Path, payloads: list[dict[str, Any]], *, keep_last: int) -> None:
    ensure_dir(path.parent)
    rows: list[str] = []
    if path.exists():
        rows = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    rows.extend(json.dumps(item, ensure_ascii=False) for item in payloads)
    if keep_last > 0 and len(rows) > keep_last:
        rows = rows[-keep_last:]
    text = "\n".join(rows)
    path.write_text((text + "\n") if text else "", encoding="utf-8")


def iso_z(ts: Any) -> str | None:
    if ts is None or pd.isna(ts):
        return None
    return pd.to_datetime(ts, utc=True).strftime("%Y-%m-%dT%H:%M:%SZ")


def normalize_for_csv(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[col]):
            out[col] = out[col].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return out


def load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return {}
    raw = read_json(STATE_PATH)
    return raw if isinstance(raw, dict) else {}


def trim_consumed_bar_keys(keys: list[str]) -> list[str]:
    cleaned = [str(k) for k in keys if k]
    return cleaned[-MAX_CONSUMED_BAR_KEYS:]


def compute_freshness_minutes(ts: Any, *, now: datetime | None = None) -> float | None:
    if ts is None or pd.isna(ts):
        return None
    ref = now or utc_now()
    return max(0.0, (pd.Timestamp(ref) - pd.Timestamp(ts)).total_seconds() / 60.0)


def is_official_bar(ts: Any) -> bool:
    if ts is None or pd.isna(ts):
        return False
    stamp = pd.Timestamp(ts)
    return int(stamp.minute) % 15 == 0 and int(stamp.second) == 0


def load_symbols() -> list[str]:
    payload = read_json(ADMISSION_SUMMARY_PATH)
    symbols = payload.get("symbols", [])
    return [str(s).upper() for s in symbols]


def load_readiness() -> dict[str, Any]:
    return read_json(READINESS_PATH) if READINESS_PATH.exists() else {}


def load_formal_summary() -> dict[str, Any]:
    return read_json(FORMAL_SUMMARY_PATH) if FORMAL_SUMMARY_PATH.exists() else {}


def build_latest_live_asof_row(panel: pd.DataFrame, symbols: list[str], *, now_ts: pd.Timestamp | None = None) -> dict[str, Any] | None:
    if panel.empty:
        return None
    idx = panel.index
    if len(idx) <= asof_mod.FORMATION_BARS:
        return None

    ref_now = now_ts if now_ts is not None else pd.Timestamp.utcnow()
    ref_now = ref_now.tz_convert("UTC") if ref_now.tzinfo else ref_now.tz_localize("UTC")
    latest_closed_bar_open_ts = ref_now.floor(f"{int(asof_mod.BAR_MINUTES)}min") - pd.Timedelta(minutes=int(asof_mod.BAR_MINUTES))

    for i in range(len(idx) - 1, asof_mod.FORMATION_BARS - 1, -1):
        ts = idx[i]
        if ts > latest_closed_bar_open_ts:
            continue
        decision_ts = ts + pd.Timedelta(minutes=int(asof_mod.BAR_MINUTES))
        exit_ts = decision_ts + pd.Timedelta(minutes=int(asof_mod.HOLD_BARS) * int(asof_mod.BAR_MINUTES))

        eligible: list[str] = []
        for sym in symbols:
            onboard = pd.to_datetime(asof_mod.SYMBOL_ONBOARD_DATE_MS[sym], unit="ms", utc=True)
            if ts < onboard:
                continue
            close_window = panel[sym].iloc[i - asof_mod.FORMATION_BARS:i + 1]
            if close_window.isna().any():
                continue
            eligible.append(sym)

        if len(eligible) < asof_mod.TOP_N + asof_mod.BOTTOM_N:
            continue

        close_window = panel[eligible].iloc[i - asof_mod.FORMATION_BARS:i + 1]
        hist = close_window.pct_change().iloc[1:]
        if hist.isna().any().any():
            continue

        cumret = close_window.iloc[-1] / close_window.iloc[0] - 1.0
        universe_med = hist.abs().max().median()
        veto_threshold = max(asof_mod.VETO_FLOOR, asof_mod.VETO_MULT * float(universe_med if pd.notna(universe_med) else 0.0))

        rank = cumret.sort_values()
        longs = rank.index[-asof_mod.TOP_N:].tolist()[::-1]
        plain_shorts = rank.index[:asof_mod.BOTTOM_N].tolist()
        short_info = [(sym, float(hist[sym].max())) for sym in plain_shorts]
        eligible_shorts = [sym for sym, mx in short_info if pd.notna(mx) and mx <= veto_threshold]
        vetoed = [sym for sym, mx in short_info if pd.notna(mx) and mx > veto_threshold]
        refill = [sym for sym in rank.index if sym not in longs and sym not in plain_shorts]

        veto_shorts = eligible_shorts.copy()
        for sym in refill:
            if len(veto_shorts) >= asof_mod.BOTTOM_N:
                break
            mx = float(hist[sym].max())
            if pd.notna(mx) and mx <= veto_threshold:
                veto_shorts.append(sym)
        if len(veto_shorts) < asof_mod.BOTTOM_N:
            for sym in rank.index:
                if sym not in longs and sym not in veto_shorts:
                    veto_shorts.append(sym)
                if len(veto_shorts) >= asof_mod.BOTTOM_N:
                    break

        veto_turnover = 1.0 + (len(set(veto_shorts) ^ set(plain_shorts)) / 6.0)
        return {
            "timestamp_ts": decision_ts,
            "exit_ts": exit_ts,
            "eligible_universe_size": int(len(eligible)),
            "eligible_symbols": ",".join(eligible),
            "plain_longs": ",".join(longs),
            "plain_shorts": ",".join(plain_shorts),
            "veto_shorts": ",".join(veto_shorts),
            "veto_count": int(len(vetoed)),
            "veto_threshold": float(veto_threshold),
            "plain_gross": np.nan,
            "veto_gross": np.nan,
            "plain_turnover_x": 1.0,
            "veto_turnover_x": float(veto_turnover),
            "long_price_contrib": np.nan,
            "plain_short_price_contrib": np.nan,
            "veto_short_price_contrib": np.nan,
            "btc_cumret": float(cumret["BTCUSDT"]) if "BTCUSDT" in cumret.index else np.nan,
            "universe_cumret_mean": float(cumret.mean()),
            "universe_cumret_std": float(cumret.std()),
            "universe_cumret_iqr": float(cumret.quantile(0.75) - cumret.quantile(0.25)),
            "universe_realized_vol_median": float(hist.std().median()),
            "timestamp": decision_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "plain_net": np.nan,
            "veto_net": np.nan,
            "year": ts.strftime("%Y"),
            "month": ts.strftime("%Y-%m"),
        }
    return None


def load_cached_detail() -> pd.DataFrame:
    if not RECOMPUTED_DETAIL_PATH.exists():
        return pd.DataFrame()
    try:
        cached = pd.read_csv(RECOMPUTED_DETAIL_PATH)
    except Exception:  # noqa: BLE001
        return pd.DataFrame()
    if cached.empty:
        return cached
    for col in ["timestamp_ts", "exit_ts"]:
        if col in cached.columns:
            cached[col] = pd.to_datetime(cached[col], utc=True, errors="coerce")
    return cached.dropna(subset=["timestamp_ts"]).sort_values("timestamp_ts").drop_duplicates(subset=["timestamp_ts"], keep="last").reset_index(drop=True)


def finalize_detail_frame(detail: pd.DataFrame, *, latest_live_row: dict[str, Any] | None, keep_start_ts: pd.Timestamp) -> pd.DataFrame:
    out = detail.copy()
    if out.empty and latest_live_row is None:
        raise RuntimeError("rank213 shadow runner recompute produced no as-of rows")
    if out.empty:
        out = pd.DataFrame([latest_live_row])
    elif latest_live_row is not None:
        latest_ts = pd.to_datetime(latest_live_row["timestamp_ts"], utc=True)
        out = out[out["timestamp_ts"] != latest_ts]
        out = pd.concat([out, pd.DataFrame([latest_live_row])], ignore_index=True)
    out["timestamp_ts"] = pd.to_datetime(out["timestamp_ts"], utc=True)
    out["exit_ts"] = pd.to_datetime(out["exit_ts"], utc=True)
    out = out[out["timestamp_ts"] >= keep_start_ts].sort_values("timestamp_ts").drop_duplicates(subset=["timestamp_ts"], keep="last").reset_index(drop=True)
    normalize_for_csv(out).to_csv(RECOMPUTED_DETAIL_PATH, index=False)
    return out


def recompute_recent_asof_detail(*, recent_days: int) -> tuple[pd.DataFrame, dict[str, Any]]:
    symbols = load_symbols()
    end_ts = pd.Timestamp.utcnow().floor("15min")
    span_days = max(MIN_RECOMPUTE_DAYS, recent_days + GATE_LOOKBACK_DAYS + 2)
    start_ts = end_ts - pd.Timedelta(days=span_days)
    panel, availability = asof_mod.build_panel(symbols, start_ts, end_ts)
    detail = asof_mod.run_asof_backtest(panel, symbols)
    latest_live_row = build_latest_live_asof_row(panel, symbols, now_ts=end_ts)
    detail = finalize_detail_frame(detail, latest_live_row=latest_live_row, keep_start_ts=start_ts)
    return detail, {
        "mode": "recompute_recent",
        "recent_days": int(recent_days),
        "span_days": int(span_days),
        "recomputed_detail_csv": str(RECOMPUTED_DETAIL_PATH.relative_to(ROOT)),
        "availability_rows": int(len(availability)),
        "panel_start_utc": iso_z(start_ts),
        "panel_end_utc": iso_z(end_ts),
        "latest_live_row_ts": iso_z(latest_live_row["timestamp_ts"]) if latest_live_row is not None else None,
    }


def recompute_incremental_asof_detail(*, recent_days: int) -> tuple[pd.DataFrame, dict[str, Any]]:
    symbols = load_symbols()
    end_ts = pd.Timestamp.utcnow().floor("15min")
    span_days = max(MIN_RECOMPUTE_DAYS, recent_days + GATE_LOOKBACK_DAYS + 2)
    keep_start_ts = end_ts - pd.Timedelta(days=span_days)
    cached = load_cached_detail()
    if cached.empty:
        return recompute_recent_asof_detail(recent_days=recent_days)
    cached = cached[cached["timestamp_ts"] >= keep_start_ts].copy()
    if cached.empty:
        return recompute_recent_asof_detail(recent_days=recent_days)

    last_cached_ts = pd.to_datetime(cached["timestamp_ts"].max(), utc=True)
    update_start_ts = max(keep_start_ts, last_cached_ts - pd.Timedelta(days=INCREMENTAL_OVERLAP_DAYS))
    panel_start_ts = update_start_ts - pd.Timedelta(days=PANEL_WARMUP_DAYS)

    panel, availability = asof_mod.build_panel(symbols, panel_start_ts, end_ts)
    detail_tail = asof_mod.run_asof_backtest(panel, symbols)
    latest_live_row = build_latest_live_asof_row(panel, symbols, now_ts=end_ts)
    if detail_tail.empty and latest_live_row is None:
        return recompute_recent_asof_detail(recent_days=recent_days)

    if not detail_tail.empty:
        detail_tail["timestamp_ts"] = pd.to_datetime(detail_tail["timestamp_ts"], utc=True)
        detail_tail = detail_tail[detail_tail["timestamp_ts"] >= update_start_ts].copy()
    base = cached[cached["timestamp_ts"] < update_start_ts].copy()
    merged = pd.concat([base, detail_tail], ignore_index=True) if not detail_tail.empty else base
    detail = finalize_detail_frame(merged, latest_live_row=latest_live_row, keep_start_ts=keep_start_ts)
    return detail, {
        "mode": "incremental_recent",
        "recent_days": int(recent_days),
        "span_days": int(span_days),
        "incremental_overlap_days": int(INCREMENTAL_OVERLAP_DAYS),
        "panel_warmup_days": int(PANEL_WARMUP_DAYS),
        "recomputed_detail_csv": str(RECOMPUTED_DETAIL_PATH.relative_to(ROOT)),
        "availability_rows": int(len(availability)),
        "cached_rows_before": int(len(cached)),
        "detail_tail_rows": int(len(detail_tail)) if not detail_tail.empty else 0,
        "merged_rows": int(len(detail)),
        "update_start_utc": iso_z(update_start_ts),
        "panel_start_utc": iso_z(panel_start_ts),
        "panel_end_utc": iso_z(end_ts),
        "latest_live_row_ts": iso_z(latest_live_row["timestamp_ts"]) if latest_live_row is not None else None,
    }


def apply_shadow_columns(gated: pd.DataFrame, *, is_preview: bool) -> pd.DataFrame:
    out = gated.sort_values("timestamp_ts").reset_index(drop=True).copy()
    out["shadow_longs"] = out["plain_longs"].fillna("")
    out["shadow_shorts"] = np.where(out["gate_on"].fillna(False), out["veto_shorts"].fillna(""), "")
    out["shadow_decision"] = np.where(out["gate_on"].fillna(False), "baseline_plus_veto_plus_gate", "flat_gate_off")
    out["shadow_has_realized_hold_return"] = False if is_preview else ~out["veto_net"].isna()
    out["shadow_is_preview"] = bool(is_preview)
    out["shadow_net_ret"] = np.where(
        out["shadow_has_realized_hold_return"],
        np.where(out["gate_on"].fillna(False), pd.to_numeric(out["veto_net"], errors="coerce"), 0.0),
        np.nan,
    )
    out["shadow_turnover_x"] = np.where(out["gate_on"].fillna(False), pd.to_numeric(out["veto_turnover_x"], errors="coerce"), 0.0)
    out["shadow_net_bps"] = pd.to_numeric(out["shadow_net_ret"], errors="coerce") * 10000.0
    out["bar_key"] = out["timestamp_ts"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return out


def build_recent_preview_rows(*, recent_days: int, existing_frame: pd.DataFrame, now_ts: pd.Timestamp) -> pd.DataFrame:
    if existing_frame.empty:
        return pd.DataFrame()
    realized = existing_frame[existing_frame["shadow_has_realized_hold_return"].fillna(False)].copy()
    last_realized_ts = pd.to_datetime(realized["timestamp_ts"].max(), utc=True) if not realized.empty else pd.NaT
    latest_existing_ts = pd.to_datetime(existing_frame["timestamp_ts"].max(), utc=True)
    if pd.isna(last_realized_ts) or pd.isna(latest_existing_ts) or latest_existing_ts <= last_realized_ts:
        return pd.DataFrame()

    preview_decision_ts = pd.date_range(
        start=last_realized_ts + pd.Timedelta(minutes=int(asof_mod.BAR_MINUTES)),
        end=latest_existing_ts,
        freq=f'{int(asof_mod.BAR_MINUTES)}min',
        tz='UTC',
    )
    if len(preview_decision_ts) == 0:
        return pd.DataFrame()

    symbols = load_symbols()
    preview_start_ts = pd.to_datetime(preview_decision_ts.min(), utc=True)
    panel_start = preview_start_ts - pd.Timedelta(days=PANEL_WARMUP_DAYS)
    panel_end = now_ts.floor('15min')
    asof_panel, _ = asof_mod.build_panel(symbols, panel_start, panel_end)
    if asof_panel.empty:
        return pd.DataFrame()

    preview_rows: list[dict[str, Any]] = []
    for decision_ts in preview_decision_ts:
        row = build_latest_live_asof_row(asof_panel, symbols, now_ts=decision_ts)
        if row is None:
            continue
        built_ts = pd.to_datetime(row.get("timestamp_ts"), utc=True, errors="coerce")
        if pd.isna(built_ts) or built_ts != decision_ts:
            continue
        preview_rows.append(row)
    if not preview_rows:
        return pd.DataFrame()

    preview_detail = pd.DataFrame(preview_rows)
    preview_detail["timestamp_ts"] = pd.to_datetime(preview_detail["timestamp_ts"], utc=True)
    preview_ts_set = set(preview_detail["timestamp_ts"])

    freeze = formal_mod.build_freeze_summary(refreeze=False)
    history_context = realized.copy()
    gate_input = pd.concat([history_context, preview_detail], ignore_index=True)
    gate_input = gate_input.sort_values("timestamp_ts").drop_duplicates(subset=["timestamp_ts"], keep="last").reset_index(drop=True)
    gated_all, _ = formal_mod.apply_frozen_gate(gate_input, freeze)
    gated_preview = gated_all[gated_all["timestamp_ts"].isin(preview_ts_set)].copy()
    return apply_shadow_columns(gated_preview, is_preview=True)


def finalize_shadow_frame(detail: pd.DataFrame, source_meta: dict[str, Any], *, recent_days: int) -> tuple[pd.DataFrame, dict[str, Any]]:
    freeze = formal_mod.build_freeze_summary(refreeze=False)
    gated, gate_snapshot = formal_mod.apply_frozen_gate(detail, freeze)
    gated = apply_shadow_columns(gated, is_preview=False)
    preview_rows = build_recent_preview_rows(recent_days=recent_days, existing_frame=gated, now_ts=pd.Timestamp.utcnow())
    if not preview_rows.empty:
        realized = gated[gated["shadow_has_realized_hold_return"].fillna(False)].copy()
        gated = pd.concat([realized, preview_rows], ignore_index=True).sort_values("timestamp_ts").drop_duplicates(subset=["timestamp_ts"], keep="last").reset_index(drop=True)
    return gated, {**source_meta, "gate_snapshot": gate_snapshot, "freeze_summary": freeze}


def build_shadow_frame(*, recent_days: int) -> tuple[pd.DataFrame, dict[str, Any]]:
    detail, source_meta = recompute_recent_asof_detail(recent_days=recent_days)
    source_meta = {
        **source_meta,
        "frame_source_mode": source_meta.get("mode"),
        "current_decision_source_mode": source_meta.get("mode"),
        "current_decision_recent_days": int(recent_days),
    }
    return finalize_shadow_frame(detail, source_meta, recent_days=recent_days)


def build_recent_decisions(frame: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "timestamp_ts",
        "exit_ts",
        "bar_key",
        "shadow_decision",
        "gate_on",
        "gate_votes",
        "gate_valid_rules",
        "gate_needed_votes",
        "shadow_longs",
        "shadow_shorts",
        "plain_longs",
        "veto_shorts",
        "veto_count",
        "veto_threshold",
        "eligible_universe_size",
        "shadow_turnover_x",
        "shadow_net_bps",
        "shadow_is_preview",
        "shadow_has_realized_hold_return",
    ]
    recent = frame[cols].tail(TAIL_ROWS).copy()
    return recent.reset_index(drop=True)


def build_current_decision(frame: pd.DataFrame, source_meta: dict[str, Any] | None = None) -> dict[str, Any]:
    if frame.empty:
        return {"state": "no_decision_rows"}
    row = frame.iloc[-1]
    source_meta = source_meta or {}
    has_realized_hold_return = bool(row.get("shadow_has_realized_hold_return", False))
    return {
        "decision_ts": iso_z(row["timestamp_ts"]),
        "planned_exit_ts": iso_z(row["exit_ts"]),
        "bar_key": row["bar_key"],
        "decision": row["shadow_decision"],
        "gate_on": bool(row["gate_on"]),
        "gate_votes": int(row["gate_votes"]),
        "gate_valid_rules": int(row["gate_valid_rules"]),
        "gate_needed_votes": int(row["gate_needed_votes"]),
        "longs": [x for x in str(row["shadow_longs"] or "").split(",") if x],
        "shorts": [x for x in str(row["shadow_shorts"] or "").split(",") if x],
        "veto_count": int(row["veto_count"]),
        "veto_threshold": float(row["veto_threshold"]),
        "eligible_universe_size": int(row["eligible_universe_size"]),
        "shadow_turnover_x": float(row["shadow_turnover_x"]),
        "shadow_net_bps": None if pd.isna(row["shadow_net_bps"]) else float(row["shadow_net_bps"]),
        "source_mode": source_meta.get("mode"),
        "frame_source_mode": source_meta.get("frame_source_mode") or source_meta.get("mode"),
        "current_decision_source_mode": source_meta.get("current_decision_source_mode") or source_meta.get("mode"),
        "is_preview": False,
        "has_realized_hold_return": has_realized_hold_return,
    }


def build_warnings(frame: pd.DataFrame, readiness: dict[str, Any], source_meta: dict[str, Any], *, freshness_minutes: float | None, latest_bar_consumed: bool) -> list[dict[str, Any]]:
    warnings: list[dict[str, Any]] = []
    wa = readiness.get("window_availability", {}) if isinstance(readiness.get("window_availability"), dict) else {}
    if wa.get("frozen_1Y") is False:
        warnings.append({
            "kind": "readiness_scope",
            "message": "frozen current-universe 1Y readiness remains unavailable; as-of long-window evidence must be treated separately.",
        })
    gate_off_rate = float((~frame["gate_on"].fillna(False)).mean()) if not frame.empty else 0.0
    if gate_off_rate > 0:
        warnings.append({
            "kind": "gate_activity",
            "message": f"formal gate is OFF on {gate_off_rate:.2%} of available rows in the loaded shadow frame.",
        })
    mode = str(source_meta.get("mode") or "unknown")
    mode_desc = {
        "incremental_recent": "runner refreshed a rolling recent ledger incrementally and published current/recent shadow artifacts from the same frame.",
        "recompute_recent": "runner recomputed recent raw-bar decisions and published current/recent shadow artifacts from the same frame.",
    }.get(mode, f"runner refreshed shadow artifacts from source_mode={mode}.")
    warnings.append({
        "kind": "source_mode",
        "message": mode_desc,
    })
    if freshness_minutes is not None and freshness_minutes > FRESHNESS_WARN_MINUTES:
        warnings.append({
            "kind": "stale_signal",
            "message": f"latest shadow decision is stale by {freshness_minutes:.1f} minutes relative to current UTC.",
        })
    if latest_bar_consumed:
        warnings.append({
            "kind": "same_bar_once",
            "message": "latest official decision bar was already consumed in state; runner refreshed artifacts without replaying a new bar.",
        })
    return warnings


def build_status(frame: pd.DataFrame, current: dict[str, Any], warnings: list[dict[str, Any]], source_meta: dict[str, Any], *, freshness_minutes: float | None, state: dict[str, Any], bar_already_consumed_before_run: bool, did_consume_latest_bar_this_run: bool) -> dict[str, Any]:
    latest_ts = frame["timestamp_ts"].max() if not frame.empty else None
    latest_exit = frame["exit_ts"].max() if not frame.empty else None
    return {
        "candidate_id": "rank213_largecap_xs_jump_veto",
        "candidate_rank": 213,
        "stage": "shadow_runner_live",
        "wiring_status": "shadow_scaffold_connected",
        "runner_mode": RUNNER_MODE,
        "runner_script": f"scripts/{Path(__file__).name}",
        "variant": VARIANT,
        "signal_timeframe": "15m",
        "formation_bars": 64,
        "hold_bars": 12,
        "latest_decision_ts": iso_z(latest_ts),
        "latest_planned_exit_ts": iso_z(latest_exit),
        "recent_decision_rows": int(min(len(frame), TAIL_ROWS)),
        "shadow_decision": current.get("decision"),
        "gate_on": current.get("gate_on"),
        "latest_longs": ",".join(current.get("longs", [])),
        "latest_shorts": ",".join(current.get("shorts", [])),
        "warnings_count": int(len(warnings)),
        "source_mode": source_meta.get("mode"),
        "frame_source_mode": source_meta.get("frame_source_mode") or source_meta.get("mode"),
        "current_decision_source_mode": source_meta.get("current_decision_source_mode") or source_meta.get("mode"),
        "current_decision_recent_days": source_meta.get("current_decision_recent_days"),
        "current_decision_panel_start_utc": source_meta.get("panel_start_utc"),
        "current_decision_panel_end_utc": source_meta.get("panel_end_utc"),
        "current_decision_latest_live_row_ts": source_meta.get("latest_live_row_ts"),
        "latest_bar_consumed": bool(did_consume_latest_bar_this_run),
        "bar_already_consumed_before_run": bool(bar_already_consumed_before_run),
        "did_consume_latest_bar_this_run": bool(did_consume_latest_bar_this_run),
        "consumed_bar_count": int(len(state.get("consumed_bar_keys", []))),
        "freshness_minutes": None if freshness_minutes is None else round(float(freshness_minutes), 3),
        "updated_at_utc": iso_z(utc_now()),
        "shadow_is_preview": bool(current.get("is_preview", False)),
        "shadow_has_realized_hold_return": bool(current.get("has_realized_hold_return", False)),
        "note": "raw-bar shadow scaffold only; no order placement. Keep as-of long-window evidence and frozen current-universe readiness explicitly separated.",
    }


def build_operator_packet(current: dict[str, Any], readiness: dict[str, Any], formal_summary: dict[str, Any], warnings: list[dict[str, Any]], source_meta: dict[str, Any], *, freshness_minutes: float | None, state: dict[str, Any], bar_already_consumed_before_run: bool, did_consume_latest_bar_this_run: bool) -> dict[str, Any]:
    formal_gate = formal_summary.get("gate", {}) if isinstance(formal_summary.get("gate"), dict) else {}
    return {
        "generated_at_utc": iso_z(utc_now()),
        "runner": RUNNER_NAME,
        "runner_mode": RUNNER_MODE,
        "source_mode": source_meta.get("mode"),
        "frame_source_mode": source_meta.get("frame_source_mode") or source_meta.get("mode"),
        "current_decision_source_mode": source_meta.get("current_decision_source_mode") or source_meta.get("mode"),
        "current_decision_recent_days": source_meta.get("current_decision_recent_days"),
        "current_decision_panel_start_utc": source_meta.get("panel_start_utc"),
        "current_decision_panel_end_utc": source_meta.get("panel_end_utc"),
        "current_decision_latest_live_row_ts": source_meta.get("latest_live_row_ts"),
        "current_decision": current,
        "current_decision_is_preview": bool(current.get("is_preview", False)),
        "current_decision_has_realized_hold_return": bool(current.get("has_realized_hold_return", False)),
        "runtime": {
            "latest_bar_consumed": bool(did_consume_latest_bar_this_run),
            "bar_already_consumed_before_run": bool(bar_already_consumed_before_run),
            "did_consume_latest_bar_this_run": bool(did_consume_latest_bar_this_run),
            "freshness_minutes": None if freshness_minutes is None else round(float(freshness_minutes), 3),
            "consumed_bar_count": int(len(state.get("consumed_bar_keys", []))),
            "last_consumed_bar_key": state.get("last_consumed_bar_key"),
            "last_event_kind": state.get("last_event_kind"),
        },
        "formal_gate_context": {
            "historical_on_rate_pct": formal_gate.get("on_rate_pct"),
            "current_snapshot": formal_gate.get("current_snapshot"),
        },
        "readiness_context": {
            "headline": readiness.get("headline"),
            "proved": readiness.get("proved"),
            "not_proved": readiness.get("not_proved"),
            "single_blocker": readiness.get("single_blocker"),
            "window_availability": readiness.get("window_availability"),
        },
        "warnings": warnings,
    }


def write_html(status: dict[str, Any], current: dict[str, Any], operator_packet: dict[str, Any]) -> None:
    ensure_dir(SITE_PATH.parent)
    body = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Rank213 shadow runner</title>
  <style>
    :root{{--bg:#f8fafc;--card:#fff;--fg:#0f172a;--muted:#64748b;--line:#e2e8f0;--ok:#166534;--okbg:#dcfce7;--warn:#9a3412;--warnbg:#ffedd5;}}
    *{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.65 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}}
    .wrap{{max-width:1100px;margin:0 auto;padding:28px 18px 64px}} .card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin-bottom:14px}}
    h1,h2{{margin:0 0 12px}} .muted{{color:var(--muted)}} code{{background:#eff6ff;border-radius:6px;padding:2px 6px}} pre{{margin:0;white-space:pre-wrap;background:#f8fafc;border:1px solid var(--line);border-radius:10px;padding:10px;font-size:12px}}
    .ok{{border-left:4px solid var(--ok);background:var(--okbg);padding:12px 14px;border-radius:10px}} .note{{border-left:4px solid var(--warn);background:var(--warnbg);padding:12px 14px;border-radius:10px}}
  </style>
</head>
<body><div class="wrap">
  <div class="card">
    <h1>Rank213 shadow runner</h1>
    <p class="muted">这是 raw-bar shadow scaffold，不下单，只用于把 rank213 的 as-of basket + formal gate 决策以 runner-grade 产物形式持续暴露出来。</p>
    <p><a href="/momentum/paper/rank213_largecap_xs_jump_veto.html">frozen seed runner</a> · <a href="/momentum/paper/rank213_largecap_xs_jump_veto_shadow_compare.html">shadow_compare</a> · <a href="/momentum/paper/rank213_largecap_xs_jump_veto_readiness_note.html">readiness_note</a> · <a href="/momentum/paper/rank213_largecap_xs_jump_veto_formal_strategy_review.html">formal_strategy_review</a></p>
  </div>
  <div class="card">
    <h2>状态</h2>
    <ul>
      <li>runner_mode: <code>{status['runner_mode']}</code></li>
      <li>source_mode: <code>{status['source_mode']}</code></li>
      <li>latest_decision_ts: <code>{status['latest_decision_ts']}</code></li>
      <li>gate_on: <code>{status['gate_on']}</code></li>
      <li>latest_longs: <code>{status['latest_longs']}</code></li>
      <li>latest_shorts: <code>{status['latest_shorts']}</code></li>
      <li>warnings_count: <code>{status['warnings_count']}</code></li>
    </ul>
    <div class="note">这个页面不表示已接实盘，只表示 raw-bar shadow 审计骨架已经建立。as-of 长窗证据可支持继续推进，但 frozen current-universe readiness 仍需单独诚实披露。</div>
  </div>
  <div class="card">
    <h2>当前决策</h2>
    <pre>{json.dumps(current, ensure_ascii=False, indent=2)}</pre>
  </div>
  <div class="card">
    <h2>operator packet</h2>
    <pre>{json.dumps(operator_packet, ensure_ascii=False, indent=2)}</pre>
  </div>
</div></body>
</html>'''
    SITE_PATH.write_text(body, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Run rank213 raw-bar shadow runner scaffold")
    ap.add_argument("--recent-days", type=int, default=14, help="Tail days to emphasize when recomputing recent rows")
    args = ap.parse_args()

    ensure_dir(ART_DIR)
    frame, source_meta = build_shadow_frame(recent_days=int(args.recent_days))
    recent = build_recent_decisions(frame)
    current = build_current_decision(frame, source_meta)
    readiness = load_readiness()
    formal_summary = load_formal_summary()

    state = load_state()
    consumed_bar_keys_before = trim_consumed_bar_keys(state.get("consumed_bar_keys", []))
    latest_bar_key = current.get("bar_key")
    bar_already_consumed_before_run = bool(latest_bar_key and latest_bar_key in consumed_bar_keys_before)
    did_consume_latest_bar_this_run = bool(latest_bar_key) and not bar_already_consumed_before_run
    consumed_bar_keys_after = list(consumed_bar_keys_before)
    if did_consume_latest_bar_this_run:
        consumed_bar_keys_after.append(latest_bar_key)
    consumed_bar_keys_after = trim_consumed_bar_keys(consumed_bar_keys_after)

    latest_decision_ts = pd.to_datetime(current.get("decision_ts"), utc=True) if current.get("decision_ts") else None
    freshness_minutes = compute_freshness_minutes(latest_decision_ts)
    now_iso = iso_z(utc_now())
    event_kind = "bar_refresh_skipped_same_bar" if bar_already_consumed_before_run else "new_shadow_decision"

    state_after = dict(state)
    last_consumed_bar_key = state_after.get("last_consumed_bar_key")
    if did_consume_latest_bar_this_run:
        last_consumed_bar_key = latest_bar_key
    state_after.update({
        "runner_mode": RUNNER_MODE,
        "last_run_at_utc": now_iso,
        "last_decision_ts": current.get("decision_ts"),
        "last_bar_key": latest_bar_key,
        "last_consumed_bar_key": last_consumed_bar_key,
        "source_mode": source_meta.get("mode"),
        "frame_source_mode": source_meta.get("frame_source_mode") or source_meta.get("mode"),
        "current_decision_source_mode": source_meta.get("current_decision_source_mode") or source_meta.get("mode"),
        "last_event_kind": event_kind,
        "latest_bar_consumed": bool(did_consume_latest_bar_this_run),
        "bar_already_consumed_before_run": bool(bar_already_consumed_before_run),
        "did_consume_latest_bar_this_run": bool(did_consume_latest_bar_this_run),
        "freshness_minutes": None if freshness_minutes is None else round(float(freshness_minutes), 3),
        "consumed_bar_keys": consumed_bar_keys_after,
    })

    warnings = build_warnings(frame, readiness, source_meta, freshness_minutes=freshness_minutes, latest_bar_consumed=bar_already_consumed_before_run)
    status = build_status(frame, current, warnings, source_meta, freshness_minutes=freshness_minutes, state=state_after, bar_already_consumed_before_run=bar_already_consumed_before_run, did_consume_latest_bar_this_run=did_consume_latest_bar_this_run)
    operator_packet = build_operator_packet(current, readiness, formal_summary, warnings, source_meta, freshness_minutes=freshness_minutes, state=state_after, bar_already_consumed_before_run=bar_already_consumed_before_run, did_consume_latest_bar_this_run=did_consume_latest_bar_this_run)

    event_payload = {
        "event_at_utc": now_iso,
        "event_kind": event_kind,
        "runner": RUNNER_NAME,
        "runner_mode": RUNNER_MODE,
        "bar_key": latest_bar_key,
        "decision_ts": current.get("decision_ts"),
        "planned_exit_ts": current.get("planned_exit_ts"),
        "decision": current.get("decision"),
        "gate_on": current.get("gate_on"),
        "source_mode": source_meta.get("mode"),
        "frame_source_mode": source_meta.get("frame_source_mode") or source_meta.get("mode"),
        "current_decision_source_mode": source_meta.get("current_decision_source_mode") or source_meta.get("mode"),
        "bar_already_consumed_before_run": bool(bar_already_consumed_before_run),
        "did_consume_latest_bar_this_run": bool(did_consume_latest_bar_this_run),
        "freshness_minutes": None if freshness_minutes is None else round(float(freshness_minutes), 3),
        "official_bar": bool(is_official_bar(latest_decision_ts)),
        "warnings_count": len(warnings),
    }

    normalize_for_csv(recent).to_csv(RECENT_DECISIONS_PATH, index=False)
    save_json(CURRENT_DECISION_PATH, current)
    save_json(WARNINGS_PATH, warnings)
    save_json(STATUS_PATH, status)
    save_json(OPERATOR_PACKET_PATH, operator_packet)
    append_jsonl(EVENTS_PATH, [event_payload], keep_last=MAX_EVENT_ROWS)
    save_json(STATE_PATH, state_after)
    write_html(status, current, operator_packet)

    run_summary = {
        "run_at_utc": now_iso,
        "runner": RUNNER_NAME,
        "runner_mode": RUNNER_MODE,
        "source_mode": source_meta.get("mode"),
        "frame_source_mode": source_meta.get("frame_source_mode") or source_meta.get("mode"),
        "current_decision_source_mode": source_meta.get("current_decision_source_mode") or source_meta.get("mode"),
        "current_decision_recent_days": source_meta.get("current_decision_recent_days"),
        "frame_rows": int(len(frame)),
        "recent_rows": int(len(recent)),
        "latest_decision_ts": current.get("decision_ts"),
        "latest_bar_consumed": bool(did_consume_latest_bar_this_run),
        "bar_already_consumed_before_run": bool(bar_already_consumed_before_run),
        "did_consume_latest_bar_this_run": bool(did_consume_latest_bar_this_run),
        "freshness_minutes": None if freshness_minutes is None else round(float(freshness_minutes), 3),
        "status_path": str(STATUS_PATH.relative_to(ROOT)),
        "state_path": str(STATE_PATH.relative_to(ROOT)),
        "recent_decisions_path": str(RECENT_DECISIONS_PATH.relative_to(ROOT)),
        "current_decision_path": str(CURRENT_DECISION_PATH.relative_to(ROOT)),
        "operator_packet_path": str(OPERATOR_PACKET_PATH.relative_to(ROOT)),
        "warnings_path": str(WARNINGS_PATH.relative_to(ROOT)),
        "events_path": str(EVENTS_PATH.relative_to(ROOT)),
        "html_path": str(SITE_PATH.relative_to(ROOT)),
    }
    if "recomputed_detail_csv" in source_meta:
        run_summary["recomputed_detail_csv"] = source_meta["recomputed_detail_csv"]
    save_json(RUN_SUMMARY_PATH, run_summary)
    print(json.dumps(run_summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
