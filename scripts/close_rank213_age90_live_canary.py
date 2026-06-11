#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.execution.canary32b.frmonitor_bridge import load_frmonitor_bridge  # noqa: E402

CONFIG_PATH = ROOT / "config" / "execution" / "rank213_age90_live_canary.yaml"
LIVE_STATE_PATH = ROOT / "reports" / "artifacts" / "rank213_age90_live_canary_shell" / "live_state.json"
LIVE_STATUS_PATH = ROOT / "reports" / "artifacts" / "rank213_age90_live_canary_shell" / "live_status.json"
LIVE_EXCHANGE_POSITIONS_PATH = ROOT / "reports" / "artifacts" / "rank213_age90_live_canary_shell" / "live_exchange_positions.json"
RECEIPT_PATH = ROOT / "reports" / "artifacts" / "rank213_age90_live_canary_shell" / "rank213_archive_closeout_receipt.json"
TIMER_UNITS = [
    "momentum-rank213-age90-live-canary.timer",
    "momentum-rank213-age90-shadow-runner.timer",
    "momentum-rank213-age90-live-pending.timer",
]


def iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def exchange_open_qty_for_position(positions_payload: Any, *, symbol: str, side: str) -> float:
    rows = positions_payload if isinstance(positions_payload, list) else [positions_payload]
    pair = symbol.upper()
    normalized_side = str(side or "").strip().lower()
    normalized_side = "long" if normalized_side in {"buy", "long"} else "short"
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


def load_owned_positions(state: dict[str, Any], status: dict[str, Any], exchange_positions: Any) -> list[dict[str, Any]]:
    candidate_rows: list[dict[str, Any]] = []
    if isinstance(exchange_positions, list) and exchange_positions:
        candidate_rows = [row for row in exchange_positions if isinstance(row, dict)]
    elif isinstance(state.get("exchange_reconciliation"), dict):
        candidate_rows = [row for row in state.get("exchange_reconciliation", {}).get("positions", []) if isinstance(row, dict)]
    else:
        candidate_rows = [row for row in status.get("exchange_open_positions", []) if isinstance(row, dict)]

    deduped: dict[tuple[str, str], dict[str, Any]] = {}
    for row in candidate_rows:
        if not bool(row.get("rank213_owned")):
            continue
        symbol = str(row.get("symbol") or "").upper().strip()
        side = str(row.get("side") or "").lower().strip()
        qty = abs(safe_float(row.get("qty") or row.get("exchange_qty_abs")))
        if not symbol or side not in {"long", "short"} or qty <= 0:
            continue
        key = (symbol, side)
        deduped[key] = {
            "symbol": symbol,
            "side": side,
            "qty": qty,
            "entry_price": safe_float(row.get("entry_price"), default=0.0),
            "unrealized_pnl": safe_float(row.get("unrealized_pnl"), default=0.0),
            "position_side": "LONG" if side == "long" else "SHORT",
            "exit_order_side": "SELL" if side == "long" else "BUY",
            "basket_ids": [str(v) for v in (row.get("matched_basket_ids") or []) if str(v)],
            "reconciliation_classification": str(row.get("reconciliation_classification") or ""),
        }
    return list(deduped.values())


def compute_pre_close_metrics(state: dict[str, Any], positions: list[dict[str, Any]]) -> dict[str, Any]:
    closed_trades = state.get("closed_trades", []) if isinstance(state.get("closed_trades"), list) else []
    realized_net_pnl = sum(safe_float(row.get("net_pnl")) for row in closed_trades if isinstance(row, dict))
    closed_basket_ids = {
        str(row.get("basket_id") or "")
        for row in closed_trades
        if isinstance(row, dict) and str(row.get("basket_id") or "")
    }
    open_unrealized = sum(safe_float(row.get("unrealized_pnl")) for row in positions)
    return {
        "realized_net_pnl": realized_net_pnl,
        "closed_trade_count": len(closed_trades),
        "closed_basket_count": len(closed_basket_ids),
        "open_unrealized_pnl": open_unrealized,
        "snapshot_total_pnl": realized_net_pnl + open_unrealized,
    }


def disable_timers(units: list[str]) -> tuple[str, list[dict[str, Any]]]:
    results: list[dict[str, Any]] = []
    all_ok = True
    for unit in units:
        proc = subprocess.run(
            ["systemctl", "disable", "--now", unit],
            check=False,
            capture_output=True,
            text=True,
        )
        ok = proc.returncode == 0
        all_ok = all_ok and ok
        results.append(
            {
                "unit": unit,
                "returncode": proc.returncode,
                "stdout": proc.stdout.strip(),
                "stderr": proc.stderr.strip(),
                "ok": ok,
            }
        )
    return ("all_disabled" if all_ok else "partial_or_failed"), results


