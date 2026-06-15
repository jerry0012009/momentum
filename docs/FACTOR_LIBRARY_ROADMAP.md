# Factor Library Roadmap

> Last updated: 2026-06-14
>
> Project: crypto perpetual cross-sectional factor research system / factor library.

---

## 0. Project Goal

This repository is not a single-strategy backtest project. It is a research system for building, evaluating, classifying, and curating a crypto perpetual cross-sectional factor library.

Core rule: **all newly implemented factors remain diagnostic until explicit human approval. No automatic alpha promotion.**

---

## 1. Current Status

| Item | Current State |
|------|---------------|
| Macro phase | Phase 7 — Large-scale Factor Mining |
| Current subphase | Phase 7N COMPLETE |
| Next subphase | PM/human decision on Phase 8 Candidate Factor Review |
| Curated library version | v0.4 |
| Curated factors | 42 (36 v0.3 + 6 crypto-native) |
| Families | 15 (13 existing + taker_imbalance + funding_rate) |
| Diagnostic tiers | T1: 11, T2: 17, T3: 6, T4: 8 |
| Redundancy groups | 8 (6 Batch-1 + 2 Batch-2) + 2 medium crypto-native review |
| Alpha promotion | None |
| Strategy backtest | Not started |
| Live / paper trading | Not started |

---

## 2. Macro Phase Roadmap

| Phase | Name | Status | Notes |
|-------|------|--------|-------|
| Phase 0 | Project Positioning & Data Contract | COMPLETE | Defined crypto perp cross-sectional factor-library scope |
| Phase 1 | V0 Engineering Loop | COMPLETE | Fetch → labels → factors → evaluation loop |
| Phase 2 | Evaluation Protocol & Factor Library Skeleton | COMPLETE | V0 audit, quality gates, factor catalog |
| Phase 3 | Long-window Baseline | COMPLETE | 11 simple probes, pipeline validation |
| Phase 4 | Factor Factory & Evaluation Platform v1 | COMPLETE | Registry-driven factor factory |
| Phase 5 | Alphalens-compatible Export | COMPLETE | Compatibility layer |
| Phase 6 | Dynamic Universe & Survivorship Control | COMPLETE | Dynamic-universe diagnostics |
| Phase 7 | Large-scale Factor Mining | IN PROGRESS | Batch-1+2 complete through 7I-E |
| Phase 8 | Candidate Factor Review | NOT STARTED | Requires explicit human review |
| Phase 9 | Multi-factor Signal Construction | NOT STARTED | Only CANDIDATE_REVIEW factors |
| Phase 10 | Strategy Backtest | NOT STARTED | |
| Phase 11 | Cost / Slippage / Capacity / Risk | NOT STARTED | |
| Phase 12 | Paper Trading | NOT STARTED | |
| Phase 13 | Small-capital Live Validation | NOT STARTED | |

---

## 3. Phase 7 Subphase Status

| Subphase | Name | Status | Main Output |
|----------|------|--------|-------------|
| 7A | Protocol & Candidate Backlog | COMPLETE | 86 candidate factors, 27 selected_for_7B |
| 7B | First Implementation Batch | COMPLETE | 27 OHLCV-derived diagnostic factors |
| 7C-A | Dynamic Adapter Hardening | COMPLETE | Candidate-mode fail-fast |
| 7C-B | Dynamic Factor Build & Evaluation | COMPLETE | Dynamic factor_values and evaluation |
| 7D-A | Static Adapter Hardening | COMPLETE | Static evaluator subset/candidate mode |
| 7D-B | Static Evaluation & Static-vs-Dynamic | COMPLETE | Static summaries and comparison |
| 7E | Diagnostic Classification | COMPLETE | TIER_1/TIER_2/TIER_3/TIER_4 |
| 7F | Redundancy Diagnostics | COMPLETE | 351+351 pairwise correlations, 6 groups |
| 7G | Factor Library Curation | COMPLETE | Curated factor library v0.2 |
| 7H | Batch-2 Factor Mining Preparation | COMPLETE | 9 PM-approved factors selected |
| 7I-A | Batch-2 Implementation | COMPLETE | 9 factors implemented |
| 7I-B | Batch-2 Evaluation | COMPLETE | Static+dynamic eval, 9 factors |
| 7I-C | Batch-2 Diagnostic Classification | COMPLETE | Tier assignment, direction alignment |
| 7I-D | Batch-2 Redundancy Diagnostics | COMPLETE | 2 redundancy groups found |
| 7I-E | Batch-2 Curated Library Update | COMPLETE | Curated factor library v0.3 (36 factors) |
| 7J | Batch-3 Planning & Data Readiness | COMPLETE | Data readiness audit, 14 candidates planned |
| 7K | Data Contract & Schema Verification | COMPLETE | taker READY_WITH_QUOTE_VARIANT, funding READY_FOR_CONTRACT |
| 7L | Canonical Data Cache Construction | COMPLETE | taker enriched bars + funding events + 1h aligned |
| 7L-R | Cache Reproducibility Hardening | COMPLETE | reproducible script + manifest + 13 tests |
| 7L-R2 | Cache Reproducibility Fixes | COMPLETE | CLI wiring + manifest semantics + 20 tests |
| 7M-A | Limited Crypto-native Factor Implementation | COMPLETE | 6 diagnostic factors (taker 3 + funding 3), 19 tests |
| 7M-B | Crypto-native Factor Values Build | COMPLETE | static+dynamic factor_values, 12 factor_values, 37 tests |
| 7M-C | Crypto-native Static/Dynamic Evaluation | COMPLETE | 6 factors × 4 labels × 2 datasets, 21 tests |
| 7M-D | Crypto-native Comparison & Classification | COMPLETE | static-vs-dynamic + diagnostic tiers, 20 tests |
| 7M-D-R | Crypto-native Classification Repair | COMPLETE | fixed all-label merge on (factor_id,label), 24 tests |
| 7M-E | Crypto-native Redundancy Diagnostics | COMPLETE | pairwise correlation, no redundancy found, 13 tests |
| 7M-F | Crypto-native Curated Library Update | COMPLETE | v0.4 = 42 factors, 15 families, 16 tests |
| 7N | v0.4 Library Audit & Phase 8 Readiness | COMPLETE | audit, review queue, 7 blockers, 18 tests |
| 7N-R | Readiness Queue & Documentation Repair | COMPLETE | repaired queue semantics, doc state fix, 21 tests |

