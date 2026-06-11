# 别把这篇 interday momentum working paper 只读成股票尾盘现象：对 short-cycle desk，更该先测的是「same-clock winners-minus-losers × next-day recurring pocket」这条 raw alpha

- 时间：2026-04-14 17:18 UTC
- 类型：2024 working paper / conference PDF 全文（EFMA Lisbon 2024 paper）+ Binance USDⓈ-M public `15m` portability probe
- 主题标签：raw-alpha/cross-sectional/momentum/relative-value/same-clock/interday/time-of-day/recurring-pocket/winners-minus-losers/market-neutral/binance-perpetual/15m/5m/paper/fulltext/public-data/cost/risk
- 证据类型：论文全文规则 + 公共历史 K 线 portability probe

- 主题类型：raw alpha
- 基础 alpha：**同一时间段里，昨天跑赢横截面的币，今天在同一 UTC 时间 pocket 里仍更可能继续跑赢昨天的输家；真正该交易的不是“全天都做多动量”，而是 `same-clock cross-sectional winner-minus-loser` 这条重复性 order-flow continuation。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否

## 1. 先把一句话说清楚：这篇东西的 base alpha 是什么？

> **base alpha = same-clock cross-sectional momentum：昨天同一时间 pocket 的 winner，今天同一 pocket 更可能继续相对跑赢 loser。**

翻成人话：
这不是“昨天涨了今天还涨”的笼统动量，也不是单资产方向判断。
它更像一条 **时间定位很强的横截面相对价值 alpha**：

- 先固定一个重复出现的时间 pocket；
- 按昨天这个 pocket 的收益做横截面排序；
- 今天到同一个 pocket 时，做 `long winners / short losers`；
- 赚的是 **重复性交易流在同一时钟位置上的延续**。

所以它不是 filter，也不是 overlay；它本体就是一条 **cross-sectional / relative-value raw alpha**。

## 2. 这次看了什么

### 主来源（paper）
- **Authors：** Sebastian Schlie, Xiaozhou Zhou
- **Year：** 2024
- **Title：** *Interday Cross-Sectional Momentum: Global Evidence and Determinants*
- **Venue：** EFMA Annual Meetings 2024 (Lisbon) conference paper / working paper PDF
- **DOI：** N/A（当前未查到正式 DOI / journal 版）
- **Readable URL：** <https://www.efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2024-Lisbon/papers/Interday_Cross_Sectional_Momentum.pdf>
- **Repo URL：** N/A

### 本轮自建 probe 产物
- 脚本：`reports/artifacts/quant_digests/2026-04-14_interday_xs_momentum_probe.py`
- 原始 `15m` K 线：`reports/artifacts/quant_digests/interday_xs_momentum_probe_2026-04-14_raw_15m.csv`
- 事件级结果：`reports/artifacts/quant_digests/interday_xs_momentum_probe_2026-04-14_events.csv`
- 槽位汇总：`reports/artifacts/quant_digests/interday_xs_momentum_probe_2026-04-14_summary.csv`

## 3. 一句话核心结论 + 一句话证明方式

### 一句话核心结论
> **这篇 paper 真正适合 desk 吸收的，不是“尾盘效应还存在”这句老话，而是 `same-clock winner-minus-loser` 这条 raw alpha；但搬到 crypto 后不能盲做全天，它更像只活在少数 recurring UTC pockets 的 market-neutral 横截面动量。**

### 一句话证明方式
> **论文全文直接给出 same-interval-on-subsequent-days 的 firm-level 排序与 long-short 组合结果；我再用 Binance USDⓈ-M `15m` 数据把它翻成 `昨天同一 30m UTC slot 排名 -> 今天同一 slot 做 top20%-minus-bottom20%` 的最小实验，发现全槽位均值约 `-0.28 bps/event`，但 `17:00 / 14:00 / 11:30 / 15:30 UTC` 这几个 recurring pockets 仍有约 `+7.28 / +5.66 / +5.60 / +4.26 bps/event`。**

## 4. 为什么这轮值得写，而不是继续围绕已有 close-window / session-pocket digest 打转

这轮仍值得单独进研究池，原因有三层：

1. **它补的是“横截面 same-clock continuation”这条 raw alpha，不是单资产时段动量。**  
   之前 intake 里已经有不少 session pocket、US close handoff、ETF 时段冲击、cross-market leader continuation；但这篇给的是更偏 **cross-sectional / relative-value** 的结构：同一个 pocket 内，谁昨天强、谁昨天弱，今天再来一次同样的分化。

2. **它天然适合短周期 desk 的 `15m -> 5m` 递进实验。**  
   因为 entry / hold window 非常清楚：固定时间点开，固定 pocket 关，先做最小 market-neutral 版，再细拆到 `15m` 或 `5m` 子腿。

3. **它对 raw alpha 池是增量，而不是又一个 filter。**  
   这条线的本体就是 `winner-minus-loser spread`，不需要先依附别的主信号才能存在；后面当然可以再叠 volatility / overnight / cost filter，但它本身先天就是 alpha。

