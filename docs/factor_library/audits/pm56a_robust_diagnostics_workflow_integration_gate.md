# PM-56A: Robust Diagnostics Workflow Integration Gate

**Date:** 2026-06-24
**Status:** Workflow integration / gate.
**Verdict:** PM56A_ROBUST_DIAGNOSTICS_WORKFLOW_INTEGRATION_PASS

---

## 1. Summary

PM-54/56 generated robust diagnostics but they were not yet part of the formal workflow gate. PM-56A integrates robust RankIC and return-side diagnostics into the post-intake workflow, consistency checker, and integrity QA, so future factor additions automatically require and validate robust outputs.

**This PM does NOT:**
- Add new factors
- Modify formulas / expected_direction / factor_values
- Modify scorecard / best_horizon
- Modify page display
- Enter signal construction
- Make trading recommendations

---

## 2. Files Changed

| File | Change |
|------|--------|
| `scripts/run_post_intake_workflow_completion.py` | Added `rankic-robust-significance` and `return-robust-significance` stages; added robust CSVs to `detect_missing_factors()` |
| `scripts/check_active_factor_workflow_consistency.py` | Added robust full-universe checks (84×4 with horizon verification) + documented subset reporting |
| `scripts/check_post_intake_workflow_integrity.py` | Added `check_rankic_robust()` and `check_ls_robust()` functions; added robust tables to `--all-active` consistency table |
| `scripts/compute_return_robust_significance.py` | Clarified cost-collapsed comment (Sharpe-based vs t-stat-based) |
| `.../factor_return_robust_significance_manifest.json` | Fixed RETURN_COST_COLLAPSED rule description: "gross robust_t >= 2" → "gross Sharpe >= 0.8 and net Sharpe < 0.5" |
| `docs/factor_library/POST_INTAKE_WORKFLOW_RUNBOOK.md` | Added §14.5 robust diagnostics integration |
| `docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md` | Added item 13: PM-56A robust diagnostics gate |
| `docs/factor_library/REGENERATION_CONTRACT.md` | Added §10.7 robust diagnostics gate |
| `docs/factor_library/audits/pm56a_robust_diagnostics_workflow_integration_gate.md` | New audit |

---

## 3. Workflow Stages Added

| Stage Name | Script | Position |
|------------|--------|----------|
| `rankic-robust-significance` | `compute_rankic_robust_significance.py` | After `scorecard`, before `profile` |
| `return-robust-significance` | `compute_return_robust_significance.py` | After `rankic-robust-significance`, before `profile` |

**`--start-from` support:** Both stages can be invoked explicitly:
```bash
python scripts/run_post_intake_workflow_completion.py --factor-ids ... --start-from rankic-robust-significance
```

**`--only-missing` behavior:** Now checks `factor_rankic_robust_significance_summary.csv` and `factor_ls_robust_significance_summary.csv` in addition to existing 12 tables.

---

## 4. Robust Full-Universe Coverage Table

| Output | Expected | Key Column | Horizon Check |
|--------|----------|------------|---------------|
| `factor_rankic_robust_significance_summary.csv` | 84 factors × 4 horizons = 336 rows | `factor_id` | ✓ 4 horizons verified |
| `factor_ls_robust_significance_summary.csv` | 84 factors × 4 horizons = 336 rows | `factor_id` | ✓ 4 horizons verified |

Both are **hard required** — missing any active factor = FAIL.

---

## 5. Documented Subset Coverage Table

| Output | Actual | Status |
|--------|--------|--------|
| `factor_paper_robust_significance_summary.csv` | 5 factors, 5 rows | Documented subset (informational) |
| `factor_fee_robust_significance_summary.csv` | 13 factors, 13 rows | Documented subset (informational) |

These are **not** full-universe required. They are reported as documented subsets.

---

## 6. Consistency Checker Result

```
Tables checked: 15
PASS: 15  |  FAIL: 0
Verdict: PASS

Robust Diagnostics (PM-54/56):
  ✓ rankic_robust            84/84  PASS (4 horizons ✓)
  ✓ ls_robust                84/84  PASS (4 horizons ✓)

Documented Subset Outputs:
  ✓ paper_robust             5 factors, 5 rows
  ✓ fee_robust               13 factors, 13 rows
```

---

## 7. All-Active Integrity QA Result

```
Factors: 84
Total checks: 1764
PASS: 1764
FAIL: 0
WARN: 0

Active-Universe Count Consistency:
  ✓ rankic_robust             84/84  PASS
  ✓ ls_robust                 84/84  PASS
  Active count consistency: PASS
```

---

## 8. Page QA Result

```
Total: 33  |  PASS: 33  |  FAIL: 0
```

---

## 9. Fee Rule Alignment

**Before (manifest, incorrect):**
```
RETURN_COST_COLLAPSED = "gross robust_t >= 2 but fee-adjusted robust_t < 2"
```

**After (manifest, aligned with code):**
```
RETURN_COST_COLLAPSED = "gross Sharpe >= 0.8 and net Sharpe < 0.5 (fee-survival diagnostic, not a t-stat test)"
```

**Code (unchanged):**
```python
"cost_status": "RETURN_COST_COLLAPSED" if (
    gross_row["sharpe"] >= 0.8 and net_row["sharpe"] < 0.5
) else "COST_SURVIVED"
```

The t-stat based path in `classify_return_robust()` is preserved for potential future use when time-series fee data is available, but the current fee sensitivity analysis uses Sharpe-based classification. Comments clarify the distinction.

---

## 10. No Unauthorized Changes

- No new factors ✓
- No formula changes ✓
- No expected_direction changes ✓
- No factor_values changes ✓
- No scorecard changes ✓
- No best_horizon changes ✓
- No page display changes ✓
- No signal construction ✓
- No trading recommendations ✓

---

## 11. Remaining Limitations

1. Paper robust covers only 5/84 factors (limited by existing paper diagnostics)
2. Fee robust covers only 13/84 factors (limited by existing fee sensitivity data)
3. Robust diagnostics are not yet integrated into page display (PM-55 covers RankIC only)
4. Return-side robust diagnostics are standalone CSV/JSON, not in factor-evaluation.html

---

## 12. Recommended Next PM

- **PM-57**: Integrate return-side robust diagnostics into factor-evaluation.html
- **PM-58**: Expand paper portfolio diagnostics to all 84 factors
