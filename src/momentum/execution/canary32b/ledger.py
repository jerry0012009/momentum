from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _parse_utc(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except Exception:
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except Exception:
            return None


def build_phase3_order_ledger(
    orders: list[dict[str, Any]],
    intentions: list[dict[str, Any]],
    receipt_chains: list[dict[str, Any]],
    *,
    now_utc: str,
    default_ttl_minutes: int,
) -> list[dict[str, Any]]:
    intent_map = {str(x.get("intention_id")): x for x in intentions}
    chain_map = {str(x.get("broker_order_id")): x for x in receipt_chains}
    now_dt = _parse_utc(now_utc) or datetime.now(timezone.utc)
    rows: list[dict[str, Any]] = []

    for order in orders:
        broker_order_id = str(order.get("broker_order_id") or "")
        intention_id = str(order.get("intention_id") or "")
        intent = intent_map.get(intention_id, {})
        chain = chain_map.get(broker_order_id, {})
        chain_stage = str(chain.get("stage") or "")
        submit_dt = _parse_utc(str(order.get("submit_at") or ""))
        ttl_minutes = int(intent.get("ttl_minutes") or default_ttl_minutes)
        expires_at = submit_dt.timestamp() + ttl_minutes * 60 if submit_dt is not None else None

        status = str(order.get("status") or "")
        if chain_stage == "cancelled_no_fill" and status == "NEW":
            status = "CANCELLED"

        ttl_state = "unknown"
        seconds_remaining = None
        if status in {"CANCELLED", "FILLED", "REJECTED"}:
            ttl_state = "finalized"
        elif expires_at is not None:
            seconds_remaining = int(expires_at - now_dt.timestamp())
            ttl_state = "expired" if seconds_remaining <= 0 else "live"

        rows.append(
            {
                "symbol": order.get("symbol"),
                "side": order.get("side"),
                "broker_order_id": broker_order_id,
                "intention_id": intention_id,
                "submit_mode": order.get("submit_mode"),
                "status": status,
                "ttl_minutes": ttl_minutes,
                "ttl_state": ttl_state,
                "seconds_remaining": seconds_remaining,
                "receipt_chain_stage": chain_stage,
                "capital_deployed": bool(chain.get("capital_deployed", False)),
                "submit_at": order.get("submit_at"),
                "last_update_at": order.get("last_update_at"),
            }
        )
    return rows
