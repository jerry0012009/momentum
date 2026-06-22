# PM-37: Incremental Redundancy / Cluster / Rolling-Stability Completion

**Date:** 2026-06-22
**Verdict:** `INCREMENTAL_REDUNDANCY_STABILITY_COMPLETION_PASS`

## 1. Why PM-37 Was Required

PM-36 completed decile-shape and capacity-liquidity blocks (8/12). Four blocks remained missing:
- redundancy_summary
- redundancy_cluster_members
- marginal_information
- rolling_stability

These required running `build_factor_pairwise_redundancy_matrix.py` (expensive, C(76,2)=2850 pairs) and `build_factor_shape_stability_diagnostics.py`.

## 2. Redundancy Completion Method

**Incremental mode.** Added `--factor-ids` to `build_factor_pairwise_redundancy_matrix.py`:
- Loaded all 76 factors (needed for pairwise computation)
- Computed only 365 pairs involving the 5 target factors (vs 2850 full)
- Merged with existing pairwise output (dropped old rows for target factors, added new)
- Rebuilt summary, clusters, and correlation matrices from merged data

## 3. Rolling Stability Fix

Added `--factor-ids` to `build_factor_shape_stability_diagnostics.py`:
- Computed shape/stability for 5 target factors only
- Merged with existing outputs
- New factors correctly classified as `INSUFFICIENT_HISTORY` (stability=None) due to insufficient monthly IC data

## 4. Evidence Matrix Before/After

| Factor | Before | After |
|---|---|---|
| rev_2h | 8/12 INCOMPLETE | 12/12 COMPLETE |
| mom_vol_adjusted_20h | 8/12 INCOMPLETE | 12/12 COMPLETE |
| range_breakout_vol_confirm_20h | 8/12 INCOMPLETE | 12/12 COMPLETE |
| volume_pressure_20h | 8/12 INCOMPLETE | 12/12 COMPLETE |
| xs_rank_mom_accel | 8/12 INCOMPLETE | 12/12 COMPLETE |

## 5. Unified Profile After

| Factor | profile_class | workflow_ready | action |
|---|---|---|---|
| rev_2h | PROMISING_BUT_REGIME_DEPENDENT | WORKFLOW_READY | WATCH_FOR_REGIME_DEPENDENCE |
| mom_vol_adjusted_20h | PROMISING_BUT_REGIME_DEPENDENT | WORKFLOW_READY | WATCH_FOR_REGIME_DEPENDENCE |
| range_breakout_vol_confirm_20h | LOW_PRIORITY_DIAGNOSTIC | WORKFLOW_READY | LOWER_PRIORITY_REVIEW |
| volume_pressure_20h | PROMISING_BUT_REGIME_DEPENDENT | WORKFLOW_READY | WATCH_FOR_REGIME_DEPENDENCE |
| xs_rank_mom_accel | PROMISING_BUT_REGIME_DEPENDENT | WORKFLOW_READY | WATCH_FOR_REGIME_DEPENDENCE |

## 6. Resource Safeguards

- Pairwise: incremental mode computed 365 pairs instead of 2850 (87% reduction)
- Shape stability: subset mode computed 5 factors instead of 76
- No full-library reruns needed

## 7. Files Changed

- `scripts/build_factor_pairwise_redundancy_matrix.py` — added --factor-ids, --only-missing, incremental merge
- `scripts/build_factor_shape_stability_diagnostics.py` — added --factor-ids, --only-missing, incremental merge
- `research/.../factor_pairwise_redundancy.csv` — merged 5 new factors
- `research/.../factor_redundancy_summary.csv` — 76 factors
- `research/.../factor_redundancy_cluster_members.csv` — 76 factors
- `research/.../factor_marginal_information_summary.csv` — 76 factors
- `research/.../factor_rolling_stability_summary.csv` — 76 factors
- `research/.../factor_shape_stability_*.csv/json` — updated
- `research/.../factor_evaluation_evidence_matrix.csv` — all 76 COMPLETE
- `research/.../factor_unified_profile_summary.csv` — updated
- `reports/site/factor-library/factor-evaluation.html` — refreshed

## 8. Non-Change Statement

- No factor formulas modified
- No factor_values modified
- No signal panel modified
- No live/strategy code modified

## 9. Remaining Limitations

1. Rolling stability for new factors is `INSUFFICIENT_HISTORY` — they need more monthly IC data
2. `range_breakout_vol_confirm_20h` classified as `LOW_PRIORITY_DIAGNOSTIC` (coverage 16.8%)

## 10. Recommended Next PM

**PM-38: Post-intake factor interpretation and direction-semantics review**
