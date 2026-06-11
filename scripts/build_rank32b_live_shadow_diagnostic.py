#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "rank32b_final_goal_gate"
LIVE_CLOSED = ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_recent_closed_trades.json"
SHADOW_SELECTED = ROOT / "reports" / "artifacts" / "rank32b_shadow_global_winner" / "shadow_selected_signals.json"
SHADOW_RECENT_SIGNALS = ROOT / "reports" / "artifacts" / "rank32b_shadow_global_winner" / "shadow_recent_signals.json"
SELECTED_SIGNAL_LEDGER = ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_selected_signal_ledger.jsonl"
COMPARE = ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_vs_shadow.csv"
COMPARE_SUMMARY = ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_vs_shadow_summary.json"
SAMPLE_LEDGER = ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_vs_shadow_high_quality_samples.csv"
LEDGER_COMPARE = ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_vs_shadow_ledger.csv"
LEDGER_COMPARE_SUMMARY = ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_vs_shadow_ledger_summary.json"


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_selected_signal_rows() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for path in (SHADOW_RECENT_SIGNALS, SHADOW_SELECTED):
        rows = read_json(path, [])
        if isinstance(rows, list):
            out.extend(row for row in rows if isinstance(row, dict))
    if SELECTED_SIGNAL_LEDGER.exists():
        for line in SELECTED_SIGNAL_LEDGER.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(row, dict):
                out.append(row)
    return out


