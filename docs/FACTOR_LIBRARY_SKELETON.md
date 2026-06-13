# Factor Library Skeleton — Phase 2C

> **Status:** Phase 2C — Factor Library Skeleton (infrastructure, not alpha)
>
> Last updated: 2026-06-13
>
> Phase 2B closed with 5 diagnostic probes passing Lightweight Quality Gate.
> Phase 2C builds the batch onboarding scaffold so that future factors enter
> the library without breaking timing, data conventions, or evaluation protocol.

---

## 1. Factor Status Enum

All factors in the library use exactly one of these statuses:

| Status | Meaning | Who can set it |
|--------|---------|---------------|
| `DIAGNOSTIC_PROBE` | Pipeline tested; not alpha evidence | auto (after first eval run) |
| `CANDIDATE_REVIEW` | Passed basic quality gate; needs deeper stats | human only |
| `CANDIDATE_FACTOR` | Passed Phase 2C review; suitable for model integration | human only |
| `PARK` | Not enough evidence, not falsified; revisit later | human only |
| `DROP` | Fails evaluation or has known flaw | human or auto (with audit) |

**Forbidden status names:** `ALPHA`, `STRONG_ALPHA`, `DEPLOYABLE_ALPHA`, `LIVE`, `SHADOW`.
These do not exist in the factor library. Alpha is a property of a strategy, not a single factor.

**Current state:** All 5 V0 factors remain `DIAGNOSTIC_PROBE`. No promotion until human reviews Phase 2C output.

---

## 2. Factor Catalog Schema

The canonical catalog is a CSV file:

```text
research/factor_runs/crypto_top50_factor_library/factor_catalog_v0_1.csv
```

Required columns:

| Column | Type | Description |
|--------|------|-------------|
| `factor_id` | str | Unique machine-readable ID, e.g. `mom_20h`. Convention: `<short_name>_<window>h` |
| `factor_name` | str | Human-readable name, e.g. "20h Momentum" |
| `factor_family` | enum | `momentum`, `mean_reversion`, `volatility`, `technical`, `microstructure`, `crypto_specific` |
| `formula_type` | str | Short formula description, e.g. `close/close_lag-1` |
| `window` | int | Lookback window in bars (primary window if multiple) |
| `expected_direction` | enum | `positive`, `negative`, `conditional` |
| `required_columns` | str | Comma-separated list of input columns needed, e.g. `close`, `close,high,low` |
| `known_at_rule` | str | When factor is first knowable: `t0` (same bar close), `t+1h`, `t+4h`, etc. |
| `implementation_status` | enum | `NOT_IMPLEMENTED`, `IMPLEMENTED` |
| `evaluation_status` | enum | `DIAGNOSTIC_PROBE`, `CANDIDATE_REVIEW`, `CANDIDATE_FACTOR`, `PARK`, `DROP` |
| `artifact_path` | str | Relative path to factor_values.parquet (auto-filled by pipeline) |
| `notes` | str | Free text: caveats, TODOs, literature references |

### 2.1 Example Record

```csv
factor_id,factor_name,factor_family,formula_type,window,expected_direction,required_columns,known_at_rule,implementation_status,evaluation_status,artifact_path,notes
mom_20h,20h Momentum,momentum,close/close_lag-1,20,positive,close,t0,IMPLEMENTED,DIAGNOSTIC_PROBE,data/features/crypto_top50_usdt_perp_1h/mom_20h/factor_values.parquet,V0 probe
```

### 2.2 Status Transition Rules

```
NOT_IMPLEMENTED → IMPLEMENTED → DIAGNOSTIC_PROBE → CANDIDATE_REVIEW → CANDIDATE_FACTOR
                                                  → PARK
                                                  → DROP
```

- `IMPLEMENTED → DIAGNOSTIC_PROBE`: automatic after first successful evaluation run
- `DIAGNOSTIC_PROBE → CANDIDATE_REVIEW`: human approval only, requires quality gate pass
- `CANDIDATE_REVIEW → CANDIDATE_FACTOR`: human approval only, requires deeper statistical review
- Any status → `PARK` or `DROP`: human decision (or automated with audit justification)

---

## 3. Factor Implementation Interface

Every factor computation function must satisfy this contract:

### 3.1 Input

