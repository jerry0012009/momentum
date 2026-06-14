# Phase 7M-B — Crypto-native Factor Values Build Closeout

> Date: 2026-06-14
>
> Status: COMPLETE

---

## A. Scope

- Phase 7M-B: build crypto-native factor_values only
- 6 factors only (taker 3 + funding 3)
- No evaluation, no classification, no redundancy, no backtest

---

## B. Dataset Join Summary

| variant | combined rows | taker coverage | funding coverage | schema_status |
|---------|--------------|----------------|------------------|---------------|
| static | 215,061 | 75.8% | 74.3% | PASS |
| dynamic | 3,316,259 | 91.7% | 88.0% | PASS |

Row count match: both variants ✅

---

## C. Factor Values Build Summary

### Static (215,061 rows)

| factor_id | coverage | gate |
|-----------|----------|------|
| taker_buy_ratio_20h | 75.379% | PASS |
| taker_buy_zscore_20h | 75.379% | PASS |
| taker_buy_delta_5h | 75.705% | PASS |
| funding_rate_level_20h | 73.833% | PASS |
| funding_rate_zscore_80h | 66.410% | PASS |
| funding_rate_change_24h | 73.742% | PASS |

### Dynamic (3,316,259 rows)

| factor_id | coverage | gate |
|-----------|----------|------|
| taker_buy_ratio_20h | 91.231% | PASS |
| taker_buy_zscore_20h | 91.231% | PASS |
| taker_buy_delta_5h | 91.410% | PASS |
| funding_rate_level_20h | 87.844% | PASS |
| funding_rate_zscore_80h | 75.482% | PASS |
| funding_rate_change_24h | 87.835% | PASS |

All 12 factor_values: gate = PASS

---

## D. Important Observations

- Taker coverage ~75% static / ~91% dynamic: early months (2021-Q4 to 2022-Q1) missing taker fields in raw klines.
- Funding coverage ~74% static / ~88% dynamic: some symbols lack funding rate history.
- funding_rate_zscore_80h has lowest coverage (66%/75%) due to 80-bar warmup window.
- NaN concentrated in early months, not structural gaps.
- No NaN caused by forward-fill or cross-symbol leakage.

---

## E. Phase 7M-C Readiness

**Phase 7M-C crypto-native static/dynamic evaluation is allowed pending PM review.**

---

## F. Negative Declarations

No static evaluation was run.
No dynamic evaluation was run.
No static-vs-dynamic comparison was run.
No diagnostic classification was run.
No redundancy analysis was run.
No strategy backtest was run.
No portfolio simulation was run.
No Qlib / VectorBT / Backtrader integration was run.
No Alphalens tear sheet was run.
No factor status was upgraded to CANDIDATE_REVIEW.
No alpha claim was made.
No factor was removed or selected for trading.
