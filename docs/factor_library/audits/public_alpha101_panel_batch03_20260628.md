# Public Alpha101 Panel Batch03 Intake Audit - 2026-06-28

## Scope

This batch adds 6 public WorldQuant 101 Alpha factors that require
cross-sectional `rank` or `scale` semantics but only use canonical OHLCV/VWAP
inputs:

- `wq101_alpha32`
- `wq101_alpha33`
- `wq101_alpha37`
- `wq101_alpha38`
- `wq101_alpha44`
- `wq101_alpha45`

Source reference: Kakushadze, "101 Formulaic Alphas"
(`https://arxiv.org/pdf/1601.00991`).

Guardrails:

- Registry remains the only factor-definition entry point.
- WQ101 `rank`/`scale` is implemented as panel, per-timestamp
  cross-sectional logic, not rewritten as single-symbol rolling rank.
- No signal panel, trading, execution, broker, or live-production code changed.
- Generated HTML was rebuilt by workflow, not edited by hand.
- No new workflow or `*_v2.py` script was added.
- All factors are diagnostic research assets only.

## Formula Mapping

| factor_id | WQ101 formula shape | required inputs | scope | lookback | direction |
| --- | --- | --- | --- | --- | --- |
| `wq101_alpha32` | `scale(mean(close,7)-close)+20*scale(corr(vwap,delay(close,5),230))` | `close`, `volume`, `quote_volume` | panel | 235 | conditional |
| `wq101_alpha33` | `rank(-1*(1-open/close))` | `open`, `close` | panel | 1 | conditional |
| `wq101_alpha37` | `rank(corr(delay(open-close,1),close,200))+rank(open-close)` | `open`, `close` | panel | 201 | conditional |
| `wq101_alpha38` | `-rank(ts_rank(close,10))*rank(close/open)` | `open`, `close` | panel | 10 | conditional |
| `wq101_alpha44` | `-corr(high,rank(volume),5)` | `high`, `volume` | panel | 5 | conditional |
| `wq101_alpha45` | `-rank(mean(delay(close,5),20))*corr(close,volume,2)*rank(corr(sum(close,5),sum(close,20),2))` | `close`, `volume` | panel | 25 | conditional |

VWAP maps to `quote_volume / volume` from canonical bars. No taxonomy, cap,
taker, funding, or industry-neutralization input is required.

## Workflow / Resource Notes

The batch uses reusable panel helpers in `scripts/alpha101_panel_ops.py`:
`xs_rank`, `xs_scale`, `rolling_corr_wide`, `rolling_sum_wide`, and
`ts_rank_wide`.

During the first build pass, multi-panel factor output exposed a scaling issue:
`build_factor_values.py` concatenated panel outputs vertically, creating
duplicate `timestamp,symbol` rows and inflated parquet files. The workflow now
uses `combine_factor_parts()` to merge outputs by `timestamp,symbol` before
writing per-factor parquet files. This keeps multi-factor panel batches resource
controlled and is covered by unit tests.

Observed full post-intake costs:

- Factor-value generation for 6 panel factors: completed successfully.
- Incremental PM-18 redundancy matrix: ~428s for 1,095 new pairs, 186 factors.
- Decile diagnostics: ~135s.
- Capacity/liquidity diagnostics: ~120s.

The redundancy stage remains the main scaling bottleneck for larger future
Alpha101 batches.

## Validation

Commands run:

```bash
.venv/bin/python -m pytest tests/unit/test_public_alpha101_panel_batch03.py tests/unit/test_public_factor_candidate_manifest.py -q
.venv/bin/python scripts/check_factor_registry_integrity.py
.venv/bin/python scripts/build_factor_values.py --factor-ids wq101_alpha32,wq101_alpha33,wq101_alpha37,wq101_alpha38,wq101_alpha44,wq101_alpha45
.venv/bin/python scripts/run_factor_intake.py --factor-ids wq101_alpha32 wq101_alpha33 wq101_alpha37 wq101_alpha38 wq101_alpha44 wq101_alpha45 --run-id public_alpha101_panel_batch03_20260628_rerun --skip-build-values --skip-redundancy
.venv/bin/python scripts/build_factor_bilingual_cards.py
.venv/bin/python scripts/run_post_intake_workflow_completion.py --factor-ids wq101_alpha32,wq101_alpha33,wq101_alpha37,wq101_alpha38,wq101_alpha44,wq101_alpha45
.venv/bin/python scripts/run_post_intake_workflow_completion.py --factor-ids wq101_alpha32,wq101_alpha33,wq101_alpha37,wq101_alpha38,wq101_alpha44,wq101_alpha45 --start-from scorecard
.venv/bin/python scripts/check_public_factor_integration_status.py
```

Results:

- Factor values computed for all 6 factors.
- Final factor-value rows per factor: 3,316,259.
- Coverage: `wq101_alpha32` 97.829%, `wq101_alpha33` 100.000%,
  `wq101_alpha37` 98.127%, `wq101_alpha38` 99.927%,
  `wq101_alpha44` 98.883%, `wq101_alpha45` 99.311%.
- Post-intake state: 186 registered, 186 computed, 0 missing factor values,
  0 missing inputs.
- Factor evaluation page QA: 112 PASS / 0 FAIL.
- Post-intake integrity QA for the 6 new factors: 138 PASS / 0 FAIL /
  6 WARN.
- Public manifest status after refresh: Alpha101 31 total,
  25 accounted/non-skipped, 6 skipped taxonomy-blocked; Alpha158 101 total,
  95 accounted/non-skipped, 6 skipped duplicates.

The warnings are optional overlapping-sleeve diagnostics, not missing factor
values, missing source metadata, page coverage failures, or core workflow
failures.
