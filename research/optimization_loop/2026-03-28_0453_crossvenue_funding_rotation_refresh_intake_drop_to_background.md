# cross-venue funding rotation refresh intake verdict — drop_to_background

- Time: 2026-03-28 04:53 UTC
- Target: `research/quant_digests/2026-03-28_0334_crossvenue-funding-rotation-refresh-alpha.md`
- Action: 对这条 `cross-venue funding rotation refresh` 做 fresh intake；回答它留下来的是否是独立的 cross-venue funding rotation raw alpha，而不是旧 funding carry 家族的换皮 refresh
- Verdict: `drop_to_background`

## 结论
这条对象不该进入前排，也不该拿新 Rank。repo 真正提供的增量是把跨 venue funding carry 写成了更完整的执行骨架：`APR gate × spread veto × forced refresh × rollback`。但这更像 **已有 carry 家族的 honest scheduler / execution wrapper**，不是一条已经独立到值得单列 front-slot 的新 raw alpha identity。

## 为什么这轮直接收口
1. digest 自己的核心定义仍是：`long 低 funding venue + short 高 funding venue` 的 delta-neutral carry；
2. 新增部分主要是 `net APR >= 5%`、`spread <= 0.15%`、`hold 8h/12h`、partial-fill rollback、funding clock refresh 这些执行与治理门槛；
3. 这些门槛当然重要，但它们本质上是在回答“**怎么别把旧 carry 做得太假**”，不是在给 desk 一个新的 alpha sign；
4. 项目里已经有多条 funding/carry 相关对象（如 `Rank 168` 的 venue-tier-duration gate、`Rank 184` 的 cross-venue contango carry、以及刚被收口到 background 的 `positive funding × positive premium` honest gate）。和这些对象相比，这条 `rotation refresh` 没有给出新的定价错位来源，只是把 carry 的开机关机与持仓刷新写得更完整。

## 系统认知变化
- 应保留的事实不是“发现了一条新的 cross-venue funding rotation alpha”；
- 而是：**cross-venue funding carry 若要诚实 desk 化，至少应显式带上 `APR gate + spread veto + forced refresh + rollback` 这一整套 execution hygiene。**
- 这条材料适合作为 carry 家族的实现参考 / shared execution overlay，而不是当前轮 front-slot 的独立候选。

## Rank / 层级处理
- 本轮结论是 `drop_to_background`，因此 **不分配新 Rank**。
- 不进入 `Surviving candidate slot`，也不升 `P2`。

## Runtime writeback sentence
`cross-venue funding rotation refresh` intake 已收口：这份 repo 提供的是跨 venue funding carry 的更诚实调度/执行骨架（`APR gate × spread veto × forced refresh × rollback`），但没有形成独立于既有 carry 家族的新 alpha identity，因此本轮直接 `drop_to_background`，不分配 Rank。
