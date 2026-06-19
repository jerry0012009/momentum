# Signal Composition Review

**Phase**: 12D-H10 Signal Composition Review
**Generated**: 2026-06-19T17:00:00+08:00
**Status**: Diagnostic review only. No signal modified, no factor added, no production claim.

---

## Executive Summary

The current signal panel uses **10 factors** across **3 variants**. All factors are
direction-adjusted and cross-sectionally z-scored before combination.

**Key findings:**

1. **All 10 signal factors show significant factor-level IC** (|adj IC| > 0.019 at 1h, all t-stat > 16).
2. **Volatility family dominates** — 4 of 10 factors are volatility-based (vol_5h, vol_40h, downside_vol_20h, vol_of_vol_20h), contributing 40% of signal weight.
3. **Several strong non-signal factors exist** — volatility_20h (adj IC 1h = 0.039), bb_zscore_20h (0.030), rsi_14h (0.028), and q158_high_low_range (0.037) are NOT in the current signal.
4. **RankIC is positive but spread is negative** — all 3 variants show this pattern, indicating bucket 0 tail non-linearity (the lowest-signal quintile has extreme positive returns). This is a known diagnostic issue documented in Phase 10A.
5. **Core_only performs best** on RankIC across all horizons; pm_full_structured slightly degrades vs core; family_balanced_diagnostic further degrades.
6. **Cost diagnostic FAILS for most variants** — only core_only 1h no_guard survives low-cost scenario. All other variants and horizons are cost-sensitive.
7. **No variant qualifies as "ready for production"** — all are diagnostic/paper only.

**PM recommendation**: Continue paper diagnostic. Investigate bucket 0 tail behavior before
attempting signal modification. The current signal composition is reasonable for a first-generation
diagnostic signal but needs improvement in tail risk management.

---

## A. Current Signal Factors: Single-Factor IC

| Factor | Family | Direction | Role | Adj IC 1h | Adj IC 4h | Adj IC 24h | Adj IC 72h | t-stat 1h | Coverage |
|--------|--------|-----------|------|-----------|-----------|------------|------------|-----------|----------|
| vol_5h | volatility | negative | risk_pressure | 0.034 | 0.047 | 0.073 | 0.081 | 23.4 | 99.96% |
| vol_40h | volatility | negative | risk_pressure | 0.038 | 0.057 | 0.092 | 0.104 | 23.6 | 99.7% |
| downside_vol_20h | volatility | negative | risk_pressure | 0.029 | 0.044 | 0.074 | 0.090 | 18.2 | 99.8% |
| vol_of_vol_20h | volatility | negative | risk_pressure | 0.030 | 0.046 | 0.073 | 0.080 | 22.2 | 99.8% |
| rsi_7h | technical | negative | oscillator | 0.030 | 0.033 | 0.023 | 0.012 | 29.2 | 99.9% |
| rsi_28h | technical | negative | oscillator | 0.025 | 0.033 | 0.032 | 0.018 | 23.8 | 99.8% |
| xs_rank_vol | liquidity | conditional | liquidity_gate | 0.019 | 0.029 | 0.055 | 0.069 | 16.8 | 99.8% |
| range_1h | range_position | conditional | position_overlay | 0.037 | 0.053 | 0.081 | 0.091 | 24.1 | 100.0% |
| range_4h | range_position | conditional | position_overlay | 0.036 | 0.053 | 0.081 | 0.092 | 23.5 | 99.98% |
| price_pos_24h | price_position | conditional | position_overlay | 0.021 | 0.021 | 0.010 | 0.001 | 20.7 | 99.8% |

**Observation**: The 4 volatility factors (risk_pressure component) have strong IC at longer horizons
(24h, 72h) but the 2 technical factors (oscillator component) are stronger at shorter horizons (1h, 4h).
The overlay factors (range, price_pos) are strong standalone but serve as modifiers, not primary signals.

---

## B. Top Factors NOT in Current Signal

### Top 15 by Direction-Adjusted IC at 1h

