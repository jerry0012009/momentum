#!/usr/bin/env python3
from __future__ import annotations

"""Dedicated paper runner seed for Rank 213 / large-cap XS momentum × short-leg jump veto.

This runner is intentionally honest about scope:
- source of truth is the frozen admission artifact for variant f64_h12_floor150_mult2p0
- it writes runner-grade artifacts (ledger / status / state / html / summary)
- scheduler ownership + first verified run make launch wiring explicit
- it does NOT yet recompute raw-bar live signals from exchange candles
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "reports" / "artifacts" / "optimization_loop" / "rank213_p2_admission_20260328"
TIMESERIES_PATH = SRC_DIR / "variant_timeseries.csv"
SUMMARY_PATH = SRC_DIR / "summary.json"
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank213_largecap_xs_jump_veto"
LEDGER_PATH = ART_DIR / "rank213_closed_trades.csv"
STATUS_PATH = ART_DIR / "rank213_status.csv"
STATE_PATH = ART_DIR / "rank213_state.json"
RUN_SUMMARY_PATH = ART_DIR / "rank213_last_run_summary.json"
CURRENT_SIGNAL_PATH = ART_DIR / "rank213_current_signal_frame.csv"
REGIME_SUMMARY_PATH = ART_DIR / "rank213_regime_review_summary.json"
LONG_HISTORY_SUMMARY_PATH = ART_DIR / "rank213_long_history_review_summary.json"
LONG_HISTORY_DETAIL_PATH = ART_DIR / "rank213_long_history_detail.csv"
ASOF_SUMMARY_PATH = ART_DIR / "rank213_asof_universe_long_history_review_summary.json"
FORMAL_THREEWAY_SUMMARY_PATH = ART_DIR / "rank213_formal_threeway_backtest_summary.json"
MONTHLY_REBUILD_SUMMARY_PATH = ART_DIR / "rank213_monthly_volume_universe_rebuild_summary.json"
MONTHLY_REBUILD_DETAIL_PATH = ART_DIR / "rank213_monthly_volume_universe_rebuild_detail.csv"
UNIVERSE_AUDIT_SUMMARY_PATH = ART_DIR / "rank213_universe_selection_audit_summary.json"
FORMAL_FREEZE_SUMMARY_PATH = ART_DIR / "rank213_formal_strategy_freeze_summary.json"
SHADOW_OPERATOR_PACKET_PATH = ART_DIR / "rank213_shadow_operator_packet.json"
HTML_PATH = ROOT / "reports" / "site" / "paper" / "rank213_largecap_xs_jump_veto.html"

CANDIDATE_ID = "rank213_largecap_xs_jump_veto"
CANDIDATE_RANK = 213
VARIANT = "f64_h12_floor150_mult2p0"
FORMATION_BARS = 64
HOLD_BARS = 12
BAR_MINUTES = 15
VETO_FLOOR_PCT = 1.5
VETO_MULT = 2.0
ROUND_TRIP_COST_BPS = 4.0
RUNNER_SERVICE = "momentum-rank213-paper-refresh.service"
RUNNER_TIMER = "momentum-rank213-paper-refresh.timer"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_z(ts) -> str:
    return pd.to_datetime(ts, utc=True).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {}
    return read_json(STATE_PATH)


def save_state(state: dict) -> None:
    ensure_dir(STATE_PATH.parent)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def normalize_for_csv(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[col]):
            out[col] = out[col].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return out


def load_variant_frame() -> tuple[pd.DataFrame, dict]:
    summary = read_json(SUMMARY_PATH)
    df = pd.read_csv(TIMESERIES_PATH)
    df = df[df["variant"] == VARIANT].copy()
    if df.empty:
        raise RuntimeError(f"variant {VARIANT} not found in {TIMESERIES_PATH}")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values("timestamp").reset_index(drop=True)
    df["entry_ts"] = df["timestamp"]
    df["exit_ts"] = df["timestamp"] + pd.to_timedelta(HOLD_BARS * BAR_MINUTES, unit="m")
    df["candidate_id"] = CANDIDATE_ID
    df["candidate_rank"] = CANDIDATE_RANK
    df["stage"] = "paper_runner_live_seed"
    df["venue_mode"] = "frozen_admission_timeseries_seed"
    df["signal_family"] = "largecap_xs_momentum_shortleg_jump_veto"
    df["trade_id"] = df["timestamp"].dt.strftime("%Y%m%dT%H%M%SZ") + "|" + VARIANT
    df["gross_ret"] = pd.to_numeric(df["veto_gross_return"], errors="coerce")
    df["gross_bps"] = df["gross_ret"] * 10000.0
    df["turnover_x"] = pd.to_numeric(df["veto_turnover_x"], errors="coerce")
    df["net_bps"] = df["gross_bps"] - ROUND_TRIP_COST_BPS * df["turnover_x"]
    df["net_ret"] = df["net_bps"] / 10000.0
    df["longs"] = df["plain_longs"].fillna("")
    df["shorts"] = df["veto_shorts"].fillna("")
    df["veto_count"] = pd.to_numeric(df["veto_count"], errors="coerce").fillna(0).astype(int)
    df["complete_trade"] = True
    return df, summary


def initialize_state(trades: pd.DataFrame, summary: dict) -> dict:
    return {
        "initialized_at_utc": iso_z(utc_now()),
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "wiring_status": "connected_runner_live",
        "runner_mode": "frozen_admission_timeseries_seed",
        "runner_script": str((ROOT / "scripts" / "run_rank213_largecap_xs_jump_veto_paper_runner.py").relative_to(ROOT)),
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "source_summary": str(SUMMARY_PATH.relative_to(ROOT)),
        "source_timeseries": str(TIMESERIES_PATH.relative_to(ROOT)),
        "variant": VARIANT,
        "watermark_exit_ts_utc": iso_z(trades["exit_ts"].max()) if not trades.empty else None,
        "sample_start_utc": iso_z(pd.to_datetime(summary["sample_start"], utc=True)),
        "sample_end_utc": iso_z(pd.to_datetime(summary["sample_end"], utc=True)),
        "notes": "Launch wiring runner uses frozen admission timeseries for the approved f64_h12_floor150_mult2p0 seed; raw-bar live recomputation is a later scope, not implied here.",
    }


def build_status(trades: pd.DataFrame, summary: dict, state: dict, new_rows: int) -> dict:
    latest = trades.iloc[-1] if not trades.empty else None
    first = trades.iloc[0] if not trades.empty else None
    lifetime_total_return = float((1.0 + trades["net_ret"]).prod() - 1.0) if not trades.empty else 0.0
    sample_start = pd.to_datetime(summary["sample_start"], utc=True)
    sample_end = pd.to_datetime(summary["sample_end"], utc=True)
    raw_panel_days = float((sample_end - sample_start).total_seconds() / 86400.0)
    trade_window_days = float((trades["exit_ts"].max() - trades["entry_ts"].min()).total_seconds() / 86400.0) if not trades.empty else 0.0
    trades_per_day = float(len(trades) / trade_window_days) if trade_window_days > 0 else 0.0
    mean_net_ret = float(trades["net_ret"].mean()) if not trades.empty else 0.0
    naive_compound_from_mean = float((1.0 + mean_net_ret) ** len(trades) - 1.0) if not trades.empty else 0.0
    median_net_bps = float(trades["net_bps"].median()) if not trades.empty else 0.0
    std_net_bps = float(trades["net_bps"].std()) if len(trades) > 1 else 0.0
    worst_net_bps = float(trades["net_bps"].min()) if not trades.empty else 0.0
    best_net_bps = float(trades["net_bps"].max()) if not trades.empty else 0.0
    nonpositive_trade_rate = float((trades["net_bps"] <= 0).mean()) if not trades.empty else 0.0
    return {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "stage": "paper_runner_live",
        "wiring_status": "connected_runner_live",
        "runner_mode": "frozen_admission_timeseries_seed",
        "runner_script": "scripts/run_rank213_largecap_xs_jump_veto_paper_runner.py",
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "source_summary": "reports/artifacts/optimization_loop/rank213_p2_admission_20260328/summary.json",
        "source_timeseries": "reports/artifacts/optimization_loop/rank213_p2_admission_20260328/variant_timeseries.csv",
        "variant": VARIANT,
        "signal_timeframe": "15m",
        "formation_bars": FORMATION_BARS,
        "hold_bars": HOLD_BARS,
        "veto_floor_pct": VETO_FLOOR_PCT,
        "veto_mult_x_median": VETO_MULT,
        "universe_size": int(summary["universe_size"]),
        "round_trip_cost_bps_per_turnover_x": ROUND_TRIP_COST_BPS,
        "sample_start_utc": iso_z(sample_start),
        "sample_end_utc": iso_z(sample_end),
        "first_trade_entry_ts": iso_z(first["entry_ts"]) if first is not None else None,
        "last_trade_exit_ts": iso_z(trades["exit_ts"].max()) if not trades.empty else None,
        "raw_panel_days": raw_panel_days,
        "trade_window_days": trade_window_days,
        "trades_per_day": trades_per_day,
        "closed_trades": int(len(trades)),
        "new_closed_trades_appended": int(new_rows),
        "pct_rebalances_with_any_veto": float((trades["veto_count"] > 0).mean()) if not trades.empty else 0.0,
        "mean_turnover_x": float(trades["turnover_x"].mean()) if not trades.empty else 0.0,
        "mean_gross_bps": float(trades["gross_bps"].mean()) if not trades.empty else 0.0,
        "mean_net_bps": float(trades["net_bps"].mean()) if not trades.empty else 0.0,
        "mean_net_ret": mean_net_ret,
        "median_net_bps": median_net_bps,
        "std_net_bps": std_net_bps,
        "worst_net_bps": worst_net_bps,
        "best_net_bps": best_net_bps,
        "nonpositive_trade_rate": nonpositive_trade_rate,
        "naive_compound_from_mean": naive_compound_from_mean,
        "win_rate": float((trades["net_bps"] > 0).mean()) if not trades.empty else 0.0,
        "lifetime_total_return": lifetime_total_return,
        "latest_signal_ts": iso_z(latest["entry_ts"]) if latest is not None else None,
        "latest_planned_exit_ts": iso_z(latest["exit_ts"]) if latest is not None else None,
        "latest_longs": latest["longs"] if latest is not None else "",
        "latest_shorts": latest["shorts"] if latest is not None else "",
        "watermark_exit_ts_utc": state.get("watermark_exit_ts_utc"),
        "updated_at_utc": iso_z(utc_now()),
        "note": "wired: dedicated runner + systemd timer live; Rank 213 now runs as an honest frozen-seed paper lane for the approved f64_h12_floor150_mult2p0 jump-veto spec. This is launch plumbing, not a claim of raw-bar live recomputation.",
    }


def load_regime_snapshot() -> dict:
    if not REGIME_SUMMARY_PATH.exists():
        return {}
    try:
        payload = read_json(REGIME_SUMMARY_PATH)
        q4 = payload.get("q4_live_like", {})
        q5 = payload.get("q5_simple_gate", {})
        cg = q5.get("current_gate", {})
        return {
            "live_like": q4.get("live_like"),
            "distance_to_good": q4.get("distance_to_good"),
            "distance_to_bad": q4.get("distance_to_bad"),
            "gate_on": cg.get("gate_on"),
            "votes": cg.get("votes"),
            "valid_rules": cg.get("valid_rules"),
            "needed_votes": cg.get("needed_votes"),
            "window_start_utc": cg.get("window_start_utc"),
            "window_end_utc": cg.get("window_end_utc"),
        }
    except Exception:
        return {}


def load_frozen_long_history_snapshot() -> dict:
    if not LONG_HISTORY_SUMMARY_PATH.exists():
        return {}
    try:
        summary = read_json(LONG_HISTORY_SUMMARY_PATH)
        out = {
            "available_start_utc": summary.get("data_availability", {}).get("actual_common_start_utc"),
            "available_end_utc": summary.get("data_availability", {}).get("actual_common_end_utc"),
            "common_history_days": summary.get("data_availability", {}).get("calendar_days"),
            "rebalances": summary.get("data_availability", {}).get("rebalances"),
            "full_available_history": summary.get("full_available_history", {}).get("veto", {}),
            "final_verdict": summary.get("final_verdict"),
        }
        if LONG_HISTORY_DETAIL_PATH.exists():
            df = pd.read_csv(LONG_HISTORY_DETAIL_PATH)
            df["timestamp_ts"] = pd.to_datetime(df["timestamp_ts"], utc=True)
            df["exit_ts"] = pd.to_datetime(df["exit_ts"], utc=True)
            df = df.sort_values("timestamp_ts").reset_index(drop=True)
            end = df["exit_ts"].max()
            start = df["timestamp_ts"].min()
            available_days = float((end - start).total_seconds() / 86400.0)
            out["actual_trade_window_days"] = available_days
            for days in (120, 180, 360):
                key = f"window_{days}d"
                if available_days + 1e-9 < days:
                    out[key] = {
                        "available": False,
                        "required_days": days,
                        "available_days": available_days,
                        "reason": "common-history shorter than requested window under frozen universe",
                    }
                    continue
                start_cut = end - pd.Timedelta(days=days)
                sub = df[df["timestamp_ts"] >= start_cut].copy()
                out[key] = {
                    "available": True,
                    "start_utc": iso_z(sub["timestamp_ts"].min()),
                    "end_utc": iso_z(sub["exit_ts"].max()),
                    "rebalances": int(len(sub)),
                    "trade_window_days": float((sub["exit_ts"].max() - sub["timestamp_ts"].min()).total_seconds() / 86400.0),
                    "mean_net_bps": float(sub["veto_net"].mean() * 10000.0),
                    "cum_pct": float(((1.0 + sub["veto_net"]).prod() - 1.0) * 100.0),
                }
        return out
    except Exception:
        return {}


def load_gate_deep_snapshot() -> dict:
    out: dict = {}
    try:
        freeze = read_json(FORMAL_FREEZE_SUMMARY_PATH)
        gate = freeze.get("gate", {})
        out["freeze_gate"] = {
            "name": gate.get("name"),
            "definition": gate.get("definition"),
            "lookback_days": gate.get("lookback_days"),
            "vote_ratio": gate.get("vote_ratio"),
            "off_action": gate.get("off_action"),
            "on_action": gate.get("on_action"),
            "rules": gate.get("rules", []),
        }
    except Exception:
        pass
    try:
        formal = read_json(FORMAL_THREEWAY_SUMMARY_PATH)
        out["formal_current_gate"] = formal.get("gate", {}).get("current_snapshot", {})
        out["formal_gate_calculation_mode"] = formal.get("gate", {}).get("calculation_mode")
        out["formal_gate_calculation_note"] = formal.get("gate", {}).get("calculation_note")
    except Exception:
        pass
    try:
        shadow = read_json(SHADOW_OPERATOR_PACKET_PATH)
        out["shadow_current_decision"] = shadow.get("current_decision", {})
        out["shadow_formal_gate_context"] = shadow.get("formal_gate_context", {}).get("current_snapshot", {})
        out["shadow_runtime"] = shadow.get("runtime", {})
        out["shadow_source_mode"] = shadow.get("source_mode")
        out["shadow_frame_source_mode"] = shadow.get("frame_source_mode")
        out["shadow_current_decision_source_mode"] = shadow.get("current_decision_source_mode")
        out["shadow_current_decision_recent_days"] = shadow.get("current_decision_recent_days")
    except Exception:
        pass
    freeze_gate = out.get("freeze_gate", {}) if isinstance(out.get("freeze_gate"), dict) else {}
    out["same_gate_as_backtest"] = bool(freeze_gate)
    return out


def build_monthly_rebuild_svg(monthly_rows: list[dict]) -> str:
    if not monthly_rows:
        return ""

    width = 1040
    height = 360
    left = 56
    right = 24
    line_top = 28
    line_bottom = 170
    bar_top = 220
    bar_bottom = 320
    inner_width = width - left - right
    count = len(monthly_rows)
    xs = [left + (inner_width * i / max(count - 1, 1)) for i in range(count)]

    equity_vals = [float(row.get("equity_cum_pct", 0.0)) for row in monthly_rows]
    eq_min = min(0.0, min(equity_vals))
    eq_max = max(equity_vals)
    if eq_max <= eq_min:
        eq_max = eq_min + 1.0
    eq_pad = max((eq_max - eq_min) * 0.08, 0.5)
    eq_lo = eq_min - eq_pad
    eq_hi = eq_max + eq_pad

    def scale_eq(val: float) -> float:
        return line_bottom - (val - eq_lo) / (eq_hi - eq_lo) * (line_bottom - line_top)

    month_vals = [float(row.get("month_ret_pct", 0.0)) for row in monthly_rows]
    max_abs_month = max(max(abs(x) for x in month_vals), 1.0)
    bar_zero = (bar_top + bar_bottom) / 2.0
    bar_half = (bar_bottom - bar_top) / 2.0 - 4.0
    bar_width = max(min(inner_width / max(count, 1) * 0.72, 10.0), 2.0)

    def scale_bar_delta(val: float) -> float:
        return abs(val) / max_abs_month * bar_half

    line_grid = []
    for step in range(5):
        val = eq_lo + (eq_hi - eq_lo) * step / 4.0
        y = scale_eq(val)
        line_grid.append(
            f"<line x1='{left}' y1='{y:.1f}' x2='{width - right}' y2='{y:.1f}' stroke='#e2e8f0' stroke-dasharray='3 4'/>"
            f"<text x='8' y='{y + 4:.1f}' fill='#64748b' font-size='11'>{val:.1f}%</text>"
        )

    polyline = " ".join(f"{x:.1f},{scale_eq(v):.1f}" for x, v in zip(xs, equity_vals))
    bars = []
    month_labels = []
    for i, (x, row, month_ret) in enumerate(zip(xs, monthly_rows, month_vals)):
        if month_ret > 0:
            y = bar_zero - scale_bar_delta(month_ret)
            h = bar_zero - y
            color = "#16a34a"
            bars.append(f"<rect x='{x - bar_width / 2:.1f}' y='{y:.1f}' width='{bar_width:.1f}' height='{max(h, 1.2):.1f}' rx='1.5' fill='{color}' opacity='0.92'/>")
        elif month_ret < 0:
            h = scale_bar_delta(month_ret)
            color = "#dc2626"
            bars.append(f"<rect x='{x - bar_width / 2:.1f}' y='{bar_zero:.1f}' width='{bar_width:.1f}' height='{max(h, 1.2):.1f}' rx='1.5' fill='{color}' opacity='0.92'/>")
        else:
            bars.append(f"<line x1='{x - bar_width / 2:.1f}' y1='{bar_zero:.1f}' x2='{x + bar_width / 2:.1f}' y2='{bar_zero:.1f}' stroke='#cbd5e1' stroke-width='2'/>")

        month = str(row.get("month", ""))
        if i == 0 or i == count - 1 or month.endswith("-01"):
            month_labels.append(
                f"<line x1='{x:.1f}' y1='{bar_bottom:.1f}' x2='{x:.1f}' y2='{bar_bottom + 6:.1f}' stroke='#94a3b8'/>"
                f"<text x='{x:.1f}' y='{bar_bottom + 20:.1f}' text-anchor='middle' fill='#64748b' font-size='11'>{month}</text>"
            )

    last_x = xs[-1]
    last_y = scale_eq(equity_vals[-1])
    return f"""
      <svg viewBox='0 0 {width} {height}' width='100%' height='360' role='img' aria-label='monthly rebuild equity curve and monthly returns'>
        <rect x='1' y='1' width='{width - 2}' height='{height - 2}' rx='16' fill='#ffffff' stroke='#dbe4f0'/>
        <text x='{left}' y='18' fill='#0f172a' font-size='13' font-weight='600'>月度重构口径：month-end equity curve（上） + calendar-month return bars（下）</text>
        {''.join(line_grid)}
        <line x1='{left}' y1='{line_bottom:.1f}' x2='{width - right}' y2='{line_bottom:.1f}' stroke='#cbd5e1'/>
        <line x1='{left}' y1='{bar_zero:.1f}' x2='{width - right}' y2='{bar_zero:.1f}' stroke='#cbd5e1'/>
        <text x='8' y='{bar_zero + 4:.1f}' fill='#64748b' font-size='11'>0%</text>
        <polyline fill='none' stroke='#2563eb' stroke-width='3' points='{polyline}'/>
        <circle cx='{last_x:.1f}' cy='{last_y:.1f}' r='4' fill='#2563eb'/>
        <text x='{last_x - 6:.1f}' y='{last_y - 10:.1f}' text-anchor='end' fill='#1d4ed8' font-size='11'>{equity_vals[-1]:.2f}%</text>
        {''.join(bars)}
        {''.join(month_labels)}
        <rect x='{width - 210}' y='24' width='12' height='12' rx='2' fill='#2563eb'/><text x='{width - 192}' y='34' fill='#475569' font-size='11'>累计净收益（month-end chain）</text>
        <rect x='{width - 210}' y='42' width='12' height='12' rx='2' fill='#16a34a'/><text x='{width - 192}' y='52' fill='#475569' font-size='11'>月度盈利</text>
        <rect x='{width - 210}' y='60' width='12' height='12' rx='2' fill='#dc2626'/><text x='{width - 192}' y='70' fill='#475569' font-size='11'>月度亏损</text>
        <line x1='{width - 210}' y1='82' x2='{width - 198}' y2='82' stroke='#cbd5e1' stroke-width='2'/><text x='{width - 192}' y='86' fill='#475569' font-size='11'>月度持平 / gate off</text>
      </svg>
