# 别把 MAX / lottery effect 统一当 fade：这篇 2021 Financial Innovation 更该先测的是「多日极端上冲 rich-vs-cheap 横截面 continuation」raw alpha
- 时间：2026-03-29 07:42 UTC
- 类型：2021 Financial Innovation 开放获取全文 PDF（Springer 可读）
- 主题类型：raw alpha
- 基础 alpha：横截面上，formation window 里打出更大“极端正收益”的币，下一持有窗继续更强；极端更弱的币继续更弱
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/momentum/lottery-effect/max-effect/extreme-return/relative-value/market-neutral/continuation/formation-vs-holding-horizon/5m/15m/1m/3m/paper/public-data/cost
- 证据类型：论文全文证据

## 1. 这次看了什么
这次看的是 **Melisa Ozdamar, Levent Akdeniz, Ahmet Sensoy (2021), _Lottery-like preferences and the MAX effect in the cryptocurrency market_**, 发表在 **Financial Innovation**。

这篇东西最值得 desk 拿走的，不是“crypto 里也有 lottery-like preference”这句学术话，而是它给出了一条 **可独立落地的横截面 raw alpha**：

> **base alpha 很清楚：过去一段时间里，谁打出过更极端的正收益，下一段时间里谁更可能继续跑赢；所以可以做多 high-MAX，做空 low-MAX。**

这点很关键，因为最近素材池里已经有一条 **“past-hour MAX rich-vs-cheap fade”** 线（更短 formation、更快 holding、更像过热回落）；而这篇 2021 论文提醒我们：**MAX / lottery 不是天然等于 fade，符号很可能随 formation horizon 改变。**

对短周期 desk 来说，这不是旧题重讲，反而是一个非常便宜、非常值得立刻做的 **horizon-split falsification**：
- `过去 1h 的极端上冲` 也许该 fade；
- 但 `过去 24h~72h 的极端上冲`，未必该 fade，可能反而该在横截面上继续跟强弱。

## 2. 核心结论
- **一句话核心结论：** 论文不是在讲 filter，而是在讲一条 **cross-sectional continuation / relative-strength raw alpha**——按过去一个 formation window 内的 `MAX` 排序，做多最强 decile、做空最弱 decile。
- **原始定义：** `MAX` = 某币在**过去 28 个交易日**里的**最大单日收益**；crypto 7x24，所以文中把一周当 `7` 天、一个月当 `28` 天。
- **交易口径：** 每周排序一次，形成 decile 组合，观察**下一周**收益；同时给了 value-weighted、equal-weighted 和三因子 alpha。
- **headline 数字很硬：** value-weighted `High MAX - Low MAX` **raw spread = `3.03%/week`**，Newey-West t-stat = **`4.10`**；对应 **three-factor alpha = `1.99%/week`**，t-stat = **`3.72`**。
- **不是只在一种 MAX 定义下成立：** 把 `MAX` 改成过去一个月里**最高 2/3/4/5 个单日收益的均值**，long-short spread 仍显著为正；value-weighted raw spread 约 **`1.8% ~ 3.0%/week`**。
- **不是被 size / momentum / reversal / liquidity 偷走：** 双重排序后，控制 `SIZE / PRICE / MOM / REV / ILLIQ`，high-MAX 仍明显跑赢 low-MAX。
- **不是波动率假扮的 MAX：** 控制 `VOL / IVOL` 后，MAX 仍有正 alpha；反过来控制 MAX 以后，波动率本身的解释力大多消失。
- **情绪高低都活：** high-MAX minus low-MAX 在**低情绪**时仍有 **`2.80%/week`**，在**高情绪**时约 **`3.25%/week`**。

## 3. 为什么和当前项目有关
这篇值得进池，有三个直接原因。

### 3.1 它补的是当前 desk 真需要的 raw alpha 槽位
当前研究池虽然已经补了不少 `trend / breakout / intraday shock / microstructure`，但也明确要求持续补：
- `cross-sectional`
- `relative value`
- `stat-arb / pairs`
- `carry / funding / basis`

这篇正好属于 **cross-sectional / relative-value raw alpha**，而且不需要额外慢频外部数据；对 `5m / 15m` 最容易做的是 liquid perp universe 的 rank-based long-short。

### 3.2 它给的是“符号随 horizon 改变”的研究假设
同样是 MAX / 极端涨幅，这篇和我们近期 intake 过的短窗 fade 方向不一样。对 desk 来说，最值钱的不是“论文之间谁对谁错”，而是：