## 5. 论文真正提供了什么

## 5.1 它研究的不是普通月频 momentum，而是“同一半小时、隔天再来一次”的微观横截面延续
paper 的核心定义非常直接：

- 看某只股票在某个半小时区间的收益；
- 再看这只股票在**后续几天同一个半小时区间**的收益；
- 检验这种 same-clock return continuation 是否存在；
- 再把它翻成横截面 winners-minus-losers 组合。

作者明确说，这不是 Gao / Li 那类 **同一天 open-to-close intraday momentum**，而是 **same interval across subsequent days 的 interday cross-sectional momentum**。

对 crypto desk 来说，这个转译很重要：
> 真正该先问的不是“收盘前半小时有没有 edge”，而是 **有没有重复出现的 UTC time pocket，会让横截面 order-flow 一天接一天地在同一位置重演。**

## 5.2 论文里的 strongest pocket 仍然是“最后半小时”
paper 的摘要和正文都强调：

- interday momentum 在所有样本市场都能看到；
- **最显著的时间段是交易日最后半小时**；
- 对美国来说，相比 Heston et al. 早年的样本，强度约 **弱了 75%**，但还没消失。

这对 desk 的启发不是“股票尾盘神奇”，而是：
> **当 price discovery 接近完成、流动性高、重复性执行单更集中时，同一时钟位置的 order-flow continuation 更容易留下横截面痕迹。**

## 5.3 经济意义不是空话：long-short 组合在 paper 里是正的，但并不自动吃满成本
论文的 baseline 组合规则很简单：

- 用**昨天最后半小时**横截面回报排序；
- 取 top `10%` 做 winners、bottom `10%` 做 losers；
- **今天同一最后半小时**持有 `long winners / short losers`。

作者给出的结果有几个值得记：

- 九个样本市场里，baseline long-short 在最后半小时都显著为正；
- 平均收益约 **`2.28 bps`（美国）到 `16.2 bps`（台湾）/ 30m**；
- 日度正收益占比约 **`54% ~ 75%`**；
- 但这些收益平均只覆盖 quoted bid-ask spread 的 **`1.84% ~ 38.32%`**。

这说明：
- 它**不是**“随便 taker 打进去就稳赢”的免费午餐；
- 但它确实足以支持“**战略性地把交易安排到更有利时段**”这一层执行价值。

## 5.4 论文顺手给了两个非常实用的 gate
作者进一步发现，interday momentum 在下面两种情况下更强：

1. **低波动股票更强**；
2. **overnight absolute return 更小**时更强。

在组合层，他们加了两个简单 threshold：

- `|overnight return| < 2%`
- long 侧要求 penultimate half-hour return 为负，short 侧要求其为正

结果是：
- threshold strategy 的平均收益进一步提高；
- 覆盖 quoted spread 的比例提升到约 **`3.82% ~ 99.49%`**。

对我们 desk，这层最有价值的不是原封不动照搬 threshold，
而是它把 same-clock XS momentum 自然拆成了：

- **raw alpha：** same-clock winners-minus-losers continuation
- **filter / regime：** 低冲击、低波动、前一小段回摆结构更优

## 6. 我做的 crypto portability probe：不要盲做全天，只做 recurring pockets

## 6.1 数据与最小实验口径
- **数据源：** Binance USDⓈ-M public `/fapi/v1/klines`
- **公开性：** 完全公开 REST
- **更新频率：** `15m` K 线
- **样本：** 近约 `130` 天
- **资产池：** `ETH/SOL/XRP/BNB/DOGE/ADA/LINK/LTC/TRX/AVAX/DOT/ATOM`
- **最小实验定义：**
  1. 把 `15m` 合成 `30m` pocket；
  2. 固定 `48` 个 UTC 半小时槽位；
  3. 对每个槽位，按**昨天同一槽位**的横截面收益排序；
  4. 今天同一槽位做 `top20% - bottom20%` 等权 long-short；
  5. 统计每个槽位的 `bps/event` 与 hit rate。

这一步的目的，不是证明 paper 在 crypto 上“一比一成立”，而是回答一个更重要的问题：
> **在 24/7 市场里，same-clock cross-sectional continuation 还能不能形成可交易 pocket？**

## 6.2 先记最重要的 6 个数

### 数 1：如果把 48 个半小时槽位一锅端，edge 基本不存在
- 全槽位平均约 **`-0.28 bps / event`**
- hit rate 约 **`49.8%`**

这说明一个非常关键的事：
> **不能把这篇 paper 粗暴翻译成“crypto 全天都做 same-clock 动量”。**

## 6.3 但少数 recurring pockets 仍然活着
表现最好的几个 UTC 槽位：

- **`17:00 UTC`：约 `+7.28 bps / event`，hit rate `54.3%`**
- **`14:00 UTC`：约 `+5.66 bps / event`，hit rate `57.4%`**
- **`11:30 UTC`：约 `+5.60 bps / event`，hit rate `54.3%`**
- **`15:30 UTC`：约 `+4.26 bps / event`，hit rate `57.4%`**

