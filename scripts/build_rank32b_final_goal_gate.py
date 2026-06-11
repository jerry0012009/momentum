#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "rank32b_final_goal_gate"

CORE3_1Y = ROOT / "reports" / "artifacts" / "scout_rank32b_slope_floor_continuation_15m" / "live_parity_core3_1y_summary.json"
PARAM_STABILITY = ROOT / "reports" / "artifacts" / "scout_rank32b_slope_floor_continuation_15m" / "parameter_stability_summary.csv"
FIVEY_ASSET = ROOT / "reports" / "artifacts" / "scout_rank32b_slope_floor_continuation_15m" / "candidate_5y_stability_asset_summary.csv"
GLOBAL_LIVE_SUMMARY = ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_last_run_summary.json"
GLOBAL_LIVE_STATUS = ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_status.json"
GLOBAL_OPERATOR = ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_operator_packet.json"
GLOBAL_LIVE_VS_SHADOW = ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_vs_shadow.csv"
GLOBAL_LIVE_VS_SHADOW_SUMMARY = ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_vs_shadow_summary.json"
GLOBAL_LIVE_VS_SHADOW_SAMPLE_LEDGER = ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_vs_shadow_high_quality_samples.csv"
GLOBAL_LIVE_VS_SHADOW_LEDGER = ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_vs_shadow_ledger.csv"
GLOBAL_LIVE_VS_SHADOW_LEDGER_SUMMARY = ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_vs_shadow_ledger_summary.json"
CANARY_SUMMARY = ROOT / "reports" / "artifacts" / "rank32b_canary" / "phase6_last_run_summary.json"
CANARY_STATUS = ROOT / "reports" / "artifacts" / "rank32b_canary" / "phase6_status.json"
CANARY_WARNINGS = ROOT / "reports" / "artifacts" / "rank32b_canary" / "phase6_warnings.json"
RANK213_STATUS = ROOT / "reports" / "artifacts" / "rank213_live_canary_shell" / "live_status.json"
RUNNER_PATH = ROOT / "scripts" / "run_rank32b_global_live.py"
SIGNAL_ADAPTER_PATH = ROOT / "src" / "momentum" / "execution" / "canary32b" / "signal_adapter.py"
LIVE_SHADOW_DIAGNOSTIC = ART_DIR / "live_shadow_diagnostic.json"
RESIDUAL_FLATTEN_APPROVAL = ART_DIR / "residual_flatten_approval_packet.json"
RESIDUAL_FLATTEN_EXECUTION_PLAN = ART_DIR / "residual_flatten_execution_plan.json"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def latest_unexpected_position(warnings: list[dict]) -> dict | None:
    for row in reversed(warnings):
        if row.get("message") == "exchange has non-whitelist open position":
            return row
    return None


def rank213_attribution(symbol: str | None) -> dict:
    if not symbol or not RANK213_STATUS.exists():
        return {"checked": False}
    status = read_json(RANK213_STATUS)
    for pos in status.get("exchange_open_positions", []) or []:
        if pos.get("symbol") == symbol:
            return {
                "checked": True,
                "source": str(RANK213_STATUS.relative_to(ROOT)),
                "rank213_owned": bool(pos.get("rank213_owned")),
                "reconciliation_classification": pos.get("reconciliation_classification"),
                "matched_local_claim_count": pos.get("matched_local_claim_count"),
                "matched_closed_basket_ids": pos.get("matched_closed_basket_ids"),
            }
    return {"checked": True, "source": str(RANK213_STATUS.relative_to(ROOT)), "matched": False}


