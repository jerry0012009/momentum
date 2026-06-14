# Factor Library Documentation Index

> Last updated: 2026-06-14
>
> Current state: Phase 7G complete; Phase 7H pending PM review.

---

## Canonical Roadmap

| Document | Description |
|----------|-------------|
| `docs/FACTOR_LIBRARY_ROADMAP.md` | Canonical macro roadmap and current Phase 7 status |
| `docs/PHASE_7_BATCHING_DESIGN.md` | Phase 7 batch pipeline and 7B first-batch design |

---

## Phase 7 Series

| Phase | Document / Artifact | Description |
|-------|---------------------|-------------|
| 7A | `PHASE_7A_FACTOR_MINING_PROTOCOL.md` | Phase 7 mining protocol |
| 7A | `factor_mining_candidates_v0_1.csv` | 86 candidates, 27 selected_for_7B |
| 7B | `PHASE_7B_IMPLEMENTATION.md` | 27 first-batch factors implemented |
| 7C-A | `PHASE_7C_A_DYNAMIC_ADAPTER_HARDENING.md` | Dynamic evaluator hardening |
| 7C-B | `PHASE_7C_B_DYNAMIC_FACTOR_EVALUATION.md` | Dynamic build/evaluation closeout |
| 7C-B | `phase7c_b_factor_values_build_summary.csv` | Dynamic factor_values build summary |
| 7C-B | `phase7c_b_dynamic_eval_summary_ret_fwd_1h.csv` | Dynamic ret_fwd_1h evaluation summary |
| 7C-B | `phase7c_b_dynamic_eval_summary_all_labels.csv` | Dynamic all-label evaluation summary |
| 7D-A | `PHASE_7D_A_STATIC_ADAPTER_HARDENING.md` | Static evaluator hardening |
| 7D-B | `PHASE_7D_B_STATIC_DYNAMIC_VALIDATION.md` | Static evaluation and static-vs-dynamic closeout |
| 7D-B | `phase7d_b_static_factor_values_build_summary.csv` | Static factor_values build summary |
| 7D-B | `phase7d_b_static_eval_summary_ret_fwd_1h.csv` | Static ret_fwd_1h evaluation summary |
| 7D-B | `phase7d_b_static_eval_summary_all_labels.csv` | Static all-label evaluation summary |
| 7D-B | `phase7d_b_static_vs_dynamic_comparison_ret_fwd_1h.csv` | Static-vs-dynamic comparison, ret_fwd_1h |
| 7D-B | `phase7d_b_static_vs_dynamic_comparison_all_labels.csv` | Static-vs-dynamic comparison, all labels |
| 7E | `PHASE_7E_DIAGNOSTIC_CLASSIFICATION.md` | Diagnostic tier classification closeout |
| 7E | `phase7e_factor_diagnostic_classification.csv` | 27-factor diagnostic classification |
| 7E | `phase7e_family_level_summary.csv` | Family-level diagnostic classification summary |
| 7E | `phase7e_review_flags.csv` | Review flags for direction/turnover/weak/sign-flip issues |
| 7F | `PHASE_7F_REDUNDANCY_DIAGNOSTICS.md` | Redundancy diagnostics closeout |
| 7F | `phase7f_static_pairwise_correlation.csv` | 351 static pairwise correlations |
| 7F | `phase7f_dynamic_pairwise_correlation.csv` | 351 dynamic pairwise correlations |
| 7F | `phase7f_redundancy_groups.csv` | 6 redundancy groups |
| 7F | `phase7f_family_redundancy_summary.csv` | Same-family redundancy summary |
| 7G | `PHASE_7G_FACTOR_LIBRARY_CURATION.md` | Curated library closeout |
| 7G | `phase7g_curated_factor_library_v0_2.csv` | 27-factor curated library v0.2 |
| 7G | `phase7g_family_curation_summary.csv` | Family curation summary |
| 7G | `phase7g_redundancy_review_queue.csv` | Redundancy review queue |

---

## Scripts

| Script | Description |
|--------|-------------|
| `scripts/factor_formula_registry.py` | Factor formula registry; includes 27 Phase 7B factors |
| `scripts/factor_ops.py` | Reusable factor operators |
| `scripts/build_factor_values.py` | Build factor_values parquet, including candidate/status subset mode |
| `scripts/evaluate_factors.py` | Static factor evaluation |
| `scripts/evaluate_factors_dynamic_universe.py` | Dynamic-universe factor evaluation |
| `scripts/analyze_factor_redundancy.py` | Pairwise redundancy and Phase 7F aggregate outputs |

---

## Tests

| Test file | Purpose |
|-----------|---------|
| `tests/unit/test_factor_mining_candidates.py` | Candidate backlog validation |
| `tests/unit/test_crypto_factor_batch7b.py` | Phase 7B factor implementation tests |
| `tests/unit/test_phase7c_dynamic_adapter.py` | Dynamic evaluator adapter tests |
| `tests/unit/test_phase7d_static_adapter.py` | Static evaluator adapter tests |
| `tests/unit/test_phase7f_redundancy.py` | Redundancy analysis tests |
| `tests/unit/test_phase7g_library_curation.py` | Curated library validation tests |

---

## Standing Constraints

- No alpha promotion without explicit PM/human approval.
- No factor removal based only on diagnostic classification or redundancy.
- No strategy backtest before Phase 10.
- Dynamic universe is diagnostic and still not true PIT.
