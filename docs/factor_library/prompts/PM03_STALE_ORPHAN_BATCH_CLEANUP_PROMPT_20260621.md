# PM-03 Prompt — Stale / Orphan Batch Cleanup

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows:

- PM-01: Canonical pipeline reality audit
- PM-02A: Default dataset contract repair
- PM-02B: Canonical monthly universe builder + stale universe builder deletion

The user explicitly wants the repository to remain clean. If stale or misleading files are proven unused by the active factor-library mainline, they should be removed from the active tree. However, deletion must be evidence-based and auditable.

## 0. Product / PM boundary

The active product is a research-grade crypto perpetual cross-sectional factor library.

Current canonical dataset / universe:

- Universe: `crypto_usdt_perp_monthly_volume_top50_current_listed_v1`
- Factor/evaluation dataset: `crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1`
- Canonical universe builder: `scripts/build_dynamic_universe_monthly_volume.py`
- Canonical factor values: `scripts/build_factor_values.py`
- Canonical factor evaluator: `scripts/evaluate_factors.py`
- Canonical factor intake: `scripts/run_factor_intake.py`
- Canonical signal panel: `scripts/build_phase9b_signal_panel.py`
- Canonical signal evaluator: `scripts/evaluate_signals.py`

Future support for US/HK equities may be added later. Do not implement that here.

## 1. Task objective

Do a **batch cleanup** of stale/orphan factor-library files that remain in active-looking locations, especially `scripts/` and root-level phase documents.

This task is larger than PM-02B, but still bounded. The goal is to remove or archive multiple proven-stale files in one pass, not to refactor active code.

## 2. Strict prohibitions

Do **not** modify factor formulas, factor ops, or factor specs.

Do **not** modify `scripts/build_factor_values.py` unless a deleted stale file is directly referenced there.

Do **not** modify `scripts/evaluate_factors.py`.

Do **not** modify `scripts/run_factor_intake.py`.

Do **not** modify `scripts/build_phase9b_signal_panel.py`.

Do **not** modify `scripts/evaluate_signals.py`.

Do **not** modify `src/momentum/signal_evaluation/`.

Do **not** regenerate data files, parquet files, factor values, labels, universe files, signal panels, factor evaluation outputs, or signal evaluation outputs.

Do **not** alter public factor/signal result pages except if a stale file reference is directly embedded in a script-map or governance page.

Do **not** touch `src/momentum/strategies/`; it is out of scope for factor-library cleanup.

Do **not** delete archive directories wholesale.

Do **not** delete PM audit files or PM prompt files.

Do **not** create a new architecture or config system.

## 3. Candidate cleanup set

Start with these candidate files/classes. They are candidates, not automatic deletions. Each must pass reference checks before deletion or movement.

### 3.1 Candidate stale scripts in `scripts/`

Check these exact files if present:

- `scripts/evaluate_factors_dynamic_universe.py`
- `scripts/compare_static_dynamic_factor_evals.py`
- `scripts/export_alphalens_factor_data.py`
- `scripts/run_alphalens_smoke_check.py`
- `scripts/build_crypto_native_factor_values.py`
- `scripts/build_factor_values_batch.py`

Check these glob classes if present:

- `scripts/audit_dynamic_universe_*.py`
- `scripts/*alphalens*.py`
- `scripts/*static_dynamic*.py`

For each candidate:

- If no active code imports it, subprocess-calls it, or lists it as an active mainline/supporting script, delete it from `scripts/`.
- If it has historical value only, deletion is still acceptable because Git history preserves it. Prefer deletion from active tree over moving to another active-looking folder.
- If a candidate is still referenced by active governance docs only, update the docs to mark it deleted/stale and then delete it.
- If a candidate is referenced by active code, do not delete; list it as blocked in the PM-03 audit note.

### 3.2 Root-level phase documents

Find root-level files matching:

```bash
ls PHASE_12D_*.md 2>/dev/null || true
```

For each root-level phase closeout document:

- If it is purely historical and not linked from the current factor-library entry path, move it to:

```text
docs/factor_library/archive/phase12d/
```

- If an identical or superseding copy already exists under docs/archive, delete the root-level duplicate.
- Do not edit the content unless needed to fix relative links after a move.

### 3.3 Historical transparency docs

Inspect:

- `docs/factor_library_transparency/`

Do not delete this directory in PM-03 unless it is clearly duplicated elsewhere and not referenced by current governance docs. If kept, ensure it is clearly classified as `HISTORICAL_ARCHIVE / SUPERSEDED` in `FILE_STATUS_REGISTER.csv` and not active mainline.

### 3.4 Project tree snapshot

Inspect:

- `docs/PROJECT_TREE.md`

