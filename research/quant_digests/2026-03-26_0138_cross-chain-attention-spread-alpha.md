# 别把跨链负 spillover 只读成宏观相关性：这篇 2026 新论文更该先测的是「leader-chain attention shock → long leader / short rival basket」raw alpha
- 时间：2026-03-26 01:38 UTC
- 类型：2026 arXiv 新论文（全文 PDF 可读）+ Binance Futures 公共 `15m` 最小快检
- 主题类型：raw alpha
- 基础 alpha：**当某条链的代表币在短时间内出现“收益冲击 + 成交放大”的 attention shock，资金更像先集中追逐 leader，而不是全体链币同步等幅上涨；对 desk 最可交易的翻译是做 `long leader / short rival basket` 的 relative-value spread，而不是裸空 rivals**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/relative-value/cross-chain/attention-spillover/leader-laggard/spread/momentum/market-neutral/eth/sol/bnb/avax/arb/binance/perpetual/15m/5m/paper/external-data
- 证据类型：论文全文证据 + 本地公共数据快检

> 先回答 base alpha：**这是 raw alpha，不是 filter。** 它的本体不是“提醒你最近哪条链热”，而是：**当一条链出现 attention shock 时，做多 leader、做空 rival-chain basket，赚的是跨链资本再配置带来的相对收益差。**

## 1. 这次看了什么
主线来源是：

1. **Mengzhong Ma, Te Bao, Yonggang Wen (2026), _One Rising Ship Sinks Other Ships: Cross-Chain Negative Spillovers in Crypto Markets_, arXiv**
2. **论文全文 PDF**（关键在 Table 4 / 6 / 7 / 8 的线性与非线性结果）
3. **Binance USDⓈ-M Futures 公共 `15m` K 线最小快检**（把论文里的“跨链 attention-driven substitution”翻译成 desk 可跑的短周期 spread）

这轮值得 intake，不是因为“跨市场传染/联动”这件事新鲜，而是因为：
- 我们最近已经收了不少 `pairs / stat-arb / cross-sectional / carry`；
- 但 **“跨链资本轮动”** 这条 raw alpha 还没有以一个干净、可执行的骨架进入池；
- 更重要的是，这篇 2026 新论文给的不是泛泛的相关性故事，而是很明确的一句话：**crypto 不只会共振，也会因为 attention reallocation 出现负 spillover。**

对短周期 desk，最值钱的翻译不是复刻论文的 half-day on-chain factor model，而是把它压缩成一句交易话：

> **谁在短时间里变成“全市场最受关注的链”，谁就更可能继续相对强；被它抢走注意力和资金的 rival chains 更可能相对落后。**

## 2. 核心结论
- **一句话核心结论：** 这篇 2026 新论文最适合 desk 的不是“链间负相关”这个学术 headline，而是 **attention shock 之后的跨链 relative-value spread**：`long leader / short rival basket`。
- **一句话证明方式：** 作者用 **Ethereum / Solana / BSC / Arbitrum / Avalanche** 五条链上 **2022-04-28 ~ 2025-03-31** 的 on-chain 资产组合，做 **线性 + 非线性 factor models**，发现某条链资产大涨、链活动/极端收益冲击上来时，其他链资产更容易承受负 spillover。

### 3 个关键数据点
1. **论文不是讲单一 token，而是讲链级别市场组合。** 作者把五条链都构造成 **market-cap weighted chain portfolios**，频率是 **half-day UTC**，样本覆盖 **2022-04-28 ~ 2025-03-31**（含 Arbitrum 的规格多用 `2023-03-17 ~ 2025-03-31`）。
2. **负 spillover 在控制市场因子后依然存在，而且 attention shock 时更强。** 论文写得很直白：
   - Table 4：加入全球股市/利率控制后，**negative return spillovers become even more pronounced**；
   - Table 6 / 7：当其他链更吸引注意力时，负 spillover 更强；例如 **BSC 对 Arbitrum attention 的条件系数 `β31 = -0.204`**；更严格规格下 **Avalanche 在 Arbitrum 更受偏好时 `β42 = -1.368`**；
   - Table 8：极端上涨事件更像 trigger。比如 **Ethereum 投资者会在 Solana / Arbitrum 极端上涨时卖出本链资产**，对应 **`β13 = -0.464`（Solana 极端上行）**、**`β33 = -0.901`（Arbitrum 极端上行）**。
3. **本地 Binance `15m` 代理快检给出的可交易结论不是“裸空 rivals”，而是“做 spread”。** 我用 `ETH / SOL / BNB / AVAX / ARB` 五个链代表币做最小代理，定义过去 `4×15m=1h` 的 leader shock：
   - 若 **leader past-1h return z-score ≥ 2.0**、**1h quote-volume / 自身 4 日中位数 ≥ 1.5**、且 **相对第二名领先 ≥ 1.5%**，样本里有 **423 次事件**；
   - 此时 **未来 4 根 `15m` 的 `long leader / short rival basket` 平均 spread = `+0.8701%`（87.0 bps）**，**胜率 `69.98%`**；
   - 但 **裸空 rival basket 本身平均是 `-0.2677%` 的收益（也就是 short rivals 会亏）**，说明 desk 应该交易 **relative-value continuation**，而不是硬赌“其他链绝对下跌”。

