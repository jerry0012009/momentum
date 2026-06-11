# PyTrendline 报告：补“当前参数为什么这样设”的解释表

## Why this was chosen now

当前 `pytrendline explainability` 主线里，最紧邻、最有杠杆的一步是把参数选择讲清楚。

用户已经明确要求：
- 页面不只是要“能看”，还要能讲清楚“如何选择 / 如何计算”；
- 这意味着读者不能只看到 `96 / 3 / pivot-only / breakout-on` 这些参数值，还需要知道它们背后的取舍逻辑。

所以这轮选择先做 `A0-Calculation` 的第一步：参数解释表。

## What changed

### 1) 在报告中新增参数解释表

文件：
- `scripts/build_pytrendline_report.py`

新增区块：
- `为什么当前参数这样设`

当前补入的四个核心参数解释：
- `window_bars = 96`
- `min_points_required = 3`
- `all_pts_must_be_pivots = True`
- `ignore_breakouts = False`

每个参数都给出三层说明：
- 当前值是什么
- 操作性含义是什么
- 为什么目前把它当成默认值

### 2) 参数取舍口径

本轮写清楚了这些当前默认值背后的意图：

- `window_bars=96`
  - 在 5m 粒度下大约是最近 8 小时
  - 比 48 更稳，不容易只看到局部噪声
  - 比 144 更省扫描成本，也更适合报告阅读

- `min_points_required=3`
  - 避免 2 点就能随便连出一条线
  - 让“代表线”更有结构支撑

- `all_pts_must_be_pivots=True`
  - 牺牲一部分灵活性
  - 换来更强的“线和锚点一一对照”的可解释性

- `ignore_breakouts=False`
  - 保留 breakout 标记
  - 这样页面不只展示结构，还能区分事件线

### 3) 回写 TODO

已将以下任务标记为完成：
- `A0-Calculation` 里的“pytrendline 当前使用参数为什么这么设”的解释表

## Validation / evidence

### A. 报告已成功重建并发布
执行：
- `/root/clawd/jerry/momentum/.venv/bin/python scripts/build_pytrendline_report.py`
- `./scripts/publish_report_site.sh`

结果：
- 页面已更新到：
  - `https://jp.jerrypsy.top/momentum/factors/pytrendline_research/report.html`

### B. 参数区不再只是“值”，而是“值 + 意图 + 取舍”

当前页面中，参数部分已经分成两层：
- 参数值表：告诉你这次用了什么
- 参数解释表：告诉你为什么当前先这么用

这比单纯展示原始参数更接近“教学型研究报告”。

## Risks / caveats

- 这轮解释的是“当前默认值的工程取舍”，不是严格穷尽式参数敏感性分析。
- 还没有回答“如果改成 48/144、2 点、非 pivot 命中、忽略 breakout，会出现什么具体结果差异”；那属于下一阶段的参数对照实验。
- 参数解释是基于当前研究页定位，不应误读成“这些参数已经被证明最优”。

## Next recommended step

下一轮最值得做的小步动作：

1. **优先方案**：单独解释 pivot points 的选择逻辑，说明当前库把哪些高低点当 pivot，以及这对 bar-by-bar 可用性意味着什么；
2. **次优方案**：补 `candidate lines before filtering` 或 `duplicate grouping before/after` 图，让“从候选到代表线”的压缩过程更直观。

## Commit hash (if committed)

f79142393bc17070717fda55b88e720aed42f750

## Commit note

本轮仍存在与 interval sweep / crypto rebound / quant digest 相关的其他脏文件，因此只会 selective commit 本轮的 pytrendline 报告与 TODO 文件，不打包无关改动。
