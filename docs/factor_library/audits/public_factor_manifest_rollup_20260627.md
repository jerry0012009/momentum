# Public Alpha101 / Alpha158 Manifest Rollup - 2026-06-29

## Scope

This audit records the current controlled public-factor intake state for the
compact manifest:

- `docs/factor_library/public_factor_candidate_manifest.csv`
- 95 implemented Alpha158 factors from Qlib Alpha158DL formula families and
  existing local Alpha158 support.
- 6 skipped Alpha158 duplicate dispositions with explicit skip reasons.
- 88 implemented WorldQuant Alpha101 factors, including existing `wq101_*`
  backfills, OHLCV/panel batches, and the market-cap-supported Alpha56 row.
- 18 skipped WorldQuant 101 formulas blocked by missing reviewed
  industry/sector/subindustry neutralization inputs.
- 1 skipped WorldQuant 101 formula blocked by low current crypto coverage.

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
| alpha158 | 95 | 6 | 101 |
| alpha101 | 88 | 19 | 107 |
| total | 183 | 25 | 208 |

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
They are blocked until the project has an approved crypto sector/industry/
subindustry taxonomy and reusable neutralization operator. The data-source and
operator requirements are now recorded in
`docs/factor_library/INDUSTRY_NEUTRALIZATION_DATA_CONTRACT.md`:

- `wq101_alpha58_indneutralize_skipped`
- `wq101_alpha59_indneutralize_skipped`
- `wq101_alpha67_indneutralize_skipped`
- `wq101_alpha69_indneutralize_skipped`
- `wq101_alpha70_indneutralize_skipped`
- `wq101_alpha93_indneutralize_skipped`
- `wq101_alpha48_indneutralize_skipped`
- `wq101_alpha63_indneutralize_skipped`
- `wq101_alpha76_indneutralize_skipped`
- `wq101_alpha79_indneutralize_skipped`
- `wq101_alpha80_indneutralize_skipped`
- `wq101_alpha82_indneutralize_skipped`
- `wq101_alpha87_indneutralize_skipped`
- `wq101_alpha89_indneutralize_skipped`
- `wq101_alpha90_indneutralize_skipped`
- `wq101_alpha91_indneutralize_skipped`
- `wq101_alpha97_indneutralize_skipped`
- `wq101_alpha100_indneutralize_skipped`

These rows are sourced from the 101 Formulaic Alphas definitions and the
DolphinDB WQ101 classification of formulas that require industry information.
No ad hoc crypto bucket proxy was introduced.

The `skipped_low_coverage_20260628` row is:

- `wq101_alpha96_low_coverage_skipped`

It remains skipped because the current crypto data coverage is too low for a
defensible implementation.

## Current Workflow Evidence

State refresh command:

```bash
python scripts/build_factor_library_state.py
```

Result:

- Registered factors: 249
- Computed factor_values: 249
- Missing factor_values: 0
- Missing input data: 0
- Warnings: 0

Full active-universe integrity command:

```bash
python scripts/check_post_intake_workflow_integrity.py --all-active --output-dir /tmp/public_factor_integrity_audit
```

Result:

- Factors checked: 249
- Total checks: 5976
- PASS: 5777
- FAIL: 0
- WARN: 199
- Active-universe consistency: PASS, 14/14 tables at 249/249.
- PM-58A LS monthly aggregate: PASS.
- PM-58B LS annualization consistency: PASS.
- PM-58C window diagnostics: PASS.

The warnings are optional PM-59A overlapping-sleeve summaries missing for
eligible diagnostic factors. They do not indicate missing factor_values,
factor-level evaluation, source metadata, robust RankIC/LS diagnostics, page
coverage, or post-intake core diagnostics.

Page completeness command:

```bash
python scripts/check_factor_evaluation_page_completeness.py
```

Result:

- Total checks: 115
- PASS: 115
- FAIL: 0

Latest page/state evidence:

- Factor evaluation page factor count: 249.
- Workflow-ready factors: 249.
- Evidence status: 243 `COMPLETE`, 6 `COMPLETE_WITH_WARNINGS`.
- Public source-family payload count: `alpha101=88`, `alpha158=95`.
- Redundancy clusters: 142.

## Guardrails Confirmed

- `docs/factor_library/START_HERE.md` remains the public development entry point.
- `scripts/factor_formula_registry.py` remains the factor definition entry point.
- No signal panel factor list was changed for these public-factor intake checks.
- No trading, broker, exchange, execution, production, or live-trading code was
  changed.
- Generated factor-library HTML was not hand-edited.
- Public factors remain diagnostic research assets only.

## Next Batch Guidance

Future Alpha101 / Alpha158 additions should be grouped by formula/data-source
similarity and remain resource-aware. Batches of roughly 8-12 Alpha101 factors
are acceptable when they share inputs/operators; each batch still needs manifest
rows first, then intake, post-intake, all-active integrity, page QA, redundancy
diagnostics, and a functional commit.

For the remaining Alpha101 `IndNeutralize(..., IndClass.*)` formulas, the next
valid step is not formula registration. First satisfy the industry
neutralization data contract with reviewed point-in-time sector, industry, and
subindustry membership plus one reusable panel neutralization operator.
