# Factor Library Transparency Documentation

This directory contains the full transparency and audit documentation for the crypto cross-sectional momentum factor library project (Phase 7–12B).

## Contents

| Document | Description |
|----------|-------------|
| [Data Lineage](data_lineage.md) | Raw data → factor values → signal panel → evaluation pipeline |
| [Workflow Map](workflow_map.md) | Phase-by-phase workflow with Mermaid diagrams |
| [Factor Handbook](factor_handbook.md) | 10 candidate factors: definition, intuition, direction, role |
| [Signal Construction](signal_construction_handbook.md) | 3 signals, why core_only survived, why others failed |
| [Evaluation Methodology](evaluation_methodology.md) | RankIC, quantile spread, cost models, capacity, monitoring |
| [Phase Summary Table](phase_summary_table.csv) | Phase 7–12B audit table |
| [Phase Decision Log](phase_decision_log.md) | Detailed decision rationale per phase |
| [Risk Register](risk_register.csv) | Identified risks with severity, likelihood, mitigation |
| [PM Decision Memo](pm_decision_memo_phase13_readiness.md) | Phase 13 readiness assessment and recommendation |
| [Phase 13 Readiness Checklist](phase13_readiness_checklist.csv) | Checklist for Phase 13 approval |
| [Index Page](index.html) | Static HTML index linking all documents |

## Key Result

One candidate survives: `signal_v0_core_only__1h__original_no_guard`

- Gross spread: +0.051%/hour mean
- Mid-cost net (15bps, turnover-adjusted): +0.209 cumulative over 30 days
- Status: PAPER_SIGNAL_DIAGNOSTIC_ONLY
- Phase 13 NOT STARTED

## Negative Declarations

- No real execution has occurred
- No alpha claim is made
- No production model exists
- Phase 13 NOT STARTED
