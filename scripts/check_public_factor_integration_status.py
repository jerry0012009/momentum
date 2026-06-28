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
SKIPPED_PREFIX = "skipped_"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from factor_formula_registry import REGISTRY_BY_ID  # noqa: E402


def load_manifest(path: Path = MANIFEST) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


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
            skipped_rows.append({
                "source_family": family,
                "factor_id": row["factor_id"],
                "implementation_status": row["implementation_status"],
                "skip_reason": row["skip_reason"],
                "required_columns": row["required_columns"],
                "required_ops": row["required_ops"],
            })
    return summary, skipped_rows


def load_state(path: Path = STATE) -> dict[str, object]:
    with path.open() as handle:
        return json.load(handle)


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
    }


def write_status_report(report: dict[str, object], out_dir: Path = OUT_DIR) -> tuple[Path, Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_dir / "public_factor_integration_status.json"
    out_summary = out_dir / "public_factor_integration_status_by_family.csv"
    out_skipped = out_dir / "public_factor_integration_skipped_rows.csv"
    out_json.write_text(json.dumps(report, indent=2, default=str))
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
