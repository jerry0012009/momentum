# 为 E 候选池补齐状态标签与缺失来源卡

## 为什么这次选这个

这轮继续沿上一轮刚定稿的 `Scout protocol v1` 往前推一个紧邻的小闭环。

上一轮已经把：
- 搜索协议
- 纳入门槛
- 来源卡模板

都写清楚了，但还差一个非常实际的落地层：**现有候选池并没有统一补齐 `evidence_status / fulltext_access`，而且 scout 页面引用了 `trendln` 与 `optimal stopping` 两个对象，但 literature map 里还没有对应来源卡。**

如果这一步不补，后面继续跑 2~3 轮 E 模块时，shortlist 还是会卡在：
- 哪些只是 read
- 哪些已经 deep dive done
- 哪些已经 parked
- 哪些真该继续 replication

这轮最值得复用/借鉴的点是：**当一个研究 intake 协议刚刚定稿后，下一步最该做的不是继续扩量找新材料，而是先把当前候选池补齐状态标签、全文可得性和缺失卡片；这样后面所有筛选、排序、shortlist 才真正可用。**

## 核心结论（中文摘要）

核心结论：**当前 `Trendline Alpha Scout` 的种子候选池已经补齐了最小状态标签体系：现有来源现在都能明确区分 `read / digest_done / deep_dive_done / replication_candidate / parked`，并且缺失的 `trendln` 与 `optimal stopping` 两张来源卡也已补回 literature map。**

证据如何支持这个结论：**本轮已在 `docs/LITERATURE_TRENDLINE_SIGNAL_MAP.md` 为现有来源卡统一补上 `fulltext_access` 与 `evidence_status`，新增 `trendln (GitHub repo)` 与 `The Support and Resistance Line Method: An Analysis via Optimal Stopping` 两张来源卡；同时重建后的 `reading/trendline_alpha_scout/report.html` 已显式出现“状态”列，`reports/site/plans/momentum_todo.html` 里“给每个候选打一个最小状态标签”也已变为 `[x]`。**

## 本轮做了什么改动

本轮只做一个主点：**把现有 E 候选池的状态标签与缺失来源卡补齐。**

具体改动：

1. 更新 `docs/LITERATURE_TRENDLINE_SIGNAL_MAP.md`
   - 为现有来源统一补上：
     - `fulltext_access`
     - `evidence_status`
   - 已覆盖的现有对象包括：
     - `pytrendline (GitHub repo)` → `repo_only + deep_dive_done`
     - `Ed Nunez blog` → `full_text + read`
     - `Chan 2022` → `full_text + parked`
     - `Svogun 2022` → `full_text + replication_candidate`
     - `Jiang/Kelly/Xiu 2023` → `abstract_only + deep_dive_done`

2. 同文件新增两张缺失来源卡
   - `trendln (GitHub repo)`
     - 当前定位：`explainability_reference`
     - 状态：`deep_dive_done`
   - `The Support and Resistance Line Method: An Analysis via Optimal Stopping`
     - 当前定位：confirmation / retest 的机制参考
     - 状态：`digest_done`

3. 更新 `docs/TODO.md`
   - 将：`给每个候选打一个最小状态标签` 标记为 `[x]`
   - 结果说明改为：当前种子来源卡已统一补齐 `evidence_status` 与 `fulltext_access`

4. 更新 `scripts/build_trendline_alpha_scout_report.py`
   - 在“首批种子材料”表中新增 `状态` 列
   - 在“初始 shortlist”表中新增 `状态` 列
   - 使页面现在能直接展示：
     - `deep_dive_done`
     - `digest_done`
     - `replication_candidate`
     - `parked`
     - `read`

5. 重建页面
   - `reports/site/reading/trendline_alpha_scout/report.html`
   - `reports/site/plans/momentum_todo.html`

## 验证 / 证据

本轮是研究组织 / 报告细化，因此采用最小必要验证：

1. 语法检查
   - `./.venv/bin/python -m py_compile scripts/build_trendline_alpha_scout_report.py scripts/build_plans_site.py`

2. 页面重建
   - `./.venv/bin/python scripts/build_trendline_alpha_scout_report.py`
   - `./.venv/bin/python scripts/build_plans_site.py`

3. 本地 grep 验证
   - `docs/LITERATURE_TRENDLINE_SIGNAL_MAP.md`
     - 已出现：`trendln (GitHub repo)`
     - 已出现：`The Support and Resistance Line Method: An Analysis via Optimal Stopping`
     - 已统一出现多个 `fulltext_access` / `evidence_status`
   - `reports/site/reading/trendline_alpha_scout/report.html`
     - 已出现：表头 `状态`
     - 已出现：`deep_dive_done / digest_done / replication_candidate / parked / read`
   - `reports/site/plans/momentum_todo.html`
     - 已出现：`[x] 给每个候选打一个最小状态标签`

## 风险 / 边界

- 这轮没有新增新的论文实验或新的 replication 运行；
- 它解决的是 **候选池状态可追踪性与页面/文档一致性**，不是直接新增 alpha 证据；
- `Jiang/Kelly/Xiu 2023` 当前先标成 `abstract_only + deep_dive_done`，代表它现在更适合作为结构理论母体，而不是马上进入高优先级 replication shortlist。

## 下一步建议

1. 继续按这套状态体系补第一批候选池
   - 目标是把来源卡数量补到 `10~20`

2. 然后做第一轮真正的 shortlist 收口
   - 从当前池里正式选出 `3~5` 个 replication candidates
   - 并在 scout 页面把 shortlist 与状态看板完全对齐

## Commit hash

- 已提交：`docs(momentum): backfill scout status labels`
- 具体 hash 以本轮提交后的当前 `HEAD` 为准。

## 如果未提交，说明原因

本轮已做安全 selective commit。

我只提交了本轮涉及的 literature map / TODO / scout 页面 / 运行记录文件，没有混入当前 repo 中与本轮无关的其它脏文件。