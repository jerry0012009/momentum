# Post-Intake Workflow Runbook

**生成时间:** 2026-06-22  
**状态:** 研究诊断文档。非生产。非实盘。

---

## 1. 新增因子前的 Checklist

Before adding any new factor, verify:

- [ ] Factor formula is well-defined and reversible (direction semantics documented)
- [ ] Input data exists in `data/` for all required symbols and timeframes
- [ ] Factor is not a trivial duplicate of an existing registered factor
- [ ] Factor belongs to a recognized family (momentum, volatility, etc.)
- [ ] Expected direction is stated (positive/negative/conditional)
- [ ] No signal or live strategy code is touched during this process

---

## 2. 选择 Batch

Select **3–5 factors** from `docs/factor_library/FACTOR_EXPANSION_BACKLOG.md` per batch.

Selection criteria:
- Prefer factors with available data (status ≠ `MISSING_INPUT_DATA`)
- Mix families (don't add 5 momentum variants at once)
- Include at least one factor that complements existing clusters

---

## 3. 注册 FactorSpec

Add a `FactorSpec(...)` entry to `scripts/factor_formula_registry.py`:

```python
FactorSpec(
    factor_id="new_factor_id",
    family="family_name",
    formula=callable_or_expression,
    expected_direction="positive",  # or "negative", "conditional"
    description="Brief English description",
)
```

After registration, verify the entry is parseable:

```bash
python -c "from scripts.factor_formula_registry import FACTOR_SPECS; print(len(FACTOR_SPECS))"
```

---

## 4. 运行 Intake

```bash
python scripts/run_factor_intake.py \
  --factor-ids new_factor_1,new_factor_2,new_factor_3 \
  --run-id intake_batch_N
```

This computes `factor_values` parquet files for the new factors.

---

## 5. 检查 factor_values

Verify parquet files exist for each new factor:

```bash
ls research/factor_runs/crypto_top50_factor_library/factor_values/
```

Each factor should have a `.parquet` file. If missing, check intake logs for errors.

---

## 6. 运行缺失诊断

Run diagnostics **incrementally** (only for new factors). Do NOT re-run full diagnostics.

### 6.1 Paper Portfolio

```bash
python scripts/build_single_factor_paper_portfolio_diagnostics.py \
  --factor-ids new_factor_1,new_factor_2,new_factor_3
```

**⚠️ Merge paper outputs — don't overwrite!**  
After running, merge new rows into existing summary CSV rather than replacing it.

### 6.2 Decile-Shape

```bash
python scripts/build_factor_decile_shape_diagnostics.py \
  --factor-ids new_factor_1,new_factor_2,new_factor_3
```

### 6.3 Capacity-Liquidity

```bash
python scripts/build_factor_capacity_liquidity_diagnostics.py \
  --factor-ids new_factor_1,new_factor_2,new_factor_3
```

### 6.4 Pairwise Redundancy

```bash
python scripts/build_factor_pairwise_redundancy_matrix.py \
  --factor-ids new_factor_1,new_factor_2,new_factor_3
```

### 6.5 Cluster Diagnostics

```bash
python scripts/build_factor_redundancy_cluster_diagnostics.py
```

Note: cluster diagnostics requires full pairwise matrix. Run after 6.4.

### 6.6 Shape Stability

```bash
python scripts/build_factor_shape_stability_diagnostics.py \
  --factor-ids new_factor_1,new_factor_2,new_factor_3
```

---

## 7. Evidence Matrix 检查

Evidence completeness progresses through stages:

| Stage | Coverage | Meaning |
|-------|----------|---------|
| Initial intake | 2/12 | factor_values + basic direction audit |
| After paper portfolio | 4/12 | + paper returns + fee sensitivity |
| After decile/shape + regime | 8/12 | + shape + regime + stability |
| After capacity + redundancy | 12/12 | Full evidence |

Check current status:

```bash
grep "evidence_completeness_rate" research/factor_runs/.../factor_diagnostics/factor_unified_profile_summary.csv
```

---

## 8. Profile + Staleness + Page 刷新

After all diagnostics pass:

```bash
# Rebuild unified profile
python scripts/build_unified_factor_profile.py

# Check staleness
python scripts/check_factor_library_staleness.py

# Rebuild page
python scripts/_build_factor_eval_html.py

# QA check
python scripts/check_factor_evaluation_page_completeness.py
```

---

## 9. 判断 workflow_ready_status

A factor is `WORKFLOW_READY` when:

1. `evidence_completeness_rate == 1.0` (12/12)
2. All source artifacts exist and are fresh (not stale)
3. No `evidence_incomplete` or `fee_sensitivity` blocks remain

Otherwise status is `WORKFLOW_INCOMPLETE` with specific block reasons listed.

---

## 10. 出错恢复

**Partial failure during intake:**

```bash
# Re-run only failed factors
python scripts/run_factor_intake.py --factor-ids failed_factor --run-id intake_retry
```

**Corrupted diagnostics output:**

```bash
# Restore from git
git restore research/factor_runs/crypto_top50_factor_library/factor_diagnostics/specific_file.csv

# Re-run that diagnostic stage only
python scripts/build_factor_decile_shape_diagnostics.py --factor-ids affected_factor
```

**Full rollback:**

```bash
git stash   # or git restore research/
```

---

## 11. Expensive Stages

These scripts load large data or do O(n²) computations. Use `--expensive-ok` flag:

| Script | Why expensive |
|--------|--------------|
| `build_single_factor_paper_portfolio_diagnostics.py` | Simulates returns across all symbols |
| `build_factor_pairwise_redundancy_matrix.py` | O(n²) pairwise correlation |
| `build_factor_shape_stability_diagnostics.py` | Rolling window recomputation |

On a 15GB server, run expensive stages one at a time. See `RESOURCE_AWARE_REFRESH_GUIDE.md`.

---

## 12. 禁止修改

During intake, **DO NOT** modify:

- ❌ Signal definitions or weights
- ❌ Live/production code
- ❌ Strategy portfolio allocations
- ❌ Factor formulas for existing factors
- ❌ Factor expected directions without audit

Only additions to registry and incremental diagnostics are permitted.
