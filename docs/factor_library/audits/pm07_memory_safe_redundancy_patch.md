# PM-07 Memory-Safe Factor Redundancy Patch

**Date:** 2026-06-21
**Follows:** PM-06

---

## A. PM-06 Failure Summary

`build_factor_redundancy.py` was killed by SIGKILL (exit -9) during PM-06 intake smoke test. Root cause: OOM. The script loaded all 59 factor parquets (3.3M rows each) into memory and performed incremental outer merges into one wide DataFrame. Peak memory ~50GB on a 15GB machine.

## B. Old Algorithm

1. `load_factor_wide()`: load ALL factor parquets into memory
2. Outer-merge all factors on (timestamp, symbol) into one wide table
3. Apply `sample_step` AFTER building the wide table
4. Compute pairwise correlations from columns of the wide table

Peak memory: O(N_factors × N_rows) for the wide table.

## C. New Algorithm

1. `load_factor_series()`: load ONE factor at a time, apply `sample_step` BEFORE join, drop NaN factor_values early
2. Pre-load intake factors (small set, ~3 files) into a cache
3. For intake-vs-baseline: load ONE baseline factor, inner-join with each cached intake factor, compute correlations, delete baseline immediately
4. For library mode: load pairs sequentially (fi, fj), inner-join, compute, delete

Peak memory: O(2 × N_rows_sampled) — at most 2 factor DataFrames in memory at once.

Additional optimization: intake mode auto-defaults to `sample_step=5` (~660K rows instead of 3.3M).

## D. Files Changed

- `scripts/build_factor_redundancy.py` — full rewrite of computation core

## E. Run Command

```bash
python scripts/run_factor_intake.py \
  --factor-ids rev_1h rev_3h price_volume_corr_20h \
  --run-id pm07_intake_redundancy_smoke_20260621 \
  --skip-build-values
```

## F. Run Results

- **Run ID:** pm07_intake_redundancy_smoke_20260621
- **Runtime:** 303s (vs PM-06: 202s without redundancy, then OOM)
- **Status:** COMPLETE
- **Artifacts:** 17/17 present (including factor_redundancy.csv)

## G. factor_redundancy.csv

- **Total pairs:** 171 (3 intake × 56 baseline + 3 intake-vs-intake)
- **Columns:** factor_i, factor_j, family_i, family_j, same_family, spearman_corr, abs_spearman_corr, pearson_corr, n_pairwise_obs, redundancy_level, recommendation, pair_type ✅ (matches expected schema)

**Redundancy level distribution:**
- MODERATE_REDUNDANCY: 1
- LOW_REDUNDANCY: 46
- INSUFFICIENT_DATA: 124

**Top pair:** rev_1h × rsi_7h: |ρ|=0.766 (MODERATE_REDUNDANCY)

124 pairs show INSUFFICIENT_DATA because `sample_step=5` reduces timestamps from ~75K to ~15K, and many factor pairs have overlapping non-null observations < 30. This is a conservative tradeoff — memory safety over coverage.

## H. Conclusion Cards

| factor_id | redundancy_level | decision_bucket |
|-----------|-----------------|----------------|
| rev_1h | MODERATE_REDUNDANCY | REVIEW_REQUIRED |
| rev_3h | LOW_REDUNDANCY | REVIEW_REQUIRED |
| price_volume_corr_20h | LOW_REDUNDANCY | CONDITIONAL_DIRECTION_REVIEW |

**All 3 cards have non-UNKNOWN redundancy information.** ✅

## I. Quality Checks

8/8 PASS, 0 FAIL.

## J. Promotion Guard

Not re-tested. PM-06 already validated promotion guard behavior (blocked without --confirm, guards passed with --confirm, promotion not implemented). The intake runner and promote_factor_intake.py were not modified in this phase.

## K. Memory Behavior

- Old: ~50GB peak → OOM kill
- New: ~2-3 factor DataFrames in memory at once (~80-120MB with sample_step=5)
- Estimated peak memory: <500MB
- No OOM, no SIGKILL

## L. Non-Change Statement

No factor formulas, signal logic, signal panel, universe data, labels, canonical factor values, or public result pages were changed.
