from __future__ import annotations

from momentum.domain.canary32b_models import AlphaSignal, IntentionStatus, OrderIntention, OrderRole, OrderType


def build_entry_intention(
    signal: AlphaSignal,
    *,
    intention_id: str,
    trace_id: str,
    qty: float,
    target_price: float,
    ttl_minutes: int,
    fallback_to_taker: bool,
    config_version: str,
) -> OrderIntention:
    return OrderIntention(
        intention_id=intention_id,
        signal_id=signal.signal_id,
        symbol=signal.symbol,
        side=signal.side,
        order_role=OrderRole.ENTRY,
        order_type=OrderType.LIMIT,
        target_price=float(target_price),
        qty=float(qty),
        ttl_minutes=int(ttl_minutes),
        created_at=signal.timestamp,
        status=IntentionStatus.CREATED,
        trace_id=trace_id,
        metadata={
            "fallback_to_taker": bool(fallback_to_taker),
            "config_version": config_version,
            "alpha_name": signal.alpha_name,
            "alpha_version": signal.alpha_version,
            "symbol_bucket": (signal.metadata or {}).get("symbol_bucket"),
        },
    )
