# 别把 fixed-major universe 里的坏分数，当成 XS momentum 家族失效：这篇 2026 FRL 更该先留作「survivor-universe falsification card」
- 时间：2026-03-28 10:10 UTC
- 类型：2026 Finance Research Letters 论文摘要页 + Crossref/OpenAlex 元数据 + Binance USDⓈ-M Perpetual 公共 `15m` desk proxy
- 主题标签：raw-alpha/cross-sectional/momentum/survivorship-bias/universe-design/control-card/liquidity/admission/market-neutral/wml/weekly/15m/5m/1m/3m/paper/external-data
- 证据类型：论文摘要证据（主）+ 本地最小 desk proxy（辅）

- 主题类型：raw alpha
- 基础 alpha：**横截面 momentum（winner-minus-loser / cross-sectional long-short）**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否

## 1. 为什么这轮值得写它
这篇 2026 FRL 不适合被误读成“又一篇周频因子论文”，因为它真正戳中的，是我们 desk 很容易犯的一个**研究流程错误**：

> **用固定幸存大币（fixed majors / survivor coins）去代表整个 crypto momentum 宇宙，然后再据此下结论。**

这件事为什么值得在现在写？因为最近几轮 intake 里，`XS momentum / trend / relative-strength` 已经越积越多；如果不把**universe 构造**这张控制卡补上，后面很容易出现两种错：

1. **假阴性**：在固定大币里测不出来，就误判“这条 alpha 家族不行”；
2. **假阳性**：在回看式挑出来的幸存样本里测出点边，就误判“这条 alpha 稳定可移植”。

对短周期 desk 来说，这篇最有价值的，不是直接给我们一条 `5m` 可上线策略，而是告诉我们：

> **以后凡是做 crypto momentum / reversal / trend cross-section，fixed-major universe 只能当 control group，不能当唯一战场。**

## 2. 这篇论文到底说了什么
主文献是：

- **Grobys, K., Sandretto, D., & Äijö, J. (2026). _On survivor cryptocurrency momentum_. Finance Research Letters, 92, 109602.**
- DOI：`10.1016/j.frl.2026.109602`

按 ScienceDirect 摘要与 highlights，这篇做的是一个很直接、也很 desk 化的问题：

### 2.1 它看哪类币
作者先定义了一组 **survivor coins**：
- **9 个 free-floating cryptocurrencies**
- 它们在样本期内都持续留在 **top 100 altcoins by market capitalization** 里
- 样本期：**2017-01 ~ 2024-08**
- 频率：**weekly**

然后作者拿这组“活到最后、一直还算主流”的币，去做 crypto 版的 momentum 组合。

### 2.2 它对照什么
论文对照了两类 momentum：

1. **SCMP（survivor cryptocurrency momentum portfolio）**
   - 只在幸存币上做 momentum；
2. **plain cryptocurrency momentum**
   - 每年使用更宽的、当年较大的币集合（摘要写的是 **largest 30 coins for a given year**）。

### 2.3 论文结论
摘要和 highlights 里最该记住的是这 4 句：

1. **SCMP does not generate significant payoffs.**  
   也就是：**幸存币动量本身，并没有显著 payoff。**

2. **SCMP does not leverage a plain momentum strategy based on a broader set of coins.**  
   翻成人话：**宽宇宙里的 plain momentum，不是靠 survivor 这批大币在发力。**

3. **Plain cryptocurrency momentum is profitable only after the dataset is trimmed.**  
   也就是：更宽宇宙下的 momentum 只有在做过 trimming 之后才显得 profitable。

4. **Significant payoffs documented for momentum strategies are an artefact of coins that are only temporarily accessible for trading.**  
   这句最关键。作者的意思很接近：**很多看上去漂亮的 crypto momentum payoff，可能来自那些“只在某段时间能交易”的币，而不是来自稳定存活的大币核心。**

所以这篇的主信息不是“再证明一次 momentum 存在/不存在”，而是：

> **crypto momentum 的研究结论，对 universe 构造高度敏感。**

## 3. 这篇东西的 base alpha 是什么
一句话先答题：

> **base alpha 就是横截面 momentum：买过去表现较强的币，卖过去表现较弱的币。**

所以它不是：
- 纯解释型综述；
- 纯 filter；
- 纯 overlay；
- 纯 survivorship bias 方法论文章。

它研究的仍然是 **raw alpha 家族本体**，只是它告诉我们：

> **这条 raw alpha 的结论，不能脱离宇宙构造单独谈。**

换句话说，这篇对 desk 的价值，不在于“给一个更 fancy 的信号”，而在于给 momentum 家族补一张：
- **研究 admission card**
- **universe falsification card**
- **control-group sanity check**

