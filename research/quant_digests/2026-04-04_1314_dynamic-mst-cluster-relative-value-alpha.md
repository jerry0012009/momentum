# 把 2026 DM-MSTP clustering paper 改写成短周期可交易的「dynamic MST cluster-relative value」raw alpha

- 时间：2026-04-04 13:14 UTC
- 类型：paper-branch
- 主题标签：raw-alpha/cross-sectional/relative-value/stat-arb/cluster-mean-reversion/mst/correlation-network/dynamic-universe/binance-perpetual/15m/5m/3m/1m/paper/public-data/cost/risk
- 证据类型：2026 open-access paper full text + 文内参考文献链路 + desk-oriented transfer spec

- 主题类型：raw alpha
- 基础 alpha：**同一动态相关性簇内部，短周期的相对超涨/超跌会比跨簇偏离更快回归；做法是只在同簇里做 leader-vs-laggard 的 residual mean reversion。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次看了什么
这次主材料不是一篇直接给出 intraday strategy backtest 的论文，而是一篇 **2026 年刚发表、目前还没进现有 digest 索引** 的 crypto clustering 论文：它用相关系数矩阵 → 距离矩阵 → minimum spanning tree（MST）→ 聚类，把 35 个币分成少数几个结构簇。对我们真正有用的，不是它的“组合优化” headline，而是它提供了一个**可复现的、能直接服务于短周期 relative-value / cross-sectional alpha 的分组骨架**。

结合最近学习进展看：最近几轮已经补了很多 pairs / cointegration / maker / carry / microstructure，但“**先怎么把 universe 分簇，再只在同簇里做残差交易**”这层还不够系统。这篇 paper 正好补这个组件层，而且能直接转成 `5m/15m`，甚至压到 `3m/1m` 的最小实验。

## 2. 论文里最值得记住的 4 个点
1. **样本与口径**：论文用 CoinMarketCap 的 **35 个 crypto**，时间从 **2018-11-01 到 2025-09-01**，频率是**月度**收盘价。
2. **核心构造**：先算相关矩阵，再转成距离矩阵，然后用 **DM-MSTP** 生成最小生成树；文中给出的整棵树总距离是 **31.424**。
3. **结构事实**：文中明确写到 **BTC-ETH 相关系数约 0.76**；稳定币 **USDT / USDC / DAI** 会形成一个很紧的低波动簇。
4. **四簇视角**：作者最终采用 **4 个 cluster** 来描述市场结构：稳定币簇、BTC/XMR/BCH 这类“成熟 core”簇、ETH/DOGE/XLM/SOL 这类高交易/高 beta 簇，以及 AAVE/PEPE/OKB 等更偏创新/DeFi/exchange-token 的簇。

这些点本身不是 alpha，但它们告诉我们一件很重要的事：**“谁和谁该被拿来比较” 不能只靠肉眼，也不该只靠全市场统一阈值。**

## 3. 为什么它能被改写成 raw alpha，而不只是 filter
如果只停在论文原文，这篇更像 `clustering / portfolio-construction tool`。但对 desk 来说，更值钱的旁支想法是：

> **别在全市场乱做 mean reversion；只在“同一动态相关性簇”内部，做 residual spread 的 leader-laggard 回归。**

这就把论文里的 `cluster map`，转成了一个可以单独交易的 raw alpha：

- 不做“BTC 和 random meme coin”的伪 relative-value；
- 只做**同簇资产**之间的相对偏离；
- 先让 MST / cluster 帮你定义可比组，再在组内做 `z-score / residual`；
- 这会比全市场 cross-sectional reversal 更接近“真正可比”的残差回归。

所以它不是纯 filter，而是一个**能独立成策略**的 raw alpha 候选。

