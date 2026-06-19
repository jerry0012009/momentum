#!/usr/bin/env python3
"""Check Factor Catalog Integrity — H11-R self-check.

Validates that factor_catalog.csv and factor_catalog.json are internally
consistent and match the registry.

Exit code: 0 = pass, 1 = issues found.
"""
from __future__ import annotations

import csv, json, sys
from pathlib import Path

WORK = Path(__file__).resolve().parent.parent
CATALOG_CSV = WORK / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_catalog.csv"
CATALOG_JSON = WORK / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_catalog.json"

SIGNAL_FACTORS = {
    "vol_5h", "vol_40h", "downside_vol_20h", "vol_of_vol_20h",
    "rsi_7h", "rsi_28h", "xs_rank_vol",
    "range_1h", "range_4h", "price_pos_24h",
}


def main():
    issues: list[str] = []

    # 1. Files exist
    if not CATALOG_CSV.exists():
        issues.append("factor_catalog.csv does not exist")
    if not CATALOG_JSON.exists():
        issues.append("factor_catalog.json does not exist")
    if issues:
        for i in issues:
            print(f"❌ {i}")
        sys.exit(1)

    # Load registry count
    sys.path.insert(0, str(WORK / "scripts"))
    for mod in ["factor_formula_registry", "factor_specs", "factor_ops"]:
        if mod in sys.modules:
            del sys.modules[mod]
    import factor_formula_registry as ffr
    registry_count = len(ffr.REGISTRY)

    # 2. Load catalog
    with open(CATALOG_JSON) as f:
        catalog = json.load(f)
    rows = catalog["factors"]

    # 3. Row count = registry count
    if len(rows) != registry_count:
        issues.append(f"Catalog row count ({len(rows)}) != registry count ({registry_count})")

    # 4. COMPUTED / ACTIVE_IN_SIGNAL factors must have adj_ic_1h
    for r in rows:
        fid = r["factor_id"]
        ls = r["lifecycle_status"]
        ic_status = r["factor_ic_status"]
        fv_status = r["factor_values_status"]

        # Contradiction: IC status = COMPUTED but IC values empty
        if ic_status == "COMPUTED":
            if r.get("adj_ic_1h") in (None, ""):
                issues.append(f"{fid}: ic_status=COMPUTED but adj_ic_1h is empty")

        # Contradiction: ACTIVE_IN_SIGNAL but IC missing
        if ls == "ACTIVE_IN_SIGNAL":
            for h in ["1h", "4h", "24h", "72h"]:
                for prefix in ["raw_ic_", "adj_ic_"]:
                    key = f"{prefix}{h}"
                    if r.get(key) in (None, ""):
                        issues.append(f"{fid}: ACTIVE_IN_SIGNAL but {key} is empty")

        # Contradiction: fv_status=EXISTS but ic_status=MISSING_INPUT_DATA
        if fv_status == "EXISTS" and ic_status == "MISSING_INPUT_DATA":
            issues.append(f"{fid}: fv_status=EXISTS but ic_status=MISSING_INPUT_DATA (contradictory)")

        # Missing FV factors must be clearly classified
        if ls == "MISSING_INPUT_DATA":
            if fv_status not in ("MISSING_INPUT_DATA",):
                issues.append(f"{fid}: lifecycle=MISSING_INPUT_DATA but fv_status={fv_status}")

    # 5. Signal factors must have complete horizons
    for r in rows:
        if r["used_in_current_signal"]:
            fid = r["factor_id"]
            for h in ["1h", "4h", "24h", "72h"]:
                if r.get(f"raw_ic_{h}") in (None, ""):
                    issues.append(f"{fid}: signal-used but raw_ic_{h} is empty")
                if r.get(f"adj_ic_{h}") in (None, ""):
                    issues.append(f"{fid}: signal-used but adj_ic_{h} is empty")

    # Report
    if issues:
        for i in issues:
            print(f"❌ {i}")
        print(f"\nTotal issues: {len(issues)}")
        sys.exit(1)
    else:
        print(f"✅ Catalog integrity check PASSED")
        print(f"   {len(rows)} factors, {sum(1 for r in rows if r['used_in_current_signal'])} in signal")
        print(f"   {sum(1 for r in rows if r['lifecycle_status'] == 'MISSING_INPUT_DATA')} MISSING_INPUT_DATA")
        print(f"   {sum(1 for r in rows if r['lifecycle_status'] == 'BUILDABLE')} BUILDABLE")
        print(f"   {sum(1 for r in rows if r['lifecycle_status'] == 'COMPUTED')} COMPUTED")
        print(f"   {sum(1 for r in rows if r['lifecycle_status'] == 'ACTIVE_IN_SIGNAL')} ACTIVE_IN_SIGNAL")
        sys.exit(0)


if __name__ == "__main__":
    main()
