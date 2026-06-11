# 在 confirmation protocol 中补 source-to-protocol 示例行

## 为什么这次选这个

这轮继续完全沿最近几轮的 confirmation protocol 线程推进，没有新开题，也没有扩新的研究候选，而是顺着上一轮刚补好的 `native -> mainline` 映射再往前推一小步。

上一轮已经把：
- `PyIndicators breakout_hold_1 -> confirm1`
- `PyTrendline v1 is_breakout -> raw_breach`

这类映射关系写进协议文档了。

但如果只停在“口头/概念映射”这一层，后面真正做 source table 时还是容易卡在两个很具体的问题上：

1. 某些字段当前没有天然来源，到底是该写 `null`，还是该硬补一个看起来完整的值？
2. 一行 source row 真正长什么样，团队成员对它的想象可能并不一致。

所以这轮最合理的小步推进，就是：**直接把 `source-to-protocol` 的示例行写出来，并明确 `v1` 允许哪些字段诚实地保留 `null`。**

这轮最值得复用/借鉴的点是：**协议从“抽象上可理解”走向“工程上可执行”，往往不靠再加更多名词，而靠补 1~2 条最小示例行，把字段落表和允许缺失的边界讲清楚。**

## 核心结论（中文摘要）

核心结论：**`TRENDLINE_CONFIRMATION_PROTOCOL` 现在已经不只定义了 ladder 枚举和 source-native 映射，还补上了 `PyIndicators confirm1` 与 `PyTrendline raw_breach` 的最小示例行，因此后续 source table 接入时，已经能明确知道一行记录怎么落表，以及哪些字段应诚实保留为 `null`。**

证据如何支持这个结论：**本轮已在 `docs/TRENDLINE_CONFIRMATION_PROTOCOL.md` 新增 `4.1 source-to-protocol 示例行（v1）`，其中明确写出了两条 YAML 风格示例行，并强调“不要为了凑齐 schema 去伪造字段”；重建后的 `reports/site/plans/trendline_confirmation_protocol.html` 已出现该新章节，而 `reports/site/plans/momentum_todo.html` 也已新增对应的 `[x]` 记录。**

## 本轮做了什么改动

本轮只做一个主点：**把 confirmation protocol 的 source table 从概念层推进到示例行层。**

具体改动：

1. 更新 `docs/TRENDLINE_CONFIRMATION_PROTOCOL.md`
   - 在 `最小必备字段` 之后新增：
     - `4.1 source-to-protocol 示例行（v1）`

2. 在这一新章节里明确了 3 条规则：
   - 示例行的作用是帮助理解字段如何落表，不是唯一实现；
   - 某些字段当前没有天然来源时，`v1` 允许先写 `null`；
   - **不要为了凑齐 schema 去伪造字段**，尤其是：
     - `is_representative`
     - `line_quality_bucket`
     - `score_bucket`

3. 新增两个最小示例行：
   - 示例 A：`PyIndicators breakout_hold_1 -> confirm1`
     - 说明：`signal_ts + breakout_hold_1` 已足够落到 `confirm1`
     - 但 `is_representative / line_quality_bucket` 当前应保留 `null`
   - 示例 B：`PyTrendline v1 breakout -> raw_breach`
     - 说明：`is_breakout=True + breakout_date` 已足够落成一条 `raw_breach` source row
     - 但它当前还没有 clean 的 `confirm1 / confirm3 / retest_hold` 原生层

4. 在同一新章节中明确 `v1` 的实务规则：
   - 字段缺失可以保留 `null`；
   - 语义缺失不能靠硬映射掩盖；
   - 先让 source row 诚实对齐，再谈更完整的 ladder coverage。

5. 更新 `docs/TODO.md`
   - 新增并标记为 `[x]`：
     - `在 confirmation protocol 中补 source-to-protocol 示例行（含允许 null 的 v1 口径）`
   - 结果说明写明：
     - 已新增 `PyIndicators confirm1` 与 `PyTrendline raw_breach` 的示例行
     - 并明确哪些字段应该保持 `null` 而不是伪造值

6. 重建 plans 镜像
   - `reports/site/plans/trendline_confirmation_protocol.html`
   - `reports/site/plans/momentum_todo.html`

## 验证 / 证据

本轮是协议 / 页面细化，因此采用最小必要验证：

1. 页面重建
   - `./.venv/bin/python scripts/build_plans_site.py`

2. 本地 grep 验证协议页
   - `reports/site/plans/trendline_confirmation_protocol.html`
     - 已出现：`4.1 source-to-protocol 示例行（v1）`
     - 已出现：`不要为了凑齐 schema 去伪造字段`
     - 已出现：`PyIndicators breakout_hold_1 -> mainline confirm1`
     - 已出现：`PyTrendline v1 breakout -> mainline raw_breach`
     - 已出现：`字段缺失可以保留 null`

3. 本地 grep 验证 TODO 页
   - `reports/site/plans/momentum_todo.html`
     - 已出现：`[x] 在 confirmation protocol 中补 source-to-protocol 示例行（含允许 null 的 v1 口径）。`

## 风险 / 边界

- 这轮没有新增新的实验或比较结果；
- 它解决的是 **source table 的可执行性与字段缺失边界**，不是直接新增 alpha 证据；
- 这些示例行仍然属于 `v1 minimal examples`，不应被误读成已经完成正式数据导出或完整 source integration。

## 下一步建议

1. 如果继续沿 protocol 线程推进，下一步更实用的动作是：
   - 把这类示例行再升级成一个更正式的 `source-to-protocol table schema example`，比如补“哪些字段 nullable / required / engine-specific”；
2. 如果转回实证推进，则可以开始：
   - 只用这些已经诚实可映射的层级，比较 `raw_breach / confirm1 / confirm3-like` 的 retention 与 forward-return 差异。

## Commit hash

- 已提交：`docs(momentum): add protocol row examples`
- 具体 hash 以本轮提交后的当前 `HEAD` 为准。

## 如果未提交，说明原因

本轮已做安全 selective commit。

我只提交了本轮涉及的 protocol / TODO / 运行记录文件，没有混入当前 repo 里与本轮无关的其它脏文件。