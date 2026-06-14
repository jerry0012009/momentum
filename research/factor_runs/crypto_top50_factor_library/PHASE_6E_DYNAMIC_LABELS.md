# Phase 6E — Dynamic Universe Forward-Return Labels

> Date: 2026-06-13
>
> Status: COMPLETE — FACTOR_VALUES BUILD ALLOWED

---

## 1. Goal

Build forward-return labels for the dynamic-universe 1h bars dataset using calendar-time join.

## 2. Label Definition

```
ret_fwd_{h}h = close[timestamp + h hours] / close[timestamp] - 1
calendar-time join, no row-shift
```

Horizons: 1h, 4h, 24h, 72h

## 3. Input Dataset

| Field | Value |
|-------|-------|
| dataset_id | `crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1` |
| Rows | 3,316,259 |
| Symbols | 266 |

## 4. Output

| File | Rows | Description |
|------|------|-------------|
| `labels.parquet` | 3,316,259 | Forward-return labels |
| `labels_manifest.json` | — | Build metadata |

## 5. Global Label Coverage

| Horizon | Missing Rate |
|---------|-------------|
| ret_fwd_1h | 0.0081% |
| ret_fwd_4h | 0.0324% |
| ret_fwd_24h | 0.1936% |
| ret_fwd_72h | 0.5786% |

Missing labels are caused by:
- Tail rows lacking future data (by design)
- Bars gaps (calendar-time join produces NaN, no fallback)

## 6. Membership-Aware Label Coverage

| Metric | Value |
|--------|-------|
| Selected label rows | 890,400 |
| selected_ret_fwd_1h_missing | 0.0056% |
| selected_ret_fwd_4h_missing | 0.0225% |
| selected_ret_fwd_24h_missing | 0.1348% |
| selected_ret_fwd_72h_missing | 0.4043% |

All membership-aware missing rates are well below QA thresholds.

## 7. QA Thresholds

| Threshold | Limit | Actual | Status |
|-----------|-------|--------|--------|
| selected_ret_fwd_1h_missing | ≤1% | 0.006% | ✅ |
| selected_ret_fwd_4h_missing | ≤1% | 0.023% | ✅ |
| selected_ret_fwd_24h_missing | ≤3% | 0.135% | ✅ |
| selected_ret_fwd_72h_missing | ≤5% | 0.404% | ✅ |

## 8. QA Decision

**Decision: ALLOWED** — Phase 6F (factor_values build) can proceed.

## 9. Tests

10/10 pass:
- Calendar-time join: exact match, gap→NaN, all horizons, tail missing, multi-symbol
- Membership-aware: selected coverage, tail counted, high→blocks, acceptable→allows, schema

## 10. Whether Phase 6F Is Allowed

**Yes — Phase 6F factor_values build is allowed.**
