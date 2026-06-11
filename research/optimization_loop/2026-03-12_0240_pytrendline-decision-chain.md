# PyTrendline 报告：补 pivot→trendline 决策链总览与有效趋势线判定规则

## Why this was chosen now

这轮继续沿当前最近的 `pytrendline_research` explainability 主线推进，不新开分支。

上轮已经补了：
- 为什么不能把所有 pivot 两两相连；
- filter waterfall；
- Step 2/3/4 的局部教学视图。

但 `A0-Core Semantics` 里还有两个紧邻且高价值的空缺：
- `从 pivot 到 trendline 的决策链总览`
- `什么情况下能被当做趋势线，什么情况下不能`

它们正好承接前面的 waterfall / 图表优化，能把“图上为什么只剩这些线”讲得更完整。

## What changed

### 1) 新增“从 pivot 到 trendline：决策链总览”区块

文件：
- `scripts/build_pytrendline_report.py`
- `reports/site/factors/pytrendline_research/report.html`

新增表格把下面这条链串成一个可读的教学区块：
- pivot collection
- pivot pair enumeration
- candidate line fitting
- validity filtering
- valid trendline
- breakout tagging
- duplicate grouping
- best-from-group selection

而且不是只写抽象定义，还直接把当前窗口下的 support / resistance 计数写进去，帮助读者把：
- 概念层
- filter waterfall 计数层
- 最终图表层

连成同一条语义链。

### 2) 新增“什么情况下能被当做趋势线，什么情况下不能”区块

本轮补了一张规则表，明确回答：
- 起点/终点为什么必须来自 pivots；
- `num_points >= min_points_required` 为什么是有效趋势线的最低门槛；
- `max_allowable_error` 如何决定“贴近这条线”的命中判定；
- slope / last-price 不合法时为什么会在第一层就被淘汰；
- breakout 为什么不是“删掉这条线”，而是把它从静态结构线改标为事件线；
- duplicate grouping 为什么会让有些线虽存在于结果里，却不再单独展示。

这样现在页面不只是在讲“有哪些线”，而是在讲“什么线算数，什么线不算数，什么线算数但不值得单独展示”。

### 3) 回写 TODO

已将以下两项标记完成：
- `增加一个 从 pivot 到 trendline 的决策链总览 区块`
- `单独解释：什么情况下能被当做趋势线，什么情况下不能`

## Validation / evidence

### A. 最小重建

执行：
- `/root/clawd/jerry/momentum/.venv/bin/python /root/clawd/jerry/momentum/scripts/build_pytrendline_report.py --ticker BTC-USD --period 10d --interval 5m --window-bars 96`

结果：
- 成功重建 `reports/site/factors/pytrendline_research/report.html`

### B. 关键区块存在性检查

额外检查确认 HTML 中已出现：
- `从 pivot 到 trendline：决策链总览`
- `什么情况下能被当做趋势线，什么情况下不能`

## Risks / caveats

- 这轮主要补的是“规则总览”，还没有把 accepted vs rejected examples 拆成真实样例卡片。
- 也还没有把 line lifecycle / state diagram 单独做成图。
- 本轮运行环境没有 elevated 权限，因此没有执行 `publish_report_site.sh` 的 rsync 发布步骤；当前完成的是 repo 内报告与 artifact 的重建与提交，外部站点同步需在有权限的运行环境中完成。

## Next recommended step

下一轮最自然的小步推进是二选一：

1. **accepted vs rejected examples**
   - 挑 2~4 条真实线，逐条解释：为什么保留、为什么淘汰、为什么被并组、为什么虽存在但不值得展示。

2. **line lifecycle / state diagram**
   - 把一条线从 candidate -> valid -> breakout tagged / grouped-not-representative / best-from-group 的状态流转讲清楚。

## Commit hash (if committed)

Committed in this run as the current `HEAD` for `report(pytrendline): add decision-chain semantics`. Exact hash omitted here to avoid amend-induced drift.

## Commit note

repo 里仍有与 interval sweep / crypto rebound / deep dive 页面等无关的脏文件，因此本轮只会 selective commit：
- `docs/TODO.md`
- `scripts/build_pytrendline_report.py`
- `reports/site/factors/pytrendline_research/report.html`
- `reports/artifacts/pytrendline_research/*`（仅本次重建产物）
- `research/optimization_loop/2026-03-12_0240_pytrendline-decision-chain.md`
