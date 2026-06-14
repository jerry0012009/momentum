# Phase 7 Batching Design

> Version: 1.1 | Phase: 7A-QA
>
> Updated: 2026-06-14 to match current candidate backlog (86 candidates, 27 in 7B)

---

## Phase Structure

| Phase | Name | Scope |
|-------|------|-------|
| 7A | Protocol & Candidate Backlog | Protocol doc, candidate CSV, batch design |
| 7B | First Implementation Batch | Implement 27 factors from backlog |
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

## 7B First Batch (27 factors, 11 families)

| Family | 7B Count | Factors |
|--------|----------|---------|
| momentum | 3 | mom_5h, mom_10h, mom_40h |
| reversal | 3 | rev_3h, rev_10h, rev_24h |
| volatility | 3 | vol_5h, vol_40h, vol_ratio_5_20 |
| range_position | 3 | range_1h, range_4h, range_24h |
| price_position | 2 | price_pos_24h, price_pos_72h |
| volume_liquidity | 2 | vol_zscore_20h, vol_zscore_48h |
| quote_volume_liquidity | 2 | qvol_zscore_20h, qvol_zscore_48h |
| trend_ma | 2 | ma_gap_5_20, ma_gap_10_40 |
| breakout | 2 | breakout_dist_20h, breakout_dist_48h |
| intraday_candle | 3 | candle_body, candle_wick_upper, candle_wick_lower |
| cross_sectional_normalized | 2 | xs_rank_ret_1h, xs_rank_vol |
| **Total** | **27** | |

Selection criteria: low complexity, low parameter count, existing OHLCV only.
Not all horizon variants are selected — avoids overfitting to one family.
