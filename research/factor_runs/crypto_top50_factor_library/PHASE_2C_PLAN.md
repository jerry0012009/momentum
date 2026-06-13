# Phase 2C Plan — Factor Library Skeleton

> **Status:** ACTIVE
>
> Date: 2026-06-13
>
> Previous phase: Phase 2B COMPLETE (Lightweight Quality Gate)
>
> Human decision: Phase 2C ALLOWED; Phase 2D/2E NOT ALLOWED

---

## 1. Phase 2C 目标

Phase 2C 的目标不是寻找 alpha，而是建立**批量因子接入骨架**（scaffold），确保未来新增因子时不会破坏：

1. **时序约定**：timestamp = bar_close_time，known_at = bar_close_time，无未来函数
2. **数据口径**：calendar-time forward returns，gap symbol 排除，direction-adjusted spread
3. **评价协议**：IC/RankIC/spread/turnover 一致输出，可跨因子比较
4. **状态管理**：统一 status 枚举，禁止虚构 alpha 状态

### 交付物

| 交付物 | 文件 | 状态 |
|--------|------|------|
| 因子库骨架文档 | `docs/FACTOR_LIBRARY_SKELETON.md` | ✅ DONE |
| 标准 catalog schema | `research/.../factor_catalog_v0_1.csv` (新列) | ✅ DONE |
| 因子实现接口 | `docs/FACTOR_LIBRARY_SKELETON.md` §3 | ✅ DONE |
| 标签规范 | `docs/FACTOR_LIBRARY_SKELETON.md` §4 | ✅ DONE |
| 评价规范 | `docs/FACTOR_LIBRARY_SKELETON.md` §5 | ✅ DONE |
| 测试规范 | `docs/FACTOR_LIBRARY_SKELETON.md` §6 | ✅ DONE |
| 状态枚举 | `docs/FACTOR_LIBRARY_SKELETON.md` §1, `FACTOR_REGISTRY.md` | ✅ DONE |
| Phase 2C 计划 | `PHASE_2C_PLAN.md` (本文件) | ✅ DONE |

---

## 2. 允许做什么

- ✅ 设计和记录因子库骨架文档
- ✅ 标准化 catalog schema、implementation interface、evaluation protocol
- ✅ 编写可复用的测试基础设施
- ✅ 更新现有文档的状态枚举
- ✅ 保持现有 5 个 DIAGNOSTIC_PROBE 因子运行
- ✅ 为未来因子编写示例接口（模板）

---

## 3. 禁止做什么

- ❌ 新增外部因子（WQ101、GTJA191、Alpha158 等）
- ❌ 批量评价外部因子
- ❌ 策略回测（backtest）
- ❌ 交易成本建模（slippage/spread/commission）
- ❌ 把任何 probe 升级为 alpha 或 candidate
- ❌ 进入 Phase 2D（External Factor Priors）、Phase 2E（Batch Factor Evaluation）或更后阶段
- ❌ 修改现有 V0 评价结果

---

## 4. Factor Status Enum

```
DIAGNOSTIC_PROBE → CANDIDATE_REVIEW → CANDIDATE_FACTOR
                   → PARK
                   → DROP
```

| Status | 含义 | 当前 V0 |
|--------|------|---------|
| `DIAGNOSTIC_PROBE` | 流水线测试通过；非 alpha 证据 | 5 个因子都在此 |
| `CANDIDATE_REVIEW` | 通过质量门；需深入审查 | 0 |
| `CANDIDATE_FACTOR` | 可接入模型 | 0 |
| `PARK` | 证据不足，暂搁 | 0 |
| `DROP` | 失败 | 0 |

**禁止状态:** `ALPHA`, `STRONG_ALPHA`, `DEPLOYABLE_ALPHA`, `LIVE`, `SHADOW`

---

## 5. 进入 Phase 2D 的条件

Phase 2D = **External Factor Priors**（引入外部先验因子族）。

Phase 2D 的真实范围：
- 收集外部因子先验族（WQ101、GTJA191、Alpha158 等）
- 将概念映射为 crypto 兼容的因子族
- 分类哪些可以用纯 OHLCV 数据实现
- **不实现所有因子**（那是 Phase 2E）
- **不批量评价**（那是 Phase 2E）

Phase 2D 开始条件：
1. Phase 2C 交付物全部完成并经 human review
2. Human 明确批准进入 Phase 2D

**当前状态：** Phase 2C skeleton 已建，等待 closeout 审查。Phase 2D 不允许开始。

---

## 6. 未来因子接入流程（骨架）

当 Phase 2C 完成后，新增因子的标准流程：

```
1. 在 factor_catalog 中添加记录（所有必填列）
2. 实现 compute_factor() 函数（遵循 implementation interface）
3. 编写单元测试（synthetic data）
4. 运行完整 pipeline: fetch → labels → factors → eval
5. 验证输出 schema、known_at、coverage、eval metrics
6. 更新 FACTOR_REGISTRY.md
7. 提交（commit message 引用 factor_id）
```

每一步都有自动化检查点，确保新因子不破坏现有协议。