这几档更像是 **Europe / US overlap 与日内固定参与者再平衡时段** 的重复性 order-flow，而不是“随机哪个半小时都有效”。

## 6.4 最强 pocket（17:00 UTC）更像“short losers”比“long winners”更重要
`17:00 UTC` 这个最强槽位，平均腿收益拆开后是：

- winners 当期平均约 **`-3.28 bps`**
- losers 当期平均约 **`-10.56 bps`**
- spread 约 **`+7.28 bps`**

翻成人话：
这里最强的不是“昨天强的今天继续大涨”，而是：
> **昨天弱的，今天同一时段更容易继续弱；winner-minus-loser spread 主要靠 loser leg 持续落后撑出来。**

这对 desk 非常重要，因为它意味着：
- 这条线更适合先做 **market-neutral / short-laggard-biased** 版本；
- 不适合直接偷懒改成 long-only winners。

## 6.5 `15:30 UTC` 则更像“正常动量”
`15:30 UTC` 这个槽位的腿拆开更顺眼：

- winners 平均约 **`+9.04 bps`**
- losers 平均约 **`+4.78 bps`**
- spread 约 **`+4.26 bps`**

这说明不是所有槽位都同一种结构：

- 有的 pocket 更像 **winner continuation**；
- 有的 pocket 更像 **loser underperformance persistence**；
- 所以最好的做法不是“一个模板覆盖所有 slot”，而是 **按 slot 做 leg decomposition**。

## 7. 这条线对 short-cycle desk 的正确定位

## 7.1 它是 raw alpha，而且是横截面 / relative-value 取向
这一点很明确：

- 信号定义清楚；
- entry/exit 时间清楚；
- 收益来源是 `winner-minus-loser spread`，不是解释性因子故事；
- 能直接落到 `15m`，再往 `5m` 压缩。

所以分类上它就是 **raw alpha**，而且比很多“只会告诉你什么时候别做”的 filter 更接近我们当前要补的素材池。

## 7.2 但它现在还不是“直接上”的完整策略
我给“是否可直接落地完整策略”打 `否`，主要因为四个缺口还没补：

1. **成本壳还没补完**：paper 自己就承认 baseline 收益吃不满 spread；
2. **crypto 端只看到 pocket，不是全天稳定存在**；
3. **slot 间结构不一样**：有的靠 winners，有的靠 losers，不能一个 sizing 模板通吃；
4. **风险中性层还没做**：还没 residualize 到 `vs BTC beta / sector bucket / funding state`。

所以更准确的定位是：
> **这是一条值得进 raw alpha 池的 same-clock XS momentum 候选，但下一步必须做 slot router + cost-aware shell。**

## 8. 风险与保留意见
- 原论文是股票微观结构，不是 crypto；crypto 没有“收盘”这一自然锚点，所以迁移时应把它读成 **recurring UTC pocket**，不是 literal market close。
- 本轮 probe 用的是 `12` 个大中型 perp 的简化 universe，还没做 sector / beta neutral；若市场 beta 主导太强，W-L spread 可能被共振污染。
- 当前结果是 **gross return**，未扣手续费与冲击；对 `4~7 bps` 级别的 edge，cost 决定生死。
- 最强槽位 `17:00 UTC` 明显偏 short-loser 结构，说明它可能更像“弱者持续弱”而非对称 momentum；落地时要区分 long 与 short 的容量、费率、funding 与尾部风险。

## 9. 下一步怎么测
1. **slot router**：对 `48` 个半小时槽位做 rolling `60d` 评分，只交易最近排名前 `2~4` 的槽位，而不是静态全天开火。
2. **leg decomposition**：分别回测 `long winners only`、`short losers only`、`W-L spread`，确认哪些槽位更偏 long continuation、哪些更偏 short laggard persistence。
3. **risk-neutral 版**：把横截面收益先对 `BTC` beta、市场单边、sector bucket 做残差化，再看 same-clock continuation 是否更干净。
4. **压缩到 desk 默认周期**：先在最强槽位上把 `30m` 持有拆成 `2 x 15m`，若第二段 edge 还在，再进一步压到 `5m` 做更细执行。
5. **成本壳**：加入 taker/maker 费、盘口冲击、最小成交额阈值，给出 first net verdict，避免 gross edge 自嗨。

## 10. 来源
- Schlie, S., & Zhou, X. (2024). *Interday Cross-Sectional Momentum: Global Evidence and Determinants*. EFMA Annual Meetings 2024 conference paper / working paper.
- Readable URL: <https://www.efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2024-Lisbon/papers/Interday_Cross_Sectional_Momentum.pdf>
- Repo URL: N/A
- 数据源（crypto probe）：Binance USDⓈ-M public klines API
  - API: <https://fapi.binance.com/fapi/v1/klines>
  - 公开性：公开 REST
  - 更新频率：`15m` K 线
  - 最小可复现实验口径：`12` 个 perp、近 `130d`、`30m` same-slot `top20%-minus-bottom20%` 组合
