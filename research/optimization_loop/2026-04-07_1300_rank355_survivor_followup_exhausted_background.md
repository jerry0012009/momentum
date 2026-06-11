# Rank 355 · survivor follow-up exit decision · keep_P1 follow-up exhausted -> background

- Time: 2026-04-07 13:00 UTC
- Target: `Rank 355 / Polymarket adjacent-horizon YES-price spread × Kalman-OU reversion`
- Action: use the one allowed survivor follow-up to answer the single decisive question
- Verdict: `keep_P1 but follow-up exhausted -> background`

## 本轮只回答的 decisive question
在 **最流动 recurring crypto markets 的 adjacent-horizon pair** 上，若诚实计入 `fee / slippage / stale-quote / expiry jump`，这条 Polymarket term-structure relative-value 线是否已经有足够公开证据证明存在 **可迁移的 post-cost pocket**，从而值得升到 `P2`？

## 本轮证据
1. intake 已确认：这不是旧 `Polymarket lag / late-entry continuation` 的换壳，而是 prediction-market 内部的 **adjacent-horizon term-structure spread mean reversion**，raw alpha 主语独立，这一点本轮不推翻。
2. 公开 repo `polymarket-pairs` 暴露的核心仍主要是 **dashboard + bundled SQLite snapshot + live monitor 壳**：
   - `pair_state` 暴露 `last_z / last_hr / ou_kappa / ou_halflife / is_cointegrated / coint_pval / kelly_fraction / position_size_usd`
   - `trades` 暴露 `entry_z / exit_z / hours_held / pnl_usd / net_pnl_per_share`
   - 但公开可见部分仍不足以把 **最流动 recurring crypto pairs 的 after-cost pocket** 压成可审计结论。
3. repo 里明确存在 Polymarket fee 参数表，且 Polymarket 官方交易文档也确认真实执行需要 CLOB 下单、签名与交易认证；这意味着这条线的 edge 不能只靠 mid/mark 幻觉成立，必须穿透到真实 fee / fill / depth 口径。
4. 当前公开材料没有给出足够 reader-auditable 的：
   - recurring crypto adjacent-horizon pair 列表与筛选结果；
   - per-pair / per-trade post-fee、post-slippage 分层；
   - stale quote / 临近 expiry jump 被剔除后剩余 edge；
   - 证明主要利润并非来自临近结算或假流动时段的 clean cut。
5. 因而，本轮唯一应收口的 blocker 仍没有被解除：**这条线有独立 alpha 主语和最小执行壳，但尚无足够公开证据证明诚实成本后的 pocket 真实存在。**

## 为什么这次不升 P2
`P2` 要求的不是“有 Kalman/OU 壳”或“有 dashboard/trade 表”，而是至少能进入更严肃 admission 的可信 pocket 线索。Rank 355 目前还停在“策略形状成立，但 pocket 证据不够硬”的状态。

如果继续把它留在 survivor/front slot，本质上会变成继续围绕同一 blocker 做开放式追问；这违反 policy 对 survivor 只允许 **1 次 cheapest decisive follow-up** 的约束。

## 为什么也不直接打成 P0 fatal flaw
本轮没有发现致命反证去证明这条线一定不成立；问题在于 **证据强度不够推进前排**，而不是已经被证伪。因此更诚实的收口不是 `background / P0`，而是：

> `keep_P1 but follow-up exhausted -> background`

也就是：保留为一个有独立主语、值得未来人工 reopen 的候选，但自动运行不再继续占用前排资源。

## 本轮写回 runtime 的系统认知
- `Rank 355` 的唯一 survivor follow-up 已用完；
- 结论不是 `promote_P2`；
- 由于缺少可审计的 `post-cost pocket` 证据，它退出 `Surviving candidate slot`，移入 `Background pool`；
- 当前前排不再由该对象占用，后续应回到 bot2 已排好的下一条 fresh intake。