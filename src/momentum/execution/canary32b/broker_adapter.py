from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Protocol

from momentum.domain.canary32b_models import BrokerOrderRecord, OrderIntention, utc_now_iso


class BrokerAdapter(Protocol):
    mode: str

    def place_entry_order(self, intention: OrderIntention) -> BrokerOrderRecord: ...

    def query_order(self, order: BrokerOrderRecord) -> BrokerOrderRecord: ...

    def cancel_order(self, order: BrokerOrderRecord) -> BrokerOrderRecord: ...


@dataclass(slots=True)
class TestNoFillBrokerAdapter:
    mode: str = "test_no_fill"

    def _order_id(self, intention: OrderIntention) -> str:
        digest = hashlib.sha1(f"{intention.intention_id}|{self.mode}".encode("utf-8")).hexdigest()[:14]
        return f"ord-{digest}"

    def place_entry_order(self, intention: OrderIntention) -> BrokerOrderRecord:
        now = utc_now_iso()
        return BrokerOrderRecord(
            broker_order_id=self._order_id(intention),
            intention_id=intention.intention_id,
            signal_id=intention.signal_id,
            symbol=intention.symbol,
            side=intention.side.value,
            order_role=intention.order_role.value,
            order_type=intention.order_type.value,
            target_price=float(intention.target_price),
            qty=float(intention.qty),
            status="NEW",
            submit_mode=self.mode,
            submit_at=now,
            last_update_at=now,
            filled_qty=0.0,
            avg_fill_price=None,
            venue_ref=f"sim://{self._order_id(intention)}",
            metadata={
                "no_fill": True,
                "ack_only": True,
                "capital_deployed": False,
            },
        )

    def query_order(self, order: BrokerOrderRecord) -> BrokerOrderRecord:
        order.last_update_at = utc_now_iso()
        if order.status not in {"CANCELLED", "FILLED", "REJECTED"}:
            order.status = "NEW"
        return order

    def cancel_order(self, order: BrokerOrderRecord) -> BrokerOrderRecord:
        order.status = "CANCELLED"
        order.last_update_at = utc_now_iso()
        return order
