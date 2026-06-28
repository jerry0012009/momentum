# Public Alpha101 Panel Batch04 Intake Audit - 2026-06-28

## Scope

This batch adds 6 public WorldQuant 101 Alpha panel factors that use
cross-sectional `rank` or `scale` semantics and only require canonical
OHLCV/VWAP inputs:

- `wq101_alpha34`
- `wq101_alpha40`
- `wq101_alpha42`
- `wq101_alpha50`
- `wq101_alpha55`
- `wq101_alpha60`

Source reference: Kakushadze, "101 Formulaic Alphas"
(`https://arxiv.org/pdf/1601.00991`).

Guardrails:

- Registry remains the only factor-definition entry point.
- WQ101 `rank`/`scale` is implemented as panel, per-timestamp
  cross-sectional logic.
- VWAP maps to `quote_volume / volume` from canonical bars.
- No signal panel, trading, execution, broker, or live-production code changed.
- Generated HTML was rebuilt by workflow, not edited by hand.
- No new workflow or `*_v2.py` script was added.
- All factors are diagnostic research assets only.

## Formula Mapping

| factor_id | WQ101 formula shape | required inputs | scope | lookback | direction |
| --- | --- | --- | --- | --- | --- |
| `wq101_alpha34` | `rank((1-rank(std(ret,2)/std(ret,5)))+(1-rank(delta(close,1))))` | `close` | panel | 6 | conditional |
| `wq101_alpha40` | `-rank(stddev(high,10))*corr(high,volume,10)` | `high`, `volume` | panel | 10 | conditional |
| `wq101_alpha42` | `rank(vwap-close)/rank(vwap+close)` | `close`, `volume`, `quote_volume` | panel | 1 | conditional |
| `wq101_alpha50` | `-ts_max(rank(corr(rank(volume),rank(vwap),5)),5)` | `volume`, `quote_volume` | panel | 9 | conditional |
| `wq101_alpha55` | `-corr(rank((close-ts_min(low,12))/(ts_max(high,12)-ts_min(low,12))),rank(volume),6)` | `high`, `low`, `close`, `volume` | panel | 17 | conditional |
| `wq101_alpha60` | `-((2*scale(rank(close-location-volume)))-scale(rank(ts_argmax(close,10))))` | `high`, `low`, `close`, `volume` | panel | 10 | conditional |

No taxonomy, cap, taker, funding, or industry-neutralization input is required.

## Workflow / Resource Notes

This batch extends `scripts/alpha101_panel_ops.py` with reusable panel helpers
for rolling maximum and rolling standard deviation, then implements the six
compute functions above. All six factors run in `compute_scope="panel"` so
their cross-sectional ranks are evaluated across symbols at each timestamp.

Observed full post-intake costs:

- Factor-value generation for 6 panel factors completed successfully.
- Incremental PM-18 redundancy matrix: ~443s for 1,131 new pairs, 192 factors.
- Decile diagnostics: ~134s.
- Capacity/liquidity diagnostics: ~120s.
- Full post-intake workflow completion: ~1,051s.

`wq101_alpha50` has materially lower value coverage than the other five
factors. This is expected from nested cross-sectional rank, rolling
correlation, and rolling maximum windows over VWAP/volume pairs; low-variance
or sparse windows propagate nulls. It is still registered, computed, evaluated,
and displayed with diagnostics.

`wq101_alpha60` uses the local `ts_argmax` convention already present in the
library's rolling-index helpers: position is interpreted as bars since the
latest maximum inside the lookback window. This keeps the panel implementation
consistent with existing factor semantics.

The redundancy stage remains the main scaling bottleneck for larger future
Alpha101 batches.

## Validation

Commands run:

```bash
.venv/bin/python -m pytest tests/unit/test_public_alpha101_panel_batch04.py tests/unit/test_public_alpha101_panel_batch03.py tests/unit/test_public_factor_candidate_manifest.py -q
.venv/bin/python scripts/check_factor_registry_integrity.py
.venv/bin/python scripts/build_factor_values.py --factor-ids wq101_alpha34,wq101_alpha40,wq101_alpha42,wq101_alpha50,wq101_alpha55,wq101_alpha60
.venv/bin/python scripts/run_factor_intake.py --factor-ids wq101_alpha34 wq101_alpha40 wq101_alpha42 wq101_alpha50 wq101_alpha55 wq101_alpha60 --run-id public_alpha101_panel_batch04_20260628 --skip-build-values --skip-redundancy
.venv/bin/python scripts/build_factor_bilingual_cards.py
.venv/bin/python scripts/run_post_intake_workflow_completion.py --factor-ids wq101_alpha34,wq101_alpha40,wq101_alpha42,wq101_alpha50,wq101_alpha55,wq101_alpha60
```

Results:

- Factor values computed for all 6 factors.
- Final factor-value rows per factor: 3,307,368.
- Coverage: `wq101_alpha34` 99.957%, `wq101_alpha40` 99.926%,
  `wq101_alpha42` 99.995%, `wq101_alpha50` 50.440%,
  `wq101_alpha55` 99.477%, `wq101_alpha60` 99.922%.
- Post-intake state: 192 registered, 192 computed, 0 missing factor values,
  0 missing inputs.
- Factor evaluation page QA: 112 PASS / 0 FAIL.
- Post-intake integrity QA for the 6 new factors: 138 PASS / 0 FAIL /
  6 WARN.
- Public manifest status after refresh: Alpha101 37 total,
  31 accounted/non-skipped, 6 skipped taxonomy-blocked; Alpha158 101 total,
  95 accounted/non-skipped, 6 skipped duplicates.

The warnings are optional overlapping-sleeve diagnostics, not missing factor
values, missing source metadata, page coverage failures, or core workflow
failures.
