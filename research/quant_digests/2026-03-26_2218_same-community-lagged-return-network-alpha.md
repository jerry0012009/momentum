# 别把跨币传染继续只写成“谁先拉谁后跟”：更该先测的是「same-community 均值信号」横截面 raw alpha
- 时间：2026-03-26 22:18 UTC
- 类型：论文（arXiv，全量正文可读）
- 主题类型：raw alpha
- 基础 alpha：同一社区内“其他币”的滞后平均收益，对该币下一期收益有横截面预测力（within-community lagged-return spillover）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha/cross-sectional/relative-value/network/community/lead-lag/inter-crypto-momentum/mean-signal/ranking/crypto/15m/5m/paper
- 证据类型：论文证据（全文源码可读）

## 1. 这次看了什么
这次看的是 **Li Guo, Wolfgang Karl Härdle, Yubo Tao (2021)** 的 arXiv 论文 *A Time-Varying Network for Cryptocurrencies*。

它最值得 desk 拿来试的，不是整套复杂 network science 叙事，而是里面那条**能单独站住的 raw alpha**：

> **先把币按“同社区”分组，再看某个币同社区其他币的刚发生收益；这个组内均值越强，该币下一期越容易继续跟。**

这比继续把跨币 alpha 只写成“BTC 一冲，alts 跟一下”更有价值，因为它给的是**横截面可排名、可做 long-short、可直接变成篮子交易**的信号，不依赖单一 leader coin。

## 2. 核心结论
- **一句话核心结论：** 真正可交易的不是“网络图长得漂亮”，而是**same-community 的滞后收益扩散**本身能做横截面排名 alpha。  
- **一句话它怎么证明：** 作者先用回报交叉预测 + 技术相似性估计动态社区，再做“社区内其他币平均收益 → 下一期收益”的分组排序组合，检验是否有单调收益与持续漂移。  
- 样本来自 `2016-01-01 ~ 2018-12-31`，起点是市值前 `400` 币，筛完后保留 `182` 个币。  
- 论文的 one-day-ahead 结果很硬：Winner 组下一日平均收益 `1.14%`，Loser 组 `0.06%`，Winner-Loser long-short 为 **`1.08%/day`**，`t=12.24`。  
- 排名是单调的：四分位从 Loser 到 Winner 依次是 `0.06% / 0.38% / 0.75% / 1.14%`，说明这不是只靠极端样本撑起来。  
- 2~7 天后没有立刻强反转，后续组合收益大致在 `0.05% ~ 0.16%` 间徘徊，说明它更像**信息扩散延续**，不是隔日噪声回补。  

## 3. 为什么和当前项目有关
- 当前 digest 池里已经有不少 **single leader / common shock / pairs z-score**，但还缺一个**“社区内横截面排名”**的裸骨架。  
- 这条思路天然属于 `cross-sectional / relative value`，能补足近期偏 trend / pairs / funding 的素材池结构。  
- 它还能把 network 这层从“解释学”压回“可下单规则”：**社区只是分桶器，真正下单的是组内 lagged-return score。**  

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值 / long-short
- 基础 alpha：同社区其他资产的滞后收益均值，对本资产下一期收益的扩散预测
- regime：无强单独 regime 设定；社区结构本身随时间滚动更新
- filter / veto：只在 liquid universe 内做；可加最小成交额 / funding 异常 veto
- risk / sizing / execution overlay：原文只给等权 long-short 排名组合；成本、仓位和持有期治理需我们自己补

## 4. 可复刻的最小实验
- **研究假设：** 在 `15m/5m` crypto perpetual 上，若把币先分成 rolling same-community，小币对“组内其他币刚发生的收益”会有 `1~3 bar` 的滞后跟随。  
- **数据源 / 公开性：** Binance Futures 公共 OHLCV 可拿；社区标签可用公开价格数据滚动估计，不依赖私有数据。  
- **最小口径：**  
  1. universe 先用 top `20~40` liquid USDT perps；  
  2. 用过去 `10~30` 天 `15m` 收益构建简化 lead-lag/相关图，月内或周内更新一次 community；  
  3. 对每个币算 `score_i(t) = mean(r_j(t-1), j∈same-community, j≠i)`，做横截面分位排序；  
  4. 下一根 `15m` 开盘 long top quantile、short bottom quantile，持有 `1 / 2 / 3` 根，做等权与 vol-scaled 两版；  
  5. 成本先上 `4/8/12 bps` 梯度，并记录 turnover、post-cost return、positive-day ratio。  
- **下一步怎么测：** 第一轮不要复刻论文的 adaptive Lasso + 技术协变量全套；先做 **`same-community mean score` vs `全市场均值 score` vs `无 community 的 leader-lag score`** 三组 honest A/B，回答“community 分桶到底有没有给 short-cycle alpha 带来增益”。

## 5. 风险与保留意见
- 论文证据是**日频现货大样本**，不是直接在 `5m/15m` perpetual 上验证过；short-cycle 映射后可能被成本打穿。  
- 原文的社区识别较重（adaptive Lasso + 技术相似性 + 动态谱聚类），desk 第一轮必须先用**轻量代理**验证，不然研究成本过高。  
- 若结果只在大波动共同冲击时成立，那它更像 **event-pocket cross-sectional alpha**，不是 all-day 常开主信号。  
- 原文没有给公开 repo，完整复刻的工程摩擦会高于“有代码仓”的候选。  

## 6. 来源
1. **Guo, L., Härdle, W. K., & Tao, Y. (2021). _A Time-Varying Network for Cryptocurrencies_. arXiv preprint.**  
   - Venue: arXiv / working paper  
   - DOI: <https://doi.org/10.48550/arXiv.2108.11921>  
   - Readable URL: <https://arxiv.org/abs/2108.11921>  
   - PDF: <https://arxiv.org/pdf/2108.11921.pdf>  
   - Source archive: <https://arxiv.org/e-print/2108.11921>  
   - Repo URL: `N/A（未见作者公开代码仓）`
2. **Menzly, L., Ozbas, O., & Ozdagli, A. (2010). _Market Segmentation and Cross-predictability of Returns_. Journal of Finance.**  
   - DOI: <https://doi.org/10.1111/j.1540-6261.2010.01580.x>  
   - Readable URL: <https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.2010.01580.x>