"""


def load_universe_transparency_snapshot() -> dict:
    out = {}
    try:
        asof = read_json(ASOF_SUMMARY_PATH)
        windows = {str(x.get("window")): x for x in asof.get("window_reviews", []) if isinstance(x, dict)}
        out["asof"] = {
            "sample": asof.get("sample", {}),
            "full_veto": asof.get("full_available_history", {}).get("veto", {}),
            "window_1y": windows.get("1Y", {}),
            "window_2y": windows.get("2Y", {}),
        }
    except Exception:
        pass
    try:
        formal = read_json(FORMAL_THREEWAY_SUMMARY_PATH)
        out["formal"] = {
            "sample": formal.get("sample", {}),
            "full_gate": formal.get("full_period", {}).get("baseline_plus_veto_plus_gate", {}),
            "gate": formal.get("gate", {}),
        }
    except Exception:
        pass
    try:
        monthly = read_json(MONTHLY_REBUILD_SUMMARY_PATH)
        monthly_out = {
            "sample": monthly.get("sample", {}),
            "coverage": monthly.get("coverage", {}),
            "full_gate": monthly.get("metrics", {}).get("monthly_volume_rebuild", {}).get("baseline_plus_veto_plus_gate", {}),
            "important_limitation": monthly.get("important_limitation", ""),
        }
        if MONTHLY_REBUILD_DETAIL_PATH.exists():
            detail = pd.read_csv(MONTHLY_REBUILD_DETAIL_PATH)
            detail["timestamp_ts"] = pd.to_datetime(detail["timestamp_ts"], utc=True)
            monthly_roll = detail.groupby("month", sort=True).apply(
                lambda g: pd.Series({
                    "baskets": int(len(g)),
                    "gate_on_baskets": int(g["gate_on"].fillna(False).astype(bool).sum()),
                    "month_ret": float((1.0 + g["gate_net"]).prod() - 1.0),
                    "mean_gate_turnover_x": float(g["gate_turnover_x"].mean()),
                })
            ).reset_index()
            monthly_roll["equity_cum_ret"] = (1.0 + monthly_roll["month_ret"]).cumprod() - 1.0
            monthly_rows = []
            for _, row in monthly_roll.iterrows():
                monthly_rows.append({
                    "month": str(row["month"]),
                    "baskets": int(row["baskets"]),
                    "gate_on_baskets": int(row["gate_on_baskets"]),
                    "month_ret_pct": float(row["month_ret"] * 100.0),
                    "equity_cum_pct": float(row["equity_cum_ret"] * 100.0),
                    "mean_gate_turnover_x": float(row["mean_gate_turnover_x"]),
                })
            positive_months = int((monthly_roll["month_ret"] > 0).sum())
            negative_months = int((monthly_roll["month_ret"] < 0).sum())
            flat_months = int((monthly_roll["month_ret"] == 0).sum())
            best_idx = int(monthly_roll["month_ret"].idxmax()) if not monthly_roll.empty else 0
            worst_idx = int(monthly_roll["month_ret"].idxmin()) if not monthly_roll.empty else 0
            years = monthly_roll["month"].astype(str).str[:4]
            yearly_rows = []
            for year, grp in monthly_roll.groupby(years, sort=True):
                yearly_rows.append({
                    "year": str(year),
                    "year_ret_pct": float(((1.0 + grp["month_ret"]).prod() - 1.0) * 100.0),
                    "positive_months": int((grp["month_ret"] > 0).sum()),
                    "negative_months": int((grp["month_ret"] < 0).sum()),
                    "flat_months": int((grp["month_ret"] == 0).sum()),
                    "gate_on_baskets": int(grp["gate_on_baskets"].sum()),
                })
            inferred_cost_bps = float((((detail["plain_gross"] - detail["plain_net"]) / detail["plain_turnover_x"]).dropna().median()) * 10000.0)
            monthly_out.update({
                "cost_roundtrip_bps_per_turnover_x": inferred_cost_bps,
                "cost_per_side_bps_if_turnover_1x": inferred_cost_bps / 2.0,
                "monthly_rows": monthly_rows,
                "yearly_rows": yearly_rows,
                "curve_svg": build_monthly_rebuild_svg(monthly_rows),
                "month_summary": {
                    "total_months": int(len(monthly_roll)),
                    "positive_months": positive_months,
                    "negative_months": negative_months,
                    "flat_months": flat_months,
                    "best_month": str(monthly_roll.loc[best_idx, "month"]) if not monthly_roll.empty else None,
                    "best_month_ret_pct": float(monthly_roll.loc[best_idx, "month_ret"] * 100.0) if not monthly_roll.empty else 0.0,
                    "worst_month": str(monthly_roll.loc[worst_idx, "month"]) if not monthly_roll.empty else None,
                    "worst_month_ret_pct": float(monthly_roll.loc[worst_idx, "month_ret"] * 100.0) if not monthly_roll.empty else 0.0,
                    "sample_years": float((detail["timestamp_ts"].max() - detail["timestamp_ts"].min()).total_seconds() / 86400.0 / 365.25) if not detail.empty else 0.0,
                },
            })
        out["monthly"] = monthly_out
    except Exception:
        pass
    try:
        audit = read_json(UNIVERSE_AUDIT_SUMMARY_PATH)
        out["audit"] = {
            "selection_honesty": audit.get("checks", {}).get("original_selection_uses_only_then_visible_info", {}),
            "survivorship_bias_risk": audit.get("checks", {}).get("survivorship_bias_risk", {}),
        }
    except Exception:
        pass
    return out


def write_html(
    status: dict,
    latest_row: dict | None,
    regime_snapshot: dict | None = None,
    long_history_snapshot: dict | None = None,
    universe_snapshot: dict | None = None,
    gate_deep_snapshot: dict | None = None,
) -> None:
    ensure_dir(HTML_PATH.parent)
    regime_snapshot = regime_snapshot or {}
    long_history_snapshot = long_history_snapshot or {}
    universe_snapshot = universe_snapshot or {}
    gate_deep_snapshot = gate_deep_snapshot or {}

    regime_block = ""
    if regime_snapshot.get("live_like"):
        live_like = regime_snapshot.get("live_like")
        gate_label = "ON" if regime_snapshot.get("gate_on") else "OFF"
        votes = regime_snapshot.get("votes")
        valid = regime_snapshot.get("valid_rules")
        needed = regime_snapshot.get("needed_votes")
        dist_good = regime_snapshot.get("distance_to_good")
        dist_bad = regime_snapshot.get("distance_to_bad")
        w0 = regime_snapshot.get("window_start_utc")
        w1 = regime_snapshot.get("window_end_utc")
        dg = f"{float(dist_good):.4f}" if dist_good is not None else "NA"
        db = f"{float(dist_bad):.4f}" if dist_bad is not None else "NA"
        regime_block = f"""
  <div class='card'>
    <h2>regime 快照（来自 regime_review）</h2>
    <ul>
      <li>live-like: <code>{live_like}</code></li>
      <li>gate: <code>{gate_label}</code>（<code>{votes}/{valid}</code>，阈值 <code>{needed}</code>）</li>
      <li>distance: good=<code>{dg}</code>，bad=<code>{db}</code></li>
      <li>window: <code>{w0}</code> → <code>{w1}</code></li>
    </ul>
  </div>
