# 别把这篇 2023 perp 定价论文只读成“模型竞赛”：对 short-cycle desk，更该先测的是「BTC perp conditional-drift slope」这条单资产 raw alpha

- 时间：2026-04-06 09:28 UTC
- 类型：2023 *Expert Systems* 论文摘要/元数据（Crossref + Semantic Scholar + OpenAlex）+ Binance Futures public endpoint availability check
- 主题类型：raw alpha
- 基础 alpha：**滚动估计 BTC perpetual futures 的条件均值 `μ̂` 与条件波动 `σ̂`；当模型隐含的未来价格相对当前价格的预期斜率，在波动归一化后显著偏正/偏负时，顺着这条短周期条件漂移做多/做空。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/single-asset/trend/momentum/directional/conditional-drift/perpetual-futures/btc/expected-price-slope/vol-normalized/egarch/arma/binance/1m/3m/5m/15m/paper/metadata/public-data/cost/risk
- 证据类型：论文摘要/元数据 + 公共 API 可得性确认

## 1. 这次看了什么
这轮主材料是：

- **Avinash Malik (2023), _A comparison of machine learning and econometric models for pricing perpetual Bitcoin futures and their application to algorithmic trading_**
  - Venue：**Expert Systems**
  - Year：**2023**
  - DOI：**10.1111/exsy.13414**
  - Readable URL：<https://www.semanticscholar.org/paper/279683d1756fe217b6cf4570d1dfb9addd60ffbe>
  - DOI URL：<https://doi.org/10.1111/exsy.13414>
  - Crossref：<https://api.crossref.org/works/10.1111/exsy.13414>
  - OpenAlex：<https://api.openalex.org/works/https://doi.org/10.1111/exsy.13414>
  - Repo URL：**无公开 repo**

我最后选它，不是因为又想补一篇“fair value 理论文献”，而是因为它补的是一条和我们最近几篇 **pairs / carry / fair-value mean reversion** 不一样的东西：

> **单资产 BTC perp 的 conditional-drift directional alpha。**

它回答的不是“偏离 fair value 后会不会回去”，而是：

> **在已知短周期条件均值 + 条件波动的情况下，下一段价格斜率有没有可交易方向性。**

这条线值得进素材池，因为它：

- 是 **raw alpha**，不是 filter 伪装成 alpha；
- 不依赖配对、cointegration、跨市场 lag；
- 可以直接映射到 `1m / 3m / 5m / 15m` 的 BTC perp 最小实验；
- 还能自然接到现有 desk 的 cost / funding / execution veto 组件上。

---

## 2. 先回答：这篇东西的 base alpha 是什么？
先把最关键的问题讲清楚。

### 2.1 它的 base alpha 是明确的，而且是 raw alpha
这篇 paper 真正可交易的本体不是“模型准确率”这几个字，而是：

> **当模型预测的未来 perp 价格相对当前价格呈现显著正/负斜率时，BTC perpetual futures 在短周期上存在可顺着做的条件漂移。**

翻成人话：

1. 先用最近一段 intraday 数据估一个 **下一段大概往哪边走**；
2. 再估一个 **这段预测有多 noisy**；
3. 只有当“方向边”足够大、能盖过波动噪音和交易成本时，才开仓；
4. 正斜率做多，负斜率做空。

这不是 overlay。
这也不是“看到波动大就别做”。
它本体就是一条：

- **single-asset**
- **directional**
- **trend / momentum / conditional drift**

raw alpha。

### 2.2 为什么它比继续补一层 filter 更值得
因为我们最近素材池里已经有不少：

- pairs / copula / reference-spread mispricing
- funding / basis / carry
- maker / order-book imbalance
- cross-sectional momentum / reversal

但 **“单资产 BTC perp 条件漂移”** 这条线，最近反而没有新增 intake。
如果这条壳能活，它有两个用途：

1. **直接作为独立策略**；
2. **给现有 breakout / continuation / event-driven 策略做 direction prior**。

也就是说，它不是只能单独用，还是一个能往多条主线里插的基础件。

