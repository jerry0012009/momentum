# Phase 7M-A — Limited Crypto-native Factor Implementation Closeout

> Date: 2026-06-14
>
> Status: COMPLETE

---

## A. Scope

- Phase 7M-A: limited crypto-native factor implementation
- 6 diagnostic factors only
- No factor_values build, no evaluation, no backtest

---

## B. Implemented Factors

### Taker Imbalance Family

| factor_id | formula | expected_direction | lookback |
|-----------|---------|-------------------|----------|
| `taker_buy_ratio_20h` | rolling_mean(taker_buy_quote_volume / quote_volume, 20) | positive | 20 |
| `taker_buy_zscore_20h` | zscore(taker_buy_quote_volume / quote_volume, 20) | positive | 20 |
| `taker_buy_delta_5h` | ratio - delay(ratio, 5) | positive | 6 |

### Funding Rate Family

| factor_id | formula | expected_direction | lookback |
|-----------|---------|-------------------|----------|
| `funding_rate_level_20h` | rolling_mean(funding_rate, 20) | negative | 20 |
| `funding_rate_zscore_80h` | zscore(funding_rate, 80) | negative | 80 |
| `funding_rate_change_24h` | funding_rate - delay(funding_rate, 24) | negative | 25 |

All 6 factors: `status = DIAGNOSTIC_PROBE`

---

## C. Data Dependency

- **Taker factors** require taker enriched bars from Phase 7L-R (`taker_buy_quote_volume`, `quote_volume`)
- **Funding factors** require funding aligned cache from Phase 7L-R (`funding_rate`)
- Current phase only implements compute functions — no factor_values build

---

## D. Tests

```
python -m pytest tests/unit/test_crypto_factor_batch7m.py -v
```

**Result: 19/19 PASS**

| Test Class | Tests | Result |
|-----------|-------|--------|
| TestRegistry | 9 | ✅ (6 in registry, family, direction, status, required_columns, no forbidden words) |
| TestTakerFormulas | 5 | ✅ (ratio, zscore, delta, zero→NaN, no forward-fill) |
| TestFundingFormulas | 5 | ✅ (level, zscore, change, NaN propagation, no future data) |

---

## E. Phase 7M-B Readiness

**Phase 7M-B crypto-native factor_values build is allowed pending PM review.**

---

## F. Negative Declarations

No factor_values were built.
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
