# Resource-Aware Refresh Guide

**生成时间:** 2026-06-22  
**状态:** 运维指南。非生产文档。

---

## 1. 为什么 PM-35 服务器 OOM

The development server has **15GB RAM, no swap**. A full factor library refresh loads all parquet files into memory simultaneously:

- ~75 factors × 50 symbols × many hours of OHLCV data
- Pairwise redundancy matrix: O(n²) correlations
- Paper portfolio: full return simulation per factor

Full refresh = ~12GB peak RAM → OOM kill on 15GB machine.

---

## 2. PM-36/PM-37 资源优化

Incremental `--factor-ids` support was added to all expensive diagnostic scripts:

```bash
python scripts/build_factor_decile_shape_diagnostics.py --factor-ids new_factor_1,new_factor_2
```

This loads only the data needed for specified factors instead of all 75+.

---

## 3. Decile-Shape 增量模式

```bash
# Only compute for specific factors
python scripts/build_factor_decile_shape_diagnostics.py --factor-ids rev_2h,mom_vol_adjusted_20h

# Only compute factors missing from output
python scripts/build_factor_decile_shape_diagnostics.py --only-missing
```

---

## 4. Capacity-Liquidity 增量模式

```bash
python scripts/build_factor_capacity_liquidity_diagnostics.py --factor-ids rev_2h
```

Same `--factor-ids` / `--only-missing` pattern.

---

## 5. Pairwise Redundancy 增量模式

The most expensive stage. With `--factor-ids`, only computes pairs involving new factors:

```bash
python scripts/build_factor_pairwise_redundancy_matrix.py \
  --factor-ids rev_2h,mom_vol_adjusted_20h
```

This is O(k × n) instead of O(n²), where k = new factors, n = total factors.

---

## 6. Rolling Stability 子集模式

```bash
python scripts/build_factor_shape_stability_diagnostics.py --factor-ids rev_2h
```

Loads only the specified factor's parquet, not all 75+.

---

## 7. 何时可以 Full Refresh

Run full refresh (no `--factor-ids` filter) only when:

- RAM > 32GB available
- After major structural changes (new data source, formula correction)
- After adding a completely new diagnostic dimension
- On CI/CD with sufficient resources

---

## 8. 何时必须 missing-only

On the 15GB development server, **always** use incremental mode:

- Normal intake batches (3–5 new factors)
- Single diagnostic stage reruns
- Staleness-driven refreshes

Never run full refresh on 15GB without `--factor-ids` or `--only-missing`.

---

## 9. Paper Portfolio 合并

Paper portfolio is special — it writes per-factor output. To avoid overwriting existing results:

1. Run to a temp directory:
   ```bash
   python scripts/build_single_factor_paper_portfolio_diagnostics.py \
     --factor-ids new_factors --output-dir /tmp/paper_new
   ```
2. Merge new rows into existing summary CSV
3. Verify no existing rows were dropped

**Never** overwrite the full paper summary with a partial run.

---

## 10. 避免无关 Reports Diff

When refreshing for new factors, only touch files related to those factors:

- `factor-evaluation.html` (rebuilt from all data, but expected to change)
- Specific factor rows in diagnostic CSVs

Do **not** regenerate or modify unrelated diagnostic files, which would create noisy git diffs.

---

## 11. 大文件原则

Do **not** commit to GitHub:

- ❌ Parquet files (`factor_values/*.parquet`)
- ❌ SQLite databases
- ❌ Large CSV files (>10MB)
- ❌ Generated HTML (>5MB)

These belong in `.gitignore`. Keep them local or in object storage.

---

## 12. 推荐批量大小

| Parameter | Recommendation |
|-----------|---------------|
| Factors per intake batch | **3–5** |
| Max factors per pairwise run | **5** (on 15GB) |
| Symbols per run | All 50 (required) |
| Timeframes | All required (1h, 4h, etc.) |

Larger batches risk OOM on the pairwise and paper portfolio stages.
