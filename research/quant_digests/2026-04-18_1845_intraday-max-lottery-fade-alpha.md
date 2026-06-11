# intraday MAX / lottery-demand fade：先别把它读成情绪注脚，更像可移植的横截面 loser-fade 原型

- 时间：2026-04-18 18:45 UTC
- 类型：paper metadata + abstract audit + Binance public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：过去 `1h` 内刚出现过更极端单根 `5m` 上冲（`MAX` 更高）的币，在随后 `15m~1h` 横截面里更容易相对跑输；做法是**做空高 MAX、做多低 MAX**，而不是顺着追涨
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha / cross-sectional / mean-reversion / lottery-demand / intraday / MAX / 5m / 15m / 1h / Binance / paper / public-data / cost / risk
- 证据类型：2025 论文摘要级证据 + Crossref/OpenAlex metadata + Binance USDⓈ-M `5m` 快检

## 1. 这次看了什么

这次看的主材料是：

- **Manisha Yadav (2025)**
- **Title:** *Intraday lottery demands in cryptocurrency market*
- **Venue:** *Studies in Economics and Finance*
- **DOI:** `10.1108/sef-07-2024-0461`

这篇东西最有价值的不是“lottery demand”这个行为金融标签，而是它给了一个**能直接落到短周期横截面的 raw alpha 说法**：

> 用过去 `1h` 的 `5m` 收益里“最大那一根”作为 `MAX` 指标；`MAX` 越高，后续预期收益越低。

OpenAlex 摘要里给出的核心结果也很直接：
- 用 top-100 liquid cryptos 的高频数据；
- 把 `MAX` 改成**过去 1 小时内 `5m` log-return 的最大值**；
- 发现 `MAX` 上升 `1` 个标准差，对随后收益有 **`-0.043%`**（约 `-4.3bps`）的负向影响；
- 相比 IVOL / skewness，作者结论更偏向：**真正站得住的是 MAX 本身。**

对我们 desk 来说，这就不是“又一篇行为金融注脚”，而是：
**“过去 1 小时里刚刚最像彩票票面的币，下一小时更该被 fade。”**

## 2. 核心结论

- **base alpha 很清楚**：`past-1h extreme 5m winner -> next 15m~1h relative underperformance`。
- 它属于我们当前更该补的那一类：
  - `raw alpha`
  - `cross-sectional`
  - `mean reversion / loser-fade / winner-fade`
- 这条线和最近做过的 `pairs / funding / options / Polymarket / OBI` 都不一样；它不依赖配对、盘口、外部 venue，也不依赖低频宏观数据，**只靠公开 K 线就能先做最小实验。**
- 但我这次用 Binance liquid-major perp 做的 portability quick probe 结果比较克制：
  - **10 个 liquid majors、约 41.7 天、`5m` 粒度**；
  - 每个时点按过去 `1h MAX` 做横截面排序，取**低 MAX 组合 - 高 MAX 组合**；
  - next `15m` 平均多空收益差约 **`+0.29bps`**；
  - next `1h` 平均多空收益差约 **`+1.09bps`**；
  - `MAX` 每升高 `1` 个横截面标准差，next `1h` 收益约降 **`0.53bps`**。

也就是说：**raw alpha 方向是对的，但 current liquid-major perp 迁移版更像“弱正 market-neutral router”，还不是可直接 taker 上线的完整策略。**

## 3. 为什么值得进研究池

因为它解决的是我们现在非常需要补的一块：

### 3.1 这是标准 raw alpha，不是 filter 假扮 alpha

它不是：
- regime gate
- 风险覆盖层
- execution veto
- pairs admission
- funding/Polymarket 外部输入

而是很直接的：
**横截面里，谁刚刚在短窗里打出最极端单根上涨，谁随后更容易相对回落。**

### 3.2 它天然适合 `5m / 15m / 1h` 最小实验

数据要求极低：
- 公开可得
- 只需要多币 `5m` K 线
- 不需要订单簿
- 不需要论文私有数据库
- 不需要外部情绪源

这点非常适合 bot7 当前目标：**持续补 raw alpha 素材池，而不是把精力耗在难拿的数据上。**

### 3.3 它能直接服务我们已有横截面框架

这条线不是孤立主题，它很容易接到现有积累上：
- 可以和 `BTC-beta-neutral residual reversal` 结合；
- 可以和 `US session loser-bounce` 做对照；
- 可以作为 `cross-sectional router`，决定哪些币值得给 reversal budget；
- 也可以和 funding / OI / flow 组件拼成二阶段 admission。

