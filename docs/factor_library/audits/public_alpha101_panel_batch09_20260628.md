# Public Alpha101 Panel Batch09 Intake Audit - 2026-06-28

## Scope

This batch adds 10 public WorldQuant 101 Alpha factors that share
OHLCV/VWAP/returns/ADV/rank/rolling correlation-covariance operators. The
batch uses only canonical bar inputs and avoids industry neutralization, market
cap, taker, funding, and live-production dependencies:

- `wq101_alpha14`
- `wq101_alpha15`
- `wq101_alpha16`
- `wq101_alpha17`
- `wq101_alpha18`
- `wq101_alpha19`
- `wq101_alpha20`
- `wq101_alpha22`
- `wq101_alpha26`
- `wq101_alpha27`

Source reference: Kakushadze, "101 Formulaic Alphas"
(`https://arxiv.org/pdf/1601.00991`).

Guardrails:

- Registry remains the only factor-definition entry point.
- WQ101 `rank` is implemented as panel, per-timestamp cross-sectional logic.
- `ts_rank`, rolling covariance, rolling correlations, and `ts_max` remain
  per-symbol time-series operations.
- VWAP maps to `quote_volume / volume` from canonical bars.
- ADV maps to rolling mean `volume` over the published window length.
- No signal panel, trading, execution, broker, or live-production code changed.
- Generated HTML was rebuilt by workflow, not edited by hand.
- All factors are diagnostic research assets only.

## Formula Mapping

| factor_id | WQ101 formula shape | required inputs | scope | lookback | direction |
| --- | --- | --- | --- | --- | --- |
| `wq101_alpha14` | `-rank(delta(returns,3))*correlation(open,volume,10)` | `open`, `close`, `volume` | panel | 10 | conditional |
| `wq101_alpha15` | `-sum(rank(correlation(rank(high),rank(volume),3)),3)` | `high`, `volume` | panel | 5 | conditional |
| `wq101_alpha16` | `-rank(covariance(rank(high),rank(volume),5))` | `high`, `volume` | panel | 5 | conditional |
| `wq101_alpha17` | `-rank(ts_rank(close,10))*rank(delta(delta(close,1),1))*rank(ts_rank(volume/adv20,5))` | `close`, `volume` | panel | 24 | conditional |
| `wq101_alpha18` | `-rank(stddev(abs(close-open),5)+(close-open)+correlation(close,open,10))` | `open`, `close` | panel | 10 | conditional |
| `wq101_alpha19` | `-sign((close-delay(close,7))+delta(close,7))*(1+rank(1+sum(returns,250)))` | `close` | panel | 251 | conditional |
| `wq101_alpha20` | `-rank(open-delay(high,1))*rank(open-delay(close,1))*rank(open-delay(low,1))` | `open`, `high`, `low`, `close` | panel | 2 | conditional |
| `wq101_alpha22` | `-delta(correlation(high,volume,5),5)*rank(stddev(close,20))` | `high`, `close`, `volume` | panel | 20 | conditional |
| `wq101_alpha26` | `-ts_max(correlation(ts_rank(volume,5),ts_rank(high,5),5),3)` | `high`, `volume` | panel | 11 | conditional |
| `wq101_alpha27` | `where(rank(mean(correlation(rank(volume),rank(vwap),6),2))>0.5,-1,1)` | `volume`, `quote_volume` | panel | 7 | conditional |

## Workflow / Resource Notes

This batch reuses existing panel helpers from `scripts/alpha101_panel_ops.py`.
No new workflow or parallel `*_v2.py` path was added. Tests independently
rebuild the formulas in wide-panel form and check registry metadata, Alpha27's
discrete branch, and per-symbol timestamp isolation.

Observed full post-intake costs:

- Factor-value generation for 10 panel factors completed successfully.
- Intake run `public_alpha101_panel_batch09_20260628` completed in 299s.
- Incremental PM-18 redundancy matrix: 2,285 target pairs, 27,261 merged pairs,
  234 factors, 127 clusters, 548.9s.
- Direction-aware decile diagnostics: 188.6s.
- Capacity/liquidity diagnostics: 176.2s.
- Full post-intake workflow completion: 1,462.3s.

## Validation

Commands run:

```bash
.venv/bin/python -m pytest tests/unit/test_public_alpha101_panel_batch09.py tests/unit/test_public_factor_candidate_manifest.py -q
.venv/bin/python scripts/check_factor_registry_integrity.py
.venv/bin/python scripts/build_factor_values.py --factor-ids wq101_alpha14,wq101_alpha15,wq101_alpha16,wq101_alpha17,wq101_alpha18,wq101_alpha19,wq101_alpha20,wq101_alpha22,wq101_alpha26,wq101_alpha27
.venv/bin/python scripts/run_factor_intake.py --factor-ids wq101_alpha14 wq101_alpha15 wq101_alpha16 wq101_alpha17 wq101_alpha18 wq101_alpha19 wq101_alpha20 wq101_alpha22 wq101_alpha26 wq101_alpha27 --run-id public_alpha101_panel_batch09_20260628 --skip-build-values --skip-redundancy
.venv/bin/python scripts/build_factor_bilingual_cards.py
.venv/bin/python scripts/run_post_intake_workflow_completion.py --factor-ids wq101_alpha14,wq101_alpha15,wq101_alpha16,wq101_alpha17,wq101_alpha18,wq101_alpha19,wq101_alpha20,wq101_alpha22,wq101_alpha26,wq101_alpha27
```

Results:

- Factor values computed for all 10 factors.
- Final coverage: `wq101_alpha14` 99.667%, `wq101_alpha15` 80.459%,
  `wq101_alpha16` 99.976%, `wq101_alpha17` 99.554%,
  `wq101_alpha18` 99.667%, `wq101_alpha19` 97.980%,
  `wq101_alpha20` 100.000%, `wq101_alpha22` 99.579%,
  `wq101_alpha26` 90.881%, `wq101_alpha27` 40.295%.
- Intake run `public_alpha101_panel_batch09_20260628`: COMPLETE.
- Intake conclusion cards: 10 `CONDITIONAL_DIRECTION_REVIEW`.
- Post-intake state: 234 registered, 234 computed, 0 missing factor values,
  0 missing inputs.
- `reports/site/factor-library/assets/factor_evaluation.json`: 234 factors,
  including all batch09 factors.
- Factor evaluation page QA: 112 PASS / 0 FAIL.
- Post-intake integrity QA for the 10 new factors: 230 PASS / 0 FAIL /
  10 WARN.
- Public manifest status after refresh: Alpha101 79 total,
  73 accounted/non-skipped, 6 skipped taxonomy-blocked; Alpha158 101 total,
  95 accounted/non-skipped, 6 skipped duplicates.

The warnings are optional overlapping-sleeve diagnostics, not missing factor
values, missing source metadata, page coverage failures, or core workflow
failures. Cost stress diagnostics remain harsh for this batch, so all ten stay
diagnostic-only pending further research review.
