# PM-20 Prompt — Factor Library Regeneration and Intake Contract

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-19:

- `docs/factor_library/audits/pm19_redundancy_aware_scorecard_page_refresh.md`
- `scripts/build_factor_quality_scorecard.py`
- `scripts/build_factor_pairwise_redundancy_matrix.py`
- `scripts/_build_factor_eval_html.py`
- `reports/site/factor-library/factor-evaluation.html`

The factor library now has factor values, factor-level diagnostics, bilingual cards, scorecard, redundancy matrix, and a scorecard-aware evaluation page. The next priority is to make the full pipeline reproducible and extensible when new factors are added.

PM-20 should not add new factors. It should define and implement the regeneration/intake contract.

## 0. PM objective

Create a clear, maintainable regeneration contract for the factor library.

The contract should answer:

1. After a new factor is registered, which scripts must run?
2. Which outputs are regenerated at each step?
3. Which steps are expensive and should be optional?
4. How does a new factor reach the public factor-evaluation page?
5. Which entry docs must be updated so future AI agents do not use stale information?

The result should make the pipeline extensible without creating new parallel scripts/pages.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify factor_values manually.

Do **not** modify `scripts/factor_formula_registry.py` except if fixing stale comments; avoid formula changes.

Do **not** modify `scripts/factor_ops.py`.

Do **not** modify signal panel construction.

Do **not** rebuild signal panel.

Do **not** create a new public page.

Do **not** make production/live/tradeability/alpha claims.

Do **not** run the full expensive evaluation/redundancy pipeline unless explicitly justified. PM-20 is primarily contract/orchestration, not a full recomputation task.

## 2. Repository structure to inspect

Read:

```text
docs/factor_library/START_HERE.md
docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md
docs/factor_library/factor_library_manifest.json
docs/factor_library/FILE_STATUS_REGISTER.csv
research/factor_runs/crypto_top50_factor_library/factor_library_state.json
```

Read active scripts:

```text
scripts/run_factor_intake.py
scripts/build_factor_values.py
scripts/evaluate_factors.py
scripts/build_factor_diagnostics_metrics.py
scripts/build_factor_bilingual_cards.py
scripts/build_factor_quality_scorecard.py
scripts/build_factor_pairwise_redundancy_matrix.py
scripts/_build_factor_eval_html.py
scripts/build_factor_library_state.py
scripts/check_factor_registry_integrity.py
scripts/build_factor_catalog.py
scripts/check_factor_catalog_integrity.py
scripts/audit_factor_direction_semantics.py
```

## 3. Required outputs

Create or update:

```text
docs/factor_library/REGENERATION_CONTRACT.md
docs/factor_library/audits/pm20_factor_library_regeneration_contract.md
scripts/run_factor_library_refresh.py
```

Update entry docs if stale:

```text
docs/factor_library/START_HERE.md
docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md
docs/factor_library/factor_library_manifest.json
```

Only update docs to remove stale counts and clarify the canonical flow. Do not rewrite unrelated content.

## 4. Required regeneration contract

`docs/factor_library/REGENERATION_CONTRACT.md` must include:

### 4.1 Full canonical pipeline

```text
factor registry
  → registry integrity check
  → build factor_values
  → build factor catalog / direction audit
  → factor-level evaluation
  → diagnostics metrics
  → bilingual factor cards
  → quality scorecard
  → pairwise redundancy matrix
  → refreshed scorecard
  → factor-evaluation page
  → factor_library_state
  → public site validation
```

### 4.2 Standard commands

Document commands for:

- adding one or many factor IDs through intake;
- refreshing diagnostics after factor_values already exist;
- rebuilding the public page only;
- rebuilding scorecard only;
- running expensive full redundancy matrix;
- running a cheap smoke/dry run.

### 4.3 Expensive vs cheap steps

Mark:

- `evaluate_factors.py` full run: expensive;
- `build_factor_pairwise_redundancy_matrix.py` full matrix: expensive;
- `build_factor_bilingual_cards.py`: cheap;
- `build_factor_quality_scorecard.py`: cheap;
- `_build_factor_eval_html.py`: cheap;
- `build_factor_library_state.py`: cheap.

### 4.4 Dependency graph

List upstream/downstream dependencies.

Example:

```text
factor_quality_scorecard depends on:
  - factor_diagnostics_summary
  - factor_metadata
  - redundancy_summary

factor-evaluation.html depends on:
  - diagnostics summary
  - monthly series
  - bilingual cards
  - quality scorecard
  - redundancy summary / clusters
```

### 4.5 Staleness rules

