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
CAP_ARTIFACT = ROOT / "data" / "cache" / "crypto_market_cap_1h_contract_v1" / "market_cap_1h_aligned.parquet"
CAP_CONTRACT_CHECK = ROOT / "data" / "cache" / "crypto_market_cap_1h_contract_v1" / "market_cap_contract_check.json"
CAP_QUALITY_REPORT = ROOT / "data" / "cache" / "crypto_market_cap_1h_contract_v1" / "market_cap_quality_report.csv"
SKIPPED_PREFIX = "skipped_"
TAXONOMY_GROUP_COLUMNS = {"sector", "industry", "subindustry"}
CAP_COLUMNS = {"cap"}

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


def load_state(path: Path = STATE) -> dict[str, object]:
    with path.open() as handle:
        return json.load(handle)


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
    review_source = summarize_review_source(source_path, required_groups=set(required_groups))

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

    return {
        "source_path": str(source_path),
        "source_exists": source_exists,
        "source_rows": review_source.get("row_count", 0),
        "source_quality_counts": review_source.get("quality_counts", {}),
        "source_ok_row_count": ok_rows,
        "source_ready_to_build_artifact": bool(review_source.get("ready_to_build_artifact")),
        "source_missing_required_ok_groups": review_source.get("missing_required_ok_groups", ""),
        "artifact_path": str(artifact_path),
        "artifact_exists": artifact_path.exists(),
        "contract_pass": contract_pass,
        "coverage_pass": coverage_pass,
        "coverage_error": coverage_error,
        "ready_for_indneutralize_unskip": contract_pass and coverage_pass,
        "blocker": blocker,
        "blocked_alpha101_factor_count": len(taxonomy_skipped),
        "blocked_alpha101_factor_ids": "|".join(row["factor_id"] for row in taxonomy_skipped),
        "required_taxonomy_groups": "|".join(required_groups),
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


def build_status_report(
    manifest_path: Path = MANIFEST,
    state_path: Path = STATE,
) -> dict[str, object]:
    rows = load_manifest(manifest_path)
    family_summary, skipped_rows = summarize_manifest(rows)
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
        "skipped_rows": skipped_rows,
        "taxonomy_readiness": summarize_taxonomy_readiness(skipped_rows=skipped_rows),
        "cap_readiness": summarize_cap_readiness(skipped_rows=skipped_rows),
    }


def write_status_report(report: dict[str, object], out_dir: Path = OUT_DIR) -> tuple[Path, Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_dir / "public_factor_integration_status.json"
    out_summary = out_dir / "public_factor_integration_status_by_family.csv"
    out_skipped = out_dir / "public_factor_integration_skipped_rows.csv"
    out_json.write_text(json.dumps(report, indent=2, default=str) + "\n")
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
