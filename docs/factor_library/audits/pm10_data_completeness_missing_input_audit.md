# PM-10 Data Completeness and Missing Input Audit

**Date:** 2026-06-21
**Type:** Read-only audit. No code changes, no data downloads, no factor computation.

---

## Summary Verdict

**`TAKER_FIELDS_PRESENT_NEEDS_MAPPING`**

Both taker-buy and funding-rate data exist in the repo under alternate paths. The 6 "missing input" factors have already been computed under a different dataset variant. The issue is a path/schema mapping gap, not missing data.

## 1. Canonical Bars Schema

**Path:** `data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet`

| Property | Value |
|----------|-------|
| File size | 133.0 MB |
| Rows | 3,316,259 |
| Symbols | 266 |
| Timestamp range | 2024-06-01 to 2026-06-13 |
| Null rate | 0% across all columns |

**Columns (15):**
- timestamp, bar_open_time, bar_close_time, symbol
- open, high, low, close, volume, quote_volume, trade_count
- source, market, instrument_type, timeframe

**Missing from canonical bars:** `taker_buy_volume`, `taker_buy_quote_volume`, `funding_rate`

## 2. Taker-Buy Data — PRESENT

**Path:** `data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1_taker_enriched/bars_1h.parquet`

| Property | Value |
|----------|-------|
| File size | 176.6 MB |
| Extra columns | `taker_buy_volume` (double), `taker_buy_quote_volume` (double) |

This is the same dataset as canonical bars but with 2 extra taker columns. The file already exists and is ready to use.

## 3. Funding-Rate Data — PRESENT

**Path:** `data/cache/crypto_funding_rate_1h_contract_v1/`

| File | Size | Key columns |
|------|------|-------------|
| funding_rate_1h_aligned_dynamic.parquet | — | timestamp, symbol, funding_rate, funding_known_at, funding_interval_hours, funding_age_hours |
| funding_rate_1h_aligned_static.parquet | — | timestamp, symbol, funding_rate, funding_known_at, funding_interval_hours |
| funding_rate_events.parquet | 12.9 MB | symbol, calc_time, known_at, funding_rate, funding_interval_hours, source_file |

Raw funding rate zips also exist under:
- `data/binance_funding_rate/` (per-symbol monthly zips)
- `data/binance_vision_rank154/data/futures/um/monthly/fundingRate/`

## 4. Factor Values — ALL 6 ALREADY COMPUTED

Under `data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1_crypto_native_v1/`:

| Factor | Rows | Symbols | Status |
|--------|------|---------|--------|
| taker_buy_ratio_20h | 3,316,259 | 266 | ✅ COMPUTED |
| taker_buy_zscore_20h | 3,316,259 | 266 | ✅ COMPUTED |
| taker_buy_delta_5h | 3,316,259 | 266 | ✅ COMPUTED |
| funding_rate_level_20h | 3,316,259 | 266 | ✅ COMPUTED |
| funding_rate_zscore_80h | 3,316,259 | 266 | ✅ COMPUTED |
| funding_rate_change_24h | 3,316,259 | 266 | ✅ COMPUTED |

These factor_values were computed under the `_crypto_native_v1` dataset variant, not the current canonical `_v1` variant. The registry marks them as "missing input" because `build_factor_values.py` looks for the canonical bars path, which lacks taker/funding columns.

## 5. Missing-Input Factor Table

| factor_id | required_columns | current_column_status | can_compute_now? | recommended_next_step |
|-----------|-----------------|----------------------|-----------------|----------------------|
| taker_buy_ratio_20h | taker_buy_quote_volume, quote_volume | PRESENT_ELSEWHERE_IN_REPO | YES_AFTER_COLUMN_MAPPING | PM-11A: map taker_enriched bars to canonical path |
| taker_buy_zscore_20h | taker_buy_quote_volume, quote_volume | PRESENT_ELSEWHERE_IN_REPO | YES_AFTER_COLUMN_MAPPING | PM-11A |
| taker_buy_delta_5h | taker_buy_quote_volume, quote_volume | PRESENT_ELSEWHERE_IN_REPO | YES_AFTER_COLUMN_MAPPING | PM-11A |
| funding_rate_level_20h | funding_rate | PRESENT_ELSEWHERE_IN_REPO | YES_AFTER_COLUMN_MAPPING | PM-11B: map aligned funding parquet |
| funding_rate_zscore_80h | funding_rate | PRESENT_ELSEWHERE_IN_REPO | YES_AFTER_COLUMN_MAPPING | PM-11B |
| funding_rate_change_24h | funding_rate | PRESENT_ELSEWHERE_IN_REPO | YES_AFTER_COLUMN_MAPPING | PM-11B |

## 6. Recommended PM-11 Sequence

### PM-11A: Taker Field Integration (simpler, do first)

1. Decide canonical bars enrichment strategy:
   - Option A: Point `build_factor_values.py` at the taker_enriched bars path for taker factors only
   - Option B: Merge taker columns into canonical bars parquet (increases file from 133MB to ~177MB)
   - Option C: Keep separate, add a `--taker-bars-path` parameter to build_factor_values.py
2. Verify taker_enriched bars timestamp/symbol alignment with canonical bars
3. Run factor intake for 3 taker factors only
4. No new downloads needed

### PM-11B: Funding Rate Integration (after PM-11A)

1. Decide funding rate alignment strategy:
   - Use `funding_rate_1h_aligned_static.parquet` (simpler) or `funding_rate_1h_aligned_dynamic.parquet` (has funding_age_hours)
2. Align funding_rate to canonical bars by (timestamp, symbol) join
3. Run factor intake for 3 funding factors only
4. No new downloads needed

**Recommendation:** Handle taker and funding separately (PM-11A then PM-11B) to keep changes small and auditable.

## 7. Non-Change Statement

- No data downloaded
- No APIs called
- No factor code modified
- No bars/labels/factor_values parquet modified
- No factor intake run
- No signal panel rebuilt
- No production/live/alpha claims
