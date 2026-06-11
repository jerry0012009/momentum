# PyTrendline 报告：补 filter waterfall，并讲清楚为什么不能把所有 pivot 两两相连

## Why this was chosen now

用户刚刚明确指出：
- 现在的 report 虽然解释了很多局部字段；
- 但最核心的链条仍然没讲透；
- 尤其是：pivot 到 trendline 的过滤逻辑、为什么不能把所有 pivot 两两相连、以及页面最终为什么只剩少数线。

因此这轮不再继续做局部图标修补，而是直接补一个更核心的 explainability 中枢：
- `为什么不能把所有 pivot 两两相连`
- `filter waterfall`

## What changed

### 1) 在报告中新增“为什么不能把所有 pivot 两两相连”区块

文件：
- `scripts/build_pytrendline_report.py`

新增内容明确解释：
- 2 点连线天然太多，候选线并不稀缺；
- 只凭 pivot pair 还不能说明它是一条“值得展示/研究的趋势线”；
- 当前代码还会继续经过：
  - slope / last-price 过滤
  - 最小命中点数过滤
  - duplicate grouping
- 所以页面里最终展示的是压缩后的代表线，而不是所有 pair 直连结果。

### 2) 在报告中新增 filter waterfall

本轮新增：
- `filter_waterfall.png`
- `Filter waterfall：候选线是如何一层层被筛下来的` 区块

当前落地的 pipeline 计数包括：
- `pivot_count`
- `pivot_pairs_considered`
- `pass_basic_filters`
- `valid_results_pre_group`
- `breakout_tagged`
- `duplicate_groups`
- `best_from_group`

而且 support / resistance 两侧都会分别统计，不是只讲一边。

### 3) 把 pipeline 计数写进 summary.json

本轮还把：
- `support_pipeline`
- `resistance_pipeline`

直接写进了 `reports/artifacts/pytrendline_research/summary.json`。

这意味着后面如果要继续做：
- accepted vs rejected examples
- lifecycle page
- state diagram

已经有一个稳定的 pipeline 数值底座可复用。

### 4) 回写 TODO

已将以下任务标记为完成：
- 单独解释：为什么不能把所有 pivot 两两相连后都当成趋势线
- 在报告中新增一个 filter waterfall（过滤漏斗）表

## Validation / evidence

### A. 报告已成功重建并发布
执行：
- `/root/clawd/jerry/momentum/.venv/bin/python scripts/build_pytrendline_report.py`
- `./scripts/publish_report_site.sh`

结果：
- 页面已更新到：
  - `https://jp.jerrypsy.top/momentum/factors/pytrendline_research/report.html`

### B. 生成后的页面与 artifacts 已包含新增内容

额外检查确认以下内容已经存在：
- HTML 中包含 `Filter waterfall`
- HTML 中包含 `为什么不能把所有 pivot 两两相连`
- artifacts 中包含 `filter_waterfall.png`
- `summary.json` 中已经包含 `support_pipeline` / `resistance_pipeline`

## Risks / caveats

- 这轮的 waterfall 重点是把“候选线如何被层层筛下去”讲清楚；但还没有把 rejected examples 单独拆成样例卡。
- 当前 `pass_basic_filters` 把 slope / last-price 归并成同一层，还没有再拆得更细展示在页面主表里。
- 这轮依然是 explainability 优化，不涉及策略收益层面的新结论。

## Next recommended step

下一轮最值得做的小步动作：

1. **优先方案**：补 `accepted vs rejected examples`，挑几条真实线，逐条解释为什么被保留、为什么被淘汰；
2. **次优方案**：补 `line lifecycle / state diagram`，把一条线从 candidate 到 best-from-group / breakout-tagged 的状态流转讲清楚。

## Commit hash (if committed)

1222c2be7e4b0708f62cc3ef35441770f4e39008

## Commit note

本轮仍存在与 interval sweep / crypto rebound / reading pages 相关的其他脏文件，因此只会 selective commit 本轮的 pytrendline 报告与 TODO 文件，不打包无关改动。
