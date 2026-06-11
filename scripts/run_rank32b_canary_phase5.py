#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.domain.canary32b_models import StrategyStatusSnapshot, utc_now_iso  # noqa: E402
from momentum.execution.canary32b.frmonitor_bridge import load_frmonitor_bridge  # noqa: E402

CONFIG_PATH = ROOT / "config" / "execution" / "rank32b_canary.yaml"
ART_DIR = ROOT / "reports" / "artifacts" / "rank32b_canary"
STATUS_PATH = ART_DIR / "phase5_status.json"
RUN_SUMMARY_PATH = ART_DIR / "phase5_last_run_summary.json"
RECEIPT_PATH = ART_DIR / "phase5_execution_receipt.json"
ACCOUNT_BEFORE_PATH = ART_DIR / "phase5_account_before.json"
ACCOUNT_AFTER_PATH = ART_DIR / "phase5_account_after.json"
OPERATOR_PACKET_PATH = ART_DIR / "phase5_operator_packet.json"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def summarize_account(snapshot: Any) -> dict[str, Any]:
    if not isinstance(snapshot, dict):
        return {"type": str(type(snapshot))}
    keys = list(snapshot.keys())[:20]
    total_wallet = snapshot.get("totalWalletBalance")
    total_margin = snapshot.get("totalMarginBalance")
    assets = snapshot.get("assets")
    positions = snapshot.get("positions")
    return {
        "top_level_keys": keys,
        "totalWalletBalance": total_wallet,
        "totalMarginBalance": total_margin,
        "asset_count": len(assets) if isinstance(assets, list) else None,
        "position_count": len(positions) if isinstance(positions, list) else None,
    }


