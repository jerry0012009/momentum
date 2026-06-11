# 别把这份 2026 multi-venue repo 只读成“大而全框架”：对 short-cycle desk，更该先测的是「same-chain DEX pool price gap close × fee/gas/slippage hurdle」这条 raw alpha

- 时间：2026-04-05 17:40 UTC
- 类型：2026 GitHub 新 repo source audit（README + `strategies/vol_surface_or_dex_arb/cross_dex_arb.py` + `docs/source_attribution.md`）+ DexScreener 公共 API live same-chain pool snapshot
- 主题类型：raw alpha
- 基础 alpha：**同一条链、同一交易对在不同 DEX 池子里的可执行价格会短时脱锚；当 gross spread 足够覆盖双边池费、滑点、gas 与 MEV buffer 后，买便宜池、卖昂贵池，赚的是 same-chain price-gap close，而不是赌币价单边方向。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/relative-value/stat-arb/same-asset/same-chain/cross-dex/pool-arbitrage/amm/price-gap-close/uniswap/sushiswap/curve/base/arbitrum/ethereum/1m/3m/5m/15m/repo/public-api/cost/gas/slippage/mev
- 证据类型：repo 源码直接给出 spread threshold / liquidity floor / gas 假设 / slippage 近似 / sizing 上限；外加 live 公共 API 快照验证同链多池价差确实存在

## 1. 先回答一句：base alpha 是什么？

**base alpha = same-chain / same-asset cross-DEX relative-value mean reversion。**

翻成人话：

- 同一个币对，比如 `WETH/USDC`，在 Uniswap、SushiSwap、Curve、Aerodrome 这些池子里，不会永远一模一样；
- 当某个池子被单边打穿、另一个池子还没完全跟上时，会出现短时价差；
- 真正能赚钱的不是“看到价差”本身，而是：
  - 这是不是**同链**、能迅速完成双腿；
  - gross spread 能不能覆盖**双边 pool fee + 滑点 + gas + MEV 风险缓冲**；
  - 价差是不是会在几分钟内回归，而不是卡成慢性失真。

所以这不是 filter，不是宏观 regime，也不是 execution 附件。
它本体就是一条 **same-asset / relative-value / stat-arb raw alpha**。

## 2. 为什么这轮值得写它？

如果先问一句：**它为什么比继续补 generic filter 更值得？**

答案很直接：

1. **它补的是当前素材池里还不够密的一支 raw alpha。**
   最近 intake 已经补了不少：
   - funding / basis / calendar spread
   - options parity / conversion
   - CEX→DEX lead-lag
   - pairs / cross-sectional reversal

   但**同链多 DEX 池价差闭合**这条更“原教旨”的 on-chain relative-value 壳，还没有单独落一篇。

2. **它比 cross-chain arb 更适合 desk 先做最小实验。**
   cross-chain 很容易变成桥延迟、库存管理、异步结算问题；
   same-chain 则更像真正的短周期 alpha：
   - 数据秒级/分钟级可拿
   - 价差闭合更快
   - 两腿执行路径更短
   - 更适合 `1m / 3m / 5m / 15m` 首轮验证

3. **repo 已经把“别只看 headline spread”这件事写进代码了。**
   这点很重要，因为很多人谈 DEX arbitrage 只会说“这里有价差”；
   但这份 repo 至少给了：
   - `min_spread_pct = 0.5%`
   - `min_liquidity_usd = 100_000`
   - `max_trade_size_usd = 50_000`
   - 链级 gas 假设（Ethereum `$15`、Arbitrum `$0.5`、Base `$0.2`、Polygon `$0.05`、Solana `$0.01`）

   也就是说，它不是纯概念，而是在逼你先做**净价差**计算。

## 3. 来源与材料信息

### Primary repo
- **Repo owner / Year**：`abailey81` / 2026
- **Title**：*Crypto-Statistical-Arbitrage*
- **Venue**：GitHub
- **Readable URL**：<https://github.com/abailey81/Crypto-Statistical-Arbitrage>
- **Repo URL**：<https://github.com/abailey81/Crypto-Statistical-Arbitrage>
- **Created / pushed**：2026-03-13 / 2026-03-15（GitHub metadata）
- **Official DOI**：未见

