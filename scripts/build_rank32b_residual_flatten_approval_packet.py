#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "rank32b_final_goal_gate"
BLOCKER_PACKET = ART_DIR / "residual_position_blocker_packet.json"
EXECUTION_SCRIPT = ROOT / "scripts" / "execute_rank32b_residual_flatten_after_approval.py"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _extract_exchange_position(packet: dict[str, Any]) -> dict[str, Any] | None:
    warning = packet.get("latest_warning") or {}
    payload = warning.get("payload") or {}
    pos = payload.get("exchange_position")
    return pos if isinstance(pos, dict) else None


def _flatten_side(position: dict[str, Any]) -> str:
    side = str(position.get("side") or "").lower()
    qty = float(position.get("qty") or 0.0)
    if side == "short" or qty < 0:
        return "BUY"
    if side == "long" or qty > 0:
        return "SELL"
    raise ValueError(f"cannot infer flatten side from position: {position}")


def build_packet() -> dict[str, Any]:
    if not BLOCKER_PACKET.exists():
        raise FileNotFoundError(f"missing blocker packet: {BLOCKER_PACKET}")

    blocker = read_json(BLOCKER_PACKET)
    pos = _extract_exchange_position(blocker)
    if not pos:
        return {
            "status": "no_residual_position",
            "source": str(BLOCKER_PACKET.relative_to(ROOT)),
            "automation_policy": "No order was generated or submitted.",
        }

    qty = abs(float(pos.get("qty") or 0.0))
    if qty <= 0:
        raise ValueError(f"residual position has non-positive qty: {pos}")

    symbol = str(pos.get("symbol") or "").upper()
    position_side = str(pos.get("position_side") or pos.get("raw", {}).get("positionSide") or "").upper()
    if not symbol or not position_side:
        raise ValueError(f"missing symbol or position_side in residual position: {pos}")

    order_side = _flatten_side(pos)
    created_at = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    client_order_id_template = f"r32b-goal-flatten-{symbol}-{datetime.now(UTC):%Y%m%d}"

    return {
        "status": "awaiting_operator_approval",
        "created_at": created_at,
        "source": str(BLOCKER_PACKET.relative_to(ROOT)),
        "blocker": blocker.get("blocker"),
        "rank213_attribution": blocker.get("rank213_attribution"),
        "residual_position_snapshot": pos,
        "proposed_order": {
            "venue": "binance_usdt_perp",
            "symbol": symbol,
            "type": "MARKET",
            "side": order_side,
            "quantity": format(qty, "f"),
            "position_side": position_side,
            "reduce_only": True,
            "client_order_id_template": client_order_id_template[:36],
            "intent": "flatten_residual_exchange_position_only",
        },
        "prepared_execution_script": str(EXECUTION_SCRIPT.relative_to(ROOT)),
        "prepared_execution_policy": (
            "The prepared script defaults to dry-run. Real execution requires --execute-live-order, "
            "the exact operator approval token, and matching symbol/position_side flags."
        ),
        "execution_safety_checks": [
            "Do not execute unless the operator explicitly approves a real order.",
            "Immediately before execution, re-fetch Binance open positions and require the same symbol and position_side to still be open.",
            "Use the freshly fetched absolute position amount, not an older cached quantity, if the exchange quantity changed.",
            "Abort if the current position side no longer matches the proposed flatten side.",
            "Submit as reduce_only=True with position_side set; if Binance rejects reduceOnly as not required in the current account mode, retry may only omit reduceOnly while preserving the same position_side and quantity cap.",
            "After execution, re-run the rank32b residual blocker packet and final goal gate.",
        ],
        "automation_policy": "This artifact is an approval packet only. It does not import trading credentials, sign requests, or submit orders.",
    }


def render_markdown(packet: dict[str, Any]) -> str:
    if packet["status"] != "awaiting_operator_approval":
        return f"""# Rank32b Residual Flatten Approval Packet

Status: `{packet["status"]}`

Automation policy:

{packet["automation_policy"]}
"""

    order = packet["proposed_order"]
    pos = packet["residual_position_snapshot"]
    checks = "\n".join(f"- {row}" for row in packet["execution_safety_checks"])
    return f"""# Rank32b Residual Flatten Approval Packet

Status: `{packet["status"]}`

This packet is intentionally non-executing. It records the exact residual position that blocks the rank32b final goal gate and the real-order action that would need explicit operator approval.

## Residual Position Snapshot

- symbol: `{pos.get("symbol")}`
- side: `{pos.get("side")}`
- qty: `{pos.get("qty")}`
- position_side: `{pos.get("position_side")}`
- entry_price: `{pos.get("entry_price")}`
- unrealized_pnl: `{pos.get("unrealized_pnl")}`

## Proposed Flatten Order

- venue: `{order["venue"]}`
- symbol: `{order["symbol"]}`
- type: `{order["type"]}`
- side: `{order["side"]}`
- quantity: `{order["quantity"]}`
- position_side: `{order["position_side"]}`
- reduce_only: `{order["reduce_only"]}`
- client_order_id_template: `{order["client_order_id_template"]}`

## Required Safety Checks

{checks}

## Automation Policy

{packet["automation_policy"]}
"""


def main() -> int:
    packet = build_packet()
    write_json(ART_DIR / "residual_flatten_approval_packet.json", packet)
    (ART_DIR / "residual_flatten_approval_packet.md").write_text(render_markdown(packet), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": packet["status"],
                "path": str((ART_DIR / "residual_flatten_approval_packet.json").relative_to(ROOT)),
                "proposed_order": packet.get("proposed_order"),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
