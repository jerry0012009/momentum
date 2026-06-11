# 别把这篇 2023 sparse-jump 论文只读成解释型 regime story：对 short-cycle desk，更该先把它当作「trend/reversal × activity/attention 三态 router」
- 时间：2026-04-14 23:21 UTC
- 类型：2023 *Digital Finance* 全文（Springer open-access HTML）
- 主题类型：regime
- 基础 alpha：不是独立 alpha；服务于 `15m trend / breakout continuation`、`15m mean reversion fade`、`15m cross-sectional relative-value` 三类现有/待建 raw alpha
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：regime / router / trend / reversal / activity / attention / sparse-jump-model / bull-neutral-bear / crypto / 15m / 5m / paper / fulltext
- 证据类型：论文全文 + 可迁移实验设计

## 1. 先说结论：这篇东西的 base alpha 是什么？
**答：它本身不是独立 raw alpha。**
它更像一个 **shared regime / router**：用一组可解释特征，把市场切成 `bull / neutral / bear` 三态，再决定 **什么时候该让 continuation 上场，什么时候该让 fade 或 XS relative-value 上场**。

这轮我没有把它当主线 raw alpha 来写，是因为按近期 digest 查重后，**pairs / liquidity-split reversal / funding / basis / microstructure** 这些更直接的 raw-alpha 方向已经被高密度覆盖；而当前还能找到的一些未覆盖近作，很多是 **黑箱 daily forecasting / end-to-end deep learning**，base alpha 说得不够诚实，也不够 desk-friendly。相比之下，这篇 paper 虽然不是独立 alpha，但它给的是一个**可解释、可迁移、可复用到多条 short-cycle alpha** 的状态层，反而更值得进研究池。

## 2. 这次看了什么
这次主读的是 **Federico P. Cortese, Petter N. Kolm, Erik Lindström (2023)** 的论文 **_What drives cryptocurrency returns? A sparse statistical jump model approach_**。

论文做的事很明确：
- 研究对象是 **5 个大币：BTC / ETH / XRP / LTC / BCH**；
- 样本区间约 **2018-01 ~ 2022-09**；
- 用一个 **statistical sparse jump model** 同时做：
  1. 特征筛选（feature selection）
  2. 参数估计（parameter estimation）
  3. 状态分类（state classification）
- 候选特征来自三大类：
  - crypto 市场自身时间序列
  - sentiment / public-attention 类特征
  - broader financial market features

它最值钱的结论不是“crypto 会分牛熊熊”这句废话，而是：
> **一个三状态模型（bull / neutral / bear）就足以抓住大币回报动态，而真正被模型留下来的关键驱动，并不是二阶波动特征本身，而是：一阶收益、trend/reversal 信号、market activity、public attention。**

## 3. 对 desk 真正有用的，不是再做一个预测器，而是做 router
这篇 paper 对我们的价值，不在于“又多一个 state model”，而在于它把一个很常见但经常被说不清的判断，拆成了可以实做的结构：

- **趋势类 alpha** 为什么有时顺、有时来回打脸？
- **均值回归类 alpha** 为什么有时好做、有时接飞刀？
- **横截面 relative-value / XS momentum** 为什么有时 breadth 扩散很强，有时全被 beta 吞掉？

这篇 paper 的回答是：
- 市场并不是单一状态；
- 切状态最有用的，不只是波动高低；
- **更重要的是 trend/reversal 本身、交易活跃度、以及公众注意力。**

这就很适合被 desk 改写成一个 shared router：
- `bull / high-activity / high-attention` → continuation、breakout、winner-hold 更值得放行；
- `bear / high-activity / overreaction` → fade、snapback、risk-down 更值得放行；
- `neutral / low-activity` → 降仓、缩短持有期、提高 admission threshold。

## 4. 论文里最值得带回 desk 的 4 个点
### 4.1 三态已经够用，不必先上过度复杂的 state machine
论文明确说 **three-state model** 就能比较自然地解释 crypto 大币动态，对应 `bull / neutral / bear`。

