#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.domain.canary32b_models import (  # noqa: E402
    EventRecord,
    EventType,
    PositionState,
    StrategyStatusSnapshot,
    SymbolRuntimeState,
    utc_now_iso,
)
from momentum.execution.canary32b.event_bus import JsonlEventBus  # noqa: E402
from momentum.execution.canary32b.intention_layer import build_entry_intention  # noqa: E402
from momentum.execution.canary32b.signal_adapter import Rank32BPerpSignalAdapter  # noqa: E402
from momentum.risk.canary32b_guard import (  # noqa: E402
    Canary32BMarketContext,
    Canary32BRiskConfig,
    evaluate_entry_risk,
    portfolio_state_from_runtime,
)

CONFIG_PATH = ROOT / "config" / "execution" / "rank32b_canary.yaml"
ART_DIR = ROOT / "reports" / "artifacts" / "rank32b_canary"
EVENTS_PATH = ART_DIR / "phase1_events.jsonl"
STATE_PATH = ART_DIR / "phase1_state.json"
STATUS_PATH = ART_DIR / "phase1_status.json"
SIGNALS_PATH = ART_DIR / "phase1_recent_signals.json"
INTENTIONS_PATH = ART_DIR / "phase1_recent_intentions.json"
REJECTIONS_PATH = ART_DIR / "phase1_recent_rejections.json"
RUN_SUMMARY_PATH = ART_DIR / "phase1_last_run_summary.json"
SYMBOL_STATE_PATH = ART_DIR / "phase1_symbol_state.json"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


class CanaryState:
    def __init__(self, raw: dict[str, Any] | None = None) -> None:
        raw = raw or {}
        self.raw = raw
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


def load_state(path: Path) -> CanaryState:
    if not path.exists():
        return CanaryState()
    return CanaryState(json.loads(path.read_text(encoding="utf-8")))


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def config_hash(cfg: dict[str, Any]) -> str:
    normalized = json.dumps(cfg, ensure_ascii=False, sort_keys=True)
    return hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:16]


def build_default_symbol_state(symbols: list[str]) -> list[dict[str, Any]]:
    return [
        SymbolRuntimeState(symbol=symbol, position_state=PositionState.FLAT, active_signal_id=None, active_intention_id=None, last_event_time=None).to_dict()
        for symbol in symbols
    ]


