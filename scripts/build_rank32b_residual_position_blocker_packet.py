#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WARNINGS_PATH = ROOT / "reports" / "artifacts" / "rank32b_canary" / "phase6_warnings.json"
RANK213_STATUS_PATH = ROOT / "reports" / "artifacts" / "rank213_live_canary_shell" / "live_status.json"
ART_DIR = ROOT / "reports" / "artifacts" / "rank32b_final_goal_gate"


def latest_unexpected_position() -> dict | None:
    warnings = json.loads(WARNINGS_PATH.read_text(encoding="utf-8")) if WARNINGS_PATH.exists() else []
    for row in reversed(warnings):
        if row.get("message") == "exchange has non-whitelist open position":
            return row
    return None


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rank213_attribution(symbol: str | None) -> dict:
    if not symbol or not RANK213_STATUS_PATH.exists():
        return {"checked": False}
    status = json.loads(RANK213_STATUS_PATH.read_text(encoding="utf-8"))
    for pos in status.get("exchange_open_positions", []) or []:
        if pos.get("symbol") == symbol:
            return {
                "checked": True,
                "source": str(RANK213_STATUS_PATH.relative_to(ROOT)),
                "rank213_owned": bool(pos.get("rank213_owned")),
                "reconciliation_classification": pos.get("reconciliation_classification"),
                "matched_local_claim_count": pos.get("matched_local_claim_count"),
                "matched_closed_basket_ids": pos.get("matched_closed_basket_ids"),
            }
    return {"checked": True, "source": str(RANK213_STATUS_PATH.relative_to(ROOT)), "matched": False}


def main() -> int:
    row = latest_unexpected_position()
    symbol = (((row or {}).get("payload") or {}).get("exchange_position") or {}).get("symbol")
    attribution = rank213_attribution(symbol)
    packet = {
        "status": "blocked" if row else "clear",
        "blocker": "cross_strategy_residual_position_present" if attribution.get("rank213_owned") else ("unexpected_exchange_position_present" if row else None),
        "source": str(WARNINGS_PATH.relative_to(ROOT)),
        "rank213_attribution": attribution,
        "latest_warning": row,
        "required_operator_decision": (
            "Approve an explicit reduce-only flatten action for the residual exchange position, or mark it as intentionally managed outside this account-level goal."
            if row
            else ""
        ),
        "automation_policy": "No automatic real-order flatten was performed by this audit packet.",
    }
    write_json(ART_DIR / "residual_position_blocker_packet.json", packet)
    md = f"""# Rank32b Residual Position Blocker

Status: `{packet["status"]}`

Blocker: `{packet["blocker"]}`

Source: `{packet["source"]}`

Rank213 attribution:

```json
{json.dumps(attribution, ensure_ascii=False, indent=2)}
```

Required operator decision:

{packet["required_operator_decision"] or "No residual decision required."}

Automation policy:

{packet["automation_policy"]}

Latest warning:

```json
{json.dumps(row, ensure_ascii=False, indent=2)}
```
"""
    (ART_DIR / "residual_position_blocker_packet.md").write_text(md, encoding="utf-8")
    print(json.dumps({"status": packet["status"], "blocker": packet["blocker"], "path": str((ART_DIR / "residual_position_blocker_packet.json").relative_to(ROOT))}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
