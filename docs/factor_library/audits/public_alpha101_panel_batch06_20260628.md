# Public Alpha101 Panel Batch06 Intake Audit - 2026-06-28

## Scope

This batch adds 6 public WorldQuant 101 Alpha panel factors that share
OHLCV/VWAP/ADV inputs, nested rolling correlation/rank operators, and boolean
comparison-style formula outputs. The batch avoids industry neutralization,
market cap, taker, funding, and decay-linear dependencies:

- `wq101_alpha47`
- `wq101_alpha61`
- `wq101_alpha65`
- `wq101_alpha68`
- `wq101_alpha74`
- `wq101_alpha75`

Source reference: Kakushadze, "101 Formulaic Alphas"
(`https://arxiv.org/pdf/1601.00991`).

Guardrails:

- Registry remains the only factor-definition entry point.
- WQ101 `rank` is implemented as panel, per-timestamp cross-sectional logic.
- `ts_rank` remains per-symbol rolling time-series rank.
- VWAP maps to `quote_volume / volume` from canonical bars.
- ADV maps to rolling mean `volume` over the published window length.
- Boolean comparison formulas emit numeric diagnostic values so they can pass
  the existing factor-value and evaluation contracts.
- No signal panel, trading, execution, broker, or live-production code changed.
- Generated HTML was rebuilt by workflow, not edited by hand.
- No new workflow or `*_v2.py` script was added.
- All factors are diagnostic research assets only.

## Formula Mapping

| factor_id | WQ101 formula shape | required inputs | scope | lookback | direction |
| --- | --- | --- | --- | --- | --- |
| `wq101_alpha47` | `rank(1/close)*volume/adv20*high*rank(high-close)/(sum(high,5)/5)-rank(vwap-delay(vwap,5))` | `high`, `close`, `volume`, `quote_volume` | panel | 20 | conditional |
| `wq101_alpha61` | `rank(vwap-ts_min(vwap,16))<rank(correlation(vwap,adv180,18))` | `volume`, `quote_volume` | panel | 197 | conditional |
| `wq101_alpha65` | `-1*(rank(correlation(0.00817205*open+0.99182795*vwap,sum(adv60,9),6))<rank(open-ts_min(open,14)))` | `open`, `volume`, `quote_volume` | panel | 73 | conditional |
| `wq101_alpha68` | `-1*(ts_rank(correlation(rank(high),rank(adv15),9),14)<rank(delta(0.518371*close+0.481629*low,1)))` | `high`, `low`, `close`, `volume` | panel | 37 | conditional |
| `wq101_alpha74` | `-1*(rank(correlation(close,sum(adv30,37),15))<rank(correlation(rank(0.0261661*high+0.9738339*vwap),rank(volume),11)))` | `high`, `close`, `volume`, `quote_volume` | panel | 80 | conditional |
| `wq101_alpha75` | `rank(correlation(vwap,volume,4))<rank(correlation(rank(low),rank(adv50),12))` | `low`, `volume`, `quote_volume` | panel | 61 | conditional |

## Workflow / Resource Notes

This batch extends `scripts/alpha101_panel_ops.py` with six panel compute
functions. The implemented formulas intentionally preserve WQ101 comparison
semantics for `alpha61`, `alpha65`, `alpha68`, `alpha74`, and `alpha75`; these
are not max/min formulas. `wq101_alpha75` also aligns the left and right
comparison inputs before evaluating the boolean panel expression, because the
two correlation branches can produce different valid index coverage.

Observed full post-intake costs:

- Factor-value generation for 6 panel factors completed successfully.
- Incremental PM-18 redundancy matrix: 20,706 pairs over 204 factors.
- Full post-intake workflow completion: ~979s.

Coverage reflects the long ADV/correlation warmups and boolean branch overlap.
`wq101_alpha68` has intentionally low coverage because its nested
cross-sectional rank, rolling correlation, and `ts_rank` branch is sparse under
the current one-hour crypto panel after validity filtering.

## Validation

Commands run:

```bash
.venv/bin/python -m pytest tests/unit/test_public_alpha101_panel_batch06.py tests/unit/test_public_factor_candidate_manifest.py -q
.venv/bin/python scripts/check_factor_registry_integrity.py
.venv/bin/python scripts/build_factor_values.py --factor-ids wq101_alpha47,wq101_alpha61,wq101_alpha65,wq101_alpha68,wq101_alpha74
.venv/bin/python scripts/build_factor_values.py --factor-ids wq101_alpha75
.venv/bin/python scripts/run_factor_intake.py --factor-ids wq101_alpha47 wq101_alpha61 wq101_alpha65 wq101_alpha68 wq101_alpha74 wq101_alpha75 --run-id public_alpha101_panel_batch06_20260628 --skip-build-values --skip-redundancy
.venv/bin/python scripts/build_factor_bilingual_cards.py
.venv/bin/python scripts/run_post_intake_workflow_completion.py --factor-ids wq101_alpha47,wq101_alpha61,wq101_alpha65,wq101_alpha68,wq101_alpha74,wq101_alpha75
```

Results:

- Factor values computed for all 6 factors.
- Final factor-value rows: `wq101_alpha47` 3,302,157, `wq101_alpha61`
  3,302,157, `wq101_alpha65` 3,302,157, `wq101_alpha68` 3,302,157,
  `wq101_alpha74` 3,302,157, `wq101_alpha75` 2,363,750.
- Coverage: `wq101_alpha47` 99.998%, `wq101_alpha61` 98.557%,
  `wq101_alpha65` 99.548%, `wq101_alpha68` 29.286%,
  `wq101_alpha74` 78.344%, `wq101_alpha75` 100.000%.
- Intake run `public_alpha101_panel_batch06_20260628`: COMPLETE.
- Intake conclusion cards: 6 `CONDITIONAL_DIRECTION_REVIEW`.
- Post-intake state: 204 registered, 204 computed, 0 missing factor values,
  0 missing inputs.
- Factor evaluation page QA: 112 PASS / 0 FAIL.
- Post-intake integrity QA for the 6 new factors: 138 PASS / 0 FAIL /
  6 WARN.
- Public manifest status after refresh: Alpha101 49 total,
  43 accounted/non-skipped, 6 skipped taxonomy-blocked; Alpha158 101 total,
  95 accounted/non-skipped, 6 skipped duplicates.

The warnings are optional overlapping-sleeve diagnostics, not missing factor
values, missing source metadata, page coverage failures, or core workflow
failures.
