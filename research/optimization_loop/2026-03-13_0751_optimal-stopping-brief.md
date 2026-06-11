# 给 Optimal Stopping 正式补一张 mechanism brief，并收口候选角色分类

## 为什么这次选这个

这轮继续严格沿最近几轮的 E 线程往前推进，没有新开题，而是直接顺着 `replication shortlist v1` 补一个最近且明确的缺口：

- 上一轮已经把 `pytrendline` 正式补成了 `active bridge brief`；
- 当前 `Trendline Replication Briefs` 里还缺 shortlist 里的另一个关键对象：`Optimal Stopping`；
- 同时 `docs/TODO.md` 里还残留一个紧邻未完成项：**明确哪些候选更适合 mainline event source / feature candidate / filter / confirmation / pure explainability reference。**

所以这轮没有再扩候选池，也没有重跑实验，而是做一个非常小但有收口价值的动作：**给 `Optimal Stopping` 正式补一张 mechanism brief，并把候选角色分类落到网页上。**

这轮最值得复用/借鉴的点是：**当 shortlist 里既有 paper replication、又有 engine bridge、也有 mechanism paper 时，不要把它们都硬塞进同一种模板；更好的做法是按“paper / bridge / mechanism”三种 brief 角色分别落地。**

## 核心结论（中文摘要）

核心结论：**`Optimal Stopping` 现在已经正式进入 `Trendline Replication Briefs` 作为一张 `mechanism brief`；与此同时，shortlist 候选的角色分类也已经被网页化，当前可以明确区分谁更像 `mainline event source`、谁更像 `feature candidate`、谁更像 `filter / confirmation`、谁更像 `pure explainability reference`。**

证据如何支持这个结论：**本轮已更新 `scripts/build_trendline_replication_briefs_report.py`，重建后的 `reports/site/reading/trendline_replication_briefs/report.html` 中已经出现 `Brief C · Optimal Stopping S/R paper` 与 `候选角色对照（对应 E3-B）`；同时 `reports/site/plans/momentum_todo.html` 已把“明确哪些候选更适合 ...”标记为 `[x]`。**

## 本轮做了什么改动

本轮只做一个主点：**把 `Optimal Stopping` 正式纳入 brief 体系，并把候选角色分类收口。**

具体改动：

1. 更新 `scripts/build_trendline_replication_briefs_report.py`
   - 调整 `Replication / Bridge priority` 表的顺序与说明，使其更贴近当前 shortlist v1：
     - `Svogun 2022`
     - `pytrendline`
     - `Optimal Stopping`
     - `trendln`
   - 把 `Optimal Stopping` 从“待补 brief”推进成正式 brief 对象

2. 在同页新增：
   - `候选角色对照（对应 E3-B）`
   - 当前明确：
     - `pytrendline -> mainline event source`
     - `Chan 2022 -> feature candidate`
     - `Svogun 2022 / Optimal Stopping -> filter / confirmation`
     - `trendln / Ed Nunez blog -> pure explainability reference`

3. 在同页新增：
   - `Brief C · Optimal Stopping S/R paper`
   - 明确它不是经验 alpha replication，而是 `mechanism brief`
   - brief 里明确写了：
     - 我们准备复现什么：`touch / break / confirmed switch / retest_hold` 的 protocol mapping
     - 我们用什么数据：优先复用现有 `pytrendline / PyIndicators` 结构线来源
     - 最小 clean-room 定义：
       - `touch_or_cross`
       - `provisional_break`
       - `confirmed_switch`
     - 第一版可允许的 confirmed-switch 证据：
       - `confirm1`
       - `confirm3`
       - `retest_hold`
     - 成功标准：不是复刻数学结果，而是证明这篇论文能稳定反哺当前 confirmation / retest protocol 设计

4. 更新同页“当前已落地页面”与“我建议的落地顺序”
   - 增加：
     - `Optimal Stopping · Quant Digest`
     - `Trendline Confirmation Protocol`
   - 明确当前角色：
     - `Svogun 2022 = active paper replication`
     - `pytrendline = active bridge brief`
     - `Optimal Stopping = mechanism brief`
     - `trendln = 仍待补 brief`

5. 更新 `docs/TODO.md`
   - 在 `为每个 replication candidate 产出一张 replication brief` 下补记：
     - `Trendline Replication Briefs` 已新增 `Optimal Stopping` 的 mechanism brief
   - 明确当前仍待补：
     - `trendln`
   - 将：
     - `明确哪些候选更适合 ...` 标记为 `[x]`
     - 并补一句结果说明，指向 brief 页里的 `候选角色对照（对应 E3-B）`

6. 重建页面
   - `reports/site/reading/trendline_replication_briefs/report.html`
   - `reports/site/plans/momentum_todo.html`

## 验证 / 证据

本轮是文档 / brief / 页面细化，因此采用最小必要验证：

1. 语法检查
   - `./.venv/bin/python -m py_compile scripts/build_trendline_replication_briefs_report.py scripts/build_plans_site.py`

2. 页面重建
   - `./.venv/bin/python scripts/build_trendline_replication_briefs_report.py`
   - `./.venv/bin/python scripts/build_plans_site.py`

3. 本地 grep 验证
   - `reports/site/reading/trendline_replication_briefs/report.html`
     - 已出现：`候选角色对照（对应 E3-B）`
     - 已出现：`pytrendline -> mainline event source`
     - 已出现：`trendln -> pure explainability reference`
     - 已出现：`Brief C · Optimal Stopping S/R paper`
     - 已出现：`mechanism brief`
   - `reports/site/plans/momentum_todo.html`
     - 已出现：`[x] 明确哪些候选更适合：`
     - `为每个 replication candidate 产出一张 replication brief` 仍保持未完成，因为 `trendln` 还没补上

## 风险 / 边界

- 这轮没有新增新的实证实验，也没有把 `Optimal Stopping` 真正挂回 confirmation protocol 页面；
- 它解决的是 **brief 类型分层与候选角色分类**，不是直接新增收益证据；
- `Optimal Stopping` 仍然是 mechanism / protocol brief，不应被误读成“已经验证能赚钱的直接规则”。

## 下一步建议

1. 继续沿同一线程补最后一个 shortlist v1 缺口
   - 给 `trendln` 补最后一张 brief

2. 然后做一个更实的回挂动作
   - 把 `Optimal Stopping` 里的 `touch / provisional_break / confirmed_switch / retest_hold` 显式映射到 `Trendline Confirmation Protocol`

3. 保持这条结构纪律
   - `paper` → replication brief
   - `engine` → bridge brief
   - `mechanism` → protocol / mechanism brief

## Commit hash

- 已提交：`docs(momentum): add optimal stopping mechanism brief`
- 具体 hash 以本轮提交后的当前 `HEAD` 为准。

## 如果未提交，说明原因

本轮已做安全 selective commit。

我只提交了本轮涉及的 brief 页面 / TODO / 运行记录文件，没有混入当前 repo 里与本轮无关的其它脏文件。