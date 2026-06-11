# 为 foundation 页补 bucket glossary（读者可直接解码标签）

## 为什么这次选这个

这轮没有继续开新实验，也没有再补新的 replication / signal，而是沿上一轮刚补完的 `foundation provenance` 继续收口一个紧邻的小缺口：

- `Trendline Event Foundation Report` 现在已经有了：
  - taxonomy mapping
  - sample coverage
  - event density
  - data gap checklist
  - source provenance
- 但它仍缺一个非常影响可读性的东西：
  - **bucket glossary**

也就是：读者看到 `confirmed_breakout_long / short`、`up_* / down_* / flat`、`score_bucket / line_quality_bucket / num_points_bucket`、`representative_only vs all_valid` 这些词时，页面本身并没有一块地方用“人话”解释它们到底是什么意思。

这轮最值得复用/借鉴的点是：**当 foundation 页开始承载越来越多统计与标签时，优先补“读者如何解码这些标签”的 glossary，往往比再加一张新表更能提升实际可用性。**

## 核心结论（中文摘要）

核心结论：**`Trendline Event Foundation Report` 现在已经补上了 `Bucket glossary / how to read the labels`，读者不需要再来回翻设计文档，也能直接理解当前 event / slope / quality / source-scope buckets 在页面里各自代表什么。**

证据如何支持这个结论：**本轮不仅把 glossary 卡片写进了 foundation HTML，还同步导出了 `reports/artifacts/trendline_event_foundation/bucket_glossary.csv`，并把 `contract.json` 的 `filled_artifacts` 扩展为包含 `bucket_glossary`；说明它不只是视觉说明块，而是已经成为 foundation contract 的正式组成部分。**

## 本轮做了什么

本轮只做一个主点：**为 foundation 页补一个真正可复用的 bucket glossary。**

具体改动：

1. 修改 `scripts/build_trendline_event_foundation_report.py`
   - 新增 `build_bucket_glossary()`
   - 统一导出一个 reader-facing glossary 表

2. glossary 当前覆盖的 bucket 类型：
   - `event_bucket`
     - `confirmed_breakout_long / short`
     - `confirmed_rebound_long / short`
   - `future ladder bucket`
     - `raw_breach / close_confirm_same_bar / confirm1 / confirm3 / retest_hold`
   - `line_side`
     - `support / resistance`
   - `slope bucket`
     - `up_* / down_* / flat`
   - `quality bucket`
     - `score_bucket / line_quality_bucket / num_points_bucket`
   - `source scope`
     - `representative_only vs all_valid`
   - `external constraint bucket`
     - `gross / net_low / net_high / bubble_proxy`

3. 在 foundation HTML 中新增卡片：
   - `Bucket glossary / how to read the labels`

4. 同步更新 contract / artifacts：
   - `reports/site/factors/trendline_event_foundation/contract.json`
   - `reports/artifacts/trendline_event_foundation/bucket_glossary.csv`

5. 更新 TODO：
   - 将“在 foundation 页面中增加一个更明确的 bucket glossary”标记为已完成 `[x]`

## 现在这块 glossary 真正解决了什么

它最主要解决的是三个实际阅读问题：

1. **当前已接入 bucket 和未来目标 bucket 不再混淆**
   - 现在页面里明确区分：
     - 当前真实接入的是 `confirmed_breakout / confirmed_rebound`
     - 未来还缺的是 `raw_breach / close_confirm / confirm1 / confirm3 / retest_hold`

2. **方向桶 / 质量桶不再像内部黑话**
   - 现在读者能直接看到：
     - `slope bucket` 关注的是“方向 × 强度”
     - `quality bucket` 关注的是“higher-score / denser-line 是否更像有效事件”

3. **外部约束切片也被纳入统一 glossary**
   - `gross / net / bubble_proxy` 现在被明确标记为：
     - 这不是 event bucket 本身
     - 但它是后续 breakout 主线默认应报告的外部约束切片

## 验证 / 证据

最小必要验证：

- `./.venv/bin/python -m py_compile scripts/build_trendline_event_foundation_report.py scripts/build_plans_site.py`
- `./.venv/bin/python scripts/build_trendline_event_foundation_report.py`
- `./.venv/bin/python scripts/build_plans_site.py`

发布：

- `reports/site/factors/trendline_event_foundation/report.html`
- `reports/site/factors/trendline_event_foundation/contract.json`
- `reports/site/plans/momentum_todo.html`

验证结果：

- 本地已导出：
  - `reports/artifacts/trendline_event_foundation/bucket_glossary.csv`
- foundation contract 中可见：
  - `filled_artifacts` 已新增 `bucket_glossary`
- 在线页面返回 200：
  - `https://jp.jerrypsy.top/momentum/factors/trendline_event_foundation/report.html`

## 风险 / 边界

- 这轮没有新增新的统计证据，也没有改变 foundation 的 event universe；
- 它解决的是 **阅读与解释层的缺口**，不是新的回测缺口；
- 因此它的价值在于减少“同样标签反复解释”的沟通成本，而不是直接改变当前主线判断。

## 下一步建议

1. 如果继续沿 foundation 收口：
   - 下一步就该优先补 `full event-universe / ladder-native source`
   - 也就是让 `raw_breach / close_confirm / confirm1 / confirm3 / retest_hold` 真正成为 direct rows

2. 如果切回主线实验：
   - 以后任何新页面都尽量沿用 glossary + provenance 这两个配套块
   - 这样页面不会越来越“内部人可读、外部人费解”

## Commit hash

- `aee441e` — `feat(momentum): add foundation bucket glossary`

## 如果未提交，说明原因

本轮核心改动已安全 selective commit。

我刻意没有一起提交其它与本轮无关的 site / reading 脏文件，因为它们不属于这次 foundation glossary 的最小闭环。
