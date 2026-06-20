# PM-02B Prompt — Canonical Universe Builder and Stale Builder Prune

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows:

- PM-01: `docs/factor_library/audits/pm01_canonical_pipeline_reality_audit.md`
- PM-02A: `docs/factor_library/audits/pm02a_default_dataset_contract_patch.md`

PM-02A aligned the default dataset contract for factor values, factor evaluation, signal panel building, and factor intake. The next repository hygiene problem is the universe builder identity.

## 0. Product / PM context

The current active product goal is a research-grade crypto perpetual cross-sectional factor library.

The current target universe is:

`crypto_usdt_perp_monthly_volume_top50_current_listed_v1`

The current factor/evaluation dataset ID is:

`crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1`

Future universes such as US equities or Hong Kong equities may be supported later. Do not implement multi-asset abstraction in this task.

The immediate goal is to keep the repository structurally honest: the canonical universe builder should be the script that actually implements monthly-volume Top50 selection, and stale/misleading builder scripts should not remain active in the mainline.

## 1. Core finding to verify before changing anything

There are two relevant universe builder scripts:

1. `scripts/build_dynamic_universe_monthly_volume.py`
   - This appears to be the true monthly-volume dynamic universe builder.
   - It selects Top N symbols using the previous full calendar month's Binance UM perpetual 1d `quote_volume` sum.
   - It writes to `data/universe/crypto_usdt_perp_monthly_volume_top50_current_listed_v1/`.
   - It documents current-listed-only survivorship limitations.

2. `scripts/build_crypto_top50_universe.py`
   - This appears to be a stale or misleading static/current Top50 builder.
   - PM-01 found that it uses 24h snapshot volume while exposing fields/names that imply trailing/monthly volume.
   - It also hardcodes `/root/clawd/jerry/momentum`.
   - It outputs or references older `crypto_top50_usdt_perp_1h` / `crypto_top50_usdt_perp_monthly_volume_top50_current_listed_v1` naming.

Before making changes, verify these facts by reading both scripts and grepping references.

## 2. Scope

This is a narrow repository hygiene task.

Allowed goals:

- Promote `scripts/build_dynamic_universe_monthly_volume.py` as the canonical universe builder in active governance/docs/site metadata.
- Remove or demote `scripts/build_crypto_top50_universe.py` if it is not imported or executed by active code.
- Update active governance references so future agents do not call the stale 24h snapshot script as canonical.
- Add one audit note describing exactly what changed and why.

Allowed changed files:

- `docs/factor_library/START_HERE.md`
- `docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md`
- `docs/factor_library/factor_library_manifest.json`
- `docs/factor_library/FILE_STATUS_REGISTER.csv`
- `reports/site/factor-library/assets/actual_script_map.json`
- `reports/site/factor-library/actual-script-map.html` only if it directly embeds the stale script name and is not generated from the JSON asset
- delete `scripts/build_crypto_top50_universe.py` only if reference checks prove it is not used by active code
- `docs/factor_library/audits/pm02b_canonical_universe_builder_patch.md`

Do not modify any other file unless a direct reference check proves it is necessary. If another file must be changed, keep the edit minimal and explain it in the audit note.

## 3. Strict prohibitions

Do **not** change universe generation logic in `scripts/build_dynamic_universe_monthly_volume.py`.

Do **not** run the universe builder.

Do **not** regenerate universe parquet files.

Do **not** regenerate bars, labels, factor values, evaluations, signal panel, or public factor/signal pages.

Do **not** modify `scripts/build_factor_values.py` unless a direct reference to the stale universe builder exists there.

Do **not** modify `scripts/evaluate_factors.py`.

Do **not** modify `scripts/build_phase9b_signal_panel.py`.

Do **not** modify `scripts/evaluate_signals.py`.

Do **not** modify factor formulas, factor ops, factor specs, or signal weights.

Do **not** add a new universe builder.

Do **not** create a new config framework.

Do **not** delete broad groups of files in this task. This task may delete at most `scripts/build_crypto_top50_universe.py` if it is proven stale and unused by active code.

Do **not** edit historical audit files from PM-01 or PM-02A.

Do **not** make production, live trading, alpha, or tradeability claims.

## 4. Required pre-change checks

Run these checks before editing:

```bash
git status --short
python -m py_compile scripts/build_dynamic_universe_monthly_volume.py
```

Search for references:

```bash
rg -n "build_crypto_top50_universe|build_dynamic_universe_monthly_volume|crypto_top50_usdt_perp_1h|crypto_usdt_perp_monthly_volume_top50_current_listed_v1|crypto_top50_usdt_perp_monthly_volume_top50_current_listed_v1" README.md docs scripts reports src research || true
```

If `rg` is unavailable, use `grep -RIn`.

Classify every reference to `build_crypto_top50_universe.py` as one of:

