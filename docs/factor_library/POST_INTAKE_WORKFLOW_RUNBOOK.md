# Post-Intake Workflow Runbook

**生成时间:** 2026-06-22  
**最后更新:** 2026-06-22 (PM-38B alignment)  
**状态:** 研究诊断文档。非生产。非实盘。

---

## 1. 新增因子前的 Checklist

Before adding any new factor, verify:

- [ ] Factor formula is well-defined and reversible (direction semantics documented)
- [ ] Input data exists in `data/` for all required symbols and timeframes
- [ ] Factor is not a trivial duplicate of an existing registered factor
- [ ] Factor belongs to a recognized family (momentum, volatility, wq101, tech, etc.)
- [ ] Expected direction is stated (positive/negative/conditional)
- [ ] No signal or live strategy code is touched during this process

---

## 2. 选择 Batch

Select **3–5 factors** per batch.

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
    required_columns=["close", "high", "low", "volume"],  # columns compute_fn reads
    lookback_window=20,         # bars required including current bar
    expected_direction="positive",  # or "negative", "conditional"
    compute_fn=my_compute_fn,   # (DataFrame) -> Series
    status="DIAGNOSTIC_PROBE",  # default, do not change during intake
    notes="Brief English description",  # free-text notes
)
```

**FactorSpec actual fields** (from `scripts/factor_specs.py`):
- `factor_id: str` — unique identifier
- `family: str` — grouping (momentum, volatility, etc.)
- `required_columns: list[str]` — DataFrame columns the compute function reads
- `lookback_window: int` — bars required including current bar
- `expected_direction: str` — "positive", "negative", or "conditional"
- `compute_fn: Callable` — (DataFrame) -> Series
- `status: str` — default "DIAGNOSTIC_PROBE"
- `notes: str` — free-text notes

After registration, verify the entry is parseable:

```bash
python -c "from scripts.factor_formula_registry import REGISTRY; print(len(REGISTRY))"
```

---

## 4. 运行 Intake

```bash
python scripts/run_factor_intake.py \
  --factor-ids new_factor_1 new_factor_2 new_factor_3 \
  --run-id intake_batch_N
```

**CLI args** (from `run_factor_intake.py`):
- `--factor-ids <id ...>` — one or more factor IDs (required, space-separated)
- `--run-id <id>` — unique run identifier (required)
- `--dataset-id <id>` — default `crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1`
- `--skip-build-values` — skip factor_values build (assume they exist)
- `--skip-redundancy` — skip redundancy diagnostics
- `--output-dir <path>` — custom output directory
- `--dry-run` — print commands without executing

This computes `factor_values.parquet` and runs partial evaluation for the new factors.

---

## 5. 检查 factor_values

Verify parquet files exist for each new factor:

```bash
ls data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/<factor_id>/factor_values.parquet
```

Canonical path: `data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/<factor_id>/factor_values.parquet`

If missing, check intake logs for errors in the run directory:
```bash
cat research/factor_runs/crypto_top50_factor_library/factor_intake/<run_id>/manifest.json
```

---

## 6. 运行缺失诊断

Run diagnostics **incrementally** (only for new factors). Do NOT re-run full diagnostics on the 15GB server.

### 6.1 Decile-Shape

```bash
python scripts/build_factor_decile_shape_diagnostics.py \
  --factor-ids new_factor_1 new_factor_2 new_factor_3
```

Supports `--factor-ids` and `--only-missing`.

### 6.2 Capacity-Liquidity

```bash
python scripts/build_factor_capacity_liquidity_diagnostics.py \
  --factor-ids new_factor_1 new_factor_2 new_factor_3
```

Supports `--factor-ids` and `--only-missing`.

### 6.3 Shape Stability (Rolling)

```bash
python scripts/build_factor_shape_stability_diagnostics.py \
  --factor-ids new_factor_1 new_factor_2 new_factor_3
```

Supports `--factor-ids` and `--only-missing`.

### 6.4 Pairwise Redundancy

```bash
python scripts/build_factor_pairwise_redundancy_matrix.py \
  --factor-ids new_factor_1 new_factor_2 new_factor_3
```

With `--factor-ids`, computes only pairs involving new factors: O(k × n) instead of O(n²).

### 6.5 Cluster Diagnostics

```bash
python scripts/build_factor_redundancy_cluster_diagnostics.py
```

Note: cluster diagnostics requires the full pairwise matrix. Run after 6.4.

### 6.6 Paper Portfolio

```bash
python scripts/build_single_factor_paper_portfolio_diagnostics.py \
  --factor-ids new_factor_1 new_factor_2 new_factor_3
```

**⚠️ Paper portfolio merge — safe rule:**

1. Run to a temp directory to avoid overwriting existing results:
   ```bash
   python scripts/build_single_factor_paper_portfolio_diagnostics.py \
     --factor-ids new_factors --output-dir /tmp/paper_new
   ```
2. Merge new rows into existing summary CSV
3. Validate count (no existing rows dropped)

Running directly on the default output directory can overwrite the full paper summary with a partial run.

---

## 7. Evidence Progression

Evidence completeness progresses through stages. The actual workflow after intake is:

| Step | Action | Evidence achieved |
|------|--------|-------------------|
| 1 | intake (`run_factor_intake.py`) | factor_values.parquet + partial eval (RankIC, period IC, quantile returns, long-short) |
| 2 | decile-shape + capacity-liquidity (`--factor-ids`) | decile diagnostics + capacity diagnostics |
| 3 | redundancy + cluster + marginal | pairwise redundancy matrix + cluster assignments |
| 4 | shape-stability / rolling (`--factor-ids`) | rolling stability diagnostics |
| 5 | paper portfolio (temp + merge) | paper returns + fee sensitivity |
| 6 | profile + staleness | unified profile + staleness check |
| 7 | page rebuild + page QA | factor-evaluation.html + completeness report |

Check current status:

```bash
grep "evidence_completeness_rate" research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_unified_profile_summary.csv
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

These scripts load large data or do O(n²) computations:

| Script | Why expensive | Supports `--factor-ids` | Notes |
|--------|--------------|------------------------|-------|
| `build_single_factor_paper_portfolio_diagnostics.py` | Simulates returns across all symbols | ✅ | Use `--factor-ids` for small batches |
| `build_factor_pairwise_redundancy_matrix.py` | O(n²) pairwise correlation | ✅ | With `--factor-ids`: O(k×n) |
| `build_factor_shape_stability_diagnostics.py` | Rolling window recomputation | ✅ | Use `--factor-ids` for small batches |

**`--expensive-ok` is a flag for `run_factor_library_refresh.py` only** (the orchestrator), not for individual diagnostic scripts. Individual scripts use `--factor-ids` to limit scope.

On a 15GB server, run expensive stages one at a time with `--factor-ids`. See `RESOURCE_AWARE_REFRESH_GUIDE.md`.

---

## 12. 禁止修改

During intake, **DO NOT** modify:

- ❌ Signal definitions or weights
- ❌ Live/production code
- ❌ Strategy portfolio allocations
- ❌ Factor formulas for existing factors
- ❌ Factor expected directions without audit
- ❌ `src/momentum/strategies/` code
- ❌ Broker, execution, or exchange API code

Only additions to registry and incremental diagnostics are permitted.
