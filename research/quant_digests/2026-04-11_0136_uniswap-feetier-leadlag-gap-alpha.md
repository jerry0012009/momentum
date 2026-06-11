# 别把这篇 Uniswap 论文只读成“DEX 价格发现变强了”：对 short-cycle desk，更该先测的是「same-pair fee-tier lead-lag gap × cross-fee-tier close」这条 raw alpha 候选

- 时间：2026-04-11 01:36 UTC
- 类型：2025 *Journal of Futures Markets* 开放获取全文 PDF + 原文 Table 3/4/6 + GeckoTerminal 公共 `1m` portability probe
- 主题类型：raw alpha
- 基础 alpha：**同一币对在 Uniswap v3 的不同 fee tier 并不会永远同步；低费率、流动性更集中的池子更容易先吸收信息，而高费率/更钝的池子会短暂滞后。于是可交易对象不是“ETH 会涨还是跌”，而是 `same-pair cross-fee-tier price gap` 会不会向更一致的价格回归。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否（alpha 本体清楚，但实盘还要补 DEX 双腿/借贷或 CEX 对冲、gas、MEV、失败成交与路由细节）
- 主题标签：raw-alpha/relative-value/stat-arb/same-asset/same-dex/cross-fee-tier/uniswap-v3/lead-lag/price-discovery/eth-usdt/1m/3m/5m/15m/paper/fulltext/public-probe/gas/mev/cost/risk
- 证据类型：论文实证 + 公共 minute 数据 portability probe

## 1. 这次看了什么
主论文是：

- **Alexander, Carol; Chen, Xi; Deng, Jun; Fu, Qi (2025)**
- **Title:** *Price Discovery and Efficiency in Uniswap Liquidity Pools*
- **Venue:** *Journal of Futures Markets*
- **DOI:** `10.1002/fut.22593`
- **Readable URL:** <https://doi.org/10.1002/fut.22593>
- **Open-access PDF（Figshare repository）:** <https://figshare.com/articles/journal_contribution/Price_Discovery_and_Efficiency_in_Uniswap_Liquidity_Pools/29209757>
- **Repo / code status:** 论文说明 `Python + R scripts available upon request`，未见公开 GitHub 仓库

这篇 paper 最容易被读成一句空话：

> `Uniswap v3 比 v2 更有效，某些 v3 池子的 price discovery 甚至逼近 Bitstamp。`

但对我们 desk 真正更值钱的，不是这句市场结构总结，而是它隐含的一条更硬的 raw alpha 候选：

> **同一币对、同一个 DEX、不同 fee tier 之间，本身就会出现短时 lead-lag；尤其是 `0.05%` 池子，往往比 `0.30%` 池子和 v2 更快吸收信息。**

一句话核心结论：

> **别只把这篇 paper 当 DEX 市场质量报告；更值得先做最小实验的是：把 `0.05%` fee pool 当 leader，把 `0.30%/v2` 当 lagging leg，去测同币对跨 fee-tier 的短时 price-gap close。**

一句话证明方式：

> **论文用近 3 年、11 个 token pair 的 minute-level 数据，做 Granger causality、component share / modified information share、spillover 与回归解释；我再补一个公开可抓的 Uniswap v3 `1m` probe，先看最近样本里 `0.05%` 池领先 `0.30%` 池这件事有没有 first-pass 痕迹。**

## 2. 为什么这条线值得单独写，而不是并到旧的 DEX / price-discovery 主题里
这次单独拎出来，是因为它和现有 digest 里的几条线并不一样：

- 它**不是** `CEX ↔ DEX` 同资产价差关闭（那更像跨 venue spatial arb）；
- 它**不是** `same-chain cross-DEX pool arbitrage`（那是 Uniswap / Sushi / Curve 等不同协议间的价差）；
- 它也**不是** “哪边更有效”的机制空结论。

这条线更具体：

> **同一条链、同一个协议、同一个币对，仅仅因为 fee tier 和池子结构不同，就会形成不同的信息吸收速度。**

所以它的 base alpha 很清楚：

> **cross-fee-tier relative-value mean reversion。**

这不是 filter / regime / overlay；它是一条可定义入场、出场与持有窗口的 raw alpha 候选。

## 3. 论文里最该拿走的，不是“v3 更先进”，而是这 4 个 hard findings
### 3.1 `0.05%` 池经常比 `0.30%` 池和 v2 更先反应
论文对 11 个 token pair 做 daily VECM / CS / MIS / spillover 之后，结论非常直接：

