# Data Validation Report — V0

Generated: 2026-06-13

## 1. Universe Summary

| Field | Value |
|-------|-------|
| n_symbols | 50 |
| bars_rows | 215,042 |
| timestamp_start | 2025-12-14 13:00:00+00:00 |
| timestamp_end | 2026-06-12 12:00:00+00:00 |
| expected_rows_approx | 216,000 (= 50 symbols × 4,320 hours) |
| actual_vs_expected | 215,042/216,000 = 99.6% |

## 2. Missing Bars by Symbol (Top 10)

| Symbol | Missing Bars | Notes |
|--------|-------------|-------|
| SPACEUSDT | 958 | ~22% missing; likely late listing or data gap |
| All other 49 symbols | 0 | Complete data |

## 3. Duplicate Timestamp+Symbol Count

0 — no duplicates.

## 4. Label Missing Rate by Horizon

| Horizon | Missing Rate | Explanation |
|---------|-------------|-------------|
| ret_fwd_1h | 0.02% | Only tail-end bars |
| ret_fwd_4h | 0.09% | Tail-end bars |
| ret_fwd_24h | 0.56% | Tail-end bars |
| ret_fwd_72h | 1.67% | Tail-end 3 days |

All missing labels are from the tail of the time series (forward returns beyond data end). This is expected and not a data quality issue.

## 5. Factor Coverage

| Factor | Rows | Coverage | Symbols | Timestamp Range |
|--------|------|----------|---------|----------------|
| mom_20h | 215,042 | 99.53% | 50 | 2025-12-14 ~ 2026-06-12 |
| reversal_5h | 215,042 | 99.88% | 50 | 2025-12-14 ~ 2026-06-12 |
| volatility_20h | 215,042 | 99.53% | 50 | 2025-12-14 ~ 2026-06-12 |
| rsi_14h | 215,042 | 99.67% | 50 | 2025-12-14 ~ 2026-06-12 |
| bb_zscore_20h | 215,042 | 99.56% | 50 | 2025-12-14 ~ 2026-06-12 |

Coverage is near-perfect for all 5 registered factors. The small missing fraction comes from lookback window warmup (first 20 bars for 20h factors, first 14 for RSI).

## 6. Manifest Consistency Check

| Check | Result |
|-------|--------|
| n_symbols match | ✅ (50 = 50) |
| bars_rows match | ✅ (215,042 = 215,042) |
| data_start match | ⚠️ Format difference only (manifest uses ISO T, pandas uses space) |
| data_end match | ⚠️ Format difference only (same timestamps, different string format) |

The data_start/data_end mismatches are formatting-only (ISO `T` separator vs space). The actual timestamps are identical.

## 7. Excluded Symbols

Symbols with `missing_bar_rate > 5%` are excluded from factor evaluation (not deleted from raw data):

| Symbol | Missing Rate | Status |
|--------|-------------|--------|
| SPACEUSDT | 22.2% | **EXCLUDED from evaluation** |

All other 49 symbols have 0% missing bars.

## 8. Known Caveats

1. **Survivorship bias**: Universe is static current Top50 by 24h quote volume snapshot taken at universe build time. Tokens that were delisted or newly listed during the 180-day evaluation period are not handled — they either appear with incomplete data or are missing entirely.
2. **Not 30d rolling volume**: `selection_rule` is `static_current_top50_by_24h_quote_volume`, not trailing 30-day. The function `fetch_30d_volume()` in the script was misnamed; it actually reads the 24h ticker. V1 should implement true 30d aggregation.
3. **Overlap inflation**: Forward return labels (4h, 24h, 72h) overlap heavily. t-stats and IC significance in `result_summary.md` are overstated. Use overlap-adjusted inference or monthly aggregation for significance claims.
4. **No slippage/spread costs**: Evaluation uses raw returns only. No transaction cost, slippage, or bid-ask spread adjustment.
5. **Single venue**: Binance USDT-M perps only. Cross-venue liquidity and pricing effects not captured.
6. **SPACEUSDT data gap**: 958 bars missing (~22%). Likely late listing or temporary delisting during the period. Factor values for this symbol during the gap are NaN.
7. **Manifest format drift**: `data_start`/`data_end` string format differs between manifest.json (written by fetch script) and what pandas produces when reading parquet. Not a data integrity issue, but worth normalizing in V1.
8. **Timestamp convention (Phase 2B fix)**: `timestamp = bar_close_time`; `bar_open_time` retained for audit. `factor known_at = bar_close_time`. Previously the fetch script used kline open time as timestamp, which is now corrected.
9. **Label convention (Phase 2B fix)**: Labels use calendar-time forward returns via merge on `(timestamp + h, symbol)`. Previously used row-shift which would produce incorrect returns across gaps.
10. **Direction-adjusted spread (Phase 2B fix)**: Evaluation now outputs `direction_adjusted_spread` (Q5-Q1 for positive, Q1-Q5 for negative) and `direction_adjusted_tstat`. Use these for cross-factor comparison instead of raw spread.
