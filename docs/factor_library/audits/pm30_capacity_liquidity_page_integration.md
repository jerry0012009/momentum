# PM-30: Capacity / Liquidity Proxy Diagnostics Page Integration

## Summary
Added a new "Capacity / Liquidity Proxy Diagnostics / 容量 / 流动性代理诊断" section to each factor's detail panel in `factor-evaluation.html`, plus a summary section at the top of the page.

## Payloads Consumed
1. `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_capacity_liquidity_payload.json` (72,309 bytes)
2. `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_capacity_liquidity_summary.csv` (51,227 bytes, 71 factors)

## Changes Made

### `_build_factor_eval_html.py`
- **Payload loading**: Added `cap_liq_payload` and `cap_liq_summary` loading from `DIAG_DIR`
- **Lookup map**: Built `cap_liq_csv_map` from CSV (CSV has more detailed fields than JSON)
- **Factor data merge**: For each factor, merged 24 capacity/liquidity fields from the CSV into the factor dict (prefixed `cap_liq_`)
- **Summary stats**: Computed `cap_liq_class_counts` for the summary section after factors are built
- **CSS**: Added `.cap-badge` and `.cap-caveat` styles with color-coding for all capacity/liquidity class values
- **JS label maps**: Added `CAP_RISK_LABELS`, `LIQ_RISK_LABELS`, `CAP_LIQ_CLASS_LABELS`, `VOL_CONC_LABELS`, `CROSS_FLAG_LABELS` with bilingual labels
- **JS badge function**: Added `capBadge(cls, map)` for rendering class badges
- **Detail panel section**: Added after shape/stability/decile section, includes:
  - Summary badges (5 classification badges)
  - Proxy method display
  - Metric grid (10 metrics: turnover stats, basket volume, symbol counts, concentration)
  - Capacity estimates (1%/5%/10% participation, USD)
  - Participation rates by notional ($100K/$1M/$10M, median and p10)
  - Bilingual caveat warning
  - Interpretation notes (bilingual)
- **Summary section**: Added `capLiqSummarySection` div and JS rendering with count cards for each capacity/liquidity class
- **Filter div**: Added `capLiqSummarySection` to page layout

### Existing Sections Preserved
- ✅ Single-Factor Paper Portfolio (PM-22)
- ✅ BTC / Market Regime Diagnostics (PM-24)
- ✅ Quantile Shape & Rolling Stability (PM-28)
- ✅ Factor Quality Scorecard
- ✅ Redundancy & Novelty (PM-19)
- ✅ Monthly RankIC / LS / Cumulative charts
- ✅ Drawdown Summary
- ✅ All existing filters

## Validation Results
| Check | Result |
|-------|--------|
| Capacity / Liquidity Proxy Diagnostics | ✅ |
| 容量 / 流动性代理诊断 | ✅ |
| capacity_risk_class | ✅ |
| liquidity_risk_class | ✅ |
| capacity_liquidity_class | ✅ |
| factor_quality_cross_flag | ✅ |
| Selected-basket proxy warning | ✅ |
| not order-book simulation (full caveat) | ✅ |
| Single-Factor Paper Portfolio | ✅ |
| Quantile Shape & Rolling Stability | ✅ |
| BTC / Market Regime Diagnostics | ✅ |
| 不是交易策略 | ✅ |

**Note**: The validation check string "not real execution capacity" doesn't match as a substring because the actual caveat reads "or real execution capacity" (the "not" applies to the entire list). The full caveat text is present: "They are not order-book simulation, slippage estimates, or real execution capacity."

## HTML Size
- **2,704,496 bytes** (~2.70MB) — under 4MB target ✅
- Previous: ~2.61MB; increase: ~90KB for 71 factors' capacity/liquidity data

## Caveat Confirmation
Both bilingual caveats are present:
- EN: "These are capacity/liquidity proxies based on selected-basket volume and turnover. They are not order-book simulation, slippage estimates, or real execution capacity."
- ZH: "这些是基于选中篮子成交量与换手率的容量 / 流动性代理指标，不是订单簿模拟、滑点估计或真实可交易容量结论。"

## Limitations
- CSV has more participation/capacity detail columns than JSON payload; JSON was used for class labels, CSV for detailed metrics
- `long_basket_volume_median` and `short_basket_volume_median` columns exist in CSV but values may be null for some factors (handled gracefully)
- Capacity estimates assume uniform daily volume distribution — real liquidity is clustered (noted in interpretation)
