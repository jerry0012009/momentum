# 别把这篇 2024 momentum 论文只读成“crypto 也有 TSMOM”：对 short-cycle desk，更该先测的是「bull-state-only × no-short-veto 的 market TSMOM 壳」这条 raw alpha

- 时间：2026-04-04 22:23 UTC
- 类型：2024 SSRN working paper / AUT 可读全文 PDF source audit（全文方法 + 表格）
- 主题类型：raw alpha
- 基础 alpha：**当 crypto 市场组合在给定回看窗内的收益处于其自身历史分位上三分之一时，只做多市场；跌到下三分之一时默认不做空而是空仓。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/trend/momentum/time-series-momentum/market-portfolio/bull-state-only/no-short-veto/percentile-rank/crypto/binance-futures/15m/5m/3m/1m/paper/public-data/cost/risk
- 证据类型：开放 PDF 全文审计 + 论文表格/方法抽取

## 1. 这次看了什么
这轮主看的是一篇 2024 新 working paper：

- **Chulwoo Han, Byeongguk Kang, Jehyeon Ryu (2024), _Time-Series and Cross-Sectional Momentum in the Cryptocurrency Market: A Comprehensive Analysis under Realistic Assumptions_**
  - Venue：**SSRN Electronic Journal / working paper**
  - DOI：**10.2139/ssrn.4675565**
  - Readable URL：<https://acfr.aut.ac.nz/__data/assets/pdf_file/0009/918729/Time_Series_and_Cross_Sectional_Momentum_in_the_Cryptocurrency_Market_with_IA.pdf>
  - DOI URL：<https://doi.org/10.2139/ssrn.4675565>
  - Repo URL：**未见作者公开 repo**

我最后选它，不是因为“momentum”这词多新，而是因为这篇东西给出的不是泛泛结论，而是一个**能直接写成完整策略壳**的结论：

1. **样本和可交易性约束清楚**：只纳入市值和日成交额都至少 `100 万美元` 的币；做空只在 **Binance futures** 可做空标的上测试。  
2. **成本和风险处理比多数 crypto momentum 文献更老实**：显式计入 **15 bps** 交易成本、按日 mark-to-market、考虑保证金和 liquidation。  
3. **最值钱的不是“多空 momentum 都行”，而是一个很明确的不对称结论**：
   - **市场上行状态下，TSMOM long-only 很强；**
   - **市场下行状态下，short 端大多不赚钱；**
   - **所以更适合 desk intake 的不是 long-short 对称 momentum，而是 bull-state-only 的 long-only 市场趋势壳。**

这符合你本轮的优先级：

> **不是写“crypto 里也有 momentum”这种解释型摘要，而是拆出一条可以独立复现、可直接落地 entry/exit/sizing/risk/cost 的 raw alpha。**

---

## 2. 先回答：这篇东西的 base alpha 是什么？
先把最关键的问题说透。

### 2.1 它的 base alpha 很明确，而且是 raw alpha
这篇最值得我们拿走的 base alpha 不是“cross-sectional winners-minus-losers”，而是：

> **market time-series momentum with bullish-state asymmetry**

翻成人话：

- 先做一个 crypto 市场组合；
- 看这个市场组合在某个回看窗内的收益，放在它自己的历史分布里排分位；
- 如果这个回看收益落在历史的 **上三分之一**，说明市场正处在一个“强趋势/好状态”；
- 此时做多市场；
- 如果落在 **下三分之一**，论文原始 long-short 壳会考虑做空，但结果显示 **short 端大多不值钱**；
- 所以 desk 更该拿走的是：**上三分之一才开 long，其余时间空仓，不做 bad-state short。**

这不是 filter 伪装成 alpha。
它本身就是一条：

- **raw alpha 类型**：trend / momentum / time-series momentum  
- **交易对象**：market portfolio（或 liquid-coin basket）  
- **核心收益来源**：上涨状态下的趋势延续 + 下跌状态下空仓回避大回撤

### 2.2 为什么我不把 cross-sectional momentum 当主 takeaway
论文也测了 XSMOM，但最关键结论恰恰是：

- cross-sectional 多空组合不少会 **liquidate**；
- 收益大多来自 **long leg**；
- **short losers** 在 crypto 里 jump risk 太大，容易把账打穿。

所以如果只问一句“这篇东西里哪条最适合现在的 desk 直接 intake 成完整策略”，我的答案不是 XSMOM，而是：

> **bull-state-only 的 market TSMOM 壳。**

---

