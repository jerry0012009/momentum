# Phase 2E Plan — Batch Factor Evaluation

> **Status:** NOT STARTED (Phase 2E0 = planning only)
>
> Date: 2026-06-13
>
> Previous: Phase 2D Review ACCEPTED
>
> Human decision: Phase 2E0 — plan only, no implementation yet

---

## 1. Phase 2E 目标

**Batch Factor Evaluation** = implement shortlisted factors, generate `factor_values`, run standardized evaluation, keep all new factors as `DIAGNOSTIC_PROBE` until human review.

Phase 2E is split into sub-phases:
- **Phase 2E0** (current): Planning only — spec, test plan, batch definitions. No code.
- **Phase 2E1**: Implement Batch 1 (6 direct_formula factors) + tests + evaluation.
- **Phase 2E2**: Implement Batch 2 (cross_sectional_rank factors) + tests + evaluation.
- **Phase 2E3**: Remaining shortlist candidates + full batch evaluation.

---

## 2. 允许做什么

### Phase 2E0 (current)
- ✅ Write `PHASE_2E_PLAN.md` (this file)
- ✅ Write `phase_2e_batch1_spec.md` (formula specifications)
- ✅ Write `phase_2e_batch1_candidates.csv` (batch 1 candidate table)
- ✅ Update `DOCS_INDEX.md`

### Phase 2E1+ (requires human approval)
- ✅ Implement factor formulas in `scripts/build_factor_values.py`
- ✅ Generate `factor_values.parquet` per factor
- ✅ Write unit tests per factor (synthetic input validation)
- ✅ Run `evaluate_factors.py` on new factors
- ✅ Update `FACTOR_REGISTRY.md` (status = `DIAGNOSTIC_PROBE`)

---

## 3. 禁止做什么

### Phase 2E0 (current)
- ❌ Implement any factor code
- ❌ Modify `build_factor_values.py`
- ❌ Generate `factor_values.parquet`
- ❌ Run `evaluate_factors.py`
- ❌ Mark any factor as `CANDIDATE_REVIEW`
- ❌ Strategy backtesting
- ❌ Portfolio modeling

### Phase 2E1+ (all of Phase 2E)
- ❌ Mark any factor as `CANDIDATE_REVIEW` without human review
- ❌ Mark any factor as `CANDIDATE_FACTOR`, `ALPHA`, etc.
- ❌ Strategy backtesting
- ❌ Portfolio modeling
- ❌ Live/paper/shadow deployment

---

## 4. 第一批实现范围 (Batch 1)

**Batch 1 = 6 direct_formula / OHLCV-only factors**

| factor_id | source_prior | factor_family | priority |
|-----------|-------------|--------------|---------|
| `wq101_alpha101` | WQ101 Alpha#101 | intraday_position | HIGH |
| `wq101_alpha12` | WQ101 Alpha#12 | volume_price_momentum | HIGH |
| `wq101_alpha53` | WQ101 Alpha#53 | intraday_position_delta | HIGH |
| `q158_high_low_range` | Alpha158 HL Range | volatility | HIGH |
| `tech_macd` | Technical MACD | trend | HIGH |
| `tech_atr` | Technical ATR | volatility | HIGH |

**Selection criteria:**
- All use `direct_formula` adaptation (no cross-sectional rank)
- All require only OHLCV columns
- All have well-documented, simple formulas
- All rated HIGH priority in shortlist

**Deferred to Batch 2:**
- `wq101_alpha06` (cross_sectional_rank)
- `wq101_alpha01` (cross_sectional_rank)
- Other direct_formula factors (wq101_alpha34, wq101_alpha21, wq101_alpha54, q158_ret_5d, q158_ma_ratio_5d, q158_vol_ratio_5d, tech_stochastic, tech_williams_r)

---

## 5. 实施顺序

### Phase 2E1 Implementation Order

1. **Extend `build_factor_values.py`** — add a `FACTOR_REGISTRY` dict mapping factor_id → computation function.
2. **Implement each factor** as a standalone function: `def compute_{factor_id}(df) -> pd.Series`.
3. **Write unit tests** — each factor gets a `test_{factor_id}` in `tests/unit/test_crypto_factor_values.py` or a new test file.
4. **Run tests** — ensure all pass.
5. **Run pipeline** — `fetch → build_labels → build_factor_values → evaluate_factors`.
6. **Verify outputs** — check `factor_values.parquet` exists per factor, check `result_summary.md` updated.
7. **Update registry** — add each factor to `FACTOR_REGISTRY.md` with `status=DIAGNOSTIC_PROBE`.

### Factor Implementation Template

```python
def compute_{factor_id}(df: pd.DataFrame) -> pd.Series:
    """{short description}"""
    # Implementation here
    return result
```

Each function must:
- Accept `df` with columns: `symbol, timestamp, open, high, low, close, volume, ...`
- Return `pd.Series` indexed same as `df`
- Use only current and past data (no future leak)
- Document `known_at_rule = timestamp`

---

## 6. 测试要求

Every factor implementation must have at least one unit test that checks:

| Check | Description |
|-------|-------------|
| **No future leak** | Only uses current and past data; no `shift(-k)` |
| **known_at == timestamp** | Output is known at bar close time |
| **Schema correct** | Output is `pd.Series` with correct index |
| **Synthetic input** | Given simple synthetic data, produces expected value |
| **NaN handling** | Handles lookback window correctly (NaN for insufficient history) |
| **Direction** | Output sign matches `expected_direction` |

### Synthetic Test Example (for `wq101_alpha101`)

```python
def test_alpha101_basic():
    # (close - open) / (high - low + 0.001)
    df = pd.DataFrame({
        'open': [100], 'high': [110], 'low': [95], 'close': [105]
    })
    result = compute_wq101_alpha101(df)
    expected = (105 - 100) / (110 - 95 + 0.001)
    assert abs(result.iloc[0] - expected) < 1e-6
```

---

## 7. 进入 Phase 2E1 的条件

1. ✅ Phase 2E0 deliverables complete (plan + spec + batch CSV)
2. ⏳ Human review and approval of Phase 2E plan
3. ⏳ Human confirms batch 1 scope (6 factors)

**Current status:** Phase 2E0 in progress. Phase 2E1 NOT ALLOWED YET.

---

## 8. Phase Status Upgrade Policy

| Phase | Factor Status | Condition |
|-------|--------------|-----------|
| 2E1 (implement) | `DIAGNOSTIC_PROBE` | After successful evaluation run |
| 2E1 (implement) | `CANDIDATE_REVIEW` | ❌ NOT ALLOWED without human review |
| Post-2E (human review) | `CANDIDATE_REVIEW` | Only after human reviews evaluation results |
| Post-2E (human review) | `CANDIDATE_FACTOR` | Only if human approves |

**Rule:** No automatic status upgrades. All upgrades require explicit human decision.

---

## 9. Expected Direction Policy

If expected direction is ambiguous, use `expected_direction = conditional`.

| Scenario | expected_direction | Direction-adjusted spread |
|----------|-------------------|--------------------------|
| Clear bullish predictor | `positive` | Use as-is |
| Clear bearish predictor | `negative` | Flip sign |
| Volatility / range proxy | `conditional` | `null` or not used as primary evidence |
| Ambiguous sign (e.g., WQ with -1×delta) | `conditional` | `null` or not used as primary evidence |
| Not yet determined | `conditional` | Evaluate raw first, then decide |

**Rule:** Do not force `expected_direction` for volatility proxies or ambiguous WQ factors. Conditional factors still enter evaluation, but `direction_adjusted_spread` should be `null` or not used as primary evidence.
