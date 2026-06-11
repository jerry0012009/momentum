# 别把这篇 2021 dynamic-factor 论文只读成“又一个协整篮子”：对 short-cycle desk，更该先测的是「BTC-like common-trend strip × second-factor residual basket fade」这条 raw alpha
- 时间：2026-04-11 07:56 UTC
- 类型：论文
- 主题类型：raw alpha
- 基础 alpha：`common-trend stripped second-factor residual mean reversion / basket stat-arb` —— 先把篮子里的共同大趋势（论文里基本就是 BTC-like market factor）剥掉，再去做**第二因子驱动的相对错位回归**；赌的不是单币方向，而是**多腿 residual basket 会向因子均衡回摆**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha / stat-arb / basket / dynamic-factor / common-trend / second-factor / residual / mean-reversion / market-neutral / crypto / btc / eth / ltc / xmr / binance-perpetual / 15m / 5m / paper / fulltext / public-data / cost / risk
- 证据类型：2021 *Decisions in Economics and Finance* 开放获取全文 + 原文 Table 3/4/5/6 + Binance USDⓈ-M `15m` portability probe（本地 proxy）

## 1. 先回答：这篇东西的 base alpha 是什么？
一句话：
**base alpha = 把共同趋势因子剥掉以后，做第二因子主导的 residual basket mean reversion。**

翻成人话：
- 不是赌 BTC 涨跌；
- 不是简单挑一对 cointegration pair 做固定 z-score；
- 而是先承认整个 crypto 篮子有一个**共同大趋势**，再把这个趋势从各资产里剥掉；
- 剥完以后，剩下那条更像“相对价值 / 风格偏离”的第二因子，如果还是均值回归的，就可以反着做。

所以它的归类是清楚的：
- `raw alpha`：**是**
- `relative-value / stat-arb / market-neutral`：**是**
- `filter / regime / overlay`：**不是 alpha 本体，但论文里的“第二因子仍然 stationary 才交易”是很关键的 admission layer**

## 2. 这篇论文到底看了什么
来源信息先摆清楚：
- **Authors**：Gianna Figà-Talamanca, Sergio M. Focardi, Marco Patacca
- **Year**：2021
- **Title**：*Common dynamic factors for cryptocurrencies and multiple pair-trading statistical arbitrages*
- **Venue**：*Decisions in Economics and Finance*
- **DOI**：`10.1007/s10203-021-00318-x`
- **Readable URL**：<https://link.springer.com/article/10.1007/s10203-021-00318-x>
- **PDF URL**：<https://link.springer.com/content/pdf/10.1007/s10203-021-00318-x.pdf>
- **Repo URL**：未见作者公开配套 repo

论文原始样本是：
- 资产：`BTC / ETH / LTC / XMR`
- 频率：**日频**
- 样本：`2016-01-01` 到 `2019-11-30`
- 训练 / 测试：前三年估计，`2019-01` 到 `2019-11` 做策略评估

作者不是只说“crypto 有协整”，而是更进一步：
**这个 4 资产篮子，在 2019 年 8 月前后之前，更像“一个 integrated factor + 一个 stationary factor”的二因子系统。**

## 3. 原文里最值钱的不是“协整”两个字，而是“共同趋势剥离后再做第二因子”
### 3.1 论文先确认：篮子不是四条各走各的线
原文 Table 3 给的 Johansen test 结果是：
- `r=0`：stat `105.0086` > c value `40.1751`
- `r=1`：stat `57.8639` > c value `24.2747`
- `r=2`：stat `15.7722` > c value `12.3206`
- `r=3`：p value `0.6356`

这等价于说：
**4 条价格序列有 3 条 cointegrating relationships，也就是 1 条共同 integrated trend。**

这一步很关键，因为它不是“随便找两条相关高的币”，而是先承认：
**大部分价格漂移其实是共同行情因子。**

### 3.2 一因子不够，要补第二因子
作者先拟合一因子，再看残差协方差矩阵特征值：
- `(1184763.89, 6946.14, 185.03, 14.32)`

因此他们判断：
**一条共同趋势不够，至少还需要第二个有效因子。**

最后定下来的结构就是：
- `f1`：integrated I(1) 因子
- `f2`：第二因子；在 2019 年 8 月底前大体 stationary，之后转坏

