# 2026-03-29 16:30 UTC — Rank 240 / stablecoin depeg jump-risk shared overlay 首判（keep_P1）

- 时间：2026-03-29 16:30 UTC
- 对象：`research/quant_digests/2026-03-29_1458_usdt-depeg-jump-risk-shared-overlay.md`
- 结论：**keep_P1，不升 P2**
- 正式 Rank：**240**

## 这轮只回答一个问题
这条 `stablecoin depeg jump-risk shared overlay`，是否足够独立到值得转成新的 queue-facing 对象？

回答：**值得。** 但它值得保留的不是“stablecoin 风险很重要”这种宏观解释，而是一个边界清楚、可复现、服务多类短周期 raw alpha 的共享风险层：

> **`downward USDT depeg -> future 30m/60m jump-risk + cojump-risk 显著抬升 -> MR / pairs / carry 做 veto/size-down，breakout/event 单做 admission tightening + size-down`**

## 为什么值得首判保留
1. **主语已经足够独立，不是泛泛稳定币叙事。**
   这条线真正交易化的核心不是“USDT 有新闻”，而是一个可操作的异常状态定义：`USDT` 明确脱锚，尤其是 **downward depeg** 后，未来 `5m~60m` 的单币 jump 与全市场 cojump 风险显著上升。这个主语和 FOMC、VPIN、crowding、Fear & Greed 这些既有 overlay 不同，它回答的是 **stablecoin plumbing shock 何时会系统性打坏正常 bar-based 执行假设**。
2. **第一轮实验边界是清楚的，能做单轮证伪。**
   digest 已给出足够具体的最小骨架：
   - 事件定义：`0.3% / 0.5% / 1.0%` depeg threshold
   - 事件方向：`all` vs `downward-only`
   - overlay 窗口：`15m / 30m / 60m`
   - 动作：`MR/pairs veto`、`carry size-down`、`breakout 同向单 admission tightening`
   这已经不是“以后再想怎么测”，而是能直接挂到现有短周期策略回放里的 queue-facing shared overlay。
3. **它服务多个现有 raw alpha 家族，而不是单一补丁。**
   这层 shared risk layer 同时对 `mean reversion / pairs / funding-carry / breakout/event` 有清楚的接法，而且论文证据指向的是 jump-risk / cojump-risk 这个共享破坏机制，而不是某一条策略自己的私有细节。

## 为什么这轮不直接升 P2
1. **当前证明的是“异常 regime 存在”，还不是“overlay 接入后净效果已被 admission”。**
   现在最强证据是 depeg 事件会把市场推入高 jump-risk / cojump-risk 状态；但还没有 `with overlay vs without overlay` 的真实策略级 A/B，不能直接把它写成已过 admission 的对象。
2. **shared overlay 家族里最容易犯的错，就是靠砍交易数伪装成改进。**
   它下一轮必须直接回答：接到现有 `MR/pairs/carry/breakout` 其中至少一类策略后，改善的是 `tail loss / drawdown / adverse excursion / slippage proxy` 中的哪一项；若只是靠大面积 veto 把交易都砍掉，就不配升 P2。

## 与既有 overlay 家族的关系
- **不是 `Rank 175 / FOMC event-clock overlay` 的换壳。** `Rank 175` 是预先已知的宏观日历事件；`Rank 240` 是由 stablecoin plumbing shock 触发的分钟级 stress flag。
- **不是 `VPIN jump-risk` 的重复。** VPIN 解释的是订单流毒性；这里的主语是 stablecoin 脱锚造成的跨市场 jump/cojump 风险抬升。
- **也不是 crowding / sentiment / spread-zscore 这类慢变量 regime gate。** 它更像一个短窗、事件驱动、直接服务执行与仓位控制的 shared stress overlay。

## 本轮改变的系统认知
**`downward USDT depeg -> 30m/60m jump-risk / cojump-risk size-down + veto` 足够独立成 `Rank 240 / stablecoin depeg jump-risk shared overlay`：它用明确 depeg 事件窗回答“何时现有短周期 alpha 该缩仓或禁做”，与现有 FOMC/VPIN/crowding overlay 家族不重复，因此首判为 `keep_P1`。**

## Runtime 落点
- `Fresh intake slot`：本轮首判完成，切换为 `Rank 240 / stablecoin depeg jump-risk shared overlay`
- `Surviving candidate slot`：切换为 `Rank 240 / stablecoin depeg jump-risk shared overlay`
- `followup_budget_remaining`：`1`
- 本轮未创建 `Active P2`，也未触发 `P2 -> P3`
