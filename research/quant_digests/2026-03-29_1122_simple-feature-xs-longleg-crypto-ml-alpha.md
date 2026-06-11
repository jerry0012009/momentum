# 别把 2024 crypto ML 论文读成“模型越复杂越好”：对 desk 更该先测的是「simple-feature XS combo × top-quintile-long」raw alpha
- 时间：2026-03-29 11:22 UTC
- 类型：2024 *International Review of Financial Analysis* 论文 accepted manuscript 全文 + Crossref 元数据 + Binance USDⓈ-M Perpetual 公共 `15m` 最小 transfer check
- 主题类型：raw alpha
- 基础 alpha：**横截面 simple-feature 评分**——用少数简单特征（近期 alpha / momentum / 流动性摩擦 / 价格层级）给币排序，做多预测分数最高的一组、做空最低的一组；对 desk 更值得先测的旁支是 **top-quintile-long / beta-light**，而不是默认把 short leg 当对称镜像。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/relative-value/machine-learning/forecast-combination/simple-features/long-leg/top-quintile/liquidity/limits-to-arbitrage/market-neutral/beta-light/binance/perpetual/15m/5m/1m/3m/paper/public-data/cost
- 证据类型：accepted manuscript 全文证据 + Binance Futures 公共 `15m` transfer check

## 1. 这次看了什么
这次主看的是 **Nusret Cakici, Syed Jawad Hussain Shahzad, Barbara Będowska-Sójka, Adam Zaremba (2024), _Machine learning and the cross-section of cryptocurrency returns_**，发表在 **International Review of Financial Analysis**。

先直接回答这篇东西的 **base alpha**：

> **不是“上更复杂的模型”。真正的 base alpha 是：crypto 横截面里，少数简单特征已经能把“更可能跑赢的币”和“更可能跑输的币”分开。**

这篇 paper 对当前 desk 最有价值的地方，不是教你把整个研究流程做成更黑箱的 ML pipeline，而是两句更实用的话：

1. **复杂度收益有限**——把一堆模型平均起来确实最好，但真正驱动预测力的，主要还是少数简单特征；
2. **收益主要来自 long leg**——横截面更像 `L-shaped`，不是“多头和空头都同样强”。

翻成人话：

> **别默认“crypto XS alpha = 一定要对称 long-short + 更复杂模型”。这篇 2024 论文更支持的，是“simple-feature 排名先把 strongest names 挑出来”，再决定 short leg 要不要做、怎么做。**

## 2. 核心结论
### 2.1 一句话版本
**这篇 paper 真正值得 desk 复用的，不是“机器学习能预测 crypto”，而是：crypto 横截面 alpha 未必需要复杂模型；少数简单特征的组合已经有料，而且盈利主要来自 top bucket，而不是 bottom bucket 的稳定崩塌。**

### 2.2 论文主口径在做什么
作者的研究骨架很清楚：
- 样本：**2017~2023**，覆盖 **500+ major coins/tokens、250+ exchanges**
- 特征：复现 **40 个 crypto characteristics**
- 数据源：
  - **CryptoCompare**：OHLC / volume
  - **CoinMarketCap**：市值
  - **IntoTheBlock**：链上活动
- 训练流程：
  - extending training window：**175 天**
  - validation：**75 天**
  - test：**接下来 1 周**
  - 每周滚动重估
- 模型族：PCA/PLS、LASSO、Elastic Net、Random Forest、GBRT、FFNN 等
- 最终组合：把不同模型的输出再做 **forecast combination**

但 paper 自己给出的结论非常重要：

> **虽然组合模型最好，但 return predictability 的大头，主要还是来自一小撮简单特征。**

### 2.3 论文里最该记住的数字
先看 headline：
- **forecast combination long-short**：平均 **`2.37%/周`**
- 年化 Sharpe：**`1.66`**
- three-factor alpha：**`2.42%/周`**

