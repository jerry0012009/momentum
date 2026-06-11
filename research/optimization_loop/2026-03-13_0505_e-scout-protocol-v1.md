# 把 E 模块的 scout protocol 与来源卡模板正式定稿

## 为什么这次选这个

这轮我刻意顺着刚刚更新的节奏偏好往前推进：既然短期默认改成 **`2~3` 轮 E 模块 / `1` 轮主线验证**，那最先该补的不是随手再加一篇 digest，而是先把 **E 模块怎样算“有效推进”** 这件事定清楚。

否则后面连续几轮 E 很容易退化成：

- 搜到一些链接；
- 写几段印象；
- 但没有统一纳入门槛、没有统一来源卡字段、也没有 replication shortlist 的纪律。

这轮最值得复用/借鉴的点是：**当研究节奏从“主线偏重”切到“E 偏重”时，第一步应该先把侦察协议和来源卡模板定稿；这样后面的论文阅读、候选筛选、clean-room replication 才能稳定复用，而不是每轮重新发明标准。**

## 核心结论（中文摘要）

核心结论：**`trendline alpha scout` 现在已经有了正式的 `Scout protocol v1` 与 `来源卡最小字段 (v1)`，后续 E 模块不再只是“找论文”，而是按统一门槛筛材料、按统一卡片字段沉淀、再按统一动作层级决定做 digest / deep dive / replication brief / park。**

证据如何支持这个结论：**本轮已在 `docs/LITERATURE_TRENDLINE_SIGNAL_MAP.md` 明确补上搜索范围、4 项高优先级纳入门槛、7 项第一轮质量审计、来源卡最小字段 checklist，并将 `docs/TODO.md` 中对应的 `E1-A` / `E1-B` 条目标记为完成；同时重建了 `reading/trendline_alpha_scout/report.html` 与 plans 镜像页，页面中已能直接看到 `Scout protocol v1`、`来源卡最小字段（v1）` 和对应 TODO 勾选状态。**

## 本轮做了什么改动

本轮只做一个主点：**把 E 模块的搜集协议和来源卡模板正式定稿。**

具体改动：

1. 更新 `docs/LITERATURE_TRENDLINE_SIGNAL_MAP.md`
   - 新增 `Scout protocol v1（正式侦察协议）`
   - 明确每轮 E 默认优先覆盖的 6 类关键词簇：
     - trendline breakout / confirmation
     - failed breakout / rebound / rejection
     - support-resistance predictive features
     - retest / confirmation / filter
     - channel / regression channel
     - pivot / swing structure
   - 明确高优先级候选池的 4 项纳入门槛：
     - 近 5 年优先
     - 来源靠谱
     - 有代码 / GitHub / 明确可复刻实现
     - 能拿到全文
   - 明确第一轮质量审计的 7 项最小检查：
     - 结构定义是否清楚
     - event / confirmation / execution 是否分层
     - 是否有回测或可读证据
     - 是否讨论交易成本 / 滑点
     - 是否有 OOS / rolling / cross-asset
     - 是否疑似 future info / repaint
     - 是否能 clean-room 重写
   - 明确每轮 E 最终只允许落到四类动作之一：
     - `digest`
     - `deep dive`
     - `replication brief`
     - `park`

2. 同文件中补强 `来源卡最小字段 checklist (v1)`
   - 除原来的标题 / 作者 / 链接 / 市场 / alpha claim / 结构定义 / 是否有代码 / 风险 / 推荐动作外，新增明确要求：
     - `fulltext_access`
     - `evidence_status`
     - `license / source boundary`
     - `clean-room` 复现难度
   - 更新卡片模板，要求这些字段以后都可追踪。

3. 更新 `docs/TODO.md`
   - 将以下条目标记为 `[x]`：
     - `明确 trendline alpha scout 的搜索协议`
     - `明确允许保留的例外材料`
     - `定义统一的来源卡片字段`
   - 并补上结果说明，明确对应已经落到 `docs/LITERATURE_TRENDLINE_SIGNAL_MAP.md`。

4. 更新 `scripts/build_trendline_alpha_scout_report.py`
   - 在 scout 页面中新增：
     - `Scout protocol v1` 的说明提示
     - `来源卡最小字段（v1）` 表格
   - 把“下一步最小交付”说明改成显式引用 `Scout protocol v1`

5. 重建页面
   - `reports/site/reading/trendline_alpha_scout/report.html`
   - `reports/site/plans/momentum_todo.html`

## 验证 / 证据

本轮是文档 / 报告细化，因此采用最小必要验证：

1. 语法检查
   - `./.venv/bin/python -m py_compile scripts/build_trendline_alpha_scout_report.py scripts/build_plans_site.py`

2. 页面重建
   - `./.venv/bin/python scripts/build_trendline_alpha_scout_report.py`
   - `./.venv/bin/python scripts/build_plans_site.py`

3. 本地 grep 验证页面已反映本轮更新
   - `reports/site/reading/trendline_alpha_scout/report.html`
     - 已出现：`Scout protocol v1`
     - 已出现：`来源卡最小字段（v1）`
     - 已出现：`fulltext_access`
   - `reports/site/plans/momentum_todo.html`
     - 已出现：`[x] 明确 trendline alpha scout 的搜索协议。`
     - 已出现：`[x] 明确允许保留的例外材料。`
     - 已出现：`[x] 定义统一的来源卡片字段。`

## 风险 / 边界

- 这轮没有新增新的论文 digest / deep dive / replication 实验；
- 它解决的是 **E 模块的流程纪律与候选池标准化**，不是直接增加某个 alpha 结果；
- 真正的价值要在后续 2~3 轮 E 模块里体现出来：如果后续来源卡仍然不按这份协议填写，那这轮协议就只会停留在纸面层。

## 下一步建议

1. 直接按新协议补第一批 `10~20` 个候选来源卡
   - 优先把“能拿全文 + 有代码 / 伪代码 + 贴近当前结构事件主线”的对象补齐

2. 从中尽快选出第一批 `3~5` 个 replication candidates
   - 尤其优先：
     - confirmation / retest / failed breakout
     - support-resistance feature
     - cost / regime 会改写结论的对象

## Commit hash

- `14fa121` — `docs(momentum): formalize E scout protocol v1`

## 如果未提交，说明原因

本轮已做安全 selective commit。

我只提交了本轮涉及的协议 / TODO / scout 页面 / 运行记录文件，没有混入当前 repo 里其它无关脏文件。