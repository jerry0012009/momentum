# PM-31 Audit: Redundancy Cluster & Marginal Information Diagnostics

**Date:** 2026-06-22  
**Status:** PASS  
**Script:** `scripts/build_factor_redundancy_cluster_diagnostics.py`

---

## Summary

Built redundancy cluster diagnostics using `abs_spearman_corr` from the pairwise
redundancy matrix. Graph construction uses union-find on edges where
`abs_spearman_corr >= 0.80`. Marginal information scores quantify each factor's
incremental value relative to its cluster peers.

---

## Key Results

| Metric | Value |
|--------|-------|
| Expected factors | 71 |
| Actual factors | 71 |
| Coverage | 100% |
| Total clusters | 44 |
| Singletons (no redundancy link) | 35 |
| Multi-factor clusters | 9 |
| Largest cluster | 14 factors |
| Redundancy field | `abs_spearman_corr` |
| Edge threshold | 0.80 |

---

## Cluster Inventory

### Largest Clusters

| Cluster | Size | Representative | Avg Intra | Max Intra | Strong Edges (≥0.90) | Class |
|---------|------|----------------|-----------|-----------|---------------------|-------|
| 4 | 14 | mom_20h | 0.871 | 1.000 | 13 | LARGE_TIGHT_CLUSTER |
| 0 | 4 | rev_1h | 0.923 | 0.995 | 3 | MEDIUM_TIGHT_CLUSTER |
| 12 | 4 | mom_40h | 0.846 | 0.871 | 0 | MEDIUM_CLUSTER |
| 15 | 3 | rev_72h | 0.916 | 1.000 | 1 | SMALL_TIGHT_CLUSTER |
| 8 | 3 | downside_vol_20h | 0.875 | 0.880 | 0 | SMALL_CLUSTER |

### Cluster 4 (Largest: 14 factors)
- **Representative:** mom_20h (quality_score ~71.5)
- **Families:** momentum, reversal, technical, etc.
- **Families span:** 8 distinct families
- **Interpretation:** Large tight cluster — most momentum/technical factors
  share high correlation. Keep representative only.

---

## Marginal Information Distribution

| Class | Count |
|-------|-------|
| DISTINCT_SINGLETON | 35 |
| LOW_MARGINAL_INFO | 35 |
| MODERATE_MARGINAL_INFO | 1 |

### Examples

**HIGH MARGINAL INFO (singleton):**  
- `klow_close` (score=0.60, DISTINCT_SINGLETON) — no redundancy links
- `range_4h` (score=0.57, DISTINCT_SINGLETON) — standalone range factor

**MODERATE MARGINAL INFO (in cluster):**  
- `volatility_20h` (score=0.46, cluster 4, size=14) — despite being in the
  largest cluster, has moderate quality and good stability

**MOSTLY REDUNDANT:**  
- No factors classified MOSTLY_REDUNDANT at threshold=0.80 — all cluster
  members have LOW_MARGINAL_INFO or higher

**DISTINCT SINGLETON examples:**  
- `amihud_illiquidity_20h` — liquidity family, no strong redundancy links
- `funding_rate_level_20h` — funding rate family, unique signal
- `realized_skew_20h` — realized shape family, standalone

---

## Workflow Integration

Stage `cluster` added to `scripts/run_factor_library_refresh.py` after
`redundancy` and before `paper-diagnostics`:

```bash
python scripts/run_factor_library_refresh.py --stage cluster
```

This is a **cheap** stage (no expensive flag required).

Pipeline order updated in `docs/factor_library/REGENERATION_CONTRACT.md`:
```
redundancy → cluster → refreshed scorecard → ...
```

---

## Output Files

| File | Description |
|------|-------------|
| `factor_redundancy_cluster_summary.csv` | Per-cluster summary (44 rows) |
| `factor_redundancy_cluster_members.csv` | Per-factor cluster membership + diagnostics (71 rows) |
| `factor_redundancy_cluster_representatives.csv` | Cluster representatives only (44 rows) |
| `factor_marginal_information_summary.csv` | Marginal information scores (71 rows) |
| `factor_redundancy_cluster_payload.json` | Full payload JSON |
| `factor_redundancy_cluster_manifest.json` | Manifest with metadata |

---

## Validation

```
clusters: 44
members: 71
singletons: 35
largest cluster: 14
marginal classes:
  DISTINCT_SINGLETON: 35
  LOW_MARGINAL_INFO: 35
  MODERATE_MARGINAL_INFO: 1
```

✅ All files generated  
✅ Coverage 71/71  
✅ py_compile passes  
✅ Validation script passes  

---

## Limitations

1. **Single threshold:** Uses fixed 0.80 threshold; different thresholds produce
   different clusterings. A sensitivity analysis could be added.
2. **Transitive clustering:** Union-find creates transitive links — two factors
   with 0.81 correlation to a third are in the same cluster even if they
   correlate at only 0.50 with each other.
3. **Marginal info scoring:** Weights are heuristic; not calibrated to
   portfolio construction impact.
4. **No graph visualization:** A network diagram would improve interpretability
   for the largest cluster (14 factors).

---

## Recommended Next PM

**PM-32: Factor cluster-aware portfolio construction**
- Use cluster structure to select representative factors for portfolio signals
- Implement cluster-conditional weight allocation
- Add graph visualization to the factor-evaluation HTML page
