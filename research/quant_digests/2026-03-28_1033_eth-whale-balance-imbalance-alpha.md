# 别把 ETH whales 只当链上慢变量：这篇 Philadelphia Fed working paper 更该先测的是「大钱包净增持 − 小钱包净减持 → ETH 后续漂移」事件型 raw alpha

- 时间：2026-03-28 10:33 UTC
- 类型：raw alpha
- 主题标签：raw-alpha/on-chain/eth/whales/holder-balance/flow-imbalance/event-driven/external-data/relative-positioning/minute-sampling/1m/3m/5m/15m/paper/public-data/cost
- 证据类型：2024/2025 Philadelphia Fed working paper 全文 PDF + 本地全文抽取 + Coin Metrics 指标口径审阅
- 主题类型：raw alpha
- 基础 alpha：当大钱包 ETH 持仓净增加、同时小钱包净减持时，后续 ETH 收益更偏向顺着 whales 的方向漂移；反向则偏空
- 是否可独立复现：是（链上原始数据公开；便利版 cohort 聚合常需 vendor / 自建）
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（但更适合做稀疏事件型部署，而不是每根 bar 常开）

## 1. 这次看了什么，为什么它比再补一篇泛 gate 更值得

这次主看的是 **Alan Chernoff, Julapa Jagtiani** 的 Philadelphia Fed working paper：

> **Beneath the Crypto Currents: The Hidden Effect of Crypto “Whales”**

先把结论翻成人话：

> **ETH 大户在涨之前往往先加仓，小户在涨之前反而更容易减仓。**

这不是那种“链上情绪看板很有趣”的描述性材料，而是有明确方向、明确对手盘、明确可交易对象的信号：

- **base alpha 很清楚**：`large-holder accumulation minus small-holder distribution`
- **交易标的是单一且直接的**：ETH 现货 / ETH perp
- **并不依赖某个固定图形**：不是 breakout / retest / trend filter 的附庸
- **天然可以作为完整策略**：entry、exit、sizing、risk、cost 都能拆

所以相比再补一篇纯 filter / regime，这篇更像**外部数据驱动的事件型 raw alpha 候选**。

## 2. 论文里真正有交易价值的 headline

论文样本是 **2018-01-01 到 2023-12-31** 的 **2191 个日度观测**，研究对象是 ETH，不是全市场散点故事。作者用 Coin Metrics 的钱包分层数据，把 ETH 持有人分成四档：

1. **>$1M ETH 持仓**
2. **$100K ~ $1M**
3. **$10K ~ $100K**
4. **$10 ~ $10K**

核心回归是看：**第 t 天不同钱包层级的持仓变化，能否预测第 t+1 天 ETH 收益。**

Table 3 的主结果非常直接：

- `PctDelta_Top1M = 0.6263`，`p = 0.001176`
- `PctDelta_100K = 0.2862`，`p = 0.000130`
- `PctDelta_10K = -0.4847`，`p = 1.24e-14`
- `PctDelta_LT10K = -1.8223`，`p < 2e-16`
- `Adjusted R² = 0.9024`

作者自己的 plain-English 总结也很硬：

> **large ETH holders tend to increase their ETH holdings prior to a price increase, while small ETH holders tend to reduce their ETH holdings prior to a price increase.**

更直白地说：

- **大户增持 → 次日更容易涨**
- **小户增持 → 次日反而更容易跌**
- 这不是“大家一起 bullish”的情绪共振，而是**不同钱包层级站在相反方向**

这点对 desk 很重要，因为它意味着信号不只是“净流入 > 0 就看多”，而是：

> **看的是大户与小户之间的持仓分歧。**

## 3. 为什么我把它归成 raw alpha，而不是只当 filter

这里必须先回答用户要求的那句：**这篇东西的 base alpha 是什么？**

答案不是“whale activity 很重要”，而是：

> **当大钱包相对更积极吸收 ETH、小钱包相对更积极让出 ETH 时，后续 ETH 价格更容易沿 whales 有利的方向漂移。**

