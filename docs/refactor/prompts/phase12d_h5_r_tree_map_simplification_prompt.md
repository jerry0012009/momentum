# Phase 12D-H5-R：Tree Map Simplification for actual-script-map

## 背景

H5 已经做了初步简化：

- 7.1 简化为 RankIC / Spread / Consistency 三个 active metrics；
- 7.2 原 phase-to-module 表格已替换为 archive explanation；
- 7.4 已从“建议未来 wrapper”改成 active structure completed；
- HTML / JSON / Markdown 已同步。

但页面仍然不够“人类可读”。用户反馈：

1. 不要写“当前因子库无关或其他 momentum 功能脚本 / canary32b / NOT_FACTOR_LIBRARY_MAINLINE”等内容。这会混淆视听。actual-script-map 页面只解释因子库主链路。
2. “研究运行账本”不是人类能理解的语言。应改成“因子库计算结果”或“本次因子库产物”。
3. 用户希望在网页上用一张树状图，同时看到：
   - 目录和脚本结构；
   - 运行前后顺序；
   - 如果新增因子 / 信号 / 回测，应该加在哪里。

本阶段目标是把 actual-script-map 从“解释性文字页”改成“主链路结构图 + 扩展点说明页”。

## 本轮目标

执行 Phase 12D-H5-R：Tree Map Simplification for actual-script-map。

目标：

- 删除所有非因子库主链路内容；
- 删除或改写“研究运行账本”；
- 在网页中加入一张清晰的树状结构图；
- 让读者一眼看懂代码目录、脚本顺序、数据产物和扩展位置；
- 不新增页面；
- 不改研究结果；
- 不启动 Phase 13。

## 允许修改

- `reports/site/factor-library/actual-script-map.html`
- `reports/site/factor-library/assets/actual_script_map.json`
- `docs/factor_library_transparency/actual_script_map.md`
- 可新增质量检查：`phase12d_h5_r_tree_map_quality_checks.csv`

## 不允许修改

- 不要修改 Python code
- 不要修改 research outputs
- 不要修改 signal panel
- 不要修改 labels
- 不要恢复旧 Phase 10 scripts
- 不要新增页面
- 不要启动 Phase 13
- 不要连接交易所 API
- 不要新增实盘、下单、交易逻辑
- 不要改变研究结论

## 一、删除非因子库主链路内容

删除任何类似以下内容：

```text
当前因子库无关或其他 momentum 功能脚本
以下脚本不属于因子库主链路，属于 momentum 项目其他功能
canary32b 相关
Canary 策略研究线
NOT_FACTOR_LIBRARY_MAINLINE
```

actual-script-map 页面不要解释其他 momentum 项目分支。读者只需要理解因子库主链路。

如果页面需要说明范围，用一句话即可：

```text
本页只展示因子库主链路；其他项目功能不在本页讨论。
```

不要列出其他项目脚本。

## 二、把“研究运行账本”改成人话

删除或替换“研究运行账本”这个标题。

建议替换为：

```text
本次因子库计算结果
```

或：

```text
因子库计算产物
```

内容应说明：

- bars 数据规模；
- universe 文件；
- factor values；
- signal panel；
- signal evaluation results；
- cost/liquidity diagnostics；
- paper diagnostic outputs。

不要使用“账本”这种内部项目管理语言。

## 三、加入一张树状图

在页面靠前位置加入一个“因子库主链路树状图”。

建议标题：

```text
因子库主链路：目录、脚本、运行顺序与扩展位置
```

树状图建议用 HTML/CSS 实现，不要生成图片，不要新增页面。

示例结构：

