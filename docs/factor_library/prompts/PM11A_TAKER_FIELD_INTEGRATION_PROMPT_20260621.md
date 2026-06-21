# PM-11A Prompt — Taker Field Integration for Canonical Factor Build

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-10:

- `docs/factor_library/audits/pm10_data_completeness_missing_input_audit.md`

PM-10 found that the three taker-buy factors are not truly missing data. The taker-enriched bars already exist under an alternate path, and the factor values already exist under a `_crypto_native_v1` dataset variant. The current issue is a canonical path / schema mapping gap.

## 0. PM objective

Integrate taker-buy fields into the canonical factor build path in the smallest safe way, then build and intake only the three taker-buy factors.

Target factors:

- `taker_buy_ratio_20h`
- `taker_buy_zscore_20h`
- `taker_buy_delta_5h`

Expected after PM-11A:

- These 3 factors should build under the canonical dataset path:
  `data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/<factor_id>/factor_values.parquet`
- Factor library state should move from 71 registered / 65 computed / 6 missing to roughly 71 registered / 68 computed / 3 missing.
- The remaining missing factors should be funding-only.

Do not touch funding factors in this task.

## 1. Strict prohibitions

Do **not** download new data.

Do **not** call external APIs.

Do **not** overwrite the canonical bars parquet.

Do **not** merge taker columns permanently into the canonical bars parquet in this task.

Do **not** modify funding data.

Do **not** build funding factors.

Do **not** modify signal panel construction.

Do **not** modify `scripts/build_phase9b_signal_panel.py`.

Do **not** add any taker factor to current signal variants.

Do **not** rebuild public result pages.

Do **not** modify live trading, execution, broker, exchange, or `src/momentum/strategies/` code.

Do **not** make production/live/tradeability/alpha claims.

## 2. Current known paths

Canonical bars path:

```text
data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet
```

Taker-enriched bars path:

```text
data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1_taker_enriched/bars_1h.parquet
```

Canonical features path:

```text
data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/
```

Existing alternate taker/funding factor_values path from PM-10:

```text
data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1_crypto_native_v1/
```

Use alternate factor values only as reference for validation. Do not just copy them into canonical path unless you document why recomputation is impossible. Preferred route: recompute via canonical build pipeline using taker-enriched bars as the source for taker factors.

## 3. Required pre-checks

Run:

```bash
git status --short
```

Inspect current registry entries for the three taker factors:

```bash
python - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, str(Path('scripts').resolve()))
from factor_formula_registry import REGISTRY_BY_ID
ids = ['taker_buy_ratio_20h','taker_buy_zscore_20h','taker_buy_delta_5h']
for fid in ids:
    fs = REGISTRY_BY_ID[fid]
    print(fid, fs.required_columns, fs.status, fs.expected_direction, fs.lookback_window)
PY
```

Profile the two bars files lightly:

```bash
python - <<'PY'
import pandas as pd
from pathlib import Path
paths = [
 'data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet',
 'data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1_taker_enriched/bars_1h.parquet',
]
for p in paths:
    df = pd.read_parquet(p)
    print('\n', p)
    print('rows', len(df), 'symbols', df['symbol'].nunique())
    print('min/max', df['timestamp'].min(), df['timestamp'].max())
    print('columns', list(df.columns))
    print('nulls', df.isna().mean().sort_values(ascending=False).head(10).to_dict())
PY
```

Verify that canonical and taker-enriched bars have identical row key coverage:

```bash
python - <<'PY'
import pandas as pd
base = pd.read_parquet('data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet', columns=['timestamp','symbol'])
taker = pd.read_parquet('data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1_taker_enriched/bars_1h.parquet', columns=['timestamp','symbol'])
print('base rows', len(base), 'taker rows', len(taker))
print('base duplicates', base.duplicated(['timestamp','symbol']).sum())
print('taker duplicates', taker.duplicated(['timestamp','symbol']).sum())
base_keys = set(map(tuple, base[['timestamp','symbol']].itertuples(index=False, name=None)))
taker_keys = set(map(tuple, taker[['timestamp','symbol']].itertuples(index=False, name=None)))
print('base_minus_taker', len(base_keys - taker_keys))
print('taker_minus_base', len(taker_keys - base_keys))
PY
```

If row key coverage is not identical, stop and report. Do not force mapping.

## 4. Preferred implementation design

Preferred design: factor-specific source resolution inside `scripts/build_factor_values.py`.

Do not overwrite canonical bars.

Do not globally switch all factor builds to taker-enriched bars.

Instead:

