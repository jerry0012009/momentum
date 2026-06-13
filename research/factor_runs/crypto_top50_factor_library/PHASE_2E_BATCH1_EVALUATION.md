# Phase 2E Batch 1 Evaluation Closeout

> Date: 2026-06-13
>
> Commit: `3997223` (pre-evaluation implementation)
>
> Status: COMPLETE

---

## 1. Test Results

| Command | Result |
|---------|--------|
| `pytest tests/unit/test_crypto_labels.py -v` | 10/10 passed |
| `pytest tests/unit/test_crypto_factor_values.py -v` | 8/8 passed |
| `pytest tests/unit/test_crypto_factor_eval_smoke.py -v` | 16/16 passed |
| `pytest tests/unit/test_crypto_factor_batch1.py -v` | 30/30 passed |
| **Total** | **63/63 passed** |

## 2. Factor Values Generation

```
python scripts/build_factor_values.py
```

| Factor | Rows | Coverage |
|--------|------|----------|
| mom_20h | 215,061 | 99.54% |
| reversal_5h | 215,061 | 99.88% |
| volatility_20h | 215,061 | 99.54% |
| rsi_14h | 215,061 | 99.68% |
| bb_zscore_20h | 215,061 | 99.56% |
| wq101_alpha101 | 215,061 | 100.00% |
| wq101_alpha12 | 215,061 | 99.98% |
| wq101_alpha53 | 215,061 | 99.79% |
| q158_high_low_range | 215,061 | 100.00% |
| tech_macd | 215,061 | 100.00% |
| tech_atr | 215,061 | 99.70% |

## 3. Evaluation

```
python scripts/evaluate_factors.py
```

- Universe: `crypto_top50_usdt_perp_1h`
- Period: `2025-12-15 09:00 ~ 2026-06-13 08:00 UTC`
- Evaluated factors: 11 (5 V0 + 6 batch1)
- Excluded symbols: `SPACEUSDT` (21.7% missing bars)
- Label horizons: `ret_fwd_1h`, `ret_fwd_4h`, `ret_fwd_24h`, `ret_fwd_72h`

## 4. Batch 1 Factor Metrics

### wq101_alpha101 (expected_direction = positive)

| Label | IC | RankIC | RankICIR | raw_spread | raw_t | dir_adj_spread | dir_t | turnover |
|-------|-----|--------|----------|------------|-------|----------------|-------|----------|
| 1h | -0.0053 | -0.0255 | -0.143 | 0.000068 | 0.46 | 0.000068 | 0.46 | 0.781 |
| 4h | -0.0021 | -0.0192 | -0.107 | 0.000657 | 2.16 | 0.000657 | 2.16 | 0.781 |
| 24h | -0.0014 | -0.0064 | -0.036 | 0.001098 | 1.40 | 0.001098 | 1.40 | 0.781 |
| 72h | 0.0035 | -0.0002 | -0.001 | 0.003419 | 2.39 | 0.003419 | 2.39 | 0.781 |

**Assessment:** Weak. IC near zero across horizons. RankIC slightly negative at short horizons. Very high turnover (78%). raw_spread barely significant at 4h/72h but IC direction inconsistent.

### wq101_alpha12 (expected_direction = conditional)

| Label | IC | RankIC | RankICIR | raw_spread | raw_t |
|-------|-----|--------|----------|------------|-------|
| 1h | 0.0003 | 0.0030 | 0.019 | -0.000164 | -1.25 |
| 4h | 0.0005 | 0.0029 | 0.019 | -0.000200 | -0.75 |
| 24h | -0.0004 | 0.0002 | 0.001 | -0.001628 | -2.52 |
| 72h | 0.0004 | 0.0008 | 0.005 | -0.001530 | -1.26 |

**direction_adjusted_spread: null** (conditional, not used as primary evidence)

**Assessment:** Flat. IC and RankIC essentially zero. No predictive signal detected.

### wq101_alpha53 (expected_direction = conditional)

| Label | IC | RankIC | RankICIR | raw_spread | raw_t |
|-------|-----|--------|----------|------------|-------|
| 1h | 0.0029 | 0.0156 | 0.092 | -0.000131 | -0.96 |
| 4h | -0.0001 | 0.0116 | 0.068 | -0.000417 | -1.43 |
| 24h | 0.0007 | 0.0056 | 0.032 | -0.000781 | -1.03 |
| 72h | 0.0009 | 0.0040 | 0.024 | -0.000178 | -0.13 |

