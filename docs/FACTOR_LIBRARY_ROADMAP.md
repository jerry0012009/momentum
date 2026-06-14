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
| Current subphase | Phase 7G COMPLETE |
| Next subphase | Phase 7H — Batch-2 Factor Mining Preparation |
| Curated library version | v0.2 |
| Curated factors | 27 selected_for_7B factors |
| Families | 11 |
| Diagnostic tiers | T1: 7, T2: 12, T3: 3, T4: 5 |
| Redundancy groups | 6 |
| Core diagnostic candidates | 6 |
| Alpha promotion | None |
| Strategy backtest | Not started |
| Live / paper trading | Not started |

---

## 2. Macro Phase Roadmap

| Phase | Name | Status | Notes |
|-------|------|--------|-------|
| Phase 0 | Project Positioning & Data Contract | COMPLETE | Defined crypto perp cross-sectional factor-library scope, not single strategy |
| Phase 1 | V0 Engineering Loop | COMPLETE | Fetch → labels → factors → evaluation loop |
| Phase 2 | Evaluation Protocol & Factor Library Skeleton | COMPLETE | V0 audit, quality gates, factor catalog, external priors, Batch 1 baseline |
| Phase 3 | Long-window Baseline | COMPLETE | 11 simple probes showed no stable long-window signal; used for pipeline validation |
| Phase 4 | Factor Factory & Evaluation Platform v1 | COMPLETE | Registry-driven factor factory and unified factor_values schema |
| Phase 5 | Alphalens-compatible Export / External Tool Compatibility | COMPLETE | Compatibility layer, not migration |
| Phase 6 | Dynamic Universe & Survivorship Control | COMPLETE | Dynamic-universe diagnostics available; current dynamic universe is still not true PIT |
| Phase 7 | Large-scale Factor Mining | IN PROGRESS | Batch-1 implementation, evaluation, classification, redundancy, and curation complete through 7G |
| Phase 8 | Candidate Factor Review | NOT STARTED | Requires explicit human review to move DIAGNOSTIC_PROBE → CANDIDATE_REVIEW |
| Phase 9 | Multi-factor Signal Construction | NOT STARTED | Only CANDIDATE_REVIEW factors may be combined |
| Phase 10 | Strategy Backtest with Borrowed Engine | NOT STARTED | Use VectorBT / Qlib / Backtrader only after Phase 9 |
| Phase 11 | Cost / Slippage / Capacity / Risk | NOT STARTED | Transaction cost, turnover, capacity, drawdown, concentration controls |
| Phase 12 | Paper Trading | NOT STARTED | Full strategy in paper-trading mode |
| Phase 13 | Small-capital Live Validation | NOT STARTED | Small-capital live validation only after prior gates |

---

## 3. Phase 7 Subphase Status

| Subphase | Name | Status | Main Output |
|----------|------|--------|-------------|
| 7A | Protocol & Candidate Backlog | COMPLETE | 86 candidate factors, 27 selected_for_7B |
| 7B | First Implementation Batch | COMPLETE | 27 OHLCV-derived diagnostic factors implemented |
| 7C-A | Dynamic Adapter Hardening | COMPLETE | Candidate-mode fail-fast and direction handling |
| 7C-B | Dynamic Factor Build & Evaluation | COMPLETE | Dynamic factor_values and dynamic evaluation summaries |
| 7D-A | Static Adapter Hardening | COMPLETE | Static evaluator subset/candidate mode and direction handling |
| 7D-B | Static Evaluation & Static-vs-Dynamic Validation | COMPLETE | Static summaries and static-vs-dynamic comparison |
| 7E | Diagnostic Classification | COMPLETE | TIER_1/TIER_2/TIER_3/TIER_4 classification |
| 7F | Redundancy Diagnostics | COMPLETE | 351 static + 351 dynamic pairwise correlations, 6 redundancy groups |
| 7G | Factor Library Curation | COMPLETE | Curated factor library v0.2 |
| 7H | Batch-2 Factor Mining Preparation | NEXT | Select next factor batch using lessons from Batch-1 |

---

## 4. Curated Library v0.2 Summary

### 4.1 Recommended research use

| recommended_research_use | Count |
|--------------------------|-------|
| CORE_DIAGNOSTIC_CANDIDATE | 6 |
| REVIEW_DIRECTION_OR_FORMULA | 16 |
| MONITOR_TURNOVER_RISK | 2 |
| WEAK_DIAGNOSTIC_ONLY | 1 |
| REDUNDANCY_REVIEW | 2 |

### 4.2 Core diagnostic candidates

These are stable diagnostic baselines, not alpha factors:

- `vol_5h`
- `vol_40h`
- `range_1h`
- `range_4h`
- `price_pos_24h`
- `xs_rank_vol`

### 4.3 Factors requiring direction or formula review

16 factors are tagged `REVIEW_DIRECTION_OR_FORMULA`, mostly due to expected-direction mismatch, sign instability, or redundancy combined with direction concerns.

### 4.4 Turnover-risk factors

2 factors are tagged primarily as `MONITOR_TURNOVER_RISK`:

- `candle_body`
- `xs_rank_ret_1h`

### 4.5 Weak diagnostic only

1 factor is tagged `WEAK_DIAGNOSTIC_ONLY`:

- `vol_ratio_5_20`

### 4.6 Redundancy review

2 factors are tagged primarily as `REDUNDANCY_REVIEW`:

- `range_24h`
- `price_pos_72h`

---

## 5. Key Constraints Carried Forward

- Calendar-time joins only.
- No `shift(-h)` feature leakage.
- No row-based forward return construction.
- expected_direction must come from theory/candidate metadata, never reverse-engineered from evaluation results.
- All new factors start as diagnostic probes.
- No alpha promotion without explicit PM/human approval.
- No factor removal based only on diagnostic classification or redundancy.
- No strategy backtest before Phase 10.
- Dynamic universe diagnostics are available, but the current dynamic universe remains `dynamic_from_current_listed_pool`, not true PIT.

---

## 6. Next Phase: 7H — Batch-2 Factor Mining Preparation

Phase 7H should not implement factors yet. It should prepare Batch-2 candidate selection.

Expected scope:

1. Review remaining candidates in `factor_mining_candidates_v0_1.csv`.
2. Use Phase 7G risk lessons: direction mismatch, high turnover, redundancy, weak signals.
3. Select a controlled Batch-2 candidate set.
4. Prefer factors that add new families or new structure rather than near-duplicates of Batch-1.
5. Keep all selected factors diagnostic-only.

Potential Batch-2 sources:

- additional formulaic OHLCV factors with low leakage risk;
- selected WQ101 / GTJA / Alpha158-style transforms that current factor factory can support;
- crypto-native candidates only if data availability, schema, and known_at semantics are already controlled.

---

## 7. Phase Transition Rule

A later phase may start only after:

1. the previous phase closeout is committed;
2. machine-readable artifacts exist where required;
3. PM review passes;
4. no BLOCK / NEEDS FIX remains;
5. no unauthorized alpha/status/backtest step was introduced.
