#!/usr/bin/env python3
"""Build Factor Catalog — H11.

Synthesizes a unified factor catalog from:
  - factor registry metadata
  - factor_values existence
  - factor-level IC summary
  - factor coverage summary
  - current signal usage

Outputs CSV + JSON.  All data auto-generated, not hand-written.
"""
from __future__ import annotations

import csv, json, os, sys
from pathlib import Path

WORK = Path(__file__).resolve().parent.parent
SCRIPTS = WORK / "scripts"
FEATURES_DIR = WORK / "data" / "features" / "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1"
IC_CSV = WORK / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_level_evaluation" / "factor_level_rankic_summary.csv"
COV_CSV = WORK / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_level_evaluation" / "factor_level_coverage_summary.csv"
OUT_DIR = WORK / "research" / "factor_runs" / "crypto_top50_factor_library"

SIGNAL_FACTORS = {
    "vol_5h", "vol_40h", "downside_vol_20h", "vol_of_vol_20h",
    "rsi_7h", "rsi_28h", "xs_rank_vol",
    "range_1h", "range_4h", "price_pos_24h",
}
SIGNAL_ROLES = {
    "vol_5h": "risk_pressure", "vol_40h": "risk_pressure",
    "downside_vol_20h": "risk_pressure", "vol_of_vol_20h": "risk_pressure",
    "rsi_7h": "oscillator", "rsi_28h": "oscillator",
    "xs_rank_vol": "liquidity_gate",
    "range_1h": "position_overlay", "range_4h": "position_overlay",
    "price_pos_24h": "position_overlay",
}
KNOWN_RAW_COLUMNS = {
    "open", "high", "low", "close", "volume", "quote_volume",
    "taker_buy_quote_volume", "funding_rate",
}


def load_registry():
    sys.path.insert(0, str(SCRIPTS))
    for mod in ["factor_formula_registry", "factor_specs", "factor_ops"]:
        if mod in sys.modules:
            del sys.modules[mod]
    import factor_formula_registry as ffr
    return ffr.REGISTRY


def load_ic_data() -> dict:
    """Load IC summary: factor_id → {horizon: {raw_ic, adj_ic, t_stat, n_periods, coverage}}"""
    if not IC_CSV.exists():
        return {}
    data: dict = {}
    with open(IC_CSV) as f:
        for row in csv.DictReader(f):
            fid = row["factor_name"]
            h = row["horizon"]
            if fid not in data:
                data[fid] = {}
            data[fid][h] = {
                "raw_ic": float(row["raw_ic"]) if row.get("raw_ic") else None,
                "adj_ic": float(row["adj_ic"]) if row.get("adj_ic") else None,
                "t_stat": float(row["t_stat"]) if row.get("t_stat") else None,
                "n_periods": int(row["n_periods"]) if row.get("n_periods") else 0,
                "coverage": float(row["coverage"]) if row.get("coverage") else None,
                "missing_rate": float(row["missing_rate"]) if row.get("missing_rate") else None,
                "ic_status": row.get("status", ""),
            }
    return data


def load_coverage_data() -> dict:
    """Load coverage summary: factor_id → {coverage, missing_rate}"""
    if not COV_CSV.exists():
        return {}
    data: dict = {}
    with open(COV_CSV) as f:
        for row in csv.DictReader(f):
            fid = row["factor_name"]
            data[fid] = {
                "coverage": float(row["coverage"]) if row.get("coverage") else None,
                "missing_rate": float(row["missing_rate"]) if row.get("missing_rate") else None,
            }
    return data


