# Report Pipeline Refactor Plan（UpDownWave → 通用因子评估工具）

## 背景

当前 `scripts/build_updownwave_report.py` 已覆盖大量研究问题（Q1~Q14），但存在典型单体脚本问题：
- 全量重跑耗时长，任何小改动都要重复计算
- 章节耦合度高，定位错误与维护成本高
- 对新因子复用成本高（复制粘贴风险）

目标是将其逐步重构为 `momentum` 内可复用的“因子评估流水线”。

---

## 目标形态

### 1) 分层架构

- **Feature Layer**：统一计算 BBW/ADR/ADX/ATR 等环境特征
- **Signal Layer**：因子信号适配器（UpDownWave 只是一个实现）
- **Evaluation Layer**：Q1~Q14 独立评估器
- **Report Layer**：HTML 页面渲染 + 图表渲染
- **Pipeline Layer**：阶段编排、缓存、发布

### 2) 运行模式

- `build`：仅生成报告产物
- `publish`：仅发布静态站点
- `all`：build + publish

第一阶段入口（已落地）：
- `scripts/run_report_pipeline.py`
- `src/momentum/analytics/report_pipeline.py`

---

## 分阶段落地步骤

### Phase 1（已完成）

- [x] 增加流水线入口脚本：`scripts/run_report_pipeline.py`
- [x] 增加流水线模块：`src/momentum/analytics/report_pipeline.py`
- [x] 支持 `--stage all|build|publish`
- [x] 支持可选完成回调：`--callback-text`
- [x] README / REPORTING_WEB / scripts README 补充使用说明

### Phase 2（进行中）

- [x] 新增独立洞察组件：`src/momentum/analytics/updownwave_insights.py`
- [x] 新增洞察脚本：`scripts/build_updownwave_insights.py`
- [x] 流水线新增 `--stage insights`（可快速生成 Q1~Q14 文字洞察）
- [x] 洞察按 Q 组解耦：`q1_q3 / q4_q6 / q7_q9 / q10_q14`
- [~] 将 `build_updownwave_report.py` 拆分为函数化 stage：
  - [x] `compute_usage_q1_q3()`（已从主流程抽离，形成显式输入输出边界）
  - [x] `compute_usage_q4_q6()`（已从主流程抽离，形成显式输入输出边界）
  - [x] `compute_usage_q7_q9()`（已从主流程抽离，形成显式输入输出边界）
  - [x] `compute_usage_q10_q11()`（已从主流程抽离，形成显式输入输出边界）
  - [x] `compute_usage_q12_q14()`（已从主流程抽离 tail-risk 产物，形成显式输入输出边界）
  - [x] `compute_core_baseline_metrics()`（已从主流程抽离 baseline 主计算块）
  - [ ] `stage_render_html()`
- [ ] stage 级参数入口（先保留在同一脚本）

### Phase 3

- [~] 引入中间产物缓存（参数指纹 + 版本）
  - [x] 基础缓存已落地：`run_report_pipeline.py --use-cache`（按已存在产物跳过 stage）
  - [ ] 参数指纹级缓存（避免陈旧缓存误命中）
- [ ] 支持增量重跑（仅重算某一组 Q）
- [ ] 支持 `render-only`（仅更新文字与页面，不重算回测）

### Phase 4

- [ ] 抽象 `FactorAdapter`，支持新因子复用同一评估流水线
- [ ] 形成 `factor.yml` 配置协议（资产池、窗口、持有期、成本场景）

### Phase 5

- [ ] 为核心 stage 增加单测/快照测试
- [ ] 加入 nightly 全量与日间增量任务建议
- [ ] 形成稳定的“研究→发布”SOP

---

## 代码可读性约定（重构时遵循）

1. **一个问题一个函数**：Q1~Q14 对应独立 evaluator
2. **输入输出显式**：每个 stage 明确输入文件与输出文件
3. **产物优先落盘**：先出 CSV，再渲染图表与文字
4. **渲染层不做重计算**：HTML 仅消费产物，不重新回测
5. **避免隐藏状态**：参数和阈值通过配置/函数参数传入

---

## 当前推荐命令

```bash
cd jerry/momentum
source .venv/bin/activate

# build + publish
python scripts/run_report_pipeline.py --stage all

# build only
python scripts/run_report_pipeline.py --stage build

# publish only
python scripts/run_report_pipeline.py --stage publish
```

带完成回调（推荐长任务）：
```bash
python scripts/run_report_pipeline.py --stage all \
  --callback-text "Done: updownwave report built and published"
```
