# PyTrendline 报告：补 duplicate grouping 与 best-from-group 的阅读逻辑

## Why this was chosen now

在 `pytrendline explainability` 主线里，candidate lines 讲清楚之后，最自然的下一步就是 duplicate grouping。

因为用户如果只看到页面最终只展示少量代表线，很容易误解成：
- 候选线本来就不多；
- 或者系统只画了几条人工挑选的线。

实际上更接近真实情况的是：
- 先有不少 candidate results；
- 其中很多在线的最后价格和斜率上都非常接近；
- 所以后面会被 duplicate grouping 压缩成少量 group；
- 页面再默认优先展示每组的 best-from-group 代表线。

所以这轮聚焦：把 duplicate grouping 的算法口径和读图口径讲清楚。

## What changed

### 1) 在报告中新增 duplicate grouping 解释区块

文件：
- `scripts/build_pytrendline_report.py`

新增区块：
- `Duplicate grouping：support 侧概览`
- `Duplicate grouping：resistance 侧概览`
- `Support duplicate groups（样例）`
- `Resistance duplicate groups（样例）`
- `如何理解 duplicate grouping 与 score`

### 2) 页面里明确写出的 duplicate grouping 逻辑

当前已补入这些核心解释：

- **为什么会有大量相近线**
  - 因为不同 pivot-pairs 可能拟合出 slope 与最后价格都很接近的线
  - 它们在视觉上几乎重合，但源码里仍是不同候选结果

- **group 是按什么聚的**
  - pytrendline 用二维条件比较：
    - `price_at_last_date`
    - `slope`
  - 只有两者差异都足够小，才会归进同一组

- **breakout / non-breakout 会不会混组**
  - 不会
  - 源码要求 `is_breakout` 相同才允许归到同一组

- **best-from-group 怎么选**
  - group 内最终按 `score` 选代表线
  - 并标记 `is_best_from_duplicate_group=True`

- **为什么页面默认只展示 best-from-group**
  - 因为否则图上会堆满视觉上几乎重合的线
  - 读者很难判断真正值得先看的结构

### 3) 把当前窗口下的 grouping 结果写成可读表

本轮除了规则说明，还把当前窗口下的 grouping 结果直接落成表：
- support / resistance 各自有多少条全部结果
- 各自有多少个 duplicate groups
- 各自有多少条 best-from-group 代表线
- 平均 group size / 最大 group size
- 当前窗口下的 duplicate thresholds 大概是多少

还补了 group 样例表，让读者直接看到：
- 每个 group 大概有多少条线
- 当前 best line 是哪条
- best score 大概是多少
- 该组里是否包含 breakout lines

### 4) 回写 TODO

已将以下任务标记为完成：
- 单独解释 duplicate grouping 的计算与阅读方式
- 在报告里单独解释 `score` 与 duplicate grouping 的语义

## Validation / evidence

### A. 报告已成功重建并发布
执行：
- `/root/clawd/jerry/momentum/.venv/bin/python scripts/build_pytrendline_report.py`
- `./scripts/publish_report_site.sh`

结果：
- 页面已更新到：
  - `https://jp.jerrypsy.top/momentum/factors/pytrendline_research/report.html`

### B. 页面现在已经能直接回答的关键问题

当前报告已经能回答：
- 为什么会出现很多近似线
- 为什么 breakout / non-breakout 不会混在同一组
- 为什么页面默认只展示 best-from-group
- `score` 在 group 内扮演什么角色
- 当前窗口下 duplicate grouping 大概压缩了多少线

## Risks / caveats

- 这轮先补的是规则说明与表格样例，还没有补 `duplicate grouping before/after` 图。
- 当前 group 样例表更偏“阅读理解”，还没有把每个 group 的线直接高亮回图上。
- duplicate grouping 依赖当前窗口下的阈值，换市场/换波动状态后数量表现会变化。

## Next recommended step

下一轮最值得做的小步动作：

1. **优先方案**：补 `is_breakout` 的判定语义，明确 support breakout / resistance breakout 到底分别意味着什么；
2. **次优方案**：补一张 `duplicate grouping before/after` 对照图，让表格解释和可视化完全对上。

## Commit hash (if committed)

b8954cf32e354611a4eca616513c894ef52c02af

## Commit note

本轮仍存在与 interval sweep / crypto rebound / reading pages 相关的其他脏文件，因此只会 selective commit 本轮的 pytrendline 报告与 TODO 文件，不打包无关改动。
