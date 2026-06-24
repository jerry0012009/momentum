# PM-53A: Complete Active 84 Workflow for 4 Non-Cap Alpha101 Panel Factors

**Date**: 2026-06-24T12:30 UTC+8
**Parent**: PM-53 (`90f00bc`)
**Scope**: Fill shape/decile/capacity gap for 4 non-cap a101 panel factors

---

## Verdict

```
PM53A_ACTIVE_84_WORKFLOW_COMPLETION_PASS
```

---

## Files Changed

| File | Change |
|------|--------|
| `factor_quantile_shape_summary.csv` | 80 → 84 (+4 factors) |
| `factor_rolling_stability_summary.csv` | 80 → 84 (+4 factors) |
| `factor_decile_shape_summary.csv` | 80 → 84 (+4 factors) |
| `factor_capacity_liquidity_summary.csv` | 80 → 84 (+4 factors) |
| `single_factor_paper_summary.csv` | +4 factors |
| `single_factor_paper_turnover.csv` | +4 factors |
| `single_factor_paper_monthly_returns.csv` | +4 factors |
| `single_factor_fee_sensitivity.csv` | +4 factors |
| `single_factor_paper_leg_decomposition.csv` | +4 factors |
| `single_factor_paper_drawdown_curve.csv` | +4 factors |
| `single_factor_paper_page_payload.json` | 84 factors |
| `factor_pairwise_redundancy.csv` | +326 pairs |
| `factor_redundancy_summary.csv` | 84 factors |
| `factor_redundancy_matrix_*.csv` | 84×84 |
| `factor_redundancy_clusters.csv` | 84 factors |
| `factor_regime_exposure_summary.csv` | 84 factors |
| `factor_quality_scorecard.csv` | 84 factors |
| `factor_unified_profile_summary.csv` | 84 factors |
| `factor_evaluation_evidence_matrix.csv` | 84 factors |
| `factor_evaluation.html` | 6.34 MB, 84 factors |
| `factor_values/` (4 dirs) | New parquet files for 4 factors |

---

## 4 Non-Cap Alpha101 Factor Status Table

| factor_id | shape | stability | decile | capacity | scorecard | profile | page | integrity |
|-----------|-------|-----------|--------|----------|-----------|---------|------|-----------|
| a101_volume_xs_z_mean_neg_112h | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ 19/19 |
| a101_vol_xs_z_product_112h | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ 19/19 |
| a101_volume_low_alpha_min_84_120 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ 19/19 |
| a101_volume_high_alpha_min_84_84 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ 19/19 |

---

## Before/After Count Table

| Source | Before (PM-53) | After (PM-53A) | Status |
|--------|---------------|----------------|--------|
| Registry | 84 | 84 | ✅ |
| Selected/active | 84 | 84 | ✅ |
| RankIC summary | 84 | 84 | ✅ |
| Long-short summary | 84 | 84 | ✅ |
| **Shape summary** | **80** | **84** | ✅ fixed |
| **Rolling stability** | **80** | **84** | ✅ fixed |
| **Decile summary** | **80** | **84** | ✅ fixed |
| **Capacity summary** | **80** | **84** | ✅ fixed |
| Scorecard | 84 | 84 | ✅ |
| Profile | 84 | 84 | ✅ |
| Bilingual cards | 84 | 84 | ✅ |
| Public page | 84 | 84 | ✅ |

---

## Page QA

- Total checks: 28
- PASS: 28
- FAIL: 0
- New checks passed: `pm53b_count_match` (84 factors), `pm53b_factor_diagnostics` (all 84 have shape/decile/capacity/scorecard/profile)

---

## Integrity QA

- Factors checked: 4
- Total checks: 76 (4 × 19)
- PASS: 76
- FAIL: 0
- WARN: 0

---

## Public Page

- Deployed: `/var/www/momentum-report/factor-library/factor-evaluation.html`
- Size: 6,524,360 bytes (6.34 MB)
- Factor count: 84/84 visible
- All 84 factors have shape/decile/capacity/scorecard/profile diagnostics

---

## What Changed vs PM-53

1. **factor_values computed**: 4 non-cap factors now have `factor_values.parquet` (panel computation)
2. **Paper diagnostics**: 4 factors added to paper summary, turnover, monthly returns, fee sensitivity, leg decomposition, drawdown
3. **Redundancy**: 326 new pairwise pairs computed (4 factors × 83 others)
4. **Regime**: 4 factors added to regime diagnostics
5. **Shape/stability/decile/capacity**: All 4 factors now have these outputs
6. **Scorecard/profile/page**: All refreshed with 84 factors

## What Did NOT Change

- No new factors added
- No formula changes
- No expected_direction changes
- No cap data source changes
- No RankIC/LS computation changes
- No signal construction
- No trading recommendations

---

## Remaining Limitations

1. 4 non-cap factors have `CAPACITY_FRAGILE` or `INSUFFICIENT_DATA` cost class (volume-based factors, expected)
2. `a101_vol_xs_z_product_112h` has negative gross Sharpe (-0.47) — not a trading signal, diagnostic only
3. Evidence completeness: 92.96% mean (71 factors INCOMPLETE, 13 COMPLETE) — normal for diagnostic library

---

## Recommended Next PM

**PM-54**: Factor library quality review — evaluate which of the 84 factors qualify as STRONG_RESEARCH_CANDIDATE vs REVIEW_REQUIRED, based on the now-complete workflow data.
