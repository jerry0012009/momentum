#!/usr/bin/env python3
"""Factor Library Staleness Monitor — PM-25.

Reusable (no hardcoded factor counts) staleness checker for the factor library.
Reads expected factor count from factor_library_state.json, falls back to
factor_formula_registry.py. Checks coverage, pairwise redundancy, timestamp
staleness, and page content.

Outputs:
  - factor_library_staleness_report.csv
  - factor_library_staleness_report.json

Usage:
  python scripts/check_factor_library_staleness.py [--json] [--strict]

NOT production. NOT live trading. Research diagnostics only.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
STATE_PATH = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_library_state.json"
REGISTRY_PATH = SCRIPTS / "factor_formula_registry.py"
DIAG_DIR = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_diagnostics"
PAGE_PATH = ROOT / "reports" / "site" / "factor-library" / "factor-evaluation.html"
REPORT_CSV_PATH = DIAG_DIR / "factor_library_staleness_report.csv"
REPORT_JSON_PATH = DIAG_DIR / "factor_library_staleness_report.json"

# ── Expected factor count resolution ────────────────────────────────────────

def _count_from_state() -> tuple[int | None, str]:
    """Read expected count from factor_library_state.json."""
    if not STATE_PATH.exists():
        return None, "state_file_missing"
    try:
        with open(STATE_PATH) as f:
            state = json.load(f)
        count = state.get("registered_factors") or len(state.get("registered_factor_ids", []))
        if count and count > 0:
            return count, "factor_library_state.json"
    except Exception:
        pass
    return None, "state_file_unreadable"


def _count_from_registry() -> tuple[int | None, str]:
    """Count FactorSpec entries in factor_formula_registry.py via regex."""
    if not REGISTRY_PATH.exists():
        return None, "registry_file_missing"
    try:
        text = REGISTRY_PATH.read_text()
        matches = re.findall(r'FactorSpec\(\s*factor_id="([^"]+)"', text)
        if matches:
            return len(matches), "factor_formula_registry.py"
    except Exception:
        pass
    return None, "registry_file_unreadable"


def resolve_expected_factor_count() -> tuple[int, str]:
    """Resolve expected factor count, preferring state over registry."""
    count, source = _count_from_state()
    if count is not None:
        return count, source
    count, source = _count_from_registry()
    if count is not None:
        return count, source
    print("ERROR: Cannot determine expected factor count from state or registry.", file=sys.stderr)
    sys.exit(1)


# ── Check definitions ───────────────────────────────────────────────────────

def _file_mtime(path: Path) -> float | None:
    """Return mtime of file, or None if missing."""
    try:
        return os.path.getmtime(path)
    except OSError:
        return None


def _count_csv_rows(path: Path, has_header: bool = True) -> int | None:
    """Count data rows in a CSV file."""
    if not path.exists():
        return None
    try:
        with open(path) as f:
            n = sum(1 for _ in f)
        return n - 1 if has_header and n > 0 else n
    except Exception:
        return None


def _count_unique_factor_ids_in_csv(path: Path, col: str = "factor_id") -> int | None:
    """Count unique factor_ids in a CSV file. Tries col, then 'factor_name'."""
    if not path.exists():
        return None
    try:
        import pandas as pd
        df = pd.read_csv(path, nrows=0)
        actual_col = col if col in df.columns else ("factor_name" if "factor_name" in df.columns else None)
        if actual_col is None:
            return None
        df = pd.read_csv(path, usecols=[actual_col])
        return df[actual_col].nunique()
    except Exception:
        return None


def _json_has_keys(path: Path, keys: list[str]) -> tuple[bool, list[str]]:
    """Check if a JSON file contains specific top-level keys."""
    if not path.exists():
        return False, keys
    try:
        with open(path) as f:
            data = json.load(f)
        missing = [k for k in keys if k not in data]
        return len(missing) == 0, missing
    except Exception:
        return False, keys


def run_checks(expected_n: int, source: str, strict: bool) -> list[dict]:
    """Run all staleness checks and return a list of check dicts."""
    checks: list[dict] = []
    expected_pair_count = expected_n * (expected_n - 1) // 2

    def _add(check_id, check_group, status, severity, artifact_path,
             expected=None, actual=None, message="", recommended_stage="", recommended_command=""):
        checks.append({
            "check_id": check_id,
            "check_group": check_group,
            "status": status,
            "severity": severity,
            "artifact_path": str(artifact_path),
            "expected": expected,
            "actual": actual,
            "message": message,
            "recommended_stage": recommended_stage,
            "recommended_command": recommended_command,
        })

    # ── Group 1: Coverage checks (row/factor-count vs expected_n) ────────
    EVAL_DIR = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_level_evaluation"
    METADATA_DIR = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_metadata"

    coverage_artifacts = [
        ("coverage_diagnostics_summary", DIAG_DIR / "factor_diagnostics_summary.csv", "diagnostics"),
        ("coverage_scorecard", DIAG_DIR / "factor_quality_scorecard.csv", "scorecard"),
        ("coverage_bilingual_cards", METADATA_DIR / "factor_bilingual_cards.csv", "metadata"),
        ("coverage_candidate_review", EVAL_DIR / "factor_level_candidate_review.csv", "evaluate"),
        ("coverage_monthly_ic", DIAG_DIR / "factor_monthly_ic_series.csv", "diagnostics"),
        ("coverage_monthly_ls", DIAG_DIR / "factor_monthly_long_short_series.csv", "diagnostics"),
        ("coverage_cumulative_ls", DIAG_DIR / "factor_cumulative_long_short_curve.csv", "diagnostics"),
        ("coverage_paper_summary", DIAG_DIR / "single_factor_paper_summary.csv", "paper-diagnostics"),
        ("coverage_state", STATE_PATH, "state"),
        # Profile / workflow output files (PM-32)
        ("coverage_workflow_contract", DIAG_DIR / "factor_evaluation_workflow_contract.json", "profile"),
        ("coverage_evidence_matrix_csv", DIAG_DIR / "factor_evaluation_evidence_matrix.csv", "profile"),
        ("coverage_evidence_matrix_json", DIAG_DIR / "factor_evaluation_evidence_matrix.json", "profile"),
        ("coverage_unified_profile_csv", DIAG_DIR / "factor_unified_profile_summary.csv", "profile"),
        ("coverage_unified_profile_json", DIAG_DIR / "factor_unified_profile_summary.json", "profile"),
        ("coverage_profile_component_scores", DIAG_DIR / "factor_profile_component_scores.csv", "profile"),
        ("coverage_profile_payload", DIAG_DIR / "factor_profile_payload.json", "profile"),
        ("coverage_profile_manifest", DIAG_DIR / "factor_profile_manifest.json", "profile"),
    ]

    for check_id, path, stage in coverage_artifacts:
        if not path.exists():
            _add(check_id, "coverage", "FAIL", "HIGH", path,
                 expected=expected_n, actual="MISSING",
                 message=f"File missing: {path.name}",
                 recommended_stage=stage,
                 recommended_command=f"python scripts/run_factor_library_refresh.py --stage {stage}")
            continue

        suffix = path.suffix
        if suffix == ".csv":
            unique = _count_unique_factor_ids_in_csv(path)
            if unique is None:
                _add(check_id, "coverage", "FAIL", "MEDIUM", path,
                     expected=expected_n, actual="UNREADABLE",
                     message=f"Cannot read factor_id column from {path.name}",
                     recommended_stage=stage,
                     recommended_command=f"python scripts/run_factor_library_refresh.py --stage {stage}")
            elif unique < expected_n:
                severity = "HIGH" if unique < expected_n * 0.5 else "MEDIUM"
                _add(check_id, "coverage", "FAIL", severity, path,
                     expected=expected_n, actual=unique,
                     message=f"Only {unique}/{expected_n} factors in {path.name}",
                     recommended_stage=stage,
                     recommended_command=f"python scripts/run_factor_library_refresh.py --stage {stage}")
            elif unique > expected_n:
                _add(check_id, "coverage", "WARN", "LOW", path,
                     expected=expected_n, actual=unique,
                     message=f"More factors ({unique}) than expected ({expected_n}) in {path.name} — registry may have changed",
                     recommended_stage=stage,
                     recommended_command=f"python scripts/run_factor_library_refresh.py --stage {stage}")
            else:
                _add(check_id, "coverage", "PASS", "INFO", path,
                     expected=expected_n, actual=unique,
                     message=f"All {expected_n} factors present in {path.name}")
        elif suffix == ".json":
            # For state JSON, check registered_factors field
            try:
                with open(path) as f:
                    data = json.load(f)
                reg_count = data.get("registered_factors", 0)
                if reg_count == expected_n:
                    _add(check_id, "coverage", "PASS", "INFO", path,
                         expected=expected_n, actual=reg_count,
                         message=f"State JSON registered_factors matches expected ({expected_n})")
                else:
                    _add(check_id, "coverage", "WARN", "MEDIUM", path,
                         expected=expected_n, actual=reg_count,
                         message=f"State registered_factors ({reg_count}) differs from expected ({expected_n})",
                         recommended_stage="state",
                         recommended_command="python scripts/run_factor_library_refresh.py --stage state")
            except Exception as e:
                _add(check_id, "coverage", "FAIL", "MEDIUM", path,
                     expected=expected_n, actual="UNREADABLE",
                     message=f"Cannot read state JSON: {e}",
                     recommended_stage="state",
                     recommended_command="python scripts/run_factor_library_refresh.py --stage state")

    # ── Group 2: Pairwise redundancy row count ───────────────────────────
    redundancy_path = DIAG_DIR / "factor_pairwise_redundancy.csv"
    pair_row_count = _count_csv_rows(redundancy_path)
    if pair_row_count is None:
        _add("redundancy_row_count", "redundancy", "FAIL", "HIGH", redundancy_path,
             expected=expected_pair_count, actual="MISSING",
             message="Pairwise redundancy CSV missing",
             recommended_stage="redundancy",
             recommended_command="python scripts/run_factor_library_refresh.py --stage redundancy --expensive-ok")
    elif pair_row_count == expected_pair_count:
        _add("redundancy_row_count", "redundancy", "PASS", "INFO", redundancy_path,
             expected=expected_pair_count, actual=pair_row_count,
             message=f"Pairwise redundancy has {pair_row_count} rows (matches n*(n-1)/2)")
    else:
        severity = "HIGH" if pair_row_count < expected_pair_count * 0.5 else "MEDIUM"
        _add("redundancy_row_count", "redundancy", "FAIL" if pair_row_count < expected_pair_count else "WARN",
             severity, redundancy_path,
             expected=expected_pair_count, actual=pair_row_count,
             message=f"Pairwise redundancy has {pair_row_count} rows, expected {expected_pair_count}",
             recommended_stage="redundancy",
             recommended_command="python scripts/run_factor_library_refresh.py --stage redundancy --expensive-ok")

    # ── Group 3: Timestamp staleness (mtime dependency chain) ────────────
    state_mtime = _file_mtime(STATE_PATH)
    upstream_paths = [
        ("mtime_diagnostics_summary", DIAG_DIR / "factor_diagnostics_summary.csv", "diagnostics"),
        ("mtime_scorecard", DIAG_DIR / "factor_quality_scorecard.csv", "scorecard"),
        ("mtime_redundancy", DIAG_DIR / "factor_pairwise_redundancy.csv", "redundancy"),
        ("mtime_monthly_ic", DIAG_DIR / "factor_monthly_ic_series.csv", "diagnostics"),
    ]
    for check_id, path, stage in upstream_paths:
        mtime = _file_mtime(path)
        if mtime is None:
            _add(check_id, "staleness", "SKIP", "INFO", path,
                 message=f"File missing — cannot check staleness")
            continue
        if state_mtime is not None and mtime > state_mtime:
            _add(check_id, "staleness", "WARN", "LOW", path,
                 expected="mtime <= state mtime", actual=f"mtime={mtime:.0f} > state={state_mtime:.0f}",
                 message=f"{path.name} is newer than state — state may be stale",
                 recommended_stage="state",
                 recommended_command="python scripts/run_factor_library_refresh.py --stage state")
        else:
            _add(check_id, "staleness", "PASS", "INFO", path,
                 message=f"{path.name} mtime is consistent with state")

    # Check page mtime vs diagnostics
    page_mtime = _file_mtime(PAGE_PATH)
    diag_mtime = _file_mtime(DIAG_DIR / "factor_diagnostics_summary.csv")
    if page_mtime is None:
        _add("mtime_page", "staleness", "FAIL", "MEDIUM", PAGE_PATH,
             message="Page file missing",
             recommended_stage="page",
             recommended_command="python scripts/run_factor_library_refresh.py --stage page")
    elif diag_mtime is not None and diag_mtime > page_mtime:
        _add("mtime_page", "staleness", "WARN", "LOW", PAGE_PATH,
             expected="page mtime >= diagnostics mtime",
             actual=f"page={page_mtime:.0f} < diag={diag_mtime:.0f}",
             message="Page is older than diagnostics — page may be stale",
             recommended_stage="page",
             recommended_command="python scripts/run_factor_library_refresh.py --stage page")
    else:
        _add("mtime_page", "staleness", "PASS", "INFO", PAGE_PATH,
             message="Page mtime is consistent with diagnostics")

    # ── Group 4: Page content soft checks ────────────────────────────────
    if not PAGE_PATH.exists():
        _add("page_content", "page", "FAIL", "HIGH", PAGE_PATH,
             message="Page file missing",
             recommended_stage="page",
             recommended_command="python scripts/run_factor_library_refresh.py --stage page")
    else:
        try:
            html = PAGE_PATH.read_text().lower()
        except Exception:
            html = ""

        sections = [
            ("diagnostics", "diagnostics"),
            ("redundancy", "redundancy"),
            ("quality", "quality"),
            ("scorecard", "scorecard"),
            ("regime", "regime"),
        ]
        for keyword, stage in sections:
            if keyword in html:
                _add(f"page_has_{keyword}", "page", "PASS", "INFO", PAGE_PATH,
                     message=f"Page contains '{keyword}' section")
            else:
                _add(f"page_has_{keyword}", "page", "WARN", "LOW", PAGE_PATH,
                     message=f"Page missing '{keyword}' section",
                     recommended_stage=stage,
                     recommended_command=f"python scripts/run_factor_library_refresh.py --stage {stage}")

    return checks


# ── Report generation ────────────────────────────────────────────────────────

def compute_summary(checks: list[dict]) -> str:
    """Compute summary status from checks."""
    has_fail = any(c["status"] == "FAIL" for c in checks)
    has_warn = any(c["status"] == "WARN" for c in checks)
    if has_fail:
        return "STALENESS_FAIL"
    if has_warn:
        return "STALENESS_PASS_WITH_WARNINGS"
    return "STALENESS_PASS"


def collect_recommended_commands(checks: list[dict]) -> list[str]:
    """Collect unique recommended commands from failing/warning checks."""
    seen = set()
    cmds = []
    for c in checks:
        if c["status"] in ("FAIL", "WARN") and c["recommended_command"]:
            if c["recommended_command"] not in seen:
                seen.add(c["recommended_command"])
                cmds.append(c["recommended_command"])
    return cmds


def write_csv(checks: list[dict], path: Path) -> None:
    """Write checks to CSV."""
    cols = ["check_id", "check_group", "status", "severity", "artifact_path",
            "expected", "actual", "message", "recommended_stage", "recommended_command"]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        writer.writeheader()
        for c in checks:
            row = {k: c.get(k, "") for k in cols}
            writer.writerow(row)


def write_json(checks: list[dict], expected_n: int, source: str, path: Path) -> None:
    """Write full JSON report."""
    counts = {"PASS": 0, "WARN": 0, "FAIL": 0, "SKIP": 0}
    for c in checks:
        counts[c["status"]] = counts.get(c["status"], 0) + 1

    report = {
        "summary_status": compute_summary(checks),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "expected_factor_count": expected_n,
        "expected_pair_count": expected_n * (expected_n - 1) // 2,
        "source_of_expected_count": source,
        "n_pass": counts["PASS"],
        "n_warn": counts["WARN"],
        "n_fail": counts["FAIL"],
        "n_skip": counts["SKIP"],
        "recommended_next_commands": collect_recommended_commands(checks),
        "checks": checks,
    }
    with open(path, "w") as f:
        json.dump(report, f, indent=2, default=str)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Factor Library Staleness Monitor — PM-25",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--json", action="store_true",
                        help="Also print JSON report to stdout")
    parser.add_argument("--strict", action="store_true",
                        help="Treat warnings as failures (exit non-zero on WARN)")
    args = parser.parse_args()

    expected_n, source = resolve_expected_factor_count()
    print(f"Expected factor count: {expected_n} (source: {source})")
    print(f"Expected pair count:   {expected_n * (expected_n - 1) // 2}")

    checks = run_checks(expected_n, source, args.strict)
    summary = compute_summary(checks)

    # Write reports
    DIAG_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(checks, REPORT_CSV_PATH)
    write_json(checks, expected_n, source, REPORT_JSON_PATH)

    # Console output
    counts = {"PASS": 0, "WARN": 0, "FAIL": 0, "SKIP": 0}
    for c in checks:
        counts[c["status"]] = counts.get(c["status"], 0) + 1

    print(f"\n{'='*60}")
    print(f"Staleness Report: {summary}")
    print(f"  PASS: {counts['PASS']}  WARN: {counts['WARN']}  FAIL: {counts['FAIL']}  SKIP: {counts['SKIP']}")
    print(f"  Reports: {REPORT_CSV_PATH}")
    print(f"           {REPORT_JSON_PATH}")
    print(f"{'='*60}")

    # Print failures/warnings
    for c in checks:
        if c["status"] in ("FAIL", "WARN"):
            print(f"  [{c['status']}] {c['check_id']}: {c['message']}")
            if c["recommended_command"]:
                print(f"         → {c['recommended_command']}")

    # Print recommended next commands
    cmds = collect_recommended_commands(checks)
    if cmds:
        print(f"\nRecommended next commands:")
        for cmd in cmds:
            print(f"  {cmd}")

    if args.json:
        print("\n" + json.dumps({
            "summary_status": summary,
            "expected_factor_count": expected_n,
            "source_of_expected_count": source,
            "n_pass": counts["PASS"],
            "n_warn": counts["WARN"],
            "n_fail": counts["FAIL"],
            "n_skip": counts["SKIP"],
            "recommended_next_commands": cmds,
        }, indent=2))

    if summary == "STALENESS_FAIL":
        return 1
    if args.strict and summary == "STALENESS_PASS_WITH_WARNINGS":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
