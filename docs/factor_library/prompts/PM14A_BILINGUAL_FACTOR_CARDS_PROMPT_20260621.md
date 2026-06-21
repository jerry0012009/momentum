# PM-14A Prompt — Bilingual Factor Cards Metadata Layer

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-13B:

- `docs/factor_library/audits/pm13b_period_quantile_diagnostics.md`
- `scripts/evaluate_factors.py`
- `scripts/build_factor_diagnostics_metrics.py`
- `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/`

PM-13B completed the quantitative diagnostics data layer: monthly IC, monthly long-short returns, cumulative long-short curves, Sharpe, annualized return/volatility, max drawdown, and positive LS month rate are now available for all 71 factors across 4 horizons and 25 months.

The next bottleneck is readability and maintainability: factor definitions are still primarily technical IDs and formulas. The factor library needs bilingual factor cards before public pages are upgraded.

## 0. PM objective

Create a machine-readable bilingual factor metadata layer for all 71 canonical factors.

This task should produce bilingual factor cards that can later be consumed by public pages. Do not modify public HTML pages in this task.

The goal is to make the factor library:

- readable for non-engineering users;
- maintainable when new factors are added;
- faithful to the registry and formulas;
- safe from exaggerated production/trading claims;
- ready for PM-15 public page integration.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify `scripts/factor_formula_registry.py`.

Do **not** modify `scripts/factor_ops.py`.

Do **not** modify factor_values.

Do **not** modify signal panel construction.

Do **not** modify public HTML pages.

Do **not** create a new public page.

Do **not** rebuild public pages.

Do **not** make production/live/tradeability/alpha claims.

Do **not** write generic marketing copy.

Do **not** claim a factor is good or tradable solely because it has a good metric.

## 2. Repository structure to understand before writing

Inspect entry documents and control documents:

```text
docs/factor_library/START_HERE.md
docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md
docs/factor_library/factor_library_manifest.json
```

Inspect current public pages, but do not edit them:

```text
reports/site/factor-library/index.html
reports/site/factor-library/actual-script-map.html
reports/site/factor-library/factor-evaluation.html
reports/site/factor-library/signal-evaluation-summary.html
```

Inspect current factor definition/evaluation sources:

```text
scripts/factor_formula_registry.py
scripts/factor_specs.py
scripts/factor_ops.py
research/factor_runs/crypto_top50_factor_library/factor_library_state.json
research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/factor_level_formula_catalog.csv
research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/factor_level_candidate_review.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_diagnostics_summary.csv
```

## 3. Required outputs

Create directory if missing:

```text
research/factor_runs/crypto_top50_factor_library/factor_metadata/
```

Generate:

```text
research/factor_runs/crypto_top50_factor_library/factor_metadata/factor_bilingual_cards.csv
research/factor_runs/crypto_top50_factor_library/factor_metadata/factor_bilingual_cards.json
research/factor_runs/crypto_top50_factor_library/factor_metadata/manifest.json
docs/factor_library/audits/pm14a_bilingual_factor_cards.md
```

Optional, if helpful and lightweight:

```text
scripts/build_factor_bilingual_cards.py
```

Preferred: create a reusable script rather than manually writing static JSON, so future factors can be regenerated. If you write a script, keep it simple and deterministic.

## 4. Required factor card schema

Each factor card must include at least:

```text
factor_id
family
lifecycle_status
name_en
name_zh
family_en
family_zh
formula_en
formula_zh
intuition_en
intuition_zh
required_columns
expected_direction
expected_direction_explanation_en
expected_direction_explanation_zh
known_limitations_en
known_limitations_zh
data_source_type
horizon_notes_en
horizon_notes_zh
status_explanation_en
status_explanation_zh
review_required_flag
metadata_quality
source_fields
```

Allowed `metadata_quality` values:

```text
COMPLETE
NEEDS_REVIEW
FORMULA_AMBIGUOUS
DIRECTION_AMBIGUOUS
AUTO_GENERATED_REVIEW_REQUIRED
```

