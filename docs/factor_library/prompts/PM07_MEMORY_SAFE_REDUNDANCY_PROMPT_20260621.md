# PM-07 Prompt — Memory-Safe Factor Redundancy Diagnostics

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-06:

- `docs/factor_library/audits/pm06_factor_intake_smoke_test.md`

PM-06 verdict was `PASS_WITH_WARNINGS`. The factor intake workflow ran successfully, but `factor_redundancy.csv` was missing because `scripts/build_factor_redundancy.py` was killed by SIGKILL / OOM.

Root cause identified in PM-06: `build_factor_redundancy.py` loads all factor parquets and performs an incremental outer merge into one wide DataFrame. With 59 factors × 3.3M rows, this can require ~50GB peak memory on a 15GB machine.

## 0. PM objective

Make redundancy diagnostics memory-safe enough for current factor intake.

This is a code-quality / intake reliability task. It is **not** factor research, signal research, or production trading work.

Goal:

1. `scripts/build_factor_redundancy.py` should complete in intake mode for the PM-06 smoke factor set.
2. It should produce `factor_redundancy.csv` without OOM.
3. `scripts/run_factor_intake.py` should then generate a complete 17/17 artifact set.
4. Output schema should remain compatible with `scripts/build_factor_conclusion_cards.py`.
5. Do not change factor formulas, signal logic, evaluation methodology, or canonical outputs.

## 1. Strict prohibitions

Do **not** modify `scripts/factor_formula_registry.py`.

Do **not** modify `scripts/factor_ops.py`.

Do **not** modify `scripts/factor_specs.py`.

Do **not** modify `scripts/build_phase9b_signal_panel.py`.

Do **not** modify signal weights, signal variants, or signal factor list.

Do **not** regenerate canonical full factor evaluation.

Do **not** regenerate canonical signal panel.

Do **not** regenerate universe data, bars, labels, or canonical factor values.

Do **not** promote anything into the current signal panel.

Do **not** add a general config framework.

Do **not** create a parallel redundancy script unless absolutely necessary; prefer fixing `scripts/build_factor_redundancy.py` in place.

Do **not** make production, live trading, alpha, or tradeability claims.

## 2. Current problem in code

Inspect `scripts/build_factor_redundancy.py`.

Current problematic behavior:

- `load_factor_wide()` reads every factor parquet into memory.
- It renames `factor_value` to factor ID.
- It outer-merges all factors on `timestamp, symbol`.
- Only after the wide table is created does it apply `sample_step`.

This is the source of OOM.

## 3. Required design change

Replace the wide-table all-factor merge with pairwise / streaming redundancy computation.

### 3.1 New preferred computation pattern

Implement helpers conceptually like:

```python
def load_factor_series(fid: str, sample_step: int = 1) -> pd.DataFrame:
    # Read only timestamp, symbol, factor_value.
    # Optionally downsample timestamps BEFORE pairwise merge.
    # Return columns: timestamp, symbol, factor_value.
```

```python
def compute_pair_from_files(fi: str, fj: str, meta: dict, sample_step: int, pair_type: str) -> dict:
    # Load fi and fj only.
    # Inner-join on timestamp, symbol.
    # Drop null factor values.
    # Compute Pearson and Spearman.
    # Return same output schema as old compute_pair().
```

Then:

- In intake mode, compare each intake factor against each baseline factor without loading all baseline factors at once.
- Compare intake-vs-intake pairwise the same way.
- In library mode, either use the same pairwise method or keep old behavior only for very small factor sets. For safety, pairwise method should be default.

### 3.2 Important requirements

Use inner joins for a pair. Do not outer-merge all factors.

Load at most two factor parquet files at a time, except optionally caching the small list of intake factors if memory remains modest.

Apply `sample_step` before pairwise join, not after building a huge wide table.

Preserve output columns exactly:

```text
factor_i
factor_j
family_i
family_j
same_family
spearman_corr
abs_spearman_corr
pearson_corr
n_pairwise_obs
redundancy_level
recommendation
pair_type
```

If adding internal helper columns, do not write them to output CSV unless downstream code expects them.

