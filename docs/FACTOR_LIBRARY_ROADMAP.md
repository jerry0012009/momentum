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
| Current subphase | Phase 7L-R COMPLETE |
| Next subphase | Phase 7M — Crypto-native Factor Implementation (pending PM) |
| Curated library version | v0.3 |
| Curated factors | 36 (27 Batch-1 + 9 Batch-2) |
| Families | 13 |
| Diagnostic tiers | T1: 11, T2: 15, T3: 3, T4: 7 |
| Redundancy groups | 8 (6 Batch-1 + 2 Batch-2) |
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

---

## 4. Curated Library v0.3 Summary

### 4.1 Recommended research use (combined)

| recommended_research_use | Batch-1 | Batch-2 | Total |
|--------------------------|---------|---------|-------|
| CORE_DIAGNOSTIC_CANDIDATE | 6 | 4 | 10 |
| REVIEW_DIRECTION_OR_FORMULA | 16 | 3 | 19 |
| MONITOR_TURNOVER_RISK | 2 | 0 | 2 |
| WEAK_DIAGNOSTIC_ONLY | 1 | 0 | 1 |
| LOW_PRIORITY_RESEARCH | 0 | 2 | 2 |
| REDUNDANCY_REVIEW | 2 | 0 | 2 |

### 4.2 Batch-2 TIER_1 factors

These are stable diagnostic baselines, not alpha factors:

- `downside_vol_20h` — negative expected direction, |RankIC|=0.035, LOW_TURNOVER
- `vol_of_vol_20h` — negative expected direction, |RankIC|=0.034, LOW_TURNOVER
- `rsi_7h` — negative expected direction, |RankIC|=0.024, NORMAL_TURNOVER
- `rsi_28h` — negative expected direction, |RankIC|=0.018, NORMAL_TURNOVER

### 4.3 Batch-2 TIER_4 factors

- `qvol_ma_ratio_5_20` — sign flip between static and dynamic
- `ma_gap_20_80` — sign flip between static and dynamic

### 4.4 New families in Batch-2

- `technical_indicators` (4 factors): ema_12_26_gap, rsi_7h, rsi_28h, williams_r_14h
- `realized_skew_kurtosis` (2 factors): downside_vol_20h, vol_of_vol_20h

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

## 6. Next Phase: 7M — Crypto-native Factor Implementation

Phase 7L built canonical data caches:
- **Taker enriched bars**: static 75.82% / dynamic 91.73% coverage of taker_buy_quote_volume
- **Funding rate events**: 679 symbols, 2.1M events, intervals [1,2,4,8]h
- **Funding 1h aligned**: static 74.29% / dynamic 88.03% coverage, max age ≤ interval

Phase 7M scope (pending PM approval):
1. Implement taker imbalance factors (taker_buy_ratio_20h, taker_buy_zscore_20h, taker_buy_delta_5h)
2. Implement funding rate factors (funding_rate_current, funding_rate_ma_3, funding_rate_change_1h)
3. All factors start as DIAGNOSTIC_PROBE
4. Use enriched bars cache for taker, aligned cache for funding

---

## 7. Phase Transition Rule

A later phase may start only after:

1. the previous phase closeout is committed;
2. machine-readable artifacts exist where required;
3. PM review passes;
4. no BLOCK / NEEDS FIX remains;
5. no unauthorized alpha/status/backtest step was introduced.
