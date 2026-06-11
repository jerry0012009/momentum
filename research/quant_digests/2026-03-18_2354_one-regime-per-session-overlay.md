# 别把 breakout/EMA 与 Fib retest 在同一段行情里一起抢单：Yu et al. (2023) 更像提醒 15m desk 先做 `one-regime-per-session` overlay
- 时间：2026-03-18 23:54 UTC
- 类型：论文
- 主题标签：breakout-short / fibonacci / retest-hold / ema / psar / continuation / pullback / regime / cost / position-sizing / paper / crypto / 15m
- 证据类型：论文证据 + 工程迁移假设
- 证据强度提示：**中等**（全文可读、实验口径清楚，但样本是美股 30m 组合，不是 crypto 15m 单品种）

## 1. 这次看了什么
这次看的是 **Jing-Rung Yu, Chieh-Hui Wei, Chi-Ju Lai, Wen-Yi Lee (2023), _Extending the Omega model with momentum and reversal strategies to intraday trading_, PLoS ONE**。论文用 **S&P 500 / NASDAQ 100 成分股 30m 数据**，把 intraday momentum、intraday reversal 和一个带交易成本的 Omega 组合模型拼起来，重点不是找“最神奇入场”，而是回答一个更像 desk 问题的事：**同一天里把不同交易时钟一起开，会不会反而把利润磨掉。**

对我们这轮更值钱的，不是论文 headline 里的 Omega 优化，而是它给出的一个旁支提醒：**intraday continuation sleeve 和另一套更慢/更回撤型的 sleeve，不要默认同日混跑。** 翻成人话，就是别让 `breakout-short / EMA-PSAR follow-up` 和 `Fib retest_hold` 在同一段 15m 行情里一起抢同一笔钱。

## 2. 核心结论
- **一句话核心结论**：这篇论文更像在提醒我们，当前三条收口线下一步未必还要继续加新 filter，而是该先测一个更上层的规则：**同一段 session 里，只开一种更适配的结构时钟。**
- **一句话说明它怎么证明**：作者直接把 `momentum-only`、`reversal-only`、`same-day momentum+reversal` 三种 intraday 组合放进同一套带成本框架里比较，结果发现 **同日双开那一组 turnover 最高、最终市值最差**。
- 论文设定很具体：用 **60 天历史收益**做组合输入，`τ = 0.1%`，买卖两侧交易成本都设 **0.025%**，momentum 用**开盘后第一个 30m** 选 winners，reversal 用**前 6 个 30m** 选 losers。
- 不设持仓上限时，`M_Omega / R_Omega / M_R_Omega` 的平均持仓数分别膨胀到 **68 / 53 / 125**，而基准 Omega 只有 **15**；作者明确把这叫作 **over-diversified** 问题。
- 把持仓上限压到 **15** 后，在 **2021-01-01 ~ 2022-04-22** 的 S&P 500 样本里，`R_Omega` 的平均日收益是 **0.077%**，高于指数的 **0.057%**；说明**不是不能做 intraday，而是不能把交易次数和结构时钟写得太贪。**
- 到最波动的 **2020~2021**，`M_Omega` 和 `R_Omega` 反而表现最好；相对 Omega，S&P 500 样本里的最终市值增量分别达到 **+$731,463** 和 **+$331,336**，NASDAQ 100 里分别是 **+$247,127** 和 **+$120,332**。这说明更强波动期可以更激进，但**不是把 continuation 与另一套逻辑一起开到满。**
- 作者最后讲得很直白：**same-day momentum + reversal 不推荐**，因为双重 rebalancing 带来的交易成本会把利润吃掉。

## 3. 为什么这轮比继续加一个新 entry filter 更值得
如果只看今天已经消化过的材料，三条收口线在 entry 端其实已经不缺零件了：
- `breakout-short follow-up` 已经补过 failure / path / follow-up gate；
- `Fib retest_hold` 已经补过 `0.618 hold / 0.5 fail / 回踩质量打分`；
- `EMA / PSAR raw alpha` 也已经有 role framing、graded score、regime veto。

所以这轮如果再塞一个“又一个确认层”，边际价值不一定最高。当前更像还没收干净的，是：**这些 lane 会不会在同一段 15m 行情里互相打架。**

这就是它为什么比继续给三条线各补一个小 filter 更值得：
- 对 **breakout-short / EMA-PSAR**：它提醒我们，顺势 follow-up 应该是一套更快的 session clock；
- 对 **Fib retest_hold**：它更像另一套“先回、再守、再接回趋势”的慢时钟；
- 对整个 desk：先判断当前更像 **follow-through session** 还是 **retest session**，再决定让哪一条线拿到预算，可能比三条线同时开火更有用。