再看 desk 更该记住的结构性信息：
- 预测力主要来自少数简单特征：**market price、past alpha、illiquidity、momentum**
- **long leg 主导**：横截面是 **L-shaped**，**top quintile** 的 alpha 很亮眼，其他 bucket 普通，说明 short side 不是同样强的镜像
- 信号 **不算很长寿**：把预测 horizon 拉长、把调仓频率降到 **2 周**，盈利通常要掉 **接近 30%**
- 成本不小：交易成本平均会吃掉 **超过一半** 的 long-short payoff，但大多数模型**成本后仍有剩余**
- alpha 明显更集中在 **small / illiquid / volatile** 的难交易币上
- limits-to-arbitrage 分层里，高限制组显著更肥：例如 aggregate `lim` 高组的等权 long-short 平均收益约 **`2.54%/周`**，低组约 **`0.73%/周`**

翻成人话：

> **这不是一篇“越花哨越有 alpha”的论文；它反而是在说，crypto 横截面还远没卷到只能靠复杂模型赚钱，但真正肥的那部分 alpha，大多长在更难交易的位置。**

## 3. 为什么和当前项目有关
这篇东西值得进当前 digest，不是因为我们又缺一篇 generic ML 论文，而是因为它正好给最近几条主线补两块空白：

### 3.1 它补的是“aggregation”，不是再补一个单点因子
最近素材池里我们已经有很多：
- 单一动量 / 反转 / MAX / volume shock / time-of-day
- short-leg veto / inverse-vol / regime gate 这类策略层修补

这篇 paper 的价值在于：

> **它告诉我们，下一步未必要先找更 exotic 的新特征；也可以先把已有的简单特征做成一个横截面组合分数。**

### 3.2 它补的是“leg attribution”
我们最近几篇 cross-sectional digest 一直在问：
- 是 long leg 不行，还是 short leg 在拖后腿？
- 是 alpha 本体坏了，还是组合层失真？

这篇 2024 paper 给了一个很具体的答案：

> **在 crypto 里，ML 聚合后的横截面收益主要来自 top bucket，而不是 bottom bucket 的稳定塌陷。**

这对 desk 很重要，因为它直接影响我们该先测：
- `top bucket long / short bottom`，还是
- `top bucket long / beta hedge`，还是
- `top-bottom symmetric long-short`

### 3.3 它也提醒我们：别把论文 gross 直接宣传成 liquid-perp alpha
论文最肥的收益，集中在更小、更 illiquid、更 volatile 的币上。

这意味着：
- **它对“alpha 是否存在”是强支持**；
- 但对“这个 alpha 能不能直接无损移植到我们 liquid perps”并不是强支持。

所以它更像：
- 一个值得 intake 的 **raw alpha family**；
- 外加一个明确的现实提醒：**liquidity segmentation 不能省。**

## 3.5 策略拆解（必填）
- 方向属性：**cross-sectional / relative-value**
- 基础 alpha：**少数 simple features 组合后的横截面排序，预测下一期 winners vs losers**
- 论文主口径：
  - features：**40 个 crypto characteristics**
  - estimation：**175d train + 75d validation + next-week test**
  - cadence：**每周重估 / 每周测试**
  - portfolio：**按预测分数分组，long 最高组 / short 最低组**
  - sizing：**文中重点展示 value-weighted 组合，亦有 equal-weight 分析**
  - risk：论文也显式讨论 limits-to-arbitrage / downside / transaction cost
- 对 desk 的短周期翻译：
  - `raw alpha layer`：先把**近期收益 / 残差 alpha / liquidity proxy**做成横截面组合分数
  - `portfolio layer`：优先比较 **top bucket long**、**top bucket long + beta hedge**、**top-bottom long-short** 三种结构
  - `risk layer`：liquidity gate、单币权重上限、turnover throttle
  - `cost layer`：必须和 rebal cadence 一起看，不能先看 gross 再补成本

## 4. 这篇最值得先复用的点
如果只从这篇 paper 里偷一件东西，我不会先偷“更多模型”，而会先偷这个：