### Key source files actually used this round
- README：<https://raw.githubusercontent.com/abailey81/Crypto-Statistical-Arbitrage/main/README.md>
- Cross-DEX strategy code：<https://raw.githubusercontent.com/abailey81/Crypto-Statistical-Arbitrage/main/strategies/vol_surface_or_dex_arb/cross_dex_arb.py>
- Data/source attribution：<https://raw.githubusercontent.com/abailey81/Crypto-Statistical-Arbitrage/main/docs/source_attribution.md>

### Public data endpoints for fast replication
- DexScreener API：<https://docs.dexscreener.com/api/reference>
- Example token-pairs endpoint：<https://api.dexscreener.com/token-pairs/v1/ethereum/0xC02aaA39b223FE8D0A0E5C4F27eAD9083C756Cc2>

## 4. 这份 repo 真正提供了什么？

别被 repo 首页的“32 venues / 211 symbols / 226k+ lines”带偏。
对我们 desk，这轮最值钱的不是它的大一统叙事，而是里面这个**可拆出来单测的 side branch**：

> `strategies/vol_surface_or_dex_arb/cross_dex_arb.py`

它把 same-chain / cross-chain DEX arbitrage 直接拆成一个独立策略壳，核心逻辑非常清楚：

1. **按 chain + token pair 分组池子**；
2. 在同组内找最便宜池与最贵池；
3. 先算 gross spread；
4. 再扣：
   - 双边 gas
   - 双边 pool fee
   - 买卖两侧 slippage
5. 只有 `expected_profit_pct > 0` 才保留机会。

这就是一条完整策略，而不是一句“DEX 有价差”。

## 5. repo 里最值得记住的三个策略参数

## 5.1 它不是“看到 5bp 就冲”，而是先设 50bp 最低门槛

代码默认：

- `min_spread_pct = 0.005` → **50 bps**
- `max_slippage_pct = 0.01` → **1%**
- `min_liquidity_usd = 100,000`
- `max_trade_size_usd = 50,000`

这说明 repo 作者的默认假设其实很保守：

> 对大多数池子，只有 spread 已经胖到足以明显超过 friction，才配进入候选集。

这跟很多“只看报价差”的 DEX arb 讨论完全不是一个严谨度。

## 5.2 它默认承认：链不同，交易成本不是一个数量级

代码里硬编码的 gas 假设是：

- Ethereum：`$15`
- Arbitrum：`$0.50`
- Optimism：`$0.30`
- Base：`$0.20`
- Polygon：`$0.05`
- Solana：`$0.01`

这对 short-cycle desk 的启发很直接：

- **L1 蓝筹大池** 更可能是“有 gross spread，但净掉成本后没肉”；
- **L2 / 低 gas 链** 才更像 first-pass research universe；
- 如果你硬把 Ethereum 主网大池当成首发战场，很多事件会在成本后直接失真。

## 5.3 它把 same-chain 和 cross-chain 明确分开了

repo 没把这两件事混为一谈：

- **same-chain**：更像真正的短时 microstructure alpha
- **cross-chain**：额外要扣 bridge 成本与 bridge 时间价格风险

对我们而言，这个区分很关键。
因为 bot7 当前更需要的是：

> **能快速进 `1m / 3m / 5m / 15m` 最小实验、且能较快被证伪/证实的 raw alpha。**

所以这轮最值得 intake 的，显然是 **same-chain branch**，不是更慢更重的 cross-chain branch。

## 6. live honesty check：同链价差确实有，但蓝筹主网未必够你吃

我做了一个非常简单但很诚实的 live sanity check，结果写在：

- `reports/artifacts/quant_digests/cross_dex_samechain_20260405/summary.json`

### 6.1 取样口径

- 数据源：DexScreener 公共 API
- 链：Ethereum
- 交易对：`WETH/USDC`
- 过滤：`liquidity >= $1,000,000`
- 抓取时间：`2026-04-05 17:33 UTC`

### 6.2 结果

在这个口径下，共找到 **7 个流动性充足的池子**。

最便宜池：
- **Curve**
- 价格：**2053.15 USD**
- 流动性：**$6.44m**

最贵池：
- **SushiSwap**
- 价格：**2055.60 USD**
- 流动性：**$2.05m**

对应的 **gross same-chain spread = 11.93 bps**。

### 6.3 这个结果为什么反而有价值？

因为它很诚实地说明了一件事：