| Rank | Factor | Family | Adj IC 1h | In Signal? | Why Not? | Recommendation |
|------|--------|--------|-----------|------------|----------|----------------|
| 1 | volatility_20h | volatility | 0.039 | No | Family already has 4 factors | diagnostic_candidate |
| 2 | rev_3h | reversal | 0.034 | No | Reversal family not represented | diagnostic_candidate |
| 3 | q158_high_low_range | alpha158 | 0.037 | No | Direction unknown (conditional) | diagnostic_candidate |
| 4 | range_1h | range_position | 0.037 | Yes | — | already_in_signal |
| 5 | range_4h | range_position | 0.036 | Yes | — | already_in_signal |
| 6 | vol_40h | volatility | 0.038 | Yes | — | already_in_signal |
| 7 | xs_rank_ret_1h | cross_sectional | 0.037 | No | Direction unknown | diagnostic_candidate |
| 8 | vol_5h | volatility | 0.034 | Yes | — | already_in_signal |
| 9 | rsi_14h | technical | 0.028 | No | Family already has 2 factors | worth_monitoring |
| 10 | bb_zscore_20h | technical | 0.030 | No | Family already has 2 factors | worth_monitoring |
| 11 | reversal_5h | momentum | 0.032 | No | Classified as momentum (reversal) | diagnostic_candidate |
| 12 | vol_of_vol_20h | volatility | 0.030 | Yes | — | already_in_signal |
| 13 | rsi_7h | technical | 0.030 | Yes | — | already_in_signal |
| 14 | candle_body | candle | 0.031 | No | Direction unknown (conditional) | worth_monitoring |
| 15 | downside_vol_20h | volatility | 0.029 | Yes | — | already_in_signal |

### Top 15 by Direction-Adjusted IC at 72h

| Rank | Factor | Family | Adj IC 72h | In Signal? | Recommendation |
|------|--------|--------|------------|------------|----------------|
| 1 | vol_40h | volatility | 0.104 | Yes | already_in_signal |
| 2 | volatility_20h | volatility | 0.100 | No | diagnostic_candidate |
| 3 | q158_high_low_range | alpha158 | 0.091 | No | diagnostic_candidate |
| 4 | range_4h | range_position | 0.092 | Yes | already_in_signal |
| 5 | downside_vol_20h | volatility | 0.090 | Yes | already_in_signal |
| 6 | range_1h | range_position | 0.091 | Yes | already_in_signal |
| 7 | range_24h | range_position | 0.094 | No | diagnostic_candidate |
| 8 | vol_of_vol_20h | volatility | 0.080 | Yes | already_in_signal |
| 9 | vol_5h | volatility | 0.081 | Yes | already_in_signal |
| 10 | xs_rank_vol | liquidity | 0.069 | Yes | already_in_signal |
| 11 | xs_rank_ret_1h | cross_sectional | 0.005 | No | low_priority |
| 12 | rev_24h | reversal | 0.020 | No | worth_monitoring |
| 13 | mom_40h | momentum | 0.021 | No | worth_monitoring |
| 14 | rsi_28h | technical | 0.018 | Yes | already_in_signal |
| 15 | rsi_14h | technical | 0.016 | No | worth_monitoring |

### Key Observations

- **volatility_20h** is NOT in the signal but has the highest adj IC at 1h (0.039) and is #2 at 72h (0.100). It was excluded because the volatility family already has 4 factors. Adding it would further concentrate volatility exposure.
- **rev_3h / reversal_5h** show strong short-horizon reversal (adj IC 1h = 0.034 / 0.032). The reversal family is completely absent from the signal.
- **q158_high_low_range** shows strong IC across horizons but has unknown direction (conditional). It's functionally similar to range_1h.
- **bb_zscore_20h** and **rsi_14h** are the strongest technical factors not in the signal. Both are already represented by rsi_7h and rsi_28h.

---

## C. Family Concentration & Redundancy

### Signal Family Distribution

| Family | Count in Signal | Share | Total Computed | Avg Adj IC 1h | Redundancy Risk |
|--------|----------------|-------|----------------|---------------|-----------------|
| volatility | 4 | 40% | 6 | 0.033 | HIGH |
| technical | 2 | 20% | 8 | 0.028 | MEDIUM |
| liquidity | 1 | 10% | 1 | 0.019 | LOW |
| range_position | 2 | 20% | 5 | 0.037 | MEDIUM |
| price_position | 1 | 10% | 2 | 0.021 | LOW |

### All Computed Factors by Family

| Family | Computed Count | In Signal | Not in Signal | Top Adj IC 1h (not in signal) |
|--------|---------------|-----------|---------------|-------------------------------|
| volatility | 6 | 4 | 2 | volatility_20h: 0.039 |
| technical | 8 | 2 | 6 | bb_zscore_20h: 0.030, rsi_14h: 0.028 |
| range_position | 5 | 2 | 3 | range_24h: 0.033 |
| momentum | 5 | 0 | 5 | mom_5h: 0.032 |
| reversal | 4 | 0 | 4 | rev_3h: 0.034 |
| trend_ma | 3 | 0 | 3 | ma_gap_5_20: 0.016 |
| breakout | 2 | 0 | 2 | breakout_dist_20h: 0.021 |
| candle | 3 | 0 | 3 | candle_body: 0.031 |
| volume | 2 | 0 | 2 | vol_zscore_20h: 0.006 |
| quote_volume | 3 | 0 | 3 | qvol_zscore_48h: 0.007 |
| cross_sectional | 2 | 1 | 1 | xs_rank_ret_1h: 0.037 |
| wq101 | 3 | 0 | 3 | wq101_alpha53: 0.018 |
| alpha158 | 1 | 0 | 1 | q158_high_low_range: 0.037 |
| price_position | 2 | 1 | 1 | price_pos_72h: 0.016 |
| liquidity | 1 | 1 | 0 | — |

