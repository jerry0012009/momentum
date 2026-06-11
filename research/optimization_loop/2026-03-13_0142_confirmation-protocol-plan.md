# 把 confirmation ladder 升级成跨引擎可复用协议

## 为什么这次选这个

这轮没有继续做新统计，而是收口 `A1-C` 里一直开着、但价值很高的一条：

- **把 ladder 比较真正升级成跨引擎可复用协议，而不是只绑定当前单一 source。**

之所以现在做这件事，时机其实正好：

1. `PyIndicators confirmation ladder` 已经有了第一批真实结论；
2. `PyTrendline` 也已经从 explainability 进入了 `bridge + validation v1`；
3. 如果不把 confirmation 层抽成协议，后面就很容易出现：
   - 两边都说自己做了“confirmation”
   - 但其实比较的不是同一层东西

所以，这轮最值得复用/借鉴的点是：**当主线开始出现多个 source 时，最应该先协议化的不是最终策略，而是事件确认层本身。**

## 核心结论（中文摘要）

核心结论：**`confirmation ladder` 现在不应再被理解成“PyIndicators 那一页报告”，而应被理解成 `Structure-Event Mainline` 的跨引擎 confirmation protocol。**

证据如何支持这个结论：**本轮已经把这套协议写成独立文档与站点页 `Trendline Confirmation Protocol`，明确规定了 breakout / rebound 的统一 confirmation level、最小必备字段、最小比较输出表，以及什么情况下才算“更强确认值得保留为默认口径”；同时也明确写出了 `PyIndicators` 是当前 `source #1`，而 `PyTrendline v2` 的目标是补齐进入该协议所缺的层级。**

## 本轮做了什么

本轮只做一个主点：**把 confirmation ladder 升级成一份 Mainline 级别的协议文档。**

具体改动：

1. 新增文档：
   - `docs/TRENDLINE_CONFIRMATION_PROTOCOL.md`

2. 这份协议文档明确了：
   - confirmation protocol 的目标与边界
   - 它管什么 / 不管什么
   - 统一 `event_family`
   - 统一 `confirmation_level`（breakout 与 rebound ladders）
   - 最小必备字段
   - 最小比较输出表
   - 主线判定规则：什么时候说“更强确认值得保留”
   - `PyIndicators v1` 当前如何接入
   - `PyTrendline v1/v2` 如何接入

3. 更新 plans 镜像生成：
   - `scripts/build_plans_site.py`
   - 新增 plan 页：
     - `reports/site/plans/trendline_confirmation_protocol.html`

4. 更新 TODO：
   - 将 `A1-C` 中“把 ladder 比较真正升级成跨引擎可复用协议”标记为已完成 `[x]`

## 协议里最重要的 4 个约束

### 1) confirmation level 必须统一到主线标签

#### breakout ladder
- `raw_breach`
- `close_confirm_same_bar`
- `confirm1`
- `confirm3`
- `retest_hold`

#### rebound ladder
- `touch_only`
- `inside_0`
- `inside_1`
- `inside_2`
- `inside_3plus`

这意味着以后各引擎可以保留 native 状态名，但进入主线比较时，必须映射到这些统一层。

### 2) 每个 source 至少吐同一套最小字段

至少包含：
- `source_engine`
- `sample_key`
- `symbol`
- `timeframe`
- `event_family`
- `confirmation_level`
- `event_timestamp`
- `line_side`
- `engine_line_id`
- `is_representative`
- `slope_bucket`
- `line_quality_bucket`
- `sample_scope`

### 3) 每个 source 至少给 3 张表

- `overall ladder summary`
- `side split summary`
- `bucket split summary`

### 4) 默认判定不能只看收益均值

最少同时看：
1. `up_ratio_after_h / positive_asset_ratio`
2. `mean_forward_return_h / mean_total_return`
3. `trade_retention / sample_count retention`

也就是说：
- 只提高均值但 retention 崩塌 → 不足以升默认口径
- 只提高胜率但均值不改善 → 更像 filter 候选
- 三者一起改善 → 才能进 `default candidate`

## 这轮为什么对后续任务有帮助

它直接解决了一个未来很容易踩坑的问题：

- 以后如果继续接 `PyTrendline v2`、`channel source`、甚至更多 confirmation 逻辑，
- 不会再每个人各写一套“确认层名字”和“判断标准”。

也就是说，它的价值不在于新增某个回测统计，而在于：

> **把后续 confirmation 研究统一到了同一个 contract 上。**

## 验证 / 证据

最小必要验证：

- `./.venv/bin/python -m py_compile scripts/build_plans_site.py`
- `./.venv/bin/python scripts/build_plans_site.py`

发布：

- `reports/site/plans/trendline_confirmation_protocol.html`
- `reports/site/plans/momentum_todo.html`
- `reports/site/plans/index.html`
- `reports/site/plans/report.html`

在线验证：

- `https://jp.jerrypsy.top/momentum/plans/trendline_confirmation_protocol.html` 已上线
- `https://jp.jerrypsy.top/momentum/plans/momentum_todo.html` 已反映对应 TODO 条目完成状态

## 风险 / 边界

- 这轮没有新增新的 confirmation 统计结果；
- 它解决的是“协议与可比性”问题，不是“哪一档确认最终最优”问题；
- 后续真正要发挥它的价值，还要靠 `PyTrendline v2` 或其它 source 按这份协议接入。

## 下一步建议

1. 如果继续走主线：
   - 下一步最合理的是让 `PyTrendline v2` 补齐进入 confirmation protocol 所需的层级
   - 尤其是：
     - `rebound / retest`
     - `representative_only vs all_valid`
     - 更明确的 `close_confirm / confirm1 / confirm3 / retest_hold`

2. 如果继续走 foundation：
   - 可以把这份 protocol 显式挂回 foundation provenance / glossary，作为“当前已存在的协议层”

## Commit hash

- `3a6fd04` — `docs(momentum): add confirmation protocol plan`

## 如果未提交，说明原因

本轮核心改动已安全 selective commit。

我刻意没有一起提交与本轮无关的其它 site / reading / factors 脏文件，因为它们不属于这次 confirmation protocol 的最小闭环。
