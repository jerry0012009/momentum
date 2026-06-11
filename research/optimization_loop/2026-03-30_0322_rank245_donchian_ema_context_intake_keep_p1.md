# Rank 245 / Donchian breakout × EMA HTF context gate intake keep P1

- Time: 2026-03-30 03:22 UTC
- Target: `Rank 25 park residual -> Donchian-only breakout with EMA demoted to HTF context gate`
- Action: fresh intake first verdict
- Verdict: `keep_P1`
- Rank: `245`

## What changed
这次留下来的不再是原 `EMA + Donchian` 双触发 breakout，而是一条**职责重新分层后的窄对象**：

> **只让 Donchian breakout 负责真正触发；EMA 只做更高时间框架的顺风背景 gate。**

这和原 `Rank 25` 不是同一个对象。原线失败的关键，不是 breakout 主题本身彻底失效，而是把 `EMA` 和 `Donchian breakout` 放成同层 co-trigger 后，时间结构只剩中段 bucket 亮、前后 bucket 反复塌。现在的新对象把问题直接改写成“trigger 与 context 是否该分岗”，因此它是一个合法的新 fresh intake，而不是旧 `Rank 25` 的自动 reopen。

## Why it is distinct enough
1. **主触发已经单独锁死**：entry 主语不再是 `EMA+Donchian` 联合确认，而是 `Donchian breakout confirmed-close / next-bar open`；EMA 不再有独立按扳机地位。
2. **与 `Rank 25b` 不同**：`25b` 解决的是外层 `30m regime matrix allow/deny`；本轮对象解决的是 `EMA` 角色错位，问的是“EMA 该不该退居 HTF context gate”。
3. **边界足够窄，且可单轮证伪**：第一轮完全可以只做 `baseline Donchian breakout` 对 `breakout + EMA HTF context gate` 的 honest A/B，不必偷带 ATR strength、新 exit、position sizing、regime matrix 第二轴。
4. **不只是原对象实现收缩**：这不是把原线参数稍微缩窄，而是把原策略里最可疑的职责层重新拆开；如果这条拆岗后仍无法修复时间结构，那就能快速证明“剩下的问题不在 EMA 岗位”，直接收口。

## Why it is not P2 yet
1. 当前还只有 `park_reframe` 级别的 spec-quality evidence，没有任何本地最小 A/B artifact 去证明 `Donchian-only trigger + EMA HTF gate` 在成本后能比 baseline breakout 留下更诚实的时间结构。
2. 这条线最关键的问题正是它能否修复原 `Rank 25` 的 `bucket_1 负 / bucket_2 正 / bucket_3 负` 时间塌陷；在没先做这个单轴验证前，直接升 `P2` 仍然太早。
3. 如果一上来就把 regime / strength / exits 一起塞进来，会把“EMA 角色改写”这条单轴问题重新污染成多轴拼装，不符合当前 policy 的 intake 口径。

## Why it still deserves keep_P1
1. **新对象的主语够清楚**：`Donchian breakout remains sole trigger, EMA only serves HTF context gate`，不是泛 trend family，也不是更大的 regime matrix。
2. **它直击原对象唯一 decisive blocker**：原 `Rank 25` 的致命点是时间不稳，而不是成本、跨资产、参数同时爆雷；因此先检查“EMA 是否放错岗位”是诚实且低成本的一刀。
3. **下一步 cheap decisive follow-up 非常明确**：只需做同一数据、同一 breakout 口径下的 `baseline breakout` vs `breakout + EMA context-only gate`，直接看 after-cost aggregate 与三桶时间结构是否同步改善。

## Minimal honest next follow-up
若进入 survivor，唯一一次 cheap decisive follow-up 应只做：
- 固定原 `Donchian breakout confirmed-close / next-bar open` 触发框架；
- 并排比较 `baseline breakout` 与 `breakout + HTF EMA context-only gate`；
- gate 只允许最简单的 `EMA rising / fast>slow 同向` 一类闭合-bar HTF 条件；
- 统一使用原成本假设与同样的时间分桶口径；
- 直接回答：**EMA 从 co-trigger 降级为 HTF context gate 后，是否能在不靠额外第二轴装饰的前提下，留下比 baseline 更诚实的时间结构与成本后 pocket。**

若答案是否定的，这条线应在 survivor 后直接回 `background/P0`；若答案肯定，再决定是否值得升 `P2`。

## Runtime implication
- 正式分配 `Rank 245`。
- 层级定性为 `P1`，不直接升 `P2`。
- 当前 `Surviving candidate slot` 为空，因此这条 fresh intake 应占据唯一合法 survivor 槽位，并恢复 **1 次** 最小 decisive follow-up 预算。

## Result sentence
`Rank 245 / Donchian breakout × EMA HTF context gate` fresh intake 完成并保留为 `keep_P1`：它不是旧 `Rank 25` 的自动 reopen，而是把失败根因收敛到“EMA 不应与 Donchian breakout 同层共触发”的单轴角色改写；但在本地还没有 baseline breakout vs EMA-context gate 的最小诚实 A/B 前，仍不足以直接升 `P2`.