也就是说，真正的信号不是单边的 `whale_buying`，而是更接近：

- `whale accumulation`
- 对上
- `retail distribution`

形成的 **holder-imbalance spread**。

这已经足够构成一个可独立交易的 alpha：

- **long leg**：ETH
- **short leg / flat leg**：空仓或做反向 ETH perp
- **signal**：链上 holder imbalance
- **exit**：时间衰减 / signal 回落 / adverse move

它当然也能进一步当：

- trend alpha 的确认层
- breakout 的 veto / size-up
- carry / basis 策略的 regime gate

但如果只把它当 gate，会低估它本身作为**外部数据 raw alpha**的价值。

## 4. 对 desk 最有用的，不是日频结论本身，而是它暴露的“谁在拿货”结构

论文最有价值的地方，不是“预测下一天 ETH 涨跌”这一个日频 headline，而是它把一个很可迁移的市场结构钉死了：

### 4.1 结构不是“链上总净流入”，而是**分层持仓的方向差**

这意味着 desk 化时不一定要机械照抄论文的四档美元阈值；更合理的做法是保留结构、放松实现：

- 大钱包 cohort：top holders / smart-money-like cohort / 非交易所巨鲸 cohort
- 小钱包 cohort：零售长尾 / 小额地址簇
- 关键不是分得多漂亮，而是**大户与小户的净方向是否背离**

### 4.2 这条 alpha 天然是**稀疏事件型**，不是每根 bar 常开

它更像：

- 有明显链上吸筹 / 派发事件时开仓
- 没有 imbalance 时空仓

所以它和很多短周期 raw alpha 不冲突，反而互补：

- 它不需要每分钟都发信号
- 但发信号时，理论上是更有“知情资金痕迹”的那种 alpha

### 4.3 它比纯 sentiment / fear-greed 更接近“可交易”

因为这里不是 survey，也不是新闻文本，而是**链上真实持仓变化**。哪怕便利聚合口径不免费，底层数据本身仍是公开账本数据，不是黑箱情绪分数。

## 5. 论文还告诉我们一件事：波动更多像是零售驱动，不是 whales 驱动

Table 4 的波动回归也很值得记一下：

- `StdDev_Top1M = -2.13e-08`，显著为负
- `StdDev_100K = 5.61e-08`，显著为正
- `StdDev_10K = 2.16e-08`，显著为正
- `StdDev_LT10K = 5.07e-08`，显著为正

论文原话大意是：

> **ETH return volatility 更像是由小投资者驱动，而不是由 whales 驱动。**

这对策略设计的含义很直接：

- **大户持仓变化**更像方向线索
- **小户剧烈动**更像噪音 / 波动来源

所以我们不该把 `retail frenzy` 误读成“趋势确认”，更像应该把它读成：

- 若只有小钱包在加速，未必是好 long
- 若大钱包吸筹、小钱包在让出筹码，才更接近这篇 paper 的正向结构

## 6. desk 化后的最小完整策略骨架

## 6.1 Base alpha

定义一个最简 holder-imbalance：

- `L_t = z(ΔHoldings_large)`
- `S_t = z(ΔHoldings_small)`
- `Imbalance_t = L_t - S_t`

其中：

- `ΔHoldings_large`：大钱包 cohort 在过去 `N` 分钟的净持仓变化
- `ΔHoldings_small`：小钱包 cohort 在过去 `N` 分钟的净持仓变化

直觉上：

- `Imbalance_t >> 0`：whales 在吸筹，零售在让筹码 → 偏多
- `Imbalance_t << 0`：whales 在派发，零售在接货 → 偏空

## 6.2 Entry

对当前短周期 desk，我会先做**事件触发式**，而不是 continuous always-on：

- **long entry**：
  - `Imbalance_t` 进入历史滚动 `95%` 或 `97.5%` 分位
  - 且 ETH 价格未在过去 `5~15m` 已经单边拉满
  - 可选：perp funding 未极端拥挤到明显反向