"""

    gate_deep_block = ""
    if gate_deep_snapshot.get("freeze_gate"):
        freeze_gate = gate_deep_snapshot.get("freeze_gate", {})
        formal_current = gate_deep_snapshot.get("formal_current_gate", {}) or {}
        shadow_current = gate_deep_snapshot.get("shadow_current_decision", {}) or {}
        shadow_formal = gate_deep_snapshot.get("shadow_formal_gate_context", {}) or {}
        rules = freeze_gate.get("rules", []) or []
        rule_rows = ""
        for rule in rules:
            var = str(rule.get("variable", ""))
            threshold = rule.get("threshold")
            higher = bool(rule.get("higher_is_good", True))
            human = {
                "veto_active_rate": "最近30天里，有 short-leg jump veto 触发的 rebalance 占比；越高说明 loser 端更常出现‘先猛冲再转弱’的异常挤兑/离散环境。",
                "xs_dispersion_bps": "最近30天横截面离散度（universe dispersion）；越高说明强弱分化更明显，cross-sectional long-short 更有施展空间。",
                "ls_divergence_bps": "最近30天 long leg 与 veto-short leg 的平均表现差；越高说明多空两边确实在拉开，而不是只有单边噪声。",
            }.get(var, "")
            sign = "≥" if higher else "≤"
            rule_rows += (
                f"<tr><td><code>{var}</code></td><td><code>{sign} {float(threshold):.4f}</code></td>"
                f"<td>{human}</td></tr>"
            )

        formal_checks_rows = ""
        for check in formal_current.get("checks", []) or []:
            if not isinstance(check, dict):
                continue
            formal_checks_rows += (
                f"<tr><td><code>{check.get('variable')}</code></td>"
                f"<td><code>{float(check.get('value', 0.0)):.4f}</code></td>"
                f"<td><code>{float(check.get('threshold', 0.0)):.4f}</code></td>"
                f"<td><b>{'pass' if check.get('pass') else 'fail'}</b></td>"
                f"<td>{'yes' if check.get('valid', True) else 'no'}</td></tr>"
            )

        calc_mode = gate_deep_snapshot.get("formal_gate_calculation_mode") or formal_current.get("calculation_mode") or "causal_live_aligned"
        calc_note = gate_deep_snapshot.get("formal_gate_calculation_note") or formal_current.get("calculation_note") or "veto/xs 用决策时点可见信息；ls_divergence 只用已完成持有期的历史样本。"
        shadow_source_mode = gate_deep_snapshot.get("shadow_source_mode") or "unknown"
        shadow_frame_source_mode = gate_deep_snapshot.get("shadow_frame_source_mode") or shadow_source_mode
        shadow_recent_days = gate_deep_snapshot.get("shadow_current_decision_recent_days")
        shadow_runtime = gate_deep_snapshot.get("shadow_runtime", {}) or {}
        shadow_runtime_note = ""
        if shadow_source_mode:
            recent_days_text = f"；当前 tail 关注窗 <code>{int(shadow_recent_days)}</code> 天" if shadow_recent_days is not None else ""
            shadow_runtime_note = f"""
      <div class=\"note\"><b>再把 shadow 运行态说人话：</b>当前 raw-bar shadow 审计 lane 的 <code>source_mode</code> 是 <code>{shadow_source_mode}</code>（frame=<code>{shadow_frame_source_mode}</code>）{recent_days_text}。这表示它现在会<strong>优先沿用已有 recent ledger，只重刷尾部 overlap + 最新 live row</strong>，而不是每次都把整段最近窗口从零重算。<br/>
        但也要诚实：这还<strong>不是</strong>最极致的“单 bar append/drop、全程 O(1) ledger 更新”；更准确的叫法是 <b>incremental tail refresh</b>。当前页面把它当作 <b>shadow / audit lane</b>，不是 live execution lane。</div>
"""
        causal_note = f"""
      <div class=\"good\"><b>这次把 shadow / formal / monthly rebuild 的 gate 口径统一成 causal 版了。</b><br/>
        计算模式：<code>{calc_mode}</code><br/>
        规则口径：{calc_note}</div>
      {shadow_runtime_note}