Allowed `data_source_type` examples:

```text
OHLCV
VOLUME
TAKER_FLOW
FUNDING_RATE
VOLATILITY
TECHNICAL
CROSS_SECTIONAL
PRICE_POSITION
MOMENTUM_REVERSAL
RANGE_CANDLE
HYBRID
```

## 5. Writing requirements

For each factor:

1. `name_en` should be concise and readable.
2. `name_zh` should be concise and readable in Chinese.
3. `formula_en` and `formula_zh` must faithfully describe the actual registry formula/proxy.
4. `intuition_en` and `intuition_zh` should explain what the factor is trying to capture, not whether it is profitable.
5. `expected_direction_explanation_*` must distinguish positive, negative, and conditional direction.
6. For `conditional` direction, do not force a bullish/bearish interpretation. State that empirical diagnostics are required.
7. For review-required factors, clearly state why human review is needed.
8. For high-redundancy families, mention possible overlap in limitations but do not invent exact redundancy unless it exists in diagnostics outputs.
9. Funding/taker factors must be described as data-derived diagnostics, not trading signals.
10. Avoid vague copy-paste text such as “this factor captures market sentiment” unless the specific formula supports it.

Chinese should be natural and practical. English should be compact and technical.

## 6. Required quality checks

Run a validation script or inline Python check confirming:

- output row count = 71;
- `factor_id` unique;
- every `factor_id` exists in registry/state;
- every registry/state factor appears in metadata;
- no empty values in:
  - `factor_id`
  - `name_en`
  - `name_zh`
  - `formula_en`
  - `formula_zh`
  - `intuition_en`
  - `intuition_zh`
  - `metadata_quality`
- `metadata_quality` only uses allowed values;
- `data_source_type` only uses declared values or is explicitly documented in manifest.

Do not mark everything `COMPLETE` if generated content obviously needs human review. Prefer honest `NEEDS_REVIEW` or `AUTO_GENERATED_REVIEW_REQUIRED`.

## 7. Manifest requirements

`manifest.json` must include:

```text
generated_at
factor_count
input_files
output_files
required_fields
metadata_quality_distribution
data_source_type_distribution
validation_status
warnings
non_change_statement
```

## 8. Audit note requirements

Create:

```text
docs/factor_library/audits/pm14a_bilingual_factor_cards.md
```

It must include:

1. Summary verdict:
   - `BILINGUAL_CARDS_PASS`
   - `BILINGUAL_CARDS_PASS_WITH_REVIEW_FLAGS`
   - `BILINGUAL_CARDS_BLOCKED`
2. Files generated.
3. Factor count coverage.
4. Required field validation.
5. `metadata_quality` distribution.
6. `data_source_type` distribution.
7. Examples of 3–5 factor cards.
8. Known limitations.
9. Non-change statement: no factor formulas, no signal panel, no public pages.
10. Recommended next PM.

## 9. Suggested implementation approach

Preferred implementation:

1. Load registry/state/formula catalog/diagnostics summary.
2. Build deterministic metadata rows using factor_id, family, required columns, expected direction, notes, lifecycle status, decision bucket, and diagnostics flags.
3. Use controlled templates by family/data_source_type to create bilingual explanations.
4. Apply per-factor overrides only where necessary.
5. Validate all required fields.
6. Write CSV/JSON/manifest.

Do not create a hand-written, untraceable JSON file with no generation logic unless you explain why a script is not practical.

## 10. Validation commands

Run py_compile if you create a script:

```bash
python -m py_compile scripts/build_factor_bilingual_cards.py
```

Run the script if created:

```bash
python scripts/build_factor_bilingual_cards.py
```

Then run a validation snippet and include results in the audit note.

## 11. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
docs: add bilingual factor card metadata
```

Final response should include:

- commit hash
- summary verdict
- files generated
- factor count coverage
- metadata_quality distribution
- examples of generated factor cards
- warnings/review flags
- recommended next PM