**direction_adjusted_spread: null** (conditional)

**Assessment:** Slight positive RankIC at 1h (0.016) but very weak. Not actionable.

### q158_high_low_range (expected_direction = conditional)

| Label | IC | RankIC | RankICIR | raw_spread | raw_t |
|-------|-----|--------|----------|------------|-------|
| 1h | 0.0065 | -0.0161 | -0.079 | 0.000706 | 4.21 |
| 4h | 0.0112 | -0.0234 | -0.117 | 0.002644 | 7.74 |
| 24h | 0.0276 | -0.0172 | -0.085 | 0.016462 | 18.06 |
| 72h | 0.0564 | -0.0086 | -0.044 | 0.042898 | 25.40 |

**direction_adjusted_spread: null** (conditional)

**Assessment:** Interesting pattern. IC is positive and grows with horizon (volatility is higher over longer periods — expected). RankIC is slightly negative. raw_spread is highly significant but this is a volatility proxy, not a directional signal. The large raw_spread at 72h (4.3%) reflects that high-range days have wider return distributions, not a tradeable edge.

### tech_macd (expected_direction = positive)

| Label | IC | RankIC | RankICIR | raw_spread | raw_t | dir_adj_spread | dir_t |
|-------|-----|--------|----------|------------|-------|----------------|-------|
| 1h | -0.0000 | -0.0064 | -0.038 | 0.000228 | 1.68 | 0.000228 | 1.68 |
| 4h | -0.0006 | -0.0091 | -0.053 | 0.000893 | 3.38 | 0.000893 | 3.38 |
| 24h | 0.0032 | 0.0079 | 0.045 | 0.003339 | 4.61 | 0.003339 | 4.61 |
| 72h | 0.0001 | -0.0024 | -0.015 | 0.005085 | 3.93 | 0.005085 | 3.93 |

**Assessment:** Very weak. IC near zero. RankIC near zero. raw_spread is significant but MACD is trend-following — the spread comes from trend persistence, not alpha. Low turnover (14%) is notable.

### tech_atr (expected_direction = conditional)

| Label | IC | RankIC | RankICIR | raw_spread | raw_t |
|-------|-----|--------|----------|------------|-------|
| 1h | -0.0010 | 0.0092 | 0.058 | -0.000077 | -0.99 |
| 4h | -0.0023 | 0.0120 | 0.074 | -0.000447 | -3.03 |
| 24h | -0.0060 | 0.0043 | 0.026 | -0.004699 | -12.52 |
| 72h | -0.0113 | -0.0080 | -0.055 | -0.016141 | -22.45 |

**direction_adjusted_spread: null** (conditional)

**Assessment:** Very low turnover (1.2%). IC negative at longer horizons. raw_spread negative and highly significant — ATR behaves like a volatility short at 72h. Not a directional signal.

## 5. Warnings

| Warning | Factors Affected |
|---------|-----------------|
| Very high turnover (>70%) | wq101_alpha101, wq101_alpha53 |
| IC near zero across all horizons | wq101_alpha12, tech_macd |
| IC direction inconsistent with expected_direction | wq101_alpha101 (IC negative at short horizons, expected positive) |
| RankIC opposite sign to IC | q158_high_low_range |
| Conditional factors: direction_adjusted_spread not used | wq101_alpha12, wq101_alpha53, q158_high_low_range, tech_atr |

## 6. Status Decision

All 6 batch1 factors are promoted to:

```
status = DIAGNOSTIC_PROBE
```

**Rationale:** No factor shows compelling predictive signal. IC and RankIC are near zero for all factors. raw_spread significance for q158_high_low_range and tech_atr reflects volatility structure, not alpha. None meet any threshold for CANDIDATE_REVIEW.

**No factor is promoted to CANDIDATE_REVIEW, CANDIDATE_FACTOR, or ALPHA.**

## 7. Updated Registry

Factor catalog `factor_catalog_v0_1.csv` updated:
- 6 new rows with `implementation_status=IMPLEMENTED`, `evaluation_status=DIAGNOSTIC_PROBE`
- `FACTOR_REGISTRY.md` updated with 6 new DIAGNOSTIC_PROBE entries

## 8. What's Next

- **Phase 2E Batch 2:** NOT ALLOWED YET (requires human approval)
- **Phase 2F (Gate Refinement):** NOT ALLOWED YET
- **No strategy backtest, no portfolio construction, no alpha claim**
