# Public Alpha101 Panel Batch08 Intake Audit - 2026-06-28

## Scope

This batch adds 10 public WorldQuant 101 Alpha factors that share
OHLCV/VWAP/returns/rank/rolling correlation-covariance operators. The batch
uses only canonical bar inputs and avoids industry neutralization, market cap,
taker, funding, and live-production dependencies:

- `wq101_alpha1`
- `wq101_alpha2`
- `wq101_alpha3`
- `wq101_alpha4`
- `wq101_alpha5`
- `wq101_alpha7`
- `wq101_alpha8`
- `wq101_alpha10`
- `wq101_alpha11`
- `wq101_alpha13`

Source reference: Kakushadze, "101 Formulaic Alphas"
(`https://arxiv.org/pdf/1601.00991`).

Guardrails:

- Registry remains the only factor-definition entry point.
- WQ101 `rank` is implemented as panel, per-timestamp cross-sectional logic.
- `ts_rank`, rolling covariance, and rolling correlations remain per-symbol
  time-series operations.
- VWAP maps to `quote_volume / volume` from canonical bars.
- ADV maps to rolling mean `volume` over the published window length.
- `ts_argmax` uses the local convention of bars since the latest rolling
  maximum, matching earlier public Alpha101 panel batches.
- No signal panel, trading, execution, broker, or live-production code changed.
- Generated HTML was rebuilt by workflow, not edited by hand.
- All factors are diagnostic research assets only.

## Formula Mapping

| factor_id | WQ101 formula shape | required inputs | scope | lookback | direction |
| --- | --- | --- | --- | --- | --- |
| `wq101_alpha1` | `rank(ts_argmax(signedpower(where(returns<0,stddev(returns,20),close),2),5))-0.5` | `close` | panel | 25 | conditional |
| `wq101_alpha2` | `-corr(rank(delta(log(volume),2)), rank((close-open)/open), 6)` | `open`, `close`, `volume` | panel | 8 | conditional |
| `wq101_alpha3` | `-corr(rank(open), rank(volume), 10)` | `open`, `volume` | panel | 10 | conditional |
| `wq101_alpha4` | `-ts_rank(rank(low), 9)` | `low` | panel | 9 | conditional |
| `wq101_alpha5` | `rank(open-mean(vwap,10)) * -abs(rank(close-vwap))` | `open`, `close`, `volume`, `quote_volume` | panel | 10 | conditional |
| `wq101_alpha7` | `where(adv20<volume, -ts_rank(abs(delta(close,7)),60)*sign(delta(close,7)), -1)` | `close`, `volume` | panel | 67 | conditional |
| `wq101_alpha8` | `-rank(sum(open,5)*sum(returns,5)-delay(sum(open,5)*sum(returns,5),10))` | `open`, `close` | panel | 15 | conditional |
| `wq101_alpha10` | `rank(where(ts_min(delta(close,1),4)>0,delta,where(ts_max(delta(close,1),4)<0,delta,-delta)))` | `close` | panel | 5 | conditional |
| `wq101_alpha11` | `(rank(ts_max(vwap-close,3))+rank(ts_min(vwap-close,3)))*rank(delta(volume,3))` | `close`, `volume`, `quote_volume` | panel | 4 | conditional |
| `wq101_alpha13` | `-rank(covariance(rank(close), rank(volume), 5))` | `close`, `volume` | panel | 5 | conditional |

## Workflow / Resource Notes

This batch extends `scripts/alpha101_panel_ops.py` with `rolling_idxmax_wide`,
`rolling_cov_wide`, and ten panel compute functions. Tests independently
rebuild the formulas in wide-panel form and check registry metadata, helper
semantics, Alpha7's hard `-1` fallback branch, and per-symbol timestamp
isolation.

Observed full post-intake costs:

- Factor-value generation for 10 panel factors completed successfully.
- Intake run `public_alpha101_panel_batch08_20260628` completed in 307s.
- Incremental PM-18 redundancy matrix: 2,185 target pairs, 24,976 merged pairs,
  224 factors, 118 clusters, 531.0s.
- Direction-aware decile diagnostics: 187.0s.
- Capacity/liquidity diagnostics: 180.6s.
- Full post-intake workflow completion: 1,431.9s.

## Validation

Commands run:

```bash
.venv/bin/python -m pytest tests/unit/test_public_alpha101_panel_batch08.py tests/unit/test_public_factor_candidate_manifest.py -q
.venv/bin/python scripts/check_factor_registry_integrity.py
.venv/bin/python scripts/build_factor_values.py --factor-ids wq101_alpha1,wq101_alpha2,wq101_alpha3,wq101_alpha4,wq101_alpha5,wq101_alpha7,wq101_alpha8,wq101_alpha10,wq101_alpha11,wq101_alpha13
.venv/bin/python scripts/run_factor_intake.py --factor-ids wq101_alpha1 wq101_alpha2 wq101_alpha3 wq101_alpha4 wq101_alpha5 wq101_alpha7 wq101_alpha8 wq101_alpha10 wq101_alpha11 wq101_alpha13 --run-id public_alpha101_panel_batch08_20260628 --skip-build-values --skip-redundancy
.venv/bin/python scripts/build_factor_bilingual_cards.py
.venv/bin/python scripts/run_post_intake_workflow_completion.py --factor-ids wq101_alpha1,wq101_alpha2,wq101_alpha3,wq101_alpha4,wq101_alpha5,wq101_alpha7,wq101_alpha8,wq101_alpha10,wq101_alpha11,wq101_alpha13
.venv/bin/python scripts/check_public_factor_integration_status.py
```

Results:

- Factor values computed for all 10 factors.
- Final coverage: `wq101_alpha1` 99.839%, `wq101_alpha2` 99.669%,
  `wq101_alpha3` 79.195%, `wq101_alpha4` 99.959%,
  `wq101_alpha5` 99.678%, `wq101_alpha7` 99.733%,
  `wq101_alpha8` 99.903%, `wq101_alpha10` 99.992%,
  `wq101_alpha11` 99.720%, `wq101_alpha13` 99.992%.
- Intake run `public_alpha101_panel_batch08_20260628`: COMPLETE.
- Intake conclusion cards: 10 `CONDITIONAL_DIRECTION_REVIEW`.
- Post-intake state: 224 registered, 224 computed, 0 missing factor values,
  0 missing inputs.
- `reports/site/factor-library/assets/factor_evaluation.json`: 224 factors,
  including all batch08 factors.
- Factor evaluation page QA: 112 PASS / 0 FAIL.
- Post-intake integrity QA for the 10 new factors: 230 PASS / 0 FAIL /
  10 WARN.
- Public manifest status after refresh: Alpha101 69 total,
  63 accounted/non-skipped, 6 skipped taxonomy-blocked; Alpha158 101 total,
  95 accounted/non-skipped, 6 skipped duplicates.

The warnings are optional overlapping-sleeve diagnostics, not missing factor
values, missing source metadata, page coverage failures, or core workflow
failures. Cost stress diagnostics remain harsh for this batch: the strongest
gross Sharpe examples collapse after transaction-cost stress, so all ten stay
diagnostic-only pending further research review.