所以即便它本身未必单独够强，它也很像一个**可复用的短窗横截面拥挤度特征**。

## 4. 我做的最小 portability probe

### 4.1 数据与口径

- 数据源：Binance USDⓈ-M 公共 `5m` klines
- 样本区间：`2026-03-08 03:40 UTC` 到 `2026-04-18 17:35 UTC`
- 样本长度：约 `41.7d`
- 币种：
  - `BTCUSDT`
  - `ETHUSDT`
  - `SOLUSDT`
  - `BNBUSDT`
  - `XRPUSDT`
  - `DOGEUSDT`
  - `ADAUSDT`
  - `LINKUSDT`
  - `AVAXUSDT`
  - `LTCUSDT`

定义：
- `MAX_1h` = 过去 `12` 根 `5m` 收益中的最大值
- 每个 `5m` 时点做横截面排序
- 组合：**low-MAX basket - high-MAX basket**
- 预测窗口：
  - next `3` bars = next `15m`
  - next `12` bars = next `1h`

### 4.2 快检结果

组合结果：
- next `15m`：`low - high = +0.29bps`
- next `1h`：`low - high = +1.09bps`
- next `15m` 胜率：`52.9%`
- next `1h` 胜率：`54.8%`

分腿看：
- low-MAX 组合 next `15m / 1h`：约 `+0.33bps / +1.12bps`
- high-MAX 组合 next `15m / 1h`：约 `+0.04bps / +0.03bps`

横截面斜率：
- `MAX` 每升高 `1` 个横截面标准差：
  - next `15m` 收益约少 `0.11bps`
  - next `1h` 收益约少 `0.53bps`

## 5. 这组结果怎么解读

### 5.1 它没有推翻论文方向

方向是一致的：
- `MAX` 高 -> 后续更差
- 做多低 `MAX`、做空高 `MAX` 的 market-neutral 组合是正的

所以这条线**不是没有 portability**。

### 5.2 但 edge 明显比论文摘要弱很多

论文摘要给的是：
- `1 SD MAX increase -> next return -4.3bps`

而我这次 liquid-major perp 快检只有：
- `1 SD MAX increase -> next 1h return -0.53bps`

差距不小。最可能的原因有三类：

1. **样本宇宙不同**
   - 论文是 top-100 liquid cryptos；
   - 我这里只看 10 个最主流永续，大概率把“彩票 demand 最重”的尾部币裁掉了。

2. **市场结构不同**
   - 论文更像全市场横截面定价；
   - 我们快检是 Binance liquid-major perpetual，更拥挤、更高效。

3. **alpha 本来就更像横截面 ranking 特征，而非单腿裸信号**
   - 从结果看，更像 low-vs-high 排名有点用；
   - 但单独 short high-MAX 并不强，说明不能简化成“看到冲高币就空”。

## 6. 它到底适合被当成什么

我现在更倾向把它定位成：

### 6.1 一级：raw alpha 候选

因为 base alpha 确实清楚，而且可以独立回测。

### 6.2 二级：cross-sectional router / crowding feature

在 current Binance major perp 口径下，它更像：
- 给 reversal basket 排序；
- 给 market-neutral long-short 做 admission；
- 给已有 mean-reversion alpha 加一层“别去追 lottery-like recent spikes”的 veto。

### 6.3 暂时不该被包装成“完整策略壳”

因为仅凭这次结果：
- gross edge 不厚；
- taker 成本大概率直接吃光；
- short-high-MAX 单腿版本不够硬；
- 还没做更广 universe / 更细 liquidity bucket / funding / volume neutralization。

所以它现在更像：
**值得继续压测的 raw alpha 原型**，而不是“今晚就能接 OMS 的完整交易系统”。

## 7. 如何把它接到当前 desk 主线

最自然的三种接法：

### 7.1 当作横截面反转篮子里的第一层排序

先用 `MAX_1h` 做 primary rank：
- long 最低分位
- short 最高分位
- 再叠加成交额、波动率、中性化约束

这最贴近论文原始精神。

### 7.2 当作已有 reversal alpha 的拥挤度 veto

比如已有某个 loser-bounce / RSI panic-fade / residual reversal 信号时：
- 若标的刚在过去 `1h` 出现极端正向 `MAX`，则降低做多优先级；
- 若要做空，则允许更高预算。

