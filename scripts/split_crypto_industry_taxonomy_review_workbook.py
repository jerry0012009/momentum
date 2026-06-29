#!/usr/bin/env python3
"""Split a reviewed taxonomy workbook back into batch packet CSVs.

This is a bridge from the single manual-review workbook to the existing
validate/apply gates. It does not infer taxonomy groups, validate OK rows,
apply targets, build artifacts, or register factors.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DIAG_DIR = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_diagnostics"
DEFAULT_WORKBOOK = DEFAULT_DIAG_DIR / "industry_taxonomy_review_workbook.csv"
DEFAULT_OUTPUT_DIR = DEFAULT_DIAG_DIR / "industry_taxonomy_reviewed_packets"
DEFAULT_STATUS = DEFAULT_DIAG_DIR / "industry_taxonomy_reviewed_packets_status.json"
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


def split_review_workbook(workbook: pd.DataFrame) -> tuple[dict[int, pd.DataFrame], dict[str, object]]:
    work = workbook.copy().fillna("")
    missing = REQUIRED_COLUMNS - set(work.columns)
    if missing:
        raise ValueError(f"workbook missing required columns: {sorted(missing)}")

    work["review_batch_id"] = pd.to_numeric(work["review_batch_id"], errors="coerce").fillna(0).astype(int)
    work["review_priority_rank"] = pd.to_numeric(work["review_priority_rank"], errors="coerce").fillna(0).astype(int)
    work["symbol"] = work["symbol"].astype(str).str.strip()

    duplicate_symbols = sorted(work.loc[work["symbol"].duplicated(), "symbol"].unique().tolist())
    bad_batch_rows = work[work["review_batch_id"] <= 0]
    if duplicate_symbols:
        raise ValueError(f"workbook has duplicate symbols: {duplicate_symbols}")
    if not bad_batch_rows.empty:
        raise ValueError(f"workbook has non-positive review_batch_id symbols: {bad_batch_rows['symbol'].tolist()}")

    packets: dict[int, pd.DataFrame] = {}
    for batch_id, packet in work.groupby("review_batch_id", sort=True):
        packets[int(batch_id)] = packet.sort_values(
            ["review_priority_rank", "symbol"],
            kind="stable",
        ).reset_index(drop=True)

    batch_ids = sorted(packets)
    expected = set(range(1, max(batch_ids or [0]) + 1))
    missing_batch_ids = sorted(expected - set(batch_ids))
    status = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "batch_count": int(len(packets)),
        "workbook_rows": int(len(work)),
        "unique_symbols": int(work["symbol"].nunique()),
        "batch_ids": "|".join(f"{batch_id:03d}" for batch_id in batch_ids),
        "missing_batch_ids": "|".join(f"{batch_id:03d}" for batch_id in missing_batch_ids),
        "overall_pass": bool(not missing_batch_ids),
        "note": "Split reviewed workbook into batch packets only; run validate/apply gates next.",
    }
    return packets, status


def write_split_packets(
    packets: dict[int, pd.DataFrame],
    status: dict[str, object],
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    status_json: Path = DEFAULT_STATUS,
) -> tuple[list[Path], Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    status_json.parent.mkdir(parents=True, exist_ok=True)
    output_paths: list[Path] = []
    for batch_id, packet in sorted(packets.items()):
        out = output_dir / f"industry_taxonomy_review_batch_{batch_id:03d}.csv"
        packet.to_csv(out, index=False)
        output_paths.append(out)
    status_json.write_text(
        json.dumps(
            {
                **status,
                "output_dir": str(output_dir),
                "output_files": "|".join(str(path) for path in output_paths),
            },
            indent=2,
            default=str,
        )
        + "\n"
    )
    return output_paths, status_json


def split_review_workbook_from_paths(
    workbook_csv: Path = DEFAULT_WORKBOOK,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    status_json: Path = DEFAULT_STATUS,
) -> dict[str, object]:
    if not workbook_csv.exists():
        raise FileNotFoundError(f"workbook CSV not found: {workbook_csv}")
    workbook = pd.read_csv(workbook_csv).fillna("")
    packets, status = split_review_workbook(workbook)
    output_paths, status_path = write_split_packets(packets, status, output_dir, status_json)
    return {
        **status,
        "workbook_csv": str(workbook_csv),
        "output_dir": str(output_dir),
        "status_json": str(status_path),
        "output_files": "|".join(str(path) for path in output_paths),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workbook-csv", default=str(DEFAULT_WORKBOOK), help="Reviewed workbook CSV")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Directory for reviewed batch packets")
    parser.add_argument("--status-json", default=str(DEFAULT_STATUS), help="Split status JSON")
    args = parser.parse_args()

    try:
        status = split_review_workbook_from_paths(
            Path(args.workbook_csv),
            Path(args.output_dir),
            Path(args.status_json),
        )
    except Exception as exc:
        print(f"ERROR: {exc}", flush=True)
        return 1

    print("Split crypto industry taxonomy review workbook")
    print(f"  batch_count: {status['batch_count']}")
    print(f"  workbook_rows: {status['workbook_rows']}")
    print(f"  unique_symbols: {status['unique_symbols']}")
    print(f"  overall_pass: {status['overall_pass']}")
    print(f"Saved: {status['output_dir']}")
    print(f"Saved: {status['status_json']}")
    return 0 if status["overall_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