- `Uniswap v3 (005)` 的价格发现能力，通常高于 `v3 (030)` 与 `v2`；
- 文中原话几乎就是：**`v3 (005)` prices tend to lead those on `v2` and `v3 (030)`**；
- 对部分 pair，`v3 (005)` 的 median CS / MIS 甚至高于 Bitstamp。

这对交易最重要，因为它把 `哪个池先动` 这件事说清楚了。

### 3.2 低 fee tier 更像信息腿，高 fee tier 更像容量腿
论文的解释不是玄学，而是很像 desk 直觉：

- 低费率池（尤其 `0.01% / 0.05%`）更适合低波动 pair，交易环境更高效；
- 高费率 `0.30%` 池更适合高波动 pair 和大额单，但 price discovery 更弱；
- 大单会**降低** `v3 (005)` 的价格发现能力，却会**提高** `v3 (030)` 与 `v2` 的价格发现能力。

翻成人话：

> **小而灵的池子更像“先知道”的腿，大而厚的池子更像“后补成交”的腿。**

这正是 lead-lag spread 会出现的微观来源。

### 3.3 波动高时，Uniswap 整体更像 shock receiver
Table 6 与正文结论都指出：

- 波动上升时，Uniswap 各池的 CS / MIS / efficiency 普遍下降；
- 说明更 informed 的交易者在高波动期更偏向 CEX；
- Uniswap 上相对更多的可能是 speculator / arbitrage flow。

所以这条 alpha 不是全天候都该开：

> **高波动时 cross-fee-tier gap 可能更大，但也更容易夹带 gas / congestion / MEV / non-informational flow。**

### 3.4 paper 已经把“哪个 pair 更适合哪个 fee tier”讲出来了
文中对 `ETH-USDC / ETH-USDT / BTC-ETH / DAI-USDC / ETH-DAI / LINK-ETH / UNI-BTC / LINK-USDT` 等 pair 做了比较，核心模式是：

- `0.01% / 0.05%` 更适合低波动 pair；
- `0.30%` 更像高波动 pair 的 liquidity bucket；
- `0.05%` 池在多个 pair 上表现出更强 price discovery。

所以这条线不是“所有 fee tier 都互相平等”。

真正更像 desk 研究对象的是：

1. **先选 pair**；
2. **再指定 leader fee tier**；
3. **最后才测 spread-close。**

## 4. 论文里最能直接转成交易语言的表格结论
### 4.1 Table 3：Granger causality 显示不同 fee tier 之间存在稳定 lead-lag 关系
Table 3 最重要的不是死盯某一格百分比，而是看**整篇 paper 的综合归纳**：

- `v3 (005)`、`v3 (030)`、`v2` 之间并不是同步一口价；
- 不同 fee tier 之间存在持续的 Granger-causal linkage；
- 结合 Table 4 的 CS / MIS 与 Table 5 的效率检验，作者最后明确总结为：**比较 Uniswap 不同池子时，`v3 (005)` 往往领先 `v3 (030)` 与 `v2`。**

也就是说，Table 3 给的是“有稳定传导关系”，而 paper 的总结合成结论给的是“哪条腿更像 leader”。

### 4.2 Table 4：`0.05%` 池的 CS / MIS 普遍更强
Table 4a 的整体模式非常一致：

- `v3 (005)` 的 median CS / MIS 基本高于 `v3 (030)` 和 `v2`；
- `v3 (030)` 常常是几个池里最弱的一腿；
- 部分 pair 上 `v3 (005)` 甚至能压过 Bitstamp。

这说明它不是偶尔的 event-time 现象，而是样本期内相对稳定的结构特征。

### 4.3 Table 6：波动 / basis / 大单对不同 fee tier 的作用方向不同
这张表对交易设计尤其重要：

- **Vol**：大多数池子的 CS / MIS / ADH 都随波动升高而下降；
- **Basis**：Uniswap 与 Coinbase / Bitstamp 的 basis 变大，通常会拖累 price discovery；
- **LTR（large trade ratio）**：
  - 对 `v3 (005)` 多数 pair 是**负向**；
  - 对 `v3 (030)` 与 `v2` 则常是**正向**。

翻译成策略语言就是：

> **`0.05%` 池更适合做“快信息腿”；`0.30%` 池更适合承接大额/高波动流。**

所以我们不该只看 spread 是否偏了，还该看：

- 当前是不是高波动时段；
- leader 池是不是仍然活跃；
- lagging 池是不是只是因为大额单或流动性迁移才临时偏离。

