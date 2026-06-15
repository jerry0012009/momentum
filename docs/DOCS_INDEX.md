# Factor Library Documentation Index

> Last updated: 2026-06-14
>
> Current state: Phase 10A diagnostic signal backtest v0 COMPLETE. 10 CANDIDATE_REVIEW, 32 parked. v0.4 diagnostic library (42 factors, 15 families).

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
| 7H | `PHASE_7H_BATCH2_SELECTION_PLAN.md` | Batch-2 candidate selection plan |
| 7H | `phase7h_batch2_candidate_selection.csv` | 59 candidates scored |
| 7H | `phase7h_operator_gap_analysis.csv` | 11 operator gaps |
| 7H | `phase7h_pm_approved_batch2.csv` | PM-approved 9 factors |
| 7I-A | `PHASE_7I_A_BATCH2_IMPLEMENTATION.md` | Batch-2 implementation closeout |
| 7I-B | `PHASE_7I_B_BATCH2_EVALUATION.md` | Batch-2 evaluation closeout |
| 7I-B | `phase7i_b_static_factor_values_build_summary.csv` | Static build summary (9 factors) |
| 7I-B | `phase7i_b_dynamic_factor_values_build_summary.csv` | Dynamic build summary (9 factors) |
| 7I-B | `phase7i_b_static_eval_summary_ret_fwd_1h.csv` | Static ret_fwd_1h (9 factors) |
| 7I-B | `phase7i_b_static_eval_summary_all_labels.csv` | Static all labels (36 rows) |
| 7I-B | `phase7i_b_dynamic_eval_summary_ret_fwd_1h.csv` | Dynamic ret_fwd_1h (9 factors) |
| 7I-B | `phase7i_b_dynamic_eval_summary_all_labels.csv` | Dynamic all labels (36 rows) |
| 7I-C | `PHASE_7I_C_DIAGNOSTIC_CLASSIFICATION.md` | Batch-2 classification closeout |
| 7I-C | `phase7i_c_static_vs_dynamic_comparison_ret_fwd_1h.csv` | Static-vs-dynamic comparison (9 rows) |
| 7I-C | `phase7i_c_static_vs_dynamic_comparison_all_labels.csv` | Static-vs-dynamic comparison (36 rows) |
| 7I-C | `phase7i_c_factor_diagnostic_classification.csv` | 9-factor diagnostic classification |
| 7I-C | `phase7i_c_family_diagnostic_summary.csv` | Family diagnostic summary |
| 7I-D | `PHASE_7I_D_REDUNDANCY_DIAGNOSTICS.md` | Batch-2 redundancy closeout |
| 7I-D | `phase7i_d_static_pairwise_correlation.csv` | 36 static pairwise correlations |
| 7I-D | `phase7i_d_dynamic_pairwise_correlation.csv` | 36 dynamic pairwise correlations |
| 7I-D | `phase7i_d_redundancy_groups.csv` | 2 redundancy groups |
| 7I-D | `phase7i_d_family_redundancy_summary.csv` | Family redundancy summary |
| 7I-E | `PHASE_7I_E_CURATED_LIBRARY_UPDATE.md` | Curated library v0.3 update closeout |
| 7I-E | `phase7i_e_curated_batch2_library.csv` | 9-factor Batch-2 curated library |
| 7I-E | `phase7i_e_curated_factor_library_v0_3.csv` | Combined 36-factor curated library v0.3 |
| 7I-E | `phase7i_e_family_catalog_summary_v0_3.csv` | Family catalog summary v0.3 |
| 7I-E | `phase7i_e_redundancy_review_queue_v0_3.csv` | Combined redundancy review queue |
| 7J | `PHASE_7J_BATCH3_PLANNING.md` | Batch-3 planning and data readiness closeout |
| 7J | `phase7j_family_gap_analysis.csv` | Family gap analysis (20 families) |
| 7J | `phase7j_crypto_native_data_readiness.csv` | Crypto-native data readiness audit (11 types) |
| 7J | `phase7j_batch3_candidate_plan.csv` | Batch-3 candidate plan (14 candidates) |
| 7K | `PHASE_7K_DATA_CONTRACT_SCHEMA_VERIFICATION.md` | Data contract & schema verification closeout |
| 7K | `phase7k_bars_schema_audit.csv` | bars_1h.parquet schema audit (static + dynamic) |
| 7K | `phase7k_taker_field_readiness.csv` | Taker field readiness (3 candidates x 2 datasets) |
| 7K | `phase7k_funding_rate_schema_audit.csv` | Funding rate schema audit (2 data sources) |
| 7K | `phase7k_crypto_native_data_contract.md` | Crypto-native data contract (中文) |
| 7L | `PHASE_7L_CANONICAL_DATA_CACHE_CONSTRUCTION.md` | Canonical data cache construction closeout |
| 7L | `phase7l_taker_enriched_bars_summary.csv` | Taker enriched bars summary (static + dynamic) |
| 7L | `phase7l_funding_events_summary.csv` | Funding events summary (679 symbols) |
| 7L | `phase7l_funding_alignment_summary.csv` | Funding 1h alignment summary (static + dynamic) |
| 7L-R | `PHASE_7L_R_CACHE_REPRODUCIBILITY.md` | Cache reproducibility closeout |
| 7L-R | `phase7l_r_crypto_native_cache_manifest.csv` | Cache manifest (5 artifacts, checksums) |
| 7L-R2 | `PHASE_7L_R_CACHE_REPRODUCIBILITY.md` | Updated closeout (CLI wiring + manifest fixes) |
| 7M-A | `PHASE_7M_A_CRYPTO_NATIVE_IMPLEMENTATION.md` | 6 crypto-native diagnostic factors closeout |
| 7M-B | `PHASE_7M_B_CRYPTO_NATIVE_FACTOR_VALUES.md` | Factor values build closeout |
| 7M-B | `phase7m_b_crypto_native_dataset_join_summary.csv` | Dataset join summary (static + dynamic) |
| 7M-B | `phase7m_b_static_factor_values_build_summary.csv` | Static factor_values build summary (6 rows) |
| 7M-B | `phase7m_b_dynamic_factor_values_build_summary.csv` | Dynamic factor_values build summary (6 rows) |
| 7M-C | `PHASE_7M_C_CRYPTO_NATIVE_EVALUATION.md` | Evaluation closeout |
| 7M-C | `phase7m_crypto_native_factor_metadata.csv` | Factor metadata (6 rows, direction) |
| 7M-C | `phase7m_c_static_eval_summary_ret_fwd_1h.csv` | Static eval ret_fwd_1h (6 rows) |
| 7M-C | `phase7m_c_static_eval_summary_all_labels.csv` | Static eval all labels (24 rows) |
| 7M-C | `phase7m_c_dynamic_eval_summary_ret_fwd_1h.csv` | Dynamic eval ret_fwd_1h (6 rows) |
| 7M-C | `phase7m_c_dynamic_eval_summary_all_labels.csv` | Dynamic eval all labels (24 rows) |
| 7M-D | `PHASE_7M_D_CRYPTO_NATIVE_CLASSIFICATION.md` | Classification closeout |
| 7M-D | `phase7m_d_static_vs_dynamic_comparison_ret_fwd_1h.csv` | Static vs dynamic comparison (6 rows) |
| 7M-D | `phase7m_d_static_vs_dynamic_comparison_all_labels.csv` | Static vs dynamic comparison (24 rows) |
| 7M-D | `phase7m_d_factor_diagnostic_classification.csv` | Diagnostic classification (6 rows) |
| 7M-D | `phase7m_d_family_diagnostic_summary.csv` | Family diagnostic summary (2 rows) |
| 7M-D | `phase7m_d_review_flags.csv` | Review flags |
| 7M-D-R | `PHASE_7M_D_R_CLASSIFICATION_REPAIR.md` | Classification repair closeout |
| 7M-E | `PHASE_7M_E_CRYPTO_NATIVE_REDUNDANCY.md` | Redundancy diagnostics closeout |
| 7M-E | `phase7m_e_static_pairwise_correlation.csv` | Static pairwise Spearman (15 pairs) |
| 7M-E | `phase7m_e_dynamic_pairwise_correlation.csv` | Dynamic pairwise Spearman (15 pairs) |
| 7M-E | `phase7m_e_redundancy_groups.csv` | Redundancy groups (none found) |
| 7M-E | `phase7m_e_family_redundancy_summary.csv` | Family redundancy summary |
| 7M-F | `PHASE_7M_F_CRYPTO_NATIVE_CURATION.md` | Curation closeout |
| 7M-F | `phase7m_f_curated_crypto_native_library.csv` | Crypto-native curated (6 rows) |
| 7M-F | `phase7m_f_curated_factor_library_v0_4.csv` | Combined v0.4 library (42 rows) |
| 7M-F | `phase7m_f_family_catalog_summary_v0_4.csv` | Family catalog v0.4 (15 rows) |
| 7M-F | `phase7m_f_redundancy_review_queue_v0_4.csv` | Redundancy queue v0.4 (10 rows) |
| 7N | `PHASE_7N_V04_LIBRARY_AUDIT_AND_PHASE8_READINESS.md` | Audit & readiness closeout |
| 7N | `phase7n_v04_library_audit_summary.csv` | Library audit (42 rows) |
| 7N | `phase7n_family_readiness_summary.csv` | Family readiness (15 rows) |
| 7N | `phase7n_phase8_review_queue.csv` | Phase 8 review queue (42 rows) |
| 7N | `phase7n_blockers_and_constraints.csv` | Blockers (7 items) |
| 7N-R | `PHASE_7N_R_READINESS_QUEUE_REPAIR.md` | Queue repair closeout |
| 7N-R | `phase7n_r_phase8_review_queue_repaired.csv` | Repaired Phase 8 review queue (42 rows) |
| 7N-R2 | `PHASE_7N_R2_READINESS_QUEUE_REPAIR.md` | Queue precedence repair closeout |
| 7N-R2 | `phase7n_r2_phase8_review_queue_repaired.csv` | Repaired queue (42 rows) |
| 7N-R2 | `phase7n_r2_queue_category_summary.csv` | Category summary (canonical counts) |
| 7N-R2 | `tests/unit/test_phase7n_r2_queue_precedence.py` | Queue precedence repair tests |
| 8A | `PHASE_8A_CANDIDATE_REVIEW_PACKET.md` | Phase 8A human review packet closeout |
| 8A | `phase8a_human_review_packet.csv` | 42-factor human review packet |
| 8A | `phase8a_ready_for_human_review_shortlist.csv` | 10-factor ready shortlist |
| 8A | `phase8a_review_protocol.md` | Human review protocol |
| 8A | `phase8a_review_decision_template.csv` | Human decision template |
| 8B | `PHASE_8B_PM_CANDIDATE_DECISIONS.md` | Phase 8B PM candidate decision closeout |
| 8B | `phase8b_candidate_review_decisions.csv` | 42-row PM decision file |
| 8B | `phase8b_candidate_review_shortlist.csv` | 10-factor approved shortlist |
| 8B | `phase8b_factor_library_v0_5_status.csv` | v0.5 status metadata (42 rows) |
| 8B | `phase8b_non_candidate_review_queue.csv` | 32 non-candidate factors |
| 8B | `tests/unit/test_phase8b_candidate_decisions.py` | Phase 8B decision validation tests |
| 9A-R | `PHASE_9A_R_PM_SIGNAL_ARCHITECTURE.md` | Phase 9A-R PM signal architecture specification closeout |
| 9A-R | `phase9a_r_factor_role_map.csv` | 10-factor role assignment (4 channels) |
| 9A-R | `phase9a_r_signal_component_spec.csv` | 4 signal component definitions |
| 9A-R | `phase9a_r_signal_basket_plan.csv` | 5 basket designs (DESIGN_ONLY) |
| 9A-R | `phase9a_r_weighting_policy.csv` | PM-specified structural weighting policies |
| 9A-R | `phase9a_r_transformation_rules.csv` | 7 transformation rules |
| 9A-R | `phase9a_r_pre_implementation_checklist.csv` | 13 pre-implementation checks |
| 9A-R | `tests/unit/test_phase9a_r_pm_signal_architecture.py` | Phase 9A-R architecture validation tests |
| 9A-R2 | `PHASE_9A_R2_PM_ARCHITECTURE_CONSISTENCY.md` | Phase 9A-R2 architecture consistency closeout |
| 9A-R2 | `phase9a_r2_signal_basket_plan.csv` | Updated 6-basket plan (basket_6 = PM-preferred) |
| 9A-R2 | `phase9a_r2_weighting_policy.csv` | Updated 6-policy weighting (pm_full_structured added) |
| 9A-R2 | `phase9a_r2_transformation_rules.csv` | Updated 9 transformation rules |
| 9A-R2 | `tests/unit/test_phase9a_r2_architecture_consistency.py` | Phase 9A-R2 consistency tests |
| 9B | `PHASE_9B_DETERMINISTIC_SIGNAL_PANEL.md` | Phase 9B signal panel closeout |
| 9B | `scripts/build_phase9b_signal_panel.py` | Reproducible signal panel builder |
| 9B | `phase9b_signal_panel_manifest.csv` | 3-signal manifest |
| 9B | `phase9b_signal_component_manifest.csv` | 6-component manifest |
| 9B | `phase9b_signal_coverage_summary.csv` | Coverage and statistics |
| 9B | `phase9b_signal_quality_checks.csv` | 11 quality checks |
| 9B | `phase9b_signal_panel.parquet` | 3.3M-row signal panel (generated locally, gitignored; regenerate with `scripts/build_phase9b_signal_panel.py`) |
| 9B | `tests/unit/test_phase9b_signal_panel.py` | Phase 9B signal panel tests |
| 10A | `PHASE_10A_SIGNAL_BACKTEST_V0.md` | Phase 10A diagnostic backtest closeout |
| 10A | `scripts/run_phase10a_signal_backtest.py` | Reproducible backtest runner |
| 10A | `phase10a_signal_rankic_summary.csv` | 3 signals × 4 horizons RankIC |
| 10A | `phase10a_signal_quantile_spread_summary.csv` | 3 signals × 4 horizons quantile spread |
| 10A | `phase10a_signal_backtest_timeseries.parquet` | Generated locally, gitignored |
| 10A | `phase10a_signal_backtest_quality_checks.csv` | 12 quality checks |
| 10A | `phase10a_label_alignment_audit.csv` | 10 label alignment checks |
| 12A | `tests/unit/test_phase12a_paper_signal_harness.py` | Phase 12A tests |
| 12B | `PHASE_12B_PAPER_MONITORING_DIAGNOSTIC.md` | Phase 12B closeout — rolling monitoring |
| 12B | `phase12b_paper_signal_log.csv` | 31,003 row rolling paper signal log |
| 12B | `phase12b_signal_stability_summary.csv` | Per-timestamp stability metrics |
| 12B | `phase12b_turnover_monitoring.csv` | Per-timestamp turnover |
| 12B | `phase12b_exposure_monitoring.csv` | Per-timestamp exposure |
| 12B | `phase12b_liquidity_monitoring.csv` | Per-timestamp liquidity |
| 12B | `phase12b_data_freshness_monitoring.csv` | Data freshness summary |
| 12B | `phase12b_realized_paper_return_tracking.csv` | Per-timestamp realized returns |
| 12B | `phase12b_realized_return_summary.csv` | Return summary |
| 12B | `phase12b_monitoring_alerts.csv` | Monitoring alerts |
| 12B | `phase12b_quality_checks.csv` | 15 quality checks |
| 12B | `tests/unit/test_phase12b_paper_monitoring.py` | Phase 12B tests |
| 12C | `PHASE_12C_GRAND_TRANSPARENCY_CLOSEOUT.md` | Phase 12C grand transparency closeout |
| 12C | `phase12c_transparency_quality_checks.csv` | 17 quality checks |
| 12C | `tests/unit/test_phase12c_transparency_closeout.py` | Phase 12C tests |
| 12C | `docs/factor_library_transparency/` | Full transparency documentation (8 docs + index) |
| 10A-R | `PHASE_10A_R_DIRECTION_QUANTILE_REPAIR.md` | Phase 10A-R direction/quantile repair closeout |
| 10A-R | `scripts/run_phase10a_r_diagnostics.py` | Phase 10A-R diagnostic runner |
| 10A-R | `phase10a_r_direction_consistency_check.csv` | 3×4 direction consistency check |
| 10A-R | `phase10a_r_quantile_bucket_returns.csv` | 5/10-bucket monotonicity check |
| 10A-R | `phase10a_r_inverted_signal_diagnostic.csv` | Inverted signal diagnostic |
| 10A-R | `phase10a_r_rankic_quantile_reconciliation.csv` | RankIC-quantile reconciliation |
| 10A-R | `phase10a_r_quality_checks.csv` | 13 quality checks |
| 10A-R | `tests/unit/test_phase10a_r_direction_quantile_repair.py` | Phase 10A-R tests |
| 10B | `PHASE_10B_TAIL_ADDENDUM_CLOSEOUT.md` | Phase 10B-lite tail diagnostics closeout |
| 10B | `scripts/run_phase10b_tail_diagnostics.py` | Phase 10B-lite diagnostic runner |
| 10B | `phase10b_bucket0_top_contributors.csv` | Bucket 0 top 50 contributors per signal×horizon |
| 10B | `phase10b_robust_spread_addendum.csv` | Robust spread diagnostics (median, winsorized, tail-trim) |
| 10B | `phase10b_pm_decision_matrix.csv` | PM decision matrix |
| 10B | `phase10b_quality_checks.csv` | 9 quality checks |
| 10B | `tests/unit/test_phase10b_tail_addendum.py` | Phase 10B-lite tests |
| 10C | `PHASE_10C_TAIL_AWARE_SIGNAL_POLICY_DESIGN.md` | Phase 10C closeout — tail-aware signal policy design |
| 10C | `phase10c_tail_policy_options.csv` | 6 tail-aware policy options |
| 10C | `phase10c_horizon_direction_policy.csv` | 12-row horizon-specific direction policy |
| 10C | `phase10c_signal_v1_design_spec.md` | Signal v1 design spec (design-only) |
| 10C | `phase10c_phase10d_evaluation_protocol.csv` | Phase 10D evaluation protocol (20 items) |
| 10C | `phase10c_quality_checks.csv` | 11 quality checks |
| 10C | `tests/unit/test_phase10c_tail_policy_design.py` | Phase 10C tests |
| 10C-R | `PHASE_10C_R_METRIC_LINEAGE_AND_POLICY_REPAIR.md` | Phase 10C-R closeout — metric lineage and direction policy repair |
| 10C-R | `phase10c_r_metric_lineage.csv` | Full metric lineage map with source files and phases |
| 10C-R | `phase10c_r_horizon_direction_policy_repaired.csv` | Repaired 12-row horizon direction policy |
| 10C-R | `phase10c_r_phase10d_protocol_repaired.csv` | Repaired Phase 10D protocol with 48 variant evaluations |
| 10C-R | `phase10c_r_quality_checks.csv` | 12 quality checks |
| 10C-R | `tests/unit/test_phase10c_r_metric_lineage_policy.py` | Phase 10C-R tests |


