# Phase 10D-R Closeout — Bucket0 Guard Implementation Repair

> Date: 2026-06-15
> Previous: Phase 10D NEEDS FIX
> Scope: Repair bucket0 guard logic and exposure metrics

---

## Status

Phase 10D-R: COMPLETE, pending PM review.

---

## What Was Wrong

### Bug 1: Bucket assignment used original signal for all variants
- **Before**: Buckets computed from original signal only; inverted variants used original signal buckets.
- **After**: Buckets computed from evaluated signal (original for original variants, inverted for inverted variants).
- **Impact**: Bucket 0 of inverted signal = highest decile of original signal. Guard was removing wrong symbols.

### Bug 2: bucket0_lower_leg_exposure_fraction measured cross-section fraction, not short-leg exposure
- **Before**: `b0_frac = b0.sum() / n` — fraction of bucket 0 in entire cross-section (~10%), same for guarded and no_guard.
- **After**: 
  - no_guard: fraction of bucket 0 symbols in the short leg (bottom 20%) — ~58%.
  - bucket0_guard: 0.0 (bucket 0 excluded from short leg).
- **Impact**: Previously showed ~10.8% for both guarded and no_guard, which was logically reversed.

---

## Repaired Results

### Bucket0 exposure (correct):
- **no_guard**: ~58% of short leg is bucket 0 (expected: bucket 0 = lowest 10%, short leg = lowest 20%, ~50% overlap).
- **bucket0_guard**: 0.0 (bucket 0 excluded from short leg).

### Pass/Fail: 9/48 PASS (up from 3/48)

| Signal | Horizon | Variant | RankIC | Median Spread | b0 Exposure |
|--------|---------|---------|--------|---------------|-------------|
| core_only | 1h | original_no_guard | +0.0325 | +0.015% | 58% |
| core_only | 1h | original_bucket0_guard | +0.0325 | +0.015% | 0% |
| core_only | 4h | original_bucket0_guard | +0.0385 | +0.012% | 0% |
| pm_full | 1h | original_no_guard | +0.0314 | +0.010% | 58% |
| pm_full | 1h | original_bucket0_guard | +0.0314 | +0.012% | 0% |
| pm_full | 4h | original_bucket0_guard | +0.0365 | +0.007% | 0% |
| family_balanced | 1h | original_no_guard | +0.0303 | +0.004% | 58% |
| family_balanced | 1h | original_bucket0_guard | +0.0303 | +0.008% | 0% |
| family_balanced | 4h | original_bucket0_guard | +0.0352 | +0.010% | 0% |

### Key finding: Bucket0 guard improves median spread
- 1h: guard improves median spread for pm_full (+0.010% → +0.012%) and family_balanced (+0.004% → +0.008%).
- 4h: guard flips median spread from negative to positive for all 3 signals.
- 24h/72h: guard improves but median spread remains negative for original direction.

---

## Does Bucket0 Guard Work?

**Yes, for 1h and 4h.** The guard consistently improves median spread by removing the extreme bucket 0 tail from the short leg. For 4h, it turns a negative median spread into a positive one.

**No, for 24h/72h original direction.** Median spread remains negative even with guard. The tail behavior at longer horizons is more severe.

---

## Phase 11 Eligibility

**6 variants are eligible for Phase 11 cost/slippage/capacity evaluation:**
- 3 × 1h original_bucket0_guard (all signals)
- 3 × 4h original_bucket0_guard (all signals)

Plus 3 × 1h original_no_guard (baseline comparison).

**Phase 11 NOT STARTED.** PM decision required.

---

## Negative Declarations

- No signal v1 implemented
- No backtest with cost/slippage
- No alpha claim
- No tradeable/live designation
- No weight optimization
- No model selection

---

## Artifacts

| File | Description |
|------|-------------|
| `phase10d_variant_evaluation_summary.csv` | 48 rows, repaired |
| `phase10d_variant_pass_fail_matrix.csv` | 48 rows, repaired |
| `phase10d_variant_bucket_exposure.csv` | 48 rows, repaired |
| `phase10d_variant_timeseries.parquet` | 48 rows, repaired |
| `phase10d_quality_checks.csv` | 11 checks, all PASS |
| `PHASE_10D_R_BUCKET0_GUARD_REPAIR.md` | This closeout |
| `scripts/run_phase10d_tail_aware_variants.py` | Repaired script |
| `tests/unit/test_phase10d_r_bucket0_guard_repair.py` | Tests |
