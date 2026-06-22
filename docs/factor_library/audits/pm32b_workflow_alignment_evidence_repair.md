# PM-32B: Workflow Alignment and Evidence Matrix Repair

**Date:** 2026-06-22
**Follows:** PM-32 (unified profile)

---

## Summary Verdict

**`WORKFLOW_ALIGNMENT_EVIDENCE_REPAIR_PASS`**

## 1. Why PM-32B

PM-32 placed `profile` too early in the runner (after cluster, before paper/regime/shape/decile/capacity). Evidence matrix lacked `has_factor_values`, `has_factor_level_evaluation`, `has_unified_profile`. Workflow contract didn't reflect actual runner.

## 2. Files Changed

- `scripts/build_unified_factor_profile.py` — evidence matrix + contract alignment checks
- `scripts/run_factor_library_refresh.py` — stage order repaired
- `scripts/check_factor_library_staleness.py` — added profile output checks
- `docs/factor_library/REGENERATION_CONTRACT.md` — profile placement
- 8 output files regenerated

## 3. Runner/Contract Alignment

✅ runner == contract (exact match)
✅ capacity-liquidity < profile
✅ profile < staleness

## 4. Stage Order (both runner and contract)

registry-integrity → catalog → values → direction-audit → evaluate → diagnostics → metadata → scorecard → redundancy → cluster → paper-diagnostics → paper-page-payload → regime → shape-stability → decile-shape → capacity-liquidity → profile → staleness → page → state

## 5. Evidence Matrix Repair

Added columns:
- has_factor_values
- has_factor_level_evaluation
- has_unified_profile
- registry_or_data_status

## 6. Factor Coverage

- Expected: 71
- Evidence: 71
- Profile: 71
- All COMPLETE

## 7. Workflow Readiness

- WORKFLOW_READY: 71

## 8. Staleness Monitor

✅ Updated with 8 profile/workflow output checks

## 9. Forbidden Language

All outputs PASS

## 10. Validation

- py_compile: ✅
- Script execution: ✅
- Runner==contract: ✅
- Stage ordering: ✅
- Evidence matrix: ✅

## 11. Limitations

1. Profile class distribution unchanged (67 BROAD_WATCHLIST, 4 UNIQUE_BUT_WEAK)

## 12. Non-Change Statement

No factors, formulas, factor_values, signal panel, public page modified.

## 13. Recommended Next PM

**PM-33:** Unified profile page integration and workflow-readiness presentation.
