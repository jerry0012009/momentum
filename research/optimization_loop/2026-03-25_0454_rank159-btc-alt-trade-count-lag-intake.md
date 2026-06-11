# Rank 159 intake — BTC→ALT `1m` trade-count 分层滞后跟随

- 时间：2026-03-25 04:54 UTC
- 轮次角色：bot3 fresh intake 执行
- 对象：`Rank 159 / BTC→ALT trade-count-sorted 1m lag follower`
- 来源：`research/quant_digests/2026-03-25_0349_liquidity-sorted-btc-alt-1m-lag-alpha.md`
- 本轮动作：fresh intake 首判（`park / keep_P1`）

## 最小公开证据
- 公开论文给出的核心 claim 不是泛泛的 “BTC 带 alt”，而是 **低 trade-count follower 对 BTC `1m` 冲击吸收更慢**，且 edge 更集中在低流动性分组，而非所有主流币平均有效。
- 证据不只停在解释层：论文直接给出带 fee 的 lag strategy skeleton，说明这不是纯机制观察，而是可落到 entry/hold 的候选 alpha。
- 数据口径可复刻：Binance `1m kline` 自带 `number of trades`，因此 `leader return + follower liquidity bucket` 这条最小 clean-room 假设可以不依赖私有源先做本地验证。

## 本地快检口径
1. **可独立复现性：通过。** 所需最小输入就是 `BTCUSDT` 与一组 ALT `1m` bar + `number of trades`，不依赖不可获得字段。
2. **工程上不是旧题原样重复。** 它和最近 desk 已提过的 `BTC 5m shock -> alt basket` 有清晰区分：这里的 alpha 单元是 `trade-count-sorted follower selection + 1m lag follow-through`，asset selection 本身就是 alpha，而不是先有大冲击再混打篮子。
3. **当前最诚实的风险判断：** 论文最强样本偏向小币，真实 taker/冲击成本可能显著抹掉收益；但这恰好能被一次 survivor follow-up 明确回答——只要把样本收紧到 desk 可接受的 perp universe，并检查 edge 是否仍集中在低 trade-count 分组。

## 首判
**结论：`keep_P1`。**

原因不是它已经足够进入 `P2`，而是它满足了 `P1` 应有的三个门槛：
- 有明确且可复刻的 raw alpha 假设；
- 有与现有家族不同的 decisive angle（`trade-count follower ranking` 而非泛篮子事件）；
- 下一步存在单一、便宜且诚实的 blocker 检查：**在 desk 可交易的 perp universe 内，这个 edge 是否仍主要集中在低 trade-count follower，且在保守成本下仍保留正的 `post-cost avg return / trade`。**

## 进入 survivor 的唯一 follow-up 应该是什么
若 bot2 下一轮将其写入 survivor，则唯一合法 follow-up 应收口为：
- 用 desk 可交易的 `20~40` 个 Binance USDT perp，按 recent median trade count 分 bucket；
- 先做最朴素规则版 `BTC 1m impulse -> ALT next 1~3 bar follow`；
- 只回答一个 decisive blocker：**edge 是否仍集中在低 trade-count 分组，并在保守 round-trip 成本下为正。**

## runtime 变化
- 分配新正式 `Rank 159`
- fresh intake 首判：`keep_P1`
- 尚未在本轮直接改写 survivor / P2；等待后续小点按 policy 执行

## 一句话结果
`Rank 159 / BTC→ALT trade-count-sorted 1m lag follower` 具备可复刻公开证据、与现有 `BTC shock->ALT basket` 明确区分，且只剩一个可低成本收口的真实性 blocker，因此 fresh intake 首判为 `keep_P1`。