```python
def compute_factor(bars: pd.DataFrame) -> pd.DataFrame:
    """
    Input: bars dataframe with at least [timestamp, symbol, <required_columns>].
    timestamp is bar_close_time (V0 convention).
    """
```

### 3.2 Temporal Constraints (hard rules)

1. **No future data access.** The function must not use any data from timestamp > current row's timestamp.
2. **No `shift(-k)` on factor values.** Only `shift(+k)` (backward-looking) is allowed.
3. **No rolling window that includes future bars.** `rolling(window).mean()` is fine if applied to already-known data; `shift(-1).rolling(5)` is not.
4. **known_at = bar_close_time.** Factor is computed at bar close, not bar open.

### 3.3 Output Schema

The output dataframe must have exactly these columns:

| Column | Type | Description |
|--------|------|-------------|
| `timestamp` | datetime[UTC] | Bar close time (= known_at) |
| `symbol` | str | Trading pair, e.g. `BTCUSDT` |
| `factor_name` | str | Must match `factor_id` in catalog |
| `factor_value` | float | The computed factor value |
| `known_at` | datetime[UTC] | Must equal `timestamp` (bar close) |
| `source_timeframe` | str | e.g. `1h` |
| `computed_at` | str | ISO timestamp of when computation was run |

### 3.4 Output Path

```text
data/features/crypto_top50_usdt_perp_1h/<factor_id>/factor_values.parquet
```

### 3.5 Validation Checklist

Before a factor passes `IMPLEMENTED` status:

- [ ] Output has all 7 required columns
- [ ] `known_at == timestamp` for all rows
- [ ] No rows with `factor_value` from future timestamps (sanity check: no `shift(-k)`)
- [ ] `factor_name` matches `factor_id` in catalog
- [ ] Coverage > 95% (excluding warmup period)
- [ ] Unit test passes: synthetic data with known formula output

---

## 4. Label Requirements

Labels are computed by `scripts/build_labels.py` and shared across all factors.

| Label | Definition | Notes |
|-------|-----------|-------|
| `ret_fwd_1h` | `close[t+1h] / close[t] - 1` | Calendar-time join |
| `ret_fwd_4h` | `close[t+4h] / close[t] - 1` | Calendar-time join |
| `ret_fwd_24h` | `close[t+24h] / close[t] - 1` | Calendar-time join |
| `ret_fwd_72h` | `close[t+72h] / close[t] - 1` | Calendar-time join |

**Hard rules:**
- Labels use calendar-time forward returns via merge on `(timestamp + h, symbol)`.
- If `timestamp + h` does not exist (gap), label is NaN. Never substitute a nearby row.
- Labels may use future prices (they ARE the future). Factor values must not.
- Symbols with `missing_bar_rate > 5%` are excluded from label generation and evaluation.

---

## 5. Evaluation Requirements

### 5.1 Required Metrics

Every factor evaluation must produce these metrics per label:

| Metric | Description |
|--------|-------------|
| `IC_mean` | Mean cross-sectional Pearson IC |
| `IC_std` | Std of cross-sectional IC |
| `ICIR` | IC_mean / IC_std |
| `RankIC_mean` | Mean cross-sectional Spearman rank IC |
| `RankIC_std` | Std of rank IC |
| `RankICIR` | RankIC_mean / RankIC_std |
| `quantile_spread_mean` | Mean Q5 - Q1 return spread (raw) |
| `quantile_spread_tstat` | t-stat of raw spread |
| `direction_adjusted_spread` | Q5-Q1 for positive, Q1-Q5 for negative, null for conditional |
| `direction_adjusted_tstat` | t-stat of direction-adjusted spread |
| `turnover` | Mean quantile membership turnover |
| `coverage` | Fraction of non-NaN factor values |

### 5.2 Direction Handling

- `expected_direction` is read from the catalog CSV.
- `direction_adjusted_spread` is the primary comparison metric across factors.
- Raw `quantile_spread_mean` is always Q5 - Q1 regardless of direction.

### 5.3 Evaluation Protocol

1. Merge factor values with labels on `(timestamp, symbol)`.
2. At each cross-section (timestamp), compute IC and RankIC.
3. Split symbols into 5 quintiles by factor value.
4. Compute mean return per quintile.
5. Compute Q5 - Q1 spread (raw) and direction-adjusted spread.
6. Compute quantile membership turnover between consecutive timestamps.
7. Aggregate all metrics over the evaluation period.

