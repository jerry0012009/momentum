#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "ema_psar_raw_alpha"
BUILD_SCRIPT = ROOT / "scripts" / "build_ema_psar_raw_alpha_report.py"
DUE_PATH = ART_DIR / "ema_paper_trading_due_guardrail_snapshot.csv"
QUEUE_PATH = ART_DIR / "ema_paper_trading_next_close_action_queue.csv"
DAILY_REFRESH_PATH = ART_DIR / "ema_paper_trading_daily_refresh_snapshot.csv"
HISTORY_PATH = ART_DIR / "ema_paper_trading_refresh_history.csv"
ACTIONABLE_BUCKETS = {"due_now_refresh_window", "overdue_refresh_check"}
SOON_BUCKETS = {"due_soon"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Guarded operator wrapper for EMA paper/shadow refresh. "
            "Default behavior rebuilds the EMA raw-alpha report artifacts, then summarizes only the lanes "
            "that are due now / overdue / due soon."
        )
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Reuse the current EMA artifacts instead of rebuilding them first.",
    )
    parser.add_argument(
        "--require-due",
        action="store_true",
        help="Exit with code 2 when there is no due-now / overdue lane.",
    )
    parser.add_argument(
        "--show-limit",
        type=int,
        default=3,
        help="How many rows to show in the fallback summary when nothing is due now (default: 3).",
    )
    return parser.parse_args()


