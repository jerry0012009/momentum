#!/usr/bin/env python3
from __future__ import annotations

"""Raw-bar shadow runner scaffold for Rank 213 / large-cap XS momentum × short-leg jump veto.

This runner is intentionally honest about scope:
- source of truth is raw-bar as-of recomputation plus the frozen formal gate
- it writes runner-grade shadow artifacts without touching the frozen-seed paper lane
- it keeps raw basket evidence visible even when the formal gate is OFF
- it is a shadow scaffold, not a claim of live order execution or scheduler cutover
"""

import argparse
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

ADMISSION_SUMMARY_PATH = ROOT / "reports" / "artifacts" / "optimization_loop" / "rank213_p2_admission_20260328" / "summary.json"
FREEZE_SUMMARY_PATH = ROOT / "reports" / "artifacts" / "paper_rank213_largecap_xs_jump_veto" / "rank213_formal_strategy_freeze_summary.json"
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank213_largecap_xs_jump_veto"
LEDGER_PATH = ART_DIR / "rank213_shadow_closed_trades.csv"
STATUS_PATH = ART_DIR / "rank213_shadow_status.csv"
STATE_PATH = ART_DIR / "rank213_shadow_state.json"
RUN_SUMMARY_PATH = ART_DIR / "rank213_shadow_last_run_summary.json"
CURRENT_SIGNAL_PATH = ART_DIR / "rank213_shadow_current_signal_frame.csv"
RAWBAR_DETAIL_PATH = ART_DIR / "rank213_shadow_rawbar_detail.csv"
HTML_PATH = ROOT / "reports" / "site" / "paper" / "rank213_largecap_xs_jump_veto_rawbar_shadow.html"

CANDIDATE_ID = "rank213_largecap_xs_jump_veto"
CANDIDATE_RANK = 213
RUNNER_MODE = "rawbar_asof_plus_frozen_gate_shadow"
RUNNER_SERVICE = "shadow_only_not_wired"
RUNNER_TIMER = "shadow_only_not_wired"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


asof_mod = load_module(ROOT / "scripts" / "build_rank213_asof_universe_long_history_review.py", "rank213_asof_shadow_mod")
formal_mod = load_module(ROOT / "scripts" / "build_rank213_formal_strategy_pack.py", "rank213_formal_shadow_mod")

FORMATION_BARS = int(asof_mod.FORMATION_BARS)
HOLD_BARS = int(asof_mod.HOLD_BARS)
BAR_MINUTES = int(asof_mod.BAR_MINUTES)
ROUND_TRIP_COST_BPS = float(asof_mod.COST_BPS)
VETO_FLOOR_PCT = float(asof_mod.VETO_FLOOR * 100.0)
VETO_MULT = float(asof_mod.VETO_MULT)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_z(ts: Any) -> str:
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


def load_shadow_frame() -> tuple[pd.DataFrame, dict, dict]:
    admission = read_json(ADMISSION_SUMMARY_PATH)
    freeze = read_json(FREEZE_SUMMARY_PATH)

    sample_start = pd.to_datetime(admission["sample_start"], utc=True)
    sample_end = pd.to_datetime(admission["sample_end"], utc=True)
    symbols = [str(sym) for sym in admission.get("symbols", [])]
    history_start = sample_start - pd.to_timedelta(FORMATION_BARS * BAR_MINUTES, unit="m")

    panel, _ = asof_mod.build_panel(symbols, history_start, sample_end)
    detail = asof_mod.run_asof_backtest(panel, symbols)
    if detail.empty:
        raise RuntimeError("rank213 raw-bar shadow runner: as-of backtest returned no rows")

    detail["timestamp_ts"] = pd.to_datetime(detail["timestamp_ts"], utc=True)
    detail["exit_ts"] = pd.to_datetime(detail["exit_ts"], utc=True)
    detail = detail[(detail["timestamp_ts"] >= sample_start) & (detail["timestamp_ts"] <= sample_end)].copy()
    detail = detail.sort_values("timestamp_ts").reset_index(drop=True)
    if detail.empty:
        raise RuntimeError("rank213 raw-bar shadow runner: filtered shadow detail is empty")

    detail, gate_snapshot = formal_mod.apply_frozen_gate(detail, freeze)
    detail["shadow_ret"] = detail["gate_on"].map(lambda x: 1.0 if bool(x) else 0.0)
    detail["net_ret"] = detail["gate_ret"]
    detail["net_bps"] = pd.to_numeric(detail["gate_ret"], errors="coerce") * 10000.0
    detail["gross_ret"] = pd.to_numeric(detail["veto_gross"], errors="coerce")
    detail["gross_bps"] = detail["gross_ret"] * 10000.0
    detail["turnover_x"] = pd.to_numeric(detail["gate_turnover_x"], errors="coerce")
    detail["entry_ts"] = detail["timestamp_ts"]
    detail["candidate_id"] = CANDIDATE_ID
    detail["candidate_rank"] = CANDIDATE_RANK
    detail["stage"] = "rawbar_shadow_runner"
    detail["venue_mode"] = RUNNER_MODE
    detail["signal_family"] = "largecap_xs_momentum_shortleg_jump_veto"
    detail["trade_id"] = detail["timestamp_ts"].dt.strftime("%Y%m%dT%H%M%SZ") + "|rawbar_shadow"
    detail["raw_longs"] = detail["plain_longs"].fillna("")
    detail["raw_shorts"] = detail["veto_shorts"].fillna("")
    detail["longs"] = detail.apply(lambda row: row["raw_longs"] if bool(row["gate_on"]) else "", axis=1)
    detail["shorts"] = detail.apply(lambda row: row["raw_shorts"] if bool(row["gate_on"]) else "", axis=1)
    detail["complete_trade"] = True
    detail["gate_label"] = detail["gate_on"].map(lambda x: "ON" if bool(x) else "OFF")
    return detail, admission, gate_snapshot


