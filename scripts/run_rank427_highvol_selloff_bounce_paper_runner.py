#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from paper_runner_utils import (
    ROOT,
    ensure_dir,
    fetch_binance_futures_book,
    iso_z,
    read_csv_or_empty,
    utc_now,
    write_json,
)

ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank427_highvol_selloff_bounce"
SOURCE_PANEL_PATH = ROOT / "reports" / "artifacts" / "quant_digests" / "2026-04-19_highvol_selloff_bounce_5m_panel.csv"
SOURCE_SUMMARY_PATH = ROOT / "reports" / "artifacts" / "quant_digests" / "2026-04-19_highvol_selloff_bounce_summary.json"
STATUS_PATH = ART_DIR / "rank427_status.csv"
STATE_PATH = ART_DIR / "rank427_state.json"
SPEC_PATH = ART_DIR / "rank427_frozen_launch_spec.json"
LEDGER_PATH = ART_DIR / "rank427_launch_checks.csv"
SNAPSHOT_PATH = ART_DIR / "rank427_current_snapshot.csv"
SIGNAL_PATH = ART_DIR / "rank427_live_signal_snapshot.csv"
RUN_SUMMARY_PATH = ART_DIR / "rank427_last_run_summary.json"

RUNNER_SERVICE = "momentum-rank427-paper-refresh.service"
RUNNER_TIMER = "momentum-rank427-paper-refresh.timer"
SYSTEMD_DIR = Path("/etc/systemd/system")
CANDIDATE_ID = "rank427_highvol_selloff_bounce_exeth_core"
CANDIDATE_RANK = 427
CORE_SYMBOLS = ["BTCUSDT", "SOLUSDT", "BNBUSDT", "DOGEUSDT"]
EXCLUDED_SYMBOLS = ["ETHUSDT"]
INTERVAL = "5m"
LOOKBACK_BARS = 12
HOLD_BARS = 12
ROUND_TRIP_COST_BPS = 8.0


def scheduler_live() -> bool:
    return (SYSTEMD_DIR / RUNNER_SERVICE).exists() and (SYSTEMD_DIR / RUNNER_TIMER).exists() and (
        SYSTEMD_DIR / "timers.target.wants" / RUNNER_TIMER
    ).exists()


def build_spec() -> dict:
    return {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "scope": "ex-ETH core bounce sleeve only; BTC/SOL/BNB/DOGE included, ETH excluded from default live scope",
        "signal_interval": INTERVAL,
        "trigger": "high-volume selloff bounce signal from frozen 2026-04-19 digest panel; use signal=1 only",
        "entry_rule": "simple long-side paper sleeve on qualifying high-volume selloff events",
        "exit_rule": "fixed hold12 on 5m bars (~1h)",
        "core_symbols": CORE_SYMBOLS,
        "excluded_symbols": EXCLUDED_SYMBOLS,
        "round_trip_cost_bps": ROUND_TRIP_COST_BPS,
        "frozen_admission_metrics": {
            "core_hold12_net8_mean_bps": 22.86375013676087,
            "core_hold24_net8_mean_bps": 22.08227168664046,
            "core_hold36_net8_mean_bps": -3.692937653260636,
            "top2_hold12_net8_mean_bps": 21.446896761518342,
            "recent_2026_04_hold12_net8_mean_bps": 24.20,
        },
        "execution_honesty": "runner freezes ex-ETH core scope and simple hold12 short-hold sleeve; no strongest-only top1 router, no long-hold extension",
        "source_records": [
            "research/quant_digests/2026-04-19_2019_highvol-selloff-bounce-5m-alpha.md",
            "research/optimization_loop/2026-04-19_2209_rank427_highvol_selloff_bounce_freshintake_keep_p1.md",
            "research/optimization_loop/2026-04-19_2254_rank427_survivor_followup_promote_p2_exeth_corebounce.md",
            "research/optimization_loop/2026-04-19_2354_rank427_p2_exit_promote_p3_exeth_corebounce.md",
        ],
        "source_artifacts": [
            str(SOURCE_PANEL_PATH.relative_to(ROOT)),
            str(SOURCE_SUMMARY_PATH.relative_to(ROOT)),
        ],
    }