---

## 3. 论文到底给了什么证据
从可抓到的摘要/元数据里，paper 明确给了几条对 desk 有用的信息：

### 3.1 它研究的是 intraday high-frequency BTC perpetual futures
Crossref/Semantic Scholar 摘要写得很直白：

- 研究对象是 **Bitcoin perpetual futures contracts**；
- 目标是做 **intra-day high-frequency** 的条件均值与条件波动建模；
- paper 把 perpetual pricing 问题和交易算法绑在一起，不只是做 forecasting score。

### 3.2 它不是只做 ML 马术表演，而是最终落到交易
摘要里的主结论有 3 个：

1. **EGARCH** 对 intraday volatility 的预测几乎无偏；
2. **ARMA(0,0)** 反而是 conditional mean 的最好刻画；
3. 交易算法用“当前价格 vs 预测未来价格”的 **slope** 来决定 long / short。

这第三点最关键。
对 desk 真正值钱的不是“谁赢了模型比赛”，而是：

> **signal = expected future price slope**

而不是“多加几个 feature 再让黑箱自己学”。

### 3.3 论文 headline 很夸张，但仍然给了我们 3 个有价值的数据点
摘要里直接写到：

- BTC perpetual futures 日交易量约 **$45B**；
- 最优模型平均方向判断正确率约 **85%**；
- 回测绝对收益在不同费用/杠杆假设下达到 **1500%–8000%**。

这些 headline 我不会原样照单全收，原因很简单：

- 单资产 + 高杠杆回测，百分比收益很容易被放大；
- 没看到完整持仓路径、滑点、资金利用率、爆仓约束，就不能把这个收益当真；
- `85%` 的 hit-rate 也必须看 horizon、class balance、是否只挑高置信样本。

但即便把夸张部分都打掉，这篇 paper 仍然给了我们一个值得 first test 的小壳：

> **波动归一化后的 expected-price slope，到底有没有 post-cost 方向边。**

这条就够了。

---

## 4. 对 short-cycle desk，最该拿走的不是“最准模型”，而是这条更小、更诚实的策略壳
### 4.1 别先复刻论文的 full model zoo，先复刻 base alpha
paper 的写法容易把人带进“我要不要也跑一堆 ML 模型”的误区。
但对我们 desk 来说，**first verdict** 根本不需要先做 full horse-race。

更实用的拆法是：

- `μ̂_t`：短周期条件均值（先用最简单的 rolling mean / EWMA / AR(1)）
- `σ̂_t`：短周期条件波动（先用 EWMA vol，第二轮再升级 EGARCH）
- `score_t = μ̂_{t→t+H} / σ̂_{t→t+H}`

然后只问一个问题：

> **当 `score_t` 足够大/小的时候，下一段 BTC perp 的 realized return 是否具有单调性与 post-cost edge？**

如果这个问题答不出，先别谈模型升级。

### 4.2 它和我们已有的 fair-value / basis mean-reversion 不是一回事
这点要说清。

这次 intake 的 base alpha 不是：

- `perp - spot` 偏离会回归；
- funding/basis 太高会均值回归；
- 某个 alt 相对 benchmark 的 residual 会收敛。

它是：

> **BTC perp 自己，在短周期上有条件方向漂移。**

所以它更像：

- **single-asset momentum / continuation** 的统计版本；
- 但又比“看上一根涨跌”多了一层 volatility normalization；
- 也比纯 breakout 更容易和成本门槛结合。

### 4.3 这条线很适合做成“基础方向层 + 交易否决层”
它的 best use 不是满脑子只看方向，而是做成两层：

- **方向层**：`score_t` 决定 long / short bias；
- **否决层**：basis / funding / event / spread 过差时不做。

这样它既保留 raw alpha 属性，也不会在最差执行环境里硬冲。

---

## 5. 公开数据能不能快速复现？能
### 5.1 数据源：公开可得
要把这条线先落成最小实验，不需要私有数据。
最实用的公开口径可以直接用 Binance：