### Redundancy Diagnosis

**High redundancy risk**: The 4 volatility factors in the signal are:
- vol_5h: std(ret, 5)
- vol_40h: std(ret, 40)
- downside_vol_20h: std(min(ret,0), 20)
- vol_of_vol_20h: std(std(ret,5), 20)

These are all mathematically related — downside_vol_20h is a subset of volatility_20h,
and vol_of_vol_20h is a second-order volatility measure. They are expected to be
highly correlated (estimated pairwise Pearson > 0.8 within this family).

**Medium redundancy risk**: range_1h and range_4h are highly correlated (both measure
high-low range with different lookback). price_pos_24h is derived from the same 24h
high-low range.

**Medium redundancy risk**: rsi_7h and rsi_28h measure the same concept (RSI) with
different lookback periods. Expected correlation ~0.7-0.9.

**Low redundancy**: xs_rank_vol is a cross-sectional liquidity proxy, not redundant with
other factors.

**Net assessment**: The signal is heavily concentrated in volatility-family factors.
This creates a "volatility bet" — the signal will perform well when volatility is
mean-reverting and poorly when volatility trends. The 4 volatility factors provide
some diversification across lookback windows but share the same economic thesis.

---

## D. Signal Variant Comparison

### Variant Construction

| Variant | Risk Pressure Weight | Oscillator Weight | Liquidity Gate | Position Overlay | Factor Count |
|---------|---------------------|-------------------|----------------|------------------|--------------|
| core_only | 0.60 | 0.40 | No | No | 6 (vol×4 + rsi×2) |
| pm_full_structured | 0.60 | 0.40 | Yes (xs_rank_vol) | Yes (range_1h, range_4h, price_pos_24h) | 10 |
| family_balanced_diagnostic | 0.25 | 0.25 | Yes (centered) | Yes (0.25 each) | 10 |

### Performance Comparison (original, no_guard)

| Metric | core_only 1h | pm_full 1h | fam_bal 1h | core_only 24h | pm_full 24h | fam_bal 24h |
|--------|-------------|------------|------------|---------------|-------------|-------------|
| RankIC | 0.0325 | 0.0314 | 0.0303 | 0.0416 | 0.0378 | 0.0340 |
| t-stat | 17.57 | 17.43 | 17.13 | 22.60 | 21.08 | 19.49 |
| Spread | -0.0003 | -0.0003 | -0.0003 | -0.0067 | -0.0066 | -0.0066 |
| Positive Rate | 55.5% | 55.3% | 55.5% | 56.6% | 56.4% | 55.9% |
| Cumulative Spread | -5.35 | -5.54 | -5.57 | -118.0 | -115.4 | -115.9 |

### Key Questions Answered

**1. Should core_only remain the primary signal?**
Yes. It has the highest RankIC and simplest construction. Adding liquidity gate and position
overlay (pm_full_structured) slightly degrades RankIC without improving spread. The overlays
add complexity without clear benefit in current evaluation.

**2. Does pm_full_structured improve or degrade vs core?**
Slightly degrades. At 1h: RankIC drops from 0.0325 to 0.0314 (-3.4%). At 72h: drops from
0.0338 to 0.0267 (-20.7%). The position overlay appears to add noise at longer horizons.

**3. Is family_balanced_diagnostic only diagnostic or research-worthy?**
It's a diagnostic baseline. Its equal-weight construction tests whether forced family
diversification improves robustness. It consistently underperforms core_only on RankIC,
suggesting the volatility-heavy weighting in core is actually optimal for IC.

**4. Is signal-level performance consistent with factor-level IC?**
Partially. The signal-level RankIC (0.03-0.04) is lower than the sum of individual factor ICs
because z-score normalization and averaging compress the signal. The negative spread despite
positive RankIC indicates non-linear tail behavior (bucket 0 has extreme positive returns).

**5. Is there family overfit or redundancy?**
Yes, in the volatility family. Having 4 highly correlated volatility factors (all measuring
variance of returns) means the "risk_pressure" component is essentially a volatility factor
with 60% weight. This is a known design choice but creates concentration risk.