## 3. 为什么和当前项目有关
### 3.1 它补的是一条目前素材池里还不够干净的 raw alpha
我们已经有：
- `BTC → alt delayed follow-through`
- `ETF → BTC lead-lag`
- `theme basket leader→follower spread`
- 多条 `pairs / stat-arb / carry / basis`

但这条的独特性在于：
- 它不是同一链内的 leader-follower；
- 也不是同币跨所价差；
- 它是 **跨链生态之间的 attention substitution**。 

也就是说，它更像一个 **ecosystem-level relative-value lane**。

### 3.2 它还能把“外部链活动数据”降级成可选增强，而不是主依赖
论文里真正的 attention proxy 包括：
- 链活动变量
- native token return
- extreme return dummies

但对 desk 来说，第一轮不需要先把所有 on-chain activity 管道都搭完。只用 **链代表币的价格冲击 + 成交放大**，就能做出最小实验。这样它不是“数据工程大项目”，而是一条今天就能压进复现队列的 raw alpha baseline。

### 3.3 它帮我们修正一个常见误读
如果只读论文 abstract，很容易把它写成：
- “某条链暴涨，其他链会跌”

但本地 tradable proxy 告诉我们更诚实的版本是：
- **leader 更强；rivals 更弱；但 rivals 不一定绝对下跌。**

所以最值得进池的不是 naked short，而是 **market-neutral spread**。

## 4. 策略拆解（必填）
- 方向属性：**relative-value / cross-chain / short-horizon momentum-spread**
- 基础 alpha：**leader-chain attention shock 之后，leader 在接下来 `1h` 内继续相对跑赢 rival-chain basket**
- 更像：**`cross-chain leader continuation spread`**，不是单腿 directional 追涨，也不是经典均值回归 pairs
- regime：
  - 更可能在 **attention dispersion 高**、**单链 narrative 很强**、**成交集中迁移** 的窗口里成立；
  - 若全市场是统一 risk-on / risk-off，大概率会被 beta 共振淹没。
- filter / veto：
  - 只在 **past-1h leader shock z-score** 足够高时交易；
  - leader 必须伴随 **volume expansion**，否则只是普通相对强弱；
  - 若 BTC 在同窗出现极端趋势 bar，可加一层 `btc_event_veto`，防止把“全市场 beta 推升”误判成跨链 substitution。
- risk / sizing / execution overlay：
  - 组合默认 **dollar-neutral**；
  - `long 1 leg + short 2~4 rival legs`，short 侧可按流动性或 inverse-vol 分配；
  - gross exposure 建议先从 `1.0x long / 1.0x short` 开始；
  - per-leg participation cap、资金费率检查、单腿异常滑点 veto 必须写进执行层。

## 5. 可复刻的最小实验
### 研究假设
当一条链代表币在过去 `1h` 里成为显著 leader，且同时伴随放量，这更像 attention shock，而不是普通随机波动；此时最该测的不是“其他链会不会马上大跌”，而是 **leader vs rival basket 的未来 `1h` spread**。

### 一个可计算定义（本轮已快检）
Universe：`ETHUSDT / SOLUSDT / BNBUSDT / AVAXUSDT / ARBUSDT`

每个 `15m` bar 收盘时：
1. 计算每个代表币过去 `4` 根 `15m` 的累计收益 `ret_4`；
2. 找出当前 `leader = argmax(ret_4)`；
3. 计算 leader 自身的 shock 强度：
   - `lead_z = (ret_4 - rolling_mean_384) / rolling_std_384`
   - `vol_ratio = past-1h quote volume / rolling_median_384`
4. 只在以下条件开仓：
   - `lead_z >= 1.5` 或更严格 `>= 2.0`
   - `vol_ratio >= 1.5`
   - `leader ret_4 - second ret_4 >= 1.0%~1.5%`
5. 持有未来 `4` 根 `15m`：
   - **主版本：`long leader / short equal-weight rivals`**
   - 对照版本：`short rivals only`

### 本轮 public-data 快检结果
样本：**2025-01-01 ~ 2026-03-25，Binance USDⓈ-M Futures 公共 `15m` K 线**

1. **全样本无门槛**（42,716 个 `15m` 观察点）：
   - `long leader / short rivals` 平均未来 `1h` spread = **`+14.40 bps`**
   - 胜率 = **`61.04%`**
2. **attention-shock 版本**：`lead_z >= 1.5`、`vol_ratio >= 1.5`、`lead_gap >= 1.0%`
   - 事件数 = **954**
   - 平均未来 `1h` spread = **`+63.30 bps`**
   - 胜率 = **`68.24%`**