- **short entry**：
  - `Imbalance_t` 进入历史滚动 `2.5%` 或 `5%` 分位
  - 即 whales 在减、小钱包在接

这一步故意不把它写成“bar close > MA 就上”，因为这条线的本质是**持仓结构事件**。

## 6.3 Exit

初版别贪复杂，直接做三层：

1. **时间退出**：`30m / 60m / 120m / 240m` 多档持有观察
2. **signal decay**：`Imbalance_t` 回到中性带就平
3. **price-based stop**：按 `1.0~1.5 x intraday ATR` 或固定 bps 止损

如果结果显示 edge 很快衰减，就把它当 `1m/3m/5m` 事件漂移；
如果结果在 `1~4h` 仍有残留，再延长持有。

## 6.4 Sizing

这条线适合**signal-strength sizing**，不适合梭哈：

- `size ∝ clip(|Imbalance_z|, 0, cap)`
- 再除以短窗 realized vol
- 单事件 notional cap 固定

因为它更像稀疏 alpha，不是高频密集刷单，没必要把 turnover 做高。

## 6.5 Risk / Cost

它的优点是：

- **单腿 ETH 交易**，比跨所 / 多腿 stat-arb 简单得多
- 不需要靠极薄 gross edge 抵成本

但也有三个真实风险：

1. **数据延迟风险**：你拿到的是不是足够快的 cohort 更新？
2. **标签污染风险**：交易所地址、合约地址、桥接地址有没有混进大钱包？
3. **价格已先走风险**：链上持仓变化被你观察到时，价格可能已经消化一部分

所以这条线的核心不是手续费，而是**数据工程诚实度**。

## 7. 它和 `1m / 3m / 5m / 15m` 的关系：能做，但别假装它是每根 bar 的主信号

这里要刻意诚实一点：

- **论文证据本身是日频**
- 不是直接给你 `next 5m ETH return` 的回归

但它依然和当前 desk 有直接关系，因为：

1. **底层数据不是日频生成的**：链上账本是 block-level 公开变化
2. **可把论文结构迁移成分钟采样**：不是复刻“日频标签”，而是复刻“大户 vs 小户分歧”
3. **最合理的部署方式本来就是稀疏事件型**：当 whale imbalance 爆出来时，在 `1m/3m/5m/15m` 上观察漂移窗口

所以我会这样定位：

- **`1m / 3m`**：最适合测事件爆发后的即时 follow-through
- **`5m / 15m`**：最适合测 drift 能否延续到更可交易的 holding window
- **不是**：逐 bar 常开主因子
- **而是**：事件型 raw alpha / execution trigger

## 8. 数据源、公开性、更新频率、最小可复现实验口径

### 8.1 原论文数据源

- **Coin Metrics**
- 论文使用的是 Coin Metrics 的 ETH 钱包分层持仓数据
- 便利性高，但常见企业级聚合口径并不总是免费

### 8.2 对我们更现实的公开替代口径

底层链上数据本身是公开的，因此最小实验可以拆成两层：

#### A. 公开原始数据层

- Ethereum 链上地址余额 / 转账 / 区块
- 公开性：**公开可得**
- 更新频率：**每个区块（约 12 秒级）**

#### B. cohort 构造层

需要自己做：

- 大钱包地址集合（尽量剔除交易所 / bridge / 合约金库）
- 小钱包地址集合
- 每分钟或每 5 分钟重算 cohort 余额变化

最小可复现实验不要求一上来完美重建 Coin Metrics 的四档美元桶；可以先做一个更 desk-friendly 的代理：

- **large cohort**：按 ETH 持仓或 USD 估值排前 `x%` 的非交易所地址
- **small cohort**：按持仓排后部、且活跃度足够的零售地址簇

### 8.3 最小实验口径

先别追求全市场高精度标签，第一轮只做：