## 3. 这篇东西为什么值得优先于继续补别的主题？
因为它刚好补的是我们当前素材池里一个很值钱但经常被写歪的位置：

- 不是又一条“单币 breakout”；
- 不是又一条“pair spread fade”；
- 不是单纯 risk overlay；
- 而是一个**可独立成立的市场级 raw alpha**，并且结论非常 desk-friendly：
  - **long 有 edge**
  - **short 默认别碰**
  - **核心增益来自回撤控制，不是暴力提均值**

这和很多 crypto momentum 材料最大的区别在于：

> **它不是说“多空都能做”；它是在认真计入成本和 liquidation 后，明确告诉你：真正能留到实盘壳里的，是 long-only 的 bullish-state TSMOM。**

对 `1m / 3m / 5m / 15m` short-cycle desk 来说，这特别重要，因为我们最常犯的错之一就是：

- 把趋势信号写成对称 long/short；
- 在 bad-state 强行做空；
- 最后被反抽、jump、手续费和 funding 一起磨掉。

这篇 paper 给的恰好是一个**结构性 veto**：

> **市场坏的时候，默认不是反手做空，而是先别做。**

---

## 4. 论文到底怎么做的

### 4.1 样本与可交易口径
论文使用的基本口径：

- 样本期：**2013-12 到 2023-08**
- 纳入币种条件：
  - **市值 ≥ 100 万美元**
  - **日成交额 ≥ 100 万美元**
- 做空口径：**只在 Binance futures 可做空标的上测试**

这点很关键，因为它已经把“纸面能排到截面里，但实盘压根不好空”的币排掉一层了。

### 4.2 成本与风险假设
这篇 paper 比一般 momentum 文献认真很多的地方在这里：

- 显式假设 **15 bps transaction cost**；
- 按日 **mark-to-market**，不允许只看持有期首尾而忽略中间剧烈波动；
- 考虑 **cross-margin / isolated-margin** 与 liquidation 风险；
- 认为传统的 **mean return t-test** 对 crypto 这种 fat-tail / jump 市场不够，需要看 **mean log return**。

这意味着它不是“学术上显著就算能交易”，而是试图回答：

> **在真实会爆仓、会磨损、会被极端日内跳涨跳跌冲垮的 crypto 市场里，这条策略还剩多少？**

### 4.3 TSMOM 的规则
论文先对不同 look-back / holding 组合做回归，然后在 portfolio analysis 里构造市场 TSMOM：

- 取 market portfolio 的 `j` 日回看收益；
- 把它在历史上做 **time-series percentile rank**；
- 若处于 **top third**：做多市场；
- 若处于 **bottom third**：做空市场；
- 否则：空仓；
- 测试多个 `(j, k)`，其中 `j` 是 look-back，`k` 是 holding period。

论文结论很清楚：

- **好状态里的 long 有效；**
- **坏状态里的 short 大多无效甚至拖后腿。**

---

## 5. 最关键的 5 个数据点

### 5.1 最强信号不是 long-short，而是 `(28, 5)` 的 long-only 市场 TSMOM
在计入 **15 bps** 成本后，论文报告：

- **(28d, 5d) long-only** 年化 Sharpe：**1.51**
- 同期 market portfolio 年化 Sharpe：**0.85**
- `(28,5)` long-only 累计收益：**36,685.8%**
- 同期 market 累计收益：**2,695.9%**
- `(28,5)` long-only 最大回撤：**61.8%**
- 同期 market 最大回撤：**89.1%**

这组数字的含义不是“收益率多夸张”，而是：

> **它主要靠回避大回撤把 Sharpe 拉起来，而不是靠 bad-state 做空去赚额外收益。**

### 5.2 这条 alpha 不是一直开着，而是只在 bullish state 才持仓
论文明确写到：

- `(28,5)` 组合只在样本期 **48%** 的时间持有仓位；
- 这也是它 drawdown 明显低于市场的关键原因。

翻成人话：

> **这不是“永远做多 crypto”策略，而是“市场状态够强才参与”的趋势壳。**

这对 desk 特别有价值，因为它直接给了我们一个思路：

- 市场壳不是 always-on；
- 不是每根 bar 都要有仓位；
- **flat is a position**。

### 5.3 short-only 基本不值钱，long-short 反而被 short 端拖累
论文对 TSMOM 的结论非常不对称：

- short-only 组合几乎都表现差；
- long-short 一般 **弱于** long-only；
- 也就是说：

> **time-series momentum in crypto is concentrated in bullish markets.**

这是本篇最值钱的 desk 结论之一：

