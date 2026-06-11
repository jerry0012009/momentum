# Rank 287 — survivor follow-up 收口：回 background/P0（post-cost binary fee shell 不过关）

- 时间：2026-04-02 03:26 UTC
- 对象：`Rank 287 / Binance impulse × Polymarket 15m lagged binary mispricing`
- 执行动作：`survivor` 的唯一一次诚实 follow-up
- 层级动作：`follow-up exhausted -> background/P0`
- 结论一句话：`Rank 287` 目前仍只有“Binance 快腿先动、Polymarket 慢腿滞后”的 raw alpha skeleton，但没有任何独立 clean-room one-lag post-cost 证据证明该 edge 在 Polymarket crypto binary 的 taker fee + spread + quote staleness + near-expiry legging 风险之后仍留下可执行净 pocket；因此 survivor 预算在本轮用尽，直接回 `background/P0`，不升 `P2`。

## 本轮到底回答了什么
本轮不是再复述 repo 的 paper 结果，而是直接问 survivor 应该回答的那条生死线：

**如果不用 repo 自报 PPO 结果，只保留公开可拿数据与 one-lag honest baseline，`p_fair_up - p_mid_up` 在 Polymarket 真实成本壳之后，还剩不剩足够厚的净 pocket？**

当前答案是：**没有足够证据支持“剩得够厚”。**

## 关键证据
### 1) repo 自己已明确承认 live 会显著劣化，且当前只做到 paper trading
从 README 可直接读到：
- `Current status: Paper trading only`
- `Paper trading assumes instant fills at mid-price`
- `Expect 20-50% performance degradation`
- 真正落地仍缺 execution layer、slippage modeling、latency compensation、extended validation

这意味着 repo 最亮眼的收益数字并不能直接回答我们关心的问题：
**独立 one-lag baseline 在真实执行壳里是否还能赚钱。**

### 2) Polymarket crypto taker fee 本身就不轻，50¢ 附近单边费用约占 trade value 3.6%
Polymarket 官方 fee 文档给出的 crypto taker fee：
- fee 公式：`fee = C × feeRate × p × (1-p)`
- crypto fee rate：`0.072`
- 100 shares、50¢ 价格时，单边 taker fee = `$1.80`，对应 `$50` trade value，也就是 **3.6% 单边**
- 40¢/60¢ 时，单边 taker fee 也仍约为 `$1.73 / $40` 或 `$1.73 / $60`

翻成人话：
**这不是一个“只要有一点 lag 就够吃”的便宜市场。**
如果 baseline edge 不是明显厚于几个百分点，再加上 spread 与 stale quote，paper edge 很容易被全部吃光。

### 3) repo 的卖点主要还是“可能存在 seconds-level lag”，但本轮没有拿到任何 clean-room monotonic edge / decile / post-cost 曲线
目前可确认的只有：
- 快腿是 Binance futures
- 慢腿是 Polymarket 15m binary
- 两边公开数据能拿
- repo 把状态空间、交易时钟与候选特征写得很清楚

但 survivor follow-up 该要求的不是这些，而是至少一种独立证据，例如：
- `edge decile -> realized convergence` 单调性
- `one-lag fair value minus mid` 在扣掉 taker fee + spread 后仍为正的分桶结果
- `>10m / 5~10m / <5m` 到期时间分桶后，净边只在可执行窗口内存活
- 与“直接做 Binance continuation”对照后，确认真正增益来自 slow-market lag 而不是 Binance 自身方向性

这些关键证据，本轮都没有独立拿到。

### 4) binary market 的已知 hard-expiry / quote staleness / legging 风险，使“没有 clean-room post-cost 图”本身就是决定性缺口
这里的坏处不是“还差一点点精修”，而是：
- 15m 到期结构把 near-expiry slippage / 未成交 / 强制平仓问题放大
- Polymarket 为 CLOB，真实交易需要签名、认证、下单与成交处理，不是纯看 mid 就结束
- repo 已承认 live 还没有 execution layer

所以当前缺口不是温和的“再补些稳定性”；而是**尚未跨过最基本的 post-cost honesty 线**。

## 为什么本轮不升 P2
P2 admission 的默认门槛是：对象至少应表现出“已经比较像一个能继续成型、值得进入 paper trade / paper launch 的东西”。

`Rank 287` 现在还没有达到这个状态，因为：
1. 有 skeleton，但还没有独立净 pocket 证据；
2. 市场成本壳对这类 15m binary 很重，不是轻微修正；
3. repo 自报结果又高度依赖 paper / mid-fill / 未实盘执行。

因此最诚实的收口不是 `keep_P1`，更不是 `promote_P2`，而是：
**survivor follow-up exhausted，退回 background/P0。**

## 本轮 verdict
- verdict: `follow-up exhausted -> background/P0`
- 不升 `P2`
- 不保留新的 survivor 预算

## 对 runtime 的直接影响
- `Surviving candidate slot`：清空为 `none`
- `Background pool`：新增 `Rank 287` 停放记录
- `cycle_plan` 第 1 项：标记 `done`

## 参考来源
- Repo README：<https://raw.githubusercontent.com/humanplane/cross-market-state-fusion/master/README.md>
- Repo training journal：<https://raw.githubusercontent.com/humanplane/cross-market-state-fusion/master/TRAINING_JOURNAL.md>
- Polymarket fees：<https://docs.polymarket.com/trading/fees>
