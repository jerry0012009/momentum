# Phase 6F — Dynamic Universe Factor Values

> Date: 2026-06-13
>
> Status: COMPLETE — PHASE 6G EVALUATION ALLOWED

---

## 1. Goal

Build all registered factor values for the dynamic-universe 1h dataset and audit
membership-aware factor coverage.

## 2. Dataset

| Field | Value |
|-------|-------|
| dataset_id | `crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1` |
| universe_id | `crypto_usdt_perp_monthly_volume_top50_current_listed_v1` |
| Rows | 3,316,259 |
| Symbols | 266 |

## 3. Factors Built

| Factor ID | Rows | Coverage | Selected Missing | Status |
|-----------|------|----------|-----------------|--------|
| bb_zscore_20h | 3,316,259 | 99.58% | 0.107% | PASS |
| mom_20h | 3,316,259 | 99.84% | 0.112% | PASS |
| q158_high_low_range | 3,316,259 | 100.00% | 0.000% | PASS |
| reversal_5h | 3,316,259 | 99.96% | 0.028% | PASS |
| rsi_14h | 3,316,259 | 99.89% | 0.079% | PASS |
| tech_atr | 3,316,259 | 99.89% | 0.079% | PASS |
| tech_macd | 3,316,259 | 100.00% | 0.000% | PASS |
| volatility_20h | 3,316,259 | 99.84% | 0.112% | PASS |
| wq101_alpha101 | 3,316,259 | 100.00% | 0.000% | PASS |
| wq101_alpha12 | 3,316,259 | 99.99% | 0.006% | PASS |
| wq101_alpha53 | 3,316,259 | 99.93% | 0.051% | PASS |

## 4. QA Decision

**Decision: ALLOWED** — All 11 factors have selected_missing_rate ≤ 5%.
Phase 6G evaluation adapter can proceed.

## 5. Schema

All factor_values.parquet files have exact schema:
```
timestamp, symbol, factor_name, factor_value, known_at, source_timeframe, computed_at
```
Where `known_at == timestamp` and `source_timeframe == 1h`.

## 6. Tests

8/8 pass:
- Membership-aware filters selected symbol-months
- Global high but selected acceptable
- High selected missing → FAIL
- Low selected missing → PASS
- Schema exact, known_at==timestamp, source_timeframe=="1h"
- Global coverage keys

## 7. Whether Phase 6G Is Allowed

**Yes — Phase 6G evaluation adapter is allowed.**
