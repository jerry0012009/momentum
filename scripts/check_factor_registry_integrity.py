#!/usr/bin/env python3
"""Factor Registry Integrity Checker — H11.

Reads factor_formula_registry.py and checks every FactorSpec against
engineering constraints.  Outputs a CSV/JSON integrity report.

Exit code:
  0  — only MISSING_INPUT_DATA / MISSING_FACTOR_VALUES (soft warnings)
  1  — critical issues found (duplicate id, invalid direction, etc.)
"""
from __future__ import annotations

import csv, json, os, re, sys, importlib
from pathlib import Path

# ── paths ──────────────────────────────────────────────────────────────
WORK = Path(__file__).resolve().parent.parent
SCRIPTS = WORK / "scripts"
FEATURES_DIR = WORK / "data" / "features" / "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1"
IC_CSV = WORK / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_level_evaluation" / "factor_level_rankic_summary.csv"
OUT_DIR = WORK / "research" / "factor_runs" / "crypto_top50_factor_library"
RAW_BARS_PATH = WORK / "data" / "cache" / "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1" / "bars_1h.parquet"

# ── constants ──────────────────────────────────────────────────────────
VALID_DIRECTIONS = {"positive", "negative", "conditional"}
VALID_STATUSES = {"IN_SIGNAL", "CANDIDATE", "DIAGNOSTIC_PROBE", "DEPRECATED", "ARCHIVED", "EXPERIMENTAL"}

# Signal factors (from build_phase9b_signal_panel.py)
SIGNAL_FACTORS = {
    "vol_5h", "vol_40h", "downside_vol_20h", "vol_of_vol_20h",
    "rsi_7h", "rsi_28h", "xs_rank_vol",
    "range_1h", "range_4h", "price_pos_24h",
}

# Conservative fallback — only basic OHLCV columns, NO taker/funding
_FALLBACK_COLUMNS = {"open", "high", "low", "close", "volume", "quote_volume"}


def _load_raw_bars_columns() -> set[str]:
    """Load available columns from raw bars parquet, or use conservative fallback."""
    if RAW_BARS_PATH.exists():
        try:
            import pyarrow.parquet as pq
            schema = pq.read_schema(str(RAW_BARS_PATH))
            cols = set(schema.names)
            print(f"Raw bars schema loaded from parquet: {len(cols)} columns")
            return cols
        except Exception as e:
            print(f"WARNING: failed to read raw bars schema: {e}")
    print(f"Using conservative fallback columns: {sorted(_FALLBACK_COLUMNS)}")
    return _FALLBACK_COLUMNS


KNOWN_RAW_COLUMNS = _load_raw_bars_columns()


def load_registry():
    """Import factor_formula_registry and return REGISTRY list."""
    sys.path.insert(0, str(SCRIPTS))
    # force reimport
    if "factor_formula_registry" in sys.modules:
        del sys.modules["factor_formula_registry"]
    if "factor_specs" in sys.modules:
        del sys.modules["factor_specs"]
    if "factor_ops" in sys.modules:
        del sys.modules["factor_ops"]
    import factor_formula_registry as ffr
    return ffr.REGISTRY


def load_ic_set() -> set[str]:
    """Return set of factor_ids that have factor-level IC computed."""
    if not IC_CSV.exists():
        return set()
    ids = set()
    with open(IC_CSV) as f:
        reader = csv.DictReader(f)
        for row in reader:
            ids.add(row["factor_name"])
    return ids


def check_factor_values_exists(factor_id: str) -> bool:
    fv_path = FEATURES_DIR / factor_id / "factor_values.parquet"
    return fv_path.exists()


