# PM-36: Resource Audit and Incremental Missing Diagnostics Repair

**Date:** 2026-06-22
**Verdict:** `RESOURCE_AUDIT_INCREMENTAL_DIAGNOSTICS_PASS_WITH_LIMITATIONS`

## 1. Why PM-36 Was Required

PM-35 registered 5 new factors (rev_2h, mom_vol_adjusted_20h, range_breakout_vol_confirm_20h, volume_pressure_20h, xs_rank_mom_accel). During PM-35's full refresh, the server hit OOM (15GB RAM, no swap) because:

- `build_factor_values.py` loads bars (1.25GB) + taker (1.30GB) + funding merge (~1.3GB), peak ~4GB
- `build_factor_decile_shape_diagnostics.py` loads ALL 76 factor_values parquet files sequentially
- `build_factor_capacity_liquidity_diagnostics.py` loads ALL 76 factor_values parquet + volume data

PM-35 completed factor_values and factor-level evaluation but decile-shape and capacity-liquidity timed out/OOMed.

## 2. Stages Identified as Heavy

| Stage | Script | is_expensive | recomputes_all |
|---|---|---|---|
| evaluate | evaluate_factors.py | moderate | no (supports subset) |
| redundancy | check_factor_redundancy.py | moderate | yes |
| paper-diagnostics | build_single_factor_paper_portfolio_diagnostics.py | expensive | yes (but has --factor-ids) |
| shape-stability | build_factor_shape_stability_diagnostics.py | moderate | yes |
| decile-shape | build_factor_decile_shape_diagnostics.py | expensive | yes → NOW supports subset |
| capacity-liquidity | build_factor_capacity_liquidity_diagnostics.py | expensive | yes → NOW supports subset |
| profile | build_unified_factor_profile.py | light | yes |
| staleness | check_factor_library_staleness.py | light | yes |
| page | _build_factor_eval_html.py | moderate | yes |

## 3. Stages Made Incremental

### 3.1 Decile-shape (`build_factor_decile_shape_diagnostics.py`)

Added CLI args:
- `--factor-ids comma,separated,list` — compute only these factors
- `--only-missing` — auto-detect from evidence matrix where `has_decile_shape == False`

Subset mode: loads existing CSV outputs, drops rows for target factors, computes only targets, merges back. Payload and manifest rebuilt from merged data (includes ALL factors).

### 3.2 Capacity-liquidity (`build_factor_capacity_liquidity_diagnostics.py`)

Same pattern:
- `--factor-ids comma,separated,list`
- `--only-missing` — auto-detect where `has_capacity_liquidity == False`

Subset mode: filters factor loop to targets only. Volume data and vol_lookup still loaded (shared). Merges with existing summary/monthly outputs.

### 3.3 Resource audit outputs

- `factor_workflow_resource_audit.csv`
- `factor_workflow_resource_audit.json`

## 4. PM-35 Factor Completion Status

### Evidence matrix before (PM-35):
```
All 5 factors: 2/12 blocks, has_decile_shape=False, has_capacity_liquidity=False, INCOMPLETE
```

### Evidence matrix after (PM-36):
```
All 5 factors: 8/12 blocks, has_decile_shape=True, has_capacity_liquidity=True, INCOMPLETE
```

### Still missing (4 blocks):
- `redundancy_summary` — from build_factor_redundancy_cluster_diagnostics.py (no subset support)
- `redundancy_cluster_members` — same
- `marginal_information` — same
- `rolling_stability` — from build_factor_shape_stability_diagnostics.py (computed but stability=None for new factors)

### Paper portfolio (intermediate step):
Ran `build_single_factor_paper_portfolio_diagnostics.py --factor-ids` for 5 new factors, merged into existing 71-factor outputs. New factors now have turnover, summary, monthly, leg, drawdown data.

### Capacity/liquidity results:
| Factor | Capacity Risk | Liquidity Risk | Combined |
|---|---|---|---|
| rev_2h | MODERATE_CAPACITY_RISK | LIQUIDITY_FRAGILE | WATCH_LIQUIDITY |
| mom_vol_adjusted_20h | CAPACITY_FRIENDLY | LIQUIDITY_FRAGILE | WATCH_LIQUIDITY |
| range_breakout_vol_confirm_20h | CAPACITY_BLOCKED_BY_TURNOVER | LIQUIDITY_FRAGILE | WATCH_BOTH |
| volume_pressure_20h | CAPACITY_FRIENDLY | LIQUIDITY_FRAGILE | WATCH_LIQUIDITY |
| xs_rank_mom_accel | MODERATE_CAPACITY_RISK | LIQUIDITY_FRAGILE | WATCH_LIQUIDITY |

## 5. Profile/Status After

All 5 factors: `profile_class=INCOMPLETE_EVIDENCE`, `workflow_ready_status=WORKFLOW_INCOMPLETE`

Remaining missing blocks require full-library rerun of redundancy diagnostics (expensive, ~5min).

## 6. Staleness Result

`check_factor_library_staleness.py` ran successfully. Recommends running redundancy + state stages.

## 7. Page Refresh Result

`_build_factor_eval_html.py` produced `factor-evaluation.html` (2,850,892 bytes). All 76 factors present.

## 8. Unrelated Report Hygiene

Only `reports/site/factor-library/factor-evaluation.html` was modified by page refresh.

## 9. Files Changed

- `scripts/build_factor_decile_shape_diagnostics.py` — added --factor-ids, --only-missing, subset merge
- `scripts/build_factor_capacity_liquidity_diagnostics.py` — added --factor-ids, --only-missing, subset merge
- `research/.../factor_workflow_resource_audit.csv` — new
- `research/.../factor_workflow_resource_audit.json` — new
- `research/.../factor_decile_*.csv/json` — merged 5 new factors
- `research/.../factor_capacity_liquidity_*.csv/json` — merged 5 new factors
- `research/.../single_factor_paper_*.csv` — merged 5 new factors
- `research/.../factor_shape_stability_payload.json` — 76 factors
- `research/.../factor_evaluation_evidence_matrix.csv` — 8/12 blocks for new factors
- `research/.../factor_unified_profile_summary.csv` — updated
- `reports/site/factor-library/factor-evaluation.html` — refreshed

## 10. Non-Change Statement

- No factor formulas modified
- No factor_values parquet modified
- No signal panel modified
- No live/strategy/execution code modified
- No new factors added

## 11. Remaining Limitations

1. **4 evidence blocks still missing** for PM-35 factors: redundancy_summary, redundancy_cluster_members, marginal_information, rolling_stability. These require full-library rerun of `build_factor_redundancy_cluster_diagnostics.py`.
2. **Rolling stability** computed but returns None for new factors (insufficient history).
3. **Server memory**: 15GB RAM, no swap. Full-library reruns of heavy scripts risk OOM.

## 12. Recommended Next PM

**PM-37: Post-intake factor interpretation review** — review the 5 new factors' decile shape, capacity/liquidity, and paper portfolio results. Determine if any formula adjustments are needed before pursuing full evidence completion.
