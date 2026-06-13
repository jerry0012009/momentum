# Phase 6C — Dynamic Universe Data Coverage Audit

> Generated: 2026-06-13T18:34:11.555044+00:00
> Universe: `crypto_usdt_perp_monthly_volume_top50_current_listed_v1`
> Dataset: `crypto_top50_usdt_perp_1h_long_v1`

---

## 1. Summary

| Metric | Value |
|--------|-------|
| Dynamic universe months | 25 |
| Dynamic universe unique symbols | 266 |
| Bars dataset symbols | 50 |
| Intersection (covered) | 43 |
| Missing from bars | 223 |
| Extra in bars (never in universe) | 7 |
| **Coverage rate** | **16.2%** |

## 2. Decision

**NOT_ALLOWED**

Dynamic universe evaluation is NOT YET allowed. A new dataset must be built for the union of dynamic universe symbols.

## 3. Recommendation

Option B: build a new 1h dataset for the union of dynamic universe selected symbols. This requires downloading bars_1h for all ~266 symbols, recomputing labels and factor_values.

## 4. Missing Symbols

223 symbols selected by dynamic universe but absent from bars dataset:

| Symbol |
|--------|
| 0GUSDT |
| 1000BONKUSDT |
| 1000FLOKIUSDT |
| 1000LUNCUSDT |
| 1000RATSUSDT |
| 1000SATSUSDT |
| 1000SHIBUSDT |
| 1MBABYDOGEUSDT |
| 2ZUSDT |
| 4USDT |
| AAVEUSDT |
| ACHUSDT |
| ACTUSDT |
| AERGOUSDT |
| AEVOUSDT |
| AGLDUSDT |
| AIGENSYNUSDT |
| AIOTUSDT |
| AIXBTUSDT |
| ALCHUSDT |
| ALGOUSDT |
| ALPINEUSDT |
| ANIMEUSDT |
| APEUSDT |
| API3USDT |
| APTUSDT |
| ARCUSDT |
| ARIAUSDT |
| ARKUSDT |
| ARUSDT |
| ASTERUSDT |
| ATUSDT |
| AUCTIONUSDT |
| AVNTUSDT |
| AXSUSDT |
| AZTECUSDT |
| BABYUSDT |
| BANANAS31USDT |
| BARDUSDT |
| BASEDUSDT |
| BASUSDT |
| BBUSDT |
| BERAUSDT |
| BIGTIMEUSDT |
| BILLUSDT |
| BIOUSDT |
| BIRBUSDT |
| BLESSUSDT |
| BOMEUSDT |
| BREVUSDT |
| ... and 173 more |

## 5. Extra Symbols (in bars but never in universe)

7 symbols in bars dataset but never selected by dynamic universe:

| Symbol |
|--------|
| AIOUSDT |
| CHZUSDT |
| EPICUSDT |
| ESPORTSUSDT |
| IDUSDT |
| STGUSDT |
| VELVETUSDT |

## 6. Monthly Coverage

| Month | Universe Symbols | Intersection | Missing | Coverage |
|-------|-----------------|--------------|---------|----------|
| 2024-06 | 50 | 22 | 28 | 44.0% |
| 2024-07 | 50 | 24 | 26 | 48.0% |
| 2024-08 | 50 | 22 | 28 | 44.0% |
| 2024-09 | 50 | 24 | 26 | 48.0% |
| 2024-10 | 50 | 20 | 30 | 40.0% |
| 2024-11 | 50 | 20 | 30 | 40.0% |
| 2024-12 | 50 | 22 | 28 | 44.0% |
| 2025-01 | 50 | 24 | 26 | 48.0% |
| 2025-02 | 50 | 23 | 27 | 46.0% |
| 2025-03 | 50 | 23 | 27 | 46.0% |
| 2025-04 | 50 | 25 | 25 | 50.0% |
| 2025-05 | 50 | 23 | 27 | 46.0% |
| 2025-06 | 50 | 24 | 26 | 48.0% |
| 2025-07 | 50 | 25 | 25 | 50.0% |
| 2025-08 | 50 | 26 | 24 | 52.0% |
| 2025-09 | 50 | 24 | 26 | 48.0% |
| 2025-10 | 50 | 24 | 26 | 48.0% |
| 2025-11 | 50 | 27 | 23 | 54.0% |
| 2025-12 | 50 | 26 | 24 | 52.0% |
| 2026-01 | 50 | 25 | 25 | 50.0% |
| 2026-02 | 50 | 26 | 24 | 52.0% |
| 2026-03 | 50 | 27 | 23 | 54.0% |
| 2026-04 | 50 | 26 | 24 | 52.0% |
| 2026-05 | 50 | 24 | 26 | 48.0% |
| 2026-06 | 50 | 33 | 17 | 66.0% |

## 7. Factor Coverage

| Factor | Factor Symbols | Intersection | Missing | Coverage |
|--------|---------------|--------------|---------|----------|
| bb_zscore_20h | 50 | 43 | 223 | 16.2% |
| mom_20h | 50 | 43 | 223 | 16.2% |
| q158_high_low_range | 50 | 43 | 223 | 16.2% |
| reversal_5h | 50 | 43 | 223 | 16.2% |
| rsi_14h | 50 | 43 | 223 | 16.2% |
| tech_atr | 50 | 43 | 223 | 16.2% |
| tech_macd | 50 | 43 | 223 | 16.2% |
| volatility_20h | 50 | 43 | 223 | 16.2% |
| wq101_alpha101 | 50 | 43 | 223 | 16.2% |
| wq101_alpha12 | 50 | 43 | 223 | 16.2% |
| wq101_alpha53 | 50 | 43 | 223 | 16.2% |

## 8. Next Steps

### Option A: Evaluate only intersection symbols
- **REJECTED** unless explicitly marked as partial and biased
- Would only evaluate ~43 symbols, missing 84% of dynamic universe

### Option B: Build new dataset for union of dynamic universe symbols
- **RECOMMENDED**
- Download bars_1h for all ~266 symbols across 25 months
- Recompute labels and factor_values
- Then run evaluation on full dynamic universe

### Option C: Abandon dynamic universe, keep static top50
- **REJECTED** for Phase 6 purpose
- Static top50 has known survivorship/look-ahead bias

## 9. Limitations

- This audit checks symbol presence only, not data quality or completeness
- Missing_bar_rate per symbol not computed here (done in Phase 3)
- Factor coverage assumes same symbol set as bars (true for current pipeline)
