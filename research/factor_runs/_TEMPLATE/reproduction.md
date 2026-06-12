# <Research Name> — Reproduction

## 1. Environment

### Repository

```yaml
repo: jerry0012009/momentum
branch: <branch>
commit_sha: <commit>
```

### Python

```yaml
python_version: <version>
virtualenv: <path or name>
requirements_file: <requirements file>
```

### Dependencies

List non-standard dependencies and data-provider packages.

| Package | Version | Required For | Notes |
|---|---|---|---|
| pandas | | | |
| numpy | | | |
| yfinance | | | |
| akshare | | | |

## 2. Input Data

| Input | Path / Provider | Frozen? | Notes |
|---|---|---:|---|
| OHLCV | | yes/no | |
| factor values | | yes/no | |
| signals | | yes/no | |

If input data is not frozen, state:

```text
Exact reproduction is not guaranteed.
```

## 3. Commands

### Data snapshot

```bash
# TODO: verify
python <script>.py --save-data
```

### Factor values

```bash
# TODO: verify
python <script>.py --build-factors
```

### Signals

```bash
# TODO: verify
python <script>.py --build-signals
```

### Backtest

```bash
# TODO: verify
python <script>.py --backtest
```

### Report

```bash
# TODO: verify
python <script>.py --report
```

## 4. Expected Outputs

| Output | Path | Required? | Verified? |
|---|---|---:|---:|
| manifest | `data/cache/<name>/manifest.json` | yes | no |
| bars | `data/cache/<name>/bars.parquet` | yes | no |
| factor values | `data/features/<name>/factor_values.parquet` | yes | no |
| signals | `data/features/<name>/signals.parquet` | yes | no |
| trades | `reports/artifacts/<name>/trades.parquet` | yes | no |
| metrics | `reports/artifacts/<name>/metrics.json` | yes | no |
| summary | `reports/artifacts/<name>/result_summary.md` | yes | no |

## 5. Verification

Minimum reproduction checks:

- [ ] Commands run without error
- [ ] Input row counts match manifest
- [ ] Factor row counts match expected bars after warmup
- [ ] Signal timestamps are not later rewritten
- [ ] Trades match signal/execution protocol
- [ ] Metrics are reproducible from trades/equity curve
- [ ] Rerun produces the same outputs when using frozen data

## 6. Known Reproduction Limits

List any reason exact reproduction may fail.

- Runtime data fetch
- Provider revisions
- Missing dependency version
- Random seed not fixed
- External API instability
- Hard-coded local paths

Notes:

- 

## 7. Reproduction Status

```yaml
reproduction_status: UNVERIFIED
last_verified_at: TBD
verified_by: TBD
```
