#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from momentum.strategies.rank32c_btc_utc_weak_cell import build_order_plan, load_cached_bars, to_iso


RAW_15M_DIR = (
    ROOT
    / "reports"
    / "artifacts"
    / "paper_rank213_largecap_xs_jump_veto"
    / "rank213_local_cache"
    / "monthly_marketcap_universe"
    / "raw_15m"
)
ART_DIR = ROOT / "reports" / "artifacts" / "rank32c_pre_live_gate"


def read_simple_config(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        out[key.strip()] = value.strip().strip('"')
    return out


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    now = pd.Timestamp.now(tz="UTC")
    config_path = (ROOT / args.config).resolve() if not Path(args.config).is_absolute() else Path(args.config)
    config = read_simple_config(config_path)
    allow_live_orders = config.get("allow_live_orders", "false").lower() == "true"

    bars = load_cached_bars(RAW_15M_DIR)
    order_plan = build_order_plan(bars, now)
    runtime_status = {
        "generated_at_utc": to_iso(now),
        "config_path": str(config_path.relative_to(ROOT)),
        "allow_live_orders_config": allow_live_orders,
        "allow_open_plan": bool(order_plan.get("allow_open")),
        "blocked_by": order_plan.get("blocked_by", []),
        "decision_blocker": order_plan.get("decision_blocker"),
        "order_plan_runtime_path": str((ART_DIR / "order_plan_runtime.json").relative_to(ROOT)),
    }
    write_json(ART_DIR / "order_plan_runtime.json", order_plan)
    write_json(ART_DIR / "runner_status.json", runtime_status)

    if not allow_live_orders:
        print(json.dumps({"status": "blocked", "reason": "allow_live_orders_false"}, ensure_ascii=False))
        return 2
    if not order_plan.get("allow_open"):
        print(json.dumps({"status": "blocked", "reason": "order_plan_not_openable", "blocked_by": order_plan.get("blocked_by", [])}, ensure_ascii=False))
        return 2

    print(json.dumps({"status": "ready_for_broker_adapter", "order_plan": order_plan}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