> **同链多池价差确实存在，但以 Ethereum 蓝筹 `WETH/USDC` 为例，11.9 bps gross spread 大概率还不够你在双边 pool fee + gas + 滑点后舒服赚钱。**

换句话说，这个 live snapshot 不是拿来证明“现在立刻开单就能赚”，而是拿来告诉我们：

1. 这条 alpha **不是空想**，真实市场里确实有 gap；
2. 但 first-pass 回测不该从 Ethereum 大蓝筹主网池开始幻想；
3. 更合理的首轮测试方向是：
   - **低 gas 链**（Base / Arbitrum / Solana）
   - **更容易出现短时错位的次级池或事件窗口**
   - 或者只做**高于净成本阈值很多**的 tail events

## 7. 对 short-cycle desk，正确读法应该是什么？

## 7.1 raw alpha 本体

最小可执行定义：

```text
net_gap_bps(t)
= gross_gap_bps(t)
- buy_pool_fee_bps
- sell_pool_fee_bps
- est_slippage_buy_bps
- est_slippage_sell_bps
- gas_bps(notional, chain)
- mev_buffer_bps
```

其中：

- `gross_gap_bps(t)` = 同链同币对下最贵可卖池 vs 最便宜可买池的价差
- 只有当 `net_gap_bps(t) > entry_hurdle`，这才算信号

所以 alpha 本体不是“price gap”，而是：

> **净掉摩擦之后仍显著为正的 same-chain executable price gap，会向零闭合。**

## 7.2 这条线最适合服务哪类 desk？

它最适合两类：

1. **本来就做 on-chain / hybrid execution 的 desk**
2. **虽然主做 perps，但想把 DEX relative-value 当成 event-driven 子策略库的 desk**

如果 desk 完全没有链上执行能力，这条线也未必白看：
它仍然可以作为：

- DEX microstructure shock 的研究样本
- CEX/DEX spread 或 execution veto 的补充素材

但本质上，它先是 raw alpha，再考虑能否退化成 filter。

## 8. 第一版最小可复现实验，应该怎么搭？

## 数据源、公开性、更新频率、实验口径

- **数据源**：DexScreener / GeckoTerminal / 协议 subgraph（Uniswap / Curve / Aerodrome 等）
- **公开性**：公开可得
- **更新频率**：近实时快照，可按 `1m` 存档；若有 websocket/更高频可再下钻
- **最小可复现实验口径**：
  - 按链分组
  - 按 token pair 分组
  - 每分钟记录 cheapest pool、richest pool、gross gap、TVL、24h volume、pool 类型、估计池费
  - 用固定名义（如 `$5k/$10k/$25k`）折算 `gas_bps` 和 `slippage_bps`

## 实验 A：先做事件统计，不先跑全自动回测

目标：先回答“净价差事件”有没有持续性。

- 链：`Base / Arbitrum / Ethereum`
- 交易对：
  - 蓝筹：`WETH/USDC`, `WBTC/USDC`, `cbBTC/WETH`
  - 稳定币：`USDC/USDT`, `DAI/USDC`
  - 再加 10~20 个中等活跃 long-tail pair
- 频率：`1m`
- 指标：
  - `gross_gap_bps`
  - `net_gap_bps`
  - 事件持续分钟数
  - 闭合速度（到 0 / 到 50%）
  - 不同链、不同池费层的事件占比

**验收标准：**
如果大部分 `net_gap_bps > 0` 事件只能活 1 帧，或者很快被反向 gap 吞掉，这条线要降优先级。

## 实验 B：只做 same-chain，不碰跨链

第一版策略规则可以非常朴素：

- `entry`：
  - `net_gap_bps > 3 / 5 / 8 bps` 三档分桶
  - 且连续存在 `2` 帧
  - 且两池 `TVL`、`24h volume` 过门槛
- `exit`：
  - `net_gap_bps <= 0`
  - 或 max holding `3m / 5m / 15m`
  - 或任一池流动性骤降 / 报价异常
- `size`：
  - 不超过较小池有效深度的一定比例（例如 `2%~5%`）
  - 不超过固定名义上限
- `risk`：
  - 单链限仓
  - 单 pair 并发限制
  - 事件级 kill switch（链拥堵、gas 飙升、区块延迟异常）

## 实验 C：把链成本当成 regime，而不是事后解释

