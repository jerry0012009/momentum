#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.domain.canary32b_models import (  # noqa: E402
    BrokerOrderRecord,
    EventRecord,
    EventType,
    PositionState,
    ReceiptChainRecord,
    StrategyStatusSnapshot,
    SymbolRuntimeState,
    utc_now_iso,
)
from momentum.execution.canary32b.broker_adapter import TestNoFillBrokerAdapter  # noqa: E402
from momentum.execution.canary32b.event_bus import JsonlEventBus  # noqa: E402
from momentum.execution.canary32b.intention_layer import build_entry_intention  # noqa: E402
from momentum.execution.canary32b.signal_adapter import Rank32BPerpSignalAdapter  # noqa: E402
from momentum.execution.canary32b.state_store import JsonStateStore  # noqa: E402
from momentum.risk.canary32b_guard import (  # noqa: E402
    Canary32BMarketContext,
    Canary32BRiskConfig,
    evaluate_entry_risk,
    portfolio_state_from_runtime,
)

CONFIG_PATH = ROOT / "config" / "execution" / "rank32b_canary.yaml"
ART_DIR = ROOT / "reports" / "artifacts" / "rank32b_canary"
EVENTS_PATH = ART_DIR / "phase2_events.jsonl"
STATE_PATH = ART_DIR / "phase2_state.json"
STATUS_PATH = ART_DIR / "phase2_status.json"
RUN_SUMMARY_PATH = ART_DIR / "phase2_last_run_summary.json"
SIGNALS_PATH = ART_DIR / "phase2_recent_signals.json"
INTENTIONS_PATH = ART_DIR / "phase2_recent_intentions.json"
ORDERS_PATH = ART_DIR / "phase2_recent_orders.json"
REJECTIONS_PATH = ART_DIR / "phase2_recent_rejections.json"
CHAINS_PATH = ART_DIR / "phase2_receipt_chains.json"
SYMBOL_STATE_PATH = ART_DIR / "phase2_symbol_state.json"
OPERATOR_PACKET_PATH = ART_DIR / "phase2_operator_packet.json"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def config_hash(cfg: dict[str, Any]) -> str:
    normalized = json.dumps(cfg, ensure_ascii=False, sort_keys=True)
    return hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:16]


class Phase2State:
    def __init__(self, raw: dict[str, Any] | None = None) -> None:
        raw = raw or {}
        self.seen_signal_ids: list[str] = list(raw.get("seen_signal_ids", []))
        self.symbol_states: list[dict[str, Any]] = list(raw.get("symbol_states", []))
        self.daily_trade_count: int = int(raw.get("daily_trade_count", 0))
        self.last_run_utc: str | None = raw.get("last_run_utc")

    def to_dict(self) -> dict[str, Any]:
        return {
            "seen_signal_ids": self.seen_signal_ids[-2000:],
            "symbol_states": self.symbol_states,
            "daily_trade_count": int(self.daily_trade_count),
            "last_run_utc": self.last_run_utc,
        }


def load_state(path: Path, symbols: list[str]) -> Phase2State:
    store = JsonStateStore(path)
    raw = store.load({})
    state = Phase2State(raw)
    if not state.symbol_states:
        state.symbol_states = [
            SymbolRuntimeState(symbol=symbol, position_state=PositionState.FLAT, active_signal_id=None, active_intention_id=None, last_event_time=None).to_dict()
            for symbol in symbols
        ]
    return state


def make_trace_id(signal_id: str) -> str:
    return f"trace-{hashlib.sha1(signal_id.encode('utf-8')).hexdigest()[:12]}"