- **Spot anchor / benchmark**
  - `https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=2`
- **Perp mark / index / premium / funding snapshot**
  - `https://fapi.binance.com/fapi/v1/premiumIndex?symbol=BTCUSDT`
- **Funding history**
  - `https://fapi.binance.com/fapi/v1/fundingRate?symbol=BTCUSDT&limit=2`
- **合约清单 / 元数据**
  - `https://fapi.binance.com/fapi/v1/exchangeInfo`

本轮 availability check 里，`premiumIndex` 和 `fundingRate` 都能直接拉到；`spot klines` 也可直接获取。

### 5.2 更新频率：能映射到 `1m / 3m / 5m / 15m`
这条信号不需要低频宏观数据，天然适合短周期：

- `1m / 3m`：适合做更高频 score 刷新与 child execution；
- `5m / 15m`：适合做 first verdict，先看 cost-adjusted monotonicity；
- live 版本建议直接改走 **websocket**，避免 REST ban。

### 5.3 最小可复现实验口径
先别追求论文 exact reproduction。
最快的 desk 版本可以定义成：

- 标的：`BTCUSDT` perpetual
- bar：`5m` 主实验，`15m` 稳健性复核
- price：perp mark / perp last / spot close 三套都做一遍
- `μ̂`：EWMA return mean 或 rolling constant-mean
- `σ̂`：EWMA realized vol（第二轮升级 EGARCH）
- `H`：`1 bar / 2 bars / 3 bars`
- `score = μ̂_H / σ̂_H`

这已经足够回答：

> **论文真正值钱的那个 base alpha，在我们的数据口径里有没有活性。**

---

## 6. 直接落地成完整策略的话，我会怎么写
### 6.1 entry
先用最小、最诚实的定义：

- `long`：`score_t >= z_entry`
- `short`：`score_t <= -z_entry`

第一轮网格：

- `z_entry ∈ {0.15, 0.25, 0.35, 0.50}`
- `H ∈ {1,2,3}` bars

同时加两个 admission 条件：

- `|basis_t|` 不在最近 `20d` 的极端分位（避免已经高度拥挤的 rich/cheap 狀态）
- 距离 funding timestamp 太近时可降权或不入场

### 6.2 exit
别把 exit 写复杂，先用 4 个最直白的：

1. **time exit**：持有 `H` bars 或 `2H` bars
2. **sign flip**：`score_t` 反向穿回 0
3. **stop-loss**：`0.75 × σ̂_H`
4. **take-profit**：`1.0 × σ̂_H` 或 `1.25 × σ̂_H`

如果 first verdict 里发现 edge 主要集中在首 bar，那就别强行拿长。

### 6.3 sizing
position size 直接用 volatility normalization：

```text
target_notional_t ∝ clip(|score_t|, 0, score_cap) / σ̂_t
```

第一轮建议：

- notional cap：单次 `0.5x ~ 1.0x` 研究杠杆
- 不做 martingale
- 不因为连胜连败改仓

### 6.4 cost
这条线最怕 turnover 被成本吃掉，所以 first test 必须显式带：

- taker-only：单边 `2~4 bps`
- maker/taker mix：`1~3 bps`
- 再单独计 funding transfer

没有 post-cost，就直接判死，不要再给它找借口。

### 6.5 risk
最小 risk shell：

- funding 窗口前后 `±10m` 降权
- CPI / FOMC / NFP 大事件前后可先做 veto 版本
- 当 realized vol 超过 rolling `95%` 分位时减半仓或不做

注意：这些是 **risk / execution overlay**，不是 alpha 本体。

---

## 7. 这条线最值得先测的 3 个问题
### 7.1 方向 score 有没有单调性
最先看这个：

- `score` 分桶后，下一 bar / 下一 `H` bars return 是否单调；
- 不是只看 top-vs-bottom，连中间桶也要看。

如果只有极端桶有点效果，而中间全乱，那说明它更像 sparse trigger，不像连续 alpha。

