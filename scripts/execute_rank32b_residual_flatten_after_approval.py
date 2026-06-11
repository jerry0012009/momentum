#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

CONFIG_PATH = ROOT / "config" / "execution" / "rank32b_canary.yaml"
ART_DIR = ROOT / "reports" / "artifacts" / "rank32b_final_goal_gate"
APPROVAL_PACKET = ART_DIR / "residual_flatten_approval_packet.json"
EXECUTION_PLAN = ART_DIR / "residual_flatten_execution_plan.json"
EXECUTION_RECEIPT = ART_DIR / "residual_flatten_execution_receipt.json"
APPROVAL_TOKEN = "EXECUTE_ONUSDT_SHORT_FLATTEN_20260504"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


phase6lib = load_module(ROOT / "scripts" / "run_rank32b_canary_phase6.py", "rank32b_residual_flatten_phase6lib")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def normalize_positions(payload: Any) -> list[dict[str, Any]]:
    rows = payload if isinstance(payload, list) else [payload]
    return [row for row in rows if isinstance(row, dict)]


def position_qty(row: dict[str, Any]) -> float:
    return phase6lib.safe_float(row.get("positionAmt"), 0.0)


def find_current_position(rows: list[dict[str, Any]], *, symbol: str, position_side: str) -> dict[str, Any] | None:
    symbol_u = symbol.upper()
    pos_side_u = position_side.upper()
    for row in rows:
        if str(row.get("symbol") or "").upper() != symbol_u:
            continue
        if str(row.get("positionSide") or "BOTH").upper() != pos_side_u:
            continue
        if abs(position_qty(row)) > 0:
            return row
    return None


def expected_flatten_side(position_side: str, qty: float) -> str:
    side = position_side.upper()
    if side == "SHORT" or qty < 0:
        return "BUY"
    if side == "LONG" or qty > 0:
        return "SELL"
    raise ValueError(f"cannot infer flatten side for position_side={position_side!r} qty={qty!r}")


def load_bridge(config_path: Path) -> Any:
    cfg = phase6lib.load_yaml(config_path)
    phase3 = cfg.get("phase3", {}) if isinstance(cfg.get("phase3"), dict) else {}
    return phase6lib.load_frmonitor_bridge(
        phase3["fr_monitor_root"],
        local_private_path=phase3.get("local_private_path"),
    )


def build_plan(packet: dict[str, Any]) -> dict[str, Any]:
    order = packet.get("proposed_order") or {}
    pos = packet.get("residual_position_snapshot") or {}
    return {
        "status": "plan_ready_awaiting_operator_approval",
        "approval_packet": str(APPROVAL_PACKET.relative_to(ROOT)),
        "required_approval_token": APPROVAL_TOKEN,
        "automation_policy": "Default mode is non-executing. A real order requires --execute-live-order and exact approval flags.",
        "residual_position_snapshot": pos,
        "proposed_order": order,
        "required_command_shape": (
            "python3 scripts/execute_rank32b_residual_flatten_after_approval.py "
            "--execute-live-order --operator-approval-token EXECUTE_ONUSDT_SHORT_FLATTEN_20260504 "
            "--approve-symbol ONUSDT --approve-position-side SHORT"
        ),
        "preflight_checks": [
            "approval packet status must be awaiting_operator_approval",
            "symbol and position_side flags must exactly match the approval packet",
            "fresh exchange position must still exist for the same symbol and position_side",
            "fresh exchange position sign must imply the same flatten side",
            "fresh quantity must be positive and must not exceed the approved quantity unless --allow-larger-current-qty is explicitly used",
        ],
    }


