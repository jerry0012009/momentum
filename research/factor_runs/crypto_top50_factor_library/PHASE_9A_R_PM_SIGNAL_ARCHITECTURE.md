# Phase 9A-R Closeout — PM Signal Architecture Specification

> Date: 2026-06-15
> Previous phase: Phase 8B COMPLETE
> Scope: Design / specification only
> PM decision: Structured multi-factor signal architecture with role assignment

---

## Status

Phase 9A-R: COMPLETE, pending PM review.
Phase 9 (design): IN PROGRESS.
Phase 10: NOT STARTED.

---

## 1. PM Rationale

The PM directed that Phase 9 must NOT use a naive 10-factor equal-weight signal.
Instead, factors are assigned structural roles in a multi-factor signal architecture:

1. **Core risk/reversion signal** — risk pressure + oscillator exhaustion
2. **Position/timing overlay** — range and price-location modulation
3. **Liquidity/participation gate** — confidence modulation via cross-sectional volume rank

This architecture separates directional alpha candidates (risk + oscillator)
from conditional modulators (position timing) and confidence gates (liquidity).

---

## 2. Factor Role Map Summary

### Channel 1: RISK_PRESSURE (4 factors)

| factor_id | pm_role | expected_direction |
|-----------|---------|-------------------|
| vol_5h | CORE_RISK_REVERSION | negative |
| vol_40h | CORE_RISK_REVERSION | negative |
| downside_vol_20h | CORE_RISK_REVERSION | negative |
| vol_of_vol_20h | CORE_RISK_REVERSION | negative |

### Channel 2: TECHNICAL_REVERSION (2 factors)

| factor_id | pm_role | expected_direction |
|-----------|---------|-------------------|
| rsi_7h | OSCILLATOR_EXHAUSTION | negative |
| rsi_28h | OSCILLATOR_EXHAUSTION | negative |

### Channel 3: RANGE_POSITION (3 factors)

| factor_id | pm_role | expected_direction |
|-----------|---------|-------------------|
| range_1h | POSITION_TIMING_OVERLAY | conditional |
| range_4h | POSITION_TIMING_OVERLAY | conditional |
| price_pos_24h | POSITION_TIMING_OVERLAY | conditional |

### Channel 4: LIQUIDITY_GATE (1 factor)

| factor_id | pm_role | expected_direction |
|-----------|---------|-------------------|
| xs_rank_vol | LIQUIDITY_PARTICIPATION_GATE | conditional |

---

## 3. Component Structure

| Component | Factors | Role | Alpha Component |
|-----------|---------|------|-----------------|
| risk_pressure_component | vol_5h, vol_40h, downside_vol_20h, vol_of_vol_20h | Cross-sectional realized risk pressure | TRUE |
| oscillator_exhaustion_component | rsi_7h, rsi_28h | Oscillator exhaustion / mean-reversion | TRUE |
| position_timing_overlay | range_1h, range_4h, price_pos_24h | Timing / price-location overlay | CONDITIONAL |
| liquidity_participation_gate | xs_rank_vol | Confidence / participation gate | FALSE_OR_GATE |

---

## 4. Basket Design

| Basket | Factors | Role | PM Priority | Status |
|--------|---------|------|-------------|--------|
| basket_1_core_risk_reversion | 6 (risk + oscillator) | Core score candidate | 2 | DESIGN_ONLY |
| basket_2_position_timing_overlay | 3 (range + position) | Timing overlay | 3 | DESIGN_ONLY |
| basket_3_liquidity_gated_core | 7 (risk + oscillator + gate) | PM-preferred production | 1 | DESIGN_ONLY |
| basket_4_family_balanced_all_candidate | 10 (all) | Diagnostic comparison | 5 | DESIGN_ONLY |
| basket_5_minimal_robust_candidate | 6 (reduced) | Robustness diagnostic | 4 | DESIGN_ONLY |

**PM-preferred basket: `basket_3_liquidity_gated_core`**
- Risk pressure (60%) + oscillator exhaustion (40%) = raw core score
- Liquidity gate (xs_rank_vol) modulates confidence
- Gate does not flip signal direction

---

## 5. PM-Preferred Architecture

**Liquidity-gated core risk/reversion signal:**

```
raw_core_score = 0.60 * risk_pressure_component + 0.40 * oscillator_exhaustion_component
gated_score = raw_core_score * liquidity_confidence_modifier
final_score = gated_score * (1 + position_timing_overlay_adjustment)  [capped]
```

Key properties:
- Core signal: risk pressure + oscillator exhaustion (directional alpha candidates)
- Gate: xs_rank_vol adjusts confidence but does not flip direction
- Overlay: range/position factors adjust exposure intensity but must not dominate
- All structural weights are PM-specified; no optimization

---

## 6. Transformation Rules

| Rule | Key Constraint |
|------|---------------|
| Cross-sectional winsorization | Robust-clip per timestamp |
| Cross-sectional z-score/rank | Standardize before combining |
| Direction adjustment | Use catalog expected_direction only |
| Conditional factor handling | Document hypothesis; do not infer from returns |
| Liquidity gate handling | xs_rank_vol as gate; not standalone alpha |
| Missing data policy | Exclude symbol; do not impute |
| Dynamic universe warning | Diagnostic only; not true PIT |

**Forbidden inputs:** forward returns, labels, fitted weights.

---

## 7. Negative Declarations

- **No backtest was run.** Phase 9A-R is design/specification only.
- **No PnL was computed.**
- **No portfolio simulation was created.**
- **No alpha claim was made.** CANDIDATE_REVIEW is not alpha.
- **No label or forward return was used.**
- **No weights were optimized against future returns.**
- **Phase 10 has not started.**
- **Phase 9B requires PM approval after 9A-R review.**

---

## 8. Deliverables

| Deliverable | File | Description |
|-------------|------|-------------|
| Factor role map | `phase9a_r_factor_role_map.csv` | 10-factor role assignment |
| Component spec | `phase9a_r_signal_component_spec.csv` | 4 component definitions |
| Basket plan | `phase9a_r_signal_basket_plan.csv` | 5 basket designs |
| Weighting policy | `phase9a_r_weighting_policy.csv` | PM-specified structural weights |
| Transformation rules | `phase9a_r_transformation_rules.csv` | 7 transformation rules |
| Pre-implementation checklist | `phase9a_r_pre_implementation_checklist.csv` | 13 verification checks |
| Closeout | `PHASE_9A_R_PM_SIGNAL_ARCHITECTURE.md` | This document |

---

## 9. Next Required PM Decision

Phase 9B (signal implementation) may **only** begin after:

1. PM reviews the signal architecture specification.
2. PM explicitly approves entry into Phase 9B.
3. Phase 9B scope is defined (which baskets to implement first).

**No action is taken automatically.** All decisions require explicit PM approval.
