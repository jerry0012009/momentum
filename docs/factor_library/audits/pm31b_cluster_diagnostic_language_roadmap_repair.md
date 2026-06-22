# PM-31B: Cluster Diagnostic Language Repair

**Date:** 2026-06-22  
**Status:** COMPLETE  
**Verdict:** `CLUSTER_LANGUAGE_ROADMAP_REPAIR_PASS`

---

## Summary

Replaced all prescriptive language in redundancy cluster diagnostic outputs with diagnostic-only language. The script no longer recommends keeping, dropping, or removing factors — instead it provides diagnostic observations and defers decisions to downstream analysis.

---

## Language Replacements

### 1. Cluster Interpretation (English)

**Before:**
```
Large redundancy cluster (14 factors) — keep representative only.
```

**After:**
```
Large redundancy cluster (14 factors) — high information overlap. Representative factor provides a useful reference point for this cluster.
```

### 2. Cluster Interpretation (Chinese)

**Before:**
```
大型冗余簇(14个因子)，建议仅保留代表性因子。
```

**After:**
```
大型冗余簇(14个因子)，该簇存在较高信息重叠，代表因子可作为后续比较基准；其他成员需结合边际信息、稳定性、容量与状态表现进一步评估。
```

### 3. Member Roles

**Before:**
- `mostly_redundant`
- `moderately_redundant`

**After:**
- `REDUNDANT_HIGH_QUALITY_ALTERNATIVE`
- `LOWER_MARGINAL_INFORMATION_MEMBER`

### 4. Member Interpretation (English)

**Before:**
```
Redundancy 0.95 with representative mom_20h — highly redundant
```

**After:**
```
Redundancy 0.95 with representative mom_20h — high overlap; requires marginal-information review before combination
```

### 5. Member Interpretation (Chinese)

**Before:**
```
与代表因子 mom_20h 相关性 0.95，信息冗余度高
```

**After:**
```
与代表因子 mom_20h 相关性 0.95，信息冗余度高，需结合边际信息、稳定性、容量与状态表现进一步评估
```

---

## Validation Results

### Bad Language Scan
All 4 output files scanned — **0 hits** on any bad language pattern:
- `keep representative only` — 0 hits
- `只保留` — 0 hits
- `delete` — 0 hits
- `drop` — 0 hits
- `remove this factor` — 0 hits
- `剔除` — 0 hits
- `删除` — 0 hits
- `淘汰` — 0 hits

### Factor Coverage
- **71/71** factors covered (100%)

### Cluster Statistics
- **44** total clusters
- **35** singletons
- **9** multi-factor clusters
- **14** factors in largest cluster (mom_20h family)

### Workflow Verification
- `python scripts/run_factor_library_refresh.py --stage cluster --dry-run` — PASS

---

## Member Roles (Approved Set)

| Role | Description |
|------|-------------|
| `CLUSTER_REPRESENTATIVE` | Highest quality factor in cluster |
| `REDUNDANT_HIGH_QUALITY_ALTERNATIVE` | High overlap (≥0.90) with representative |
| `LOWER_MARGINAL_INFORMATION_MEMBER` | Moderate overlap with representative |
| `DISTINCT_SINGLETON` | Standalone factor, no redundancy links |
| `DIVERSIFYING_WEAK_SIGNAL` | (Reserved for future use) |
| `INSUFFICIENT_DATA` | (Reserved for future use) |

---

## Files Modified

1. `scripts/build_factor_redundancy_cluster_diagnostics.py` — Updated 6 functions:
   - `_member_role()` — New role names
   - `_interpret_cluster_zh()` — Diagnostic language
   - `_interpret_cluster_en()` — Diagnostic language
   - `_interpret_member_zh()` — Diagnostic language with role-specific messages
   - `_interpret_member_en()` — Diagnostic language with role-specific messages
   - Two inline references to role names in `compute_marginal_information()` and `write_outputs()`

2. All 6 output files regenerated:
   - `factor_redundancy_cluster_summary.csv`
   - `factor_redundancy_cluster_members.csv`
   - `factor_redundancy_cluster_representatives.csv`
   - `factor_marginal_information_summary.csv`
   - `factor_redundancy_cluster_payload.json`
   - `factor_redundancy_cluster_manifest.json`

---

## Limitations

1. Two reserved roles (`DIVERSIFYING_WEAK_SIGNAL`, `INSUFFICIENT_DATA`) are defined but not yet used by the script — they may be needed for future edge cases.
2. The language repair does not change the underlying clustering logic or thresholds — only the interpretation text.

---

## Recommended Next PM

**PM-32: Unified Factor Profile / Scorecard v2**

This would consolidate all diagnostic dimensions (quality, redundancy, marginal information, regime, capacity, stability) into a single unified factor profile or scorecard, providing a comprehensive view of each factor's characteristics and trade-offs.
