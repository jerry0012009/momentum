# 别把这篇 CTREND 论文只读成周频因子：对 desk 更该先测的是「多指标聚合的 XS trend score」raw alpha

- 时间：2026-04-01 03:46 UTC
- 类型：2025 *Journal of Financial and Quantitative Analysis* 开放获取全文 PDF（本地全文抽取）+ Crossref 元数据
- 主题标签：raw-alpha/cross-sectional/trend/momentum/multi-signal/technical-indicators/elastic-net/value-weighted/liquid-coins/crypto/1m/3m/5m/15m/paper/public-data/cost
- 证据类型：论文（全文细读）
- 主题类型：raw alpha
- 基础 alpha：把跨币种的价格/成交量技术指标聚合成一个横截面 trend score（CTREND），做“高分多、低分空”的 weekly top-minus-bottom 组合
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次看了什么
这次补的不是 pairs、carry，也不是一个只会服务别人的 gate，而是一条**可独立跑起来的横截面 raw alpha**：

- **Fieberg, Liedtke, Poddig, Walker, Zaremba (2025, *Journal of Financial and Quantitative Analysis*)**
- 题目：*A Trend Factor for the Cross Section of Cryptocurrency Returns*
- 核心动作不是“再发明一个单指标”，而是把 **28 个 price / volume / volatility 技术指标** 的信息汇总成一个 **CTREND** 分数，然后做 **high-minus-low** 横截面多空。

这条线值得进当前池子，原因很简单：

1. **base alpha 很清楚**，不是 filter 伪装成 alpha；
2. 它补的是我们当前素材池里相对偏少的 **cross-sectional multi-signal trend** 主线；
3. 它天然可以 desk 化成 `1m/3m/5m/15m` 的 **top-minus-bottom 组合策略**，而不是只能停留在论文解释层。

## 2. 先回答：这篇东西的 base alpha 是什么？
一句话：

**base alpha = 用多组技术指标预测“下一个横截面里谁更强、谁更弱”，然后做 strongest-minus-weakest 的 market-neutral 趋势组合。**

它不是：

- 纯 filter
- 纯 regime
- 纯 risk overlay
- 纯资产定价解释

它就是一个可以单独交易的 **cross-sectional / relative-value raw alpha**。

## 3. 一句话核心结论 & 它怎么证明的
### 一句话核心结论
**crypto 横截面里，单看传统 momentum 还不够；把价格、成交量、波动相关技术指标合成一个 CTREND 分数后，能得到比常见 crypto 因子更强、且成本后仍存活的多空趋势 alpha。**

### 它怎么证明
作者用 `2015-04 ~ 2022-05`、`3,245` 个市值超过 `100 万美元` 的币种样本，先从日频 OHLCV 计算 `28` 个技术指标，再用 **cross-sectional combined elastic net (CS-C-ENet)** 做 out-of-sample 选特征与聚合预测，最后按每周分数做 value-weighted quintile long-short 回测，并额外检验：

- 因子 alpha 是否能被已有 crypto 因子解释；
- 在大币 / 液态币里是否还活着；
- 加交易成本后是否还能活；
- 换 `55,296` 种研究设计后是否依然稳。

## 4. 论文里最值得 desk 先抄的，不是“周频因子”四个字
如果把它只读成“又一篇 crypto factor paper”，就读窄了。

**对短周期 desk 更值钱的，是这条可迁移骨架：**

1. 不赌单个指标永久有效；
2. 先让每个指标各自给出一个横截面 forecast；
3. 再用轻量机器学习只保留“当前还在工作”的 forecast；
4. 最后做 strongest-minus-weakest 的组合，而不是单币方向押注。

这意味着它真正能迁移的不是“周频收益有多高”，而是：

- **信号工程**：多指标 → 单一 composite score
- **组合工程**：cross-sectional ranking → top/bottom baskets
- **参数治理**：让模型自己淘汰失效指标，而不是手写一串硬规则

这和当前 desk 已有的：

- pairs / stat-arb
- carry / funding / basis
- event-driven / microstructure

是互补关系，不是重复 intake。

## 5. 论文原始方法，拆成人话
### 5.1 数据与样本
- 数据源：`CoinMarketCap`
- 输入：price、volume、market cap
- 样本期：`2015-04 ~ 2022-05`
- 样本规模：`3,245` 个币
- 频率：用**日频**数据算指标，用**周频**做横截面预测与组合
- 过滤：
  - market cap 至少 `100 万美元`
  - 剔除明显错误值
  - returns 做极端值截尾

### 5.2 他们用了哪些指标
总共 `28` 个，四大类：

1. **Momentum oscillators**
   - RSI
   - stochastic K / D
   - stochRSI
   - CCI

