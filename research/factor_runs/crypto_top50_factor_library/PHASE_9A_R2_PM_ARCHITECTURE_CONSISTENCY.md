# Phase 9A-R2 Closeout — PM Architecture Consistency & Docs Patch

> Date: 2026-06-15
> Previous phase: Phase 9A-R COMPLETE
> Scope: Resolve PM architecture ambiguity; docs synchronization
> PM decision: Full 10-factor structured architecture is the true PM-preferred design

---

## Status

Phase 9A-R2: COMPLETE, pending PM review.
Phase 9 (design): IN PROGRESS.
Phase 10: NOT STARTED.

---

## 1. Problem Resolved

Phase 9A-R had an ambiguity:

- `basket_3_liquidity_gated_core` (7 factors) was marked as PM-preferred production.
- But the closeout formula included `position_timing_overlay_adjustment` using range_1h, range_4h, and price_pos_24h.
- This implied the true PM-preferred design is a 10-factor full structured architecture.

**PM decision:** The true PM-preferred architecture is the 10-factor full structured design.

---

## 2. Architecture Resolution

### PM-Preferred: `basket_6_pm_full_structured_architecture` (10 factors)

```
final_score = raw_core_score × liquidity_gate × position_overlay_multiplier
```

Where:
- `raw_core_score` = 60% risk_pressure_component + 40% oscillator_exhaustion_component
  - risk_pressure_component: vol_5h, vol_40h, downside_vol_20h, vol_of_vol_20h (equal weight)
  - oscillator_exhaustion_component: rsi_7h, rsi_28h (equal weight)
- `liquidity_gate` = xs_rank_vol-based confidence modifier (capped; does not flip direction)
- `position_overlay_multiplier` = capped modifier from range_1h, range_4h, price_pos_24h

### Demoted basket

- `basket_3_liquidity_gated_core` (7 factors) remains useful as a core-gated intermediate basket.
- It is no longer the final PM-preferred production architecture.
- pm_priority demoted from 1 to 2.

---

## 3. Updated Basket Priority

| Basket | PM Priority | Status |
|--------|-------------|--------|
| basket_6_pm_full_structured_architecture | 1 (PM-preferred) | DESIGN_ONLY |
| basket_3_liquidity_gated_core | 2 | DESIGN_ONLY |
| basket_1_core_risk_reversion | 3 | DESIGN_ONLY |
| basket_2_position_timing_overlay | 4 | DESIGN_ONLY |
| basket_5_minimal_robust_candidate | 5 | DESIGN_ONLY |
| basket_4_family_balanced_all_candidate | 6 | DESIGN_ONLY |

---

## 4. Key Implementation Constraints

- **No labels or forward returns** used in any policy or rule.
- **No optimization** of weights against future returns.
- **No backtest** computed.
- **No PnL** computed.
- **No portfolio simulation** created.
- **No alpha claim** made.
- All baskets remain DESIGN_ONLY.
- Phase 9B requires PM approval after 9A-R2 review.

---

## 5. Deliverables

| Deliverable | File | Description |
|-------------|------|-------------|
| Updated basket plan | `phase9a_r2_signal_basket_plan.csv` | 6 baskets; basket_6 = PM-preferred |
| Updated weighting policy | `phase9a_r2_weighting_policy.csv` | 6 policies; pm_full_structured added |
| Updated transformation rules | `phase9a_r2_transformation_rules.csv` | 9 rules; overlay cap + gate cap + formula added |
| Closeout | `PHASE_9A_R2_PM_ARCHITECTURE_CONSISTENCY.md` | This document |

---

## 6. Negative Declarations

- **No backtest was run.** Phase 9A-R2 is design/specification only.
- **No PnL was computed.**
- **No portfolio simulation was created.**
- **No alpha claim was made.** CANDIDATE_REVIEW is not alpha.
- **No label or forward return was used.**
- **No weights were optimized against future returns.**
- **Phase 10 has not started.**
- **Phase 9B requires PM approval after 9A-R2 review.**

---

## 7. Next Required PM Decision

Phase 9B (Deterministic Signal Panel Implementation) may **only** begin after:

1. PM reviews the updated architecture specification (9A-R + 9A-R2).
2. PM explicitly approves entry into Phase 9B.
3. Phase 9B scope is defined (implement which baskets first).

**No action is taken automatically.** All decisions require explicit PM approval.