> **simple-feature XS combo + long-leg-first attribution。**

原因很简单：
1. **这是 paper 里最可 desk 化、最便宜的部分**；
2. 它直接服务当前素材池：把很多单点 signal 汇成一个组合分数；
3. 它迫使我们先回答一个更实际的问题：
   - **short leg 到底是 alpha 的一半，还是只是一个容易失真的附属层？**

所以对当前 desk，更合理的顺序不是：
1. 先追更复杂模型；
2. 再想组合落地；

而是：
1. **先做 simple-feature 排名**；
2. **先拆 long leg / short leg attribution**；
3. **再决定要不要上更复杂 stacking / nonlinear ML**。

## 5. Binance Futures 公共 `15m` transfer check
我做了一个很轻的 `15m` transfer check。目的不是硬复刻论文的周频 ML，而是只测它最值得 desk 先搬的那条主线：

> **“simple-feature 横截面排名 + 先看 long leg 是否比 full long-short 更诚实。”**

### 5.1 口径
- 数据：**Binance USDⓈ-M Futures 公共 `15m` K 线**
- 样本：**2026-01-14 11:00 UTC ~ 2026-03-29 10:00 UTC**
- Universe：**20 个 liquid USDT perpetual**
  - `BTC ETH SOL XRP BNB DOGE ADA LINK LTC AVAX SUI DOT AAVE BCH UNI NEAR ATOM TRX ETC FIL`
- 每次只保留 **近 24h quote volume 前 15 名**，避免把 paper 的“小币肥 alpha”直接误抄成 liquid-major 结论
- simple-feature score（只保留最便宜、最容易快复现的价格侧特征）：
  - 过去 **1h** 收益
  - 过去 **4h** 收益
  - 过去 **24h** 相对全市场平均收益的残差 alpha
  - 三者做简单 z-score 加总
- 调仓：**每 1h**
- 持有：**未来 1h**
- 组合：**long top 3 / short bottom 3** 等权；同时单独看 long leg 和 top-bucket-vs-market

### 5.2 结果
#### 直接 long top bucket
- gross mean：**`-5.94 bps / rebalance`**
- hit-rate：**`44.5%`**
- gross cumulative：**`-67.3%`**

#### short bucket 的原始 forward return
- short bucket 自身未来收益：**`-1.22 bps / rebalance`**
- 这意味着：如果你 short 它们，short leg 本身是**有一点贡献**的

#### full long-short
- gross mean：**`-4.72 bps / rebalance`**
- hit-rate：**`42.8%`**
- gross cumulative：**`-57.6%`**

#### top-bucket vs market（更接近 beta-light long 的读法）
- gross mean：**`-3.38 bps / rebalance`**
- gross cumulative：**`-45.5%`**

#### turnover
- long bucket membership turnover：约 **`0.69` / rebalance**
- short bucket membership turnover：约 **`0.67` / rebalance**

### 5.3 进一步 parameter sweep
我又顺手扫了一圈更慢的 formation / holding：
- formation：大致 **1h ~ 72h**
- holding：大致 **1h ~ 8h**
- cadence：1h 或 4h 级别

结果很一致：

> **在这段 2026Q1 的 liquid-major `15m` pocket 里，paper 这条“simple-feature XS combo”做 direct sign transfer，long-only 不活，long-short 也不活。**

最好的一组 long-short 也仍是负的，约在 **`-4.4 ~ -4.7 bps / rebalance`** 这一带。

### 5.4 这组快检怎么解读
这组 proxy 最值得记住的，不是“paper 错了”，而是：

1. **周频、小币、难交易 segment 里的 alpha，并不会自动压缩成 liquid-major `15m` alpha。**
2. 这篇 paper 强调的 **long-leg dominance**，在当前这段 liquid-major 样本里并没有直接继承下来。
3. 说明这条思路更像：
   - 一个**中低频 cross-sectional composite 家族**；
   - 或一个更慢 cadence 的 ranking layer；
   - 而不是立刻能按 `15m`/`1h` 高频率收租的现成口袋。