---

## E. Why Factor-Level IC ≠ Signal Selection

This section explicitly documents the distinction between factor diagnostics and signal construction:

1. **Factor-level IC is necessary but not sufficient.** A factor with high IC may be redundant
   with existing signal factors, reducing marginal contribution.

2. **High IC factors may be highly correlated.** Adding volatility_20h (IC=0.039) to a signal
   that already has vol_5h, vol_40h, downside_vol_20h, vol_of_vol_20h would increase
   volatility concentration without meaningful diversification.

3. **Single-factor IC does not guarantee combination improvement.** Two individually strong
   factors may cancel each other if they capture the same signal with opposite noise.

4. **Low IC factors may provide diversification.** xs_rank_vol (IC=0.019) has the lowest IC
   among signal factors but provides liquidity information orthogonal to the volatility/RSI
   components.

5. **Direction-adjusted IC is just the first filter.** Beyond IC, a factor needs:
   - Positive quantile spread (currently all signals show negative spread)
   - Survivability after transaction costs (most variants fail cost diagnostic)
   - Sufficient liquidity (capacity analysis deferred to Phase 11B)
   - Paper diagnostic validation (in progress)

6. **Current results do NOT constitute a tradeable alpha claim.** All signals are diagnostic
   only. The negative spread and cost sensitivity mean these signals cannot be directly
   deployed. Further research on tail risk management and cost reduction is needed.

---

## F. PM Recommendation

### Immediate Actions (Recommended)
1. **Continue paper diagnostic** for all 3 variants. Do not modify signal construction.
2. **Investigate bucket 0 tail behavior** — the lowest-signal quintile has extreme positive
   returns, causing RankIC-positive / spread-negative inconsistency. This needs root-cause
   analysis before any signal modification.
3. **Document redundancy** — factor-level correlation matrix between the 10 signal factors
   should be computed and published.

### Short-Term Research (Suggested for Next Phase)
4. **Reversal factor diagnostic** — rev_3h and reversal_5h show strong IC (0.034, 0.032)
   but are completely absent from the signal. A diagnostic variant including reversal factors
   could test whether they provide orthogonal information.
5. **Volatility deduplication test** — create a variant using only vol_40h (strongest) instead
   of all 4 volatility factors to test whether deduplication improves risk-adjusted performance.

### Not Recommended
- ❌ Do not add factors based solely on IC ranking
- ❌ Do not claim signal is ready for production
- ❌ Do not modify signal panel based on this review alone
- ❌ Do not start Phase 13 based on current results

---

## G. What NOT to Do

| Action | Status | Reason |
|--------|--------|--------|
| Modify signal panel | FORBIDDEN | No evidence that modification improves outcomes |
| Add new factors | FORBIDDEN | Needs systematic evaluation framework first |
| Claim alpha verified | FORBIDDEN | Negative spread + cost sensitivity = not verified |
| Claim production ready | FORBIDDEN | All variants are paper diagnostic only |
| Start Phase 13 | FORBIDDEN | Pre-conditions not met |
| Replace current signal | FORBIDDEN | core_only still performs best |

---

## H. Next Recommended Phase

The natural next step after this review would be:

1. **Bucket 0 tail analysis** — understand why the lowest-signal quintile has extreme positive returns
2. **Factor correlation matrix** — compute pairwise correlation between the 10 signal factors
3. **Reversal diagnostic variant** — test whether adding reversal factors improves the signal
4. **Volatility deduplication** — test whether reducing from 4 to 1-2 volatility factors improves risk-adjusted performance

None of these require modifying the current signal. They are diagnostic/research activities.

---

## Appendix: Data Sources

- Factor-level IC: `research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/factor_level_rankic_summary.csv`
- Signal-level RankIC: `research/factor_runs/crypto_top50_factor_library/phase10a_signal_rankic_summary.csv`
- Signal-level Spread: `research/factor_runs/crypto_top50_factor_library/phase10a_signal_quantile_spread_summary.csv`
- Variant Evaluation: `research/factor_runs/crypto_top50_factor_library/phase10d_variant_evaluation_summary.csv`
- Cost Summary: `research/factor_runs/crypto_top50_factor_library/phase11a_variant_cost_summary.csv`
- Direction Consistency: `research/factor_runs/crypto_top50_factor_library/phase10a_r_direction_consistency_check.csv`
- Signal Panel Script: `scripts/build_phase9b_signal_panel.py`

---

*This is a diagnostic document. It does not constitute investment advice, trading recommendations, or alpha claims.*
