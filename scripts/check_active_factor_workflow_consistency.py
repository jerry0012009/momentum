#!/usr/bin/env python3
"""Active Factor Workflow Consistency Checker — PM-53B.

Verifies that every active factor (from factor_library_state.json) appears
in ALL required downstream diagnostic outputs. This catches the failure mode
where a factor is registered and visible on the page but missing diagnostics
like shape, decile, or capacity.

Required outputs checked:
  1. factor_library_state.json registered_factor_ids (source of truth)
  2. factor_level_rankic_summary.csv
  3. factor_level_long_short_summary.csv
  4. factor_diagnostics_summary.csv
  5. factor_quantile_shape_summary.csv
  6. factor_rolling_stability_summary.csv
  7. factor_decile_shape_summary.csv
  8. factor_capacity_liquidity_summary.csv
  9. factor_quality_scorecard.csv
  10. factor_redundancy_summary.csv
  11. factor_regime_exposure_summary.csv
  12. factor_unified_profile_summary.csv
  13. factor_bilingual_cards.csv
  14. factor-evaluation.html payload factor count

Outputs:
  - Active factor count per table
  - Missing factor IDs by table
  - Extra factor IDs by table (not in active list)
  - PASS/FAIL verdict (exit code 0 = PASS, non-zero = FAIL)

Usage:
    python scripts/check_active_factor_workflow_consistency.py

NOT production. Research diagnostics only.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"
DIAG_DIR = BASE / "factor_diagnostics"
EVAL_DIR = BASE / "factor_level_evaluation"
META_DIR = BASE / "factor_metadata"
STATE_PATH = BASE / "factor_library_state.json"
HTML_PATH = ROOT / "reports" / "site" / "factor-library" / "factor-evaluation.html"

# ── Table definitions ──────────────────────────────────────────────────────
# (check_id, description, csv_path, key_column)
REQUIRED_TABLES = [
    ("rankic", "factor_level_rankic_summary.csv",
     EVAL_DIR / "factor_level_rankic_summary.csv", "factor_name"),
    ("long_short", "factor_level_long_short_summary.csv",
     EVAL_DIR / "factor_level_long_short_summary.csv", "factor_name"),
    ("diagnostics_summary", "factor_diagnostics_summary.csv",
     DIAG_DIR / "factor_diagnostics_summary.csv", "factor_id"),
    ("shape", "factor_quantile_shape_summary.csv",
     DIAG_DIR / "factor_quantile_shape_summary.csv", "factor_id"),
    ("rolling_stability", "factor_rolling_stability_summary.csv",
     DIAG_DIR / "factor_rolling_stability_summary.csv", "factor_id"),
    ("decile", "factor_decile_shape_summary.csv",
     DIAG_DIR / "factor_decile_shape_summary.csv", "factor_id"),
    ("capacity", "factor_capacity_liquidity_summary.csv",
     DIAG_DIR / "factor_capacity_liquidity_summary.csv", "factor_id"),
    ("scorecard", "factor_quality_scorecard.csv",
     DIAG_DIR / "factor_quality_scorecard.csv", "factor_id"),
    ("redundancy_summary", "factor_redundancy_summary.csv",
     DIAG_DIR / "factor_redundancy_summary.csv", "factor_id"),
    ("regime_exposure", "factor_regime_exposure_summary.csv",
     DIAG_DIR / "factor_regime_exposure_summary.csv", "factor_id"),
    ("profile", "factor_unified_profile_summary.csv",
     DIAG_DIR / "factor_unified_profile_summary.csv", "factor_id"),
    ("bilingual_cards", "factor_bilingual_cards.csv",
     META_DIR / "factor_bilingual_cards.csv", "factor_id"),
]


def load_active_factors() -> list[str]:
    """Load active factor IDs from state JSON."""
    if not STATE_PATH.exists():
        print(f"ERROR: {STATE_PATH} not found")
        sys.exit(2)
    state = json.loads(STATE_PATH.read_text())
    fids = state.get("registered_factor_ids", [])
    if not fids:
        print("ERROR: No registered_factor_ids in state")
        sys.exit(2)
    return sorted(fids)


def check_csv_table(active_set: set[str], path: Path, key_col: str) -> dict:
    """Check a CSV table for factor coverage.

    Returns dict with keys: status, count, missing, extra, error.
    """
    if not path.exists():
        return {
            "status": "MISSING_FILE",
            "count": 0,
            "missing": sorted(active_set),
            "extra": [],
            "error": f"File not found: {path}",
        }
    try:
        # Read just the key column for efficiency
        ids_in_file = set()
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if key_col not in (reader.fieldnames or []):
                # Try alternate key
                alt = "factor_id" if "factor_name" not in (reader.fieldnames or []) else "factor_name"
                if alt not in (reader.fieldnames or []):
                    return {
                        "status": "ERROR",
                        "count": 0,
                        "missing": sorted(active_set),
                        "extra": [],
                        "error": f"Neither '{key_col}' nor '{alt}' found in {path.name}",
                    }
                key_col = alt
            for row in reader:
                val = row.get(key_col, "").strip()
                if val:
                    ids_in_file.add(val)

        missing = sorted(active_set - ids_in_file)
        extra = sorted(ids_in_file - active_set)
        status = "PASS" if not missing else "FAIL"
        return {
            "status": status,
            "count": len(ids_in_file),
            "missing": missing,
            "extra": extra,
            "error": None,
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "count": 0,
            "missing": sorted(active_set),
            "extra": [],
            "error": str(e),
        }


def check_html_payload(active_set: set[str]) -> dict:
    """Check factor-evaluation.html payload for factor count."""
    if not HTML_PATH.exists():
        return {
            "status": "MISSING_FILE",
            "count": 0,
            "missing": sorted(active_set),
            "extra": [],
            "error": f"File not found: {HTML_PATH}",
        }
    try:
        text = HTML_PATH.read_text(encoding="utf-8", errors="replace")
        m = re.search(
            r'<script id="factorPayload" type="application/json">(.*?)</script>',
            text, re.DOTALL,
        )
        if not m:
            return {
                "status": "ERROR",
                "count": 0,
                "missing": sorted(active_set),
                "extra": [],
                "error": "factorPayload script tag not found in HTML",
            }
        data = json.loads(m.group(1))
        factors = data.get("factors", [])
        ids_in_html = {f.get("factor_id", "") for f in factors if f.get("factor_id")}
        missing = sorted(active_set - ids_in_html)
        extra = sorted(ids_in_html - active_set)
        status = "PASS" if not missing else "FAIL"
        return {
            "status": status,
            "count": len(ids_in_html),
            "missing": missing,
            "extra": extra,
            "error": None,
        }
    except json.JSONDecodeError as e:
        return {
            "status": "ERROR",
            "count": 0,
            "missing": sorted(active_set),
            "extra": [],
            "error": f"JSON parse error: {e}",
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "count": 0,
            "missing": sorted(active_set),
            "extra": [],
            "error": str(e),
        }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Active Factor Workflow Consistency Checker — PM-53B",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.parse_args()

    active = load_active_factors()
    active_set = set(active)
    n_active = len(active)

    print("=" * 72)
    print("Active Factor Workflow Consistency Check — PM-53B")
    print("=" * 72)
    print(f"  Active factor count: {n_active}")
    print(f"  Source: {STATE_PATH}")
    print()

    all_results = []
    any_fail = False

    # Check CSV tables
    for check_id, desc, path, key_col in REQUIRED_TABLES:
        result = check_csv_table(active_set, path, key_col)
        result["check_id"] = check_id
        result["description"] = desc
        all_results.append(result)

        icon = "✓" if result["status"] == "PASS" else "✗"
        count_str = f"{result['count']}/{n_active}"
        print(f"  {icon} [{check_id:25s}] {count_str}  {result['status']}")
        if result["missing"]:
            print(f"    missing: {', '.join(result['missing'][:10])}")
            if len(result["missing"]) > 10:
                print(f"    ... and {len(result['missing']) - 10} more")
        if result["extra"]:
            print(f"    extra:   {', '.join(result['extra'][:5])}")
        if result["error"]:
            print(f"    error:   {result['error']}")
        if result["status"] != "PASS":
            any_fail = True

    # Check HTML payload
    html_result = check_html_payload(active_set)
    html_result["check_id"] = "html_payload"
    html_result["description"] = "factor-evaluation.html payload"
    all_results.append(html_result)

    icon = "✓" if html_result["status"] == "PASS" else "✗"
    print(f"  {icon} [{'html_payload':25s}] {html_result['count']}/{n_active}  {html_result['status']}")
    if html_result["missing"]:
        print(f"    missing: {', '.join(html_result['missing'][:10])}")
    if html_result["error"]:
        print(f"    error:   {html_result['error']}")
    if html_result["status"] != "PASS":
        any_fail = True

    # ── PM-56A: Robust diagnostics (full-universe required) ────────────────
    print()
    print("  --- Robust Diagnostics (PM-54/56) ---")

    robust_full_tables = [
        ("rankic_robust", "RankIC robust significance",
         DIAG_DIR / "factor_rankic_robust_significance_summary.csv", "factor_id"),
        ("ls_robust", "LS robust significance",
         DIAG_DIR / "factor_ls_robust_significance_summary.csv", "factor_id"),
    ]

    for check_id, desc, path, key_col in robust_full_tables:
        result = check_csv_table(active_set, path, key_col)
        result["check_id"] = check_id
        result["description"] = desc
        all_results.append(result)

        # Also check horizon coverage: expect 4 horizons per factor
        horizon_ok = False
        if path.exists() and result["status"] == "PASS":
            try:
                import pandas as _pd
                rdf = _pd.read_csv(path)
                hz_col = "horizon"
                if hz_col in rdf.columns:
                    fid_col = key_col if key_col in rdf.columns else "factor_id"
                    n_horizons = rdf[hz_col].nunique()
                    # Check each active factor has 4 horizons
                    fid_hz = rdf.groupby(fid_col)[hz_col].nunique()
                    missing_hz = {fid: 4 - cnt for fid, cnt in fid_hz.items()
                                  if fid in active_set and cnt < 4}
                    horizon_ok = n_horizons == 4 and not missing_hz
                    result["horizon_count"] = int(n_horizons)
                    result["horizon_ok"] = horizon_ok
                    if not horizon_ok:
                        result["status"] = "FAIL"
                        any_fail = True
            except Exception:
                pass

        icon = "✓" if result["status"] == "PASS" else "✗"
        hz_str = f" (4 horizons ✓)" if horizon_ok else ""
        print(f"  {icon} [{check_id:25s}] {result['count']}/{n_active}  {result['status']}{hz_str}")
        if result["missing"]:
            print(f"    missing: {', '.join(result['missing'][:10])}")
        if result["error"]:
            print(f"    error:   {result['error']}")
        if result["status"] != "PASS":
            any_fail = True

    # PM-58A: LS monthly aggregate field completeness
    print()
    print("  --- LS Monthly Aggregate Fields (PM-58A) ---")
    import pandas as _pd
    ls_path = EVAL_DIR / "factor_level_long_short_summary.csv"
    ls_required_fields = [
        "long_short_spread_std", "long_short_spread_annualized_return",
        "long_short_spread_annualized_vol", "long_short_spread_max_drawdown",
        "long_short_spread_positive_period_rate", "n_monthly_periods",
    ]
    if ls_path.exists():
        lsdf = _pd.read_csv(ls_path)
        ls_active = lsdf[lsdf["factor_name"].isin(active_set)]
        n_ls_rows = len(ls_active)
        n_expected = n_active * 4
        ls_result = {
            "check_id": "ls_monthly_aggregate",
            "description": "LS monthly aggregate fields (PM-58A)",
            "count": n_ls_rows,
            "expected": n_expected,
            "status": "PASS",
            "missing_fields": [],
            "error": "",
        }
        if n_ls_rows < n_expected:
            ls_result["status"] = "FAIL"
            ls_result["error"] = f"Expected {n_expected} rows, found {n_ls_rows}"
        for fld in ls_required_fields:
            n_null = ls_active[fld].isna().sum()
            if n_null > 0:
                ls_result["status"] = "FAIL"
                ls_result["missing_fields"].append(f"{fld}: {n_null} null")
        # Check n_monthly_periods >= 2
        if "n_monthly_periods" in ls_active.columns:
            low = (ls_active["n_monthly_periods"] < 2).sum()
            if low > 0:
                ls_result["status"] = "FAIL"
                ls_result["missing_fields"].append(f"n_monthly_periods < 2: {low} rows")
        all_results.append(ls_result)
        icon = "✓" if ls_result["status"] == "PASS" else "✗"
        print(f"  {icon} [{'ls_monthly_aggregate':25s}] {n_ls_rows}/{n_expected}  {ls_result['status']}")
        if ls_result["missing_fields"]:
            for mf in ls_result["missing_fields"]:
                print(f"    {mf}")
        if ls_result["status"] != "PASS":
            any_fail = True
    else:
        print(f"  ✗ [{'ls_monthly_aggregate':25s}] FILE MISSING")
        any_fail = True

    # Documented subset outputs (informational, not full-universe required)
    robust_subset_tables = [
        ("paper_robust", "Paper robust significance (subset: 5 factors)",
         DIAG_DIR / "factor_paper_robust_significance_summary.csv", "factor_id"),
        ("fee_robust", "Fee cost-collapse diagnostics (subset: 13 factors)",
         DIAG_DIR / "factor_fee_robust_significance_summary.csv", "factor_id"),
    ]

    print()
    print("  --- Documented Subset Outputs (informational) ---")
    for check_id, desc, path, key_col in robust_subset_tables:
        if not path.exists():
            print(f"  ⚠ [{check_id:25s}] FILE MISSING — {desc}")
            continue
        try:
            import pandas as _pd
            sdf = _pd.read_csv(path)
            n_rows = len(sdf)
            n_factors = sdf[key_col].nunique() if key_col in sdf.columns else 0
            print(f"  ✓ [{check_id:25s}] {n_factors} factors, {n_rows} rows  (documented subset)")
        except Exception as e:
            print(f"  ⚠ [{check_id:25s}] ERROR — {e}")

    # Summary
    n_pass = sum(1 for r in all_results if r["status"] == "PASS")
    n_fail = sum(1 for r in all_results if r["status"] != "PASS")
    verdict = "PASS" if not any_fail else "FAIL"

    print()
    print("-" * 72)
    print(f"  Tables checked: {len(all_results)}")
    print(f"  PASS: {n_pass}  |  FAIL: {n_fail}")
    print(f"  Verdict: {verdict}")
    print("-" * 72)

    # Write JSON report
    report = {
        "active_factor_count": n_active,
        "tables_checked": len(all_results),
        "pass_count": n_pass,
        "fail_count": n_fail,
        "verdict": verdict,
        "tables": all_results,
    }
    out_path = DIAG_DIR / "active_workflow_consistency_report.json"
    DIAG_DIR.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, default=str))
    print(f"\n  Report: {out_path}")

    return 0 if not any_fail else 1


if __name__ == "__main__":
    sys.exit(main())
