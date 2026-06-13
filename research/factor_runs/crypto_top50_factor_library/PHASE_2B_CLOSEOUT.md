# Phase 2B Closeout — Lightweight Quality Gate

## Status

- Phase 2B status: **COMPLETE**
- Date: 2026-06-13
- Commit: `6b5092b3b0f30d3b447545d5fa5f4bf048294968`
- Human review required: **yes**

## Fixed Issues

1. **timestamp = bar_close_time**: `fetch_crypto_top50_bars.py` now sets `timestamp` to `bar_open_time + 1h` (the bar close). Previously used kline open time, which meant factors were "known" before the bar closed — a look-ahead bias.
2. **bar_open_time retained for audit**: Both `bar_open_time` and `bar_close_time` columns are in `bars_1h.parquet` for traceability.
3. **factor known_at = bar_close_time**: All factor values have `known_at = timestamp = bar_close_time`. No factor is considered known before the bar closes.
4. **labels use calendar-time forward returns**: `build_labels.py` uses merge on `(timestamp + h, symbol)` to look up future close. Previously used `groupby.shift(-h)` which: (a) produced backward returns due to a merge direction bug, and (b) substituted nearby rows across gaps instead of returning NaN.
5. **symbols with missing_bar_rate > 5% excluded from evaluation**: `evaluate_factors.py` computes missing bar rate per symbol and excludes those above 5%. SPACEUSDT (21.7% missing) is excluded.
6. **direction-adjusted spread added**: Evaluation reads `expected_direction` from factor catalog. For positive factors, `direction_adjusted_spread = Q5 - Q1`. For negative factors, `Q1 - Q5`. For conditional, null.

## Validation Results

- n_symbols: 50
- excluded_symbols: ['SPACEUSDT'] (1 symbol, 21.7% missing bars)
- bars_rows: 215,061
- duplicate timestamp-symbol: 0
- label missing rates:
  - ret_fwd_1h: 0.0232%
  - ret_fwd_4h: 0.0930%
  - ret_fwd_24h: 0.5580%
  - ret_fwd_72h: 1.6739%
- factor coverage:
  - mom_20h: 99.54%
  - reversal_5h: 99.88%
  - volatility_20h: 99.54%
  - rsi_14h: 99.68%
  - bb_zscore_20h: 99.56%
- tests run: 33
- tests passed: 33

## Result Summary Check

`result_summary.md` confirmed to contain:

- [x] raw_spread (column: `raw_spread`)
- [x] raw_spread_t (column: `raw_spread_t`)
- [x] direction_adjusted_spread (column: `dir_adj_spread`)
- [x] direction_adjusted_tstat (column: `dir_adj_t`)
- [x] excluded_symbols (header: `excluded_symbols (missing_bar_rate > 5%)`)
- [x] timestamp_convention (header: `timestamp_convention`)
- [x] label_convention (header: `label_convention`)

## Remaining Caveats

1. **V0 uses static current Top50 by 24h quote volume**: The universe is a snapshot of the current top 50, not a dynamic rolling universe. Tokens that were delisted or newly listed during the 180-day period are not handled.
2. **V0 has survivorship bias**: Only tokens that survived to the snapshot date are included. Failed/delisted tokens are missing, biasing results upward.
3. **V0 is not dynamic universe**: A proper V1 should use 30d rolling volume ranking with monthly rebalancing.
4. **V0 t-stats are inflated by overlapping labels**: 4h, 24h, and 72h forward returns overlap heavily. IC and spread t-stats are overstated. Use overlap-adjusted inference or monthly aggregation for significance claims.
5. **V0 does not include slippage/spread/trading costs**: Evaluation uses raw returns only. No transaction cost, slippage, or bid-ask spread adjustment.
6. **V0 is diagnostic, not deployable alpha**: The 5 registered factors are `DIAGNOSTIC_PROBE` status. None are `CANDIDATE_ALPHA`. Do not use these results to justify live trading.

## Decision

Recommended decision:

- Phase 2B: **COMPLETE**
- Phase 2C: **NOT ALLOWED** (do not enter Phase 2C until human reviews this closeout and approves)

Do not promote any factor to candidate alpha.
Do not start strategy backtest.
Do not enter Phase 2D/2E yet.

### Next Steps (require human approval)

1. Human reviews this closeout and the validation results.
2. If approved, Phase 2C can begin: deeper statistical analysis (overlap-adjusted inference, monthly stability, cross-validation).
3. Only after Phase 2C produces positive evidence can any factor be promoted to `CANDIDATE_ALPHA`.
4. Phase 2D/2E (strategy backtest, paper trading) require CANDIDATE_ALPHA factors and are not in scope today.