def build_gate() -> tuple[dict, str]:
    core3 = read_json(CORE3_1Y)
    live = read_json(GLOBAL_LIVE_SUMMARY)
    live_status = read_json(GLOBAL_LIVE_STATUS) if GLOBAL_LIVE_STATUS.exists() else {}
    operator = read_json(GLOBAL_OPERATOR)
    canary = read_json(CANARY_SUMMARY)
    canary_status = read_json(CANARY_STATUS)
    warnings = read_json(CANARY_WARNINGS) if CANARY_WARNINGS.exists() else []
    compare_summary = read_json(GLOBAL_LIVE_VS_SHADOW_SUMMARY) if GLOBAL_LIVE_VS_SHADOW_SUMMARY.exists() else {}
    ledger_compare_summary = read_json(GLOBAL_LIVE_VS_SHADOW_LEDGER_SUMMARY) if GLOBAL_LIVE_VS_SHADOW_LEDGER_SUMMARY.exists() else {}
    live_shadow_diagnostic = read_json(LIVE_SHADOW_DIAGNOSTIC) if LIVE_SHADOW_DIAGNOSTIC.exists() else {}
    residual_flatten_approval = read_json(RESIDUAL_FLATTEN_APPROVAL) if RESIDUAL_FLATTEN_APPROVAL.exists() else {}
    residual_flatten_execution_plan = read_json(RESIDUAL_FLATTEN_EXECUTION_PLAN) if RESIDUAL_FLATTEN_EXECUTION_PLAN.exists() else {}
    compare = pd.read_csv(GLOBAL_LIVE_VS_SHADOW) if GLOBAL_LIVE_VS_SHADOW.exists() else pd.DataFrame()
    sample_ledger = pd.read_csv(GLOBAL_LIVE_VS_SHADOW_SAMPLE_LEDGER) if GLOBAL_LIVE_VS_SHADOW_SAMPLE_LEDGER.exists() else pd.DataFrame()
    param = pd.read_csv(PARAM_STABILITY)
    fivey = pd.read_csv(FIVEY_ASSET)
    runner_text = RUNNER_PATH.read_text(encoding="utf-8")

    core_assets = fivey[fivey["asset"].isin(["BTC-USD", "ETH-USD", "SOL-USD"])]
    positive_core_asset_ratio = float((core_assets["total_return"] > 0).mean()) if not core_assets.empty else 0.0
    positive_param_ratio_10bps = float((param[param["cost_bps_per_side"] == 10.0]["mean_total_return"] > 0).mean()) if not param.empty else 0.0
    unexpected = latest_unexpected_position(warnings if isinstance(warnings, list) else [])
    unexpected_symbol = (((unexpected or {}).get("payload") or {}).get("exchange_position") or {}).get("symbol")
    unexpected_attribution = rank213_attribution(unexpected_symbol)
    exit_bucket_match_rate = float(compare["exit_bucket_match"].astype(str).str.lower().eq("true").mean()) if not compare.empty and "exit_bucket_match" in compare else None
    close_match_rate = float(compare["close_match"].astype(str).str.lower().eq("true").mean()) if not compare.empty and "close_match" in compare else None
    minute_unavailable_count = 0
    high_quality_compare_rows = 0
    entry_alignment_match_rate = None
    if not compare.empty:
        shadow_reason = compare.get("shadow_proxy_exit_reason")
        if shadow_reason is not None:
            minute_unavailable_mask = shadow_reason.astype(str).str.contains("minute_bars_unavailable", case=False, na=False)
            minute_unavailable_count = int(minute_unavailable_mask.sum())
        else:
            minute_unavailable_mask = pd.Series([False] * len(compare))
        if "live_entry_time" in compare.columns and "shadow_proxy_entry_time" in compare.columns:
            live_entry = pd.to_datetime(compare["live_entry_time"], utc=True, errors="coerce")
            shadow_entry = pd.to_datetime(compare["shadow_proxy_entry_time"], utc=True, errors="coerce")
            entry_diff_seconds = (shadow_entry - live_entry).dt.total_seconds().abs()
            aligned_mask = entry_diff_seconds.le(300)
            valid_entry_mask = live_entry.notna() & shadow_entry.notna()
            entry_alignment_match_rate = float(aligned_mask[valid_entry_mask].mean()) if valid_entry_mask.any() else None
        else:
            aligned_mask = pd.Series([False] * len(compare))
        high_quality_mask = (~minute_unavailable_mask) & aligned_mask.fillna(False)
        high_quality_compare_rows = int(high_quality_mask.sum())
    sample_ledger_rows = int(len(sample_ledger))
    sample_ledger_exit_bucket_match_rate = float(sample_ledger["exit_bucket_match"].astype(str).str.lower().eq("true").mean()) if not sample_ledger.empty and "exit_bucket_match" in sample_ledger else None
    sample_ledger_close_match_rate = float(sample_ledger["close_match"].astype(str).str.lower().eq("true").mean()) if not sample_ledger.empty and "close_match" in sample_ledger else None
    current_live_config_hash = live_status.get("current_config_hash")
    current_spec_samples = sample_ledger
    if current_live_config_hash and not sample_ledger.empty and "live_config_version" in sample_ledger.columns:
        current_spec_samples = sample_ledger[sample_ledger["live_config_version"].astype(str) == str(current_live_config_hash)]
    current_spec_sample_rows = int(len(current_spec_samples))
    current_spec_sample_close_match_rate = float(current_spec_samples["close_match"].astype(str).str.lower().eq("true").mean()) if not current_spec_samples.empty and "close_match" in current_spec_samples else None

    evidence = {
        "strategy_id": "rank32b_slope_floor_continuation_core_live",
        "research_positive": {
            "core3_1y_portfolio_total_return": core3.get("portfolio_total_return"),
            "core3_1y_selected_trades": core3.get("selected_trades"),
            "core3_1y_win_rate": core3.get("win_rate"),
            "core3_5y_positive_asset_ratio": positive_core_asset_ratio,
            "param_positive_ratio_10bps": positive_param_ratio_10bps,
        },
        "current_live": {
            "global_live_allow_live_orders": live.get("allow_live_orders"),
            "global_live_status": live.get("status"),
            "global_live_current_config_hash": current_live_config_hash,
            "global_live_closed_trades_total": live.get("closed_trades_total"),
            "global_live_latest_evaluated_bar_time": live.get("latest_evaluated_bar_time"),
            "global_live_desired_notional_usdt_by_symbol": live.get("desired_notional_usdt_by_symbol"),
            "canary_trade_enabled": canary_status.get("trade_enabled"),
            "canary_system_health": canary_status.get("system_health"),
            "canary_closed_trades_total": canary.get("closed_trades_total"),
            "canary_exchange_open_positions": canary.get("exchange_open_positions"),
            "canary_unexpected_exchange_positions": canary.get("unexpected_exchange_positions"),
            "latest_unexpected_position_warning": unexpected,
            "latest_unexpected_position_attribution": unexpected_attribution,
        },
        "live_vs_shadow": {
            "summary": compare_summary,
            "rows": int(len(compare)),
            "high_quality_rows": high_quality_compare_rows,
            "high_quality_sample_ledger_rows": sample_ledger_rows,
            "high_quality_sample_ledger_path": str(GLOBAL_LIVE_VS_SHADOW_SAMPLE_LEDGER.relative_to(ROOT)) if GLOBAL_LIVE_VS_SHADOW_SAMPLE_LEDGER.exists() else None,
            "high_quality_sample_ledger_exit_bucket_match_rate": sample_ledger_exit_bucket_match_rate,
            "high_quality_sample_ledger_close_match_rate": sample_ledger_close_match_rate,
            "current_spec_high_quality_sample_rows": current_spec_sample_rows,
            "current_spec_high_quality_sample_close_match_rate": current_spec_sample_close_match_rate,
            "minute_bars_unavailable_rows": minute_unavailable_count,
            "entry_alignment_match_rate_5m": entry_alignment_match_rate,
            "exit_bucket_match_rate": exit_bucket_match_rate,
            "close_match_rate": close_match_rate,
            "diagnostic": live_shadow_diagnostic,
            "supplementary_ledger_summary": ledger_compare_summary,
            "supplementary_ledger_path": str(GLOBAL_LIVE_VS_SHADOW_LEDGER.relative_to(ROOT)) if GLOBAL_LIVE_VS_SHADOW_LEDGER.exists() else None,
        },
        "code_path": {
            "runner_path": str(RUNNER_PATH.relative_to(ROOT)),
            "signal_adapter_path": str(SIGNAL_ADAPTER_PATH.relative_to(ROOT)),
            "runner_uses_signal_adapter": "Rank32BPerpSignalAdapter" in runner_text,
            "signal_adapter_exists": SIGNAL_ADAPTER_PATH.exists(),
        },
        "blocker_work_packets": {
            "live_shadow_diagnostic_path": str(LIVE_SHADOW_DIAGNOSTIC.relative_to(ROOT)) if LIVE_SHADOW_DIAGNOSTIC.exists() else None,
            "residual_flatten_approval_path": str(RESIDUAL_FLATTEN_APPROVAL.relative_to(ROOT)) if RESIDUAL_FLATTEN_APPROVAL.exists() else None,
            "residual_flatten_execution_plan_path": str(RESIDUAL_FLATTEN_EXECUTION_PLAN.relative_to(ROOT)) if RESIDUAL_FLATTEN_EXECUTION_PLAN.exists() else None,
            "residual_flatten_approval": residual_flatten_approval,
            "residual_flatten_execution_plan": residual_flatten_execution_plan,
        },
    }

    blockers: list[str] = []
    if float(core3.get("portfolio_total_return") or 0.0) <= 0:
        blockers.append("rank32b_core3_1y_not_positive")
    if int(core3.get("selected_trades") or 0) < 100:
        blockers.append("rank32b_core3_frequency_too_low")
    if positive_core_asset_ratio < 1.0:
        blockers.append("rank32b_core3_5y_asset_not_all_positive")
    if positive_param_ratio_10bps < 0.8:
        blockers.append("rank32b_parameter_neighborhood_weak")
    if not live.get("allow_live_orders"):
        blockers.append("global_live_not_running_with_live_orders")
    if canary.get("unexpected_exchange_positions", 0):
        if unexpected_attribution.get("rank213_owned"):
            blockers.append("cross_strategy_residual_position_present")
        else:
            blockers.append("unexpected_exchange_position_present")
    if compare.empty or len(compare) < 5:
        blockers.append("live_vs_shadow_sample_too_small")
    if high_quality_compare_rows < 5:
        blockers.append("live_vs_shadow_high_quality_sample_too_small")
    if sample_ledger_rows < 5:
        blockers.append("durable_live_shadow_sample_ledger_too_small")
    if current_spec_sample_rows < 5:
        blockers.append("current_spec_live_shadow_sample_ledger_too_small")
    if sample_ledger_exit_bucket_match_rate is not None and sample_ledger_exit_bucket_match_rate < 0.8:
        blockers.append("durable_live_shadow_sample_ledger_bucket_mismatch")
    if sample_ledger_close_match_rate is not None and sample_ledger_close_match_rate < 0.8:
        blockers.append("durable_live_shadow_sample_ledger_close_mismatch")
    if minute_unavailable_count:
        blockers.append("live_vs_shadow_replay_has_unavailable_minute_bars")
    if entry_alignment_match_rate is not None and entry_alignment_match_rate < 0.9:
        blockers.append("live_vs_shadow_entry_alignment_weak")
    if exit_bucket_match_rate is not None and exit_bucket_match_rate < 0.8:
        blockers.append("live_vs_shadow_exit_bucket_mismatch")
    if close_match_rate is not None and close_match_rate < 0.8:
        blockers.append("live_vs_shadow_close_mismatch")
    ledger_close_rate = ledger_compare_summary.get("close_match_rate") if isinstance(ledger_compare_summary, dict) else None
    if ledger_close_rate is not None and float(ledger_close_rate) < 0.8:
        blockers.append("supplementary_live_shadow_ledger_close_mismatch")
    if not evidence["code_path"]["runner_uses_signal_adapter"]:
        blockers.append("runner_not_using_shared_signal_adapter")

    decision = "continue_tiny_live_audit_blocked_from_goal_completion" if blockers else "goal_candidate_passes_current_gate"
    status = {
        "decision": decision,
        "hard_blockers": blockers,
        "evidence_path": str((ART_DIR / "evidence.json").relative_to(ROOT)),
        "audit_path": str((ART_DIR / "release_gate_audit.md").relative_to(ROOT)),
        "active_goal_completion_audit_path": str((ART_DIR / "active_goal_completion_audit.md").relative_to(ROOT)),
        "live_shadow_diagnostic_path": str(LIVE_SHADOW_DIAGNOSTIC.relative_to(ROOT)) if LIVE_SHADOW_DIAGNOSTIC.exists() else None,
        "residual_flatten_approval_path": str(RESIDUAL_FLATTEN_APPROVAL.relative_to(ROOT)) if RESIDUAL_FLATTEN_APPROVAL.exists() else None,
        "residual_flatten_execution_plan_path": str(RESIDUAL_FLATTEN_EXECUTION_PLAN.relative_to(ROOT)) if RESIDUAL_FLATTEN_EXECUTION_PLAN.exists() else None,
    }
    audit = render_audit(status, evidence)
    return {"status": status, "evidence": evidence}, audit


