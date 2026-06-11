# 2026-04-02 01:39 UTC · Rank 285 / 24h losers-vs-winners XS reversal × dispersion / turnover：P2 admission（effectiveness + cross-asset stability）

- 严格遵循：`docs/BOT2_BOT3_POLICY.md`
- 本轮只执行 `cycle_plan` 第 1 个 pending 小点
- admission 目标：只回答两件事——
  1. `effectiveness / expected return`：这条线在统一现实成本口径下，是否已经具备可重复的净收益结构；
  2. `cross-asset stability`：该结构是否能扩成广义 top-liquid perp 统一 alpha，还是只活在少数明确子口袋。

## 1. 本轮禁止重复的轴
上一轮 survivor 已经回答的是：`liquid perp` 里**存在 after-cost pocket**，因此这轮不能再把“pocket existence”重写一遍。

本轮要回答的是更强的问题：

> pocket 是否已经宽到足以支持 `promote_P3` 的 admission 级别，还是仍然只是需要继续收口的有限子口袋。

## 2. 采用的现有证据
本轮不引入新的 story，也不依赖 repo headline；只汇总已经落库的 perp clean-room 证据。

### A. mature liquid tail bucket：已有净正，但不是 broad-universe 普适
来源：`research/quant_digests/2026-03-25_0631_liquidity-split-tail-reversal-24h-loser-basket.md`

关键结果：
- 数据：Binance USDⓈ-M perpetual 公共 `15m` K 线，近 `90` 天
- bucket：
  - majors：`BTC/ETH/SOL/XRP/DOGE/BNB`
  - mature tail：`ADA/LINK/AVAX/TRX/LTC/BCH`
- signal：过去 `24h` 横截面收益排序
- 组合：`long bottom-third / short top-third`
- 成本：显式加入简化 `5 bps one-way per unit turnover`

最关键结果：
- mature tail bucket 的 `24h loser-basket reversal` 在 **`1h hold`** 下，平均**净收益约 `+0.942 bps / rebalance`，净 Sharpe 约 `1.758`**；
- 同一次实验里，majors momentum 对照腿在 `15m / 1h / 4h` 三档持有下都为负，例如 **`1h hold` 约 `-2.055 bps / rebalance`**。

这说明：
- `24h` XS reversal 的可交易部分，并不是“在所有高流动币上统一展开”；
- 当前最稳的净 pocket 更像是**成熟 tail、但仍具备现实流动性**的子篮子；
- 把 major names 与 mature tail 混成一个 broad signal 会掩盖结构差异。

### B. high-RV interaction shell：毛边更厚，但 break-even 仍靠更慢壳子
来源：`research/quant_digests/2026-03-25_1323_xs-interactions-highrv-loser-reversal.md`

关键结果：
- 数据：Binance USDⓈ-M perpetual 公共 `15m` K 线，近 `90` 天
- universe：`BTC/ETH/SOL/XRP/BNB/DOGE/ADA/LINK/AVAX/LTC/BCH/TRX`
- gate：先按 `24h realized vol` 分 bucket，只在高 RV bucket 内做 `long losers / short winners`

最关键结果：
- 高 RV bucket 内，**`1h hold、15m rebalance`** 的平均**毛收益约 `+2.31 bps / rebalance`**；
- 同一条腿在 **`4h hold、1h rebalance`** 下，平均**毛收益约 `+7.99 bps / rebalance`**；
- 文档已明确给出：这条腿的 **break-even 更接近 `~8 bps round-trip`**。

这说明：
- 这条 reversal 在高 RV 状态下确实更厚，不只是一次 tail-bucket 偶发现象；
- 但它依然明显依赖**更慢 rebalance / 更低 turnover 壳子**；
- 若直接把它读成 bar-by-bar taker alpha，会高估可交易性。

### C. broad fast-lane transfer 的失败边界仍然成立
来源：`research/quant_digests/2026-03-26_0449_repo-xs-reversal-cost-cliff-transfer-check.md`

