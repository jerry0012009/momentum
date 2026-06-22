# PM-44: Factor Evaluation Layer Freeze, Transparency, and Reproducibility Audit

**Date:** 2026-06-23
**Verdict:** `EVALUATION_LAYER_V0_1_FROZEN`

---

## Summary

Factor evaluation layer v0.1 is frozen. The system is stable, transparent, and reproducible.

## Stale Warnings Check

✅ All 76 factors clean of stale warnings:
- `no_horizon_data`: 0 occurrences
- `monthly_ls_unavailable`: 0 occurrences
- `evidence_incomplete`: 0 occurrences
- `fee_sensitivity stale`: 0 occurrences

## Factor Evaluation Layer v0.1 Boundary

**IN SCOPE:** RankIC, LS, paper portfolio, fee sensitivity, regime/BTC, shape, stability, decile, capacity, liquidity, redundancy, cluster, marginal, scorecard, profile, page.

**OUT OF SCOPE:** Signal panel, entry/exit rules, position sizing, portfolio construction, live trading.

**Recommendation:** Stop at factor evaluation layer. Do not enter signal construction until factor interpretation is complete.

## PM-35 Five-Factor Completeness

| Factor | Integrity | Scorecard | Regime | Pairwise | Page QA |
|--------|-----------|-----------|--------|----------|---------|
| rev_2h | 11/11 ✅ | 57.0 | REGIME_ROBUST | ✅ | ✅ |
| mom_vol_adjusted_20h | 11/11 ✅ | 50.5 | REGIME_ROBUST | ✅ | ✅ |
| range_breakout_vol_confirm_20h | 11/11 ✅ | 49.9 | BTC_BETA_SENSITIVE | ✅ | ✅ |
| volume_pressure_20h | 11/11 ✅ | 51.5 | VOL_DEPENDENT | ✅ | ✅ |
| xs_rank_mom_accel | 11/11 ✅ | 48.9 | REGIME_ROBUST | ✅ | ✅ |

## START_HERE Adequacy

✅ START_HERE.md now includes:
- Factor evaluation layer v0.1 boundary definition
- New factor complete workflow (6 steps)
- Key document references (FACTOR_EVALUATION_LAYER_V0_1.md, POST_INTAKE_WORKFLOW_RUNBOOK.md, NEW_FACTOR_INTAKE_REPRODUCIBILITY_TEST_PLAN.md)
- Canonical vs defensive data source clarification

## Reproducibility

✅ `run_post_intake_workflow_completion.py` automates steps 5-16 of the workflow.
✅ `check_post_intake_workflow_integrity.py` verifies 11 dimensions per factor.
✅ `NEW_FACTOR_INTAKE_REPRODUCIBILITY_TEST_PLAN.md` provides 16-step dry-run plan.

## Remaining Manual Steps

1. **Factor formula design** — requires domain knowledge, cannot be automated.
2. **Registry entry** — `factor_ops.py` must be called to register the factor.
3. **Factor values computation** — `build_factor_values.py` must be run.
4. **Evaluation + paper diagnostics** — EXPENSIVE, must be run once per factor.
5. **Pairwise redundancy** — EXPENSIVE, must be run once per factor.
6. **Interpretation** — requires human judgment on expected direction and economic mechanism.

Steps 4-5 can be automated via `run_post_intake_workflow_completion.py` (without `--skip-expensive`).

## No Formula / Expected Direction / Factor Values / Signal Changes

- No `factor_formula_registry.py` changes
- No `factor_ops.py` changes
- No `build_factor_values.py` changes
- No `expected_direction` changes
- No signal panel changes

## QA Results

- `check_factor_evaluation_page_completeness.py`: 23/23 PASS
- `check_post_intake_workflow_integrity.py`: 55/55 PASS (5 factors × 11 checks)
- Public page: HTTP 200
- Stale warnings: 0/76 factors

## New Documents Created

1. `docs/factor_library/FACTOR_EVALUATION_LAYER_V0_1.md` — system boundary, 14 data blocks, pipeline order, completeness criteria
2. `docs/factor_library/NEW_FACTOR_INTAKE_REPRODUCIBILITY_TEST_PLAN.md` — 16-step dry-run plan

## Files Changed

1. `docs/factor_library/FACTOR_EVALUATION_LAYER_V0_1.md` — new
2. `docs/factor_library/NEW_FACTOR_INTAKE_REPRODUCIBILITY_TEST_PLAN.md` — new
3. `docs/factor_library/START_HERE.md` — updated with v0.1 freeze section
4. `docs/factor_library/audits/pm44_factor_evaluation_layer_freeze_transparency_reproducibility.md` — new

## Recommended Next Steps

1. **Factor interpretation** — understand expected direction and economic mechanism for PM-35 factors
2. **Batch02 planning** — design next batch of factors based on evaluation learnings
3. **Dry-run test** — execute NEW_FACTOR_INTAKE_REPRODUCIBILITY_TEST_PLAN.md with a truly new factor