def _query_order_with_retry(
    bridge,
    *,
    symbol: str,
    order_id: Any,
    client_order_id: str | None,
    attempts: int = 3,
    sleep_seconds: float = 0.6,
) -> dict[str, Any]:
    last_err: Exception | None = None
    for i in range(max(1, int(attempts))):
        try:
            payload = bridge.get_binance_perp_order(symbol, order_id=order_id, client_order_id=client_order_id)
            if isinstance(payload, dict):
                return payload
            return {"raw": payload}
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            if i < attempts - 1:
                time.sleep(max(0.0, float(sleep_seconds)))
    raise RuntimeError(f"query order failed after retries: {last_err}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Rank 32b canary Phase-5 minimal live order gate.")
    parser.add_argument("--config", default=str(CONFIG_PATH))
    args = parser.parse_args()

    ensure_dir(ART_DIR)
    cfg = load_yaml(Path(args.config))
    phase3 = cfg["phase3"]
    phase5 = cfg["phase5"]

    bridge = load_frmonitor_bridge(
        phase3["fr_monitor_root"],
        local_private_path=phase3.get("local_private_path"),
    )

    symbol = str(phase5["symbol"])
    side = str(phase5["side"]).upper()
    rules = bridge.get_binance_perp_trade_rules(symbol)
    last_price = bridge.get_binance_perp_last_price(symbol)
    sizing_floor = bridge.estimate_binance_min_trade_floor(symbol, last_price=last_price, rules=rules)
    floor_notional = float(sizing_floor["effective_min_notional"])
    buffer_mult = max(1.0, float(phase5.get("min_notional_buffer_mult", 1.0)))
    target_notional = max(float(phase5["desired_notional_usdt"]), floor_notional * buffer_mult)
    qty_info = bridge.derive_binance_qty_from_notional(symbol, target_notional, last_price=last_price, rules=rules)
    quantity = float(qty_info["quantity"])
    chosen_notional = quantity * float(last_price)

    offset_bps = float(phase5["limit_offset_bps"])
    if side == "BUY":
        limit_price = float(last_price) * (1.0 - offset_bps / 10000.0)
    else:
        limit_price = float(last_price) * (1.0 + offset_bps / 10000.0)

    before = bridge.get_binance_perp_account() if bool(phase5.get("query_account_before_after", True)) else None
    client_order_id = f"rank32b-p5-{datetime.now(timezone.utc).strftime('%H%M%S')}"
    time_in_force = str(phase5.get("time_in_force", "GTX")).upper()
    placed = bridge.place_binance_perp_live_limit_order(
        symbol=symbol,
        side=side,
        quantity=quantity,
        price=limit_price,
        reduce_only=None,
        client_order_id=client_order_id,
        time_in_force=time_in_force,
    )

    order_snapshot = _query_order_with_retry(
        bridge,
        symbol=symbol,
        order_id=placed.get("order_id"),
        client_order_id=placed.get("client_order_id") or client_order_id,
        attempts=int(phase5.get("query_retry_attempts", 3)),
        sleep_seconds=float(phase5.get("query_retry_sleep_seconds", 0.6)),
    )

    cancel_result = None
    cancel_error = None
    if bool(phase5.get("cancel_immediately_after_ack", True)):
        try:
            cancel_result = bridge.cancel_binance_perp_order(
                symbol=symbol,
                order_id=placed.get("order_id"),
                client_order_id=placed.get("client_order_id") or client_order_id,
            )
        except Exception as exc:  # noqa: BLE001
            cancel_error = str(exc)

    final_status = _query_order_with_retry(
        bridge,
        symbol=symbol,
        order_id=placed.get("order_id"),
        client_order_id=placed.get("client_order_id") or client_order_id,
        attempts=int(phase5.get("query_retry_attempts", 3)),
        sleep_seconds=float(phase5.get("query_retry_sleep_seconds", 0.6)),
    )
    after = bridge.get_binance_perp_account() if bool(phase5.get("query_account_before_after", True)) else None

    receipt = {
        "generated_at_utc": utc_now_iso(),
        "venue": "binance",
        "mode": "live_limit_then_cancel",
        "capital_deployed_target": "minimal_live_order",
        "symbol": symbol,
        "side": side,
        "last_price": last_price,
        "limit_offset_bps": offset_bps,
        "limit_price_requested": limit_price,
        "rules": rules,
        "sizing_floor": sizing_floor,
        "buffer_mult": buffer_mult,
        "target_notional_usdt": target_notional,
        "chosen_notional_usdt": chosen_notional,
        "quantity_info": qty_info,
        "place_ack": placed,
        "order_snapshot_after_place": order_snapshot,
        "cancel_result": cancel_result,
        "cancel_error": cancel_error,
        "final_status": final_status,
        "time_in_force": time_in_force,
        "account_before_summary": summarize_account(before),
        "account_after_summary": summarize_account(after),
    }
    operator_packet = {
        "candidate_id": "rank32b_canary",
        "phase": 5,
        "experiment_type": "minimal_live_limit_then_cancel",
        "venue": "binance",
        "capital_deployed_target": "minimal_live_order",
        "symbol": symbol,
        "side": side,
        "target_notional_usdt": target_notional,
        "chosen_notional_usdt": chosen_notional,
        "sizing_floor": sizing_floor,
        "buffer_mult": buffer_mult,
        "limit_offset_bps": offset_bps,
        "time_in_force": time_in_force,
        "client_order_id": client_order_id,
        "notes": [
            "This is a real live order, not a test order.",
            "Quantity is automatically adjusted to pass Binance min quantity / min notional filters.",
            "Default is post-only GTX; runner can cancel immediately after ack.",
        ],
    }
    status = StrategyStatusSnapshot(
        alpha_name="rank32b_slope_floor_continuation",
        version="phase5_live_gate_v2",
        mode="live_limit_then_cancel",
        enabled_symbols=list(cfg["universe"]["symbols"]),
        current_config_hash="phase5_live_gate_v2",
        last_signal_time=None,
        system_health="ok" if cancel_error is None else "degraded",
        last_run_utc=utc_now_iso(),
        trade_enabled=bool(cfg["risk"]["trade_enabled"]),
        kill_switch=bool(cfg["risk"]["kill_switch"]),
        recent_signal_count=0,
        recent_intention_count=0,
        recent_reject_count=0,
        notes=[
            "Phase 5 places one real live LIMIT order and supports configurable timeInForce (default GTX).",
            "Order query has retry logic to reduce immediate-ack race failures.",
            "This phase remains isolated and non-recurring.",
        ],
    )

    save_json(ACCOUNT_BEFORE_PATH, before or {})
    save_json(ACCOUNT_AFTER_PATH, after or {})
    save_json(RECEIPT_PATH, receipt)
    save_json(OPERATOR_PACKET_PATH, operator_packet)
    save_json(STATUS_PATH, status.to_dict())
    save_json(
        RUN_SUMMARY_PATH,
        {
            "generated_at_utc": utc_now_iso(),
            "venue": "binance",
            "mode": "live_limit_then_cancel",
            "symbol": symbol,
            "side": side,
            "target_notional_usdt": target_notional,
            "chosen_notional_usdt": chosen_notional,
            "sizing_floor": sizing_floor,
            "buffer_mult": buffer_mult,
            "limit_offset_bps": offset_bps,
            "time_in_force": time_in_force,
            "place_http_status": placed.get("http_status"),
            "final_status": final_status.get("status") if isinstance(final_status, dict) else None,
            "client_order_id": client_order_id,
            "cancel_error": cancel_error,
        },
    )

    print(
        {
            "generated_at_utc": utc_now_iso(),
            "venue": "binance",
            "mode": "live_limit_then_cancel",
            "symbol": symbol,
            "side": side,
            "target_notional_usdt": target_notional,
            "chosen_notional_usdt": chosen_notional,
            "time_in_force": time_in_force,
            "place_http_status": placed.get("http_status"),
            "final_status": final_status.get("status") if isinstance(final_status, dict) else None,
            "client_order_id": client_order_id,
            "cancel_error": cancel_error,
        }
    )


if __name__ == "__main__":
    main()
