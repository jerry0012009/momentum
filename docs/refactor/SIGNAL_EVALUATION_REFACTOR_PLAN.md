# Signal Evaluation Refactor Plan

> Phase 12D-H1 · 2026-06-18

## 1. Why Not Rename Old Phase Scripts

Old scripts are historical audit trail:
- `run_phase10a_signal_backtest.py` — Phase 10A audit
- `run_phase10a_r_diagnostics.py` — Phase 10A-R audit
- `run_phase10b_tail_diagnostics.py` — Phase 10B audit
- `run_phase10d_tail_aware_variants.py` — Phase 10D audit

They should be preserved as-is for reproducibility.
New code lives in `src/momentum/signal_evaluation/`.

## 2. Old → New Mapping

| Old Phase | Human Name | New Module |
|-----------|-----------|------------|
| 10A | RankIC / QuantileSpread evaluation | `rank_ic.py` + `quantile_spread.py` |
| 10A-R | Direction consistency check | `consistency.py` |
| 10B | Bucket / tail diagnostics | `bucket_tail.py` (future) |
| 10C | Tail-aware policy design | `VariantPolicySpec` / `PolicyDesignNotes` (docs, not evaluator) |
| 10D | Variant grid evaluation | `variant_grid.py` (future) |
| 11A/11B | Cost / liquidity bridge | `cost_bridge.py` (future) |
| 12A/12B | Paper diagnostic / rolling monitoring | `PaperDiagnostic` (future) |

## 3. Target Structure

```
src/momentum/signal_evaluation/
├── __init__.py
├── schema.py              # Input schema definitions
├── rank_ic.py             # RankIC computation + summary
├── quantile_spread.py     # Quantile spread computation + summary
├── consistency.py         # Direction consistency check
├── bucket_tail.py         # (future) Bucket/tail diagnostics
├── variant_grid.py        # (future) Variant grid evaluator
├── cost_bridge.py         # (future) Cost/liquidity bridge
├── report_schema.py       # (future) Standard report output format
└── README.md
```

## 4. Migration Principles

1. New modules first validated with toy tests
2. Then validated with old outputs (parity tests)
3. Then old phase scripts become thin wrappers
4. **Never change historical results**
5. Never change existing CSV schema unless creating v2

## 5. ML Signal Integration

Any model that outputs `timestamp / symbol / signal_name / signal_value` can reuse all evaluation modules. No special integration needed.

## 6. Current Status

- [x] schema.py
- [x] rank_ic.py
- [x] quantile_spread.py
- [x] consistency.py
- [ ] bucket_tail.py
- [ ] variant_grid.py
- [ ] cost_bridge.py
- [ ] report_schema.py
- [ ] Parity tests against old phase outputs
- [ ] Old scripts wrapped as thin CLI entry points