> **MAX 可能是一个 horizon-conditioned family，而不是单一方向因子。**

也就是：
- **超短 formation（如过去 1h）**：过热更像 `fade`
- **更长 formation（如过去 24h/72h/7d）**：极端强势更像 `continuation`

如果这个 split 成立，那它就不是“又一个 alpha”，而是一条可以扩成 **formation-horizon ladder** 的母策略分支。

### 3.3 它有完整策略骨架，不只是解释型文献
这篇不是“市场为什么会这样”的纯解释文。它已经给了：
- 排序变量：`MAX`
- 调仓频率：周频
- entry：long high-MAX / short low-MAX
- exit：持有到下次再平衡
- weighting：VW / EW
- 风险控制：三因子 alpha、双重排序控制
- 成本提醒：高 MAX 更偏小币、低价币、低流动性币，短周期迁移必须做流动性和 turnover 治理

这就满足了“能独立成为完整策略候选”的标准。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对强弱 / market-neutral
- 基础 alpha：过去 formation window 里更容易打出极端正收益的币，下一 holding window 继续更强
- entry：按 `MAX` 排序，做多 top bucket、做空 bottom bucket
- exit：固定持有到下一个再平衡窗口；或分数穿越中性阈值时提前换仓
- sizing：先做等权；第二层再加 `inverse-vol / liquidity-cap / score-proportional`
- risk：限制单币权重、单主题权重、beta 偏移；剔除 stablecoin、极低流动性币、新上市币
- cost：这条线**最怕换手和小币幻觉**；若迁到 `1m/3m` 后只能靠边角料留收益，就不该硬上
- 更适合的 regime：截面分化高、leader-laggard 清晰、强势币有持续资金拥挤时
- 主要 veto：极端新闻拉盘、单点上影线伪信号、低流动性小币、交易所活动导致的假极端收益

## 4. 论文里到底怎么做的
### 4.1 数据与样本
- 数据源：**CoinMarketCap** 公共数据
- 样本期：**2014-01 到 2020-09**
- Universe：所有有公开数据的 crypto，**市值 > 500 万美元**，且**上市满 6 个月后**才纳入
- 样本规模：期初 **17** 个币，期末最高到 **523** 个币

### 4.2 变量构造
- `MAX`：过去 **28 天**里最大的单日收益
- `MAX(2~5)`：过去 28 天里最高 `2/3/4/5` 个单日收益的均值
- 控制变量：
  - `BETA`
  - `SIZE`
  - `PRICE`
  - `MOM`：前 `t-4` 到 `t-2` 周的累计收益
  - `REV`：过去 `1` 周收益
  - `ILLIQ`：Amihud illiquidity
  - `VOL`：Garman-Klass volatility

### 4.3 交易规则
- 每周按 `MAX` 排序成 decile
- 做多 `High MAX`，做空 `Low MAX`
- 持有下一周
- 同时看：
  - value-weighted 组合收益
  - equal-weighted 组合收益
  - 三因子 alpha
  - Fama-MacBeth 横截面回归

### 4.4 最关键的 6 个数字
1. **VW long-short raw spread = `3.03%/week`**，t = **`4.10`**
2. **VW long-short alpha = `1.99%/week`**，t = **`3.72`**
3. **EW long-short raw spread = `2.45%/week`**，t = **`3.22`**
4. **EW long-short alpha = `2.44%/week`**，t = **`3.34`**
5. Fama-MacBeth 单变量回归里，`MAX` 对未来周收益的斜率约 **`8.21%`**，t = **`3.14`**
6. 全控制变量回归里，`MAX` 斜率升到约 **`28.43%`**，t = **`6.14`**

### 4.5 额外 desk-relevant 细节
- high-MAX 组合更偏：
  - **小市值**
  - **低价币**
  - **高波动**
  - **更不流动**
  - **本来就更强的动量 / 近端收益**
- high-MAX 组合未来收益分布右尾也更厚：例如后续周收益的 `90%/95%/99%` 分位都明显高于 low-MAX。

这意味着：**paper alpha 本身是真的，但 desk 迁移时最先要防的是“alpha 没死，容量和成本先死”。**

## 5. 最适合映射到 1m / 3m / 5m / 15m 的最小实验
这里不要把论文机械地“日频压缩到 5m 单 bar”。真正更合理的短周期映射，是保留它的结构：

> **formation window 内的“极端正收益强度”排序 → 下一 holding window 的横截面 continuation**

