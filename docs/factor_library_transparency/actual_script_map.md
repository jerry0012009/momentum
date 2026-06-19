# 因子库真实执行链路与脚本地图

> Phase 12D-H5-R · 研究解释页

## 声明

本页是研究解释页，不是实盘，不是交易建议。Phase 13 尚未开始。本页只解释因子库主链路，其他 momentum 项目功能不在本页讨论。

## 主链路：目录、脚本、运行顺序与扩展位置

从上到下是执行顺序。★ 标记是扩展位置。

```
因子库主链路
│
├─ 1. 数据层 Data
│  ├─ scripts/download_full_binance_1h_universe.py
│  └─ 输出：data/cache/.../bars_1h.parquet（266 symbols, 3.3M rows）
│
├─ 2. Universe 层
│  ├─ scripts/build_crypto_top50_universe.py
│  └─ 输出：universe_snapshots.parquet + universe_membership.parquet
│
├─ 3. Labels 层
│  ├─ scripts/build_labels.py
│  └─ 输出：labels.parquet（1h/4h/24h/72h forward returns）
│
├─ 4. 因子层 Factor Values
│  ├─ scripts/build_factor_values.py
│  ├─ scripts/factor_formula_registry.py（804 行公式定义）
│  ├─ src/momentum/factors/（可复用因子组件）
│  └─ ★ 新增因子：改 factor_formula_registry.py，或在 src/momentum/factors/ 新增模块
│
├─ 5. 信号层 Signal Panel
│  ├─ scripts/build_phase9b_signal_panel.py
│  ├─ 输出：phase9b_signal_panel.parquet（3 signal variants × 266 symbols）
│  └─ ★ 新增信号：改 signal panel builder，输出统一 schema（timestamp/symbol/signal_value）
│
├─ 6. 信号评价层 Signal Evaluation
│  ├─ scripts/evaluate_signals.py ← 规范活跃入口
│  ├─ src/momentum/signal_evaluation/（公共 API）
│  └─ ★ 新增评价指标：加在 src/momentum/signal_evaluation/
│
├─ 7. 成本与流动性 Cost/Liquidity
│  ├─ scripts/run_phase11a_cost_slippage_capacity.py
│  └─ 注意：成本模型不要混进 signal evaluation
│
├─ 8. Paper Diagnostic
│  ├─ scripts/run_phase12a_paper_signal_harness.py
│  ├─ scripts/run_phase12b_paper_monitoring.py
│  └─ 注意：不是真实交易，不是 Phase 13
│
└─ 9. 展示层 Transparency Site
   ├─ reports/site/factor-library/
   └─ 输出：网页解释和研究透明度材料
```

## 活跃入口点

- **CLI 入口**：`scripts/evaluate_signals.py`（使用公共 API）
- **公共 API 包**：`src/momentum/signal_evaluation/`（rank_ic, quantile_spread, consistency, _vectorized）
- **Parity 测试**：`scripts/run_signal_evaluation_parity_harness.py`
- **旧 Phase 10 脚本**：已归档至 `archive/legacy_phase_scripts/phase10/`

## 因子库计算产物

| 产物 | 文件 | 说明 |
|------|------|------|
| 原始 K 线 | `data/cache/.../bars_1h.parquet` | 266 symbols, 3.3M rows |
| Universe | `universe_snapshots.parquet` | 动态 Top50 |
| Factor Values | `data/features/.../<factor>/factor_values.parquet` | 10 因子 |
| Labels | `labels.parquet` | 1h/4h/24h/72h |
| Signal Panel | `phase9b_signal_panel.parquet` | 3 variants × 266 symbols |
| RankIC | `phase10a_signal_rankic_summary.csv` | 各 horizon |
| Spread | `phase10a_signal_quantile_spread_summary.csv` | 分位数价差 |
| 成本 | `phase11a_*.csv` | 成本/滑点/容量 |
| Paper | `phase12a_*.csv, phase12b_*.csv` | 纸面信号 |

结果目录 `research/factor_runs/crypto_top50_factor_library/` 是审计档案，不是主要代码目录。

## 扩展位置

| 扩展类型 | 在哪里改 | 注意事项 |
|----------|----------|----------|
| ★ 新增因子 | `factor_formula_registry.py` / `src/momentum/factors/` | 先作为 diagnostic factor |
| ★ 新增信号 | `build_phase9b_signal_panel.py` | 输出统一 schema |
| ★ 新增评价指标 | `src/momentum/signal_evaluation/` | 加入公共 API |
| ★ 新增 horizon | `scripts/build_labels.py` | 增加 horizon 参数 |

## 当前研究结论

当前核心信号 **signal_v0_core_only** 在 RankIC 上显著为正，但 mean quantile spread 为负，**不是已经干净验证的 alpha**。当前结论：继续 paper diagnostic，不可解释为可交易策略。

活跃评价：RankIC · Quantile Spread · Direction Consistency → `evaluate_signals.py`
历史归档：Bucket/Tail Diagnostics（10B）· Variant Grid（10D）→ CSV 结果保留

---

*Phase 12D-H5-R · Authority: actual repository scan · 2026-06-19*
