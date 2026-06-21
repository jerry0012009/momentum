# PM-11B Funding Rate Integration

**Date:** 2026-06-21
**Follows:** PM-11A (taker field integration)

---

## Summary Verdict

**`FUNDING_CANONICAL_BUILD_PASS`**

All 3 funding-rate factors successfully built under canonical feature path. Perfect match with alternate `_crypto_native_v1` factor_values (correlation=1.0, max_diff=0).

## A. Funding File Selected

**`funding_rate_1h_aligned_dynamic.parquet`** — selected because:
- 3,316,259 rows (matches canonical bars exactly)
- 266 symbols (matches canonical bars exactly)
- 0 row-key diff in either direction
- 12% null rate (acceptable — newer symbols lack historical funding)

Rejected `funding_rate_1h_aligned_static.parquet`:
- Only 215,061 rows (50 symbols)
- 3,131,782 keys missing from bars
- 25.7% null rate

## B. Pre-Check Results

| Check | Result |
|-------|--------|
| Canonical bars rows | 3,316,259 |
| Dynamic funding rows | 3,316,259 |
| Row key match | 100% (0 diff) |
| Duplicates | 0 in both |
| Funding null rate | 12.0% |
| Funding columns | funding_rate, funding_known_at, funding_interval_hours, funding_age_hours |

## C. Code Changes

**`scripts/build_factor_values.py`:**
- Added `FUNDING_RATE_PATH` and `FUNDING_REQUIRED_COLUMNS` constants
- Added `_needs_funding_source()` helper
- Extended main() with 3-way split: ordinary / taker / funding
- Funding factors: canonical bars merged with funding data on (timestamp, symbol)
- Each group prints its source for auditability

## D. Intake Results

| Property | Value |
|----------|-------|
| Run ID | pm11b_funding_rate_integration_20260621 |
| Factors | 3 |
| Runtime | 337s |
| Status | COMPLETE |
| Quality checks | PASS |

## E. Factor Values Generated

| Factor | Rows | Symbols | Coverage |
|--------|------|---------|----------|
| funding_rate_level_20h | 3,316,259 | 266 | 87.8% |
| funding_rate_zscore_80h | 3,316,259 | 266 | 75.5% |
| funding_rate_change_24h | 3,316,259 | 266 | 87.8% |

## F. Validation vs `_crypto_native_v1` Alternate

| Factor | Correlation | Max Abs Diff |
|--------|-------------|--------------|
| funding_rate_level_20h | 1.000000 | 0.00e+00 |
| funding_rate_zscore_80h | 1.000000 | 0.00e+00 |
| funding_rate_change_24h | 1.000000 | 0.00e+00 |

Perfect match — same funding source, same formula, same result.

## G. Conclusion Cards

- REVIEW_REQUIRED: 3 (all funding factors)

## H. Before/After Factor Library Counts

| Metric | Before PM-11B | After PM-11B |
|--------|---------------|--------------|
| Registered | 71 | 71 |
| Computed | 68 | 71 |
| Missing FV | 3 | 0 |
| Missing Input | 3 | 0 |
| Signal factors | 10 | 10 |
| Signal variants | 3 | 3 |
| Warnings | 1 | 0 |

## I. Remaining Missing Factors

**None.** All 71 registered factors have computed factor_values.

## J. Non-Change Statement

- No taker changes beyond preservation
- No signal panel changes
- No public page rebuilds
- No production/live/tradeability/alpha claims
- No new factors added
- No data downloaded
