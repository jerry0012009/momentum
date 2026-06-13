# Phase 2D Plan — External Factor Priors

> **Status:** ACTIVE
>
> Date: 2026-06-13
>
> Previous phase: Phase 2C COMPLETE (Factor Library Skeleton)
>
> Human decision: Phase 2D ALLOWED; Phase 2E NOT ALLOWED

---

## 1. Phase 2D 目标

Phase 2D 的目标是建立**外部因子先验地图**（External Factor Prior Map），系统梳理外部因子来源，分类哪些可以迁移到 crypto OHLCV 数据上。

Phase 2D 只做**收集、分类、映射**，不做实现。

### 核心问题

1. 外部因子来源有哪些？（WQ101、GTJA191、Alpha158 等）
2. 每个来源的典型数据需求是什么？
3. 哪些因子可以用纯 OHLCV 数据实现？
4. 哪些需要额外数据（VWAP、orderbook、funding 等）？
5. 实现难度如何？
6. 优先级是什么？

---

## 2. 允许做什么

- ✅ 收集外部因子先验来源文献
- ✅ 分类因子族（momentum、reversal、volatility、liquidity 等）
- ✅ 映射到 crypto 可用性 bucket
- ✅ 评估实现难度和优先级
- ✅ 编写 `EXTERNAL_FACTOR_PRIORS.md`
- ✅ 编写 `CRYPTO_FACTOR_PRIOR_MAPPING.md`
- ✅ 编写 `external_factor_prior_table.csv`
- ✅ 更新文档索引

---

## 3. 禁止做什么

- ❌ 实现任何因子代码
- ❌ 修改 `build_factor_values.py`
- ❌ 新增 `factor_values.parquet`
- ❌ 运行 `evaluate_factors.py`
- ❌ 计算 IC / RankIC / spread
- ❌ 修改 V0 评价结果
- ❌ 策略回测
- ❌ 进入 Phase 2E（Batch Factor Evaluation）
- ❌ 把任何 prior 标记为 `IMPLEMENTED` / `CANDIDATE_*` / `ALPHA`

---

## 4. 交付物

| 交付物 | 文件 | 状态 |
|--------|------|------|
| Phase 2D 计划 | `PHASE_2D_PLAN.md` (本文件) | ✅ |
| 外部因子来源梳理 | `docs/EXTERNAL_FACTOR_PRIORS.md` | 待完成 |
| Crypto 可用性映射 | `docs/CRYPTO_FACTOR_PRIOR_MAPPING.md` | 待完成 |
| 先验记录表 | `external_factor_prior_table.csv` | 待完成 |
| 文档索引更新 | `docs/DOCS_INDEX.md` | 待完成 |

---

## 5. 进入 Phase 2E 的条件

Phase 2E = **Batch Factor Evaluation**（批量实现和评价因子）。

Phase 2E 开始条件：
1. Phase 2D 交付物全部完成并经 human review
2. Human 明确批准进入 Phase 2E
3. 从 prior table 中选定首批实现候选（human 决策）
4. 确认所需数据已可用（OHLCV-only 或已获取额外数据源）

**当前状态：** Phase 2D 刚开始。Phase 2E 不允许开始。

---

## 6. Phase 在全局路线中的位置

```
Phase 2A: V0 Audit — COMPLETE
Phase 2B: Lightweight Quality Gate — COMPLETE
Phase 2C: Factor Library Skeleton — COMPLETE
Phase 2D: External Factor Priors — ← 当前
Phase 2E: Batch Factor Evaluation — NOT ALLOWED
Phase 2F: Gate Refinement — NOT STARTED
```