1. **标的**：ETHUSDT perp（或 ETH 现货）
2. **频率**：`1m`
3. **signal window**：过去 `15m / 30m / 60m`
4. **signal**：
   - `Δlarge_balance`
   - `Δsmall_balance`
   - `imbalance = z(Δlarge) - z(Δsmall)`
5. **entry**：`imbalance` 超分位阈值
6. **holding**：`15m / 30m / 60m / 240m`
7. **cost**：按单腿 ETH perp taker / maker-taker 两档

这个实验已经足够回答第一层 admission question：

> **分钟化后的 whale-vs-retail imbalance，到底有没有可持续到短周期 bar 的 drift？**

## 9. 下一步怎么测（这次最重要）

先不要做花哨建模，先做 **structure-preserving minimal experiment**：

1. **先做 cohort 代理，不追求完美标签**
   - 只要能稳定分出 `large` 与 `small`，就先跑
   - 第一轮重点是检验结构，不是竞赛谁的地址标签最全

2. **分钟化 signal**
   - 对每个 `1m` 时间点，计算过去 `15m / 30m / 60m` 的 `Δlarge`、`Δsmall`
   - 构造 `imbalance z-score`

3. **做四个 holding horizon**
   - `15m`
   - `30m`
   - `60m`
   - `240m`

4. **只问三个问题**
   - `imbalance > q95` 时，ETH 后续收益是否显著更高？
   - `imbalance < q05` 时，ETH 后续收益是否显著更低？
   - 边际主要出现在 `1m/3m/5m` 还是更像 `1h/4h`？

5. **再做一次最关键的对照**
   - 只看 `Δlarge`
   - 只看 `Δsmall`
   - 看 `Δlarge - Δsmall`

如果第三个显著强于前两个，就说明这条线真正的 alpha 本体确实是：

> **holder imbalance spread**，而不是单边净流入。

## 10. 诚实约束 / 风险提示

- **原论文不是 intraday 论文**：它证明的是日频 lead-lag，不是直接证明 `next 5m`
- **美元桶会随 ETH 价格变化而漂移**：实盘更适合改成持仓分位 / ETH 数量阈值 / 滚动 USD 阈值
- **地址标签是关键误差源**：若把交易所热钱包当 whale，信号会严重变形
- **这条 alpha 更像稀疏事件，不像全天候 bar-bar 因子**
- **别把它硬伪装成 every-bar master signal**：更诚实的读法是 `event-driven raw alpha`

## 11. 结论

这篇 paper 值得进当前素材池，不是因为“whales 很神秘”，而是因为它给了一个**可以直接交易化的结构性方向信号**：

> **当大钱包吸筹、小钱包让筹码时，ETH 后续价格更可能朝对 whales 有利的方向漂移。**

它不是现成的 `5m bar-close` 因子，但非常适合当前 desk 做一轮**分钟采样的事件型 raw alpha admission check**。

一句话总结：

> **先别把 whale 数据只当链上故事；更该先测的是“大户拿货 − 小户出货”这个 holder-imbalance spread，能不能在 `1m/3m/5m/15m` 上留下可交易的 ETH drift。**

## 12. 来源

1. **Alan Chernoff, Julapa Jagtiani (2025 draft; Philadelphia Fed Working Paper series WP 24-14, published Aug 2024, revised Dec 2025). _Beneath the Crypto Currents: The Hidden Effect of Crypto “Whales”_.**  
   Venue: Federal Reserve Bank of Philadelphia Working Paper  
   DOI: `https://doi.org/10.21799/frbp.wp.2024.14`  
   Readable URL: `https://www.philadelphiafed.org/the-economy/banking-and-financial-markets/beneath-the-crypto-currents-the-hidden-effect-of-crypto-whales`  
   PDF URL: `https://www.philadelphiafed.org/-/media/frbp/assets/working-papers/2024/wp24-14.pdf`

2. **Coin Metrics. Network / market data provider referenced by the paper.**  
   Readable URL: `https://coinmetrics.io/`