```text
因子库主链路
├─ 1. 数据层 Data
│  ├─ scripts/download_full_binance_1h_universe.py
│  └─ 输出：raw/cache bars
│
├─ 2. Universe 层
│  ├─ scripts/build_crypto_top50_universe.py
│  └─ 输出：crypto_top50 universe snapshots
│
├─ 3. Labels 层
│  ├─ scripts/build_labels.py
│  └─ 输出：forward return labels
│
├─ 4. 因子层 Factor Values
│  ├─ scripts/build_factor_values.py
│  ├─ src/momentum/factors/
│  └─ 新增因子：加在 src/momentum/factors/，并接入 factor value builder
│
├─ 5. 信号层 Signal Panel
│  ├─ scripts/build_phase9b_signal_panel.py 或后续 canonical signal builder
│  ├─ 输出：timestamp / symbol / signal_name / signal_value
│  └─ 新增信号：在 signal construction / signal panel builder 中接入，保持统一 schema
│
├─ 6. 信号评价层 Signal Evaluation
│  ├─ scripts/evaluate_signals.py
│  ├─ src/momentum/signal_evaluation/
│  ├─ 输出：RankIC / Spread / Consistency
│  └─ 新增评价指标：加到 src/momentum/signal_evaluation/，再由 evaluate_signals.py 调用
│
├─ 7. 成本与流动性 Cost / Liquidity
│  ├─ scripts/run_phase11a_cost_slippage_capacity.py
│  └─ 新增成本模型：加在 cost/liquidity module，不要混进 signal evaluation
│
├─ 8. Paper Diagnostic / Monitoring
│  ├─ scripts/run_phase12a_paper_signal_harness.py
│  ├─ scripts/run_phase12b_paper_monitoring.py
│  └─ 注意：不是真实交易，不是 Phase 13
│
└─ 9. Transparency Site
   ├─ reports/site/factor-library/
   └─ 输出：网页解释和研究透明度材料
```

图中必须明确三类“新增位置”：

### 新增因子在哪里加？

```text
src/momentum/factors/
```

并接入：

```text
scripts/build_factor_values.py
```

### 新增信号在哪里加？

```text
signal construction / signal panel builder
```

要求输出统一 schema：

```text
timestamp / symbol / signal_name / signal_value
```

### 新增回测 / 新评价指标在哪里加？

如果是 signal evaluation metric：

```text
src/momentum/signal_evaluation/
```

如果是成本/流动性：

```text
cost/liquidity module 或对应脚本
```

如果是真实执行 / paper trading future validation：

```text
不是当前阶段；Phase 13 未启动
```

## 四、重新组织页面结构

建议 actual-script-map 页面结构调整为：

1. 一句话说明：本页只解释因子库主链路
2. 树状图：目录、脚本、顺序、扩展位置
3. 当前关键输出：因子库计算产物
4. 当前 active signal evaluation 入口：`scripts/evaluate_signals.py`
5. 历史归档说明：旧 Phase 10 scripts 在 archive
6. 当前研究结论：RankIC 正、Spread 负、不是可交易 alpha
7. No production / No real execution / Phase 13 NOT STARTED

不要保留“当前因子库无关脚本”章节。

## 五、同步 JSON / Markdown

同步更新：

- `reports/site/factor-library/assets/actual_script_map.json`
- `docs/factor_library_transparency/actual_script_map.md`

JSON 应包含：

- `mainline_tree`
- `active_entrypoints`
- `extension_points`
- `archived_legacy_scripts`
- `current_outputs`
- `phase13_status: NOT_STARTED`

不要包含 canary / not factor mainline list。

## 六、质量检查

新增：

```text
phase12d_h5_r_tree_map_quality_checks.csv
```

至少包括：

- non-factor-library script section removed
- canary32b references removed from actual-script-map
- NOT_FACTOR_LIBRARY_MAINLINE labels removed
- “研究运行账本” removed or renamed
- tree diagram exists
- tree diagram includes directory structure
- tree diagram includes execution order
- tree diagram includes where to add new factors
- tree diagram includes where to add new signals
- tree diagram includes where to add new evaluation/backtest modules
- active entrypoint remains scripts/evaluate_signals.py
- archive note remains for old Phase 10 scripts
- JSON synced
- Markdown synced
- no new page created
- no research outputs modified
- no signal panel modified
- no labels modified
- no Phase 13
- no real execution
- no production claim

## 七、完成标准

完成后提交 commit。

commit message 建议：

```text
Phase 12D-H5-R: add mainline tree map and remove non-factor clutter
```

完成后输出：

- commit hash
- whether canary/non-mainline section removed
- whether 研究运行账本 was renamed
- where the tree diagram appears
- whether extension points are shown
- whether JSON/Markdown synced
- whether Phase 13 remains not started
