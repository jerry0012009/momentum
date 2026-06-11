# 在 confirmation protocol 中补 source-native 到 mainline ladder 的最小映射例子

## 为什么这次选这个

这轮继续严格沿最近几轮的 confirmation protocol 线程推进，没有新开题，也没有扩新的 E 候选，而是直接补一个很靠近上一轮的缺口：

- 上一轮已经把 `Optimal Stopping` 的机制解释正式挂回 `TRENDLINE_CONFIRMATION_PROTOCOL`；
- 但协议文档里虽然已经有了 ladder 枚举和机制解释，仍然还缺一个很实操的层：
  - **具体到 `PyIndicators` 和 `PyTrendline`，native 状态名到底怎么落到 mainline ladder？**

如果这一步不补，后面每次讨论 `source #1`、`source #2` 接协议时，还是得反复口头解释：
- `breakout_hold_1` 到底算 `confirm1` 还是别的？
- `breakout_hold_4` 是不是要单独升一层？
- `PyTrendline v1` 的 `is_breakout` 到底只算 `raw_breach`，还是已经接近 `confirm1`？

这轮最值得复用/借鉴的点是：**一份协议真正开始可执行，不是从“抽象定义已经很好”开始，而是从“至少有 1~2 个 source 的 native -> mainline 示例映射”开始。**

## 核心结论（中文摘要）

核心结论：**`TRENDLINE_CONFIRMATION_PROTOCOL` 现在已经不只定义了 mainline ladder 的抽象枚举，还明确补上了 `PyIndicators / PyTrendline` 的 native -> mainline 最小映射例子，因此后续 source 接入时不必再反复口头解释。**

证据如何支持这个结论：**本轮已在 `docs/TRENDLINE_CONFIRMATION_PROTOCOL.md` 中新增 `PyIndicators` 与 `PyTrendline` 的最小映射说明，明确 `breakout_hold_1 -> confirm1`、`breakout_hold_2/3/4 -> confirm3-like stronger confirmation`、`rebound_inside_0/1/2/3 -> inside_0/1/2/3plus`，以及 `PyTrendline v1 is_breakout -> raw_breach`；重建后的 `reports/site/plans/trendline_confirmation_protocol.html` 和 `reports/site/plans/momentum_todo.html` 已可直接看到这些映射例子。**

## 本轮做了什么改动

本轮只做一个主点：**给 confirmation protocol 补上 source-native 到 mainline ladder 的最小映射例子。**

具体改动：

1. 更新 `docs/TRENDLINE_CONFIRMATION_PROTOCOL.md`
   - 在 `PyIndicators v1 当前怎么接入这份协议` 一节中，明确把它标成当前默认的 `source #1`
   - 新增 `7.1 native -> mainline 的最小映射例子`

2. 在 `PyIndicators` 一节里明确：
   - breakout 侧：
     - `candidate_ts` 更接近 `raw_breach`
     - `signal_ts + breakout_hold_1` 更接近 `confirm1`
     - `signal_ts + breakout_hold_2/3` 更接近 `confirm3-like stronger confirmation`
     - `breakout_hold_4` 当前先并入 `confirm3-plus / stronger-than-confirm3`
   - rebound 侧：
     - `rebound_inside_0 -> inside_0`
     - `rebound_inside_1 -> inside_1`
     - `rebound_inside_2 -> inside_2`
     - `rebound_inside_3+ -> inside_3plus`
   - 并明确：
     - `close_confirm_same_bar`
     - `retest_hold`
     - 当前还没有 clean 的 `PyIndicators` 原生映射

3. 在 `PyTrendline` 一节里明确：
   - `PyTrendline v1` 当前最接近：
     - `is_breakout=True + breakout_date -> raw_breach`
     - `is_breakout=False + ends_at_date -> touch_only / touch candidate`
   - 明确当前仍没有 clean 映射到：
     - `close_confirm_same_bar`
     - `confirm1`
     - `confirm3`
     - `retest_hold`
     - `inside_0/1/2/3plus`
   - 因此把 `PyTrendline v2` 的目标改写得更具体：
     - native state transition 要能稳定落到这 5 层 breakout ladder

4. 更新 `docs/TODO.md`
   - 新增并标记为 `[x]`：
     - `在 confirmation protocol 中补 PyIndicators / PyTrendline 的 native -> mainline 最小映射例子`
   - 并补结果说明，明确两边的最小映射口径

5. 重建 plans 镜像
   - `reports/site/plans/trendline_confirmation_protocol.html`
   - `reports/site/plans/momentum_todo.html`

## 验证 / 证据

本轮是协议 / 页面细化，因此采用最小必要验证：

1. 页面重建
   - `./.venv/bin/python scripts/build_plans_site.py`

2. 本地 grep 验证协议页
   - `reports/site/plans/trendline_confirmation_protocol.html`
     - 已出现：`source #1`
     - 已出现：`breakout_hold_1`
     - 已出现：`confirm3-like stronger confirmation`
     - 已出现：`rebound_inside_0`
     - 已出现：`is_breakout=True + breakout_date`
     - 已出现：`same bar close outside line -> close_confirm_same_bar`

3. 本地 grep 验证 TODO 页
   - `reports/site/plans/momentum_todo.html`
     - 已出现：`[x] 在 confirmation protocol 中补 PyIndicators / PyTrendline 的 native -> mainline 最小映射例子。`
     - 已出现：
       - `PyIndicators breakout_hold_1 -> confirm1`
       - `PyTrendline v1 is_breakout -> raw_breach`

## 风险 / 边界

- 这轮没有新增新的实验或统计结果；
- 它解决的是 **协议可执行性与 source 接入时的歧义消除**，不是直接新增 alpha 证据；
- 这里的映射仍是 `v1 minimal mapping`，不代表 `PyIndicators / PyTrendline` 已经天然拥有完整同构的状态机。

## 下一步建议

1. 如果继续沿 protocol 收口，下一步最有价值的是：
   - 把这些最小映射再落成一个更正式的 `source-to-protocol table schema` 示例；
2. 如果转回实证推进，则可以开始：
   - 只针对这些已明确映射的层级，比较 `raw_breach / confirm1 / confirm3-like` 的 retention 与 forward-return 差异。

## Commit hash

- 已提交：`docs(momentum): add native ladder mapping examples`
- 具体 hash 以本轮提交后的当前 `HEAD` 为准。

## 如果未提交，说明原因

本轮已做安全 selective commit。

我只提交了本轮涉及的 protocol / TODO / 运行记录文件，没有混入当前 repo 里与本轮无关的其它脏文件。