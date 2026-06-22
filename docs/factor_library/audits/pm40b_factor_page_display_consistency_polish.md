# PM-40B: Factor Page Display Consistency Polish

**Date:** 2026-06-23
**Scope:** 5 PM-35 new factors display consistency on public factor evaluation page
**Verdict:** `PM40B_DISPLAY_CONSISTENCY_PASS`

---

## Summary

After PM-40 merged factor-level evaluation data as fallback, 5 PM-35 new factors (`rev_2h`, `mom_vol_adjusted_20h`, `range_breakout_vol_confirm_20h`, `volume_pressure_20h`, `xs_rank_mom_accel`) had correct summary metrics but two display consistency issues remained:

1. **Monthly RankIC** showed bare "No data" despite summary RankIC being available
2. **Redundancy section** showed stale values (`INSUFFICIENT_OVERLAP`, `Cluster #-1`) conflicting with Unified Profile (`DISTINCT_SINGLETON`, `Cluster #45`)

---

## rev_2h Before/After

| Section | Before | After |
|---------|--------|-------|
| RankIC Mean | 0.0361 ✅ | 0.0361 ✅ |
| IC t-stat | 29.82 ✅ | 29.82 ✅ |
| Monthly RankIC chart | "No data" (no context) | Explanatory message: "Summary RankIC: 0.0361 (t=29.82). Monthly IC series unavailable." |
| Redundancy level | (empty) | LOW_REDUNDANCY (derived from profile) |
| Novelty Assessment | INSUFFICIENT_OVERLAP | NOVEL_DISTINCT (derived from cluster_member_role) |
| Cluster | `#-1` | `#45 (1 factors, from profile)` |
| Cluster Role | (not in old section) | DISTINCT_SINGLETON (from Unified Profile) |
| Marginal Info | (not in old section) | DISTINCT_SINGLETON (from Unified Profile) |

---

## Fix Details

### Fix 1: Profile field mapping

Added `profile_cluster_id` and `profile_cluster_size` from the unified profile payload to the HTML builder's profile merge. These fields are now available for fallback.

### Fix 2: Monthly RankIC explanatory message

When `monthly_ic` array is empty but `rankic_mean` exists, the chart now shows a bilingual explanatory message with the summary RankIC value and t-stat, instead of a bare "No data".

**Root cause:** `factor_level_period_ic_summary.csv` has 71 factors but is missing 5 PM-35 factors. The factor-level evaluation ran rankic/LS aggregation for all 76 factors but period IC computation only covered 71. Monthly IC data simply doesn't exist for these 5 factors — this is a data gap, not a display bug.

### Fix 3: Redundancy reconciliation

Post-processing step after all merges:
- `redundancy_cluster_id` = `-1` or `None` → use `profile_cluster_id` (from Unified Profile)
- `novelty_assessment` = `INSUFFICIENT_OVERLAP` or empty → derive from `cluster_member_role`:
  - `DISTINCT_SINGLETON` → `NOVEL_DISTINCT`
  - `REDUNDANT_*` → `REDUNDANT_NOVELTY_DERIVED`
- `redundancy_level` = `UNKNOWN` or empty → derive from `marginal_information_class`:
  - `DISTINCT_SINGLETON` → `LOW_REDUNDANCY`
  - `MOSTLY_REDUNDANT` → `MODERATE_REDUNDANCY`

---

## QA Results

### PM-35 Five-Factor Consistency Check (pm40b_display_consistency)

| Factor | source_warning | cluster_id | rankic_mean | Verdict |
|--------|---------------|------------|-------------|---------|
| rev_2h | (empty) | #45 | 0.036 | PASS |
| mom_vol_adjusted_20h | (empty) | #4 | -0.026 | PASS |
| range_breakout_vol_confirm_20h | (empty) | #32 | -0.041 | PASS |
| volume_pressure_20h | (empty) | #44 | -0.016 | PASS |
| xs_rank_mom_accel | (empty) | #46 | -0.024 | PASS |

**QA script:** 21/21 PASS (including new `pm40b_display_consistency` check)

---

## No Formulas / Factor Values / Signal Changed

- No factor formulas modified
- No `expected_direction` values changed
- No `factor_values` files modified
- No signal panel changes
- Only `_build_factor_eval_html.py` (HTML builder) and QA script modified

---

## Remaining Limitations

1. **5 factors lack monthly IC series data** — `factor_level_period_ic_summary.csv` doesn't have `rev_2h`, `mom_vol_adjusted_20h`, `range_breakout_vol_confirm_20h`, `volume_pressure_20h`, `xs_rank_mom_accel`. This means:
   - Monthly RankIC chart shows explanatory message instead of data
   - `rankic_std`, `rankic_ir`, `monthly_ic_positive_rate` cannot be computed
   - Need to re-run period IC computation with expanded factor set

2. **Redundancy values are derived, not computed** — `NOVEL_DISTINCT` and `LOW_REDUNDANCY` are mapped from profile roles, not from actual pairwise correlation. The old redundancy computation (`factor_redundancy_summary.csv`) has `None` for these 5 factors.

3. **Shape/stability data empty** — `monotonicity_class`, `q_spread_return`, `q_spearman_corr` are all None for these 5 factors in `factor_shape_stability_payload.json`. Quantile shape payload doesn't have them at all.

4. **Paper payload missing** — `single_factor_paper_page_payload.json` doesn't have entries for these 5 factors.

---

## Recommended Next PM

**PM-41: Post-intake factor interpretation and direction-semantics review**

- Review `expected_direction` for 5 new factors (all marked `positive` but some have negative t-stats at longer horizons)
- Run period IC computation to fill monthly IC gap
- Run shape/stability computation for new factors
- Generate paper payload entries for new factors
- Review decision_bucket (`DIRECTION_REVIEW_REQUIRED`) and update based on actual factor-level evidence
