#!/usr/bin/env python3
"""Build a single manual-review workbook from taxonomy batch packets.

The workbook is a convenience artifact for human review. It does not infer
taxonomy groups, approve rows, apply packet targets, build artifacts, or
register factors.
"""
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
DEFAULT_PATTERN = "industry_taxonomy_review_batch_*.csv"
DEFAULT_OUTPUT = DEFAULT_DIAG_DIR / "industry_taxonomy_review_workbook.csv"
DEFAULT_STATUS = DEFAULT_DIAG_DIR / "industry_taxonomy_review_workbook_status.json"
PACKET_RE = re.compile(r"industry_taxonomy_review_batch_(\d+)\.csv$")
REQUIRED_COLUMNS = {
    "review_batch_id",
    "review_priority_rank",
    "symbol",
    "target_sector",
    "target_industry",
    "target_subindustry",
    "target_quality_flag",
    "target_known_at",
    "target_effective_from",
}


def _batch_id_from_path(path: Path) -> int:
    match = PACKET_RE.match(path.name)
    return int(match.group(1)) if match else 0


def _packet_paths(diag_dir: Path, pattern: str) -> list[Path]:
    candidates = sorted(diag_dir.glob(pattern), key=str)
    return sorted(
        [path for path in candidates if PACKET_RE.match(path.name)],
        key=lambda path: (_batch_id_from_path(path), str(path)),
    )


def build_review_workbook(diag_dir: Path = DEFAULT_DIAG_DIR, pattern: str = DEFAULT_PATTERN) -> tuple[pd.DataFrame, dict[str, object]]:
    packet_paths = _packet_paths(diag_dir, pattern)
    if not packet_paths:
        raise FileNotFoundError(f"No taxonomy review batch packets matched {pattern} under {diag_dir}")

    frames: list[pd.DataFrame] = []
    for path in packet_paths:
        packet = pd.read_csv(path).fillna("")
        missing = REQUIRED_COLUMNS - set(packet.columns)
        if missing:
            raise ValueError(f"{path} missing required columns: {sorted(missing)}")
        packet["packet_path"] = str(path)
        packet["packet_file_batch_id"] = _batch_id_from_path(path)
        frames.append(packet)

    workbook = pd.concat(frames, ignore_index=True).fillna("")
    workbook["review_batch_id"] = pd.to_numeric(workbook["review_batch_id"], errors="coerce").fillna(0).astype(int)
    workbook["review_priority_rank"] = pd.to_numeric(workbook["review_priority_rank"], errors="coerce").fillna(0).astype(int)
    workbook["symbol"] = workbook["symbol"].astype(str).str.strip()
    workbook = workbook.sort_values(["review_batch_id", "review_priority_rank", "symbol"], kind="stable").reset_index(drop=True)

    duplicate_symbols = sorted(workbook.loc[workbook["symbol"].duplicated(), "symbol"].unique().tolist())
    mismatched_batch_rows = workbook[workbook["review_batch_id"] != workbook["packet_file_batch_id"]]
    status = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "diag_dir": str(diag_dir),
        "pattern": pattern,
        "packet_file_count": int(len(packet_paths)),
        "workbook_rows": int(len(workbook)),
        "unique_symbols": int(workbook["symbol"].nunique()),
        "duplicate_symbols": "|".join(duplicate_symbols),
        "batch_id_mismatch_symbols": "|".join(mismatched_batch_rows["symbol"].astype(str).tolist()),
        "overall_pass": bool(not duplicate_symbols and mismatched_batch_rows.empty),
        "note": "Manual review convenience workbook only; validate/apply gates still control taxonomy changes.",
    }
    return workbook, status


def write_review_workbook(
    workbook: pd.DataFrame,
    status: dict[str, object],
    output_csv: Path = DEFAULT_OUTPUT,
    status_json: Path = DEFAULT_STATUS,
) -> tuple[Path, Path]:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    status_json.parent.mkdir(parents=True, exist_ok=True)
    workbook.to_csv(output_csv, index=False)
    status_json.write_text(json.dumps({**status, "output_csv": str(output_csv)}, indent=2, default=str) + "\n")
    return output_csv, status_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--diag-dir", default=str(DEFAULT_DIAG_DIR), help="Factor diagnostics directory")
    parser.add_argument("--pattern", default=DEFAULT_PATTERN, help="Review packet glob under --diag-dir")
    parser.add_argument("--output-csv", default=str(DEFAULT_OUTPUT), help="Merged manual review workbook CSV")
    parser.add_argument("--status-json", default=str(DEFAULT_STATUS), help="Workbook status JSON")
    args = parser.parse_args()

    try:
        workbook, status = build_review_workbook(Path(args.diag_dir), args.pattern)
        out_csv, out_json = write_review_workbook(workbook, status, Path(args.output_csv), Path(args.status_json))
    except Exception as exc:
        print(f"ERROR: {exc}", flush=True)
        return 1

    print("Crypto industry taxonomy review workbook")
    print(f"  packet_file_count: {status['packet_file_count']}")
    print(f"  workbook_rows: {status['workbook_rows']}")
    print(f"  unique_symbols: {status['unique_symbols']}")
    print(f"  overall_pass: {status['overall_pass']}")
    print(f"Saved: {out_csv}")
    print(f"Saved: {out_json}")
    return 0 if status["overall_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
