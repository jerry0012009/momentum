# PyTrendline 报告：补 accepted vs rejected examples 真实样例区块

## Why this was chosen now

这轮继续沿最近几次自动优化的同一条主线推进：`pytrendline_research` 的 explainability / auditability。

当前 `A0-Core Semantics` 里，前面已经补了：
- 为什么不能把所有 pivot 两两相连；
- filter waterfall；
- pivot → trendline 决策链总览；
- 什么情况下能被当做趋势线，什么情况下不能。

在这些抽象规则之后，最自然、也最缺的一步就是：
- 不再只讲原则；
- 直接拿当前窗口里的真实线举例，说明哪些被保留、哪些被打成 breakout、哪些虽然有效但被并组压掉、哪些在进入有效结果池前就被淘汰。

所以本轮选择完成 `accepted vs rejected examples`。

## What changed

### 1) 在报告中新增 `Accepted vs rejected examples` 区块

文件：
- `scripts/build_pytrendline_report.py`
- `reports/site/factors/pytrendline_research/report.html`

新增逻辑会自动从当前窗口里抽取 4 类真实样例：
- `Accepted example / valid non-breakout representative`
- `Accepted example / breakout-tagged representative`
- `Grouped-away example / valid but not shown as representative`
- `Rejected candidate / rejected at min-points filter`（若当前窗口更适合别的拒绝原因，也可退化为别的 rejection stage）

每条样例都会给出：
- side
- 当前状态
- 具体案例（line id / score / num_points / pointset / breakout_index / duplicate group 等）
- 为什么这条线会落在这个状态上

这样页面现在已经能把：
- 抽象规则
- 当前窗口计数
- 真实个案

三层信息接起来，而不只是停留在“原则说明”。

### 2) 新增 rejected candidate 的真实抽样逻辑

为了不只展示结果表里已经留下来的线，本轮还补了一个轻量的候选线回放逻辑：
- 重新按当前配置遍历 pivot-pairs；
- 优先抓一个真实的 rejected candidate；
- 当前窗口下最稳定拿到的是 `rejected at min-points filter` 的样例。

这能直接回答：
- 为什么有些 pivot-pair 虽然也能画线；
- 但仍然不能被当成有效趋势线。

### 3) 回写 TODO

已将以下条目标记完成：
- `在报告中新增一个 accepted vs rejected examples 区块`

## Validation / evidence

### A. 最小重建

执行：
- `/root/clawd/jerry/momentum/.venv/bin/python /root/clawd/jerry/momentum/scripts/build_pytrendline_report.py --ticker BTC-USD --period 10d --interval 5m --window-bars 96`

结果：
- 成功重建 `reports/site/factors/pytrendline_research/report.html`

### B. 页面存在性检查

已确认生成后的 HTML 中包含：
- `Accepted vs rejected examples：抽象规则对应到真实样例`
- `valid non-breakout representative`
- `Grouped-away example`
- `Rejected candidate`

### C. 当前窗口下抽到的真实样例类型

本次生成出的页面中，实际出现了：
- 1 条 non-breakout representative 样例；
- 1 条 breakout-tagged representative 样例；
- 1 条 grouped-away 样例；
- 1 条 min-points reject 样例。

说明当前抽样逻辑已经确实把抽象规则落到了真实窗口个案上。

## Risks / caveats

- 本轮样例区块以“表格个案解释”为主，还没有把这些 accepted / rejected 个案直接回画成单独小图。
- rejected sample 当前优先选的是最稳定可得的 rejection stage；不同窗口下不一定总是同一种拒绝原因。
- 当前运行环境没有 elevated 权限，因此没有执行站点 rsync 发布；本轮完成的是 repo 内报告与 artifact 的重建、记录与提交。

## Next recommended step

下一轮最自然的相邻动作有两个：

1. **selected line deep-dive**
   - 从当前样例里再挑 1 条 support、1 条 resistance，逐项解释它们的 `m / b / num_points / score / breakout_index`。

2. **line lifecycle / state diagram**
   - 把 candidate → valid non-breakout → breakout-tagged / grouped-not-representative / best-from-group 画成状态流转图。

## Commit hash (if committed)

Recorded in this run as commit `report(pytrendline): add accepted rejected examples` (see current `HEAD`).

## Commit note

repo 中仍存在与 interval sweep / crypto rebound / deep dive 页面相关的无关脏文件，因此本轮只会 selective commit：
- `docs/TODO.md`
- `scripts/build_pytrendline_report.py`
- `reports/site/factors/pytrendline_research/report.html`
- `reports/artifacts/pytrendline_research/*`（本次重建产物）
- `research/optimization_loop/2026-03-12_0320_pytrendline-accepted-rejected-examples.md`