2. **Price moving averages**
   - `3/5/10/20/50/100/200` 日 SMA
   - MACD
   - MACD 与 signal line 的差

3. **Volume indicators**
   - `3/5/10/20/50/100/200` 日 volume SMA
   - vol MACD
   - vol MACD-signal
   - Chaikin money flow

4. **Volatility indicators**
   - Bollinger lower / middle / upper band
   - Bollinger bandwidth

### 5.3 CTREND 是怎么做出来的
不是把 28 个指标简单平均。

而是三步：

1. **每个指标单独做一个横截面 forecast**
   - 先把指标转成横截面 rank，并映射到 `[-0.5, 0.5]`
   - 用 rolling `52` 周窗口做 Fama-MacBeth 风格预测

2. **让 elastic net 只保留仍然有用的 forecast**
   - 用 CS-C-ENet 做 forecast selection
   - 只保留 `θj > 0` 的预测器

3. **把 surviving forecasts 再平均，得到 CTREND**
   - 这就变成每个币的 aggregate trend score

然后每周：

- long CTREND 最高 quintile
- short CTREND 最低 quintile
- value-weighted
- weekly rebalance

## 6. 关键结果：这不是“解释型因子”，是能交易的 raw alpha
### 6.1 主结果
论文主结果很硬：

- **H-L 收益：`3.87% / week`**
- **t-stat：`5.19`**
- **年化 Sharpe：`1.94`**
- **对 LTW 三因子模型的 alpha：`2.62% / week`**，`t = 4.22`

换句话说，它和经典 crypto momentum 有关，但**并没有被 momentum 吞掉**。

### 6.2 不是只靠小垃圾币
这点对 desk 特别重要。作者专门看了大币和液态币子样本：

- **Top 50% liquidity**：H-L `4.36% / week`
- **Top 10% liquidity**：H-L 仍有 `2.20% / week`
- **Top 100 coins**：H-L `3.30% / week`

也就是说，这条边并不主要来自“难交易的小币灰尘角落”。

### 6.3 成本后仍有边，但 turnover 很高
这篇论文没有假装“免费换仓”。

- long-short 组合周换手：**`68.46%`**
- 全样本在较保守成本假设下，net return 仍有：
  - **`2.90% / week`**
  - **`2.62% / week`**
  - **`2.35% / week`**
- Largest 100 样本下，net return 仍有：
  - **`2.45% / week`**
  - **`2.17% / week`**
  - **`1.90% / week`**

这很关键：

**它不是低换手 alpha；但它也不是“加一点费用就死”的脆边。**

### 6.4 不是靠某个单指标偶然撞对
作者做了 variable importance，最高的不是“老三样纯动量”独占，而是：

- `boll_mid`
- `cci`
- `macd`

这说明它更像一个**多指标共振的 composite trend score**，而不是把一个 RSI 或均线信号换个壳重新卖。

### 6.5 研究设计鲁棒性不差
作者还跑了 `55,296` 种实现组合：

- 大多数 CTREND 规格的年化 Sharpe 分布在 `0.5 ~ 2.5`
- 加 `1-day` implementation lag 后表现下降，但仍存活
- 去掉 volume-based indicators，表现会降，但不会完全崩掉

这说明：

**真正值钱的不是某一套唯一参数，而是“多指标聚合 + 预测器筛选”的总框架。**

## 7. 对当前 desk，最应该怎么读这篇 paper
### 7.1 不要机械抄“周频”
论文原版是：

- 日频指标
- 周频排序
- 周频换仓

这对我们不是最终形态。

**desk 化的正确读法**应该是：

- 保留“多指标 → aggregate score → top-minus-bottom”这条骨架；
- 把频率压到 `15m/5m` 执行，必要时 `1m/3m` 做高强度版本；
- 不强行保留论文里的完整 28 指标和周频壳。

### 7.2 它服务的是哪类短周期 alpha
它服务的是：

- **cross-sectional trend / momentum raw alpha**
- 也可兼作 **market-neutral relative-strength alpha**

不服务的是：

- 单币 breakout 形态学
- pairs spread mean reversion
- funding carry

所以它对当前素材池的意义，是在 **pairs / carry / event-driven** 之外，再补一条**标准化 XS trend 主线**。

## 8. 最适合 desk 的转译版本
### 8.1 最小可复现实验（第一版）
**Universe**
- Binance USDⓈ-M perpetual
- 过去 `30d` ADV 前 `30~60` 个币
- 上线满 `90d`
- 过滤极端 funding、明显异常盘口、长期低成交标的

**Bar 频率**
- 主实验：`15m`
- 强化实验：`5m`
- 极限实验：`3m / 1m` 只做后续扩展，不作为首轮 baseline