def main():
    registry = load_registry()
    ic_data = load_ic_data()
    cov_data = load_coverage_data()

    rows = []
    for fs in registry:
        fid = fs.factor_id
        missing_cols = [c for c in fs.required_columns if c not in KNOWN_RAW_COLUMNS]
        fv_exists = (FEATURES_DIR / fid / "factor_values.parquet").exists()
        ic_exists = fid in ic_data
        in_signal = fid in SIGNAL_FACTORS

        # lifecycle
        if missing_cols:
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

        # factor_values status
        if missing_cols:
            fv_status = "MISSING_INPUT_DATA"
        elif fv_exists:
            fv_status = "EXISTS"
        else:
            fv_status = "NOT_COMPUTED"

        # IC status
        ic_status = "NOT_COMPUTED"
        if ic_exists:
            first_h = list(ic_data[fid].values())[0]
            ic_status = first_h.get("ic_status", "COMPUTED")
        elif missing_cols:
            ic_status = "MISSING_INPUT_DATA"
        elif not fv_exists:
            ic_status = "NEEDS_FACTOR_VALUES"

        # IC values (use 1h as primary)
        def get_ic(h, field):
            if fid in ic_data and h in ic_data[fid]:
                v = ic_data[fid][h].get(field)
                return round(v, 6) if v is not None else None
            return None

        cov_entry = cov_data.get(fid, {})
        ic_1h = ic_data.get(fid, {}).get("1h", {})

        # recommendation
        if in_signal:
            rec = "ACTIVE — no action needed"
        elif lifecycle == "MISSING_INPUT_DATA":
            rec = "Acquire data source before building"
        elif lifecycle == "BUILDABLE":
            rec = "Run build_factor_values.py"
        elif lifecycle == "COMPUTED":
            rec = "Run evaluate_factors.py"
        elif lifecycle == "DIAGNOSTIC_ONLY":
            rec = "Direction unknown; keep for diagnostic"
        else:
            adj_1h = get_ic("1h", "adj_ic")
            if adj_1h and abs(adj_1h) > 0.03:
                rec = "Strong IC candidate; consider for future signal variant"
            elif adj_1h and abs(adj_1h) > 0.02:
                rec = "Moderate IC; monitor"
            else:
                rec = "Low IC; keep in registry"

        rows.append({
            "factor_id": fid,
            "family": fs.family,
            "required_columns": "; ".join(fs.required_columns),
            "missing_required_columns": "; ".join(missing_cols) if missing_cols else "",
            "lookback_window": fs.lookback_window,
            "expected_direction": fs.expected_direction,
            "registry_status": fs.status or "DIAGNOSTIC_PROBE",
            "lifecycle_status": lifecycle,
            "factor_values_status": fv_status,
            "factor_ic_status": ic_status,
            "coverage": cov_entry.get("coverage"),
            "missing_rate": cov_entry.get("missing_rate"),
            "raw_ic_1h": get_ic("1h", "raw_ic"),
            "adj_ic_1h": get_ic("1h", "adj_ic"),
            "raw_ic_4h": get_ic("4h", "raw_ic"),
            "adj_ic_4h": get_ic("4h", "adj_ic"),
            "raw_ic_24h": get_ic("24h", "raw_ic"),
            "adj_ic_24h": get_ic("24h", "adj_ic"),
            "raw_ic_72h": get_ic("72h", "raw_ic"),
            "adj_ic_72h": get_ic("72h", "adj_ic"),
            "used_in_current_signal": in_signal,
            "signal_role": SIGNAL_ROLES.get(fid, ""),
            "recommendation": rec,
            "notes": fs.notes or "",
        })

    # ── write CSV ──────────────────────────────────────────────────
    csv_path = OUT_DIR / "factor_catalog.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    os.chmod(csv_path, 0o644)

    # ── write JSON ─────────────────────────────────────────────────
    json_path = OUT_DIR / "factor_catalog.json"
    catalog = {
        "phase": "12D-H11",
        "generated_at": __import__("datetime").datetime.now().isoformat(),
        "total_factors": len(rows),
        "lifecycle_distribution": {},
        "factors": rows,
    }
    # lifecycle dist
    for r in rows:
        ls = r["lifecycle_status"]
        catalog["lifecycle_distribution"][ls] = catalog["lifecycle_distribution"].get(ls, 0) + 1
    with open(json_path, "w") as f:
        json.dump(catalog, f, indent=2)
    os.chmod(json_path, 0o644)

    # ── summary ────────────────────────────────────────────────────
    print(f"Factor catalog: {len(rows)} factors")
    print(f"Lifecycle distribution:")
    for ls, count in sorted(catalog["lifecycle_distribution"].items(), key=lambda x: -x[1]):
        print(f"  {ls}: {count}")
    print(f"Output: {csv_path}")
    print(f"Output: {json_path}")


if __name__ == "__main__":
    main()
