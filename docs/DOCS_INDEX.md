# Factor Library Documentation Index

> Last updated: 2026-06-14 (Phase 7G)

---

## Phase 7 Series

| Phase | Document | Description |
|-------|----------|-------------|
| 7A-B | `factor_mining_candidates_v0_1.csv` | 86 candidates, 27 selected_for_7B |
| 7C-B | `phase7c_b_dynamic_eval_summary_*.csv` | Dynamic evaluation of 27 factors |
| 7C-B | `phase7c_b_factor_values_build_summary.csv` | Dynamic factor values build |
| 7D-A | `PHASE_7D_A_STATIC_BUILD.md` | Static build + comparison plan |
| 7D-B | `phase7d_b_static_eval_summary_*.csv` | Static evaluation of 27 factors |
| 7D-B | `phase7d_b_static_vs_dynamic_comparison_*.csv` | Static vs dynamic comparison |
| 7E | `phase7e_factor_diagnostic_classification.csv` | Diagnostic tier classification |
| 7E | `phase7e_family_level_summary.csv` | Family-level classification summary |
| 7E | `PHASE_7E_DIAGNOSTIC_CLASSIFICATION.md` | Phase 7E closeout |
| 7F | `phase7f_static_pairwise_correlation.csv` | 351 pairwise correlations (static) |
| 7F | `phase7f_dynamic_pairwise_correlation.csv` | 351 pairwise correlations (dynamic) |
| 7F | `phase7f_redundancy_groups.csv` | 6 redundancy groups |
| 7F | `phase7f_family_redundancy_summary.csv` | Within-family redundancy |
| 7F | `PHASE_7F_REDUNDANCY_DIAGNOSTICS.md` | Phase 7F closeout |
| 7G | `phase7g_curated_factor_library_v0_2.csv` | **27-factor curated library** |
| 7G | `phase7g_family_curation_summary.csv` | Family curation summary |
| 7G | `phase7g_redundancy_review_queue.csv` | Redundancy review queue |
| 7G | `PHASE_7G_FACTOR_LIBRARY_CURATION.md` | Phase 7G closeout |

## Scripts

| Script | Description |
|--------|-------------|
| `scripts/build_factor_values.py` | Build factor_values parquet |
| `scripts/evaluate_factors.py` | Static evaluation |
| `scripts/evaluate_factors_dynamic_universe.py` | Dynamic evaluation |
| `scripts/analyze_factor_redundancy.py` | Pairwise redundancy analysis |
| `scripts/factor_formula_registry.py` | Factor formula registry (27 factors) |

## Tests

| Test file | Tests |
|-----------|-------|
| `tests/unit/test_crypto_factor_batch7b.py` | 37 |
| `tests/unit/test_factor_mining_candidates.py` | 15 |
| `tests/unit/test_phase7c_dynamic_adapter.py` | 21 |
| `tests/unit/test_phase7d_static_adapter.py` | 14 |
| `tests/unit/test_phase7f_redundancy.py` | 19 |
| `tests/unit/test_phase7g_library_curation.py` | 9 |