### 3.3 第一因子基本就是 BTC-like common trend
原文 Table 4 参数：
- `β11 (BTC on factor1) = 0.9911`
- `β21 (ETH) = 0.0700`
- `β31 (LTC) = 0.0170`
- `β41 (XMR) = 0.0260`

论文还明确写到：
**第一因子 essentially emulates the dynamics of Bitcoin。**

也就是说，这里最像 desk 语言的解读其实是：
- `f1` ≈ 市场共同大趋势 / BTC-like beta
- `f2` ≈ 脱离共同趋势之后的次级相对错位因子

这就是它和“普通 pair spread”最不一样的地方。

### 3.4 真正可交易的是“按 β1 缩放后的价差”
论文第 4 节把价格按 `βi1` 缩放：

`p*i,t = p_i,t / β_i1`

这样处理后，每个缩放价格都可以写成：
- 同一个共同 integrated factor `f1`
- 再加一个由 `βi2 / βi1` 决定暴露的第二因子 `f2`
- 再加 idiosyncratic noise

于是任意两资产的 scaled spread：
- **共同趋势项会互相抵消**
- 剩下主要由第二因子和噪音驱动

翻成人话：
**不是直接做原始 price spread，而是先 strip 掉共同市场 beta，再做 residual spread fade。**

这条思路比“相关高 → pair → z-score”更像一个真正能扩展成 basket stat-arb 的壳。

## 4. 论文原始策略怎么做
论文的单步逻辑其实挺直接：
1. 用 rolling window 估参数；
2. 预测下一期 `f2`；
3. 由此得到各资产 one-step-ahead forecasted scaled prices；
4. **做多 forecasted scaled price 最低的两只，做空最高的两只**；
5. 如果第二因子不再 stationary，或者因子相关性过高，就不交易。

论文给的例子（Table 5）里，排序后策略动作是：
- **short：BTC、ETH**
- **long：LTC、XMR**

所以它不是一条固定 pair，而是：
**共同趋势剥离后的 rank-based 多腿 mean reversion / stat-arb。**

## 5. 原文里最值得记住的几个数字
### 5.1 第二因子在 2019 年 8 月前更像 stationary alpha driver
OpenAlex 摘要和正文都指向同一个结论：
- **直到 2019 年 8 月底前**，篮子更像 `1 integrated + 1 stationary factor`
- 之后更像 `2 integrated factors`

论文正文还写得很直白：
- **2019-08-20 之后**，rolling Johansen test 开始支持 `two common integrated factors`
- 因子相关性也上升
- 因此**不再建议交易**

这对 desk 很重要：
**第二因子是不是还 stationary，本身就是 admission layer，而不是事后解释。**

### 5.2 Table 6：原文策略不是玩具，至少日频上是能挣钱的
Table 6 给了不同 no-trade 常数 `c` 下的 summary：

`c = 0.20`（作者认为更合理，兼顾费用后更优）时：
- Trade n.：`222`
- `G_{τ+M}` mean：`7623.34`
- `G*_{τ+M}` mean（含 0.10% 交易费）：`3032.97`
- `G*_{τ+M}` st.dev.：`2598.39`

文中还明确说：
- `c=0` 时 cumulative gain 最大
- 但**考虑手续费后**，`c=0.20` 更像合理选择
- **9 月以后几乎没交易**，因为模型前提坏了

所以这篇东西不是纯理论文章；它至少给了一条：
- entry
- ranking / pair selection
- no-trade band
- regime admission
- transaction fee discussion

都比较完整的原始壳。

## 6. 为什么它不是“又一篇和现有 cointegration pairs 重复”的旧题
表面上它也在做 market-neutral / spread fade，容易被误判成“和已有 pairs digest 差不多”。

但我觉得它真正新增的点有 3 个：

### 6.1 它先显式拆共同趋势，再谈 residual alpha
很多 pairs / basket stat-arb 文章默认：
- 先找到协整关系
- 再做 spread z-score

而这篇更像：
- 先承认 crypto 有一个 BTC-like common trend
- 再把这个 trend strip 掉
- 真正拿来交易的是**第二因子主导的 residual 错位**

这比“裸 spread mean reversion”更接近 factor-neutral stat-arb。