- active code call/import/subprocess
- active governance/documentation reference
- public site metadata reference
- historical audit/prompt reference
- archived/historical reference

Only active code calls block deletion.

Historical audit/prompt references do not need to be edited.

## 5. Required changes if checks confirm the expected state

### 5.1 Canonical builder

Update active governance/docs/site metadata to identify this as the canonical universe builder:

`src/script: scripts/build_dynamic_universe_monthly_volume.py`

Description should be honest:

- Monthly dynamic universe
- Top50 by previous full calendar month's Binance UM perpetual 1d quote_volume sum
- Current-listed candidate pool only
- Not true point-in-time universe
- Survivorship bias remains because delisted symbols are absent

Do not exaggerate. Do not call it production-grade. Do not call it bias-free.

### 5.2 Stale builder

If no active code imports or subprocess-calls `scripts/build_crypto_top50_universe.py`, delete it from the repository.

Reason:

- It is not the true monthly-volume builder.
- It uses 24h snapshot volume.
- It has hardcoded absolute path(s).
- Its presence in `scripts/` misleads future agents into treating it as canonical.

If deletion is blocked by an active code reference, do not delete. Instead:

- update active docs to mark it `DEPRECATED_STALE_DO_NOT_USE`, and
- include the blocking reference in the audit note.

### 5.3 FILE_STATUS_REGISTER

Update `docs/factor_library/FILE_STATUS_REGISTER.csv` so:

- `scripts/build_dynamic_universe_monthly_volume.py` is listed as `ACTIVE_MAINLINE` or equivalent current status.
- `scripts/build_crypto_top50_universe.py` is removed if deleted, or marked `DEPRECATED_STALE_DO_NOT_USE` if not deleted.

Do not perform broad status cleanup for unrelated files in this task.

### 5.4 Manifest

Update `docs/factor_library/factor_library_manifest.json` so the active universe node points to `scripts/build_dynamic_universe_monthly_volume.py`.

Remove or demote `scripts/build_crypto_top50_universe.py` from active mainline/supporting sections.

Do not overhaul the manifest schema.

### 5.5 Control Center and START_HERE

Update only the universe-builder references necessary to prevent future confusion.

Keep wording compact.

Avoid broad documentation rewrites.

### 5.6 Public script map

Update `reports/site/factor-library/assets/actual_script_map.json` so the universe node points to `scripts/build_dynamic_universe_monthly_volume.py` and describes the monthly-volume current-listed limitation accurately.

If `actual-script-map.html` embeds static text with the old script name, update only that text.

Do not regenerate unrelated public pages.

## 6. Required audit note

Create:

`docs/factor_library/audits/pm02b_canonical_universe_builder_patch.md`

The note must include:

- Summary of changed files
- Whether `scripts/build_crypto_top50_universe.py` was deleted or retained
- Evidence that no active code imports/subprocess-calls the deleted/retained stale builder
- The canonical universe builder after this patch
- The exact universe limitation statement:
  - monthly Top50 by previous full calendar month's quote_volume sum
  - current-listed candidate pool only
  - not true point-in-time
  - survivorship bias remains
- Validation commands run
- Explicit statement that no universe files, bars, labels, factor values, evaluations, signal panels, or public factor/signal result pages were regenerated

## 7. Validation after changes

Run:

```bash
python -m py_compile scripts/build_dynamic_universe_monthly_volume.py
```

If `scripts/build_crypto_top50_universe.py` is retained, also run:

```bash
python -m py_compile scripts/build_crypto_top50_universe.py
```

Then run reference checks:

```bash
rg -n "build_crypto_top50_universe.py|build_crypto_top50_universe" README.md docs scripts reports src research || true
rg -n "build_dynamic_universe_monthly_volume.py|build_dynamic_universe_monthly_volume" README.md docs scripts reports src research || true
```

Expected result:

- No active governance/public-site references should call `build_crypto_top50_universe.py` canonical.
- Historical audit/prompt references may remain.
- Active governance/public-site references should identify `build_dynamic_universe_monthly_volume.py` as canonical.

Before committing, inspect:

```bash
git diff --stat
git diff -- docs/factor_library/START_HERE.md docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md docs/factor_library/factor_library_manifest.json docs/factor_library/FILE_STATUS_REGISTER.csv reports/site/factor-library/assets/actual_script_map.json reports/site/factor-library/actual-script-map.html scripts/build_crypto_top50_universe.py docs/factor_library/audits/pm02b_canonical_universe_builder_patch.md
```

Confirm that no generated data files changed.

## 8. Commit rules

Commit with this message:

```bash
chore: canonicalize monthly universe builder
```

Final response should include:

- commit hash
- whether stale script was deleted or retained
- files changed
- validation commands run
- any remaining stale references and whether they are historical only
