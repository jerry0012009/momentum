# PM-29B: Selected-Basket Capacity/Liquidity Repair

**Date:** 2026-06-22
**Follows:** PM-29 (universe proxy)

---

## Summary Verdict

**`SELECTED_BASKET_CAPACITY_REPAIR_PASS`**

## 1. Why PM-29B

PM-29 used universe-level volume proxy, making all 71 factors appear CAPACITY_LIQUIDITY_OK. PM-29B upgrades to selected-basket proxy for realistic capacity assessment.

## 2. Implementation Method

**Selected-basket proxy** using hourly bar data:
- Load factor values parquet for each factor
- Join with hourly quote volume from bars_1h.parquet
- Rank cross-section by factor value at each rebalance
- Select top/bottom decile (matching paper portfolio convention)
- Compute selected-basket liquidity metrics

**Sampling:** Every 4th hour (4h deterministic sampling) for performance. ~6 months of hourly data per factor.

## 3. Factor Coverage

- Expected: 71
- Summary: 71
- Monthly: 71 (1,769 rows)
- Payload: 71
- Missing: 0
- Proxy method: selected_basket_proxy (71/71)

## 4. Capacity Risk Distribution (PM-29 → PM-29B)

| Class | PM-29 | PM-29B |
|---|---:|---:|
| CAPACITY_FRIENDLY | 59 | 34 |
| MODERATE_CAPACITY_RISK | 12 | 35 |
| CAPACITY_FRAGILE | 0 | 2 |

## 5. Liquidity Risk Distribution

| Class | PM-29 | PM-29B |
|---|---:|---:|
| LIQUIDITY_FRIENDLY | 71 | 0 |
| LIQUIDITY_FRAGILE | 0 | 71 |

All factors are LIQUIDITY_FRAGILE when measured by selected-basket volume (much lower than universe aggregate).

## 6. Volume Concentration Distribution

| Class | Count |
|---|---:|
| DIVERSIFIED_LIQUIDITY | 71 |

## 7. Combined Class Distribution

| Class | Count |
|---|---:|
| WATCH_LIQUIDITY | 69 |
| WATCH_BOTH | 2 |

## 8. Capacity-Fragile Examples

- taker_buy_zscore_20h: selected_vol_median=$1.09M, WATCH_BOTH, turnover=0.78
- taker_buy_delta_5h: selected_vol_median=$0.74M, WATCH_BOTH

## 9. Cross Flags

| Flag | Count |
|---|---:|
| STABLE_BUT_TOO_ILLIQUID | 61 |
| NONE | 10 |

## 10. Limitations

1. **Proxy still** — not real execution simulation
2. **4h sampling** — not full hourly reconstruction
3. **All factors LIQUIDITY_FRAGILE** — selected basket volume is always much lower than universe aggregate; this is expected but means liquidity_risk_class may be too uniformly pessimistic
4. **No order book modeling** — participation rate is volume-weighted proxy

## 11. Non-Change Statement

No factors, formulas, factor_values, signal panel, public page modified.

## 12. Recommended Next PM

**PM-30:** Page integration for capacity/liquidity diagnostics.
