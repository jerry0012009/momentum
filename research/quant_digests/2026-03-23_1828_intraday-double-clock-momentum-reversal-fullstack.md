# 别把 Bitcoin intraday TSMOM 只读成开段跟涨：这篇 2022 论文更值得先复现的是 `open-impulse momentum + pre-close reversal` 双时钟完整策略
- 时间：2026-03-23 18:28 UTC
- 类型：近 5 年论文（全文可得）
- 主题类型：raw alpha
- 基础 alpha：固定时钟的日内双腿——开段信息冲击同向延续，收尾前一档价格冲击短暂反转
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/trend/momentum/mean-reversion/intraday/session-effect/double-clock/clock-alpha/btc/perp/cost/paper/crypto/5m/15m
- 证据类型：论文证据（全文）

> 先回答 base alpha：这不是 filter，也不只是“first 30m 有信息”。它的 base alpha 是**两个可交易的日内时钟效应**：`开段 30m → 收段 30m` 的同向延续，以及 `倒数第二个 30m → 最后 30m` 的反向回归；两者还能拼成一条更完整的 raw alpha 策略。

## 1. 这次看了什么
这次主看 **Shen, Urquhart, Wang (2022), _Bitcoin intraday time-series momentum_**。和我们 3 月 19 日那篇把它读成 `first-30m impulse quality gate` 不同，这次我刻意不再把它降级成 filter，而是回到论文原始交易规则：**把“开段动量”和“临收段反转”当成两条可独立下单的 raw alpha，再评估能否合成完整策略骨架。**

## 2. 核心结论
- **一句话核心结论：** 这篇论文里真正更适合当前 desk 先复现的，不只是“开头涨了尾盘也涨”，而是**`open-impulse momentum + pre-close reversal` 这条双时钟 raw alpha**。
- **一句话证明方式：** 作者直接用 5 个 BTC/USD 交易所 tick 数据聚合到 1 分钟，做 pooled 回归、样本外 R²、交易收益、CER 和 breakeven cost，给的是**可落地的完整交易骨架**，不是抽象解释。
- 关键数据点 1：`first half-hour -> last half-hour` 的斜率约 **0.968**，Newey-West **t=4.38**，样本内 **R²=1.44%**；说明开段冲击并非纯噪声。
- 关键数据点 2：把 `first half-hour` 和 `second-to-last half-hour` 一起放进模型，样本外 **OOS R²=1.61%**，高于只用前者的 **1.09%**；说明**开段动量 + 临收段反转**是互补而不是互斥。
- 关键数据点 3：交易层里，只用开段信号年化约 **7.82%**，只用倒数第二段信号年化约 **17.32%**，双信号组合年化约 **16.69%**；而在效用层，双信号组合给到 **13.95%** 平均收益、**1.15 Sharpe**、**8.09% CER**，是论文里更像“完整策略”的那条。
- 成本上要诚实：论文给出的全样本 breakeven cost 仅约 **3 / 7 / 10 bps**（三种规则），明显不是“随便 taker 都能活”的宽边；但若有更优执行或杠杆，策略生存空间会明显改善。

## 3. 为什么和当前项目有关
这篇这次值得插队，不是因为它又讲了一遍 intraday momentum，而是因为它正好补了我们当前素材池里相对少的一类：**固定时钟 raw alpha**。

它对当前 `momentum` desk 的直接价值有三层：
1. **它是 raw alpha，不是 gate。** 今天 bot7 已经连续补了不少横截面 / 配对 / stat-arb；这篇补的是另一条独立家族：`session clock alpha`。
2. **它自带完整策略链条。** 论文已经把 entry / exit / stay-flat / utility / cost 都写出来了，比只给一个 predictor 更接近可复现策略。
3. **它天然适合 15m 先做最小实验。** 因为核心定义就是 30 分钟窗口，对 15m 正好等于 2 根 bar；不用先上 1m 高频撮合才能判死活。

更重要的是：它让我们别把短周期 alpha 只理解成“逐根 rolling feature”。有些 edge 其实来自**会话中的离散信息批次和仓位回补时钟**，这跟 breakout / retest 不是一条线上的东西，值得独立进研究池。

## 3.5 策略拆解（必填）
- 方向属性：同一标的的日内双腿；一条顺势、一条逆势
- 基础 alpha：
  - leg A：开段 30m 信息冲击后的同向延续（momentum）
  - leg B：倒数第二个 30m 冲击在最后 30m 的短暂反向修正（mean reversion）
- regime：更偏向高量、高波动、信息集中、且存在明确会话边界代理的时段
- filter / veto：
  - 只做高成交/高波动分位的会话
  - 宏观公告 / FOMC / CPI 等超大跳变窗口先 blackout
  - funding cut 前后若点差/滑点异常放大则 veto
