# PyTrendline explainability report：把最终结果图拆成“步骤图 + 操作性定义”

## Why this was chosen now

当前最近明确主线已经切到 `A0. 以 pytrendline 为起点的“可讲清楚步骤”研究报告`。

Jerry 刚刚明确提出：
- 不满足于只看最终趋势线图；
- 更想看这个仓库“到底是怎么一步步画出趋势线”的可复现过程；
- 希望网页报告里把每个细节步骤的操作性定义讲清楚。

所以这轮优先做 explainability/report refinement，而不是直接新开 parallel channel 实现。

## What changed

### 1) 升级 `build_pytrendline_report.py`

文件：
- `scripts/build_pytrendline_report.py`

本轮把原本偏“最终结果展示”的 pytrendline report，升级成更像“研究拆解页”的结构：

- 新增 **窗口 / 运行边界** 表
  - 解释 `period / interval / window_bars`
  - 明确当前为什么只做 recent-window inspection

- 新增 **逐步骤操作性定义** 表
  - bars -> pivots -> candidate lines -> filtering -> duplicate grouping -> breakout labels

- 新增 **字段解释** 表
  - `m / b / num_points / score / starts_at_date / ends_at_date / is_breakout`

- 新增 **bar-by-bar 可用性 / research-only 边界** 区块
  - 明确为什么当前仍然只是研究功能，而不是正式 signal engine

- 新增 **从 pytrendline 到 parallel channel 的映射** 区块
  - 明确它已经解决 `pivot -> line -> breakout` 这半条链
  - 也明确它还没有解决平行约束 / 通道宽度 / 多周期共振 / rebound 规则

### 2) 新增分步骤图表

新 artifacts：
- `reports/artifacts/pytrendline_research/step1_close_and_pivots.png`
- `reports/artifacts/pytrendline_research/step2_support_lines.png`
- `reports/artifacts/pytrendline_research/step3_resistance_lines.png`
- `reports/artifacts/pytrendline_research/step4_breakout_only.png`

保留并更新：
- `trendlines_overlay.png`
- `support_trendlines.csv`
- `resistance_trendlines.csv`
- `candles_window.csv`
- `summary.json`
- `reports/site/factors/pytrendline_research/report.html`

### 3) 回写 TODO 状态

已把以下 A0 条目标记为完成：
- 输入窗口语义解释
- trendline 参数操作性解释
- 分步骤图表补充
- 从 pytrendline 到 parallel channel 的映射
- bar-by-bar / research-only 边界说明

## Validation / evidence

### A. 报告成功重建
验证命令：
- 先尝试系统 Python，发现缺少 `yfinance`
- 随后改用项目虚拟环境：
  - `/root/clawd/jerry/momentum/.venv/bin/python scripts/build_pytrendline_report.py`

结果：报告成功写出到：
- `reports/site/factors/pytrendline_research/report.html`

### B. 当前报告已具备新的 explainability 结构
报告首页现在已经能直接看到：
- 参数
- 窗口 / 运行边界
- 逐步骤操作性定义
- 窗口内数量概览
- close + pivots 图
- support lines 图
- resistance lines 图
- breakout-only 图
- final overlay 图
- 字段解释
- research-only 边界
- parallel channel 映射

这比原先只有“参数 + 边界 + 一张总览图 + 两张表”要清楚得多。

## Risks / caveats

- 当前仍然依赖在线下载行情（`yfinance`）；本轮没有把 pytrendline 报告改成完全离线可复现。
- duplicate-group before/after 对比图这一步暂时还没单独补；目前只是在文字和字段层解释了 duplicate grouping。
- 这轮没有新增 bar-by-bar 因果审计代码，只是把边界说明讲清楚了。

## Next recommended step

下一轮最值得做的小步动作：

1. **优先方案**：补一张 `duplicate grouping before/after` 对比图，让“为什么只展示 best-from-group”更直观；
2. **次优方案**：在报告里加入 pivot / line 的索引级明细表（例如 line id 对应哪些 pivot index），进一步增强可复验性。

## Commit hash (if committed)

7e287732e3f06d5f613b0db15be759ea81b3e740

## Commit note

本轮存在与 interval-sweep/quant-digest 相关的其他脏文件，因此只会 selective commit 本轮涉及的 pytrendline report / TODO 文件，不打包无关改动。
