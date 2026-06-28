# Industry Neutralization Data Contract

**Status:** `BLOCKED_NO_APPROVED_CRYPTO_TAXONOMY`
**Last reviewed:** 2026-06-28

This contract records what must exist before any public Alpha101 formula that
uses `IndNeutralize(..., IndClass.*)` can move from skipped manifest status into
the factor registry.

This is not a production, live-trading, tradeability, or alpha claim.

## 1. Current State

The public manifest currently has 6 skipped Alpha101 rows blocked by
industry/sector neutralization:

| factor_id | required neutralization group |
| --- | --- |
| `wq101_alpha58_indneutralize_skipped` | `IndClass.sector` |
| `wq101_alpha59_indneutralize_skipped` | `IndClass.industry` |
| `wq101_alpha67_indneutralize_skipped` | `IndClass.sector`, `IndClass.subindustry` |
| `wq101_alpha69_indneutralize_skipped` | `IndClass.industry` |
| `wq101_alpha70_indneutralize_skipped` | `IndClass.industry` |
| `wq101_alpha93_indneutralize_skipped` | `IndClass.industry` |

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
- a reusable neutralization operator;
- a `build_factor_values.py` source branch that supplies group columns to
  panel factors.

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

Add one reusable panel operator only after the taxonomy exists:

```text
panel_indneutralize(values, groups, timestamp, symbol)
```

Required behavior:

- operate cross-sectionally within each timestamp;
- subtract the group mean from each symbol's value;
- require at least 2 non-null symbols per group unless explicitly configured;
- preserve `NaN` for missing values or missing group membership;
- never use future group assignments;
- return a Series aligned to the input rows.

The operator belongs in the existing factor/operator layer. Do not create a
parallel factor workflow or a one-off Alpha101 evaluator.

## 5. Required Workflow Extension

To unblock the skipped Alpha101 rows, the workflow must add:

1. a data contract document for the taxonomy source;
2. a generated or reviewed taxonomy artifact under `data/`;
3. a `build_factor_values.py` source branch that loads taxonomy columns for
   panel factors requiring `sector`, `industry`, or `subindustry`;
4. `FactorSpec` rows whose `required_columns` include the exact group columns;
5. manifest rows changed from `skipped_missing_industry_neutralization_*` to a
   small `implemented_batch_*` status only after factor values and QA pass;
6. unit tests that prove skipped rows are not registered until the data contract
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

Next valid implementation step is a taxonomy/data-source project, not formula
registration.