### 6.2 它天然是 basket 思维，不是固定 pair 思维
原文虽然最后落到多腿 long-short，但底层不是固定 pair，
而是**整个篮子的因子结构**。

这对当前 desk 的价值在于：
- 不一定非得找一对 coin 长期死绑；
- 可以先找“共同趋势很强的液态篮子”，
- 再从第二因子上拆 residual trade。

### 6.3 它自带一个非常明确的 regime stop-rule
这篇东西最能落到 desk 的一句其实不是“trade spread”，而是：
**当第二因子不再 stationary，就停。**

这比很多 pairs repo 里的固定 z-score / 固定半衰期规则更干净。

## 7. 我做的 short-cycle portability probe：先看它能不能翻到 Binance `15m`
### 7.1 probe 口径（注意：这是 desk-friendly proxy，不是全文 faithful replication）
因为论文原始是日频 + Bayesian dynamic factor / state-space 估计，
我先做一个**最小 desk proxy**，看它有没有 short-cycle 素材价值：

- 市场：Binance USDⓈ-M perpetual 公共 klines
- 资产篮子：`BTCUSDT / ETHUSDT / LTCUSDT / SOLUSDT`
  - 说明：原文的 `XMR` 在当前 Binance 永续不可直接照搬，所以我用 `SOL` 做可交易替代，重点保留“共同 market factor + 次级 residual factor”这个结构，而不是硬复刻原资产集合
- 频率：`15m`
- 样本：`2025-11-12 08:00 UTC` 到 `2026-04-11 07:45 UTC`
- 训练窗：`10d` rolling
- 因子 proxy：rolling PCA 两因子
  - 第一主成分近似 `common trend`
  - 第二主成分近似 `residual factor`
- stationarity-like proxy：第二因子 AR(1) half-life 落在可交易区间
- 信号：当第二因子 z-score 偏离足够大时，按第二因子暴露做**demeaned dollar-neutral basket fade**
- 持有：测试 `4 / 8 / 12 bars`

产物：
- `reports/artifacts/literature/dynamic_factor_shortcycle_probe_2026-04-11.csv`
- `reports/artifacts/literature/dynamic_factor_shortcycle_probe_2026-04-11.json`

### 7.2 probe 先给结论：alpha 结构还在，但 naive intraday 执行太薄
如果用 `10d` 训练、half-life 上限 `200 bars` 的宽松 proxy：
- 有效评估点：`13,436`
- stationarity-like share：`85.84%`
- `z >= 1.0` 时信号数：`5,432`

但问题是：
- **`4-bar` 持有 gross mean 只有 `+1.06 bps/trade`**
- **`8-bar` 持有 gross mean `+2.02 bps/trade`**
- **`12-bar` 持有 gross mean `+2.59 bps/trade`**

也就是说：
**共同趋势剥离后的第二因子 fade，在 `15m` 上不是完全失效，但 naive trade 太薄，直接 taker 化基本不行。**

### 7.3 更强偏离会更好，但还没强到“完整策略可直接上线”
把 entry 提高到更极端的 `|z| >= 1.75`：
- 信号数：`1,708`
- `4-bar` gross mean：`+2.01 bps/trade`
- `8-bar` gross mean：`+3.67 bps/trade`
- `12-bar` gross mean：`+5.07 bps/trade`
- `12-bar` win rate：`56.8%`

这说明什么？
- **alpha 不是没有**；
- 真正有效的是**更极端的 residual 偏离**；
- 但如果你给它一个粗暴的 `20 bps` round-trip 成本假设，它还是过不了。

所以我对这轮 probe 的结论是：
**它是“可独立复现的 raw alpha 候选”，但还不是“当前 desk 可直接拿来完整部署的 finished strategy”。**

### 7.4 这个 proxy 里，第一因子和第二因子的经济含义也基本没跑偏
在可交易窗口中位数上：
- 第一因子 loadings 中位数：
  - BTC `0.367`
  - ETH `0.538`
  - LTC `0.402`
  - SOL `0.577`
- 第二因子 loadings 中位数：
  - BTC `+0.154`
  - ETH `+0.451`
  - LTC `-0.457`
  - SOL `-0.249`

