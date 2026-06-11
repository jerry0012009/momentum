# 在 confirmation protocol 中补 source onboarding checklist

## 为什么这次选这个

这轮继续沿最近几轮的 confirmation protocol 线程往前推进，没有扩新题，也没有去跑新实验，而是顺着上一轮刚补好的 `字段分层表` 再往前收口一步。

上一轮已经把：
- `required`
- `nullable`
- `engine-specific`

三类字段边界写清楚了。

但如果只有字段分层表，后面谁要接一个新 source 进 confirmation protocol，仍然可能不知道应该按什么顺序检查：
- 是先看 required 字段？
- 还是先看 native->mainline 映射？
- source 明明只是 `raw-breach-only`，是不是已经够资格直接上 compare page？

所以这轮最合适的小步推进，就是把这些判断顺序整理成一张 **source onboarding checklist**，让后续 source onboarding 不再靠临场口头判断。

这轮最值得复用/借鉴的点是：**协议文档真正开始指导团队协作，不只是因为定义更完整，而是因为它把“接入一个新 source 应该怎么过关”写成了可执行 checklist。**

## 核心结论（中文摘要）

核心结论：**`TRENDLINE_CONFIRMATION_PROTOCOL` 现在已经补上了 `source onboarding checklist (v1)`，因此后续任何新 source 要进入 confirmation compare 时，已经有了一套明确的过关顺序与最小准入条件。**

证据如何支持这个结论：**本轮已在 `docs/TRENDLINE_CONFIRMATION_PROTOCOL.md` 新增 `4.3 source onboarding checklist (v1)`，明确要求新 source 依次检查身份识别、required 字段、native->mainline 映射、nullable/engine-specific 边界，以及最小 compare 准入条件；重建后的 `reports/site/plans/trendline_confirmation_protocol.html` 已出现该章节，而 `reports/site/plans/momentum_todo.html` 也新增了对应的 `[x]` 记录。**

## 本轮做了什么改动

本轮只做一个主点：**给 confirmation protocol 补 source onboarding checklist。**

具体改动：

1. 更新 `docs/TRENDLINE_CONFIRMATION_PROTOCOL.md`
   - 在 `4.2 字段分层表` 之后新增：
     - `4.3 source onboarding checklist (v1)`

2. 在 checklist 中明确了 6 层检查顺序：
   - 第 0 层：身份识别
     - 是否能明确 `source_engine`
     - 是否能明确 `sample_key / sample_scope`
     - source 更像 breakout / rebound / mixed / explainability reference
   - 第 1 层：最小 required 字段
     - `symbol / timeframe / event_family / confirmation_level / event_timestamp / line_side / engine_line_id`
   - 第 2 层：native -> mainline 映射是否清楚
   - 第 3 层：字段缺失是否诚实
     - 不伪造 `is_representative / line_quality_bucket / score_bucket / is_confirmed`
   - 第 4 层：是否足够进入 compare
     - 至少能稳定输出一种 `event_family`
     - 至少能稳定输出一种 mainline `confirmation_level`
     - 至少能产出 `overall ladder summary`
   - 第 5 层：进入 compare 后的默认诚实标签
     - `source #1 / baseline compare source`
     - `raw-breach-only source`
     - `partial ladder coverage`
     - `rebound-only source`
     - `mechanism-backed but not full-event-universe`

3. 在 checklist 里明确一条关键规则：
   - **只有通过前 4 项，才值得继续做 compare page**
   - 否则 source 应先留在：
     - bridge
     - brief
     - mapping
     - explainability reference

4. 更新 `docs/TODO.md`
   - 新增并标记为 `[x]`：
     - `在 confirmation protocol 中补 source onboarding checklist`
   - 结果说明中写明：
     - 新 source 进入 compare 前，应依次检查身份识别、required 字段、native->mainline 映射、nullable/engine-specific 边界，以及最小 compare 准入条件

5. 重建 plans 镜像
   - `reports/site/plans/trendline_confirmation_protocol.html`
   - `reports/site/plans/momentum_todo.html`

## 验证 / 证据

本轮是协议 / 页面细化，因此采用最小必要验证：

1. 页面重建
   - `./.venv/bin/python scripts/build_plans_site.py`

2. 本地 grep 验证协议页
   - `reports/site/plans/trendline_confirmation_protocol.html`
     - 已出现：`4.3 source onboarding checklist（v1）`
     - 已出现：`只有通过前 4 项，才值得继续做 compare page`
     - 已出现：`第 4 层：是否足够进入 compare`
     - 已出现：`partial ladder coverage`
     - 已出现：`mechanism-backed but not full-event-universe`

3. 本地 grep 验证 TODO 页
   - `reports/site/plans/momentum_todo.html`
     - 已出现：`[x] 在 confirmation protocol 中补 source onboarding checklist。`

## 风险 / 边界

- 这轮没有新增新的实验或统计结果；
- 它解决的是 **source onboarding 的执行顺序与 compare 准入纪律**，不是直接新增 alpha 证据；
- 这份 checklist 当前仍是 `v1`，后面随着新 source 增多，某些条件可能还会继续收紧或细分。

## 下一步建议

1. 如果继续沿这条 protocol 线程推进，下一步可以考虑：
   - 把这张 checklist 再进一步沉淀成一个更正式的 `schema checklist / onboarding card` 模板，方便每个 source 单独复用；
2. 如果转回实证推进，则可以开始：
   - 只让通过 checklist 前 4 层的 source 进入第一轮真实 ladder compare。

## Commit hash

- 已提交：`docs(momentum): add source onboarding checklist`
- 具体 hash 以本轮提交后的当前 `HEAD` 为准。

## 如果未提交，说明原因

本轮已做安全 selective commit。

我只提交了本轮涉及的 protocol / TODO / 运行记录文件，没有混入当前 repo 里与本轮无关的其它脏文件。