#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone

from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE_DIR = ROOT / "reports" / "site" / "factors" / "alpha_closure_board"
OUT_PATH = SITE_DIR / "report.html"
ARTIFACT_DIR = ROOT / "reports" / "artifacts" / "alpha_closure_board"
PROMOTION_GATE_PATH = ARTIFACT_DIR / "paper_live_promotion_gate_v1.csv"
BASELINE_COMPARE_PATH = ARTIFACT_DIR / "structure_vs_ema_baseline_v1.csv"
SMALL_LIVE_PLUMBING_PATH = ARTIFACT_DIR / "small_live_plumbing_v1.csv"
SMALL_LIVE_LEDGER_TEMPLATE_PATH = ARTIFACT_DIR / "small_live_ledger_template_v1.csv"
SMALL_LIVE_ROUTING_DRY_RUN_CHECKLIST_PATH = ARTIFACT_DIR / "small_live_routing_dry_run_checklist_v1.csv"
SMALL_LIVE_ROUTING_DRY_RUN_SAMPLE_ROW_PATH = ARTIFACT_DIR / "small_live_routing_dry_run_sample_row_v1.csv"
SMALL_LIVE_OPERATOR_RECONCILIATION_SEQUENCE_PATH = ARTIFACT_DIR / "small_live_operator_reconciliation_sequence_v1.csv"
SMALL_LIVE_OPERATOR_HANDOFF_PACKET_PATH = ARTIFACT_DIR / "small_live_operator_handoff_packet_v1.csv"
SMALL_LIVE_REVIEW_TICKET_TEMPLATE_PATH = ARTIFACT_DIR / "small_live_review_ticket_template_v1.csv"
SMALL_LIVE_REVIEW_WRITEBACK_MATRIX_PATH = ARTIFACT_DIR / "small_live_review_writeback_matrix_v1.csv"
SMALL_LIVE_REVIEW_REGISTRY_TEMPLATE_PATH = ARTIFACT_DIR / "small_live_review_registry_template_v1.csv"
SMALL_LIVE_SHADOW_PARITY_CHECKLIST_PATH = ARTIFACT_DIR / "paper_live_shadow_parity_checklist_v1.csv"
SMALL_LIVE_PARITY_RED_ACTION_LADDER_PATH = ARTIFACT_DIR / "small_live_parity_red_action_ladder_v1.csv"
SMALL_LIVE_SHADOW_PARITY_SAMPLE_ROW_PATH = ARTIFACT_DIR / "small_live_shadow_parity_sample_row_v1.csv"
SMALL_LIVE_GREEN_SHADOW_PARITY_SAMPLE_ROW_PATH = ARTIFACT_DIR / "small_live_green_shadow_parity_sample_row_v1.csv"
SMALL_LIVE_REOPEN_GATE_CHECKLIST_PATH = ARTIFACT_DIR / "small_live_reopen_gate_checklist_v1.csv"
SMALL_LIVE_REOPEN_RESUME_SAMPLE_ROW_PATH = ARTIFACT_DIR / "small_live_reopen_resume_sample_row_v1.csv"
SMALL_LIVE_RANK2_STATUS_SNAPSHOT_PATH = ARTIFACT_DIR / "small_live_rank2_status_snapshot_v1.csv"
SMALL_LIVE_RANK2_RECEIPT_OPERATOR_PACKET_PATH = ARTIFACT_DIR / "small_live_rank2_receipt_chain_operator_packet_v1.csv"
SMALL_LIVE_RANK2_RECEIPT_COMPLETION_GATE_PATH = ARTIFACT_DIR / "small_live_rank2_receipt_chain_completion_gate_v1.csv"
SMALL_LIVE_RANK2_CLOSEOUT_SNAPSHOT_PATH = ARTIFACT_DIR / "small_live_rank2_closeout_snapshot_v1.csv"
SMALL_LIVE_RANK2_RECEIPT_AUDIT_PATH = ARTIFACT_DIR / "small_live_rank2_receipt_chain_audit_v1.csv"
SMALL_LIVE_RANK2_REPLAY_RUNSHEET_PATH = ARTIFACT_DIR / "small_live_rank2_replay_runsheet_v1.csv"
SMALL_LIVE_RANK2_REPLAY_PREFLIGHT_SNAPSHOT_PATH = ARTIFACT_DIR / "small_live_rank2_replay_preflight_snapshot_v1.csv"
SMALL_LIVE_RANK2_REPLAY_ROUNDING_BUDGET_LADDER_PATH = ARTIFACT_DIR / "small_live_rank2_replay_rounding_budget_ladder_v1.csv"
SMALL_LIVE_RANK2_REPLAY_CLOSEOUT_MATRIX_PATH = ARTIFACT_DIR / "small_live_rank2_replay_closeout_matrix_v1.csv"
SMALL_LIVE_RANK2_SHADOW_PARITY_LAUNCH_PACKET_PATH = ARTIFACT_DIR / "small_live_rank2_shadow_parity_launch_packet_v1.csv"
SMALL_LIVE_RANK2_SHADOW_PARITY_STARTER_ROWS_PATH = ARTIFACT_DIR / "small_live_rank2_shadow_parity_starter_rows_v1.csv"
SMALL_LIVE_RANK2_NEXT_STATUS_CHANGE_GATE_PATH = ARTIFACT_DIR / "small_live_rank2_next_status_change_gate_v1.csv"
SMALL_LIVE_RANK2_NEXT_REPLAY_BUNDLE_PATH = ARTIFACT_DIR / "small_live_rank2_next_replay_bundle_v1.csv"
SMALL_LIVE_DEFAULT_SEAT_QUEUE_PATH = ARTIFACT_DIR / "small_live_default_seat_queue_v1.csv"
SMALL_LIVE_LIVE_SEAT_REENTRY_TRIGGER_MATRIX_PATH = ARTIFACT_DIR / "small_live_live_seat_reentry_trigger_matrix_v1.csv"
SMALL_LIVE_STATUS_CHANGE_WATCHBOARD_PATH = ARTIFACT_DIR / "small_live_status_change_watchboard_v1.csv"
SMALL_LIVE_STATUS_TRIGGER_SNAPSHOT_PATH = ARTIFACT_DIR / "small_live_status_trigger_snapshot_v1.csv"
SMALL_LIVE_NOW_ACTION_QUEUE_PATH = ARTIFACT_DIR / "small_live_now_action_queue_v1.csv"
SMALL_LIVE_EVIDENCE_FRESHNESS_BOARD_PATH = ARTIFACT_DIR / "small_live_evidence_freshness_board_v1.csv"
SMALL_LIVE_STATE_RESYNC_GUARD_PATH = ARTIFACT_DIR / "small_live_state_resync_guard_v1.csv"
SMALL_LIVE_RANK2_EXECUTION_SYNC_GUARD_PATH = ARTIFACT_DIR / "small_live_rank2_execution_sync_guard_v1.csv"
SMALL_LIVE_RANK2_REPLAY_READY_GATE_PATH = ARTIFACT_DIR / "small_live_rank2_replay_ready_gate_v1.csv"
TODO_PATH = ROOT / "docs" / "TODO.md"
MANUAL_NARROW_RECONCILIATION_PATH = ROOT / "reports" / "artifacts" / "manual_narrow_paper_lanes" / "manual_narrow_paper_desk_reconciliation.csv"
MANUAL_NARROW_BOT3_TRIGGER_PATH = ROOT / "reports" / "artifacts" / "manual_narrow_paper_lanes" / "manual_narrow_paper_bot3_reentry_queue.csv"


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def read_json_dict(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def get_rank2_replay_priority_context() -> dict[str, object]:
    default_priority_by_symbol = {
        "ETH-USD": "P1",
        "SOL-USD": "P2",
        "BTC-USD": "P3",
    }
    default_order_text = "ETH → SOL → BTC"
    default_policy_blurb = (
        "若只按当前 packet 的静态白名单顺序读，默认仍是 ETH → SOL → BTC；"
        "但若后续已有更晚的 rounding 预算快照，应以更晚快照为准。"
    )
    default_action_text = "只做 1 次 whitelist-bound test/no-fill replay，并回填 intent+ack+cancel(close) 真实 refs"
    default_why_by_symbol = {
        "ETH-USD": "packet 已标注 preferred whitelist leg；当前更适合作为单次真实 test/no-fill replay 的首选。",
        "SOL-USD": "若 ETH 的 venue precision / min_notional 不顺，SOL 是次优白名单腿；仍保持同一 candidate scope。",
        "BTC-USD": "BTC 当前 lane_note 仍偏 weakest cross-asset leg，更适合作为最后备选而非首腿。",
    }
    default_suggested_notional_by_symbol = {
        "ETH-USD": "100",
        "SOL-USD": "40",
        "BTC-USD": "300",
    }
    default_budget_read_by_symbol = {
        "ETH-USD": "pass_50bps_only",
        "SOL-USD": "pass_25bps",
        "BTC-USD": "fails_even_50bps_guard",
    }

    ladder_rows = read_csv_rows(SMALL_LIVE_RANK2_REPLAY_ROUNDING_BUDGET_LADDER_PATH)
    if not ladder_rows:
        return {
            "priority_by_symbol": default_priority_by_symbol,
            "why_by_symbol": default_why_by_symbol,
            "order_text": default_order_text,
            "policy_blurb": default_policy_blurb,
            "action_text": default_action_text,
            "suggested_notional_by_symbol": default_suggested_notional_by_symbol,
            "budget_read_by_symbol": default_budget_read_by_symbol,
            "ladder_row_by_symbol": {},
        }

    def priority_value(value: str) -> int:
        value = (value or "").strip().upper()
        if value.startswith("P") and value[1:].isdigit():
            return int(value[1:])
        return 99

    ordered_rows = sorted(ladder_rows, key=lambda row: (priority_value(row.get("rounding_budget_order", "")), row.get("research_symbol", "")))
    ladder_row_by_symbol = {row.get("research_symbol", ""): row for row in ordered_rows if row.get("research_symbol")}
    priority_by_symbol = {
        row.get("research_symbol", ""): row.get("rounding_budget_order", "") or default_priority_by_symbol.get(row.get("research_symbol", ""), "P9")
        for row in ordered_rows
    }
    why_by_symbol = {
        row.get("research_symbol", ""): row.get("operator_action_read", "") or default_why_by_symbol.get(row.get("research_symbol", ""), "")
        for row in ordered_rows
    }
    suggested_notional_by_symbol = {
        row.get("research_symbol", ""): row.get("suggested_notional_for_25bps_usdt", "") or default_suggested_notional_by_symbol.get(row.get("research_symbol", ""), "")
        for row in ordered_rows
    }
    budget_read_by_symbol = {
        row.get("research_symbol", ""): row.get("sample_50u_budget_read", "") or default_budget_read_by_symbol.get(row.get("research_symbol", ""), "")
        for row in ordered_rows
    }
    for symbol, priority in default_priority_by_symbol.items():
        priority_by_symbol.setdefault(symbol, priority)
        why_by_symbol.setdefault(symbol, default_why_by_symbol[symbol])
        suggested_notional_by_symbol.setdefault(symbol, default_suggested_notional_by_symbol[symbol])
        budget_read_by_symbol.setdefault(symbol, default_budget_read_by_symbol[symbol])

    ordered_symbols = [row.get("research_symbol", "") for row in ordered_rows if row.get("research_symbol")]
    symbol_label = lambda symbol: symbol.replace("-USD", "")
    order_text = " → ".join(symbol_label(symbol) for symbol in ordered_symbols) or default_order_text

    eth_row = next((row for row in ordered_rows if row.get("research_symbol") == "ETH-USD"), {})
    btc_row = next((row for row in ordered_rows if row.get("research_symbol") == "BTC-USD"), {})
    eth_25 = eth_row.get("suggested_notional_for_25bps_usdt", "100")
    btc_25 = btc_row.get("suggested_notional_for_25bps_usdt", "300")
    policy_blurb = (
        f"若坚持 50U test/no-fill 且把 rounding 损耗预算压到 <=25bps，当前更诚实的 replay 顺序应读成 {order_text}；"
        f"其中 SOL 已过线，ETH 更适合先把样例抬到 >= {eth_25}U，BTC 继续只保留最后备选（约 >= {btc_25}U 才接近同档口径）。"
    )
    action_text = (
        f"只做 1 次 whitelist-bound test/no-fill replay，并回填 intent+ack+cancel(close) 真实 refs；"
        f"若坚持 50U 且要把 rounding 损耗预算压到 <=25bps，当前先做 {order_text.split(' → ')[0]} 更诚实。"
    )
    return {
        "priority_by_symbol": priority_by_symbol,
        "why_by_symbol": why_by_symbol,
        "order_text": order_text,
        "policy_blurb": policy_blurb,
        "action_text": action_text,
        "suggested_notional_by_symbol": suggested_notional_by_symbol,
        "budget_read_by_symbol": budget_read_by_symbol,
        "ladder_row_by_symbol": ladder_row_by_symbol,
    }


def format_file_freshness(path: Path, *, stale_after_min: int, warning_after_min: int) -> dict[str, str]:
    if not path.exists():
        return {
            "latest_file_mtime_utc": "missing",
            "approx_age": "missing",
            "freshness_state": "missing",
        }

    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    age_minutes = max(0, int((datetime.now(timezone.utc) - mtime).total_seconds() // 60))
    if age_minutes >= stale_after_min:
        freshness = "stale"
    elif age_minutes >= warning_after_min:
        freshness = "warning"
    else:
        freshness = "fresh"

    if age_minutes < 60:
        approx_age = f"{age_minutes}m"
    else:
        approx_age = f"{age_minutes / 60:.1f}h"

    return {
        "latest_file_mtime_utc": mtime.strftime("%Y-%m-%d %H:%M UTC"),
        "approx_age": approx_age,
        "freshness_state": freshness,
    }


def format_sync_guard(source_path: Path, dependent_path: Path) -> dict[str, str]:
    if not source_path.exists():
        return {
            "source_mtime_utc": "missing",
            "dependent_mtime_utc": datetime.fromtimestamp(dependent_path.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC") if dependent_path.exists() else "missing",
            "lag_read": "missing_source",
            "guard_state": "missing_source",
        }
    if not dependent_path.exists():
        return {
            "source_mtime_utc": datetime.fromtimestamp(source_path.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "dependent_mtime_utc": "missing",
            "lag_read": "dependent_missing",
            "guard_state": "resync_due",
        }

    source_mtime = datetime.fromtimestamp(source_path.stat().st_mtime, tz=timezone.utc)
    dependent_mtime = datetime.fromtimestamp(dependent_path.stat().st_mtime, tz=timezone.utc)
    lag_seconds = int((source_mtime - dependent_mtime).total_seconds())

    if lag_seconds > 0:
        lag_read = f"source_newer_by_{lag_seconds}s" if lag_seconds < 60 else f"source_newer_by_{lag_seconds // 60}m"
        guard_state = "resync_due"
    else:
        ahead_seconds = abs(lag_seconds)
        lag_read = f"dependent_not_older({ahead_seconds}s)" if ahead_seconds < 60 else f"dependent_not_older({ahead_seconds // 60}m)"
        guard_state = "synced"

    return {
        "source_mtime_utc": source_mtime.strftime("%Y-%m-%d %H:%M UTC"),
        "dependent_mtime_utc": dependent_mtime.strftime("%Y-%m-%d %H:%M UTC"),
        "lag_read": lag_read,
        "guard_state": guard_state,
    }


def get_rank2_closeout_snapshot_rows() -> list[dict[str, str]]:
    status_rows = read_csv_rows(SMALL_LIVE_RANK2_STATUS_SNAPSHOT_PATH)
    packet_rows = read_csv_rows(SMALL_LIVE_RANK2_RECEIPT_OPERATOR_PACKET_PATH)
    gate_rows = read_csv_rows(SMALL_LIVE_RANK2_RECEIPT_COMPLETION_GATE_PATH)
    if not status_rows or not packet_rows or not gate_rows:
        return []

    status = status_rows[0]
    gate_by_symbol = {row["research_symbol"]: row for row in gate_rows}
    merged_rows = []
    for packet in packet_rows:
        gate = gate_by_symbol.get(packet["research_symbol"], {})
        merged_rows.append(
            {
                "row_order": packet["packet_order"],
                "research_symbol": packet["research_symbol"],
                "venue_symbol": packet["venue_symbol"],
                "deployment_scope": packet["deployment_scope"],
                "next_allowed_action": status["next_allowed_action"],
                "allowed_operator_action": packet["allowed_operator_action"],
                "pass_condition": gate.get("pass_condition", ""),
                "hard_stop": packet["hard_stop"],
                "current_blockers": packet["current_blockers"],
                "current_state": status["current_hard_verdict"],
                "closeout_state": status["closeout_state"],
                "generated_at_utc": gate.get("generated_at_utc", status.get("generated_at_utc", "")),
            }
        )
    return merged_rows


def write_rank2_closeout_snapshot_csv(rows: list[dict[str, str]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with SMALL_LIVE_RANK2_CLOSEOUT_SNAPSHOT_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "row_order",
                "research_symbol",
                "venue_symbol",
                "deployment_scope",
                "next_allowed_action",
                "allowed_operator_action",
                "pass_condition",
                "hard_stop",
                "current_blockers",
                "current_state",
                "closeout_state",
                "generated_at_utc",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def get_rank2_receipt_audit_rows() -> list[dict[str, str]]:
    status_rows = read_csv_rows(SMALL_LIVE_RANK2_STATUS_SNAPSHOT_PATH)
    log_rows = read_csv_rows(ARTIFACT_DIR / "small_live_rank2_receipt_chain_log_template_v1.csv")
    gate_rows = read_csv_rows(SMALL_LIVE_RANK2_RECEIPT_COMPLETION_GATE_PATH)
    if not status_rows or not log_rows or not gate_rows:
        return []

    status = status_rows[0]
    gate_by_symbol = {row["research_symbol"]: row for row in gate_rows}
    replay_context = get_rank2_replay_priority_context()
    priority_by_symbol = replay_context["priority_by_symbol"]
    suggested_notional_by_symbol = replay_context["suggested_notional_by_symbol"]
    budget_read_by_symbol = replay_context["budget_read_by_symbol"]
    why_by_symbol = replay_context["why_by_symbol"]
    ladder_row_by_symbol = replay_context["ladder_row_by_symbol"]

    def is_real_ref(value: str) -> bool:
        value = (value or "").strip()
        if not value:
            return False
        return not value.startswith("pending_")

    def priority_value(value: str) -> int:
        value = (value or "").strip().upper()
        if value.startswith("P") and value[1:].isdigit():
            return int(value[1:])
        return 99

    rows: list[dict[str, str]] = []
    for log in log_rows:
        symbol = log["research_symbol"]
        gate = gate_by_symbol.get(symbol, {})
        ladder_row = ladder_row_by_symbol.get(symbol, {})
        ref_pairs = [
            ("intent_ref", log.get("intent_ref", "")),
            ("ack_ref", log.get("ack_ref", "")),
            ("cancel_or_close_ref", log.get("cancel_or_close_ref", "")),
        ]
        landed = [name for name, value in ref_pairs if is_real_ref(value)]
        missing = [name for name, value in ref_pairs if not is_real_ref(value)]
        all_real = len(missing) == 0
        priority = str(priority_by_symbol.get(symbol, "P9"))
        rows.append(
            {
                "audit_order": priority,
                "research_symbol": symbol,
                "venue_symbol": log["venue_symbol"],
                "chain_status": log.get("chain_status", ""),
                "real_refs_landed": f"{len(landed)}/3",
                "missing_real_refs": ", ".join(missing) if missing else "none",
                "required_scope_guard": gate.get("scope_guard", log.get("scope_check", "")),
                "required_capital_guard": gate.get("capital_guard", log.get("capital_check", "")),
                "suggested_notional_for_25bps_usdt": str(suggested_notional_by_symbol.get(symbol, "")),
                "sample_50u_budget_read": str(budget_read_by_symbol.get(symbol, "")),
                "operator_action_read": str(why_by_symbol.get(symbol, "")),
                "current_verdict": "eligible_for_shadow_parity_review" if all_real else "keep paper_candidate_only / blocked",
                "next_queue": "shadow_parity" if all_real else "routing_dry_run_replay",
                "hard_reason": gate.get("fail_condition", status.get("current_hard_verdict", "")) if not all_real else gate.get("pass_transition", ""),
                "generated_at_utc": ladder_row.get("observed_at_utc", gate.get("generated_at_utc", status.get("generated_at_utc", ""))),
            }
        )
    rows.sort(key=lambda row: (priority_value(row.get("audit_order", "")), row.get("research_symbol", "")))
    return rows


def write_rank2_receipt_audit_csv(rows: list[dict[str, str]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with SMALL_LIVE_RANK2_RECEIPT_AUDIT_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "audit_order",
                "research_symbol",
                "venue_symbol",
                "chain_status",
                "real_refs_landed",
                "missing_real_refs",
                "required_scope_guard",
                "required_capital_guard",
                "suggested_notional_for_25bps_usdt",
                "sample_50u_budget_read",
                "operator_action_read",
                "current_verdict",
                "next_queue",
                "hard_reason",
                "generated_at_utc",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def get_rank2_replay_runsheet_rows() -> list[dict[str, str]]:
    status_rows = read_csv_rows(SMALL_LIVE_RANK2_STATUS_SNAPSHOT_PATH)
    packet_rows = read_csv_rows(SMALL_LIVE_RANK2_RECEIPT_OPERATOR_PACKET_PATH)
    log_rows = read_csv_rows(ARTIFACT_DIR / "small_live_rank2_receipt_chain_log_template_v1.csv")
    gate_rows = read_csv_rows(SMALL_LIVE_RANK2_RECEIPT_COMPLETION_GATE_PATH)
    if not status_rows or not packet_rows or not log_rows or not gate_rows:
        return []

    status = status_rows[0]
    log_by_symbol = {row["research_symbol"]: row for row in log_rows}
    gate_by_symbol = {row["research_symbol"]: row for row in gate_rows}
    replay_context = get_rank2_replay_priority_context()
    priority_by_symbol = replay_context["priority_by_symbol"]
    why_by_symbol = replay_context["why_by_symbol"]

    rows: list[dict[str, str]] = []
    for packet in packet_rows:
        symbol = packet["research_symbol"]
        log = log_by_symbol.get(symbol, {})
        gate = gate_by_symbol.get(symbol, {})
        priority = str(priority_by_symbol.get(symbol, "P9"))
        why = str(why_by_symbol.get(symbol, "默认白名单备选。"))
        rows.append(
            {
                "replay_priority": priority,
                "research_symbol": symbol,
                "venue_symbol": packet["venue_symbol"],
                "venue_mode": packet.get("venue_mode", ""),
                "why_this_order": why,
                "preflight_gate": status.get("next_allowed_action", ""),
                "operator_action": packet.get("allowed_operator_action", ""),
                "must_capture_refs": packet.get("required_receipt_chain", ""),
                "current_log_stub": log.get("receipt_stub_id", ""),
                "pass_writeback": log.get("writeback_on_success", ""),
                "fail_writeback": log.get("writeback_on_fail", ""),
                "final_gate": gate.get("pass_transition", ""),
                "hard_stop": packet.get("hard_stop", ""),
                "generated_at_utc": gate.get("generated_at_utc", status.get("generated_at_utc", "")),
            }
        )

    rows.sort(key=lambda r: r["replay_priority"])
    return rows


def write_rank2_replay_runsheet_csv(rows: list[dict[str, str]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with SMALL_LIVE_RANK2_REPLAY_RUNSHEET_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "replay_priority",
                "research_symbol",
                "venue_symbol",
                "venue_mode",
                "why_this_order",
                "preflight_gate",
                "operator_action",
                "must_capture_refs",
                "current_log_stub",
                "pass_writeback",
                "fail_writeback",
                "final_gate",
                "hard_stop",
                "generated_at_utc",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def get_rank2_replay_closeout_matrix_rows() -> list[dict[str, str]]:
    status_rows = read_csv_rows(SMALL_LIVE_RANK2_STATUS_SNAPSHOT_PATH)
    packet_rows = read_csv_rows(SMALL_LIVE_RANK2_RECEIPT_OPERATOR_PACKET_PATH)
    log_rows = read_csv_rows(ARTIFACT_DIR / "small_live_rank2_receipt_chain_log_template_v1.csv")
    gate_rows = read_csv_rows(SMALL_LIVE_RANK2_RECEIPT_COMPLETION_GATE_PATH)
    if not status_rows or not packet_rows or not log_rows or not gate_rows:
        return []

    status = status_rows[0]
    log_by_symbol = {row["research_symbol"]: row for row in log_rows}
    gate_by_symbol = {row["research_symbol"]: row for row in gate_rows}
    priority_by_symbol = get_rank2_replay_priority_context()["priority_by_symbol"]

    rows: list[dict[str, str]] = []
    for packet in packet_rows:
        symbol = packet["research_symbol"]
        log = log_by_symbol.get(symbol, {})
        gate = gate_by_symbol.get(symbol, {})
        priority = priority_by_symbol.get(symbol, "P9")
        ticket_stub = log.get("receipt_stub_id", "pending-stub").replace("rank2-", "SL-DRYRUN-RANK2-").upper()
        rows.append(
            {
                "replay_priority": priority,
                "research_symbol": symbol,
                "venue_symbol": packet.get("venue_symbol", ""),
                "current_log_stub": log.get("receipt_stub_id", ""),
                "review_ticket_to_open": ticket_stub,
                "pass_closeout": "dry_run_pass -> eligible_for_shadow_parity_review only",
                "pass_writeback": packet.get("success_writeback", ""),
                "fail_closeout": "keep dry_run_only / blocked",
                "fail_writeback": packet.get("fail_writeback", ""),
                "next_queue_if_pass": "shadow_parity",
                "next_queue_if_fail": "routing_dry_run_replay",
                "required_refs": gate.get("required_real_refs", packet.get("required_receipt_chain", "")),
                "hard_stop": gate.get("fail_condition", packet.get("hard_stop", status.get("current_hard_verdict", ""))),
                "generated_at_utc": gate.get("generated_at_utc", status.get("generated_at_utc", "")),
            }
        )

    rows.sort(key=lambda r: r["replay_priority"])
    return rows


def write_rank2_replay_closeout_matrix_csv(rows: list[dict[str, str]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with SMALL_LIVE_RANK2_REPLAY_CLOSEOUT_MATRIX_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "replay_priority",
                "research_symbol",
                "venue_symbol",
                "current_log_stub",
                "review_ticket_to_open",
                "pass_closeout",
                "pass_writeback",
                "fail_closeout",
                "fail_writeback",
                "next_queue_if_pass",
                "next_queue_if_fail",
                "required_refs",
                "hard_stop",
                "generated_at_utc",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def get_rank2_shadow_parity_launch_packet_rows() -> list[dict[str, str]]:
    status_rows = read_csv_rows(SMALL_LIVE_RANK2_STATUS_SNAPSHOT_PATH)
    packet_rows = read_csv_rows(SMALL_LIVE_RANK2_RECEIPT_OPERATOR_PACKET_PATH)
    gate_rows = read_csv_rows(SMALL_LIVE_RANK2_RECEIPT_COMPLETION_GATE_PATH)
    ticket_rows = read_csv_rows(SMALL_LIVE_REVIEW_TICKET_TEMPLATE_PATH)
    if not status_rows or not packet_rows or not gate_rows or len(ticket_rows) < 2:
        return []

    status = status_rows[0]
    gate_by_symbol = {row["research_symbol"]: row for row in gate_rows}
    ticket = ticket_rows[1]
    priority_by_symbol = get_rank2_replay_priority_context()["priority_by_symbol"]

    rows: list[dict[str, str]] = []
    for packet in packet_rows:
        symbol = packet.get("research_symbol", "")
        venue_symbol = packet.get("venue_symbol", "")
        gate = gate_by_symbol.get(symbol, {})
        symbol_slug = venue_symbol.lower()
        paper_ref_stub = f"paper-rank2-{symbol_slug}-next-001"
        shadow_ref_stub = f"shadow-rank2-{symbol_slug}-next-001"
        rows.append(
            {
                "launch_priority": priority_by_symbol.get(symbol, "P9"),
                "research_symbol": symbol,
                "venue_symbol": venue_symbol,
                "dry_run_pass_trigger": gate.get("pass_transition", "eligible_for_shadow_parity_review only; still not tiny-live"),
                "shadow_review_ticket_stub": ticket.get("ticket_stub", "SL-PARITY-<paper_ref>-<yyyymmddhhmm>").replace("<paper_ref>", paper_ref_stub),
                "paper_ref_stub": paper_ref_stub,
                "live_shadow_ref_stub": shadow_ref_stub,
                "required_open_bundle": ticket.get("open_bundle", ""),
                "first_shadow_writeback": "paper_ref_id + live_shadow_ref_id + rounded_qty + cost_estimate_bps + mismatch_status=green",
                "green_closeout": ticket.get("success_closeout", ""),
                "red_closeout": ticket.get("fail_closeout", ""),
                "hard_stop": "仍只允许 shadow_parity；若缺 paper_ref / qty rounding / cost snapshot / whitelist / clock 对齐，继续 blocked，绝不进入 tiny-live。",
                "generated_at_utc": gate.get("generated_at_utc", status.get("generated_at_utc", "")),
            }
        )

    rows.sort(key=lambda r: r["launch_priority"])
    return rows


def write_rank2_shadow_parity_launch_packet_csv(rows: list[dict[str, str]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with SMALL_LIVE_RANK2_SHADOW_PARITY_LAUNCH_PACKET_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "launch_priority",
                "research_symbol",
                "venue_symbol",
                "dry_run_pass_trigger",
                "shadow_review_ticket_stub",
                "paper_ref_stub",
                "live_shadow_ref_stub",
                "required_open_bundle",
                "first_shadow_writeback",
                "green_closeout",
                "red_closeout",
                "hard_stop",
                "generated_at_utc",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def get_rank2_shadow_parity_starter_rows() -> list[dict[str, str]]:
    launch_rows = get_rank2_shadow_parity_launch_packet_rows()
    rows: list[dict[str, str]] = []
    for launch in launch_rows:
        rows.append(
            {
                "launch_priority": launch["launch_priority"],
                "research_symbol": launch["research_symbol"],
                "venue_symbol": launch["venue_symbol"],
                "shadow_review_ticket_stub": launch["shadow_review_ticket_stub"],
                "paper_ref_id_stub": launch["paper_ref_stub"],
                "live_shadow_ref_id_stub": launch["live_shadow_ref_stub"],
                "stage_status": "shadow_parity",
                "mismatch_status": "green_when_first_row_lands",
                "operator_action": "continue_shadow_review",
                "minimum_writeback": "paper_ref_id + live_shadow_ref_id + rounded_qty + cost_estimate_bps + mismatch_status=green",
                "pending_fields_before_closeout": "rounded_qty=<fill_after_qty_rounding>; cost_estimate_bps=<fill_after_shadow_snapshot>",
                "hard_boundary": "若 rounded_qty / cost / whitelist / clock 任一未过关，就不要用这张 starter row 冒充 green closeout；必须回到 parity_red / freeze_review。",
                "generated_at_utc": launch["generated_at_utc"],
            }
        )
    return rows


def write_rank2_shadow_parity_starter_rows_csv(rows: list[dict[str, str]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with SMALL_LIVE_RANK2_SHADOW_PARITY_STARTER_ROWS_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "launch_priority",
                "research_symbol",
                "venue_symbol",
                "shadow_review_ticket_stub",
                "paper_ref_id_stub",
                "live_shadow_ref_id_stub",
                "stage_status",
                "mismatch_status",
                "operator_action",
                "minimum_writeback",
                "pending_fields_before_closeout",
                "hard_boundary",
                "generated_at_utc",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def get_rank2_next_status_change_gate_rows() -> list[dict[str, str]]:
    status_rows = read_csv_rows(SMALL_LIVE_RANK2_STATUS_SNAPSHOT_PATH)
    launch_rows = read_csv_rows(SMALL_LIVE_RANK2_SHADOW_PARITY_LAUNCH_PACKET_PATH)
    starter_rows = read_csv_rows(SMALL_LIVE_RANK2_SHADOW_PARITY_STARTER_ROWS_PATH)
    status = status_rows[0] if status_rows else {}
    generated = status.get("generated_at_utc", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
    return [
        {
            "gate_order": "1",
            "gate_name": "当前唯一会改变状态的动作",
            "current_state": status.get("current_hard_verdict", "paper_candidate_only / blocked"),
            "what_counts": status.get("next_allowed_action", "only one real test/no-fill receipt-chain replay on BTC/ETH/SOL whitelist"),
            "what_does_not_count": "再补 launch packet / starter row / review wording / operator packet 近义页，都不算 status change。",
            "why": "Rank 2 现在缺的不是字段模板，而是同一条 whitelist-bound replay 的真实 intent/ack/cancel(close) refs；没有真实 refs，state 不会从 blocked 变成 eligible_for_shadow_parity_review。",
            "evidence_ready_today": f"launch_packet_rows={len(launch_rows)}; starter_rows={len(starter_rows)}; 第一条 shadow_parity green row 所需 paper_ref/live_shadow_ref/qty/cost 占位字段已齐。",
            "next_queue_if_done": "eligible_for_shadow_parity_review -> shadow_parity only",
            "generated_at_utc": generated,
        },
        {
            "gate_order": "2",
            "gate_name": "为什么当前默认不再继续补 doc-chain",
            "current_state": status.get("closeout_state", "dry_run_only"),
            "what_counts": "只允许 operator 真跑一次 whitelist-bound replay，并把真实 refs 回填进同一 receipt-chain log / audit。",
            "what_does_not_count": "新增 closeout copy、重复写 no-default-append 边界、或继续预写更多 green sample rows。",
            "why": "starter rows 已把 replay 成功后的第一条 shadow_parity green row 最小字段压成可照抄模板；继续写更多相邻文档不会再减少真实 blocker。",
            "evidence_ready_today": "small_live_rank2_shadow_parity_launch_packet_v1.csv + small_live_rank2_shadow_parity_starter_rows_v1.csv",
            "next_queue_if_done": "若 replay 失败 -> routing_dry_run_replay；若 replay 成功 -> shadow_parity review",
            "generated_at_utc": generated,
        },
    ]


def write_rank2_next_status_change_gate_csv(rows: list[dict[str, str]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with SMALL_LIVE_RANK2_NEXT_STATUS_CHANGE_GATE_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "gate_order",
                "gate_name",
                "current_state",
                "what_counts",
                "what_does_not_count",
                "why",
                "evidence_ready_today",
                "next_queue_if_done",
                "generated_at_utc",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def get_rank2_next_replay_bundle_rows() -> list[dict[str, str]]:
    receipt_rows = get_rank2_receipt_audit_rows()
    runsheet_rows = get_rank2_replay_runsheet_rows()
    closeout_rows = get_rank2_replay_closeout_matrix_rows()
    launch_rows = get_rank2_shadow_parity_launch_packet_rows()
    if not receipt_rows or not runsheet_rows or not closeout_rows or not launch_rows:
        return []

    receipt = receipt_rows[0]
    runsheet = runsheet_rows[0]
    closeout = closeout_rows[0]
    launch = launch_rows[0]
    return [
        {
            "bundle_order": receipt.get("audit_order", "P9"),
            "research_symbol": receipt.get("research_symbol", ""),
            "venue_symbol": receipt.get("venue_symbol", ""),
            "why_this_leg_now": runsheet.get("why_this_order", ""),
            "sample_notional_usdt": receipt.get("suggested_notional_for_25bps_usdt", ""),
            "sample_budget_read": receipt.get("sample_50u_budget_read", ""),
            "replay_action": runsheet.get("operator_action", ""),
            "must_capture_refs": runsheet.get("must_capture_refs", ""),
            "current_log_stub": runsheet.get("current_log_stub", ""),
            "if_pass": closeout.get("pass_closeout", ""),
            "if_fail": closeout.get("fail_closeout", ""),
            "parity_ticket_stub_if_pass": launch.get("shadow_review_ticket_stub", ""),
            "hard_stop": closeout.get("hard_stop", ""),
            "generated_at_utc": closeout.get("generated_at_utc", launch.get("generated_at_utc", "")),
        }
    ]


def write_rank2_next_replay_bundle_csv(rows: list[dict[str, str]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with SMALL_LIVE_RANK2_NEXT_REPLAY_BUNDLE_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "bundle_order",
                "research_symbol",
                "venue_symbol",
                "why_this_leg_now",
                "sample_notional_usdt",
                "sample_budget_read",
                "replay_action",
                "must_capture_refs",
                "current_log_stub",
                "if_pass",
                "if_fail",
                "parity_ticket_stub_if_pass",
                "hard_stop",
                "generated_at_utc",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def get_rows() -> list[dict[str, str]]:
    return [
        {
            "priority": "bench",
            "title": "V3 final verdict / breakout-short follow-up",
            "status": "bench：一次性 hard verdict 已同步；当前仍只能诚实地读成 up-flat biased conditional alpha / cached evidence challenger，不再占用默认主资源",
            "role": "保留历史证据与条件性 alpha 读法，但默认退出 Live Seat 主资源竞争，等待 genuinely new blocker reduction 再申请重开",
            "admission": "bench",
            "evidence": "v3 最终收口后留下 `support_breakout_raw / confirm_1 @ h24`；其中最朴素的 `support_breakout_raw @ h24` v0 页面仍有 48 笔、平均单笔约 +1.44%、累计约 +92.45%。更关键的是，最近几轮已把 realism / sizing / shadow honesty 压到更硬的 desk 口径：`20bps` 下 raw 的 per-asset / entry-only equal-weight / hourly portfolio path / 1-slot global 约为 `75.03% / 19.40% / 14.04% / 13.83%`；把 `avoid_fluctuating` 放进同一套 hourly path 后，overall hourly path 约提到 `15.46%`、max drawdown 约改善到 `-9.97%`；再对 `ETH+SOL` 两仓小时做 `0.5x` halfsize，hourly path 可进一步到约 `19.90%`、max drawdown 约收窄到 `-9.04%`。这些都证明 breakout 不是零信息噪音，而是有条件性的 alpha 线索。但 desk 现在更看重能不能继续减少 blocker，而不是继续重复同一样本上的漂亮切片。上一轮已沿 cached latest evidence 落下一次性 hard verdict artifact：`breakout_live_seat_hard_verdict_20260316_0624.csv`。其中关键 blocker 仍保持不变：`pure_down=0/100`、`predown_bridge_12h=0/11`、`downrisk_48h=0/109`、`future_pure_down_48h=0/44`。换句话说，这条线虽然保留了 conditional alpha 价值，但在 desk 资源排序上，已经完成了“最后一枪后仍未降 blocker”的收口条件。",
            "not_yet": "这条线当前不该再继续写成 `one_more_gate`，更不该伪装成 ‘再多切一刀也许就能上 shadow/live’。真正的问题已经压成一组很具体的 blocker：默认 `ETH+SOL pair-conditioned halfsize` 虽能改善 path，但对 pure `down` 的覆盖仍是 `0/100`，`48h down-risk zone` 仍是 `0/109`，policy 自己命中的小时在未来 `48h` 里接上 pure `down` 的也仍是 `0/44`。这说明当前样本里并没有新的 blocker reduction 证据，而不是还差一页解释。既然 Live Seat 的“唯一一枪”已经打过，且 hard verdict 仍没有把这些数字压下去，继续把它挂在默认主资源位只会变成近义续命。",
            "next": "下一步默认不是继续在 breakout 上重跑同类 rerun，而是把默认 bot3 主资源让给 Scout Seat 与 tiny-live plumbing。breakout 这条线从现在起只保留两种重开条件：一是未来拿到 genuinely new `pure-test / down-tail` blocker reduction；二是 Scout Seat 产出更强 challenger 后，再回头做替换比较。换句话说，这页现在要表达的不是‘它下一刀该怎么继续切’，而是‘它为什么被 bench，以及什么证据才配让它回来’。",
            "main_link": "../support_breakout_v0_h24/report.html",
            "main_label": "打开 breakout v0 原型页",
            "side_link": "../pytrendline_event_validation_v3_final_verdict/report.html",
            "side_label": "打开 v3 final verdict",
            "tone": "park",
        },
        {
            "priority": "archive",
            "title": "Fibonacci confirmation / retest_hold",
            "status": "park / archive：正式收口，降级为 optional filter candidate / archived idea",
            "role": "当前不再当主 alpha 推进；只保留为小过滤器备选",
            "admission": "park",
            "evidence": "它确实能改善一部分‘被打脸率 / invalidation’问题，也曾在某些切片里比 baseline 更平衡；但一旦放到 breakout v0 的同样本 A/B，对主线最关键的问题——‘有没有更值得保留为主策略’——答案是没有。",
            "not_yet": "不能继续包装成通用 alpha enhancer。A/B 页显示：`breakout + fib retest_hold` 的平均单笔约 +0.71%、累计约 +20.00%，明显弱于裸 `breakout v0`，而且平均入场还延迟约 12.5 根 bar。",
            "next": "网页上把它改成清晰的 archived/filter 结论页；如果以后再看，只问一个更窄的问题：在更明确的 down regime 里，它能不能当小过滤器。",
            "main_link": "../support_breakout_v0_fib_ab/report.html",
            "main_label": "打开 Fib A/B 收口页",
            "side_link": "../fibonacci_retest_hold_long/report.html",
            "side_label": "打开 Fib 扩展回测页",
            "tone": "park",
        },
        {
            "priority": "#1",
            "title": "EMA / PSAR raw alpha focus",
            "status": "closest to paper：EMA baseline family 已有 paper-trading candidate spec + operating spec + monitoring board + runbook，并已落下首份 day-0 ledger snapshot + first-refresh queue；A股 daily primary/shadow refresh 也已切到 live source，当前账本是在按时等待下一次 market-close refresh，而 PSAR overlay 现已被收紧成 `创业板ETF 1d` 的 narrow shadow-protective protocol",
            "role": "EMA = 主 raw alpha baseline / paper candidate；PSAR = 只配 `创业板ETF 1d` sidecar shadow-protective 观察位，不是默认 runbook overlay",
            "admission": "closest to paper",
            "evidence": "这条线现在已经不只收成 final survivor map，还进一步压成了一版 deployment-facing 的 `paper-trading candidate spec + operating spec + monitoring board + runbook`。真实结果切片显示：`EMA 60m crypto` 在 `BTC / ETH / SOL` 的 rolling falsification 下已是明确 fail pocket——gross 正窗口仅 `4/30`、扣 `20bps` 后只剩 `2/30`，且 `0/3` 资产达到“多数窗口 net 为正”；进一步叠加 `PSAR exit overlay` 后，net 正窗口反而掉到 `0/30`，median window net20 delta 约 `-6.26pp`。同时，A股 frontier 的 strict holdout 也把 family 边界压清：`A股 weekly` 应移出 EMA family——两格 weekly pocket 共 `14` 个 holdout，`EMA` 正 holdout 占比仅约 `42.86%`，低于 `PSAR` 的约 `85.71%`；但 `A股 daily` 还没一起塌掉——两格 daily pocket 共 `16` 个 holdout，`EMA` 正 holdout 占比约 `62.50%`，高于 `PSAR` 的约 `43.75%`，其中 `创业板ETF 1d` 的 `EMA` median net20 约 `12.05%`，仍明显高于 `PSAR` 的约 `5.13%`。更进一步，这版 spec 已明确：`创业板ETF 1d` 可作 primary paper pilot，`美股/crypto/贵州茅台 1d+1wk` 可作 secondary batch，`沪深300ETF 1d` 只保留 shadow，而 weekly frontier 与 crypto 60m 则直接排除；最新 monitoring board + runbook 则把这些口袋进一步压成 active / shadow / stoplist 的日常盯盘、刷新频率、升降级与 rollback 清单。现在又把这些规则真正落成了首份 `day-0 ledger snapshot`，并继续压成 `first-refresh queue`：固定的 `11` 条 day-0 rows 已按同一时刻写进账本，并分别带上 `paper_status / monitor_status / review_action / data_health`；其中 `创业板ETF 1d` 已明确记成 `start_primary_paper`，front-queue secondary 会在 day-0 就标成 `kickoff_yellow_front_queue` 等待优先复核，`沪深300ETF 1d` 只记成 `stay_shadow_until_promotion_gate`，stoplist 继续 `keep_excluded`；而 queue 又把首刷顺序写死为 primary 先、front-queue secondary 跟上、shadow refresh-only、stoplist audit-only。这说明 EMA 线已经不只是“paper-ready 文档”，而是首笔 `0` 真资金的 paper/shadow 记账动作和首轮执行顺序都已真正落表。最新又把 `创业板ETF 1d / 沪深300ETF 1d` 的 A股日频 refresh 从 frontier cache fallback 升成了可重复的 Eastmoney live source，所以 primary 与同组 shadow 现在默认不再卡在 A股 daily source-risk。最新又把 A股 daily 的 `EMA + PSAR exit overlay` 直接压到 runbook 口径：`创业板ETF 1d` 这格 primary pilot 约 `75%` 的 holdout 能改善 net20、median delta 约 `+2.00pp`，但 `沪深300ETF 1d` 这格 shadow 仅约 `25%` 改善、median delta 约 `-1.51pp`；两格合并后 overall 改善占比约 `50%`、median delta 约 `-0.38pp`。这说明 PSAR 当前最多只配留在 primary pocket 的 shadow protective 观察位，不能焊进 A股 daily 默认 runbook。",
            "not_yet": "这不等于 EMA baseline 已经被彻底坐实。当前 fixed boundary 只是把“谁该移出、谁还能保留、谁只能 mixed/watch”说清楚了；其中非前线 non60m backstops 目前主要还是靠长样本 gross/cost 支撑，还没全部经历和 A股 frontier 一样严格的 holdout 复核，所以不能把整条 family 重新吹成‘全面稳固’。同样，PSAR overlay 也还不能凭 `创业板ETF 1d` 这一个 primary pocket 的改善，就偷渡成整个 A股 daily 的默认 protective layer。",
            "next": "既然 `day-0 ledger snapshot + first-refresh queue` 都已经落表，且 A股 daily 的 primary / shadow source-risk 已显著下降，EMA 默认下一步就该按这张 queue 执行真实 forward refresh / week-1 review。当前更诚实的状态不是‘还缺一页说明’，而是 active `1d` ledger 正在按时等待下一次真实 market close；因此后续默认别再扩近义 board 页面，而是等下一根 completed bar 后继续写账。若还要补研究刀口，也只该围绕 `沪深300ETF 1d` 这种 mixed pocket 的升格诚实度，或抽查 secondary batch backstops 是否需要从 active_secondary_backstop 降回 shadow；`PSAR overlay` 则只保留在 `创业板ETF 1d` 的 shadow protocol 观察位，不改默认持有逻辑。",
            "main_link": "../ema_psar_raw_alpha/report.html",
            "main_label": "打开 EMA / PSAR 主页",
            "side_link": "../../reading/regime_switch_indicator_stack_replication/report.html",
            "side_label": "打开上游复现页",
            "tone": "good",
        },
    ]


def get_promotion_gate_rows() -> list[dict[str, str]]:
    return [
        {
            "stage": "Paper / shadow start",
            "who": "只适用于已过 Step 2 且已有 candidate spec + operating spec + monitoring board / runbook 的对象。当前更像先给 EMA 用；breakout 已退回 `bench`，若 future genuinely new blocker reduction 出现，再重新申请。",
            "min_forward": "先以 `0` 真资金启动；从第 1 天开始并行记 paper / shadow 账。若缺 runbook、监控字段、或 promote-demote 规则，则不得启动。",
            "drawdown": "启动阶段不谈真钱回撤容忍；核心要求是 forward 记账口径与监控字段先稳定跑起来。",
            "stop": "数据断流、执行规则不完整、或 monitoring board 无法日常更新时，不启动 / 立即暂停。",
            "capital": "`0`（paper / shadow only）。",
            "rollback": "不适用；未满足条件时继续留在 Step 3。",
        },
        {
            "stage": "Paper -> small-live review eligible",
            "who": "所有已进入 paper / shadow 的候选。",
            "min_forward": "至少满足 `30` 个自然日，且 `>=20` 个已关闭 decision cycles / trades；若策略更慢，则至少 `60` 个自然日 + `>=8` 个已关闭 trades。",
            "drawdown": "paper max drawdown 不得超过研究基线的 `max(1.25x, +3pp)` 容忍带；同时不能连续两次 review 都落在 monitoring board 的 `red` 区。",
            "stop": "若 paper 累计回撤跌破 `-5%`，或触发上述 drawdown guardrail，则冻结 promotion review，只保留 paper。",
            "capital": "仍为 `0`；这里只是拿到 small-live review 资格，不自动上真钱。",
            "rollback": "任一条件未达标，维持 / 退回 `paper only`，并按 monitoring board 标红。",
        },
        {
            "stage": "Small-live pilot start",
            "who": "只适用于已经通过 paper review 的对象。",
            "min_forward": "继续保留 paper 并行记账；small-live 只做最小 pilot，不取消 shadow。",
            "drawdown": "live 期间的 max drawdown 不得超过通过 review 时的 paper guardrail；若 live 与 paper 同步路径偏离超过 `5pp`，视为 execution mismatch。",
            "stop": "任一 kill switch 触发即停：`drawdown breach`、`live vs paper mismatch > 5pp`、`连续两次 red review`、`数据/执行异常`。",
            "capital": "单候选 live pilot 先限制在 `<= 总可部署资金 1%` 且 `<= 该策略 sleeve 10%`；单 symbol / pair 不得超过 pilot capital 的 `50%`。",
            "rollback": "任一 kill switch 触发，立即退回 `paper only`；问题修复前不得自动重启 live。",
        },
        {
            "stage": "Rollback / re-entry",
            "who": "所有已进入 live pilot 的候选。",
            "min_forward": "rollback 后至少再观察 `10` 个交易日或 `5` 个 closed trades（更慢系统取更长 calendar）后，才可重新申请 live review。",
            "drawdown": "rollback 后重新以新的 paper equity baseline 记账，不得用旧 live 高水位稀释本次失败。",
            "stop": "同一 candidate 若 `90` 天内两次触发 kill switch，自动降回 Step 3，等待人工重新立项，而不是自动二次尝试。",
            "capital": "rollback 期间真实资金 = `0`。",
            "rollback": "这是硬规则，不因单次反弹自动取消。",
        },
    ]


def write_promotion_gate_csv(rows: list[dict[str, str]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with PROMOTION_GATE_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["stage", "who", "min_forward", "drawdown", "stop", "capital", "rollback"],
        )
        writer.writeheader()
        writer.writerows(rows)


def get_small_live_plumbing_rows() -> list[dict[str, str]]:
    return [
        {
            "stage": "Routing dry-run / symbol whitelist lock",
            "venue_mode": "`0` 真资金；先在目标 venue 的 dry-run / test / no-fill 路径验证 symbol mapping、最小下单单位与时钟同步。",
            "capital_rule": "真实资金 = `0`；只允许 candidate spec 已批准的 symbol / pair 进入路由白名单。",
            "routing_rule": "同一条信号必须先产出 `intent -> route_ack -> cancel/close_ack` 三段回执；缺任一段就不允许进入 tiny-live。",
            "ledger_rule": "每次 dry-run 都写进同一张 live ledger：至少记录 `candidate / symbol / side / intended_qty / route_ts / ack_ts / cancel_ts / venue_mode`。",
            "mismatch_guard": "若 paper intent 与路由 payload 的 symbol / side / qty / timestamp 任一不一致，或时钟漂移 > `60s`，直接阻断。",
            "kill_switch": "连续 `1` 次 route_ack 缺失、qty 被 venue 强制改写、或 symbol mapping 漂移，即刻停在 dry-run，不升级。",
        },
        {
            "stage": "Paper-live shadow parity",
            "venue_mode": "继续 `0` 真资金；paper 与 live-shadow 并行，不发真实成交。",
            "capital_rule": "真实资金 = `0`；仅允许读取 paper candidate 的目标 notional 与 cap snapshot，不做真钱发送。",
            "routing_rule": "每条 paper 信号都生成一条 live-shadow payload，检查 price source、qty rounding、venue precision、pair whitelist 是否一致。",
            "ledger_rule": "同一行 ledger 必须同时留 `paper_ref_id / live_shadow_ref_id / intended_notional / cap_pct_total / cap_pct_sleeve / shadow_price`。",
            "mismatch_guard": "若 live-shadow 与 paper 同步路径偏离 > `1 bar` 或同笔预估成本偏离 > `25bps`，标记 `parity_red`。",
            "kill_switch": "连续 `2` 次 `parity_red`、或出现 data gap / precision mismatch 未解释，继续留在 paper，不升级。",
        },
        {
            "stage": "Tiny-live pilot start",
            "venue_mode": "只适用于已通过 paper review 的候选；paper 与 live 并行记账，live 只做最小 pilot。",
            "capital_rule": "沿用项目级硬上限：单候选 `<= 总可部署资金 1%` 且 `<= sleeve 10%`；单 symbol / pair `<= pilot capital 50%`。",
            "routing_rule": "只允许白名单 symbol；每笔 live 下单前先检查 `remaining_cap / min_notional / venue_precision / cooldown`。",
            "ledger_rule": "每笔 live 必须与 paper row 成对：新增 `live_order_id / fill_price / fill_qty / slippage_bps / remaining_cap / mismatch_status`。",
            "mismatch_guard": "若 live 与 paper 同步路径偏离 > `5pp`、或出现未解释滑点 > `50bps`，视为 execution mismatch。",
            "kill_switch": "任一触发即停：`drawdown breach`、`capital breach`、`live vs paper mismatch > 5pp`、`连续两次 red review`、`数据/执行异常`。",
        },
        {
            "stage": "Rollback / re-entry",
            "venue_mode": "kill switch 后立即回到 `paper only`；live 资金归零。",
            "capital_rule": "真实资金 = `0`；未完成复盘前不得自动恢复 live。",
            "routing_rule": "先冻结白名单与路由开关；修复后也必须先重走 dry-run -> shadow parity。",
            "ledger_rule": "rollback 行必须记录 `trigger_reason / trigger_ts / exposure_zeroed_ts / reopen_earliest_ts / operator_note`。",
            "mismatch_guard": "rollback 后至少再观察 `10` 个交易日或 `5` 个 closed trades；不得用旧 live 高水位稀释本次失败。",
            "kill_switch": "同一 candidate 若 `90` 天内两次触发 kill switch，自动降回 Step 3，等待人工重新立项。",
        },
    ]


def write_small_live_plumbing_csv(rows: list[dict[str, str]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with SMALL_LIVE_PLUMBING_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "stage",
                "venue_mode",
                "capital_rule",
                "routing_rule",
                "ledger_rule",
                "mismatch_guard",
                "kill_switch",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def get_small_live_ledger_rows() -> list[dict[str, str]]:
    return [
        {
            "field_order": "1",
            "field_name": "candidate_id / deployment_scope",
            "required_stage": "dry-run / shadow parity / tiny-live / rollback",
            "fill_rule": "只允许引用已批准 candidate spec 里的候选与 scope；例如 `EMA-paper-primary`、`breakout-live-challenger`，不得临时手写新 scope。",
            "red_flag": "账本行若无法映射回已批准候选，或同一策略被写成多个随意别名，直接阻断。",
            "why_it_matters": "先把 live row 和研究 admission scope 锁死，避免 paper/live 混账。",
        },
        {
            "field_order": "2",
            "field_name": "stage_status",
            "required_stage": "all rows",
            "fill_rule": "只能填 `dry_run` / `shadow_parity` / `tiny_live` / `rollback` 四类之一；状态切换必须按顺序前进。",
            "red_flag": "若出现跳过 `dry_run`/`shadow_parity` 直接写 `tiny_live`，或 kill switch 后未落 `rollback` 行，直接判流程失真。",
            "why_it_matters": "把 operator 流程写进账本，而不是只靠口头记忆当前跑到哪一步。",
        },
        {
            "field_order": "3",
            "field_name": "paper_ref_id / signal_bar_utc",
            "required_stage": "shadow parity / tiny-live / rollback",
            "fill_rule": "每笔 shadow/live 都必须能追溯到对应的 paper 信号行与触发 bar；dry-run 可先留空 paper_ref，但必须记录 signal bar。",
            "red_flag": "若 live 行找不到对应 paper row，或 bar 时间与 paper 偏离 > `1 bar` 仍未解释，直接标 `mismatch_red`。",
            "why_it_matters": "这是 `paper vs live` 同步审计的主键；没有它就无法判断 execution mismatch。",
        },
        {
            "field_order": "4",
            "field_name": "research_symbol / venue_symbol / side",
            "required_stage": "dry-run / shadow parity / tiny-live",
            "fill_rule": "同时记录研究口径 symbol 与 venue 实际路由 symbol，并写明方向；只允许白名单 pair。",
            "red_flag": "symbol mapping 含糊、pair 不在白名单、或 venue_symbol 与 research_symbol 未对齐时，直接阻断发送。",
            "why_it_matters": "crypto live 最容易在 symbol mapping 和合约命名上出错，这列是第一道防呆。",
        },
        {
            "field_order": "5",
            "field_name": "route_intent_ts_utc / route_ack_ts_utc / ack_latency_ms",
            "required_stage": "dry-run / shadow parity / tiny-live",
            "fill_rule": "每次路由都要成对记录 intent 与 ack 时间，并回填延迟；没有 ack 就不能假装‘已发出’。",
            "red_flag": "缺 `route_ack_ts_utc`、或时钟漂移 > `60s`、或 ack latency 异常却无说明，直接停在当前阶段。",
            "why_it_matters": "把 routing dry-run 从一句‘测过了’变成可审计回执。",
        },
        {
            "field_order": "6",
            "field_name": "intended_notional_usd / cap_pct_total / cap_pct_sleeve / remaining_cap_pct",
            "required_stage": "shadow parity / tiny-live",
            "fill_rule": "按当前项目级 cap 规则同步记录目标 notional、占总资金比例、占 sleeve 比例与剩余容量。",
            "red_flag": "任何一列缺失、或超过 `<=总可部署资金1%` / `<=sleeve10%` / `单 pair <= pilot 50%`，直接触发 capital breach。",
            "why_it_matters": "让 capital cap 不再只是 policy，而是每笔都能核对的硬字段。",
        },
        {
            "field_order": "7",
            "field_name": "intended_qty / rounded_qty / min_notional_check",
            "required_stage": "shadow parity / tiny-live",
            "fill_rule": "先写策略想下的数量，再写 venue rounding 后数量，并记录是否通过最小下单单位 / 最小名义金额检查。",
            "red_flag": "若 rounding 后数量偏离 intended 太多、或 min_notional 未通过却仍下发，直接停机。",
            "why_it_matters": "很多 crypto live mismatch 不是方向错，而是数量被交易所精度规则 silently 改写。",
        },
        {
            "field_order": "8",
            "field_name": "shadow_price / fill_price / fill_qty",
            "required_stage": "shadow parity / tiny-live",
            "fill_rule": "shadow 阶段至少留 `shadow_price`；tiny-live 阶段必须补 `fill_price / fill_qty`。",
            "red_flag": "有 route ack 却没有 shadow/fill 价格，或 fill_qty 与 rounded_qty 明显不符却没解释，直接标红。",
            "why_it_matters": "没有价格与成交量，就无法算后续偏差、滑点与剩余容量。",
        },
        {
            "field_order": "9",
            "field_name": "cost_estimate_bps / slippage_bps",
            "required_stage": "shadow parity / tiny-live",
            "fill_rule": "shadow 阶段记录预估成本；tiny-live 阶段补真实滑点。",
            "red_flag": "若 live 出现未解释滑点 > `50bps`，或 shadow 预估与 live 实际偏离持续 > `25bps`，直接触发 mismatch review。",
            "why_it_matters": "这列把 ‘crypto live mismatch’ 从感觉不对变成量化阈值。",
        },
        {
            "field_order": "10",
            "field_name": "mismatch_status / mismatch_reason",
            "required_stage": "shadow parity / tiny-live / rollback",
            "fill_rule": "统一写 `ok` / `yellow` / `red`，并在非 `ok` 时补一句原因，如 `clock_drift`、`precision_gap`、`slippage_spike`。",
            "red_flag": "若出现 `parity_red` 或 `execution_mismatch` 却没有原因与后续动作，说明账本不可审计。",
            "why_it_matters": "这是把 mismatch guard 真接进 operator 流程的核心状态列。",
        },
        {
            "field_order": "11",
            "field_name": "operator_action / live_order_id",
            "required_stage": "shadow parity / tiny-live / rollback",
            "fill_rule": "记录本次动作是 `hold` / `send` / `cancel` / `rollback`；若进入 tiny-live，还必须有 `live_order_id`。",
            "red_flag": "若账本写了 tiny-live 但没有订单引用，或标了 rollback 却没执行动作，直接视为流程断链。",
            "why_it_matters": "让审计能直接回答：这笔信号最后到底有没有真的被路由/撤单/回滚。",
        },
        {
            "field_order": "12",
            "field_name": "trigger_reason / reopen_earliest_ts / operator_note",
            "required_stage": "rollback rows",
            "fill_rule": "一旦 kill switch 触发，必须补这三列：为什么触发、最早何时可重开、操作员备注。",
            "red_flag": "若 rollback 行缺原因或重开时间，说明 future run 可能会无约束重启 live。",
            "why_it_matters": "把 rollback / re-entry 也纳入同一张 ledger，避免失败被静默覆盖。",
        },
    ]


def write_small_live_ledger_csv(rows: list[dict[str, str]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with SMALL_LIVE_LEDGER_TEMPLATE_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "field_order",
                "field_name",
                "required_stage",
                "fill_rule",
                "red_flag",
                "why_it_matters",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def get_small_live_routing_dry_run_rows() -> list[dict[str, str]]:
    return [
        {
            "step_order": "1",
            "step_name": "白名单候选冻结",
            "required_input": "candidate spec / deployment_scope / 允许交易的 research_symbol 清单",
            "pass_rule": "只允许已批准 candidate 与白名单 pair 进入 dry-run；未批准 symbol 不生成路由 payload。",
            "block_on_fail": "candidate_id、deployment_scope 或 symbol whitelist 任一缺失 / 临时手写，直接停在 dry-run 前。",
            "ledger_fields": "candidate_id / deployment_scope、research_symbol / venue_symbol / side",
        },
        {
            "step_order": "2",
            "step_name": "venue symbol / precision 映射快照",
            "required_input": "venue_symbol、lot size、tick size、min_notional、price source timestamp",
            "pass_rule": "研究 symbol 与 venue symbol 一一映射，数量精度 / 最小名义金额规则已落快照。",
            "block_on_fail": "symbol mapping 含糊、precision 缺失、或 min_notional 无法提前校验，直接阻断发送。",
            "ledger_fields": "research_symbol / venue_symbol / side、intended_qty / rounded_qty / min_notional_check",
        },
        {
            "step_order": "3",
            "step_name": "intent → ack → cancel/close 回执链",
            "required_input": "route_intent_ts_utc、route_ack_ts_utc、cancel_ts 或 close_ack_ts、venue_mode=test/no-fill",
            "pass_rule": "同一条 dry-run 必须完整留下 intent、ack、cancel/close 三段回执；无真实成交。",
            "block_on_fail": "任一回执缺失、或 venue_mode 不是 dry-run / test / no-fill，直接停机，不进入下一阶段。",
            "ledger_fields": "route_intent_ts_utc / route_ack_ts_utc / ack_latency_ms、operator_action / live_order_id",
        },
        {
            "step_order": "4",
            "step_name": "时钟 / bar 对齐审计",
            "required_input": "signal_bar_utc、paper_ref_id（若已有）、venue clock、price source clock",
            "pass_rule": "paper intent 与路由 payload 的 bar / timestamp 对齐，clock drift <= 60s。",
            "block_on_fail": "bar 对齐偏差 > 1 bar，或 clock drift > 60s 未解释，直接标记 mismatch_red。",
            "ledger_fields": "paper_ref_id / signal_bar_utc、mismatch_status / mismatch_reason",
        },
        {
            "step_order": "5",
            "step_name": "数量舍入 / 资金占用预检",
            "required_input": "intended_notional_usd、cap_pct_total、cap_pct_sleeve、remaining_cap_pct、rounded_qty",
            "pass_rule": "dry-run 前先验证 rounding 后数量仍在资金上限内，且通过 min_notional 检查。",
            "block_on_fail": "rounded_qty 偏离 intended 太多、capital cap 超限、或 min_notional 未过仍试图路由，直接阻断。",
            "ledger_fields": "intended_notional_usd / cap_pct_total / cap_pct_sleeve / remaining_cap_pct、intended_qty / rounded_qty / min_notional_check",
        },
        {
            "step_order": "6",
            "step_name": "同账本留痕 + 红旗动作",
            "required_input": "同一张 live ledger row、mismatch_status、operator_action、operator_note",
            "pass_rule": "每次 dry-run 都在同一张 live ledger 留痕，并明确写出 `hold` / `cancel` 等 operator 动作。",
            "block_on_fail": "dry-run 结果只出现在终端 / 日志、没有落 ledger，或红旗没有对应动作，视为流程不可审计。",
            "ledger_fields": "mismatch_status / mismatch_reason、operator_action / live_order_id、trigger_reason / reopen_earliest_ts / operator_note",
        },
    ]


def write_small_live_routing_dry_run_csv(rows: list[dict[str, str]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with SMALL_LIVE_ROUTING_DRY_RUN_CHECKLIST_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "step_order",
                "step_name",
                "required_input",
                "pass_rule",
                "block_on_fail",
                "ledger_fields",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def get_small_live_routing_dry_run_sample_rows() -> list[dict[str, str]]:
    return [
        {
            "row_kind": "routing_dry_run_green_example",
            "candidate_id": "future-crypto-live-challenger",
            "deployment_scope": "dry_run_only",
            "stage_status": "dry_run",
            "signal_bar_utc": "2026-03-16 07:32:00 UTC",
            "research_symbol": "ETHUSDT",
            "venue_symbol": "ETH-USDT-SWAP",
            "side": "short",
            "venue_mode": "test/no-fill",
            "route_intent_ts_utc": "2026-03-16 07:38:12 UTC",
            "route_ack_ts_utc": "2026-03-16 07:38:13 UTC",
            "cancel_ts_utc": "2026-03-16 07:38:17 UTC",
            "ack_latency_ms": "880",
            "intended_notional_usd": "50.00",
            "cap_pct_total": "0.30%",
            "cap_pct_sleeve": "3.00%",
            "remaining_cap_pct": "97.00%",
            "intended_qty": "0.0250",
            "rounded_qty": "0.0250",
            "min_notional_check": "pass",
            "mismatch_status": "green",
            "mismatch_reason": "none",
            "operator_action": "cancel_after_ack",
            "operator_note": "示例 row：同一条 dry-run 已完整留下 intent->ack->cancel 回执，symbol/precision/cap 检查通过，但 venue_mode 仍是 test/no-fill，不代表 tiny-live 已放行。",
        }
    ]


def write_small_live_routing_dry_run_sample_row_csv(rows: list[dict[str, str]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with SMALL_LIVE_ROUTING_DRY_RUN_SAMPLE_ROW_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "row_kind",
                "candidate_id",
                "deployment_scope",
                "stage_status",
                "signal_bar_utc",
                "research_symbol",
                "venue_symbol",
                "side",
                "venue_mode",
                "route_intent_ts_utc",
                "route_ack_ts_utc",
                "cancel_ts_utc",
                "ack_latency_ms",
                "intended_notional_usd",
                "cap_pct_total",
                "cap_pct_sleeve",
                "remaining_cap_pct",
                "intended_qty",
                "rounded_qty",
                "min_notional_check",
                "mismatch_status",
                "mismatch_reason",
                "operator_action",
                "operator_note",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def get_small_live_operator_reconciliation_rows() -> list[dict[str, str]]:
    return [
        {
            "step_order": "1",
            "operator_phase": "dry-run green row 先落账",
            "source_artifact": "small_live_routing_dry_run_sample_row_v1.csv",
            "what_to_check": "先确认 route_intent / route_ack / cancel 三段回执完整，且 venue_mode 仍是 test/no-fill，不把 dry-run 误读成 live。",
            "pass_output": "保留一条 green dry_run row，并把 candidate 维持在 dry_run_only。",
            "fail_output": "若 ack 缺失、cancel 缺失、或 symbol/precision/cap 未过，则停在 routing review，不进入 shadow parity。",
            "ledger_anchor": "signal_bar_utc / route_intent_ts_utc / route_ack_ts_utc / cancel_ts_utc / operator_action",
        },
        {
            "step_order": "2",
            "operator_phase": "paper_ref 与 shadow payload 对齐",
            "source_artifact": "paper_live_shadow_parity_checklist_v1.csv",
            "what_to_check": "把同一条 paper 信号绑定到唯一 live-shadow payload，检查 symbol / side / qty rounding / cost snapshot / clock drift。",
            "pass_output": "允许生成一条新的 shadow parity row，并继续做成本/数量 parity 审计。",
            "fail_output": "任一 payload、clock、qty、cost 失真就记 parity_red；不得跳过 shadow 审计直接讨论 tiny-live。",
            "ledger_anchor": "paper_ref_id / live_shadow_ref_id / rounded_qty / cost_estimate_bps / mismatch_status",
        },
        {
            "step_order": "3",
            "operator_phase": "parity_red 时按硬分支处理",
            "source_artifact": "small_live_parity_red_action_ladder_v1.csv + small_live_shadow_parity_sample_row_v1.csv",
            "what_to_check": "看到 red row 后，必须按 mismatch_reason 选择 hold / cancel_or_no_send / escalate / freeze review，而不是口头说‘先等等看’。",
            "pass_output": "red row 留下清楚 trigger_reason、operator_action 与 reopen_earliest_ts，形成可审计冻结状态。",
            "fail_output": "若 red 只出现在日志里、没有账本动作，视为流程失真；candidate 保持 paper only。",
            "ledger_anchor": "mismatch_reason / operator_action / trigger_reason / reopen_earliest_ts / operator_note",
        },
        {
            "step_order": "4",
            "operator_phase": "reopen gate 逐条过关",
            "source_artifact": "small_live_reopen_gate_checklist_v1.csv",
            "what_to_check": "只有 cooldown 到点、root-cause 被单独关单、并重走一次最小 routing receipt 后，才配讨论重开。",
            "pass_output": "允许新开一条 green shadow parity row，恢复 shadow review。",
            "fail_output": "任一条件未满足都继续 freeze review；reopen_earliest_ts 不是自动赦免。",
            "ledger_anchor": "operator_note / route_intent_ts_utc / route_ack_ts_utc / mismatch_status",
        },
        {
            "step_order": "5",
            "operator_phase": "green resume row 接回同一审计链",
            "source_artifact": "small_live_reopen_resume_sample_row_v1.csv",
            "what_to_check": "恢复行必须显式引用 prior_red_ref_id，并把新的 paper_ref / shadow_ref / qty / cost / operator_action 一次落齐。",
            "pass_output": "账本形成 red -> reopen -> green 的闭环，candidate 才算恢复到 resume_shadow_review。",
            "fail_output": "若恢复行与 prior red 脱节，或只写‘已恢复’不写引用，视为审计链断裂，不能推进 tiny-live review。",
            "ledger_anchor": "prior_red_ref_id / paper_ref_id / live_shadow_ref_id / cost_estimate_bps / operator_action",
        },
    ]


def write_small_live_operator_reconciliation_csv(rows: list[dict[str, str]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with SMALL_LIVE_OPERATOR_RECONCILIATION_SEQUENCE_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "step_order",
                "operator_phase",
                "source_artifact",
                "what_to_check",
                "pass_output",
                "fail_output",
                "ledger_anchor",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def get_small_live_operator_handoff_rows() -> list[dict[str, str]]:
    return [
        {
            "packet_order": "1",
            "review_state": "准备启动一次新的 venue / route review",
            "open_bundle": "small_live_routing_dry_run_checklist_v1.csv + small_live_routing_dry_run_sample_row_v1.csv + small_live_ledger_template_v1.csv",
            "operator_goal": "先确认 symbol whitelist、precision、intent->ack->cancel 回执链与 live ledger 主键字段都齐，再决定这次 review 只能停在 dry_run 还是能继续往 shadow parity 走。",
            "expected_writeback": "至少留下 1 条 green dry_run row；如果 ack / cancel 缺失或时钟漂移超阈值，就继续 `dry_run_only`，不得伪装成 shadow 通过。",
            "hard_stop": "只要 route receipt chain 不完整、candidate/scope 对不上，或 ledger 主键字段没写齐，就不允许打开下一张 shadow parity 卡。",
        },
        {
            "packet_order": "2",
            "review_state": "dry-run 已干净，准备核对 paper vs live-shadow",
            "open_bundle": "paper_live_shadow_parity_checklist_v1.csv + small_live_green_shadow_parity_sample_row_v1.csv",
            "operator_goal": "把同一条 paper 信号映射成唯一 live-shadow payload，并一次核对 qty rounding、cap、price snapshot 与 cost snapshot 是否都在允许带内。",
            "expected_writeback": "若全部过关，就写 1 条 `mismatch_status=green` 的 shadow parity row，并把 operator_action 固定成 `continue_shadow_review`。",
            "hard_stop": "只要 rounded_qty / cost / clock / whitelist 任一不合格，就不能把这次检查描述成‘影子侧基本没问题’。",
        },
        {
            "packet_order": "3",
            "review_state": "shadow parity 出现 red，需要冻结并等待重开",
            "open_bundle": "small_live_parity_red_action_ladder_v1.csv + small_live_shadow_parity_sample_row_v1.csv + small_live_reopen_gate_checklist_v1.csv",
            "operator_goal": "把 red 变成清楚的 `hold / escalate / freeze review` 动作，并同时写清 reopen 最早时点与必须补齐的 root-cause 证据。",
            "expected_writeback": "至少留下 1 条 parity_red row，包含 `mismatch_reason / trigger_reason / reopen_earliest_ts / operator_note`；后续是否能重开，由 reopen gate 单独决定。",
            "hard_stop": "red 不能只留在日志里；若没有 ledger writeback 或没有明确 reopen 条件，就默认继续 `paper only`。",
        },
        {
            "packet_order": "4",
            "review_state": "red cause 已关闭，准备恢复 shadow review",
            "open_bundle": "small_live_reopen_gate_checklist_v1.csv + small_live_reopen_resume_sample_row_v1.csv + small_live_operator_reconciliation_sequence_v1.csv",
            "operator_goal": "确认 cooldown 到点、root-cause 已单独关单、并重新拿到干净 route receipt 后，再把恢复动作接回同一条审计链。",
            "expected_writeback": "写 1 条带 `prior_red_ref_id` 的 green resume row，把 candidate 恢复到 `resume_shadow_review`，而不是开一条与历史断开的新记录。",
            "hard_stop": "如果 prior_red_ref_id 缺失、route receipt 没重走、或新的 qty/cost parity 还没重新过关，就继续 freeze review。",
        },
    ]


def write_small_live_operator_handoff_csv(rows: list[dict[str, str]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with SMALL_LIVE_OPERATOR_HANDOFF_PACKET_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "packet_order",
                "review_state",
                "open_bundle",
                "operator_goal",
                "expected_writeback",
                "hard_stop",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def get_small_live_review_ticket_template_rows() -> list[dict[str, str]]:
    return [
        {
            "template_order": "1",
            "review_state": "新的 venue / route dry-run review",
            "ticket_stub": "SL-DRYRUN-<candidate>-<yyyymmddhhmm>",
            "required_refs": "candidate_id / deployment_scope、symbol whitelist snapshot、small_live_ledger_template 主键字段、dry-run intent->ack->cancel receipt ref",
            "open_bundle": "small_live_routing_dry_run_checklist_v1.csv + small_live_routing_dry_run_sample_row_v1.csv + small_live_operator_handoff_packet_v1.csv",
            "success_closeout": "至少绑定 1 条 green dry_run row ref，并把结论写成 `dry_run_pass -> eligible_for_shadow_parity_review`。",
            "fail_closeout": "若 ack/cancel 缺失、clock drift 超阈值或 candidate/scope 对不上，就把 ticket 关成 `dry_run_only / blocked`，不得口头推进到 shadow parity。",
        },
        {
            "template_order": "2",
            "review_state": "paper vs live-shadow parity review",
            "ticket_stub": "SL-PARITY-<paper_ref>-<yyyymmddhhmm>",
            "required_refs": "paper_ref_id、live_shadow_ref_id、shadow price snapshot、qty rounding / cap snapshot、paper_live_shadow_parity_checklist ref",
            "open_bundle": "paper_live_shadow_parity_checklist_v1.csv + small_live_green_shadow_parity_sample_row_v1.csv + small_live_operator_handoff_packet_v1.csv",
            "success_closeout": "绑定 1 条 `mismatch_status=green` 的 shadow parity row，并把结论写成 `continue_shadow_review`。",
            "fail_closeout": "若 rounded_qty / cost / clock / whitelist 任一不合格，就必须关成 `parity_red / freeze_review`，并留下 red row ref。",
        },
        {
            "template_order": "3",
            "review_state": "parity_red 冻结 / reopen 准备 review",
            "ticket_stub": "SL-RED-<candidate>-<yyyymmddhhmm>",
            "required_refs": "prior parity_red row、trigger_reason、reopen_earliest_ts、root-cause evidence ref、small_live_reopen_gate_checklist ref",
            "open_bundle": "small_live_parity_red_action_ladder_v1.csv + small_live_shadow_parity_sample_row_v1.csv + small_live_reopen_gate_checklist_v1.csv",
            "success_closeout": "把 ticket 关成 `freeze_review_with_reopen_gate`，并显式留下 reopen gate 所需的补件列表。",
            "fail_closeout": "若 red 只有日志没有 ledger writeback，或 reopen 条件没写清，就继续标 `paper_only / blocked`，不得默认可重开。",
        },
        {
            "template_order": "4",
            "review_state": "red cause 已关闭，恢复 shadow review",
            "ticket_stub": "SL-RESUME-<prior_red_ref>-<yyyymmddhhmm>",
            "required_refs": "prior_red_ref_id、reopen gate pass ref、最新 dry-run receipt ref、green resume row / operator reconciliation sequence ref",
            "open_bundle": "small_live_reopen_gate_checklist_v1.csv + small_live_reopen_resume_sample_row_v1.csv + small_live_operator_reconciliation_sequence_v1.csv",
            "success_closeout": "绑定 1 条带 `prior_red_ref_id` 的 green resume row，并把结论写成 `resume_shadow_review`。",
            "fail_closeout": "若 prior_red_ref_id 缺失、route receipt 没重走、或新的 qty/cost parity 仍未过关，就继续关成 `freeze_review`。",
        },
    ]


def write_small_live_review_ticket_template_csv(rows: list[dict[str, str]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with SMALL_LIVE_REVIEW_TICKET_TEMPLATE_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "template_order",
                "review_state",
                "ticket_stub",
                "required_refs",
                "open_bundle",
                "success_closeout",
                "fail_closeout",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def get_small_live_review_writeback_matrix_rows() -> list[dict[str, str]]:
    return [
        {
            "matrix_order": "1",
            "closeout_case": "dry_run_pass -> eligible_for_shadow_parity_review",
            "ticket_status": "closed_green",
            "minimum_writeback": "ticket_id、candidate_id / deployment_scope、dry_run_row_ref、route receipt ref、ack_latency_ms、close_reason=dry_run_pass",
            "same_ledger_or_registry": "在同一 review registry / ledger row 上补 `review_stage=dry_run`、`closeout_state=eligible_for_shadow_parity_review`、`next_queue=shadow_parity`。",
            "next_queue": "排入 shadow parity review；不得因为 ticket 关绿就直接跳 tiny-live。",
            "hard_stop": "若缺 dry_run row ref 或 route receipt 链不完整，只能回退 `dry_run_only / blocked`。",
        },
        {
            "matrix_order": "2",
            "closeout_case": "shadow parity green -> continue_shadow_review",
            "ticket_status": "closed_green",
            "minimum_writeback": "ticket_id、paper_ref_id、live_shadow_ref_id、green parity row ref、shadow_price / rounded_qty / cost_estimate_bps 快照、close_reason=parity_green",
            "same_ledger_or_registry": "同账本写 `review_stage=shadow_parity`、`mismatch_status=green`、`closeout_state=continue_shadow_review`，并保留 paper/live-shadow 主键配对。",
            "next_queue": "继续 shadow review 或等待 paper review 达到 small-live eligible；默认不直接切真钱。",
            "hard_stop": "若 paper/live_shadow 主键断裂、qty/cost 快照缺失，不能关绿。",
        },
        {
            "matrix_order": "3",
            "closeout_case": "shadow parity red -> freeze_review_with_reopen_gate",
            "ticket_status": "closed_red",
            "minimum_writeback": "ticket_id、parity_red row ref、trigger_reason、reopen_earliest_ts、root_cause_owner、close_reason=parity_red",
            "same_ledger_or_registry": "同账本写 `mismatch_status=red`、`operator_action=freeze_review`、`closeout_state=freeze_review_with_reopen_gate`，并绑定 prior red row。",
            "next_queue": "进入 root-cause / reopen gate 审计；停止新的 shadow parity 尝试。",
            "hard_stop": "如果 red 只有日志描述、却没有 red row / reopen ts writeback，就不能算真正 freeze。",
        },
        {
            "matrix_order": "4",
            "closeout_case": "freeze review 完成 -> reopen_ready",
            "ticket_status": "closed_yellow",
            "minimum_writeback": "ticket_id、prior_red_ref_id、reopen_gate_pass_ref、missing_docs_checklist、close_reason=reopen_gate_pass",
            "same_ledger_or_registry": "同账本写 `review_stage=reopen_gate`、`closeout_state=reopen_ready`、`next_queue=routing_dry_run_replay`，但 candidate 仍保持非 live。",
            "next_queue": "必须先重走 routing dry-run，再回 shadow parity；不允许从 freeze 直接跳到 resume green。",
            "hard_stop": "若 prior_red_ref_id / reopen_gate_pass_ref 任一缺失，只能继续 freeze_review。",
        },
        {
            "matrix_order": "5",
            "closeout_case": "resume green -> resume_shadow_review",
            "ticket_status": "closed_green",
            "minimum_writeback": "ticket_id、prior_red_ref_id、new dry_run receipt ref、green resume row ref、close_reason=resume_shadow_review",
            "same_ledger_or_registry": "同账本写 `review_stage=resume`、`mismatch_status=green`、`closeout_state=resume_shadow_review`，并把历史 red 链接到新的 green resume row。",
            "next_queue": "恢复 shadow review 连续性，等待后续 paper/live promotion review。",
            "hard_stop": "若没重走 receipt、或新的 qty/cost parity 仍未过关，就继续 freeze，不得口头宣布恢复。",
        },
    ]


def write_small_live_review_writeback_matrix_csv(rows: list[dict[str, str]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with SMALL_LIVE_REVIEW_WRITEBACK_MATRIX_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "matrix_order",
                "closeout_case",
                "ticket_status",
                "minimum_writeback",
                "same_ledger_or_registry",
                "next_queue",
                "hard_stop",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def get_small_live_review_registry_template_rows() -> list[dict[str, str]]:
    return [
        {
            "row_order": "1",
            "registry_row_kind": "dry_run review row",
            "required_keys": "ticket_id、candidate_id / deployment_scope、review_stage=dry_run、dry_run_row_ref、route_receipt_ref、opened_ts / closed_ts",
            "status_fields": "ticket_status=closed_green 或 blocked、closeout_state=eligible_for_shadow_parity_review / dry_run_only、next_queue=shadow_parity / routing_dry_run_replay",
            "evidence_links": "symbol whitelist snapshot、intent->ack->cancel receipt chain、ack_latency_ms、operator_note",
            "ready_for_next_queue": "只有 dry_run row ref 与 receipt chain 都齐，且 candidate/scope 未漂移时，才配排入 shadow_parity。",
            "hard_stop": "若只写了一句 dry-run 通过、却没有 row ref / receipt ref / next_queue，就不能算 registry closeout 完成。",
        },
        {
            "row_order": "2",
            "registry_row_kind": "shadow parity green row",
            "required_keys": "ticket_id、paper_ref_id、live_shadow_ref_id、review_stage=shadow_parity、green_parity_row_ref、candidate_id、closed_ts",
            "status_fields": "ticket_status=closed_green、mismatch_status=green、closeout_state=continue_shadow_review、next_queue=shadow_monitor / paper_review_gate",
            "evidence_links": "shadow_price、rounded_qty、cost_estimate_bps、cap snapshot、paper/live-shadow 主键配对 ref",
            "ready_for_next_queue": "paper/live-shadow 主键、qty rounding 与成本快照都齐，才配继续 shadow review 或等待 promotion review。",
            "hard_stop": "若 green closeout 没绑定 parity row ref 或 paper/live-shadow 主键断裂，就不能口头写成‘影子侧已对齐’。",
        },
        {
            "row_order": "3",
            "registry_row_kind": "parity_red freeze row",
            "required_keys": "ticket_id、parity_red_row_ref、prior_green_or_ticket_ref、review_stage=shadow_parity、trigger_reason、reopen_earliest_ts、root_cause_owner",
            "status_fields": "ticket_status=closed_red、mismatch_status=red、operator_action=freeze_review、closeout_state=freeze_review_with_reopen_gate、next_queue=root_cause_audit",
            "evidence_links": "mismatch_reason、root-cause evidence placeholder、operator_note、freeze_ts",
            "ready_for_next_queue": "只有 red 已显式写成 freeze review，且 reopen 最早时点与 root-cause owner 都齐，才算真正进入 root-cause / reopen 队列。",
            "hard_stop": "如果 red 只留在日志里、registry 没有 freeze row，就不能假装已经完成停机与收口。",
        },
        {
            "row_order": "4",
            "registry_row_kind": "reopen gate row",
            "required_keys": "ticket_id、prior_red_ref_id、review_stage=reopen_gate、reopen_gate_pass_ref、missing_docs_checklist、closed_ts",
            "status_fields": "ticket_status=closed_yellow、closeout_state=reopen_ready、next_queue=routing_dry_run_replay、candidate_live_state=still_blocked",
            "evidence_links": "reopen gate checklist ref、补件清单、operator_note、cooldown_done_ts",
            "ready_for_next_queue": "只有 prior_red_ref_id 与 reopen_gate_pass_ref 都能追溯，才配回到 routing dry-run replay。",
            "hard_stop": "若 reopen_ready 没绑定 prior_red_ref_id，就会把恢复动作与历史红单断开，必须继续 freeze_review。",
        },
        {
            "row_order": "5",
            "registry_row_kind": "resume green row",
            "required_keys": "ticket_id、prior_red_ref_id、review_stage=resume、green_resume_row_ref、new_dry_run_receipt_ref、closed_ts",
            "status_fields": "ticket_status=closed_green、mismatch_status=green、closeout_state=resume_shadow_review、next_queue=shadow_monitor",
            "evidence_links": "new dry-run receipt、qty/cost parity refresh、operator_reconciliation_sequence ref、operator_note",
            "ready_for_next_queue": "只有 receipt replay 与新的 qty/cost parity 都重新过关，才配把历史 red 链接回绿色连续链。",
            "hard_stop": "若缺 prior_red_ref_id 或新的 receipt / parity ref，就不能把 resume 写成 green continuity。",
        },
    ]


def write_small_live_review_registry_template_csv(rows: list[dict[str, str]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with SMALL_LIVE_REVIEW_REGISTRY_TEMPLATE_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "row_order",
                "registry_row_kind",
                "required_keys",
                "status_fields",
                "evidence_links",
                "ready_for_next_queue",
                "hard_stop",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def get_small_live_shadow_parity_rows() -> list[dict[str, str]]:
    return [
        {
            "step_order": "1",
            "step_name": "paper signal 配对冻结",
            "required_input": "candidate_id / deployment_scope、paper_ref_id、signal_bar_utc、已批准的 paper candidate row",
            "pass_rule": "每条 live-shadow 检查都必须先绑定到唯一一条 paper row；bar 时间与 deployment scope 一致，不能临时换候选或换口径。",
            "block_on_fail": "找不到 paper_ref、同一 live-shadow 对应多个 paper row、或 scope 与 candidate spec 不一致，直接停在 shadow parity 前。",
            "ledger_fields": "candidate_id / deployment_scope、paper_ref_id / signal_bar_utc",
        },
        {
            "step_order": "2",
            "step_name": "payload parity 快照",
            "required_input": "research_symbol、venue_symbol、side、intended_notional_usd、intended_qty、venue precision / pair whitelist",
            "pass_rule": "live-shadow payload 必须逐项复用 paper 的 symbol / side / scope，并通过 venue precision 与白名单检查；不允许靠人工临时修 payload。",
            "block_on_fail": "symbol / side / whitelist / precision 任一不一致，或 payload 需要手工改写后才能发出，直接记 `parity_red`。",
            "ledger_fields": "research_symbol / venue_symbol / side、intended_notional_usd、intended_qty / rounded_qty / min_notional_check",
        },
        {
            "step_order": "3",
            "step_name": "shadow price + 成本快照",
            "required_input": "shadow_price、price_source_ts_utc、cost_estimate_bps、cap_pct_total / cap_pct_sleeve",
            "pass_rule": "在 hypothetic send 前就锁定 shadow 价格、价格源时间戳与预估成本；价格源与 paper 所见市场状态不得错位超过 `1 bar`。",
            "block_on_fail": "缺 `shadow_price`、price source 过旧、或成本预估根本没落表，说明还不能审计 live vs paper 偏差，直接阻断。",
            "ledger_fields": "shadow_price、cost_estimate_bps / slippage_bps、cap_pct_total / cap_pct_sleeve / remaining_cap_pct",
        },
        {
            "step_order": "4",
            "step_name": "数量舍入 / 资金占用 parity",
            "required_input": "intended_qty、rounded_qty、min_notional_check、remaining_cap_pct、pilot cap snapshot",
            "pass_rule": "venue rounding 后的数量仍应落在同一笔 paper 想表达的资金范围内，并继续满足 min_notional 与 pilot cap 约束。",
            "block_on_fail": "rounded_qty 把 notional 拉出资金上限、min_notional 未过、或 venue rounding 让 exposure 明显偏离 paper 意图，直接记 `parity_red`。",
            "ledger_fields": "intended_qty / rounded_qty / min_notional_check、intended_notional_usd / cap_pct_total / cap_pct_sleeve / remaining_cap_pct",
        },
        {
            "step_order": "5",
            "step_name": "paper vs live-shadow 时钟 / 路径对齐",
            "required_input": "paper signal ts、shadow payload ts、route/shadow ack ts、price source clock、paper path snapshot",
            "pass_rule": "paper 与 live-shadow 必须对齐到同一 decision bar；clock drift <= `60s`，且 shadow 预估成本相对 paper 偏差 <= `25bps`。",
            "block_on_fail": "bar 偏离 > `1 bar`、clock drift > `60s`、或同笔成本差持续 > `25bps` 仍无解释，直接标 `parity_red` 并停止升级。",
            "ledger_fields": "route_intent_ts_utc / route_ack_ts_utc / ack_latency_ms、mismatch_status / mismatch_reason",
        },
        {
            "step_order": "6",
            "step_name": "同账本留双引用 + 红旗动作",
            "required_input": "paper_ref_id、live_shadow_ref_id、mismatch_status、operator_action、operator_note",
            "pass_rule": "同一行 ledger 同时留下 paper 与 live-shadow 引用，并明确写出 `hold` / `cancel` / `escalate` 等 operator 动作。",
            "block_on_fail": "shadow parity 结果只留在终端/日志，没有回写 ledger，或出现 `parity_red` 却没有动作与备注，视为流程不可审计。",
            "ledger_fields": "paper_ref_id / live_shadow_ref_id、mismatch_status / mismatch_reason、operator_action / live_order_id、trigger_reason / reopen_earliest_ts / operator_note",
        },
    ]


def write_small_live_shadow_parity_csv(rows: list[dict[str, str]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with SMALL_LIVE_SHADOW_PARITY_CHECKLIST_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "step_order",
                "step_name",
                "required_input",
                "pass_rule",
                "block_on_fail",
                "ledger_fields",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def get_small_live_parity_red_action_rows() -> list[dict[str, str]]:
    return [
        {
            "action_order": "1",
            "red_trigger": "payload / whitelist / precision mismatch",
            "operator_action": "立即 `hold` 当前 shadow parity，并把 route 尝试停在 `cancel_or_no_send`；不得手工改 payload 后硬发。",
            "route_handling": "若 route 还没出 ack，就不继续发送；若已出 dry-run ack，则补一条 cancel/close 回执并冻结这条 parity row。",
            "ledger_writeback": "写 `mismatch_status=red`、`mismatch_reason=payload_or_precision_gap`、`operator_action=hold`，并补 `paper_ref_id / live_shadow_ref_id / operator_note`。",
            "clear_to_retry": "只有等 symbol mapping、precision snapshot 与白名单重新核对一致后，才允许重开下一条 shadow row。",
        },
        {
            "action_order": "2",
            "red_trigger": "clock drift > 60s / stale price source / bar misalignment",
            "operator_action": "直接 `hold`；当前 row 不升级成 tiny-live，也不把这次检查包装成‘只是小延迟’。",
            "route_handling": "停止继续沿旧 price source 走下去；重新抓 price snapshot、校对 paper signal bar，再决定是否新开 shadow row。",
            "ledger_writeback": "写 `mismatch_reason=clock_drift_or_stale_price`，并记录 `route_intent_ts_utc / route_ack_ts_utc / ack_latency_ms / signal_bar_utc`。",
            "clear_to_retry": "只有在 paper 与 shadow 回到同一 decision bar，且 drift 回到 `<=60s`，才允许重试。",
        },
        {
            "action_order": "3",
            "red_trigger": "rounded_qty 把 notional 拉出 cap / min_notional 未过 / venue rounding 失真",
            "operator_action": "保持 `paper only`，本次 shadow row 记 `hold`；不得临时手改数量凑单。",
            "route_handling": "不继续发送新 payload；先回到 sizing / cap review，确认 intended_qty 与 venue rounding 重新一致。",
            "ledger_writeback": "写 `mismatch_reason=qty_rounding_or_cap_breach`，并回填 `intended_qty / rounded_qty / min_notional_check / remaining_cap_pct`。",
            "clear_to_retry": "只有在 rounded_qty 重新落回 cap 规则内，且 min_notional 检查通过时，才允许开下一条 parity row。",
        },
        {
            "action_order": "4",
            "red_trigger": "shadow 成本偏差 > 25bps / 成本快照缺失 / 无法解释的高滑点预估",
            "operator_action": "记 `escalate` 到 parity review；当前 row 不进入 tiny-live 资格讨论。",
            "route_handling": "停止沿当前成本假设继续；先补 price / fee / slippage 证据，再决定是否重跑 shadow parity。",
            "ledger_writeback": "写 `mismatch_reason=cost_gap_or_missing_snapshot`，并保留 `shadow_price / cost_estimate_bps / operator_note`。",
            "clear_to_retry": "只有成本快照齐全，且 paper vs shadow 成本差回到 `<=25bps` 或有明确解释，才允许继续。",
        },
        {
            "action_order": "5",
            "red_trigger": "连续 `2` 次 parity_red / 未解释 data gap / 未解释 precision mismatch",
            "operator_action": "冻结当前 candidate 的 small-live promotion review，明确退回 `paper only`；必要时标记 `rollback_pre_live`。",
            "route_handling": "暂停新的 shadow parity 尝试，直到问题被单独审计关闭；不允许靠更多重试稀释红旗。",
            "ledger_writeback": "写 `mismatch_status=red`、`operator_action=rollback_or_freeze_review`、`trigger_reason=repeat_parity_red`、`reopen_earliest_ts`。",
            "clear_to_retry": "只有完成 root-cause 审计，并重新走 `routing dry-run -> shadow parity`，才允许恢复。",
        },
    ]


def write_small_live_parity_red_action_csv(rows: list[dict[str, str]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with SMALL_LIVE_PARITY_RED_ACTION_LADDER_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "action_order",
                "red_trigger",
                "operator_action",
                "route_handling",
                "ledger_writeback",
                "clear_to_retry",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def get_small_live_shadow_parity_sample_rows() -> list[dict[str, str]]:
    return [
        {
            "row_kind": "parity_red_shadow_example",
            "candidate_id": "breakout-live-challenger",
            "deployment_scope": "shadow_parity_only",
            "stage_status": "shadow_parity",
            "paper_ref_id": "paper-20260316-0519-breakout-ethusdt-short-001",
            "live_shadow_ref_id": "shadow-20260316-0519-breakout-ethusdt-short-001",
            "signal_bar_utc": "2026-03-16 05:15:00 UTC",
            "research_symbol": "ETHUSDT",
            "venue_symbol": "ETH-USDT-SWAP",
            "side": "short",
            "route_intent_ts_utc": "2026-03-16 05:19:12 UTC",
            "route_ack_ts_utc": "2026-03-16 05:19:14 UTC",
            "ack_latency_ms": "2400",
            "intended_notional_usd": "50.00",
            "cap_pct_total": "0.30%",
            "cap_pct_sleeve": "3.00%",
            "remaining_cap_pct": "97.00%",
            "intended_qty": "0.0250",
            "rounded_qty": "0.0200",
            "min_notional_check": "pass",
            "shadow_price": "1985.20",
            "cost_estimate_bps": "31",
            "mismatch_status": "red",
            "mismatch_reason": "cost_gap_or_missing_snapshot",
            "operator_action": "hold",
            "trigger_reason": "shadow_cost_delta_gt_25bps",
            "reopen_earliest_ts": "2026-03-16 05:35:00 UTC",
            "operator_note": "paper 与 shadow bar 对齐，但当前 shadow 成本预估 31bps，高于 v1 阈值 25bps；本行留在 parity review，不升级 tiny-live。",
        }
    ]


def write_small_live_shadow_parity_sample_row_csv(rows: list[dict[str, str]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with SMALL_LIVE_SHADOW_PARITY_SAMPLE_ROW_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "row_kind",
                "candidate_id",
                "deployment_scope",
                "stage_status",
                "paper_ref_id",
                "live_shadow_ref_id",
                "signal_bar_utc",
                "research_symbol",
                "venue_symbol",
                "side",
                "route_intent_ts_utc",
                "route_ack_ts_utc",
                "ack_latency_ms",
                "intended_notional_usd",
                "cap_pct_total",
                "cap_pct_sleeve",
                "remaining_cap_pct",
                "intended_qty",
                "rounded_qty",
                "min_notional_check",
                "shadow_price",
                "cost_estimate_bps",
                "mismatch_status",
                "mismatch_reason",
                "operator_action",
                "trigger_reason",
                "reopen_earliest_ts",
                "operator_note",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def get_small_live_green_shadow_parity_sample_rows() -> list[dict[str, str]]:
    return [
        {
            "row_kind": "green_shadow_parity_example",
            "candidate_id": "future-crypto-live-challenger",
            "deployment_scope": "shadow_parity_only",
            "stage_status": "shadow_parity",
            "paper_ref_id": "paper-20260316-0820-ema-btcusdt-long-001",
            "live_shadow_ref_id": "shadow-20260316-0820-ema-btcusdt-long-001",
            "signal_bar_utc": "2026-03-16 08:15:00 UTC",
            "research_symbol": "BTCUSDT",
            "venue_symbol": "BTC-USDT-SWAP",
            "side": "long",
            "route_intent_ts_utc": "2026-03-16 08:20:09 UTC",
            "route_ack_ts_utc": "2026-03-16 08:20:10 UTC",
            "ack_latency_ms": "850",
            "intended_notional_usd": "40.00",
            "cap_pct_total": "0.25%",
            "cap_pct_sleeve": "2.50%",
            "remaining_cap_pct": "97.50%",
            "intended_qty": "0.00092",
            "rounded_qty": "0.00090",
            "min_notional_check": "pass",
            "shadow_price": "43210.50",
            "cost_estimate_bps": "14",
            "mismatch_status": "green",
            "mismatch_reason": "none",
            "operator_action": "continue_shadow_review",
            "trigger_reason": "shadow_parity_pass",
            "reopen_earliest_ts": "2026-03-16 08:40:00 UTC",
            "operator_note": "paper_ref 与 live-shadow payload、qty rounding、cap 与成本快照都已对齐；当前行只表示 shadow parity 通过，可继续 shadow review，仍不代表 tiny-live 已放行。",
        }
    ]


def write_small_live_green_shadow_parity_sample_row_csv(rows: list[dict[str, str]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with SMALL_LIVE_GREEN_SHADOW_PARITY_SAMPLE_ROW_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "row_kind",
                "candidate_id",
                "deployment_scope",
                "stage_status",
                "paper_ref_id",
                "live_shadow_ref_id",
                "signal_bar_utc",
                "research_symbol",
                "venue_symbol",
                "side",
                "route_intent_ts_utc",
                "route_ack_ts_utc",
                "ack_latency_ms",
                "intended_notional_usd",
                "cap_pct_total",
                "cap_pct_sleeve",
                "remaining_cap_pct",
                "intended_qty",
                "rounded_qty",
                "min_notional_check",
                "shadow_price",
                "cost_estimate_bps",
                "mismatch_status",
                "mismatch_reason",
                "operator_action",
                "trigger_reason",
                "reopen_earliest_ts",
                "operator_note",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def get_small_live_reopen_gate_rows() -> list[dict[str, str]]:
    return [
        {
            "step_order": "1",
            "reopen_step": "先尊重 cooldown / reopen_earliest_ts",
            "must_be_true": "当前时间已晚于 ledger 里的 `reopen_earliest_ts`，且没有新的 `parity_red` / route ack 缺失还挂在同一 candidate 上。",
            "if_not_true": "继续 `paper only`，不新开 shadow parity row，也不把等待包装成‘问题已自然消失’。",
            "ledger_writeback": "保留上一条 red row，并在 operator note 明确写 `waiting_reopen_window`。",
        },
        {
            "step_order": "2",
            "reopen_step": "root-cause 必须被单独关单",
            "must_be_true": "前一条 red row 的 `mismatch_reason / trigger_reason` 已有明确解释，且补上对应证据：例如 precision snapshot、fee/slippage snapshot、symbol mapping diff、或 data-gap 修复说明。",
            "if_not_true": "不得靠‘再试一次也许就好’重开；默认维持 freeze review。",
            "ledger_writeback": "新增 `operator_note` 或审计引用，明确是哪条证据把 red cause 关掉。",
        },
        {
            "step_order": "3",
            "reopen_step": "先重走 routing dry-run 最小回执",
            "must_be_true": "同一 candidate / symbol 已重新拿到干净的 `intent -> ack -> cancel/close` 回执链，且 `clock drift <= 60s`。",
            "if_not_true": "说明基础执行链还不稳；继续停在 dry-run，不回 shadow parity。",
            "ledger_writeback": "回填新的 `route_intent_ts_utc / route_ack_ts_utc / ack_latency_ms`，必要时补 `cancel_ts` 备注。",
        },
        {
            "step_order": "4",
            "reopen_step": "新 shadow row 必须重新过 qty / cost parity",
            "must_be_true": "新的 shadow row 在 `rounded_qty / min_notional / cap` 上都重新通过，且 paper vs shadow 成本差回到 `<=25bps`。",
            "if_not_true": "继续记 `parity_red`，并把 candidate 留在 `paper only`；不能跳过 shadow parity 直接讨论 tiny-live。",
            "ledger_writeback": "写新的 `paper_ref_id / live_shadow_ref_id / rounded_qty / cost_estimate_bps / mismatch_status`。",
        },
        {
            "step_order": "5",
            "reopen_step": "只有 green shadow parity 才允许恢复 review",
            "must_be_true": "至少出现一条新的 `mismatch_status=green` shadow parity row，且当前 candidate 仍在 whitelist / capital cap / sleeve cap 内。",
            "if_not_true": "继续冻结 small-live promotion review；必要时降回更早的 paper review。",
            "ledger_writeback": "把 `operator_action` 改回 `resume_shadow_review`，并记录新的 `reopen_earliest_ts`（若仍需观察）。",
        },
    ]


def write_small_live_reopen_gate_csv(rows: list[dict[str, str]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with SMALL_LIVE_REOPEN_GATE_CHECKLIST_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "step_order",
                "reopen_step",
                "must_be_true",
                "if_not_true",
                "ledger_writeback",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def get_small_live_reopen_resume_sample_rows() -> list[dict[str, str]]:
    return [
        {
            "row_kind": "reopen_green_shadow_example",
            "candidate_id": "breakout-live-challenger",
            "prior_red_ref_id": "shadow-20260316-0519-breakout-ethusdt-short-001",
            "deployment_scope": "shadow_parity_only",
            "stage_status": "resume_shadow_review",
            "paper_ref_id": "paper-20260316-0659-breakout-ethusdt-short-002",
            "live_shadow_ref_id": "shadow-20260316-0659-breakout-ethusdt-short-002",
            "signal_bar_utc": "2026-03-16 06:55:00 UTC",
            "research_symbol": "ETHUSDT",
            "venue_symbol": "ETH-USDT-SWAP",
            "side": "short",
            "route_intent_ts_utc": "2026-03-16 06:59:12 UTC",
            "route_ack_ts_utc": "2026-03-16 06:59:13 UTC",
            "ack_latency_ms": "900",
            "intended_notional_usd": "50.00",
            "cap_pct_total": "0.30%",
            "cap_pct_sleeve": "3.00%",
            "remaining_cap_pct": "97.00%",
            "intended_qty": "0.0250",
            "rounded_qty": "0.0250",
            "min_notional_check": "pass",
            "shadow_price": "1984.80",
            "cost_estimate_bps": "18",
            "mismatch_status": "green",
            "mismatch_reason": "resolved_after_fee_snapshot_refresh",
            "operator_action": "resume_shadow_review",
            "trigger_reason": "reopen_gate_passed",
            "reopen_earliest_ts": "2026-03-16 07:20:00 UTC",
            "operator_note": "上一条 red row 的成本快照缺口已补齐，并重走 intent->ack->cancel/close 回执；当前 qty/cap/cost 都重新过关，因此恢复 shadow review，但仍保留下一次最早重检时点。",
        }
    ]


def write_small_live_reopen_resume_sample_row_csv(rows: list[dict[str, str]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with SMALL_LIVE_REOPEN_RESUME_SAMPLE_ROW_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "row_kind",
                "candidate_id",
                "prior_red_ref_id",
                "deployment_scope",
                "stage_status",
                "paper_ref_id",
                "live_shadow_ref_id",
                "signal_bar_utc",
                "research_symbol",
                "venue_symbol",
                "side",
                "route_intent_ts_utc",
                "route_ack_ts_utc",
                "ack_latency_ms",
                "intended_notional_usd",
                "cap_pct_total",
                "cap_pct_sleeve",
                "remaining_cap_pct",
                "intended_qty",
                "rounded_qty",
                "min_notional_check",
                "shadow_price",
                "cost_estimate_bps",
                "mismatch_status",
                "mismatch_reason",
                "operator_action",
                "trigger_reason",
                "reopen_earliest_ts",
                "operator_note",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def get_baseline_compare_rows() -> list[dict[str, str]]:
    return [
        {
            "line": "EMA baseline family",
            "current_rank": "默认 baseline / closest to paper",
            "ema_baseline_role": "基准本体：当前主 raw alpha baseline 与 deployment reference",
            "current_increment": "不适用；它本身就是当前默认比较基线。补充读法：PSAR overlay 当前只在 `创业板ETF 1d` 显示出 shadow-protective 方向，还没有形成新的 baseline seat。",
            "why_not_above_ema": "不适用。当前 seat 之所以还由 EMA 持有，是因为它已有 survivor map + candidate spec + runbook + day-0 ledger snapshot，并且 active 1d lanes 已清掉 source-risk；同时 A股 daily overlay overall 仍是 mixed，不支持把 PSAR 额外焊成默认保护层。",
            "next_honest_test": "继续沿同一张 live ledger 落下真实 market-close refresh / week-1 review；若 primary 或 front-queue secondary 转弱，再按 runbook demote / rollback。PSAR overlay 只在 `创业板ETF 1d` 的 shadow protocol 下继续观察，不改默认持有规则。",
        },
        {
            "line": "support_breakout_v0 / breakout-short follow-up",
            "current_rank": "bench / conditional alpha",
            "ema_baseline_role": "当前所有结构层都该先回答：它有没有比 EMA 更早、更诚实地拿到 paper admission 资格；如果没有，就应退出默认资源位。",
            "current_increment": "有条件性 alpha 价值，但 deployment rank 上已被 desk 正式压成 `bench`。当前更诚实的位置是保留证据、等待 genuinely new blocker reduction，而不是继续争主位。",
            "why_not_above_ema": "默认 pair halfsize 虽把 hourly path 抬到约 +19.90%，但 pure down coverage 仍是 0/100，predown_bridge_12h 仍是 0/11，downrisk_48h 仍是 0/109；在“唯一一枪”打完后 blocker 仍未下降，所以它不能继续占用默认 Live Seat 主资源。",
            "next_honest_test": "只有新的 shadow / holdout 真正命中 pure-test/down-tail blocker reduction，或 Scout Seat 先产出更强 challenger 后再回来同框比较，才配讨论它是否重回默认资源位。",
        },
        {
            "line": "Fibonacci confirmation / retest_hold",
            "current_rank": "archive / optional filter",
            "ema_baseline_role": "默认只作为过滤层候选；若不能先胜过 breakout v0，就更谈不上挑战 EMA baseline seat。",
            "current_increment": "当前没有。它改善了一些 invalidation / 机制表达，但在 breakout v0 同样本 A/B 里并没有把主线收益或部署可用性做得更诚实。",
            "why_not_above_ema": "Fib A/B 里平均单笔约 +0.71%、累计约 +20.00%，明显弱于 breakout v0，而且平均还延迟约 12.5 根 bar；因此当前连 structure 主线内部都不是胜出者。",
            "next_honest_test": "除非以后只把它放回更窄的 down-regime filter 问题，并证明它能在不明显压塌 entry 的前提下改善一个已保留候选，否则继续维持 archive。",
        },
    ]


def write_baseline_compare_csv(rows: list[dict[str, str]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with BASELINE_COMPARE_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "line",
                "current_rank",
                "ema_baseline_role",
                "current_increment",
                "why_not_above_ema",
                "next_honest_test",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def get_small_live_default_seat_queue_rows() -> list[dict[str, str]]:
    recon_rows = read_csv_rows(MANUAL_NARROW_RECONCILIATION_PATH)
    trigger_rows = {row.get("candidate_id", ""): row for row in read_csv_rows(MANUAL_NARROW_BOT3_TRIGGER_PATH)}
    rank2_status_rows = read_csv_rows(SMALL_LIVE_RANK2_STATUS_SNAPSHOT_PATH)
    rank2_status = rank2_status_rows[0] if rank2_status_rows else {}

    rows = [
        {
            "queue_order": "0",
            "seat_or_candidate": "Live Seat / default",
            "current_stage": "empty_by_default",
            "tiny_live_review_now": "no",
            "default_owner": "bot2 explicit promotion only",
            "hard_blocker": "当前 board 明确要求 Live Seat 保持暂空；P3 身份、open paper positions 或 narrow-paper continuity 都不能自动占位。",
            "promotion_trigger": "只有 bot2 明确点名新的 promoted candidate 时，才允许重新进入 tiny-live review。",
            "evidence_note": "这张队列表达的是默认部署排序，而不是谁在研究上看起来更有希望。",
        }
    ]

    order_map = {
        "rank2_combo_all": "1",
        "rank17_pullback_ethsol_narrow_pilot": "2",
        "rank29_trendline_breakout_navigator": "3",
    }
    stage_map = {
        "rank2_combo_all": "narrow_paper_candidate_closeout_only",
        "rank17_pullback_ethsol_narrow_pilot": "p3_narrow_paper_continuity_only",
        "rank29_trendline_breakout_navigator": "p3_monitoring_only",
    }
    blocker_map = {
        "rank17_pullback_ethsol_narrow_pilot": "当前 open paper positions 只属于 manual narrow-paper refresh continuity，不自动构成 tiny-live review need。",
        "rank29_trendline_breakout_navigator": "当前只保留 paper-only narrow pilot + middle-bucket red-watch；没有新的 append/review 行，也没有新的 live review promotion。",
    }

    for recon in recon_rows:
        candidate_id = recon.get("candidate_id", "")
        trigger = trigger_rows.get(candidate_id, {})
        if candidate_id == "rank2_combo_all":
            hard_blocker = rank2_status.get("current_blockers", "仍缺 whitelist-bound test/no-fill receipt chain。")
            promotion_trigger = "先拿到同一条 whitelist-bound replay 的真实 intent/ack/cancel(close) refs，再由 bot2 明确点名是否进入 shadow parity / tiny-live review。"
            evidence_note = rank2_status.get("status_summary", "Rank 2 当前仍停在 paper_candidate_only / blocked。")
            default_owner = "run3 closeout / operator dry-run"
        else:
            hard_blocker = blocker_map.get(candidate_id, recon.get("desk_read", ""))
            promotion_trigger = trigger.get("trigger_condition", "出现新的 closed trade append 或 weekly-review row") + "；若无 bot2 promoted candidate 点名，仍不自动进入 tiny-live review。"
            evidence_note = trigger.get("evidence_note", recon.get("desk_read", ""))
            default_owner = recon.get("default_owner", "manual_narrow_paper_runner")

        rows.append({
            "queue_order": order_map.get(candidate_id, "9"),
            "seat_or_candidate": f"Rank {recon.get('candidate_rank', '?')} / {candidate_id}",
            "current_stage": stage_map.get(candidate_id, recon.get("scope_tag", "narrow_paper")),
            "tiny_live_review_now": "no",
            "default_owner": default_owner,
            "hard_blocker": hard_blocker,
            "promotion_trigger": promotion_trigger,
            "evidence_note": evidence_note,
        })

    rows.sort(key=lambda r: (int(r["queue_order"]), r["seat_or_candidate"]))
    return rows


def write_small_live_default_seat_queue_csv(rows: list[dict[str, str]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with SMALL_LIVE_DEFAULT_SEAT_QUEUE_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "queue_order",
                "seat_or_candidate",
                "current_stage",
                "tiny_live_review_now",
                "default_owner",
                "hard_blocker",
                "promotion_trigger",
                "evidence_note",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def get_small_live_live_seat_reentry_trigger_rows() -> list[dict[str, str]]:
    rows = [
        {
            "trigger_order": "0",
            "seat_or_candidate": "Live Seat / default",
            "current_stage": "empty_by_default",
            "status_change_event": "只有 bot2 明确点名新的 promoted candidate，才允许从空席改成 review 中。",
            "minimum_evidence_bundle": "seat verdict change + promoted candidate id + why-now reason",
            "next_allowed_stage": "tiny_live_review_candidate_only",
            "why_not_now": "当前 desk 明确保持空席；P3 身份、open paper positions、或 manual continuity 都不自动改席位。",
        },
        {
            "trigger_order": "1",
            "seat_or_candidate": "Rank 2 / combo_all",
            "current_stage": "paper_candidate_only / blocked",
            "status_change_event": "同一条 whitelist-bound `test/no-fill` replay 真正留下 `intent + ack + cancel(close)` refs。",
            "minimum_evidence_bundle": "receipt chain refs + whitelist scope freeze + capital=0 dry-run proof",
            "next_allowed_stage": "eligible_for_shadow_parity_review_only",
            "why_not_now": "当前真正会改状态的只剩真实 replay；继续补 packet / starter rows 不再减少 blocker。",
        },
        {
            "trigger_order": "2",
            "seat_or_candidate": "Rank 17 / pullback recovery（ETH+SOL only）",
            "current_stage": "P3 narrow paper continuity",
            "status_change_event": "manual runner 真新增 `closed trade append` 或 `weekly-review row`，且 bot2 明确把它从 P3 升到 P4 review。",
            "minimum_evidence_bundle": "new append/review row + ETH/SOL continuity proof + explicit bot2 promotion",
            "next_allowed_stage": "P4 tiny-live review candidate",
            "why_not_now": "当前 open paper positions 只说明 narrow-paper continuity 在跑，不说明该自动重开 Live Seat。",
        },
        {
            "trigger_order": "3",
            "seat_or_candidate": "Rank 29 / trendline breakout navigator",
            "current_stage": "P3 monitoring / paper-only red-watch",
            "status_change_event": "manual runner 真新增 `closed trade append` 或 `weekly-review row`，并且 middle-bucket red-watch 不再恶化，再由 bot2 明确升到 P4 review。",
            "minimum_evidence_bundle": "new append/review row + red-watch not worse note + explicit bot2 promotion",
            "next_allowed_stage": "P4 tiny-live review candidate",
            "why_not_now": "当前新增的只是 open continuity position，不是新的 review trigger；仍属于 paper-only narrow pilot。",
        },
    ]
    rows.sort(key=lambda r: (int(r["trigger_order"]), r["seat_or_candidate"]))
    return rows


def write_small_live_live_seat_reentry_trigger_csv(rows: list[dict[str, str]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with SMALL_LIVE_LIVE_SEAT_REENTRY_TRIGGER_MATRIX_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "trigger_order",
                "seat_or_candidate",
                "current_stage",
                "status_change_event",
                "minimum_evidence_bundle",
                "next_allowed_stage",
                "why_not_now",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def get_small_live_status_change_watchboard_rows() -> list[dict[str, str]]:
    rows = [
        {
            "watch_order": "0",
            "seat_or_candidate": "Live Seat / default",
            "current_stage": "empty_by_default",
            "where_to_watch": "docs/TODO.md top desk board + bot2 explicit promotion note",
            "default_owner": "bot2",
            "what_event_wakes_tiny_live": "bot2 明确点名新的 promoted candidate，并写清 why-now reason",
            "minimum_evidence": "promoted candidate id + seat verdict change + why-now reason",
            "if_event_lands": "才允许从 empty_by_default 切到 tiny_live_review_candidate_only",
            "if_event_missing": "继续空席；P3 continuity / open positions 不自动占位",
        },
        {
            "watch_order": "1",
            "seat_or_candidate": "Rank 2 / combo_all",
            "current_stage": "paper_candidate_only / blocked",
            "where_to_watch": "small_live_rank2_receipt_chain_log_template_v1.csv + small_live_rank2_receipt_chain_audit_v1.csv",
            "default_owner": "operator / run3 closeout",
            "what_event_wakes_tiny_live": "同一条 whitelist-bound test/no-fill replay 真回填 intent + ack + cancel(close) refs",
            "minimum_evidence": "real receipt chain refs + whitelist scope freeze + capital=0 dry-run proof",
            "if_event_lands": "只允许进入 eligible_for_shadow_parity_review / shadow_parity，不是 tiny-live pass",
            "if_event_missing": "不要再把 packet / starter row / wording 近义页当进展",
        },
        {
            "watch_order": "2",
            "seat_or_candidate": "Rank 17 / pullback recovery（ETH+SOL only）",
            "current_stage": "P3 narrow paper continuity",
            "where_to_watch": "manual_narrow_paper_bot3_reentry_queue.csv + manual_narrow_paper_status.csv + bot2 promotion note",
            "default_owner": "manual_narrow_paper_runner + bot2",
            "what_event_wakes_tiny_live": "manual runner 真新增 closed trade append / weekly-review row，且 bot2 明确升到 P4 review",
            "minimum_evidence": "new append/review row + ETH/SOL continuity proof + explicit bot2 promotion",
            "if_event_lands": "才配进入 P4 tiny-live review candidate",
            "if_event_missing": "继续按 cron-managed continuity 处理，不因 open positions 自动升级",
        },
        {
            "watch_order": "3",
            "seat_or_candidate": "Rank 29 / trendline breakout navigator",
            "current_stage": "P3 monitoring / paper-only red-watch",
            "where_to_watch": "manual_narrow_paper_bot3_reentry_queue.csv + manual_narrow_paper_status.csv + bot2 promotion note",
            "default_owner": "manual_narrow_paper_runner + bot2",
            "what_event_wakes_tiny_live": "manual runner 真新增 closed trade append / weekly-review row，且 middle-bucket red-watch 不再恶化，再由 bot2 明确升到 P4 review",
            "minimum_evidence": "new append/review row + red-watch not worse note + explicit bot2 promotion",
            "if_event_lands": "才配进入 P4 tiny-live review candidate",
            "if_event_missing": "继续 paper-only monitoring；P3 身份本身不是 re-entry 通道",
        },
    ]
    rows.sort(key=lambda r: (int(r["watch_order"]), r["seat_or_candidate"]))
    return rows


def write_small_live_status_change_watchboard_csv(rows: list[dict[str, str]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with SMALL_LIVE_STATUS_CHANGE_WATCHBOARD_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "watch_order",
                "seat_or_candidate",
                "current_stage",
                "where_to_watch",
                "default_owner",
                "what_event_wakes_tiny_live",
                "minimum_evidence",
                "if_event_lands",
                "if_event_missing",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def get_small_live_status_trigger_snapshot_rows() -> list[dict[str, str]]:
    rank2_rows = get_rank2_receipt_audit_rows()
    reentry_rows = read_csv_rows(MANUAL_NARROW_BOT3_TRIGGER_PATH)
    status_rows = read_csv_rows(ROOT / "reports" / "artifacts" / "manual_narrow_paper_lanes" / "manual_narrow_paper_status.csv")
    todo_text = TODO_PATH.read_text(encoding="utf-8") if TODO_PATH.exists() else ""
    manual_summary = read_json_dict(ROOT / "reports" / "artifacts" / "manual_narrow_paper_lanes" / "manual_narrow_paper_last_run_summary.json")

    latest_status_by_rank = {row.get("candidate_rank", ""): row for row in status_rows}
    reentry_by_rank = {row.get("candidate_rank", ""): row for row in reentry_rows}
    todo_lower = todo_text.lower()
    live_note = (
        "current desk board still says Live Seat = 暂空 / waiting for next promoted scout winner"
        if "当前候选**：`暂空 / waiting for next promoted scout winner`" in todo_text or "**`live seat = 暂空`**" in todo_lower
        else "desk board should be re-read for latest live-seat verdict"
    )
    observed_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    rank2_real_refs = ", ".join(sorted({row.get("real_refs_landed", "") for row in rank2_rows if row.get("real_refs_landed")})) or "n/a"
    rank2_missing = "; ".join(sorted({row.get("missing_real_refs", "") for row in rank2_rows if row.get("missing_real_refs")})) or "n/a"
    rank2_generated = max((row.get("generated_at_utc", "") for row in rank2_rows if row.get("generated_at_utc")), default=observed_now)

    rows = [
        {
            "snapshot_order": "0",
            "seat_or_candidate": "Live Seat / default",
            "trigger_state_now": "blocked_now",
            "latest_observed_evidence": live_note,
            "next_allowed_stage": "tiny_live_review_candidate_only",
            "hard_read": "继续 empty_by_default；只有 bot2 明确 promotion 才配重开 Live Seat",
            "observed_at_utc": observed_now,
        },
        {
            "snapshot_order": "1",
            "seat_or_candidate": "Rank 2 / combo_all",
            "trigger_state_now": "waiting_real_receipt_chain",
            "latest_observed_evidence": f"real_refs={rank2_real_refs}; missing={rank2_missing}",
            "next_allowed_stage": "eligible_for_shadow_parity_review / shadow_parity",
            "hard_read": "没有同一条 whitelist-bound replay 的 intent+ack+cancel(close) 真实 refs，就继续 paper_candidate_only / blocked",
            "observed_at_utc": rank2_generated,
        },
    ]

    fresh_closed_trade_count = int(manual_summary.get("new_closed_trades_appended") or 0)
    manual_run_at = manual_summary.get("run_at_utc", "") or observed_now

    for order, rank, name in [("2", "17", "Rank 17 / pullback recovery（ETH+SOL only）"), ("3", "29", "Rank 29 / trendline breakout navigator")]:
        reentry = reentry_by_rank.get(rank, {})
        status = latest_status_by_rank.get(rank, {})
        new_trades = status.get("new_trades_appended", "") or "0"
        open_position = status.get("open_position", "unknown") or "unknown"
        latest_closed_exit = status.get("latest_closed_exit_ts_utc", "") or "n/a"
        sample_end = reentry.get("latest_sample_end_utc") or status.get("sample_end_utc") or observed_now

        fresh_append_now = str(new_trades) not in {"", "0"}
        if fresh_append_now:
            trigger_state_now = "fresh_p3_append_landed"
            latest_observed_evidence = (
                f"manual_refresh_run_at={manual_run_at}; new_trades_appended={new_trades}; "
                f"latest_closed_exit_ts_utc={latest_closed_exit}; open_position={open_position}"
            )
            hard_read = (
                "已出现新的 closed-trade append，但这仍只构成 P3 review / continuity 事件；"
                "没有 bot2 promotion，就不要把它误读成 tiny-live re-entry。"
            )
        else:
            trigger_state_now = "continuity_only"
            latest_observed_evidence = (
                f"bot3_reentry_now={reentry.get('bot3_reentry_now', 'no')}; new_trades_appended={new_trades}; "
                f"open_position={open_position}; latest_closed_exit_ts_utc={latest_closed_exit}; "
                f"manual_refresh_new_closed_trades={fresh_closed_trade_count}"
            )
            hard_read = reentry.get("evidence_note", "仍属于 cron-managed continuity；当前没有新的 append/review 触发") or "仍属于 cron-managed continuity；当前没有新的 append/review 触发"

        rows.append(
            {
                "snapshot_order": order,
                "seat_or_candidate": name,
                "trigger_state_now": trigger_state_now,
                "latest_observed_evidence": latest_observed_evidence,
                "next_allowed_stage": "P3 review / continuity writeback now；P4 tiny-live review candidate only after real append/review + bot2 promotion",
                "hard_read": hard_read,
                "observed_at_utc": sample_end,
            }
        )

    rows.sort(key=lambda r: (int(r["snapshot_order"]), r["seat_or_candidate"]))
    return rows


def write_small_live_status_trigger_snapshot_csv(rows: list[dict[str, str]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with SMALL_LIVE_STATUS_TRIGGER_SNAPSHOT_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "snapshot_order",
                "seat_or_candidate",
                "trigger_state_now",
                "latest_observed_evidence",
                "next_allowed_stage",
                "hard_read",
                "observed_at_utc",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def get_small_live_now_action_queue_rows() -> list[dict[str, str]]:
    snapshot_rows = get_small_live_status_trigger_snapshot_rows()
    watchboard_rows = {row.get("seat_or_candidate", ""): row for row in get_small_live_status_change_watchboard_rows()}
    replay_context = get_rank2_replay_priority_context()

    rows: list[dict[str, str]] = []
    for snapshot in snapshot_rows:
        seat = snapshot.get("seat_or_candidate", "")
        trigger_state = snapshot.get("trigger_state_now", "")
        watch = watchboard_rows.get(seat, {})

        if seat == "Live Seat / default":
            owner = "bot2"
            next_action = "保持空席；只等待 bot2 明确 promotion note"
            waiting_for = "promoted candidate id + why-now reason + seat verdict change"
            hard_stop = "P3 continuity / open paper positions / manual append 都不能自动占 Live Seat"
            why = "当前 desk 顶板明确要求 Live Seat 默认空席；最诚实动作就是别偷跑。"
        elif seat == "Rank 2 / combo_all":
            rank2_sync_rows = get_rank2_execution_sync_guard_rows()
            rank2_sync_ok = all(row.get("guard_state") == "synced" for row in rank2_sync_rows)
            if rank2_sync_ok:
                owner = "operator / run3 closeout"
                next_action = str(replay_context["action_text"])
                waiting_for = "同一条 replay 的 real receipt chain refs"
                hard_stop = "没有三段真实 refs，就继续 paper_candidate_only / blocked，不得跳去 shadow parity"
                why = f"它当前唯一会改状态的动作就是真 replay；{replay_context['policy_blurb']}"
            else:
                owner = "run3 closure sync"
                next_action = "先重建 Rank 2 replay bundle；等 execution-sync guard 全部回到 synced 后，再信任当前 replay 顺序与预算读法。"
                waiting_for = "rank2 execution-sync guard 全部转回 synced"
                hard_stop = "上游 source 比 replay bundle 新时，不得继续照旧 bundle 执行 replay / shadow parity 解释"
                why = "当前更值钱的动作是先修 bundle 与上游 evidence 的不同步，而不是带着旧 replay 包继续推进 operator 步骤。"
        elif trigger_state == "fresh_p3_append_landed":
            owner = watch.get("default_owner", "manual_narrow_paper_runner + bot2")
            next_action = "只做 P3 review / continuity writeback；若无 bot2 promotion，不得升成 tiny-live review"
            waiting_for = watch.get("minimum_evidence", "new append/review row + explicit bot2 promotion")
            hard_stop = "fresh append 也只代表 P3 continuity 事件，不代表 Live Seat 重开"
            why = "当前最容易犯的错是把新 append 误读成 tiny-live trigger；这张队列把层级钉死。"
        else:
            owner = watch.get("default_owner", "manual_narrow_paper_runner + bot2")
            next_action = "继续 monitoring / continuity；等真实 append/review 行 + bot2 promotion"
            waiting_for = watch.get("minimum_evidence", "new append/review row + explicit bot2 promotion")
            hard_stop = "没有新的 append/review 行或 bot2 promotion，就不得推进到 P4 / tiny-live review"
            why = "当前没有真正的 status-changing event；继续补 tiny-live 同义文档不会减少 blocker。"

        rows.append(
            {
                "queue_order": snapshot.get("snapshot_order", "9"),
                "seat_or_candidate": seat,
                "trigger_state_now": trigger_state,
                "action_owner_now": owner,
                "next_allowed_action_now": next_action,
                "still_waiting_for": waiting_for,
                "hard_stop": hard_stop,
                "why_this_is_the_honest_next_step": why,
                "observed_at_utc": snapshot.get("observed_at_utc", ""),
            }
        )

    rows.sort(key=lambda r: (int(r["queue_order"]), r["seat_or_candidate"]))
    return rows


def write_small_live_now_action_queue_csv(rows: list[dict[str, str]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with SMALL_LIVE_NOW_ACTION_QUEUE_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "queue_order",
                "seat_or_candidate",
                "trigger_state_now",
                "action_owner_now",
                "next_allowed_action_now",
                "still_waiting_for",
                "hard_stop",
                "why_this_is_the_honest_next_step",
                "observed_at_utc",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def get_small_live_evidence_freshness_board_rows() -> list[dict[str, str]]:
    rows = [
        {
            "freshness_order": "0",
            "evidence_source": "docs/TODO.md top desk board",
            "backs_which_lane": "Live Seat default verdict / whole desk routing",
            **format_file_freshness(TODO_PATH, stale_after_min=360, warning_after_min=120),
            "why_it_matters": "如果 desk board 太旧，tiny-live 空席或 scout exhaustion 的读法可能已经落后。",
            "hard_read": "board 新鲜时，才适合继续把 Live Seat 读成 empty_by_default；若转 stale，就该优先重读顶板后再解释 tiny-live。",
        },
        {
            "freshness_order": "1",
            "evidence_source": "small_live_rank2_receipt_chain_audit_v1.csv",
            "backs_which_lane": "Rank 2 receipt-chain blocker",
            **format_file_freshness(SMALL_LIVE_RANK2_RECEIPT_AUDIT_PATH, stale_after_min=240, warning_after_min=90),
            "why_it_matters": "Rank 2 只差真实 replay refs；若 audit 过旧，就不能太自信地说它仍卡在完全相同的 missing refs。",
            "hard_read": "audit 新鲜时，继续把 Rank 2 读成 waiting_real_receipt_chain；若 stale，优先补新 audit 或 replay，而不是继续写 doc-chain。",
        },
        {
            "freshness_order": "2",
            "evidence_source": "manual_narrow_paper_status.csv",
            "backs_which_lane": "Rank 17 / Rank 29 P3 continuity snapshot",
            **format_file_freshness(ROOT / "reports" / "artifacts" / "manual_narrow_paper_lanes" / "manual_narrow_paper_status.csv", stale_after_min=180, warning_after_min=60),
            "why_it_matters": "P3 lane 最容易因为 status 表过旧而把 continuity / append 事件读错层级。",
            "hard_read": "status 新鲜时，新的 closed-trade append 才能被诚实压成 P3 continuity；若 stale，就别过度解读 continuity 没变化。",
        },
        {
            "freshness_order": "3",
            "evidence_source": "manual_narrow_paper_last_run_summary.json",
            "backs_which_lane": "manual runner latest append / refresh evidence",
            **format_file_freshness(ROOT / "reports" / "artifacts" / "manual_narrow_paper_lanes" / "manual_narrow_paper_last_run_summary.json", stale_after_min=180, warning_after_min=60),
            "why_it_matters": "这决定 tiny-live snapshot 看到的是刚跑完的 manual refresh，还是一张过时 summary。",
            "hard_read": "summary 新鲜时，可把 fresh append 限定为 P3 review 事件；若 stale，应该先等下一次 runner refresh，而不是把旧 snapshot 当现状。",
        },
    ]
    rows.sort(key=lambda r: (int(r["freshness_order"]), r["evidence_source"]))
    return rows


def write_small_live_evidence_freshness_board_csv(rows: list[dict[str, str]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with SMALL_LIVE_EVIDENCE_FRESHNESS_BOARD_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "freshness_order",
                "evidence_source",
                "backs_which_lane",
                "latest_file_mtime_utc",
                "approx_age",
                "freshness_state",
                "why_it_matters",
                "hard_read",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def get_rank2_execution_sync_guard_rows() -> list[dict[str, str]]:
    guard_specs = [
        (
            "0",
            SMALL_LIVE_RANK2_REPLAY_PREFLIGHT_SNAPSHOT_PATH,
            SMALL_LIVE_RANK2_NEXT_REPLAY_BUNDLE_PATH,
            "preflight symbol / budget read",
            "next replay bundle",
        ),
        (
            "1",
            SMALL_LIVE_RANK2_REPLAY_ROUNDING_BUDGET_LADDER_PATH,
            SMALL_LIVE_RANK2_NEXT_REPLAY_BUNDLE_PATH,
            "rounding ladder order",
            "next replay bundle",
        ),
        (
            "2",
            SMALL_LIVE_RANK2_RECEIPT_AUDIT_PATH,
            SMALL_LIVE_RANK2_NEXT_REPLAY_BUNDLE_PATH,
            "receipt-chain blocker read",
            "next replay bundle",
        ),
        (
            "3",
            SMALL_LIVE_RANK2_REPLAY_RUNSHEET_PATH,
            SMALL_LIVE_RANK2_NEXT_REPLAY_BUNDLE_PATH,
            "operator replay steps",
            "next replay bundle",
        ),
    ]
    rows = []
    for order, source_path, dependent_path, source_role, dependent_role in guard_specs:
        sync = format_sync_guard(source_path, dependent_path)
        guard_state = sync["guard_state"]
        if guard_state == "synced":
            hard_read = "当前可继续相信这张 replay bundle 的 symbol / budget / blocker 读法；不用再凭旧截图手动拼接。"
            required_action = "keep current bundle authoritative"
        elif guard_state == "missing_source":
            hard_read = "上游 source 缺失时，这张 replay bundle 不能再当 authoritative 执行包。"
            required_action = "rebuild missing upstream artifact before any operator replay read"
        else:
            hard_read = "上游 source 已比 bundle 更新；此时先重建 replay bundle，比继续照旧页面执行更诚实。"
            required_action = "rebuild alpha_closure_board before trusting replay order / budget / blocker read"

        rows.append(
            {
                "guard_order": order,
                "source_file": source_path.name,
                "source_role": source_role,
                "dependent_artifact": dependent_path.name,
                "dependent_role": dependent_role,
                "source_mtime_utc": sync["source_mtime_utc"],
                "dependent_mtime_utc": sync["dependent_mtime_utc"],
                "lag_read": sync["lag_read"],
                "guard_state": guard_state,
                "hard_read": hard_read,
                "required_action": required_action,
            }
        )

    rows.sort(key=lambda r: (int(r["guard_order"]), r["source_file"]))
    return rows


def write_rank2_execution_sync_guard_csv(rows: list[dict[str, str]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with SMALL_LIVE_RANK2_EXECUTION_SYNC_GUARD_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "guard_order",
                "source_file",
                "source_role",
                "dependent_artifact",
                "dependent_role",
                "source_mtime_utc",
                "dependent_mtime_utc",
                "lag_read",
                "guard_state",
                "hard_read",
                "required_action",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def get_rank2_replay_ready_gate_rows() -> list[dict[str, str]]:
    queue_rows = get_small_live_now_action_queue_rows()
    bundle_rows = get_rank2_next_replay_bundle_rows()
    execution_guard_rows = get_rank2_execution_sync_guard_rows()
    state_guard_rows = get_small_live_state_resync_guard_rows()

    rank2_queue = next((row for row in queue_rows if row.get("seat_or_candidate") == "Rank 2 / combo_all"), {})
    bundle = bundle_rows[0] if bundle_rows else {}

    execution_synced = bool(execution_guard_rows) and all(row.get("guard_state") == "synced" for row in execution_guard_rows)
    tiny_live_synced = bool(state_guard_rows) and all(row.get("guard_state") == "synced" for row in state_guard_rows)
    missing_execution = any(row.get("guard_state") == "missing_source" for row in execution_guard_rows)
    missing_state = any(row.get("guard_state") == "missing" for row in state_guard_rows)

    if not rank2_queue or not bundle:
        ready_state = "blocked_missing_inputs"
        hard_read = "缺少 Rank 2 queue 或 replay bundle 时，当前不应继续解释 operator 下一步。"
        next_action = "先重建 alpha_closure_board 相关 artifacts；不要继续沿旧 replay 读法推进。"
        waiting_for = "rank2 queue + next replay bundle regenerated"
    elif missing_execution or missing_state:
        ready_state = "blocked_missing_guard_inputs"
        hard_read = "有 guard 输入缺失时，当前最诚实的动作不是 replay，而是先补齐缺失依赖。"
        next_action = "先补齐缺失 source / artifact，再重建 alpha_closure_board。"
        waiting_for = "all guard inputs restored"
    elif not execution_synced:
        ready_state = "blocked_resync_execution_bundle"
        hard_read = "上游 evidence 已比 replay bundle 新；这时先 resync，比继续拿旧 bundle 做 operator 动作更诚实。"
        next_action = "先重建 Rank 2 replay bundle；guard 回到 synced 后再读 operator next step。"
        waiting_for = "rank2 execution-sync guard -> synced"
    elif not tiny_live_synced:
        ready_state = "blocked_resync_tiny_live_state"
        hard_read = "manual runner source 已比 closure-layer 新；当前先同步 tiny-live state，比继续读旧 queue 更诚实。"
        next_action = "先重建 alpha_closure_board closure-layer，再决定是否继续按当前 queue 推进。"
        waiting_for = "small_live state-resync guard -> synced"
    else:
        ready_state = "ready_for_one_test_no_fill_replay"
        hard_read = "当前所有已落地 guard 都表明：可以继续把 Rank 2 的下一步读成 1 次 whitelist-bound test/no-fill replay；成功也只推进到 shadow parity review eligible。"
        next_action = rank2_queue.get("next_allowed_action_now", bundle.get("replay_action", ""))
        waiting_for = rank2_queue.get("still_waiting_for", "same replay receipt chain refs")

    observed_at = rank2_queue.get("observed_at_utc", bundle.get("generated_at_utc", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")))
    rows = [
        {
            "gate_order": "0",
            "candidate": "Rank 2 / combo_all",
            "ready_state": ready_state,
            "bundle_leg_now": bundle.get("venue_symbol", "missing"),
            "action_owner_now": rank2_queue.get("action_owner_now", "run3 closure sync"),
            "execution_sync_state": "synced" if execution_synced else ("missing" if missing_execution else "needs_resync"),
            "tiny_live_state_sync": "synced" if tiny_live_synced else ("missing" if missing_state else "needs_resync"),
            "next_allowed_action_now": next_action,
            "still_waiting_for": waiting_for,
            "hard_stop": rank2_queue.get("hard_stop", bundle.get("hard_stop", "do not advance beyond shadow parity review eligible")),
            "hard_read": hard_read,
            "observed_at_utc": observed_at,
        }
    ]
    return rows


def write_rank2_replay_ready_gate_csv(rows: list[dict[str, str]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with SMALL_LIVE_RANK2_REPLAY_READY_GATE_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "gate_order",
                "candidate",
                "ready_state",
                "bundle_leg_now",
                "action_owner_now",
                "execution_sync_state",
                "tiny_live_state_sync",
                "next_allowed_action_now",
                "still_waiting_for",
                "hard_stop",
                "hard_read",
                "observed_at_utc",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def get_small_live_state_resync_guard_rows() -> list[dict[str, str]]:
    now = datetime.now(timezone.utc)

    def build_guard_row(*, guard_order: str, source_path: Path, dependent_path: Path, source_label: str, dependent_label: str, why_it_matters: str) -> dict[str, str]:
        if not source_path.exists() or not dependent_path.exists():
            return {
                "guard_order": guard_order,
                "source_file": source_label,
                "dependent_artifact": dependent_label,
                "source_file_mtime_utc": "missing" if not source_path.exists() else datetime.fromtimestamp(source_path.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                "dependent_artifact_mtime_utc": "missing" if not dependent_path.exists() else datetime.fromtimestamp(dependent_path.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                "lag_read": "missing",
                "guard_state": "missing",
                "why_it_matters": why_it_matters,
                "hard_read": "有文件缺失时，先补齐 source / artifact，再谈 tiny-live 当前态。",
                "required_action": "先重建缺失对象；不要继续按旧 queue / snapshot 行动。",
            }

        source_mtime = datetime.fromtimestamp(source_path.stat().st_mtime, tz=timezone.utc)
        dependent_mtime = datetime.fromtimestamp(dependent_path.stat().st_mtime, tz=timezone.utc)
        lag_minutes = int((source_mtime - dependent_mtime).total_seconds() // 60)
        source_age_minutes = max(0, int((now - source_mtime).total_seconds() // 60))

        if lag_minutes > 10:
            guard_state = "resync_due"
            hard_read = "source 已明显新于 closure-layer；继续引用旧 snapshot / queue 会把当前 tiny-live 状态读旧。"
            required_action = "优先重跑 alpha closure board builder，再解释 tiny-live 当前动作。"
        elif lag_minutes > 0:
            guard_state = "resync_soon"
            hard_read = "source 略新于 closure-layer；当前结论大概率没翻面，但 reader-facing 层最好尽快补同步。"
            required_action = "本轮若落到 Run 3，可优先做一次最小 resync。"
        else:
            guard_state = "synced"
            hard_read = "closure-layer 没落后于 source；可继续相信当前 now-action queue / snapshot。"
            required_action = "继续按现有 queue 行动；等下一次真实 source 更新后再检查。"

        if source_age_minutes < 60:
            source_age = f"source_newer_by={lag_minutes}m; source_age={source_age_minutes}m"
        else:
            source_age = f"source_newer_by={lag_minutes}m; source_age={source_age_minutes / 60:.1f}h"

        return {
            "guard_order": guard_order,
            "source_file": source_label,
            "dependent_artifact": dependent_label,
            "source_file_mtime_utc": source_mtime.strftime("%Y-%m-%d %H:%M UTC"),
            "dependent_artifact_mtime_utc": dependent_mtime.strftime("%Y-%m-%d %H:%M UTC"),
            "lag_read": source_age,
            "guard_state": guard_state,
            "why_it_matters": why_it_matters,
            "hard_read": hard_read,
            "required_action": required_action,
        }

    rows = [
        build_guard_row(
            guard_order="0",
            source_path=ROOT / "reports" / "artifacts" / "manual_narrow_paper_lanes" / "manual_narrow_paper_status.csv",
            dependent_path=SMALL_LIVE_STATUS_TRIGGER_SNAPSHOT_PATH,
            source_label="manual_narrow_paper_status.csv",
            dependent_label="small_live_status_trigger_snapshot_v1.csv",
            why_it_matters="status source 一旦更晚，Rank 17 / Rank 29 的 continuity / append 读法就可能已经变了。",
        ),
        build_guard_row(
            guard_order="1",
            source_path=ROOT / "reports" / "artifacts" / "manual_narrow_paper_lanes" / "manual_narrow_paper_last_run_summary.json",
            dependent_path=SMALL_LIVE_NOW_ACTION_QUEUE_PATH,
            source_label="manual_narrow_paper_last_run_summary.json",
            dependent_label="small_live_now_action_queue_v1.csv",
            why_it_matters="summary source 更晚时，now-action queue 可能还在替上一个 refresh 说话。",
        ),
    ]
    rows.sort(key=lambda r: (int(r["guard_order"]), r["source_file"]))
    return rows


def write_small_live_state_resync_guard_csv(rows: list[dict[str, str]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with SMALL_LIVE_STATE_RESYNC_GUARD_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "guard_order",
                "source_file",
                "dependent_artifact",
                "source_file_mtime_utc",
                "dependent_artifact_mtime_utc",
                "lag_read",
                "guard_state",
                "why_it_matters",
                "hard_read",
                "required_action",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def render() -> str:
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    rows = get_rows()
    promotion_gate_rows = get_promotion_gate_rows()
    small_live_plumbing_rows = get_small_live_plumbing_rows()
    small_live_ledger_rows = get_small_live_ledger_rows()
    small_live_routing_dry_run_rows = get_small_live_routing_dry_run_rows()
    small_live_routing_dry_run_sample_rows = get_small_live_routing_dry_run_sample_rows()
    small_live_operator_reconciliation_rows = get_small_live_operator_reconciliation_rows()
    small_live_operator_handoff_rows = get_small_live_operator_handoff_rows()
    small_live_review_ticket_template_rows = get_small_live_review_ticket_template_rows()
    small_live_review_writeback_matrix_rows = get_small_live_review_writeback_matrix_rows()
    small_live_review_registry_template_rows = get_small_live_review_registry_template_rows()
    small_live_shadow_parity_rows = get_small_live_shadow_parity_rows()
    small_live_parity_red_action_rows = get_small_live_parity_red_action_rows()
    small_live_shadow_parity_sample_rows = get_small_live_shadow_parity_sample_rows()
    small_live_green_shadow_parity_sample_rows = get_small_live_green_shadow_parity_sample_rows()
    small_live_reopen_gate_rows = get_small_live_reopen_gate_rows()
    small_live_reopen_resume_sample_rows = get_small_live_reopen_resume_sample_rows()
    rank2_closeout_snapshot_rows = get_rank2_closeout_snapshot_rows()
    rank2_receipt_audit_rows = get_rank2_receipt_audit_rows()
    rank2_replay_runsheet_rows = get_rank2_replay_runsheet_rows()
    rank2_replay_closeout_matrix_rows = get_rank2_replay_closeout_matrix_rows()
    rank2_shadow_parity_launch_packet_rows = get_rank2_shadow_parity_launch_packet_rows()
    rank2_shadow_parity_starter_rows = get_rank2_shadow_parity_starter_rows()
    rank2_next_status_change_gate_rows = get_rank2_next_status_change_gate_rows()
    rank2_next_replay_bundle_rows = get_rank2_next_replay_bundle_rows()
    rank2_replay_preflight_snapshot_rows = read_csv_rows(SMALL_LIVE_RANK2_REPLAY_PREFLIGHT_SNAPSHOT_PATH)
    rank2_execution_sync_guard_rows = get_rank2_execution_sync_guard_rows()
    baseline_compare_rows = get_baseline_compare_rows()
    small_live_default_seat_queue_rows = get_small_live_default_seat_queue_rows()
    small_live_live_seat_reentry_trigger_rows = get_small_live_live_seat_reentry_trigger_rows()
    small_live_status_change_watchboard_rows = get_small_live_status_change_watchboard_rows()
    small_live_status_trigger_snapshot_rows = get_small_live_status_trigger_snapshot_rows()
    small_live_now_action_queue_rows = get_small_live_now_action_queue_rows()
    small_live_evidence_freshness_board_rows = get_small_live_evidence_freshness_board_rows()
    small_live_state_resync_guard_rows = get_small_live_state_resync_guard_rows()
    rank2_execution_sync_guard_rows = get_rank2_execution_sync_guard_rows()
    rank2_replay_ready_gate_rows = get_rank2_replay_ready_gate_rows()

    def tone_cls(v: str) -> str:
        return {
            "good": "good",
            "park": "park",
        }.get(v, "neutral")

    cards = []
    for row in rows:
        cards.append(
            f"""
            <section class=\"track-card {tone_cls(row['tone'])}\">
              <div class=\"track-head\">
                <div>
                  <h2>{escape(row['title'])}</h2>
                  <p class=\"status\">{escape(row['status'])}</p>
                </div>
                <span class=\"pill\">资源顺序：{escape(row['priority'])} · paper admission：{escape(row['admission'])} · {escape(row['role'])}</span>
              </div>
              <div class=\"qa\">
                <div class=\"q\">当前最强证据</div>
                <div class=\"a\">{escape(row['evidence'])}</div>
              </div>
              <div class=\"qa\">
                <div class=\"q\">当前不能过度解读什么</div>
                <div class=\"a\">{escape(row['not_yet'])}</div>
              </div>
              <div class=\"qa\">
                <div class=\"q\">下一步最值得做什么</div>
                <div class=\"a\">{escape(row['next'])}</div>
              </div>
              <div class=\"actions\">
                <a class=\"btn\" href=\"{escape(row['main_link'])}\">{escape(row['main_label'])}</a>
                <a class=\"btn subtle\" href=\"{escape(row['side_link'])}\">{escape(row['side_label'])}</a>
              </div>
            </section>
            """.strip()
        )

    compare_rows = "".join(
        [
            "<tr>"
            f"<td>{escape(r['priority'])}</td>"
            f"<td>{escape(r['admission'])}</td>"
            f"<td>{escape(r['title'])}</td>"
            f"<td>{escape(r['role'])}</td>"
            f"<td>{escape(r['status'])}</td>"
            f"<td>{escape(r['next'])}</td>"
            "</tr>"
            for r in rows
        ]
    )

    promotion_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['stage'])}</td>"
            f"<td>{escape(r['who'])}</td>"
            f"<td>{escape(r['min_forward'])}</td>"
            f"<td>{escape(r['drawdown'])}</td>"
            f"<td>{escape(r['stop'])}</td>"
            f"<td>{escape(r['capital'])}</td>"
            f"<td>{escape(r['rollback'])}</td>"
            "</tr>"
            for r in promotion_gate_rows
        ]
    )

    baseline_compare_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['line'])}</td>"
            f"<td>{escape(r['current_rank'])}</td>"
            f"<td>{escape(r['ema_baseline_role'])}</td>"
            f"<td>{escape(r['current_increment'])}</td>"
            f"<td>{escape(r['why_not_above_ema'])}</td>"
            f"<td>{escape(r['next_honest_test'])}</td>"
            "</tr>"
            for r in baseline_compare_rows
        ]
    )

    small_live_default_seat_queue_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['queue_order'])}</td>"
            f"<td>{escape(r['seat_or_candidate'])}</td>"
            f"<td>{escape(r['current_stage'])}</td>"
            f"<td>{escape(r['tiny_live_review_now'])}</td>"
            f"<td>{escape(r['default_owner'])}</td>"
            f"<td>{escape(r['hard_blocker'])}</td>"
            f"<td>{escape(r['promotion_trigger'])}</td>"
            f"<td>{escape(r['evidence_note'])}</td>"
            "</tr>"
            for r in small_live_default_seat_queue_rows
        ]
    )

    small_live_live_seat_reentry_trigger_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['trigger_order'])}</td>"
            f"<td>{escape(r['seat_or_candidate'])}</td>"
            f"<td>{escape(r['current_stage'])}</td>"
            f"<td>{escape(r['status_change_event'])}</td>"
            f"<td>{escape(r['minimum_evidence_bundle'])}</td>"
            f"<td>{escape(r['next_allowed_stage'])}</td>"
            f"<td>{escape(r['why_not_now'])}</td>"
            "</tr>"
            for r in small_live_live_seat_reentry_trigger_rows
        ]
    )

    small_live_status_change_watchboard_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['watch_order'])}</td>"
            f"<td>{escape(r['seat_or_candidate'])}</td>"
            f"<td>{escape(r['current_stage'])}</td>"
            f"<td>{escape(r['where_to_watch'])}</td>"
            f"<td>{escape(r['default_owner'])}</td>"
            f"<td>{escape(r['what_event_wakes_tiny_live'])}</td>"
            f"<td>{escape(r['minimum_evidence'])}</td>"
            f"<td>{escape(r['if_event_lands'])}</td>"
            f"<td>{escape(r['if_event_missing'])}</td>"
            "</tr>"
            for r in small_live_status_change_watchboard_rows
        ]
    )

    small_live_status_trigger_snapshot_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['snapshot_order'])}</td>"
            f"<td>{escape(r['seat_or_candidate'])}</td>"
            f"<td>{escape(r['trigger_state_now'])}</td>"
            f"<td>{escape(r['latest_observed_evidence'])}</td>"
            f"<td>{escape(r['next_allowed_stage'])}</td>"
            f"<td>{escape(r['hard_read'])}</td>"
            f"<td>{escape(r['observed_at_utc'])}</td>"
            "</tr>"
            for r in small_live_status_trigger_snapshot_rows
        ]
    )

    small_live_now_action_queue_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['queue_order'])}</td>"
            f"<td>{escape(r['seat_or_candidate'])}</td>"
            f"<td>{escape(r['trigger_state_now'])}</td>"
            f"<td>{escape(r['action_owner_now'])}</td>"
            f"<td>{escape(r['next_allowed_action_now'])}</td>"
            f"<td>{escape(r['still_waiting_for'])}</td>"
            f"<td>{escape(r['hard_stop'])}</td>"
            f"<td>{escape(r['why_this_is_the_honest_next_step'])}</td>"
            f"<td>{escape(r['observed_at_utc'])}</td>"
            "</tr>"
            for r in small_live_now_action_queue_rows
        ]
    )

    small_live_evidence_freshness_board_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['freshness_order'])}</td>"
            f"<td>{escape(r['evidence_source'])}</td>"
            f"<td>{escape(r['backs_which_lane'])}</td>"
            f"<td>{escape(r['latest_file_mtime_utc'])}</td>"
            f"<td>{escape(r['approx_age'])}</td>"
            f"<td>{escape(r['freshness_state'])}</td>"
            f"<td>{escape(r['why_it_matters'])}</td>"
            f"<td>{escape(r['hard_read'])}</td>"
            "</tr>"
            for r in small_live_evidence_freshness_board_rows
        ]
    )

    small_live_state_resync_guard_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['guard_order'])}</td>"
            f"<td>{escape(r['source_file'])}</td>"
            f"<td>{escape(r['dependent_artifact'])}</td>"
            f"<td>{escape(r['source_file_mtime_utc'])}</td>"
            f"<td>{escape(r['dependent_artifact_mtime_utc'])}</td>"
            f"<td>{escape(r['lag_read'])}</td>"
            f"<td>{escape(r['guard_state'])}</td>"
            f"<td>{escape(r['why_it_matters'])}</td>"
            f"<td>{escape(r['hard_read'])}</td>"
            f"<td>{escape(r['required_action'])}</td>"
            "</tr>"
            for r in small_live_state_resync_guard_rows
        ]
    )

    small_live_plumbing_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['stage'])}</td>"
            f"<td>{escape(r['venue_mode'])}</td>"
            f"<td>{escape(r['capital_rule'])}</td>"
            f"<td>{escape(r['routing_rule'])}</td>"
            f"<td>{escape(r['ledger_rule'])}</td>"
            f"<td>{escape(r['mismatch_guard'])}</td>"
            f"<td>{escape(r['kill_switch'])}</td>"
            "</tr>"
            for r in small_live_plumbing_rows
        ]
    )

    small_live_ledger_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['field_order'])}</td>"
            f"<td>{escape(r['field_name'])}</td>"
            f"<td>{escape(r['required_stage'])}</td>"
            f"<td>{escape(r['fill_rule'])}</td>"
            f"<td>{escape(r['red_flag'])}</td>"
            f"<td>{escape(r['why_it_matters'])}</td>"
            "</tr>"
            for r in small_live_ledger_rows
        ]
    )

    small_live_routing_dry_run_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['step_order'])}</td>"
            f"<td>{escape(r['step_name'])}</td>"
            f"<td>{escape(r['required_input'])}</td>"
            f"<td>{escape(r['pass_rule'])}</td>"
            f"<td>{escape(r['block_on_fail'])}</td>"
            f"<td>{escape(r['ledger_fields'])}</td>"
            "</tr>"
            for r in small_live_routing_dry_run_rows
        ]
    )

    small_live_routing_dry_run_sample_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['row_kind'])}</td>"
            f"<td>{escape(r['candidate_id'])}</td>"
            f"<td>{escape(r['stage_status'])}</td>"
            f"<td>{escape(r['signal_bar_utc'])}</td>"
            f"<td>{escape(r['research_symbol'])}</td>"
            f"<td>{escape(r['venue_symbol'])}</td>"
            f"<td>{escape(r['side'])}</td>"
            f"<td>{escape(r['venue_mode'])}</td>"
            f"<td>{escape(r['route_intent_ts_utc'])}</td>"
            f"<td>{escape(r['route_ack_ts_utc'])}</td>"
            f"<td>{escape(r['cancel_ts_utc'])}</td>"
            f"<td>{escape(r['ack_latency_ms'])}</td>"
            f"<td>{escape(r['intended_notional_usd'])}</td>"
            f"<td>{escape(r['intended_qty'])}</td>"
            f"<td>{escape(r['rounded_qty'])}</td>"
            f"<td>{escape(r['mismatch_status'])}</td>"
            f"<td>{escape(r['operator_action'])}</td>"
            f"<td>{escape(r['operator_note'])}</td>"
            "</tr>"
            for r in small_live_routing_dry_run_sample_rows
        ]
    )

    small_live_operator_reconciliation_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['step_order'])}</td>"
            f"<td>{escape(r['operator_phase'])}</td>"
            f"<td>{escape(r['source_artifact'])}</td>"
            f"<td>{escape(r['what_to_check'])}</td>"
            f"<td>{escape(r['pass_output'])}</td>"
            f"<td>{escape(r['fail_output'])}</td>"
            f"<td>{escape(r['ledger_anchor'])}</td>"
            "</tr>"
            for r in small_live_operator_reconciliation_rows
        ]
    )

    small_live_operator_handoff_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['packet_order'])}</td>"
            f"<td>{escape(r['review_state'])}</td>"
            f"<td>{escape(r['open_bundle'])}</td>"
            f"<td>{escape(r['operator_goal'])}</td>"
            f"<td>{escape(r['expected_writeback'])}</td>"
            f"<td>{escape(r['hard_stop'])}</td>"
            "</tr>"
            for r in small_live_operator_handoff_rows
        ]
    )

    small_live_review_ticket_template_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['template_order'])}</td>"
            f"<td>{escape(r['review_state'])}</td>"
            f"<td>{escape(r['ticket_stub'])}</td>"
            f"<td>{escape(r['required_refs'])}</td>"
            f"<td>{escape(r['open_bundle'])}</td>"
            f"<td>{escape(r['success_closeout'])}</td>"
            f"<td>{escape(r['fail_closeout'])}</td>"
            "</tr>"
            for r in small_live_review_ticket_template_rows
        ]
    )

    small_live_review_writeback_matrix_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['matrix_order'])}</td>"
            f"<td>{escape(r['closeout_case'])}</td>"
            f"<td>{escape(r['ticket_status'])}</td>"
            f"<td>{escape(r['minimum_writeback'])}</td>"
            f"<td>{escape(r['same_ledger_or_registry'])}</td>"
            f"<td>{escape(r['next_queue'])}</td>"
            f"<td>{escape(r['hard_stop'])}</td>"
            "</tr>"
            for r in small_live_review_writeback_matrix_rows
        ]
    )

    small_live_review_registry_template_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['row_order'])}</td>"
            f"<td>{escape(r['registry_row_kind'])}</td>"
            f"<td>{escape(r['required_keys'])}</td>"
            f"<td>{escape(r['status_fields'])}</td>"
            f"<td>{escape(r['evidence_links'])}</td>"
            f"<td>{escape(r['ready_for_next_queue'])}</td>"
            f"<td>{escape(r['hard_stop'])}</td>"
            "</tr>"
            for r in small_live_review_registry_template_rows
        ]
    )

    small_live_shadow_parity_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['step_order'])}</td>"
            f"<td>{escape(r['step_name'])}</td>"
            f"<td>{escape(r['required_input'])}</td>"
            f"<td>{escape(r['pass_rule'])}</td>"
            f"<td>{escape(r['block_on_fail'])}</td>"
            f"<td>{escape(r['ledger_fields'])}</td>"
            "</tr>"
            for r in small_live_shadow_parity_rows
        ]
    )

    small_live_parity_red_action_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['action_order'])}</td>"
            f"<td>{escape(r['red_trigger'])}</td>"
            f"<td>{escape(r['operator_action'])}</td>"
            f"<td>{escape(r['route_handling'])}</td>"
            f"<td>{escape(r['ledger_writeback'])}</td>"
            f"<td>{escape(r['clear_to_retry'])}</td>"
            "</tr>"
            for r in small_live_parity_red_action_rows
        ]
    )

    small_live_shadow_parity_sample_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['row_kind'])}</td>"
            f"<td>{escape(r['candidate_id'])}</td>"
            f"<td>{escape(r['stage_status'])}</td>"
            f"<td>{escape(r['paper_ref_id'])}</td>"
            f"<td>{escape(r['live_shadow_ref_id'])}</td>"
            f"<td>{escape(r['research_symbol'])}</td>"
            f"<td>{escape(r['venue_symbol'])}</td>"
            f"<td>{escape(r['side'])}</td>"
            f"<td>{escape(r['intended_notional_usd'])}</td>"
            f"<td>{escape(r['intended_qty'])}</td>"
            f"<td>{escape(r['rounded_qty'])}</td>"
            f"<td>{escape(r['shadow_price'])}</td>"
            f"<td>{escape(r['cost_estimate_bps'])}</td>"
            f"<td>{escape(r['mismatch_status'])}</td>"
            f"<td>{escape(r['mismatch_reason'])}</td>"
            f"<td>{escape(r['operator_action'])}</td>"
            f"<td>{escape(r['trigger_reason'])}</td>"
            f"<td>{escape(r['reopen_earliest_ts'])}</td>"
            f"<td>{escape(r['operator_note'])}</td>"
            "</tr>"
            for r in small_live_shadow_parity_sample_rows
        ]
    )

    small_live_green_shadow_parity_sample_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['row_kind'])}</td>"
            f"<td>{escape(r['candidate_id'])}</td>"
            f"<td>{escape(r['stage_status'])}</td>"
            f"<td>{escape(r['paper_ref_id'])}</td>"
            f"<td>{escape(r['live_shadow_ref_id'])}</td>"
            f"<td>{escape(r['research_symbol'])}</td>"
            f"<td>{escape(r['venue_symbol'])}</td>"
            f"<td>{escape(r['side'])}</td>"
            f"<td>{escape(r['intended_notional_usd'])}</td>"
            f"<td>{escape(r['intended_qty'])}</td>"
            f"<td>{escape(r['rounded_qty'])}</td>"
            f"<td>{escape(r['shadow_price'])}</td>"
            f"<td>{escape(r['cost_estimate_bps'])}</td>"
            f"<td>{escape(r['mismatch_status'])}</td>"
            f"<td>{escape(r['mismatch_reason'])}</td>"
            f"<td>{escape(r['operator_action'])}</td>"
            f"<td>{escape(r['trigger_reason'])}</td>"
            f"<td>{escape(r['reopen_earliest_ts'])}</td>"
            f"<td>{escape(r['operator_note'])}</td>"
            "</tr>"
            for r in small_live_green_shadow_parity_sample_rows
        ]
    )

    small_live_reopen_gate_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['step_order'])}</td>"
            f"<td>{escape(r['reopen_step'])}</td>"
            f"<td>{escape(r['must_be_true'])}</td>"
            f"<td>{escape(r['if_not_true'])}</td>"
            f"<td>{escape(r['ledger_writeback'])}</td>"
            "</tr>"
            for r in small_live_reopen_gate_rows
        ]
    )

    small_live_reopen_resume_sample_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['row_kind'])}</td>"
            f"<td>{escape(r['candidate_id'])}</td>"
            f"<td>{escape(r['prior_red_ref_id'])}</td>"
            f"<td>{escape(r['stage_status'])}</td>"
            f"<td>{escape(r['paper_ref_id'])}</td>"
            f"<td>{escape(r['live_shadow_ref_id'])}</td>"
            f"<td>{escape(r['research_symbol'])}</td>"
            f"<td>{escape(r['venue_symbol'])}</td>"
            f"<td>{escape(r['side'])}</td>"
            f"<td>{escape(r['intended_notional_usd'])}</td>"
            f"<td>{escape(r['intended_qty'])}</td>"
            f"<td>{escape(r['rounded_qty'])}</td>"
            f"<td>{escape(r['shadow_price'])}</td>"
            f"<td>{escape(r['cost_estimate_bps'])}</td>"
            f"<td>{escape(r['mismatch_status'])}</td>"
            f"<td>{escape(r['mismatch_reason'])}</td>"
            f"<td>{escape(r['operator_action'])}</td>"
            f"<td>{escape(r['trigger_reason'])}</td>"
            f"<td>{escape(r['reopen_earliest_ts'])}</td>"
            f"<td>{escape(r['operator_note'])}</td>"
            "</tr>"
            for r in small_live_reopen_resume_sample_rows
        ]
    )

    rank2_closeout_snapshot_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['row_order'])}</td>"
            f"<td>{escape(r['research_symbol'])}</td>"
            f"<td>{escape(r['venue_symbol'])}</td>"
            f"<td>{escape(r['deployment_scope'])}</td>"
            f"<td>{escape(r['next_allowed_action'])}</td>"
            f"<td>{escape(r['allowed_operator_action'])}</td>"
            f"<td>{escape(r['pass_condition'])}</td>"
            f"<td>{escape(r['hard_stop'])}</td>"
            f"<td>{escape(r['current_blockers'])}</td>"
            "</tr>"
            for r in rank2_closeout_snapshot_rows
        ]
    )

    rank2_receipt_audit_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['audit_order'])}</td>"
            f"<td>{escape(r['research_symbol'])}</td>"
            f"<td>{escape(r['venue_symbol'])}</td>"
            f"<td>{escape(r['chain_status'])}</td>"
            f"<td>{escape(r['real_refs_landed'])}</td>"
            f"<td>{escape(r['missing_real_refs'])}</td>"
            f"<td>{escape(r['required_scope_guard'])}</td>"
            f"<td>{escape(r['required_capital_guard'])}</td>"
            f"<td>{escape(r['current_verdict'])}</td>"
            f"<td>{escape(r['next_queue'])}</td>"
            "</tr>"
            for r in rank2_receipt_audit_rows
        ]
    )

    rank2_replay_runsheet_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['replay_priority'])}</td>"
            f"<td>{escape(r['research_symbol'])}</td>"
            f"<td>{escape(r['venue_symbol'])}</td>"
            f"<td>{escape(r['venue_mode'])}</td>"
            f"<td>{escape(r['why_this_order'])}</td>"
            f"<td>{escape(r['operator_action'])}</td>"
            f"<td>{escape(r['must_capture_refs'])}</td>"
            f"<td>{escape(r['current_log_stub'])}</td>"
            f"<td>{escape(r['final_gate'])}</td>"
            f"<td>{escape(r['hard_stop'])}</td>"
            "</tr>"
            for r in rank2_replay_runsheet_rows
        ]
    )

    rank2_replay_closeout_matrix_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['replay_priority'])}</td>"
            f"<td>{escape(r['research_symbol'])}</td>"
            f"<td>{escape(r['venue_symbol'])}</td>"
            f"<td>{escape(r['current_log_stub'])}</td>"
            f"<td>{escape(r['review_ticket_to_open'])}</td>"
            f"<td>{escape(r['pass_closeout'])}</td>"
            f"<td>{escape(r['pass_writeback'])}</td>"
            f"<td>{escape(r['fail_closeout'])}</td>"
            f"<td>{escape(r['fail_writeback'])}</td>"
            f"<td>{escape(r['next_queue_if_pass'])}</td>"
            f"<td>{escape(r['next_queue_if_fail'])}</td>"
            "</tr>"
            for r in rank2_replay_closeout_matrix_rows
        ]
    )

    rank2_shadow_parity_launch_packet_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['launch_priority'])}</td>"
            f"<td>{escape(r['research_symbol'])}</td>"
            f"<td>{escape(r['venue_symbol'])}</td>"
            f"<td>{escape(r['dry_run_pass_trigger'])}</td>"
            f"<td>{escape(r['shadow_review_ticket_stub'])}</td>"
            f"<td>{escape(r['paper_ref_stub'])}</td>"
            f"<td>{escape(r['live_shadow_ref_stub'])}</td>"
            f"<td>{escape(r['first_shadow_writeback'])}</td>"
            f"<td>{escape(r['hard_stop'])}</td>"
            "</tr>"
            for r in rank2_shadow_parity_launch_packet_rows
        ]
    )

    rank2_shadow_parity_starter_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['launch_priority'])}</td>"
            f"<td>{escape(r['research_symbol'])}</td>"
            f"<td>{escape(r['venue_symbol'])}</td>"
            f"<td>{escape(r['shadow_review_ticket_stub'])}</td>"
            f"<td>{escape(r['paper_ref_id_stub'])}</td>"
            f"<td>{escape(r['live_shadow_ref_id_stub'])}</td>"
            f"<td>{escape(r['stage_status'])}</td>"
            f"<td>{escape(r['mismatch_status'])}</td>"
            f"<td>{escape(r['operator_action'])}</td>"
            f"<td>{escape(r['minimum_writeback'])}</td>"
            f"<td>{escape(r['pending_fields_before_closeout'])}</td>"
            f"<td>{escape(r['hard_boundary'])}</td>"
            "</tr>"
            for r in rank2_shadow_parity_starter_rows
        ]
    )

    rank2_next_status_change_gate_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['gate_order'])}</td>"
            f"<td>{escape(r['gate_name'])}</td>"
            f"<td>{escape(r['current_state'])}</td>"
            f"<td>{escape(r['what_counts'])}</td>"
            f"<td>{escape(r['what_does_not_count'])}</td>"
            f"<td>{escape(r['why'])}</td>"
            f"<td>{escape(r['evidence_ready_today'])}</td>"
            f"<td>{escape(r['next_queue_if_done'])}</td>"
            "</tr>"
            for r in rank2_next_status_change_gate_rows
        ]
    )

    rank2_next_replay_bundle_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['bundle_order'])}</td>"
            f"<td>{escape(r['research_symbol'])}</td>"
            f"<td>{escape(r['venue_symbol'])}</td>"
            f"<td>{escape(r['why_this_leg_now'])}</td>"
            f"<td>{escape(r['sample_notional_usdt'])}</td>"
            f"<td>{escape(r['sample_budget_read'])}</td>"
            f"<td>{escape(r['replay_action'])}</td>"
            f"<td>{escape(r['must_capture_refs'])}</td>"
            f"<td>{escape(r['current_log_stub'])}</td>"
            f"<td>{escape(r['if_pass'])}</td>"
            f"<td>{escape(r['parity_ticket_stub_if_pass'])}</td>"
            f"<td>{escape(r['hard_stop'])}</td>"
            "</tr>"
            for r in rank2_next_replay_bundle_rows
        ]
    )

    rank2_execution_sync_guard_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['source_file'])}</td>"
            f"<td>{escape(r['source_role'])}</td>"
            f"<td>{escape(r['dependent_artifact'])}</td>"
            f"<td>{escape(r['source_mtime_utc'])}</td>"
            f"<td>{escape(r['dependent_mtime_utc'])}</td>"
            f"<td>{escape(r['lag_read'])}</td>"
            f"<td>{escape(r['guard_state'])}</td>"
            f"<td>{escape(r['hard_read'])}</td>"
            f"<td>{escape(r['required_action'])}</td>"
            "</tr>"
            for r in rank2_execution_sync_guard_rows
        ]
    )

    rank2_replay_ready_gate_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['candidate'])}</td>"
            f"<td>{escape(r['ready_state'])}</td>"
            f"<td>{escape(r['bundle_leg_now'])}</td>"
            f"<td>{escape(r['action_owner_now'])}</td>"
            f"<td>{escape(r['execution_sync_state'])}</td>"
            f"<td>{escape(r['tiny_live_state_sync'])}</td>"
            f"<td>{escape(r['next_allowed_action_now'])}</td>"
            f"<td>{escape(r['still_waiting_for'])}</td>"
            f"<td>{escape(r['hard_stop'])}</td>"
            f"<td>{escape(r['hard_read'])}</td>"
            f"<td>{escape(r['observed_at_utc'])}</td>"
            "</tr>"
            for r in rank2_replay_ready_gate_rows
        ]
    )

    rank2_replay_preflight_snapshot_rows_html = "".join(
        [
            "<tr>"
            f"<td>{escape(r['preflight_priority'])}</td>"
            f"<td>{escape(r['research_symbol'])}</td>"
            f"<td>{escape(r['venue_symbol'])}</td>"
            f"<td>{escape(r['sample_notional_usdt'])}</td>"
            f"<td>{escape(r['rounded_notional_usdt'])}</td>"
            f"<td>{escape(r['qty_rounding_loss_bps'])}</td>"
            f"<td>{escape(r['replay_priority_verdict'])}</td>"
            f"<td>{escape(r['min_notional_check'])}</td>"
            f"<td>{escape(r['hard_read'])}</td>"
            "</tr>"
            for r in rank2_replay_preflight_snapshot_rows
        ]
    )

    replay_context = get_rank2_replay_priority_context()
    rank2_replay_order_text = escape(str(replay_context["order_text"]))
    rank2_replay_policy_blurb = escape(str(replay_context["policy_blurb"]))

    return f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Current Alpha Closure Board</title>
  <style>
    :root {{
      --fg:#0f172a; --muted:#64748b; --bg:#f8fafc; --card:#ffffff; --border:#e2e8f0;
      --good:#ecfdf5; --good-b:#86efac; --park:#fff7ed; --park-b:#fdba74; --neutral:#eff6ff; --neutral-b:#93c5fd;
      --link:#2563eb;
    }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; background:var(--bg); color:var(--fg); }}
    a {{ color:var(--link); text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
    .wrap {{ max-width:1240px; margin:0 auto; padding:28px 18px 52px; }}
    .hero, .track-card, .card {{ background:var(--card); border:1px solid var(--border); border-radius:18px; }}
    .hero {{ padding:24px 26px; margin-bottom:18px; }}
    .hero h1 {{ margin:0 0 10px; font-size:34px; line-height:1.18; }}
    .muted {{ color:var(--muted); }}
    .pills {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:12px; }}
    .pill {{ display:inline-block; padding:5px 10px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; }}
    .summary-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:12px; margin-top:18px; }}
    .summary-box {{ border:1px solid var(--border); border-radius:14px; background:#fff; padding:14px 16px; }}
    .summary-box h3 {{ margin:0 0 8px; font-size:17px; }}
    .section-title {{ margin:22px 0 10px; font-size:22px; }}
    .tracks {{ display:grid; gap:14px; }}
    .track-card {{ padding:18px 20px; }}
    .track-card.good {{ background:linear-gradient(180deg, #ffffff 0%, var(--good) 100%); border-color:var(--good-b); }}
    .track-card.park {{ background:linear-gradient(180deg, #ffffff 0%, var(--park) 100%); border-color:var(--park-b); }}
    .track-head {{ display:flex; justify-content:space-between; gap:16px; align-items:flex-start; }}
    .track-head h2 {{ margin:0 0 6px; font-size:24px; line-height:1.25; }}
    .status {{ margin:0; color:var(--muted); }}
    .qa {{ margin-top:14px; }}
    .q {{ font-weight:700; margin-bottom:6px; }}
    .a {{ color:#334155; line-height:1.75; }}
    .actions {{ display:flex; flex-wrap:wrap; gap:10px; margin-top:16px; }}
    .btn {{ display:inline-block; padding:9px 12px; border-radius:10px; border:1px solid var(--border); background:white; }}
    .btn.subtle {{ background:#f8fafc; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; background:white; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:10px 12px; text-align:left; vertical-align:top; }}
    th {{ background:#f8fafc; }}
    ul {{ margin:0; padding-left:20px; line-height:1.7; }}
    code {{ background:#eff6ff; border-radius:6px; padding:1px 4px; }}
    @media (max-width:900px) {{ .track-head {{ flex-direction:column; }} }}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <p><a href=\"../../index.html\">← 返回站点首页</a></p>
    <div class=\"hero\">
      <h1>Current Alpha Closure Board</h1>
      <p class=\"muted\">这页只做一件事：把当前最重要的三条收口线并排讲清楚，回答 <b>现在最值得继续做什么、什么该讲清楚、什么该收口归档</b>。</p>
      <div class=\"pills\">
        <span class=\"pill\">当前阶段：closure-first</span>
        <span class=\"pill\">生成时间：{escape(generated)}</span>
        <span class=\"pill\">不是实盘决策页；是研发排优先级页</span>
      </div>
      <div class=\"summary-grid\">
        <div class=\"summary-box\">
          <h3>如果只看“谁最接近 paper trading”</h3>
          <p class=\"muted\"><b>EMA / PSAR</b> 当前是 <b>closest to paper</b>：已经有 final survivor map + paper candidate / operating / monitoring spec + runbook，并已落下首份 day-0 ledger snapshot + first-refresh queue。<b>breakout-short follow-up</b> 当前更诚实的 reader-facing 结论已改成 <b>bench</b>：它仍保留条件性 alpha 价值与完整证据链，但在“唯一一枪”打完后，关键 blocker 仍停在 <code>pure_down=0/100</code>、<code>predown_bridge_12h=0/11</code>、<code>downrisk_48h=0/109</code>、<code>future_pure_down_48h=0/44</code>，因此不再占用默认主资源。<b>Fibonacci</b> 则已进入 <b>park / archive</b>。</p>
        </div>
        <div class=\"summary-box\">
          <h3>如果只看“网页先该怎么讲”</h3>
          <p class=\"muted\">先把三条线的 <b>当前结论 / 不支持什么 / 下一步</b> 写清楚，再去补图，不要先堆页面数量。</p>
        </div>
        <div class=\"summary-box\">
          <h3>如果只看“什么时候再去找新 alpha”</h3>
          <p class=\"muted\">等这三条线完成一轮更完整的成本 / OOS / rolling / 角色判断后，再决定是否回拨更多资源给外部 alpha scouting。</p>
        </div>
      </div>
    </div>

    <div class=\"card\" style=\"padding:18px 20px; margin-top:18px;\">
      <h2 style=\"margin:0 0 8px;\">从现在到 paper trading / 小资金实盘的路线图</h2>
      <p class=\"muted\">这张路线图不是收益承诺，也不是“快要上实盘”的营销图；它只是把当前项目强制放进同一条 deployment ladder 里，回答：<b>我们现在到底在哪一格，离 `paper trading` 和小资金实盘还差哪几道硬门槛</b>。</p>
      <table>
        <thead>
          <tr>
            <th>Step</th>
            <th>这一步在回答什么</th>
            <th>当前状态</th>
            <th>离部署还差什么</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Step 1 — 收口 / survivor map / archived map</td>
            <td>把候选分成 keep / mixed-watch / archive，先回答“还有什么值得留下来”。</td>
            <td>基本完成：三条线的 keep / park / mixed 边界已经清楚。</td>
            <td>这一层本身不够，下一步必须进入更 deployment-facing 的 admission gate。</td>
          </tr>
          <tr>
            <td>Step 2 — admission gate / candidate spec</td>
            <td>回答谁有资格进入 paper-admission queue，当前 verdict 是 `paper-now / bench / park` 哪一个。</td>
            <td><b>我们现在主要就在这一步。</b> EMA 已经到 `closest to paper`；breakout 已正式转成 `bench`；Fib 已 park。</td>
            <td>要把候选从“看起来值得做”推进成“可以真正准备跑 shadow / paper”，或者诚实地退出默认资源位。</td>
          </tr>
          <tr>
            <td>Step 3 — operating spec / monitoring board / shadow-ready runbook</td>
            <td>回答如果真开始伪实盘，该盯哪些市场、哪些 symbol、怎样记账、怎样升降级。</td>
            <td>EMA 已基本补齐：已有 candidate spec / operating spec / monitoring board / runbook，并已落下一份 day-0 ledger snapshot + first-refresh queue；breakout 还没完全到这层。</td>
            <td>EMA 已从 runbook 走到首笔 day-0 账本记录与首刷顺序；下一步不是再补页面，而是按同一张 queue 继续做真实 shadow / paper refresh。</td>
          </tr>
          <tr>
            <td>Step 4 — 真实 paper trading / shadow run</td>
            <td>在真实前瞻观察下检验路径、回撤、停机条件、promotion/demotion 是否还成立。</td>
            <td>尚未开始，但现在已有一版项目级 `promotion gate v1` 可直接约束 paper -> live 顺序。</td>
            <td>需要先按同一套 gate 跑出真实 forward 账本，而不是从研究页直接跳到真钱。</td>
          </tr>
          <tr>
            <td>Step 5 — 小资金实盘试点</td>
            <td>在通过 paper/shadow gate 后，用 capital cap / kill switch / rollback rules 做最小 live pilot。</td>
            <td>尚未开始；但 `capital cap / kill switch / rollback` 的项目级底线已固定成 v1。</td>
            <td>仍不能跳过 Step 4；要先满足最短观察期、回撤护栏、以及监控板连续不过红线。</td>
          </tr>
        </tbody>
      </table>
      <div class=\"summary-grid\" style=\"margin-top:14px;\">
        <div class=\"summary-box\">
          <h3>我们当前在哪</h3>
          <p class=\"muted\"><b>EMA</b> 大致位于 <b>Step 3.6</b>：runbook、day-0 ledger snapshot 与 first-refresh queue 都已落地，等于已经迈出第一笔 `0` 真资金记账动作并写清首刷顺序，但还没积累出真实 forward review。<b>breakout</b> 当前更诚实的位置已不是继续卡在 `one_more_gate`，而是完成 hard verdict 后退回 <b>bench</b>：保留证据，但退出默认主资源位。<b>Fibonacci</b> 已固定在 `park / archive`。</p>
        </div>
        <div class=\"summary-box\">
          <h3>离 paper trading 还有多远</h3>
          <p class=\"muted\"><b>EMA：</b>首份 day-0 ledger snapshot 与 first-refresh queue 都已经落表，离真正 paper trading 不再差“要不要开账”，而是差后续真实 refresh / week-1 review 能不能按同一张 queue 持续跑下去。<b>breakout：</b>当前已不再默认排队争夺 shadow-ready，而是先退回 `bench`；除非后续拿出 genuinely new blocker reduction，否则不再继续消耗默认主资源。</p>
        </div>
        <div class=\"summary-box\">
          <h3>离小资金实盘还有多远</h3>
          <p class=\"muted\">现在终于不只是“更远一些”这句空话了：项目级 `promotion gate v1` 已写清 <b>最短观察期 / 回撤护栏 / kill switch / capital cap / rollback</b>，随后又把 <b>routing dry-run / live ledger / mismatch guard</b> 压成了 tiny-live plumbing board，并继续补出 <b>routing dry-run checklist + paper-live shadow parity checklist</b>。也就是说，当前不只知道“什么时候才配上 live”，还知道上 live 前先要按什么执行栏位做检查、以及进入 `paper vs live-shadow` 同步审计时要先锁哪些红旗。但因为两条主候选都还没跑出真正的 forward 观察期，所以正确顺序仍不变：<b>EMA 先沿已落地的 day-0 ledger snapshot + first-refresh queue 持续进入 paper/shadow refresh，breakout 先清掉最后一道 gate，再谈 small live</b>。</p>
        </div>
      </div>
    </div>

    <div class=\"card\" style=\"padding:18px 20px; margin-top:18px;\">
      <h2 style=\"margin:0 0 8px;\">如果把 EMA 视为默认 baseline：结构层现在有没有增量价值？</h2>
      <p class=\"muted\">这张表不是在问“结构事件有没有一点 alpha 感”，而是更 deployment-facing 地问：<b>它们有没有比当前 EMA baseline 更诚实地拿到 paper admission 资格，或者至少明确展示出值得并列保留的增量价值。</b> 当前项目级答案已经能先写死：EMA 仍是默认 baseline seat；breakout 还在争取有条件并列资格；Fib 则已退出主资源竞争。</p>
      <table>
        <thead>
          <tr>
            <th>研究线</th>
            <th>当前相对 EMA 的排位</th>
            <th>EMA 在这张比较里的角色</th>
            <th>当前是否已证明增量价值</th>
            <th>为什么还不能高于 EMA</th>
            <th>下一刀什么才算有效比较</th>
          </tr>
        </thead>
        <tbody>{baseline_compare_rows_html}</tbody>
      </table>
      <p class=\"muted\" style=\"margin-top:12px;\">artifact：<code>reports/artifacts/alpha_closure_board/structure_vs_ema_baseline_v1.csv</code></p>
    </div>

    <div class=\"card\" style=\"padding:18px 20px; margin-top:18px;\">
      <h2 style=\"margin:0 0 8px;\">Paper trading → 小资金实盘 promotion gate（v1）</h2>
      <p class=\"muted\">这不是“准备马上上实盘”的承诺，而是一套更保守的项目级底线：只有先跑出真实 paper / shadow 账本，并满足同一套最短观察期、回撤护栏、停机条件、capital cap 与 rollback 规则，才配讨论小资金 pilot。</p>
      <table>
        <thead>
          <tr>
            <th>阶段</th>
            <th>适用对象</th>
            <th>最小前瞻观察</th>
            <th>回撤 / 路径护栏</th>
            <th>停机 / kill switch</th>
            <th>资金上限</th>
            <th>rollback 规则</th>
          </tr>
        </thead>
        <tbody>{promotion_rows_html}</tbody>
      </table>
      <p class=\"muted\" style=\"margin-top:12px;\">artifact：<code>reports/artifacts/alpha_closure_board/paper_live_promotion_gate_v1.csv</code></p>
    </div>

    <div class="card" style="padding:18px 20px; margin-top:18px;">
      <h2 style="margin:0 0 8px;">Small-live default seat queue（v1）</h2>
      <p class="muted">这张表只回答一个更容易被误读的问题：<b>当前有没有哪条 lane 会因为自己属于 P3 / narrow paper、或者还有 open paper positions，就自动重回 tiny-live / Live Seat review</b>。当前统一答案都是 <code>no</code>：默认 <b>Live Seat 继续留空</b>，除非 bot2 明确点名新的 promoted candidate；否则 Rank 2 / 17 / 29 只分别停在 closeout、manual refresh continuity、或 paper-only monitoring。</p>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>seat / candidate</th>
            <th>当前阶段</th>
            <th>现在可进 tiny-live review?</th>
            <th>默认 owner</th>
            <th>当前硬阻断</th>
            <th>什么条件下才配重开</th>
            <th>证据备注</th>
          </tr>
        </thead>
        <tbody>{small_live_default_seat_queue_rows_html}</tbody>
      </table>
      <div class="summary-grid" style="margin-top:14px;">
        <div class="summary-box">
          <h3>当前 hard verdict</h3>
          <p class="muted"><b>Live Seat = empty by default</b>。P3 身份、open paper positions、或 narrow-paper continuity 本身都不再自动占位。</p>
        </div>
        <div class="summary-box">
          <h3>为什么这张表有用</h3>
          <p class="muted">它把“默认空席”与“什么情况下才允许重新进 tiny-live review”写成 deployable queue，避免后续继续把 Rank 17 的 open positions 或 Rank 29 的 P3 身份误读成 bot3 / operator 现在就该接手的 live review。</p>
        </div>
        <div class="summary-box">
          <h3>当前唯一更接近动作的一条线</h3>
          <p class="muted">只有 <b>Rank 2</b> 还保留一个更贴近执行的 closeout blocker：同一条 whitelist-bound <code>test/no-fill</code> replay 的真实 receipt chain。即便这一步过了，也只是进入 <code>shadow_parity</code>，仍不是 tiny-live 放行。</p>
        </div>
      </div>
      <p class="muted" style="margin-top:12px;">artifact：<code>reports/artifacts/alpha_closure_board/small_live_default_seat_queue_v1.csv</code></p>
    </div>

    <div class="card" style="padding:18px 20px; margin-top:18px;">
      <h2 style="margin:0 0 8px;">Live Seat re-entry trigger matrix（v1）</h2>
      <p class="muted">这张表不是再谈“谁研究上更好看”，而是把 <b>什么事件才真的允许 Live Seat 从空席变成 review 中</b> 压成统一 trigger matrix。它把当前 desk 最容易滑坡的边界写死：<b>默认空席</b>、<b>Rank 2 只有真实 replay 才能改状态</b>、<b>Rank 17 / Rank 29 只有在 manual runner 真新增 append/review 行且 bot2 明确升格时，才配进入 P4 / tiny-live review</b>。</p>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>seat / candidate</th>
            <th>当前阶段</th>
            <th>唯一 status-changing 事件</th>
            <th>最小证据包</th>
            <th>下一步只允许到哪</th>
            <th>为什么现在还不行</th>
          </tr>
        </thead>
        <tbody>{small_live_live_seat_reentry_trigger_rows_html}</tbody>
      </table>
      <div class="summary-grid" style="margin-top:14px;">
        <div class="summary-box">
          <h3>当前 hard verdict</h3>
          <p class="muted"><b>Live Seat 现在没有任何 auto-reentry 通道</b>。没有 bot2 明确 promotion，就默认继续空席。</p>
        </div>
        <div class="summary-box">
          <h3>对 Rank 2 的止损含义</h3>
          <p class="muted">它把 <b>“真正会改状态的只剩真实 whitelist-bound replay”</b> 再压成一张 desk-level trigger matrix；所以后续没有 receipt refs 时，不该再把相邻 packet / wording 当进展。</p>
        </div>
        <div class="summary-box">
          <h3>对 Rank 17 / 29 的止滑含义</h3>
          <p class="muted">open paper positions 或 manual continuity 只是运行状态，不是 re-entry trigger。只有 <b>新 append/review 行 + bot2 明确升格</b> 才配进 P4 / tiny-live review。</p>
        </div>
      </div>
      <p class="muted" style="margin-top:12px;">artifact：<code>reports/artifacts/alpha_closure_board/small_live_live_seat_reentry_trigger_matrix_v1.csv</code></p>
    </div>

    <div class="card" style="padding:18px 20px; margin-top:18px;">
      <h2 style="margin:0 0 8px;">Tiny-live status-change watchboard（v1）</h2>
      <p class="muted">这张表不是再增加一层 closeout 文档，而是把 <b>未来到底要盯哪个外部事件、在哪个文件里出现、谁负责、出现后只允许推进到哪一步</b> 压成统一 watchboard。它解决的是当前 Run 3 最容易继续空磨的问题：<b>没有真实 status-changing 事件时，bot3 不该继续把 tiny-live 资源花在近义 packet 上；有事件时，也要知道该看哪条证据链</b>。</p>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>seat / candidate</th>
            <th>当前阶段</th>
            <th>去哪里看</th>
            <th>默认 owner</th>
            <th>什么事件才会唤醒 tiny-live</th>
            <th>最小证据</th>
            <th>事件出现后只允许推进到哪</th>
            <th>事件没出现时该怎么读</th>
          </tr>
        </thead>
        <tbody>{small_live_status_change_watchboard_rows_html}</tbody>
      </table>
      <div class="summary-grid" style="margin-top:14px;">
        <div class="summary-box">
          <h3>当前 hard verdict</h3>
          <p class="muted"><b>现在 tiny-live 侧真正该看的不是更多近义文档，而是 status-changing 事件本身有没有落地。</b> 没有事件，就继续 empty / blocked / continuity-only；有事件，也必须沿既定证据链推进，而不是跳步。</p>
        </div>
        <div class="summary-box">
          <h3>为什么这张表比继续补 packet 更值钱</h3>
          <p class="muted">因为它把 <b>watch source + owner + wake event + next allowed stage</b> 放到同一张表里。以后不管是 Rank 2 receipt refs、还是 Rank 17 / 29 的 append-review 行，都能先回答“到底该看哪里、看到什么才算数”。</p>
        </div>
        <div class="summary-box">
          <h3>对当前 desk 排班的含义</h3>
          <p class="muted">当 `EMA = waiting_not_due` 且 `Scout fast lane = temporarily exhausted` 时，Run 3 默认也不该无限长在同一条 doc-chain 上；更诚实的做法是守着这张 watchboard，等真正的 status-changing event 出现再接力。</p>
        </div>
      </div>
      <p class="muted" style="margin-top:12px;">artifact：<code>reports/artifacts/alpha_closure_board/small_live_status_change_watchboard_v1.csv</code></p>
    </div>

    <div class="card" style="padding:18px 20px; margin-top:18px;">
      <h2 style="margin:0 0 8px;">Tiny-live trigger snapshot（live now）</h2>
      <p class="muted">watchboard 负责告诉后续轮次 <b>该看哪里</b>；这张快照则直接回答 <b>现在有没有任何 tiny-live 相关事件已经落地</b>。这里刻意把两件事拆开：<b>P3 continuity 事件</b>（例如 manual runner 刚追加了新的 closed trade / review 行）应该被如实标出来，但它 <b>不等于</b> tiny-live re-entry；真正要从 `paper / continuity` 升到 `tiny-live review`，仍然必须额外满足 `bot2 promotion`（以及 Rank 2 的 receipt refs / Rank 29 的 red-watch 约束）。因此读这张表时，先看有没有新事件，再看它最多只允许推进到哪一步。</p>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>seat / candidate</th>
            <th>当前触发状态</th>
            <th>最新观察证据</th>
            <th>若触发也只允许推进到哪</th>
            <th>当前硬读法</th>
            <th>观察时间</th>
          </tr>
        </thead>
        <tbody>{small_live_status_trigger_snapshot_rows_html}</tbody>
      </table>
      <div class="summary-grid" style="margin-top:14px;">
        <div class="summary-box">
          <h3>当前 hard verdict</h3>
          <p class="muted"><b>现在没有任何一条 tiny-live re-entry trigger 已经落地。</b> 所以当前不是“快上 tiny-live 了”，而是继续保持默认空席、Rank 2 blocked、Rank 17 / 29 continuity-only。</p>
        </div>
        <div class="summary-box">
          <h3>为什么这张表比继续补 wording 更值钱</h3>
          <p class="muted">因为它把静态规则换成了 <b>live-now snapshot</b>：后续轮次可以直接先看 trigger 有没有真变化，而不是再猜“是不是已经快够了”。</p>
        </div>
        <div class="summary-box">
          <h3>对 desk 排班的含义</h3>
          <p class="muted">只要这张快照继续显示 trigger 没落地，Run 3 就不该再次围着同一条 tiny-live 文档链打转；应该继续等真实事件，或在允许时切回 Scout / Paper 主线。</p>
        </div>
      </div>
      <p class="muted" style="margin-top:12px;">artifact：<code>reports/artifacts/alpha_closure_board/small_live_status_trigger_snapshot_v1.csv</code></p>
    </div>

    <div class="card" style="padding:18px 20px; margin-top:18px;">
      <h2 style="margin:0 0 8px;">Tiny-live evidence freshness board（v1）</h2>
      <p class="muted">这张表不再重复“谁该等谁该动”，而是补 tiny-live 侧一个更容易被忽略的真实 blocker：<b>我们现在看的这些 watch source，到底够不够新</b>。如果 desk board、Rank 2 audit 或 manual runner summary 已经变陈旧，那“继续空席 / 继续 blocked / 继续 continuity-only”的结论就可能只是读旧快照。</p>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>证据源</th>
            <th>支撑哪条 lane</th>
            <th>最新文件时间</th>
            <th>大概年龄</th>
            <th>freshness</th>
            <th>为什么重要</th>
            <th>当前 hard read</th>
          </tr>
        </thead>
        <tbody>{small_live_evidence_freshness_board_rows_html}</tbody>
      </table>
      <div class="summary-grid" style="margin-top:14px;">
        <div class="summary-box">
          <h3>这轮新增的价值</h3>
          <p class="muted"><b>先校验证据是不是还新，再决定 tiny-live 该不该继续等待。</b> 这能避免后续轮次把“没有 trigger”误读成真实静止，实际上只是监控源太旧。</p>
        </div>
        <div class="summary-box">
          <h3>对当前 desk 的意义</h3>
          <p class="muted">当 `EMA = waiting_not_due`、Scout 又暂时耗尽时，Run 3 最诚实的工作之一就是把 tiny-live 监控链做成可审计。freshness board 让后续知道：应该继续相信当前 snapshot，还是先等下一次 source refresh。</p>
        </div>
        <div class="summary-box">
          <h3>默认动作</h3>
          <p class="muted">若 source 仍 fresh，就继续遵守 now-action queue；若转 stale，优先补新 snapshot / refresh，而不是继续写 tiny-live 近义说明页。</p>
        </div>
      </div>
      <p class="muted" style="margin-top:12px;">artifact：<code>reports/artifacts/alpha_closure_board/small_live_evidence_freshness_board_v1.csv</code></p>
    </div>

    <div class="card" style="padding:18px 20px; margin-top:18px;">
      <h2 style="margin:0 0 8px;">Tiny-live state resync guard（v1）</h2>
      <p class="muted">这张表把上轮暴露出来的一个真实执行坑压成了 deployable guardrail：<b>当 manual runner source 已经更新时，closure-layer 的 snapshot / queue / 网页入口有没有跟上</b>。它不是再写一遍 tiny-live 规则，而是回答：<b>什么时候必须先 resync，什么时候才配继续相信当前 reader-facing 解释</b>。</p>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>source file</th>
            <th>dependent artifact</th>
            <th>source 时间</th>
            <th>artifact 时间</th>
            <th>lag read</th>
            <th>guard state</th>
            <th>为什么重要</th>
            <th>当前 hard read</th>
            <th>required action</th>
          </tr>
        </thead>
        <tbody>{small_live_state_resync_guard_rows_html}</tbody>
      </table>
      <div class="summary-grid" style="margin-top:14px;">
        <div class="summary-box">
          <h3>这轮新增的价值</h3>
          <p class="muted"><b>不是等到看错状态后才补 sync。</b> guard 表会直接告诉后续轮次：当前 closure-layer 是同步的，还是已经落后于 source。</p>
        </div>
        <div class="summary-box">
          <h3>对当前 desk 的意义</h3>
          <p class="muted">当 `EMA = waiting_not_due` 且 Scout 暂时 exhaustion 时，Run 3 最容易退化成“继续解释旧状态”。这个 guard 让 bot3 / operator 先回答：该先 resync，还是可以继续按 now-action queue 执行。</p>
        </div>
        <div class="summary-box">
          <h3>默认动作</h3>
          <p class="muted">若 guard state = `resync_due / resync_soon`，优先重跑 closure board builder；只有 guard state 回到 `synced`，才继续相信当前网页上的 tiny-live 解释。</p>
        </div>
      </div>
      <p class="muted" style="margin-top:12px;">artifact：<code>reports/artifacts/alpha_closure_board/small_live_state_resync_guard_v1.csv</code></p>
    </div>

    <div class="card" style="padding:18px 20px; margin-top:18px;">
      <h2 style="margin:0 0 8px;">Rank 2 replay execution sync guard（v1）</h2>
      <p class="muted">这张 guard 不再回答“现在先做哪一腿”，而是专门回答：<b>当前 reader-facing 的 Rank 2 replay bundle 还跟不跟得上它依赖的 preflight / rounding / receipt-audit / runsheet</b>。如果上游 evidence 比 bundle 更新，就先重建 bundle；别拿旧页面继续解释 whitelist replay 顺序。</p>
      <table>
        <thead>
          <tr>
            <th>source</th>
            <th>source role</th>
            <th>dependent</th>
            <th>source mtime</th>
            <th>dependent mtime</th>
            <th>lag read</th>
            <th>guard</th>
            <th>hard read</th>
            <th>required action</th>
          </tr>
        </thead>
        <tbody>{rank2_execution_sync_guard_rows_html}</tbody>
      </table>
      <div class="summary-grid" style="margin-top:16px;">
        <div class="summary-box">
          <h3>这轮新增的价值</h3>
          <p class="muted"><b>不是再写一张 Rank 2 说明页。</b> 而是明确告诉 future run：只要 bundle 落后于上游 evidence，先 resync，再谈 replay。</p>
        </div>
        <div class="summary-box">
          <h3>对 operator 的意义</h3>
          <p class="muted">它把“这张 replay bundle 还能不能信”压成显式 guard；operator 不用自己比对多个 CSV 的时间戳。</p>
        </div>
        <div class="summary-box">
          <h3>默认动作</h3>
          <p class="muted">如果这里全是 <code>synced</code>，就继续相信下面那张 <code>next replay bundle</code>；若不是，就先重建 <code>alpha_closure_board</code>。</p>
        </div>
      </div>
      <p class="muted" style="margin-top:12px;">artifact：<code>reports/artifacts/alpha_closure_board/small_live_rank2_execution_sync_guard_v1.csv</code></p>
    </div>

    <div class="card" style="padding:18px 20px; margin-top:18px;">
      <h2 style="margin:0 0 8px;">Rank 2 replay ready gate（v1）</h2>
      <p class="muted">这张表不再把 Run 3 的信息拆在 queue、bundle、sync guard 三处看，而是把 <b>Rank 2 当前到底能不能进入那 1 次 whitelist-bound <code>test/no-fill</code> replay、如果不能先该修哪层同步、如果能做也只允许推进到哪一步</b> 压成单行 gate。它解决的是当前 operator 最容易犯的错：拿着已经不再同步的 replay bundle，或者在 tiny-live state 已落后时，继续按旧读法执行。</p>
      <table>
        <thead>
          <tr>
            <th>candidate</th>
            <th>当前 ready state</th>
            <th>当前 bundle leg</th>
            <th>当前 owner</th>
            <th>execution sync</th>
            <th>tiny-live state sync</th>
            <th>现在唯一允许动作</th>
            <th>还在等什么</th>
            <th>硬阻断</th>
            <th>hard read</th>
            <th>observed at</th>
          </tr>
        </thead>
        <tbody>{rank2_replay_ready_gate_rows_html}</tbody>
      </table>
      <div class="summary-grid" style="margin-top:14px;">
        <div class="summary-box">
          <h3>为什么这张 gate 有用</h3>
          <p class="muted">它把 <code>queue + bundle + guards</code> 合成一条 operator-ready 判断：当前若两层 guard 都同步，才允许继续把下一步读成 1 次 SOL 优先的 test/no-fill replay；任何一层不同步，都先回到 resync。</p>
        </div>
        <div class="summary-box">
          <h3>当前 hard verdict</h3>
          <p class="muted">只要这里还是 <code>ready_for_one_test_no_fill_replay</code>，成功也最多推进到 <code>eligible_for_shadow_parity_review</code>；它不是 tiny-live 放行卡。</p>
        </div>
        <div class="summary-box">
          <h3>默认动作</h3>
          <p class="muted">先看这张单行 gate：若任一 sync 不是 <code>synced</code>，先做 resync；只有双 sync 都绿时，才继续按下面的 replay bundle 读 operator next step。</p>
        </div>
      </div>
      <p class="muted" style="margin-top:12px;">artifact：<code>reports/artifacts/alpha_closure_board/small_live_rank2_replay_ready_gate_v1.csv</code></p>
    </div>

    <div class="card" style="padding:18px 20px; margin-top:18px;">
      <h2 style="margin:0 0 8px;">Tiny-live now-action queue（v1）</h2>
      <p class="muted">watchboard 解决“去哪里看”，snapshot 解决“刚才有没有新事件”；这张队列再往前压一步，直接回答 <b>现在谁该等、谁该由谁接、下一步唯一允许动作是什么</b>。它刻意不发明新的流程，只把当前已落地的硬边界压成 operator / bot2 / manual runner 都能立刻执行的 `now-action` 队列，避免后续轮次继续围着 tiny-live 文档链猜“那现在到底该做什么”。</p>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>seat / candidate</th>
            <th>当前触发状态</th>
            <th>当前 owner</th>
            <th>现在唯一允许动作</th>
            <th>还在等什么</th>
            <th>硬阻断</th>
            <th>为什么这是最诚实下一步</th>
            <th>观察时间</th>
          </tr>
        </thead>
        <tbody>{small_live_now_action_queue_rows_html}</tbody>
      </table>
      <div class="summary-grid" style="margin-top:14px;">
        <div class="summary-box">
          <h3>当前 hard verdict</h3>
          <p class="muted"><b>当前 tiny-live 侧最多只配做三类动作：</b>保持 Live Seat 空席、催成 Rank 2 的唯一一次真实 receipt-chain replay、以及把 Rank 17 / 29 的新事件如实限制在 `P3 review / continuity`。除此之外的近义 tiny-live 文档扩写，当前都不算真实进展。</p>
        </div>
        <div class="summary-box">
          <h3>为什么这张表比再补一张 snapshot 更值钱</h3>
          <p class="muted">因为它不再只回答“有没有变化”，而是把 <b>owner + next allowed action now + 仍缺的证据 + 硬阻断</b> 放在一张表里。后续轮次可以直接拿它当操作队列，而不是先读三四张表再自己拼结论。</p>
        </div>
        <div class="summary-box">
          <h3>对 desk 排班的含义</h3>
          <p class="muted">只要这张队列没有出现新的 `next allowed action now` 级别变化，Run 3 就不该继续围绕 tiny-live 做同义补文档；更应该等待真实事件，或在允许时切回 Scout / Paper 主线。</p>
        </div>
      </div>
      <p class="muted" style="margin-top:12px;">artifact：<code>reports/artifacts/alpha_closure_board/small_live_now_action_queue_v1.csv</code></p>
    </div>

    <div class="card" style="padding:18px 20px; margin-top:18px;">
      <h2 style="margin:0 0 8px;">Tiny-live plumbing board（v1）</h2>
      <p class=\"muted\">这张表不回答“该不该上 live”，而是回答：<b>一旦 promotion gate 放行，真正执行前要先怎么做 routing dry-run、live ledger、mismatch guard 与 kill switch</b>。它的作用是把 Step 5 从一句抽象 policy 再压成 operator 可执行的检查栏位，避免 future run 临时拼接。</p>
      <table>
        <thead>
          <tr>
            <th>阶段</th>
            <th>账户 / venue 模式</th>
            <th>资金规则</th>
            <th>routing 规则</th>
            <th>ledger 必记字段</th>
            <th>mismatch guard</th>
            <th>kill switch</th>
          </tr>
        </thead>
        <tbody>{small_live_plumbing_rows_html}</tbody>
      </table>
      <p class=\"muted\" style=\"margin-top:12px;\">当前读法：<b>EMA</b> 还要先把同一张 paper ledger 连续跑起来；<b>breakout</b> 已退回 `bench`，所以这张表现在主要是在给 future challenger 与 tiny-live operator 流程预铺执行栏位，而不是继续默认替 breakout 预留升级通道。</p>
      <p class=\"muted\" style=\"margin-top:12px;\">artifact：<code>reports/artifacts/alpha_closure_board/small_live_plumbing_v1.csv</code></p>
    </div>

    <div class=\"card\" style=\"padding:18px 20px; margin-top:18px;\">
      <h2 style=\"margin:0 0 8px;\">Rank 2 paper-candidate closeout snapshot（v1）</h2>
      <p class=\"muted\">这张快照不回答“Rank 2 能不能直接上 tiny-live”，而是把当前最关键的一句实话挂到 alpha closure board：<b>它已经是窄范围 paper candidate，但 closeout 仍卡在 `paper_candidate_only / blocked`，唯一允许动作仍是一次 whitelist-bound `test/no-fill` receipt-chain replay</b>。换句话说，这张表是把最近几轮散落在 scout 页面里的 closeout 规则，压回当前更核心的部署读板。</p>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>研究口径</th>
            <th>venue symbol</th>
            <th>当前 scope</th>
            <th>当前唯一允许动作</th>
            <th>operator 限定</th>
            <th>什么时候才算 closeout 通过</th>
            <th>硬阻断</th>
            <th>当前 blocker</th>
          </tr>
        </thead>
        <tbody>{rank2_closeout_snapshot_rows_html}</tbody>
      </table>
      <div class=\"summary-grid\" style=\"margin-top:14px;\">
        <div class=\"summary-box\">
          <h3>当前状态</h3>
          <p class=\"muted\"><b>Rank 2 = narrow paper candidate</b>，但当前 closeout_state 仍是 <code>dry_run_only</code>，并且 hard verdict 仍是：没有真实 receipt chain 之前，只能继续 <code>paper_candidate_only / blocked</code>。</p>
        </div>
        <div class=\"summary-box\">
          <h3>什么才算通过</h3>
          <p class=\"muted\">不是模板、不是单段 ack，也不是换 scope 后的“差不多同一条 replay”。只有同一条 whitelist-bound replay 上同时拿到真实 <code>intent_ref + ack_ref + cancel_or_close_ref</code>，且 <code>scope</code> 不漂移、<code>capital=0</code>，才允许收口到 <code>eligible_for_shadow_parity_review</code>。</p>
        </div>
        <div class=\"summary-box\">
          <h3>这张表的作用</h3>
          <p class=\"muted\">把当前 desk 最容易被误读的一点钉死：<b>Rank 2 已经不该继续扩 scout 研究，但也绝对还没到 tiny-live ready</b>。现在缺的不是更多漂亮解释，而是一条真实 dry-run receipt chain。</p>
        </div>
      </div>
      <p class=\"muted\" style=\"margin-top:12px;\">artifact：<code>reports/artifacts/alpha_closure_board/small_live_rank2_closeout_snapshot_v1.csv</code></p>
    </div>

    <div class="card" style="padding:18px 20px; margin-top:18px;">
      <h2 style="margin:0 0 8px;">Rank 2 receipt-chain audit snapshot（v1）</h2>
      <p class="muted">这张表是对 <code>small_live_rank2_receipt_chain_log_template_v1.csv</code> 的诚实审计，不再只说“需要三段 refs”，而是逐个白名单符号直接回答：<b>现在到底落了几段真实 refs、还缺哪几段、因此下一步只能排到哪个队列</b>。当前模板里 3 个 leg 都还是占位 refs，所以这张 audit 的价值是把“blocked”从一句原则话压成逐行可复核的 operator 证据。</p>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>研究口径</th>
            <th>venue symbol</th>
            <th>当前链路状态</th>
            <th>真实 refs 已落地</th>
            <th>还缺哪些真实 refs</th>
            <th>scope guard</th>
            <th>capital guard</th>
            <th>当前 verdict</th>
            <th>当前 next queue</th>
          </tr>
        </thead>
        <tbody>{rank2_receipt_audit_rows_html}</tbody>
      </table>
      <div class="summary-grid" style="margin-top:14px;">
        <div class="summary-box">
          <h3>现在的硬结论</h3>
          <p class="muted">当前 3 条 whitelist leg 都还是 <code>0/3</code> 真实 refs 落地，因此 next queue 只能继续是 <code>routing_dry_run_replay</code>，不能偷切到 <code>shadow_parity</code>。</p>
        </div>
        <div class="summary-box">
          <h3>为什么这比近义说明页更有用</h3>
          <p class="muted">因为以后只要 operator 把真实 <code>intent_ref / ack_ref / cancel_or_close_ref</code> 回填进同一张 log template，再重建一次，这张 audit 就会自动显示到底是继续 blocked，还是终于够资格进入 <code>eligible_for_shadow_parity_review</code>。</p>
        </div>
        <div class="summary-box">
          <h3>边界</h3>
          <p class="muted">这依然不是 tiny-live pass，更不是 venue execution 本身；它只是把 Rank 2 receipt-chain blocker 变成一张能跟着真实 refs 自动收口的审计表。</p>
        </div>
      </div>
      <p class="muted" style="margin-top:12px;">artifact：<code>reports/artifacts/alpha_closure_board/small_live_rank2_receipt_chain_audit_v1.csv</code></p>
    </div>

    <div class="card" style="padding:18px 20px; margin-top:18px;">
      <h2 style="margin:0 0 8px;">Rank 2 single-replay runsheet（v1）</h2>
      <p class="muted">这张表不再继续解释为什么 blocked，而是直接回答 operator 下一步该怎么排：<b>如果现在只允许做一次真实 whitelist-bound <code>test/no-fill</code> replay，优先顺序应该怎么走、每个 leg 要抓哪三段 refs、过了以后才允许进入什么 gate</b>。它把前几轮已经散落的 ticket / packet / log template / completion gate 压成一张更接近开工包的读板。</p>
      <table>
        <thead>
          <tr>
            <th>优先级</th>
            <th>研究口径</th>
            <th>venue symbol</th>
            <th>venue mode</th>
            <th>为什么排这个顺序</th>
            <th>允许动作</th>
            <th>必须抓到的 refs</th>
            <th>当前 log stub</th>
            <th>通过后才允许进入的 gate</th>
            <th>硬阻断</th>
          </tr>
        </thead>
        <tbody>{rank2_replay_runsheet_rows_html}</tbody>
      </table>
      <div class="summary-grid" style="margin-top:14px;">
        <div class="summary-box">
          <h3>当前推荐顺序</h3>
          <p class="muted"><b>{rank2_replay_order_text}</b>。{rank2_replay_policy_blurb}</p>
        </div>
        <div class="summary-box">
          <h3>这张表解决什么问题</h3>
          <p class="muted">把“下一步只能做一次真实 replay”再往前压半步：不是继续补近义说明，而是把 operator 真正开工时的腿顺序、log stub 与 pass gate 放到同一张表里，减少 future run 临时拼接。</p>
        </div>
        <div class="summary-box">
          <h3>仍然没变的边界</h3>
          <p class="muted">这依然不是 tiny-live 放行。即使首腿 replay 成功，也只是第一次拿到 <code>eligible_for_shadow_parity_review</code>，仍不是 live ready。</p>
        </div>
      </div>
      <p class="muted" style="margin-top:12px;">artifact：<code>reports/artifacts/alpha_closure_board/small_live_rank2_replay_runsheet_v1.csv</code></p>
    </div>

    <div class="card" style="padding:18px 20px; margin-top:18px;">
      <h2 style="margin:0 0 8px;">Rank 2 replay closeout matrix（v1）</h2>
      <p class="muted">这张表继续只做 runsheet 的紧邻下一步：<b>如果某一条 whitelist-bound replay 真的执行了，应该开什么 review ticket、成功时怎么关单、失败时又该如何写回同一条审计链</b>。它的价值不是新增一层规则，而是把 <code>一次真实 replay</code> 的 green / blocked 两种收口写成 operator 能直接照抄的 closeout matrix。</p>
      <table>
        <thead>
          <tr>
            <th>优先级</th>
            <th>研究口径</th>
            <th>venue symbol</th>
            <th>当前 log stub</th>
            <th>建议打开的 review ticket</th>
            <th>若 replay 成功</th>
            <th>成功时 writeback</th>
            <th>若 replay 失败</th>
            <th>失败时 writeback</th>
            <th>成功后 next queue</th>
            <th>失败后 next queue</th>
          </tr>
        </thead>
        <tbody>{rank2_replay_closeout_matrix_rows_html}</tbody>
      </table>
      <div class="summary-grid" style="margin-top:14px;">
        <div class="summary-box">
          <h3>它补的是哪一格</h3>
          <p class="muted">runsheet 解决的是先做哪条腿；这张 matrix 解决的是：<b>腿真的跑完之后，operator 该把它关成什么状态</b>。这样 future run 不会只知道要抓 receipt refs，却不知道通过/失败后该怎样落 review registry。</p>
        </div>
        <div class="summary-box">
          <h3>当前硬结论</h3>
          <p class="muted">即使 replay 成功，green closeout 也只能收口到 <code>eligible_for_shadow_parity_review</code>，默认 next queue 只是 <code>shadow_parity</code>；它依然不是 tiny-live 放行。</p>
        </div>
        <div class="summary-box">
          <h3>为什么这是 deployable artifact</h3>
          <p class="muted">因为它把真实 operator replay 后的 closeout / writeback 路径直接写成表格，减少后续轮次在 ticket、registry、next queue 之间临时拼接。</p>
        </div>
      </div>
      <p class="muted" style="margin-top:12px;">artifact：<code>reports/artifacts/alpha_closure_board/small_live_rank2_replay_closeout_matrix_v1.csv</code></p>
    </div>

    <div class="card" style="padding:18px 20px; margin-top:18px;">
      <h2 style="margin:0 0 8px;">Rank 2 shadow-parity launch packet（v1）</h2>
      <p class="muted">这张表只补 <b>replay 成功后的下一步</b>：不是再解释为什么 blocked，也不是偷写成 tiny-live ready，而是把 <b>一次 whitelist-bound replay 真通过后，operator 应该如何打开第一张 shadow parity review ticket、绑定哪条 paper_ref / live_shadow_ref、以及第一条 green row 至少要写回哪些字段</b> 压成可直接照抄的启动包。</p>
      <table>
        <thead>
          <tr>
            <th>优先级</th>
            <th>研究口径</th>
            <th>venue symbol</th>
            <th>触发条件</th>
            <th>建议打开的 parity ticket</th>
            <th>paper_ref stub</th>
            <th>live_shadow_ref stub</th>
            <th>第一条 shadow row 必须写回</th>
            <th>硬边界</th>
          </tr>
        </thead>
        <tbody>{rank2_shadow_parity_launch_packet_rows_html}</tbody>
      </table>
      <div class="summary-grid" style="margin-top:14px;">
        <div class="summary-box">
          <h3>它补的是哪一格</h3>
          <p class="muted">前一张 closeout matrix 解决的是 dry-run replay 如何关单；这张 launch packet 解决的是：<b>dry-run 真关成 green 以后，第一张 shadow parity ticket 应该怎么开</b>。这样 future run 不会从 <code>eligible_for_shadow_parity_review</code> 直接跳成口头‘可以继续’。</p>
        </div>
        <div class="summary-box">
          <h3>当前推荐顺序</h3>
          <p class="muted"><b>{rank2_replay_order_text}</b> 是当前更诚实的 launch 顺序；{rank2_replay_policy_blurb} 这次只是把这三个腿各自的 <code>SL-PARITY-*</code>、<code>paper_ref</code> 与 <code>live_shadow_ref</code> 启动 stub 一次写清，减少 future run 临时命名漂移。</p>
        </div>
        <div class="summary-box">
          <h3>硬结论</h3>
          <p class="muted">即使 dry-run replay 成功，下一步也仍然只是 <code>shadow_parity</code>；只要缺 paper_ref、qty rounding / cost snapshot、白名单或时钟对齐，仍继续 blocked，<b>绝不</b>允许偷写成 tiny-live ready。</p>
        </div>
      </div>
      <p class="muted" style="margin-top:12px;">artifact：<code>reports/artifacts/alpha_closure_board/small_live_rank2_shadow_parity_launch_packet_v1.csv</code></p>
    </div>

    <div class="card" style="padding:18px 20px; margin-top:18px;">
      <h2 style="margin:0 0 8px;">Rank 2 shadow-parity starter rows（v1）</h2>
      <p class="muted">这张表只补 launch packet 的紧邻下一格：<b>一旦 Rank 2 的那条 whitelist-bound replay 真关成 green，第一条 shadow-parity 绿行应该怎么落</b>。它不是新规则，而是把 <b>ticket stub / paper_ref / live_shadow_ref / stage_status / operator_action / 最低 writeback</b> 预先压成 starter rows，避免 future run 到了真要写第一条 green row 时再临时拼字段。</p>
      <table>
        <thead>
          <tr>
            <th>优先级</th>
            <th>研究口径</th>
            <th>venue symbol</th>
            <th>parity ticket stub</th>
            <th>paper_ref stub</th>
            <th>live_shadow_ref stub</th>
            <th>stage</th>
            <th>mismatch_status</th>
            <th>operator_action</th>
            <th>最小 writeback</th>
            <th>closeout 前仍待补字段</th>
            <th>硬边界</th>
          </tr>
        </thead>
        <tbody>{rank2_shadow_parity_starter_rows_html}</tbody>
      </table>
      <div class="summary-grid" style="margin-top:14px;">
        <div class="summary-box">
          <h3>它补的是哪一格</h3>
          <p class="muted">launch packet 解决的是第一张 parity ticket 怎么开；这张 starter rows 解决的是：<b>开完以后，第一条 green parity row 至少该长什么样</b>。这样 future run 不会只知道 stub 名称，却还得现场临时拼 row 字段。</p>
        </div>
        <div class="summary-box">
          <h3>为什么它算 deployable artifact</h3>
          <p class="muted">因为它已经把 <b>{rank2_replay_order_text}</b> 三条腿的 `ticket / paper_ref / live_shadow_ref / operator_action / minimum_writeback` 固定成可直接照抄的 starter rows；当前排序口径同样遵循：{rank2_replay_policy_blurb} 后面真的拿到 replay green closeout 时，只需要把 `rounded_qty` 与 `cost_estimate_bps` 这些真实字段补进去。</p>
        </div>
        <div class="summary-box">
          <h3>仍然没变的硬结论</h3>
          <p class="muted">这仍然不是 tiny-live 放行。只要 `rounded_qty / cost / whitelist / clock` 任一没过，就不能用 starter row 冒充 green parity closeout；默认必须回到 <code>parity_red / freeze_review</code>。</p>
        </div>
      </div>
      <p class="muted" style="margin-top:12px;">artifact：<code>reports/artifacts/alpha_closure_board/small_live_rank2_shadow_parity_starter_rows_v1.csv</code></p>
    </div>

    <div class="card" style="padding:18px 20px; margin-top:18px;">
      <h2 style="margin:0 0 8px;">Rank 2 next status-changing gate（v1）</h2>
      <p class="muted">这张表专门给最近几轮的 Rank 2 doc-chain 设一个止损闸门：<b>现在到底什么动作还会真的改变状态，什么动作已经不该再默认算进展</b>。它不是再发明新流程，而是把当前 desk 最需要钉死的一句实话 reader-facing 化：<b>launch packet 与 starter row 已经够了；接下来若没有真实 whitelist-bound replay 的 receipt refs，状态就不会动。</b></p>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>gate</th>
            <th>当前状态</th>
            <th>什么才算 status change</th>
            <th>什么不再算</th>
            <th>为什么</th>
            <th>今天已经就绪的证据</th>
            <th>一旦做完会进哪条队列</th>
          </tr>
        </thead>
        <tbody>{rank2_next_status_change_gate_rows_html}</tbody>
      </table>
      <div class="summary-grid" style="margin-top:14px;">
        <div class="summary-box">
          <h3>当前 hard verdict</h3>
          <p class="muted"><b>继续补 Rank 2 近义 packet / starter / wording，默认已不再减少 blocker。</b> 真正会改状态的只剩一次真实 whitelist-bound <code>test/no-fill</code> replay。</p>
        </div>
        <div class="summary-box">
          <h3>为什么这轮要加这张表</h3>
          <p class="muted">因为 Rank 2 这条线已经连续几轮主要新增 launch packet / starter row / closeout copy。与其继续磨同类 artifact，不如把“文档链到此为止”的闸门写清楚，逼后续只在真实 replay 或新 intake 之间做选择。</p>
        </div>
        <div class="summary-box">
          <h3>对默认排班的影响</h3>
          <p class="muted">除非 operator 真回填 receipt refs，否则 bot3 默认不该再把 Run 3 主资源继续花在 Rank 2 相邻文档；更诚实的下一步要么是真 replay，要么切回新的 paper / repo Scout intake。</p>
        </div>
      </div>
      <p class="muted" style="margin-top:12px;">artifact：<code>reports/artifacts/alpha_closure_board/small_live_rank2_next_status_change_gate_v1.csv</code></p>
    </div>

    <div class="card" style="padding:18px 20px; margin-top:18px;">
      <h2 style="margin:0 0 8px;">Rank 2 next replay bundle（v1）</h2>
      <p class="muted">这张表把当前 <code>Run 3</code> 真正唯一允许的一腿压成单行执行包：<b>如果现在只做 1 次不会动用真钱的 whitelist-bound <code>test/no-fill</code> replay，到底先做哪条腿、样例金额怎么读、必须抓哪三段 refs、成功后又只允许推进到哪一步</b>。它不再要求 operator 自己在 runsheet、closeout matrix、shadow parity packet 之间来回拼接。</p>
      <table>
        <thead>
          <tr>
            <th>优先级</th>
            <th>研究口径</th>
            <th>venue symbol</th>
            <th>为什么先做这条腿</th>
            <th>样例名义金额（USDT）</th>
            <th>当前预算读法</th>
            <th>唯一允许动作</th>
            <th>必须抓到的 refs</th>
            <th>当前 log stub</th>
            <th>若通过</th>
            <th>若通过后建议开的 parity ticket</th>
            <th>硬阻断</th>
          </tr>
        </thead>
        <tbody>{rank2_next_replay_bundle_rows_html}</tbody>
      </table>
      <div class="summary-grid" style="margin-top:14px;">
        <div class="summary-box">
          <h3>当前 hard verdict</h3>
          <p class="muted"><b>当前最诚实的第一腿是 SOL-USD / SOLUSDT。</b> 通过也只意味着 <code>eligible_for_shadow_parity_review</code>；仍不是 tiny-live 放行。</p>
        </div>
        <div class="summary-box">
          <h3>它补的是哪一格</h3>
          <p class="muted"><code>next status-changing gate</code> 已经把“只有真实 replay 才会改状态”写死；这张 bundle 再往前半步，把 <b>那次 replay 该怎样开工</b> 压成一行 deployable artifact。</p>
        </div>
        <div class="summary-box">
          <h3>为什么它比继续磨说明页更值钱</h3>
          <p class="muted">因为它直接回答现在只许做什么、不许做什么，并把 <code>log stub / refs / parity ticket stub</code> 放进同一行，减少 future run 继续长文档链却不减 blocker。</p>
        </div>
      </div>
      <p class="muted" style="margin-top:12px;">artifact：<code>reports/artifacts/alpha_closure_board/small_live_rank2_next_replay_bundle_v1.csv</code></p>
    </div>

    <div class="card" style="padding:18px 20px; margin-top:18px;">
      <h2 style="margin:0 0 8px;">Rank 2 replay preflight snapshot（v1）</h2>
      <p class="muted">这张表只给上面的 replay bundle 做一个最小 numeric sanity check：<b>同样按当前 venue precision / step-size 读，白名单三条腿在样例金额下各自会损失多少 rounding bps、因此当前更该先碰哪条腿</b>。它不是新的 admission gate，只是把“为什么是这条腿先上”从口头判断压成可复核快照。</p>
      <table>
        <thead>
          <tr>
            <th>优先级</th>
            <th>研究口径</th>
            <th>venue symbol</th>
            <th>样例名义金额（USDT）</th>
            <th>rounded notional（USDT）</th>
            <th>rounding loss（bps）</th>
            <th>当前优先级 verdict</th>
            <th>最小名义金额检查</th>
            <th>一句话硬读法</th>
          </tr>
        </thead>
        <tbody>{rank2_replay_preflight_snapshot_rows_html}</tbody>
      </table>
      <div class="summary-grid" style="margin-top:14px;">
        <div class="summary-box">
          <h3>当前数字读法</h3>
          <p class="muted">在当前 50U 示例下，<b>SOL</b> 的 rounding 损耗最干净；<b>ETH</b> 也可做，但若要更稳地压到同一档预算，名义金额抬高会更诚实；<b>BTC</b> 继续只保留最后备选。</p>
        </div>
        <div class="summary-box">
          <h3>它解决什么误读</h3>
          <p class="muted">避免 future run 只因为白名单顺序或主观偏好就先碰高 rounding-loss 的腿。当前选择顺序必须能被最小 precision / notional 快照解释，而不是只靠文字偏好。</p>
        </div>
        <div class="summary-box">
          <h3>边界</h3>
          <p class="muted">这依然不是 venue replay 本身；就算 preflight 最优，也必须等真实 <code>intent -> ack -> cancel/close</code> 三段 refs 落地后才会改状态。</p>
        </div>
      </div>
      <p class="muted" style="margin-top:12px;">artifact：<code>reports/artifacts/alpha_closure_board/small_live_rank2_replay_preflight_snapshot_v1.csv</code></p>
    </div>

    <div class=\"card\" style=\"padding:18px 20px; margin-top:18px;\">
      <h2 style=\"margin:0 0 8px;\">Tiny-live live-ledger template（v1）</h2>
      <p class=\"muted\">这张表继续只做 Run 3 的一个紧邻子点：把 <b>live ledger</b> 从“要记哪些字段”的口头提醒，压成 future dry-run / shadow / tiny-live / rollback 都能复用的最小 schema。它不替代交易逻辑，只负责把 <b>paper_ref、route_ack、数量精度、滑点、mismatch、rollback</b> 这些 execution 字段锁进同一张账本。</p>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>字段</th>
            <th>必须出现在哪些阶段</th>
            <th>填写规则</th>
            <th>缺失时的红旗</th>
            <th>为什么重要</th>
          </tr>
        </thead>
        <tbody>{small_live_ledger_rows_html}</tbody>
      </table>
      <p class=\"muted\" style=\"margin-top:12px;\">当前作用不是“准备立刻上 live”，而是把 `crypto live mismatch` 继续往前压成可审计 ledger schema。未来若先跑 `routing dry-run` 或 `paper-live shadow parity`，默认也应该沿这张模板落行，而不是临时想起再补字段。</p>
      <p class=\"muted\" style=\"margin-top:12px;\">artifact：<code>reports/artifacts/alpha_closure_board/small_live_ledger_template_v1.csv</code></p>
    </div>

    <div class=\"card\" style=\"padding:18px 20px; margin-top:18px;\">
      <h2 style=\"margin:0 0 8px;\">Routing dry-run checklist（v1）</h2>
      <p class=\"muted\">这张表继续沿同一个 Run 3 主线，只做 <b>routing dry-run</b> 这一刀：把“先做一次 dry-run 再说”压成 operator 真能逐项勾的 checklist。它不假装已经接通交易所，只负责把 <b>候选白名单、symbol/precision 映射、intent→ack→cancel 回执链、时钟对齐、数量舍入与资金上限</b> 这些最容易 silently 出错的步骤先锁死。</p>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>步骤</th>
            <th>必须先拿到什么</th>
            <th>什么才算通过</th>
            <th>失败时为什么直接阻断</th>
            <th>必须落到哪些 ledger 字段</th>
          </tr>
        </thead>
        <tbody>{small_live_routing_dry_run_rows_html}</tbody>
      </table>
      <p class=\"muted\" style=\"margin-top:12px;\">当前读法：这还不是 `paper-live shadow parity`，更不是 tiny-live 放行；它只是把 Step 5 最前面的 `routing dry-run` 从一句抽象提醒压成可审计清单，避免 future run 一上 venue 就先踩 symbol mapping / precision / receipt chain 这些基础坑。</p>
      <p class=\"muted\" style=\"margin-top:12px;\">artifact：<code>reports/artifacts/alpha_closure_board/small_live_routing_dry_run_checklist_v1.csv</code></p>
    </div>

    <div class=\"card\" style=\"padding:18px 20px; margin-top:18px;\">
      <h2 style=\"margin:0 0 8px;\">Routing dry-run sample row（v1）</h2>
      <p class=\"muted\">这张表不是再写一份 checklist，而是把 <b>一条合格的 dry-run 回执到底该怎么落到账本</b> 固定成样例。它回答的不是“能不能 tiny-live”，而是：<b>当 routing dry-run 通过 symbol/precision/cap 检查，且完整留下 `intent -> ack -> cancel` 三段回执后，第一条 green dry-run row 应该长什么样</b>。</p>
      <table>
        <thead>
          <tr>
            <th>row_kind</th>
            <th>candidate</th>
            <th>stage</th>
            <th>signal_bar_utc</th>
            <th>research_symbol</th>
            <th>venue_symbol</th>
            <th>side</th>
            <th>venue_mode</th>
            <th>route_intent_ts</th>
            <th>route_ack_ts</th>
            <th>cancel_ts</th>
            <th>ack_latency_ms</th>
            <th>notional_usd</th>
            <th>intended_qty</th>
            <th>rounded_qty</th>
            <th>mismatch_status</th>
            <th>operator_action</th>
            <th>operator_note</th>
          </tr>
        </thead>
        <tbody>{small_live_routing_dry_run_sample_rows_html}</tbody>
      </table>
      <p class=\"muted\" style=\"margin-top:12px;\">当前读法：这张 sample row 仍然只停在 `test/no-fill`，不是 tiny-live 放行，也不是任何真实成交。它的价值是把最前面的 dry-run 留痕方式固定下来，避免 future run 只在日志里说“回执链没问题”，却没有同账本样例。</p>
      <p class=\"muted\" style=\"margin-top:12px;\">artifact：<code>reports/artifacts/alpha_closure_board/small_live_routing_dry_run_sample_row_v1.csv</code></p>
    </div>

    <div class=\"card\" style=\"padding:18px 20px; margin-top:18px;\">
      <h2 style=\"margin:0 0 8px;\">Small-live operator reconciliation sequence（v1）</h2>
      <p class=\"muted\">这张表不是新增一套 live 规则，而是把 <b>dry-run green row → shadow parity checklist → parity_red 分支 → reopen gate → green resume row</b> 串成一条 operator 真能顺着走的对账顺序。它回答的是：<b>future run 真开始对账时，先看哪张 artifact、通过后产出什么、失败后又该停在哪</b>。</p>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>operator 阶段</th>
            <th>复用哪张 artifact</th>
            <th>这一步到底核对什么</th>
            <th>通过后应产出什么</th>
            <th>失败后必须停在哪</th>
            <th>同账本锚点</th>
          </tr>
        </thead>
        <tbody>{small_live_operator_reconciliation_rows_html}</tbody>
      </table>
      <p class=\"muted\" style=\"margin-top:12px;\">当前读法：它依然不是 tiny-live 放行卡；价值在于把已有的多个 v1 artifact 压成同一条执行顺序，避免 future run 明明已经有 checklist 和 sample row，却不知道先看哪张、失败后该回退到哪一步。</p>
      <p class=\"muted\" style=\"margin-top:12px;\">artifact：<code>reports/artifacts/alpha_closure_board/small_live_operator_reconciliation_sequence_v1.csv</code></p>
    </div>

    <div class=\"card\" style=\"padding:18px 20px; margin-top:18px;\">
      <h2 style=\"margin:0 0 8px;\">Small-live operator handoff packet（v1）</h2>
      <p class=\"muted\">这张表继续沿同一条 Run 3 执行链，只补一个更贴近开工的切面：<b>当 future run 真要开始一次 venue / shadow review 时，operator 该一口气打开哪几张 artifact、目标写回哪条 row、什么情况下必须立刻停手</b>。它不是替代 sequence，而是把 sequence 压成更像“启动包”的场景化 bundle。</p>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>当前 review 场景</th>
            <th>先打开哪几张 artifact</th>
            <th>这次 handoff 的目标</th>
            <th>预期写回</th>
            <th>什么时候必须停</th>
          </tr>
        </thead>
        <tbody>{small_live_operator_handoff_rows_html}</tbody>
      </table>
      <p class=\"muted\" style=\"margin-top:12px;\">当前读法：它依旧不是 tiny-live 放行；价值在于把多张已存在的 v1 卡片压成 4 个最常见 review 场景的开工包，减少 future operator 在多张 CSV / 页面之间来回找，结果却没写出同账本 row 的摩擦。</p>
      <p class=\"muted\" style=\"margin-top:12px;\">artifact：<code>reports/artifacts/alpha_closure_board/small_live_operator_handoff_packet_v1.csv</code></p>
    </div>

    <div class=\"card\" style=\"padding:18px 20px; margin-top:18px;\">
      <h2 style=\"margin:0 0 8px;\">Small-live review ticket template（v1）</h2>
      <p class=\"muted\">这张表继续沿 handoff bundle 再往前补一格，但不重新发明规则：它只回答一个更贴近 future venue review 的问题——<b>当 operator 真要开一张 dry-run / parity / reopen 恢复 review 时，这张 ticket 至少要带哪些引用、成功时怎么关单、失败时必须怎么收口</b>。这样 future run 不会只在日志里说“这轮看了哪几张卡”，却没有一张可复用的 review ticket 模板把 artifact 与 writeback 锚在一起。</p>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>当前 review 场景</th>
            <th>ticket stub</th>
            <th>必须绑定的引用</th>
            <th>开工 bundle</th>
            <th>成功时怎么关单</th>
            <th>失败时怎么收口</th>
          </tr>
        </thead>
        <tbody>{small_live_review_ticket_template_rows_html}</tbody>
      </table>
      <p class=\"muted\" style=\"margin-top:12px;\">当前读法：它仍然不是 tiny-live 放行卡；价值在于把 handoff packet 从“知道先开哪几张 artifact”推进到“知道这次 review ticket 至少要绑哪些 ref、结束时必须留哪条 closeout”。</p>
      <p class=\"muted\" style=\"margin-top:12px;\">artifact：<code>reports/artifacts/alpha_closure_board/small_live_review_ticket_template_v1.csv</code></p>
    </div>

    <div class=\"card\" style=\"padding:18px 20px; margin-top:18px;\">
      <h2 style=\"margin:0 0 8px;\">Small-live review writeback matrix（v1）</h2>
      <p class=\"muted\">这张表是 review ticket template 的紧邻下一格：它不再回答“ticket 该带什么”，而是把<b>每种 closeout 结果至少要写回哪些字段、必须留在同一条 review registry / ledger 上的状态、以及下一步该进哪条队列</b>压成固定矩阵。这样 future operator 关单时不只是写一句“绿了/红了”，而是能把 `ticket -> row ref -> next queue` 这条链闭合。</p>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>closeout 场景</th>
            <th>ticket 状态</th>
            <th>最少要写回什么</th>
            <th>必须留在同账本/同 registry 的状态</th>
            <th>下一步进入哪条队列</th>
            <th>什么时候不能口头过关</th>
          </tr>
        </thead>
        <tbody>{small_live_review_writeback_matrix_rows_html}</tbody>
      </table>
      <p class=\"muted\" style=\"margin-top:12px;\">当前读法：它依旧不是 tiny-live 放行卡；价值在于把 `review ticket -> closeout -> writeback -> next queue` 固定成同一条可审计链，减少 future venue/shadow review 只留下日志、不留下 registry / ledger 状态切换的摩擦。</p>
      <p class=\"muted\" style=\"margin-top:12px;\">artifact：<code>reports/artifacts/alpha_closure_board/small_live_review_writeback_matrix_v1.csv</code></p>
    </div>

    <div class=\"card\" style=\"padding:18px 20px; margin-top:18px;\">
      <h2 style=\"margin:0 0 8px;\">Small-live review registry template（v1）</h2>
      <p class=\"muted\">这张表继续沿 `closeout / registry / writeback` 这条 Run 3 fallback 执行链，只补一格最贴近 future venue review 落表的模板：<b>一张 review ticket 真关掉以后，同一条 registry row 至少该长什么样、哪些状态字段必须一起落、历史 red/ref continuity 要怎样接回去</b>。它不是新规则，而是把 writeback matrix 里提到的“同一条 registry / ledger 状态切换”具体压成可复用的 row schema。</p>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>registry 行类型</th>
            <th>最小主键 / 引用</th>
            <th>必须同时落下的状态字段</th>
            <th>证据 / 附件引用</th>
            <th>什么情况下才配进下一队列</th>
            <th>什么时候必须继续阻断</th>
          </tr>
        </thead>
        <tbody>{small_live_review_registry_template_rows_html}</tbody>
      </table>
      <p class=\"muted\" style=\"margin-top:12px;\">当前读法：它仍然不是 tiny-live 放行卡；价值在于把 `ticket -> registry row -> next queue` 固定成可以直接复用的记录模板，避免 future run 明明已经有 closeout 结论，却仍把状态切换散落在日志、邮件与多张 CSV 之间。</p>
      <p class=\"muted\" style=\"margin-top:12px;\">artifact：<code>reports/artifacts/alpha_closure_board/small_live_review_registry_template_v1.csv</code></p>
    </div>

    <div class=\"card\" style=\"padding:18px 20px; margin-top:18px;\">
      <h2 style=\"margin:0 0 8px;\">Paper-live shadow parity checklist（v1）</h2>
      <p class=\"muted\">这张表是 Run 3 当前最紧邻的下一刀：把 <b>paper vs live-shadow</b> 的同步审计，压成真正可复用的 checklist。它不回答“现在能不能上 tiny-live”，只回答：<b>当 paper 信号被映射成 live-shadow payload 时，哪些 symbol / qty / cost / clock / ledger 红旗必须先被锁死，否则一律停在 parity review</b>。</p>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>步骤</th>
            <th>必须先拿到什么</th>
            <th>什么才算通过</th>
            <th>失败时为什么直接阻断</th>
            <th>必须落到哪些 ledger 字段</th>
          </tr>
        </thead>
        <tbody>{small_live_shadow_parity_rows_html}</tbody>
      </table>
      <p class=\"muted\" style=\"margin-top:12px;\">当前读法：这仍然不是 tiny-live 放行卡，而是先把 `paper_ref -> live_shadow_ref` 这条同步审计链写死。只有 shadow parity 自己先可审计，后面才谈得上 live mismatch、kill switch 与 rollback 是否靠谱。</p>
      <p class=\"muted\" style=\"margin-top:12px;\">artifact：<code>reports/artifacts/alpha_closure_board/paper_live_shadow_parity_checklist_v1.csv</code></p>
    </div>

    <div class=\"card\" style=\"padding:18px 20px; margin-top:18px;\">
      <h2 style=\"margin:0 0 8px;\">Parity-red action ladder（v1）</h2>
      <p class=\"muted\">这张表继续沿同一个 Run 3 子链，只补一件事：<b>一旦 shadow parity 真出现 `parity_red`，operator 当场到底该怎么做</b>。目标不是写更多原则，而是把 `hold / cancel / escalate / freeze review` 的默认动作锁死，避免 future run 看到红旗后又靠临场解释把它淡化。</p>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>触发红旗</th>
            <th>默认 operator 动作</th>
            <th>route / shadow 如何处理</th>
            <th>必须怎么回写 ledger</th>
            <th>什么条件下才允许重试</th>
          </tr>
        </thead>
        <tbody>{small_live_parity_red_action_rows_html}</tbody>
      </table>
      <p class=\"muted\" style=\"margin-top:12px;\">当前读法：`parity_red` 不是一句状态标签，而是会直接改变 operator 动作顺序的硬分支。尤其连续两次 `parity_red` 时，默认动作应是冻结当前 candidate 的 small-live review，而不是靠更多重试稀释问题。</p>
      <p class=\"muted\" style=\"margin-top:12px;\">artifact：<code>reports/artifacts/alpha_closure_board/small_live_parity_red_action_ladder_v1.csv</code></p>
    </div>

    <div class=\"card\" style=\"padding:18px 20px; margin-top:18px;\">
      <h2 style=\"margin:0 0 8px;\">Shadow parity sample row（v1）</h2>
      <p class=\"muted\">这张表不是新规则，而是把前面的 checklist / action ladder 压成 <b>同一行 ledger 长什么样</b> 的最小示例。当前示例故意选 `parity_red` 场景：让 future run 不用再猜，看到成本偏差超阈值时，哪几个字段必须同时出现、这行应停在哪一步、最早何时才允许重开。</p>
      <table>
        <thead>
          <tr>
            <th>row_kind</th>
            <th>candidate</th>
            <th>stage</th>
            <th>paper_ref</th>
            <th>shadow_ref</th>
            <th>research_symbol</th>
            <th>venue_symbol</th>
            <th>side</th>
            <th>notional_usd</th>
            <th>intended_qty</th>
            <th>rounded_qty</th>
            <th>shadow_price</th>
            <th>cost_bps</th>
            <th>mismatch_status</th>
            <th>mismatch_reason</th>
            <th>operator_action</th>
            <th>trigger_reason</th>
            <th>reopen_earliest_ts</th>
            <th>operator_note</th>
          </tr>
        </thead>
        <tbody>{small_live_shadow_parity_sample_rows_html}</tbody>
      </table>
      <p class=\"muted\" style=\"margin-top:12px;\">当前读法：sample row 的作用不是假装已经有真实 live 订单，而是给 future `shadow_parity` 留一份“红旗发生时账本该怎么写”的模板，避免只在日志里说“这次先 hold”。</p>
      <p class=\"muted\" style=\"margin-top:12px;\">artifact：<code>reports/artifacts/alpha_closure_board/small_live_shadow_parity_sample_row_v1.csv</code></p>
    </div>

    <div class=\"card\" style=\"padding:18px 20px; margin-top:18px;\">
      <h2 style=\"margin:0 0 8px;\">Green shadow parity sample row（v1）</h2>
      <p class=\"muted\">这张表补的是另一半：<b>如果 shadow parity 本身通过了，第一条 green row 该怎么写</b>。它回答的是：在还没进入 tiny-live、只允许继续 `shadow review` 的情况下，哪些字段必须一次落齐，才能证明这轮不是“看起来没问题”，而是真的留下了可审计的 green parity 行。</p>
      <table>
        <thead>
          <tr>
            <th>row_kind</th>
            <th>candidate</th>
            <th>stage</th>
            <th>paper_ref</th>
            <th>shadow_ref</th>
            <th>research_symbol</th>
            <th>venue_symbol</th>
            <th>side</th>
            <th>notional_usd</th>
            <th>intended_qty</th>
            <th>rounded_qty</th>
            <th>shadow_price</th>
            <th>cost_bps</th>
            <th>mismatch_status</th>
            <th>mismatch_reason</th>
            <th>operator_action</th>
            <th>trigger_reason</th>
            <th>reopen_earliest_ts</th>
            <th>operator_note</th>
          </tr>
        </thead>
        <tbody>{small_live_green_shadow_parity_sample_rows_html}</tbody>
      </table>
      <p class=\"muted\" style=\"margin-top:12px;\">当前读法：这不是 tiny-live 放行，也不是说某条候选已经过审；它只是把 `paper_ref -> live_shadow_ref` 真过关时的 green ledger 模板写死，让 future run 知道什么时候只该继续 `shadow review`，而不该偷渡成真钱发送。</p>
      <p class=\"muted\" style=\"margin-top:12px;\">artifact：<code>reports/artifacts/alpha_closure_board/small_live_green_shadow_parity_sample_row_v1.csv</code></p>
    </div>

    <div class="card" style="padding:18px 20px; margin-top:18px;">
      <h2 style="margin:0 0 8px;">Parity-red reopen gate checklist（v1）</h2>
      <p class="muted">这张表是前一轮 `parity_red action ladder + sample row` 的紧邻续刀：不是再解释为什么会红，而是明确 <b>红旗之后，什么条件都补齐了，才配重新打开下一条 shadow parity row</b>。目标是防止 future run 把 `reopen_earliest_ts` 误读成“时间到了就能自动重试”。</p>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>重开前必须过的步骤</th>
            <th>什么才算真的满足</th>
            <th>如果没满足就该怎么做</th>
            <th>必须怎么回写 ledger</th>
          </tr>
        </thead>
        <tbody>{small_live_reopen_gate_rows_html}</tbody>
      </table>
      <p class="muted" style="margin-top:12px;">当前读法：`reopen_earliest_ts` 只是最早时点，不是自动赦免。真正的 reopen 必须先关掉上一条 red cause、重走最小 routing 回执，再拿到新的 green shadow parity row，才允许恢复 small-live review。</p>
      <p class="muted" style="margin-top:12px;">artifact：<code>reports/artifacts/alpha_closure_board/small_live_reopen_gate_checklist_v1.csv</code></p>
    </div>

    <div class="card" style="padding:18px 20px; margin-top:18px;">
      <h2 style="margin:0 0 8px;">Reopen resume sample row（v1）</h2>
      <p class="muted">这张表继续沿同一条 Run 3 子链往前走半步：不是再写一张新 checklist，而是把 <b>reopen gate 真的通过后，第一条 `green shadow parity row` 该长什么样</b> 固定成样例。这样 future run 不会只知道“可以恢复 review 了”，却不知道账上要怎样同时保留 `prior_red_ref_id`、新的 route 回执、以及恢复后的 `resume_shadow_review` 动作。</p>
      <table>
        <thead>
          <tr>
            <th>row_kind</th>
            <th>candidate</th>
            <th>prior_red_ref</th>
            <th>stage</th>
            <th>paper_ref</th>
            <th>shadow_ref</th>
            <th>research_symbol</th>
            <th>venue_symbol</th>
            <th>side</th>
            <th>notional_usd</th>
            <th>intended_qty</th>
            <th>rounded_qty</th>
            <th>shadow_price</th>
            <th>cost_bps</th>
            <th>mismatch_status</th>
            <th>mismatch_reason</th>
            <th>operator_action</th>
            <th>trigger_reason</th>
            <th>reopen_earliest_ts</th>
            <th>operator_note</th>
          </tr>
        </thead>
        <tbody>{small_live_reopen_resume_sample_rows_html}</tbody>
      </table>
      <p class="muted" style="margin-top:12px;">当前读法：这张 green sample row 不是说 tiny-live 已经放行，而是把“red 已被关掉，shadow review 允许恢复”时必须留下的最小审计链一次写清。尤其 `prior_red_ref_id` 不能丢，否则 future run 很容易把恢复动作写成一条与历史断开的新行。</p>
      <p class="muted" style="margin-top:12px;">artifact：<code>reports/artifacts/alpha_closure_board/small_live_reopen_resume_sample_row_v1.csv</code></p>
    </div>

    <h2 class=\"section-title\">三条线并排看</h2>
    <div class=\"tracks\">{' '.join(cards)}</div>

    <div class=\"card\" style=\"padding:18px 20px; margin-top:18px;\">
      <h2 style=\"margin:0 0 8px;\">一张表看当前排优先级</h2>
      <table>
        <thead>
          <tr>
            <th>资源顺序</th>
            <th>paper admission</th>
            <th>研究线</th>
            <th>当前角色</th>
            <th>当前状态</th>
            <th>下一步最值得做什么</th>
          </tr>
        </thead>
        <tbody>{compare_rows}</tbody>
      </table>
    </div>

    <div class=\"card\" style=\"padding:18px 20px; margin-top:18px;\">
      <h2 style=\"margin:0 0 8px;\">如果这三条线都没过 gate，下一轮该回到哪里找新 alpha？</h2>
      <ul>
        <li>不是回到泛泛 digest，而是优先回到 <b>E. External Alpha / Literature Scout</b> 里最贴当前主线的问题：<b>structure-event 的 confirmation / retest / filter / raw baseline</b>。</li>
        <li>优先寻找三类新对象：<b>能和 EMA baseline 正面对比的 raw alpha</b>、<b>能改善 breakout-short honesty 的执行/过滤层</b>、以及 <b>比 Fibonacci 更诚实的窄确认层</b>。</li>
        <li>只有当这三条收口线在 rolling / OOS / cost 后都明显转弱，才值得把默认资源顺序从 closure-first 重新拨回外部 alpha hunting。</li>
      </ul>
    </div>

    <div class=\"card\" style=\"padding:18px 20px; margin-top:18px;\">
      <h2 style=\"margin:0 0 8px;\">建议的网页阅读顺序</h2>
      <ul>
        <li>先看这页：确认三条线的当前定位、别过度解读什么、下一步该补什么。</li>
        <li>再看 <a href=\"../ema_psar_raw_alpha/report.html\">EMA / PSAR Raw Alpha Focus</a>：回答 raw alpha baseline 候选现在最像谁。</li>
        <li>再看 <a href=\"../pytrendline_event_validation_v3_final_verdict/report.html\">v3 Final Verdict</a> + <a href=\"../support_breakout_v0_h24/report.html\">breakout v0</a>：回答结构事件线里真正保留下来的是什么。</li>
        <li>最后看 <a href=\"../support_breakout_v0_fib_ab/report.html\">Fib A/B 收口页</a>：回答为什么 Fibonacci 这轮应该收口，而不是继续升格。</li>
      </ul>
    </div>
  </div>
</body>
</html>
"""


def main() -> int:
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    promotion_gate_rows = get_promotion_gate_rows()
    small_live_plumbing_rows = get_small_live_plumbing_rows()
    small_live_ledger_rows = get_small_live_ledger_rows()
    small_live_routing_dry_run_rows = get_small_live_routing_dry_run_rows()
    small_live_routing_dry_run_sample_rows = get_small_live_routing_dry_run_sample_rows()
    small_live_operator_reconciliation_rows = get_small_live_operator_reconciliation_rows()
    small_live_operator_handoff_rows = get_small_live_operator_handoff_rows()
    small_live_review_ticket_template_rows = get_small_live_review_ticket_template_rows()
    small_live_review_writeback_matrix_rows = get_small_live_review_writeback_matrix_rows()
    small_live_review_registry_template_rows = get_small_live_review_registry_template_rows()
    small_live_shadow_parity_rows = get_small_live_shadow_parity_rows()
    small_live_parity_red_action_rows = get_small_live_parity_red_action_rows()
    small_live_shadow_parity_sample_rows = get_small_live_shadow_parity_sample_rows()
    small_live_green_shadow_parity_sample_rows = get_small_live_green_shadow_parity_sample_rows()
    small_live_reopen_gate_rows = get_small_live_reopen_gate_rows()
    small_live_reopen_resume_sample_rows = get_small_live_reopen_resume_sample_rows()
    rank2_closeout_snapshot_rows = get_rank2_closeout_snapshot_rows()
    rank2_receipt_audit_rows = get_rank2_receipt_audit_rows()
    rank2_replay_runsheet_rows = get_rank2_replay_runsheet_rows()
    rank2_replay_closeout_matrix_rows = get_rank2_replay_closeout_matrix_rows()
    rank2_shadow_parity_launch_packet_rows = get_rank2_shadow_parity_launch_packet_rows()
    rank2_shadow_parity_starter_rows = get_rank2_shadow_parity_starter_rows()
    rank2_next_status_change_gate_rows = get_rank2_next_status_change_gate_rows()
    rank2_next_replay_bundle_rows = get_rank2_next_replay_bundle_rows()
    rank2_execution_sync_guard_rows = get_rank2_execution_sync_guard_rows()
    baseline_compare_rows = get_baseline_compare_rows()
    small_live_default_seat_queue_rows = get_small_live_default_seat_queue_rows()
    small_live_live_seat_reentry_trigger_rows = get_small_live_live_seat_reentry_trigger_rows()
    small_live_status_change_watchboard_rows = get_small_live_status_change_watchboard_rows()
    small_live_status_trigger_snapshot_rows = get_small_live_status_trigger_snapshot_rows()
    small_live_now_action_queue_rows = get_small_live_now_action_queue_rows()
    small_live_evidence_freshness_board_rows = get_small_live_evidence_freshness_board_rows()
    small_live_state_resync_guard_rows = get_small_live_state_resync_guard_rows()
    rank2_replay_ready_gate_rows = get_rank2_replay_ready_gate_rows()
    write_promotion_gate_csv(promotion_gate_rows)
    write_small_live_plumbing_csv(small_live_plumbing_rows)
    write_small_live_ledger_csv(small_live_ledger_rows)
    write_small_live_routing_dry_run_csv(small_live_routing_dry_run_rows)
    write_small_live_routing_dry_run_sample_row_csv(small_live_routing_dry_run_sample_rows)
    write_small_live_operator_reconciliation_csv(small_live_operator_reconciliation_rows)
    write_small_live_operator_handoff_csv(small_live_operator_handoff_rows)
    write_small_live_review_ticket_template_csv(small_live_review_ticket_template_rows)
    write_small_live_review_writeback_matrix_csv(small_live_review_writeback_matrix_rows)
    write_small_live_review_registry_template_csv(small_live_review_registry_template_rows)
    write_small_live_shadow_parity_csv(small_live_shadow_parity_rows)
    write_small_live_parity_red_action_csv(small_live_parity_red_action_rows)
    write_small_live_shadow_parity_sample_row_csv(small_live_shadow_parity_sample_rows)
    write_small_live_green_shadow_parity_sample_row_csv(small_live_green_shadow_parity_sample_rows)
    write_small_live_reopen_gate_csv(small_live_reopen_gate_rows)
    write_small_live_reopen_resume_sample_row_csv(small_live_reopen_resume_sample_rows)
    write_rank2_closeout_snapshot_csv(rank2_closeout_snapshot_rows)
    write_rank2_receipt_audit_csv(rank2_receipt_audit_rows)
    write_rank2_replay_runsheet_csv(rank2_replay_runsheet_rows)
    write_rank2_replay_closeout_matrix_csv(rank2_replay_closeout_matrix_rows)
    write_rank2_shadow_parity_launch_packet_csv(rank2_shadow_parity_launch_packet_rows)
    write_rank2_shadow_parity_starter_rows_csv(rank2_shadow_parity_starter_rows)
    write_rank2_next_status_change_gate_csv(rank2_next_status_change_gate_rows)
    write_rank2_next_replay_bundle_csv(rank2_next_replay_bundle_rows)
    write_baseline_compare_csv(baseline_compare_rows)
    write_small_live_default_seat_queue_csv(small_live_default_seat_queue_rows)
    write_small_live_live_seat_reentry_trigger_csv(small_live_live_seat_reentry_trigger_rows)
    write_small_live_status_change_watchboard_csv(small_live_status_change_watchboard_rows)
    write_small_live_status_trigger_snapshot_csv(small_live_status_trigger_snapshot_rows)
    write_small_live_now_action_queue_csv(small_live_now_action_queue_rows)
    write_small_live_evidence_freshness_board_csv(small_live_evidence_freshness_board_rows)
    write_small_live_state_resync_guard_csv(small_live_state_resync_guard_rows)
    write_rank2_execution_sync_guard_csv(rank2_execution_sync_guard_rows)
    write_rank2_replay_ready_gate_csv(rank2_replay_ready_gate_rows)
    OUT_PATH.write_text(render(), encoding="utf-8")
    print("[ok] alpha closure board generated")
    print("[site]", OUT_PATH)
    print("[artifact]", PROMOTION_GATE_PATH)
    print("[artifact]", SMALL_LIVE_PLUMBING_PATH)
    print("[artifact]", SMALL_LIVE_LEDGER_TEMPLATE_PATH)
    print("[artifact]", SMALL_LIVE_ROUTING_DRY_RUN_CHECKLIST_PATH)
    print("[artifact]", SMALL_LIVE_ROUTING_DRY_RUN_SAMPLE_ROW_PATH)
    print("[artifact]", SMALL_LIVE_OPERATOR_RECONCILIATION_SEQUENCE_PATH)
    print("[artifact]", SMALL_LIVE_OPERATOR_HANDOFF_PACKET_PATH)
    print("[artifact]", SMALL_LIVE_REVIEW_TICKET_TEMPLATE_PATH)
    print("[artifact]", SMALL_LIVE_REVIEW_WRITEBACK_MATRIX_PATH)
    print("[artifact]", SMALL_LIVE_REVIEW_REGISTRY_TEMPLATE_PATH)
    print("[artifact]", SMALL_LIVE_SHADOW_PARITY_CHECKLIST_PATH)
    print("[artifact]", SMALL_LIVE_PARITY_RED_ACTION_LADDER_PATH)
    print("[artifact]", SMALL_LIVE_SHADOW_PARITY_SAMPLE_ROW_PATH)
    print("[artifact]", SMALL_LIVE_GREEN_SHADOW_PARITY_SAMPLE_ROW_PATH)
    print("[artifact]", SMALL_LIVE_REOPEN_GATE_CHECKLIST_PATH)
    print("[artifact]", SMALL_LIVE_REOPEN_RESUME_SAMPLE_ROW_PATH)
    print("[artifact]", SMALL_LIVE_RANK2_CLOSEOUT_SNAPSHOT_PATH)
    print("[artifact]", SMALL_LIVE_RANK2_RECEIPT_AUDIT_PATH)
    print("[artifact]", SMALL_LIVE_RANK2_REPLAY_RUNSHEET_PATH)
    print("[artifact]", SMALL_LIVE_RANK2_REPLAY_CLOSEOUT_MATRIX_PATH)
    print("[artifact]", SMALL_LIVE_RANK2_SHADOW_PARITY_LAUNCH_PACKET_PATH)
    print("[artifact]", SMALL_LIVE_RANK2_SHADOW_PARITY_STARTER_ROWS_PATH)
    print("[artifact]", SMALL_LIVE_RANK2_NEXT_STATUS_CHANGE_GATE_PATH)
    print("[artifact]", SMALL_LIVE_RANK2_NEXT_REPLAY_BUNDLE_PATH)
    print("[artifact]", SMALL_LIVE_DEFAULT_SEAT_QUEUE_PATH)
    print("[artifact]", SMALL_LIVE_LIVE_SEAT_REENTRY_TRIGGER_MATRIX_PATH)
    print("[artifact]", SMALL_LIVE_STATUS_CHANGE_WATCHBOARD_PATH)
    print("[artifact]", SMALL_LIVE_STATUS_TRIGGER_SNAPSHOT_PATH)
    print("[artifact]", SMALL_LIVE_NOW_ACTION_QUEUE_PATH)
    print("[artifact]", SMALL_LIVE_STATE_RESYNC_GUARD_PATH)
    print("[artifact]", BASELINE_COMPARE_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