def execute(args: argparse.Namespace) -> dict[str, Any]:
    packet = read_json(APPROVAL_PACKET)
    if packet.get("status") != "awaiting_operator_approval":
        raise SystemExit(f"approval packet not executable: status={packet.get('status')!r}")

    order = packet.get("proposed_order") or {}
    symbol = str(order.get("symbol") or "").upper()
    position_side = str(order.get("position_side") or "").upper()
    proposed_side = str(order.get("side") or "").upper()
    proposed_qty = phase6lib.safe_float(order.get("quantity"), 0.0)
    if not symbol or not position_side or proposed_qty <= 0:
        raise SystemExit(f"invalid proposed order in approval packet: {order}")

    if args.operator_approval_token != APPROVAL_TOKEN:
        raise SystemExit("operator approval token mismatch")
    if str(args.approve_symbol or "").upper() != symbol:
        raise SystemExit(f"approved symbol mismatch: expected {symbol}")
    if str(args.approve_position_side or "").upper() != position_side:
        raise SystemExit(f"approved position_side mismatch: expected {position_side}")

    bridge = load_bridge(Path(args.config))
    current_positions = normalize_positions(bridge.get_binance_perp_positions(symbol=symbol))
    current = find_current_position(current_positions, symbol=symbol, position_side=position_side)
    if current is None:
        receipt = {
            "status": "clear_no_order_submitted",
            "reason": "fresh exchange query found no matching open position",
            "symbol": symbol,
            "position_side": position_side,
            "current_positions": current_positions,
        }
        write_json(EXECUTION_RECEIPT, receipt)
        return receipt

    fresh_qty_signed = position_qty(current)
    fresh_qty_abs = abs(fresh_qty_signed)
    if fresh_qty_abs <= 0:
        raise SystemExit(f"fresh exchange position has non-positive qty: {current}")
    fresh_side = expected_flatten_side(position_side, fresh_qty_signed)
    if fresh_side != proposed_side:
        raise SystemExit(f"fresh flatten side {fresh_side} does not match approved side {proposed_side}: {current}")
    if fresh_qty_abs > proposed_qty and not args.allow_larger_current_qty:
        raise SystemExit(f"fresh qty {fresh_qty_abs} exceeds approved qty {proposed_qty}; rerun with a fresh approval packet")

    client_order_id = str(order.get("client_order_id_template") or "r32b-goal-flatten")[:36]
    live_order = bridge.place_binance_perp_live_market_order(
        symbol=symbol,
        side=proposed_side,
        quantity=fresh_qty_abs,
        reduce_only=True,
        position_side=position_side,
        client_order_id=client_order_id,
    )
    normalized = phase6lib.normalize_order_payload(live_order, source="rank32b_goal_residual_flatten")
    receipt = {
        "status": "submitted",
        "symbol": symbol,
        "position_side": position_side,
        "side": proposed_side,
        "quantity": fresh_qty_abs,
        "reduce_only_requested": True,
        "fresh_position_before": current,
        "order": live_order,
        "normalized_order": normalized,
        "post_execution_note": "Re-run residual blocker and final goal gate after exchange state updates.",
    }
    write_json(EXECUTION_RECEIPT, receipt)

    if args.refresh_gate:
        for script in (
            "scripts/build_rank32b_residual_position_blocker_packet.py",
            "scripts/build_rank32b_residual_flatten_approval_packet.py",
            "scripts/build_rank32b_live_shadow_diagnostic.py",
            "scripts/build_rank32b_final_goal_gate.py",
        ):
            subprocess.run([sys.executable, script], cwd=str(ROOT), check=False)
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="Execute approved rank32b account-level residual flatten, default dry-run")
    ap.add_argument("--config", default=str(CONFIG_PATH))
    ap.add_argument("--execute-live-order", action="store_true", help="Submit the real Binance flatten order after all explicit approval checks pass")
    ap.add_argument("--operator-approval-token", default="")
    ap.add_argument("--approve-symbol", default="")
    ap.add_argument("--approve-position-side", default="")
    ap.add_argument("--allow-larger-current-qty", action="store_true", help="Allow fresh exchange qty to exceed the approval packet qty")
    ap.add_argument("--refresh-gate", action="store_true", help="After a submitted order, rerun local gate builders")
    args = ap.parse_args()

    packet = read_json(APPROVAL_PACKET)
    plan = build_plan(packet)
    write_json(EXECUTION_PLAN, plan)
    if not args.execute_live_order:
        print(json.dumps({"status": plan["status"], "plan_path": str(EXECUTION_PLAN.relative_to(ROOT))}, ensure_ascii=False))
        return 0

    receipt = execute(args)
    print(json.dumps({"status": receipt["status"], "receipt_path": str(EXECUTION_RECEIPT.relative_to(ROOT))}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