"""

        gate_deep_block = f"""
    <div class='card'>
      <h2>gate 到底是不是同一套？什么时候会开？</h2>
      <div class="good"><b>先给结论：</b>当前网页、formal 5~6 年回测、monthly rebuild、以及最新 shadow decision 用的，都是同一套 frozen <code>regime_gate_v1</code>；并且现在统一成 <b>causal / live-aligned</b> 口径：最近 <code>{freeze_gate.get('lookback_days')}</code> 天滚动窗口，按 3 条规则投票；只要 <code>votes &gt;= ceil(valid_rules × {float(freeze_gate.get('vote_ratio', 0.67)):.2f})</code> 就 <b>ON</b>，否则 <b>OFF</b>。OFF 时不是反手，而是 <code>{freeze_gate.get('off_action')}</code>。</div>
      <table>
        <thead>
          <tr><th>gate 变量</th><th>阈值</th><th>它在看什么</th></tr>
        </thead>
        <tbody>
          {rule_rows}
        </tbody>
      </table>
      <ul>
        <li><b>规则不是“永远写死必须 3/3”。</b> 正式定义是 <code>ceil(valid_rules × 0.67)</code>。在成熟样本里通常是三条都有效，因此当前这版多数时候等价于 <b>3/3 才 ON</b>；若冷启动或数据覆盖缺口导致有效规则减少，则按当时 <code>valid_rules</code> 自动重算门槛。</li>
        <li><b>所以你问“是三者都达到，还是达到其中几个？”</b>——严格答案是：<b>看当时有效规则数</b>。而在当前成熟运行链路里，重点是三条规则已经能按 causal 口径完整评估。</li>
      </ul>
      <h3>当前这两层“ON”要分开看</h3>
      <table>
        <thead>
          <tr><th>观察面</th><th>窗口 / bar</th><th>当前状态</th><th>你该怎么读</th></tr>
        </thead>
        <tbody>
          <tr>
            <td><code>formal current gate snapshot</code></td>
            <td><code>{formal_current.get('window_start_utc')}</code> → <code>{formal_current.get('window_end_utc')}</code></td>
            <td><b>{'ON' if formal_current.get('gate_on') else 'OFF'}</b>（<code>{formal_current.get('votes')}</code>/<code>{formal_current.get('valid_rules')}</code>，阈值 <code>{formal_current.get('needed_votes')}</code>）</td>
            <td>这是和长期 formal 回测同定义的一层，并且明确按 causal/live-aligned 方式计算。</td>
          </tr>
          <tr>
            <td><code>latest raw-bar shadow decision</code></td>
            <td><code>{shadow_current.get('decision_ts')}</code></td>
            <td><b>{'ON' if shadow_current.get('gate_on') else 'OFF'}</b>（<code>{shadow_current.get('gate_votes')}</code>/<code>{shadow_current.get('gate_valid_rules')}</code>，阈值 <code>{shadow_current.get('gate_needed_votes')}</code>）</td>
            <td>这是最新实时 decision bar；现在 preview 行也会带上过去 30 天已实现样本，不再因为“当前这笔未走完”而丢第三条规则。</td>
          </tr>
        </tbody>
      </table>
      <h3>formal 当前窗口，三条规则具体过没过？</h3>
      <table>
        <thead>
          <tr><th>变量</th><th>当前值</th><th>阈值</th><th>是否通过</th><th>是否有效</th></tr>
        </thead>
        <tbody>
          {formal_checks_rows}
        </tbody>
      </table>
      <div class="note"><b>人话版：</b>当前不只是“运气好，刚好碰到 gate 开着”。从 formal 当前窗口看，三条指标都明显高过阈值：更像是<b>横截面分化、veto 活跃度、多空分化</b>同时处于强区间，所以 gate 打开。</div>
      {causal_note}
      <ul>
        <li><b>回答你最核心那句：</b>“此时此刻的 gate 和过去 5 年回测里的 gate 是不是一样？”——<b>现在定义和实现都对齐</b>：shadow / formal / monthly rebuild 按同一套 causal frozen gate。</li>
        <li><b>再翻成人话：</b>不是“随便碰巧 market 好一点就放行”。它要求最近 30 天里 <b>强弱分化够大、veto 异动够活跃、且多空分化够明显</b>；否则就 flat。</li>
      </ul>
    </div>
"""

    shadow_mode_label = gate_deep_snapshot.get("shadow_source_mode") or "unknown"
    cadence_compare = f"""
      <table>
        <thead>
          <tr><th>页面 / 运行面</th><th>核心公式</th><th>cadence</th><th>这里能不能说成当前 live runtime</th></tr>
        </thead>
        <tbody>
          <tr>
            <td><code>rank213_largecap_xs_jump_veto.html</code></td>
            <td>同一套 baseline + short-leg jump veto</td>
            <td><b>每 3h 非重叠一次</b>（UTC <code>02:15 / 05:15 / ...</code>）</td>
            <td><b>可以</b>；这是当前 frozen seed live/paper lane</td>
          </tr>
          <tr>
            <td><code>rank213_largecap_xs_jump_veto_shadow_runner</code></td>
            <td>同一套 baseline + short-leg jump veto + formal frozen gate</td>
            <td><b>每 15m raw-bar 审计刷新</b>；当前实现口径是 <code>{shadow_mode_label}</code></td>
            <td><b>不可以</b>；这是 shadow / audit lane，用来暴露最新决策与 gate 状态，不是当前 live execution lane</td>
          </tr>
          <tr>
            <td><code>formal_strategy_review</code> / <code>asof_universe_long_history_review</code></td>
            <td>同一套 baseline + short-leg jump veto</td>
            <td><b>每 15m rolling 重算一次</b></td>
            <td><b>不可以</b>；这是 research / formal evidence 口径，不是当前 live runtime cadence</td>
          </tr>
        </tbody>
      </table>
    """

    long_history_rows = ""
    for label in ("window_120d", "window_180d", "window_360d"):
        item = long_history_snapshot.get(label, {})
        days = label.replace("window_", "").upper()
        if item.get("available"):
            long_history_rows += (
                f"<tr><td><code>{days}</code></td><td><b>yes</b></td>"
                f"<td><code>{item['start_utc']}</code> → <code>{item['end_utc']}</code></td>"
                f"<td><code>{item['rebalances']}</code></td>"
                f"<td><code>{item['mean_net_bps']:.2f}</code></td>"
                f"<td><code>{item['cum_pct']:.4f}%</code></td>"
                f"<td>同口径 frozen current-universe historical recompute</td></tr>"
            )
        elif item:
            long_history_rows += (
                f"<tr><td><code>{days}</code></td><td><b>no</b></td>"
                f"<td>—</td><td>—</td><td>—</td><td>—</td>"
                f"<td>{item.get('reason', 'unavailable')}（可用共同历史约 <code>{item.get('available_days', 0.0):.2f}</code> 天）</td></tr>"
            )

    long_history_block = ""
    if long_history_snapshot:
        full_hist = long_history_snapshot.get("full_available_history", {})
        long_history_block = f"""
    <div class='card'>
      <h2>更长周期：我们现在到底有什么数据？</h2>
      <div class="warn"><b>先把边界说清楚：</b>在<b>当前 frozen current-universe</b> 的同口径检查里，公共共同历史最多只到 <code>{long_history_snapshot.get('common_history_days', 0.0):.2f}</code> 天（<code>{long_history_snapshot.get('available_start_utc')}</code> → <code>{long_history_snapshot.get('available_end_utc')}</code>）。所以 <b>120D 可以算</b>；但 <b>180D / 360D 不能在同一 frozen current-universe 口径下硬算</b>。</div>
      <table>
        <thead>
          <tr><th>窗口</th><th>是否可用</th><th>覆盖区间</th><th>rebalances</th><th>mean net bps</th><th>cum return</th><th>备注</th></tr>
        </thead>
        <tbody>
          <tr>
            <td><code>MAX AVAILABLE</code></td>
            <td><b>yes</b></td>
            <td><code>{long_history_snapshot.get('available_start_utc')}</code> → <code>{long_history_snapshot.get('available_end_utc')}</code></td>
            <td><code>{long_history_snapshot.get('rebalances', 0)}</code></td>
            <td><code>{float(full_hist.get('net_mean_bps', 0.0)):.2f}</code></td>
            <td><code>{float(full_hist.get('net_cum_pct', 0.0)):.4f}%</code></td>
            <td>这是当前 frozen current-universe 同 spec 的最大可用共同历史</td>
          </tr>
          {long_history_rows}
        </tbody>
      </table>
      <ul>
        <li><b>120D 现在有数据：</b>当前同口径 historical recompute 给到 <b>{long_history_snapshot.get('window_120d', {}).get('cum_pct', 0.0):.4f}%</b>，对应 <b>{long_history_snapshot.get('window_120d', {}).get('mean_net_bps', 0.0):.2f} bps/笔</b>、<b>{long_history_snapshot.get('window_120d', {}).get('rebalances', 0)}</b> 笔。</li>
        <li><b>180D / 360D 现在不要乱说：</b>不是结果不好所以不报，而是<b>同一 frozen current-universe 的共同历史根本不够长</b>。</li>
        <li>如果要看更长（1Y/2Y/3Y/5Y/6Y），目前只能去看独立的 <code>asof_universe_long_history_review</code> / <code>formal_strategy_review</code> / <code>monthly_volume_universe_rebuild</code> 这类<strong>不同证据面</strong>，不能直接冒充为这页 frozen current-universe 已验证通过。</li>
      </ul>
    </div>
