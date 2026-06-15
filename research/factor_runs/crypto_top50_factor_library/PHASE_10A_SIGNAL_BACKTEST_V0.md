# Phase 10A Closeout — Diagnostic Signal Backtest v0

> Date: 2026-06-15
> Previous phase: Phase 9B COMPLETE
> Scope: Diagnostic signal evaluation only
> PM decision: Evaluate 3 Phase 9B signals across 4 horizons

---

## Status

Phase 10A: COMPLETE, pending PM review.
Phase 10B: NOT STARTED.
Phase 11: NOT STARTED. Phase 12: NOT STARTED. Phase 13: NOT STARTED.

---

## 1. Implementation

Phase 10A ran a diagnostic backtest/evaluation for the 3 Phase 9B signals across 4 forward return horizons.

### Signals Evaluated

| Signal | Description | Factors |
|--------|-------------|---------|
| signal_v0_core_only | Risk pressure + oscillator (60/40), z-scored | 6 |
| signal_v0_pm_full_structured | Core × liquidity gate × position overlay, z-scored (PM-preferred v0) | 10 |
| signal_v0_family_balanced_diagnostic | 4-channel equal weight, z-scored (diagnostic only) | 10 |

### Horizons

| Horizon | Forward Return |
|---------|---------------|
| 1h | ret_fwd_1h |
| 4h | ret_fwd_4h |
| 24h | ret_fwd_24h |
| 72h | ret_fwd_72h |

### Data

- Signal panel: 3,314,397 rows, 17,801 timestamps
- Forward returns: 713,572 rows, 17,533 timestamps
- Joined: 626,438 rows, 17,520 timestamps
- Join method: calendar timestamp + symbol (no shift, no recomputation)

---

## 2. Evaluation Methods

### RankIC

Cross-sectional Spearman RankIC computed per timestamp for each signal × horizon:
- mean RankIC, std RankIC, t-stat, positive rate
- Minimum cross-section: 10 symbols per timestamp

### Quantile Spread

Top/bottom 20% long-short spread (equal-weight within legs):
- mean spread, std spread, t-stat, hit rate
- Cumulative spread return, max drawdown
- No transaction costs, no slippage

---

## 3. Deliverables

| Deliverable | File | Description |
|-------------|------|-------------|
| Closeout | `PHASE_10A_SIGNAL_BACKTEST_V0.md` | This document |
| Script | `scripts/run_phase10a_signal_backtest.py` | Reproducible backtest runner |
| RankIC summary | `phase10a_signal_rankic_summary.csv` | 3 signals × 4 horizons |
| Quantile spread | `phase10a_signal_quantile_spread_summary.csv` | 3 signals × 4 horizons |
| Timeseries | `phase10a_signal_backtest_timeseries.parquet` | 420K rows per signal×horizon |
| Quality checks | `phase10a_signal_backtest_quality_checks.csv` | 12 checks all PASS |
| Label audit | `phase10a_label_alignment_audit.csv` | 10 checks all PASS |

---

## 4. Negative Declarations

- **No alpha claim was made.** All outputs are diagnostic.
- **No tradeable/live claim.**
- **No cost/slippage/capacity analysis.** Phase 11 handles costs.
- **No portfolio optimization.**
- **No parameter optimization.**
- **No weight fitting.**
- **No model selection based on best result.**
- **Phase 11 has not started.**
- **Phase 12 has not started.**
- **Phase 13 has not started.**

---

## 5. Next Required PM Decision

Phase 10B or Phase 11 may **only** begin after:

1. PM reviews Phase 10A RankIC and quantile spread results.
2. PM explicitly approves next phase.
3. Phase 11 scope would be cost/slippage/capacity-aware evaluation.

**No action is taken automatically.** All decisions require explicit PM approval.
