# Phase 7 Batching Design

> Version: 1.0 | Phase: 7A

---

## Phase Structure

| Phase | Name | Scope |
|-------|------|-------|
| 7A | Protocol & Candidate Backlog | Protocol doc, candidate CSV, batch design |
| 7B | First Implementation Batch | Implement 20-30 factors from backlog |
| 7C | Dynamic-Universe Evaluation of 7B | factor_values build + dynamic evaluation |
| 7D | Static-vs-Dynamic / Alphalens Validation | Comparison + external cross-check |
| 7E | Batch-2 Selection | Select next batch from backlog |

Each batch (7B, 7E, ...) follows the same pipeline:

1. Candidate selection (from backlog, with rationale)
2. Implementation (factor_formula_registry.py + tests)
3. factor_values build (build_factor_values.py)
4. Dynamic evaluation (evaluate_factors_dynamic_universe.py)
5. Coverage QA (audit_dynamic_universe_factor_values.py)
6. Static-vs-dynamic comparison (compare_static_dynamic_factor_evals.py)
7. No alpha promotion (all factors DIAGNOSTIC_PROBE)
8. Batch closeout (markdown + JSON + commit+push)

## Batch Completion Gate

A new batch may begin only when:
- Previous batch closeout is committed and pushed
- PM reviews and approves
- No BLOCK status from QA

## 7B First Batch Selection Criteria

Priority: low complexity, low parameter count, existing OHLCV only.

Selected families (20-30 factors):
- momentum: 5 (5h, 10h, 40h, 80h, acceleration)
- reversal: 4 (3h, 10h, 24h, 48h)
- volatility: 4 (5h, 40h, ratio 5/20, ratio 10/40)
- range_position: 5 (1h, 4h, 24h, price_pos_24h, price_pos_72h)
- volume_liquidity: 3 (vol_zscore_20h, vol_zscore_48h, vol_ma_ratio)
- quote_volume_liquidity: 3 (qvol_zscore_20h, qvol_zscore_48h, qvol_ma_ratio)
- trend_ma: 3 (ma_gap_5/20, 10/40, 20/80)
- breakout: 2 (breakout_dist_20h, breakout_dist_48h)
- intraday_candle: 3 (body, wick_upper, wick_lower)
- cross_sectional_normalized: 3 (rank_ret, rank_vol, rank_range)

Total: ~35 factors across 10 families.