def build_snapshot(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, float | None, float | None]:
    rows: list[dict] = []
    signal_rows: list[dict] = []
    core = panel[(panel["signal"] == 1) & (panel["symbol"].isin(CORE_SYMBOLS))].copy()
    if core.empty:
        raise RuntimeError("rank427 core signal panel is empty")
    core = core.sort_values("dt").reset_index(drop=True)
    core["net12_bps"] = core["fwd_12"] * 10000.0 - ROUND_TRIP_COST_BPS
    core["net24_bps"] = core["fwd_24"] * 10000.0 - ROUND_TRIP_COST_BPS
    core["net36_bps"] = core["fwd_36"] * 10000.0 - ROUND_TRIP_COST_BPS
    top2 = core.sort_values(["dt", "shock_score"], ascending=[True, False]).groupby("dt").head(2).copy()
    top2_net12 = float(top2["net12_bps"].mean()) if not top2.empty else None
    now = utc_now()

    for symbol in CORE_SYMBOLS:
        sym = core[core["symbol"] == symbol].copy()
        if sym.empty:
            continue
        latest = sym.iloc[-1]
        bid = ask = mid = spread_bps = None
        try:
            book = fetch_binance_futures_book(symbol, limit=5)
            bid = float(book["bids"][0][0]) if book.get("bids") else None
            ask = float(book["asks"][0][0]) if book.get("asks") else None
            mid = (bid + ask) / 2.0 if bid and ask else None
            spread_bps = ((ask - bid) / mid) * 10000.0 if mid else None
        except Exception:
            spread_bps = None
            mid = None
        rows.append(
            {
                "captured_at_utc": iso_z(now),
                "candidate_rank": CANDIDATE_RANK,
                "symbol": symbol,
                "runner_role": "core_live_scope",
                "signal_interval": INTERVAL,
                "lookback_bars": LOOKBACK_BARS,
                "hold_bars": HOLD_BARS,
                "signals_n": int(len(sym)),
                "hold12_net8_mean_bps": float(sym["net12_bps"].mean()),
                "hold12_net8_median_bps": float(sym["net12_bps"].median()),
                "hold24_net8_mean_bps": float(sym["net24_bps"].mean()),
                "hold36_net8_mean_bps": float(sym["net36_bps"].mean()),
                "latest_source_signal_ts": iso_z(latest["dt"]),
                "latest_source_shock_score": float(latest["shock_score"]),
                "book_mid": mid,
                "book_spread_bps": spread_bps,
            }
        )
        signal_rows.append(
            {
                "captured_at_utc": iso_z(now),
                "symbol": symbol,
                "latest_source_signal_ts": iso_z(latest["dt"]),
                "latest_source_shock_score": float(latest["shock_score"]),
                "latest_source_vol_ratio": float(latest["vol_ratio"]),
                "latest_source_ret_n": float(latest["ret_n"]),
                "hold12_net8_bps": float(latest["net12_bps"]),
                "hold24_net8_bps": float(latest["net24_bps"]),
                "hold36_net8_bps": float(latest["net36_bps"]),
            }
        )
    snapshot = pd.DataFrame(rows)
    signal_snapshot = pd.DataFrame(signal_rows)
    core_mean = float(core["net12_bps"].mean()) if not core.empty else None
    return snapshot, signal_snapshot, core_mean, top2_net12


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank 427 high-volume selloff bounce paper runner")
    parser.add_argument("--refresh", action="store_true", help="refresh runtime artifacts")
    args = parser.parse_args()
    if not args.refresh:
        parser.error("choose --refresh")

    missing = [str(p.relative_to(ROOT)) for p in [SOURCE_PANEL_PATH, SOURCE_SUMMARY_PATH] if not p.exists()]
    if missing:
        raise FileNotFoundError(f"rank427 source artifacts missing: {missing}")

    ensure_dir(ART_DIR)
    panel = pd.read_csv(SOURCE_PANEL_PATH)
    panel["dt"] = pd.to_datetime(panel["dt"], utc=True)
    spec = build_spec()
    write_json(SPEC_PATH, spec)

    snapshot, signal_snapshot, core_hold12_mean, top2_hold12_mean = build_snapshot(panel)
    snapshot.to_csv(SNAPSHOT_PATH, index=False)
    signal_snapshot.to_csv(SIGNAL_PATH, index=False)

    live_scheduler = scheduler_live()
    wiring_status = "connected_runner_live" if live_scheduler else "runner_ready_pending_scheduler"
    blocker = "none" if live_scheduler else "scheduler_not_installed_or_not_enabled"
    now = utc_now()
    avg_spread = float(snapshot["book_spread_bps"].dropna().mean()) if snapshot["book_spread_bps"].dropna().size else None

    ledger_row = pd.DataFrame([
        {
            "captured_at_utc": iso_z(now),
            "candidate_rank": CANDIDATE_RANK,
            "runner_script": "scripts/run_rank427_highvol_selloff_bounce_paper_runner.py",
            "symbols": "|".join(CORE_SYMBOLS),
            "signal_interval": INTERVAL,
            "hold_bars": HOLD_BARS,
            "core_hold12_net8_mean_bps": core_hold12_mean,
            "top2_hold12_net8_mean_bps": top2_hold12_mean,
            "avg_book_spread_bps": avg_spread,
            "wiring_status": wiring_status,
            "verified_run": True,
        }
    ])
    prev = read_csv_or_empty(LEDGER_PATH)
    pd.concat([prev, ledger_row], ignore_index=True).to_csv(LEDGER_PATH, index=False)

    status = {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "stage": "paper_runner_ready",
        "wiring_status": wiring_status,
        "runner_mode": "frozen_scope_highvol_selloff_bounce",
        "runner_script": "scripts/run_rank427_highvol_selloff_bounce_paper_runner.py",
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "core_symbols": "|".join(CORE_SYMBOLS),
        "excluded_symbols": "|".join(EXCLUDED_SYMBOLS),
        "signal_interval": INTERVAL,
        "hold_bars": HOLD_BARS,
        "round_trip_cost_bps": ROUND_TRIP_COST_BPS,
        "core_hold12_net8_mean_bps": core_hold12_mean,
        "top2_hold12_net8_mean_bps": top2_hold12_mean,
        "avg_book_spread_bps": avg_spread,
        "updated_at_utc": iso_z(now),
        "decisive_blocker": blocker,
    }
    pd.DataFrame([status]).to_csv(STATUS_PATH, index=False)

    state = {
        **status,
        "source_records": spec["source_records"],
        "source_artifacts": spec["source_artifacts"],
        "last_run_at_utc": iso_z(now),
        "verified_run": True,
    }
    write_json(STATE_PATH, state)

    run_summary = {
        "run_at_utc": iso_z(now),
        "runner": "rank427_highvol_selloff_bounce_paper_runner",
        "wiring_status": wiring_status,
        "decisive_blocker": blocker,
        "status_path": str(STATUS_PATH.relative_to(ROOT)),
        "state_path": str(STATE_PATH.relative_to(ROOT)),
        "snapshot_path": str(SNAPSHOT_PATH.relative_to(ROOT)),
        "signal_path": str(SIGNAL_PATH.relative_to(ROOT)),
        "ledger_path": str(LEDGER_PATH.relative_to(ROOT)),
        "spec_path": str(SPEC_PATH.relative_to(ROOT)),
    }
    write_json(RUN_SUMMARY_PATH, run_summary)
    print(json.dumps(run_summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
