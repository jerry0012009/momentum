# PyTrendline 报告：给 Step 1 的 pivot 图补 index 标签

## Why this was chosen now

这轮继续沿着最近几次自动优化的同一条主线推进：`pytrendline_research` 的 explainability / auditability。

最近两轮已经补了：
- 时间语义 / 生命周期边界
- selected line deep-dive

在这之后，最相邻、最小步、也最直接提升可读性的一项，就是把 `close + pivots` 图里的锚点和表格真正对上。

这正对应 TODO 里的未完成项：
- `在 close/pivots 图里，把 pivot index 或时间标签以适度方式标出来`

这样做的价值很直接：
- 读者不再需要只靠肉眼猜哪个三角标对应哪个 pivot；
- Step 1 图现在能直接和 `pointset_indeces`、selected line deep-dive 里的 pivot 列表互相对照；
- 仍然是很小的页面细化，不会打断当前主线。

## What changed

### 1) 给 Step 1 的 support / resistance pivots 加了小号 index 标签

文件：
- `scripts/build_pytrendline_report.py`
- `reports/artifacts/pytrendline_research/step1_close_and_pivots.png`
- `reports/site/factors/pytrendline_research/report.html`

新增了一个轻量标注函数，在 Step 1 的 `close + pivots` 图里：
- support pivots：在低点三角标附近标出对应的 bar index；
- resistance pivots：在高点三角标附近标出对应的 bar index；
- 标签使用小字号、白底、轻微偏移，尽量保持“能对照，但不过分压图”。

### 2) 更新页面文案与图例

报告正文与图上元素字典里都明确写了：
- 三角标旁的小数字就是对应的 pivot index；
- Step 1 现在可以直接和 `pointset_indeces` / deep-dive 表对照。

### 3) 回写 TODO

已将以下条目标记完成：
- `在 close/pivots 图里，把 pivot index 或时间标签以适度方式标出来`

## Validation / evidence

### A. 最小重建

执行：
- `/root/clawd/jerry/momentum/.venv/bin/python /root/clawd/jerry/momentum/scripts/build_pytrendline_report.py --ticker BTC-USD --period 10d --interval 5m --window-bars 96`

结果：
- 成功重建 `reports/site/factors/pytrendline_research/report.html`

### B. 页面存在性检查

已确认生成后的 HTML 中包含：
- `三角标旁的小数字`
- `每个三角标旁的小数字就是对应的 pivot index`
- `Step 1 现在已经可以直接和 deep-dive / best lines 表里的 pointset_indeces 对照`

### C. 产物更新检查

已确认本轮最直接相关的 artifact 已更新：
- `reports/artifacts/pytrendline_research/step1_close_and_pivots.png`

## Risks / caveats

- 这轮做的是“适度标注”，不是把时间戳也全部铺到图上；如果窗口更拥挤，后面仍可能需要进一步做抽样或防重叠处理。
- 当前标签使用的是 bar index，而不是时间标签；优点是能和内部表格字段更直接对照，但不如时间直观。
- 这轮只细化了 Step 1 图，没有新补 `candidate lines before filtering` 或 `duplicate grouping before/after` 图。

## Next recommended step

下一轮最自然的相邻动作有两个：

1. **candidate lines before filtering 示意图**
   - 让读者更直观看到“原始候选线很多”，当前页面展示的是筛选后的代表线。

2. **duplicate grouping before/after 对照图**
   - 让 `best-from-group` 的压缩效果从文字说明变成直观图像。

## Commit hash (if committed)

- 实现与报告变更已 selective commit：`9ea5f64` (`report(pytrendline): label pivots in step1 chart`)

## Commit note

repo 中仍存在与本轮无关的脏文件（例如 interval sweep / crypto rebound / reading deep dives / 较早 optimization loop 记录等），因此没有整仓提交；只 selective commit 了本轮直接相关的：
- `docs/TODO.md`
- `scripts/build_pytrendline_report.py`
- `reports/site/factors/pytrendline_research/report.html`
- `reports/artifacts/pytrendline_research/step1_close_and_pivots.png`

本记录文件将单独提交，避免把无关脏文件一并打包进同一个提交。