### 5.1 建议的 desk 版信号定义
先在 liquid perp universe 上测三档：
- `MAX_24h_1hret`：过去 24h 内，最大 `1h` 累计收益
- `MAX_72h_2hret`：过去 72h 内，最大 `2h` 累计收益
- `MAX_7d_4hret`：过去 7d 内，最大 `4h` 累计收益

这样做比“最大单根 5m 涨幅”更稳，因为它减少 wick 噪声，更接近论文里的“极端单日回报”定义。

### 5.2 组合口径
1. Universe：Binance / OKX / Bybit 流动性最好的 `20~40` 个 USDT perp
2. Bar：先做 `15m`，再下钻 `5m`
3. 排序：每 `4h` 或 `8h` 重算一次 `MAX score`
4. 组合：`long top 20% / short bottom 20%`
5. Holding：`4h / 8h / 24h` 三档
6. Weighting：
   - baseline：等权
   - overlay：inverse-vol + liquidity cap
7. 成本：至少跑 `4 / 8 / 12 / 20 bps round-trip` 梯度

### 5.3 最便宜、最关键的对照
一定要做 **horizon sign test**：
- A 组：`过去 1h MAX` → 看后续 `1h/3h`，检验是否更像 fade
- B 组：`过去 24h/72h MAX` → 看后续 `4h/8h/24h`，检验是否转成 continuation

如果 A fade、B continue，那这条线就非常值钱，因为它不是单一 alpha，而是一条 **formation-horizon conditional family**。

## 6. 我对这条线的当前判断
我的判断是：**值得进研究池，而且优先级不低。**

原因不是论文 headline 回报高，而是它对当前 desk 有两个很实际的价值：

1. **它是 raw alpha，不是 filter。**
2. **它能直接回答一个当前很重要的问题：MAX 到底该顺着做还是反着做？答案可能取决于 formation horizon。**

如果这个判断成立，那么我们后面做 MAX / lottery family 时，就不该再问“它是 continuation 还是 reversal”，而应该问：
- formation 多长？
- holding 多长？
- universe 多窄？
- 成本和容量还能不能活？

这比继续争论“MAX 到底是赌博偏好还是过热幻觉”更有交易价值。

## 7. 这条线最可能在哪些地方失效
1. **论文更偏周频，短周期压缩后可能只剩噪声。**
   - 原文是 `28d formation -> 1w holding`，不是 `5m formation -> 15m holding`。
2. **原文 alpha 很可能部分依赖小币 / 低价 / 不流动币。**
   - 一旦只保留 liquid majors，spread 可能大幅缩水。
3. **极端正收益在短周期里更容易是 news spike 或清算刺穿。**
   - 若不做 wick / announcement / liquidation veto，信号会混入大量假 continuation。
4. **短周期 market-neutral 换手可能很高。**
   - gross 为正，不代表 net 还活。
5. **MAX 与已有 momentum 家族相关性不低。**
   - 必须做对照：它到底提供新信息，还是只是把 trend chasing 重新包装？

## 8. 下一步最该怎么测
如果只给一个优先动作，我会做这个：

> **先在 Binance USDT perp `15m` universe 上，做一组 `MAX horizon ladder`：`1h / 24h / 72h formation` × `1h / 4h / 8h holding`，直接看 spread 符号是否翻转。**

最关键不是先卷参数，而是先回答：
- `short formation` 是不是更像 fade？
- `longer formation` 是不是更像 continuation？
- `MAX score` 是否优于 plain return-rank？

如果这三问里有两问答“是”，这条线就值得进入下一轮 clean replication；如果都答不上来，就把它降级成“论文层启发”，不要硬推实盘。

## 9. 来源与可复用材料
1. **Ozdamar, M., Akdeniz, L., & Sensoy, A. (2021). _Lottery-like preferences and the MAX effect in the cryptocurrency market_. Financial Innovation, 7, 74.**
   - DOI：<https://doi.org/10.1186/s40854-021-00291-9>
   - Readable URL：<https://link.springer.com/article/10.1186/s40854-021-00291-9>
   - PDF URL：<https://link.springer.com/content/pdf/10.1186/s40854-021-00291-9.pdf>
2. **概念母体：** Bali, Cakici, Whitelaw (2011), _Maxing out: Stocks as lotteries and the cross-section of expected returns_. Journal of Financial Economics.
3. **Repo URL：** 暂未见作者公开官方复现仓库；这条线更适合按论文定义直接轻量复写。