**Feature family（先做缩减版，不必一口气 28 个全上）**
1. 价格趋势类：
   - `SMA distance (8/16/32/64/128 bars)`
   - `MACD`
   - `MACD-signal`
2. 振荡类：
   - `RSI`
   - `CCI`
   - `stochK / stochD`
3. 成交量类：
   - volume SMA ratio
   - Chaikin / signed-volume proxy
4. 波动类：
   - Bollinger mid / width

**Signal construction**
- 每个 bar 或每 `4h` 更新一次横截面 rank
- 每个指标单独预测下一段收益（例如 next `4h` / `12h`）
- 用 elastic-net / L1 筛掉当前失效特征
- 生成 composite score
- long top `20%`
- short bottom `20%`

### 8.2 Entry / Exit / Sizing / Risk / Cost
**Entry**
- 仅在 rebalance 时点按 composite score 排序开仓
- top basket 开多，bottom basket 开空

**Exit**
- 固定 holding：`4h / 12h / 24h`
- 或下一次 rebalance 全量重排

**Sizing**
- 先做 dollar-neutral
- 再做 BTC beta 近中性
- 单币权重 cap：`5%~10%`

**Risk**
- universe 少于 `15` 个可交易币时暂停
- 组合单侧行业/主题集中度设上限
- 单币异常 funding / spread / ADL 风险做 admission veto

**Cost**
- 第一轮统一用 `6 / 10 / 15 bps` one-way cost ladder
- 第二轮再拆 maker/taker/slippage/funding

## 9. 我对这条线的判断
这篇东西对当前 desk 的价值，不在于“论文里周频回报很夸张”，而在于：

**它提供了一条很像工业化生产线的 raw alpha 骨架：**

- 输入是公开可得的 OHLCV
- base alpha 很清楚
- 组合结构清楚
- 风险与成本可以直接接进去
- 最终很容易和现有 execution stack 对接

如果当前要继续补 **raw alpha 素材池**，我会把它排得比“再来一个纯 filter / regime paper”更前。

## 10. 下一步怎么测
不要直接复刻论文的整套周频大宇宙；先做一个 **3 维最小实验矩阵**：

### A. 预测 horizon
- next `4h`
- next `12h`
- next `24h`

### B. bar 频率
- `15m`
- `5m`

### C. 特征组
1. `trend-only`：SMA + MACD + Bollinger mid
2. `trend+oscillator`：再加 RSI / CCI / stoch
3. `full-lite`：再加 volume features

### D. 组合方式
- top/bottom `20%`
- top/bottom `30%`
- top/bottom decile（仅在 universe 足够大时）

### E. 必看输出
- gross / net spread return
- turnover
- long / short leg contribution
- BTC beta
- universe breadth
- implementation lag sensitivity
- 不同成本梯度下的生存线

### 第一轮 verdict 标准
如果出现下面任一情况，就直接砍：

1. `10 bps` one-way 成本后净边接近 0
2. alpha 只靠极少数小币支撑
3. 一加 `1 bar` 实施延迟就崩
4. short leg 才是真边、long leg 基本没贡献且无法稳定 borrow/execute

如果结果是：

- **trend-only 已经活**：先上 production candidate，不急着堆更多特征；
- **只有 full-lite 才活**：说明 volume / breadth 信息重要，再考虑做更完整 CTREND；
- **只在高 dispersion 时活**：把它降级成 regime-gated raw alpha；
- **只在 24h horizon 活**：那就诚实承认它更像“中速 XS trend”，由 `15m/5m` 负责执行，不要硬装成逐根 alpha。

## 11. 来源
1. **Fieberg, C., Liedtke, G., Poddig, T., Walker, T., & Zaremba, A. (2025). _A Trend Factor for the Cross Section of Cryptocurrency Returns_. Journal of Financial and Quantitative Analysis, 60(7), 3116–3153.**
   - DOI: https://doi.org/10.1017/S0022109024000747
   - Readable URL: https://www.cambridge.org/core/product/identifier/S0022109024000747/type/journal_article
   - Direct content URL: https://www.cambridge.org/core/services/aop-cambridge-core/content/view/S0022109024000747
   - Crossref metadata: https://api.crossref.org/works/10.1017/S0022109024000747
   - Repo URL: 未见作者公开 repo（至少本轮未检到明确官方实现）

## 12. 给自己的简短结论
**这不是“周频因子论文”，而是一条可以直接 desk 化成 `top-minus-bottom` 组合策略的多指标 XS trend raw alpha 骨架。**

对当前 `1m/3m/5m/15m` 研发节奏，最值得先偷的不是论文里的全市场回报数字，而是：

- 多指标聚合
- 预测器自动筛选
- 横截面 strongest-vs-weakest 组合
- 对大币 / 液态币 / 成本的诚实检验