- risk / sizing / execution overlay：
  - 只在最后 30m 持仓，其他时间空仓
  - 用预测幅度或会话内 RVOL/realized vol 做分档 sizing
  - maker 优先、taker 受限；必须显式审查 break-even bps
  - 先单资产 BTC，再决定是否扩展到 ETH/SOL 做并行 clock alpha

## 4. 对 1m / 3m / 5m / 15m 的真实关系
这里要诚实：**论文原始定义是 30m bucket，不是逐根 1m alpha。**

所以更合理的 desk 落地顺序是：
- **15m：第一优先。** 两根 bar 就能复原论文核心窗口，最适合做 yes/no verdict。
- **5m：第二优先。** 保留 30m 信号定义不变，只把最后 30m 的进出拆细成 6 根 5m 来优化成交。
- **1m / 3m：执行层，不是第一轮 alpha 定义层。** 先别把它误写成“天生 1m 信号”，否则很容易只把摩擦和噪声放大。

## 5. 可复刻的最小实验（下一步怎么测）
**研究假设：** 在 crypto perp 上，存在一条可复原的 `double-clock` raw alpha：会话前 30m 的方向可预测会话末 30m 的同向收益，而会话倒数第二个 30m 对最后 30m 存在短回归；两者组合后，post-cost 指标优于单腿。

### 最小实验定义
1. **标的**：先做 `BTCUSDT perp`；通过后再加 `ETHUSDT / SOLUSDT`。
2. **bar**：先做 `15m`，只保留 closed-bar 计算。
3. **会话边界**：并行测两套，不预设哪套胜出：
   - `funding session`：`00:00 / 08:00 / 16:00 UTC`
   - `US macro session proxy`：`13:30–21:00 UTC`
4. **信号定义**：
   - `lead_ret = first_2bars_return`
   - `preclose_ret = second_last_2bars_return`
   - `close_ret = last_2bars_return`
   - leg A：`signal_mom = sign(lead_ret)`，交易 `close_ret`
   - leg B：`signal_rev = -sign(preclose_ret)`，交易 `close_ret`
   - combo：仅当 `sign(lead_ret) = -sign(preclose_ret)` 时入场，否则空仓
5. **成本**：至少显式测 `2 / 4 / 8 / 12 bps` round-trip，maker/taker 分开看。
6. **sizing**：先 equal-notional；第二轮再试 `|lead_ret|` 或会话 RVOL 分档仓位。

### 先看哪 5 个指标
1. `net Sharpe`
2. `break-even bps`
3. `hit rate`
4. `OOS R²`
5. `session-by-session stability`

### 最小 verdict 规则
- 若 combo 在 `4~8 bps` 仍优于单腿，且命中率/夏普更稳：**升为 clean replication candidate**。
- 若只有 leg B（pre-close reversal）能活：**保留为会话尾盘均值回归 alpha**。
- 若只有 leg A（open-impulse momentum）能活：**保留为 session continuation alpha**。
- 若两腿都只在零成本成立：**降级为 paper-evidence only，不进实盘素材池。**

## 6. 风险与保留意见
- 论文样本是 **2013–2020 的 BTC/USD 现货交易所**，不是当前 perp 微结构；funding、maker rebate、ADL 风险都没被完整覆盖。
- 作者原始 closing proxy 用了 **CME 17:00 EST break** 与交易所高量 opening window；搬到 24/7 perp 时，**会话边界定义本身就是第一风险点**。
- 成本是最大不确定项：论文自己的结论已经说明，不加执行优化时，edge 没大到可以无视摩擦。
- 这条 alpha 也未必全天有效，更可能只活在某几个 session proxy；如果我们把所有时段混在一起，很容易把 pocket edge 洗掉。

## 7. 来源
1. **Shen, D., Urquhart, A., & Wang, P. (2022). _Bitcoin intraday time-series momentum_. Financial Review, 57(2), 319–344.**  
   - DOI: https://doi.org/10.1111/fire.12290  
   - Readable URL: https://onlinelibrary.wiley.com/doi/10.1111/fire.12290  
   - Full-text PDF: https://centaur.reading.ac.uk/100181/3/21Sep2021Bitcoin%20Intraday%20Time-Series%20Momentum.R2.pdf  
   - Repo URL: 未找到作者公开代码仓（本次检索范围内）
2. **Gao, L., Han, Y., Li, S. Z., & Zhou, G. (2018). _Market Intraday Momentum_. Journal of Financial Economics, 129(2), 394–414.**  
   - DOI: https://doi.org/10.1016/j.jfineco.2018.04.009  
   - Readable URL: https://www.sciencedirect.com/science/article/pii/S0304405X18301001

## 8. 给这篇 digest 的一句落地结论
**如果这一轮只补 1 个更像完整策略的固定时钟 raw alpha，我会先测这条：别再把 Bitcoin intraday TSMOM 只读成“开头涨尾盘也涨”，而是先用 15m 诚实验证 `open-impulse momentum + pre-close reversal` 这条双时钟策略到底能不能在当前 perp 成本下活下来。**
