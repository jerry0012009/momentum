# PM-32C: Evidence Truthfulness and Profile Calibration

**Date:** 2026-06-22
**Follows:** PM-32B (workflow alignment)

---

## Summary Verdict

**`EVIDENCE_TRUTHFULNESS_PROFILE_CALIBRATION_PASS`**

## 1. Why PM-32C

PM-32B had evidence truthfulness issues:
- `has_factor_values` was False for some factors but evidence_status was COMPLETE
- `has_factor_level_evaluation` was False but evidence_status was COMPLETE
- `registry_or_data_status` was UNKNOWN
- Profile collapsed to BROAD_WATCHLIST: 67, UNIQUE_BUT_WEAK: 4

## 2. How has_factor_values is computed

Checks actual existence of `data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/{factor_id}/factor_values.parquet` AND state file `computed_factor_values` set.

## 3. How has_factor_level_evaluation is computed

Checks existence of `factor_level_evaluation/factor_level_rankic_summary.csv` AND factor present in rankic file AND all 3 evaluation artifacts exist.

## 4. How registry_or_data_status is computed

Read from `factor_diagnostics_summary.csv` `lifecycle_status` column per factor. Falls back to state file `factor_lifecycle_distribution`.

## 5. Evidence Matrix Before/After

| Metric | Before | After |
|---|---|---|
| evidence_status=COMPLETE | 71 | 65 |
| evidence_status=COMPLETE_WITH_WARNINGS | 0 | 6 |

The 6 COMPLETE_WITH_WARNINGS factors have MISSING_INPUT_DATA status.

## 6. Workflow Readiness

- WORKFLOW_READY: 71

## 7. Profile Class Before/After

| Class | Before | After |
|---|---|---|
| BROAD_WATCHLIST | 67 | 43 |
| PROMISING_BUT_REGIME_DEPENDENT | 0 | 25 |
| UNIQUE_BUT_WEAK | 4 | 3 |

## 8. Research Action Before/After

| Action | Before | After |
|---|---|---|
| LOWER_PRIORITY_REVIEW | 59 | 37 |
| WATCH_FOR_REGIME_DEPENDENCE | 0 | 25 |
| WATCH_FOR_STABILITY_RISK | 8 | 6 |
| KEEP_AS_DIAGNOSTIC_PROBE | 4 | 3 |

## 9. Validation

- py_compile: ✅
- Script execution: ✅
- All has_factor_values True: ✅
- All has_factor_level_evaluation True: ✅
- All has_unified_profile True: ✅
- Zero bad COMPLETE rows: ✅

## 10. Forbidden Language

All outputs PASS

## 11. Limitations

1. 6 factors with MISSING_INPUT_DATA still WORKFLOW_READY (downstream artifacts exist)
2. NaN registry_or_data_status for 6 factors (state file lacks lifecycle info)

## 12. Non-Change Statement

No factors, formulas, factor_values, signal panel, public page modified.

## 13. Recommended Next PM

**PM-33:** Unified profile page integration and workflow-readiness presentation.
