# Public Alpha101 Panel Batch07 Intake Audit - 2026-06-28

## Scope

This batch adds 10 public WorldQuant 101 Alpha panel factors that share
OHLCV/VWAP/ADV inputs and nested rank/correlation/time-series rank/linear-decay
operators. The batch avoids industry neutralization, market cap, taker,
funding, and live-production dependencies:

- `wq101_alpha77`
- `wq101_alpha78`
- `wq101_alpha83`
- `wq101_alpha85`
- `wq101_alpha86`
- `wq101_alpha88`
- `wq101_alpha92`
- `wq101_alpha94`
- `wq101_alpha95`
- `wq101_alpha99`

Source reference: Kakushadze, "101 Formulaic Alphas"
(`https://arxiv.org/pdf/1601.00991`).

Guardrails:

- Registry remains the only factor-definition entry point.
- WQ101 `rank` is implemented as panel, per-timestamp cross-sectional logic.
- `ts_rank` remains per-symbol rolling time-series rank.
- VWAP maps to `quote_volume / volume` from canonical bars.
- ADV maps to rolling mean `volume` over the published window length.
- Decimal WQ101 windows are mapped to the nearest integer, consistent with the
  previous public Alpha101 panel batches in this repo.
- `decay_linear_wide` was added as a reusable panel operator and implemented
  with numpy sliding windows for resource control.
- No signal panel, trading, execution, broker, or live-production code changed.
- Generated HTML was rebuilt by workflow, not edited by hand.
- No new workflow or `*_v2.py` script was added.
- All factors are diagnostic research assets only.

## Formula Mapping

| factor_id | WQ101 formula shape | required inputs | scope | lookback | direction |
| --- | --- | --- | --- | --- | --- |
| `wq101_alpha77` | `min(rank(decay_linear(mid-vwap,20)), rank(decay_linear(corr(mid,adv40,3),6)))` | `high`, `low`, `volume`, `quote_volume` | panel | 47 | conditional |
| `wq101_alpha78` | `rank(corr(sum(low/vwap blend,20),sum(adv40,20),7))^rank(corr(rank(vwap),rank(volume),6))` | `low`, `volume`, `quote_volume` | panel | 65 | conditional |
| `wq101_alpha83` | `rank(delay((high-low)/(sum(close,5)/5),2))*rank(rank(volume))/(((high-low)/(sum(close,5)/5))/(vwap-close))` | `high`, `low`, `close`, `volume`, `quote_volume` | panel | 7 | conditional |
| `wq101_alpha85` | `rank(corr(high/close blend,adv30,10))^rank(corr(ts_rank(mid,4),ts_rank(volume,10),7))` | `high`, `low`, `close`, `volume` | panel | 39 | conditional |
| `wq101_alpha86` | `-1*(ts_rank(corr(close,sum(adv20,15),6),20)<rank(close-vwap))` | `open`, `close`, `volume`, `quote_volume` | panel | 58 | conditional |
| `wq101_alpha88` | `min(rank(decay_linear(rank(open)+rank(low)-rank(high)-rank(close),8)), ts_rank(decay_linear(corr(ts_rank(close,8),ts_rank(adv60,21),8),7),3))` | `open`, `high`, `low`, `close`, `volume` | panel | 95 | conditional |
| `wq101_alpha92` | `min(ts_rank(decay_linear(mid+close<low+open,15),19), ts_rank(decay_linear(corr(rank(low),rank(adv30),8),7),7))` | `open`, `high`, `low`, `close`, `volume` | panel | 49 | conditional |
| `wq101_alpha94` | `-rank(vwap-ts_min(vwap,12))^ts_rank(corr(ts_rank(vwap,20),ts_rank(adv60,4),18),3)` | `volume`, `quote_volume` | panel | 82 | conditional |
| `wq101_alpha95` | `rank(open-ts_min(open,12))<ts_rank(rank(corr(sum(mid,19),sum(adv40,19),13))^5,12)` | `open`, `high`, `low`, `volume` | panel | 81 | conditional |
| `wq101_alpha99` | `-1*(rank(corr(sum(mid,20),sum(adv60,20),9))<rank(corr(low,volume,6)))` | `high`, `low`, `volume` | panel | 87 | conditional |