def main() -> int:
    closed = read_json(LIVE_CLOSED, [])
    selected = read_selected_signal_rows()
    compare_summary = read_json(COMPARE_SUMMARY, {})
    ledger_compare_summary = read_json(LEDGER_COMPARE_SUMMARY, {})
    compare_df = pd.read_csv(COMPARE) if COMPARE.exists() else pd.DataFrame()
    sample_ledger_df = pd.read_csv(SAMPLE_LEDGER) if SAMPLE_LEDGER.exists() else pd.DataFrame()

    selected_by_id = {str(row.get("signal_id") or ""): row for row in selected if isinstance(row, dict) and row.get("signal_id")}
    matched: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    symbol_counts: Counter[str] = Counter()
    missing_symbol_counts: Counter[str] = Counter()
    current_core_symbols = {"BTCUSDT", "ETHUSDT"}

    for trade in closed if isinstance(closed, list) else []:
        if not isinstance(trade, dict):
            continue
        signal_id = str(trade.get("signal_id") or "")
        symbol = str(trade.get("symbol") or "").upper()
        symbol_counts[symbol] += 1
        if signal_id in selected_by_id:
            matched.append(trade)
        else:
            missing_symbol_counts[symbol] += 1
            missing.append(
                {
                    "signal_id": signal_id,
                    "symbol": symbol,
                    "side": trade.get("side"),
                    "signal_confirmed_at": trade.get("signal_confirmed_at"),
                    "entry_time": trade.get("entry_time"),
                    "exit_time": trade.get("exit_time"),
                    "exit_reason": trade.get("exit_reason"),
                    "net_pnl": trade.get("net_pnl"),
                    "likely_reason": "signal_id_absent_from_current_shadow_selected_signal_artifact",
                    "current_core_symbol": symbol in current_core_symbols,
                }
            )

    compare_signal_ids = set()
    high_quality_rows = 0
    minute_unavailable_rows = 0
    entry_alignment_match_rate = None
    if not compare_df.empty and "signal_id" in compare_df.columns:
        compare_signal_ids = {str(value) for value in compare_df["signal_id"].dropna().tolist()}
        if "shadow_proxy_exit_reason" in compare_df.columns:
            minute_unavailable_mask = compare_df["shadow_proxy_exit_reason"].astype(str).str.contains("minute_bars_unavailable", case=False, na=False)
            minute_unavailable_rows = int(minute_unavailable_mask.sum())
        else:
            minute_unavailable_mask = pd.Series([False] * len(compare_df))
        if "live_entry_time" in compare_df.columns and "shadow_proxy_entry_time" in compare_df.columns:
            live_entry = pd.to_datetime(compare_df["live_entry_time"], utc=True, errors="coerce")
            shadow_entry = pd.to_datetime(compare_df["shadow_proxy_entry_time"], utc=True, errors="coerce")
            entry_diff_seconds = (shadow_entry - live_entry).dt.total_seconds().abs()
            aligned_mask = entry_diff_seconds.le(300)
            valid_entry_mask = live_entry.notna() & shadow_entry.notna()
            entry_alignment_match_rate = float(aligned_mask[valid_entry_mask].mean()) if valid_entry_mask.any() else None
        else:
            aligned_mask = pd.Series([False] * len(compare_df))
        high_quality_rows = int(((~minute_unavailable_mask) & aligned_mask.fillna(False)).sum())

    matched_but_not_compared = [
        {
            "signal_id": str(trade.get("signal_id") or ""),
            "symbol": str(trade.get("symbol") or "").upper(),
            "entry_time": trade.get("entry_time"),
            "exit_time": trade.get("exit_time"),
        }
        for trade in matched
        if str(trade.get("signal_id") or "") not in compare_signal_ids
    ]

    payload = {
        "status": "blocked_live_shadow_sample_insufficient",
        "live_closed_trades_total": len(closed) if isinstance(closed, list) else 0,
        "shadow_selected_signals_total": len(selected) if isinstance(selected, list) else 0,
        "selected_signal_ledger_exists": SELECTED_SIGNAL_LEDGER.exists(),
        "shadow_recent_signals_exists": SHADOW_RECENT_SIGNALS.exists(),
        "closed_trades_with_selected_signal_match": len(matched),
        "closed_trades_missing_selected_signal_match": len(missing),
        "live_vs_shadow_rows": int(len(compare_df)),
        "live_vs_shadow_high_quality_rows": high_quality_rows,
        "durable_high_quality_sample_ledger_rows": int(len(sample_ledger_df)),
        "durable_high_quality_sample_ledger_path": str(SAMPLE_LEDGER.relative_to(ROOT)) if SAMPLE_LEDGER.exists() else None,
        "live_vs_shadow_minute_bars_unavailable_rows": minute_unavailable_rows,
        "live_vs_shadow_entry_alignment_match_rate_5m": entry_alignment_match_rate,
        "matched_but_not_compared": len(matched_but_not_compared),
        "live_vs_shadow_summary": compare_summary,
        "supplementary_live_vs_shadow_ledger_summary": ledger_compare_summary,
        "closed_trade_symbol_counts": dict(sorted(symbol_counts.items())),
        "missing_signal_symbol_counts": dict(sorted(missing_symbol_counts.items())),
        "diagnosis": [
            "Current live-vs-shadow evidence is not enough to claim live/backtest consistency.",
            "The comparator audits closed live trades whose signal_id can be recovered from selected/recent signal artifacts or the append-only live ledger.",
            "Recovered historical coverage improved, but most recovered rows still lack minute-bar replay quality.",
            "Rows with minute_bars_unavailable or weak entry alignment are not enough to claim honest live/backtest parity.",
        ],
        "required_next_steps": [
            "Preserve every future selected live signal row in an append-only audit ledger at entry time.",
            "Compare at least five newly closed trades from the frozen current BTCUSDT/ETHUSDT global_live spec.",
            "Require high exit-bucket and close-match rates before marking the account-level goal complete.",
        ],
        "missing_examples": missing[:20],
        "matched_but_not_compared_examples": matched_but_not_compared[:20],
        "sources": {
            "live_closed": str(LIVE_CLOSED.relative_to(ROOT)),
            "shadow_selected": str(SHADOW_SELECTED.relative_to(ROOT)),
            "shadow_recent_signals": str(SHADOW_RECENT_SIGNALS.relative_to(ROOT)),
            "selected_signal_ledger": str(SELECTED_SIGNAL_LEDGER.relative_to(ROOT)),
            "compare": str(COMPARE.relative_to(ROOT)),
            "compare_summary": str(COMPARE_SUMMARY.relative_to(ROOT)),
            "durable_high_quality_sample_ledger": str(SAMPLE_LEDGER.relative_to(ROOT)),
            "supplementary_ledger_compare": str(LEDGER_COMPARE.relative_to(ROOT)),
            "supplementary_ledger_compare_summary": str(LEDGER_COMPARE_SUMMARY.relative_to(ROOT)),
        },
    }

    write_json(ART_DIR / "live_shadow_diagnostic.json", payload)
    md = f"""# Rank32b Live Shadow Diagnostic

Status: `{payload["status"]}`

- live closed trades total: `{payload["live_closed_trades_total"]}`
- shadow selected signals total: `{payload["shadow_selected_signals_total"]}`
- closed trades with selected signal match: `{payload["closed_trades_with_selected_signal_match"]}`
- closed trades missing selected signal match: `{payload["closed_trades_missing_selected_signal_match"]}`
- live_vs_shadow rows: `{payload["live_vs_shadow_rows"]}`
- high-quality live_vs_shadow rows: `{payload["live_vs_shadow_high_quality_rows"]}`
- durable high-quality sample ledger rows: `{payload["durable_high_quality_sample_ledger_rows"]}`
- minute bars unavailable rows: `{payload["live_vs_shadow_minute_bars_unavailable_rows"]}`
- entry alignment match rate within 5m: `{payload["live_vs_shadow_entry_alignment_match_rate_5m"]}`
- matched but not compared: `{payload["matched_but_not_compared"]}`

## Diagnosis

{chr(10).join(f"- {row}" for row in payload["diagnosis"])}

## Required Next Steps

{chr(10).join(f"- {row}" for row in payload["required_next_steps"])}

## Live Vs Shadow Summary

```json
{json.dumps(compare_summary, ensure_ascii=False, indent=2)}
```

## Supplementary Ledger Summary

```json
{json.dumps(ledger_compare_summary, ensure_ascii=False, indent=2)}
```
"""
    (ART_DIR / "live_shadow_diagnostic.md").write_text(md, encoding="utf-8")
    print(json.dumps({"status": payload["status"], "live_vs_shadow_rows": payload["live_vs_shadow_rows"], "missing": len(missing)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
