#!/usr/bin/env python3
"""Build the validated crypto industry taxonomy artifact from reviewed CSV.

This is the only supported intake path for the optional taxonomy parquet used
by Alpha101 IndNeutralize factors. It validates the contract before writing the
artifact consumed by build_factor_values.py.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "sources" / "crypto_industry_taxonomy_contract_v1" / "symbol_taxonomy.csv"
DEFAULT_OUTPUT = ROOT / "data" / "cache" / "crypto_industry_taxonomy_contract_v1" / "symbol_taxonomy.parquet"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_crypto_industry_taxonomy_contract import (  # noqa: E402
    validate_taxonomy_contract,
    write_check_reports,
)

TIMESTAMP_COLUMNS = ["known_at", "effective_from", "effective_to"]


def load_reviewed_taxonomy_csv(path: Path) -> pd.DataFrame:
    """Load reviewed taxonomy CSV and normalize timestamp columns."""
    if not path.exists():
        raise FileNotFoundError(f"Reviewed taxonomy CSV not found: {path}")

    df = pd.read_csv(path)
    for col in TIMESTAMP_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], utc=True, errors="coerce")
    return df


def build_taxonomy_artifact(input_csv: Path, output_parquet: Path) -> list[dict[str, object]]:
    """Validate reviewed taxonomy CSV and write the parquet artifact on pass."""
    df = load_reviewed_taxonomy_csv(input_csv)
    checks = validate_taxonomy_contract(df.copy())
    write_check_reports(checks, output_parquet.parent, output_parquet)

    if not all(bool(c["passed"]) for c in checks):
        if output_parquet.exists():
            output_parquet.unlink()
        return checks

    output_parquet.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_parquet, index=False)
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-csv", default=str(DEFAULT_INPUT), help="Reviewed taxonomy CSV")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Validated parquet artifact path")
    args = parser.parse_args()

    input_csv = Path(args.input_csv)
    output = Path(args.output)
    print(f"Building crypto industry taxonomy artifact")
    print(f"  input_csv: {input_csv}")
    print(f"  output:    {output}")

    try:
        checks = build_taxonomy_artifact(input_csv, output)
    except Exception as exc:
        print(f"ERROR: {exc}", flush=True)
        return 1

    all_passed = all(bool(c["passed"]) for c in checks)
    for check in checks:
        status = "PASS" if check["passed"] else "FAIL"
        print(f"  {status} {check['check']}: {check['detail']}")
    print(f"Overall: {'PASS' if all_passed else 'FAIL'}")
    if all_passed:
        print(f"Saved taxonomy parquet: {output}")
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
