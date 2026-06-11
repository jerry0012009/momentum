# 2026-04-09 15:22 UTC · Rank 16b fresh intake first verdict

## 本轮执行小点
- target: `research/park_reframe/2026-03-18_0629_rank16-park-reframe.md`
- action: 判断 `Rank 16b / fixed pseudo-open ORB -> active-hours session-range break/retest gate` 是否已足够从旧 ORB/protective-close park 中升成独立、queue-facing 的 active-hours structure pocket

## 读取证据
- `research/park_reframe/2026-03-18_0629_rank16-park-reframe.md`
- `research/optimization_loop/2026-03-17_0139_rank16-orb-protective-closing-intake.md`
- `research/optimization_loop/2026-03-17_0159_rank16-clean-replication-park.md`
- `research/quant_digests/2026-03-18_0549_session-range-active-hours-gate.md`

## 关键信号
1. 原始 `Rank 16` 被 park 的核心，不是 `session threshold + confirmation` 完全没边际，而是固定 `00:00 / 08:00 / 13:30 UTC` pseudo-open ORB 在 crypto 15m 上明显失真：`confirm1_outside` 虽比 `raw_orb` 少亏，但仍是跨资产全负、成本后持续塌。
2. `Rank 16b` 的唯一改写轴，实际上只是把这个失败的固定 pseudo-open 触发，替换成更通用的 `active-hours + session-range structure gate`。
3. 但这条改写并没有形成新的、专属于 `Rank 16` 的 queue-facing pocket；它本质上就是把原来过硬的 ORB 语义抽掉，回到更泛化的 `15m 信号先过 active-hours / session-range gate` 这一层。
4. 这层 gate 的来源证据本身也明确服务多条线：breakout-short、Fib retest_hold、EMA/PSAR continuation 都可以共享；因此它更像通用 overlay / family-level filter，而不是 `Rank 16` 独有的 alpha identity。
5. 本轮不需要额外 honesty 子检查，因为 decisive blocker 已经不是执行细节，而是对象身份本身：`Rank 16b` 并未保留足够独立的 ORB/session-threshold 语义，无法证明自己不是被既有 session-pocket / active-hours / breakout-structure family 直接吸收。

## First verdict
- verdict: `background / P0`
- object_read: `absorbed by existing session-range / active-hours overlay family`

## 为什么不是 keep_P1
- 若把 `fixed pseudo-open ORB` 拿掉后，剩下的只是“活跃时段里的 session high/low break + retest/continuation”，那它已经不再是原 `Rank 16` 的窄派生口袋，而是现有 session-structure gating 家族的通用表达。
- 当前证据没有给出一个只属于 `Rank 16b` 的独特可验证边界，例如：
  - 明确优于通用 active-hours gate 的 ORB-specific 事件定义；
  - 不依赖 generic session structure family 也能成立的独立 execution identity；
  - 或一个唯一 decisive honesty blocker 被解除后就能升格的剩余差异。
- 因此最诚实的收口不是把它再送去 P1，而是承认它已被已有 family 吸收，停止为旧 ORB park 造一个看似新、实则泛化的入口。

## 对 runtime 的影响
- `Fresh intake slot` 本轮 first verdict 收口为：`Rank 16b` 不升 `keep_P1`，直接 `background / P0`。
- `cycle_plan` 第 1 项完成并写成 `done`；后续是否继续执行第 2 项，留待下一轮按顺序处理。

## 一句话结论
`Rank 16b` 并没有把旧 ORB park 压成独立 pocket，而只是把失败的 pseudo-open ORB 抽象成现有 session-range / active-hours 通用 gate，所以本轮 first verdict 直接收口为 `background / P0`。
