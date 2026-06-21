# PM-11B Prompt — Funding Rate Integration for Canonical Factor Build

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-11A:

- `docs/factor_library/audits/pm11a_taker_field_integration.md`

PM-11A successfully integrated taker fields into canonical factor build. After PM-11A, the remaining missing factors are funding-only:

- `funding_rate_level_20h`
- `funding_rate_zscore_80h`
- `funding_rate_change_24h`

## 0. PM objective

Integrate funding_rate data into the canonical factor build path in the smallest safe way, then build and intake only the three funding-rate factors.

Expected after PM-11B:

- These 3 factors should build under the canonical dataset path:
  `data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/<factor_id>/factor_values.parquet`
- Factor library state should move from roughly 71 registered / 68 computed / 3 missing to 71 registered / 71 computed / 0 missing.
- No funding data should be downloaded.
- No signal panel changes.

Do not touch taker integration except to preserve it.

## 1. Strict prohibitions

Do **not** download new data.

Do **not** call external APIs.

Do **not** overwrite canonical bars parquet.

Do **not** merge funding permanently into canonical bars parquet in this task.

Do **not** modify taker-enriched bars.

Do **not** rebuild taker factors unless required by validation; if so, explain why.

Do **not** modify signal panel construction.

Do **not** modify `scripts/build_phase9b_signal_panel.py`.

Do **not** add any funding factor to current signal variants.

Do **not** rebuild public result pages.

Do **not** modify live trading, execution, broker, exchange, or `src/momentum/strategies/` code.

Do **not** make production/live/tradeability/alpha claims.

## 2. Current known paths

Canonical bars path:

```text
data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet
```

Funding data paths from PM-10:

```text
data/cache/crypto_funding_rate_1h_contract_v1/funding_rate_1h_aligned_static.parquet
data/cache/crypto_funding_rate_1h_contract_v1/funding_rate_1h_aligned_dynamic.parquet
data/cache/crypto_funding_rate_1h_contract_v1/funding_rate_events.parquet
```

Canonical features path:

```text
data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/
```

Existing alternate factor_values path:

```text
data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1_crypto_native_v1/
```

Use alternate factor values only as reference for validation. Preferred route: recompute via canonical build pipeline using funding data as a factor-specific source.

## 3. Required pre-checks

Run:

```bash
git status --short
```

Inspect current registry entries:

```bash
python - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, str(Path('scripts').resolve()))
from factor_formula_registry import REGISTRY_BY_ID
ids = ['funding_rate_level_20h','funding_rate_zscore_80h','funding_rate_change_24h']
for fid in ids:
    fs = REGISTRY_BY_ID[fid]
    print(fid, fs.required_columns, fs.status, fs.expected_direction, fs.lookback_window)
PY
```

Profile funding files lightly:

```bash
python - <<'PY'
import pandas as pd
paths = [
 'data/cache/crypto_funding_rate_1h_contract_v1/funding_rate_1h_aligned_static.parquet',
 'data/cache/crypto_funding_rate_1h_contract_v1/funding_rate_1h_aligned_dynamic.parquet',
 'data/cache/crypto_funding_rate_1h_contract_v1/funding_rate_events.parquet',
]
for p in paths:
    df = pd.read_parquet(p)
    print('\n', p)
    print('rows', len(df), 'symbols', df['symbol'].nunique() if 'symbol' in df.columns else None)
    if 'timestamp' in df.columns:
        print('timestamp min/max', df['timestamp'].min(), df['timestamp'].max())
    if 'calc_time' in df.columns:
        print('calc_time min/max', df['calc_time'].min(), df['calc_time'].max())
    print('columns', list(df.columns))
    print('nulls', df.isna().mean().sort_values(ascending=False).head(10).to_dict())
PY
```

Verify row-key alignment of the selected aligned funding file against canonical bars:

1. Prefer `funding_rate_1h_aligned_static.parquet` if it has `timestamp`, `symbol`, and `funding_rate`, and row keys align to canonical bars.
2. Use `funding_rate_1h_aligned_dynamic.parquet` only if static is incomplete or dynamic is clearly the source used for existing `_crypto_native_v1` factor_values.
3. Do not use `funding_rate_events.parquet` directly for factor build in this task unless both aligned files fail validation.

Run row-key check:

```bash
python - <<'PY'
import pandas as pd
bars = pd.read_parquet('data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet', columns=['timestamp','symbol'])
for p in [
 'data/cache/crypto_funding_rate_1h_contract_v1/funding_rate_1h_aligned_static.parquet',
 'data/cache/crypto_funding_rate_1h_contract_v1/funding_rate_1h_aligned_dynamic.parquet',
]:
    f = pd.read_parquet(p, columns=['timestamp','symbol','funding_rate'])
    print('\n', p)
    print('bars rows', len(bars), 'funding rows', len(f))
    print('bars duplicates', bars.duplicated(['timestamp','symbol']).sum())
    print('funding duplicates', f.duplicated(['timestamp','symbol']).sum())
    print('funding null rate', f['funding_rate'].isna().mean())
    bkeys = set(map(tuple, bars[['timestamp','symbol']].itertuples(index=False, name=None)))
    fkeys = set(map(tuple, f[['timestamp','symbol']].itertuples(index=False, name=None)))
    print('bars_minus_funding', len(bkeys - fkeys))
    print('funding_minus_bars', len(fkeys - bkeys))
PY
```

If no aligned funding file has acceptable row-key coverage, stop and report. Do not force mapping.

