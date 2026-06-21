# PM-14B Prompt — Factor Card Review, Chinese Polish, and Metadata QA

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-14A:

- `docs/factor_library/audits/pm14a_bilingual_factor_cards.md`
- `scripts/build_factor_bilingual_cards.py`
- `research/factor_runs/crypto_top50_factor_library/factor_metadata/factor_bilingual_cards.csv`
- `research/factor_runs/crypto_top50_factor_library/factor_metadata/factor_bilingual_cards.json`

PM-14A generated bilingual cards for all 71 factors, but all cards are marked `AUTO_GENERATED_REVIEW_REQUIRED`. This means PM-14A created the metadata framework, not final human-readable content quality.

## 0. PM objective

Review, polish, and quality-control the bilingual factor cards so they can safely support the future factor-evaluation HTML page.

The goal is to move factor cards from generic template-generated metadata toward a maintainable, readable, domain-aware metadata layer.

Do **not** modify public HTML pages in this task.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify `scripts/factor_formula_registry.py`.

Do **not** modify `scripts/factor_ops.py`.

Do **not** modify factor_values.

Do **not** modify factor diagnostics metrics.

Do **not** modify signal panel construction.

Do **not** modify or rebuild public HTML pages.

Do **not** make production/live/tradeability/alpha claims.

Do **not** mark every factor `COMPLETE` just to pass validation.

Do **not** hand-edit generated CSV/JSON only. Preserve a reproducible generation path.

## 2. Repository structure to respect

Current metadata generator:

```text
scripts/build_factor_bilingual_cards.py
```

Current metadata outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_metadata/factor_bilingual_cards.csv
research/factor_runs/crypto_top50_factor_library/factor_metadata/factor_bilingual_cards.json
research/factor_runs/crypto_top50_factor_library/factor_metadata/manifest.json
```

Current diagnostics metrics:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_diagnostics_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_monthly_ic_series.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_monthly_long_short_series.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_cumulative_long_short_curve.csv
```

Current public pages, for context only:

```text
reports/site/factor-library/index.html
reports/site/factor-library/factor-evaluation.html
reports/site/factor-library/signal-evaluation-summary.html
```

Do not edit these pages in PM-14B.

## 3. Required approach

Improve `scripts/build_factor_bilingual_cards.py` so polished cards are still reproducible.

Acceptable implementation patterns:

1. Add explicit per-factor override dictionaries inside the script; or
2. Add a small metadata override file such as:

```text
research/factor_runs/crypto_top50_factor_library/factor_metadata/factor_card_overrides.json
```

and make the script apply overrides deterministically.

Prefer option 2 if it keeps the script cleaner. In either case, regenerated CSV/JSON must reflect the polished content.

## 4. Review priorities

Review all 71 factors, but pay special attention to:

### 4.1 Direction-sensitive factors

Factors with conditional or ambiguous direction should not be described as simply bullish or bearish. Their `expected_direction_explanation_zh/en` should say that direction depends on empirical diagnostics and market regime.

### 4.2 High-risk generic text

Replace repeated template language such as:

- “captures market condition”
- “measures market pressure”
- “higher values may be informative”

with formula-specific explanations.

### 4.3 Taker and funding factors

Taker and funding factors must be described as diagnostics of flow/carry/funding conditions, not standalone trading signals.

### 4.4 Volatility, range, candle, and technical factors

Chinese explanations should clearly distinguish:

- realized volatility;
- intrabar range;
- candle body/wick structure;
- RSI / Bollinger / ATR / Williams %R style technical indicators.

Do not collapse them into the same generic “波动风险” explanation.

### 4.5 Cross-sectional factors

Explain that cross-sectional factors rank symbols relative to each other at the same timestamp.

### 4.6 Review flags

After review, assign one of:

```text
COMPLETE
NEEDS_REVIEW
FORMULA_AMBIGUOUS
DIRECTION_AMBIGUOUS
AUTO_GENERATED_REVIEW_REQUIRED
```

Expected outcome:

- Not all cards should remain `AUTO_GENERATED_REVIEW_REQUIRED`.
- Not all cards should become `COMPLETE`.
- Conditional/direction-sensitive factors may remain `DIRECTION_AMBIGUOUS` or `NEEDS_REVIEW`.

## 5. Required outputs

Regenerate:

```text
research/factor_runs/crypto_top50_factor_library/factor_metadata/factor_bilingual_cards.csv
research/factor_runs/crypto_top50_factor_library/factor_metadata/factor_bilingual_cards.json
research/factor_runs/crypto_top50_factor_library/factor_metadata/manifest.json
```

Create a QA report:

```text
research/factor_runs/crypto_top50_factor_library/factor_metadata/factor_card_qa_report.csv
```

Suggested QA report columns:

```text
factor_id
metadata_quality
qa_notes_zh
qa_notes_en
changed_in_pm14b
needs_human_review
reason
```

Create audit note:

```text
docs/factor_library/audits/pm14b_factor_card_review_polish.md
```

## 6. Required validation

Run:

```bash
python -m py_compile scripts/build_factor_bilingual_cards.py
python scripts/build_factor_bilingual_cards.py
```

Then run a validation snippet confirming:

- row count = 71;
- factor_id unique;
- every factor in registry/state appears exactly once;
- no empty required fields;
- metadata_quality only uses allowed values;
- QA report row count = 71;
- manifest quality distribution matches actual CSV.

## 7. Audit note requirements

The audit note must include:

1. Summary verdict:
   - `FACTOR_CARD_REVIEW_PASS`
   - `FACTOR_CARD_REVIEW_PASS_WITH_FLAGS`
   - `FACTOR_CARD_REVIEW_BLOCKED`
2. Files changed/generated.
3. Whether generator remains reproducible.
4. Factor count coverage.
5. Metadata quality distribution before vs after.
6. Data source type distribution.
7. Number of cards changed in PM-14B.
8. Examples of improved cards, at least:
   - one momentum/reversal factor;
   - one volatility factor;
   - one taker factor;
   - one funding factor;
   - one conditional/direction-ambiguous factor.
9. Remaining review flags and why.
10. Non-change statement: no formulas, no factor_values, no signal panel, no public pages.
11. Recommended next PM.

## 8. Recommended next PM after PM-14B

If PM-14B passes with a reasonable quality distribution and no severe metadata gaps, next PM should be:

```text
PM-15: Integrate diagnostics metrics and bilingual cards into existing factor-evaluation page
```

Important: PM-15 should upgrade the existing page:

```text
reports/site/factor-library/factor-evaluation.html
```

It should not create a random new page unless there is a documented routing reason.

## 9. Allowed files to change

Allowed code:

```text
scripts/build_factor_bilingual_cards.py
```

Allowed metadata:

```text
research/factor_runs/crypto_top50_factor_library/factor_metadata/*
```

Allowed audit:

```text
docs/factor_library/audits/pm14b_factor_card_review_polish.md
```

Do not edit public pages in this task.

## 10. Stop conditions

Stop and report if:

- factor count is not 71;
- generator cannot reproduce outputs;
- required fields cannot be populated faithfully from registry/formula/metadata;
- too many cards require human-only domain judgment and cannot be safely improved by rule-based overrides;
- proposed changes would modify formulas, diagnostics, signals, or public pages.

## 11. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
docs: review and polish bilingual factor cards
```

Final response should include:

- commit hash
- summary verdict
- files changed/generated
- metadata_quality before vs after
- number of cards changed
- examples of improved cards
- remaining review flags
- recommended next PM
