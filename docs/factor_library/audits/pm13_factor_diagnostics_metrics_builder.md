# PM-13 Factor Diagnostics Metrics Builder

**Date:** 2026-06-21
**Follows:** PM-12 (factor diagnostics product spec)

---

## Summary Verdict

**`PARTIAL_PASS_MONTHLY_LS_MISSING`**

Monthly IC series successfully generated for all 71 factors × 4 horizons × 25 months. Monthly long-short returns unavailable because `factor_level_quantile_return_summary.csv` lacks a period/month column — it aggregates quantile returns across all time. Sharpe, drawdown, cumulative curve all depend on monthly LS and are therefore also unavailable.

## A. Evaluation Refresh

**Required:** Yes. Canonical evaluation covered only 65/71 factors (missing 6 alpha158 batch factors from PM-09).

**Action taken:** Ran `scripts/evaluate_factors.py` (3182s). Result: 71/71 factors now in evaluation outputs.

**Updated artifacts:**
- factor_level_metric_panel.csv: 284 rows (71 factors × 4 horizons)
- factor_level_period_ic_summary.csv: 7076 rows (71 × 4 × 25 months)
- factor_level_quantile_return_summary.csv: 1420 rows (71 × 4 × 5 buckets)
- factor_level_long_short_summary.csv: 284 rows
- factor_level_formula_catalog.csv: 71 rows
- factor_level_candidate_review.csv: 71 rows

## B. Files Generated

| File | Rows | Factors | Status |
|------|------|---------|--------|
| factor_diagnostics_summary.csv | 71 | 71 | ✅ |
| factor_diagnostics_summary.json | 71 | 71 | ✅ |
| factor_monthly_ic_series.csv | 7076 | 71 | ✅ |
| factor_monthly_long_short_series.csv | 0 | 0 | ⚠️ Empty (schema gap) |
| factor_cumulative_long_short_curve.csv | 0 | 0 | ⚠️ Empty (depends on LS) |
| manifest.json | — | — | ✅ |

## C. Availability Matrix

| Metric | Available | Source |
|--------|-----------|--------|
| Monthly IC | ✅ | period_ic_summary (monthly aggregation) |
| Monthly IC positive rate | ✅ | Derived from monthly IC |
| RankIC mean/std/IR/t-stat | ✅ | metric_panel (best horizon) |
| Coverage rate | ✅ | metric_panel (row count / total rows) |
| Redundancy level | ⚠️ Sparse | factor_redundancy.csv (6 pairs only) |
| Decision bucket | ✅ | candidate_review |
| Monthly LS return | ❌ | quantile_return_summary lacks period column |
| Cumulative LS curve | ❌ | Depends on monthly LS |
| Sharpe ratio | ❌ | Depends on monthly LS |
| Annualized return/vol | ❌ | Depends on monthly LS |
| Max drawdown | ❌ | Depends on cumulative LS |

## D. Schema Gap

**Root cause:** `evaluate_factors.py` computes quantile returns by grouping `(timestamp, bucket)` and then aggregating across all timestamps into a single mean. The per-timestamp bucket returns are computed internally (line 301: `bucket_ts = hz_merged.groupby(["timestamp", "bucket"])[ret_col].mean().unstack()`) but not outputted with period labels.

**Fix required:** Extend `evaluate_factors.py` to output period-level (monthly) quantile returns. This is a ~50-line change: add a period column to the quantile_long_short rows, group by period before aggregating.

**Recommendation:** PM-13B — extend evaluator to output monthly quantile returns, then re-run diagnostics builder.

## E. Diagnostics Summary Highlights

| Metric | Value |
|--------|-------|
| Factors with IC data | 71/71 |
| Factors with LS data | 0/71 |
| Best horizon distribution | 1h: 19, 4h: 19, 24h: 17, 72h: 16 |
| Mean coverage rate | 99.5%+ |

## F. Non-Change Statement

- No factor formulas modified
- No signal panel modified
- No public pages modified
- No production/live/tradeability/alpha claims
- Evaluation refresh was required (6 factors missing) and performed

## G. Next PM

**PM-13B:** Extend `evaluate_factors.py` to output period-level quantile returns, then re-run diagnostics builder to generate monthly LS, cumulative curve, Sharpe, and drawdown.