关键结果：
- 当把更宽的短反转母体粗暴压到 `1h / 15m` fast-lane perp 壳子时，结果显著变差；
- `1h` 版本在 `8 bps` 下仍约 **Sharpe `-3.04` / total return `-15.4%`**；
- `15m` 版本更差。

虽然这份证据不是同一精确策略的 admission 主体，但它对本轮很重要：
- 它提醒我们不能因为看到单个 perp pocket 生存，就把整个 `24h XS reversal` 家族误写成广义 top-liquid 普适 alpha；
- 这条线的生存边界，当前仍然明显受 turnover / cadence / bucket choice 约束。

## 3. 对两条 admission 维度的直接判断

### 3.1 effectiveness / expected return
结论：**有效，但只在收窄后的现实子口袋里有效；尚未显示 broad-universe 级别的统一净收益结构。**

更具体地说：
- `mature tail` 口袋已经给出 **净正**（不是只看 gross）；
- `high-RV` 口袋给出更厚的 **gross edge**，但能否稳定跨过现实 round-trip 仍依赖更慢的换手壳；
- 因此这条线不能再被描述成“repo gross 很高但还没验证”，因为 **现实 perp shell 已经给出可保留的净边际**；
- 但也不能被描述成“统一 top-liquid perp 上已经形成 ready-to-paper 的 expected return profile”，因为当前净生存还没有跨 bucket / cadence 一致展开。

### 3.2 cross-asset stability
结论：**当前呈现的是条件化稳定，而不是 broad cross-asset 普适稳定。**

更准确的口径是：
- 该 alpha family 在**不同可交易子集**上并非同质；
- 成熟 tail 子桶可保留净正，高 RV 状态下 edge 更厚；
- 但 majors、broad fast-lane、无条件统一壳子下，并没有看到同等强度的可交易稳定性；
- 所以这条线当前更像：
  - `24h XS reversal` 是母体；
  - 真正可交易的是**被流动性层级 / realized-vol 状态 / 更慢 cadence 收窄后的 pocket**。

## 4. admission verdict（只针对第一半）
### 结论
**本轮把 `Rank 285` 记为 `keep_P2`。**

### 为什么不是 `promote_P3`
因为当前 admission 第一半已经给出一个很清楚的收口：
- 这条线不是“广义 top-liquid perp 统一净收益结构已成立”；
- 它目前仍更像**条件化 pocket family**，还需要第二半 admission 去回答：
  - 这是不是只靠最近 burst；
  - 参数 / cadence / bucket cut 是否过于敏感；
  - maker/mixed/taker 与换手压缩后是否还能留住现实净边际。

在这些问题补齐前，直接 `promote_P3` 会把“有条件生存”误写成“paper-ready”。

### 为什么不是 `drop_to_background`
因为本轮已经有足够强的反证说明它不该被一刀判死：
- `mature tail` 口袋是**净正**；
- `high-RV` 口袋给出更厚毛边；
- 因此它不只是 repo 叙事，而是已经有现实 perp shell 的 admission 级证据可继续收口。

## 5. 本轮改变的系统认知
一句话：

> `Rank 285` 的 admission 第一半已收口：`24h` XS reversal 在现实 perp shell 下并非 broad top-liquid 普适 alpha，但在 mature-tail 与 high-RV 条件化子口袋里已显示可重复净边际 / 厚毛边，因此当前应维持 `keep_P2`，并把第二半 admission 聚焦到时间稳定性、参数稳定性与执行诚实性，而不是再重复“有没有 pocket”。

## 6. 对下一小点的约束
下一轮（同对象的 admission 第二半）不得再重复：
- `有没有 perp pocket`
- `mature tail/high-RV 是否比 broad shell 更好`

下一轮必须直接回答：
1. `time stability`
2. `parameter stability`
3. `honesty / execution realism`
4. 以及是否已足够形成 `P3 / P1 / P0` 出口决策。

## 7. 一句话 result
`Rank 285` 的 P2 admission 第一半已明确：**现实 perp after-cost edge 只在成熟 tail / 高-RV 条件化子口袋里成立，尚不足以诚实外推成 broad top-liquid 普适结构，因此本轮记为 `keep_P2`，继续等待第二半出口决策。**