Define when outputs become stale:

- registry changes → factor_values/evaluation/diagnostics/metadata/scorecard/page stale;
- factor_values changes → evaluation/diagnostics/scorecard/page stale;
- redundancy changes → scorecard/page stale;
- metadata changes → page stale;
- scorecard changes → page stale.

### 4.6 AI guardrails

Include explicit instructions for future AI agents:

- do not create parallel evaluator;
- do not create random new page;
- do not hand-edit generated CSV/JSON except documented overrides;
- do not use stale docs if state JSON disagrees;
- do not touch `src/momentum/strategies/` for factor library work;
- do not claim production/live/tradeability.

## 5. Required script: `run_factor_library_refresh.py`

Create a lightweight orchestration script:

```text
scripts/run_factor_library_refresh.py
```

The script should support dry-run first.

Suggested CLI:

```bash
python scripts/run_factor_library_refresh.py --dry-run
python scripts/run_factor_library_refresh.py --stage page
python scripts/run_factor_library_refresh.py --stage scorecard
python scripts/run_factor_library_refresh.py --stage metadata
python scripts/run_factor_library_refresh.py --stage diagnostics
python scripts/run_factor_library_refresh.py --stage redundancy --expensive-ok
python scripts/run_factor_library_refresh.py --stage all --expensive-ok
```

Stages:

```text
state
metadata
scorecard
page
diagnostics
redundancy
all
```

Minimum implementation acceptable:

- `--dry-run` prints commands without executing;
- cheap stages can execute real commands;
- expensive stages require `--expensive-ok`;
- every command is logged to stdout;
- failure stops the run;
- script must not silently continue after failed command.

Do not make it overly complex.

## 6. Entry docs cleanup

Update `START_HERE.md` and `FACTOR_LIBRARY_CONTROL_CENTER.md` if they contain stale hard-coded status such as old missing factor counts.

Preferred pattern:

- Use `factor_library_state.json/md` as source of truth.
- Avoid hard-coding volatile counts unless clearly marked as generated/current.
- Link to `REGENERATION_CONTRACT.md`.
- Preserve the existing warning that this is research diagnostics only.

## 7. Validation

Run:

```bash
python -m py_compile scripts/run_factor_library_refresh.py
python scripts/run_factor_library_refresh.py --dry-run
python scripts/run_factor_library_refresh.py --stage page --dry-run
python scripts/run_factor_library_refresh.py --stage scorecard --dry-run
```

Check docs for stale terms:

```bash
python - <<'PY'
from pathlib import Path
for p in ['docs/factor_library/START_HERE.md','docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md']:
    text = Path(p).read_text(encoding='utf-8')
    print('\n', p)
    for term in ['6 taker/funding factors missing', 'Missing factor_values: **6**', '65 registered', '59 computed']:
        print(term, term in text)
PY
```

Do not force removal of all numeric counts if they are accurate and generated, but remove clearly stale claims.

## 8. Required audit note

Create:

```text
docs/factor_library/audits/pm20_factor_library_regeneration_contract.md
```

Audit must include:

1. Summary verdict:
   - `REGENERATION_CONTRACT_PASS`
   - `REGENERATION_CONTRACT_PASS_WITH_LIMITATIONS`
   - `REGENERATION_CONTRACT_BLOCKED`
2. Files changed/created.
3. Canonical pipeline stages documented.
4. Orchestration script features.
5. Expensive step guard behavior.
6. Entry docs cleanup summary.
7. Validation results.
8. Remaining limitations.
9. Non-change statement: no factors, no formulas, no factor_values, no signal panel.
10. Recommended next PM.

## 9. Allowed files to change

Allowed docs:

```text
docs/factor_library/REGENERATION_CONTRACT.md
docs/factor_library/START_HERE.md
docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md
docs/factor_library/factor_library_manifest.json
docs/factor_library/audits/pm20_factor_library_regeneration_contract.md
```

Allowed script:

```text
scripts/run_factor_library_refresh.py
```

Avoid changing generated diagnostics/page outputs in PM-20 unless validation requires it.

## 10. Stop conditions

Stop and report if:

- current docs disagree with actual repository state and cannot be reconciled safely;
- orchestration would require changing formulas/factor_values/signals;
- expensive stages would be accidentally run without explicit `--expensive-ok`;
- public pages would need major redesign.

## 11. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
docs: add factor library regeneration contract
```

Final response should include:

- commit hash
- summary verdict
- files changed
- regeneration stages documented
- dry-run validation results
- stale doc cleanup summary
- recommended next PM