If it is an old static snapshot that now misleads more than it helps, either:

- delete it if no active docs link to it, or
- mark it clearly as historical/stale in `FILE_STATUS_REGISTER.csv`.

Do not spend time rewriting it.

## 4. Required pre-change reference checks

Run:

```bash
git status --short
```

Then list candidates:

```bash
for f in \
  scripts/evaluate_factors_dynamic_universe.py \
  scripts/compare_static_dynamic_factor_evals.py \
  scripts/export_alphalens_factor_data.py \
  scripts/run_alphalens_smoke_check.py \
  scripts/build_crypto_native_factor_values.py \
  scripts/build_factor_values_batch.py; do
  [ -e "$f" ] && echo "$f"
done

find scripts -maxdepth 1 -type f \( -name '*alphalens*.py' -o -name '*static_dynamic*.py' -o -name 'audit_dynamic_universe_*.py' \) -print | sort
ls PHASE_12D_*.md 2>/dev/null || true
```

For each candidate, run reference checks:

```bash
rg -n "<basename_without_py>|<exact_filename>" README.md docs scripts src reports research || true
```

If `rg` is unavailable, use `grep -RIn`.

Classify each reference as:

- active code import/subprocess call
- active governance reference
- public site reference
- historical audit/prompt reference
- archive/historical reference

Only active code references block deletion.

Historical audit/prompt references do not block deletion and should not be edited.

## 5. Allowed changes

Allowed changes include:

- Delete proven-stale candidate scripts from `scripts/`
- Move root `PHASE_12D_*.md` files to `docs/factor_library/archive/phase12d/` or delete exact duplicates
- Update `docs/factor_library/FILE_STATUS_REGISTER.csv`
- Update `docs/factor_library/factor_library_manifest.json`
- Update `docs/factor_library/ORPHAN_WORK_AUDIT.md`
- Update `docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md` only if it directly references a stale/deleted file
- Update `docs/factor_library/START_HERE.md` only if it directly references a stale/deleted file
- Update `reports/site/factor-library/assets/actual_script_map.json` or `actual-script-map.html` only if they directly reference a stale/deleted file
- Add `docs/factor_library/audits/pm03_stale_orphan_batch_cleanup.md`

Do not modify unrelated files.

## 6. Required audit note

Create:

`docs/factor_library/audits/pm03_stale_orphan_batch_cleanup.md`

The note must contain a table with one row per candidate path:

```text
path | action | reason | active_code_refs | active_doc_refs_before | historical_refs_remaining | risk | validation
```

Actions must be one of:

- `DELETED`
- `MOVED_TO_ARCHIVE`
- `KEPT_ACTIVE`
- `KEPT_HISTORICAL`
- `BLOCKED_BY_ACTIVE_REFERENCE`
- `NOT_FOUND`

The audit note must also state:

- Total files deleted
- Total files moved
- Total governance files updated
- Any candidates blocked from deletion and why
- Explicit non-change statement: no factor logic, signal logic, universe data, labels, factor values, or evaluation outputs changed

## 7. Validation after cleanup

Run syntax checks for active scripts only:

```bash
python -m py_compile \
  scripts/build_dynamic_universe_monthly_volume.py \
  scripts/build_factor_values.py \
  scripts/evaluate_factors.py \
  scripts/run_factor_intake.py \
  scripts/build_phase9b_signal_panel.py \
  scripts/evaluate_signals.py
```

Run reference checks for deleted files:

```bash
rg -n "evaluate_factors_dynamic_universe|compare_static_dynamic_factor_evals|export_alphalens_factor_data|run_alphalens_smoke_check|build_crypto_native_factor_values|build_factor_values_batch|audit_dynamic_universe" README.md docs scripts src reports research || true
```

Expected result:

- Deleted files may still appear in historical PM audit/prompt files.
- Deleted files should not appear as active mainline/supporting entries in `FILE_STATUS_REGISTER.csv`, manifest, START_HERE, Control Center, or public script map.
- No active code should reference deleted files.

Inspect final diff:

```bash
git diff --stat
git diff -- docs/factor_library/FILE_STATUS_REGISTER.csv docs/factor_library/factor_library_manifest.json docs/factor_library/ORPHAN_WORK_AUDIT.md docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md docs/factor_library/START_HERE.md docs/factor_library/audits/pm03_stale_orphan_batch_cleanup.md
```

Also inspect deleted/moved files with:

```bash
git status --short
```

## 8. Commit rules

Commit with this message:

```bash
chore: prune stale factor-library orphan files
```

Final response should include:

- commit hash
- files deleted
- files moved
- governance files updated
- validation commands run
- any blocked deletion candidates
- any remaining stale references that are historical only