翻成人话：
- 第一因子仍像广义 market factor；
- 第二因子更像 **ETH / BTC 偏强 vs LTC / SOL 偏弱** 的 residual style factor；
- 所以 short-cycle 版的交易动作，不一定非得是固定 pair，
  更像是：
  **short 第二因子偏热的一侧，long 第二因子偏冷的一侧。**

## 8. 对当前 desk，我会怎么落地这条主题
### 8.1 这轮不该把它定位成“完整策略已成”
虽然论文原始框架是完整的，
但对我们当前 `5m/15m` short-cycle desk，我认为更诚实的定位是：

- `主题类型`：**raw alpha**
- `是否可独立复现`：**是**
- `是否可直接落地完整策略`：**否**

原因不是 base alpha 不清楚；
恰恰相反，**base alpha 很清楚**。

真正的问题在于：
- intraday 版 residual edge 太薄；
- 需要更强 admission / 更低换手 / 更好的被动成交；
- 否则会死在成本，而不是死在方向判断。

### 8.2 但它仍然值得进素材池，因为它补的是“factor-neutral basket stat-arb”这条线
我们最近 pairs / stat-arb 积累已经很多，
但大多还是：
- cointegration spread
- z-score fade
- OU half-life
- pair / basket selection

这篇新增的是：
**共同趋势先 strip，再做第二因子 residual 的 market-neutral mean reversion。**

也就是把 raw alpha 从“pair spread 回归”再往上抬了一层：
从 spread 工程，变成**common-trend neutralized factor-residual stat-arb**。

这条线值得继续挖。

## 9. 下一步怎么测
我建议下一轮不要再做“大而全重写论文”，而是直接做这 4 个最小实验：

### 9.1 先做 exact-vs-proxy 对照
当前 probe 用的是 rolling PCA proxy。
下一步应补一个更接近论文原意的版本：
- rolling 2-factor state-space / dynamic factor
- 明确估 `f1`、`f2`
- 明确检验 `f2` 的 stationarity / half-life
- 再和 PCA proxy 对照

先回答：
**PCA 的第二主成分，能不能稳定近似论文里的第二因子？**

### 9.2 只做更极端偏离，不做连续小幅抖仓
当前结果已经说明：
- 小偏离太薄
- 大偏离更像有 edge

因此下一步应把 alpha 限制到：
- `|z_f2| >= 1.75` 或 `2.0`
- 只做 `8~12 bar` 这一档
- 进场后禁止连续加减仓
- 用 `zero-cross / half-z / time-stop` 做离场比较

### 9.3 执行必须切到 maker / passive queue join，不能默认 taker
如果继续做 4-leg basket：
- taker round-trip 基本把 edge 吃完

所以下一步必须显式比较：
- taker / taker
- maker-in / taker-out
- maker / maker

不然这条线永远只会停留在 paper alpha。

### 9.4 篮子不一定要含 BTC，本质是“common-trend strip”，不是“必须 BTC/XMR 原样复刻”
下一步应该试两类 universe：
1. **BTC-inclusive liquid majors**：`BTC / ETH / LTC / SOL / XRP`
2. **alt-heavy residual book**：`ETH / LTC / SOL / XRP / ADA`

看哪个更容易形成：
- 强共同趋势
- 可交易的 stationary second factor
- 更厚的 residual mispricing

如果 alt-heavy 版本能把共同 market beta 外显得更干净，
它在 `15m` 上可能反而比 BTC-inclusive 更像可交易对象。

## 10. 这轮结论
这篇 2021 dynamic-factor 论文，**不是**又一篇可以直接塞进“普通 cointegration pairs”抽屉里的旧材料。

对当前 desk，最值得拿出来单独测的，不是“原文那套日频 long-short 排名”本身，
而是它背后的这条 raw alpha：

**先剥共同趋势，再做第二因子 residual basket fade。**

这是条：
- 基础 alpha 清楚
- 可独立复现
- 与当前 short-cycle relative-value / stat-arb 素材池直接相关
- 但在 intraday 上仍明显受成本与换手约束

的 **raw alpha 候选**。

所以我会把它放在当前研究池里的定位定为：
**“值得继续做 exact-factor replication 与 maker-execution 细化的 factor-neutral basket stat-arb 支线”，而不是立刻上 production 的完成品。**