3. **更强 shock 版本**：`lead_z >= 2.0`、`vol_ratio >= 1.5`、`lead_gap >= 1.5%`
   - 事件数 = **423**
   - 平均未来 `1h` spread = **`+87.01 bps`**
   - 胜率 = **`69.98%`**
   - 但 rival basket 自身未来 `1h` 平均仍是 **`+26.77 bps`**，所以 **`short rivals only` 不诚实，spread 才是对的**

### leader 分解（`z>=1.5 & vol>=1.5 & gap>=1.0%`）
- `SOL` 作为 leader：平均 spread **`+83.27 bps`**，胜率 **`71.67%`**
- `ETH` 作为 leader：平均 spread **`+89.47 bps`**，但仅 **34** 次事件，样本少
- `ARB` 作为 leader：平均 spread **`+64.53 bps`**
- `AVAX` 作为 leader：平均 spread **`+51.99 bps`**
- `BNB` 作为 leader：平均 spread **`+49.18 bps`**

## 6. 风险与保留意见
- 论文本身是 **half-day on-chain chain-portfolio** 研究，不是直接为我们验证过 `15m perp spread`；所以本轮只是 **transfer candidate**，不是“论文已直接帮我们实盘背书”。
- 本地最小快检用的是 **5 个大链代表币**，而不是论文里的全链上资产组合，实际上是一个 **proxy of proxy**。好处是易交易，坏处是生态代表性有限。
- 快检说明了一个很重要的坑：**不要把“negative spillover”误读成“rivals 一定绝对下跌”。** 在 Binance perp 上，更靠谱的是 **leader relative outperformance**。
- 这条线天然会和 **市场 beta / narrative event / listing news / airdrop** 混在一起；若不加 BTC 或 total-market beta 过滤，可能只是在做单腿追强。
- 多腿 spread 虽然毛边厚，但也更吃执行：腿数越多，滑点、资金费率、仓位同步、借币/合约可交易性就越重要。

## 7. 下一步怎么测
1. **先把 5-leg 代理压缩成 3-leg 交易版。** 只保留流动性最好的 `ETH / SOL / BNB / AVAX`，做 `1 long + 2 shorts`，看看 `net of realistic cost` 还能剩多少。  
2. **补 beta-hedged honesty test。** 对主 spread 回归 `BTCUSDT` 与 crypto market proxy，确认赚的不是简单 beta continuation。  
3. **把 `15m→15m` 扩成 `5m signal / 15m execution`。** `5m` 负责更早发现 leader shock，`15m` 负责降频执行，测试能否保留边同时减少换手。  
4. **显式接入公开链活动数据。** 第二轮再加 `DefiLlama / Artemis / Dune / Coingecko on-chain activity proxies`，测试 `price-shock only` vs `price + activity` 谁更好。  
5. **检查事件拥挤窗口。** 按 token launch / airdrop / upgrade / meme narrative 爆发日分层，看这条线到底是常态 alpha，还是只在高 attention dispersion 日特别厚。  

## 8. 来源
1. **Ma, M., Bao, T., & Wen, Y. (2026). _One Rising Ship Sinks Other Ships: Cross-Chain Negative Spillovers in Crypto Markets_. arXiv.**  
   - Authors: Mengzhong Ma, Te Bao, Yonggang Wen  
   - Year: 2026（paper 内部日期 Sep 17, 2025；arXiv v1 发布于 2026-02-27）  
   - Venue: arXiv / q-fin.PR  
   - DOI: `10.48550/arXiv.2602.23762`  
   - Readable URL: `https://arxiv.org/abs/2602.23762`  
   - PDF URL: `https://arxiv.org/pdf/2602.23762v1.pdf`  
   - Repo URL: `N/A`
2. **Binance Developers – USDⓈ-M Futures Kline/Candlestick Data**  
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

## 9. 外部数据说明（若后续做增强版）
- 论文主要依赖的外部数据：**链级 on-chain 资产价格、native token returns、staking reward rates、极端收益 dummy**
- 公开性：**公开可得**（论文使用 Coingecko API、链上数据、全节点/QuickNode 重建等路径）
- 更新频率：论文主回归是 **half-day UTC**；对 desk 的最小实验可先降级成 **代表币价格 + 成交量的 `15m`/`5m` proxy**
- 最小可复现实验口径：
  - **不依赖私有数据**
  - 先用 Binance perp 的链代表币代理 attention shock
  - 第二轮再把链活动变量作为 filter / state enhancement 接回去

## 10. 本地产物
- `research/quant_digests/2026-03-26_0138_cross-chain-attention-spread-alpha.md`
- `reports/artifacts/quant_digests/cross_chain_negative_spillover_20260326/summary.csv`
- `reports/artifacts/quant_digests/cross_chain_negative_spillover_20260326/leader_breakdown.csv`
- `reports/artifacts/quant_digests/cross_chain_negative_spillover_20260326/event_panel.csv`
- `tmp_cross_chain_negative_spillovers_2026.pdf`
- `tmp_cross_chain_negative_spillovers_2026.txt`
