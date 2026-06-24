#!/usr/bin/env python3
"""Check market cap data contract.

Validates market_cap_1h_aligned.parquet against the data contract defined in PM spec.

Usage:
    python scripts/check_market_cap_data_contract.py

Outputs:
    data/cache/crypto_market_cap_1h_contract_v1/market_cap_contract_check.json
    data/cache/crypto_market_cap_1h_contract_v1/market_cap_contract_check.csv
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CAP_DIR = ROOT / "data" / "cache" / "crypto_market_cap_1h_contract_v1"
ALIGNED_PATH = CAP_DIR / "market_cap_1h_aligned.parquet"

REQUIRED_COLUMNS = {
    "timestamp", "symbol", "cap",
    "cap_source_timestamp", "cap_known_at",
    "cap_source", "cap_frequency", "cap_fill_method", "cap_quality_flag",
}


def check_contract():
    checks = []

    def add_check(name, passed, detail=""):
        checks.append({"check": name, "passed": passed, "detail": detail})

    # 1. File exists
    if not ALIGNED_PATH.exists():
        add_check("file_exists", False, f"File not found: {ALIGNED_PATH}")
        return checks

    add_check("file_exists", True, str(ALIGNED_PATH))

    df = pd.read_parquet(ALIGNED_PATH)

    # 2. Required columns
    missing_cols = REQUIRED_COLUMNS - set(df.columns)
    add_check("required_columns", len(missing_cols) == 0,
              f"Missing: {missing_cols}" if missing_cols else "All present")

    if missing_cols:
        return checks

    # 3. UTC-aware datetime
    ts_is_utc = hasattr(df["timestamp"].dtype, "tz") and str(df["timestamp"].dtype.tz) == "UTC"
    cap_ts_is_utc = hasattr(df["cap_source_timestamp"].dtype, "tz") and str(df["cap_source_timestamp"].dtype.tz) == "UTC"
    add_check("timestamp_utc_aware", ts_is_utc, str(df["timestamp"].dtype))
    add_check("cap_source_timestamp_utc_aware", cap_ts_is_utc, str(df["cap_source_timestamp"].dtype))

    # 4. No duplicate keys
    n_dupes = df.duplicated(subset=["timestamp", "symbol"]).sum()
    add_check("no_duplicate_keys", n_dupes == 0, f"{n_dupes} duplicates" if n_dupes else "None")

    # 5. cap > 0 or NaN
    cap_valid = df["cap"]
    bad_cap = cap_valid.notna() & (cap_valid <= 0)
    add_check("cap_positive_or_nan", bad_cap.sum() == 0,
              f"{bad_cap.sum()} rows with cap <= 0" if bad_cap.any() else "All valid")

    # 6. No forward-looking leakage
    has_ts = df["cap_source_timestamp"].notna()
    cap_ts = pd.to_datetime(df["cap_source_timestamp"], utc=True)
    bar_ts = pd.to_datetime(df["timestamp"], utc=True)
    leakage = has_ts & (cap_ts > bar_ts)
    add_check("no_forward_looking_leakage", leakage.sum() == 0,
              f"{leakage.sum()} violations" if leakage.any() else "None")

    # 7. Coverage
    overall_coverage = df["cap"].notna().mean()
    per_symbol = df.groupby("symbol")["cap"].apply(lambda x: x.notna().mean())
    n_above_90 = (per_symbol >= 0.9).sum()
    n_below_80 = (per_symbol < 0.8).sum()
    add_check("overall_coverage", overall_coverage >= 0.90,
              f"{overall_coverage:.1%} ({'PASS' if overall_coverage >= 0.90 else 'FAIL'})")
    add_check("symbol_coverage_summary", True,
              f"{n_above_90} symbols >= 90%, {n_below_80} symbols < 80%")

    return checks


def main():
    print("Checking market cap data contract ...")
    checks = check_contract()

    all_passed = all(c["passed"] for c in checks)

    # Print results
    for c in checks:
        status = "✅" if c["passed"] else "❌"
        print(f"  {status} {c['check']}: {c['detail']}")

    print(f"\nOverall: {'PASS' if all_passed else 'FAIL'}")

    # Save JSON
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "overall_pass": all_passed,
        "checks": checks,
    }
    out_json = CAP_DIR / "market_cap_contract_check.json"
    with open(out_json, "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"Saved: {out_json}")

    # Save CSV
    out_csv = CAP_DIR / "market_cap_contract_check.csv"
    pd.DataFrame(checks).to_csv(out_csv, index=False)
    print(f"Saved: {out_csv}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
