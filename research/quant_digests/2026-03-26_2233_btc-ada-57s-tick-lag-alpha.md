# 别把跨币 lead-lag 继续写成“谁先动谁后跟”：这篇 2023 开放获取论文更该先钉住的是「57 秒 BTC→ADA tick-lag」1m/3m raw alpha
- 时间：2026-03-26 22:33 UTC
- 类型：2023 开放获取论文（全文 PDF 可读）
- 主题类型：raw alpha
- 基础 alpha：BTC 的价格变化会在大约 `1` 分钟内传到 ADA；当 BTC 已发生显著冲击而 ADA 同步反应不足时，可做 ADA 对 BTC 的 catch-up spread
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha/cross-crypto/lead-lag/tick-data/seconds-scale/relative-value/stat-arb/btc/ada/1m/3m/paper
- 证据类型：开放获取论文证据（全文 PDF 可读）

## 1. 这次看了什么
先回答 base alpha：**这次最该拿走的不是“BTC 是龙头”这句废话，而是更可交易的那句——BTC 对 ADA 的 lead-lag 在 tick 级大约只有一分钟量级，所以 `BTC 先冲、ADA 同向欠反应` 本身就是一个可以在 `1m/3m` 上快测的 raw alpha 候选。**

主材料是 **Bing Anderson (2023)** 的开放获取论文 *A tick-by-tick level measurement of the lead-lag duration between cryptocurrencies: The case of Bitcoin versus Cardano*。它的价值不在于再证明一次“Bitcoin leads alts”，而在于把这个 lag **量化到秒**：不是几小时，不是几根 `15m`，而是 **`16~118` 秒，均值约 `56.5` 秒**。

这对当前 desk 的意义非常直接：如果 lag 只有几十秒，那它就不是 `15m` 主信号，而更像 **`1m/3m` 高强度 catch-up / spread` pocket`**；反过来，如果我们在公开数据上已经看不到这类秒级 pocket，就该尽快判定“这条线已被现代市场结构压扁”，而不是继续把跨币 lead-lag 当成宽泛叙事。

## 2. 核心结论
- **一句话核心结论：** 这篇论文真正给 desk 的，不是“BTC 领先 ADA”这种方向判断，而是**BTC 对 ADA 的可交易 lead time 大致只有 1 分钟量级**。  
- **一句话它怎么证明：** 作者不用低频 bar，而是直接拿异步 tick-by-tick 交易数据，在 Bitcoin 与 Cardano 之间插入一个人工时间间隔 `X`，看当 `X` 增大到多大时，BTC 更早一段价格变化对 ADA 下一次价格变化的解释力消失。  
- 数据来自 **FirstRateData** 提供的 tick 数据；Cardano 原始样本覆盖 `2018-02 ~ 2021-05`，但因 `2018` 年成交太稀疏，正式分析使用 **`2019-01 ~ 2021-05` 共 `29` 个月**。  
- 为减少数据不均衡，作者最后只保留 **HitBTC** 的交易数据做主分析；原因是大多数月份里 Cardano 在 HitBTC 的成交明显多于 Kraken。  
- 估出来的 **BTC→ADA lead time** 月度范围是 **`16` 秒到 `118` 秒**：  
  - 最短：`2020-10` 的 **`16` 秒**  
  - 最长：`2020-01` 的 **`118` 秒**  
  - 均值：**`56.5` 秒**  
  - 中位数：**`62` 秒**  
  - 标准差：**`26` 秒**  
- 论文还发现这个 lag 在样本期内**显著缩短**：  
  - Pearson 相关：**`-0.4747`**，`p=0.0093`  
  - Spearman rho：**`-0.4601`**，`p=0.0120`  
  - Kendall tau-b：**`-0.2900`**，`p=0.0294`  
  翻成人话：**越往后，ADA 对 BTC 的反应越快。**  
- 作者还测了月度 seasonality，但**没看到稳健显著的季节性**。  
- 论文给了一个很好的“秒级边界”示例：在 `2020-01`，当人工 gap `X=118s` 时，回归里更早一段 BTC 收益项仍显著；到 `119~120s` 左右就不再稳健，故把该月 lag 估成 **`118` 秒**。

## 2.5 方法翻成人话
原文最值钱的方法点，是它没有粗暴把 tick 数据塞进固定 1 分钟或 5 分钟 bar。作者做法可以翻成：

1. 先盯住 **ADA 下一次真正发生价格变化** 的那一跳；
2. 回头看这次 ADA 变动之前，BTC 最近两段有效价格变化；
3. 在“更早那段 BTC 变化”和“这次 ADA 变化”之间，强行插入一个人工空档 `X` 秒；
4. 如果即便隔开 `X` 秒，更早那段 BTC 变化仍然能解释 ADA 下一跳，说明真正 lead time 至少还有这么长；
5. 一旦 `X` 增大到某个阈值以后，这个解释力消失，就把那个阈值附近当成 lead-lag 持续时间。

用论文里的回归写法，就是：

`r_C = α + β1 r_B(-1) + β2 r_B(-2) + ε`

其中关键不在公式本身，而在于 **`r_B(-2)` 被人工隔到了 `X` 秒之前**。作者再用 `10s` 网格 + 逐步缩小区间，把 lag 缩到秒级估计。

