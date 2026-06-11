# Rank 265 / same-venue delta-neutral carry × premium-z admission × current+next funding > close-cost — fresh intake keep_P1

- 时间：2026-03-31 01:13 UTC
- 执行身份：bot3 自动执行器
- 本轮执行小点：`cycle_plan #2` / Fresh intake slot
- 来源底稿：`research/quant_digests/2026-03-30_2344_current-next-funding-closecost-carry-alpha.md`
- Assigned Rank: `265`

## 1. 本轮为什么轮到它
当前 runtime 已把 `Rank 264` 的 survivor 唯一 follow-up 收口回 `background/P0`，`Fresh intake slot` 回到 `ready_for_new_intake`。按照当前 `cycle_plan`，排在最前的合法 pending 小点就是把 `current+next funding close-cost carry` 做 fresh intake 首判；本轮只执行这一项，不改排班。

## 2. 主语锁定
这条对象的主语必须锁定为：

> **same-venue delta-neutral spot-perp carry**，并且不是“funding 为正就收租”的朴素版本，而是 `vol-adjusted selection -> premium-z admission -> current+next funding > close-cost hurdle` 的完整 raw alpha skeleton。

它和 `Rank 235` 的 cross-venue routing carry 不是一回事：
- `Rank 235` 的核心问题是跨 venue 轮换、ex-post best funding、basis drift 与换腿成本；
- 本对象的核心问题是 **同 venue** 的现货-永续 carry 什么时候值得开、值得继续扛、以及 funding 现金流是否真的覆盖未来关仓成本。

所以它构成独立主语，不该被并回 generic funding/basis 面板，也不该与 `Rank 235` 混写。

## 3. 本轮 first verdict 依据
底稿里已经给出了足够形成 fresh intake verdict 的三层证据：

1. **源码不是脚手架，而是完整策略骨架。**
   repo 把 same-venue carry 写成了：
   - 候选排序：`funding / sqrt(ATR)` 这类 vol-adjusted ranking；
   - 开仓门槛：`premium z-score` 而不是“premium > 0”；
   - 持仓治理：`current + next funding > close-cost hurdle`，不够就主动平。

2. **对象有独立的 entry / hold / exit / cost 语义。**
   这不是单个 filter 或 basis 监控面板，而是完整策略闭环：
   - 先问 perp 是否已经明显 rich；
   - 再问未来 funding 现金流是否足以覆盖未来 close-cost；
   - 持仓中继续用同一条 hurdle 判断是否还值得拿。

3. **当前 live sanity check 同时证明“正 funding ≠ 值得做”。**
   底稿给出的 OKX majors 快照里：
   - ETH：`current+next funding ≈ +0.68 bps` vs `close-cost hurdle ≈ 11.16 bps`
   - BTC：`≈ +0.19 bps` vs `≈ 11.42 bps`
   - SOL：`≈ -0.59 bps` vs `≈ 12.96 bps`

翻成人话就是：

> 这条 alpha 的骨架是成立的，但当前主流币 live 状态离“真钱值得开/继续持有”还差一个数量级。

## 4. 为什么不是 background/P0
不该直接打回 background，原因是：

1. **独立主语已经够清楚。**
   `premium-z admission × current+next funding > close-cost` 已经把 same-venue carry 从泛 funding 叙事里拆成可审计策略。

2. **底稿不是空泛观点，而是源码级闭环。**
   这里不是只说“funding 应该结合 premium 看”，而是已经把 if/else 写到了 repo 里，具备继续做 honest follow-up 的价值。

3. **当前快照虽然偏弱，但反而验证了 hurdle 设计的重要性。**
   如果没有这两层门槛，这条线会把大量“funding 为正但根本不够覆盖 close-cost”的时点误判成机会。

## 5. 为什么还不能升 P2
当前还不该直接 `promote_P2`，因为本轮只够回答“这是不是独立 raw alpha”，还没回答“它在诚实 execution 下有没有真钱 pocket”。

决定性缺口主要有三条：

1. **活口径尚未锁定。**
   当前 majors snapshot 明确偏弱，下一步必须回答：这条线到底只在 maker/taker、rebate、或更窄 alt pocket 下才成立，还是在主流币上也能稳定跨过 hurdle。

2. **close-cost 仍是 proxy，不是成交级 reality。**
   底稿已用手续费 + premium band 做了诚实方向的 hurdle，但还没把真实盘口深度、切片、maker/taker 组合与 rebalance slippage 一次性锁死。

3. **对象更像“slow alpha + fast execution”，不是直接逐 bar alpha。**
   funding 是慢变量，是否能做成短周期 desk 上可执行的 pocket，还要看 `1m/3m` execution veto 之后还剩多少净边。

## 6. 本轮 verdict
本轮将该对象正式分配为 **`Rank 265`**，verdict = **`keep_P1`**。

一句话写法：

> `Rank 265：fresh intake 首判完成；same-venue spot-perp carry 已被收口成「vol-adjusted selection -> premium-z admission -> current+next funding > close-cost hurdle」的独立 raw alpha skeleton，但当前 OKX majors live snapshot 下 funding 现金流远小于 close-cost hurdle，所以本轮只记 keep_P1，并把唯一 survivor follow-up 锁定为更诚实的 pocket-existence / execution-honesty 检查。`

## 7. 唯一合法 survivor follow-up 方向
如果后续进入 survivor follow-up，唯一高杠杆动作应是：

- 固定在 `same-venue spot-perp carry` 主语，不准漂移成 generic funding 面板；
- 分 `BTC/ETH/SOL` 与少数高 funding alt pocket；
- 明确比较 `taker/taker`、`maker/taker`、`maker/maker or rebate-assisted` 三种 execution 口径；
- 用成交级或至少盘口深度代理回答：
  - `premium-z` 门槛是否真的提升单笔质量；
  - `current+next funding > close-cost hurdle` 是否明显减少伪机会；
  - 这条线是否只在窄 pocket 下可活。

这一步应该一次性收口成：`promote_P2` / `background/P0`，而不是继续开放式补 compare。

## 8. Runtime writeback
- 新正式 Rank：`265`
- `Fresh intake slot`：更新为 `Rank 265 / same-venue delta-neutral carry × premium-z admission × current+next funding > close-cost`
- `Surviving candidate slot`：切换到同一对象，`followup_budget_remaining: 1`
- `cycle_plan #2`：标记为 `done`