## 4. 最小可复现实验：直接翻成 15m / 5m 版本
### 4.1 Universe
- 标的：Binance USDⓈ-M 或 Hyperliquid 上 **20~40 个最活跃 perp**。
- 先排除：稳定币锚定类、明显断档/新上市样本不足的标的。
- 建议起步池：`BTC ETH SOL XRP ADA DOGE LINK AVAX LTC BCH DOT TON SUI NEAR AAVE UNI TRX XLM ETC HYPE`。

### 4.2 动态分簇
- bar：先做 `15m`，再压到 `5m`。
- rolling window：
  - `15m`：过去 **14 天**（约 `14*24*4=1344` bars）
  - `5m`：过去 **7 天**（约 `7*24*12=2016` bars）
- return：log return。
- 相似度：Pearson correlation。
- 距离：`d_ij = sqrt(2 * (1 - rho_ij))`。
- 构图：对距离矩阵做 MST；然后切成 **3~4 个 cluster**，默认先试 `K=4`，因为这和论文的最终读法一致。

### 4.3 raw alpha 定义
对每个 cluster 内的每个资产 `i`：
1. 先算 cluster benchmark：`r_cluster,t = equal_weight(return of peers in same cluster)`
2. 定义残差：`resid_i,t = r_i,t - beta_i * r_cluster,t`
   - beta 可以先简化成 `1`
   - 第二版再换成 rolling OLS beta
3. 对残差做 rolling z-score：
   - `15m` 先试 `lookback = 96`（约 1 天）
   - `5m` 先试 `lookback = 288`（约 1 天）
4. 交易规则：
   - `z_i >= +1.75`：做空该币，同时在同簇里做多最弱的 1 个或 cluster basket
   - `z_i <= -1.75`：做多该币，同时在同簇里做空最强的 1 个或 cluster basket

本质就是：**同簇 leader-laggard spread 不追趋势，先赌 residual 回归。**

## 5. 我建议的第一版完整策略壳
### 5.1 Entry
- 仅在 cluster size `>= 3` 时开仓；太小的簇不做。
- 仅在该币与 cluster 的 rolling corr `>= 0.35` 时开仓；否则说明“同簇名义成立，但短期同步性不够”。
- `|z| >= 1.75` 入场。
- 若 cluster 当下 1h realized vol 处于过去 30 天 **前 10%**，暂停开新仓；避免把结构性 break 当成均值回归。

### 5.2 Exit
- 主止盈：`z` 回到 `0 ~ 0.35`。
- 时间止损：
  - `15m`：`12~16` bars
  - `5m`：`24~36` bars
- 结构止损：若该币在最新一次重算 cluster 时**换簇**，直接平仓。
- 价差止损：`|z|` 从入场后继续扩大 **0.9~1.1** 个 z 单位则止损。

### 5.3 Sizing
- 每条 spread 目标波动率一致化：按 spread 过去 20 天 realized vol 做 inverse-vol sizing。
- 单 cluster 风险上限：组合 NAV 的 `20%~25%`。
- 单资产 notional cap：组合 NAV 的 `8%~10%`。
- 同时活跃持仓条数先限制在 `4~8` 条，防止“看似分散，实则都押在同一个 beta shock 上”。

### 5.4 Cost
- 默认按 perp taker+taker 双边先估；如果能 maker 进、taker 出，再做第二版。
- 第一版必须记录：
  - spread crossing cost
  - funding carry（若持仓跨 funding 结算）
  - cluster rebalance turnover
- 这类 alpha 很容易**gross 有 edge，net 被 turnover 吃掉**，所以 turnover/holding-time 要和 PnL 一起看，不要只看 Sharpe。

## 6. 这篇 paper 真正给我们的启发
### 启发 1：先分簇，再做 residual，比“全市场统一反转”更像正经 stat-arb
全市场 cross-sectional reversal 最大的问题是：你把不同风格、不同 beta、不同交易人群的币硬塞进一个 ranking。MST cluster 至少给了一个比“拍脑袋分组”更有依据的 universe partition。

