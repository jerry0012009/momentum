# Public Alpha101 Panel Batch05 Intake Audit - 2026-06-28

## Scope

This batch adds 6 public WorldQuant 101 Alpha panel factors that share
OHLCV/VWAP/ADV inputs and avoid industry neutralization, market cap, taker,
funding, and decay-linear dependencies:

- `wq101_alpha25`
- `wq101_alpha28`
- `wq101_alpha30`
- `wq101_alpha35`
- `wq101_alpha43`
- `wq101_alpha52`

Source reference: Kakushadze, "101 Formulaic Alphas"
(`https://arxiv.org/pdf/1601.00991`).

Guardrails:

- Registry remains the only factor-definition entry point.
- WQ101 `rank`/`scale` is implemented as panel, per-timestamp
  cross-sectional logic.
- `ts_rank` remains per-symbol rolling time-series rank.
- VWAP maps to `quote_volume / volume` from canonical bars.
- ADV maps to rolling mean `volume` over the published window length.
- No signal panel, trading, execution, broker, or live-production code changed.
- Generated HTML was rebuilt by workflow, not edited by hand.
- No new workflow or `*_v2.py` script was added.
- All factors are diagnostic research assets only.

## Formula Mapping

| factor_id | WQ101 formula shape | required inputs | scope | lookback | direction |
| --- | --- | --- | --- | --- | --- |
| `wq101_alpha25` | `rank((-returns*adv20*vwap)*(high-close))` | `high`, `close`, `volume`, `quote_volume` | panel | 20 | conditional |
| `wq101_alpha28` | `scale(corr(adv20,low,5)+((high+low)/2)-close)` | `high`, `low`, `close`, `volume` | panel | 24 | conditional |
| `wq101_alpha30` | `(1-rank(sign(delta(close))+sign(delay(delta(close),1))+sign(delay(delta(close),2))))*sum(volume,5)/sum(volume,20)` | `close`, `volume` | panel | 20 | conditional |
| `wq101_alpha35` | `ts_rank(volume,32)*(1-ts_rank(close+high-low,16))*(1-ts_rank(returns,32))` | `high`, `low`, `close`, `volume` | panel | 33 | conditional |
| `wq101_alpha43` | `ts_rank(volume/adv20,20)*ts_rank(-delta(close,7),8)` | `close`, `volume` | panel | 39 | conditional |
| `wq101_alpha52` | `-delta(ts_min(low,5),5)*rank((sum(returns,240)-sum(returns,20))/220)*ts_rank(volume,5)` | `low`, `close`, `volume` | panel | 241 | conditional |

## Workflow / Resource Notes

This batch extends `scripts/alpha101_panel_ops.py` with six panel compute
functions and one reusable `rolling_idxmin_wide` helper for future
argmin-style WQ101 formulas. The helper follows the existing local convention
for rolling extrema positions: bars since the latest extremum inside the
lookback window.

Observed full post-intake costs:

- Factor-value generation for 6 panel factors completed successfully.
- Incremental PM-18 redundancy matrix: ~456s for 1,167 new pairs, 198 factors.
- Decile diagnostics: ~134s.
- Capacity/liquidity diagnostics: ~118s.
- Full post-intake workflow completion: ~1,078s.

`wq101_alpha52` has the longest warmup in this batch because it uses a 240-bar
return-sum window plus return construction. Coverage remained above 98%.
Redundancy remains the main scaling bottleneck for larger future Alpha101
batches.

## Validation

Commands run:

```bash
.venv/bin/python -m pytest tests/unit/test_public_alpha101_panel_batch05.py tests/unit/test_public_factor_candidate_manifest.py -q
.venv/bin/python scripts/check_factor_registry_integrity.py
.venv/bin/python scripts/build_factor_values.py --factor-ids wq101_alpha25,wq101_alpha28,wq101_alpha30,wq101_alpha35,wq101_alpha43,wq101_alpha52
.venv/bin/python scripts/run_factor_intake.py --factor-ids wq101_alpha25 wq101_alpha28 wq101_alpha30 wq101_alpha35 wq101_alpha43 wq101_alpha52 --run-id public_alpha101_panel_batch05_20260628 --skip-build-values --skip-redundancy
.venv/bin/python scripts/build_factor_bilingual_cards.py
.venv/bin/python scripts/run_post_intake_workflow_completion.py --factor-ids wq101_alpha25,wq101_alpha28,wq101_alpha30,wq101_alpha35,wq101_alpha43,wq101_alpha52
```

Results:

- Factor values computed for all 6 factors.
- Final factor-value rows per factor: 3,311,148.
- Coverage: `wq101_alpha25` 99.727%, `wq101_alpha28` 99.687%,
  `wq101_alpha30` 99.732%, `wq101_alpha35` 99.894%,
  `wq101_alpha43` 99.578%, `wq101_alpha52` 98.205%.
- Intake run `public_alpha101_panel_batch05_20260628`: COMPLETE.
- Intake conclusion cards: 6 `CONDITIONAL_DIRECTION_REVIEW`.
- Post-intake state: 198 registered, 198 computed, 0 missing factor values,
  0 missing inputs.
- Factor evaluation page QA: 112 PASS / 0 FAIL.
- Post-intake integrity QA for the 6 new factors: 138 PASS / 0 FAIL /
  6 WARN.
- Public manifest status after refresh: Alpha101 43 total,
  37 accounted/non-skipped, 6 skipped taxonomy-blocked; Alpha158 101 total,
  95 accounted/non-skipped, 6 skipped duplicates.

The warnings are optional overlapping-sleeve diagnostics, not missing factor
values, missing source metadata, page coverage failures, or core workflow
failures.
