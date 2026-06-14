# Phase 6G — Dynamic-Universe Factor Evaluation

> Date: 2026-06-14
>
> Status: COMPLETE — PHASE 6H COMPARISON ALLOWED

---

## 1. Goal

Evaluate all 11 registered factors under dynamic-universe membership filtering,
producing IC / RankIC / quintile spread / turnover metrics.

## 2. Dataset & Universe

| Field | Value |
|-------|-------|
| dataset_id | `crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1` |
| universe_id | `crypto_usdt_perp_monthly_volume_top50_current_listed_v1` |
| evaluation_mode | dynamic_universe_membership |
| universe_mode | dynamic_from_current_listed_pool |

## 3. Rows Before / After Universe Filter

Every factor: 3,316,259 → 890,400 rows (266 symbols, 25 months).

## 4. Factor Evaluation Summary (ret_fwd_1h)

| Factor | RankIC | Direction-Adjusted Spread | Turnover | Coverage |
|--------|--------|--------------------------|----------|----------|
| volatility_20h | -0.0428 | +0.000110 | 0.065 | 99.84% |
| q158_high_low_range | -0.0413 | 0.000000 | 0.396 | 100.00% |
| reversal_5h | +0.0282 | +0.000013 | 0.349 | 99.96% |
| bb_zscore_20h | -0.0244 | -0.000056 | 0.301 | 99.58% |
| rsi_14h | -0.0210 | -0.000044 | 0.215 | 99.89% |
| tech_atr | +0.0200 | 0.000000 | 0.007 | 99.89% |
| mom_20h | -0.0191 | +0.000036 | 0.184 | 99.84% |
| wq101_alpha101 | -0.0176 | -0.000051 | 0.785 | 100.00% |
| wq101_alpha53 | +0.0127 | 0.000000 | 0.787 | 99.93% |
| tech_macd | -0.0065 | +0.000048 | 0.142 | 100.00% |
| wq101_alpha12 | +0.0041 | 0.000000 | 0.632 | 99.99% |

## 5. Best / Worst RankIC

- **Best |RankIC|:** volatility_20h (-0.0428), q158_high_low_range (-0.0413)
- **Weakest |RankIC|:** wq101_alpha12 (+0.0041), tech_macd (-0.0065)

## 6. Best / Worst Direction-Adjusted Spread

- **Best spread:** volatility_20h (+0.000110), tech_macd (+0.000048)
- **Near-zero:** q158_high_low_range (0.000000), tech_atr (0.000000)

## 7. Coverage Summary

All factors >99.5% coverage after universe filter. No global missing-rate exclusion applied.

## 8. Known Limitations

- Universe is `dynamic_from_current_listed_pool`, not true point-in-time.
- No global missing_bar_rate exclusion (correct for dynamic universe).
- Membership-aware filtering: only selected symbol-months evaluated.
- Static vs dynamic comparison deferred to Phase 6H (static summary not found).

## 9. Tests

6/6 pass in `test_evaluate_factors_dynamic_universe.py`.

## 10. Whether Phase 6H Is Allowed

**Yes — Phase 6H static-vs-dynamic comparison is allowed.**
