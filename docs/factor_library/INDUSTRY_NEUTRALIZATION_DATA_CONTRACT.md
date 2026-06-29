# Industry Neutralization Data Contract

**Status:** `BLOCKED_NO_APPROVED_CRYPTO_TAXONOMY`
**Last reviewed:** 2026-06-28

This contract records what must exist before any public Alpha101 formula that
uses `IndNeutralize(..., IndClass.*)` can move from skipped manifest status into
the factor registry.

This is not a production, live-trading, tradeability, or alpha claim.

## 1. Current State

The public manifest currently has 18 skipped Alpha101 rows blocked by
industry/sector neutralization:

| factor_id | required neutralization group |
| --- | --- |
| `wq101_alpha58_indneutralize_skipped` | `IndClass.sector` |
| `wq101_alpha59_indneutralize_skipped` | `IndClass.industry` |
| `wq101_alpha67_indneutralize_skipped` | `IndClass.sector`, `IndClass.subindustry` |
| `wq101_alpha69_indneutralize_skipped` | `IndClass.industry` |
| `wq101_alpha70_indneutralize_skipped` | `IndClass.industry` |
| `wq101_alpha93_indneutralize_skipped` | `IndClass.industry` |
| `wq101_alpha48_indneutralize_skipped` | `IndClass.subindustry` |
| `wq101_alpha63_indneutralize_skipped` | `IndClass.industry` |
| `wq101_alpha76_indneutralize_skipped` | `IndClass.sector` |
| `wq101_alpha79_indneutralize_skipped` | `IndClass.sector` |
| `wq101_alpha80_indneutralize_skipped` | `IndClass.industry` |
| `wq101_alpha82_indneutralize_skipped` | `IndClass.sector` |
| `wq101_alpha87_indneutralize_skipped` | `IndClass.industry` |
| `wq101_alpha89_indneutralize_skipped` | `IndClass.industry` |
| `wq101_alpha90_indneutralize_skipped` | `IndClass.subindustry` |
| `wq101_alpha91_indneutralize_skipped` | `IndClass.industry` |
| `wq101_alpha97_indneutralize_skipped` | `IndClass.industry` |
| `wq101_alpha100_indneutralize_skipped` | `IndClass.subindustry` |

These rows must remain skipped until this contract is satisfied. They are not
registry entries and must stay excluded from factor-value, intake, post-intake,
and integrity factor ID lists.

## 2. Why They Are Blocked

WorldQuant Alpha101 `IndNeutralize(x, group)` is an equity cross-sectional
operator. It removes the contemporaneous group mean from `x` by an approved
industry, sector, or subindustry classification.

The current crypto factor library does not have:

- an approved crypto sector/industry/subindustry taxonomy;
- point-in-time symbol-to-group membership;

Existing project documentation explicitly warns that crypto has no direct
industry neutralization equivalent. Therefore the blocked Alpha101 formulas must
not be approximated by ad hoc buckets or silent time-series demeaning.

## 3. Required Data Source

Before implementation, create a reviewed taxonomy artifact with this minimum
schema:

| column | meaning |
| --- | --- |
| `symbol` | Canonical exchange symbol used by the factor dataset, e.g. `BTCUSDT` |
| `known_at` | UTC timestamp when this mapping is known to the workflow |
| `effective_from` | UTC timestamp when this mapping starts applying |
| `effective_to` | UTC timestamp when this mapping stops applying, nullable |
| `sector` | Approved coarse crypto sector bucket |
| `industry` | Approved middle-level crypto industry bucket |
| `subindustry` | Approved fine-level crypto subindustry bucket |
| `taxonomy_version` | Immutable taxonomy version identifier |
| `source` | Source or review artifact for the classification |
| `quality_flag` | `OK`, `REVIEW`, or `BLOCKED` |

Point-in-time rule:

- factor computation at timestamp `t` may only use rows with
  `known_at <= t` and `effective_from <= t < effective_to`;
- if no valid row exists, the neutralized factor value must be `NaN`;
- current static classifications may be recorded only as
  `POINT_IN_TIME_APPROXIMATE` and must be disclosed in factor notes.

## 4. Required Operator

The reusable pure operator is available in `scripts/factor_ops.py`:

```text
panel_indneutralize(values, groups, timestamps, min_group_size=2)
```

Required behavior, covered by unit tests:

- operate cross-sectionally within each timestamp;
- subtract the group mean from each symbol's value;
- require at least 2 non-null symbols per group unless explicitly configured;
- preserve `NaN` for missing values or missing group membership;
- never use future group assignments;
- return a Series aligned to the input rows.

The operator does not load, infer, or validate a taxonomy. The remaining blocker
is the approved point-in-time taxonomy data source.

## 5. Required Workflow Extension

The reviewed source file should live at:

```text
data/sources/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.csv
```

Start from the schema-only template:

```text
data/sources/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.template.csv
```

The template is intentionally not a valid artifact; it has no reviewed rows.

Initialize a review CSV from the factor bars:

