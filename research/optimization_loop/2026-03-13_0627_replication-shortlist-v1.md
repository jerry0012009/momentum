# 修正 E 候选池底稿并正式给出 replication shortlist v1

## 为什么这次选这个

这轮继续沿最近 3 轮的 E 线程往前推进，但没有再盲目加新论文，而是先收口一个更近、更必要的缺口：

- 上一轮已经把 `Scout protocol v1`、状态标签体系和 scout 页面都搭起来了；
- 但当前 `docs/LITERATURE_TRENDLINE_SIGNAL_MAP.md` 里还残留一处卡片重复/错位问题；
- 同时 `shortlist` 还停留在“建议优先顺序”的半成品状态，没有真正定成第一版正式名单。

如果这一步不补，后面继续跑 E 模块会有两个明显问题：

1. 候选池底稿本身不够干净，auditability 会下降；
2. 大家会反复讨论“哪些算 shortlist，哪些只是参考材料”，而不是直接往 replication / bridge / deep dive 上推进。

这轮最值得复用/借鉴的点是：**当 intake / protocol 已经搭起来后，下一步优先做“候选池去重校准 + shortlist 正式化”，比继续扩量搜新材料更能提升后续 E 任务的可执行性。**

## 核心结论（中文摘要）

核心结论：**当前 `Trendline Alpha Scout` 已经从“候选池草稿”升级成有正式名单的 `replication shortlist v1`：在修正卡片重复/错位后，第一批先收口为 4 个对象——`Svogun 2022`、`pytrendline`、`trendln`、`Optimal Stopping`。**

证据如何支持这个结论：**本轮已修正 `docs/LITERATURE_TRENDLINE_SIGNAL_MAP.md` 中 `pytrendline / trendln / Ed Nunez blog` 一段的重复与错位，并新增 `第一版 replication shortlist（2026-03-13）`；重建后的 scout 页面已把 shortlist 正式展示为 `正式 shortlist v1`，而 `docs/TODO.md` 中“选出第一批 3~5 个 replication candidates”和“生成 Trendline Alpha Scout 总览页”两项也已同步勾选。**

## 本轮做了什么改动

本轮只做一个主点：**把 E 候选池底稿修干净，并正式给出第一版 shortlist。**

具体改动：

1. 修正 `docs/LITERATURE_TRENDLINE_SIGNAL_MAP.md`
   - 重写了第一批种子来源卡中这 3 张卡的底稿，消除了重复/错位：
     - `pytrendline (GitHub repo)`
     - `trendln (GitHub repo)`
     - `Building a reliable and testable day trading bot on python`
   - 验证后，这 3 个标题现在都只出现 1 次。

2. 在同文件中新增正式名单：
   - `## 第一版 replication shortlist（2026-03-13）`
   - 当前先收口为 4 个对象：
     1. `Svogun 2022` — 成本 / regime 约束复现
     2. `pytrendline` — event-source bridge
     3. `trendln` — geometry / channel baseline
     4. `Optimal Stopping` — confirmation / retest 机制候选
   - 并明确暂不进入 shortlist 的对象：
     - `Chan 2022`
     - `Jiang/Kelly/Xiu 2023`
     - `Ed Nunez blog`

3. 更新 `docs/TODO.md`
   - 将 `从 intake queue 中选出第一批 3~5 个 replication candidates` 标记为 `[x]`
   - 将 `在网页侧生成一个 Trendline Alpha Scout 总览页` 标记为 `[x]`
   - 并补上结果说明，说明当前 shortlist v1 的 4 个对象与排除项。

4. 更新 `scripts/build_trendline_alpha_scout_report.py`
   - 将页面中的“初始 shortlist（建议优先顺序）”升级为：
     - `正式 shortlist v1（2026-03-13）`
   - 改成更正式的字段：
     - 候选
     - 角色
     - 状态
     - 为什么入选
     - 下一步
   - 同时在页面里明确写出“不进 shortlist”的对象。

5. 重建页面
   - `reports/site/reading/trendline_alpha_scout/report.html`
   - `reports/site/plans/momentum_todo.html`

## 验证 / 证据

本轮是研究组织 / 文档 / 页面细化，因此采用最小必要验证：

1. 语法检查
   - `./.venv/bin/python -m py_compile scripts/build_trendline_alpha_scout_report.py scripts/build_plans_site.py`

2. 页面重建
   - `./.venv/bin/python scripts/build_trendline_alpha_scout_report.py`
   - `./.venv/bin/python scripts/build_plans_site.py`

3. 本地 grep / 计数验证
   - `docs/LITERATURE_TRENDLINE_SIGNAL_MAP.md`
     - 已出现：`第一版 replication shortlist（2026-03-13）`
     - `pytrendline / trendln / Ed Nunez blog` 各标题都只剩 1 次
   - `reports/site/reading/trendline_alpha_scout/report.html`
     - 已出现：`正式 shortlist v1（2026-03-13）`
     - 已出现：`event-source bridge / geometry / channel baseline / Optimal Stopping S/R paper`
     - 已出现：“当前明确不进 shortlist”说明
   - `reports/site/plans/momentum_todo.html`
     - 已出现：`[x] 从 intake queue 中选出第一批 3~5 个 replication candidates`
     - 已出现：`[x] 在网页侧生成一个 Trendline Alpha Scout 总览页`

## 风险 / 边界

- 这轮没有新增新的 digest / deep dive / replication 实验；
- 它解决的是 **shortlist 正式化与候选池底稿洁净度**，不是直接增加新的 alpha 证据；
- 当前 shortlist v1 里有 2 个更偏 bridge / baseline / mechanism 的对象，而不是全部都是“论文 + 官方代码”的高确定性 replication 对象，这反映的是当前候选池仍然偏小、且与主线贴得最近的材料类型本身就不完全相同。

## 下一步建议

1. 优先为 shortlist v1 中仍缺正式 brief 的对象补齐 brief
   - 尤其是：
     - `pytrendline`
     - `trendln`
     - `Optimal Stopping`

2. 继续把候选池扩到 `10~20`
   - 但默认优先补：
     - confirmation / retest
     - failed breakout / rebound
     - support-resistance feature with public code

3. 等候选池扩大后，再考虑 `shortlist v2`
   - 不要在当前只有少量候选时频繁改 shortlist 口径。

## Commit hash

- 已提交：`docs(momentum): formalize replication shortlist v1`
- 具体 hash 以本轮提交后的当前 `HEAD` 为准。

## 如果未提交，说明原因

本轮已做安全 selective commit。

我只提交了本轮涉及的 literature map / TODO / scout 页面 / 运行记录文件，没有混入当前 repo 里与本轮无关的其它脏文件。