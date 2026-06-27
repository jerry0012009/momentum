# Public Alpha101 / Alpha158 Manifest Rollup - 2026-06-27

## Scope

This audit records the current controlled public-factor intake state for the
compact manifest:

- `docs/factor_library/public_factor_candidate_manifest.csv`
- 45 Alpha158 factors from Qlib Alpha158DL formula families and existing local
  Alpha158 support.
- 6 curated Alpha101 panel factors from the local Alpha101 migration layer.
- 3 existing WorldQuant 101 proxy factors already registered as `wq101_*`.

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

| source_family | rows |
| --- | ---: |
| alpha158 | 45 |
| alpha101 | 9 |
| total | 54 |

The `existing_support_backfill_20260627` rows are metadata backfills for factors
that were already registered and computed before the public manifest existed:

- `q158_high_low_range`
- `wq101_alpha101`
- `wq101_alpha12`
- `wq101_alpha53`

## Current Workflow Evidence

State refresh command:

```bash
python scripts/build_factor_library_state.py
```

Result:

- Registered factors: 128
- Computed factor_values: 128
- Missing factor_values: 0
- Missing input data: 0
- Warnings: 0

Full public-manifest integrity command:

```bash
python scripts/check_post_intake_workflow_integrity.py --factor-ids q158_high_low_range,wq101_alpha101,wq101_alpha12,wq101_alpha53,q158_klen_open,q158_kup_open,q158_klow_open,q158_ksft_open,q158_ksft_range,q158_rsv_20h,q158_qtlu_20h,q158_qtld_20h,q158_rank_close_20h,q158_cntp_20h,q158_cntn_20h,q158_sumd_20h,q158_beta_20h,q158_rsqr_20h,q158_resi_20h,q158_imax_20h,q158_imin_20h,q158_imxd_20h,q158_roc_20h,q158_ma_20h,q158_std_20h,q158_max_20h,q158_min_20h,q158_cntd_20h,q158_corr_20h,q158_cord_20h,q158_sump_20h,q158_sumn_20h,q158_vma_20h,q158_vstd_20h,q158_wvma_20h,q158_vsump_20h,q158_vsumn_20h,q158_vsumd_20h,q158_kmid_open,q158_kmid_range,q158_kup_range,q158_klow_range,q158_open_close_0h,q158_high_close_0h,q158_low_close_0h,q158_open_close_1h,q158_high_close_1h,q158_low_close_1h,a101_volume_xs_z_mean_neg_112h,a101_vol_xs_z_product_112h,a101_volume_low_alpha_min_84_120,a101_volume_high_alpha_min_84_84,a101_volume_cap_alpha_min_80_80,a101_volume_cap_alpha_min_56_84
```

Result:

- Factors checked: 54
- Total checks: 1296
- PASS: 1243
- FAIL: 0
- WARN: 53

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
