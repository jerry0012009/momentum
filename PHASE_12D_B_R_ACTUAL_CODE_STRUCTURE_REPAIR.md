# Phase 12D-B-R: 真实代码结构与脚本地图修复

**Status:** COMPLETE
**Date:** 2026-06-17
**Previous:** Phase 12D-A-R (Repository Map Repair)

---

## 背景

用户阅读 repository-map.html 后反馈：
1. 当前页面过于抽象，颜色标签和 source/generated/human-edit/read-only/git 等标记混在数据管道区域里，容易误导
2. 页面把 src/momentum/ 讲得像整个框架中心，但当前 factor library 研究主线实际上更像 scripts-driven research pipeline
3. 需要修正页面，使其更贴近真实代码结构和真实执行链路

## 目标

修正 repository-map.html / pipeline-layers.html / data-lineage.html 中不够真实、不够落地的表达。新增"真实执行脚本地图"，帮助用户理解每个功能到底由哪个脚本或文件负责。

## 执行摘要

### 重点修正一：颜色标签位置

- **问题：** source / generated / human-edit / read-only / git ✓ / git ✗ 标签混在数据管道区域
- **修正：** 在页面底部单独做"文件标签说明"卡片，数据管道区域只展示数据节点和箭头
- **标签简化为：** 人工维护源文件 / 脚本生成产物 / 不要手动修改 / 进入版本控制 / 不进入版本控制

### 重点修正二：src/momentum 表述

- **问题：** 页面暗示 "src/momentum/ 是当前 factor library 的完整框架本体"
- **修正：** 明确说明 "src/momentum/ 是已有可复用代码组件库，当前 run 的主执行逻辑仍主要由 scripts/ 驱动"

### 重点修正三：research/factor_runs 表述

- **问题：** 页面未明确 research/factor_runs 的真实角色
- **修正：** 明确说明 "research/factor_runs/crypto_top50_factor_library/ 是当前研究 run 的审计档案和结果目录，不是主要代码目录"

### 重点修正四：新增真实执行脚本地图

- 新增 `reports/site/factor-library/actual-script-map.html`
- 新增 `reports/site/factor-library/assets/actual_script_map.json`
- 新增 `docs/factor_library_transparency/actual_script_map.md`
- 回答 10 个关于真实执行链路的问题
- 表格字段：功能 / 文件路径 / 是否当前主线 / 输入 / 输出 / 是否手动运行 / 是否生成文件 / 是否有测试 / 备注

### 重点修正五：当前真实架构说明

在 repository-map.html、pipeline-layers.html、data-lineage.html 中加入：

> 当前真实架构不是纯 src-package-driven，而是 scripts-driven research pipeline + partial reusable src components。也就是说，当前 run 的主要执行入口在 scripts/，研究档案在 research/，可复用组件部分在 src/。未来如果要工程化，应逐步把稳定逻辑从 scripts/ 沉淀到 src/，但当前阶段不做重构。

### 重点修正六：避免错误路径推断

- 所有脚本清单基于实际扫描 scripts/ (602 文件)、src/momentum/ (39 文件)、research/factor_runs/ (273+ 文件)
- 未编造不存在的脚本
- 未确认的功能标记为"未确认 / 需要人工确认"

## 交付物

| 文件 | 状态 |
|------|------|
| PHASE_12D_B_R_ACTUAL_CODE_STRUCTURE_REPAIR.md | ✅ |
| reports/site/factor-library/actual-script-map.html | ✅ |
| reports/site/factor-library/assets/actual_script_map.json | ✅ |
| docs/factor_library_transparency/actual_script_map.md | ✅ |
| phase12d_b_r_quality_checks.csv | ✅ |
| tests/unit/test_phase12d_b_r_actual_code_structure.py | ✅ |
| reports/site/factor-library/index.html (updated) | ✅ |
| reports/site/factor-library/repository-map.html (updated) | ✅ |
| reports/site/factor-library/pipeline-layers.html (updated) | ✅ |
| reports/site/factor-library/data-lineage.html (updated) | ✅ |

## 不做的事

- ✅ 不移动文件
- ✅ 不重构代码
- ✅ 不修改研究结果
- ✅ 不启动 Phase 13
- ✅ 不重跑因子、信号、回测、paper monitoring
- ✅ 不新增交易、API、实盘、下单逻辑
- ✅ 不编造不存在的脚本

## 重要声明

- Phase 13 NOT STARTED
- 无实盘执行
- 无 alpha 声明
- 无生产声明
- 无研究结果变更
