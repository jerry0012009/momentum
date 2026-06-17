# Workflow Map v2

**Version:** 2.0 (Phase 12D-B)
**Current Run ID:** `crypto_top50_usdt_perp_1h`
**Date:** 2026-06-17
**Status:** CURRENT

> This is the v2 workflow map, updated for Phase 12D. It supersedes the v1 `workflow_map.md` for current reference purposes. The v1 is preserved as LEGACY.

> **Note:** `crypto_top50_factor_library` is the audit dossier for the current research run, not the entire factor library framework. The framework is reusable; this run is its first complete execution.

---

## Phase Overview

| Phase | Name | Goal | Status |
|-------|------|------|--------|
| 2 | Factor Prior | 建立因子先验知识体系 | COMPLETE |
| 3 | Data Validation | 验证数据源质量 | COMPLETE |
| 4 | Factor Factory | 批量计算 18 个候选因子 | COMPLETE |
| 5 | Alphalens Export | 计算前瞻收益标签 | COMPLETE |
| 6 | Dynamic Universe | 按月度成交量选取 Top 50 | COMPLETE |
| 7 | Factor Mining | 从 18 个因子筛选到 10 个 | COMPLETE |
| 8 | Human Review | PM 人工审查批准 | COMPLETE |
| 9 | Signal Design | 构建 3 个信号变体 | COMPLETE |
| 10 | Signal Evaluation | 48 变体网格评估，9/48 PASS | COMPLETE |
| 11 | Cost/Liquidity | 成本流动性评估，1 个存活 | COMPLETE |
| 12A | Paper Signal | 构建 paper trading 信号 | COMPLETE |
| 12B | Rolling Monitoring | 30 天滚动验证 | COMPLETE |
| 12C | Transparency | 全面透明化文档收尾 | COMPLETE |
| 12D | Transparency Portal | 仓库结构审计、工作流可视化 | IN_PROGRESS |
| 13 | Paper Execution | 扩展验证 | NOT STARTED |

---

## Data Flow Summary

```
Raw Klines (Binance API)
  → Dynamic Universe (Top 50 by volume)
  → 1H Bars Cache
  → 18 Factor Values (cross-sectional z-scored)
  → Forward Return Labels (1h/4h/24h/72h)
  → Phase 9B Signal Panel (3.3M rows, 3 variants)
  → Phase 10 Evaluation (48 variants → 9 PASS)
  → Phase 11 Cost/Liquidity (9 → 1 survivor)
  → Phase 12A Paper Signal (16 weighted symbols)
  → Phase 12B Rolling Monitoring (31,003 rows)
  → Phase 12C Transparency Docs
  → Phase 12D Website Output
```

---

## Key Decision Points

| Phase | Decision | Outcome |
|-------|----------|---------|
| 7 | 因子筛选标准 | 18 → 10 CANDIDATE_REVIEW |
| 8 | PM 人工审查 | 批准 10 因子进入信号设计 |
| 10D | 48 变体评估 | 9/48 PASS |
| 11A | 成本筛选 | 1/9 survives: core_only 1h no_guard |
| 12B | 滚动验证 | 信号在 mid-cost 下存活 |
| 12C | 透明化收尾 | COMPLETE |
| 12D | 仓库审计 | IN_PROGRESS |

---

## Disclaimers

- **Phase 13 NOT STARTED**
- **No real execution.** No exchange connection, no order placement.
- **No alpha claim.** Research metrics are in-sample/backtest results.
- **No production claim.** This is a research pipeline, not a live trading system.

---

## Companion Pages

- **Showcase:** `reports/site/factor-library/workflow-map.html`
- **Data:** `reports/site/factor-library/assets/workflow_map.json`
- **v1 (legacy):** `docs/factor_library_transparency/workflow_map.md`