def initialize_state(trades: pd.DataFrame, admission: dict, gate_snapshot: dict) -> dict:
    return {
        "initialized_at_utc": iso_z(utc_now()),
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "wiring_status": "shadow_scaffold_ready",
        "runner_mode": RUNNER_MODE,
        "runner_script": str((ROOT / "scripts" / "run_rank213_largecap_xs_jump_veto_rawbar_shadow_runner.py").relative_to(ROOT)),
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "source_admission_summary": str(ADMISSION_SUMMARY_PATH.relative_to(ROOT)),
        "source_freeze_summary": str(FREEZE_SUMMARY_PATH.relative_to(ROOT)),
        "variant": "formal_gate_v1_on_top_of_asof_veto_v1",
        "watermark_exit_ts_utc": iso_z(trades["exit_ts"].max()) if not trades.empty else None,
        "sample_start_utc": iso_z(pd.to_datetime(admission["sample_start"], utc=True)),
        "sample_end_utc": iso_z(pd.to_datetime(admission["sample_end"], utc=True)),
        "current_gate_snapshot": gate_snapshot,
        "notes": "Raw-bar shadow scaffold recomputes the as-of basket and frozen formal gate, writes separate shadow artifacts, and does not replace or reinterpret the frozen-seed paper lane.",
    }


def build_status(trades: pd.DataFrame, admission: dict, state: dict, gate_snapshot: dict, new_rows: int) -> dict:
    latest = trades.iloc[-1] if not trades.empty else None
    gated = trades[trades["gate_on"].astype(bool)].copy()
    lifetime_total_return = float((1.0 + trades["net_ret"]).prod() - 1.0) if not trades.empty else 0.0
    return {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "stage": "rawbar_shadow_runner",
        "wiring_status": "shadow_scaffold_ready",
        "runner_mode": RUNNER_MODE,
        "runner_script": "scripts/run_rank213_largecap_xs_jump_veto_rawbar_shadow_runner.py",
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "source_admission_summary": "reports/artifacts/optimization_loop/rank213_p2_admission_20260328/summary.json",
        "source_freeze_summary": "reports/artifacts/paper_rank213_largecap_xs_jump_veto/rank213_formal_strategy_freeze_summary.json",
        "variant": "formal_gate_v1_on_top_of_asof_veto_v1",
        "signal_timeframe": "15m",
        "formation_bars": FORMATION_BARS,
        "hold_bars": HOLD_BARS,
        "veto_floor_pct": VETO_FLOOR_PCT,
        "veto_mult_x_median": VETO_MULT,
        "universe_size": int(admission["universe_size"]),
        "round_trip_cost_bps_per_turnover_x": ROUND_TRIP_COST_BPS,
        "sample_start_utc": iso_z(pd.to_datetime(admission["sample_start"], utc=True)),
        "sample_end_utc": iso_z(pd.to_datetime(admission["sample_end"], utc=True)),
        "closed_trades": int(len(trades)),
        "gated_on_trades": int(len(gated)),
        "new_closed_trades_appended": int(new_rows),
        "pct_rebalances_with_any_veto": float((pd.to_numeric(trades["veto_count"], errors="coerce").fillna(0) > 0).mean()) if not trades.empty else 0.0,
        "gate_on_rate": float(trades["gate_on"].astype(bool).mean()) if not trades.empty else 0.0,
        "mean_turnover_x": float(trades["turnover_x"].mean()) if not trades.empty else 0.0,
        "mean_net_bps": float(trades["net_bps"].mean()) if not trades.empty else 0.0,
        "win_rate": float((trades["net_bps"] > 0).mean()) if not trades.empty else 0.0,
        "lifetime_total_return": lifetime_total_return,
        "latest_signal_ts": iso_z(latest["entry_ts"]) if latest is not None else None,
        "latest_planned_exit_ts": iso_z(latest["exit_ts"]) if latest is not None else None,
        "latest_raw_longs": latest["raw_longs"] if latest is not None else "",
        "latest_raw_shorts": latest["raw_shorts"] if latest is not None else "",
        "latest_gate_on": bool(latest["gate_on"]) if latest is not None else None,
        "watermark_exit_ts_utc": state.get("watermark_exit_ts_utc"),
        "updated_at_utc": iso_z(utc_now()),
        "current_gate_votes": gate_snapshot.get("votes"),
        "current_gate_valid_rules": gate_snapshot.get("valid_rules"),
        "current_gate_needed_votes": gate_snapshot.get("needed_votes"),
        "note": "shadow-only scaffold: recomputes raw-bar as-of basket and applies frozen formal gate into separate artifacts. It preserves the honest separation from the frozen-seed paper lane and is not a live execution claim.",
    }