```bash
python scripts/init_crypto_industry_taxonomy_review.py \
  --bars-path data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet \
  --output-csv data/sources/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.csv \
  --known-at 2026-06-28T00:00:00Z \
  --taxonomy-version reviewed_v1 \
  --source manual_review
```

The initializer creates one `REVIEW` row per current factor-bar symbol and
leaves group fields empty. It is a review workbook, not an approved taxonomy.

Build the validated parquet artifact with:

```bash
python scripts/build_crypto_industry_taxonomy_artifact.py \
  --input-csv data/sources/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.csv \
  --output data/cache/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.parquet
```

The builder writes `data/cache/.../symbol_taxonomy.parquet` only after the
contract checks pass. The contract requires at least one `OK` row; a
review-only workbook is not a valid artifact. On failure the builder removes
any stale output parquet so `build_factor_values.py` cannot accidentally
consume an invalid taxonomy.

`scripts/build_factor_values.py` now has a guarded source branch for taxonomy
panel factors:

- it triggers only when a registered panel `FactorSpec` declares one of
  `sector`, `industry`, or `subindustry` in `required_columns`;
- it expects `data/cache/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.parquet`;
- it uses `known_at`, `effective_from`, and `effective_to` to merge only
  mappings known and effective at each bar timestamp;
- it only accepts taxonomy rows with `quality_flag == "OK"`;
- if the taxonomy file is missing, taxonomy factors are blocked rather than
  approximated.

Before any taxonomy artifact can be used, run:

```bash
python scripts/check_crypto_industry_taxonomy_contract.py \
  --path data/cache/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.parquet
python scripts/check_crypto_industry_taxonomy_coverage.py \
  --bars-path data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet \
  --taxonomy-path data/cache/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.parquet \
  --min-full-coverage 0.98
```

The validator checks required columns, quality-flag domain, known/effective
timestamps, `effective_from <= known_at`, group-field completeness for `OK`
rows, and overlapping effective windows. The coverage checker verifies that the
point-in-time taxonomy covers the current factor bars before any
industry-neutralized Alpha101 row can move from skipped to implemented.

After a batch packet has been manually reviewed and validated, apply only the
explicit `target_quality_flag == OK` rows to a temporary source CSV:

```bash
python scripts/apply_crypto_industry_taxonomy_review_packet.py \
  --source-csv data/sources/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.csv \
  --packet-csv research/factor_runs/crypto_top50_factor_library/factor_diagnostics/industry_taxonomy_review_batch_001.csv \
  --bars-path data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet \
  --output-csv /tmp/symbol_taxonomy.reviewed.csv
```

The apply helper reuses the review-packet validator before writing output. It
does not infer groups, does not approve CoinGecko evidence, and rejects OK rows
whose `known_at` or `effective_from` timestamps are not valid for the current
bar window.

To unblock the skipped Alpha101 rows, the workflow must add:

1. a data contract document for the taxonomy source;
2. a reviewed source CSV under `data/sources/crypto_industry_taxonomy_contract_v1/`;
3. a generated parquet artifact under `data/cache/crypto_industry_taxonomy_contract_v1/`;
4. a passing `check_crypto_industry_taxonomy_contract.py` result;
5. a passing `check_crypto_industry_taxonomy_coverage.py` result against the
   factor bars used by the intake run;
6. `FactorSpec` rows whose `required_columns` include the exact group columns;
7. manifest rows changed from `skipped_missing_industry_neutralization_*` to a
   small `implemented_batch_*` status only after factor values and QA pass;
8. unit tests that prove skipped rows are not registered until the data contract
   is satisfied, and implemented rows have registry parity after migration.

## 6. Disallowed Shortcuts

Do not unblock these formulas by:

- replacing `IndNeutralize` with rolling time-series demeaning;
- using market cap, volume, exchange, listing age, or BTC beta as a fake
  industry group;
- assigning groups from future knowledge without a `known_at` timestamp;
- adding `_v2.py`, one-off loaders, or a separate Alpha101 workflow;
- hand-editing generated HTML or factor diagnostics;
- adding any of these factors directly to the signal panel.

## 7. Current Verdict

The current public-factor integration has covered the auditable and supported
portion of Alpha158 and Alpha101 in the compact manifest. The remaining
Alpha101 industry-neutralized formulas are correctly blocked, not forgotten.

The current review packet is:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/industry_taxonomy_review_priority.csv
```

It ranks 266 symbols by observed `quote_volume`, joins available CoinGecko
mapping evidence from the market-cap workflow, and records the 18 blocked
Alpha101 factor IDs that would become eligible after an approved taxonomy passes
contract and coverage gates. It remains review-only: it does not infer
`sector`, `industry`, or `subindustry`, does not change any `quality_flag` to
`OK`, and does not build `symbol_taxonomy.parquet`.

Next valid implementation step is to manually review and approve a
point-in-time taxonomy source, then run the artifact, contract, and coverage
gates before any formula registration.