def render_audit(status: dict, evidence: dict) -> str:
    research = evidence["research_positive"]
    live = evidence["current_live"]
    compare = evidence["live_vs_shadow"]
    code = evidence["code_path"]
    packets = evidence["blocker_work_packets"]
    return f"""# Rank32b Final Goal Gate

## Decision

`{status["decision"]}`

This gate does not claim the overall user goal is complete. It checks whether the strongest currently running candidate can honestly satisfy the goal today.

## Research Evidence

- core3 1y portfolio_total_return: `{research["core3_1y_portfolio_total_return"]}`
- core3 1y selected_trades: `{research["core3_1y_selected_trades"]}`
- core3 1y win_rate: `{research["core3_1y_win_rate"]}`
- core3 5y positive asset ratio: `{research["core3_5y_positive_asset_ratio"]}`
- parameter neighborhood positive ratio at 10bps/side: `{research["param_positive_ratio_10bps"]}`

## Current Live Evidence

- global_live allow_live_orders: `{live["global_live_allow_live_orders"]}`
- global_live status: `{live["global_live_status"]}`
- global_live closed_trades_total: `{live["global_live_closed_trades_total"]}`
- canary trade_enabled: `{live["canary_trade_enabled"]}`
- canary system_health: `{live["canary_system_health"]}`
- canary exchange_open_positions: `{live["canary_exchange_open_positions"]}`
- canary unexpected_exchange_positions: `{live["canary_unexpected_exchange_positions"]}`
- unexpected position attribution: `{live["latest_unexpected_position_attribution"]}`

## Live Vs Shadow

- rows: `{compare["rows"]}`
- high_quality_rows: `{compare["high_quality_rows"]}`
- high_quality_sample_ledger_rows: `{compare["high_quality_sample_ledger_rows"]}`
- high_quality_sample_ledger_path: `{compare["high_quality_sample_ledger_path"]}`
- high_quality_sample_ledger_exit_bucket_match_rate: `{compare["high_quality_sample_ledger_exit_bucket_match_rate"]}`
- high_quality_sample_ledger_close_match_rate: `{compare["high_quality_sample_ledger_close_match_rate"]}`
- current_spec_high_quality_sample_rows: `{compare["current_spec_high_quality_sample_rows"]}`
- current_spec_high_quality_sample_close_match_rate: `{compare["current_spec_high_quality_sample_close_match_rate"]}`
- minute_bars_unavailable_rows: `{compare["minute_bars_unavailable_rows"]}`
- entry_alignment_match_rate_5m: `{compare["entry_alignment_match_rate_5m"]}`
- exit_bucket_match_rate: `{compare["exit_bucket_match_rate"]}`
- close_match_rate: `{compare["close_match_rate"]}`
- summary: `{compare["summary"]}`
- diagnostic status: `{compare["diagnostic"].get("status") if isinstance(compare.get("diagnostic"), dict) else None}`
- closed trades missing selected signal match: `{compare["diagnostic"].get("closed_trades_missing_selected_signal_match") if isinstance(compare.get("diagnostic"), dict) else None}`
- supplementary ledger: `{compare["supplementary_ledger_path"]}`
- supplementary ledger summary: `{compare["supplementary_ledger_summary"]}`

## Code Path

- runner: `{code["runner_path"]}`
- signal_adapter: `{code["signal_adapter_path"]}`
- runner_uses_signal_adapter: `{code["runner_uses_signal_adapter"]}`

## Blocker Work Packets

- live shadow diagnostic: `{packets["live_shadow_diagnostic_path"]}`
- residual flatten approval: `{packets["residual_flatten_approval_path"]}`
- residual flatten approval status: `{packets["residual_flatten_approval"].get("status") if isinstance(packets.get("residual_flatten_approval"), dict) else None}`
- residual flatten execution plan: `{packets["residual_flatten_execution_plan_path"]}`
- residual flatten execution plan status: `{packets["residual_flatten_execution_plan"].get("status") if isinstance(packets.get("residual_flatten_execution_plan"), dict) else None}`

## Hard Blockers

{chr(10).join(f"- `{b}`" for b in status["hard_blockers"])}
"""


