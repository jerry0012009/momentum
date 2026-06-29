#!/usr/bin/env python3
"""Summarize public Alpha101/Alpha158 integration status.

Reads the compact public factor manifest, registry, and factor library state.
This is a reporting/check script only; it does not register factors or compute
factor_values.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "factor_library" / "public_factor_candidate_manifest.csv"
STATE = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_library_state.json"
OUT_DIR = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_diagnostics"
TAXONOMY_SOURCE = ROOT / "data" / "sources" / "crypto_industry_taxonomy_contract_v1" / "symbol_taxonomy.csv"
TAXONOMY_ARTIFACT = ROOT / "data" / "cache" / "crypto_industry_taxonomy_contract_v1" / "symbol_taxonomy.parquet"
TAXONOMY_PACKET_VALIDATION = OUT_DIR / "industry_taxonomy_review_packet_validation.json"
TAXONOMY_PACKET_ROLLUP = OUT_DIR / "industry_taxonomy_review_batch_validation_rollup.json"
TAXONOMY_PACKET_COVERAGE = OUT_DIR / "industry_taxonomy_review_packet_coverage.json"
TAXONOMY_REVIEWED_PACKET_ROLLUP = (
    OUT_DIR
    / "industry_taxonomy_reviewed_packets"
    / "industry_taxonomy_review_batch_validation_rollup.json"
)
CAP_ARTIFACT = ROOT / "data" / "cache" / "crypto_market_cap_1h_contract_v1" / "market_cap_1h_aligned.parquet"
CAP_CONTRACT_CHECK = ROOT / "data" / "cache" / "crypto_market_cap_1h_contract_v1" / "market_cap_contract_check.json"
CAP_QUALITY_REPORT = ROOT / "data" / "cache" / "crypto_market_cap_1h_contract_v1" / "market_cap_quality_report.csv"
SKIPPED_PREFIX = "skipped_"
TAXONOMY_GROUP_COLUMNS = {"sector", "industry", "subindustry"}
CAP_COLUMNS = {"cap"}
SOURCE_CHECK_STATUS_NAMES = [
    "required_columns",
    "quality_flag_domain",
    "has_ok_rows",
    "required_groups_have_ok_rows",
    "symbol_non_empty",
    "symbol_unique",
    "ok_rows_have_valid_known_at",
    "ok_rows_have_valid_effective_from",
    "ok_effective_from_not_after_known_at",
    "ok_rows_known_by_latest_bar",
]

sys.path.insert(0, str(Path(__file__).resolve().parent))
from factor_formula_registry import REGISTRY_BY_ID  # noqa: E402
from check_crypto_industry_taxonomy_contract import check_contract  # noqa: E402
from check_crypto_industry_taxonomy_coverage import DEFAULT_BARS, check_coverage  # noqa: E402
from check_crypto_industry_taxonomy_review_source import summarize_review_source  # noqa: E402


def load_manifest(path: Path = MANIFEST) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def taxonomy_groups_for_row(row: dict[str, str]) -> list[str]:
    """Return required taxonomy group columns for an Alpha101 skipped manifest row."""
    required_columns = {
        col.strip()
        for col in row.get("required_columns", "").split("|")
        if col.strip()
    }
    return sorted(required_columns & TAXONOMY_GROUP_COLUMNS)


def cap_required_for_row(row: dict[str, str]) -> bool:
    """Return whether a skipped row needs the market-cap contract artifact."""
    required_columns = {
        col.strip()
        for col in row.get("required_columns", "").split("|")
        if col.strip()
    }
    return bool(required_columns & CAP_COLUMNS)


def summarize_manifest(rows: list[dict[str, str]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    families = sorted({row["source_family"] for row in rows})
    summary: list[dict[str, object]] = []
    skipped_rows: list[dict[str, object]] = []
    for family in families:
        fam_rows = [row for row in rows if row["source_family"] == family]
        skipped = [row for row in fam_rows if row["implementation_status"].startswith(SKIPPED_PREFIX)]
        accounted = [row for row in fam_rows if not row["implementation_status"].startswith(SKIPPED_PREFIX)]
        registry_missing = [
            row["factor_id"]
            for row in accounted
            if row["factor_id"] not in REGISTRY_BY_ID
        ]
        skipped_in_registry = [
            row["factor_id"]
            for row in skipped
            if row["factor_id"] in REGISTRY_BY_ID
        ]
        summary.append({
            "source_family": family,
            "manifest_total": len(fam_rows),
            "accounted_non_skipped": len(accounted),
            "skipped": len(skipped),
            "registry_missing_non_skipped": len(registry_missing),
            "skipped_present_in_registry": len(skipped_in_registry),
            "registry_missing_ids": "|".join(registry_missing),
            "skipped_present_ids": "|".join(skipped_in_registry),
        })
        for row in skipped:
            taxonomy_groups = taxonomy_groups_for_row(row)
            skipped_rows.append({
                "source_family": family,
                "factor_id": row["factor_id"],
                "implementation_status": row["implementation_status"],
                "skip_reason": row["skip_reason"],
                "required_columns": row["required_columns"],
                "required_ops": row["required_ops"],
                "taxonomy_required_groups": "|".join(taxonomy_groups),
                "taxonomy_blocker": bool(taxonomy_groups),
                "cap_blocker": cap_required_for_row(row),
                "ready_for_unskip": False,
            })
    return summary, skipped_rows


def summarize_registry_guard(family_summary: list[dict[str, object]]) -> dict[str, object]:
    """Summarize manifest-vs-registry guardrails for public factor candidates."""
    registry_missing_ids: list[str] = []
    skipped_present_ids: list[str] = []
    for row in family_summary:
        registry_missing_ids.extend(
            fid for fid in str(row.get("registry_missing_ids", "")).split("|") if fid
        )
        skipped_present_ids.extend(
            fid for fid in str(row.get("skipped_present_ids", "")).split("|") if fid
        )
    return {
        "non_skipped_missing_registry_count": len(registry_missing_ids),
        "non_skipped_missing_registry_ids": "|".join(registry_missing_ids),
        "skipped_present_in_registry_count": len(skipped_present_ids),
        "skipped_present_in_registry_ids": "|".join(skipped_present_ids),
        "pass": not registry_missing_ids and not skipped_present_ids,
    }


def load_state(path: Path = STATE) -> dict[str, object]:
    with path.open() as handle:
        return json.load(handle)


def summarize_taxonomy_packet_validation(path: Path = TAXONOMY_PACKET_VALIDATION) -> dict[str, object]:
    """Return compact status for the current manual taxonomy review packet gate."""
    if not path.exists():
        return {
            "packet_validation_path": str(path),
            "packet_validation_exists": False,
            "packet_validation_pass": False,
            "packet_validation_blocker": "packet_validation_missing",
            "packet_rows": 0,
            "packet_approved_rows": 0,
            "packet_approved_symbols": "",
            "packet_approved_bar_count_share": None,
            "packet_approved_quote_volume_share": None,
            "packet_latest_bar_timestamp": "",
            "packet_allow_no_ok": False,
            "packet_csv": "",
        }
    try:
        payload = json.loads(path.read_text())
    except Exception as exc:
        return {
            "packet_validation_path": str(path),
            "packet_validation_exists": True,
            "packet_validation_pass": False,
            "packet_validation_blocker": f"packet_validation_unreadable:{exc}",
            "packet_rows": 0,
            "packet_approved_rows": 0,
            "packet_approved_symbols": "",
            "packet_approved_bar_count_share": None,
            "packet_approved_quote_volume_share": None,
            "packet_latest_bar_timestamp": "",
            "packet_allow_no_ok": False,
            "packet_csv": "",
        }
    return {
        "packet_validation_path": str(path),
        "packet_validation_exists": True,
        "packet_validation_pass": bool(payload.get("overall_pass", False)),
        "packet_validation_blocker": str(payload.get("blocker", "")),
        "packet_rows": int(payload.get("packet_rows", 0) or 0),
        "packet_approved_rows": int(payload.get("approved_packet_rows", 0) or 0),
        "packet_approved_symbols": str(payload.get("approved_symbols", "")),
        "packet_approved_bar_count_share": payload.get("approved_bar_count_share"),
        "packet_approved_quote_volume_share": payload.get("approved_quote_volume_share"),
        "packet_latest_bar_timestamp": str(payload.get("latest_bar_timestamp", "")),
        "packet_allow_no_ok": bool(payload.get("allow_no_ok", False)),
        "packet_csv": str(payload.get("packet_csv", "")),
    }


def summarize_taxonomy_packet_rollup(
    path: Path = TAXONOMY_PACKET_ROLLUP,
    *,
    prefix: str = "packet_rollup",
) -> dict[str, object]:
    """Return compact status for all batch-specific taxonomy packet validations."""
    if not path.exists():
        return {
            f"{prefix}_path": str(path),
            f"{prefix}_exists": False,
            f"{prefix}_blocker": f"{prefix}_missing",
            f"{prefix}_batch_count": 0,
            f"{prefix}_ready_to_apply_batch_count": 0,
            f"{prefix}_blocked_batch_count": 0,
            f"{prefix}_total_packet_rows": 0,
            f"{prefix}_total_approved_rows": 0,
            f"{prefix}_approved_bar_count_share_sum": None,
            f"{prefix}_approved_quote_volume_share_sum": None,
            f"{prefix}_ready_to_apply_batch_ids": "",
            f"{prefix}_blocked_batch_ids": "",
        }
    try:
        payload = json.loads(path.read_text())
        summary = payload.get("summary", {})
    except Exception as exc:
        return {
            f"{prefix}_path": str(path),
            f"{prefix}_exists": True,
            f"{prefix}_blocker": f"{prefix}_unreadable:{exc}",
            f"{prefix}_batch_count": 0,
            f"{prefix}_ready_to_apply_batch_count": 0,
            f"{prefix}_blocked_batch_count": 0,
            f"{prefix}_total_packet_rows": 0,
            f"{prefix}_total_approved_rows": 0,
            f"{prefix}_approved_bar_count_share_sum": None,
            f"{prefix}_approved_quote_volume_share_sum": None,
            f"{prefix}_ready_to_apply_batch_ids": "",
            f"{prefix}_blocked_batch_ids": "",
        }
    return {
        f"{prefix}_path": str(path),
        f"{prefix}_exists": True,
        f"{prefix}_blocker": "",
        f"{prefix}_batch_count": int(summary.get("batch_report_count", 0) or 0),
        f"{prefix}_ready_to_apply_batch_count": int(summary.get("ready_to_apply_batch_count", 0) or 0),
        f"{prefix}_blocked_batch_count": int(summary.get("blocked_batch_count", 0) or 0),
        f"{prefix}_total_packet_rows": int(summary.get("total_packet_rows", 0) or 0),
        f"{prefix}_total_approved_rows": int(summary.get("total_approved_packet_rows", 0) or 0),
        f"{prefix}_approved_bar_count_share_sum": summary.get("approved_bar_count_share_sum"),
        f"{prefix}_approved_quote_volume_share_sum": summary.get("approved_quote_volume_share_sum"),
        f"{prefix}_ready_to_apply_batch_ids": str(summary.get("ready_to_apply_batch_ids", "")),
        f"{prefix}_blocked_batch_ids": str(summary.get("blocked_batch_ids", "")),
    }


def summarize_taxonomy_packet_coverage(path: Path = TAXONOMY_PACKET_COVERAGE) -> dict[str, object]:
    """Return compact status for review packet set coverage QA."""
    if not path.exists():
        return {
            "packet_coverage_path": str(path),
            "packet_coverage_exists": False,
            "packet_coverage_pass": False,
            "packet_coverage_blocker": "packet_coverage_missing",
            "packet_coverage_candidate_file_count": 0,
            "packet_coverage_file_count": 0,
            "packet_coverage_source_rows": 0,
            "packet_coverage_rows": 0,
            "packet_coverage_unique_symbols": 0,
            "packet_coverage_missing_source_symbols": "",
            "packet_coverage_extra_symbols": "",
            "packet_coverage_duplicate_symbols": "",
        }
    try:
        payload = json.loads(path.read_text())
    except Exception as exc:
        return {
            "packet_coverage_path": str(path),
            "packet_coverage_exists": True,
            "packet_coverage_pass": False,
            "packet_coverage_blocker": f"packet_coverage_unreadable:{exc}",
            "packet_coverage_candidate_file_count": 0,
            "packet_coverage_file_count": 0,
            "packet_coverage_source_rows": 0,
            "packet_coverage_rows": 0,
            "packet_coverage_unique_symbols": 0,
            "packet_coverage_missing_source_symbols": "",
            "packet_coverage_extra_symbols": "",
            "packet_coverage_duplicate_symbols": "",
        }
    return {
        "packet_coverage_path": str(path),
        "packet_coverage_exists": True,
        "packet_coverage_pass": bool(payload.get("overall_pass", False)),
        "packet_coverage_blocker": str(payload.get("blocker", "")),
        "packet_coverage_candidate_file_count": int(payload.get("candidate_file_count", 0) or 0),
        "packet_coverage_file_count": int(payload.get("packet_file_count", 0) or 0),
        "packet_coverage_source_rows": int(payload.get("source_rows", 0) or 0),
        "packet_coverage_rows": int(payload.get("packet_rows", 0) or 0),
        "packet_coverage_unique_symbols": int(payload.get("unique_packet_symbols", 0) or 0),
        "packet_coverage_missing_source_symbols": str(payload.get("missing_source_symbols", "")),
        "packet_coverage_extra_symbols": str(payload.get("extra_packet_symbols", "")),
        "packet_coverage_duplicate_symbols": str(payload.get("duplicate_packet_symbols", "")),
    }


def summarize_taxonomy_group_readiness(
    taxonomy_skipped: list[dict[str, object]],
    review_source: dict[str, object],
) -> list[dict[str, object]]:
    """Return per taxonomy-group unblock status for skipped IndNeutralize rows."""
    ok_groups = {
        group
        for group in str(review_source.get("ok_groups_present", "")).split("|")
        if group
    }
    rows: list[dict[str, object]] = []
    for group in sorted(TAXONOMY_GROUP_COLUMNS):
        factor_ids = sorted(
            str(row["factor_id"])
            for row in taxonomy_skipped
            if group in str(row.get("taxonomy_required_groups", "")).split("|")
        )
        if not factor_ids:
            continue
        group_ready = group in ok_groups
        rows.append({
            "taxonomy_group": group,
            "ready": group_ready,
            "blocker": "" if group_ready else f"taxonomy_review_missing_ok_{group}",
            "blocked_alpha101_factor_count": len(factor_ids),
            "blocked_alpha101_factor_ids": "|".join(factor_ids),
        })
    return rows


def summarize_taxonomy_source_checks(review_source: dict[str, object]) -> dict[str, object]:
    """Return compact source-level check status for public reporting."""
    checks = [
        check for check in review_source.get("checks", [])
        if isinstance(check, dict)
    ]
    check_by_name = {str(check.get("check", "")): check for check in checks}
    failed_checks = sorted(
        str(check.get("check", ""))
        for check in checks
        if check.get("check") and not bool(check.get("passed", False))
    )
    status: dict[str, object] = {
        "source_check_pass": bool(checks) and not failed_checks,
        "source_check_count": len(checks),
        "source_failed_check_count": len(failed_checks),
        "source_failed_checks": "|".join(failed_checks),
    }
    for name in SOURCE_CHECK_STATUS_NAMES:
        check = check_by_name.get(name, {})
        status[f"source_check_{name}_pass"] = (
            bool(check.get("passed", False)) if check else False
        )
        status[f"source_check_{name}_detail"] = str(check.get("detail", ""))
    return status


def summarize_taxonomy_readiness(
    source_path: Path = TAXONOMY_SOURCE,
    artifact_path: Path = TAXONOMY_ARTIFACT,
    skipped_rows: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    source_exists = source_path.exists()

    contract_checks = check_contract(artifact_path)
    contract_pass = all(bool(c["passed"]) for c in contract_checks)
    coverage_pass = False
    coverage_error = ""
    if artifact_path.exists():
        try:
            _summary, coverage_checks, _symbol_coverage = check_coverage(
                DEFAULT_BARS,
                artifact_path,
                min_full_coverage=0.98,
            )
            coverage_pass = all(bool(c["passed"]) for c in coverage_checks)
        except Exception as exc:
            coverage_error = str(exc)
    else:
        coverage_error = f"Taxonomy file not found: {artifact_path}"

    taxonomy_skipped = [
        row for row in (skipped_rows or [])
        if row.get("source_family") == "alpha101" and row.get("taxonomy_blocker")
    ]
    required_groups = sorted({
        group
        for row in taxonomy_skipped
        for group in str(row.get("taxonomy_required_groups", "")).split("|")
        if group
    })
    review_source = summarize_review_source(
        source_path,
        required_groups=set(required_groups),
        bars_path=DEFAULT_BARS,
    )
    taxonomy_group_readiness = summarize_taxonomy_group_readiness(
        taxonomy_skipped,
        review_source,
    )
    packet_validation = summarize_taxonomy_packet_validation()
    packet_rollup = summarize_taxonomy_packet_rollup()
    reviewed_packet_rollup = summarize_taxonomy_packet_rollup(
        TAXONOMY_REVIEWED_PACKET_ROLLUP,
        prefix="reviewed_packet_rollup",
    )
    packet_coverage = summarize_taxonomy_packet_coverage()

    ok_rows = int(review_source.get("ok_row_count", 0))
    blocker = ""
    if not source_exists:
        blocker = "taxonomy_source_missing"
    elif not review_source.get("ready_to_build_artifact"):
        blocker = str(review_source.get("blocker") or "taxonomy_review_source_checks_failed")
    elif not artifact_path.exists():
        blocker = "taxonomy_artifact_missing"
    elif not contract_pass:
        blocker = "taxonomy_contract_failed"
    elif not coverage_pass:
        blocker = "taxonomy_coverage_failed"

    taxonomy_ready = (
        source_exists
        and bool(review_source.get("ready_to_build_artifact"))
        and artifact_path.exists()
        and contract_pass
        and coverage_pass
    )

    return {
        "source_path": str(source_path),
        "source_exists": source_exists,
        "source_rows": review_source.get("row_count", 0),
        "source_quality_counts": review_source.get("quality_counts", {}),
        "source_ok_row_count": ok_rows,
        "source_ready_to_build_artifact": bool(review_source.get("ready_to_build_artifact")),
        "source_missing_required_ok_groups": review_source.get("missing_required_ok_groups", ""),
        "source_bars_path": str(review_source.get("bars_path", "")),
        "source_bar_last_timestamp": str(review_source.get("bar_last_timestamp", "")),
        "source_ok_rows_known_by_last_bar": int(review_source.get("ok_rows_known_by_last_bar", 0) or 0),
        "source_ok_symbols_known_by_last_bar": int(review_source.get("ok_symbols_known_by_last_bar", 0) or 0),
        "source_ok_rows_known_after_last_bar": int(review_source.get("ok_rows_known_after_last_bar", 0) or 0),
        "source_ok_known_at_blocks_bars": bool(review_source.get("ok_known_at_blocks_bars", False)),
        **summarize_taxonomy_source_checks(review_source),
        **packet_validation,
        **packet_rollup,
        **reviewed_packet_rollup,
        **packet_coverage,
        "artifact_path": str(artifact_path),
        "artifact_exists": artifact_path.exists(),
        "contract_pass": contract_pass,
        "coverage_pass": coverage_pass,
        "coverage_error": coverage_error,
        "ready_for_indneutralize_unskip": taxonomy_ready,
        "blocker": blocker,
        "blocked_alpha101_factor_count": len(taxonomy_skipped),
        "blocked_alpha101_factor_ids": "|".join(row["factor_id"] for row in taxonomy_skipped),
        "required_taxonomy_groups": "|".join(required_groups),
        "taxonomy_group_readiness": taxonomy_group_readiness,
    }


def _load_cap_contract_status(path: Path = CAP_CONTRACT_CHECK) -> tuple[bool, dict[str, str], str]:
    if not path.exists():
        return False, {}, f"contract_check_missing:{path}"
    try:
        payload = json.loads(path.read_text())
    except Exception as exc:
        return False, {}, f"contract_check_unreadable:{exc}"
    checks = payload.get("checks", [])
    details = {str(row.get("check")): str(row.get("detail", "")) for row in checks}
    return bool(payload.get("overall_pass")), details, ""


def summarize_cap_readiness(
    artifact_path: Path = CAP_ARTIFACT,
    contract_check_path: Path = CAP_CONTRACT_CHECK,
    quality_report_path: Path = CAP_QUALITY_REPORT,
    skipped_rows: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    cap_skipped = [
        row for row in (skipped_rows or [])
        if row.get("source_family") == "alpha101" and row.get("cap_blocker")
    ]
    contract_pass, contract_details, contract_error = _load_cap_contract_status(contract_check_path)

    low_coverage_symbols = ""
    low_coverage_symbol_count = 0
    if quality_report_path.exists():
        try:
            quality = pd.read_csv(quality_report_path)
            if {"symbol", "cap_quality_status"}.issubset(quality.columns):
                low = quality[quality["cap_quality_status"].astype(str) == "LOW_COVERAGE"]
                low_coverage_symbol_count = int(len(low))
                low_coverage_symbols = "|".join(low["symbol"].astype(str).tolist())
        except Exception as exc:
            low_coverage_symbols = f"quality_report_unreadable:{exc}"

    if not artifact_path.exists():
        blocker = "cap_artifact_missing"
    elif contract_error:
        blocker = contract_error
    elif not contract_pass:
        blocker = "cap_contract_failed"
    else:
        blocker = ""

    return {
        "artifact_path": str(artifact_path),
        "artifact_exists": artifact_path.exists(),
        "contract_check_path": str(contract_check_path),
        "contract_check_exists": contract_check_path.exists(),
        "contract_pass": contract_pass,
        "overall_coverage": contract_details.get("overall_coverage", ""),
        "symbol_coverage_summary": contract_details.get("symbol_coverage_summary", ""),
        "quality_report_path": str(quality_report_path),
        "quality_report_exists": quality_report_path.exists(),
        "low_coverage_symbol_count": low_coverage_symbol_count,
        "low_coverage_symbols": low_coverage_symbols,
        "ready_for_cap_unskip": artifact_path.exists() and contract_pass,
        "blocker": blocker,
        "blocked_alpha101_factor_count": len(cap_skipped),
        "blocked_alpha101_factor_ids": "|".join(row["factor_id"] for row in cap_skipped),
    }


def mark_skipped_rows_ready(
    skipped_rows: list[dict[str, object]],
    *,
    taxonomy_readiness: dict[str, object],
    cap_readiness: dict[str, object],
) -> list[dict[str, object]]:
    taxonomy_ready = bool(taxonomy_readiness.get("ready_for_indneutralize_unskip", False))
    cap_ready = bool(cap_readiness.get("ready_for_cap_unskip", False))
    marked: list[dict[str, object]] = []
    for row in skipped_rows:
        needs_taxonomy = bool(row.get("taxonomy_blocker", False))
        needs_cap = bool(row.get("cap_blocker", False))
        ready = bool(
            (not needs_taxonomy or taxonomy_ready)
            and (not needs_cap or cap_ready)
            and (needs_taxonomy or needs_cap)
        )
        marked.append({**row, "ready_for_unskip": ready})
    return marked


def build_status_report(
    manifest_path: Path = MANIFEST,
    state_path: Path = STATE,
) -> dict[str, object]:
    rows = load_manifest(manifest_path)
    family_summary, skipped_rows = summarize_manifest(rows)
    registry_guard = summarize_registry_guard(family_summary)
    taxonomy_readiness = summarize_taxonomy_readiness(skipped_rows=skipped_rows)
    cap_readiness = summarize_cap_readiness(skipped_rows=skipped_rows)
    skipped_rows = mark_skipped_rows_ready(
        skipped_rows,
        taxonomy_readiness=taxonomy_readiness,
        cap_readiness=cap_readiness,
    )
    state = load_state(state_path)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "manifest_path": str(manifest_path),
        "state_path": str(state_path),
        "state": {
            "registered_factors": state.get("registered_factors"),
            "computed_factor_values": state.get("computed_factor_values"),
            "missing_factor_values": state.get("missing_factor_values"),
            "missing_input_factors": state.get("missing_input_factors"),
        },
        "family_summary": family_summary,
        "registry_guard": registry_guard,
        "skipped_rows": skipped_rows,
        "taxonomy_readiness": taxonomy_readiness,
        "cap_readiness": cap_readiness,
    }


def _without_generated_at(report: dict[str, object]) -> dict[str, object]:
    """Return report content relevant for semantic status comparisons."""
    return {key: value for key, value in report.items() if key != "generated_at"}


def write_status_json_if_changed(report: dict[str, object], out_json: Path) -> None:
    """Write status JSON only when semantic content changed.

    The report embeds a generation timestamp. Preserving the existing file when
    only that timestamp changed keeps repeated status checks from dirtying the
    worktree during factor-intake QA.
    """
    if out_json.exists():
        try:
            current = json.loads(out_json.read_text())
        except Exception:
            current = None
        if isinstance(current, dict) and _without_generated_at(current) == _without_generated_at(report):
            return
    out_json.write_text(json.dumps(report, indent=2, default=str) + "\n")


def write_status_report(report: dict[str, object], out_dir: Path = OUT_DIR) -> tuple[Path, Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_dir / "public_factor_integration_status.json"
    out_summary = out_dir / "public_factor_integration_status_by_family.csv"
    out_skipped = out_dir / "public_factor_integration_skipped_rows.csv"
    write_status_json_if_changed(report, out_json)
    pd.DataFrame(report["family_summary"]).to_csv(out_summary, index=False)
    pd.DataFrame(report["skipped_rows"]).to_csv(out_skipped, index=False)
    return out_json, out_summary, out_skipped


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default=str(MANIFEST), help="Public factor manifest CSV")
    parser.add_argument("--state", default=str(STATE), help="Factor library state JSON")
    parser.add_argument("--out-dir", default=str(OUT_DIR), help="Output diagnostics directory")
    args = parser.parse_args()

    report = build_status_report(Path(args.manifest), Path(args.state))
    state = report["state"]
    print("Public factor integration status")
    print(
        "  state: "
        f"registered={state['registered_factors']} "
        f"computed={state['computed_factor_values']} "
        f"missing_fv={state['missing_factor_values']} "
        f"missing_inputs={state['missing_input_factors']}"
    )
    for row in report["family_summary"]:
        print(
            f"  {row['source_family']}: total={row['manifest_total']} "
            f"accounted={row['accounted_non_skipped']} skipped={row['skipped']}"
        )
    taxonomy = report["taxonomy_readiness"]
    print(
        "  taxonomy: "
        f"source_rows={taxonomy['source_rows']} "
        f"quality={taxonomy['source_quality_counts']} "
        f"source_check_pass={taxonomy['source_check_pass']} "
        f"source_failed={taxonomy['source_failed_check_count']} "
        f"packet_pass={taxonomy['packet_validation_pass']} "
        f"packet_blocker={taxonomy['packet_validation_blocker']} "
        f"rollup_ready={taxonomy['packet_rollup_ready_to_apply_batch_count']} "
        f"rollup_blocked={taxonomy['packet_rollup_blocked_batch_count']} "
        f"reviewed_rollup_ready={taxonomy['reviewed_packet_rollup_ready_to_apply_batch_count']} "
        f"reviewed_rollup_blocked={taxonomy['reviewed_packet_rollup_blocked_batch_count']} "
        f"coverage_pass={taxonomy['packet_coverage_pass']} "
        f"coverage_rows={taxonomy['packet_coverage_rows']} "
        f"artifact_exists={taxonomy['artifact_exists']} "
        f"ready={taxonomy['ready_for_indneutralize_unskip']} "
        f"blocker={taxonomy['blocker']}"
    )
    cap = report["cap_readiness"]
    print(
        "  cap: "
        f"artifact_exists={cap['artifact_exists']} "
        f"contract_pass={cap['contract_pass']} "
        f"ready={cap['ready_for_cap_unskip']} "
        f"blocker={cap['blocker']} "
        f"coverage={cap['overall_coverage']}"
    )
    out_json, out_summary, out_skipped = write_status_report(report, Path(args.out_dir))
    print(f"Saved: {out_json}")
    print(f"Saved: {out_summary}")
    print(f"Saved: {out_skipped}")

    has_registry_gap = any(
        row["registry_missing_non_skipped"] or row["skipped_present_in_registry"]
        for row in report["family_summary"]
    )
    return 1 if has_registry_gap else 0


if __name__ == "__main__":
    sys.exit(main())
