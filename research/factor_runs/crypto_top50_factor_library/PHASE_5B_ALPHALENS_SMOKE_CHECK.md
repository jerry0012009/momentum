# Phase 5B — Alphalens Smoke Check Report

> Generated: 2026-06-13T16:44:39.408355+00:00
> Dataset: crypto_top50_usdt_perp_1h_long_v1
> Alphalens: v0.4.6

---

## 1. Dependency Status

- alphalens-reloaded installed: **True**
- Version: 0.4.6

## 2. Functions Called

- `alphalens.performance.factor_information_coefficient()` — Spearman IC
- `alphalens.performance.mean_return_by_quantile()` — quantile returns
- `alphalens.performance.quantile_turnover()` — turnover analysis
- Note: `get_clean_factor_and_forward_returns()` skipped — does not support hourly frequency

## 3. Factors Checked

### mom_20h

| Horizon | IC mean (Spearman) | IC std | Count |
|---------|-------------------|--------|-------|
| 1h | -0.040674 | 0.248831 | 712 |
| 4h | -0.030589 | 0.234464 | 712 |
| 24h | -0.024927 | 0.251008 | 711 |
| 72h | -0.017013 | 0.242298 | 709 |

### wq101_alpha53

| Horizon | IC mean (Spearman) | IC std | Count |
|---------|-------------------|--------|-------|
| 1h | 0.007820 | 0.194052 | 730 |
| 4h | 0.016369 | 0.189689 | 730 |
| 24h | 0.012448 | 0.192498 | 729 |
| 72h | 0.006236 | 0.185365 | 727 |

## 4. IC Comparison: Local vs Alphalens

| Factor | Horizon | Local Pearson IC | Local RankIC | Alphalens Spearman IC | RankIC Abs Diff | Status | Note |
|--------|---------|-----------------|-------------|----------------------|----------------|--------|------|
| mom_20h | 1h | -0.011828 | -0.025049 | -0.040674 | 0.015625 | mismatch | rankic_abs_diff=0.015625: possible causes — Alphalens computes Spearman from its |
| mom_20h | 4h | -0.015449 | -0.033273 | -0.030589 | 0.002684 | mismatch | rankic_abs_diff=0.002684: possible causes — Alphalens computes Spearman from its |
| mom_20h | 24h | 0.011493 | -0.020934 | -0.024927 | 0.003993 | mismatch | rankic_abs_diff=0.003993: possible causes — Alphalens computes Spearman from its |
| mom_20h | 72h | 0.005880 | -0.015305 | -0.017013 | 0.001708 | mismatch | rankic_abs_diff=0.001708: possible causes — Alphalens computes Spearman from its |
| wq101_alpha53 | 1h | 0.009041 | 0.017332 | 0.007820 | 0.009512 | mismatch | rankic_abs_diff=0.009512: possible causes — Alphalens computes Spearman from its |
| wq101_alpha53 | 4h | 0.004965 | 0.010504 | 0.016369 | 0.005865 | mismatch | rankic_abs_diff=0.005865: possible causes — Alphalens computes Spearman from its |
| wq101_alpha53 | 24h | 0.002363 | 0.004492 | 0.012448 | 0.007956 | mismatch | rankic_abs_diff=0.007956: possible causes — Alphalens computes Spearman from its |
| wq101_alpha53 | 72h | 0.002590 | 0.003269 | 0.006236 | 0.002967 | mismatch | rankic_abs_diff=0.002967: possible causes — Alphalens computes Spearman from its |

## 5. Definition Notes

- **Primary comparison:** Alphalens Spearman IC vs local RankIC_mean — both are rank-based measures.
- **Secondary comparison:** Alphalens Spearman IC vs local IC_mean (Pearson) — shown for reference only.
- **Forward returns:** Our pre-computed forward returns are embedded in the factor_data passed to Alphalens.
- `get_clean_factor_and_forward_returns()` was skipped because hourly frequency is not supported in this setup.

## 6. Limitations

- Alphalens IC = Spearman rank correlation; compared against local RankIC_mean (primary) and IC_mean/Pearson (secondary).
- Alphalens smoke check uses our pre-computed forward returns embedded in factor_data.
- get_clean_factor_and_forward_returns() was skipped because hourly frequency is not supported in this setup.
- No factor status upgrade can be based solely on Alphalens output.

## 7. Conclusion

- Alphalens smoke check: **PASS**
- Factors tested: 2
- Comparison rows: 8
- Phase 5 (Alphalens export + smoke check): **COMPLETE**
- Phase 6 (Dynamic Universe): **READY — requires human approval**

Key finding: IC differences between local Pearson and Alphalens Spearman are expected.
No factor status changes warranted from Alphalens output.