## 4. 为什么它和当前短周期 desk 直接相关
### 4.1 我们最容易偷懒的地方，就是 fixed majors
做 `1m / 3m / 5m / 15m` 研究时，最方便的样本往往是：
- BTC / ETH / SOL / XRP / ADA / DOGE / LINK / LTC / AVAX / BNB

问题是，这组东西：
- 数据最干净；
- 容量最好；
- 存活性最强；
- 也最容易让人误以为“这就是整个 crypto 可交易宇宙”。

而这篇论文的提醒刚好相反：

> **如果你只看 survivor majors，你看到的不是“crypto momentum 全貌”，而更像是“幸存大币 momentum 的一个特例”。**

### 4.2 这会怎么误导短周期研发
它至少会误导 3 件事：

1. **误判 alpha 家族是否存在**  
   fixed-major 里没边，不代表 broad/dynamic universe 没边；

2. **误判边来自哪里**  
   你以为边来自大币趋势，实际上可能来自中腰部资产的 churn、attention、temporary accessibility；

3. **误判 short leg 的意义**  
   很多 crypto momentum/reversal 的胜负手，不在 long winner，而在 short loser / weak cohort 的构造。

这和我们最近几轮 intake 是对得上的：
- 一旦 universe 收得太窄，很多 `XS momentum / XS reversal / relative-value` 都会被测成“只剩 BTC beta 或完全没边”；
- 但 universe 放得太野，又会把 listing bias、流动性幻觉、cost cliff 一起放进来。

所以这篇最该落在当前 desk 的位置是：

> **不是直接当 alpha recipe，而是当“以后谁都不能跳过的 universe control card”。**

## 5. 本地最小 desk proxy：把 fixed survivors 和更宽 liquid universe 放到同一条 15m XS momentum 骨架里，会怎样？
为了把这件事尽量拉近到我们当前频率，我做了一个**很轻的 desk proxy**，不是 faithful 复现论文：

### 5.1 口径
- 数据：Binance USDⓈ-M Perpetual 公共 `15m` K 线
- 样本：最近约 **90 天**
- survivor universe（固定 10 币）：
  - `BTC ETH BNB SOL XRP ADA DOGE LTC LINK AVAX`
- plain universe（更宽 current liquid set）：
  - 按当前 24h quote volume 取 **top 30 active USDT perpetuals**，再做基础数据可用性过滤
- 信号：过去 **24h return** 排名
- 持有：未来 **1h（4 根 15m bar）**
- 组合：等权 long top 20%，short bottom 20%
- 成本：每次 rebalance 粗略记 **8 bps round-turn bundle cost**

### 5.2 结果
#### fixed survivor 10 币
- 有效 rebalances：**727**
- 平均每次换仓净收益：**-10.7 bps**
- hit rate：**40.0%**
- 累计净值：**-54.6%**
- pseudo Sharpe：**-16.4**

#### current liquid top 30
- 有效 rebalances：**1642**
- 平均每次换仓净收益：**-19.2 bps**
- hit rate：**48.8%**
- 累计净值：**-99.4%**
- pseudo Sharpe：**-3.94**

### 5.3 这组 proxy 该怎么读
先说结论：**这组 15m price-only momentum proxy 对两种 universe 都不成立。**

但它仍然有 3 个有用信息：

1. **survivor majors 并不是天然更稳的 XS momentum pocket。**  
   fixed-major universe 也一样可以把这类简单 WML 测成负的。

2. **把 universe 直接放宽，不会自动救活 plain momentum。**  
   尤其在 `15m` 上，价格排序本身很容易被换手和短噪音吃掉。

3. **对短周期来说，plain price-only momentum 更像控制组，不像最终策略。**  
   真要做，得叠加：
   - short-leg veto
   - relative-volume / participation filter
   - trend composite / technical compression
   - session pocket / crowding gate

所以这组 proxy 没有推翻论文，也没有复现论文；它更像在短周期语境里补了一句：

> **别指望“只换 universe、不改信号结构”就把 intraday XS momentum 救活。**

## 6. 我现在对它的 desk 定位
我的判断是：**值得进研究池，但要明确标成“universe falsification / control card”，不是主 raw alpha recipe。**

它服务的，不是“再找一条新信号”，而是下面这个更基础的问题：

> **我们以后怎么诚实地判定 momentum 家族到底有没有边。**

具体说，这篇最适合服务 3 类后续主题：

1. **XS momentum raw alpha**  
   比如 volume-adjusted momentum、technical composite momentum、same-slot momentum；

2. **XS reversal / loser-basket alpha**  
   因为很多时候真正稳定的不是 winner continuation，而是 loser leg 的挤兑/反打；

3. **relative-value / pair-admission universe design**  
   它提醒我们：固定大币样本和动态可交易样本，研究结论可能完全不是一回事。

