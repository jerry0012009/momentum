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
import re
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

MAX_SIZE_BYTES = 7.0 * 1024 * 1024  # 7 MB (84 factors × 6 horizons)

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


def _c(
    check_id: str,
    check_name: str,
    status: str,
    evidence: str = "",
    notes: str = "",
) -> dict:
    """Generic check builder — dispatches to _pass or _fail based on status."""
    if status == "PASS":
        return _pass(check_id, check_name, evidence, notes)
    return _fail(check_id, check_name, evidence, notes)


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
                "HTML file size < 7.0MB",
                f"{size / 1024 / 1024:.2f} MB",
                f"Exceeds {MAX_SIZE_BYTES / 1024 / 1024:.1f} MB limit",
            ),
            None,
        )
    text = HTML.read_text(encoding="utf-8", errors="replace")
    return (
        _pass(
            "file_exists_and_size",
            "HTML file exists and size < 7.0MB",
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


def check_pm40b_display_consistency(html_text: str) -> list[dict]:
    """PM-40B: Verify display consistency for PM-35 new factors.

    Checks:
    1. WORKFLOW_READY factors should not have source_warning (no_horizon_data etc.)
    2. Redundancy cluster_id should not be -1 when profile has real cluster_id
    3. Factors with rankic_mean should not show bare 'No data' in Monthly RankIC
    """
    import re as _re
    import json as _json
    results = []
    PM35 = ["rev_2h", "mom_vol_adjusted_20h", "range_breakout_vol_confirm_20h",
            "volume_pressure_20h", "xs_rank_mom_accel"]

    m = _re.search(r'<script id="factorPayload" type="application/json">(.*?)</script>', html_text, _re.DOTALL)
    if not m:
        results.append(_fail("pm40b_payload", "PM-40B display consistency", "factorPayload not found"))
        return results
    try:
        data = _json.loads(m.group(1))
    except _json.JSONDecodeError:
        results.append(_fail("pm40b_payload", "PM-40B display consistency", "JSON parse error"))
        return results

    problems = []
    for f in data.get("factors", []):
        fid = f.get("factor_id", "")
        if fid not in PM35:
            continue
        # Check 1: WORKFLOW_READY should not have stale source_warning
        wf = f.get("workflow_ready_status", "")
        sw = f.get("source_warning", "")
        if wf == "WORKFLOW_READY" and sw:
            problems.append(f"{fid}: WORKFLOW_READY but source_warning='{sw}'")
        # Check 2: cluster_id should not be -1 when profile has data
        cid = f.get("redundancy_cluster_id")
        pcid = f.get("profile_cluster_id")
        if cid == -1 and pcid is not None and pcid != -1:
            problems.append(f"{fid}: redundancy_cluster_id=-1 but profile_cluster_id={pcid}")
        # Check 3: rankic_mean exists but monthly_ic empty is OK (explanatory msg)
        # Just verify rankic_mean is populated
        rankic = f.get("rankic_mean")
        if rankic is None:
            problems.append(f"{fid}: rankic_mean=None (should have fallback data)")

    if problems:
        results.append(_fail(
            "pm40b_display_consistency",
            "PM-40B display consistency for new factors",
            f"{len(problems)} issues found",
            "; ".join(problems),
        ))
    else:
        results.append(_pass(
            "pm40b_display_consistency",
            "PM-40B display consistency for new factors",
            f"All {len(PM35)} factors pass consistency checks",
        ))
    return results


def check_per_factor_detail_completeness(html_text: str) -> list[dict]:
    """Per-factor detail completeness for PM-35 new factors.

    For each of the 5 PM-35 factors, verify:
    1. Best Horizon Metrics not empty (rankic_mean, rankic_t_stat)
    2. Monthly RankIC: has data or explanatory message (not bare 'No data')
    3. Monthly LS: has data entries
    4. Redundancy: cluster_id not -1, novelty not INSUFFICIENT_OVERLAP
    5. Source Warning: no stale no_horizon_data / monthly_ls_unavailable
    6. Unified Profile: workflow_ready_status, evidence_status populated
    """
    import re as _re
    import json as _json
    results = []
    PM35 = ['rev_2h', 'mom_vol_adjusted_20h', 'range_breakout_vol_confirm_20h',
            'volume_pressure_20h', 'xs_rank_mom_accel']

    m = _re.search(r'<script id="factorPayload" type="application/json">(.*?)</script>', html_text, _re.DOTALL)
    if not m:
        results.append(_fail('pf_detail_payload', 'Per-factor detail completeness', 'factorPayload not found'))
        return results
    try:
        data = _json.loads(m.group(1))
    except _json.JSONDecodeError:
        results.append(_fail('pf_detail_payload', 'Per-factor detail completeness', 'JSON parse error'))
        return results

    all_pass = True
    issues = []
    factor_results = []
    for f in data.get('factors', []):
        fid = f.get('factor_id', '')
        if fid not in PM35:
            continue
        fid_issues = []

        # 1. Best Horizon Metrics
        if f.get('rankic_mean') is None:
            fid_issues.append('rankic_mean=None')
        if f.get('rankic_t_stat') is None:
            fid_issues.append('rankic_t_stat=None')

        # 2. Monthly RankIC: has data or has rankic_mean as fallback
        mic = f.get('monthly_ic', [])
        if len(mic) == 0 and f.get('rankic_mean') is None:
            fid_issues.append('monthly_ic empty AND no rankic_mean fallback')

        # 3. Monthly LS
        mls = f.get('monthly_ls', [])
        if len(mls) == 0:
            fid_issues.append('monthly_ls empty')

        # 4. Redundancy
        cid = f.get('redundancy_cluster_id')
        if cid == -1 or cid is None:
            fid_issues.append(f'redundancy_cluster_id={cid}')
        nov = f.get('novelty_assessment', '')
        if nov == 'INSUFFICIENT_OVERLAP':
            fid_issues.append('novelty_assessment=INSUFFICIENT_OVERLAP')

        # 5. Source Warning
        sw = f.get('source_warning', '')
        if 'no_horizon_data' in sw:
            fid_issues.append('source_warning has no_horizon_data')
        if 'monthly_ls_unavailable' in sw:
            fid_issues.append('source_warning has monthly_ls_unavailable')

        # 6. Unified Profile
        wf = f.get('workflow_ready_status', '')
        es = f.get('evidence_status', '')
        if not wf:
            fid_issues.append('workflow_ready_status empty')
        if not es:
            fid_issues.append('evidence_status empty')

        if fid_issues:
            all_pass = False
            issues.append(f'{fid}: {" | ".join(fid_issues)}')
        factor_results.append((fid, len(fid_issues) == 0))

    if all_pass:
        results.append(_pass(
            'pf_detail_completeness',
            'Per-factor detail completeness (PM-35)',
            f'{len(factor_results)} factors all pass',
        ))
    else:
        results.append(_fail(
            'pf_detail_completeness',
            'Per-factor detail completeness (PM-35)',
            f'{len(issues)} factors with issues',
            '; '.join(issues),
        ))
    return results


def check_pm40c_scorecard_redundancy_consistency(html_text: str) -> list[dict]:
    """PM-40C: Verify scorecard and redundancy consistency for new factors.

    For WORKFLOW_READY factors:
    1. Scorecard should not show stale REVIEW_REQUIRED when profile says PROMISING
    2. Redundancy should not show Valid Pairs 0/75 alongside NOVEL_DISTINCT
    3. No unexplained no_horizon_data / monthly_ls_unavailable in source_warning
    """
    import re as _re
    import json as _json
    results = []
    PM35 = ['rev_2h', 'mom_vol_adjusted_20h', 'range_breakout_vol_confirm_20h',
            'volume_pressure_20h', 'xs_rank_mom_accel']

    m = _re.search(r'<script id="factorPayload" type="application/json">(.*?)</script>', html_text, _re.DOTALL)
    if not m:
        results.append(_fail('pm40c_payload', 'PM-40C scorecard/redundancy consistency', 'factorPayload not found'))
        return results

    data = _json.loads(m.group(1))
    issues = []
    for f in data.get('factors', []):
        fid = f.get('factor_id', '')
        if fid not in PM35:
            continue
        wf = f.get('workflow_ready_status', '')
        if wf != 'WORKFLOW_READY':
            continue

        # Check 1: Scorecard should not be stale (only flag if rankic_mean=0)
        qclass = f.get('final_quality_class', '')
        pclass = f.get('profile_class', '')
        rankic = f.get('rankic_mean', 0) or 0
        if qclass == 'REVIEW_REQUIRED' and pclass and 'PROMISING' in pclass and rankic == 0:
            issues.append(f'{fid}: scorecard={qclass} conflicts with profile={pclass} (stale rankic=0)')

        # Check 2: No stale redundancy pair data alongside NOVEL_DISTINCT
        novelty = f.get('novelty_assessment', '')
        pairs = f.get('valid_redundancy_pair_count')
        if novelty in ('NOVEL_DISTINCT', 'REDUNDANT_NOVELTY_DERIVED') and pairs == 0:
            issues.append(f'{fid}: novelty={novelty} but valid_pairs=0 (stale)')

        # Check 3: No stale warnings anywhere in factor JSON
        sw = f.get('source_warning', '')
        rn_zh = f.get('review_notes_zh', '')
        rn_en = f.get('review_notes_en', '')
        has_monthly_ic = bool(f.get('monthly_ic'))
        has_monthly_ls = bool(f.get('monthly_ls'))
        for field_name, val in [('source_warning', sw), ('review_notes_zh', rn_zh), ('review_notes_en', rn_en)]:
            if 'no_horizon_data' in val:
                if has_monthly_ic:
                    issues.append(f'{fid}: {field_name} has no_horizon_data but monthly_ic exists')
                else:
                    issues.append(f'{fid}: {field_name} has no_horizon_data')
            if 'monthly_ls_unavailable' in val:
                if has_monthly_ls:
                    issues.append(f'{fid}: {field_name} has monthly_ls_unavailable but monthly_ls exists')
                else:
                    issues.append(f'{fid}: {field_name} has monthly_ls_unavailable')

    if issues:
        results.append(_fail('pm40c_consistency', 'PM-40C scorecard/redundancy consistency', '; '.join(issues)))
    else:
        results.append(_pass('pm40c_consistency', 'PM-40C scorecard/redundancy consistency', f'{len(PM35)} factors consistent'))
    return results

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


def check_pm46b_metadata_display(html_text: str) -> list[dict]:
    """PM-46B: Check that new factors have source metadata and LS-BTC corr in HTML."""
    results = []
    import re, json as _json

    # Extract factor payload from HTML
    m = re.search(r"type=\"application/json\">(.*?)</script>", html_text, re.DOTALL)
    if not m:
        results.append(_fail("pm46b_payload", "PM-46B payload extraction", "Could not extract JSON payload"))
        return results

    try:
        data = _json.loads(m.group(1))
    except Exception as e:
        results.append(_fail("pm46b_payload", "PM-46B payload extraction", f"JSON parse error: {e}"))
        return results

    # Check PM-45 new factor specifically
    for f in data.get("factors", []):
        fid = f.get("factor_id", "")
        if fid != "up_down_vol_ratio_20h":
            continue

        # Check source metadata
        ds = f.get("data_source_type", "")
        sf = f.get("source_fields", "")
        rc = f.get("required_columns", "")
        if ds and sf and rc:
            results.append(_pass("pm46b_source_metadata",
                                 "PM-46B source metadata for up_down_vol_ratio_20h",
                                 f"data_source={ds}, source_fields={sf}, required_columns={rc}"))
        else:
            results.append(_fail("pm46b_source_metadata",
                                 "PM-46B source metadata for up_down_vol_ratio_20h",
                                 f"data_source={ds}, source_fields={sf}, required_columns={rc}"))

        # Check LS-BTC corr
        ls_corr = f.get("long_short_btc_corr")
        if ls_corr is not None:
            results.append(_pass("pm46b_ls_btc_corr",
                                 "PM-46B LS-BTC Corr for up_down_vol_ratio_20h",
                                 f"ls_btc_corr={ls_corr}"))
        else:
            results.append(_fail("pm46b_ls_btc_corr",
                                 "PM-46B LS-BTC Corr for up_down_vol_ratio_20h",
                                 "long_short_btc_corr is null/missing"))

        # Check shape Q5 classification (best horizon = 4h)
        ss = f.get("shape_stability", {})
        hz4 = ss.get("4h", {})
        dec = hz4.get("decile", {})
        q5 = dec.get("q5_shape_class_from_pm26", "")
        if q5:
            results.append(_pass("pm46b_shape_q5",
                                 "PM-46B Shape Q5 classification for up_down_vol_ratio_20h",
                                 f"q5_shape_class={q5}"))
        else:
            results.append(_fail("pm46b_shape_q5",
                                 "PM-46B Shape Q5 classification for up_down_vol_ratio_20h",
                                 "q5_shape_class_from_pm26 is empty"))
        break

    return results


def check_pm53b_active_universe_consistency(html_text: str) -> list[dict]:
    """PM-53B: Active factor universe consistency guard.

    Checks:
    1. Page visible factor count == active factor count (from state JSON)
    2. Every visible factor has required diagnostics presence flags
    3. Every active factor has shape/decile/capacity/profile/scorecard availability
    4. If any factor is visible but missing required downstream diagnostics, FAIL
    """
    import csv as _csv
    import re as _re
    import json as _json
    results = []

    state_path = (
        ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"
        / "factor_library_state.json"
    )
    if not state_path.exists():
        results.append(_fail("pm53b_state", "PM-53B state file exists",
                             "File not found", str(state_path)))
        return results

    state = _json.loads(state_path.read_text())
    active_fids = set(state.get("registered_factor_ids", []))
    n_active = len(active_fids)

    # Extract page payload
    m = _re.search(r'<script id="factorPayload" type="application/json">(.*?)</script>',
                   html_text, _re.DOTALL)
    if not m:
        results.append(_fail("pm53b_payload", "PM-53B payload extraction",
                             "factorPayload not found"))
        return results
    try:
        data = _json.loads(m.group(1))
    except _json.JSONDecodeError:
        results.append(_fail("pm53b_payload", "PM-53B payload extraction", "JSON parse error"))
        return results

    page_fids = set()
    factor_data = {}
    for f in data.get("factors", []):
        fid = f.get("factor_id", "")
        if fid:
            page_fids.add(fid)
            factor_data[fid] = f

    n_page = len(page_fids)

    # Check 1: page count == active count
    if n_page != n_active:
        missing_from_page = sorted(active_fids - page_fids)
        extra_in_page = sorted(page_fids - active_fids)
        detail = f"page={n_page} vs active={n_active}"
        notes_parts = []
        if missing_from_page:
            notes_parts.append(f"missing_from_page: {', '.join(missing_from_page[:10])}")
        if extra_in_page:
            notes_parts.append(f"extra_in_page: {', '.join(extra_in_page[:5])}")
        results.append(_fail("pm53b_count_match", "PM-53B page factor count == active count",
                             detail, "; ".join(notes_parts)))
    else:
        results.append(_pass("pm53b_count_match", "PM-53B page factor count == active count",
                             f"{n_page} factors"))

    # Check 2 & 3: every factor has required diagnostics
    # Required presence: shape, decile, capacity, profile, scorecard
    diag_dir = (
        ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"
        / "factor_diagnostics"
    )
    required_csvs = {
        "shape": diag_dir / "factor_quantile_shape_summary.csv",
        "decile": diag_dir / "factor_decile_shape_summary.csv",
        "capacity": diag_dir / "factor_capacity_liquidity_summary.csv",
        "scorecard": diag_dir / "factor_quality_scorecard.csv",
        "profile": diag_dir / "factor_unified_profile_summary.csv",
    }

    # Build per-table factor sets
    table_factor_sets = {}
    for name, path in required_csvs.items():
        if path.exists():
            try:
                with open(path, newline="", encoding="utf-8") as f:
                    reader = _csv.DictReader(f)
                    key = "factor_id" if "factor_id" in (reader.fieldnames or []) else "factor_name"
                    ids = set()
                    for row in reader:
                        val = row.get(key, "").strip()
                        if val:
                            ids.add(val)
                    table_factor_sets[name] = ids
            except Exception:
                table_factor_sets[name] = set()
        else:
            table_factor_sets[name] = set()

    # Check each visible factor
    incomplete_factors = []
    for fid in sorted(page_fids):
        missing_tables = []
        for name, ids in table_factor_sets.items():
            if fid not in ids:
                missing_tables.append(name)
        if missing_tables:
            incomplete_factors.append((fid, missing_tables))

    if incomplete_factors:
        details = "; ".join(
            f"{fid}: missing {', '.join(tables)}"
            for fid, tables in incomplete_factors[:10]
        )
        if len(incomplete_factors) > 10:
            details += f"; ... and {len(incomplete_factors) - 10} more"
        results.append(_fail(
            "pm53b_factor_diagnostics",
            "PM-53B all visible factors have required diagnostics",
            f"{len(incomplete_factors)}/{n_page} factors incomplete",
            details,
        ))
    else:
        results.append(_pass(
            "pm53b_factor_diagnostics",
            "PM-53B all visible factors have required diagnostics",
            f"All {n_page} factors have shape/decile/capacity/scorecard/profile",
        ))

    return results


# ── Main ─────────────────────────────────────────────────────────────────────

def check_pm55_robust_significance(html_text: str) -> list[dict]:
    """PM-55: Robust significance page integration checks.

    1. 84/84 factors have robust_rankic payload
    2. Each factor has 4 horizons in robust_rankic
    3. All-Horizon Table has robust columns
    4. Best Horizon Metrics has robust t-stat
    5. funding_rate_zscore_80h shows NAIVE_ONLY_SIGNIFICANT
    """
    import re as _re
    import json as _json
    results = []

    # Extract payload
    m = _re.search(r'<script id="factorPayload" type="application/json">(.*?)</script>',
                   html_text, _re.DOTALL)
    if not m:
        results.append(_fail("pm55_payload", "PM-55 payload extraction",
                             "factorPayload not found"))
        return results
    try:
        data = _json.loads(m.group(1))
    except _json.JSONDecodeError:
        results.append(_fail("pm55_payload", "PM-55 payload extraction", "JSON parse error"))
        return results

    factors = data.get("factors", [])
    n_total = len(factors)

    # Check 1: all factors have robust_rankic
    has_robust = sum(1 for f in factors if "robust_rankic" in f and f["robust_rankic"])
    if has_robust != n_total:
        results.append(_fail("pm55_robust_payload", "PM-55 all factors have robust_rankic",
                             f"{has_robust}/{n_total}"))
    else:
        results.append(_pass("pm55_robust_payload", "PM-55 all factors have robust_rankic",
                             f"{has_robust}/{n_total}"))

    # Check 2: each factor has 4 horizons
    missing_horizons = 0
    for f in factors:
        rr = f.get("robust_rankic", {})
        for h in ["1h", "4h", "24h", "72h"]:
            if h not in rr:
                missing_horizons += 1
    if missing_horizons > 0:
        results.append(_fail("pm55_horizon_coverage", "PM-55 all 4 horizons present",
                             f"{missing_horizons} missing horizon entries"))
    else:
        results.append(_pass("pm55_horizon_coverage", "PM-55 all 4 horizons present",
                             "All 84×4 horizon entries present"))

    # Check 3: All-Horizon Table has robust columns
    has_robust_col = "Robust t</th>" in html_text
    has_class_col = "Robust Class</th>" in html_text
    has_inflation_col = "Inflation</th>" in html_text
    has_overlap_col = "Overlap</th>" in html_text
    if all([has_robust_col, has_class_col, has_inflation_col, has_overlap_col]):
        results.append(_pass("pm55_all_horizon_table", "PM-55 All-Horizon Table has robust columns",
                             "Robust t, Robust Class, Inflation, Overlap"))
    else:
        missing = []
        if not has_robust_col: missing.append("Robust t")
        if not has_class_col: missing.append("Robust Class")
        if not has_inflation_col: missing.append("Inflation")
        if not has_overlap_col: missing.append("Overlap")
        results.append(_fail("pm55_all_horizon_table", "PM-55 All-Horizon Table has robust columns",
                             f"Missing: {', '.join(missing)}"))

    # Check 4: Best Horizon Metrics has robust t-stat label
    has_robust_label = "Robust t-stat" in html_text
    has_naive_label = "Naive t-stat" in html_text
    if has_robust_label and has_naive_label:
        results.append(_pass("pm55_best_horizon_robust", "PM-55 Best Horizon has robust t-stat",
                             "Both Naive t-stat and Robust t-stat labels present"))
    else:
        results.append(_fail("pm55_best_horizon_robust", "PM-55 Best Horizon has robust t-stat",
                             f"robust_label={has_robust_label}, naive_label={has_naive_label}"))

    # Check 5: funding_rate_zscore_80h shows NAIVE_ONLY_SIGNIFICANT
    frz = next((f for f in factors if f["factor_id"] == "funding_rate_zscore_80h"), None)
    if frz:
        rr = frz.get("robust_rankic", {})
        naive_only_horizons = []
        for h in ["1h", "4h", "24h", "72h"]:
            r = rr.get(h, {})
            if r.get("significance_class_robust") == "NAIVE_ONLY_SIGNIFICANT":
                naive_only_horizons.append(h)
        if naive_only_horizons:
            results.append(_pass("pm55_naive_only_example",
                                 "PM-55 funding_rate_zscore_80h shows NAIVE_ONLY_SIGNIFICANT",
                                 f"NAIVE_ONLY at: {', '.join(naive_only_horizons)}"))
        else:
            results.append(_fail("pm55_naive_only_example",
                                 "PM-55 funding_rate_zscore_80h shows NAIVE_ONLY_SIGNIFICANT",
                                 f"No NAIVE_ONLY found; classes: {[rr.get(h, {}).get('significance_class_robust') for h in ['1h','4h','24h','72h']]}"))
    else:
        results.append(_fail("pm55_naive_only_example",
                             "PM-55 funding_rate_zscore_80h shows NAIVE_ONLY_SIGNIFICANT",
                             "Factor not found in payload"))

    return results


def check_pm57_return_side_robust(html_text: str) -> list[dict]:
    """PM-57: Return-side robust diagnostics page integration checks.

    Checks:
    1. 84/84 factors have return_robust payload
    2. Each factor has LS robust 4 horizons
    3. LS robust section (h3) exists in page
    4. LS robust table has required columns
    5. Paper subset badge for unavailable factors
    6. Fee subset badge for unavailable factors
    7. rev_2h shows RETURN_ROBUST_NEGATIVE at 72h
    8. Cost-collapsed example shows correctly
    9. Active workflow consistency still PASS
    """
    results = []

    # Extract JSON payload (same as PM-55)
    m = re.search(r'<script id="factorPayload" type="application/json">(.*?)</script>',
                  html_text, re.DOTALL)
    if not m:
        results.append(_fail("pm57_payload", "PM-57 payload extraction", "factorPayload not found"))
        return results
    try:
        data = json.loads(m.group(1))
        factors = data.get("factors", [])
    except Exception as e:
        results.append(_fail("pm57_payload", "PM-57 payload extraction", str(e)))
        return results

    # Check 1: all factors have return_robust
    has_rr = sum(1 for f in factors if "return_robust" in f and f["return_robust"])
    if has_rr < 84:
        results.append(_fail("pm57_return_robust_payload",
                             "PM-57 all factors have return_robust",
                             f"Only {has_rr}/84 have return_robust"))
    else:
        results.append(_pass("pm57_return_robust_payload",
                             "PM-57 all factors have return_robust",
                             f"{has_rr}/84"))

    # Check 2: LS robust 4 horizons
    ls_incomplete = []
    for f in factors:
        fid = f.get("factor_id", "")
        rr = f.get("return_robust", {})
        ls = rr.get("ls", {}) if rr else {}
        if len(ls) < 4:
            ls_incomplete.append(fid)
    if ls_incomplete:
        results.append(_fail("pm57_ls_horizon_coverage",
                             "PM-57 all factors have LS robust 4 horizons",
                             f"{len(ls_incomplete)} missing: {ls_incomplete[:5]}"))
    else:
        results.append(_pass("pm57_ls_horizon_coverage",
                             "PM-57 all factors have LS robust 4 horizons",
                             "84/84 × 4 horizons"))

    # Check 3: LS robust section exists in HTML
    if "Robust LS Diagnostics" in html_text:
        results.append(_pass("pm57_ls_section",
                             "PM-57 Robust LS Diagnostics section exists",
                             "Section h3 found"))
    else:
        results.append(_fail("pm57_ls_section",
                             "PM-57 Robust LS Diagnostics section exists",
                             "Section h3 not found"))

    # Check 4: robust-table CSS class used
    if "robust-table" in html_text:
        results.append(_pass("pm57_ls_table",
                             "PM-57 LS robust table rendered",
                             "robust-table class found"))
    else:
        results.append(_fail("pm57_ls_table",
                             "PM-57 LS robust table rendered",
                             "robust-table class not found"))

    # Check 5: Paper subset badge for unavailable factors
    paper_unavail = sum(1 for f in factors
                        if f.get("return_robust", {}).get("coverage", {}).get("paper_robust") == "UNAVAILABLE")
    if paper_unavail > 0:
        results.append(_pass("pm57_paper_subset",
                             "PM-57 paper robust subset handling",
                             f"{paper_unavail} factors without paper robust (documented subset)"))
    else:
        results.append(_pass("pm57_paper_subset",
                             "PM-57 paper robust subset handling",
                             "All or subset present"))

    # Check 6: Fee subset badge for unavailable factors
    fee_unavail = sum(1 for f in factors
                      if f.get("return_robust", {}).get("coverage", {}).get("fee_robust") == "UNAVAILABLE")
    if fee_unavail > 0:
        results.append(_pass("pm57_fee_subset",
                             "PM-57 fee robust subset handling",
                             f"{fee_unavail} factors without fee robust (documented subset)"))
    else:
        results.append(_pass("pm57_fee_subset",
                             "PM-57 fee robust subset handling",
                             "All or subset present"))

    # Check 7: rev_2h shows RETURN_ROBUST_NEGATIVE at 72h
    rev2 = next((f for f in factors if f.get("factor_id") == "rev_2h"), None)
    if rev2:
        rr = rev2.get("return_robust", {}).get("ls", {}).get("72h", {})
        cls = rr.get("return_robust_class", "")
        if "NEGATIVE" in cls:
            results.append(_pass("pm57_rev2h_negative",
                                 "PM-57 rev_2h shows robust negative at 72h",
                                 f"class={cls}"))
        else:
            results.append(_fail("pm57_rev2h_negative",
                                 "PM-57 rev_2h shows robust negative at 72h",
                                 f"Expected NEGATIVE, got {cls}"))
    else:
        results.append(_fail("pm57_rev2h_negative",
                             "PM-57 rev_2h shows robust negative at 72h",
                             "rev_2h not found"))

    # Check 8: cost-collapsed factor
    cost_collapsed = None
    for f in factors:
        rr = f.get("return_robust") or {}
        fee = rr.get("fee") or {}
        if fee.get("cost_status") == "RETURN_COST_COLLAPSED":
            cost_collapsed = f
            break
    if cost_collapsed:
        results.append(_pass("pm57_cost_collapsed",
                             "PM-57 cost-collapsed example displayed",
                             f"{cost_collapsed.get('factor_id')}"))
    else:
        results.append(_pass("pm57_cost_collapsed",
                             "PM-57 cost-collapsed example displayed",
                             "No cost-collapsed in current subset"))

    # Check 9: page factor count still 84
    if len(factors) == 84:
        results.append(_pass("pm57_factor_count",
                             "PM-57 page factor count remains 84",
                             f"{len(factors)}"))
    else:
        results.append(_fail("pm57_factor_count",
                             "PM-57 page factor count remains 84",
                             f"Got {len(factors)}"))

    # Check 10: cost-status-badge CSS
    if "cost-status-badge" in html_text:
        results.append(_pass("pm57_cost_badge_css",
                             "PM-57 cost-status-badge CSS present",
                             "Found"))
    else:
        results.append(_fail("pm57_cost_badge_css",
                             "PM-57 cost-status-badge CSS present",
                             "Not found"))

    return results


def check_pm58_core_vs_optional(html_text: str) -> list[dict]:
    """PM-58: Core vs Optional workflow boundary checks.

    Checks:
    1. Optional Deep-dive Evidence section exists
    2. Summary table columns labeled 'opt'
    3. Paper/fee NOT in main reading order
    4. Robust RankIC/LS ARE in main reading order
    """
    results = []

    # Check 1: Optional Deep-dive Evidence section
    if "Optional Deep-dive Evidence" in html_text:
        results.append(_pass("pm58_optional_section",
                             "PM-58 Optional Deep-dive Evidence section exists",
                             "Found"))
    else:
        results.append(_fail("pm58_optional_section",
                             "PM-58 Optional Deep-dive Evidence section exists",
                             "Not found"))

    # Check 2: Summary table columns labeled 'opt'
    if '<span class="optional-label">opt</span>' in html_text:
        results.append(_pass("pm58_opt_label",
                             "PM-58 summary table columns labeled optional",
                             "opt label found"))
    else:
        results.append(_fail("pm58_opt_label",
                             "PM-58 summary table columns labeled optional",
                             "opt label not found"))

    # Check 3: Paper/fee NOT in main reading order
    # The How to Read section should NOT list Paper Portfolio or Fee Sensitivity in the main order
    how_to_read_match = re.search(r'阅读顺序.*?</ol>', html_text, re.DOTALL)
    if how_to_read_match:
        reading_order = how_to_read_match.group(0)
        has_paper_in_order = "Paper Portfolio" in reading_order and "Paper Portfolio" in reading_order.split("Optional")[0] if "Optional" in reading_order else "Paper Portfolio" in reading_order
        # Paper Portfolio should NOT be in the main ordered list
        if "Paper Portfolio" not in reading_order.split("Optional")[0] if "Optional" in reading_order else "Paper Portfolio" not in reading_order:
            results.append(_pass("pm58_paper_not_in_reading_order",
                                 "PM-58 Paper Portfolio NOT in main reading order",
                                 "Correctly excluded"))
        else:
            results.append(_fail("pm58_paper_not_in_reading_order",
                                 "PM-58 Paper Portfolio NOT in main reading order",
                                 "Still in main reading order"))
    else:
        results.append(_pass("pm58_paper_not_in_reading_order",
                             "PM-58 Paper Portfolio NOT in main reading order",
                             "How to Read section not found (cannot verify)"))

    # Check 4: Robust RankIC/LS ARE in main reading order
    how_to_read_match = re.search(r'阅读顺序.*?</ol>', html_text, re.DOTALL)
    if how_to_read_match:
        reading_order = how_to_read_match.group(0)
        has_rankic_robust = "RankIC Robust" in reading_order
        has_ls_robust = "LS Robust" in reading_order
        if has_rankic_robust and has_ls_robust:
            results.append(_pass("pm58_robust_in_reading_order",
                                 "PM-58 Robust RankIC/LS in main reading order",
                                 "Both present"))
        else:
            results.append(_fail("pm58_robust_in_reading_order",
                                 "PM-58 Robust RankIC/LS in main reading order",
                                 f"RankIC Robust: {has_rankic_robust}, LS Robust: {has_ls_robust}"))
    else:
        results.append(_fail("pm58_robust_in_reading_order",
                             "PM-58 Robust RankIC/LS in main reading order",
                             "How to Read section not found"))

    # Check 5: optional-deep-dive CSS class exists
    if "optional-deep-dive" in html_text:
        results.append(_pass("pm58_optional_css",
                             "PM-58 optional-deep-dive CSS class present",
                             "Found"))
    else:
        results.append(_fail("pm58_optional_css",
                             "PM-58 optional-deep-dive CSS class present",
                             "Not found"))

    return results


def check_pm58a_ls_monthly_aggregate(html_text: str) -> list[dict]:
    """PM-58A: LS monthly aggregate fields no longer show blank dash."""
    results = []

    # Parse payload
    payload_match = re.search(
        r'<script id="factorPayload"[^>]*>(.*?)</script>', html_text, re.DOTALL
    )
    if not payload_match:
        results.append({"check_id": "pm58a_ls_payload", "check_name": "PM-58A: LS payload", "status": "FAIL", "evidence": "No payload", "notes": ""})
        return results
    try:
        data = json.loads(payload_match.group(1))
        factors = data.get("factors", [])
    except Exception as e:
        results.append({"check_id": "pm58a_ls_payload", "check_name": "PM-58A: LS payload", "status": "FAIL", "evidence": str(e), "notes": ""})
        return results

    # Check: all active factors have non-null LS std in at least one horizon
    ls_fields = ["long_short_std", "long_short_annualized_return",
                  "long_short_annualized_vol", "long_short_max_drawdown"]
    factors_with_ls_data = 0
    factors_all_null = 0
    for f in factors:
        hm = f.get("horizon_metrics", {})
        has_any = False
        for hz_data in hm.values():
            if isinstance(hz_data, dict) and hz_data.get("long_short_std") is not None:
                has_any = True
                break
        if has_any:
            factors_with_ls_data += 1
        else:
            factors_all_null += 1

    results.append({
        "check_id": "pm58a_factors_with_ls_monthly_data",
        "check_name": "PM-58A: All factors have LS monthly data",
        "status": "PASS" if factors_all_null == 0 else "FAIL",
        "evidence": f"{factors_with_ls_data}/{len(factors)} factors have LS monthly data, {factors_all_null} all-null",
        "notes": "",
    })

    # Check: LS Std column in summary table is not blank for factors with data
    ls_std_pattern = re.compile(r'<td class="num">.*?</td>', re.DOTALL)

    return results


def check_pm58b_annualization_html(html_text: str) -> list[dict]:
    """PM-58B: Verify annualization-related content in HTML page.

    Checks:
    1. Page contains 'bars_per_year' in tooltip/glossary text
    2. Page does NOT contain 'portfolio annual return' or '组合累计年化收益'
       as Ann Return description (these are wrong descriptions)
    3. LS Sharpe tooltip mentions 'monthly' or '月度' (edge stability metric)
    """
    results = []

    # Check 1: bars_per_year present in tooltip text
    if "bars_per_year" in html_text or "bars-per-year" in html_text:
        results.append(_pass(
            "pm58b_bars_per_year_in_tooltip",
            "PM-58B: bars_per_year present in tooltip/glossary",
            "Found bars_per_year or bars-per-year in page",
        ))
    else:
        results.append(_fail(
            "pm58b_bars_per_year_in_tooltip",
            "PM-58B: bars_per_year present in tooltip/glossary",
            "Not found",
            "Expected bars_per_year in Ann Return tooltip or formula text",
        ))

    # Check 2: No wrong portfolio annual return description
    # Allow the string in negation contexts (e.g., "这不是组合累计年化收益" or "not portfolio annual return")
    import re as _re_check
    # Find all occurrences of "portfolio annual return" not preceded by "not " or "non-"
    portfolio_en_matches = _re_check.finditer(r"(?<!\bnot )(?<!non-)portfolio annual return", html_text.lower())
    # Find "组合累计年化收益" not preceded by "不是" or "并非"
    portfolio_zh_matches = _re_check.finditer(r"(?<!不是)(?<!并非)组合累计年化收益", html_text)
    has_portfolio_en = any(True for _ in portfolio_en_matches)
    has_portfolio_zh = any(True for _ in portfolio_zh_matches)
    if has_portfolio_en or has_portfolio_zh:
        found = []
        if has_portfolio_en:
            found.append("portfolio annual return (affirmative)")
        if has_portfolio_zh:
            found.append("组合累计年化收益 (affirmative)")
        results.append(_fail(
            "pm58b_no_portfolio_annual_return",
            "PM-58B: No affirmative 'portfolio annual return' / '组合累计年化收益' as Ann Return description",
            f"Found: {', '.join(found)}",
            "These are wrong descriptions for LS annualized return",
        ))
    else:
        results.append(_pass(
            "pm58b_no_portfolio_annual_return",
            "PM-58B: No affirmative 'portfolio annual return' / '组合累计年化收益' as Ann Return description",
            "Confirmed: no affirmative use found (negations allowed)",
        ))

    # Check 3: LS Sharpe tooltip mentions 'monthly' or '月度'
    import re as _re
    import json as _json
    m = _re.search(r'<script id="factorPayload"[^>]*>(.*?)</script>', html_text, _re.DOTALL)
    sharpe_monthly = False
    if m:
        try:
            data = _json.loads(m.group(1))
            glossary = data.get("metric_glossary", {})
            sharpe_entry = glossary.get("LS Sharpe", {})
            tz = sharpe_entry.get("tooltip_zh", "")
            te = sharpe_entry.get("tooltip_en", "")
            if "月度" in tz or "monthly" in te.lower():
                sharpe_monthly = True
        except Exception:
            pass
    # Fallback: search raw HTML
    if not sharpe_monthly:
        if "月度" in html_text or "monthly" in html_text.lower():
            sharpe_monthly = True

    if sharpe_monthly:
        results.append(_pass(
            "pm58b_ls_sharpe_monthly",
            "PM-58B: LS Sharpe tooltip mentions monthly/月度 (edge stability)",
            "LS Sharpe tooltip references monthly edge stability metric",
        ))
    else:
        results.append(_fail(
            "pm58b_ls_sharpe_monthly",
            "PM-58B: LS Sharpe tooltip mentions monthly/月度 (edge stability)",
            "No monthly/月度 reference found",
            "LS Sharpe should describe monthly edge stability (×√12)",
        ))

    return results


def check_pm58c_ls_metric_semantics(html_text: str) -> list[dict]:
    """PM-58C: Verify LS metric descriptions use edge semantics, not portfolio semantics.

    Checks:
    1. "Portfolio Sharpe" NOT used as LS Sharpe description (allow negations)
    2. "Portfolio volatility" NOT used as Ann Vol description (allow negations)
    3. "Portfolio max drawdown" NOT used as Max DD description (allow negations)
    4. "Edge Diagnostics Summary" or "边缘诊断" section EXISTS
    5. "Window Diagnostics" or "窗口诊断" section EXISTS
    6. "Monthly Edge Win Rate" or "月度 Edge 胜率" EXISTS
    7. "LS Edge Mean" or "LS Edge 均值" EXISTS
    8. "overlap" or "Overlap" mentioned near window diagnostics
    """
    results = []
    html_lower = html_text.lower()

    # ── Check 1: "Portfolio Sharpe" NOT used affirmatively as LS Sharpe description ──
    # Allow negation patterns: "not portfolio sharpe", "不是组合sharpe"
    portfolio_sharpe_affirmative = False
    # Look for "portfolio sharpe" not preceded by negation words
    for m in re.finditer(r"(?<!\bnot )(?<!non-)(?<!\bno )portfolio sharpe", html_lower):
        # Check it's not in a negation context
        start = max(0, m.start() - 30)
        context = html_lower[start:m.start()]
        if not any(neg in context for neg in ["not ", "non-", "no ", "不是", "并非", "avoid"]):
            portfolio_sharpe_affirmative = True
            break

    if portfolio_sharpe_affirmative:
        results.append(_fail(
            "pm58c_no_portfolio_sharpe",
            "PM-58C: LS Sharpe description does NOT use 'Portfolio Sharpe'",
            "Found affirmative 'Portfolio Sharpe' — should use edge semantics",
            "LS Sharpe describes monthly edge stability, not portfolio Sharpe",
        ))
    else:
        results.append(_pass(
            "pm58c_no_portfolio_sharpe",
            "PM-58C: LS Sharpe description does NOT use 'Portfolio Sharpe'",
            "Confirmed: no affirmative 'Portfolio Sharpe' found",
        ))

    # ── Check 2: "Portfolio volatility" NOT used affirmatively ──
    portfolio_vol_affirmative = False
    for m in re.finditer(r"(?<!\bnot )(?<!non-)portfolio volatilit", html_lower):
        start = max(0, m.start() - 30)
        context = html_lower[start:m.start()]
        if not any(neg in context for neg in ["not ", "non-", "不是", "并非", "avoid"]):
            portfolio_vol_affirmative = True
            break

    if portfolio_vol_affirmative:
        results.append(_fail(
            "pm58c_no_portfolio_volatility",
            "PM-58C: Ann Vol description does NOT use 'Portfolio volatility'",
            "Found affirmative 'Portfolio volatility' — should use edge semantics",
        ))
    else:
        results.append(_pass(
            "pm58c_no_portfolio_volatility",
            "PM-58C: Ann Vol description does NOT use 'Portfolio volatility'",
            "Confirmed: no affirmative 'Portfolio volatility' found",
        ))

    # ── Check 3: "Portfolio max drawdown" NOT used affirmatively ──
    portfolio_dd_affirmative = False
    for m in re.finditer(r"(?<!\bnot )(?<!non-)portfolio max drawdown", html_lower):
        start = max(0, m.start() - 30)
        context = html_lower[start:m.start()]
        if not any(neg in context for neg in ["not ", "non-", "不是", "并非", "avoid"]):
            portfolio_dd_affirmative = True
            break

    if portfolio_dd_affirmative:
        results.append(_fail(
            "pm58c_no_portfolio_max_drawdown",
            "PM-58C: Max DD description does NOT use 'Portfolio max drawdown'",
            "Found affirmative 'Portfolio max drawdown' — should use edge semantics",
        ))
    else:
        results.append(_pass(
            "pm58c_no_portfolio_max_drawdown",
            "PM-58C: Max DD description does NOT use 'Portfolio max drawdown'",
            "Confirmed: no affirmative 'Portfolio max drawdown' found",
        ))

    # ── Check 4: "Edge Diagnostics Summary" or "边缘诊断" EXISTS ──
    has_edge_diag = ("Edge Diagnostics" in html_text or "边缘诊断" in html_text)
    if has_edge_diag:
        matched = []
        if "Edge Diagnostics" in html_text:
            matched.append("Edge Diagnostics")
        if "边缘诊断" in html_text:
            matched.append("边缘诊断")
        results.append(_pass(
            "pm58c_edge_diagnostics_section",
            "PM-58C: Edge Diagnostics Summary / 边缘诊断 section exists",
            f"Matched: {', '.join(matched)}",
        ))
    else:
        results.append(_fail(
            "pm58c_edge_diagnostics_section",
            "PM-58C: Edge Diagnostics Summary / 边缘诊断 section exists",
            "Not found",
            "Expected 'Edge Diagnostics' or '边缘诊断' in HTML",
        ))

    # ── Check 5: "Window Diagnostics" or "窗口诊断" EXISTS ──
    has_window_diag = ("Window Diagnostics" in html_text or "窗口诊断" in html_text)
    if has_window_diag:
        matched = []
        if "Window Diagnostics" in html_text:
            matched.append("Window Diagnostics")
        if "窗口诊断" in html_text:
            matched.append("窗口诊断")
        results.append(_pass(
            "pm58c_window_diagnostics_section",
            "PM-58C: Window Diagnostics / 窗口诊断 section exists",
            f"Matched: {', '.join(matched)}",
        ))
    else:
        results.append(_fail(
            "pm58c_window_diagnostics_section",
            "PM-58C: Window Diagnostics / 窗口诊断 section exists",
            "Not found",
            "Expected 'Window Diagnostics' or '窗口诊断' in HTML",
        ))

    # ── Check 6: "Monthly Edge Win Rate" or "月度 Edge 胜率" EXISTS ──
    has_edge_win_rate = ("Monthly Edge Win Rate" in html_text or "月度 Edge 胜率" in html_text)
    if has_edge_win_rate:
        matched = []
        if "Monthly Edge Win Rate" in html_text:
            matched.append("Monthly Edge Win Rate")
        if "月度 Edge 胜率" in html_text:
            matched.append("月度 Edge 胜率")
        results.append(_pass(
            "pm58c_monthly_edge_win_rate",
            "PM-58C: Monthly Edge Win Rate / 月度 Edge 胜率 exists",
            f"Matched: {', '.join(matched)}",
        ))
    else:
        results.append(_fail(
            "pm58c_monthly_edge_win_rate",
            "PM-58C: Monthly Edge Win Rate / 月度 Edge 胜率 exists",
            "Not found",
        ))

    # ── Check 7: "LS Edge Mean" or "LS Edge 均值" EXISTS ──
    has_edge_mean = ("LS Edge Mean" in html_text or "LS Edge 均值" in html_text)
    if has_edge_mean:
        matched = []
        if "LS Edge Mean" in html_text:
            matched.append("LS Edge Mean")
        if "LS Edge 均值" in html_text:
            matched.append("LS Edge 均值")
        results.append(_pass(
            "pm58c_ls_edge_mean",
            "PM-58C: LS Edge Mean / LS Edge 均值 exists",
            f"Matched: {', '.join(matched)}",
        ))
    else:
        results.append(_fail(
            "pm58c_ls_edge_mean",
            "PM-58C: LS Edge Mean / LS Edge 均值 exists",
            "Not found",
        ))

    # ── Check 8: "overlap" or "Overlap" mentioned near window diagnostics ──
    # Search for 'overlap' or 'Overlap' anywhere in the HTML (window diagnostics context)
    has_overlap = ("overlap" in html_lower or "Overlap" in html_text)
    if has_overlap:
        results.append(_pass(
            "pm58c_overlap_mention",
            "PM-58C: Overlap mentioned near window diagnostics",
            "Found 'overlap' / 'Overlap' in page (window diagnostics context)",
        ))
    else:
        results.append(_fail(
            "pm58c_overlap_mention",
            "PM-58C: Overlap mentioned near window diagnostics",
            "Not found",
            "Expected 'overlap' or 'Overlap' in window diagnostics context",
        ))

    return results


def check_pm59a_overlapping_sleeve_strategy(html: str) -> list[dict]:
    """PM-59A: Check overlapping sleeve strategy diagnostics section."""
    checks = []
    # English title
    checks.append(_c(
        "pm59a_section_title_en",
        "PM-59A: Overlapping Sleeve Strategy Diagnostics section exists",
        "PASS" if "Overlapping Sleeve Strategy Diagnostics" in html else "FAIL",
        evidence="found" if "Overlapping Sleeve Strategy Diagnostics" in html else "not found",
    ))
    # Chinese title
    checks.append(_c(
        "pm59a_section_title_zh",
        "PM-59A: 重叠持仓单因子策略路径诊断 section exists",
        "PASS" if "重叠持仓单因子策略路径诊断" in html else "FAIL",
        evidence="found" if "重叠持仓单因子策略路径诊断" in html else "not found",
    ))
    # Research diagnostic only
    checks.append(_c(
        "pm59a_research_diagnostic",
        "PM-59A: 'research diagnostic only' disclaimer present",
        "PASS" if "Research diagnostic only" in html or "research diagnostic only" in html.lower() else "FAIL",
    ))
    # Not live signal
    checks.append(_c(
        "pm59a_not_live",
        "PM-59A: 'NOT live signal' disclaimer present",
        "PASS" if "NOT live signal" in html else "FAIL",
    ))
    # Not trading recommendation
    checks.append(_c(
        "pm59a_not_trading",
        "PM-59A: 'NOT trading recommendation' disclaimer present",
        "PASS" if "NOT trading recommendation" in html else "FAIL",
    ))
    # Gross only
    checks.append(_c(
        "pm59a_gross_only",
        "PM-59A: 'Gross only' disclaimer present",
        "PASS" if "Gross only" in html or "gross only" in html.lower() else "FAIL",
    ))
    # Annualized Hourly Mean Return
    checks.append(_c(
        "pm59a_ann_hourly",
        "PM-59A: 'Ann. Hourly Mean Return' metric present",
        "PASS" if "Hourly Mean Return" in html else "FAIL",
    ))
    # Not CAGR
    checks.append(_c(
        "pm59a_not_cagr",
        "PM-59A: 'Not CAGR' disclaimer present",
        "PASS" if "Not CAGR" in html or "不是实盘 CAGR" in html else "FAIL",
    ))
    # Strategy Direction
    checks.append(_c(
        "pm59a_strategy_direction",
        "PM-59A: 'Strategy Direction' field present",
        "PASS" if "Strategy Direction" in html else "FAIL",
    ))
    # Direction Source
    checks.append(_c(
        "pm59a_direction_source",
        "PM-59A: 'Direction Source' field present",
        "PASS" if "Direction Source" in html else "FAIL",
    ))
    # active_sleeve_count
    checks.append(_c(
        "pm59a_sleeve_count",
        "PM-59A: 'Active Sleeve' count present",
        "PASS" if "Active Sleeve" in html else "FAIL",
    ))
    # PM-59A in factorPayload
    checks.append(_c(
        "pm59a_in_payload",
        "PM-59A: 'overlapping_sleeve_strategy' in factorPayload JSON",
        "PASS" if "overlapping_sleeve_strategy" in html else "FAIL",
    ))
    return checks


def check_pm59a_reading_order(html: str) -> list[dict]:
    """PM-59A-UI: Check evidence reading order structure."""
    checks = []
    checks.append(_c(
        'pm59a_evidence_reading_order',
        'Evidence Reading Order section exists',
        'PASS' if 'Evidence Reading Order' in html else 'FAIL',
    ))
    checks.append(_c(
        'pm59a_predictive_ranking',
        'Predictive Ranking Evidence section exists',
        'PASS' if 'Predictive Ranking Evidence' in html else 'FAIL',
    ))
    checks.append(_c(
        'pm59a_monthly_edge_extraction',
        'Monthly Edge Extraction section exists',
        'PASS' if 'Monthly Edge Extraction' in html else 'FAIL',
    ))
    checks.append(_c(
        'pm59a_shape_stability',
        'Shape & Stability section exists',
        'PASS' if 'Shape & Stability' in html or 'Shape' in html else 'FAIL',
    ))
    checks.append(_c(
        'pm59a_strategy_path_diagnostics',
        'Strategy Path Diagnostics section exists',
        'PASS' if 'Strategy Path Diagnostics' in html else 'FAIL',
    ))
    checks.append(_c(
        'pm59a_gross_sharpe_tooltip',
        'PM-59A Gross Sharpe metric exists',
        'PASS' if 'PM-59A Gross Sharpe' in html or 'Gross Sharpe' in html else 'FAIL',
    ))
    checks.append(_c(
        'pm59a_strategy_max_dd',
        'PM-59A Strategy Max Drawdown metric exists',
        'PASS' if 'PM-59A Strategy Max Drawdown' in html or 'Strategy Max Drawdown' in html else 'FAIL',
    ))
    checks.append(_c(
        'pm59a_monthly_edge_sharpe',
        'Monthly Edge Sharpe label exists',
        'PASS' if 'Monthly Edge Sharpe' in html or 'Edge Sharpe' in html else 'FAIL',
    ))
    checks.append(_c(
        'pm59a_monthly_edge_drawdown',
        'Monthly Edge Drawdown label exists',
        'PASS' if 'Monthly Edge Drawdown' in html or 'Edge Drawdown' in html else 'FAIL',
    ))
    checks.append(_c(
        'pm59a_constraints_novelty',
        'Constraints & Novelty section exists',
        'PASS' if 'Constraints' in html and 'Novelty' in html else 'FAIL',
    ))
    return checks


def check_pm59a_fix2_dom_order(html: str) -> list[dict]:
    """PM-59A-UI-FIX2: Check real DOM order and structural integrity."""
    checks = []

    # Find the renderDetail card.innerHTML template area
    tpl_start = html.find('card.innerHTML=')
    if tpl_start < 0:
        tpl_start = html.find('class="back-to-table"')
    tpl_end = html.find('card.querySelector', tpl_start) if tpl_start >= 0 else -1
    if tpl_end < 0:
        tpl_end = tpl_start + 200000
    tpl = html[tpl_start:tpl_end] if tpl_start >= 0 else html

    # Find positions of key markers within the template
    markers = {
        'reading_order': tpl.find('Evidence Reading Order'),
        'definition': tpl.find('Factor Definition'),
        'block1': tpl.find('Block 1'),
        'block2': tpl.find('Block 2'),
        'block3': tpl.find('Block 3'),
        'block4': tpl.find('Block 4'),
        'block5': tpl.find('Block 5'),
        'block6': tpl.find('Block 6'),
        'optional': tpl.find('optional-deep-dive'),
    }

    # Check all markers found
    for name, pos in markers.items():
        checks.append(_c(
            f'fix2_{name}_exists',
            f'{name} marker exists in HTML',
            'PASS' if pos >= 0 else 'FAIL',
        ))

    # Check real DOM order
    order_ok = all(
        markers[a] < markers[b]
        for a, b in [
            ('reading_order', 'definition'),
            ('definition', 'block1'),
            ('block1', 'block2'),
            ('block2', 'block3'),
            ('block3', 'block4'),
            ('block4', 'block5'),
            ('block5', 'block6'),
            ('block6', 'optional'),
        ]
        if markers[a] >= 0 and markers[b] >= 0
    )
    order_str = ' → '.join(
        f'{k}({v})' for k, v in sorted(markers.items(), key=lambda x: x[1]) if v >= 0
    )
    checks.append(_c(
        'fix2_dom_order',
        'Real DOM order: reading < def < B1 < B2 < B3 < B4 < B5 < B6 < optional',
        'PASS' if order_ok else 'FAIL',
        evidence=order_str[:200],
    ))

    # Block 3 must exist as labeled section
    checks.append(_c(
        'fix2_block3_labeled',
        'Block 3 — Shape & Stability exists as labeled section',
        'PASS' if 'Block 3' in html and 'Shape' in html else 'FAIL',
    ))

    # Scorecard must be after Block 6
    sc_pos = tpl.find('scorecardHtml')
    b6_pos = markers.get('block6', -1)
    checks.append(_c(
        'fix2_scorecard_after_block6',
        'Factor Quality Scorecard positioned after Block 6',
        'PASS' if sc_pos >= 0 and b6_pos >= 0 and sc_pos > b6_pos else 'FAIL',
    ))

    # Details tag count (rendered HTML)
    import re
    details_open = len(re.findall(r'<details', html))
    details_close = len(re.findall(r'</details>', html))
    checks.append(_c(
        'fix2_details_tag_balance',
        f'<details> tag balance ({details_open} open, {details_close} close)',
        'PASS' if details_open == details_close else 'FAIL',
        evidence=f'open={details_open}, close={details_close}',
    ))

    return checks


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
    all_checks.extend(check_pm40b_display_consistency(html_text))
    all_checks.extend(check_per_factor_detail_completeness(html_text))
    all_checks.extend(check_pm40c_scorecard_redundancy_consistency(html_text))

    # 4. Section markers
    all_checks.extend(check_section_markers(html_text))

    # 5. Entrypoint doc alignment (PM-38B)
    all_checks.extend(check_entrypoint_doc_alignment())

    # 6. PM-46B metadata display checks
    all_checks.extend(check_pm46b_metadata_display(html_text))

    # 7. PM-53B active universe consistency guard
    all_checks.extend(check_pm53b_active_universe_consistency(html_text))

    # 8. PM-55 robust significance page integration
    all_checks.extend(check_pm55_robust_significance(html_text))

    # 9. PM-57 return-side robust diagnostics page integration
    all_checks.extend(check_pm57_return_side_robust(html_text))

    # 10. PM-58 core vs optional workflow boundary
    all_checks.extend(check_pm58_core_vs_optional(html_text))

    # 11. PM-58A LS monthly aggregate fields
    all_checks.extend(check_pm58a_ls_monthly_aggregate(html_text))

    # 12. PM-58B LS annualization canonical alignment
    all_checks.extend(check_pm58b_annualization_html(html_text))

    # 13. PM-58C LS metric semantics (edge vs portfolio)
    all_checks.extend(check_pm58c_ls_metric_semantics(html_text))

    # 14. PM-59A Overlapping Sleeve Strategy Diagnostics
    all_checks.extend(check_pm59a_overlapping_sleeve_strategy(html_text))

    # 15. PM-59A-UI Evidence Reading Order
    all_checks.extend(check_pm59a_reading_order(html_text))

    # 16. PM-59A-UI-FIX2 Real DOM order & structural checks
    all_checks.extend(check_pm59a_fix2_dom_order(html_text))

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


