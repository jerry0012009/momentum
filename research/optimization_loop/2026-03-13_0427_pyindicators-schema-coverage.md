# 把 PyIndicators 现有字段盘清到 unified schema

## 为什么这次选这个

这轮继续沿最近几轮的 `mainline / foundation / cross-engine mapping` 线程往前推一个很小但很实用的点：

- `PyTrendline` 这边已经有了最小 bridge v1；
- `PyIndicators` 虽然早就贡献了大量证据，但一直缺一条很明确的说明：**它现在到底已经有哪些字段能接进 unified event schema，哪些还没有。**

如果这一步不补，后面很容易出现两种误判：

1. 误以为 `PyIndicators` 还完全没有 schema bridge，只能从零重做；
2. 误以为 `trade_detail` 已经等于干净的 event-source export，忽略它仍然混着 execution 语义。

这轮最值得复用/借鉴的点是：**在进入“再做一轮新实验”之前，先把现有 source 的字段覆盖盘清，往往能用很小的工作量明显提高后续 Mainline 接入的可审计性。**

## 核心结论（中文摘要）

核心结论：**`PyIndicators` 现在已经具备一批可直接映射到 unified event schema 的核心字段（如 `source_engine / sample_key / event_family / line_side / event_timestamp / confirmation_level / engine_line_id / slope_bucket`），它并不是“完全没有 bridge”，但仍然缺一份与 execution 解耦的干净 event-source 导出。**

证据如何支持这个结论：**本轮直接核查了 `segment_strategy_events.csv`、`navigator_segments.csv`、`trendline_confirmation_ladder/trade_detail.csv` 三份现有产物，确认其中已经稳定存在 `strategy/strategy_event`、`side_label`、`signal_ts/candidate_ts`、`segment_id`、`ladder_label`、`slope_bucket` 等字段，并已把这些映射关系与缺口明确写入 `docs/CROSS_ENGINE_MAPPING.md`，同时将 TODO 对应条目标记为完成。**

## 本轮做了什么改动

本轮只做一个主点：**把 `PyIndicators` 当前字段覆盖正式写清楚，并挂回主线文档。**

具体改动：

1. 更新 `docs/CROSS_ENGINE_MAPPING.md`
   - 新增 `## 7. PyIndicators mapping v1（当前哪些字段已经能接 unified schema）`
   - 明确当前 3 份最可审计输入：
     - `reports/artifacts/trendline_segment_backtest/segment_strategy_events.csv`
     - `reports/artifacts/trendline_segment_backtest/navigator_segments.csv`
     - `reports/artifacts/trendline_confirmation_ladder/trade_detail.csv`
   - 明确哪些 unified 字段已经有直接落点：
     - `source_engine`
     - `sample_key`
     - `symbol`
     - `timeframe`（当前先保留 engine horizon label）
     - `event_family`
     - `line_side`
     - `event_timestamp`
     - `engine_line_id`
     - `line_origin_type`
     - `confirmation_level`
     - `is_provisional`
     - `slope_bucket`
   - 明确哪些字段目前只差一步派生：
     - `event_subtype`
     - `is_confirmed`
     - `bars_since_first_cross`
     - `bars_since_touch`
     - `sample_scope`
   - 明确哪些字段当前仍缺、或不应硬补：
     - `line_quality_bucket`
     - `num_points_bucket`
     - `score_bucket`
     - `is_representative`
     - `duplicate_group_id`
     - 与 execution 解耦后的 `full event-universe rows`

2. 更新 `docs/TODO.md`
   - 将 `B2-C` 里“明确哪些现有事件字段已经满足 unified event schema”标记为 `[x]`
   - 补一行结果说明，指向 `PyIndicators mapping v1`

3. 重建 plans 镜像
   - 重新生成：
     - `reports/site/plans/cross_engine_mapping.html`
     - `reports/site/plans/momentum_todo.html`

## 验证 / 证据

本轮做的是文档/报告细化，因此采用最小必要验证：

1. 先核查现有 CSV 表头与样例值
   - `segment_strategy_events.csv`
     - 已有：`strategy / event_type / side_label / candidate_ts / segment_id / segment_is_provisional`
   - `navigator_segments.csv`
     - 已有：`segment_id / side_label / is_provisional / slope / timeframe`
   - `trendline_confirmation_ladder/trade_detail.csv`
     - 已有：`sample_key / strategy_event / signal_ts / ladder_label / slope_bucket`

2. 重建镜像页面
   - 运行：`./.venv/bin/python scripts/build_plans_site.py`
   - 结果：`[ok] plans pages generated -> /root/clawd/jerry/momentum/reports/site/plans`

3. 本地 grep 验证页面已反映本轮更新
   - `reports/site/plans/cross_engine_mapping.html`
     - 已出现：`PyIndicators mapping v1（当前哪些字段已经能接 unified schema）`
   - `reports/site/plans/momentum_todo.html`
     - 已出现：`[x] 明确哪些现有事件字段已经满足 unified event schema。`

## 风险 / 边界

- 这轮没有新增任何新的事件统计或回测结果；
- 它解决的是 **schema coverage 可审计性**，不是 `PyIndicators` 已经完成 clean event export；
- 当前 `PyIndicators` 侧最核心的剩余缺口仍然是：**把 detection / confirmation 与 execution 分开导出**，否则后续 mainline 对照时还会继续混层。

## 下一步建议

1. 先做一份 `PyIndicators baseline event-source sample`
   - 只保留 detection / confirmation / line context
   - 不再把 trade execution 字段混在同一层

2. 然后再接第二个紧邻动作
   - 让这份 sample 真正按 unified schema 导出
   - 再和 `PyTrendline v1` 做更严格的 apples-to-apples source 对照

## Commit hash

未提交。

## 如果未提交，说明原因

当前 repo 工作区已经存在多批与本轮无关的脏文件，尤其是 `reports/site/*`、`reports/artifacts/*` 以及工作区上层若干未跟踪文件；而这轮又需要重建 `plans` 镜像，涉及的 `reports/site/plans/*.html` 本身也已经处于脏状态。

为了避免把之前未收口的 site/thread 变更一并打包进这轮自动优化，我这次选择**不做 selective commit**，只把原因明确记录下来。