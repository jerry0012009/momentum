# Data Lineage v2

**Version:** 2.0 (Phase 12D-B)
**Current Run ID:** `crypto_top50_usdt_perp_1h`
**Date:** 2026-06-17
**Status:** CURRENT

> This is the v2 data lineage document, updated for Phase 12D. It supersedes the v1 `data_lineage.md` for current reference purposes. The v1 is preserved as LEGACY.

> **Note:** `crypto_top50_factor_library` is the audit dossier for the current research run, not the entire factor library framework.

---

## End-to-End Data Flow

### Layer 1: Raw Data

| Node | Path | Source | Script | Git | Generated |
|------|------|--------|--------|-----|-----------|
| Raw Klines | `data/raw/{symbol}/` | Binance API | `fetch_crypto_top50_bars.py` | ✗ | No |
| Dynamic Universe | `data/cache/.../universe_membership.parquet` | Raw klines | `build_dynamic_universe_monthly_volume.py` | ✓ | Yes |
| 1H Bars | `data/cache/.../bars_1h.parquet` | Raw klines + universe | `build_dynamic_universe_bars_1h.py` | ✓ | Yes |

### Layer 2: Factor Computation

| Node | Path | Source | Script | Git | Generated |
|------|------|--------|--------|-----|-----------|
| Factor Values | `data/features/.../factor_values.parquet` | bars_1h | `build_factor_values.py` | ✓ | Yes |
| Forward Returns | `data/features/*/labels.parquet` | bars_1h | `build_labels.py` | ✓ | Yes |
| Alphalens Exports | `research/.../alphalens_exports/` | factors + labels | `export_alphalens_factor_data.py` | ✓ | Yes |

### Layer 3: Signal Construction

| Node | Path | Source | Script | Git | Generated |
|------|------|--------|--------|-----|-----------|
| Signal Panel | `research/.../phase9b_signal_panel.parquet` | factors + labels | `build_phase9b_signal_panel.py` | ✗ | Yes |

### Layer 4: Evaluation

| Node | Path | Source | Script | Git | Generated |
|------|------|--------|--------|-----|-----------|
| Phase 10 Evaluation | `research/.../phase10*.csv` | signal panel | `run_phase10a/d_*.py` | ✓ | Yes |
| Phase 11 Cost/Liquidity | `research/.../phase11*.csv` | phase10 + volume | `run_phase11a/b_*.py` | ✓ | Yes |
| Phase 12 Paper Monitoring | `research/.../phase12*.csv` | phase11 + signal | `run_phase12a/b_*.py` | ✓ | Yes |

### Layer 5: Documentation & Output

| Node | Path | Source | Script | Git | Generated |
|------|------|--------|--------|-----|-----------|
| Transparency Docs | `docs/factor_library_transparency/` | All phases + human | Human-authored | ✓ | No |
| Website Output | `reports/site/factor-library/` | Research + docs | Various scripts | ✓ | Yes |

---

## Flow Edges

```
Raw Klines ──filter+align──→ 1H Bars ──compute──→ Factor Values ──┐
     │                                                              │
     └──volume ranking──→ Dynamic Universe ──universe filter──→ 1H Bars
                                                                  │
Forward Returns ←──compute labels── 1H Bars ──────────────────────┘
     │
     ├──join──→ Alphalens Exports
     │
     └──join──→ Signal Panel ──evaluate──→ Phase 10 ──cost+liquidity──→ Phase 11 ──paper signal──→ Phase 12
                                                                                                        │
                                                                              Transparency Docs ←──document──┘
                                                                                   │
                                                                              Website Output ←──publish──┘
```

---

## Risk Matrix

| Node | Risk | Mitigation |
|------|------|------------|
| Raw Klines | API 变更导致数据缺失 | 定期检查数据完整性 |
| Factor Values | 计算逻辑变更需重跑全部 | 修改前运行测试 |
| Forward Returns | 前瞻收益错误导致评估无效 | 交叉验证多 horizon |
| Signal Panel | 214MB gitignored，丢失需重生成 | 保留生成脚本 |
| Phase 10 Evaluation | 评估逻辑变更影响下游 | 严格 phase gate |
| Paper Monitoring | 持续产物，不可回溯重放 | 实时备份 |

---

## Disclaimers

- `reports/site/factor-library/` is **generated website output**, not the sole source of truth.
- **Phase 13 NOT STARTED.** No real execution, no alpha claim, no production claim.

---

## Companion Pages

- **Showcase:** `reports/site/factor-library/data-lineage.html`
- **Data:** `reports/site/factor-library/assets/data_lineage.json`
- **v1 (legacy):** `docs/factor_library_transparency/data_lineage.md`
