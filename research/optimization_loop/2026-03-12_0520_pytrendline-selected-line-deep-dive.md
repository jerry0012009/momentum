# PyTrendline 报告：补 selected line deep-dive

## Why this was chosen now

这轮继续沿着最近几次自动优化的同一条主线推进：`pytrendline_research` 的 explainability / auditability。

最近两轮已经补了：
- line lifecycle / state diagram
- 时间语义 / 生命周期边界

在这些“总览层”补齐之后，当前最相邻、最自然的一步，就是回到真实个案，直接挑 1 条 support、1 条 resistance 做逐项拆解。

这正对应 TODO 里的未完成项：
- `增加一个 selected line deep-dive 区块`

而且这一步有实际价值：
- 不再只停留在抽象规则；
- 能把 `m / b / num_points / breakout_index / duplicate group` 这些字段放回真实线身上解释；
- 也能把“为什么它是 best-from-group”从抽象概念变成当前窗口里的具体对照。

## What changed

### 1) 在报告中新增 `Selected line deep-dive` 区块

文件：
- `scripts/build_pytrendline_report.py`
- `reports/site/factors/pytrendline_research/report.html`

新逻辑会在当前窗口里为两侧各选 1 条代表线：
- 优先选 **group_size > 1** 且 `is_best_from_duplicate_group=True` 的代表线；
- 如果当前侧没有这种情况，再退化为该侧 score 最高的代表线。

这样做的目的不是选“绝对最高分”而已，而是尽量选出**最适合教学展开**的个案：既能讲结构点，也能讲 duplicate grouping 里为什么它赢了。

### 2) 对 support / resistance 各自逐项拆解

每条 selected line 现在都会解释：
- 它命中了哪些 pivots（index + time）；
- `m / b` 的当前数值与操作性含义；
- `num_points` 与当前阈值的关系；
- 为什么它通过了 slope filter；
- 为什么它通过了 last-price filter；
- 为什么它是 best-from-group；
- 如果它是 breakout，事件发生在哪根 bar（并直接给出 breakout bar 的 OHLC）。

### 3) 新增“同组对照”表

在 deep-dive 主表下面，新增了同一个 duplicate group 内的候选结果对照表。

这让页面现在能直接回答：
- 同组里还有哪些近似线；
- 当前代表线的 score / num_points 相对同组其他线处在什么位置；
- 为什么页面默认展示它，而不是同组别的线。

### 4) 当前窗口下实际被选中的两条线

本次生成出的当前窗口里：

- support selected line：`S-[4,18,59,61,64]`
  - group size = 2
  - score = `7884.29`
  - num_points = `5`
  - 同组第二名：`S-[18,59,61,64]`，score = `2601.98`
  - breakout_index = `14`

- resistance selected line：`R-[5,21,22,52,75,89]`
  - group size = 5
  - score = `19364.02`
  - num_points = `6`
  - 同组第二名：`R-[52,75,89]`，score = `1215.34`
  - breakout_index = `6`

这说明当前区块已经不只是“抽象上能做”，而是真的落到了当前窗口里的真实线与真实 group 对照上。

### 5) 回写 TODO

已将以下条目标记完成：
- `增加一个 selected line deep-dive 区块`

## Validation / evidence

### A. 最小重建

执行：
- `/root/clawd/jerry/momentum/.venv/bin/python /root/clawd/jerry/momentum/scripts/build_pytrendline_report.py --ticker BTC-USD --period 10d --interval 5m --window-bars 96`

结果：
- 成功重建 `reports/site/factors/pytrendline_research/report.html`

### B. 页面存在性检查

已确认生成后的 HTML 中包含：
- `Selected line deep-dive：挑 1 条 support / 1 条 resistance 逐项拆开`
- `Support selected line`
- `Resistance selected line`
- `为什么是 best-from-group`
- `breakout 事件 bar`

说明 deep-dive 区块已经进入最终页面。

## Risks / caveats

- 这轮 deep-dive 仍然是**窗口末端研究快照**，不是 bar-by-bar replay。
- selected line 会随着最新窗口变化而变化，因此它更适合教学解释，而不是被当成稳定的长期基准样本。
- 当前只补了表格层面的个案拆解，还没有再额外生成“单线专属局部图”。

## Next recommended step

下一轮最自然的相邻动作有两个：

1. **close/pivots 图补 pivot index / 时间标签**
   - 这样 Step 1 图本身就能和 deep-dive 表里的 pivot index 更直接互相对照。

2. **candidate lines before filtering 示意图**
   - 让读者更直观看到“原始候选很多，当前 deep-dive 只是筛选后代表线中的个案”。

## Commit hash (if committed)

- 实现与报告变更已 selective commit：`d6c13f0` (`report(pytrendline): add selected line deep dive`)

## Commit note

repo 中仍存在与本轮无关的脏文件（例如 interval sweep / crypto rebound / deep dive 页面 / 较早 optimization loop 记录等），因此没有整仓提交；只 selective commit 了本轮直接相关的：
- `docs/TODO.md`
- `scripts/build_pytrendline_report.py`
- `reports/site/factors/pytrendline_research/report.html`
- `reports/artifacts/pytrendline_research/*`（本轮重建产物）

本记录文件将单独提交，避免把无关脏文件一并打包进同一个提交。
