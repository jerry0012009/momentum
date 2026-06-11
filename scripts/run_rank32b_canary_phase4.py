#!/usr/bin/env python3
from __future__ import annotations

import argparse
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

from momentum.domain.canary32b_models import StrategyStatusSnapshot, utc_now_iso  # noqa: E402
from momentum.execution.canary32b.frmonitor_bridge import load_frmonitor_bridge  # noqa: E402

CONFIG_PATH = ROOT / "config" / "execution" / "rank32b_canary.yaml"
ART_DIR = ROOT / "reports" / "artifacts" / "rank32b_canary"
STATUS_PATH = ART_DIR / "phase4_status.json"
RUN_SUMMARY_PATH = ART_DIR / "phase4_last_run_summary.json"
RECEIPT_PATH = ART_DIR / "phase4_execution_receipt.json"
ACCOUNT_BEFORE_PATH = ART_DIR / "phase4_account_before.json"
ACCOUNT_AFTER_PATH = ART_DIR / "phase4_account_after.json"
OPERATOR_PACKET_PATH = ART_DIR / "phase4_operator_packet.json"


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


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Rank 32b canary Phase-4 minimal real order experiment.")
    parser.add_argument("--config", default=str(CONFIG_PATH))
    args = parser.parse_args()

    ensure_dir(ART_DIR)
    cfg = load_yaml(Path(args.config))
    phase3 = cfg["phase3"]
    phase4 = cfg["phase4"]

    bridge = load_frmonitor_bridge(
        phase3["fr_monitor_root"],
        local_private_path=phase3.get("local_private_path"),
    )

    before = bridge.get_binance_perp_account() if bool(phase4.get("query_account_before_after", True)) else None
    receipt = bridge.submit_binance_perp_test_order(
        symbol=str(phase4["symbol"]),
        side=str(phase4["side"]),
        quantity=phase4["quantity"],
        reduce_only=bool(phase4.get("reduce_only", False)),
        client_order_id=f"rank32b-p4-{datetime.now(timezone.utc).strftime('%H%M%S')}",
    )
    after = bridge.get_binance_perp_account() if bool(phase4.get("query_account_before_after", True)) else None

    receipt_out = {
        "generated_at_utc": utc_now_iso(),
        "venue": str(phase4["venue"]),
        "mode": "binance_test_order",
        "capital_deployed": False,
        "order_receipt": receipt,
        "account_before_summary": summarize_account(before),
        "account_after_summary": summarize_account(after),
    }
    operator_packet = {
        "candidate_id": "rank32b_canary",
        "phase": 4,
        "experiment_type": "minimal_real_order_path_no_fill",
        "venue": str(phase4["venue"]),
        "endpoint": receipt.get("endpoint"),
        "capital_deployed": False,
        "symbol": receipt.get("symbol"),
        "side": receipt.get("side"),
        "quantity": receipt.get("quantity"),
        "notes": [
            "Real private key signing path was used.",
            "Real Binance private endpoint was used.",
            "Endpoint is /fapi/v1/order/test, so no position or capital deployment occurs.",
        ],
    }
    status = StrategyStatusSnapshot(
        alpha_name="rank32b_slope_floor_continuation",
        version="phase4_test_order_v1",
        mode="binance_test_order",
        enabled_symbols=list(cfg["universe"]["symbols"]),
        current_config_hash="phase4_test_order",
        last_signal_time=None,
        system_health="ok",
        last_run_utc=utc_now_iso(),
        trade_enabled=bool(cfg["risk"]["trade_enabled"]),
        kill_switch=bool(cfg["risk"]["kill_switch"]),
        recent_signal_count=0,
        recent_intention_count=0,
        recent_reject_count=0,
        notes=[
            "Phase 4 uses a real signed Binance test order.",
            "No capital deployed; this is the smallest real order-path experiment.",
            "Lighter remains query-only in this phase.",
        ],
    )

    save_json(ACCOUNT_BEFORE_PATH, before or {})
    save_json(ACCOUNT_AFTER_PATH, after or {})
    save_json(RECEIPT_PATH, receipt_out)
    save_json(OPERATOR_PACKET_PATH, operator_packet)
    save_json(STATUS_PATH, status.to_dict())
    save_json(RUN_SUMMARY_PATH, {
        "generated_at_utc": utc_now_iso(),
        "venue": str(phase4["venue"]),
        "mode": "binance_test_order",
        "capital_deployed": False,
        "http_status": receipt.get("http_status"),
        "symbol": receipt.get("symbol"),
        "side": receipt.get("side"),
        "quantity": receipt.get("quantity"),
    })

    print({
        "generated_at_utc": utc_now_iso(),
        "venue": str(phase4["venue"]),
        "mode": "binance_test_order",
        "capital_deployed": False,
        "http_status": receipt.get("http_status"),
        "symbol": receipt.get("symbol"),
        "side": receipt.get("side"),
        "quantity": receipt.get("quantity"),
    })


if __name__ == "__main__":
    main()
