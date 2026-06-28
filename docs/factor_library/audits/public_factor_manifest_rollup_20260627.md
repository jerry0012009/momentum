# Public Alpha101 / Alpha158 Manifest Rollup - 2026-06-27

## Scope

This audit records the current controlled public-factor intake state for the
compact manifest:

- `docs/factor_library/public_factor_candidate_manifest.csv`
- 91 implemented Alpha158 factors from Qlib Alpha158DL formula families and
  existing local Alpha158 support.
- 6 skipped Alpha158 duplicate dispositions with explicit skip reasons.
- 6 curated Alpha101 panel factors from the local Alpha101 migration layer.
- 3 existing WorldQuant 101 proxy factors already registered as `wq101_*`.
- 6 skipped WorldQuant 101 formulas blocked by missing equity
  industry/sector-neutralization inputs.

The manifest is the expansion checklist. The registry remains the only factor
definition entry point.

## Manifest Coverage

The compact manifest now records, for every candidate:

- formula source
- exact formula
- required columns
- required reusable operators
- compute scope (`single_symbol` or `panel`)
- timeframe mapping
- lookback
- expected direction
- implementation status
- skip reason when blocked

Current manifest row counts:

| source_family | implemented rows | skipped rows | total rows |
| --- | ---: | ---: | ---: |
| alpha158 | 91 | 6 | 97 |
| alpha101 | 9 | 6 | 15 |
| total | 100 | 12 | 112 |

The `existing_support_backfill_20260627` rows are metadata backfills for factors
that were already registered and computed before the public manifest existed:

- `q158_high_low_range`
- `wq101_alpha101`
- `wq101_alpha12`
- `wq101_alpha53`

The `existing_alpha158_family_backfill_20260627` rows are metadata backfills
for already registered and computed factors whose registry families are
Alpha158-derived but whose factor IDs predated the `q158_` prefix convention:

- `vwap_dev_20h`
- `wvma_20h`
- `vol_ret_corr_20h`
- `intraday_ret`
- `klow_close`
- `ksft_5h`
- `up_down_vol_ratio_20h`
- `clv_20h`

The `skipped_duplicate_20260627` rows are explicit no-implementation
dispositions. They keep the public candidate checklist auditable without adding
parallel aliases for formulas already covered by registered factors:

- `q158_roc_5h_skipped` duplicates `mom_5h` horizon coverage.
- `q158_roc_10h_skipped` duplicates `mom_10h` horizon coverage.
- `q158_roc_72h_skipped` duplicates `mom_72h` horizon coverage.
- `q158_roc_120h_skipped` duplicates `mom_120h` horizon coverage.
- `q158_ksft_20h_skipped` duplicates `realized_skew_20h`.
- `q158_volume_xs_rank_skipped` duplicates `xs_rank_vol`.

Skipped rows are not registry entries and are intentionally excluded from
factor-value and post-intake integrity factor ID lists.

The `skipped_missing_industry_neutralization_20260627` rows are Alpha101
formulas whose published definitions require `IndNeutralize(..., IndClass.*)`.
They are blocked until the project has an approved crypto sector/industry
taxonomy and reusable neutralization operator:

- `wq101_alpha58_indneutralize_skipped`
- `wq101_alpha59_indneutralize_skipped`
- `wq101_alpha67_indneutralize_skipped`
- `wq101_alpha69_indneutralize_skipped`
- `wq101_alpha70_indneutralize_skipped`
- `wq101_alpha93_indneutralize_skipped`

These rows are sourced from the 101 Formulaic Alphas definitions and the
DolphinDB WQ101 classification of formulas that require industry information.
No ad hoc crypto bucket proxy was introduced.

## Current Workflow Evidence

State refresh command:

```bash
python scripts/build_factor_library_state.py
```

Result:

- Registered factors: 166
- Computed factor_values: 166
- Missing factor_values: 0
- Missing input data: 0
- Warnings: 0

Full public-manifest integrity command:

```bash
python scripts/check_post_intake_workflow_integrity.py --factor-ids <100 implemented public manifest factor IDs>
```

Result:

- Factors checked: 100
- Total checks: 2400
- PASS: 2305
- FAIL: 0
- WARN: 95

The warnings are optional PM-59A overlapping-sleeve summaries missing for
eligible diagnostic factors. They do not indicate missing factor_values,
factor-level evaluation, source metadata, robust RankIC/LS diagnostics, page
coverage, or post-intake core diagnostics.

Page completeness command:

```bash
python scripts/check_factor_evaluation_page_completeness.py
```

Result:

- Total checks: 108
- PASS: 108
- FAIL: 0

## Guardrails Confirmed

- `docs/factor_library/START_HERE.md` remains the public development entry point.
- `scripts/factor_formula_registry.py` remains the factor definition entry point.
- No signal panel factor list was changed for these public-factor intake checks.
- No trading, broker, exchange, execution, production, or live-trading code was
  changed.
- Generated factor-library HTML was not hand-edited.
- Public factors remain diagnostic research assets only.

## Next Batch Guidance

Future Alpha101 / Alpha158 additions should stay small. Prefer 4-6 factors per
batch, run only missing or named-factor workflow steps, and require one manifest
row per candidate before implementation. If a formula needs a new operator, add
one reusable operator in the existing operator layer and keep using the existing
intake and post-intake workflow.
