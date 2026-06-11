# 为 foundation 页补 source provenance / 接入状态区块

## 为什么这次选这个

这轮我没有继续做新的 strategy / signal / replication，而是收口一个早就挂在 TODO 里的 auditability 缺口：

- `Trendline Event Foundation Report` 之前已经有 taxonomy、sample coverage、event density、data gap checklist；
- 但它一直没有一块地方明确说明：
  - 当前到底有哪些 source 已经接进来了
  - 哪些 source 只是外围证据
  - 哪些关键 source 层还没接上

随着最近几轮我们连续接入：
- `PyIndicators confirmation ladder`
- `PyTrendline validation v1`
- `Cross-engine source comparison`
- `Svogun 2022 cost/regime experiment`

这个 provenance 空洞就越来越不该继续留着。

这轮最值得复用/借鉴的点是：**当一个 foundation 页开始承载越来越多“拼起来的证据”时，最重要的不是继续加更多结论，而是先把“这些结论分别来自哪一层 source”写清楚，否则页面会越来越像黑箱摘要。**

## 核心结论（中文摘要）

核心结论：**`Trendline Event Foundation Report` 现在终于补上了 `Current source provenance / what is already connected` 区块，能明确告诉读者：当前页面已经接入了哪些 source、哪些只是外围约束、以及最关键还缺什么。**

证据如何支持这个结论：**本轮不仅把 provenance 区块写进了 foundation HTML，还把同一信息写入了 `contract.json` 与新的 `source_provenance.csv`；其中已明确列出：`PyIndicators slope audit`、`confirmation ladder`、`PyTrendline validation v1`、`cross-engine source comparison`、`Svogun 2022 cost/regime experiment` 均已接入，而 `full event-universe / ladder-native source` 仍然缺失。**

## 本轮做了什么

本轮只做一个主点：**为 foundation 页补一个真正可审计的 source provenance 区块。**

具体改动：

1. 修改 `scripts/build_trendline_event_foundation_report.py`
   - 新增路径常量：
     - `CONFIRMATION_DIR`
     - `PYT_VAL_DIR`
     - `XENG_DIR`
     - `SVOGUN_DIR`
   - 新增 `build_source_provenance(...)`
     - 汇总当前已接入 / 未接入 source
     - 为每一层 source 写明：
       - `source_layer`
       - `status`
       - `path`
       - `current_scope`
       - `why_it_matters`

2. 在 foundation HTML 中新增卡片：
   - `Current source provenance / what is already connected`

3. 在 foundation contract 中同步新增：
   - `current_sources` 扩展字段
   - `source_provenance` records
   - `filled_artifacts` 新增 `source_provenance`

4. 新增导出：
   - `reports/artifacts/trendline_event_foundation/source_provenance.csv`

5. 更新 TODO：
   - 将“foundation 页补 source provenance / what is already connected 区块”标记为已完成 `[x]`

## 当前 provenance 区块明确了什么

它现在把 foundation 页的 source 层分成了 6 类：

1. **PyIndicators slope audit source**
   - 已接入
   - 是当前 foundation 最早期、最核心的 real-data base

2. **PyIndicators confirmation ladder**
   - 已接入
   - 已经把 foundation 延伸到 confirmation trade-off 这一层

3. **PyTrendline validation v1**
   - 已接入，但仍是 `bridge-v1`
   - 当前 scope 仍然窄：`BTC-USD / 10d / 5m / mostly breakout-touch`

4. **Cross-engine source comparison**
   - 已接入
   - 不提供新 event rows，但提供成熟度 / 证据广度的 provenance context

5. **External constraint track (Svogun 2022)**
   - 已接入，属于 external evidence
   - 现在已经能明确约束 foundation 的读法：后续 breakout 研究默认应报告 `gross / net / regime split`

6. **Full event-universe / ladder-native source**
   - 仍缺失
   - 这也是当前 foundation 距离“完整 event-study page”最大的缺口

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

- 在线页面返回 200：
  - `https://jp.jerrypsy.top/momentum/factors/trendline_event_foundation/report.html`
- 本地导出存在：
  - `reports/artifacts/trendline_event_foundation/source_provenance.csv`
- foundation contract 中可见：
  - `filled_artifacts` 已包含 `source_provenance`
  - `current_sources` 已包含 confirmation / pytrendline / cross-engine / svogun

## 风险 / 边界

- 这轮没有新增任何新的事件统计，只是提升 foundation 页的 auditability / explainability。
- provenance 区块不会自动解决“缺 full event-universe rows”的问题；它只是把这个缺口更清楚地暴露出来。
- 当前 foundation 仍然是 `partial_stats`，不是完整 ladder-native event-study page。

## 下一步建议

1. 如果继续走 foundation 主线：
   - 下一步应优先补 `full event-universe / ladder-native source`
   - 也就是 `raw_breach / close_confirm / confirm1 / confirm3 / retest_hold` 的 direct rows

2. 如果切回主线实验：
   - 以后在任何新报告里，都尽量沿用这种 provenance 写法
   - 避免页面越来越像“结论堆叠”，却不清楚这些结论来自哪个 source 层

## Commit hash

- `8c7ee97` — `feat(momentum): add foundation source provenance`

## 如果未提交，说明原因

本轮核心改动已安全 selective commit。

我刻意没有一起提交其它与本轮无关的 site / reading 脏文件，因为它们不属于这次 foundation provenance 的最小闭环。
