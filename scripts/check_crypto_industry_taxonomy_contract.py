#!/usr/bin/env python3
"""Validate the crypto industry taxonomy data contract.

This checks the optional taxonomy artifact required before Alpha101
IndNeutralize formulas can move from skipped manifest rows into the registry.
It does not register factors, compute factor_values, or modify diagnostics.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TAXONOMY_DIR = ROOT / "data" / "cache" / "crypto_industry_taxonomy_contract_v1"
TAXONOMY_PATH = TAXONOMY_DIR / "symbol_taxonomy.parquet"

REQUIRED_COLUMNS = {
    "symbol",
    "known_at",
    "effective_from",
    "effective_to",
    "sector",
    "industry",
    "subindustry",
    "taxonomy_version",
    "source",
    "quality_flag",
}
GROUP_COLUMNS = ["sector", "industry", "subindustry"]
VALID_QUALITY_FLAGS = {"OK", "REVIEW", "BLOCKED"}


def _check_row(checks: list[dict[str, object]], name: str, passed: bool, detail: str = "") -> None:
    checks.append({"check": name, "passed": bool(passed), "detail": detail})


def validate_taxonomy_contract(df: pd.DataFrame) -> list[dict[str, object]]:
    """Return contract checks for a taxonomy DataFrame."""
    checks: list[dict[str, object]] = []

    missing_cols = REQUIRED_COLUMNS - set(df.columns)
    _check_row(
        checks,
        "required_columns",
        not missing_cols,
        f"Missing: {sorted(missing_cols)}" if missing_cols else "All present",
    )
    if missing_cols:
        return checks

    for col in ["known_at", "effective_from", "effective_to"]:
        df[col] = pd.to_datetime(df[col], utc=True, errors="coerce")

    _check_row(checks, "non_empty", len(df) > 0, f"{len(df)} rows")
    _check_row(
        checks,
        "symbol_non_empty",
        df["symbol"].notna().all() and (df["symbol"].astype(str).str.len() > 0).all(),
        "All symbols populated" if df["symbol"].notna().all() else "Null symbol present",
    )

    bad_flags = sorted(set(df["quality_flag"].dropna().astype(str)) - VALID_QUALITY_FLAGS)
    _check_row(
        checks,
        "quality_flag_domain",
        not bad_flags and df["quality_flag"].notna().all(),
        f"Bad flags: {bad_flags}" if bad_flags else "OK/REVIEW/BLOCKED only",
    )

    ok = df["quality_flag"] == "OK"
    _check_row(
        checks,
        "has_ok_rows",
        ok.any(),
        f"{int(ok.sum())} OK rows",
    )
    missing_known = ok & df["known_at"].isna()
    missing_effective = ok & df["effective_from"].isna()
    _check_row(
        checks,
        "ok_rows_have_known_at",
        not missing_known.any(),
        f"{int(missing_known.sum())} OK rows missing known_at",
    )
    _check_row(
        checks,
        "ok_rows_have_effective_from",
        not missing_effective.any(),
        f"{int(missing_effective.sum())} OK rows missing effective_from",
    )

    bad_interval = ok & df["effective_to"].notna() & (df["effective_to"] <= df["effective_from"])
    _check_row(
        checks,
        "effective_interval_valid",
        not bad_interval.any(),
        f"{int(bad_interval.sum())} rows with effective_to <= effective_from",
    )

    for col in GROUP_COLUMNS:
        missing_group = ok & df[col].isna()
        empty_group = ok & df[col].notna() & (df[col].astype(str).str.len() == 0)
        _check_row(
            checks,
            f"ok_rows_have_{col}",
            not (missing_group.any() or empty_group.any()),
            f"{int((missing_group | empty_group).sum())} OK rows missing {col}",
        )

    ok_rows = df.loc[ok].copy()
    overlap_count = 0
    if not ok_rows.empty:
        sentinel = pd.Timestamp.max.tz_localize("UTC")
        ok_rows["effective_to_cmp"] = ok_rows["effective_to"].fillna(sentinel)
        for _symbol, g in ok_rows.sort_values(["symbol", "effective_from", "effective_to_cmp"]).groupby("symbol"):
            previous_end = None
            for row in g.itertuples(index=False):
                start = row.effective_from
                end = row.effective_to_cmp
                if previous_end is not None and start < previous_end:
                    overlap_count += 1
                previous_end = max(previous_end, end) if previous_end is not None else end
    _check_row(
        checks,
        "no_overlapping_ok_effective_windows",
        overlap_count == 0,
        f"{overlap_count} overlapping OK windows",
    )

    return checks


def check_contract(path: Path = TAXONOMY_PATH) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []
    if not path.exists():
        _check_row(checks, "file_exists", False, f"File not found: {path}")
        return checks

    _check_row(checks, "file_exists", True, str(path))
    df = pd.read_parquet(path)
    checks.extend(validate_taxonomy_contract(df))
    return checks


def write_check_reports(
    checks: list[dict[str, object]],
    out_dir: Path,
    checked_path: Path,
) -> tuple[Path, Path]:
    """Write JSON/CSV contract check reports and return their paths."""
    out_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "path": str(checked_path),
        "overall_pass": all(bool(c["passed"]) for c in checks),
        "checks": checks,
    }
    out_json = out_dir / "industry_taxonomy_contract_check.json"
    out_csv = out_dir / "industry_taxonomy_contract_check.csv"
    out_json.write_text(json.dumps(result, indent=2, default=str))
    pd.DataFrame(checks).to_csv(out_csv, index=False)
    return out_json, out_csv


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default=str(TAXONOMY_PATH), help="Taxonomy parquet path")
    args = parser.parse_args()

    path = Path(args.path)
    print(f"Checking crypto industry taxonomy contract: {path}")
    checks = check_contract(path)
    all_passed = all(bool(c["passed"]) for c in checks)

    for check in checks:
        status = "PASS" if check["passed"] else "FAIL"
        print(f"  {status} {check['check']}: {check['detail']}")
    print(f"\nOverall: {'PASS' if all_passed else 'FAIL'}")

    out_json, out_csv = write_check_reports(checks, path.parent, path)
    print(f"Saved: {out_json}")
    print(f"Saved: {out_csv}")
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
