#!/usr/bin/env python3
from __future__ import annotations

"""Dedicated paper runner seed for Rank 229 / ETH-led abnormal-day continuation.

This is launch wiring for the approved frozen spec only:
- symbol: ETHUSDT perp
- bar: 5m
- session offset: 20h
- trigger threshold: 1.25 * sigma_session
- minimum remaining bars: 12
- entry: next-bar open
- exit: session close
- cost: 12 bps round-trip

The runner is intentionally explicit about scope:
- source of truth is the frozen P2 admission trade-level artifact
- it writes runner-grade artifacts (ledger / status / state / html / summary)
- it is scheduler-ready but does NOT claim raw-bar live recomputation yet
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "reports" / "artifacts" / "rank229_p2_admission_time_parameter"
TRADE_LEVEL_PATH = SRC_DIR / "trade_level.csv"
SUMMARY_PATH = SRC_DIR / "summary.json"
SPEC_PATH = ROOT / "reports" / "artifacts" / "paper_rank229_eth_abnormal_day" / "rank229_frozen_launch_spec.json"
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank229_eth_abnormal_day"
LEDGER_PATH = ART_DIR / "rank229_closed_trades.csv"
STATUS_PATH = ART_DIR / "rank229_status.csv"
STATE_PATH = ART_DIR / "rank229_state.json"
RUN_SUMMARY_PATH = ART_DIR / "rank229_last_run_summary.json"
CURRENT_SIGNAL_PATH = ART_DIR / "rank229_current_signal_frame.csv"
HTML_PATH = ROOT / "reports" / "site" / "paper" / "rank229_eth_abnormal_day.html"

CANDIDATE_ID = "rank229_eth_abnormal_day_continuation"
CANDIDATE_RANK = 229
SYMBOL = "ETHUSDT"
VENUE = "Binance Futures"
BAR_SIZE = "5m"
SESSION_OFFSET_H = 20
THRESHOLD_K = 1.25
MIN_REMAINING = 12
ROUND_TRIP_COST_BPS = 12.0
ENTRY_RULE = "next-bar open"
EXIT_RULE = "session close"
RUNNER_MODE = "frozen_admission_trade_seed"
SPEC_VERSION = "v1"


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


def load_frozen_trades() -> tuple[pd.DataFrame, dict, dict]:
    summary = read_json(SUMMARY_PATH)
    spec = read_json(SPEC_PATH)
    df = pd.read_csv(TRADE_LEVEL_PATH)
    df = df[(df["offset_h"] == SESSION_OFFSET_H) & (df["k"] == THRESHOLD_K) & (df["min_remaining"] == MIN_REMAINING)].copy()
    if df.empty:
        raise RuntimeError(f"frozen spec rows not found in {TRADE_LEVEL_PATH}")
    df["entry_ts"] = pd.to_datetime(df["timestamp"], utc=True)
    df["session_id"] = pd.to_datetime(df["session_id"], utc=True)
    df = df.sort_values("entry_ts").reset_index(drop=True)
    session_end_hour = (SESSION_OFFSET_H + 24) % 24
    df["session_close_ts"] = df["session_id"] + pd.to_timedelta(24, unit="h")
    df["remaining_minutes"] = (df["session_close_ts"] - df["entry_ts"]).dt.total_seconds() / 60.0
    df["holding_minutes"] = df["remaining_minutes"]
    df["exit_ts"] = df["session_close_ts"]
    df["candidate_id"] = CANDIDATE_ID
    df["candidate_rank"] = CANDIDATE_RANK
    df["symbol"] = SYMBOL
    df["venue"] = VENUE
    df["bar_size"] = BAR_SIZE
    df["stage"] = "paper_runner_live_seed"
    df["runner_mode"] = RUNNER_MODE
    df["signal_family"] = "eth_led_abnormal_day_continuation"
    df["trade_id"] = df["entry_ts"].dt.strftime("%Y%m%dT%H%M%SZ") + f"|offset{SESSION_OFFSET_H}|k{THRESHOLD_K}|m{MIN_REMAINING}"
    df["gross_ret"] = pd.to_numeric(df["gross_bps"], errors="coerce") / 10000.0
    df["net_bps"] = pd.to_numeric(df["net12_bps"], errors="coerce")
    df["net_ret"] = df["net_bps"] / 10000.0
    df["cost_bps"] = ROUND_TRIP_COST_BPS
    df["complete_trade"] = True
    df["session_end_hour_utc"] = session_end_hour
    return df, summary, spec


def initialize_state(trades: pd.DataFrame, summary: dict, spec: dict) -> dict:
    return {
        "initialized_at_utc": iso_z(utc_now()),
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "wiring_status": "connected_runner_live",
        "runner_mode": RUNNER_MODE,
        "runner_script": str((ROOT / "scripts" / "run_rank229_eth_abnormal_day_paper_runner.py").relative_to(ROOT)),
        "frozen_spec_path": str(SPEC_PATH.relative_to(ROOT)),
        "source_summary": str(SUMMARY_PATH.relative_to(ROOT)),
        "source_trade_level": str(TRADE_LEVEL_PATH.relative_to(ROOT)),
        "symbol": SYMBOL,
        "bar_size": BAR_SIZE,
        "session_offset_h": SESSION_OFFSET_H,
        "threshold_k": THRESHOLD_K,
        "min_remaining": MIN_REMAINING,
        "round_trip_cost_bps": ROUND_TRIP_COST_BPS,
        "entry_rule": ENTRY_RULE,
        "exit_rule": EXIT_RULE,
        "watermark_exit_ts_utc": iso_z(trades["exit_ts"].max()) if not trades.empty else None,
        "sample_start_utc": summary.get("sample_start_utc") or summary.get("sample_start"),
        "sample_end_utc": summary.get("sample_end_utc") or summary.get("sample_end"),
        "notes": spec.get("scope_note", "frozen admission seed only; scheduler wiring and first verified run are separate steps."),
    }


def build_status(trades: pd.DataFrame, summary: dict, state: dict, new_rows: int) -> dict:
    latest = trades.iloc[-1] if not trades.empty else None
    lifetime_total_return = float((1.0 + trades["net_ret"]).prod() - 1.0) if not trades.empty else 0.0
    return {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "stage": "connected_runner_live",
        "wiring_status": "connected_runner_live",
        "runner_mode": RUNNER_MODE,
        "runner_script": "scripts/run_rank229_eth_abnormal_day_paper_runner.py",
        "frozen_spec_path": "reports/artifacts/paper_rank229_eth_abnormal_day/rank229_frozen_launch_spec.json",
        "source_summary": "reports/artifacts/rank229_p2_admission_time_parameter/summary.json",
        "source_trade_level": "reports/artifacts/rank229_p2_admission_time_parameter/trade_level.csv",
        "symbol": SYMBOL,
        "venue": VENUE,
        "signal_timeframe": BAR_SIZE,
        "session_offset_h": SESSION_OFFSET_H,
        "threshold_k": THRESHOLD_K,
        "min_remaining": MIN_REMAINING,
        "entry_rule": ENTRY_RULE,
        "exit_rule": EXIT_RULE,
        "round_trip_cost_bps": ROUND_TRIP_COST_BPS,
        "sample_start_utc": state.get("sample_start_utc"),
        "sample_end_utc": state.get("sample_end_utc"),
        "closed_trades": int(len(trades)),
        "new_closed_trades_appended": int(new_rows),
        "mean_net_bps": float(trades["net_bps"].mean()) if not trades.empty else 0.0,
        "win_rate": float((trades["net_bps"] > 0).mean()) if not trades.empty else 0.0,
        "lifetime_total_return": lifetime_total_return,
        "latest_signal_ts": iso_z(latest["entry_ts"]) if latest is not None else None,
        "latest_planned_exit_ts": iso_z(latest["exit_ts"]) if latest is not None else None,
        "watermark_exit_ts_utc": state.get("watermark_exit_ts_utc"),
        "updated_at_utc": iso_z(utc_now()),
        "note": "wired to frozen P2-admission seed for Rank 229; dedicated runner, enabled scheduler, and first verified run are now live, while raw-bar recomputation remains a separate future scope.",
    }


def write_html(status: dict, latest_row: dict | None) -> None:
    ensure_dir(HTML_PATH.parent)
    body = f'''<!doctype html>
<html lang="zh">
<head>
  <meta charset="utf-8" />
  <title>Rank 229 Paper Runner Seed</title>
  <style>body{{font-family:Arial,sans-serif;margin:24px;line-height:1.5}}code{{background:#f3f3f3;padding:2px 4px}}pre{{background:#fafafa;padding:12px;border:1px solid #eee;overflow:auto}}</style>
</head>
<body>
  <h1>Rank 229 / ETH-led abnormal-day continuation</h1>
  <p><strong>接线状态：</strong>{status['wiring_status']}</p>
  <ul>
    <li>runner: <code>{status['runner_script']}</code></li>
    <li>frozen spec: <code>{status['frozen_spec_path']}</code></li>
    <li>source trade level: <code>{status['source_trade_level']}</code></li>
    <li>symbol: <code>{status['symbol']}</code></li>
    <li>offset / k / M: <code>{status['session_offset_h']}h / {status['threshold_k']} / {status['min_remaining']}</code></li>
    <li>最近更新时间: <code>{status['updated_at_utc']}</code></li>
    <li>闭合交易数: <code>{status['closed_trades']}</code></li>
    <li>平均净收益: <code>{status['mean_net_bps']:.2f} bps</code></li>
    <li>累计净收益: <code>{status['lifetime_total_return']:.4%}</code></li>
  </ul>
  <p>当前 runner 只把已经通过 admission 的 frozen spec 显式接出来，供下一步 scheduler + 首跑验证使用；它不等于 raw-bar live 复算已经完成。</p>
  <h2>最新一笔信号快照</h2>
  <pre>{json.dumps(latest_row or {'state': 'no-latest-row'}, ensure_ascii=False, indent=2)}</pre>
</body>
</html>
'''
    HTML_PATH.write_text(body, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank229 ETH abnormal-day paper runner")
    parser.add_argument("--init-from-now", action="store_true", help="Initialize runner state from the frozen seed and write the full paper ledger.")
    parser.add_argument("--refresh", action="store_true", help="Refresh runner artifacts from the same frozen seed.")
    parser.add_argument("--force-reinit", action="store_true", help="Allow reinitialization when state already exists.")
    args = parser.parse_args()
    if not args.init_from_now and not args.refresh:
        parser.error("choose one of --init-from-now or --refresh")

    ensure_dir(ART_DIR)
    trades, summary, spec = load_frozen_trades()
    state = load_state()

    if args.init_from_now and state and not args.force_reinit:
        parser.error(f"state already exists at {STATE_PATH}; use --force-reinit to reset")
    if args.refresh and not state:
        parser.error(f"missing state at {STATE_PATH}; run --init-from-now first")

    columns = [
        "trade_id", "candidate_id", "candidate_rank", "symbol", "venue", "bar_size", "stage", "runner_mode",
        "signal_family", "session_id", "entry_ts", "exit_ts", "holding_minutes", "gross_bps", "net_bps",
        "gross_ret", "net_ret", "cost_bps", "offset_h", "k", "min_remaining", "half", "third",
        "session_end_hour_utc", "complete_trade"
    ]
    normalized = normalize_for_csv(trades[columns])

    if args.init_from_now:
        state = initialize_state(trades, summary, spec)
        normalized.to_csv(LEDGER_PATH, index=False)
        new_rows = len(trades)
    else:
        normalized.to_csv(LEDGER_PATH, index=False)
        state["watermark_exit_ts_utc"] = iso_z(trades["exit_ts"].max()) if not trades.empty else state.get("watermark_exit_ts_utc")
        new_rows = 0

    state["wiring_status"] = "connected_runner_live"
    state["last_run_at_utc"] = iso_z(utc_now())
    state["latest_signal_ts"] = iso_z(trades["entry_ts"].max()) if not trades.empty else None
    state["latest_planned_exit_ts"] = iso_z(trades["exit_ts"].max()) if not trades.empty else None
    state["closed_trades"] = int(len(trades))
    state["lifetime_total_return"] = float((1.0 + trades["net_ret"]).prod() - 1.0) if not trades.empty else 0.0
    save_state(state)

    latest_frame = normalize_for_csv(trades[["entry_ts", "exit_ts", "gross_bps", "net_bps", "half", "third"]].tail(96))
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
            "half": row["half"],
            "third": row["third"],
            "offset_h": int(row["offset_h"]),
            "k": float(row["k"]),
            "min_remaining": int(row["min_remaining"]),
        }
    write_html(status, latest_row)

    run_summary = {
        "run_at_utc": iso_z(utc_now()),
        "mode": "init_from_now" if args.init_from_now else "refresh",
        "runner": "rank229_eth_abnormal_day_paper_runner",
        "runner_mode": RUNNER_MODE,
        "symbol": SYMBOL,
        "offset_h": SESSION_OFFSET_H,
        "k": THRESHOLD_K,
        "min_remaining": MIN_REMAINING,
        "closed_trades_total": int(len(trades)),
        "new_closed_trades_appended": int(new_rows),
        "status_path": str(STATUS_PATH.relative_to(ROOT)),
        "ledger_path": str(LEDGER_PATH.relative_to(ROOT)),
        "state_path": str(STATE_PATH.relative_to(ROOT)),
        "html_path": str(HTML_PATH.relative_to(ROOT)),
        "current_signal_path": str(CURRENT_SIGNAL_PATH.relative_to(ROOT)),
        "frozen_spec_path": str(SPEC_PATH.relative_to(ROOT)),
    }
    RUN_SUMMARY_PATH.write_text(json.dumps(run_summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(run_summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
