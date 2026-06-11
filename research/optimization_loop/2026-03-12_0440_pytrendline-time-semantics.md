# PyTrendline 报告：补时间语义 / 生命周期边界说明

## Why this was chosen now

这轮继续沿着最近几次自动优化的同一条主线推进：`pytrendline_research` 的 explainability / auditability。

上一轮已经补了：
- line lifecycle
- state diagram

在 lifecycle 之后，最自然、也最贴近因果有效性的下一步，就是把“这些线到底是什么时候才算已知”讲清楚。

这直接对应 TODO 里的未完成项：
- `单独说明当前 report 的 时间语义 / 生命周期边界`

而且它比继续堆更多图表更优先，因为这一步直接关系到：
- 是否会把页面误读成 bar-by-bar 在线状态；
- 哪些字段带事后视角；
- 哪些内容只能作为 research snapshot 使用。

## What changed

### 1) 在报告中新增 `时间语义 / 生命周期边界` 专门区块

文件：
- `scripts/build_pytrendline_report.py`
- `reports/site/factors/pytrendline_research/report.html`

新增表格逐项解释以下对象的“何时才算已知”：
- 当前页面整体视角
- 原始 OHLC bars
- pivot 身份
- candidate / valid line
- `num_points` / `pointset_indeces`
- `is_breakout` / `breakout_index` / `breakout_date`
- `duplicate_group_id` / `is_best_from_duplicate_group`
- expired / retired state（明确当前未单独建模）

核心结论现在被明确写进报告：
- 这页更接近 **窗口末端重新扫描后的回看快照**；
- 不是 **bar-by-bar 在线状态机**；
- bars 本身可视为收盘后已知，但 pivots / valid lines / breakout labels / grouping state 都带不同程度的延迟或事后视角。

### 2) 让时间语义和 lifecycle 连在一起读

这轮没有新开分支，而是把新表直接放在：
- `Accepted vs rejected examples`
- `Line lifecycle`
- `State diagram`

之后。

这样读者现在可以顺着同一条叙事链读下来：
- 一条线会经历哪些状态；
- 这些状态在页面里如何出现；
- 这些状态分别是在什么时点才算“知道了”。

### 3) 回写 TODO

已将以下条目标记完成：
- `单独说明当前 report 的 时间语义 / 生命周期边界`

## Validation / evidence

### A. 最小重建

执行：
- `/root/clawd/jerry/momentum/.venv/bin/python /root/clawd/jerry/momentum/scripts/build_pytrendline_report.py --ticker BTC-USD --period 10d --interval 5m --window-bars 96`

结果：
- 成功重建 `reports/site/factors/pytrendline_research/report.html`

### B. 页面存在性检查

已确认生成后的 HTML 中包含：
- `时间语义 / 生命周期边界：现在看到的线，到底是“当时知道的”还是“回头看知道的”？`
- `窗口末端回看快照`
- `bar-by-bar 在线状态机`

这说明新加的时间语义区块已经进入最终页面。

## Risks / caveats

- 这轮补的是**解释层边界说明**，不是 bar-by-bar replay 引擎。
- 当前页面仍然没有把 pivot confirmed time / line birth time / breakout label birth time 做成逐 bar 审计日志。
- 因此这轮能做的是：
  - 明确哪些内容有事后视角；
  - 防止误读；
  - 为后续真的做 causal audit 铺路。

## Next recommended step

下一轮最自然的相邻动作有两个：

1. **selected line deep-dive**
   - 选 1 条 support、1 条 resistance，把 `m / b / num_points / score / breakout_index` 逐项拆开讲。

2. **bar-by-bar 审计原型（更小步版本）**
   - 不一定一口气做全量 replay；
   - 可以先定义一份最小字段清单，明确未来如果做 causal audit，最少要记录哪些时间戳与状态变更。

## Commit hash (if committed)

- 实现与报告变更已 selective commit：`039deac` (`report(pytrendline): clarify time semantics boundary`)

## Commit note

repo 中仍存在与本轮无关的脏文件（例如 interval sweep / crypto rebound / deep dive 页面 / 较早 optimization loop 记录等），因此没有整仓提交；只 selective commit 了本轮直接相关的：
- `docs/TODO.md`
- `scripts/build_pytrendline_report.py`
- `reports/site/factors/pytrendline_research/report.html`
- `reports/artifacts/pytrendline_research/*`（本轮重建产物）

本记录文件将单独提交，避免把无关脏文件一并打包进同一个提交。
