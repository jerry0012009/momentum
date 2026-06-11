#!/usr/bin/env python3
"""Scheduler wrapper for Rank 154 honest daily paper runner.

This keeps the existing unit/script anchor but upgrades the behavior:
- if no state exists yet, initialize from the latest completed daily bar;
- otherwise refresh once and process any newly completed daily bar(s);
- publish the site index after a successful tick.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank154_crypto_stat_arb_runner"
STATE_PATH = ART_DIR / "rank154_paper_state.json"
LAST_RUN_PATH = ART_DIR / "rank154_sidecar_refresh_last_run.json"
DEFAULT_TIMER_UNIT = "momentum-rank154-paper-sidecar-refresh.timer"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run(cmd: list[str], *, cwd: Path) -> dict:
    started = utc_now_iso()
    p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    return {
        "cmd": cmd,
        "started_at_utc": started,
        "finished_at_utc": utc_now_iso(),
        "returncode": int(p.returncode),
        "stdout": (p.stdout or "").strip()[-12000:],
        "stderr": (p.stderr or "").strip()[-12000:],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Autonomous daily paper tick for Rank 154 / Crypto-Stat-Arb.")
    parser.add_argument("--skip-publish", action="store_true", help="Skip publishing homepage/site index.")
    parser.add_argument("--timer-unit", default=DEFAULT_TIMER_UNIT, help="Systemd timer unit owning this sidecar refresh.")
    args = parser.parse_args()

    ART_DIR.mkdir(parents=True, exist_ok=True)

    mode = "--refresh" if STATE_PATH.exists() else "--init-from-now"
    report: dict = {
        "run_at_utc": utc_now_iso(),
        "ok": False,
        "mode": mode,
        "steps": [],
        "timer_unit": args.timer_unit,
    }

    try:
        report["steps"].append(
            run(
                [
                    sys.executable,
                    "scripts/run_rank154_crypto_stat_arb_paper_runner.py",
                    mode,
                    "--scheduler-attached",
                    "--scheduler-unit",
                    args.timer_unit,
                ],
                cwd=ROOT,
            )
        )

        if not args.skip_publish:
            report["steps"].append(
                run(
                    [
                        "bash",
                        "scripts/publish_homepage_index.sh",
                    ],
                    cwd=ROOT,
                )
            )

        report["ok"] = all(int(step.get("returncode", 1)) == 0 for step in report["steps"]) and len(report["steps"]) >= 1
    except Exception as exc:  # noqa: BLE001
        report["error"] = str(exc)
        report["ok"] = False

    LAST_RUN_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": report["ok"], "run_at_utc": report["run_at_utc"], "mode": mode, "timer_unit": args.timer_unit, "steps": [s.get("cmd") for s in report["steps"]]}, ensure_ascii=False))
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
