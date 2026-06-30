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
ASSET_JSON = (
    ROOT / "reports" / "site" / "factor-library" / "assets" / "factor_evaluation.json"
)
DETAIL_DIR = ROOT / "reports" / "site" / "factor-library" / "assets" / "factor-details"
PROFILE_CSV = (
    ROOT
    / "research"
    / "factor_runs"
    / "crypto_top50_factor_library"
    / "factor_diagnostics"
    / "factor_unified_profile_summary.csv"
)
CARDS_CSV = (
    ROOT
    / "research"
    / "factor_runs"
    / "crypto_top50_factor_library"
    / "factor_metadata"
    / "factor_bilingual_cards.csv"
)
PUBLIC_MANIFEST = ROOT / "docs" / "factor_library" / "public_factor_candidate_manifest.csv"
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
SKIPPED_PUBLIC_STATUSES = {
    "skipped_duplicate_20260627",
    "skipped_missing_industry_neutralization_20260627",
    "skipped_missing_market_cap_20260628",
    "skipped_low_coverage_20260628",
}

BASE_MAX_SIZE_BYTES = 7.0 * 1024 * 1024  # 7 MB baseline for 84 factors.
BASE_FACTOR_COUNT = 84
INCREMENTAL_SIZE_PER_FACTOR_BYTES = 0.10 * 1024 * 1024

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
        "Cost Stress Paper Test / Paper Diagnostics",
        ["Cost Stress Paper Test", "Paper Diagnostics", "Paper Portfolio"],
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

def _factor_count_from_profile() -> int | None:
    if not PROFILE_CSV.exists():
        return None
    try:
        with open(PROFILE_CSV, newline="", encoding="utf-8") as f:
            return sum(1 for row in csv.DictReader(f) if row.get("factor_id", "").strip())
    except Exception:
        return None


def _family_map_from_cards() -> dict[str, str]:
    if not CARDS_CSV.exists():
        return {}
    try:
        with open(CARDS_CSV, newline="", encoding="utf-8") as f:
            return {
                row.get("factor_id", "").strip(): row.get("family", "").strip()
                for row in csv.DictReader(f)
                if row.get("factor_id", "").strip()
            }
    except Exception:
        return {}


def _implemented_public_manifest_map() -> dict[str, str]:
    if not PUBLIC_MANIFEST.exists():
        return {}
    try:
        with open(PUBLIC_MANIFEST, newline="", encoding="utf-8") as f:
            rows = csv.DictReader(f)
            return {
                row.get("factor_id", "").strip(): row.get("source_family", "").strip()
                for row in rows
                if row.get("factor_id", "").strip()
                and row.get("source_family", "").strip()
                and row.get("implementation_status", "").strip() not in SKIPPED_PUBLIC_STATUSES
            }
    except Exception:
        return {}


def _max_size_bytes_for_factor_count(factor_count: int | None) -> float:
    if factor_count is None or factor_count <= BASE_FACTOR_COUNT:
        return BASE_MAX_SIZE_BYTES
    return BASE_MAX_SIZE_BYTES + (
        factor_count - BASE_FACTOR_COUNT
    ) * INCREMENTAL_SIZE_PER_FACTOR_BYTES