### 5.4 Output

```text
reports/artifacts/factor_eval/crypto_top50_usdt_perp_1h/<factor_id>/metrics.json
reports/artifacts/factor_eval/crypto_top50_usdt_perp_1h/<factor_id>/result_summary.md
research/factor_runs/crypto_top50_factor_library/result_summary.md  (master)
```

---

## 6. Test Requirements

Every factor must have unit tests before `IMPLEMENTED` status.

### 6.1 Required Test Categories

| Test | File | What it verifies |
|------|------|-----------------|
| Label correctness | `test_crypto_labels.py` | Calendar-time join, gap handling, tail NaN |
| Factor value schema | `test_crypto_factor_values.py` | Columns, known_at == timestamp, no future leak |
| Evaluation smoke | `test_crypto_factor_eval_smoke.py` | IC/RankIC/spread fields, direction adjustment |

### 6.2 Synthetic Data Tests

All tests must use synthetic data (not real Binance data) to ensure:
- Reproducibility (no network dependency)
- Correctness (known input → expected output)
- Gap handling (deliberate missing bars → correct NaN behavior)

### 6.3 Test Command

```bash
python -m pytest tests/unit/test_crypto_labels.py tests/unit/test_crypto_factor_values.py tests/unit/test_crypto_factor_eval_smoke.py -v
```

---

## 7. Promotion Rules

A factor can move from `DIAGNOSTIC_PROBE` to `CANDIDATE_REVIEW` only if ALL of:

1. ✅ Implementation passes unit tests
2. ✅ `known_at == timestamp` verified
3. ✅ No `shift(-k)` in factor code (code audit)
4. ✅ `coverage > 95%` on evaluation universe
5. ✅ `|RankIC_mean| > 0.01` on at least one label
6. ✅ `direction_adjusted_tstat > 1.96` on at least one label (at 5% significance)
7. ✅ `turnover < 80%` (quantile membership stability)
8. ✅ Human reviews and approves

A factor can move from `CANDIDATE_REVIEW` to `CANDIDATE_FACTOR` only if:

1. ✅ All of the above, plus:
2. ✅ Monthly IC stability: no more than 2 months with IC of opposite sign to expected
3. ✅ Not perfectly correlated (|RankIC| > 0.8) with an existing CANDIDATE_FACTOR
4. ✅ Human approves with documented reasoning

**No factor is alpha.** Factors are inputs to models/strategies. Alpha is a property of a complete strategy with execution, costs, and risk management.

---

## 8. Adding a New Factor (Checklist)

To add a new factor to the library:

1. **Define** the record in `factor_catalog_v0_1.csv` with all required columns.
2. **Implement** in `scripts/build_factor_values.py` (or a new script following the interface).
3. **Write unit tests** in `tests/unit/` following the synthetic data pattern.
4. **Run** the full pipeline: `fetch → build_labels → build_factor_values → evaluate_factors`.
5. **Verify** output schema, known_at, coverage, and evaluation metrics.
6. **Update** `FACTOR_REGISTRY.md` and `FACTOR_LIBRARY_SKELETON.md` status tables.
7. **Commit** with clear message referencing the factor_id.

Do NOT:
- Batch-add factors without individual testing
- Use real market data in unit tests
- Skip the known_at audit
- Promote to CANDIDATE without human review

---

## 9. Phase 2C Scope

### Allowed

- Design and document the factor library skeleton (this document)
- Standardize catalog schema, implementation interface, and evaluation protocol
- Write reusable test infrastructure
- Create PHASE_2C_PLAN.md
- Keep existing 5 DIAGNOSTIC_PROBE factors running

### NOT Allowed

- Add external factors (WQ101, GTJA191, Alpha158, etc.)
- Batch-evaluate external factors
- Strategy backtesting
- Trading cost modeling
- Promote any probe to alpha or candidate status
- Enter Phase 2D or 2E

---

## 10. References

| Resource | Link / Citation |
|----------|----------------|
| WorldQuant 101 Alphas | Kakushadze (2016), SSRN 2701346 |
| GTJA 191 Factors | Guotai Junan Securities research reports |
| Qlib Alpha158/360 | Microsoft Qlib documentation |
| IC / ICIR methodology | Grinold & Kahn, "Active Portfolio Management" (2000) |