## 5. 本地 public-data probe：最近样本里，这条线还有没有 first verdict？
我用 **GeckoTerminal 公共 API** 做了一个非常克制的最小快检，只看：

- Ethereum 主网 Uniswap v3
- 同一币对：`WETH / USDT`
- fee tiers：
  - `0.05%` pool：`0x11b815efB8f581194ae79006d24E0d814B7697F6`
  - `0.30%` pool：`0x4e68Ccd3E89f51C3074ca5072bbAC773960dFa36`
- 频率：`1m`
- 数据：各池最近 `1000` 条 minute OHLCV；两池可对齐后的重叠样本约 **393 分钟**

本地 artifact：

- `/root/clawd/jerry/momentum/reports/artifacts/literature/uniswap_fee_tier_leadlag_probe_summary_2026-04-11.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/uniswap_fee_tier_leadlag_probe_detail_2026-04-11.csv`

### 5.1 最近重叠样本里，`0.05%` 池确实更像 leader
在这段最近窗口中：

- cross-fee-tier log spread 的均值约 **+0.23 bps**；
- spread 标准差约 **2.46 bps**；
- return cross-corr 里：
  - `corr(r_005[t-1], r_030[t]) ≈ 0.483`
  - `corr(r_030[t-1], r_005[t]) ≈ 0.228`

这不是论文级证明，但至少和 paper 的方向一致：

> **最近样本里，`0.05%` 池的一步领先相关性，明显强于 `0.30%` 池反过来的领先相关性。**

### 5.2 若只做 spread 极端回归，最近样本里有 first-pass 正 edge
我用很朴素的壳：

- 定义 `spread = log(price_005 / price_030)`
- 用 `240` 分钟滚动均值/标准差构造 `z-score`
- 当 `|z| > 2` 时，做 **spread-close**（`z>2` 则 short spread，`z<-2` 则 long spread）
- 看未来 `1 / 3 / 5 / 15` 分钟的 signed spread-close bps

结果（样本很小，只作 first verdict）：

- `1m`：约 **20** 次事件，均值约 **+6.82 bps**，胜率约 **85%**
- `3m`：约 **20** 次事件，均值约 **+5.97 bps**，胜率约 **90%**
- `5m`：约 **20** 次事件，均值约 **+6.92 bps**，胜率约 **100%**
- `15m`：约 **20** 次事件，均值约 **+7.46 bps**，胜率约 **95%**

这组数字不能直接当 production PnL，但它至少说明：

> **最近样本里，跨 fee-tier 的极端价差没有立刻塌成随机噪声，仍有可见的 close 倾向。**

## 6. 但必须诚实：这轮 probe 很容易高估
这里要非常保守。

### 6.1 当前还不是 executable quote
现在用的是 pool 的 minute OHLCV close proxy，不是：

- 同步可执行 marginal quote
- 指定 notional 后的 executable quote
- 扣掉 gas / priority fee / MEV buffer 后的净价差

所以这些 bps 不是“可以直接赚到”的 bps。

### 6.2 只对齐到了 393 个重叠分钟，样本很薄
`0.30%` pool 的分钟活跃度明显比 `0.05%` 差，导致最近对齐样本不多。

这本身也许就是信息：

- `0.05%` 池更像主信息腿；
- `0.30%` 更像低频、承接型、容量型腿。

但它也意味着：

> **当前快检更像“admission signal”而不是“足够大样本的策略定稿”。**

### 6.3 on-chain 真正的敌人不只是手续费
这条线最容易被忽略的成本包括：

- gas fee
- priority fee / inclusion delay
- MEV / sandwich / backrun risk
- pool 状态在同一块内被别人先吃掉
- 你做第二条腿时 quote 已经变了

所以如果真的做 production，核心问题不是“alpha 有没有”，而是：

> **net executable edge 扣完这些链上摩擦后还剩多少。**

## 6.5 策略拆解（必填）
- 方向属性：relative value / stat-arb / market-neutral-ish
- 基础 alpha：same-pair cross-fee-tier price-gap close
- regime：优先低至中等波动、链上拥堵正常、leader pool 活跃而 lagging pool 非极端稀疏时
- filter / veto：`|z|` 不够大不做；gas / priority fee / MEV buffer 不过线不做；大额单冲击后 lagging pool 若本身 liquidity 太薄也不做
- risk / sizing / execution overlay：按 expected executable edge 分层 sizing；限制单次 notional 只打在不会把 pool 自己推回来的深度内；设置 `time stop + spread stop + chain congestion veto`

