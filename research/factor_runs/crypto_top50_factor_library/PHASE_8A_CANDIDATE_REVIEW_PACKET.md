# Phase 8A Closeout — Candidate Review Packet

> Date: 2026-06-15
> Previous phase: Phase 7N-R2 COMPLETE
> Human review required: yes

---

## Status

Phase 8A: COMPLETE, pending human review.

---

## 1. Scope

Phase 8A prepares a structured human review packet for all 42 factors in the v0.4
diagnostic factor library. Phase 8A is a documentation and decision-preparation phase
only. No factors are promoted, no backtests are run, no alpha claims are made.

---

## 2. Inputs

| Input | Description |
|-------|-------------|
| `phase7n_r2_phase8_review_queue_repaired.csv` | 42-factor review queue with categories |
| `phase7n_r2_queue_category_summary.csv` | Category distribution summary |
| `phase7n_v04_library_audit_summary.csv` | Per-factor audit (42 rows) |
| `phase7n_family_readiness_summary.csv` | Per-family readiness (15 families) |
| `phase7n_blockers_and_constraints.csv` | Blockers (7 items) |
| `phase7m_f_curated_factor_library_v0_4.csv` | v0.4 curated library (42 factors) |

---

## 3. Summary Counts

| Metric | Count |
|--------|-------|
| Total factors | 42 |
| Families | 15 |
| Diagnostic tiers | TIER_1_STABLE_DIAGNOSTIC: 11, TIER_2_PROMISING_BUT_NEEDS_REVIEW: 17, TIER_3_WEAK_DIAGNOSTIC: 6, TIER_4_UNSTABLE_OR_SIGN_FLIP: 8 |

### Category Distribution

| Category | Count |
|----------|-------|
| PHASE8_READY_FOR_HUMAN_REVIEW | 10 |
| REDUNDANCY_REVIEW_FIRST | 10 |
| REVIEW_DIRECTION_FIRST | 14 |
| WEAK_OR_LOW_PRIORITY | 8 |

### Recommended Research Use Distribution

| recommended_research_use | Count |
|--------------------------|-------|
| CORE_DIAGNOSTIC_CANDIDATE | 10 |
| LOW_PRIORITY_RESEARCH | 3 |
| MONITOR_TURNOVER_RISK | 2 |
| REDUNDANCY_REVIEW | 2 |
| REVIEW_DIRECTION_OR_FORMULA | 22 |
| WEAK_DIAGNOSTIC_ONLY | 3 |

---

## 4. Ready Shortlist (10 factors)

These 10 factors are `PHASE8_READY_FOR_HUMAN_REVIEW` — TIER_1, CORE_DIAGNOSTIC_CANDIDATE,
non-redundant, clean review flags:

| factor_id | factor_family | diagnostic_tier | recommended_research_use |
|-----------|---------------|-----------------|--------------------------|
| vol_5h | volatility | TIER_1_STABLE_DIAGNOSTIC | CORE_DIAGNOSTIC_CANDIDATE |
| vol_40h | volatility | TIER_1_STABLE_DIAGNOSTIC | CORE_DIAGNOSTIC_CANDIDATE |
| range_1h | range_position | TIER_1_STABLE_DIAGNOSTIC | CORE_DIAGNOSTIC_CANDIDATE |
| range_4h | range_position | TIER_1_STABLE_DIAGNOSTIC | CORE_DIAGNOSTIC_CANDIDATE |
| price_pos_24h | price_position | TIER_1_STABLE_DIAGNOSTIC | CORE_DIAGNOSTIC_CANDIDATE |
| xs_rank_vol | cross_sectional_normalized | TIER_1_STABLE_DIAGNOSTIC | CORE_DIAGNOSTIC_CANDIDATE |
| rsi_28h | technical_indicators | TIER_1_STABLE_DIAGNOSTIC | CORE_DIAGNOSTIC_CANDIDATE |
| rsi_7h | technical_indicators | TIER_1_STABLE_DIAGNOSTIC | CORE_DIAGNOSTIC_CANDIDATE |
| downside_vol_20h | realized_skew_kurtosis | TIER_1_STABLE_DIAGNOSTIC | CORE_DIAGNOSTIC_CANDIDATE |
| vol_of_vol_20h | realized_skew_kurtosis | TIER_1_STABLE_DIAGNOSTIC | CORE_DIAGNOSTIC_CANDIDATE |


---

## 5. Blockers and Constraints

| ID | Category | Description | Impact |
|----|----------|-------------|--------|
| B1 | DATA | Dynamic universe is not true point-in-time (PIT); uses dynamic_from_current_listed_pool | Cannot trust cross-sectional factor values as live-deployable signals |
| B2 | BACKTEST | No strategy backtest has been run (Phase 10 not started) | Cannot assess factor value in a portfolio context |
| B3 | COST | No cost/slippage/capacity analysis (Phase 11 not started) | Cannot assess feasibility of trading signals |
| B4 | DIRECTION | All 6 crypto-native factors have EXPECTED_DIRECTION_MISMATCH | Theory/formula review needed before alpha consideration |
| B5 | SIGNAL | taker_buy_delta_5h, funding_rate_zscore_80h, funding_rate_change_24h are weak diagnostic (TIER_3/4) | Weak signal strength; may not add value in multi-factor model |
| B6 | REDUNDANCY | 8 OHLCV-derived redundancy review groups unresolved | May affect factor selection for Phase 9 multi-factor construction |
| B7 | MULTI_LABEL | taker_buy_ratio_20h, funding_rate_level_20h, funding_rate_zscore_80h, funding_rate_change_24h have MULTI_LABEL_INCONSISTENT | Factor direction may differ across return horizons |


---

## 6. Negative Declarations

- **No factor was promoted.** All 42 factors remain DIAGNOSTIC_PROBE.
- **No factor entered CANDIDATE_REVIEW.** No status change was made.
- **No alpha claim was made.** Phase 8A is documentation only.
- **No strategy backtest was run.** Backtesting starts at Phase 10.
- **No portfolio simulation was run.**
- **No factor was removed.** All 42 factors remain in the library.
- **v0.4 remains a diagnostic library.** No upgrade occurred.

---

## 7. Deliverables

| Deliverable | File | Description |
|-------------|------|-------------|
| Human review packet | `phase8a_human_review_packet.csv` | 42-factor review packet |
| Ready shortlist | `phase8a_ready_for_human_review_shortlist.csv` | 10-factor clean shortlist |
| Review protocol | `phase8a_review_protocol.md` | Human review instructions |
| Decision template | `phase8a_review_decision_template.csv` | Decision recording template |
| Closeout | `PHASE_8A_CANDIDATE_REVIEW_PACKET.md` | This document |

---

## 8. Next Required PM Decision

The PM/human reviewer must:

1. Review the 42-factor human review packet.
2. Focus first on the 10-factor ready shortlist.
3. Record decisions in `phase8a_review_decision_template.csv`.
4. Decide whether to proceed to Phase 8B (factor promotion / backtest preparation).

**No action is taken automatically.** All decisions require explicit human approval.
