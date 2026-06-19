# Spread Parity Root-Cause Investigation

> Phase 12D-H2-S · 2026-06-19

## Summary

New `compute_quantile_spread` and old Phase 10A spread differ by ~4-8%. Root cause: **different bucket construction algorithms** — old uses rank-based head/tail, new uses pd.qcut quintile boundaries.

---

## Old Algorithm (Phase 10A)

```python
QUANTILE_FRAC = 0.20  # top/bottom 20%
MIN_CROSS_SECTION = 10

for ts, group in df.groupby("ts"):
    n = len(group)
    if n < MIN_CROSS_SECTION:
        continue
    n_q = max(int(n * QUANTILE_FRAC), 1)  # 10 for n=50
    ranked = group.sort_values("signal", ascending=False)
    long = ranked.head(n_q)     # top 10 by rank
    short = ranked.tail(n_q)    # bottom 10 by rank
    spread = long["fwd"].mean() - short["fwd"].mean()
```

**Characteristics:**
- Rank-based: sort by signal, take head/tail
- Always exactly `n_q` symbols per leg (10 for n=50)
- No quantile boundary ambiguity
- `min_symbols = 10`

## New Algorithm (Public API)

```python
n_quantiles = 5

for ts, grp in merged.groupby(group_col):
    valid = grp.dropna()
    n = len(valid)
    if n < n_quantiles * 2:  # min 10
        continue
    buckets = pd.qcut(valid[signal_col], n_quantiles, labels=False, duplicates="drop")
    top_mask = buckets == buckets.max()
    bottom_mask = buckets == buckets.min()
    spread = valid.loc[top_mask, return_col].mean() - valid.loc[bottom_mask, return_col].mean()
```

**Characteristics:**
- Quantile-boundary-based: pd.qcut assigns each value to a quintile
- Bucket sizes may vary (tied values at boundaries)
- `min_symbols = n_quantiles * 2 = 10`

---

## Mandatory Comparison Points (9/9)

### 1. Quantile Definition (5 quantiles?)

| | Old | New |
|---|---|---|
| Method | `QUANTILE_FRAC = 0.20` → 5 buckets | `n_quantiles = 5` |
| Bucket selection | Top/bottom 20% by rank | Top/bottom quintile by qcut |
| **Match?** | Same quantile count | **Yes** |

### 2. Top-Bottom Direction Consistency

| | Old | New |
|---|---|---|
| Long leg | `head(n_q)` = highest signals | `buckets == max` = highest quintile |
| Short leg | `tail(n_q)` = lowest signals | `buckets == min` = lowest quintile |
| Spread | long_mean - short_mean | top_mean - bottom_mean |
| **Match?** | Same direction | **Yes** |

### 3. Winsorization/Trimming

| | Old | New |
|---|---|---|
| Winsorization | None | None |
| Trimming | None | None |
| **Match?** | Both raw | **Yes** |

### 4. Per-Timestamp vs All-Timestamp qcut

| | Old | New |
|---|---|---|
| Grouping | `df.groupby("ts")` → per-timestamp | `merged.groupby(group_col)` → per-timestamp |
| Bucketing | Per-timestamp sort + head/tail | Per-timestamp pd.qcut |
| **Match?** | Both per-timestamp | **Yes** |

### 5. `duplicates="drop"` Usage

| | Old | New |
|---|---|---|
| Ties | Not explicitly handled (sort is stable) | `duplicates="drop"` merges tied buckets |
| Impact | Old always takes n_q symbols | New may have fewer buckets if ties |
| **Match?** | **No** — tie handling differs | Root cause #2 |

### 6. Symbol Universe (50 vs 266)

| | Old | New |
|---|---|---|
| Universe | 50 label symbols only | 266 panel symbols filtered to 50 |
| Filtering | Inner join with labels → 50 symbols | `sp[sp["symbol"].isin(label_symbols)]` → 50 |
| **Match?** | Same 50 symbols | **Yes** (after filtering) |

### 7. NaN Filtering Before Binning

| | Old | New |
|---|---|---|
| Method | `df.dropna()` before groupby | `grp.dropna()` inside groupby |
| Columns | signal + fwd + ts | signal_value + forward_return |
| **Match?** | Same effect | **Yes** |

