# 2026-04-08 10:30 UTC · Rank 28 fresh intake first verdict

## Executed step
- cycle_plan item: `2`
- target: `research/park_reframe/2026-04-08_0019_rank28-park-reframe.md`
- action: 判断更快的 `leader-laggard delayed catch-up` 读法是否已足够从旧 `Rank 28` 的 residual 收敛成新的正式 raw alpha intake

## Evidence used
- `research/park_reframe/2026-04-08_0019_rank28-park-reframe.md`
- `docs/PARK_REFRAME_QUEUE.md` 中既有 `Rank 28b` 记录
- 原 rank clean replication 摘要：`research/optimization_loop/2026-03-17_0841_rank28-crossmarket-clean-replication.md`（由 reframe 文档引用）

## Decision
本轮 first verdict：`background / P0`。

## Why
- 当前这条“更快、更窄的 delayed catch-up”证据，指向的是 **lower-TF / same-underlier / cross-venue / session-handoff** 一类新的 raw-alpha 宿主，而不是仍可诚实归属于旧 `Rank 28 / cross-market intraday leader-laggard` 的单轴残差。
- `Rank 28` 原 park 的核心否决仍成立：15m direct leader-laggard follow 在 clean replication 中成本后为负，且没有证明可以靠同 family 的小改写恢复成 queue-facing intake。
- 既有 `Rank 28b` 已经占据旧 Rank 28 最诚实、最窄的 residual：`alt-vs-BTC RS breadth shared regime gate`。本轮 delayed catch-up 读法没有提供一个**独立于 Rank 28b**、且仍属于旧 Rank 28 family 的唯一宿主。
- 因此，把它写成新的正式 intake 会把“主题还活着”和“旧 Rank 28 residual 还能派生”混为一谈，属于越界派生。

## Runtime write-back
- `cycle_plan` item 2 标记为 `done`
- item 2 `result` 写回：`Rank 28` 的更快 `leader-laggard delayed catch-up` 读法已明显偏向新的 lower-TF / same-underlier raw-alpha family，未形成独立于既有 `Rank 28b` 的旧 family queue-facing residual，因此本轮 first verdict 收口为 `background / P0`。
- `Fresh intake slot` 前槽对象已处理完毕，前移到下一条仍待执行的具体 intake：`research/park_reframe/2026-04-07_2055_rank33-park-reframe.md`

## Reader-facing conclusion
`Rank 28` 不形成新的正式 intake；保留 park 语义，继续停在背景池，不新增 `Rank 28c`。
