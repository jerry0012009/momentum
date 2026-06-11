#!/usr/bin/env python3
"""Rank 139 hosted pilot — autonomous refresh runner (no LLM).

Intent:
- Keep Rank 139 running as a self-refreshing hosted P3 sidecar.
- Do NOT rely on bot2/bot3 to repeatedly “watch” Rank 139.

What it does (one-shot):
1) Recompute Rank 139 minimal clean replication (updates trade_log/summary/report).
2) Rebuild the minimal hosted pilot monitoring board (CSV + ops HTML + refresh clock).
3) Optionally publish the site index.

Safe: offline/paper artifacts only (no broker/exchange trading).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank139_cusum_event_bar_confirm_veto_15m"
LAST_RUN_PATH = ART_DIR / "hosted_pilot_refresh_last_run.json"


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
        "stdout": (p.stdout or "").strip()[-8000:],
        "stderr": (p.stderr or "").strip()[-8000:],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Autonomous refresh for Rank 139 hosted pilot artifacts.")
    parser.add_argument("--skip-publish", action="store_true", help="Skip publishing homepage/site index.")
    args = parser.parse_args()

    ART_DIR.mkdir(parents=True, exist_ok=True)

    report: dict = {
        "run_at_utc": utc_now_iso(),
        "ok": False,
        "steps": [],
    }

    try:
        report["steps"].append(
            run(
                [
                    sys.executable,
                    "scripts/build_rank139_cusum_event_bar_confirm_veto_clean_replication.py",
                ],
                cwd=ROOT,
            )
        )

        report["steps"].append(
            run(
                [
                    sys.executable,
                    "scripts/build_rank139_narrow_paper_pilot_minimal.py",
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

        report["ok"] = all(int(s.get("returncode", 1)) == 0 for s in report["steps"]) and len(report["steps"]) >= 2
    except Exception as exc:  # noqa: BLE001
        report["error"] = str(exc)
        report["ok"] = False

    LAST_RUN_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    # Print short summary for systemd/journal
    print(json.dumps({"ok": report["ok"], "run_at_utc": report["run_at_utc"], "steps": [s.get("cmd") for s in report["steps"]]}, ensure_ascii=False))

    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
