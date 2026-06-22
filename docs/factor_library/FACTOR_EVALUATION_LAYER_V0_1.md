# Factor Evaluation Layer v0.1 — Freeze Specification

**Frozen:** 2026-06-23 (PM-44)
**Status:** STABLE — no new features until v0.2

---

## 1. What Is the Factor Evaluation Layer?

The factor evaluation layer is the **data pipeline that measures a factor's statistical properties**. It answers: "Is this factor worth investigating further?" — NOT "Should we trade this?"

## 2. Boundary: What Belongs Here

| IN SCOPE (factor evaluation) | OUT OF SCOPE (signal construction) |
|------------------------------|-------------------------------------|
| Factor formula + value computation | Signal panel design |
| RankIC / IR / t-stat | Entry/exit rules |
| Monthly IC time series | Position sizing |
| Long-short spread metrics | Portfolio construction |
| Paper portfolio diagnostics | Live trading |
| Fee sensitivity curve | Execution logic |
| Regime / BTC correlation | Regime-adaptive switching |
| Quantile shape + decile analysis | Factor combination |
| Rolling stability | Multi-factor models |
| Capacity / liquidity | Order management |
| Pairwise redundancy / cluster | Risk management |
| Quality scorecard | — |
| Unified profile | — |
| Public evaluation page | — |

## 3. Why We Stop Here

- Signal construction requires directional conviction — we don't have it yet for most factors.
- Factor interpretation (expected direction, economic mechanism) must precede signal design.
- We need reproducible evaluation before adding complexity.
- Current 76 factors need triage before investing in signal engineering.

## 4. Required Data Blocks for a Complete Evaluation

A factor's evaluation is **complete** when all 14 blocks below are present and pass QA.

| # | Block | Canonical Source Script | Output File | QA Check |
|---|-------|------------------------|-------------|----------|
| 1 | Registry entry | `factor_ops.py` | `factor_library_state.json` | Factor ID in registered_factor_ids |
| 2 | Factor values | `build_factor_values.py` | `factor_values.parquet` | File exists, non-empty |
| 3 | Factor-level RankIC | `evaluate_factors.py` | `factor_level_rankic_summary.csv` | Factor present, rankic_mean populated |
| 4 | Period IC | `evaluate_factors.py` | `factor_level_period_ic_summary.csv` | 25 months of IC data |
| 5 | Period LS | `evaluate_factors.py` | `factor_level_period_long_short_summary.csv` | 25 months of LS data |
| 6 | LS aggregate | `evaluate_factors.py` | `factor_level_long_short_summary.csv` | std/ann_ret/ann_vol/max_dd/pos_rate populated |
| 7 | Paper portfolio | `build_single_factor_paper_page_payload.py` | `single_factor_paper_page_payload.json` | Factor in payload, NAV series present |
| 8 | Fee sensitivity | (inside paper payload) | `single_factor_fee_sensitivity.csv` | Fee curve data points present |
| 9 | Regime / BTC | `build_factor_market_regime_diagnostics.py` | `factor_regime_exposure_summary.csv` | regime_class ≠ INSUFFICIENT_REGIME_DATA |
| 10 | Redundancy / cluster / marginal | `build_factor_pairwise_redundancy_matrix.py` + `build_factor_redundancy_cluster_diagnostics.py` | `factor_pairwise_redundancy.csv` + `factor_redundancy_clusters.csv` + `factor_redundancy_summary.csv` | nearest_factor not None, cluster_id populated |
| 11 | Capacity / liquidity | `build_factor_capacity_liquidity_summary.py` | `factor_capacity_liquidity_summary.csv` | capacity class populated |
| 12 | Shape / stability / decile | `build_factor_quantile_shape_summary.py` + `build_factor_rolling_stability.py` + `build_factor_decile_shape_summary.py` | Multiple CSVs | quantile_shape_class populated |
| 13 | Quality scorecard | `build_factor_quality_scorecard.py` | `factor_quality_scorecard.csv` | rankic_mean ≠ 0, coverage ≠ 0 |
| 14 | Unified profile | `build_unified_factor_profile.py` | `factor_unified_profile_summary.csv` | profile_score populated, profile_class populated |

## 5. Stage Pipeline Order

```
1. Registry entry          (factor_ops.py)
2. Factor values           (build_factor_values.py)
3. Factor-level evaluation (evaluate_factors.py)  ← EXPENSIVE
4. Paper diagnostics       (build_single_factor_paper_portfolio_diagnostics.py)  ← EXPENSIVE
5. Paper page payload      (build_single_factor_paper_page_payload.py)
6. Pairwise redundancy     (build_factor_pairwise_redundancy_matrix.py)  ← EXPENSIVE
7. Cluster + marginal      (build_factor_redundancy_cluster_diagnostics.py)
8. Regime / BTC            (build_factor_market_regime_diagnostics.py --canonical-ic-path)
9. Capacity / liquidity    (build_factor_capacity_liquidity_summary.py)
10. Shape / stability      (build_factor_quantile_shape_summary.py + rolling stability + decile)
11. Scorecard              (build_factor_quality_scorecard.py)
12. Unified profile        (build_unified_factor_profile.py)
13. Page build             (_build_factor_eval_html.py)
14. Page QA                (check_factor_evaluation_page_completeness.py)
15. Integrity QA           (check_post_intake_workflow_integrity.py)
```

## 6. How to Judge "Evaluation Complete"

A factor is **evaluation complete** when:

1. All 14 data blocks exist with non-null values.
2. `check_post_intake_workflow_integrity.py` reports 11/11 PASS.
3. `check_factor_evaluation_page_completeness.py` shows no FAIL for that factor.
4. The public page displays all sections without "—", "N/A", or stale warnings.

## 7. Canonical vs Defensive Data Sources

| Data | Canonical Source | Defensive Fallback |
|------|-----------------|-------------------|
| RankIC / LS metrics | `factor_level_rankic_summary.csv` | `factor_diagnostics_summary.csv` (legacy, may have NaN) |
| Monthly IC | `factor_level_period_ic_summary.csv` | `factor_monthly_ic_series.csv` (legacy, may be incomplete) |
| Scorecard scores | Canonical factor-level evaluation CSVs | `factor_diagnostics_summary.csv` (stale for new factors) |
| Regime IC source | `--canonical-ic-path` flag | `factor_monthly_ic_series.csv` |
| Page source_warning | Scorecard (cleared when canonical data exists) | Page builder fallback strip |

**Rule:** Canonical sources are always preferred. Defensive fallbacks exist only to prevent crashes, not as data sources.

## 8. Version History

| Version | Date | Changes |
|---------|------|---------|
| v0.1 | 2026-06-23 | Initial freeze. 76 factors. PM-35 batch complete. |