- 不要把趋势信号机械对称化；
- **底三分之一不是“理所当然应该开空”的镜像世界。**

### 5.4 cross-sectional momentum 没你想得那么稳
论文对 XSMOM 的结果也很有用，主要用来提醒我们别把赢家-输家多空写得太乐观：

- 选出的 **21** 个 XSMOM 组合里，有 **5 个直接 liquidated**；
- 只有 **6 个** 在 Sharpe 上跑赢 market；
- 成本后表现最好的 XSMOM `(14,7)`：
  - Sharpe **1.28**
  - 累计收益 **101,218.2%**
  - 但 **7 个分散账户里有 3 个被 liquidate**。

也就是说：

> **XSMOM 不是没 edge，但它更像“看起来很香，真加上 jump risk 就开始漏水”的东西。**

### 5.5 论文还给了一个特别重要的结构性提示：收益主要来自 long leg
论文总结非常明确：

- crypto momentum 的利润主要来自 **long leg**；
- short leg 面临高 jump risk；
- 这和 equity 里的很多经典 momentum 画像并不一样。

这意味着我们做 short-cycle transfer 时，默认不该先写：

- `long winners + short losers`

而更该先写：

- `long winners / long market in strong state`
- `short leg 默认 veto`
- 如果要做空，必须有额外 admission layer

---

## 6. 对 short-cycle desk，真正该 intake 的不是“28d/5d 原样照抄”，而是这条重构读法
### 6.1 desk 版主结论
这篇 paper 对我们最值钱的，不是“28 天回看、5 天持有”这个具体参数，而是：

> **市场级 TSMOM 在 crypto 里呈现明显的 bullish-state asymmetry：强状态才做 long，弱状态默认空仓，不要自动开 short。**

换句话说，这篇 paper 真正能迁移到 `1m / 3m / 5m / 15m` 的，不是日频参数本身，而是这三个结构：

1. **time-series percentile rank** 比绝对涨跌幅更稳；
2. **bull-state-only** 比 long-short 对称壳更可交易；
3. **回撤控制** 是收益质量的核心来源。

### 6.2 一个可直接落地的 desk 壳
我会把它压成这样一条短周期最小可复现实验：

#### 信号对象
- `market portfolio`：
  - 方案 A：Binance USDⓈ-M 前 `10~20` 个最活跃 perp 的等权篮子；
  - 方案 B：BTC / ETH / SOL / BNB / XRP / DOGE / ADA / LINK 的 beta 调整等权篮子。

#### 信号定义
以 `15m` 为主时钟：
- 计算市场篮子过去 `L` 根的滚动收益；
- 在过去 `N` 个同长度窗口里做 percentile rank；
- 若 percentile ≥ `0.67`：开多市场篮子；
- 若 percentile ≤ `0.33`：**默认空仓，不做空**；
- 否则：空仓。

#### 第一轮参数网格
用 bar 数而不是天数直接压缩：
- `L ∈ {32, 64, 96, 192}`
- `H ∈ {4, 8, 16, 32}`
- `N ∈ {60, 120, 240}`
- bar 周期：`15m` 主测，`5m` 次测

翻成人话：
- `15m × 96` 大约是 `1 天` look-back；
- `15m × 192` 大约是 `2 天` look-back；
- `H=4/8/16/32` 对应 `1h / 2h / 4h / 8h` 持有期。

#### sizing
- `vol-target` 或固定 notional 都行；
- 第一轮建议：
  - 目标 ex-ante annualized vol：`15%~20%`
  - 单笔最大净敞口：`1.0x`
  - 若只做单边 long，允许用 BTC perp 作为 beta hedge 对照书，但**不是默认版本**。

#### risk / exit
- 时间止盈止损：到 `H` 根自动平；
- 若 percentile 从 `>=0.67` 掉回 `<0.55` 提前平；
- 若入场后 realized vol 急升到过去 `Nvol` 的 `95%` 分位上方，可做风险减半；
- **不因为 `<=0.33` 自动开空。**

#### cost
- maker-first / taker-backup；
- 回测先跑三档：`5 / 10 / 15 bps` 全包成本；
- 单独记录 turnover、持仓占比、胜率、持仓期间 adverse excursion。

---

## 7. 下一步怎么测：直接做 4 本书
这轮最重要的不是继续讨论，而是立刻测。

### 书 A：bull-state-only 市场 TSMOM（主书）
- 周期：`15m`
- `L={64,96,192}`，`H={4,8,16}`
- 条件：percentile `>=0.67` 才 long
- 离场：时间到 or percentile 掉回 `<0.55`
- 目标：验证“只做强状态 long”是否比 buy-and-hold / always-on long 更优

