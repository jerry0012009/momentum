# Factor Evaluation Workflow Boundary

**Version:** PM-58 (2026-06-24)
**Purpose:** Define what is core, conditional, and optional in the factor evaluation workflow.

---

## 1. Current Core Workflow Diagram

```
FactorSpec (registry)
    │
    ▼
factor_values (panel CSV)
    │
    ├──► RankIC summary ──► RankIC robust significance (84×4) ──┐
    ├──► LS summary ──────► LS robust significance (84×4) ──────┤
    ├──► diagnostics summary                                      │
    ├──► shape                                                     │
    ├──► rolling stability                                         │
    ├──► decile                                                    │
    ├──► capacity                                                  │
    ├──► regime                                                    │
    ├──► redundancy                                                │
    ├──► scorecard ◄──────────────────────────────────────────────┘
    ├──► profile
    ├──► bilingual card
    ├──► page payload ──► page QA
    └──► active consistency check ──► integrity QA --all-active

[CONDITIONAL]
    cap (market-cap proxy) ──► cap-based factors only
    See: CAP_DATA_SOURCE_CONTRACT.md

[OPTIONAL — candidate-only, not in core workflow]
    paper simulation ──► paper robust
    fee sensitivity ──► fee cost-collapse
```

## 2. Core Full-Universe Required Diagnostics

Every active factor (currently 84) MUST have ALL of the following:

| # | Diagnostic | Output | Full-Universe Gate |
|---|-----------|--------|-------------------|
| 1 | registry / FactorSpec | FactorSpec in registry | consistency |
| 2 | factor_values | factor_values_panel.csv | consistency |
| 3 | RankIC summary | factor_level_rankic_summary.csv/json | consistency |
| 4 | LS summary | factor_level_long_short_summary.csv | consistency |
| 5 | diagnostics summary | factor_diagnostics_summary.csv | consistency |
| 6 | shape | factor_quantile_shape_summary.csv | consistency |
| 7 | rolling stability | factor_rolling_stability_summary.csv | consistency |
| 8 | decile | factor_decile_shape_summary.csv | consistency |
| 9 | capacity | factor_capacity_liquidity_summary.csv | consistency |
| 10 | regime | factor_regime_exposure_summary.csv/json | consistency |
| 11 | redundancy | factor_redundancy_summary.csv/json | consistency |
| 12 | scorecard | factor_quality_scorecard.csv/json | consistency |
| 13 | profile | factor_unified_profile_summary.csv/json | consistency |
| 14 | bilingual card | factor_bilingual_cards.csv | consistency |
| 15 | page payload | factor-evaluation.html | page QA |
| 16 | RankIC robust | factor_rankic_robust_significance_summary.csv (84×4) | integrity QA |
| 17 | LS robust | factor_ls_robust_significance_summary.csv (84×4) | integrity QA |
| 18 | active consistency | active_workflow_consistency_report.json | checker |
| 19 | integrity QA | post_intake_workflow_integrity_report.json | integrity |
| 20 | page QA | factor_evaluation_page_completeness_report.json | page QA |

## 3. Conditional Input Sources

| Source | Condition | Active Factors | Contract |
|--------|-----------|---------------|----------|
| cap (market-cap proxy) | Only for cap-based factors | a101_volume_cap_alpha_min_80_80, a101_volume_cap_alpha_min_56_84 | CAP_DATA_SOURCE_CONTRACT.md |

Cap is NOT a downstream diagnostic. It is a conditional input source.

## 4. Optional Deep-dive Diagnostics

These are candidate-only. Their absence does NOT block factor reading.

| Diagnostic | Coverage | Blocks Reading? | Affects Scorecard? |
|-----------|----------|-----------------|-------------------|
| Paper simulation | 5/84 | NO | NO |
| Paper robust | 5/84 | NO | NO |
| Fee sensitivity | 13/84 | NO | NO |
| Fee cost-collapse | 13/84 | NO | NO |

## 5. Paper Simulation Decision

**Decision: OPTIONAL_CANDIDATE_ONLY**

- Paper simulation is optional candidate-only strategy-style deep dive
- Not part of core factor evaluation workflow
- Paper robust does NOT require 84/84
- Paper robust does NOT affect scorecard or best_horizon
- Paper robust does NOT affect factor reading primary conclusion
- Current 5/84 results are legacy/optional/subset
- Factors without paper: display "Not run — optional", NOT "Missing"

## 6. Fee Sensitivity Decision

**Decision: OPTIONAL_CANDIDATE_ONLY**

- Fee sensitivity is optional candidate-only cost survival deep dive
- Not part of core full-universe workflow
- Fee cost-collapse does NOT require 84/84
- Fee cost-collapse does NOT affect scorecard or best_horizon
- Fee cost-collapse does NOT affect factor reading primary conclusion
- Current 13/84 results are optional/subset
- Factors without fee: display "Not run — optional", NOT "Missing"
- Fee cost-collapse is Sharpe-based cost survival diagnostic, NOT t-stat robust test

## 7. Cap Source Decision

**Decision: KEEP_AS_CONDITIONAL_CORE_SOURCE**

- Cap is a conditional core input source for cap-based factors
- NOT a downstream diagnostic
- NOT required for all factors
- If active factor uses cap, must have cap source contract
- Current status: `CAP_POINT_IN_TIME_APPROXIMATE`
- Cap is size / market-cap proxy
- Cap is NOT liquidity, NOT tradable capacity, NOT open interest
- Cap does NOT enter signal construction
- Cap factors can remain active with source caveat
- See: CAP_DATA_SOURCE_CONTRACT.md

## 8. Closure Definition

A factor's evaluation is **CLOSED** when:
- All 20 core diagnostics are present and PASS
- Active workflow consistency PASS
- All-active integrity QA PASS
- Page QA PASS

A factor's evaluation is **NOT CLOSED** when:
- Any core diagnostic is missing
- Consistency check FAIL
- Integrity QA FAIL
- Page QA FAIL

## 9. Reading Readiness Definition

A factor is **READING READY** when:
- Evaluation is CLOSED (all core diagnostics present)
- Scorecard is computed
- Profile is generated
- Bilingual card is generated
- Page payload is complete

## 10. What Blocks Factor Reading

- Missing factor_values
- Missing RankIC summary
- Missing LS summary
- Missing shape / decile / capacity
- Missing scorecard / profile / bilingual card
- Missing RankIC robust (84×4)
- Missing LS robust (84×4)
- Missing page payload
- Consistency check FAIL
- Integrity QA FAIL
- Page QA FAIL

## 11. What Does NOT Block Factor Reading

- Missing paper simulation (optional)
- Missing paper robust (optional)
- Missing fee sensitivity (optional)
- Missing fee cost-collapse (optional)
- Paper/fee subset limitations (documented, not failures)
- Cap source caveat (documented, not failure)

---

## Decision Summary

```
Paper simulation decision: OPTIONAL_CANDIDATE_ONLY
Fee sensitivity decision:  OPTIONAL_CANDIDATE_ONLY
Cap source decision:       KEEP_AS_CONDITIONAL_CORE_SOURCE
Robust RankIC decision:    KEEP_AS_CORE_SINGLE_FACTOR_EVALUATION
Robust LS decision:        KEEP_AS_CORE_SINGLE_FACTOR_EVALUATION
```
