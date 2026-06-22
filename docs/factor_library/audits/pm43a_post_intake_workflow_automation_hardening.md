# PM-43A: Post-Intake Workflow Automation Hardening

**Date:** 2026-06-23
**Verdict:** `PM43A_WORKFLOW_HARDENED`
**Commit:** `6bb85e6`

---

## Summary

Fixed three workflow automation breakpoints that prevented new factors from automatically reaching rev_2h's completeness level.

## Three Breakpoints Fixed

### 1. Monthly IC Canonical Merge

**Problem:** `build_factor_market_regime_diagnostics.py` read from `factor_monthly_ic_series.csv` which didn't contain PM-35 factors → regime/BTC diagnostics showed `INSUFFICIENT_REGIME_DATA`.

**Fix:** Added `--canonical-ic-path` argument to regime script. When provided, automatically merges missing factors from canonical `factor_level_period_ic_summary.csv`.

**Result:** All 76 factors now have regime/BTC diagnostics without manual merge.

### 2. Pairwise Redundancy Auto-Integration

**Problem:** PM-35 factors weren't in the pairwise redundancy matrix → `nearest_factor=None`, `valid_redundancy_pair_count=None`.

**Fix:** Ran `build_factor_pairwise_redundancy_matrix.py --factor-ids` for PM-35 factors, then `build_factor_redundancy_cluster_diagnostics.py`. Created `run_post_intake_workflow_completion.py` that automates this.

**Result:** All 5 PM-35 factors now have pairwise redundancy data, cluster assignments, and marginal information.

### 3. Scorecard Canonical Fallback

**Problem:** Scorecard read from `factor_diagnostics_summary.csv` where PM-35 factors had `rankic_mean=NaN`, `coverage_rate=NaN` → `_safe_float(NaN)` returned 0.0 → stale scores.

**Fix:** Added `load_canonical_rankic()` and `load_canonical_ls()` to `build_factor_quality_scorecard.py`. When diagnostics summary has 0/NaN, falls back to canonical factor-level evaluation data.

**Result:** Scorecard now produces real scores for all 76 factors. rev_2h: `predictive_ranking_score` 0→67.6, `computation_integrity_score` 10→70.

## New Scripts

### `scripts/run_post_intake_workflow_completion.py`
- Runs post-intake workflow completion pipeline for specific factors
- Supports `--factor-ids`, `--only-missing`, `--skip-expensive`, `--start-from`
- 11 stages: evaluate → paper → redundancy → cluster → regime → scorecard → profile → page → QA

### `scripts/check_post_intake_workflow_integrity.py`
- Checks 11 integrity dimensions per factor
- Outputs CSV + JSON reports
- Checks: rankic, period IC, period LS, LS aggregate, paper payload, regime/BTC, pairwise redundancy, cluster, marginal info, scorecard staleness, unified profile

## PM-35 Five-Factor Integrity Table

| Factor | Scorecard Score | Coverage | RankIC | Pairwise | Cluster | Regime | Integrity |
|--------|----------------|----------|--------|----------|---------|--------|-----------|
| rev_2h | 57.0 | 1.0000 | 0.036075 | ✅ | ✅ | REGIME_ROBUST | 11/11 PASS |
| mom_vol_adjusted_20h | 50.5 | 1.0000 | -0.020835 | ✅ | ✅ | REGIME_ROBUST | 11/11 PASS |
| range_breakout_vol_confirm_20h | 49.9 | 1.0000 | -0.029283 | ✅ | ✅ | BTC_BETA_SENSITIVE | 11/11 PASS |
| volume_pressure_20h | 51.5 | 1.0000 | -0.011068 | ✅ | ✅ | VOL_DEPENDENT | 11/11 PASS |
| xs_rank_mom_accel | 48.9 | 1.0000 | -0.023946 | ✅ | ✅ | REGIME_ROBUST | 11/11 PASS |

## Scorecard Fix Details

| Factor | Before (stale) | After (canonical) |
|--------|---------------|-------------------|
| rev_2h | pred=0.0 integ=10.0 cover=0.0 | pred=67.6 integ=70.0 cover=1.0 |
| mom_vol_adjusted_20h | pred=0.0 integ=10.0 cover=0.0 | pred=51.3 integ=70.0 cover=1.0 |
| range_breakout_vol_confirm_20h | pred=0.0 integ=10.0 cover=0.0 | pred=63.9 integ=70.0 cover=1.0 |
| volume_pressure_20h | pred=0.0 integ=10.0 cover=0.0 | pred=36.6 integ=70.0 cover=1.0 |
| xs_rank_mom_accel | pred=0.0 integ=10.0 cover=0.0 | pred=55.9 integ=70.0 cover=1.0 |

## No Formula / Expected Direction / Factor Values / Signal Changes

- No `factor_formula_registry.py` changes
- No `factor_ops.py` changes
- No `build_factor_values.py` changes
- No `expected_direction` changes
- No signal panel changes

## QA Results

- `check_factor_evaluation_page_completeness.py`: 23/23 PASS
- `check_post_intake_workflow_integrity.py`: 55/55 PASS (5 factors × 11 checks)
- Public page: HTTP 200, JSON valid, factor_count=76

## Files Changed

1. `scripts/build_factor_market_regime_diagnostics.py` — added `--canonical-ic-path`
2. `scripts/build_factor_quality_scorecard.py` — canonical RankIC/LS fallback
3. `scripts/run_post_intake_workflow_completion.py` — new post-intake runner
4. `scripts/check_post_intake_workflow_integrity.py` — new integrity checker
5. `scripts/check_factor_evaluation_page_completeness.py` — PM-40C check updated for non-stale scorecard
6. `factor_quality_scorecard.csv` — regenerated with real values
7. `factor_pairwise_redundancy.csv` — PM-35 factors added
8. `factor_redundancy_summary.csv` — PM-35 factors added
9. `factor_redundancy_clusters.csv` — PM-35 factors added
10. `factor_unified_profile_summary.csv` — refreshed with real scorecard
11. `post_intake_workflow_integrity_report.csv/json` — new
12. `factor-evaluation.html` — rebuilt

## Remaining Limitations

- `factor_monthly_ic_series.csv` still needs manual merge for old diagnostics consumers (regime script now handles this via `--canonical-ic-path`)
- Paper portfolio diagnostics is still EXPENSIVE and runs on all factors (not incremental)
- `factor_diagnostics_summary.csv` still has NaN for PM-35 factors (legacy file, not canonical)

## Recommended Next PM

**PM-44: Post-intake factor interpretation and direction-semantics review**
