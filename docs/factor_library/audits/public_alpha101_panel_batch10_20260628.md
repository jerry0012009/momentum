# Public Alpha101 Panel Batch10 Audit - 2026-06-28

## Scope

Batch10 adds ten WorldQuant Alpha101 panel formulas that share OHLCV/VWAP/ADV, cross-sectional rank, time-series rank, decay, and rolling-correlation inputs:

- `wq101_alpha29`: coverage=331330000.000%, best_horizon=4h, best_adj_ic=+0.011685, consistency=DIVERGENT
- `wq101_alpha31`: coverage=329929200.000%, best_horizon=72h, best_adj_ic=-0.011574, consistency=CONSISTENT
- `wq101_alpha36`: coverage=325368400.000%, best_horizon=24h, best_adj_ic=+0.017858, consistency=DIVERGENT
- `wq101_alpha39`: coverage=324014200.000%, best_horizon=4h, best_adj_ic=+0.018444, consistency=DIVERGENT
- `wq101_alpha57`: coverage=329914300.000%, best_horizon=1h, best_adj_ic=+0.020796, consistency=DIVERGENT
- `wq101_alpha62`: coverage=329403200.000%, best_horizon=4h, best_adj_ic=+0.006471, consistency=CONSISTENT
- `wq101_alpha64`: coverage=326755200.000%, best_horizon=72h, best_adj_ic=-0.005561, consistency=CONSISTENT
- `wq101_alpha66`: coverage=289367000.000%, best_horizon=4h, best_adj_ic=+0.011333, consistency=DIVERGENT
- `wq101_alpha71`: coverage=259361100.000%, best_horizon=4h, best_adj_ic=+0.005693, consistency=DIVERGENT
- `wq101_alpha72`: coverage=319628900.000%, best_horizon=4h, best_adj_ic=+0.008159, consistency=CONSISTENT

Skipped in this batch: formulas requiring unavailable industry/sector/subindustry neutralization or cap/source contracts. No signal, trading, execution, or live-alpha code was changed.

## Workflow Evidence

- `build_factor_values.py --factor-ids ...`: completed for all 10 factors.
- `run_factor_intake.py --run-id public_alpha101_panel_batch10_20260628 --skip-build-values --skip-redundancy`: COMPLETE; 10 conclusion cards, all `CONDITIONAL_DIRECTION_REVIEW`.
- `build_factor_bilingual_cards.py`: PASS; 244 cards populated.
- `run_post_intake_workflow_completion.py --factor-ids ...`: all 18 stages completed successfully in 1474.8s.
- Redundancy: 244 factors, 29,646 pairwise rows, 137 clusters; all Batch10 factors have pairwise and summary rows.
- Page QA: 112 PASS / 0 FAIL; `factor_evaluation.json` has 244 factors.
- Post-intake integrity: 230 PASS / 0 FAIL / 10 WARN for the Batch10 factors.

## Current State

- Registered factors: 244
- Computed factor values: 244
- Missing factor values: 0
- Missing input factors: 0

## Interpretation Boundary

All ten factors remain research diagnostics with conditional direction. Paper/cost diagnostics remain harsh (`COST_COLLAPSED` or `INSUFFICIENT_DATA` in the batch), so this batch does not promote any production/live signal or trading claim.
