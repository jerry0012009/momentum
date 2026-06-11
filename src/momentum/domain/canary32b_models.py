from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any


class Side(StrEnum):
    LONG = "long"
    SHORT = "short"


class OrderRole(StrEnum):
    ENTRY = "entry"
    TAKE_PROFIT = "take_profit"
    TIMEOUT_EXIT = "timeout_exit"
    FORCED_EXIT = "forced_exit"


class OrderType(StrEnum):
    LIMIT = "limit"
    MARKET = "market"


class IntentionStatus(StrEnum):
    CREATED = "created"
    BLOCKED = "blocked"
    SUBMITTED = "submitted"
    CANCELLED = "cancelled"
    FILLED = "filled"


class PositionState(StrEnum):
    FLAT = "flat"
    ENTRY_PENDING = "entry_pending"
    LIVE_POSITION = "live_position"
    EXIT_PENDING = "exit_pending"
    CLOSED = "closed"
    BLOCKED = "blocked"


class EventType(StrEnum):
    SIGNAL_RECEIVED = "SignalReceived"
    INTENTION_CREATED = "IntentionCreated"
    RISK_REJECTED = "RiskRejected"
    ORDER_PLACED = "OrderPlaced"
    ORDER_ACK = "OrderAck"
    ORDER_STATUS_SYNC = "OrderStatusSync"
    ORDER_PARTIALLY_FILLED = "OrderPartiallyFilled"
    ORDER_FILLED = "OrderFilled"
    ORDER_CANCELLED = "OrderCancelled"
    TIMEOUT_TRIGGERED = "TimeoutTriggered"
    POSITION_OPENED = "PositionOpened"
    POSITION_CLOSED = "PositionClosed"
    EXEC_REJECT = "ExecReject"
    EMERGENCY_STOP = "EmergencyStop"
    WARNING_RAISED = "WarningRaised"


@dataclass(slots=True)
class AlphaSignal:
    signal_id: str
    timestamp: str
    symbol: str
    side: Side
    signal_price: float
    alpha_name: str
    alpha_version: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class OrderIntention:
    intention_id: str
    signal_id: str
    symbol: str
    side: Side
    order_role: OrderRole
    order_type: OrderType
    target_price: float
    qty: float
    ttl_minutes: int
    created_at: str
    status: IntentionStatus
    trace_id: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class RiskDecision:
    accepted: bool
    reason: str
    trace_id: str
    checks: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class EventRecord:
    timestamp: str
    event_type: EventType
    symbol: str
    side: str
    trace_id: str
    message: str
    payload: dict[str, Any] = field(default_factory=dict)
    level: str = "INFO"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class StrategyStatusSnapshot:
    alpha_name: str
    version: str
    mode: str
    enabled_symbols: list[str]
    current_config_hash: str
    last_signal_time: str | None
    system_health: str
    last_run_utc: str
    trade_enabled: bool
    kill_switch: bool
    recent_signal_count: int
    recent_intention_count: int
    recent_reject_count: int
    notes: list[str] = field(default_factory=list)
    latest_evaluated_bar_time: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class SymbolRuntimeState:
    symbol: str
    position_state: PositionState
    active_signal_id: str | None = None
    active_intention_id: str | None = None
    last_event_time: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class BrokerOrderRecord:
    broker_order_id: str
    intention_id: str
    signal_id: str
    symbol: str
    side: str
    order_role: str
    order_type: str
    target_price: float
    qty: float
    status: str
    submit_mode: str
    submit_at: str
    last_update_at: str
    filled_qty: float = 0.0
    avg_fill_price: float | None = None
    venue_ref: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ReceiptChainRecord:
    trace_id: str
    signal_id: str
    intention_id: str
    broker_order_id: str
    symbol: str
    stage: str
    complete: bool
    capital_deployed: bool
    steps: list[str] = field(default_factory=list)
    refs: dict[str, Any] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