def render_active_goal_completion_audit(status: dict, evidence: dict) -> str:
    blockers = status["hard_blockers"]
    decision = status["decision"]
    research = evidence["research_positive"]
    live = evidence["current_live"]
    compare = evidence["live_vs_shadow"]
    code = evidence["code_path"]
    packets = evidence["blocker_work_packets"]
    checklist = [
        {
            "requirement": "Use current momentum project results",
            "status": "pass",
            "evidence": "rank32b_slope_floor_continuation_core_live selected from existing scout/live artifacts",
        },
        {
            "requirement": "Honest/no future-function signal path",
            "status": "partial",
            "evidence": f"live runner uses shared signal adapter={code['runner_uses_signal_adapter']}; final live-vs-shadow parity is still blocked",
        },
        {
            "requirement": "Positive return evidence",
            "status": "pass",
            "evidence": (
                f"core3_1y_return={research['core3_1y_portfolio_total_return']}; "
                f"core3_5y_positive_asset_ratio={research['core3_5y_positive_asset_ratio']}"
            ),
        },
        {
            "requirement": "Trigger frequency",
            "status": "pass",
            "evidence": f"core3_1y_selected_trades={research['core3_1y_selected_trades']}; global_live_closed_trades_total={live['global_live_closed_trades_total']}",
        },
        {
            "requirement": "Parameter time stability",
            "status": "pass",
            "evidence": f"param_positive_ratio_10bps={research['param_positive_ratio_10bps']}",
        },
        {
            "requirement": "Small live operation",
            "status": "pass",
            "evidence": (
                f"allow_live_orders={live['global_live_allow_live_orders']}; "
                f"desired_notional_by_symbol={live['global_live_desired_notional_usdt_by_symbol']}"
            ),
        },
        {
            "requirement": "Account-level cleanliness for honest live audit",
            "status": "fail",
            "evidence": f"unexpected position attribution={live['latest_unexpected_position_attribution']}; flatten approval packet={packets['residual_flatten_approval_path']}",
        },
        {
            "requirement": "Live-vs-backtest consistency during operation",
            "status": "fail",
            "evidence": (
                f"rows={compare['rows']}; high_quality_rows={compare['high_quality_rows']}; "
                f"durable_sample_ledger_rows={compare['high_quality_sample_ledger_rows']}; "
                f"current_spec_sample_ledger_rows={compare['current_spec_high_quality_sample_rows']}; "
                f"minute_bars_unavailable_rows={compare['minute_bars_unavailable_rows']}; "
                f"exit_bucket_match_rate={compare['exit_bucket_match_rate']}; close_match_rate={compare['close_match_rate']}; "
                f"supplementary_ledger_close_match_rate={compare['supplementary_ledger_summary'].get('close_match_rate') if isinstance(compare.get('supplementary_ledger_summary'), dict) else None}; "
                f"diagnostic={packets['live_shadow_diagnostic_path']}"
            ),
        },
    ]
    checklist_md = "\n".join(
        f"- `{row['status']}` {row['requirement']}: {row['evidence']}"
        for row in checklist
    )
    return f"""# Active Goal Completion Audit

Decision: `{decision}`

The active user goal is not complete while any hard blocker remains. Do not mark the goal complete from this artifact unless the decision changes to `goal_candidate_passes_current_gate`.

Current blockers:

{chr(10).join(f"- `{b}`" for b in blockers) if blockers else "- none"}

## Prompt-To-Artifact Checklist

{checklist_md}

Current strongest candidate:

- strategy_id: `{evidence["strategy_id"]}`
- live enabled: `{evidence["current_live"]["global_live_allow_live_orders"]}`
- live status: `{evidence["current_live"]["global_live_status"]}`
- live_vs_shadow rows: `{evidence["live_vs_shadow"]["rows"]}`
- unexpected exchange position attribution: `{evidence["current_live"]["latest_unexpected_position_attribution"]}`

Required before completion:

- Resolve or explicitly scope out the residual exchange position.
- Accumulate enough newly closed live trades from the frozen BTCUSDT/ETHUSDT global-live spec.
- Re-run live-vs-shadow and require close/bucket consistency before claiming honest live/backtest parity.
"""


def main() -> int:
    ART_DIR.mkdir(parents=True, exist_ok=True)
    payload, audit = build_gate()
    write_json(ART_DIR / "evidence.json", payload["evidence"])
    write_json(ART_DIR / "status.json", payload["status"])
    (ART_DIR / "release_gate_audit.md").write_text(audit, encoding="utf-8")
    (ART_DIR / "active_goal_completion_audit.md").write_text(
        render_active_goal_completion_audit(payload["status"], payload["evidence"]),
        encoding="utf-8",
    )
    print(json.dumps(payload["status"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
