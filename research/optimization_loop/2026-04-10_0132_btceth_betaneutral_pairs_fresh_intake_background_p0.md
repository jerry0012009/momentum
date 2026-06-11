# bot3 自动优化日志：BTC/ETH beta-neutral cost-aware pairs fresh intake 收口为 background / P0

- Time: 2026-04-10 01:32 UTC
- Slot: Fresh intake
- Target: `research/quant_digests/2026-04-09_2254_btceth-betaneutral-costaware-pairs-shell.md`
- Focus: 判断 `spread fade × beta-neutral sizing / funding-aware cost shell` 是否已经形成值得前排化的新独立 pairs alpha 主语，还是只是旧 `pairs / stat-arb / spread mean reversion` 家族上的 sizing / 记账壳升级。

## 本轮执行
1. 重读 fixed policy 与 runtime state，确认当前最前的合法 `pending` 小点就是这条 fresh intake，且本轮只能执行这一条。
2. 重读 source digest，核对其 strongest claim：
   - 基础 alpha 仍是 `BTC/ETH cointegrated spread mean reversion`；
   - 所谓新增价值主要是 `dollar-neutral -> beta-neutral` 的 sizing A/B，以及把 `fee + slippage + funding` 并入净收益；
   - digest 自己也把 repo 定位成 **signal 本体 vs sizing/cost/funding 壳** 的拆解，而不是新 spread 主体。
3. 交叉检查当前 workspace 里的既有 runtime truth，确认这类 pairs 家族并不是空白：
   - 已有 `Rank 322` 明确把 `major-pair 15m spread z-score mean reversion` 推到过 `P2`；
   - 已有 `Rank 365` 被保留为 `benchmark-beta return differential × pair fade`，它的可独立主语是“先对 market beta 去残差，再做 pair fade”；
   - 另有多条 `pairs / stat-arb / spread MR + admission / cost governance` 已被作为旧家族处理。
4. 对比这次对象和旧家族的差异是否足以构成新的 fresh intake：
   - 这次并没有提出新的 spread 定义、pair admission、regime router 或新的可迁移 lane；
   - 新增层几乎全部集中在 **仓位映射与记账口径**：`rolling beta hedge ratio`、`beta-neutral notional mapping`、`funding-aware net PnL`；
   - 这类内容更像已有 pairs alpha 的 **execution/sizing shell upgrade**，不是独立 raw alpha 主语。
5. 诚实性与执行现实层面的收口：
   - digest 给出的最强数字仍来自同一 repo 对 `BTC/ETH 1h` 回测的 A/B 摘要（`dollar-neutral -791.6 USD` vs `beta-neutral +67.0 USD`）；
   - 但它没有给出在统一 `15m/5m` crypto desk 宿主下、相对已有 pairs baseline 的最小 clean-room after-cost 增量；
   - 也没有证明该增量可迁移到 `BTC/ETH` 之外，或能把旧 pairs 家族里已经出现的 surviving lane 实质性改判为更强对象。
6. 因此本对象的 blocker 不是某个还能靠一次 survivor follow-up 补上的单点漏洞，而是：
   - **它的“新增内容”本质上是旧 pairs 家族上的 sizing / funding-aware accounting 升级件；**
   - 当前证据不足以把它单独提升成新的前排对象。

## 结论
`BTC/ETH beta-neutral sizing / funding-aware cost shell` 不构成新的独立 fresh intake 主语：它本质上仍依附于已知 `pairs / stat-arb / spread mean reversion` 家族，新增部分主要是 `beta-neutral sizing + funding-aware accounting` 的 execution 壳，而不是新的可迁移 spread alpha；当前公开证据也不足以证明它在统一 short-cycle 宿主下，能相对已有 pairs baseline 产生独立、稳健、after-cost 的新增 pocket，因此本轮 fresh intake 直接收口为 `background / P0`，不分配新 Rank。

## Result sentence
`BTC/ETH beta-neutral sizing / funding-aware cost shell` 仍属于已知 `pairs / stat-arb / spread mean reversion` 家族上的 sizing/记账升级件，新增证据不足以证明独立可迁移的 after-cost alpha pocket，因此 fresh intake first verdict 直接收口为 `background / P0`，不分配新 Rank.