## 3. 为什么和当前项目有关
- 我们最近已经积累了不少 **`5m/15m` lead-lag / spillover / network`** 题材，但真正能服务 **`1m/3m` 高强度 raw alpha`** 的“明确时长估计”还不够多。  
- 这篇论文的价值，在于把 lead-lag 从“宏观上谁带谁”压缩成了一个更可执行的问题：**如果 edge 只有几十秒，我们就该用更快的 event-driven / spread 思路，而不是把它误当成慢速方向因子。**  
- 它还能帮我们区分两件事：  
  1. **有没有可交易 lag；**  
  2. **这个 lag 是不是已经快到只剩 execution alpha，而不是 bar-close alpha。**

## 3.5 策略拆解（必填）
- 方向属性：cross-crypto / relative-value / statistical-arbitrage / long-short
- 基础 alpha：BTC 先发生价格冲击，ADA 在接下来约 `1` 分钟内同向补动；若 ADA 当下反应不足，则做 ADA catch-up
- regime：更适合 leader-follower 结构清晰、BTC 仍是显著价格发现中心、且 follower 流动性足够的时段
- filter / veto：只做 **BTC 冲击显著** 且 **ADA 同步欠反应** 的事件；避免重大新闻瞬间、极端点差扩张、连续重叠信号
- risk / sizing / execution overlay：优先做 **long ADA / short β·BTC** 的 spread 版本，而不是裸做 ADA 方向；仓位应按 follower 波动与盘口深度限额；超短持有必须把手续费和滑点显式入账

## 4. 可复刻的最小实验
- **研究假设：** 在公开可得的现代交易所数据上，BTC 对 ADA 的 lead-lag 虽然大概率比论文时代更短，但在 `1m/3m` 里仍可能留下一个“BTC shock → ADA 欠反应补动”的 pocket。  
- **原论文数据源 / 公开性：** 原文用的是 **FirstRateData 的付费 tick 数据**，主分析落在 **HitBTC**，因此**原始数据并非完全公开可免费复现**。  
- **当前可公开复现实验口径：** 第一轮直接用 **Binance Spot/Futures 公共 aggTrades 或 `1s` / `1m` 数据**，先测 BTCUSDT 与 ADAUSDT；若成，再扩到 BTC 对 ETH/SOL/DOGE 等 follower。  
- **最小口径：**  
  1. 用公开 tick/aggTrades 重采样成 `1s`；  
  2. 计算 BTC 最近 `30/60/90s` 冲击收益，以及 ADA 同窗收益；  
  3. 估一个滚动 `β`，构造 `gap_t = β·ret_BTC - ret_ADA`；  
  4. 当 `|ret_BTC|` 位于过去 `1~3` 天同类窗口的高分位、且 `gap_t` 同号显著时，开 **long laggard / short leader**；  
  5. 持有 `60/90/120/180s`，以及 bar 化后的 `1/2/3` 分钟版本；  
  6. 先比较三组：  
     - `裸做 ADA 方向`  
     - `ADA vs β·BTC spread`  
     - `1m bar-close proxy`  
  7. 成本先上 **`2/4/6 bps` round-trip（spot 代理）**，perp transfer 另跑 **`4/8/12 bps`**。  
- **下一步怎么测：** 第一轮不要急着扩 universe；先老老实实回答三个问题：  
  1. **秒级 lag 到了 `1m` bar 还有没有残留 edge？**  
  2. **edge 来自 ADA 自身补动，还是只是 BTC beta 暴露？**  
  3. **2025~2026 现代市场结构下，这条线是不是已经被手续费 + 更快 price discovery 压到只剩 paper edge？**

## 5. 风险与保留意见
- 论文只研究 **一对资产（BTC/ADA）**，不是全市场 follower basket；可迁移性不能默认。  
- 原始样本来自 **`2019~2021` 的 HitBTC tick 数据**，与现在主流 CEX、主流 perp 的撮合速度和参与者结构差异很大。  
- 论文量化的是 **lead time**，不是已经扣完成本、定义完退出、做完容量评估的完整策略；因此它更像**raw alpha 候选 + execution 研究起点**。  
- 论文发现 lag 随时间显著缩短，这反而提示我们：**今天的真实 lag 很可能比 `56.5s` 更短。** 若公开数据上只能在秒级存在、到 `1m` 就消失，那这条线对当前 desk 的意义会降级为“micro execution pocket”，而不是主交易引擎。  
- 若不做 `β` 对冲，信号很容易被误读成“BTC 涨、ADA 也涨”的市场 beta 跟随，而不是独立 relative-value alpha。  

## 6. 来源
1. **Anderson, B. (2023). _A tick-by-tick level measurement of the lead-lag duration between cryptocurrencies: The case of Bitcoin versus Cardano_. Investment Management and Financial Innovations, 20(1), 174-183.**  
   - DOI: <https://doi.org/10.21511/imfi.20(1).2023.15>  
   - Journal page: <https://www.businessperspectives.org/index.php/journals/investment-management-and-financial-innovations/issue-437/a-tick-by-tick-level-measurement-of-the-lead-lag-duration-between-cryptocurrencies-the-case-of-bitcoin-versus-cardano>  
   - PDF: <https://www.businessperspectives.org/images/pdf/applications/publishing/templates/article/assets/17735/IMFI_2023_01_Anderson.pdf>  
   - Repo URL: `N/A（未见作者公开代码仓）`
