#!/usr/bin/env python3
"""Check that taxonomy review batch packets cover the source workbook.

This is a packet-set QA gate. It verifies batch packet completeness before
manual review/apply, but it does not infer taxonomy groups, apply packets,
build artifacts, or register factors.
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
DEFAULT_SOURCE = ROOT / "data" / "sources" / "crypto_industry_taxonomy_contract_v1" / "symbol_taxonomy.csv"
DEFAULT_DIAG_DIR = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_diagnostics"
DEFAULT_PATTERN = "industry_taxonomy_review_batch_*.csv"
DEFAULT_JSON = "industry_taxonomy_review_packet_coverage.json"
DEFAULT_CSV = "industry_taxonomy_review_packet_coverage_checks.csv"
PACKET_RE = re.compile(r"industry_taxonomy_review_batch_(\d+)\.csv$")
REQUIRED_PACKET_COLUMNS = {"review_batch_id", "symbol", "target_quality_flag"}


def _check(checks: list[dict[str, object]], name: str, passed: bool, detail: str) -> None:
    checks.append({"check": name, "passed": bool(passed), "detail": detail})


def _pipe_join(values: list[str] | set[str]) -> str:
    return "|".join(sorted(str(v) for v in values if str(v)))


def _batch_id_from_path(path: Path) -> int:
    match = PACKET_RE.match(path.name)
    return int(match.group(1)) if match else 0


def load_packet_rows(paths: list[Path]) -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    for path in sorted(paths, key=lambda p: (_batch_id_from_path(p), str(p))):
        packet = pd.read_csv(path).fillna("")
        packet["packet_path"] = str(path)
        packet["packet_file_batch_id"] = _batch_id_from_path(path)
        rows.append(packet)
    if not rows:
        return pd.DataFrame(columns=["packet_path", "packet_file_batch_id"])
    return pd.concat(rows, ignore_index=True)


def check_review_packet_coverage(
    source_csv: Path = DEFAULT_SOURCE,
    diag_dir: Path = DEFAULT_DIAG_DIR,
    pattern: str = DEFAULT_PATTERN,
) -> dict[str, object]:
    checks: list[dict[str, object]] = []
    candidate_paths = sorted(diag_dir.glob(pattern), key=str)
    packet_paths = sorted(
        [path for path in candidate_paths if PACKET_RE.match(path.name)],
        key=lambda p: (_batch_id_from_path(p), str(p)),
    )

    _check(checks, "source_exists", source_csv.exists(), str(source_csv))
    if not source_csv.exists():
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_csv": str(source_csv),
            "diag_dir": str(diag_dir),
            "pattern": pattern,
            "candidate_file_count": int(len(candidate_paths)),
            "source_rows": 0,
            "packet_file_count": int(len(packet_paths)),
            "packet_rows": 0,
            "unique_packet_symbols": 0,
            "missing_source_symbols": "",
            "extra_packet_symbols": "",
            "duplicate_packet_symbols": "",
            "missing_batch_ids": "",
            "unexpected_batch_ids": "",
            "overall_pass": False,
            "blocker": "source_missing",
            "checks": checks,
        }

    source = pd.read_csv(source_csv).fillna("")
    source_symbols = source["symbol"].astype(str).str.strip() if "symbol" in source.columns else pd.Series(dtype=str)
    _check(checks, "source_has_symbol_column", "symbol" in source.columns, "symbol column present")
    _check(
        checks,
        "source_symbols_unique",
        not bool(source_symbols.duplicated().any()),
        f"{int(source_symbols.duplicated().sum())} duplicate source symbols",
    )

    _check(checks, "packet_files_exist", bool(packet_paths), f"{len(packet_paths)} packet files")
    packets = load_packet_rows(packet_paths)
    missing_packet_cols = REQUIRED_PACKET_COLUMNS - set(packets.columns)
    _check(
        checks,
        "packet_required_columns",
        not missing_packet_cols,
        f"Missing: {sorted(missing_packet_cols)}" if missing_packet_cols else "All present",
    )

    if missing_packet_cols:
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_csv": str(source_csv),
            "diag_dir": str(diag_dir),
            "pattern": pattern,
            "candidate_file_count": int(len(candidate_paths)),
            "source_rows": int(len(source)),
            "packet_file_count": int(len(packet_paths)),
            "packet_rows": int(len(packets)),
            "unique_packet_symbols": 0,
            "missing_source_symbols": "",
            "extra_packet_symbols": "",
            "duplicate_packet_symbols": "",
            "missing_batch_ids": "",
            "unexpected_batch_ids": "",
            "overall_pass": False,
            "blocker": "packet_missing_required_columns",
            "checks": checks,
        }

    packets["symbol"] = packets["symbol"].astype(str).str.strip()
    packets["review_batch_id"] = pd.to_numeric(packets["review_batch_id"], errors="coerce").fillna(0).astype(int)
    packet_symbols = packets["symbol"]

    non_empty_packet_symbols = packet_symbols.ne("")
    _check(
        checks,
        "packet_symbols_non_empty",
        bool(non_empty_packet_symbols.all()),
        f"{int(non_empty_packet_symbols.sum())}/{len(packets)} non-empty",
    )

    duplicate_packet_symbols = sorted(packet_symbols[packet_symbols.duplicated()].unique().tolist())
    _check(
        checks,
        "packet_symbols_unique_across_batches",
        not duplicate_packet_symbols,
        f"Duplicates: {duplicate_packet_symbols}" if duplicate_packet_symbols else "No duplicates",
    )

    source_symbol_set = set(source_symbols.tolist())
    packet_symbol_set = set(packet_symbols.tolist())
    missing_source_symbols = sorted(source_symbol_set - packet_symbol_set)
    extra_packet_symbols = sorted(packet_symbol_set - source_symbol_set)
    _check(
        checks,
        "all_source_symbols_in_packets",
        not missing_source_symbols,
        f"Missing: {missing_source_symbols}" if missing_source_symbols else "All source symbols covered",
    )
    _check(
        checks,
        "no_extra_packet_symbols",
        not extra_packet_symbols,
        f"Extra: {extra_packet_symbols}" if extra_packet_symbols else "No extra packet symbols",
    )
    _check(
        checks,
        "packet_row_count_matches_source",
        int(len(packets)) == int(len(source)),
        f"packet_rows={len(packets)} source_rows={len(source)}",
    )

    file_batch_ids = sorted({_batch_id_from_path(path) for path in packet_paths})
    expected_batch_ids = set(range(1, max(file_batch_ids or [0]) + 1))
    missing_batch_ids = sorted(expected_batch_ids - set(file_batch_ids))
    unexpected_batch_ids = sorted(batch_id for batch_id in file_batch_ids if batch_id <= 0)
    _check(
        checks,
        "packet_batch_ids_contiguous",
        not missing_batch_ids and not unexpected_batch_ids,
        (
            f"missing={missing_batch_ids} unexpected={unexpected_batch_ids}"
            if missing_batch_ids or unexpected_batch_ids
            else f"1..{max(file_batch_ids or [0])}"
        ),
    )

    mismatched_file_rows = packets[packets["review_batch_id"] != packets["packet_file_batch_id"]]
    mismatch_symbols = sorted(mismatched_file_rows["symbol"].astype(str).tolist())
    _check(
        checks,
        "packet_row_batch_id_matches_file",
        mismatch_symbols == [],
        f"Symbols: {mismatch_symbols}" if mismatch_symbols else "All rows match packet file batch id",
    )

    failed = [row["check"] for row in checks if not bool(row["passed"])]
    if not failed:
        blocker = ""
    elif "all_source_symbols_in_packets" in failed:
        blocker = "packet_coverage_missing_source_symbols"
    elif "no_extra_packet_symbols" in failed:
        blocker = "packet_coverage_extra_symbols"
    elif "packet_symbols_unique_across_batches" in failed:
        blocker = "packet_coverage_duplicate_symbols"
    elif "packet_batch_ids_contiguous" in failed:
        blocker = "packet_coverage_batch_ids_not_contiguous"
    else:
        blocker = "packet_coverage_checks_failed"

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_csv": str(source_csv),
        "diag_dir": str(diag_dir),
        "pattern": pattern,
        "candidate_file_count": int(len(candidate_paths)),
        "source_rows": int(len(source)),
        "packet_file_count": int(len(packet_paths)),
        "packet_rows": int(len(packets)),
        "unique_packet_symbols": int(packet_symbols.nunique()),
        "missing_source_symbols": _pipe_join(missing_source_symbols),
        "extra_packet_symbols": _pipe_join(extra_packet_symbols),
        "duplicate_packet_symbols": _pipe_join(set(duplicate_packet_symbols)),
        "missing_batch_ids": "|".join(str(v) for v in missing_batch_ids),
        "unexpected_batch_ids": "|".join(str(v) for v in unexpected_batch_ids),
        "overall_pass": not failed,
        "blocker": blocker,
        "checks": checks,
    }


def write_packet_coverage_reports(
    report: dict[str, object],
    out_dir: Path = DEFAULT_DIAG_DIR,
    json_name: str = DEFAULT_JSON,
    csv_name: str = DEFAULT_CSV,
) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_dir / json_name
    out_csv = out_dir / csv_name
    out_json.write_text(json.dumps(report, indent=2, default=str) + "\n")
    pd.DataFrame(report["checks"]).to_csv(out_csv, index=False)
    return out_json, out_csv


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-csv", default=str(DEFAULT_SOURCE), help="Reviewed taxonomy source CSV")
    parser.add_argument("--diag-dir", default=str(DEFAULT_DIAG_DIR), help="Factor diagnostics directory")
    parser.add_argument("--pattern", default=DEFAULT_PATTERN, help="Review packet glob under --diag-dir")
    parser.add_argument("--json-name", default=DEFAULT_JSON, help="Output JSON file name")
    parser.add_argument("--csv-name", default=DEFAULT_CSV, help="Output checks CSV file name")
    args = parser.parse_args()

    report = check_review_packet_coverage(Path(args.source_csv), Path(args.diag_dir), args.pattern)
    out_json, out_csv = write_packet_coverage_reports(
        report,
        Path(args.diag_dir),
        json_name=args.json_name,
        csv_name=args.csv_name,
    )

    print("Crypto industry taxonomy review packet coverage")
    print(f"  source_rows: {report['source_rows']}")
    print(f"  packet_file_count: {report['packet_file_count']}")
    print(f"  packet_rows: {report['packet_rows']}")
    print(f"  unique_packet_symbols: {report['unique_packet_symbols']}")
    print(f"  overall_pass: {report['overall_pass']}")
    print(f"  blocker: {report['blocker']}")
    print(f"Saved: {out_json}")
    print(f"Saved: {out_csv}")
    return 0 if report["overall_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
