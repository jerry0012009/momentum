#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "ema_psar_raw_alpha"
STATUS_PATH = ART_DIR / "ema_paper_autopilot_status.json"
RUNS_JSONL_PATH = ART_DIR / "ema_paper_autopilot_runs.jsonl"
DUE_PATH = ART_DIR / "ema_paper_trading_due_guardrail_snapshot.csv"
HISTORY_PATH = ART_DIR / "ema_paper_trading_refresh_history.csv"
GUARD_SCRIPT = ROOT / "scripts" / "run_ema_paper_trading_guarded_refresh.py"
PUBLISH_SCRIPT = ROOT / "scripts" / "publish_ema_paper_trading_site.sh"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Autopilot wrapper for EMA paper trading guarded refresh.")
    parser.add_argument("--show-limit", type=int, default=3)
    parser.add_argument("--skip-publish", action="store_true", help="Skip site publish even when a due refresh is performed.")
    return parser.parse_args()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def sort_rows(rows: list[dict[str, str]], key_name: str) -> list[dict[str, str]]:
    def key_fn(row: dict[str, str]) -> int:
        raw = str(row.get(key_name, "") or "")
        try:
            return int(raw)
        except ValueError:
            return 10**9

    return sorted(rows, key=key_fn)


def classify_exit(code: int) -> str:
    if code == 0:
        return "due_refreshed"
    if code == 2:
        return "waiting_not_due"
    return "error"


def parse_utc_label(raw: str | None) -> datetime | None:
    text = str(raw or "").strip()
    if not text:
        return None
    for fmt in ("%Y-%m-%d %H:%M UTC", "%Y-%m-%d %H:%M:%S UTC"):
        try:
            return datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def cheap_waiting_precheck(limit: int) -> dict[str, Any] | None:
    rows = sort_rows(read_csv_rows(DUE_PATH), "guardrail_rank")
    if not rows:
        return None
    now = datetime.now(timezone.utc)
    parsed = [parse_utc_label(row.get("next_expected_close_utc")) for row in rows]
    if any(ts is None for ts in parsed):
        return None
    if any(ts <= now for ts in parsed if ts is not None):
        return None
    return {
        "mode": "waiting_not_due",
        "guard_returncode": 2,
        "guard_stdout_tail": "[ema-autopilot] cheap-precheck: next_expected_close_utc 全部仍在未来，跳过本轮 full rebuild。",
        "guard_stderr_tail": "",
        "history_rows": count_history_rows(),
        "top_due_rows": top_due_rows(limit),
    }


def top_due_rows(limit: int) -> list[dict[str, str]]:
    rows = sort_rows(read_csv_rows(DUE_PATH), "guardrail_rank")
    keep = []
    for row in rows[: max(1, limit)]:
        keep.append(
            {
                "guardrail_rank": row.get("guardrail_rank"),
                "deployment_scope": row.get("deployment_scope"),
                "market_freq_book": row.get("market_freq_book"),
                "due_bucket": row.get("due_bucket"),
                "next_expected_close_utc": row.get("next_expected_close_utc"),
                "guardrail_action": row.get("guardrail_action"),
            }
        )
    return keep


def count_history_rows() -> int:
    rows = read_csv_rows(HISTORY_PATH)
    return len(rows)


def run_subprocess(cmd: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True)
    return proc.returncode, proc.stdout, proc.stderr


def write_status(payload: dict[str, Any]) -> None:
    STATUS_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def main() -> int:
    args = parse_args()
    ensure_dir(ART_DIR)

    started_at = utc_now_iso()
    prechecked = cheap_waiting_precheck(args.show_limit)
    if prechecked is not None:
        mode = str(prechecked["mode"])
        guard_rc = int(prechecked["guard_returncode"])
        guard_stdout = str(prechecked["guard_stdout_tail"])
        guard_stderr = str(prechecked["guard_stderr_tail"])
    else:
        guard_cmd = [sys.executable, str(GUARD_SCRIPT), "--require-due", "--show-limit", str(max(1, args.show_limit))]
        guard_rc, guard_stdout, guard_stderr = run_subprocess(guard_cmd)
        mode = classify_exit(guard_rc)

    publish_payload: dict[str, Any] = {
        "attempted": False,
        "returncode": None,
        "stdout_tail": "",
        "stderr_tail": "",
    }
    if mode == "due_refreshed" and not args.skip_publish:
        publish_payload["attempted"] = True
        rc, out, err = run_subprocess(["bash", str(PUBLISH_SCRIPT)])
        publish_payload.update(
            {
                "returncode": rc,
                "stdout_tail": "\n".join(out.strip().splitlines()[-20:]),
                "stderr_tail": "\n".join(err.strip().splitlines()[-20:]),
            }
        )
        if rc != 0:
            mode = "error"

    status_payload = {
        "updated_at_utc": utc_now_iso(),
        "runner": "ema_paper_autopilot_host_cron",
        "mode": mode,
        "guard_returncode": guard_rc,
        "guard_stdout_tail": "\n".join(guard_stdout.strip().splitlines()[-30:]),
        "guard_stderr_tail": "\n".join(guard_stderr.strip().splitlines()[-20:]),
        "publish": publish_payload,
        "history_rows": prechecked["history_rows"] if prechecked is not None else count_history_rows(),
        "top_due_rows": prechecked["top_due_rows"] if prechecked is not None else top_due_rows(args.show_limit),
    }
    write_status(status_payload)

    run_record = {
        "started_at_utc": started_at,
        "finished_at_utc": utc_now_iso(),
        "mode": mode,
        "guard_returncode": guard_rc,
        "publish_attempted": publish_payload["attempted"],
        "publish_returncode": publish_payload["returncode"],
        "top_due_rows": status_payload["top_due_rows"],
    }
    append_jsonl(RUNS_JSONL_PATH, run_record)

    print(json.dumps(status_payload, ensure_ascii=False, indent=2))
    return 0 if mode in {"due_refreshed", "waiting_not_due"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
