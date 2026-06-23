# PM-46: Batch02 Workflow Gap Repair

**Date:** 2026-06-23
**Verdict:** `BATCH02_WORKFLOW_REPAIR_PASS`

---

## Summary

Fixed 10 workflow gaps exposed by PM-45 batch02 factor intake. The post-intake runner now covers all 15 evaluation blocks, the integrity checker validates 17 dimensions (up from 11), and `up_down_vol_ratio_20h` achieves 15/15 evidence completeness.

## Root Cause Table

| # | Missing Block | Root Cause | Fix |
|---|---------------|-----------|-----|
| 1 | LS metrics NaN in diagnostics_summary | Wrong column names in manual merge (`long_short_annualized_return` vs `long_short_spread_annualized_return`) | Fixed by `build_factor_diagnostics_metrics.py` regeneration |
| 2 | Cumulative LS curve missing | `build_factor_diagnostics_metrics.py` not called in runner | Added as stage `diagnostics-metrics` |
| 3 | Quantile shape missing | `build_factor_shape_stability_diagnostics.py` not called in runner | Added as stage `shape-stability` |
| 4 | Rolling stability missing | Same as #3 — same script generates both | Same fix |
| 5 | Decile shape missing | `build_factor_decile_shape_diagnostics.py` not called in runner | Added as stage `decile` |
| 6 | Capacity/liquidity missing | `build_factor_capacity_liquidity_diagnostics.py` not called in runner | Added as stage `capacity` |
| 7 | Unified profile incomplete | Cascading from #2-6 | Fixed by fixing #2-6 |
| 8 | Integrity checker false positive | Only 11 checks, missing quantile/rolling/decile/capacity/cumulative/factor_values | Expanded to 17 checks |
| 9 | Evaluate partial mode failure | Safety guard blocks `--factor-ids` without `--output-suffix` | Runner now uses `--output-suffix batch` + auto-merge |
| 10 | Paper diagnostics overwrites canonical | `--output-dir` not used for subset runs | Runner now uses temp dir + auto-merge |

## Existing Scripts Reused

| Script | Purpose | Was in runner? |
|--------|---------|---------------|
| `build_factor_shape_stability_diagnostics.py` | Quantile shape + rolling stability | NO → added |
| `build_factor_decile_shape_diagnostics.py` | Decile shape | NO → added |
| `build_factor_capacity_liquidity_diagnostics.py` | Capacity/liquidity | NO → added |
| `build_factor_diagnostics_metrics.py` | Cumulative LS, monthly IC/LS series, diagnostics summary | NO → added |

## New Scripts Added

None. All needed scripts already existed in the repo.

## Changes to Post-Intake Runner

**File:** `scripts/run_post_intake_workflow_completion.py`

1. **Added 5 new stages:** `diagnostics-metrics`, `shape-stability`, `decile`, `capacity`
2. **Fixed evaluate stage:** Uses `--output-suffix batch` + `post_action` to merge results into canonical CSVs
3. **Fixed paper-diagnostics stage:** Uses `--output-dir` temp dir + `post_action` to merge
4. **Added merge helpers:** `_merge_csv()`, `_merge_evaluate_outputs()`, `_merge_paper_outputs()`
5. **Total stages:** 15 (up from 11)

## Changes to Integrity Checker

**File:** `scripts/check_post_intake_workflow_integrity.py`

Added 6 new checks:
1. `factor_values` — checks `data/features/` and `research/factor_runs/` paths
2. `quantile_shape` — checks `factor_quantile_shape_summary.csv`
3. `rolling_stability` — checks `factor_rolling_stability_summary.csv` (allows INSUFFICIENT_HISTORY as WARNING)
4. `decile_shape` — checks `factor_decile_shape_summary.csv`
5. `capacity_liquidity` — checks `factor_capacity_liquidity_summary.csv`
6. `cumulative_ls` — checks `factor_cumulative_long_short_curve.csv`

**Total checks:** 17 (up from 11)

## up_down_vol_ratio_20h Completeness Before/After

| Block | Before (PM-45) | After (PM-46) |
|-------|---------------|---------------|
| factor_values | ✓ | ✓ |
| factor_level_rankic | ✓ | ✓ |
| period_ic | ✓ | ✓ |
| period_ls | ✓ | ✓ |
| ls_aggregate | ✓ | ✓ |
| cumulative_ls | ✗ | ✓ |
| paper_payload | ✓ | ✓ |
| regime_btc | ✓ | ✓ |
| quantile_shape | ✗ | ✓ |
| rolling_stability | ✗ | ✓ (INSUFFICIENT_HISTORY) |
| decile_shape | ✗ | ✓ |
| capacity_liquidity | ✗ | ✓ |
| pairwise_redundancy | ✓ | ✓ |
| cluster | ✓ | ✓ |
| marginal_info | ✓ | ✓ |
| scorecard_not_stale | ✓ | ✓ |
| unified_profile | ✓ | ✓ |
| **Integrity total** | **11/11** | **17/17** |
| Evidence blocks | 11/15 | 15/15 |
| Profile score | 40.6 | 44.6 |

## PM-35 Regression Check

```
✅ rev_2h                         PASS=17 FAIL=0
✅ mom_vol_adjusted_20h           PASS=17 FAIL=0
✅ range_breakout_vol_confirm_20h PASS=17 FAIL=0
✅ volume_pressure_20h            PASS=17 FAIL=0
✅ xs_rank_mom_accel              PASS=17 FAIL=0
```

All 5 PM-35 factors pass 17/17 checks (regression clean).

## Page QA

```
Total: 23 | PASS: 23 | FAIL: 0
```

## Public Page

HTTP 200, JSON valid, factor_count=77.

## No Changes Confirmation

- ✅ No existing factor formulas changed
- ✅ No existing factor_values changed
- ✅ No expected_direction changed
- ✅ No signal panel changed

## Remaining Limitations

1. **Rolling stability shows INSUFFICIENT_HISTORY** for `up_down_vol_ratio_20h` — this is correct behavior (new factor has limited history), not a bug.
2. **evaluate_factors.py safety guard** still exists — runner works around it with temp output + merge, which is the intended pattern.

## Recommended Next Steps

- **PM-47:** Factor interpretation for `up_down_vol_ratio_20h`
- **PM-48:** Batch03 planning