Keep threshold constants unchanged:

- `NEAR_DUPLICATE = 0.95`
- `HIGH_REDUNDANCY = 0.85`
- `MODERATE_REDUNDANCY = 0.70`
- `MIN_PAIRWISE_OBS = 30`

Keep `recommendation_for_pair()` semantics unchanged unless a bug is found.

## 4. Required test run

Use a new run ID to avoid overwriting PM-06:

```text
pm07_intake_redundancy_smoke_20260621
```

Run:

```bash
python -m py_compile \
  scripts/build_factor_redundancy.py \
  scripts/run_factor_intake.py \
  scripts/build_factor_conclusion_cards.py \
  scripts/generate_intake_report.py

python scripts/run_factor_intake.py \
  --factor-ids rev_1h rev_3h price_volume_corr_20h \
  --run-id pm07_intake_redundancy_smoke_20260621 \
  --skip-build-values
```

Expected:

- Intake completes.
- `factor_redundancy.csv` exists.
- `factor_redundancy.csv` is non-empty.
- Conclusion cards read redundancy results rather than degrading to UNKNOWN for all factors.
- Quality checks remain PASS.

If the run is still too heavy, add an explicit safe intake-mode default such as limiting baseline to computed factors with available parquets and using `--sample-step` before join. However, do not silently skip baseline comparison. If you must sample, record sampling in the audit note and printed output.

## 5. Validate output schema compatibility

After the run, inspect:

```text
research/factor_runs/crypto_top50_factor_library/factor_intake/pm07_intake_redundancy_smoke_20260621/factor_redundancy.csv
research/factor_runs/crypto_top50_factor_library/factor_intake/pm07_intake_redundancy_smoke_20260621/factor_conclusion_cards.csv
research/factor_runs/crypto_top50_factor_library/factor_intake/pm07_intake_redundancy_smoke_20260621/quality_checks.csv
research/factor_runs/crypto_top50_factor_library/factor_intake/pm07_intake_redundancy_smoke_20260621/report.md
```

Record:

- number of redundancy pairs
- number of intake-vs-intake pairs
- number of intake-vs-baseline pairs
- redundancy level distribution
- whether conclusion cards have non-UNKNOWN redundancy information
- total runtime

## 6. Allowed files to change

Allowed code file:

- `scripts/build_factor_redundancy.py`

Allowed audit file:

- `docs/factor_library/audits/pm07_memory_safe_redundancy_patch.md`

Do not modify `run_factor_intake.py` unless absolutely necessary. If you need to modify it, explain why in the audit note.

Do not modify `build_factor_conclusion_cards.py` unless its schema assumptions are incompatible with the existing documented redundancy output schema. If you need to modify it, explain why.

## 7. Required audit note

Create:

```text
docs/factor_library/audits/pm07_memory_safe_redundancy_patch.md
```

The audit note must include:

- PM-06 failure summary
- root cause
- old algorithm description
- new algorithm description
- files changed
- run command
- run ID
- runtime
- whether `factor_redundancy.csv` exists and is non-empty
- number of redundancy pairs
- redundancy level distribution
- quality check summary
- conclusion card decision buckets
- whether promotion guard was re-tested or not; if not, explain why PM-06 already tested it
- memory behavior notes, even if approximate
- explicit non-change statement: no factor formula, signal logic, signal panel, universe data, labels, canonical factor values, or public result pages changed

## 8. Validation before commit

Run:

```bash
git diff --stat
git status --short
python -m py_compile scripts/build_factor_redundancy.py scripts/run_factor_intake.py scripts/build_factor_conclusion_cards.py scripts/generate_intake_report.py
```

If the intake run succeeded, do not delete the isolated PM-07 intake run directory. It is a diagnostic artifact.

## 9. Commit rules

Commit with:

```bash
fix: make factor redundancy diagnostics memory safe
```

Final response should include:

- commit hash
- old OOM cause
- new redundancy algorithm summary
- PM-07 intake run status
- whether `factor_redundancy.csv` was generated
- redundancy pair count and level distribution
- files changed
- remaining warnings or blockers
