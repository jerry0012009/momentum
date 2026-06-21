# PM-06 Prompt — Factor Intake Smoke Test

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-05:

- `docs/factor_library/audits/pm05_stale_dataset_reference_cleanup.md`

PM-05 resolved stale dataset references in supporting/non-mainline scripts. The active factor-library pipeline is now clean enough to test the standard factor intake workflow.

## 0. PM objective

Verify that the current factor intake workflow actually works end-to-end in the current repository.

This is a smoke test of the intake system. It is **not** a factor research expansion and **not** a signal research task.

The goal is to prove that:

1. `scripts/run_factor_intake.py` can run on existing registered factors.
2. It creates a complete isolated intake run directory.
3. It generates manifest, command log, output index, quality checks, conclusion cards, and report.
4. Redundancy diagnostics and conclusion-card logic are usable.
5. `scripts/promote_factor_intake.py` guards against accidental promotion and does not modify canonical factor/signal state.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify `scripts/factor_formula_registry.py`.

Do **not** modify `scripts/factor_ops.py`.

Do **not** modify `scripts/factor_specs.py`.

Do **not** modify `scripts/build_phase9b_signal_panel.py`.

Do **not** modify signal weights, signal variants, or signal factor list.

Do **not** regenerate canonical full factor evaluation.

Do **not** regenerate canonical signal panel.

Do **not** regenerate universe data, bars, labels, or canonical factor values.

Do **not** promote anything into the current signal panel.

Do **not** make production, live trading, alpha, or tradeability claims.

## 2. Smoke-test factor set

Use this existing registered factor set:

```text
rev_1h rev_3h price_volume_corr_20h
```

These are already registered factors. Treat them only as test inputs for the intake runner.

Do not add or remove factors from this smoke set unless a factor is proven missing from the registry. If one factor is missing, stop and report instead of silently substituting.

## 3. Required pre-checks

Run:

```bash
git status --short

python -m py_compile \
  scripts/run_factor_intake.py \
  scripts/build_factor_redundancy.py \
  scripts/build_factor_conclusion_cards.py \
  scripts/generate_intake_report.py \
  scripts/promote_factor_intake.py \
  scripts/evaluate_factors.py \
  scripts/build_factor_values.py
```

Verify registry membership without modifying files:

```bash
python - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, str(Path('scripts').resolve()))
from factor_formula_registry import REGISTRY_BY_ID
ids = ['rev_1h', 'rev_3h', 'price_volume_corr_20h']
missing = [x for x in ids if x not in REGISTRY_BY_ID]
print('missing:', missing)
raise SystemExit(1 if missing else 0)
PY
```

## 4. Run intake smoke test

Use a new isolated run ID:

```text
pm06_intake_smoke_20260621
```

Run:

```bash
python scripts/run_factor_intake.py \
  --factor-ids rev_1h rev_3h price_volume_corr_20h \
  --run-id pm06_intake_smoke_20260621 \
  --skip-build-values
```

Do not use `--dry-run`.

Do not skip redundancy unless the redundancy step fails due to a code bug. If it fails, fix the smallest code bug possible and re-run.

## 5. Required artifact inspection

Inspect the run directory:

```text
research/factor_runs/crypto_top50_factor_library/factor_intake/pm06_intake_smoke_20260621/
```

Required artifacts:

```text
manifest.json
command_log.json
outputs_index.json
factor_inventory.csv
quality_checks.csv
report.md
factor_metric_panel.csv
factor_rankic_summary.csv
factor_period_ic_summary.csv
factor_quantile_return_summary.csv
factor_long_short_summary.csv
factor_candidate_review.csv
factor_formula_catalog.csv
evaluation_manifest.json
factor_redundancy.csv
factor_conclusion_cards.csv
factor_conclusion_cards.json
```

For each artifact, record whether it exists and whether it is non-empty.

Inspect:

- `manifest.json` status
- `command_log.json` exit codes
- `quality_checks.csv` PASS/FAIL rows
- `factor_conclusion_cards.csv` decision buckets
- `report.md` readability and whether it contains diagnostic-only language

## 6. Promotion guard behavior

Run without confirm:

```bash
python scripts/promote_factor_intake.py --run-id pm06_intake_smoke_20260621
```

Expected: blocked because `--confirm` is missing.

Then run with confirm:

```bash
python scripts/promote_factor_intake.py --run-id pm06_intake_smoke_20260621 --confirm
```

Expected: either:

- blocked by guard conditions, or
- all guards pass but script clearly states actual promotion is not implemented in this phase.

In all cases, it must not modify:

- `scripts/factor_formula_registry.py`
- `scripts/build_phase9b_signal_panel.py`
- any canonical signal output
- any canonical factor evaluation output without suffix

## 7. Allowed fixes

Allowed code changes only if necessary:

- `scripts/run_factor_intake.py`
- `scripts/build_factor_redundancy.py`
- `scripts/build_factor_conclusion_cards.py`
- `scripts/generate_intake_report.py`
- `scripts/promote_factor_intake.py`

Examples of allowed fixes:

- output filename mismatch
- schema mismatch
- missing file copy into intake run directory
- stale path assumption
- promotion guard path bug
- report generation failure
- quality check incorrectly failing because of a schema rename

Do not change evaluation methodology or factor formulas.

If no code fix is required, do not force one.

## 8. Required audit note

Create:

```text
docs/factor_library/audits/pm06_factor_intake_smoke_test.md
```

The audit note must include:

- command run
- factor IDs tested
- run directory
- required artifact checklist
- quality check summary
- conclusion card decision buckets
- promotion guard result without `--confirm`
- promotion guard result with `--confirm`
- any code changes made
- explicit non-change statement: no factor formula, signal logic, signal panel, universe data, labels, canonical factor values, or public result pages changed

## 9. Validation before commit

Run:

```bash
git diff --stat
git status --short
python -m py_compile \
  scripts/run_factor_intake.py \
  scripts/build_factor_redundancy.py \
  scripts/build_factor_conclusion_cards.py \
  scripts/generate_intake_report.py \
  scripts/promote_factor_intake.py
```

If code changed, also re-run the intake smoke command after the fix.

## 10. Commit rules

Commit with:

```bash
test: add factor intake smoke test audit
```

Final response should include:

- commit hash
- whether intake smoke test passed
- artifacts created
- conclusion card buckets
- promotion guard behavior
- files changed
- remaining warnings or blockers