翻成人话：

> **别把这篇 paper 的“ML 有效”直接翻译成“liquid perp 每小时重排就能赚钱”。当前数据更像在提醒我们：这个 alpha 的原生 habitat 比我们 desk 当前测试的 pocket 更慢、更脏、也更不对称。**

## 6. 风险与保留意见
1. **我做的不是原论文的完整 40 特征复刻。**
   这里故意只取了最 cheap 的 price-side features，因为当前目标是找“先做什么最值钱”，不是先搭 full ML infra。
2. **liquid-major universe 可能过于干净。**
   论文里最肥的收益，本来就更集中在更小、更 illiquid 的币；而我这里为了 desk 可交易性，主动做了 liquidity gate。
3. **当前样本是 2026Q1 单一窗口。**
   这段市场状态可能天然不适合顺着周频 cross-sectional winner ranking 压缩到 15m。
4. **perp 口径还没扣 funding cashflow。**
   不过因为 gross 已经显著为负，这一层目前不是主要矛盾。

## 7. 下一步怎么测
### 7.1 先别继续加模型复杂度，先加 cadence 对照
优先做：
- bar：`15m`
- rebalance：`4h / 8h / 24h`
- hold：`4h / 8h / 24h`

要先回答：
> **这条 simple-feature combo 是不是只是在“每小时太快”时被噪音与成本打烂。**

### 7.2 把 universe 明确分层
至少分 3 层：
1. **top liquidity majors**
2. **mid-cap liquid alts**
3. **更宽但仍可交易的尾部 perps**

因为 paper 的关键信息本来就是：
> **alpha 更肥的地方，通常也是更难交易的地方。**

### 7.3 不要默认只做 symmetric long-short
下一轮必须并排跑：
1. **top bucket long only**
2. **top bucket long + market / beta hedge**
3. **top-bottom long-short**
4. **short-only loser basket**

要看的是：
- `leg attribution`
- `after-cost spread pnl`
- `top bucket standalone drift`

而不是先假设 short leg 一定和 long leg 对称。

### 7.4 再决定要不要往“更完整组合分数”扩展
如果更慢 cadence 里开始看到边，再逐步加：
- funding / basis
- OI / liquidation proxy
- on-chain activity
- spread / volatility / microstructure friction proxy

顺序应该是：
> **先确认 cadence 和 universe 对不对，再加 feature richness。**

## 8. 研究结论（给自己留一句话）
**这篇 2024 IRFA 对当前 desk 最值钱的，不是“要上更复杂 ML”，而是“先把少数简单特征做成 XS combo，并且先拆清楚收益到底来自 long leg 还是 short leg”。**

但当前 `15m` liquid-perp quick check 也提醒得很直白：

> **这条 alpha 的 paper habitat 明显比我们测试的 pocket 更慢、更脏、更偏向难交易币；所以它值得进 raw-alpha 素材池，但不该被误写成“已经完成短周期 transfer”。**

## 9. 来源与链接
- **Authors**：Nusret Cakici, Syed Jawad Hussain Shahzad, Barbara Będowska-Sójka, Adam Zaremba
- **Year**：2024
- **Title**：*Machine learning and the cross-section of cryptocurrency returns*
- **Venue**：*International Review of Financial Analysis*
- **DOI**：`10.1016/j.irfa.2024.103244`
- **DOI URL**：https://doi.org/10.1016/j.irfa.2024.103244
- **Readable URL（accepted manuscript handle）**：https://open.icm.edu.pl/handle/123456789/25543
- **Visual companion / strategy explorer**：https://azaremba.shinyapps.io/Cryptocurrency_machine_learning/
- **Working paper / SSRN**：https://doi.org/10.2139/ssrn.4295427
- **Repo URL**：无公开官方 repo（至少本轮未发现）