1. Ordinary factors continue to use canonical bars.
2. If a factor requires taker columns (`taker_buy_volume` or `taker_buy_quote_volume`) and those columns are absent from canonical bars, load taker-enriched bars for that factor.
3. Load taker-enriched bars at most once per build run, cache it in memory, and reuse for all taker factors.
4. Print clearly which source is used for each factor group.

Possible implementation pattern:

```python
TAKER_BARS_PATH = ROOT / 'data' / 'cache' / 'crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1_taker_enriched' / 'bars_1h.parquet'
TAKER_REQUIRED_COLUMNS = {'taker_buy_volume', 'taker_buy_quote_volume'}

def factor_needs_taker_source(spec):
    return bool(set(spec.required_columns) & TAKER_REQUIRED_COLUMNS)
```

Then in factor build loop:

- if required columns are present in canonical bars, use canonical bars;
- else if factor needs taker source, use taker-enriched bars and verify required columns exist;
- else mark missing input as before.

Keep behavior for non-taker missing inputs unchanged. Funding should remain missing after PM-11A.

If `build_factor_values.py` already has a better abstraction, reuse it rather than adding a parallel mini-framework.

## 5. Required run

After code change, run py_compile:

```bash
python -m py_compile \
  scripts/build_factor_values.py \
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

Run factor intake for only the three taker factors:

```bash
python scripts/run_factor_intake.py \
  --factor-ids taker_buy_ratio_20h taker_buy_zscore_20h taker_buy_delta_5h \
  --run-id pm11a_taker_field_integration_20260621
```

Do not use dry-run.

Do not use skip-build-values.

Do not include funding factors.

## 6. Validation against alternate existing factor values

If alternate `_crypto_native_v1` factor_values exist, compare the new canonical factor_values against the alternate factor_values for the same factor IDs.

For each taker factor, report:

- canonical rows
- alternate rows
- symbol counts
- timestamp min/max
- exact row-key match count if feasible
- correlation or max absolute difference for overlapping row keys

If they are not identical, do not automatically treat that as failure. Explain whether the difference is due to dataset filtering, row alignment, or formula/source difference.

## 7. Refresh factor library state

After successful intake, run:

```bash
python scripts/build_factor_library_state.py
```

Expected after PM-11A:

- registered remains 71
- computed increases by 3 if canonical taker factor_values are created
- missing decreases from 6 to 3
- remaining missing should be funding-only

## 8. Required audit note

Create:

```text
docs/factor_library/audits/pm11a_taker_field_integration.md
```

The audit note must include:

1. Summary verdict:
   - `TAKER_CANONICAL_BUILD_PASS`
   - `TAKER_MAPPING_BLOCKED`
   - `TAKER_BUILD_FAILED`
2. Pre-check results for canonical vs taker-enriched bars alignment.
3. Code changes made.
4. Taker source resolution design.
5. Intake command and run ID.
6. Whether factor_values were generated for all 3 taker factors.
7. Quality check summary.
8. Conclusion card buckets.
9. Comparison against `_crypto_native_v1` alternate factor_values if available.
10. Before/after factor library counts.
11. Remaining missing factors.
12. Explicit non-change statement: no funding integration, no signal panel, no public pages, no production/live claims.

## 9. Allowed files to change

Allowed code:

- `scripts/build_factor_values.py`

Allowed generated state/report files:

- `research/factor_runs/crypto_top50_factor_library/factor_library_state.json`
- `research/factor_runs/crypto_top50_factor_library/factor_library_state.md`
- `research/factor_runs/crypto_top50_factor_library/factor_registry_integrity_report.json`
- `research/factor_runs/crypto_top50_factor_library/factor_registry_integrity_report.csv`
- isolated intake output under:
  - `research/factor_runs/crypto_top50_factor_library/factor_intake/pm11a_taker_field_integration_20260621/`

Allowed audit:

- `docs/factor_library/audits/pm11a_taker_field_integration.md`

Do not edit unrelated docs.

## 10. Stop conditions

Stop and report instead of forcing through if:

- taker-enriched bars are missing;
- canonical and taker-enriched bars row keys are not aligned;
- required taker columns are missing or mostly null;
- modifying `build_factor_values.py` would affect non-taker factor builds in an uncontrolled way;
- taker factor intake fails for formula/evaluation reasons that need PM review.

## 11. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
fix: integrate taker fields into canonical factor build
```

Final response should include:

- commit hash
- summary verdict
- code files changed
- whether canonical taker factor_values were generated
- before/after registered/computed/missing counts
- remaining missing factors
- conclusion card buckets
- validation vs `_crypto_native_v1` outputs
- warnings/blockers