## Workflow / Resource Notes

This batch extends `scripts/alpha101_panel_ops.py` with `decay_linear_wide` and
ten panel compute functions. The first build attempt showed the original
rolling-apply implementation was too slow for the 15GB resource envelope, so
`decay_linear_wide` and `ts_rank_wide` were optimized to numpy sliding-window
implementations before final factor-value generation.

Observed full post-intake costs:

- Factor-value generation for 10 panel factors completed successfully.
- Intake run completed in 269s.
- Incremental PM-18 redundancy matrix: 2,085 new pairs, 22,791 merged pairs,
  214 factors, 108 clusters, 497.2s.
- Direction-aware decile diagnostics: 161.6s.
- Capacity/liquidity diagnostics: 170.1s.
- Full post-intake workflow completion: 1,311.8s.

Coverage reflects nested ADV/correlation/decay/time-series-rank warmups and
branch overlap. `wq101_alpha92` is intentionally sparse under the current
one-hour crypto panel because its decayed boolean candle branch and ADV
correlation branch both need valid overlapping windows.

## Validation

Commands run:

```bash
.venv/bin/python -m pytest tests/unit/test_public_alpha101_panel_batch07.py tests/unit/test_public_factor_candidate_manifest.py -q
.venv/bin/python scripts/check_factor_registry_integrity.py
.venv/bin/python scripts/build_factor_values.py --factor-ids wq101_alpha77,wq101_alpha78,wq101_alpha83,wq101_alpha85,wq101_alpha86,wq101_alpha88,wq101_alpha92,wq101_alpha94,wq101_alpha95,wq101_alpha99
.venv/bin/python scripts/run_factor_intake.py --factor-ids wq101_alpha77 wq101_alpha78 wq101_alpha83 wq101_alpha85 wq101_alpha86 wq101_alpha88 wq101_alpha92 wq101_alpha94 wq101_alpha95 wq101_alpha99 --run-id public_alpha101_panel_batch07_20260628 --skip-build-values --skip-redundancy
.venv/bin/python scripts/build_factor_bilingual_cards.py
.venv/bin/python scripts/run_post_intake_workflow_completion.py --factor-ids wq101_alpha77,wq101_alpha78,wq101_alpha83,wq101_alpha85,wq101_alpha86,wq101_alpha88,wq101_alpha92,wq101_alpha94,wq101_alpha95,wq101_alpha99
```

Results:

- Factor values computed for all 10 factors.
- Final coverage: `wq101_alpha77` 99.399%, `wq101_alpha78` 72.879%,
  `wq101_alpha83` 99.993%, `wq101_alpha85` 99.509%,
  `wq101_alpha86` 99.558%, `wq101_alpha88` 65.370%,
  `wq101_alpha92` 20.630%, `wq101_alpha94` 92.023%,
  `wq101_alpha95` 99.398%, `wq101_alpha99` 99.346%.
- Intake run `public_alpha101_panel_batch07_20260628`: COMPLETE.
- Intake conclusion cards: 10 `CONDITIONAL_DIRECTION_REVIEW`.
- Post-intake state: 214 registered, 214 computed, 0 missing factor values,
  0 missing inputs.
- Factor evaluation page QA: 112 PASS / 0 FAIL.
- Post-intake integrity QA for the 10 new factors: 230 PASS / 0 FAIL /
  10 WARN.
- Public manifest status after refresh: Alpha101 59 total,
  53 accounted/non-skipped, 6 skipped taxonomy-blocked; Alpha158 101 total,
  95 accounted/non-skipped, 6 skipped duplicates.

The warnings are optional overlapping-sleeve diagnostics, not missing factor
values, missing source metadata, page coverage failures, or core workflow
failures. `wq101_alpha92` also appears as a naive-only RankIC example in the
robust-significance layer, so it remains diagnostic-only pending further
research review.