## 7. 为什么它和当前 desk 仍然相关
虽然当前 desk 主战场不是纯 DEX，但这条线仍有直接价值：

### 7.1 它补的是“同协议内部”这层 relative-value
我们已经有：

- CEX ↔ DEX spread
- same-chain cross-DEX spread
- spot ↔ futures / perp basis
- cross-venue futures basis

但**同协议、同币对、不同 fee bucket** 这层还没单独写过。

这层很有研究价值，因为它更纯：

- 不涉及不同协议的实现差异；
- 不涉及不同 venue 的 custody / API / outage 差异；
- 只剩下 **fee tier + liquidity distribution + informed flow routing**。

### 7.2 它也能反哺更大的 CEX/DEX 壳
即使最后不做独立策略，这条线也能服务：

- DEX leg 该打哪个池
- 某个池的报价是否更适合作为 leader quote
- 同链路由时是否该优先 `0.05%` 还是 `0.30%`

也就是说：

> **它既可以是独立 raw alpha candidate，也可以是未来 CEX/DEX routing shell 的 routing prior。**

## 8. 可复刻的最小实验
### 数据源 / 公开性 / 更新频率
- **论文层**：开放获取 PDF（Figshare repository）
- **链上市场数据**：GeckoTerminal / DexScreener / Uniswap subgraph / Dune（公开）
- **更新频率**：可做到分钟级，进一步可下探到 swap-level / block-level

### 最小研究假设
> 对同一币对，若 `0.05%` pool 相对 `0.30%` pool 的 price spread 明显偏离自己的滚动带宽，未来 `1m ~ 15m` 更容易发生 spread-close，而不是继续无限扩散。

### 最小回测切口
1. 先只做 `WETH/USDT`、`WETH/USDC`
2. 只比较 `0.05%` 与 `0.30%`
3. 用 `1m / 3m / 5m / 15m` 测：
   - leader-lag corr
   - signed spread-close
   - friction ladder 前后的剩余 edge

## 9. 下一步怎么测
下一步别急着扩到十几个 pair，我会先补这 4 件最值钱的事：

1. **把 minute close proxy 升级成 swap / quote 级 executable edge**
   - 直接抓 pool swap 与 liquidity state
   - 对固定 notional 计算真实 executable price
2. **把 cost ladder 补完整**
   - gas
   - priority fee
   - MEV / reordering buffer
   - 单腿失败概率
3. **把 pair 扩到 `ETH-USDC / ETH-USDT / DAI-USDC`**
   - 检查是不是只有主流稳定币 pair 才成立
   - 还是更多 low-volatility pair 都能看到类似结构
4. **做“独立交易壳”与“routing prior”两条分支**
   - A 分支：直接做 cross-fee-tier spread-close
   - B 分支：把 `0.05%` 视作 leader quote，只拿来指导更大的 CEX/DEX 价差交易

如果 executable 版本扣完链上摩擦后还剩正 edge，它就能进 DEX-RV clean replication；如果一扣 gas / MEV 就塌，那它仍然值得保留为 **DEX quote selection / routing prior**，不算白做。

## 10. 来源
1. **Alexander, C., Chen, X., Deng, J., & Fu, Q. (2025). _Price Discovery and Efficiency in Uniswap Liquidity Pools_. Journal of Futures Markets.**
   - DOI: <https://doi.org/10.1002/fut.22593>
   - Publisher page: <https://onlinelibrary.wiley.com/doi/10.1002/fut.22593>
   - OA repository / PDF: <https://figshare.com/articles/journal_contribution/Price_Discovery_and_Efficiency_in_Uniswap_Liquidity_Pools/29209757>
2. **GeckoTerminal API**
   - Pool info / OHLCV docs root: <https://www.geckoterminal.com/dex-api>
   - Pools used in probe:
     - `WETH / USDT 0.05%`: `0x11b815efB8f581194ae79006d24E0d814B7697F6`
     - `WETH / USDT 0.30%`: `0x4e68Ccd3E89f51C3074ca5072bbAC773960dFa36`
3. **本地 portability artifacts**
   - `/root/clawd/jerry/momentum/reports/artifacts/literature/uniswap_fee_tier_leadlag_probe_summary_2026-04-11.csv`
   - `/root/clawd/jerry/momentum/reports/artifacts/literature/uniswap_fee_tier_leadlag_probe_detail_2026-04-11.csv`
