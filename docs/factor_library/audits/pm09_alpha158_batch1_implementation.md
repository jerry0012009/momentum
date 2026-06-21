# PM-09 Alpha158-Inspired Factor Batch 1 Implementation

**Date:** 2026-06-21
**Follows:** PM-08 (candidate source map)

---

## A. Factors Added

| # | factor_id | family | formula_proxy | required_columns | direction | lookback |
|---|-----------|--------|---------------|-----------------|-----------|----------|
| 1 | vwap_dev_20h | alpha158_ohlcv | (close - vwap_20h) / vwap_20h | close, volume | conditional | 20 |
| 2 | wvma_20h | alpha158_ohlcv | std(ret*vol,20) / mean(vol,20) | close, volume | negative | 21 |
| 3 | vol_ret_corr_20h | alpha158_ohlcv | corr(ret, Δvolume, 20) | close, volume | conditional | 21 |
| 4 | intraday_ret | alpha158_ohlcv | (close - open) / open | open, close | conditional | 1 |
| 5 | klow_close | alpha158_ohlcv | (min(open,close) - low) / close | open, low, close | positive | 1 |
| 6 | ksft_5h | alpha158_ohlcv | rolling_skewness(ret, 5) | close | conditional | 6 |

## B. Files Changed

- `scripts/factor_ops.py` — added `rolling_skew()` helper
- `scripts/factor_formula_registry.py` — 6 compute functions + 6 FactorSpec entries + rolling_skew import

## C. Validation

- `py_compile` ALL OK (8 scripts)
- Registry integrity: 71 factors, 0 critical issues
- Intake run: COMPLETE (705s)

## D. Intake Results

- Quality checks: 8/8 PASS
- factor_values: ✅ generated for all 6 factors
- Factor library state: 71 registered → 65 computed (before: 65/59)

### Evaluation Summary

| Factor | Best Horizon | Best Adj IC | Best ICIR | Monthly Stability | Redundancy | Decision |
|--------|-------------|------------|----------|-------------------|------------|----------|
| vwap_dev_20h | 4h | -0.0273 | -0.167 | UNSTABLE (0/25) | HIGH | REDUNDANT_WITH_EXISTING |
| wvma_20h | 72h | +0.0763 | +0.444 | STABLE (24/25) | HIGH | REVIEW_REQUIRED |
| vol_ret_corr_20h | 24h | -0.0377 | -0.326 | UNSTABLE (2/25) | HIGH | REDUNDANT_WITH_EXISTING |
| intraday_ret | 1h | -0.0366 | -0.230 | UNSTABLE (0/25) | HIGH | REDUNDANT_WITH_EXISTING |
| klow_close | 72h | -0.0548 | -0.372 | UNSTABLE (2/25) | MODERATE | REVIEW_REQUIRED |
| ksft_5h | 24h | -0.0074 | -0.071 | UNSTABLE (6/25) | LOW | CONDITIONAL_DIRECTION_REVIEW |

### Conclusion Card Buckets

- REDUNDANT_WITH_EXISTING: 3 (vwap_dev_20h, vol_ret_corr_20h, intraday_ret)
- REVIEW_REQUIRED: 2 (wvma_20h, klow_close)
- CONDITIONAL_DIRECTION_REVIEW: 1 (ksft_5h)
- PROMOTE: 0

### Key Redundancy Findings

- intraday_ret ↔ candle_body: |ρ| = 0.949 (HIGH)
- vol_ret_corr_20h ↔ price_volume_corr_20h: |ρ| = 0.940 (HIGH)
- vwap_dev_20h ↔ breakout_dist_20h: |ρ| = 0.918 (HIGH)
- vwap_dev_20h ↔ bb_zscore_20h: |ρ| = 0.917 (HIGH)
- wvma_20h ↔ volatility_20h: |ρ| = 0.892 (HIGH)

### Redundancy Summary

- HIGH_REDUNDANCY: 9 pairs
- MODERATE_REDUNDANCY: 6 pairs
- LOW_REDUNDANCY: 226 pairs
- INSUFFICIENT_DATA: 128 pairs

## E. Factor Library State (Before → After)

| Metric | Before | After |
|--------|--------|-------|
| Registered | 65 | 71 |
| Computed | 59 | 65 |
| Missing FV | 6 | 6 |
| Signal factors | 10 | 10 |

## F. Non-Change Statement

- No signal panel modification
- No signal weights changed
- No public result pages rebuilt
- No production/live/alpha/tradeability claims
- No promotion executed

## G. Observations

1. **3/6 factors are near-duplicates of existing factors.** intraday_ret ≈ candle_body, vol_ret_corr_20h ≈ price_volume_corr_20h, vwap_dev_20h ≈ bb_zscore_20h/breakout_dist_20h. This validates the PM-08 redundancy concern.

2. **wvma_20h has the strongest signal** (ICIR 0.444, STABLE 24/25 months at 72h) but is HIGH redundant with volatility_20h. Need to assess if the volume-weighting adds incremental value.

3. **ksft_5h has LOW redundancy** but very weak signal (ICIR 0.071). Short-window skewness may need longer horizons or combination with other factors.

4. **klow_close shows moderate signal** at 72h but direction is opposite to expected (negative IC vs expected positive). Needs direction semantics audit.

5. **All factors show divergent RankIC-LS consistency** — IC direction and long-short spread direction disagree. This is a known pattern in the library.
