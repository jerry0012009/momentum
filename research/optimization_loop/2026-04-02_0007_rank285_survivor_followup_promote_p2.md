# 2026-04-02 00:07 UTC · Rank 285 / 24h losers-vs-winners XS reversal × dispersion / turnover：survivor decisive follow-up

- 严格遵循：`docs/BOT2_BOT3_POLICY.md`
- 本轮只执行 `cycle_plan` 第 1 个 pending 小点
- 目标：只回答一个问题——这条 `24h losers-vs-winners XS reversal` 在 `top-liquid perp + lower-turnover execution shell` 下，是否已经出现足以进入 `P2 admission` 的现实 after-cost pocket

## 1. 本轮采用的证据口径
本轮不重复 repo 首判里已经确认过的 `daily Binance spot OOS gross alpha skeleton`，而是只看本地已经存在、且更接近 desk shell 的两类 perp 证据：

### A. mature liquid tail-bucket perp transfer check
来源：`research/quant_digests/2026-03-25_0631_liquidity-split-tail-reversal-24h-loser-basket.md`

- 数据：Binance USDⓈ-M perpetual 公共 `15m` K 线
- 样本：近 `90` 天
- bucket：
  - majors：`BTC/ETH/SOL/XRP/DOGE/BNB`
  - mature tail：`ADA/LINK/AVAX/TRX/LTC/BCH`
- signal：过去 `24h` 横截面收益排序
- 组合：`long bottom-third / short top-third`
- 持有：`1h / 4h`
- 成本：显式加入简化 `5 bps one-way per unit turnover`

最关键结果：
- mature tail bucket 的 `24h loser-basket reversal` 在 **`1h hold`** 下平均**净收益约 `+0.942 bps / rebalance`，净 Sharpe 约 `1.758`**；
- 同时，大币 momentum 对照腿在 `15m / 1h / 4h` 三个持有窗都为负。

这说明：
- repo 里的 `24h XS reversal` 不是只能活在日频 spot 黑盒里；
- 迁到更诚实的 perp shell 后，至少在**成熟、仍高流动但非超大币**的子桶里，已经出现正的 after-cost pocket；
- 真正该保留的不是“全市场统一 loser basket”，而是**流动性分层后的 reversal pocket**。

### B. high-RV interaction shell on liquid perps
来源：`research/quant_digests/2026-03-25_1323_xs-interactions-highrv-loser-reversal.md`

- 数据：Binance USDⓈ-M perpetual 公共 `15m` K 线
- 样本：近 `90` 天
- universe：`BTC/ETH/SOL/XRP/BNB/DOGE/ADA/LINK/AVAX/LTC/BCH/TRX`
- signal：过去 `24h` return 排名
- gate：先按 `24h realized vol` 分 bucket，只在高 RV bucket 内做 `long losers / short winners`
- shell：`15m/1h` 调仓、`1h/2h/4h` 持有

最关键结果：
- 高 `24h RV` bucket 内，`1h hold、15m rebalance` 的平均**毛收益约 `+2.31 bps / rebalance`**；
- 同一条腿在 **`4h hold、1h rebalance`** 下平均**毛收益约 `+7.99 bps / rebalance`**；
- 该文档已明确给出：这条腿的 **break-even 更接近 `~8 bps round-trip`**，说明它不是 bar-by-bar taker alpha，但在**更慢 rebalance / 更低 turnover shell** 下，已经接近可交易区间。

这条证据对应的不是“再发明新 alpha”，而是回答本轮真正的问题：
**把 `24h XS reversal` 放进 `lower-turnover execution shell` 后，生存线确实比 repo 原始 daily spot 壳子好得多，而且已出现可继续 admission 的现实 pocket。**

## 2. 本轮该怎么读
这次 survivor follow-up 最关键的系统认知变化是：

1. **原始 repo 壳子确实不合格，但 alpha 本体没有被 perp transfer 一刀判死。**
   - repo 自带的是 `daily spot + 138.83% daily turnover + ~101% annual cost drag`；
   - 这只能证明“原始 implementation shell 不可交易”，不能证明 `24h XS reversal` 这个 raw alpha family 本身在 realistic perp shell 下一定死亡。

2. **一旦把对象收窄到更诚实的 perp 子口袋，after-cost pocket 已经出现。**
   - 不是 broad all-25 daily spot；
   - 也不是“top majors 全市场统一 losers-vs-winners”；
   - 而是：
     - **mature liquid tail bucket** 下的 `24h loser-basket reversal` 已有**净正**；
     - **high-RV bucket + slower rebalance** 下的 reversal 也已接近/进入可交易 break-even 区间。

3. **因此这条 survivor 的正确升级，不是继续停在 P1，也不是直接进 P3。**
   - 还没到 P3：因为当前还没有完成统一 clean-room 的 admission 套件（effectiveness / cross-asset / time stability / parameter stability / execution realism 五轴仍未补齐）；
   - 但已经超过“只剩 hypothesis / shell 叙事”的阶段：**现实 perp shell 下的 pocket existence 问题，答案已从不确定变成肯定。**

## 3. survivor verdict
### 结论
**`Rank 285` 本轮从 `Surviving candidate` 升级到 `Active P2`。**

### 升级口径
不是把它表述成“全市场 24h XS reversal 已可直接 paper”，而是更窄、更诚实的版本：

> `Rank 285` 的 repo 原始 `daily spot` 壳子不可交易，但在 Binance liquid perp 的更低换手/条件化子口袋里，`24h losers-vs-winners XS reversal` 已出现现实 after-cost 生存证据；因此它已值得进入正式 `P2 admission`，下一轮应围绕 `effectiveness / cross-asset stability / time stability / parameter stability / honesty-execution realism` 做 admission 收口，而不是继续把它留在 survivor。

## 4. 为什么不是 background/P0
因为这条线已经满足了 survivor follow-up 的肯定回答：

- **问题不是“spot repo 扣完 20bps 变负”，而是“在更诚实的 perp shell 下还有没有 pocket”。**
- 现在本地证据给出的答案是：**有。**
  - mature tail liquid perp 子桶：已有净正；
  - high-RV + slower rebalance 子桶：gross 已接近/达到现实 break-even；
  - 这已经足够支持进入 `P2 admission`。

## 5. 下一轮 P2 应回答什么
下一轮不应再重复“有没有 raw alpha skeleton”或“repo headline 是否有意思”，而应直接做 admission：

1. `effectiveness / expected return`：在统一 cost ladder 下的净值与 break-even；
2. `cross-asset stability`：是只活在 mature tail bucket，还是能扩到更大的 top-liquid perp 集合；
3. `time stability`：这是不是只靠最近几周 burst；
4. `parameter stability`：`1h/4h hold`、`15m/1h rebalance`、bucket cut 是否稳；
5. `honesty / execution realism`：maker/mixed/taker、buffer、换手压缩后是否仍留净 pocket。

## 6. 一句话结果
`Rank 285` 的唯一 survivor follow-up 已诚实收口：**repo 原始 daily spot 壳子虽不可交易，但在 liquid perp 的成熟 tail / 高-RV 低换手子口袋里，`24h` XS reversal 已出现现实 after-cost 生存证据，因此本轮应从 `keep_P1` 直接升级到 `Active P2`。**