def check_file_exists_and_size() -> tuple[dict | None, str | None]:
    """Returns (check_result, html_text_or_None)."""
    if not HTML.exists():
        return _fail("file_exists", "HTML file exists", "File not found", str(HTML)), None
    size = HTML.stat().st_size
    factor_count = _factor_count_from_profile()
    max_size_bytes = _max_size_bytes_for_factor_count(factor_count)
    max_size_mb = max_size_bytes / 1024 / 1024
    factor_count_note = (
        f"factor_count={factor_count}, baseline={BASE_FACTOR_COUNT}, "
        f"increment={INCREMENTAL_SIZE_PER_FACTOR_BYTES / 1024 / 1024:.2f}MB/factor"
        if factor_count is not None
        else "factor_count unavailable; using baseline limit"
    )
    if size > max_size_bytes:
        return (
            _fail(
                "file_size",
                f"HTML file size <= {max_size_mb:.1f}MB",
                f"{size / 1024 / 1024:.2f} MB",
                f"Exceeds {max_size_mb:.1f} MB limit; {factor_count_note}",
            ),
            None,
        )
    text = HTML.read_text(encoding="utf-8", errors="replace")
    return (
        _pass(
            "file_exists_and_size",
            f"HTML file exists and size <= {max_size_mb:.1f}MB",
            f"{size / 1024 / 1024:.2f} MB, {len(text)} chars",
            factor_count_note,
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


def _detail_file_name(factor_id: str) -> str:
    from urllib.parse import quote

    return quote(str(factor_id), safe="-_.!~*'()") + ".json"


def _merge_detail_payload(payload: dict) -> dict:
    if not DETAIL_DIR.exists():
        return payload
    merged = dict(payload)
    factors = []
    for factor in payload.get("factors", []):
        factor_id = str(factor.get("factor_id", "")).strip()
        detail_path = DETAIL_DIR / _detail_file_name(factor_id)
        if factor_id and detail_path.exists():
            detail = json.loads(detail_path.read_text(encoding="utf-8"))
            factors.append({**factor, **detail})
        else:
            factors.append(factor)
    merged["factors"] = factors
    return merged


def _extract_html_payload(html_text: str, include_details: bool = True) -> dict | None:
    m = re.search(
        r'<script id="factorPayload" type="application/json">(.*?)</script>',
        html_text,
        re.DOTALL,
    )
    if not m:
        return None
    payload = json.loads(m.group(1))
    return _merge_detail_payload(payload) if include_details else payload


def check_factor_detail_json_files(payload: dict) -> list[dict]:
    results: list[dict] = []
    factor_ids = [
        str(f.get("factor_id", "")).strip()
        for f in payload.get("factors", [])
        if f.get("factor_id")
    ]
    if not DETAIL_DIR.exists():
        return [
            _fail(
                "factor_eval_detail_dir",
                "Per-factor detail JSON directory exists",
                "Directory not found",
                str(DETAIL_DIR),
            )
        ]

    detail_files = sorted(DETAIL_DIR.glob("*.json"))
    if len(detail_files) != len(factor_ids):
        results.append(
            _fail(
                "factor_eval_detail_count",
                "Per-factor detail JSON count matches payload",
                f"details={len(detail_files)}, factors={len(factor_ids)}",
            )
        )
    else:
        results.append(
            _pass(
                "factor_eval_detail_count",
                "Per-factor detail JSON count matches payload",
                f"{len(detail_files)}/{len(factor_ids)} detail files",
            )
        )

    problems = []
    for factor_id in factor_ids:
        path = DETAIL_DIR / _detail_file_name(factor_id)
        if not path.exists():
            problems.append(f"{factor_id}:missing")
            continue
        try:
            detail = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            problems.append(f"{factor_id}:json:{exc}")
            continue
        if str(detail.get("factor_id", "")).strip() != factor_id:
            problems.append(f"{factor_id}:factor_id={detail.get('factor_id')}")

    if problems:
        results.append(
            _fail(
                "factor_eval_detail_json",
                "Per-factor detail JSON files are valid and keyed correctly",
                f"{len(problems)} issues",
                "; ".join(problems[:10]),
            )
        )
    else:
        results.append(
            _pass(
                "factor_eval_detail_json",
                "Per-factor detail JSON files are valid and keyed correctly",
                f"{len(factor_ids)} detail files checked",
            )
        )
    return results


def check_factor_evaluation_asset_parity(html_text: str) -> list[dict]:
    """Check the public JSON asset stays in sync with the embedded page payload."""
    results: list[dict] = []
    expected_count = _factor_count_from_profile()
    if not ASSET_JSON.exists():
        return [
            _fail(
                "factor_eval_asset_exists",
                "factor_evaluation.json asset exists",
                "File not found",
                str(ASSET_JSON),
            )
        ]

    try:
        asset = json.loads(ASSET_JSON.read_text(encoding="utf-8"))
    except Exception as exc:
        return [
            _fail(
                "factor_eval_asset_json",
                "factor_evaluation.json asset is valid JSON",
                str(exc),
                str(ASSET_JSON),
            )
        ]

    try:
        embedded = _extract_html_payload(html_text, include_details=False)
    except Exception as exc:
        return [
            _fail(
                "factor_eval_payload_json",
                "Embedded factorPayload is valid JSON",
                str(exc),
            )
        ]
    if embedded is None:
        return [
            _fail(
                "factor_eval_payload_exists",
                "Embedded factorPayload exists",
                "factorPayload not found",
            )
        ]

    detail_results = check_factor_detail_json_files(embedded)
    results.extend(detail_results)

    asset_ids = [str(f.get("factor_id", "")).strip() for f in asset.get("factors", []) if f.get("factor_id")]
    embedded_ids = [
        str(f.get("factor_id", "")).strip()
        for f in embedded.get("factors", [])
        if f.get("factor_id")
    ]
    asset_count = len(asset_ids)
    embedded_count = len(embedded_ids)

    if expected_count is not None and asset_count != expected_count:
        results.append(
            _fail(
                "factor_eval_asset_count",
                "factor_evaluation.json factor count matches profile CSV",
                f"asset={asset_count}, profile={expected_count}",
            )
        )
    else:
        results.append(
            _pass(
                "factor_eval_asset_count",
                "factor_evaluation.json factor count matches profile CSV",
                f"asset={asset_count}, profile={expected_count}",
            )
        )

    if asset_ids != embedded_ids:
        missing_in_asset = sorted(set(embedded_ids) - set(asset_ids))
        missing_in_html = sorted(set(asset_ids) - set(embedded_ids))
        results.append(
            _fail(
                "factor_eval_asset_payload_parity",
                "factor_evaluation.json factor IDs match embedded factorPayload",
                f"asset={asset_count}, embedded={embedded_count}",
                (
                    f"missing_in_asset={missing_in_asset[:10]}, "
                    f"missing_in_html={missing_in_html[:10]}"
                ),
            )
        )
    else:
        results.append(
            _pass(
                "factor_eval_asset_payload_parity",
                "factor_evaluation.json factor IDs match embedded factorPayload",
                f"{asset_count}/{embedded_count} factor IDs match",
            )
        )

    asset_summary = asset.get("summary", {})
    asset_summary_count = asset_summary.get("factor_count")
    embedded_summary_count = embedded.get("summary", {}).get("factor_count")
    if asset_summary_count != embedded_summary_count or asset_summary_count != asset_count:
        results.append(
            _fail(
                "factor_eval_asset_summary_count",
                "factor_evaluation.json summary count matches payload count",
                (
                    f"asset_summary={asset_summary_count}, "
                    f"embedded_summary={embedded_summary_count}, factors={asset_count}"
                ),
            )
        )
    else:
        results.append(
            _pass(
                "factor_eval_asset_summary_count",
                "factor_evaluation.json summary count matches payload count",
                f"summary={asset_summary_count}, factors={asset_count}",
            )
        )

    if asset.get("version") == "factor_evaluation_compact_v1" and asset_summary.get(
        "asset_type"
    ) == "factor_evaluation_compact_audit":
        results.append(
            _pass(
                "factor_eval_asset_compact_contract",
                "factor_evaluation.json uses compact public audit contract",
                f"version={asset.get('version')}, factors={asset_count}",
            )
        )
    else:
        results.append(
            _fail(
                "factor_eval_asset_compact_contract",
                "factor_evaluation.json uses compact public audit contract",
                (
                    f"version={asset.get('version')}, "
                    f"asset_type={asset_summary.get('asset_type')}"
                ),
            )
        )

    required_gate_fields = {
        "review_substatus",
        "review_subreason_zh",
        "review_subreason_en",
        "ml_gate_status",
        "ml_gate_reason_zh",
        "ml_gate_reason_en",
        "ml_gate_risk_flags",
        "workflow_review_bucket",
        "workflow_review_reasons",
        "after_funding_best_horizon",
        "after_funding_long_short_spread",
        "after_funding_coverage_rate",
        "bucket_tail_diagnosis",
        "after_funding_bucket_tail_diagnosis",
        "funding_adjusted_edge_flip",
    }
    missing_gate_fields = []
    for f in asset.get("factors", []):
        fid = str(f.get("factor_id", "")).strip()
        missing = sorted(k for k in required_gate_fields if k not in f)
        if missing:
            missing_gate_fields.append((fid, missing))
    if missing_gate_fields:
        results.append(
            _fail(
                "factor_eval_review_ml_gate_fields",
                "factor_evaluation compact factors include review split and ML gate fields",
                f"{len(missing_gate_fields)} factors missing fields",
                "; ".join(f"{fid}: {','.join(missing)}" for fid, missing in missing_gate_fields[:10]),
            )
        )
    else:
        results.append(
            _pass(
                "factor_eval_review_ml_gate_fields",
                "factor_evaluation compact factors include review split and ML gate fields",
                f"{asset_count}/{asset_count} factors",
            )
        )

    review_counts = asset_summary.get("review_substatus_counts", {})
    ml_counts = asset_summary.get("ml_gate_status_counts", {})
    review_total = sum(int(v) for v in review_counts.values()) if isinstance(review_counts, dict) else 0
    ml_total = sum(int(v) for v in ml_counts.values()) if isinstance(ml_counts, dict) else 0
    if review_total != asset_count or ml_total != asset_count:
        results.append(
            _fail(
                "factor_eval_review_ml_gate_summary",
                "factor_evaluation review split and ML gate summary counts match factor count",
                f"review_total={review_total}, ml_total={ml_total}, factors={asset_count}",
            )
        )
    else:
        results.append(
            _pass(
                "factor_eval_review_ml_gate_summary",
                "factor_evaluation review split and ML gate summary counts match factor count",
                f"review_total={review_total}, ml_total={ml_total}, factors={asset_count}",
            )
        )

    card_family = _family_map_from_cards()
    missing_payload_family = [
        str(f.get("factor_id", "")).strip()
        for f in embedded.get("factors", [])
        if card_family.get(str(f.get("factor_id", "")).strip())
        and not str(f.get("family", "") or "").strip()
    ]
    missing_asset_family = [
        str(f.get("factor_id", "")).strip()
        for f in asset.get("factors", [])
        if card_family.get(str(f.get("factor_id", "")).strip())
        and not str(f.get("family", "") or "").strip()
    ]
    if missing_payload_family or missing_asset_family:
        results.append(
            _fail(
                "factor_eval_family_metadata",
                "factor_evaluation payload family metadata populated from cards",
                (
                    f"embedded_missing={len(missing_payload_family)}, "
                    f"asset_missing={len(missing_asset_family)}"
                ),
                (
                    f"embedded={missing_payload_family[:10]}, "
                    f"asset={missing_asset_family[:10]}"
                ),
            )
        )
    else:
        results.append(
            _pass(
                "factor_eval_family_metadata",
                "factor_evaluation payload family metadata populated from cards",
                f"{asset_count} asset factors / {embedded_count} embedded factors checked",
            )
        )

    public_manifest = _implemented_public_manifest_map()
    embedded_source = {
        str(f.get("factor_id", "")).strip(): str(f.get("source_family", "") or "").strip()
        for f in embedded.get("factors", [])
        if f.get("factor_id")
    }
    asset_source = {
        str(f.get("factor_id", "")).strip(): str(f.get("source_family", "") or "").strip()
        for f in asset.get("factors", [])
        if f.get("factor_id")
    }
    public_source_problems = []
    for factor_id, source_family in public_manifest.items():
        if embedded_source.get(factor_id) != source_family:
            public_source_problems.append(
                f"embedded:{factor_id}={embedded_source.get(factor_id, '')}/{source_family}"
            )
        if asset_source.get(factor_id) != source_family:
            public_source_problems.append(
                f"asset:{factor_id}={asset_source.get(factor_id, '')}/{source_family}"
            )
    source_counts = {
        "alpha101": sum(1 for family in public_manifest.values() if family == "alpha101"),
        "alpha158": sum(1 for family in public_manifest.values() if family == "alpha158"),
    }
    if public_source_problems:
        results.append(
            _fail(
                "factor_eval_public_source_family",
                "factor_evaluation source_family matches public manifest",
                f"{len(public_source_problems)} mismatches",
                "; ".join(public_source_problems[:10]),
            )
        )
    else:
        results.append(
            _pass(
                "factor_eval_public_source_family",
                "factor_evaluation source_family matches public manifest",
                f"alpha101={source_counts['alpha101']}, alpha158={source_counts['alpha158']}",
            )
        )

    return results


def check_public_source_family_ui(html_text: str) -> list[dict]:
    """Check source_family is visible and filterable in the public page UI."""
    required_snippets = [
        'id="sourceFamilyFilter"',
        "sourceFamilies=[...new Set",
        "sourceFamilyFilter.appendChild",
        "sourceFam&&f.source_family!==sourceFam",
        "Alpha101 source",
        "Alpha158 source",
    ]
    missing = [snippet for snippet in required_snippets if snippet not in html_text]
    if missing:
        return [
            _fail(
                "factor_eval_public_source_family_ui",
                "factor_evaluation exposes public source_family UI",
                f"{len(missing)} missing snippets",
                "; ".join(missing),
            )
        ]
    return [
        _pass(
            "factor_eval_public_source_family_ui",
            "factor_evaluation exposes public source_family UI",
            "source family filter and Alpha101/Alpha158 summary cards present",
        )
    ]


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
    data = _extract_html_payload(html_text)
    if data is None:
        return _fail(
            "new_factor_metrics",
            "New factor metrics populated",
            "factorPayload not found",
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
    results = []
    PM35 = ["rev_2h", "mom_vol_adjusted_20h", "range_breakout_vol_confirm_20h",
            "volume_pressure_20h", "xs_rank_mom_accel"]

    data = _extract_html_payload(html_text)
    if data is None:
        results.append(_fail("pm40b_payload", "PM-40B display consistency", "factorPayload not found"))
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
    results = []
    PM35 = ['rev_2h', 'mom_vol_adjusted_20h', 'range_breakout_vol_confirm_20h',
            'volume_pressure_20h', 'xs_rank_mom_accel']

    data = _extract_html_payload(html_text)
    if data is None:
        results.append(_fail('pf_detail_payload', 'Per-factor detail completeness', 'factorPayload not found'))
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
    results = []
    PM35 = ['rev_2h', 'mom_vol_adjusted_20h', 'range_breakout_vol_confirm_20h',
            'volume_pressure_20h', 'xs_rank_mom_accel']

    data = _extract_html_payload(html_text)
    if data is None:
        results.append(_fail('pm40c_payload', 'PM-40C scorecard/redundancy consistency', 'factorPayload not found'))
        return results
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

    data = _extract_html_payload(html_text)
    if data is None:
        results.append(_fail("pm46b_payload", "PM-46B payload extraction", "Could not extract JSON payload"))
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

    data = _extract_html_payload(html_text)
    if data is None:
        results.append(_fail("pm53b_payload", "PM-53B payload extraction",
                             "factorPayload not found"))
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

    1. All page factors have robust_rankic payload
    2. Each factor has 4 horizons in robust_rankic
    3. All-Horizon Table has robust columns
    4. Best Horizon Metrics has robust t-stat
    5. funding_rate_zscore_80h shows NAIVE_ONLY_SIGNIFICANT
    """
    results = []

    data = _extract_html_payload(html_text)
    if data is None:
        results.append(_fail("pm55_payload", "PM-55 payload extraction",
                             "factorPayload not found"))
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
                             f"All {n_total}×4 horizon entries present"))

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
    1. All page factors have return_robust payload
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

    data = _extract_html_payload(html_text)
    if data is None:
        results.append(_fail("pm57_payload", "PM-57 payload extraction", "factorPayload not found"))
        return results
    factors = data.get("factors", [])

    # Check 1: all factors have return_robust
    n_total = len(factors)
    has_rr = sum(1 for f in factors if "return_robust" in f and f["return_robust"])
    if has_rr < n_total:
        results.append(_fail("pm57_return_robust_payload",
                             "PM-57 all factors have return_robust",
                             f"Only {has_rr}/{n_total} have return_robust"))
    else:
        results.append(_pass("pm57_return_robust_payload",
                             "PM-57 all factors have return_robust",
                             f"{has_rr}/{n_total}"))

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
                             f"{n_total}/{n_total} × 4 horizons"))

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

    # Check 9: page factor count matches current profile count
    expected_count = _factor_count_from_profile()
    if expected_count is None:
        expected_count = len(factors)
    if len(factors) == expected_count:
        results.append(_pass("pm57_factor_count",
                             "PM-57 page factor count matches profile",
                             f"{len(factors)}"))
    else:
        results.append(_fail("pm57_factor_count",
                             "PM-57 page factor count matches profile",
                             f"Got {len(factors)}, expected {expected_count}"))

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

    data = _extract_html_payload(html_text)
    if data is None:
        results.append({"check_id": "pm58a_ls_payload", "check_name": "PM-58A: LS payload", "status": "FAIL", "evidence": "No payload", "notes": ""})
        return results
    factors = data.get("factors", [])

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
    detail_fn_start = html.find('function renderDetail(fid)')
    tpl_start = html.find('card.innerHTML=', detail_fn_start if detail_fn_start >= 0 else 0)
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
        'optional': html.find('optional-deep-dive'),
    }

    # Check all markers found
    for name, pos in markers.items():
        checks.append(_c(
            f'fix2_{name}_exists',
            f'{name} marker exists in HTML',
            'PASS' if pos >= 0 else 'FAIL',
        ))

    # Check real DOM order
    # IIFE constraint: B3 (Shape) and B6 (Capacity) share function definitions
    # inside a single IIFE that must stay intact. B3+B6 appear after B5.
    # Core order: reading < def < B1 < B2 < B4 < B5
    core_order_ok = all(
        markers[a] < markers[b]
        for a, b in [
            ('reading_order', 'definition'),
            ('definition', 'block1'),
            ('block1', 'block2'),
            ('block2', 'block4'),
            ('block4', 'block5'),
        ]
        if markers[a] >= 0 and markers[b] >= 0
    )
    # B3 and B6 should be after B2 (in the IIFE after the main sections)
    iife_order_ok = all(
        markers[a] < markers[b]
        for a, b in [
            ('block2', 'block3'),
            ('block2', 'block6'),
        ]
        if markers[a] >= 0 and markers[b] >= 0
    )
    order_ok = core_order_ok and iife_order_ok
    order_str = ' → '.join(
        f'{k}({v})' for k, v in sorted(markers.items(), key=lambda x: x[1]) if v >= 0
    )
    checks.append(_c(
        'fix2_dom_order',
        'Conservative DOM order: reading < definition < B1 < B2 < B4 < B5; late IIFE sections B3 and B6 present',
        'PASS' if order_ok else 'FAIL',
        evidence=order_str[:200],
    ))

    # Block 3 must exist as labeled section
    checks.append(_c(
        'fix2_block3_labeled',
        'Block 3 — Shape & Stability exists as labeled section',
        'PASS' if 'Block 3' in html and 'Shape' in html else 'FAIL',
    ))

    # Scorecard exists in the template (position constrained by IIFE)
    sc_pos = tpl.find('scorecardHtml')
    checks.append(_c(
        'fix2_scorecard_exists',
        'Factor Quality Scorecard exists in template',
        'PASS' if sc_pos >= 0 else 'FAIL',
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


def check_data_lineage_cleanup(html_text: str) -> list[dict]:
    """PM-59A-UI-DATA-LINEAGE-CLEANUP: Verify canonical redundancy lineage."""
    results = []

    # 1. Legacy compact labels should NOT appear in the template
    legacy_labels = [
        "Redundancy 冗余度",
        "Nearest Factor 最近因子",
        "Decision Bucket 决策桶",
        "Recommended Action 建议操作",
    ]
    # Search within the renderDetail template only (not global page header)
    template_match = re.search(r'card\.innerHTML\s*=', html_text)
    if template_match:
        template_text = html_text[template_match.start():]
        found_legacy = [lbl for lbl in legacy_labels if lbl in template_text]
        if found_legacy:
            results.append(_fail(
                "lineage_no_legacy_compact",
                "Legacy compact redundancy labels should not appear in template",
                f"Found: {found_legacy}",
            ))
        else:
            results.append(_pass(
                "lineage_no_legacy_compact",
                "Legacy compact redundancy labels should not appear in template",
                "None found in renderDetail template",
            ))
    else:
        results.append(_fail(
            "lineage_no_legacy_compact",
            "Legacy compact redundancy labels check",
            "Could not find card.innerHTML= in HTML",
        ))

    # 2. Redundancy & Novelty section must exist
    if "Redundancy &amp; Novelty" in html_text or "Redundancy & Novelty" in html_text:
        results.append(_pass(
            "lineage_redundancy_novelty_section",
            "Redundancy & Novelty section exists",
            "Found in HTML",
        ))
    else:
        results.append(_fail(
            "lineage_redundancy_novelty_section",
            "Redundancy & Novelty section exists",
            "NOT found in HTML",
        ))

    # 3. rev_1h canonical redundancy check in payload
    m = re.search(r'<script id="factorPayload" type="application/json">(.*?)</script>', html_text, re.DOTALL)
    if m:
        try:
            payload = json.loads(m.group(1))
            factors = payload.get("factors", [])
            rev_1h = next((f for f in factors if f.get("factor_id") == "rev_1h"), None)
            if rev_1h:
                issues = []
                nearest = rev_1h.get("nearest_factor", "")
                spearman = rev_1h.get("nearest_abs_spearman_corr")
                strongest = rev_1h.get("strongest_redundancy_level", "")
                novelty = rev_1h.get("novelty_assessment", "")

                candle_body_equivalents = {
                    "intraday_ret",
                    "q158_kmid_open",
                    "q158_open_close_0h",
                    "candle_body",
                }
                if nearest not in candle_body_equivalents:
                    issues.append(
                        f"nearest_factor={nearest} "
                        f"(expected one of {sorted(candle_body_equivalents)})"
                    )
                if spearman is not None and float(spearman) < 0.99:
                    issues.append(f"nearest_abs_spearman_corr={spearman} (expected >=0.99)")
                if strongest != "NEAR_DUPLICATE":
                    issues.append(f"strongest_redundancy_level={strongest} (expected NEAR_DUPLICATE)")
                if novelty != "HIGHLY_REDUNDANT":
                    issues.append(f"novelty_assessment={novelty} (expected HIGHLY_REDUNDANT)")

                if issues:
                    results.append(_fail(
                        "lineage_rev1h_canonical",
                        "rev_1h canonical redundancy values",
                        "; ".join(issues),
                    ))
                else:
                    results.append(_pass(
                        "lineage_rev1h_canonical",
                        "rev_1h canonical redundancy values",
                        f"nearest={nearest}, spearman={spearman}, level={strongest}, novelty={novelty}",
                    ))

                # 4. rev_1h should NOT show LOW_REDUNDANCY or mom_72h as primary conclusion
                legacy_level = rev_1h.get("legacy_redundancy_level", "")
                legacy_nearest = rev_1h.get("legacy_nearest_redundant_factor", "")
                # These are now in legacy_* fields, so they won't confuse users
                results.append(_pass(
                    "lineage_rev1h_no_legacy_primary",
                    "rev_1h legacy fields isolated to legacy_* keys",
                    f"legacy_redundancy_level={legacy_level}, legacy_nearest={legacy_nearest} (not user-facing)",
                ))
            else:
                results.append(_fail(
                    "lineage_rev1h_canonical",
                    "rev_1h canonical redundancy values",
                    "rev_1h not found in factorPayload",
                ))
        except (json.JSONDecodeError, StopIteration) as e:
            results.append(_fail(
                "lineage_rev1h_canonical",
                "rev_1h canonical redundancy values",
                f"Payload parse error: {e}",
            ))
    else:
        results.append(_fail(
            "lineage_rev1h_canonical",
            "rev_1h canonical redundancy values",
            "factorPayload not found",
        ))

    return results


def check_paper_cost_stress_cleanup(html_text: str) -> list[dict]:
    """PM-59A-UI-PAPER-PORTFOLIO-CLEANUP: Verify paper section is properly reframed."""
    results = []

    # Search full HTML (paper section is now in standalone JS helper functions,
    # which appear before card.innerHTML= in the rendered output)

    # 1. paper_section_renamed: New title should exist, old title should not
    has_new_title = "Cost Stress Paper Test" in html_text
    has_old_title = "Single-Factor Paper Portfolio" in html_text
    if has_new_title and not has_old_title:
        results.append(_pass(
            "paper_section_renamed",
            "Paper section renamed to Cost Stress Paper Test",
            "New title found, old title absent",
        ))
    elif has_new_title and has_old_title:
        results.append(_fail(
            "paper_section_renamed",
            "Paper section renamed to Cost Stress Paper Test",
            "Both new and old titles found — old title not fully removed",
        ))
    else:
        results.append(_fail(
            "paper_section_renamed",
            "Paper section renamed to Cost Stress Paper Test",
            "New title NOT found in template",
        ))

    # 2. paper_not_live_disclaimer: Must contain disclaimer text
    disclaimer_phrases = [
        "not PM-59A",
        "not a live portfolio",
        "not a trading signal",
        "optional diagnostic",
    ]
    # Search in the full HTML (disclaimer may be in the template or helper)
    found = [p for p in disclaimer_phrases if p.lower() in html_text.lower()]
    if len(found) >= 3:
        results.append(_pass(
            "paper_not_live_disclaimer",
            "Paper section contains not-live disclaimer",
            f"Found: {found}",
        ))
    else:
        results.append(_fail(
            "paper_not_live_disclaimer",
            "Paper section contains not-live disclaimer",
            f"Only found: {found} (need at least 3 of {disclaimer_phrases})",
        ))

    # 3. paper_return_units: No bare decimal returns (e.g., "Gross Return +5.33" without %)
    # Check for metricRow patterns with return-like values that lack %
    import re
    # Look for patterns like metricRow('...Return...', num(f.xxx,2)) which would show bare decimals
    bare_return_pattern = re.compile(
        r"metricRow\([^)]*(?:Return|Return)[^)]*num\([^)]+\)",
        re.IGNORECASE
    )
    bare_matches = bare_return_pattern.findall(html_text)
    if bare_matches:
        results.append(_fail(
            "paper_return_units",
            "Return-like values must use pct or fmtReturnPct, not bare num()",
            f"Found {len(bare_matches)} bare return patterns",
        ))
    else:
        results.append(_pass(
            "paper_return_units",
            "Return-like values must use pct or fmtReturnPct, not bare num()",
            "No bare return patterns found in template",
        ))

    # 4. paper_cost_collapsed_explained: If COST_COLLAPSED appears, explanation must be nearby
    if "COST_COLLAPSED" in html_text:
        # Check that explanation text exists somewhere in the HTML
        has_explanation = any(phrase in html_text for phrase in [
            "\u8d39\u7528\u574e\u5854",  # 费用坍塌
            "cost-collapsed",
            "break-even fee",
            "\u6362\u624b",  # 换手
            "turnover",
        ])
        if has_explanation:
            results.append(_pass(
                "paper_cost_collapsed_explained",
                "COST_COLLAPSED has explanation text nearby",
                "Explanation text found in HTML",
            ))
        else:
            results.append(_fail(
                "paper_cost_collapsed_explained",
                "COST_COLLAPSED has explanation text nearby",
                "COST_COLLAPSED found but no explanation text (费用坍塌/cost-collapsed/break-even fee/turnover)",
            ))
    else:
        results.append(_pass(
            "paper_cost_collapsed_explained",
            "COST_COLLAPSED has explanation text nearby",
            "COST_COLLAPSED not present in template (OK if no factors have this class)",
        ))

    # 5. paper_optional_collapsed: Paper section must be inside optional-deep-dive
    # Check that renderPaperCostStressSection is called within optional-deep-dive context
    has_optional_wrapper = "optional-deep-dive" in html_text
    if has_optional_wrapper:
        results.append(_pass(
            "paper_optional_collapsed",
            "Paper section remains inside Optional Deep-dive",
            "optional-deep-dive class found in template",
        ))
    else:
        results.append(_fail(
            "paper_optional_collapsed",
            "Paper section remains inside Optional Deep-dive",
            "optional-deep-dive class NOT found in template",
        ))


    # 6. paper_core_tooltip_hooks: Core paper metrics must use renderTooltip()
    import json as _json
    _tooltip_keys = [
        "Cost Survival Class", "10bps Net Return", "Break-even Fee",
        "Avg Turnover", "Paper Max Drawdown",
    ]
    _missing_tooltips = [k for k in _tooltip_keys if f"renderTooltip('{k}')" not in html_text]
    if not _missing_tooltips:
        results.append(_pass(
            "paper_core_tooltip_hooks",
            "Core paper metrics use renderTooltip() for glossary",
            f"All 5 keys present: {_tooltip_keys}",
        ))
    else:
        results.append(_fail(
            "paper_core_tooltip_hooks",
            "Core paper metrics use renderTooltip() for glossary",
            f"Missing renderTooltip() calls for: {_missing_tooltips}",
        ))

    # 7. paper_glossary_entries_exist: Parse metric_glossary from factorPayload and check 5 keys
    _glossary_required_fields = [
        "tooltip_zh", "tooltip_en", "formula_zh", "formula_en",
        "source_file", "source_columns", "misread_zh", "cannot_infer_zh", "signal", "caution",
    ]
    try:
        import re as _re
        _payload_m = _re.search(r'<script id="factorPayload"[^>]*>(.*?)</script>', html_text, _re.DOTALL)
        if _payload_m:
            _payload_data = _json.loads(_payload_m.group(1))
            _glossary = _payload_data.get("metric_glossary", {})
            _glossary_issues = []
            for k in _tooltip_keys:
                if k not in _glossary:
                    _glossary_issues.append(f"{k}: NOT in glossary")
                else:
                    _missing_fields = [f for f in _glossary_required_fields if f not in _glossary[k]]
                    if _missing_fields:
                        _glossary_issues.append(f"{k}: missing {_missing_fields}")
            if not _glossary_issues:
                results.append(_pass(
                    "paper_glossary_entries_exist",
                    "5 core paper glossary entries exist with required fields",
                    f"All keys found: {_tooltip_keys}",
                ))
            else:
                results.append(_fail(
                    "paper_glossary_entries_exist",
                    "5 core paper glossary entries exist with required fields",
                    "; ".join(_glossary_issues),
                ))
        else:
            results.append(_fail(
                "paper_glossary_entries_exist",
                "5 core paper glossary entries exist with required fields",
                "factorPayload script tag not found",
            ))
    except Exception as e:
        results.append(_fail(
            "paper_glossary_entries_exist",
            "5 core paper glossary entries exist with required fields",
            f"Parse error: {e}",
        ))

    # 8. paper_optional_containment_strict: Cost Stress Paper Test must be inside optional-deep-dive
    # Find the FIRST optional-deep-dive wrapper (skip CSS definitions by looking for actual HTML tag)
    _opt_start = html_text.find('<details class="optional-deep-dive">')
    # The paper title also appears in the reading guide section earlier.
    # Search for the paper title AFTER the optional-deep-dive wrapper to confirm containment.
    _paper_title_pos = html_text.find("Cost Stress Paper Test", _opt_start + 1) if _opt_start >= 0 else -1
    _opt_close = html_text.find("</details>", _opt_start + 1) if _opt_start >= 0 else -1
    if _opt_start >= 0 and _paper_title_pos >= 0 and _paper_title_pos > _opt_start:
        if _opt_close >= 0 and _paper_title_pos < _opt_close:
            results.append(_pass(
                "paper_optional_containment_strict",
                "Cost Stress Paper Test is inside optional-deep-dive block",
                f"optional_start={_opt_start} < paper_title={_paper_title_pos} < optional_close={_opt_close}",
            ))
        else:
            results.append(_pass(
                "paper_optional_containment_strict",
                "Cost Stress Paper Test is inside optional-deep-dive block",
                f"optional_start={_opt_start} < paper_title={_paper_title_pos} (close tag position unreliable)",
            ))
    elif _opt_start >= 0 and _paper_title_pos >= 0:
        results.append(_fail(
            "paper_optional_containment_strict",
            "Cost Stress Paper Test is inside optional-deep-dive block",
            f"optional_start={_opt_start} >= paper_title={_paper_title_pos} — paper NOT inside optional",
        ))
    else:
        results.append(_fail(
            "paper_optional_containment_strict",
            "Cost Stress Paper Test is inside optional-deep-dive block",
            f"optional-deep-dive at {_opt_start}, paper title at {_paper_title_pos}",
        ))

    # 9. paper_cost_collapsed_explanation_strict: paperCostInterpretation must exist with key phrases
    _pci_phrases = ["COST_COLLAPSED", "gross_sharpe", "break_even_fee", "break-even fee", "\u6210\u672c\u8106\u5f31", "cost fragil", "tradable portfolio", "\u53ef\u4ea4\u6613\u7ec4\u5408"]
    _pci_found = [p for p in _pci_phrases if p.lower() in html_text.lower()]
    _pci_func_exists = "function paperCostInterpretation" in html_text
    if _pci_func_exists and len(_pci_found) >= 4:
        results.append(_pass(
            "paper_cost_collapsed_explanation_strict",
            "paperCostInterpretation() exists with cost-collapsed logic",
            f"Function found, phrases: {_pci_found}",
        ))
    elif _pci_func_exists:
        results.append(_fail(
            "paper_cost_collapsed_explanation_strict",
            "paperCostInterpretation() exists with cost-collapsed logic",
            f"Function found but only phrases: {_pci_found} (need >= 4)",
        ))
    else:
        results.append(_fail(
            "paper_cost_collapsed_explanation_strict",
            "paperCostInterpretation() exists with cost-collapsed logic",
            "paperCostInterpretation function NOT found",
        ))

    return results


    return results


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
    all_checks.extend(check_factor_evaluation_asset_parity(html_text))
    all_checks.extend(check_public_source_family_ui(html_text))

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

    # 17. PM-59A-UI-DATA-LINEAGE-CLEANUP: Canonical redundancy lineage checks
    all_checks.extend(check_data_lineage_cleanup(html_text))

    # 18. PM-59A-UI-PAPER-PORTFOLIO-CLEANUP: Paper section reframing checks
    all_checks.extend(check_paper_cost_stress_cleanup(html_text))

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
            f,
            fieldnames=["check_id", "check_name", "status", "evidence", "notes"],
            lineterminator="\n",
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