def read_csv_rows(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing artifact: {path}")
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def sort_rows(rows: List[Dict[str, str]], key_name: str) -> List[Dict[str, str]]:
    def key_fn(row: Dict[str, str]) -> int:
        raw = str(row.get(key_name, "") or "")
        try:
            return int(raw)
        except ValueError:
            return 10**9

    return sorted(rows, key=key_fn)


def rebuild_if_needed(skip_build: bool) -> None:
    if skip_build:
        return
    subprocess.run([sys.executable, str(BUILD_SCRIPT)], cwd=str(ROOT), check=True)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_now_label() -> str:
    return utc_now().strftime("%Y-%m-%d %H:%M UTC")


def parse_utc_timestamp(raw: str) -> datetime | None:
    text = (raw or "").strip()
    if not text:
        return None
    for fmt in ("%Y-%m-%d %H:%M UTC", "%Y-%m-%d %H:%M:%S UTC"):
        try:
            return datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def format_due_gap(target: datetime, now: datetime | None = None) -> str:
    ref = now or utc_now()
    delta_seconds = int(round((target - ref).total_seconds()))
    if delta_seconds <= 0:
        overdue_seconds = abs(delta_seconds)
        if overdue_seconds < 3600:
            return f"已超时约 {max(1, round(overdue_seconds / 60))} 分钟"
        return f"已超时约 {overdue_seconds / 3600:.1f} 小时"
    if delta_seconds < 3600:
        return f"约 {max(1, round(delta_seconds / 60))} 分钟 后到点"
    return f"约 {delta_seconds / 3600:.1f} 小时 后到点"


def build_history_key(row: Dict[str, str]) -> str:
    scope = (row.get("deployment_scope") or "-").strip()
    market_freq = (row.get("market_freq_book") or "-").strip()
    latest_bar = (row.get("latest_completed_bar_utc") or "-").strip()
    return " | ".join([scope, market_freq, latest_bar])


def append_refresh_history(snapshot_rows: List[Dict[str, str]]) -> Tuple[int, int]:
    if not snapshot_rows:
        return 0, 0

    history_rows: List[Dict[str, str]] = []
    existing_keys = set()
    if HISTORY_PATH.exists():
        with HISTORY_PATH.open("r", encoding="utf-8", newline="") as f:
            history_rows = list(csv.DictReader(f))
        for row in history_rows:
            key = (row.get("history_key") or "").strip() or build_history_key(row)
            if key:
                existing_keys.add(key)

    recorded_at = utc_now_label()
    appended = 0
    for row in snapshot_rows:
        history_key = build_history_key(row)
        if history_key in existing_keys:
            continue
        history_rows.append(
            {
                "history_recorded_at_utc": recorded_at,
                "history_key": history_key,
                **row,
            }
        )
        existing_keys.add(history_key)
        appended += 1

    fieldnames = ["history_recorded_at_utc", "history_key", *snapshot_rows[0].keys()]
    with HISTORY_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(history_rows)

    return appended, len(history_rows)


def fmt_queue_hint(queue_lookup: Dict[str, Dict[str, str]], scope: str) -> str:
    queue_row = queue_lookup.get(scope)
    if not queue_row:
        return "-"
    action = (queue_row.get("action_when_due") or "-").strip()
    blocked = (queue_row.get("if_blocked") or "-").strip()
    return f"到点动作：{action}｜若阻塞：{blocked}"


def maybe_fast_precheck(args: argparse.Namespace) -> Tuple[List[Dict[str, str]], Dict[str, Dict[str, str]]] | None:
    if args.skip_build or not args.require_due:
        return None
    if not DUE_PATH.exists() or not QUEUE_PATH.exists():
        return None

    due_rows = sort_rows(read_csv_rows(DUE_PATH), "guardrail_rank")
    queue_rows = sort_rows(read_csv_rows(QUEUE_PATH), "queue_rank")
    if not due_rows:
        return None

    now = utc_now()
    refreshed_rows: List[Dict[str, str]] = []
    for row in due_rows:
        next_close = parse_utc_timestamp(row.get("next_expected_close_utc") or "")
        if next_close is None or next_close <= now:
            return None
        refreshed_rows.append(
            {
                **row,
                "relative_due_gap": format_due_gap(next_close, now),
            }
        )

    queue_lookup = {row.get("deployment_scope", ""): row for row in queue_rows}
    return refreshed_rows, queue_lookup


def print_actionable(rows: List[Dict[str, str]], queue_lookup: Dict[str, Dict[str, str]]) -> None:
    print("[ema-refresh-guard] 当前存在 due-now / overdue lane：")
    for row in rows:
        scope = row.get("deployment_scope", "-")
        due_bucket = row.get("due_bucket", "-")
        gap = row.get("relative_due_gap", "-")
        action = (row.get("guardrail_action") or "-").strip()
        missed = (row.get("if_missed") or "-").strip()
        queue_hint = fmt_queue_hint(queue_lookup, scope)
        print(f"- {scope} | {due_bucket} | {gap}")
        print(f"  守门动作：{action}")
        print(f"  漏跑后：{missed}")
        print(f"  {queue_hint}")


def print_fallback(rows: List[Dict[str, str]], queue_lookup: Dict[str, Dict[str, str]], limit: int) -> None:
    print("[ema-refresh-guard] 当前没有 due-now / overdue lane。最靠前的 lane 如下：")
    for row in rows[:limit]:
        scope = row.get("deployment_scope", "-")
        due_bucket = row.get("due_bucket", "-")
        gap = row.get("relative_due_gap", "-")
        action = (row.get("guardrail_action") or "-").strip()
        queue_hint = fmt_queue_hint(queue_lookup, scope)
        print(f"- {scope} | {due_bucket} | {gap}")
        print(f"  当前守门：{action}")
        print(f"  {queue_hint}")


def main() -> int:
    args = parse_args()

    fast_precheck = maybe_fast_precheck(args)
    if fast_precheck is not None:
        due_rows, queue_lookup = fast_precheck
        fallback_rows = [row for row in due_rows if (row.get("due_bucket") or "") in SOON_BUCKETS] or due_rows
        print("[ema-refresh-guard] fast-precheck：所有 lane 的 next_expected_close_utc 仍在未来，跳过本轮 full rebuild。")
        print(
            f"[ema-refresh-history] fast-precheck 已跳过 history 追加；下一根 completed bar 到来前，{HISTORY_PATH.name} 不会出现新 rows。"
        )
        print_fallback(fallback_rows, queue_lookup, max(args.show_limit, 1))
        print("[ema-refresh-guard] require-due 已开启：当前仍应等待下一根 completed bar，而不是伪造 refresh。")
        return 2

    rebuild_if_needed(args.skip_build)

    due_rows = sort_rows(read_csv_rows(DUE_PATH), "guardrail_rank")
    queue_rows = sort_rows(read_csv_rows(QUEUE_PATH), "queue_rank")
    daily_refresh_rows = sort_rows(read_csv_rows(DAILY_REFRESH_PATH), "refresh_rank")
    queue_lookup = {row.get("deployment_scope", ""): row for row in queue_rows}

    appended, total_rows = append_refresh_history(daily_refresh_rows)
    if appended:
        print(
            f"[ema-refresh-history] 已向 {HISTORY_PATH.name} 追加 {appended} 条新 completed-bar rows（累计 {total_rows} 条）。"
        )
    else:
        print(f"[ema-refresh-history] 当前没有新的 completed-bar rows；{HISTORY_PATH.name} 仍为 {total_rows} 条。")

    actionable_rows = [row for row in due_rows if (row.get("due_bucket") or "") in ACTIONABLE_BUCKETS]
    fallback_rows = [row for row in due_rows if (row.get("due_bucket") or "") in SOON_BUCKETS] or due_rows

    if actionable_rows:
        print_actionable(actionable_rows, queue_lookup)
        return 0

    print_fallback(fallback_rows, queue_lookup, max(args.show_limit, 1))
    if args.require_due:
        print("[ema-refresh-guard] require-due 已开启：当前仍应等待下一根 completed bar，而不是伪造 refresh。")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