def main() -> int:
    ap = argparse.ArgumentParser(description="Close out rank213 age90 live canary positions and optionally stop timers.")
    ap.add_argument("--config", default=str(CONFIG_PATH))
    ap.add_argument("--receipt", default=str(RECEIPT_PATH))
    ap.add_argument("--allow-live", action="store_true", help="Actually submit reduce-only market flatten orders.")
    ap.add_argument("--stop-timers", action="store_true", help="Disable and stop rank213 age90 systemd timers after flatten.")
    args = ap.parse_args()

    cfg = load_yaml(Path(args.config))
    phase3 = cfg.get("phase3", {}) if isinstance(cfg.get("phase3"), dict) else {}
    state = read_json(LIVE_STATE_PATH, {}) or {}
    status = read_json(LIVE_STATUS_PATH, {}) or {}
    exchange_positions = read_json(LIVE_EXCHANGE_POSITIONS_PATH, []) or []
    owned_positions = load_owned_positions(state, status, exchange_positions)

    receipt: dict[str, Any] = {
        "generated_at_utc": iso_now(),
        "strategy_id": str(((cfg.get("meta") or {}) if isinstance(cfg.get("meta"), dict) else {}).get("strategy_id") or "rank213_age90"),
        "mode": "execute" if args.allow_live else "dry_run",
        "closeout_reason": "sustained_loss_archive",
        "source_paths": {
            "config": str(Path(args.config)),
            "live_state": str(LIVE_STATE_PATH),
            "live_status": str(LIVE_STATUS_PATH),
            "live_exchange_positions": str(LIVE_EXCHANGE_POSITIONS_PATH),
        },
        "pending_entries_count": len(state.get("pending_entries", []) if isinstance(state.get("pending_entries"), list) else []),
        "pending_entries_symbols": [str(row.get("symbol") or "") for row in (state.get("pending_entries") or []) if isinstance(row, dict)],
        "positions_to_flatten": owned_positions,
        "pre_close_metrics": compute_pre_close_metrics(state, owned_positions),
        "flatten_orders": [],
        "remaining_positions_after_flatten": [],
        "remaining_position_count_after_flatten": len(owned_positions),
        "flatten_status": "dry_run_no_orders",
        "timers_disable_status": "not_requested",
        "timer_results": [],
        "flatten_submitted_at_utc": None,
        "timers_disabled_at_utc": None,
    }

    if not args.allow_live:
        write_json(Path(args.receipt), receipt)
        print(json.dumps({
            "mode": receipt["mode"],
            "positions_to_flatten": len(owned_positions),
            "pending_entries_count": receipt["pending_entries_count"],
            "snapshot_total_pnl": receipt["pre_close_metrics"]["snapshot_total_pnl"],
        }, ensure_ascii=False, indent=2))
        return 0

    bridge = load_frmonitor_bridge(
        phase3.get("fr_monitor_root", "/root/jerry/wlfi/FR_Monitor"),
        local_private_path=phase3.get("local_private_path"),
    )
    pre_positions_payload = bridge.get_binance_perp_positions()
    submitted_at = iso_now()
    receipt["flatten_submitted_at_utc"] = submitted_at

    orders: list[dict[str, Any]] = []
    for row in owned_positions:
        current_qty = exchange_open_qty_for_position(pre_positions_payload, symbol=row["symbol"], side=row["side"])
        if current_qty <= 0:
            orders.append({
                **row,
                "requested_qty": row["qty"],
                "current_exchange_qty": current_qty,
                "status": "already_flat_or_missing",
            })
            continue
        client_order_id = f"r213-close-{row['symbol'].lower()[:8]}-{datetime.now(timezone.utc).strftime('%H%M%S')}"[:36]
        result = bridge.place_binance_perp_live_market_order(
            symbol=row["symbol"],
            side=row["exit_order_side"],
            quantity=current_qty,
            reduce_only=True,
            position_side=row["position_side"],
            client_order_id=client_order_id,
        )
        orders.append(
            {
                **row,
                "requested_qty": row["qty"],
                "current_exchange_qty": current_qty,
                "submitted_qty": current_qty,
                "client_order_id": client_order_id,
                "result": result,
                "status": "submitted",
            }
        )

    post_positions_payload = bridge.get_binance_perp_positions()
    remaining_positions: list[dict[str, Any]] = []
    for row in owned_positions:
        remaining_qty = exchange_open_qty_for_position(post_positions_payload, symbol=row["symbol"], side=row["side"])
        if remaining_qty > 0:
            remaining_positions.append(
                {
                    "symbol": row["symbol"],
                    "side": row["side"],
                    "remaining_qty": remaining_qty,
                }
            )

    receipt["flatten_orders"] = orders
    receipt["remaining_positions_after_flatten"] = remaining_positions
    receipt["remaining_position_count_after_flatten"] = len(remaining_positions)
    receipt["flatten_status"] = "flatten_submitted_and_cleared" if not remaining_positions else "flatten_submitted_but_positions_remain"

    if args.stop_timers:
        timer_status, timer_results = disable_timers(TIMER_UNITS)
        receipt["timers_disable_status"] = timer_status
        receipt["timer_results"] = timer_results
        receipt["timers_disabled_at_utc"] = iso_now()

    write_json(Path(args.receipt), receipt)
    print(json.dumps({
        "flatten_status": receipt["flatten_status"],
        "remaining_position_count_after_flatten": receipt["remaining_position_count_after_flatten"],
        "timers_disable_status": receipt["timers_disable_status"],
        "pending_entries_count": receipt["pending_entries_count"],
        "snapshot_total_pnl": receipt["pre_close_metrics"]["snapshot_total_pnl"],
    }, ensure_ascii=False, indent=2))
    return 0 if not remaining_positions and receipt["timers_disable_status"] in {"not_requested", "all_disabled"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