def write_html(status: dict, latest_row: dict | None, gate_snapshot: dict) -> None:
    ensure_dir(HTML_PATH.parent)
    gate_label = "ON" if gate_snapshot.get("gate_on") else "OFF"
    body = f'''<!doctype html>
<html lang="zh">
<head>
  <meta charset="utf-8" />
  <title>Rank 213 Raw-Bar Shadow Runner</title>
  <style>body{{font-family:Arial,sans-serif;margin:24px;line-height:1.5}}code{{background:#f3f3f3;padding:2px 4px}}pre{{background:#fafafa;padding:12px;border:1px solid #eee;overflow:auto}}</style>
</head>
<body>
  <h1>Rank 213 / raw-bar as-of shadow runner</h1>
  <p><strong>接线状态：</strong>{status['wiring_status']}</p>
  <ul>
    <li>runner: <code>{status['runner_script']}</code></li>
    <li>runner mode: <code>{status['runner_mode']}</code></li>
    <li>source admission: <code>{status['source_admission_summary']}</code></li>
    <li>source freeze: <code>{status['source_freeze_summary']}</code></li>
    <li>最近更新时间: <code>{status['updated_at_utc']}</code></li>
    <li>闭合 shadow 记录数: <code>{status['closed_trades']}</code></li>
    <li>gate ON 占比: <code>{status['gate_on_rate']:.4f}</code></li>
    <li>平均净收益: <code>{status['mean_net_bps']:.2f} bps</code></li>
    <li>累计净收益: <code>{status['lifetime_total_return']:.4%}</code></li>
  </ul>
  <p>这个 shadow runner 复算 raw-bar as-of basket，并套用 frozen formal gate；它写入独立 shadow artifacts，不替代 frozen admission seed runner。</p>
  <h2>当前 gate 快照</h2>
  <ul>
    <li>gate: <code>{gate_label}</code>（<code>{gate_snapshot.get('votes')}/{gate_snapshot.get('valid_rules')}</code>, 阈值 <code>{gate_snapshot.get('needed_votes')}</code>）</li>
    <li>window: <code>{gate_snapshot.get('window_start_utc')}</code> → <code>{gate_snapshot.get('window_end_utc')}</code></li>
  </ul>
  <p>
    <a href="/momentum/paper/rank213_largecap_xs_jump_veto.html">frozen-seed runner</a>
    · <a href="/momentum/paper/rank213_largecap_xs_jump_veto_shadow_compare.html">shadow_compare</a>
    · <a href="/momentum/paper/rank213_largecap_xs_jump_veto_formal_strategy_review.html">formal_strategy_review</a>
    · <a href="/momentum/paper/rank213_largecap_xs_jump_veto_asof_universe_long_history_review.html">asof_universe_long_history_review</a>
  </p>
  <h2>最新一笔 shadow 快照</h2>
  <pre>{json.dumps(latest_row or {'state': 'no-latest-row'}, ensure_ascii=False, indent=2)}</pre>
</body>
</html>
'''
    HTML_PATH.write_text(body, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank213 raw-bar shadow runner scaffold")
    parser.add_argument("--init-from-now", action="store_true", help="Initialize shadow runner state from raw-bar as-of recomputation and write full shadow ledger.")
    parser.add_argument("--refresh", action="store_true", help="Refresh shadow runner artifacts from raw-bar as-of recomputation.")
    parser.add_argument("--force-reinit", action="store_true", help="Allow reinitialization when shadow state already exists.")
    args = parser.parse_args()
    if not args.init_from_now and not args.refresh:
        parser.error("choose one of --init-from-now or --refresh")

    ensure_dir(ART_DIR)
    trades, admission, gate_snapshot = load_shadow_frame()
    state = load_state()

    if args.init_from_now and state and not args.force_reinit:
        parser.error(f"state already exists at {STATE_PATH}; use --force-reinit to reset")
    if args.refresh and not state:
        parser.error(f"missing state at {STATE_PATH}; run --init-from-now first")

    ledger_cols = [
        "trade_id", "candidate_id", "candidate_rank", "stage", "venue_mode", "signal_family",
        "entry_ts", "exit_ts", "gross_bps", "net_bps", "gross_ret", "net_ret", "turnover_x",
        "veto_count", "gate_on", "gate_votes", "gate_valid_rules", "gate_needed_votes",
        "raw_longs", "raw_shorts", "longs", "shorts", "complete_trade",
    ]

    if args.init_from_now:
        state = initialize_state(trades, admission, gate_snapshot)
        normalized = normalize_for_csv(trades[ledger_cols])
        normalized.to_csv(LEDGER_PATH, index=False)
        new_rows = len(trades)
    else:
        normalized = normalize_for_csv(trades[ledger_cols])
        normalized.to_csv(LEDGER_PATH, index=False)
        state["watermark_exit_ts_utc"] = iso_z(trades["exit_ts"].max()) if not trades.empty else state.get("watermark_exit_ts_utc")
        new_rows = 0

    state["last_run_at_utc"] = iso_z(utc_now())
    state["latest_signal_ts"] = iso_z(trades["entry_ts"].max()) if not trades.empty else None
    state["latest_planned_exit_ts"] = iso_z(trades["exit_ts"].max()) if not trades.empty else None
    state["closed_trades"] = int(len(trades))
    state["gate_on_trades"] = int(trades["gate_on"].astype(bool).sum()) if not trades.empty else 0
    state["lifetime_total_return"] = float((1.0 + trades["net_ret"]).prod() - 1.0) if not trades.empty else 0.0
    state["current_gate_snapshot"] = gate_snapshot
    save_state(state)

    rawbar_detail = normalize_for_csv(trades[[
        "entry_ts", "exit_ts", "raw_longs", "raw_shorts", "longs", "shorts", "veto_count",
        "gate_on", "gate_votes", "gate_valid_rules", "gate_needed_votes", "net_bps", "turnover_x",
    ]])
    rawbar_detail.to_csv(RAWBAR_DETAIL_PATH, index=False)
    rawbar_detail.tail(96).to_csv(CURRENT_SIGNAL_PATH, index=False)

    status = build_status(trades, admission, state, gate_snapshot, new_rows)
    pd.DataFrame([status]).to_csv(STATUS_PATH, index=False)

    latest_row = None
    if not trades.empty:
        row = trades.iloc[-1]
        latest_row = {
            "entry_ts": iso_z(row["entry_ts"]),
            "exit_ts": iso_z(row["exit_ts"]),
            "raw_longs": row["raw_longs"].split(",") if row["raw_longs"] else [],
            "raw_shorts": row["raw_shorts"].split(",") if row["raw_shorts"] else [],
            "executed_longs": row["longs"].split(",") if row["longs"] else [],
            "executed_shorts": row["shorts"].split(",") if row["shorts"] else [],
            "gate_on": bool(row["gate_on"]),
            "gate_votes": int(row["gate_votes"]),
            "gate_valid_rules": int(row["gate_valid_rules"]),
            "gate_needed_votes": int(row["gate_needed_votes"]),
            "gross_bps": float(row["gross_bps"]),
            "net_bps": float(row["net_bps"]),
            "turnover_x": float(row["turnover_x"]),
            "veto_count": int(row["veto_count"]),
        }
    write_html(status, latest_row, gate_snapshot)

    run_summary = {
        "run_at_utc": iso_z(utc_now()),
        "mode": "init_from_now" if args.init_from_now else "refresh",
        "runner": "rank213_largecap_xs_jump_veto_rawbar_shadow_runner",
        "runner_mode": RUNNER_MODE,
        "closed_trades_total": int(len(trades)),
        "gate_on_trades": int(trades["gate_on"].astype(bool).sum()) if not trades.empty else 0,
        "new_closed_trades_appended": int(new_rows),
        "status_path": str(STATUS_PATH.relative_to(ROOT)),
        "ledger_path": str(LEDGER_PATH.relative_to(ROOT)),
        "state_path": str(STATE_PATH.relative_to(ROOT)),
        "html_path": str(HTML_PATH.relative_to(ROOT)),
        "current_signal_path": str(CURRENT_SIGNAL_PATH.relative_to(ROOT)),
        "rawbar_detail_path": str(RAWBAR_DETAIL_PATH.relative_to(ROOT)),
        "frozen_seed_lane_left_untouched": True,
    }
    RUN_SUMMARY_PATH.write_text(json.dumps(run_summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(run_summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
