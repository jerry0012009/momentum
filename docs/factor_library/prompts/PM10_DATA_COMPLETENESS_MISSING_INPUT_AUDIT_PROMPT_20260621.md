# PM-10 Prompt — Data Completeness and Missing Input Audit

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-09:

- `docs/factor_library/audits/pm09_alpha158_batch1_implementation.md`

PM-09 successfully added 6 Alpha158-inspired OHLCV-only factors and refreshed factor library state to 71 registered / 65 computed / 6 missing input factors.

The user explicitly flagged that many factors may have incomplete data. Current state confirms 6 registered factors still have missing input data:

- `taker_buy_ratio_20h`
- `taker_buy_zscore_20h`
- `taker_buy_delta_5h`
- `funding_rate_level_20h`
- `funding_rate_zscore_80h`
- `funding_rate_change_24h`

## 0. PM objective

Perform a read-only data completeness audit and create an implementation plan for unlocking missing-input factors.

This task should answer:

1. What columns are currently present in the canonical bars/features data?
2. Which registered factors are missing because required columns are absent?
3. Are taker-buy fields already available somewhere in current raw/cached data but not mapped?
4. Are funding-rate fields available somewhere in current raw/cached data but not mapped?
5. What is the safest implementation sequence to compute the 6 missing factors?
6. Should taker-buy and funding be handled together or separately?

This is a planning/audit task. Do not implement data ingestion yet.

## 1. Strict prohibitions

Do **not** download new data in this task.

Do **not** call external APIs in this task.

Do **not** modify `scripts/factor_formula_registry.py`.

Do **not** modify `scripts/factor_ops.py`.

Do **not** modify any factor computation code.

Do **not** modify `scripts/download_full_binance_1h_universe.py`.

Do **not** modify bars parquet, labels parquet, factor_values parquet, or universe parquet.

Do **not** run factor intake.

Do **not** rebuild factor values.

Do **not** rebuild signal panel.

Do **not** rebuild public pages.

Do **not** make production/live/tradeability/alpha claims.

## 2. Canonical paths to inspect

Inspect current canonical dataset:

```text
data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet
data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/labels.parquet
data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/<factor>/factor_values.parquet
research/factor_runs/crypto_top50_factor_library/factor_library_state.json
research/factor_runs/crypto_top50_factor_library/factor_registry_integrity_report.json
research/factor_runs/crypto_top50_factor_library/factor_catalog.json
```

Also search for possible existing taker/funding data in repo:

```bash
find data research -iname '*taker*' -o -iname '*funding*' -o -iname '*fund*' | sort
rg -n "taker|funding|funding_rate|taker_buy" scripts data research docs/factor_library | head -300
```

## 3. Required data profiling

Use lightweight Python profiling. Avoid loading unnecessary full columns into memory.

For `bars_1h.parquet`, report:

- file size
- row count
- columns
- timestamp min/max
- symbol count
- null rate per column
- whether columns exist that could represent taker buy volume, such as any column containing:
  - `taker`
  - `buy`
  - `taker_buy`
  - `taker_buy_base`
  - `taker_buy_quote`
- whether columns exist that could represent funding, such as any column containing:
  - `funding`
  - `funding_rate`

For labels, report:

- row count
- columns
- timestamp min/max
- null rates for forward return columns

For factor values:

- count registered factors
- count computed factor_values directories
- list missing factor_values
- list missing-input factors and their required columns from registry/catalog/integrity report

## 4. Required factor-level missing input analysis

For each of the 6 missing factors, produce a table:

```text
factor_id | required_columns | current_column_status | likely_data_source | can_compute_now? | recommended_next_step
```

Use these categories for `current_column_status`:

- `PRESENT_IN_BARS`
- `PRESENT_ELSEWHERE_IN_REPO`
- `ABSENT_NEEDS_DOWNLOAD`
- `UNCLEAR_NEEDS_SOURCE_CHECK`

Use these categories for `can_compute_now?`:

- `YES_NOW`
- `YES_AFTER_COLUMN_MAPPING`
- `NO_NEEDS_DATA_BACKFILL`
- `NO_SOURCE_UNCLEAR`

## 5. Implementation sequencing recommendation

Make a concrete sequencing recommendation.

Possible outcomes:

### Outcome A — taker fields already exist in bars

If taker-buy fields exist in `bars_1h.parquet` under different names, recommend PM-11A as a small mapping/build task:

- update required column mapping or registry compute functions only if needed
- run factor intake for the 3 taker factors
- no new downloads

### Outcome B — taker fields absent but derivable from raw kline source

If bars lack taker fields but raw kline files/caches contain them, recommend PM-11A as a bars enrichment task:

- enrich canonical bars with taker fields from existing raw cache
- do not change OHLCV semantics
- recompute only taker factors

### Outcome C — funding data absent

If funding data is absent, recommend PM-11B as a separate data ingestion/backfill task:

- define funding data schema
- backfill funding_rate by symbol/timestamp
- align to 1h bars by forward-fill or nearest funding interval, but only after PM approval
- compute funding factors only after data audit

### Outcome D — both absent

If both taker and funding are absent, recommend doing taker first only if it is simpler and already available from kline-like data; otherwise do a source-design task before implementation.

Do not recommend implementing taker and funding in one commit unless the audit shows both are already present and only need column mapping.

## 6. Required output

Create:

```text
docs/factor_library/audits/pm10_data_completeness_missing_input_audit.md
```

The audit note must include:

1. Summary verdict:
   - `DATA_COMPLETE_FOR_OHLCV_ONLY`
   - `TAKER_FIELDS_PRESENT_NEEDS_MAPPING`
   - `TAKER_FIELDS_ABSENT_FUNDING_ABSENT`
   - `FUNDING_PRESENT_NEEDS_MAPPING`
   - `MIXED_NEEDS_BACKFILL`
2. Current bars schema and coverage.
3. Labels schema and coverage.
4. Factor registry / factor_values completeness.
5. Missing-input factor table.
6. Existing repo evidence for taker/funding data, if any.
7. Recommended PM-11 sequence.
8. Explicit non-change statement.

## 7. Validation

Run:

```bash
python -m py_compile scripts/factor_formula_registry.py scripts/build_factor_values.py scripts/run_factor_intake.py
```

Also run a read-only Python profiling snippet and include it in the audit note, or summarize its output.

## 8. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
docs: audit data completeness for missing factors
```

Final response should include:

- commit hash
- summary verdict
- whether taker fields are present
- whether funding fields are present
- which missing factors can be unlocked now
- recommended PM-11 sequence
- blockers
