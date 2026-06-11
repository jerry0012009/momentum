# Formalize trendline_event foundation report 的 blueprint

## Why this was chosen now

这轮继续严格沿当前最近的主线推进：把 `trendline_event_foundation_report` 从“设计文档里的一串想法”继续收紧成后续 Agent 可直接开工的 blueprint。

上一轮已经把 `P1-D`（event study metrics protocol） formalize 掉了；此时 `docs/TODO.md` 中最自然、最邻近的下一步就是：
- 把 `P1-E` 的最小 artifacts 清单与“最小读法”定稿。

这一步的价值在于：
- 到这一步为止，文档里已经基本回答了“应该看什么”和“该怎么判断”；
- 但如果不把最终页面应该长什么样、每张表回答什么问题、应该按什么顺序读 这些也定清楚，后续 Agent 还是会在实现时各自拼页面结构，导致产物风格和阅读路径继续发散。

因此本轮选择：
- **主点：formalize foundation report blueprint**
- 紧邻子点：同步回写 TODO，并更新 plans 镜像

## What changed

### 1) 在 `docs/RESEARCH_TRENDLINE_EVENT.md` 中把 foundation report 的最小 artifacts 升级成 blueprint

原来该部分只列出一串建议 artifact 名称；本轮已扩写为更明确的页面 blueprint，并给每个 artifact 加上：
- 它要回答的问题
- 建议字段
- 默认排序 / 默认读法

当前定稿的第一轮最小 artifacts 包括：
1. `event_taxonomy_card`
2. `sample_coverage_table`
3. `event_density_summary`
4. `breakout_confirmation_comparison`
5. `rebound_confirmation_comparison`
6. `slope_bucket_summary`
7. `quality_bucket_summary`
8. `false_break_statistics`
9. `representative_vs_all_valid_sensitivity`
10. `2~4 case charts`

### 2) 明确每个 artifact 的职责

文档中已明确：
- `event_taxonomy_card`：统一这页到底在比较哪些 event bucket
- `sample_coverage_table`：先回答样本够不够，哪些 bucket 只能展示
- `event_density_summary`：回答事件是稀有事件、可用事件，还是噪声级高频事件
- `breakout_confirmation_comparison`：回答 raw → confirmed ladder 中哪一层真的改善质量
- `rebound_confirmation_comparison`：回答 rebound ladder 是否也有同样的层级提升
- `slope_bucket_summary`：回答 sign / sign×magnitude 是否真正改变事件结果
- `quality_bucket_summary`：回答 `num_points / score / representative` 是否提供增量解释力
- `false_break_statistics`：回答假突破到底多不多、失败有多快
- `representative_vs_all_valid_sensitivity`：回答 duplicate grouping 压缩是否改变结论方向
- `case charts`：把统计结论落回真实线与真实事件

### 3) 定稿 foundation report 的“最小读法”

文档中现在明确建议：
1. 先看 `sample_coverage_table`
2. 再看 `event_density_summary`
3. 再看 `breakout / rebound confirmation comparison`
4. 再看 `slope_bucket_summary`
5. 再看 `quality_bucket_summary`
6. 最后才看 `go / feature / park judgement`

并明确说明：
- 第一轮不要求一开始就有净值曲线；
- 不要求完整交易规则；
- 不要求全市场 / 全周期覆盖；
- 不要求所有 bucket 都配 case chart。

### 4) 回写 TODO

已将 `P1-E` 下两项标记完成：
- `trendline_event_foundation_report` 的最小 artifacts
- foundation report 的“最小读法”

并补入文档中已定稿的 blueprint 摘要，方便后续 Agent 直接认领脚本与页面实现。

## Validation / evidence

### A. 最小同步

执行：
- `python3 scripts/build_plans_site.py`
- `bash scripts/publish_report_site.sh`

结果：
- plans 镜像页成功重建并发布

### B. 线上检查

已确认线上 `trendline_event_research.html` 中出现新的 foundation report blueprint 段落，包括：
- `sample_coverage_table`
- `event_density_summary`
- `representative_vs_all_valid_sensitivity`
- foundation report 的最小读法顺序

也已确认 `momentum_todo.html` 中 `P1-E` 两项均已转为 `[x]`。

## Risks / caveats

- 这轮仍然是 **文档级 blueprint 定稿**，还没有创建 `scripts/build_trendline_event_foundation_report.py`；
- blueprint 里列出的字段与排序是第一轮建议定稿，后续若真实实现发现某些字段冗余或样本不足，仍可在实现层再做小调整；
- 发布脚本会顺手刷新 `reading/deep_dives/*` 与 `reading/quant_digests/*` 的站点时间戳，这些文件依然会在工作区显示 dirty，本轮未将它们一并提交。

## Next recommended step

现在 `P1-A ~ P1-E` 的设计与 blueprint 已经基本收齐。下一轮最自然的主点有两个：

1. **起草 `scripts/build_trendline_event_foundation_report.py` 的输入 / 输出草图**
   - 先不写完整实现，先把脚本目标、目录结构、输入数据源和产出文件名定清楚。

2. **把 `trendline_event_foundation_report` 的页面 skeleton 先搭出来**
   - 例如先生成占位 HTML 与标题结构，让后续统计表逐块填进去。

如果只选一个，我建议下一轮优先做：
- **脚本输入 / 输出草图**

原因：蓝图已经定了，下一步最应该把“文档 blueprint”转换成“脚本 contract”，这样后续 Agent 才能真正接手实现。

## Commit hash (if committed)

- 已 selective commit：`f1ac1a9` (`docs(momentum): formalize foundation report blueprint`)

## Commit note

repo 中仍有与本轮无关的 dirty files（例如 `reports/site/reading/deep_dives/*`、`reports/site/reading/quant_digests/*` 的自动刷新项，以及工作区外层的未跟踪文件），因此没有整仓提交；本轮只 selective commit 了：
- `docs/RESEARCH_TRENDLINE_EVENT.md`
- `docs/TODO.md`
- `reports/site/plans/*`

本记录文件将单独提交并邮件发送，避免把无关脏文件混入同一提交。
