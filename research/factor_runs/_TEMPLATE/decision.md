# <Research Name> — Decision

## 1. Decision Summary

```yaml
decision_status: PENDING
decision: PENDING
reviewed_by: TBD
reviewed_at: TBD
```

Allowed decisions:

- `ARCHIVE_OLD_CODE`
- `REBUILD_CLEAN_BASELINE`
- `PROMOTE_TO_PAPER`
- `PROMOTE_TO_SHADOW`
- `DROP`
- `PARK`

## 2. Decision

Selected decision:

```text
PENDING
```

One-sentence rationale:

```text
<TODO>
```

## 3. Evidence Used

| Evidence | Path | Supports | Notes |
|---|---|---|---|
| status | `research/factor_runs/<name>/status.md` | | |
| factor memo | `research/factor_runs/<name>/factor_memo.md` | | |
| data contract | `research/factor_runs/<name>/data_contract.md` | | |
| audit notes | `research/factor_runs/<name>/audit_notes.md` | | |
| reproduction | `research/factor_runs/<name>/reproduction.md` | | |
| Code Trust Map | `docs/CODE_TRUST_MAP.md` | | |
| report | `<path>` | | |
| artifacts | `<path>` | | |

## 4. Archive Decision

Fill if decision is `ARCHIVE_OLD_CODE`.

```yaml
archive_old_code: true/false
old_code_should_be_extended: true/false
old_code_should_be_deleted: false
idea_kept_as_candidate: true/false
```

Reason:

- 

Archive rule:

> Archive means preserve the old files and stop extending them. It does not mean delete.

## 5. Rebuild Decision

Fill if decision is `REBUILD_CLEAN_BASELINE`.

```yaml
rebuild_name: <new_clean_name>
source_idea: <old_name>
old_code_reused: false
new_folder_required: true
```

Required new folder:

```text
research/factor_runs/<new_clean_name>/
```

Required artifacts:

```text
data/cache/<new_clean_name>/manifest.json
data/cache/<new_clean_name>/bars.parquet
data/features/<new_clean_name>/factor_values.parquet
data/features/<new_clean_name>/signals.parquet
reports/artifacts/<new_clean_name>/trades.parquet
reports/artifacts/<new_clean_name>/metrics.json
```

## 6. Promotion Decision

Fill if decision is promotion.

Promotion is forbidden unless all required checks are satisfied.

- [ ] Frozen input data or manifest
- [ ] Standalone factor values
- [ ] Standalone signals
- [ ] Standalone trades
- [ ] Explicit cost model
- [ ] Documented PnL / drawdown / Sharpe basis
- [ ] No unresolved future-leak issue
- [ ] Factor memo completed
- [ ] Reproduction command verified
- [ ] Code Trust Map reviewed
- [ ] Human reviewer approval

## 7. Drop or Park Decision

Fill if decision is `DROP` or `PARK`.

Reason:

- 

What would change this decision?

- 

## 8. Next Actions

- [ ] Update `status.md`
- [ ] Update `docs/CODE_TRUST_MAP.md`
- [ ] Update `docs/FACTOR_BACKLOG.md`
- [ ] Create clean rebuild folder if needed
- [ ] Stop extending archived scripts
- [ ] Add tests if rebuilding

## 9. Human Notes

- 
