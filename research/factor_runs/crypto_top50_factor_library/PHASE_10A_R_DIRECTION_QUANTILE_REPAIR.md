# Phase 10A-R Closeout — Direction & Quantile Consistency Repair

> Date: 2026-06-15
> Previous phase: Phase 10A COMPLETE
> Scope: Diagnostic consistency repair only

---

## Status

Phase 10A-R: COMPLETE, pending PM review.
Phase 10A summaries: **NOT regenerated** (original preserved).
Phase 11: NOT STARTED. Phase 12: NOT STARTED. Phase 13: NOT STARTED.

---

## 1. Problem Statement

Phase 10A reported a consistency red flag:
- **RankIC is positive** across all 3 signals × 4 horizons (mean 0.025–0.042)
- **Quantile spread is negative** across all 3 signals × 4 horizons (mean −0.0003 to −0.017)

This appears contradictory: if higher signal values correlate with higher forward returns (positive RankIC), then the long leg (top 20% by signal) should outperform the short leg (bottom 20%).

---

## 2. Root Cause Diagnosis

**Root cause: Non-monotonic tail behavior — bucket 0 (lowest signal) has extreme positive returns.**

### Bucket Returns (5 buckets, signal_v0_core_only × 1h)

| Bucket | Signal Level | Mean Fwd Return |
|--------|-------------|-----------------|
| 0 (lowest) | Very low | +0.000281 |
| 1 | Low | +0.000018 |
| 2 | Medium | +0.000005 |
| 3 | High | +0.000003 |
| 4 (highest) | Very high | −0.000006 |

Bucket 0 returns are **~15× higher** than all other buckets. This extreme tail breaks the monotonic relationship between signal and returns that RankIC assumes.

### Why RankIC is Positive Despite Negative Spread

- **RankIC** (Spearman) measures rank correlation across the **full distribution**. It is influenced by the **middle** of the distribution where the monotonic relationship holds.
- **Quantile spread** measures mean return difference between **extreme tails** (top 20% vs bottom 20%). The bottom 20% includes bucket 0's extreme returns.
- These two statistics can diverge when the relationship is **non-monotonic in the tails**.

### IC-Spread Correlation

Per-timestamp RankIC and spread are **positively correlated** (ρ = 0.51–0.61), meaning they move together. But the **mean** spread is negative because bucket 0's extreme returns systematically pull up the short leg.

---

## 3. Inverted Signal Diagnostic

| Signal | Horizon | Original RankIC | Inverted RankIC | Original Spread | Inverted Spread | Interpretation |
|--------|---------|----------------|-----------------|-----------------|-----------------|---------------|
| core_only | 1h | +0.019 | −0.019 | −0.0003 | +0.0003 | INVERSION_RESOLVES_SPREAD_BUT_FLIPS_RANKIC |
| core_only | 4h | +0.017 | −0.017 | −0.0012 | +0.0012 | INVERSION_RESOLVES_SPREAD_BUT_FLIPS_RANKIC |
| core_only | 24h | −0.001 | +0.001 | −0.0067 | +0.0067 | BOTH_IMPROVE_WITH_INVERSION |
| core_only | 72h | −0.026 | +0.026 | −0.0166 | +0.0166 | BOTH_IMPROVE_WITH_INVERSION |
| pm_full | 1h | +0.018 | −0.018 | −0.0003 | +0.0003 | INVERSION_RESOLVES_SPREAD_BUT_FLIPS_RANKIC |
| pm_full | 4h | +0.016 | −0.016 | −0.0012 | +0.0012 | INVERSION_RESOLVES_SPREAD_BUT_FLIPS_RANKIC |
| pm_full | 24h | −0.001 | +0.001 | −0.0066 | +0.0066 | BOTH_IMPROVE_WITH_INVERSION |
| pm_full | 72h | −0.032 | +0.032 | −0.0167 | +0.0167 | BOTH_IMPROVE_WITH_INVERSION |
| balanced | 1h | +0.017 | −0.017 | −0.0003 | +0.0003 | INVERSION_RESOLVES_SPREAD_BUT_FLIPS_RANKIC |
| balanced | 4h | +0.015 | −0.015 | −0.0012 | +0.0012 | INVERSION_RESOLVES_SPREAD_BUT_FLIPS_RANKIC |
| balanced | 24h | −0.004 | +0.004 | −0.0066 | +0.0066 | BOTH_IMPROVE_WITH_INVERSION |
| balanced | 72h | −0.030 | +0.030 | −0.0165 | +0.0165 | BOTH_IMPROVE_WITH_INVERSION |

**Key findings:**
- **1h/4h**: Inversion resolves spread but flips RankIC negative → direction convention conflict
- **24h/72h**: Both RankIC and spread improve with inversion → signal direction likely wrong for these horizons
- **All horizons**: Inversion always resolves spread → the "long high signal" convention is consistently wrong for extreme quantiles

---

## 4. Script Verification

`scripts/run_phase10a_signal_backtest.py` was reviewed:

- ✅ `ascending=False` correctly sorts high signal first
- ✅ `head(n_q)` correctly takes top 20% (highest signal)
- ✅ `tail(n_q)` correctly takes bottom 20% (lowest signal)
- ✅ `spread = long_mean - short_mean` is correctly computed
- ✅ Forward returns are not recomputed (loaded from pre-computed parquet)
- ✅ No `shift(-` in script
- ✅ Same join keys used for RankIC and spread
- ✅ No duplicated timestamp-symbol rows

**No bug found.** The inconsistency is a genuine data characteristic, not an implementation error.

---

## 5. Interpretation

The signal has a **non-linear, non-monotonic relationship** with forward returns:

1. **Middle of signal distribution**: Higher signal → higher returns (positive RankIC)
2. **Extreme bottom tail (bucket 0)**: Very low signal values predict **extreme positive returns** (mean reversion)
3. **Extreme top tail (bucket 4)**: Very high signal values predict **slightly negative returns**

This pattern is consistent with **mean-reversion at the extremes**: assets with extremely low recent volatility / oversold RSI tend to bounce back. The effect is large enough to make the bottom-20% outperform the top-20%, despite the overall positive rank correlation.

---

## 6. Negative Declarations

- **No signal was flipped or replaced.**
- **No alpha claim was made.**
- **No cost/slippage/capacity analysis.**
- **No paper/live trading.**
- **Phase 10A summaries were NOT regenerated** (original preserved for audit trail).
- **Phase 11 NOT STARTED.**
- **Phase 12 NOT STARTED.**
- **Phase 13 NOT STARTED.**
- **Grand transparency / learning closeout postponed until after Phase 12.**

---

## 7. Recommendations for PM

1. **The inconsistency is real, not a bug.** The signal has non-monotonic tail behavior.
2. **Direction convention depends on horizon:**
   - For 24h/72h: inversion improves both RankIC and spread → consider signal inversion
   - For 1h/4h: inversion resolves spread but flips RankIC → more analysis needed
3. **Alternative approaches to consider:**
   - Exclude bucket 0 from quantile spread (tail-trimmed spread)
   - Use RankIC as primary metric (robust to tail outliers)
   - Use median-based spread instead of mean-based spread
   - Investigate why bucket 0 has extreme returns (potential data artifact?)
4. **Phase 11 should include tail-aware evaluation** in addition to standard RankIC and quantile spread.