这对我们很重要，因为它意味着：
- 第一版 router 不需要先搞 7-state / 12-state HMM；
- 先做一个诚实的 `3-state` 框架，更容易落地、调参和和现有 alpha 对接；
- 对 `5m/15m` desk 来说，先做 “**方向状态 + 活跃度状态**” 已经足够开始筛。

### 4.2 被选中的关键驱动，不是“波动越大越重要”
论文结论里一个对 desk 很有启发的点是：
- **first moments of returns** 是关键；
- **trend / reversal signals** 是关键；
- **market activity** 是关键；
- **public attention** 是关键；
- 但 **second moments / volatility-based features** 没有那么核心。

这和很多 desk 直觉不同。我们常常先想“vol 高/低是不是主变量”，但这篇 paper 更像在说：
> **决定短周期 alpha 该怎么打的，不只是波动大小，而是“价格在朝哪边走、走得有没有延续/反抽结构、市场有没有在看、有没有在动”。**

换成人话：
- `高波动` 本身不是策略；
- `趋势 + 活跃 + 注意力` 的组合，才更像可执行路由信号。

### 4.3 这不是单币预测器，而是共享状态层
很多 ML forecasting paper 的问题是：
- base alpha 说不清；
- 模型太黑箱；
- 迁移到 desk 时只能得到一句“再训练一个模型试试”。

这篇 paper 至少把事说清了：
- 它不是直接给你 “下一根涨跌” 的 black box；
- 它是在做 **状态识别**；
- 因而更适合作为 **多条 alpha 的共享上层**。

如果后面 Jerry 的研究线要同时跑：
- `trend / breakout`
- `mean reversion / fade`
- `cross-sectional / relative value`

那这种 shared state layer 的复用价值其实很高。

### 4.4 它服务的是真正的 short-cycle 研究流程
虽然论文原始频率不是为 `5m/15m` 生的，但它给的结构特别适合 short-cycle desk：
- 慢一层：状态识别（1h / 4h / 1d 更新都行）
- 快一层：具体执行 alpha（1m / 3m / 5m / 15m）

也就是：
- **state 决定谁能上场**
- **signal 决定什么时候进场**

这比“让一个大模型直接同时做状态、方向、仓位、退出”更干净，也更容易审计。

## 5. 策略拆解（必填）
- 方向属性：shared regime / router
- 基础 alpha：`trend continuation`、`mean reversion fade`、`cross-sectional relative-value`
- regime：`bull / neutral / bear` 三态
- filter / veto：用 `trend/reversal + activity + attention` 去决定哪条 alpha 被放行/降权/否决
- risk / sizing / execution overlay：不同 state 下改持仓上限、admission threshold、hold horizon、stop 宽度

## 6. 最适合当前 desk 的改写方式
### 6.1 不直接复刻论文原模型，先做“弱复刻版 router”
第一版别急着上完整 sparse jump model；先做一个 **proxy router** 就够：

#### state feature family（先用公开、好拿的数据）
1. **trend / reversal**
   - `ret_1d`
   - `ret_8h`
   - `ema_gap(16,64)`
   - `distance_to_rolling_high`
   - `close_location_in_range`
2. **market activity**
   - `vol_z_1d`
   - `turnover_z_1d`
   - `range_expansion`
   - `trade_count_z`
3. **attention / participation proxy**
   - 若只用交易所公共数据：`taker_buy_ratio`、`OI change`、`funding dispersion`、`liquidation count/value`
   - 若允许外部数据：Google Trends、Fear & Greed、活跃地址 / exchange netflow 等慢变量

先把这些特征在 `BTC / ETH / SOL / XRP / ADA` 上做一个简单的 `3-state clustering / rule-based router`，再去切现有 alpha。

### 6.2 它最适合服务哪些现有主线
优先服务这三类：

1. **trend / breakout continuation**
   - 看看 `bull + high-activity + high-attention` 是否显著提高 continuation hit-rate；
