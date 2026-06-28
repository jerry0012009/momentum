#!/usr/bin/env python3
"""Check the reviewed crypto industry taxonomy source CSV.

This is a source-level review gate before building the optional parquet
taxonomy artifact used by Alpha101 IndNeutralize factors. It does not register
factors, build factor values, or write taxonomy parquet.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "data" / "sources" / "crypto_industry_taxonomy_contract_v1" / "symbol_taxonomy.csv"
DEFAULT_DATASET_ID = "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1"
DEFAULT_BARS = ROOT / "data" / "cache" / DEFAULT_DATASET_ID / "bars_1h.parquet"
DEFAULT_OUT_DIR = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_diagnostics"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_crypto_industry_taxonomy_contract import (  # noqa: E402
    GROUP_COLUMNS,
    REQUIRED_COLUMNS,
    VALID_QUALITY_FLAGS,
)


def _check(checks: list[dict[str, object]], name: str, passed: bool, detail: str) -> None:
    checks.append({"check": name, "passed": bool(passed), "detail": detail})


def _pipe_join(values: set[str] | list[str]) -> str:
    return "|".join(sorted(str(v) for v in values if str(v)))


def summarize_review_source(
    source_path: Path = DEFAULT_SOURCE,
    required_groups: set[str] | None = None,
    bars_path: Path | None = None,
) -> dict[str, object]:
    required_groups = required_groups or set(GROUP_COLUMNS)
    checks: list[dict[str, object]] = []
    if not source_path.exists():
        _check(checks, "source_exists", False, f"File not found: {source_path}")
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_path": str(source_path),
            "source_exists": False,
            "row_count": 0,
            "quality_counts": {},
            "ok_row_count": 0,
            "required_groups": _pipe_join(required_groups),
            "ok_groups_present": "",
            "missing_required_ok_groups": _pipe_join(required_groups),
            "bars_path": str(bars_path) if bars_path else "",
            "bar_last_timestamp": "",
            "ok_rows_known_by_last_bar": 0,
            "ok_symbols_known_by_last_bar": 0,
            "ok_rows_known_after_last_bar": 0,
            "ok_known_at_blocks_bars": False,
            "ready_to_build_artifact": False,
            "blocker": "taxonomy_source_missing",
            "checks": checks,
        }

    df = pd.read_csv(source_path).fillna("")
    missing_cols = REQUIRED_COLUMNS - set(df.columns)
    _check(
        checks,
        "required_columns",
        not missing_cols,
        f"Missing: {sorted(missing_cols)}" if missing_cols else "All present",
    )
    if missing_cols:
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_path": str(source_path),
            "source_exists": True,
            "row_count": int(len(df)),
            "quality_counts": {},
            "ok_row_count": 0,
            "required_groups": _pipe_join(required_groups),
            "ok_groups_present": "",
            "missing_required_ok_groups": _pipe_join(required_groups),
            "bars_path": str(bars_path) if bars_path else "",
            "bar_last_timestamp": "",
            "ok_rows_known_by_last_bar": 0,
            "ok_symbols_known_by_last_bar": 0,
            "ok_rows_known_after_last_bar": 0,
            "ok_known_at_blocks_bars": False,
            "ready_to_build_artifact": False,
            "blocker": "taxonomy_source_missing_required_columns",
            "checks": checks,
        }

    quality_counts = {
        str(k): int(v)
        for k, v in df["quality_flag"].value_counts(dropna=False).to_dict().items()
    }
    bad_flags = sorted(set(df["quality_flag"].astype(str)) - VALID_QUALITY_FLAGS)
    _check(
        checks,
        "quality_flag_domain",
        not bad_flags,
        f"Bad flags: {bad_flags}" if bad_flags else "OK/REVIEW/BLOCKED only",
    )

    ok = df["quality_flag"] == "OK"
    ok_count = int(ok.sum())
    _check(checks, "has_ok_rows", ok_count > 0, f"{ok_count} OK rows")

    ok_groups_present: set[str] = set()
    for group in sorted(required_groups):
        if group not in df.columns:
            _check(checks, f"has_{group}_column", False, f"Missing column: {group}")
            continue
        complete = bool((ok_count > 0) and df.loc[ok, group].astype(str).str.len().gt(0).all())
        populated = bool((ok_count > 0) and df.loc[ok, group].astype(str).str.len().gt(0).any())
        if populated:
            ok_groups_present.add(group)
        missing = int((ok & df[group].astype(str).str.len().eq(0)).sum())
        _check(
            checks,
            f"ok_rows_have_{group}",
            complete,
            f"{missing} OK rows missing {group}",
        )

    missing_required_groups = sorted(required_groups - ok_groups_present)
    _check(
        checks,
        "required_groups_have_ok_rows",
        not missing_required_groups,
        (
            f"Missing groups with OK rows: {missing_required_groups}"
            if missing_required_groups
            else f"OK rows cover: {sorted(ok_groups_present)}"
        ),
    )

    symbol_count = int(df["symbol"].astype(str).str.len().gt(0).sum())
    _check(checks, "symbol_non_empty", symbol_count == len(df), f"{symbol_count}/{len(df)} non-empty")

    bar_last_timestamp = ""
    ok_rows_known_by_last_bar = 0
    ok_symbols_known_by_last_bar = 0
    ok_rows_known_after_last_bar = 0
    ok_known_at_blocks_bars = False
    if bars_path is not None:
        if not bars_path.exists():
            _check(checks, "bars_path_exists", False, f"File not found: {bars_path}")
            ok_known_at_blocks_bars = ok_count > 0
        else:
            bars = pd.read_parquet(bars_path, columns=["timestamp"])
            bar_ts = pd.to_datetime(bars["timestamp"], utc=True, errors="coerce").dropna()
            if bar_ts.empty:
                _check(checks, "bars_have_timestamps", False, "No valid bar timestamps")
                ok_known_at_blocks_bars = ok_count > 0
            else:
                last_bar = bar_ts.max()
                bar_last_timestamp = last_bar.strftime("%Y-%m-%dT%H:%M:%SZ")
                known_at = pd.to_datetime(df["known_at"], utc=True, errors="coerce")
                ok_known_by_last_bar = ok & known_at.notna() & (known_at <= last_bar)
                ok_known_after_last_bar = ok & known_at.notna() & (known_at > last_bar)
                ok_rows_known_by_last_bar = int(ok_known_by_last_bar.sum())
                ok_symbols_known_by_last_bar = int(df.loc[ok_known_by_last_bar, "symbol"].astype(str).nunique())
                ok_rows_known_after_last_bar = int(ok_known_after_last_bar.sum())
                ok_known_at_blocks_bars = bool(ok_count > 0 and ok_rows_known_by_last_bar == 0)
                _check(
                    checks,
                    "ok_rows_known_by_latest_bar",
                    not ok_known_at_blocks_bars,
                    (
                        f"{ok_rows_known_by_last_bar}/{ok_count} OK rows known by latest bar {bar_last_timestamp}"
                        if ok_count > 0
                        else "No OK rows to check against latest bar"
                    ),
                )

    ready = all(bool(c["passed"]) for c in checks)
    if ready:
        blocker = ""
    elif ok_count == 0:
        blocker = "taxonomy_review_has_no_ok_rows"
    elif ok_known_at_blocks_bars:
        blocker = "taxonomy_review_ok_known_at_after_bars"
    elif missing_required_groups:
        blocker = "taxonomy_review_missing_required_ok_groups"
    else:
        blocker = "taxonomy_review_source_checks_failed"

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_path": str(source_path),
        "source_exists": True,
        "row_count": int(len(df)),
        "quality_counts": quality_counts,
        "ok_row_count": ok_count,
        "required_groups": _pipe_join(required_groups),
        "ok_groups_present": _pipe_join(ok_groups_present),
        "missing_required_ok_groups": _pipe_join(set(missing_required_groups)),
        "bars_path": str(bars_path) if bars_path else "",
        "bar_last_timestamp": bar_last_timestamp,
        "ok_rows_known_by_last_bar": ok_rows_known_by_last_bar,
        "ok_symbols_known_by_last_bar": ok_symbols_known_by_last_bar,
        "ok_rows_known_after_last_bar": ok_rows_known_after_last_bar,
        "ok_known_at_blocks_bars": ok_known_at_blocks_bars,
        "ready_to_build_artifact": ready,
        "blocker": blocker,
        "checks": checks,
    }


def write_review_source_reports(report: dict[str, object], out_dir: Path = DEFAULT_OUT_DIR) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_dir / "industry_taxonomy_review_source_status.json"
    out_csv = out_dir / "industry_taxonomy_review_source_checks.csv"
    out_json.write_text(json.dumps(report, indent=2, default=str) + "\n")
    pd.DataFrame(report["checks"]).to_csv(out_csv, index=False)
    return out_json, out_csv


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-csv", default=str(DEFAULT_SOURCE), help="Reviewed taxonomy source CSV")
    parser.add_argument("--bars-path", default="", help="Optional factor bars parquet path for source known_at alignment checks")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Output diagnostics directory")
    parser.add_argument(
        "--required-groups",
        default=",".join(GROUP_COLUMNS),
        help="Comma-separated taxonomy groups required by currently blocked factors",
    )
    args = parser.parse_args()

    required_groups = {g.strip() for g in args.required_groups.split(",") if g.strip()}
    bars_path = Path(args.bars_path) if args.bars_path else None
    report = summarize_review_source(Path(args.source_csv), required_groups=required_groups, bars_path=bars_path)
    print("Crypto industry taxonomy review source status")
    print(f"  source: {report['source_path']}")
    print(f"  rows: {report['row_count']}")
    print(f"  quality: {report['quality_counts']}")
    print(f"  required_groups: {report['required_groups']}")
    print(f"  ok_groups_present: {report['ok_groups_present']}")
    if report["bars_path"]:
        print(f"  bars: {report['bars_path']}")
        print(f"  bar_last_timestamp: {report['bar_last_timestamp']}")
        print(f"  ok_rows_known_by_last_bar: {report['ok_rows_known_by_last_bar']}")
        print(f"  ok_known_at_blocks_bars: {report['ok_known_at_blocks_bars']}")
    print(f"  ready_to_build_artifact: {report['ready_to_build_artifact']}")
    print(f"  blocker: {report['blocker']}")
    out_json, out_csv = write_review_source_reports(report, Path(args.out_dir))
    print(f"Saved: {out_json}")
    print(f"Saved: {out_csv}")
    return 0 if report["ready_to_build_artifact"] else 1


if __name__ == "__main__":
    sys.exit(main())