### 启发 2：cluster 变化本身也可以当 regime 信号
如果某个币频繁换簇，或者某个 cluster 在短时间内从紧密变松散，那通常意味着：
- regime 变了；
- 这时候 continuation 可能比 mean reversion 更占优；
- 或者至少应该把 reversal size 降下来。

### 启发 3：它同时服务至少两类 raw alpha
这套动态分簇不只服务这一条 residual MR：
1. **cluster-internal mean reversion**（本文主推）
2. **cluster-relative momentum / leader continuation**（当 cluster breadth 明显单边时）

所以就算第一版 residual MR 结果一般，这篇东西也不会白看。

## 7. 下一步怎么测
### A. 最小实验（优先）
- 数据：Binance USDⓈ-M `15m` klines，最近 180 天。
- Universe：20 个主流 perp。
- 每天/每 4 小时重算一次 MST + 4 clusters。
- 组内 residual z-score 进出场。
- 先只看：
  - 胜率
  - 平均持仓时长
  - 单笔毛利 / 单笔净利
  - turnover
  - cluster 内/cluster 外对照

### B. 关键对照
1. **同簇 residual MR** vs **全市场 residual MR**
2. **动态 cluster** vs **静态人工 sector bucket**
3. `K=3` vs `K=4`
4. `equal-weight cluster benchmark` vs `beta-adjusted cluster benchmark`

### C. 快速失败条件
如果出现以下任一情况，可以尽快判弱：
- 扣成本后显著转负；
- `15m` 有效但 `5m` 明显崩掉，且不是 sample size 问题；
- 换簇频率过高，导致策略等于在追噪音；
- 所谓 alpha 其实只是 BTC beta 的伪装。

## 8. 我对这篇材料的判断
这篇 paper 的 headline 其实偏 **结构识别 / 组合优化**，不是现成的 intraday alpha 论文；但它给了我们一个目前研究池里还不够完整的拼图：

**用可复现的 MST / cluster 方法，先定义“谁应该和谁比较”，再在组内做 short-cycle relative value。**

如果你让我在当前 desk 里排优先级，我会把它放在：
- 不是最高优先级的“拿来即跑”论文，
- 但属于**非常值得补进素材池**的结构件，
- 尤其适合服务后续的 `pairs / relative value / cross-sectional mean reversion` 这三条线。

一句话版：

> **这篇 2026 clustering paper 最值得抄的，不是它的组合优化结论，而是把它改写成“dynamic MST cluster → 同簇 residual MR”的短周期 raw alpha。**

## 9. 来源与链接
1. **Dhouib, S., Ezzine, H., Abdelhedi, M., Ellouz, S., & Chabchoub, H. (2026). _Clustering cryptocurrencies market through the innovative DM-MSTP method_. Frontiers in Blockchain, 9, 1744921.**
   - Venue: *Frontiers in Blockchain*
   - DOI: https://doi.org/10.3389/fbloc.2026.1744921
   - Readable URL: https://www.frontiersin.org/journals/blockchain/articles/10.3389/fbloc.2026.1744921/full
   - PDF: https://public-pages-files-2025.frontiersin.org/journals/blockchain/articles/10.3389/fbloc.2026.1744921/pdf

2. **Mantegna, R. N. (1999). _Hierarchical structure in financial markets_. European Physical Journal B, 11, 193–197.**
   - Venue: *The European Physical Journal B*
   - DOI: https://doi.org/10.1007/s100510050929
   - 用途：MST / correlation-network 地基文献。

3. **Jing, R., & Rocha, L. E. C. (2023). _A network-based strategy of price correlations for optimal cryptocurrency portfolios_. Finance Research Letters, 58, 104503.**
   - Venue: *Finance Research Letters*
   - DOI: https://doi.org/10.1016/j.frl.2023.104503
   - 用途：crypto 相关性网络在投资组合/结构识别中的直接前作。
