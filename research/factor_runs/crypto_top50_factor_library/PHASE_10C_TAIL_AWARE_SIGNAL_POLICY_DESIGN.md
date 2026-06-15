# Phase 10C Closeout — Tail-Aware Signal Policy Design

> Date: 2026-06-15
> Previous: Phase 10B-lite COMPLETE
> Scope: Design-only. No signal v1 implementation. No backtest. No Phase 11.

---

## Status

Phase 10C: COMPLETE, pending PM review.
Phase 10D: NOT STARTED (requires PM approval).
Phase 11: NOT STARTED. Phase 12: NOT STARTED. Phase 13: NOT STARTED.

---

## 1. What Phase 10B Found

Phase 10B-lite diagnosed the RankIC-positive / spread-negative inconsistency:

- **Median spread is POSITIVE** for 11/12 signal×horizon combos
- **Mean spread is NEGATIVE** for all 12 combos — driven by outlier-dominated distribution
- **Bucket 0** (lowest-signal decile) has structurally higher returns (~0.0003 vs ~0 for buckets 1-4)
- **Bucket 0 concentration** is moderate (top 1% ≈ 11%), not driven by a few extreme outliers
- **Winsorized spreads** are still negative but 5-15% smaller than standard
- **Tail-trim spreads** (ex bucket 0) are still negative but 50-70% smaller
- Diagnosis: **MEAN_SPREAD_OUTLIER_DOMINATED** (11/12), **ROBUST_SPREAD_STILL_NEGATIVE** (1/12)

---

## 2. PM-Modified Interpretation

The signal has value for the **median cross-section** (RankIC positive for 1h/4h, median spread positive for 11/12 combos). The negative mean spread is not evidence that the signal "doesn't work" — it is evidence that the **evaluation framework was wrong** (mean spread is not the right metric when tails are non-linear).

The correct response is NOT to flip the signal. The correct response is:
1. Use median/winsorized/tail-trim metrics alongside mean spread
2. Guard against bucket 0 exposure in the short leg
3. Evaluate horizon-specific direction separately

---

## 3. Selected Policy

**PM Recommended: POLICY_F — HYBRID_BUCKET0_GUARD_PLUS_HORIZON_DIRECTION**

Components:
1. **Bucket 0 guard**: Do not short symbols in the bottom signal decile
2. **Horizon-specific direction**: Keep original for 1h/4h; evaluate inverted for 24h/72h
3. **Multi-metric evaluation**: Median spread, winsorized spread, tail-trim spread as primary metrics (not just mean spread)

This is the most comprehensive policy and addresses all three identified issues simultaneously.

---

## 4. Why Not Go Directly to Phase 11

Phase 11 handles costs, slippage, and capacity. Before adding transaction costs, we must first establish:
- Whether the signal works at all with a tail-aware evaluation framework
- Whether the bucket 0 guard actually resolves the mean-spread negativity
- Whether horizon-specific direction is needed or if bucket 0 guard alone suffices

Going to Phase 11 without this foundation would mean evaluating costs on a signal whose basic direction and evaluation framework are still uncertain.

---

## 5. What Phase 10D Should Do

Phase 10D will:
1. Implement signal v1 variants (original + inverted, with + without bucket 0 guard)
2. Evaluate all variants across 3 signals × 4 horizons using the multi-metric framework
3. Determine which variants pass the evaluation criteria (RankIC > 0, median spread > 0, tail-trim spread > 0)
4. Report results to PM for Phase 11 gating decision

Phase 10D will NOT:
- Add costs, slippage, or capacity
- Optimize weights or parameters
- Make alpha claims
- Enter Phase 11

---

## 6. Negative Declarations

- No signal v1 was implemented.
- No backtest was run.
- No Phase 10A/10A-R/10B results were modified.
- No alpha claim.
- No cost/slippage/capacity.
- Phase 11/12/13 NOT STARTED.
