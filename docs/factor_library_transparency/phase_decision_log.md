# Phase Decision Log

> Phase 12C transparency documentation

---

## Phase 7: Factor Screening
**Decision:** Keep 10 factors for diagnostic library.
**Rationale:** Correlation analysis showed 8 factors were redundant or unstable. The remaining 10 have low inter-factor correlation and stable cross-sectional properties.
**Risk accepted:** Factor definitions are diagnostic, not production-optimized.

## Phase 8: Human Review
**Decision:** Approve 10 CANDIDATE_REVIEW factors for signal construction.
**Rationale:** Human review confirmed factor definitions, directions, and limitations are reasonable.
**Risk accepted:** Human judgment is subjective.

## Phase 9A/9A-R: Factor Library v0.4
**Decision:** Create 42-factor library with 10 CANDIDATE_REVIEW factors.
**Rationale:** Library provides a complete audit trail for all factors evaluated.
**Risk accepted:** None significant.

## Phase 9B: Signal Panel Construction
**Decision:** Build signal panel with 3 signal variants × 10 factors × 266 symbols.
**Rationale:** Need a unified panel for all downstream evaluation.
**Risk accepted:** Some symbols have incomplete data. 266 symbols in panel, only 43 have forward returns.

## Phase 10A: RankIC / Quantile Spread
**Decision:** Evaluate all 48 variants. Initial result: 3/48 PASS.
**Rationale:** RankIC and quantile spread are the primary screening metrics.
**Risk accepted:** RankIC is a weak predictor (typical values 0.025-0.042). Spread is thin.

## Phase 10A-R: Direction Correction
**Decision:** All 12 canonical RankIC are positive. No direction changes needed.
**Rationale:** Initial NEGATIVE labels for 24h/72h were caused by mixing diagnostic values with canonical values.
**Risk accepted:** None — this was a data reconciliation, not a modeling decision.

## Phase 10B-lite: Tail Diagnostics
**Decision:** Spread is robust to tail trimming. No factors dropped.
**Rationale:** Winsorized and tail-trim spreads are similar to raw spreads.
**Risk accepted:** Limited tail analysis. Only tested 1st/99th percentile winsorization.

## Phase 10C: Multi-Metric Evaluation
**Decision:** Use RankIC + median spread + hit rate for comprehensive evaluation.
**Rationale:** Single metric (RankIC or spread alone) can be misleading.
**Risk accepted:** Metric weighting is equal — may need tuning.

## Phase 10C-R: RankIC Reconciliation
**Decision:** Correct false NEGATIVE labels. All 12 RankIC confirmed positive.
**Rationale:** The NEGATIVE labels were caused by comparing 10A-R diagnostic values with canonical 10A values.
**Risk accepted:** None.

## Phase 10D: 48-Variant Grid
**Decision:** Evaluate all 48 combinations. 3/48 PASS initially.
**Rationale:** Comprehensive grid to find the best variant.
**Risk accepted:** Multiple testing — 48 variants increases false positive risk.

## Phase 10D-R: Bucket0 Guard Repair
**Decision:** Fix guard logic (bucket assignment + exposure metric). 9/48 PASS after repair.
**Rationale:** Guard was using wrong signal for bucket assignment and measuring wrong exposure quantity.
**Risk accepted:** Guarded variants still need cost evaluation.

## Phase 11A: Cost/Slippage Diagnostic
**Decision:** Only 1/9 survives — core_only 1h no_guard.
**Rationale:** Bucket0 guard increases turnover without proportional spread improvement. All 4h variants fail due to higher per-rebalance turnover.
**Risk accepted:** Per-rebalance cost model is conservative (overly pessimistic). Actual turnover is lower.

## Phase 11B: Liquidity/Capacity
**Decision:** Rebuild liquidity data. Capacity is sufficient ($660k median at 1%). Bottleneck is cost, not capacity.
**Rationale:** Original kline files were empty for some symbols. Rebuilt from non-empty files.
**Risk accepted:** 43-symbol universe is limited. Volume data quality varies.

## Phase 12A: Paper Signal Harness
**Decision:** Build paper signal for single survivor. 16 weighted symbols.
**Rationale:** Need a concrete paper signal before monitoring.
**Risk accepted:** Static single-timestamp snapshot. Not yet validated over time.

## Phase 12B: Rolling Monitoring
**Decision:** 30-day rolling monitoring. Signal survives mid-cost (turnover-adjusted).
**Rationale:** Phase 11A's per-rebalance cost model was overly pessimistic. Rolling monitoring with actual turnover is more realistic.
**Risk accepted:** 30-day window is short. Historical backfill, not forward validation.

## Phase 12C: Grand Transparency
**Decision:** Full transparency closeout. PM decision pending.
**Rationale:** Need complete audit trail before Phase 13 decision.
**Risk accepted:** Documentation may be incomplete or contain errors.

## Phase 13: NOT STARTED
**PM preference:** Phase 13A future paper validation only, no real execution, no capital.
**Decision:** PENDING Phase 12C review.