## 4. Preferred implementation design

Extend the factor-specific source resolution introduced in PM-11A inside `scripts/build_factor_values.py`.

Do not overwrite canonical bars.

Do not globally switch all factor builds to a funding-merged bars file.

Instead:

1. Ordinary factors continue to use canonical bars.
2. Taker factors continue to use taker-enriched bars as implemented in PM-11A.
3. Funding factors use canonical bars joined in memory with the selected aligned funding file on `(timestamp, symbol)`.
4. Load funding data at most once per build run and cache it.
5. Print clearly which source is used for funding factors.

Possible pattern:

```python
FUNDING_RATE_PATH = ROOT / 'data' / 'cache' / 'crypto_funding_rate_1h_contract_v1' / 'funding_rate_1h_aligned_static.parquet'
FUNDING_REQUIRED_COLUMNS = {'funding_rate'}

def _needs_funding_source(spec):
    return bool(set(spec.required_columns) & FUNDING_REQUIRED_COLUMNS)
```

For funding factors:

- load canonical bars with normal columns;
- load funding parquet with `timestamp`, `symbol`, `funding_rate`;
- validate no duplicate row keys;
- merge/join in memory;
- verify `funding_rate` exists and has acceptable null rate;
- compute only funding factors from this merged DataFrame.

Keep non-funding behavior unchanged.

## 5. Required run

After code change, run py_compile:

```bash
python -m py_compile \
  scripts/build_factor_values.py \
  scripts/build_factor_library_state.py \
  scripts/factor_formula_registry.py \
  scripts/factor_ops.py \
  scripts/run_factor_intake.py \
  scripts/evaluate_factors.py \
  scripts/build_factor_redundancy.py \
  scripts/build_factor_conclusion_cards.py \
  scripts/generate_intake_report.py
```

Run registry integrity:

```bash
python scripts/check_factor_registry_integrity.py
```

Run factor intake for only the three funding factors:

```bash
python scripts/run_factor_intake.py \
  --factor-ids funding_rate_level_20h funding_rate_zscore_80h funding_rate_change_24h \
  --run-id pm11b_funding_rate_integration_20260621
```

Do not use dry-run.

Do not use skip-build-values.

Do not include taker factors.

## 6. Validation against alternate existing factor values

If alternate `_crypto_native_v1` factor_values exist, compare the new canonical factor_values against them.

For each funding factor, report:

- canonical rows
- alternate rows
- symbol counts
- timestamp min/max
- exact row-key match count if feasible
- correlation or max absolute difference for overlapping row keys

If outputs differ, explain whether the difference is due to static vs dynamic funding alignment, row filtering, known-at semantics, or formula/source difference. Do not hide differences.

## 7. Refresh factor library state

After successful intake, run:

```bash
python scripts/build_factor_library_state.py
```

Expected after PM-11B:

- registered remains 71
- computed increases from 68 to 71
- missing decreases from 3 to 0
- missing input decreases from 3 to 0

## 8. Required audit note

Create:

```text
docs/factor_library/audits/pm11b_funding_rate_integration.md
```

The audit note must include:

1. Summary verdict:
   - `FUNDING_CANONICAL_BUILD_PASS`
   - `FUNDING_MAPPING_BLOCKED`
   - `FUNDING_BUILD_FAILED`
2. Funding file selected and why.
3. Pre-check results for funding file vs canonical bars alignment.
4. Code changes made.
5. Funding source resolution design.
6. Intake command and run ID.
7. Whether factor_values were generated for all 3 funding factors.
8. Quality check summary.
9. Conclusion card buckets.
10. Comparison against `_crypto_native_v1` alternate factor_values if available.
11. Before/after factor library counts.
12. Remaining missing factors.
13. Explicit non-change statement: no taker changes beyond preservation, no signal panel, no public pages, no production/live claims.

## 9. Allowed files to change

Allowed code:

- `scripts/build_factor_values.py`
- `scripts/build_factor_library_state.py` only if PM-11A missing-state handling needs a minimal correction

Allowed generated state/report files:

- `research/factor_runs/crypto_top50_factor_library/factor_library_state.json`
- `research/factor_runs/crypto_top50_factor_library/factor_library_state.md`
- `research/factor_runs/crypto_top50_factor_library/factor_registry_integrity_report.json`
- `research/factor_runs/crypto_top50_factor_library/factor_registry_integrity_report.csv`
- isolated intake output under:
  - `research/factor_runs/crypto_top50_factor_library/factor_intake/pm11b_funding_rate_integration_20260621/`

Allowed audit:

- `docs/factor_library/audits/pm11b_funding_rate_integration.md`

Do not edit unrelated docs.

## 10. Stop conditions

Stop and report instead of forcing through if:

- aligned funding files are missing;
- funding row keys are badly misaligned with canonical bars;
- funding_rate is mostly null;
- static and dynamic funding files produce materially different results and the correct choice is unclear;
- modifying `build_factor_values.py` would affect non-funding factor builds in an uncontrolled way;
- funding factor intake fails for formula/evaluation reasons that need PM review.

## 11. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
fix: integrate funding rate into canonical factor build
```

Final response should include:

- commit hash
- summary verdict
- funding file selected
- code files changed
- whether canonical funding factor_values were generated
- before/after registered/computed/missing counts
- remaining missing factors
- conclusion card buckets
- validation vs `_crypto_native_v1` outputs
- warnings/blockers