def make_trace_id(signal_id: str) -> str:
    return f"trace-{hashlib.sha1(signal_id.encode('utf-8')).hexdigest()[:12]}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Rank 32b canary Phase-1 skeleton.")
    parser.add_argument("--config", default=str(CONFIG_PATH))
    parser.add_argument("--force-replay", action="store_true", help="Ignore seen_signal_ids and replay recent signals.")
    args = parser.parse_args()

    ensure_dir(ART_DIR)
    cfg = load_yaml(Path(args.config))
    state = load_state(STATE_PATH)
    if not state.symbol_states:
        state.symbol_states = build_default_symbol_state(cfg["universe"]["symbols"])

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
    snapshot = adapter.load_recent_signals()
    recent_signals = [sig.to_dict() for sig in snapshot.signals]
    seen = set() if args.force_replay else set(state.seen_signal_ids)
    new_signals = [sig for sig in snapshot.signals if sig.signal_id not in seen]

    event_bus = JsonlEventBus(EVENTS_PATH)
    intentions: list[dict[str, Any]] = []
    rejections: list[dict[str, Any]] = []
    event_count = 0

    portfolio = portfolio_state_from_runtime(state.symbol_states, state.daily_trade_count, api_healthy=True)
    now_utc = utc_now_iso()
    for signal in new_signals:
        trace_id = make_trace_id(signal.signal_id)
        event_bus.append(
            EventRecord(
                timestamp=now_utc,
                event_type=EventType.SIGNAL_RECEIVED,
                symbol=signal.symbol,
                side=signal.side.value,
                trace_id=trace_id,
                message="signal normalized into canary envelope",
                payload=signal.to_dict(),
            )
        )
        event_count += 1

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
            event_bus.append(
                EventRecord(
                    timestamp=utc_now_iso(),
                    event_type=EventType.RISK_REJECTED,
                    symbol=signal.symbol,
                    side=signal.side.value,
                    trace_id=trace_id,
                    message=decision.reason,
                    payload=payload,
                    level="WARN",
                )
            )
            event_count += 1
            state.seen_signal_ids.append(signal.signal_id)
            continue

        intended_entry_price = float(signal.signal_price) * (1.0 - float(cfg["execution"]["entry"]["maker_offset_bps"]) / 10000.0) if signal.side.value == "long" else float(signal.signal_price) * (1.0 + float(cfg["execution"]["entry"]["maker_offset_bps"]) / 10000.0)
        intention_id = f"intent-{hashlib.sha1((signal.signal_id + '|entry').encode('utf-8')).hexdigest()[:14]}"
        intention = build_entry_intention(
            signal,
            intention_id=intention_id,
            trace_id=trace_id,
            qty=float(cfg["execution"]["entry"]["qty"]),
            target_price=float(intended_entry_price),
            ttl_minutes=int(cfg["execution"]["entry"]["ttl_minutes"]),
            fallback_to_taker=bool(cfg["execution"]["entry"]["allow_fallback_to_taker"]),
            config_version=config_hash(cfg),
        )
        payload = intention.to_dict()
        payload["dry_run_only"] = True
        intentions.append(payload)
        event_bus.append(
            EventRecord(
                timestamp=utc_now_iso(),
                event_type=EventType.INTENTION_CREATED,
                symbol=signal.symbol,
                side=signal.side.value,
                trace_id=trace_id,
                message="phase1 created entry intention (no order submission yet)",
                payload=payload,
            )
        )
        event_count += 1
        event_bus.append(
            EventRecord(
                timestamp=utc_now_iso(),
                event_type=EventType.WARNING_RAISED,
                symbol=signal.symbol,
                side=signal.side.value,
                trace_id=trace_id,
                message="phase1 is dry-run only; no broker actions are sent",
                payload={"mode": cfg["run_mode"]},
                level="WARN",
            )
        )
        event_count += 1
        state.seen_signal_ids.append(signal.signal_id)

    state.last_run_utc = utc_now_iso()
    save_json(STATE_PATH, state.to_dict())
    save_json(SIGNALS_PATH, recent_signals[-80:])
    save_json(INTENTIONS_PATH, intentions[-80:])
    save_json(REJECTIONS_PATH, rejections[-80:])
    save_json(SYMBOL_STATE_PATH, state.symbol_states)

    status = StrategyStatusSnapshot(
        alpha_name="rank32b_slope_floor_continuation",
        version="phase1_skeleton_v1",
        mode=str(cfg["run_mode"]),
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
            "Phase 1 = signal -> risk -> intention -> event log -> dashboard JSON.",
            "Paper/manual is only for minimal order-routing experiments, not a project-wide rollback to paper trading.",
            "No broker actions are emitted in this phase.",
        ],
    )
    save_json(STATUS_PATH, status.to_dict())
    save_json(
        RUN_SUMMARY_PATH,
        {
            "generated_at_utc": utc_now_iso(),
            "config_hash": config_hash(cfg),
            "signals_seen_this_window": len(recent_signals),
            "new_signals_processed": len(new_signals),
            "intentions_created": len(intentions),
            "risk_rejections": len(rejections),
            "events_appended": event_count,
            "mode": cfg["run_mode"],
        },
    )

    print(
        {
            "generated_at_utc": utc_now_iso(),
            "signals_seen_this_window": len(recent_signals),
            "new_signals_processed": len(new_signals),
            "intentions_created": len(intentions),
            "risk_rejections": len(rejections),
            "events_appended": event_count,
        }
    )


if __name__ == "__main__":
    main()