## 4. 可复刻的最小实验
### 研究假设
在 crypto `15m` 上，**one-regime-per-session overlay** 会优于“所有 lane 默认都可开”：
- 若一段 session 早期表现出明显 follow-through，就优先放行 `breakout-short follow-up + EMA/PSAR continuation`，同时关闭 `Fib retest_hold`；
- 若一段 session 早期更像冲高/破位后回到均值，再优先放行 `Fib retest_hold`，同时关闭 continuation lane。

### 最小可计算定义
先只看流动性最好的三个 session anchor：`Asia / Europe / US`。对每个 session 的前 **4 根 15m bar** 先打一个状态：
- **Continuation regime**：
  - session 前 1 小时绝对位移 `> 1.0 ATR(14)`；
  - 4 根里至少 **3 根** 收在 `session VWAP` 同一侧；
  - 首次离开 opening range 后，2 根内没有回到 range 中值。
- **Retest regime**：
  - 前 4 根里至少出现一次 opening-range 假突破/假跌破；
  - 价格两次回到 `session VWAP` 附近；
  - impulse leg 之后能回抽到 `0.382~0.618` 区间。

### A/B 测法
1. `baseline`：三条线都照常可开；
2. `continuation-only`：只允许 breakout-short + EMA/PSAR；
3. `retest-only`：只允许 Fib retest_hold；
4. `one-regime-per-session`：按上面的 regime 只放行一种 lane；不明确时 `no-trade` 或 `half-size`。

### 最小回测切口
- 标的：`BTC / ETH / SOL` perpetual
- 周期：`15m`
- 样本：近 `180~365d`
- 执行：`next-bar open`，`no-overlap`
- 成本：至少跑 `6 / 10 / 15 bps per side`

### 第一轮最该看什么
- `post_cost_expectancy`
- `same-session conflict rate`（同一 session 内 continuation 与 retest 同时触发的比例）
- `trade count retention`
- `positive-session ratio`
- `whipsaw-after-switch rate`

## 5. 风险与保留意见
- 论文是**美股 30m 横截面组合**，不是 crypto 15m 单品种；它证明的是“不同 intraday 时钟混跑会被成本惩罚”，不是直接证明我们的三条线已经能靠这个赚钱。
- 论文里的 reversal 是“买前 6 个 30m losers”，和我们的 `Fib retest_hold` 不是同一策略；这里做的是**结构类比**，不是硬说两者完全等价。
- 结果很可能部分来自 **turnover tax**，不一定全是 regime 真有信息；所以实验里一定要把 `same-session conflict rate` 和 `成本后收益` 放在一起看。
- 如果 `one-regime-per-session` 只是把交易数砍很多，却没有抬升成本后收益，那它就只是一个保守开关，不该升主线。

## 6. 下一步怎么测
最直接的一步，不是再发散找新因子，而是把当前三条线各冻结一个最诚实版本，跑同一套 overlay：
- breakout-short：选当前最接近 `final-verdict / follow-up` 的版本；
- Fibonacci：选 `0.618 hold / 0.5 fail` 当前版本；
- EMA / PSAR：选 raw alpha 最干净的 continuation 版本。

如果 `one-regime-per-session` 在 `BTC / ETH / SOL` 上同时满足：
- 成本后期望值上升；
- 同 session 冲突单明显下降；
- 不只是靠砍交易数硬抬胜率；
那它就值得升成 **shared allocation overlay**。否则就老实留在 backlog，别把“先判状态再分配预算”讲成已经被证明的真理。

## 7. 来源
1. **Yu, J.-R., Wei, C.-H., Lai, C.-J., & Lee, W.-Y. (2023). _Extending the Omega model with momentum and reversal strategies to intraday trading_. PLoS ONE, 18(9), e0291119.**
   - Venue: PLoS ONE
   - DOI: 10.1371/journal.pone.0291119
   - Readable URL: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0291119
   - Repo URL: N/A
2. **Gao, L., Han, Y., Li, S. Z., & Zhou, G. (2018). _Market intraday momentum_. Journal of Financial Economics, 129(2), 394-414.**
   - Venue: Journal of Financial Economics
   - DOI: 10.1016/j.jfineco.2018.05.009
   - Readable URL: https://doi.org/10.1016/j.jfineco.2018.05.009
   - Repo URL: N/A
3. **Herberger, T. A., Horn, M., & Oehler, A. (2020). _Are intraday reversal and momentum trading strategies feasible? An analysis for German blue chip stocks_. Financial Markets and Portfolio Management, 34(2), 179-197.**
   - Venue: Financial Markets and Portfolio Management
   - DOI: 10.1007/s11408-020-00356-2
   - Readable URL: https://doi.org/10.1007/s11408-020-00356-2
   - Repo URL: N/A
