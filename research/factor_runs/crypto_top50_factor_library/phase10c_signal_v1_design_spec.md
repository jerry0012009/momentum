# Phase 10C — Signal v1 Design Spec

> Design-only. No implementation. No backtest. No Phase 11.

---

## 1. Current Signal v0 Architecture

Three signals exist from Phase 9B:

- `signal_v0_core_only`: 6-factor core (risk pressure + oscillator), z-scored cross-sectionally
- `signal_v0_pm_full_structured`: 10-factor full PM architecture (core × liquidity_gate × position_overlay)
- `signal_v0_family_balanced_diagnostic`: 10-factor equal-weight 4-channel (diagnostic only)

All three suffer from the same tail nonlinearity: bucket 0 (lowest-signal decile) has structurally higher returns than buckets 1-4, causing mean long-short spread to be negative while median spread is positive.

---

## 2. Is `signal_v0_pm_full_structured` Retained as Core?

**Yes, with modifications.** The PM-preferred v0 signal (`signal_v0_pm_full_structured`) remains the base architecture. Its structure (core × liquidity_gate × position_overlay) is sound. The problem is not the signal construction — it is the evaluation framework (mean spread vs. median spread) and the short-leg bucket 0 exposure.

Signal v1 will be built on top of `signal_v0_pm_full_structured` with two additions:
1. Bucket 0 guard on the short leg
2. Horizon-specific direction policy

---

## 3. Bucket 0 Guard

**Rule**: Do not short any symbol whose signal rank is in the bottom decile (bucket 0) at the time of signal evaluation.

**Rationale**: Bucket 0 has structurally higher returns (mean ≈ 0.0003 vs. buckets 1-4 ≈ 0). Shorting bucket 0 is the primary source of negative mean spread. Removing bucket 0 from the short leg eliminates the dominant outlier effect.

**Implementation in Phase 10D**:
- At each timestamp, rank symbols by signal value
- Bottom 10% (bucket 0) are excluded from the short leg
- Short leg is drawn from bucket 1 (next-lowest 10%) instead
- Long leg remains top 20% unchanged
- This is a diagnostic guard, not a trading rule

---

## 4. Evaluation Metrics for Phase 10D

Phase 10D will use a **multi-metric evaluation framework**:

| Metric | Role | Why |
|--------|------|-----|
| RankIC | Primary | Direction-agnostic rank correlation; positive for 1h/4h |
| Median spread | Primary | Robust to outliers; positive for 11/12 combos |
| Mean spread | Secondary | Standard metric but outlier-dominated; report but do not rely on |
| Winsorized spread (1-99%) | Secondary | Partially robust; still negative but smaller |
| Tail-trim spread (ex bucket 0) | Primary guard check | Directly measures bucket 0 impact |
| Bucket 0 guard check | Gate | Verify short leg has no bucket 0 exposure |

**Decision rule**: A signal variant passes Phase 10D if:
- RankIC > 0 (statistically significant, t-stat > 2)
- Median spread > 0
- Tail-trim spread > 0 (bucket 0 excluded)
- No cost/slippage/capacity in Phase 10D

---

## 5. Horizon-Specific Direction Policy

| Horizon | 1h/4h | 24h/72h |
|---------|-------|---------|
| RankIC direction | Positive | Negative (inverted helps) |
| Median spread | Positive | Positive (inverted) |
| Proposed policy | Keep original signal direction | Evaluate inverted signal direction |
| Bucket 0 guard | Apply | Apply |

**Rationale**:
- 1h/4h: RankIC is positive, median spread is positive → signal direction is correct for the typical cross-section. Bucket 0 guard removes the outlier effect.
- 24h/72h: RankIC is negative, inversion improves both RankIC and spread → signal direction should be inverted for these horizons. Bucket 0 guard still applies.

---

## 6. What Enters Phase 10D

Phase 10D will evaluate **four signal variants**:

| Variant | Description | Horizons |
|---------|-------------|----------|
| `v1_original_with_guard` | v0 signal + bucket 0 guard on short leg | 1h, 4h, 24h, 72h |
| `v1_inverted_with_guard` | v0 signal × -1 + bucket 0 guard | 24h, 72h only |
| `v1_original_no_guard` | v0 signal, no bucket 0 guard (baseline) | 1h, 4h, 24h, 72h |
| `v1_inverted_no_guard` | v0 signal × -1, no guard (baseline) | 24h, 72h only |

Each variant × horizon combination will be evaluated with:
- RankIC (mean, std, t-stat, positive rate)
- Median spread
- Mean spread (secondary)
- Winsorized spread (secondary)
- Tail-trim spread (guard check)
- Bucket 0 exposure in short leg (must be 0 for guard variants)

---

## 7. What Does NOT Enter Phase 10D

- No cost model
- No slippage model
- No capacity analysis
- No portfolio optimization
- No position sizing beyond equal-weight diagnostic
- No alpha claim
- No tradeable/live claim
- No paper trading
- Phase 11 handles costs (if PM approves after 10D)

---

## 8. Summary

Signal v1 design = v0 signal + bucket 0 guard + horizon-specific direction.

The key insight from Phase 10A-R and 10B: the signal's rank correlation is positive for short horizons and the median spread is positive across all horizons. The negative mean spread is driven by bucket 0 structural outliers in the short leg. Removing bucket 0 from the short leg (guard) is the minimal intervention that addresses the root cause.

Phase 10D will validate this design with multi-metric evaluation across all signal × horizon × guard × direction combinations.
