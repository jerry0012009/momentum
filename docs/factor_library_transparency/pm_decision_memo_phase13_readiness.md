# PM Decision Memo — Phase 13 Readiness

> Date: 2026-06-15
> Status: PENDING PM DECISION

---

## Summary

After 6 phases of diagnostic evaluation (Phase 7–12B), one candidate remains conditionally viable:

**signal_v0_core_only__1h__original_no_guard**

- Gross spread: +0.051%/hour (mean)
- Mid-cost net (15bps, turnover-adjusted): +0.209 cumulative over 30 days
- Turnover: median 12.5%
- Capacity: $660k median at 1% participation
- Universe: 43 symbols
- Status: PAPER_SIGNAL_DIAGNOSTIC_ONLY

The signal has survived all diagnostic gates. The main remaining risk is forward performance validation — the 30-day rolling monitoring used historical data, not true out-of-sample forward returns.

## Decision Options

### Option A: Proceed to Phase 13A — Future Paper Validation Only

**Description:** Run the paper signal harness on live incoming data for 30-90 days. No real execution. No capital. No exchange connection. Pure monitoring.

**Pros:**
- Zero capital risk
- Validates forward performance
- Builds confidence before any real execution decision
- Can detect regime changes, data issues, or signal decay

**Cons:**
- Takes 30-90 days
- May find the signal doesn't work forward (which is valuable information)
- Requires maintaining the signal infrastructure

**Risk:** LOW

### Option B: Extend Phase 12B Monitoring — Longer Historical Window

**Description:** Run the rolling monitoring over 90-180 days instead of 30 days before deciding on Phase 13.

**Pros:**
- More data, more confidence
- Captures different market regimes
- No forward waiting period

**Cons:**
- Still historical, not forward
- May be overfitting to historical patterns
- Delays forward validation

**Risk:** LOW

### Option C: Return to Phase 9/10 — Signal Redesign

**Description:** Go back to factor construction and try to build a higher-spread signal.

**Pros:**
- Current spread is thin (0.051%/hour)
- May find a better signal
- Can address the 43-symbol universe limitation

**Cons:**
- No guarantee of improvement
- May take many more phases
- Current signal is the best of 48 variants

**Risk:** MEDIUM

### Option D: Pause Project

**Description:** Stop and revisit later.

**Pros:**
- No risk
- Time to reflect

**Cons:**
- No progress
- Market conditions may change

**Risk:** NONE

## Recommendation

**Option A: Proceed to Phase 13A — Future Paper Validation Only.**

Rationale:
1. The signal has survived all diagnostic gates. This is meaningful evidence.
2. The only missing piece is forward validation. Phase 13A addresses this directly.
3. Zero capital risk. If the signal fails forward, we learn without losing money.
4. 30-90 days is a reasonable investment to validate months of diagnostic work.
5. If Phase 13A confirms similar performance, the project can consider Phase 14 (real execution with small capital).

## Phase 13A Constraints (if approved)

If PM approves Phase 13A, it must be:
- **Future-only:** No historical backfill. Only new incoming data.
- **Paper only:** No real capital. No real orders.
- **No exchange connection:** No API calls to any exchange.
- **No real order placement:** Pure monitoring.
- **Monitoring only:** Track signal, turnover, spread, cost, liquidity.
- **Duration:** 30-90 days minimum before Phase 14 decision.
- **No alpha claim:** Phase 13A is validation, not production.
- **No production claim:** Phase 13A is diagnostic.

## PM Decision

**Decision:** PENDING

**Reviewer:** ________________

**Date:** ________________

**Notes:**