2. **fade / mean reversion**
   - 看看 `bear + shock-activity + reversal-feature-extreme` 是否更适合 snapback；
3. **XS momentum / relative-value**
   - 看看 `neutral vs bull` 状态下，breadth 扩散与 winners-hold 是否明显不同。

## 7. 可复刻的最小实验
### 7.1 研究假设
对 `5m/15m` desk，**状态层不是用来预测每根 bar，而是用来决定“哪类 raw alpha 今天该更用力，哪类该收手”。**

### 7.2 最小实验口径
- **市场**：Binance USDⓈ-M Perps
- **频率**：信号执行 `15m`，状态更新 `1h` 或 `4h`
- **资产池**：`BTC / ETH / SOL / XRP / ADA / DOGE`
- **状态数**：固定 `3` 态（bull / neutral / bear）
- **最小特征**：
  - `ret_1d, ret_8h, ema_gap, distance_to_20d_high`
  - `vol_z_1d, turnover_z_1d, tradecount_z`
  - `OI_change_1d, funding_dispersion, taker_buy_ratio`

### 7.3 先挂接哪 3 条 alpha
1. **15m breakout continuation shell**
   - 观察 state 条件下 `entry bps / win rate / avg MFE`
2. **15m band-fade MR shell**
   - 观察 state 条件下 `next-4bar mean reversion bps`
3. **15m XS momentum sleeve**
   - 观察 state 条件下 `top-bottom decile spread`

### 7.4 最该先看的不是收益率，而是“分流能力”
第一轮先看这几个：
- 被 router 放行后，alpha 的 `bps/笔` 是否更高；
- trade count 是否掉太多；
- 是否出现明确分工：`某状态更适合 continuation，另一状态更适合 fade`。

如果 router 不能明显提升 **条件期望 / admission efficiency**，那就别继续复杂化。

## 8. 我对这篇材料的判断
### 值得保留的部分
- 可解释；
- 不是只会给“黑箱预测分数”；
- 可以同时服务多条 alpha；
- 很适合作为现有 `5m/15m` 研究线的上层状态框架。

### 不该过度脑补的部分
- 它**不是**一条独立 raw alpha；
- 论文原始特征里有 attention / sentiment / broader-market 变量，迁移到纯交易所公开数据时要做 proxy；
- 三态 router 如果做得太复杂，很容易变成“解释一切、交易不了”的玩具。

## 9. 下一步怎么测（必须落地）
1. 先做一个 **无需外部数据** 的 `3-state proxy router v0`：
   - 仅用 Binance 公共 `klines + funding + OI + taker ratio`；
2. 用它去切三条现成壳：
   - `15m breakout`
   - `15m fade`
   - `15m XS momentum`
3. 每条只看三件事：
   - `gross bps/笔`
   - `cost after 2/4/6 bps`
   - `trade count 保留率`
4. 如果 `router` 只会减少交易、不提升条件期望，就判失败；
5. 若有效，再加一层慢变量：
   - Fear & Greed / Google Trends / 活跃地址 / exchange netflow

## 10. 来源
1. **Cortese, F. P., Kolm, P. N., & Lindström, E. (2023).** *What drives cryptocurrency returns? A sparse statistical jump model approach*. *Digital Finance*, 5, 483–518.
   - DOI：`10.1007/s42521-023-00085-x`
   - Readable URL：<https://link.springer.com/article/10.1007/s42521-023-00085-x>
   - PDF URL：<https://link.springer.com/content/pdf/10.1007/s42521-023-00085-x.pdf>
2. 论文摘要与全文关键信息（Springer open-access HTML）明确给出：
   - `three-state model best describes the dynamics of cryptocurrency returns`
   - states 对应 `bull / neutral / bear`
   - 关键驱动是 `first moments of returns`、`trend/reversal signals`、`market activity`、`public attention`
   - 波动/二阶矩类特征并非最核心