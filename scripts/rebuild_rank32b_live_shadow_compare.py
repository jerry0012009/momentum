#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_rank32b_global_live.py"
CONFIG_PATH = ROOT / "config" / "execution" / "rank32b_canary.yaml"
CLOSED_TRADES_PATH = ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_recent_closed_trades.json"
COMPARE_PATH = ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_vs_shadow.csv"
COMPARE_SUMMARY_PATH = ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_vs_shadow_summary.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    runner = load_module(RUNNER, "rank32b_global_live_compare_rebuild")
    cfg = runner.phase6lib.load_yaml(CONFIG_PATH)
    live_cfg = runner.load_global_live_cfg(cfg)
    closed = runner.phase6lib.load_json(CLOSED_TRADES_PATH, [])
    if not isinstance(closed, list):
        closed = []
    runner.write_compare_artifacts(live_cfg, closed)
    summary = runner.phase6lib.load_json(COMPARE_SUMMARY_PATH, {})
    print(
        json.dumps(
            {
                "status": summary.get("status"),
                "closed_trades": summary.get("closed_trades"),
                "compare_path": str(COMPARE_PATH.relative_to(ROOT)),
                "summary_path": str(COMPARE_SUMMARY_PATH.relative_to(ROOT)),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
