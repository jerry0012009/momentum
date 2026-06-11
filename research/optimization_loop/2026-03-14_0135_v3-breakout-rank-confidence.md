# 给 breakout 排序补“置信度层”：raw 的平均优势成立，但对 confirm_1 不是压倒性领先

## 为什么这次选这个

这轮继续沿 `pytrendline_event_validation_v3` 的 breakout-short OOS 线程推进，只做一个小切片：

前一轮我们把 `h24` 的 split-specific excess 排序修正为：
`support_breakout_raw → support_breakout_confirm_1 → support_breakout_confirm_2`。

这个排序本身有价值，但还缺一个关键问题：
**raw 的领先到底稳不稳，还是只靠少数大幅样本把均值拉出来？**

如果不补这一步，后续正式 OOS 容易把“均值更负”误当成“跨单元更稳定”。

这轮最值得复用/借鉴的点是：**候选排序不能只看 pooled / avg excess，还要看 split×asset 单元层面的胜率和 best-cell 分布，否则容易被尾部幅度带偏。**

## 核心结论（中文摘要）

核心结论：**在 `h24` 的 validate+test 范围里，`support_breakout_raw` 的 OOS 平均 excess 仍是三档最负，但它相对 `support_breakout_confirm_1` 的单元胜率仅 `4:4` 打平，说明两者更像并列第一梯队，而不是 raw 压倒性第一。**

证据如何支持这个结论：**按 split-specific excess 汇总，raw 的 OOS 平均约 `-1.55%`（confirm_1 约 `-1.24%`，confirm_2 约 `-1.21%`）；但在 `2 个 split × 4 个资产 = 8 个单元` 上，raw 对 confirm_1 的“更负 excess”仅赢 `4` 个单元、输 `4` 个单元；并且按“每个单元谁最负”计数，confirm_1 拿到 `4` 个 best-cell，raw 只有 `2` 个（confirm_2 也有 `2` 个）。**

## 做了什么改动

本轮只做一个主点：**为 breakout 三档 `h24` 排序增加“置信度层”**。

1. 使用已有产物，不重跑重型流程
   - 输入：
     - `reports/artifacts/pytrendline_event_validation_v3_variant_excess_rank_v1/variant_h24_split_excess_by_asset.csv`
   - 范围：
     - 仅 `validate + test`
     - 仅 `support_breakout_raw / support_breakout_confirm_1 / support_breakout_confirm_2`

2. 新增置信度产物
   - `reports/artifacts/pytrendline_event_validation_v3_variant_rank_confidence_v1/oos_excess_aggregate.csv`
   - `reports/artifacts/pytrendline_event_validation_v3_variant_rank_confidence_v1/pairwise_cell_dominance.csv`
   - `reports/artifacts/pytrendline_event_validation_v3_variant_rank_confidence_v1/best_variant_by_cell.csv`
   - `reports/artifacts/pytrendline_event_validation_v3_variant_rank_confidence_v1/best_variant_cell_count.csv`
   - `reports/artifacts/pytrendline_event_validation_v3_variant_rank_confidence_v1/summary.json`

3. 更新 TODO
   - 在 `V3X-E` breakout OOS 进度中补充“排序置信度不高”的说明：
     - raw 平均更优；
     - 但 raw vs confirm_1 的单元胜率打平；
     - `confirm_1` 在 best-cell 计数上更多。

4. 最小发布
   - 重建 `plans/momentum_todo.html` 并同步到站点。

## 验证 / 证据

### 1) OOS 聚合（validate+test, h24）

- `support_breakout_raw`
  - `oos_avg_excess_h24 ≈ -1.55%`
- `support_breakout_confirm_1`
  - `oos_avg_excess_h24 ≈ -1.24%`
- `support_breakout_confirm_2`
  - `oos_avg_excess_h24 ≈ -1.21%`

从“平均幅度”看，raw 确实领先。

### 2) raw vs confirm_1 的单元胜率（更负 excess 记为胜）

- 总单元数：8（`validate/test × 4 symbols`）
- raw 胜：4
- confirm_1 胜：4
- 打平：0

说明 raw 的领先不是“跨单元普遍领先”，而是“平均幅度领先 + 单元胜率打平”。

### 3) best-cell 计数（每个单元取最负者）

- `support_breakout_confirm_1`: 4
- `support_breakout_raw`: 2
- `support_breakout_confirm_2`: 2

说明 confirm_1 在“局部最强单元”上更常出现，排序结论需要保留不确定性。

## 风险 / 边界

- 这轮是低成本复核，不新增事件样本；
- 样本仍小（仅 validate+test 的 8 个 split×asset 单元）；
- 结论应理解为“排序置信度校准”，不是最终策略定论。

## 下一步建议

- 后续正式 OOS 若只能先做一条，仍可先做 `support_breakout_raw @ h24`；
- 但更稳妥的是把 `support_breakout_confirm_1 @ h24` 作为并列第一梯队同步保留，不建议把它降到明显次级；
- 报告措辞建议改成：
  - “raw 在 OOS 平均 excess 上暂时领先；
  - 但 raw vs confirm_1 的单元优势不具压倒性，需更长样本再定最终先后。”

## Commit hash

- 本轮未提交。

## 如果未提交，说明原因

当前 worktree 仍存在大量与本轮无关的脏文件与历史改动，selective commit 风险较高，容易混入无关内容；因此本轮只完成 artifact / TODO / 页面最小同步，不做提交。