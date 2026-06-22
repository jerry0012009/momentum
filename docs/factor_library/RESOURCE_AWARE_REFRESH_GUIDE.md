# Resource-Aware Refresh Guide

**生成时间:** 2026-06-22  
**最后更新:** 2026-06-22 (PM-38B alignment)  
**状态:** 运维指南。非生产文档。

---

## 1. 为什么 PM-35 服务器 OOM

The development server has **15GB RAM, no swap**. A full factor library refresh loads all parquet files into memory simultaneously:

- ~75 factors × 50 symbols × many hours of OHLCV data
- Pairwise redundancy matrix: O(n²) correlations
- Paper portfolio: full return simulation per factor

Full refresh = ~12GB peak RAM → OOM kill on 15GB machine.

---

## 2. Heavy Stage Table (Actual Times)

| Script | Mode | Approx. time (15GB) | RAM peak | Notes |
|--------|------|---------------------|----------|-------|
| `evaluate_factors.py` | full (75 factors) | 5–8 min | ~4GB | Loads all factor_values + labels |
| `evaluate_factors.py` | `--factor-ids` (3–5) | 30–60s | ~1GB | Only loads specified factors |
| `build_factor_pairwise_redundancy_matrix.py` | full | 3–5 min | ~6GB | O(n²) pairwise correlations |
| `build_factor_pairwise_redundancy_matrix.py` | `--factor-ids` (3–5) | 20–40s | ~1GB | O(k×n) |
| `build_single_factor_paper_portfolio_diagnostics.py` | full | 8–12 min | ~4GB | Simulates returns per factor |
| `build_single_factor_paper_portfolio_diagnostics.py` | `--factor-ids` (3–5) | 1–2 min | ~1GB | Subset only |
| `build_factor_shape_stability_diagnostics.py` | full | 3–5 min | ~3GB | Rolling windows |
| `build_factor_shape_stability_diagnostics.py` | `--factor-ids` (3–5) | 20–40s | ~0.5GB | Subset only |
| `build_factor_decile_shape_diagnostics.py` | full | 2–3 min | ~2GB | Decile computation |
| `build_factor_decile_shape_diagnostics.py` | `--factor-ids` (3–5) | 15–30s | ~0.5GB | Subset only |
| `build_factor_capacity_liquidity_diagnostics.py` | full | 2–3 min | ~2GB | Capacity analysis |
| `build_factor_capacity_liquidity_diagnostics.py` | `--factor-ids` (3–5) | 15–30s | ~0.5GB | Subset only |

**Peak combined RAM for full refresh: ~12GB** (stages run sequentially but OS may cache).

---

## 3. Recommended Commands for Small Batches (3–5 Factors)

After intake completes (producing factor_values + partial eval), run these incrementally:

```bash
# Step 1: Decile-shape diagnostics (incremental)
python scripts/build_factor_decile_shape_diagnostics.py \
  --factor-ids new_factor_1 new_factor_2 new_factor_3

# Step 2: Capacity-liquidity diagnostics (incremental)
python scripts/build_factor_capacity_liquidity_diagnostics.py \
  --factor-ids new_factor_1 new_factor_2 new_factor_3

# Step 3: Shape stability (rolling) (incremental)
python scripts/build_factor_shape_stability_diagnostics.py \
  --factor-ids new_factor_1 new_factor_2 new_factor_3

# Step 4: Pairwise redundancy (incremental, O(k×n))
python scripts/build_factor_pairwise_redundancy_matrix.py \
  --factor-ids new_factor_1 new_factor_2 new_factor_3

# Step 5: Cluster diagnostics (needs full matrix, but cheap after step 4)
python scripts/build_factor_redundancy_cluster_diagnostics.py

# Step 6: Paper portfolio (to temp, then merge — see section 9)
python scripts/build_single_factor_paper_portfolio_diagnostics.py \
  --factor-ids new_factor_1 new_factor_2 new_factor_3 \
  --output-dir /tmp/paper_new

# Step 7: Unified profile + staleness + page (cheap, run normally)
python scripts/build_unified_factor_profile.py
python scripts/check_factor_library_staleness.py
python scripts/_build_factor_eval_html.py
python scripts/check_factor_evaluation_page_completeness.py
```

---

## 4. When to Use `--factor-ids`

Use `--factor-ids` when:

- Adding a small batch of new factors (3–5)
- Re-running diagnostics for specific factors that had errors
- Operating on the 15GB development server
- You want to avoid touching unrelated diagnostic files (clean git diffs)

**Scripts that support `--factor-ids`:**
- `build_factor_values.py`
- `evaluate_factors.py`
- `build_factor_decile_shape_diagnostics.py`
- `build_factor_capacity_liquidity_diagnostics.py`
- `build_factor_pairwise_redundancy_matrix.py`
- `build_factor_shape_stability_diagnostics.py`
- `build_single_factor_paper_portfolio_diagnostics.py`

---

## 5. When to Use `--only-missing`

Use `--only-missing` when:

- You want to compute diagnostics only for factors that don't have existing output
- Running after a partial failure to fill gaps
- Staleness-driven refreshes

**Scripts that support `--only-missing`:**
- `build_factor_decile_shape_diagnostics.py`
- `build_factor_capacity_liquidity_diagnostics.py`
- `build_factor_shape_stability_diagnostics.py`