---

## Scripts

| Script | Description |
|--------|-------------|
| `scripts/factor_formula_registry.py` | Factor formula registry; includes 38 factors (27 Batch-1 + 9 Batch-2) |
| `scripts/factor_ops.py` | Reusable factor operators |
| `scripts/build_factor_values.py` | Build factor_values parquet |
| `scripts/evaluate_factors.py` | Static factor evaluation |
| `scripts/evaluate_factors_dynamic_universe.py` | Dynamic-universe factor evaluation |
| `scripts/analyze_factor_redundancy.py` | Pairwise redundancy analysis |
| `scripts/phase7h_selection.py` | Phase 7H candidate scoring and operator gap analysis |

---

## Tests

| Test file | Purpose |
|-----------|---------|
| `tests/unit/test_factor_mining_candidates.py` | Candidate backlog validation |
| `tests/unit/test_crypto_factor_batch7b.py` | Phase 7B factor implementation tests |
| `tests/unit/test_crypto_factor_batch7i.py` | Phase 7I-A Batch-2 implementation tests |
| `tests/unit/test_phase7c_dynamic_adapter.py` | Dynamic evaluator adapter tests |
| `tests/unit/test_phase7d_static_adapter.py` | Static evaluator adapter tests |
| `tests/unit/test_phase7f_redundancy.py` | Redundancy analysis tests |
| `tests/unit/test_phase7g_library_curation.py` | Curated library v0.2 validation |
| `tests/unit/test_phase7h_batch2_selection.py` | Phase 7H selection validation |
| `tests/unit/test_phase7i_curated_library.py` | Curated library v0.3 validation |
| `tests/unit/test_phase7n_r2_queue_precedence.py` | 7N-R2 queue precedence repair tests |
| `tests/unit/test_phase8a_candidate_review_packet.py` | Phase 8A review packet validation |
| `tests/unit/test_phase8b_candidate_decisions.py` | Phase 8B PM decision validation |

---

## Standing Constraints

- No alpha promotion without explicit PM/human approval.
- No factor removal based only on diagnostic classification or redundancy.
- No strategy backtest before Phase 10.
- Dynamic universe is diagnostic and still not true PIT.
