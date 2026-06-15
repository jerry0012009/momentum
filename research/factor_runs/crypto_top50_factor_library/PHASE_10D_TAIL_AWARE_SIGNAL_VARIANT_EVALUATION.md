# Phase 10D Closeout — Tail-Aware Signal Variant Evaluation

> Date: 2026-06-15
> Previous: Phase 10C-R COMPLETE
> Scope: Evaluate 48 signal variants (3 signals × 4 horizons × 4 variants)

---

## Status

Phase 10D: COMPLETE, pending PM review.

---

## Evaluation Matrix

48 variants evaluated:

- 3 signals: core_only, pm_full_structured, family_balanced_diagnostic
- 4 horizons: 1h, 4h, 24h, 72h
- 4 variants: original_no_guard, original_bucket0_guard, inverted_no_guard, inverted_bucket0_guard

---

## Pass/Fail Summary

**3/48 PASS** (RankIC > 0 AND median_spread > 0):

| Signal | Horizon | Variant | RankIC | Median Spread |
|--------|---------|---------|--------|---------------|
| core_only | 1h | original_no_guard | +0.0325 | +0.000153 |
| pm_full_structured | 1h | original_no_guard | +0.0314 | +0.000102 |
| family_balanced_diagnostic | 1h | original_no_guard | +0.0303 | +0.000042 |

**Pattern: only 1h original_no_guard passes both criteria.**

---

## Key Findings

### 1. RankIC consistency
All original variants show positive RankIC (0.025–0.042). All inverted variants show negative RankIC (by construction, RankIC sign flips). This confirms Phase 10A canonical results.

### 2. Median spread pattern
- **1h**: original median spread positive (weak, ~0.004–0.015%)
- **4h**: original median spread mixed (near zero); bucket0_guard helps
- **24h**: original median spread negative; inverted positive (confirms 10B tail finding)
- **72h**: original median spread strongly negative; inverted strongly positive

### 3. Bucket0 guard effect
Bucket0 guard consistently improves median spread for original variants (reduces negative tail pull). For 4h core_only: median_spread flips from −0.0055% to +0.0116% with guard.

### 4. Inverted variants
Inverted variants have negative RankIC (sign flip). Even though median_spread is positive for 24h/72h inverted, the RankIC < 0 means the signal loses cross-sectional information when inverted.

### 5. Winsorized/tail-trim spreads
Winsorized spreads are more stable than mean spreads, confirming Phase 10B outlier-dominated diagnosis.

---

## PM Decision Matrix

| Condition | Recommendation |
|-----------|---------------|
| 1h original_no_guard PASS | Evaluate in Phase 11 with cost/slippage |
| 4h bucket0_guard improves spread | Consider tail-aware evaluation in Phase 11 |
| 24h/72h inverted median_spread positive but RankIC negative | Do NOT invert; direction conflict unresolved |
| All horizons: original RankIC positive | Original direction is canonical |
| No variant passes for 4h/24h/72h without guard or inversion | Phase 11 must evaluate with proper cost framework |

---

## What Was NOT Done

- No signal v1 implemented
- No backtest with cost/slippage
- No alpha claim
- No tradeable/live designation
- No weight optimization
- No model selection
- Phase 11 NOT STARTED

---

## Artifacts

| File | Description |
|------|-------------|
| `phase10d_variant_evaluation_summary.csv` | 48 rows, full evaluation |
| `phase10d_variant_pass_fail_matrix.csv` | 48 rows, pass/fail |
| `phase10d_variant_bucket_exposure.csv` | 48 rows, bucket0 exposure |
| `phase10d_variant_timeseries.parquet` | 48 rows, key metrics |
| `phase10d_quality_checks.csv` | 10 checks, all PASS |
| `scripts/run_phase10d_tail_aware_variants.py` | Evaluation script |
| `tests/unit/test_phase10d_tail_aware_variants.py` | Tests |

---

## Next Required PM Decision

Phase 10D evaluation complete. PM must decide:

1. **Proceed to Phase 11** with 1h original_no_guard as baseline + cost/slippage framework?
2. **Phase 10D-R** to investigate 4h bucket0_guard improvement?
3. **Different direction** — e.g., multi-horizon signal blending?

Phase 11 NOT STARTED until PM approval.