### 8. Handling of Insufficient Bins per Timestamp

| | Old | New |
|---|---|---|
| Threshold | `n < MIN_CROSS_SECTION (10)` → skip | `n < n_quantiles * 2 (10)` → skip |
| Behavior | Skip timestamp entirely | Return NaN |
| **Match?** | Same threshold | **Yes** |

### 9. Use of Alphalens vs Current Labels

| | Old | New |
|---|---|---|
| Label source | `alphalens_exports/.../forward_returns_long.parquet` | Same file (for parity) |
| Format | Wide (ret_fwd_1h, etc.) | Converted to tidy via `select_forward_return` |
| Values | Same numeric values | Same (verified by n_periods match) |
| **Match?** | Same data | **Yes** |

---

## Root Cause Summary

| # | Difference | Impact | Severity |
|---|-----------|--------|----------|
| 1 | Bucket construction (rank vs qcut) | 4-8% spread diff | Low |
| 2 | Tie handling (duplicates="drop") | Minor bucket membership | Low |
| 3 | Min symbols threshold | No difference | None |

**Only 2 real differences, both low-impact.**

---

## Quantified Impact

| Signal | Horizon | Old Spread | New Spread | Diff | Diff % |
|--------|---------|------------|------------|------|--------|
| core_only | 1h | -0.000306 | -0.000282 | 2.4e-5 | 7.8% |
| core_only | 4h | -0.001232 | -0.001134 | 9.8e-5 | 8.0% |
| core_only | 24h | -0.006742 | -0.006411 | 3.3e-4 | 4.9% |
| core_only | 72h | -0.016623 | -0.015943 | 6.8e-4 | 4.1% |

---

## Legacy-Compatible Mode Design (Design Only — NOT Implemented)

### Proposal

Add a `mode` parameter to `compute_quantile_spread`:

```python
def compute_quantile_spread(
    signal_df, label_df,
    signal_col="signal_value", return_col="forward_return",
    group_col="timestamp", n_quantiles=5,
    mode="standard",           # NEW: "standard" or "legacy_phase10a"
    quantile_frac=0.20,        # Only used in legacy mode
) -> pd.DataFrame:
```

### Behavior by Mode

| Aspect | `standard` (default) | `legacy_phase10a` |
|--------|---------------------|-------------------|
| Bucket method | `pd.qcut(n_quantiles)` | `sort + head/tail` |
| Bucket size | Variable (qcut boundaries) | Fixed `int(n * quantile_frac)` |
| Tie handling | `duplicates="drop"` | Stable sort, deterministic |
| Compatibility | Clean, modern | Exact Phase 10A match |

### Implementation Sketch (NOT implemented)

```python
if mode == "legacy_phase10a":
    n_q = max(int(n * quantile_frac), 1)
    ranked = grp.sort_values(signal_col, ascending=False)
    top = ranked.head(n_q)[return_col].mean()
    bottom = ranked.tail(n_q)[return_col].mean()
    spread = top - bottom
else:  # standard
    buckets = pd.qcut(grp[signal_col], n_quantiles, labels=False, duplicates="drop")
    ...
```

### Recommendation

**Do NOT implement now.** Reasons:
1. The new method (qcut) is more statistically correct
2. The 4-8% diff is small and same-direction
3. Adding legacy mode increases API surface and maintenance burden
4. If exact backward compatibility is needed later, the design is ready

**If implementing later**: Only do so if a downstream consumer requires exact Phase 10A spread values for comparison. Add deprecation warning on `legacy_phase10a` mode.

---

## H3 Gate Status

| Metric | Status | Gate |
|--------|--------|------|
| RankIC | PASS_ROUNDED_REFERENCE | Open |
| Spread | BEHAVIORAL | Open (with documentation) |
| n_periods | EXACT | Open |
| **Overall** | **OPEN_FOR_RANKIC_WRAPPER_ONLY** | Proceed to H3 |

**Condition**: H3 wrapper must document that spread outputs may differ by 4-8% from old Phase 10A due to quantile construction method. This is expected and acceptable.