"""

    universe_transparency_block = ""
    verdict_block = ""
    monthly_rebuild_block = ""
    if universe_snapshot:
        asof_snapshot = universe_snapshot.get("asof", {})
        formal_snapshot = universe_snapshot.get("formal", {})
        monthly_snapshot = universe_snapshot.get("monthly", {})
        audit_snapshot = universe_snapshot.get("audit", {})
        rows = [
            f"""<tr>
              <td><code>当前 live/paper runner</code></td>
              <td><b>不会</b></td>
              <td>固定读取 admission 冻结的 <code>{status['universe_size']}</code> 币名单；refresh 只更新新 signal / ledger，不按月或按季度重选 Top30。</td>
              <td><code>{status['sample_start_utc']}</code> → <code>{status['sample_end_utc']}</code></td>
              <td><code>{status['lifetime_total_return']:.4%}</code>（<code>{status['closed_trades']}</code> 笔）</td>
              <td>这才是当前真正跑着的口径；但它不是历史滚动 Top30 证据。</td>
            </tr>"""
        ]
        if long_history_snapshot:
            full_hist = long_history_snapshot.get("full_available_history", {})
            rows.append(
                f"""<tr>
                  <td><code>frozen current-universe historical recompute</code></td>
                  <td><b>不会</b></td>
                  <td>还是同一份 frozen 30 币名单；只是把当前名单往历史上硬回放。</td>
                  <td><code>{long_history_snapshot.get('available_start_utc')}</code> → <code>{long_history_snapshot.get('available_end_utc')}</code></td>
                  <td>MAX <code>{float(full_hist.get('net_cum_pct', 0.0)):.4f}%</code>；120D <code>{float(long_history_snapshot.get('window_120d', {}).get('cum_pct', 0.0)):.4f}%</code></td>
                  <td>能回答“当前 frozen 名单最近共同历史怎样”，不能回答“历史上是否该滚动换池”。</td>
                </tr>"""
            )
        if asof_snapshot:
            sample = asof_snapshot.get("sample", {})
            full_veto = asof_snapshot.get("full_veto", {})
            rows.append(
                f"""<tr>
                  <td><code>asof_universe_long_history_review</code></td>
                  <td><b>不按 Top30 重选</b></td>
                  <td>仍是 frozen 30 币种子名单；只是名字会在各自 <b>onboard 之后</b> 才参与排名，所以是“按上线时间可见”，不是“按历史市值滚动换池”。</td>
                  <td><code>{sample.get('start_utc')}</code> → <code>{sample.get('end_utc')}</code>；平均可交易 universe <code>{float(sample.get('avg_eligible_universe_size', 0.0)):.2f}</code></td>
                  <td>全周期 veto <code>{float(full_veto.get('net_cum_pct', 0.0)):.4f}%</code></td>
                  <td>它解决的是“后上市名字不能穿越历史提前参赛”；但仍不是你说的“每月/每段时间滚动 Top30”。</td>
                </tr>"""
            )
        if formal_snapshot:
            sample = formal_snapshot.get("sample", {})
            full_gate = formal_snapshot.get("full_gate", {})
            gate = formal_snapshot.get("gate", {})
            rows.append(
                f"""<tr>
                  <td><code>formal_strategy_review</code></td>
                  <td><b>不按 Top30 重选</b></td>
                  <td>名单逻辑继承 <code>asof_universe</code>：仍是 frozen 30 币 + onboard 可见性；区别只是再叠加 frozen regime gate。</td>
                  <td><code>{sample.get('start_utc')}</code> → <code>{sample.get('end_utc')}</code>；gate ON rate <code>{float(gate.get('on_rate_pct', 0.0)):.2f}%</code></td>
                  <td>baseline+veto+gate 全周期 <code>{float(full_gate.get('net_cum_pct', 0.0)):.4f}%</code></td>
                  <td>这是当前最强的 formal 证据面，但它也不是历史滚动市值 Top30 回测。</td>
                </tr>"""
            )
        if monthly_snapshot:
            sample = monthly_snapshot.get("sample", {})
            coverage = monthly_snapshot.get("coverage", {})
            full_gate = monthly_snapshot.get("full_gate", {})
            rows.append(
                f"""<tr>
                  <td><code>monthly_volume_universe_rebuild</code></td>
                  <td><b>会（月度重建）</b></td>
                  <td>按月用 volume-proxy 重建 as-of universe；这是当前文件里最接近“历史滚动 Top30”的证据面。</td>
                  <td><code>{sample.get('start_utc')}</code> → <code>{sample.get('end_utc')}</code>；与 frozen30 平均重叠 <code>{float(coverage.get('avg_overlap_with_frozen30', 0.0)):.2f}</code>/30</td>
                  <td>baseline+veto+gate 全周期 <code>{float(full_gate.get('net_cum_pct', 0.0)):.4f}%</code></td>
                  <td><b>如果你要问“历史上不固定某一时刻 Top30，滚动换池以后还行不行？”</b>，当前最应该看的就是这一行。</td>
                </tr>"""
            )
        audit_note = ""
        if audit_snapshot:
            honesty = audit_snapshot.get("selection_honesty", {})
            survivor = audit_snapshot.get("survivorship_bias_risk", {})
            audit_note = (
                f"<li><b>selection 风险披露：</b>universe audit 认为 frozen30 在 selection 维度存在 survivorship bias 风险（status=<code>{survivor.get('status', 'unknown')}</code>）；"
                f"同时 original selection uses only then-visible info 的检查结果是 <code>{honesty.get('status', 'unknown')}</code>。</li>"
            )
        universe_transparency_block = f"""
    <div class='card'>
      <h2>标的选择 / Universe 更新：这页现在把口径拆开讲清楚</h2>
      <div class="warn"><b>关键统一：</b>讨论长周期时，不能把“固定某一时刻的 Top30”直接当成“历史滚动 Top30”。当前 rank213 相关文件里，至少有 4 种证据面；其中只有 <code>monthly_volume_universe_rebuild</code> 接近“按时间滚动重选 Top30”。</div>
      <table>
        <thead>
          <tr><th>页面 / 证据面</th><th>名单会不会更新</th><th>它到底怎么选池</th><th>样本覆盖</th><th>结果摘要</th><th>你该怎么理解</th></tr>
        </thead>
        <tbody>
          {''.join(rows)}
        </tbody>
      </table>
      <ul>
        <li><b>直接回答：</b>当前这条正在跑的 <b>live/paper runner 没有按月更新 Top30</b>；它跑的是 frozen admission 30 币名单。</li>
        <li><b>第二个关键点：</b><code>asof_universe_long_history_review</code> 也<b>不是</b>“每月滚动 Top30”；它只是解决“币在历史上还没上市时不能提前参赛”的问题。</li>
        <li><b>如果你要看真正更接近“历史滚动换池”的证据</b>，当前应该优先看 <code>monthly_volume_universe_rebuild</code>。</li>
        {audit_note}
      </ul>
    </div>
"""

        monthly_gate = monthly_snapshot.get("full_gate", {})
        formal_gate = formal_snapshot.get("full_gate", {})
        asof_veto = asof_snapshot.get("full_veto", {})
        verdict_block = f"""
    <div class='card'>
      <h2>最终裁决卡：这几条证据到底该怎么用</h2>
      <div class="good"><b>先给最终版人话：</b>如果你问“<b>现在实际跑的</b>是什么”，答案看 <code>当前 live/paper runner</code>；如果你问“<b>历史上滚动换池以后</b>还站不站得住”，当前优先看 <code>monthly_volume_universe_rebuild</code>；如果你问“<b>同一 frozen 名单</b> 最近共同历史怎样”，看 <code>frozen current-universe historical recompute</code>；如果你问“<b>后上市币不要穿越参赛</b> 后会怎样”，看 <code>asof_universe_long_history_review</code>。</div>
      <table>
        <thead>
          <tr><th>你真正想回答的问题</th><th>默认应看哪条证据</th><th>一句话裁决</th></tr>
        </thead>
        <tbody>
          <tr>
            <td>当前 live/paper 到底是不是会定期更新 Top30？</td>
            <td><code>当前 live/paper runner</code></td>
            <td><b>不会。</b> 当前运行口径是 frozen admission 30-symbol universe，不做 monthly/quarterly rebuild。</td>
          </tr>
          <tr>
            <td>同一份 frozen30 名单，最近共同历史表现怎样？</td>
            <td><code>frozen current-universe historical recompute</code></td>
            <td><b>近期共同历史是强的</b>，但它只是在回答“当前名单往回推”这一题，不是在回答历史滚动换池。</td>
          </tr>
          <tr>
            <td>把未上市币穿越问题修掉以后，这策略还怎样？</td>
            <td><code>asof_universe_long_history_review</code></td>
            <td><b>as-of 修正后，全周期 veto 是负的</b>（<code>{float(asof_veto.get('net_cum_pct', 0.0)):.4f}%</code>）；所以不能再把 as-of 读成“已经证明长期稳定赚钱”。</td>
          </tr>
          <tr>
            <td>如果真的按时间滚动换池，而不是固定某一刻 Top30，会怎样？</td>
            <td><code>monthly_volume_universe_rebuild</code></td>
            <td><b>不支持强结论</b>：当前最接近滚动换池的 full-period <code>baseline+veto+gate</code> 为 <code>{float(monthly_gate.get('net_cum_pct', 0.0)):.4f}%</code>，远弱于 formal 页那条 <code>{float(formal_gate.get('net_cum_pct', 0.0)):.4f}%</code>。</td>
          </tr>
        </tbody>
      </table>
      <ul>
        <li><b>默认优先级建议：</b>讨论“运行事实”时先看 <code>live/paper runner</code>；讨论“最新 15m 审计态 / gate 是否开门”时看 <code>shadow_runner</code>；讨论“历史严谨性”时先看 <code>monthly_volume_universe_rebuild</code>；<code>asof</code> 只负责解决上市时点可见性，不负责证明滚动换池有效。</li>
        <li><b>因此这页现在的统一口径应该是：</b>Rank213 当前可以被描述为“<b>一个正在运行的 frozen30 paper/live lane</b>，外加一个 15m raw-bar 的 shadow/audit lane”；但<b>不能</b>直接被描述为“历史滚动 Top30 已被长周期验证通过的策略”。</li>
        <li><b>如果以后要做更正式的历史口径升级</b>，下一步不是再重复 frozen30/asof，而是继续把 <code>monthly_volume_universe_rebuild</code> 做得更接近真实历史 market cap / liquidity rebuild，同时再把 shadow runner 从当前的 <b>incremental tail refresh</b> 继续收成更纯的 append/drop rolling ledger。</li>
      </ul>
    </div>
"""

        month_summary = monthly_snapshot.get("month_summary", {})
        yearly_rows = monthly_snapshot.get("yearly_rows", [])
        curve_svg = monthly_snapshot.get("curve_svg", "")
        limitation = monthly_snapshot.get("important_limitation", "")
        yearly_table = "".join(
            f"<tr><td><code>{row['year']}</code></td><td><code>{row['year_ret_pct']:.4f}%</code></td><td><code>{row['positive_months']}</code></td><td><code>{row['negative_months']}</code></td><td><code>{row['flat_months']}</code></td><td><code>{row['gate_on_baskets']}</code></td></tr>"
            for row in yearly_rows
        )
        monthly_rebuild_block = f"""
    <div class='card'>
      <h2>如果按“月度重构 universe”口径看，过去 5~6 年曲线长什么样？</h2>
      <div class="good"><b>先直接回答你的问题：</b>按当前 <code>monthly_volume_universe_rebuild</code> 的 <code>baseline+veto+gate</code> 口径，样本从 <code>{monthly_snapshot.get('sample', {}).get('start_utc')}</code> 到 <code>{monthly_snapshot.get('sample', {}).get('end_utc')}</code>，约 <b>{month_summary.get('sample_years', 0.0):.2f}</b> 年 / <b>{month_summary.get('total_months', 0)}</b> 个自然月，full-period 累计净收益是 <b>{float(monthly_snapshot.get('full_gate', {}).get('net_cum_pct', 0.0)):.4f}%</b>。严格说，这不是“整整 6 年固定历史市值真值回测”，而是 <b>volume-proxy 月度重建</b> 下的最好现有近似证据面。</div>
      <div class="note"><b>手续费口径也可以钉死：</b>这里不是 <code>5/10000</code> 单边。当前代码/产物的净收益口径等价于 <code>net = gross - {float(monthly_snapshot.get('cost_roundtrip_bps_per_turnover_x', 0.0)):.1f}bps × turnover_x</code>。也就是说：当 <code>turnover_x = 1.0</code> 时，按的是 <b>{float(monthly_snapshot.get('cost_roundtrip_bps_per_turnover_x', 0.0)):.1f} bps round-trip</b>，等价于大约 <b>{float(monthly_snapshot.get('cost_per_side_bps_if_turnover_1x', 0.0)):.1f} bps / 10000 每边</b>；不是 <b>5 bps/10000</b>。如果某笔因为 veto refill 导致 <code>turnover_x &gt; 1</code>，成本会按这个 turnover 比例继续放大。</div>
      <div class="warn"><b>这条曲线非常不“顺滑上行”：</b>按月末口径看，<b>{month_summary.get('positive_months', 0)}</b> 个盈利月、<b>{month_summary.get('negative_months', 0)}</b> 个亏损月、<b>{month_summary.get('flat_months', 0)}</b> 个持平月。也就是说，这 5~6 年不是“每个月都赚”，而是 <b>绝大多数月份 gate 根本没开、月收益为 0</b>，收益主要集中在少数开启月份里。注意：full-period 里的月内路径最大回撤仍有 <code>{float(monthly_snapshot.get('full_gate', {}).get('max_drawdown_pct', 0.0)):.4f}%</code>，所以月末曲线会比真实 3h-basket 路径更平。</div>
      {curve_svg}
      <table>
        <thead>
          <tr><th>月度重构口径的关键问题</th><th>当前答案</th></tr>
        </thead>
        <tbody>
          <tr><td>过去 5~6 年 total return 到底是多少？</td><td><b>不是 11.7%。</b> 当前 full-period <code>baseline+veto+gate</code> 为 <code>{float(monthly_snapshot.get('full_gate', {}).get('net_cum_pct', 0.0)):.4f}%</code>。</td></tr>
          <tr><td>是不是每个月都盈利？</td><td><b>不是。</b> 当前月末口径下是 <code>{month_summary.get('positive_months', 0)}</code> 个盈利月、<code>{month_summary.get('negative_months', 0)}</code> 个亏损月、<code>{month_summary.get('flat_months', 0)}</code> 个持平月。</td></tr>
          <tr><td>最好 / 最差月分别是哪一个？</td><td>最好月是 <code>{month_summary.get('best_month')}</code>，月度链式收益 <code>{float(month_summary.get('best_month_ret_pct', 0.0)):.4f}%</code>；最差月是 <code>{month_summary.get('worst_month')}</code>，收益 <code>{float(month_summary.get('worst_month_ret_pct', 0.0)):.4f}%</code>。</td></tr>
          <tr><td>为什么月度曲线看起来这么平？</td><td>因为这条线的 <code>gate_on_rate</code> 只有 <code>{float(monthly_snapshot.get('full_gate', {}).get('gate_on_rate_pct', 0.0)):.4f}%</code>；绝大部分 3h rebalance 都被 gate 关掉了，所以月末大多是 0 变化。</td></tr>
        </tbody>
      </table>
      <h3>按年拆开看（月度重构 × baseline+veto+gate）</h3>
      <table>
        <thead>
          <tr><th>年份</th><th>全年累计收益</th><th>盈利月数</th><th>亏损月数</th><th>持平月数</th><th>gate-on baskets</th></tr>
        </thead>
        <tbody>
          {yearly_table}
        </tbody>
      </table>
      <ul>
        <li><b>最重要的人话：</b>这不是一条“每个月都在稳定赚钱”的线，而更像一条 <b>长期大部分时间不动、少数月份跳一下</b> 的机会型曲线。</li>
        <li><b>所以任何单一正收益口径</b> 都不能被读成“这条策略 6 年里月月赚钱、慢慢上涨”。更准确的读法是：<b>在月度重构 + gate 之后，旧 15m 母体证据明显偏弱，收益高度集中且回撤很深。</b></li>
        <li><b>这条证据面的限制也别忘：</b>{limitation}</li>
      </ul>
    </div>