---

## 6. When Full Refresh Is Acceptable

Run full refresh (no `--factor-ids` filter) only when:

- RAM > 32GB available
- After major structural changes (new data source, formula correction affecting many factors)
- After adding a completely new diagnostic dimension
- On CI/CD with sufficient resources
- Bulk adding >10 factors in a single batch

**Warning:** On the 15GB server, full refresh WILL OOM. Always use `--factor-ids` or `--only-missing`.

---

## 7. How to Avoid OOM on 15GB/No-Swap

1. **Never run full refresh** without `--factor-ids` on the development server
2. **Run expensive stages one at a time** — don't combine evaluate + redundancy + paper in one session
3. **Limit batch size** to 3–5 factors per intake
4. **Use `--factor-ids` on all expensive scripts** to load only needed data
5. **Monitor memory** — if `free -h` shows <2GB available, stop and wait
6. **Run cheap stages together** — profile + staleness + page + state are safe to combine

---

## 8. How to Avoid Unrelated Reports/Site Diffs

When refreshing for new factors, only touch files related to those factors:

- `factor-evaluation.html` (rebuilt from all data, but expected to change)
- Specific factor rows in diagnostic CSVs
- `factor_unified_profile_summary.csv` (new rows for new factors)
- `factor_library_state.json/md` (regenerated)

Do **not** regenerate or modify:
- Unrelated diagnostic files (creates noisy git diffs)
- Signal evaluation outputs
- Paper monitoring outputs
- Strategy research files

---

## 9. Paper Portfolio Temp + Merge

Paper portfolio writes per-factor output. To avoid overwriting existing results:

1. Run to a temp directory:
   ```bash
   python scripts/build_single_factor_paper_portfolio_diagnostics.py \
     --factor-ids new_factor_1 new_factor_2 new_factor_3 \
     --output-dir /tmp/paper_new
   ```
2. Merge new rows into existing summary CSV:
   ```bash
   # Check what exists
   wc -l research/factor_runs/.../single_factor_paper_portfolio_summary.csv
   
   # Append new rows (skip header)
   tail -n +2 /tmp/paper_new/single_factor_paper_portfolio_summary.csv \
     >> research/factor_runs/.../single_factor_paper_portfolio_summary.csv
   
   # Verify count increased
   wc -l research/factor_runs/.../single_factor_paper_portfolio_summary.csv
   ```
3. Validate no existing rows were dropped (row count should only increase)

**Never** overwrite the full paper summary with a partial run.

---

## 10. Recovery from Partial Failure

**If a diagnostic stage fails mid-run:**

1. Check which factors completed successfully (inspect output files)
2. Re-run only the failed factors:
   ```bash
   python scripts/build_factor_decile_shape_diagnostics.py \
     --factor-ids only_the_failed_factor
   ```
3. Or use `--only-missing` to automatically skip completed factors:
   ```bash
   python scripts/build_factor_decile_shape_diagnostics.py --only-missing
   ```

**If intake fails:**

```bash
# Re-run only the failed factors with a new run-id
python scripts/run_factor_intake.py \
  --factor-ids failed_factor --run-id intake_retry_N
```

**If paper portfolio merge goes wrong:**

```bash
# Restore from git
git restore research/factor_runs/crypto_top50_factor_library/single_factor_paper_portfolio_summary.csv

# Re-run for specific factors
python scripts/build_single_factor_paper_portfolio_diagnostics.py \
  --factor-ids affected_factor --output-dir /tmp/paper_retry
```

**Nuclear option (full rollback):**

```bash
git stash   # or git restore research/
```

---

## 11. 何时必须 missing-only

On the 15GB development server, **always** use incremental mode:

- Normal intake batches (3–5 new factors)
- Single diagnostic stage reruns
- Staleness-driven refreshes

Never run full refresh on 15GB without `--factor-ids` or `--only-missing`.

---

## 12. 推荐批量大小

| Parameter | Recommendation |
|-----------|---------------|
| Factors per intake batch | **3–5** |
| Max factors per pairwise run | **5** (on 15GB) |
| Symbols per run | All 50 (required) |
| Timeframes | All required (1h, 4h, etc.) |

Larger batches risk OOM on the pairwise and paper portfolio stages.

---

## 13. 大文件原则

Do **not** commit to GitHub:

- ❌ Parquet files (`factor_values/*.parquet`)
- ❌ SQLite databases
- ❌ Large CSV files (>10MB)
- ❌ Generated HTML (>5MB)

These belong in `.gitignore`. Keep them local or in object storage.

## 8. Post-rebuild JSON validity check

After any page rebuild (`_build_factor_eval_html.py`), verify the embedded JSON is valid:

```bash
python3 -c "
import re, json; from pathlib import Path
txt = Path('reports/site/factor-library/factor-evaluation.html').read_text()
data = json.loads(re.search(r'<script id=\"factorPayload\" type=\"application/json\">(.*?)</script>', txt, re.DOTALL).group(1))
print(f'JSON valid. {len(data[\"factors\"])} factors')
"
```

If this fails with `NaN` error, the source diagnostic CSV/JSON has unguarded NaN values. Fix the source script, re-run diagnostics, then rebuild page. See POST_INTAKE_WORKFLOW_RUNBOOK.md §8 for details.
