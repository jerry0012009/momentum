# PM-58A: LS Monthly Aggregate Backfill

**Date:** 2026-06-24
**Status:** Backfill of historical missing fields.
**Verdict:** PM58A_LS_MONTHLY_AGGREGATE_BACKFILL_PASS

---

## 1. Summary

Backfilled 284/336 missing LS monthly aggregate rows in `factor_level_long_short_summary.csv`.
All 84 active factors × 4 horizons now have complete LS monthly aggregate fields.
No full evaluate_factors.py run was needed — backfill used existing monthly LS series.

## 2. Root Cause

`evaluate_factors.py` PM-41 code (monthly LS aggregate computation) was added after most factors
were already evaluated. The canonical `factor_level_long_short_summary.csv` was assembled from
multiple intake batches:

- **52/336 rows** (13 factors × 4 horizons): evaluated after PM-41 → had data
- **284/336 rows** (71 factors × 4 horizons): evaluated before PM-41 → fields were NaN

The monthly LS series (`factor_monthly_long_short_series.csv`) had full 84×4 coverage,
so the aggregate fields could be computed without re-running the full evaluation pipeline.

## 3. Files Changed

| File | Change |
|------|--------|
| `scripts/backfill_ls_monthly_aggregate_fields.py` | **New** — backfill script |
| `research/.../factor_level_long_short_summary.csv` | 284 rows backfilled |
| `research/.../factor_level_long_short_summary.json` | **New** — JSON mirror |
| `reports/.../factor-evaluation.html` | Rebuilt (6.90 MB) |
| `scripts/check_active_factor_workflow_consistency.py` | PM-58A LS monthly aggregate check |
| `scripts/check_factor_evaluation_page_completeness.py` | PM-58A page check |
| `scripts/check_post_intake_workflow_integrity.py` | PM-58A integrity check |
| `docs/factor_library/FACTOR_EVALUATION_WORKFLOW_BOUNDARY.md` | §7: LS monthly aggregate |
| `docs/factor_library/POST_INTAKE_WORKFLOW_RUNBOOK.md` | §14.7: LS monthly aggregate |
| `docs/factor_library/REGENERATION_CONTRACT.md` | §10.9: LS monthly aggregate |
| `docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md` | §16: LS monthly aggregate |
| `docs/factor_library/audits/pm58a_ls_monthly_aggregate_backfill.md` | **This file** |

## 4. Input File Coverage

| File | Coverage |
|------|----------|
| `factor_monthly_long_short_series.csv` | 84/84 factors × 4/4 horizons = 336 combos, 8376 rows |
| `factor_library_state.json` | 84 registered factors |

## 5. Before/After Missing Counts

| Field | Before Missing | After Missing |
|-------|---------------|---------------|
| `long_short_spread_std` | 284/336 | 0/336 |
| `long_short_spread_annualized_return` | 284/336 | 0/336 |
| `long_short_spread_annualized_vol` | 284/336 | 0/336 |
| `long_short_spread_max_drawdown` | 284/336 | 0/336 |
| `long_short_spread_positive_period_rate` | 284/336 | 0/336 |
| `n_monthly_periods` | 284/336 | 0/336 |

## 6. Calculation Rules

Match `evaluate_factors.py` PM-41 logic exactly:

```
std = monthly_ls_returns.std(ddof=1)
mean = monthly_ls_returns.mean()
annualized_return = mean * 12
annualized_vol = std * sqrt(12)
cum = cumprod(1 + monthly_ls_returns)
peak = maximum.accumulate(cum)
drawdown = (cum - peak) / peak
max_drawdown = drawdown.min()
positive_period_rate = mean(monthly_ls_returns > 0)
n_monthly_periods = len(monthly_ls_returns)
annualization_method = "monthly_x12"
```

## 7. Full Evaluate Avoided

Yes. Backfill used `factor_monthly_long_short_series.csv` (pre-computed monthly LS returns)
to compute aggregates without re-running the full evaluation pipeline. This avoids:
- Unnecessary diff in other evaluation outputs
- Risk of changing existing LS mean/t-stat/win-rate values
- Long compute time for 84 factors × 4 horizons

## 8. QA Results

```
Consistency Checker: 16/16 PASS (including new PM-58A ls_monthly_aggregate check)
Integrity QA: PASS (all 84×4 = 336 rows, all 6 fields non-null, n_monthly_periods ≥ 2)
Page QA: 49/49 PASS (including new PM-58A check)
```

## 9. Page Verification

- rev_1h 1h: LS Std=0.000282, Ann Return=0.001443, Max DD=-0.000769, Win Rate=68.0%
- All 84 factors: 0 missing LS fields in page payload
- No blank "—" for LS Std/Ann Return/Ann Vol/Max Drawdown when monthly series exists

## 10. No Unauthorized Changes

- No formula changes
- No expected_direction changes
- No factor_values changes
- No cap data changes
- No RankIC changes
- No scorecard changes
- No best_horizon changes
- No signal construction
- No paper simulation
- No fee sensitivity
- LS mean/t-stat/win-rate values unchanged (only monthly aggregate fields added)

## 11. Remaining Limitations

1. `factor_level_long_short_summary.json` is a new file (didn't exist before)
2. Backfill script is a one-time repair tool — future factors should get these fields from evaluate_factors.py
3. n_monthly_periods distribution: 24 rows have 24 months, 312 rows have 25 months

## 12. Recommended Next PM

- **PM-59**: Robust diagnostics trend tracking
- **PM-60**: Historical supply data for true point-in-time cap
