# 把 confirmation protocol 反挂回 foundation 页

## 为什么这次选这个

这轮没有继续做新的实验或新统计，而是沿最近两轮 `foundation provenance + foundation glossary + confirmation protocol` 这条很近的线程继续收口一个小缺口：

- `Trendline Event Foundation Report` 现在已经有 provenance；
- `Trendline Confirmation Protocol` 也已经独立成文；
- 但 foundation 本身还没有明确把这个 protocol 当作一个独立层来承认。

如果不补这一步，读者还是很容易把 confirmation 理解成“某一页 PyIndicators 报告的局部实现”，而不是 Mainline 的统一 contract。

这轮最值得复用/借鉴的点是：**当一个协议文档已经单独存在时，最好尽快把它回挂到 foundation provenance 里；否则协议层和证据层会被页面结构重新割裂。**

## 核心结论（中文摘要）

核心结论：**foundation 页现在已经正式承认 `confirmation protocol` 是一个独立的 protocol layer，confirmation 不再只是某个 source 的局部实现，而是 Mainline 的统一比较 contract。**

证据如何支持这个结论：**本轮不仅把 `Confirmation protocol layer` 写进了 `source_provenance.csv`，还把 `confirmation_level protocol` 写进了 `bucket_glossary.csv`，同时 `contract.json` 的 `current_sources` 也新增了 `confirmation_protocol`；说明这不是一句说明文字，而是已经进入 foundation 的正式 contract 与 provenance 导出。**

## 本轮做了什么

本轮只做一个主点：**把 `Trendline Confirmation Protocol` 反挂回 foundation。**

具体改动：

1. 修改 `scripts/build_trendline_event_foundation_report.py`
   - 新增常量：
     - `CONFIRMATION_PROTOCOL_DOC = ROOT / "docs" / "TRENDLINE_CONFIRMATION_PROTOCOL.md"`

2. 在 `build_source_provenance(...)` 中增加一层：
   - `Confirmation protocol layer`
   - 状态标记为 `connected (protocol)`
   - scope 说明为：
     - breakout / rebound ladder labels
     - required fields
     - required output tables
     - default judgement rules

3. 在 `build_bucket_glossary()` 中增加一行：
   - `protocol layer / confirmation_level protocol`
   - 明确告诉读者：
     - confirmation 不再只是某个 source 的局部实现
     - 而已经被提升成 Mainline 的统一比较 contract

4. 在 foundation contract 中新增：
   - `current_sources.confirmation_protocol = docs/TRENDLINE_CONFIRMATION_PROTOCOL.md`

5. 更新 TODO 已完成条目说明：
   - 现在不仅有 protocol 文档本身
   - foundation 也已经把它作为 `protocol layer` 接入 provenance / glossary

## 验证 / 证据

最小必要验证：

- `./.venv/bin/python -m py_compile scripts/build_trendline_event_foundation_report.py scripts/build_plans_site.py`
- `./.venv/bin/python scripts/build_trendline_event_foundation_report.py`
- `./.venv/bin/python scripts/build_plans_site.py`

发布：

- `reports/site/factors/trendline_event_foundation/report.html`
- `reports/site/factors/trendline_event_foundation/contract.json`
- `reports/site/plans/momentum_todo.html`

关键本地证据：

- `reports/artifacts/trendline_event_foundation/source_provenance.csv`
  - 已新增 `Confirmation protocol layer`
- `reports/artifacts/trendline_event_foundation/bucket_glossary.csv`
  - 已新增 `protocol layer / confirmation_level protocol`
- `reports/site/factors/trendline_event_foundation/contract.json`
  - `current_sources` 已新增 `confirmation_protocol`

在线验证：

- `https://jp.jerrypsy.top/momentum/factors/trendline_event_foundation/report.html` 返回 200

## 风险 / 边界

- 这轮没有新增新的统计与样本，只是提升 foundation 的结构一致性；
- 它解决的是“协议层没有回挂到 foundation”的问题，不是“full event-universe rows 仍缺失”的问题；
- 因此它的价值在于让页面结构与当前主线心智模型一致，而不是直接改变研究结论。

## 下一步建议

1. 如果继续沿 foundation 收口：
   - 下一个更值得补的仍然是 `full event-universe / ladder-native source`

2. 如果切回主线实验：
   - 以后所有新的 confirmation / rebound 页面，默认都应显式引用这份 protocol
   - 避免再次回到“每页自己发明一套确认层名字”的状态

## Commit hash

- `27da13c` — `docs(momentum): wire protocol into foundation`

## 如果未提交，说明原因

本轮核心改动已安全 selective commit。

我刻意没有一起提交其它与本轮无关的 site / reading / factors 脏文件，因为它们不属于这次 foundation protocol-layer 收口的最小闭环。