### 7.3 当作 mean-reversion 对象选择器

很多短周期反转策略死在“全市场都测，但 edge 只在一小撮被过度追逐的币上”。
`MAX` 很像一个**拥挤度代理变量**，适合先决定谁进入反转候选池。

## 8. 与 `1m / 3m / 5m / 15m` 的关系

- **最自然母频率：`5m`**
  - 因为论文定义本身就是过去 `1h` 的 `5m` 极值。
- **最自然持有窗：`15m ~ 1h`**
  - 也是这次快检里 slightly positive 的区间。
- **`1m / 3m` 更适合做 child execution，而不是原始信号生成**
  - 比如 `5m` 生成横截面 rank；
  - `1m/3m` 再看是否已有价格回落、盘口是否支持入场。
- **`15m` 不适合重定义 MAX 本体**
  - 若把 `MAX` 改成过去 `1h` 里的最大 `15m` return，味道就变了，容易丢掉论文的微观拥挤信息。

## 9. 风险与保留意见

### 9.1 最大风险：论文 edge 主要来自长尾币，不来自 majors

如果真是这样，那么：
- 研究上它仍成立；
- 但实盘上会碰到更高冲击成本、更差流动性和更难借券/更高资金费率噪音。

### 9.2 另一个风险：它其实需要横截面中性化，不适合裸方向化

如果没有：
- beta neutral
- sector / theme neutral
- liquidity scaling
- funding / fee control

那就容易把本来属于“relative underperformance”的 edge，误做成“绝对价格要跌”的错误版本。

### 9.3 还有一个现实风险：event crowding 太快

主流永续里，过去 1h 的极端 winner 很可能已经被各种 reversal / vol-selling / basis desks 部分套利掉，所以主流币口径 edge 会明显变薄。

## 10. 下一步怎么测

这条线值得继续，但必须按下面顺序测，别直接上线：

1. **把 universe 扩到 `30~80` 个可交易币**
   - 至少分成 `majors / upper-mid / tail-liquid` 三档，检查 alpha 是否只活在尾部。

2. **做严格横截面中性化**
   - market beta neutral
   - sector / L1-L2 / meme 分组约束
   - quote-volume bucket neutral

3. **把 `MAX` 和别的拥挤变量分开测**
   - 同时控制 `IVOL_1h`、`skew_1h`、`ret_1h`
   - 看 `MAX` 是否还有独立解释力

4. **做 cost ladder**
   - `0 / 2 / 4 / 6 / 8bps` 五档
   - 分别测 `15m` 与 `1h` horizon
   - 看它到底更适合 maker router 还是 taker router

5. **测试更像 desk 版本的两阶段结构**
   - stage A：`5m MAX rank`
   - stage B：`1m/3m` 入场确认（比如 pullback 一格、成交额回落、flow 转弱）

6. **明确它服务哪个 raw alpha 母板**
   - 如果 standalone 不够厚，就把它正式降级为：
     - `cross-sectional reversal admission feature`
     - 或 `winner-fade basket router`

## 11. 一句话 verdict

这篇 2025 论文给出的 **intraday MAX / lottery-demand fade**，在定义上是很干净的 `cross-sectional mean-reversion raw alpha`；但 current Binance liquid-major perp `5m` 快检只显示出**偏弱但同方向**的 edge，所以它现在更像**值得继续压测的 raw alpha 原型 / router 特征**，还不是可以直接照抄上线的完整策略。

## 12. 来源

- Author: Manisha Yadav
- Year: 2025
- Title: *Intraday lottery demands in cryptocurrency market*
- Venue: *Studies in Economics and Finance*
- DOI: `10.1108/sef-07-2024-0461`
- DOI URL: https://doi.org/10.1108/sef-07-2024-0461
- Crossref URL: https://api.crossref.org/works/10.1108/sef-07-2024-0461
- OpenAlex URL: https://api.openalex.org/works/https://doi.org/10.1108/sef-07-2024-0461
- 本地 artifacts：
  - `reports/artifacts/quant_digests/2026-04-18_intraday_max_lottery_summary.json`
  - `reports/artifacts/quant_digests/2026-04-18_intraday_max_lottery_ls.csv`
  - `reports/artifacts/quant_digests/2026-04-18_intraday_max_lottery_panel.csv`
  - `reports/artifacts/quant_digests/2026-04-18_intraday_max_lottery_strongshort.csv`