### 书 B：对照书——对称 long-short
- 与书 A 同参数
- 但 percentile `<=0.33` 时开空
- 目标：验证论文结论能否迁移到短周期：**short 端是否持续拖累 Sharpe / hit rate / tail risk**

### 书 C：winner-basket 替代书
- 不做市场篮子，改做 liquid top `10~20` perp 的截面
- 当 market percentile `>=0.67` 时，只买过去 `L` 根 return 前 `20%` 的 winners
- 不 short losers
- 目标：验证“crypto momentum 利润主要来自 long leg”是否能在短周期转成可交易的 winner-only 壳

### 书 D：bad-state flat-vs-short 的纯 veto 试验
- 只在 market percentile `<=0.33` 处比较：
  1. flat
  2. short BTC
  3. short market basket
- 目标：别空谈，直接看 **flat 是否系统性优于 short**

### 第一轮评估指标
除了 PnL / Sharpe，必须额外看：
- 持仓占比
- turnover
- MDD
- 95% worst trade / worst day
- holding-period MAE/MFE
- 盈利是否主要来自少数趋势段
- short side 单独的 skew / kurtosis / tail loss

---

## 8. 我对这条 alpha 的判断
### 8.1 我会把它放进研究池，而且优先级不低
原因很简单：

- **主题类型是 raw alpha，不是纯 filter；**
- **base alpha 清楚；**
- **entry/exit/sizing/risk/cost 都能落地；**
- **最有价值的结构性结论是 asymmetric，刚好适合 desk 避坑。**

### 8.2 但它不是“日频参数直接缩短就能赚钱”
要老实讲，paper 到 desk 还有三层 transfer 风险：

1. **参数选择有 look-ahead bias**  
   论文是先看很多 `(j,k)` 再挑最优组合，这个必须在我们的 walk-forward 里重做。  
2. **原文主时钟是日频，不是 15m**  
   短周期迁移要验证 percentile-state 结构是否保留，而不是默认保留。  
3. **市场组合定义会影响结果**  
   等权、成交额加权、beta 调整、是否含 microcap，都会改信号质量。

### 8.3 但它至少给了我们一个高质量、低歧义的实验起点
相较于很多“讲 momentum 存在”的论文，这篇最好的地方是：

> **它已经很明确地告诉你：short-side 可能是错的，flat 可能比 short 更值钱。**

这对短周期 crypto desk 不是小修小补，而是一个很核心的壳设计差异。

---

## 9. 这篇 paper 里最值得抄下来的 3 句话
如果只允许记 3 句，我会记这 3 句：

1. **Crypto 的 TSMOM 主要存在于 bullish market。**  
2. **真正有用的是 long-only，不是 long-short 对称壳。**  
3. **看 mean return 不够，必须把 transaction cost、mark-to-market 和 liquidation 一起算。**

---

## 10. 结论
一句话版：

> **这篇 2024 paper 最值得 desk intake 的不是“crypto 也有 momentum”，而是「bull-state-only × no-short-veto 的 market TSMOM 壳」：强状态做多，弱状态默认空仓，不把底分位机械翻译成开空。**

如果下一步只做一个最小实验，我会选：

> **Binance liquid perp market basket，`15m` 主时钟，rolling-return percentile `>=0.67` 才 long，`<=0.33` 只 flat 不 short，和对称 long-short 做正面对照。**

这是这篇 paper 里最容易被快速复现、也最可能对当前 short-cycle desk 真有帮助的 raw alpha 部件。

---

## 11. 来源
### 主来源
- Han, Chulwoo; Kang, Byeongguk; Ryu, Jehyeon (2024). **Time-Series and Cross-Sectional Momentum in the Cryptocurrency Market: A Comprehensive Analysis under Realistic Assumptions**. SSRN Electronic Journal. DOI: `10.2139/ssrn.4675565`  
  Readable PDF: <https://acfr.aut.ac.nz/__data/assets/pdf_file/0009/918729/Time_Series_and_Cross_Sectional_Momentum_in_the_Cryptocurrency_Market_with_IA.pdf>  
  DOI URL: <https://doi.org/10.2139/ssrn.4675565>

### 这篇笔记的 desk 化主张
- 主 intake：**bull-state-only market TSMOM long-only shell**
- 明确不主张直接 intake：**bad-state automatic short**
- 明确作为对照而非主书：**cross-sectional long-short winners-minus-losers**
