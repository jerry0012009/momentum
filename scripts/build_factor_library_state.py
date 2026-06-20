#!/usr/bin/env python3
"""Generate factor library state — single source of truth for current counts.

Reads canonical sources (registry, factor_values directories, catalog, integrity
report, candidate review, signal component manifest, signal composition review).
Never hard-codes counts. Derives signal_factor_ids and signal_variants from
canonical artifacts; falls back to code constants only with explicit warnings.

Outputs:
  research/factor_runs/crypto_top50_factor_library/factor_library_state.json
  research/factor_runs/crypto_top50_factor_library/factor_library_state.md

Phase 13A-P3. Not production. Not live trading.
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
FEATURES_DIR = ROOT / "data" / "features" / "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1"
EVAL_DIR = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_level_evaluation"
CATALOG_JSON = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_catalog.json"
INTEGRITY_JSON = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_registry_integrity_report.json"
OUT_DIR = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"

# Canonical signal artifacts (in priority order)
SIGNAL_COMPONENT_MANIFEST = OUT_DIR / "phase9b_signal_component_manifest.csv"
SIGNAL_FACTOR_REVIEW = OUT_DIR / "signal_composition_review" / "signal_factor_component_review.csv"
SIGNAL_COMPOSITION_MANIFEST = OUT_DIR / "signal_composition_review" / "signal_composition_review_manifest.json"
SIGNAL_VARIANT_COMPARISON = OUT_DIR / "signal_composition_review" / "signal_variant_comparison.csv"

# Fallback constant — used only if no canonical artifact is found
_FALLBACK_SIGNAL_FACTOR_IDS = {
    "vol_5h", "vol_40h", "downside_vol_20h", "vol_of_vol_20h",
    "rsi_7h", "rsi_28h", "xs_rank_vol",
    "range_1h", "range_4h", "price_pos_24h",
}

LABEL_HORIZONS = ["1h", "4h", "24h", "72h"]


def load_registry():
    """Load REGISTRY from factor_formula_registry.py."""
    sys.path.insert(0, str(SCRIPTS))
    for mod in ["factor_formula_registry", "factor_specs", "factor_ops"]:
        if mod in sys.modules:
            del sys.modules[mod]
    from factor_formula_registry import REGISTRY
    return REGISTRY


def load_json_if_exists(path: Path) -> dict | None:
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


def load_csv_if_exists(path: Path) -> list[dict] | None:
    if path.exists():
        with open(path) as f:
            return list(csv.DictReader(f))
    return None


def _derive_signal_factor_ids(warnings: list[str]) -> tuple[list[str], str]:
    """Derive current_signal_factor_ids from canonical artifacts.

    Priority:
      1. phase9b_signal_component_manifest.csv — extract leaf factor IDs
      2. signal_composition_review/signal_factor_component_review.csv
      3. Fallback to code constant + warning

    Returns (sorted_factor_ids, source_description).
    """
    # Source 1: signal component manifest
    if SIGNAL_COMPONENT_MANIFEST.exists():
        rows = load_csv_if_exists(SIGNAL_COMPONENT_MANIFEST)
        if rows:
            # First pass: collect all component IDs
            component_ids = set()
            for row in rows:
                cid = row.get("component_id", "").strip()
                if cid:
                    component_ids.add(cid)
            # Second pass: extract leaf factor IDs (exclude composite components)
            factor_ids = set()
            for row in rows:
                factors_str = row.get("included_factors", "")
                for f in factors_str.split(","):
                    f = f.strip()
                    # Skip empty, composite references containing "+", and known component IDs
                    if not f:
                        continue
                    if "+" in f:
                        continue
                    if f in component_ids:
                        continue
                    factor_ids.add(f)
            if factor_ids:
                return sorted(factor_ids), "phase9b_signal_component_manifest.csv"

    # Source 2: signal factor component review
    if SIGNAL_FACTOR_REVIEW.exists():
        rows = load_csv_if_exists(SIGNAL_FACTOR_REVIEW)
        if rows:
            factor_ids = set()
            for row in rows:
                fid = row.get("factor_id", "") or row.get("factor_name", "")
                if fid:
                    factor_ids.add(fid)
            if factor_ids:
                return sorted(factor_ids), "signal_factor_component_review.csv"

    # Fallback
    warnings.append(
        "current_signal_factor_ids derived from code constant (no canonical signal artifact found). "
        "Run build_phase9b_signal_panel.py or signal composition review to generate canonical artifacts."
    )
    return sorted(_FALLBACK_SIGNAL_FACTOR_IDS), "code_constant_FALLBACK"


def _derive_signal_variants(warnings: list[str]) -> tuple[int, str]:
    """Derive signal_variants from canonical artifacts.

    Priority:
      1. signal_composition_review_manifest.json — signal_variants field
      2. signal_variant_comparison.csv — count unique variant names
      3. Return 0 + warning

    Returns (count, source_description).
    """
    # Source 1: composition review manifest
    if SIGNAL_COMPOSITION_MANIFEST.exists():
        manifest = load_json_if_exists(SIGNAL_COMPOSITION_MANIFEST)
        if manifest and "signal_variants" in manifest:
            return int(manifest["signal_variants"]), "signal_composition_review_manifest.json"

    # Source 2: variant comparison CSV
    if SIGNAL_VARIANT_COMPARISON.exists():
        rows = load_csv_if_exists(SIGNAL_VARIANT_COMPARISON)
        if rows:
            variants = set()
            for row in rows:
                sv = row.get("signal_variant", "")
                if sv:
                    variants.add(sv)
            if variants:
                return len(variants), "signal_variant_comparison.csv"

    # Fallback
    warnings.append(
        "signal_variants set to 0 (no canonical signal variant artifact found). "
        "Run signal composition review to generate canonical artifacts."
    )
    return 0, "no_artifact_FALLBACK"


def build_state() -> dict:
    """Build the canonical factor library state dict."""
    registry = load_registry()
    registered_ids = [fs.factor_id for fs in registry]

    # Compute factor_values existence
    computed_ids = []
    missing_fv_ids = []
    for fid in registered_ids:
        fv_path = FEATURES_DIR / fid / "factor_values.parquet"
        if fv_path.exists():
            computed_ids.append(fid)
        else:
            missing_fv_ids.append(fid)

    # Missing input factors (from registry integrity report or catalog)
    integrity = load_json_if_exists(INTEGRITY_JSON)
    catalog = load_json_if_exists(CATALOG_JSON)
    missing_input_ids = []
    if integrity and "factor_details" in integrity:
        missing_input_ids = [
            d["factor_id"] for d in integrity["factor_details"]
            if d.get("lifecycle") == "MISSING_INPUT_DATA"
        ]
    elif catalog and "factors" in catalog:
        missing_input_ids = [
            f["factor_id"] for f in catalog["factors"]
            if f.get("lifecycle_status") == "MISSING_INPUT_DATA"
        ]

    # Lifecycle distribution
    lifecycle_dist = Counter()
    if catalog and "lifecycle_distribution" in catalog:
        lifecycle_dist = Counter(catalog["lifecycle_distribution"])
    else:
        # Derive signal factor IDs for lifecycle classification
        signal_ids, _ = _derive_signal_factor_ids([])
        for fs in registry:
            fv_exists = (FEATURES_DIR / fs.factor_id / "factor_values.parquet").exists()
            if fs.factor_id in missing_input_ids:
                lifecycle_dist["MISSING_INPUT_DATA"] += 1
            elif not fv_exists:
                lifecycle_dist["BUILDABLE"] += 1
            elif fs.factor_id in signal_ids:
                lifecycle_dist["ACTIVE_IN_SIGNAL"] += 1
            elif fs.expected_direction == "conditional":
                lifecycle_dist["DIAGNOSTIC_ONLY"] += 1
            else:
                lifecycle_dist["CANDIDATE"] += 1

    # Candidate review distribution
    review_csv_path = EVAL_DIR / "factor_level_candidate_review.csv"
    review_data = load_csv_if_exists(review_csv_path)
    review_dist = Counter()
    if review_data:
        for row in review_data:
            bucket = row.get("review_bucket", "UNKNOWN")
            review_dist[bucket] += 1

    # Metric panel — find best factors
    metric_csv_path = EVAL_DIR / "factor_level_metric_panel.csv"
    metric_data = load_csv_if_exists(metric_csv_path)
    best_factors = []
    if metric_data:
        by_fid = {}
        for row in metric_data:
            fid = row.get("factor_name", "")
            if fid not in by_fid:
                by_fid[fid] = []
            by_fid[fid].append(row)
        for fid, rows in by_fid.items():
            best_adj = None
            best_hz = None
            for r in rows:
                adj = r.get("direction_adjusted_mean_rank_ic")
                if adj not in (None, "", "None"):
                    adj = float(adj)
                    if best_adj is None or abs(adj) > abs(best_adj):
                        best_adj = adj
                        best_hz = r.get("horizon")
            if best_adj is not None:
                best_factors.append({
                    "factor_id": fid,
                    "best_adj_ic": round(best_adj, 8),
                    "best_horizon": best_hz,
                })
        best_factors.sort(key=lambda x: abs(x["best_adj_ic"]), reverse=True)

    # Warnings
    warnings = []
    if len(computed_ids) + len(missing_fv_ids) != len(registered_ids):
        warnings.append("computed + missing != registered — possible registry/factor_values drift")
    if missing_input_ids:
        warnings.append(f"{len(missing_input_ids)} factors have missing input data: {', '.join(missing_input_ids)}")
    if not review_data:
        warnings.append("candidate review CSV not found — run evaluate_factors.py first")

    # Derive signal factor IDs from canonical artifacts
    signal_factor_ids, signal_source = _derive_signal_factor_ids(warnings)

    # Derive signal variants from canonical artifacts
    signal_variants, variant_source = _derive_signal_variants(warnings)

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset_id": "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1",
        "registered_factors": len(registered_ids),
        "registered_factor_ids": registered_ids,
        "computed_factor_values": len(computed_ids),
        "computed_factor_ids": computed_ids,
        "missing_factor_values": len(missing_fv_ids),
        "missing_factor_ids": missing_fv_ids,
        "missing_input_factors": len(missing_input_ids),
        "missing_input_factor_ids": missing_input_ids,
        "active_signal_factors": len(signal_factor_ids),
        "signal_factor_ids": signal_factor_ids,
        "signal_factor_source": signal_source,
        "signal_variants": signal_variants,
        "signal_variant_source": variant_source,
        "horizons": LABEL_HORIZONS,
        "factor_lifecycle_distribution": dict(lifecycle_dist),
        "candidate_review_distribution": dict(review_dist),
        "current_signal_factor_ids": signal_factor_ids,
        "canonical_paths": {
            "features_dir": str(FEATURES_DIR),
            "evaluation_dir": str(EVAL_DIR),
            "catalog_json": str(CATALOG_JSON),
            "integrity_json": str(INTEGRITY_JSON),
            "candidate_review_csv": str(review_csv_path),
            "metric_panel_csv": str(metric_csv_path),
            "signal_component_manifest": str(SIGNAL_COMPONENT_MANIFEST),
            "signal_factor_component_review": str(SIGNAL_FACTOR_REVIEW),
            "signal_composition_review_manifest": str(SIGNAL_COMPOSITION_MANIFEST),
            "signal_variant_comparison": str(SIGNAL_VARIANT_COMPARISON),
            "phase9b_signal_panel_manifest": str(OUT_DIR / "phase9b_signal_panel_manifest.csv"),
            "phase9b_signal_panel_parquet": str(OUT_DIR / "phase9b_signal_panel.parquet"),
        },
        "top_factors_by_adj_ic": best_factors[:15],
        "warnings": warnings,
        "disclaimer": "Factor library state. Diagnostic only. Not production. Not live trading.",
    }
    return state


def write_json(state: dict, out_dir: Path) -> Path:
    path = out_dir / "factor_library_state.json"
    with open(path, "w") as f:
        json.dump(state, f, indent=2, default=str)
    return path


def write_markdown(state: dict, out_dir: Path) -> Path:
    path = out_dir / "factor_library_state.md"
    lines = []
    lines.append("# Factor Library State")
    lines.append("")
    lines.append(f"**Generated:** {state['generated_at']}")
    lines.append(f"**Dataset:** {state['dataset_id']}")
    lines.append("")
    lines.append("## Counts")
    lines.append("")
    lines.append(f"| Metric | Count |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Registered factors | {state['registered_factors']} |")
    lines.append(f"| Computed factor_values | {state['computed_factor_values']} |")
    lines.append(f"| Missing factor_values | {state['missing_factor_values']} |")
    lines.append(f"| Missing input data | {state['missing_input_factors']} |")
    lines.append(f"| Active signal factors | {state['active_signal_factors']} |")
    lines.append(f"| Signal variants | {state['signal_variants']} |")
    lines.append("")
    lines.append("## Lifecycle Distribution")
    lines.append("")
    for k, v in sorted(state["factor_lifecycle_distribution"].items(), key=lambda x: -x[1]):
        lines.append(f"- **{k}:** {v}")
    lines.append("")
    if state["candidate_review_distribution"]:
        lines.append("## Candidate Review Distribution")
        lines.append("")
        for k, v in sorted(state["candidate_review_distribution"].items(), key=lambda x: -x[1]):
            lines.append(f"- **{k}:** {v}")
        lines.append("")
    lines.append("## Signal Factor IDs")
    lines.append("")
    lines.append(f"*Source: {state.get('signal_factor_source', 'unknown')}*")
    lines.append("")
    for fid in state["current_signal_factor_ids"]:
        lines.append(f"- {fid}")
    lines.append("")
    lines.append(f"## Signal Variants: {state['signal_variants']}")
    lines.append("")
    lines.append(f"*Source: {state.get('signal_variant_source', 'unknown')}*")
    lines.append("")
    if state["missing_input_factor_ids"]:
        lines.append("## Missing Input Factors")
        lines.append("")
        for fid in state["missing_input_factor_ids"]:
            lines.append(f"- {fid}")
        lines.append("")
    if state["top_factors_by_adj_ic"]:
        lines.append("## Top Factors by Adjusted IC")
        lines.append("")
        lines.append("| factor_id | best_adj_ic | horizon |")
        lines.append("|-----------|-------------|---------|")
        for f in state["top_factors_by_adj_ic"]:
            lines.append(f"| {f['factor_id']} | {f['best_adj_ic']:+.6f} | {f['best_horizon']} |")
        lines.append("")
    if state["warnings"]:
        lines.append("## Warnings")
        lines.append("")
        for w in state["warnings"]:
            lines.append(f"- {w}")
        lines.append("")
    lines.append("---")
    lines.append("*Diagnostic only. Not production. Not live trading.*")
    lines.append("")
    with open(path, "w") as f:
        f.write("\n".join(lines))
    return path


def main():
    state = build_state()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = write_json(state, OUT_DIR)
    md_path = write_markdown(state, OUT_DIR)
    print(f"Factor Library State:")
    print(f"  Registered: {state['registered_factors']}")
    print(f"  Computed:   {state['computed_factor_values']}")
    print(f"  Missing FV: {state['missing_factor_values']}")
    print(f"  Missing Input: {state['missing_input_factors']}")
    print(f"  Signal:     {state['active_signal_factors']} (source: {state['signal_factor_source']})")
    print(f"  Variants:   {state['signal_variants']} (source: {state['signal_variant_source']})")
    print(f"  Warnings:   {len(state['warnings'])}")
    for w in state["warnings"]:
        print(f"    ⚠️  {w}")
    print(f"Output: {json_path}")
    print(f"Output: {md_path}")


if __name__ == "__main__":
    main()