"""

    example_rows = [
        ("ALPHA", "+12.4%", "1.0%", "long", "过去 16h 最强，进 top-3 long"),
        ("BETA", "+9.1%", "1.4%", "long", "过去 16h 第二强，进 top-3 long"),
        ("GAMMA", "+5.6%", "1.8%", "long", "过去 16h 第三强，进 top-3 long"),
        ("DELTA", "-4.2%", "1.3%", "refill short", "原本不是 bottom-3，但因为 veto refill 被补进 short"),
        ("EPSILON", "-7.8%", "1.4%", "plain short", "bottom-3 loser，且 max-up-bar 未超阈值"),
        ("PHI", "-9.5%", "3.9%", "vetoed", "bottom-3 loser，但 16h 内出现异常 15m 上冲，被 veto"),
        ("OMEGA", "-11.2%", "1.1%", "plain short", "最弱 loser，进入 short"),
    ]
    example_table = "".join(
        f"<tr><td><code>{sym}</code></td><td>{cumret}</td><td>{mx}</td><td>{role}</td><td>{note}</td></tr>"
        for sym, cumret, mx, role, note in example_rows
    )

    example_svg = """
      <svg viewBox="0 0 860 240" width="100%" height="240" role="img" aria-label="rank213 example ranking and veto flow">
        <rect x="18" y="20" width="824" height="194" rx="14" fill="#fff" stroke="#dbe4f0"/>
        <line x1="130" y1="50" x2="130" y2="190" stroke="#cbd5e1" stroke-dasharray="4 4"/>
        <text x="26" y="40" fill="#475569" font-size="12">formation = 64 × 15m = 16h；按首尾 close 算 cumret</text>
        <text x="26" y="58" fill="#475569" font-size="12">阈值 = max(1.5%, 2.0 × 全市场 median(max-up-bar)) = max(1.5%, 2.0 × 1.6%) = 3.2%</text>
        <line x1="130" y1="120" x2="810" y2="120" stroke="#94a3b8" stroke-dasharray="4 4"/>

        <rect x="150" y="86" width="126" height="22" rx="8" fill="#16a34a"/>
        <text x="158" y="101" fill="#fff" font-size="12">ALPHA +12.4%</text>
        <rect x="150" y="112" width="103" height="22" rx="8" fill="#16a34a"/>
        <text x="158" y="127" fill="#fff" font-size="12">BETA +9.1%</text>
        <rect x="150" y="138" width="79" height="22" rx="8" fill="#16a34a"/>
        <text x="158" y="153" fill="#fff" font-size="12">GAMMA +5.6%</text>
        <text x="286" y="101" fill="#166534" font-size="12">top-3 → long</text>
        <text x="263" y="127" fill="#166534" font-size="12">top-3 → long</text>
        <text x="239" y="153" fill="#166534" font-size="12">top-3 → long</text>

        <rect x="500" y="134" width="67" height="22" rx="8" fill="#dc2626"/>
        <text x="508" y="149" fill="#fff" font-size="12">DELTA -4.2%</text>
        <text x="574" y="149" fill="#7f1d1d" font-size="12">refill 候选</text>

        <rect x="500" y="160" width="97" height="22" rx="8" fill="#dc2626"/>
        <text x="508" y="175" fill="#fff" font-size="12">EPSILON -7.8%</text>
        <text x="603" y="175" fill="#7f1d1d" font-size="12">bottom-3；1.4% ≤ 3.2% → 保留</text>

        <rect x="500" y="186" width="113" height="22" rx="8" fill="#dc2626"/>
        <text x="508" y="201" fill="#fff" font-size="12">OMEGA -11.2%</text>
        <text x="620" y="201" fill="#7f1d1d" font-size="12">bottom-3；1.1% ≤ 3.2% → 保留</text>

        <rect x="500" y="108" width="88" height="22" rx="8" fill="#f59e0b"/>
        <text x="508" y="123" fill="#111827" font-size="12">PHI -9.5%</text>
        <text x="596" y="123" fill="#92400e" font-size="12">bottom-3；3.9% &gt; 3.2% → veto</text>

        <path d="M 593 118 C 650 96, 680 96, 735 118" fill="none" stroke="#f59e0b" stroke-width="2.4" marker-end="url(#arrow)"/>
        <path d="M 567 144 C 645 144, 685 144, 760 144" fill="none" stroke="#dc2626" stroke-width="2.4" marker-end="url(#arrowRed)"/>

        <rect x="700" y="70" width="120" height="30" rx="10" fill="#0f172a"/>
        <text x="712" y="89" fill="#fff" font-size="12">最终执行篮子</text>
        <text x="712" y="106" fill="#cbd5e1" font-size="11">long = ALPHA,BETA,GAMMA</text>
        <text x="712" y="122" fill="#cbd5e1" font-size="11">short = OMEGA,EPSILON,DELTA</text>

        <defs>
          <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
            <polygon points="0 0, 6 3, 0 6" fill="#f59e0b"/>
          </marker>
          <marker id="arrowRed" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
            <polygon points="0 0, 6 3, 0 6" fill="#dc2626"/>
          </marker>
        </defs>
      </svg>
    """

    body = f'''<!doctype html>
<html lang="zh">
<head>
  <meta charset="utf-8" />
  <title>Rank 213 Paper Runner</title>
  <style>
    :root {{ color-scheme: light; }}
    body {{ font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif; margin: 0; background: #f8fafc; color: #0f172a; line-height: 1.6; }}
    .wrap {{ max-width: 1180px; margin: 0 auto; padding: 24px 16px 56px; }}
    .card {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 18px 20px; margin-bottom: 16px; box-shadow: 0 1px 2px rgba(15,23,42,0.04); }}
    .hero {{ background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%); }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }}
    .metric {{ border: 1px solid #e2e8f0; border-radius: 12px; padding: 12px; background: #fbfdff; }}
    .metric .k {{ color: #64748b; font-size: 12px; text-transform: uppercase; letter-spacing: .04em; }}
    .metric .v {{ font-size: 22px; font-weight: 700; margin-top: 6px; }}
    .note {{ background: #eff6ff; border-left: 4px solid #2563eb; padding: 12px 14px; border-radius: 10px; }}
    .warn {{ background: #fff7ed; border-left: 4px solid #ea580c; padding: 12px 14px; border-radius: 10px; }}
    .good {{ background: #f0fdf4; border-left: 4px solid #16a34a; padding: 12px 14px; border-radius: 10px; }}
    code {{ background: #eef2ff; padding: 2px 5px; border-radius: 6px; }}
    pre {{ background: #0f172a; color: #e2e8f0; padding: 14px; border-radius: 12px; overflow: auto; font-size: 12px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #e2e8f0; padding: 10px 8px; text-align: left; vertical-align: top; }}
    th {{ color: #475569; background: #f8fafc; }}
    ul {{ margin-top: 8px; }}
    a {{ color: #2563eb; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .pill {{ display: inline-block; padding: 4px 9px; border-radius: 999px; background: #e2e8f0; font-size: 12px; margin-right: 6px; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class='card hero'>
      <h1>Rank 213 / large-cap XS momentum × short-leg jump veto</h1>
      <p><strong>接线状态：</strong>{status['wiring_status']}</p>
      <div class="grid">
        <div class="metric"><div class="k">runner</div><div class="v"><code>{status['runner_script']}</code></div></div>
        <div class="metric"><div class="k">runner mode</div><div class="v"><code>{status['runner_mode']}</code></div></div>
        <div class="metric"><div class="k">frozen variant</div><div class="v"><code>{status['variant']}</code></div></div>
        <div class="metric"><div class="k">最近更新时间</div><div class="v"><code>{status['updated_at_utc']}</code></div></div>
        <div class="metric"><div class="k">闭合 basket 数</div><div class="v">{status['closed_trades']}</div></div>
        <div class="metric"><div class="k">平均净收益 / 每笔 3h basket</div><div class="v">{status['mean_net_bps']:.2f} bps</div></div>
        <div class="metric"><div class="k">累计净收益 / 链式复利</div><div class="v">{status['lifetime_total_return']:.4%}</div></div>
        <div class="metric"><div class="k">scheduler</div><div class="v"><code>{status['service_unit']}</code><br/><code>{status['timer_unit']}</code></div></div>
      </div>
      <p class="note"><b>这页现在锁定的是当前 live 真正在跑的 frozen runtime 定义：</b>它读的是 admission 已冻结的 timeseries seed，用来把 P3 接线显式化；<b>它不是 raw-bar live recomputation</b>。因此本页的“硬定义”以 frozen seed runtime 为准，不拿 rolling research 口径来偷换。</p>
      <p class="warn"><b>先看证据地图：</b><a href="/momentum/paper/rank213_evidence_map.html">Rank213 Evidence Map</a> 已把 current runtime、monthly-volume causal history、as-of 修正、live audit、退役证据分层。后续讨论历史有效性时，默认先从这张地图进入。</p>
    </div>

    <div class='card'>
      <h2>这两个数字到底怎么算？</h2>
      <div class="good"><b>一句话：</b>这页里的每一笔，不是单个币、也不是任意时点滚动交易；而是 <b>1 个固定持有 3 小时的 market-neutral basket</b>。当前 frozen live 版每 <b>3 小时</b> 才开一笔新 basket，并持有到 <b>3 小时后</b> 时间退出；这 3 小时里，<b>不做二次换仓、不做持仓内重排</b>。</div>
      <table>
        <thead>
          <tr><th>字段</th><th>当前页面的实际含义</th><th>当前值</th></tr>
        </thead>
        <tbody>
          <tr>
            <td><code>平均净收益</code></td>
            <td>对每笔 closed basket 先算 <code>net_bps = gross_bps - 4.0 × turnover_x</code>，再对全部 closed baskets 做<strong>算术平均</strong>。所以它表示的是：<b>平均每笔 3h basket 赚多少 bps</b>。</td>
            <td><code>{status['mean_net_bps']:.2f} bps / 笔</code></td>
          </tr>
          <tr>
            <td><code>累计净收益</code></td>
            <td>不是把每笔 bps 直接相加，而是把每笔净收益先转成 <code>net_ret = net_bps / 10000</code>，然后按 <code>∏(1 + net_ret) - 1</code> 做<strong>链式复利</strong>。所以它表示的是：<b>按这批 closed baskets 顺序连续滚下去后的累计净值变化</b>。</td>
            <td><code>{status['lifetime_total_return']:.4%}</code></td>
          </tr>
          <tr>
            <td><code>闭合 basket 数</code></td>
            <td>当前累计纳入统计的 closed baskets 数量；每一笔都对应 1 次 <b>3h 非重叠持有</b>。</td>
            <td><code>{status['closed_trades']}</code> 笔</td>
          </tr>
          <tr>
            <td><code>持有时间</code></td>
            <td>固定 <code>HOLD_BARS = 12</code> 根 <code>15m</code> bar，即 <b>3 小时</b>；持有窗内不再二次开新 basket。</td>
            <td><code>3h</code></td>
          </tr>
        </tbody>
      </table>
      <ul>
        <li>把它翻成人话：当前页面上的 <b>{status['mean_net_bps']:.2f} bps</b>，意思不是“每天平均赚这么多”，也不是“每小时平均赚这么多”，而是：<b>这 {status['closed_trades']} 笔 3 小时 basket 的单笔净收益均值约为 +{status['mean_net_bps']:.2f} bps</b>。</li>
        <li><b>{status['lifetime_total_return']:.4%}</b> 也不是年化；它表示的是：按这批 closed baskets 的先后顺序，把每笔净收益链式滚动以后，累计净值大约变成 <b>{1.0 + float(status['lifetime_total_return']):.4f}x</b>。</li>
      </ul>
    </div>

    <div class='card'>
      <h2>为什么每笔只有 {status['mean_net_bps']:.2f} bps，却还能滚到 {status['lifetime_total_return']:.4%}？</h2>
      <div class="good"><b>核心不是“单笔很大”，而是“单笔期望为正 × 频率很高 × 连续复利”</b>。这页是 <b>{status['closed_trades']}</b> 笔、约 <b>{status['trades_per_day']:.2f}</b> 笔/天、每笔持有 <b>3h</b> 的非重叠 basket，不是一天只做 1 笔。</div>
      <table>
        <thead>
          <tr><th>拆解项</th><th>当前值</th><th>它说明什么</th></tr>
        </thead>
        <tbody>
          <tr><td>每笔平均净收益</td><td><code>{status['mean_net_bps']:.2f} bps = {100 * status['mean_net_ret']:.4f}%</code></td><td>单笔看起来不大，但因为频次高，可以被复利放大。</td></tr>
          <tr><td>总笔数</td><td><code>{status['closed_trades']}</code> 笔</td><td>{status['trade_window_days']:.2f} 天里大约做了 <code>{status['closed_trades']}</code> 次 3h basket。</td></tr>
          <tr><td>如果“每笔都刚好等于均值”</td><td><code>{status['naive_compound_from_mean']:.4%}</code></td><td>这只是一个均值复利的直觉参考，不是实际路径。</td></tr>
          <tr><td>实际 realized cumulative</td><td><code>{status['lifetime_total_return']:.4%}</code></td><td>真实路径比“均值机械复利”略低，说明中间有波动拖累（volatility drag）。</td></tr>
          <tr><td>单笔收益中位数</td><td><code>{status['median_net_bps']:.2f} bps</code></td><td>说明平均值会被一部分大赢单往上拉；典型一笔并没有均值那么高。</td></tr>
          <tr><td>单笔离散度</td><td><code>std = {status['std_net_bps']:.2f} bps</code></td><td>分布很宽，不能把均值误读成“每笔都稳定赚 22bps”。</td></tr>
          <tr><td>最好 / 最差一笔</td><td><code>{status['best_net_bps']:.2f}</code> / <code>{status['worst_net_bps']:.2f} bps</code></td><td>尾部分布很重；大赢单对最终复利贡献不小。</td></tr>
          <tr><td>非正收益占比</td><td><code>{status['nonpositive_trade_rate']:.2%}</code></td><td>接近一半的单子并不赚钱，所以这个结果绝不是“几乎单单都赢”。</td></tr>
        </tbody>
      </table>
      <ul>
        <li>如果只看 <b>{status['mean_net_bps']:.2f} bps/笔</b>，会觉得“很小”；但别忘了这是 <b>{status['closed_trades']}</b> 次非重叠复利，而不是 1 次。</li>
        <li>这批样本里，“按均值机械复利”大约会到 <b>{status['naive_compound_from_mean']:.4%}</b>；实际是 <b>{status['lifetime_total_return']:.4%}</b>，两者差距就是路径波动带来的 drag。</li>
        <li>所以更准确的人话是：<b>不是每笔都很赚，而是小正期望在高频重复下被复利累起来了。</b></li>
      </ul>
    </div>

    <div class='card'>
      <h2>样本窗口到底是哪一段？</h2>
      <table>
        <thead>
          <tr><th>窗口</th><th>含义</th><th>当前值</th></tr>
        </thead>
        <tbody>
          <tr><td><code>sample_start_utc</code></td><td>原始 frozen panel 的起点；它包含 formation warm-up，不等于第一笔交易时间。</td><td><code>{status['sample_start_utc']}</code></td></tr>
          <tr><td><code>sample_end_utc</code></td><td>原始 frozen panel 的终点。</td><td><code>{status['sample_end_utc']}</code></td></tr>
          <tr><td><code>first_trade_entry_ts</code></td><td>第一笔真正纳入统计的 basket 开仓时点。</td><td><code>{status['first_trade_entry_ts']}</code></td></tr>
          <tr><td><code>last_trade_exit_ts</code></td><td>最后一笔真正纳入统计的 basket 平仓时点。</td><td><code>{status['last_trade_exit_ts']}</code></td></tr>
          <tr><td><code>raw_panel_days</code></td><td>底层 frozen panel 覆盖天数。</td><td><code>{status['raw_panel_days']:.2f}</code> 天</td></tr>
          <tr><td><code>trade_window_days</code></td><td>真正有 basket 统计的交易窗口天数。</td><td><code>{status['trade_window_days']:.2f}</code> 天</td></tr>
          <tr><td><code>trades_per_day</code></td><td>平均每天多少笔 closed baskets；当前 frozen 版应该接近每 3h 一笔，也就是约 8 笔/天。</td><td><code>{status['trades_per_day']:.2f}</code> 笔/天</td></tr>
        </tbody>
      </table>
      <p class="warn"><b>注意：</b><code>sample_start_utc</code> 是原始面板起点，不是第一笔交易起点。因为策略先要看 <code>64 × 15m = 16h</code> 的 formation window，所以第一笔 basket 会比 panel 起点晚一个 formation 窗。</p>
    </div>

    <div class='card'>
      <h2>持仓 3 小时期间，能不能再交易？</h2>
      <ul>
        <li><b>当前这页对应的 frozen live 版：</b>不可以。它是 <b>每 3h 非重叠一次</b> 的 basket。</li>
        <li>具体说：在 <code>t</code> 开仓以后，固定持有到 <code>t + 3h</code>；这段时间里，<b>不因为新的 15m bar 到来而重排持仓</b>。</li>
        <li>所以这页上的收益统计，应该理解成：<b>{status['closed_trades']} 次“开一笔 3h basket → 持有 → 时间退出”</b> 的结果。</li>
        <li>如果以后要展示“每 15m rolling 重算、持仓互相重叠”的研究口径，那必须放到 formal/as-of 页面，不能和这页混写。</li>
      </ul>
    </div>

    <div class='card'>
      <h2>先把口径钉死：这页采用哪一版定义？</h2>
      <div class="warn"><b>结论：</b>本页采用 <b>当前 live frozen spec</b> 作为唯一 runtime 定义：<code>15m</code> bar，<code>formation=64</code>，<code>hold=12</code>，<b>每 3h 非重叠换仓一次</b>。formal/as-of 页面虽然使用同一套核心公式，但 cadence 是 <b>每 15m rolling</b>，不能在这页伪装成“当前 live runtime 也是 rolling 15m”。</div>
      {cadence_compare}
    </div>

    {universe_transparency_block}
    {verdict_block}
    {monthly_rebuild_block}

    <div class='card'>
      <h2>策略逻辑解释卡片：它到底怎么选币？</h2>
      <p>下面这张卡片只讲 <b>当前 frozen live spec</b>。不说“高/低”，直接说计算过程：</p>
      <ol>
        <li>固定 universe：当前 frozen 版直接读取 admission summary 里的固定 <code>30</code> 币名单；refresh 时<b>不按月/按季度重选 Top30</b>。所以这页讲的是“当前运行口径”，不是“历史滚动 Top30”口径。</li>
        <li>bar 粒度：用 <code>15m</code> K 线。</li>
        <li>formation window：往前看 <code>64</code> 根 <code>15m</code> bar，也就是 <code>16h</code>。</li>
        <li>baseline score：对每个币取 formation window 的<strong>首尾 close</strong>，按 <code>cumret = close[-1] / close[0] - 1</code> 算过去 16h 累计收益。</li>
        <li>横截面排序：把 universe 里所有币按 <code>cumret</code> 从低到高排序；<b>top-3 做多</b>，<b>bottom-3 先作为 plain short 候选</b>。</li>
        <li>short-leg jump veto：只检查 plain short 候选。对每个 short 候选，在同一个 formation window 里算它的 <code>max 15m up-bar</code>；再算同一时点全市场的 <code>median(max-up-bar)</code>。阈值固定为 <code>max(1.5%, 2.0 × median(max-up-bar))</code>。</li>
        <li>如果某个 plain short 候选的 <code>max-up-bar</code> 超过该阈值，就 <b>veto</b>；然后从后续 loser rank 里往下补，直到 short leg 补满 <code>3</code> 个名字。</li>
        <li>最终执行：<b>long = plain_longs</b>，<b>short = veto_shorts</b>；持有 <code>12</code> 根 <code>15m</code> bar，也就是 <code>3h</code> 后时间退出。</li>
      </ol>
      <p class="note"><b>成本口径也锁死：</b><code>net_bps = gross_bps - 4.0 × turnover_x</code>。这页上的 live/paper 指标都是按这个 frozen 成本口径记，不额外夹带别的 fee 假设。</p>
    </div>

    <div class='card'>
      <h2>假数据示例：plain short 怎样被 veto，short 名额怎样 refill？</h2>
      <p>下面用一组假数据，把代码里的实际流程一步一步画出来。注意这里只是为了解释机制，不是当前真实持仓。</p>
      {example_svg}
      <table>
        <thead>
          <tr><th>symbol</th><th>过去 16h cumret</th><th>formation 窗内 max 15m up-bar</th><th>在这一步的角色</th><th>为什么</th></tr>
        </thead>
        <tbody>
          {example_table}
        </tbody>
      </table>
      <ul>
        <li>先看 <b>cumret 排名</b>：<code>ALPHA/BETA/GAMMA</code> 是 top-3，所以进 <b>long</b>。</li>
        <li>plain short 候选会先落在最弱的三个：<code>OMEGA / PHI / EPSILON</code>。</li>
        <li>然后只对这三个 short 候选做 jump veto。假设当前全市场 <code>median(max-up-bar)=1.6%</code>，那阈值就是 <code>max(1.5%, 2.0×1.6%) = 3.2%</code>。</li>
        <li><code>PHI</code> 的 <code>max-up-bar=3.9%</code>，超过 <code>3.2%</code>，所以被 veto；<code>OMEGA</code> 和 <code>EPSILON</code> 保留。</li>
        <li>short leg 少了一个名额，就从后续 loser rank 往下补，补到 <code>DELTA</code>；因为它的 <code>max-up-bar=1.3%</code> 没超阈值，所以最终 short 变成 <code>OMEGA / EPSILON / DELTA</code>。</li>
        <li><b>最终执行篮子</b>：<code>long = ALPHA,BETA,GAMMA</code>；<code>short = OMEGA,EPSILON,DELTA</code>。</li>
      </ul>
    </div>

    {long_history_block}

    <div class='card'>
      <h2>把公式和代码一一对上</h2>
      <table>
        <thead>
          <tr><th>概念</th><th>这页的硬定义</th><th>对应代码实现</th></tr>
        </thead>
        <tbody>
          <tr><td>formation 窗</td><td>过去 <code>64</code> 根 <code>15m</code> bar（<code>16h</code>）</td><td><code>close_window = panel[eligible].iloc[i - FORMATION_BARS:i + 1]</code></td></tr>
          <tr><td>baseline score</td><td><code>cumret = close[-1] / close[0] - 1</code></td><td><code>cumret = close_window.iloc[-1] / close_window.iloc[0] - 1.0</code></td></tr>
          <tr><td>做多名单</td><td>按 <code>cumret</code> 排名的 <code>top-3</code></td><td><code>longs = rank.index[-TOP_N:].tolist()[::-1]</code></td></tr>
          <tr><td>plain short 候选</td><td>按 <code>cumret</code> 排名的 <code>bottom-3</code></td><td><code>plain_shorts = rank.index[:BOTTOM_N].tolist()</code></td></tr>
          <tr><td>jump veto 统计量</td><td>formation 窗内 <code>max 15m up-bar</code></td><td><code>short_info = [(sym, float(hist[sym].max())) ...]</code></td></tr>
          <tr><td>veto 阈值</td><td><code>max(1.5%, 2.0 × median(max-up-bar))</code></td><td><code>veto_threshold = max(VETO_FLOOR, VETO_MULT * universe_med)</code></td></tr>
          <tr><td>refill</td><td>被 veto 后，从后续 loser rank 继续往下补</td><td><code>refill = [sym for sym in rank.index if sym not in longs and sym not in plain_shorts]</code></td></tr>
          <tr><td>最终执行 short</td><td><code>veto_shorts</code></td><td><code>shorts = veto_shorts</code> / frozen seed 对应 <code>variant_timeseries.csv.veto_shorts</code></td></tr>
          <tr><td>退出</td><td>持有 <code>12</code> 根 <code>15m</code> bar = <code>3h</code></td><td><code>exit_ts = timestamp + 12 × 15m</code></td></tr>
          <tr><td>成本</td><td><code>4.0 bps × turnover_x</code></td><td><code>net_bps = gross_bps - 4.0 × turnover_x</code></td></tr>
        </tbody>
      </table>
    </div>

    {regime_block}
    {gate_deep_block}

    <div class='card'>
      <h2>相关审计页</h2>
      <p>
        <a href="/momentum/paper/rank213_evidence_map.html">evidence_map（推荐先看）</a>
        ·
        <a href="/momentum/paper/rank213_largecap_xs_jump_veto_honesty_audit.html">honesty_audit（seed causality）</a>
        · <a href="/momentum/paper/rank213_largecap_xs_jump_veto_ffill_impact_audit.html">ffill_impact_audit</a>
        · <a href="/momentum/paper/rank213_largecap_xs_jump_veto_readiness_note.html">readiness_note</a>
        · <a href="/momentum/paper/rank213_largecap_xs_jump_veto_long_history_review_with_funding.html">funding-adjusted long-history</a>
        · <a href="/momentum/paper/rank213_largecap_xs_jump_veto_asof_universe_long_history_review.html">asof_universe_long_history_review</a>
        · <a href="/momentum/paper/rank213_largecap_xs_jump_veto_regime_review.html">regime_review</a>
        · <a href="/momentum/paper/rank213_largecap_xs_jump_veto_formal_strategy_review.html">formal_strategy_review</a>
        · <a href="/momentum/paper/rank213_largecap_xs_jump_veto_fee_sensitivity_review.html">fee_sensitivity_review</a>
        · <a href="/momentum/paper/rank213_largecap_xs_jump_veto_monthly_volume_universe_rebuild.html">monthly_volume_universe_rebuild</a>
        · <a href="/momentum/paper/rank213_largecap_xs_jump_veto_monthly_volume_percentile_gate_review.html">monthly_volume_percentile_gate_review</a>
        · <a href="/momentum/paper/rank213_largecap_xs_jump_veto_universe_selection_audit.html">universe_selection_audit</a>
        · <a href="/momentum/paper/rank213_largecap_xs_jump_veto_family_operating_board.html">family_operating_board</a>
      </p>
    </div>

    <div class='card'>
      <h2>最新一笔信号快照</h2>
      <pre>{json.dumps(latest_row or {'state': 'no-latest-row'}, ensure_ascii=False, indent=2)}</pre>
    </div>
  </div>
</body>
</html>
'''
    HTML_PATH.write_text(body, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank213 large-cap XS jump veto paper runner")
    parser.add_argument("--init-from-now", action="store_true", help="Initialize runner state from the frozen seed and write the full paper ledger.")
    parser.add_argument("--refresh", action="store_true", help="Refresh runner artifacts from the same frozen seed.")
    parser.add_argument("--force-reinit", action="store_true", help="Allow reinitialization when state already exists.")
    args = parser.parse_args()
    if not args.init_from_now and not args.refresh:
        parser.error("choose one of --init-from-now or --refresh")

    ensure_dir(ART_DIR)
    trades, summary = load_variant_frame()
    state = load_state()

    if args.init_from_now and state and not args.force_reinit:
        parser.error(f"state already exists at {STATE_PATH}; use --force-reinit to reset")
    if args.refresh and not state:
        parser.error(f"missing state at {STATE_PATH}; run --init-from-now first")

    if args.init_from_now:
        state = initialize_state(trades, summary)
        normalized = normalize_for_csv(trades[[
            "trade_id", "candidate_id", "candidate_rank", "stage", "venue_mode", "signal_family",
            "entry_ts", "exit_ts", "gross_bps", "net_bps", "gross_ret", "net_ret", "turnover_x",
            "veto_count", "longs", "shorts", "complete_trade"
        ]])
        normalized.to_csv(LEDGER_PATH, index=False)
        new_rows = len(trades)
    else:
        normalized = normalize_for_csv(trades[[
            "trade_id", "candidate_id", "candidate_rank", "stage", "venue_mode", "signal_family",
            "entry_ts", "exit_ts", "gross_bps", "net_bps", "gross_ret", "net_ret", "turnover_x",
            "veto_count", "longs", "shorts", "complete_trade"
        ]])
        normalized.to_csv(LEDGER_PATH, index=False)
        state["watermark_exit_ts_utc"] = iso_z(trades["exit_ts"].max()) if not trades.empty else state.get("watermark_exit_ts_utc")
        new_rows = 0

    state["last_run_at_utc"] = iso_z(utc_now())
    state["latest_signal_ts"] = iso_z(trades["entry_ts"].max()) if not trades.empty else None
    state["latest_planned_exit_ts"] = iso_z(trades["exit_ts"].max()) if not trades.empty else None
    state["closed_trades"] = int(len(trades))
    state["lifetime_total_return"] = float((1.0 + trades["net_ret"]).prod() - 1.0) if not trades.empty else 0.0
    save_state(state)

    latest_frame = normalize_for_csv(trades[[
        "entry_ts", "exit_ts", "gross_bps", "net_bps", "turnover_x", "veto_count", "longs", "shorts"
    ]].tail(96))
    latest_frame.to_csv(CURRENT_SIGNAL_PATH, index=False)

    status = build_status(trades, summary, state, new_rows)
    pd.DataFrame([status]).to_csv(STATUS_PATH, index=False)
    latest_row = None
    if not trades.empty:
        row = trades.iloc[-1]
        latest_row = {
            "entry_ts": iso_z(row["entry_ts"]),
            "exit_ts": iso_z(row["exit_ts"]),
            "gross_bps": float(row["gross_bps"]),
            "net_bps": float(row["net_bps"]),
            "turnover_x": float(row["turnover_x"]),
            "veto_count": int(row["veto_count"]),
            "longs": row["longs"].split(",") if row["longs"] else [],
            "shorts": row["shorts"].split(",") if row["shorts"] else [],
        }
    regime_snapshot = load_regime_snapshot()
    long_history_snapshot = load_frozen_long_history_snapshot()
    universe_snapshot = load_universe_transparency_snapshot()
    gate_deep_snapshot = load_gate_deep_snapshot()
    write_html(status, latest_row, regime_snapshot, long_history_snapshot, universe_snapshot, gate_deep_snapshot)

    run_summary = {
        "run_at_utc": iso_z(utc_now()),
        "mode": "init_from_now" if args.init_from_now else "refresh",
        "runner": "rank213_largecap_xs_jump_veto_paper_runner",
        "runner_mode": "frozen_admission_timeseries_seed",
        "variant": VARIANT,
        "closed_trades_total": int(len(trades)),
        "new_closed_trades_appended": int(new_rows),
        "status_path": str(STATUS_PATH.relative_to(ROOT)),
        "ledger_path": str(LEDGER_PATH.relative_to(ROOT)),
        "state_path": str(STATE_PATH.relative_to(ROOT)),
        "html_path": str(HTML_PATH.relative_to(ROOT)),
        "current_signal_path": str(CURRENT_SIGNAL_PATH.relative_to(ROOT)),
    }
    RUN_SUMMARY_PATH.write_text(json.dumps(run_summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(run_summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
