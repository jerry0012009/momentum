#!/usr/bin/env python3
"""Build a rollup for batch-specific taxonomy review packet validations."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DIAG_DIR = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_diagnostics"
DEFAULT_GLOB = "industry_taxonomy_review_batch_*_validation.json"
DEFAULT_JSON = "industry_taxonomy_review_batch_validation_rollup.json"
DEFAULT_CSV = "industry_taxonomy_review_batch_validation_rollup.csv"
BATCH_RE = re.compile(r"industry_taxonomy_review_batch_(\d+)_validation\.json$")


def _batch_id_from_path(path: Path, payload: dict[str, object]) -> int:
    match = BATCH_RE.match(path.name)
    if match:
        return int(match.group(1))
    packet_csv = str(payload.get("packet_csv", ""))
    packet_match = re.search(r"industry_taxonomy_review_batch_(\d+)\.csv$", packet_csv)
    if packet_match:
        return int(packet_match.group(1))
    return 0


def load_validation_rollup_rows(paths: list[Path]) -> list[dict[str, object]]:
    """Load validation reports into compact rollup rows."""
    rows: list[dict[str, object]] = []
    for path in sorted(paths):
        try:
            payload = json.loads(path.read_text())
        except Exception as exc:
            rows.append({
                "review_batch_id": _batch_id_from_path(path, {}),
                "validation_report": str(path),
                "packet_csv": "",
                "overall_pass": False,
                "blocker": f"validation_report_unreadable:{exc}",
                "packet_rows": 0,
                "approved_packet_rows": 0,
                "approved_symbols": "",
                "approved_bar_count_share": None,
                "approved_quote_volume_share": None,
                "latest_bar_timestamp": "",
                "allow_no_ok": False,
                "generated_at": "",
                "ready_to_apply": False,
            })
            continue
        overall_pass = bool(payload.get("overall_pass", False))
        approved_rows = int(payload.get("approved_packet_rows", 0) or 0)
        rows.append({
            "review_batch_id": _batch_id_from_path(path, payload),
            "validation_report": str(path),
            "packet_csv": str(payload.get("packet_csv", "")),
            "overall_pass": overall_pass,
            "blocker": str(payload.get("blocker", "")),
            "packet_rows": int(payload.get("packet_rows", 0) or 0),
            "approved_packet_rows": approved_rows,
            "approved_symbols": str(payload.get("approved_symbols", "")),
            "approved_bar_count_share": payload.get("approved_bar_count_share"),
            "approved_quote_volume_share": payload.get("approved_quote_volume_share"),
            "latest_bar_timestamp": str(payload.get("latest_bar_timestamp", "")),
            "allow_no_ok": bool(payload.get("allow_no_ok", False)),
            "generated_at": str(payload.get("generated_at", "")),
            "ready_to_apply": bool(overall_pass and approved_rows > 0),
        })
    return sorted(rows, key=lambda row: (int(row["review_batch_id"]), str(row["validation_report"])))


def build_rollup(
    diag_dir: Path = DEFAULT_DIAG_DIR,
    pattern: str = DEFAULT_GLOB,
) -> dict[str, object]:
    paths = sorted(diag_dir.glob(pattern))
    rows = load_validation_rollup_rows(paths)
    ready_rows = [row for row in rows if row["ready_to_apply"]]
    blocked_rows = [row for row in rows if not row["ready_to_apply"]]
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "diag_dir": str(diag_dir),
        "pattern": pattern,
        "batch_report_count": int(len(rows)),
        "ready_to_apply_batch_count": int(len(ready_rows)),
        "blocked_batch_count": int(len(blocked_rows)),
        "total_packet_rows": int(sum(int(row["packet_rows"] or 0) for row in rows)),
        "total_approved_packet_rows": int(sum(int(row["approved_packet_rows"] or 0) for row in rows)),
        "approved_bar_count_share_sum": float(sum(float(row["approved_bar_count_share"] or 0.0) for row in rows)),
        "approved_quote_volume_share_sum": float(sum(float(row["approved_quote_volume_share"] or 0.0) for row in rows)),
        "ready_to_apply_batch_ids": "|".join(str(row["review_batch_id"]) for row in ready_rows),
        "blocked_batch_ids": "|".join(str(row["review_batch_id"]) for row in blocked_rows),
    }
    return {"summary": summary, "batches": rows}


def write_rollup_reports(
    rollup: dict[str, object],
    out_dir: Path = DEFAULT_DIAG_DIR,
    json_name: str = DEFAULT_JSON,
    csv_name: str = DEFAULT_CSV,
) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_dir / json_name
    out_csv = out_dir / csv_name
    out_json.write_text(json.dumps(rollup, indent=2, default=str) + "\n")
    pd.DataFrame(rollup["batches"]).to_csv(out_csv, index=False)
    return out_json, out_csv


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--diag-dir", default=str(DEFAULT_DIAG_DIR), help="Factor diagnostics directory")
    parser.add_argument("--pattern", default=DEFAULT_GLOB, help="Validation report glob")
    parser.add_argument("--json-name", default=DEFAULT_JSON, help="Output JSON file name")
    parser.add_argument("--csv-name", default=DEFAULT_CSV, help="Output CSV file name")
    args = parser.parse_args()

    try:
        rollup = build_rollup(Path(args.diag_dir), args.pattern)
        out_json, out_csv = write_rollup_reports(
            rollup,
            Path(args.diag_dir),
            json_name=args.json_name,
            csv_name=args.csv_name,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", flush=True)
        return 1

    summary = rollup["summary"]
    print("Crypto industry taxonomy review validation rollup")
    print(f"  batch_report_count: {summary['batch_report_count']}")
    print(f"  ready_to_apply_batch_count: {summary['ready_to_apply_batch_count']}")
    print(f"  blocked_batch_count: {summary['blocked_batch_count']}")
    print(f"  total_approved_packet_rows: {summary['total_approved_packet_rows']}")
    print(f"  ready_to_apply_batch_ids: {summary['ready_to_apply_batch_ids']}")
    print(f"  blocked_batch_ids: {summary['blocked_batch_ids']}")
    print(f"Saved: {out_json}")
    print(f"Saved: {out_csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