## 7. 现在最值得偷的，不是论文 headline，而是 4 条研究纪律
### 7.1 fixed-major universe 只能当 control，不能当唯一主结论
以后写 `XS momentum / trend / reversal`，至少要并行给出：
- fixed majors control
- dynamic liquid universe
- optional churn-heavy universe

### 7.2 明确区分“可交易的 broad universe”和“回看式幸存样本”
如果用的是今天还活着的币回看过去，基本默认带 survivorship 问题。

### 7.3 long leg / short leg 要拆开看
这篇 FRL 的启发之一是：**payoff 可能不是来自你以为的那一侧。**
短周期里尤其要拆：
- long winners
- short losers
- neutral basket
- beta-neutral residual

### 7.4 broad universe 的正结果，必须追问是不是 temporary-accessibility artifact
即使测出边，也要问：
- 是不是只靠短寿命热点币？
- 是不是 listing 初期 attention 冲击？
- 是不是容量极差、实盘不可拿？

## 8. 下一步怎么测
这篇最重要的是“下一步怎么把它变成 honest test rig”。

### 实验 A：三层 universe A/B/C
在同一条短周期 XS momentum 骨架上，同时跑：
1. **A：fixed majors**（幸存大币对照）
2. **B：rolling liquid top-N**（按当期流动性动态更新）
3. **C：rolling liquid top-N，但去掉新上市冷启动窗口**

目标：回答边到底来自：
- 幸存大币；
- 普通 liquid universe；
- 还是新币 / 临时可交易币的 churn。

### 实验 B：同 universe，下钻到 long/short attribution
对每个 universe 单独拆：
- long-only winners
- short-only losers
- long-short spread

目标：回答短周期里到底是哪一侧在贡献净边。

### 实验 C：给 price-only momentum 只加一层结构化增强
不要一上来叠 5 层；先只加 1 层：
- `relative-volume` 或
- `short-leg veto` 或
- `technical composite score`

看哪层最能把 `plain price-only momentum` 从 control 变成 candidate。

### 实验 D：把“universe 构造”写入所有后续 digest 模板
以后凡是写 `XS raw alpha`，默认都回答：
- fixed or dynamic universe?
- current survivors or historical constituents?
- liquidity floor?
- listing age floor?

## 9. 风险与保留意见
- 主论文证据当前主要来自 **ScienceDirect 摘要页 + 元数据**，不是全文逐节细读。
- 我做的 `15m` proxy 只是 desk translation，不是 paper replication。
- 当前 top-30 current-liquid universe 里混入了高 turnover 新热点合约，说明**动态宇宙本身也需要更严格 admission**。
- 所以这篇不能被写成“momentum 不存在”或“dynamic universe 一定更好”；它真正提供的是：
  - **fixed-survivor universe 不够**；
  - **broad-universe 结果必须追问 temporary-accessibility artifact**。

## 10. 一句话结论
如果要把这篇压缩成一句 desk 话：

> **别再拿固定幸存大币去给整个 crypto XS momentum 家族判死刑或判无罪；它最多是 control group，不是最终法庭。**

## 11. 来源
1. **Grobys, K., Sandretto, D., & Äijö, J. (2026). _On survivor cryptocurrency momentum_. Finance Research Letters, 92, 109602.**
   - DOI：https://doi.org/10.1016/j.frl.2026.109602
   - Readable URL：https://www.sciencedirect.com/science/article/pii/S1544612326001339
   - Repo URL：N/A

2. **Grobys, K., Sandretto, D., & Äijö, J. (2025). _Cryptocurrency momentum has (not) its moments_. Financial Markets and Portfolio Management, 39, 443–471.**
   - DOI：https://doi.org/10.1007/s11408-025-00474-9
   - Readable URL：https://link.springer.com/article/10.1007/s11408-025-00474-9
   - Repo URL：N/A

3. **Fieberg, C., Liedtke, G., Poddig, T., Walker, T., & Zaremba, A. (2025). _A Trend Factor for the Cross Section of Cryptocurrency Returns_. Journal of Financial and Quantitative Analysis, 60(7), 3116–3153.**
   - DOI：https://doi.org/10.1017/S0022109024000747
   - Readable URL：https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/trend-factor-for-the-cross-section-of-cryptocurrency-returns/4C1509ACBA33D5DCAF0AC24379148178
   - Repo URL：N/A

## 12. 本地产物
- `reports/artifacts/quant_digests/survivor_crypto_momentum_20260328_1003/summary.json`
- `reports/artifacts/quant_digests/survivor_crypto_momentum_20260328_1003/nav_compare.csv`
- `reports/artifacts/quant_digests/survivor_crypto_momentum_20260328_1003/survivor_last50_picks.csv`
- `reports/artifacts/quant_digests/survivor_crypto_momentum_20260328_1003/plain_last50_picks.csv`
