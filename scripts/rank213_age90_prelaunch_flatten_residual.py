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

from momentum.execution.canary32b.frmonitor_bridge import load_frmonitor_bridge  # noqa: E402

CONFIG_PATH = ROOT / "config" / "execution" / "rank213_age90_live_canary.yaml"
OLD_STATUS_PATH = ROOT / "reports" / "artifacts" / "rank213_live_canary_shell" / "live_status.json"
PLAN_PATH = ROOT / "reports" / "artifacts" / "rank213_age90_live_canary" / "prelaunch_flatten_plan.json"


def iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def residual_rows(status: dict[str, Any]) -> list[dict[str, Any]]:
    rows = status.get("exchange_open_positions", [])
    if not isinstance(rows, list):
        return []
    out: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        if str(row.get("reconciliation_classification") or "") != "residual_open_on_exchange":
            continue
        if not bool(row.get("rank213_owned", False)):
            continue
        symbol = str(row.get("symbol") or "").upper().strip()
        side = str(row.get("side") or "").lower().strip()
        qty = abs(float(row.get("qty") or row.get("exchange_qty_abs") or 0.0))
        if not symbol or side not in {"long", "short"} or qty <= 0:
            continue
        out.append({
            **row,
            "symbol": symbol,
            "side": side,
            "qty": qty,
            "exit_order_side": "SELL" if side == "long" else "BUY",
            "position_side": "LONG" if side == "long" else "SHORT",
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Prepare or execute prelaunch flatten for old rank213 residual positions.")
    ap.add_argument("--status-path", default=str(OLD_STATUS_PATH))
    ap.add_argument("--plan-path", default=str(PLAN_PATH))
    ap.add_argument("--config", default=str(CONFIG_PATH))
    ap.add_argument("--allow-live", action="store_true", help="Actually submit reduce-only market orders.")
    ap.add_argument("--confirm-symbol", action="append", default=[], help="Required once per symbol when --allow-live is used.")
    args = ap.parse_args()

    status_path = Path(args.status_path)
    cfg = load_yaml(Path(args.config))
    status = read_json(status_path, {})
    rows = residual_rows(status if isinstance(status, dict) else {})
    confirmed = {str(x).upper().strip() for x in args.confirm_symbol if str(x).strip()}
    missing_confirm = sorted({row["symbol"] for row in rows} - confirmed)

    plan: dict[str, Any] = {
        "generated_at_utc": iso_now(),
        "mode": "execute" if args.allow_live else "dry_run_plan_only",
        "source_status_path": str(status_path),
        "residual_count": len(rows),
        "residual_symbols": [row["symbol"] for row in rows],
        "blocked_until_flat": bool(rows),
        "requires_live_confirmation": bool(rows),
        "missing_confirm_symbols": missing_confirm if args.allow_live else [row["symbol"] for row in rows],
        "orders": [],
        "source_rows": rows,
    }

    if args.allow_live:
        if not rows:
            plan["execution_status"] = "nothing_to_flatten"
        elif missing_confirm:
            plan["execution_status"] = "refused_missing_confirm_symbol"
        else:
            phase3 = cfg.get("phase3", {}) if isinstance(cfg.get("phase3"), dict) else {}
            bridge = load_frmonitor_bridge(
                phase3.get("fr_monitor_root", "/root/jerry/wlfi/FR_Monitor"),
                local_private_path=phase3.get("local_private_path"),
            )
            submitted = []
            for row in rows:
                cid = f"r213age90-flat-{row['symbol'].lower()[:8]}-{datetime.now(timezone.utc).strftime('%H%M%S')}"
                result = bridge.place_binance_perp_live_market_order(
                    symbol=row["symbol"],
                    side=row["exit_order_side"],
                    quantity=row["qty"],
                    reduce_only=True,
                    position_side=row["position_side"],
                    client_order_id=cid[:36],
                )
                submitted.append({
                    "symbol": row["symbol"],
                    "source_side": row["side"],
                    "qty": row["qty"],
                    "order_side": row["exit_order_side"],
                    "position_side": row["position_side"],
                    "client_order_id": cid[:36],
                    "result": result,
                })
            plan["orders"] = submitted
            plan["execution_status"] = "submitted"
    else:
        plan["execution_status"] = "plan_written_no_live_orders"

    save_json(Path(args.plan_path), plan)
    print(f"wrote {args.plan_path}")
    print(json.dumps({k: plan[k] for k in ["mode", "residual_count", "residual_symbols", "execution_status", "missing_confirm_symbols"]}, ensure_ascii=False, indent=2))
    return 0 if plan.get("execution_status") not in {"refused_missing_confirm_symbol"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