def main():
    registry = load_registry()
    ic_set = load_ic_set()

    # ── check 1: factor_id uniqueness ──────────────────────────────
    seen_ids: dict[str, int] = {}
    critical_issues: list[str] = []
    for fs in registry:
        seen_ids[fs.factor_id] = seen_ids.get(fs.factor_id, 0) + 1
    for fid, count in seen_ids.items():
        if count > 1:
            critical_issues.append(f"DUPLICATE factor_id: {fid} appears {count} times")

    # ── per-factor checks ──────────────────────────────────────────
    rows = []
    for fs in registry:
        issues: list[str] = []
        missing_cols: list[str] = []

        # 1. factor_id format
        if not fs.factor_id or not re.match(r"^[a-z][a-z0-9_]*$", fs.factor_id):
            issues.append(f"INVALID factor_id format: '{fs.factor_id}'")

        # 2. family non-empty
        if not fs.family:
            issues.append("EMPTY family")

        # 3. required_columns
        if not fs.required_columns or not isinstance(fs.required_columns, list):
            issues.append("required_columns is empty or not a list")
        else:
            for col in fs.required_columns:
                if not isinstance(col, str):
                    issues.append(f"required_column non-string: {type(col)}")
                elif col not in KNOWN_RAW_COLUMNS:
                    missing_cols.append(col)

        # 4. lookback_window
        if not isinstance(fs.lookback_window, int) or fs.lookback_window < 1:
            issues.append(f"INVALID lookback_window: {fs.lookback_window}")

        # 5. expected_direction
        if fs.expected_direction not in VALID_DIRECTIONS:
            issues.append(f"INVALID expected_direction: '{fs.expected_direction}'")

        # 6. compute_fn callable (or panel_compute_fn for panel-scope factors)
        if fs.compute_scope == "panel":
            if not callable(fs.panel_compute_fn):
                issues.append("panel_compute_fn is not callable for panel-scope factor")
        else:
            if not callable(fs.compute_fn):
                issues.append("compute_fn is not callable")

        # 7. status
        status = fs.status or "DIAGNOSTIC_PROBE"
        if status not in VALID_STATUSES:
            issues.append(f"INVALID status: '{status}'")

        # 8. notes is string
        if fs.notes is not None and not isinstance(fs.notes, str):
            issues.append(f"notes is not string: {type(fs.notes)}")

        # 9. factor_values exists
        fv_exists = check_factor_values_exists(fs.factor_id)

        # 10. factor IC exists
        ic_exists = fs.factor_id in ic_set

        # 11. signal-used factor validation
        in_signal = fs.factor_id in SIGNAL_FACTORS
        if in_signal:
            if not fv_exists:
                issues.append("CRITICAL: signal-used factor missing factor_values")
            if not ic_exists:
                issues.append("CRITICAL: signal-used factor missing factor-level IC")
            if fs.expected_direction == "conditional":
                issues.append("WARNING: signal-used factor has conditional direction")

        # 12. taker/funding explicit classification
        missing_input = bool(missing_cols)
        if missing_input:
            for col in missing_cols:
                issues.append(f"MISSING_INPUT_DATA: required column '{col}' not in known raw bars schema")

        # lifecycle status
        if missing_input:
            lifecycle = "MISSING_INPUT_DATA"
        elif not fv_exists:
            lifecycle = "BUILDABLE"
        elif not ic_exists:
            lifecycle = "COMPUTED"
        elif in_signal:
            lifecycle = "ACTIVE_IN_SIGNAL"
        elif fs.expected_direction == "conditional":
            lifecycle = "DIAGNOSTIC_ONLY"
        else:
            lifecycle = "CANDIDATE"

        # recommended action
        if lifecycle == "MISSING_INPUT_DATA":
            action = "Acquire data source (taker/funding); cannot build without input columns"
        elif lifecycle == "BUILDABLE":
            action = "Run build_factor_values.py to compute factor_values"
        elif lifecycle == "COMPUTED":
            action = "Run evaluate_factors.py to compute factor-level IC"
        elif lifecycle == "ACTIVE_IN_SIGNAL":
            action = "No action needed; factor is in current signal panel"
        elif lifecycle == "DIAGNOSTIC_ONLY":
            action = "Keep for diagnostic; direction unknown prevents signal entry"
        else:
            action = "Monitor; consider for future signal variants"

        # classify critical vs soft
        for iss in issues:
            if iss.startswith("CRITICAL") or iss.startswith("INVALID") or iss.startswith("DUPLICATE") or iss == "compute_fn is not callable" or "panel_compute_fn is not callable" in iss:
                critical_issues.append(f"{fs.factor_id}: {iss}")

        rows.append({
            "factor_id": fs.factor_id,
            "family": fs.family,
            "required_columns": "; ".join(fs.required_columns),
            "missing_required_columns": "; ".join(missing_cols) if missing_cols else "",
            "lookback_window": fs.lookback_window,
            "expected_direction": fs.expected_direction,
            "registry_status": status,
            "factor_values_exists": fv_exists,
            "factor_ic_exists": ic_exists,
            "used_in_current_signal": in_signal,
            "lifecycle_status": lifecycle,
            "issues": "; ".join(issues) if issues else "OK",
            "recommended_action": action,
        })

    # ── write CSV ──────────────────────────────────────────────────
    csv_path = OUT_DIR / "factor_registry_integrity_report.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    os.chmod(csv_path, 0o644)

    # ── write JSON ─────────────────────────────────────────────────
    json_path = OUT_DIR / "factor_registry_integrity_report.json"
    report = {
        "phase": "12D-H11",
        "generated_at": __import__("datetime").datetime.now().isoformat(),
        "total_factors": len(rows),
        "critical_issues": critical_issues,
        "summary": {
            "factor_id_unique": len(critical_issues) == 0 or all("DUPLICATE" not in i for i in critical_issues),
            "all_directions_valid": all("INVALID expected_direction" not in r["issues"] for r in rows),
            "all_compute_fn_callable": all("compute_fn is not callable" not in r["issues"] for r in rows),
            "missing_input_data": sum(1 for r in rows if r["lifecycle_status"] == "MISSING_INPUT_DATA"),
            "buildable": sum(1 for r in rows if r["lifecycle_status"] == "BUILDABLE"),
            "computed": sum(1 for r in rows if r["lifecycle_status"] == "COMPUTED"),
            "active_in_signal": sum(1 for r in rows if r["lifecycle_status"] == "ACTIVE_IN_SIGNAL"),
            "diagnostic_only": sum(1 for r in rows if r["lifecycle_status"] == "DIAGNOSTIC_ONLY"),
            "candidate": sum(1 for r in rows if r["lifecycle_status"] == "CANDIDATE"),
        },
        "factors": rows,
    }
    with open(json_path, "w") as f:
        json.dump(report, f, indent=2)
    os.chmod(json_path, 0o644)

    # ── print summary ──────────────────────────────────────────────
    print(f"Registry: {len(rows)} factors checked")
    print(f"Critical issues: {len(critical_issues)}")
    for iss in critical_issues:
        print(f"  ❌ {iss}")
    print(f"Lifecycle distribution:")
    for status in ["ACTIVE_IN_SIGNAL", "CANDIDATE", "DIAGNOSTIC_ONLY", "COMPUTED", "BUILDABLE", "MISSING_INPUT_DATA"]:
        count = sum(1 for r in rows if r["lifecycle_status"] == status)
        if count:
            print(f"  {status}: {count}")
    print(f"Output: {csv_path}")
    print(f"Output: {json_path}")

    # ── exit code ──────────────────────────────────────────────────
    # Only DUPLICATE id, INVALID direction, missing compute_fn, signal-used missing IC → exit 1
    has_critical = any(
        "DUPLICATE" in i or "INVALID" in i or "compute_fn" in i or "signal-used factor missing" in i.lower()
        for i in critical_issues
    )
    sys.exit(1 if has_critical else 0)


if __name__ == "__main__":
    main()
