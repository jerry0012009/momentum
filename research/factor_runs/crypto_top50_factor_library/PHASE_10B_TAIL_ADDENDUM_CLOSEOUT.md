# Phase 10B-lite Closeout — Tail Diagnostics Addendum

> Date: 2026-06-15
> Previous: Phase 10A-R COMPLETE
> Scope: Tail outlier diagnostics only

---

## Status

Phase 10B-lite: COMPLETE, pending PM review.
Phase 11: NOT STARTED. Phase 12: NOT STARTED. Phase 13: NOT STARTED.

---

## 1. Key Findings

### 1.1 Median Spread is POSITIVE

The **median** per-timestamp spread is positive for all signals × horizons (except pm_full_72h which is ≈0):

| Signal | Horizon | Mean Spread | Median Spread | Diagnosis |
|--------|---------|------------|---------------|-----------|
| core_only | 1h | −0.000306 | **+0.000392** | MEAN_SPREAD_OUTLIER_DOMINATED |
| core_only | 4h | −0.001232 | **+0.000829** | MEAN_SPREAD_OUTLIER_DOMINATED |
| core_only | 24h | −0.006742 | **+0.001649** | MEAN_SPREAD_OUTLIER_DOMINATED |
| core_only | 72h | −0.016623 | **+0.000341** | MEAN_SPREAD_OUTLIER_DOMINATED |
| pm_full | 1h | −0.000316 | **+0.000375** | MEAN_SPREAD_OUTLIER_DOMINATED |
| pm_full | 4h | −0.001182 | **+0.000833** | MEAN_SPREAD_OUTLIER_DOMINATED |
| pm_full | 24h | −0.006594 | **+0.001629** | MEAN_SPREAD_OUTLIER_DOMINATED |
| pm_full | 72h | −0.016746 | −0.000010 | ROBUST_SPREAD_STILL_NEGATIVE |

**Interpretation**: The typical long-short spread is positive (median), but extreme negative outliers in the short leg drag the mean negative. This is **outlier-dominated mean**, not non-monotonic tail behavior.

### 1.2 Bucket 0 Concentration is Moderate

- Top 1% contribution: ~11% (not extreme)
- Top 5% contribution: ~28-30% (moderate)
- Bucket 0 is NOT driven by a handful of extreme outliers — it's a **structural effect** of the lowest-signal bucket having systematically higher returns.

### 1.3 Robust Spread Still Negative (But Much Smaller)

- Winsorized (1-99%) spread: still negative, ~5-15% smaller than standard
- Winsorized (5-95%) spread: still negative, ~20-40% smaller
- Tail-trim (ex bucket 0) spread: still negative, ~50-70% smaller

The spread improves substantially with robust measures but doesn't fully reverse. This suggests the negative mean spread is driven by **both** bucket 0 outliers AND general non-monotonicity.

---

## 2. Answers to Required Questions

1. **Is bucket 0 driven by a few samples?** No. Top 1% contribution is only ~11%. It's a structural effect, not a few outliers.

2. **Is median/winsorized/tail-trimmed spread still negative?**
   - Median spread: **POSITIVE** (key finding)
   - Winsorized: **Negative** (but smaller)
   - Tail-trim: **Negative** (but much smaller)

3. **Is data quality audit needed?** Optional but recommended. The outlier-dominated mean suggests some timestamps have extreme short-leg returns worth investigating.

4. **Is tail-aware signal redesign needed?** Yes, for 1h/4h horizons (direction conflict). Median-spread is positive, suggesting the signal works for the typical case.

5. **Is horizon-specific direction policy needed?** Yes, for 24h/72h (both RankIC and spread improve with inversion).

6. **Is Phase 11 allowed?** **NOT YET.** PM must review the median-vs-mean finding and decide on direction policy before cost/slippage analysis.

---

## 3. Negative Declarations

- No signal was flipped.
- No Phase 10A or 10A-R results were modified.
- No alpha claim.
- No cost/slippage/capacity.
- No paper/live trading.
- Phase 11/12/13 NOT STARTED.
