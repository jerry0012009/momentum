# PM-59A-UI-DATA-LINEAGE-CLEANUP: Audit

**Date:** 2026-06-25
**Status:** COMPLETE

## 1. Before cleanup: Source of `redundancy_level` / `nearest_redundant_factor` in `factor_diagnostics_summary.csv`

> **Before cleanup (pre-a851527).** See §6 for post-cleanup state.

**Source script:** `scripts/build_factor_diagnostics_metrics.py` (L176, L194-202, L281-282, L316-317)

The script read `factor_redundancy.csv` (old pairwise file, **did not exist** in repo).
When the file was missing, `rd_lookup` was empty → all factors got `redundancy_level = UNKNOWN`, `nearest_redundant_factor = ""`.

For `rev_1h` specifically: the CSV showed `redundancy_level = LOW_REDUNDANCY`, `nearest_redundant_factor = mom_72h`.
This was stale data from a previous run when `factor_redundancy.csv` existed.

**Secondary fallback** in `_build_factor_eval_html.py` (L829-834): when `redundancy_level == UNKNOWN`, it backfilled from `marginal_information_class`:
- `DISTINCT_SINGLETON` → `LOW_REDUNDANCY`
- `MOSTLY_REDUNDANT` → `MODERATE_REDUNDANCY`

This fallback used cluster-derived data, NOT the PM-18 canonical redundancy summary. **Now removed.**

## 2. Before cleanup: Source of `nearest_factor` / `strongest_redundancy_level` in `factor_redundancy_summary.csv`

**Source script:** `scripts/build_factor_pairwise_redundancy_matrix.py` → `build_factor_redundancy_cluster_diagnostics.py`

These are produced by the PM-18 full pairwise redundancy pipeline (Spearman+Pearson correlation matrix → cluster analysis).
Canonical fields: `nearest_factor`, `nearest_abs_spearman_corr`, `strongest_redundancy_level`, `novelty_assessment`, etc.

## 3. `rev_1h` Conflict

| Source | `nearest_factor` | `redundancy_level` | `novelty_assessment` |
|--------|-----------------|-------------------|---------------------|
| `factor_diagnostics_summary.csv` (legacy) | `mom_72h` | `LOW_REDUNDANCY` | *(not present)* |
| `factor_redundancy_summary.csv` (canonical) | `intraday_ret` | `NEAR_DUPLICATE` | `HIGHLY_REDUNDANT` |

**Verdict:** Direct conflict. Canonical source says `rev_1h` is NEAR_DUPLICATE with `intraday_ret` (ρ=0.9949).
Legacy source says LOW_REDUNDANCY with `mom_72h` — stale and wrong.

## 4. Other Conflicts

82 factors show conflicts between the two sources:
- 80 factors have `UNKNOWN` in diag summary (because `factor_redundancy.csv` doesn't exist) vs real values in redundancy summary
- 2 factors (`rev_1h`, `mom_120h`) have explicit conflicting nearest_factor values

## 5. Page Dual Display

**YES** — the page currently shows BOTH sets of redundancy information:

1. **Legacy compact kv** (L3054-3061 in `_build_factor_eval_html.py`):
   - `Redundancy 冗余度` → `f.redundancy_level` (from diag summary, mostly UNKNOWN/stale)
   - `Nearest Factor 最近因子` → `f.nearest_redundant_factor` (stale)
   - `Decision Bucket 决策桶` → `f.decision_bucket`
   - `Recommended Action 建议操作` → `f.recommended_action`
   - `Source Warning 源警告` → `f.source_warning`

2. **Canonical Redundancy & Novelty section** (L3070+):
   - `Novelty Assessment` → `f.novelty_assessment` (from PM-18 scorecard)
   - `Nearest Factor` → `f.nearest_factor` (canonical)
   - `Nearest abs Spearman` → `f.nearest_abs_spearman_corr` (canonical)
   - `Strongest Redundancy` → `f.strongest_redundancy_level` (canonical)

For `rev_1h`, the legacy block shows `LOW_REDUNDANCY / mom_72h` while the canonical block shows `HIGHLY_REDUNDANT / intraday_ret (0.9949)`.

## Recommendation

1. Remove legacy compact kv entirely
2. Fix `build_factor_diagnostics_metrics.py` to read from canonical `factor_redundancy_summary.csv`
3. Remove/rename legacy fields in payload
4. Add QA checks to prevent regression

## 6. Post-cleanup verification

After commit a851527:
- Legacy compact redundancy block has been removed from factor-evaluation.html.
- Redundancy & Novelty is the only user-facing redundancy section.
- `factor_diagnostics_summary.csv` now reads canonical PM-18 redundancy summary (`factor_redundancy_summary.csv`).
- `rev_1h` uses `nearest_factor=intraday_ret`, `nearest_abs_spearman_corr=0.994932`, `strongest_redundancy_level=NEAR_DUPLICATE`, `novelty_assessment=HIGHLY_REDUNDANT`.
- Page QA includes `lineage_no_legacy_compact` and `lineage_rev1h_canonical`.
- Legacy fields isolated to `legacy_*` prefix in payload (not user-facing).
