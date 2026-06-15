# Signal Construction Handbook

> Phase 12C transparency documentation

---

## Overview

Three signal variants were constructed from the 10 candidate factors. Each produces a cross-sectional score per symbol per timestamp, which is then used to rank symbols and assign upper/lower sides for the paper signal.

## Signal Definitions

### signal_v0_core_only

**Factors used:** vol_5h, vol_40h, downside_vol_20h, vol_of_vol_20h, rsi_7h, rsi_28h (6 factors)

**Formula:**
```
raw_core_score = mean(z_score(vol_5h × -1), z_score(vol_40h × -1), 
                      z_score(downside_vol_20h × -1), z_score(vol_of_vol_20h × -1),
                      z_score(rsi_7h × -1), z_score(rsi_28h × -1))
signal_v0_core_only = raw_core_score
```

**Interpretation:** Equal-weight average of 6 normalized, sign-flipped factors. All factors are negative-direction (high value = bad), so the signal identifies symbols with the lowest combined risk/momentum scores as "upper side" (buy candidates) and highest as "lower side" (sell/short candidates).

**Why it survived:** Simple, robust, no additional parameters. The 6 factors capture volatility risk (3 measures) and momentum/mean-reversion (2 RSI measures) plus regime stability (vol-of-vol). Equal-weight avoids overfitting to any single factor.

### signal_v0_pm_full_structured

**Factors used:** All 10 factors

**Formula:**
```
raw_core_score = (same as core_only)
final_score = raw_core_score × liquidity_gate × position_overlay_multiplier

where:
  liquidity_gate = bounded(xs_rank_vol, 0.50, 1.00)
  position_overlay_multiplier = 1 + (-1 × mean(z_score(range_1h), z_score(range_4h), z_score(price_pos_24h)))
```

**Interpretation:** Core score modified by liquidity (down-weight illiquid symbols) and position timing overlay (reduce weight when price has already moved significantly).

**Why it failed:** The additional factors (xs_rank_vol, range_1h, range_4h, price_pos_24h) add noise without improving cross-sectional ranking power. The liquidity gate helps avoid illiquid symbols but doesn't improve gross spread. The position overlay assumes mean reversion within the rebalancing horizon, which is not consistently true.

### signal_v0_family_balanced_diagnostic

**Factors used:** All 10 factors, family-weighted

**Formula:**
```
family_weights = {vol_family: 0.4, momentum_family: 0.3, position_family: 0.3}
signal = weighted_average(factor_scores, family_weights)
```

**Interpretation:** Groups factors into families (volatility, momentum, position) and weights families rather than individual factors.

**Why it failed:** Similar to pm_full — the additional position factors don't improve results. The family weighting adds a layer of indirection without clear benefit.

## Why core_only Survived

1. **Simplicity:** 6 factors, equal-weight. No parameter tuning.
2. **Consistent direction:** All factors are negative-direction. No conflicting signals.
3. **No liquidity gate dependency:** Works without xs_rank_vol, which can be noisy.
4. **No position overlay dependency:** Avoids the debatable mean-reversion assumption.
5. **Highest gross spread:** Across all Phase 10D variants, core_only consistently produced the highest gross median spread.

## Why no_guard Survived (not bucket0_guard)

The bucket0_guard excludes the lowest-decile bucket from the short leg. This was intended to avoid shorting the most extreme losers (which may have microstructure issues).

**What happened:**
- Phase 10D-R: Guard improved median spread (from +0.010% to +0.015% for core_only 1h)
- Phase 11A: Guard increased turnover (from 18.8% to 28.6%) — more symbols change when bucket 0 is dynamically excluded
- Cost drag from higher turnover outweighed the spread improvement
- Net result: no_guard has better cost-adjusted performance

**Lesson:** A guard that improves spread but increases turnover can be net-negative after costs. Turnover is a first-order concern.

## Weight Convention

For paper signal generation:
- Gross exposure: 1.0
- Upper-side total weight: +0.5
- Lower-side total weight: -0.5
- Equal-weight within each side
- Net exposure: 0.0

This is a diagnostic paper convention. It does not represent a real portfolio.