def build_packet(signal: dict[str, Any], intention: dict[str, Any], order: dict[str, Any], receipt_chain: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_id": "rank32b_canary",
        "deployment_scope": "phase2_receipt_chain_only",
        "required_receipt_chain": "intent -> ack -> status_sync -> cancel -> final_status",
        "allowed_operator_action": "one isolated test/no-fill receipt-chain replay; no capital deployment",
        "signal": signal,
        "intention": intention,
        "order": order,
        "receipt_chain": receipt_chain,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Rank 32b canary Phase-2 minimal receipt-chain loop.")
    parser.add_argument("--config", default=str(CONFIG_PATH))
    parser.add_argument("--force-replay", action="store_true")
    args = parser.parse_args()

    ensure_dir(ART_DIR)
    cfg = load_yaml(Path(args.config))
    state = load_state(STATE_PATH, cfg["universe"]["symbols"])
    adapter = Rank32BPerpSignalAdapter(
        asset_to_symbol=cfg["universe"]["asset_to_symbol"],
        days=int(cfg["signal_adapter"]["lookback_days"]),
        recent_hours=int(cfg["signal_adapter"]["recent_hours"]),
        variant=str(cfg["signal_adapter"]["variant"]),
        refresh_bars=bool(cfg["signal_adapter"].get("refresh_bars", True)),
        refresh_tail_days=(
            int(cfg["signal_adapter"]["refresh_tail_days"])
            if cfg["signal_adapter"].get("refresh_tail_days") is not None
            else None
        ),
    )
    broker = TestNoFillBrokerAdapter(mode=str(cfg["phase2"]["broker_mode"]))
    risk_cfg = Canary32BRiskConfig(
        kill_switch=bool(cfg["risk"]["kill_switch"]),
        trade_enabled=bool(cfg["risk"]["trade_enabled"]),
        enabled_symbols=list(cfg["universe"]["symbols"]),
        max_concurrent_positions=int(cfg["risk"]["max_concurrent_positions"]),
        max_daily_trades=int(cfg["risk"]["max_daily_trades"]),
        max_position_notional_per_symbol=float(cfg["risk"]["max_position_notional_per_symbol"]),
        allow_entry_fallback_to_taker=bool(cfg["execution"]["entry"]["allow_fallback_to_taker"]),
        max_data_delay_seconds=int(cfg["risk"]["max_data_delay_seconds"]),
        require_atr=bool(cfg["risk"]["require_atr"]),
    )
    snapshot = adapter.load_recent_signals()
    recent_signals = [sig.to_dict() for sig in snapshot.signals]
    seen = set() if args.force_replay else set(state.seen_signal_ids)
    new_signals = [sig for sig in snapshot.signals if sig.signal_id not in seen]

    portfolio = portfolio_state_from_runtime(state.symbol_states, state.daily_trade_count, api_healthy=True)
    event_bus = JsonlEventBus(EVENTS_PATH)

    intentions: list[dict[str, Any]] = []
    orders: list[dict[str, Any]] = []
    rejections: list[dict[str, Any]] = []
    chains: list[dict[str, Any]] = []
    operator_packets: list[dict[str, Any]] = []
    events_appended = 0

    for signal in new_signals:
        trace_id = make_trace_id(signal.signal_id)
        event_bus.append(EventRecord(timestamp=utc_now_iso(), event_type=EventType.SIGNAL_RECEIVED, symbol=signal.symbol, side=signal.side.value, trace_id=trace_id, message="phase2 received signal", payload=signal.to_dict()))
        events_appended += 1

        signal_ts = datetime.strptime(signal.timestamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        age_seconds = max(0.0, (datetime.now(timezone.utc) - signal_ts).total_seconds())
        market_ctx = Canary32BMarketContext(
            atr_available=bool(signal.metadata.get("atr_ready", False)),
            data_delay_seconds=float(age_seconds),
            metadata={"variant": signal.metadata.get("variant")},
        )
        decision = evaluate_entry_risk(signal, trace_id=trace_id, config=risk_cfg, portfolio=portfolio, market=market_ctx)
        if not decision.accepted:
            payload = {**signal.to_dict(), "risk": decision.to_dict()}
            rejections.append(payload)
            event_bus.append(EventRecord(timestamp=utc_now_iso(), event_type=EventType.RISK_REJECTED, symbol=signal.symbol, side=signal.side.value, trace_id=trace_id, message=decision.reason, payload=payload, level="WARN"))
            events_appended += 1
            state.seen_signal_ids.append(signal.signal_id)
            continue

        target_price = float(signal.signal_price) * (1.0 - float(cfg["execution"]["entry"]["maker_offset_bps"]) / 10000.0) if signal.side.value == "long" else float(signal.signal_price) * (1.0 + float(cfg["execution"]["entry"]["maker_offset_bps"]) / 10000.0)
        intention_id = f"intent-{hashlib.sha1((signal.signal_id + '|entry').encode('utf-8')).hexdigest()[:14]}"
        intention = build_entry_intention(
            signal,
            intention_id=intention_id,
            trace_id=trace_id,
            qty=float(cfg["execution"]["entry"]["qty"]),
            target_price=float(target_price),
            ttl_minutes=int(cfg["execution"]["entry"]["ttl_minutes"]),
            fallback_to_taker=bool(cfg["execution"]["entry"]["allow_fallback_to_taker"]),
            config_version=config_hash(cfg),
        )
        intention_payload = intention.to_dict() | {"phase": 2, "capital_deployed": False}
        intentions.append(intention_payload)
        event_bus.append(EventRecord(timestamp=utc_now_iso(), event_type=EventType.INTENTION_CREATED, symbol=signal.symbol, side=signal.side.value, trace_id=trace_id, message="phase2 entry intention created", payload=intention_payload))
        events_appended += 1

        order: BrokerOrderRecord = broker.place_entry_order(intention)
        order_payload = order.to_dict()
        orders.append(order_payload)
        event_bus.append(EventRecord(timestamp=utc_now_iso(), event_type=EventType.ORDER_PLACED, symbol=signal.symbol, side=signal.side.value, trace_id=trace_id, message="test/no-fill order submitted", payload=order_payload))
        event_bus.append(EventRecord(timestamp=utc_now_iso(), event_type=EventType.ORDER_ACK, symbol=signal.symbol, side=signal.side.value, trace_id=trace_id, message="broker ack received", payload=order_payload))
        events_appended += 2

        queried = broker.query_order(order)
        query_payload = queried.to_dict() | {"query_stage": "post_ack_sync"}
        event_bus.append(EventRecord(timestamp=utc_now_iso(), event_type=EventType.ORDER_STATUS_SYNC, symbol=signal.symbol, side=signal.side.value, trace_id=trace_id, message="queried order status after ack", payload=query_payload))
        events_appended += 1

        cancelled = broker.cancel_order(queried)
        cancel_payload = cancelled.to_dict() | {"cancel_reason": "phase2_test_no_fill_closeout"}
        event_bus.append(EventRecord(timestamp=utc_now_iso(), event_type=EventType.ORDER_CANCELLED, symbol=signal.symbol, side=signal.side.value, trace_id=trace_id, message="cancelled after ack to complete receipt chain", payload=cancel_payload))
        events_appended += 1

        final_status = broker.query_order(cancelled)
        final_payload = final_status.to_dict() | {"query_stage": "post_cancel_final"}
        event_bus.append(EventRecord(timestamp=utc_now_iso(), event_type=EventType.ORDER_STATUS_SYNC, symbol=signal.symbol, side=signal.side.value, trace_id=trace_id, message="queried final status after cancel", payload=final_payload))
        events_appended += 1

        receipt = ReceiptChainRecord(
            trace_id=trace_id,
            signal_id=signal.signal_id,
            intention_id=intention.intention_id,
            broker_order_id=final_status.broker_order_id,
            symbol=signal.symbol,
            stage="cancelled_no_fill",
            complete=True,
            capital_deployed=False,
            steps=["intent", "ack", "status_sync", "cancel", "final_status"],
            refs={
                "intention_id": intention.intention_id,
                "broker_order_id": final_status.broker_order_id,
                "venue_ref": final_status.venue_ref,
            },
            notes=[
                "Phase 2 is an isolated receipt-chain experiment.",
                "No capital deployed.",
                "This does not move the whole project back into paper trading.",
            ],
        )
        receipt_payload = receipt.to_dict()
        chains.append(receipt_payload)
        operator_packets.append(build_packet(signal.to_dict(), intention_payload, final_payload, receipt_payload))

        for row in state.symbol_states:
            if row.get("symbol") == signal.symbol:
                row["position_state"] = PositionState.FLAT.value
                row["active_signal_id"] = signal.signal_id
                row["active_intention_id"] = intention.intention_id
                row["last_event_time"] = utc_now_iso()
                break
        state.seen_signal_ids.append(signal.signal_id)

    state.last_run_utc = utc_now_iso()
    JsonStateStore(STATE_PATH).save(state.to_dict())
    save_json(STATUS_PATH, StrategyStatusSnapshot(
        alpha_name="rank32b_slope_floor_continuation",
        version="phase2_receipt_chain_v1",
        mode=str(cfg["phase2"]["broker_mode"]),
        enabled_symbols=list(cfg["universe"]["symbols"]),
        current_config_hash=config_hash(cfg),
        last_signal_time=snapshot.latest_signal_utc,
        system_health="ok",
        last_run_utc=state.last_run_utc,
        trade_enabled=bool(cfg["risk"]["trade_enabled"]),
        kill_switch=bool(cfg["risk"]["kill_switch"]),
        recent_signal_count=len(recent_signals),
        recent_intention_count=len(intentions),
        recent_reject_count=len(rejections),
        notes=[
            "Phase 2 = minimal isolated receipt-chain experiment.",
            "Default mode is test/no-fill with ack -> cancel -> final status.",
            "No capital deployed; no bot2/3/6/7 chain reuse.",
        ],
    ).to_dict())
    save_json(RUN_SUMMARY_PATH, {
        "generated_at_utc": utc_now_iso(),
        "config_hash": config_hash(cfg),
        "signals_seen_this_window": len(recent_signals),
        "new_signals_processed": len(new_signals),
        "intentions_created": len(intentions),
        "risk_rejections": len(rejections),
        "orders_placed": len(orders),
        "receipt_chains_completed": len(chains),
        "events_appended": events_appended,
        "mode": cfg["phase2"]["broker_mode"],
    })
    save_json(SIGNALS_PATH, recent_signals[-80:])
    save_json(INTENTIONS_PATH, intentions[-80:])
    save_json(ORDERS_PATH, orders[-80:])
    save_json(REJECTIONS_PATH, rejections[-80:])
    save_json(CHAINS_PATH, chains[-80:])
    save_json(SYMBOL_STATE_PATH, state.symbol_states)
    save_json(OPERATOR_PACKET_PATH, operator_packets[-20:])

    print({
        "generated_at_utc": utc_now_iso(),
        "signals_seen_this_window": len(recent_signals),
        "new_signals_processed": len(new_signals),
        "intentions_created": len(intentions),
        "risk_rejections": len(rejections),
        "orders_placed": len(orders),
        "receipt_chains_completed": len(chains),
        "events_appended": events_appended,
    })


if __name__ == "__main__":
    main()