---

## 4. Curated Library v0.4 Summary

### 4.1 Recommended research use (combined)

| recommended_research_use | v0.3 (OHLCV) | v0.4 (crypto-native) | Total |
|--------------------------|--------------|----------------------|-------|
| CORE_DIAGNOSTIC_CANDIDATE | 10 | 0 | 10 |
| REVIEW_DIRECTION_OR_FORMULA | 19 | 3 | 22 |
| MONITOR_TURNOVER_RISK | 2 | 0 | 2 |
| WEAK_DIAGNOSTIC_ONLY | 1 | 2 | 3 |
| LOW_PRIORITY_RESEARCH | 2 | 1 | 3 |
| REDUNDANCY_REVIEW | 2 | 0 | 2 |

### 4.2 New crypto-native families in v0.4

- `taker_imbalance` (3 factors): taker_buy_ratio_20h, taker_buy_zscore_20h, taker_buy_delta_5h
- `funding_rate` (3 factors): funding_rate_level_20h, funding_rate_zscore_80h, funding_rate_change_24h

### 4.3 Crypto-native diagnostic tiers

- TIER_2: taker_buy_ratio_20h, taker_buy_zscore_20h
- TIER_3: taker_buy_delta_5h, funding_rate_level_20h, funding_rate_zscore_80h
- TIER_4: funding_rate_change_24h

---

## 5. Key Constraints Carried Forward

- Calendar-time joins only.
- No `shift(-h)` feature leakage.
- No row-based forward return construction.
- expected_direction must come from theory/candidate metadata, never reverse-engineered.
- All new factors start as diagnostic probes.
- No alpha promotion without explicit PM/human approval.
- No factor removal based only on diagnostic classification or redundancy.
- No strategy backtest before Phase 10.
- Dynamic universe diagnostics available but not true PIT.

---

## 6. Next Phase: PM/human decision on Phase 8 Candidate Factor Review

Phase 7M-A through 7N are complete:
- **7M-A**: 6 crypto-native diagnostic factors implemented (taker 3 + funding 3)
- **7M-B**: Factor values built for static + dynamic datasets
- **7M-C**: Static/dynamic evaluation across 4 labels
- **7M-D**: Static-vs-dynamic comparison and diagnostic classification
- **7M-D-R**: Repaired all-label merge bug, classification accepted
- **7M-E**: Redundancy diagnostics — no pairs at abs(corr) >= 0.80
- **7M-F**: Curated library v0.4 (42 factors, 15 families)
- **7N**: v0.4 library audit & Phase 8 readiness package
- **7N-R**: Repaired review queue semantics & documentation state

Phase 8 is not started:
- No factor has entered CANDIDATE_REVIEW
- No factor has been promoted
- No backtest has been run
- v0.4 remains a diagnostic factor library
- PM/human decision required to begin Phase 8

---

## 7. Phase Transition Rule

A later phase may start only after:

1. the previous phase closeout is committed;
2. machine-readable artifacts exist where required;
3. PM review passes;
4. no BLOCK / NEEDS FIX remains;
5. no unauthorized alpha/status/backtest step was introduced.
