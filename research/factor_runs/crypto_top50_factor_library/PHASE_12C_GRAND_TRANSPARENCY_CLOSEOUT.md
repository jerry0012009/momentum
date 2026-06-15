# Phase 12C — Grand Transparency, Learning & PM Decision Closeout

> Date: 2026-06-15
> Author: Hermes Agent (automated)
> Status: COMPLETE, pending PM review

---

## 1. Executive Summary

This document is the full-stage transparency and learning closeout for the crypto cross-sectional momentum factor library project, covering Phase 7 through Phase 12B.

**Bottom line:** One candidate — `signal_v0_core_only__1h__original_no_guard` — has survived a rigorous multi-phase diagnostic pipeline. It produces a thin but positive gross spread (+0.051%/hour mean), survives turnover-adjusted mid-cost assumptions (+0.209 cumulative over 30 days), and operates within a 43-symbol liquidity universe. No real execution has occurred. No alpha claim is made. The project is ready for PM decision on whether to proceed to Phase 13A (future paper validation only).

## 2. Current Final Candidate

| Field | Value |
|-------|-------|
| Candidate ID | `signal_v0_core_only__1h__original_no_guard` |
| Source Phase | Phase 11B (cost+capacity diagnostic) |
| Status | `PAPER_SIGNAL_DIAGNOSTIC_ONLY` |
| Allowed for real execution | FALSE |
| Signal | `signal_v0_core_only` (equal-weight combination of 10 diagnostic factors) |
| Horizon | 1h |
| Bucket0 guard | None (no_guard) |
| Universe | 43 symbols with liquidity data |
| Gross exposure | 1.0 (0.5 long + 0.5 short) |
| Net exposure | 0.0 |

## 3. Why Only This Candidate Remains

The project evaluated 3 signals × 4 horizons × 4 variants = 48 total variants in Phase 10D. Of these:

- **Phase 10D-R:** 9/48 passed RankIC + median spread criteria (all 1h and 4h, original direction, with and without bucket0 guard)
- **Phase 11A:** 1/9 survived cost diagnostic — only `core_only 1h no_guard` survived low-cost assumptions. All bucket0 guard variants failed due to higher turnover eating the spread improvement. All 4h variants failed due to higher per-rebalance turnover.
- **Phase 11B:** Capacity analysis confirmed the bottleneck is cost, not capacity. Median capacity at 1% participation: $660k.
- **Phase 12A:** Paper signal harness built for the single survivor.
- **Phase 12B:** Rolling 30-day monitoring confirmed the signal survives mid-cost assumptions when cost is properly scaled by actual turnover (not per-rebalance full cost).

**Why pm_full and family_balanced failed:** These signals add more factors but do not improve gross spread. The additional factors (range_1h, range_4h, price_pos_24h as position overlay; xs_rank_vol as liquidity gate) add noise without improving cross-sectional ranking power. `core_only` consistently produces the highest gross spread among all signal variants.

**Why bucket0_guard failed:** The guard excludes the lowest-decile bucket from the short leg, which reduces spread (by removing the most extreme short candidates) while increasing turnover (more symbols change when bucket 0 is dynamically excluded). The net effect is negative after costs.

**Why 4h failed:** Per-rebalance turnover is higher for 4h (50% vs 18.8% for 1h) because 4 hours of signal evolution causes more position changes between rebalances. The 4h forward return spread does not proportionally increase to compensate.

## 4. What Failed and Why

### Factors dropped during Phase 7-8 screening (8 factors)
- `momentum_1h`, `momentum_4h`, `momentum_24h`, `momentum_72h`: Redundant with each other and with the signal itself.
- `vol_5h_raw`, `vol_40h_raw`, `rsi_7h_raw`, `rsi_28h_raw`: Non-normalized versions had unstable cross-sectional properties.

### Signals that did not survive cost diagnostic
- `signal_v0_pm_full_structured`: Added position overlay (range_1h, range_4h, price_pos_24h) and liquidity gate (xs_rank_vol). Did not improve gross spread vs core_only. Same cost drag, lower net.
- `signal_v0_family_balanced_diagnostic`: Similar to pm_full with different weighting. Same result.

### Variants that failed
- All `inverted` variants: Negative RankIC in original direction evaluation. Inverting the signal does not improve cross-sectional power.
- All `bucket0_guard` variants: Improved median spread in Phase 10D-R but increased turnover enough to fail cost diagnostic in Phase 11A.
- All 4h variants: Higher per-rebalance turnover without proportional spread increase.

## 5. What Worked and Why

### Cross-sectional momentum signal (core_only)
The 10 diagnostic factors, equal-weighted, produce a consistent cross-sectional ranking. The signal captures short-term momentum (vol_5h, rsi_7h), medium-term momentum (vol_40h, rsi_28h), tail risk (downside_vol_20h, vol_of_vol_20h), and relative position (range_1h, range_4h, price_pos_24h). The equal-weight combination is robust to individual factor noise.

### Rolling paper monitoring (Phase 12B)
- 721 hourly timestamps over 30 days
- Gross spread: +0.370 cumulative
- Low-cost net (7bps): +0.295 (POSITIVE)
- Mid-cost net (15bps): +0.209 (POSITIVE)
- Turnover: median 12.5%, manageable
- Only 1 alert (turnover spike)

### Turnover-adjusted cost model
Phase 11A used a per-rebalance full-cost model (cost × full turnover every period), which was overly pessimistic. Phase 12B used actual per-timestamp turnover, giving a more realistic cost picture. The signal survives mid-cost when costs are properly scaled.

## 6. What Remains Uncertain

1. **Thin gross spread:** Mean 0.051%/hour is small. A few bad hours can erase days of gains.
2. **30-day monitoring window:** Too short to capture different market regimes (bull, bear, sideways, high-vol, low-vol).
3. **Historical backfill vs true future:** Phase 12B used historical data. True out-of-sample performance is unknown.
4. **43-symbol universe:** Limited liquidity coverage. May not scale.
5. **Execution cost uncertainty:** Real slippage may differ from diagnostic assumptions.
6. **Label alignment risk:** Forward return labels may have subtle timestamp alignment issues.
7. **Model overfitting:** Equal-weight is simple but may be overfit to the specific dataset.

## 7. PM Decision Options

| Option | Description | Risk |
|--------|-------------|------|
| **A. Phase 13A future paper validation** | Continue monitoring on live data (no real execution) for 30-90 days | Low risk, validates forward performance |
| **B. Extend Phase 12B monitoring** | Run longer historical backfill (90-180 days) before Phase 13 | Low risk, more data, but still historical |
| **C. Return to signal redesign** | Go back to Phase 9/10 to build a higher-spread signal | Medium risk, may find better signal, may not |
| **D. Pause project** | Stop and revisit later | No risk, no progress |

## 8. Phase 13 Readiness Status

**Phase 13 NOT STARTED.** Phase 13A (future paper validation) is the only recommended next step. It must be:
- Future-only (no historical backfill)
- Paper only (no real capital)
- No exchange connection
- No real order placement
- Monitoring only, for 30-90 days

## 9. Clear Recommendation

**Proceed to Phase 13A future paper validation only.**

Rationale:
- The signal has survived all diagnostic gates
- Rolling paper monitoring confirms cost viability
- The main risk is forward performance validation
- Phase 13A addresses this with zero capital risk
- If Phase 13A confirms similar performance over 30-90 days, the project can consider Phase 14 (real execution with small capital)

---

## Negative Declarations

- Phase 13 NOT STARTED
- No real execution
- No final production model
- No alpha claim
- Current result is diagnostic paper monitoring only
