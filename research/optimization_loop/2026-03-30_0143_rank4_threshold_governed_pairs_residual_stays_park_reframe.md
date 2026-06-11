# 2026-03-30 01:43 UTC · Rank 4 park residual -> threshold-governed pairs family residual

## 本轮执行小点
- target: `Rank 4 park residual -> threshold-governed pairs family residual`
- action: 只回答最近 `threshold governance / basket governance / dynamic sizing` 证据，是否已让 `Rank 4` 从旧 `pairs spread direct-entry` 失败边界中收敛成新的 queue-facing 对象
- success_criterion: 若它能形成与既有 `Rank 4c` 不重复、边界清楚、可单轮证伪的新对象，则正式写成 fresh intake；否则明确写成 `继续留在 park_reframe，不进入前排`

## 读取到的既有 runtime / park 约束
- `BOT2_BOT3_STATE.md` 当前前排为空，因此本轮合法动作落到第一个 `fresh intake` 小点。
- `research/park_reframe/2026-03-24_1430_rank4-park-reframe.md` 已经明确：
  - 原 `Rank 4` 的 direct-entry pairs alpha 继续 `park`；
  - 唯一诚实的窄派生仍是既有 `Rank 4c`；
  - `threshold governance + basket governance + dynamic sizing` 更像一条新的 **full-stack pairs raw-alpha family**，而不是原 `Rank 4` 可再诚实切出的一刀 `Rank 4d`。
- `research/park_reframe/INDEX.md` 也把 `2026-03-24 14:30` 这轮结论登记为 `soft_reframe_candidate`，并明确写成：主题未死，但已超出原 Rank 4 可窄救边界。

## 本轮只回答这一个问题
### 1) threshold governance 不是单一窄轴
`2026-03-29_1350_pair-rebalancing-threshold-map-alpha.md` 给出的新增价值，核心是在说：
- pair-rebalancing 的成败受 pair 统计属性影响；
- threshold 需要随 pair 结构而变；
- 这不是“原 Rank 4 多补一个 entry threshold 参数”就能诚实表达的增强。

换成人话：它证明的不是“原 Rank 4 只差一个更聪明的阈值”，而是“pairs 这类东西如果要活，阈值本身就是策略设计的一大块”。

### 2) basket governance 说明对象已经从单条残余变成完整家族
前一轮 park reframe 已经写明：新证据真正抬升的是 **pairs full-stack family**，因为它默认连同：
- 哪些 pair 能进 basket；
- 阈值怎么按 pair 特征分层；
- 成本与换仓怎么处理；
- 是否需要共享风险预算层；
一起重写。

这已经不是原 `Rank 4` 从失败边界里剩下的一条“唯一主修改轴”，而是另一条更宽的 raw-alpha 家族入口。

### 3) dynamic sizing 更像风险预算层，不是原始 spread alpha 本体
`2026-03-24_1424_rl2-pairs-dynamic-scaling-fullstack.md` 对 desk 最有用的读法，本身就是：
- 先看 `cointegration spread raw alpha + dynamic sizing` 的**完整骨架**；
- 而不是把 dynamic sizing 伪装成原 `Rank 4` 的一个小修补件。

因此这条新增旁证并没有把对象收敛成更窄，反而进一步证明：如果真要重开，会是一个新 family intake，而不是 `Rank 4` 的 queue-facing residual。

## 结论
**`Rank 4 park residual -> threshold-governed pairs family residual` 仍不足以形成一个与既有 `Rank 4c` 不重复、边界清楚、可单轮证伪的新对象；新增 evidence 抬升的是另一条 full-stack pairs raw-alpha family，而不是原 `Rank 4` 的窄 residual。**

## runtime 写回口径
- 本轮不分配新 Rank；
- 不把该对象写入 `Fresh intake slot` 前排；
- 正式 verdict：`继续留在 park_reframe，不进入前排`。

## 产出文件
- 本日志：`research/optimization_loop/2026-03-30_0143_rank4_threshold_governed_pairs_residual_stays_park_reframe.md`
