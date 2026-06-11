# PyTrendline 报告：补 `is_breakout` 判定语义，并修正 `breakout_date` 对齐

## Why this was chosen now

在 `pytrendline explainability` 主线里，duplicate grouping 讲清楚之后，剩下最关键的一块计算语义就是 `is_breakout`。

因为对读者来说，如果不知道 breakout 的底层判定是：
- 看 `Close` 还是看 `High/Low`
- support / resistance 两边是否对称
- `breakout_date` 指的是哪根 bar

那页面里的 breakout-only 图和结果表就很容易被误读。

所以这轮聚焦两件彼此紧邻的事：
1. 在报告中把 `is_breakout` 的判定语义讲清楚；
2. 在本地 bridge 中修正 `breakout_date` 对齐到真实 `breakout_index` 的日期。

## What changed

### 1) 在报告中新增 breakout 语义区块

文件：
- `scripts/build_pytrendline_report.py`

新增区块：
- ``is_breakout` 应该怎么读`

当前已明确写出：
- **support breakout 是什么**
  - 当前更接近：trendline 在某 bar 上方，且 `trend_price > Low + tolerance`
  - 所以它不是 close-based cross，更像 low-based breach

- **resistance breakout 是什么**
  - 当前更接近：trendline 在某 bar 下方，且 `trend_price < High - tolerance`
  - 所以它也不是 close-based cross，更像 high-based breach

- **当前 tolerance**
  - 源码用 `avg_candle_range * 0.08`
  - 目的是避免很小的穿越也被直接标成 breakout

- **当前标签定位**
  - 它更像 research inspection 下的事件标签
  - 不是已经过 bar-by-bar 审计的正式交易信号

### 2) 修正 `breakout_date` 对齐问题

文件：
- `src/momentum/factors/pytrendline_bridge.py`

本轮新增了本地归一化逻辑：
- 若 `breakout_index` 存在，就用该 index 对应的 candle `Date` 回填 `breakout_date`

这样做的原因是：
- 上游 `pytrendline` 在 breakout 被识别时，`breakout_date` 记录的是起点 `i` 的日期，而不是 `k`（即实际 breakout bar）的日期；
- 这会让页面里的 breakout 时间信息产生误导；
- 我没有去改动站点包本体，而是在本地 bridge 层做矫正，保持隔离。

### 3) 结果表里也补入 breakout 事件字段

本轮还顺手把 best support / resistance lines 表增加了：
- `breakout_index`
- `breakout_date`

这样读者可以直接把：
- 这条线是否 breakout
- breakout 发生在第几根 bar
- breakout 发生在什么时候

对照着看，而不只是看到一个布尔值。

### 4) 回写 TODO

已将以下任务标记为完成：
- 单独解释 breakout label 的当前判定逻辑
- 在报告里单独解释 `is_breakout` 的判定语义

## Validation / evidence

### A. 报告已成功重建并发布
执行：
- `/root/clawd/jerry/momentum/.venv/bin/python scripts/build_pytrendline_report.py`
- `./scripts/publish_report_site.sh`

结果：
- 页面已更新到：
  - `https://jp.jerrypsy.top/momentum/factors/pytrendline_research/report.html`

### B. `breakout_date` 已和真实事件 bar 对齐

本轮在重建后抽样检查 `support_trendlines.csv`：
- `breakout_index=1` 对应 `breakout_date=2026-03-11T14:45:00`
- `starts_at_date` 则保留在更早的起始锚点时间

这说明：
- breakout 发生时间已不再错误贴着趋势线起点
- 页面里 breakout 字段的可解释性更强了

## Risks / caveats

- 这轮修正的是本地 bridge 层，不是上游 `pytrendline` 包本身；后续若升级依赖，仍要记得重新检查这一点。
- 当前 breakout 语义解释已经到位，但还没有把“触发 breakout 的那根 K 线”单独高亮到 breakout-only 图里。
- `is_breakout` 依然是窗口扫描结果里的研究标签，不能直接替代严格的实时信号审计。

## Next recommended step

下一轮最值得做的小步动作：

1. **优先方案**：在 breakout-only 图里把触发 breakout 的那根 K 线单独高亮或打标，让“文字语义 -> 表格字段 -> 图上位置”彻底打通；
2. **次优方案**：给 support / resistance 表补更多锚点对照字段（如 pivot indices / timestamps），进一步增强图表-表格联动。

## Commit hash (if committed)

4eb119135f5146b6b91d82eb0806c3bcf8916c9b

## Commit note

本轮仍存在与 interval sweep / crypto rebound / reading pages 相关的其他脏文件，因此只会 selective commit 本轮的 pytrendline 报告、bridge 与 TODO 文件，不打包无关改动。
