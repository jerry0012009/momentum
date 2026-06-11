# 在 confirmation protocol 中补字段分层表

## 为什么这次选这个

这轮继续完全沿最近几轮的 confirmation protocol 线程推进，没有扩新方向，也没有开新实验，而是顺着上一轮刚补好的 `source-to-protocol` 示例行再往前推进一个很小但很实用的点。

上一轮已经把：
- `PyIndicators confirm1` 的示例行
- `PyTrendline raw_breach` 的示例行

写进了协议文档。

但如果只有示例行，后面真正接 source 时仍然很容易卡在一个更基础的问题：

- 哪些字段 **没有就不该进 protocol compare**？
- 哪些字段 **可以先保留 null**？
- 哪些字段 **根本就应该继续只留在 source audit / mapping 层**，不该被强行升成跨引擎必填？

所以这轮最合适的小步推进，就是直接把这三类字段分层清楚。这样后面接 source 的时候，团队就不会再反复争论 `score_bucket / duplicate_group_id / is_representative` 这些字段到底该怎么处理。

这轮最值得复用/借鉴的点是：**schema 真正开始变得可执行，往往不是因为字段更多，而是因为字段边界更清楚——尤其是“哪些必须、哪些可空、哪些只应保留为 engine-specific”。**

## 核心结论（中文摘要）

核心结论：**`TRENDLINE_CONFIRMATION_PROTOCOL` 现在已经补上了 `required / nullable / engine-specific` 字段分层表，因此后续 source 接入时，已经能更明确地区分“必须填的跨引擎字段”“允许暂时留空的字段”“以及不该硬升成统一 schema 的引擎专属字段”。**

证据如何支持这个结论：**本轮已在 `docs/TRENDLINE_CONFIRMATION_PROTOCOL.md` 新增 `4.2 字段分层表（required / nullable / engine-specific）`，明确 `source_engine / event_family / confirmation_level / event_timestamp / engine_line_id` 等属于 `required`，`slope_bucket / is_representative / line_quality_bucket` 等可先为 `nullable`，而 `duplicate_group_id / navigator_state / pytrendline_score` 等仍应保留为 `engine-specific`；重建后的 `reports/site/plans/trendline_confirmation_protocol.html` 与 `reports/site/plans/momentum_todo.html` 已同步显示这项更新。**

## 本轮做了什么改动

本轮只做一个主点：**给 confirmation protocol 补字段分层表。**

具体改动：

1. 更新 `docs/TRENDLINE_CONFIRMATION_PROTOCOL.md`
   - 在 `4.1 source-to-protocol 示例行（v1）` 之后新增：
     - `4.2 字段分层表（required / nullable / engine-specific）`

2. 在这张表里把字段分成三类：
   - `required`
     - 如：
       - `source_engine`
       - `sample_key`
       - `symbol`
       - `timeframe`
       - `event_family`
       - `confirmation_level`
       - `event_timestamp`
       - `line_side`
       - `engine_line_id`
       - `sample_scope`
   - `nullable`
     - 如：
       - `slope_bucket`
       - `is_representative`
       - `line_quality_bucket`
       - `event_subtype`
       - `bars_since_first_cross`
       - `bars_since_touch`
       - `is_confirmed`
       - `is_provisional`
   - `engine-specific`
     - 如：
       - `num_points_bucket`
       - `score_bucket`
       - `duplicate_group_id`
       - `navigator_state`
       - `active_line_start_bar`
       - `active_line_reset_reason`
       - `pytrendline_score`

3. 在同一新章节里明确三条原则：
   - `required`：没有就不该进 protocol compare；
   - `nullable`：可以先为空，但要诚实承认 coverage 不完整；
   - `engine-specific`：可以保留，但不要强行升成跨引擎必填字段。

4. 更新 `docs/TODO.md`
   - 新增并标记为 `[x]`：
     - `在 confirmation protocol 中补字段分层表：required / nullable / engine-specific`
   - 结果说明里明确：
     - 哪些字段没有就不该进 protocol compare
     - 哪些字段允许先保留 `null`
     - 哪些字段应继续只留在 source audit / mapping 层

5. 重建 plans 镜像
   - `reports/site/plans/trendline_confirmation_protocol.html`
   - `reports/site/plans/momentum_todo.html`

## 验证 / 证据

本轮是协议 / 页面细化，因此采用最小必要验证：

1. 页面重建
   - `./.venv/bin/python scripts/build_plans_site.py`

2. 本地 grep 验证协议页
   - `reports/site/plans/trendline_confirmation_protocol.html`
     - 已出现：`4.2 字段分层表（required / nullable / engine-specific）`
     - 已出现：`required：没有就不该进 protocol compare`

3. 本地 grep 验证 TODO 页
   - `reports/site/plans/momentum_todo.html`
     - 已出现：`[x] 在 confirmation protocol 中补字段分层表：required / nullable / engine-specific。`

## 风险 / 边界

- 这轮没有新增新的实验或统计结果；
- 它解决的是 **schema 边界清晰度**，不是直接新增 alpha 证据；
- 这张表仍然是 `v1` 口径，后面随着 source 覆盖增多，某些当前 `nullable` 的字段未来可能会上升为更强约束，但现在不宜过早硬收紧。

## 下一步建议

1. 如果继续沿这条 protocol 线程推进，下一步可以考虑：
   - 把 `required / nullable / engine-specific` 再补成一个更正式的 `schema checklist`，用于后续 source onboarding；
2. 如果转回更实证的工作，则可以开始：
   - 只在 `required` 字段完整的前提下，做第一轮真实的跨 source ladder compare。

## Commit hash

- 已提交：`docs(momentum): add protocol field tiering`
- 具体 hash 以本轮提交后的当前 `HEAD` 为准。

## 如果未提交，说明原因

本轮已做安全 selective commit。

我只提交了本轮涉及的 protocol / TODO / 运行记录文件，没有混入当前 repo 里与本轮无关的其它脏文件。