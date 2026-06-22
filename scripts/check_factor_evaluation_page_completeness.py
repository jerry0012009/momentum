#!/usr/bin/env python3
"""Factor Evaluation Page Completeness QA — checks that the HTML page is complete.

Verifies file existence/size, factor coverage from the unified profile CSV,
PM-35 new factor presence, and section markers for all required diagnostics
and disclaimers.

Outputs:
  research/factor_runs/crypto_top50_factor_library/factor_diagnostics/
    factor_evaluation_page_completeness_report.csv
    factor_evaluation_page_completeness_report.json

Usage:
  python scripts/check_factor_evaluation_page_completeness.py

NOT production. NOT live trading. Research diagnostics only.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "reports" / "site" / "factor-library" / "factor-evaluation.html"
PROFILE_CSV = (
    ROOT
    / "research"
    / "factor_runs"
    / "crypto_top50_factor_library"
    / "factor_diagnostics"
    / "factor_unified_profile_summary.csv"
)
OUTPUT_DIR = (
    ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_diagnostics"
)
REPORT_CSV = OUTPUT_DIR / "factor_evaluation_page_completeness_report.csv"
REPORT_JSON = OUTPUT_DIR / "factor_evaluation_page_completeness_report.json"

PM35_NEW_FACTORS = [
    "rev_2h",
    "mom_vol_adjusted_20h",
    "range_breakout_vol_confirm_20h",
    "volume_pressure_20h",
    "xs_rank_mom_accel",
]

MAX_SIZE_BYTES = 4.5 * 1024 * 1024  # 4.5 MB

# ── Section markers ──────────────────────────────────────────────────────────
# Each entry: (check_id, check_name, list_of_alternative_phrases)
SECTION_CHECKS = [
    (
        "section_unified_workflow",
        "Unified Factor Evaluation Workflow / Unified Factor Profile",
        ["Unified Factor Evaluation Workflow", "Unified Factor Profile"],
    ),
    (
        "section_evidence_status",
        "evidence_status",
        ["evidence_status"],
    ),
    (
        "section_workflow_ready_status",
        "workflow_ready_status",
        ["workflow_ready_status"],
    ),
    (
        "section_source_artifacts",
        "Source Artifacts",
        ["source_artifacts", "Source Artifacts"],
    ),
    (
        "section_paper_portfolio",
        "Single-Factor Paper Portfolio / Paper Portfolio",
        ["Single-Factor Paper Portfolio", "Paper Portfolio"],
    ),
    (
        "section_regime",
        "Regime diagnostics",
        ["Regime"],
    ),
    (
        "section_quantile_shape",
        "Quantile Shape / Shape",
        ["Quantile Shape", "Shape"],
    ),
    (
        "section_decile",
        "Decile (direction-aware)",
        ["Decile"],
    ),
    (
        "section_capacity_liquidity",
        "Capacity / Liquidity",
        ["Capacity", "Liquidity"],
    ),
    (
        "section_redundancy",
        "Redundancy",
        ["Redundancy", "redundancy"],
    ),
    (
        "section_marginal",
        "Marginal",
        ["Marginal", "marginal"],
    ),
    (
        "section_disclaimer",
        "Disclaimer text",
        ["Not production", "not production", "NOT production", "not live", "NOT live",
         "not tradeable", "NOT tradeable", "NOT live trading", "not live trading",
         "Diagnostic only", "diagnostic only", "研究诊断",
         "not make production", "does not promote", "not a trading strategy",
         "不是交易策略", "not trade", "research diagnostics only"],
    ),
]


def _pass(check_id: str, check_name: str, evidence: str, notes: str = "") -> dict:
    return {
        "check_id": check_id,
        "check_name": check_name,
        "status": "PASS",
        "evidence": evidence,
        "notes": notes,
    }


def _fail(check_id: str, check_name: str, evidence: str, notes: str = "") -> dict:
    return {
        "check_id": check_id,
        "check_name": check_name,
        "status": "FAIL",
        "evidence": evidence,
        "notes": notes,
    }


# ── Checks ───────────────────────────────────────────────────────────────────

def check_file_exists_and_size() -> tuple[dict | None, str | None]:
    """Returns (check_result, html_text_or_None)."""
    if not HTML.exists():
        return _fail("file_exists", "HTML file exists", "File not found", str(HTML)), None
    size = HTML.stat().st_size
    if size > MAX_SIZE_BYTES:
        return (
            _fail(
                "file_size",
                "HTML file size < 4.5MB",
                f"{size / 1024 / 1024:.2f} MB",
                f"Exceeds {MAX_SIZE_BYTES / 1024 / 1024:.1f} MB limit",
            ),
            None,
        )
    text = HTML.read_text(encoding="utf-8", errors="replace")
    return (
        _pass(
            "file_exists_and_size",
            "HTML file exists and size < 4.5MB",
            f"{size / 1024 / 1024:.2f} MB, {len(text)} chars",
        ),
        text,
    )


def check_csv_factor_coverage(html_text: str) -> list[dict]:
    """Check all factor_ids from CSV appear in HTML."""
    results = []
    if not PROFILE_CSV.exists():
        results.append(
            _fail(
                "csv_exists",
                "Profile CSV exists",
                "File not found",
                str(PROFILE_CSV),
            )
        )
        return results

    factor_ids: list[str] = []
    try:
        with open(PROFILE_CSV, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                fid = row.get("factor_id", "").strip()
                if fid:
                    factor_ids.append(fid)
    except Exception as exc:
        results.append(
            _fail("csv_readable", "Profile CSV readable", str(exc))
        )
        return results

    if not factor_ids:
        results.append(
            _fail("csv_factor_count", "Profile CSV has factor_ids", "0 factors found")
        )
        return results

    results.append(
        _pass("csv_factor_count", "Profile CSV has factor_ids", f"{len(factor_ids)} factors")
    )

    missing = [fid for fid in factor_ids if fid not in html_text]
    if missing:
        results.append(
            _fail(
                "csv_factor_coverage",
                "All CSV factor_ids present in HTML",
                f"{len(factor_ids) - len(missing)}/{len(factor_ids)} found",
                f"Missing: {', '.join(missing[:20])}",
            )
        )
    else:
        results.append(
            _pass(
                "csv_factor_coverage",
                "All CSV factor_ids present in HTML",
                f"{len(factor_ids)}/{len(factor_ids)} found",
            )
        )
    return results


def check_pm35_factors(html_text: str) -> dict:
    """Check PM-35 five new factors appear in HTML."""
    missing = [fid for fid in PM35_NEW_FACTORS if fid not in html_text]
    if missing:
        return _fail(
            "pm35_new_factors",
            "PM-35 new factors present in HTML",
            f"{len(PM35_NEW_FACTORS) - len(missing)}/{len(PM35_NEW_FACTORS)} found",
            f"Missing: {', '.join(missing)}",
        )
    return _pass(
        "pm35_new_factors",
        "PM-35 new factors present in HTML",
        f"{len(PM35_NEW_FACTORS)}/{len(PM35_NEW_FACTORS)} found",
    )



def check_new_factor_metrics_populated(html_text: str) -> dict:
    """Verify factors with factor-level evaluation data have populated metrics.

    This catches the PM-40 issue where new factors showed blank Best Horizon Metrics
    because the HTML builder only read from old diagnostics files.
    """
    import re as _re
    import json as _json
    m = _re.search(r'<script id="factorPayload" type="application/json">(.*?)</script>', html_text, _re.DOTALL)
    if not m:
        return _fail(
            "new_factor_metrics",
            "New factor metrics populated",
            "factorPayload not found",
        )
    try:
        data = _json.loads(m.group(1))
    except _json.JSONDecodeError:
        return _fail(
            "new_factor_metrics",
            "New factor metrics populated",
            "JSON parse error",
        )
    problems = []
    for f in data.get("factors", []):
        fid = f.get("factor_id", "")
        has_level_eval = f.get("ev_has_factor_level_evaluation", False)
        rankic = f.get("rankic_mean")
        if has_level_eval and rankic is None:
            problems.append(f"{fid}: rankic_mean=None despite having factor-level evaluation")
    if problems:
        return _fail(
            "new_factor_metrics",
            "New factor metrics populated",
            f"{len(problems)} factors with missing metrics",
            "; ".join(problems[:5]),
        )
    return _pass(
        "new_factor_metrics",
        "New factor metrics populated",
        f"All {len(data.get('factors', []))} factors have metrics",
    )

def check_section_markers(html_text: str) -> list[dict]:
    """Check each required section marker set."""
    results = []
    for check_id, check_name, phrases in SECTION_CHECKS:
        found = any(phrase in html_text for phrase in phrases)
        matched = [p for p in phrases if p in html_text]
        if found:
            results.append(
                _pass(check_id, check_name, f"Matched: {', '.join(matched)}")
            )
        else:
            results.append(
                _fail(
                    check_id,
                    check_name,
                    "Not found",
                    f"None of: {', '.join(phrases)}",
                )
            )
    return results


def check_entrypoint_doc_alignment() -> list[dict]:
    """Check that entrypoint docs reference post-intake workflow docs."""
    results = []

    start_here = ROOT / "docs" / "factor_library" / "START_HERE.md"
    control_center = ROOT / "docs" / "factor_library" / "FACTOR_LIBRARY_CONTROL_CENTER.md"
    regen_contract = ROOT / "docs" / "factor_library" / "REGENERATION_CONTRACT.md"

    # Check 1: START_HERE.md contains POST_INTAKE_WORKFLOW_RUNBOOK.md
    if start_here.exists():
        txt = start_here.read_text(encoding="utf-8")
        if "POST_INTAKE_WORKFLOW_RUNBOOK.md" in txt:
            results.append(_pass(
                "doc_align_start_here",
                "START_HERE.md references POST_INTAKE_WORKFLOW_RUNBOOK.md",
                "Found",
            ))
        else:
            results.append(_fail(
                "doc_align_start_here",
                "START_HERE.md references POST_INTAKE_WORKFLOW_RUNBOOK.md",
                "Not found",
                "Add section referencing POST_INTAKE_WORKFLOW_RUNBOOK.md",
            ))
    else:
        results.append(_fail("doc_align_start_here", "START_HERE.md exists", "File not found"))

    # Check 2: FACTOR_LIBRARY_CONTROL_CENTER.md contains POST_INTAKE_WORKFLOW_RUNBOOK.md
    if control_center.exists():
        txt = control_center.read_text(encoding="utf-8")
        if "POST_INTAKE_WORKFLOW_RUNBOOK.md" in txt:
            results.append(_pass(
                "doc_align_control_center",
                "FACTOR_LIBRARY_CONTROL_CENTER.md references POST_INTAKE_WORKFLOW_RUNBOOK.md",
                "Found",
            ))
        else:
            results.append(_fail(
                "doc_align_control_center",
                "FACTOR_LIBRARY_CONTROL_CENTER.md references POST_INTAKE_WORKFLOW_RUNBOOK.md",
                "Not found",
                "Add reference to POST_INTAKE_WORKFLOW_RUNBOOK.md in Extension Points or Audit First Steps",
            ))
    else:
        results.append(_fail("doc_align_control_center", "FACTOR_LIBRARY_CONTROL_CENTER.md exists", "File not found"))

    # Check 3: REGENERATION_CONTRACT.md contains POST_INTAKE_WORKFLOW_RUNBOOK.md or RESOURCE_AWARE_REFRESH_GUIDE.md
    if regen_contract.exists():
        txt = regen_contract.read_text(encoding="utf-8")
        has_runbook = "POST_INTAKE_WORKFLOW_RUNBOOK.md" in txt
        has_guide = "RESOURCE_AWARE_REFRESH_GUIDE.md" in txt
        if has_runbook and has_guide:
            results.append(_pass(
                "doc_align_regen_contract",
                "REGENERATION_CONTRACT.md references post-intake docs",
                "Found both POST_INTAKE_WORKFLOW_RUNBOOK.md and RESOURCE_AWARE_REFRESH_GUIDE.md",
            ))
        elif has_runbook or has_guide:
            found = "POST_INTAKE_WORKFLOW_RUNBOOK.md" if has_runbook else "RESOURCE_AWARE_REFRESH_GUIDE.md"
            results.append(_fail(
                "doc_align_regen_contract",
                "REGENERATION_CONTRACT.md references post-intake docs",
                f"Found only {found}",
                "Add missing reference",
            ))
        else:
            results.append(_fail(
                "doc_align_regen_contract",
                "REGENERATION_CONTRACT.md references post-intake docs",
                "Not found",
                "Add section referencing POST_INTAKE_WORKFLOW_RUNBOOK.md and RESOURCE_AWARE_REFRESH_GUIDE.md",
            ))
    else:
        results.append(_fail("doc_align_regen_contract", "REGENERATION_CONTRACT.md exists", "File not found"))

    return results


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check factor-evaluation.html completeness."
    )
    # No required args — fully standalone
    parser.parse_args()

    all_checks: list[dict] = []

    # 1. File existence & size
    result, html_text = check_file_exists_and_size()
    if result is not None:
        all_checks.append(result)
    if html_text is None:
        # Cannot continue
        _write_reports(all_checks)
        _print_summary(all_checks)
        return 1

    # 2. CSV factor coverage
    all_checks.extend(check_csv_factor_coverage(html_text))

    # 3. PM-35 new factors
    all_checks.append(check_pm35_factors(html_text))
    all_checks.append(check_new_factor_metrics_populated(html_text))

    # 4. Section markers
    all_checks.extend(check_section_markers(html_text))

    # 5. Entrypoint doc alignment (PM-38B)
    all_checks.extend(check_entrypoint_doc_alignment())

    # Write outputs
    _write_reports(all_checks)
    _print_summary(all_checks)

    any_fail = any(c["status"] == "FAIL" for c in all_checks)
    return 1 if any_fail else 0


def _write_reports(checks: list[dict]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # CSV
    with open(REPORT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["check_id", "check_name", "status", "evidence", "notes"]
        )
        writer.writeheader()
        writer.writerows(checks)

    # JSON
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "html_path": str(HTML),
        "profile_csv_path": str(PROFILE_CSV),
        "total_checks": len(checks),
        "passed": sum(1 for c in checks if c["status"] == "PASS"),
        "failed": sum(1 for c in checks if c["status"] == "FAIL"),
        "checks": checks,
    }
    with open(REPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)


def _print_summary(checks: list[dict]) -> None:
    passed = sum(1 for c in checks if c["status"] == "PASS")
    failed = sum(1 for c in checks if c["status"] == "FAIL")
    total = len(checks)

    print("=" * 72)
    print("Factor Evaluation Page — Completeness QA Report")
    print("=" * 72)
    for c in checks:
        icon = "✓" if c["status"] == "PASS" else "✗"
        print(f"  {icon} [{c['check_id']}] {c['check_name']}: {c['status']}")
        if c.get("evidence"):
            print(f"      evidence: {c['evidence']}")
        if c.get("notes") and c["status"] == "FAIL":
            print(f"      notes:    {c['notes']}")
    print("-" * 72)
    print(f"  Total: {total}  |  PASS: {passed}  |  FAIL: {failed}")
    print(f"  CSV:   {REPORT_CSV}")
    print(f"  JSON:  {REPORT_JSON}")
    print("=" * 72)


if __name__ == "__main__":
    sys.exit(main())
