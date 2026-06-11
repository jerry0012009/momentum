#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
LIVE_CLOSED = ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_recent_closed_trades.json"
SHADOW_CLOSED = ROOT / "reports" / "artifacts" / "rank32b_shadow_global_winner" / "paper_closed_trades.json"
OUT_CSV = ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_vs_shadow_ledger.csv"
OUT_JSON = ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_vs_shadow_ledger_summary.json"


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def normalize_bucket(reason: Any) -> str:
    text = str(reason or "").lower()
    if any(token in text for token in ("take_profit", "target")):
        return "tp"
    if any(token in text for token in ("stop_loss", "stop")):
        return "sl"
    if "timeout" in text:
        return "timeout"
    if "external" in text:
        return "external"
    return text or "unknown"


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def main() -> int:
    live_rows = read_json(LIVE_CLOSED, [])
    shadow_rows = read_json(SHADOW_CLOSED, [])
    if not isinstance(live_rows, list):
        live_rows = []
    if not isinstance(shadow_rows, list):
        shadow_rows = []

    shadow_by_id: dict[str, dict[str, Any]] = {}
    for row in shadow_rows:
        if isinstance(row, dict) and row.get("signal_id"):
            shadow_by_id[str(row["signal_id"])] = row

    out: list[dict[str, Any]] = []
    for live in live_rows:
        if not isinstance(live, dict):
            continue
        signal_id = str(live.get("signal_id") or "")
        shadow = shadow_by_id.get(signal_id)
        if shadow is None:
            continue
        live_entry = pd.to_datetime(live.get("entry_time"), utc=True, errors="coerce")
        shadow_entry = pd.to_datetime(shadow.get("entry_ts"), utc=True, errors="coerce")
        live_exit = pd.to_datetime(live.get("exit_time"), utc=True, errors="coerce")
        shadow_exit = pd.to_datetime(shadow.get("exit_ts") or shadow.get("mark_ts"), utc=True, errors="coerce")
        entry_diff = float((shadow_entry - live_entry).total_seconds()) if pd.notna(live_entry) and pd.notna(shadow_entry) else None
        exit_diff = float((shadow_exit - live_exit).total_seconds()) if pd.notna(live_exit) and pd.notna(shadow_exit) else None

        live_notional = safe_float(live.get("entry_price")) * safe_float(live.get("qty"))
        shadow_net_ret = safe_float(shadow.get("net_ret"), safe_float(shadow.get("paper_effective_net_ret")))
        shadow_proxy_pnl = live_notional * shadow_net_ret
        live_bucket = normalize_bucket(live.get("exit_reason"))
        shadow_bucket = normalize_bucket(shadow.get("exit_reason"))
        bucket_match = live_bucket == shadow_bucket
        entry_match = entry_diff is not None and abs(entry_diff) <= 60.0
        exit_match = exit_diff is not None and abs(exit_diff) <= 300.0
        pnl_delta = safe_float(live.get("net_pnl")) - shadow_proxy_pnl
        out.append(
            {
                "signal_id": signal_id,
                "symbol": live.get("symbol"),
                "side": live.get("side"),
                "live_entry_time": live.get("entry_time"),
                "shadow_entry_time": shadow.get("entry_ts"),
                "entry_time_diff_seconds": entry_diff,
                "live_exit_time": live.get("exit_time"),
                "shadow_exit_time": shadow.get("exit_ts") or shadow.get("mark_ts"),
                "exit_time_diff_seconds": exit_diff,
                "live_exit_reason": live.get("exit_reason"),
                "shadow_exit_reason": shadow.get("exit_reason"),
                "live_exit_bucket": live_bucket,
                "shadow_exit_bucket": shadow_bucket,
                "exit_bucket_match": bucket_match,
                "entry_time_match_60s": entry_match,
                "exit_time_match_300s": exit_match,
                "close_match": bool(bucket_match and entry_match and exit_match),
                "live_net_pnl_usdt": safe_float(live.get("net_pnl")),
                "shadow_proxy_net_pnl_usdt": shadow_proxy_pnl,
                "delta_vs_shadow_usdt": pnl_delta,
                "live_net_return_bps": safe_float(live.get("net_return_bps")),
                "shadow_net_return_bps": shadow_net_ret * 10000.0,
                "shadow_model_version": shadow.get("shadow_model_version"),
                "shadow_status": shadow.get("status"),
                "shadow_bar_key": shadow.get("bar_key"),
            }
        )

    df = pd.DataFrame(out)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False)
    summary = {
        "status": "ok" if out else "empty",
        "method": "direct_match_live_closed_to_shadow_paper_closed_by_signal_id",
        "caveat": "Supplementary only: shadow_global_winner ledger may reflect all26 historical shadow config, not the current frozen BTCUSDT/ETHUSDT global_live spec.",
        "live_closed_trades": len(live_rows),
        "shadow_closed_trades": len(shadow_rows),
        "matched_rows": int(len(df)),
        "exit_bucket_match_rate": float(df["exit_bucket_match"].mean()) if not df.empty else None,
        "entry_time_match_60s_rate": float(df["entry_time_match_60s"].mean()) if not df.empty else None,
        "exit_time_match_300s_rate": float(df["exit_time_match_300s"].mean()) if not df.empty else None,
        "close_match_rate": float(df["close_match"].mean()) if not df.empty else None,
        "live_net_pnl_usdt": float(df["live_net_pnl_usdt"].sum()) if not df.empty else 0.0,
        "shadow_proxy_net_pnl_usdt": float(df["shadow_proxy_net_pnl_usdt"].sum()) if not df.empty else 0.0,
        "delta_vs_shadow_usdt": float(df["delta_vs_shadow_usdt"].sum()) if not df.empty else 0.0,
    }
    write_json(OUT_JSON, summary)
    print(json.dumps({"status": summary["status"], "matched_rows": summary["matched_rows"], "close_match_rate": summary["close_match_rate"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