直接分桶比较：

1. Ethereum
2. Base / Arbitrum
3. 稳定币池 vs 波动币池
4. 主流深池 vs 中等流动性池

看的是：

- 哪一桶的 `gross → net` 保留率最高；
- 哪一桶的 `time-to-close` 最短；
- 哪一桶在 `5m / 15m` 内仍留有 alpha。

我猜首轮最可能有戏的，不是 Ethereum 主网蓝筹，而是：

> **低 gas 链上的中高流动性池，在事件驱动时刻出现的短时价差闭合。**

## 9. 这条 alpha 最容易被误读成什么？

### 误读 1：看到任意价差就当套利

错。很多 gap 只是：
- 池费差异
- pool 类型差异
- 报价 stale
- 深度不够
- 同一 DEX 不同 fee tier 的自然价差

所以必须回到 **net executable gap**。

### 误读 2：把 cross-chain 和 same-chain 混写

错。桥延迟、库存调度、链间时间差，会把一条短周期 alpha 变成另一种生物。

这轮应该严格聚焦：
**same-chain only。**

### 误读 3：只盯蓝筹池

错。蓝筹池确实最干净，但也最容易被竞争压平。
如果要从 `1m / 3m / 5m / 15m` 里找 pocket，很多时候应该把注意力放在：

- L2
- 次级但非垃圾池
- 高波动事件窗口

## 10. 我的判断

**Verdict：值得进入 raw alpha 池，而且比继续补一个 shared filter 更值。**

原因：

1. **base alpha 清楚**：same-chain executable price-gap close
2. **完整策略壳清楚**：entry / exit / size / cost / gas / slippage 都能写
3. **公开数据好拿**：DexScreener / GeckoTerminal / subgraph 都足够做最小实验
4. **与当前池子互补**：它补的是 on-chain same-asset relative-value，而不是又一篇 funding / options / trend
5. **可快速证伪**：如果净价差事件太少、闭合太慢、成本太高，几天数据就能知道

如果用一句话总结：

> 这份 repo 最值得 desk 抄的，不是“multi-venue 大系统”外壳，而是里面那条更容易独立复现的 same-chain DEX pool price-gap close：只有当 gross spread 扣完 fee / gas / slippage 还活着，它才配叫 raw alpha。

## 11. 下一步怎么测（直接排执行顺序）

### Step 1：先搭 `1m` 池快照板
连续抓 7 天：
- `chain`
- `pair`
- `pool`
- `priceUsd`
- `liquidityUsd`
- `volume24h`
- `dexId`
- `estimated_fee_bps`
- `gross_gap_bps`
- `net_gap_bps($5k/$10k/$25k)`

### Step 2：只做 same-chain event study
统计：
- `net_gap_bps > 0` 事件数
- 持续时间分布
- 3m / 5m / 15m 闭合概率
- 按链、按 pair、按池费层分桶

### Step 3：再上最简单策略回测
- `entry`: `net_gap_bps > 5 bps` 且连续 2 帧
- `exit`: 回到 `<= 0` 或 `15m` 超时
- `size`: `$5k/$10k` 两档
- `cost`: maker/taker、滑点、gas、MEV buffer 都显式计入

### Step 4：只在证明 same-chain 能活后，才考虑 cross-chain
否则别急着把题目做重。

## 12. 来源链接

### Primary repo
- GitHub: <https://github.com/abailey81/Crypto-Statistical-Arbitrage>
- README: <https://raw.githubusercontent.com/abailey81/Crypto-Statistical-Arbitrage/main/README.md>
- Strategy source: <https://raw.githubusercontent.com/abailey81/Crypto-Statistical-Arbitrage/main/strategies/vol_surface_or_dex_arb/cross_dex_arb.py>
- Source attribution: <https://raw.githubusercontent.com/abailey81/Crypto-Statistical-Arbitrage/main/docs/source_attribution.md>

### Public data
- DexScreener API docs: <https://docs.dexscreener.com/api/reference>
- Ethereum WETH token-pairs endpoint used for live snapshot: <https://api.dexscreener.com/token-pairs/v1/ethereum/0xC02aaA39b223FE8D0A0E5C4F27eAD9083C756Cc2>

## 13. 本地 artifacts

- `reports/artifacts/quant_digests/cross_dex_samechain_20260405/summary.json`
