# PM-11A Taker Field Integration

**Date:** 2026-06-21
**Follows:** PM-10 (data completeness audit)

---

## Summary Verdict

**`TAKER_CANONICAL_BUILD_PASS`**

All 3 taker-buy factors successfully built under canonical feature path. Perfect match with alternate `_crypto_native_v1` factor_values (correlation=1.0, max_diff=0).

## A. Pre-Check Results

| Check | Result |
|-------|--------|
| Canonical bars rows | 3,316,259 |
| Taker-enriched bars rows | 3,316,259 |
| Row key match | 100% (0 diff in either direction) |
| Duplicates | 0 in both |
| Taker columns in enriched bars | taker_buy_volume, taker_buy_quote_volume ✅ |

## B. Code Changes

**`scripts/build_factor_values.py`:**
- Added `TAKER_BARS_PATH` and `TAKER_REQUIRED_COLUMNS` constants
- Added `_needs_taker_source()` helper
- Modified `main()` to split factors into taker/non-taker groups
- Non-taker factors: built from canonical bars (unchanged behavior)
- Taker factors: built from taker-enriched bars (new path)
- Each group prints its source for auditability

**`scripts/build_factor_library_state.py`:**
- Fixed `missing_input_ids` to exclude factors with existing factor_values
- Prevents taker factors from being double-counted as "missing" after successful build

## C. Intake Results

| Property | Value |
|----------|-------|
| Run ID | pm11a_taker_field_integration_20260621 |
| Factors | 3 |
| Runtime | 359s |
| Status | COMPLETE |
| Quality checks | PASS |

## D. Factor Values Generated

| Factor | Rows | Symbols | Coverage |
|--------|------|---------|----------|
| taker_buy_ratio_20h | 3,316,259 | 266 | ✅ |
| taker_buy_zscore_20h | 3,316,259 | 266 | ✅ |
| taker_buy_delta_5h | 3,316,259 | 266 | ✅ |

## E. Validation vs `_crypto_native_v1` Alternate

| Factor | Correlation | Max Abs Diff |
|--------|-------------|--------------|
| taker_buy_ratio_20h | 1.000000 | 0.00e+00 |
| taker_buy_zscore_20h | 1.000000 | 0.00e+00 |
| taker_buy_delta_5h | 1.000000 | 0.00e+00 |

Perfect match — same taker-enriched source, same formula, same result.

## F. Conclusion Cards

- REVIEW_REQUIRED: 3 (all taker factors)

## G. Before/After Factor Library Counts

| Metric | Before PM-11A | After PM-11A |
|--------|---------------|--------------|
| Registered | 71 | 71 |
| Computed | 65 | 68 |
| Missing FV | 6 | 3 |
| Missing Input | 6 | 3 |
| Signal factors | 10 | 10 |
| Signal variants | 3 | 3 |

## H. Remaining Missing Factors (funding-only)

1. funding_rate_level_20h
2. funding_rate_zscore_80h
3. funding_rate_change_24h

## I. Non-Change Statement

- No funding integration
- No signal panel changes
- No public page rebuilds
- No production/live/tradeability/alpha claims
- No new factors added
- No data downloaded