### 7.2 edge 是不是被波动环境伪装出来的
因为信号本身来自 `μ̂/σ̂`，最容易出现的问题是：

- 表面像方向预测；
- 实际上只是高波动环境里“顺着大波动继续抖”。

所以必须切：

- 低 vol / 中 vol / 高 vol
- funding 正 / funding 负
- basis rich / cheap / neutral

看 edge 到底在哪一层活。

### 7.3 论文 headline 的 85% / 1500%-8000% 能留下多少“干货”
我的预期是：

- 真正可移植到 desk 的，不会是 8000% 这种 headline；
- 更现实的是：**某些 `score` 极端桶在 `5m / 15m` 上有稳定的正负偏移，并且能在合理 round-trip cost 后剩下一点边。**

这就够了。

---

## 8. 下一步怎么测（最小实验，别拖）
### 8.1 第一轮：先做 cheapest possible verdict
**目标：一下午内回答“这条 alpha 活不活”。**

1. 拉 `BTCUSDT` spot `5m` + perp mark/premium/funding 数据；
2. 用 `20d` rolling window 估 `μ̂` 和 `σ̂`；
3. 先不用 EGARCH，直接上 **EWMA mean + EWMA vol**；
4. 计算 `score_t = μ̂_H / σ̂_H`；
5. 跑 `H = 1,2,3` bars；
6. 输出：
   - 分桶 next-return monotonicity
   - top-bottom spread
   - hit-rate
   - gross / net PnL
   - turnover
   - funding-adjusted PnL

### 8.2 第二轮：再验证论文最值钱的那块——EGARCH 值不值得加
如果第一轮活，再做：

- `σ̂`：EWMA vs EGARCH
- `μ̂`：constant mean vs AR(1) vs simple EWMA mean
- 对比谁带来更好的 **net monotonicity**，而不是只看 in-sample fit

### 8.3 第三轮：接到 desk 现有执行壳
如果第二轮仍然活，就把它接进：

- funding veto
- event veto
- maker/taker route split
- size scaler

再看它更适合：

- 独立跑；还是
- 作为 breakout / continuation / event-driven 的 direction prior。

---

## 9. 我对这篇材料的判断
### 9.1 值得 intake，但不要被 headline 绑架
这篇 paper 值得进研究池，不是因为我信它的高收益回测，而是因为它给了一个对 short-cycle 很实用、而且最近没重复 intake 的基元：

> **BTC perp 的 vol-normalized expected slope。**

### 9.2 它在我们 desk 的最好定位
我会把它定位成：

- **主标签：raw alpha**
- **子标签：single-asset / directional / conditional drift**
- **首轮战术：5m/15m minimal experiment**
- **后续用途：独立策略或 shared direction prior**

### 9.3 一句话结论
> **别先复刻论文那串模型比赛；先测“vol-normalized expected-price slope”这条最小 raw alpha，在 `BTCUSDT` perpetual 的 `5m / 15m` 上看它有没有 post-cost 单调性。**

---

## 10. 参考与来源
1. **Malik, A. (2023). _A comparison of machine learning and econometric models for pricing perpetual Bitcoin futures and their application to algorithmic trading_. Expert Systems, 40(10).**  
   - DOI：<https://doi.org/10.1111/exsy.13414>  
   - Crossref：<https://api.crossref.org/works/10.1111/exsy.13414>  
   - Semantic Scholar：<https://www.semanticscholar.org/paper/279683d1756fe217b6cf4570d1dfb9addd60ffbe>  
   - OpenAlex：<https://api.openalex.org/works/https://doi.org/10.1111/exsy.13414>
2. **Binance Spot API**  
   - Klines example：<https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=2>
3. **Binance Futures Public API**  
   - Premium / mark / index snapshot：<https://fapi.binance.com/fapi/v1/premiumIndex?symbol=BTCUSDT>  
   - Funding history：<https://fapi.binance.com/fapi/v1/fundingRate?symbol=BTCUSDT&limit=2>  
   - Exchange metadata：<https://fapi.binance.com/fapi/v1/exchangeInfo>
