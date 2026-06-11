#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.domain.canary32b_models import StrategyStatusSnapshot, utc_now_iso  # noqa: E402
from momentum.execution.canary32b.frmonitor_bridge import load_frmonitor_bridge  # noqa: E402
from momentum.execution.canary32b.ledger import build_phase3_order_ledger  # noqa: E402

CONFIG_PATH = ROOT / "config" / "execution" / "rank32b_canary.yaml"
ART_DIR = ROOT / "reports" / "artifacts" / "rank32b_canary"
STATUS_PATH = ART_DIR / "phase3_status.json"
RUN_SUMMARY_PATH = ART_DIR / "phase3_last_run_summary.json"
VENUE_HEALTH_PATH = ART_DIR / "phase3_venue_health.json"
ACCOUNT_SNAPSHOT_PATH = ART_DIR / "phase3_account_snapshot.json"
LEDGER_PATH = ART_DIR / "phase3_order_ledger.json"
OPERATOR_PACKET_PATH = ART_DIR / "phase3_operator_packet.json"

PH2_ORDERS_PATH = ART_DIR / "phase2_recent_orders.json"
PH2_INTENTIONS_PATH = ART_DIR / "phase2_recent_intentions.json"
PH2_CHAINS_PATH = ART_DIR / "phase2_receipt_chains.json"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_json(path: Path, default: Any):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _ok(name: str, payload: Any) -> dict[str, Any]:
    return {"name": name, "ok": True, "payload": payload}


def _fail(name: str, exc: Exception) -> dict[str, Any]:
    return {"name": name, "ok": False, "error": str(exc)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Rank 32b canary Phase-3 venue query + ledger sync.")
    parser.add_argument("--config", default=str(CONFIG_PATH))
    args = parser.parse_args()

    ensure_dir(ART_DIR)
    cfg = load_yaml(Path(args.config))
    phase3 = cfg["phase3"]

    if bool(phase3.get("lighter", {}).get("disable_proxy_for_query", False)):
        os.environ["LIGHTER_PROXY_ENABLED"] = "0"
        os.environ["LIGHTER_PROXY_URL"] = ""

    bridge = load_frmonitor_bridge(
        phase3["fr_monitor_root"],
        local_private_path=phase3.get("local_private_path"),
    )

    venue_health: list[dict[str, Any]] = []
    account_snapshot: dict[str, Any] = {"generated_at_utc": utc_now_iso(), "query_only": bool(phase3.get("query_only", True)), "venues": {}}

    if bool(phase3["venues"].get("binance", False)):
        try:
            account = bridge.get_binance_perp_account()
            positions = bridge.get_binance_perp_positions()
            balance = bridge.get_binance_perp_usdt_balance()
            venue_health.append(_ok("binance.private_query", {"account": True, "positions": True, "balance": True}))
            account_snapshot["venues"]["binance"] = {
                "account_keys": list(account.keys())[:20] if isinstance(account, dict) else [],
                "position_count": len(positions) if isinstance(positions, list) else None,
                "usdt_balance": balance,
            }
        except Exception as exc:
            venue_health.append(_fail("binance.private_query", exc))
            account_snapshot["venues"]["binance"] = {"error": str(exc)}

    if bool(phase3["venues"].get("lighter", False)):
        try:
            balance_summary = bridge.get_lighter_balance_summary()
            funding_map = bridge.get_lighter_funding_rates_map()
            venue_health.append(_ok("lighter.private_query", {"balance": True, "funding": True}))
            raw_account = balance_summary.get("raw_account") if isinstance(balance_summary, dict) else None
            positions = raw_account.get("positions") if isinstance(raw_account, dict) else None
            account_snapshot["venues"]["lighter"] = {
                "position_count": len(positions) if isinstance(positions, list) else None,
                "funding_symbol_count": len(funding_map) if isinstance(funding_map, dict) else None,
            }
        except Exception as exc:
            venue_health.append(_fail("lighter.private_query", exc))
            account_snapshot["venues"]["lighter"] = {"error": str(exc)}

    phase2_orders = load_json(PH2_ORDERS_PATH, [])
    phase2_intentions = load_json(PH2_INTENTIONS_PATH, [])
    phase2_chains = load_json(PH2_CHAINS_PATH, [])
    ledger_rows = build_phase3_order_ledger(
        phase2_orders,
        phase2_intentions,
        phase2_chains,
        now_utc=utc_now_iso(),
        default_ttl_minutes=int(phase3["ttl_scan"]["default_entry_ttl_minutes"]),
    )

    operator_packet = {
        "candidate_id": "rank32b_canary",
        "phase": 3,
        "query_only": bool(phase3.get("query_only", True)),
        "fr_monitor_root": str(phase3["fr_monitor_root"]),
        "local_private_path": str(phase3.get("local_private_path")),
        "venue_health": venue_health,
        "ledger_summary": {
            "rows": len(ledger_rows),
            "finalized_rows": sum(1 for r in ledger_rows if r.get("ttl_state") == "finalized"),
            "live_rows": sum(1 for r in ledger_rows if r.get("ttl_state") == "live"),
            "expired_rows": sum(1 for r in ledger_rows if r.get("ttl_state") == "expired"),
        },
        "notes": [
            "Phase 3 uses real private query surfaces via FR_Monitor bridge.",
            "No order placement in this phase.",
            "This prepares the ground for one isolated minimal live-order experiment in the next phase.",
        ],
    }

    status = StrategyStatusSnapshot(
        alpha_name="rank32b_slope_floor_continuation",
        version="phase3_query_ledger_v1",
        mode="query_only",
        enabled_symbols=list(cfg["universe"]["symbols"]),
        current_config_hash="phase3_query_only",
        last_signal_time=None,
        system_health="ok" if all(x.get("ok") for x in venue_health) else "degraded",
        last_run_utc=utc_now_iso(),
        trade_enabled=bool(cfg["risk"]["trade_enabled"]),
        kill_switch=bool(cfg["risk"]["kill_switch"]),
        recent_signal_count=0,
        recent_intention_count=len(phase2_intentions),
        recent_reject_count=0,
        notes=[
            "Phase 3 = real venue private query + local order ledger + TTL scan.",
            "No capital deployed in this phase.",
            "Local secrets are expected under config/private/ and ignored by git.",
        ],
    )

    save_json(VENUE_HEALTH_PATH, venue_health)
    save_json(ACCOUNT_SNAPSHOT_PATH, account_snapshot)
    save_json(LEDGER_PATH, ledger_rows)
    save_json(OPERATOR_PACKET_PATH, operator_packet)
    save_json(STATUS_PATH, status.to_dict())
    save_json(RUN_SUMMARY_PATH, {
        "generated_at_utc": utc_now_iso(),
        "venue_checks": len(venue_health),
        "venue_ok_count": sum(1 for x in venue_health if x.get("ok")),
        "ledger_rows": len(ledger_rows),
        "query_only": bool(phase3.get("query_only", True)),
    })

    print({
        "generated_at_utc": utc_now_iso(),
        "venue_checks": len(venue_health),
        "venue_ok_count": sum(1 for x in venue_health if x.get("ok")),
        "ledger_rows": len(ledger_rows),
        "query_only": bool(phase3.get("query_only", True)),
    })


if __name__ == "__main__":
    main()
